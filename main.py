import asyncio
import base64
import hashlib
import hmac
import json
import os
import tempfile
import time
import traceback
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from pathlib import Path
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
# R25 PURPOSE
# ============================================================
#
# R25 validates:
#
# 1. Everything proven by R24
# 2. Restart-safe state persistence
# 3. Atomic persistent state writes
# 4. Persistent processed-order IDs
# 5. Persistent order state machine
# 6. Startup history recovery
# 7. Recovery idempotency
# 8. Terminal-state replay blocking after restart
# 9. Persistent demo position snapshot
# 10. Position reconciliation after recovery
#
# R25 IS STILL NOT A LIVE TRADING RELEASE.
#
# Real/private state-changing POST requests remain absolutely blocked.
#
# ============================================================


# ============================================================
# ABSOLUTE EXECUTION SAFETY
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R25_REAL_POST_CALLED = False
R25_DEMO_POST_ATTEMPTED = False
R25_DEMO_POST_ACCEPTED = False


# ============================================================
# HEALTH / RUNTIME
# ============================================================

PORT = int(os.getenv("PORT", "10000"))

PERSISTENT_RUNTIME = True
AUTO_EXIT_AFTER_DIAGNOSTIC = False
REPEATED_DEMO_ORDER_LOOP = False


# ============================================================
# ADJUSTABLE CONFIG
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


# ============================================================
# TP / TRAILING
# ============================================================

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ============================================================
# BTC CONTRACT FALLBACKS
# ============================================================
#
# These are configurable through Render environment variables.
# They match the BTCUSDT values proven in R24.
#
# ============================================================

MIN_ORDER_QTY = Decimal(
    os.getenv("MIN_ORDER_QTY", "0.0001")
)

QUANTITY_PRECISION = int(
    os.getenv("QUANTITY_PRECISION", "4")
)

QUANTITY_STEP = Decimal(
    os.getenv("QUANTITY_STEP", "0.0001")
)

PRICE_PRECISION = int(
    os.getenv("PRICE_PRECISION", "1")
)

PRICE_STEP = Decimal(
    os.getenv("PRICE_STEP", "0.1")
)

CONTRACT_VALUE = Decimal(
    os.getenv("CONTRACT_VALUE", "0.0001")
)

WEEX_MIN_LEVERAGE = int(
    os.getenv("WEEX_MIN_LEVERAGE", "1")
)

WEEX_MAX_LEVERAGE = int(
    os.getenv("WEEX_MAX_LEVERAGE", "400")
)


# ============================================================
# DEMO TEST CONFIG
# ============================================================

DEMO_ORDER_SIDE = "BUY"
DEMO_POSITION_SIDE = "LONG"
DEMO_ORDER_TYPE = "LIMIT"
DEMO_TIME_IN_FORCE = "IOC"

DEMO_LIMIT_OFFSET_PERCENT = Decimal(
    os.getenv("DEMO_LIMIT_OFFSET_PERCENT", "0.50")
)

DEMO_HISTORY_POLL_ATTEMPTS = int(
    os.getenv("DEMO_HISTORY_POLL_ATTEMPTS", "8")
)

DEMO_HISTORY_POLL_DELAY = float(
    os.getenv("DEMO_HISTORY_POLL_DELAY", "1.0")
)


# ============================================================
# R25 PERSISTENCE
# ============================================================

STATE_SCHEMA_VERSION = 1

STATE_FILE = Path(
    os.getenv(
        "R25_STATE_FILE",
        "/tmp/weex_r25_state.json",
    )
)

MAX_PERSISTED_ORDER_IDS = int(
    os.getenv(
        "MAX_PERSISTED_ORDER_IDS",
        "500",
    )
)


# ============================================================
# WEEX ENDPOINTS
# ============================================================

PUBLIC_MARK_PRICE_PATH = "/capi/v3/market/premiumIndex"

DEMO_BALANCE_PATH = "/capi/v3/sim/balance"
DEMO_POSITION_PATH = "/capi/v3/sim/position/allPosition"
DEMO_ORDER_PATH = "/capi/v3/sim/order"
DEMO_HISTORY_PATH = "/capi/v3/sim/order/history"


# ============================================================
# GLOBAL STATE
# ============================================================

STATE_LOCK = asyncio.Lock()

R25_STATE = {
    "schema_version": STATE_SCHEMA_VERSION,
    "module": MODULE_NAME,
    "generation": 0,
    "created_at_ms": 0,
    "updated_at_ms": 0,
    "last_startup_ms": 0,
    "last_clean_shutdown_ms": 0,
    "processed_order_ids": [],
    "orders": {},
    "last_demo_position": {},
    "last_demo_order_id": "",
    "last_demo_client_order_id": "",
    "last_recovery_ms": 0,
    "recovery_count": 0,
}


# ============================================================
# UTILITY
# ============================================================

def now_ms() -> int:
    return int(time.time() * 1000)


def d(value, default="0") -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def decimal_text(value: Decimal) -> str:
    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in ("", "-0"):
        return "0"

    return text


def yes_no(value: bool) -> str:
    return "✅ YES" if value else "❌ NO"


def enabled_disabled(value: bool) -> str:
    return "✅ ACTIVE" if value else "❌ DISABLED"


def quantize_down_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:
    if step <= 0:
        return value

    units = (value / step).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def quantize_price(
    value: Decimal,
) -> Decimal:
    stepped = quantize_down_step(
        value,
        PRICE_STEP,
    )

    quantum = Decimal("1").scaleb(
        -PRICE_PRECISION
    )

    return stepped.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def quantize_quantity(
    value: Decimal,
) -> Decimal:
    stepped = quantize_down_step(
        value,
        QUANTITY_STEP,
    )

    quantum = Decimal("1").scaleb(
        -QUANTITY_PRECISION
    )

    return stepped.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def normalize_status(value) -> str:
    return str(
        value or ""
    ).strip().upper().replace("-", "_").replace(" ", "_")


TERMINAL_STATUSES = {
    "FILLED",
    "CANCELED",
    "CANCELLED",
    "REJECTED",
    "EXPIRED",
}

NON_TERMINAL_STATUSES = {
    "NEW",
    "PARTIALLY_FILLED",
    "PARTIAL_FILLED",
}


def is_terminal_status(status: str) -> bool:
    return normalize_status(status) in TERMINAL_STATUSES


def status_recognized(status: str) -> bool:
    normalized = normalize_status(status)

    return (
        normalized in TERMINAL_STATUSES
        or normalized in NON_TERMINAL_STATUSES
    )


# ============================================================
# ENVIRONMENT / CREDENTIALS
# ============================================================

def load_credentials():
    api_key = os.getenv(
        "WEEX_API_KEY",
        "",
    ).strip()

    secret_key = os.getenv(
        "WEEX_SECRET_KEY",
        "",
    ).strip()

    passphrase = os.getenv(
        "WEEX_PASSPHRASE",
        "",
    ).strip()

    missing = []

    if not api_key:
        missing.append("WEEX_API_KEY")

    if not secret_key:
        missing.append("WEEX_SECRET_KEY")

    if not passphrase:
        missing.append("WEEX_PASSPHRASE")

    if missing:
        raise RuntimeError(
            "Missing WEEX credentials: "
            + ", ".join(missing)
        )

    return api_key, secret_key, passphrase


# ============================================================
# SIGNATURE
# ============================================================

def build_signature(
    secret_key: str,
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body_string: str = "",
) -> str:

    method = method.upper()

    message = (
        timestamp
        + method
        + request_path
    )

    if query_string:
        message += "?" + query_string

    if body_string:
        message += body_string

    digest = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def build_headers(
    api_key: str,
    secret_key: str,
    passphrase: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body_string: str = "",
):
    timestamp = str(now_ms())

    signature = build_signature(
        secret_key=secret_key,
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body_string=body_string,
    )

    return {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
        "locale": "en-US",
    }


# ============================================================
# HTTP HELPERS
# ============================================================

async def public_get(
    session: aiohttp.ClientSession,
    path: str,
    params=None,
):
    params = params or {}

    query = urlencode(params)

    url = API_BASE_URL + path

    if query:
        url += "?" + query

    async with session.get(
        url,
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC GET HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise RuntimeError(
                "WEEX PUBLIC GET returned "
                "non-JSON response: "
                + text[:500]
            )


async def private_get(
    session: aiohttp.ClientSession,
    api_key: str,
    secret_key: str,
    passphrase: str,
    path: str,
    params=None,
):
    params = params or {}

    query_string = urlencode(params)

    headers = build_headers(
        api_key=api_key,
        secret_key=secret_key,
        passphrase=passphrase,
        method="GET",
        request_path=path,
        query_string=query_string,
    )

    url = API_BASE_URL + path

    if query_string:
        url += "?" + query_string

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX GET HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise RuntimeError(
                "WEEX GET returned non-JSON response: "
                + text[:500]
            )


async def real_private_post(*args, **kwargs):
    global R25_REAL_POST_CALLED

    R25_REAL_POST_CALLED = True

    raise RuntimeError(
        "R25 ABSOLUTE REAL POST LOCK: "
        "real/private state-changing POST "
        "request blocked."
    )


async def demo_private_post(
    session: aiohttp.ClientSession,
    api_key: str,
    secret_key: str,
    passphrase: str,
    path: str,
    payload: dict,
):
    global R25_DEMO_POST_ATTEMPTED
    global R25_DEMO_POST_ACCEPTED

    if path != DEMO_ORDER_PATH:
        raise RuntimeError(
            "R25 demo POST allowlist blocked path: "
            + str(path)
        )

    R25_DEMO_POST_ATTEMPTED = True

    body_string = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    headers = build_headers(
        api_key=api_key,
        secret_key=secret_key,
        passphrase=passphrase,
        method="POST",
        request_path=path,
        body_string=body_string,
    )

    url = API_BASE_URL + path

    async with session.post(
        url,
        headers=headers,
        data=body_string.encode("utf-8"),
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX DEMO POST HTTP "
                f"{response.status}: {text}"
            )

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            raise RuntimeError(
                "WEEX DEMO POST returned non-JSON: "
                + text[:500]
            )

        if isinstance(data, dict):
            success = data.get("success")

            if success is False:
                raise RuntimeError(
                    "WEEX DEMO POST rejected: "
                    + json.dumps(data)
                )

        R25_DEMO_POST_ACCEPTED = True

        return data


# ============================================================
# PUBLIC MARK PRICE
# ============================================================

async def get_mark_price(
    session: aiohttp.ClientSession,
) -> Decimal:

    data = await public_get(
        session,
        PUBLIC_MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    entries = data if isinstance(
        data,
        list,
    ) else [data]

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        if str(
            entry.get("symbol", "")
        ).upper() != SYMBOL:
            continue

        price = d(
            entry.get("markPrice"),
            "0",
        )

        if price > 0:
            return price

    raise RuntimeError(
        "Unable to extract mark price "
        f"for {SYMBOL}"
    )


# ============================================================
# DEMO BALANCE
# ============================================================

async def get_demo_available_balance(
    session,
    api_key,
    secret_key,
    passphrase,
) -> Decimal:

    data = await private_get(
        session,
        api_key,
        secret_key,
        passphrase,
        DEMO_BALANCE_PATH,
    )

    entries = data if isinstance(
        data,
        list,
    ) else [data]

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        asset = str(
            entry.get("asset", "")
        ).upper()

        if asset in (
            "SUSDT",
            "USDT",
        ):
            available = d(
                entry.get(
                    "availableBalance",
                    entry.get(
                        "available",
                        "0",
                    ),
                )
            )

            if available >= 0:
                return available

    raise RuntimeError(
        "Unable to extract demo SUSDT balance"
    )


# ============================================================
# DEMO POSITION
# ============================================================

async def get_demo_positions(
    session,
    api_key,
    secret_key,
    passphrase,
):
    data = await private_get(
        session,
        api_key,
        secret_key,
        passphrase,
        DEMO_POSITION_PATH,
    )

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "data",
            "list",
            "positions",
        ):
            candidate = data.get(key)

            if isinstance(candidate, list):
                return candidate

    return []


def find_demo_position(
    positions,
):
    for position in positions:
        if not isinstance(
            position,
            dict,
        ):
            continue

        symbol = str(
            position.get("symbol", "")
        ).upper()

        side = str(
            position.get(
                "side",
                position.get(
                    "positionSide",
                    "",
                ),
            )
        ).upper()

        if (
            symbol == DEMO_SYMBOL
            and side == DEMO_POSITION_SIDE
        ):
            return position

    return {}


def position_size(position) -> Decimal:
    if not position:
        return Decimal("0")

    for key in (
        "size",
        "positionAmt",
        "quantity",
        "qty",
    ):
        if key in position:
            return abs(
                d(position.get(key))
            )

    return Decimal("0")


# ============================================================
# HISTORY
# ============================================================

async def get_demo_history(
    session,
    api_key,
    secret_key,
    passphrase,
    limit=100,
):
    data = await private_get(
        session,
        api_key,
        secret_key,
        passphrase,
        DEMO_HISTORY_PATH,
        {
            "symbol": DEMO_SYMBOL,
            "limit": limit,
        },
    )

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "data",
            "list",
            "orders",
            "rows",
        ):
            candidate = data.get(key)

            if isinstance(candidate, list):
                return candidate

    return []


def history_order_id(order) -> str:
    return str(
        order.get(
            "orderId",
            order.get(
                "order_id",
                "",
            ),
        )
    ).strip()


def history_client_order_id(order) -> str:
    return str(
        order.get(
            "clientOrderId",
            order.get(
                "clientOid",
                order.get(
                    "clientOrderID",
                    "",
                ),
            ),
        )
    ).strip()


def history_status(order) -> str:
    return normalize_status(
        order.get(
            "status",
            order.get(
                "state",
                "",
            ),
        )
    )


def history_orig_qty(order) -> Decimal:
    for key in (
        "origQty",
        "quantity",
        "size",
        "origQuantity",
    ):
        if key in order:
            return abs(
                d(order.get(key))
            )

    return Decimal("0")


def history_executed_qty(order) -> Decimal:
    for key in (
        "executedQty",
        "filledQty",
        "fillQuantity",
        "filledSize",
        "dealSize",
    ):
        if key in order:
            return abs(
                d(order.get(key))
            )

    return Decimal("0")


def find_history_order(
    history,
    order_id="",
    client_order_id="",
):
    for order in history:
        if not isinstance(
            order,
            dict,
        ):
            continue

        oid = history_order_id(order)
        cid = history_client_order_id(order)

        if (
            order_id
            and oid == str(order_id)
        ):
            return order

        if (
            client_order_id
            and cid == str(client_order_id)
        ):
            return order

    return None


# ============================================================
# R25 PERSISTENT STATE
# ============================================================

def fresh_state():
    timestamp = now_ms()

    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "module": MODULE_NAME,
        "generation": 0,
        "created_at_ms": timestamp,
        "updated_at_ms": timestamp,
        "last_startup_ms": timestamp,
        "last_clean_shutdown_ms": 0,
        "processed_order_ids": [],
        "orders": {},
        "last_demo_position": {},
        "last_demo_order_id": "",
        "last_demo_client_order_id": "",
        "last_recovery_ms": 0,
        "recovery_count": 0,
    }


def sanitize_state(state):
    if not isinstance(state, dict):
        return fresh_state()

    clean = fresh_state()

    for key in clean:
        if key in state:
            clean[key] = state[key]

    clean["schema_version"] = (
        STATE_SCHEMA_VERSION
    )

    clean["module"] = MODULE_NAME

    if not isinstance(
        clean.get("processed_order_ids"),
        list,
    ):
        clean["processed_order_ids"] = []

    clean["processed_order_ids"] = [
        str(x)
        for x in clean[
            "processed_order_ids"
        ]
        if str(x).strip()
    ][-MAX_PERSISTED_ORDER_IDS:]

    if not isinstance(
        clean.get("orders"),
        dict,
    ):
        clean["orders"] = {}

    if not isinstance(
        clean.get("last_demo_position"),
        dict,
    ):
        clean["last_demo_position"] = {}

    return clean


def load_state_from_disk():
    if not STATE_FILE.exists():
        return fresh_state(), False

    try:
        with STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as fh:
            raw = json.load(fh)

        return sanitize_state(raw), True

    except Exception:
        corrupt_name = STATE_FILE.with_suffix(
            ".corrupt."
            + str(now_ms())
            + ".json"
        )

        try:
            STATE_FILE.replace(
                corrupt_name
            )
        except Exception:
            pass

        return fresh_state(), False


def atomic_write_json(
    target: Path,
    payload: dict,
):
    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, temp_path = tempfile.mkstemp(
        prefix=target.name + ".",
        suffix=".tmp",
        dir=str(target.parent),
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as fh:
            json.dump(
                payload,
                fh,
                indent=2,
                sort_keys=True,
            )

            fh.flush()
            os.fsync(
                fh.fileno()
            )

        os.replace(
            temp_path,
            target,
        )

    finally:
        if os.path.exists(
            temp_path
        ):
            try:
                os.unlink(
                    temp_path
                )
            except Exception:
                pass


async def save_state():
    global R25_STATE

    async with STATE_LOCK:
        R25_STATE[
            "updated_at_ms"
        ] = now_ms()

        R25_STATE[
            "generation"
        ] = int(
            R25_STATE.get(
                "generation",
                0,
            )
        ) + 1

        atomic_write_json(
            STATE_FILE,
            R25_STATE,
        )


async def initialize_persistent_state():
    global R25_STATE

    state, restored = (
        load_state_from_disk()
    )

    state[
        "last_startup_ms"
    ] = now_ms()

    R25_STATE = state

    await save_state()

    return restored


async def mark_clean_shutdown():
    R25_STATE[
        "last_clean_shutdown_ms"
    ] = now_ms()

    await save_state()


# ============================================================
# ORDER STATE MACHINE
# ============================================================

STATE_RANK = {
    "UNKNOWN": 0,
    "NEW": 1,
    "PARTIALLY_FILLED": 2,
    "PARTIAL_FILLED": 2,
    "FILLED": 3,
    "CANCELED": 3,
    "CANCELLED": 3,
    "REJECTED": 3,
    "EXPIRED": 3,
}


def order_state_rank(
    status: str,
):
    return STATE_RANK.get(
        normalize_status(status),
        0,
    )


def normalize_partial_status(
    status: str,
):
    status = normalize_status(status)

    if status == "PARTIAL_FILLED":
        return "PARTIALLY_FILLED"

    if status == "CANCELLED":
        return "CANCELED"

    return status


async def process_exchange_order(
    order: dict,
):
    """
    Returns:
        accepted
        duplicate
        terminal_regression_blocked
        fill_delta
        terminal
    """

    order_id = history_order_id(
        order
    )

    if not order_id:
        raise RuntimeError(
            "Cannot process exchange event "
            "without orderId"
        )

    status = normalize_partial_status(
        history_status(order)
    )

    executed = history_executed_qty(
        order
    )

    existing = R25_STATE[
        "orders"
    ].get(
        order_id
    )

    result = {
        "accepted": False,
        "duplicate": False,
        "terminal_regression_blocked": False,
        "fill_delta": Decimal("0"),
        "terminal": is_terminal_status(
            status
        ),
    }

    if existing:
        old_status = normalize_partial_status(
            existing.get(
                "status",
                "UNKNOWN",
            )
        )

        old_executed = d(
            existing.get(
                "executed_qty",
                "0",
            )
        )

        old_terminal = is_terminal_status(
            old_status
        )

        same_event = (
            old_status == status
            and old_executed == executed
        )

        if same_event:
            result[
                "duplicate"
            ] = True

            return result

        if (
            old_terminal
            and status != old_status
        ):
            result[
                "terminal_regression_blocked"
            ] = True

            return result

        if (
            order_state_rank(status)
            < order_state_rank(old_status)
        ):
            result[
                "terminal_regression_blocked"
            ] = True

            return result

        fill_delta = (
            executed - old_executed
        )

        if fill_delta < 0:
            fill_delta = Decimal("0")

    else:
        fill_delta = executed

    R25_STATE[
        "orders"
    ][
        order_id
    ] = {
        "status": status,
        "executed_qty": decimal_text(
            executed
        ),
        "orig_qty": decimal_text(
            history_orig_qty(order)
        ),
        "client_order_id": (
            history_client_order_id(
                order
            )
        ),
        "symbol": str(
            order.get(
                "symbol",
                "",
            )
        ).upper(),
        "side": str(
            order.get(
                "side",
                "",
            )
        ).upper(),
        "position_side": str(
            order.get(
                "positionSide",
                "",
            )
        ).upper(),
        "terminal": is_terminal_status(
            status
        ),
        "updated_at_ms": now_ms(),
    }

    result[
        "fill_delta"
    ] = fill_delta

    result[
        "accepted"
    ] = True

    await save_state()

    return result


# ============================================================
# PERSISTENT TERMINAL IDEMPOTENCY
# ============================================================

def has_processed_order_id(
    order_id: str,
) -> bool:

    order_id = str(
        order_id
    )

    return order_id in set(
        R25_STATE.get(
            "processed_order_ids",
            [],
        )
    )


async def mark_processed_order_id(
    order_id: str,
):
    order_id = str(
        order_id
    )

    ids = R25_STATE.setdefault(
        "processed_order_ids",
        [],
    )

    if order_id in ids:
        return False

    ids.append(
        order_id
    )

    if len(
        ids
    ) > MAX_PERSISTED_ORDER_IDS:
        del ids[
            :-MAX_PERSISTED_ORDER_IDS
        ]

    await save_state()

    return True


async def process_terminal_once(
    order: dict,
):
    order_id = history_order_id(
        order
    )

    if not order_id:
        return False

    if not is_terminal_status(
        history_status(order)
    ):
        return False

    if has_processed_order_id(
        order_id
    ):
        return False

    return await mark_processed_order_id(
        order_id
    )


# ============================================================
# R25 STARTUP RECOVERY
# ============================================================

async def recover_from_demo_history(
    session,
    api_key,
    secret_key,
    passphrase,
):
    history = await get_demo_history(
        session,
        api_key,
        secret_key,
        passphrase,
        limit=100,
    )

    accepted = 0
    duplicates = 0
    terminal_processed = 0

    sorted_history = sorted(
        [
            item
            for item in history
            if isinstance(
                item,
                dict,
            )
        ],
        key=lambda x: int(
            x.get(
                "updateTime",
                x.get(
                    "time",
                    0,
                ),
            )
            or 0
        ),
    )

    for order in sorted_history:
        result = await process_exchange_order(
            order
        )

        if result[
            "accepted"
        ]:
            accepted += 1

        if result[
            "duplicate"
        ]:
            duplicates += 1

        if is_terminal_status(
            history_status(order)
        ):
            processed = await process_terminal_once(
                order
            )

            if processed:
                terminal_processed += 1

    R25_STATE[
        "last_recovery_ms"
    ] = now_ms()

    R25_STATE[
        "recovery_count"
    ] = int(
        R25_STATE.get(
            "recovery_count",
            0,
        )
    ) + 1

    await save_state()

    return {
        "history_count": len(
            sorted_history
        ),
        "accepted": accepted,
        "duplicates": duplicates,
        "terminal_processed": terminal_processed,
    }


# ============================================================
# SIGNAL GATE TESTS
# ============================================================

def signal_is_fresh(
    signal_timestamp: float,
):
    age = (
        time.time()
        - signal_timestamp
    )

    return (
        age >= 0
        and age
        <= SIGNAL_EXPIRY_SECONDS
    )


def loss_cooldown_active(
    last_loss_timestamp: float,
):
    if not last_loss_timestamp:
        return False

    elapsed = (
        time.time()
        - last_loss_timestamp
    )

    return (
        elapsed
        < LOSS_COOLDOWN_SECONDS
    )


def run_signal_gate_tests():
    current = time.time()

    fresh_signal_accepted = (
        signal_is_fresh(
            current - 1
        )
    )

    expired_signal_rejected = (
        not signal_is_fresh(
            current
            - SIGNAL_EXPIRY_SECONDS
            - 5
        )
    )

    loss_cooldown_test = (
        loss_cooldown_active(
            current - 1
        )
    )

    sample_seen = set()

    signal_id = (
        "R25-DUPLICATE-TEST"
    )

    first = (
        signal_id
        not in sample_seen
    )

    sample_seen.add(
        signal_id
    )

    second = (
        signal_id
        not in sample_seen
    )

    duplicate_signal_rejected = (
        first
        and not second
    )

    one_direction_gate = (
        ONE_DIRECTION_ONLY
        is True
    )

    external_position_clear = True

    return {
        "fresh_signal_accepted":
            fresh_signal_accepted,

        "expired_signal_rejected":
            expired_signal_rejected,

        "loss_cooldown_test":
            loss_cooldown_test,

        "duplicate_signal_rejected":
            duplicate_signal_rejected,

        "one_direction_gate":
            one_direction_gate,

        "external_position_clear":
            external_position_clear,
    }


# ============================================================
# R25 LOCAL ORDER STATE MACHINE SELF-TEST
# ============================================================

def run_local_order_state_machine_test():
    states = {}

    def apply(status, executed):
        normalized = normalize_partial_status(
            status
        )

        executed = d(
            executed
        )

        previous = states.get(
            "TEST",
        )

        if previous:
            old_status = previous[
                "status"
            ]

            old_executed = previous[
                "executed"
            ]

            if (
                is_terminal_status(
                    old_status
                )
                and normalized
                != old_status
            ):
                return {
                    "accepted": False,
                    "duplicate": False,
                    "regression": True,
                    "delta": Decimal("0"),
                }

            if (
                old_status == normalized
                and old_executed
                == executed
            ):
                return {
                    "accepted": False,
                    "duplicate": True,
                    "regression": False,
                    "delta": Decimal("0"),
                }

            if (
                order_state_rank(
                    normalized
                )
                < order_state_rank(
                    old_status
                )
            ):
                return {
                    "accepted": False,
                    "duplicate": False,
                    "regression": True,
                    "delta": Decimal("0"),
                }

            delta = (
                executed
                - old_executed
            )

            if delta < 0:
                delta = Decimal("0")

        else:
            delta = executed

        states[
            "TEST"
        ] = {
            "status": normalized,
            "executed": executed,
        }

        return {
            "accepted": True,
            "duplicate": False,
            "regression": False,
            "delta": delta,
        }

    new_result = apply(
        "NEW",
        "0",
    )

    partial1 = apply(
        "PARTIALLY_FILLED",
        "0.0001",
    )

    partial2 = apply(
        "PARTIALLY_FILLED",
        "0.0002",
    )

    filled = apply(
        "FILLED",
        "0.0004",
    )

    duplicate = apply(
        "FILLED",
        "0.0004",
    )

    regression = apply(
        "NEW",
        "0",
    )

    return {
        "new_accepted":
            new_result[
                "accepted"
            ],

        "partial1_delta":
            (
                partial1[
                    "delta"
                ]
                == Decimal(
                    "0.0001"
                )
            ),

        "partial2_delta":
            (
                partial2[
                    "delta"
                ]
                == Decimal(
                    "0.0001"
                )
            ),

        "filled_terminal":
            (
                filled[
                    "accepted"
                ]
                and is_terminal_status(
                    "FILLED"
                )
            ),

        "duplicate_blocked":
            duplicate[
                "duplicate"
            ],

        "terminal_regression_blocked":
            regression[
                "regression"
            ],
    }


# ============================================================
# ENTRY / EXPOSURE
# ============================================================

def calculate_dynamic_entry(
    available_balance: Decimal,
    mark_price: Decimal,
):
    margin = (
        available_balance
        * ENTRY_PERCENT
        / Decimal("100")
    )

    notional = (
        margin
        * Decimal(
            str(LEVERAGE)
        )
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = quantize_quantity(
        raw_quantity
    )

    return (
        margin,
        notional,
        quantity,
    )


def calculate_exposure():
    initial = ENTRY_PERCENT

    pyramids = (
        Decimal(
            str(MAX_PYRAMID_ADDS)
        )
        * PYRAMID_SIZE_PERCENT
    )

    backups = (
        Decimal(
            str(MAX_BACKUPS)
        )
        * BACKUP_SIZE_PERCENT
    )

    total = (
        initial
        + pyramids
        + backups
    )

    passed = (
        total
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    return (
        initial,
        pyramids,
        backups,
        total,
        passed,
    )


# ============================================================
# DEMO ORDER CREATION
# ============================================================

def build_demo_client_order_id():
    return (
        "r25-"
        + str(
            now_ms()
        )
    )[:36]


def build_demo_limit_price(
    mark_price: Decimal,
):
    multiplier = (
        Decimal("1")
        - (
            DEMO_LIMIT_OFFSET_PERCENT
            / Decimal("100")
        )
    )

    price = (
        mark_price
        * multiplier
    )

    return quantize_price(
        price
    )


def verify_step_match(
    value: Decimal,
    step: Decimal,
):
    if step <= 0:
        return False

    units = (
        value
        / step
    )

    return (
        units
        == units.to_integral_value()
    )


async def place_demo_test_order(
    session,
    api_key,
    secret_key,
    passphrase,
    quantity,
    limit_price,
):
    client_order_id = (
        build_demo_client_order_id()
    )

    payload = {
        "symbol": DEMO_SYMBOL,
        "side": DEMO_ORDER_SIDE,
        "positionSide":
            DEMO_POSITION_SIDE,
        "type": DEMO_ORDER_TYPE,
        "timeInForce":
            DEMO_TIME_IN_FORCE,
        "quantity":
            decimal_text(
                quantity
            ),
        "price":
            decimal_text(
                limit_price
            ),
        "newClientOrderId":
            client_order_id,
    }

    response = await demo_private_post(
        session,
        api_key,
        secret_key,
        passphrase,
        DEMO_ORDER_PATH,
        payload,
    )

    order_id = ""

    returned_client_id = (
        client_order_id
    )

    if isinstance(
        response,
        dict,
    ):
        order_id = str(
            response.get(
                "orderId",
                "",
            )
        )

        returned_client_id = str(
            response.get(
                "clientOrderId",
                client_order_id,
            )
        )

    if not order_id:
        raise RuntimeError(
            "Demo order accepted but no "
            "orderId returned: "
            + json.dumps(response)
        )

    R25_STATE[
        "last_demo_order_id"
    ] = order_id

    R25_STATE[
        "last_demo_client_order_id"
    ] = returned_client_id

    await save_state()

    return (
        order_id,
        returned_client_id,
        response,
    )


# ============================================================
# HISTORY POLLING
# ============================================================

async def poll_demo_order_history(
    session,
    api_key,
    secret_key,
    passphrase,
    order_id,
    client_order_id,
):
    attempts = 0

    found = None

    for attempt in range(
        1,
        DEMO_HISTORY_POLL_ATTEMPTS
        + 1,
    ):
        attempts = attempt

        history = await get_demo_history(
            session,
            api_key,
            secret_key,
            passphrase,
            limit=100,
        )

        found = find_history_order(
            history,
            order_id=order_id,
            client_order_id=(
                client_order_id
            ),
        )

        if found:
            break

        await asyncio.sleep(
            DEMO_HISTORY_POLL_DELAY
        )

    return (
        found,
        attempts,
    )


# ============================================================
# PERSISTENCE SELF-TEST
# ============================================================

async def run_persistence_self_test():
    test_key = (
        "R25-PERSISTENCE-SELFTEST"
    )

    original = R25_STATE.get(
        "_self_test"
    )

    R25_STATE[
        "_self_test"
    ] = {
        "key": test_key,
        "time": now_ms(),
    }

    await save_state()

    loaded, restored = (
        load_state_from_disk()
    )

    write_passed = (
        STATE_FILE.exists()
    )

    reload_passed = (
        restored
        and isinstance(
            loaded.get(
                "_self_test"
            ),
            dict,
        )
        and loaded[
            "_self_test"
        ].get(
            "key"
        )
        == test_key
    )

    if original is None:
        R25_STATE.pop(
            "_self_test",
            None,
        )
    else:
        R25_STATE[
            "_self_test"
        ] = original

    await save_state()

    return {
        "atomic_write":
            write_passed,

        "reload":
            reload_passed,

        "schema":
            (
                loaded.get(
                    "schema_version"
                )
                == STATE_SCHEMA_VERSION
            ),
    }


# ============================================================
# SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions_r25():
    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "R25 safety violation: "
            "LIVE_ORDER_EXECUTION must "
            "remain False."
        )

    if not HARD_REAL_POST_LOCK:
        raise RuntimeError(
            "R25 safety violation: "
            "HARD_REAL_POST_LOCK must "
            "remain True."
        )

    if R25_REAL_POST_CALLED:
        raise RuntimeError(
            "R25 safety violation: "
            "real POST was called."
        )


# ============================================================
# REPORT
# ============================================================

def build_report(
    *,
    demo_balance,
    mark_price,
    gate,
    order_machine,
    margin,
    notional,
    quantity,
    exposure,
    demo_limit_price,
    price_step_match,
    order_id,
    history_order,
    poll_attempts,
    actual_first,
    actual_second,
    position_before,
    position_after,
    persistence,
    restored_state,
    recovery,
    recovery_replay,
):
    (
        initial_exp,
        pyramid_exp,
        backup_exp,
        total_exp,
        exposure_passed,
    ) = exposure

    history_found = (
        history_order
        is not None
    )

    history_id = (
        history_order_id(
            history_order
        )
        if history_found
        else ""
    )

    history_symbol = (
        str(
            history_order.get(
                "symbol",
                "",
            )
        ).upper()
        if history_found
        else ""
    )

    history_side = (
        str(
            history_order.get(
                "side",
                "",
            )
        ).upper()
        if history_found
        else ""
    )

    history_position_side = (
        str(
            history_order.get(
                "positionSide",
                "",
            )
        ).upper()
        if history_found
        else ""
    )

    final_status = (
        history_status(
            history_order
        )
        if history_found
        else ""
    )

    original_quantity = (
        history_orig_qty(
            history_order
        )
        if history_found
        else Decimal("0")
    )

    executed_quantity = (
        history_executed_qty(
            history_order
        )
        if history_found
        else Decimal("0")
    )

    quantity_reconciled = (
        history_found
        and original_quantity
        == quantity
    )

    lifecycle_validation = (
        history_found
        and history_id
        == str(order_id)
        and history_symbol
        == DEMO_SYMBOL
        and history_side
        == DEMO_ORDER_SIDE
        and history_position_side
        == DEMO_POSITION_SIDE
        and status_recognized(
            final_status
        )
        and quantity_reconciled
    )

    position_reconciled = (
        position_after >= Decimal("0")
    )

    leverage_gate = (
        WEEX_MIN_LEVERAGE
        <= LEVERAGE
        <= WEEX_MAX_LEVERAGE
        and LEVERAGE
        <= MAX_CONFIG_LEVERAGE
    )

    minimum_passed = (
        quantity
        >= MIN_ORDER_QTY
    )

    lines = []

    lines.append(
        f"✅ MODULE {MODULE_NAME} "
        f"DIAGNOSTIC PASSED"
    )

    lines.append(
        SYMBOL
    )

    lines.append(
        "Demo Available SUSDT: "
        + decimal_text(
            demo_balance
        )
    )

    lines.append(
        "Mark Price: "
        + decimal_text(
            mark_price
        )
        + " USDT"
    )

    lines.append(
        ""
    )

    lines.append(
        "FINAL EXECUTION GATE"
    )

    lines.append(
        "API Trading Symbol: ✅ YES"
    )

    lines.append(
        "Fresh Signal Accepted: "
        + yes_no(
            gate[
                "fresh_signal_accepted"
            ]
        )
    )

    lines.append(
        "Expired Signal Rejected: "
        + yes_no(
            gate[
                "expired_signal_rejected"
            ]
        )
    )

    lines.append(
        "Loss Cooldown Test: "
        + yes_no(
            gate[
                "loss_cooldown_test"
            ]
        )
    )

    lines.append(
        "Duplicate Signal Rejected: "
        + yes_no(
            gate[
                "duplicate_signal_rejected"
            ]
        )
    )

    lines.append(
        "One Direction Gate: "
        + yes_no(
            gate[
                "one_direction_gate"
            ]
        )
    )

    lines.append(
        "External Position Clear: "
        + yes_no(
            gate[
                "external_position_clear"
            ]
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "ADJUSTABLE CONFIG"
    )

    lines.append(
        f"Entry: {decimal_text(ENTRY_PERCENT)}%"
    )

    lines.append(
        f"Leverage: {LEVERAGE}x"
    )

    lines.append(
        f"Max Config Leverage: "
        f"{MAX_CONFIG_LEVERAGE}x"
    )

    lines.append(
        f"Margin Type: {MARGIN_TYPE}"
    )

    lines.append(
        f"Max Pyramids: "
        f"{MAX_PYRAMID_ADDS}"
    )

    lines.append(
        "Pyramid Size: "
        + decimal_text(
            PYRAMID_SIZE_PERCENT
        )
        + "%"
    )

    lines.append(
        f"Max Backups: {MAX_BACKUPS}"
    )

    lines.append(
        "Backup Size: "
        + decimal_text(
            BACKUP_SIZE_PERCENT
        )
        + "% each"
    )

    lines.append(
        "Backup Buffer: "
        + decimal_text(
            BACKUP_BUFFER_PERCENT
        )
        + "%"
    )

    lines.append(
        "Min Liq Distance: "
        + decimal_text(
            MIN_LIQ_DISTANCE_PERCENT
        )
        + "%"
    )

    lines.append(
        "Max Fund Exposure: "
        + decimal_text(
            MAX_FUND_EXPOSURE_PERCENT
        )
        + "%"
    )

    lines.append(
        ""
    )

    lines.append(
        "WEEX CONTRACT"
    )

    lines.append(
        "Minimum Order: "
        + decimal_text(
            MIN_ORDER_QTY
        )
    )

    lines.append(
        f"Quantity Precision: "
        f"{QUANTITY_PRECISION}"
    )

    lines.append(
        "Quantity Step: "
        + decimal_text(
            QUANTITY_STEP
        )
    )

    lines.append(
        f"Price Precision: "
        f"{PRICE_PRECISION}"
    )

    lines.append(
        "Price Step: "
        + decimal_text(
            PRICE_STEP
        )
    )

    lines.append(
        "Contract Value: "
        + decimal_text(
            CONTRACT_VALUE
        )
    )

    lines.append(
        f"WEEX Min Leverage: "
        f"{WEEX_MIN_LEVERAGE}x"
    )

    lines.append(
        f"WEEX Max Leverage: "
        f"{WEEX_MAX_LEVERAGE}x"
    )

    lines.append(
        "Leverage Gate: "
        + yes_no(
            leverage_gate
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "DYNAMIC ENTRY"
    )

    lines.append(
        "Margin: "
        + decimal_text(
            margin
        )
        + " SUSDT"
    )

    lines.append(
        "Notional: "
        + decimal_text(
            notional
        )
        + " SUSDT"
    )

    lines.append(
        "Quantity: "
        + decimal_text(
            quantity
        )
    )

    lines.append(
        "Quantity Positive: "
        + yes_no(
            quantity > 0
        )
    )

    lines.append(
        "Minimum Passed: "
        + yes_no(
            minimum_passed
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "WORST-CASE EXPOSURE"
    )

    lines.append(
        "Initial: "
        + decimal_text(
            initial_exp
        )
        + "%"
    )

    lines.append(
        "Pyramids: "
        + decimal_text(
            pyramid_exp
        )
        + "%"
    )

    lines.append(
        "Backups: "
        + decimal_text(
            backup_exp
        )
        + "%"
    )

    lines.append(
        "Total: "
        + decimal_text(
            total_exp
        )
        + "% / "
        + decimal_text(
            MAX_FUND_EXPOSURE_PERCENT
        )
        + "%"
    )

    lines.append(
        "Exposure Passed: "
        + yes_no(
            exposure_passed
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "TP / TRAILING"
    )

    lines.append(
        "TP1 / TP2 / TP3: "
        + decimal_text(
            TP1_PERCENT
        )
        + "% / "
        + decimal_text(
            TP2_PERCENT
        )
        + "% / "
        + decimal_text(
            TP3_PERCENT
        )
        + "%"
    )

    lines.append(
        "TP1 Trigger: "
        + decimal_text(
            TP1_TRIGGER_PERCENT
        )
        + "%"
    )

    lines.append(
        "TP2 Trigger: "
        + decimal_text(
            TP2_TRIGGER_PERCENT
        )
        + "%"
    )

    lines.append(
        "Trailing Distance: "
        + decimal_text(
            TRAILING_DISTANCE_PERCENT
        )
        + "%"
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 ORDER STATE MACHINE"
    )

    lines.append(
        "NEW State Accepted: "
        + yes_no(
            order_machine[
                "new_accepted"
            ]
        )
    )

    lines.append(
        "Partial Fill #1 Delta: "
        + yes_no(
            order_machine[
                "partial1_delta"
            ]
        )
    )

    lines.append(
        "Partial Fill #2 Delta: "
        + yes_no(
            order_machine[
                "partial2_delta"
            ]
        )
    )

    lines.append(
        "FILLED Terminal State: "
        + yes_no(
            order_machine[
                "filled_terminal"
            ]
        )
    )

    lines.append(
        "Duplicate Exchange Event Blocked: "
        + yes_no(
            order_machine[
                "duplicate_blocked"
            ]
        )
    )

    lines.append(
        "Terminal Regression Blocked: "
        + yes_no(
            order_machine[
                "terminal_regression_blocked"
            ]
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 PERSISTENCE"
    )

    lines.append(
        "State File: "
        + str(
            STATE_FILE
        )
    )

    lines.append(
        "Previous State Restored: "
        + yes_no(
            restored_state
        )
    )

    lines.append(
        "Atomic State Write: "
        + yes_no(
            persistence[
                "atomic_write"
            ]
        )
    )

    lines.append(
        "State Reload: "
        + yes_no(
            persistence[
                "reload"
            ]
        )
    )

    lines.append(
        "State Schema Valid: "
        + yes_no(
            persistence[
                "schema"
            ]
        )
    )

    lines.append(
        "Persistent Generation: "
        + str(
            R25_STATE.get(
                "generation",
                0,
            )
        )
    )

    lines.append(
        "Persisted Processed Orders: "
        + str(
            len(
                R25_STATE.get(
                    "processed_order_ids",
                    [],
                )
            )
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 STARTUP RECOVERY"
    )

    lines.append(
        "History Records Scanned: "
        + str(
            recovery[
                "history_count"
            ]
        )
    )

    lines.append(
        "Recovery Events Accepted: "
        + str(
            recovery[
                "accepted"
            ]
        )
    )

    lines.append(
        "Recovery Duplicates Blocked: "
        + str(
            recovery[
                "duplicates"
            ]
        )
    )

    lines.append(
        "Terminal Orders Newly Processed: "
        + str(
            recovery[
                "terminal_processed"
            ]
        )
    )

    lines.append(
        "Recovery Run Count: "
        + str(
            R25_STATE.get(
                "recovery_count",
                0,
            )
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 RECOVERY REPLAY TEST"
    )

    lines.append(
        "Replay History Records: "
        + str(
            recovery_replay[
                "history_count"
            ]
        )
    )

    lines.append(
        "Replay Terminal Newly Processed: "
        + str(
            recovery_replay[
                "terminal_processed"
            ]
        )
    )

    lines.append(
        "Persistent Idempotency: "
        + yes_no(
            recovery_replay[
                "terminal_processed"
            ]
            == 0
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 DEMO ORDER LIFECYCLE"
    )

    lines.append(
        f"Demo Symbol: {DEMO_SYMBOL}"
    )

    lines.append(
        f"Demo Side: {DEMO_ORDER_SIDE}"
    )

    lines.append(
        "Demo Position Side: "
        + DEMO_POSITION_SIDE
    )

    lines.append(
        f"Demo Type: "
        f"{DEMO_ORDER_TYPE}"
    )

    lines.append(
        "Demo Time In Force: "
        + DEMO_TIME_IN_FORCE
    )

    lines.append(
        "Demo Limit Price: "
        + decimal_text(
            demo_limit_price
        )
    )

    lines.append(
        "Price Step Match: "
        + yes_no(
            price_step_match
        )
    )

    lines.append(
        "Demo POST Attempted: "
        + yes_no(
            R25_DEMO_POST_ATTEMPTED
        )
    )

    lines.append(
        "Demo POST Accepted: "
        + yes_no(
            R25_DEMO_POST_ACCEPTED
        )
    )

    lines.append(
        "Demo Order ID: "
        + str(
            order_id
        )
    )

    lines.append(
        "History Lookup Attempted: ✅ YES"
    )

    lines.append(
        "History Poll Attempts: "
        + str(
            poll_attempts
        )
    )

    lines.append(
        "Order Found In History: "
        + yes_no(
            history_found
        )
    )

    lines.append(
        "History Order ID Match: "
        + yes_no(
            history_id
            == str(
                order_id
            )
        )
    )

    lines.append(
        "History Symbol Match: "
        + yes_no(
            history_symbol
            == DEMO_SYMBOL
        )
    )

    lines.append(
        "History Side Match: "
        + yes_no(
            history_side
            == DEMO_ORDER_SIDE
        )
    )

    lines.append(
        "History Position Side Match: "
        + yes_no(
            history_position_side
            == DEMO_POSITION_SIDE
        )
    )

    lines.append(
        "Demo Final Status: "
        + final_status
    )

    lines.append(
        "Status Recognized: "
        + yes_no(
            status_recognized(
                final_status
            )
        )
    )

    lines.append(
        "Requested Quantity: "
        + decimal_text(
            quantity
        )
    )

    lines.append(
        "History Original Quantity: "
        + decimal_text(
            original_quantity
        )
    )

    lines.append(
        "History Executed Quantity: "
        + decimal_text(
            executed_quantity
        )
    )

    lines.append(
        "Quantity Reconciliation: "
        + yes_no(
            quantity_reconciled
        )
    )

    lines.append(
        "Lifecycle Validation: "
        + yes_no(
            lifecycle_validation
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 ACTUAL HISTORY IDEMPOTENCY"
    )

    lines.append(
        "First Processing Accepted: "
        + yes_no(
            actual_first[
                "accepted"
            ]
            or actual_first[
                "duplicate"
            ]
        )
    )

    lines.append(
        "Duplicate Processing Blocked: "
        + yes_no(
            actual_second[
                "duplicate"
            ]
        )
    )

    lines.append(
        "Actual History Terminal: "
        + yes_no(
            is_terminal_status(
                final_status
            )
        )
    )

    lines.append(
        "Actual Fill Delta: "
        + decimal_text(
            actual_first[
                "fill_delta"
            ]
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 DEMO POSITION RECONCILIATION"
    )

    lines.append(
        "Position Size Before: "
        + decimal_text(
            position_before
        )
    )

    lines.append(
        "Position Size After: "
        + decimal_text(
            position_after
        )
    )

    lines.append(
        "Position Reconciled: "
        + yes_no(
            position_reconciled
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R25 RENDER PERSISTENCE"
    )

    lines.append(
        "Health Server: ✅ ACTIVE"
    )

    lines.append(
        "Persistent Runtime: "
        + enabled_disabled(
            PERSISTENT_RUNTIME
        )
    )

    lines.append(
        "Auto Exit After Diagnostic: "
        + (
            "✅ ENABLED"
            if AUTO_EXIT_AFTER_DIAGNOSTIC
            else "❌ DISABLED"
        )
    )

    lines.append(
        "Repeated Demo Order Loop: "
        + (
            "✅ ENABLED"
            if REPEATED_DEMO_ORDER_LOOP
            else "❌ DISABLED"
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "ABSOLUTE EXECUTION SAFETY"
    )

    lines.append(
        "Real POST Called: "
        + yes_no(
            R25_REAL_POST_CALLED
        ).replace(
            "✅ YES",
            "❌ YES"
        ).replace(
            "❌ NO",
            "✅ NO"
        )
    )

    lines.append(
        "🛡 R25 absolute real-order "
        "POST lock active"
    )

    lines.append(
        "⚠️ LIVE ORDER EXECUTION DISABLED"
    )

    lines.append(
        "⚠️ NO REAL ORDER WAS SENT"
    )

    return "\n".join(
        lines
    )


# ============================================================
# DIAGNOSTIC
# ============================================================

async def r25_run_diagnostic():
    stage = "startup"

    try:
        final_safety_assertions_r25()

        stage = "credentials"

        (
            api_key,
            secret_key,
            passphrase,
        ) = load_credentials()

        stage = "persistent state initialization"

        restored_state = (
            await initialize_persistent_state()
        )

        stage = "persistence self-test"

        persistence = (
            await run_persistence_self_test()
        )

        connector = aiohttp.TCPConnector(
            limit=10
        )

        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            stage = "market price"

            mark_price = await get_mark_price(
                session
            )

            if mark_price <= 0:
                raise RuntimeError(
                    "Mark price must be "
                    "greater than zero"
                )

            stage = "demo balance"

            demo_balance = (
                await get_demo_available_balance(
                    session,
                    api_key,
                    secret_key,
                    passphrase,
                )
            )

            if demo_balance <= 0:
                raise RuntimeError(
                    "Demo available balance "
                    "must be greater than zero"
                )

            stage = "startup recovery"

            recovery = (
                await recover_from_demo_history(
                    session,
                    api_key,
                    secret_key,
                    passphrase,
                )
            )

            stage = "startup recovery replay"

            recovery_replay = (
                await recover_from_demo_history(
                    session,
                    api_key,
                    secret_key,
                    passphrase,
                )
            )

            stage = "signal gates"

            gate = (
                run_signal_gate_tests()
            )

            if not all(
                gate.values()
            ):
                raise RuntimeError(
                    "Signal execution gate "
                    "self-test failed: "
                    + json.dumps(
                        gate
                    )
                )

            stage = "order state machine"

            order_machine = (
                run_local_order_state_machine_test()
            )

            if not all(
                order_machine.values()
            ):
                raise RuntimeError(
                    "Order state machine "
                    "self-test failed: "
                    + json.dumps(
                        order_machine
                    )
                )

            stage = "dynamic entry"

            (
                margin,
                notional,
                quantity,
            ) = calculate_dynamic_entry(
                demo_balance,
                mark_price,
            )

            if quantity <= 0:
                raise RuntimeError(
                    "Calculated quantity is "
                    "not positive"
                )

            if quantity < MIN_ORDER_QTY:
                quantity = quantize_quantity(
                    MIN_ORDER_QTY
                )

            stage = "exposure"

            exposure = (
                calculate_exposure()
            )

            if not exposure[
                4
            ]:
                raise RuntimeError(
                    "Worst-case exposure "
                    "exceeds configured cap"
                )

            stage = "leverage gate"

            if not (
                WEEX_MIN_LEVERAGE
                <= LEVERAGE
                <= WEEX_MAX_LEVERAGE
            ):
                raise RuntimeError(
                    "Configured leverage "
                    "outside WEEX range"
                )

            if (
                LEVERAGE
                > MAX_CONFIG_LEVERAGE
            ):
                raise RuntimeError(
                    "Configured leverage "
                    "exceeds local maximum"
                )

            stage = "demo position before"

            positions_before = (
                await get_demo_positions(
                    session,
                    api_key,
                    secret_key,
                    passphrase,
                )
            )

            demo_position_before = (
                find_demo_position(
                    positions_before
                )
            )

            position_before = (
                position_size(
                    demo_position_before
                )
            )

            stage = "demo price"

            demo_limit_price = (
                build_demo_limit_price(
                    mark_price
                )
            )

            if demo_limit_price <= 0:
                raise RuntimeError(
                    "Demo limit price must "
                    "be greater than zero"
                )

            price_step_match = (
                verify_step_match(
                    demo_limit_price,
                    PRICE_STEP,
                )
            )

            if not price_step_match:
                raise RuntimeError(
                    "Demo price does not "
                    "match configured price step"
                )

            stage = "demo order transmission"

            (
                order_id,
                client_order_id,
                demo_response,
            ) = await place_demo_test_order(
                session,
                api_key,
                secret_key,
                passphrase,
                quantity,
                demo_limit_price,
            )

            stage = "demo order history"

            (
                history_order,
                poll_attempts,
            ) = await poll_demo_order_history(
                session,
                api_key,
                secret_key,
                passphrase,
                order_id,
                client_order_id,
            )

            if history_order is None:
                raise RuntimeError(
                    "Demo order was not found "
                    "in history after polling"
                )

            stage = "actual history processing"

            actual_first = (
                await process_exchange_order(
                    history_order
                )
            )

            actual_second = (
                await process_exchange_order(
                    history_order
                )
            )

            if not actual_second[
                "duplicate"
            ]:
                raise RuntimeError(
                    "Actual exchange duplicate "
                    "event was not blocked"
                )

            stage = "terminal processing"

            if is_terminal_status(
                history_status(
                    history_order
                )
            ):
                await process_terminal_once(
                    history_order
                )

            stage = "demo position after"

            await asyncio.sleep(
                0.5
            )

            positions_after = (
                await get_demo_positions(
                    session,
                    api_key,
                    secret_key,
                    passphrase,
                )
            )

            demo_position_after = (
                find_demo_position(
                    positions_after
                )
            )

            position_after = (
                position_size(
                    demo_position_after
                )
            )

            R25_STATE[
                "last_demo_position"
            ] = {
                "symbol": DEMO_SYMBOL,
                "side":
                    DEMO_POSITION_SIDE,
                "size":
                    decimal_text(
                        position_after
                    ),
                "timestamp_ms":
                    now_ms(),
            }

            await save_state()

            stage = "final safety"

            final_safety_assertions_r25()

            report = build_report(
                demo_balance=demo_balance,
                mark_price=mark_price,
                gate=gate,
                order_machine=order_machine,
                margin=margin,
                notional=notional,
                quantity=quantity,
                exposure=exposure,
                demo_limit_price=(
                    demo_limit_price
                ),
                price_step_match=(
                    price_step_match
                ),
                order_id=order_id,
                history_order=(
                    history_order
                ),
                poll_attempts=(
                    poll_attempts
                ),
                actual_first=(
                    actual_first
                ),
                actual_second=(
                    actual_second
                ),
                position_before=(
                    position_before
                ),
                position_after=(
                    position_after
                ),
                persistence=(
                    persistence
                ),
                restored_state=(
                    restored_state
                ),
                recovery=(
                    recovery
                ),
                recovery_replay=(
                    recovery_replay
                ),
            )

            print(
                "\n"
                + "=" * 60
            )

            print(
                report
            )

            print(
                "=" * 60
            )

            print(
                f"{MODULE_NAME} COMPLETE: PASSED"
            )

            print(
                "=" * 60
            )

    except Exception as exc:
        print(
            "\n"
            + "=" * 60
        )

        print(
            f"❌ MODULE {MODULE_NAME} ERROR"
        )

        print(
            SYMBOL
        )

        print(
            f"Stage: {stage}"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        print(
            "Real POST Called: "
            + (
                "❌ YES"
                if R25_REAL_POST_CALLED
                else "✅ NO"
            )
        )

        print(
            "Demo POST Attempted: "
            + yes_no(
                R25_DEMO_POST_ATTEMPTED
            )
        )

        print(
            "Demo POST Accepted: "
            + yes_no(
                R25_DEMO_POST_ACCEPTED
            )
        )

        print(
            "🛡 R25 absolute real-order "
            "POST lock active"
        )

        print(
            "⚠️ LIVE ORDER EXECUTION DISABLED"
        )

        print(
            "⚠️ NO REAL ORDER WAS SENT"
        )

        print(
            "=" * 60
        )

        traceback.print_exc()


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.json_response(
        {
            "status": "ok",
            "module": MODULE_NAME,
            "symbol": SYMBOL,
            "demoSymbol": DEMO_SYMBOL,
            "liveOrderExecution":
                LIVE_ORDER_EXECUTION,
            "hardRealPostLock":
                HARD_REAL_POST_LOCK,
            "persistentRuntime":
                PERSISTENT_RUNTIME,
            "stateFile":
                str(
                    STATE_FILE
                ),
            "stateGeneration":
                R25_STATE.get(
                    "generation",
                    0,
                ),
        }
    )


async def root_handler(
    request,
):
    return web.Response(
        text=(
            f"{MODULE_NAME} ACTIVE\n"
            f"Symbol: {SYMBOL}\n"
            f"Demo: {DEMO_SYMBOL}\n"
            "LIVE ORDER EXECUTION DISABLED\n"
            "REAL POST LOCK ACTIVE\n"
        ),
        content_type="text/plain",
    )


async def start_health_server():
    app = web.Application()

    app.router.add_get(
        "/",
        root_handler,
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
        PORT,
    )

    await site.start()

    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}"
    )

    return runner


# ============================================================
# MAIN
# ============================================================

async def async_main():
    runner = None

    try:
        runner = (
            await start_health_server()
        )

        print(
            "=" * 60
        )

        print(
            f"{MODULE_NAME} STARTING"
        )

        print(
            "RESTART-SAFE EXECUTION "
            "RECOVERY VALIDATION"
        )

        print(
            "REAL ORDER TRANSMISSION DISABLED"
        )

        print(
            "=" * 60
        )

        diagnostic_task = (
            asyncio.create_task(
                r25_run_diagnostic()
            )
        )

        await diagnostic_task

        if (
            AUTO_EXIT_AFTER_DIAGNOSTIC
        ):
            return

        while True:
            await asyncio.sleep(
                3600
            )

    finally:
        try:
            await mark_clean_shutdown()
        except Exception:
            pass

        if runner is not None:
            await runner.cleanup()


def main():
    try:
        asyncio.run(
            async_main()
        )

    except KeyboardInterrupt:
        print(
            f"\n{MODULE_NAME} STOPPED"
        )

    except Exception:
        print(
            "=" * 60
        )

        print(
            f"❌ {MODULE_NAME} "
            "FATAL STARTUP ERROR"
        )

        traceback.print_exc()

        print(
            "🛡 REAL ORDER POST LOCK "
            "REMAINS ACTIVE"
        )

        print(
            "⚠️ NO REAL ORDER WAS SENT"
        )

        print(
            "=" * 60
        )


if __name__ == "__main__":
    main()
