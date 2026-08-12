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

MODULE_NAME = "0F-4H-R18"

API_BASE_URL = "https://api-contract.weex.com"

LIVE_SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

# WEEX V3 demo-mode symbols use SUSDT.
DEMO_SYMBOL = os.getenv(
    "DEMO_SYMBOL",
    "BTCSUSDT",
).strip().upper()


# ============================================================
# R18 EXECUTION POLICY
# ============================================================
#
# REAL ORDERS:
#     ABSOLUTELY LOCKED
#
# DEMO ORDERS:
#     ENABLED FOR ONE CONTROLLED TRANSMISSION
#
# R18 exists only to validate:
#
# 1. Authentication
# 2. Signature
# 3. Demo endpoint
# 4. Demo payload format
# 5. WEEX response
#
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_REAL_ORDER_LOCK = True

DEMO_ORDER_EXECUTION = (
    os.getenv(
        "R18_DEMO_ORDER_EXECUTION",
        "true",
    ).strip().lower()
    in ("1", "true", "yes", "on")
)

# One attempt per running process.
DEMO_POST_ALREADY_ATTEMPTED = False


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
# ADJUSTABLE TRADING CONFIG
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
# R18 DEMO ORDER
# ============================================================

DEMO_ORDER_SIDE = os.getenv(
    "R18_DEMO_SIDE",
    "BUY",
).strip().upper()

DEMO_POSITION_SIDE = os.getenv(
    "R18_DEMO_POSITION_SIDE",
    "LONG",
).strip().upper()

DEMO_ORDER_TYPE = "MARKET"

# Fixed ID deliberately prevents R18 from intentionally
# generating a new ID after every Render restart.
DEMO_CLIENT_ORDER_ID = os.getenv(
    "R18_DEMO_CLIENT_ORDER_ID",
    "0F4HR18-BTC-LONG-001",
).strip()


# ============================================================
# BTCUSDT CONTRACT BASELINE CONFIRMED BY R17
# ============================================================

MIN_ORDER_QTY = Decimal("0.0001")
QUANTITY_PRECISION = 4
CONTRACT_VALUE = Decimal("0.0001")

WEEX_MIN_LEVERAGE = Decimal("1")
WEEX_MAX_LEVERAGE = Decimal("400")


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")

HTTP_TIMEOUT = aiohttp.ClientTimeout(
    total=20
)


# ============================================================
# UTILITIES
# ============================================================

def safe_decimal(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        return Decimal(
            str(value)
        )

    except Exception:
        return Decimal(default)


def fmt(value):
    if isinstance(value, Decimal):
        text = format(
            value,
            "f",
        )

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return text or "0"

    return str(value)


def floor_decimal(
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


def yes_no(value):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


# ============================================================
# CREDENTIAL VALIDATION
# ============================================================

def validate_weex_credentials():
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

def generate_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body_string="",
):
    method = method.upper()

    if query_string:
        message = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body_string
        )
    else:
        message = (
            timestamp
            + method
            + request_path
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


def signed_headers(
    method,
    request_path,
    query_string="",
    body_string="",
):
    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = generate_signature(
        timestamp,
        method,
        request_path,
        query_string,
        body_string,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
    }


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

    headers = signed_headers(
        "GET",
        path,
        query_string,
        "",
    )

    url = (
        f"{API_BASE_URL}{path}"
    )

    async with session.get(
        url,
        params=params,
        headers=headers,
        timeout=HTTP_TIMEOUT,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX GET HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(text)

        except Exception:
            raise RuntimeError(
                "Invalid WEEX JSON response: "
                + text
            )


# ============================================================
# PUBLIC MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):
    path = (
        "/capi/v3/market/symbolPrice"
    )

    params = {
        "symbol": LIVE_SYMBOL,
        "priceType": "MARK",
    }

    url = (
        f"{API_BASE_URL}{path}"
    )

    async with session.get(
        url,
        params=params,
        timeout=HTTP_TIMEOUT,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            data = json.loads(text)

        except Exception:
            raise RuntimeError(
                "Invalid mark-price JSON: "
                + text
            )

        return extract_mark_price(
            data
        )


def extract_mark_price(
    ticker,
):
    if isinstance(
        ticker,
        list,
    ):
        if not ticker:
            raise RuntimeError(
                "Empty ticker response"
            )

        ticker = ticker[0]

    if isinstance(
        ticker,
        dict,
    ):
        possible = [
            ticker,
            ticker.get("data"),
            ticker.get("result"),
        ]

        for obj in possible:

            if isinstance(
                obj,
                list,
            ):
                if obj:
                    obj = obj[0]

            if not isinstance(
                obj,
                dict,
            ):
                continue

            for key in (
                "markPrice",
                "price",
                "lastPrice",
                "last",
            ):
                if key in obj:
                    value = safe_decimal(
                        obj[key]
                    )

                    if value > ZERO:
                        return value

    raise RuntimeError(
        "Unable to extract mark price"
    )


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_available_usdt(
    session,
):
    paths = [
        (
            "/capi/v2/account/getAccounts",
            {},
        ),
        (
            "/capi/v3/account/assets",
            {},
        ),
    ]

    errors = []

    for path, params in paths:

        try:
            data = await private_get(
                session,
                path,
                params,
            )

            balance = extract_available_usdt(
                data
            )

            if balance >= ZERO:
                return balance

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Unable to extract available USDT: "
        + " | ".join(errors)
    )


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
            "list",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                candidates.extend(
                    value
                )

            elif isinstance(
                value,
                dict,
            ):
                candidates.append(
                    value
                )

    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):
            continue

        coin = str(
            item.get(
                "coinName",
                item.get(
                    "asset",
                    item.get(
                        "coin",
                        "",
                    ),
                ),
            )
        ).upper()

        if coin and coin != "USDT":
            continue

        for key in (
            "available",
            "availableBalance",
            "availableAmount",
            "balance",
        ):
            if key in item:
                value = safe_decimal(
                    item[key]
                )

                if value >= ZERO:
                    return value

    raise RuntimeError(
        "Available USDT field not found"
    )


# ============================================================
# LIVE POSITION CHECK
# ============================================================

async def check_live_position(
    session,
):
    paths = [
        (
            "/capi/v3/account/position/singlePosition",
            {
                "symbol": LIVE_SYMBOL,
            },
        ),
        (
            "/capi/v2/account/position/singlePosition",
            {
                "symbol": LIVE_SYMBOL,
            },
        ),
    ]

    for path, params in paths:

        try:
            data = await private_get(
                session,
                path,
                params,
            )

            return extract_position_state(
                data
            )

        except Exception:
            continue

    # R18 does NOT allow inability to verify a
    # live position to trigger a real order because
    # real orders are structurally impossible.
    return False, None


def extract_position_state(
    data,
):
    entries = []

    if isinstance(
        data,
        list,
    ):
        entries = data

    elif isinstance(
        data,
        dict,
    ):
        entries = [
            data
        ]

        nested = data.get(
            "data"
        )

        if isinstance(
            nested,
            list,
        ):
            entries = nested

        elif isinstance(
            nested,
            dict,
        ):
            entries = [
                nested
            ]

    for item in entries:

        if not isinstance(
            item,
            dict,
        ):
            continue

        quantity = ZERO

        for key in (
            "quantity",
            "size",
            "positionAmt",
            "holdVolume",
            "total",
        ):
            if key in item:
                quantity = abs(
                    safe_decimal(
                        item[key]
                    )
                )

                if quantity > ZERO:
                    return True, item

    return False, None


# ============================================================
# DEMO ACCOUNT BALANCE
# ============================================================

async def get_demo_balance(
    session,
):
    try:
        data = await private_get(
            session,
            "/capi/v3/sim/balance",
        )

        return data

    except Exception as exc:
        return {
            "error": str(exc)
        }


# ============================================================
# ENTRY CALCULATION
# ============================================================

def calculate_entry(
    available_usdt,
    mark_price,
):
    margin = (
        available_usdt
        * INITIAL_ENTRY_PERCENT
        / ONE_HUNDRED
    )

    notional = (
        margin
        * LEVERAGE
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = floor_decimal(
        raw_quantity,
        QUANTITY_PRECISION,
    )

    return (
        margin,
        notional,
        quantity,
    )


# ============================================================
# EXPOSURE
# ============================================================

def calculate_worst_case_exposure():
    initial = (
        INITIAL_ENTRY_PERCENT
    )

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
# R18 SAFETY-GATE SIMULATION
# ============================================================

def run_execution_gate_tests():
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
        now
        - LOSS_COOLDOWN_SECONDS
        - 10
    )

    cooldown_clear = (
        now
        - last_loss_time
        >= LOSS_COOLDOWN_SECONDS
    )

    seen_signal_ids = set()

    test_signal_id = (
        "R18-TEST-SIGNAL"
    )

    duplicate_first = (
        test_signal_id
        not in seen_signal_ids
    )

    seen_signal_ids.add(
        test_signal_id
    )

    duplicate_second_rejected = (
        test_signal_id
        in seen_signal_ids
    )

    one_direction_gate = True

    api_symbol_gate = (
        LIVE_SYMBOL == "BTCUSDT"
    )

    return {
        "api_symbol": api_symbol_gate,
        "fresh_signal": fresh_signal_accepted,
        "expired_signal": expired_signal_rejected,
        "cooldown": cooldown_clear,
        "duplicate": (
            duplicate_first
            and duplicate_second_rejected
        ),
        "one_direction": one_direction_gate,
    }


# ============================================================
# DEMO PAYLOAD
# ============================================================

def build_demo_payload(
    quantity,
):
    if DEMO_ORDER_SIDE not in (
        "BUY",
        "SELL",
    ):
        raise RuntimeError(
            "R18_DEMO_SIDE must be BUY or SELL"
        )

    if DEMO_POSITION_SIDE not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "R18_DEMO_POSITION_SIDE must be LONG or SHORT"
        )

    if not DEMO_CLIENT_ORDER_ID:
        raise RuntimeError(
            "R18 demo client order ID is empty"
        )

    if len(
        DEMO_CLIENT_ORDER_ID
    ) > 36:
        raise RuntimeError(
            "R18 demo client order ID exceeds "
            "36 characters"
        )

    return {
        "symbol": DEMO_SYMBOL,
        "side": DEMO_ORDER_SIDE,
        "positionSide": DEMO_POSITION_SIDE,
        "type": DEMO_ORDER_TYPE,
        "quantity": fmt(quantity),
        "newClientOrderId": DEMO_CLIENT_ORDER_ID,
    }


# ============================================================
# ABSOLUTE REAL-ORDER LOCK
# ============================================================

async def transmit_real_order(
    session,
    payload,
):
    # ========================================================
    # DO NOT REMOVE THIS LOCK IN R18.
    #
    # No HTTP request exists inside this function.
    # Therefore R18 cannot transmit a real order through it.
    # ========================================================

    raise RuntimeError(
        "R18 ABSOLUTE REAL-ORDER LOCK: "
        "real POST transmission prohibited"
    )


# ============================================================
# R18 DEMO POST
# ============================================================

async def transmit_demo_order(
    session,
    payload,
):
    global DEMO_POST_ALREADY_ATTEMPTED

    if not DEMO_ORDER_EXECUTION:
        raise RuntimeError(
            "R18 demo execution disabled by configuration"
        )

    if DEMO_POST_ALREADY_ATTEMPTED:
        raise RuntimeError(
            "R18 demo POST already attempted "
            "during this process"
        )

    # Lock before any network activity.
    DEMO_POST_ALREADY_ATTEMPTED = True

    path = (
        "/capi/v3/sim/order"
    )

    # Compact JSON is critical:
    # the body used for the signature must be
    # exactly the body transmitted.
    body_string = json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )

    headers = signed_headers(
        "POST",
        path,
        "",
        body_string,
    )

    url = (
        f"{API_BASE_URL}{path}"
    )

    async with session.post(
        url,
        data=body_string.encode(
            "utf-8"
        ),
        headers=headers,
        timeout=HTTP_TIMEOUT,
    ) as response:

        text = await response.text()

        try:
            data = json.loads(
                text
            )

        except Exception:
            data = {
                "raw": text
            }

        return {
            "http_status": response.status,
            "response": data,
            "raw": text,
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
        print(
            "Telegram credentials not configured"
        )
        return

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=HTTP_TIMEOUT,
        ) as response:

            text = await response.text()

            if response.status != 200:
                print(
                    "Telegram error:",
                    response.status,
                    text,
                )

    except Exception as exc:
        print(
            "Telegram exception:",
            exc,
        )


# ============================================================
# REPORT BUILDERS
# ============================================================

def demo_response_summary(
    result,
):
    response = result.get(
        "response",
        {}
    )

    if not isinstance(
        response,
        dict,
    ):
        return str(response)

    success = response.get(
        "success"
    )

    order_id = response.get(
        "orderId",
        "N/A",
    )

    client_order_id = response.get(
        "clientOrderId",
        DEMO_CLIENT_ORDER_ID,
    )

    error_code = response.get(
        "errorCode",
        "",
    )

    error_message = response.get(
        "errorMessage",
        "",
    )

    lines = [
        f"HTTP Status: "
        f"{result.get('http_status')}",
        f"Success: {success}",
        f"Order ID: {order_id}",
        f"Client Order ID: "
        f"{client_order_id}",
    ]

    if error_code:
        lines.append(
            f"Error Code: {error_code}"
        )

    if error_message:
        lines.append(
            f"Error Message: {error_message}"
        )

    return "\n".join(
        lines
    )


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_r18():
    stage = "startup"

    real_post_called = False
    demo_post_called = False
    demo_result = None

    try:
        print(
            "=" * 60
        )
        print(
            f"{MODULE_NAME} STARTING"
        )
        print(
            "CONTROLLED WEEX DEMO ORDER TRANSMISSION"
        )
        print(
            "REAL ORDER TRANSMISSION ABSOLUTELY LOCKED"
        )
        print(
            "=" * 60
        )

        # ====================================================
        # CREDENTIALS
        # ====================================================

        stage = "configuration"

        validate_weex_credentials()

        async with aiohttp.ClientSession() as session:

            # =================================================
            # BALANCE
            # =================================================

            stage = "balance"

            balance = await get_available_usdt(
                session
            )

            # =================================================
            # MARK PRICE
            # =================================================

            stage = "mark price"

            mark_price = await get_mark_price(
                session
            )

            # =================================================
            # GATES
            # =================================================

            stage = "execution gates"

            gates = run_execution_gate_tests()

            # =================================================
            # POSITION
            # =================================================

            stage = "position check"

            position_open, position_data = (
                await check_live_position(
                    session
                )
            )

            external_position_clear = (
                not position_open
            )

            # =================================================
            # LEVERAGE
            # =================================================

            leverage_gate = (
                LEVERAGE
                >= WEEX_MIN_LEVERAGE
                and LEVERAGE
                <= WEEX_MAX_LEVERAGE
                and LEVERAGE
                <= MAX_LEVERAGE
            )

            # =================================================
            # ENTRY
            # =================================================

            (
                margin,
                notional,
                quantity,
            ) = calculate_entry(
                balance,
                mark_price,
            )

            quantity_positive = (
                quantity > ZERO
            )

            minimum_passed = (
                quantity
                >= MIN_ORDER_QTY
            )

            # =================================================
            # EXPOSURE
            # =================================================

            (
                initial_exposure,
                pyramid_exposure,
                backup_exposure,
                total_exposure,
            ) = calculate_worst_case_exposure()

            exposure_passed = (
                total_exposure
                <= MAX_FUND_EXPOSURE_PERCENT
            )

            tp_allocation_passed = (
                TP1_PERCENT
                + TP2_PERCENT
                + TP3_PERCENT
                == ONE_HUNDRED
            )

            # =================================================
            # FINAL PRE-DEMO GATE
            # =================================================

            all_pre_demo_gates = all(
                [
                    gates["api_symbol"],
                    gates["fresh_signal"],
                    gates["expired_signal"],
                    gates["cooldown"],
                    gates["duplicate"],
                    gates["one_direction"],
                    external_position_clear,
                    leverage_gate,
                    quantity_positive,
                    minimum_passed,
                    exposure_passed,
                    tp_allocation_passed,
                    HARD_REAL_ORDER_LOCK,
                    not LIVE_ORDER_EXECUTION,
                ]
            )

            # =================================================
            # PAYLOAD
            # =================================================

            stage = "demo payload"

            demo_payload = build_demo_payload(
                quantity
            )

            # =================================================
            # OPTIONAL DEMO BALANCE CHECK
            # =================================================

            stage = "demo balance"

            demo_balance_response = (
                await get_demo_balance(
                    session
                )
            )

            # =================================================
            # DEMO TRANSMISSION
            # =================================================

            stage = "demo order transmission"

            if not all_pre_demo_gates:
                raise RuntimeError(
                    "R18 pre-demo safety gate failed; "
                    "demo POST blocked"
                )

            if not DEMO_ORDER_EXECUTION:
                raise RuntimeError(
                    "R18_DEMO_ORDER_EXECUTION is disabled"
                )

            demo_result = (
                await transmit_demo_order(
                    session,
                    demo_payload,
                )
            )

            demo_post_called = True

            http_status = demo_result[
                "http_status"
            ]

            response_data = demo_result[
                "response"
            ]

            demo_success = False

            if isinstance(
                response_data,
                dict,
            ):
                demo_success = (
                    response_data.get(
                        "success"
                    )
                    is True
                )

            # HTTP 200 confirms transmission reached WEEX.
            transmission_reached_weex = (
                http_status == 200
            )

            # =================================================
            # REPORT
            # =================================================

            print(
                "\n"
                + "=" * 60
            )

            if demo_success:
                print(
                    f"✅ MODULE {MODULE_NAME} "
                    "DEMO ORDER ACCEPTED"
                )

            elif transmission_reached_weex:
                print(
                    f"⚠️ MODULE {MODULE_NAME} "
                    "DEMO POST REACHED WEEX"
                )

            else:
                print(
                    f"❌ MODULE {MODULE_NAME} "
                    "DEMO POST FAILED"
                )

            print(
                LIVE_SYMBOL
            )

            print(
                f"Available USDT: "
                f"{fmt(balance)}"
            )

            print(
                f"Mark Price: "
                f"{fmt(mark_price)} USDT"
            )

            print()

            print(
                "FINAL EXECUTION GATE"
            )

            print(
                "API Trading Symbol:",
                yes_no(
                    gates[
                        "api_symbol"
                    ]
                ),
            )

            print(
                "Fresh Signal Accepted:",
                yes_no(
                    gates[
                        "fresh_signal"
                    ]
                ),
            )

            print(
                "Expired Signal Rejected:",
                yes_no(
                    gates[
                        "expired_signal"
                    ]
                ),
            )

            print(
                "Loss Cooldown Test:",
                yes_no(
                    gates[
                        "cooldown"
                    ]
                ),
            )

            print(
                "Duplicate Signal Rejected:",
                yes_no(
                    gates[
                        "duplicate"
                    ]
                ),
            )

            print(
                "One Direction Gate:",
                yes_no(
                    gates[
                        "one_direction"
                    ]
                ),
            )

            print(
                "External Position Clear:",
                yes_no(
                    external_position_clear
                ),
            )

            print()

            print(
                "ADJUSTABLE CONFIG"
            )

            print(
                f"Entry: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%"
            )

            print(
                f"Leverage: "
                f"{fmt(LEVERAGE)}x"
            )

            print(
                f"Max Config Leverage: "
                f"{fmt(MAX_LEVERAGE)}x"
            )

            print(
                f"Margin Type: "
                f"{MARGIN_TYPE}"
            )

            print(
                f"Max Pyramids: "
                f"{MAX_PYRAMID_ADDS}"
            )

            print(
                f"Pyramid Size: "
                f"{fmt(PYRAMID_SIZE_PERCENT)}%"
            )

            print(
                f"Max Backups: "
                f"{MAX_BACKUPS}"
            )

            print(
                f"Backup Size: "
                f"{fmt(BACKUP_SIZE_PERCENT)}% each"
            )

            print(
                f"Backup Buffer: "
                f"{fmt(BACKUP_BUFFER_PERCENT)}%"
            )

            print(
                f"Min Liq Distance: "
                f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%"
            )

            print(
                f"Max Fund Exposure: "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
            )

            print()

            print(
                "WEEX CONTRACT"
            )

            print(
                f"Minimum Order: "
                f"{fmt(MIN_ORDER_QTY)}"
            )

            print(
                f"Quantity Precision: "
                f"{QUANTITY_PRECISION}"
            )

            print(
                f"Contract Value: "
                f"{fmt(CONTRACT_VALUE)}"
            )

            print(
                f"WEEX Min Leverage: "
                f"{fmt(WEEX_MIN_LEVERAGE)}x"
            )

            print(
                f"WEEX Max Leverage: "
                f"{fmt(WEEX_MAX_LEVERAGE)}x"
            )

            print(
                "Leverage Gate:",
                yes_no(
                    leverage_gate
                ),
            )

            print()

            print(
                "DYNAMIC ENTRY"
            )

            print(
                f"Margin: "
                f"{fmt(margin)} USDT"
            )

            print(
                f"Notional: "
                f"{fmt(notional)} USDT"
            )

            print(
                f"Quantity: "
                f"{fmt(quantity)}"
            )

            print(
                "Quantity Positive:",
                yes_no(
                    quantity_positive
                ),
            )

            print(
                "Minimum Passed:",
                yes_no(
                    minimum_passed
                ),
            )

            print()

            print(
                "WORST-CASE EXPOSURE"
            )

            print(
                f"Initial: "
                f"{fmt(initial_exposure)}%"
            )

            print(
                f"Pyramids: "
                f"{fmt(pyramid_exposure)}%"
            )

            print(
                f"Backups: "
                f"{fmt(backup_exposure)}%"
            )

            print(
                f"Total: "
                f"{fmt(total_exposure)}% / "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
            )

            print(
                "Exposure Passed:",
                yes_no(
                    exposure_passed
                ),
            )

            print()

            print(
                "TP / TRAILING"
            )

            print(
                f"TP1 / TP2 / TP3: "
                f"{fmt(TP1_PERCENT)}% / "
                f"{fmt(TP2_PERCENT)}% / "
                f"{fmt(TP3_PERCENT)}%"
            )

            print(
                f"TP1 Trigger: "
                f"{fmt(TP1_TRIGGER_PERCENT)}%"
            )

            print(
                f"TP2 Trigger: "
                f"{fmt(TP2_TRIGGER_PERCENT)}%"
            )

            print(
                f"Trailing Distance: "
                f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
            )

            print()

            print(
                "POSITION CHECK"
            )

            if position_open:
                print(
                    f"Open {LIVE_SYMBOL} "
                    "position detected"
                )
            else:
                print(
                    f"No open {LIVE_SYMBOL} "
                    "position detected"
                )

            print()

            print(
                "R18 DEMO ORDER PAYLOAD"
            )

            print(
                f"Live Symbol: "
                f"{LIVE_SYMBOL}"
            )

            print(
                f"Demo Symbol: "
                f"{DEMO_SYMBOL}"
            )

            print(
                f"Side: "
                f"{DEMO_ORDER_SIDE}"
            )

            print(
                f"Position Side: "
                f"{DEMO_POSITION_SIDE}"
            )

            print(
                f"Type: "
                f"{DEMO_ORDER_TYPE}"
            )

            print(
                f"Quantity: "
                f"{fmt(quantity)}"
            )

            print(
                f"Client Order ID: "
                f"{DEMO_CLIENT_ORDER_ID}"
            )

            print()

            print(
                "ORDER TRANSMISSION"
            )

            print(
                "Real Endpoint: "
                "/capi/v3/order"
            )

            print(
                "Demo Endpoint: "
                "/capi/v3/sim/order"
            )

            print(
                "Real POST Called: "
                "❌ NO"
            )

            print(
                "Demo POST Called: "
                + (
                    "✅ YES"
                    if demo_post_called
                    else "❌ NO"
                )
            )

            print(
                "Demo HTTP Status: "
                f"{http_status}"
            )

            print()

            print(
                "WEEX DEMO RESPONSE"
            )

            print(
                demo_response_summary(
                    demo_result
                )
            )

            print()

            print(
                "🛡 R18 ABSOLUTE "
                "REAL-ORDER POST LOCK ACTIVE"
            )

            print(
                "⚠️ LIVE ORDER EXECUTION DISABLED"
            )

            print(
                "⚠️ NO REAL ORDER WAS SENT"
            )

            if demo_success:
                print(
                    "✅ DEMO ORDER WAS ACCEPTED BY WEEX"
                )

            elif transmission_reached_weex:
                print(
                    "⚠️ DEMO REQUEST REACHED WEEX "
                    "BUT WAS NOT ACCEPTED"
                )

            else:
                print(
                    "❌ DEMO REQUEST DID NOT "
                    "COMPLETE SUCCESSFULLY"
                )

            print(
                "=" * 60
            )

            # =================================================
            # TELEGRAM REPORT
            # =================================================

            status_icon = (
                "✅"
                if demo_success
                else "⚠️"
            )

            telegram_message = (
                f"{status_icon} MODULE "
                f"{MODULE_NAME}\n"
                f"{LIVE_SYMBOL}\n\n"

                f"Available USDT: "
                f"{fmt(balance)}\n"

                f"Mark Price: "
                f"{fmt(mark_price)} USDT\n\n"

                f"R18 DEMO TRANSMISSION\n"

                f"Live Symbol: "
                f"{LIVE_SYMBOL}\n"

                f"Demo Symbol: "
                f"{DEMO_SYMBOL}\n"

                f"Side: "
                f"{DEMO_ORDER_SIDE}\n"

                f"Position Side: "
                f"{DEMO_POSITION_SIDE}\n"

                f"Type: "
                f"{DEMO_ORDER_TYPE}\n"

                f"Quantity: "
                f"{fmt(quantity)}\n"

                f"Client Order ID: "
                f"{DEMO_CLIENT_ORDER_ID}\n\n"

                f"Real POST Called: "
                f"❌ NO\n"

                f"Demo POST Called: "
                f"{'✅ YES' if demo_post_called else '❌ NO'}\n"

                f"Demo HTTP Status: "
                f"{http_status}\n\n"

                f"{demo_response_summary(demo_result)}\n\n"

                f"🛡 R18 absolute real-order "
                f"POST lock active\n"

                f"⚠️ LIVE ORDER EXECUTION DISABLED\n"

                f"⚠️ NO REAL ORDER WAS SENT"
            )

            await send_telegram(
                session,
                telegram_message,
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
            LIVE_SYMBOL
        )

        print(
            f"Stage: {stage}"
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            "🛡 R18 absolute "
            "real-order POST lock active"
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

        try:
            async with aiohttp.ClientSession() as session:

                message = (
                    f"❌ MODULE "
                    f"{MODULE_NAME} ERROR\n"
                    f"{LIVE_SYMBOL}\n\n"

                    f"Stage: "
                    f"{stage}\n"

                    f"{type(exc).__name__}: "
                    f"{exc}\n\n"

                    f"Real POST Called: "
                    f"❌ NO\n"

                    f"Demo POST Attempted: "
                    f"{'✅ YES' if DEMO_POST_ALREADY_ATTEMPTED else '❌ NO'}\n\n"

                    f"🛡 R18 absolute real-order "
                    f"POST lock active\n"

                    f"⚠️ LIVE ORDER EXECUTION DISABLED\n"

                    f"⚠️ NO REAL ORDER WAS SENT"
                )

                await send_telegram(
                    session,
                    message,
                )

        except Exception as telegram_exc:
            print(
                "Telegram error report failed:",
                telegram_exc,
            )


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.Response(
        text=(
            f"{MODULE_NAME} ACTIVE\n"
            f"REAL ORDERS: LOCKED\n"
            f"DEMO ORDERS: "
            f"{'ENABLED' if DEMO_ORDER_EXECUTION else 'DISABLED'}"
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
        f"HEALTH SERVER ACTIVE ON PORT "
        f"{port}"
    )

    return runner


# ============================================================
# APPLICATION
# ============================================================

async def main():
    runner = await start_health_server()

    try:
        # R18 diagnostic/demo transmission executes ONCE
        # for this running process.
        await run_r18()

        # Keep Render web service alive without repeating
        # the demo order.
        while True:
            await asyncio.sleep(
                3600
            )

    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(
        main())
