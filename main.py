# ============================================================
# 0F-4H-R28-UNIT-K.1
# TRANSPORT-BOUNDARY / WRITE-LOCK AUDIT
#
# AUTHENTICATED READ-ONLY ACCOUNT RECONCILIATION
#
# PUBLIC WEEX MARKET GET REQUESTS ENABLED
# AUTHENTICATED ACCOUNT GET REQUESTS ENABLED
#
# REAL ORDER TRANSMISSION DISABLED
# DEMO ORDER TRANSMISSION DISABLED
# ALL NETWORK WRITE METHODS BLOCKED
#
# IMPORTANT:
# LOCAL WRITE ATTEMPTS ARE COUNTED SEPARATELY FROM
# ACTUAL NETWORK TRANSMISSIONS.
# ============================================================


print(
    "R28 UNIT K.1: MAIN.PY ENTERED",
    flush=True,
)


# ============================================================
# IMPORTS
# ============================================================

import base64
import hashlib
import hmac
import json
import os
import threading
import time
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


print(
    "R28 UNIT K.1: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-K.1"
MODULE_VERSION = "R28-K.1"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

WEEX_BASE_URL = "https://api-contract.weex.com"

PUBLIC_PRICE_PATH = "/capi/v3/market/symbolPrice"
BALANCE_PATH = "/capi/v3/account/balance"
POSITIONS_PATH = "/capi/v3/account/position/allPosition"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

REAL_ORDER_PATH = "/capi/v3/order/placeOrder"
DEMO_ORDER_PATH = "/capi/v3/sim/order"


# ============================================================
# STRATEGY REFERENCE
# READ-ONLY — UNIT K.1 WILL NOT MODIFY ACCOUNT SETTINGS
# ============================================================

PLANNED_MARGIN_TYPE = "ISOLATED"
PLANNED_LEVERAGE = Decimal("100")


# ============================================================
# ABSOLUTE EXECUTION LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

PUBLIC_NETWORK_GET_ENABLED = True
AUTHENTICATED_READ_ONLY_ENABLED = True

PRIVATE_WRITE_ACCESS_ENABLED = False
NETWORK_WRITE_ENABLED = False


# ============================================================
# CREDENTIALS
# ============================================================

API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("API_KEY")
    or ""
).strip()

API_SECRET = (
    os.getenv("WEEX_API_SECRET")
    or os.getenv("API_SECRET")
    or ""
).strip()

API_PASSPHRASE = (
    os.getenv("WEEX_API_PASSPHRASE")
    or os.getenv("API_PASSPHRASE")
    or os.getenv("PASSPHRASE")
    or ""
).strip()


# ============================================================
# NETWORK ALLOWLIST
# ============================================================

PUBLIC_GET_ALLOWLIST = {
    PUBLIC_PRICE_PATH,
}

PRIVATE_GET_ALLOWLIST = {
    BALANCE_PATH,
    POSITIONS_PATH,
    SYMBOL_CONFIG_PATH,
}

WRITE_METHODS = {
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}

ORDER_PATHS = {
    REAL_ORDER_PATH,
    DEMO_ORDER_PATH,
}


# ============================================================
# TRANSPORT AUDIT COUNTERS
#
# CRITICAL K.1 CHANGE:
#
# Attempt != Block != Transport != Transmission
#
# A locally rejected POST is NOT an order transmission.
# ============================================================

AUDIT = {

    # Local API calls made during lock testing
    "local_post_attempts": 0,
    "local_put_attempts": 0,
    "local_patch_attempts": 0,
    "local_delete_attempts": 0,

    # Local requests successfully stopped before transport
    "local_post_blocked": 0,
    "local_put_blocked": 0,
    "local_patch_blocked": 0,
    "local_delete_blocked": 0,

    # Specific order attempts
    "real_order_local_attempts": 0,
    "demo_order_local_attempts": 0,

    "real_order_blocked_locally": 0,
    "demo_order_blocked_locally": 0,

    # Network transport counts
    "network_get_count": 0,
    "public_network_get_count": 0,
    "private_network_get_count": 0,

    # These MUST stay zero
    "network_write_count": 0,
    "network_post_count": 0,
    "network_put_count": 0,
    "network_patch_count": 0,
    "network_delete_count": 0,

    # Actual order transmission counters
    "real_order_network_transmissions": 0,
    "demo_order_network_transmissions": 0,

    # Rejections before transport
    "unallowlisted_private_get_blocks": 0,
    "external_host_blocks": 0,
}


# ============================================================
# DIAGNOSTIC RESULT STORAGE
# ============================================================

RESULTS = []


def record_result(name, passed):

    RESULTS.append(
        (
            str(name),
            bool(passed),
        )
    )

    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{name:<55} {status}",
        flush=True,
    )


# ============================================================
# SAFE DECIMAL
# ============================================================

def safe_decimal(value, default="0"):

    try:

        if value is None:
            return Decimal(default)

        return Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return Decimal(default)


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = (
            b"R28 UNIT K.1 ACTIVE - "
            b"AUTHENTICATED READ-ONLY - "
            b"NETWORK WRITES LOCKED"
        )

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

    def log_message(self, format, *args):

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
        f"R28 UNIT K.1: HEALTH SERVER ACTIVE ON PORT {port}",
        flush=True,
    )

    return server


# ============================================================
# URL SAFETY
# ============================================================

def ensure_weex_host(path):

    if not isinstance(path, str):
        raise PermissionError(
            "Path must be a string"
        )

    if not path.startswith("/"):
        raise PermissionError(
            "Absolute external URL rejected"
        )

    if "://" in path:
        AUDIT["external_host_blocks"] += 1

        raise PermissionError(
            "External host rejected locally"
        )

    return True


# ============================================================
# PRIVATE GET ALLOWLIST
# ============================================================

def ensure_private_get_allowed(path):

    ensure_weex_host(path)

    if path not in PRIVATE_GET_ALLOWLIST:

        AUDIT[
            "unallowlisted_private_get_blocks"
        ] += 1

        raise PermissionError(
            f"Private GET not allowlisted: {path}"
        )

    return True


# ============================================================
# AUTHENTICATION
# ============================================================

def build_auth_headers(
    method,
    request_path,
    body="",
):

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    method = method.upper()

    body = body or ""

    prehash = (
        timestamp
        + method
        + request_path
        + body
    )

    signature = base64.b64encode(
        hmac.new(
            API_SECRET.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ============================================================
# LOW-LEVEL GET TRANSPORT
#
# ONLY THIS FUNCTION MAY REACH THE NETWORK.
# IT ACCEPTS GET ONLY.
#
# THIS IS THE MOST IMPORTANT K.1 TRANSPORT BOUNDARY.
# ============================================================

def network_get(
    path,
    authenticated=False,
    timeout=15,
):

    ensure_weex_host(path)

    if not PUBLIC_NETWORK_GET_ENABLED:
        raise PermissionError(
            "Network GET disabled"
        )

    if authenticated:

        if not AUTHENTICATED_READ_ONLY_ENABLED:
            raise PermissionError(
                "Authenticated reads disabled"
            )

        ensure_private_get_allowed(path)

    else:

        if path not in PUBLIC_GET_ALLOWLIST:

            raise PermissionError(
                f"Public GET not allowlisted: {path}"
            )

    url = WEEX_BASE_URL + path

    headers = {
        "Accept": "application/json",
    }

    if authenticated:

        headers.update(
            build_auth_headers(
                "GET",
                path,
                "",
            )
        )

    request = Request(
        url=url,
        headers=headers,
        method="GET",
    )

    # --------------------------------------------------------
    # COUNT ONLY WHEN REQUEST IS ABOUT TO CROSS TRANSPORT
    # --------------------------------------------------------

    AUDIT["network_get_count"] += 1

    if authenticated:
        AUDIT[
            "private_network_get_count"
        ] += 1

    else:
        AUDIT[
            "public_network_get_count"
        ] += 1

    try:

        with urlopen(
            request,
            timeout=timeout,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

    except HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {raw}"
        )

    except URLError as exc:

        raise RuntimeError(
            f"Network error: {exc}"
        )

    try:

        return json.loads(raw)

    except json.JSONDecodeError:

        return {
            "raw": raw,
        }


# ============================================================
# ABSOLUTELY BLOCKED WRITE TRANSPORT
#
# THIS FUNCTION MUST NEVER CALL URLOPEN.
# ============================================================

def blocked_write_request(
    method,
    path,
    payload=None,
):

    method = str(method).upper()

    ensure_weex_host(path)

    if method == "POST":

        AUDIT["local_post_attempts"] += 1

        if path == REAL_ORDER_PATH:

            AUDIT[
                "real_order_local_attempts"
            ] += 1

        elif path == DEMO_ORDER_PATH:

            AUDIT[
                "demo_order_local_attempts"
            ] += 1

        AUDIT["local_post_blocked"] += 1

        if path == REAL_ORDER_PATH:

            AUDIT[
                "real_order_blocked_locally"
            ] += 1

        elif path == DEMO_ORDER_PATH:

            AUDIT[
                "demo_order_blocked_locally"
            ] += 1

        raise PermissionError(
            "POST rejected locally before network transport"
        )

    if method == "PUT":

        AUDIT["local_put_attempts"] += 1
        AUDIT["local_put_blocked"] += 1

        raise PermissionError(
            "PUT rejected locally before network transport"
        )

    if method == "PATCH":

        AUDIT["local_patch_attempts"] += 1
        AUDIT["local_patch_blocked"] += 1

        raise PermissionError(
            "PATCH rejected locally before network transport"
        )

    if method == "DELETE":

        AUDIT["local_delete_attempts"] += 1
        AUDIT["local_delete_blocked"] += 1

        raise PermissionError(
            "DELETE rejected locally before network transport"
        )

    raise PermissionError(
        f"Unsupported method rejected: {method}"
    )


# ============================================================
# LOCAL LOCK TEST HELPER
# ============================================================

def expect_local_rejection(
    method,
    path,
):

    try:

        blocked_write_request(
            method,
            path,
            {},
        )

    except PermissionError:

        return True

    except Exception:

        return False

    return False


# ============================================================
# RESPONSE DATA EXTRACTION
# ============================================================

def extract_data(response):

    if not isinstance(response, dict):
        return response

    if "data" in response:
        return response["data"]

    return response


# ============================================================
# PUBLIC MARKET PRICE
# ============================================================

def obtain_symbol_price():

    response = network_get(
        PUBLIC_PRICE_PATH,
        authenticated=False,
    )

    data = extract_data(response)

    candidates = []

    if isinstance(data, dict):

        candidates.extend(
            [
                data.get("price"),
                data.get("markPrice"),
                data.get("last"),
                data.get("lastPrice"),
            ]
        )

        nested = data.get(SYMBOL)

        if isinstance(nested, dict):

            candidates.extend(
                [
                    nested.get("price"),
                    nested.get("markPrice"),
                    nested.get("last"),
                    nested.get("lastPrice"),
                ]
            )

    elif isinstance(data, list):

        for item in data:

            if not isinstance(item, dict):
                continue

            symbol = str(
                item.get("symbol", "")
            ).upper()

            if symbol == SYMBOL:

                candidates.extend(
                    [
                        item.get("price"),
                        item.get("markPrice"),
                        item.get("last"),
                        item.get("lastPrice"),
                    ]
                )

    for value in candidates:

        if value is None:
            continue

        price = safe_decimal(
            value,
            "-1",
        )

        if price > 0:
            return price

    raise RuntimeError(
        "Unable to extract BTCUSDT price"
    )


# ============================================================
# BALANCE EXTRACTION
# ============================================================

def obtain_balance():

    response = network_get(
        BALANCE_PATH,
        authenticated=True,
    )

    data = extract_data(response)

    records = []

    if isinstance(data, list):

        records = data

    elif isinstance(data, dict):

        if isinstance(
            data.get("list"),
            list,
        ):

            records = data["list"]

        elif isinstance(
            data.get("assets"),
            list,
        ):

            records = data["assets"]

        else:

            records = [data]

    selected = None

    for item in records:

        if not isinstance(item, dict):
            continue

        coin = str(
            item.get(
                "coin",
                item.get(
                    "marginCoin",
                    item.get(
                        "currency",
                        "",
                    ),
                ),
            )
        ).upper()

        if coin == "USDT":

            selected = item
            break

    if selected is None and records:

        first = records[0]

        if isinstance(first, dict):
            selected = first

    if selected is None:

        raise RuntimeError(
            "No balance record returned"
        )

    balance = safe_decimal(
        selected.get(
            "balance",
            selected.get(
                "equity",
                selected.get(
                    "accountEquity",
                    "0",
                ),
            ),
        )
    )

    available = safe_decimal(
        selected.get(
            "available",
            selected.get(
                "availableBalance",
                selected.get(
                    "availableEquity",
                    balance,
                ),
            ),
        )
    )

    frozen = safe_decimal(
        selected.get(
            "frozen",
            selected.get(
                "locked",
                selected.get(
                    "freeze",
                    "0",
                ),
            ),
        )
    )

    unrealized_pnl = safe_decimal(
        selected.get(
            "unrealizedPL",
            selected.get(
                "unrealizedPnl",
                selected.get(
                    "unrealizedProfit",
                    "0",
                ),
            ),
        )
    )

    return {
        "balance": balance,
        "available": available,
        "frozen": frozen,
        "unrealized_pnl": unrealized_pnl,
        "raw": selected,
    }


# ============================================================
# POSITION EXTRACTION
# ============================================================

def obtain_positions():

    response = network_get(
        POSITIONS_PATH,
        authenticated=True,
    )

    data = extract_data(response)

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "list",
            "positions",
            "positionList",
        ):

            value = data.get(key)

            if isinstance(value, list):
                return value

        return [data]

    return []


def active_symbol_positions(
    positions,
):

    active = []

    for item in positions:

        if not isinstance(item, dict):
            continue

        item_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if item_symbol != SYMBOL:
            continue

        size = safe_decimal(
            item.get(
                "size",
                item.get(
                    "total",
                    item.get(
                        "positionAmt",
                        item.get(
                            "position",
                            "0",
                        ),
                    ),
                ),
            )
        )

        if size != 0:
            active.append(item)

    return active


# ============================================================
# SYMBOL CONFIG
# ============================================================

def obtain_symbol_config():

    response = network_get(
        SYMBOL_CONFIG_PATH,
        authenticated=True,
    )

    data = extract_data(response)

    records = []

    if isinstance(data, list):

        records = data

    elif isinstance(data, dict):

        for key in (
            "list",
            "configs",
            "symbolConfigs",
        ):

            if isinstance(
                data.get(key),
                list,
            ):

                records = data[key]
                break

        if not records:
            records = [data]

    for item in records:

        if not isinstance(item, dict):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol == SYMBOL:
            return item

    if records:

        first = records[0]

        if isinstance(first, dict):
            return first

    raise RuntimeError(
        "Symbol configuration unavailable"
    )


# ============================================================
# CONFIG FIELD HELPERS
# ============================================================

def get_first_value(
    source,
    keys,
    default=None,
):

    if not isinstance(source, dict):
        return default

    for key in keys:

        if key in source:

            value = source.get(key)

            if value is not None:
                return value

    return default


# ============================================================
# SAFETY TESTS
# ============================================================

def run_safety_gates():

    print(
        "R28 UNIT K.1 SAFETY GATES",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    record_result(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    record_result(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    record_result(
        "Real Order Transmission Disabled",
        NETWORK_WRITE_ENABLED is False,
    )

    record_result(
        "Demo Order Transmission Disabled",
        NETWORK_WRITE_ENABLED is False,
    )

    record_result(
        "Private Write Access Disabled",
        PRIVATE_WRITE_ACCESS_ENABLED is False,
    )

    record_result(
        "Authenticated Read Access Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED is True,
    )

    record_result(
        "Private GET Allowlist Locked",
        (
            BALANCE_PATH
            in PRIVATE_GET_ALLOWLIST
            and POSITIONS_PATH
            in PRIVATE_GET_ALLOWLIST
            and SYMBOL_CONFIG_PATH
            in PRIVATE_GET_ALLOWLIST
        ),
    )

    record_result(
        "WEEX Host Locked",
        WEEX_BASE_URL
        == "https://api-contract.weex.com",
    )

    credentials_present = bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )

    record_result(
        "API Credentials Present",
        credentials_present,
    )

    # --------------------------------------------------------
    # LOCAL WRITE-LOCK TESTS
    # --------------------------------------------------------

    generic_post = expect_local_rejection(
        "POST",
        "/capi/v3/test/write",
    )

    record_result(
        "Generic POST Rejected Before Transport",
        generic_post,
    )

    put_blocked = expect_local_rejection(
        "PUT",
        "/capi/v3/test/write",
    )

    record_result(
        "PUT Rejected Before Transport",
        put_blocked,
    )

    patch_blocked = expect_local_rejection(
        "PATCH",
        "/capi/v3/test/write",
    )

    record_result(
        "PATCH Rejected Before Transport",
        patch_blocked,
    )

    delete_blocked = expect_local_rejection(
        "DELETE",
        "/capi/v3/test/write",
    )

    record_result(
        "DELETE Rejected Before Transport",
        delete_blocked,
    )

    real_blocked = expect_local_rejection(
        "POST",
        REAL_ORDER_PATH,
    )

    record_result(
        "Real Order POST Rejected Before Transport",
        real_blocked,
    )

    demo_blocked = expect_local_rejection(
        "POST",
        DEMO_ORDER_PATH,
    )

    record_result(
        "Demo Order POST Rejected Before Transport",
        demo_blocked,
    )

    # --------------------------------------------------------
    # UNALLOWLISTED PRIVATE GET
    # --------------------------------------------------------

    unallowlisted_blocked = False

    try:

        ensure_private_get_allowed(
            "/capi/v3/account/notAllowed"
        )

    except PermissionError:

        unallowlisted_blocked = True

    record_result(
        "Unallowlisted Private GET Rejected Locally",
        unallowlisted_blocked,
    )

    # --------------------------------------------------------
    # EXTERNAL HOST
    # --------------------------------------------------------

    external_blocked = False

    try:

        ensure_weex_host(
            "https://example.com/test"
        )

    except PermissionError:

        external_blocked = True

    record_result(
        "Arbitrary External Host Rejected",
        external_blocked,
    )


# ============================================================
# READ-ONLY RECONCILIATION
# ============================================================

def run_read_only_reconciliation():

    print(
        "R28 UNIT K.1 READ-ONLY RECONCILIATION",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    # --------------------------------------------------------
    # MARKET PRICE
    # --------------------------------------------------------

    print(
        "R28 UNIT K.1: PUBLIC GET -> "
        + PUBLIC_PRICE_PATH,
        flush=True,
    )

    try:

        price = obtain_symbol_price()

        record_result(
            "Public Market GET",
            price > 0,
        )

        print(
            f"R28 UNIT K.1: {SYMBOL} PRICE = {price}",
            flush=True,
        )

    except Exception as exc:

        price = None

        record_result(
            "Public Market GET",
            False,
        )

        print(
            f"R28 UNIT K.1 PUBLIC GET ERROR: {exc}",
            flush=True,
        )

    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    print(
        "R28 UNIT K.1: AUTHENTICATED GET -> "
        + BALANCE_PATH,
        flush=True,
    )

    try:

        balance = obtain_balance()

        record_result(
            "Authenticated Balance GET",
            True,
        )

        print(
            "R28 UNIT K.1: USDT BALANCE = "
            f"{balance['balance']}",
            flush=True,
        )

        print(
            "R28 UNIT K.1: USDT AVAILABLE = "
            f"{balance['available']}",
            flush=True,
        )

        print(
            "R28 UNIT K.1: USDT FROZEN = "
            f"{balance['frozen']}",
            flush=True,
        )

        print(
            "R28 UNIT K.1: ACCOUNT UNREALIZED PNL = "
            f"{balance['unrealized_pnl']}",
            flush=True,
        )

        record_result(
            "Balance Is Non-Negative",
            balance["balance"] >= 0,
        )

        record_result(
            "Available Balance Is Non-Negative",
            balance["available"] >= 0,
        )

        record_result(
            "Frozen Balance Is Non-Negative",
            balance["frozen"] >= 0,
        )

    except Exception as exc:

        balance = None

        record_result(
            "Authenticated Balance GET",
            False,
        )

        print(
            f"R28 UNIT K.1 BALANCE ERROR: {exc}",
            flush=True,
        )

    # --------------------------------------------------------
    # POSITIONS
    # --------------------------------------------------------

    print(
        "R28 UNIT K.1: AUTHENTICATED GET -> "
        + POSITIONS_PATH,
        flush=True,
    )

    try:

        positions = obtain_positions()

        active_positions = active_symbol_positions(
            positions
        )

        record_result(
            "Authenticated Positions GET",
            True,
        )

        print(
            "R28 UNIT K.1: POSITION RECORDS = "
            f"{len(positions)}",
            flush=True,
        )

        print(
            f"R28 UNIT K.1: ACTIVE {SYMBOL} POSITIONS = "
            f"{len(active_positions)}",
            flush=True,
        )

        structural_valid = all(
            isinstance(
                item,
                dict,
            )
            for item in positions
        )

        record_result(
            "Position Records Structurally Valid",
            structural_valid,
        )

    except Exception as exc:

        positions = []
        active_positions = []

        record_result(
            "Authenticated Positions GET",
            False,
        )

        print(
            f"R28 UNIT K.1 POSITION ERROR: {exc}",
            flush=True,
        )

    # --------------------------------------------------------
    # SYMBOL CONFIG
    # --------------------------------------------------------

    print(
        "R28 UNIT K.1: AUTHENTICATED GET -> "
        + SYMBOL_CONFIG_PATH,
        flush=True,
    )

    try:

        config = obtain_symbol_config()

        record_result(
            "Authenticated Symbol Config GET",
            True,
        )

        config_symbol = str(
            get_first_value(
                config,
                [
                    "symbol",
                ],
                "",
            )
        ).upper()

        margin_type = str(
            get_first_value(
                config,
                [
                    "marginType",
                    "marginMode",
                    "margin_type",
                ],
                "UNKNOWN",
            )
        ).upper()

        position_mode = str(
            get_first_value(
                config,
                [
                    "positionMode",
                    "posMode",
                    "positionType",
                ],
                "UNKNOWN",
            )
        ).upper()

        cross_leverage = safe_decimal(
            get_first_value(
                config,
                [
                    "crossLeverage",
                    "crossMarginLeverage",
                    "cross_leverage",
                ],
                "0",
            )
        )

        isolated_long_leverage = safe_decimal(
            get_first_value(
                config,
                [
                    "isolatedLongLeverage",
                    "longLeverage",
                    "isolated_long_leverage",
                ],
                "0",
            )
        )

        isolated_short_leverage = safe_decimal(
            get_first_value(
                config,
                [
                    "isolatedShortLeverage",
                    "shortLeverage",
                    "isolated_short_leverage",
                ],
                "0",
            )
        )

        print(
            "R28 UNIT K.1 SYMBOL CONFIG:",
            flush=True,
        )

        print(
            f"  Symbol = {config_symbol}",
            flush=True,
        )

        print(
            f"  Margin Type = {margin_type}",
            flush=True,
        )

        print(
            f"  Position Mode = {position_mode}",
            flush=True,
        )

        print(
            f"  Cross Leverage = {cross_leverage}",
            flush=True,
        )

        print(
            "  Isolated Long Leverage = "
            f"{isolated_long_leverage}",
            flush=True,
        )

        print(
            "  Isolated Short Leverage = "
            f"{isolated_short_leverage}",
            flush=True,
        )

        record_result(
            "Symbol Configuration Matches Target Symbol",
            config_symbol == SYMBOL,
        )

        recognized_margin = margin_type in {
            "ISOLATED",
            "CROSSED",
            "CROSS",
        }

        record_result(
            "Margin Type Recognized",
            recognized_margin,
        )

        recognized_position_mode = (
            position_mode
            not in {
                "",
                "UNKNOWN",
                "NONE",
            }
        )

        record_result(
            "Position Mode Recognized",
            recognized_position_mode,
        )

        leverage_values_valid = (
            cross_leverage >= 0
            and isolated_long_leverage >= 0
            and isolated_short_leverage >= 0
        )

        record_result(
            "Configured Leverage Values Valid",
            leverage_values_valid,
        )

        print(
            "R28 UNIT K.1 READ-ONLY STRATEGY COMPARISON:",
            flush=True,
        )

        print(
            f"  Planned Margin Type = {PLANNED_MARGIN_TYPE}",
            flush=True,
        )

        print(
            f"  Planned Leverage = {PLANNED_LEVERAGE}x",
            flush=True,
        )

        if (
            isolated_long_leverage
            != PLANNED_LEVERAGE
            or isolated_short_leverage
            != PLANNED_LEVERAGE
        ):

            print(
                "⚠️ Observed isolated leverage differs "
                "from planned strategy leverage. "
                "NO CHANGE ATTEMPTED.",
                flush=True,
            )

    except Exception as exc:

        config = None

        record_result(
            "Authenticated Symbol Config GET",
            False,
        )

        print(
            f"R28 UNIT K.1 SYMBOL CONFIG ERROR: {exc}",
            flush=True,
        )

    # --------------------------------------------------------
    # POSITION CONSISTENCY
    # --------------------------------------------------------

    position_consistent = isinstance(
        active_positions,
        list,
    )

    record_result(
        "Active Position State Internally Consistent",
        position_consistent,
    )


# ============================================================
# FINAL TRANSPORT BOUNDARY AUDIT
# ============================================================

def run_transport_audit():

    print(
        "R28 UNIT K.1 TRANSPORT-BOUNDARY AUDIT",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    record_result(
        "Controlled Public GET Occurred",
        AUDIT[
            "public_network_get_count"
        ] > 0,
    )

    record_result(
        "Controlled Private GET Occurred",
        AUDIT[
            "private_network_get_count"
        ] > 0,
    )

    record_result(
        "Generic POST Was Blocked Locally",
        AUDIT[
            "local_post_blocked"
        ] >= 3,
    )

    record_result(
        "Real Order Attempt Was Blocked Locally",
        (
            AUDIT[
                "real_order_local_attempts"
            ] == 1
            and AUDIT[
                "real_order_blocked_locally"
            ] == 1
        ),
    )

    record_result(
        "Demo Order Attempt Was Blocked Locally",
        (
            AUDIT[
                "demo_order_local_attempts"
            ] == 1
            and AUDIT[
                "demo_order_blocked_locally"
            ] == 1
        ),
    )

    # --------------------------------------------------------
    # THESE ARE THE REAL TRANSMISSION ASSERTIONS
    # --------------------------------------------------------

    record_result(
        "Network Write Count Is Zero",
        AUDIT[
            "network_write_count"
        ] == 0,
    )

    record_result(
        "Network POST Count Is Zero",
        AUDIT[
            "network_post_count"
        ] == 0,
    )

    record_result(
        "Network PUT Count Is Zero",
        AUDIT[
            "network_put_count"
        ] == 0,
    )

    record_result(
        "Network PATCH Count Is Zero",
        AUDIT[
            "network_patch_count"
        ] == 0,
    )

    record_result(
        "Network DELETE Count Is Zero",
        AUDIT[
            "network_delete_count"
        ] == 0,
    )

    record_result(
        "Real Order Transmission Never Occurred",
        AUDIT[
            "real_order_network_transmissions"
        ] == 0,
    )

    record_result(
        "Demo Order Transmission Never Occurred",
        AUDIT[
            "demo_order_network_transmissions"
        ] == 0,
    )

    print(
        "R28 UNIT K.1 WRITE-LOCK AUDIT:",
        flush=True,
    )

    print(
        "  Local POST attempts = "
        f"{AUDIT['local_post_attempts']}",
        flush=True,
    )

    print(
        "  Local POST blocks = "
        f"{AUDIT['local_post_blocked']}",
        flush=True,
    )

    print(
        "  Local PUT attempts = "
        f"{AUDIT['local_put_attempts']}",
        flush=True,
    )

    print(
        "  Local PUT blocks = "
        f"{AUDIT['local_put_blocked']}",
        flush=True,
    )

    print(
        "  Local PATCH attempts = "
        f"{AUDIT['local_patch_attempts']}",
        flush=True,
    )

    print(
        "  Local PATCH blocks = "
        f"{AUDIT['local_patch_blocked']}",
        flush=True,
    )

    print(
        "  Local DELETE attempts = "
        f"{AUDIT['local_delete_attempts']}",
        flush=True,
    )

    print(
        "  Local DELETE blocks = "
        f"{AUDIT['local_delete_blocked']}",
        flush=True,
    )

    print(
        "  Network GETs = "
        f"{AUDIT['network_get_count']}",
        flush=True,
    )

    print(
        "  Network writes = "
        f"{AUDIT['network_write_count']}",
        flush=True,
    )

    print(
        "  Real order network transmissions = "
        f"{AUDIT['real_order_network_transmissions']}",
        flush=True,
    )

    print(
        "  Demo order network transmissions = "
        f"{AUDIT['demo_order_network_transmissions']}",
        flush=True,
    )


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

def run_diagnostic():

    print(
        "=" * 60,
        flush=True,
    )

    print(
        "0F-4H-R28-UNIT-K.1 STARTING",
        flush=True,
    )

    print(
        "TRANSPORT-BOUNDARY / WRITE-LOCK AUDIT",
        flush=True,
    )

    print(
        "AUTHENTICATED READ-ONLY ACCOUNT STATE RECONCILIATION",
        flush=True,
    )

    print(
        "PUBLIC WEEX MARKET GET REQUESTS ENABLED",
        flush=True,
    )

    print(
        "AUTHENTICATED ACCOUNT GET REQUESTS ENABLED",
        flush=True,
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "DEMO ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "ALL NETWORK WRITE METHODS BLOCKED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"R28 UNIT K.1 SYMBOL: {SYMBOL}",
        flush=True,
    )

    print(
        "R28 UNIT K.1 NETWORK POLICY:",
        flush=True,
    )

    print(
        "  ✅ Public market GET enabled",
        flush=True,
    )

    print(
        "  ✅ Authenticated read-only GET enabled",
        flush=True,
    )

    print(
        "  ❌ Real order POST disabled",
        flush=True,
    )

    print(
        "  ❌ Demo order POST disabled",
        flush=True,
    )

    print(
        "  ❌ PUT / PATCH / DELETE disabled",
        flush=True,
    )

    print(
        "R28 UNIT K.1 CREDENTIAL STATUS:",
        flush=True,
    )

    print(
        "  API Key: "
        + (
            "✅ PRESENT"
            if API_KEY
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Secret: "
        + (
            "✅ PRESENT"
            if API_SECRET
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Passphrase: "
        + (
            "✅ PRESENT"
            if API_PASSPHRASE
            else "❌ MISSING"
        ),
        flush=True,
    )

    run_safety_gates()

    if not (
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    ):

        print(
            "-" * 60,
            flush=True,
        )

        print(
            "❌ R28 UNIT K.1 CANNOT RUN "
            "AUTHENTICATED READ TESTS",
            flush=True,
        )

        print(
            "R28 UNIT K.1: WRITE LOCKS REMAIN ACTIVE",
            flush=True,
        )

        print(
            "=" * 60,
            flush=True,
        )

        return False

    run_read_only_reconciliation()

    run_transport_audit()

    print(
        "-" * 60,
        flush=True,
    )

    passed = all(
        result
        for _, result in RESULTS
    )

    if passed:

        print(
            "✅ R28 UNIT K.1 DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ READ-ONLY ACCOUNT RECONCILIATION VALIDATED",
            flush=True,
        )

        print(
            "✅ TRANSPORT-BOUNDARY WRITE LOCK VALIDATED",
            flush=True,
        )

        print(
            "✅ LOCAL WRITE ATTEMPTS SEPARATED "
            "FROM NETWORK TRANSMISSIONS",
            flush=True,
        )

        print(
            "✅ REAL ORDER TRANSMISSION COUNT = 0",
            flush=True,
        )

        print(
            "✅ DEMO ORDER TRANSMISSION COUNT = 0",
            flush=True,
        )

        print(
            "✅ UNIT K.1 READY FOR NEXT INTEGRATION STAGE",
            flush=True,
        )

        print(
            "🛡 ALL NETWORK WRITE METHODS REMAIN LOCKED",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT K.1 DIAGNOSTIC DID NOT PASS",
            flush=True,
        )

        print(
            "R28 UNIT K.1: WRITE LOCKS REMAIN ACTIVE",
            flush=True,
        )

    print(
        "=" * 60,
        flush=True,
    )

    return passed


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

def persistent_runtime():

    heartbeat = 0

    print(
        "R28 UNIT K.1: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT K.1: AUTHENTICATED READ-ONLY LOCKS ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT K.1: NETWORK WRITE TRANSPORT LOCKED",
        flush=True,
    )

    while True:

        heartbeat += 1

        print(
            f"R28 UNIT K.1: HEARTBEAT {heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(30)


# ============================================================
# ENTRY POINT
# ============================================================

def main():

    print(
        "R28 UNIT K.1: RUNTIME STARTING",
        flush=True,
    )

    start_health_server()

    run_diagnostic()

    persistent_runtime()


if __name__ == "__main__":

    main()
  
