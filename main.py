import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R8"
API_BASE_URL = "https://api-contract.weex.com"


# ============================================================
# ADJUSTABLE CONFIGURATION
# Change later with Render environment variables.
# ============================================================

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()
MARGIN_ASSET = os.getenv("MARGIN_ASSET", "USDT").strip().upper()

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

MAX_PYRAMIDS = int(
    os.getenv(
        "MAX_PYRAMIDS",
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

PLANNING_MMR_PERCENT = Decimal(
    os.getenv(
        "PLANNING_MMR_PERCENT",
        "0.5",
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

ONE_DIRECTION_ONLY = (
    os.getenv(
        "ONE_DIRECTION_ONLY",
        "true",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# SAFETY LOCKS
# ============================================================

# R8 is diagnostic/simulation only.
#
# There is deliberately NO live order POST function
# anywhere in this file.
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

SEND_TELEGRAM = (
    os.getenv(
        "SEND_TELEGRAM",
        "true",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# RENDER KEEP-ALIVE
# ============================================================
#
# Prevents the Python process from finishing immediately
# after the diagnostic.
#
# This helps prevent:
#
# diagnostic
# -> Python exits
# -> Render restarts
# -> Telegram sent again
# -> Python exits
# -> repeated Telegram messages
#
# ============================================================

KEEP_ALIVE = (
    os.getenv(
        "KEEP_ALIVE",
        "true",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

KEEP_ALIVE_SECONDS = max(
    30,
    int(
        os.getenv(
            "KEEP_ALIVE_SECONDS",
            "300",
        )
    ),
)

HTTP_TIMEOUT_SECONDS = max(
    5,
    int(
        os.getenv(
            "HTTP_TIMEOUT_SECONDS",
            "15",
        )
    ),
)


# ============================================================
# DECIMAL HELPERS
# ============================================================

D0 = Decimal("0")
D100 = Decimal("100")


def dec(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        if isinstance(value, bool):
            return Decimal(default)

        return Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal(default)


def fmt(value, places=None):
    value = dec(value)

    if places is not None:
        quantum = Decimal("1").scaleb(
            -places
        )

        value = value.quantize(
            quantum,
            rounding=ROUND_DOWN,
        )

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def floor_decimal(
    value,
    precision,
):
    quantum = Decimal("1").scaleb(
        -int(precision)
    )

    return dec(value).quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def percent_amount(
    balance,
    percent,
):
    return (
        balance
        * percent
        / D100
    )


def yn(value):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


# ============================================================
# WEEX AUTH
# ============================================================


def credentials_ready():
    return all(
        (
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        )
    )


def sign_request(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):
    request_path = path

    if query_string:
        request_path += (
            "?"
            + query_string
        )

    message = (
        f"{timestamp}"
        f"{method.upper()}"
        f"{request_path}"
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


# ============================================================
# HTTP ENGINE
# ============================================================


async def request_json(
    session,
    method,
    path,
    params=None,
    private=False,
):
    params = params or {}

    query_string = urlencode(
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

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "locale": "en-US",
        "User-Agent": (
            f"{MODULE_NAME}/1.0"
        ),
    }

    if private:
        if not credentials_ready():
            raise RuntimeError(
                "WEEX credentials are missing"
            )

        timestamp = str(
            int(
                time.time()
                * 1000
            )
        )

        signature = sign_request(
            timestamp,
            method,
            path,
            query_string,
            "",
        )

        headers.update(
            {
                "ACCESS-KEY":
                    WEEX_API_KEY,

                "ACCESS-SIGN":
                    signature,

                "ACCESS-PASSPHRASE":
                    WEEX_API_PASSPHRASE,

                "ACCESS-TIMESTAMP":
                    timestamp,
            }
        )

    async with session.request(
        method,
        url,
        headers=headers,
    ) as response:

        text = await response.text()

        if (
            response.status < 200
            or response.status >= 300
        ):
            raise RuntimeError(
                f"WEEX HTTP "
                f"{response.status} "
                f"{path}: "
                f"{text[:500]}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"WEEX returned "
                f"non-JSON data "
                f"from {path}: "
                f"{text[:500]}"
            ) from exc


async def public_get(
    session,
    path,
    params=None,
):
    return await request_json(
        session,
        "GET",
        path,
        params,
        private=False,
    )


async def private_get(
    session,
    path,
    params=None,
):
    return await request_json(
        session,
        "GET",
        path,
        params,
        private=True,
    )


# ============================================================
# WEEX CONTRACT
# ============================================================


async def get_contract(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL,
        },
    )

    symbols = (
        data.get(
            "symbols",
            [],
        )
        if isinstance(
            data,
            dict,
        )
        else []
    )

    for item in symbols:

        item_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if item_symbol == SYMBOL:
            return item

    raise RuntimeError(
        f"{SYMBOL} "
        "not found in "
        "WEEX exchangeInfo"
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

    price = dec(
        data.get(
            "price"
        )
        if isinstance(
            data,
            dict,
        )
        else None
    )

    if price <= 0:
        raise RuntimeError(
            "Invalid WEEX "
            "mark price response: "
            f"{data}"
        )

    return price


# ============================================================
# ACCOUNT BALANCE
# ============================================================


async def get_available_balance(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    rows = (
        data
        if isinstance(
            data,
            list,
        )
        else [data]
    )

    for item in rows:

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

        if asset == MARGIN_ASSET:

            available = dec(
                item.get(
                    "availableBalance"
                )
            )

            return (
                available,
                item,
            )

    raise RuntimeError(
        f"{MARGIN_ASSET} "
        "balance not found"
    )


# ============================================================
# CURRENT POSITION
# ============================================================


async def get_positions(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/"
        "position/singlePosition",
        {
            "symbol": SYMBOL,
        },
    )

    if data is None:
        return []

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
        wrapped = data.get(
            "data"
        )

        if isinstance(
            wrapped,
            list,
        ):
            return [
                item
                for item in wrapped
                if isinstance(
                    item,
                    dict,
                )
            ]

        return [data]

    return []


# ============================================================
# TELEGRAM
# ============================================================


async def send_telegram(
    session,
    message,
):
    if not SEND_TELEGRAM:
        print(
            "TELEGRAM: "
            "DISABLED BY "
            "SEND_TELEGRAM"
        )
        return False

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM: TOKEN "
            "OR CHAT ID MISSING"
        )
        return False

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
        ) as response:

            text = (
                await response.text()
            )

            if (
                200
                <= response.status
                < 300
            ):
                print(
                    "TELEGRAM MESSAGE SENT"
                )

                return True

            print(
                f"TELEGRAM ERROR "
                f"{response.status}: "
                f"{text[:500]}"
            )

            return False

    except Exception as exc:

        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return False


# ============================================================
# STATIC CONFIG VALIDATION
# ============================================================


def validate_static_config():

    checks = {
        "entry_percent_positive":
            INITIAL_ENTRY_PERCENT > 0,

        "leverage_positive":
            LEVERAGE > 0,

        "configured_leverage_cap":
            LEVERAGE
            <= MAX_LEVERAGE,

        "max_pyramids_valid":
            MAX_PYRAMIDS >= 0,

        "max_backups_valid":
            MAX_BACKUPS >= 0,

        "pyramid_size_nonnegative":
            PYRAMID_SIZE_PERCENT >= 0,

        "backup_size_nonnegative":
            BACKUP_SIZE_PERCENT >= 0,

        "max_exposure_valid":
            (
                D0
                < MAX_FUND_EXPOSURE_PERCENT
                <= D100
            ),

        "tp_split_equals_100":
            (
                TP1_PERCENT
                + TP2_PERCENT
                + TP3_PERCENT
                == D100
            ),

        "tp1_trigger_positive":
            TP1_TRIGGER_PERCENT > 0,

        "tp2_after_tp1":
            (
                TP2_TRIGGER_PERCENT
                > TP1_TRIGGER_PERCENT
            ),

        "trailing_positive":
            (
                TRAILING_DISTANCE_PERCENT
                > 0
            ),

        "signal_expiry_positive":
            SIGNAL_EXPIRY_SECONDS > 0,

        "cooldown_nonnegative":
            LOSS_COOLDOWN_SECONDS >= 0,

        "hard_execution_lock":
            HARD_EXECUTION_LOCK,

        "live_execution_disabled":
            not LIVE_ORDER_EXECUTION,
    }

    return checks


# ============================================================
# POSITION HELPERS
# ============================================================


def active_position_summary(
    positions,
):
    active = []

    for position in positions:

        size = dec(
            position.get(
                "size"
            )
        )

        if size > 0:
            active.append(
                position
            )

    return active


# ============================================================
# ORDER PAYLOAD SIMULATION
# ============================================================


def build_order_payload_simulation(
    quantity,
):
    # SIMULATION ONLY.
    #
    # This dictionary is never
    # transmitted to WEEX.

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
            fmt(quantity),

        "newClientOrderId":
            (
                f"r8sim-"
                f"{int(time.time())}"
            )[:36],
    }


# ============================================================
# PLANNING LIQUIDATION ESTIMATE
# ============================================================


def approximate_liquidation(
    entry_price,
    leverage,
    mmr_percent,
    side="LONG",
):
    # Planning estimate only.
    #
    # WEEX's real liquidation
    # price remains authoritative.

    if (
        entry_price <= 0
        or leverage <= 0
    ):
        return D0

    mmr = (
        mmr_percent
        / D100
    )

    inverse_leverage = (
        Decimal("1")
        / leverage
    )

    if side.upper() == "SHORT":

        result = (
            entry_price
            * (
                Decimal("1")
                + inverse_leverage
                - mmr
            )
        )

    else:

        result = (
            entry_price
            * (
                Decimal("1")
                - inverse_leverage
                + mmr
            )
        )

    return max(
        D0,
        result,
    )


# ============================================================
# R8 DIAGNOSTIC
# ============================================================


async def run_diagnostic():

    print(
        "=" * 64
    )

    print(
        f"MODULE "
        f"{MODULE_NAME} "
        "STARTING"
    )

    print(
        f"{SYMBOL} "
        "ADJUSTABLE WEEX "
        "READINESS + "
        "R8 SIMULATION"
    )

    print(
        "=" * 64
    )

    print(
        "Entry: "
        f"{fmt(INITIAL_ENTRY_PERCENT)}%"
    )

    print(
        "Leverage: "
        f"{fmt(LEVERAGE)}x"
    )

    print(
        "Max configured leverage: "
        f"{fmt(MAX_LEVERAGE)}x"
    )

    print(
        "Max pyramids: "
        f"{MAX_PYRAMIDS}"
    )

    print(
        "Pyramid size: "
        f"{fmt(PYRAMID_SIZE_PERCENT)}%"
    )

    print(
        "Max backups: "
        f"{MAX_BACKUPS}"
    )

    print(
        "Backup size: "
        f"{fmt(BACKUP_SIZE_PERCENT)}% "
        "each"
    )

    print(
        "Max fund exposure: "
        f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    print(
        "LIVE ORDER EXECUTION: "
        "DISABLED"
    )

    print(
        "HARD EXECUTION LOCK: "
        "ACTIVE"
    )

    print(
        "=" * 64
    )

    static_checks = (
        validate_static_config()
    )

    timeout = aiohttp.ClientTimeout(
        total=HTTP_TIMEOUT_SECONDS
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:

            # ================================================
            # CREDENTIAL CHECK
            # ================================================

            if not credentials_ready():

                raise RuntimeError(
                    "WEEX_API_KEY / "
                    "WEEX_API_SECRET / "
                    "WEEX_API_PASSPHRASE "
                    "missing"
                )


            # ================================================
            # WEEX READ-ONLY DATA
            # ================================================

            contract = await get_contract(
                session
            )

            mark_price = (
                await get_mark_price(
                    session
                )
            )

            (
                balance,
                _balance_row,
            ) = await get_available_balance(
                session
            )

            positions = await get_positions(
                session
            )


            # ================================================
            # CONTRACT DETAILS
            # ================================================

            min_order = dec(
                contract.get(
                    "minOrderSize"
                )
            )

            qty_precision = int(
                contract.get(
                    "quantityPrecision",
                    6,
                )
            )

            contract_value = dec(
                contract.get(
                    "contractVal"
                )
            )

            weex_max_leverage = dec(
                contract.get(
                    "maxLeverage"
                )
            )


            # ================================================
            # ENTRY SIZING
            # ================================================

            entry_margin = (
                percent_amount(
                    balance,
                    INITIAL_ENTRY_PERCENT,
                )
            )

            entry_notional = (
                entry_margin
                * LEVERAGE
            )

            if mark_price > 0:

                raw_quantity = (
                    entry_notional
                    / mark_price
                )

            else:

                raw_quantity = D0

            quantity = floor_decimal(
                raw_quantity,
                qty_precision,
            )


            # ================================================
            # EXPOSURE PLAN
            # ================================================

            initial_exposure = (
                INITIAL_ENTRY_PERCENT
            )

            pyramid_exposure = (
                PYRAMID_SIZE_PERCENT
                * Decimal(
                    MAX_PYRAMIDS
                )
            )

            backup_exposure = (
                BACKUP_SIZE_PERCENT
                * Decimal(
                    MAX_BACKUPS
                )
            )

            total_planned_exposure = (
                initial_exposure
                + pyramid_exposure
                + backup_exposure
            )


            # ================================================
            # LIVE VALIDATION
            # ================================================

            static_checks.update(
                {
                    "symbol_valid":
                        bool(contract),

                    "mark_price_positive":
                        mark_price > 0,

                    "balance_nonnegative":
                        balance >= 0,

                    "weex_leverage_allowed":
                        (
                            LEVERAGE
                            <= weex_max_leverage
                        ),

                    "quantity_positive":
                        quantity > 0,

                    "minimum_order_met":
                        quantity >= min_order,

                    "fund_exposure_within_cap":
                        (
                            total_planned_exposure
                            <= MAX_FUND_EXPOSURE_PERCENT
                        ),
                }
            )


            # ================================================
            # REAL POSITIONS
            # ================================================

            active_positions = (
                active_position_summary(
                    positions
                )
            )

            real_liq_prices = []

            for position in active_positions:

                liq = dec(
                    position.get(
                        "liquidatePrice"
                    )
                )

                if liq > 0:
                    real_liq_prices.append(
                        liq
                    )


            # ================================================
            # PLANNING LIQUIDATION
            # ================================================

            planning_liq = (
                approximate_liquidation(
                    mark_price,
                    LEVERAGE,
                    PLANNING_MMR_PERCENT,
                    "LONG",
                )
            )

            if (
                mark_price > 0
                and planning_liq > 0
            ):

                planning_liq_distance = (
                    (
                        mark_price
                        - planning_liq
                    )
                    / mark_price
                    * D100
                )

            else:

                planning_liq_distance = D0


            # ================================================
            # SIMULATED ORDER PAYLOAD
            # ================================================

            payload = (
                build_order_payload_simulation(
                    quantity
                )
            )


            # ================================================
            # RESULT
            # ================================================

            all_passed = all(
                static_checks.values()
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

            failed_checks = [
                name
                for name, passed
                in static_checks.items()
                if not passed
            ]


            # ================================================
            # SINGLE CONSOLIDATED TELEGRAM REPORT
            # ================================================

            report_lines = [

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
                    "Mark Price: "
                    f"{fmt(mark_price)} USDT"
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
                    f"{MAX_PYRAMIDS}"
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
                    f"{fmt(BACKUP_SIZE_PERCENT)}% "
                    "each"
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
                    f"{qty_precision}"
                ),

                (
                    "Contract Value: "
                    f"{fmt(contract_value)}"
                ),

                (
                    "WEEX Max Leverage: "
                    f"{fmt(weex_max_leverage)}x"
                ),

                "",

                "CURRENT ENTRY",

                (
                    "Margin: "
                    f"{fmt(entry_margin)} USDT"
                ),

                (
                    "Notional: "
                    f"{fmt(entry_notional)} USDT"
                ),

                (
                    "Quantity: "
                    f"{fmt(quantity)}"
                ),

                (
                    "Minimum Passed: "
                    f"{yn(
                        quantity >= min_order
                        and quantity > 0
                    )}"
                ),

                "",

                "WORST-CASE EXPOSURE",

                (
                    "Initial: "
                    f"{fmt(initial_exposure)}%"
                ),

                (
                    "Pyramids: "
                    f"{fmt(pyramid_exposure)}%"
                ),

                (
                    "Backups: "
                    f"{fmt(backup_exposure)}%"
                ),

                (
                    "Total: "
                    f"{fmt(total_planned_exposure)}% "
                    f"/ "
                    f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
                ),

                (
                    "Exposure Passed: "
                    f"{yn(
                        total_planned_exposure
                        <= MAX_FUND_EXPOSURE_PERCENT
                    )}"
                ),

                "",

                "TP / TRAILING",

                (
                    "TP1 / TP2 / TP3: "
                    f"{fmt(TP1_PERCENT)}% / "
                    f"{fmt(TP2_PERCENT)}% / "
                    f"{fmt(TP3_PERCENT)}%"
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

                "PROTECTION",

                (
                    "Signal Expiry: "
                    f"{SIGNAL_EXPIRY_SECONDS}s"
                ),

                (
                    "Loss Cooldown: "
                    f"{LOSS_COOLDOWN_SECONDS}s"
                ),

                (
                    "One Direction Only: "
                    + (
                        "ACTIVE"
                        if ONE_DIRECTION_ONLY
                        else "OFF"
                    )
                ),

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

                (
                    (
                        "Open position(s): "
                        f"{len(active_positions)}"
                    )
                    if active_positions
                    else
                    "No open position detected"
                ),

                (
                    (
                        "WEEX Liquidation Price: "
                        + ", ".join(
                            fmt(value)
                            for value
                            in real_liq_prices
                        )
                    )
                    if real_liq_prices
                    else
                    "WEEX Liquidation Price: N/A"
                ),

                "",

                "R8 PLANNING ONLY",

                (
                    "Estimated Long Liq: "
                    f"{fmt(planning_liq)}"
                ),

                (
                    "Estimated Liq Distance: "
                    f"{fmt(planning_liq_distance)}%"
                ),

                (
                    "Actual WEEX liquidation "
                    "price remains authoritative."
                ),

                "",

                "R8 ORDER PAYLOAD SIMULATION",

                (
                    "Symbol: "
                    f"{payload['symbol']}"
                ),

                (
                    "Side: "
                    f"{payload['side']} / "
                    f"{payload['positionSide']}"
                ),

                (
                    "Type: "
                    f"{payload['type']}"
                ),

                (
                    "Quantity: "
                    f"{payload['quantity']}"
                ),

                (
                    "Endpoint Target: "
                    "SIMULATION ONLY — NOT SENT"
                ),

                "",

                "🛡 Hard execution lock active",

                "⚠️ Live order execution disabled",

                "⚠️ NO LIVE ORDER WAS SENT",
            ]


            # ================================================
            # FAILED CHECKS
            # ================================================

            if failed_checks:

                report_lines.extend(
                    [
                        "",
                        "FAILED CHECKS",
                    ]
                )

                report_lines.extend(
                    [
                        f"❌ {name}"
                        for name
                        in failed_checks
                    ]
                )


            # ================================================
            # FINAL REPORT
            # ================================================

            report = "\n".join(
                report_lines
            )

            print(
                report
            )

            print(
                "=" * 64
            )


            # ================================================
            # ONLY ONE TELEGRAM CALL
            # ================================================

            await send_telegram(
                session,
                report,
            )

            return all_passed


        except Exception as exc:

            # ================================================
            # SINGLE ERROR REPORT
            # ================================================

            error_report = "\n".join(
                [
                    (
                        f"❌ MODULE "
                        f"{MODULE_NAME} "
                        "ERROR"
                    ),

                    SYMBOL,

                    "",

                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),

                    "",

                    "🛡 Hard execution lock active",

                    "⚠️ Live order execution disabled",

                    "⚠️ NO LIVE ORDER WAS SENT",
                ]
            )

            print(
                error_report
            )

            print(
                "=" * 64
            )


            # Only one Telegram call
            # on the error path.

            await send_telegram(
                session,
                error_report,
            )

            return False


# ============================================================
# KEEP RENDER PROCESS ALIVE
# ============================================================


async def keep_service_alive():

    if not KEEP_ALIVE:
        return

    print(
        "R8 KEEP-ALIVE ACTIVE"
    )

    print(
        "Process will remain running "
        "after the diagnostic."
    )

    print(
        "This prevents normal "
        "diagnostic completion from "
        "causing repeated startup "
        "Telegram messages."
    )

    print(
        "=" * 64
    )

    while True:

        await asyncio.sleep(
            KEEP_ALIVE_SECONDS
        )


# ============================================================
# MAIN
# ============================================================


async def main():

    await run_diagnostic()

    await keep_service_alive()


# ============================================================
# START
# ============================================================


if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "MODULE STOPPED"
        )
