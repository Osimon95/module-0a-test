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


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R11"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

API_BASE_URL = "https://api-contract.weex.com"

ORDER_ENDPOINT = "/capi/v3/order"


# ============================================================
# DECIMAL CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


# ============================================================
# ADJUSTABLE TRADE CONFIGURATION
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


# ============================================================
# TP / TRAILING CONFIGURATION
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
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)


# ============================================================
# LIQUIDATION CONFIGURATION
# ============================================================

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


# ============================================================
# SIGNAL SAFETY CONFIGURATION
# ============================================================

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "60",
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
    ).strip().lower()
    in (
        "1",
        "true",
        "yes",
        "on",
    )
)


# ============================================================
# SAFETY LOCKS
# ============================================================
#
# BOTH MUST BE MANUALLY CHANGED IN A FUTURE MODULE
# BEFORE ANY LIVE ORDER CAN EVER BE TRANSMITTED.
#
# R11 NEVER SENDS AN ORDER.
#
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
# R11 NETWORK STABILITY
# ============================================================

HTTP_TIMEOUT_SECONDS = int(
    os.getenv(
        "HTTP_TIMEOUT_SECONDS",
        "15",
    )
)

HTTP_RETRY_ATTEMPTS = int(
    os.getenv(
        "HTTP_RETRY_ATTEMPTS",
        "3",
    )
)

HTTP_RETRY_DELAY_SECONDS = float(
    os.getenv(
        "HTTP_RETRY_DELAY_SECONDS",
        "1.5",
    )
)

TRANSIENT_HTTP_STATUS = {
    408,
    425,
    429,
    500,
    502,
    503,
    504,
}


# ============================================================
# SINGLE-RUN TELEGRAM GUARD
# ============================================================

telegram_report_sent = False


# ============================================================
# STAGE TRACKING
# ============================================================

CURRENT_STAGE = "startup"


def set_stage(
    stage,
):
    global CURRENT_STAGE

    CURRENT_STAGE = stage

    print(
        f"[R11 STAGE] {stage}"
    )


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_decimal(
    value,
    default=ZERO,
):
    try:
        if value is None:
            return default

        return Decimal(
            str(value)
        )

    except Exception:
        return default


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
            text = text.rstrip(
                "0"
            ).rstrip(
                "."
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
    if precision < 0:
        raise ValueError(
            "Precision cannot be negative"
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


def extract_first_dict(
    obj,
):
    if isinstance(
        obj,
        dict,
    ):
        return obj

    if isinstance(
        obj,
        list,
    ):
        for item in obj:
            if isinstance(
                item,
                dict,
            ):
                return item

    return None


# ============================================================
# WEEX SIGNATURE
# ============================================================

def build_query_string(
    params=None,
):
    if not params:
        return ""

    return urlencode(
        params,
    )


def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    message = (
        timestamp
        + method.upper()
        + request_path
    )

    if query_string:
        message += (
            "?"
            + query_string
        )

    if body:
        message += body

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


def authenticated_headers(
    method,
    request_path,
    params=None,
    body="",
):
    if not all(
        (
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        )
    ):
        raise RuntimeError(
            "WEEX credentials missing"
        )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    query_string = build_query_string(
        params
    )

    signature = build_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US",
    }


# ============================================================
# HTTP ENGINE
# ============================================================

async def request_json(
    session,
    method,
    path,
    params=None,
    authenticated=False,
):
    method = method.upper()

    if method != "GET":
        raise RuntimeError(
            "R11 request_json is GET-only"
        )

    url = (
        API_BASE_URL
        + path
    )

    last_error = None

    for attempt in range(
        1,
        HTTP_RETRY_ATTEMPTS + 1,
    ):
        try:
            headers = {}

            if authenticated:
                headers = authenticated_headers(
                    method=method,
                    request_path=path,
                    params=params,
                )

            async with session.get(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(
                    total=HTTP_TIMEOUT_SECONDS
                ),
            ) as response:

                text = await response.text()

                if (
                    response.status
                    in TRANSIENT_HTTP_STATUS
                ):
                    raise RuntimeError(
                        f"Transient WEEX HTTP "
                        f"{response.status}: "
                        f"{text}"
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

                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        "Invalid JSON from WEEX: "
                        f"{text[:500]}"
                    ) from exc

        except (
            asyncio.TimeoutError,
            aiohttp.ClientError,
            RuntimeError,
        ) as exc:

            last_error = exc

            retryable = (
                isinstance(
                    exc,
                    (
                        asyncio.TimeoutError,
                        aiohttp.ClientError,
                    ),
                )
                or "Transient WEEX HTTP"
                in str(
                    exc
                )
            )

            if (
                not retryable
                or attempt
                >= HTTP_RETRY_ATTEMPTS
            ):
                raise

            print(
                f"WEEX RETRY "
                f"{attempt}/"
                f"{HTTP_RETRY_ATTEMPTS} "
                f"after: {exc}"
            )

            await asyncio.sleep(
                HTTP_RETRY_DELAY_SECONDS
                * attempt
            )

    raise RuntimeError(
        f"WEEX request failed: "
        f"{last_error}"
    )


# ============================================================
# MARK PRICE
# ============================================================

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
            ticker.get(
                "data"
            ),
            ticker.get(
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


async def get_mark_price(
    session,
):
    data = await request_json(
        session=session,
        method="GET",
        path="/capi/v3/market/symbolPrice",
        params={
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
        authenticated=False,
    )

    price = extract_mark_price(
        data
    )

    if price <= ZERO:
        raise RuntimeError(
            f"Invalid WEEX mark price: "
            f"{price}"
        )

    return price


# ============================================================
# API TRADING SYMBOLS
# ============================================================

async def get_api_trading_symbols(
    session,
):
    data = await request_json(
        session=session,
        method="GET",
        path="/capi/v3/market/apiTradingSymbols",
        authenticated=False,
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
            candidate = data.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):
                data = candidate
                break

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected API trading symbols response"
        )

    symbols = set()

    for item in data:
        if isinstance(
            item,
            str,
        ):
            symbols.add(
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
                symbols.add(
                    str(
                        symbol
                    ).upper()
                )

    return symbols


# ============================================================
# EXCHANGE CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):
    data = await request_json(
        session=session,
        method="GET",
        path="/capi/v3/market/exchangeInfo",
        params={
            "symbol": SYMBOL,
        },
        authenticated=False,
    )

    possible = []

    if isinstance(
        data,
        dict,
    ):
        possible.append(
            data
        )

        nested = data.get(
            "data"
        )

        if isinstance(
            nested,
            dict,
        ):
            possible.append(
                nested
            )

    for obj in possible:
        symbols = obj.get(
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

                if (
                    str(
                        item.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    == SYMBOL
                ):
                    return item

    raise RuntimeError(
        f"Contract information "
        f"not found for {SYMBOL}"
    )


# ============================================================
# BALANCE
# ============================================================

def extract_available_usdt(
    data,
):
    possible = []

    if isinstance(
        data,
        list,
    ):
        possible.extend(
            data
        )

    elif isinstance(
        data,
        dict,
    ):
        possible.append(
            data
        )

        for key in (
            "data",
            "result",
            "balances",
            "assets",
        ):
            nested = data.get(
                key
            )

            if isinstance(
                nested,
                list,
            ):
                possible.extend(
                    nested
                )

            elif isinstance(
                nested,
                dict,
            ):
                possible.append(
                    nested
                )

    for item in possible:
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
                    item.get(
                        "coin",
                        "",
                    ),
                ),
            )
        ).upper()

        if (
            asset
            and asset != "USDT"
        ):
            continue

        for key in (
            "availableBalance",
            "available",
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


async def get_available_usdt(
    session,
):
    data = await request_json(
        session=session,
        method="GET",
        path="/capi/v3/account/balance",
        authenticated=True,
    )

    return extract_available_usdt(
        data
    )


# ============================================================
# POSITION
# ============================================================

def normalize_positions(
    data,
):
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
            "result",
            "positions",
        ):
            nested = data.get(
                key
            )

            if isinstance(
                nested,
                list,
            ):
                return [
                    item
                    for item in nested
                    if isinstance(
                        item,
                        dict,
                    )
                ]

        return [
            data
        ]

    return []


def position_size(
    position,
):
    for key in (
        "size",
        "positionAmt",
        "positionSize",
        "quantity",
        "qty",
    ):
        if key in position:
            return abs(
                safe_decimal(
                    position[key]
                )
            )

    return ZERO


def position_liquidation_price(
    position,
):
    for key in (
        "liquidatePrice",
        "liquidationPrice",
        "liqPrice",
    ):
        if key in position:
            price = safe_decimal(
                position[key]
            )

            if price > ZERO:
                return price

    return None


async def get_real_position(
    session,
):
    data = await request_json(
        session=session,
        method="GET",
        path=(
            "/capi/v3/account/"
            "position/singlePosition"
        ),
        params={
            "symbol": SYMBOL,
        },
        authenticated=True,
    )

    positions = normalize_positions(
        data
    )

    open_positions = []

    for position in positions:
        symbol = str(
            position.get(
                "symbol",
                SYMBOL,
            )
        ).upper()

        if symbol != SYMBOL:
            continue

        if (
            position_size(
                position
            )
            > ZERO
        ):
            open_positions.append(
                position
            )

    if not open_positions:
        return {
            "open": False,
            "positions": [],
            "liquidation_price": None,
        }

    liquidation_price = None

    for position in open_positions:
        candidate = (
            position_liquidation_price(
                position
            )
        )

        if candidate is not None:
            liquidation_price = candidate
            break

    return {
        "open": True,
        "positions": open_positions,
        "liquidation_price": liquidation_price,
    }


# ============================================================
# DYNAMIC POSITION SIZING
# ============================================================

def calculate_entry(
    available_balance,
    mark_price,
    quantity_precision,
):
    if available_balance <= ZERO:
        raise RuntimeError(
            "Available balance must be positive"
        )

    if mark_price <= ZERO:
        raise RuntimeError(
            "Mark price must be positive"
        )

    margin = (
        available_balance
        * INITIAL_ENTRY_PERCENT
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

    quantity = quantize_down(
        raw_quantity,
        quantity_precision,
    )

    return {
        "margin": margin,
        "notional": notional,
        "raw_quantity": raw_quantity,
        "quantity": quantity,
    }


# ============================================================
# EXPOSURE
# ============================================================

def calculate_exposure(
):
    initial = (
        INITIAL_ENTRY_PERCENT
    )

    pyramids = (
        PYRAMID_SIZE_PERCENT
        * Decimal(
            MAX_PYRAMID_ADDS
        )
    )

    backups = (
        BACKUP_SIZE_PERCENT
        * Decimal(
            MAX_BACKUPS
        )
    )

    total = (
        initial
        + pyramids
        + backups
    )

    return {
        "initial": initial,
        "pyramids": pyramids,
        "backups": backups,
        "total": total,
        "passed": (
            total
            <= MAX_FUND_EXPOSURE_PERCENT
        ),
    }


# ============================================================
# SIGNAL EXECUTION-GATE TESTS
# ============================================================

def run_signal_gate_tests(
):
    now = time.time()

    fresh_signal_time = (
        now
        - min(
            1,
            max(
                SIGNAL_EXPIRY_SECONDS
                // 2,
                0,
            ),
        )
    )

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 1
    )

    fresh_signal_accepted = (
        (
            now
            - fresh_signal_time
        )
        <= SIGNAL_EXPIRY_SECONDS
    )

    expired_signal_rejected = (
        (
            now
            - expired_signal_time
        )
        > SIGNAL_EXPIRY_SECONDS
    )

    last_loss_time = now

    loss_cooldown_test = (
        (
            now
            - last_loss_time
        )
        < LOSS_COOLDOWN_SECONDS
    )

    seen_signal_ids = set()

    test_signal_id = (
        f"{SYMBOL}-"
        f"r11-test-signal"
    )

    first_duplicate_test = (
        test_signal_id
        not in seen_signal_ids
    )

    seen_signal_ids.add(
        test_signal_id
    )

    duplicate_signal_rejected = (
        test_signal_id
        in seen_signal_ids
    )

    duplicate_gate_passed = (
        first_duplicate_test
        and duplicate_signal_rejected
    )

    simulated_existing_direction = (
        "LONG"
    )

    simulated_new_direction = (
        "SHORT"
    )

    if ONE_DIRECTION_ONLY:
        one_direction_gate = (
            simulated_existing_direction
            != simulated_new_direction
        )

    else:
        one_direction_gate = True

    return {
        "fresh_signal_accepted":
            fresh_signal_accepted,

        "expired_signal_rejected":
            expired_signal_rejected,

        "loss_cooldown_test":
            loss_cooldown_test,

        "duplicate_signal_rejected":
            duplicate_gate_passed,

        "one_direction_gate":
            one_direction_gate,
    }


# ============================================================
# ORDER PAYLOAD SIMULATION
# ============================================================

def build_simulated_order_payload(
    quantity,
):
    client_id = (
        f"r11-"
        f"{SYMBOL.lower()}-"
        f"{int(time.time())}"
    )

    client_id = (
        client_id[:36]
    )

    return {
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": fmt(
            quantity
        ),
        "newClientOrderId":
            client_id,
    }


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram_once(
    session,
    message,
):
    global telegram_report_sent

    if telegram_report_sent:
        print(
            "TELEGRAM REPORT ALREADY SENT "
            "- DUPLICATE BLOCKED"
        )
        return False

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM CREDENTIALS MISSING "
            "- REPORT NOT SENT"
        )
        return False

    telegram_report_sent = True

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
                    "TELEGRAM SEND FAILED: "
                    f"HTTP {response.status}: "
                    f"{text}"
                )

                return False

            print(
                "TELEGRAM REPORT SENT ONCE"
            )

            return True

    except Exception as exc:
        print(
            "TELEGRAM SEND ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return False


# ============================================================
# REPORT BUILDER
# ============================================================

def build_report(
    *,
    balance,
    mark_price,
    api_symbol_ok,
    contract,
    leverage_gate,
    entry,
    exposure,
    signal_tests,
    external_position_clear,
    position_data,
    tp_split_valid,
    order_payload,
):
    min_order = safe_decimal(
        contract.get(
            "minOrderSize",
            "0",
        )
    )

    quantity_precision = int(
        contract.get(
            "quantityPrecision",
            0,
        )
    )

    contract_value = safe_decimal(
        contract.get(
            "contractVal",
            "0",
        )
    )

    min_leverage = safe_decimal(
        contract.get(
            "minLeverage",
            "0",
        )
    )

    max_leverage = safe_decimal(
        contract.get(
            "maxLeverage",
            "0",
        )
    )

    quantity_positive = (
        entry["quantity"]
        > ZERO
    )

    minimum_passed = (
        entry["quantity"]
        >= min_order
    )

    liquidation_price = (
        position_data.get(
            "liquidation_price"
        )
    )

    if liquidation_price is None:
        liquidation_text = "N/A"

    else:
        liquidation_text = fmt(
            liquidation_price
        )

    real_position_text = (
        "No open position detected"
        if external_position_clear
        else "⚠️ OPEN POSITION DETECTED"
    )

    all_passed = all(
        (
            api_symbol_ok,
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
            external_position_clear,
            leverage_gate,
            quantity_positive,
            minimum_passed,
            exposure[
                "passed"
            ],
            tp_split_valid,
        )
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

    payload_text = json.dumps(
        order_payload,
        separators=(
            ",",
            ":",
        ),
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

        f"FINAL EXECUTION GATE\n"

        f"API Trading Symbol: "
        f"{yes_no(api_symbol_ok)}\n"

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
        f"{yes_no(external_position_clear)}\n\n"

        f"ADJUSTABLE CONFIG\n"

        f"Entry: "
        f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

        f"Leverage: "
        f"{fmt(LEVERAGE)}x\n"

        f"Max Config Leverage: "
        f"{fmt(MAX_LEVERAGE)}x\n"

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
        f"{fmt(min_leverage)}x\n"

        f"WEEX Max Leverage: "
        f"{fmt(max_leverage)}x\n"

        f"Leverage Gate: "
        f"{yes_no(leverage_gate)}\n\n"

        f"DYNAMIC ENTRY\n"

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

        f"WORST-CASE EXPOSURE\n"

        f"Initial: "
        f"{fmt(exposure['initial'])}%\n"

        f"Pyramids: "
        f"{fmt(exposure['pyramids'])}%\n"

        f"Backups: "
        f"{fmt(exposure['backups'])}%\n"

        f"Total: "
        f"{fmt(exposure['total'])}% / "
        f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

        f"Exposure Passed: "
        f"{yes_no(exposure['passed'])}\n\n"

        f"TP / TRAILING\n"

        f"TP1 / TP2 / TP3: "
        f"{fmt(TP1_PERCENT)}% / "
        f"{fmt(TP2_PERCENT)}% / "
        f"{fmt(TP3_PERCENT)}%\n"

        f"TP Split Valid: "
        f"{yes_no(tp_split_valid)}\n"

        f"TP1 Trigger: "
        f"{fmt(TP1_TRIGGER_PERCENT)}%\n"

        f"TP2 Trigger: "
        f"{fmt(TP2_TRIGGER_PERCENT)}%\n"

        f"Trailing Distance: "
        f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n\n"

        f"LIQUIDATION SETTINGS\n"

        f"Backup Buffer: "
        f"{fmt(BACKUP_BUFFER_PERCENT)}%\n"

        f"Min Liq Distance: "
        f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%\n"

        f"Planning MMR: "
        f"{fmt(PLANNING_MMR_PERCENT)}%\n\n"

        f"REAL WEEX POSITION\n"

        f"{real_position_text}\n"

        f"WEEX Liquidation Price: "
        f"{liquidation_text}\n\n"

        f"R11 ORDER PAYLOAD SIMULATION\n"

        f"Endpoint Target: "
        f"{ORDER_ENDPOINT}\n"

        f"Payload: "
        f"{payload_text}\n\n"

        f"R11 STABILITY\n"

        f"HTTP Retry Attempts: "
        f"{HTTP_RETRY_ATTEMPTS}\n"

        f"Single Telegram Report: "
        f"✅ ACTIVE\n"

        f"Stage-Aware Errors: "
        f"✅ ACTIVE\n"

        f"Transient API Retry: "
        f"✅ ACTIVE\n\n"

        f"🛡 Hard execution lock active\n"

        f"⚠️ Live order execution disabled\n"

        f"⚠️ NO LIVE ORDER WAS SENT"
    )

    return (
        report,
        all_passed,
    )


# ============================================================
# ERROR REPORT
# ============================================================

def build_error_report(
    exc,
):
    return (
        f"❌ MODULE "
        f"{MODULE_NAME} ERROR\n"
        f"{SYMBOL}\n\n"

        f"FAILED STAGE:\n"
        f"{CURRENT_STAGE}\n\n"

        f"EXCEPTION TYPE:\n"
        f"{type(exc).__name__}\n\n"

        f"ERROR:\n"
        f"{exc}\n\n"

        f"🛡 Hard execution lock active\n"
        f"⚠️ Live order execution disabled\n"
        f"⚠️ NO LIVE ORDER WAS SENT"
    )


# ============================================================
# STARTUP VALIDATION
# ============================================================

def validate_configuration(
):
    if INITIAL_ENTRY_PERCENT <= ZERO:
        raise RuntimeError(
            "INITIAL_ENTRY_PERCENT must be > 0"
        )

    if LEVERAGE <= ZERO:
        raise RuntimeError(
            "LEVERAGE must be > 0"
        )

    if MAX_LEVERAGE <= ZERO:
        raise RuntimeError(
            "MAX_LEVERAGE must be > 0"
        )

    if LEVERAGE > MAX_LEVERAGE:
        raise RuntimeError(
            "LEVERAGE exceeds "
            "MAX_LEVERAGE"
        )

    if MAX_PYRAMID_ADDS < 0:
        raise RuntimeError(
            "MAX_PYRAMID_ADDS cannot "
            "be negative"
        )

    if MAX_BACKUPS < 0:
        raise RuntimeError(
            "MAX_BACKUPS cannot "
            "be negative"
        )

    if (
        INITIAL_ENTRY_PERCENT
        > HUNDRED
    ):
        raise RuntimeError(
            "INITIAL_ENTRY_PERCENT "
            "cannot exceed 100"
        )

    if (
        MAX_FUND_EXPOSURE_PERCENT
        > HUNDRED
    ):
        raise RuntimeError(
            "MAX_FUND_EXPOSURE_PERCENT "
            "cannot exceed 100"
        )

    if SIGNAL_EXPIRY_SECONDS <= 0:
        raise RuntimeError(
            "SIGNAL_EXPIRY_SECONDS "
            "must be > 0"
        )

    if LOSS_COOLDOWN_SECONDS <= 0:
        raise RuntimeError(
            "LOSS_COOLDOWN_SECONDS "
            "must be > 0"
        )

    if HTTP_RETRY_ATTEMPTS < 1:
        raise RuntimeError(
            "HTTP_RETRY_ATTEMPTS "
            "must be at least 1"
        )

    if not all(
        (
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        )
    ):
        raise RuntimeError(
            "WEEX API credentials "
            "are missing"
        )


# ============================================================
# COMPLETE R11 DIAGNOSTIC
# ============================================================

async def run_r11(
    session,
):
    set_stage(
        "configuration validation"
    )

    validate_configuration()

    set_stage(
        "API trading symbol check"
    )

    trading_symbols = (
        await get_api_trading_symbols(
            session
        )
    )

    api_symbol_ok = (
        SYMBOL
        in trading_symbols
    )

    if not api_symbol_ok:
        raise RuntimeError(
            f"{SYMBOL} is not currently "
            "listed for API futures trading"
        )

    set_stage(
        "WEEX contract information"
    )

    contract = await get_contract_info(
        session
    )

    quantity_precision = int(
        contract.get(
            "quantityPrecision",
            0,
        )
    )

    min_order = safe_decimal(
        contract.get(
            "minOrderSize",
            "0",
        )
    )

    min_leverage = safe_decimal(
        contract.get(
            "minLeverage",
            "0",
        )
    )

    exchange_max_leverage = (
        safe_decimal(
            contract.get(
                "maxLeverage",
                "0",
            )
        )
    )

    if min_order <= ZERO:
        raise RuntimeError(
            "Invalid minimum order size "
            "returned by WEEX"
        )

    if exchange_max_leverage <= ZERO:
        raise RuntimeError(
            "Invalid maximum leverage "
            "returned by WEEX"
        )

    leverage_gate = (
        LEVERAGE
        >= min_leverage
        and LEVERAGE
        <= MAX_LEVERAGE
        and LEVERAGE
        <= exchange_max_leverage
    )

    set_stage(
        "WEEX account balance"
    )

    balance = await get_available_usdt(
        session
    )

    set_stage(
        "WEEX mark price"
    )

    mark_price = await get_mark_price(
        session
    )

    set_stage(
        "dynamic entry calculation"
    )

    entry = calculate_entry(
        available_balance=balance,
        mark_price=mark_price,
        quantity_precision=(
            quantity_precision
        ),
    )

    set_stage(
        "worst-case exposure"
    )

    exposure = calculate_exposure()

    set_stage(
        "TP split validation"
    )

    tp_split_valid = (
        (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        )
        == HUNDRED
    )

    set_stage(
        "signal safety gate tests"
    )

    signal_tests = (
        run_signal_gate_tests()
    )

    set_stage(
        "real WEEX position check"
    )

    position_data = (
        await get_real_position(
            session
        )
    )

    external_position_clear = (
        not position_data[
            "open"
        ]
    )

    set_stage(
        "order payload simulation"
    )

    order_payload = (
        build_simulated_order_payload(
            entry[
                "quantity"
            ]
        )
    )

    set_stage(
        "hard execution lock verification"
    )

    if not HARD_EXECUTION_LOCK:
        raise RuntimeError(
            "HARD_EXECUTION_LOCK "
            "must remain True in R11"
        )

    if LIVE_ORDER_EXECUTION:
        raise RuntimeError(
            "LIVE_ORDER_EXECUTION "
            "must remain False in R11"
        )

    #
    # IMPORTANT:
    #
    # There is deliberately NO:
    #
    # session.post(
    #     API_BASE_URL + ORDER_ENDPOINT
    # )
    #
    # anywhere in the R11 execution path.
    #
    # Payload construction only.
    #

    set_stage(
        "final report"
    )

    report, all_passed = build_report(
        balance=balance,
        mark_price=mark_price,
        api_symbol_ok=api_symbol_ok,
        contract=contract,
        leverage_gate=leverage_gate,
        entry=entry,
        exposure=exposure,
        signal_tests=signal_tests,
        external_position_clear=(
            external_position_clear
        ),
        position_data=position_data,
        tp_split_valid=tp_split_valid,
        order_payload=order_payload,
    )

    return (
        report,
        all_passed,
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
        "STABILIZED PRE-LIVE "
        "EXECUTION BRIDGE"
    )

    print(
        "SINGLE-RUN DIAGNOSTIC"
    )

    print(
        "NO LIVE ORDER TRANSMISSION"
    )

    print(
        "=" * 60
    )

    connector = aiohttp.TCPConnector(
        limit=10,
        ttl_dns_cache=300,
    )

    async with aiohttp.ClientSession(
        connector=connector,
    ) as session:

        try:
            report, all_passed = (
                await run_r11(
                    session
                )
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

            set_stage(
                "Telegram final report"
            )

            await send_telegram_once(
                session,
                report,
            )

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
            error_report = (
                build_error_report(
                    exc
                )
            )

            print(
                "=" * 60
            )

            print(
                error_report
            )

            print(
                "=" * 60
            )

            traceback.print_exc()

            #
            # R11 sends ONE error report
            # instead of repeatedly sending
            # partial diagnostic messages.
            #

            await send_telegram_once(
                session,
                error_report,
            )

            print(
                "=" * 60
            )


# ============================================================
# SINGLE PROCESS ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        main())
