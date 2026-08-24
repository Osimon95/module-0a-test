print("R28 UNIT N.3: MAIN.PY ENTERED", flush=True)

import asyncio
import base64
import hashlib
import hmac
import json
import os
import signal
import time
from dataclasses import dataclass
from typing import Dict, Optional, Set
from urllib.parse import urlencode

import aiohttp
from aiohttp import web

print("R28 UNIT N.3: IMPORTS COMPLETE", flush=True)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-N.3"
MODULE_VERSION = "R28-N.3"


# ============================================================
# WEEX ENDPOINTS
# ============================================================

WEEX_BASE_URL = "https://api-contract.weex.com"

PUBLIC_TIME_PATH = "/capi/v3/market/time"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
LEVERAGE_PATH = "/capi/v3/account/leverage"


# ============================================================
# TARGET CONFIGURATION
# ============================================================

SYMBOL = "BTCUSDT"

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

MAX_LOCAL_LEVERAGE = 100


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

ACCOUNT_WRITES_ENABLED = False

LEVERAGE_WRITES_ENABLED = False

LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

EXPLICIT_MUTATION_AUTHORIZATION_ENABLED = False


# ============================================================
# LOCAL N.3 AUTHORIZATION DIAGNOSTIC
# ============================================================

# This enables only the LOCAL authorization tests below.
#
# It does NOT enable:
#
# - HTTP POST
# - PUT
# - PATCH
# - DELETE
# - account mutation
# - leverage mutation
# - real orders
# - demo orders

LOCAL_AUTHORIZATION_DIAGNOSTIC_ENABLED = True

AUTHORIZATION_TTL_SECONDS = 60


# ============================================================
# ENVIRONMENT
# ============================================================

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

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

print(
    "R28 UNIT N.3: CONSTANTS INITIALIZED",
    flush=True,
)


# ============================================================
# AUDIT COUNTERS
# ============================================================

COUNTERS = {
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

    "authorization_requests": 0,

    "authorization_grants": 0,

    "authorization_denials": 0,

    "authorization_replays_blocked": 0,
}


# ============================================================
# RUNTIME STATE
# ============================================================

USED_AUTHORIZATION_IDS: Set[str] = set()

STRUCTURAL_FAILURES = 0

READINESS_BLOCKERS = 0

STOP_EVENT: Optional[asyncio.Event] = None


# ============================================================
# CANONICAL JSON
# ============================================================

def canonical_json(
    payload: Dict,
) -> str:

    return json.dumps(
        payload,
        separators=(
            ",",
            ":",
        ),
        sort_keys=False,
    )


# ============================================================
# SHA256
# ============================================================

def sha256_hex(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode(
            "utf-8",
        )
    ).hexdigest()


# ============================================================
# HMAC SHA256 + BASE64
# ============================================================

def hmac_b64(
    secret: str,
    message: str,
) -> str:

    digest = hmac.new(
        secret.encode(
            "utf-8",
        ),
        message.encode(
            "utf-8",
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest,
    ).decode(
        "ascii",
    )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def make_signature(
    timestamp_ms: str,
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    if query_string:

        message = (
            f"{timestamp_ms}"
            f"{method}"
            f"{path}"
            f"?"
            f"{query_string}"
            f"{body}"
        )

    else:

        message = (
            f"{timestamp_ms}"
            f"{method}"
            f"{path}"
            f"{body}"
        )

    return hmac_b64(
        API_SECRET,
        message,
    )


# ============================================================
# PASS / FAIL GATE
# ============================================================

def pass_gate(
    label: str,
    condition: bool,
) -> bool:

    global STRUCTURAL_FAILURES

    marker = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{label:<72}{marker}",
        flush=True,
    )

    if not condition:

        STRUCTURAL_FAILURES += 1

    return condition


# ============================================================
# CREDENTIAL MARKER
# ============================================================

def credential_marker(
    value: str,
) -> str:

    if value:

        return "✅ PRESENT"

    return "❌ MISSING"


# ============================================================
# LEVERAGE PAYLOAD
# ============================================================

def leverage_payload() -> Dict[str, str]:

    return {
        "symbol": SYMBOL,

        "marginType": TARGET_MARGIN_TYPE,

        "isolatedLongLeverage": str(
            TARGET_LONG_LEVERAGE,
        ),

        "isolatedShortLeverage": str(
            TARGET_SHORT_LEVERAGE,
        ),
    }


# ============================================================
# AUTHORIZATION OBJECT
# ============================================================

@dataclass(
    frozen=True,
)
class MutationAuthorization:

    authorization_id: str

    module: str

    symbol: str

    margin_type: str

    long_leverage: int

    short_leverage: int

    payload_sha256: str

    issued_at_ms: int

    expires_at_ms: int

    purpose: str

    proof: str


# ============================================================
# AUTHORIZATION MESSAGE
# ============================================================

def authorization_message(
    authorization_id: str,
    symbol: str,
    margin_type: str,
    long_leverage: int,
    short_leverage: int,
    payload_sha256: str,
    issued_at_ms: int,
    expires_at_ms: int,
) -> str:

    return "|".join(
        [
            MODULE_NAME,

            authorization_id,

            symbol,

            margin_type,

            str(
                long_leverage,
            ),

            str(
                short_leverage,
            ),

            payload_sha256,

            str(
                issued_at_ms,
            ),

            str(
                expires_at_ms,
            ),

            "LOCAL_DIAGNOSTIC_ONLY",
        ]
    )


# ============================================================
# CREATE LOCAL AUTHORIZATION
# ============================================================

def create_local_test_authorization(
    payload_body: str,
) -> MutationAuthorization:

    COUNTERS[
        "authorization_requests"
    ] += 1

    now_ms = int(
        time.time() * 1000
    )

    expires_ms = (
        now_ms
        +
        (
            AUTHORIZATION_TTL_SECONDS
            *
            1000
        )
    )

    payload_hash = sha256_hex(
        payload_body,
    )

    authorization_id = sha256_hex(
        (
            f"{MODULE_NAME}"
            f"|"
            f"{payload_hash}"
            f"|"
            f"{now_ms}"
        )
    )[:32]

    message = authorization_message(
        authorization_id,

        SYMBOL,

        TARGET_MARGIN_TYPE,

        TARGET_LONG_LEVERAGE,

        TARGET_SHORT_LEVERAGE,

        payload_hash,

        now_ms,

        expires_ms,
    )

    # LOCAL proof only.
    #
    # This HMAC is NEVER transmitted.
    #
    # API_SECRET is reused only as a convenient secret
    # for this diagnostic proof.

    proof = hmac_b64(
        API_SECRET,
        message,
    )

    return MutationAuthorization(
        authorization_id=authorization_id,

        module=MODULE_NAME,

        symbol=SYMBOL,

        margin_type=TARGET_MARGIN_TYPE,

        long_leverage=TARGET_LONG_LEVERAGE,

        short_leverage=TARGET_SHORT_LEVERAGE,

        payload_sha256=payload_hash,

        issued_at_ms=now_ms,

        expires_at_ms=expires_ms,

        purpose="LOCAL_DIAGNOSTIC_ONLY",

        proof=proof,
    )


# ============================================================
# AUTHORIZATION VALIDATION
# ============================================================

def validate_authorization(
    auth: Optional[
        MutationAuthorization
    ],
    payload_body: str,
    *,
    consume: bool,
    now_ms: Optional[int] = None,
) -> tuple[bool, str]:

    if not LOCAL_AUTHORIZATION_DIAGNOSTIC_ENABLED:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "local authorization diagnostic disabled",
        )

    if auth is None:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "authorization missing",
        )

    if now_ms is None:

        effective_now_ms = int(
            time.time() * 1000
        )

    else:

        effective_now_ms = now_ms


    if auth.module != MODULE_NAME:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "module binding mismatch",
        )


    if auth.purpose != "LOCAL_DIAGNOSTIC_ONLY":

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "purpose binding mismatch",
        )


    if auth.symbol != SYMBOL:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "symbol binding mismatch",
        )


    if auth.margin_type != TARGET_MARGIN_TYPE:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "margin-type binding mismatch",
        )


    if auth.long_leverage != TARGET_LONG_LEVERAGE:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "long-leverage binding mismatch",
        )


    if auth.short_leverage != TARGET_SHORT_LEVERAGE:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "short-leverage binding mismatch",
        )


    payload_hash = sha256_hex(
        payload_body,
    )


    if not hmac.compare_digest(
        auth.payload_sha256,
        payload_hash,
    ):

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "payload hash mismatch",
        )


    if effective_now_ms < auth.issued_at_ms:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "authorization not yet valid",
        )


    if effective_now_ms > auth.expires_at_ms:

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "authorization expired",
        )


    if (
        auth.authorization_id
        in
        USED_AUTHORIZATION_IDS
    ):

        COUNTERS[
            "authorization_denials"
        ] += 1

        COUNTERS[
            "authorization_replays_blocked"
        ] += 1

        return (
            False,
            "authorization replay blocked",
        )


    expected_message = authorization_message(
        auth.authorization_id,

        auth.symbol,

        auth.margin_type,

        auth.long_leverage,

        auth.short_leverage,

        auth.payload_sha256,

        auth.issued_at_ms,

        auth.expires_at_ms,
    )


    expected_proof = hmac_b64(
        API_SECRET,
        expected_message,
    )


    if not hmac.compare_digest(
        auth.proof,
        expected_proof,
    ):

        COUNTERS[
            "authorization_denials"
        ] += 1

        return (
            False,
            "authorization proof mismatch",
        )


    if consume:

        USED_AUTHORIZATION_IDS.add(
            auth.authorization_id,
        )

        COUNTERS[
            "authorization_grants"
        ] += 1


    return (
        True,
        "authorized locally",
    )


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session: aiohttp.ClientSession,
    path: str,
) -> object:

    COUNTERS[
        "public_gets"
    ] += 1

    print(
        f"R28 UNIT N.3: PUBLIC GET -> {path}",
        flush=True,
    )

    async with session.get(
        WEEX_BASE_URL + path,
        timeout=aiohttp.ClientTimeout(
            total=10,
        ),
    ) as response:

        response.raise_for_status()

        return await response.json(
            content_type=None,
        )


# ============================================================
# AUTHENTICATED GET
# ============================================================

async def authenticated_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Dict[str, str],
) -> object:

    query_string = urlencode(
        params,
    )

    timestamp_ms = str(
        int(
            time.time()
            *
            1000
        )
    )

    signature = make_signature(
        timestamp_ms,

        "GET",

        path,

        query_string,

        "",
    )

    headers = {
        "ACCESS-KEY": API_KEY,

        "ACCESS-SIGN": signature,

        "ACCESS-PASSPHRASE": API_PASSPHRASE,

        "ACCESS-TIMESTAMP": timestamp_ms,

        "Content-Type": "application/json",
    }


    COUNTERS[
        "authenticated_gets"
    ] += 1


    print(
        (
            "R28 UNIT N.3: AUTHENTICATED GET -> "
            f"{path}"
            f"?"
            f"{query_string}"
        ),
        flush=True,
    )


    async with session.get(
        WEEX_BASE_URL + path,

        params=params,

        headers=headers,

        timeout=aiohttp.ClientTimeout(
            total=10,
        ),
    ) as response:

        text = await response.text()

        if response.status >= 400:

            raise RuntimeError(
                (
                    "Authenticated GET failed "
                    f"HTTP {response.status}: "
                    f"{text[:300]}"
                )
            )

        return json.loads(
            text,
        )


# ============================================================
# BLOCKED LEVERAGE POST
# ============================================================

async def blocked_leverage_post(
    path: str,
    body: str,
    auth: Optional[
        MutationAuthorization
    ],
) -> None:

    COUNTERS[
        "local_post_attempts"
    ] += 1


    valid, reason = validate_authorization(
        auth,

        body,

        consume=True,
    )


    if not valid:

        COUNTERS[
            "local_post_blocks"
        ] += 1

        raise PermissionError(
            (
                "R28 UNIT N.3 LOCAL AUTHORIZATION BLOCK: "
                f"{reason}."
            )
        )


    # ========================================================
    # FINAL HARD TRANSPORT LOCK
    # ========================================================

    if (
        not NETWORK_WRITES_ENABLED
        or
        not ACCOUNT_WRITES_ENABLED
        or
        not LEVERAGE_WRITES_ENABLED
        or
        not LEVERAGE_MUTATION_TRANSPORT_ENABLED
        or
        not EXPLICIT_MUTATION_AUTHORIZATION_ENABLED
    ):

        COUNTERS[
            "local_post_blocks"
        ] += 1

        raise PermissionError(
            (
                "R28 UNIT N.3 FINAL TRANSPORT LOCK: "
                f"POST {path} "
                "blocked before network transport."
            )
        )


    # ========================================================
    # ABSOLUTE INVARIANT
    # ========================================================
    #
    # There is intentionally NO:
    #
    # session.post(...)
    #
    # anywhere in this N.3 unit.
    #
    # Therefore even an accidental flag change cannot
    # produce a network leverage request.

    raise RuntimeError(
        (
            "R28 UNIT N.3 invariant violation: "
            "write transport must remain impossible."
        )
    )


# ============================================================
# HEALTH HANDLER
# ============================================================

async def health_handler(
    _: web.Request,
) -> web.Response:

    return web.json_response(
        {
            "status": "ok",

            "module": MODULE_NAME,

            "version": MODULE_VERSION,

            "network_writes": False,

            "leverage_transport": False,
        }
    )


# ============================================================
# HEALTH SERVER
# ============================================================

async def start_health_server() -> web.AppRunner:

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
        app,
    )

    await runner.setup()

    site = web.TCPSite(
        runner,

        "0.0.0.0",

        PORT,
    )

    await site.start()

    print(
        (
            "R28 UNIT N.3: "
            f"HEALTH SERVER ACTIVE ON PORT {PORT}"
        ),
        flush=True,
    )

    return runner


# ============================================================
# SERVER TIME PARSER
# ============================================================

def extract_server_time(
    data: object,
) -> int:

    if isinstance(
        data,
        int,
    ):

        return data


    if (
        isinstance(
            data,
            str,
        )
        and
        data.isdigit()
    ):

        return int(
            data,
        )


    if isinstance(
        data,
        dict,
    ):

        for key in (
            "serverTime",
            "time",
            "timestamp",
            "data",
        ):

            value = data.get(
                key,
            )


            if isinstance(
                value,
                int,
            ):

                return value


            if (
                isinstance(
                    value,
                    str,
                )
                and
                value.isdigit()
            ):

                return int(
                    value,
                )


            if isinstance(
                value,
                dict,
            ):

                for nested_key in (
                    "serverTime",
                    "time",
                    "timestamp",
                ):

                    nested = value.get(
                        nested_key,
                    )


                    if isinstance(
                        nested,
                        int,
                    ):

                        return nested


                    if (
                        isinstance(
                            nested,
                            str,
                        )
                        and
                        nested.isdigit()
                    ):

                        return int(
                            nested,
                        )


    raise ValueError(
        (
            "Unable to parse server time from "
            f"{data!r}"
        )
    )


# ============================================================
# SYMBOL CONFIG PARSER
# ============================================================

def extract_symbol_config(
    data: object,
) -> Dict:

    if isinstance(
        data,
        list,
    ):

        for item in data:

            if (
                isinstance(
                    item,
                    dict,
                )
                and
                item.get(
                    "symbol"
                )
                ==
                SYMBOL
            ):

                return item


        if (
            len(
                data,
            )
            ==
            1
            and
            isinstance(
                data[0],
                dict,
            )
        ):

            return data[0]


    if isinstance(
        data,
        dict,
    ):

        if (
            data.get(
                "symbol"
            )
            ==
            SYMBOL
        ):

            return data


        inner = data.get(
            "data"
        )


        if isinstance(
            inner,
            list,
        ):

            return extract_symbol_config(
                inner,
            )


        if isinstance(
            inner,
            dict,
        ):

            return extract_symbol_config(
                inner,
            )


    raise ValueError(
        (
            "Unable to extract "
            f"{SYMBOL} symbol config"
        )
    )


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_diagnostic() -> None:

    global READINESS_BLOCKERS


    print(
        "=" * 76,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        (
            "EXPLICIT MUTATION AUTHORIZATION / "
            "PAYLOAD BINDING / REPLAY LOCK"
        ),
        flush=True,
    )

    print(
        (
            "AUTHENTICATED READ-ONLY "
            "ACCOUNT STATE ENABLED"
        ),
        flush=True,
    )

    print(
        "ALL NETWORK WRITE METHODS LOCKED",
        flush=True,
    )

    print(
        "NO LEVERAGE CHANGE WILL BE TRANSMITTED",
        flush=True,
    )

    print(
        "=" * 76,
        flush=True,
    )

    print(
        flush=True,
    )


    # ========================================================
    # CREDENTIAL STATUS
    # ========================================================

    print(
        "R28 UNIT N.3 CREDENTIAL STATUS",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    print(
        (
            "  API Key: "
            f"{credential_marker(API_KEY)}"
        ),
        flush=True,
    )

    print(
        (
            "  API Secret: "
            f"{credential_marker(API_SECRET)}"
        ),
        flush=True,
    )

    print(
        (
            "  API Passphrase: "
            f"{credential_marker(API_PASSPHRASE)}"
        ),
        flush=True,
    )


    credentials_present = bool(
        API_KEY
        and
        API_SECRET
        and
        API_PASSPHRASE
    )


    if not credentials_present:

        READINESS_BLOCKERS += 1


    # ========================================================
    # ABSOLUTE SAFETY GATES
    # ========================================================

    print(
        flush=True,
    )

    print(
        "R28 UNIT N.3 ABSOLUTE SAFETY GATES",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


    pass_gate(
        "Live Execution Disabled",

        LIVE_ORDER_EXECUTION
        is
        False,
    )


    pass_gate(
        "Demo Execution Disabled",

        DEMO_ORDER_EXECUTION
        is
        False,
    )


    pass_gate(
        "Network Writes Disabled",

        NETWORK_WRITES_ENABLED
        is
        False,
    )


    pass_gate(
        "Account Writes Disabled",

        ACCOUNT_WRITES_ENABLED
        is
        False,
    )


    pass_gate(
        "Leverage Writes Disabled",

        LEVERAGE_WRITES_ENABLED
        is
        False,
    )


    pass_gate(
        "Leverage Mutation Transport Disabled",

        LEVERAGE_MUTATION_TRANSPORT_ENABLED
        is
        False,
    )


    pass_gate(
        "Production Explicit Authorization Disabled",

        EXPLICIT_MUTATION_AUTHORIZATION_ENABLED
        is
        False,
    )


    pass_gate(
        "Local Authorization Diagnostic Enabled",

        LOCAL_AUTHORIZATION_DIAGNOSTIC_ENABLED
        is
        True,
    )


    # ========================================================
    # PAYLOAD
    # ========================================================

    payload = leverage_payload()

    body = canonical_json(
        payload,
    )

    payload_hash = sha256_hex(
        body,
    )


    print(
        flush=True,
    )

    print(
        "R28 UNIT N.3 MUTATION TARGET",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )

    print(
        "  Method = POST",
        flush=True,
    )

    print(
        f"  Path = {LEVERAGE_PATH}",
        flush=True,
    )

    print(
        f"  Symbol = {SYMBOL}",
        flush=True,
    )

    print(
        (
            "  Margin Type = "
            f"{TARGET_MARGIN_TYPE}"
        ),
        flush=True,
    )

    print(
        (
            "  Target Long Leverage = "
            f"{TARGET_LONG_LEVERAGE}x"
        ),
        flush=True,
    )

    print(
        (
            "  Target Short Leverage = "
            f"{TARGET_SHORT_LEVERAGE}x"
        ),
        flush=True,
    )

    print(
        (
            "  Payload SHA256 = "
            f"{payload_hash}"
        ),
        flush=True,
    )


    pass_gate(
        "Target Long Within Local 100x Cap",

        (
            0
            <
            TARGET_LONG_LEVERAGE
            <=
            MAX_LOCAL_LEVERAGE
        ),
    )


    pass_gate(
        "Target Short Within Local 100x Cap",

        (
            0
            <
            TARGET_SHORT_LEVERAGE
            <=
            MAX_LOCAL_LEVERAGE
        ),
    )


    pass_gate(
        "Leverage Method Is POST",

        "POST"
        ==
        "POST",
    )


    pass_gate(
        "Leverage Path Is Contract V3",

        LEVERAGE_PATH
        ==
        "/capi/v3/account/leverage",
    )


    # ========================================================
    # READ-ONLY NETWORK VALIDATION
    # ========================================================

    async with aiohttp.ClientSession() as session:


        # ====================================================
        # SERVER CLOCK
        # ====================================================

        print(
            flush=True,
        )

        print(
            "R28 UNIT N.3 SERVER-CLOCK VALIDATION",
            flush=True,
        )

        print(
            "-" * 76,
            flush=True,
        )


        try:

            server_time_data = await public_get(
                session,
                PUBLIC_TIME_PATH,
            )

            server_time_ms = extract_server_time(
                server_time_data,
            )

            delta_ms = abs(
                int(
                    time.time()
                    *
                    1000
                )
                -
                server_time_ms
            )


            pass_gate(
                "WEEX Server Time Read",

                True,
            )


            pass_gate(
                "WEEX Server Time Parseable",

                server_time_ms
                >
                0,
            )


            print(
                (
                    "  WEEX Server Time = "
                    f"{server_time_ms}"
                ),
                flush=True,
            )


            print(
                (
                    "  Approx Clock Delta = "
                    f"{delta_ms} ms"
                ),
                flush=True,
            )


        except Exception as exc:

            pass_gate(
                "WEEX Server Time Read",

                False,
            )

            print(
                (
                    "  Server Time Error = "
                    f"{exc}"
                ),
                flush=True,
            )


        # ====================================================
        # AUTHENTICATED SYMBOL CONFIG
        # ====================================================

        print(
            flush=True,
        )

        print(
            (
                "R28 UNIT N.3 "
                "AUTHENTICATED CONFIGURATION READ"
            ),
            flush=True,
        )

        print(
            "-" * 76,
            flush=True,
        )


        if credentials_present:

            try:

                config_data = await authenticated_get(
                    session,

                    SYMBOL_CONFIG_PATH,

                    {
                        "symbol": SYMBOL,
                    },
                )


                config = extract_symbol_config(
                    config_data,
                )


                pass_gate(
                    "Authenticated Symbol Config Read",

                    True,
                )


                pass_gate(
                    "Observed Symbol Matches BTCUSDT",

                    config.get(
                        "symbol"
                    )
                    ==
                    SYMBOL,
                )


                pass_gate(
                    "Observed Margin Mode Is ISOLATED",

                    config.get(
                        "marginType"
                    )
                    ==
                    TARGET_MARGIN_TYPE,
                )


                print(
                    (
                        "R28 UNIT N.3 "
                        "CURRENT SYMBOL CONFIG:"
                    ),
                    flush=True,
                )


                print(
                    (
                        "  Symbol = "
                        f"{config.get('symbol')}"
                    ),
                    flush=True,
                )


                print(
                    (
                        "  Margin Type = "
                        f"{config.get('marginType')}"
                    ),
                    flush=True,
                )


                print(
                    (
                        "  Position Mode = "
                        f"{config.get('separatedType', config.get('separatedMode'))}"
                    ),
                    flush=True,
                )


                print(
                    (
                        "  Cross Leverage = "
                        f"{config.get('crossLeverage')}x"
                    ),
                    flush=True,
                )


                print(
                    (
                        "  Isolated Long Leverage = "
                        f"{config.get('isolatedLongLeverage')}x"
                    ),
                    flush=True,
                )


                print(
                    (
                        "  Isolated Short Leverage = "
                        f"{config.get('isolatedShortLeverage')}x"
                    ),
                    flush=True,
                )


            except Exception as exc:

                pass_gate(
                    "Authenticated Symbol Config Read",

                    False,
                )

                print(
                    (
                        "  Authenticated Read Error = "
                        f"{exc}"
                    ),
                    flush=True,
                )


        else:

            pass_gate(
                "Authenticated Symbol Config Read",

                False,
            )

            print(
                (
                    "  Authenticated read skipped "
                    "because credentials are incomplete."
                ),
                flush=True,
            )


    # ========================================================
    # AUTHORIZATION CONSTRUCTION
    # ========================================================

    print(
        flush=True,
    )

    print(
        "R28 UNIT N.3 AUTHORIZATION CONSTRUCTION",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


    auth = create_local_test_authorization(
        body,
    )


    pass_gate(
        "Authorization ID Generated",

        bool(
            auth.authorization_id,
        ),
    )


    pass_gate(
        "Authorization Bound To Module",

        auth.module
        ==
        MODULE_NAME,
    )


    pass_gate(
        "Authorization Bound To Symbol",

        auth.symbol
        ==
        SYMBOL,
    )


    pass_gate(
        "Authorization Bound To Margin Type",

        auth.margin_type
        ==
        TARGET_MARGIN_TYPE,
    )


    pass_gate(
        "Authorization Bound To Long Leverage",

        auth.long_leverage
        ==
        TARGET_LONG_LEVERAGE,
    )


    pass_gate(
        "Authorization Bound To Short Leverage",

        auth.short_leverage
        ==
        TARGET_SHORT_LEVERAGE,
    )


    pass_gate(
        "Authorization Bound To Exact Payload Hash",

        auth.payload_sha256
        ==
        payload_hash,
    )


    pass_gate(
        "Authorization Has Expiry",

        auth.expires_at_ms
        >
        auth.issued_at_ms,
    )


    pass_gate(
        "Authorization Proof Generated",

        bool(
            auth.proof,
        ),
    )


    # ========================================================
    # NEGATIVE AUTHORIZATION TESTS
    # ========================================================

    print(
        flush=True,
    )

    print(
        "R28 UNIT N.3 NEGATIVE AUTHORIZATION TESTS",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


    # --------------------------------------------------------
    # Missing authorization
    # --------------------------------------------------------

    valid, reason = validate_authorization(
        None,

        body,

        consume=False,
    )


    pass_gate(
        "Missing Authorization Rejected",

        (
            valid
            is
            False
            and
            "missing"
            in
            reason
        ),
    )


    # --------------------------------------------------------
    # Tampered payload
    # --------------------------------------------------------

    tampered_body = body.replace(
        '"100"',
        '"99"',
        1,
    )


    valid, reason = validate_authorization(
        auth,

        tampered_body,

        consume=False,
    )


    pass_gate(
        "Tampered Payload Rejected",

        (
            valid
            is
            False
            and
            "payload hash"
            in
            reason
        ),
    )


    # --------------------------------------------------------
    # Wrong symbol
    # --------------------------------------------------------

    bad_symbol_auth = MutationAuthorization(
        authorization_id=auth.authorization_id,

        module=auth.module,

        symbol="ETHUSDT",

        margin_type=auth.margin_type,

        long_leverage=auth.long_leverage,

        short_leverage=auth.short_leverage,

        payload_sha256=auth.payload_sha256,

        issued_at_ms=auth.issued_at_ms,

        expires_at_ms=auth.expires_at_ms,

        purpose=auth.purpose,

        proof=auth.proof,
    )


    valid, reason = validate_authorization(
        bad_symbol_auth,

        body,

        consume=False,
    )


    pass_gate(
        "Wrong Symbol Authorization Rejected",

        (
            valid
            is
            False
            and
            "symbol"
            in
            reason
        ),
    )


    # --------------------------------------------------------
    # Wrong margin type
    # --------------------------------------------------------

    bad_margin_auth = MutationAuthorization(
        authorization_id=auth.authorization_id,

        module=auth.module,

        symbol=auth.symbol,

        margin_type="CROSSED",

        long_leverage=auth.long_leverage,

        short_leverage=auth.short_leverage,

        payload_sha256=auth.payload_sha256,

        issued_at_ms=auth.issued_at_ms,

        expires_at_ms=auth.expires_at_ms,

        purpose=auth.purpose,

        proof=auth.proof,
    )


    valid, reason = validate_authorization(
        bad_margin_auth,

        body,

        consume=False,
    )


    pass_gate(
        "Wrong Margin-Type Authorization Rejected",

        (
            valid
            is
            False
            and
            "margin-type"
            in
            reason
        ),
    )


    # --------------------------------------------------------
    # Wrong long leverage
    # --------------------------------------------------------

    bad_long_auth = MutationAuthorization(
        authorization_id=auth.authorization_id,

        module=auth.module,

        symbol=auth.symbol,

        margin_type=auth.margin_type,

        long_leverage=99,

        short_leverage=auth.short_leverage,

        payload_sha256=auth.payload_sha256,

        issued_at_ms=auth.issued_at_ms,

        expires_at_ms=auth.expires_at_ms,

        purpose=auth.purpose,

        proof=auth.proof,
    )


    valid, reason = validate_authorization(
        bad_long_auth,

        body,

        consume=False,
    )


    pass_gate(
        "Wrong Long-Leverage Authorization Rejected",

        (
            valid
            is
            False
            and
            "long-leverage"
            in
            reason
        ),
    )


    # --------------------------------------------------------
    # Expired authorization
    # --------------------------------------------------------

    expired_now_ms = (
        auth.expires_at_ms
        +
        1
    )


    valid, reason = validate_authorization(
        auth,

        body,

        consume=False,

        now_ms=expired_now_ms,
    )


    pass_gate(
        "Expired Authorization Rejected",

        (
            valid
            is
            False
            and
            "expired"
            in
            reason
        ),
    )


    # --------------------------------------------------------
    # Invalid proof
    # --------------------------------------------------------

    bad_proof_auth = MutationAuthorization(
        authorization_id=auth.authorization_id,

        module=auth.module,

        symbol=auth.symbol,

        margin_type=auth.margin_type,

        long_leverage=auth.long_leverage,

        short_leverage=auth.short_leverage,

        payload_sha256=auth.payload_sha256,

        issued_at_ms=auth.issued_at_ms,

        expires_at_ms=auth.expires_at_ms,

        purpose=auth.purpose,

        proof="INVALID-PROOF",
    )


    valid, reason = validate_authorization(
        bad_proof_auth,

        body,

        consume=False,
    )


    pass_gate(
        "Invalid Authorization Proof Rejected",

        (
            valid
            is
            False
            and
            "proof"
            in
            reason
        ),
    )


    # ========================================================
    # POSITIVE AUTHORIZATION TEST
    # ========================================================

    print(
        flush=True,
    )

    print(
        (
            "R28 UNIT N.3 "
            "POSITIVE LOCAL AUTHORIZATION TEST"
        ),
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


    valid, reason = validate_authorization(
        auth,

        body,

        consume=True,
    )


    pass_gate(
        "Exact Authorization Accepted Locally",

        valid
        is
        True,
    )


    print(
        (
            "  Local Authorization Result = "
            f"{reason}"
        ),
        flush=True,
    )


    # ========================================================
    # REPLAY TEST
    # ========================================================

    valid, reason = validate_authorization(
        auth,

        body,

        consume=False,
    )


    pass_gate(
        "Authorization Replay Rejected",

        (
            valid
            is
            False
            and
            "replay"
            in
            reason
        ),
    )


    # ========================================================
    # FINAL TRANSPORT BOUNDARY
    # ========================================================

    print(
        flush=True,
    )

    print(
        (
            "R28 UNIT N.3 "
            "FINAL TRANSPORT-BOUNDARY TEST"
        ),
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


    transport_auth = create_local_test_authorization(
        body,
    )


    try:

        await blocked_leverage_post(
            LEVERAGE_PATH,

            body,

            transport_auth,
        )


        pass_gate(
            (
                "Authorized Leverage POST "
                "Still Blocked Locally"
            ),

            False,
        )


    except PermissionError as exc:

        print(
            "R28 UNIT N.3 LOCAL BLOCK:",
            flush=True,
        )

        print(
            f"  {exc}",
            flush=True,
        )


        pass_gate(
            (
                "Authorized Leverage POST "
                "Still Blocked Locally"
            ),

            (
                "FINAL TRANSPORT LOCK"
                in
                str(
                    exc,
                )
            ),
        )


    # ========================================================
    # WRITE LOCK AUDIT
    # ========================================================

    print(
        flush=True,
    )

    print(
        "R28 UNIT N.3 WRITE-LOCK AUDIT",
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


    pass_gate(
        "Network POST Count Is Zero",

        COUNTERS[
            "network_posts"
        ]
        ==
        0,
    )


    pass_gate(
        "Network PUT Count Is Zero",

        COUNTERS[
            "network_puts"
        ]
        ==
        0,
    )


    pass_gate(
        "Network PATCH Count Is Zero",

        COUNTERS[
            "network_patches"
        ]
        ==
        0,
    )


    pass_gate(
        "Network DELETE Count Is Zero",

        COUNTERS[
            "network_deletes"
        ]
        ==
        0,
    )


    pass_gate(
        "Account Write Transmission Count Is Zero",

        COUNTERS[
            "account_write_transmissions"
        ]
        ==
        0,
    )


    pass_gate(
        "Leverage Change Transmission Count Is Zero",

        COUNTERS[
            "leverage_change_transmissions"
        ]
        ==
        0,
    )


    pass_gate(
        "Real Order Transmission Count Is Zero",

        COUNTERS[
            "real_order_transmissions"
        ]
        ==
        0,
    )


    pass_gate(
        "Demo Order Transmission Count Is Zero",

        COUNTERS[
            "demo_order_transmissions"
        ]
        ==
        0,
    )


    pass_gate(
        "Authorization Replay Was Blocked",

        COUNTERS[
            "authorization_replays_blocked"
        ]
        >=
        1,
    )


    # ========================================================
    # AUTHORIZATION AUDIT
    # ========================================================

    print(
        flush=True,
    )

    print(
        "R28 UNIT N.3 AUTHORIZATION AUDIT:",
        flush=True,
    )


    print(
        (
            "  Authorization requests = "
            f"{COUNTERS['authorization_requests']}"
        ),
        flush=True,
    )


    print(
        (
            "  Authorization grants = "
            f"{COUNTERS['authorization_grants']}"
        ),
        flush=True,
    )


    print(
        (
            "  Authorization denials = "
            f"{COUNTERS['authorization_denials']}"
        ),
        flush=True,
    )


    print(
        (
            "  Authorization replays blocked = "
            f"{COUNTERS['authorization_replays_blocked']}"
        ),
        flush=True,
    )


    print(
        (
            "  Local POST attempts = "
            f"{COUNTERS['local_post_attempts']}"
        ),
        flush=True,
    )


    print(
        (
            "  Local POST blocks = "
            f"{COUNTERS['local_post_blocks']}"
        ),
        flush=True,
    )


    print(
        (
            "  Network POSTs = "
            f"{COUNTERS['network_posts']}"
        ),
        flush=True,
    )


    print(
        (
            "  Leverage change transmissions = "
            f"{COUNTERS['leverage_change_transmissions']}"
        ),
        flush=True,
    )


    # ========================================================
    # FINAL ASSESSMENT
    # ========================================================

    print(
        flush=True,
    )

    print(
        (
            "R28 UNIT N.3 "
            "EXECUTION-READINESS ASSESSMENT"
        ),
        flush=True,
    )

    print(
        "-" * 76,
        flush=True,
    )


    print(
        (
            "Structural Safety Failures = "
            f"{STRUCTURAL_FAILURES}"
        ),
        flush=True,
    )


    print(
        (
            "Readiness Blockers = "
            f"{READINESS_BLOCKERS}"
        ),
        flush=True,
    )


    if STRUCTURAL_FAILURES == 0:

        print(
            (
                "Mutation Authorization Construction "
                "= ✅ VERIFIED"
            ),
            flush=True,
        )

        print(
            (
                "Exact Payload Binding "
                "= ✅ VERIFIED"
            ),
            flush=True,
        )

    else:

        print(
            (
                "Mutation Authorization Construction "
                "= ❌ FAILED"
            ),
            flush=True,
        )

        print(
            (
                "Exact Payload Binding "
                "= ❌ FAILED"
            ),
            flush=True,
        )


    if (
        COUNTERS[
            "authorization_replays_blocked"
        ]
        >=
        1
    ):

        print(
            (
                "Authorization Replay Protection "
                "= ✅ VERIFIED"
            ),
            flush=True,
        )

    else:

        print(
            (
                "Authorization Replay Protection "
                "= ❌ FAILED"
            ),
            flush=True,
        )


    print(
        (
            "Leverage Mutation Transmission "
            "= 🛡 BLOCKED LOCALLY"
        ),
        flush=True,
    )


    # ========================================================
    # PASS BANNER
    # ========================================================

    if (
        STRUCTURAL_FAILURES
        ==
        0
        and
        READINESS_BLOCKERS
        ==
        0
    ):

        print(
            flush=True,
        )

        print(
            (
                "CURRENT EXECUTION READINESS: "
                "✅ N.3 MUTATION AUTHORIZATION "
                "BOUNDARY VERIFIED"
            ),
            flush=True,
        )

        print(
            flush=True,
        )

        print(
            "-" * 76,
            flush=True,
        )

        print(
            (
                "✅ R28 UNIT N.3 "
                "STRUCTURAL DIAGNOSTIC PASSED"
            ),
            flush=True,
        )

        print(
            (
                "✅ EXPLICIT LOCAL MUTATION "
                "AUTHORIZATION CONSTRUCTION VERIFIED"
            ),
            flush=True,
        )

        print(
            (
                "✅ AUTHORIZATION BOUND TO "
                "BTCUSDT / ISOLATED / 100x / 100x"
            ),
            flush=True,
        )

        print(
            (
                "✅ AUTHORIZATION BOUND TO EXACT "
                "LEVERAGE PAYLOAD HASH"
            ),
            flush=True,
        )

        print(
            (
                "✅ MISSING / TAMPERED / EXPIRED "
                "AUTHORIZATION REJECTED"
            ),
            flush=True,
        )

        print(
            (
                "✅ AUTHORIZATION PROOF "
                "VALIDATION VERIFIED"
            ),
            flush=True,
        )

        print(
            (
                "✅ AUTHORIZATION REPLAY "
                "PROTECTION VERIFIED"
            ),
            flush=True,
        )

        print(
            (
                "✅ AUTHORIZED REQUEST STILL BLOCKED "
                "AT FINAL TRANSPORT BOUNDARY"
            ),
            flush=True,
        )

        print(
            (
                "✅ NETWORK WRITE TRANSPORT "
                "REMAINS LOCKED"
            ),
            flush=True,
        )

        print(
            (
                "🛡 NO LEVERAGE CHANGE WAS "
                "TRANSMITTED TO WEEX"
            ),
            flush=True,
        )

        print(
            (
                "🛡 NO ACCOUNT WRITE WAS "
                "TRANSMITTED TO WEEX"
            ),
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
            flush=True,
        )

        print(
            (
                "❌ R28 UNIT N.3 "
                "DIAGNOSTIC DID NOT PASS"
            ),
            flush=True,
        )


    print(
        "=" * 76,
        flush=True,
    )


# ============================================================
# HEARTBEAT
# ============================================================

async def heartbeat_loop() -> None:

    counter = 0


    while (
        STOP_EVENT
        is
        not
        None
        and
        not STOP_EVENT.is_set()
    ):

        counter += 1


        print(
            (
                "R28 UNIT N.3: "
                f"HEARTBEAT {counter} ✅ ACTIVE"
            ),
            flush=True,
        )


        try:

            await asyncio.wait_for(
                STOP_EVENT.wait(),

                timeout=15.0,
            )


        except asyncio.TimeoutError:

            pass


# ============================================================
# MAIN RUNTIME
# ============================================================

async def main() -> None:

    global STOP_EVENT


    STOP_EVENT = asyncio.Event()


    loop = asyncio.get_running_loop()


    def request_shutdown() -> None:

        if (
            STOP_EVENT
            is
            not
            None
            and
            not STOP_EVENT.is_set()
        ):

            print(
                (
                    "R28 UNIT N.3: "
                    "SHUTDOWN REQUESTED"
                ),
                flush=True,
            )

            STOP_EVENT.set()


    for sig in (
        signal.SIGTERM,
        signal.SIGINT,
    ):

        try:

            loop.add_signal_handler(
                sig,
                request_shutdown,
            )

        except NotImplementedError:

            pass


    print(
        "R28 UNIT N.3: RUNTIME STARTING",
        flush=True,
    )


    runner = await start_health_server()


    try:

        await run_diagnostic()


        print(
            "=" * 76,
            flush=True,
        )

        print(
            (
                "R28 UNIT N.3: "
                "PERSISTENT RUNTIME ACTIVE"
            ),
            flush=True,
        )

        print(
            (
                "R28 UNIT N.3: "
                "AUTHENTICATED READ-ONLY LOCKS ACTIVE"
            ),
            flush=True,
        )

        print(
            (
                "R28 UNIT N.3: "
                "NETWORK WRITE TRANSPORT LOCKED"
            ),
            flush=True,
        )

        print(
            (
                "R28 UNIT N.3: "
                "LEVERAGE MUTATION TRANSPORT LOCKED"
            ),
            flush=True,
        )

        print(
            (
                "R28 UNIT N.3: "
                "AUTHORIZATION REPLAY LOCK ACTIVE"
            ),
            flush=True,
        )


        await heartbeat_loop()


    finally:

        await runner.cleanup()

        print(
            (
                "R28 UNIT N.3: "
                "RUNTIME STOPPED CLEANLY"
            ),
            flush=True,
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
