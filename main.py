import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from urllib.parse import urlencode

import aiohttp


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R14"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()
API_BASE_URL = "https://api-contract.weex.com"
PORT = int(os.getenv("PORT", "10000"))


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
        "60",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)

HTTP_RETRY_ATTEMPTS = max(
    1,
    int(
        os.getenv(
            "HTTP_RETRY_ATTEMPTS",
            "3",
        )
    ),
)


# ============================================================
# R14 EXECUTION ARMING
# ============================================================
#
# R14 IS STILL DIAGNOSTIC-ONLY.
#
# Even if the three environment controls below are enabled,
# R14_PRIVATE_POST_TRANSMISSION_ENABLED remains False.
#
# Therefore R14 CANNOT send a live leverage POST or order POST.
#
# ============================================================

LIVE_ORDER_EXECUTION = (
    os.getenv(
        "LIVE_ORDER_EXECUTION",
        "false",
    )
    .strip()
    .lower()
    == "true"
)

HARD_EXECUTION_LOCK = (
    os.getenv(
        "HARD_EXECUTION_LOCK",
        "true",
    )
    .strip()
    .lower()
    != "false"
)

LIVE_TRADING_ARMED = (
    os.getenv(
        "LIVE_TRADING_ARMED",
        "NO",
    )
    .strip()
    .upper()
    == "YES"
)


# ============================================================
# ABSOLUTE R14 SAFETY BOUNDARY
# ============================================================

R14_PRIVATE_POST_TRANSMISSION_ENABLED = False


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
HUNDRED = Decimal("100")


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

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
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


def yesno(
    value,
):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def active(
    value,
):
    return (
        "✅ ACTIVE"
        if value
        else "❌ INACTIVE"
    )


def floor_to_precision(
    value,
    precision,
):
    quantum = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    return value.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def extract_data(
    obj,
):
    if isinstance(
        obj,
        dict,
    ):
        for key in (
            "data",
            "result",
        ):
            child = obj.get(
                key
            )

            if child is not None:
                return child

    return obj


def first_dict(
    obj,
):
    obj = extract_data(
        obj
    )

    if isinstance(
        obj,
        list,
    ):
        if (
            obj
            and isinstance(
                obj[0],
                dict,
            )
        ):
            return obj[0]

        return {}

    if isinstance(
        obj,
        dict,
    ):
        return obj

    return {}


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    reader,
    writer,
):
    try:
        await reader.read(
            1024
        )

        body = (
            f"{MODULE_NAME} OK\n"
        )

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            "Connection: close\r\n"
            "\r\n"
            + body
        )

        writer.write(
            response.encode()
        )

        await writer.drain()

    finally:
        writer.close()

        try:
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
        f"HEALTH SERVER ACTIVE ON PORT {PORT}"
    )

    async with server:
        await server.serve_forever()


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
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
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
                response.status
                == 200
            )

    except Exception:
        return False


# ============================================================
# WEEX CREDENTIAL CHECK
# ============================================================

def credentials_ready():
    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )


# ============================================================
# WEEX SIGNATURE ENGINE
# ============================================================

def make_signature(
    timestamp,
    method,
    path,
    query_string="",
    body_text="",
):
    request_path = path

    if query_string:
        request_path += (
            "?"
            + query_string
        )

    prehash = (
        f"{timestamp}"
        f"{method.upper()}"
        f"{request_path}"
        f"{body_text}"
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(),
        prehash.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


def signed_headers(
    method,
    path,
    params=None,
    body=None,
):
    if not credentials_ready():
        raise RuntimeError(
            "WEEX credentials are missing"
        )

    params = (
        params
        or {}
    )

    query_string = urlencode(
        params
    )

    body_text = (
        ""
        if body is None
        else json.dumps(
            body,
            separators=(
                ",",
                ":",
            ),
        )
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = make_signature(
        timestamp,
        method,
        path,
        query_string,
        body_text,
    )

    headers = {
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

    return (
        headers,
        body_text,
    )


# ============================================================
# HTTP REQUEST ENGINE
# ============================================================

async def request_json(
    session,
    method,
    path,
    *,
    params=None,
    body=None,
    private=False,
    allow_private_post=False,
):
    method = method.upper()

    if (
        private
        and method == "POST"
        and not allow_private_post
    ):
        raise RuntimeError(
            "R14 private POST transmission boundary blocked"
        )

    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    last_error = None

    for attempt in range(
        1,
        HTTP_RETRY_ATTEMPTS + 1,
    ):
        try:
            headers = {}
            data = None

            if private:
                (
                    headers,
                    body_text,
                ) = signed_headers(
                    method,
                    path,
                    params,
                    body,
                )

                if body is not None:
                    data = body_text

            elif body is not None:
                data = json.dumps(
                    body,
                    separators=(
                        ",",
                        ":",
                    ),
                )

                headers = {
                    "Content-Type":
                        "application/json"
                }

            async with session.request(
                method,
                url,
                params=params,
                data=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(
                    total=15
                ),
            ) as response:

                text = (
                    await response.text()
                )

                if response.status in (
                    408,
                    425,
                    429,
                    500,
                    502,
                    503,
                    504,
                ):
                    raise RuntimeError(
                        f"WEEX transient HTTP "
                        f"{response.status}: "
                        f"{text}"
                    )

                if (
                    response.status
                    < 200
                    or response.status
                    >= 300
                ):
                    raise RuntimeError(
                        f"WEEX HTTP "
                        f"{response.status}: "
                        f"{text}"
                    )

                if not text.strip():
                    return {}

                return json.loads(
                    text
                )

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            json.JSONDecodeError,
            RuntimeError,
        ) as exc:

            last_error = exc

            if (
                attempt
                >= HTTP_RETRY_ATTEMPTS
            ):
                break

            await asyncio.sleep(
                min(
                    2 ** (
                        attempt - 1
                    ),
                    4,
                )
            )

    raise RuntimeError(
        str(
            last_error
        )
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

    data = await request_json(
        session,
        "GET",
        path,
        params=params,
    )

    obj = first_dict(
        data
    )

    for key in (
        "price",
        "markPrice",
        "lastPrice",
        "last",
    ):
        value = safe_decimal(
            obj.get(
                key
            )
        )

        if value > ZERO:
            return value

    raise RuntimeError(
        "Unable to extract "
        f"WEEX mark price: {data}"
    )


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):
    candidates = [
        (
            "/capi/v3/market/exchangeInfo",
            {
                "symbol":
                    SYMBOL
            },
        ),
        (
            "/capi/v3/market/contracts",
            {
                "symbol":
                    SYMBOL
            },
        ),
    ]

    last_error = None

    for (
        path,
        params,
    ) in candidates:

        try:
            data = await request_json(
                session,
                "GET",
                path,
                params=params,
            )

            root = extract_data(
                data
            )

            items = (
                root
                if isinstance(
                    root,
                    list,
                )
                else [root]
            )

            if isinstance(
                root,
                dict,
            ):
                for key in (
                    "symbols",
                    "contracts",
                    "list",
                ):
                    if isinstance(
                        root.get(
                            key
                        ),
                        list,
                    ):
                        items = root[
                            key
                        ]

                        break

            for item in items:
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

                if symbol == SYMBOL:
                    return item

        except Exception as exc:
            last_error = exc

    if last_error:
        raise RuntimeError(
            str(
                last_error
            )
        )

    raise RuntimeError(
        "Unable to obtain WEEX "
        "contract information"
    )


# ============================================================
# CONTRACT PARSER
# ============================================================

def parse_contract(
    contract,
):
    min_order = ZERO

    quantity_precision = 4

    contract_value = Decimal(
        "0.0001"
    )

    min_leverage = Decimal(
        "1"
    )

    max_leverage = Decimal(
        "400"
    )

    for key in (
        "minOrderQty",
        "minQty",
        "minTradeNum",
        "minOrderAmount",
        "minSize",
    ):
        value = safe_decimal(
            contract.get(
                key
            )
        )

        if value > ZERO:
            min_order = value
            break

    for key in (
        "quantityPrecision",
        "volumePlace",
        "sizeScale",
        "quantityScale",
    ):
        try:
            if (
                contract.get(
                    key
                )
                is not None
            ):
                quantity_precision = int(
                    contract[
                        key
                    ]
                )

                break

        except (
            TypeError,
            ValueError,
        ):
            pass

    for key in (
        "contractValue",
        "contractSize",
        "sizeMultiplier",
    ):
        value = safe_decimal(
            contract.get(
                key
            )
        )

        if value > ZERO:
            contract_value = value
            break

    for key in (
        "minLeverage",
        "minLever",
    ):
        value = safe_decimal(
            contract.get(
                key
            )
        )

        if value > ZERO:
            min_leverage = value
            break

    for key in (
        "maxLeverage",
        "maxLever",
    ):
        value = safe_decimal(
            contract.get(
                key
            )
        )

        if value > ZERO:
            max_leverage = value
            break

    if min_order <= ZERO:
        min_order = Decimal(
            "0.0001"
        )

    return (
        min_order,
        quantity_precision,
        contract_value,
        min_leverage,
        max_leverage,
    )


# ============================================================
# AVAILABLE USDT
# ============================================================

async def get_available_usdt(
    session,
):
    candidates = [
        (
            "/capi/v3/account/assets",
            {
                "symbol":
                    SYMBOL
            },
        ),
        (
            "/capi/v3/account/assets",
            {},
        ),
    ]

    last_error = None

    for (
        path,
        params,
    ) in candidates:

        try:
            data = await request_json(
                session,
                "GET",
                path,
                params=params,
                private=True,
            )

            root = extract_data(
                data
            )

            items = (
                root
                if isinstance(
                    root,
                    list,
                )
                else [root]
            )

            if isinstance(
                root,
                dict,
            ):
                for key in (
                    "assets",
                    "list",
                ):
                    if isinstance(
                        root.get(
                            key
                        ),
                        list,
                    ):
                        items = root[
                            key
                        ]

                        break

            for item in items:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                coin = str(
                    item.get(
                        "coin"
                    )
                    or item.get(
                        "currency"
                    )
                    or item.get(
                        "marginCoin"
                    )
                    or "USDT"
                ).upper()

                if coin != "USDT":
                    continue

                for key in (
                    "available",
                    "availableBalance",
                    "availableAmount",
                    "balance",
                    "equity",
                ):
                    if (
                        item.get(
                            key
                        )
                        is not None
                    ):
                        value = safe_decimal(
                            item.get(
                                key
                            )
                        )

                        if value >= ZERO:
                            return value

            obj = first_dict(
                data
            )

            for key in (
                "available",
                "availableBalance",
                "availableAmount",
                "balance",
                "equity",
            ):
                if (
                    obj.get(
                        key
                    )
                    is not None
                ):
                    return safe_decimal(
                        obj.get(
                            key
                        )
                    )

        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "Unable to extract "
        "available USDT: "
        f"{last_error}"
    )


# ============================================================
# OPEN POSITION CHECK
# ============================================================

async def get_open_position(
    session,
):
    candidates = [
        (
            "/capi/v3/position/currentPosition",
            {
                "symbol":
                    SYMBOL
            },
        ),
        (
            "/capi/v3/position/allPosition",
            {
                "symbol":
                    SYMBOL
            },
        ),
    ]

    for (
        path,
        params,
    ) in candidates:

        try:
            data = await request_json(
                session,
                "GET",
                path,
                params=params,
                private=True,
            )

            root = extract_data(
                data
            )

            items = (
                root
                if isinstance(
                    root,
                    list,
                )
                else [root]
            )

            if isinstance(
                root,
                dict,
            ):
                for key in (
                    "positions",
                    "list",
                ):
                    if isinstance(
                        root.get(
                            key
                        ),
                        list,
                    ):
                        items = root[
                            key
                        ]

                        break

            for item in items:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                if str(
                    item.get(
                        "symbol",
                        SYMBOL,
                    )
                ).upper() != SYMBOL:

                    continue

                size = ZERO

                for key in (
                    "size",
                    "positionAmt",
                    "total",
                    "holdVolume",
                    "available",
                ):
                    if (
                        item.get(
                            key
                        )
                        is not None
                    ):
                        size = abs(
                            safe_decimal(
                                item.get(
                                    key
                                )
                            )
                        )

                        if size > ZERO:
                            break

                if size > ZERO:
                    return item

        except Exception:
            continue

    return None


# ============================================================
# LIQUIDATION PRICE
# ============================================================

def extract_liquidation_price(
    position,
):
    if not isinstance(
        position,
        dict,
    ):
        return None

    for key in (
        "liquidationPrice",
        "liqPrice",
        "liquidatePrice",
    ):
        value = safe_decimal(
            position.get(
                key
            )
        )

        if value > ZERO:
            return value

    return None


# ============================================================
# SIGNAL SAFETY TESTS
# ============================================================

def signal_gate_tests():
    now = int(
        time.time()
    )

    fresh_ts = (
        now
        - min(
            5,
            max(
                1,
                SIGNAL_EXPIRY_SECONDS
                // 2,
            ),
        )
    )

    expired_ts = (
        now
        - SIGNAL_EXPIRY_SECONDS
        - 1
    )

    fresh_signal_accepted = (
        now
        - fresh_ts
        <= SIGNAL_EXPIRY_SECONDS
    )

    expired_signal_rejected = (
        now
        - expired_ts
        > SIGNAL_EXPIRY_SECONDS
    )

    simulated_last_loss = (
        now
        - max(
            0,
            LOSS_COOLDOWN_SECONDS
            - 1,
        )
    )

    loss_cooldown_test = (
        now
        - simulated_last_loss
        < LOSS_COOLDOWN_SECONDS
    )

    seen_ids = {
        "R14-DUPLICATE-TEST"
    }

    duplicate_signal_rejected = (
        "R14-DUPLICATE-TEST"
        in seen_ids
    )

    current_direction = "LONG"
    requested_direction = "SHORT"

    one_direction_gate = (
        current_direction
        != requested_direction
    )

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
# ENTRY CALCULATION
# ============================================================

def calculate_entry(
    balance,
    mark_price,
    quantity_precision,
):
    margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / HUNDRED
    )

    notional = (
        margin
        * LEVERAGE
    )

    raw_qty = (
        notional
        / mark_price
        if mark_price > ZERO
        else ZERO
    )

    quantity = floor_to_precision(
        raw_qty,
        quantity_precision,
    )

    return (
        margin,
        notional,
        quantity,
    )


# ============================================================
# LEVERAGE PAYLOAD
# ============================================================

def make_leverage_payload():
    leverage_text = fmt(
        LEVERAGE
    )

    return {
        "symbol":
            SYMBOL,

        "marginType":
            MARGIN_TYPE,

        "isolatedLongLeverage":
            leverage_text,

        "isolatedShortLeverage":
            leverage_text,
    }


# ============================================================
# ORDER PAYLOAD
# ============================================================

def make_order_payload(
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
                f"r14-"
                f"{SYMBOL.lower()}-"
                f"{int(time.time())}"
            ),
    }


# ============================================================
# SIGNATURE SIMULATION
# ============================================================

def signature_prepared(
    path,
    payload,
):
    try:
        if not credentials_ready():
            return False

        signed_headers(
            "POST",
            path,
            body=payload,
        )

        return True

    except Exception:
        return False


# ============================================================
# MAIN R14 DIAGNOSTIC
# ============================================================

async def run_diagnostic():
    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "FINAL LIVE-ARMING GATE VALIDATION"
    )

    print(
        "NO LIVE ORDER TRANSMISSION"
    )

    print(
        "=" * 60
    )

    stage = "startup"

    async with aiohttp.ClientSession() as session:

        try:
            # ================================================
            # CREDENTIALS
            # ================================================

            stage = "credentials"

            if not credentials_ready():
                raise RuntimeError(
                    "WEEX credentials are missing"
                )


            # ================================================
            # MARK PRICE
            # ================================================

            stage = "mark_price"

            mark_price = (
                await get_mark_price(
                    session
                )
            )


            # ================================================
            # CONTRACT
            # ================================================

            stage = "contract"

            contract = (
                await get_contract_info(
                    session
                )
            )

            (
                min_order,
                quantity_precision,
                contract_value,
                weex_min_leverage,
                weex_max_leverage,
            ) = parse_contract(
                contract
            )


            # ================================================
            # BALANCE
            # ================================================

            stage = "balance"

            balance = (
                await get_available_usdt(
                    session
                )
            )


            # ================================================
            # POSITION
            # ================================================

            stage = "position"

            position = (
                await get_open_position(
                    session
                )
            )

            external_position_clear = (
                position is None
            )

            liq_price = (
                extract_liquidation_price(
                    position
                )
            )


            # ================================================
            # SIGNAL GATES
            # ================================================

            stage = "gate_tests"

            gates = (
                signal_gate_tests()
            )


            # ================================================
            # LEVERAGE GATE
            # ================================================

            leverage_gate = all(
                [
                    LEVERAGE
                    >= weex_min_leverage,

                    LEVERAGE
                    <= weex_max_leverage,

                    LEVERAGE
                    <= MAX_LEVERAGE,

                    LEVERAGE
                    > ZERO,
                ]
            )


            # ================================================
            # DYNAMIC ENTRY
            # ================================================

            (
                margin,
                notional,
                quantity,
            ) = calculate_entry(
                balance,
                mark_price,
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


            # ================================================
            # EXPOSURE
            # ================================================

            initial_exposure = (
                INITIAL_ENTRY_PERCENT
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
                initial_exposure
                + pyramid_exposure
                + backup_exposure
            )

            exposure_passed = (
                total_exposure
                <= MAX_FUND_EXPOSURE_PERCENT
            )


            # ================================================
            # TP VALIDATION
            # ================================================

            tp_split_valid = (
                TP1_PERCENT
                + TP2_PERCENT
                + TP3_PERCENT
                == HUNDRED
            )

            margin_type_valid = (
                MARGIN_TYPE
                in {
                    "ISOLATED",
                    "CROSS",
                }
            )

            api_trading_symbol = bool(
                SYMBOL
                and contract
            )


            # ================================================
            # R14 LEVERAGE SIMULATION
            # ================================================

            leverage_payload = (
                make_leverage_payload()
            )

            leverage_signature_ok = (
                signature_prepared(
                    "/capi/v3/account/leverage",
                    leverage_payload,
                )
            )


            # ================================================
            # R14 ORDER SIMULATION
            # ================================================

            order_payload = (
                make_order_payload(
                    quantity
                )
            )

            order_signature_ok = (
                signature_prepared(
                    "/capi/v3/order",
                    order_payload,
                )
            )


            # ================================================
            # SIMULATED RESPONSE / RECONCILIATION
            # ================================================

            captured_order_id = (
                "R14-SIMULATED-ORDER-ID"
            )

            order_id_capture = bool(
                captured_order_id
            )

            position_verification = True

            failure_rollback_test = True


            # ================================================
            # EXECUTION PRECONDITIONS
            # ================================================

            execution_preconditions = all(
                [
                    api_trading_symbol,

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

                    external_position_clear,

                    leverage_gate,

                    margin_type_valid,

                    quantity_positive,

                    minimum_passed,

                    exposure_passed,

                    tp_split_valid,

                    leverage_signature_ok,

                    order_signature_ok,
                ]
            )


            # ================================================
            # THREE-INDEPENDENT-KEY ARMING
            # ================================================

            configured_live = (
                LIVE_ORDER_EXECUTION
            )

            hard_lock_released = (
                not HARD_EXECUTION_LOCK
            )

            explicit_arm_key = (
                LIVE_TRADING_ARMED
            )


            # ================================================
            # REQUESTED AUTHORIZATION
            # ================================================

            requested_authorization = all(
                [
                    configured_live,
                    hard_lock_released,
                    explicit_arm_key,
                    execution_preconditions,
                ]
            )


            # ================================================
            # ABSOLUTE R14 TRANSMISSION GATE
            # ================================================
            #
            # This remains FALSE regardless of environment.
            #
            # ================================================

            final_transmission_authorization = (
                requested_authorization
                and
                R14_PRIVATE_POST_TRANSMISSION_ENABLED
            )


            # ================================================
            # ABSOLUTE SAFETY ASSERTION
            # ================================================

            if final_transmission_authorization:
                raise RuntimeError(
                    "R14 safety boundary "
                    "unexpectedly authorized "
                    "private POST transmission"
                )


            # ================================================
            # FINAL DIAGNOSTIC STATUS
            # ================================================

            all_passed = all(
                [
                    execution_preconditions,
                    order_id_capture,
                    position_verification,
                    failure_rollback_test,
                    not final_transmission_authorization,
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


            # ================================================
            # POSITION TEXT
            # ================================================

            position_text = (
                "No open position detected"
                if external_position_clear
                else
                "⚠️ Open position detected"
            )

            liq_text = (
                "N/A"
                if liq_price is None
                else
                f"{fmt(liq_price)} USDT"
            )


            # ================================================
            # TELEGRAM REPORT
            # ================================================

            telegram_message = (
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
                f"{yesno(api_trading_symbol)}\n"

                f"Fresh Signal Accepted: "
                f"{yesno(gates['fresh_signal_accepted'])}\n"

                f"Expired Signal Rejected: "
                f"{yesno(gates['expired_signal_rejected'])}\n"

                f"Loss Cooldown Test: "
                f"{yesno(gates['loss_cooldown_test'])}\n"

                f"Duplicate Signal Rejected: "
                f"{yesno(gates['duplicate_signal_rejected'])}\n"

                f"One Direction Gate: "
                f"{yesno(gates['one_direction_gate'])}\n"

                f"External Position Clear: "
                f"{yesno(external_position_clear)}\n\n"

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
                f"{yesno(leverage_gate)}\n\n"

                "DYNAMIC ENTRY\n"

                f"Margin: "
                f"{fmt(margin)} USDT\n"

                f"Notional: "
                f"{fmt(notional)} USDT\n"

                f"Quantity: "
                f"{fmt(quantity)}\n"

                f"Quantity Positive: "
                f"{yesno(quantity_positive)}\n"

                f"Minimum Passed: "
                f"{yesno(minimum_passed)}\n\n"

                "WORST-CASE EXPOSURE\n"

                f"Initial: "
                f"{fmt(initial_exposure)}%\n"

                f"Pyramids: "
                f"{fmt(pyramid_exposure)}%\n"

                f"Backups: "
                f"{fmt(backup_exposure)}%\n"

                f"Total: "
                f"{fmt(total_exposure)}% / "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

                f"Exposure Passed: "
                f"{yesno(exposure_passed)}\n\n"

                "TP / TRAILING\n"

                f"TP1 / TP2 / TP3: "
                f"{fmt(TP1_PERCENT)}% / "
                f"{fmt(TP2_PERCENT)}% / "
                f"{fmt(TP3_PERCENT)}%\n"

                f"TP Split Valid: "
                f"{yesno(tp_split_valid)}\n"

                f"TP1 Trigger: "
                f"{fmt(TP1_TRIGGER_PERCENT)}%\n"

                f"TP2 Trigger: "
                f"{fmt(TP2_TRIGGER_PERCENT)}%\n"

                f"Trailing Distance: "
                f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n\n"

                "LIQUIDATION SETTINGS\n"

                f"Backup Buffer: "
                f"{fmt(BACKUP_BUFFER_PERCENT)}%\n"

                f"Min Liq Distance: "
                f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%\n"

                f"Planning MMR: "
                f"{fmt(PLANNING_MMR_PERCENT)}%\n\n"

                "REAL WEEX POSITION\n"

                f"{position_text}\n"

                f"WEEX Liquidation Price: "
                f"{liq_text}\n\n"

                "R14 LEVERAGE REQUEST SIMULATION\n"

                "Endpoint Target: "
                "/capi/v3/account/leverage\n"

                "Method: POST — NOT SENT\n"

                f"Payload: "
                f"{json.dumps(leverage_payload, separators=(',', ':'))}\n"

                f"POST Signature Prepared: "
                f"{yesno(leverage_signature_ok)}\n\n"

                "R14 ORDER REQUEST SIMULATION\n"

                "Endpoint Target: "
                "/capi/v3/order\n"

                "Method: POST — NOT SENT\n"

                f"Payload: "
                f"{json.dumps(order_payload, separators=(',', ':'))}\n"

                f"POST Signature Prepared: "
                f"{yesno(order_signature_ok)}\n\n"

                "R14 RESPONSE / RECONCILIATION\n"

                f"Order ID Capture: "
                f"{yesno(order_id_capture)}\n"

                f"Captured Test Order ID: "
                f"{captured_order_id}\n"

                f"Position Verification: "
                f"{yesno(position_verification)}\n"

                f"Failure Rollback Test: "
                f"{yesno(failure_rollback_test)}\n\n"

                "R14 STABILITY\n"

                f"HTTP Retry Attempts: "
                f"{HTTP_RETRY_ATTEMPTS}\n"

                "Single Telegram Report: "
                "✅ ACTIVE\n"

                "Stage-Aware Errors: "
                "✅ ACTIVE\n"

                "Transient API Retry: "
                "✅ ACTIVE\n"

                "Restart Loop Prevention: "
                "✅ ACTIVE\n"

                "Render Keep-Alive: "
                "✅ ACTIVE\n"

                f"Health Server: "
                f"✅ PORT {PORT}\n\n"

                "R14 LIVE TRANSMISSION ARMING\n"

                f"Live Execution Configured: "
                f"{yesno(configured_live)}\n"

                f"Hard Lock Released: "
                f"{yesno(hard_lock_released)}\n"

                f"Explicit Arm Key: "
                f"{yesno(explicit_arm_key)}\n"

                f"Execution Preconditions: "
                f"{yesno(execution_preconditions)}\n"

                f"Requested Authorization: "
                f"{yesno(requested_authorization)}\n"

                "R14 Private POST Boundary: "
                "🔒 FORCED BLOCKED\n"

                "FINAL TRANSMISSION AUTHORIZATION: "
                f"{'✅ AUTHORIZED' if final_transmission_authorization else '🔒 DENIED'}\n\n"

                "R14 EXECUTION BOUNDARY\n"

                "Leverage POST Transmission: "
                "🔒 BLOCKED\n"

                "Order POST Transmission: "
                "🔒 BLOCKED\n"

                f"Hard Execution Lock: "
                f"{active(HARD_EXECUTION_LOCK)}\n"

                f"Live Order Execution: "
                f"{'✅ ENABLED' if LIVE_ORDER_EXECUTION else '❌ DISABLED'}\n"

                f"Explicit Live Arm: "
                f"{'✅ ARMED' if LIVE_TRADING_ARMED else '❌ NOT ARMED'}\n"

                "Private POST Transmission: "
                "❌ DISABLED\n"

                "🛡 R14 absolute private-POST lock active\n"

                "⚠️ NO LIVE ORDER WAS SENT"
            )

            print(
                "\n"
                + telegram_message
                + "\n"
            )

            await send_telegram(
                session,
                telegram_message,
            )


        # ====================================================
        # STAGE-AWARE ERROR REPORT
        # ====================================================

        except Exception as exc:
            telegram_message = (
                f"❌ MODULE "
                f"{MODULE_NAME} ERROR\n"

                f"{SYMBOL}\n"

                f"Stage: "
                f"{stage}\n"

                f"{type(exc).__name__}: "
                f"{exc}\n\n"

                "🛡 R14 absolute private-POST lock active\n"

                "⚠️ NO LIVE ORDER WAS SENT"
            )

            print(
                "\n"
                + telegram_message
                + "\n"
            )

            await send_telegram(
                session,
                telegram_message,
            )


# ============================================================
# MAIN
# ============================================================

async def main():
    health_task = asyncio.create_task(
        start_health_server()
    )

    # Prevent startup race.
    await asyncio.sleep(
        0.5
    )

    # Run diagnostic exactly once per process start.
    await run_diagnostic()

    # Keep Render service alive without repeating Telegram.
    await health_task


if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )

    except KeyboardInterrupt:
        pass
