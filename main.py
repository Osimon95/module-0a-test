# ==================================================================================================
# R34W.1 - LIVE STATE + SYNTHETIC STRATEGY DECISION / ORDER CANDIDATE VALIDATION
# ==================================================================================================
#
# SAFETY MODEL
#
#   - AUTHENTICATED GET ONLY
#   - PUBLIC GET ONLY
#   - NO POST
#   - NO PUT
#   - NO PATCH
#   - NO DELETE
#   - NO REAL ORDER
#   - NO DEMO ORDER
#   - NO LEVERAGE CHANGE
#   - NO MARGIN CHANGE
#   - NO POSITION CHANGE
#   - NO ACCOUNT MUTATION
#
# R34W.1 CHANGE
#
#   Correct WEEX V3 authenticated signing:
#
#       timestamp
#       + METHOD
#       + requestPath
#       + optional "?" + queryString
#       + body
#
#   HMAC-SHA256 using WEEX_API_SECRET
#       ↓
#   BASE64 encoding
#       ↓
#   ACCESS-SIGN
#
# IMPORTANT
#
#   THIS FILE HAS NO LIVE WRITE TRANSPORT.
#
#   ALL ORDER OBJECTS ARE SYNTHETIC.
#
# ==================================================================================================


import base64
import hashlib
import hmac
import json
import math
import os
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

from decimal import Decimal, ROUND_DOWN, ROUND_UP, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# VERSION
# ==================================================================================================


VERSION = "R34W.1"


# ==================================================================================================
# EXCHANGE
# ==================================================================================================


WEEX_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ==================================================================================================
# CREDENTIALS
# ==================================================================================================


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


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ==================================================================================================
# STRATEGY
# ==================================================================================================


TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")

PYRAMID_SIZE_PERCENT = Decimal("5")

BACKUP_SIZE_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1

MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

BACKUP_BUFFER_PERCENT = Decimal("0.3")

SIGNAL_EXPIRY_SECONDS = 120

LOSS_COOLDOWN_SECONDS = 300


# ==================================================================================================
# TAKE PROFIT MODEL
# ==================================================================================================


TP1_PERCENT = Decimal("20")

TP2_PERCENT = Decimal("20")

TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")

TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ==================================================================================================
# SAFETY FLAGS
# ==================================================================================================


AUTHENTICATED_READ_ONLY = True

PUBLIC_READ_ONLY = True

NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION_ENABLED = False

DEMO_ORDER_EXECUTION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# ==================================================================================================
# STRATEGY SAFETY TOGGLES
# ==================================================================================================


ONE_DIRECTION_ONLY = True

ANTI_DUPLICATE_ORDERS = True

TREND_REVERSAL_EXIT = True

IDLE_PYRAMID_CLEANUP = True


# ==================================================================================================
# LIVE READ PATHS
# ==================================================================================================


BALANCE_PATH = "/capi/v3/account/balance"

POSITION_PATH = "/capi/v3/account/position/allPosition"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

SYMBOL_PRICE_PATH = "/capi/v3/market/symbolPrice"

EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"


# ==================================================================================================
# COUNTERS
# ==================================================================================================


authenticated_get_count = 0

public_get_count = 0

network_write_count = 0

real_order_count = 0

demo_order_count = 0

leverage_mutation_count = 0

margin_mutation_count = 0

position_mutation_count = 0

account_mutation_count = 0

synthetic_dispatch_count = 0


# ==================================================================================================
# RUNTIME STATE
# ==================================================================================================


runtime_state = {
    "version": VERSION,
    "phase": "STARTING",
    "validation_complete": False,
    "validation_passed": False,
    "last_error": None,
    "available_usdt": None,
    "market_price": None,
    "margin_type": None,
    "long_leverage": None,
    "short_leverage": None,
    "open_positions": 0,
    "synthetic_decision": None,
    "synthetic_quantity": None,
    "synthetic_payload_hash": None,
}


# ==================================================================================================
# PRINT HELPERS
# ==================================================================================================


LINE = "-" * 100


def banner(text):
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def log(message):
    print(
        f"{VERSION}: {message}",
        flush=True,
    )


def status(label, passed):
    marker = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<88} {marker}",
        flush=True,
    )

    return bool(passed)


def require(label, condition):
    condition = bool(condition)

    status(
        label,
        condition,
    )

    if not condition:
        raise RuntimeError(
            f"Validation assertion failed: {label}"
        )


# ==================================================================================================
# DECIMAL HELPERS
# ==================================================================================================


def D(value):
    if isinstance(value, Decimal):
        return value

    if value is None:
        raise ValueError(
            "Cannot convert None to Decimal"
        )

    try:
        return Decimal(
            str(value)
        )

    except InvalidOperation as exc:
        raise ValueError(
            f"Invalid decimal value: {value!r}"
        ) from exc


def decimal_text(value):
    value = D(value)

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    if text in (
        "",
        "-0",
    ):
        return "0"

    return text


# ==================================================================================================
# ABSOLUTE NETWORK WRITE FIREBREAK
# ==================================================================================================


def reject_network_write(*args, **kwargs):
    raise RuntimeError(
        "R34W.1 ABSOLUTE FIREBREAK: "
        "network write transport is disabled"
    )


def http_post(*args, **kwargs):
    return reject_network_write(
        *args,
        **kwargs,
    )


def http_put(*args, **kwargs):
    return reject_network_write(
        *args,
        **kwargs,
    )


def http_patch(*args, **kwargs):
    return reject_network_write(
        *args,
        **kwargs,
    )


def http_delete(*args, **kwargs):
    return reject_network_write(
        *args,
        **kwargs,
    )


def send_real_order(*args, **kwargs):
    raise RuntimeError(
        "R34W.1 FIREBREAK: "
        "real order execution is disabled"
    )


def send_demo_order(*args, **kwargs):
    raise RuntimeError(
        "R34W.1 FIREBREAK: "
        "demo order execution is disabled"
    )


def change_leverage(*args, **kwargs):
    raise RuntimeError(
        "R34W.1 FIREBREAK: "
        "leverage mutation is disabled"
    )


def change_margin_type(*args, **kwargs):
    raise RuntimeError(
        "R34W.1 FIREBREAK: "
        "margin mutation is disabled"
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        "R34W.1 FIREBREAK: "
        "position mutation is disabled"
    )


def mutate_account(*args, **kwargs):
    raise RuntimeError(
        "R34W.1 FIREBREAK: "
        "account mutation is disabled"
    )


# ==================================================================================================
# CANONICAL QUERY ENCODING
# ==================================================================================================


def canonical_query_string(params):
    if not params:
        return ""

    cleaned = []

    for key, value in params.items():

        if value is None:
            continue

        if isinstance(
            value,
            bool,
        ):
            value = (
                "true"
                if value
                else "false"
            )

        cleaned.append(
            (
                str(key),
                str(value),
            )
        )

    return urllib.parse.urlencode(
        cleaned,
        doseq=True,
    )


# ==================================================================================================
# R34W.1 WEEX SIGNATURE
# ==================================================================================================


def build_weex_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    """
    WEEX signature:

        timestamp
        + method.upper()
        + requestPath
        + optional "?" + queryString
        + body

    HMAC-SHA256
        ↓
    Base64
    """

    method = str(
        method
    ).upper()

    timestamp = str(
        timestamp
    )

    request_path = str(
        request_path
    )

    query_string = str(
        query_string or ""
    )

    body = str(
        body or ""
    )

    if query_string:

        prehash = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        prehash = (
            timestamp
            + method
            + request_path
            + body
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

    signature = base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )

    return signature


# ==================================================================================================
# AUTHENTICATED GET
# ==================================================================================================


def authenticated_get(
    path,
    params=None,
):
    global authenticated_get_count

    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only access is disabled"
        )

    if not isinstance(
        path,
        str,
    ):
        raise RuntimeError(
            "Authenticated GET path must be a string"
        )

    if not path.startswith(
        "/capi/v3/"
    ):
        raise RuntimeError(
            "Authenticated GET rejected outside "
            f"WEEX V3 contract namespace: {path}"
        )

    if not WEEX_API_KEY:
        raise RuntimeError(
            "WEEX_API_KEY missing"
        )

    if not WEEX_API_SECRET:
        raise RuntimeError(
            "WEEX_API_SECRET missing"
        )

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing"
        )

    params = params or {}

    query_string = canonical_query_string(
        params
    )

    if query_string:

        url = (
            WEEX_BASE_URL
            + path
            + "?"
            + query_string
        )

    else:

        url = (
            WEEX_BASE_URL
            + path
        )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = build_weex_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "R34W.1-ReadOnly/1.0",
    }

    request = urllib.request.Request(
        url=url,
        data=None,
        headers=headers,
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            authenticated_get_count += 1

            if not raw.strip():
                return None

            return json.loads(
                raw
            )

    except urllib.error.HTTPError as exc:

        try:

            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:

            error_body = (
                "<unable to read response body>"
            )

        raise RuntimeError(
            "Authenticated GET failed: "
            f"{path}"
            f" | HTTP {exc.code}"
            f" | WEEX_RESPONSE={error_body}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "Authenticated GET failed: "
            f"{path}"
            f" | URLError: {exc}"
        ) from exc

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Authenticated GET returned "
            f"invalid JSON: {path}"
        ) from exc


# ==================================================================================================
# PUBLIC GET
# ==================================================================================================


def public_get(
    path,
    params=None,
):
    global public_get_count

    if not PUBLIC_READ_ONLY:
        raise RuntimeError(
            "Public read-only access is disabled"
        )

    if not isinstance(
        path,
        str,
    ):
        raise RuntimeError(
            "Public GET path must be a string"
        )

    if not path.startswith(
        "/capi/v3/market/"
    ):
        raise RuntimeError(
            "Public GET rejected outside "
            f"market namespace: {path}"
        )

    params = params or {}

    query_string = canonical_query_string(
        params
    )

    if query_string:

        url = (
            WEEX_BASE_URL
            + path
            + "?"
            + query_string
        )

    else:

        url = (
            WEEX_BASE_URL
            + path
        )

    request = urllib.request.Request(
        url=url,
        data=None,
        headers={
            "Accept": "application/json",
            "User-Agent": "R34W.1-PublicReadOnly/1.0",
        },
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            public_get_count += 1

            if not raw.strip():
                return None

            return json.loads(
                raw
            )

    except urllib.error.HTTPError as exc:

        try:

            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:

            error_body = (
                "<unable to read response body>"
            )

        raise RuntimeError(
            "Public GET failed: "
            f"{path}"
            f" | HTTP {exc.code}"
            f" | WEEX_RESPONSE={error_body}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "Public GET failed: "
            f"{path}"
            f" | URLError: {exc}"
        ) from exc


# ==================================================================================================
# RESPONSE HELPERS
# ==================================================================================================


def unwrap_data(response):
    if isinstance(
        response,
        dict,
    ):

        if "data" in response:

            data = response[
                "data"
            ]

            if data is not None:
                return data

    return response


# ==================================================================================================
# LIVE BALANCE
# ==================================================================================================


def read_available_usdt():
    response = authenticated_get(
        BALANCE_PATH
    )

    data = unwrap_data(
        response
    )

    if isinstance(
        data,
        dict,
    ):

        if (
            str(
                data.get(
                    "asset",
                    ""
                )
            ).upper()
            == "USDT"
        ):

            value = data.get(
                "availableBalance"
            )

            if value is not None:
                return D(
                    value
                )

    if isinstance(
        data,
        list,
    ):

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            asset = str(
                item.get(
                    "asset",
                    ""
                )
            ).upper()

            if asset != "USDT":
                continue

            value = item.get(
                "availableBalance"
            )

            if value is None:

                value = item.get(
                    "available"
                )

            if value is None:

                value = item.get(
                    "balance"
                )

            if value is not None:

                return D(
                    value
                )

    raise RuntimeError(
        "USDT available balance "
        "could not be parsed"
    )


# ==================================================================================================
# LIVE POSITIONS
# ==================================================================================================


def read_positions():
    response = authenticated_get(
        POSITION_PATH
    )

    data = unwrap_data(
        response
    )

    if data is None:
        return []

    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):

        for key in (
            "positions",
            "list",
            "items",
            "rows",
        ):

            candidate = data.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):
                return candidate

    raise RuntimeError(
        "Position response could "
        "not be parsed"
    )


# ==================================================================================================
# SYMBOL CONFIGURATION
# ==================================================================================================


def read_symbol_config():
    response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    data = unwrap_data(
        response
    )

    if isinstance(
        data,
        dict,
    ):

        if str(
            data.get(
                "symbol",
                SYMBOL,
            )
        ).upper() == SYMBOL:

            return data

    if isinstance(
        data,
        list,
    ):

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if str(
                item.get(
                    "symbol",
                    ""
                )
            ).upper() == SYMBOL:

                return item

    raise RuntimeError(
        f"Symbol configuration "
        f"not found for {SYMBOL}"
    )


# ==================================================================================================
# MARKET PRICE
# ==================================================================================================


def read_market_price():
    response = public_get(
        SYMBOL_PRICE_PATH,
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    data = unwrap_data(
        response
    )

    if isinstance(
        data,
        dict,
    ):

        value = data.get(
            "price"
        )

        if value is not None:

            price = D(
                value
            )

            if price > 0:
                return price

    if isinstance(
        data,
        list,
    ):

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if str(
                item.get(
                    "symbol",
                    ""
                )
            ).upper() != SYMBOL:
                continue

            value = item.get(
                "price"
            )

            if value is not None:

                price = D(
                    value
                )

                if price > 0:
                    return price

    raise RuntimeError(
        "Market price could "
        "not be parsed"
    )


# ==================================================================================================
# EXCHANGE INFORMATION
# ==================================================================================================


def read_exchange_info():
    response = public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    return unwrap_data(
        response
    )


# ==================================================================================================
# CONTRACT PARSER
# ==================================================================================================


def find_symbol_record(
    exchange_info
):
    data = exchange_info

    if isinstance(
        data,
        dict,
    ):

        symbols = data.get(
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

                if str(
                    item.get(
                        "symbol",
                        ""
                    )
                ).upper() == SYMBOL:

                    return item

        if str(
            data.get(
                "symbol",
                ""
            )
        ).upper() == SYMBOL:

            return data

    if isinstance(
        data,
        list,
    ):

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if str(
                item.get(
                    "symbol",
                    ""
                )
            ).upper() == SYMBOL:

                return item

    return {}


# ==================================================================================================
# FILTER PARSER
# ==================================================================================================


def find_filter(
    symbol_record,
    filter_type,
):
    filters = symbol_record.get(
        "filters",
        []
    )

    if not isinstance(
        filters,
        list,
    ):
        return {}

    for item in filters:

        if not isinstance(
            item,
            dict,
        ):
            continue

        if str(
            item.get(
                "filterType",
                ""
            )
        ).upper() == filter_type.upper():

            return item

    return {}


# ==================================================================================================
# CONTRACT CONSTRAINT EXTRACTION
# ==================================================================================================


def parse_contract_constraints(
    symbol_record
):
    lot_filter = find_filter(
        symbol_record,
        "LOT_SIZE",
    )

    price_filter = find_filter(
        symbol_record,
        "PRICE_FILTER",
    )

    min_qty_candidates = [
        lot_filter.get(
            "minQty"
        ),
        symbol_record.get(
            "minQty"
        ),
        symbol_record.get(
            "minOrderQty"
        ),
        symbol_record.get(
            "minOrderAmount"
        ),
        "0.0001",
    ]

    qty_step_candidates = [
        lot_filter.get(
            "stepSize"
        ),
        symbol_record.get(
            "quantityStep"
        ),
        symbol_record.get(
            "qtyStep"
        ),
        "0.0001",
    ]

    price_step_candidates = [
        price_filter.get(
            "tickSize"
        ),
        symbol_record.get(
            "priceStep"
        ),
        "0.1",
    ]

    qty_precision_candidates = [
        symbol_record.get(
            "quantityPrecision"
        ),
        symbol_record.get(
            "qtyPrecision"
        ),
        4,
    ]

    price_precision_candidates = [
        symbol_record.get(
            "pricePrecision"
        ),
        1,
    ]

    def first_decimal(
        candidates,
        default,
    ):
        for value in candidates:

            if value is None:
                continue

            try:

                result = D(
                    value
                )

                if result > 0:
                    return result

            except Exception:
                continue

        return D(
            default
        )

    def first_int(
        candidates,
        default,
    ):
        for value in candidates:

            if value is None:
                continue

            try:

                return int(
                    value
                )

            except Exception:
                continue

        return int(
            default
        )

    return {
        "min_qty": first_decimal(
            min_qty_candidates,
            "0.0001",
        ),
        "qty_step": first_decimal(
            qty_step_candidates,
            "0.0001",
        ),
        "price_step": first_decimal(
            price_step_candidates,
            "0.1",
        ),
        "qty_precision": first_int(
            qty_precision_candidates,
            4,
        ),
        "price_precision": first_int(
            price_precision_candidates,
            1,
        ),
    }


# ==================================================================================================
# QUANTITY NORMALIZATION
# ==================================================================================================


def normalize_quantity(
    raw_quantity,
    min_qty,
    qty_step,
):
    raw_quantity = D(
        raw_quantity
    )

    min_qty = D(
        min_qty
    )

    qty_step = D(
        qty_step
    )

    if raw_quantity <= 0:
        raise RuntimeError(
            "Raw quantity must be positive"
        )

    if qty_step <= 0:
        raise RuntimeError(
            "Quantity step must be positive"
        )

    steps = (
        raw_quantity
        / qty_step
    ).to_integral_value(
        rounding=ROUND_UP
    )

    normalized = (
        steps
        * qty_step
    )

    if normalized < min_qty:
        normalized = min_qty

    return normalized


# ==================================================================================================
# OPEN POSITION PARSER
# ==================================================================================================


def symbol_positions(
    positions
):
    result = []

    for item in positions:

        if not isinstance(
            item,
            dict,
        ):
            continue

        if str(
            item.get(
                "symbol",
                ""
            )
        ).upper() != SYMBOL:
            continue

        result.append(
            item
        )

    return result


def position_size(
    record
):
    for key in (
        "size",
        "positionAmt",
        "positionSize",
        "qty",
        "quantity",
    ):

        value = record.get(
            key
        )

        if value is None:
            continue

        try:
            return abs(
                D(
                    value
                )
            )

        except Exception:
            continue

    return Decimal(
        "0"
    )


def open_symbol_positions(
    positions
):
    result = []

    for item in symbol_positions(
        positions
    ):

        if position_size(
            item
        ) > 0:

            result.append(
                item
            )

    return result


# ==================================================================================================
# STRATEGY DECISION
# ==================================================================================================


def build_synthetic_decision(
    open_positions,
):
    if open_positions:

        return {
            "action": "HOLD",
            "reason": (
                "existing BTCUSDT "
                "position detected"
            ),
            "side": None,
            "positionSide": None,
            "synthetic": True,
        }

    return {
        "action": "OPEN_LONG_CANDIDATE",
        "reason": (
            "no open BTCUSDT "
            "position detected"
        ),
        "side": "BUY",
        "positionSide": "LONG",
        "synthetic": True,
    }


# ==================================================================================================
# SYNTHETIC CLIENT ORDER ID
# ==================================================================================================


def build_synthetic_client_order_id(
    decision,
    quantity,
    market_price,
):
    seed = (
        VERSION
        + "|"
        + SYMBOL
        + "|"
        + str(
            decision.get(
                "action"
            )
        )
        + "|"
        + decimal_text(
            quantity
        )
        + "|"
        + decimal_text(
            market_price
        )
    )

    digest = hashlib.sha256(
        seed.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        "r34w1-"
        + digest[:20]
    )


# ==================================================================================================
# SYNTHETIC ORDER INTENT
# ==================================================================================================


def build_order_intent(
    decision,
    quantity,
    market_price,
    available_usdt,
):
    if decision.get(
        "action"
    ) != "OPEN_LONG_CANDIDATE":

        return None

    client_order_id = (
        build_synthetic_client_order_id(
            decision,
            quantity,
            market_price,
        )
    )

    return {
        "syntheticOnly": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": decimal_text(
            quantity
        ),
        "newClientOrderId": client_order_id,
        "referencePrice": decimal_text(
            market_price
        ),
        "availableUSDT": decimal_text(
            available_usdt
        ),
        "targetLeverage": decimal_text(
            TARGET_LEVERAGE
        ),
        "targetMarginType": (
            TARGET_MARGIN_TYPE
        ),
        "strategyVersion": VERSION,
    }


# ==================================================================================================
# SYNTHETIC PAYLOAD
# ==================================================================================================


def build_synthetic_payload(
    intent
):
    if intent is None:
        return None

    return {
        "symbol": intent[
            "symbol"
        ],
        "side": intent[
            "side"
        ],
        "positionSide": intent[
            "positionSide"
        ],
        "type": intent[
            "type"
        ],
        "quantity": intent[
            "quantity"
        ],
        "newClientOrderId": intent[
            "newClientOrderId"
        ],
    }


# ==================================================================================================
# CANONICAL JSON
# ==================================================================================================


def canonical_json(
    value
):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


# ==================================================================================================
# SHA256
# ==================================================================================================


def sha256_json(
    value
):
    return hashlib.sha256(
        canonical_json(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


# ==================================================================================================
# SYNTHETIC EXECUTION ENVELOPE
# ==================================================================================================


def build_synthetic_envelope(
    live_state,
    decision,
    intent,
    payload,
):
    return {
        "version": VERSION,
        "syntheticOnly": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "liveState": live_state,
        "decision": decision,
        "intent": intent,
        "payload": payload,
        "bindings": {
            "liveStateSHA256": sha256_json(
                live_state
            ),
            "decisionSHA256": sha256_json(
                decision
            ),
            "intentSHA256": (
                sha256_json(
                    intent
                )
                if intent
                else None
            ),
            "payloadSHA256": (
                sha256_json(
                    payload
                )
                if payload
                else None
            ),
        },
    }


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================


def synthetic_dispatch(
    envelope
):
    global synthetic_dispatch_count

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "Synthetic-only transport "
            "must remain enabled"
        )

    if envelope.get(
        "syntheticOnly"
    ) is not True:
        raise RuntimeError(
            "Synthetic envelope required"
        )

    if envelope.get(
        "transmissionAllowed"
    ) is not False:
        raise RuntimeError(
            "Transmission must be forbidden"
        )

    if envelope.get(
        "networkWriteAllowed"
    ) is not False:
        raise RuntimeError(
            "Network write must be forbidden"
        )

    synthetic_dispatch_count += 1

    return {
        "syntheticOnly": True,
        "transmitted": False,
        "networkWriteOccurred": False,
        "dispatchNumber": (
            synthetic_dispatch_count
        ),
        "payloadSHA256": (
            envelope
            .get(
                "bindings",
                {}
            )
            .get(
                "payloadSHA256"
            )
        ),
    }


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self
    ):
        payload = {
            "ok": True,
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": runtime_state.get(
                "phase"
            ),
            "validation_complete": (
                runtime_state.get(
                    "validation_complete"
                )
            ),
            "validation_passed": (
                runtime_state.get(
                    "validation_passed"
                )
            ),
            "network_writes": (
                network_write_count
            ),
            "real_orders": (
                real_order_count
            ),
            "demo_orders": (
                demo_order_count
            ),
            "synthetic_dispatches": (
                synthetic_dispatch_count
            ),
        }

        body = json.dumps(
            payload
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json",
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
    def worker():
        try:

            server = HTTPServer(
                (
                    "0.0.0.0",
                    HEALTH_PORT,
                ),
                HealthHandler,
            )

            server.serve_forever()

        except Exception as exc:

            log(
                "HEALTH SERVER ERROR="
                + repr(
                    exc
                )
            )

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# TEST 1
# ==================================================================================================


def test_absolute_safety():
    banner(
        f"{VERSION} TEST 1: "
        "ABSOLUTE SAFETY FIREBREAK"
    )

    require(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION_ENABLED,
    )

    require(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION_ENABLED,
    )

    require(
        "Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    require(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    require(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    require(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    require(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION_ENABLED,
    )

    require(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY,
    )

    require(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY,
    )

    require(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )


# ==================================================================================================
# TEST 2
# ==================================================================================================


def test_credentials():
    banner(
        f"{VERSION} TEST 2: "
        "CREDENTIAL PRESENCE"
    )

    require(
        "WEEX API Key Is Present",
        bool(
            WEEX_API_KEY
        ),
    )

    require(
        "WEEX API Secret Is Present",
        bool(
            WEEX_API_SECRET
        ),
    )

    require(
        "WEEX API Passphrase Is Present",
        bool(
            WEEX_API_PASSPHRASE
        ),
    )


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================


def run_validation():
    runtime_state[
        "phase"
    ] = "VALIDATING"

    # ----------------------------------------------------------------------------------------------
    # TEST 1
    # ----------------------------------------------------------------------------------------------

    test_absolute_safety()

    # ----------------------------------------------------------------------------------------------
    # TEST 2
    # ----------------------------------------------------------------------------------------------

    test_credentials()

    # ----------------------------------------------------------------------------------------------
    # TEST 3
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 3: "
        "LIVE BALANCE RECONCILIATION"
    )

    available_usdt = (
        read_available_usdt()
    )

    runtime_state[
        "available_usdt"
    ] = decimal_text(
        available_usdt
    )

    require(
        "Available Balance Was Read",
        available_usdt is not None,
    )

    require(
        "Available Balance Is Positive",
        available_usdt > 0,
    )

    log(
        "BALANCE PATH="
        + BALANCE_PATH
    )

    log(
        "AVAILABLE USDT="
        + decimal_text(
            available_usdt
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 4
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 4: "
        "LIVE POSITION RECONCILIATION"
    )

    positions = read_positions()

    btc_positions = symbol_positions(
        positions
    )

    open_positions = (
        open_symbol_positions(
            positions
        )
    )

    runtime_state[
        "open_positions"
    ] = len(
        open_positions
    )

    require(
        "Position Response Was Read",
        isinstance(
            positions,
            list,
        ),
    )

    log(
        "POSITION PATH="
        + POSITION_PATH
    )

    log(
        "TOTAL POSITION RECORDS="
        + str(
            len(
                positions
            )
        )
    )

    log(
        f"{SYMBOL} POSITION RECORDS="
        + str(
            len(
                btc_positions
            )
        )
    )

    log(
        f"{SYMBOL} OPEN POSITIONS="
        + str(
            len(
                open_positions
            )
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 5
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 5: "
        "ACCOUNT CONFIGURATION RECONCILIATION"
    )

    symbol_config = (
        read_symbol_config()
    )

    margin_type = str(
        symbol_config.get(
            "marginType",
            "",
        )
    ).upper()

    separated_type = str(
        symbol_config.get(
            "separatedType",
            symbol_config.get(
                "positionMode",
                "",
            ),
        )
    ).upper()

    long_leverage = D(
        symbol_config.get(
            "isolatedLongLeverage",
            symbol_config.get(
                "longLeverage",
                "0",
            ),
        )
    )

    short_leverage = D(
        symbol_config.get(
            "isolatedShortLeverage",
            symbol_config.get(
                "shortLeverage",
                "0",
            ),
        )
    )

    runtime_state[
        "margin_type"
    ] = margin_type

    runtime_state[
        "long_leverage"
    ] = decimal_text(
        long_leverage
    )

    runtime_state[
        "short_leverage"
    ] = decimal_text(
        short_leverage
    )

    require(
        "Symbol Configuration Was Read",
        bool(
            symbol_config
        ),
    )

    require(
        "Observed Margin Type Exists",
        bool(
            margin_type
        ),
    )

    require(
        "Observed Long Leverage Is Positive",
        long_leverage > 0,
    )

    require(
        "Observed Short Leverage Is Positive",
        short_leverage > 0,
    )

    log(
        "OBSERVED MARGIN TYPE="
        + margin_type
    )

    log(
        "OBSERVED POSITION MODE="
        + (
            separated_type
            or "<unknown>"
        )
    )

    log(
        "OBSERVED LONG LEVERAGE="
        + decimal_text(
            long_leverage
        )
        + "x"
    )

    log(
        "OBSERVED SHORT LEVERAGE="
        + decimal_text(
            short_leverage
        )
        + "x"
    )

    log(
        "TARGET MARGIN="
        + TARGET_MARGIN_TYPE
    )

    log(
        "TARGET LONG="
        + decimal_text(
            TARGET_LEVERAGE
        )
        + "x"
    )

    log(
        "TARGET SHORT="
        + decimal_text(
            TARGET_LEVERAGE
        )
        + "x"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 6
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 6: "
        "LIVE MARKET PRICE"
    )

    market_price = (
        read_market_price()
    )

    runtime_state[
        "market_price"
    ] = decimal_text(
        market_price
    )

    require(
        "Market Price Was Read",
        market_price is not None,
    )

    require(
        "Market Price Is Positive",
        market_price > 0,
    )

    log(
        "MARKET PRICE PATH="
        + SYMBOL_PRICE_PATH
    )

    log(
        "MARK PRICE="
        + decimal_text(
            market_price
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 7
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 7: "
        "LIVE CONTRACT INFORMATION"
    )

    exchange_info = (
        read_exchange_info()
    )

    symbol_record = (
        find_symbol_record(
            exchange_info
        )
    )

    require(
        "Exchange Information Was Read",
        exchange_info is not None,
    )

    require(
        "Symbol Contract Record Was Found",
        bool(
            symbol_record
        ),
    )

    constraints = (
        parse_contract_constraints(
            symbol_record
        )
    )

    min_qty = constraints[
        "min_qty"
    ]

    qty_step = constraints[
        "qty_step"
    ]

    price_step = constraints[
        "price_step"
    ]

    qty_precision = constraints[
        "qty_precision"
    ]

    price_precision = constraints[
        "price_precision"
    ]

    require(
        "Minimum Quantity Is Positive",
        min_qty > 0,
    )

    require(
        "Quantity Step Is Positive",
        qty_step > 0,
    )

    require(
        "Price Step Is Positive",
        price_step > 0,
    )

    log(
        "MIN ORDER QTY="
        + decimal_text(
            min_qty
        )
    )

    log(
        "QTY STEP="
        + decimal_text(
            qty_step
        )
    )

    log(
        "QTY PRECISION="
        + str(
            qty_precision
        )
    )

    log(
        "PRICE STEP="
        + decimal_text(
            price_step
        )
    )

    log(
        "PRICE PRECISION="
        + str(
            price_precision
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 8
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 8: "
        "STRATEGY BUDGET"
    )

    initial_margin_budget = (
        available_usdt
        * INITIAL_ENTRY_PERCENT
        / Decimal(
            "100"
        )
    )

    maximum_strategy_margin = (
        available_usdt
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal(
            "100"
        )
    )

    planned_initial_notional = (
        initial_margin_budget
        * TARGET_LEVERAGE
    )

    require(
        "Initial Entry Percent Is Positive",
        INITIAL_ENTRY_PERCENT > 0,
    )

    require(
        "Initial Entry Is Within Exposure Cap",
        INITIAL_ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    require(
        "Initial Entry Margin Budget Is Positive",
        initial_margin_budget > 0,
    )

    require(
        "Maximum Strategy Margin Is Positive",
        maximum_strategy_margin > 0,
    )

    require(
        "Planned Initial Notional Is Positive",
        planned_initial_notional > 0,
    )

    log(
        "INITIAL ENTRY="
        + decimal_text(
            INITIAL_ENTRY_PERCENT
        )
        + "%"
    )

    log(
        "INITIAL MARGIN BUDGET="
        + decimal_text(
            initial_margin_budget
        )
        + " USDT"
    )

    log(
        "MAX FUND EXPOSURE="
        + decimal_text(
            MAX_FUND_EXPOSURE_PERCENT
        )
        + "%"
    )

    log(
        "MAX ALLOWED STRATEGY MARGIN="
        + decimal_text(
            maximum_strategy_margin
        )
        + " USDT"
    )

    log(
        "PLANNED INITIAL NOTIONAL="
        + decimal_text(
            planned_initial_notional
        )
        + " USDT"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 9
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 9: "
        "SYNTHETIC STRATEGY DECISION"
    )

    decision = (
        build_synthetic_decision(
            open_positions
        )
    )

    runtime_state[
        "synthetic_decision"
    ] = decision.get(
        "action"
    )

    require(
        "Decision Is Synthetic",
        decision.get(
            "synthetic"
        ) is True,
    )

    require(
        "Decision Action Exists",
        bool(
            decision.get(
                "action"
            )
        ),
    )

    log(
        "DECISION="
        + canonical_json(
            decision
        )
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 10
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 10: "
        "QUANTITY CALCULATION"
    )

    raw_quantity = (
        planned_initial_notional
        / market_price
    )

    normalized_quantity = (
        normalize_quantity(
            raw_quantity,
            min_qty,
            qty_step,
        )
    )

    runtime_state[
        "synthetic_quantity"
    ] = decimal_text(
        normalized_quantity
    )

    normalized_notional = (
        normalized_quantity
        * market_price
    )

    normalized_margin = (
        normalized_notional
        / TARGET_LEVERAGE
    )

    require(
        "Raw Quantity Is Positive",
        raw_quantity > 0,
    )

    require(
        "Normalized Quantity Is Positive",
        normalized_quantity > 0,
    )

    require(
        "Normalized Quantity Meets Minimum",
        normalized_quantity >= min_qty,
    )

    require(
        "Normalized Margin Is Positive",
        normalized_margin > 0,
    )

    log(
        "RAW QUANTITY="
        + decimal_text(
            raw_quantity
        )
        + " BTC"
    )

    log(
        "NORMALIZED QUANTITY="
        + decimal_text(
            normalized_quantity
        )
        + " BTC"
    )

    log(
        "NORMALIZED NOTIONAL="
        + decimal_text(
            normalized_notional
        )
        + " USDT"
    )

    log(
        "NORMALIZED MARGIN AT "
        + decimal_text(
            TARGET_LEVERAGE
        )
        + "x="
        + decimal_text(
            normalized_margin
        )
        + " USDT"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 11
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 11: "
        "MAXIMUM STRATEGY EXPOSURE"
    )

    planned_max_strategy_percent = (
        INITIAL_ENTRY_PERCENT
        + (
            PYRAMID_SIZE_PERCENT
            * Decimal(
                MAX_PYRAMID_ADDS
            )
        )
        + (
            BACKUP_SIZE_PERCENT
            * Decimal(
                MAX_BACKUPS
            )
        )
    )

    planned_max_strategy_margin = (
        available_usdt
        * planned_max_strategy_percent
        / Decimal(
            "100"
        )
    )

    require(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    require(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3,
    )

    require(
        "Maximum Planned Strategy Margin Is Within 35%",
        planned_max_strategy_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    log(
        "MAX FUND EXPOSURE="
        + decimal_text(
            MAX_FUND_EXPOSURE_PERCENT
        )
        + "%"
    )

    log(
        "MAX ALLOWED STRATEGY MARGIN="
        + decimal_text(
            maximum_strategy_margin
        )
        + " USDT"
    )

    log(
        "PLANNED MAX STRATEGY MARGIN="
        + decimal_text(
            planned_max_strategy_margin
        )
        + " USDT"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 12
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 12: "
        "STRATEGY SAFETY TOGGLES"
    )

    require(
        "One Direction Only Is Enabled",
        ONE_DIRECTION_ONLY,
    )

    require(
        "Anti Duplicate Orders Is Enabled",
        ANTI_DUPLICATE_ORDERS,
    )

    require(
        "Trend Reversal Exit Is Enabled",
        TREND_REVERSAL_EXIT,
    )

    require(
        "Idle Pyramid Cleanup Is Enabled",
        IDLE_PYRAMID_CLEANUP,
    )

    require(
        "Signal Expiry Is Positive",
        SIGNAL_EXPIRY_SECONDS > 0,
    )

    require(
        "Loss Cooldown Is Positive",
        LOSS_COOLDOWN_SECONDS > 0,
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 13
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 13: "
        "TAKE PROFIT MODEL"
    )

    require(
        "TP1 Allocation Is 20%",
        TP1_PERCENT
        == Decimal(
            "20"
        ),
    )

    require(
        "TP2 Allocation Is 20%",
        TP2_PERCENT
        == Decimal(
            "20"
        ),
    )

    require(
        "TP3 Allocation Is 60%",
        TP3_PERCENT
        == Decimal(
            "60"
        ),
    )

    require(
        "TP Allocation Totals 100%",
        (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        )
        == Decimal(
            "100"
        ),
    )

    require(
        "TP1 Trigger Is Positive",
        TP1_TRIGGER_PERCENT > 0,
    )

    require(
        "TP2 Trigger Is Above TP1",
        TP2_TRIGGER_PERCENT
        > TP1_TRIGGER_PERCENT,
    )

    require(
        "Trailing Distance Is Positive",
        TRAILING_DISTANCE_PERCENT > 0,
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 14
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 14: "
        "LIVE STATE SNAPSHOT"
    )

    live_state = {
        "symbol": SYMBOL,
        "availableUSDT": decimal_text(
            available_usdt
        ),
        "marketPrice": decimal_text(
            market_price
        ),
        "marginType": margin_type,
        "positionMode": separated_type,
        "isolatedLongLeverage": (
            decimal_text(
                long_leverage
            )
        ),
        "isolatedShortLeverage": (
            decimal_text(
                short_leverage
            )
        ),
        "openPositionCount": len(
            open_positions
        ),
        "targetMarginType": (
            TARGET_MARGIN_TYPE
        ),
        "targetLeverage": (
            decimal_text(
                TARGET_LEVERAGE
            )
        ),
        "initialEntryPercent": (
            decimal_text(
                INITIAL_ENTRY_PERCENT
            )
        ),
        "maxExposurePercent": (
            decimal_text(
                MAX_FUND_EXPOSURE_PERCENT
            )
        ),
    }

    live_state_hash = (
        sha256_json(
            live_state
        )
    )

    require(
        "Live State Exists",
        bool(
            live_state
        ),
    )

    require(
        "Live State Hash Exists",
        len(
            live_state_hash
        )
        == 64,
    )

    log(
        "LIVE STATE="
        + canonical_json(
            live_state
        )
    )

    log(
        "LIVE STATE SHA256="
        + live_state_hash
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 15
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 15: "
        "EXACT SYNTHETIC ORDER INTENT"
    )

    intent = build_order_intent(
        decision,
        normalized_quantity,
        market_price,
        available_usdt,
    )

    if intent is None:

        require(
            "Existing Position Prevents New Synthetic Entry",
            bool(
                open_positions
            ),
        )

        log(
            "SYNTHETIC ENTRY INTENT="
            "NONE"
        )

    else:

        require(
            "Intent Is Synthetic Only",
            intent.get(
                "syntheticOnly"
            ) is True,
        )

        require(
            "Intent Forbids Transmission",
            intent.get(
                "transmissionAllowed"
            ) is False,
        )

        require(
            "Intent Forbids Network Write",
            intent.get(
                "networkWriteAllowed"
            ) is False,
        )

        require(
            "Intent Symbol Matches",
            intent.get(
                "symbol"
            )
            == SYMBOL,
        )

        require(
            "Intent Side Is BUY",
            intent.get(
                "side"
            )
            == "BUY",
        )

        require(
            "Intent Position Side Is LONG",
            intent.get(
                "positionSide"
            )
            == "LONG",
        )

        require(
            "Intent Type Is MARKET",
            intent.get(
                "type"
            )
            == "MARKET",
        )

        require(
            "Intent Quantity Matches Normalized Quantity",
            intent.get(
                "quantity"
            )
            == decimal_text(
                normalized_quantity
            ),
        )

        log(
            "SYNTHETIC INTENT="
            + canonical_json(
                intent
            )
        )

        log(
            "SYNTHETIC INTENT SHA256="
            + sha256_json(
                intent
            )
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 16
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 16: "
        "EXACT SYNTHETIC PAYLOAD"
    )

    payload = build_synthetic_payload(
        intent
    )

    if payload is None:

        require(
            "No Payload Exists Without Entry Intent",
            intent is None,
        )

        log(
            "SYNTHETIC PAYLOAD=NONE"
        )

    else:

        payload_hash = (
            sha256_json(
                payload
            )
        )

        runtime_state[
            "synthetic_payload_hash"
        ] = payload_hash

        require(
            "Payload Symbol Matches Intent",
            payload.get(
                "symbol"
            )
            == intent.get(
                "symbol"
            ),
        )

        require(
            "Payload Side Matches Intent",
            payload.get(
                "side"
            )
            == intent.get(
                "side"
            ),
        )

        require(
            "Payload Position Side Matches Intent",
            payload.get(
                "positionSide"
            )
            == intent.get(
                "positionSide"
            ),
        )

        require(
            "Payload Type Matches Intent",
            payload.get(
                "type"
            )
            == intent.get(
                "type"
            ),
        )

        require(
            "Payload Quantity Matches Intent",
            payload.get(
                "quantity"
            )
            == intent.get(
                "quantity"
            ),
        )

        require(
            "Payload Client Order ID Matches Intent",
            payload.get(
                "newClientOrderId"
            )
            == intent.get(
                "newClientOrderId"
            ),
        )

        require(
            "Payload Hash Exists",
            len(
                payload_hash
            )
            == 64,
        )

        log(
            "SYNTHETIC PAYLOAD="
            + canonical_json(
                payload
            )
        )

        log(
            "SYNTHETIC PAYLOAD SHA256="
            + payload_hash
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 17
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 17: "
        "SYNTHETIC AUTHENTICATED EXECUTION ENVELOPE"
    )

    envelope = (
        build_synthetic_envelope(
            live_state,
            decision,
            intent,
            payload,
        )
    )

    require(
        "Envelope Is Synthetic Only",
        envelope.get(
            "syntheticOnly"
        ) is True,
    )

    require(
        "Envelope Forbids Transmission",
        envelope.get(
            "transmissionAllowed"
        ) is False,
    )

    require(
        "Envelope Forbids Network Write",
        envelope.get(
            "networkWriteAllowed"
        ) is False,
    )

    require(
        "Envelope Binds Exact Live State",
        (
            envelope[
                "bindings"
            ][
                "liveStateSHA256"
            ]
            == sha256_json(
                live_state
            )
        ),
    )

    require(
        "Envelope Binds Exact Decision",
        (
            envelope[
                "bindings"
            ][
                "decisionSHA256"
            ]
            == sha256_json(
                decision
            )
        ),
    )

    if intent:

        require(
            "Envelope Binds Exact Intent",
            (
                envelope[
                    "bindings"
                ][
                    "intentSHA256"
                ]
                == sha256_json(
                    intent
                )
            ),
        )

    if payload:

        require(
            "Envelope Binds Exact Payload",
            (
                envelope[
                    "bindings"
                ][
                    "payloadSHA256"
                ]
                == sha256_json(
                    payload
                )
            ),
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 18
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 18: "
        "SYNTHETIC TRANSPORT"
    )

    if payload is not None:

        receipt = synthetic_dispatch(
            envelope
        )

        require(
            "Synthetic Dispatch Is Synthetic Only",
            receipt.get(
                "syntheticOnly"
            ) is True,
        )

        require(
            "Synthetic Dispatch Was Not Transmitted",
            receipt.get(
                "transmitted"
            ) is False,
        )

        require(
            "Synthetic Dispatch Performed No Network Write",
            receipt.get(
                "networkWriteOccurred"
            ) is False,
        )

        require(
            "Synthetic Receipt Binds Payload Hash",
            receipt.get(
                "payloadSHA256"
            )
            == sha256_json(
                payload
            ),
        )

        log(
            "SYNTHETIC RECEIPT="
            + canonical_json(
                receipt
            )
        )

    else:

        require(
            "No Synthetic Dispatch Required",
            intent is None,
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 19
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 19: "
        "FINAL WRITE FIREBREAK"
    )

    require(
        "Network Write Count Remains Zero",
        network_write_count == 0,
    )

    require(
        "Real Order Count Remains Zero",
        real_order_count == 0,
    )

    require(
        "Demo Order Count Remains Zero",
        demo_order_count == 0,
    )

    require(
        "Leverage Mutation Count Remains Zero",
        leverage_mutation_count == 0,
    )

    require(
        "Margin Mutation Count Remains Zero",
        margin_mutation_count == 0,
    )

    require(
        "Position Mutation Count Remains Zero",
        position_mutation_count == 0,
    )

    require(
        "Account Mutation Count Remains Zero",
        account_mutation_count == 0,
    )

    require(
        "Authenticated Transport Used GET Only",
        authenticated_get_count >= 3,
    )

    require(
        "Public Transport Used GET Only",
        public_get_count >= 2,
    )

    # ----------------------------------------------------------------------------------------------
    # COMPLETE
    # ----------------------------------------------------------------------------------------------

    runtime_state[
        "phase"
    ] = "LIVE_READ_ONLY_VALIDATED"

    runtime_state[
        "validation_complete"
    ] = True

    runtime_state[
        "validation_passed"
    ] = True

    banner(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        "AUTHENTICATED GETS="
        + str(
            authenticated_get_count
        )
    )

    log(
        "PUBLIC GETS="
        + str(
            public_get_count
        )
    )

    log(
        "NETWORK WRITES="
        + str(
            network_write_count
        )
    )

    log(
        "REAL ORDERS="
        + str(
            real_order_count
        )
    )

    log(
        "DEMO ORDERS="
        + str(
            demo_order_count
        )
    )

    log(
        "SYNTHETIC DISPATCHES="
        + str(
            synthetic_dispatch_count
        )
    )

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO ACCOUNT MUTATION WAS SENT"
    )


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================


def heartbeat_loop():
    heartbeat = 0

    while True:

        time.sleep(
            30
        )

        heartbeat += 1

        log(
            "HEARTBEAT "
            + str(
                heartbeat
            )
            + " | phase="
            + str(
                runtime_state.get(
                    "phase"
                )
            )
            + " | authenticated-read-only="
            + str(
                AUTHENTICATED_READ_ONLY
            )
            + " | authenticated-get="
            + str(
                authenticated_get_count
            )
            + " | public-get="
            + str(
                public_get_count
            )
            + " | network-writes="
            + str(
                network_write_count
            )
            + " | real-orders="
            + str(
                real_order_count
            )
            + " | demo-orders="
            + str(
                demo_order_count
            )
            + " | synthetic-dispatches="
            + str(
                synthetic_dispatch_count
            )
        )


# ==================================================================================================
# MAIN
# ==================================================================================================


def main():
    banner(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(
        "SYMBOL="
        + SYMBOL
    )

    log(
        "VERSION="
        + VERSION
    )

    log(
        "HEALTH PORT="
        + str(
            HEALTH_PORT
        )
    )

    log(
        "AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        "PUBLIC READ-ONLY ENABLED"
    )

    log(
        "NETWORK WRITES DISABLED"
    )

    log(
        "REAL ORDER EXECUTION DISABLED"
    )

    log(
        "DEMO ORDER EXECUTION DISABLED"
    )

    log(
        "LEVERAGE MUTATION DISABLED"
    )

    log(
        "MARGIN MUTATION DISABLED"
    )

    log(
        "POSITION MUTATION DISABLED"
    )

    log(
        "ACCOUNT MUTATION DISABLED"
    )

    start_health_server()

    try:

        run_validation()

    except Exception as exc:

        runtime_state[
            "phase"
        ] = "VALIDATION_FAILED"

        runtime_state[
            "validation_complete"
        ] = True

        runtime_state[
            "validation_passed"
        ] = False

        runtime_state[
            "last_error"
        ] = (
            type(
                exc
            ).__name__
            + ": "
            + str(
                exc
            )
        )

        banner(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            "ERROR="
            + type(
                exc
            ).__name__
            + ": "
            + str(
                exc
            )
        )

        traceback.print_exc()

        print(
            LINE,
            flush=True,
        )

        log(
            "NETWORK WRITES="
            + str(
                network_write_count
            )
        )

        log(
            "REAL ORDERS="
            + str(
                real_order_count
            )
        )

        log(
            "DEMO ORDERS="
            + str(
                demo_order_count
            )
        )

        log(
            "SYNTHETIC DISPATCHES="
            + str(
                synthetic_dispatch_count
            )
        )

        log(
            "NO REAL ORDER WAS SENT"
        )

        log(
            "NO ACCOUNT MUTATION WAS SENT"
        )

    heartbeat_loop()


# ==================================================================================================
# ENTRYPOINT
# ==================================================================================================


if __name__ == "__main__":
    main()
