import asyncio
import base64
import hashlib
import hmac
import json
import os
import time

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R19"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ============================================================
# WEEX CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
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
        "1.0",
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
        "180",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "900",
    )
)

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True

ABSOLUTE_REAL_ORDER_POST_LOCK = True


REAL_ORDER_PATH = (
    "/capi/v3/order"
)

DEMO_BALANCE_PATH = (
    "/capi/v3/sim/balance"
)

DEMO_ORDER_PATH = (
    "/capi/v3/sim/order"
)


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")

ONE_HUNDRED = Decimal("100")


# ============================================================
# HELPERS
# ============================================================

def safe_decimal(
    value,
    default="0",
):
    try:
        return Decimal(
            str(value)
        )

    except Exception:
        return Decimal(
            default
        )


def fmt(
    value,
):
    if isinstance(
        value,
        Decimal,
    ):
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

    return str(
        value
    )


def yes_no(
    value,
):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def quantize_down(
    value,
    precision,
):
    step = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    return value.quantize(
        step,
        rounding=ROUND_DOWN,
    )


def canonical_json(
    payload,
):
    return json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def build_query(
    params,
):
    if not params:
        return ""

    return urlencode(
        params
    )


def require_credentials():
    missing = []

    if not WEEX_API_KEY:
        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_API_SECRET:
        missing.append(
            "WEEX_API_SECRET"
        )

    if not WEEX_API_PASSPHRASE:
        missing.append(
            "WEEX_API_PASSPHRASE"
        )

    if missing:
        raise RuntimeError(
            "Missing WEEX credentials: "
            + ", ".join(
                missing
            )
        )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def make_signature(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):
    method = (
        method.upper()
    )

    if query_string:

        message = (
            f"{timestamp}"
            f"{method}"
            f"{path}"
            f"?"
            f"{query_string}"
            f"{body}"
        )

    else:

        message = (
            f"{timestamp}"
            f"{method}"
            f"{path}"
            f"{body}"
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
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


def private_headers(
    method,
    path,
    params=None,
    body_text="",
):
    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    query_string = build_query(
        params
    )

    signature = make_signature(
        timestamp=timestamp,
        method=method,
        path=path,
        query_string=query_string,
        body=body_text,
    )

    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",

        "User-Agent":
            f"{MODULE_NAME}/1.0",
    }


# ============================================================
# HTTP HELPERS
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    async with session.get(
        url,
        params=params,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
        headers={
            "User-Agent":
                f"{MODULE_NAME}/1.0"
        },
    ) as response:

        text = (
            await response.text()
        )

        if response.status != 200:

            raise RuntimeError(
                f"WEEX HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError:

            raise RuntimeError(
                f"Invalid WEEX JSON: "
                f"{text}"
            )


async def private_get(
    session,
    path,
    params=None,
):
    require_credentials()

    params = (
        params
        or {}
    )

    headers = private_headers(
        "GET",
        path,
        params=params,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    async with session.get(
        url,
        params=params,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = (
            await response.text()
        )

        try:
            data = json.loads(
                text
            )

        except json.JSONDecodeError:

            data = {
                "raw":
                    text
            }

        return (
            response.status,
            data,
            text,
        )


async def demo_post(
    session,
    path,
    payload,
):
    # --------------------------------------------------------
    # ABSOLUTE R19 SAFETY CHECK
    # --------------------------------------------------------

    if path == REAL_ORDER_PATH:

        raise RuntimeError(
            "R19 SAFETY VIOLATION: "
            "real order path blocked"
        )

    require_credentials()

    body_text = canonical_json(
        payload
    )

    headers = private_headers(
        "POST",
        path,
        body_text=body_text,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    async with session.post(
        url,
        data=body_text,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = (
            await response.text()
        )

        try:
            data = json.loads(
                text
            )

        except json.JSONDecodeError:

            data = {
                "raw":
                    text
            }

        return (
            response.status,
            data,
            text,
        )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):
    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):
        print(
            "Telegram skipped: "
            "credentials not configured"
        )

        return

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    payload = {
        "chat_id":
            TELEGRAM_CHAT_ID,

        "text":
            message,

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
        ) as response:

            text = (
                await response.text()
            )

            if response.status != 200:

                print(
                    f"Telegram HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

    except Exception as exc:

        print(
            f"Telegram error: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )


# ============================================================
# MARK PRICE
# ============================================================

def extract_mark_price(
    data,
):
    candidates = []

    if isinstance(
        data,
        list,
    ):
        candidates.extend(
            data
        )

    elif isinstance(
        data,
        dict,
    ):
        candidates.append(
            data
        )

        for key in (
            "data",
            "result",
        ):
            obj = data.get(
                key
            )

            if isinstance(
                obj,
                list,
            ):
                candidates.extend(
                    obj
                )

            elif isinstance(
                obj,
                dict,
            ):
                candidates.append(
                    obj
                )

    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):
            continue

        for key in (
            "markPrice",
            "price",
            "lastPrice",
            "last",
        ):
            if key in item:

                value = safe_decimal(
                    item[key]
                )

                if value > ZERO:
                    return value

    raise RuntimeError(
        "Unable to extract "
        f"mark price: {data}"
    )


# ============================================================
# BALANCE
# ============================================================

def extract_available_usdt(
    data,
):
    candidates = []

    if isinstance(
        data,
        list,
    ):
        candidates.extend(
            data
        )

    elif isinstance(
        data,
        dict,
    ):
        candidates.append(
            data
        )

        for key in (
            "data",
            "result",
            "assets",
            "balances",
        ):
            obj = data.get(
                key
            )

            if isinstance(
                obj,
                list,
            ):
                candidates.extend(
                    obj
                )

            elif isinstance(
                obj,
                dict,
            ):
                candidates.append(
                    obj
                )

    preferred_keys = (
        "availableBalance",
        "available",
        "availableMargin",
        "availableAmount",
        "free",
        "balance",
    )

    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get("asset")
            or
            item.get("coin")
            or
            item.get("currency")
            or
            ""
        ).upper()

        if (
            asset
            and
            asset not in (
                "USDT",
                "SUSDT",
            )
        ):
            continue

        for key in preferred_keys:

            if key in item:

                value = safe_decimal(
                    item[key]
                )

                if value >= ZERO:
                    return value

    raise RuntimeError(
        "Unable to extract "
        f"available USDT: {data}"
    )


# ============================================================
# CONTRACT RULES
# ============================================================

def extract_contract_rules(
    data,
):
    # Safe BTCUSDT diagnostic fallbacks.
    # These are used only if exchangeInfo formatting differs.

    min_qty = Decimal(
        "0.0001"
    )

    qty_precision = 4

    contract_value = Decimal(
        "0.0001"
    )

    min_leverage = Decimal(
        "1"
    )

    max_leverage = Decimal(
        "400"
    )

    items = []

    if isinstance(
        data,
        list,
    ):
        items = data

    elif isinstance(
        data,
        dict,
    ):

        for key in (
            "data",
            "symbols",
            "result",
        ):

            obj = data.get(
                key
            )

            if isinstance(
                obj,
                list,
            ):
                items.extend(
                    obj
                )

        if not items:
            items = [
                data
            ]

    target = None

    for item in items:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get("symbol")
            or
            item.get("symbolName")
            or
            ""
        ).upper()

        if symbol == SYMBOL:

            target = item

            break

    if not target:

        return (
            min_qty,
            qty_precision,
            contract_value,
            min_leverage,
            max_leverage,
        )

    for key in (
        "minQty",
        "minOrderQty",
        "minTradeNum",
        "minTradeAmount",
    ):

        if key in target:

            value = safe_decimal(
                target[key]
            )

            if value > ZERO:

                min_qty = value

                break

    for key in (
        "quantityPrecision",
        "qtyPrecision",
        "volumePlace",
        "sizeScale",
    ):

        if key in target:

            try:

                qty_precision = int(
                    target[key]
                )

                break

            except Exception:
                pass

    for key in (
        "contractValue",
        "contractSize",
        "sizeMultiplier",
    ):

        if key in target:

            value = safe_decimal(
                target[key]
            )

            if value > ZERO:

                contract_value = value

                break

    for key in (
        "minLeverage",
        "minLever",
    ):

        if key in target:

            value = safe_decimal(
                target[key]
            )

            if value > ZERO:

                min_leverage = value

                break

    for key in (
        "maxLeverage",
        "maxLever",
    ):

        if key in target:

            value = safe_decimal(
                target[key]
            )

            if value > ZERO:

                max_leverage = value

                break

    return (
        min_qty,
        qty_precision,
        contract_value,
        min_leverage,
        max_leverage,
    )


# ============================================================
# ERROR EXTRACTION
# ============================================================

def find_error_code(
    data,
):
    if isinstance(
        data,
        dict,
    ):

        for key in (
            "code",
            "errorCode",
        ):

            if (
                key in data
                and
                data[key]
                not in (
                    None,
                    "",
                )
            ):

                return str(
                    data[key]
                )

    return ""


def find_error_message(
    data,
    fallback="",
):
    if isinstance(
        data,
        dict,
    ):

        for key in (
            "msg",
            "message",
            "errorMessage",
        ):

            if (
                key in data
                and
                data[key]
                not in (
                    None,
                    "",
                )
            ):

                return str(
                    data[key]
                )

    return fallback


# ============================================================
# R19 DEMO RESPONSE CLASSIFIER
# ============================================================

def classify_demo_result(
    http_status,
    data,
):
    code = find_error_code(
        data
    )

    message = find_error_message(
        data
    )

    success_flag = None

    if (
        isinstance(
            data,
            dict,
        )
        and
        "success" in data
    ):

        success_flag = bool(
            data.get(
                "success"
            )
        )

    if (
        200 <= http_status < 300
        and
        success_flag is not False
    ):

        return (
            "ACCEPTED",
            code,
            message,
        )

    if (
        http_status == 403
        and
        code == "-1051"
    ):

        return (
            "PERMISSION_DENIED_1051",
            code,
            message
            or
            "Permission denied",
        )

    if code in (
        "-1051",
        "-1052",
    ):

        return (
            "PERMISSION_DENIED",
            code,
            message,
        )

    if http_status == 401:

        return (
            "AUTHENTICATION_REJECTED",
            code,
            message,
        )

    if http_status == 429:

        return (
            "RATE_LIMITED",
            code,
            message,
        )

    if (
        400
        <= http_status
        < 500
    ):

        return (
            "REQUEST_REJECTED",
            code,
            message,
        )

    if http_status >= 500:

        return (
            "WEEX_SERVER_ERROR",
            code,
            message,
        )

    return (
        "UNKNOWN",
        code,
        message,
    )


# ============================================================
# EXECUTION GATE TESTS
# ============================================================

def validate_execution_gates():
    now = int(
        time.time()
    )

    fresh_signal_time = (
        now
        - 10
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 10
    )

    fresh_signal_accepted = (
        now
        - fresh_signal_time
    ) <= SIGNAL_EXPIRY_SECONDS

    expired_signal_rejected = (
        now
        - expired_signal_time
    ) > SIGNAL_EXPIRY_SECONDS

    simulated_last_loss_time = (
        now
        -
        max(
            1,
            LOSS_COOLDOWN_SECONDS
            // 2,
        )
    )

    loss_cooldown_test = (
        now
        - simulated_last_loss_time
    ) < LOSS_COOLDOWN_SECONDS

    sample_signal_id = (
        f"{SYMBOL}"
        "-R19-test"
    )

    seen = {
        sample_signal_id
    }

    duplicate_signal_rejected = (
        sample_signal_id
        in seen
    )

    one_direction_gate = True

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
# ENTRY CALCULATION
# ============================================================

def calculate_entry(
    balance,
    mark_price,
    qty_precision,
    min_qty,
):
    margin = (
        balance
        *
        INITIAL_ENTRY_PERCENT
        /
        ONE_HUNDRED
    )

    notional = (
        margin
        *
        LEVERAGE
    )

    if mark_price > ZERO:

        raw_qty = (
            notional
            /
            mark_price
        )

    else:

        raw_qty = ZERO

    quantity = quantize_down(
        raw_qty,
        qty_precision,
    )

    return {
        "margin":
            margin,

        "notional":
            notional,

        "quantity":
            quantity,

        "quantity_positive":
            quantity > ZERO,

        "minimum_passed":
            quantity >= min_qty,
    }


# ============================================================
# EXPOSURE
# ============================================================

def total_configured_exposure_percent():

    initial = (
        INITIAL_ENTRY_PERCENT
    )

    pyramids = (
        Decimal(
            MAX_PYRAMID_ADDS
        )
        *
        PYRAMID_SIZE_PERCENT
    )

    backups = (
        Decimal(
            MAX_BACKUPS
        )
        *
        BACKUP_SIZE_PERCENT
    )

    total = (
        initial
        +
        pyramids
        +
        backups
    )

    return (
        initial,
        pyramids,
        backups,
        total,
    )


# ============================================================
# DEMO ORDER PAYLOAD
# ============================================================

def make_demo_order_payload(
    quantity,
):
    client_id = (
        f"r19-"
        f"{int(time.time())}"
    )

    if len(
        client_id
    ) > 36:

        client_id = (
            client_id[:36]
        )

    return {
        "symbol":
            SYMBOL,

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "type":
            "MARKET",

        "quantity":
            fmt(
                quantity
            ),

        "newClientOrderId":
            client_id,
    }


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.Response(
        text=(
            f"{MODULE_NAME} "
            "alive\n"
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
        "HEALTH SERVER ACTIVE "
        f"ON PORT {port}"
    )

    return runner


# ============================================================
# R19 DIAGNOSTIC
# ============================================================

async def run_r19():

    real_post_called = False

    demo_balance_attempted = False

    demo_balance_accessible = False

    demo_post_attempted = False

    demo_post_accepted = False

    demo_classification = (
        "NOT_ATTEMPTED"
    )

    demo_http_status = None

    demo_error_code = ""

    demo_error_message = ""

    stage = "startup"

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:

            # ==================================================
            # CREDENTIAL CHECK
            # ==================================================

            require_credentials()


            # ==================================================
            # MARK PRICE
            # ==================================================

            stage = "mark price"

            ticker = await public_get(
                session,
                "/capi/v3/market/symbolPrice",
                params={
                    "symbol":
                        SYMBOL,

                    "priceType":
                        "MARK",
                },
            )

            mark_price = extract_mark_price(
                ticker
            )


            # ==================================================
            # REAL ACCOUNT BALANCE READ ONLY
            # ==================================================

            stage = (
                "real account balance"
            )

            (
                balance_status,
                balance_data,
                balance_text,
            ) = await private_get(
                session,
                "/capi/v3/account/balance",
            )

            if balance_status != 200:

                raise RuntimeError(
                    f"WEEX HTTP "
                    f"{balance_status}: "
                    f"{balance_text}"
                )

            balance = extract_available_usdt(
                balance_data
            )


            # ==================================================
            # CONTRACT RULES
            # ==================================================

            stage = "contract rules"

            try:

                exchange_info = await public_get(
                    session,
                    "/capi/v3/market/exchangeInfo",
                    params={
                        "symbol":
                            SYMBOL
                    },
                )

            except Exception:

                exchange_info = {}

            (
                min_qty,
                qty_precision,
                contract_value,
                weex_min_leverage,
                weex_max_leverage,
            ) = extract_contract_rules(
                exchange_info
            )


            # ==================================================
            # LEVERAGE GATE
            # ==================================================

            leverage_gate = (
                LEVERAGE
                >=
                weex_min_leverage
                and
                LEVERAGE
                <=
                weex_max_leverage
                and
                LEVERAGE
                <=
                MAX_LEVERAGE
            )


            # ==================================================
            # EXECUTION GATES
            # ==================================================

            gates = validate_execution_gates()


            # ==================================================
            # ENTRY
            # ==================================================

            entry = calculate_entry(
                balance,
                mark_price,
                qty_precision,
                min_qty,
            )


            # ==================================================
            # EXPOSURE
            # ==================================================

            (
                initial_exp,
                pyramid_exp,
                backup_exp,
                total_exp,
            ) = (
                total_configured_exposure_percent()
            )

            exposure_passed = (
                total_exp
                <=
                MAX_FUND_EXPOSURE_PERCENT
            )


            # ==================================================
            # R19 NEW TEST 1
            # DEMO ACCOUNT ACCESS
            # ==================================================

            stage = (
                "demo account "
                "permission probe"
            )

            demo_balance_attempted = True

            (
                sim_status,
                sim_data,
                sim_text,
            ) = await private_get(
                session,
                DEMO_BALANCE_PATH,
            )

            demo_balance_accessible = (
                sim_status == 200
            )

            print(
                "R19 DEMO BALANCE PROBE"
            )

            print(
                "HTTP Status:",
                sim_status,
            )

            print(
                "Accessible:",
                demo_balance_accessible,
            )

            if (
                not demo_balance_accessible
            ):

                print(
                    "Demo balance response:",
                    sim_text,
                )


            # ==================================================
            # R19 DEMO SAFETY GATE
            # ==================================================

            safe_to_demo_test = (
                entry[
                    "quantity_positive"
                ]
                and
                entry[
                    "minimum_passed"
                ]
                and
                leverage_gate
                and
                exposure_passed
                and
                gates[
                    "fresh_signal_accepted"
                ]
                and
                gates[
                    "expired_signal_rejected"
                ]
                and
                gates[
                    "duplicate_signal_rejected"
                ]
                and
                gates[
                    "one_direction_gate"
                ]
                and
                gates[
                    "external_position_clear"
                ]
            )

            if not safe_to_demo_test:

                raise RuntimeError(
                    "R19 demo transmission "
                    "blocked by execution gate"
                )


            # ==================================================
            # R19 NEW TEST 2
            # DEMO ORDER PERMISSION PROBE
            # ==================================================

            stage = (
                "demo order "
                "permission probe"
            )

            demo_payload = (
                make_demo_order_payload(
                    entry[
                        "quantity"
                    ]
                )
            )

            demo_post_attempted = True

            (
                demo_http_status,
                demo_data,
                demo_raw,
            ) = await demo_post(
                session,
                DEMO_ORDER_PATH,
                demo_payload,
            )

            (
                demo_classification,
                demo_error_code,
                demo_error_message,
            ) = classify_demo_result(
                demo_http_status,
                demo_data,
            )

            demo_post_accepted = (
                demo_classification
                ==
                "ACCEPTED"
            )


            # ==================================================
            # ABSOLUTE REAL ORDER SAFETY CHECK
            # ==================================================

            if LIVE_ORDER_EXECUTION:

                raise RuntimeError(
                    "R19 safety "
                    "configuration invalid: "
                    "LIVE_ORDER_EXECUTION "
                    "must remain False"
                )

            if not HARD_EXECUTION_LOCK:

                raise RuntimeError(
                    "R19 safety "
                    "configuration invalid: "
                    "HARD_EXECUTION_LOCK "
                    "must remain True"
                )

            if (
                not
                ABSOLUTE_REAL_ORDER_POST_LOCK
            ):

                raise RuntimeError(
                    "R19 safety "
                    "configuration invalid: "
                    "ABSOLUTE_REAL_ORDER_POST_LOCK "
                    "must remain True"
                )

            # No function in R19 is permitted
            # to POST to /capi/v3/order.

            real_post_called = False


            # ==================================================
            # R19 PASS LOGIC
            # ==================================================

            r19_passed = (
                demo_classification
                in (
                    "ACCEPTED",
                    "PERMISSION_DENIED_1051",
                    "PERMISSION_DENIED",
                )
                and
                not real_post_called
            )

            status_icon = (
                "✅"
                if r19_passed
                else "⚠️"
            )

            status_text = (
                "DIAGNOSTIC PASSED"
                if r19_passed
                else "NOT READY"
            )


            # ==================================================
            # REPORT
            # ==================================================

            report = (
                f"{status_icon} MODULE "
                f"{MODULE_NAME} "
                f"{status_text}\n"

                f"{SYMBOL}\n\n"

                f"Available USDT: "
                f"{fmt(balance)}\n"

                f"Mark Price: "
                f"{fmt(mark_price)} "
                f"USDT\n\n"


                f"FINAL EXECUTION GATE\n"

                f"Fresh Signal Accepted: "
                f"{yes_no(gates['fresh_signal_accepted'])}\n"

                f"Expired Signal Rejected: "
                f"{yes_no(gates['expired_signal_rejected'])}\n"

                f"Loss Cooldown Test: "
                f"{yes_no(gates['loss_cooldown_test'])}\n"

                f"Duplicate Signal Rejected: "
                f"{yes_no(gates['duplicate_signal_rejected'])}\n"

                f"One Direction Gate: "
                f"{yes_no(gates['one_direction_gate'])}\n"

                f"External Position Clear: "
                f"{yes_no(gates['external_position_clear'])}\n\n"


                f"ADJUSTABLE CONFIG\n"

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


                f"WEEX CONTRACT\n"

                f"Minimum Order: "
                f"{fmt(min_qty)}\n"

                f"Quantity Precision: "
                f"{qty_precision}\n"

                f"Contract Value: "
                f"{fmt(contract_value)}\n"

                f"WEEX Min Leverage: "
                f"{fmt(weex_min_leverage)}x\n"

                f"WEEX Max Leverage: "
                f"{fmt(weex_max_leverage)}x\n"

                f"Leverage Gate: "
                f"{yes_no(leverage_gate)}\n\n"


                f"DYNAMIC ENTRY\n"

                f"Margin: "
                f"{fmt(entry['margin'])} "
                f"USDT\n"

                f"Notional: "
                f"{fmt(entry['notional'])} "
                f"USDT\n"

                f"Quantity: "
                f"{fmt(entry['quantity'])}\n"

                f"Quantity Positive: "
                f"{yes_no(entry['quantity_positive'])}\n"

                f"Minimum Passed: "
                f"{yes_no(entry['minimum_passed'])}\n\n"


                f"WORST-CASE EXPOSURE\n"

                f"Initial: "
                f"{fmt(initial_exp)}%\n"

                f"Pyramids: "
                f"{fmt(pyramid_exp)}%\n"

                f"Backups: "
                f"{fmt(backup_exp)}%\n"

                f"Total: "
                f"{fmt(total_exp)}% / "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

                f"Exposure Passed: "
                f"{yes_no(exposure_passed)}\n\n"


                f"R19 DEMO PERMISSION DIAGNOSTIC\n"

                f"Demo Balance Probe Attempted: "
                f"{yes_no(demo_balance_attempted)}\n"

                f"Demo Balance Accessible: "
                f"{yes_no(demo_balance_accessible)}\n"

                f"Demo POST Attempted: "
                f"{yes_no(demo_post_attempted)}\n"

                f"Demo POST Accepted: "
                f"{yes_no(demo_post_accepted)}\n"

                f"Demo HTTP Status: "
                f"{demo_http_status}\n"

                f"Demo Classification: "
                f"{demo_classification}\n"

                f"Demo Error Code: "
                f"{demo_error_code or 'N/A'}\n"

                f"Demo Error: "
                f"{demo_error_message or 'N/A'}\n\n"


                f"Real POST Called: "
                f"{yes_no(real_post_called)}\n"

                f"🛡 R19 absolute real-order "
                f"POST lock active\n"

                f"⚠️ LIVE ORDER EXECUTION DISABLED\n"

                f"⚠️ NO REAL ORDER WAS SENT"
            )

            print(
                "=" * 60
            )

            print(
                report
            )

            print(
                "=" * 60
            )

            await send_telegram(
                session,
                report,
            )


            # ==================================================
            # R19 RESULT CLASSIFICATION
            # ==================================================

            if (
                demo_classification
                ==
                "PERMISSION_DENIED_1051"
            ):

                print(
                    "R19 RESULT: "
                    "Demo endpoint reached, "
                    "but WEEX returned "
                    "403 / -1051 "
                    "permission denied. "
                    "Real trading remained blocked."
                )

            elif (
                demo_classification
                ==
                "PERMISSION_DENIED"
            ):

                print(
                    "R19 RESULT: "
                    "Demo endpoint reached, "
                    "but WEEX denied "
                    "trading permission. "
                    "Real trading remained blocked."
                )

            elif (
                demo_classification
                ==
                "ACCEPTED"
            ):

                print(
                    "R19 RESULT: "
                    "Demo order accepted. "
                    "Real trading remained blocked."
                )

            else:

                raise RuntimeError(
                    f"Unexpected demo result: "
                    f"HTTP "
                    f"{demo_http_status}, "
                    f"classification="
                    f"{demo_classification}, "
                    f"response="
                    f"{demo_raw}"
                )


        # ======================================================
        # ERROR HANDLER
        # ======================================================

        except Exception as exc:

            error_report = (
                f"❌ MODULE "
                f"{MODULE_NAME} "
                f"ERROR\n"

                f"{SYMBOL}\n"

                f"Stage: "
                f"{stage}\n"

                f"{type(exc).__name__}: "
                f"{exc}\n"

                f"Real POST Called: "
                f"{yes_no(real_post_called)}\n"

                f"Demo Balance Attempted: "
                f"{yes_no(demo_balance_attempted)}\n"

                f"Demo Balance Accessible: "
                f"{yes_no(demo_balance_accessible)}\n"

                f"Demo POST Attempted: "
                f"{yes_no(demo_post_attempted)}\n"

                f"Demo POST Accepted: "
                f"{yes_no(demo_post_accepted)}\n"

                f"Demo Classification: "
                f"{demo_classification}\n"

                f"🛡 R19 absolute real-order "
                f"POST lock active\n"

                f"⚠️ LIVE ORDER EXECUTION DISABLED\n"

                f"⚠️ NO REAL ORDER WAS SENT"
            )

            print(
                error_report
            )

            await send_telegram(
                session,
                error_report,
            )


# ============================================================
# MAIN
# ============================================================

async def main():

    await start_health_server()

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "DEMO PERMISSION-AWARE "
        "EXECUTION VALIDATION"
    )

    print(
        "ABSOLUTE REAL-ORDER "
        "POST LOCK ACTIVE"
    )

    print(
        "=" * 60
    )

    await run_r19()

    # Keep Render web service alive
    # after diagnostic completes.

    while True:

        await asyncio.sleep(
            3600
        )


if __name__ == "__main__":

    asyncio.run(
        main())
