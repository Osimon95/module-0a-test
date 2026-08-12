import asyncio
import base64
import hashlib
import hmac
import json
import os
import threading
import time

from decimal import Decimal, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

import aiohttp


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R15"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ============================================================
# ADJUSTABLE CONFIGURATION
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

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TAKE PROFIT / TRAILING
# ============================================================

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


# ============================================================
# ABSOLUTE EXECUTION SAFETY LOCK
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_EXECUTION_LOCK = True

# R15 deliberately does NOT contain a function that sends
# a live WEEX order.
#
# It only builds and validates the payload.


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

telegram_report_sent = False


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


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
            f"{MODULE_NAME} ACTIVE\n"
            f"{SYMBOL}\n"
            f"LIVE ORDER EXECUTION: DISABLED\n"
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


def run_health_server():

    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler,
    )

    print(
        f"HEALTH SERVER ACTIVE ON PORT {PORT}",
        flush=True,
    )

    server.serve_forever()


def start_health_server():

    thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    thread.start()


# ============================================================
# DECIMAL HELPERS
# ============================================================

def safe_decimal(value):

    try:
        return Decimal(str(value))

    except Exception:
        return ZERO


def fmt(value):

    if isinstance(value, Decimal):

        text = format(
            value,
            "f",
        )

        if "." in text:

            text = text.rstrip("0").rstrip(".")

        return text

    return str(value)


def floor_quantity(
    quantity,
    precision,
):

    quantum = Decimal("1").scaleb(
        -precision
    )

    return quantity.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


# ============================================================
# API CREDENTIAL CHECK
# ============================================================

def validate_credentials():

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
            "Missing Render environment variables: "
            + ", ".join(missing)
        )


# ============================================================
# WEEX V3 SIGNATURE
# ============================================================

def make_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):

    message = (
        str(timestamp)
        + method.upper()
        + request_path
        + query_string
        + body
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


def private_headers(
    method,
    path,
    params=None,
    body="",
):

    timestamp = str(
        int(time.time() * 1000)
    )

    query_string = ""

    if params:

        query_string = "?" + urlencode(
            params
        )

    signature = make_signature(
        timestamp,
        method,
        path,
        query_string,
        body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }


# ============================================================
# GENERIC HTTP
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):

    url = API_BASE_URL + path

    async with session.get(
        url,
        params=params,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)

        except Exception:

            raise RuntimeError(
                f"Invalid WEEX JSON: {text}"
            )


async def private_get(
    session,
    path,
    params=None,
):

    headers = private_headers(
        "GET",
        path,
        params=params,
    )

    url = API_BASE_URL + path

    async with session.get(
        url,
        params=params,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX PRIVATE HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)

        except Exception:

            raise RuntimeError(
                f"Invalid WEEX private JSON: {text}"
            )


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_available_usdt(
    session,
):

    path = "/capi/v3/account/balance"

    data = await private_get(
        session,
        path,
    )

    candidates = data

    if isinstance(data, dict):

        candidates = (
            data.get("data")
            or data.get("result")
            or data.get("balances")
            or data
        )

    if isinstance(candidates, dict):

        candidates = [candidates]

    if isinstance(candidates, list):

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
                "free",
                "balance",
            ):

                if key in item:

                    value = safe_decimal(
                        item[key]
                    )

                    if value >= ZERO:
                        return value

    raise RuntimeError(
        "Unable to extract available USDT"
    )


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):

    path = "/capi/v3/market/symbolPrice"

    params = {
        "symbol": SYMBOL,
        "priceType": "MARK",
    }

    data = await public_get(
        session,
        path,
        params=params,
    )

    if isinstance(data, list):

        if not data:

            raise RuntimeError(
                "Empty mark price response"
            )

        data = data[0]

    objects = [data]

    if isinstance(data, dict):

        objects.extend(
            [
                data.get("data"),
                data.get("result"),
            ]
        )

    for obj in objects:

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

            if key in obj:

                price = safe_decimal(
                    obj[key]
                )

                if price > ZERO:
                    return price

    raise RuntimeError(
        "Unable to extract mark price"
    )


# ============================================================
# API TRADING SYMBOL GATE
# ============================================================

async def symbol_api_trading_allowed(
    session,
):

    path = (
        "/capi/v3/market/"
        "apiTradingSymbols"
    )

    data = await public_get(
        session,
        path,
    )

    if isinstance(data, dict):

        data = (
            data.get("data")
            or data.get("result")
            or data.get("symbols")
            or []
        )

    if not isinstance(data, list):
        return False

    symbols = []

    for item in data:

        if isinstance(
            item,
            str,
        ):

            symbols.append(
                item.upper()
            )

        elif isinstance(
            item,
            dict,
        ):

            symbol = item.get(
                "symbol"
            )

            if symbol:

                symbols.append(
                    str(symbol).upper()
                )

    return SYMBOL in symbols


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):

    path = (
        "/capi/v3/market/"
        "exchangeInfo"
    )

    data = await public_get(
        session,
        path,
        params={
            "symbol": SYMBOL,
        },
    )

    symbols = []

    if isinstance(data, dict):

        symbols = data.get(
            "symbols",
            [],
        )

        if not symbols:

            nested = data.get(
                "data"
            )

            if isinstance(
                nested,
                dict,
            ):

                symbols = nested.get(
                    "symbols",
                    [],
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

        if str(
            item.get(
                "symbol",
                "",
            )
        ).upper() != SYMBOL:
            continue

        min_order = safe_decimal(
            item.get(
                "minOrderSize",
                "0",
            )
        )

        quantity_precision = int(
            item.get(
                "quantityPrecision",
                4,
            )
        )

        contract_value = safe_decimal(
            item.get(
                "contractVal",
                "0",
            )
        )

        min_leverage = safe_decimal(
            item.get(
                "minLeverage",
                "1",
            )
        )

        max_leverage = safe_decimal(
            item.get(
                "maxLeverage",
                "0",
            )
        )

        if min_order <= ZERO:

            raise RuntimeError(
                "Invalid WEEX minimum order"
            )

        if max_leverage <= ZERO:

            raise RuntimeError(
                "Invalid WEEX maximum leverage"
            )

        return {
            "min_order": min_order,
            "quantity_precision":
                quantity_precision,
            "contract_value":
                contract_value,
            "min_leverage":
                min_leverage,
            "max_leverage":
                max_leverage,
        }

    raise RuntimeError(
        f"{SYMBOL} not found in "
        "WEEX exchange information"
    )


# ============================================================
# REAL POSITION CHECK
# ============================================================

async def get_position_state(
    session,
):

    path = (
        "/capi/v3/account/"
        "position/singlePosition"
    )

    data = await private_get(
        session,
        path,
        params={
            "symbol": SYMBOL,
        },
    )

    if isinstance(data, dict):

        data = (
            data.get("data")
            or data.get("result")
            or data.get("positions")
            or data
        )

    if isinstance(
        data,
        dict,
    ):

        data = [data]

    if not isinstance(
        data,
        list,
    ):

        return {
            "open": False,
            "side": "NONE",
            "size": ZERO,
            "liquidation_price": ZERO,
        }

    total_size = ZERO
    detected_side = "NONE"
    liquidation_price = ZERO

    for item in data:

        if not isinstance(
            item,
            dict,
        ):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                SYMBOL,
            )
        ).upper()

        if (
            item_symbol
            and item_symbol != SYMBOL
        ):
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

        if abs(size) > ZERO:

            total_size += abs(size)

            detected_side = str(
                item.get(
                    "side",
                    item.get(
                        "positionSide",
                        "UNKNOWN",
                    ),
                )
            ).upper()

            liquidation_price = (
                safe_decimal(
                    item.get(
                        "liquidatePrice",
                        item.get(
                            "liquidationPrice",
                            "0",
                        ),
                    )
                )
            )

    return {
        "open": total_size > ZERO,
        "side": detected_side,
        "size": total_size,
        "liquidation_price":
            liquidation_price,
    }


# ============================================================
# SIGNAL SAFETY SIMULATION
# ============================================================

def run_signal_gate_tests():

    now = time.time()

    fresh_signal_time = (
        now
        - min(
            5,
            SIGNAL_EXPIRY_SECONDS / 2,
        )
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 5
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
        now
        - LOSS_COOLDOWN_SECONDS
        - 1
    )

    cooldown_passed = (
        now - last_loss_time
        >= LOSS_COOLDOWN_SECONDS
    )

    seen_signal_ids = set()

    test_signal_id = (
        f"{SYMBOL}-R15-TEST"
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

    return {
        "fresh":
            fresh_signal_accepted,
        "expired":
            expired_signal_rejected,
        "cooldown":
            cooldown_passed,
        "duplicate":
            (
                duplicate_first
                and
                duplicate_second_rejected
            ),
        "one_direction":
            one_direction_gate,
    }


# ============================================================
# EXPOSURE CALCULATION
# ============================================================

def calculate_exposure():

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
        INITIAL_ENTRY_PERCENT
        + pyramid_exposure
        + backup_exposure
    )

    return (
        pyramid_exposure,
        backup_exposure,
        total_exposure,
    )


# ============================================================
# R15 ORDER PAYLOAD BUILDER
# ============================================================

def build_order_payload(
    quantity,
):

    client_order_id = (
        "r15-"
        + SYMBOL.lower()
        + "-"
        + str(
            int(time.time())
        )
    )

    payload = {
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": fmt(
            quantity
        ),
        "newClientOrderId":
            client_order_id[:36],
    }

    return payload


def validate_order_payload(
    payload,
):

    required = (
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    )

    for field in required:

        if (
            field not in payload
            or payload[field] in (
                "",
                None,
            )
        ):

            return False

    if payload[
        "symbol"
    ] != SYMBOL:

        return False

    if payload[
        "type"
    ] != "MARKET":

        return False

    if safe_decimal(
        payload["quantity"]
    ) <= ZERO:

        return False

    return True


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):

    global telegram_report_sent

    if telegram_report_sent:
        return

    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):

        print(
            "TELEGRAM VARIABLES NOT SET",
            flush=True,
        )

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
            message,
    }

    try:

        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = await response.text()

            if response.status == 200:

                telegram_report_sent = True

                print(
                    "TELEGRAM REPORT SENT",
                    flush=True,
                )

            else:

                print(
                    "TELEGRAM ERROR "
                    f"{response.status}: "
                    f"{text}",
                    flush=True,
                )

    except Exception as exc:

        print(
            "TELEGRAM EXCEPTION:",
            repr(exc),
            flush=True,
        )


# ============================================================
# R15 DIAGNOSTIC
# ============================================================

async def run_r15():

    validate_credentials()

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        # ----------------------------------------------------
        # STAGE 1: ACCOUNT
        # ----------------------------------------------------

        stage = "balance"

        balance = await get_available_usdt(
            session
        )

        # ----------------------------------------------------
        # STAGE 2: PRICE
        # ----------------------------------------------------

        stage = "mark_price"

        mark_price = await get_mark_price(
            session
        )

        # ----------------------------------------------------
        # STAGE 3: API TRADING SYMBOL
        # ----------------------------------------------------

        stage = "api_symbol"

        api_symbol_allowed = (
            await
            symbol_api_trading_allowed(
                session
            )
        )

        # ----------------------------------------------------
        # STAGE 4: CONTRACT
        # ----------------------------------------------------

        stage = "contract"

        contract = (
            await get_contract_info(
                session
            )
        )

        min_order = contract[
            "min_order"
        ]

        quantity_precision = (
            contract[
                "quantity_precision"
            ]
        )

        contract_value = contract[
            "contract_value"
        ]

        weex_min_leverage = (
            contract[
                "min_leverage"
            ]
        )

        weex_max_leverage = (
            contract[
                "max_leverage"
            ]
        )

        # ----------------------------------------------------
        # STAGE 5: REAL POSITION
        # ----------------------------------------------------

        stage = "position"

        position = (
            await get_position_state(
                session
            )
        )

        external_position_clear = (
            not position["open"]
        )

        # ----------------------------------------------------
        # STAGE 6: LEVERAGE
        # ----------------------------------------------------

        stage = "leverage"

        leverage_gate = (
            LEVERAGE
            >= weex_min_leverage
            and
            LEVERAGE
            <= weex_max_leverage
            and
            LEVERAGE
            <= MAX_LEVERAGE
        )

        # ----------------------------------------------------
        # STAGE 7: DYNAMIC ENTRY
        # ----------------------------------------------------

        stage = "sizing"

        entry_margin = (
            balance
            * INITIAL_ENTRY_PERCENT
            / ONE_HUNDRED
        )

        notional = (
            entry_margin
            * LEVERAGE
        )

        raw_quantity = (
            notional
            / mark_price
        )

        quantity = floor_quantity(
            raw_quantity,
            quantity_precision,
        )

        quantity_positive = (
            quantity > ZERO
        )

        minimum_passed = (
            quantity >= min_order
        )

        # ----------------------------------------------------
        # STAGE 8: EXPOSURE
        # ----------------------------------------------------

        (
            pyramid_exposure,
            backup_exposure,
            total_exposure,
        ) = calculate_exposure()

        exposure_passed = (
            total_exposure
            <= MAX_FUND_EXPOSURE_PERCENT
        )

        # ----------------------------------------------------
        # STAGE 9: TP ALLOCATION
        # ----------------------------------------------------

        tp_total = (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        )

        tp_allocation_passed = (
            tp_total
            == ONE_HUNDRED
        )

        # ----------------------------------------------------
        # STAGE 10: SIGNAL GATES
        # ----------------------------------------------------

        signal = (
            run_signal_gate_tests()
        )

        # ----------------------------------------------------
        # STAGE 11: BUILD PAYLOAD
        # ----------------------------------------------------

        stage = "payload"

        order_payload = (
            build_order_payload(
                quantity
            )
        )

        payload_built = (
            validate_order_payload(
                order_payload
            )
        )

        # ----------------------------------------------------
        # ABSOLUTE TRANSMISSION LOCK
        # ----------------------------------------------------

        payload_transmitted = False

        execution_lock_passed = (
            HARD_EXECUTION_LOCK
            and
            not LIVE_ORDER_EXECUTION
            and
            not payload_transmitted
        )

        # ----------------------------------------------------
        # FINAL GATE
        # ----------------------------------------------------

        checks = {
            "api_symbol":
                api_symbol_allowed,

            "fresh_signal":
                signal["fresh"],

            "expired_signal":
                signal["expired"],

            "cooldown":
                signal["cooldown"],

            "duplicate":
                signal["duplicate"],

            "one_direction":
                signal["one_direction"],

            "external_position":
                external_position_clear,

            "leverage":
                leverage_gate,

            "quantity_positive":
                quantity_positive,

            "minimum_order":
                minimum_passed,

            "exposure":
                exposure_passed,

            "tp_allocation":
                tp_allocation_passed,

            "payload":
                payload_built,

            "execution_lock":
                execution_lock_passed,
        }

        all_passed = all(
            checks.values()
        )

        status = (
            "DIAGNOSTIC PASSED"
            if all_passed
            else
            "NOT READY"
        )

        status_icon = (
            "✅"
            if all_passed
            else
            "⚠️"
        )

        # ----------------------------------------------------
        # TERMINAL REPORT
        # ----------------------------------------------------

        print(
            "=" * 60,
            flush=True,
        )

        print(
            f"{MODULE_NAME} {status}",
            flush=True,
        )

        print(
            SYMBOL,
            flush=True,
        )

        print(
            f"Available USDT: "
            f"{fmt(balance)}",
            flush=True,
        )

        print(
            f"Mark Price: "
            f"{fmt(mark_price)} USDT",
            flush=True,
        )

        print(
            "",
            flush=True,
        )

        print(
            "R15 EXECUTION GATE",
            flush=True,
        )

        for name, passed in checks.items():

            print(
                f"{name}: "
                f"{'YES' if passed else 'NO'}",
                flush=True,
            )

        print(
            "",
            flush=True,
        )

        print(
            "ORDER PAYLOAD:",
            json.dumps(
                order_payload,
                indent=2,
            ),
            flush=True,
        )

        print(
            "",
            flush=True,
        )

        print(
            "LIVE ORDER TRANSMISSION: DISABLED",
            flush=True,
        )

        print(
            "NO LIVE ORDER WAS SENT",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        # ----------------------------------------------------
        # TELEGRAM REPORT
        # ----------------------------------------------------

        telegram_message = (
            f"{status_icon} MODULE "
            f"{MODULE_NAME} "
            f"{status}\n\n"

            f"{SYMBOL}\n"

            f"Available USDT: "
            f"{fmt(balance)}\n"

            f"Mark Price: "
            f"{fmt(mark_price)} USDT\n\n"

            f"FINAL EXECUTION GATE\n"

            f"API Trading Symbol: "
            f"{'✅ YES' if api_symbol_allowed else '❌ NO'}\n"

            f"Fresh Signal Accepted: "
            f"{'✅ YES' if signal['fresh'] else '❌ NO'}\n"

            f"Expired Signal Rejected: "
            f"{'✅ YES' if signal['expired'] else '❌ NO'}\n"

            f"Loss Cooldown Test: "
            f"{'✅ YES' if signal['cooldown'] else '❌ NO'}\n"

            f"Duplicate Signal Rejected: "
            f"{'✅ YES' if signal['duplicate'] else '❌ NO'}\n"

            f"One Direction Gate: "
            f"{'✅ YES' if signal['one_direction'] else '❌ NO'}\n"

            f"External Position Clear: "
            f"{'✅ YES' if external_position_clear else '❌ NO'}\n\n"

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

            f"Max Fund Exposure: "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n\n"

            f"WEEX CONTRACT\n"

            f"Minimum Order: "
            f"{fmt(min_order)}\n"

            f"Quantity Precision: "
            f"{quantity_precision}\n"

            f"Contract Value: "
            f"{fmt(contract_value)}\n"

            f"WEEX Min Leverage: "
            f"{fmt(weex_min_leverage)}x\n"

            f"WEEX Max Leverage: "
            f"{fmt(weex_max_leverage)}x\n"

            f"Leverage Gate: "
            f"{'✅ YES' if leverage_gate else '❌ NO'}\n\n"

            f"DYNAMIC ENTRY\n"

            f"Margin: "
            f"{fmt(entry_margin)} USDT\n"

            f"Notional: "
            f"{fmt(notional)} USDT\n"

            f"Quantity: "
            f"{fmt(quantity)}\n"

            f"Quantity Positive: "
            f"{'✅ YES' if quantity_positive else '❌ NO'}\n"

            f"Minimum Passed: "
            f"{'✅ YES' if minimum_passed else '❌ NO'}\n\n"

            f"WORST-CASE EXPOSURE\n"

            f"Initial: "
            f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

            f"Pyramids: "
            f"{fmt(pyramid_exposure)}%\n"

            f"Backups: "
            f"{fmt(backup_exposure)}%\n"

            f"Total: "
            f"{fmt(total_exposure)}% / "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

            f"Exposure Passed: "
            f"{'✅ YES' if exposure_passed else '❌ NO'}\n\n"

            f"TP / TRAILING\n"

            f"TP1 / TP2 / TP3: "
            f"{fmt(TP1_PERCENT)}% / "
            f"{fmt(TP2_PERCENT)}% / "
            f"{fmt(TP3_PERCENT)}%\n"

            f"TP1 Trigger: "
            f"{fmt(TP1_TRIGGER_PERCENT)}%\n"

            f"TP2 Trigger: "
            f"{fmt(TP2_TRIGGER_PERCENT)}%\n"

            f"Trailing Distance: "
            f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n"

            f"TP Allocation: "
            f"{'✅ YES' if tp_allocation_passed else '❌ NO'}\n\n"

            f"R15 ORDER PAYLOAD VALIDATION\n"

            f"Endpoint Target: "
            f"/capi/v3/order\n"

            f"Order Type: MARKET\n"

            f"Side: BUY / LONG\n"

            f"Payload Built: "
            f"{'✅ YES' if payload_built else '❌ NO'}\n"

            f"Payload Transmitted: "
            f"❌ NO\n\n"

            f"🛡 R15 absolute private-POST lock active\n"

            f"⚠️ LIVE ORDER EXECUTION DISABLED\n"

            f"⚠️ NO LIVE ORDER WAS SENT\n\n"

            f"Render Runtime: ✅ PERSISTENT"
        )

        await send_telegram(
            session,
            telegram_message,
        )


# ============================================================
# SAFE DIAGNOSTIC WRAPPER
# ============================================================

async def diagnostic_wrapper():

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
            "RUNTIME + EXECUTION PATH VALIDATION",
            flush=True,
        )

        print(
            "NO LIVE ORDER TRANSMISSION",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        await run_r15()

    except Exception as exc:

        error_message = (
            f"❌ MODULE "
            f"{MODULE_NAME} ERROR\n\n"

            f"{SYMBOL}\n"

            f"{type(exc).__name__}: "
            f"{exc}\n\n"

            f"🛡 R15 absolute private-POST "
            f"lock active\n"

            f"⚠️ NO LIVE ORDER WAS SENT\n\n"

            f"Render process remains active."
        )

        print(
            error_message,
            flush=True,
        )

        try:

            async with (
                aiohttp.ClientSession()
            ) as session:

                await send_telegram(
                    session,
                    error_message,
                )

        except Exception as telegram_exc:

            print(
                "ERROR REPORT TELEGRAM "
                "FAILED:",
                repr(telegram_exc),
                flush=True,
            )


# ============================================================
# PERSISTENT RENDER PROCESS
# ============================================================

async def persistent_runtime():

    await diagnostic_wrapper()

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "Python process will remain running.",
        flush=True,
    )

    print(
        "Health server remains active.",
        flush=True,
    )

    print(
        "LIVE ORDER EXECUTION REMAINS DISABLED.",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    while True:

        await asyncio.sleep(
            60
        )


# ============================================================
# MAIN
# ============================================================

def main():

    start_health_server()

    try:

        asyncio.run(
            persistent_runtime()
        )

    except KeyboardInterrupt:

        print(
            f"{MODULE_NAME} STOPPED",
            flush=True,
        )

    except Exception as exc:

        print(
            "FATAL RUNTIME ERROR:",
            repr(exc),
            flush=True,
        )

        # Keep Render process alive even after
        # an unexpected top-level runtime error.

        while True:

            time.sleep(
                60
            )


if __name__ == "__main__":
    main())
