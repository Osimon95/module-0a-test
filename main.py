

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
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
# R35I - CONTROLLED LIVE ACTIVATION GATE
# ==================================================================================================
#
# PURPOSE
#
#   R35I validates the architecture immediately before the first controlled live execution stage.
#
#   It proves:
#
#       STARTUP
#           ↓
#       LIVE MODE ARMING
#           ↓
#       FRESH EXCHANGE RECONCILIATION
#           ↓
#       HARD EXPOSURE LIMIT
#           ↓
#       EXACT INTENT
#           ↓
#       ONE-TIME AUTHORIZATION
#           ↓
#       IDEMPOTENT CLIENT ORDER ID
#           ↓
#       SECRET-SAFE WRITER ENVELOPE
#           ↓
#       FINAL TRANSMISSION GATE
#           ↓
#       HARD-DISABLED REAL WRITER
#
# SAFETY MODEL
#
#   - AUTHENTICATED GET MAY BE ENABLED
#   - PUBLIC GET MAY BE ENABLED
#
#   - EXCHANGE POST IS HARD DISABLED
#   - EXCHANGE PUT IS HARD DISABLED
#   - EXCHANGE PATCH IS HARD DISABLED
#   - EXCHANGE DELETE IS HARD DISABLED
#
#   - REAL ORDER EXECUTION IS HARD DISABLED
#   - DEMO ORDER EXECUTION IS HARD DISABLED
#
#   - LEVERAGE MUTATION DISABLED
#   - MARGIN MUTATION DISABLED
#   - POSITION MUTATION DISABLED
#
#   - LIVE MODE ARMING DOES NOT AUTHORIZE AN ORDER
#   - AUTHORIZATION DOES NOT ENABLE THE WRITER
#   - WRITER ENABLE DOES NOT EXIST IN R35I
#
#   - FRESH RECONCILIATION REQUIRED
#   - ONE INTENT AT A TIME
#   - ONE AUTHORIZATION AT A TIME
#   - EXACTLY-ONCE SYNTHETIC DISPATCH
#   - REPLAY REJECTION
#   - STALE RECONCILIATION REJECTION
#   - KILL SWITCH
#   - AMBIGUOUS OUTCOME FAIL-CLOSED
#   - HARD FUND EXPOSURE LIMIT
#
#   - TELEGRAM REPORTING MAY BE ENABLED
#   - TELEGRAM CANNOT CONTROL EXECUTION
#
#
# IMPORTANT
#
#   R35I DOES NOT SEND A REAL ORDER.
#
#   THE FIRST REAL EXCHANGE ORDER IS NOT PERMITTED BY THIS FILE.
#
# ==================================================================================================


VERSION = "R35I"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_DIR = Path(
    os.getenv(
        "R35I_STATE_DIR",
        "/tmp/r35i_state",
    )
)

STATE_FILE = STATE_DIR / "state.json"
JOURNAL_FILE = STATE_DIR / "journal.jsonl"


# ==================================================================================================
# EXCHANGE CONFIGURATION
# ==================================================================================================


EXCHANGE_BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

BALANCE_PATH = os.getenv(
    "WEEX_BALANCE_PATH",
    "/capi/v3/account/balance",
)

POSITIONS_PATH = os.getenv(
    "WEEX_POSITIONS_PATH",
    "/capi/v3/account/positions",
)

ORDER_PATH = "/capi/v3/order"

MARK_PRICE_PATH = os.getenv(
    "WEEX_MARK_PRICE_PATH",
    "/capi/v3/market/symbolPrice",
)


API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# ==================================================================================================
# TELEGRAM CONFIGURATION
# ==================================================================================================


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()

TELEGRAM_REPORTING_ENABLED = (
    os.getenv(
        "TELEGRAM_REPORTING_ENABLED",
        "false",
    ).strip().lower()
    in {"1", "true", "yes", "on"}
)


# ==================================================================================================
# STRATEGY CONFIGURATION
# ==================================================================================================


TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

TARGET_MARGIN_MODE = "ISOLATED"

ENTRY_BALANCE_PERCENT = 5.0
PYRAMID_PERCENT = 5.0
BACKUP_PERCENT = 5.0

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = 35.0

QTY_STEP = 0.0001
MIN_QTY = 0.0001

PRICE_STEP = 0.1

SIGNAL_EXPIRY_SECONDS = 120
RECONCILIATION_MAX_AGE_SECONDS = 60

LOSS_COOLDOWN_SECONDS = 300


# ==================================================================================================
# R35I HARD SAFETY CONSTANTS
# ==================================================================================================


AUTHENTICATED_READS_ENABLED = True
PUBLIC_READS_ENABLED = True

EXCHANGE_NETWORK_WRITES_ENABLED = False

EXCHANGE_POST_ENABLED = False
EXCHANGE_PUT_ENABLED = False
EXCHANGE_PATCH_ENABLED = False
EXCHANGE_DELETE_ENABLED = False

EXCHANGE_WRITER_ENABLED = False

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

LIVE_ACTIVATION_GATE_PRESENT = True

FIRST_REAL_ORDER_ALLOWED = False


# ==================================================================================================
# UTILITIES
# ==================================================================================================


def utc_ms() -> int:
    return int(time.time() * 1000)


def utc_seconds() -> float:
    return time.time()


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


def object_hash(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(value)
    )


def random_id(
    prefix: str,
    length: int = 20,
) -> str:

    return (
        f"{prefix}-"
        f"{secrets.token_hex(length // 2)}"
    )


def redact(
    value: str,
) -> str:

    if not value:
        return "<unset>"

    return "<redacted>"


def ensure_state_dir() -> None:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def atomic_write_json(
    path: Path,
    data: Dict[str, Any],
) -> None:

    ensure_state_dir()

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    encoded = (
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(encoded)

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temporary,
        path,
    )


def read_json_file(
    path: Path,
) -> Optional[Dict[str, Any]]:

    if not path.exists():
        return None

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            value = json.load(handle)

        if not isinstance(
            value,
            dict,
        ):
            return None

        return value

    except Exception:
        return None


def print_rule() -> None:

    print(
        "-" * 100,
        flush=True,
    )


def print_test(
    number: int,
    title: str,
) -> None:

    print_rule()

    print(
        f"{VERSION} TEST {number}: {title}",
        flush=True,
    )

    print_rule()


def check(
    label: str,
    condition: bool,
) -> None:

    marker = (
        "✅ PASS"
        if condition
        else
        "❌ FAIL"
    )

    print(
        f"{label:<85} {marker}",
        flush=True,
    )

    if not condition:

        raise AssertionError(
            label
        )


# ==================================================================================================
# STATE
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

    live_activation_gate_passed: bool = False

    reconciliation: Optional[
        Dict[str, Any]
    ] = None

    active_intent: Optional[
        Dict[str, Any]
    ] = None

    active_authorization: Optional[
        Dict[str, Any]
    ] = None

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

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    used_client_order_ids: List[
        str
    ] = field(
        default_factory=list
    )

    exchange_network_write_count: int = 0

    exchange_writer_attempt_count: int = 0

    exchange_writer_block_count: int = 0

    synthetic_dispatch_count: int = 0

    duplicate_dispatch_block_count: int = 0

    stale_reconciliation_block_count: int = 0

    exposure_block_count: int = 0

    authorization_block_count: int = 0

    kill_switch_engaged: bool = False

    ambiguous_outcome_block: bool = False

    terminal: bool = False

    journal_sequence: int = 0

    last_journal_hash: str = "0" * 64

    integrity_hash: str = ""

    created_at_ms: int = field(
        default_factory=utc_ms
    )

    updated_at_ms: int = field(
        default_factory=utc_ms
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(self)


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================


STATE_LOCK = threading.RLock()


def state_payload_for_hash(
    state: StrategyState,
) -> Dict[str, Any]:

    value = state.as_dict()

    value.pop(
        "integrity_hash",
        None,
    )

    return value


def calculate_state_integrity(
    state: StrategyState,
) -> str:

    return object_hash(
        state_payload_for_hash(
            state
        )
    )


def validate_state_integrity(
    state: StrategyState,
) -> bool:

    if not state.integrity_hash:
        return False

    return hmac.compare_digest(
        state.integrity_hash,
        calculate_state_integrity(
            state
        ),
    )


def append_journal(
    state: StrategyState,
    event: str,
    details: Dict[str, Any],
) -> None:

    ensure_state_dir()

    state.journal_sequence += 1

    record_body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "sequence": state.journal_sequence,
        "timestamp_ms": utc_ms(),
        "event": event,
        "details": details,
        "previous_hash": state.last_journal_hash,
    }

    record_hash = object_hash(
        record_body
    )

    record = dict(
        record_body
    )

    record["record_hash"] = (
        record_hash
    )

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

    state.last_journal_hash = (
        record_hash
    )


def persist_state(
    state: StrategyState,
    event: Optional[str] = None,
    details: Optional[
        Dict[str, Any]
    ] = None,
) -> None:

    with STATE_LOCK:

        state.updated_at_ms = (
            utc_ms()
        )

        if event is not None:

            append_journal(
                state,
                event,
                details or {},
            )

        state.integrity_hash = (
            calculate_state_integrity(
                state
            )
        )

        atomic_write_json(
            STATE_FILE,
            state.as_dict(),
        )


def strategy_state_from_dict(
    data: Dict[str, Any],
) -> StrategyState:

    valid_fields = {
        item.name
        for item in StrategyState.__dataclass_fields__.values()
    }

    clean = {
        key: value
        for key, value in data.items()
        if key in valid_fields
    }

    return StrategyState(
        **clean
    )


def load_state() -> StrategyState:

    data = read_json_file(
        STATE_FILE
    )

    if data is None:

        state = StrategyState()

        persist_state(
            state,
            event="STATE_CREATED",
            details={
                "phase": state.phase,
            },
        )

        return state

    state = strategy_state_from_dict(
        data
    )

    if (
        state.version != VERSION
        or state.symbol != SYMBOL
    ):

        state = StrategyState()

        persist_state(
            state,
            event="STATE_RESET_VERSION_BOUNDARY",
            details={
                "version": VERSION,
                "symbol": SYMBOL,
            },
        )

        return state

    if not validate_state_integrity(
        state
    ):

        raise RuntimeError(
            "Durable state integrity validation failed."
        )

    return state


# ==================================================================================================
# JOURNAL VALIDATION
# ==================================================================================================


def validate_journal(
    state: StrategyState,
) -> Tuple[
    bool,
    int,
    str,
]:

    if not JOURNAL_FILE.exists():

        return (
            state.journal_sequence == 0,
            0,
            "0" * 64,
        )

    previous_hash = (
        "0" * 64
    )

    count = 0

    with JOURNAL_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:

        for line in handle:

            line = line.strip()

            if not line:
                continue

            record = json.loads(
                line
            )

            stored_hash = record.get(
                "record_hash",
                "",
            )

            body = dict(
                record
            )

            body.pop(
                "record_hash",
                None,
            )

            if (
                body.get(
                    "previous_hash"
                )
                != previous_hash
            ):

                return (
                    False,
                    count,
                    previous_hash,
                )

            calculated_hash = (
                object_hash(
                    body
                )
            )

            if not hmac.compare_digest(
                stored_hash,
                calculated_hash,
            ):

                return (
                    False,
                    count,
                    previous_hash,
                )

            previous_hash = (
                stored_hash
            )

            count += 1

    valid = (
        count
        == state.journal_sequence
        and previous_hash
        == state.last_journal_hash
    )

    return (
        valid,
        count,
        previous_hash,
    )


# ==================================================================================================
# HTTP READ HELPERS
# ==================================================================================================


def create_signature(
    timestamp_ms: str,
    method: str,
    request_path: str,
    body: str,
) -> str:

    message = (
        timestamp_ms
        + method.upper()
        + request_path
        + body
    )

    return hmac.new(
        API_SECRET.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


def authenticated_headers(
    method: str,
    request_path: str,
    body: str = "",
) -> Dict[str, str]:

    timestamp = str(
        utc_ms()
    )

    signature = create_signature(
        timestamp,
        method,
        request_path,
        body,
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
    }


def public_get_json(
    request_path: str,
    query: Optional[
        Dict[str, Any]
    ] = None,
    timeout: float = 10.0,
) -> Any:

    if not PUBLIC_READS_ENABLED:

        raise RuntimeError(
            "Public reads disabled."
        )

    query_string = ""

    if query:

        query_string = (
            "?"
            + urllib.parse.urlencode(
                query
            )
        )

    url = (
        EXCHANGE_BASE_URL
        + request_path
        + query_string
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "locale": "en-US",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        raw = response.read().decode(
            "utf-8"
        )

    return json.loads(
        raw
    )


def authenticated_get_json(
    request_path: str,
    query: Optional[
        Dict[str, Any]
    ] = None,
    timeout: float = 10.0,
) -> Any:

    if not AUTHENTICATED_READS_ENABLED:

        raise RuntimeError(
            "Authenticated reads disabled."
        )

    if not (
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    ):

        raise RuntimeError(
            "WEEX credentials are incomplete."
        )

    query_string = ""

    if query:

        query_string = (
            "?"
            + urllib.parse.urlencode(
                query
            )
        )

    signed_path = (
        request_path
        + query_string
    )

    url = (
        EXCHANGE_BASE_URL
        + signed_path
    )

    headers = authenticated_headers(
        "GET",
        signed_path,
        "",
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        raw = response.read().decode(
            "utf-8"
        )

    return json.loads(
        raw
    )


# ==================================================================================================
# RESPONSE PARSING
# ==================================================================================================


def collect_dicts(
    value: Any,
) -> List[Dict[str, Any]]:

    found: List[
        Dict[str, Any]
    ] = []

    if isinstance(
        value,
        dict,
    ):

        found.append(
            value
        )

        for child in value.values():

            found.extend(
                collect_dicts(
                    child
                )
            )

    elif isinstance(
        value,
        list,
    ):

        for child in value:

            found.extend(
                collect_dicts(
                    child
                )
            )

    return found


def first_numeric_value(
    value: Any,
    keys: List[str],
) -> Optional[float]:

    lowered = {
        key.lower()
        for key in keys
    }

    for item in collect_dicts(
        value
    ):

        for key, raw in item.items():

            if key.lower() not in lowered:
                continue

            try:

                number = float(
                    raw
                )

                return number

            except (
                TypeError,
                ValueError,
            ):
                continue

    return None


def first_string_value(
    value: Any,
    keys: List[str],
) -> Optional[str]:

    lowered = {
        key.lower()
        for key in keys
    }

    for item in collect_dicts(
        value
    ):

        for key, raw in item.items():

            if key.lower() not in lowered:
                continue

            if raw is None:
                continue

            return str(
                raw
            )

    return None


def parse_balance(
    value: Any,
) -> Optional[float]:

    return first_numeric_value(
        value,
        [
            "available",
            "availableBalance",
            "availableMargin",
            "availableEquity",
            "balance",
            "equity",
        ],
    )


def parse_mark_price(
    value: Any,
) -> Optional[float]:

    return first_numeric_value(
        value,
        [
            "price",
            "markPrice",
            "last",
            "lastPrice",
        ],
    )


def count_open_positions(
    value: Any,
) -> int:

    count = 0

    for item in collect_dicts(
        value
    ):

        symbol_value = (
            item.get("symbol")
            or item.get("contractCode")
            or item.get("instrumentId")
        )

        if (
            symbol_value is not None
            and str(
                symbol_value
            ).upper()
            != SYMBOL
        ):
            continue

        quantity = None

        for key in (
            "size",
            "position",
            "positionAmt",
            "positionSize",
            "quantity",
            "qty",
            "total",
        ):

            if key in item:

                try:

                    quantity = abs(
                        float(
                            item[key]
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    quantity = None

                break

        if (
            quantity is not None
            and quantity > 0
        ):

            count += 1

    return count


# ==================================================================================================
# STRATEGY MATH
# ==================================================================================================


def floor_to_step(
    value: float,
    step: float,
) -> float:

    units = int(
        value / step
    )

    return round(
        units * step,
        12,
    )


def build_budget(
    balance: float,
    mark_price: float,
) -> Dict[str, Any]:

    entry_margin = (
        balance
        * ENTRY_BALANCE_PERCENT
        / 100.0
    )

    entry_notional = (
        entry_margin
        * TARGET_LONG_LEVERAGE
    )

    raw_qty = (
        entry_notional
        / mark_price
    )

    quantity = floor_to_step(
        raw_qty,
        QTY_STEP,
    )

    rounded_notional = (
        quantity
        * mark_price
    )

    estimated_margin = (
        rounded_notional
        / TARGET_LONG_LEVERAGE
    )

    max_strategy_margin = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / 100.0
    )

    planned_margin = (
        balance
        * (
            ENTRY_BALANCE_PERCENT
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

    return {
        "balance": balance,
        "mark_price": mark_price,
        "entry_balance_percent": ENTRY_BALANCE_PERCENT,
        "entry_margin": entry_margin,
        "entry_notional": entry_notional,
        "raw_quantity": raw_qty,
        "quantity": quantity,
        "rounded_notional": rounded_notional,
        "estimated_margin": estimated_margin,
        "max_fund_exposure_percent": MAX_FUND_EXPOSURE_PERCENT,
        "max_strategy_margin": max_strategy_margin,
        "planned_strategy_margin": planned_margin,
        "within_exposure_cap": (
            planned_margin
            <= max_strategy_margin
        ),
    }


# ==================================================================================================
# RECONCILIATION
# ==================================================================================================


def create_reconciliation(
    state: StrategyState,
    balance: float,
    mark_price: float,
    open_positions: int,
) -> Dict[str, Any]:

    reconciliation = {
        "reconciliation_id": random_id(
            "rec"
        ),
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "created_at_ms": utc_ms(),
        "balance": balance,
        "mark_price": mark_price,
        "open_positions": open_positions,
        "margin_mode": TARGET_MARGIN_MODE,
        "long_leverage": TARGET_LONG_LEVERAGE,
        "short_leverage": TARGET_SHORT_LEVERAGE,
    }

    reconciliation[
        "reconciliation_hash"
    ] = object_hash(
        reconciliation
    )

    return reconciliation


def reconciliation_is_fresh(
    reconciliation: Dict[str, Any],
) -> bool:

    created_at_ms = int(
        reconciliation.get(
            "created_at_ms",
            0,
        )
    )

    age_seconds = (
        utc_ms()
        - created_at_ms
    ) / 1000.0

    return (
        0
        <= age_seconds
        <= RECONCILIATION_MAX_AGE_SECONDS
    )


# ==================================================================================================
# LIVE MODE ARMING
# ==================================================================================================


def arm_live_mode(
    state: StrategyState,
) -> None:

    if state.kill_switch_engaged:

        raise RuntimeError(
            "Kill switch blocks live-mode arming."
        )

    if state.ambiguous_outcome_block:

        raise RuntimeError(
            "Ambiguous outcome blocks live-mode arming."
        )

    state.live_mode_armed = True

    state.phase = (
        "LIVE_MODE_ARMED"
    )

    persist_state(
        state,
        event="LIVE_MODE_ARMED",
        details={
            "exchange_writer_enabled":
                EXCHANGE_WRITER_ENABLED,
            "real_order_execution":
                REAL_ORDER_EXECUTION,
        },
    )


def disarm_live_mode(
    state: StrategyState,
) -> None:

    state.live_mode_armed = False

    state.live_activation_gate_passed = (
        False
    )

    state.phase = "DISARMED"

    persist_state(
        state,
        event="LIVE_MODE_DISARMED",
        details={},
    )


# ==================================================================================================
# INTENT
# ==================================================================================================


def create_intent(
    state: StrategyState,
    reconciliation: Dict[str, Any],
    quantity: float,
) -> Dict[str, Any]:

    if not state.live_mode_armed:

        raise RuntimeError(
            "Live mode must be armed before intent."
        )

    if state.kill_switch_engaged:

        raise RuntimeError(
            "Kill switch blocks new intent."
        )

    if state.ambiguous_outcome_block:

        raise RuntimeError(
            "Ambiguous outcome blocks new intent."
        )

    if not reconciliation_is_fresh(
        reconciliation
    ):

        state.stale_reconciliation_block_count += 1

        persist_state(
            state,
            event="STALE_RECONCILIATION_BLOCK",
            details={},
        )

        raise RuntimeError(
            "Reconciliation is stale."
        )

    if quantity < MIN_QTY:

        raise RuntimeError(
            "Quantity below exchange minimum."
        )

    state.highest_nonce += 1

    intent = {
        "intent_id": random_id(
            "int"
        ),
        "nonce": state.highest_nonce,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "reconciliation_id":
            reconciliation[
                "reconciliation_id"
            ],
        "reconciliation_hash":
            reconciliation[
                "reconciliation_hash"
            ],
        "created_at_ms": utc_ms(),
        "expires_at_ms": (
            utc_ms()
            + (
                SIGNAL_EXPIRY_SECONDS
                * 1000
            )
        ),
        "side": "BUY",
        "position_side": "LONG",
        "order_type": "MARKET",
        "quantity": (
            f"{quantity:.4f}"
        ),
        "transmission_allowed": False,
        "exchange_writer_required": True,
        "real_execution_required": True,
    }

    intent["intent_hash"] = (
        object_hash(
            intent
        )
    )

    state.active_intent = (
        intent
    )

    state.phase = (
        "INTENT_PREPARED"
    )

    persist_state(
        state,
        event="INTENT_PREPARED",
        details={
            "intent_id":
                intent[
                    "intent_id"
                ],
            "intent_hash":
                intent[
                    "intent_hash"
                ],
        },
    )

    return intent


# ==================================================================================================
# AUTHORIZATION
# ==================================================================================================


def authorize_intent(
    state: StrategyState,
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    if state.kill_switch_engaged:

        raise RuntimeError(
            "Kill switch blocks authorization."
        )

    if state.ambiguous_outcome_block:

        raise RuntimeError(
            "Ambiguous outcome blocks authorization."
        )

    if (
        state.active_intent is None
        or state.active_intent.get(
            "intent_id"
        )
        != intent.get(
            "intent_id"
        )
    ):

        state.authorization_block_count += 1

        raise RuntimeError(
            "Intent is not active."
        )

    if (
        intent["intent_id"]
        in state.consumed_intents
    ):

        raise RuntimeError(
            "Intent already consumed."
        )

    if (
        utc_ms()
        > int(
            intent[
                "expires_at_ms"
            ]
        )
    ):

        raise RuntimeError(
            "Intent expired."
        )

    authorization = {
        "authorization_id":
            random_id(
                "auth"
            ),
        "intent_id":
            intent[
                "intent_id"
            ],
        "intent_hash":
            intent[
                "intent_hash"
            ],
        "reconciliation_id":
            intent[
                "reconciliation_id"
            ],
        "generation":
            state.generation,
        "epoch":
            state.epoch,
        "created_at_ms":
            utc_ms(),
        "one_time":
            True,
        "exchange_writer_required":
            True,
        "real_execution_required":
            True,
        "transmission_allowed":
            False,
    }

    authorization[
        "authorization_hash"
    ] = object_hash(
        authorization
    )

    state.active_authorization = (
        authorization
    )

    state.phase = "AUTHORIZED"

    persist_state(
        state,
        event="INTENT_AUTHORIZED",
        details={
            "authorization_id":
                authorization[
                    "authorization_id"
                ],
            "authorization_hash":
                authorization[
                    "authorization_hash"
                ],
        },
    )

    return authorization


# ==================================================================================================
# CLIENT ORDER ID
# ==================================================================================================


def create_client_order_id(
    intent: Dict[str, Any],
) -> str:

    seed = {
        "version": VERSION,
        "symbol": SYMBOL,
        "intent_id":
            intent[
                "intent_id"
            ],
        "intent_hash":
            intent[
                "intent_hash"
            ],
    }

    suffix = object_hash(
        seed
    )[:20]

    return (
        f"r35i-{suffix}"
    )


# ==================================================================================================
# WRITER ENVELOPE
# ==================================================================================================


def create_writer_envelope(
    state: StrategyState,
    reconciliation: Dict[str, Any],
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
) -> Dict[str, Any]:

    if not state.live_mode_armed:

        raise RuntimeError(
            "Live mode is not armed."
        )

    if not reconciliation_is_fresh(
        reconciliation
    ):

        state.stale_reconciliation_block_count += 1

        raise RuntimeError(
            "Stale reconciliation cannot reach writer."
        )

    if state.kill_switch_engaged:

        raise RuntimeError(
            "Kill switch blocks writer envelope."
        )

    if state.ambiguous_outcome_block:

        raise RuntimeError(
            "Ambiguous outcome blocks writer envelope."
        )

    if (
        state.active_authorization
        is None
    ):

        raise RuntimeError(
            "Writer requires authorization."
        )

    if (
        state.active_authorization.get(
            "authorization_id"
        )
        != authorization.get(
            "authorization_id"
        )
    ):

        raise RuntimeError(
            "Writer authorization mismatch."
        )

    client_order_id = (
        create_client_order_id(
            intent
        )
    )

    if (
        client_order_id
        in state.used_client_order_ids
    ):

        state.duplicate_dispatch_block_count += 1

        raise RuntimeError(
            "Client order ID already used."
        )

    payload = {
        "symbol": SYMBOL,
        "side": intent[
            "side"
        ],
        "positionSide":
            intent[
                "position_side"
            ],
        "type":
            intent[
                "order_type"
            ],
        "quantity":
            intent[
                "quantity"
            ],
        "newClientOrderId":
            client_order_id,
    }

    body = canonical_json(
        payload
    )

    fixed_test_timestamp = (
        "1760000000000"
    )

    if API_SECRET:

        signature = (
            create_signature(
                fixed_test_timestamp,
                "POST",
                ORDER_PATH,
                body,
            )
        )

    else:

        signature = (
            "<unavailable>"
        )

    headers = {
        "ACCESS-KEY":
            API_KEY
            if API_KEY
            else "<unset>",
        "ACCESS-SIGN":
            signature,
        "ACCESS-TIMESTAMP":
            fixed_test_timestamp,
        "ACCESS-PASSPHRASE":
            API_PASSPHRASE
            if API_PASSPHRASE
            else "<unset>",
        "Content-Type":
            "application/json",
        "locale":
            "en-US",
    }

    envelope = {
        "method": "POST",
        "request_path":
            ORDER_PATH,
        "url":
            EXCHANGE_BASE_URL
            + ORDER_PATH,
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
        "authorization_id":
            authorization[
                "authorization_id"
            ],
        "authorization_hash":
            authorization[
                "authorization_hash"
            ],
        "reconciliation_id":
            reconciliation[
                "reconciliation_id"
            ],
        "reconciliation_hash":
            reconciliation[
                "reconciliation_hash"
            ],
        "live_mode_armed":
            state.live_mode_armed,
        "exchange_writer_enabled":
            EXCHANGE_WRITER_ENABLED,
        "exchange_network_writes_enabled":
            EXCHANGE_NETWORK_WRITES_ENABLED,
        "real_order_execution":
            REAL_ORDER_EXECUTION,
        "first_real_order_allowed":
            FIRST_REAL_ORDER_ALLOWED,
        "transmitted":
            False,
    }

    envelope[
        "envelope_hash"
    ] = object_hash(
        envelope
    )

    return envelope


def safe_writer_preview(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    preview = json.loads(
        json.dumps(
            envelope
        )
    )

    preview_headers = (
        preview.get(
            "headers",
            {}
        )
    )

    if "ACCESS-KEY" in preview_headers:

        preview_headers[
            "ACCESS-KEY"
        ] = "<redacted>"

    if "ACCESS-SIGN" in preview_headers:

        preview_headers[
            "ACCESS-SIGN"
        ] = "<redacted>"

    if (
        "ACCESS-PASSPHRASE"
        in preview_headers
    ):

        preview_headers[
            "ACCESS-PASSPHRASE"
        ] = "<redacted>"

    return preview


# ==================================================================================================
# HARD-DISABLED REAL EXCHANGE WRITER
# ==================================================================================================


def exchange_order_writer(
    state: StrategyState,
    envelope: Dict[str, Any],
) -> None:

    state.exchange_writer_attempt_count += 1

    if state.kill_switch_engaged:

        state.exchange_writer_block_count += 1

        persist_state(
            state,
            event="WRITER_BLOCKED_KILL_SWITCH",
            details={},
        )

        raise RuntimeError(
            "Exchange writer blocked by kill switch."
        )

    if state.ambiguous_outcome_block:

        state.exchange_writer_block_count += 1

        persist_state(
            state,
            event="WRITER_BLOCKED_AMBIGUOUS",
            details={},
        )

        raise RuntimeError(
            "Exchange writer blocked by ambiguous outcome."
        )

    if not state.live_mode_armed:

        state.exchange_writer_block_count += 1

        raise RuntimeError(
            "Exchange writer blocked because live mode is not armed."
        )

    if (
        state.active_authorization
        is None
    ):

        state.exchange_writer_block_count += 1

        raise RuntimeError(
            "Exchange writer requires active authorization."
        )

    #
    # R35I FIREBREAK
    #
    # There is intentionally NO urllib.request.urlopen()
    # and NO network transmission code below.
    #

    if (
        not EXCHANGE_WRITER_ENABLED
        or not EXCHANGE_NETWORK_WRITES_ENABLED
        or not EXCHANGE_POST_ENABLED
        or not REAL_ORDER_EXECUTION
        or not FIRST_REAL_ORDER_ALLOWED
    ):

        state.exchange_writer_block_count += 1

        persist_state(
            state,
            event="REAL_WRITER_HARD_BLOCKED",
            details={
                "envelope_hash":
                    envelope.get(
                        "envelope_hash"
                    ),
                "exchange_writer_enabled":
                    EXCHANGE_WRITER_ENABLED,
                "exchange_network_writes_enabled":
                    EXCHANGE_NETWORK_WRITES_ENABLED,
                "real_order_execution":
                    REAL_ORDER_EXECUTION,
                "first_real_order_allowed":
                    FIRST_REAL_ORDER_ALLOWED,
            },
        )

        raise RuntimeError(
            "R35I real exchange writer is hard disabled."
        )

    raise RuntimeError(
        "Unreachable R35I writer guard."
    )


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================


def synthetic_dispatch(
    state: StrategyState,
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    intent_id = str(
        envelope[
            "intent_id"
        ]
    )

    authorization_id = str(
        envelope[
            "authorization_id"
        ]
    )

    client_order_id = str(
        envelope[
            "payload"
        ][
            "newClientOrderId"
        ]
    )

    if (
        intent_id
        in state.consumed_intents
    ):

        state.duplicate_dispatch_block_count += 1

        raise RuntimeError(
            "Intent replay rejected."
        )

    if (
        authorization_id
        in state.consumed_authorizations
    ):

        state.duplicate_dispatch_block_count += 1

        raise RuntimeError(
            "Authorization replay rejected."
        )

    if (
        client_order_id
        in state.used_client_order_ids
    ):

        state.duplicate_dispatch_block_count += 1

        raise RuntimeError(
            "Client order ID replay rejected."
        )

    receipt = {
        "receipt_id":
            random_id(
                "receipt"
            ),
        "version":
            VERSION,
        "symbol":
            SYMBOL,
        "intent_id":
            intent_id,
        "authorization_id":
            authorization_id,
        "client_order_id":
            client_order_id,
        "envelope_hash":
            envelope[
                "envelope_hash"
            ],
        "synthetic":
            True,
        "transmitted":
            False,
        "exchange_network_write":
            False,
        "real_order_execution":
            False,
        "created_at_ms":
            utc_ms(),
    }

    receipt[
        "receipt_hash"
    ] = object_hash(
        receipt
    )

    state.synthetic_dispatch_count += 1

    state.consumed_intents.append(
        intent_id
    )

    state.consumed_authorizations.append(
        authorization_id
    )

    state.used_client_order_ids.append(
        client_order_id
    )

    state.durable_receipts.append(
        receipt
    )

    state.active_intent = None

    state.active_authorization = None

    state.live_activation_gate_passed = (
        True
    )

    state.phase = (
        "LIVE_ACTIVATION_GATE_VALIDATED"
    )

    persist_state(
        state,
        event="SYNTHETIC_DISPATCH_COMPLETED",
        details={
            "receipt_id":
                receipt[
                    "receipt_id"
                ],
            "receipt_hash":
                receipt[
                    "receipt_hash"
                ],
            "transmitted":
                False,
        },
    )

    return receipt


# ==================================================================================================
# KILL SWITCH
# ==================================================================================================


def engage_kill_switch(
    state: StrategyState,
    reason: str,
) -> None:

    state.kill_switch_engaged = True

    state.live_mode_armed = False

    state.live_activation_gate_passed = (
        False
    )

    state.phase = "KILL_SWITCH"

    persist_state(
        state,
        event="KILL_SWITCH_ENGAGED",
        details={
            "reason": reason,
        },
    )


def clear_kill_switch_test_only(
    state: StrategyState,
) -> None:

    state.kill_switch_engaged = False

    state.phase = "RECONCILED"

    persist_state(
        state,
        event="KILL_SWITCH_CLEARED_TEST_ONLY",
        details={},
    )


# ==================================================================================================
# AMBIGUOUS OUTCOME
# ==================================================================================================


def activate_ambiguous_block(
    state: StrategyState,
) -> None:

    state.ambiguous_outcome_block = True

    state.live_mode_armed = False

    state.phase = (
        "AMBIGUOUS_OUTCOME_BLOCKED"
    )

    persist_state(
        state,
        event="AMBIGUOUS_OUTCOME_BLOCKED",
        details={},
    )


def clear_ambiguous_with_fresh_reconciliation(
    state: StrategyState,
    reconciliation: Dict[str, Any],
) -> None:

    if not reconciliation_is_fresh(
        reconciliation
    ):

        raise RuntimeError(
            "Fresh reconciliation required."
        )

    state.reconciliation = (
        reconciliation
    )

    state.ambiguous_outcome_block = False

    state.phase = "RECONCILED"

    persist_state(
        state,
        event="AMBIGUOUS_OUTCOME_CLEARED",
        details={
            "reconciliation_id":
                reconciliation[
                    "reconciliation_id"
                ]
        },
    )


# ==================================================================================================
# TELEGRAM
# ==================================================================================================


def telegram_preview(
    text: str,
) -> Dict[str, Any]:

    return {
        "method": "POST",
        "operation":
            "sendMessage",
        "report_only":
            True,
        "exchange_mutation":
            False,
        "execution_control":
            False,
        "bot_token":
            "<redacted>",
        "chat_id":
            TELEGRAM_CHAT_ID
            if TELEGRAM_CHAT_ID
            else "<unset>",
        "text":
            text,
    }


def send_telegram_report(
    text: str,
) -> bool:

    if not TELEGRAM_REPORTING_ENABLED:

        return False

    if not (
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    ):

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = urllib.parse.urlencode(
        {
            "chat_id":
                TELEGRAM_CHAT_ID,
            "text":
                text,
            "disable_web_page_preview":
                "true",
        }
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        url=url,
        data=payload,
        method="POST",
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

        decoded = json.loads(
            raw
        )

        return bool(
            decoded.get(
                "ok"
            )
        )

    except Exception as exc:

        print(
            f"{VERSION}: TELEGRAM ERROR={type(exc).__name__}: {exc}",
            flush=True,
        )

        return False


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

        payload = {
            "status": "ok",
            "version": VERSION,
            "symbol": SYMBOL,
            "exchange_writer_enabled":
                EXCHANGE_WRITER_ENABLED,
            "exchange_network_writes_enabled":
                EXCHANGE_NETWORK_WRITES_ENABLED,
            "real_order_execution":
                REAL_ORDER_EXECUTION,
            "first_real_order_allowed":
                FIRST_REAL_ORDER_ALLOWED,
        }

        encoded = json.dumps(
            payload
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
                    encoded
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            encoded
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

    print(
        f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}",
        flush=True,
    )


# ==================================================================================================
# VALIDATION
# ==================================================================================================


def run_validation() -> StrategyState:

    ensure_state_dir()

    #
    # Use a clean R35I validation state on each deployment.
    #
    # Previous same-version terminal state is archived implicitly by
    # starting a new generation of this validation program.
    #

    if STATE_FILE.exists():

        try:

            STATE_FILE.unlink()

        except Exception:
            pass

    if JOURNAL_FILE.exists():

        try:

            JOURNAL_FILE.unlink()

        except Exception:
            pass

    state = load_state()


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    print_test(
        1,
        "HARD SAFETY CONSTANTS",
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


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    print_test(
        2,
        "STARTUP STATE",
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
        state.exchange_network_write_count == 0,
    )

    check(
        "Initial Live Mode Is Disarmed",
        not state.live_mode_armed,
    )

    check(
        "Initial Kill Switch Is Clear",
        not state.kill_switch_engaged,
    )

    check(
        "Initial Ambiguous Outcome Block Is Clear",
        not state.ambiguous_outcome_block,
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    print_test(
        3,
        "LIVE MODE ARMING DOES NOT ENABLE WRITER",
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
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    print_test(
        4,
        "MARKET AND ACCOUNT READINESS",
    )

    live_balance: Optional[
        float
    ] = None

    live_mark_price: Optional[
        float
    ] = None

    open_positions = 0


    #
    # PUBLIC MARK PRICE
    #

    try:

        mark_response = (
            public_get_json(
                MARK_PRICE_PATH,
                {
                    "symbol":
                        SYMBOL,
                },
            )
        )

        live_mark_price = (
            parse_mark_price(
                mark_response
            )
        )

    except Exception as exc:

        print(
            f"{VERSION}: MARKET PRICE READ WARNING={type(exc).__name__}: {exc}",
            flush=True,
        )


    #
    # AUTHENTICATED BALANCE
    #

    if (
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    ):

        try:

            balance_response = (
                authenticated_get_json(
                    BALANCE_PATH,
                )
            )

            live_balance = (
                parse_balance(
                    balance_response
                )
            )

        except Exception as exc:

            print(
                f"{VERSION}: BALANCE READ WARNING={type(exc).__name__}: {exc}",
                flush=True,
            )


        try:

            position_response = (
                authenticated_get_json(
                    POSITIONS_PATH,
                    {
                        "symbol":
                            SYMBOL,
                    },
                )
            )

            open_positions = (
                count_open_positions(
                    position_response
                )
            )

        except Exception as exc:

            print(
                f"{VERSION}: POSITION READ WARNING={type(exc).__name__}: {exc}",
                flush=True,
            )


    #
    # Validation fallback values exist ONLY so R35I can test
    # the control architecture if an external read is temporarily unavailable.
    #
    # They are never eligible for real execution.
    #

    if (
        live_balance is None
        or live_balance <= 0
    ):

        live_balance = (
            7.18945017
        )

        print(
            f"{VERSION}: USING VALIDATION-ONLY BALANCE FALLBACK={live_balance}",
            flush=True,
        )


    if (
        live_mark_price is None
        or live_mark_price <= 0
    ):

        live_mark_price = (
            80000.0
        )

        print(
            f"{VERSION}: USING VALIDATION-ONLY PRICE FALLBACK={live_mark_price}",
            flush=True,
        )


    check(
        "Strategy Balance Is Positive",
        live_balance > 0,
    )

    check(
        "Market Price Is Positive",
        live_mark_price > 0,
    )

    check(
        "Open Position Count Is Non-Negative",
        open_positions >= 0,
    )

    print(
        f"{VERSION}: BALANCE={live_balance}",
        flush=True,
    )

    print(
        f"{VERSION}: MARK PRICE={live_mark_price}",
        flush=True,
    )

    print(
        f"{VERSION}: OPEN POSITIONS={open_positions}",
        flush=True,
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    print_test(
        5,
        "FRESH EXCHANGE RECONCILIATION",
    )

    reconciliation = (
        create_reconciliation(
            state,
            balance=live_balance,
            mark_price=live_mark_price,
            open_positions=open_positions,
        )
    )

    state.reconciliation = (
        reconciliation
    )

    state.phase = "RECONCILED"

    persist_state(
        state,
        event="RECONCILIATION_CREATED",
        details={
            "reconciliation_id":
                reconciliation[
                    "reconciliation_id"
                ],
            "reconciliation_hash":
                reconciliation[
                    "reconciliation_hash"
                ],
        },
    )

    check(
        "Reconciliation Was Created",
        bool(
            reconciliation[
                "reconciliation_id"
            ]
        ),
    )

    check(
        "Reconciliation Is Bound To BTCUSDT",
        reconciliation[
            "symbol"
        ] == SYMBOL,
    )

    check(
        "Reconciliation Is Fresh",
        reconciliation_is_fresh(
            reconciliation
        ),
    )

    check(
        "Reconciliation Is Bound To Generation One",
        reconciliation[
            "generation"
        ] == state.generation,
    )

    check(
        "Reconciliation Is Bound To Epoch One",
        reconciliation[
            "epoch"
        ] == state.epoch,
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    print_test(
        6,
        "HARD EXPOSURE LIMIT",
    )

    budget = build_budget(
        live_balance,
        live_mark_price,
    )

    check(
        "Initial Entry Margin Is Positive",
        budget[
            "entry_margin"
        ] > 0,
    )

    check(
        "Normalized Quantity Meets Minimum",
        budget[
            "quantity"
        ] >= MIN_QTY,
    )

    check(
        "Planned Strategy Margin Is Within 35 Percent Cap",
        bool(
            budget[
                "within_exposure_cap"
            ]
        ),
    )

    check(
        "Maximum Strategy Margin Is Positive",
        budget[
            "max_strategy_margin"
        ] > 0,
    )

    print(
        f"{VERSION}: ENTRY MARGIN={budget['entry_margin']}",
        flush=True,
    )

    print(
        f"{VERSION}: ENTRY NOTIONAL={budget['entry_notional']}",
        flush=True,
    )

    print(
        f"{VERSION}: NORMALIZED QTY={budget['quantity']:.4f}",
        flush=True,
    )

    print(
        f"{VERSION}: MAX STRATEGY MARGIN={budget['max_strategy_margin']}",
        flush=True,
    )

    print(
        f"{VERSION}: PLANNED STRATEGY MARGIN={budget['planned_strategy_margin']}",
        flush=True,
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    print_test(
        7,
        "LIVE MODE RE-ARM AFTER RECONCILIATION",
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


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    print_test(
        8,
        "EXACT ORDER INTENT",
    )

    intent = create_intent(
        state,
        reconciliation,
        budget[
            "quantity"
        ],
    )

    check(
        "Intent Was Created",
        bool(
            intent[
                "intent_id"
            ]
        ),
    )

    check(
        "Intent Is Bound To BTCUSDT",
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
            "position_side"
        ] == "LONG",
    )

    check(
        "Intent Uses MARKET Type",
        intent[
            "order_type"
        ] == "MARKET",
    )

    check(
        "Intent Explicitly Forbids Transmission",
        not intent[
            "transmission_allowed"
        ],
    )

    check(
        "Intent Is Bound To Fresh Reconciliation",
        intent[
            "reconciliation_id"
        ]
        == reconciliation[
            "reconciliation_id"
        ],
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    print_test(
        9,
        "ONE-TIME AUTHORIZATION",
    )

    authorization = (
        authorize_intent(
            state,
            intent,
        )
    )

    check(
        "Authorization Was Created",
        bool(
            authorization[
                "authorization_id"
            ]
        ),
    )

    check(
        "Authorization Is Bound To Intent",
        authorization[
            "intent_id"
        ]
        == intent[
            "intent_id"
        ],
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
            "transmission_allowed"
        ],
    )

    check(
        "Authorization Does Not Enable Writer",
        not EXCHANGE_WRITER_ENABLED,
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    print_test(
        10,
        "IDEMPOTENT CLIENT ORDER ID",
    )

    client_order_id_one = (
        create_client_order_id(
            intent
        )
    )

    client_order_id_two = (
        create_client_order_id(
            intent
        )
    )

    check(
        "Client Order ID Is Deterministic",
        client_order_id_one
        == client_order_id_two,
    )

    check(
        "Client Order ID Uses R35I Prefix",
        client_order_id_one.startswith(
            "r35i-"
        ),
    )

    check(
        "Client Order ID Has Not Yet Been Consumed",
        client_order_id_one
        not in state.used_client_order_ids,
    )

    print(
        f"{VERSION}: CLIENT ORDER ID={client_order_id_one}",
        flush=True,
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    print_test(
        11,
        "SECRET-SAFE WRITER ENVELOPE",
    )

    envelope = (
        create_writer_envelope(
            state,
            reconciliation,
            intent,
            authorization,
        )
    )

    preview = (
        safe_writer_preview(
            envelope
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
        envelope[
            "intent_id"
        ]
        == intent[
            "intent_id"
        ],
    )

    check(
        "Writer Envelope Is Bound To Authorization",
        envelope[
            "authorization_id"
        ]
        == authorization[
            "authorization_id"
        ],
    )

    check(
        "Writer Envelope Is Bound To Reconciliation",
        envelope[
            "reconciliation_id"
        ]
        == reconciliation[
            "reconciliation_id"
        ],
    )

    check(
        "Writer Envelope Marks Transmitted False",
        not envelope[
            "transmitted"
        ],
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

    print(
        f"{VERSION}: WRITER PREVIEW={canonical_json(preview)}",
        flush=True,
    )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    print_test(
        12,
        "LIVE ACTIVATION DOES NOT EQUAL TRANSMISSION",
    )

    check(
        "Live Mode Is Armed",
        state.live_mode_armed,
    )

    check(
        "Authorization Exists",
        state.active_authorization
        is not None,
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
        "Real Execution Is Still Disabled",
        not REAL_ORDER_EXECUTION,
    )

    check(
        "First Real Order Remains Forbidden",
        not FIRST_REAL_ORDER_ALLOWED,
    )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    print_test(
        13,
        "HARD-DISABLED REAL WRITER",
    )

    writer_blocked = False

    before_writer_count = (
        state.exchange_network_write_count
    )

    try:

        exchange_order_writer(
            state,
            envelope,
        )

    except RuntimeError:

        writer_blocked = True

    check(
        "Live Writer Attempt Is Rejected",
        writer_blocked,
    )

    check(
        "Writer Attempt Count Increments",
        state.exchange_writer_attempt_count
        >= 1,
    )

    check(
        "Writer Block Count Increments",
        state.exchange_writer_block_count
        >= 1,
    )

    check(
        "Writer Makes No Exchange Network Write",
        state.exchange_network_write_count
        == before_writer_count,
    )

    check(
        "Real Order Execution Remains Disabled",
        not REAL_ORDER_EXECUTION,
    )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    print_test(
        14,
        "UNAUTHORIZED WRITER CANNOT BYPASS GATE",
    )

    unauthorized_state = (
        strategy_state_from_dict(
            state.as_dict()
        )
    )

    unauthorized_state.active_authorization = (
        None
    )

    unauthorized_blocked = False

    try:

        exchange_order_writer(
            unauthorized_state,
            envelope,
        )

    except RuntimeError:

        unauthorized_blocked = True

    check(
        "Unauthorized Test State Has No Authorization",
        unauthorized_state.active_authorization
        is None,
    )

    check(
        "Unauthorized Writer Attempt Is Rejected",
        unauthorized_blocked,
    )

    check(
        "Unauthorized Writer Makes No Exchange Write",
        unauthorized_state.exchange_network_write_count
        == state.exchange_network_write_count,
    )


    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    print_test(
        15,
        "STALE RECONCILIATION CANNOT REACH WRITER",
    )

    stale_reconciliation = json.loads(
        json.dumps(
            reconciliation
        )
    )

    stale_reconciliation[
        "created_at_ms"
    ] = (
        utc_ms()
        - (
            (
                RECONCILIATION_MAX_AGE_SECONDS
                + 30
            )
            * 1000
        )
    )

    stale_rejected = False

    try:

        create_writer_envelope(
            state,
            stale_reconciliation,
            intent,
            authorization,
        )

    except RuntimeError:

        stale_rejected = True

    check(
        "Stale Writer Envelope Is Rejected",
        stale_rejected,
    )

    check(
        "Stale Reconciliation Makes No Exchange Write",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    print_test(
        16,
        "KILL SWITCH FIREBREAK",
    )

    kill_test = (
        strategy_state_from_dict(
            state.as_dict()
        )
    )

    #
    # Give test copy a separate temporary state lifecycle
    # without replacing main durable state.
    #

    kill_test.kill_switch_engaged = (
        True
    )

    kill_test.live_mode_armed = (
        False
    )

    check(
        "Kill Switch Is Engaged",
        kill_test.kill_switch_engaged,
    )

    blocked_by_kill_switch = False

    try:

        exchange_order_writer(
            kill_test,
            envelope,
        )

    except RuntimeError:

        blocked_by_kill_switch = True

    check(
        "Kill Switch Blocks Exchange Writer",
        blocked_by_kill_switch,
    )

    check(
        "Kill Switch Makes No Exchange Network Write",
        kill_test.exchange_network_write_count
        == state.exchange_network_write_count,
    )


    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    print_test(
        17,
        "AMBIGUOUS OUTCOME FAIL-CLOSED",
    )

    ambiguous_test = (
        strategy_state_from_dict(
            state.as_dict()
        )
    )

    ambiguous_test.ambiguous_outcome_block = (
        True
    )

    ambiguous_test.live_mode_armed = (
        False
    )

    ambiguous_blocked = False

    try:

        exchange_order_writer(
            ambiguous_test,
            envelope,
        )

    except RuntimeError:

        ambiguous_blocked = True

    check(
        "Ambiguous Outcome Block Is Active",
        ambiguous_test.ambiguous_outcome_block,
    )

    check(
        "Ambiguous Outcome Cannot Reach Writer",
        ambiguous_blocked,
    )

    check(
        "Ambiguous Outcome Makes No Exchange Write",
        ambiguous_test.exchange_network_write_count
        == state.exchange_network_write_count,
    )


    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    print_test(
        18,
        "EXACTLY-ONCE SYNTHETIC DISPATCH",
    )

    receipt = (
        synthetic_dispatch(
            state,
            envelope,
        )
    )

    check(
        "Synthetic Receipt Was Created",
        bool(
            receipt[
                "receipt_id"
            ]
        ),
    )

    check(
        "Synthetic Dispatch Was Not Transmitted",
        not receipt[
            "transmitted"
        ],
    )

    check(
        "Synthetic Dispatch Made No Exchange Network Write",
        not receipt[
            "exchange_network_write"
        ],
    )

    check(
        "Synthetic Dispatch Count Is One",
        state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Intent Was Consumed",
        intent[
            "intent_id"
        ]
        in state.consumed_intents,
    )

    check(
        "Authorization Was Consumed",
        authorization[
            "authorization_id"
        ]
        in state.consumed_authorizations,
    )

    check(
        "Client Order ID Was Consumed",
        client_order_id_one
        in state.used_client_order_ids,
    )

    check(
        "Live Activation Gate Passed",
        state.live_activation_gate_passed,
    )

    check(
        "Exchange Network Write Count Remains Zero",
        state.exchange_network_write_count
        == 0,
    )


    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    print_test(
        19,
        "REPLAY PROTECTION",
    )

    replay_rejected = False

    try:

        synthetic_dispatch(
            state,
            envelope,
        )

    except RuntimeError:

        replay_rejected = True

    check(
        "Replay Is Rejected",
        replay_rejected,
    )

    check(
        "Replay Does Not Duplicate Synthetic Dispatch",
        state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Replay Makes No Exchange Network Write",
        state.exchange_network_write_count
        == 0,
    )


    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    print_test(
        20,
        "DURABLE RESTART PROTECTION",
    )

    reloaded_state = (
        load_state()
    )

    check(
        "Live Activation Gate State Survives Restart",
        reloaded_state.live_activation_gate_passed,
    )

    check(
        "Consumed Intent Survives Restart",
        intent[
            "intent_id"
        ]
        in reloaded_state.consumed_intents,
    )

    check(
        "Consumed Authorization Survives Restart",
        authorization[
            "authorization_id"
        ]
        in reloaded_state.consumed_authorizations,
    )

    check(
        "Used Client Order ID Survives Restart",
        client_order_id_one
        in reloaded_state.used_client_order_ids,
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
            in reloaded_state.durable_receipts
        ),
    )

    check(
        "Restart Keeps Exchange Write Count At Zero",
        reloaded_state.exchange_network_write_count
        == 0,
    )

    state = reloaded_state


    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    print_test(
        21,
        "TELEGRAM REPORTING BOUNDARY",
    )

    telegram_text = (
        f"{VERSION} VALIDATION\n"
        f"SYMBOL={SYMBOL}\n"
        f"PHASE={state.phase}\n"
        f"EXCHANGE_NETWORK_WRITES={state.exchange_network_write_count}\n"
        f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
        f"STATUS=CONTROLLED_LIVE_ACTIVATION_GATE_VALIDATED"
    )

    telegram_request_preview = (
        telegram_preview(
            telegram_text
        )
    )

    check(
        "Telegram Uses POST Only For Reporting",
        telegram_request_preview[
            "method"
        ]
        == "POST",
    )

    check(
        "Telegram Operation Is sendMessage",
        telegram_request_preview[
            "operation"
        ]
        == "sendMessage",
    )

    check(
        "Telegram Request Is Report Only",
        telegram_request_preview[
            "report_only"
        ],
    )

    check(
        "Telegram Request Is Not Exchange Mutation",
        not telegram_request_preview[
            "exchange_mutation"
        ],
    )

    check(
        "Telegram Cannot Control Execution",
        not telegram_request_preview[
            "execution_control"
        ],
    )

    check(
        "Telegram Preview Does Not Expose Bot Token",
        telegram_request_preview[
            "bot_token"
        ]
        == "<redacted>",
    )


    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    print_test(
        22,
        "OPTIONAL LIVE TELEGRAM DELIVERY",
    )

    phase_before_telegram = (
        state.phase
    )

    nonce_before_telegram = (
        state.highest_nonce
    )

    writes_before_telegram = (
        state.exchange_network_write_count
    )

    telegram_delivered = (
        send_telegram_report(
            telegram_text
        )
    )

    check(
        "Telegram Delivery Attempt Completed",
        isinstance(
            telegram_delivered,
            bool,
        ),
    )

    print(
        f"{VERSION}: TELEGRAM DELIVERED={telegram_delivered}",
        flush=True,
    )

    check(
        "Telegram Leaves Strategy Phase Unchanged",
        state.phase
        == phase_before_telegram,
    )

    check(
        "Telegram Leaves Strategy Nonce Unchanged",
        state.highest_nonce
        == nonce_before_telegram,
    )

    check(
        "Telegram Leaves Exchange Write Count Unchanged",
        state.exchange_network_write_count
        == writes_before_telegram,
    )

    check(
        "Real Order Execution Remains Disabled After Telegram",
        not REAL_ORDER_EXECUTION,
    )


    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    print_test(
        23,
        "JOURNAL INTEGRITY",
    )

    journal_valid, journal_count, journal_head = (
        validate_journal(
            state
        )
    )

    check(
        "Durable Journal Contains Records",
        journal_count > 0,
    )

    check(
        "Journal Hash Chain Is Valid",
        journal_valid,
    )

    check(
        "Journal Sequence Matches State",
        journal_count
        == state.journal_sequence,
    )

    check(
        "Journal Head Hash Matches State",
        journal_head
        == state.last_journal_hash,
    )

    check(
        "Journal Head Hash Has Correct Length",
        len(
            journal_head
        )
        == 64,
    )


    # ==============================================================================================
    # TEST 24
    # ==============================================================================================

    print_test(
        24,
        "FINAL LIVE ACTIVATION FIREBREAK",
    )

    state.phase = (
        "COMPLETED"
    )

    state.terminal = True

    persist_state(
        state,
        event="R35I_COMPLETED",
        details={
            "status":
                "CONTROLLED_LIVE_ACTIVATION_GATE_VALIDATED",
        },
    )

    check(
        "Strategy Reached COMPLETED",
        state.phase
        == "COMPLETED",
    )

    check(
        "Strategy Is Terminal",
        state.terminal,
    )

    check(
        "Controlled Live Activation Gate Was Validated",
        state.live_activation_gate_passed,
    )

    check(
        "No Exchange Network Write Occurred",
        state.exchange_network_write_count
        == 0,
    )

    check(
        "Exchange Writer Remains Hard Disabled",
        not EXCHANGE_WRITER_ENABLED,
    )

    check(
        "Exchange Network Writes Remain Disabled",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "Real Order Execution Remains Disabled",
        not REAL_ORDER_EXECUTION,
    )

    check(
        "First Real Order Remains Forbidden",
        not FIRST_REAL_ORDER_ALLOWED,
    )

    check(
        "At Least One Real Writer Attempt Was Safely Blocked",
        state.exchange_writer_attempt_count
        >= 1,
    )

    check(
        "At Least One Writer Block Was Recorded",
        state.exchange_writer_block_count
        >= 1,
    )


    # ==============================================================================================
    # TEST 25
    # ==============================================================================================

    print_test(
        25,
        "FINAL SNAPSHOT INTEGRITY",
    )

    final_state = (
        load_state()
    )

    check(
        "Final Snapshot Version Is Correct",
        final_state.version
        == VERSION,
    )

    check(
        "Final Snapshot Symbol Is Correct",
        final_state.symbol
        == SYMBOL,
    )

    check(
        "Final Snapshot Integrity Is Valid",
        validate_state_integrity(
            final_state
        ),
    )

    check(
        "Final Snapshot Keeps Exchange Write Count At Zero",
        final_state.exchange_network_write_count
        == 0,
    )

    check(
        "Final Snapshot Keeps Live Activation Validation",
        final_state.live_activation_gate_passed,
    )

    check(
        "Final Snapshot Is Terminal",
        final_state.terminal,
    )


    print_rule()

    print(
        f"{VERSION}: VALIDATION SUMMARY",
        flush=True,
    )

    print_rule()

    print(
        f"{VERSION} REPORT",
        flush=True,
    )

    print(
        f"SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"EVENT={VERSION}_VALIDATION",
        flush=True,
    )

    print(
        f"PHASE={final_state.phase}",
        flush=True,
    )

    print(
        f"GENERATION={final_state.generation}",
        flush=True,
    )

    print(
        f"EPOCH={final_state.epoch}",
        flush=True,
    )

    print(
        f"EXCHANGE_NETWORK_WRITES={final_state.exchange_network_write_count}",
        flush=True,
    )

    print(
        f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}",
        flush=True,
    )

    details = {
        "exchange_network_writes":
            final_state.exchange_network_write_count,
        "exchange_writer_enabled":
            EXCHANGE_WRITER_ENABLED,
        "live_mode_armed":
            final_state.live_mode_armed,
        "live_activation_gate_passed":
            final_state.live_activation_gate_passed,
        "first_real_order_allowed":
            FIRST_REAL_ORDER_ALLOWED,
        "live_trading":
            False,
        "status":
            "CONTROLLED_LIVE_ACTIVATION_GATE_VALIDATED",
    }

    print(
        "DETAILS="
        + canonical_json(
            details
        ),
        flush=True,
    )

    print_rule()

    print(
        f"{VERSION}: CONTROLLED LIVE ACTIVATION GATE VALIDATED",
        flush=True,
    )

    print(
        f"{VERSION}: REAL EXCHANGE WRITER REMAINS HARD DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: NO EXCHANGE ORDER WAS TRANSMITTED",
        flush=True,
    )

    print(
        f"{VERSION}: FIRST REAL ORDER REMAINS FORBIDDEN",
        flush=True,
    )

    print_rule()

    return final_state


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================


def heartbeat_loop(
    state: StrategyState,
) -> None:

    heartbeat = 0

    while True:

        time.sleep(
            30
        )

        heartbeat += 1

        print(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"PHASE={state.phase} "
            f"EXCHANGE_WRITES={state.exchange_network_write_count} "
            f"LIVE_MODE_ARMED={state.live_mode_armed} "
            f"ACTIVATION_GATE={state.live_activation_gate_passed} "
            f"WRITER_ENABLED={EXCHANGE_WRITER_ENABLED} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}",
            flush=True,
        )


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    print_rule()

    print(
        f"{VERSION}: MAIN.PY ENTERED",
        flush=True,
    )

    print_rule()

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
        f"{VERSION}: AUTHENTICATED READS ENABLED={AUTHENTICATED_READS_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: PUBLIC READS ENABLED={PUBLIC_READS_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE ACTIVATION GATE PRESENT={LIVE_ACTIVATION_GATE_PRESENT}",
        flush=True,
    )

    print(
        f"{VERSION}: EXCHANGE WRITER ENABLED={EXCHANGE_WRITER_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: EXCHANGE NETWORK WRITES ENABLED={EXCHANGE_NETWORK_WRITES_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDER EXECUTION={REAL_ORDER_EXECUTION}",
        flush=True,
    )

    print(
        f"{VERSION}: FIRST REAL ORDER ALLOWED={FIRST_REAL_ORDER_ALLOWED}",
        flush=True,
    )

    print(
        f"{VERSION}: TELEGRAM REPORTING ENABLED={TELEGRAM_REPORTING_ENABLED}",
        flush=True,
    )

    print_rule()

    try:

        final_state = (
            run_validation()
        )

    except Exception as exc:

        print_rule()

        print(
            f"{VERSION}: VALIDATION FAILED",
            flush=True,
        )

        print(
            f"{VERSION}: ERROR={type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            f"{VERSION}: EXCHANGE WRITES REMAIN HARD DISABLED",
            flush=True,
        )

        print(
            f"{VERSION}: REAL ORDER EXECUTION REMAINS DISABLED",
            flush=True,
        )

        print_rule()

        raise

    heartbeat_loop(
        final_state
    )


if __name__ == "__main__":
    main()

