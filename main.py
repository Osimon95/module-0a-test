import os
import sys
import json
import time
import hmac
import hashlib
import base64
import threading
import urllib.request
import urllib.error
from decimal import Decimal, InvalidOperation, ROUND_UP
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# R34L
# LIVE READ-ONLY MARKET PRICE CORRECTION + EXECUTION PRECONDITION RECONCILIATION
#
# IMPORTANT:
# - AUTHENTICATED GETS ARE ALLOWED.
# - PUBLIC GETS ARE ALLOWED.
# - ALL NETWORK WRITES ARE DISABLED.
# - REAL ORDER EXECUTION IS DISABLED.
# - DEMO ORDER EXECUTION IS DISABLED.
# - LEVERAGE MUTATION IS DISABLED.
# - MARGIN MUTATION IS DISABLED.
# - POSITION MUTATION IS DISABLED.
# - ACCOUNT MUTATION IS DISABLED.
#
# R34L PURPOSE:
# 1. Preserve the successful R32K/R34-series authenticated account reconciliation.
# 2. Correct the public BTCUSDT contract market-price reader.
# 3. Use:
#       GET /capi/v3/market/symbolPrice?symbol=BTCUSDT&priceType=MARK
# 4. Require a successful public GET.
# 5. Require market_price > 0.
# 6. Bind market-price readiness into final execution-precondition readiness.
# 7. KEEP ALL EXCHANGE WRITES HARD-DISABLED.
# ==================================================================================================


VERSION = "R34L"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", "10000"))

TARGET_MARGIN = "ISOLATED"
TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

REQUEST_TIMEOUT_SECONDS = 15
HEARTBEAT_SECONDS = 30


# ==================================================================================================
# HARD SAFETY CONFIGURATION
# ==================================================================================================

AUTHENTICATED_READ_ONLY_ENABLED = True
PUBLIC_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# ==================================================================================================
# GLOBAL RUNTIME STATE
# ==================================================================================================

runtime = {
    "phase": "BOOTING",

    "authenticated_get_count": 0,
    "public_get_count": 0,

    "network_writes": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "real_orders": 0,
    "demo_orders": 0,

    "available_usdt": None,
    "total_position_records": None,
    "symbol_position_records": None,
    "active_positions": None,

    "observed_margin": None,
    "observed_position_mode": None,
    "observed_cross_leverage": None,
    "observed_long_leverage": None,
    "observed_short_leverage": None,

    "market_price": None,
    "market_price_time": None,
    "market_price_path": None,
    "market_price_ready": False,

    "initial_margin_budget": None,
    "initial_notional_target": None,
    "maximum_exposure_budget": None,

    "credentials_ready": False,
    "balance_ready": False,
    "positions_ready": False,
    "margin_ready": False,
    "leverage_ready": False,
    "strategy_budget_ready": False,
    "strategy_parameters_ready": False,
    "write_firebreak_ready": False,
    "execution_preconditions_ready": False,

    "final_validation_status": "UNKNOWN",
    "heartbeat": 0,
}


# ==================================================================================================
# LOGGING
# ==================================================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def banner(message):
    log(LINE)
    log(message)
    log(LINE)


def pass_fail(description, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    log(f"{description:<86} {status}")
    return bool(condition)


# ==================================================================================================
# DECIMAL HELPERS
# ==================================================================================================

def to_decimal(value, default=None):
    if value is None:
        return default

    if isinstance(value, Decimal):
        return value

    try:
        text = str(value).strip()

        if text == "":
            return default

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return default


def decimal_text(value):
    if value is None:
        return "None"

    if not isinstance(value, Decimal):
        value = to_decimal(value)

    if value is None:
        return "None"

    result = format(value, "f")

    if "." in result:
        result = result.rstrip("0").rstrip(".")

    return result


def leverage_text(value):
    decimal_value = to_decimal(value)

    if decimal_value is None:
        return "None"

    return f"{decimal_text(decimal_value)}x"


# ==================================================================================================
# ENVIRONMENT CREDENTIALS
# ==================================================================================================

def read_env_first(*names):
    for name in names:
        value = os.getenv(name)

        if value is not None:
            value = value.strip()

            if value:
                return value

    return ""


WEEX_API_KEY = read_env_first(
    "WEEX_API_KEY",
    "API_KEY",
)

WEEX_API_SECRET = read_env_first(
    "WEEX_API_SECRET",
    "API_SECRET",
)

WEEX_API_PASSPHRASE = read_env_first(
    "WEEX_API_PASSPHRASE",
    "WEEX_PASSPHRASE",
    "API_PASSPHRASE",
)


# ==================================================================================================
# HTTP HELPERS
# ==================================================================================================

def decode_json_response(raw_bytes):
    text = raw_bytes.decode("utf-8", errors="replace").strip()

    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"WEEX returned non-JSON response: {text[:500]}"
        )


def public_get(path):
    """
    Public read-only GET.

    There is deliberately no generic HTTP method argument here.
    This helper can ONLY issue GET requests.
    """

    if not PUBLIC_READ_ONLY_ENABLED:
        raise RuntimeError("Public read-only access is disabled.")

    if not path.startswith("/"):
        raise RuntimeError("Public GET path must begin with '/'.")

    url = BASE_URL + path

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-read-only-validator",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read()

            if response.status < 200 or response.status >= 300:
                raise RuntimeError(
                    f"Public GET failed HTTP {response.status}"
                )

            payload = decode_json_response(raw)

            runtime["public_get_count"] += 1

            return payload

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Public GET HTTP {exc.code}: {body[:700]}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Public GET transport error: {exc}"
        ) from exc


def make_signature(timestamp, method, request_path, body=""):
    """
    WEEX authenticated request signature.

    Canonical prehash:
        timestamp + method + request_path + body

    Signature:
        Base64(HMAC_SHA256(secret, prehash))
    """

    method = method.upper()

    prehash = (
        str(timestamp)
        + method
        + request_path
        + body
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def authenticated_get(path):
    """
    Authenticated read-only GET.

    This function has no POST/PUT/PATCH/DELETE capability.
    """

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only access is disabled."
        )

    if not WEEX_API_KEY:
        raise RuntimeError("Missing WEEX_API_KEY.")

    if not WEEX_API_SECRET:
        raise RuntimeError("Missing WEEX_API_SECRET.")

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError("Missing WEEX_API_PASSPHRASE.")

    if not path.startswith("/"):
        raise RuntimeError(
            "Authenticated GET path must begin with '/'."
        )

    timestamp = str(int(time.time() * 1000))

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        body="",
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"{VERSION}-read-only-validator",
    }

    request = urllib.request.Request(
        url=BASE_URL + path,
        method="GET",
        headers=headers,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read()

            if response.status < 200 or response.status >= 300:
                raise RuntimeError(
                    f"Authenticated GET failed HTTP "
                    f"{response.status}"
                )

            payload = decode_json_response(raw)

            runtime["authenticated_get_count"] += 1

            return payload

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Authenticated GET HTTP {exc.code}: "
            f"{body[:700]}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Authenticated GET transport error: {exc}"
        ) from exc


# ==================================================================================================
# RESPONSE NORMALIZATION
# ==================================================================================================

def unwrap_data(payload):
    """
    Handles both:
        {"data": ...}

    and raw V3 responses:
        {...}
        [...]
    """

    if isinstance(payload, dict) and "data" in payload:
        return payload.get("data")

    return payload


def find_dict_for_symbol(payload, symbol):
    data = unwrap_data(payload)

    if isinstance(data, dict):

        data_symbol = str(
            data.get("symbol", "")
        ).upper()

        if not data_symbol or data_symbol == symbol:
            return data

        for key in (
            "list",
            "rows",
            "result",
            "symbols",
        ):
            nested = data.get(key)

            found = find_dict_for_symbol(
                nested,
                symbol,
            )

            if found is not None:
                return found

    if isinstance(data, list):

        for item in data:

            if not isinstance(item, dict):
                continue

            item_symbol = str(
                item.get("symbol", "")
            ).upper()

            if item_symbol == symbol:
                return item

        if len(data) == 1 and isinstance(data[0], dict):
            return data[0]

    return None


def normalize_position_records(payload):
    data = unwrap_data(payload)

    if data is None:
        return []

    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, dict):

        for key in (
            "list",
            "rows",
            "positions",
            "result",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return [
                    item
                    for item in value
                    if isinstance(item, dict)
                ]

        # If a single position object was returned.
        if "symbol" in data:
            return [data]

    return []


# ==================================================================================================
# READ-ONLY ACCOUNT FUNCTIONS
# ==================================================================================================

def obtain_available_balance():
    paths = [
        "/capi/v3/account/balance",
    ]

    last_error = None

    for path in paths:

        try:
            payload = authenticated_get(path)
            data = unwrap_data(payload)

            candidates = []

            if isinstance(data, dict):

                candidates.append(data)

                for key in (
                    "balances",
                    "assets",
                    "list",
                    "rows",
                ):
                    value = data.get(key)

                    if isinstance(value, list):
                        candidates.extend(
                            item
                            for item in value
                            if isinstance(item, dict)
                        )

            elif isinstance(data, list):
                candidates.extend(
                    item
                    for item in data
                    if isinstance(item, dict)
                )

            for item in candidates:

                asset = str(
                    item.get(
                        "asset",
                        item.get(
                            "coin",
                            item.get("currency", ""),
                        ),
                    )
                ).upper()

                if asset and asset != "USDT":
                    continue

                for field in (
                    "available",
                    "availableBalance",
                    "availableAmount",
                    "availableEquity",
                    "balance",
                ):

                    value = to_decimal(
                        item.get(field)
                    )

                    if value is not None:
                        return path, value

            # Some endpoint versions may return a direct balance object.
            if isinstance(data, dict):

                for field in (
                    "available",
                    "availableBalance",
                    "availableAmount",
                    "availableEquity",
                    "balance",
                ):

                    value = to_decimal(
                        data.get(field)
                    )

                    if value is not None:
                        return path, value

        except Exception as exc:
            last_error = exc

    if last_error is not None:
        raise RuntimeError(
            f"Unable to obtain available balance: "
            f"{last_error}"
        )

    raise RuntimeError(
        "Unable to locate available USDT balance "
        "in WEEX response."
    )


def obtain_positions():
    path = "/capi/v3/account/position/allPosition"

    payload = authenticated_get(path)

    records = normalize_position_records(payload)

    symbol_records = []

    for record in records:

        record_symbol = str(
            record.get("symbol", "")
        ).upper()

        if record_symbol == SYMBOL:
            symbol_records.append(record)

    active = []

    for record in symbol_records:

        quantity = None

        for field in (
            "positionAmt",
            "positionAmount",
            "size",
            "qty",
            "quantity",
            "total",
            "available",
        ):

            if field in record:
                quantity = to_decimal(
                    record.get(field)
                )

                if quantity is not None:
                    break

        if quantity is None:
            # If WEEX returned a symbol position object but no recognizable
            # size field, do not incorrectly treat it as active.
            continue

        if abs(quantity) > Decimal("0"):
            active.append(record)

    return (
        path,
        records,
        symbol_records,
        active,
    )


def obtain_symbol_configuration():
    path = (
        "/capi/v3/account/symbolConfig"
        f"?symbol={SYMBOL}"
    )

    payload = authenticated_get(path)

    item = find_dict_for_symbol(
        payload,
        SYMBOL,
    )

    if item is None:
        raise RuntimeError(
            "BTCUSDT symbol configuration was not found."
        )

    margin = item.get(
        "marginType",
        item.get(
            "marginMode",
            item.get("margin", None),
        ),
    )

    position_mode = item.get(
        "positionMode",
        item.get(
            "holdMode",
            item.get("positionType", None),
        ),
    )

    cross_leverage = to_decimal(
        item.get(
            "crossLeverage",
            item.get(
                "crossMarginLeverage",
                item.get("leverage", None),
            ),
        )
    )

    long_leverage = to_decimal(
        item.get(
            "isolatedLongLeverage",
            item.get(
                "longLeverage",
                item.get(
                    "buyLeverage",
                    None,
                ),
            ),
        )
    )

    short_leverage = to_decimal(
        item.get(
            "isolatedShortLeverage",
            item.get(
                "shortLeverage",
                item.get(
                    "sellLeverage",
                    None,
                ),
            ),
        )
    )

    observed_symbol = str(
        item.get("symbol", SYMBOL)
    ).upper()

    return {
        "path": path,
        "raw": item,
        "symbol": observed_symbol,
        "margin": (
            str(margin).upper()
            if margin is not None
            else None
        ),
        "position_mode": position_mode,
        "cross_leverage": cross_leverage,
        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
    }


# ==================================================================================================
# R34L CORRECTED PUBLIC MARKET PRICE READER
# ==================================================================================================

def obtain_mark_price():
    """
    R34L corrected market-price implementation.

    Official WEEX contract endpoint:

        GET /capi/v3/market/symbolPrice
            ?symbol=BTCUSDT
            &priceType=MARK

    Expected V3 response:

        {
            "symbol": "BTCUSDT",
            "price": "...",
            "time": ...
        }

    The parser is deliberately tolerant of a response wrapped inside
    {"data": ...} in case the transport returns an envelope.
    """

    path = (
        "/capi/v3/market/symbolPrice"
        f"?symbol={SYMBOL}"
        "&priceType=MARK"
    )

    payload = public_get(path)

    item = find_dict_for_symbol(
        payload,
        SYMBOL,
    )

    if item is None:
        raise RuntimeError(
            "Market-price response did not contain "
            f"a {SYMBOL} record."
        )

    response_symbol = str(
        item.get("symbol", "")
    ).upper()

    if response_symbol and response_symbol != SYMBOL:
        raise RuntimeError(
            "Market-price response symbol mismatch: "
            f"expected={SYMBOL} "
            f"received={response_symbol}"
        )

    price = to_decimal(
        item.get("price")
    )

    # Defensive fallback only.
    if price is None:
        price = to_decimal(
            item.get("markPrice")
        )

    if price is None:
        raise RuntimeError(
            "Market-price response contained no "
            "numeric price field."
        )

    if price <= Decimal("0"):
        raise RuntimeError(
            f"Invalid non-positive market price: {price}"
        )

    market_time = item.get(
        "time",
        item.get(
            "timestamp",
            item.get("ts", None),
        ),
    )

    return path, price, market_time


# ==================================================================================================
# HARD WRITE FIREBREAK
# ==================================================================================================

def authenticated_post(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY FIREBREAK: "
        "authenticated POST is disabled."
    )


def place_real_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY FIREBREAK: "
        "real order execution is disabled."
    )


def place_demo_order(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY FIREBREAK: "
        "demo order execution is disabled."
    )


def change_leverage(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY FIREBREAK: "
        "leverage mutation is disabled."
    )


def change_margin(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY FIREBREAK: "
        "margin mutation is disabled."
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY FIREBREAK: "
        "position mutation is disabled."
    )


def mutate_account(*args, **kwargs):
    raise RuntimeError(
        f"{VERSION} SAFETY FIREBREAK: "
        "account mutation is disabled."
    )


# ==================================================================================================
# FIREBREAK TEST HELPER
# ==================================================================================================

def locally_rejected(function):
    try:
        function()
    except RuntimeError:
        return True
    except Exception:
        return True

    return False


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps(
            {
                "status": "ok",
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": runtime["phase"],
                "authenticated_read_only": (
                    AUTHENTICATED_READ_ONLY_ENABLED
                ),
                "public_read_only": (
                    PUBLIC_READ_ONLY_ENABLED
                ),
                "real_execution": (
                    REAL_ORDER_EXECUTION_ENABLED
                ),
                "demo_execution": (
                    DEMO_ORDER_EXECUTION_ENABLED
                ),
                "network_writes_enabled": (
                    EXCHANGE_NETWORK_WRITES_ENABLED
                ),
                "authenticated_get_count": (
                    runtime["authenticated_get_count"]
                ),
                "public_get_count": (
                    runtime["public_get_count"]
                ),
                "available_usdt": (
                    decimal_text(
                        runtime["available_usdt"]
                    )
                ),
                "active_positions": (
                    runtime["active_positions"]
                ),
                "observed_margin": (
                    runtime["observed_margin"]
                ),
                "observed_long_leverage": (
                    decimal_text(
                        runtime[
                            "observed_long_leverage"
                        ]
                    )
                ),
                "observed_short_leverage": (
                    decimal_text(
                        runtime[
                            "observed_short_leverage"
                        ]
                    )
                ),
                "market_price": (
                    decimal_text(
                        runtime["market_price"]
                    )
                ),
                "market_price_ready": (
                    runtime["market_price_ready"]
                ),
                "execution_preconditions_ready": (
                    runtime[
                        "execution_preconditions_ready"
                    ]
                ),
                "network_writes": (
                    runtime["network_writes"]
                ),
                "real_orders": (
                    runtime["real_orders"]
                ),
                "demo_orders": (
                    runtime["demo_orders"]
                ),
            },
            separators=(",", ":"),
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    return server


# ==================================================================================================
# TEST 1
# ==================================================================================================

def test_safety_configuration():
    banner(f"{VERSION} TEST 1: SAFETY CONFIGURATION")

    results = [
        pass_fail(
            "Authenticated Read-Only Is Enabled",
            AUTHENTICATED_READ_ONLY_ENABLED is True,
        ),
        pass_fail(
            "Public Read-Only Is Enabled",
            PUBLIC_READ_ONLY_ENABLED is True,
        ),
        pass_fail(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION_ENABLED is False,
        ),
        pass_fail(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION_ENABLED is False,
        ),
        pass_fail(
            "Exchange Network Writes Are Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED is False,
        ),
        pass_fail(
            "Leverage Mutation Is Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        ),
        pass_fail(
            "Margin Mutation Is Disabled",
            MARGIN_MUTATION_ENABLED is False,
        ),
        pass_fail(
            "Position Mutation Is Disabled",
            POSITION_MUTATION_ENABLED is False,
        ),
        pass_fail(
            "Account Mutation Is Disabled",
            ACCOUNT_MUTATION_ENABLED is False,
        ),
    ]

    return all(results)


# ==================================================================================================
# TEST 2
# ==================================================================================================

def test_credentials():
    banner(
        f"{VERSION} TEST 2: "
        "AUTHENTICATED READ-ONLY CREDENTIALS"
    )

    key_ready = bool(WEEX_API_KEY)
    secret_ready = bool(WEEX_API_SECRET)
    passphrase_ready = bool(WEEX_API_PASSPHRASE)

    results = [
        pass_fail(
            "WEEX API Key Is Present",
            key_ready,
        ),
        pass_fail(
            "WEEX API Secret Is Present",
            secret_ready,
        ),
        pass_fail(
            "WEEX API Passphrase Is Present",
            passphrase_ready,
        ),
    ]

    runtime["credentials_ready"] = all(results)

    return runtime["credentials_ready"]


# ==================================================================================================
# TEST 3
# ==================================================================================================

def test_balance():
    banner(
        f"{VERSION} TEST 3: "
        "LIVE BALANCE RECONCILIATION"
    )

    path = None
    balance = None

    try:
        path, balance = obtain_available_balance()

        log(
            f"{VERSION}: BALANCE PATH={path}"
        )

        log(
            f"{VERSION}: AVAILABLE USDT="
            f"{decimal_text(balance)}"
        )

    except Exception as exc:
        log(
            f"{VERSION}: BALANCE READ ERROR={exc}"
        )

    runtime["available_usdt"] = balance

    read_ok = balance is not None
    positive = (
        balance is not None
        and balance > Decimal("0")
    )

    results = [
        pass_fail(
            "Available Balance Was Read",
            read_ok,
        ),
        pass_fail(
            "Available Balance Is Positive",
            positive,
        ),
    ]

    runtime["balance_ready"] = all(results)

    return runtime["balance_ready"]


# ==================================================================================================
# TEST 4
# ==================================================================================================

def test_positions():
    banner(
        f"{VERSION} TEST 4: "
        "POSITION RECONCILIATION"
    )

    path = None
    records = None
    symbol_records = None
    active = None

    try:
        (
            path,
            records,
            symbol_records,
            active,
        ) = obtain_positions()

        log(
            f"{VERSION}: POSITION PATH={path}"
        )

        log(
            f"{VERSION}: TOTAL POSITION RECORDS="
            f"{len(records)}"
        )

        log(
            f"{VERSION}: {SYMBOL} POSITION RECORDS="
            f"{len(symbol_records)}"
        )

        log(
            f"{VERSION}: {SYMBOL} ACTIVE POSITIONS="
            f"{len(active)}"
        )

    except Exception as exc:
        log(
            f"{VERSION}: POSITION READ ERROR={exc}"
        )

    runtime["total_position_records"] = (
        len(records)
        if records is not None
        else None
    )

    runtime["symbol_position_records"] = (
        len(symbol_records)
        if symbol_records is not None
        else None
    )

    runtime["active_positions"] = (
        len(active)
        if active is not None
        else None
    )

    endpoint_read = records is not None
    reconciled = active is not None
    symbol_reconciled = symbol_records is not None
    zero_positions = (
        active is not None
        and len(active) == 0
    )

    results = [
        pass_fail(
            "Position Endpoint Was Read",
            endpoint_read,
        ),
        pass_fail(
            "Position Response Is Reconciled",
            reconciled,
        ),
        pass_fail(
            f"{SYMBOL} Position State Was Reconciled",
            symbol_reconciled,
        ),
        pass_fail(
            "Zero Open Positions Is Accepted As Valid State",
            zero_positions,
        ),
    ]

    runtime["positions_ready"] = all(results)

    return runtime["positions_ready"]


# ==================================================================================================
# TEST 5
# ==================================================================================================

def test_symbol_configuration():
    banner(
        f"{VERSION} TEST 5: "
        "SYMBOL CONFIGURATION READ-BACK"
    )

    config = None

    try:
        config = obtain_symbol_configuration()

        runtime["observed_margin"] = (
            config["margin"]
        )

        runtime["observed_position_mode"] = (
            config["position_mode"]
        )

        runtime["observed_cross_leverage"] = (
            config["cross_leverage"]
        )

        runtime["observed_long_leverage"] = (
            config["long_leverage"]
        )

        runtime["observed_short_leverage"] = (
            config["short_leverage"]
        )

        log(
            f"{VERSION}: SYMBOL CONFIG PATH="
            f"{config['path']}"
        )

        log(
            f"{VERSION}: OBSERVED MARGIN="
            f"{config['margin']}"
        )

        log(
            f"{VERSION}: OBSERVED POSITION MODE="
            f"{config['position_mode']}"
        )

        log(
            f"{VERSION}: OBSERVED CROSS LEVERAGE="
            f"{leverage_text(config['cross_leverage'])}"
        )

        log(
            f"{VERSION}: OBSERVED ISOLATED LONG="
            f"{leverage_text(config['long_leverage'])}"
        )

        log(
            f"{VERSION}: OBSERVED ISOLATED SHORT="
            f"{leverage_text(config['short_leverage'])}"
        )

    except Exception as exc:
        log(
            f"{VERSION}: SYMBOL CONFIG ERROR={exc}"
        )

    config_read = config is not None

    symbol_ok = (
        config is not None
        and config["symbol"] == SYMBOL
    )

    margin_ok = (
        config is not None
        and config["margin"] == TARGET_MARGIN
    )

    long_ok = (
        config is not None
        and config["long_leverage"]
        == TARGET_LONG_LEVERAGE
    )

    short_ok = (
        config is not None
        and config["short_leverage"]
        == TARGET_SHORT_LEVERAGE
    )

    results = [
        pass_fail(
            "Symbol Configuration Was Read",
            config_read,
        ),
        pass_fail(
            f"Configuration Belongs To {SYMBOL}",
            symbol_ok,
        ),
        pass_fail(
            f"Margin Type Is {TARGET_MARGIN}",
            margin_ok,
        ),
        pass_fail(
            "Isolated Long Leverage Is 100x",
            long_ok,
        ),
        pass_fail(
            "Isolated Short Leverage Is 100x",
            short_ok,
        ),
    ]

    runtime["margin_ready"] = margin_ok
    runtime["leverage_ready"] = (
        long_ok and short_ok
    )

    return all(results)


# ==================================================================================================
# TEST 6 -- R34L CORRECTION
# ==================================================================================================

def test_public_market_price():
    banner(
        f"{VERSION} TEST 6: "
        "CORRECTED PUBLIC CONTRACT MARKET PRICE"
    )

    path = None
    price = None
    market_time = None

    public_before = runtime["public_get_count"]

    try:
        (
            path,
            price,
            market_time,
        ) = obtain_mark_price()

        runtime["market_price_path"] = path
        runtime["market_price"] = price
        runtime["market_price_time"] = market_time

        log(
            f"{VERSION}: MARKET PRICE PATH={path}"
        )

        log(
            f"{VERSION}: MARKET PRICE="
            f"{decimal_text(price)}"
        )

        log(
            f"{VERSION}: MARKET PRICE TIME="
            f"{market_time}"
        )

    except Exception as exc:

        runtime["market_price"] = None
        runtime["market_price_time"] = None

        log(
            f"{VERSION}: MARKET PRICE=UNAVAILABLE"
        )

        log(
            f"{VERSION}: MARKET PRICE ERROR={exc}"
        )

    public_after = runtime["public_get_count"]

    endpoint_read = (
        public_after > public_before
    )

    price_read = (
        price is not None
    )

    price_positive = (
        price is not None
        and price > Decimal("0")
    )

    public_count_positive = (
        runtime["public_get_count"] >= 1
    )

    results = [
        pass_fail(
            "Correct Contract Market Price Endpoint Was Read",
            endpoint_read,
        ),
        pass_fail(
            "Public GET Count Increased",
            public_after > public_before,
        ),
        pass_fail(
            "Public GET Count Is At Least One",
            public_count_positive,
        ),
        pass_fail(
            "BTCUSDT Market Price Was Read",
            price_read,
        ),
        pass_fail(
            "BTCUSDT Market Price Is Positive",
            price_positive,
        ),
    ]

    runtime["market_price_ready"] = all(results)

    return runtime["market_price_ready"]


# ==================================================================================================
# TEST 7
# ==================================================================================================

def test_strategy_budget():
    banner(
        f"{VERSION} TEST 7: "
        "STRATEGY BUDGET RECONCILIATION"
    )

    balance = runtime["available_usdt"]

    if balance is None:
        initial_margin_budget = None
        initial_notional = None
        max_exposure_budget = None

    else:
        initial_margin_budget = (
            balance
            * INITIAL_ENTRY_PERCENT
            / Decimal("100")
        )

        initial_notional = (
            initial_margin_budget
            * TARGET_LONG_LEVERAGE
        )

        max_exposure_budget = (
            balance
            * MAX_FUND_EXPOSURE_PERCENT
            / Decimal("100")
        )

    runtime["initial_margin_budget"] = (
        initial_margin_budget
    )

    runtime["initial_notional_target"] = (
        initial_notional
    )

    runtime["maximum_exposure_budget"] = (
        max_exposure_budget
    )

    log(
        f"{VERSION}: AVAILABLE BALANCE="
        f"{decimal_text(balance)} USDT"
    )

    log(
        f"{VERSION}: INITIAL ENTRY PERCENT="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: INITIAL MARGIN BUDGET="
        f"{decimal_text(initial_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: TARGET INITIAL NOTIONAL AT 100x="
        f"{decimal_text(initial_notional)} USDT"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE PERCENT="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE BUDGET="
        f"{decimal_text(max_exposure_budget)} USDT"
    )

    initial_percent_ok = (
        INITIAL_ENTRY_PERCENT == Decimal("5")
    )

    max_percent_ok = (
        MAX_FUND_EXPOSURE_PERCENT
        == Decimal("35")
    )

    initial_positive = (
        initial_margin_budget is not None
        and initial_margin_budget > Decimal("0")
    )

    max_positive = (
        max_exposure_budget is not None
        and max_exposure_budget > Decimal("0")
    )

    initial_below_max = (
        initial_margin_budget is not None
        and max_exposure_budget is not None
        and initial_margin_budget
        < max_exposure_budget
    )

    results = [
        pass_fail(
            "Initial Entry Percent Is 5%",
            initial_percent_ok,
        ),
        pass_fail(
            "Maximum Fund Exposure Is 35%",
            max_percent_ok,
        ),
        pass_fail(
            "Initial Margin Budget Is Positive",
            initial_positive,
        ),
        pass_fail(
            "Maximum Exposure Budget Is Positive",
            max_positive,
        ),
        pass_fail(
            "Initial Budget Is Below Maximum Exposure",
            initial_below_max,
        ),
    ]

    runtime["strategy_budget_ready"] = all(results)

    return runtime["strategy_budget_ready"]


# ==================================================================================================
# TEST 8
# ==================================================================================================

def test_strategy_parameters():
    banner(
        f"{VERSION} TEST 8: "
        "STRATEGY PARAMETER INTEGRITY"
    )

    tp_total = (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
    )

    results = [
        pass_fail(
            "Maximum Pyramid Adds Is One",
            MAX_PYRAMID_ADDS == 1,
        ),
        pass_fail(
            "Pyramid Size Is 5%",
            PYRAMID_SIZE_PERCENT
            == Decimal("5"),
        ),
        pass_fail(
            "Maximum Backups Is Three",
            MAX_BACKUPS == 3,
        ),
        pass_fail(
            "Backup Size Is 5%",
            BACKUP_SIZE_PERCENT
            == Decimal("5"),
        ),
        pass_fail(
            "Backup Buffer Is 0.3%",
            BACKUP_BUFFER_PERCENT
            == Decimal("0.3"),
        ),
        pass_fail(
            "TP Distribution Totals 100%",
            tp_total == Decimal("100"),
        ),
        pass_fail(
            "TP1 Trigger Is 0.5%",
            TP1_TRIGGER_PERCENT
            == Decimal("0.5"),
        ),
        pass_fail(
            "TP2 Trigger Is 1.0%",
            TP2_TRIGGER_PERCENT
            == Decimal("1.0"),
        ),
        pass_fail(
            "Trailing Distance Is 0.20%",
            TRAILING_DISTANCE_PERCENT
            == Decimal("0.20"),
        ),
        pass_fail(
            "Signal Expiry Is 120 Seconds",
            SIGNAL_EXPIRY_SECONDS == 120,
        ),
        pass_fail(
            "Loss Cooldown Is 300 Seconds",
            LOSS_COOLDOWN_SECONDS == 300,
        ),
    ]

    runtime["strategy_parameters_ready"] = (
        all(results)
    )

    return runtime["strategy_parameters_ready"]


# ==================================================================================================
# TEST 9
# ==================================================================================================

def test_write_firebreak():
    banner(
        f"{VERSION} TEST 9: "
        "WRITE FIREBREAK VERIFICATION"
    )

    post_blocked = locally_rejected(
        authenticated_post
    )

    real_blocked = locally_rejected(
        place_real_order
    )

    demo_blocked = locally_rejected(
        place_demo_order
    )

    leverage_blocked = locally_rejected(
        change_leverage
    )

    margin_blocked = locally_rejected(
        change_margin
    )

    position_blocked = locally_rejected(
        mutate_position
    )

    account_blocked = locally_rejected(
        mutate_account
    )

    results = [
        pass_fail(
            "Authenticated POST Is Rejected Locally",
            post_blocked,
        ),
        pass_fail(
            "Real Order Function Is Rejected Locally",
            real_blocked,
        ),
        pass_fail(
            "Demo Order Function Is Rejected Locally",
            demo_blocked,
        ),
        pass_fail(
            "Leverage Mutation Is Rejected Locally",
            leverage_blocked,
        ),
        pass_fail(
            "Margin Mutation Is Rejected Locally",
            margin_blocked,
        ),
        pass_fail(
            "Position Mutation Is Rejected Locally",
            position_blocked,
        ),
        pass_fail(
            "Account Mutation Is Rejected Locally",
            account_blocked,
        ),
        pass_fail(
            "Exchange Network Writes Remain Zero",
            runtime["network_writes"] == 0,
        ),
        pass_fail(
            "Leverage Mutations Remain Zero",
            runtime["leverage_mutations"] == 0,
        ),
        pass_fail(
            "Margin Mutations Remain Zero",
            runtime["margin_mutations"] == 0,
        ),
        pass_fail(
            "Position Mutations Remain Zero",
            runtime["position_mutations"] == 0,
        ),
        pass_fail(
            "Account Mutations Remain Zero",
            runtime["account_mutations"] == 0,
        ),
        pass_fail(
            "Real Orders Remain Zero",
            runtime["real_orders"] == 0,
        ),
        pass_fail(
            "Demo Orders Remain Zero",
            runtime["demo_orders"] == 0,
        ),
    ]

    runtime["write_firebreak_ready"] = all(
        results
    )

    return runtime["write_firebreak_ready"]


# ==================================================================================================
# TEST 10
# ==================================================================================================

def test_execution_preconditions():
    banner(
        f"{VERSION} TEST 10: "
        "EXECUTION PRECONDITION READINESS"
    )

    credentials_ready = (
        runtime["credentials_ready"]
    )

    balance_ready = (
        runtime["balance_ready"]
    )

    positions_ready = (
        runtime["positions_ready"]
        and runtime["active_positions"] == 0
    )

    margin_ready = (
        runtime["margin_ready"]
    )

    leverage_ready = (
        runtime["leverage_ready"]
    )

    # R34L IMPORTANT CHANGE:
    # Market price is now a mandatory readiness condition.
    market_price_ready = (
        runtime["market_price_ready"]
        and runtime["market_price"] is not None
        and runtime["market_price"]
        > Decimal("0")
        and runtime["public_get_count"] >= 1
    )

    budget_ready = (
        runtime["strategy_budget_ready"]
    )

    parameters_ready = (
        runtime["strategy_parameters_ready"]
    )

    firebreak_ready = (
        runtime["write_firebreak_ready"]
    )

    results = [
        pass_fail(
            "Authenticated Credentials Are Ready",
            credentials_ready,
        ),
        pass_fail(
            "Available Balance Is Ready",
            balance_ready,
        ),
        pass_fail(
            f"{SYMBOL} Has Zero Active Positions",
            positions_ready,
        ),
        pass_fail(
            "Margin Mode Is Ready",
            margin_ready,
        ),
        pass_fail(
            "100x Long And Short Leverage Are Ready",
            leverage_ready,
        ),
        pass_fail(
            "Public Market Price Is Ready",
            market_price_ready,
        ),
        pass_fail(
            "Public GET Count Is Ready",
            runtime["public_get_count"] >= 1,
        ),
        pass_fail(
            "Strategy Budget Is Ready",
            budget_ready,
        ),
        pass_fail(
            "Strategy Parameters Are Internally Valid",
            parameters_ready,
        ),
        pass_fail(
            "Write Firebreak Remains Intact",
            firebreak_ready,
        ),
    ]

    runtime["execution_preconditions_ready"] = all(
        results
    )

    pass_fail(
        "Read-Only Execution Preconditions Are Fully Ready",
        runtime["execution_preconditions_ready"],
    )

    if runtime["execution_preconditions_ready"]:
        log(
            f"{VERSION}: "
            "EXECUTION PRECONDITIONS VERIFIED"
        )
    else:
        log(
            f"{VERSION}: "
            "EXECUTION PRECONDITIONS NOT READY"
        )

    log(
        f"{VERSION}: IMPORTANT: "
        "ORDER EXECUTION REMAINS DISABLED"
    )

    return runtime["execution_preconditions_ready"]


# ==================================================================================================
# TEST 11
# ==================================================================================================

def test_final_state():
    banner(
        f"{VERSION} TEST 11: "
        "FINAL LIVE READ-ONLY STATE"
    )

    mutation_total = (
        runtime["leverage_mutations"]
        + runtime["margin_mutations"]
        + runtime["position_mutations"]
        + runtime["account_mutations"]
    )

    order_total = (
        runtime["real_orders"]
        + runtime["demo_orders"]
    )

    results = [
        pass_fail(
            "Credentials Remain Present",
            runtime["credentials_ready"],
        ),
        pass_fail(
            "Authenticated GET Count Is At Least Three",
            runtime["authenticated_get_count"] >= 3,
        ),
        pass_fail(
            "Public GET Count Is At Least One",
            runtime["public_get_count"] >= 1,
        ),
        pass_fail(
            "Available Balance Remains Valid",
            runtime["available_usdt"] is not None
            and runtime["available_usdt"]
            > Decimal("0"),
        ),
        pass_fail(
            "Zero Position Readiness Remains Valid",
            runtime["active_positions"] == 0,
        ),
        pass_fail(
            "ISOLATED Margin Readiness Remains Valid",
            runtime["observed_margin"]
            == TARGET_MARGIN,
        ),
        pass_fail(
            "100x Leverage Readiness Remains Valid",
            runtime["observed_long_leverage"]
            == TARGET_LONG_LEVERAGE
            and runtime["observed_short_leverage"]
            == TARGET_SHORT_LEVERAGE,
        ),
        pass_fail(
            "Market Price Readiness Remains Valid",
            runtime["market_price"] is not None
            and runtime["market_price"]
            > Decimal("0")
            and runtime["market_price_ready"],
        ),
        pass_fail(
            "Strategy Budget Readiness Remains Valid",
            runtime["strategy_budget_ready"],
        ),
        pass_fail(
            "Network Writes Remain Disabled",
            not EXCHANGE_NETWORK_WRITES_ENABLED
            and runtime["network_writes"] == 0,
        ),
        pass_fail(
            "All Mutation Counters Remain Zero",
            mutation_total == 0,
        ),
        pass_fail(
            "Real And Demo Orders Remain Zero",
            order_total == 0,
        ),
        pass_fail(
            "Execution Preconditions Are Ready",
            runtime[
                "execution_preconditions_ready"
            ],
        ),
    ]

    return all(results)


# ==================================================================================================
# FINAL SUMMARY
# ==================================================================================================

def final_summary(validation_passed):
    banner(f"{VERSION}: VALIDATION COMPLETE")

    runtime["phase"] = (
        "EXECUTION_PRECONDITIONS_VALIDATED"
        if validation_passed
        else "VALIDATION_FAILED"
    )

    runtime["final_validation_status"] = (
        "PASS"
        if validation_passed
        else "FAIL"
    )

    log(
        f"{VERSION}: PHASE="
        f"{runtime['phase']}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GET COUNT="
        f"{runtime['authenticated_get_count']}"
    )

    log(
        f"{VERSION}: PUBLIC GET COUNT="
        f"{runtime['public_get_count']}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(runtime['available_usdt'])}"
    )

    log(
        f"{VERSION}: ACTIVE POSITIONS="
        f"{runtime['active_positions']}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{runtime['observed_margin']}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{leverage_text(runtime['observed_long_leverage'])}"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{leverage_text(runtime['observed_short_leverage'])}"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{leverage_text(TARGET_LONG_LEVERAGE)}"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{leverage_text(TARGET_SHORT_LEVERAGE)}"
    )

    log(
        f"{VERSION}: INITIAL MARGIN BUDGET="
        f"{decimal_text(runtime['initial_margin_budget'])} "
        f"USDT"
    )

    log(
        f"{VERSION}: INITIAL NOTIONAL TARGET="
        f"{decimal_text(runtime['initial_notional_target'])} "
        f"USDT"
    )

    log(
        f"{VERSION}: MAXIMUM EXPOSURE BUDGET="
        f"{decimal_text(runtime['maximum_exposure_budget'])} "
        f"USDT"
    )

    log(
        f"{VERSION}: MARKET PRICE PATH="
        f"{runtime['market_price_path']}"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{decimal_text(runtime['market_price'])}"
    )

    log(
        f"{VERSION}: MARKET PRICE READY="
        f"{runtime['market_price_ready']}"
    )

    log(
        f"{VERSION}: EXECUTION PRECONDITIONS READY="
        f"{runtime['execution_preconditions_ready']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{runtime['network_writes']}"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{runtime['leverage_mutations']}"
    )

    log(
        f"{VERSION}: MARGIN MUTATIONS="
        f"{runtime['margin_mutations']}"
    )

    log(
        f"{VERSION}: POSITION MUTATIONS="
        f"{runtime['position_mutations']}"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATIONS="
        f"{runtime['account_mutations']}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{runtime['real_orders']}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{runtime['demo_orders']}"
    )

    log(
        f"{VERSION}: FINAL VALIDATION STATUS="
        f"{runtime['final_validation_status']}"
    )

    log(LINE)


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def persistent_heartbeat():
    banner(
        f"{VERSION}: "
        "ENTERING PERSISTENT HEALTH / HEARTBEAT MODE"
    )

    while True:

        time.sleep(HEARTBEAT_SECONDS)

        runtime["heartbeat"] += 1

        log(
            f"{VERSION}: HEARTBEAT "
            f"{runtime['heartbeat']} | "
            f"phase={runtime['phase']} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED} | "
            f"authenticated-get="
            f"{runtime['authenticated_get_count']} | "
            f"public-get="
            f"{runtime['public_get_count']} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"demo-execution="
            f"{DEMO_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"available-usdt="
            f"{decimal_text(runtime['available_usdt'])} | "
            f"active-positions="
            f"{runtime['active_positions']} | "
            f"observed-margin="
            f"{runtime['observed_margin']} | "
            f"observed-long="
            f"{decimal_text(runtime['observed_long_leverage'])} | "
            f"observed-short="
            f"{decimal_text(runtime['observed_short_leverage'])} | "
            f"target-long="
            f"{decimal_text(TARGET_LONG_LEVERAGE)}x | "
            f"target-short="
            f"{decimal_text(TARGET_SHORT_LEVERAGE)}x | "
            f"market-price="
            f"{decimal_text(runtime['market_price'])} | "
            f"market-price-ready="
            f"{runtime['market_price_ready']} | "
            f"execution-preconditions-ready="
            f"{runtime['execution_preconditions_ready']}"
        )


# ==================================================================================================
# MAIN
# ==================================================================================================

def main():
    banner(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")

    log(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: PUBLIC READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )

    log(
        f"{VERSION}: MARGIN MUTATION DISABLED"
    )

    log(
        f"{VERSION}: POSITION MUTATION DISABLED"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATION DISABLED"
    )

    log(
        f"{VERSION}: TARGET MARGIN="
        f"{TARGET_MARGIN}"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: MARKET PRICE ENDPOINT="
        f"/capi/v3/market/symbolPrice"
        f"?symbol={SYMBOL}&priceType=MARK"
    )

    # Start Render health listener before exchange tests.
    try:
        start_health_server()

    except OSError as exc:
        log(
            f"{VERSION}: HEALTH SERVER ERROR={exc}"
        )

        # A health-port collision should not enable any exchange action.
        # Stop here because Render health availability is part of runtime
        # integrity.
        sys.exit(1)

    runtime["phase"] = "VALIDATING"

    test_results = []

    # ----------------------------------------------------------------------------------------------
    # TEST 1
    # ----------------------------------------------------------------------------------------------
    test_results.append(
        test_safety_configuration()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 2
    # ----------------------------------------------------------------------------------------------
    credentials_ok = test_credentials()
    test_results.append(credentials_ok)

    # We do not attempt authenticated account requests when
    # credentials themselves are missing.
    if credentials_ok:

        # ------------------------------------------------------------------------------------------
        # TEST 3
        # ------------------------------------------------------------------------------------------
        test_results.append(
            test_balance()
        )

        # ------------------------------------------------------------------------------------------
        # TEST 4
        # ------------------------------------------------------------------------------------------
        test_results.append(
            test_positions()
        )

        # ------------------------------------------------------------------------------------------
        # TEST 5
        # ------------------------------------------------------------------------------------------
        test_results.append(
            test_symbol_configuration()
        )

    else:

        banner(
            f"{VERSION}: "
            "AUTHENTICATED LIVE READS SKIPPED"
        )

        log(
            f"{VERSION}: Credentials are incomplete."
        )

        runtime["balance_ready"] = False
        runtime["positions_ready"] = False
        runtime["margin_ready"] = False
        runtime["leverage_ready"] = False

        test_results.extend(
            [
                False,
                False,
                False,
            ]
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 6
    #
    # Public endpoint is independent of authenticated credentials.
    # ----------------------------------------------------------------------------------------------
    test_results.append(
        test_public_market_price()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 7
    # ----------------------------------------------------------------------------------------------
    test_results.append(
        test_strategy_budget()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 8
    # ----------------------------------------------------------------------------------------------
    test_results.append(
        test_strategy_parameters()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 9
    # ----------------------------------------------------------------------------------------------
    test_results.append(
        test_write_firebreak()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 10
    # ----------------------------------------------------------------------------------------------
    test_results.append(
        test_execution_preconditions()
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 11
    # ----------------------------------------------------------------------------------------------
    test_results.append(
        test_final_state()
    )

    validation_passed = all(test_results)

    final_summary(
        validation_passed
    )

    # Persistent process required by Render.
    persistent_heartbeat()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        log(
            f"{VERSION}: SHUTDOWN REQUESTED"
        )

    except Exception as exc:
        runtime["phase"] = "FATAL_ERROR"
        runtime["final_validation_status"] = "FAIL"

        banner(
            f"{VERSION}: FATAL ERROR"
        )

        log(
            f"{VERSION}: {type(exc).__name__}: {exc}"
        )

        log(
            f"{VERSION}: NETWORK WRITES="
            f"{runtime['network_writes']}"
        )

        log(
            f"{VERSION}: REAL ORDERS="
            f"{runtime['real_orders']}"
        )

        log(
            f"{VERSION}: DEMO ORDERS="
            f"{runtime['demo_orders']}"
        )

        log(LINE)

        raise
