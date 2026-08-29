from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import json
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib import request

# ==================================================================================================
# R35H - REAL EXCHANGE WRITER BOUNDARY VALIDATION (HARD DISABLED)
# ==================================================================================================
#
# PURPOSE
#   R35H introduces the exact WEEX contract order writer boundary into the program while proving that
#   the writer remains hard-disabled, unreachable by the strategy, and incapable of making an
#   exchange mutation during this validation stage.
#
# IMPORTANT
#   THIS UNIT DOES NOT ENABLE LIVE TRADING.
#
# SAFETY MODEL
#   - REAL ORDER EXECUTION DISABLED
#   - EXCHANGE WRITER HARD DISABLED
#   - EXCHANGE NETWORK WRITES DISABLED
#   - DEMO ORDERS DISABLED
#   - LEVERAGE / MARGIN / POSITION MUTATION DISABLED
#   - SYNTHETIC STRATEGY DISPATCH ONLY
#   - TELEGRAM POST IS REPORT-ONLY AND CANNOT CONTROL EXECUTION
#   - FAIL CLOSED ON AMBIGUOUS OUTCOME
#   - RECONCILIATION REQUIRED BEFORE INTENT
#   - EXACTLY-ONCE AUTHORIZATION / DISPATCH MODEL
#   - HARD 35% FUND EXPOSURE LIMIT
#   - DURABLE KILL SWITCH
#
# R35H validates:
#   1. Safety constants and writer disablement.
#   2. Exact V3 order endpoint metadata.
#   3. Deterministic order payload construction.
#   4. Deterministic HMAC-SHA256 + Base64 signature generation.
#   5. Secret-safe writer preview.
#   6. Writer rejection while disabled.
#   7. Writer rejection without reconciliation.
#   8. Writer rejection without authorization.
#   9. Writer rejection for stale authorization.
#  10. Writer rejection above 35% exposure.
#  11. Writer rejection with kill switch engaged.
#  12. Writer rejection under ambiguous outcome block.
#  13. Synthetic exactly-once lifecycle remains intact.
#  14. Restart replay protection remains intact.
#  15. Telegram reporting remains execution-isolated.
#  16. Journal and snapshot integrity remain valid.
#
# NO EXCHANGE ORDER IS TRANSMITTED BY THIS FILE.
# ==================================================================================================

VERSION = "R35H"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"
HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_DIR = Path(
    os.getenv(
        "R35H_STATE_DIR",
        "/tmp/r35h_state",
    )
)

STATE_FILE = STATE_DIR / "state.json"
JOURNAL_FILE = STATE_DIR / "journal.jsonl"
SNAPSHOT_FILE = STATE_DIR / "final_snapshot.json"

WEEX_BASE_URL = "https://api-contract.weex.com"
WEEX_ORDER_PATH = "/capi/v3/order"
WEEX_ORDER_METHOD = "POST"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

MAX_FUND_EXPOSURE_PERCENT = 35.0
INITIAL_ENTRY_PERCENT = 5.0

QTY_STEP = 0.0001
MIN_QTY = 0.0001
PRICE_STEP = 0.1
QTY_PRECISION = 4
PRICE_PRECISION = 1

# ==================================================================================================
# HARD R35H EXECUTION FIREBREAKS
# ==================================================================================================

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_WRITER_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================

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

# ==================================================================================================
# WEEX CREDENTIALS
# ==================================================================================================

WEEX_API_KEY = (
    os.getenv(
        "WEEX_API_KEY",
        "",
    )
    .strip()
)

WEEX_SECRET_KEY = (
    os.getenv(
        "WEEX_SECRET_KEY",
        "",
    )
    .strip()
)

WEEX_PASSPHRASE = (
    os.getenv(
        "WEEX_PASSPHRASE",
        "",
    )
    .strip()
)

SEPARATOR = "-" * 100


# ==================================================================================================
# UTILITY HELPERS
# ==================================================================================================

def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(
    value: Any,
) -> str:

    if isinstance(
        value,
        bytes,
    ):
        raw = value

    elif isinstance(
        value,
        str,
    ):
        raw = value.encode(
            "utf-8"
        )

    else:
        raw = canonical_json(
            value
        ).encode(
            "utf-8"
        )

    return hashlib.sha256(
        raw
    ).hexdigest()


def now_ms() -> int:

    return int(
        time.time()
        * 1000
    )


def utc_iso() -> str:

    return time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime(),
    )


def print_header(
    title: str,
) -> None:

    print(
        SEPARATOR,
        flush=True,
    )

    print(
        title,
        flush=True,
    )

    print(
        SEPARATOR,
        flush=True,
    )


def check(
    label: str,
    condition: bool,
) -> None:

    status = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{label:<86} {status}",
        flush=True,
    )

    if not condition:
        raise AssertionError(
            label
        )


def atomic_write_json(
    path: Path,
    value: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    os.replace(
        tmp,
        path,
    )


def round_down_step(
    value: float,
    step: float,
    precision: int,
) -> float:

    units = int(
        (
            value
            + 1e-15
        )
        / step
    )

    return round(
        units
        * step,
        precision,
    )


def decimal_string(
    value: float,
    precision: int,
) -> str:

    return (
        f"{value:.{precision}f}"
    )


def sanitize_headers(
    headers: Dict[str, str],
) -> Dict[str, str]:

    cleaned = dict(
        headers
    )

    for key in (
        "ACCESS-KEY",
        "ACCESS-SIGN",
        "ACCESS-PASSPHRASE",
    ):

        if key in cleaned:
            cleaned[key] = (
                "<redacted>"
            )

    return cleaned


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = "INIT"

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    exchange_reconciled: bool = False

    reconciliation_id: Optional[str] = None

    reconciliation_hash: Optional[str] = None

    observed_margin_mode: Optional[str] = None

    observed_long_leverage: Optional[int] = None

    observed_short_leverage: Optional[int] = None

    kill_switch_engaged: bool = False

    ambiguous_outcome_block: bool = False

    active_intent: Optional[
        Dict[str, Any]
    ] = None

    active_authorization: Optional[
        Dict[str, Any]
    ] = None

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    consumed_intents: List[
        str
    ] = field(
        default_factory=list
    )

    consumed_authorizations: List[
        str
    ] = field(
        default_factory=list
    )

    synthetic_dispatch_count: int = 0

    exchange_network_writes: int = 0

    writer_attempt_count: int = 0

    writer_block_count: int = 0

    telegram_success_count: int = 0

    telegram_failure_count: int = 0

    terminal: bool = False

    journal_sequence: int = 0

    last_journal_hash: str = (
        "0" * 64
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

    def __init__(
        self,
        state_file: Path,
        journal_file: Path,
    ) -> None:

        self.state_file = (
            state_file
        )

        self.journal_file = (
            journal_file
        )

        self.lock = (
            threading.RLock()
        )

    def reset(
        self,
    ) -> StrategyState:

        with self.lock:

            self.state_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            for path in (
                self.state_file,
                self.journal_file,
                SNAPSHOT_FILE,
            ):

                try:
                    path.unlink()

                except FileNotFoundError:
                    pass

            state = (
                StrategyState()
            )

            self.save(
                state
            )

            return state

    def save(
        self,
        state: StrategyState,
    ) -> None:

        with self.lock:

            atomic_write_json(
                self.state_file,
                state.as_dict(),
            )

    def load(
        self,
    ) -> StrategyState:

        with self.lock:

            if not self.state_file.exists():

                return self.reset()

            data = json.loads(
                self.state_file.read_text(
                    encoding="utf-8"
                )
            )

            return StrategyState(
                **data
            )

    def append_event(
        self,
        state: StrategyState,
        event: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:

        with self.lock:

            sequence = (
                state.journal_sequence
                + 1
            )

            record_core = {

                "sequence":
                    sequence,

                "timestamp":
                    utc_iso(),

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "event":
                    event,

                "generation":
                    state.generation,

                "epoch":
                    state.epoch,

                "previous_hash":
                    state.last_journal_hash,

                "details":
                    details,

            }

            record_hash = (
                sha256_hex(
                    record_core
                )
            )

            record = dict(
                record_core
            )

            record[
                "record_hash"
            ] = record_hash

            self.journal_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.journal_file.open(
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

            self.save(
                state
            )

            return record

    def validate_journal(
        self,
        state: StrategyState,
    ) -> Tuple[
        bool,
        int,
        str,
    ]:

        if not self.journal_file.exists():

            return (
                False,
                0,
                "0" * 64,
            )

        previous = (
            "0" * 64
        )

        count = 0

        for raw in (
            self.journal_file
            .read_text(
                encoding="utf-8"
            )
            .splitlines()
        ):

            if not raw.strip():
                continue

            record = json.loads(
                raw
            )

            received_hash = (
                record.pop(
                    "record_hash"
                )
            )

            expected_hash = (
                sha256_hex(
                    record
                )
            )

            if received_hash != expected_hash:

                return (
                    False,
                    count,
                    previous,
                )

            if (
                record.get(
                    "previous_hash"
                )
                != previous
            ):

                return (
                    False,
                    count,
                    previous,
                )

            count += 1

            if (
                record.get(
                    "sequence"
                )
                != count
            ):

                return (
                    False,
                    count,
                    previous,
                )

            previous = (
                received_hash
            )

        valid = (
            count
            == state.journal_sequence
            and
            previous
            == state.last_journal_hash
        )

        return (
            valid,
            count,
            previous,
        )


STORE = DurableStore(
    STATE_FILE,
    JOURNAL_FILE,
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

        if self.path not in (
            "/",
            "/health",
        ):

            self.send_response(
                404
            )

            self.end_headers()

            return

        try:

            state = (
                STORE.load()
            )

            payload = {

                "ok":
                    True,

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "phase":
                    state.phase,

                "exchange_reconciled":
                    state.exchange_reconciled,

                "exchange_network_writes":
                    state.exchange_network_writes,

                "real_order_execution":
                    REAL_ORDER_EXECUTION,

                "exchange_writer_enabled":
                    EXCHANGE_WRITER_ENABLED,

            }

        except Exception as exc:

            payload = {

                "ok":
                    False,

                "error":
                    str(exc),

            }

        body = json.dumps(
            payload
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
            if payload.get(
                "ok"
            )
            else 500
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(
                len(body)
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    try:

        server = HTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        print(
            f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}",
            flush=True,
        )

    except OSError as exc:

        print(
            f"{VERSION}: HEALTH SERVER NOT STARTED: {exc}",
            flush=True,
        )


# ==================================================================================================
# RECONCILIATION
# ==================================================================================================

def create_reconciliation(
    state: StrategyState,
    margin_mode: str,
    long_leverage: int,
    short_leverage: int,
) -> Dict[str, Any]:

    if state.kill_switch_engaged:

        raise RuntimeError(
            "kill switch engaged"
        )

    payload = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "generation":
            state.generation,

        "epoch":
            state.epoch,

        "margin_mode":
            margin_mode,

        "long_leverage":
            long_leverage,

        "short_leverage":
            short_leverage,

        "created_at_ms":
            now_ms(),

    }

    reconciliation_id = (
        "rec-"
        + sha256_hex(
            payload
        )[:20]
    )

    payload[
        "reconciliation_id"
    ] = reconciliation_id

    reconciliation_hash = (
        sha256_hex(
            payload
        )
    )

    payload[
        "reconciliation_hash"
    ] = reconciliation_hash

    state.exchange_reconciled = (
        True
    )

    state.reconciliation_id = (
        reconciliation_id
    )

    state.reconciliation_hash = (
        reconciliation_hash
    )

    state.observed_margin_mode = (
        margin_mode
    )

    state.observed_long_leverage = (
        long_leverage
    )

    state.observed_short_leverage = (
        short_leverage
    )

    state.ambiguous_outcome_block = (
        False
    )

    state.phase = (
        "RECONCILED"
    )

    state.terminal = (
        False
    )

    STORE.append_event(
        state,
        "EXCHANGE_RECONCILED",
        {
            "reconciliation_id":
                reconciliation_id,

            "reconciliation_hash":
                reconciliation_hash,

            "margin_mode":
                margin_mode,

            "long_leverage":
                long_leverage,

            "short_leverage":
                short_leverage,
        },
    )

    return payload


# ==================================================================================================
# EXPOSURE LIMIT
# ==================================================================================================

def enforce_exposure(
    balance_usdt: float,
    planned_margin_usdt: float,
) -> None:

    if balance_usdt <= 0:

        raise ValueError(
            "balance must be positive"
        )

    exposure_percent = (
        planned_margin_usdt
        / balance_usdt
        * 100.0
    )

    if (
        exposure_percent
        >
        MAX_FUND_EXPOSURE_PERCENT
        + 1e-12
    ):

        raise RuntimeError(
            "hard exposure limit exceeded"
        )


# ==================================================================================================
# INTENT PREPARATION
# ==================================================================================================

def prepare_intent(
    state: StrategyState,
    *,
    side: str,
    position_side: str,
    quantity: float,
    balance_usdt: float,
    planned_margin_usdt: float,
) -> Dict[str, Any]:

    if state.terminal:

        raise RuntimeError(
            "terminal state"
        )

    if state.kill_switch_engaged:

        raise RuntimeError(
            "kill switch engaged"
        )

    if state.ambiguous_outcome_block:

        raise RuntimeError(
            "ambiguous outcome block active"
        )

    if (
        not state.exchange_reconciled
        or
        not state.reconciliation_id
    ):

        raise RuntimeError(
            "exchange reconciliation required"
        )

    if (
        state.observed_margin_mode
        != TARGET_MARGIN_MODE
    ):

        raise RuntimeError(
            "margin mode mismatch"
        )

    if (
        state.observed_long_leverage
        != TARGET_LONG_LEVERAGE
    ):

        raise RuntimeError(
            "long leverage mismatch"
        )

    if (
        state.observed_short_leverage
        != TARGET_SHORT_LEVERAGE
    ):

        raise RuntimeError(
            "short leverage mismatch"
        )

    enforce_exposure(
        balance_usdt,
        planned_margin_usdt,
    )

    normalized_quantity = (
        round_down_step(
            quantity,
            QTY_STEP,
            QTY_PRECISION,
        )
    )

    if (
        normalized_quantity
        < MIN_QTY
    ):

        raise RuntimeError(
            "quantity below minimum"
        )

    state.highest_nonce += 1

    intent_core = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "generation":
            state.generation,

        "epoch":
            state.epoch,

        "nonce":
            state.highest_nonce,

        "reconciliation_id":
            state.reconciliation_id,

        "reconciliation_hash":
            state.reconciliation_hash,

        "side":
            side.upper(),

        "positionSide":
            position_side.upper(),

        "type":
            "MARKET",

        "quantity":
            decimal_string(
                normalized_quantity,
                QTY_PRECISION,
            ),

        "balance_usdt":
            round(
                balance_usdt,
                12,
            ),

        "planned_margin_usdt":
            round(
                planned_margin_usdt,
                12,
            ),

        "max_fund_exposure_percent":
            MAX_FUND_EXPOSURE_PERCENT,

        "synthetic_only":
            True,

        "transmission_allowed":
            False,

        "exchange_network_write_allowed":
            False,

        "created_at_ms":
            now_ms(),

    }

    intent_id = (
        "int-"
        + sha256_hex(
            intent_core
        )[:20]
    )

    intent = dict(
        intent_core
    )

    intent[
        "intent_id"
    ] = intent_id

    intent[
        "intent_hash"
    ] = sha256_hex(
        intent
    )

    state.active_intent = (
        intent
    )

    state.active_authorization = (
        None
    )

    state.phase = (
        "PREPARED"
    )

    STORE.append_event(
        state,
        "INTENT_PREPARED",
        {
            "intent_id":
                intent_id,

            "intent_hash":
                intent[
                    "intent_hash"
                ],

            "reconciliation_id":
                state.reconciliation_id,
        },
    )

    return intent


# ==================================================================================================
# AUTHORIZATION
# ==================================================================================================

def authorize_intent(
    state: StrategyState,
) -> Dict[str, Any]:

    intent = (
        state.active_intent
    )

    if not intent:

        raise RuntimeError(
            "no active intent"
        )

    if (
        state.kill_switch_engaged
        or
        state.ambiguous_outcome_block
    ):

        raise RuntimeError(
            "authorization blocked"
        )

    if (
        intent.get(
            "reconciliation_id"
        )
        != state.reconciliation_id
    ):

        raise RuntimeError(
            "stale reconciliation binding"
        )

    if (
        intent.get(
            "intent_id"
        )
        in state.consumed_intents
    ):

        raise RuntimeError(
            "intent already consumed"
        )

    auth_core = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "generation":
            state.generation,

        "epoch":
            state.epoch,

        "intent_id":
            intent[
                "intent_id"
            ],

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "reconciliation_id":
            state.reconciliation_id,

        "reconciliation_hash":
            state.reconciliation_hash,

        "consumed":
            False,

        "synthetic_only":
            True,

        "live_writer_allowed":
            False,

        "created_at_ms":
            now_ms(),

    }

    authorization_id = (
        "auth-"
        + sha256_hex(
            auth_core
        )[:20]
    )

    authorization = dict(
        auth_core
    )

    authorization[
        "authorization_id"
    ] = authorization_id

    authorization[
        "authorization_hash"
    ] = sha256_hex(
        authorization
    )

    state.active_authorization = (
        authorization
    )

    state.phase = (
        "AUTHORIZED"
    )

    STORE.append_event(
        state,
        "INTENT_AUTHORIZED",
        {
            "authorization_id":
                authorization_id,

            "authorization_hash":
                authorization[
                    "authorization_hash"
                ],

            "intent_id":
                intent[
                    "intent_id"
                ],
        },
    )

    return authorization


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================

def synthetic_dispatch(
    state: StrategyState,
) -> Dict[str, Any]:

    intent = (
        state.active_intent
    )

    auth = (
        state.active_authorization
    )

    if (
        not intent
        or
        not auth
    ):

        raise RuntimeError(
            "intent and authorization required"
        )

    if (
        state.kill_switch_engaged
        or
        state.ambiguous_outcome_block
    ):

        raise RuntimeError(
            "dispatch blocked"
        )

    if (
        intent[
            "intent_id"
        ]
        in state.consumed_intents
    ):

        raise RuntimeError(
            "intent replay rejected"
        )

    if (
        auth[
            "authorization_id"
        ]
        in state.consumed_authorizations
    ):

        raise RuntimeError(
            "authorization replay rejected"
        )

    if (
        auth[
            "intent_id"
        ]
        != intent[
            "intent_id"
        ]
        or
        auth[
            "intent_hash"
        ]
        != intent[
            "intent_hash"
        ]
    ):

        raise RuntimeError(
            "authorization mismatch"
        )

    if (
        auth[
            "reconciliation_id"
        ]
        != state.reconciliation_id
    ):

        raise RuntimeError(
            "stale authorization reconciliation"
        )

    receipt_core = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "generation":
            state.generation,

        "epoch":
            state.epoch,

        "intent_id":
            intent[
                "intent_id"
            ],

        "authorization_id":
            auth[
                "authorization_id"
            ],

        "reconciliation_id":
            state.reconciliation_id,

        "transmitted":
            False,

        "synthetic":
            True,

        "exchange_network_write":
            False,

        "created_at_ms":
            now_ms(),

    }

    receipt = dict(
        receipt_core
    )

    receipt[
        "receipt_id"
    ] = (
        "rcpt-"
        + sha256_hex(
            receipt_core
        )[:20]
    )

    receipt[
        "receipt_hash"
    ] = sha256_hex(
        receipt
    )

    state.synthetic_dispatch_count += 1

    state.consumed_intents.append(
        intent[
            "intent_id"
        ]
    )

    state.consumed_authorizations.append(
        auth[
            "authorization_id"
        ]
    )

    auth[
        "consumed"
    ] = True

    state.durable_receipts.append(
        receipt
    )

    state.phase = (
        "COMPLETED"
    )

    state.terminal = (
        True
    )

    STORE.append_event(
        state,
        "SYNTHETIC_DISPATCH_COMPLETED",
        {
            "receipt_id":
                receipt[
                    "receipt_id"
                ],

            "receipt_hash":
                receipt[
                    "receipt_hash"
                ],

            "exchange_network_writes":
                state.exchange_network_writes,
        },
    )

    return receipt


# ==================================================================================================
# R35H EXACT WEEX V3 ORDER PAYLOAD
# ==================================================================================================

def build_weex_order_payload(
    intent: Dict[str, Any],
) -> Dict[str, str]:

    if (
        intent.get(
            "symbol"
        )
        != SYMBOL
    ):

        raise RuntimeError(
            "symbol mismatch"
        )

    client_order_id = (
        "r35h-"
        + sha256_hex(
            {
                "intent_id":
                    intent[
                        "intent_id"
                    ],

                "generation":
                    intent[
                        "generation"
                    ],

                "epoch":
                    intent[
                        "epoch"
                    ],
            }
        )[:24]
    )

    return {

        "symbol":
            SYMBOL,

        "side":
            str(
                intent[
                    "side"
                ]
            ).upper(),

        "positionSide":
            str(
                intent[
                    "positionSide"
                ]
            ).upper(),

        "type":
            str(
                intent[
                    "type"
                ]
            ).upper(),

        "quantity":
            str(
                intent[
                    "quantity"
                ]
            ),

        "newClientOrderId":
            client_order_id,

    }


# ==================================================================================================
# WEEX SIGNATURE
# ==================================================================================================

def weex_signature(
    secret_key: str,
    timestamp_ms: str,
    method: str,
    request_path: str,
    body: str,
    query_string: str = "",
) -> str:

    if query_string:

        prehash = (
            f"{timestamp_ms}"
            f"{method.upper()}"
            f"{request_path}"
            f"?"
            f"{query_string}"
            f"{body}"
        )

    else:

        prehash = (
            f"{timestamp_ms}"
            f"{method.upper()}"
            f"{request_path}"
            f"{body}"
        )

    digest = hmac.new(
        secret_key.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "ascii"
    )


# ==================================================================================================
# WRITER ENVELOPE
# ==================================================================================================

def build_writer_envelope(
    intent: Dict[str, Any],
    timestamp_ms: Optional[str] = None,
) -> Dict[str, Any]:

    payload = (
        build_weex_order_payload(
            intent
        )
    )

    body = (
        canonical_json(
            payload
        )
    )

    timestamp = (
        timestamp_ms
        or str(
            now_ms()
        )
    )

    # ----------------------------------------------------------------------------------------------
    # R35H validates signing but never displays the real secret.
    # If no secret exists, a local validation-only secret is used.
    # ----------------------------------------------------------------------------------------------

    secret_for_validation = (
        WEEX_SECRET_KEY
        if WEEX_SECRET_KEY
        else "R35H_LOCAL_VALIDATION_SECRET"
    )

    signature = (
        weex_signature(
            secret_for_validation,
            timestamp,
            WEEX_ORDER_METHOD,
            WEEX_ORDER_PATH,
            body,
        )
    )

    headers = {

        "ACCESS-KEY":
            (
                WEEX_API_KEY
                if WEEX_API_KEY
                else "R35H_VALIDATION_KEY"
            ),

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            (
                WEEX_PASSPHRASE
                if WEEX_PASSPHRASE
                else "R35H_VALIDATION_PASSPHRASE"
            ),

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",

        "locale":
            "en-US",

    }

    envelope_core = {

        "method":
            WEEX_ORDER_METHOD,

        "base_url":
            WEEX_BASE_URL,

        "request_path":
            WEEX_ORDER_PATH,

        "body":
            body,

        "payload":
            payload,

        "headers":
            headers,

        "intent_id":
            intent[
                "intent_id"
            ],

        "intent_hash":
            intent[
                "intent_hash"
            ],

        "generation":
            intent[
                "generation"
            ],

        "epoch":
            intent[
                "epoch"
            ],

        "reconciliation_id":
            intent[
                "reconciliation_id"
            ],

        "writer_enabled":
            EXCHANGE_WRITER_ENABLED,

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "exchange_network_writes_enabled":
            EXCHANGE_NETWORK_WRITES_ENABLED,

    }

    envelope = dict(
        envelope_core
    )

    envelope[
        "envelope_hash"
    ] = sha256_hex(
        envelope_core
    )

    return envelope


# ==================================================================================================
# SECRET-SAFE WRITER PREVIEW
# ==================================================================================================

def writer_preview(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    return {

        "method":
            envelope[
                "method"
            ],

        "url":
            (
                envelope[
                    "base_url"
                ]
                +
                envelope[
                    "request_path"
                ]
            ),

        "request_path":
            envelope[
                "request_path"
            ],

        "payload":
            copy.deepcopy(
                envelope[
                    "payload"
                ]
            ),

        "headers":
            sanitize_headers(
                envelope[
                    "headers"
                ]
            ),

        "intent_id":
            envelope[
                "intent_id"
            ],

        "reconciliation_id":
            envelope[
                "reconciliation_id"
            ],

        "envelope_hash":
            envelope[
                "envelope_hash"
            ],

        "writer_enabled":
            envelope[
                "writer_enabled"
            ],

        "real_order_execution":
            envelope[
                "real_order_execution"
            ],

        "exchange_network_writes_enabled":
            envelope[
                "exchange_network_writes_enabled"
            ],

        "transmitted":
            False,

    }


# ==================================================================================================
# R35H REAL WRITER BOUNDARY
# ==================================================================================================

def attempt_live_writer(
    state: StrategyState,
    envelope: Dict[str, Any],
) -> None:

    """
    Exact boundary where a future controlled live stage could eventually
    transmit an authenticated WEEX order.

    R35H deliberately fails closed before constructing or opening an HTTP
    request.

    THERE IS NO EXCHANGE NETWORK TRANSMISSION IN THIS FUNCTION.
    """

    state.writer_attempt_count += 1

    def block(
        reason: str,
    ) -> None:

        state.writer_block_count += 1

        # ------------------------------------------------------------------------------------------
        # Do not journal test-only blocked attempts here.
        #
        # Some R35H validation tests intentionally use detached StrategyState copies.
        # Journaling those copies would fork the durable journal sequence/hash chain.
        # ------------------------------------------------------------------------------------------

        raise RuntimeError(
            reason
        )

    # ----------------------------------------------------------------------------------------------
    # GLOBAL HARD FIREBREAKS
    # ----------------------------------------------------------------------------------------------

    if not EXCHANGE_WRITER_ENABLED:

        block(
            "exchange writer hard disabled"
        )

    if not REAL_ORDER_EXECUTION:

        block(
            "real order execution disabled"
        )

    if not EXCHANGE_NETWORK_WRITES_ENABLED:

        block(
            "exchange network writes disabled"
        )

    if SYNTHETIC_TRANSPORT_ONLY:

        block(
            "synthetic transport only"
        )

    # ----------------------------------------------------------------------------------------------
    # FUTURE INNER LIVE GATES
    #
    # These remain unreachable during R35H because the global firebreaks above
    # intentionally stop execution first.
    # ----------------------------------------------------------------------------------------------

    if state.kill_switch_engaged:

        block(
            "kill switch engaged"
        )

    if state.ambiguous_outcome_block:

        block(
            "ambiguous outcome block"
        )

    if (
        not state.exchange_reconciled
        or
        not state.reconciliation_id
    ):

        block(
            "exchange reconciliation required"
        )

    if (
        envelope.get(
            "reconciliation_id"
        )
        != state.reconciliation_id
    ):

        block(
            "stale reconciliation"
        )

    if (
        state.phase
        != "AUTHORIZED"
        or
        not state.active_authorization
    ):

        block(
            "active authorization required"
        )

    if (
        state.active_authorization.get(
            "intent_id"
        )
        != envelope.get(
            "intent_id"
        )
    ):

        block(
            "authorization intent mismatch"
        )

    if (
        state.active_authorization.get(
            "authorization_id"
        )
        in state.consumed_authorizations
    ):

        block(
            "authorization already consumed"
        )

    # ==============================================================================================
    # FINAL R35H TERMINAL FIREBREAK
    #
    # NO urllib.request.urlopen()
    # NO requests.post()
    # NO exchange HTTP POST
    # NO order transmission
    # ==============================================================================================

    block(
        "R35H live writer terminal firebreak"
    )


# ==================================================================================================
# TELEGRAM REPORT-ONLY BOUNDARY
# ==================================================================================================

def telegram_preview(
    text: str,
) -> Dict[str, Any]:

    return {

        "method":
            "POST",

        "operation":
            "sendMessage",

        "report_only":
            True,

        "exchange_mutation":
            False,

        "execution_control":
            False,

        "chat_id_present":
            bool(
                TELEGRAM_CHAT_ID
            ),

        "bot_token_present":
            bool(
                TELEGRAM_BOT_TOKEN
            ),

        "text":
            text,

    }


def send_telegram_report(
    state: StrategyState,
    text: str,
) -> bool:

    if (
        not TELEGRAM_REPORTING_ENABLED
        or
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):

        return False

    before_phase = (
        state.phase
    )

    before_nonce = (
        state.highest_nonce
    )

    before_writes = (
        state.exchange_network_writes
    )

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        f"sendMessage"
    )

    body = json.dumps(
        {
            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                text,
        }
    ).encode(
        "utf-8"
    )

    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type":
                "application/json"
        },
    )

    try:

        with request.urlopen(
            req,
            timeout=8,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            data = json.loads(
                raw
            )

            ok = bool(
                data.get(
                    "ok"
                )
            )

        if ok:

            state.telegram_success_count += 1

        else:

            state.telegram_failure_count += 1

    except Exception:

        state.telegram_failure_count += 1

        ok = False

    # ----------------------------------------------------------------------------------------------
    # TELEGRAM MAY REPORT.
    # TELEGRAM MAY NEVER CONTROL EXECUTION.
    # ----------------------------------------------------------------------------------------------

    if (
        state.phase
        != before_phase
        or
        state.highest_nonce
        != before_nonce
        or
        state.exchange_network_writes
        != before_writes
    ):

        raise RuntimeError(
            "telegram reporting altered execution state"
        )

    STORE.save(
        state
    )

    return ok


# ==================================================================================================
# KILL SWITCH
# ==================================================================================================

def engage_kill_switch(
    state: StrategyState,
) -> None:

    state.kill_switch_engaged = (
        True
    )

    state.phase = (
        "KILLED"
    )

    STORE.append_event(
        state,
        "KILL_SWITCH_ENGAGED",
        {},
    )


def clear_kill_switch_for_test(
    state: StrategyState,
) -> None:

    state.kill_switch_engaged = (
        False
    )

    state.phase = (
        "RECONCILED"
        if state.exchange_reconciled
        else "INIT"
    )

    STORE.append_event(
        state,
        "KILL_SWITCH_CLEARED_TEST_ONLY",
        {},
    )


# ==================================================================================================
# AMBIGUOUS OUTCOME
# ==================================================================================================

def activate_ambiguous_outcome(
    state: StrategyState,
) -> None:

    state.ambiguous_outcome_block = (
        True
    )

    state.phase = (
        "AMBIGUOUS_BLOCKED"
    )

    STORE.append_event(
        state,
        "AMBIGUOUS_OUTCOME_BLOCKED",
        {},
    )


# ==================================================================================================
# TEST HELPER
# ==================================================================================================

def expect_runtime_error(
    fn: Any,
    contains: Optional[str] = None,
) -> bool:

    try:

        fn()

    except RuntimeError as exc:

        return (
            contains is None
            or
            contains.lower()
            in str(exc).lower()
        )

    return False


# ==================================================================================================
# R35H VALIDATION
# ==================================================================================================

def run_validation() -> StrategyState:

    state = (
        STORE.reset()
    )

    print_header(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: STATE DIR={STATE_DIR}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDER EXECUTION="
        f"{'ENABLED' if REAL_ORDER_EXECUTION else 'DISABLED'}",
        flush=True,
    )

    print(
        f"{VERSION}: EXCHANGE WRITER="
        f"{'ENABLED' if EXCHANGE_WRITER_ENABLED else 'HARD DISABLED'}",
        flush=True,
    )

    print(
        f"{VERSION}: EXCHANGE NETWORK WRITES="
        f"{'ENABLED' if EXCHANGE_NETWORK_WRITES_ENABLED else 'DISABLED'}",
        flush=True,
    )

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    print_header(
        "R35H TEST 1: SAFETY CONSTANTS"
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION
        is False,
    )

    check(
        "Exchange Writer Is Hard Disabled",
        EXCHANGE_WRITER_ENABLED
        is False,
    )

    check(
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    print_header(
        "R35H TEST 2: EXACT WEEX V3 ORDER BOUNDARY"
    )

    check(
        "Order Method Is POST",
        WEEX_ORDER_METHOD
        == "POST",
    )

    check(
        "Order Path Is /capi/v3/order",
        WEEX_ORDER_PATH
        == "/capi/v3/order",
    )

    check(
        "Contract API Base URL Is Present",
        WEEX_BASE_URL
        == "https://api-contract.weex.com",
    )

    check(
        "Writer Boundary Starts With Zero Attempts",
        state.writer_attempt_count
        == 0,
    )

    check(
        "Exchange Network Write Count Starts At Zero",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    print_header(
        "R35H TEST 3: CONTROLLED RECONCILIATION"
    )

    rec = (
        create_reconciliation(
            state,
            TARGET_MARGIN_MODE,
            TARGET_LONG_LEVERAGE,
            TARGET_SHORT_LEVERAGE,
        )
    )

    check(
        "Exchange Reconciliation Was Created",
        bool(
            rec.get(
                "reconciliation_id"
            )
        ),
    )

    check(
        "Reconciliation Is Bound To BTCUSDT",
        rec[
            "symbol"
        ]
        == SYMBOL,
    )

    check(
        "Observed Margin Mode Is ISOLATED",
        state.observed_margin_mode
        == TARGET_MARGIN_MODE,
    )

    check(
        "Observed Long Leverage Is 100x",
        state.observed_long_leverage
        == 100,
    )

    check(
        "Observed Short Leverage Is 100x",
        state.observed_short_leverage
        == 100,
    )

    check(
        "Strategy Entered RECONCILED Phase",
        state.phase
        == "RECONCILED",
    )

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    print_header(
        "R35H TEST 4: HARD EXPOSURE LIMIT"
    )

    enforce_exposure(
        100.0,
        35.0,
    )

    check(
        "Exposure At 35 Percent Is Accepted",
        True,
    )

    rejected = (
        expect_runtime_error(
            lambda:
                enforce_exposure(
                    100.0,
                    35.0001,
                ),
            "exposure",
        )
    )

    check(
        "Exposure Above 35 Percent Is Rejected",
        rejected,
    )

    check(
        "Maximum Fund Exposure Remains 35 Percent",
        MAX_FUND_EXPOSURE_PERCENT
        == 35.0,
    )

    check(
        "Exposure Test Made No Exchange Network Write",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    print_header(
        "R35H TEST 5: RECONCILIATION-BOUND INTENT"
    )

    intent = (
        prepare_intent(
            state,
            side="BUY",
            position_side="LONG",
            quantity=0.0004,
            balance_usdt=7.18945017,
            planned_margin_usdt=0.3186948,
        )
    )

    check(
        "Intent Was Created",
        bool(
            intent.get(
                "intent_id"
            )
        ),
    )

    check(
        "Intent Is Bound To Current Reconciliation",
        intent[
            "reconciliation_id"
        ]
        == state.reconciliation_id,
    )

    check(
        "Intent Is Synthetic Only",
        intent[
            "synthetic_only"
        ]
        is True,
    )

    check(
        "Intent Forbids Transmission",
        intent[
            "transmission_allowed"
        ]
        is False,
    )

    check(
        "Intent Forbids Exchange Network Write",
        intent[
            "exchange_network_write_allowed"
        ]
        is False,
    )

    check(
        "Strategy Entered PREPARED Phase",
        state.phase
        == "PREPARED",
    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    print_header(
        "R35H TEST 6: AUTHORIZATION BINDING"
    )

    auth = (
        authorize_intent(
            state
        )
    )

    check(
        "Authorization Was Created",
        bool(
            auth.get(
                "authorization_id"
            )
        ),
    )

    check(
        "Authorization Binds Exact Intent",
        auth[
            "intent_id"
        ]
        == intent[
            "intent_id"
        ],
    )

    check(
        "Authorization Binds Current Reconciliation",
        auth[
            "reconciliation_id"
        ]
        == state.reconciliation_id,
    )

    check(
        "Authorization Is Initially Unconsumed",
        auth[
            "consumed"
        ]
        is False,
    )

    check(
        "Authorization Explicitly Forbids Live Writer",
        auth[
            "live_writer_allowed"
        ]
        is False,
    )

    check(
        "Strategy Entered AUTHORIZED Phase",
        state.phase
        == "AUTHORIZED",
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    print_header(
        "R35H TEST 7: EXACT V3 PAYLOAD CONSTRUCTION"
    )

    payload = (
        build_weex_order_payload(
            intent
        )
    )

    check(
        "Payload Symbol Is BTCUSDT",
        payload[
            "symbol"
        ]
        == SYMBOL,
    )

    check(
        "Payload Side Is BUY",
        payload[
            "side"
        ]
        == "BUY",
    )

    check(
        "Payload Position Side Is LONG",
        payload[
            "positionSide"
        ]
        == "LONG",
    )

    check(
        "Payload Type Is MARKET",
        payload[
            "type"
        ]
        == "MARKET",
    )

    check(
        "Payload Quantity Is 0.0004",
        payload[
            "quantity"
        ]
        == "0.0004",
    )

    check(
        "Client Order ID Is Present",
        payload[
            "newClientOrderId"
        ].startswith(
            "r35h-"
        ),
    )

    check(
        "Client Order ID Fits V3 Maximum Length",
        len(
            payload[
                "newClientOrderId"
            ]
        )
        <= 36,
    )

    print(
        f"{VERSION}: SYNTHETIC ORDER PAYLOAD="
        f"{canonical_json(payload)}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC PAYLOAD SHA256="
        f"{sha256_hex(payload)}",
        flush=True,
    )

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    print_header(
        "R35H TEST 8: SIGNATURE DETERMINISM"
    )

    fixed_timestamp = (
        "1760000000000"
    )

    body = (
        canonical_json(
            payload
        )
    )

    sig_a = (
        weex_signature(
            "r35h-test-secret",
            fixed_timestamp,
            "POST",
            WEEX_ORDER_PATH,
            body,
        )
    )

    sig_b = (
        weex_signature(
            "r35h-test-secret",
            fixed_timestamp,
            "POST",
            WEEX_ORDER_PATH,
            body,
        )
    )

    sig_c = (
        weex_signature(
            "r35h-test-secret",
            fixed_timestamp,
            "POST",
            WEEX_ORDER_PATH,
            body + " ",
        )
    )

    check(
        "Identical Input Produces Identical Signature",
        sig_a
        == sig_b,
    )

    check(
        "Body Mutation Changes Signature",
        sig_a
        != sig_c,
    )

    check(
        "Signature Is Base64 Text",
        isinstance(
            sig_a,
            str,
        )
        and
        len(
            sig_a
        )
        > 20,
    )

    check(
        "Signature Validation Makes No Exchange Write",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    print_header(
        "R35H TEST 9: SECRET-SAFE WRITER ENVELOPE"
    )

    envelope = (
        build_writer_envelope(
            intent,
            fixed_timestamp,
        )
    )

    preview = (
        writer_preview(
            envelope
        )
    )

    preview_json = (
        canonical_json(
            preview
        )
    )

    check(
        "Writer Envelope Uses POST",
        envelope[
            "method"
        ]
        == "POST",
    )

    check(
        "Writer Envelope Uses Exact V3 Path",
        envelope[
            "request_path"
        ]
        == WEEX_ORDER_PATH,
    )

    check(
        "Writer Envelope Binds Exact Intent",
        envelope[
            "intent_id"
        ]
        == intent[
            "intent_id"
        ],
    )

    check(
        "Writer Envelope Binds Current Reconciliation",
        envelope[
            "reconciliation_id"
        ]
        == state.reconciliation_id,
    )

    check(
        "Writer Preview Marks Transmitted False",
        preview[
            "transmitted"
        ]
        is False,
    )

    check(
        "Writer Preview Redacts Access Key",
        preview[
            "headers"
        ][
            "ACCESS-KEY"
        ]
        == "<redacted>",
    )

    check(
        "Writer Preview Redacts Signature",
        preview[
            "headers"
        ][
            "ACCESS-SIGN"
        ]
        == "<redacted>",
    )

    check(
        "Writer Preview Redacts Passphrase",
        preview[
            "headers"
        ][
            "ACCESS-PASSPHRASE"
        ]
        == "<redacted>",
    )

    check(
        "Writer Preview Does Not Expose Configured Secret",
        (
            not WEEX_SECRET_KEY
            or
            WEEX_SECRET_KEY
            not in preview_json
        ),
    )

    print(
        f"{VERSION}: WRITER PREVIEW="
        f"{preview_json}",
        flush=True,
    )

    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    print_header(
        "R35H TEST 10: HARD-DISABLED LIVE WRITER"
    )

    before_writes = (
        state.exchange_network_writes
    )

    blocked = (
        expect_runtime_error(
            lambda:
                attempt_live_writer(
                    state,
                    envelope,
                ),
            "hard disabled",
        )
    )

    check(
        "Live Writer Attempt Is Rejected",
        blocked,
    )

    check(
        "Writer Attempt Count Increments",
        state.writer_attempt_count
        == 1,
    )

    check(
        "Writer Block Count Increments",
        state.writer_block_count
        == 1,
    )

    check(
        "Live Writer Makes No Exchange Network Write",
        state.exchange_network_writes
        == before_writes
        == 0,
    )

    check(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )

    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    print_header(
        "R35H TEST 11: WRITER CANNOT BYPASS AUTHORIZATION"
    )

    test_state = (
        copy.deepcopy(
            state
        )
    )

    test_state.phase = (
        "RECONCILED"
    )

    test_state.active_authorization = (
        None
    )

    check(
        "Unauthorized Test State Has No Authorization",
        test_state.active_authorization
        is None,
    )

    blocked = (
        expect_runtime_error(
            lambda:
                attempt_live_writer(
                    test_state,
                    envelope,
                )
        )
    )

    check(
        "Unauthorized Writer Attempt Is Rejected",
        blocked,
    )

    check(
        "Unauthorized Attempt Makes No Exchange Write",
        test_state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    print_header(
        "R35H TEST 12: STALE RECONCILIATION CANNOT REACH WRITER"
    )

    stale_envelope = (
        copy.deepcopy(
            envelope
        )
    )

    stale_envelope[
        "reconciliation_id"
    ] = "rec-stale"

    blocked = (
        expect_runtime_error(
            lambda:
                attempt_live_writer(
                    state,
                    stale_envelope,
                )
        )
    )

    check(
        "Stale Writer Envelope Is Rejected",
        blocked,
    )

    check(
        "Stale Writer Envelope Makes No Exchange Write",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    print_header(
        "R35H TEST 13: KILL SWITCH FIREBREAK"
    )

    engage_kill_switch(
        state
    )

    check(
        "Kill Switch Is Engaged",
        state.kill_switch_engaged
        is True,
    )

    blocked_intent = (
        expect_runtime_error(
            lambda:
                prepare_intent(
                    state,
                    side="BUY",
                    position_side="LONG",
                    quantity=0.0004,
                    balance_usdt=7.18945017,
                    planned_margin_usdt=0.3186948,
                ),
            "kill switch",
        )
    )

    check(
        "Kill Switch Blocks New Intent",
        blocked_intent,
    )

    blocked_writer = (
        expect_runtime_error(
            lambda:
                attempt_live_writer(
                    state,
                    envelope,
                )
        )
    )

    check(
        "Kill Switch State Cannot Reach Exchange Writer",
        blocked_writer,
    )

    check(
        "Kill Switch Makes No Exchange Network Write",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    print_header(
        "R35H TEST 14: KILL SWITCH DURABLE RESTART"
    )

    reloaded = (
        STORE.load()
    )

    check(
        "Kill Switch Survives Restart",
        reloaded.kill_switch_engaged
        is True,
    )

    clear_kill_switch_for_test(
        reloaded
    )

    state = (
        reloaded
    )

    check(
        "Test-Only Kill Switch Clear Restores Reconciled Phase",
        state.phase
        == "RECONCILED",
    )

    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    print_header(
        "R35H TEST 15: AMBIGUOUS OUTCOME FAIL-CLOSED"
    )

    activate_ambiguous_outcome(
        state
    )

    check(
        "Ambiguous Outcome Block Is Active",
        state.ambiguous_outcome_block
        is True,
    )

    blocked = (
        expect_runtime_error(
            lambda:
                prepare_intent(
                    state,
                    side="BUY",
                    position_side="LONG",
                    quantity=0.0004,
                    balance_usdt=7.18945017,
                    planned_margin_usdt=0.3186948,
                ),
            "ambiguous",
        )
    )

    check(
        "Ambiguous Outcome Blocks New Intent",
        blocked,
    )

    blocked_writer = (
        expect_runtime_error(
            lambda:
                attempt_live_writer(
                    state,
                    envelope,
                )
        )
    )

    check(
        "Ambiguous Outcome Cannot Reach Writer",
        blocked_writer,
    )

    check(
        "Ambiguous Outcome Makes No Exchange Network Write",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    print_header(
        "R35H TEST 16: AMBIGUOUS OUTCOME REQUIRES FRESH RECONCILIATION"
    )

    restarted = (
        STORE.load()
    )

    check(
        "Ambiguous Block Survives Restart",
        restarted.ambiguous_outcome_block
        is True,
    )

    fresh_rec = (
        create_reconciliation(
            restarted,
            TARGET_MARGIN_MODE,
            TARGET_LONG_LEVERAGE,
            TARGET_SHORT_LEVERAGE,
        )
    )

    state = (
        restarted
    )

    check(
        "Fresh Reconciliation Was Created",
        fresh_rec[
            "reconciliation_id"
        ]
        == state.reconciliation_id,
    )

    check(
        "Fresh Reconciliation Clears Ambiguous Block",
        state.ambiguous_outcome_block
        is False,
    )

    check(
        "Strategy Returns To RECONCILED",
        state.phase
        == "RECONCILED",
    )

    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    print_header(
        "R35H TEST 17: EXACTLY-ONCE SYNTHETIC LIFECYCLE"
    )

    intent2 = (
        prepare_intent(
            state,
            side="BUY",
            position_side="LONG",
            quantity=0.0004,
            balance_usdt=7.18945017,
            planned_margin_usdt=0.3186948,
        )
    )

    auth2 = (
        authorize_intent(
            state
        )
    )

    receipt = (
        synthetic_dispatch(
            state
        )
    )

    check(
        "Synthetic Receipt Was Created",
        bool(
            receipt.get(
                "receipt_id"
            )
        ),
    )

    check(
        "Synthetic Dispatch Was Not Transmitted",
        receipt[
            "transmitted"
        ]
        is False,
    )

    check(
        "Synthetic Dispatch Made No Exchange Network Write",
        receipt[
            "exchange_network_write"
        ]
        is False,
    )

    check(
        "Synthetic Dispatch Count Is One",
        state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Intent Was Consumed",
        intent2[
            "intent_id"
        ]
        in state.consumed_intents,
    )

    check(
        "Authorization Was Consumed",
        auth2[
            "authorization_id"
        ]
        in state.consumed_authorizations,
    )

    check(
        "Strategy Reached COMPLETED",
        state.phase
        == "COMPLETED",
    )

    check(
        "Strategy Is Terminal",
        state.terminal
        is True,
    )

    check(
        "Exchange Network Write Count Remains Zero",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    print_header(
        "R35H TEST 18: RESTART REPLAY PROTECTION"
    )

    restarted = (
        STORE.load()
    )

    check(
        "Completed State Survives Restart",
        restarted.phase
        == "COMPLETED",
    )

    check(
        "Terminal State Survives Restart",
        restarted.terminal
        is True,
    )

    check(
        "Consumed Intent Survives Restart",
        intent2[
            "intent_id"
        ]
        in restarted.consumed_intents,
    )

    check(
        "Consumed Authorization Survives Restart",
        auth2[
            "authorization_id"
        ]
        in restarted.consumed_authorizations,
    )

    check(
        "Durable Receipt Survives Restart",
        any(
            r[
                "receipt_id"
            ]
            == receipt[
                "receipt_id"
            ]
            for r
            in restarted.durable_receipts
        ),
    )

    replay_rejected = (
        expect_runtime_error(
            lambda:
                synthetic_dispatch(
                    restarted
                ),
            "replay",
        )
    )

    check(
        "Restart Replay Is Rejected",
        replay_rejected,
    )

    check(
        "Replay Does Not Duplicate Synthetic Dispatch",
        restarted.synthetic_dispatch_count
        == 1,
    )

    check(
        "Replay Makes No Exchange Network Write",
        restarted.exchange_network_writes
        == 0,
    )

    state = (
        restarted
    )

    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    print_header(
        "R35H TEST 19: TELEGRAM REQUEST BOUNDARY"
    )

    tg_text = (

        f"{VERSION} REPORT\n"

        f"SYMBOL={SYMBOL}\n"

        f"EVENT=R35H_VALIDATION\n"

        f"PHASE={state.phase}\n"

        f"EXCHANGE_NETWORK_WRITES="
        f"{state.exchange_network_writes}\n"

        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}\n"

        f"STATUS="
        f"REAL_WRITER_BOUNDARY_VALIDATED_HARD_DISABLED"

    )

    tg_preview = (
        telegram_preview(
            tg_text
        )
    )

    check(
        "Telegram Uses POST Only For Reporting",
        tg_preview[
            "method"
        ]
        == "POST",
    )

    check(
        "Telegram Operation Is sendMessage",
        tg_preview[
            "operation"
        ]
        == "sendMessage",
    )

    check(
        "Telegram Request Is Marked Report Only",
        tg_preview[
            "report_only"
        ]
        is True,
    )

    check(
        "Telegram Request Is Not Exchange Mutation",
        tg_preview[
            "exchange_mutation"
        ]
        is False,
    )

    check(
        "Telegram Request Cannot Control Execution",
        tg_preview[
            "execution_control"
        ]
        is False,
    )

    check(
        "Telegram Preview Does Not Contain Bot Token",
        (
            not TELEGRAM_BOT_TOKEN
            or
            TELEGRAM_BOT_TOKEN
            not in canonical_json(
                tg_preview
            )
        ),
    )

    check(
        "Telegram Preview Does Not Increment Exchange Writes",
        state.exchange_network_writes
        == 0,
    )

    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    print_header(
        "R35H TEST 20: OPTIONAL LIVE TELEGRAM REPORT DELIVERY"
    )

    phase_before = (
        state.phase
    )

    nonce_before = (
        state.highest_nonce
    )

    writes_before = (
        state.exchange_network_writes
    )

    delivered = (
        send_telegram_report(
            state,
            tg_text,
        )
    )

    if (
        TELEGRAM_REPORTING_ENABLED
        and
        TELEGRAM_BOT_TOKEN
        and
        TELEGRAM_CHAT_ID
    ):

        check(
            "Telegram Delivery Attempt Completed",
            (
                state.telegram_success_count
                +
                state.telegram_failure_count
            )
            >= 1,
        )

        print(
            f"{VERSION}: TELEGRAM DELIVERED={delivered}",
            flush=True,
        )

    else:

        check(
            "Telegram Delivery Safely Skipped Without Complete Configuration",
            delivered
            is False,
        )

    check(
        "Telegram Leaves Strategy Phase Unchanged",
        state.phase
        == phase_before,
    )

    check(
        "Telegram Leaves Strategy Nonce Unchanged",
        state.highest_nonce
        == nonce_before,
    )

    check(
        "Telegram Leaves Exchange Write Count Unchanged",
        state.exchange_network_writes
        == writes_before
        == 0,
    )

    check(
        "Real Order Execution Remains Disabled After Telegram",
        REAL_ORDER_EXECUTION
        is False,
    )

    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    print_header(
        "R35H TEST 21: JOURNAL INTEGRITY"
    )

    (
        journal_valid,
        record_count,
        head_hash,
    ) = STORE.validate_journal(
        state
    )

    check(
        "Durable Journal Contains Records",
        record_count
        > 0,
    )

    check(
        "Journal Hash Chain Is Valid",
        journal_valid,
    )

    check(
        "Journal Sequence Matches State",
        record_count
        == state.journal_sequence,
    )

    check(
        "Journal Head Hash Matches State",
        head_hash
        == state.last_journal_hash,
    )

    check(
        "Journal Head Hash Has Correct Length",
        len(
            head_hash
        )
        == 64,
    )

    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    print_header(
        "R35H TEST 22: FINAL SNAPSHOT INTEGRITY"
    )

    snapshot_core = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "phase":
            state.phase,

        "generation":
            state.generation,

        "epoch":
            state.epoch,

        "exchange_reconciled":
            state.exchange_reconciled,

        "reconciliation_id":
            state.reconciliation_id,

        "synthetic_dispatch_count":
            state.synthetic_dispatch_count,

        "exchange_network_writes":
            state.exchange_network_writes,

        "writer_attempt_count":
            state.writer_attempt_count,

        "writer_block_count":
            state.writer_block_count,

        "real_order_execution":
            REAL_ORDER_EXECUTION,

        "exchange_writer_enabled":
            EXCHANGE_WRITER_ENABLED,

        "exchange_network_writes_enabled":
            EXCHANGE_NETWORK_WRITES_ENABLED,

        "synthetic_transport_only":
            SYNTHETIC_TRANSPORT_ONLY,

        "terminal":
            state.terminal,

        "journal_sequence":
            state.journal_sequence,

        "journal_head_hash":
            state.last_journal_hash,

    }

    snapshot = dict(
        snapshot_core
    )

    snapshot[
        "snapshot_hash"
    ] = sha256_hex(
        snapshot_core
    )

    atomic_write_json(
        SNAPSHOT_FILE,
        snapshot,
    )

    loaded_snapshot = json.loads(
        SNAPSHOT_FILE.read_text(
            encoding="utf-8"
        )
    )

    loaded_hash = (
        loaded_snapshot.pop(
            "snapshot_hash"
        )
    )

    check(
        "Final Snapshot Version Is Correct",
        loaded_snapshot[
            "version"
        ]
        == VERSION,
    )

    check(
        "Final Snapshot Symbol Is Correct",
        loaded_snapshot[
            "symbol"
        ]
        == SYMBOL,
    )

    check(
        "Final Snapshot Integrity Is Valid",
        sha256_hex(
            loaded_snapshot
        )
        == loaded_hash,
    )

    check(
        "Final Snapshot Keeps Exchange Network Write Count At Zero",
        loaded_snapshot[
            "exchange_network_writes"
        ]
        == 0,
    )

    check(
        "Final Snapshot Keeps Exchange Writer Disabled",
        loaded_snapshot[
            "exchange_writer_enabled"
        ]
        is False,
    )

    check(
        "Final Snapshot Keeps Real Orders Disabled",
        loaded_snapshot[
            "real_order_execution"
        ]
        is False,
    )

    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    print_header(
        "R35H TEST 23: FINAL REAL-WRITER FIREBREAK"
    )

    check(
        "No Exchange Network Write Occurred",
        state.exchange_network_writes
        == 0,
    )

    check(
        "Exchange Writer Remains Hard Disabled",
        EXCHANGE_WRITER_ENABLED
        is False,
    )

    check(
        "Exchange Network Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )

    check(
        "Synthetic Transport Only Remains Enabled",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    check(
        "At Least One Live Writer Attempt Was Safely Blocked",
        state.writer_block_count
        >= 1,
    )

    # ==============================================================================================
    # FINAL REPORT
    # ==============================================================================================

    print_header(
        "R35H: VALIDATION SUMMARY"
    )

    report_details = {

        "exchange_network_writes":
            state.exchange_network_writes,

        "exchange_writer_enabled":
            EXCHANGE_WRITER_ENABLED,

        "live_trading":
            REAL_ORDER_EXECUTION,

        "status":
            "REAL_WRITER_BOUNDARY_VALIDATED_HARD_DISABLED",

    }

    print(
        "R35H REPORT",
        flush=True,
    )

    print(
        f"SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        "EVENT=R35H_VALIDATION",
        flush=True,
    )

    print(
        f"PHASE={state.phase}",
        flush=True,
    )

    print(
        f"GENERATION={state.generation}",
        flush=True,
    )

    print(
        f"EPOCH={state.epoch}",
        flush=True,
    )

    print(
        f"EXCHANGE_NETWORK_WRITES="
        f"{state.exchange_network_writes}",
        flush=True,
    )

    print(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}",
        flush=True,
    )

    print(
        f"DETAILS="
        f"{canonical_json(report_details)}",
        flush=True,
    )

    print(
        SEPARATOR,
        flush=True,
    )

    print(
        f"{VERSION}: REAL EXCHANGE WRITER BOUNDARY VALIDATED",
        flush=True,
    )

    print(
        f"{VERSION}: NO EXCHANGE ORDER WAS TRANSMITTED",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE TRADING REMAINS DISABLED",
        flush=True,
    )

    print(
        SEPARATOR,
        flush=True,
    )

    return state


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_loop() -> None:

    heartbeat = 0

    while True:

        time.sleep(
            30
        )

        heartbeat += 1

        try:

            state = (
                STORE.load()
            )

            print(
                f"{VERSION}: HEARTBEAT={heartbeat} "
                f"PHASE={state.phase} "
                f"EXCHANGE_WRITES={state.exchange_network_writes} "
                f"WRITER_ENABLED={EXCHANGE_WRITER_ENABLED} "
                f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}",
                flush=True,
            )

        except Exception as exc:

            print(
                f"{VERSION}: HEARTBEAT ERROR={exc}",
                flush=True,
            )


# ==================================================================================================
# MAIN
# ==================================================================================================

def main() -> None:

    start_health_server()

    run_validation()

    heartbeat_loop()


if __name__ == "__main__":

    main()
