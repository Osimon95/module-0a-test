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

MODULE_NAME = "0F-4H-R9"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


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

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TP / TRAILING
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
# PROTECTION
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

ONE_DIRECTION_ONLY = (
    os.getenv(
        "ONE_DIRECTION_ONLY",
        "true",
    ).strip().lower()
    == "true"
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


# ============================================================
# R9 TEST SIGNAL
# ============================================================

R9_SIGNAL_SIDE = os.getenv(
    "R9_SIGNAL_SIDE",
    "LONG",
).strip().upper()


# ============================================================
# ABSOLUTE EXECUTION LOCK
# ============================================================
#
# DO NOT convert these to environment variables in R9.
#
# There is also NO WEEX order-post function anywhere in R9.
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

telegram_attempted = False


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


# ============================================================
# HELPERS
# ============================================================

def dec(value, default="0"):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def fmt(value):
    if value is None:
        return "N/A"

    if isinstance(value, Decimal):
        text = format(
            value,
            "f",
        )
    else:
        text = str(value)

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def yes_no(value):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def floor_quantity(
    value,
    precision,
):
    quantum = Decimal("1").scaleb(
        -int(precision)
    )

    return value.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def get_order_side(
    position_side,
):
    if position_side == "LONG":
        return (
            "BUY",
            "LONG",
        )

    if position_side == "SHORT":
        return (
            "SELL",
            "SHORT",
        )

    raise ValueError(
        "R9_SIGNAL_SIDE must be LONG or SHORT"
    )


def make_client_order_id(
    signal_id,
):
    digest = hashlib.sha256(
        signal_id.encode()
    ).hexdigest()[:18]

    return f"r9-{digest}"


# ============================================================
# WEEX SIGNING
# ============================================================

def make_signature(
    timestamp,
    method,
    path,
    query="",
    body="",
):
    message = (
        str(timestamp)
        + method.upper()
        + path
        + query
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


def auth_headers(
    method,
    path,
    query="",
    body="",
):
    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            make_signature(
                timestamp,
                method,
                path,
                query,
                body,
            ),

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",
    }


# ============================================================
# HTTP
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    params = params or {}

    query = (
        "?"
        + urlencode(params)
        if params
        else ""
    )

    url = (
        API_BASE_URL
        + path
        + query
    )

    async with session.get(
        url,
        timeout=15,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                "WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text[:500]}"
            )

        return json.loads(text)


async def private_get(
    session,
    path,
    params=None,
):
    params = params or {}

    query = (
        "?"
        + urlencode(params)
        if params
        else ""
    )

    url = (
        API_BASE_URL
        + path
        + query
    )

    headers = auth_headers(
        "GET",
        path,
        query,
    )

    async with session.get(
        url,
        headers=headers,
        timeout=15,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                "WEEX PRIVATE HTTP "
                f"{response.status}: "
                f"{text[:500]}"
            )

        return json.loads(text)


# ============================================================
# TELEGRAM
# ============================================================
#
# ONE Telegram attempt per running process.
#
# No startup message.
# No separate test message.
# No repeating diagnostic loop.
#
# ============================================================

async def send_telegram_once(
    session,
    message,
):
    global telegram_attempted

    if telegram_attempted:
        return

    telegram_attempted = True

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
            timeout=15,
        ) as response:

            text = await response.text()

            if response.status == 200:
                print(
                    "TELEGRAM MESSAGE SENT"
                )

            else:
                print(
                    "TELEGRAM HTTP "
                    f"{response.status}: "
                    f"{text[:300]}"
                )

    except Exception as exc:
        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )


# ============================================================
# SIGNAL / PROTECTION TESTS
# ============================================================

def run_signal_tests():
    now = time.time()

    # ------------------------------------
    # Fresh signal
    # ------------------------------------

    fresh_signal_time = now

    fresh_age = (
        now
        - fresh_signal_time
    )

    fresh_allowed = (
        fresh_age
        <= SIGNAL_EXPIRY_SECONDS
    )

    # ------------------------------------
    # Simulated expired signal
    # ------------------------------------

    expired_signal_time = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 1
    )

    expired_age = (
        now
        - expired_signal_time
    )

    expired_rejected = (
        expired_age
        > SIGNAL_EXPIRY_SECONDS
    )

    # ------------------------------------
    # Normal cooldown clear
    # ------------------------------------

    last_loss_time = None

    cooldown_clear = (
        last_loss_time is None
        or (
            now
            - last_loss_time
            >= LOSS_COOLDOWN_SECONDS
        )
    )

    # ------------------------------------
    # Simulated recent loss
    # ------------------------------------

    recent_loss_time = (
        now
        - max(
            1,
            LOSS_COOLDOWN_SECONDS // 2,
        )
    )

    recent_loss_blocked = (
        now
        - recent_loss_time
        < LOSS_COOLDOWN_SECONDS
    )

    # ------------------------------------
    # Duplicate signal protection
    # ------------------------------------

    signal_id = (
        f"{SYMBOL}:"
        f"{R9_SIGNAL_SIDE}:"
        f"{int(now)}"
    )

    processed_signals = set()

    first_signal_allowed = (
        signal_id
        not in processed_signals
    )

    if first_signal_allowed:
        processed_signals.add(
            signal_id
        )

    duplicate_rejected = (
        signal_id
        in processed_signals
    )

    return {
        "signal_id":
            signal_id,

        "fresh_allowed":
            fresh_allowed,

        "expired_rejected":
            expired_rejected,

        "cooldown_clear":
            cooldown_clear,

        "recent_loss_blocked":
            recent_loss_blocked,

        "duplicate_rejected":
            duplicate_rejected,
    }


# ============================================================
# R9 DIAGNOSTIC
# ============================================================

async def run_r9():

    credentials_ready = all(
        [
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        ]
    )

    if not credentials_ready:
        raise RuntimeError(
            "WEEX credentials are missing"
        )

    (
        order_side,
        position_side,
    ) = get_order_side(
        R9_SIGNAL_SIDE
    )

    async with aiohttp.ClientSession() as session:

        # ====================================================
        # FRESH CONTRACT DATA
        # ====================================================

        exchange_info = await public_get(
            session,
            "/capi/v3/market/exchangeInfo",
            {
                "symbol":
                    SYMBOL,
            },
        )

        symbols = exchange_info.get(
            "symbols",
            [],
        )

        contract = next(
            (
                item
                for item in symbols
                if item.get("symbol")
                == SYMBOL
            ),
            None,
        )

        if not contract:
            raise RuntimeError(
                f"{SYMBOL} not found "
                "in exchangeInfo"
            )

        quantity_precision = int(
            contract.get(
                "quantityPrecision",
                0,
            )
        )

        min_order = dec(
            contract.get(
                "minOrderSize"
            )
        )

        contract_value = dec(
            contract.get(
                "contractVal"
            )
        )

        weex_min_leverage = dec(
            contract.get(
                "minLeverage",
                1,
            )
        )

        weex_max_leverage = dec(
            contract.get(
                "maxLeverage"
            )
        )


        # ====================================================
        # API TRADING SYMBOL CHECK
        # ====================================================

        api_symbols = await public_get(
            session,
            "/capi/v3/market/apiTradingSymbols",
        )

        api_trading_allowed = (
            SYMBOL
            in api_symbols
        )


        # ====================================================
        # FRESH MARK PRICE
        # ====================================================

        price_data = await public_get(
            session,
            "/capi/v3/market/symbolPrice",
            {
                "symbol":
                    SYMBOL,

                "priceType":
                    "MARK",
            },
        )

        mark_price = dec(
            price_data.get(
                "price"
            )
        )

        if mark_price <= ZERO:
            raise RuntimeError(
                "Invalid WEEX mark price"
            )


        # ====================================================
        # FRESH ACCOUNT BALANCE
        # ====================================================

        balance_data = await private_get(
            session,
            "/capi/v3/account/balance",
        )

        usdt = next(
            (
                item
                for item
                in balance_data
                if item.get("asset")
                == "USDT"
            ),
            None,
        )

        if not usdt:
            raise RuntimeError(
                "USDT balance not found"
            )

        available_balance = dec(
            usdt.get(
                "availableBalance"
            )
        )


        # ====================================================
        # REAL WEEX POSITION
        # ====================================================

        position_data = await private_get(
            session,
            "/capi/v3/account/position/singlePosition",
            {
                "symbol":
                    SYMBOL,
            },
        )

        open_positions = [
            position
            for position
            in position_data
            if dec(
                position.get(
                    "size"
                )
            ) > ZERO
        ]

        real_position = (
            open_positions[0]
            if open_positions
            else None
        )

        if real_position:

            real_position_side = str(
                real_position.get(
                    "side",
                    "",
                )
            ).upper()

            real_position_size = dec(
                real_position.get(
                    "size"
                )
            )

            real_liq_price = dec(
                real_position.get(
                    "liquidatePrice"
                )
            )

        else:

            real_position_side = "NONE"

            real_position_size = ZERO

            real_liq_price = ZERO


        # ====================================================
        # ONE-DIRECTION GATE
        # ====================================================

        direction_gate = (
            not ONE_DIRECTION_ONLY
            or real_position is None
            or (
                real_position_side
                == R9_SIGNAL_SIDE
            )
        )


        # ====================================================
        # INITIAL ENTRY SAFETY
        # ====================================================
        #
        # R9 intentionally blocks a new INITIAL entry if any
        # existing/manual position is detected.
        #
        # Later modules can distinguish controlled pyramids.
        #
        # ====================================================

        external_position_clear = (
            real_position is None
        )


        # ====================================================
        # DYNAMIC ENTRY SIZE
        # ====================================================

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

        quantity = floor_quantity(
            raw_quantity,
            quantity_precision,
        )

        quantity_positive = (
            quantity
            > ZERO
        )

        minimum_passed = (
            quantity
            >= min_order
        )


        # ====================================================
        # WORST-CASE EXPOSURE
        # ====================================================

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


        # ====================================================
        # LEVERAGE GATE
        # ====================================================

        leverage_passed = (
            LEVERAGE
            > ZERO

            and LEVERAGE
            <= MAX_LEVERAGE

            and LEVERAGE
            >= weex_min_leverage

            and LEVERAGE
            <= weex_max_leverage
        )


        # ====================================================
        # TP SPLIT
        # ====================================================

        tp_total = (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        )

        tp_split_passed = (
            tp_total
            == HUNDRED
        )


        # ====================================================
        # SIGNAL SAFETY TESTS
        # ====================================================

        signal = run_signal_tests()

        signal_gate_passed = all(
            [
                signal[
                    "fresh_allowed"
                ],

                signal[
                    "expired_rejected"
                ],

                signal[
                    "cooldown_clear"
                ],

                signal[
                    "recent_loss_blocked"
                ],

                signal[
                    "duplicate_rejected"
                ],
            ]
        )


        # ====================================================
        # LIQUIDATION PLANNING
        # ====================================================

        planning_mmr = (
            PLANNING_MMR_PERCENT
            / HUNDRED
        )

        leverage_fraction = (
            ONE
            / LEVERAGE
        )

        if R9_SIGNAL_SIDE == "LONG":

            estimated_liq = (
                mark_price
                * (
                    ONE
                    - leverage_fraction
                    + planning_mmr
                )
            )

        else:

            estimated_liq = (
                mark_price
                * (
                    ONE
                    + leverage_fraction
                    - planning_mmr
                )
            )

        estimated_liq_distance = (
            abs(
                mark_price
                - estimated_liq
            )
            / mark_price
            * HUNDRED
        )

        liq_distance_passed = (
            estimated_liq_distance
            >= MIN_LIQ_DISTANCE_PERCENT
        )


        # ====================================================
        # UNIQUE CLIENT ORDER ID
        # ====================================================

        client_order_id = (
            make_client_order_id(
                signal[
                    "signal_id"
                ]
            )
        )


        # ====================================================
        # EXACT R9 ORDER PAYLOAD
        # ====================================================
        #
        # BUILT ONLY.
        #
        # NEVER POSTED.
        #
        # ====================================================

        order_payload = {
            "symbol":
                SYMBOL,

            "side":
                order_side,

            "positionSide":
                position_side,

            "type":
                "MARKET",

            "quantity":
                fmt(quantity),

            "newClientOrderId":
                client_order_id,
        }


        # ====================================================
        # EXECUTION LOCK VALIDATION
        # ====================================================

        safety_lock_passed = (
            HARD_EXECUTION_LOCK
            is True

            and LIVE_ORDER_EXECUTION
            is False
        )


        # ====================================================
        # FINAL CHECKS
        # ====================================================

        checks = {
            "credentials_ready":
                credentials_ready,

            "api_trading_allowed":
                api_trading_allowed,

            "quantity_positive":
                quantity_positive,

            "minimum_passed":
                minimum_passed,

            "exposure_passed":
                exposure_passed,

            "leverage_passed":
                leverage_passed,

            "tp_split_passed":
                tp_split_passed,

            "signal_gate_passed":
                signal_gate_passed,

            "direction_gate":
                direction_gate,

            "external_position_clear":
                external_position_clear,

            "liq_distance_passed":
                liq_distance_passed,

            "safety_lock_passed":
                safety_lock_passed,
        }

        all_passed = all(
            checks.values()
        )

        failed_checks = [
            name
            for name, passed
            in checks.items()
            if not passed
        ]


        # ====================================================
        # REPORT STATUS
        # ====================================================

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


        # ====================================================
        # SINGLE CONSOLIDATED REPORT
        # ====================================================

        lines = [

            (
                f"{status_icon} MODULE "
                f"{MODULE_NAME} "
                f"{status_text}"
            ),

            SYMBOL,

            "",

            (
                "Available USDT: "
                f"{fmt(available_balance)}"
            ),

            (
                "Mark Price: "
                f"{fmt(mark_price)} USDT"
            ),

            "",

            "FINAL EXECUTION GATE",

            (
                "API Trading Symbol: "
                f"{yes_no(api_trading_allowed)}"
            ),

            (
                "Fresh Signal Accepted: "
                f"{yes_no(signal['fresh_allowed'])}"
            ),

            (
                "Expired Signal Rejected: "
                f"{yes_no(signal['expired_rejected'])}"
            ),

            (
                "Loss Cooldown Test: "
                f"{yes_no(signal['recent_loss_blocked'])}"
            ),

            (
                "Duplicate Signal Rejected: "
                f"{yes_no(signal['duplicate_rejected'])}"
            ),

            (
                "One Direction Gate: "
                f"{yes_no(direction_gate)}"
            ),

            (
                "External Position Clear: "
                f"{yes_no(external_position_clear)}"
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
                f"{yes_no(leverage_passed)}"
            ),

            "",

            "DYNAMIC ENTRY",

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
                f"{yes_no(minimum_passed)}"
            ),

            "",

            "WORST-CASE EXPOSURE",

            (
                "Initial: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%"
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
                f"{fmt(total_exposure)}% / "
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
                f"{fmt(TP1_PERCENT)}% / "
                f"{fmt(TP2_PERCENT)}% / "
                f"{fmt(TP3_PERCENT)}%"
            ),

            (
                "TP Split = 100%: "
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

        ]


        # ====================================================
        # REAL POSITION REPORT
        # ====================================================

        if real_position is None:

            lines.append(
                "No open position detected"
            )

            lines.append(
                "WEEX Liquidation Price: N/A"
            )

        else:

            lines.append(
                (
                    "Open Position: "
                    f"{real_position_side}"
                )
            )

            lines.append(
                (
                    "Position Size: "
                    f"{fmt(real_position_size)}"
                )
            )

            if real_liq_price > ZERO:

                lines.append(
                    (
                        "WEEX Liquidation Price: "
                        f"{fmt(real_liq_price)}"
                    )
                )

            else:

                lines.append(
                    "WEEX Liquidation Price: N/A"
                )


        # ====================================================
        # LIQUIDATION PLANNING REPORT
        # ====================================================

        lines.extend(
            [

                "",

                "R9 LIQUIDATION PLANNING ONLY",

                (
                    "Estimated "
                    f"{R9_SIGNAL_SIDE.title()} "
                    "Liq: "
                    f"{fmt(estimated_liq)}"
                ),

                (
                    "Estimated Liq Distance: "
                    f"{fmt(estimated_liq_distance)}%"
                ),

                (
                    "Min Distance Passed: "
                    f"{yes_no(liq_distance_passed)}"
                ),

                (
                    "Actual WEEX liquidation price "
                    "remains authoritative."
                ),

                "",

                "R9 EXACT ORDER PAYLOAD SIMULATION",

                "Endpoint: POST /capi/v3/order",

                (
                    "Symbol: "
                    f"{order_payload['symbol']}"
                ),

                (
                    "Side: "
                    f"{order_payload['side']} / "
                    f"{order_payload['positionSide']}"
                ),

                (
                    "Type: "
                    f"{order_payload['type']}"
                ),

                (
                    "Quantity: "
                    f"{order_payload['quantity']}"
                ),

                (
                    "newClientOrderId: "
                    f"{order_payload['newClientOrderId']}"
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
        )


        # ====================================================
        # FAILED CHECKS
        # ====================================================

        if failed_checks:

            lines.extend(
                [
                    "",
                    "FAILED CHECKS",
                ]
            )

            for check in failed_checks:

                lines.append(
                    f"❌ {check}"
                )


        # ====================================================
        # OUTPUT
        # ====================================================

        report = "\n".join(
            lines
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

        print(
            "SIMULATED PAYLOAD JSON"
        )

        print(
            json.dumps(
                order_payload,
                indent=2,
            )
        )

        print(
            "=" * 60
        )


        # ====================================================
        # ONLY TELEGRAM MESSAGE THIS RUN
        # ====================================================

        await send_telegram_once(
            session,
            report,
        )

        return all_passed


# ============================================================
# MAIN
# ============================================================

async def main():

    try:

        await run_r9()

    except Exception as exc:

        error_report = (
            f"❌ MODULE {MODULE_NAME} ERROR\n"
            f"{SYMBOL}\n\n"
            f"{type(exc).__name__}: {exc}\n\n"
            "🛡 Hard execution lock active\n"
            "⚠️ Live order execution disabled\n"
            "⚠️ NO LIVE ORDER WAS SENT"
        )

        print(
            error_report
        )

        async with aiohttp.ClientSession() as session:

            await send_telegram_once(
                session,
                error_report,
            )


    # ========================================================
    # KEEP PROCESS ALIVE
    # ========================================================
    #
    # Diagnostic does NOT repeat.
    # Telegram does NOT repeat.
    #
    # ========================================================

    print(
        "R9 diagnostic complete."
    )

    print(
        "Process remains alive."
    )

    print(
        "No repeat diagnostic cycle."
    )

    await asyncio.Event().wait()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
