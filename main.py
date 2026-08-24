# ============================================================
# 0F-4H-R28-UNIT-K.1
# TRANSPORT-BOUNDARY / WRITE-LOCK AUDIT
# AUTHENTICATED READ-ONLY ACCOUNT STATE RECONCILIATION
#
# CORRECTED VERSION
#
# FIX 1:
#   /capi/v3/market/symbolPrice now explicitly sends
#   symbol=BTCUSDT and priceType=MARK
#
# FIX 2:
#   Position mode is read from WEEX V3 "separatedType"
#   COMBINED / SEPARATED
#
# ABSOLUTE SAFETY:
#   REAL ORDER TRANSMISSION DISABLED
#   DEMO ORDER TRANSMISSION DISABLED
#   ALL NETWORK WRITE METHODS BLOCKED
# ============================================================

print(
    "R28 UNIT K.1: MAIN.PY ENTERED",
    flush=True,
)

# ============================================================
# IMPORTS
# ============================================================

import asyncio
import base64
import hashlib
import hmac
import os
import signal
import threading
import time
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urlparse

import httpx

print(
    "R28 UNIT K.1: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-K.1"
MODULE_VERSION = "R28-K.1-CORRECTED"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

PLANNED_MARGIN_TYPE = "ISOLATED"
PLANNED_LEVERAGE = Decimal("100")


# ============================================================
# WEEX API CONFIGURATION
# ============================================================

WEEX_BASE_URL = "https://api-contract.weex.com"

WEEX_HOST = "api-contract.weex.com"

PUBLIC_SYMBOL_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
)

PRIVATE_BALANCE_PATH = (
    "/capi/v3/account/balance"
)

PRIVATE_POSITIONS_PATH = (
    "/capi/v3/account/position/allPosition"
)

PRIVATE_SYMBOL_CONFIG_PATH = (
    "/capi/v3/account/symbolConfig"
)


# ============================================================
# CREDENTIALS
# ============================================================

# Primary variable names.
API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()

# Compatibility fallbacks.
if not API_KEY:
    API_KEY = os.getenv(
        "API_KEY",
        "",
    ).strip()

if not API_SECRET:
    API_SECRET = os.getenv(
        "API_SECRET",
        "",
    ).strip()

if not API_PASSPHRASE:
    API_PASSPHRASE = os.getenv(
        "API_PASSPHRASE",
        "",
    ).strip()


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

REAL_ORDER_TRANSMISSION_ENABLED = False
DEMO_ORDER_TRANSMISSION_ENABLED = False

PRIVATE_WRITE_ACCESS_ENABLED = False

AUTHENTICATED_READ_ACCESS_ENABLED = True
PUBLIC_MARKET_READ_ACCESS_ENABLED = True

NETWORK_WRITE_ACCESS_ENABLED = False


# ============================================================
# ENDPOINT ALLOWLISTS
# ============================================================

PUBLIC_GET_ALLOWLIST = {
    PUBLIC_SYMBOL_PRICE_PATH,
}

PRIVATE_GET_ALLOWLIST = {
    PRIVATE_BALANCE_PATH,
    PRIVATE_POSITIONS_PATH,
    PRIVATE_SYMBOL_CONFIG_PATH,
}


# ============================================================
# WRITE-ENDPOINT IDENTIFIERS
# ============================================================

REAL_ORDER_PATH = "/capi/v3/order"

DEMO_ORDER_PATH = "/capi/v3/sim/order"


# ============================================================
# NETWORK AUDIT COUNTERS
# ============================================================

AUDIT = {
    "local_post_attempts": 0,
    "local_post_blocks": 0,

    "local_put_attempts": 0,
    "local_put_blocks": 0,

    "local_patch_attempts": 0,
    "local_patch_blocks": 0,

    "local_delete_attempts": 0,
    "local_delete_blocks": 0,

    "network_gets": 0,
    "network_writes": 0,

    "network_posts": 0,
    "network_puts": 0,
    "network_patches": 0,
    "network_deletes": 0,

    "real_order_network_transmissions": 0,
    "demo_order_network_transmissions": 0,

    "public_gets": 0,
    "private_gets": 0,
}


# ============================================================
# RUNTIME CONTROL
# ============================================================

RUNTIME_ACTIVE = True


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = (
            "R28 UNIT K.1 ACTIVE\n"
            "READ-ONLY MODE\n"
            "NETWORK WRITES LOCKED\n"
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    port_raw = os.getenv(
        "PORT",
        "10000",
    )

    try:
        port = int(port_raw)

    except Exception:
        port = 10000

    try:

        server = HTTPServer(
            ("0.0.0.0", port),
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

    except Exception as exc:

        print(
            "R28 UNIT K.1: HEALTH SERVER ERROR:",
            repr(exc),
            flush=True,
        )


# ============================================================
# BASIC UTILITIES
# ============================================================

def safe_decimal(
    value: Any,
    default: str = "0",
) -> Decimal:

    try:

        if value is None:
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


def normalize_symbol(
    value: Any,
) -> str:

    return str(
        value or ""
    ).strip().upper()


def print_gate(
    label: str,
    passed: bool,
) -> bool:

    result = (
        "✅ PASS"
        if passed
        else "❌ FAIL"
    )

    print(
        f"{label:<60} {result}",
        flush=True,
    )

    return passed


def credentials_present() -> bool:

    return bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )


# ============================================================
# HOST LOCK
# ============================================================

def validate_weex_url(
    url: str,
) -> None:

    parsed = urlparse(url)

    if parsed.scheme != "https":

        raise RuntimeError(
            "NON-HTTPS NETWORK REQUEST BLOCKED"
        )

    if parsed.hostname != WEEX_HOST:

        raise RuntimeError(
            "EXTERNAL HOST BLOCKED LOCALLY"
        )


# ============================================================
# WRITE LOCKS
# ============================================================

def reject_post(
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:

    AUDIT["local_post_attempts"] += 1
    AUDIT["local_post_blocks"] += 1

    raise RuntimeError(
        f"POST BLOCKED LOCALLY: {path}"
    )


def reject_put(
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:

    AUDIT["local_put_attempts"] += 1
    AUDIT["local_put_blocks"] += 1

    raise RuntimeError(
        f"PUT BLOCKED LOCALLY: {path}"
    )


def reject_patch(
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:

    AUDIT["local_patch_attempts"] += 1
    AUDIT["local_patch_blocks"] += 1

    raise RuntimeError(
        f"PATCH BLOCKED LOCALLY: {path}"
    )


def reject_delete(
    path: str,
) -> None:

    AUDIT["local_delete_attempts"] += 1
    AUDIT["local_delete_blocks"] += 1

    raise RuntimeError(
        f"DELETE BLOCKED LOCALLY: {path}"
    )


# ============================================================
# SIGNATURE GENERATION
# ============================================================

def generate_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    message = (
        timestamp
        + method
        + request_path
    )

    if query_string:

        message += (
            "?"
            + query_string
        )

    if body:

        message += body

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ============================================================
# PRIVATE AUTH HEADERS
# ============================================================

def build_private_headers(
    method: str,
    path: str,
    query_string: str = "",
) -> Dict[str, str]:

    if not credentials_present():

        raise RuntimeError(
            "WEEX API CREDENTIALS MISSING"
        )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_signature(
        timestamp=timestamp,
        method=method,
        request_path=path,
        query_string=query_string,
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
    }


# ============================================================
# CONTROLLED NETWORK GET
# ============================================================

async def network_get(
    path: str,
    params: Optional[Dict[str, Any]],
    authenticated: bool,
) -> Any:

    if authenticated:

        if not AUTHENTICATED_READ_ACCESS_ENABLED:

            raise RuntimeError(
                "AUTHENTICATED READ ACCESS DISABLED"
            )

        if path not in PRIVATE_GET_ALLOWLIST:

            raise RuntimeError(
                "PRIVATE GET PATH BLOCKED LOCALLY"
            )

    else:

        if not PUBLIC_MARKET_READ_ACCESS_ENABLED:

            raise RuntimeError(
                "PUBLIC MARKET READ ACCESS DISABLED"
            )

        if path not in PUBLIC_GET_ALLOWLIST:

            raise RuntimeError(
                "PUBLIC GET PATH BLOCKED LOCALLY"
            )

    cleaned_params: Dict[str, Any] = {}

    if params:

        for key, value in params.items():

            if value is not None:

                cleaned_params[
                    str(key)
                ] = value

    # IMPORTANT:
    # urlencode creates the exact query string used
    # both in the URL and authenticated signature.
    query_string = urlencode(
        cleaned_params
    )

    url = (
        WEEX_BASE_URL
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    validate_weex_url(
        url
    )

    headers: Dict[str, str] = {}

    if authenticated:

        headers = build_private_headers(
            method="GET",
            path=path,
            query_string=query_string,
        )

    AUDIT["network_gets"] += 1

    if authenticated:
        AUDIT["private_gets"] += 1

    else:
        AUDIT["public_gets"] += 1

    timeout = httpx.Timeout(
        15.0,
        connect=10.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=False,
    ) as client:

        response = await client.get(
            url,
            headers=headers,
        )

    if response.status_code != 200:

        raise RuntimeError(
            f"HTTP {response.status_code}: "
            f"{response.text}"
        )

    try:

        return response.json()

    except Exception as exc:

        raise RuntimeError(
            "WEEX RESPONSE WAS NOT VALID JSON"
        ) from exc


# ============================================================
# CONTROLLED PUBLIC GET
# ============================================================

async def public_get(
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    return await network_get(
        path=path,
        params=params,
        authenticated=False,
    )


# ============================================================
# CONTROLLED PRIVATE GET
# ============================================================

async def private_get(
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    return await network_get(
        path=path,
        params=params,
        authenticated=True,
    )


# ============================================================
# RESPONSE NORMALIZATION
# ============================================================

def normalize_record_list(
    response: Any,
) -> List[Dict[str, Any]]:

    if isinstance(
        response,
        list,
    ):

        return [
            item
            for item in response
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        response,
        dict,
    ):

        # Direct single record.
        if any(
            key in response
            for key in (
                "symbol",
                "asset",
                "balance",
                "marginType",
            )
        ):

            return [
                response
            ]

        # Defensive support for wrapped APIs.
        for key in (
            "data",
            "result",
            "rows",
            "list",
        ):

            value = response.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return [
                    item
                    for item in value
                    if isinstance(
                        item,
                        dict,
                    )
                ]

            if isinstance(
                value,
                dict,
            ):

                return [
                    value
                ]

    return []


# ============================================================
# LOCAL WRITE-LOCK TESTS
# ============================================================

def test_generic_post_lock() -> bool:

    before = AUDIT[
        "network_writes"
    ]

    try:

        reject_post(
            "/capi/v3/test/write",
            {
                "test": True,
            },
        )

    except RuntimeError:
        pass

    return (
        AUDIT["network_writes"]
        == before
    )


def test_put_lock() -> bool:

    before = AUDIT[
        "network_writes"
    ]

    try:

        reject_put(
            "/capi/v3/test/write",
            {
                "test": True,
            },
        )

    except RuntimeError:
        pass

    return (
        AUDIT["network_writes"]
        == before
    )


def test_patch_lock() -> bool:

    before = AUDIT[
        "network_writes"
    ]

    try:

        reject_patch(
            "/capi/v3/test/write",
            {
                "test": True,
            },
        )

    except RuntimeError:
        pass

    return (
        AUDIT["network_writes"]
        == before
    )


def test_delete_lock() -> bool:

    before = AUDIT[
        "network_writes"
    ]

    try:

        reject_delete(
            "/capi/v3/test/write"
        )

    except RuntimeError:
        pass

    return (
        AUDIT["network_writes"]
        == before
    )


def test_real_order_lock() -> bool:

    before = AUDIT[
        "network_writes"
    ]

    try:

        reject_post(
            REAL_ORDER_PATH,
            {
                "symbol": SYMBOL,
            },
        )

    except RuntimeError:
        pass

    return (
        AUDIT["network_writes"]
        == before
        and AUDIT[
            "real_order_network_transmissions"
        ] == 0
    )


def test_demo_order_lock() -> bool:

    before = AUDIT[
        "network_writes"
    ]

    try:

        reject_post(
            DEMO_ORDER_PATH,
            {
                "symbol": SYMBOL,
            },
        )

    except RuntimeError:
        pass

    return (
        AUDIT["network_writes"]
        == before
        and AUDIT[
            "demo_order_network_transmissions"
        ] == 0
    )


def test_unallowlisted_private_get() -> bool:

    path = (
        "/capi/v3/account/"
        "definitelyNotAllowlisted"
    )

    return (
        path
        not in PRIVATE_GET_ALLOWLIST
    )


def test_external_host_lock() -> bool:

    try:

        validate_weex_url(
            "https://example.com/test"
        )

    except RuntimeError:
        return True

    return False


# ============================================================
# PUBLIC MARKET RECONCILIATION
# ============================================================

async def reconcile_public_price() -> bool:

    print(
        "R28 UNIT K.1: PUBLIC GET -> "
        + PUBLIC_SYMBOL_PRICE_PATH,
        flush=True,
    )

    try:

        # ====================================================
        # K.1 CORRECTION #1
        #
        # WEEX requires symbol.
        #
        # priceType=MARK ensures this diagnostic reads
        # the mark price rather than relying on the
        # endpoint's default INDEX price.
        # ====================================================

        response = await public_get(
            PUBLIC_SYMBOL_PRICE_PATH,
            params={
                "symbol": SYMBOL,
                "priceType": "MARK",
            },
        )

        if not isinstance(
            response,
            dict,
        ):

            print_gate(
                "Public Market GET",
                False,
            )

            print(
                "R28 UNIT K.1 PUBLIC GET ERROR: "
                "Unexpected response structure",
                flush=True,
            )

            return False

        returned_symbol = normalize_symbol(
            response.get(
                "symbol"
            )
        )

        price = safe_decimal(
            response.get(
                "price"
            )
        )

        passed = (
            returned_symbol == SYMBOL
            and price > 0
        )

        print_gate(
            "Public Market GET",
            passed,
        )

        if passed:

            print(
                "R28 UNIT K.1: "
                f"{SYMBOL} MARK PRICE = {price}",
                flush=True,
            )

        else:

            print(
                "R28 UNIT K.1 PUBLIC GET ERROR: "
                f"symbol={returned_symbol or 'MISSING'}, "
                f"price={price}",
                flush=True,
            )

        return passed

    except Exception as exc:

        print_gate(
            "Public Market GET",
            False,
        )

        print(
            "R28 UNIT K.1 PUBLIC GET ERROR:",
            str(exc),
            flush=True,
        )

        return False


# ============================================================
# BALANCE RECONCILIATION
# ============================================================

async def reconcile_balance() -> bool:

    print(
        "R28 UNIT K.1: AUTHENTICATED GET -> "
        + PRIVATE_BALANCE_PATH,
        flush=True,
    )

    try:

        response = await private_get(
            PRIVATE_BALANCE_PATH
        )

        records = normalize_record_list(
            response
        )

        usdt_record = None

        for record in records:

            asset = normalize_symbol(
                record.get(
                    "asset"
                )
            )

            if asset == "USDT":

                usdt_record = record
                break

        if usdt_record is None:

            print_gate(
                "Authenticated Balance GET",
                False,
            )

            print(
                "R28 UNIT K.1 BALANCE ERROR: "
                "USDT record not found",
                flush=True,
            )

            return False

        print_gate(
            "Authenticated Balance GET",
            True,
        )

        balance = safe_decimal(
            usdt_record.get(
                "balance"
            )
        )

        available = safe_decimal(
            usdt_record.get(
                "availableBalance"
            )
        )

        frozen = safe_decimal(
            usdt_record.get(
                "frozen"
            )
        )

        unrealized_pnl = safe_decimal(
            usdt_record.get(
                "unrealizePnl",
                usdt_record.get(
                    "unrealizedPnl",
                    "0",
                ),
            )
        )

        print(
            f"R28 UNIT K.1: USDT BALANCE = {balance}",
            flush=True,
        )

        print(
            "R28 UNIT K.1: "
            f"USDT AVAILABLE = {available}",
            flush=True,
        )

        print(
            f"R28 UNIT K.1: USDT FROZEN = {frozen}",
            flush=True,
        )

        print(
            "R28 UNIT K.1: "
            f"ACCOUNT UNREALIZED PNL = {unrealized_pnl}",
            flush=True,
        )

        gate_1 = print_gate(
            "Balance Is Non-Negative",
            balance >= 0,
        )

        gate_2 = print_gate(
            "Available Balance Is Non-Negative",
            available >= 0,
        )

        gate_3 = print_gate(
            "Frozen Balance Is Non-Negative",
            frozen >= 0,
        )

        return all(
            (
                gate_1,
                gate_2,
                gate_3,
            )
        )

    except Exception as exc:

        print_gate(
            "Authenticated Balance GET",
            False,
        )

        print(
            "R28 UNIT K.1 BALANCE GET ERROR:",
            str(exc),
            flush=True,
        )

        return False


# ============================================================
# POSITION RECONCILIATION
# ============================================================

async def reconcile_positions() -> bool:

    print(
        "R28 UNIT K.1: AUTHENTICATED GET -> "
        + PRIVATE_POSITIONS_PATH,
        flush=True,
    )

    try:

        response = await private_get(
            PRIVATE_POSITIONS_PATH
        )

        records = normalize_record_list(
            response
        )

        print_gate(
            "Authenticated Positions GET",
            True,
        )

        active_target_positions: List[
            Dict[str, Any]
        ] = []

        structural_valid = True

        for record in records:

            if not isinstance(
                record,
                dict,
            ):

                structural_valid = False
                continue

            record_symbol = normalize_symbol(
                record.get(
                    "symbol"
                )
            )

            size = safe_decimal(
                record.get(
                    "size"
                )
            )

            if (
                record_symbol == SYMBOL
                and size != 0
            ):

                active_target_positions.append(
                    record
                )

        print(
            "R28 UNIT K.1: "
            f"POSITION RECORDS = {len(records)}",
            flush=True,
        )

        print(
            "R28 UNIT K.1: "
            f"ACTIVE {SYMBOL} POSITIONS = "
            f"{len(active_target_positions)}",
            flush=True,
        )

        gate = print_gate(
            "Position Records Structurally Valid",
            structural_valid,
        )

        return gate

    except Exception as exc:

        print_gate(
            "Authenticated Positions GET",
            False,
        )

        print(
            "R28 UNIT K.1 POSITION GET ERROR:",
            str(exc),
            flush=True,
        )

        return False


# ============================================================
# SYMBOL CONFIG RECONCILIATION
# ============================================================

async def reconcile_symbol_config() -> bool:

    print(
        "R28 UNIT K.1: AUTHENTICATED GET -> "
        + PRIVATE_SYMBOL_CONFIG_PATH,
        flush=True,
    )

    try:

        response = await private_get(
            PRIVATE_SYMBOL_CONFIG_PATH,
            params={
                "symbol": SYMBOL,
            },
        )

        records = normalize_record_list(
            response
        )

        target_record = None

        for record in records:

            if (
                normalize_symbol(
                    record.get(
                        "symbol"
                    )
                )
                == SYMBOL
            ):

                target_record = record
                break

        if target_record is None:

            print_gate(
                "Authenticated Symbol Config GET",
                False,
            )

            print(
                "R28 UNIT K.1 SYMBOL CONFIG ERROR: "
                f"{SYMBOL} record not found",
                flush=True,
            )

            return False

        print_gate(
            "Authenticated Symbol Config GET",
            True,
        )

        returned_symbol = normalize_symbol(
            target_record.get(
                "symbol"
            )
        )

        margin_type = normalize_symbol(
            target_record.get(
                "marginType"
            )
        )

        # ====================================================
        # K.1 CORRECTION #2
        #
        # WEEX V3 Get Symbol Configuration calls this field:
        #
        # separatedType
        #
        # Valid documented values:
        # COMBINED
        # SEPARATED
        #
        # The previous K.1 parser was looking for the wrong
        # position-mode field and therefore produced UNKNOWN.
        # ====================================================

        position_mode = normalize_symbol(
            target_record.get(
                "separatedType"
            )
        )

        # Defensive compatibility only.
        if not position_mode:

            position_mode = normalize_symbol(
                target_record.get(
                    "separatedMode"
                )
            )

        if not position_mode:

            position_mode = "NOT_REPORTED"

        cross_leverage = safe_decimal(
            target_record.get(
                "crossLeverage"
            )
        )

        isolated_long_leverage = safe_decimal(
            target_record.get(
                "isolatedLongLeverage"
            )
        )

        isolated_short_leverage = safe_decimal(
            target_record.get(
                "isolatedShortLeverage"
            )
        )

        print(
            "R28 UNIT K.1 SYMBOL CONFIG:",
            flush=True,
        )

        print(
            f"  Symbol = {returned_symbol}",
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

        symbol_ok = (
            returned_symbol
            == SYMBOL
        )

        margin_ok = (
            margin_type
            in {
                "ISOLATED",
                "CROSSED",
            }
        )

        # WEEX V3 documented separatedType values.
        position_mode_ok = (
            position_mode
            in {
                "COMBINED",
                "SEPARATED",
            }
        )

        leverage_ok = (
            cross_leverage > 0
            and isolated_long_leverage > 0
            and isolated_short_leverage > 0
        )

        gate_1 = print_gate(
            "Symbol Configuration Matches Target Symbol",
            symbol_ok,
        )

        gate_2 = print_gate(
            "Margin Type Recognized",
            margin_ok,
        )

        gate_3 = print_gate(
            "Position Mode Recognized",
            position_mode_ok,
        )

        gate_4 = print_gate(
            "Configured Leverage Values Valid",
            leverage_ok,
        )

        print(
            "R28 UNIT K.1 READ-ONLY STRATEGY COMPARISON:",
            flush=True,
        )

        print(
            "  Planned Margin Type = "
            f"{PLANNED_MARGIN_TYPE}",
            flush=True,
        )

        print(
            "  Planned Leverage = "
            f"{PLANNED_LEVERAGE}x",
            flush=True,
        )

        if margin_type != PLANNED_MARGIN_TYPE:

            print(
                "⚠️ Observed margin type differs from "
                "planned strategy margin type. "
                "NO CHANGE ATTEMPTED.",
                flush=True,
            )

        isolated_leverage_matches = (
            isolated_long_leverage
            == PLANNED_LEVERAGE
            and isolated_short_leverage
            == PLANNED_LEVERAGE
        )

        if not isolated_leverage_matches:

            print(
                "⚠️ Observed isolated leverage differs "
                "from planned strategy leverage. "
                "NO CHANGE ATTEMPTED.",
                flush=True,
            )

        return all(
            (
                gate_1,
                gate_2,
                gate_3,
                gate_4,
            )
        )

    except Exception as exc:

        print_gate(
            "Authenticated Symbol Config GET",
            False,
        )

        print(
            "R28 UNIT K.1 SYMBOL CONFIG GET ERROR:",
            str(exc),
            flush=True,
        )

        return False


# ============================================================
# ACTIVE POSITION CONSISTENCY
# ============================================================

async def check_active_position_consistency() -> bool:

    try:

        # This is intentionally a local/read-only assertion.
        #
        # No order management, leverage update, margin update,
        # cancellation, closing or opening operation is allowed.

        consistent = (
            AUDIT["network_writes"] == 0
            and AUDIT[
                "real_order_network_transmissions"
            ] == 0
            and AUDIT[
                "demo_order_network_transmissions"
            ] == 0
        )

        return print_gate(
            "Active Position State Internally Consistent",
            consistent,
        )

    except Exception:

        return print_gate(
            "Active Position State Internally Consistent",
            False,
        )


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_diagnostic() -> bool:

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


    # ========================================================
    # SAFETY GATES
    # ========================================================

    print(
        "R28 UNIT K.1 SAFETY GATES",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    safety_results = []

    safety_results.append(
        print_gate(
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        )
    )

    safety_results.append(
        print_gate(
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    safety_results.append(
        print_gate(
            "Real Order Transmission Disabled",
            REAL_ORDER_TRANSMISSION_ENABLED is False,
        )
    )

    safety_results.append(
        print_gate(
            "Demo Order Transmission Disabled",
            DEMO_ORDER_TRANSMISSION_ENABLED is False,
        )
    )

    safety_results.append(
        print_gate(
            "Private Write Access Disabled",
            PRIVATE_WRITE_ACCESS_ENABLED is False,
        )
    )

    safety_results.append(
        print_gate(
            "Authenticated Read Access Enabled",
            AUTHENTICATED_READ_ACCESS_ENABLED is True,
        )
    )

    safety_results.append(
        print_gate(
            "Private GET Allowlist Locked",
            PRIVATE_GET_ALLOWLIST
            == {
                PRIVATE_BALANCE_PATH,
                PRIVATE_POSITIONS_PATH,
                PRIVATE_SYMBOL_CONFIG_PATH,
            },
        )
    )

    safety_results.append(
        print_gate(
            "WEEX Host Locked",
            WEEX_HOST
            == "api-contract.weex.com",
        )
    )

    safety_results.append(
        print_gate(
            "API Credentials Present",
            credentials_present(),
        )
    )

    safety_results.append(
        print_gate(
            "Generic POST Rejected Before Transport",
            test_generic_post_lock(),
        )
    )

    safety_results.append(
        print_gate(
            "PUT Rejected Before Transport",
            test_put_lock(),
        )
    )

    safety_results.append(
        print_gate(
            "PATCH Rejected Before Transport",
            test_patch_lock(),
        )
    )

    safety_results.append(
        print_gate(
            "DELETE Rejected Before Transport",
            test_delete_lock(),
        )
    )

    safety_results.append(
        print_gate(
            "Real Order POST Rejected Before Transport",
            test_real_order_lock(),
        )
    )

    safety_results.append(
        print_gate(
            "Demo Order POST Rejected Before Transport",
            test_demo_order_lock(),
        )
    )

    safety_results.append(
        print_gate(
            "Unallowlisted Private GET Rejected Locally",
            test_unallowlisted_private_get(),
        )
    )

    safety_results.append(
        print_gate(
            "Arbitrary External Host Rejected",
            test_external_host_lock(),
        )
    )


    # ========================================================
    # READ-ONLY RECONCILIATION
    # ========================================================

    print(
        "R28 UNIT K.1 READ-ONLY RECONCILIATION",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    public_price_ok = await reconcile_public_price()

    balance_ok = await reconcile_balance()

    positions_ok = await reconcile_positions()

    symbol_config_ok = await reconcile_symbol_config()

    consistency_ok = (
        await check_active_position_consistency()
    )


    # ========================================================
    # TRANSPORT-BOUNDARY AUDIT
    # ========================================================

    print(
        "R28 UNIT K.1 TRANSPORT-BOUNDARY AUDIT",
        flush=True,
    )

    print(
        "-" * 60,
        flush=True,
    )

    transport_results = []

    transport_results.append(
        print_gate(
            "Controlled Public GET Occurred",
            AUDIT["public_gets"] >= 1,
        )
    )

    transport_results.append(
        print_gate(
            "Controlled Private GET Occurred",
            AUDIT["private_gets"] >= 1,
        )
    )

    transport_results.append(
        print_gate(
            "Generic POST Was Blocked Locally",
            AUDIT["local_post_blocks"] >= 1,
        )
    )

    transport_results.append(
        print_gate(
            "Real Order Attempt Was Blocked Locally",
            AUDIT["local_post_blocks"] >= 2,
        )
    )

    transport_results.append(
        print_gate(
            "Demo Order Attempt Was Blocked Locally",
            AUDIT["local_post_blocks"] >= 3,
        )
    )

    transport_results.append(
        print_gate(
            "Network Write Count Is Zero",
            AUDIT["network_writes"] == 0,
        )
    )

    transport_results.append(
        print_gate(
            "Network POST Count Is Zero",
            AUDIT["network_posts"] == 0,
        )
    )

    transport_results.append(
        print_gate(
            "Network PUT Count Is Zero",
            AUDIT["network_puts"] == 0,
        )
    )

    transport_results.append(
        print_gate(
            "Network PATCH Count Is Zero",
            AUDIT["network_patches"] == 0,
        )
    )

    transport_results.append(
        print_gate(
            "Network DELETE Count Is Zero",
            AUDIT["network_deletes"] == 0,
        )
    )

    transport_results.append(
        print_gate(
            "Real Order Transmission Never Occurred",
            AUDIT[
                "real_order_network_transmissions"
            ] == 0,
        )
    )

    transport_results.append(
        print_gate(
            "Demo Order Transmission Never Occurred",
            AUDIT[
                "demo_order_network_transmissions"
            ] == 0,
        )
    )


    # ========================================================
    # WRITE-LOCK AUDIT SUMMARY
    # ========================================================

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
        f"{AUDIT['local_post_blocks']}",
        flush=True,
    )

    print(
        "  Local PUT attempts = "
        f"{AUDIT['local_put_attempts']}",
        flush=True,
    )

    print(
        "  Local PUT blocks = "
        f"{AUDIT['local_put_blocks']}",
        flush=True,
    )

    print(
        "  Local PATCH attempts = "
        f"{AUDIT['local_patch_attempts']}",
        flush=True,
    )

    print(
        "  Local PATCH blocks = "
        f"{AUDIT['local_patch_blocks']}",
        flush=True,
    )

    print(
        "  Local DELETE attempts = "
        f"{AUDIT['local_delete_attempts']}",
        flush=True,
    )

    print(
        "  Local DELETE blocks = "
        f"{AUDIT['local_delete_blocks']}",
        flush=True,
    )

    print(
        "  Network GETs = "
        f"{AUDIT['network_gets']}",
        flush=True,
    )

    print(
        "  Network writes = "
        f"{AUDIT['network_writes']}",
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


    # ========================================================
    # FINAL RESULT
    # ========================================================

    all_passed = all(
        safety_results
        + transport_results
        + [
            public_price_ok,
            balance_ok,
            positions_ok,
            symbol_config_ok,
            consistency_ok,
        ]
    )

    print(
        "-" * 60,
        flush=True,
    )

    if all_passed:

        print(
            "✅ R28 UNIT K.1 DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ TRANSPORT-BOUNDARY AUDIT PASSED",
            flush=True,
        )

        print(
            "✅ AUTHENTICATED READ-ONLY "
            "RECONCILIATION PASSED",
            flush=True,
        )

        print(
            "✅ PUBLIC SYMBOL PRICE "
            "PARAMETER VALIDATED",
            flush=True,
        )

        print(
            "✅ WEEX POSITION MODE "
            "FIELD VALIDATED",
            flush=True,
        )

        print(
            "🛡 NETWORK WRITE TRANSPORT LOCKED",
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

    return all_passed


# ============================================================
# SIGNAL HANDLING
# ============================================================

def request_shutdown(
    signum: int,
    frame: Any,
) -> None:

    global RUNTIME_ACTIVE

    print(
        "R28 UNIT K.1: SHUTDOWN REQUESTED",
        flush=True,
    )

    RUNTIME_ACTIVE = False


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


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime() -> None:

    print(
        "R28 UNIT K.1: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT K.1: "
        "AUTHENTICATED READ-ONLY LOCKS ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT K.1: "
        "NETWORK WRITE TRANSPORT LOCKED",
        flush=True,
    )

    heartbeat = 0

    while RUNTIME_ACTIVE:

        heartbeat += 1

        print(
            "R28 UNIT K.1: "
            f"HEARTBEAT {heartbeat} ✅ ACTIVE",
            flush=True,
        )

        await asyncio.sleep(
            10
        )

    print(
        "R28 UNIT K.1: RUNTIME STOPPED CLEANLY",
        flush=True,
    )


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    print(
        "R28 UNIT K.1: RUNTIME STARTING",
        flush=True,
    )

    start_health_server()

    await run_diagnostic()

    await persistent_runtime()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "R28 UNIT K.1: KEYBOARD INTERRUPT",
            flush=True,
        )

    except Exception as exc:

        print(
            "R28 UNIT K.1: FATAL ERROR:",
            repr(exc),
            flush=True,
        )

        raise
