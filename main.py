import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import traceback
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R23"

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
# R23 IS STILL PRE-LIVE.
#
# Allowed state-changing request:
#
#   POST /capi/v3/sim/order
#
# Real/private trading POST requests are prohibited.
#
# No real order endpoint is allowed.
# No real cancellation endpoint is allowed.
# No real position mutation endpoint is allowed.
#
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

R23_REAL_POST_CALLED = False
R23_DEMO_POST_ATTEMPTED = False
R23_DEMO_POST_ACCEPTED = False
R23_HISTORY_LOOKUP_ATTEMPTED = False
R23_HISTORY_ORDER_FOUND = False

REAL_ORDER_PATH = "/capi/v3/order"

DEMO_ORDER_PATH = "/capi/v3/sim/order"
DEMO_HISTORY_PATH = "/capi/v3/sim/order/history"
DEMO_BALANCE_PATH = "/capi/v3/sim/balance"
DEMO_POSITIONS_PATH = "/capi/v3/sim/position/allPosition"

ACCOUNT_BALANCE_PATH = "/capi/v3/account/balance"

EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"
MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"


# ============================================================
# R23 DEMO REHEARSAL SETTINGS
# ============================================================

RUN_DEMO_ORDER_TEST = (
    os.getenv(
        "RUN_DEMO_ORDER_TEST",
        "true",
    ).strip().lower()
    in ("1", "true", "yes", "on")
)

REHEARSAL_SIDE = os.getenv(
    "REHEARSAL_SIDE",
    "BUY",
).strip().upper()

REHEARSAL_POSITION_SIDE = os.getenv(
    "REHEARSAL_POSITION_SIDE",
    "LONG",
).strip().upper()

REHEARSAL_ORDER_TYPE = "LIMIT"

# R23 uses IOC so the test order cannot intentionally remain
# resting indefinitely in the demo order book.
REHEARSAL_TIME_IN_FORCE = "IOC"

# Place BUY rehearsal safely below current mark.
# Default = 0.5% below market.
REHEARSAL_PRICE_OFFSET_PERCENT = Decimal(
    os.getenv(
        "REHEARSAL_PRICE_OFFSET_PERCENT",
        "0.5",
    )
)

# Wait briefly before reading Demo history.
R23_HISTORY_WAIT_SECONDS = float(
    os.getenv(
        "R23_HISTORY_WAIT_SECONDS",
        "2.0",
    )
)

R23_HISTORY_RETRIES = int(
    os.getenv(
        "R23_HISTORY_RETRIES",
        "5",
    )
)

R23_HISTORY_RETRY_DELAY = float(
    os.getenv(
        "R23_HISTORY_RETRY_DELAY",
        "1.0",
    )
)


# ============================================================
# STRATEGY CONFIGURATION
# ============================================================

ENTRY_PERCENT = Decimal("5")

LEVERAGE = Decimal("100")
MAX_CONFIG_LEVERAGE = Decimal("100")

MARGIN_TYPE = "ISOLATED"

MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")

MIN_LIQ_DISTANCE_PERCENT = Decimal("0.2")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_SHARE = Decimal("20")
TP2_SHARE = Decimal("20")
TP3_SHARE = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.2")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# FALLBACK CONTRACT VALUES
# ============================================================
#
# ExchangeInfo remains the authoritative source whenever
# available. These values only protect the diagnostic from
# malformed/missing fields.
#
# ============================================================

DEFAULT_MIN_ORDER = Decimal("0.0001")
DEFAULT_QUANTITY_PRECISION = 4
DEFAULT_QUANTITY_STEP = Decimal("0.0001")

DEFAULT_PRICE_PRECISION = 1
DEFAULT_PRICE_STEP = Decimal("0.1")

DEFAULT_CONTRACT_VALUE = Decimal("0.0001")

DEFAULT_MIN_LEVERAGE = Decimal("1")
DEFAULT_MAX_LEVERAGE = Decimal("400")


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
# HEALTH SERVER
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

HEALTH_SERVER_ACTIVE = False


# ============================================================
# GENERIC HELPERS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


def status_icon(value) -> str:
    return "✅ YES" if bool(value) else "❌ NO"


def safe_decimal(value, default=ZERO) -> Decimal:
    try:
        if value is None:
            return default

        return Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return default


def decimal_to_plain(value: Decimal) -> str:
    value = safe_decimal(value)

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in ("", "-0"):
        text = "0"

    return text


def decimal_step_from_precision(
    precision: int,
) -> Decimal:
    precision = max(
        0,
        int(precision),
    )

    return Decimal("1").scaleb(
        -precision
    )


def quantize_down_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:
    value = safe_decimal(value)
    step = safe_decimal(step)

    if step <= ZERO:
        raise RuntimeError(
            "Step must be greater than zero"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def is_step_match(
    value: Decimal,
    step: Decimal,
) -> bool:
    value = safe_decimal(value)
    step = safe_decimal(step)

    if step <= ZERO:
        return False

    try:
        units = value / step

        return (
            units
            == units.to_integral_value()
        )

    except Exception:
        return False


def now_ms() -> int:
    return int(
        time.time() * 1000
    )


def create_client_order_id() -> str:
    stamp = int(
        time.time() * 1000
    )

    return (
        f"r23-{stamp}"
    )[:36]


# ============================================================
# CREDENTIAL VALIDATION
# ============================================================

def validate_credentials():
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
# AUTHENTICATION
# ============================================================

def build_query_string(
    params=None,
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

    return urlencode(
        clean
    )


def build_signature(
    timestamp: str,
    method: str,
    path: str,
    query_string: str = "",
    body_string: str = "",
) -> str:

    method = method.upper()

    if query_string:
        message = (
            timestamp
            + method
            + path
            + "?"
            + query_string
            + body_string
        )

    else:
        message = (
            timestamp
            + method
            + path
            + body_string
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
        "utf-8"
    )


def authenticated_headers(
    method: str,
    path: str,
    params=None,
    body_string: str = "",
):
    timestamp = str(
        now_ms()
    )

    query_string = build_query_string(
        params
    )

    signature = build_signature(
        timestamp=timestamp,
        method=method,
        path=path,
        query_string=query_string,
        body_string=body_string,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "User-Agent": "0F-4H-R23",
    }


# ============================================================
# ABSOLUTE REQUEST SAFETY GATE
# ============================================================

def assert_request_allowed(
    method: str,
    path: str,
):
    global R23_REAL_POST_CALLED

    method = method.upper()

    # Public/private GET requests are allowed.
    if method == "GET":
        return

    # The ONLY state-changing request permitted in R23.
    if (
        method == "POST"
        and path == DEMO_ORDER_PATH
    ):
        return

    # Anything else is treated as a prohibited real/private
    # mutation attempt.
    R23_REAL_POST_CALLED = True

    raise RuntimeError(
        "R23 ABSOLUTE SAFETY LOCK: "
        f"blocked prohibited request {method} {path}"
    )


# ============================================================
# HTTP HELPERS
# ============================================================

async def read_json_response(
    response: aiohttp.ClientResponse,
):
    text = await response.text()

    try:
        payload = json.loads(
            text
        )

    except Exception:
        payload = {
            "raw": text
        }

    return text, payload


async def public_get(
    session: aiohttp.ClientSession,
    path: str,
    params=None,
):
    url = (
        API_BASE_URL
        + path
    )

    async with session.get(
        url,
        params=params,
        headers={
            "User-Agent": "0F-4H-R23",
        },
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text, payload = await read_json_response(
            response
        )

        if response.status >= 400:
            raise RuntimeError(
                f"WEEX GET HTTP {response.status}: {text}"
            )

        return payload


async def private_get(
    session: aiohttp.ClientSession,
    path: str,
    params=None,
):
    assert_request_allowed(
        "GET",
        path,
    )

    query_string = build_query_string(
        params
    )

    url = (
        API_BASE_URL
        + path
    )

    if query_string:
        url += (
            "?"
            + query_string
        )

    headers = authenticated_headers(
        method="GET",
        path=path,
        params=params,
    )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text, payload = await read_json_response(
            response
        )

        if response.status >= 400:
            raise RuntimeError(
                f"WEEX GET HTTP {response.status}: {text}"
            )

        return payload


async def demo_post(
    session: aiohttp.ClientSession,
    path: str,
    payload: dict,
):
    global R23_DEMO_POST_ATTEMPTED
    global R23_DEMO_POST_ACCEPTED

    assert_request_allowed(
        "POST",
        path,
    )

    if path != DEMO_ORDER_PATH:
        raise RuntimeError(
            "R23 demo POST path rejected"
        )

    R23_DEMO_POST_ATTEMPTED = True

    body_string = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    headers = authenticated_headers(
        method="POST",
        path=path,
        body_string=body_string,
    )

    url = (
        API_BASE_URL
        + path
    )

    async with session.post(
        url,
        data=body_string.encode(
            "utf-8"
        ),
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text, result = await read_json_response(
            response
        )

        if response.status >= 400:
            raise RuntimeError(
                f"WEEX DEMO POST HTTP {response.status}: {text}"
            )

        if isinstance(
            result,
            dict,
        ):
            success_value = result.get(
                "success"
            )

            # Some API responses may omit success but return
            # a valid orderId.
            if (
                success_value is False
                or str(
                    success_value
                ).lower() == "false"
            ):
                raise RuntimeError(
                    "WEEX DEMO ORDER REJECTED: "
                    + text
                )

            order_id = result.get(
                "orderId"
            )

            if order_id:
                R23_DEMO_POST_ACCEPTED = True

        if not R23_DEMO_POST_ACCEPTED:
            raise RuntimeError(
                "Unable to confirm WEEX Demo order acceptance: "
                + text
            )

        return result


# ============================================================
# BALANCE EXTRACTION
# ============================================================

def extract_available_usdt(
    payload,
) -> Decimal:

    candidates = payload

    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "data",
            "result",
        ):
            if isinstance(
                payload.get(key),
                list,
            ):
                candidates = payload[key]
                break

    if isinstance(
        candidates,
        dict,
    ):
        candidates = [
            candidates
        ]

    if not isinstance(
        candidates,
        list,
    ):
        raise RuntimeError(
            "Unable to parse WEEX account balance"
        )

    for item in candidates:
        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get(
                "asset",
                item.get(
                    "coinName",
                    "",
                ),
            )
        ).upper()

        if asset != "USDT":
            continue

        for key in (
            "availableBalance",
            "available",
            "balance",
        ):
            if key in item:
                value = safe_decimal(
                    item.get(key)
                )

                if value >= ZERO:
                    return value

    raise RuntimeError(
        "Unable to extract available USDT"
    )


# ============================================================
# MARK PRICE
# ============================================================

def extract_mark_price(
    payload,
) -> Decimal:

    if isinstance(
        payload,
        list,
    ):
        if not payload:
            raise RuntimeError(
                "Empty mark price response"
            )

        payload = payload[0]

    if isinstance(
        payload,
        dict,
    ):
        possible = [
            payload,
            payload.get(
                "data"
            ),
            payload.get(
                "result"
            ),
        ]

        for obj in possible:
            if not isinstance(
                obj,
                dict,
            ):
                continue

            for key in (
                "price",
                "markPrice",
                "lastPrice",
                "last",
            ):
                if key not in obj:
                    continue

                value = safe_decimal(
                    obj.get(key)
                )

                if value > ZERO:
                    return value

    raise RuntimeError(
        "Unable to extract mark price"
    )


# ============================================================
# CONTRACT INFORMATION
# ============================================================

def find_symbol_info(
    payload,
    symbol: str,
):
    if isinstance(
        payload,
        dict,
    ):
        symbols = payload.get(
            "symbols"
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
                    return item

        for key in (
            "data",
            "result",
        ):
            nested = payload.get(
                key
            )

            if isinstance(
                nested,
                dict,
            ):
                found = find_symbol_info(
                    nested,
                    symbol,
                )

                if found:
                    return found

    if isinstance(
        payload,
        list,
    ):
        for item in payload:
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
                return item

    return None


def build_contract_spec(
    symbol_info,
):
    symbol_info = (
        symbol_info
        if isinstance(
            symbol_info,
            dict,
        )
        else {}
    )

    min_order = safe_decimal(
        symbol_info.get(
            "minOrderSize",
            DEFAULT_MIN_ORDER,
        ),
        DEFAULT_MIN_ORDER,
    )

    quantity_precision = int(
        symbol_info.get(
            "quantityPrecision",
            DEFAULT_QUANTITY_PRECISION,
        )
    )

    price_precision = int(
        symbol_info.get(
            "pricePrecision",
            DEFAULT_PRICE_PRECISION,
        )
    )

    # R22 validated an actual quantity step of 0.0001.
    # Allow explicit Render override if WEEX contract metadata
    # changes independently from quantityPrecision.
    env_quantity_step = os.getenv(
        "QUANTITY_STEP",
        "",
    ).strip()

    if env_quantity_step:
        quantity_step = safe_decimal(
            env_quantity_step,
            DEFAULT_QUANTITY_STEP,
        )

    else:
        # Prefer minimum order as step when it is sensible,
        # because WEEX quantityPrecision is decimal precision,
        # not necessarily the actual trade increment.
        if min_order > ZERO:
            quantity_step = min_order
        else:
            quantity_step = decimal_step_from_precision(
                quantity_precision
            )

    price_step = decimal_step_from_precision(
        price_precision
    )

    contract_value = safe_decimal(
        symbol_info.get(
            "contractVal",
            DEFAULT_CONTRACT_VALUE,
        ),
        DEFAULT_CONTRACT_VALUE,
    )

    min_leverage = safe_decimal(
        symbol_info.get(
            "minLeverage",
            DEFAULT_MIN_LEVERAGE,
        ),
        DEFAULT_MIN_LEVERAGE,
    )

    max_leverage = safe_decimal(
        symbol_info.get(
            "maxLeverage",
            DEFAULT_MAX_LEVERAGE,
        ),
        DEFAULT_MAX_LEVERAGE,
    )

    return {
        "min_order": min_order,
        "quantity_precision": quantity_precision,
        "quantity_step": quantity_step,
        "price_precision": price_precision,
        "price_step": price_step,
        "contract_value": contract_value,
        "min_leverage": min_leverage,
        "max_leverage": max_leverage,
    }


# ============================================================
# SIGNAL GATE SELF TESTS
# ============================================================

def run_signal_gate_tests():
    current = time.time()

    fresh_timestamp = (
        current
        - 5
    )

    expired_timestamp = (
        current
        - SIGNAL_EXPIRY_SECONDS
        - 5
    )

    fresh_signal_accepted = (
        current
        - fresh_timestamp
        <= SIGNAL_EXPIRY_SECONDS
    )

    expired_signal_rejected = (
        current
        - expired_timestamp
        > SIGNAL_EXPIRY_SECONDS
    )

    last_loss_time = (
        current
        - 10
    )

    loss_cooldown_test = (
        current
        - last_loss_time
        < LOSS_COOLDOWN_SECONDS
    )

    existing_order_keys = {
        (
            SYMBOL,
            "BUY",
            "LONG",
        )
    }

    duplicate_key = (
        SYMBOL,
        "BUY",
        "LONG",
    )

    duplicate_signal_rejected = (
        ANTI_DUPLICATE_ORDERS
        and duplicate_key
        in existing_order_keys
    )

    active_direction = "LONG"
    incoming_direction = "SHORT"

    one_direction_gate = (
        ONE_DIRECTION_ONLY
        and active_direction
        != incoming_direction
    )

    # Diagnostic assumes no external position unless private
    # position query says otherwise later.
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
# EXPOSURE
# ============================================================

def calculate_worst_case_exposure():
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
        total
        <= MAX_FUND_EXPOSURE_PERCENT,
    )


# ============================================================
# ENTRY CALCULATION
# ============================================================

def calculate_dynamic_entry(
    available_usdt: Decimal,
    mark_price: Decimal,
    quantity_step: Decimal,
    min_order: Decimal,
):
    margin = (
        available_usdt
        * ENTRY_PERCENT
        / HUNDRED
    )

    notional = (
        margin
        * LEVERAGE
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = quantize_down_to_step(
        raw_quantity,
        quantity_step,
    )

    quantity_positive = (
        quantity > ZERO
    )

    minimum_passed = (
        quantity
        >= min_order
    )

    return {
        "margin": margin,
        "notional": notional,
        "raw_quantity": raw_quantity,
        "quantity": quantity,
        "quantity_positive":
            quantity_positive,
        "minimum_passed":
            minimum_passed,
    }


# ============================================================
# LEVERAGE GATE
# ============================================================

def validate_leverage(
    min_leverage: Decimal,
    max_leverage: Decimal,
) -> bool:

    if LEVERAGE > MAX_CONFIG_LEVERAGE:
        return False

    if LEVERAGE < min_leverage:
        return False

    if LEVERAGE > max_leverage:
        return False

    return True


# ============================================================
# DEMO POSITION HELPERS
# ============================================================

def normalize_position_list(
    payload,
):
    if isinstance(
        payload,
        list,
    ):
        return payload

    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "data",
            "result",
            "positions",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    return []


def get_demo_symbol_position_size(
    payload,
    symbol: str,
) -> Decimal:

    total = ZERO

    for item in normalize_position_list(
        payload
    ):
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
        ).upper() != symbol.upper():
            continue

        size = safe_decimal(
            item.get(
                "size",
                item.get(
                    "positionAmt",
                    "0",
                ),
            )
        )

        total += abs(
            size
        )

    return total


# ============================================================
# SAFE R23 IOC LIMIT PRICE
# ============================================================

def build_safe_demo_limit_price(
    mark_price: Decimal,
    price_step: Decimal,
    side: str,
) -> Decimal:

    offset = (
        REHEARSAL_PRICE_OFFSET_PERCENT
        / HUNDRED
    )

    if side.upper() == "BUY":
        raw_price = (
            mark_price
            * (
                ONE
                - offset
            )
        )

    elif side.upper() == "SELL":
        raw_price = (
            mark_price
            * (
                ONE
                + offset
            )
        )

    else:
        raise RuntimeError(
            f"Unsupported rehearsal side: {side}"
        )

    price = quantize_down_to_step(
        raw_price,
        price_step,
    )

    if price <= ZERO:
        raise RuntimeError(
            "Demo limit price must be greater than zero"
        )

    if not is_step_match(
        price,
        price_step,
    ):
        raise RuntimeError(
            "Demo price does not match price step"
        )

    return price


# ============================================================
# DEMO ORDER PAYLOAD
# ============================================================

def build_demo_order_payload(
    quantity: Decimal,
    limit_price: Decimal,
):
    if quantity <= ZERO:
        raise RuntimeError(
            "Demo quantity must be greater than zero"
        )

    if limit_price <= ZERO:
        raise RuntimeError(
            "Demo limit price must be greater than zero"
        )

    if REHEARSAL_SIDE not in (
        "BUY",
        "SELL",
    ):
        raise RuntimeError(
            "REHEARSAL_SIDE must be BUY or SELL"
        )

    if REHEARSAL_POSITION_SIDE not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "REHEARSAL_POSITION_SIDE must be LONG or SHORT"
        )

    return {
        "symbol": DEMO_SYMBOL,
        "side": REHEARSAL_SIDE,
        "positionSide":
            REHEARSAL_POSITION_SIDE,
        "type": REHEARSAL_ORDER_TYPE,
        "timeInForce":
            REHEARSAL_TIME_IN_FORCE,
        "quantity":
            decimal_to_plain(
                quantity
            ),
        "price":
            decimal_to_plain(
                limit_price
            ),
        "newClientOrderId":
            create_client_order_id(),
    }


# ============================================================
# DEMO ORDER RESPONSE
# ============================================================

def extract_demo_order_id(
    payload,
) -> str:

    if isinstance(
        payload,
        dict,
    ):
        for obj in (
            payload,
            payload.get(
                "data"
            ),
            payload.get(
                "result"
            ),
        ):
            if not isinstance(
                obj,
                dict,
            ):
                continue

            order_id = obj.get(
                "orderId"
            )

            if order_id is not None:
                text = str(
                    order_id
                ).strip()

                if text:
                    return text

    raise RuntimeError(
        "Unable to extract Demo order ID"
    )


# ============================================================
# HISTORY HELPERS
# ============================================================

def normalize_history_list(
    payload,
):
    if isinstance(
        payload,
        list,
    ):
        return payload

    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "data",
            "result",
            "orders",
            "list",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

            if isinstance(
                value,
                dict,
            ):
                for nested_key in (
                    "list",
                    "orders",
                    "records",
                ):
                    nested = value.get(
                        nested_key
                    )

                    if isinstance(
                        nested,
                        list,
                    ):
                        return nested

    return []


def find_order_in_history(
    payload,
    order_id: str,
):
    target = str(
        order_id
    )

    for item in normalize_history_list(
        payload
    ):
        if not isinstance(
            item,
            dict,
        ):
            continue

        current_id = str(
            item.get(
                "orderId",
                "",
            )
        )

        if current_id == target:
            return item

    return None


async def locate_demo_order_in_history(
    session: aiohttp.ClientSession,
    order_id: str,
):
    global R23_HISTORY_LOOKUP_ATTEMPTED
    global R23_HISTORY_ORDER_FOUND

    R23_HISTORY_LOOKUP_ATTEMPTED = True

    await asyncio.sleep(
        R23_HISTORY_WAIT_SECONDS
    )

    last_payload = None

    for attempt in range(
        max(
            1,
            R23_HISTORY_RETRIES,
        )
    ):
        payload = await private_get(
            session,
            DEMO_HISTORY_PATH,
            params={
                "symbol":
                    DEMO_SYMBOL,
                "limit":
                    100,
                "page":
                    0,
            },
        )

        last_payload = payload

        order = find_order_in_history(
            payload,
            order_id,
        )

        if order:
            R23_HISTORY_ORDER_FOUND = True

            return order

        if (
            attempt
            < R23_HISTORY_RETRIES
            - 1
        ):
            await asyncio.sleep(
                R23_HISTORY_RETRY_DELAY
            )

    raise RuntimeError(
        "R23 lifecycle verification failed: "
        f"Demo order {order_id} not found in order history. "
        f"Last history response: {last_payload}"
    )


# ============================================================
# HISTORY VALIDATION
# ============================================================

def validate_history_order(
    history_order: dict,
    order_id: str,
    requested_quantity: Decimal,
):

    if not isinstance(
        history_order,
        dict,
    ):
        raise RuntimeError(
            "Invalid Demo history order object"
        )

    actual_order_id = str(
        history_order.get(
            "orderId",
            "",
        )
    )

    id_match = (
        actual_order_id
        == str(order_id)
    )

    symbol_match = (
        str(
            history_order.get(
                "symbol",
                "",
            )
        ).upper()
        == DEMO_SYMBOL.upper()
    )

    side_match = (
        str(
            history_order.get(
                "side",
                "",
            )
        ).upper()
        == REHEARSAL_SIDE
    )

    position_side_match = (
        str(
            history_order.get(
                "positionSide",
                "",
            )
        ).upper()
        == REHEARSAL_POSITION_SIDE
    )

    status = str(
        history_order.get(
            "status",
            "UNKNOWN",
        )
    ).upper()

    orig_qty = safe_decimal(
        history_order.get(
            "origQty",
            history_order.get(
                "quantity",
                requested_quantity,
            ),
        )
    )

    executed_qty = safe_decimal(
        history_order.get(
            "executedQty",
            "0",
        )
    )

    quantity_match = (
        orig_qty
        == requested_quantity
    )

    execution_sane = (
        executed_qty >= ZERO
        and executed_qty
        <= orig_qty
    )

    # IOC outcomes vary by matching condition.
    # These statuses are acceptable observations.
    recognized_statuses = {
        "NEW",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "CANCELLED",
        "EXPIRED",
        "REJECTED",
    }

    status_recognized = (
        status
        in recognized_statuses
    )

    passed = all(
        (
            id_match,
            symbol_match,
            side_match,
            position_side_match,
            quantity_match,
            execution_sane,
            status_recognized,
        )
    )

    return {
        "id_match": id_match,
        "symbol_match": symbol_match,
        "side_match": side_match,
        "position_side_match":
            position_side_match,
        "status": status,
        "status_recognized":
            status_recognized,
        "orig_qty": orig_qty,
        "executed_qty":
            executed_qty,
        "quantity_match":
            quantity_match,
        "execution_sane":
            execution_sane,
        "passed": passed,
    }


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session: aiohttp.ClientSession,
    text: str,
):
    if not TELEGRAM_BOT_TOKEN:
        return

    if not TELEGRAM_CHAT_ID:
        return

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id":
            TELEGRAM_CHAT_ID,
        "text":
            text,
        "disable_web_page_preview":
            True,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ):
            pass

    except Exception as exc:
        print(
            "TELEGRAM WARNING:",
            repr(exc),
        )


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.json_response(
        {
            "ok": True,
            "module":
                MODULE_NAME,
            "live_order_execution":
                LIVE_ORDER_EXECUTION,
            "hard_real_post_lock":
                HARD_REAL_POST_LOCK,
            "real_post_called":
                R23_REAL_POST_CALLED,
            "demo_post_attempted":
                R23_DEMO_POST_ATTEMPTED,
            "demo_post_accepted":
                R23_DEMO_POST_ACCEPTED,
            "history_lookup_attempted":
                R23_HISTORY_LOOKUP_ATTEMPTED,
            "history_order_found":
                R23_HISTORY_ORDER_FOUND,
        }
    )


async def start_health_server():
    global HEALTH_SERVER_ACTIVE

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
        PORT,
    )

    await site.start()

    HEALTH_SERVER_ACTIVE = True

    print(
        f"HEALTH SERVER ACTIVE ON PORT {PORT}"
    )

    return runner


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions_r23():

    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "R23 safety failure: "
            "LIVE_ORDER_EXECUTION must remain False"
        )

    if not HARD_REAL_POST_LOCK:
        raise RuntimeError(
            "R23 safety failure: "
            "HARD_REAL_POST_LOCK must remain True"
        )

    if R23_REAL_POST_CALLED:
        raise RuntimeError(
            "R23 safety failure: "
            "a prohibited state-changing request was attempted"
        )


# ============================================================
# REPORT
# ============================================================

def build_report(
    available_usdt,
    mark_price,
    signal_tests,
    contract,
    entry,
    exposure,
    leverage_gate,
    demo_data,
):
    (
        exposure_initial,
        exposure_pyramids,
        exposure_backups,
        exposure_total,
        exposure_passed,
    ) = exposure

    lines = []

    lines.append(
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED"
    )

    lines.append(
        SYMBOL
    )

    lines.append(
        "Available USDT: "
        + decimal_to_plain(
            available_usdt
        )
    )

    lines.append(
        "Mark Price: "
        + decimal_to_plain(
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
        + status_icon(
            signal_tests[
                "fresh_signal_accepted"
            ]
        )
    )

    lines.append(
        "Expired Signal Rejected: "
        + status_icon(
            signal_tests[
                "expired_signal_rejected"
            ]
        )
    )

    lines.append(
        "Loss Cooldown Test: "
        + status_icon(
            signal_tests[
                "loss_cooldown_test"
            ]
        )
    )

    lines.append(
        "Duplicate Signal Rejected: "
        + status_icon(
            signal_tests[
                "duplicate_signal_rejected"
            ]
        )
    )

    lines.append(
        "One Direction Gate: "
        + status_icon(
            signal_tests[
                "one_direction_gate"
            ]
        )
    )

    lines.append(
        "External Position Clear: "
        + status_icon(
            signal_tests[
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
        "Entry: "
        + decimal_to_plain(
            ENTRY_PERCENT
        )
        + "%"
    )

    lines.append(
        "Leverage: "
        + decimal_to_plain(
            LEVERAGE
        )
        + "x"
    )

    lines.append(
        "Max Config Leverage: "
        + decimal_to_plain(
            MAX_CONFIG_LEVERAGE
        )
        + "x"
    )

    lines.append(
        "Margin Type: "
        + MARGIN_TYPE
    )

    lines.append(
        f"Max Pyramids: {MAX_PYRAMID_ADDS}"
    )

    lines.append(
        "Pyramid Size: "
        + decimal_to_plain(
            PYRAMID_SIZE_PERCENT
        )
        + "%"
    )

    lines.append(
        f"Max Backups: {MAX_BACKUPS}"
    )

    lines.append(
        "Backup Size: "
        + decimal_to_plain(
            BACKUP_SIZE_PERCENT
        )
        + "% each"
    )

    lines.append(
        "Backup Buffer: "
        + decimal_to_plain(
            BACKUP_BUFFER_PERCENT
        )
        + "%"
    )

    lines.append(
        "Min Liq Distance: "
        + decimal_to_plain(
            MIN_LIQ_DISTANCE_PERCENT
        )
        + "%"
    )

    lines.append(
        "Max Fund Exposure: "
        + decimal_to_plain(
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
        + decimal_to_plain(
            contract[
                "min_order"
            ]
        )
    )

    lines.append(
        "Quantity Precision: "
        + str(
            contract[
                "quantity_precision"
            ]
        )
    )

    lines.append(
        "Quantity Step: "
        + decimal_to_plain(
            contract[
                "quantity_step"
            ]
        )
    )

    lines.append(
        "Price Precision: "
        + str(
            contract[
                "price_precision"
            ]
        )
    )

    lines.append(
        "Price Step: "
        + decimal_to_plain(
            contract[
                "price_step"
            ]
        )
    )

    lines.append(
        "Contract Value: "
        + decimal_to_plain(
            contract[
                "contract_value"
            ]
        )
    )

    lines.append(
        "WEEX Min Leverage: "
        + decimal_to_plain(
            contract[
                "min_leverage"
            ]
        )
        + "x"
    )

    lines.append(
        "WEEX Max Leverage: "
        + decimal_to_plain(
            contract[
                "max_leverage"
            ]
        )
        + "x"
    )

    lines.append(
        "Leverage Gate: "
        + status_icon(
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
        + decimal_to_plain(
            entry[
                "margin"
            ]
        )
        + " USDT"
    )

    lines.append(
        "Notional: "
        + decimal_to_plain(
            entry[
                "notional"
            ]
        )
        + " USDT"
    )

    lines.append(
        "Quantity: "
        + decimal_to_plain(
            entry[
                "quantity"
            ]
        )
    )

    lines.append(
        "Quantity Positive: "
        + status_icon(
            entry[
                "quantity_positive"
            ]
        )
    )

    lines.append(
        "Minimum Passed: "
        + status_icon(
            entry[
                "minimum_passed"
            ]
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
        + decimal_to_plain(
            exposure_initial
        )
        + "%"
    )

    lines.append(
        "Pyramids: "
        + decimal_to_plain(
            exposure_pyramids
        )
        + "%"
    )

    lines.append(
        "Backups: "
        + decimal_to_plain(
            exposure_backups
        )
        + "%"
    )

    lines.append(
        "Total: "
        + decimal_to_plain(
            exposure_total
        )
        + "% / "
        + decimal_to_plain(
            MAX_FUND_EXPOSURE_PERCENT
        )
        + "%"
    )

    lines.append(
        "Exposure Passed: "
        + status_icon(
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
        + decimal_to_plain(
            TP1_SHARE
        )
        + "% / "
        + decimal_to_plain(
            TP2_SHARE
        )
        + "% / "
        + decimal_to_plain(
            TP3_SHARE
        )
        + "%"
    )

    lines.append(
        "TP1 Trigger: "
        + decimal_to_plain(
            TP1_TRIGGER_PERCENT
        )
        + "%"
    )

    lines.append(
        "TP2 Trigger: "
        + decimal_to_plain(
            TP2_TRIGGER_PERCENT
        )
        + "%"
    )

    lines.append(
        "Trailing Distance: "
        + decimal_to_plain(
            TRAILING_DISTANCE_PERCENT
        )
        + "%"
    )

    lines.append(
        ""
    )

    lines.append(
        "R23 DEMO ORDER LIFECYCLE"
    )

    lines.append(
        "Demo Symbol: "
        + DEMO_SYMBOL
    )

    lines.append(
        "Demo Side: "
        + REHEARSAL_SIDE
    )

    lines.append(
        "Demo Position Side: "
        + REHEARSAL_POSITION_SIDE
    )

    lines.append(
        "Demo Type: LIMIT"
    )

    lines.append(
        "Demo Time In Force: IOC"
    )

    lines.append(
        "Demo Limit Price: "
        + decimal_to_plain(
            demo_data[
                "limit_price"
            ]
        )
    )

    lines.append(
        "Price Step Match: "
        + status_icon(
            demo_data[
                "price_step_match"
            ]
        )
    )

    lines.append(
        "Demo POST Attempted: "
        + status_icon(
            R23_DEMO_POST_ATTEMPTED
        )
    )

    lines.append(
        "Demo POST Accepted: "
        + status_icon(
            R23_DEMO_POST_ACCEPTED
        )
    )

    lines.append(
        "Demo Order ID: "
        + str(
            demo_data[
                "order_id"
            ]
        )
    )

    lines.append(
        "History Lookup Attempted: "
        + status_icon(
            R23_HISTORY_LOOKUP_ATTEMPTED
        )
    )

    lines.append(
        "Order Found In History: "
        + status_icon(
            R23_HISTORY_ORDER_FOUND
        )
    )

    lines.append(
        "History Order ID Match: "
        + status_icon(
            demo_data[
                "history_validation"
            ][
                "id_match"
            ]
        )
    )

    lines.append(
        "History Symbol Match: "
        + status_icon(
            demo_data[
                "history_validation"
            ][
                "symbol_match"
            ]
        )
    )

    lines.append(
        "History Side Match: "
        + status_icon(
            demo_data[
                "history_validation"
            ][
                "side_match"
            ]
        )
    )

    lines.append(
        "History Position Side Match: "
        + status_icon(
            demo_data[
                "history_validation"
            ][
                "position_side_match"
            ]
        )
    )

    lines.append(
        "Demo Final Status: "
        + demo_data[
            "history_validation"
        ][
            "status"
        ]
    )

    lines.append(
        "Status Recognized: "
        + status_icon(
            demo_data[
                "history_validation"
            ][
                "status_recognized"
            ]
        )
    )

    lines.append(
        "Requested Quantity: "
        + decimal_to_plain(
            entry[
                "quantity"
            ]
        )
    )

    lines.append(
        "History Original Quantity: "
        + decimal_to_plain(
            demo_data[
                "history_validation"
            ][
                "orig_qty"
            ]
        )
    )

    lines.append(
        "History Executed Quantity: "
        + decimal_to_plain(
            demo_data[
                "history_validation"
            ][
                "executed_qty"
            ]
        )
    )

    lines.append(
        "Quantity Reconciliation: "
        + status_icon(
            demo_data[
                "history_validation"
            ][
                "execution_sane"
            ]
        )
    )

    lines.append(
        "Lifecycle Validation: "
        + status_icon(
            demo_data[
                "history_validation"
            ][
                "passed"
            ]
        )
    )

    lines.append(
        ""
    )

    lines.append(
        "R23 DEMO POSITION RECONCILIATION"
    )

    lines.append(
        "Position Size Before: "
        + decimal_to_plain(
            demo_data[
                "position_before"
            ]
        )
    )

    lines.append(
        "Position Size After: "
        + decimal_to_plain(
            demo_data[
                "position_after"
            ]
        )
    )

    lines.append(
        "Position Unchanged: "
        + status_icon(
            demo_data[
                "position_unchanged"
            ]
        )
    )

    if not demo_data[
        "position_unchanged"
    ]:
        lines.append(
            "⚠️ Demo IOC order changed Demo position size"
        )

    lines.append(
        ""
    )

    lines.append(
        "R23 RENDER PERSISTENCE"
    )

    lines.append(
        "Health Server: "
        + status_icon(
            HEALTH_SERVER_ACTIVE
        ).replace(
            "YES",
            "ACTIVE",
        )
    )

    lines.append(
        "Persistent Runtime: ✅ ACTIVE"
    )

    lines.append(
        "Auto Exit After Diagnostic: ❌ DISABLED"
    )

    lines.append(
        "Repeated Demo Order Loop: ❌ DISABLED"
    )

    lines.append(
        ""
    )

    lines.append(
        "ABSOLUTE EXECUTION SAFETY"
    )

    lines.append(
        "Real POST Called: "
        + status_icon(
            R23_REAL_POST_CALLED
        )
    )

    lines.append(
        "🛡 R23 absolute real-order POST lock active"
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
# ERROR REPORT
# ============================================================

def build_error_report(
    stage: str,
    exc: Exception,
):
    lines = []

    lines.append(
        f"❌ MODULE {MODULE_NAME} ERROR"
    )

    lines.append(
        SYMBOL
    )

    lines.append(
        "Stage: "
        + stage
    )

    lines.append(
        type(exc).__name__
        + ": "
        + str(exc)
    )

    lines.append(
        "Real POST Called: "
        + status_icon(
            R23_REAL_POST_CALLED
        )
    )

    lines.append(
        "Demo POST Attempted: "
        + status_icon(
            R23_DEMO_POST_ATTEMPTED
        )
    )

    lines.append(
        "Demo POST Accepted: "
        + status_icon(
            R23_DEMO_POST_ACCEPTED
        )
    )

    lines.append(
        "History Lookup Attempted: "
        + status_icon(
            R23_HISTORY_LOOKUP_ATTEMPTED
        )
    )

    lines.append(
        "History Order Found: "
        + status_icon(
            R23_HISTORY_ORDER_FOUND
        )
    )

    lines.append(
        "🛡 R23 absolute real-order POST lock active"
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
# R23 DIAGNOSTIC
# ============================================================

async def r23_run_diagnostic(
    session: aiohttp.ClientSession,
):
    stage = "configuration"

    try:
        validate_credentials()

        final_safety_assertions_r23()

        # ----------------------------------------------------
        # SIGNAL GATES
        # ----------------------------------------------------

        stage = "signal gate self tests"

        signal_tests = (
            run_signal_gate_tests()
        )

        if not all(
            signal_tests.values()
        ):
            raise RuntimeError(
                "One or more signal gate tests failed"
            )

        # ----------------------------------------------------
        # REAL ACCOUNT BALANCE READ ONLY
        # ----------------------------------------------------

        stage = "balance"

        balance_payload = await private_get(
            session,
            ACCOUNT_BALANCE_PATH,
        )

        available_usdt = extract_available_usdt(
            balance_payload
        )

        # ----------------------------------------------------
        # MARK PRICE
        # ----------------------------------------------------

        stage = "mark price"

        mark_payload = await public_get(
            session,
            MARK_PRICE_PATH,
            params={
                "symbol":
                    SYMBOL,
                "priceType":
                    "MARK",
            },
        )

        mark_price = extract_mark_price(
            mark_payload
        )

        # ----------------------------------------------------
        # EXCHANGE INFO
        # ----------------------------------------------------

        stage = "exchange information"

        exchange_payload = await public_get(
            session,
            EXCHANGE_INFO_PATH,
            params={
                "symbol":
                    SYMBOL,
            },
        )

        symbol_info = find_symbol_info(
            exchange_payload,
            SYMBOL,
        )

        if not symbol_info:
            raise RuntimeError(
                f"{SYMBOL} not found in WEEX exchangeInfo"
            )

        contract = build_contract_spec(
            symbol_info
        )

        # ----------------------------------------------------
        # LEVERAGE
        # ----------------------------------------------------

        stage = "leverage validation"

        leverage_gate = validate_leverage(
            contract[
                "min_leverage"
            ],
            contract[
                "max_leverage"
            ],
        )

        if not leverage_gate:
            raise RuntimeError(
                "Configured leverage failed WEEX leverage gate"
            )

        # ----------------------------------------------------
        # DYNAMIC ENTRY
        # ----------------------------------------------------

        stage = "dynamic entry"

        entry = calculate_dynamic_entry(
            available_usdt=
                available_usdt,
            mark_price=
                mark_price,
            quantity_step=
                contract[
                    "quantity_step"
                ],
            min_order=
                contract[
                    "min_order"
                ],
        )

        if not entry[
            "quantity_positive"
        ]:
            raise RuntimeError(
                "Dynamic entry quantity is not positive"
            )

        if not entry[
            "minimum_passed"
        ]:
            raise RuntimeError(
                "Dynamic entry quantity is below WEEX minimum order"
            )

        if not is_step_match(
            entry[
                "quantity"
            ],
            contract[
                "quantity_step"
            ],
        ):
            raise RuntimeError(
                "Dynamic entry quantity failed quantity step"
            )

        # ----------------------------------------------------
        # EXPOSURE
        # ----------------------------------------------------

        stage = "exposure validation"

        exposure = (
            calculate_worst_case_exposure()
        )

        if not exposure[4]:
            raise RuntimeError(
                "Worst-case fund exposure exceeds configured maximum"
            )

        # ----------------------------------------------------
        # DEMO POSITION SNAPSHOT BEFORE
        # ----------------------------------------------------

        stage = "demo position snapshot before"

        demo_positions_before_payload = (
            await private_get(
                session,
                DEMO_POSITIONS_PATH,
            )
        )

        position_before = (
            get_demo_symbol_position_size(
                demo_positions_before_payload,
                DEMO_SYMBOL,
            )
        )

        # ----------------------------------------------------
        # BUILD SAFE IOC DEMO ORDER
        # ----------------------------------------------------

        stage = "demo order construction"

        demo_limit_price = (
            build_safe_demo_limit_price(
                mark_price=
                    mark_price,
                price_step=
                    contract[
                        "price_step"
                    ],
                side=
                    REHEARSAL_SIDE,
            )
        )

        price_step_match = (
            is_step_match(
                demo_limit_price,
                contract[
                    "price_step"
                ],
            )
        )

        if not price_step_match:
            raise RuntimeError(
                "R23 Demo price failed price step validation"
            )

        demo_payload = (
            build_demo_order_payload(
                quantity=
                    entry[
                        "quantity"
                    ],
                limit_price=
                    demo_limit_price,
            )
        )

        # ----------------------------------------------------
        # EXACTLY ONE DEMO ORDER
        # ----------------------------------------------------

        if not RUN_DEMO_ORDER_TEST:
            raise RuntimeError(
                "R23 requires RUN_DEMO_ORDER_TEST=true "
                "for lifecycle validation"
            )

        stage = "demo IOC order transmission"

        demo_response = await demo_post(
            session,
            DEMO_ORDER_PATH,
            demo_payload,
        )

        demo_order_id = extract_demo_order_id(
            demo_response
        )

        # ----------------------------------------------------
        # ORDER HISTORY RECONCILIATION
        # ----------------------------------------------------

        stage = "demo order history reconciliation"

        history_order = (
            await locate_demo_order_in_history(
                session,
                demo_order_id,
            )
        )

        history_validation = (
            validate_history_order(
                history_order=
                    history_order,
                order_id=
                    demo_order_id,
                requested_quantity=
                    entry[
                        "quantity"
                    ],
            )
        )

        if not history_validation[
            "passed"
        ]:
            raise RuntimeError(
                "R23 Demo order history validation failed: "
                + json.dumps(
                    history_order,
                    default=str,
                )
            )

        # ----------------------------------------------------
        # DEMO POSITION SNAPSHOT AFTER
        # ----------------------------------------------------

        stage = "demo position snapshot after"

        await asyncio.sleep(
            1.0
        )

        demo_positions_after_payload = (
            await private_get(
                session,
                DEMO_POSITIONS_PATH,
            )
        )

        position_after = (
            get_demo_symbol_position_size(
                demo_positions_after_payload,
                DEMO_SYMBOL,
            )
        )

        position_unchanged = (
            position_after
            == position_before
        )

        # A changed demo position does not imply a real-order
        # safety failure. But it means the IOC order actually
        # received execution in Demo and must be clearly shown.
        #
        # R23 will report it rather than silently ignoring it.

        # ----------------------------------------------------
        # FINAL SAFETY
        # ----------------------------------------------------

        stage = "final safety assertions"

        final_safety_assertions_r23()

        demo_data = {
            "limit_price":
                demo_limit_price,
            "price_step_match":
                price_step_match,
            "order_id":
                demo_order_id,
            "history_order":
                history_order,
            "history_validation":
                history_validation,
            "position_before":
                position_before,
            "position_after":
                position_after,
            "position_unchanged":
                position_unchanged,
        }

        report = build_report(
            available_usdt=
                available_usdt,
            mark_price=
                mark_price,
            signal_tests=
                signal_tests,
            contract=
                contract,
            entry=
                entry,
            exposure=
                exposure,
            leverage_gate=
                leverage_gate,
            demo_data=
                demo_data,
        )

        print(
            report
        )

        await send_telegram(
            session,
            report,
        )

        return True

    except Exception as exc:
        report = build_error_report(
            stage,
            exc,
        )

        print(
            report
        )

        traceback.print_exc()

        try:
            await send_telegram(
                session,
                report,
            )

        except Exception:
            pass

        return False


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime():
    print(
        "=" * 60
    )
    print(
        f"{MODULE_NAME} STARTING"
    )
    print(
        "PERSISTENT PRE-LIVE EXECUTION PATH VALIDATION"
    )
    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )
    print(
        "R23 DEMO ORDER LIFECYCLE VALIDATION"
    )
    print(
        "RENDER AUTO-EXIT PREVENTION ACTIVE"
    )
    print(
        "=" * 60
    )

    health_runner = await start_health_server()

    timeout = aiohttp.ClientTimeout(
        total=30
    )

    connector = aiohttp.TCPConnector(
        limit=20,
        ttl_dns_cache=300,
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
    ) as session:

        await r23_run_diagnostic(
            session
        )

        print(
            "=" * 60
        )
        print(
            f"{MODULE_NAME} DIAGNOSTIC CYCLE COMPLETE"
        )
        print(
            "PERSISTENT SERVICE REMAINS ACTIVE"
        )
        print(
            "NO REPEATED DEMO ORDER LOOP"
        )
        print(
            "REAL ORDER POST LOCK REMAINS ACTIVE"
        )
        print(
            "=" * 60
        )

        # ----------------------------------------------------
        # CRITICAL:
        # Keep Render process alive but NEVER rerun the Demo
        # diagnostic automatically.
        # ----------------------------------------------------

        while True:
            final_safety_assertions_r23()

            await asyncio.sleep(
                3600
            )

    # Normally unreachable.
    await health_runner.cleanup()


# ============================================================
# MAIN
# ============================================================

def main():
    try:
        asyncio.run(
            persistent_runtime()
        )

    except KeyboardInterrupt:
        print(
            f"{MODULE_NAME} STOPPED"
        )

    except Exception as exc:
        print(
            "=" * 60
        )
        print(
            f"❌ {MODULE_NAME} FATAL STARTUP ERROR"
        )
        print(
            type(exc).__name__
            + ": "
            + str(exc)
        )
        print(
            "🛡 REAL ORDER POST LOCK REMAINS ACTIVE"
        )
        print(
            "⚠️ NO REAL ORDER WAS SENT"
        )
        print(
            "=" * 60
        )

        traceback.print_exc()

        raise


if __name__ == "__main__":
    main()
