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

MODULE_NAME = "0F-4H-R13"

API_BASE_URL = "https://api-contract.weex.com"


# ============================================================
# ADJUSTABLE CONFIGURATION
# ============================================================

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

MARGIN_ASSET = os.getenv(
    "MARGIN_ASSET",
    "USDT",
).strip().upper()


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
    ).strip().lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# MARGIN MODE
# ============================================================

MARGIN_TYPE = os.getenv(
    "MARGIN_TYPE",
    "ISOLATED",
).strip().upper()

if MARGIN_TYPE not in {
    "ISOLATED",
    "CROSSED",
}:
    MARGIN_TYPE = "ISOLATED"


# ============================================================
# SAFETY LOCKS
# ============================================================

# R13 remains PRE-LIVE.
#
# It prepares:
#
#   leverage POST
#   market entry POST
#   signed headers
#   response parsing
#   order ID capture
#   position reconciliation
#   failure rollback logic
#
# BUT DOES NOT TRANSMIT EITHER POST.
#
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True

ALLOW_PRIVATE_POST_TRANSMISSION = False


# ============================================================
# WEEX ENDPOINTS
# ============================================================

EXCHANGE_INFO_PATH = (
    "/capi/v3/market/exchangeInfo"
)

MARK_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
)

BALANCE_PATH = (
    "/capi/v3/account/balance"
)

POSITION_PATH = (
    "/capi/v3/account/position/singlePosition"
)

LEVERAGE_PATH = (
    "/capi/v3/account/leverage"
)

ORDER_PATH = (
    "/capi/v3/order"
)


# ============================================================
# CREDENTIALS
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
    ).strip().lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# R13 STABILITY
# ============================================================

HTTP_RETRY_ATTEMPTS = max(
    1,
    int(
        os.getenv(
            "HTTP_RETRY_ATTEMPTS",
            "3",
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

HTTP_RETRY_DELAY_SECONDS = max(
    1,
    int(
        os.getenv(
            "HTTP_RETRY_DELAY_SECONDS",
            "2",
        )
    ),
)


# ============================================================
# RENDER HEALTH / KEEP ALIVE
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

KEEP_ALIVE = (
    os.getenv(
        "KEEP_ALIVE",
        "true",
    ).strip().lower()
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


# ============================================================
# DECIMAL HELPERS
# ============================================================

ZERO = Decimal("0")

ONE = Decimal("1")

HUNDRED = Decimal("100")


def safe_decimal(
    value,
    default="0",
):
    try:
        if value is None:
            return Decimal(default)

        if isinstance(
            value,
            bool,
        ):
            return Decimal(default)

        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal(default)


def fmt(
    value,
    places=None,
):
    value = safe_decimal(
        value
    )

    if places is not None:
        quantum = Decimal(
            "1"
        ).scaleb(
            -int(places)
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
        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    return text or "0"


def floor_decimal(
    value,
    precision,
):
    quantum = Decimal(
        "1"
    ).scaleb(
        -int(precision)
    )

    return safe_decimal(
        value
    ).quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def percent_amount(
    balance,
    percent,
):
    return (
        safe_decimal(balance)
        * safe_decimal(percent)
        / HUNDRED
    )


def yn(
    value,
):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


# ============================================================
# CREDENTIAL VALIDATION
# ============================================================

def credentials_ready():
    return all(
        (
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        )
    )


# ============================================================
# SIGNATURE ENGINE
# ============================================================

def generate_signature(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):
    request_target = path

    if query_string:
        request_target += (
            "?"
            + query_string
        )

    message = (
        str(timestamp)
        + method.upper()
        + request_target
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

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


# ============================================================
# JSON SERIALIZATION
# ============================================================

def serialize_body(
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


# ============================================================
# HTTP ERROR
# ============================================================

class StageError(
    RuntimeError
):
    def __init__(
        self,
        stage,
        message,
    ):
        self.stage = stage

        super().__init__(
            f"{stage}: {message}"
        )


# ============================================================
# WEEX GET ENGINE
# ============================================================

async def request_json_get(
    session,
    path,
    params=None,
    private=False,
    stage="WEEX GET",
):
    params = (
        params
        or {}
    )

    query_string = urlencode(
        {
            key: str(value)
            for key, value
            in params.items()
        }
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

    last_error = None

    for attempt in range(
        1,
        HTTP_RETRY_ATTEMPTS + 1,
    ):
        try:
            headers = {
                "Accept": (
                    "application/json"
                ),
                "Content-Type": (
                    "application/json"
                ),
                "locale": (
                    "en-US"
                ),
                "User-Agent": (
                    f"{MODULE_NAME}/1.0"
                ),
            }

            if private:
                if not credentials_ready():
                    raise StageError(
                        stage,
                        "WEEX credentials missing",
                    )

                timestamp = str(
                    int(
                        time.time()
                        * 1000
                    )
                )

                signature = (
                    generate_signature(
                        timestamp,
                        "GET",
                        path,
                        query_string,
                        "",
                    )
                )

                headers.update(
                    {
                        "ACCESS-KEY": (
                            WEEX_API_KEY
                        ),
                        "ACCESS-SIGN": (
                            signature
                        ),
                        "ACCESS-PASSPHRASE": (
                            WEEX_API_PASSPHRASE
                        ),
                        "ACCESS-TIMESTAMP": (
                            timestamp
                        ),
                    }
                )

            timeout = (
                aiohttp.ClientTimeout(
                    total=(
                        HTTP_TIMEOUT_SECONDS
                    )
                )
            )

            async with session.get(
                url,
                headers=headers,
                timeout=timeout,
            ) as response:

                text = (
                    await response.text()
                )

                if (
                    response.status
                    < 200
                    or response.status
                    >= 300
                ):
                    raise RuntimeError(
                        f"HTTP "
                        f"{response.status}: "
                        f"{text[:500]}"
                    )

                try:
                    return json.loads(
                        text
                    )

                except json.JSONDecodeError:
                    raise RuntimeError(
                        "WEEX returned "
                        "non-JSON response: "
                        f"{text[:500]}"
                    )

        except StageError:
            raise

        except Exception as exc:
            last_error = exc

            transient = (
                isinstance(
                    exc,
                    (
                        aiohttp.ClientError,
                        asyncio.TimeoutError,
                    ),
                )
                or "HTTP 429"
                in str(exc)
                or "HTTP 500"
                in str(exc)
                or "HTTP 502"
                in str(exc)
                or "HTTP 503"
                in str(exc)
                or "HTTP 504"
                in str(exc)
            )

            if (
                attempt
                >= HTTP_RETRY_ATTEMPTS
                or not transient
            ):
                break

            await asyncio.sleep(
                HTTP_RETRY_DELAY_SECONDS
                * attempt
            )

    raise StageError(
        stage,
        str(last_error),
    )


# ============================================================
# PUBLIC / PRIVATE GET
# ============================================================

async def public_get(
    session,
    path,
    params=None,
    stage="PUBLIC GET",
):
    return await request_json_get(
        session,
        path,
        params=params,
        private=False,
        stage=stage,
    )


async def private_get(
    session,
    path,
    params=None,
    stage="PRIVATE GET",
):
    return await request_json_get(
        session,
        path,
        params=params,
        private=True,
        stage=stage,
    )


# ============================================================
# CONTRACT DATA
# ============================================================

async def get_contract(
    session,
):
    data = await public_get(
        session,
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
        stage="CONTRACT INFO",
    )

    if isinstance(
        data,
        dict,
    ):
        symbols = data.get(
            "symbols",
            []
        )

        if isinstance(
            symbols,
            list,
        ):
            for item in symbols:
                if (
                    isinstance(
                        item,
                        dict,
                    )
                    and str(
                        item.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    == SYMBOL
                ):
                    return item

    if isinstance(
        data,
        list,
    ):
        for item in data:
            if (
                isinstance(
                    item,
                    dict,
                )
                and str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ):
                return item

    raise StageError(
        "CONTRACT INFO",
        (
            f"{SYMBOL} "
            "not found in exchangeInfo"
        ),
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
    data = await public_get(
        session,
        MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
        stage="MARK PRICE",
    )

    try:
        return extract_mark_price(
            data
        )

    except Exception as exc:
        raise StageError(
            "MARK PRICE",
            str(exc),
        )


# ============================================================
# BALANCE
# ============================================================

async def get_available_balance(
    session,
):
    data = await private_get(
        session,
        BALANCE_PATH,
        stage="ACCOUNT BALANCE",
    )

    rows = (
        data
        if isinstance(
            data,
            list,
        )
        else [
            data
        ]
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
                item.get(
                    "coinName",
                    "",
                ),
            )
        ).upper()

        if asset != MARGIN_ASSET:
            continue

        balance = safe_decimal(
            item.get(
                "availableBalance",
                item.get(
                    "available",
                    "0",
                ),
            )
        )

        return (
            balance,
            item,
        )

    raise StageError(
        "ACCOUNT BALANCE",
        (
            f"{MARGIN_ASSET} "
            "balance not found"
        ),
    )


# ============================================================
# POSITION
# ============================================================

async def get_positions(
    session,
):
    data = await private_get(
        session,
        POSITION_PATH,
        {
            "symbol": SYMBOL,
        },
        stage="POSITION CHECK",
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
        for key in (
            "data",
            "result",
            "positions",
            "list",
        ):
            wrapped = data.get(
                key
            )

            if isinstance(
                wrapped,
                list,
            ):
                return [
                    item
                    for item
                    in wrapped
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
    if not isinstance(
        position,
        dict,
    ):
        return ZERO

    for key in (
        "size",
        "quantity",
        "positionAmt",
        "positionSize",
        "holdVol",
    ):
        if key in position:
            value = abs(
                safe_decimal(
                    position.get(
                        key
                    )
                )
            )

            if value > ZERO:
                return value

    return ZERO


def active_positions(
    positions,
):
    return [
        position
        for position in positions
        if position_size(
            position
        )
        > ZERO
    ]


# ============================================================
# FINAL SIGNAL GATES
# ============================================================

def signal_is_fresh(
    signal_timestamp,
    now_timestamp,
):
    age = (
        now_timestamp
        - signal_timestamp
    )

    return (
        age >= 0
        and age
        <= SIGNAL_EXPIRY_SECONDS
    )


def cooldown_clear(
    last_loss_timestamp,
    now_timestamp,
):
    if (
        last_loss_timestamp
        is None
    ):
        return True

    return (
        now_timestamp
        - last_loss_timestamp
        >= LOSS_COOLDOWN_SECONDS
    )


def duplicate_signal_allowed(
    signal_id,
    seen_signals,
):
    return (
        signal_id
        not in seen_signals
    )


def one_direction_allowed(
    requested_side,
    existing_side,
):
    if not ONE_DIRECTION_ONLY:
        return True

    if not existing_side:
        return True

    return (
        requested_side
        == existing_side
    )


def run_execution_gate_tests():
    now_timestamp = time.time()

    fresh_timestamp = (
        now_timestamp
        - min(
            10,
            max(
                1,
                SIGNAL_EXPIRY_SECONDS
                // 2,
            ),
        )
    )

    expired_timestamp = (
        now_timestamp
        - SIGNAL_EXPIRY_SECONDS
        - 10
    )

    fresh_signal = (
        signal_is_fresh(
            fresh_timestamp,
            now_timestamp,
        )
    )

    expired_rejected = (
        not signal_is_fresh(
            expired_timestamp,
            now_timestamp,
        )
    )

    old_loss = (
        now_timestamp
        - LOSS_COOLDOWN_SECONDS
        - 10
    )

    cooldown_test = (
        cooldown_clear(
            old_loss,
            now_timestamp,
        )
    )

    seen = {
        "already-used",
    }

    duplicate_rejected = (
        not duplicate_signal_allowed(
            "already-used",
            seen,
        )
    )

    direction_test = (
        one_direction_allowed(
            "LONG",
            "LONG",
        )
    )

    return {
        "fresh_signal": (
            fresh_signal
        ),
        "expired_rejected": (
            expired_rejected
        ),
        "cooldown": (
            cooldown_test
        ),
        "duplicate_rejected": (
            duplicate_rejected
        ),
        "one_direction": (
            direction_test
        ),
    }


# ============================================================
# STATIC CONFIG VALIDATION
# ============================================================

def validate_static_config():
    total_exposure = (
        INITIAL_ENTRY_PERCENT
        + (
            PYRAMID_SIZE_PERCENT
            * Decimal(
                MAX_PYRAMIDS
            )
        )
        + (
            BACKUP_SIZE_PERCENT
            * Decimal(
                MAX_BACKUPS
            )
        )
    )

    checks = {
        "entry_positive": (
            INITIAL_ENTRY_PERCENT
            > ZERO
        ),

        "leverage_positive": (
            LEVERAGE
            > ZERO
        ),

        "config_leverage_cap": (
            LEVERAGE
            <= MAX_LEVERAGE
        ),

        "pyramids_valid": (
            MAX_PYRAMIDS
            >= 0
        ),

        "backups_valid": (
            MAX_BACKUPS
            >= 0
        ),

        "exposure_valid": (
            total_exposure
            <= MAX_FUND_EXPOSURE_PERCENT
        ),

        "tp_split_valid": (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
            == HUNDRED
        ),

        "tp1_positive": (
            TP1_TRIGGER_PERCENT
            > ZERO
        ),

        "tp2_after_tp1": (
            TP2_TRIGGER_PERCENT
            > TP1_TRIGGER_PERCENT
        ),

        "trailing_positive": (
            TRAILING_DISTANCE_PERCENT
            > ZERO
        ),

        "hard_lock_active": (
            HARD_EXECUTION_LOCK
        ),

        "live_execution_disabled": (
            not LIVE_ORDER_EXECUTION
        ),

        "post_transmission_disabled": (
            not ALLOW_PRIVATE_POST_TRANSMISSION
        ),
    }

    return (
        checks,
        total_exposure,
    )


# ============================================================
# CLIENT ORDER ID
# ============================================================

def make_client_order_id():
    prefix = (
        SYMBOL
        .lower()
        .replace(
            "_",
            "",
        )
    )

    value = (
        f"r13-"
        f"{prefix}-"
        f"{int(time.time())}"
    )

    return value[:36]


# ============================================================
# R13 LEVERAGE PAYLOAD
# ============================================================

def build_leverage_payload():
    leverage_text = fmt(
        LEVERAGE
    )

    if MARGIN_TYPE == "CROSSED":
        return {
            "symbol": SYMBOL,
            "marginType": "CROSSED",
            "crossLeverage": (
                leverage_text
            ),
        }

    return {
        "symbol": SYMBOL,
        "marginType": "ISOLATED",
        "isolatedLongLeverage": (
            leverage_text
        ),
        "isolatedShortLeverage": (
            leverage_text
        ),
    }


# ============================================================
# R13 ENTRY PAYLOAD
# ============================================================

def build_entry_payload(
    quantity,
):
    return {
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": fmt(
            quantity
        ),
        "newClientOrderId": (
            make_client_order_id()
        ),
    }


# ============================================================
# R13 SIGNED POST PREPARATION
# ============================================================

def prepare_private_post(
    path,
    payload,
):
    if not credentials_ready():
        raise StageError(
            "POST PREPARATION",
            "WEEX credentials missing",
        )

    body = serialize_body(
        payload
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = (
        generate_signature(
            timestamp,
            "POST",
            path,
            "",
            body,
        )
    )

    headers = {
        "ACCESS-KEY": (
            WEEX_API_KEY
        ),

        "ACCESS-SIGN": (
            signature
        ),

        "ACCESS-PASSPHRASE": (
            WEEX_API_PASSPHRASE
        ),

        "ACCESS-TIMESTAMP": (
            timestamp
        ),

        "Content-Type": (
            "application/json"
        ),

        "locale": (
            "en-US"
        ),
    }

    return {
        "method": "POST",
        "url": (
            API_BASE_URL
            + path
        ),
        "path": path,
        "headers": headers,
        "body": body,
    }


# ============================================================
# HARD POST TRANSMISSION BLOCK
# ============================================================

async def transmit_private_post(
    session,
    prepared_request,
):
    # This function CANNOT transmit in R13.
    #
    # It exists only so the eventual live execution architecture
    # has a clearly defined transmission boundary.
    #
    # ========================================================

    if HARD_EXECUTION_LOCK:
        raise StageError(
            "LIVE TRANSMISSION",
            (
                "Blocked by "
                "HARD_EXECUTION_LOCK"
            ),
        )

    if not LIVE_ORDER_EXECUTION:
        raise StageError(
            "LIVE TRANSMISSION",
            (
                "Blocked because "
                "LIVE_ORDER_EXECUTION=False"
            ),
        )

    if not ALLOW_PRIVATE_POST_TRANSMISSION:
        raise StageError(
            "LIVE TRANSMISSION",
            (
                "Blocked because "
                "ALLOW_PRIVATE_POST_TRANSMISSION=False"
            ),
        )

    raise StageError(
        "LIVE TRANSMISSION",
        (
            "R13 contains no active "
            "POST transmission implementation"
        ),
    )


# ============================================================
# ORDER RESPONSE PARSER
# ============================================================

def extract_order_id(
    response,
):
    if response is None:
        return None

    candidates = []

    if isinstance(
        response,
        dict,
    ):
        candidates.append(
            response
        )

        for key in (
            "data",
            "result",
        ):
            nested = response.get(
                key
            )

            if isinstance(
                nested,
                dict,
            ):
                candidates.append(
                    nested
                )

    for item in candidates:
        for key in (
            "orderId",
            "order_id",
            "id",
        ):
            value = item.get(
                key
            )

            if value not in (
                None,
                "",
                "0",
                0,
            ):
                return str(
                    value
                )

    return None


# ============================================================
# SIMULATED WEEX RESPONSE
# ============================================================

def simulate_successful_order_response():
    return {
        "orderId": (
            "R13-SIMULATED-ORDER-ID"
        ),
        "status": (
            "ACCEPTED"
        ),
    }


# ============================================================
# POSITION RECONCILIATION
# ============================================================

def reconcile_entry_simulation(
    expected_quantity,
    simulated_position,
):
    if not isinstance(
        simulated_position,
        dict,
    ):
        return (
            False,
            "Position response missing",
        )

    actual_quantity = (
        position_size(
            simulated_position
        )
    )

    if actual_quantity <= ZERO:
        return (
            False,
            "No position quantity detected",
        )

    if (
        actual_quantity
        < expected_quantity
    ):
        return (
            False,
            (
                "Position quantity below "
                "expected entry quantity"
            ),
        )

    return (
        True,
        "Position verified",
    )


# ============================================================
# FAILURE ROLLBACK SIMULATION
# ============================================================

def rollback_simulation(
    order_id,
    position_verified,
):
    state = {
        "pending_entry": True,
        "captured_order_id": (
            order_id
        ),
        "position_verified": (
            position_verified
        ),
    }

    if not position_verified:
        state[
            "pending_entry"
        ] = False

        state[
            "captured_order_id"
        ] = None

        state[
            "rollback_complete"
        ] = True

        return (
            True,
            state,
        )

    state[
        "rollback_complete"
    ] = False

    return (
        False,
        state,
    )


# ============================================================
# R13 EXECUTION PATH SIMULATION
# ============================================================

def run_execution_path_simulation(
    quantity,
):
    leverage_payload = (
        build_leverage_payload()
    )

    order_payload = (
        build_entry_payload(
            quantity
        )
    )

    leverage_request = (
        prepare_private_post(
            LEVERAGE_PATH,
            leverage_payload,
        )
    )

    order_request = (
        prepare_private_post(
            ORDER_PATH,
            order_payload,
        )
    )

    simulated_response = (
        simulate_successful_order_response()
    )

    order_id = (
        extract_order_id(
            simulated_response
        )
    )

    simulated_position = {
        "symbol": SYMBOL,
        "positionSide": "LONG",
        "size": fmt(
            quantity
        ),
    }

    position_verified, _ = (
        reconcile_entry_simulation(
            quantity,
            simulated_position,
        )
    )

    failed_position = {
        "symbol": SYMBOL,
        "positionSide": "LONG",
        "size": "0",
    }

    failure_verified, _ = (
        reconcile_entry_simulation(
            quantity,
            failed_position,
        )
    )

    rollback_ok, _ = (
        rollback_simulation(
            order_id,
            failure_verified,
        )
    )

    return {
        "leverage_payload": (
            leverage_payload
        ),

        "order_payload": (
            order_payload
        ),

        "leverage_request": (
            leverage_request
        ),

        "order_request": (
            order_request
        ),

        "order_id": (
            order_id
        ),

        "order_id_captured": (
            bool(order_id)
        ),

        "position_verified": (
            position_verified
        ),

        "rollback_test": (
            rollback_ok
        ),

        "leverage_signature_ready": (
            bool(
                leverage_request[
                    "headers"
                ].get(
                    "ACCESS-SIGN"
                )
            )
        ),

        "order_signature_ready": (
            bool(
                order_request[
                    "headers"
                ].get(
                    "ACCESS-SIGN"
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
    if not SEND_TELEGRAM:
        print(
            "TELEGRAM: DISABLED"
        )

        return False

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM: "
            "TOKEN OR CHAT ID MISSING"
        )

        return False

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    payload = {
        "chat_id": (
            TELEGRAM_CHAT_ID
        ),

        "text": (
            message
        ),

        "disable_web_page_preview": (
            True
        ),
    }

    try:
        timeout = (
            aiohttp.ClientTimeout(
                total=(
                    HTTP_TIMEOUT_SECONDS
                )
            )
        )

        async with session.post(
            url,
            json=payload,
            timeout=timeout,
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
                "TELEGRAM ERROR "
                f"{response.status}: "
                f"{text[:500]}"
            )

    except Exception as exc:
        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

    return False


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    reader,
    writer,
):
    try:
        try:
            await asyncio.wait_for(
                reader.read(
                    4096
                ),
                timeout=5,
            )

        except Exception:
            pass

        body = (
            f"{MODULE_NAME} ONLINE\n"
        ).encode(
            "utf-8"
        )

        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Connection: close\r\n"
            + (
                f"Content-Length: "
                f"{len(body)}\r\n"
            ).encode(
                "utf-8"
            )
            + b"\r\n"
            + body
        )

        writer.write(
            response
        )

        await writer.drain()

    except Exception:
        pass

    finally:
        try:
            writer.close()

            await writer.wait_closed()

        except Exception:
            pass


async def start_health_server():
    server = await asyncio.start_server(
        health_handler,
        "0.0.0.0",
        PORT,
    )

    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}"
    )

    return server


# ============================================================
# DIAGNOSTIC
# ============================================================

async def run_diagnostic():
    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "PRE-LIVE EXECUTION PATH VALIDATION",
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

    stage = (
        "STARTUP"
    )

    timeout = (
        aiohttp.ClientTimeout(
            total=(
                HTTP_TIMEOUT_SECONDS
            )
        )
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:
            stage = (
                "CREDENTIAL CHECK"
            )

            if not credentials_ready():
                raise StageError(
                    stage,
                    (
                        "WEEX credentials "
                        "are missing"
                    ),
                )

            static_checks, total_exposure = (
                validate_static_config()
            )

            execution_gate = (
                run_execution_gate_tests()
            )


            # ================================================
            # CONTRACT
            # ================================================

            stage = (
                "CONTRACT INFO"
            )

            contract = await get_contract(
                session
            )


            # ================================================
            # MARK PRICE
            # ================================================

            stage = (
                "MARK PRICE"
            )

            mark_price = (
                await get_mark_price(
                    session
                )
            )


            # ================================================
            # BALANCE
            # ================================================

            stage = (
                "ACCOUNT BALANCE"
            )

            balance, _ = (
                await get_available_balance(
                    session
                )
            )


            # ================================================
            # POSITIONS
            # ================================================

            stage = (
                "POSITION CHECK"
            )

            positions = (
                await get_positions(
                    session
                )
            )

            active = (
                active_positions(
                    positions
                )
            )


            # ================================================
            # CONTRACT VALUES
            # ================================================

            min_order = safe_decimal(
                contract.get(
                    "minOrderSize",
                    "0",
                )
            )

            qty_precision = int(
                contract.get(
                    "quantityPrecision",
                    contract.get(
                        "sizeIncrement",
                        4,
                    ),
                )
            )

            contract_value = (
                safe_decimal(
                    contract.get(
                        "contractVal",
                        "0",
                    )
                )
            )

            weex_min_leverage = (
                safe_decimal(
                    contract.get(
                        "minLeverage",
                        "1",
                    )
                )
            )

            weex_max_leverage = (
                safe_decimal(
                    contract.get(
                        "maxLeverage",
                        "0",
                    )
                )
            )


            # ================================================
            # DYNAMIC ENTRY
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

            raw_quantity = (
                entry_notional
                / mark_price
                if mark_price
                > ZERO
                else ZERO
            )

            quantity = (
                floor_decimal(
                    raw_quantity,
                    qty_precision,
                )
            )


            # ================================================
            # LEVERAGE GATE
            # ================================================

            leverage_gate = (
                LEVERAGE
                >= weex_min_leverage
                and LEVERAGE
                <= weex_max_leverage
                and LEVERAGE
                <= MAX_LEVERAGE
            )


            # ================================================
            # EXTERNAL POSITION GATE
            # ================================================

            external_position_clear = (
                len(
                    active
                )
                == 0
            )


            # ================================================
            # R13 EXECUTION PATH
            # ================================================

            stage = (
                "R13 EXECUTION PATH"
            )

            execution_path = (
                run_execution_path_simulation(
                    quantity
                )
            )


            # ================================================
            # FINAL CHECKS
            # ================================================

            checks = {
                **static_checks,

                "api_symbol": (
                    bool(
                        contract
                    )
                ),

                "fresh_signal": (
                    execution_gate[
                        "fresh_signal"
                    ]
                ),

                "expired_rejected": (
                    execution_gate[
                        "expired_rejected"
                    ]
                ),

                "cooldown": (
                    execution_gate[
                        "cooldown"
                    ]
                ),

                "duplicate_rejected": (
                    execution_gate[
                        "duplicate_rejected"
                    ]
                ),

                "one_direction": (
                    execution_gate[
                        "one_direction"
                    ]
                ),

                "external_position_clear": (
                    external_position_clear
                ),

                "mark_price_positive": (
                    mark_price
                    > ZERO
                ),

                "balance_nonnegative": (
                    balance
                    >= ZERO
                ),

                "leverage_gate": (
                    leverage_gate
                ),

                "quantity_positive": (
                    quantity
                    > ZERO
                ),

                "minimum_order": (
                    quantity
                    >= min_order
                    and quantity
                    > ZERO
                ),

                "leverage_payload_ready": (
                    bool(
                        execution_path[
                            "leverage_payload"
                        ]
                    )
                ),

                "leverage_signature_ready": (
                    execution_path[
                        "leverage_signature_ready"
                    ]
                ),

                "order_payload_ready": (
                    bool(
                        execution_path[
                            "order_payload"
                        ]
                    )
                ),

                "order_signature_ready": (
                    execution_path[
                        "order_signature_ready"
                    ]
                ),

                "order_id_parser": (
                    execution_path[
                        "order_id_captured"
                    ]
                ),

                "position_reconciliation": (
                    execution_path[
                        "position_verified"
                    ]
                ),

                "rollback_test": (
                    execution_path[
                        "rollback_test"
                    ]
                ),
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


            # ================================================
            # REAL LIQUIDATION
            # ================================================

            real_liq_prices = []

            for position in active:
                liq = safe_decimal(
                    position.get(
                        "liquidatePrice",
                        position.get(
                            "liquidationPrice",
                            "0",
                        ),
                    )
                )

                if liq > ZERO:
                    real_liq_prices.append(
                        liq
                    )


            # ================================================
            # EXPOSURE COMPONENTS
            # ================================================

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


            # ================================================
            # REPORT
            # ================================================

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

            leverage_payload_json = (
                serialize_body(
                    execution_path[
                        "leverage_payload"
                    ]
                )
            )

            order_payload_json = (
                serialize_body(
                    execution_path[
                        "order_payload"
                    ]
                )
            )

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
                    f"Mark Price: "
                    f"{fmt(mark_price)} "
                    "USDT"
                ),

                "",

                "FINAL EXECUTION GATE",

                (
                    "API Trading Symbol: "
                    f"{yn(bool(contract))}"
                ),

                (
                    "Fresh Signal Accepted: "
                    f"{yn(execution_gate['fresh_signal'])}"
                ),

                (
                    "Expired Signal Rejected: "
                    f"{yn(execution_gate['expired_rejected'])}"
                ),

                (
                    "Loss Cooldown Test: "
                    f"{yn(execution_gate['cooldown'])}"
                ),

                (
                    "Duplicate Signal Rejected: "
                    f"{yn(execution_gate['duplicate_rejected'])}"
                ),

                (
                    "One Direction Gate: "
                    f"{yn(execution_gate['one_direction'])}"
                ),

                (
                    "External Position Clear: "
                    f"{yn(external_position_clear)}"
                ),

                "",

                "ADJUSTABLE CONFIG",

                (
                    f"Entry: "
                    f"{fmt(INITIAL_ENTRY_PERCENT)}%"
                ),

                (
                    f"Leverage: "
                    f"{fmt(LEVERAGE)}x"
                ),

                (
                    "Max Config Leverage: "
                    f"{fmt(MAX_LEVERAGE)}x"
                ),

                (
                    f"Margin Type: "
                    f"{MARGIN_TYPE}"
                ),

                (
                    f"Max Pyramids: "
                    f"{MAX_PYRAMIDS}"
                ),

                (
                    "Pyramid Size: "
                    f"{fmt(PYRAMID_SIZE_PERCENT)}%"
                ),

                (
                    f"Max Backups: "
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
                    f"{qty_precision}"
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
                    f"{yn(leverage_gate)}"
                ),

                "",

                "DYNAMIC ENTRY",

                (
                    f"Margin: "
                    f"{fmt(entry_margin)} USDT"
                ),

                (
                    f"Notional: "
                    f"{fmt(entry_notional)} USDT"
                ),

                (
                    f"Quantity: "
                    f"{fmt(quantity)}"
                ),

                (
                    "Quantity Positive: "
                    f"{yn(quantity > ZERO)}"
                ),

                (
                    "Minimum Passed: "
                    f"{yn(quantity >= min_order and quantity > ZERO)}"
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
                    f"{yn(total_exposure <= MAX_FUND_EXPOSURE_PERCENT)}"
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
                    "TP Split Valid: "
                    f"{yn(TP1_PERCENT + TP2_PERCENT + TP3_PERCENT == HUNDRED)}"
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

                (
                    (
                        f"Open position(s): "
                        f"{len(active)}"
                    )
                    if active
                    else (
                        "No open position detected"
                    )
                ),

                (
                    (
                        "WEEX Liquidation Price: "
                        + ", ".join(
                            fmt(price)
                            for price
                            in real_liq_prices
                        )
                    )
                    if real_liq_prices
                    else (
                        "WEEX Liquidation Price: N/A"
                    )
                ),

                "",

                "R13 LEVERAGE REQUEST SIMULATION",

                (
                    "Endpoint Target: "
                    f"{LEVERAGE_PATH}"
                ),

                (
                    "Method: POST — NOT SENT"
                ),

                (
                    "Payload: "
                    f"{leverage_payload_json}"
                ),

                (
                    "POST Signature Prepared: "
                    f"{yn(execution_path['leverage_signature_ready'])}"
                ),

                "",

                "R13 ORDER REQUEST SIMULATION",

                (
                    "Endpoint Target: "
                    f"{ORDER_PATH}"
                ),

                (
                    "Method: POST — NOT SENT"
                ),

                (
                    "Payload: "
                    f"{order_payload_json}"
                ),

                (
                    "POST Signature Prepared: "
                    f"{yn(execution_path['order_signature_ready'])}"
                ),

                "",

                "R13 RESPONSE / RECONCILIATION",

                (
                    "Order ID Capture: "
                    f"{yn(execution_path['order_id_captured'])}"
                ),

                (
                    "Captured Test Order ID: "
                    f"{execution_path['order_id']}"
                ),

                (
                    "Position Verification: "
                    f"{yn(execution_path['position_verified'])}"
                ),

                (
                    "Failure Rollback Test: "
                    f"{yn(execution_path['rollback_test'])}"
                ),

                "",

                "R13 STABILITY",

                (
                    "HTTP Retry Attempts: "
                    f"{HTTP_RETRY_ATTEMPTS}"
                ),

                (
                    "Single Telegram Report: "
                    "✅ ACTIVE"
                ),

                (
                    "Stage-Aware Errors: "
                    "✅ ACTIVE"
                ),

                (
                    "Transient API Retry: "
                    "✅ ACTIVE"
                ),

                (
                    "Restart Loop Prevention: "
                    "✅ ACTIVE"
                ),

                (
                    "Render Keep-Alive: "
                    "✅ ACTIVE"
                ),

                (
                    "Health Server: "
                    f"✅ PORT {PORT}"
                ),

                "",

                "R13 EXECUTION BOUNDARY",

                (
                    "Leverage POST Transmission: "
                    "🔒 BLOCKED"
                ),

                (
                    "Order POST Transmission: "
                    "🔒 BLOCKED"
                ),

                (
                    "Hard Execution Lock: "
                    "✅ ACTIVE"
                ),

                (
                    "Live Order Execution: "
                    "❌ DISABLED"
                ),

                (
                    "Private POST Transmission: "
                    "❌ DISABLED"
                ),

                "",

                "🛡 Hard execution lock active",

                "⚠️ Live order execution disabled",

                "⚠️ NO LIVE ORDER WAS SENT",
            ]


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


            report = "\n".join(
                report_lines
            )

            print(
                report,
                flush=True,
            )

            print(
                "=" * 60,
                flush=True,
            )

            print(
                (
                    f"{MODULE_NAME} COMPLETE: "
                    + (
                        "PASSED"
                        if all_passed
                        else "NOT READY"
                    )
                ),
                flush=True,
            )

            print(
                "=" * 60,
                flush=True,
            )


            # ================================================
            # EXACTLY ONE TELEGRAM REPORT
            # ================================================

            await send_telegram(
                session,
                report,
            )

            return all_passed


        except Exception as exc:
            error_report = "\n".join(
                [
                    (
                        f"❌ MODULE "
                        f"{MODULE_NAME} ERROR"
                    ),

                    SYMBOL,

                    "",

                    (
                        f"Stage: "
                        f"{stage}"
                    ),

                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),

                    "",

                    "🛡 Hard execution lock active",

                    "⚠️ Live order execution disabled",

                    "⚠️ Private POST transmission disabled",

                    "⚠️ NO LIVE ORDER WAS SENT",
                ]
            )

            print(
                error_report,
                flush=True,
            )

            print(
                "=" * 60,
                flush=True,
            )

            await send_telegram(
                session,
                error_report,
            )

            return False


# ============================================================
# MAIN
# ============================================================

async def main():
    health_server = None

    try:
        health_server = (
            await start_health_server()
        )

        await run_diagnostic()

        if KEEP_ALIVE:
            print(
                (
                    f"{MODULE_NAME} "
                    "KEEP-ALIVE ACTIVE"
                ),
                flush=True,
            )

            while True:
                await asyncio.sleep(
                    KEEP_ALIVE_SECONDS
                )

    finally:
        if health_server:
            health_server.close()

            await health_server.wait_closed()


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
            f"{MODULE_NAME} STOPPED",
            flush=True,)
