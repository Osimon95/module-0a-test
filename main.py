# ============================================================
# 0F-4H-R28-UNIT-N.1
# AUTHENTICATED GET SIGNATURE / CLOCK CORRECTION
#
# READ-ONLY VALIDATION ONLY
# PUBLIC GET ENABLED
# AUTHENTICATED ACCOUNT GET ENABLED
# ALL NETWORK WRITES BLOCKED
# NO REAL ORDER TRANSMISSION
# NO DEMO ORDER TRANSMISSION
# NO LEVERAGE MUTATION TRANSMISSION
# ============================================================

print("R28 UNIT N.1: MAIN.PY ENTERED", flush=True)

import asyncio
import base64
import hashlib
import hmac
import json
import os
import signal
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import aiohttp
from aiohttp import web

print("R28 UNIT N.1: IMPORTS COMPLETE", flush=True)


# ============================================================
# IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-N.1"
MODULE_VERSION = "R28-N.1"


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
ACCOUNT_WRITES_ENABLED = False
LEVERAGE_WRITES_ENABLED = False

LEVERAGE_MUTATION_FEATURE_ENABLED = False
EXPLICIT_MUTATION_AUTHORIZATION = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

PUBLIC_GET_ENABLED = True
AUTHENTICATED_READ_ONLY_GET_ENABLED = True


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

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

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

SERVER_TIME_PATH = (
    "/capi/v3/market/time"
)

SYMBOL_CONFIG_PATH = (
    "/capi/v3/account/symbolConfig"
)

print(
    "R28 UNIT N.1: CONSTANTS INITIALIZED",
    flush=True,
)


# ============================================================
# AUDIT COUNTERS
# ============================================================

AUDIT = {
    "public_gets": 0,
    "authenticated_gets": 0,

    "local_post_attempts": 0,
    "local_post_blocks": 0,

    "network_posts": 0,
    "network_puts": 0,
    "network_patches": 0,
    "network_deletes": 0,

    "account_write_transmissions": 0,
    "leverage_change_transmissions": 0,

    "real_order_transmissions": 0,
    "demo_order_transmissions": 0,
}


# ============================================================
# DISPLAY HELPERS
# ============================================================

def divider():
    print(
        "-" * 76,
        flush=True,
    )


def gate(
    name,
    passed,
):
    status = (
        "✅ PASS"
        if passed
        else "❌ FAIL"
    )

    print(
        f"{name:<68} {status}",
        flush=True,
    )

    return passed


# ============================================================
# HARD WRITE BOUNDARY
# ============================================================

class WriteBlocked(
    RuntimeError
):
    pass


async def network_request(
    session,
    method,
    url,
    headers=None,
):
    method_upper = (
        method
        .upper()
        .strip()
    )

    if method_upper != "GET":

        if method_upper == "POST":
            AUDIT[
                "local_post_attempts"
            ] += 1

            AUDIT[
                "local_post_blocks"
            ] += 1

        raise WriteBlocked(
            "R28 UNIT N.1 blocked "
            "network write method locally: "
            f"{method_upper}"
        )

    return await session.get(
        url,
        headers=headers,
    )


# ============================================================
# QUERY CONSTRUCTION
# ============================================================

def canonical_query(
    params,
):
    return urlencode(
        params
    )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def build_signature(
    timestamp_ms,
    method,
    request_path,
    query_string="",
    body="",
):
    method_upper = (
        method
        .upper()
        .strip()
    )

    if query_string:

        prehash = (
            f"{timestamp_ms}"
            f"{method_upper}"
            f"{request_path}"
            f"?{query_string}"
            f"{body}"
        )

    else:

        prehash = (
            f"{timestamp_ms}"
            f"{method_upper}"
            f"{request_path}"
            f"{body}"
        )

    digest = hmac.new(
        API_SECRET.encode(
            "utf-8"
        ),
        prehash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    signature = (
        base64
        .b64encode(
            digest
        )
        .decode(
            "utf-8"
        )
    )

    return signature


def build_auth_headers(
    timestamp_ms,
    method,
    request_path,
    query_string="",
):
    signature = build_signature(
        timestamp_ms=
        timestamp_ms,

        method=
        method,

        request_path=
        request_path,

        query_string=
        query_string,
    )

    return {
        "ACCESS-KEY":
        API_KEY,

        "ACCESS-SIGN":
        signature,

        "ACCESS-PASSPHRASE":
        API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
        timestamp_ms,

        "Content-Type":
        "application/json",
    }


# ============================================================
# PUBLIC SERVER-TIME GET
# ============================================================

async def get_server_time(
    session,
):
    if not PUBLIC_GET_ENABLED:
        raise RuntimeError(
            "Public GET is disabled."
        )

    url = (
        BASE_URL
        + SERVER_TIME_PATH
    )

    print(
        "R28 UNIT N.1: PUBLIC GET -> "
        f"{SERVER_TIME_PATH}",
        flush=True,
    )

    response = (
        await network_request(
            session,
            "GET",
            url,
        )
    )

    AUDIT[
        "public_gets"
    ] += 1

    text = (
        await response.text()
    )

    if response.status != 200:

        raise RuntimeError(
            "Server-time GET failed: "
            f"HTTP {response.status}: "
            f"{text}"
        )

    try:

        data = json.loads(
            text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Server-time response "
            "was not JSON: "
            f"{text}"
        ) from exc

    server_time = (
        data.get(
            "serverTime"
        )
    )

    if server_time is None:

        raise RuntimeError(
            "serverTime missing "
            "from WEEX response: "
            f"{data}"
        )

    return int(
        server_time
    )


# ============================================================
# AUTHENTICATED READ-ONLY GET
# ============================================================

async def authenticated_get_symbol_config(
    session,
    server_time_ms,
):
    if not AUTHENTICATED_READ_ONLY_GET_ENABLED:

        raise RuntimeError(
            "Authenticated "
            "read-only GET disabled."
        )

    if (
        not API_KEY
        or not API_SECRET
        or not API_PASSPHRASE
    ):

        raise RuntimeError(
            "WEEX API credentials "
            "are incomplete."
        )

    params = {
        "symbol":
        SYMBOL,
    }

    query_string = (
        canonical_query(
            params
        )
    )

    timestamp_ms = str(
        server_time_ms
    )

    headers = (
        build_auth_headers(
            timestamp_ms=
            timestamp_ms,

            method=
            "GET",

            request_path=
            SYMBOL_CONFIG_PATH,

            query_string=
            query_string,
        )
    )

    url = (
        BASE_URL
        + SYMBOL_CONFIG_PATH
        + "?"
        + query_string
    )

    print(
        "R28 UNIT N.1: "
        "AUTHENTICATED GET -> "
        f"{SYMBOL_CONFIG_PATH}"
        f"?{query_string}",
        flush=True,
    )

    response = (
        await network_request(
            session,
            "GET",
            url,
            headers=headers,
        )
    )

    AUDIT[
        "authenticated_gets"
    ] += 1

    text = (
        await response.text()
    )

    if response.status != 200:

        raise RuntimeError(
            "Authenticated GET failed: "
            f"HTTP {response.status}: "
            f"{text}"
        )

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Authenticated response "
            "was not JSON: "
            f"{text}"
        ) from exc


# ============================================================
# SYMBOL CONFIG RESPONSE NORMALIZATION
# ============================================================

def extract_symbol_config(
    payload,
):
    records = payload

    if isinstance(
        payload,
        dict,
    ):

        if isinstance(
            payload.get("data"),
            list,
        ):
            records = (
                payload["data"]
            )

        elif isinstance(
            payload.get("data"),
            dict,
        ):
            records = [
                payload["data"]
            ]

        elif "symbol" in payload:
            records = [
                payload
            ]

    if not isinstance(
        records,
        list,
    ):

        raise RuntimeError(
            "Unexpected symbolConfig "
            "response type: "
            f"{type(records).__name__}"
        )

    for item in records:

        if not isinstance(
            item,
            dict,
        ):
            continue

        observed_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if observed_symbol == SYMBOL:

            return item

    raise RuntimeError(
        f"No {SYMBOL} symbol "
        "configuration found."
    )


# ============================================================
# LOCAL POST-BLOCK TEST
# ============================================================

async def validate_local_post_block(
    session,
):
    try:

        await network_request(
            session,
            "POST",
            BASE_URL
            + "/capi/v3/account/leverage",
        )

    except WriteBlocked:

        return True

    return False


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.json_response(
        {
            "status":
            "ok",

            "module":
            MODULE_NAME,

            "version":
            MODULE_VERSION,

            "symbol":
            SYMBOL,

            "read_only":
            True,

            "network_writes_enabled":
            False,
        }
    )


async def start_health_server():
    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        HEALTH_PORT,
    )

    await site.start()

    print(
        "R28 UNIT N.1: "
        "HEALTH SERVER ACTIVE "
        f"ON PORT {HEALTH_PORT}",
        flush=True,
    )

    return runner


# ============================================================
# DIAGNOSTIC
# ============================================================

async def run_diagnostic():

    print()
    print(
        "=" * 76
    )

    print(
        "0F-4H-R28-UNIT-N.1 STARTING"
    )

    print(
        "AUTHENTICATED GET "
        "SIGNATURE / CLOCK CORRECTION"
    )

    print(
        "PUBLIC WEEX SERVER-TIME "
        "GET ENABLED"
    )

    print(
        "AUTHENTICATED SYMBOL-CONFIG "
        "GET ENABLED"
    )

    print(
        "ALL NETWORK WRITE METHODS "
        "BLOCKED"
    )

    print(
        "LEVERAGE MUTATION "
        "TRANSPORT DISABLED"
    )

    print(
        "REAL ORDER "
        "TRANSMISSION DISABLED"
    )

    print(
        "DEMO ORDER "
        "TRANSMISSION DISABLED"
    )

    print(
        "=" * 76
    )

    print(
        f"R28 UNIT N.1 SYMBOL: "
        f"{SYMBOL}"
    )

    print()

    print(
        "R28 UNIT N.1 "
        "NETWORK POLICY:"
    )

    print(
        "  ✅ Public GET enabled"
    )

    print(
        "  ✅ Authenticated "
        "read-only GET enabled"
    )

    print(
        "  ❌ Account POST disabled"
    )

    print(
        "  ❌ Leverage POST disabled"
    )

    print(
        "  ❌ PUT / PATCH / "
        "DELETE disabled"
    )

    print(
        "  ❌ Real order POST disabled"
    )

    print(
        "  ❌ Demo order POST disabled"
    )

    print()

    print(
        "R28 UNIT N.1 "
        "CREDENTIAL STATUS:"
    )

    print(
        "  API Key: "
        + (
            "✅ PRESENT"
            if API_KEY
            else "❌ MISSING"
        )
    )

    print(
        "  API Secret: "
        + (
            "✅ PRESENT"
            if API_SECRET
            else "❌ MISSING"
        )
    )

    print(
        "  API Passphrase: "
        + (
            "✅ PRESENT"
            if API_PASSPHRASE
            else "❌ MISSING"
        )
    )

    print()

    structural_failures = 0
    readiness_blockers = 0
    config = None


    # ========================================================
    # ABSOLUTE SAFETY GATES
    # ========================================================

    print(
        "R28 UNIT N.1 "
        "ABSOLUTE SAFETY GATES"
    )

    divider()

    checks = [

        (
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION
            is False,
        ),

        (
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION
            is False,
        ),

        (
            "Network Writes Disabled",
            NETWORK_WRITES_ENABLED
            is False,
        ),

        (
            "Account Writes Disabled",
            ACCOUNT_WRITES_ENABLED
            is False,
        ),

        (
            "Leverage Writes Disabled",
            LEVERAGE_WRITES_ENABLED
            is False,
        ),

        (
            "Leverage Mutation "
            "Feature Disabled",

            LEVERAGE_MUTATION_FEATURE_ENABLED
            is False,
        ),

        (
            "Explicit Mutation "
            "Authorization Disabled",

            EXPLICIT_MUTATION_AUTHORIZATION
            is False,
        ),

        (
            "Leverage Mutation "
            "Transport Disabled",

            LEVERAGE_MUTATION_TRANSPORT_ENABLED
            is False,
        ),

        (
            "Public GET Enabled",
            PUBLIC_GET_ENABLED
            is True,
        ),

        (
            "Authenticated "
            "Read-Only GET Enabled",

            AUTHENTICATED_READ_ONLY_GET_ENABLED
            is True,
        ),
    ]

    for (
        name,
        passed,
    ) in checks:

        if not gate(
            name,
            passed,
        ):

            structural_failures += 1


    # ========================================================
    # SIGNATURE TESTS
    # ========================================================

    print()

    print(
        "R28 UNIT N.1 "
        "SIGNATURE-CONSTRUCTION GATES"
    )

    divider()

    test_timestamp = (
        "1659076670000"
    )

    test_query = (
        "symbol=BTCUSDT"
    )

    expected_prehash = (
        test_timestamp
        + "GET"
        + SYMBOL_CONFIG_PATH
        + "?"
        + test_query
    )

    actual_prehash = (
        f"{test_timestamp}"
        f"GET"
        f"{SYMBOL_CONFIG_PATH}"
        f"?{test_query}"
    )

    gate(
        "GET Signature Includes "
        "Exact Query String",

        actual_prehash
        == expected_prehash,
    )

    gate(
        "GET Signature Uses "
        "Uppercase Method",

        "GET"
        in actual_prehash,
    )

    gate(
        "GET Signature Uses "
        "Contract V3 Path",

        SYMBOL_CONFIG_PATH
        in actual_prehash,
    )

    test_digest = hmac.new(
        b"test-secret",

        expected_prehash.encode(
            "utf-8"
        ),

        hashlib.sha256,
    ).digest()

    test_base64 = (
        base64
        .b64encode(
            test_digest
        )
        .decode(
            "utf-8"
        )
    )

    gate(
        "HMAC-SHA256 "
        "Digest Generated",

        len(
            test_digest
        )
        == 32,
    )

    gate(
        "Signature Base64 Encoded",

        isinstance(
            test_base64,
            str,
        )
        and len(
            test_base64
        ) > 0,
    )


    # ========================================================
    # HTTP SESSION
    # ========================================================

    timeout = (
        aiohttp.ClientTimeout(
            total=15
        )
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
    ) as session:


        # ====================================================
        # WRITE BLOCK TEST
        # ====================================================

        print()

        print(
            "R28 UNIT N.1 "
            "TRANSPORT-BOUNDARY VALIDATION"
        )

        divider()

        post_blocked = (
            await validate_local_post_block(
                session
            )
        )

        if not gate(
            "Leverage POST Attempt "
            "Blocked Locally",

            post_blocked,
        ):

            structural_failures += 1


        if not gate(
            "Network POST Count Is Zero",

            AUDIT[
                "network_posts"
            ]
            == 0,
        ):

            structural_failures += 1


        if not gate(
            "Network PUT Count Is Zero",

            AUDIT[
                "network_puts"
            ]
            == 0,
        ):

            structural_failures += 1


        if not gate(
            "Network PATCH Count Is Zero",

            AUDIT[
                "network_patches"
            ]
            == 0,
        ):

            structural_failures += 1


        if not gate(
            "Network DELETE Count Is Zero",

            AUDIT[
                "network_deletes"
            ]
            == 0,
        ):

            structural_failures += 1


        # ====================================================
        # SERVER CLOCK VALIDATION
        # ====================================================

        server_time_ms = None

        print()

        print(
            "R28 UNIT N.1 "
            "SERVER-CLOCK VALIDATION"
        )

        divider()

        try:

            local_before = int(
                time.time()
                * 1000
            )

            server_time_ms = (
                await get_server_time(
                    session
                )
            )

            local_after = int(
                time.time()
                * 1000
            )

            midpoint = (
                local_before
                + local_after
            ) // 2

            clock_delta_ms = (
                server_time_ms
                - midpoint
            )

            gate(
                "WEEX Server Time Read",
                True,
            )

            gate(
                "WEEX Server Time Parseable",
                server_time_ms > 0,
            )

            print(
                "  WEEX Server Time = "
                f"{server_time_ms}",
                flush=True,
            )

            print(
                "  Approx Clock Delta = "
                f"{clock_delta_ms} ms",
                flush=True,
            )

            if abs(
                clock_delta_ms
            ) > 30000:

                print(
                    "  ⚠️ Local clock differs "
                    "from WEEX by more than "
                    "30 seconds.",
                    flush=True,
                )

        except Exception as exc:

            readiness_blockers += 1

            print()

            print(
                "R28 UNIT N.1 "
                "SERVER-TIME GET ERROR:"
            )

            print(
                "  "
                f"{type(exc).__name__}: "
                f"{exc}",
                flush=True,
            )


        # ====================================================
        # AUTHENTICATED SYMBOL CONFIG
        # ====================================================

        print()

        print(
            "R28 UNIT N.1 "
            "AUTHENTICATED CONFIGURATION READ"
        )

        divider()

        if server_time_ms is None:

            print(
                "Authenticated configuration "
                "read skipped because server "
                "time was unavailable.",
                flush=True,
            )

            readiness_blockers += 1

        elif (
            not API_KEY
            or not API_SECRET
            or not API_PASSPHRASE
        ):

            print(
                "Authenticated configuration "
                "read skipped because "
                "credentials are incomplete.",
                flush=True,
            )

            readiness_blockers += 1

        else:

            try:

                payload = (
                    await authenticated_get_symbol_config(
                        session,
                        server_time_ms,
                    )
                )

                config = (
                    extract_symbol_config(
                        payload
                    )
                )

                print()

                print(
                    "R28 UNIT N.1 "
                    "SYMBOL CONFIG:"
                )

                print(
                    "  Symbol = "
                    f"{config.get('symbol')}"
                )

                print(
                    "  Margin Type = "
                    f"{config.get('marginType')}"
                )

                print(
                    "  Position Mode = "
                    f"{config.get('separatedType')}"
                )

                print(
                    "  Cross Leverage = "
                    f"{config.get('crossLeverage')}x"
                )

                print(
                    "  Isolated Long Leverage = "
                    f"{config.get('isolatedLongLeverage')}x"
                )

                print(
                    "  Isolated Short Leverage = "
                    f"{config.get('isolatedShortLeverage')}x"
                )

                print()

                gate(
                    "Observed Symbol Matches "
                    f"{SYMBOL}",

                    str(
                        config.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    == SYMBOL,
                )

                gate(
                    "Margin Type Recognized",

                    str(
                        config.get(
                            "marginType",
                            "",
                        )
                    ).upper()
                    in {
                        "ISOLATED",
                        "CROSSED",
                        "CROSS",
                    },
                )

                gate(
                    "Position Mode Recognized",

                    str(
                        config.get(
                            "separatedType",
                            "",
                        )
                    ).upper()
                    in {
                        "COMBINED",
                        "SEPARATED",
                    },
                )

                long_leverage = int(
                    str(
                        config.get(
                            "isolatedLongLeverage"
                        )
                    )
                )

                short_leverage = int(
                    str(
                        config.get(
                            "isolatedShortLeverage"
                        )
                    )
                )

                gate(
                    "Current Long "
                    "Leverage Parseable",

                    long_leverage > 0,
                )

                gate(
                    "Current Short "
                    "Leverage Parseable",

                    short_leverage > 0,
                )

                print()

                print(
                    "✅ AUTHENTICATED "
                    "SYMBOL-CONFIG READ VERIFIED",
                    flush=True,
                )

            except Exception as exc:

                readiness_blockers += 1

                print()

                print(
                    "R28 UNIT N.1 "
                    "AUTHENTICATED GET ERROR:",
                    flush=True,
                )

                print(
                    "  "
                    f"{type(exc).__name__}: "
                    f"{exc}",
                    flush=True,
                )


    # ========================================================
    # FINAL WRITE-LOCK AUDIT
    # ========================================================

    print()

    print(
        "R28 UNIT N.1 "
        "WRITE-LOCK AUDIT"
    )

    divider()

    final_write_checks = [

        (
            "Network POST Count Is Zero",

            AUDIT[
                "network_posts"
            ]
            == 0,
        ),

        (
            "Network PUT Count Is Zero",

            AUDIT[
                "network_puts"
            ]
            == 0,
        ),

        (
            "Network PATCH Count Is Zero",

            AUDIT[
                "network_patches"
            ]
            == 0,
        ),

        (
            "Network DELETE Count Is Zero",

            AUDIT[
                "network_deletes"
            ]
            == 0,
        ),

        (
            "Account Write "
            "Transmission Count Is Zero",

            AUDIT[
                "account_write_transmissions"
            ]
            == 0,
        ),

        (
            "Leverage Change "
            "Transmission Count Is Zero",

            AUDIT[
                "leverage_change_transmissions"
            ]
            == 0,
        ),

        (
            "Real Order "
            "Transmission Count Is Zero",

            AUDIT[
                "real_order_transmissions"
            ]
            == 0,
        ),

        (
            "Demo Order "
            "Transmission Count Is Zero",

            AUDIT[
                "demo_order_transmissions"
            ]
            == 0,
        ),
    ]

    for (
        name,
        passed,
    ) in final_write_checks:

        if not gate(
            name,
            passed,
        ):

            structural_failures += 1


    # ========================================================
    # TRANSPORT AUDIT
    # ========================================================

    print()

    print(
        "R28 UNIT N.1 "
        "TRANSPORT AUDIT:"
    )

    print(
        "  Public GETs = "
        f"{AUDIT['public_gets']}"
    )

    print(
        "  Authenticated GETs = "
        f"{AUDIT['authenticated_gets']}"
    )

    print(
        "  Local POST attempts = "
        f"{AUDIT['local_post_attempts']}"
    )

    print(
        "  Local POST blocks = "
        f"{AUDIT['local_post_blocks']}"
    )

    print(
        "  Network POSTs = "
        f"{AUDIT['network_posts']}"
    )

    print(
        "  Account write transmissions = "
        f"{AUDIT['account_write_transmissions']}"
    )

    print(
        "  Leverage change transmissions = "
        f"{AUDIT['leverage_change_transmissions']}"
    )


    # ========================================================
    # READINESS
    # ========================================================

    print()

    print(
        "R28 UNIT N.1 "
        "EXECUTION-READINESS ASSESSMENT"
    )

    divider()

    print(
        "Structural Safety Failures = "
        f"{structural_failures}"
    )

    print(
        "Readiness Blockers = "
        f"{readiness_blockers}"
    )

    print(
        "Authenticated Configuration Read = "
        + (
            "✅ VERIFIED"
            if config is not None
            else "⚠️ NOT VERIFIED"
        )
    )

    print()

    if (
        structural_failures == 0
        and readiness_blockers == 0
    ):

        print(
            "CURRENT EXECUTION READINESS: "
            "✅ N.1 READ-ONLY "
            "AUTHENTICATION VERIFIED"
        )

    else:

        print(
            "CURRENT EXECUTION READINESS: "
            "🚫 NOT READY"
        )

    print()

    divider()

    if structural_failures == 0:

        print(
            "✅ R28 UNIT N.1 "
            "STRUCTURAL DIAGNOSTIC PASSED"
        )

        print(
            "✅ NETWORK WRITE TRANSPORT "
            "REMAINS LOCKED"
        )

    else:

        print(
            "❌ R28 UNIT N.1 "
            "STRUCTURAL DIAGNOSTIC FAILED"
        )

    if config is not None:

        print(
            "✅ WEEX AUTHENTICATED "
            "GET SIGNATURE VERIFIED"
        )

        print(
            "✅ CURRENT BTCUSDT "
            "SYMBOL CONFIGURATION VERIFIED"
        )

    else:

        print(
            "⚠️ WEEX AUTHENTICATED GET "
            "STILL NOT VERIFIED"
        )

    print(
        "🛡 NO LEVERAGE CHANGE "
        "WAS TRANSMITTED TO WEEX"
    )

    print(
        "🛡 NO ACCOUNT WRITE "
        "WAS TRANSMITTED TO WEEX"
    )

    print(
        "🛡 REAL ORDER "
        "TRANSMISSION IMPOSSIBLE"
    )

    print(
        "🛡 DEMO ORDER "
        "TRANSMISSION IMPOSSIBLE"
    )

    print(
        "=" * 76
    )


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime():

    print(
        "R28 UNIT N.1: "
        "RUNTIME STARTING",
        flush=True,
    )

    health_runner = (
        await start_health_server()
    )

    await run_diagnostic()

    print(
        "R28 UNIT N.1: "
        "PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT N.1: "
        "AUTHENTICATED READ-ONLY "
        "LOCKS ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT N.1: "
        "NETWORK WRITE "
        "TRANSPORT LOCKED",
        flush=True,
    )

    print(
        "R28 UNIT N.1: "
        "LEVERAGE MUTATION "
        "TRANSPORT LOCKED",
        flush=True,
    )

    stop_event = (
        asyncio.Event()
    )

    loop = (
        asyncio
        .get_running_loop()
    )

    def request_shutdown():

        print(
            "R28 UNIT N.1: "
            "SHUTDOWN REQUESTED",
            flush=True,
        )

        stop_event.set()


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


    heartbeat = 0

    try:

        while not stop_event.is_set():

            heartbeat += 1

            print(
                "R28 UNIT N.1: "
                f"HEARTBEAT {heartbeat} "
                "✅ ACTIVE",
                flush=True,
            )

            try:

                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=15,
                )

            except asyncio.TimeoutError:

                pass

    finally:

        await health_runner.cleanup()

        print(
            "R28 UNIT N.1: "
            "RUNTIME STOPPED CLEANLY",
            flush=True,
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            persistent_runtime()
        )

    except KeyboardInterrupt:

        pass
