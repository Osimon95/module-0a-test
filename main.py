import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import time
import traceback
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_DOWN
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
    default_demo_symbol(SYMBOL)
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================
#
# R28 IS STILL PRE-LIVE.
#
# R28 adds a SHADOW EXECUTION COMMIT GATE:
#
# signal
#   -> intent
#   -> preflight
#   -> ready
#   -> shadow commit
#   -> reconcile
#
# The shadow commit proves that the exact live request is ready,
# fingerprinted, idempotent and locally signed.
#
# IT NEVER TRANSMITS A REAL /capi/v3/order POST.
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R28_REAL_POST_CALLED = False

REAL_ORDER_PATH = "/capi/v3/order"

DEMO_ORDER_PATH = "/capi/v3/sim/order"

DEMO_HISTORY_PATH = (
    "/capi/v3/sim/order/history"
)

DEMO_POSITION_PATH = (
    "/capi/v3/sim/position/allPosition"
)

RUN_DEMO_ORDER_TEST = (
    os.getenv(
        "RUN_DEMO_ORDER_TEST",
        "true"
    ).lower()
    == "true"
)

DEMO_FILL_MODE = os.getenv(
    "DEMO_FILL_MODE",
    "AUTO"
).strip().upper()


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(
    os.getenv(
        "ENTRY_PERCENT",
        "5"
    )
)

LEVERAGE = int(
    os.getenv(
        "LEVERAGE",
        "100"
    )
)

MAX_CONFIG_LEVERAGE = int(
    os.getenv(
        "MAX_CONFIG_LEVERAGE",
        "100"
    )
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED"
).strip().upper()


MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
        "1"
    )
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_SIZE_PERCENT",
        "5"
    )
)


MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3"
    )
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5"
    )
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3"
    )
)


MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2"
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35"
    )
)


TP1_SHARE = Decimal("20")
TP2_SHARE = Decimal("20")
TP3_SHARE = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1")

TRAILING_DISTANCE_PERCENT = Decimal("0.2")


SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120"
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300"
    )
)


ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# ENVIRONMENT
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    ""
).strip()

WEEX_SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    ""
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    ""
).strip()


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
).strip()


PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)


# ============================================================
# HELPERS
# ============================================================

D0 = Decimal("0")
D1 = Decimal("1")
D100 = Decimal("100")


def D(
    value: Any,
    default: str = "0",
) -> Decimal:

    try:
        if value is None or value == "":
            return Decimal(default)

        return Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal(default)


def yesno(value: bool) -> str:

    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def bool_word(value: bool) -> str:

    return (
        "✅ ACTIVE"
        if value
        else "❌ DISABLED"
    )


def fmt_decimal(
    value: Decimal,
) -> str:

    s = format(value, "f")

    if "." in s:
        s = (
            s.rstrip("0")
            .rstrip(".")
        )

    return s or "0"


def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    if step <= 0:
        return value

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_step_from_precision(
    precision: int,
) -> Decimal:

    if precision <= 0:
        return Decimal("1")

    return Decimal("1").scaleb(
        -precision
    )


def stable_json(
    data: Dict[str, Any],
) -> str:

    return json.dumps(
        data,
        separators=(",", ":"),
        sort_keys=True,
    )


def raw_json(
    data: Dict[str, Any],
) -> str:

    return json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def make_client_order_id(
    prefix: str,
    seed: str,
) -> str:

    digest = hashlib.sha256(
        seed.encode("utf-8")
    ).hexdigest()[:20]

    value = (
        f"{prefix}-{digest}"
    )

    return value[:36]


def client_id_valid(
    value: str,
) -> bool:

    return bool(
        re.fullmatch(
            r"[\.A-Z\:/a-z0-9_-]{1,36}",
            value or "",
        )
    )


def env_credentials_present() -> bool:

    return bool(
        WEEX_API_KEY
        and WEEX_SECRET_KEY
        and WEEX_PASSPHRASE
    )


def validate_credentials() -> None:

    missing = []

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
            "Missing WEEX credentials: "
            + ", ".join(missing)
        )


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class ContractInfo:

    symbol: str

    min_order: Decimal

    quantity_precision: int
    quantity_step: Decimal

    price_precision: int
    price_step: Decimal

    contract_value: Decimal

    min_leverage: int
    max_leverage: int


@dataclass
class Signal:

    signal_id: str
    direction: str
    created_at: float


@dataclass
class ExecutionIntent:

    intent_id: str

    signal_id: str

    symbol: str

    side: str

    position_side: str

    quantity: Decimal

    leverage: int

    created_at: float

    client_order_id: str

    state: str = "NEW"

    history: List[str] = field(
        default_factory=lambda: [
            "NEW"
        ]
    )

    def transition(
        self,
        new_state: str,
    ) -> bool:

        allowed = {

            "NEW": {
                "PREFLIGHT",
                "REJECTED",
            },

            "PREFLIGHT": {
                "READY",
                "REJECTED",
            },

            "READY": {
                "SHADOW_COMMITTED",
                "REJECTED",
            },

            "SHADOW_COMMITTED": {
                "RECONCILED",
                "REJECTED",
            },

            "RECONCILED": set(),

            "REJECTED": set(),
        }

        if new_state in allowed.get(
            self.state,
            set(),
        ):

            self.state = new_state

            self.history.append(
                new_state
            )

            return True

        return False


@dataclass
class OrderStateMachine:

    state: str = "NONE"

    executed_qty: Decimal = D0

    seen_events: Set[str] = field(
        default_factory=set
    )

    def apply(
        self,
        event_id: str,
        status: str,
        cumulative_executed: Decimal,
    ) -> Tuple[bool, Decimal]:

        if event_id in self.seen_events:

            return (
                False,
                D0,
            )

        terminal = {
            "FILLED",
            "CANCELED",
            "CANCELLED",
            "REJECTED",
            "EXPIRED",
        }

        if self.state in terminal:

            return (
                False,
                D0,
            )

        self.seen_events.add(
            event_id
        )

        delta = max(
            D0,
            cumulative_executed
            - self.executed_qty,
        )

        self.executed_qty = max(
            self.executed_qty,
            cumulative_executed,
        )

        self.state = status

        return (
            True,
            delta,
        )


@dataclass
class ShadowCommit:

    endpoint: str

    payload: Dict[str, Any]

    body: str

    timestamp: str

    signature: str

    request_fingerprint: str

    intent_fingerprint: str

    commit_token: str

    real_post_blocked: bool


# ============================================================
# WEEX CLIENT
# ============================================================

class WeexClient:

    def __init__(
        self,
    ) -> None:

        self.session: Optional[
            aiohttp.ClientSession
        ] = None


    async def start(
        self,
    ) -> None:

        if (
            self.session is None
            or self.session.closed
        ):

            timeout = (
                aiohttp.ClientTimeout(
                    total=20
                )
            )

            self.session = (
                aiohttp.ClientSession(
                    timeout=timeout
                )
            )


    async def close(
        self,
    ) -> None:

        if (
            self.session
            and not self.session.closed
        ):

            await self.session.close()


    def _signature(
        self,
        timestamp: str,
        method: str,
        path: str,
        query: str = "",
        body: str = "",
    ) -> str:

        method = method.upper()

        prehash = (
            timestamp
            + method
            + path
        )

        if query:

            prehash += (
                "?"
                + query
            )

        prehash += body

        digest = hmac.new(
            WEEX_SECRET_KEY.encode(
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


    def signed_headers(
        self,
        method: str,
        path: str,
        query: str = "",
        body: str = "",
        timestamp: Optional[str] = None,
    ) -> Dict[str, str]:

        ts = (
            timestamp
            or str(
                int(
                    time.time()
                    * 1000
                )
            )
        )

        return {

            "ACCESS-KEY":
                WEEX_API_KEY,

            "ACCESS-SIGN":
                self._signature(
                    ts,
                    method,
                    path,
                    query,
                    body,
                ),

            "ACCESS-TIMESTAMP":
                ts,

            "ACCESS-PASSPHRASE":
                WEEX_PASSPHRASE,

            "Content-Type":
                "application/json",

            "User-Agent":
                f"{MODULE_NAME}/1.0",
        }


    async def public_get(
        self,
        path: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Any:

        await self.start()

        assert (
            self.session
            is not None
        )

        async with (
            self.session.get(
                API_BASE_URL + path,
                params=params,
            )
        ) as resp:

            text = await resp.text()

            if resp.status >= 400:

                raise RuntimeError(
                    "WEEX PUBLIC GET "
                    f"HTTP {resp.status}: "
                    f"{text}"
                )

            try:
                return json.loads(
                    text
                )

            except json.JSONDecodeError:

                return text
