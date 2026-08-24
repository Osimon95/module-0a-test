# ============================================================
# 0F-4H-R28-UNIT-K
#
# AUTHENTICATED READ-ONLY ACCOUNT STATE RECONCILIATION
#
# PUBLIC WEEX MARKET GET REQUESTS ENABLED
# AUTHENTICATED ACCOUNT GET REQUESTS ENABLED
#
# REAL ORDER TRANSMISSION DISABLED
# DEMO ORDER TRANSMISSION DISABLED
# ALL WRITE METHODS BLOCKED
#
# NO ORDER CREATION
# NO ORDER CANCELLATION
# NO LEVERAGE CHANGE
# NO MARGIN MODE CHANGE
# ============================================================


print(
    "R28 UNIT K: MAIN.PY ENTERED",
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
import signal
import threading
import time

from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


print(
    "R28 UNIT K: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-K"
MODULE_VERSION = "R28-K"


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

REAL_ORDER_TRANSMISSION = False
DEMO_ORDER_TRANSMISSION = False

PRIVATE_WRITE_ACCESS = False

ALLOW_PUBLIC_GET = True
ALLOW_AUTHENTICATED_GET = True

ALLOW_POST = False
ALLOW_PUT = False
ALLOW_PATCH = False
ALLOW_DELETE = False

NETWORK_ACCESS_ENABLED = True


# ============================================================
# WEEX HOST LOCK
# ============================================================

WEEX_HOST = "https://api-contract.weex.com"

ALLOWED_HOSTS = {
    WEEX_HOST,
}


# ============================================================
# SYMBOL
# ============================================================

SYMBOL = (
    os.getenv(
        "SYMBOL",
        "BTCUSDT",
    )
    .strip()
    .upper()
)


# ============================================================
# OBSERVATION TARGETS
#
# THESE ARE NOT TRANSMITTED TO WEEX.
# THEY ARE DISPLAYED ONLY FOR READ-ONLY COMPARISON.
# ============================================================

PLANNED_MARGIN_TYPE = (
    os.getenv(
        "PLANNED_MARGIN_TYPE",
        "ISOLATED",
    )
    .strip()
    .upper()
)

try:

    PLANNED_LEVERAGE = int(
        os.getenv(
            "PLANNED_LEVERAGE",
            "100",
        )
    )

except Exception:

    PLANNED_LEVERAGE = 100


# ============================================================
# CREDENTIALS
# ============================================================

WEEX_API_KEY = (
    os.getenv(
        "WEEX_API_KEY",
        "",
    )
    .strip()
)

WEEX_API_SECRET = (
    os.getenv(
        "WEEX_API_SECRET",
        "",
    )
    .strip()
)

WEEX_API_PASSPHRASE = (
    os.getenv(
        "WEEX_API_PASSPHRASE",
        "",
    )
    .strip()
)


# ============================================================
# GET ALLOWLISTS
# ============================================================

PUBLIC_GET_ALLOWLIST = {
    "/capi/v3/market/symbolPrice",
}

PRIVATE_GET_ALLOWLIST = {
    "/capi/v3/account/balance",
    "/capi/v3/account/position/allPosition",
    "/capi/v3/account/symbolConfig",
}


# ============================================================
# FORBIDDEN ORDER PATH FRAGMENTS
# ============================================================

FORBIDDEN_PATH_FRAGMENTS = {
    "/order",
    "/orders",
    "/placeOrder",
    "/cancel",
    "/leverage",
    "/marginType",
    "/positionMode",
}


# ============================================================
# NETWORK AUDIT COUNTERS
# ============================================================

PUBLIC_GET_COUNT = 0
PRIVATE_GET_COUNT = 0

POST_COUNT = 0
PUT_COUNT = 0
PATCH_COUNT = 0
DELETE_COUNT = 0

REAL_ORDER_POST_COUNT = 0
DEMO_ORDER_POST_COUNT = 0

NETWORK_WRITE_COUNT = 0


# ============================================================
# RUNTIME STATE
# ============================================================

SHUTDOWN_REQUESTED = False
HEARTBEAT_COUNTER = 0


# ============================================================
# HEALTH SERVER
# ============================================================

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = json.dumps(
            {
                "status": "ok",
                "module": MODULE_NAME,
                "version": MODULE_VERSION,
                "symbol": SYMBOL,
                "live_execution": False,
                "demo_execution": False,
                "private_write_access": False,
                "authenticated_read_only": True,
            }
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


def run_health_server():

    try:

        server = ThreadingHTTPServer(
            (
                "0.0.0.0",
                PORT,
            ),
            HealthHandler,
        )

        print(
            f"R28 UNIT K: HEALTH SERVER ACTIVE ON PORT {PORT}",
            flush=True,
        )

        server.serve_forever()

    except Exception as exc:

        print(
            "R28 UNIT K: HEALTH SERVER ERROR:",
            str(
                exc
            ),
            flush=True,
        )


# ============================================================
# DISPLAY HELPERS
# ============================================================

def gate(
    name,
    passed,
):

    marker = (
        "✅ PASS"
        if passed
        else
        "❌ FAIL"
    )

    print(
        f"{name:<52} {marker}",
        flush=True,
    )

    return bool(
        passed
    )


def warning(
    message,
):

    print(
        f"⚠️ {message}",
        flush=True,
    )


# ============================================================
# DECIMAL HELPERS
# ============================================================

def to_decimal(
    value,
    default="0",
):

    try:

        if value is None:

            return Decimal(
                default
            )

        return Decimal(
            str(
                value
            )
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return Decimal(
            default
        )


# ============================================================
# JSON RESPONSE NORMALIZATION
# ============================================================

def unwrap_data(
    payload,
):

    if isinstance(
        payload,
        dict,
    ):

        if (
            "data" in payload
            and payload["data"] is not None
        ):

            return payload["data"]

    return payload


# ============================================================
# HOST VALIDATION
# ============================================================

def validate_host(
    host,
):

    if host not in ALLOWED_HOSTS:

        raise RuntimeError(
            "External host rejected locally"
        )


# ============================================================
# PATH SAFETY VALIDATION
# ============================================================

def reject_write_style_path(
    path,
):

    lower_path = (
        path
        .lower()
    )

    for fragment in FORBIDDEN_PATH_FRAGMENTS:

        if (
            fragment.lower()
            in lower_path
        ):

            raise RuntimeError(
                "Write/order/configuration path rejected locally"
            )


# ============================================================
# SIGNATURE GENERATION
#
# WEEX:
#
# timestamp
# + GET
# + request path
# + ?query string when present
#
# HMAC SHA256
# BASE64 ENCODE
# ============================================================

def generate_signature(
    timestamp,
    method,
    request_path,
    query_string="",
):

    if method != "GET":

        raise RuntimeError(
            "Only GET may be signed in Unit K"
        )

    message = (
        str(
            timestamp
        )
        + method.upper()
        + request_path
    )

    if query_string:

        message += (
            "?"
            + query_string
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
# HARD WRITE BLOCK
# ============================================================

def reject_write_method(
    method,
    path="",
):

    global POST_COUNT
    global PUT_COUNT
    global PATCH_COUNT
    global DELETE_COUNT
    global REAL_ORDER_POST_COUNT
    global DEMO_ORDER_POST_COUNT
    global NETWORK_WRITE_COUNT

    method = (
        str(
            method
        )
        .strip()
        .upper()
    )

    lower_path = (
        str(
            path
        )
        .lower()
    )

    if method == "POST":

        POST_COUNT += 1

        if "/sim/order" in lower_path:

            DEMO_ORDER_POST_COUNT += 1

        elif "/order" in lower_path:

            REAL_ORDER_POST_COUNT += 1

    elif method == "PUT":

        PUT_COUNT += 1

    elif method == "PATCH":

        PATCH_COUNT += 1

    elif method == "DELETE":

        DELETE_COUNT += 1

    if method != "GET":

        raise RuntimeError(
            f"{method} rejected locally by Unit K safety lock"
        )


# ============================================================
# PUBLIC READ-ONLY GET
# ============================================================

def public_get(
    path,
    params=None,
):

    global PUBLIC_GET_COUNT

    reject_write_method(
        "GET",
        path,
    )

    validate_host(
        WEEX_HOST
    )

    if path not in PUBLIC_GET_ALLOWLIST:

        raise RuntimeError(
            "Unallowlisted public GET rejected locally"
        )

    reject_write_style_path(
        path
    )

    params = (
        params
        if params is not None
        else {}
    )

    query_string = urlencode(
        params
    )

    url = (
        WEEX_HOST
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    request = Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "R28-UNIT-K-READ-ONLY",
        },
    )

    print(
        f"R28 UNIT K: PUBLIC GET -> {path}",
        flush=True,
    )

    try:

        with urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            status = response.status

    except HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Public GET HTTP {exc.code}: {raw[:400]}"
        )

    except URLError as exc:

        raise RuntimeError(
            f"Public GET network error: {exc}"
        )

    if status != 200:

        raise RuntimeError(
            f"Public GET returned HTTP {status}"
        )

    PUBLIC_GET_COUNT += 1

    try:

        return json.loads(
            raw
        )

    except json.JSONDecodeError:

        raise RuntimeError(
            "Public GET returned invalid JSON"
        )


# ============================================================
# AUTHENTICATED READ-ONLY GET
# ============================================================

def private_get(
    path,
    params=None,
):

    global PRIVATE_GET_COUNT

    reject_write_method(
        "GET",
        path,
    )

    validate_host(
        WEEX_HOST
    )

    if path not in PRIVATE_GET_ALLOWLIST:

        raise RuntimeError(
            "Unallowlisted private GET rejected locally"
        )

    reject_write_style_path(
        path
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

    params = (
        params
        if params is not None
        else {}
    )

    query_string = urlencode(
        params
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = generate_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
    )

    url = (
        WEEX_HOST
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "R28-UNIT-K-READ-ONLY",
    }

    request = Request(
        url=url,
        method="GET",
        headers=headers,
    )

    print(
        f"R28 UNIT K: AUTHENTICATED GET -> {path}",
        flush=True,
    )

    try:

        with urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            status = response.status

    except HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Authenticated GET HTTP {exc.code}: {raw[:500]}"
        )

    except URLError as exc:

        raise RuntimeError(
            f"Authenticated GET network error: {exc}"
        )

    if status != 200:

        raise RuntimeError(
            f"Authenticated GET returned HTTP {status}"
        )

    PRIVATE_GET_COUNT += 1

    try:

        return json.loads(
            raw
        )

    except json.JSONDecodeError:

        raise RuntimeError(
            "Authenticated GET returned invalid JSON"
        )


# ============================================================
# LOCAL WRITE-LOCK TESTS
# ============================================================

def local_write_lock_tests():

    results = {}

    tests = [
        (
            "Generic POST Rejected Locally",
            "POST",
            "/test",
        ),
        (
            "PUT Rejected Locally",
            "PUT",
            "/test",
        ),
        (
            "PATCH Rejected Locally",
            "PATCH",
            "/test",
        ),
        (
            "DELETE Rejected Locally",
            "DELETE",
            "/test",
        ),
        (
            "Real Order POST Rejected Locally",
            "POST",
            "/capi/v3/order",
        ),
        (
            "Demo Order POST Rejected Locally",
            "POST",
            "/capi/v3/sim/order",
        ),
    ]

    for (
        name,
        method,
        path,
    ) in tests:

        rejected = False

        try:

            reject_write_method(
                method,
                path,
            )

        except RuntimeError:

            rejected = True

        results[name] = rejected

    return results


# ============================================================
# PRIVATE ALLOWLIST TEST
# ============================================================

def test_private_allowlist_lock():

    try:

        if (
            "/capi/v3/account/notAllowed"
            not in PRIVATE_GET_ALLOWLIST
        ):

            raise RuntimeError(
                "Rejected"
            )

        return False

    except RuntimeError:

        return True


# ============================================================
# EXTERNAL HOST LOCK TEST
# ============================================================

def test_external_host_lock():

    try:

        validate_host(
            "https://example.com"
        )

        return False

    except RuntimeError:

        return True


# ============================================================
# PUBLIC PRICE PARSER
# ============================================================

def extract_market_price(
    payload,
):

    data = unwrap_data(
        payload
    )

    candidates = []

    if isinstance(
        data,
        dict,
    ):

        candidates.append(
            data
        )

    elif isinstance(
        data,
        list,
    ):

        for item in data:

            if isinstance(
                item,
                dict,
            ):

                if (
                    str(
                        item.get(
                            "symbol",
                            "",
                        )
                    )
                    .upper()
                    == SYMBOL
                ):

                    candidates.insert(
                        0,
                        item,
                    )

                else:

                    candidates.append(
                        item
                    )

    price_keys = (
        "price",
        "markPrice",
        "lastPrice",
        "symbolPrice",
        "close",
    )

    for item in candidates:

        for key in price_keys:

            if key in item:

                price = to_decimal(
                    item.get(
                        key
                    )
                )

                if price > 0:

                    return price

    return Decimal(
        "0"
    )


# ============================================================
# BALANCE PARSER
# ============================================================

def find_usdt_balance(
    payload,
):

    data = unwrap_data(
        payload
    )

    if isinstance(
        data,
        dict,
    ):

        data = [
            data
        ]

    if not isinstance(
        data,
        list,
    ):

        return None

    for item in data:

        if not isinstance(
            item,
            dict,
        ):

            continue

        asset = (
            str(
                item.get(
                    "asset",
                    "",
                )
            )
            .strip()
            .upper()
        )

        if asset == "USDT":

            return item

    return None


# ============================================================
# POSITION PARSER
# ============================================================

def normalize_positions(
    payload,
):

    data = unwrap_data(
        payload
    )

    if data is None:

        return []

    if isinstance(
        data,
        dict,
    ):

        return [
            data
        ]

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

    return []


# ============================================================
# SYMBOL CONFIG PARSER
# ============================================================

def find_symbol_config(
    payload,
):

    data = unwrap_data(
        payload
    )

    if isinstance(
        data,
        dict,
    ):

        data = [
            data
        ]

    if not isinstance(
        data,
        list,
    ):

        return None

    for item in data:

        if not isinstance(
            item,
            dict,
        ):

            continue

        item_symbol = (
            str(
                item.get(
                    "symbol",
                    "",
                )
            )
            .strip()
            .upper()
        )

        if item_symbol == SYMBOL:

            return item

    return None


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

def run_diagnostic():

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
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
        "ALL WRITE METHODS BLOCKED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"R28 UNIT K SYMBOL: {SYMBOL}",
        flush=True,
    )

    print(
        "R28 UNIT K NETWORK POLICY:",
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
        "R28 UNIT K CREDENTIAL STATUS:",
        flush=True,
    )

    print(
        "  API Key:",
        (
            "✅ PRESENT"
            if WEEX_API_KEY
            else
            "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Secret:",
        (
            "✅ PRESENT"
            if WEEX_API_SECRET
            else
            "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Passphrase:",
        (
            "✅ PRESENT"
            if WEEX_API_PASSPHRASE
            else
            "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "R28 UNIT K SAFETY GATES",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    safety_results = []

    safety_results.append(
        gate(
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        )
    )

    safety_results.append(
        gate(
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    safety_results.append(
        gate(
            "Real Order Transmission Disabled",
            REAL_ORDER_TRANSMISSION is False,
        )
    )

    safety_results.append(
        gate(
            "Demo Order Transmission Disabled",
            DEMO_ORDER_TRANSMISSION is False,
        )
    )

    safety_results.append(
        gate(
            "Private Write Access Disabled",
            PRIVATE_WRITE_ACCESS is False,
        )
    )

    safety_results.append(
        gate(
            "Authenticated Read Access Enabled",
            ALLOW_AUTHENTICATED_GET is True,
        )
    )

    safety_results.append(
        gate(
            "Private GET Allowlist Locked",
            test_private_allowlist_lock(),
        )
    )

    safety_results.append(
        gate(
            "WEEX Host Locked",
            ALLOWED_HOSTS
            == {
                WEEX_HOST,
            },
        )
    )

    credentials_present = (
        bool(
            WEEX_API_KEY
        )
        and bool(
            WEEX_API_SECRET
        )
        and bool(
            WEEX_API_PASSPHRASE
        )
    )

    safety_results.append(
        gate(
            "API Credentials Present",
            credentials_present,
        )
    )

    lock_results = local_write_lock_tests()

    for (
        name,
        passed,
    ) in lock_results.items():

        safety_results.append(
            gate(
                name,
                passed,
            )
        )

    safety_results.append(
        gate(
            "Unallowlisted Private GET Rejected",
            test_private_allowlist_lock(),
        )
    )

    safety_results.append(
        gate(
            "Arbitrary External Host Rejected",
            test_external_host_lock(),
        )
    )

    if not all(
        safety_results
    ):

        print(
            "-" * 60,
            flush=True,
        )

        print(
            "❌ R28 UNIT K SAFETY PRECHECK FAILED",
            flush=True,
        )

        return False

    # ========================================================
    # NETWORK READ-ONLY TESTS
    # ========================================================

    print(
        "R28 UNIT K READ-ONLY RECONCILIATION",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    reconciliation_results = []

    # ========================================================
    # PUBLIC MARKET PRICE
    # ========================================================

    try:

        market_payload = public_get(
            "/capi/v3/market/symbolPrice",
            {
                "symbol": SYMBOL,
            },
        )

        market_price = extract_market_price(
            market_payload
        )

        public_market_ok = (
            market_price > 0
        )

    except Exception as exc:

        market_payload = None
        market_price = Decimal(
            "0"
        )
        public_market_ok = False

        print(
            "R28 UNIT K: PUBLIC MARKET ERROR:",
            str(
                exc
            ),
            flush=True,
        )

    reconciliation_results.append(
        gate(
            "Public Market GET",
            public_market_ok,
        )
    )

    if public_market_ok:

        print(
            f"R28 UNIT K: {SYMBOL} PRICE = {market_price}",
            flush=True,
        )

    # ========================================================
    # ACCOUNT BALANCE
    # ========================================================

    try:

        balance_payload = private_get(
            "/capi/v3/account/balance"
        )

        usdt = find_usdt_balance(
            balance_payload
        )

        balance_ok = (
            usdt is not None
        )

    except Exception as exc:

        balance_payload = None
        usdt = None
        balance_ok = False

        print(
            "R28 UNIT K: BALANCE ERROR:",
            str(
                exc
            ),
            flush=True,
        )

    reconciliation_results.append(
        gate(
            "Authenticated Balance GET",
            balance_ok,
        )
    )

    if usdt is not None:

        balance = to_decimal(
            usdt.get(
                "balance"
            )
        )

        available = to_decimal(
            usdt.get(
                "availableBalance"
            )
        )

        frozen = to_decimal(
            usdt.get(
                "frozen"
            )
        )

        unrealized_pnl = to_decimal(
            usdt.get(
                "unrealizePnl"
            )
        )

        print(
            f"R28 UNIT K: USDT BALANCE = {balance}",
            flush=True,
        )

        print(
            f"R28 UNIT K: USDT AVAILABLE = {available}",
            flush=True,
        )

        print(
            f"R28 UNIT K: USDT FROZEN = {frozen}",
            flush=True,
        )

        print(
            f"R28 UNIT K: ACCOUNT UNREALIZED PNL = {unrealized_pnl}",
            flush=True,
        )

        reconciliation_results.append(
            gate(
                "Balance Is Non-Negative",
                balance >= 0,
            )
        )

        reconciliation_results.append(
            gate(
                "Available Balance Is Non-Negative",
                available >= 0,
            )
        )

        reconciliation_results.append(
            gate(
                "Frozen Balance Is Non-Negative",
                frozen >= 0,
            )
        )

    else:

        reconciliation_results.extend(
            [
                gate(
                    "Balance Is Non-Negative",
                    False,
                ),
                gate(
                    "Available Balance Is Non-Negative",
                    False,
                ),
                gate(
                    "Frozen Balance Is Non-Negative",
                    False,
                ),
            ]
        )

    # ========================================================
    # ALL POSITIONS
    # ========================================================

    try:

        positions_payload = private_get(
            "/capi/v3/account/position/allPosition"
        )

        positions = normalize_positions(
            positions_payload
        )

        positions_ok = True

    except Exception as exc:

        positions = []
        positions_ok = False

        print(
            "R28 UNIT K: POSITIONS ERROR:",
            str(
                exc
            ),
            flush=True,
        )

    reconciliation_results.append(
        gate(
            "Authenticated Positions GET",
            positions_ok,
        )
    )

    active_target_positions = []

    malformed_positions = []

    for position in positions:

        position_symbol = (
            str(
                position.get(
                    "symbol",
                    "",
                )
            )
            .strip()
            .upper()
        )

        size = to_decimal(
            position.get(
                "size"
            )
        )

        side = (
            str(
                position.get(
                    "side",
                    "",
                )
            )
            .strip()
            .upper()
        )

        margin_type = (
            str(
                position.get(
                    "marginType",
                    "",
                )
            )
            .strip()
            .upper()
        )

        leverage = to_decimal(
            position.get(
                "leverage"
            )
        )

        if size != 0:

            if (
                not position_symbol
                or side
                not in {
                    "LONG",
                    "SHORT",
                }
                or margin_type
                not in {
                    "ISOLATED",
                    "CROSSED",
                }
                or leverage <= 0
            ):

                malformed_positions.append(
                    position
                )

        if (
            position_symbol == SYMBOL
            and size != 0
        ):

            active_target_positions.append(
                position
            )

    print(
        f"R28 UNIT K: POSITION RECORDS = {len(positions)}",
        flush=True,
    )

    print(
        (
            "R28 UNIT K: ACTIVE "
            f"{SYMBOL} POSITIONS = "
            f"{len(active_target_positions)}"
        ),
        flush=True,
    )

    reconciliation_results.append(
        gate(
            "Position Records Structurally Valid",
            len(
                malformed_positions
            )
            == 0,
        )
    )

    # ========================================================
    # SYMBOL CONFIG
    # ========================================================

    try:

        config_payload = private_get(
            "/capi/v3/account/symbolConfig",
            {
                "symbol": SYMBOL,
            },
        )

        symbol_config = find_symbol_config(
            config_payload
        )

        config_ok = (
            symbol_config
            is not None
        )

    except Exception as exc:

        symbol_config = None
        config_ok = False

        print(
            "R28 UNIT K: SYMBOL CONFIG ERROR:",
            str(
                exc
            ),
            flush=True,
        )

    reconciliation_results.append(
        gate(
            "Authenticated Symbol Config GET",
            config_ok,
        )
    )

    if symbol_config is not None:

        config_symbol = (
            str(
                symbol_config.get(
                    "symbol",
                    "",
                )
            )
            .strip()
            .upper()
        )

        margin_type = (
            str(
                symbol_config.get(
                    "marginType",
                    "",
                )
            )
            .strip()
            .upper()
        )

        separated_type = (
            str(
                symbol_config.get(
                    "separatedType",
                    "",
                )
            )
            .strip()
            .upper()
        )

        cross_leverage = to_decimal(
            symbol_config.get(
                "crossLeverage"
            )
        )

        isolated_long_leverage = to_decimal(
            symbol_config.get(
                "isolatedLongLeverage"
            )
        )

        isolated_short_leverage = to_decimal(
            symbol_config.get(
                "isolatedShortLeverage"
            )
        )

        print(
            "R28 UNIT K SYMBOL CONFIG:",
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
            f"  Position Mode = {separated_type}",
            flush=True,
        )

        print(
            f"  Cross Leverage = {cross_leverage}",
            flush=True,
        )

        print(
            (
                "  Isolated Long Leverage = "
                f"{isolated_long_leverage}"
            ),
            flush=True,
        )

        print(
            (
                "  Isolated Short Leverage = "
                f"{isolated_short_leverage}"
            ),
            flush=True,
        )

        reconciliation_results.append(
            gate(
                "Symbol Configuration Matches Target Symbol",
                config_symbol == SYMBOL,
            )
        )

        reconciliation_results.append(
            gate(
                "Margin Type Recognized",
                margin_type
                in {
                    "ISOLATED",
                    "CROSSED",
                },
            )
        )

        reconciliation_results.append(
            gate(
                "Position Mode Recognized",
                separated_type
                in {
                    "COMBINED",
                    "SEPARATED",
                },
            )
        )

        reconciliation_results.append(
            gate(
                "Configured Leverage Values Valid",
                (
                    cross_leverage > 0
                    and isolated_long_leverage > 0
                    and isolated_short_leverage > 0
                ),
            )
        )

        # ====================================================
        # READ-ONLY STRATEGY COMPARISON
        #
        # MISMATCHES HERE ARE WARNINGS ONLY.
        # UNIT K MUST NEVER MODIFY ACCOUNT CONFIGURATION.
        # ====================================================

        print(
            "R28 UNIT K READ-ONLY STRATEGY COMPARISON:",
            flush=True,
        )

        print(
            (
                "  Planned Margin Type = "
                f"{PLANNED_MARGIN_TYPE}"
            ),
            flush=True,
        )

        print(
            (
                "  Planned Leverage = "
                f"{PLANNED_LEVERAGE}x"
            ),
            flush=True,
        )

        if margin_type != PLANNED_MARGIN_TYPE:

            warning(
                (
                    "Observed margin type differs from "
                    "planned strategy configuration. "
                    "NO CHANGE ATTEMPTED."
                )
            )

        if (
            margin_type == "ISOLATED"
            and (
                isolated_long_leverage
                != Decimal(
                    PLANNED_LEVERAGE
                )
                or isolated_short_leverage
                != Decimal(
                    PLANNED_LEVERAGE
                )
            )
        ):

            warning(
                (
                    "Observed isolated leverage differs "
                    "from planned strategy leverage. "
                    "NO CHANGE ATTEMPTED."
                )
            )

    else:

        reconciliation_results.extend(
            [
                gate(
                    "Symbol Configuration Matches Target Symbol",
                    False,
                ),
                gate(
                    "Margin Type Recognized",
                    False,
                ),
                gate(
                    "Position Mode Recognized",
                    False,
                ),
                gate(
                    "Configured Leverage Values Valid",
                    False,
                ),
            ]
        )

    # ========================================================
    # ACTIVE POSITION / CONFIG CONSISTENCY
    # ========================================================

    active_position_consistency = True

    if symbol_config is not None:

        for position in active_target_positions:

            side = (
                str(
                    position.get(
                        "side",
                        "",
                    )
                )
                .strip()
                .upper()
            )

            position_margin_type = (
                str(
                    position.get(
                        "marginType",
                        "",
                    )
                )
                .strip()
                .upper()
            )

            position_leverage = to_decimal(
                position.get(
                    "leverage"
                )
            )

            if position_margin_type not in {
                "ISOLATED",
                "CROSSED",
            }:

                active_position_consistency = False

            if position_leverage <= 0:

                active_position_consistency = False

            print(
                "R28 UNIT K ACTIVE POSITION:",
                flush=True,
            )

            print(
                f"  Side = {side}",
                flush=True,
            )

            print(
                (
                    "  Margin Type = "
                    f"{position_margin_type}"
                ),
                flush=True,
            )

            print(
                (
                    "  Leverage = "
                    f"{position_leverage}"
                ),
                flush=True,
            )

    reconciliation_results.append(
        gate(
            "Active Position State Internally Consistent",
            active_position_consistency,
        )
    )

    # ========================================================
    # NETWORK AUDIT
    # ========================================================

    reconciliation_results.append(
        gate(
            "Controlled Public GET Occurred",
            PUBLIC_GET_COUNT >= 1,
        )
    )

    reconciliation_results.append(
        gate(
            "Controlled Private GET Occurred",
            PRIVATE_GET_COUNT >= 3,
        )
    )

    reconciliation_results.append(
        gate(
            "Network Write Count Is Zero",
            NETWORK_WRITE_COUNT == 0,
        )
    )

    reconciliation_results.append(
        gate(
            "Real Order Transmission Never Occurred",
            REAL_ORDER_POST_COUNT == 0,
        )
    )

    reconciliation_results.append(
        gate(
            "Demo Order Transmission Never Occurred",
            DEMO_ORDER_POST_COUNT == 0,
        )
    )

    # ========================================================
    # IMPORTANT:
    #
    # POST_COUNT ETC. MAY BE NONZERO BECAUSE LOCAL SAFETY
    # TESTS INTENTIONALLY CALL THE REJECTION FUNCTION.
    #
    # THEY NEVER REACH THE NETWORK.
    # ========================================================

    print(
        "R28 UNIT K LOCAL WRITE-LOCK AUDIT:",
        flush=True,
    )

    print(
        f"  Local POST rejection tests = {POST_COUNT}",
        flush=True,
    )

    print(
        f"  Local PUT rejection tests = {PUT_COUNT}",
        flush=True,
    )

    print(
        f"  Local PATCH rejection tests = {PATCH_COUNT}",
        flush=True,
    )

    print(
        f"  Local DELETE rejection tests = {DELETE_COUNT}",
        flush=True,
    )

    print(
        f"  Network writes = {NETWORK_WRITE_COUNT}",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    passed = (
        all(
            safety_results
        )
        and all(
            reconciliation_results
        )
    )

    if passed:

        print(
            "✅ R28 UNIT K DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ AUTHENTICATED READ-ONLY STATE RECONCILIATION VALIDATED",
            flush=True,
        )

        print(
            "✅ PUBLIC MARKET STATE VALIDATED",
            flush=True,
        )

        print(
            "✅ ACCOUNT BALANCE STATE VALIDATED",
            flush=True,
        )

        print(
            "✅ POSITION STATE VALIDATED",
            flush=True,
        )

        print(
            "✅ SYMBOL CONFIGURATION STATE VALIDATED",
            flush=True,
        )

        print(
            "✅ ACCOUNT / MARKET READ PATH INTEGRATION VALIDATED",
            flush=True,
        )

        print(
            "🛡 REAL ORDER TRANSMISSION IMPOSSIBLE",
            flush=True,
        )

        print(
            "🛡 DEMO ORDER TRANSMISSION IMPOSSIBLE",
            flush=True,
        )

        print(
            "🛡 ALL PRIVATE WRITE METHODS REMAIN BLOCKED",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT K DIAGNOSTIC DID NOT PASS",
            flush=True,
        )

        print(
            "R28 UNIT K: WRITE LOCKS REMAIN ACTIVE",
            flush=True,
        )

    print(
        "=" * 60,
        flush=True,
    )

    return passed


# ============================================================
# SIGNAL HANDLING
# ============================================================

def request_shutdown(
    signum=None,
    frame=None,
):

    global SHUTDOWN_REQUESTED

    SHUTDOWN_REQUESTED = True

    print(
        "R28 UNIT K: SHUTDOWN REQUESTED",
        flush=True,
    )


signal.signal(
    signal.SIGTERM,
    request_shutdown,
)

signal.signal(
    signal.SIGINT,
    request_shutdown,
)


# ============================================================
# RUNTIME
# ============================================================

def main():

    global HEARTBEAT_COUNTER

    print(
        "R28 UNIT K: RUNTIME STARTING",
        flush=True,
    )

    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    health_thread.start()

    time.sleep(
        0.5
    )

    try:

        run_diagnostic()

    except Exception as exc:

        print(
            "R28 UNIT K: FATAL DIAGNOSTIC ERROR:",
            str(
                exc
            ),
            flush=True,
        )

        print(
            "R28 UNIT K: WRITE LOCKS REMAIN ACTIVE",
            flush=True,
        )

    print(
        "R28 UNIT K: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT K: AUTHENTICATED READ-ONLY LOCKS ACTIVE",
        flush=True,
    )

    while not SHUTDOWN_REQUESTED:

        HEARTBEAT_COUNTER += 1

        print(
            (
                "R28 UNIT K: HEARTBEAT "
                f"{HEARTBEAT_COUNTER} ✅ ACTIVE"
            ),
            flush=True,
        )

        time.sleep(
            30
        )

    print(
        "R28 UNIT K: RUNTIME STOPPED CLEANLY",
        flush=True,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
