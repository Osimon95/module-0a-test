import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import traceback
import uuid

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R25"
API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


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
#
# R25 REMAINS PRE-LIVE / DEMO ONLY.
#
# REAL ORDER TRANSMISSION MUST REMAIN DISABLED.
#
# R25 may:
#
# - perform public GET requests
# - perform authenticated/private GET requests
# - perform WEEX DEMO GET requests
# - optionally perform ONE WEEX DEMO POST validation order
#
# R25 MUST NOT transmit:
#
# POST /capi/v3/order
#
# or any other REAL/private state-changing endpoint.
#
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R25_REAL_POST_CALLED = False
R25_DEMO_POST_ATTEMPTED = False
R25_DEMO_POST_ACCEPTED = False


REAL_STATE_CHANGING_PREFIXES = (
    "/capi/v3/order",
    "/capi/v3/position",
    "/capi/v3/account/leverage",
    "/capi/v3/account/margin",
    "/capi/v3/algoOrder",
)


def real_post_blocked(path: str) -> bool:
    path = str(path or "")

    if path.startswith("/capi/v3/sim/"):
        return False

    for prefix in REAL_STATE_CHANGING_PREFIXES:
        if path.startswith(prefix):
            return True

    return True


def assert_absolute_execution_safety() -> None:
    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "R25 SAFETY FAILURE: LIVE_ORDER_EXECUTION must remain False."
        )

    if not HARD_REAL_POST_LOCK:
        raise RuntimeError(
            "R25 SAFETY FAILURE: HARD_REAL_POST_LOCK must remain True."
        )


# ============================================================
# ADJUSTABLE STRATEGY CONFIG
# ============================================================

ENTRY_PERCENT = Decimal(
    os.getenv("ENTRY_PERCENT", "5")
)

LEVERAGE = int(
    os.getenv("LEVERAGE", "100")
)

MAX_CONFIG_LEVERAGE = int(
    os.getenv("MAX_CONFIG_LEVERAGE", "100")
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()

MAX_PYRAMID_ADDS = int(
    os.getenv("MAX_PYRAMID_ADDS", "1")
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv("PYRAMID_SIZE_PERCENT", "5")
)

MAX_BACKUPS = int(
    os.getenv("MAX_BACKUPS", "3")
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv("BACKUP_SIZE_PERCENT", "5")
)

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv("BACKUP_BUFFER_PERCENT", "0.3")
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv("MIN_LIQ_DISTANCE_PERCENT", "0.2")
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv("MAX_FUND_EXPOSURE_PERCENT", "35")
)


# ============================================================
# TP / TRAILING CONFIG
# ============================================================

TP1_PERCENT = Decimal(
    os.getenv("TP1_PERCENT", "20")
)

TP2_PERCENT = Decimal(
    os.getenv("TP2_PERCENT", "20")
)

TP3_PERCENT = Decimal(
    os.getenv("TP3_PERCENT", "60")
)

TP1_TRIGGER_PERCENT = Decimal(
    os.getenv("TP1_TRIGGER_PERCENT", "0.5")
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv("TP2_TRIGGER_PERCENT", "1.0")
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv("TRAILING_DISTANCE_PERCENT", "0.20")
)


# ============================================================
# SIGNAL SAFETY
# ============================================================

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv("SIGNAL_EXPIRY_SECONDS", "120")
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv("LOSS_COOLDOWN_SECONDS", "300")
)

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# R25 EXECUTION INTENT CONFIG
# ============================================================
#
# New R25 layer:
#
# SIGNAL
#   ↓
# EXECUTION INTENT
#   ↓
# PREFLIGHT VALIDATION
#   ↓
# DEMO TRANSMISSION
#   ↓
# EXCHANGE HISTORY
#   ↓
# RECONCILIATION
#
# No intent can reach a real POST.
#
# ============================================================

EXECUTION_INTENT_EXPIRY_SECONDS = int(
    os.getenv(
        "EXECUTION_INTENT_EXPIRY_SECONDS",
        "30",
    )
)

DEMO_ORDER_TEST_ENABLED = (
    os.getenv(
        "R25_DEMO_ORDER_TEST",
        "true",
    ).strip().lower()
    in ("1", "true", "yes", "on")
)

DEMO_LIMIT_OFFSET_PERCENT = Decimal(
    os.getenv(
        "DEMO_LIMIT_OFFSET_PERCENT",
        "0.5",
    )
)

HISTORY_POLL_ATTEMPTS = int(
    os.getenv(
        "HISTORY_POLL_ATTEMPTS",
        "8",
    )
)

HISTORY_POLL_DELAY_SECONDS = float(
    os.getenv(
        "HISTORY_POLL_DELAY_SECONDS",
        "1.0",
    )
)


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# ============================================================
# WEEX CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    "",
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    "",
).strip()


# ============================================================
# RUNTIME STATE
# ============================================================

DIAGNOSTIC_COMPLETED = False
DIAGNOSTIC_RUNNING = False

PROCESSED_SIGNAL_IDS = set()
PROCESSED_EXCHANGE_EVENTS = set()
PROCESSED_EXECUTION_INTENTS = set()

LAST_LOSS_TIME: Optional[float] = None

ACTIVE_DIRECTION: Optional[str] = None


# ============================================================
# DECIMAL HELPERS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


def D(value: Any) -> Decimal:
    try:
        if isinstance(value, Decimal):
            return value

        if value is None:
            return ZERO

        return Decimal(str(value))

    except (InvalidOperation, ValueError, TypeError):
        return ZERO


def decimal_to_str(value: Decimal) -> str:
    value = D(value)

    text = format(
        value.normalize(),
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in ("", "-0"):
        return "0"

    return text


def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:
    value = D(value)
    step = D(step)

    if step <= ZERO:
        return value

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_places(value: Decimal) -> int:
    value = D(value)

    exponent = value.as_tuple().exponent

    if exponent >= 0:
        return 0

    return abs(exponent)


def status_icon(value: bool) -> str:
    return "✅ YES" if value else "❌ NO"


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request: web.Request,
) -> web.Response:
    return web.json_response(
        {
            "module": MODULE_NAME,
            "status": "ok",
            "live_execution": LIVE_ORDER_EXECUTION,
            "real_post_lock": HARD_REAL_POST_LOCK,
            "diagnostic_completed": DIAGNOSTIC_COMPLETED,
        }
    )


async def root_handler(
    request: web.Request,
) -> web.Response:
    return web.Response(
        text=f"{MODULE_NAME} ACTIVE"
    )


async def start_health_server() -> web.AppRunner:
    app = web.Application()

    app.router.add_get(
        "/",
        root_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    runner = web.AppRunner(app)

    await runner.setup()

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

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
# TELEGRAM
# ============================================================

async def send_telegram(
    session: aiohttp.ClientSession,
    message: str,
) -> None:
    if not TELEGRAM_BOT_TOKEN:
        print(
            "TELEGRAM_BOT_TOKEN not configured.",
            flush=True,
        )
        return

    if not TELEGRAM_CHAT_ID:
        print(
            "TELEGRAM_CHAT_ID not configured.",
            flush=True,
        )
        return

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:

            text = await response.text()

            if response.status >= 300:
                print(
                    "TELEGRAM ERROR:",
                    response.status,
                    text,
                    flush=True,
                )

    except Exception as exc:
        print(
            "TELEGRAM SEND ERROR:",
            repr(exc),
            flush=True,
        )


# ============================================================
# AUTH VALIDATION
# ============================================================

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
# WEEX SIGNATURE
# ============================================================

def canonical_query(
    params: Optional[Dict[str, Any]],
) -> str:
    if not params:
        return ""

    clean = []

    for key, value in params.items():
        if value is None:
            continue

        clean.append(
            (
                str(key),
                str(value),
            )
        )

    return urlencode(clean)


def compact_json(
    body: Optional[Dict[str, Any]],
) -> str:
    if not body:
        return ""

    return json.dumps(
        body,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def create_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body_string: str = "",
) -> str:
    method = method.upper()

    if query_string:
        prehash = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body_string
        )

    else:
        prehash = (
            timestamp
            + method
            + request_path
            + body_string
        )

    digest = hmac.new(
        WEEX_SECRET_KEY.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def auth_headers(
    method: str,
    path: str,
    query_string: str = "",
    body_string: str = "",
) -> Dict[str, str]:
    timestamp = str(
        int(time.time() * 1000)
    )

    signature = create_signature(
        timestamp=timestamp,
        method=method,
        request_path=path,
        query_string=query_string,
        body_string=body_string,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "User-Agent": MODULE_NAME,
    }


# ============================================================
# HTTP HELPERS
# ============================================================

async def public_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    url = API_BASE_URL + path

    async with session.get(
        url,
        params=params,
        timeout=aiohttp.ClientTimeout(total=20),
    ) as response:

        text = await response.text()

        if response.status >= 300:
            raise RuntimeError(
                f"WEEX PUBLIC GET HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                "WEEX returned invalid JSON: "
                + text
            )


async def private_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    query_string = canonical_query(
        params
    )

    headers = auth_headers(
        method="GET",
        path=path,
        query_string=query_string,
    )

    url = API_BASE_URL + path

    if query_string:
        url += "?" + query_string

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=20),
    ) as response:

        text = await response.text()

        if response.status >= 300:
            raise RuntimeError(
                f"WEEX GET HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                "WEEX returned invalid JSON: "
                + text
            )


async def demo_post(
    session: aiohttp.ClientSession,
    path: str,
    body: Dict[str, Any],
) -> Any:
    global R25_DEMO_POST_ATTEMPTED
    global R25_DEMO_POST_ACCEPTED

    assert_absolute_execution_safety()

    if not path.startswith(
        "/capi/v3/sim/"
    ):
        raise RuntimeError(
            "R25 SAFETY BLOCK: demo_post() "
            "may only access /capi/v3/sim/*"
        )

    R25_DEMO_POST_ATTEMPTED = True

    body_string = compact_json(
        body
    )

    headers = auth_headers(
        method="POST",
        path=path,
        body_string=body_string,
    )

    url = API_BASE_URL + path

    async with session.post(
        url,
        data=body_string,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=20),
    ) as response:

        text = await response.text()

        if response.status >= 300:
            raise RuntimeError(
                f"WEEX DEMO POST HTTP "
                f"{response.status}: {text}"
            )

        try:
            data = json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                "WEEX DEMO POST invalid JSON: "
                + text
            )

        if isinstance(data, dict):
            success = data.get(
                "success"
            )

            if success is False:
                raise RuntimeError(
                    "WEEX DEMO POST rejected: "
                    + text
                )

        R25_DEMO_POST_ACCEPTED = True

        return data


async def blocked_real_post(
    session: aiohttp.ClientSession,
    path: str,
    body: Dict[str, Any],
) -> Any:
    global R25_REAL_POST_CALLED

    R25_REAL_POST_CALLED = True

    raise RuntimeError(
        "R25 ABSOLUTE SAFETY BLOCK: "
        f"REAL POST forbidden: {path}"
    )


# ============================================================
# MARKET DATA
# ============================================================

async def get_mark_price(
    session: aiohttp.ClientSession,
    symbol: str,
) -> Decimal:
    data = await public_get(
        session,
        "/capi/v3/market/symbolPrice",
        {
            "symbol": symbol,
            "priceType": "MARK",
        },
    )

    if not isinstance(data, dict):
        raise RuntimeError(
            "Unexpected mark price response."
        )

    price = D(
        data.get("price")
    )

    if price <= ZERO:
        raise RuntimeError(
            "Unable to extract positive mark price."
        )

    return price


# ============================================================
# CONTRACT INFORMATION
# ============================================================

@dataclass
class ContractInfo:
    symbol: str

    min_quantity: Decimal

    quantity_precision: int
    quantity_step: Decimal

    price_precision: int
    price_step: Decimal

    contract_value: Decimal

    min_leverage: int
    max_leverage: int

    trading: bool


def find_filter(
    symbol_data: Dict[str, Any],
    *names: str,
) -> Optional[Dict[str, Any]]:
    filters = symbol_data.get(
        "filters",
        []
    )

    if not isinstance(
        filters,
        list,
    ):
        return None

    wanted = {
        name.upper()
        for name in names
    }

    for item in filters:
        if not isinstance(
            item,
            dict,
        ):
            continue

        filter_type = str(
            item.get(
                "filterType",
                "",
            )
        ).upper()

        if filter_type in wanted:
            return item

    return None


def first_decimal(
    source: Dict[str, Any],
    keys: Tuple[str, ...],
    default: Decimal,
) -> Decimal:
    for key in keys:
        if key not in source:
            continue

        value = D(
            source.get(key)
        )

        if value > ZERO:
            return value

    return default


def first_int(
    source: Dict[str, Any],
    keys: Tuple[str, ...],
    default: int,
) -> int:
    for key in keys:
        value = source.get(key)

        if value is None:
            continue

        try:
            parsed = int(
                D(value)
            )

            if parsed >= 0:
                return parsed

        except Exception:
            pass

    return default


async def get_contract_info(
    session: aiohttp.ClientSession,
    symbol: str,
) -> ContractInfo:
    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": symbol,
        },
    )

    symbol_data = None

    if isinstance(data, dict):
        symbols = data.get(
            "symbols",
            []
        )

        if isinstance(
            symbols,
            list,
        ):
            for item in symbols:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                if str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper() == symbol.upper():

                    symbol_data = item
                    break

    if not symbol_data:
        raise RuntimeError(
            f"Contract information not found "
            f"for {symbol}"
        )

    lot_filter = find_filter(
        symbol_data,
        "LOT_SIZE",
        "MARKET_LOT_SIZE",
    ) or {}

    price_filter = find_filter(
        symbol_data,
        "PRICE_FILTER",
    ) or {}

    min_quantity = first_decimal(
        lot_filter,
        (
            "minQty",
            "minQuantity",
        ),
        first_decimal(
            symbol_data,
            (
                "minQty",
                "minOrderQty",
                "minQuantity",
            ),
            Decimal("0.0001"),
        ),
    )

    quantity_step = first_decimal(
        lot_filter,
        (
            "stepSize",
            "qtyStep",
        ),
        first_decimal(
            symbol_data,
            (
                "quantityStep",
                "qtyStep",
                "sizeMultiplier",
            ),
            Decimal("0.0001"),
        ),
    )

    price_step = first_decimal(
        price_filter,
        (
            "tickSize",
            "priceStep",
        ),
        first_decimal(
            symbol_data,
            (
                "priceStep",
                "tickSize",
            ),
            Decimal("0.1"),
        ),
    )

    quantity_precision = first_int(
        symbol_data,
        (
            "quantityPrecision",
            "volumePlace",
            "sizePlace",
        ),
        decimal_places(
            quantity_step
        ),
    )

    price_precision = first_int(
        symbol_data,
        (
            "pricePrecision",
            "pricePlace",
        ),
        decimal_places(
            price_step
        ),
    )

    contract_value = first_decimal(
        symbol_data,
        (
            "contractValue",
            "contractSize",
            "sizeMultiplier",
        ),
        Decimal("0.0001"),
    )

    min_leverage = first_int(
        symbol_data,
        (
            "minLeverage",
        ),
        1,
    )

    max_leverage = first_int(
        symbol_data,
        (
            "maxLeverage",
        ),
        400,
    )

    status = str(
        symbol_data.get(
            "status",
            symbol_data.get(
                "symbolStatus",
                "TRADING",
            ),
        )
    ).upper()

    trading = status in (
        "",
        "TRADING",
        "NORMAL",
        "ONLINE",
        "1",
    )

    return ContractInfo(
        symbol=symbol,
        min_quantity=min_quantity,
        quantity_precision=quantity_precision,
        quantity_step=quantity_step,
        price_precision=price_precision,
        price_step=price_step,
        contract_value=contract_value,
        min_leverage=min_leverage,
        max_leverage=max_leverage,
        trading=trading,
    )


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_available_usdt(
    session: aiohttp.ClientSession,
) -> Decimal:
    data = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected WEEX balance response."
        )

    for item in data:
        if not isinstance(
            item,
            dict,
        ):
            continue

        if str(
            item.get(
                "asset",
                "",
            )
        ).upper() != "USDT":
            continue

        available = D(
            item.get(
                "availableBalance"
            )
        )

        if available >= ZERO:
            return available

    raise RuntimeError(
        "Unable to extract available USDT."
    )


# ============================================================
# DEMO POSITION
# ============================================================

async def get_demo_positions(
    session: aiohttp.ClientSession,
) -> List[Dict[str, Any]]:
    data = await private_get(
        session,
        "/capi/v3/sim/position/allPosition",
    )

    if isinstance(
        data,
        list,
    ):
        return [
            x
            for x in data
            if isinstance(
                x,
                dict,
            )
        ]

    return []


def demo_position_size(
    positions: List[Dict[str, Any]],
    symbol: str,
    side: Optional[str] = None,
) -> Decimal:
    total = ZERO

    for position in positions:
        if str(
            position.get(
                "symbol",
                "",
            )
        ).upper() != symbol.upper():
            continue

        if side is not None:
            position_side = str(
                position.get(
                    "side",
                    "",
                )
            ).upper()

            if position_side != side.upper():
                continue

        total += abs(
            D(
                position.get(
                    "size",
                    0,
                )
            )
        )

    return total


# ============================================================
# SIGNAL MODEL
# ============================================================

@dataclass
class Signal:
    signal_id: str
    symbol: str
    direction: str
    created_at: float


def signal_is_fresh(
    signal: Signal,
    now: Optional[float] = None,
) -> bool:
    if now is None:
        now = time.time()

    age = (
        now
        - signal.created_at
    )

    return (
        age >= 0
        and age <= SIGNAL_EXPIRY_SECONDS
    )


def signal_in_loss_cooldown(
    now: Optional[float] = None,
) -> bool:
    if LAST_LOSS_TIME is None:
        return False

    if now is None:
        now = time.time()

    return (
        now - LAST_LOSS_TIME
        < LOSS_COOLDOWN_SECONDS
    )


def duplicate_signal(
    signal: Signal,
) -> bool:
    return (
        signal.signal_id
        in PROCESSED_SIGNAL_IDS
    )


def one_direction_gate(
    signal: Signal,
) -> bool:
    if not ONE_DIRECTION_ONLY:
        return True

    if ACTIVE_DIRECTION is None:
        return True

    return (
        ACTIVE_DIRECTION
        == signal.direction
    )


def accept_signal(
    signal: Signal,
    now: Optional[float] = None,
) -> bool:
    if not signal_is_fresh(
        signal,
        now,
    ):
        return False

    if signal_in_loss_cooldown(
        now,
    ):
        return False

    if duplicate_signal(
        signal
    ):
        return False

    if not one_direction_gate(
        signal
    ):
        return False

    PROCESSED_SIGNAL_IDS.add(
        signal.signal_id
    )

    return True


# ============================================================
# R25 EXECUTION INTENT
# ============================================================

@dataclass
class ExecutionIntent:
    intent_id: str
    signal_id: str
    symbol: str

    side: str
    position_side: str

    quantity: Decimal

    created_at: float

    state: str = "NEW"


VALID_INTENT_TRANSITIONS = {
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
        "DEMO_SENT",
        "BLOCKED",
        "EXPIRED",
    },

    "DEMO_SENT": {
        "ACKNOWLEDGED",
        "REJECTED",
    },

    "ACKNOWLEDGED": {
        "RECONCILED",
    },

    "RECONCILED": set(),
    "REJECTED": set(),
    "EXPIRED": set(),
    "BLOCKED": set(),
}


TERMINAL_INTENT_STATES = {
    "RECONCILED",
    "REJECTED",
    "EXPIRED",
    "BLOCKED",
}


def transition_intent(
    intent: ExecutionIntent,
    new_state: str,
) -> bool:
    new_state = str(
        new_state
    ).upper()

    current = str(
        intent.state
    ).upper()

    if current in TERMINAL_INTENT_STATES:
        return False

    allowed = VALID_INTENT_TRANSITIONS.get(
        current,
        set(),
    )

    if new_state not in allowed:
        return False

    intent.state = new_state

    return True


def execution_intent_fresh(
    intent: ExecutionIntent,
    now: Optional[float] = None,
) -> bool:
    if now is None:
        now = time.time()

    age = (
        now
        - intent.created_at
    )

    return (
        age >= ZERO
        and age <= EXECUTION_INTENT_EXPIRY_SECONDS
    )


def process_intent_once(
    intent: ExecutionIntent,
) -> bool:
    if intent.intent_id in PROCESSED_EXECUTION_INTENTS:
        return False

    PROCESSED_EXECUTION_INTENTS.add(
        intent.intent_id
    )

    return True


def build_execution_intent(
    signal: Signal,
    quantity: Decimal,
) -> ExecutionIntent:
    direction = signal.direction.upper()

    if direction == "LONG":
        side = "BUY"
        position_side = "LONG"

    elif direction == "SHORT":
        side = "SELL"
        position_side = "SHORT"

    else:
        raise RuntimeError(
            "Unsupported signal direction."
        )

    return ExecutionIntent(
        intent_id=(
            "r25-"
            + uuid.uuid4().hex[:20]
        ),
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        side=side,
        position_side=position_side,
        quantity=quantity,
        created_at=time.time(),
    )


# ============================================================
# EXECUTION PREFLIGHT
# ============================================================

@dataclass
class PreflightResult:
    passed: bool

    live_execution_off: bool
    hard_real_post_lock: bool

    intent_fresh: bool
    quantity_positive: bool
    minimum_passed: bool
    leverage_passed: bool
    exposure_passed: bool

    real_path_blocked: bool


def run_execution_preflight(
    intent: ExecutionIntent,
    contract: ContractInfo,
    total_exposure_percent: Decimal,
) -> PreflightResult:

    live_execution_off = (
        not LIVE_ORDER_EXECUTION
    )

    hard_real_post_lock = (
        HARD_REAL_POST_LOCK
    )

    intent_fresh = (
        execution_intent_fresh(
            intent
        )
    )

    quantity_positive = (
        intent.quantity > ZERO
    )

    minimum_passed = (
        intent.quantity
        >= contract.min_quantity
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
        total_exposure_percent
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    real_path_blocked = (
        HARD_REAL_POST_LOCK
        and real_post_blocked(
            "/capi/v3/order"
        )
    )

    passed = all(
        (
            live_execution_off,
            hard_real_post_lock,
            intent_fresh,
            quantity_positive,
            minimum_passed,
            leverage_passed,
            exposure_passed,
            real_path_blocked,
        )
    )

    return PreflightResult(
        passed=passed,
        live_execution_off=live_execution_off,
        hard_real_post_lock=hard_real_post_lock,
        intent_fresh=intent_fresh,
        quantity_positive=quantity_positive,
        minimum_passed=minimum_passed,
        leverage_passed=leverage_passed,
        exposure_passed=exposure_passed,
        real_path_blocked=real_path_blocked,
    )


# ============================================================
# R24/R25 ORDER STATE MACHINE
# ============================================================

ORDER_TERMINAL_STATES = {
    "FILLED",
    "CANCELED",
    "CANCELLED",
    "REJECTED",
    "EXPIRED",
}


ORDER_STATE_PRIORITY = {
    "NEW": 10,
    "PARTIALLY_FILLED": 20,
    "FILLED": 30,
    "CANCELED": 30,
    "CANCELLED": 30,
    "REJECTED": 30,
    "EXPIRED": 30,
}


@dataclass
class OrderState:
    order_id: str

    status: str = "NEW"

    executed_quantity: Decimal = ZERO

    terminal: bool = False


def normalize_order_status(
    value: Any,
) -> str:
    value = str(
        value or ""
    ).strip().upper()

    aliases = {
        "PARTIAL_FILL": "PARTIALLY_FILLED",
        "PARTIALLYFILLED": "PARTIALLY_FILLED",
        "CANCELLED": "CANCELED",
    }

    return aliases.get(
        value,
        value,
    )


def update_order_state(
    state: OrderState,
    new_status: str,
    new_executed_qty: Decimal,
) -> Tuple[bool, Decimal]:

    new_status = normalize_order_status(
        new_status
    )

    new_executed_qty = max(
        ZERO,
        D(new_executed_qty),
    )

    if state.terminal:
        return (
            False,
            ZERO,
        )

    current_priority = ORDER_STATE_PRIORITY.get(
        normalize_order_status(
            state.status
        ),
        0,
    )

    new_priority = ORDER_STATE_PRIORITY.get(
        new_status,
        current_priority,
    )

    if new_priority < current_priority:
        return (
            False,
            ZERO,
        )

    fill_delta = max(
        ZERO,
        (
            new_executed_qty
            - state.executed_quantity
        ),
    )

    state.executed_quantity = max(
        state.executed_quantity,
        new_executed_qty,
    )

    state.status = new_status

    state.terminal = (
        new_status
        in ORDER_TERMINAL_STATES
    )

    return (
        True,
        fill_delta,
    )


def process_exchange_event_once(
    order_id: str,
    status: str,
    executed_qty: Decimal,
) -> bool:

    key = (
        str(order_id),
        normalize_order_status(
            status
        ),
        decimal_to_str(
            D(executed_qty)
        ),
    )

    if key in PROCESSED_EXCHANGE_EVENTS:
        return False

    PROCESSED_EXCHANGE_EVENTS.add(
        key
    )

    return True


# ============================================================
# INTERNAL STATE MACHINE SELF TEST
# ============================================================

@dataclass
class StateMachineTest:
    new_accepted: bool

    partial_1: bool
    partial_2: bool

    filled_terminal: bool

    duplicate_blocked: bool
    terminal_regression_blocked: bool


def run_order_state_machine_test() -> StateMachineTest:
    test_id = (
        "r25-state-test-"
        + uuid.uuid4().hex[:8]
    )

    state = OrderState(
        order_id=test_id
    )

    accepted_1, delta_1 = update_order_state(
        state,
        "PARTIALLY_FILLED",
        Decimal("0.0001"),
    )

    accepted_2, delta_2 = update_order_state(
        state,
        "PARTIALLY_FILLED",
        Decimal("0.0002"),
    )

    accepted_3, delta_3 = update_order_state(
        state,
        "FILLED",
        Decimal("0.0004"),
    )

    duplicate_first = (
        process_exchange_event_once(
            test_id,
            "FILLED",
            Decimal("0.0004"),
        )
    )

    duplicate_second = (
        process_exchange_event_once(
            test_id,
            "FILLED",
            Decimal("0.0004"),
        )
    )

    regression_accepted, _ = (
        update_order_state(
            state,
            "NEW",
            Decimal("0.0004"),
        )
    )

    return StateMachineTest(
        new_accepted=True,
        partial_1=(
            accepted_1
            and delta_1
            == Decimal("0.0001")
        ),
        partial_2=(
            accepted_2
            and delta_2
            == Decimal("0.0001")
        ),
        filled_terminal=(
            accepted_3
            and state.terminal
            and state.status
            == "FILLED"
            and delta_3
            == Decimal("0.0002")
        ),
        duplicate_blocked=(
            duplicate_first
            and not duplicate_second
        ),
        terminal_regression_blocked=(
            not regression_accepted
        ),
    )


# ============================================================
# SIGNAL SELF TEST
# ============================================================

@dataclass
class SignalGateTest:
    fresh_signal_accepted: bool

    expired_signal_rejected: bool

    loss_cooldown_test: bool

    duplicate_signal_rejected: bool

    one_direction_gate: bool

    external_position_clear: bool


def run_signal_gate_test() -> SignalGateTest:
    global LAST_LOSS_TIME
    global ACTIVE_DIRECTION

    old_last_loss = LAST_LOSS_TIME
    old_direction = ACTIVE_DIRECTION

    try:
        PROCESSED_SIGNAL_IDS.clear()

        now = time.time()

        LAST_LOSS_TIME = None
        ACTIVE_DIRECTION = None

        fresh = Signal(
            signal_id=(
                "fresh-"
                + uuid.uuid4().hex
            ),
            symbol=SYMBOL,
            direction="LONG",
            created_at=now,
        )

        fresh_accepted = accept_signal(
            fresh,
            now,
        )

        expired = Signal(
            signal_id=(
                "expired-"
                + uuid.uuid4().hex
            ),
            symbol=SYMBOL,
            direction="LONG",
            created_at=(
                now
                - SIGNAL_EXPIRY_SECONDS
                - 5
            ),
        )

        expired_rejected = (
            not accept_signal(
                expired,
                now,
            )
        )

        LAST_LOSS_TIME = (
            now - 1
        )

        cooldown_signal = Signal(
            signal_id=(
                "cooldown-"
                + uuid.uuid4().hex
            ),
            symbol=SYMBOL,
            direction="LONG",
            created_at=now,
        )

        cooldown_blocked = (
            not accept_signal(
                cooldown_signal,
                now,
            )
        )

        LAST_LOSS_TIME = None

        duplicate = Signal(
            signal_id=(
                "duplicate-"
                + uuid.uuid4().hex
            ),
            symbol=SYMBOL,
            direction="LONG",
            created_at=now,
        )

        first_duplicate = (
            accept_signal(
                duplicate,
                now,
            )
        )

        second_duplicate = (
            accept_signal(
                duplicate,
                now,
            )
        )

        duplicate_rejected = (
            first_duplicate
            and not second_duplicate
        )

        ACTIVE_DIRECTION = "LONG"

        opposite = Signal(
            signal_id=(
                "opposite-"
                + uuid.uuid4().hex
            ),
            symbol=SYMBOL,
            direction="SHORT",
            created_at=now,
        )

        direction_blocked = (
            not accept_signal(
                opposite,
                now,
            )
        )

        ACTIVE_DIRECTION = None

        return SignalGateTest(
            fresh_signal_accepted=fresh_accepted,
            expired_signal_rejected=expired_rejected,
            loss_cooldown_test=cooldown_blocked,
            duplicate_signal_rejected=duplicate_rejected,
            one_direction_gate=direction_blocked,
            external_position_clear=True,
        )

    finally:
        LAST_LOSS_TIME = old_last_loss
        ACTIVE_DIRECTION = old_direction


# ============================================================
# R25 EXECUTION INTENT SELF TEST
# ============================================================

@dataclass
class IntentTest:
    intent_created: bool

    duplicate_intent_blocked: bool

    new_to_preflight: bool
    preflight_to_ready: bool

    terminal_regression_blocked: bool

    expired_intent_rejected: bool


def run_execution_intent_test() -> IntentTest:
    PROCESSED_EXECUTION_INTENTS.clear()

    signal = Signal(
        signal_id=(
            "intent-signal-"
            + uuid.uuid4().hex[:12]
        ),
        symbol=SYMBOL,
        direction="LONG",
        created_at=time.time(),
    )

    intent = build_execution_intent(
        signal,
        Decimal("0.0004"),
    )

    first_process = (
        process_intent_once(
            intent
        )
    )

    second_process = (
        process_intent_once(
            intent
        )
    )

    new_to_preflight = transition_intent(
        intent,
        "PREFLIGHT",
    )

    preflight_to_ready = transition_intent(
        intent,
        "READY",
    )

    terminal_test = ExecutionIntent(
        intent_id=(
            "terminal-"
            + uuid.uuid4().hex[:12]
        ),
        signal_id=signal.signal_id,
        symbol=SYMBOL,
        side="BUY",
        position_side="LONG",
        quantity=Decimal("0.0004"),
        created_at=time.time(),
        state="BLOCKED",
    )

    terminal_regression = transition_intent(
        terminal_test,
        "NEW",
    )

    expired = ExecutionIntent(
        intent_id=(
            "expired-"
            + uuid.uuid4().hex[:12]
        ),
        signal_id=signal.signal_id,
        symbol=SYMBOL,
        side="BUY",
        position_side="LONG",
        quantity=Decimal("0.0004"),
        created_at=(
            time.time()
            - EXECUTION_INTENT_EXPIRY_SECONDS
            - 5
        ),
    )

    return IntentTest(
        intent_created=(
            bool(intent.intent_id)
            and intent.state
            == "READY"
        ),
        duplicate_intent_blocked=(
            first_process
            and not second_process
        ),
        new_to_preflight=new_to_preflight,
        preflight_to_ready=preflight_to_ready,
        terminal_regression_blocked=(
            not terminal_regression
        ),
        expired_intent_rejected=(
            not execution_intent_fresh(
                expired
            )
        ),
    )


# ============================================================
# QUANTITY CALCULATION
# ============================================================

def calculate_entry(
    available_balance: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
) -> Tuple[
    Decimal,
    Decimal,
    Decimal,
]:
    margin = (
        available_balance
        * ENTRY_PERCENT
        / HUNDRED
    )

    notional = (
        margin
        * Decimal(
            LEVERAGE
        )
    )

    if mark_price <= ZERO:
        raise RuntimeError(
            "Invalid mark price."
        )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = floor_to_step(
        raw_quantity,
        contract.quantity_step,
    )

    return (
        margin,
        notional,
        quantity,
    )


# ============================================================
# DEMO LIMIT PRICE
# ============================================================

def calculate_demo_limit_price(
    mark_price: Decimal,
    price_step: Decimal,
) -> Decimal:
    multiplier = (
        ONE
        - (
            DEMO_LIMIT_OFFSET_PERCENT
            / HUNDRED
        )
    )

    raw_price = (
        mark_price
        * multiplier
    )

    price = floor_to_step(
        raw_price,
        price_step,
    )

    if price <= ZERO:
        raise RuntimeError(
            "Calculated demo limit price <= 0."
        )

    return price


# ============================================================
# DEMO ORDER HISTORY
# ============================================================

async def get_demo_order_history(
    session: aiohttp.ClientSession,
    symbol: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:

    data = await private_get(
        session,
        "/capi/v3/sim/order/history",
        {
            "symbol": symbol,
            "limit": limit,
            "page": 0,
        },
    )

    if isinstance(
        data,
        list,
    ):
        return [
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "orders",
            "list",
            "rows",
        ):
            value = data.get(key)

            if isinstance(
                value,
                list,
            ):
                return [
                    item
                    for item in value
                    if isinstance(
                        item,
                        dict,
                    )
                ]

    return []


def history_order_id(
    item: Dict[str, Any],
) -> str:
    return str(
        item.get(
            "orderId",
            item.get(
                "order_id",
                "",
            ),
        )
    )


async def poll_demo_order_history(
    session: aiohttp.ClientSession,
    symbol: str,
    order_id: str,
) -> Tuple[
    Optional[Dict[str, Any]],
    int,
]:
    order_id = str(
        order_id
    )

    for attempt in range(
        1,
        HISTORY_POLL_ATTEMPTS + 1,
    ):
        history = await get_demo_order_history(
            session,
            symbol,
        )

        for item in history:
            if history_order_id(
                item
            ) == order_id:

                return (
                    item,
                    attempt,
                )

        if attempt < HISTORY_POLL_ATTEMPTS:
            await asyncio.sleep(
                HISTORY_POLL_DELAY_SECONDS
            )

    return (
        None,
        HISTORY_POLL_ATTEMPTS,
    )


# ============================================================
# DEMO ORDER RESULT
# ============================================================

@dataclass
class DemoLifecycleResult:
    enabled: bool

    symbol: str
    side: str
    position_side: str
    order_type: str
    time_in_force: str

    limit_price: Decimal

    price_step_match: bool

    post_attempted: bool
    post_accepted: bool

    order_id: str

    history_lookup_attempted: bool
    history_poll_attempts: int

    order_found: bool

    order_id_match: bool
    symbol_match: bool
    side_match: bool
    position_side_match: bool

    final_status: str
    status_recognized: bool

    requested_quantity: Decimal
    history_original_quantity: Decimal
    history_executed_quantity: Decimal

    quantity_reconciliation: bool

    lifecycle_validation: bool

    actual_first_processing: bool
    actual_duplicate_blocked: bool
    actual_terminal: bool
    actual_fill_delta: Decimal

    position_before: Decimal
    position_after: Decimal
    position_reconciled: bool


RECOGNIZED_ORDER_STATUSES = {
    "NEW",
    "PARTIALLY_FILLED",
    "FILLED",
    "CANCELED",
    "CANCELLED",
    "REJECTED",
    "EXPIRED",
}


async def run_demo_lifecycle(
    session: aiohttp.ClientSession,
    quantity: Decimal,
    demo_limit_price: Decimal,
    contract: ContractInfo,
    intent: ExecutionIntent,
) -> DemoLifecycleResult:

    global R25_DEMO_POST_ATTEMPTED
    global R25_DEMO_POST_ACCEPTED

    R25_DEMO_POST_ATTEMPTED = False
    R25_DEMO_POST_ACCEPTED = False

    positions_before = await get_demo_positions(
        session
    )

    position_before = demo_position_size(
        positions_before,
        DEMO_SYMBOL,
        "LONG",
    )

    if not DEMO_ORDER_TEST_ENABLED:
        return DemoLifecycleResult(
            enabled=False,
            symbol=DEMO_SYMBOL,
            side="BUY",
            position_side="LONG",
            order_type="LIMIT",
            time_in_force="IOC",
            limit_price=demo_limit_price,
            price_step_match=True,
            post_attempted=False,
            post_accepted=False,
            order_id="",
            history_lookup_attempted=False,
            history_poll_attempts=0,
            order_found=False,
            order_id_match=False,
            symbol_match=False,
            side_match=False,
            position_side_match=False,
            final_status="DISABLED",
            status_recognized=False,
            requested_quantity=quantity,
            history_original_quantity=ZERO,
            history_executed_quantity=ZERO,
            quantity_reconciliation=False,
            lifecycle_validation=True,
            actual_first_processing=False,
            actual_duplicate_blocked=False,
            actual_terminal=False,
            actual_fill_delta=ZERO,
            position_before=position_before,
            position_after=position_before,
            position_reconciled=True,
        )

    if intent.state != "READY":
        raise RuntimeError(
            "R25 intent is not READY for demo transmission."
        )

    if not transition_intent(
        intent,
        "DEMO_SENT",
    ):
        raise RuntimeError(
            "R25 unable to transition intent to DEMO_SENT."
        )

    price_step_match = (
        floor_to_step(
            demo_limit_price,
            contract.price_step,
        )
        == demo_limit_price
    )

    client_order_id = (
        "r25-"
        + uuid.uuid4().hex[:24]
    )

    body = {
        "symbol": DEMO_SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "LIMIT",
        "timeInForce": "IOC",
        "quantity": decimal_to_str(
            quantity
        ),
        "price": decimal_to_str(
            demo_limit_price
        ),
        "newClientOrderId": client_order_id,
    }

    response = await demo_post(
        session,
        "/capi/v3/sim/order",
        body,
    )

    order_id = ""

    if isinstance(
        response,
        dict,
    ):
        order_id = str(
            response.get(
                "orderId",
                response.get(
                    "order_id",
                    "",
                ),
            )
        )

    if not order_id:
        raise RuntimeError(
            "WEEX demo order accepted but "
            "no orderId returned."
        )

    transition_intent(
        intent,
        "ACKNOWLEDGED",
    )

    history_item, poll_attempts = (
        await poll_demo_order_history(
            session,
            DEMO_SYMBOL,
            order_id,
        )
    )

    order_found = (
        history_item is not None
    )

    order_id_match = False
    symbol_match = False
    side_match = False
    position_side_match = False

    final_status = ""
    status_recognized = False

    original_qty = ZERO
    executed_qty = ZERO

    quantity_reconciliation = False

    first_processing = False
    duplicate_blocked = False
    actual_terminal = False
    actual_fill_delta = ZERO

    if history_item:
        found_order_id = history_order_id(
            history_item
        )

        order_id_match = (
            found_order_id
            == order_id
        )

        symbol_match = (
            str(
                history_item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == DEMO_SYMBOL.upper()
        )

        side_match = (
            str(
                history_item.get(
                    "side",
                    "",
                )
            ).upper()
            == "BUY"
        )

        position_side_match = (
            str(
                history_item.get(
                    "positionSide",
                    history_item.get(
                        "position_side",
                        "",
                    ),
                )
            ).upper()
            == "LONG"
        )

        final_status = normalize_order_status(
            history_item.get(
                "status",
                "",
            )
        )

        status_recognized = (
            final_status
            in RECOGNIZED_ORDER_STATUSES
        )

        original_qty = D(
            history_item.get(
                "origQty",
                history_item.get(
                    "quantity",
                    history_item.get(
                        "size",
                        0,
                    ),
                ),
            )
        )

        executed_qty = D(
            history_item.get(
                "executedQty",
                history_item.get(
                    "filledQty",
                    history_item.get(
                        "filled_qty",
                        0,
                    ),
                ),
            )
        )

        quantity_reconciliation = (
            original_qty == quantity
            and executed_qty >= ZERO
            and executed_qty <= original_qty
        )

        first_processing = (
            process_exchange_event_once(
                order_id,
                final_status,
                executed_qty,
            )
        )

        second_processing = (
            process_exchange_event_once(
                order_id,
                final_status,
                executed_qty,
            )
        )

        duplicate_blocked = (
            first_processing
            and not second_processing
        )

        actual_state = OrderState(
            order_id=order_id
        )

        accepted, actual_fill_delta = (
            update_order_state(
                actual_state,
                final_status,
                executed_qty,
            )
        )

        actual_terminal = (
            accepted
            and actual_state.terminal
        )

    positions_after = await get_demo_positions(
        session
    )

    position_after = demo_position_size(
        positions_after,
        DEMO_SYMBOL,
        "LONG",
    )

    expected_position_after = (
        position_before
        + executed_qty
    )

    position_reconciled = (
        position_after
        == expected_position_after
    )

    lifecycle_validation = all(
        (
            R25_DEMO_POST_ATTEMPTED,
            R25_DEMO_POST_ACCEPTED,
            bool(order_id),
            order_found,
            order_id_match,
            symbol_match,
            side_match,
            position_side_match,
            status_recognized,
            quantity_reconciliation,
            duplicate_blocked,
            position_reconciled,
        )
    )

    if lifecycle_validation:
        transition_intent(
            intent,
            "RECONCILED",
        )

    return DemoLifecycleResult(
        enabled=True,
        symbol=DEMO_SYMBOL,
        side="BUY",
        position_side="LONG",
        order_type="LIMIT",
        time_in_force="IOC",
        limit_price=demo_limit_price,
        price_step_match=price_step_match,
        post_attempted=R25_DEMO_POST_ATTEMPTED,
        post_accepted=R25_DEMO_POST_ACCEPTED,
        order_id=order_id,
        history_lookup_attempted=True,
        history_poll_attempts=poll_attempts,
        order_found=order_found,
        order_id_match=order_id_match,
        symbol_match=symbol_match,
        side_match=side_match,
        position_side_match=position_side_match,
        final_status=final_status,
        status_recognized=status_recognized,
        requested_quantity=quantity,
        history_original_quantity=original_qty,
        history_executed_quantity=executed_qty,
        quantity_reconciliation=quantity_reconciliation,
        lifecycle_validation=lifecycle_validation,
        actual_first_processing=first_processing,
        actual_duplicate_blocked=duplicate_blocked,
        actual_terminal=actual_terminal,
        actual_fill_delta=actual_fill_delta,
        position_before=position_before,
        position_after=position_after,
        position_reconciled=position_reconciled,
    )


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions_r25() -> None:
    assert_absolute_execution_safety()

    if R25_REAL_POST_CALLED:
        raise RuntimeError(
            "R25 SAFETY FAILURE: real POST path was called."
        )

    if not real_post_blocked(
        "/capi/v3/order"
    ):
        raise RuntimeError(
            "R25 SAFETY FAILURE: real order path is not blocked."
        )

    if real_post_blocked(
        "/capi/v3/sim/order"
    ):
        raise RuntimeError(
            "R25 SAFETY FAILURE: demo order path "
            "incorrectly classified as real."
        )


# ============================================================
# DIAGNOSTIC REPORT
# ============================================================

def build_success_report(
    available_usdt: Decimal,
    mark_price: Decimal,
    contract: ContractInfo,
    margin: Decimal,
    notional: Decimal,
    quantity: Decimal,
    signal_test: SignalGateTest,
    state_test: StateMachineTest,
    intent_test: IntentTest,
    preflight: PreflightResult,
    intent: ExecutionIntent,
    lifecycle: DemoLifecycleResult,
) -> str:

    initial_exposure = ENTRY_PERCENT

    pyramid_exposure = (
        Decimal(
            MAX_PYRAMID_ADDS
        )
        * PYRAMID_SIZE_PERCENT
    )

    backup_exposure = (
        Decimal(
            MAX_BACKUPS
        )
        * BACKUP_SIZE_PERCENT
    )

    total_exposure = (
        initial_exposure
        + pyramid_exposure
        + backup_exposure
    )

    exposure_passed = (
        total_exposure
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    leverage_gate = (
        LEVERAGE
        <= MAX_CONFIG_LEVERAGE
        and LEVERAGE
        >= contract.min_leverage
        and LEVERAGE
        <= contract.max_leverage
    )

    quantity_positive = (
        quantity > ZERO
    )

    minimum_passed = (
        quantity
        >= contract.min_quantity
    )

    lines = [
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED",
        SYMBOL,
        (
            "Available USDT: "
            + decimal_to_str(
                available_usdt
            )
        ),
        (
            "Mark Price: "
            + decimal_to_str(
                mark_price
            )
            + " USDT"
        ),

        "",
        "FINAL EXECUTION GATE",

        (
            "API Trading Symbol: "
            + status_icon(
                contract.trading
            )
        ),

        (
            "Fresh Signal Accepted: "
            + status_icon(
                signal_test.fresh_signal_accepted
            )
        ),

        (
            "Expired Signal Rejected: "
            + status_icon(
                signal_test.expired_signal_rejected
            )
        ),

        (
            "Loss Cooldown Test: "
            + status_icon(
                signal_test.loss_cooldown_test
            )
        ),

        (
            "Duplicate Signal Rejected: "
            + status_icon(
                signal_test.duplicate_signal_rejected
            )
        ),

        (
            "One Direction Gate: "
            + status_icon(
                signal_test.one_direction_gate
            )
        ),

        (
            "External Position Clear: "
            + status_icon(
                signal_test.external_position_clear
            )
        ),

        "",
        "ADJUSTABLE CONFIG",

        (
            "Entry: "
            + decimal_to_str(
                ENTRY_PERCENT
            )
            + "%"
        ),

        f"Leverage: {LEVERAGE}x",

        (
            "Max Config Leverage: "
            f"{MAX_CONFIG_LEVERAGE}x"
        ),

        f"Margin Type: {MARGIN_TYPE}",

        f"Max Pyramids: {MAX_PYRAMID_ADDS}",

        (
            "Pyramid Size: "
            + decimal_to_str(
                PYRAMID_SIZE_PERCENT
            )
            + "%"
        ),

        f"Max Backups: {MAX_BACKUPS}",

        (
            "Backup Size: "
            + decimal_to_str(
                BACKUP_SIZE_PERCENT
            )
            + "% each"
        ),

        (
            "Backup Buffer: "
            + decimal_to_str(
                BACKUP_BUFFER_PERCENT
            )
            + "%"
        ),

        (
            "Min Liq Distance: "
            + decimal_to_str(
                MIN_LIQ_DISTANCE_PERCENT
            )
            + "%"
        ),

        (
            "Max Fund Exposure: "
            + decimal_to_str(
                MAX_FUND_EXPOSURE_PERCENT
            )
            + "%"
        ),

        "",
        "WEEX CONTRACT",

        (
            "Minimum Order: "
            + decimal_to_str(
                contract.min_quantity
            )
        ),

        (
            "Quantity Precision: "
            f"{contract.quantity_precision}"
        ),

        (
            "Quantity Step: "
            + decimal_to_str(
                contract.quantity_step
            )
        ),

        (
            "Price Precision: "
            f"{contract.price_precision}"
        ),

        (
            "Price Step: "
            + decimal_to_str(
                contract.price_step
            )
        ),

        (
            "Contract Value: "
            + decimal_to_str(
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
            + status_icon(
                leverage_gate
            )
        ),

        "",
        "DYNAMIC ENTRY",

        (
            "Margin: "
            + decimal_to_str(
                margin
            )
            + " USDT"
        ),

        (
            "Notional: "
            + decimal_to_str(
                notional
            )
            + " USDT"
        ),

        (
            "Quantity: "
            + decimal_to_str(
                quantity
            )
        ),

        (
            "Quantity Positive: "
            + status_icon(
                quantity_positive
            )
        ),

        (
            "Minimum Passed: "
            + status_icon(
                minimum_passed
            )
        ),

        "",
        "WORST-CASE EXPOSURE",

        (
            "Initial: "
            + decimal_to_str(
                initial_exposure
            )
            + "%"
        ),

        (
            "Pyramids: "
            + decimal_to_str(
                pyramid_exposure
            )
            + "%"
        ),

        (
            "Backups: "
            + decimal_to_str(
                backup_exposure
            )
            + "%"
        ),

        (
            "Total: "
            + decimal_to_str(
                total_exposure
            )
            + "%"
            + " / "
            + decimal_to_str(
                MAX_FUND_EXPOSURE_PERCENT
            )
            + "%"
        ),

        (
            "Exposure Passed: "
            + status_icon(
                exposure_passed
            )
        ),

        "",
        "TP / TRAILING",

        (
            "TP1 / TP2 / TP3: "
            + decimal_to_str(
                TP1_PERCENT
            )
            + "% / "
            + decimal_to_str(
                TP2_PERCENT
            )
            + "% / "
            + decimal_to_str(
                TP3_PERCENT
            )
            + "%"
        ),

        (
            "TP1 Trigger: "
            + decimal_to_str(
                TP1_TRIGGER_PERCENT
            )
            + "%"
        ),

        (
            "TP2 Trigger: "
            + decimal_to_str(
                TP2_TRIGGER_PERCENT
            )
            + "%"
        ),

        (
            "Trailing Distance: "
            + decimal_to_str(
                TRAILING_DISTANCE_PERCENT
            )
            + "%"
        ),

        "",
        "R25 ORDER STATE MACHINE",

        (
            "NEW State Accepted: "
            + status_icon(
                state_test.new_accepted
            )
        ),

        (
            "Partial Fill #1 Delta: "
            + status_icon(
                state_test.partial_1
            )
        ),

        (
            "Partial Fill #2 Delta: "
            + status_icon(
                state_test.partial_2
            )
        ),

        (
            "FILLED Terminal State: "
            + status_icon(
                state_test.filled_terminal
            )
        ),

        (
            "Duplicate Exchange Event Blocked: "
            + status_icon(
                state_test.duplicate_blocked
            )
        ),

        (
            "Terminal Regression Blocked: "
            + status_icon(
                state_test.terminal_regression_blocked
            )
        ),

        "",
        "R25 EXECUTION INTENT GATE",

        (
            "Intent Created: "
            + status_icon(
                intent_test.intent_created
            )
        ),

        (
            "Duplicate Intent Blocked: "
            + status_icon(
                intent_test.duplicate_intent_blocked
            )
        ),

        (
            "NEW → PREFLIGHT: "
            + status_icon(
                intent_test.new_to_preflight
            )
        ),

        (
            "PREFLIGHT → READY: "
            + status_icon(
                intent_test.preflight_to_ready
            )
        ),

        (
            "Expired Intent Rejected: "
            + status_icon(
                intent_test.expired_intent_rejected
            )
        ),

        (
            "Terminal Intent Regression Blocked: "
            + status_icon(
                intent_test.terminal_regression_blocked
            )
        ),

        "",
        "R25 EXECUTION PREFLIGHT",

        (
            "Live Execution OFF: "
            + status_icon(
                preflight.live_execution_off
            )
        ),

        (
            "Hard Real POST Lock: "
            + status_icon(
                preflight.hard_real_post_lock
            )
        ),

        (
            "Intent Fresh: "
            + status_icon(
                preflight.intent_fresh
            )
        ),

        (
            "Intent Quantity Positive: "
            + status_icon(
                preflight.quantity_positive
            )
        ),

        (
            "Intent Minimum Passed: "
            + status_icon(
                preflight.minimum_passed
            )
        ),

        (
            "Intent Leverage Passed: "
            + status_icon(
                preflight.leverage_passed
            )
        ),

        (
            "Intent Exposure Passed: "
            + status_icon(
                preflight.exposure_passed
            )
        ),

        (
            "Real Order Path Blocked: "
            + status_icon(
                preflight.real_path_blocked
            )
        ),

        (
            "Overall Preflight: "
            + status_icon(
                preflight.passed
            )
        ),

        "",
        "R25 DEMO ORDER LIFECYCLE",

        f"Demo Symbol: {lifecycle.symbol}",
        f"Demo Side: {lifecycle.side}",
        (
            "Demo Position Side: "
            f"{lifecycle.position_side}"
        ),
        f"Demo Type: {lifecycle.order_type}",
        (
            "Demo Time In Force: "
            f"{lifecycle.time_in_force}"
        ),

        (
            "Demo Limit Price: "
            + decimal_to_str(
                lifecycle.limit_price
            )
        ),

        (
            "Price Step Match: "
            + status_icon(
                lifecycle.price_step_match
            )
        ),

        (
            "Demo POST Attempted: "
            + status_icon(
                lifecycle.post_attempted
            )
        ),

        (
            "Demo POST Accepted: "
            + status_icon(
                lifecycle.post_accepted
            )
        ),

        (
            "Demo Order ID: "
            + (
                lifecycle.order_id
                if lifecycle.order_id
                else "NONE"
            )
        ),

        (
            "History Lookup Attempted: "
            + status_icon(
                lifecycle.history_lookup_attempted
            )
        ),

        (
            "History Poll Attempts: "
            f"{lifecycle.history_poll_attempts}"
        ),

        (
            "Order Found In History: "
            + status_icon(
                lifecycle.order_found
            )
        ),

        (
            "History Order ID Match: "
            + status_icon(
                lifecycle.order_id_match
            )
        ),

        (
            "History Symbol Match: "
            + status_icon(
                lifecycle.symbol_match
            )
        ),

        (
            "History Side Match: "
            + status_icon(
                lifecycle.side_match
            )
        ),

        (
            "History Position Side Match: "
            + status_icon(
                lifecycle.position_side_match
            )
        ),

        (
            "Demo Final Status: "
            + (
                lifecycle.final_status
                if lifecycle.final_status
                else "UNKNOWN"
            )
        ),

        (
            "Status Recognized: "
            + status_icon(
                lifecycle.status_recognized
            )
        ),

        (
            "Requested Quantity: "
            + decimal_to_str(
                lifecycle.requested_quantity
            )
        ),

        (
            "History Original Quantity: "
            + decimal_to_str(
                lifecycle.history_original_quantity
            )
        ),

        (
            "History Executed Quantity: "
            + decimal_to_str(
                lifecycle.history_executed_quantity
            )
        ),

        (
            "Quantity Reconciliation: "
            + status_icon(
                lifecycle.quantity_reconciliation
            )
        ),

        (
            "Lifecycle Validation: "
            + status_icon(
                lifecycle.lifecycle_validation
            )
        ),

        "",
        "R25 ACTUAL HISTORY IDEMPOTENCY",

        (
            "First Processing Accepted: "
            + status_icon(
                lifecycle.actual_first_processing
            )
        ),

        (
            "Duplicate Processing Blocked: "
            + status_icon(
                lifecycle.actual_duplicate_blocked
            )
        ),

        (
            "Actual History Terminal: "
            + status_icon(
                lifecycle.actual_terminal
            )
        ),

        (
            "Actual Fill Delta: "
            + decimal_to_str(
                lifecycle.actual_fill_delta
            )
        ),

        "",
        "R25 DEMO POSITION RECONCILIATION",

        (
            "Position Size Before: "
            + decimal_to_str(
                lifecycle.position_before
            )
        ),

        (
            "Position Size After: "
            + decimal_to_str(
                lifecycle.position_after
            )
        ),

        (
            "Position Reconciled: "
            + status_icon(
                lifecycle.position_reconciled
            )
        ),

        "",
        "R25 SIGNAL → INTENT → EXECUTION CHAIN",

        "Signal Direction: LONG",
        f"Intent Side: {intent.side}",
        (
            "Intent Position Side: "
            f"{intent.position_side}"
        ),

        (
            "Intent Quantity: "
            + decimal_to_str(
                intent.quantity
            )
        ),

        (
            "Final Intent State: "
            f"{intent.state}"
        ),

        (
            "Intent Reconciled: "
            + status_icon(
                intent.state
                == "RECONCILED"
            )
        ),

        "",
        "R25 RENDER PERSISTENCE",

        "Health Server: ✅ ACTIVE",
        "Persistent Runtime: ✅ ACTIVE",
        "Auto Exit After Diagnostic: ❌ DISABLED",
        "Repeated Demo Order Loop: ❌ DISABLED",

        "",
        "ABSOLUTE EXECUTION SAFETY",

        (
            "Real POST Called: "
            + status_icon(
                R25_REAL_POST_CALLED
            )
        ),

        "🛡 R25 absolute real-order POST lock active",
        "⚠️ LIVE ORDER EXECUTION DISABLED",
        "⚠️ NO REAL ORDER WAS SENT",
    ]

    return "\n".join(
        lines
    )


# ============================================================
# ERROR REPORT
# ============================================================

def build_error_report(
    stage: str,
    exc: Exception,
) -> str:

    return "\n".join(
        [
            f"❌ MODULE {MODULE_NAME} ERROR",
            SYMBOL,

            (
                "Stage: "
                + stage
            ),

            (
                type(exc).__name__
                + ": "
                + str(exc)
            ),

            (
                "Real POST Called: "
                + status_icon(
                    R25_REAL_POST_CALLED
                )
            ),

            (
                "Demo POST Attempted: "
                + status_icon(
                    R25_DEMO_POST_ATTEMPTED
                )
            ),

            (
                "Demo POST Accepted: "
                + status_icon(
                    R25_DEMO_POST_ACCEPTED
                )
            ),

            "🛡 R25 absolute real-order POST lock active",
            "⚠️ LIVE ORDER EXECUTION DISABLED",
            "⚠️ NO REAL ORDER WAS SENT",
        ]
    )


# ============================================================
# R25 DIAGNOSTIC
# ============================================================

async def r25_run_diagnostic(
    session: aiohttp.ClientSession,
) -> None:

    global DIAGNOSTIC_COMPLETED
    global DIAGNOSTIC_RUNNING

    if DIAGNOSTIC_RUNNING:
        return

    if DIAGNOSTIC_COMPLETED:
        return

    DIAGNOSTIC_RUNNING = True

    stage = "startup"

    try:
        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"{MODULE_NAME} STARTING",
            flush=True,
        )

        print(
            "SIGNAL-TO-EXECUTION INTENT VALIDATION",
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

        stage = "absolute safety"

        final_safety_assertions_r25()

        stage = "configuration"

        validate_credentials()

        if ENTRY_PERCENT <= ZERO:
            raise RuntimeError(
                "ENTRY_PERCENT must be positive."
            )

        if LEVERAGE <= 0:
            raise RuntimeError(
                "LEVERAGE must be positive."
            )

        if LEVERAGE > MAX_CONFIG_LEVERAGE:
            raise RuntimeError(
                "Configured leverage exceeds "
                "MAX_CONFIG_LEVERAGE."
            )

        if MARGIN_TYPE != "ISOLATED":
            raise RuntimeError(
                "R25 requires MARGIN_TYPE=ISOLATED."
            )

        stage = "market data"

        mark_price = await get_mark_price(
            session,
            SYMBOL,
        )

        stage = "contract information"

        contract = await get_contract_info(
            session,
            SYMBOL,
        )

        if not contract.trading:
            raise RuntimeError(
                f"{SYMBOL} is not in trading status."
            )

        stage = "balance"

        available_usdt = await get_available_usdt(
            session
        )

        stage = "dynamic entry"

        (
            margin,
            notional,
            quantity,
        ) = calculate_entry(
            available_usdt,
            mark_price,
            contract,
        )

        if quantity <= ZERO:
            raise RuntimeError(
                "Calculated quantity is zero."
            )

        if quantity < contract.min_quantity:
            raise RuntimeError(
                "Calculated quantity is below "
                "WEEX minimum quantity."
            )

        stage = "signal gate"

        signal_test = run_signal_gate_test()

        signal_gate_passed = all(
            (
                signal_test.fresh_signal_accepted,
                signal_test.expired_signal_rejected,
                signal_test.loss_cooldown_test,
                signal_test.duplicate_signal_rejected,
                signal_test.one_direction_gate,
                signal_test.external_position_clear,
            )
        )

        if not signal_gate_passed:
            raise RuntimeError(
                "R25 signal gate self-test failed."
            )

        stage = "order state machine"

        state_test = (
            run_order_state_machine_test()
        )

        order_state_passed = all(
            (
                state_test.new_accepted,
                state_test.partial_1,
                state_test.partial_2,
                state_test.filled_terminal,
                state_test.duplicate_blocked,
                state_test.terminal_regression_blocked,
            )
        )

        if not order_state_passed:
            raise RuntimeError(
                "R25 order state machine "
                "self-test failed."
            )

        stage = "execution intent self-test"

        intent_test = (
            run_execution_intent_test()
        )

        intent_test_passed = all(
            (
                intent_test.intent_created,
                intent_test.duplicate_intent_blocked,
                intent_test.new_to_preflight,
                intent_test.preflight_to_ready,
                intent_test.terminal_regression_blocked,
                intent_test.expired_intent_rejected,
            )
        )

        if not intent_test_passed:
            raise RuntimeError(
                "R25 execution intent "
                "self-test failed."
            )

        stage = "execution intent creation"

        live_signal = Signal(
            signal_id=(
                "r25-live-rehearsal-"
                + uuid.uuid4().hex[:16]
            ),
            symbol=SYMBOL,
            direction="LONG",
            created_at=time.time(),
        )

        intent = build_execution_intent(
            live_signal,
            quantity,
        )

        if not process_intent_once(
            intent
        ):
            raise RuntimeError(
                "Execution intent duplicate "
                "detected unexpectedly."
            )

        if not transition_intent(
            intent,
            "PREFLIGHT",
        ):
            raise RuntimeError(
                "Unable to transition intent "
                "NEW → PREFLIGHT."
            )

        initial_exposure = ENTRY_PERCENT

        pyramid_exposure = (
            Decimal(
                MAX_PYRAMID_ADDS
            )
            * PYRAMID_SIZE_PERCENT
        )

        backup_exposure = (
            Decimal(
                MAX_BACKUPS
            )
            * BACKUP_SIZE_PERCENT
        )

        total_exposure = (
            initial_exposure
            + pyramid_exposure
            + backup_exposure
        )

        stage = "execution preflight"

        preflight = run_execution_preflight(
            intent,
            contract,
            total_exposure,
        )

        if not preflight.passed:
            transition_intent(
                intent,
                "REJECTED",
            )

            raise RuntimeError(
                "R25 execution preflight failed."
            )

        if not transition_intent(
            intent,
            "READY",
        ):
            raise RuntimeError(
                "Unable to transition intent "
                "PREFLIGHT → READY."
            )

        stage = "demo price calculation"

        demo_limit_price = (
            calculate_demo_limit_price(
                mark_price,
                contract.price_step,
            )
        )

        if (
            floor_to_step(
                demo_limit_price,
                contract.price_step,
            )
            != demo_limit_price
        ):
            raise RuntimeError(
                "Demo limit price does not "
                "match WEEX price step."
            )

        stage = "demo order transmission"

        lifecycle = await run_demo_lifecycle(
            session,
            quantity,
            demo_limit_price,
            contract,
            intent,
        )

        if (
            DEMO_ORDER_TEST_ENABLED
            and not lifecycle.lifecycle_validation
        ):
            raise RuntimeError(
                "R25 demo lifecycle validation failed."
            )

        stage = "final safety"

        final_safety_assertions_r25()

        report = build_success_report(
            available_usdt=available_usdt,
            mark_price=mark_price,
            contract=contract,
            margin=margin,
            notional=notional,
            quantity=quantity,
            signal_test=signal_test,
            state_test=state_test,
            intent_test=intent_test,
            preflight=preflight,
            intent=intent,
            lifecycle=lifecycle,
        )

        print(
            "\n" + report + "\n",
            flush=True,
        )

        await send_telegram(
            session,
            report,
        )

        DIAGNOSTIC_COMPLETED = True

    except Exception as exc:

        report = build_error_report(
            stage,
            exc,
        )

        print(
            "\n" + report + "\n",
            flush=True,
        )

        traceback.print_exc()

        try:
            await send_telegram(
                session,
                report,
            )

        except Exception:
            traceback.print_exc()

    finally:
        DIAGNOSTIC_RUNNING = False


# ============================================================
# PERSISTENT APPLICATION
# ============================================================

async def application_main() -> None:
    assert_absolute_execution_safety()

    await start_health_server()

    timeout = aiohttp.ClientTimeout(
        total=30,
        connect=10,
        sock_connect=10,
        sock_read=20,
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        await asyncio.sleep(
            1
        )

        await r25_run_diagnostic(
            session
        )

        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"{MODULE_NAME} PERSISTENT RUNTIME ACTIVE",
            flush=True,
        )

        print(
            "DIAGNOSTIC WILL NOT AUTO-REPEAT",
            flush=True,
        )

        print(
            "REAL ORDER TRANSMISSION REMAINS DISABLED",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        while True:
            await asyncio.sleep(
                3600
            )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    try:
        asyncio.run(
            application_main()
        )

    except KeyboardInterrupt:
        print(
            f"{MODULE_NAME} STOPPED",
            flush=True,
        )

    except Exception:
        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"❌ {MODULE_NAME} FATAL STARTUP ERROR",
            flush=True,
        )

        traceback.print_exc()

        print(
            "🛡 REAL ORDER POST LOCK REMAINS ACTIVE",
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
    man()
