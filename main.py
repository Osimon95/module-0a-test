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

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = (
            text
            .rstrip("0")
            .rstrip(".")
        )

    return text or "0"


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

ORDER_TERMINAL = {
    "FILLED",
    "CANCELED",
    "REJECTED",
    "EXPIRED",
}

ORDER_ALLOWED = {
    "NEW": {
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "REJECTED",
        "EXPIRED",
    },
    "PARTIALLY_FILLED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "EXPIRED",
    },
}


class OrderStateMachine:

    def __init__(
        self,
    ) -> None:

        self.state = "NEW"

        self.executed_qty = Decimal(
            "0"
        )

        self.seen_events: Set[
            str
        ] = set()


    def apply(
        self,
        status: str,
        executed_qty: Decimal,
        event_id: str,
    ) -> Tuple[
        bool,
        Decimal,
    ]:

        status = status.upper()

        if event_id in self.seen_events:

            return (
                False,
                Decimal("0"),
            )

        self.seen_events.add(
            event_id
        )

        if self.state in ORDER_TERMINAL:

            if status != self.state:

                return (
                    False,
                    Decimal("0"),
                )

            return (
                False,
                Decimal("0"),
            )

        if (
            status != self.state
            and status
            not in ORDER_ALLOWED.get(
                self.state,
                set(),
            )
        ):

            return (
                False,
                Decimal("0"),
            )

        delta = max(
            Decimal("0"),
            executed_qty
            - self.executed_qty,
        )

        self.executed_qty = max(
            self.executed_qty,
            executed_qty,
        )

        self.state = status

        return (
            True,
            delta,
        )


INTENT_TERMINAL = {
    "RECONCILED",
    "REJECTED",
    "EXPIRED",
    "FAILED",
}

INTENT_ALLOWED = {

    "NEW": {
        "PREFLIGHT",
        "REJECTED",
        "EXPIRED",
    },

    "PREFLIGHT": {
        "READY",
        "REJECTED",
        "EXPIRED",
    },

    "READY": {
        "TRANSMITTED",
        "REJECTED",
        "EXPIRED",
    },

    "TRANSMITTED": {
        "ACKNOWLEDGED",
        "REJECTED",
        "FAILED",
    },

    "ACKNOWLEDGED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "FAILED",
    },

    "PARTIALLY_FILLED": {
        "PARTIALLY_FILLED",
        "FILLED",
        "FAILED",
    },

    "FILLED": {
        "RECONCILED",
        "FAILED",
    },
}


def transition_intent(
    intent: ExecutionIntent,
    new_state: str,
) -> bool:

    new_state = (
        new_state
        .upper()
    )

    old = (
        intent.state
        .upper()
    )

    if old in INTENT_TERMINAL:
        return False

    if (
        new_state
        not in INTENT_ALLOWED.get(
            old,
            set(),
        )
    ):
        return False

    intent.state = new_state

    intent.updated_ms = int(
        time.time()
        * 1000
    )

    return True


# ============================================================
# R28 JOURNAL / RESTART RECOVERY
# ============================================================

class IntentJournal:

    def __init__(
        self,
        path: Path,
    ) -> None:

        self.path = path


    def save(
        self,
        intent: ExecutionIntent,
    ) -> None:

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp = self.path.with_suffix(
            self.path.suffix
            + ".tmp"
        )

        data = asdict(
            intent
        )

        raw = json.dumps(
            data,
            separators=(
                ",",
                ":",
            ),
            sort_keys=True,
        )

        tmp.write_text(
            raw,
            encoding="utf-8",
        )

        os.replace(
            tmp,
            self.path,
        )


    def load(
        self,
    ) -> Optional[
        ExecutionIntent
    ]:

        if not self.path.exists():
            return None

        raw = self.path.read_text(
            encoding="utf-8",
        )

        data = json.loads(
            raw
        )

        return ExecutionIntent(
            **data
        )


    def clear(
        self,
    ) -> None:

        try:

            self.path.unlink()

        except FileNotFoundError:

            pass


def recovery_decision(
    intent: ExecutionIntent,
    now_ms: int,
) -> str:

    if intent.state in INTENT_TERMINAL:

        return "DO_NOT_TRANSMIT"

    if (
        now_ms
        > intent.expires_ms
        and intent.state
        in {
            "NEW",
            "PREFLIGHT",
            "READY",
        }
    ):

        return "EXPIRE"

    if intent.state in {
        "TRANSMITTED",
        "ACKNOWLEDGED",
        "PARTIALLY_FILLED",
        "FILLED",
    }:

        return "RECONCILE_ONLY"

    return "PREFLIGHT_ONLY"


# ============================================================
# HTTP CLIENT
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
