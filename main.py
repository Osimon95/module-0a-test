

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import shutil
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35I - CORRECTED LIVE ACTIVATION GATE + TELEGRAM REPORTING + DURABLE JOURNAL VALIDATION
# ==================================================================================================
#
# IMPORTANT SAFETY MODEL
#
#   THIS BUILD DOES NOT PLACE REAL ORDERS.
#
#   EXCHANGE WRITER                 = HARD DISABLED
#   EXCHANGE NETWORK WRITES         = HARD DISABLED
#   EXCHANGE POST                   = HARD DISABLED
#   EXCHANGE PUT                    = HARD DISABLED
#   EXCHANGE PATCH                  = HARD DISABLED
#   EXCHANGE DELETE                 = HARD DISABLED
#   REAL ORDER EXECUTION            = HARD DISABLED
#   DEMO ORDER EXECUTION            = HARD DISABLED
#   FIRST REAL ORDER                = HARD DISABLED
#
#   AUTHENTICATED WEEX GET REQUESTS = ENABLED
#   PUBLIC WEEX GET REQUESTS        = ENABLED
#
#   TELEGRAM POST MAY BE ENABLED.
#   TELEGRAM POST IS REPORTING ONLY.
#   TELEGRAM CAN NEVER CONTROL EXECUTION.
#
#
# R35I CORRECTIONS
#
#   1. Journal writer and journal verifier now use exactly the same canonical hash algorithm.
#
#   2. A journal created by an incompatible earlier R35I build is quarantined before the corrected
#      journal is created. The old file is preserved with a ".legacy-invalid-<timestamp>" suffix.
#
#   3. Authenticated account reads use the WEEX V3 endpoints:
#
#          GET /capi/v3/account/balance
#          GET /capi/v3/account/position/allPosition
#          GET /capi/v3/account/symbolConfig
#
#   4. No validation-only balance fallback is accepted.
#
#   5. Telegram reporting is enabled automatically when both Telegram token and chat ID exist,
#      unless TELEGRAM_REPORTING_ENABLED explicitly disables it.
#
#   6. Telegram delivery is only PASS when Telegram returns a successful sendMessage response.
#
#   7. Telegram POST does NOT increment exchange_network_writes.
#
#   8. Writer envelope construction remains synthetic/local only.
#
#   9. No function in this file can transmit an exchange mutation.
#
# ==================================================================================================


VERSION = "R35I"
SYMBOL = os.environ.get("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"

HEALTH_PORT = int(os.environ.get("PORT", "10000"))

STATE_DIR = Path(
    os.environ.get(
        "R35I_STATE_DIR",
        "/tmp/r35i_state",
    )
)

STATE_FILE = STATE_DIR / "state.json"
JOURNAL_FILE = STATE_DIR / "journal.jsonl"


# ==================================================================================================
# WEEX CONFIGURATION
# ==================================================================================================


WEEX_BASE_URL = (
    os.environ.get(
        "WEEX_BASE_URL",
        "https://api-contract.weex.com",
    )
    .strip()
    .rstrip("/")
)


def first_env(*names: str) -> str:

    for name in names:

        value = os.environ.get(name)

        if value is not None and value.strip():

            return value.strip()

    return ""


WEEX_API_KEY = first_env(
    "WEEX_API_KEY",
    "API_KEY",
    "ACCESS_KEY",
)

WEEX_SECRET_KEY = first_env(
    "WEEX_SECRET_KEY",
    "WEEX_API_SECRET",
    "API_SECRET",
    "SECRET_KEY",
)

WEEX_PASSPHRASE = first_env(
    "WEEX_PASSPHRASE",
    "WEEX_API_PASSPHRASE",
    "API_PASSPHRASE",
    "PASSPHRASE",
)


# ==================================================================================================
# TELEGRAM CONFIGURATION
# ==================================================================================================


TELEGRAM_BOT_TOKEN = first_env(
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_TOKEN",
    "BOT_TOKEN",
)

TELEGRAM_CHAT_ID = first_env(
    "TELEGRAM_CHAT_ID",
    "CHAT_ID",
)


def env_bool(
    name: str,
    default: bool,
) -> bool:

    raw = os.environ.get(name)

    if raw is None:

        return default

    return raw.strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
        "enabled",
    }


TELEGRAM_CREDENTIALS_PRESENT = bool(
    TELEGRAM_BOT_TOKEN
    and TELEGRAM_CHAT_ID
)

TELEGRAM_REPORTING_ENABLED = env_bool(
    "TELEGRAM_REPORTING_ENABLED",
    TELEGRAM_CREDENTIALS_PRESENT,
)


# ==================================================================================================
# HARD SAFETY CONSTANTS
# ==================================================================================================


AUTHENTICATED_READS_ENABLED = True
PUBLIC_READS_ENABLED = True

LIVE_ACTIVATION_GATE_PRESENT = True

EXCHANGE_WRITER_ENABLED = False
EXCHANGE_NETWORK_WRITES_ENABLED = False

EXCHANGE_POST_ENABLED = False
EXCHANGE_PUT_ENABLED = False
EXCHANGE_PATCH_ENABLED = False
EXCHANGE_DELETE_ENABLED = False

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

FIRST_REAL_ORDER_ALLOWED = False

SYNTHETIC_TRANSPORT_ONLY = True

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

MAX_FUND_EXPOSURE_PERCENT = 35.0

INITIAL_ENTRY_PERCENT = 5.0
PYRAMID_PERCENT = 5.0
BACKUP_PERCENT = 5.0

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

PLANNED_LEVERAGE = 100

RECONCILIATION_MAX_AGE_SECONDS = 120

HTTP_TIMEOUT_SECONDS = 12


# ==================================================================================================
# CURRENT WEEX V3 PATHS
# ==================================================================================================


BALANCE_PATH = "/capi/v3/account/balance"

POSITIONS_PATH = "/capi/v3/account/position/allPosition"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

SYMBOL_PRICE_PATH = "/capi/v3/market/symbolPrice"

ORDER_PATH = "/capi/v3/order"


# ==================================================================================================
# TERMINAL OUTPUT
# ==================================================================================================


DIVIDER = "-" * 100


def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="microseconds"
    ).replace(
        "+00:00",
        "Z",
    )


def log(
    message: str = "",
) -> None:

    if message:

        print(
            f"{utc_now()} {message}",
            flush=True,
        )

    else:

        print(
            utc_now(),
            flush=True,
        )


def section(
    title: str,
) -> None:

    log(DIVIDER)
    log(title)
    log(DIVIDER)


def check(
    label: str,
    condition: bool,
) -> None:

    status = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    log(
        f"{label:<85} {status}"
    )

    if not condition:

        raise AssertionError(
            label
        )


# ==================================================================================================
# CANONICAL JSON + HASHING
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


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def hash_object(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(value)
    )


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = "BOOT"

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    live_mode_armed: bool = False

    kill_switch: bool = False

    ambiguous_outcome_block: bool = False

    exchange_network_writes: int = 0

    real_order_execution: bool = False

    demo_order_execution: bool = False

    first_real_order_allowed: bool = False

    reconciliation: Optional[
        Dict[str, Any]
    ] = None

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

    used_client_order_ids: List[str] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    last_journal_hash: str = "0" * 64

    journal_sequence: int = 0

    telegram_delivery_count: int = 0

    telegram_last_delivery_ok: bool = False

    terminal: bool = False


STATE_LOCK = threading.RLock()


def state_to_dict(
    state: StrategyState,
) -> Dict[str, Any]:

    return asdict(
        state
    )


def write_json_atomic(
    path: Path,
    value: Any,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    encoded = (
        canonical_json(value)
        + "\n"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(
            encoded
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temporary,
        path,
    )


def save_state(
    state: StrategyState,
) -> None:

    with STATE_LOCK:

        write_json_atomic(
            STATE_FILE,
            state_to_dict(state),
        )


def load_state() -> StrategyState:

    if not STATE_FILE.exists():

        return StrategyState()

    try:

        with STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:

            raw = json.load(
                handle
            )

        allowed = {
            field_name
            for field_name in StrategyState.__dataclass_fields__
        }

        cleaned = {
            key: value
            for key, value in raw.items()
            if key in allowed
        }

        state = StrategyState(
            **cleaned
        )

        if state.version != VERSION:

            return StrategyState()

        if state.symbol != SYMBOL:

            return StrategyState()

        return state

    except Exception as exc:

        log(
            f"{VERSION}: STATE LOAD WARNING="
            f"{type(exc).__name__}: {exc}"
        )

        return StrategyState()


# ==================================================================================================
# JOURNAL
# ==================================================================================================
#
# HASH RULE
#
#   hash_payload =
#
#       {
#           "sequence": sequence,
#           "timestamp": timestamp,
#           "event": event,
#           "details": details,
#           "previous_hash": previous_hash
#       }
#
#   record_hash = SHA256(canonical_json(hash_payload))
#
# The verifier reconstructs EXACTLY the same payload.
#
# ==================================================================================================


def journal_hash_payload(
    *,
    sequence: int,
    timestamp: str,
    event: str,
    details: Dict[str, Any],
    previous_hash: str,
) -> Dict[str, Any]:

    return {
        "sequence": sequence,
        "timestamp": timestamp,
        "event": event,
        "details": details,
        "previous_hash": previous_hash,
    }


def calculate_journal_hash(
    *,
    sequence: int,
    timestamp: str,
    event: str,
    details: Dict[str, Any],
    previous_hash: str,
) -> str:

    payload = journal_hash_payload(
        sequence=sequence,
        timestamp=timestamp,
        event=event,
        details=details,
        previous_hash=previous_hash,
    )

    return hash_object(
        payload
    )


def append_journal(
    state: StrategyState,
    event: str,
    details: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:

    with STATE_LOCK:

        if details is None:

            details = {}

        sequence = (
            state.journal_sequence
            + 1
        )

        timestamp = utc_now()

        previous_hash = (
            state.last_journal_hash
        )

        record_hash = calculate_journal_hash(
            sequence=sequence,
            timestamp=timestamp,
            event=event,
            details=details,
            previous_hash=previous_hash,
        )

        record = {
            "sequence": sequence,
            "timestamp": timestamp,
            "event": event,
            "details": details,
            "previous_hash": previous_hash,
            "record_hash": record_hash,
        }

        JOURNAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        encoded = (
            canonical_json(record)
            + "\n"
        )

        with JOURNAL_FILE.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                encoded
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

        save_state(
            state
        )

        return record


def read_journal() -> List[
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

        for line_number, line in enumerate(
            handle,
            start=1,
        ):

            line = line.strip()

            if not line:

                continue

            try:

                record = json.loads(
                    line
                )

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    f"invalid journal JSON at line "
                    f"{line_number}: {exc}"
                ) from exc

            records.append(
                record
            )

    return records


def validate_journal_records(
    records: List[
        Dict[str, Any]
    ],
) -> Tuple[
    bool,
    str,
    int,
    str,
]:

    expected_previous_hash = (
        "0" * 64
    )

    expected_sequence = 1

    if not records:

        return (
            True,
            "empty journal",
            0,
            expected_previous_hash,
        )

    for index, record in enumerate(
        records,
        start=1,
    ):

        required = {
            "sequence",
            "timestamp",
            "event",
            "details",
            "previous_hash",
            "record_hash",
        }

        missing = (
            required
            - set(record.keys())
        )

        if missing:

            return (
                False,
                f"record {index} missing "
                f"{sorted(missing)}",
                expected_sequence - 1,
                expected_previous_hash,
            )

        sequence = record[
            "sequence"
        ]

        timestamp = record[
            "timestamp"
        ]

        event = record[
            "event"
        ]

        details = record[
            "details"
        ]

        previous_hash = record[
            "previous_hash"
        ]

        record_hash = record[
            "record_hash"
        ]

        if sequence != expected_sequence:

            return (
                False,
                f"record {index} sequence mismatch",
                expected_sequence - 1,
                expected_previous_hash,
            )

        if previous_hash != expected_previous_hash:

            return (
                False,
                f"record {index} previous hash mismatch",
                expected_sequence - 1,
                expected_previous_hash,
            )

        recalculated = calculate_journal_hash(
            sequence=sequence,
            timestamp=timestamp,
            event=event,
            details=details,
            previous_hash=previous_hash,
        )

        if not hmac.compare_digest(
            str(record_hash),
            recalculated,
        ):

            return (
                False,
                f"record {index} record hash mismatch",
                expected_sequence - 1,
                expected_previous_hash,
            )

        expected_previous_hash = (
            recalculated
        )

        expected_sequence += 1

    return (
        True,
        "valid",
        expected_sequence - 1,
        expected_previous_hash,
    )


def validate_journal_file() -> Tuple[
    bool,
    str,
    int,
    str,
]:

    try:

        records = read_journal()

    except Exception as exc:

        return (
            False,
            f"{type(exc).__name__}: {exc}",
            0,
            "0" * 64,
        )

    return validate_journal_records(
        records
    )


def quarantine_incompatible_journal(
    state: StrategyState,
) -> bool:

    if not JOURNAL_FILE.exists():

        return False

    valid, reason, _, _ = (
        validate_journal_file()
    )

    if valid:

        return False

    #
    # R35I is still a zero-exchange-write validation build.
    # We preserve an incompatible journal rather than deleting it.
    #

    if state.exchange_network_writes != 0:

        raise RuntimeError(
            "journal invalid while exchange write count "
            "is non-zero; refusing automatic migration"
        )

    if state.real_order_execution:

        raise RuntimeError(
            "journal invalid while real order execution "
            "is recorded; refusing automatic migration"
        )

    timestamp = str(
        int(time.time() * 1000)
    )

    archive = JOURNAL_FILE.with_name(
        f"{JOURNAL_FILE.name}."
        f"legacy-invalid-{timestamp}"
    )

    shutil.move(
        str(JOURNAL_FILE),
        str(archive),
    )

    log(
        f"{VERSION}: LEGACY JOURNAL QUARANTINED="
        f"{archive}"
    )

    log(
        f"{VERSION}: LEGACY JOURNAL REASON="
        f"{reason}"
    )

    state.journal_sequence = 0
    state.last_journal_hash = (
        "0" * 64
    )

    save_state(
        state
    )

    append_journal(
        state,
        "LEGACY_JOURNAL_QUARANTINED",
        {
            "reason": reason,
            "archived_filename": archive.name,
            "exchange_network_writes": 0,
            "real_order_execution": False,
        },
    )

    return True


def reconcile_state_with_valid_journal(
    state: StrategyState,
) -> None:

    valid, reason, sequence, last_hash = (
        validate_journal_file()
    )

    if not valid:

        raise RuntimeError(
            f"journal invalid after migration: {reason}"
        )

    state.journal_sequence = (
        sequence
    )

    state.last_journal_hash = (
        last_hash
    )

    save_state(
        state
    )


# ==================================================================================================
# HTTP GET
# ==================================================================================================


def public_get_json(
    path: str,
    query: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not PUBLIC_READS_ENABLED:

        raise RuntimeError(
            "public reads disabled"
        )

    query_string = ""

    if query:

        query_string = urllib.parse.urlencode(
            query
        )

    url = (
        WEEX_BASE_URL
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"{VERSION}-validation",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=HTTP_TIMEOUT_SECONDS,
    ) as response:

        body = response.read().decode(
            "utf-8"
        )

    return json.loads(
        body
    )


# ==================================================================================================
# WEEX SIGNATURE
# ==================================================================================================


def require_weex_credentials() -> None:

    missing: List[str] = []

    if not WEEX_API_KEY:

        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_SECRET_KEY:

        missing.append(
            "WEEX_SECRET_KEY"
        )

    if not WEEX_PASSPHRASE:

        missing.append(
            "WEEX_PASSPHRASE"
        )

    if missing:

        raise RuntimeError(
            "missing WEEX credentials: "
            + ", ".join(missing)
        )


def make_weex_signature(
    *,
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    if query_string:

        message = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        message = (
            timestamp
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        WEEX_SECRET_KEY.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "ascii"
    )


def authenticated_get_json(
    path: str,
    query: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not AUTHENTICATED_READS_ENABLED:

        raise RuntimeError(
            "authenticated reads disabled"
        )

    require_weex_credentials()

    query_string = ""

    if query:

        query_string = urllib.parse.urlencode(
            query
        )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = make_weex_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
    )

    url = (
        WEEX_BASE_URL
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "locale": "en-US",
        "User-Agent": f"{VERSION}-validation",
    }

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            body = response.read().decode(
                "utf-8"
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:

            error_body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            pass

        raise RuntimeError(
            f"WEEX GET {path} failed "
            f"HTTP {exc.code}: "
            f"{error_body[:500]}"
        ) from exc

    return json.loads(
        body
    )


# ==================================================================================================
# ACCOUNT PARSERS
# ==================================================================================================


def extract_available_usdt(
    payload: Any,
) -> float:

    rows: List[Any]

    if isinstance(
        payload,
        list,
    ):

        rows = payload

    elif isinstance(
        payload,
        dict,
    ):

        data = payload.get(
            "data",
            payload,
        )

        if isinstance(
            data,
            list,
        ):

            rows = data

        elif isinstance(
            data,
            dict,
        ):

            rows = [
                data
            ]

        else:

            rows = []

    else:

        rows = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        asset = str(
            row.get(
                "asset",
                "",
            )
        ).upper()

        if asset != "USDT":

            continue

        raw = row.get(
            "availableBalance"
        )

        if raw is None:

            raw = row.get(
                "available"
            )

        if raw is None:

            continue

        return float(
            raw
        )

    raise RuntimeError(
        "USDT availableBalance not found "
        "in WEEX balance response"
    )


def extract_open_positions(
    payload: Any,
) -> List[
    Dict[str, Any]
]:

    rows: Any = payload

    if isinstance(
        payload,
        dict,
    ):

        rows = payload.get(
            "data",
            payload.get(
                "positions",
                [],
            ),
        )

    if not isinstance(
        rows,
        list,
    ):

        raise RuntimeError(
            "unexpected WEEX positions response"
        )

    open_positions: List[
        Dict[str, Any]
    ] = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        if str(
            row.get(
                "symbol",
                "",
            )
        ).upper() != SYMBOL:

            continue

        size_raw = row.get(
            "size",
            row.get(
                "quantity",
                "0",
            ),
        )

        try:

            size = abs(
                float(size_raw)
            )

        except Exception:

            size = 0.0

        if size > 0:

            open_positions.append(
                row
            )

    return open_positions


def extract_symbol_config(
    payload: Any,
) -> Dict[str, Any]:

    rows: Any = payload

    if isinstance(
        payload,
        dict,
    ):

        data = payload.get(
            "data"
        )

        if data is not None:

            rows = data

    if isinstance(
        rows,
        dict,
    ):

        rows = [
            rows
        ]

    if not isinstance(
        rows,
        list,
    ):

        raise RuntimeError(
            "unexpected symbol config response"
        )

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        if str(
            row.get(
                "symbol",
                "",
            )
        ).upper() == SYMBOL:

            return row

    raise RuntimeError(
        f"{SYMBOL} symbol config not found"
    )


def obtain_mark_price() -> float:

    payload = public_get_json(
        SYMBOL_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    if isinstance(
        payload,
        dict,
    ):

        if "data" in payload:

            data = payload[
                "data"
            ]

            if isinstance(
                data,
                dict,
            ):

                payload = data

        raw = payload.get(
            "price"
        )

        if raw is not None:

            price = float(
                raw
            )

            if price > 0:

                return price

    raise RuntimeError(
        "valid mark price not found"
    )


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================
#
# Telegram is the ONLY POST transport implemented in R35I.
#
# The Telegram function cannot access an exchange writer because no exchange writer exists.
#
# ==================================================================================================


def telegram_configuration_status() -> Tuple[
    bool,
    str,
]:

    if not TELEGRAM_REPORTING_ENABLED:

        return (
            False,
            "TELEGRAM_REPORTING_ENABLED is false",
        )

    if not TELEGRAM_BOT_TOKEN:

        return (
            False,
            "Telegram bot token missing",
        )

    if not TELEGRAM_CHAT_ID:

        return (
            False,
            "Telegram chat ID missing",
        )

    return (
        True,
        "configured",
    )


def telegram_send_message(
    message: str,
) -> Tuple[
    bool,
    str,
]:

    configured, reason = (
        telegram_configuration_status()
    )

    if not configured:

        return (
            False,
            reason,
        )

    #
    # Telegram only.
    #
    # This URL is not an exchange URL.
    #

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    form = urllib.parse.urlencode(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        url=url,
        data=form,
        method="POST",
        headers={
            "Content-Type": (
                "application/"
                "x-www-form-urlencoded"
            ),
            "User-Agent": (
                f"{VERSION}-telegram-reporting"
            ),
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

        payload = json.loads(
            raw
        )

    except urllib.error.HTTPError as exc:

        body = ""

        try:

            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:

            pass

        return (
            False,
            f"Telegram HTTP {exc.code}: "
            f"{body[:300]}",
        )

    except Exception as exc:

        return (
            False,
            f"{type(exc).__name__}: {exc}",
        )

    if not isinstance(
        payload,
        dict,
    ):

        return (
            False,
            "Telegram returned non-object JSON",
        )

    if payload.get(
        "ok"
    ) is not True:

        description = payload.get(
            "description",
            "Telegram ok=false",
        )

        return (
            False,
            str(description),
        )

    result = payload.get(
        "result",
        {},
    )

    message_id = None

    if isinstance(
        result,
        dict,
    ):

        message_id = result.get(
            "message_id"
        )

    return (
        True,
        f"message_id={message_id}",
    )


def telegram_preview() -> Dict[
    str,
    Any
]:

    return {
        "method": "POST",
        "operation": "sendMessage",
        "report_only": True,
        "exchange_mutation": False,
        "can_control_execution": False,
        "bot_token": (
            "<redacted>"
            if TELEGRAM_BOT_TOKEN
            else "<missing>"
        ),
        "chat_id_present": bool(
            TELEGRAM_CHAT_ID
        ),
    }


# ==================================================================================================
# RECONCILIATION
# ==================================================================================================


def make_reconciliation(
    *,
    state: StrategyState,
    balance: float,
    mark_price: float,
    positions: List[
        Dict[str, Any]
    ],
    symbol_config: Dict[str, Any],
) -> Dict[str, Any]:

    timestamp_ms = int(
        time.time() * 1000
    )

    body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "timestamp_ms": timestamp_ms,
        "available_balance": balance,
        "mark_price": mark_price,
        "open_position_count": len(
            positions
        ),
        "symbol_config_hash": hash_object(
            symbol_config
        ),
    }

    reconciliation_hash = (
        hash_object(body)
    )

    reconciliation_id = (
        "rec-"
        + reconciliation_hash[:20]
    )

    result = {
        **body,
        "reconciliation_id": (
            reconciliation_id
        ),
        "reconciliation_hash": (
            reconciliation_hash
        ),
    }

    return result


def reconciliation_is_fresh(
    reconciliation: Dict[
        str,
        Any
    ],
) -> bool:

    timestamp_ms = int(
        reconciliation.get(
            "timestamp_ms",
            0,
        )
    )

    age_ms = (
        int(time.time() * 1000)
        - timestamp_ms
    )

    return (
        0
        <= age_ms
        <= (
            RECONCILIATION_MAX_AGE_SECONDS
            * 1000
        )
    )


# ==================================================================================================
# LIVE MODE GATE
# ==================================================================================================


def arm_live_mode(
    state: StrategyState,
) -> None:

    #
    # IMPORTANT:
    #
    # "live_mode_armed" in R35I means the validation gate is armed.
    # It DOES NOT enable any writer.
    #

    if state.kill_switch:

        raise RuntimeError(
            "kill switch active"
        )

    if state.ambiguous_outcome_block:

        raise RuntimeError(
            "ambiguous outcome block active"
        )

    state.live_mode_armed = True

    state.phase = "ARMED"

    save_state(
        state
    )

    append_journal(
        state,
        "LIVE_GATE_ARMED",
        {
            "exchange_writer_enabled": False,
            "exchange_network_writes_enabled": False,
            "real_order_execution": False,
        },
    )


# ==================================================================================================
# ORDER INTENT
# ==================================================================================================


def normalize_quantity(
    quantity: float,
) -> float:

    #
    # Existing BTCUSDT validation assumption:
    # 4 decimal quantity precision.
    #

    normalized = round(
        quantity,
        4,
    )

    if normalized < 0.0001:

        normalized = 0.0001

    return normalized


def make_order_intent(
    *,
    state: StrategyState,
    balance: float,
    mark_price: float,
    reconciliation: Dict[
        str,
        Any
    ],
) -> Dict[str, Any]:

    if not state.live_mode_armed:

        raise RuntimeError(
            "live validation gate not armed"
        )

    if not reconciliation_is_fresh(
        reconciliation
    ):

        raise RuntimeError(
            "reconciliation is stale"
        )

    margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / 100.0
    )

    notional = (
        margin
        * PLANNED_LEVERAGE
    )

    quantity = normalize_quantity(
        notional
        / mark_price
    )

    intent_body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "nonce": state.highest_nonce + 1,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": (
            f"{quantity:.4f}"
        ),
        "transmission_permitted": False,
        "exchange_network_write_permitted": False,
        "real_order_permitted": False,
        "reconciliation_id": reconciliation[
            "reconciliation_id"
        ],
        "reconciliation_hash": reconciliation[
            "reconciliation_hash"
        ],
    }

    intent_hash = hash_object(
        intent_body
    )

    intent = {
        **intent_body,
        "intent_id": (
            "int-"
            + intent_hash[:20]
        ),
        "intent_hash": intent_hash,
    }

    state.highest_nonce = int(
        intent[
            "nonce"
        ]
    )

    state.active_intent = intent

    state.phase = "INTENT_PREPARED"

    save_state(
        state
    )

    append_journal(
        state,
        "ORDER_INTENT_CREATED",
        {
            "intent_id": intent[
                "intent_id"
            ],
            "intent_hash": intent[
                "intent_hash"
            ],
            "transmission_permitted": False,
        },
    )

    return intent


# ==================================================================================================
# ONE-TIME AUTHORIZATION
# ==================================================================================================


def make_authorization(
    state: StrategyState,
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    if intent[
        "intent_id"
    ] in state.consumed_intents:

        raise RuntimeError(
            "intent already consumed"
        )

    body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "intent_id": intent[
            "intent_id"
        ],
        "intent_hash": intent[
            "intent_hash"
        ],
        "one_time": True,
        "transmission_permitted": False,
        "exchange_writer_permitted": False,
        "real_order_permitted": False,
    }

    authorization_hash = (
        hash_object(body)
    )

    authorization = {
        **body,
        "authorization_id": (
            "auth-"
            + authorization_hash[:20]
        ),
        "authorization_hash": (
            authorization_hash
        ),
    }

    state.active_authorization = (
        authorization
    )

    state.phase = "AUTHORIZED"

    save_state(
        state
    )

    append_journal(
        state,
        "AUTHORIZATION_CREATED",
        {
            "authorization_id": (
                authorization[
                    "authorization_id"
                ]
            ),
            "authorization_hash": (
                authorization[
                    "authorization_hash"
                ]
            ),
            "transmission_permitted": False,
        },
    )

    return authorization


# ==================================================================================================
# IDEMPOTENT CLIENT ORDER ID
# ==================================================================================================


def make_client_order_id(
    intent: Dict[str, Any],
) -> str:

    material = {
        "version": VERSION,
        "symbol": SYMBOL,
        "intent_id": intent[
            "intent_id"
        ],
        "intent_hash": intent[
            "intent_hash"
        ],
    }

    digest = hash_object(
        material
    )

    return (
        "r35i-"
        + digest[:20]
    )


# ==================================================================================================
# SECRET-SAFE SYNTHETIC WRITER ENVELOPE
# ==================================================================================================
#
# THIS FUNCTION DOES NOT TRANSMIT.
#
# It validates what a future writer boundary would receive.
#
# ==================================================================================================


def build_writer_envelope(
    *,
    state: StrategyState,
    reconciliation: Dict[
        str,
        Any
    ],
    intent: Dict[
        str,
        Any
    ],
    authorization: Dict[
        str,
        Any
    ],
    client_order_id: str,
) -> Dict[str, Any]:

    #
    # Fixed placeholder timestamp is deliberately used here.
    # No usable live exchange signature is produced.
    #

    validation_timestamp = (
        "1760000000000"
    )

    payload = {
        "symbol": SYMBOL,
        "side": intent[
            "side"
        ],
        "positionSide": intent[
            "positionSide"
        ],
        "type": intent[
            "type"
        ],
        "quantity": intent[
            "quantity"
        ],
        "newClientOrderId": (
            client_order_id
        ),
    }

    envelope_core = {
        "method": "POST",
        "request_path": ORDER_PATH,
        "payload": payload,
        "intent_id": intent[
            "intent_id"
        ],
        "intent_hash": intent[
            "intent_hash"
        ],
        "authorization_id": (
            authorization[
                "authorization_id"
            ]
        ),
        "authorization_hash": (
            authorization[
                "authorization_hash"
            ]
        ),
        "reconciliation_id": (
            reconciliation[
                "reconciliation_id"
            ]
        ),
        "reconciliation_hash": (
            reconciliation[
                "reconciliation_hash"
            ]
        ),
        "exchange_writer_enabled": False,
        "exchange_network_writes_enabled": False,
        "real_order_execution": False,
        "first_real_order_allowed": False,
        "live_mode_armed": (
            state.live_mode_armed
        ),
        "transmitted": False,
    }

    envelope_hash = hash_object(
        envelope_core
    )

    #
    # No real signature.
    #
    # These values only prove that secrets would be redacted.
    #

    envelope = {
        **envelope_core,
        "url": (
            WEEX_BASE_URL
            + ORDER_PATH
        ),
        "headers": {
            "ACCESS-KEY": "<redacted>",
            "ACCESS-SIGN": "<redacted>",
            "ACCESS-PASSPHRASE": (
                "<redacted>"
            ),
            "ACCESS-TIMESTAMP": (
                validation_timestamp
            ),
            "Content-Type": (
                "application/json"
            ),
            "locale": "en-US",
        },
        "envelope_hash": (
            envelope_hash
        ),
    }

    return envelope


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================


def synthetic_dispatch(
    *,
    state: StrategyState,
    intent: Dict[
        str,
        Any
    ],
    authorization: Dict[
        str,
        Any
    ],
    client_order_id: str,
    envelope: Dict[
        str,
        Any
    ],
) -> Dict[str, Any]:

    if EXCHANGE_WRITER_ENABLED:

        raise RuntimeError(
            "R35I safety violation: "
            "writer unexpectedly enabled"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:

        raise RuntimeError(
            "R35I safety violation: "
            "network writes unexpectedly enabled"
        )

    if REAL_ORDER_EXECUTION:

        raise RuntimeError(
            "R35I safety violation: "
            "real execution unexpectedly enabled"
        )

    if FIRST_REAL_ORDER_ALLOWED:

        raise RuntimeError(
            "R35I safety violation: "
            "first real order unexpectedly allowed"
        )

    if envelope.get(
        "transmitted"
    ):

        raise RuntimeError(
            "envelope already transmitted"
        )

    if intent[
        "intent_id"
    ] in state.consumed_intents:

        raise RuntimeError(
            "intent replay"
        )

    if authorization[
        "authorization_id"
    ] in state.consumed_authorizations:

        raise RuntimeError(
            "authorization replay"
        )

    if (
        client_order_id
        in state.used_client_order_ids
    ):

        raise RuntimeError(
            "client order ID replay"
        )

    receipt_body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "intent_id": intent[
            "intent_id"
        ],
        "authorization_id": (
            authorization[
                "authorization_id"
            ]
        ),
        "client_order_id": (
            client_order_id
        ),
        "envelope_hash": (
            envelope[
                "envelope_hash"
            ]
        ),
        "synthetic": True,
        "transmitted": False,
        "exchange_network_write": False,
        "real_order": False,
        "timestamp": utc_now(),
    }

    receipt_hash = hash_object(
        receipt_body
    )

    receipt = {
        **receipt_body,
        "receipt_id": (
            "rcpt-"
            + receipt_hash[:20]
        ),
        "receipt_hash": (
            receipt_hash
        ),
    }

    state.consumed_intents.append(
        intent[
            "intent_id"
        ]
    )

    state.consumed_authorizations.append(
        authorization[
            "authorization_id"
        ]
    )

    state.used_client_order_ids.append(
        client_order_id
    )

    state.durable_receipts.append(
        receipt
    )

    state.active_intent = None
    state.active_authorization = None

    state.phase = "SYNTHETIC_DISPATCHED"

    save_state(
        state
    )

    append_journal(
        state,
        "SYNTHETIC_DISPATCH_COMPLETED",
        {
            "receipt_id": receipt[
                "receipt_id"
            ],
            "receipt_hash": receipt[
                "receipt_hash"
            ],
            "transmitted": False,
            "exchange_network_write": False,
            "real_order": False,
        },
    )

    return receipt


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


HEALTH_STATE = {
    "version": VERSION,
    "symbol": SYMBOL,
    "status": "starting",
    "exchange_network_writes": 0,
    "real_order_execution": False,
}


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        if self.path not in {
            "/",
            "/health",
            "/healthz",
        }:

            self.send_response(
                404
            )

            self.end_headers()

            return

        body = json.dumps(
            HEALTH_STATE,
            sort_keys=True,
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
            str(len(body)),
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

    log(
        f"{VERSION}: HEALTH SERVER STARTED "
        f"ON PORT {HEALTH_PORT}"
    )


# ==================================================================================================
# VALIDATION
# ==================================================================================================


def run_validation() -> None:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    state = load_state()

    #
    # Force hard safety values back to zero/false on every R35I startup.
    #

    state.version = VERSION
    state.symbol = SYMBOL

    state.exchange_network_writes = 0
    state.real_order_execution = False
    state.demo_order_execution = False
    state.first_real_order_allowed = False

    state.kill_switch = False
    state.ambiguous_outcome_block = False

    save_state(
        state
    )

    migrated = (
        quarantine_incompatible_journal(
            state
        )
    )

    reconcile_state_with_valid_journal(
        state
    )

    if not JOURNAL_FILE.exists():

        append_journal(
            state,
            "R35I_CORRECTED_JOURNAL_INITIALIZED",
            {
                "version": VERSION,
                "symbol": SYMBOL,
                "exchange_network_writes": 0,
                "real_order_execution": False,
            },
        )

    elif not migrated:

        append_journal(
            state,
            "R35I_VALIDATION_RUN_STARTED",
            {
                "version": VERSION,
                "symbol": SYMBOL,
                "exchange_network_writes": 0,
                "real_order_execution": False,
            },
        )

    section(
        f"{VERSION} TEST 1: HARD SAFETY CONSTANTS"
    )

    check(
        "Live Activation Gate Is Present",
        LIVE_ACTIVATION_GATE_PRESENT,
    )

    check(
        "Exchange Writer Is Hard Disabled",
        not EXCHANGE_WRITER_ENABLED,
    )

    check(
        "Exchange Network Writes Are Disabled",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "Exchange POST Is Disabled",
        not EXCHANGE_POST_ENABLED,
    )

    check(
        "Exchange PUT Is Disabled",
        not EXCHANGE_PUT_ENABLED,
    )

    check(
        "Exchange PATCH Is Disabled",
        not EXCHANGE_PATCH_ENABLED,
    )

    check(
        "Exchange DELETE Is Disabled",
        not EXCHANGE_DELETE_ENABLED,
    )

    check(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION,
    )

    check(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    check(
        "First Real Order Is Not Allowed",
        not FIRST_REAL_ORDER_ALLOWED,
    )

    check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    check(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    check(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    check(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    check(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION_ENABLED,
    )

    section(
        f"{VERSION} TEST 2: STARTUP STATE"
    )

    check(
        "State Version Is Correct",
        state.version == VERSION,
    )

    check(
        "State Symbol Is Correct",
        state.symbol == SYMBOL,
    )

    check(
        "Initial Exchange Write Count Is Zero",
        state.exchange_network_writes == 0,
    )

    check(
        "Initial Kill Switch Is Clear",
        not state.kill_switch,
    )

    check(
        "Initial Ambiguous Outcome Block Is Clear",
        not state.ambiguous_outcome_block,
    )

    section(
        f"{VERSION} TEST 3: LIVE MODE ARMING DOES NOT ENABLE WRITER"
    )

    writes_before = (
        state.exchange_network_writes
    )

    arm_live_mode(
        state
    )

    check(
        "Live Mode Was Armed",
        state.live_mode_armed,
    )

    check(
        "Exchange Writer Remains Disabled",
        not EXCHANGE_WRITER_ENABLED,
    )

    check(
        "Real Order Execution Remains Disabled",
        not REAL_ORDER_EXECUTION,
    )

    check(
        "Arming Live Mode Makes No Exchange Write",
        (
            state.exchange_network_writes
            == writes_before
        ),
    )

    section(
        f"{VERSION} TEST 4: REAL MARKET AND ACCOUNT READINESS"
    )

    check(
        "WEEX API Key Is Present",
        bool(WEEX_API_KEY),
    )

    check(
        "WEEX Secret Key Is Present",
        bool(WEEX_SECRET_KEY),
    )

    check(
        "WEEX Passphrase Is Present",
        bool(WEEX_PASSPHRASE),
    )

    #
    # NO FALLBACKS.
    #
    # Any failure here aborts R35I.
    #

    balance_payload = (
        authenticated_get_json(
            BALANCE_PATH
        )
    )

    positions_payload = (
        authenticated_get_json(
            POSITIONS_PATH
        )
    )

    symbol_config_payload = (
        authenticated_get_json(
            SYMBOL_CONFIG_PATH,
            {
                "symbol": SYMBOL,
            },
        )
    )

    mark_price = (
        obtain_mark_price()
    )

    balance = (
        extract_available_usdt(
            balance_payload
        )
    )

    open_positions = (
        extract_open_positions(
            positions_payload
        )
    )

    symbol_config = (
        extract_symbol_config(
            symbol_config_payload
        )
    )

    check(
        "Authenticated Balance Read Succeeded",
        balance >= 0,
    )

    check(
        "Authenticated Position Read Succeeded",
        isinstance(
            open_positions,
            list,
        ),
    )

    check(
        "Authenticated Symbol Config Read Succeeded",
        bool(
            symbol_config
        ),
    )

    check(
        "Strategy Balance Is Positive",
        balance > 0,
    )

    check(
        "Market Price Is Positive",
        mark_price > 0,
    )

    check(
        "Open Position Count Is Non-Negative",
        len(open_positions) >= 0,
    )

    log(
        f"{VERSION}: BALANCE={balance}"
    )

    log(
        f"{VERSION}: MARK PRICE={mark_price}"
    )

    log(
        f"{VERSION}: OPEN POSITIONS="
        f"{len(open_positions)}"
    )

    log(
        f"{VERSION}: MARGIN TYPE="
        f"{symbol_config.get('marginType')}"
    )

    log(
        f"{VERSION}: ISOLATED LONG LEVERAGE="
        f"{symbol_config.get('isolatedLongLeverage')}"
    )

    log(
        f"{VERSION}: ISOLATED SHORT LEVERAGE="
        f"{symbol_config.get('isolatedShortLeverage')}"
    )

    section(
        f"{VERSION} TEST 5: FRESH EXCHANGE RECONCILIATION"
    )

    reconciliation = make_reconciliation(
        state=state,
        balance=balance,
        mark_price=mark_price,
        positions=open_positions,
        symbol_config=symbol_config,
    )

    state.reconciliation = (
        reconciliation
    )

    state.phase = "RECONCILED"

    save_state(
        state
    )

    append_journal(
        state,
        "EXCHANGE_RECONCILED",
        {
            "reconciliation_id": (
                reconciliation[
                    "reconciliation_id"
                ]
            ),
            "reconciliation_hash": (
                reconciliation[
                    "reconciliation_hash"
                ]
            ),
            "balance": balance,
            "mark_price": mark_price,
            "open_position_count": len(
                open_positions
            ),
        },
    )

    check(
        "Reconciliation Was Created",
        bool(
            reconciliation
        ),
    )

    check(
        f"Reconciliation Is Bound To {SYMBOL}",
        (
            reconciliation[
                "symbol"
            ]
            == SYMBOL
        ),
    )

    check(
        "Reconciliation Is Fresh",
        reconciliation_is_fresh(
            reconciliation
        ),
    )

    check(
        "Reconciliation Is Bound To Generation One",
        (
            reconciliation[
                "generation"
            ]
            == state.generation
        ),
    )

    check(
        "Reconciliation Is Bound To Epoch One",
        (
            reconciliation[
                "epoch"
            ]
            == state.epoch
        ),
    )

    section(
        f"{VERSION} TEST 6: HARD EXPOSURE LIMIT"
    )

    entry_margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / 100.0
    )

    entry_notional = (
        entry_margin
        * PLANNED_LEVERAGE
    )

    normalized_quantity = (
        normalize_quantity(
            entry_notional
            / mark_price
        )
    )

    maximum_strategy_margin = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / 100.0
    )

    planned_strategy_margin = (
        balance
        * (
            INITIAL_ENTRY_PERCENT
            + (
                MAX_PYRAMID_ADDS
                * PYRAMID_PERCENT
            )
            + (
                MAX_BACKUPS
                * BACKUP_PERCENT
            )
        )
        / 100.0
    )

    check(
        "Initial Entry Margin Is Positive",
        entry_margin > 0,
    )

    check(
        "Normalized Quantity Meets Minimum",
        normalized_quantity >= 0.0001,
    )

    check(
        "Planned Strategy Margin Is Within 35 Percent Cap",
        (
            planned_strategy_margin
            <= maximum_strategy_margin
        ),
    )

    check(
        "Maximum Strategy Margin Is Positive",
        maximum_strategy_margin > 0,
    )

    log(
        f"{VERSION}: ENTRY MARGIN="
        f"{entry_margin}"
    )

    log(
        f"{VERSION}: ENTRY NOTIONAL="
        f"{entry_notional}"
    )

    log(
        f"{VERSION}: NORMALIZED QTY="
        f"{normalized_quantity:.4f}"
    )

    log(
        f"{VERSION}: MAX STRATEGY MARGIN="
        f"{maximum_strategy_margin}"
    )

    log(
        f"{VERSION}: PLANNED STRATEGY MARGIN="
        f"{planned_strategy_margin}"
    )

    section(
        f"{VERSION} TEST 7: LIVE MODE RE-ARM AFTER RECONCILIATION"
    )

    arm_live_mode(
        state
    )

    check(
        "Live Mode Is Armed",
        state.live_mode_armed,
    )

    check(
        "Strategy Still Cannot Transmit",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "Real Orders Remain Disabled",
        not REAL_ORDER_EXECUTION,
    )

    section(
        f"{VERSION} TEST 8: EXACT ORDER INTENT"
    )

    intent = make_order_intent(
        state=state,
        balance=balance,
        mark_price=mark_price,
        reconciliation=reconciliation,
    )

    check(
        "Intent Was Created",
        bool(
            intent
        ),
    )

    check(
        f"Intent Is Bound To {SYMBOL}",
        intent[
            "symbol"
        ] == SYMBOL,
    )

    check(
        "Intent Uses BUY",
        intent[
            "side"
        ] == "BUY",
    )

    check(
        "Intent Uses LONG Position Side",
        intent[
            "positionSide"
        ] == "LONG",
    )

    check(
        "Intent Uses MARKET Type",
        intent[
            "type"
        ] == "MARKET",
    )

    check(
        "Intent Explicitly Forbids Transmission",
        not intent[
            "transmission_permitted"
        ],
    )

    check(
        "Intent Is Bound To Fresh Reconciliation",
        (
            intent[
                "reconciliation_hash"
            ]
            == reconciliation[
                "reconciliation_hash"
            ]
        ),
    )

    section(
        f"{VERSION} TEST 9: ONE-TIME AUTHORIZATION"
    )

    authorization = (
        make_authorization(
            state,
            intent,
        )
    )

    check(
        "Authorization Was Created",
        bool(
            authorization
        ),
    )

    check(
        "Authorization Is Bound To Intent",
        (
            authorization[
                "intent_hash"
            ]
            == intent[
                "intent_hash"
            ]
        ),
    )

    check(
        "Authorization Is One-Time",
        authorization[
            "one_time"
        ],
    )

    check(
        "Authorization Does Not Permit Transmission",
        not authorization[
            "transmission_permitted"
        ],
    )

    check(
        "Authorization Does Not Enable Writer",
        not authorization[
            "exchange_writer_permitted"
        ],
    )

    section(
        f"{VERSION} TEST 10: IDEMPOTENT CLIENT ORDER ID"
    )

    client_order_id = (
        make_client_order_id(
            intent
        )
    )

    client_order_id_again = (
        make_client_order_id(
            intent
        )
    )

    check(
        "Client Order ID Is Deterministic",
        (
            client_order_id
            == client_order_id_again
        ),
    )

    check(
        "Client Order ID Uses R35I Prefix",
        client_order_id.startswith(
            "r35i-"
        ),
    )

    check(
        "Client Order ID Has Not Yet Been Consumed",
        (
            client_order_id
            not in state.used_client_order_ids
        ),
    )

    log(
        f"{VERSION}: CLIENT ORDER ID="
        f"{client_order_id}"
    )

    section(
        f"{VERSION} TEST 11: SECRET-SAFE WRITER ENVELOPE"
    )

    envelope = (
        build_writer_envelope(
            state=state,
            reconciliation=reconciliation,
            intent=intent,
            authorization=authorization,
            client_order_id=client_order_id,
        )
    )

    check(
        "Writer Envelope Uses POST",
        envelope[
            "method"
        ] == "POST",
    )

    check(
        "Writer Envelope Uses Exact V3 Order Path",
        envelope[
            "request_path"
        ] == ORDER_PATH,
    )

    check(
        "Writer Envelope Is Bound To Intent",
        (
            envelope[
                "intent_hash"
            ]
            == intent[
                "intent_hash"
            ]
        ),
    )

    check(
        "Writer Envelope Is Bound To Authorization",
        (
            envelope[
                "authorization_hash"
            ]
            == authorization[
                "authorization_hash"
            ]
        ),
    )

    check(
        "Writer Envelope Is Bound To Reconciliation",
        (
            envelope[
                "reconciliation_hash"
            ]
            == reconciliation[
                "reconciliation_hash"
            ]
        ),
    )

    check(
        "Writer Envelope Marks Transmitted False",
        (
            envelope[
                "transmitted"
            ]
            is False
        ),
    )

    check(
        "Writer Preview Redacts Access Key",
        (
            envelope[
                "headers"
            ][
                "ACCESS-KEY"
            ]
            == "<redacted>"
        ),
    )

    check(
        "Writer Preview Redacts Signature",
        (
            envelope[
                "headers"
            ][
                "ACCESS-SIGN"
            ]
            == "<redacted>"
        ),
    )

    check(
        "Writer Preview Redacts Passphrase",
        (
            envelope[
                "headers"
            ][
                "ACCESS-PASSPHRASE"
            ]
            == "<redacted>"
        ),
    )

    log(
        f"{VERSION}: WRITER PREVIEW="
        f"{canonical_json(envelope)}"
    )

    section(
        f"{VERSION} TEST 12: EXCHANGE NETWORK FIREBREAK"
    )

    check(
        "Exchange Writer Is Still Disabled",
        not EXCHANGE_WRITER_ENABLED,
    )

    check(
        "Exchange Network Writes Are Still Disabled",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "Real Order Execution Is Still Disabled",
        not REAL_ORDER_EXECUTION,
    )

    check(
        "First Real Order Is Still Forbidden",
        not FIRST_REAL_ORDER_ALLOWED,
    )

    check(
        "Envelope Was Not Transmitted",
        not envelope[
            "transmitted"
        ],
    )

    section(
        f"{VERSION} TEST 13: SYNTHETIC DISPATCH"
    )

    exchange_writes_before = (
        state.exchange_network_writes
    )

    receipt = synthetic_dispatch(
        state=state,
        intent=intent,
        authorization=authorization,
        client_order_id=client_order_id,
        envelope=envelope,
    )

    check(
        "Synthetic Dispatch Produced Receipt",
        bool(
            receipt
        ),
    )

    check(
        "Synthetic Receipt Marks Transmitted False",
        not receipt[
            "transmitted"
        ],
    )

    check(
        "Synthetic Receipt Marks Exchange Write False",
        not receipt[
            "exchange_network_write"
        ],
    )

    check(
        "Synthetic Receipt Marks Real Order False",
        not receipt[
            "real_order"
        ],
    )

    check(
        "Synthetic Dispatch Makes No Exchange Network Write",
        (
            state.exchange_network_writes
            == exchange_writes_before
        ),
    )

    section(
        f"{VERSION} TEST 14: INTENT REPLAY PROTECTION"
    )

    replay_rejected = False

    try:

        synthetic_dispatch(
            state=state,
            intent=intent,
            authorization=authorization,
            client_order_id=client_order_id,
            envelope=envelope,
        )

    except RuntimeError:

        replay_rejected = True

    check(
        "Consumed Intent Replay Is Rejected",
        replay_rejected,
    )

    section(
        f"{VERSION} TEST 15: AUTHORIZATION REPLAY PROTECTION"
    )

    check(
        "Authorization Is Persistently Consumed",
        (
            authorization[
                "authorization_id"
            ]
            in state.consumed_authorizations
        ),
    )

    section(
        f"{VERSION} TEST 16: CLIENT ORDER ID REPLAY PROTECTION"
    )

    check(
        "Client Order ID Is Persistently Used",
        (
            client_order_id
            in state.used_client_order_ids
        ),
    )

    section(
        f"{VERSION} TEST 17: DURABLE RECEIPT"
    )

    check(
        "Durable Receipt Exists",
        any(
            item.get(
                "receipt_id"
            )
            == receipt[
                "receipt_id"
            ]
            for item
            in state.durable_receipts
        ),
    )

    section(
        f"{VERSION} TEST 18: KILL SWITCH BOUNDARY"
    )

    original_live_mode = (
        state.live_mode_armed
    )

    state.kill_switch = True

    save_state(
        state
    )

    kill_switch_rejected = False

    try:

        arm_live_mode(
            state
        )

    except RuntimeError:

        kill_switch_rejected = True

    check(
        "Kill Switch Rejects Live Gate Arming",
        kill_switch_rejected,
    )

    check(
        "Kill Switch Makes No Exchange Write",
        state.exchange_network_writes == 0,
    )

    state.kill_switch = False
    state.live_mode_armed = (
        original_live_mode
    )

    save_state(
        state
    )

    section(
        f"{VERSION} TEST 19: AMBIGUOUS OUTCOME BLOCK"
    )

    state.ambiguous_outcome_block = (
        True
    )

    save_state(
        state
    )

    ambiguous_rejected = False

    try:

        arm_live_mode(
            state
        )

    except RuntimeError:

        ambiguous_rejected = True

    check(
        "Ambiguous Outcome Blocks Live Gate",
        ambiguous_rejected,
    )

    state.ambiguous_outcome_block = (
        False
    )

    save_state(
        state
    )

    section(
        f"{VERSION} TEST 20: DURABLE RESTART PROTECTION"
    )

    save_state(
        state
    )

    restarted = load_state()

    check(
        "Live Activation Gate State Survives Restart",
        (
            restarted.live_mode_armed
            == state.live_mode_armed
        ),
    )

    check(
        "Consumed Intent Survives Restart",
        (
            intent[
                "intent_id"
            ]
            in restarted.consumed_intents
        ),
    )

    check(
        "Consumed Authorization Survives Restart",
        (
            authorization[
                "authorization_id"
            ]
            in restarted.consumed_authorizations
        ),
    )

    check(
        "Used Client Order ID Survives Restart",
        (
            client_order_id
            in restarted.used_client_order_ids
        ),
    )

    check(
        "Durable Receipt Survives Restart",
        any(
            item.get(
                "receipt_id"
            )
            == receipt[
                "receipt_id"
            ]
            for item
            in restarted.durable_receipts
        ),
    )

    check(
        "Restart Keeps Exchange Write Count At Zero",
        restarted.exchange_network_writes == 0,
    )

    section(
        f"{VERSION} TEST 21: TELEGRAM REPORTING BOUNDARY"
    )

    preview = telegram_preview()

    check(
        "Telegram Uses POST Only For Reporting",
        preview[
            "method"
        ] == "POST",
    )

    check(
        "Telegram Operation Is sendMessage",
        preview[
            "operation"
        ] == "sendMessage",
    )

    check(
        "Telegram Request Is Report Only",
        preview[
            "report_only"
        ],
    )

    check(
        "Telegram Request Is Not Exchange Mutation",
        not preview[
            "exchange_mutation"
        ],
    )

    check(
        "Telegram Cannot Control Execution",
        not preview[
            "can_control_execution"
        ],
    )

    check(
        "Telegram Preview Does Not Expose Bot Token",
        preview[
            "bot_token"
        ] in {
            "<redacted>",
            "<missing>",
        },
    )

    section(
        f"{VERSION} TEST 22: LIVE TELEGRAM DELIVERY"
    )

    check(
        "Telegram Reporting Is Enabled",
        TELEGRAM_REPORTING_ENABLED,
    )

    check(
        "Telegram Bot Token Is Present",
        bool(
            TELEGRAM_BOT_TOKEN
        ),
    )

    check(
        "Telegram Chat ID Is Present",
        bool(
            TELEGRAM_CHAT_ID
        ),
    )

    telegram_phase_before = (
        state.phase
    )

    telegram_nonce_before = (
        state.highest_nonce
    )

    telegram_exchange_writes_before = (
        state.exchange_network_writes
    )

    telegram_real_execution_before = (
        state.real_order_execution
    )

    telegram_message = (
        f"✅ {VERSION} VALIDATION REPORT\n"
        f"Symbol: {SYMBOL}\n"
        f"Authenticated WEEX reads: PASS\n"
        f"Balance: {balance:.8f} USDT\n"
        f"Mark price: {mark_price}\n"
        f"Open positions: {len(open_positions)}\n"
        f"Journal test: pending final verification\n"
        f"Exchange network writes: 0\n"
        f"Real order execution: DISABLED\n"
        f"Status: validation only"
    )

    delivered, telegram_result = (
        telegram_send_message(
            telegram_message
        )
    )

    log(
        f"{VERSION}: TELEGRAM DELIVERED="
        f"{delivered}"
    )

    log(
        f"{VERSION}: TELEGRAM RESULT="
        f"{telegram_result}"
    )

    check(
        "Telegram Delivery Succeeded",
        delivered,
    )

    state.telegram_delivery_count += 1
    state.telegram_last_delivery_ok = (
        delivered
    )

    save_state(
        state
    )

    append_journal(
        state,
        "TELEGRAM_REPORT_DELIVERED",
        {
            "delivered": delivered,
            "operation": "sendMessage",
            "report_only": True,
            "exchange_mutation": False,
        },
    )

    check(
        "Telegram Leaves Strategy Phase Unchanged",
        state.phase == telegram_phase_before,
    )

    check(
        "Telegram Leaves Strategy Nonce Unchanged",
        (
            state.highest_nonce
            == telegram_nonce_before
        ),
    )

    check(
        "Telegram Leaves Exchange Write Count Unchanged",
        (
            state.exchange_network_writes
            == telegram_exchange_writes_before
        ),
    )

    check(
        "Real Order Execution Remains Disabled After Telegram",
        (
            state.real_order_execution
            == telegram_real_execution_before
            == False
        ),
    )

    section(
        f"{VERSION} TEST 23: JOURNAL INTEGRITY"
    )

    journal_records = (
        read_journal()
    )

    check(
        "Durable Journal Contains Records",
        len(
            journal_records
        ) > 0,
    )

    (
        journal_valid,
        journal_reason,
        journal_sequence,
        journal_last_hash,
    ) = validate_journal_records(
        journal_records
    )

    if not journal_valid:

        log(
            f"{VERSION}: JOURNAL VALIDATION DETAIL="
            f"{journal_reason}"
        )

    check(
        "Journal Hash Chain Is Valid",
        journal_valid,
    )

    check(
        "Journal Sequence Matches Durable State",
        (
            journal_sequence
            == state.journal_sequence
        ),
    )

    check(
        "Journal Terminal Hash Matches Durable State",
        (
            journal_last_hash
            == state.last_journal_hash
        ),
    )

    section(
        f"{VERSION} TEST 24: JOURNAL TAMPER DETECTION"
    )

    original_records = (
        read_journal()
    )

    tampered_records = json.loads(
        json.dumps(
            original_records
        )
    )

    check(
        "Tamper Test Has Journal Record",
        len(
            tampered_records
        ) > 0,
    )

    tampered_records[
        -1
    ][
        "details"
    ][
        "_tamper_probe"
    ] = True

    (
        tampered_valid,
        _,
        _,
        _,
    ) = validate_journal_records(
        tampered_records
    )

    check(
        "Journal Tampering Is Rejected",
        not tampered_valid,
    )

    section(
        f"{VERSION} TEST 25: FINAL HARD WRITE FIREBREAK"
    )

    check(
        "Final Exchange Writer Is Disabled",
        not EXCHANGE_WRITER_ENABLED,
    )

    check(
        "Final Exchange Network Writes Are Disabled",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "Final Exchange POST Is Disabled",
        not EXCHANGE_POST_ENABLED,
    )

    check(
        "Final Exchange PUT Is Disabled",
        not EXCHANGE_PUT_ENABLED,
    )

    check(
        "Final Exchange PATCH Is Disabled",
        not EXCHANGE_PATCH_ENABLED,
    )

    check(
        "Final Exchange DELETE Is Disabled",
        not EXCHANGE_DELETE_ENABLED,
    )

    check(
        "Final Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION,
    )

    check(
        "Final Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION,
    )

    check(
        "Final First Real Order Is Forbidden",
        not FIRST_REAL_ORDER_ALLOWED,
    )

    check(
        "Final Exchange Write Count Is Zero",
        state.exchange_network_writes == 0,
    )

    #
    # Final successful journal entry.
    #

    state.phase = "VALIDATED"

    save_state(
        state
    )

    append_journal(
        state,
        "R35I_VALIDATION_COMPLETED",
        {
            "symbol": SYMBOL,
            "phase": "VALIDATED",
            "exchange_network_writes": 0,
            "real_order_execution": False,
            "telegram_delivered": delivered,
            "journal_valid": True,
        },
    )

    #
    # Verify AGAIN after final append.
    #

    (
        final_journal_valid,
        final_journal_reason,
        final_sequence,
        final_hash,
    ) = validate_journal_file()

    section(
        f"{VERSION} TEST 26: FINAL DURABLE CONSISTENCY"
    )

    check(
        "Final Journal Hash Chain Is Valid",
        final_journal_valid,
    )

    check(
        "Final Journal Sequence Matches State",
        (
            final_sequence
            == state.journal_sequence
        ),
    )

    check(
        "Final Journal Hash Matches State",
        (
            final_hash
            == state.last_journal_hash
        ),
    )

    final_restart = (
        load_state()
    )

    check(
        "Final State Survives Restart",
        (
            final_restart.phase
            == "VALIDATED"
        ),
    )

    check(
        "Final Restart Keeps Exchange Writes Zero",
        (
            final_restart.exchange_network_writes
            == 0
        ),
    )

    check(
        "Final Restart Keeps Real Orders Disabled",
        (
            final_restart.real_order_execution
            is False
        ),
    )

    HEALTH_STATE.update(
        {
            "status": "validated",
            "phase": state.phase,
            "exchange_network_writes": 0,
            "real_order_execution": False,
            "telegram_delivered": delivered,
            "journal_valid": True,
        }
    )

    section(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    log(
        f"{VERSION} REPORT"
    )

    log(
        f"SYMBOL={SYMBOL}"
    )

    log(
        f"EVENT={VERSION}_VALIDATION"
    )

    log(
        f"PHASE={state.phase}"
    )

    log(
        f"GENERATION={state.generation}"
    )

    log(
        f"EPOCH={state.epoch}"
    )

    log(
        "EXCHANGE_NETWORK_WRITES=0"
    )

    log(
        "REAL_ORDER_EXECUTION=False"
    )

    log(
        f"TELEGRAM_DELIVERED={delivered}"
    )

    log(
        "JOURNAL_HASH_CHAIN_VALID=True"
    )

    log(
        "AUTHENTICATED_ACCOUNT_READS=PASS"
    )

    log(
        "STATUS=R35I_VALIDATED_NO_EXCHANGE_MUTATION"
    )

    log(DIVIDER)


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        f"{VERSION}: HEALTH PORT="
        f"{HEALTH_PORT}"
    )

    log(
        f"{VERSION}: STATE DIR="
        f"{STATE_DIR}"
    )

    log(
        f"{VERSION}: WEEX BASE URL="
        f"{WEEX_BASE_URL}"
    )

    log(
        f"{VERSION}: AUTHENTICATED READS ENABLED="
        f"{AUTHENTICATED_READS_ENABLED}"
    )

    log(
        f"{VERSION}: PUBLIC READS ENABLED="
        f"{PUBLIC_READS_ENABLED}"
    )

    log(
        f"{VERSION}: LIVE ACTIVATION GATE PRESENT="
        f"{LIVE_ACTIVATION_GATE_PRESENT}"
    )

    log(
        f"{VERSION}: EXCHANGE WRITER ENABLED="
        f"{EXCHANGE_WRITER_ENABLED}"
    )

    log(
        f"{VERSION}: EXCHANGE NETWORK WRITES ENABLED="
        f"{EXCHANGE_NETWORK_WRITES_ENABLED}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: FIRST REAL ORDER ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"{VERSION}: TELEGRAM REPORTING ENABLED="
        f"{TELEGRAM_REPORTING_ENABLED}"
    )

    log(
        f"{VERSION}: TELEGRAM CREDENTIALS PRESENT="
        f"{TELEGRAM_CREDENTIALS_PRESENT}"
    )

    log(DIVIDER)

    try:

        run_validation()

    except Exception as exc:

        HEALTH_STATE.update(
            {
                "status": "validation_failed",
                "exchange_network_writes": 0,
                "real_order_execution": False,
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            }
        )

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        log(
            f"{VERSION}: EXCHANGE WRITES "
            f"REMAIN HARD DISABLED"
        )

        log(
            f"{VERSION}: REAL ORDER EXECUTION "
            f"REMAINS DISABLED"
        )

        log(DIVIDER)

        raise


if __name__ == "__main__":

    main()
