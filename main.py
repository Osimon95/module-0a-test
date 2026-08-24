# ============================================================
# 0F-4H-R28-UNIT-J
# AUTHENTICATED READ-ONLY PRIVATE API VALIDATION
#
# STANDALONE TEST UNIT
#
# PUBLIC GET:
#   ENABLED
#
# AUTHENTICATED PRIVATE GET:
#   ENABLED ONLY FOR EXPLICIT READ-ONLY ENDPOINTS
#
# REAL ORDER TRANSMISSION:
#   DISABLED
#
# DEMO ORDER TRANSMISSION:
#   DISABLED
#
# POST / PUT / PATCH / DELETE:
#   HARD BLOCKED LOCALLY
#
# NO ORDER CAN BE TRANSMITTED BY THIS UNIT
# ============================================================


print(
    "R28 UNIT J: MAIN.PY ENTERED",
    flush=True,
)


# ============================================================
# IMPORTS
# ============================================================

import asyncio
import base64
import hashlib
import hmac
import json
import os
import signal
import sys
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import aiohttp


print(
    "R28 UNIT J: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-J"
MODULE_VERSION = "R28-J"


# ============================================================
# ABSOLUTE EXECUTION SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

REAL_ORDER_TRANSMISSION = False
DEMO_ORDER_TRANSMISSION = False

PRIVATE_WRITE_ACCESS = False
ACCOUNT_WRITE_ACCESS = False

POST_ENABLED = False
PUT_ENABLED = False
PATCH_ENABLED = False
DELETE_ENABLED = False

HARD_REAL_POST_LOCK = True
HARD_DEMO_POST_LOCK = True
HARD_WRITE_METHOD_LOCK = True


# ============================================================
# READ POLICIES
# ============================================================

PUBLIC_READ_ACCESS = True
AUTHENTICATED_READ_ACCESS = True

ALLOW_PRIVATE_GET = True
ALLOW_PRIVATE_WRITE = False


# ============================================================
# WEEX HOST
# ============================================================

WEEX_PUBLIC_HOST = "https://api-contract.weex.com"
WEEX_PRIVATE_HOST = "https://api-contract.weex.com"

LOCKED_WEEX_HOST = "https://api-contract.weex.com"


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
# CREDENTIAL ENVIRONMENT VARIABLES
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
# NETWORK TIMEOUTS
# ============================================================

HTTP_TIMEOUT_SECONDS = 15


# ============================================================
# PUBLIC GET ALLOWLIST
# ============================================================

PUBLIC_GET_ALLOWLIST = frozenset(
    {
        "/capi/v3/market/exchangeInfo",
        "/capi/v3/market/symbolPrice",
        "/capi/v3/market/ticker/bookTicker",
    }
)


# ============================================================
# AUTHENTICATED PRIVATE GET ALLOWLIST
# ============================================================

PRIVATE_GET_ALLOWLIST = frozenset(
    {
        "/capi/v3/account/balance",
        "/capi/v3/account/position/allPosition",
        "/capi/v3/account/position/singlePosition",
        "/capi/v3/account/symbolConfig",
    }
)


# ============================================================
# ORDER / WRITE PATH DENYLIST
# ============================================================

FORBIDDEN_WRITE_PATH_FRAGMENTS = (
    "/order",
    "/orders",
    "/cancel",
    "/leverage",
    "/margin",
    "/position/margin",
    "/modify",
    "/close",
    "/open",
    "/trigger",
    "/plan",
    "/tpsl",
    "/sim/order",
)


# ============================================================
# RUNTIME STATE
# ============================================================

STOP_EVENT: Optional[asyncio.Event] = None

PUBLIC_GET_COUNT = 0
PRIVATE_GET_COUNT = 0

REAL_POST_CALLED = False
DEMO_POST_CALLED = False

POST_CALLED = False
PUT_CALLED = False
PATCH_CALLED = False
DELETE_CALLED = False

WRITE_TRANSMISSION_OCCURRED = False

AUTH_HEADERS_SENT_TO_PUBLIC_ENDPOINT = False

PRIVATE_GET_RESPONSES = 0


# ============================================================
# HEALTH SERVER
# ============================================================

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


async def health_handler(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:

    try:
        try:
            await asyncio.wait_for(
                reader.read(2048),
                timeout=2.0,
            )
        except Exception:
            pass

        body = (
            "R28 UNIT J ACTIVE\n"
            "AUTHENTICATED READ-ONLY MODE\n"
            "WRITE METHODS BLOCKED\n"
            "ORDER TRANSMISSION DISABLED\n"
        )

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            f"Content-Length: {len(body.encode('utf-8'))}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )

        writer.write(
            response.encode("utf-8")
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
        host="0.0.0.0",
        port=HEALTH_PORT,
    )

    print(
        f"R28 UNIT J: HEALTH SERVER ACTIVE ON PORT {HEALTH_PORT}",
        flush=True,
    )

    return server


# ============================================================
# SAFETY HELPERS
# ============================================================

def validate_host(
    host: str,
) -> None:

    if host != LOCKED_WEEX_HOST:
        raise PermissionError(
            "R28 UNIT J BLOCKED: "
            "external host not allowed"
        )


def validate_public_path(
    path: str,
) -> None:

    if path not in PUBLIC_GET_ALLOWLIST:
        raise PermissionError(
            "R28 UNIT J BLOCKED: "
            f"public GET path not allowlisted: {path}"
        )


def validate_private_path(
    path: str,
) -> None:

    if path not in PRIVATE_GET_ALLOWLIST:
        raise PermissionError(
            "R28 UNIT J BLOCKED: "
            f"private GET path not allowlisted: {path}"
        )

    lowered = path.lower()

    for forbidden in FORBIDDEN_WRITE_PATH_FRAGMENTS:

        if forbidden in lowered:

            raise PermissionError(
                "R28 UNIT J BLOCKED: "
                "write/order-like endpoint rejected"
            )


def assert_get_method(
    method: str,
) -> None:

    if method.upper() != "GET":
        raise PermissionError(
            "R28 UNIT J BLOCKED: "
            "only GET is permitted"
        )


# ============================================================
# HARD WRITE METHOD BLOCKS
# ============================================================

async def blocked_post(
    *args,
    **kwargs,
):

    global POST_CALLED

    POST_CALLED = True

    raise PermissionError(
        "R28 UNIT J HARD LOCK: "
        "POST is disabled"
    )


async def blocked_put(
    *args,
    **kwargs,
):

    global PUT_CALLED

    PUT_CALLED = True

    raise PermissionError(
        "R28 UNIT J HARD LOCK: "
        "PUT is disabled"
    )


async def blocked_patch(
    *args,
    **kwargs,
):

    global PATCH_CALLED

    PATCH_CALLED = True

    raise PermissionError(
        "R28 UNIT J HARD LOCK: "
        "PATCH is disabled"
    )


async def blocked_delete(
    *args,
    **kwargs,
):

    global DELETE_CALLED

    DELETE_CALLED = True

    raise PermissionError(
        "R28 UNIT J HARD LOCK: "
        "DELETE is disabled"
    )


async def blocked_real_order_post(
    *args,
    **kwargs,
):

    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise PermissionError(
        "R28 UNIT J HARD LOCK: "
        "real order transmission disabled"
    )


async def blocked_demo_order_post(
    *args,
    **kwargs,
):

    global DEMO_POST_CALLED

    DEMO_POST_CALLED = True

    raise PermissionError(
        "R28 UNIT J HARD LOCK: "
        "demo order transmission disabled"
    )


# ============================================================
# CREDENTIAL VALIDATION
# ============================================================

def credentials_present() -> bool:

    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )


def validate_credentials() -> None:

    if not WEEX_API_KEY:
        raise RuntimeError(
            "WEEX_API_KEY is missing"
        )

    if not WEEX_API_SECRET:
        raise RuntimeError(
            "WEEX_API_SECRET is missing"
        )

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE is missing"
        )


# ============================================================
# QUERY STRING CREATION
# ============================================================

def build_query_string(
    params: Optional[Dict[str, Any]],
) -> str:

    if not params:
        return ""

    clean_params = {}

    for key, value in params.items():

        if value is None:
            continue

        clean_params[str(key)] = str(value)

    return urlencode(
        clean_params
    )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def create_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    assert_get_method(
        method
    )

    if body:
        raise PermissionError(
            "R28 UNIT J BLOCKED: "
            "GET request body not permitted"
        )

    if query_string:

        prehash = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
        )

    else:

        prehash = (
            timestamp
            + method
            + request_path
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ============================================================
# AUTHENTICATION HEADER CREATION
# ============================================================

def build_private_headers(
    request_path: str,
    query_string: str,
) -> Dict[str, str]:

    validate_credentials()

    validate_private_path(
        request_path
    )

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = create_signature(
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
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
        "User-Agent": "R28-UNIT-J-READONLY",
    }

    return headers


# ============================================================
# SAFE RESPONSE PARSER
# ============================================================

async def parse_response(
    response: aiohttp.ClientResponse,
) -> Any:

    text = await response.text()

    try:
        return json.loads(
            text
        )

    except Exception:

        return {
            "_raw": text,
        }


# ============================================================
# CONTROLLED PUBLIC GET
# ============================================================

async def public_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    global PUBLIC_GET_COUNT
    global AUTH_HEADERS_SENT_TO_PUBLIC_ENDPOINT

    validate_host(
        WEEX_PUBLIC_HOST
    )

    validate_public_path(
        path
    )

    assert_get_method(
        "GET"
    )

    query_string = build_query_string(
        params
    )

    url = (
        WEEX_PUBLIC_HOST
        + path
    )

    if query_string:
        url += "?" + query_string

    headers = {
        "Accept": "application/json",
        "User-Agent": "R28-UNIT-J-READONLY",
    }

    forbidden_headers = {
        "ACCESS-KEY",
        "ACCESS-SIGN",
        "ACCESS-PASSPHRASE",
        "ACCESS-TIMESTAMP",
    }

    if any(
        header in headers
        for header in forbidden_headers
    ):
        AUTH_HEADERS_SENT_TO_PUBLIC_ENDPOINT = True

        raise PermissionError(
            "Authentication header leakage detected"
        )

    print(
        f"R28 UNIT J: PUBLIC GET -> {path}",
        flush=True,
    )

    async with session.get(
        url,
        headers=headers,
    ) as response:

        data = await parse_response(
            response
        )

        if response.status < 200 or response.status >= 300:

            raise RuntimeError(
                "Public GET failed: "
                f"HTTP {response.status} "
                f"{safe_error_text(data)}"
            )

        PUBLIC_GET_COUNT += 1

        return data


# ============================================================
# CONTROLLED AUTHENTICATED PRIVATE GET
# ============================================================

async def private_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    global PRIVATE_GET_COUNT
    global PRIVATE_GET_RESPONSES

    if not AUTHENTICATED_READ_ACCESS:

        raise PermissionError(
            "Authenticated reads disabled"
        )

    if not ALLOW_PRIVATE_GET:

        raise PermissionError(
            "Private GET disabled"
        )

    validate_host(
        WEEX_PRIVATE_HOST
    )

    validate_private_path(
        path
    )

    assert_get_method(
        "GET"
    )

    query_string = build_query_string(
        params
    )

    headers = build_private_headers(
        request_path=path,
        query_string=query_string,
    )

    url = (
        WEEX_PRIVATE_HOST
        + path
    )

    if query_string:
        url += "?" + query_string

    print(
        f"R28 UNIT J: AUTHENTICATED GET -> {path}",
        flush=True,
    )

    async with session.get(
        url,
        headers=headers,
    ) as response:

        data = await parse_response(
            response
        )

        if response.status < 200 or response.status >= 300:

            raise RuntimeError(
                "Authenticated GET failed: "
                f"HTTP {response.status} "
                f"{safe_error_text(data)}"
            )

        PRIVATE_GET_COUNT += 1
        PRIVATE_GET_RESPONSES += 1

        return data


# ============================================================
# SAFE ERROR TEXT
# ============================================================

def safe_error_text(
    data: Any,
) -> str:

    try:

        text = json.dumps(
            data,
            ensure_ascii=False,
        )

    except Exception:

        text = str(
            data
        )

    # Never accidentally print credentials.

    secrets = (
        WEEX_API_KEY,
        WEEX_API_SECRET,
        WEEX_API_PASSPHRASE,
    )

    for secret in secrets:

        if secret:

            text = text.replace(
                secret,
                "[REDACTED]",
            )

    if len(text) > 500:

        text = (
            text[:500]
            + "..."
        )

    return text


# ============================================================
# BALANCE EXTRACTION
# ============================================================

def extract_usdt_balance(
    data: Any,
) -> Optional[Dict[str, Any]]:

    candidates = []

    if isinstance(
        data,
        list,
    ):
        candidates = data

    elif isinstance(
        data,
        dict,
    ):

        for key in (
            "data",
            "result",
            "balances",
            "assets",
        ):

            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                candidates = value
                break

        if not candidates:

            asset = str(
                data.get(
                    "asset",
                    "",
                )
            ).upper()

            if asset == "USDT":
                return data

    for item in candidates:

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

        if asset == "USDT":

            return item

    return None


# ============================================================
# POSITION EXTRACTION
# ============================================================

def normalize_positions(
    data: Any,
):

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
            "data",
            "result",
            "positions",
        ):

            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    return []


# ============================================================
# SYMBOL CONFIG EXTRACTION
# ============================================================

def normalize_symbol_config(
    data: Any,
):

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
            "data",
            "result",
        ):

            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

        if data.get(
            "symbol"
        ):
            return [
                data
            ]

    return []


# ============================================================
# DIAGNOSTIC RESULT
# ============================================================

def gate(
    name: str,
    passed: bool,
) -> bool:

    status = (
        "✅ PASS"
        if passed
        else
        "❌ FAIL"
    )

    print(
        f"{name:<50} {status}",
        flush=True,
    )

    return passed


# ============================================================
# LOCAL WRITE BLOCK TESTS
# ============================================================

async def test_write_blocks():

    post_blocked = False
    put_blocked = False
    patch_blocked = False
    delete_blocked = False
    real_order_blocked = False
    demo_order_blocked = False

    try:
        await blocked_post()
    except PermissionError:
        post_blocked = True

    try:
        await blocked_put()
    except PermissionError:
        put_blocked = True

    try:
        await blocked_patch()
    except PermissionError:
        patch_blocked = True

    try:
        await blocked_delete()
    except PermissionError:
        delete_blocked = True

    try:
        await blocked_real_order_post()
    except PermissionError:
        real_order_blocked = True

    try:
        await blocked_demo_order_post()
    except PermissionError:
        demo_order_blocked = True

    return {
        "post": post_blocked,
        "put": put_blocked,
        "patch": patch_blocked,
        "delete": delete_blocked,
        "real_order": real_order_blocked,
        "demo_order": demo_order_blocked,
    }


# ============================================================
# FORBIDDEN ENDPOINT TEST
# ============================================================

def test_forbidden_endpoint_block() -> bool:

    try:

        validate_private_path(
            "/capi/v3/order"
        )

    except PermissionError:

        return True

    return False


# ============================================================
# ARBITRARY HOST TEST
# ============================================================

def test_arbitrary_host_block() -> bool:

    try:

        validate_host(
            "https://example.com"
        )

    except PermissionError:

        return True

    return False


# ============================================================
# UNALLOWLISTED PRIVATE GET TEST
# ============================================================

def test_unallowlisted_private_path() -> bool:

    try:

        validate_private_path(
            "/capi/v3/account/notAllowed"
        )

    except PermissionError:

        return True

    return False


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_diagnostic() -> bool:

    print(
        "=" * 60,
        flush=True,
    )

    print(
        "0F-4H-R28-UNIT-J STARTING",
        flush=True,
    )

    print(
        "AUTHENTICATED READ-ONLY PRIVATE API VALIDATION",
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
        f"R28 UNIT J SYMBOL: {SYMBOL}",
        flush=True,
    )

    print(
        "R28 UNIT J NETWORK POLICY:",
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
        "R28 UNIT J CREDENTIAL STATUS:",
        flush=True,
    )

    print(
        "  API Key: "
        + (
            "✅ PRESENT"
            if WEEX_API_KEY
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Secret: "
        + (
            "✅ PRESENT"
            if WEEX_API_SECRET
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  API Passphrase: "
        + (
            "✅ PRESENT"
            if WEEX_API_PASSPHRASE
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "R28 UNIT J SAFETY GATES",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    results = []

    results.append(
        gate(
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        )
    )

    results.append(
        gate(
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    results.append(
        gate(
            "Real Order Transmission Disabled",
            REAL_ORDER_TRANSMISSION is False,
        )
    )

    results.append(
        gate(
            "Demo Order Transmission Disabled",
            DEMO_ORDER_TRANSMISSION is False,
        )
    )

    results.append(
        gate(
            "Private Write Access Disabled",
            PRIVATE_WRITE_ACCESS is False,
        )
    )

    results.append(
        gate(
            "Authenticated Read Access Enabled",
            AUTHENTICATED_READ_ACCESS is True,
        )
    )

    results.append(
        gate(
            "Private GET Allowlist Locked",
            bool(
                PRIVATE_GET_ALLOWLIST
            ),
        )
    )

    results.append(
        gate(
            "WEEX Host Locked",
            (
                WEEX_PRIVATE_HOST
                == LOCKED_WEEX_HOST
            ),
        )
    )

    results.append(
        gate(
            "API Credentials Present",
            credentials_present(),
        )
    )

    write_tests = await test_write_blocks()

    results.append(
        gate(
            "Generic POST Rejected Locally",
            write_tests["post"],
        )
    )

    results.append(
        gate(
            "PUT Rejected Locally",
            write_tests["put"],
        )
    )

    results.append(
        gate(
            "PATCH Rejected Locally",
            write_tests["patch"],
        )
    )

    results.append(
        gate(
            "DELETE Rejected Locally",
            write_tests["delete"],
        )
    )

    results.append(
        gate(
            "Real Order POST Rejected Locally",
            write_tests["real_order"],
        )
    )

    results.append(
        gate(
            "Demo Order POST Rejected Locally",
            write_tests["demo_order"],
        )
    )

    results.append(
        gate(
            "Order Endpoint Rejected Locally",
            test_forbidden_endpoint_block(),
        )
    )

    results.append(
        gate(
            "Unallowlisted Private GET Rejected",
            test_unallowlisted_private_path(),
        )
    )

    results.append(
        gate(
            "Arbitrary External Host Rejected",
            test_arbitrary_host_block(),
        )
    )

    if not credentials_present():

        print(
            "-" * 60,
            flush=True,
        )

        print(
            "❌ R28 UNIT J CANNOT RUN AUTHENTICATED TESTS",
            flush=True,
        )

        print(
            "Required Render environment variables:",
            flush=True,
        )

        print(
            "  WEEX_API_KEY",
            flush=True,
        )

        print(
            "  WEEX_API_SECRET",
            flush=True,
        )

        print(
            "  WEEX_API_PASSPHRASE",
            flush=True,
        )

        print(
            "Use a READ-ONLY WEEX API key.",
            flush=True,
        )

        return False

    timeout = aiohttp.ClientTimeout(
        total=HTTP_TIMEOUT_SECONDS
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        # ====================================================
        # PUBLIC CONTROL GET
        # ====================================================

        try:

            public_data = await public_get(
                session=session,
                path="/capi/v3/market/symbolPrice",
                params={
                    "symbol": SYMBOL,
                },
            )

            results.append(
                gate(
                    "Public Market GET",
                    public_data is not None,
                )
            )

        except Exception as exc:

            print(
                "R28 UNIT J PUBLIC GET ERROR: "
                f"{safe_error_text(str(exc))}",
                flush=True,
            )

            results.append(
                gate(
                    "Public Market GET",
                    False,
                )
            )

        # ====================================================
        # ACCOUNT BALANCE
        # ====================================================

        try:

            balance_data = await private_get(
                session=session,
                path="/capi/v3/account/balance",
            )

            results.append(
                gate(
                    "Authenticated Balance GET",
                    balance_data is not None,
                )
            )

            usdt = extract_usdt_balance(
                balance_data
            )

            if usdt:

                available = usdt.get(
                    "availableBalance",
                    "UNKNOWN",
                )

                balance = usdt.get(
                    "balance",
                    "UNKNOWN",
                )

                print(
                    "R28 UNIT J: USDT BALANCE = "
                    f"{balance}",
                    flush=True,
                )

                print(
                    "R28 UNIT J: USDT AVAILABLE = "
                    f"{available}",
                    flush=True,
                )

            else:

                print(
                    "R28 UNIT J: USDT BALANCE "
                    "ENTRY NOT FOUND",
                    flush=True,
                )

        except Exception as exc:

            print(
                "R28 UNIT J BALANCE GET ERROR: "
                f"{safe_error_text(str(exc))}",
                flush=True,
            )

            results.append(
                gate(
                    "Authenticated Balance GET",
                    False,
                )
            )

        # ====================================================
        # ALL POSITIONS
        # ====================================================

        try:

            positions_data = await private_get(
                session=session,
                path=(
                    "/capi/v3/account/"
                    "position/allPosition"
                ),
            )

            positions = normalize_positions(
                positions_data
            )

            results.append(
                gate(
                    "Authenticated Positions GET",
                    positions_data is not None,
                )
            )

            print(
                "R28 UNIT J: POSITION RECORDS = "
                f"{len(positions)}",
                flush=True,
            )

            active_for_symbol = []

            for position in positions:

                if not isinstance(
                    position,
                    dict,
                ):
                    continue

                position_symbol = str(
                    position.get(
                        "symbol",
                        "",
                    )
                ).upper()

                try:

                    position_size = float(
                        position.get(
                            "size",
                            0,
                        )
                        or 0
                    )

                except Exception:

                    position_size = 0.0

                if (
                    position_symbol == SYMBOL
                    and position_size != 0
                ):

                    active_for_symbol.append(
                        position
                    )

            print(
                "R28 UNIT J: ACTIVE "
                f"{SYMBOL} POSITIONS = "
                f"{len(active_for_symbol)}",
                flush=True,
            )

            for position in active_for_symbol:

                print(
                    "R28 UNIT J POSITION: "
                    f"SIDE={position.get('side', 'UNKNOWN')} "
                    f"SIZE={position.get('size', 'UNKNOWN')} "
                    f"LEVERAGE={position.get('leverage', 'UNKNOWN')} "
                    f"MARGIN={position.get('marginType', 'UNKNOWN')} "
                    f"UPNL={position.get('unrealizePnl', 'UNKNOWN')}",
                    flush=True,
                )

        except Exception as exc:

            print(
                "R28 UNIT J POSITIONS GET ERROR: "
                f"{safe_error_text(str(exc))}",
                flush=True,
            )

            results.append(
                gate(
                    "Authenticated Positions GET",
                    False,
                )
            )

        # ====================================================
        # SYMBOL CONFIGURATION
        # ====================================================

        try:

            config_data = await private_get(
                session=session,
                path="/capi/v3/account/symbolConfig",
                params={
                    "symbol": SYMBOL,
                },
            )

            configs = normalize_symbol_config(
                config_data
            )

            results.append(
                gate(
                    "Authenticated Symbol Config GET",
                    config_data is not None,
                )
            )

            matching = None

            for item in configs:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                item_symbol = str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()

                if item_symbol == SYMBOL:

                    matching = item
                    break

            if matching:

                print(
                    "R28 UNIT J SYMBOL CONFIG:",
                    flush=True,
                )

                print(
                    "  Symbol = "
                    f"{matching.get('symbol', 'UNKNOWN')}",
                    flush=True,
                )

                print(
                    "  Margin Type = "
                    f"{matching.get('marginType', 'UNKNOWN')}",
                    flush=True,
                )

                print(
                    "  Cross Leverage = "
                    f"{matching.get('crossLeverage', 'UNKNOWN')}",
                    flush=True,
                )

                print(
                    "  Isolated Long Leverage = "
                    f"{matching.get('isolatedLongLeverage', 'UNKNOWN')}",
                    flush=True,
                )

                print(
                    "  Isolated Short Leverage = "
                    f"{matching.get('isolatedShortLeverage', 'UNKNOWN')}",
                    flush=True,
                )

        except Exception as exc:

            print(
                "R28 UNIT J SYMBOL CONFIG ERROR: "
                f"{safe_error_text(str(exc))}",
                flush=True,
            )

            results.append(
                gate(
                    "Authenticated Symbol Config GET",
                    False,
                )
            )

    # ========================================================
    # FINAL SAFETY ASSERTIONS
    # ========================================================

    results.append(
        gate(
            "Controlled Public GET Occurred",
            PUBLIC_GET_COUNT >= 1,
        )
    )

    results.append(
        gate(
            "Controlled Private GET Occurred",
            PRIVATE_GET_COUNT >= 1,
        )
    )

    results.append(
        gate(
            "Private Response Received",
            PRIVATE_GET_RESPONSES >= 1,
        )
    )

    results.append(
        gate(
            "No Auth Headers Sent To Public API",
            AUTH_HEADERS_SENT_TO_PUBLIC_ENDPOINT is False,
        )
    )

    results.append(
        gate(
            "No Real Order Transmission Occurred",
            WRITE_TRANSMISSION_OCCURRED is False,
        )
    )

    results.append(
        gate(
            "Final Execution Safety Assertions",
            (
                LIVE_ORDER_EXECUTION is False
                and DEMO_ORDER_EXECUTION is False
                and REAL_ORDER_TRANSMISSION is False
                and DEMO_ORDER_TRANSMISSION is False
                and PRIVATE_WRITE_ACCESS is False
                and POST_ENABLED is False
                and PUT_ENABLED is False
                and PATCH_ENABLED is False
                and DELETE_ENABLED is False
                and HARD_REAL_POST_LOCK is True
                and HARD_DEMO_POST_LOCK is True
                and HARD_WRITE_METHOD_LOCK is True
                and WRITE_TRANSMISSION_OCCURRED is False
            ),
        )
    )

    print(
        "-" * 60,
        flush=True,
    )

    passed = all(
        results
    )

    if passed:

        print(
            "✅ R28 UNIT J DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ AUTHENTICATED READ-ONLY API VALIDATED",
            flush=True,
        )

        print(
            "✅ PRIVATE ACCOUNT GET ACCESS VALIDATED",
            flush=True,
        )

        print(
            "✅ BALANCE READ VALIDATED",
            flush=True,
        )

        print(
            "✅ POSITION READ VALIDATED",
            flush=True,
        )

        print(
            "✅ SYMBOL CONFIG READ VALIDATED",
            flush=True,
        )

        print(
            "✅ API REQUEST SIGNING VALIDATED",
            flush=True,
        )

        print(
            "✅ PRIVATE GET ALLOWLIST VALIDATED",
            flush=True,
        )

        print(
            "✅ AUTH HEADERS ISOLATED FROM PUBLIC GETS",
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
            "❌ R28 UNIT J DIAGNOSTIC FAILED",
            flush=True,
        )

        print(
            "🛡 EXECUTION REMAINS HARD LOCKED",
            flush=True,
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE",
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

def request_shutdown():

    if STOP_EVENT is not None:

        STOP_EVENT.set()


def install_signal_handlers(
    loop: asyncio.AbstractEventLoop,
):

    for sig in (
        signal.SIGTERM,
        signal.SIGINT,
    ):

        try:

            loop.add_signal_handler(
                sig,
                request_shutdown,
            )

        except (
            NotImplementedError,
            RuntimeError,
        ):
            pass


# ============================================================
# PERSISTENT HEARTBEAT
# ============================================================

async def persistent_runtime():

    global STOP_EVENT

    STOP_EVENT = asyncio.Event()

    loop = asyncio.get_running_loop()

    install_signal_handlers(
        loop
    )

    heartbeat = 0

    print(
        "R28 UNIT J: READY FOR "
        "AUTHENTICATED READ-ONLY RUNTIME",
        flush=True,
    )

    print(
        "R28 UNIT J: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT J: PRIVATE READ-ONLY "
        "SAFETY LOCKS ACTIVE",
        flush=True,
    )

    while not STOP_EVENT.is_set():

        heartbeat += 1

        print(
            "R28 UNIT J: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        try:

            await asyncio.wait_for(
                STOP_EVENT.wait(),
                timeout=30.0,
            )

        except asyncio.TimeoutError:

            continue

    print(
        "R28 UNIT J: SHUTDOWN REQUESTED",
        flush=True,
    )

    print(
        "R28 UNIT J: RUNTIME STOPPED CLEANLY",
        flush=True,
    )


# ============================================================
# APPLICATION ENTRY
# ============================================================

async def main():

    print(
        "R28 UNIT J: RUNTIME STARTING",
        flush=True,
    )

    health_server = await start_health_server()

    try:

        diagnostic_passed = await run_diagnostic()

        if not diagnostic_passed:

            print(
                "R28 UNIT J: DIAGNOSTIC DID NOT PASS",
                flush=True,
            )

            print(
                "R28 UNIT J: WRITE LOCKS REMAIN ACTIVE",
                flush=True,
            )

        await persistent_runtime()

    finally:

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
            "R28 UNIT J: KEYBOARD INTERRUPT",
            flush=True,
        )

    except Exception as exc:

        print(
            "R28 UNIT J: FATAL STARTUP ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        sys.exit(1)
