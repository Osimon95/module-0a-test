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
