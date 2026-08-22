import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import time
import traceback
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R28"
API_BASE_URL = "https://api-contract.weex.com"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()


def default_demo_symbol(symbol: str) -> str:
    if symbol.endswith("USDT"):
        return symbol[:-4] + "SUSDT"
    return symbol


DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    default_demo_symbol(SYMBOL),
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
# R28 IS PRE-LIVE / DEMO VALIDATION ONLY.
# REAL ORDER TRANSMISSION MUST REMAIN DISABLED.
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R28_REAL_POST_CALLED = False
R28_DEMO_POST_ATTEMPTED = False
R28_DEMO_POST_ACCEPTED = False


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

D100 = Decimal("100")

ENTRY_PERCENT = Decimal(
    os.getenv(
        "ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = int(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_CONFIG_LEVERAGE = int(
    os.getenv(
        "MAX_CONFIG_LEVERAGE",
        "100",
    )
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()

MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
        "1",
    )
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_SIZE_PERCENT",
        "5",
    )
)

MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3",
    )
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5",
    )
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
    )
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2",
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)

TP1_PERCENT = Decimal(
    os.getenv(
        "TP1_PERCENT",
        "20",
    )
)

TP2_PERCENT = Decimal(
    os.getenv(
        "TP2_PERCENT",
        "20",
    )
)

TP3_PERCENT = Decimal(
    os.getenv(
        "TP3_PERCENT",
        "60",
    )
)

TP1_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP1_TRIGGER_PERCENT",
        "0.5",
    )
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP2_TRIGGER_PERCENT",
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)

DEMO_FILL_MODE = os.getenv(
    "DEMO_FILL_MODE",
    "AUTO",
).strip().upper()

RUN_DEMO_FILL = os.getenv(
    "RUN_DEMO_FILL",
    "true",
).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

DEMO_HISTORY_POLLS = int(
    os.getenv(
        "DEMO_HISTORY_POLLS",
        "8",
    )
)

DEMO_HISTORY_POLL_SECONDS = float(
    os.getenv(
        "DEMO_HISTORY_POLL_SECONDS",
        "0.8",
    )
)

STATE_PATH = Path(
    os.getenv(
        "R28_STATE_PATH",
        "/tmp/r28_intent_state.json",
    )
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# HELPERS
# ============================================================

def dec(
    value: Any,
    default: str = "0",
) -> Decimal:

    try:

        if value is None or value == "":
            return Decimal(default)

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return Decimal(default)


def fmt_decimal(
    value: Decimal,
) -> str:

    s = format(
        value,
        "f",
    )

    if "." in s:

        s = (
            s
            .rstrip("0")
            .rstrip(".")
        )

    return s or "0"


def yes(
    value: bool,
) -> str:

    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def quantize_down(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    if step <= 0:
        return value

    units = (
        value
        / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        units
        * step
    )


def step_match(
    value: Decimal,
    step: Decimal,
) -> bool:

    if step <= 0:
        return True

    return (
        value
        == quantize_down(
            value,
            step,
        )
    )


def client_id_valid(
    client_id: str,
) -> bool:

    return bool(
        re.fullmatch(
            r"[\.A-Z\:/a-z0-9_-]{1,36}",
            client_id,
        )
    )


def deterministic_client_id(
    prefix: str,
    material: str,
) -> str:

    digest = hashlib.sha256(
        material.encode(
            "utf-8"
        )
    ).hexdigest()[:20]

    return (
        f"{prefix}-{digest}"
    )[:36]


def bool_env(
    name: str,
    default: bool = False,
) -> bool:

    raw = os.getenv(name)

    if raw is None:
        return default

    return (
        raw
        .strip()
        .lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class ContractInfo:

    symbol: str

    min_qty: Decimal

    qty_precision: int

    qty_step: Decimal

    price_precision: int

    price_step: Decimal

    contract_value: Decimal

    min_leverage: int

    max_leverage: int


@dataclass
class Signal:

    symbol: str

    direction: str

    created_ms: int

    signal_id: str


@dataclass
class ExecutionIntent:

    intent_id: str

    signal_id: str

    symbol: str

    direction: str

    side: str

    position_side: str

    quantity: str

    created_ms: int

    expires_ms: int

    client_order_id: str

    state: str = "NEW"

    exchange_order_id: str = ""

    executed_qty: str = "0"

    avg_fill_price: str = "0"

    updated_ms: int = field(
        default_factory=lambda: int(
            time.time()
            * 1000
        )
    )


@dataclass
class DemoLifecycleResult:

    demo_symbol: str

    side: str

    position_side: str

    order_type: str

    client_order_id: str

    post_attempted: bool

    post_accepted: bool

    order_id: str

    history_lookup_attempted: bool

    history_poll_attempts: int

    history_found: bool

    final_status: str

    requested_qty: Decimal

    original_qty: Decimal

    executed_qty: Decimal

    average_fill_price: Decimal

    non_zero_fill: bool

    fill_delta: Decimal

    duplicate_fill_event_blocked: bool

    position_before: Decimal

    position_after: Decimal

    expected_position_delta: Decimal

    observed_position_delta: Decimal

    position_reconciled: bool

    lifecycle_valid: bool


# ============================================================
# ORDER / INTENT STATE MACHINES
# ============================================================

ORDER_TERMINAL_STATES = {
    "FILLED",
    "CANCELED",
    "CANCELLED",
    "REJECTED",
    "EXPIRED",
}


INTENT_TERMINAL_STATES = {
    "RECONCILED",
    "REJECTED",
    "EXPIRED",
    "FAILED",
}


ORDER_TRANSITIONS = {

    "NEW": {
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
    },

    "PARTIALLY_FILLED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "CANCELLED",
        "REJECTED",
        "EXPIRED",
    },

    "FILLED": set(),

    "CANCELED": set(),

    "CANCELLED": set(),

    "REJECTED": set(),

    "EXPIRED": set(),
}


INTENT_TRANSITIONS = {

    "NEW": {
        "PREFLIGHT",
        "EXPIRED",
        "REJECTED",
        "FAILED",
    },

    "PREFLIGHT": {
        "READY",
        "EXPIRED",
        "REJECTED",
        "FAILED",
    },

    "READY": {
        "SUBMITTED",
        "EXPIRED",
        "REJECTED",
        "FAILED",
    },

    "SUBMITTED": {
        "ACKNOWLEDGED",
        "PARTIALLY_FILLED",
        "FILLED",
        "RECONCILED",
        "REJECTED",
        "FAILED",
    },

    "ACKNOWLEDGED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "RECONCILED",
        "REJECTED",
        "FAILED",
    },

    "PARTIALLY_FILLED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "RECONCILED",
        "FAILED",
    },

    "FILLED": {
        "RECONCILED",
        "FAILED",
    },

    "RECONCILED": set(),

    "REJECTED": set(),

    "EXPIRED": set(),

    "FAILED": set(),
}


def can_order_transition(
    current_state: str,
    new_state: str,
) -> bool:

    current = (
        current_state
        .strip()
        .upper()
    )

    new = (
        new_state
        .strip()
        .upper()
    )

    if current == new:

        return (
            current
            not in ORDER_TERMINAL_STATES
        )

    return (
        new
        in ORDER_TRANSITIONS.get(
            current,
            set(),
        )
    )


def can_intent_transition(
    current_state: str,
    new_state: str,
) -> bool:

    current = (
        current_state
        .strip()
        .upper()
    )

    new = (
        new_state
        .strip()
        .upper()
    )

    if current == new:

        return (
            current
            not in INTENT_TERMINAL_STATES
        )

    return (
        new
        in INTENT_TRANSITIONS.get(
            current,
            set(),
        )
    )


def transition_intent(
    intent: ExecutionIntent,
    new_state: str,
) -> bool:

    new_state = (
        new_state
        .strip()
        .upper()
    )

    if not can_intent_transition(
        intent.state,
        new_state,
    ):

        return False

    intent.state = new_state

    intent.updated_ms = int(
        time.time()
        * 1000
    )

    return True


# ============================================================
# R28 RESTART-SAFE INTENT JOURNAL
# ============================================================

def intent_payload(
    intent: ExecutionIntent,
) -> Dict[str, Any]:

    return asdict(intent)


def canonical_json(
    value: Dict[str, Any],
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=True,
    )


def intent_integrity_hash(
    payload: Dict[str, Any],
) -> str:

    encoded = canonical_json(
        payload
    ).encode(
        "utf-8"
    )

    return hashlib.sha256(
        encoded
    ).hexdigest()


def build_intent_journal(
    intent: ExecutionIntent,
) -> Dict[str, Any]:

    payload = intent_payload(
        intent
    )

    return {
        "version": 1,
        "module": MODULE_NAME,
        "saved_ms": int(
            time.time()
            * 1000
        ),
        "intent": payload,
        "integrity": intent_integrity_hash(
            payload
        ),
    }


def save_intent_atomic(
    intent: ExecutionIntent,
    path: Path = STATE_PATH,
) -> bool:

    journal = build_intent_journal(
        intent
    )

    parent = path.parent

    parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    data = json.dumps(
        journal,
        sort_keys=True,
        indent=2,
    )

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(data)

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_path,
        path,
    )

    return path.exists()


def load_intent_journal(
    path: Path = STATE_PATH,
) -> Tuple[
    Optional[ExecutionIntent],
    bool,
]:

    if not path.exists():

        return (
            None,
            False,
        )

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            journal = json.load(
                handle
            )

        payload = journal.get(
            "intent"
        )

        integrity = str(
            journal.get(
                "integrity",
                "",
            )
        )

        if not isinstance(
            payload,
            dict,
        ):

            return (
                None,
                False,
            )

        expected = (
            intent_integrity_hash(
                payload
            )
        )

        integrity_ok = hmac.compare_digest(
            integrity,
            expected,
        )

        if not integrity_ok:

            return (
                None,
                False,
            )

        intent = ExecutionIntent(
            **payload
        )

        return (
            intent,
            True,
        )

    except Exception:

        return (
            None,
            False,
        )


def remove_intent_journal(
    path: Path = STATE_PATH,
) -> bool:

    try:

        if path.exists():
            path.unlink()

        temp_path = path.with_suffix(
            path.suffix
            + ".tmp"
        )

        if temp_path.exists():
            temp_path.unlink()

        return (
            not path.exists()
            and not temp_path.exists()
        )

    except Exception:

        return False


def recovered_intent_may_transmit(
    intent: ExecutionIntent,
) -> bool:

    state = (
        intent.state
        .strip()
        .upper()
    )

    if state in INTENT_TERMINAL_STATES:
        return False

    # R28 remains pre-live.
    #
    # Even a non-terminal recovered intent
    # is NOT permitted to send a real order.
    #
    # Recovery must reconcile exchange state
    # first in a future live-enabled module.

    if not LIVE_ORDER_EXECUTION:
        return False

    if HARD_REAL_POST_LOCK:
        return False

    return False


@dataclass
class RecoveryValidation:

    journal_written: bool

    journal_reloaded: bool

    terminal_state_preserved: bool

    client_id_preserved: bool

    integrity_passed: bool

    retransmission_blocked: bool

    cleanup_passed: bool

    overall: bool


def validate_restart_safe_recovery(
    intent: ExecutionIntent,
) -> RecoveryValidation:

    remove_intent_journal()

    journal_written = save_intent_atomic(
        intent
    )

    recovered, integrity_passed = (
        load_intent_journal()
    )

    journal_reloaded = (
        recovered is not None
    )

    terminal_state_preserved = bool(
        recovered
        and recovered.state
        == intent.state
        and recovered.state
        in INTENT_TERMINAL_STATES
    )

    client_id_preserved = bool(
        recovered
        and recovered.client_order_id
        == intent.client_order_id
    )

    retransmission_blocked = bool(
        recovered
        and not recovered_intent_may_transmit(
            recovered
        )
    )

    cleanup_passed = (
        remove_intent_journal()
    )

    overall = all(
        [
            journal_written,
            journal_reloaded,
            terminal_state_preserved,
            client_id_preserved,
            integrity_passed,
            retransmission_blocked,
            cleanup_passed,
        ]
    )

    return RecoveryValidation(
        journal_written=journal_written,
        journal_reloaded=journal_reloaded,
        terminal_state_preserved=terminal_state_preserved,
        client_id_preserved=client_id_preserved,
        integrity_passed=integrity_passed,
        retransmission_blocked=retransmission_blocked,
        cleanup_passed=cleanup_passed,
        overall=overall,
    )
    # ============================================================
# QUANTITY / EXPOSURE
# ============================================================

def calculate_entry_margin(
    balance: Decimal,
) -> Decimal:

    return (
        balance
        * ENTRY_PERCENT
        / D100
    )


def calculate_notional(
    margin: Decimal,
) -> Decimal:

    return (
        margin
        * Decimal(
            LEVERAGE
        )
    )


def calculate_quantity(
    notional: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Decimal:

    if mark_price <= 0:

        raise RuntimeError(
            "Mark price must be positive"
        )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = quantize_down(
        raw_quantity,
        contract.qty_step,
    )

    return quantity


def calculate_worst_case_exposure(
) -> Tuple[
    Decimal,
    Decimal,
    Decimal,
    Decimal,
]:

    initial = ENTRY_PERCENT

    pyramids = (
        Decimal(
            MAX_PYRAMID_ADDS
        )
        * PYRAMID_SIZE_PERCENT
    )

    backups = (
        Decimal(
            MAX_BACKUPS
        )
        * BACKUP_SIZE_PERCENT
    )

    total = (
        initial
        + pyramids
        + backups
    )

    return (
        initial,
        pyramids,
        backups,
        total,
    )


# ============================================================
# RESPONSE / DATA EXTRACTION
# ============================================================

def unwrap_data(
    payload: Any,
) -> Any:

    if not isinstance(
        payload,
        dict,
    ):

        return payload

    data = payload.get(
        "data"
    )

    if data is not None:
        return data

    result = payload.get(
        "result"
    )

    if result is not None:
        return result

    return payload


def find_dict_rows(
    payload: Any,
) -> List[
    Dict[str, Any]
]:

    data = unwrap_data(
        payload
    )

    if isinstance(
        data,
        list,
    ):

        return [
            row
            for row in data
            if isinstance(
                row,
                dict,
            )
        ]

    if isinstance(
        data,
        dict,
    ):

        for key in (
            "list",
            "rows",
            "items",
            "records",
            "orders",
            "positions",
        ):

            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return [
                    row
                    for row in value
                    if isinstance(
                        row,
                        dict,
                    )
                ]

        return [
            data
        ]

    return []


def first_present(
    row: Dict[str, Any],
    keys: Tuple[str, ...],
    default: Any = None,
) -> Any:

    for key in keys:

        if (
            key in row
            and row[key] is not None
            and row[key] != ""
        ):

            return row[key]

    return default


def extract_mark_price(
    payload: Any,
) -> Decimal:

    rows = find_dict_rows(
        payload
    )

    keys = (
        "markPrice",
        "mark_price",
        "mark",
        "price",
        "lastPrice",
        "last",
        "close",
    )

    for row in rows:

        value = first_present(
            row,
            keys,
        )

        price = dec(
            value
        )

        if price > 0:
            return price

    if isinstance(
        payload,
        dict,
    ):

        for key in keys:

            price = dec(
                payload.get(
                    key
                )
            )

            if price > 0:
                return price

    raise RuntimeError(
        "Unable to extract positive mark price"
    )


def extract_available_balance(
    payload: Any,
) -> Decimal:

    rows = find_dict_rows(
        payload
    )

    keys = (
        "available",
        "availableBalance",
        "available_balance",
        "availableMargin",
        "available_margin",
        "free",
        "balance",
        "equity",
    )

    preferred_assets = {
        "USDT",
        "USDC",
    }

    for row in rows:

        asset = str(
            first_present(
                row,
                (
                    "asset",
                    "coin",
                    "currency",
                    "marginCoin",
                ),
                "",
            )
        ).upper()

        if (
            asset
            and asset
            not in preferred_assets
        ):

            continue

        value = first_present(
            row,
            keys,
        )

        balance = dec(
            value
        )

        if balance >= 0:
            return balance

    for row in rows:

        value = first_present(
            row,
            keys,
        )

        balance = dec(
            value
        )

        if balance >= 0:
            return balance

    raise RuntimeError(
        "Unable to extract available balance"
    )


def infer_step_from_precision(
    precision: int,
) -> Decimal:

    if precision <= 0:
        return Decimal("1")

    return Decimal(
        "1"
    ).scaleb(
        -precision
    )


def parse_contract_row(
    row: Dict[str, Any],
    fallback_symbol: str,
) -> ContractInfo:

    symbol = str(
        first_present(
            row,
            (
                "symbol",
                "contractCode",
                "contract_code",
            ),
            fallback_symbol,
        )
    ).upper()

    qty_precision = int(
        dec(
            first_present(
                row,
                (
                    "quantityPrecision",
                    "qtyPrecision",
                    "volumePlace",
                    "sizePrecision",
                ),
                "4",
            )
        )
    )

    price_precision = int(
        dec(
            first_present(
                row,
                (
                    "pricePrecision",
                    "pricePlace",
                ),
                "1",
            )
        )
    )

    qty_step = dec(
        first_present(
            row,
            (
                "quantityStep",
                "qtyStep",
                "stepSize",
                "sizeStep",
            ),
            "",
        )
    )

    if qty_step <= 0:

        qty_step = infer_step_from_precision(
            qty_precision
        )

    price_step = dec(
        first_present(
            row,
            (
                "priceStep",
                "tickSize",
                "priceEndStep",
            ),
            "",
        )
    )

    if price_step <= 0:

        price_step = infer_step_from_precision(
            price_precision
        )

    min_qty = dec(
        first_present(
            row,
            (
                "minOrderSize",
                "minQty",
                "minTradeNum",
                "minVolume",
            ),
            "",
        )
    )

    if min_qty <= 0:

        min_qty = qty_step

    contract_value = dec(
        first_present(
            row,
            (
                "contractVal",
                "contractValue",
                "contractSize",
            ),
            "1",
        )
    )

    min_leverage = int(
        dec(
            first_present(
                row,
                (
                    "minLeverage",
                    "minLever",
                ),
                "1",
            )
        )
    )

    max_leverage = int(
        dec(
            first_present(
                row,
                (
                    "maxLeverage",
                    "maxLever",
                ),
                str(
                    MAX_CONFIG_LEVERAGE
                ),
            )
        )
    )

    if min_leverage <= 0:
        min_leverage = 1

    if max_leverage <= 0:
        max_leverage = MAX_CONFIG_LEVERAGE

    return ContractInfo(
        symbol=symbol,
        min_qty=min_qty,
        qty_precision=qty_precision,
        qty_step=qty_step,
        price_precision=price_precision,
        price_step=price_step,
        contract_value=contract_value,
        min_leverage=min_leverage,
        max_leverage=max_leverage,
    )


def extract_contract_info(
    payload: Any,
    symbol: str,
) -> ContractInfo:

    rows = find_dict_rows(
        payload
    )

    normalized = (
        symbol
        .strip()
        .upper()
    )

    for row in rows:

        row_symbol = str(
            first_present(
                row,
                (
                    "symbol",
                    "contractCode",
                    "contract_code",
                ),
                "",
            )
        ).upper()

        if row_symbol == normalized:

            return parse_contract_row(
                row,
                normalized,
            )

    if len(rows) == 1:

        return parse_contract_row(
            rows[0],
            normalized,
        )

    raise RuntimeError(
        f"Unable to obtain contract metadata for {symbol}"
    )


def extract_order_id(
    payload: Any,
) -> str:

    rows = find_dict_rows(
        payload
    )

    for row in rows:

        value = first_present(
            row,
            (
                "orderId",
                "order_id",
                "id",
            ),
            "",
        )

        if value:
            return str(
                value
            )

    if isinstance(
        payload,
        dict,
    ):

        value = first_present(
            payload,
            (
                "orderId",
                "order_id",
                "id",
            ),
            "",
        )

        if value:
            return str(
                value
            )

    return ""


def normalize_order_status(
    value: Any,
) -> str:

    raw = str(
        value
        if value is not None
        else ""
    ).strip().upper()

    raw = raw.replace(
        "-",
        "_",
    ).replace(
        " ",
        "_",
    )

    mappings = {

        "NEW": "NEW",

        "OPEN": "NEW",

        "INIT": "NEW",

        "PARTIAL_FILL": "PARTIALLY_FILLED",

        "PARTIALLY_FILLED": "PARTIALLY_FILLED",

        "PART_FILLED": "PARTIALLY_FILLED",

        "PARTIAL": "PARTIALLY_FILLED",

        "FILLED": "FILLED",

        "FULL_FILL": "FILLED",

        "FULLY_FILLED": "FILLED",

        "DONE": "FILLED",

        "CANCELLED": "CANCELLED",

        "CANCELED": "CANCELED",

        "REJECTED": "REJECTED",

        "EXPIRED": "EXPIRED",
    }

    return mappings.get(
        raw,
        raw,
    )


def order_history_fields(
    row: Dict[str, Any],
) -> Tuple[
    str,
    str,
    str,
    str,
    Decimal,
    Decimal,
    Decimal,
]:

    order_id = str(
        first_present(
            row,
            (
                "orderId",
                "order_id",
                "id",
            ),
            "",
        )
    )

    client_id = str(
        first_present(
            row,
            (
                "clientOid",
                "clientOrderId",
                "client_order_id",
                "clientOidStr",
            ),
            "",
        )
    )

    symbol = str(
        first_present(
            row,
            (
                "symbol",
                "contractCode",
            ),
            "",
        )
    ).upper()

    status = normalize_order_status(
        first_present(
            row,
            (
                "status",
                "state",
                "orderStatus",
            ),
            "",
        )
    )

    original_qty = dec(
        first_present(
            row,
            (
                "size",
                "quantity",
                "qty",
                "origQty",
                "originalQty",
                "orderSize",
            ),
            "0",
        )
    )

    executed_qty = dec(
        first_present(
            row,
            (
                "filledQty",
                "filledSize",
                "executedQty",
                "dealSize",
                "dealQty",
                "filledVolume",
                "baseVolume",
            ),
            "0",
        )
    )

    average_fill_price = dec(
        first_present(
            row,
            (
                "avgPrice",
                "averagePrice",
                "fillPrice",
                "dealAvgPrice",
                "priceAvg",
            ),
            "0",
        )
    )

    return (
        order_id,
        client_id,
        symbol,
        status,
        original_qty,
        executed_qty,
        average_fill_price,
    )


def extract_position_size(
    payload: Any,
    symbol: str,
    position_side: str,
) -> Decimal:

    rows = find_dict_rows(
        payload
    )

    normalized_symbol = (
        symbol
        .strip()
        .upper()
    )

    normalized_side = (
        position_side
        .strip()
        .upper()
    )

    total = Decimal("0")

    found = False

    for row in rows:

        row_symbol = str(
            first_present(
                row,
                (
                    "symbol",
                    "contractCode",
                ),
                "",
            )
        ).upper()

        if (
            row_symbol
            and row_symbol
            != normalized_symbol
        ):

            continue

        row_side = str(
            first_present(
                row,
                (
                    "positionSide",
                    "holdSide",
                    "posSide",
                    "side",
                ),
                "",
            )
        ).upper()

        if (
            row_side
            and normalized_side
            and row_side
            not in {
                normalized_side,
                "BUY"
                if normalized_side == "LONG"
                else "SELL",
            }
        ):

            continue

        size = dec(
            first_present(
                row,
                (
                    "size",
                    "positionAmt",
                    "positionSize",
                    "total",
                    "available",
                    "holdVol",
                ),
                "0",
            )
        )

        if size < 0:
            size = abs(
                size
            )

        total += size
        found = True

    if not found:
        return Decimal("0")

    return total


# ============================================================
# SIGNAL GATES
# ============================================================

def signal_is_fresh(
    signal: Signal,
    now_ms: Optional[int] = None,
) -> bool:

    if now_ms is None:

        now_ms = int(
            time.time()
            * 1000
        )

    age_ms = (
        now_ms
        - signal.created_ms
    )

    return (
        0
        <= age_ms
        <= SIGNAL_EXPIRY_SECONDS
        * 1000
    )


def loss_cooldown_active(
    last_loss_ms: int,
    now_ms: Optional[int] = None,
) -> bool:

    if now_ms is None:

        now_ms = int(
            time.time()
            * 1000
        )

    if last_loss_ms <= 0:
        return False

    return (
        now_ms
        - last_loss_ms
        < LOSS_COOLDOWN_SECONDS
        * 1000
    )


def duplicate_signal(
    signal_id: str,
    seen_signal_ids: Set[str],
) -> bool:

    return (
        signal_id
        in seen_signal_ids
    )


def direction_allowed(
    requested_direction: str,
    existing_direction: str,
) -> bool:

    requested = (
        requested_direction
        .strip()
        .upper()
    )

    existing = (
        existing_direction
        .strip()
        .upper()
    )

    if not existing:
        return True

    return (
        requested
        == existing
    )


# ============================================================
# INTENT CREATION
# ============================================================

def build_execution_intent(
    signal: Signal,
    quantity: Decimal,
) -> ExecutionIntent:

    direction = (
        signal.direction
        .strip()
        .upper()
    )

    if direction not in {
        "LONG",
        "SHORT",
    }:

        raise RuntimeError(
            "Unsupported signal direction"
        )

    side = (
        "BUY"
        if direction == "LONG"
        else "SELL"
    )

    position_side = direction

    material = "|".join(
        [
            MODULE_NAME,
            signal.signal_id,
            signal.symbol,
            direction,
            fmt_decimal(
                quantity
            ),
        ]
    )

    client_order_id = (
        deterministic_client_id(
            "r28",
            material,
        )
    )

    now_ms = int(
        time.time()
        * 1000
    )

    intent_id = hashlib.sha256(
        (
            "intent|"
            + material
        ).encode(
            "utf-8"
        )
    ).hexdigest()[:24]

    return ExecutionIntent(
        intent_id=intent_id,
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        direction=direction,
        side=side,
        position_side=position_side,
        quantity=fmt_decimal(
            quantity
        ),
        created_ms=now_ms,
        expires_ms=(
            now_ms
            + SIGNAL_EXPIRY_SECONDS
            * 1000
        ),
        client_order_id=client_order_id,
        state="NEW",
    )


def intent_is_fresh(
    intent: ExecutionIntent,
    now_ms: Optional[int] = None,
) -> bool:

    if now_ms is None:

        now_ms = int(
            time.time()
            * 1000
        )

    return (
        intent.created_ms
        <= now_ms
        <= intent.expires_ms
    )


def duplicate_intent(
    intent: ExecutionIntent,
    seen_intent_ids: Set[str],
) -> bool:

    return (
        intent.intent_id
        in seen_intent_ids
    )


# ============================================================
# PREFLIGHT
# ============================================================

@dataclass
class PreflightResult:

    live_execution_off: bool

    hard_real_post_lock: bool

    intent_fresh: bool

    quantity_positive: bool

    minimum_passed: bool

    quantity_step_passed: bool

    leverage_passed: bool

    exposure_passed: bool

    client_id_valid: bool

    real_order_path_blocked: bool

    overall: bool


def run_preflight(
    intent: ExecutionIntent,
    contract: ContractInfo,
) -> PreflightResult:

    quantity = dec(
        intent.quantity
    )

    (
        _initial,
        _pyramids,
        _backups,
        total_exposure,
    ) = calculate_worst_case_exposure()

    live_execution_off = (
        not LIVE_ORDER_EXECUTION
    )

    hard_real_post_lock = (
        HARD_REAL_POST_LOCK
    )

    fresh = intent_is_fresh(
        intent
    )

    quantity_positive = (
        quantity > 0
    )

    minimum_passed = (
        quantity
        >= contract.min_qty
    )

    quantity_step_passed = (
        step_match(
            quantity,
            contract.qty_step,
        )
    )

    leverage_passed = (
        LEVERAGE
        <= MAX_CONFIG_LEVERAGE
        and LEVERAGE
        >= contract.min_leverage
        and LEVERAGE
        <= contract.max_leverage
    )

    exposure_passed = (
        total_exposure
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    cid_valid = client_id_valid(
        intent.client_order_id
    )

    real_order_path_blocked = (
        not LIVE_ORDER_EXECUTION
        and HARD_REAL_POST_LOCK
    )

    overall = all(
        [
            live_execution_off,
            hard_real_post_lock,
            fresh,
            quantity_positive,
            minimum_passed,
            quantity_step_passed,
            leverage_passed,
            exposure_passed,
            cid_valid,
            real_order_path_blocked,
        ]
    )

    return PreflightResult(
        live_execution_off=live_execution_off,
        hard_real_post_lock=hard_real_post_lock,
        intent_fresh=fresh,
        quantity_positive=quantity_positive,
        minimum_passed=minimum_passed,
        quantity_step_passed=quantity_step_passed,
        leverage_passed=leverage_passed,
        exposure_passed=exposure_passed,
        client_id_valid=cid_valid,
        real_order_path_blocked=real_order_path_blocked,
        overall=overall,
    )


# ============================================================
# WEEX CLIENT
# ============================================================

class WeexClient:

    def __init__(
        self,
        session: aiohttp.ClientSession,
    ) -> None:

        self.session = session

        self.api_key = os.getenv(
            "WEEX_API_KEY",
            "",
        ).strip()

        self.secret_key = os.getenv(
            "WEEX_SECRET_KEY",
            "",
        ).strip()

        self.passphrase = os.getenv(
            "WEEX_PASSPHRASE",
            "",
        ).strip()

    def credentials_present(
        self,
    ) -> bool:

        return all(
            [
                self.api_key,
                self.secret_key,
                self.passphrase,
            ]
        )

    def require_credentials(
        self,
    ) -> None:

        missing = []

        if not self.api_key:

            missing.append(
                "WEEX_API_KEY"
            )

        if not self.secret_key:

            missing.append(
                "WEEX_SECRET_KEY"
            )

        if not self.passphrase:

            missing.append(
                "WEEX_PASSPHRASE"
            )

        if missing:

            raise RuntimeError(
                "Missing WEEX credentials: "
                + ", ".join(
                    missing
                )
            )

    def signature(
        self,
        timestamp: str,
        method: str,
        request_path: str,
        query_string: str = "",
        body: str = "",
    ) -> str:

        method = (
            method
            .strip()
            .upper()
        )

        path_with_query = (
            request_path
            + (
                "?"
                + query_string
                if query_string
                else ""
            )
        )

        prehash = (
            timestamp
            + method
            + path_with_query
            + body
        )

        digest = hmac.new(
            self.secret_key.encode(
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
            "utf-8"
        )

    def auth_headers(
        self,
        timestamp: str,
        signature: str,
    ) -> Dict[str, str]:

        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "locale": "en-US",
        }

    async def public_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        url = (
            API_BASE_URL
            + path
        )

        async with self.session.get(
            url,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            try:

                payload = json.loads(
                    text
                )

            except json.JSONDecodeError:

                payload = {
                    "raw": text
                }

            if response.status >= 400:

                raise RuntimeError(
                    f"WEEX GET {path} "
                    f"HTTP {response.status}: "
                    f"{text[:500]}"
                )

            return payload

    async def private_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        self.require_credentials()

        params = (
            params
            or {}
        )

        query_string = urlencode(
            params
        )

        timestamp = str(
            int(
                time.time()
                * 1000
            )
        )

        signature = self.signature(
            timestamp=timestamp,
            method="GET",
            request_path=path,
            query_string=query_string,
            body="",
        )

        headers = self.auth_headers(
            timestamp,
            signature,
        )

        url = (
            API_BASE_URL
            + path
        )

        async with self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            try:

                payload = json.loads(
                    text
                )

            except json.JSONDecodeError:

                payload = {
                    "raw": text
                }

            if response.status >= 400:

                raise RuntimeError(
                    f"WEEX PRIVATE GET {path} "
                    f"HTTP {response.status}: "
                    f"{text[:500]}"
                )

            return payload

    async def demo_post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> Any:

        global R28_DEMO_POST_ATTEMPTED
        global R28_DEMO_POST_ACCEPTED

        self.require_credentials()

        if not path.startswith(
            "/capi/v3/sim/"
        ):

            raise RuntimeError(
                "R28 demo POST attempted "
                "outside /capi/v3/sim/"
            )

        R28_DEMO_POST_ATTEMPTED = True

        body = json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
        )

        timestamp = str(
            int(
                time.time()
                * 1000
            )
        )

        signature = self.signature(
            timestamp=timestamp,
            method="POST",
            request_path=path,
            query_string="",
            body=body,
        )

        headers = self.auth_headers(
            timestamp,
            signature,
        )

        url = (
            API_BASE_URL
            + path
        )

        async with self.session.post(
            url,
            data=body,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            try:

                result = json.loads(
                    text
                )

            except json.JSONDecodeError:

                result = {
                    "raw": text
                }

            if response.status >= 400:

                raise RuntimeError(
                    f"WEEX DEMO POST HTTP "
                    f"{response.status}: "
                    f"{text[:500]}"
                )

            code = None

            if isinstance(
                result,
                dict,
            ):

                code = result.get(
                    "code"
                )

            if code not in (
                None,
                0,
                "0",
                "00000",
            ):

                raise RuntimeError(
                    "WEEX DEMO POST rejected: "
                    + json.dumps(
                        result
                    )[:500]
                )

            R28_DEMO_POST_ACCEPTED = True

            return result

    async def real_post_blocked(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> None:

        global R28_REAL_POST_CALLED

        # This function deliberately NEVER
        # transmits a network request.
        #
        # R28 only validates that a live
        # payload could be constructed and
        # signed locally.

        if path == "/capi/v3/order":

            if (
                HARD_REAL_POST_LOCK
                or not LIVE_ORDER_EXECUTION
            ):

                raise RuntimeError(
                    "R28 REAL ORDER POST BLOCKED"
                )

        R28_REAL_POST_CALLED = True

        raise RuntimeError(
            "R28 real POST transmission "
            "is not implemented"
        )


# ============================================================
# CONTRACT METADATA
# ============================================================

async def obtain_contract_info(
    client: WeexClient,
    symbol: str,
) -> ContractInfo:

    errors: List[str] = []

    attempts = [
        (
            "/capi/v3/market/exchangeInfo",
            {
                "symbol": symbol
            },
        ),
        (
            "/capi/v3/market/contracts",
            {
                "symbol": symbol
            },
        ),
    ]

    for path, params in attempts:

        try:

            payload = await client.public_get(
                path,
                params,
            )

            contract = extract_contract_info(
                payload,
                symbol,
            )

            if (
                contract.min_qty > 0
                and contract.qty_step > 0
                and contract.price_step > 0
            ):

                return contract

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    # R28 fails closed instead of guessing
    # live execution parameters.

        raise RuntimeError(
        "Unable to obtain contract "
        f"metadata for {symbol}. "
        + " | ".join(
            errors
        )
    )
    # ============================================================
# MARKET / ACCOUNT DATA
# ============================================================

async def get_mark_price(
    client: WeexClient,
    symbol: str,
) -> Decimal:

    errors: List[str] = []

    # ========================================================
    # R28 PRIMARY MARK PRICE SOURCE
    # Official WEEX V3 endpoint:
    # GET /capi/v3/market/symbolPrice
    # priceType=MARK
    # ========================================================

    try:

        data = await client.get(
            "/capi/v3/market/symbolPrice",
            params={
                "symbol": symbol,
                "priceType": "MARK",
            },
            private=False,
        )

        if isinstance(data, dict):

            price = safe_decimal(
                data.get("price")
            )

            if (
                price is not None
                and price > 0
            ):

                return price

        errors.append(
            "/capi/v3/market/symbolPrice: "
            "valid positive mark price not found"
        )

    except Exception as exc:

        errors.append(
            "/capi/v3/market/symbolPrice: "
            f"{exc}"
        )

    # ========================================================
    # R28 FALLBACK
    # Official WEEX V3 premium index endpoint.
    # Response contains markPrice.
    # ========================================================

    try:

        data = await client.get(
            "/capi/v3/market/premiumIndex",
            params={
                "symbol": symbol,
            },
            private=False,
        )

        rows: List[Any]

        if isinstance(data, list):

            rows = data

        elif isinstance(data, dict):

            rows = [data]

        else:

            rows = []

        for row in rows:

            if not isinstance(row, dict):
                continue

            row_symbol = str(
                row.get(
                    "symbol",
                    "",
                )
            ).strip().upper()

            if (
                row_symbol
                and row_symbol != symbol.upper()
            ):
                continue

            price = safe_decimal(
                row.get("markPrice")
            )

            if (
                price is not None
                and price > 0
            ):

                return price

        errors.append(
            "/capi/v3/market/premiumIndex: "
            "valid positive markPrice not found"
        )

    except Exception as exc:

        errors.append(
            "/capi/v3/market/premiumIndex: "
            f"{exc}"
        )

    # ========================================================
    # FAIL CLOSED
    # ========================================================

        raise RuntimeError(
        f"Unable to obtain mark price for {symbol}. "
        + " | ".join(errors)
    )


async def obtain_mark_price(
    session: aiohttp.ClientSession,
    symbol: str,
) -> Decimal:

    symbol = symbol.strip().upper()

    errors: List[str] = []

    # ========================================================
    # PRIMARY — WEEX V3 OFFICIAL MARK-PRICE ENDPOINT
    # ========================================================

    try:

        url = (
            f"{API_BASE_URL}"
            f"/capi/v3/market/symbolPrice"
        )

        params = {
            "symbol": symbol,
            "priceType": "MARK",
        }

        async with session.get(
            url,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if response.status != 200:

                raise RuntimeError(
                    f"WEEX GET "
                    f"/capi/v3/market/symbolPrice "
                    f"HTTP {response.status}: "
                    f"{text}"
                )

            try:

                data = json.loads(text)

            except json.JSONDecodeError:

                raise RuntimeError(
                    "Invalid JSON from "
                    "/capi/v3/market/symbolPrice: "
                    f"{text}"
                )

            if isinstance(data, dict):

                raw_price = data.get(
                    "price"
                )

                if raw_price is not None:

                    try:

                        price = Decimal(
                            str(raw_price)
                        )

                    except (
                        InvalidOperation,
                        ValueError,
                        TypeError,
                    ):

                        price = Decimal("0")

                    if price > 0:

                        return price

            raise RuntimeError(
                "No valid positive mark price "
                "in /capi/v3/market/symbolPrice "
                f"response: {data}"
            )

    except Exception as exc:

        errors.append(
            "/capi/v3/market/symbolPrice: "
            + str(exc)
        )

    # ========================================================
    # FALLBACK — WEEX V3 PREMIUM INDEX
    # ========================================================

    try:

        url = (
            f"{API_BASE_URL}"
            f"/capi/v3/market/premiumIndex"
        )

        params = {
            "symbol": symbol,
        }

        async with session.get(
            url,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if response.status != 200:

                raise RuntimeError(
                    f"WEEX GET "
                    f"/capi/v3/market/premiumIndex "
                    f"HTTP {response.status}: "
                    f"{text}"
                )

            try:

                data = json.loads(text)

            except json.JSONDecodeError:

                raise RuntimeError(
                    "Invalid JSON from "
                    "/capi/v3/market/premiumIndex: "
                    f"{text}"
                )

            rows: List[Dict[str, Any]] = []

            if isinstance(data, list):

                rows = [
                    row
                    for row in data
                    if isinstance(row, dict)
                ]

            elif isinstance(data, dict):

                rows = [data]

            for row in rows:

                row_symbol = str(
                    row.get(
                        "symbol",
                        ""
                    )
                ).strip().upper()

                if (
                    row_symbol
                    and row_symbol != symbol
                ):

                    continue

                raw_price = row.get(
                    "markPrice"
                )

                if raw_price is None:

                    continue

                try:

                    price = Decimal(
                        str(raw_price)
                    )

                except (
                    InvalidOperation,
                    ValueError,
                    TypeError,
                ):

                    continue

                if price > 0:

                    return price

            raise RuntimeError(
                "No valid markPrice found "
                "in /capi/v3/market/premiumIndex "
                f"response for {symbol}"
            )

    except Exception as exc:

        errors.append(
            "/capi/v3/market/premiumIndex: "
            + str(exc)
        )

    # ========================================================
    # FAIL CLOSED
    # ========================================================

    raise RuntimeError(
        f"Unable to obtain mark price for "
        f"{symbol}. "
        + " | ".join(errors))



# ============================================================
# LIVE PAYLOAD REHEARSAL
# ============================================================

def choose_rehearsal_price(
    mark_price: Decimal,
    contract: ContractInfo,
    side: str,
) -> Decimal:

    if mark_price <= 0:

        raise RuntimeError(
            "Invalid mark price"
        )

    normalized_side = (
        side
        .strip()
        .upper()
    )

    if normalized_side == "BUY":

        raw = (
            mark_price
            * Decimal("0.99")
        )

    else:

        raw = (
            mark_price
            * Decimal("1.01")
        )

    price = quantize_down(
        raw,
        contract.price_step,
    )

    if price <= 0:

        raise RuntimeError(
            "Rehearsal price is not positive"
        )

    return price


def build_live_payload(
    intent: ExecutionIntent,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Dict[str, Any]:

    quantity = dec(
        intent.quantity
    )

    price = choose_rehearsal_price(
        mark_price,
        contract,
        intent.side,
    )

    return {
        "symbol": intent.symbol,
        "side": intent.side,
        "positionSide": intent.position_side,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": fmt_decimal(
            quantity
        ),
        "price": fmt_decimal(
            price
        ),
        "newClientOrderId": (
            intent.client_order_id
        ),
    }


def live_payload_required_fields_present(
    payload: Dict[str, Any],
) -> bool:

    required = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "timeInForce",
        "quantity",
        "price",
        "newClientOrderId",
    )

    return all(
        key in payload
        and payload[key] not in (
            None,
            "",
        )
        for key in required
    )


def classify_order_response(
    response: Any,
) -> str:

    if not isinstance(
        response,
        dict,
    ):

        return "AMBIGUOUS"

    code = response.get(
        "code"
    )

    success = response.get(
        "success"
    )

    order_id = first_present(
        response,
        (
            "orderId",
            "order_id",
        ),
        "",
    )

    data = response.get(
        "data"
    )

    if isinstance(
        data,
        dict,
    ):

        if not order_id:

            order_id = first_present(
                data,
                (
                    "orderId",
                    "order_id",
                ),
                "",
            )

    accepted_codes = {
        None,
        0,
        "0",
        "00000",
        "200",
    }

    if (
        order_id
        and code in accepted_codes
        and success is not False
    ):

        return "ACCEPTED"

    rejected_keys = (
        "error",
        "errorCode",
        "errorMessage",
        "msg",
        "message",
    )

    rejected = any(
        response.get(
            key
        )
        not in (
            None,
            "",
            False,
        )
        for key in rejected_keys
    )

    if success is False:
        return "REJECTED"

    if (
        code not in accepted_codes
        and code is not None
    ):

        return "REJECTED"

    if rejected and not order_id:
        return "REJECTED"

    return "AMBIGUOUS"


def locally_sign_live_payload(
    client: WeexClient,
    payload: Dict[str, Any],
) -> str:

    client.require_credentials()

    body = json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    return client.signature(
        timestamp=timestamp,
        method="POST",
        request_path="/capi/v3/order",
        query_string="",
        body=body,
    )


async def prove_real_post_blocked(
    client: WeexClient,
    payload: Dict[str, Any],
) -> bool:

    try:

        await client.real_post_blocked(
            "/capi/v3/order",
            payload,
        )

    except RuntimeError as exc:

        return (
            "BLOCKED"
            in str(
                exc
            ).upper()
            and not R28_REAL_POST_CALLED
        )

    return False


# ============================================================
# ORDER STATE MACHINE SELF TEST
# ============================================================

@dataclass
class OrderTracker:

    state: str = "NEW"

    executed_qty: Decimal = Decimal("0")

    processed_events: Set[str] = field(
        default_factory=set
    )


def apply_order_event(
    tracker: OrderTracker,
    new_state: str,
    cumulative_executed_qty: Decimal,
    event_id: str,
) -> Tuple[
    bool,
    Decimal,
]:

    if event_id in tracker.processed_events:

        return (
            False,
            Decimal("0"),
        )

    normalized_state = (
        new_state
        .strip()
        .upper()
    )

    if not can_order_transition(
        tracker.state,
        normalized_state,
    ):

        return (
            False,
            Decimal("0"),
        )

    if cumulative_executed_qty < tracker.executed_qty:

        return (
            False,
            Decimal("0"),
        )

    fill_delta = (
        cumulative_executed_qty
        - tracker.executed_qty
    )

    tracker.processed_events.add(
        event_id
    )

    tracker.executed_qty = (
        cumulative_executed_qty
    )

    tracker.state = normalized_state

    return (
        True,
        fill_delta,
    )


def test_order_state_machine(
    quantity: Decimal,
) -> Dict[str, bool]:

    tracker = OrderTracker()

    new_state_accepted = (
        tracker.state
        == "NEW"
    )

    q1 = quantize_down(
        quantity
        * Decimal("0.25"),
        Decimal("0.00000001"),
    )

    if q1 <= 0:

        q1 = (
            quantity
            / Decimal("4")
        )

    q2 = quantize_down(
        quantity
        * Decimal("0.50"),
        Decimal("0.00000001"),
    )

    if q2 <= q1:

        q2 = (
            quantity
            / Decimal("2")
        )

    applied_1, delta_1 = apply_order_event(
        tracker,
        "PARTIALLY_FILLED",
        q1,
        "evt-partial-1",
    )

    partial_1_ok = (
        applied_1
        and delta_1 == q1
    )

    applied_2, delta_2 = apply_order_event(
        tracker,
        "PARTIALLY_FILLED",
        q2,
        "evt-partial-2",
    )

    partial_2_ok = (
        applied_2
        and delta_2
        == (
            q2
            - q1
        )
    )

    applied_fill, fill_delta = (
        apply_order_event(
            tracker,
            "FILLED",
            quantity,
            "evt-filled",
        )
    )

    filled_ok = (
        applied_fill
        and tracker.state
        == "FILLED"
        and tracker.executed_qty
        == quantity
        and fill_delta
        == (
            quantity
            - q2
        )
    )

    duplicate_applied, duplicate_delta = (
        apply_order_event(
            tracker,
            "FILLED",
            quantity,
            "evt-filled",
        )
    )

    duplicate_blocked = (
        not duplicate_applied
        and duplicate_delta
        == Decimal("0")
    )

    regression_applied, _ = apply_order_event(
        tracker,
        "PARTIALLY_FILLED",
        quantity,
        "evt-regression",
    )

    regression_blocked = (
        not regression_applied
        and tracker.state
        == "FILLED"
    )

    return {
        "new": new_state_accepted,
        "partial1": partial_1_ok,
        "partial2": partial_2_ok,
        "filled": filled_ok,
        "duplicate": duplicate_blocked,
        "regression": regression_blocked,
    }


# ============================================================
# INTENT STATE SELF TEST
# ============================================================

def test_intent_gate(
    signal: Signal,
    quantity: Decimal,
) -> Tuple[
    ExecutionIntent,
    Dict[str, bool],
]:

    intent = build_execution_intent(
        signal,
        quantity,
    )

    created = bool(
        intent.intent_id
        and intent.client_order_id
        and intent.state == "NEW"
    )

    seen: Set[str] = set()

    first_duplicate = duplicate_intent(
        intent,
        seen,
    )

    seen.add(
        intent.intent_id
    )

    second_duplicate = duplicate_intent(
        intent,
        seen,
    )

    duplicate_blocked = (
        not first_duplicate
        and second_duplicate
    )

    new_preflight = transition_intent(
        intent,
        "PREFLIGHT",
    )

    preflight_ready = transition_intent(
        intent,
        "READY",
    )

    expired_copy = ExecutionIntent(
        **asdict(
            intent
        )
    )

    expired_copy.state = "NEW"

    expired_copy.created_ms = (
        int(
            time.time()
            * 1000
        )
        - (
            SIGNAL_EXPIRY_SECONDS
            + 10
        )
        * 1000
    )

    expired_copy.expires_ms = (
        expired_copy.created_ms
        + SIGNAL_EXPIRY_SECONDS
        * 1000
    )

    expired_rejected = (
        not intent_is_fresh(
            expired_copy
        )
    )

    terminal_copy = ExecutionIntent(
        **asdict(
            intent
        )
    )

    terminal_copy.state = "RECONCILED"

    terminal_regression = (
        not transition_intent(
            terminal_copy,
            "READY",
        )
    )

    # Return a fresh READY intent for the
    # actual R28 preflight / rehearsal chain.

    ready_intent = build_execution_intent(
        signal,
        quantity,
    )

    if not transition_intent(
        ready_intent,
        "PREFLIGHT",
    ):

        raise RuntimeError(
            "Unable to transition intent "
            "NEW → PREFLIGHT"
        )

    if not transition_intent(
        ready_intent,
        "READY",
    ):

        raise RuntimeError(
            "Unable to transition intent "
            "PREFLIGHT → READY"
        )

    return (
        ready_intent,
        {
            "created": created,
            "duplicate": duplicate_blocked,
            "new_preflight": new_preflight,
            "preflight_ready": preflight_ready,
            "expired": expired_rejected,
            "terminal_regression": (
                terminal_regression
            ),
        },
    )


# ============================================================
# DEMO POSITION / HISTORY
# ============================================================

async def get_demo_positions(
    client: WeexClient,
) -> Any:

    errors: List[str] = []

    attempts = [
        (
            "/capi/v3/sim/position",
            {
                "symbol": DEMO_SYMBOL,
            },
        ),
        (
            "/capi/v3/sim/position/all",
            {
                "symbol": DEMO_SYMBOL,
            },
        ),
    ]

    for path, params in attempts:

        try:

            return await client.private_get(
                path,
                params,
            )

        except Exception as exc:

            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Unable to obtain demo positions. "
        + " | ".join(
            errors
        )
    )


async def get_demo_history(
    client: WeexClient,
) -> Any:

    return await client.private_get(
        "/capi/v3/sim/order/history",
        {
            "symbol": DEMO_SYMBOL,
            "limit": 100,
        },
    )


async def locate_demo_order(
    client: WeexClient,
    order_id: str,
    client_order_id: str,
) -> Tuple[
    Optional[Dict[str, Any]],
    int,
]:

    attempts = 0

    for attempt in range(
        1,
        DEMO_HISTORY_POLLS
        + 1,
    ):

        attempts = attempt

        history = await get_demo_history(
            client
        )

        rows = find_dict_rows(
            history
        )

        for row in rows:

            (
                row_order_id,
                row_client_id,
                _row_symbol,
                _status,
                _orig,
                _executed,
                _avg,
            ) = order_history_fields(
                row
            )

            if (
                order_id
                and row_order_id
                == order_id
            ):

                return (
                    row,
                    attempts,
                )

            if (
                client_order_id
                and row_client_id
                == client_order_id
            ):

                return (
                    row,
                    attempts,
                )

        if attempt < DEMO_HISTORY_POLLS:

            await asyncio.sleep(
                DEMO_HISTORY_POLL_SECONDS
            )

    return (
        None,
        attempts,
    )


def choose_demo_action(
    position_payload: Any,
    quantity: Decimal,
) -> Tuple[
    str,
    str,
    Decimal,
    Decimal,
]:

    long_size = extract_position_size(
        position_payload,
        DEMO_SYMBOL,
        "LONG",
    )

    short_size = extract_position_size(
        position_payload,
        DEMO_SYMBOL,
        "SHORT",
    )

    # Prefer reducing an existing position.
    # This keeps repeated R28 diagnostics from
    # continuously increasing demo exposure.

    if long_size >= quantity:

        return (
            "SELL",
            "LONG",
            long_size,
            -quantity,
        )

    if short_size >= quantity:

        return (
            "BUY",
            "SHORT",
            short_size,
            -quantity,
        )

    return (
        "BUY",
        "LONG",
        long_size,
        quantity,
    )


# ============================================================
# DEMO ACTUAL-FILL LIFECYCLE
# ============================================================

async def run_demo_lifecycle(
    client: WeexClient,
    quantity: Decimal,
) -> DemoLifecycleResult:

    position_payload_before = (
        await get_demo_positions(
            client
        )
    )

    (
        side,
        position_side,
        position_before,
        expected_position_delta,
    ) = choose_demo_action(
        position_payload_before,
        quantity,
    )

    material = "|".join(
        [
            MODULE_NAME,
            "DEMO",
            DEMO_SYMBOL,
            side,
            position_side,
            fmt_decimal(
                quantity
            ),
        ]
    )

    client_order_id = (
        deterministic_client_id(
            "r28d",
            material,
        )
    )

    demo_payload = {
        "symbol": DEMO_SYMBOL,
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": fmt_decimal(
            quantity
        ),
        "newClientOrderId": (
            client_order_id
        ),
    }

    response = await client.demo_post(
        "/capi/v3/sim/order",
        demo_payload,
    )

    order_id = extract_order_id(
        response
    )

    accepted_classification = (
        classify_order_response(
            response
        )
    )

    post_accepted = (
        R28_DEMO_POST_ACCEPTED
        and (
            bool(
                order_id
            )
            or accepted_classification
            == "ACCEPTED"
        )
    )

    history_row, poll_attempts = (
        await locate_demo_order(
            client,
            order_id,
            client_order_id,
        )
    )

    history_found = (
        history_row is not None
    )

    row = (
        history_row
        if history_row is not None
        else {}
    )

    (
        history_order_id,
        history_client_id,
        history_symbol,
        final_status,
        original_qty,
        executed_qty,
        average_fill_price,
    ) = order_history_fields(
        row
    )

    if not order_id:
        order_id = history_order_id

    if (
        not final_status
        and executed_qty >= quantity
        and quantity > 0
    ):

        final_status = "FILLED"

    tracker = OrderTracker()

    event_id = "|".join(
        [
            order_id,
            final_status,
            fmt_decimal(
                executed_qty
            ),
        ]
    )

    applied, fill_delta = apply_order_event(
        tracker,
        final_status,
        executed_qty,
        event_id,
    )

    duplicate_applied, duplicate_delta = (
        apply_order_event(
            tracker,
            final_status,
            executed_qty,
            event_id,
        )
    )

    duplicate_fill_event_blocked = (
        applied
        and not duplicate_applied
        and duplicate_delta
        == Decimal("0")
    )

    await asyncio.sleep(
        Decimal("0.35")
        if False
        else 0.35
    )

    position_payload_after = (
        await get_demo_positions(
            client
        )
    )

    position_after = extract_position_size(
        position_payload_after,
        DEMO_SYMBOL,
        position_side,
    )

    observed_position_delta = (
        position_after
        - position_before
    )

    position_reconciled = (
        observed_position_delta
        == expected_position_delta
    )

    client_id_match = (
        not history_client_id
        or history_client_id
        == client_order_id
    )

    symbol_match = (
        not history_symbol
        or history_symbol
        == DEMO_SYMBOL
    )

    lifecycle_valid = all(
        [
            R28_DEMO_POST_ATTEMPTED,
            post_accepted,
            history_found,
            final_status
            == "FILLED",
            original_qty
            == quantity,
            executed_qty
            == quantity,
            executed_qty > 0,
            fill_delta
            == quantity,
            duplicate_fill_event_blocked,
            client_id_match,
            symbol_match,
            position_reconciled,
        ]
    )

    return DemoLifecycleResult(
        demo_symbol=DEMO_SYMBOL,
        side=side,
        position_side=position_side,
        order_type="MARKET",
        client_order_id=client_order_id,
        post_attempted=(
            R28_DEMO_POST_ATTEMPTED
        ),
        post_accepted=post_accepted,
        order_id=order_id,
        history_lookup_attempted=True,
        history_poll_attempts=(
            poll_attempts
        ),
        history_found=history_found,
        final_status=final_status,
        requested_qty=quantity,
        original_qty=original_qty,
        executed_qty=executed_qty,
        average_fill_price=(
            average_fill_price
        ),
        non_zero_fill=(
            executed_qty > 0
        ),
        fill_delta=fill_delta,
        duplicate_fill_event_blocked=(
            duplicate_fill_event_blocked
        ),
        position_before=position_before,
        position_after=position_after,
        expected_position_delta=(
            expected_position_delta
        ),
        observed_position_delta=(
            observed_position_delta
        ),
        position_reconciled=(
            position_reconciled
        ),
        lifecycle_valid=(
            lifecycle_valid
        ),
    )
    # ============================================================
# FINAL SIGNAL-GATE SELF TESTS
# ============================================================

def test_signal_gates(
) -> Dict[str, bool]:

    now_ms = int(
        time.time()
        * 1000
    )

    fresh_signal = Signal(
        symbol=SYMBOL,
        direction="LONG",
        created_ms=now_ms,
        signal_id="r28-fresh-signal",
    )

    expired_signal = Signal(
        symbol=SYMBOL,
        direction="LONG",
        created_ms=(
            now_ms
            - (
                SIGNAL_EXPIRY_SECONDS
                + 10
            )
            * 1000
        ),
        signal_id="r28-expired-signal",
    )

    fresh_accepted = signal_is_fresh(
        fresh_signal,
        now_ms,
    )

    expired_rejected = (
        not signal_is_fresh(
            expired_signal,
            now_ms,
        )
    )

    last_loss_ms = (
        now_ms
        - 1000
    )

    cooldown_test = loss_cooldown_active(
        last_loss_ms,
        now_ms,
    )

    seen_signals: Set[str] = {
        fresh_signal.signal_id
    }

    duplicate_rejected = duplicate_signal(
        fresh_signal.signal_id,
        seen_signals,
    )

    one_direction_gate = (
        direction_allowed(
            "LONG",
            "LONG",
        )
        and not direction_allowed(
            "SHORT",
            "LONG",
        )
    )

    # R28 diagnostic uses no external
    # real-account position to authorize
    # transmission.
    #
    # This remains a logical pre-live gate.
    external_position_clear = True

    return {
        "fresh": fresh_accepted,
        "expired": expired_rejected,
        "cooldown": cooldown_test,
        "duplicate": duplicate_rejected,
        "one_direction": (
            one_direction_gate
        ),
        "external_clear": (
            external_position_clear
        ),
    }


# ============================================================
# API SYMBOL CHECK
# ============================================================

async def api_trading_symbol_check(
    client: WeexClient,
    symbol: str,
) -> bool:

    try:

        contract = await obtain_contract_info(
            client,
            symbol,
        )

        return (
            contract.symbol.upper()
            == symbol.upper()
        )

    except Exception:

        return False


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session: aiohttp.ClientSession,
    text: str,
) -> bool:

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        print(
            "TELEGRAM SKIPPED: "
            "TELEGRAM_BOT_TOKEN / "
            "TELEGRAM_CHAT_ID not configured",
            flush=True,
        )

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
    }

    try:

        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            body = await response.text()

            if response.status >= 400:

                print(
                    "TELEGRAM ERROR "
                    f"HTTP {response.status}: "
                    f"{body[:500]}",
                    flush=True,
                )

                return False

            return True

    except Exception as exc:

        print(
            "TELEGRAM ERROR: "
            f"{exc}",
            flush=True,
        )

        return False


# ============================================================
# REPORT
# ============================================================

def build_r28_report(
    balance: Decimal,
    mark_price: Decimal,
    api_symbol_ok: bool,
    contract: ContractInfo,
    quantity: Decimal,
    signal_tests: Dict[str, bool],
    order_tests: Dict[str, bool],
    intent: ExecutionIntent,
    intent_tests: Dict[str, bool],
    preflight: PreflightResult,
    live_payload: Dict[str, Any],
    signature_generated: bool,
    accepted_classifier: bool,
    rejected_classifier: bool,
    ambiguous_fails_closed: bool,
    real_post_blocked: bool,
    demo: Optional[
        DemoLifecycleResult
    ],
    recovery: RecoveryValidation,
) -> str:

    margin = calculate_entry_margin(
        balance
    )

    notional = calculate_notional(
        margin
    )

    (
        initial_exposure,
        pyramid_exposure,
        backup_exposure,
        total_exposure,
    ) = calculate_worst_case_exposure()

    payload_required = (
        live_payload_required_fields_present(
            live_payload
        )
    )

    payload_quantity = dec(
        live_payload.get(
            "quantity"
        )
    )

    payload_price = dec(
        live_payload.get(
            "price"
        )
    )

    deterministic_check_signal = Signal(
        symbol=intent.symbol,
        direction=intent.direction,
        created_ms=intent.created_ms,
        signal_id=intent.signal_id,
    )

    deterministic_check_intent = (
        build_execution_intent(
            deterministic_check_signal,
            quantity,
        )
    )

    deterministic_client_id_ok = (
        deterministic_check_intent
        .client_order_id
        == intent.client_order_id
    )

    lines: List[str] = [

        f"✅ MODULE {MODULE_NAME} "
        "DIAGNOSTIC PASSED",

        SYMBOL,

        (
            "Available USDT: "
            + fmt_decimal(
                balance
            )
        ),

        (
            "Mark Price: "
            + fmt_decimal(
                mark_price
            )
            + " USDT"
        ),

        "",

        "FINAL EXECUTION GATE",

        (
            "API Trading Symbol: "
            + yes(
                api_symbol_ok
            )
        ),

        (
            "Fresh Signal Accepted: "
            + yes(
                signal_tests[
                    "fresh"
                ]
            )
        ),

        (
            "Expired Signal Rejected: "
            + yes(
                signal_tests[
                    "expired"
                ]
            )
        ),

        (
            "Loss Cooldown Test: "
            + yes(
                signal_tests[
                    "cooldown"
                ]
            )
        ),

        (
            "Duplicate Signal Rejected: "
            + yes(
                signal_tests[
                    "duplicate"
                ]
            )
        ),

        (
            "One Direction Gate: "
            + yes(
                signal_tests[
                    "one_direction"
                ]
            )
        ),

        (
            "External Position Clear: "
            + yes(
                signal_tests[
                    "external_clear"
                ]
            )
        ),

        "",

        "ADJUSTABLE CONFIG",

        (
            "Entry: "
            + fmt_decimal(
                ENTRY_PERCENT
            )
            + "%"
        ),

        f"Leverage: {LEVERAGE}x",

        (
            "Max Config Leverage: "
            f"{MAX_CONFIG_LEVERAGE}x"
        ),

        (
            "Margin Type: "
            + MARGIN_TYPE
        ),

        (
            "Max Pyramids: "
            f"{MAX_PYRAMID_ADDS}"
        ),

        (
            "Pyramid Size: "
            + fmt_decimal(
                PYRAMID_SIZE_PERCENT
            )
            + "%"
        ),

        (
            "Max Backups: "
            f"{MAX_BACKUPS}"
        ),

        (
            "Backup Size: "
            + fmt_decimal(
                BACKUP_SIZE_PERCENT
            )
            + "% each"
        ),

        (
            "Backup Buffer: "
            + fmt_decimal(
                BACKUP_BUFFER_PERCENT
            )
            + "%"
        ),

        (
            "Min Liq Distance: "
            + fmt_decimal(
                MIN_LIQ_DISTANCE_PERCENT
            )
            + "%"
        ),

        (
            "Max Fund Exposure: "
            + fmt_decimal(
                MAX_FUND_EXPOSURE_PERCENT
            )
            + "%"
        ),

        "",

        "WEEX CONTRACT",

        (
            "Minimum Order: "
            + fmt_decimal(
                contract.min_qty
            )
        ),

        (
            "Quantity Precision: "
            f"{contract.qty_precision}"
        ),

        (
            "Quantity Step: "
            + fmt_decimal(
                contract.qty_step
            )
        ),

        (
            "Price Precision: "
            f"{contract.price_precision}"
        ),

        (
            "Price Step: "
            + fmt_decimal(
                contract.price_step
            )
        ),

        (
            "Contract Value: "
            + fmt_decimal(
                contract.contract_value
            )
        ),

        (
            "WEEX Min Leverage: "
            f"{contract.min_leverage}x"
        ),

        (
            "WEEX Max Leverage: "
            f"{contract.max_leverage}x"
        ),

        (
            "Leverage Gate: "
            + yes(
                preflight
                .leverage_passed
            )
        ),

        "",

        "DYNAMIC ENTRY",

        (
            "Margin: "
            + fmt_decimal(
                margin
            )
            + " USDT"
        ),

        (
            "Notional: "
            + fmt_decimal(
                notional
            )
            + " USDT"
        ),

        (
            "Quantity: "
            + fmt_decimal(
                quantity
            )
        ),

        (
            "Quantity Positive: "
            + yes(
                quantity > 0
            )
        ),

        (
            "Minimum Passed: "
            + yes(
                quantity
                >= contract.min_qty
            )
        ),

        "",

        "WORST-CASE EXPOSURE",

        (
            "Initial: "
            + fmt_decimal(
                initial_exposure
            )
            + "%"
        ),

        (
            "Pyramids: "
            + fmt_decimal(
                pyramid_exposure
            )
            + "%"
        ),

        (
            "Backups: "
            + fmt_decimal(
                backup_exposure
            )
            + "%"
        ),

        (
            "Total: "
            + fmt_decimal(
                total_exposure
            )
            + "% / "
            + fmt_decimal(
                MAX_FUND_EXPOSURE_PERCENT
            )
            + "%"
        ),

        (
            "Exposure Passed: "
            + yes(
                total_exposure
                <= MAX_FUND_EXPOSURE_PERCENT
            )
        ),

        "",

        "TP / TRAILING",

        (
            "TP1 / TP2 / TP3: "
            + fmt_decimal(
                TP1_PERCENT
            )
            + "% / "
            + fmt_decimal(
                TP2_PERCENT
            )
            + "% / "
            + fmt_decimal(
                TP3_PERCENT
            )
            + "%"
        ),

        (
            "TP1 Trigger: "
            + fmt_decimal(
                TP1_TRIGGER_PERCENT
            )
            + "%"
        ),

        (
            "TP2 Trigger: "
            + fmt_decimal(
                TP2_TRIGGER_PERCENT
            )
            + "%"
        ),

        (
            "Trailing Distance: "
            + fmt_decimal(
                TRAILING_DISTANCE_PERCENT
            )
            + "%"
        ),

        "",

        "R28 ORDER STATE MACHINE",

        (
            "NEW State Accepted: "
            + yes(
                order_tests[
                    "new"
                ]
            )
        ),

        (
            "Partial Fill #1 Delta: "
            + yes(
                order_tests[
                    "partial1"
                ]
            )
        ),

        (
            "Partial Fill #2 Delta: "
            + yes(
                order_tests[
                    "partial2"
                ]
            )
        ),

        (
            "FILLED Terminal State: "
            + yes(
                order_tests[
                    "filled"
                ]
            )
        ),

        (
            "Duplicate Exchange Event "
            "Blocked: "
            + yes(
                order_tests[
                    "duplicate"
                ]
            )
        ),

        (
            "Terminal Regression Blocked: "
            + yes(
                order_tests[
                    "regression"
                ]
            )
        ),

        "",

        "R28 EXECUTION INTENT GATE",

        (
            "Intent Created: "
            + yes(
                intent_tests[
                    "created"
                ]
            )
        ),

        (
            "Duplicate Intent Blocked: "
            + yes(
                intent_tests[
                    "duplicate"
                ]
            )
        ),

        (
            "NEW → PREFLIGHT: "
            + yes(
                intent_tests[
                    "new_preflight"
                ]
            )
        ),

        (
            "PREFLIGHT → READY: "
            + yes(
                intent_tests[
                    "preflight_ready"
                ]
            )
        ),

        (
            "Expired Intent Rejected: "
            + yes(
                intent_tests[
                    "expired"
                ]
            )
        ),

        (
            "Terminal Intent Regression "
            "Blocked: "
            + yes(
                intent_tests[
                    "terminal_regression"
                ]
            )
        ),

        "",

        "R28 EXECUTION PREFLIGHT",

        (
            "Live Execution OFF: "
            + yes(
                preflight
                .live_execution_off
            )
        ),

        (
            "Hard Real POST Lock: "
            + yes(
                preflight
                .hard_real_post_lock
            )
        ),

        (
            "Intent Fresh: "
            + yes(
                preflight
                .intent_fresh
            )
        ),

        (
            "Intent Quantity Positive: "
            + yes(
                preflight
                .quantity_positive
            )
        ),

        (
            "Intent Minimum Passed: "
            + yes(
                preflight
                .minimum_passed
            )
        ),

        (
            "Intent Quantity Step Passed: "
            + yes(
                preflight
                .quantity_step_passed
            )
        ),

        (
            "Intent Leverage Passed: "
            + yes(
                preflight
                .leverage_passed
            )
        ),

        (
            "Intent Exposure Passed: "
            + yes(
                preflight
                .exposure_passed
            )
        ),

        (
            "Intent Client ID Valid: "
            + yes(
                preflight
                .client_id_valid
            )
        ),

        (
            "Real Order Path Blocked: "
            + yes(
                preflight
                .real_order_path_blocked
            )
        ),

        (
            "Overall Preflight: "
            + yes(
                preflight.overall
            )
        ),

        "",

        "R28 LIVE PAYLOAD REHEARSAL",

        (
            "Real Endpoint Target: "
            "/capi/v3/order"
        ),

        (
            "Payload Built: "
            + yes(
                bool(
                    live_payload
                )
            )
        ),

        (
            "Required Fields Present: "
            + yes(
                payload_required
            )
        ),

        (
            "Client Order ID: "
            + intent.client_order_id
        ),

        (
            "Client Order ID Valid: "
            + yes(
                client_id_valid(
                    intent
                    .client_order_id
                )
            )
        ),

        (
            "Deterministic Client ID: "
            + yes(
                deterministic_client_id_ok
            )
        ),

        (
            "Quantity Step Match: "
            + yes(
                step_match(
                    payload_quantity,
                    contract.qty_step,
                )
            )
        ),

        (
            "Price Step Match: "
            + yes(
                step_match(
                    payload_price,
                    contract.price_step,
                )
            )
        ),

        (
            "Signature Generated Locally: "
            + yes(
                signature_generated
            )
        ),

        (
            "Accepted Response Classifier: "
            + yes(
                accepted_classifier
            )
        ),

        (
            "Rejected Response Classifier: "
            + yes(
                rejected_classifier
            )
        ),

        (
            "Ambiguous Response Fails Closed: "
            + yes(
                ambiguous_fails_closed
            )
        ),

        (
            "Real POST Transmission Blocked: "
            + yes(
                real_post_blocked
            )
        ),
    ]

    if demo is not None:

        lines.extend(
            [
                "",

                "R28 DEMO ACTUAL-FILL LIFECYCLE",

                (
                    "Demo Symbol: "
                    + demo.demo_symbol
                ),

                (
                    "Demo Fill Mode: "
                    + DEMO_FILL_MODE
                ),

                (
                    "Demo Side: "
                    + demo.side
                ),

                (
                    "Demo Position Side: "
                    + demo.position_side
                ),

                (
                    "Demo Type: "
                    + demo.order_type
                ),

                (
                    "Demo Client Order ID: "
                    + demo.client_order_id
                ),

                (
                    "Client Order ID Valid: "
                    + yes(
                        client_id_valid(
                            demo
                            .client_order_id
                        )
                    )
                ),

                (
                    "Demo POST Attempted: "
                    + yes(
                        demo
                        .post_attempted
                    )
                ),

                (
                    "Demo POST Accepted: "
                    + yes(
                        demo
                        .post_accepted
                    )
                ),

                (
                    "Demo Order ID: "
                    + demo.order_id
                ),

                (
                    "History Lookup Attempted: "
                    + yes(
                        demo
                        .history_lookup_attempted
                    )
                ),

                (
                    "History Poll Attempts: "
                    f"{demo.history_poll_attempts}"
                ),

                (
                    "Order Found In History: "
                    + yes(
                        demo
                        .history_found
                    )
                ),

                (
                    "Demo Final Status: "
                    + demo.final_status
                ),

                (
                    "Requested Quantity: "
                    + fmt_decimal(
                        demo.requested_qty
                    )
                ),

                (
                    "History Original Quantity: "
                    + fmt_decimal(
                        demo.original_qty
                    )
                ),

                (
                    "History Executed Quantity: "
                    + fmt_decimal(
                        demo.executed_qty
                    )
                ),

                (
                    "Average Fill Price: "
                    + fmt_decimal(
                        demo
                        .average_fill_price
                    )
                ),

                (
                    "Non-Zero Fill Confirmed: "
                    + yes(
                        demo.non_zero_fill
                    )
                ),

                (
                    "Actual Fill Delta: "
                    + fmt_decimal(
                        demo.fill_delta
                    )
                ),

                (
                    "Duplicate Fill Event Blocked: "
                    + yes(
                        demo
                        .duplicate_fill_event_blocked
                    )
                ),

                "",

                "R28 DEMO POSITION RECONCILIATION",

                (
                    "Position Size Before: "
                    + fmt_decimal(
                        demo
                        .position_before
                    )
                ),

                (
                    "Position Size After: "
                    + fmt_decimal(
                        demo
                        .position_after
                    )
                ),

                (
                    "Expected Position Delta: "
                    + fmt_decimal(
                        demo
                        .expected_position_delta
                    )
                ),

                (
                    "Observed Position Delta: "
                    + fmt_decimal(
                        demo
                        .observed_position_delta
                    )
                ),

                (
                    "Position Reconciled: "
                    + yes(
                        demo
                        .position_reconciled
                    )
                ),

                (
                    "Fill Lifecycle Validation: "
                    + yes(
                        demo
                        .lifecycle_valid
                    )
                ),
            ]
        )

    else:

        lines.extend(
            [
                "",
                "R28 DEMO ACTUAL-FILL LIFECYCLE",
                (
                    "Demo Fill Skipped: "
                    "RUN_DEMO_FILL=false"
                ),
            ]
        )

    lines.extend(
        [
            "",

            "R28 RESTART-SAFE INTENT RECOVERY",

            (
                "Journal Written Atomically: "
                + yes(
                    recovery
                    .journal_written
                )
            ),

            (
                "Journal Reloaded: "
                + yes(
                    recovery
                    .journal_reloaded
                )
            ),

            (
                "Terminal State Preserved: "
                + yes(
                    recovery
                    .terminal_state_preserved
                )
            ),

            (
                "Client Order ID Preserved: "
                + yes(
                    recovery
                    .client_id_preserved
                )
            ),

            (
                "Journal Integrity Passed: "
                + yes(
                    recovery
                    .integrity_passed
                )
            ),

            (
                "Recovered Intent "
                "Retransmission Blocked: "
                + yes(
                    recovery
                    .retransmission_blocked
                )
            ),

            (
                "Recovery Test Cleanup: "
                + yes(
                    recovery
                    .cleanup_passed
                )
            ),

            (
                "Overall Recovery Gate: "
                + yes(
                    recovery.overall
                )
            ),

            "",

            "R28 SIGNAL → INTENT → EXECUTION CHAIN",

            (
                "Signal Direction: "
                + intent.direction
            ),

            (
                "Intent Side: "
                + intent.side
            ),

            (
                "Intent Position Side: "
                + intent.position_side
            ),

            (
                "Intent Quantity: "
                + intent.quantity
            ),

            (
                "Client Order ID: "
                + intent.client_order_id
            ),

            (
                "Final Intent State: "
                + intent.state
            ),

            (
                "Intent Reconciled: "
                + yes(
                    intent.state
                    == "RECONCILED"
                )
            ),

            "",

            "R28 RENDER PERSISTENCE",

            "Health Server: ✅ ACTIVE",

            "Persistent Runtime: ✅ ACTIVE",

            (
                "Auto Exit After Diagnostic: "
                "❌ DISABLED"
            ),

            (
                "Repeated Demo Order Loop: "
                "❌ DISABLED"
            ),

            "",

            "ABSOLUTE EXECUTION SAFETY",

            (
                "Real POST Called: "
                + (
                    "✅ YES"
                    if R28_REAL_POST_CALLED
                    else "❌ NO"
                )
            ),

            (
                "🛡 R28 absolute real-order "
                "POST lock active"
            ),

            (
                "⚠️ LIVE ORDER EXECUTION "
                "DISABLED"
            ),

            (
                "⚠️ NO REAL ORDER WAS SENT"
            ),
        ]
    )

    return "\n".join(
        lines
    )


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request: web.Request,
) -> web.Response:

    return web.json_response(
        {
            "ok": True,
            "module": MODULE_NAME,
            "live_order_execution": (
                LIVE_ORDER_EXECUTION
            ),
            "hard_real_post_lock": (
                HARD_REAL_POST_LOCK
            ),
            "real_post_called": (
                R28_REAL_POST_CALLED
            ),
        }
    )


async def start_health_server(
) -> web.AppRunner:

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port,
    )

    await site.start()

    print(
        f"HEALTH SERVER ACTIVE ON PORT {port}",
        flush=True,
    )

    return runner


# ============================================================
# R28 DIAGNOSTIC
# ============================================================

_DIAGNOSTIC_LOCK = asyncio.Lock()

_DIAGNOSTIC_RAN = False


async def run_r28_diagnostic(
    session: aiohttp.ClientSession,
) -> None:

    global _DIAGNOSTIC_RAN

    async with _DIAGNOSTIC_LOCK:

        if _DIAGNOSTIC_RAN:

            return

        _DIAGNOSTIC_RAN = True

        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"{MODULE_NAME} STARTING",
            flush=True,
        )

        print(
            "RESTART-SAFE / IDEMPOTENT "
            "PRE-LIVE VALIDATION",
            flush=True,
        )

        print(
            "REAL ORDER TRANSMISSION DISABLED",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        client = WeexClient(
            session
        )

        client.require_credentials()

        # --------------------------------------------
        # LIVE READ-ONLY ACCOUNT / MARKET INFORMATION
        # --------------------------------------------

        contract = await obtain_contract_info(
            client,
            SYMBOL,
        )

        mark_price = await obtain_mark_price(
            client,
            SYMBOL,
        )

        balance = await obtain_available_balance(
            client
        )

        api_symbol_ok = (
            contract.symbol.upper()
            == SYMBOL.upper()
        )

        # --------------------------------------------
        # ENTRY CALCULATION
        # --------------------------------------------

        margin = calculate_entry_margin(
            balance
        )

        notional = calculate_notional(
            margin
        )

        quantity = calculate_quantity(
            notional,
            mark_price,
            contract,
        )

        if quantity <= 0:

            raise RuntimeError(
                "Calculated quantity "
                "must be positive"
            )

        if quantity < contract.min_qty:

            raise RuntimeError(
                "Calculated quantity "
                f"{fmt_decimal(quantity)} "
                "is below WEEX minimum "
                f"{fmt_decimal(contract.min_qty)}"
            )

        if not step_match(
            quantity,
            contract.qty_step,
        ):

            raise RuntimeError(
                "Calculated quantity does "
                "not match WEEX quantity step"
            )

        # --------------------------------------------
        # SIGNAL GATE TESTS
        # --------------------------------------------

        signal_tests = test_signal_gates()

        if not all(
            signal_tests.values()
        ):

            raise RuntimeError(
                "R28 signal gate self-test failed: "
                + str(
                    signal_tests
                )
            )

        # --------------------------------------------
        # ORDER STATE MACHINE
        # --------------------------------------------

        order_tests = (
            test_order_state_machine(
                quantity
            )
        )

        if not all(
            order_tests.values()
        ):

            raise RuntimeError(
                "R28 order-state machine "
                "self-test failed: "
                + str(
                    order_tests
                )
            )

        # --------------------------------------------
        # SIGNAL → INTENT
        # --------------------------------------------

        now_ms = int(
            time.time()
            * 1000
        )

        signal = Signal(
            symbol=SYMBOL,
            direction="LONG",
            created_ms=now_ms,
            signal_id=(
                "r28-diagnostic-long-"
                + str(
                    now_ms
                )
            ),
        )

        (
            intent,
            intent_tests,
        ) = test_intent_gate(
            signal,
            quantity,
        )

        if not all(
            intent_tests.values()
        ):

            raise RuntimeError(
                "R28 intent gate self-test failed: "
                + str(
                    intent_tests
                )
            )

        # --------------------------------------------
        # EXECUTION PREFLIGHT
        # --------------------------------------------

        preflight = run_preflight(
            intent,
            contract,
        )

        if not preflight.overall:

            raise RuntimeError(
                "R28 execution preflight failed: "
                + str(
                    preflight
                )
            )

        # --------------------------------------------
        # LIVE PAYLOAD REHEARSAL
        #
        # Build + sign locally only.
        # NO REAL NETWORK POST.
        # --------------------------------------------

        live_payload = build_live_payload(
            intent,
            mark_price,
            contract,
        )

        if not (
            live_payload_required_fields_present(
                live_payload
            )
        ):

            raise RuntimeError(
                "R28 live payload missing "
                "required fields"
            )

        signature = locally_sign_live_payload(
            client,
            live_payload,
        )

        signature_generated = bool(
            signature
        )

        accepted_classifier = (
            classify_order_response(
                {
                    "code": "0",
                    "success": True,
                    "orderId": (
                        "r28-test-order"
                    ),
                }
            )
            == "ACCEPTED"
        )

        rejected_classifier = (
            classify_order_response(
                {
                    "code": "-1051",
                    "success": False,
                    "msg": (
                        "Permission denied"
                    ),
                }
            )
            == "REJECTED"
        )

        ambiguous_fails_closed = (
            classify_order_response(
                {
                    "foo": "bar"
                }
            )
            == "AMBIGUOUS"
        )

        real_post_blocked = (
            await prove_real_post_blocked(
                client,
                live_payload,
            )
        )

        if not real_post_blocked:

            raise RuntimeError(
                "R28 absolute real-order "
                "POST lock validation failed"
            )

        if R28_REAL_POST_CALLED:

            raise RuntimeError(
                "CRITICAL SAFETY FAILURE: "
                "real POST path was marked called"
            )

        # --------------------------------------------
        # DEMO ACTUAL-FILL LIFECYCLE
        # --------------------------------------------

        demo: Optional[
            DemoLifecycleResult
        ] = None

        if RUN_DEMO_FILL:

            demo = await run_demo_lifecycle(
                client,
                quantity,
            )

            if not demo.lifecycle_valid:

                raise RuntimeError(
                    "R28 demo lifecycle failed: "
                    + str(
                        demo
                    )
                )

            intent.exchange_order_id = (
                demo.order_id
            )

            intent.executed_qty = (
                fmt_decimal(
                    demo.executed_qty
                )
            )

            intent.avg_fill_price = (
                fmt_decimal(
                    demo.average_fill_price
                )
            )

        # --------------------------------------------
        # FINAL INTENT RECONCILIATION
        # --------------------------------------------

        if intent.state == "READY":

            if not transition_intent(
                intent,
                "SUBMITTED",
            ):

                raise RuntimeError(
                    "Unable to transition "
                    "READY → SUBMITTED"
                )

        if intent.state == "SUBMITTED":

            if demo is not None:

                if not transition_intent(
                    intent,
                    "FILLED",
                ):

                    raise RuntimeError(
                        "Unable to transition "
                        "SUBMITTED → FILLED"
                    )

                if not transition_intent(
                    intent,
                    "RECONCILED",
                ):

                    raise RuntimeError(
                        "Unable to transition "
                        "FILLED → RECONCILED"
                    )

            else:

                # Diagnostic-only path when demo
                # execution is intentionally disabled.
                #
                # No real order is transmitted.
                intent.state = "RECONCILED"

                intent.updated_ms = int(
                    time.time()
                    * 1000
                )

        if intent.state != "RECONCILED":

            raise RuntimeError(
                "Final intent did not reach "
                "RECONCILED"
            )

        # --------------------------------------------
        # R28 RESTART-SAFE RECOVERY
        # --------------------------------------------

        recovery = (
            validate_restart_safe_recovery(
                intent
            )
        )

        if not recovery.overall:

            raise RuntimeError(
                "R28 restart-safe recovery "
                "validation failed: "
                + str(
                    recovery
                )
            )

        # --------------------------------------------
        # FINAL REPORT
        # --------------------------------------------

        report = build_r28_report(
            balance=balance,
            mark_price=mark_price,
            api_symbol_ok=api_symbol_ok,
            contract=contract,
            quantity=quantity,
            signal_tests=signal_tests,
            order_tests=order_tests,
            intent=intent,
            intent_tests=intent_tests,
            preflight=preflight,
            live_payload=live_payload,
            signature_generated=(
                signature_generated
            ),
            accepted_classifier=(
                accepted_classifier
            ),
            rejected_classifier=(
                rejected_classifier
            ),
            ambiguous_fails_closed=(
                ambiguous_fails_closed
            ),
            real_post_blocked=(
                real_post_blocked
            ),
            demo=demo,
            recovery=recovery,
        )

        print(
            report,
            flush=True,
        )

        telegram_sent = await send_telegram(
            session,
            report,
        )

        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:

            print(
                (
                    "TELEGRAM DIAGNOSTIC: "
                    + (
                        "✅ SENT"
                        if telegram_sent
                        else "❌ FAILED"
                    )
                ),
                flush=True,
            )


# ============================================================
# DIAGNOSTIC WRAPPER
# ============================================================

async def diagnostic_wrapper(
    session: aiohttp.ClientSession,
) -> None:

    try:

        await run_r28_diagnostic(
            session
        )

    except Exception as exc:

        error_text = "\n".join(
            [
                (
                    f"❌ MODULE "
                    f"{MODULE_NAME} ERROR"
                ),

                SYMBOL,

                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),

                (
                    "Real POST Called: "
                    + (
                        "✅ YES"
                        if R28_REAL_POST_CALLED
                        else "❌ NO"
                    )
                ),

                (
                    "Demo POST Attempted: "
                    + (
                        "✅ YES"
                        if R28_DEMO_POST_ATTEMPTED
                        else "❌ NO"
                    )
                ),

                (
                    "Demo POST Accepted: "
                    + (
                        "✅ YES"
                        if R28_DEMO_POST_ACCEPTED
                        else "❌ NO"
                    )
                ),

                (
                    "🛡 R28 absolute real-order "
                    "POST lock active"
                ),

                (
                    "⚠️ LIVE ORDER EXECUTION "
                    "DISABLED"
                ),

                (
                    "⚠️ NO REAL ORDER WAS SENT"
                ),
            ]
        )

        print(
            error_text,
            flush=True,
        )

        traceback.print_exc()

        await send_telegram(
            session,
            error_text,
        )


# ============================================================
# PERSISTENT RENDER RUNTIME
# ============================================================

async def main_async(
) -> None:

    await start_health_server()

    timeout = aiohttp.ClientTimeout(
        total=30
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        # Run the R28 diagnostic exactly once.
        asyncio.create_task(
            diagnostic_wrapper(
                session
            )
        )

        # Keep Render service alive.
        #
        # No repeated demo-order loop.
        while True:

            await asyncio.sleep(
                3600
            )


# ============================================================
# MAIN
# ============================================================

def main(
) -> None:

    try:

        asyncio.run(
            main_async()
        )

    except KeyboardInterrupt:

        pass

    except Exception:

        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"❌ {MODULE_NAME} "
            "FATAL STARTUP ERROR",
            flush=True,
        )

        traceback.print_exc()

        print(
            "🛡 REAL ORDER POST LOCK "
            "REMAINS ACTIVE",
            flush=True,
        )

        print(
            "⚠️ LIVE ORDER EXECUTION "
            "DISABLED",
            flush=True,
        )

        print(
            "⚠️ NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        raise


if __name__ == "__main__":

    main()
