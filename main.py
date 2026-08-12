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

MODULE_NAME = "0F-4H-R17"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ============================================================
# WEEX CREDENTIALS
#
# IMPORTANT:
# THESE NAMES MUST MATCH RENDER EXACTLY.
#
# WEEX_API_KEY
# WEEX_API_SECRET
# WEEX_API_PASSPHRASE
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
# ADJUSTABLE STRATEGY CONFIG
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


# ============================================================
# PYRAMID SETTINGS
# ============================================================

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


# ============================================================
# BACKUP SETTINGS
# ============================================================

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


# ============================================================
# EXPOSURE SETTINGS
# ============================================================

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TAKE PROFIT SETTINGS
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
# SIGNAL SAFETY SETTINGS
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
# ABSOLUTE EXECUTION SAFETY
# ============================================================

LIVE_ORDER_EXECUTION = False

ABSOLUTE_REAL_ORDER_POST_LOCK = True

ABSOLUTE_DEMO_ORDER_POST_LOCK = True

REAL_ORDER_PATH = "/capi/v3/order"

DEMO_ORDER_PATH = "/capi/v3/sim/order"

ZERO = Decimal("0")


# ============================================================
# BASIC HELPERS
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


def yes_no(
    value,
):
    if value:
        return "✅ YES"

    return "❌ NO"


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_weex_credentials():
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


def validate_configuration():
    validate_weex_credentials()

    if INITIAL_ENTRY_PERCENT <= ZERO:
        raise RuntimeError(
            "INITIAL_ENTRY_PERCENT "
            "must be greater than 0"
        )

    if LEVERAGE <= ZERO:
        raise RuntimeError(
            "LEVERAGE must be greater than 0"
        )

    if MAX_LEVERAGE <= ZERO:
        raise RuntimeError(
            "MAX_LEVERAGE must be greater than 0"
        )

    if LEVERAGE > MAX_LEVERAGE:
        raise RuntimeError(
            "LEVERAGE exceeds "
            "MAX_LEVERAGE"
        )

    if MARGIN_TYPE not in {
        "ISOLATED",
        "CROSSED",
    }:
        raise RuntimeError(
            "MARGIN_TYPE must be "
            "ISOLATED or CROSSED"
        )

    if MAX_PYRAMID_ADDS < 0:
        raise RuntimeError(
            "MAX_PYRAMID_ADDS "
            "cannot be negative"
        )

    if MAX_BACKUPS < 0:
        raise RuntimeError(
            "MAX_BACKUPS "
            "cannot be negative"
        )

    if MAX_FUND_EXPOSURE_PERCENT <= ZERO:
        raise RuntimeError(
            "MAX_FUND_EXPOSURE_PERCENT "
            "must be greater than 0"
        )

    tp_total = (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
    )

    if tp_total != Decimal(
        "100"
    ):
        raise RuntimeError(
            "TP allocation must "
            "total 100%, got "
            f"{fmt(tp_total)}%"
        )

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

    worst_case_exposure = (
        INITIAL_ENTRY_PERCENT
        + pyramid_exposure
        + backup_exposure
    )

    if (
        worst_case_exposure
        > MAX_FUND_EXPOSURE_PERCENT
    ):
        raise RuntimeError(
            "Configured worst-case "
            "exposure exceeds "
            "MAX_FUND_EXPOSURE_PERCENT"
        )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    message = (
        str(
            timestamp
        )
        + method.upper()
        + request_path
        + query_string
        + body
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

    signature = base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )

    return signature


# ============================================================
# PRIVATE AUTH HEADERS
# ============================================================

def private_headers(
    method,
    request_path,
    query_string="",
    body="",
):
    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = build_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "Content-Type":
            "application/json",

        "locale":
            "en-US",
    }


# ============================================================
# HTTP RESPONSE HANDLER
# ============================================================

async def read_json_response(
    response,
    label,
):
    text = await response.text()

    if response.status != 200:
        raise RuntimeError(
            f"{label} HTTP "
            f"{response.status}: "
            f"{text}"
        )

    try:
        return json.loads(
            text
        )

    except json.JSONDecodeError:
        raise RuntimeError(
            f"{label} returned "
            f"invalid JSON: {text}"
        )


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    params = params or {}

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
    ) as response:

        return await read_json_response(
            response,
            "WEEX PUBLIC",
        )


# ============================================================
# PRIVATE GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):
    params = params or {}

    query_string = ""

    if params:
        query_string = (
            "?"
            + urlencode(
                params
            )
        )

    headers = private_headers(
        method="GET",
        request_path=path,
        query_string=query_string,
    )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
        f"{query_string}"
    )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        return await read_json_response(
            response,
            "WEEX PRIVATE",
        )


# ============================================================
# ABSOLUTE WEEX POST LOCK
# ============================================================

async def weex_post(
    session,
    path,
    payload,
):
    raise RuntimeError(
        "R17 ABSOLUTE WEEX POST LOCK: "
        f"POST blocked for {path}. "
        "No WEEX order transmission "
        "is permitted."
    )


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_balance(
    session,
):
    path = (
        "/capi/v3/account/balance"
    )

    data = await private_get(
        session,
        path,
    )

    if isinstance(
        data,
        list,
    ):
        items = data

    else:
        items = [
            data
        ]

    for item in items:
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

        if asset != "USDT":
            continue

        available = safe_decimal(
            item.get(
                "availableBalance",
                item.get(
                    "balance",
                    "0",
                ),
            )
        )

        if available >= ZERO:
            return available

    raise RuntimeError(
        "Unable to extract "
        "available USDT balance"
    )


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):
    path = (
        "/capi/v3/market/"
        "symbolPrice"
    )

    params = {
        "symbol": SYMBOL,
        "priceType": "MARK",
    }

    data = await public_get(
        session,
        path,
        params,
    )

    if isinstance(
        data,
        list,
    ):
        if not data:
            raise RuntimeError(
                "Empty WEEX "
                "symbol price response"
            )

        data = data[0]

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Unexpected WEEX "
            "symbol price response"
        )

    price = safe_decimal(
        data.get(
            "price",
            "0",
        )
    )

    if price <= ZERO:
        raise RuntimeError(
            "Invalid WEEX "
            f"mark price: {price}"
        )

    return price


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

    params = {
        "symbol": SYMBOL,
    }

    data = await public_get(
        session,
        path,
        params,
    )

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Unexpected WEEX "
            "exchange information "
            "response"
        )

    symbols = data.get(
        "symbols",
        [],
    )

    for item in symbols:
        if not isinstance(
            item,
            dict,
        ):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if item_symbol == SYMBOL:
            return item

    raise RuntimeError(
        "Unable to locate "
        f"contract info for {SYMBOL}"
    )


# ============================================================
# API TRADING SYMBOLS
# ============================================================

async def get_api_trading_symbols(
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

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected API "
            "trading symbols response"
        )

    symbols = set()

    for item in data:
        symbols.add(
            str(
                item
            ).upper()
        )

    return symbols


# ============================================================
# POSITIONS
# ============================================================

async def get_positions(
    session,
):
    path = (
        "/capi/v3/account/"
        "position/allPosition"
    )

    data = await private_get(
        session,
        path,
    )

    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):
        possible_keys = (
            "data",
            "result",
            "positions",
        )

        for key in possible_keys:
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    raise RuntimeError(
        "Unexpected WEEX "
        "positions response"
    )


# ============================================================
# CONTRACT SETTINGS
# ============================================================

def extract_contract_settings(
    contract,
):
    quantity_precision = int(
        contract.get(
            "quantityPrecision",
            4,
        )
    )

    min_order_size = safe_decimal(
        contract.get(
            "minOrderSize",
            "0.0001",
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

    if min_order_size <= ZERO:
        raise RuntimeError(
            "Invalid WEEX "
            "minimum order size"
        )

    if weex_max_leverage <= ZERO:
        raise RuntimeError(
            "Invalid WEEX "
            "maximum leverage"
        )

    return {
        "quantity_precision":
            quantity_precision,

        "min_order_size":
            min_order_size,

        "contract_value":
            contract_value,

        "weex_min_leverage":
            weex_min_leverage,

        "weex_max_leverage":
            weex_max_leverage,
    }


# ============================================================
# ACTIVE POSITION FILTER
# ============================================================

def active_symbol_positions(
    positions,
):
    active = []

    for item in positions:
        if not isinstance(
            item,
            dict,
        ):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        size = safe_decimal(
            item.get(
                "size",
                "0",
            )
        )

        if (
            item_symbol == SYMBOL
            and size > ZERO
        ):
            active.append(
                item
            )

    return active


# ============================================================
# DYNAMIC ENTRY SIZE
# ============================================================

def calculate_entry(
    balance,
    mark_price,
    quantity_precision,
):
    entry_margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / Decimal(
            "100"
        )
    )

    entry_notional = (
        entry_margin
        * LEVERAGE
    )

    raw_quantity = (
        entry_notional
        / mark_price
    )

    quantity = floor_decimal(
        raw_quantity,
        quantity_precision,
    )

    return {
        "margin":
            entry_margin,

        "notional":
            entry_notional,

        "quantity":
            quantity,
    }


# ============================================================
# SIGNAL GATE TESTS
# ============================================================

def run_signal_gate_tests():
    now = int(
        time.time()
    )

    fresh_signal_time = (
        now - 5
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 1
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
        "R17_TEST_SIGNAL"
    }

    duplicate_signal_rejected = (
        "R17_TEST_SIGNAL"
        in seen_signal_ids
    )

    one_direction_gate = True

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
    }


# ============================================================
# ORDER PAYLOAD SIMULATION
#
# IMPORTANT:
# THIS CREATES A DICTIONARY ONLY.
# IT DOES NOT TRANSMIT ANYTHING.
# ============================================================

def create_simulated_order_payload(
    quantity,
):
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
            (
                "R17-"
                + str(
                    int(
                        time.time()
                    )
                )
            ),
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
            "TELEGRAM SKIPPED: "
            "credentials missing"
        )

        return

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        "sendMessage"
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

            if response.status != 200:
                print(
                    "TELEGRAM ERROR "
                    f"HTTP {response.status}: "
                    f"{text}"
                )

    except Exception as exc:
        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )


# ============================================================
# SUCCESS REPORT
# ============================================================

def build_success_report(
    balance,
    mark_price,
    contract_settings,
    api_symbol_ok,
    entry,
    gates,
    active_positions,
    simulated_payload,
):
    quantity_precision = (
        contract_settings[
            "quantity_precision"
        ]
    )

    min_order = (
        contract_settings[
            "min_order_size"
        ]
    )

    contract_value = (
        contract_settings[
            "contract_value"
        ]
    )

    weex_min_leverage = (
        contract_settings[
            "weex_min_leverage"
        ]
    )

    weex_max_leverage = (
        contract_settings[
            "weex_max_leverage"
        ]
    )

    leverage_gate = (
        LEVERAGE
        >= weex_min_leverage
        and LEVERAGE
        <= weex_max_leverage
        and LEVERAGE
        <= MAX_LEVERAGE
    )

    quantity_positive = (
        entry[
            "quantity"
        ]
        > ZERO
    )

    minimum_passed = (
        entry[
            "quantity"
        ]
        >= min_order
    )

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

    exposure_passed = (
        total_exposure
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    external_position_clear = (
        len(
            active_positions
        )
        == 0
    )

    all_passed = all(
        [
            api_symbol_ok,
            gates[
                "fresh_signal_accepted"
            ],
            gates[
                "expired_signal_rejected"
            ],
            gates[
                "loss_cooldown_test"
            ],
            gates[
                "duplicate_signal_rejected"
            ],
            gates[
                "one_direction_gate"
            ],
            leverage_gate,
            quantity_positive,
            minimum_passed,
            exposure_passed,
        ]
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

    if external_position_clear:
        position_text = (
            f"No open {SYMBOL} "
            "position detected"
        )

    else:
        position_text = (
            f"{len(active_positions)} "
            f"active {SYMBOL} "
            "position(s) detected"
        )

    report = (
        f"{status_icon} MODULE "
        f"{MODULE_NAME} "
        f"{status_text}\n"

        f"{SYMBOL}\n\n"

        f"Available USDT: "
        f"{fmt(balance)}\n"

        f"Mark Price: "
        f"{fmt(mark_price)} USDT\n\n"

        "FINAL EXECUTION GATE\n"

        f"API Trading Symbol: "
        f"{yes_no(api_symbol_ok)}\n"

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
        f"{yes_no(external_position_clear)}\n\n"

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
        f"{yes_no(leverage_gate)}\n\n"

        "DYNAMIC ENTRY\n"

        f"Margin: "
        f"{fmt(entry['margin'])} USDT\n"

        f"Notional: "
        f"{fmt(entry['notional'])} USDT\n"

        f"Quantity: "
        f"{fmt(entry['quantity'])}\n"

        f"Quantity Positive: "
        f"{yes_no(quantity_positive)}\n"

        f"Minimum Passed: "
        f"{yes_no(minimum_passed)}\n\n"

        "WORST-CASE EXPOSURE\n"

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
        f"{yes_no(exposure_passed)}\n\n"

        "TP / TRAILING\n"

        f"TP1 / TP2 / TP3: "
        f"{fmt(TP1_PERCENT)}% / "
        f"{fmt(TP2_PERCENT)}% / "
        f"{fmt(TP3_PERCENT)}%\n"

        f"TP1 Trigger: "
        f"{fmt(TP1_TRIGGER_PERCENT)}%\n"

        f"TP2 Trigger: "
        f"{fmt(TP2_TRIGGER_PERCENT)}%\n"

        f"Trailing Distance: "
        f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n\n"

        "POSITION CHECK\n"

        f"{position_text}\n\n"

        "R17 ORDER PAYLOAD SIMULATION\n"

        f"Symbol: "
        f"{simulated_payload['symbol']}\n"

        f"Side: "
        f"{simulated_payload['side']}\n"

        f"Position Side: "
        f"{simulated_payload['positionSide']}\n"

        f"Type: "
        f"{simulated_payload['type']}\n"

        f"Quantity: "
        f"{simulated_payload['quantity']}\n\n"

        "ORDER TRANSMISSION\n"

        f"Real Endpoint: "
        f"{REAL_ORDER_PATH}\n"

        f"Demo Endpoint: "
        f"{DEMO_ORDER_PATH}\n"

        "Real POST Called: ❌ NO\n"
        "Demo POST Called: ❌ NO\n"
        "Payload Transmission: ❌ NO\n\n"

        "🛡 R17 absolute real-order POST lock active\n"
        "🛡 R17 demo-order POST lock active\n"
        "⚠️ LIVE ORDER EXECUTION DISABLED\n"
        "⚠️ NO LIVE ORDER WAS SENT"
    )

    return (
        all_passed,
        report,
    )


# ============================================================
# ERROR REPORT
# ============================================================

def build_error_report(
    stage,
    exc,
):
    return (
        f"❌ MODULE "
        f"{MODULE_NAME} ERROR\n"

        f"{SYMBOL}\n\n"

        f"Stage: "
        f"{stage}\n"

        f"{type(exc).__name__}: "
        f"{exc}\n\n"

        "🛡 R17 absolute real-order POST lock active\n"
        "🛡 R17 demo-order POST lock active\n"
        "⚠️ LIVE ORDER EXECUTION DISABLED\n"
        "⚠️ NO LIVE ORDER WAS SENT"
    )


# ============================================================
# HEALTH SERVER FOR RENDER
# ============================================================

class HealthHandler(
    BaseHTTPRequestHandler
):
    def do_GET(
        self,
    ):
        body = (
            f"{MODULE_NAME} ACTIVE\n"
            "LIVE ORDER EXECUTION DISABLED\n"
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    body
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args,
    ):
        return


def start_health_server():
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = HTTPServer(
        (
            "0.0.0.0",
            port,
        ),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {port}"
    )


# ============================================================
# MAIN
# ============================================================

async def main():
    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "READ-ONLY AUTHENTICATED "
        "EXECUTION VALIDATION"
    )

    print(
        "ABSOLUTE ORDER POST LOCK"
    )

    print(
        "=" * 60
    )

    stage = (
        "configuration"
    )

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:
            # ================================================
            # CONFIGURATION
            # ================================================

            validate_configuration()


            # ================================================
            # BALANCE
            # ================================================

            stage = "balance"

            balance = await get_balance(
                session
            )


            # ================================================
            # MARK PRICE
            # ================================================

            stage = "mark price"

            mark_price = await get_mark_price(
                session
            )


            # ================================================
            # CONTRACT INFO
            # ================================================

            stage = (
                "contract information"
            )

            contract = await get_contract_info(
                session
            )

            contract_settings = (
                extract_contract_settings(
                    contract
                )
            )


            # ================================================
            # API TRADING SYMBOLS
            # ================================================

            stage = (
                "API trading symbols"
            )

            api_symbols = (
                await get_api_trading_symbols(
                    session
                )
            )

            api_symbol_ok = (
                SYMBOL
                in api_symbols
            )


            # ================================================
            # POSITIONS
            # ================================================

            stage = "positions"

            positions = await get_positions(
                session
            )

            active_positions = (
                active_symbol_positions(
                    positions
                )
            )


            # ================================================
            # DYNAMIC ENTRY
            # ================================================

            stage = (
                "dynamic entry sizing"
            )

            entry = calculate_entry(
                balance=balance,
                mark_price=mark_price,
                quantity_precision=(
                    contract_settings[
                        "quantity_precision"
                    ]
                ),
            )


            # ================================================
            # SIGNAL SAFETY GATES
            # ================================================

            stage = (
                "signal gate simulation"
            )

            gates = (
                run_signal_gate_tests()
            )


            # ================================================
            # PAYLOAD SIMULATION ONLY
            # ================================================

            stage = (
                "order payload simulation"
            )

            simulated_payload = (
                create_simulated_order_payload(
                    entry[
                        "quantity"
                    ]
                )
            )


            # ================================================
            # IMPORTANT
            #
            # THERE IS DELIBERATELY NO:
            #
            # await weex_post(...)
            #
            # HERE.
            #
            # NO REAL OR DEMO ORDER IS TRANSMITTED.
            # ================================================


            # ================================================
            # REPORT
            # ================================================

            stage = "report"

            (
                all_passed,
                report,
            ) = build_success_report(
                balance=balance,
                mark_price=mark_price,
                contract_settings=contract_settings,
                api_symbol_ok=api_symbol_ok,
                entry=entry,
                gates=gates,
                active_positions=active_positions,
                simulated_payload=simulated_payload,
            )

            print()

            print(
                report
            )

            print()


            # ================================================
            # SINGLE TELEGRAM MESSAGE
            # ================================================

            await send_telegram(
                session,
                report,
            )


            # ================================================
            # FINAL STATUS
            # ================================================

            print(
                "=" * 60
            )

            if all_passed:
                print(
                    f"{MODULE_NAME} "
                    "COMPLETE: PASSED"
                )

            else:
                print(
                    f"{MODULE_NAME} "
                    "COMPLETE: NOT READY"
                )

            print(
                "=" * 60
            )


        except Exception as exc:
            report = (
                build_error_report(
                    stage,
                    exc,
                )
            )

            print()

            print(
                report
            )

            print()

            await send_telegram(
                session,
                report,
            )

            print(
                "=" * 60
            )

            print(
                f"{MODULE_NAME} "
                "COMPLETE: ERROR"
            )

            print(
                "=" * 60
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    start_health_server()

    asyncio.run(
        main()
    )

    while True:
        time.sleep(
            3600
        )
