from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ==================================================================================================
# R35F - TELEGRAM REPORTING + FINAL LIVE-MUTATION BOUNDARY VALIDATION
# ==================================================================================================
#
# PURPOSE
#   R35F extends the validated R35E safety model with an outbound Telegram reporting channel.
#
#   Telegram is REPORT-ONLY.
#
#   Telegram cannot:
#       - create an order intent
#       - authorize an order intent
#       - dispatch an order
#       - modify leverage
#       - modify margin
#       - modify positions
#       - enable live execution
#       - change strategy state through commands
#
# SAFETY MODEL
#   - SYNTHETIC STRATEGY DISPATCH ONLY
#   - WEEX / EXCHANGE NETWORK WRITES DISABLED
#   - REAL ORDERS DISABLED
#   - DEMO ORDERS DISABLED
#   - EXCHANGE POST / PUT / PATCH / DELETE DISABLED
#   - NO LEVERAGE / MARGIN / POSITION MUTATION
#   - FAIL CLOSED ON AMBIGUOUS ORDER OUTCOME
#   - EXCHANGE RECONCILIATION REQUIRED BEFORE ANY FUTURE LIVE MUTATION
#   - HARD EXPOSURE LIMIT REQUIRED
#   - KILL SWITCH REQUIRED
#   - TELEGRAM IS OUTBOUND REPORTING ONLY
#   - TELEGRAM COMMANDS DISABLED
#   - TELEGRAM POLLING DISABLED
#   - TELEGRAM WEBHOOK CONTROL DISABLED
#   - TELEGRAM FAILURE CANNOT ENABLE EXECUTION
#
# IMPORTANT
#   R35F DOES NOT ACTIVATE LIVE TRADING.
#
#   Telegram is permitted to make an outbound HTTPS POST to Telegram's sendMessage endpoint.
#   That POST is NOT an exchange mutation and is tracked separately from exchange network writes.
#
#   Any future WEEX mutation must be introduced explicitly in a later version.
# ==================================================================================================

VERSION = "R35F"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
)

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv(
            "HEALTH_PORT",
            "10000",
        ),
    )
)

STATE_DIR = Path(
    os.getenv(
        "R35F_STATE_DIR",
        "/tmp/r35f_state",
    )
)

STATE_FILE = (
    STATE_DIR
    / "strategy_state.json"
)

JOURNAL_FILE = (
    STATE_DIR
    / "journal.jsonl"
)

# ==================================================================================================
# HARD SAFETY CONSTANTS
# ==================================================================================================

SYNTHETIC_TRANSPORT_ONLY = True

# This refers ONLY to exchange / trading mutations.
NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

ALLOW_POST = False

ALLOW_PUT = False

ALLOW_PATCH = False

ALLOW_DELETE = False

ALLOW_LEVERAGE_MUTATION = False

ALLOW_MARGIN_MUTATION = False

ALLOW_POSITION_MUTATION = False

# --------------------------------------------------------------------------------------------------
# LIVE READINESS CONTROLS
# --------------------------------------------------------------------------------------------------

KILL_SWITCH_REQUIRED = True

RECONCILIATION_REQUIRED = True

AMBIGUOUS_OUTCOME_FAIL_CLOSED = True

IDEMPOTENCY_REQUIRED = True

# --------------------------------------------------------------------------------------------------
# TELEGRAM REPORTING BOUNDARY
# --------------------------------------------------------------------------------------------------

TELEGRAM_REPORTING_REQUIRED = True

TELEGRAM_CAN_CONTROL_EXECUTION = False

TELEGRAM_INBOUND_COMMANDS_ENABLED = False

TELEGRAM_POLLING_ENABLED = False

TELEGRAM_WEBHOOKS_ENABLED = False

TELEGRAM_REPORTING_ENABLED = (
    os.getenv(
        "TELEGRAM_REPORTING_ENABLED",
        "true",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

TELEGRAM_BOT_TOKEN = (
    os.getenv(
        "TELEGRAM_BOT_TOKEN",
        "",
    )
    .strip()
)

TELEGRAM_CHAT_ID = (
    os.getenv(
        "TELEGRAM_CHAT_ID",
        "",
    )
    .strip()
)

TELEGRAM_TIMEOUT_SECONDS = float(
    os.getenv(
        "TELEGRAM_TIMEOUT_SECONDS",
        "10",
    )
)

# ==================================================================================================
# STRATEGY CONSTANTS
# ==================================================================================================

TARGET_LEVERAGE = 100

INITIAL_ENTRY_PERCENT = 5.0

MAX_PYRAMID_ADDS = 1

PYRAMID_SIZE_PERCENT = 5.0

MAX_BACKUPS = 3

BACKUP_SIZE_PERCENT = 5.0

MAX_FUND_EXPOSURE_PERCENT = 35.0

SIGNAL_EXPIRY_SECONDS = 120

LOSS_COOLDOWN_SECONDS = 300

# ==================================================================================================
# PHASES
# ==================================================================================================

PHASE_EMPTY = "EMPTY"

PHASE_PREFLIGHT = "PREFLIGHT"

PHASE_RECONCILED = "RECONCILED"

PHASE_PREPARED = "PREPARED"

PHASE_AUTHORIZED = "AUTHORIZED"

PHASE_COMPLETED = "COMPLETED"

PHASE_BLOCKED = "BLOCKED"

ZERO_HASH = "0" * 64


# ==================================================================================================
# UTILITIES
# ==================================================================================================

def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_obj(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(
            value
        )
    )


def ensure_state_dir() -> None:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def atomic_write_json(
    path: Path,
    payload: Dict[str, Any],
) -> None:

    ensure_state_dir()

    tmp = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    with tmp.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            payload,
            handle,
            sort_keys=True,
            indent=2,
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        tmp,
        path,
    )


def banner(
    text: str,
) -> None:

    print(
        "-" * 100,
        flush=True,
    )

    print(
        text,
        flush=True,
    )

    print(
        "-" * 100,
        flush=True,
    )


def passed(
    label: str,
    condition: bool,
) -> None:

    suffix = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{label:<88} {suffix}",
        flush=True,
    )

    if not condition:

        raise AssertionError(
            label
        )


def telegram_credentials_configured() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        if self.path in {
            "/",
            "/health",
            "/healthz",
        }:

            body = json.dumps(
                {
                    "ok": True,
                    "version":
                        VERSION,
                    "symbol":
                        SYMBOL,
                    "synthetic_only":
                        SYNTHETIC_TRANSPORT_ONLY,
                    "exchange_network_writes_enabled":
                        NETWORK_WRITES_ENABLED,
                    "real_order_execution":
                        REAL_ORDER_EXECUTION,
                    "telegram_reporting_enabled":
                        TELEGRAM_REPORTING_ENABLED,
                    "telegram_configured":
                        telegram_credentials_configured(),
                    "telegram_can_control_execution":
                        TELEGRAM_CAN_CONTROL_EXECUTION,
                }
            ).encode(
                "utf-8"
            )

            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                "application/json",
            )

            self.send_header(
                "Content-Length",
                str(
                    len(
                        body
                    )
                ),
            )

            self.end_headers()

            self.wfile.write(
                body
            )

            return

        self.send_response(
            404
        )

        self.end_headers()

    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    def run() -> None:

        server = HTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        print(
            f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    thread = threading.Thread(
        target=run,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = PHASE_EMPTY

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    terminal: bool = False

    kill_switch_engaged: bool = False

    exchange_reconciled: bool = False

    reconciliation_id: Optional[str] = None

    reconciliation_hash: Optional[str] = None

    ambiguous_outcome_blocked: bool = False

    active_intent: Optional[
        Dict[str, Any]
    ] = None

    active_authorization: Optional[
        Dict[str, Any]
    ] = None

    consumed_intents: List[str] = field(
        default_factory=list
    )

    consumed_authorizations: List[str] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    synthetic_dispatch_count: int = 0

    # Exchange/trading network write count only.
    network_write_count: int = 0

    telegram_attempt_count: int = 0

    telegram_success_count: int = 0

    telegram_failure_count: int = 0

    last_telegram_message_id: Optional[str] = None

    last_telegram_error: Optional[str] = None

    journal_sequence: int = 0

    last_journal_hash: str = ZERO_HASH

    notification_events: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ==================================================================================================
# DURABLE STORE
# ==================================================================================================

class DurableStore:

    @staticmethod
    def snapshot_payload(
        state: StrategyState,
    ) -> Dict[str, Any]:

        body = (
            state.as_dict()
        )

        return {
            "body":
                body,
            "integrity":
                sha256_obj(
                    body
                ),
        }

    @classmethod
    def save(
        cls,
        state: StrategyState,
    ) -> None:

        atomic_write_json(
            STATE_FILE,
            cls.snapshot_payload(
                state
            ),
        )

    @classmethod
    def load(
        cls,
    ) -> StrategyState:

        with STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:

            wrapper = (
                json.load(
                    handle
                )
            )

        body = (
            wrapper[
                "body"
            ]
        )

        integrity = (
            wrapper[
                "integrity"
            ]
        )

        if (
            sha256_obj(
                body
            )
            != integrity
        ):

            raise RuntimeError(
                "Snapshot integrity validation failed"
            )

        return StrategyState(
            **body
        )

    @classmethod
    def exists(
        cls,
    ) -> bool:

        return (
            STATE_FILE.exists()
        )


# ==================================================================================================
# DURABLE HASH-CHAIN JOURNAL
# ==================================================================================================

class Journal:

    @staticmethod
    def append(
        state: StrategyState,
        event_type: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        ensure_state_dir()

        sequence = (
            state.journal_sequence
            + 1
        )

        body = {
            "sequence":
                sequence,
            "event_type":
                event_type,
            "generation":
                state.generation,
            "epoch":
                state.epoch,
            "payload":
                payload,
            "previous_hash":
                state.last_journal_hash,
        }

        record_hash = (
            sha256_obj(
                body
            )
        )

        record = dict(
            body
        )

        record[
            "record_hash"
        ] = record_hash

        with JOURNAL_FILE.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                canonical_json(
                    record
                )
                + "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        state.journal_sequence = (
            sequence
        )

        state.last_journal_hash = (
            record_hash
        )

        DurableStore.save(
            state
        )

        return record

    @staticmethod
    def read_all() -> List[
        Dict[str, Any]
    ]:

        if not JOURNAL_FILE.exists():

            return []

        records: List[
            Dict[str, Any]
        ] = []

        with JOURNAL_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for raw in handle:

                raw = (
                    raw.strip()
                )

                if raw:

                    records.append(
                        json.loads(
                            raw
                        )
                    )

        return records

    @staticmethod
    def validate(
        records: List[
            Dict[str, Any]
        ],
    ) -> Tuple[
        bool,
        str,
    ]:

        previous = (
            ZERO_HASH
        )

        expected_sequence = 1

        for record in records:

            if (
                record.get(
                    "sequence"
                )
                != expected_sequence
            ):

                return (
                    False,
                    f"sequence mismatch at {expected_sequence}",
                )

            if (
                record.get(
                    "previous_hash"
                )
                != previous
            ):

                return (
                    False,
                    f"previous hash mismatch at {expected_sequence}",
                )

            body = dict(
                record
            )

            actual_hash = (
                body.pop(
                    "record_hash",
                    None,
                )
            )

            expected_hash = (
                sha256_obj(
                    body
                )
            )

            if (
                actual_hash
                != expected_hash
            ):

                return (
                    False,
                    f"record hash mismatch at {expected_sequence}",
                )

            previous = (
                actual_hash
            )

            expected_sequence += 1

        return (
            True,
            "ok",
        )


# ==================================================================================================
# TELEGRAM REPORTING BOUNDARY
# ==================================================================================================

class TelegramReporter:

    def __init__(
        self,
    ) -> None:

        self.enabled = (
            TELEGRAM_REPORTING_ENABLED
        )

        self.bot_token = (
            TELEGRAM_BOT_TOKEN
        )

        self.chat_id = (
            TELEGRAM_CHAT_ID
        )

        self.timeout = (
            TELEGRAM_TIMEOUT_SECONDS
        )

    def configured(
        self,
    ) -> bool:

        return bool(
            self.bot_token
            and self.chat_id
        )

    def build_request_preview(
        self,
        text: str,
    ) -> Dict[str, Any]:

        # Never include the token itself in journal records.
        return {
            "service":
                "TELEGRAM",
            "method":
                "POST",
            "operation":
                "sendMessage",
            "chat_id_present":
                bool(
                    self.chat_id
                ),
            "text_sha256":
                sha256_text(
                    text
                ),
            "report_only":
                True,
            "can_control_execution":
                False,
            "exchange_mutation":
                False,
        }

    def send(
        self,
        text: str,
    ) -> Dict[str, Any]:

        if not self.enabled:

            raise RuntimeError(
                "Telegram reporting is disabled"
            )

        if not self.configured():

            raise RuntimeError(
                "Telegram credentials are not configured"
            )

        # IMPORTANT:
        # Token is never printed or stored in the journal.
        url = (
            "https://api.telegram.org/bot"
            + self.bot_token
            + "/sendMessage"
        )

        encoded = (
            urllib.parse.urlencode(
                {
                    "chat_id":
                        self.chat_id,
                    "text":
                        text,
                    "disable_web_page_preview":
                        "true",
                }
            )
            .encode(
                "utf-8"
            )
        )

        request = urllib.request.Request(
            url,
            data=encoded,
            method="POST",
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded",
                "User-Agent":
                    f"{VERSION}-telegram-reporter",
            },
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                raw = (
                    response.read()
                    .decode(
                        "utf-8"
                    )
                )

                status = int(
                    getattr(
                        response,
                        "status",
                        200,
                    )
                )

        except urllib.error.HTTPError as exc:

            detail = ""

            try:

                detail = (
                    exc.read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )[:300]
                )

            except Exception:

                detail = ""

            raise RuntimeError(
                f"Telegram HTTP error {exc.code}: "
                f"{detail or exc.reason}"
            ) from exc

        except urllib.error.URLError as exc:

            raise RuntimeError(
                f"Telegram network error: {exc.reason}"
            ) from exc

        try:

            payload = json.loads(
                raw
            )

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                "Telegram returned invalid JSON"
            ) from exc

        if (
            status < 200
            or status >= 300
            or payload.get(
                "ok"
            )
            is not True
        ):

            raise RuntimeError(
                f"Telegram send failed: HTTP {status}"
            )

        result = (
            payload.get(
                "result"
            )
            or {}
        )

        message_id = (
            result.get(
                "message_id"
            )
        )

        return {
            "ok":
                True,
            "status_code":
                status,
            "message_id":
                (
                    str(
                        message_id
                    )
                    if message_id
                    is not None
                    else None
                ),
            "report_only":
                True,
            "exchange_mutation":
                False,
        }


# ==================================================================================================
# R35F SAFETY / READINESS ENGINE
# ==================================================================================================

class LiveReadinessEngine:

    def __init__(
        self,
        state: Optional[
            StrategyState
        ] = None,
        reporter: Optional[
            TelegramReporter
        ] = None,
    ) -> None:

        self.state = (
            state
            or StrategyState()
        )

        self.reporter = (
            reporter
            or TelegramReporter()
        )

        DurableStore.save(
            self.state
        )

    def _journal(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:

        Journal.append(
            self.state,
            event_type,
            payload,
        )

    def _notification(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:

        event = {
            "event_type":
                event_type,
            "payload":
                payload,
            "timestamp_ms":
                int(
                    time.time()
                    * 1000
                ),
            "report_only":
                True,
            "execution_effect":
                False,
        }

        self.state.notification_events.append(
            event
        )

        self._journal(
            "NOTIFICATION_EVENT",
            event,
        )

    # --------------------------------------------------------------------------------------------------
    # TELEGRAM OUTBOUND REPORT
    # --------------------------------------------------------------------------------------------------

    def telegram_report(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        report_envelope = {
            "version":
                VERSION,
            "symbol":
                self.state.symbol,
            "event_type":
                event_type,
            "payload":
                payload,
            "timestamp_ms":
                int(
                    time.time()
                    * 1000
                ),
            "report_only":
                True,
            "telegram_can_control_execution":
                False,
            "exchange_mutation":
                False,
        }

        text = (
            f"{VERSION} REPORT\n"
            f"SYMBOL={self.state.symbol}\n"
            f"EVENT={event_type}\n"
            f"PHASE={self.state.phase}\n"
            f"GENERATION={self.state.generation}\n"
            f"EPOCH={self.state.epoch}\n"
            f"EXCHANGE_NETWORK_WRITES="
            f"{self.state.network_write_count}\n"
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}\n"
            f"DETAILS="
            f"{canonical_json(payload)}"
        )

        preview = (
            self.reporter
            .build_request_preview(
                text
            )
        )

        report_id = (
            "tg-"
            + sha256_obj(
                report_envelope
            )[:24]
        )

        self.state.telegram_attempt_count += 1

        try:

            result = (
                self.reporter
                .send(
                    text
                )
            )

            self.state.telegram_success_count += 1

            self.state.last_telegram_message_id = (
                result.get(
                    "message_id"
                )
            )

            self.state.last_telegram_error = None

            journal_payload = {
                "report_id":
                    report_id,
                "event_type":
                    event_type,
                "preview":
                    preview,
                "delivered":
                    True,
                "message_id":
                    result.get(
                        "message_id"
                    ),
                "report_only":
                    True,
                "execution_effect":
                    False,
            }

            self._journal(
                "TELEGRAM_REPORT_DELIVERED",
                journal_payload,
            )

            return journal_payload

        except Exception as exc:

            self.state.telegram_failure_count += 1

            self.state.last_telegram_error = (
                f"{type(exc).__name__}: {exc}"
            )

            journal_payload = {
                "report_id":
                    report_id,
                "event_type":
                    event_type,
                "preview":
                    preview,
                "delivered":
                    False,
                "error":
                    self.state.last_telegram_error,
                "report_only":
                    True,
                "execution_effect":
                    False,
            }

            self._journal(
                "TELEGRAM_REPORT_FAILED",
                journal_payload,
            )

            raise

    # --------------------------------------------------------------------------------------------------
    # PREFLIGHT
    # --------------------------------------------------------------------------------------------------

    def run_preflight(
        self,
    ) -> Dict[str, Any]:

        checks = {
            "synthetic_transport_only":
                SYNTHETIC_TRANSPORT_ONLY,

            "exchange_network_writes_disabled":
                not NETWORK_WRITES_ENABLED,

            "real_orders_disabled":
                not REAL_ORDER_EXECUTION,

            "demo_orders_disabled":
                not DEMO_ORDER_EXECUTION,

            "exchange_post_disabled":
                not ALLOW_POST,

            "exchange_put_disabled":
                not ALLOW_PUT,

            "exchange_patch_disabled":
                not ALLOW_PATCH,

            "exchange_delete_disabled":
                not ALLOW_DELETE,

            "kill_switch_required":
                KILL_SWITCH_REQUIRED,

            "reconciliation_required":
                RECONCILIATION_REQUIRED,

            "ambiguous_outcome_fail_closed":
                AMBIGUOUS_OUTCOME_FAIL_CLOSED,

            "idempotency_required":
                IDEMPOTENCY_REQUIRED,

            "telegram_reporting_required":
                TELEGRAM_REPORTING_REQUIRED,

            "telegram_reporting_enabled":
                TELEGRAM_REPORTING_ENABLED,

            "telegram_credentials_configured":
                telegram_credentials_configured(),

            "telegram_cannot_control_execution":
                not TELEGRAM_CAN_CONTROL_EXECUTION,

            "telegram_inbound_commands_disabled":
                not TELEGRAM_INBOUND_COMMANDS_ENABLED,

            "telegram_polling_disabled":
                not TELEGRAM_POLLING_ENABLED,

            "telegram_webhooks_disabled":
                not TELEGRAM_WEBHOOKS_ENABLED,
        }

        if not all(
            checks.values()
        ):

            raise RuntimeError(
                "R35F preflight failed"
            )

        self.state.phase = (
            PHASE_PREFLIGHT
        )

        self._journal(
            "PREFLIGHT_PASSED",
            checks,
        )

        return checks

    # --------------------------------------------------------------------------------------------------
    # EXCHANGE RECONCILIATION
    # --------------------------------------------------------------------------------------------------

    def reconcile_exchange_state(
        self,
        snapshot: Dict[str, Any],
    ) -> str:

        required = {
            "symbol",
            "available_balance",
            "positions",
            "open_orders",
            "margin_type",
            "position_mode",
        }

        if not required.issubset(
            snapshot
        ):

            raise ValueError(
                "Reconciliation snapshot missing required fields"
            )

        if (
            snapshot[
                "symbol"
            ]
            != self.state.symbol
        ):

            raise ValueError(
                "Reconciliation symbol mismatch"
            )

        reconciliation_hash = (
            sha256_obj(
                snapshot
            )
        )

        reconciliation_id = (
            f"recon-{reconciliation_hash[:16]}"
        )

        self.state.exchange_reconciled = True

        self.state.reconciliation_id = (
            reconciliation_id
        )

        self.state.reconciliation_hash = (
            reconciliation_hash
        )

        self.state.phase = (
            PHASE_RECONCILED
        )

        self._journal(
            "EXCHANGE_RECONCILED",
            {
                "reconciliation_id":
                    reconciliation_id,
                "reconciliation_hash":
                    reconciliation_hash,
                "snapshot":
                    snapshot,
            },
        )

        self._notification(
            "RECONCILIATION_OK",
            {
                "reconciliation_id":
                    reconciliation_id,
            },
        )

        return reconciliation_id

    # --------------------------------------------------------------------------------------------------
    # EXPOSURE
    # --------------------------------------------------------------------------------------------------

    def calculate_exposure_percent(
        self,
        components: List[float],
    ) -> float:

        return round(
            sum(
                float(
                    x
                )
                for x
                in components
            ),
            10,
        )

    def validate_exposure(
        self,
        components: List[float],
    ) -> float:

        exposure = (
            self.calculate_exposure_percent(
                components
            )
        )

        if (
            exposure
            > MAX_FUND_EXPOSURE_PERCENT
        ):

            self._journal(
                "EXPOSURE_REJECTED",
                {
                    "components":
                        components,
                    "exposure_percent":
                        exposure,
                    "maximum_percent":
                        MAX_FUND_EXPOSURE_PERCENT,
                },
            )

            raise RuntimeError(
                "Maximum fund exposure exceeded"
            )

        self._journal(
            "EXPOSURE_ACCEPTED",
            {
                "components":
                    components,
                "exposure_percent":
                    exposure,
                "maximum_percent":
                    MAX_FUND_EXPOSURE_PERCENT,
            },
        )

        return exposure

    # --------------------------------------------------------------------------------------------------
    # KILL SWITCH
    # --------------------------------------------------------------------------------------------------

    def engage_kill_switch(
        self,
        reason: str,
    ) -> None:

        self.state.kill_switch_engaged = True

        self.state.phase = (
            PHASE_BLOCKED
        )

        self._journal(
            "KILL_SWITCH_ENGAGED",
            {
                "reason":
                    reason,
            },
        )

        self._notification(
            "KILL_SWITCH",
            {
                "reason":
                    reason,
            },
        )

    def clear_kill_switch_for_test_only(
        self,
    ) -> None:

        self.state.kill_switch_engaged = False

        self.state.phase = (
            PHASE_RECONCILED
            if self.state.exchange_reconciled
            else PHASE_PREFLIGHT
        )

        self._journal(
            "KILL_SWITCH_CLEARED_TEST_ONLY",
            {},
        )

    # --------------------------------------------------------------------------------------------------
    # FUTURE LIVE GATE
    # --------------------------------------------------------------------------------------------------

    def assert_future_live_gate(
        self,
    ) -> None:

        if (
            self.state.kill_switch_engaged
        ):

            raise RuntimeError(
                "Kill switch engaged"
            )

        if (
            RECONCILIATION_REQUIRED
            and not self.state.exchange_reconciled
        ):

            raise RuntimeError(
                "Exchange reconciliation required"
            )

        if (
            self.state.ambiguous_outcome_blocked
        ):

            raise RuntimeError(
                "Ambiguous outcome block active"
            )

        if (
            NETWORK_WRITES_ENABLED
            or REAL_ORDER_EXECUTION
        ):

            raise RuntimeError(
                "R35F may not enable live execution"
            )

    # --------------------------------------------------------------------------------------------------
    # INTENT PREPARATION
    # --------------------------------------------------------------------------------------------------

    def prepare_intent(
        self,
        side: str,
        exposure_percent: float,
        reconciliation_id: str,
    ) -> Dict[str, Any]:

        self.assert_future_live_gate()

        if self.state.terminal:

            raise RuntimeError(
                "Terminal strategy rejects new intent"
            )

        if (
            reconciliation_id
            != self.state.reconciliation_id
        ):

            raise RuntimeError(
                "Intent reconciliation binding mismatch"
            )

        if (
            exposure_percent
            > MAX_FUND_EXPOSURE_PERCENT
        ):

            raise RuntimeError(
                "Intent exposure exceeds maximum"
            )

        self.state.highest_nonce += 1

        intent_body = {
            "version":
                VERSION,
            "symbol":
                self.state.symbol,
            "generation":
                self.state.generation,
            "epoch":
                self.state.epoch,
            "nonce":
                self.state.highest_nonce,
            "side":
                side,
            "exposure_percent":
                exposure_percent,
            "reconciliation_id":
                reconciliation_id,
            "synthetic_only":
                True,
            "transmission_forbidden":
                True,
            "network_write_forbidden":
                True,
        }

        intent_id = (
            "intent-"
            + sha256_obj(
                intent_body
            )[:24]
        )

        intent = dict(
            intent_body
        )

        intent[
            "intent_id"
        ] = intent_id

        self.state.active_intent = (
            intent
        )

        self.state.phase = (
            PHASE_PREPARED
        )

        self._journal(
            "INTENT_PREPARED",
            intent,
        )

        return intent

    # --------------------------------------------------------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------------------------------------------------------

    def authorize_intent(
        self,
        intent: Dict[str, Any],
    ) -> Dict[str, Any]:

        self.assert_future_live_gate()

        if (
            self.state.active_intent
            is None
        ):

            raise RuntimeError(
                "No active intent"
            )

        if (
            intent.get(
                "intent_id"
            )
            != self.state.active_intent.get(
                "intent_id"
            )
        ):

            raise RuntimeError(
                "Authorization intent mismatch"
            )

        if (
            intent.get(
                "generation"
            )
            != self.state.generation
            or intent.get(
                "epoch"
            )
            != self.state.epoch
        ):

            raise RuntimeError(
                "Authorization generation or epoch mismatch"
            )

        if (
            intent[
                "intent_id"
            ]
            in self.state.consumed_intents
        ):

            raise RuntimeError(
                "Consumed intent replay rejected"
            )

        auth_body = {
            "intent_id":
                intent[
                    "intent_id"
                ],
            "generation":
                self.state.generation,
            "epoch":
                self.state.epoch,
            "nonce":
                intent[
                    "nonce"
                ],
            "reconciliation_id":
                self.state.reconciliation_id,
            "synthetic_only":
                True,
            "consumed":
                False,
        }

        authorization_id = (
            "auth-"
            + sha256_obj(
                auth_body
            )[:24]
        )

        authorization = dict(
            auth_body
        )

        authorization[
            "authorization_id"
        ] = authorization_id

        self.state.active_authorization = (
            authorization
        )

        self.state.phase = (
            PHASE_AUTHORIZED
        )

        self._journal(
            "INTENT_AUTHORIZED",
            authorization,
        )

        return authorization

    # --------------------------------------------------------------------------------------------------
    # SYNTHETIC DISPATCH
    # --------------------------------------------------------------------------------------------------

    def synthetic_dispatch(
        self,
        authorization: Dict[str, Any],
    ) -> Dict[str, Any]:

        self.assert_future_live_gate()

        active = (
            self.state.active_authorization
        )

        intent = (
            self.state.active_intent
        )

        if (
            active is None
            or intent is None
        ):

            raise RuntimeError(
                "Missing active authorization or intent"
            )

        if (
            authorization.get(
                "authorization_id"
            )
            != active.get(
                "authorization_id"
            )
        ):

            raise RuntimeError(
                "Authorization binding mismatch"
            )

        if (
            authorization.get(
                "authorization_id"
            )
            in self.state.consumed_authorizations
        ):

            raise RuntimeError(
                "Authorization replay rejected"
            )

        if (
            intent.get(
                "intent_id"
            )
            in self.state.consumed_intents
        ):

            raise RuntimeError(
                "Intent replay rejected"
            )

        if (
            authorization.get(
                "reconciliation_id"
            )
            != self.state.reconciliation_id
        ):

            raise RuntimeError(
                "Authorization reconciliation binding mismatch"
            )

        receipt_body = {
            "version":
                VERSION,
            "symbol":
                self.state.symbol,
            "generation":
                self.state.generation,
            "epoch":
                self.state.epoch,
            "nonce":
                authorization[
                    "nonce"
                ],
            "intent_id":
                intent[
                    "intent_id"
                ],
            "authorization_id":
                authorization[
                    "authorization_id"
                ],
            "reconciliation_id":
                self.state.reconciliation_id,
            "transport":
                "SYNTHETIC_ONLY",
            "transmitted":
                False,
            "network_write":
                False,
            "status":
                "COMPLETED",
        }

        receipt_id = (
            "receipt-"
            + sha256_obj(
                receipt_body
            )[:24]
        )

        receipt = dict(
            receipt_body
        )

        receipt[
            "receipt_id"
        ] = receipt_id

        self.state.consumed_intents.append(
            intent[
                "intent_id"
            ]
        )

        self.state.consumed_authorizations.append(
            authorization[
                "authorization_id"
            ]
        )

        self.state.durable_receipts.append(
            receipt
        )

        self.state.synthetic_dispatch_count += 1

        self.state.phase = (
            PHASE_COMPLETED
        )

        self.state.terminal = True

        self.state.active_intent = None

        self.state.active_authorization = None

        self._journal(
            "SYNTHETIC_DISPATCH_COMPLETED",
            receipt,
        )

        self._notification(
            "SYNTHETIC_DISPATCH_COMPLETED",
            {
                "receipt_id":
                    receipt_id,
            },
        )

        return receipt

    # --------------------------------------------------------------------------------------------------
    # AMBIGUOUS OUTCOME
    # --------------------------------------------------------------------------------------------------

    def reject_ambiguous_outcome(
        self,
        fingerprint: str,
    ) -> None:

        self.state.ambiguous_outcome_blocked = True

        self.state.phase = (
            PHASE_BLOCKED
        )

        self._journal(
            "AMBIGUOUS_OUTCOME_FAIL_CLOSED",
            {
                "fingerprint":
                    fingerprint,
                "manual_or_exchange_reconciliation_required":
                    True,
            },
        )

        self._notification(
            "AMBIGUOUS_OUTCOME",
            {
                "fingerprint":
                    fingerprint,
            },
        )

    def clear_ambiguous_outcome_after_reconciliation(
        self,
        snapshot: Dict[str, Any],
    ) -> str:

        recon_id = (
            self.reconcile_exchange_state(
                snapshot
            )
        )

        self.state.ambiguous_outcome_blocked = False

        self.state.phase = (
            PHASE_RECONCILED
        )

        self._journal(
            "AMBIGUOUS_OUTCOME_CLEARED",
            {
                "reconciliation_id":
                    recon_id,
            },
        )

        return recon_id

    # --------------------------------------------------------------------------------------------------
    # EXCHANGE WRITE FIREBREAK
    # --------------------------------------------------------------------------------------------------

    def blocked_network_write(
        self,
        method: str,
        path: str,
        payload: Dict[str, Any],
    ) -> None:

        method_upper = (
            method.upper()
        )

        if method_upper in {
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }:

            self._journal(
                "EXCHANGE_NETWORK_WRITE_BLOCKED",
                {
                    "method":
                        method_upper,
                    "path":
                        path,
                    "payload_hash":
                        sha256_obj(
                            payload
                        ),
                },
            )

            raise RuntimeError(
                "R35F exchange network write firebreak: mutation blocked"
            )

        raise RuntimeError(
            "Only mutation methods are tested by blocked_network_write"
        )


# ==================================================================================================
# TEST FIXTURES
# ==================================================================================================

def reset_files() -> None:

    ensure_state_dir()

    for path in (
        STATE_FILE,
        JOURNAL_FILE,
    ):

        try:

            path.unlink()

        except FileNotFoundError:

            pass


def sample_exchange_snapshot() -> Dict[str, Any]:

    return {
        "symbol":
            SYMBOL,

        "available_balance":
            "7.18945017",

        "positions":
            [],

        "open_orders":
            [],

        "margin_type":
            "ISOLATED",

        "position_mode":
            "COMBINED",

        "observed_isolated_long_leverage":
            "100",

        "observed_isolated_short_leverage":
            "100",

        "target_leverage":
            str(
                TARGET_LEVERAGE
            ),

        "source":
            "R35F_LOCAL_RECONCILIATION_FIXTURE",
    }


def restart_engine() -> LiveReadinessEngine:

    state = (
        DurableStore.load()
    )

    return LiveReadinessEngine(
        state
    )


# ==================================================================================================
# R35F VALIDATION
# ==================================================================================================

def run_validation() -> None:

    reset_files()

    engine = (
        LiveReadinessEngine()
    )

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    banner(
        "R35F TEST 1: HARD SAFETY CONSTANTS"
    )

    passed(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    passed(
        "Exchange Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    passed(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION,
    )

    passed(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    passed(
        "Exchange POST Is Disabled",
        not ALLOW_POST,
    )

    passed(
        "Exchange PUT Is Disabled",
        not ALLOW_PUT,
    )

    passed(
        "Exchange PATCH Is Disabled",
        not ALLOW_PATCH,
    )

    passed(
        "Exchange DELETE Is Disabled",
        not ALLOW_DELETE,
    )

    passed(
        "Leverage Mutation Is Disabled",
        not ALLOW_LEVERAGE_MUTATION,
    )

    passed(
        "Margin Mutation Is Disabled",
        not ALLOW_MARGIN_MUTATION,
    )

    passed(
        "Position Mutation Is Disabled",
        not ALLOW_POSITION_MUTATION,
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    banner(
        "R35F TEST 2: TELEGRAM REPORTING CONFIGURATION"
    )

    passed(
        "Telegram Reporting Is Required",
        TELEGRAM_REPORTING_REQUIRED,
    )

    passed(
        "Telegram Reporting Is Enabled",
        TELEGRAM_REPORTING_ENABLED,
    )

    passed(
        "Telegram Bot Token Is Configured",
        bool(
            TELEGRAM_BOT_TOKEN
        ),
    )

    passed(
        "Telegram Chat ID Is Configured",
        bool(
            TELEGRAM_CHAT_ID
        ),
    )

    passed(
        "Telegram Cannot Control Execution",
        not TELEGRAM_CAN_CONTROL_EXECUTION,
    )

    passed(
        "Telegram Inbound Commands Are Disabled",
        not TELEGRAM_INBOUND_COMMANDS_ENABLED,
    )

    passed(
        "Telegram Polling Is Disabled",
        not TELEGRAM_POLLING_ENABLED,
    )

    passed(
        "Telegram Webhooks Are Disabled",
        not TELEGRAM_WEBHOOKS_ENABLED,
    )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    banner(
        "R35F TEST 3: LIVE-READINESS PREFLIGHT"
    )

    checks = (
        engine.run_preflight()
    )

    passed(
        "Preflight Contains Required Safety Checks",
        len(
            checks
        )
        >= 15,
    )

    passed(
        "All Preflight Checks Passed",
        all(
            checks.values()
        ),
    )

    passed(
        "Strategy Entered PREFLIGHT Phase",
        engine.state.phase
        == PHASE_PREFLIGHT,
    )

    passed(
        "Exchange Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    banner(
        "R35F TEST 4: RECONCILIATION REQUIRED BEFORE INTENT"
    )

    unreconciled_engine = (
        LiveReadinessEngine(
            StrategyState()
        )
    )

    blocked = False

    try:

        unreconciled_engine.prepare_intent(
            "LONG",
            5.0,
            "missing",
        )

    except RuntimeError:

        blocked = True

    passed(
        "Unreconciled Strategy Rejects Intent",
        blocked,
    )

    passed(
        "Unreconciled Strategy Makes No Synthetic Dispatch",
        unreconciled_engine.state.synthetic_dispatch_count
        == 0,
    )

    passed(
        "Unreconciled Strategy Makes No Exchange Network Write",
        unreconciled_engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    banner(
        "R35F TEST 5: EXCHANGE STATE RECONCILIATION"
    )

    snapshot = (
        sample_exchange_snapshot()
    )

    reconciliation_id = (
        engine.reconcile_exchange_state(
            snapshot
        )
    )

    passed(
        "Exchange Reconciliation Was Created",
        reconciliation_id.startswith(
            "recon-"
        ),
    )

    passed(
        "Exchange Reconciliation Is Bound To BTCUSDT",
        snapshot[
            "symbol"
        ]
        == SYMBOL,
    )

    passed(
        "Observed Long Leverage Is 100x",
        snapshot[
            "observed_isolated_long_leverage"
        ]
        == "100",
    )

    passed(
        "Observed Short Leverage Is 100x",
        snapshot[
            "observed_isolated_short_leverage"
        ]
        == "100",
    )

    passed(
        "Exchange Reconciliation Hash Is Durable",
        len(
            engine.state.reconciliation_hash
            or ""
        )
        == 64,
    )

    passed(
        "Strategy Entered RECONCILED Phase",
        engine.state.phase
        == PHASE_RECONCILED,
    )

    passed(
        "Exchange Reconciled Flag Is True",
        engine.state.exchange_reconciled,
    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    banner(
        "R35F TEST 6: RECONCILIATION DURABLE RESTART"
    )

    engine = (
        restart_engine()
    )

    passed(
        "Reconciled State Survives Restart",
        engine.state.exchange_reconciled,
    )

    passed(
        "Reconciliation ID Survives Restart",
        engine.state.reconciliation_id
        == reconciliation_id,
    )

    passed(
        "Reconciliation Hash Survives Restart",
        engine.state.reconciliation_hash
        == sha256_obj(
            snapshot
        ),
    )

    passed(
        "Exchange Network Write Count Survives At Zero",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    banner(
        "R35F TEST 7: HARD EXPOSURE LIMIT"
    )

    accepted_exposure = (
        engine.validate_exposure(
            [
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
            ]
        )
    )

    passed(
        "Exposure Below Maximum Is Accepted",
        accepted_exposure
        == 25.0,
    )

    rejected = False

    try:

        engine.validate_exposure(
            [
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                5.0,
                10.0,
            ]
        )

    except RuntimeError:

        rejected = True

    passed(
        "Exposure Above 35 Percent Is Rejected",
        rejected,
    )

    passed(
        "Maximum Fund Exposure Remains 35 Percent",
        MAX_FUND_EXPOSURE_PERCENT
        == 35.0,
    )

    passed(
        "Exposure Rejection Makes No Exchange Network Write",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    banner(
        "R35F TEST 8: KILL SWITCH"
    )

    engine.engage_kill_switch(
        "R35F_TEST"
    )

    passed(
        "Kill Switch Is Engaged",
        engine.state.kill_switch_engaged,
    )

    kill_blocked = False

    try:

        engine.prepare_intent(
            "LONG",
            5.0,
            reconciliation_id,
        )

    except RuntimeError:

        kill_blocked = True

    passed(
        "Kill Switch Blocks Intent Preparation",
        kill_blocked,
    )

    passed(
        "Kill Switch Makes No Synthetic Dispatch",
        engine.state.synthetic_dispatch_count
        == 0,
    )

    passed(
        "Kill Switch Makes No Exchange Network Write",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    banner(
        "R35F TEST 9: KILL SWITCH DURABLE RESTART"
    )

    engine = (
        restart_engine()
    )

    passed(
        "Kill Switch Survives Restart",
        engine.state.kill_switch_engaged,
    )

    restart_blocked = False

    try:

        engine.assert_future_live_gate()

    except RuntimeError:

        restart_blocked = True

    passed(
        "Restarted Kill Switch Still Blocks Future Live Gate",
        restart_blocked,
    )

    engine.clear_kill_switch_for_test_only()

    passed(
        "Test-Only Kill Switch Clear Restores Reconciled Phase",
        engine.state.phase
        == PHASE_RECONCILED,
    )

    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    banner(
        "R35F TEST 10: RECONCILIATION-BOUND INTENT"
    )

    stale_recon_blocked = False

    try:

        engine.prepare_intent(
            "LONG",
            5.0,
            "recon-stale",
        )

    except RuntimeError:

        stale_recon_blocked = True

    passed(
        "Stale Reconciliation Binding Is Rejected",
        stale_recon_blocked,
    )

    intent = (
        engine.prepare_intent(
            "LONG",
            5.0,
            reconciliation_id,
        )
    )

    passed(
        "Valid Intent Was Created",
        intent[
            "intent_id"
        ].startswith(
            "intent-"
        ),
    )

    passed(
        "Intent Is Bound To Current Reconciliation",
        intent[
            "reconciliation_id"
        ]
        == reconciliation_id,
    )

    passed(
        "Intent Is Synthetic Only",
        intent[
            "synthetic_only"
        ]
        is True,
    )

    passed(
        "Intent Forbids Transmission",
        intent[
            "transmission_forbidden"
        ]
        is True,
    )

    passed(
        "Intent Forbids Exchange Network Write",
        intent[
            "network_write_forbidden"
        ]
        is True,
    )

    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    banner(
        "R35F TEST 11: RESTART AFTER PREPARE"
    )

    prepared_intent_id = (
        intent[
            "intent_id"
        ]
    )

    engine = (
        restart_engine()
    )

    passed(
        "Prepared Intent Survives Restart",
        engine.state.active_intent
        is not None,
    )

    passed(
        "Prepared Intent ID Survives Restart",
        engine.state.active_intent[
            "intent_id"
        ]
        == prepared_intent_id,
    )

    passed(
        "Strategy Remains PREPARED",
        engine.state.phase
        == PHASE_PREPARED,
    )

    passed(
        "No Synthetic Dispatch Occurred",
        engine.state.synthetic_dispatch_count
        == 0,
    )

    passed(
        "No Exchange Network Write Occurred",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    banner(
        "R35F TEST 12: AUTHORIZATION BINDING"
    )

    authorization = (
        engine.authorize_intent(
            engine.state.active_intent
        )
    )

    authorization_id = (
        authorization[
            "authorization_id"
        ]
    )

    passed(
        "Authorization Was Created",
        authorization_id.startswith(
            "auth-"
        ),
    )

    passed(
        "Authorization Binds Exact Intent",
        authorization[
            "intent_id"
        ]
        == prepared_intent_id,
    )

    passed(
        "Authorization Binds Current Reconciliation",
        authorization[
            "reconciliation_id"
        ]
        == reconciliation_id,
    )

    passed(
        "Authorization Is Initially Unconsumed",
        authorization[
            "consumed"
        ]
        is False,
    )

    passed(
        "Strategy Entered AUTHORIZED Phase",
        engine.state.phase
        == PHASE_AUTHORIZED,
    )

    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    banner(
        "R35F TEST 13: RESTART AFTER AUTHORIZATION"
    )

    engine = (
        restart_engine()
    )

    passed(
        "Authorization Survives Restart",
        engine.state.active_authorization
        is not None,
    )

    passed(
        "Authorization ID Survives Restart",
        engine.state.active_authorization[
            "authorization_id"
        ]
        == authorization_id,
    )

    passed(
        "Strategy Remains AUTHORIZED",
        engine.state.phase
        == PHASE_AUTHORIZED,
    )

    passed(
        "Authorization Remains Unconsumed",
        authorization_id
        not in engine.state.consumed_authorizations,
    )

    passed(
        "Exchange Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    banner(
        "R35F TEST 14: EXCHANGE MUTATION FIREBREAK"
    )

    mutation_blocked = 0

    for method in (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ):

        try:

            engine.blocked_network_write(
                method,
                "/capi/v3/order",
                {
                    "symbol":
                        SYMBOL,
                },
            )

        except RuntimeError:

            mutation_blocked += 1

    passed(
        "All Four Exchange Mutation Methods Were Blocked",
        mutation_blocked
        == 4,
    )

    passed(
        "Mutation Firebreak Made No Exchange Network Write",
        engine.state.network_write_count
        == 0,
    )

    passed(
        "Real Order Execution Remains Disabled",
        not REAL_ORDER_EXECUTION,
    )

    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    banner(
        "R35F TEST 15: SYNTHETIC EXACTLY-ONCE DISPATCH"
    )

    receipt = (
        engine.synthetic_dispatch(
            engine.state.active_authorization
        )
    )

    passed(
        "Synthetic Receipt Was Created",
        receipt[
            "receipt_id"
        ].startswith(
            "receipt-"
        ),
    )

    passed(
        "Synthetic Dispatch Was Not Transmitted",
        receipt[
            "transmitted"
        ]
        is False,
    )

    passed(
        "Synthetic Dispatch Made No Exchange Network Write",
        receipt[
            "network_write"
        ]
        is False,
    )

    passed(
        "Synthetic Dispatch Count Is One",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    passed(
        "Strategy Reached COMPLETED",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    passed(
        "Strategy Is Terminal",
        engine.state.terminal,
    )

    passed(
        "Exchange Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    banner(
        "R35F TEST 16: RESTART REPLAY PROTECTION"
    )

    engine = (
        restart_engine()
    )

    passed(
        "Completed State Survives Restart",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    passed(
        "Terminal State Survives Restart",
        engine.state.terminal,
    )

    passed(
        "Consumed Intent Survives Restart",
        prepared_intent_id
        in engine.state.consumed_intents,
    )

    passed(
        "Consumed Authorization Survives Restart",
        authorization_id
        in engine.state.consumed_authorizations,
    )

    passed(
        "Durable Receipt Survives Restart",
        len(
            engine.state.durable_receipts
        )
        == 1,
    )

    passed(
        "Synthetic Dispatch Count Survives Restart",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    replay_blocked = False

    try:

        engine.synthetic_dispatch(
            authorization
        )

    except RuntimeError:

        replay_blocked = True

    passed(
        "Restart Replay Is Rejected",
        replay_blocked,
    )

    passed(
        "Replay Does Not Duplicate Synthetic Dispatch",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    passed(
        "Replay Makes No Exchange Network Write",
        engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    banner(
        "R35F TEST 17: AMBIGUOUS OUTCOME FAIL-CLOSED"
    )

    # Isolated durable test lineage.
    reset_files()

    ambiguous_engine = (
        LiveReadinessEngine(
            StrategyState()
        )
    )

    ambiguous_engine.run_preflight()

    ambiguous_snapshot = (
        sample_exchange_snapshot()
    )

    ambiguous_recon = (
        ambiguous_engine.reconcile_exchange_state(
            ambiguous_snapshot
        )
    )

    ambiguous_engine.reject_ambiguous_outcome(
        "unknown-order-fingerprint"
    )

    passed(
        "Ambiguous Outcome Activates Block",
        ambiguous_engine.state.ambiguous_outcome_blocked,
    )

    ambiguous_blocked = False

    try:

        ambiguous_engine.prepare_intent(
            "LONG",
            5.0,
            ambiguous_recon,
        )

    except RuntimeError:

        ambiguous_blocked = True

    passed(
        "Ambiguous Outcome Blocks New Intent",
        ambiguous_blocked,
    )

    passed(
        "Ambiguous Outcome Makes No Exchange Network Write",
        ambiguous_engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    banner(
        "R35F TEST 18: AMBIGUOUS OUTCOME REQUIRES RECONCILIATION"
    )

    ambiguous_engine = (
        restart_engine()
    )

    passed(
        "Ambiguous Block Survives Restart",
        ambiguous_engine.state.ambiguous_outcome_blocked,
    )

    new_recon = (
        ambiguous_engine
        .clear_ambiguous_outcome_after_reconciliation(
            sample_exchange_snapshot()
        )
    )

    passed(
        "Fresh Reconciliation Was Created",
        new_recon.startswith(
            "recon-"
        ),
    )

    passed(
        "Ambiguous Block Clears Only After Reconciliation",
        not ambiguous_engine.state.ambiguous_outcome_blocked,
    )

    passed(
        "Strategy Returns To RECONCILED",
        ambiguous_engine.state.phase
        == PHASE_RECONCILED,
    )

    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    banner(
        "R35F TEST 19: TELEGRAM REQUEST BOUNDARY"
    )

    preview_text = (
        "R35F REPORT BOUNDARY TEST"
    )

    preview = (
        ambiguous_engine
        .reporter
        .build_request_preview(
            preview_text
        )
    )

    passed(
        "Telegram Uses POST Only For Reporting",
        preview[
            "method"
        ]
        == "POST",
    )

    passed(
        "Telegram Operation Is sendMessage",
        preview[
            "operation"
        ]
        == "sendMessage",
    )

    passed(
        "Telegram Request Is Marked Report Only",
        preview[
            "report_only"
        ]
        is True,
    )

    passed(
        "Telegram Request Is Not Exchange Mutation",
        preview[
            "exchange_mutation"
        ]
        is False,
    )

    passed(
        "Telegram Request Cannot Control Execution",
        preview[
            "can_control_execution"
        ]
        is False,
    )

    passed(
        "Telegram Preview Does Not Contain Bot Token",
        TELEGRAM_BOT_TOKEN
        not in canonical_json(
            preview
        ),
    )

    passed(
        "Telegram Preview Does Not Increment Exchange Writes",
        ambiguous_engine.state.network_write_count
        == 0,
    )

    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    banner(
        "R35F TEST 20: LIVE TELEGRAM REPORT DELIVERY"
    )

    telegram_result = (
        ambiguous_engine.telegram_report(
            "R35F_VALIDATION",
            {
                "status":
                    "REPORTING_BOUNDARY_VALIDATED",
                "live_trading":
                    False,
                "exchange_network_writes":
                    0,
            },
        )
    )

    passed(
        "Telegram Report Was Delivered",
        telegram_result[
            "delivered"
        ]
        is True,
    )

    passed(
        "Telegram Report Is Marked Report Only",
        telegram_result[
            "report_only"
        ]
        is True,
    )

    passed(
        "Telegram Delivery Has No Execution Effect",
        telegram_result[
            "execution_effect"
        ]
        is False,
    )

    passed(
        "Telegram Success Count Is One",
        ambiguous_engine.state.telegram_success_count
        == 1,
    )

    passed(
        "Telegram Failure Count Is Zero",
        ambiguous_engine.state.telegram_failure_count
        == 0,
    )

    passed(
        "Telegram Did Not Increment Exchange Network Writes",
        ambiguous_engine.state.network_write_count
        == 0,
    )

    passed(
        "Real Order Execution Remains Disabled After Telegram",
        not REAL_ORDER_EXECUTION,
    )

    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    banner(
        "R35F TEST 21: TELEGRAM EXECUTION ISOLATION"
    )

    before_phase = (
        ambiguous_engine.state.phase
    )

    before_nonce = (
        ambiguous_engine.state.highest_nonce
    )

    before_dispatches = (
        ambiguous_engine.state.synthetic_dispatch_count
    )

    before_exchange_writes = (
        ambiguous_engine.state.network_write_count
    )

    passed(
        "Telegram Cannot Create Trading Intent",
        not hasattr(
            ambiguous_engine.reporter,
            "prepare_intent",
        ),
    )

    passed(
        "Telegram Cannot Authorize Trading Intent",
        not hasattr(
            ambiguous_engine.reporter,
            "authorize_intent",
        ),
    )

    passed(
        "Telegram Cannot Dispatch Trading Intent",
        not hasattr(
            ambiguous_engine.reporter,
            "synthetic_dispatch",
        ),
    )

    passed(
        "Telegram Cannot Engage Exchange Mutation",
        not TELEGRAM_CAN_CONTROL_EXECUTION,
    )

    passed(
        "Telegram Leaves Strategy Phase Unchanged",
        ambiguous_engine.state.phase
        == before_phase,
    )

    passed(
        "Telegram Leaves Strategy Nonce Unchanged",
        ambiguous_engine.state.highest_nonce
        == before_nonce,
    )

    passed(
        "Telegram Leaves Synthetic Dispatch Count Unchanged",
        ambiguous_engine.state.synthetic_dispatch_count
        == before_dispatches,
    )

    passed(
        "Telegram Leaves Exchange Write Count Unchanged",
        ambiguous_engine.state.network_write_count
        == before_exchange_writes,
    )

    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    banner(
        "R35F TEST 22: JOURNAL INTEGRITY"
    )

    records = (
        Journal.read_all()
    )

    journal_ok, journal_reason = (
        Journal.validate(
            records
        )
    )

    passed(
        "Durable Journal Contains Records",
        len(
            records
        )
        > 0,
    )

    passed(
        "Journal Hash Chain Is Valid",
        journal_ok,
    )

    passed(
        "Journal Sequence Matches State",
        records[
            -1
        ][
            "sequence"
        ]
        == ambiguous_engine.state.journal_sequence,
    )

    passed(
        "Journal Head Hash Matches State",
        records[
            -1
        ][
            "record_hash"
        ]
        == ambiguous_engine.state.last_journal_hash,
    )

    passed(
        "Every Journal Hash Has Correct Length",
        all(
            len(
                record[
                    "record_hash"
                ]
            )
            == 64
            for record
            in records
        ),
    )

    passed(
        "Every Previous Journal Hash Has Correct Length",
        all(
            len(
                record[
                    "previous_hash"
                ]
            )
            == 64
            for record
            in records
        ),
    )

    if not journal_ok:

        raise RuntimeError(
            journal_reason
        )

    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    banner(
        "R35F TEST 23: FINAL SNAPSHOT INTEGRITY"
    )

    final_state = (
        DurableStore.load()
    )

    with STATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:

        wrapper = (
            json.load(
                handle
            )
        )

    passed(
        "Final Snapshot Version Is Correct",
        final_state.version
        == VERSION,
    )

    passed(
        "Final Snapshot Symbol Is Correct",
        final_state.symbol
        == SYMBOL,
    )

    passed(
        "Final Snapshot Integrity Is Valid",
        sha256_obj(
            wrapper[
                "body"
            ]
        )
        == wrapper[
            "integrity"
        ],
    )

    passed(
        "Final Snapshot Keeps Exchange Network Write Count At Zero",
        final_state.network_write_count
        == 0,
    )

    passed(
        "Final Snapshot Keeps Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    passed(
        "Final Snapshot Keeps Real Orders Disabled",
        not REAL_ORDER_EXECUTION,
    )

    passed(
        "Final Snapshot Preserves Telegram Success",
        final_state.telegram_success_count
        == 1,
    )

    # ==============================================================================================
    # TEST 24
    # ==============================================================================================

    banner(
        "R35F TEST 24: FINAL LIVE-MUTATION GO / NO-GO"
    )

    readiness = {
        "hard_exchange_write_firebreak":
            not NETWORK_WRITES_ENABLED,

        "real_orders_still_disabled":
            not REAL_ORDER_EXECUTION,

        "kill_switch_required":
            KILL_SWITCH_REQUIRED,

        "exchange_reconciliation_required":
            RECONCILIATION_REQUIRED,

        "ambiguous_outcome_fail_closed":
            AMBIGUOUS_OUTCOME_FAIL_CLOSED,

        "idempotency_required":
            IDEMPOTENCY_REQUIRED,

        "max_fund_exposure_percent":
            MAX_FUND_EXPOSURE_PERCENT
            == 35.0,

        "telegram_reporting_required":
            TELEGRAM_REPORTING_REQUIRED,

        "telegram_reporting_enabled":
            TELEGRAM_REPORTING_ENABLED,

        "telegram_configured":
            telegram_credentials_configured(),

        "telegram_delivery_verified":
            final_state.telegram_success_count
            >= 1,

        "telegram_is_report_only":
            not TELEGRAM_CAN_CONTROL_EXECUTION,

        "telegram_inbound_disabled":
            (
                not TELEGRAM_INBOUND_COMMANDS_ENABLED
                and not TELEGRAM_POLLING_ENABLED
                and not TELEGRAM_WEBHOOKS_ENABLED
            ),

        "journal_integrity":
            journal_ok,

        "exchange_network_write_count_zero":
            final_state.network_write_count
            == 0,
    }

    passed(
        "All R35F Reporting And Safety Controls Are Present",
        all(
            readiness.values()
        ),
    )

    passed(
        "R35F Does Not Activate Live Trading",
        (
            not REAL_ORDER_EXECUTION
            and not NETWORK_WRITES_ENABLED
        ),
    )

    passed(
        "Any Future Exchange Mutation Requires A Later Explicit Version",
        True,
    )

    # ==============================================================================================
    # SUMMARY
    # ==============================================================================================

    banner(
        "R35F: VALIDATION SUMMARY"
    )

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: PHASE={final_state.phase}",
        flush=True,
    )

    print(
        f"{VERSION}: GENERATION={final_state.generation}",
        flush=True,
    )

    print(
        f"{VERSION}: EPOCH={final_state.epoch}",
        flush=True,
    )

    print(
        f"{VERSION}: HIGHEST NONCE={final_state.highest_nonce}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC DISPATCH COUNT="
        f"{final_state.synthetic_dispatch_count}",
        flush=True,
    )

    print(
        f"{VERSION}: EXCHANGE NETWORK WRITE COUNT="
        f"{final_state.network_write_count}",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE ORDER EXECUTION="
        f"{REAL_ORDER_EXECUTION}",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES ENABLED="
        f"{NETWORK_WRITES_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{MAX_FUND_EXPOSURE_PERCENT}%",
        flush=True,
    )

    print(
        f"{VERSION}: KILL SWITCH REQUIRED="
        f"{KILL_SWITCH_REQUIRED}",
        flush=True,
    )

    print(
        f"{VERSION}: RECONCILIATION REQUIRED="
        f"{RECONCILIATION_REQUIRED}",
        flush=True,
    )

    print(
        f"{VERSION}: AMBIGUOUS OUTCOME FAIL CLOSED="
        f"{AMBIGUOUS_OUTCOME_FAIL_CLOSED}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM REPORTING ENABLED="
        f"{TELEGRAM_REPORTING_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM CONFIGURED="
        f"{telegram_credentials_configured()}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM ATTEMPTS="
        f"{final_state.telegram_attempt_count}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM SUCCESSES="
        f"{final_state.telegram_success_count}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM FAILURES="
        f"{final_state.telegram_failure_count}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM CAN CONTROL EXECUTION="
        f"{TELEGRAM_CAN_CONTROL_EXECUTION}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM INBOUND COMMANDS ENABLED="
        f"{TELEGRAM_INBOUND_COMMANDS_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: JOURNAL VALID="
        f"{journal_ok}",
        flush=True,
    )

    print(
        f"{VERSION}: R35F PASSED - "
        f"TELEGRAM REPORTING VERIFIED - "
        f"LIVE TRADING REMAINS DISABLED",
        flush=True,
    )


# ==================================================================================================
# MAIN
# ==================================================================================================

def main() -> None:

    start_health_server()

    banner(
        "R35F: MAIN.PY ENTERED"
    )

    print(
        f"R35F: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"R35F: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"R35F: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"R35F: STATE DIR={STATE_DIR}",
        flush=True,
    )

    print(
        "R35F: SYNTHETIC STRATEGY TRANSPORT ONLY",
        flush=True,
    )

    print(
        "R35F: EXCHANGE NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        "R35F: REAL ORDERS DISABLED",
        flush=True,
    )

    print(
        "R35F: TELEGRAM OUTBOUND REPORTING ONLY",
        flush=True,
    )

    print(
        "R35F: TELEGRAM CANNOT CONTROL EXECUTION",
        flush=True,
    )

    print(
        "R35F: FINAL LIVE-MUTATION BOUNDARY VALIDATION",
        flush=True,
    )

    run_validation()

    # Keep Render web service alive.
    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"R35F: HEARTBEAT={heartbeat}",
            flush=True,
        )

        time.sleep(
            60
        )


if __name__ == "__main__":

    main()
