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


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R10"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

MARGIN_ASSET = os.getenv(
    "MARGIN_ASSET",
    "USDT",
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

TP1_CLOSE_PERCENT = Decimal(
    os.getenv(
        "TP1_CLOSE_PERCENT",
        "20",
    )
)

TP2_CLOSE_PERCENT = Decimal(
    os.getenv(
        "TP2_CLOSE_PERCENT",
        "20",
    )
)

TP3_CLOSE_PERCENT = Decimal(
    os.getenv(
        "TP3_CLOSE_PERCENT",
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
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
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

PLANNING_MMR_PERCENT = Decimal(
    os.getenv(
        "PLANNING_MMR_PERCENT",
        "0.5",
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

ONE_DIRECTION_ONLY = (
    os.getenv(
        "ONE_DIRECTION_ONLY",
        "true",
    ).lower()
    == "true"
)


# ============================================================
# HARD SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True


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
# CONSTANTS
# ============================================================

ZERO = Decimal("0")

ONE_HUNDRED = Decimal("100")


# ============================================================
# DECIMAL HELPERS
# ============================================================

def safe_decimal(
    value,
    default="0",
):
    try:
        if value is None:
            return Decimal(
                default
            )

        if value == "":
            return Decimal(
                default
            )

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
    value = safe_decimal(
        value
    )

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

    return text or "0"


def quantize_down(
    value,
    precision,
):
    value = safe_decimal(
        value
    )

    precision = max(
        0,
        int(
            precision
        ),
    )

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
# TELEGRAM SENDER
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
            "TELEGRAM: credentials missing"
        )

        return False

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
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

            text = await response.text()

            if response.status != 200:
                print(
                    "TELEGRAM HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

                return False

            print(
                "TELEGRAM MESSAGE SENT"
            )

            return True

    except Exception as exc:
        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return False


# ============================================================
# WEEX REQUEST SIGNING
# ============================================================

def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    path_with_query = request_path

    if query_string:
        path_with_query += (
            "?"
            + query_string
        )

    prehash = (
        f"{timestamp}"
        f"{method.upper()}"
        f"{path_with_query}"
        f"{body}"
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
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


def auth_headers(
    method,
    request_path,
    params=None,
    body="",
):
    if (
        not WEEX_API_KEY
        or not WEEX_API_SECRET
        or not WEEX_API_PASSPHRASE
    ):
        raise RuntimeError(
            "WEEX credentials are missing"
        )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    query_string = urlencode(
        params or {}
    )

    signature = build_signature(
        timestamp,
        method,
        request_path,
        query_string,
        body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP":
            timestamp,
        "Content-Type":
            "application/json",
    }


# ============================================================
# PUBLIC WEEX GET
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
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                "WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Invalid WEEX JSON: "
                f"{text}"
            ) from exc


# ============================================================
# PRIVATE WEEX GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):
    params = (
        params
        or {}
    )

    headers = auth_headers(
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

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                "WEEX PRIVATE HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Invalid WEEX private JSON: "
                f"{text}"
            ) from exc


# ============================================================
# MARK PRICE
# R10 CORRECTED WEEX V3 ENDPOINT
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
        params=params,
    )

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Unexpected mark-price "
            f"response: {data}"
        )

    price = safe_decimal(
        data.get(
            "price"
        )
    )

    if price <= ZERO:
        raise RuntimeError(
            "Invalid WEEX mark price: "
            f"{price}"
        )

    return price


# ============================================================
# API TRADING SYMBOL CHECK
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

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "symbols",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                data = value
                break

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected trading "
            "symbol response: "
            f"{data}"
        )

    normalized = set()

    for item in data:

        if isinstance(
            item,
            str,
        ):
            normalized.add(
                item.upper()
            )

        elif isinstance(
            item,
            dict,
        ):
            symbol = str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()

            if symbol:
                normalized.add(
                    symbol
                )

    return normalized


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

    if isinstance(
        data,
        dict,
    ):
        symbols = (
            data.get(
                "symbols"
            )
            or []
        )

    elif isinstance(
        data,
        list,
    ):
        symbols = data

    target = None

    for item in symbols:

        if not isinstance(
            item,
            dict,
        ):
            continue

        if (
            str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):
            target = item
            break

    if (
        target is None
        and len(
            symbols
        )
        == 1
        and isinstance(
            symbols[0],
            dict,
        )
    ):
        target = symbols[0]

    if target is None:
        raise RuntimeError(
            "Contract information "
            f"not found for {SYMBOL}"
        )

    quantity_precision = int(
        target.get(
            "quantityPrecision",
            4,
        )
    )

    min_order = safe_decimal(
        target.get(
            "minOrderSize"
        )
        or target.get(
            "minQty"
        )
        or target.get(
            "minTradeNum"
        )
        or "0.0001"
    )

    contract_value = safe_decimal(
        target.get(
            "contractVal"
        )
        or target.get(
            "contractValue"
        )
        or target.get(
            "sizeMultiplier"
        )
        or min_order
        or "0.0001"
    )

    min_leverage = safe_decimal(
        target.get(
            "minLeverage"
        ),
        "1",
    )

    max_leverage = safe_decimal(
        target.get(
            "maxLeverage"
        ),
        "0",
    )

    filters = (
        target.get(
            "filters"
        )
        or []
    )

    if isinstance(
        filters,
        list,
    ):
        for item in filters:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if "minLeverage" in item:
                min_leverage = (
                    safe_decimal(
                        item.get(
                            "minLeverage"
                        ),
                        fmt(
                            min_leverage
                        ),
                    )
                )

            if "maxLeverage" in item:
                max_leverage = (
                    safe_decimal(
                        item.get(
                            "maxLeverage"
                        ),
                        fmt(
                            max_leverage
                        ),
                    )
                )

    # BTCUSDT confirmed diagnostic baseline.
    # Used only if WEEX omits these fields.

    if SYMBOL == "BTCUSDT":

        if min_order <= ZERO:
            min_order = Decimal(
                "0.0001"
            )

        if contract_value <= ZERO:
            contract_value = Decimal(
                "0.0001"
            )

        if min_leverage <= ZERO:
            min_leverage = Decimal(
                "1"
            )

        if max_leverage <= ZERO:
            max_leverage = Decimal(
                "400"
            )

    if min_order <= ZERO:
        raise RuntimeError(
            "Unable to determine "
            "minimum order"
        )

    return {
        "min_order":
            min_order,

        "quantity_precision":
            quantity_precision,

        "contract_value":
            contract_value,

        "min_leverage":
            min_leverage,

        "max_leverage":
            max_leverage,
    }


# ============================================================
# AVAILABLE BALANCE
# ============================================================

async def get_available_balance(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    candidates = []

    if isinstance(
        data,
        list,
    ):
        candidates = data

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

        asset = str(
            item.get(
                "asset"
            )
            or item.get(
                "coinName"
            )
            or item.get(
                "coin"
            )
            or ""
        ).upper()

        if (
            asset
            and asset
            != MARGIN_ASSET
        ):
            continue

        for key in (
            "availableBalance",
            "available",
            "availableAmount",
            "free",
            "balance",
        ):
            if key not in item:
                continue

            value = safe_decimal(
                item.get(
                    key
                )
            )

            if value >= ZERO:
                return value

    raise RuntimeError(
        "Unable to extract "
        f"available {MARGIN_ASSET} "
        "balance"
    )


# ============================================================
# REAL WEEX POSITION CHECK
# ============================================================

async def get_symbol_positions(
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

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "positions",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                data = value
                break

    if not isinstance(
        data,
        list,
    ):

        if isinstance(
            data,
            dict,
        ):
            data = [
                data
            ]

        else:
            return []

    positions = []

    for item in data:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                SYMBOL,
            )
        ).upper()

        if symbol != SYMBOL:
            continue

        size = safe_decimal(
            item.get(
                "size"
            )
        )

        if size > ZERO:
            positions.append(
                item
            )

    return positions


# ============================================================
# DYNAMIC ENTRY SIZING
# ============================================================

def calculate_quantity(
    balance,
    mark_price,
    quantity_precision,
):
    margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / ONE_HUNDRED
    )

    notional = (
        margin
        * LEVERAGE
    )

    if mark_price <= ZERO:
        return (
            margin,
            notional,
            ZERO,
        )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = quantize_down(
        raw_quantity,
        quantity_precision,
    )

    return (
        margin,
        notional,
        quantity,
    )


# ============================================================
# EXPOSURE PLAN
# ============================================================

def worst_case_exposure_percent():
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
# FINAL EXECUTION GATE SIMULATION
# ============================================================

def run_signal_gate_simulation(
    no_external_position,
):
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
        - 1
    )

    last_loss_time = (
        now
        - LOSS_COOLDOWN_SECONDS
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

    cooldown_passed = (
        now
        - last_loss_time
        >= LOSS_COOLDOWN_SECONDS
    )

    seen_signal_ids = set()

    signal_id = (
        f"{SYMBOL}:"
        "LONG:"
        f"{fresh_signal_time}"
    )

    first_accept = (
        signal_id
        not in seen_signal_ids
    )

    seen_signal_ids.add(
        signal_id
    )

    second_reject = (
        signal_id
        in seen_signal_ids
    )

    duplicate_signal_rejected = (
        first_accept
        and second_reject
    )

    one_direction_gate = True

    if ONE_DIRECTION_ONLY:
        one_direction_gate = (
            no_external_position
        )

    return {
        "fresh_signal_accepted":
            fresh_signal_accepted,

        "expired_signal_rejected":
            expired_signal_rejected,

        "cooldown_passed":
            cooldown_passed,

        "duplicate_signal_rejected":
            duplicate_signal_rejected,

        "one_direction_gate":
            one_direction_gate,
    }


# ============================================================
# DRY-RUN ORDER PAYLOAD
# NO REQUEST IS TRANSMITTED
# ============================================================

def build_dry_run_order_payload(
    quantity,
):
    client_id = (
        "r10-"
        f"{SYMBOL.lower()}-"
        f"{int(time.time())}"
    )

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
# REPORT BUILDER
# ============================================================

def build_report(
    balance,
    mark_price,
    contract,
    api_symbol_ok,
    positions,
    margin,
    notional,
    quantity,
    gates,
):
    min_order = (
        contract[
            "min_order"
        ]
    )

    quantity_precision = (
        contract[
            "quantity_precision"
        ]
    )

    contract_value = (
        contract[
            "contract_value"
        ]
    )

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

    leverage_gate = (
        LEVERAGE
        >= weex_min_leverage
        and LEVERAGE
        <= MAX_LEVERAGE
        and (
            weex_max_leverage
            <= ZERO
            or LEVERAGE
            <= weex_max_leverage
        )
    )

    quantity_positive = (
        quantity
        > ZERO
    )

    minimum_passed = (
        quantity
        >= min_order
    )

    (
        initial,
        pyramids,
        backups,
        exposure_total,
    ) = (
        worst_case_exposure_percent()
    )

    exposure_passed = (
        exposure_total
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    tp_total = (
        TP1_CLOSE_PERCENT
        + TP2_CLOSE_PERCENT
        + TP3_CLOSE_PERCENT
    )

    tp_split_passed = (
        tp_total
        == ONE_HUNDRED
    )

    no_external_position = (
        len(
            positions
        )
        == 0
    )

    final_gate = all(
        [
            api_symbol_ok,
            leverage_gate,
            quantity_positive,
            minimum_passed,
            exposure_passed,
            tp_split_passed,

            gates[
                "fresh_signal_accepted"
            ],

            gates[
                "expired_signal_rejected"
            ],

            gates[
                "cooldown_passed"
            ],

            gates[
                "duplicate_signal_rejected"
            ],

            gates[
                "one_direction_gate"
            ],

            no_external_position,

            HARD_EXECUTION_LOCK,

            not LIVE_ORDER_EXECUTION,
        ]
    )

    payload = (
        build_dry_run_order_payload(
            quantity
        )
    )

    position_lines = []

    if no_external_position:

        position_lines.append(
            "No open position detected"
        )

        position_lines.append(
            "WEEX Liquidation Price: N/A"
        )

    else:

        for position in positions:

            side = str(
                position.get(
                    "side",
                    "UNKNOWN",
                )
            )

            size = fmt(
                position.get(
                    "size",
                    "0",
                )
            )

            liquidation_price = fmt(
                position.get(
                    "liquidatePrice",
                    "0",
                )
            )

            position_lines.append(
                f"{side} Size: "
                f"{size}"
            )

            if liquidation_price == "0":
                liquidation_price = "N/A"

            position_lines.append(
                "WEEX Liquidation Price: "
                f"{liquidation_price}"
            )

    status_icon = (
        "✅"
        if final_gate
        else "⚠️"
    )

    status_text = (
        "DIAGNOSTIC PASSED"
        if final_gate
        else "NOT READY"
    )

    lines = [
        (
            f"{status_icon} MODULE "
            f"{MODULE_NAME} "
            f"{status_text}"
        ),

        SYMBOL,

        "",

        (
            f"Available "
            f"{MARGIN_ASSET}: "
            f"{fmt(balance)}"
        ),

        (
            f"Mark Price: "
            f"{fmt(mark_price)} "
            f"{MARGIN_ASSET}"
        ),

        "",

        "FINAL EXECUTION GATE",

        (
            "API Trading Symbol: "
            f"{yes_no(api_symbol_ok)}"
        ),

        (
            "Fresh Signal Accepted: "
            f"{yes_no(gates['fresh_signal_accepted'])}"
        ),

        (
            "Expired Signal Rejected: "
            f"{yes_no(gates['expired_signal_rejected'])}"
        ),

        (
            "Loss Cooldown Test: "
            f"{yes_no(gates['cooldown_passed'])}"
        ),

        (
            "Duplicate Signal Rejected: "
            f"{yes_no(gates['duplicate_signal_rejected'])}"
        ),

        (
            "One Direction Gate: "
            f"{yes_no(gates['one_direction_gate'])}"
        ),

        (
            "External Position Clear: "
            f"{yes_no(no_external_position)}"
        ),

        "",

        "ADJUSTABLE CONFIG",

        (
            "Entry: "
            f"{fmt(INITIAL_ENTRY_PERCENT)}%"
        ),

        (
            "Leverage: "
            f"{fmt(LEVERAGE)}x"
        ),

        (
            "Max Config Leverage: "
            f"{fmt(MAX_LEVERAGE)}x"
        ),

        (
            "Max Pyramids: "
            f"{MAX_PYRAMID_ADDS}"
        ),

        (
            "Pyramid Size: "
            f"{fmt(PYRAMID_SIZE_PERCENT)}%"
        ),

        (
            "Max Backups: "
            f"{MAX_BACKUPS}"
        ),

        (
            "Backup Size: "
            f"{fmt(BACKUP_SIZE_PERCENT)}% each"
        ),

        (
            "Max Fund Exposure: "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),

        "",

        "WEEX CONTRACT",

        (
            "Minimum Order: "
            f"{fmt(min_order)}"
        ),

        (
            "Quantity Precision: "
            f"{quantity_precision}"
        ),

        (
            "Contract Value: "
            f"{fmt(contract_value)}"
        ),

        (
            "WEEX Min Leverage: "
            f"{fmt(weex_min_leverage)}x"
        ),

        (
            "WEEX Max Leverage: "
            f"{fmt(weex_max_leverage)}x"
        ),

        (
            "Leverage Gate: "
            f"{yes_no(leverage_gate)}"
        ),

        "",

        "DYNAMIC ENTRY",

        (
            "Margin: "
            f"{fmt(margin)} "
            f"{MARGIN_ASSET}"
        ),

        (
            "Notional: "
            f"{fmt(notional)} "
            f"{MARGIN_ASSET}"
        ),

        (
            "Quantity: "
            f"{fmt(quantity)}"
        ),

        (
            "Quantity Positive: "
            f"{yes_no(quantity_positive)}"
        ),

        (
            "Minimum Passed: "
            f"{yes_no(minimum_passed)}"
        ),

        "",

        "WORST-CASE EXPOSURE",

        (
            "Initial: "
            f"{fmt(initial)}%"
        ),

        (
            "Pyramids: "
            f"{fmt(pyramids)}%"
        ),

        (
            "Backups: "
            f"{fmt(backups)}%"
        ),

        (
            "Total: "
            f"{fmt(exposure_total)}% / "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),

        (
            "Exposure Passed: "
            f"{yes_no(exposure_passed)}"
        ),

        "",

        "TP / TRAILING",

        (
            "TP1 / TP2 / TP3: "
            f"{fmt(TP1_CLOSE_PERCENT)}% / "
            f"{fmt(TP2_CLOSE_PERCENT)}% / "
            f"{fmt(TP3_CLOSE_PERCENT)}%"
        ),

        (
            "TP Split Valid: "
            f"{yes_no(tp_split_passed)}"
        ),

        (
            "TP1 Trigger: "
            f"{fmt(TP1_TRIGGER_PERCENT)}%"
        ),

        (
            "TP2 Trigger: "
            f"{fmt(TP2_TRIGGER_PERCENT)}%"
        ),

        (
            "Trailing Distance: "
            f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
        ),

        "",

        "LIQUIDATION SETTINGS",

        (
            "Backup Buffer: "
            f"{fmt(BACKUP_BUFFER_PERCENT)}%"
        ),

        (
            "Min Liq Distance: "
            f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%"
        ),

        (
            "Planning MMR: "
            f"{fmt(PLANNING_MMR_PERCENT)}%"
        ),

        "",

        "REAL WEEX POSITION",

        *position_lines,

        "",

        "R10 ORDER PAYLOAD SIMULATION",

        (
            "Endpoint Target: "
            "/capi/v3/order"
        ),

        (
            "Payload: "
            + json.dumps(
                payload,
                separators=(
                    ",",
                    ":",
                ),
            )
        ),

        "",

        "🛡 Hard execution lock active",

        "⚠️ Live order execution disabled",

        "⚠️ NO LIVE ORDER WAS SENT",
    ]

    return (
        "\n".join(
            lines
        ),
        final_gate,
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
        "FINAL PRE-LIVE DRY-RUN"
    )

    print(
        "NO LIVE ORDER TRANSMISSION"
    )

    print(
        "=" * 60
    )

    timeout = (
        aiohttp.ClientTimeout(
            total=20
        )
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:

            # ================================================
            # ABSOLUTE R10 SAFETY CHECK
            # ================================================

            if (
                not HARD_EXECUTION_LOCK
                or LIVE_ORDER_EXECUTION
            ):
                raise RuntimeError(
                    "R10 safety lock "
                    "configuration is invalid"
                )

            # ================================================
            # MARK PRICE
            # ================================================

            mark_price = (
                await get_mark_price(
                    session
                )
            )

            # ================================================
            # API SYMBOL
            # ================================================

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
            # CONTRACT
            # ================================================

            contract = (
                await get_contract_info(
                    session
                )
            )

            # ================================================
            # BALANCE
            # ================================================

            balance = (
                await get_available_balance(
                    session
                )
            )

            # ================================================
            # REAL POSITION CHECK
            # ================================================

            positions = (
                await get_symbol_positions(
                    session
                )
            )

            # ================================================
            # ENTRY SIZE
            # ================================================

            (
                margin,
                notional,
                quantity,
            ) = (
                calculate_quantity(
                    balance,
                    mark_price,
                    contract[
                        "quantity_precision"
                    ],
                )
            )

            # ================================================
            # EXECUTION GATE SIMULATION
            # ================================================

            no_external_position = (
                len(
                    positions
                )
                == 0
            )

            gates = (
                run_signal_gate_simulation(
                    no_external_position
                )
            )

            # ================================================
            # FINAL REPORT
            # ================================================

            (
                report,
                final_gate,
            ) = (
                build_report(
                    balance,
                    mark_price,
                    contract,
                    api_symbol_ok,
                    positions,
                    margin,
                    notional,
                    quantity,
                    gates,
                )
            )

            print(
                report
            )

            print(
                "=" * 60
            )

            # ================================================
            # ONE TELEGRAM MESSAGE ONLY
            # ================================================

            await send_telegram(
                session,
                report,
            )

        except Exception as exc:

            error_message = (
                f"❌ MODULE "
                f"{MODULE_NAME} ERROR\n"
                f"{SYMBOL}\n\n"

                f"{type(exc).__name__}: "
                f"{exc}\n\n"

                "🛡 Hard execution lock active\n"

                "⚠️ Live order execution disabled\n"

                "⚠️ NO LIVE ORDER WAS SENT"
            )

            print(
                error_message
            )

            print(
                "=" * 60
            )

            # Only one error Telegram
            # if an actual exception occurs.

            await send_telegram(
                session,
                error_message,
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        main())
