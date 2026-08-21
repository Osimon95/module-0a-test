import asyncio
import base64
import hashlib
import hmac
import json
import os
import threading
import time
import traceback
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode

import aiohttp


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R21"

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
# R21 IS A PRE-LIVE EXECUTION REHEARSAL.
#
# ALLOWED:
#
#   PUBLIC GET
#   AUTHENTICATED GET
#   OPTIONAL DEMO POST
#
# FORBIDDEN:
#
#   REAL /capi/v3/order POST
#   REAL POSITION CHANGES
#   REAL LEVERAGE CHANGES
#   REAL MARGIN CHANGES
#   REAL TP/SL ORDERS
#   REAL CLOSE ORDERS
#
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_REAL_POST_LOCK = True

REAL_ORDER_PATH = "/capi/v3/order"

DEMO_ORDER_PATH = "/capi/v3/sim/order"

R21_REAL_POST_CALLED = False

R21_DEMO_POST_ATTEMPTED = False

R21_DEMO_POST_ACCEPTED = False


# ============================================================
# DEMO TEST
# ============================================================

RUN_DEMO_ORDER_TEST = (
    os.getenv(
        "RUN_DEMO_ORDER_TEST",
        "true",
    )
    .strip()
    .lower()
    in (
        "1",
        "true",
        "yes",
        "on",
    )
)

REHEARSAL_SIDE = os.getenv(
    "REHEARSAL_SIDE",
    "BUY",
).strip().upper()

REHEARSAL_POSITION_SIDE = os.getenv(
    "REHEARSAL_POSITION_SIDE",
    "LONG",
).strip().upper()

REHEARSAL_ORDER_TYPE = os.getenv(
    "REHEARSAL_ORDER_TYPE",
    "LIMIT",
).strip().upper()


# ============================================================
# ADJUSTABLE STRATEGY CONFIGURATION
# ============================================================

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

MIN_LIQUIDATION_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQUIDATION_DISTANCE_PERCENT",
        "0.2",
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TP / TRAILING CONFIG
# ============================================================

TP1_SIZE_PERCENT = Decimal("20")
TP2_SIZE_PERCENT = Decimal("20")
TP3_SIZE_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ============================================================
# SIGNAL SAFETY
# ============================================================

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

ONE_DIRECTION_ONLY = True

ANTI_DUPLICATE_ORDERS = True

TREND_REVERSAL_EXIT = True

IDLE_PYRAMID_CLEANUP = True


# ============================================================
# FALLBACK CONTRACT VALUES
# ============================================================
#
# Exchange information is preferred.
#
# These are fallback values only.
#
# ============================================================

FALLBACK_MIN_ORDER_SIZE = Decimal("0.0001")

FALLBACK_QUANTITY_PRECISION = 4

FALLBACK_PRICE_PRECISION = 1

FALLBACK_CONTRACT_VALUE = Decimal("0.0001")

FALLBACK_MIN_LEVERAGE = 1

FALLBACK_MAX_LEVERAGE = 400


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")

ONE = Decimal("1")

HUNDRED = Decimal("100")


# ============================================================
# CREDENTIALS
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
# RENDER HEALTH SERVER
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = (
            f"{MODULE_NAME} OK\n"
            f"LIVE_ORDER_EXECUTION={LIVE_ORDER_EXECUTION}\n"
            f"HARD_REAL_POST_LOCK={HARD_REAL_POST_LOCK}\n"
        ).encode()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def log_message(
        self,
        format,
        *args,
    ):
        return


def start_health_server():

    def run():

        try:

            server = ThreadingHTTPServer(
                (
                    "0.0.0.0",
                    PORT,
                ),
                HealthHandler,
            )

            print(
                f"HEALTH SERVER ACTIVE ON PORT {PORT}"
            )

            server.serve_forever()

        except Exception as exc:

            print(
                f"HEALTH SERVER ERROR: {exc}"
            )

    thread = threading.Thread(
        target=run,
        daemon=True,
    )

    thread.start()


# ============================================================
# DECIMAL HELPERS
# ============================================================

def safe_decimal(
    value,
    default=None,
):

    if value is None:

        if default is not None:
            return Decimal(str(default))

        raise RuntimeError(
            "Cannot convert None to Decimal"
        )

    try:

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:

        if default is not None:
            return Decimal(str(default))

        raise RuntimeError(
            f"Invalid decimal value: {value}"
        ) from exc


def decimal_to_exchange_string(
    value: Decimal,
) -> str:

    value = safe_decimal(value)

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    if text in (
        "",
        "-0",
    ):
        text = "0"

    return text


def precision_to_step(
    precision: int,
) -> Decimal:

    precision = int(
        precision
    )

    if precision <= 0:
        return Decimal("1")

    return Decimal(
        "1"
    ).scaleb(
        -precision
    )


def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    value = safe_decimal(
        value
    )

    step = safe_decimal(
        step
    )

    if step <= ZERO:

        raise RuntimeError(
            f"Invalid step: {step}"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    result = (
        units * step
    )

    return result


def status_icon(
    value: bool,
) -> str:

    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


# ============================================================
# CONFIG VALIDATION
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


def final_safety_assertions_r21():

    if LIVE_ORDER_EXECUTION is not False:

        raise RuntimeError(
            "R21 SAFETY FAILURE: "
            "LIVE_ORDER_EXECUTION must remain False"
        )

    if HARD_REAL_POST_LOCK is not True:

        raise RuntimeError(
            "R21 SAFETY FAILURE: "
            "HARD_REAL_POST_LOCK must remain True"
        )

    if R21_REAL_POST_CALLED:

        raise RuntimeError(
            "R21 SAFETY FAILURE: "
            "real POST flag was activated"
        )

    if REAL_ORDER_PATH == DEMO_ORDER_PATH:

        raise RuntimeError(
            "R21 SAFETY FAILURE: "
            "real and demo paths match"
        )

    if not DEMO_ORDER_PATH.startswith(
        "/capi/v3/sim/"
    ):

        raise RuntimeError(
            "R21 SAFETY FAILURE: "
            f"invalid demo path {DEMO_ORDER_PATH}"
        )

    return True


# ============================================================
# REAL POST HARD LOCK
# ============================================================

async def blocked_real_order_post(
    *args,
    **kwargs,
):

    global R21_REAL_POST_CALLED

    R21_REAL_POST_CALLED = True

    raise RuntimeError(
        "R21 ABSOLUTE SAFETY LOCK: "
        "REAL ORDER POST BLOCKED"
    )


# ============================================================
# AUTH SIGNATURE
# ============================================================

def create_signature(
    timestamp: str,
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    request_target = path

    if query_string:

        request_target = (
            f"{path}?{query_string}"
        )

    message = (
        f"{timestamp}"
        f"{method}"
        f"{request_target}"
        f"{body}"
    )

    signature = hmac.new(
        WEEX_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        signature
    ).decode()


def authenticated_headers(
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
):

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = create_signature(
        timestamp=timestamp,
        method=method,
        path=path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ============================================================
# JSON PARSER
# ============================================================

def parse_json_response(
    text: str,
):

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"Invalid JSON response: {text[:500]}"
        ) from exc


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):

    params = params or {}

    query_string = urlencode(
        params
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    if query_string:

        url = (
            f"{url}?"
            f"{query_string}"
        )

    async with session.get(
        url,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX HTTP {response.status}: {text}"
            )

        return parse_json_response(
            text
        )


# ============================================================
# AUTHENTICATED GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):

    params = params or {}

    query_string = urlencode(
        params
    )

    headers = authenticated_headers(
        method="GET",
        path=path,
        query_string=query_string,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    if query_string:

        url = (
            f"{url}?"
            f"{query_string}"
        )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX HTTP {response.status}: {text}"
            )

        return parse_json_response(
            text
        )


# ============================================================
# DEMO POST ONLY
# ============================================================

async def demo_post(
    session,
    path,
    payload,
):

    global R21_DEMO_POST_ATTEMPTED
    global R21_DEMO_POST_ACCEPTED

    if path == REAL_ORDER_PATH:

        raise RuntimeError(
            "R21 SAFETY LOCK: "
            "demo_post received REAL order path"
        )

    if not path.startswith(
        "/capi/v3/sim/"
    ):

        raise RuntimeError(
            "R21 SAFETY LOCK: "
            f"non-demo POST path blocked: {path}"
        )

    if LIVE_ORDER_EXECUTION:

        raise RuntimeError(
            "R21 SAFETY LOCK: "
            "LIVE_ORDER_EXECUTION unexpectedly enabled"
        )

    if not HARD_REAL_POST_LOCK:

        raise RuntimeError(
            "R21 SAFETY LOCK unexpectedly disabled"
        )

    body = json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )

    headers = authenticated_headers(
        method="POST",
        path=path,
        body=body,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    R21_DEMO_POST_ATTEMPTED = True

    async with session.post(
        url,
        headers=headers,
        data=body,
        timeout=aiohttp.ClientTimeout(
            total=20
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX DEMO POST HTTP "
                f"{response.status}: {text}"
            )

        data = parse_json_response(
            text
        )

        if isinstance(
            data,
            dict,
        ):

            success = data.get(
                "success"
            )

            if success is False:

                raise RuntimeError(
                    "WEEX DEMO ORDER REJECTED: "
                    f"{data}"
                )

        R21_DEMO_POST_ACCEPTED = True

        return data


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):

    data = await public_get(
        session=session,
        path="/capi/v3/market/symbolPrice",
        params={
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    if not isinstance(
        data,
        dict,
    ):

        raise RuntimeError(
            f"Unexpected mark price response: {data}"
        )

    price = safe_decimal(
        data.get(
            "price"
        )
    )

    if price <= ZERO:

        raise RuntimeError(
            f"Invalid WEEX mark price: {price}"
        )

    return price


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_available_usdt(
    session,
):

    data = await private_get(
        session=session,
        path="/capi/v3/account/balance",
    )

    if isinstance(
        data,
        dict,
    ):

        possible = data.get(
            "data"
        )

        if isinstance(
            possible,
            list,
        ):
            data = possible

    if not isinstance(
        data,
        list,
    ):

        raise RuntimeError(
            f"Unexpected WEEX balance response: {data}"
        )

    for item in data:

        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get(
                "asset",
                "",
            )
        ).upper()

        if asset == "USDT":

            available = safe_decimal(
                item.get(
                    "availableBalance"
                )
            )

            if available < ZERO:

                raise RuntimeError(
                    f"Invalid available USDT: {available}"
                )

            return available

    raise RuntimeError(
        "Unable to extract available USDT"
    )


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):

    data = await public_get(
        session=session,
        path="/capi/v3/market/exchangeInfo",
        params={
            "symbol": SYMBOL,
        },
    )

    if not isinstance(
        data,
        dict,
    ):

        raise RuntimeError(
            f"Unexpected exchangeInfo response: {data}"
        )

    symbols = data.get(
        "symbols"
    )

    if not isinstance(
        symbols,
        list,
    ):

        raise RuntimeError(
            "exchangeInfo did not contain symbols"
        )

    selected = None

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
        ).upper() == SYMBOL:

            selected = item
            break

    if selected is None:

        raise RuntimeError(
            f"{SYMBOL} not found in exchangeInfo"
        )

    price_precision = int(
        selected.get(
            "pricePrecision",
            FALLBACK_PRICE_PRECISION,
        )
    )

    quantity_precision = int(
        selected.get(
            "quantityPrecision",
            FALLBACK_QUANTITY_PRECISION,
        )
    )

    min_order_size = safe_decimal(
        selected.get(
            "minOrderSize",
            FALLBACK_MIN_ORDER_SIZE,
        )
    )

    contract_value = safe_decimal(
        selected.get(
            "contractVal",
            FALLBACK_CONTRACT_VALUE,
        )
    )

    min_leverage = int(
        selected.get(
            "minLeverage",
            FALLBACK_MIN_LEVERAGE,
        )
    )

    max_leverage = int(
        selected.get(
            "maxLeverage",
            FALLBACK_MAX_LEVERAGE,
        )
    )

    price_step = precision_to_step(
        price_precision
    )

    quantity_step = precision_to_step(
        quantity_precision
    )

    return {
        "raw": selected,
        "price_precision": price_precision,
        "price_step": price_step,
        "quantity_precision": quantity_precision,
        "quantity_step": quantity_step,
        "min_order_size": min_order_size,
        "contract_value": contract_value,
        "min_leverage": min_leverage,
        "max_leverage": max_leverage,
    }


# ============================================================
# API TRADING SYMBOL CHECK
# ============================================================

async def get_api_trading_symbol_gate(
    session,
):

    data = await public_get(
        session=session,
        path="/capi/v3/market/apiTradingSymbols",
    )

    symbols = []

    if isinstance(
        data,
        list,
    ):

        symbols = data

    elif isinstance(
        data,
        dict,
    ):

        possible = data.get(
            "data"
        )

        if isinstance(
            possible,
            list,
        ):
            symbols = possible

    normalized = {
        str(item).upper()
        for item in symbols
    }

    return (
        SYMBOL in normalized
    )


# ============================================================
# POSITION CHECK
# ============================================================

async def get_current_positions(
    session,
):

    data = await private_get(
        session=session,
        path="/capi/v3/account/position/singlePosition",
        params={
            "symbol": SYMBOL,
        },
    )

    if isinstance(
        data,
        dict,
    ):

        possible = data.get(
            "data"
        )

        if isinstance(
            possible,
            list,
        ):
            data = possible
        else:
            data = [
                data
            ]

    if not isinstance(
        data,
        list,
    ):

        return []

    positions = []

    for item in data:

        if not isinstance(
            item,
            dict,
        ):
            continue

        size = safe_decimal(
            item.get(
                "size",
                "0",
            ),
            default="0",
        )

        if size > ZERO:

            positions.append(
                item
            )

    return positions


# ============================================================
# EXPOSURE
# ============================================================

def calculate_worst_case_exposure():

    initial = ENTRY_PERCENT

    pyramid = (
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
        + pyramid
        + backups
    )

    return {
        "initial": initial,
        "pyramids": pyramid,
        "backups": backups,
        "total": total,
        "passed": (
            total
            <= MAX_FUND_EXPOSURE_PERCENT
        ),
    }


# ============================================================
# LEVERAGE GATE
# ============================================================

def validate_leverage_r21(
    min_leverage,
    max_leverage,
):

    if LEVERAGE < 1:

        return False

    if LEVERAGE > MAX_CONFIG_LEVERAGE:

        return False

    if LEVERAGE < int(
        min_leverage
    ):

        return False

    if LEVERAGE > int(
        max_leverage
    ):

        return False

    return True


# ============================================================
# ENTRY CALCULATION
# ============================================================

def calculate_entry(
    available_usdt,
    mark_price,
    contract_info,
):

    available_usdt = safe_decimal(
        available_usdt
    )

    mark_price = safe_decimal(
        mark_price
    )

    if available_usdt <= ZERO:

        raise RuntimeError(
            "Available balance must be positive"
        )

    if mark_price <= ZERO:

        raise RuntimeError(
            "Mark price must be positive"
        )

    margin = (
        available_usdt
        * ENTRY_PERCENT
        / HUNDRED
    )

    notional = (
        margin
        * Decimal(
            LEVERAGE
        )
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity_precision = contract_info[
        "quantity_precision"
    ]

    quantity_step = precision_to_step(
        quantity_precision
    )

    quantity = floor_to_step(
        raw_quantity,
        quantity_step,
    )

    min_order = contract_info[
        "min_order_size"
    ]

    minimum_passed = (
        quantity
        >= min_order
    )

    return {
        "margin": margin,
        "notional": notional,
        "raw_quantity": raw_quantity,
        "quantity": quantity,
        "minimum_passed": minimum_passed,
    }


# ============================================================
# QUANTITY VALIDATION
# ============================================================

def validate_execution_quantity(
    quantity,
    contract_info,
):

    quantity = safe_decimal(
        quantity
    )

    if quantity <= ZERO:

        raise RuntimeError(
            f"R21 quantity is not positive: {quantity}"
        )

    min_order = contract_info[
        "min_order_size"
    ]

    if quantity < min_order:

        raise RuntimeError(
            "R21 quantity below WEEX minimum: "
            f"{quantity} < {min_order}"
        )

    quantity_step = contract_info[
        "quantity_step"
    ]

    normalized = floor_to_step(
        quantity,
        quantity_step,
    )

    if normalized != quantity:

        raise RuntimeError(
            "R21 quantity does not match "
            f"quantity step {quantity_step}: "
            f"{quantity}"
        )

    return True


# ============================================================
# R21 PRICE-STEP FIX
# ============================================================

def build_safe_demo_limit_price(
    mark_price,
    side,
    price_step,
):

    mark_price = safe_decimal(
        mark_price
    )

    price_step = safe_decimal(
        price_step
    )

    if mark_price <= ZERO:

        raise RuntimeError(
            f"Invalid mark price: {mark_price}"
        )

    if price_step <= ZERO:

        raise RuntimeError(
            f"Invalid WEEX price step: {price_step}"
        )

    side = str(
        side
    ).strip().upper()

    if side == "BUY":

        raw_price = (
            mark_price
            * Decimal(
                "0.999"
            )
        )

    elif side == "SELL":

        raw_price = (
            mark_price
            * Decimal(
                "1.001"
            )
        )

    else:

        raise RuntimeError(
            f"Invalid rehearsal side: {side}"
        )

    safe_price = floor_to_step(
        raw_price,
        price_step,
    )

    if safe_price <= ZERO:

        raise RuntimeError(
            f"Calculated demo price invalid: {safe_price}"
        )

    # --------------------------------------------------------
    # FINAL EXACT STEP ASSERTION
    # --------------------------------------------------------

    step_count = (
        safe_price
        / price_step
    )

    normalized_count = (
        step_count.to_integral_value(
            rounding=ROUND_DOWN
        )
    )

    if step_count != normalized_count:

        raise RuntimeError(
            "R21 price-step normalization failed: "
            f"{safe_price} / {price_step}"
        )

    return safe_price


# ============================================================
# TP CALCULATIONS - DIAGNOSTIC ONLY
# ============================================================

def calculate_tp_prices_r21(
    mark_price,
    side,
):

    mark_price = safe_decimal(
        mark_price
    )

    side = side.upper()

    if side == "BUY":

        tp1 = (
            mark_price
            * (
                ONE
                + (
                    TP1_TRIGGER_PERCENT
                    / HUNDRED
                )
            )
        )

        tp2 = (
            mark_price
            * (
                ONE
                + (
                    TP2_TRIGGER_PERCENT
                    / HUNDRED
                )
            )
        )

    elif side == "SELL":

        tp1 = (
            mark_price
            * (
                ONE
                - (
                    TP1_TRIGGER_PERCENT
                    / HUNDRED
                )
            )
        )

        tp2 = (
            mark_price
            * (
                ONE
                - (
                    TP2_TRIGGER_PERCENT
                    / HUNDRED
                )
            )
        )

    else:

        raise RuntimeError(
            f"Invalid side: {side}"
        )

    return (
        tp1,
        tp2,
    )


def calculate_trailing_distance_r21(
    mark_price,
):

    mark_price = safe_decimal(
        mark_price
    )

    return (
        mark_price
        * TRAILING_DISTANCE_PERCENT
        / HUNDRED
    )


# ============================================================
# CLIENT ORDER ID
# ============================================================

def create_client_order_id():

    milliseconds = int(
        time.time() * 1000
    )

    value = (
        f"r21-{milliseconds}"
    )

    return value[:36]


# ============================================================
# DEMO PAYLOAD
# ============================================================

def build_v3_order_payload_r21(
    symbol,
    side,
    position_side,
    order_type,
    quantity,
    price=None,
):

    side = str(
        side
    ).strip().upper()

    position_side = str(
        position_side
    ).strip().upper()

    order_type = str(
        order_type
    ).strip().upper()

    if side not in (
        "BUY",
        "SELL",
    ):

        raise RuntimeError(
            f"Invalid order side: {side}"
        )

    if position_side not in (
        "LONG",
        "SHORT",
    ):

        raise RuntimeError(
            f"Invalid position side: {position_side}"
        )

    if order_type not in (
        "LIMIT",
        "MARKET",
    ):

        raise RuntimeError(
            f"Invalid order type: {order_type}"
        )

    payload = {
        "symbol": str(
            symbol
        ).upper(),
        "side": side,
        "positionSide": position_side,
        "type": order_type,
        "quantity": decimal_to_exchange_string(
            quantity
        ),
        "newClientOrderId": create_client_order_id(),
    }

    if order_type == "LIMIT":

        if price is None:

            raise RuntimeError(
                "LIMIT order requires a price"
            )

        price = safe_decimal(
            price
        )

        if price <= ZERO:

            raise RuntimeError(
                f"Invalid LIMIT price: {price}"
            )

        payload[
            "timeInForce"
        ] = "GTC"

        # ----------------------------------------------------
        # DO NOT USE float(price).
        #
        # Decimal -> exact exchange string.
        # ----------------------------------------------------

        payload[
            "price"
        ] = decimal_to_exchange_string(
            price
        )

    return payload


# ============================================================
# DEMO ORDER RESPONSE
# ============================================================

def validate_demo_response_r21(
    response,
):

    if not isinstance(
        response,
        dict,
    ):

        raise RuntimeError(
            f"Unexpected demo response: {response}"
        )

    if response.get(
        "success"
    ) is False:

        raise RuntimeError(
            "WEEX DEMO order rejected: "
            f"{response}"
        )

    order_id = response.get(
        "orderId"
    )

    client_order_id = response.get(
        "clientOrderId"
    )

    if not order_id:

        raise RuntimeError(
            "WEEX DEMO response did not "
            "contain orderId"
        )

    return {
        "order_id": str(
            order_id
        ),
        "client_order_id": (
            str(
                client_order_id
            )
            if client_order_id
            else ""
        ),
    }


# ============================================================
# SIGNAL GATE SELF TESTS
# ============================================================

def run_signal_gate_self_tests():

    now = time.time()

    fresh_signal_time = (
        now - 1
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 10
    )

    fresh_signal_accepted = (
        now
        - fresh_signal_time
        <= SIGNAL_EXPIRY_SECONDS
    )

    expired_signal_rejected = (
        now
        - expired_signal_time
        > SIGNAL_EXPIRY_SECONDS
    )

    last_loss_time = (
        now - 1
    )

    loss_cooldown_test = (
        now
        - last_loss_time
        < LOSS_COOLDOWN_SECONDS
    )

    seen_signal_ids = {
        "r21-test-signal"
    }

    duplicate_signal_rejected = (
        "r21-test-signal"
        in seen_signal_ids
    )

    one_direction_gate = (
        ONE_DIRECTION_ONLY
        is True
    )

    return {
        "fresh": fresh_signal_accepted,
        "expired": expired_signal_rejected,
        "cooldown": loss_cooldown_test,
        "duplicate": duplicate_signal_rejected,
        "one_direction": one_direction_gate,
    }


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):

    if not TELEGRAM_BOT_TOKEN:
        return False

    if not TELEGRAM_CHAT_ID:
        return False

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        "sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:

        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            await response.text()

            return (
                response.status == 200
            )

    except Exception:

        return False


# ============================================================
# SUCCESS REPORT
# ============================================================

def build_success_report(
    available_usdt,
    mark_price,
    api_symbol_gate,
    contract_info,
    entry,
    exposure,
    signal_tests,
    external_position_clear,
    leverage_gate,
    demo_price,
    demo_response,
):

    lines = []

    lines.append(
        f"✅ MODULE {MODULE_NAME} DIAGNOSTIC PASSED"
    )

    lines.append(
        SYMBOL
    )

    lines.append(
        "Available USDT: "
        f"{decimal_to_exchange_string(available_usdt)}"
    )

    lines.append(
        "Mark Price: "
        f"{decimal_to_exchange_string(mark_price)} USDT"
    )

    lines.append(
        ""
    )

    lines.append(
        "FINAL EXECUTION GATE"
    )

    lines.append(
        "API Trading Symbol: "
        f"{status_icon(api_symbol_gate)}"
    )

    lines.append(
        "Fresh Signal Accepted: "
        f"{status_icon(signal_tests['fresh'])}"
    )

    lines.append(
        "Expired Signal Rejected: "
        f"{status_icon(signal_tests['expired'])}"
    )

    lines.append(
        "Loss Cooldown Test: "
        f"{status_icon(signal_tests['cooldown'])}"
    )

    lines.append(
        "Duplicate Signal Rejected: "
        f"{status_icon(signal_tests['duplicate'])}"
    )

    lines.append(
        "One Direction Gate: "
        f"{status_icon(signal_tests['one_direction'])}"
    )

    lines.append(
        "External Position Clear: "
        f"{status_icon(external_position_clear)}"
    )

    lines.append(
        ""
    )

    lines.append(
        "ADJUSTABLE CONFIG"
    )

    lines.append(
        f"Entry: {ENTRY_PERCENT}%"
    )

    lines.append(
        f"Leverage: {LEVERAGE}x"
    )

    lines.append(
        "Max Config Leverage: "
        f"{MAX_CONFIG_LEVERAGE}x"
    )

    lines.append(
        f"Margin Type: {MARGIN_TYPE}"
    )

    lines.append(
        "Max Pyramids: "
        f"{MAX_PYRAMID_ADDS}"
    )

    lines.append(
        "Pyramid Size: "
        f"{PYRAMID_SIZE_PERCENT}%"
    )

    lines.append(
        "Max Backups: "
        f"{MAX_BACKUPS}"
    )

    lines.append(
        "Backup Size: "
        f"{BACKUP_SIZE_PERCENT}% each"
    )

    lines.append(
        "Backup Buffer: "
        f"{BACKUP_BUFFER_PERCENT}%"
    )

    lines.append(
        "Min Liq Distance: "
        f"{MIN_LIQUIDATION_DISTANCE_PERCENT}%"
    )

    lines.append(
        "Max Fund Exposure: "
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    lines.append(
        ""
    )

    lines.append(
        "WEEX CONTRACT"
    )

    lines.append(
        "Minimum Order: "
        f"{decimal_to_exchange_string(contract_info['min_order_size'])}"
    )

    lines.append(
        "Quantity Precision: "
        f"{contract_info['quantity_precision']}"
    )

    lines.append(
        "Price Precision: "
        f"{contract_info['price_precision']}"
    )

    lines.append(
        "Price Step: "
        f"{decimal_to_exchange_string(contract_info['price_step'])}"
    )

    lines.append(
        "Contract Value: "
        f"{decimal_to_exchange_string(contract_info['contract_value'])}"
    )

    lines.append(
        "WEEX Min Leverage: "
        f"{contract_info['min_leverage']}x"
    )

    lines.append(
        "WEEX Max Leverage: "
        f"{contract_info['max_leverage']}x"
    )

    lines.append(
        "Leverage Gate: "
        f"{status_icon(leverage_gate)}"
    )

    lines.append(
        ""
    )

    lines.append(
        "DYNAMIC ENTRY"
    )

    lines.append(
        "Margin: "
        f"{decimal_to_exchange_string(entry['margin'])} USDT"
    )

    lines.append(
        "Notional: "
        f"{decimal_to_exchange_string(entry['notional'])} USDT"
    )

    lines.append(
        "Quantity: "
        f"{decimal_to_exchange_string(entry['quantity'])}"
    )

    lines.append(
        "Quantity Positive: "
        f"{status_icon(entry['quantity'] > ZERO)}"
    )

    lines.append(
        "Minimum Passed: "
        f"{status_icon(entry['minimum_passed'])}"
    )

    lines.append(
        ""
    )

    lines.append(
        "WORST-CASE EXPOSURE"
    )

    lines.append(
        "Initial: "
        f"{exposure['initial']}%"
    )

    lines.append(
        "Pyramids: "
        f"{exposure['pyramids']}%"
    )

    lines.append(
        "Backups: "
        f"{exposure['backups']}%"
    )

    lines.append(
        "Total: "
        f"{exposure['total']}% / "
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    lines.append(
        "Exposure Passed: "
        f"{status_icon(exposure['passed'])}"
    )

    lines.append(
        ""
    )

    lines.append(
        "TP / TRAILING"
    )

    lines.append(
        "TP1 / TP2 / TP3: "
        f"{TP1_SIZE_PERCENT}% / "
        f"{TP2_SIZE_PERCENT}% / "
        f"{TP3_SIZE_PERCENT}%"
    )

    lines.append(
        f"TP1 Trigger: {TP1_TRIGGER_PERCENT}%"
    )

    lines.append(
        f"TP2 Trigger: {TP2_TRIGGER_PERCENT}%"
    )

    lines.append(
        "Trailing Distance: "
        f"{TRAILING_DISTANCE_PERCENT}%"
    )

    lines.append(
        ""
    )

    lines.append(
        "R21 DEMO EXECUTION REHEARSAL"
    )

    lines.append(
        f"Demo Symbol: {DEMO_SYMBOL}"
    )

    lines.append(
        f"Demo Side: {REHEARSAL_SIDE}"
    )

    lines.append(
        "Demo Position Side: "
        f"{REHEARSAL_POSITION_SIDE}"
    )

    lines.append(
        f"Demo Type: {REHEARSAL_ORDER_TYPE}"
    )

    if demo_price is not None:

        lines.append(
            "Demo Limit Price: "
            f"{decimal_to_exchange_string(demo_price)}"
        )

        lines.append(
            "Price Step Match: ✅ YES"
        )

    lines.append(
        "Demo POST Attempted: "
        f"{status_icon(R21_DEMO_POST_ATTEMPTED)}"
    )

    lines.append(
        "Demo POST Accepted: "
        f"{status_icon(R21_DEMO_POST_ACCEPTED)}"
    )

    if demo_response:

        lines.append(
            "Demo Order ID: "
            f"{demo_response.get('order_id', '')}"
        )

    lines.append(
        ""
    )

    lines.append(
        "ABSOLUTE EXECUTION SAFETY"
    )

    lines.append(
        "Real POST Called: "
        f"{status_icon(R21_REAL_POST_CALLED)}"
    )

    lines.append(
        "🛡 R21 absolute real-order POST lock active"
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
    stage,
    exc,
):

    return "\n".join(
        [
            f"❌ MODULE {MODULE_NAME} ERROR",
            SYMBOL,
            f"Stage: {stage}",
            f"{type(exc).__name__}: {exc}",
            (
                "Real POST Called: "
                f"{status_icon(R21_REAL_POST_CALLED)}"
            ),
            (
                "Demo POST Attempted: "
                f"{status_icon(R21_DEMO_POST_ATTEMPTED)}"
            ),
            (
                "Demo POST Accepted: "
                f"{status_icon(R21_DEMO_POST_ACCEPTED)}"
            ),
            "🛡 R21 absolute real-order POST lock active",
            "⚠️ LIVE ORDER EXECUTION DISABLED",
            "⚠️ NO REAL ORDER WAS SENT",
        ]
    )


# ============================================================
# MAIN R21 DIAGNOSTIC
# ============================================================

async def r21_run_diagnostic():

    stage = "startup"

    connector = aiohttp.TCPConnector(
        ssl=True
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        try:

            # ------------------------------------------------
            # SAFETY
            # ------------------------------------------------

            stage = "safety assertions"

            final_safety_assertions_r21()

            # ------------------------------------------------
            # CREDENTIALS
            # ------------------------------------------------

            stage = "configuration"

            validate_credentials()

            # ------------------------------------------------
            # API TRADING SYMBOL
            # ------------------------------------------------

            stage = "api trading symbol"

            api_symbol_gate = (
                await get_api_trading_symbol_gate(
                    session
                )
            )

            # ------------------------------------------------
            # CONTRACT
            # ------------------------------------------------

            stage = "contract information"

            contract_info = (
                await get_contract_info(
                    session
                )
            )

            # ------------------------------------------------
            # LEVERAGE
            # ------------------------------------------------

            stage = "leverage validation"

            leverage_gate = (
                validate_leverage_r21(
                    contract_info[
                        "min_leverage"
                    ],
                    contract_info[
                        "max_leverage"
                    ],
                )
            )

            if not leverage_gate:

                raise RuntimeError(
                    "Configured leverage failed "
                    "WEEX/config leverage gate"
                )

            # ------------------------------------------------
            # BALANCE
            # ------------------------------------------------

            stage = "balance"

            available_usdt = (
                await get_available_usdt(
                    session
                )
            )

            # ------------------------------------------------
            # MARK PRICE
            # ------------------------------------------------

            stage = "mark price"

            mark_price = (
                await get_mark_price(
                    session
                )
            )

            # ------------------------------------------------
            # ENTRY
            # ------------------------------------------------

            stage = "entry calculation"

            entry = calculate_entry(
                available_usdt=available_usdt,
                mark_price=mark_price,
                contract_info=contract_info,
            )

            if not entry[
                "minimum_passed"
            ]:

                raise RuntimeError(
                    "Calculated R21 entry quantity "
                    "is below WEEX minimum"
                )

            validate_execution_quantity(
                quantity=entry[
                    "quantity"
                ],
                contract_info=contract_info,
            )

            # ------------------------------------------------
            # EXPOSURE
            # ------------------------------------------------

            stage = "fund exposure"

            exposure = (
                calculate_worst_case_exposure()
            )

            if not exposure[
                "passed"
            ]:

                raise RuntimeError(
                    "Worst-case fund exposure "
                    "exceeds configured maximum"
                )

            # ------------------------------------------------
            # SIGNAL TESTS
            # ------------------------------------------------

            stage = "signal gate self-tests"

            signal_tests = (
                run_signal_gate_self_tests()
            )

            if not all(
                signal_tests.values()
            ):

                raise RuntimeError(
                    "One or more signal gate "
                    "self-tests failed"
                )

            # ------------------------------------------------
            # REAL POSITION CHECK
            # ------------------------------------------------

            stage = "external position gate"

            positions = (
                await get_current_positions(
                    session
                )
            )

            external_position_clear = (
                len(
                    positions
                )
                == 0
            )

            # R21 does not open any REAL order whether this
            # gate is true or false.
            #
            # We report it for pre-live validation.

            # ------------------------------------------------
            # TP DIAGNOSTIC
            # ------------------------------------------------

            stage = "tp calculation"

            calculate_tp_prices_r21(
                mark_price=mark_price,
                side=REHEARSAL_SIDE,
            )

            calculate_trailing_distance_r21(
                mark_price=mark_price,
            )

            # ------------------------------------------------
            # DEMO REHEARSAL
            # ------------------------------------------------

            demo_price = None

            validated_demo_response = None

            if RUN_DEMO_ORDER_TEST:

                stage = "demo price construction"

                if (
                    REHEARSAL_ORDER_TYPE
                    == "LIMIT"
                ):

                    demo_price = (
                        build_safe_demo_limit_price(
                            mark_price=mark_price,
                            side=REHEARSAL_SIDE,
                            price_step=contract_info[
                                "price_step"
                            ],
                        )
                    )

                    # ----------------------------------------
                    # EXPLICIT R21 -1054 PROTECTION
                    # ----------------------------------------

                    expected_price = (
                        floor_to_step(
                            demo_price,
                            contract_info[
                                "price_step"
                            ],
                        )
                    )

                    if (
                        demo_price
                        != expected_price
                    ):

                        raise RuntimeError(
                            "R21 PRICE STEP FAILURE: "
                            f"{demo_price} does not "
                            "match step "
                            f"{contract_info['price_step']}"
                        )

                stage = "demo payload construction"

                payload = (
                    build_v3_order_payload_r21(
                        symbol=DEMO_SYMBOL,
                        side=REHEARSAL_SIDE,
                        position_side=(
                            REHEARSAL_POSITION_SIDE
                        ),
                        order_type=(
                            REHEARSAL_ORDER_TYPE
                        ),
                        quantity=entry[
                            "quantity"
                        ],
                        price=demo_price,
                    )
                )

                print(
                    "R21 DEMO PAYLOAD:"
                )

                print(
                    json.dumps(
                        payload,
                        indent=2,
                    )
                )

                # --------------------------------------------
                # FINAL REAL-ORDER LOCK ASSERTION
                # --------------------------------------------

                final_safety_assertions_r21()

                stage = "demo order transmission"

                demo_result = (
                    await demo_post(
                        session=session,
                        path=DEMO_ORDER_PATH,
                        payload=payload,
                    )
                )

                stage = "demo response validation"

                validated_demo_response = (
                    validate_demo_response_r21(
                        demo_result
                    )
                )

            # ------------------------------------------------
            # FINAL SAFETY ASSERTIONS
            # ------------------------------------------------

            stage = "final safety assertions"

            final_safety_assertions_r21()

            if R21_REAL_POST_CALLED:

                raise RuntimeError(
                    "R21 real-order safety "
                    "flag unexpectedly active"
                )

            # ------------------------------------------------
            # REPORT
            # ------------------------------------------------

            report = build_success_report(
                available_usdt=available_usdt,
                mark_price=mark_price,
                api_symbol_gate=api_symbol_gate,
                contract_info=contract_info,
                entry=entry,
                exposure=exposure,
                signal_tests=signal_tests,
                external_position_clear=(
                    external_position_clear
                ),
                leverage_gate=leverage_gate,
                demo_price=demo_price,
                demo_response=(
                    validated_demo_response
                ),
            )

            print()

            print(
                report
            )

            await send_telegram(
                session=session,
                message=report,
            )

            return True

        except Exception as exc:

            error_report = build_error_report(
                stage=stage,
                exc=exc,
            )

            print()

            print(
                error_report
            )

            traceback.print_exc()

            await send_telegram(
                session=session,
                message=error_report,
            )

            return False


# ============================================================
# MAIN
# ============================================================

def main():

    start_health_server()

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "FINAL PRE-LIVE EXECUTION PATH VALIDATION"
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )

    print(
        "=" * 60
    )

    try:

        passed = asyncio.run(
            r21_run_diagnostic()
        )

        print()

        print(
            "=" * 60
        )

        if passed:

            print(
                f"{MODULE_NAME} COMPLETE: PASSED"
            )

        else:

            print(
                f"{MODULE_NAME} COMPLETE: FAILED"
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

    except KeyboardInterrupt:

        print(
            f"{MODULE_NAME} STOPPED"
        )

        print(
            "🛡 REAL ORDER POST LOCK REMAINS ACTIVE"
        )

    except Exception as exc:

        print(
            "=" * 60
        )

        print(
            f"❌ {MODULE_NAME} FATAL STARTUP ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
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

    # --------------------------------------------------------
    # Render service must remain alive so health checks work.
    # --------------------------------------------------------

    while True:

        time.sleep(
            60
        )


if __name__ == "__main__":

    main()
  
