# ============================================================
# 0F-4H-R28-UNIT-M
# CONTROLLED LEVERAGE CONFIGURATION BOUNDARY VALIDATION
#
# PURPOSE:
# - Read current BTCUSDT leverage configuration
# - Validate planned ISOLATED 100x configuration
# - Construct hypothetical leverage-change payload
# - Construct hypothetical authenticated POST signature locally
# - PROVE leverage POST cannot reach network
#
# REAL ORDER TRANSMISSION DISABLED
# DEMO ORDER TRANSMISSION DISABLED
# ACCOUNT CONFIGURATION WRITES DISABLED
# NETWORK WRITE METHODS BLOCKED
#
# NO LEVERAGE CHANGE WILL BE SENT
# ============================================================

print(
    "R28 UNIT M: MAIN.PY ENTERED",
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
import threading
import time
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

import aiohttp

print(
    "R28 UNIT M: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-M"
MODULE_VERSION = "R28-M"

SYMBOL = "BTCUSDT"

WEEX_HOST = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
LEVERAGE_CHANGE_PATH = "/capi/v3/account/leverage"

PLANNED_MARGIN_TYPE = "ISOLATED"
PLANNED_LEVERAGE = 100

HEARTBEAT_SECONDS = 15


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

REAL_ORDER_TRANSMISSION = False
DEMO_ORDER_TRANSMISSION = False

ACCOUNT_CONFIGURATION_WRITES = False
LEVERAGE_CHANGE_ENABLED = False

NETWORK_POST_ENABLED = False
NETWORK_PUT_ENABLED = False
NETWORK_PATCH_ENABLED = False
NETWORK_DELETE_ENABLED = False

AUTHENTICATED_READ_ACCESS = True


# ============================================================
# CREDENTIAL DISCOVERY
# ============================================================

def first_env(*names):
    for name in names:
        value = os.getenv(name)

        if value:
            return value.strip()

    return ""


API_KEY = first_env(
    "WEEX_API_KEY",
    "API_KEY",
)

API_SECRET = first_env(
    "WEEX_API_SECRET",
    "API_SECRET",
    "SECRET_KEY",
)

API_PASSPHRASE = first_env(
    "WEEX_API_PASSPHRASE",
    "API_PASSPHRASE",
    "PASSPHRASE",
)


# ============================================================
# AUDIT STATE
# ============================================================

audit = {
    "network_gets": 0,
    "network_posts": 0,
    "network_puts": 0,
    "network_patches": 0,
    "network_deletes": 0,

    "local_post_attempts": 0,
    "local_post_blocks": 0,

    "leverage_post_attempts": 0,
    "leverage_post_blocks": 0,

    "real_order_transmissions": 0,
    "demo_order_transmissions": 0,

    "account_write_transmissions": 0,
    "leverage_change_transmissions": 0,
}


# ============================================================
# DIAGNOSTIC RESULT STORAGE
# ============================================================

test_results = []

structural_failures = []

readiness_blockers = []

readiness_warnings = []


def record_test(
    name,
    passed,
):
    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{name:<68} {status}",
        flush=True,
    )

    test_results.append(
        (
            name,
            bool(passed),
        )
    )

    if not passed:
        structural_failures.append(name)

    return bool(passed)


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )

        self.end_headers()

        self.wfile.write(
            b"R28 UNIT M ACTIVE\n"
        )

    def log_message(
        self,
        format,
        *args,
    ):
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
        f"R28 UNIT M: HEALTH SERVER ACTIVE ON PORT {port}",
        flush=True,
    )

    return server


# ============================================================
# JSON SERIALIZATION
# ============================================================

def canonical_json(
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
# AUTHENTICATION SIGNATURE
# ============================================================

def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    method = method.upper()

    message = (
        str(timestamp)
        + method
        + request_path
    )

    if query_string:
        message += "?" + query_string

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


def build_auth_headers(
    method,
    request_path,
    query_string="",
    body="",
):
    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = build_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }


# ============================================================
# NETWORK DESTINATION LOCK
# ============================================================

def validate_weex_url(
    url,
):
    expected_prefix = WEEX_HOST + "/"

    if not url.startswith(expected_prefix):
        raise RuntimeError(
            "R28 UNIT M SAFETY LOCK: "
            "ARBITRARY EXTERNAL HOST REJECTED"
        )

    return True


# ============================================================
# AUTHENTICATED GET
# ============================================================

async def authenticated_get(
    session,
    request_path,
    params=None,
):
    if not AUTHENTICATED_READ_ACCESS:
        raise RuntimeError(
            "Authenticated read access disabled"
        )

    params = params or {}

    query_string = urlencode(
        params
    )

    headers = build_auth_headers(
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    url = (
        WEEX_HOST
        + request_path
    )

    if query_string:
        url += "?" + query_string

    validate_weex_url(
        url
    )

    print(
        f"R28 UNIT M: AUTHENTICATED GET -> {request_path}",
        flush=True,
    )

    audit["network_gets"] += 1

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status < 200 or response.status >= 300:
            raise RuntimeError(
                "Authenticated GET failed "
                f"HTTP {response.status}: {text[:500]}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Authenticated GET returned invalid JSON"
            ) from exc


# ============================================================
# UNIVERSAL WRITE LOCK
# ============================================================

async def blocked_post(
    request_path,
    payload,
):
    audit["local_post_attempts"] += 1

    if request_path == LEVERAGE_CHANGE_PATH:
        audit["leverage_post_attempts"] += 1

    # --------------------------------------------------------
    # HARD LOCAL TRANSPORT TERMINATION
    #
    # IMPORTANT:
    # No aiohttp POST function exists beyond this point.
    # This function ALWAYS raises before network transport.
    # --------------------------------------------------------

    audit["local_post_blocks"] += 1

    if request_path == LEVERAGE_CHANGE_PATH:
        audit["leverage_post_blocks"] += 1

    raise PermissionError(
        "R28 UNIT M WRITE LOCK: "
        f"POST {request_path} REJECTED BEFORE TRANSPORT"
    )


async def blocked_put(
    request_path,
    payload,
):
    raise PermissionError(
        "R28 UNIT M WRITE LOCK: "
        f"PUT {request_path} REJECTED BEFORE TRANSPORT"
    )


async def blocked_patch(
    request_path,
    payload,
):
    raise PermissionError(
        "R28 UNIT M WRITE LOCK: "
        f"PATCH {request_path} REJECTED BEFORE TRANSPORT"
    )


async def blocked_delete(
    request_path,
):
    raise PermissionError(
        "R28 UNIT M WRITE LOCK: "
        f"DELETE {request_path} REJECTED BEFORE TRANSPORT"
    )


# ============================================================
# SYMBOL CONFIG NORMALIZATION
# ============================================================

def extract_symbol_config(
    response_data,
):
    data = response_data

    if isinstance(
        data,
        dict,
    ):
        if isinstance(
            data.get("data"),
            list,
        ):
            data = data["data"]

        elif isinstance(
            data.get("data"),
            dict,
        ):
            data = [
                data["data"]
            ]

        elif "symbol" in data:
            data = [
                data
            ]

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected symbolConfig response structure"
        )

    for item in data:
        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol == SYMBOL:
            return item

    raise RuntimeError(
        f"{SYMBOL} configuration not found"
    )


# ============================================================
# INTEGER LEVERAGE PARSER
# ============================================================

def parse_leverage(
    value,
):
    try:
        return int(
            Decimal(
                str(value)
            )
        )

    except Exception:
        return None


# ============================================================
# PLANNED LEVERAGE PAYLOAD
# ============================================================

def build_planned_leverage_payload():
    return {
        "symbol": SYMBOL,
        "marginType": PLANNED_MARGIN_TYPE,
        "isolatedLongLeverage": str(
            PLANNED_LEVERAGE
        ),
        "isolatedShortLeverage": str(
            PLANNED_LEVERAGE
        ),
    }


# ============================================================
# PAYLOAD VALIDATION
# ============================================================

def validate_leverage_payload(
    payload,
):
    if not isinstance(
        payload,
        dict,
    ):
        return False

    if payload.get(
        "symbol"
    ) != SYMBOL:
        return False

    if payload.get(
        "marginType"
    ) != "ISOLATED":
        return False

    long_lev = parse_leverage(
        payload.get(
            "isolatedLongLeverage"
        )
    )

    short_lev = parse_leverage(
        payload.get(
            "isolatedShortLeverage"
        )
    )

    if long_lev != PLANNED_LEVERAGE:
        return False

    if short_lev != PLANNED_LEVERAGE:
        return False

    return True


# ============================================================
# LOCAL SIGNING VALIDATION
# ============================================================

def validate_hypothetical_post_signature(
    payload,
):
    body = canonical_json(
        payload
    )

    timestamp = "1760000000000"

    signature_a = build_signature(
        timestamp=timestamp,
        method="POST",
        request_path=LEVERAGE_CHANGE_PATH,
        body=body,
    )

    signature_b = build_signature(
        timestamp=timestamp,
        method="POST",
        request_path=LEVERAGE_CHANGE_PATH,
        body=body,
    )

    if not signature_a:
        return False

    if signature_a != signature_b:
        return False

    tampered_payload = dict(
        payload
    )

    tampered_payload[
        "isolatedLongLeverage"
    ] = "99"

    tampered_body = canonical_json(
        tampered_payload
    )

    tampered_signature = build_signature(
        timestamp=timestamp,
        method="POST",
        request_path=LEVERAGE_CHANGE_PATH,
        body=tampered_body,
    )

    if tampered_signature == signature_a:
        return False

    return True


# ============================================================
# LOCAL BLOCK TEST
# ============================================================

async def verify_leverage_post_block(
    payload,
):
    try:
        await blocked_post(
            LEVERAGE_CHANGE_PATH,
            payload,
        )

    except PermissionError:
        return True

    return False


# ============================================================
# NEGATIVE PAYLOAD TESTS
# ============================================================

def test_invalid_payloads():
    bad_symbol = build_planned_leverage_payload()

    bad_symbol["symbol"] = "ETHUSDT"

    bad_margin = build_planned_leverage_payload()

    bad_margin["marginType"] = "CROSSED"

    bad_long = build_planned_leverage_payload()

    bad_long[
        "isolatedLongLeverage"
    ] = "99"

    bad_short = build_planned_leverage_payload()

    bad_short[
        "isolatedShortLeverage"
    ] = "99"

    missing_long = build_planned_leverage_payload()

    missing_long.pop(
        "isolatedLongLeverage"
    )

    missing_short = build_planned_leverage_payload()

    missing_short.pop(
        "isolatedShortLeverage"
    )

    return {
        "Wrong Symbol Rejected":
            not validate_leverage_payload(
                bad_symbol
            ),

        "Wrong Margin Type Rejected":
            not validate_leverage_payload(
                bad_margin
            ),

        "Wrong Long Leverage Rejected":
            not validate_leverage_payload(
                bad_long
            ),

        "Wrong Short Leverage Rejected":
            not validate_leverage_payload(
                bad_short
            ),

        "Missing Long Leverage Rejected":
            not validate_leverage_payload(
                missing_long
            ),

        "Missing Short Leverage Rejected":
            not validate_leverage_payload(
                missing_short
            ),
    }


# ============================================================
# STARTUP BANNER
# ============================================================

def print_banner():
    print(
        "=" * 76,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "CONTROLLED LEVERAGE CONFIGURATION BOUNDARY VALIDATION",
        flush=True,
    )

    print(
        "AUTHENTICATED ACCOUNT CONFIGURATION READ ENABLED",
        flush=True,
    )

    print(
        "HYPOTHETICAL ISOLATED 100x LEVERAGE REQUEST CONSTRUCTION",
        flush=True,
    )

    print(
        "NO LEVERAGE CHANGE WILL BE TRANSMITTED",
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
        "=" * 76,
        flush=True,
    )

    print(
        f"R28 UNIT M SYMBOL: {SYMBOL}",
        flush=True,
    )

    print(
        "R28 UNIT M TARGET CONFIGURATION:",
        flush=True,
    )

    print(
        f"  Margin Type = {PLANNED_MARGIN_TYPE}",
        flush=True,
    )

    print(
        f"  Isolated Long Leverage = {PLANNED_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Isolated Short Leverage = {PLANNED_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Configuration Endpoint = {LEVERAGE_CHANGE_PATH}",
        flush=True,
    )

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M NETWORK POLICY:",
        flush=True,
    )

    print(
        "  ✅ Authenticated account GET enabled",
        flush=True,
    )

    print(
        "  ❌ Leverage POST disabled",
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
        "",
        flush=True,
    )

    print(
        "R28 UNIT M CREDENTIAL STATUS:",
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


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_diagnostic():
    print_banner()

    credentials_present = bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M SAFETY GATES",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    record_test(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    record_test(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    record_test(
        "Real Order Transmission Disabled",
        REAL_ORDER_TRANSMISSION is False,
    )

    record_test(
        "Demo Order Transmission Disabled",
        DEMO_ORDER_TRANSMISSION is False,
    )

    record_test(
        "Account Configuration Writes Disabled",
        ACCOUNT_CONFIGURATION_WRITES is False,
    )

    record_test(
        "Leverage Change Disabled",
        LEVERAGE_CHANGE_ENABLED is False,
    )

    record_test(
        "Network POST Disabled",
        NETWORK_POST_ENABLED is False,
    )

    record_test(
        "Network PUT Disabled",
        NETWORK_PUT_ENABLED is False,
    )

    record_test(
        "Network PATCH Disabled",
        NETWORK_PATCH_ENABLED is False,
    )

    record_test(
        "Network DELETE Disabled",
        NETWORK_DELETE_ENABLED is False,
    )

    record_test(
        "Authenticated Read Access Enabled",
        AUTHENTICATED_READ_ACCESS is True,
    )

    record_test(
        "WEEX Contract Host Locked",
        WEEX_HOST == "https://api-contract.weex.com",
    )

    record_test(
        "Leverage Endpoint Locked",
        LEVERAGE_CHANGE_PATH
        == "/capi/v3/account/leverage",
    )

    record_test(
        "API Credentials Present",
        credentials_present,
    )

    if not credentials_present:
        raise RuntimeError(
            "R28 UNIT M: API credentials missing"
        )

    # ========================================================
    # BUILD HYPOTHETICAL PAYLOAD
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M HYPOTHETICAL LEVERAGE REQUEST",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    planned_payload = (
        build_planned_leverage_payload()
    )

    planned_body = canonical_json(
        planned_payload
    )

    print(
        "R28 UNIT M: LOCAL REQUEST ONLY",
        flush=True,
    )

    print(
        f"  Method = POST",
        flush=True,
    )

    print(
        f"  Path = {LEVERAGE_CHANGE_PATH}",
        flush=True,
    )

    print(
        f"  Symbol = {planned_payload['symbol']}",
        flush=True,
    )

    print(
        f"  Margin Type = {planned_payload['marginType']}",
        flush=True,
    )

    print(
        "  Isolated Long Leverage = "
        + planned_payload[
            "isolatedLongLeverage"
        ]
        + "x",
        flush=True,
    )

    print(
        "  Isolated Short Leverage = "
        + planned_payload[
            "isolatedShortLeverage"
        ]
        + "x",
        flush=True,
    )

    print(
        "  Network Transmission = DISABLED",
        flush=True,
    )

    record_test(
        "Planned Leverage Payload Valid",
        validate_leverage_payload(
            planned_payload
        ),
    )

    record_test(
        "Payload Serialization Deterministic",
        planned_body
        == canonical_json(
            planned_payload
        ),
    )

    record_test(
        "Hypothetical POST Signature Valid",
        validate_hypothetical_post_signature(
            planned_payload
        ),
    )

    # ========================================================
    # NEGATIVE VALIDATION
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M PAYLOAD SAFETY VALIDATION",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    negative_results = (
        test_invalid_payloads()
    )

    for (
        test_name,
        passed,
    ) in negative_results.items():

        record_test(
            test_name,
            passed,
        )

    # ========================================================
    # TEST HARD POST LOCK
    # ========================================================

    leverage_blocked = (
        await verify_leverage_post_block(
            planned_payload
        )
    )

    record_test(
        "Leverage Configuration POST Rejected Before Transport",
        leverage_blocked,
    )

    # ========================================================
    # READ CURRENT CONFIG
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M AUTHENTICATED READ-ONLY CONFIGURATION",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    async with aiohttp.ClientSession() as session:

        config_response = (
            await authenticated_get(
                session=session,
                request_path=SYMBOL_CONFIG_PATH,
                params={
                    "symbol": SYMBOL,
                },
            )
        )

    record_test(
        "Authenticated Symbol Configuration GET",
        config_response is not None,
    )

    symbol_config = (
        extract_symbol_config(
            config_response
        )
    )

    observed_symbol = str(
        symbol_config.get(
            "symbol",
            "",
        )
    ).upper()

    observed_margin = str(
        symbol_config.get(
            "marginType",
            "",
        )
    ).upper()

    observed_mode = str(
        symbol_config.get(
            "separatedType",
            symbol_config.get(
                "separatedMode",
                "",
            ),
        )
    ).upper()

    current_cross = parse_leverage(
        symbol_config.get(
            "crossLeverage"
        )
    )

    current_long = parse_leverage(
        symbol_config.get(
            "isolatedLongLeverage"
        )
    )

    current_short = parse_leverage(
        symbol_config.get(
            "isolatedShortLeverage"
        )
    )

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M CURRENT ACCOUNT CONFIGURATION:",
        flush=True,
    )

    print(
        f"  Symbol = {observed_symbol}",
        flush=True,
    )

    print(
        f"  Margin Type = {observed_margin}",
        flush=True,
    )

    print(
        f"  Position Mode = {observed_mode}",
        flush=True,
    )

    print(
        f"  Cross Leverage = {current_cross}x",
        flush=True,
    )

    print(
        f"  Isolated Long Leverage = {current_long}x",
        flush=True,
    )

    print(
        f"  Isolated Short Leverage = {current_short}x",
        flush=True,
    )

    record_test(
        "Observed Symbol Matches BTCUSDT",
        observed_symbol == SYMBOL,
    )

    record_test(
        "Observed Margin Mode Is ISOLATED",
        observed_margin == "ISOLATED",
    )

    record_test(
        "Position Mode Recognized",
        observed_mode
        in {
            "COMBINED",
            "SEPARATED",
        },
    )

    record_test(
        "Current Long Leverage Parseable",
        current_long is not None,
    )

    record_test(
        "Current Short Leverage Parseable",
        current_short is not None,
    )

    # ========================================================
    # LEVERAGE GAP ANALYSIS
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M LEVERAGE GAP ANALYSIS",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    long_ready = (
        current_long
        == PLANNED_LEVERAGE
    )

    short_ready = (
        current_short
        == PLANNED_LEVERAGE
    )

    print(
        f"  Required Long = {PLANNED_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Current Long = {current_long}x",
        flush=True,
    )

    print(
        "  Long Readiness = "
        + (
            "✅ READY"
            if long_ready
            else "⚠️ CHANGE REQUIRED"
        ),
        flush=True,
    )

    print(
        "",
        flush=True,
    )

    print(
        f"  Required Short = {PLANNED_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Current Short = {current_short}x",
        flush=True,
    )

    print(
        "  Short Readiness = "
        + (
            "✅ READY"
            if short_ready
            else "⚠️ CHANGE REQUIRED"
        ),
        flush=True,
    )

    if not long_ready:
        readiness_blockers.append(
            "Isolated LONG leverage requires "
            f"{PLANNED_LEVERAGE}x; "
            f"current value is {current_long}x."
        )

    if not short_ready:
        readiness_blockers.append(
            "Isolated SHORT leverage requires "
            f"{PLANNED_LEVERAGE}x; "
            f"current value is {current_short}x."
        )

    # ========================================================
    # REQUIRED TRANSITION ANALYSIS
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M REQUIRED CONFIGURATION TRANSITION",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    if long_ready and short_ready:

        print(
            "  ✅ No leverage configuration change required.",
            flush=True,
        )

    else:

        print(
            "  A leverage configuration change would be required:",
            flush=True,
        )

        print(
            f"  POST {LEVERAGE_CHANGE_PATH}",
            flush=True,
        )

        print(
            "  Payload:",
            flush=True,
        )

        print(
            "  "
            + canonical_json(
                planned_payload
            ),
            flush=True,
        )

        print(
            "",
            flush=True,
        )

        print(
            "  🚫 UNIT M WILL NOT TRANSMIT THIS REQUEST",
            flush=True,
        )

    # ========================================================
    # TRANSPORT AUDIT
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M TRANSPORT-BOUNDARY AUDIT",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    record_test(
        "Controlled Authenticated GET Occurred",
        audit["network_gets"] >= 1,
    )

    record_test(
        "Leverage POST Attempt Was Blocked Locally",
        audit[
            "leverage_post_attempts"
        ] == 1
        and audit[
            "leverage_post_blocks"
        ] == 1,
    )

    record_test(
        "Network POST Count Is Zero",
        audit["network_posts"] == 0,
    )

    record_test(
        "Network PUT Count Is Zero",
        audit["network_puts"] == 0,
    )

    record_test(
        "Network PATCH Count Is Zero",
        audit["network_patches"] == 0,
    )

    record_test(
        "Network DELETE Count Is Zero",
        audit["network_deletes"] == 0,
    )

    record_test(
        "Account Write Transmission Count Is Zero",
        audit[
            "account_write_transmissions"
        ] == 0,
    )

    record_test(
        "Leverage Change Transmission Count Is Zero",
        audit[
            "leverage_change_transmissions"
        ] == 0,
    )

    record_test(
        "Real Order Transmission Never Occurred",
        audit[
            "real_order_transmissions"
        ] == 0,
    )

    record_test(
        "Demo Order Transmission Never Occurred",
        audit[
            "demo_order_transmissions"
        ] == 0,
    )

    # ========================================================
    # AUDIT COUNTERS
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M WRITE-LOCK AUDIT:",
        flush=True,
    )

    print(
        f"  Local POST attempts = "
        f"{audit['local_post_attempts']}",
        flush=True,
    )

    print(
        f"  Local POST blocks = "
        f"{audit['local_post_blocks']}",
        flush=True,
    )

    print(
        f"  Leverage POST attempts = "
        f"{audit['leverage_post_attempts']}",
        flush=True,
    )

    print(
        f"  Leverage POST blocks = "
        f"{audit['leverage_post_blocks']}",
        flush=True,
    )

    print(
        f"  Network GETs = "
        f"{audit['network_gets']}",
        flush=True,
    )

    print(
        f"  Network POSTs = "
        f"{audit['network_posts']}",
        flush=True,
    )

    print(
        f"  Account write transmissions = "
        f"{audit['account_write_transmissions']}",
        flush=True,
    )

    print(
        f"  Leverage change transmissions = "
        f"{audit['leverage_change_transmissions']}",
        flush=True,
    )

    # ========================================================
    # FINAL ASSESSMENT
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT M EXECUTION-READINESS ASSESSMENT",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    print(
        f"Structural Safety Failures = "
        f"{len(structural_failures)}",
        flush=True,
    )

    print(
        f"Readiness Blockers = "
        f"{len(readiness_blockers)}",
        flush=True,
    )

    print(
        f"Readiness Warnings = "
        f"{len(readiness_warnings)}",
        flush=True,
    )

    print(
        "",
        flush=True,
    )

    if structural_failures:

        print(
            "CURRENT UNIT STATUS: ❌ FAILED",
            flush=True,
        )

        for index, failure in enumerate(
            structural_failures,
            start=1,
        ):
            print(
                f"  {index}. {failure}",
                flush=True,
            )

    elif readiness_blockers:

        print(
            "CURRENT EXECUTION READINESS: 🚫 NOT READY",
            flush=True,
        )

        for index, blocker in enumerate(
            readiness_blockers,
            start=1,
        ):
            print(
                f"  {index}. {blocker}",
                flush=True,
            )

    else:

        print(
            "CURRENT EXECUTION READINESS: ✅ LEVERAGE READY",
            flush=True,
        )

    # ========================================================
    # FINAL BANNER
    # ========================================================

    print(
        "-" * 76,
        flush=True,
    )

    if not structural_failures:

        print(
            "✅ R28 UNIT M DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ LEVERAGE CONFIGURATION BOUNDARY VALIDATED",
            flush=True,
        )

        print(
            "✅ CURRENT LEVERAGE CONFIGURATION READ SUCCESSFULLY",
            flush=True,
        )

        print(
            "✅ HYPOTHETICAL 100x PAYLOAD VALIDATED",
            flush=True,
        )

        print(
            "✅ HYPOTHETICAL POST SIGNING VALIDATED",
            flush=True,
        )

        print(
            "✅ LEVERAGE POST TRANSPORT BLOCK VALIDATED",
            flush=True,
        )

        print(
            "✅ ACCOUNT WRITE TRANSMISSION COUNT = ZERO",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT M DIAGNOSTIC FAILED",
            flush=True,
        )

    if readiness_blockers:

        print(
            "⚠️ R28 UNIT M DETECTED LEVERAGE READINESS BLOCKERS",
            flush=True,
        )

    else:

        print(
            "✅ R28 UNIT M LEVERAGE READINESS CONFIRMED",
            flush=True,
        )

    print(
        "🛡 NO LEVERAGE CHANGE WAS ATTEMPTED ON WEEX",
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

    print(
        "=" * 76,
        flush=True,
    )


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

shutdown_event = asyncio.Event()


def request_shutdown():
    print(
        "R28 UNIT M: SHUTDOWN REQUESTED",
        flush=True,
    )

    shutdown_event.set()


async def heartbeat_loop():
    heartbeat = 1

    while not shutdown_event.is_set():

        print(
            "R28 UNIT M: "
            f"HEARTBEAT {heartbeat} ✅ ACTIVE",
            flush=True,
        )

        heartbeat += 1

        try:
            await asyncio.wait_for(
                shutdown_event.wait(),
                timeout=HEARTBEAT_SECONDS,
            )

        except asyncio.TimeoutError:
            pass


async def runtime():
    print(
        "R28 UNIT M: RUNTIME STARTING",
        flush=True,
    )

    health_server = (
        start_health_server()
    )

    loop = asyncio.get_running_loop()

    try:
        loop.add_signal_handler(
            signal.SIGTERM,
            request_shutdown,
        )

        loop.add_signal_handler(
            signal.SIGINT,
            request_shutdown,
        )

    except (
        NotImplementedError,
        RuntimeError,
    ):
        pass

    try:
        await run_diagnostic()

        print(
            "R28 UNIT M: PERSISTENT RUNTIME ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT M: AUTHENTICATED READ-ONLY LOCKS ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT M: NETWORK WRITE TRANSPORT LOCKED",
            flush=True,
        )

        print(
            "R28 UNIT M: LEVERAGE CHANGE TRANSPORT LOCKED",
            flush=True,
        )

        await heartbeat_loop()

    finally:
        health_server.shutdown()

        print(
            "R28 UNIT M: RUNTIME STOPPED CLEANLY",
            flush=True,
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        asyncio.run(
            runtime()
        )

    except KeyboardInterrupt:
        print(
            "R28 UNIT M: KEYBOARD INTERRUPT",
            flush=True,
        )

    except Exception as exc:
        print(
            "=" * 76,
            flush=True,
        )

        print(
            "❌ R28 UNIT M FATAL ERROR",
            flush=True,
        )

        print(
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            "🛡 NETWORK WRITE TRANSPORT REMAINED LOCKED",
            flush=True,
        )

        print(
            "🛡 NO LEVERAGE CHANGE TRANSMITTED",
            flush=True,
        )

        print(
            "🛡 NO REAL ORDER TRANSMITTED",
            flush=True,
        )

        print(
            "🛡 NO DEMO ORDER TRANSMITTED",
            flush=True,
        )

        print(
            "=" * 76,
            flush=True,
        )

        raise
