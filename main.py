# ============================================================
# 0F-4H-R28-UNIT-I
# CONTROLLED PUBLIC READ-ONLY NETWORK VALIDATION
#
# PUBLIC WEEX MARKET DATA ONLY
# NO AUTHENTICATED REQUESTS
# NO ACCOUNT REQUESTS
# NO REAL ORDER TRANSMISSION
# NO DEMO ORDER TRANSMISSION
# POST / PUT / PATCH / DELETE BLOCKED
# ============================================================

print(
    "R28 UNIT I: MAIN.PY ENTERED",
    flush=True,
)

# ============================================================
# IMPORTS
# ============================================================

import asyncio
import json
import os
import signal
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from typing import Tuple

print(
    "R28 UNIT I: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-I"
MODULE_VERSION = "R28-I"


# ============================================================
# ABSOLUTE EXECUTION SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

REAL_ORDER_TRANSMISSION = False
DEMO_ORDER_TRANSMISSION = False

HARD_REAL_POST_LOCK = True
HARD_DEMO_POST_LOCK = True

AUTHENTICATED_REQUESTS_ENABLED = False
PRIVATE_API_ENABLED = False
ACCOUNT_API_ENABLED = False

ORDER_ENDPOINTS_ENABLED = False

PUBLIC_READ_ONLY_NETWORK_ENABLED = True


# ============================================================
# NETWORK POLICY
# ============================================================

WEEX_PUBLIC_BASE_URL = (
    "https://api-contract.weex.com"
)

MAIN_SYMBOL = (
    os.getenv(
        "SYMBOL",
        "BTCUSDT",
    )
    .strip()
    .upper()
)

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv(
        "REQUEST_TIMEOUT_SECONDS",
        "10",
    )
)

HEARTBEAT_SECONDS = float(
    os.getenv(
        "HEARTBEAT_SECONDS",
        "10",
    )
)

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# ONLY THESE PUBLIC GET PATHS MAY LEAVE THE PROCESS
# ============================================================

APPROVED_PUBLIC_GET_PATHS: Set[str] = {
    "/capi/v3/market/exchangeInfo",
    "/capi/v3/market/symbolPrice",
    "/capi/v3/market/ticker/bookTicker",
}


# ============================================================
# EXPLICITLY FORBIDDEN ORDER PATHS
# ============================================================

FORBIDDEN_ORDER_PATHS: Set[str] = {
    "/capi/v3/order",
    "/capi/v3/sim/order",
}


# ============================================================
# REQUEST COUNTERS
# ============================================================

PUBLIC_GET_REQUEST_COUNT = 0
BLOCKED_REQUEST_COUNT = 0

REAL_POST_CALLED = False
DEMO_POST_CALLED = False

ORDER_TRANSMISSION_OCCURRED = False

LAST_NETWORK_ERROR: Optional[str] = None


# ============================================================
# RUNTIME STATE
# ============================================================

shutdown_event = threading.Event()

health_server: Optional[ThreadingHTTPServer] = None
health_server_thread: Optional[threading.Thread] = None


# ============================================================
# OUTPUT HELPERS
# ============================================================

def print_gate(
    name: str,
    passed: bool,
) -> None:

    status = (
        "✅ PASS"
        if passed
        else "❌ FAIL"
    )

    print(
        f"{name:<49} {status}",
        flush=True,
    )


def print_separator() -> None:

    print(
        "-" * 60,
        flush=True,
    )


# ============================================================
# URL / SECURITY HELPERS
# ============================================================

def normalize_path(
    path: str,
) -> str:

    if not isinstance(
        path,
        str,
    ):
        raise TypeError(
            "path must be a string"
        )

    path = path.strip()

    if not path:
        raise ValueError(
            "path cannot be empty"
        )

    parsed = urllib.parse.urlparse(
        path
    )

    if parsed.scheme or parsed.netloc:

        raise PermissionError(
            "Absolute external URLs are forbidden"
        )

    clean_path = parsed.path

    if not clean_path.startswith(
        "/"
    ):
        clean_path = (
            "/"
            + clean_path
        )

    return clean_path


def validate_headers(
    headers: Optional[Dict[str, str]],
) -> Dict[str, str]:

    if headers is None:

        return {
            "Accept": "application/json",
            "User-Agent": "R28-UNIT-I-READ-ONLY",
        }

    clean_headers = dict(
        headers
    )

    forbidden_header_names = {
        "ACCESS-KEY",
        "ACCESS-SIGN",
        "ACCESS-PASSPHRASE",
        "ACCESS-TIMESTAMP",
        "AUTHORIZATION",
        "X-API-KEY",
        "API-KEY",
    }

    for header_name in clean_headers:

        normalized_name = (
            str(header_name)
            .strip()
            .upper()
        )

        if normalized_name in forbidden_header_names:

            raise PermissionError(
                "Authenticated/private headers "
                "are forbidden in Unit I"
            )

    clean_headers.setdefault(
        "Accept",
        "application/json",
    )

    clean_headers.setdefault(
        "User-Agent",
        "R28-UNIT-I-READ-ONLY",
    )

    return clean_headers


# ============================================================
# CENTRAL NETWORK SAFETY GATE
# ============================================================

def validate_outbound_request(
    method: str,
    path: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[bytes] = None,
) -> Tuple[str, Dict[str, str]]:

    global BLOCKED_REQUEST_COUNT

    normalized_method = (
        str(method)
        .strip()
        .upper()
    )

    try:

        if normalized_method != "GET":

            raise PermissionError(
                "Only HTTP GET is permitted "
                "in R28 Unit I"
            )

        clean_path = normalize_path(
            path
        )

        if clean_path in FORBIDDEN_ORDER_PATHS:

            raise PermissionError(
                "Order endpoint blocked"
            )

        if clean_path not in APPROVED_PUBLIC_GET_PATHS:

            raise PermissionError(
                "Endpoint not in Unit I "
                "public GET allowlist"
            )

        if body not in {
            None,
            b"",
        }:

            raise PermissionError(
                "Request bodies are forbidden "
                "in Unit I"
            )

        clean_headers = validate_headers(
            headers
        )

        return (
            clean_path,
            clean_headers,
        )

    except Exception:

        BLOCKED_REQUEST_COUNT += 1

        raise


# ============================================================
# HARD BLOCK FOR ALL WRITE METHODS
# ============================================================

def hard_blocked_post(
    *args: Any,
    **kwargs: Any,
) -> None:

    global BLOCKED_REQUEST_COUNT

    BLOCKED_REQUEST_COUNT += 1

    raise PermissionError(
        "HTTP POST is permanently blocked "
        "in R28 Unit I"
    )


def hard_blocked_put(
    *args: Any,
    **kwargs: Any,
) -> None:

    global BLOCKED_REQUEST_COUNT

    BLOCKED_REQUEST_COUNT += 1

    raise PermissionError(
        "HTTP PUT is permanently blocked "
        "in R28 Unit I"
    )


def hard_blocked_patch(
    *args: Any,
    **kwargs: Any,
) -> None:

    global BLOCKED_REQUEST_COUNT

    BLOCKED_REQUEST_COUNT += 1

    raise PermissionError(
        "HTTP PATCH is permanently blocked "
        "in R28 Unit I"
    )


def hard_blocked_delete(
    *args: Any,
    **kwargs: Any,
) -> None:

    global BLOCKED_REQUEST_COUNT

    BLOCKED_REQUEST_COUNT += 1

    raise PermissionError(
        "HTTP DELETE is permanently blocked "
        "in R28 Unit I"
    )


# ============================================================
# THE ONLY FUNCTION ALLOWED TO ACCESS WEEX
# ============================================================

def public_get_json(
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    global PUBLIC_GET_REQUEST_COUNT
    global LAST_NETWORK_ERROR

    if not PUBLIC_READ_ONLY_NETWORK_ENABLED:

        raise PermissionError(
            "Public network disabled"
        )

    clean_path, headers = (
        validate_outbound_request(
            method="GET",
            path=path,
            headers=None,
            body=None,
        )
    )

    query_string = ""

    if params:

        query_string = urllib.parse.urlencode(
            params
        )

    url = (
        WEEX_PUBLIC_BASE_URL
        + clean_path
    )

    if query_string:

        url = (
            url
            + "?"
            + query_string
        )

    request = urllib.request.Request(
        url=url,
        data=None,
        headers=headers,
        method="GET",
    )

    PUBLIC_GET_REQUEST_COUNT += 1

    print(
        "R28 UNIT I: PUBLIC GET -> "
        f"{clean_path}",
        flush=True,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            status_code = getattr(
                response,
                "status",
                200,
            )

            raw_body = response.read()

        if status_code < 200 or status_code >= 300:

            raise RuntimeError(
                "Unexpected HTTP status: "
                f"{status_code}"
            )

        decoded_body = raw_body.decode(
            "utf-8"
        )

        data = json.loads(
            decoded_body
        )

        LAST_NETWORK_ERROR = None

        return data

    except urllib.error.HTTPError as exc:

        LAST_NETWORK_ERROR = (
            f"HTTP {exc.code}: {exc.reason}"
        )

        raise RuntimeError(
            LAST_NETWORK_ERROR
        ) from exc

    except urllib.error.URLError as exc:

        LAST_NETWORK_ERROR = (
            f"Network error: {exc.reason}"
        )

        raise RuntimeError(
            LAST_NETWORK_ERROR
        ) from exc

    except TimeoutError as exc:

        LAST_NETWORK_ERROR = (
            "Network request timed out"
        )

        raise RuntimeError(
            LAST_NETWORK_ERROR
        ) from exc


# ============================================================
# PUBLIC MARKET DATA FUNCTIONS
# ============================================================

def get_exchange_info(
    symbol: str,
) -> Any:

    return public_get_json(
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": symbol,
        },
    )


def get_mark_price(
    symbol: str,
) -> Any:

    return public_get_json(
        "/capi/v3/market/symbolPrice",
        {
            "symbol": symbol,
            "priceType": "MARK",
        },
    )


def get_book_ticker(
    symbol: str,
) -> Any:

    return public_get_json(
        "/capi/v3/market/ticker/bookTicker",
        {
            "symbol": symbol,
        },
    )


# ============================================================
# DATA VALIDATION
# ============================================================

def validate_mark_price_response(
    data: Any,
    symbol: str,
) -> float:

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "Mark price response must be an object"
        )

    response_symbol = (
        str(
            data.get(
                "symbol",
                "",
            )
        )
        .strip()
        .upper()
    )

    if response_symbol != symbol:

        raise ValueError(
            "Mark price symbol mismatch: "
            f"{response_symbol}"
        )

    price_raw = data.get(
        "price"
    )

    if price_raw is None:

        raise ValueError(
            "Mark price missing"
        )

    price = float(
        price_raw
    )

    if price <= 0:

        raise ValueError(
            "Mark price must be positive"
        )

    return price


def validate_book_ticker_response(
    data: Any,
    symbol: str,
) -> Tuple[float, float]:

    record = data

    if isinstance(
        data,
        list,
    ):

        if not data:

            raise ValueError(
                "Book ticker response is empty"
            )

        record = data[0]

    if not isinstance(
        record,
        dict,
    ):

        raise ValueError(
            "Book ticker record invalid"
        )

    response_symbol = (
        str(
            record.get(
                "symbol",
                "",
            )
        )
        .strip()
        .upper()
    )

    if response_symbol != symbol:

        raise ValueError(
            "Book ticker symbol mismatch: "
            f"{response_symbol}"
        )

    bid = float(
        record.get(
            "bidPrice",
            "0",
        )
    )

    ask = float(
        record.get(
            "askPrice",
            "0",
        )
    )

    if bid <= 0:

        raise ValueError(
            "Bid price must be positive"
        )

    if ask <= 0:

        raise ValueError(
            "Ask price must be positive"
        )

    if ask < bid:

        raise ValueError(
            "Ask cannot be below bid"
        )

    return (
        bid,
        ask,
    )


def validate_exchange_info_response(
    data: Any,
    symbol: str,
) -> bool:

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "Exchange info response must be an object"
        )

    symbols = data.get(
        "symbols"
    )

    if not isinstance(
        symbols,
        list,
    ):

        raise ValueError(
            "Exchange info symbols missing"
        )

    for record in symbols:

        if not isinstance(
            record,
            dict,
        ):

            continue

        response_symbol = (
            str(
                record.get(
                    "symbol",
                    "",
                )
            )
            .strip()
            .upper()
        )

        if response_symbol == symbol:

            return True

    raise ValueError(
        f"{symbol} not found in exchange info"
    )


# ============================================================
# LOCAL SAFETY TEST HELPERS
# ============================================================

def expect_permission_error(
    callback,
) -> bool:

    try:

        callback()

    except PermissionError:

        return True

    except Exception:

        return False

    return False


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        if self.path in {
            "/",
            "/health",
            "/healthz",
        }:

            payload = json.dumps(
                {
                    "status": "ok",
                    "module": MODULE_NAME,
                    "version": MODULE_VERSION,
                    "mode": "PUBLIC_READ_ONLY",
                    "live_execution": False,
                    "demo_execution": False,
                    "order_transmission": False,
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
                        payload
                    )
                ),
            )

            self.end_headers()

            self.wfile.write(
                payload
            )

            return

        self.send_response(
            404
        )

        self.end_headers()

    def do_POST(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()

    def do_PUT(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()

    def do_PATCH(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()

    def do_DELETE(
        self,
    ) -> None:

        self.send_response(
            405
        )

        self.end_headers()

    def log_message(
        self,
        format,
        *args,
    ) -> None:

        return


def start_health_server() -> None:

    global health_server
    global health_server_thread

    health_server = ThreadingHTTPServer(
        (
            "0.0.0.0",
            PORT,
        ),
        HealthHandler,
    )

    health_server_thread = threading.Thread(
        target=health_server.serve_forever,
        daemon=True,
        name="r28-unit-i-health",
    )

    health_server_thread.start()

    print(
        "R28 UNIT I: HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}",
        flush=True,
    )


def stop_health_server() -> None:

    global health_server

    if health_server is None:

        return

    try:

        health_server.shutdown()

    except Exception:

        pass

    try:

        health_server.server_close()

    except Exception:

        pass


# ============================================================
# DIAGNOSTIC
# ============================================================

def run_diagnostic() -> bool:

    global REAL_POST_CALLED
    global DEMO_POST_CALLED
    global ORDER_TRANSMISSION_OCCURRED

    print(
        "=" * 60,
        flush=True,
    )

    print(
        "0F-4H-R28-UNIT-I STARTING",
        flush=True,
    )

    print(
        "CONTROLLED PUBLIC READ-ONLY NETWORK VALIDATION",
        flush=True,
    )

    print(
        "PUBLIC WEEX MARKET DATA GET REQUESTS ONLY",
        flush=True,
    )

    print(
        "NO AUTHENTICATED API ACCESS",
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
        f"R28 UNIT I SYMBOL: {MAIN_SYMBOL}",
        flush=True,
    )

    print(
        "R28 UNIT I NETWORK POLICY:",
        flush=True,
    )

    print(
        "  ✅ Public market GET enabled",
        flush=True,
    )

    print(
        "  ❌ Authenticated API disabled",
        flush=True,
    )

    print(
        "  ❌ Account API disabled",
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
        "",
        flush=True,
    )

    print(
        "R28 UNIT I SAFETY GATES",
        flush=True,
    )

    print_separator()

    results = []

    result = (
        LIVE_ORDER_EXECUTION is False
        and
        DEMO_ORDER_EXECUTION is False
        and
        REAL_ORDER_TRANSMISSION is False
        and
        DEMO_ORDER_TRANSMISSION is False
        and
        HARD_REAL_POST_LOCK is True
        and
        HARD_DEMO_POST_LOCK is True
    )

    print_gate(
        "Execution Locks Active",
        result,
    )

    results.append(
        result
    )

    result = (
        PUBLIC_READ_ONLY_NETWORK_ENABLED
        is True
    )

    print_gate(
        "Public Read-Only Network Enabled",
        result,
    )

    results.append(
        result
    )

    result = (
        AUTHENTICATED_REQUESTS_ENABLED
        is False
        and
        PRIVATE_API_ENABLED
        is False
        and
        ACCOUNT_API_ENABLED
        is False
    )

    print_gate(
        "Authenticated / Private API Disabled",
        result,
    )

    results.append(
        result
    )

    result = (
        ORDER_ENDPOINTS_ENABLED
        is False
    )

    print_gate(
        "Order Endpoints Disabled",
        result,
    )

    results.append(
        result
    )

    result = (
        WEEX_PUBLIC_BASE_URL
        ==
        "https://api-contract.weex.com"
    )

    print_gate(
        "WEEX Public Host Locked",
        result,
    )

    results.append(
        result
    )

    expected_paths = {
        "/capi/v3/market/exchangeInfo",
        "/capi/v3/market/symbolPrice",
        "/capi/v3/market/ticker/bookTicker",
    }

    result = (
        APPROVED_PUBLIC_GET_PATHS
        ==
        expected_paths
    )

    print_gate(
        "Public GET Allowlist Locked",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: validate_outbound_request(
            method="POST",
            path="/capi/v3/order",
        )
    )

    print_gate(
        "Real Order POST Rejected Locally",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: validate_outbound_request(
            method="POST",
            path="/capi/v3/sim/order",
        )
    )

    print_gate(
        "Demo Order POST Rejected Locally",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: hard_blocked_post()
    )

    print_gate(
        "Generic POST Method Blocked",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: hard_blocked_put()
    )

    print_gate(
        "PUT Method Blocked",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: hard_blocked_patch()
    )

    print_gate(
        "PATCH Method Blocked",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: hard_blocked_delete()
    )

    print_gate(
        "DELETE Method Blocked",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: validate_outbound_request(
            method="GET",
            path="/capi/v3/account/symbolConfig",
        )
    )

    print_gate(
        "Account Endpoint Rejected Locally",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: validate_outbound_request(
            method="GET",
            path="/capi/v3/position",
        )
    )

    print_gate(
        "Private Endpoint Rejected Locally",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: validate_outbound_request(
            method="GET",
            path="/capi/v3/market/symbolPrice",
            headers={
                "ACCESS-KEY": "BLOCKED",
            },
        )
    )

    print_gate(
        "API Credential Header Rejected",
        result,
    )

    results.append(
        result
    )

    result = expect_permission_error(
        lambda: validate_outbound_request(
            method="GET",
            path="https://example.com/test",
        )
    )

    print_gate(
        "Arbitrary External Host Rejected",
        result,
    )

    results.append(
        result
    )

    # ========================================================
    # LIVE PUBLIC READ-ONLY TEST 1
    # EXCHANGE INFORMATION
    # ========================================================

    exchange_info_ok = False

    try:

        exchange_info = get_exchange_info(
            MAIN_SYMBOL
        )

        exchange_info_ok = (
            validate_exchange_info_response(
                exchange_info,
                MAIN_SYMBOL,
            )
        )

    except Exception as exc:

        print(
            "R28 UNIT I: EXCHANGE INFO ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

    print_gate(
        "Public Exchange Info GET",
        exchange_info_ok,
    )

    results.append(
        exchange_info_ok
    )

    # ========================================================
    # LIVE PUBLIC READ-ONLY TEST 2
    # MARK PRICE
    # ========================================================

    mark_price_ok = False
    mark_price = None

    try:

        mark_price_data = get_mark_price(
            MAIN_SYMBOL
        )

        mark_price = (
            validate_mark_price_response(
                mark_price_data,
                MAIN_SYMBOL,
            )
        )

        mark_price_ok = (
            mark_price > 0
        )

    except Exception as exc:

        print(
            "R28 UNIT I: MARK PRICE ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

    print_gate(
        "Public Mark Price GET",
        mark_price_ok,
    )

    results.append(
        mark_price_ok
    )

    if mark_price is not None:

        print(
            "R28 UNIT I: "
            f"{MAIN_SYMBOL} MARK PRICE = "
            f"{mark_price}",
            flush=True,
        )

    # ========================================================
    # LIVE PUBLIC READ-ONLY TEST 3
    # BEST BID / ASK
    # ========================================================

    book_ticker_ok = False
    best_bid = None
    best_ask = None

    try:

        book_data = get_book_ticker(
            MAIN_SYMBOL
        )

        best_bid, best_ask = (
            validate_book_ticker_response(
                book_data,
                MAIN_SYMBOL,
            )
        )

        book_ticker_ok = (
            best_bid > 0
            and
            best_ask > 0
            and
            best_ask >= best_bid
        )

    except Exception as exc:

        print(
            "R28 UNIT I: BOOK TICKER ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

    print_gate(
        "Public Best Bid / Ask GET",
        book_ticker_ok,
    )

    results.append(
        book_ticker_ok
    )

    if (
        best_bid is not None
        and
        best_ask is not None
    ):

        print(
            "R28 UNIT I: BEST BID = "
            f"{best_bid}",
            flush=True,
        )

        print(
            "R28 UNIT I: BEST ASK = "
            f"{best_ask}",
            flush=True,
        )

    # ========================================================
    # FINAL SAFETY ASSERTIONS
    # ========================================================

    result = (
        PUBLIC_GET_REQUEST_COUNT >= 3
    )

    print_gate(
        "Controlled Public GETs Occurred",
        result,
    )

    results.append(
        result
    )

    result = (
        REAL_POST_CALLED is False
        and
        DEMO_POST_CALLED is False
        and
        ORDER_TRANSMISSION_OCCURRED is False
    )

    print_gate(
        "No Order Transmission Occurred",
        result,
    )

    results.append(
        result
    )

    result = (
        LIVE_ORDER_EXECUTION is False
        and
        DEMO_ORDER_EXECUTION is False
        and
        ORDER_ENDPOINTS_ENABLED is False
        and
        HARD_REAL_POST_LOCK is True
        and
        HARD_DEMO_POST_LOCK is True
    )

    print_gate(
        "Final Execution Safety Assertions",
        result,
    )

    results.append(
        result
    )

    print_separator()

    all_passed = all(
        results
    )

    if all_passed:

        print(
            "✅ R28 UNIT I DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ CONTROLLED PUBLIC NETWORK ACCESS VALIDATED",
            flush=True,
        )

        print(
            "✅ WEEX PUBLIC MARKET DATA ACCESS VALIDATED",
            flush=True,
        )

        print(
            "✅ EXCHANGE INFO READ VALIDATED",
            flush=True,
        )

        print(
            "✅ MARK PRICE READ VALIDATED",
            flush=True,
        )

        print(
            "✅ BEST BID / ASK READ VALIDATED",
            flush=True,
        )

        print(
            "✅ PUBLIC GET ALLOWLIST VALIDATED",
            flush=True,
        )

        print(
            "✅ PRIVATE / ACCOUNT API BLOCKED",
            flush=True,
        )

        print(
            "✅ AUTHENTICATED REQUESTS BLOCKED",
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
            "🛡 ALL WRITE METHODS BLOCKED",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT I DIAGNOSTIC FAILED",
            flush=True,
        )

        print(
            "❌ DO NOT PROCEED TO UNIT J",
            flush=True,
        )

        if LAST_NETWORK_ERROR:

            print(
                "NETWORK ERROR: "
                f"{LAST_NETWORK_ERROR}",
                flush=True,
            )

        print(
            "🛡 EXECUTION LOCKS REMAIN ACTIVE",
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
        "=" * 60,
        flush=True,
    )

    return all_passed


# ============================================================
# SHUTDOWN HANDLING
# ============================================================

def request_shutdown(
    signum=None,
    frame=None,
) -> None:

    if shutdown_event.is_set():

        return

    print(
        "R28 UNIT I: SHUTDOWN REQUESTED",
        flush=True,
    )

    shutdown_event.set()


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime() -> None:

    print(
        "R28 UNIT I: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT I: "
        "PUBLIC READ-ONLY SAFETY LOCKS ACTIVE",
        flush=True,
    )

    heartbeat = 0

    while not shutdown_event.is_set():

        heartbeat += 1

        print(
            "R28 UNIT I: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        elapsed = 0.0

        while (
            elapsed < HEARTBEAT_SECONDS
            and
            not shutdown_event.is_set()
        ):

            step = min(
                0.5,
                HEARTBEAT_SECONDS - elapsed,
            )

            await asyncio.sleep(
                step
            )

            elapsed += step


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    print(
        "R28 UNIT I: RUNTIME STARTING",
        flush=True,
    )

    try:

        start_health_server()

        diagnostic_passed = (
            run_diagnostic()
        )

        if diagnostic_passed:

            print(
                "R28 UNIT I: READY FOR "
                "CONTROLLED READ-ONLY RUNTIME",
                flush=True,
            )

        else:

            print(
                "R28 UNIT I: DIAGNOSTIC FAILURE "
                "DETECTED",
                flush=True,
            )

            print(
                "R28 UNIT I: EXECUTION REMAINS "
                "HARD LOCKED",
                flush=True,
            )

        await persistent_runtime()

    finally:

        stop_health_server()

        print(
            "R28 UNIT I: RUNTIME STOPPED CLEANLY",
            flush=True,
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        signal.signal(
            signal.SIGTERM,
            request_shutdown,
        )

        signal.signal(
            signal.SIGINT,
            request_shutdown,
        )

    except Exception:

        pass

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        request_shutdown()

    except Exception as exc:

        print(
            "R28 UNIT I: FATAL STARTUP ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        raise
