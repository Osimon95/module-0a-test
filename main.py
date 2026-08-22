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
