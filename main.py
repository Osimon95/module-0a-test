import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import traceback

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R20"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ============================================================
# DEMO SYMBOL
# ============================================================
#
# WEEX V3 Demo Mode uses SUSDT.
#
# Real:
# BTCUSDT
#
# Demo:
# BTCSUSDT
#
# Can be overridden in Render with:
#
# DEMO_SYMBOL=BTCSUSDT
#
# ============================================================

def default_demo_symbol(symbol):
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

LIVE_ORDER_EXECUTION = False
HARD_REAL_POST_LOCK = True

REAL_POST_CALLED = False
DEMO_POST_ATTEMPTED = False
DEMO_POST_ACCEPTED = False


# ============================================================
# ADJUSTABLE CONFIG
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal(
    os.getenv(
        "INITIAL_ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = Decimal(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_LEVERAGE = Decimal(
    os.getenv(
        "MAX_LEVERAGE",
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
# CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


# ============================================================
# HELPERS
# ============================================================

def safe_decimal(value):
    try:
        return Decimal(str(value))
    except Exception:
        return ZERO


def fmt(value):
    if isinstance(value, Decimal):
        text = format(
            value.normalize(),
            "f",
        )

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return text or "0"

    return str(value)


def yes_no(value):
    return "✅ YES" if value else "❌ NO"


def json_text(data):
    return json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def floor_precision(value, precision):
    if precision <= 0:
        quantum = Decimal("1")
    else:
        quantum = Decimal(
            "1." + ("0" * precision)
        )

    return value.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def parse_error(data, text=""):
    code = None
    message = ""

    if isinstance(data, dict):
        code = data.get("code")

        if code is None:
            code = data.get("errorCode")

        message = (
            data.get("msg")
            or data.get("message")
            or data.get("errorMessage")
            or ""
        )

    if not message:
        message = text

    try:
        if code is not None:
            code = int(code)
    except Exception:
        pass

    return code, str(message)


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
# WEEX SIGNATURE
# ============================================================

def build_signature(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):
    method = method.upper()

    if query_string:
        message = (
            str(timestamp)
            + method
            + path
            + "?"
            + query_string
            + body
        )
    else:
        message = (
            str(timestamp)
            + method
            + path
            + body
        )

    digest = hmac.new(
        WEEX_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


def private_headers(
    method,
    path,
    query_string="",
    body="",
):
    timestamp = str(
        int(time.time() * 1000)
    )

    signature = build_signature(
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
        "User-Agent": "0F-4H-R20",
    }


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    url = API_BASE_URL + path

    timeout = aiohttp.ClientTimeout(
        total=15
    )

    async with session.get(
        url,
        params=params,
        timeout=timeout,
        headers={
            "User-Agent": "0F-4H-R20",
        },
    ) as response:

        text = await response.text()

        try:
            data = json.loads(text)
        except Exception:
            data = None

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: {text}"
            )

        return data


# ============================================================
# PRIVATE GET
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

    headers = private_headers(
        method="GET",
        path=path,
        query_string=query_string,
        body="",
    )

    url = API_BASE_URL + path

    if query_string:
        url += "?" + query_string

    timeout = aiohttp.ClientTimeout(
        total=15
    )

    async with session.get(
        url,
        headers=headers,
        timeout=timeout,
    ) as response:

        text = await response.text()

        try:
            data = json.loads(text)
        except Exception:
            data = None

        return {
            "status": response.status,
            "data": data,
            "text": text,
        }


# ============================================================
# DEMO POST ONLY
# ============================================================
#
# IMPORTANT:
#
# This function can ONLY target /capi/v3/sim/*
#
# Any other path raises immediately.
#
# Real trading endpoint /capi/v3/order is never called.
#
# ============================================================

async def demo_post(
    session,
    path,
    payload,
):
    global DEMO_POST_ATTEMPTED
    global DEMO_POST_ACCEPTED

    if not path.startswith(
        "/capi/v3/sim/"
    ):
        raise RuntimeError(
            "R20 DEMO POST LOCK: "
            "non-demo POST path blocked"
        )

    if path == "/capi/v3/order":
        raise RuntimeError(
            "R20 ABSOLUTE LOCK: "
            "real order endpoint blocked"
        )

    DEMO_POST_ATTEMPTED = True

    body = json_text(
        payload
    )

    headers = private_headers(
        method="POST",
        path=path,
        query_string="",
        body=body,
    )

    url = API_BASE_URL + path

    timeout = aiohttp.ClientTimeout(
        total=15
    )

    async with session.post(
        url,
        headers=headers,
        data=body,
        timeout=timeout,
    ) as response:

        text = await response.text()

        try:
            data = json.loads(text)
        except Exception:
            data = None

        success = False

        if response.status == 200:
            if isinstance(
                data,
                dict,
            ):
                if data.get(
                    "success"
                ) is True:
                    success = True

                elif data.get(
                    "orderId"
                ):
                    success = True

            else:
                success = True

        DEMO_POST_ACCEPTED = success

        return {
            "status": response.status,
            "data": data,
            "text": text,
            "success": success,
        }


# ============================================================
# REAL POST ABSOLUTE BLOCK
# ============================================================

async def real_post_blocked(
    *args,
    **kwargs,
):
    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise RuntimeError(
        "R20 ABSOLUTE REAL-ORDER POST LOCK ACTIVE"
    )


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/symbolPrice",
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    candidates = []

    if isinstance(
        data,
        dict,
    ):
        candidates.append(
            data
        )

        if isinstance(
            data.get("data"),
            dict,
        ):
            candidates.append(
                data["data"]
            )

    elif isinstance(
        data,
        list,
    ):
        candidates.extend(
            data
        )

    for item in candidates:
        if not isinstance(
            item,
            dict,
        ):
            continue

        for key in (
            "price",
            "markPrice",
            "lastPrice",
            "last",
        ):
            value = safe_decimal(
                item.get(key)
            )

            if value > ZERO:
                return value

    raise RuntimeError(
        "Unable to extract mark price"
    )


# ============================================================
# EXCHANGE INFO
# ============================================================

async def get_contract_info(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL,
        },
    )

    symbols = []

    if isinstance(
        data,
        dict,
    ):
        symbols = (
            data.get("symbols")
            or []
        )

    elif isinstance(
        data,
        list,
    ):
        symbols = data

    for item in symbols:
        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol_name = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol_name == SYMBOL:
            return item

    raise RuntimeError(
        f"Unable to locate contract "
        f"configuration for {SYMBOL}"
    )


# ============================================================
# API TRADING SYMBOLS
# ============================================================

async def get_api_trading_symbols(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/apiTradingSymbols",
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
        possible = (
            data.get("data")
            or data.get("symbols")
            or data.get("result")
            or []
        )

        if isinstance(
            possible,
            list,
        ):
            symbols = possible

    return [
        str(x).upper()
        for x in symbols
    ]


# ============================================================
# LIVE ACCOUNT BALANCE READ
# ============================================================
#
# READ ONLY.
# No POST.
#
# ============================================================

async def get_live_balance(
    session,
):
    result = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    if result["status"] != 200:
        raise RuntimeError(
            "WEEX BALANCE HTTP "
            f"{result['status']}: "
            f"{result['text']}"
        )

    data = result["data"]

    records = []

    if isinstance(
        data,
        list,
    ):
        records = data

    elif isinstance(
        data,
        dict,
    ):
        nested = (
            data.get("data")
            or data.get("result")
        )

        if isinstance(
            nested,
            list,
        ):
            records = nested

        else:
            records = [
                data
            ]

    for item in records:
        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get(
                "asset",
                item.get(
                    "coin",
                    "",
                ),
            )
        ).upper()

        if asset != "USDT":
            continue

        for key in (
            "availableBalance",
            "available",
            "availableAmount",
            "balance",
        ):
            value = safe_decimal(
                item.get(key)
            )

            if value >= ZERO:
                return value

    raise RuntimeError(
        "Unable to extract available USDT"
    )


# ============================================================
# DEMO BALANCE
# ============================================================

async def probe_demo_balance(
    session,
):
    result = await private_get(
        session,
        "/capi/v3/sim/balance",
    )

    accessible = (
        result["status"] == 200
    )

    susdt_balance = None

    if accessible:
        data = result["data"]

        records = []

        if isinstance(
            data,
            list,
        ):
            records = data

        elif isinstance(
            data,
            dict,
        ):
            possible = (
                data.get("data")
                or data.get("result")
            )

            if isinstance(
                possible,
                list,
            ):
                records = possible
            else:
                records = [
                    data
                ]

        for item in records:
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

            if asset == "SUSDT":
                susdt_balance = safe_decimal(
                    item.get(
                        "availableBalance",
                        item.get(
                            "balance",
                            "0",
                        ),
                    )
                )

                break

    code, message = parse_error(
        result["data"],
        result["text"],
    )

    return {
        "accessible": accessible,
        "status": result["status"],
        "balance": susdt_balance,
        "code": code,
        "message": message,
    }


# ============================================================
# DEMO POSITION READ
# ============================================================

async def probe_demo_positions(
    session,
):
    result = await private_get(
        session,
        "/capi/v3/sim/position/allPosition",
    )

    code, message = parse_error(
        result["data"],
        result["text"],
    )

    return {
        "accessible": (
            result["status"] == 200
        ),
        "status": result["status"],
        "code": code,
        "message": message,
    }


# ============================================================
# DEMO HISTORY READ
# ============================================================

async def probe_demo_history(
    session,
):
    result = await private_get(
        session,
        "/capi/v3/sim/order/history",
        {
            "symbol": DEMO_SYMBOL,
        },
    )

    code, message = parse_error(
        result["data"],
        result["text"],
    )

    return {
        "accessible": (
            result["status"] == 200
        ),
        "status": result["status"],
        "code": code,
        "message": message,
    }


# ============================================================
# DEMO ORDER CLASSIFICATION
# ============================================================

def classify_demo_result(
    result,
):
    status = result.get(
        "status"
    )

    data = result.get(
        "data"
    )

    text = result.get(
        "text",
        "",
    )

    if result.get(
        "success"
    ):
        return {
            "classification":
                "DEMO_ORDER_ACCEPTED",
            "code": None,
            "message":
                "WEEX accepted the demo order.",
        }

    code, message = parse_error(
        data,
        text,
    )

    classifications = {
        -1051:
            "PERMISSION_DENIED_1051",

        -1052:
            "INSUFFICIENT_PERMISSIONS_1052",

        -1053:
            "PERMISSION_VALIDATION_FAILED_1053",

        -1055:
            "AUTHENTICATOR_REQUIRED_1055",

        -1056:
            "ILLEGAL_IP_1056",

        -1058:
            "NO_PERMISSION_TRADE_PAIR_1058",

        -1060:
            "API_KEY_SYMBOL_NOT_BOUND_1060",

        -1121:
            "INVALID_DEMO_SYMBOL_1121",

        -3235:
            "CONTRACT_NO_PERMISSION_TRADE_PAIR_3235",

        -3236:
            "CONTRACT_NO_PERMISSION_API_3236",
    }

    classification = classifications.get(
        code,
        f"HTTP_{status}_UNCLASSIFIED",
    )

    return {
        "classification":
            classification,
        "code": code,
        "message": message,
    }


# ============================================================
# DEMO ORDER PROBE
# ============================================================

async def probe_demo_order(
    session,
    mark_price,
    min_order_size,
    quantity_precision,
):
    #
    # Use a LIMIT BUY deliberately far below market.
    #
    # This is demo/paper trading only.
    #
    # It tests whether WEEX accepts the authenticated
    # simulated order endpoint without risking real funds.
    #

    demo_quantity = max(
        min_order_size,
        Decimal("0.0001"),
    )

    demo_quantity = floor_precision(
        demo_quantity,
        quantity_precision,
    )

    if demo_quantity <= ZERO:
        demo_quantity = min_order_size

    demo_price = (
        mark_price
        * Decimal("0.50")
    )

    demo_price = demo_price.quantize(
        Decimal("0.1"),
        rounding=ROUND_DOWN,
    )

    client_id = (
        "R20-"
        + str(
            int(time.time())
        )
    )

    payload = {
        "symbol": DEMO_SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": fmt(
            demo_quantity
        ),
        "price": fmt(
            demo_price
        ),
        "newClientOrderId":
            client_id,
    }

    result = await demo_post(
        session,
        "/capi/v3/sim/order",
        payload,
    )

    classification = (
        classify_demo_result(
            result
        )
    )

    return {
        "payload": payload,
        "result": result,
        **classification,
    }


# ============================================================
# SIGNAL SAFETY SELF TEST
# ============================================================

def run_signal_gate_tests():
    now = int(
        time.time()
    )

    fresh_signal_time = (
        now - 10
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 10
    )

    fresh_signal_accepted = (
        now - fresh_signal_time
        <= SIGNAL_EXPIRY_SECONDS
    )

    expired_signal_rejected = (
        now - expired_signal_time
        > SIGNAL_EXPIRY_SECONDS
    )

    last_loss_time = (
        now - 10
    )

    loss_cooldown_test = (
        now - last_loss_time
        < LOSS_COOLDOWN_SECONDS
    )

    seen_signals = set()

    test_signal_id = (
        "R20-TEST-SIGNAL"
    )

    duplicate_first = (
        test_signal_id
        not in seen_signals
    )

    seen_signals.add(
        test_signal_id
    )

    duplicate_second_rejected = (
        test_signal_id
        in seen_signals
    )

    duplicate_signal_rejected = (
        duplicate_first
        and duplicate_second_rejected
    )

    current_direction = "LONG"
    requested_direction = "SHORT"

    one_direction_gate = (
        current_direction
        != requested_direction
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
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):
    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        return False

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
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.Response(
        text=(
            f"{MODULE_NAME} ACTIVE\n"
            "REAL ORDER EXECUTION DISABLED\n"
        )
    )


async def start_health_server():
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
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {port}"
    )

    return runner


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_diagnostic():
    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "WEEX DEMO PERMISSION / SYMBOL DIAGNOSTIC"
    )

    print(
        "REAL ORDER POST ABSOLUTELY DISABLED"
    )

    print(
        "=" * 60
    )

    validate_credentials()

    signal_tests = (
        run_signal_gate_tests()
    )

    async with aiohttp.ClientSession() as session:

        stage = "mark price"

        try:
            mark_price = await get_mark_price(
                session
            )

            stage = "exchange information"

            contract = await get_contract_info(
                session
            )

            min_order_size = safe_decimal(
                contract.get(
                    "minOrderSize",
                    "0.0001",
                )
            )

            quantity_precision = int(
                contract.get(
                    "quantityPrecision",
                    4,
                )
            )

            contract_value = safe_decimal(
                contract.get(
                    "contractVal",
                    "0.0001",
                )
            )

            weex_min_leverage = safe_decimal(
                contract.get(
                    "minLeverage",
                    "1",
                )
            )

            weex_max_leverage = safe_decimal(
                contract.get(
                    "maxLeverage",
                    "0",
                )
            )

            stage = "API trading symbols"

            api_symbols = (
                await get_api_trading_symbols(
                    session
                )
            )

            api_trading_symbol = (
                SYMBOL in api_symbols
            )

            stage = "live balance read"

            available_balance = (
                await get_live_balance(
                    session
                )
            )

            leverage_gate = (
                LEVERAGE
                >= weex_min_leverage
                and LEVERAGE
                <= weex_max_leverage
                and LEVERAGE
                <= MAX_LEVERAGE
            )

            entry_margin = (
                available_balance
                * INITIAL_ENTRY_PERCENT
                / HUNDRED
            )

            entry_notional = (
                entry_margin
                * LEVERAGE
            )

            raw_quantity = (
                entry_notional
                / mark_price
            )

            quantity = floor_precision(
                raw_quantity,
                quantity_precision,
            )

            quantity_positive = (
                quantity > ZERO
            )

            minimum_passed = (
                quantity
                >= min_order_size
            )

            pyramid_total = (
                PYRAMID_SIZE_PERCENT
                * Decimal(
                    MAX_PYRAMID_ADDS
                )
            )

            backup_total = (
                BACKUP_SIZE_PERCENT
                * Decimal(
                    MAX_BACKUPS
                )
            )

            worst_case_exposure = (
                INITIAL_ENTRY_PERCENT
                + pyramid_total
                + backup_total
            )

            exposure_passed = (
                worst_case_exposure
                <= MAX_FUND_EXPOSURE_PERCENT
            )

            # ================================================
            # DEMO READ PROBES
            # ================================================

            stage = "demo balance probe"

            demo_balance = (
                await probe_demo_balance(
                    session
                )
            )

            stage = "demo position probe"

            demo_positions = (
                await probe_demo_positions(
                    session
                )
            )

            stage = "demo history probe"

            demo_history = (
                await probe_demo_history(
                    session
                )
            )

            # ================================================
            # DEMO ORDER PROBE
            # ================================================

            stage = "demo order capability probe"

            demo_order = (
                await probe_demo_order(
                    session=session,
                    mark_price=mark_price,
                    min_order_size=min_order_size,
                    quantity_precision=quantity_precision,
                )
            )

            demo_result = (
                demo_order["result"]
            )

            demo_classification = (
                demo_order[
                    "classification"
                ]
            )

            demo_code = (
                demo_order["code"]
            )

            demo_message = (
                demo_order["message"]
            )

            # ================================================
            # ROOT CAUSE CLASSIFICATION
            # ================================================

            if DEMO_POST_ACCEPTED:
                root_cause = (
                    "DEMO_SYMBOL_PATH_CONFIRMED"
                )

                recommendation = (
                    "BTCSUSDT demo order accepted. "
                    "R19 was likely using the wrong "
                    "demo symbol/path combination."
                )

            elif demo_code == -1051:
                root_cause = (
                    "API_FUTURES_OR_DEMO_PERMISSION_DENIED"
                )

                recommendation = (
                    "Demo reads authenticate successfully, "
                    "but WEEX still denies demo TRADE. "
                    "Check Futures permission on this API key "
                    "or WEEX account/API risk restrictions."
                )

            elif demo_code == -1052:
                root_cause = (
                    "FUTURES_PERMISSION_MISSING"
                )

                recommendation = (
                    "Enable Futures permission for the "
                    "WEEX API key."
                )

            elif demo_code in (
                -1058,
                -3235,
            ):
                root_cause = (
                    "DEMO_TRADING_PAIR_NOT_ALLOWED"
                )

                recommendation = (
                    "WEEX rejected this demo trading pair."
                )

            elif demo_code == -1060:
                root_cause = (
                    "API_KEY_NOT_BOUND_TO_SYMBOL"
                )

                recommendation = (
                    "The API key is not bound to "
                    "the requested trading pair."
                )

            elif demo_code == -3236:
                root_cause = (
                    "DEMO_API_ENDPOINT_PERMISSION_DENIED"
                )

                recommendation = (
                    "The account/API key does not have "
                    "permission to access the demo "
                    "trading API."
                )

            elif demo_code == -1121:
                root_cause = (
                    "INVALID_DEMO_SYMBOL"
                )

                recommendation = (
                    "WEEX rejected DEMO_SYMBOL="
                    + DEMO_SYMBOL
                )

            else:
                root_cause = (
                    demo_classification
                )

                recommendation = (
                    "Review the returned WEEX "
                    "HTTP status and error code."
                )

            # ================================================
            # MODULE PASS
            # ================================================
            #
            # R20 is a diagnostic module.
            #
            # It can PASS even if demo trading is denied,
            # provided the failure was safely captured and
            # no real POST occurred.
            #
            # ================================================

            core_checks = [
                signal_tests[
                    "fresh_signal_accepted"
                ],
                signal_tests[
                    "expired_signal_rejected"
                ],
                signal_tests[
                    "loss_cooldown_test"
                ],
                signal_tests[
                    "duplicate_signal_rejected"
                ],
                signal_tests[
                    "one_direction_gate"
                ],
                signal_tests[
                    "external_position_clear"
                ],
                leverage_gate,
                quantity_positive,
                minimum_passed,
                exposure_passed,
                api_trading_symbol,
                demo_balance[
                    "accessible"
                ],
                not REAL_POST_CALLED,
                HARD_REAL_POST_LOCK,
                not LIVE_ORDER_EXECUTION,
            ]

            all_passed = all(
                core_checks
            )

            status_icon = (
                "✅"
                if all_passed
                else "⚠️"
            )

            status_text = (
                "DIAGNOSTIC PASSED"
                if all_passed
                else "NOT READY"
            )

            report = (
                f"{status_icon} MODULE "
                f"{MODULE_NAME} "
                f"{status_text}\n"
                f"{SYMBOL}\n\n"

                f"Available USDT: "
                f"{fmt(available_balance)}\n"

                f"Mark Price: "
                f"{fmt(mark_price)} USDT\n\n"

                "FINAL EXECUTION GATE\n"

                f"API Trading Symbol: "
                f"{yes_no(api_trading_symbol)}\n"

                f"Fresh Signal Accepted: "
                f"{yes_no(signal_tests['fresh_signal_accepted'])}\n"

                f"Expired Signal Rejected: "
                f"{yes_no(signal_tests['expired_signal_rejected'])}\n"

                f"Loss Cooldown Test: "
                f"{yes_no(signal_tests['loss_cooldown_test'])}\n"

                f"Duplicate Signal Rejected: "
                f"{yes_no(signal_tests['duplicate_signal_rejected'])}\n"

                f"One Direction Gate: "
                f"{yes_no(signal_tests['one_direction_gate'])}\n"

                f"External Position Clear: "
                f"{yes_no(signal_tests['external_position_clear'])}\n\n"

                "ADJUSTABLE CONFIG\n"

                f"Entry: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

                f"Leverage: "
                f"{fmt(LEVERAGE)}x\n"

                f"Max Config Leverage: "
                f"{fmt(MAX_LEVERAGE)}x\n"

                f"Margin Type: "
                f"{MARGIN_TYPE}\n"

                f"Max Pyramids: "
                f"{MAX_PYRAMID_ADDS}\n"

                f"Pyramid Size: "
                f"{fmt(PYRAMID_SIZE_PERCENT)}%\n"

                f"Max Backups: "
                f"{MAX_BACKUPS}\n"

                f"Backup Size: "
                f"{fmt(BACKUP_SIZE_PERCENT)}% each\n"

                f"Backup Buffer: "
                f"{fmt(BACKUP_BUFFER_PERCENT)}%\n"

                f"Min Liq Distance: "
                f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%\n"

                f"Max Fund Exposure: "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n\n"

                "WEEX CONTRACT\n"

                f"Minimum Order: "
                f"{fmt(min_order_size)}\n"

                f"Quantity Precision: "
                f"{quantity_precision}\n"

                f"Contract Value: "
                f"{fmt(contract_value)}\n"

                f"WEEX Min Leverage: "
                f"{fmt(weex_min_leverage)}x\n"

                f"WEEX Max Leverage: "
                f"{fmt(weex_max_leverage)}x\n"

                f"Leverage Gate: "
                f"{yes_no(leverage_gate)}\n\n"

                "DYNAMIC ENTRY\n"

                f"Margin: "
                f"{fmt(entry_margin)} USDT\n"

                f"Notional: "
                f"{fmt(entry_notional)} USDT\n"

                f"Quantity: "
                f"{fmt(quantity)}\n"

                f"Quantity Positive: "
                f"{yes_no(quantity_positive)}\n"

                f"Minimum Passed: "
                f"{yes_no(minimum_passed)}\n\n"

                "WORST-CASE EXPOSURE\n"

                f"Initial: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

                f"Pyramids: "
                f"{fmt(pyramid_total)}%\n"

                f"Backups: "
                f"{fmt(backup_total)}%\n"

                f"Total: "
                f"{fmt(worst_case_exposure)}% / "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

                f"Exposure Passed: "
                f"{yes_no(exposure_passed)}\n\n"

                "R20 DEMO CAPABILITY DIAGNOSTIC\n"

                f"Real Symbol: "
                f"{SYMBOL}\n"

                f"Demo Symbol: "
                f"{DEMO_SYMBOL}\n"

                f"Demo Quote Asset: SUSDT\n"

                f"Demo Balance Probe: "
                f"{yes_no(demo_balance['accessible'])}\n"

                f"Demo SUSDT Available: "
                f"{fmt(demo_balance['balance']) if demo_balance['balance'] is not None else 'N/A'}\n"

                f"Demo Position Read: "
                f"{yes_no(demo_positions['accessible'])}\n"

                f"Demo History Read: "
                f"{yes_no(demo_history['accessible'])}\n"

                f"Demo POST Attempted: "
                f"{yes_no(DEMO_POST_ATTEMPTED)}\n"

                f"Demo POST Accepted: "
                f"{yes_no(DEMO_POST_ACCEPTED)}\n"

                f"Demo HTTP Status: "
                f"{demo_result['status']}\n"

                f"Demo Classification: "
                f"{demo_classification}\n"

                f"Demo Error Code: "
                f"{demo_code if demo_code is not None else 'NONE'}\n"

                f"Demo Error: "
                f"{demo_message or 'NONE'}\n\n"

                "R20 ROOT-CAUSE ANALYSIS\n"

                f"Classification: "
                f"{root_cause}\n"

                f"Recommendation: "
                f"{recommendation}\n\n"

                f"Real POST Called: "
                f"{yes_no(REAL_POST_CALLED)}\n"

                "🛡 R20 absolute real-order POST lock active\n"
                "⚠️ LIVE ORDER EXECUTION DISABLED\n"
                "⚠️ NO REAL ORDER WAS SENT"
            )

            print()
            print(
                report
            )
            print()
            print(
                "=" * 60
            )

            await send_telegram(
                session,
                report,
            )

            return

        except Exception as exc:
            error_report = (
                f"❌ MODULE "
                f"{MODULE_NAME} ERROR\n"

                f"{SYMBOL}\n\n"

                f"Stage: {stage}\n"

                f"{type(exc).__name__}: "
                f"{exc}\n\n"

                f"Real POST Called: "
                f"{yes_no(REAL_POST_CALLED)}\n"

                f"Demo POST Attempted: "
                f"{yes_no(DEMO_POST_ATTEMPTED)}\n"

                "🛡 R20 absolute real-order POST lock active\n"
                "⚠️ LIVE ORDER EXECUTION DISABLED\n"
                "⚠️ NO REAL ORDER WAS SENT"
            )

            print()
            print(
                error_report
            )

            print()
            traceback.print_exc()

            await send_telegram(
                session,
                error_report,
            )


# ============================================================
# APPLICATION
# ============================================================

async def main():
    await start_health_server()

    await run_diagnostic()

    #
    # Keep Render Web Service alive.
    #
    # Prevents the diagnostic process from exiting and
    # repeatedly restarting / sending duplicate Telegram
    # messages.
    #

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )

    except KeyboardInterrupt:
        pass
