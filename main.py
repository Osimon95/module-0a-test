# ============================================================
# 0F-4H-R28-UNIT-N.3
# EXPLICIT MUTATION AUTHORIZATION / PAYLOAD BINDING / REPLAY LOCK
#
# CORRECTED VERSION
#
# IMPORTANT SAFETY DESIGN
# ------------------------------------------------------------
# - PUBLIC GET ALLOWED
# - AUTHENTICATED READ-ONLY GET ALLOWED
# - REAL ORDER EXECUTION DISABLED
# - DEMO ORDER EXECUTION DISABLED
# - ACCOUNT WRITES DISABLED
# - LEVERAGE WRITES DISABLED
# - ALL NETWORK POST/PUT/PATCH/DELETE DISABLED
# - NO LEVERAGE CHANGE CAN BE TRANSMITTED
#
# CORRECTION:
# Replay test authorization and final transport-boundary
# authorization are now DIFFERENT authorization objects.
# ============================================================


print(
    "R28 UNIT N.3: MAIN.PY ENTERED",
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
import secrets
import signal
import sys
import time

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Set
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


print(
    "R28 UNIT N.3: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-N.3"
MODULE_VERSION = "R28-N.3-CORRECTED"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

LOCAL_MAX_LEVERAGE = 100

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

SERVER_TIME_PATH = "/capi/v3/market/time"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

LEVERAGE_PATH = "/capi/v3/account/leverage"

LEVERAGE_METHOD = "POST"

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

REQUEST_TIMEOUT_SECONDS = 15

AUTHORIZATION_TTL_SECONDS = 30


print(
    "R28 UNIT N.3: CONSTANTS INITIALIZED",
    flush=True,
)


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

ACCOUNT_WRITES_ENABLED = False

LEVERAGE_WRITES_ENABLED = False

LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

PRODUCTION_EXPLICIT_AUTHORIZATION_ENABLED = False

LOCAL_AUTHORIZATION_DIAGNOSTIC_ENABLED = True


# ============================================================
# CREDENTIALS
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


# ============================================================
# AUDIT COUNTERS
# ============================================================

AUDIT = {
    "authorization_requests": 0,
    "authorization_grants": 0,
    "authorization_denials": 0,
    "authorization_replays_blocked": 0,

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
# DIAGNOSTIC STATE
# ============================================================

STRUCTURAL_FAILURES = 0

READINESS_BLOCKERS = 0

AUTHORIZATION_CONSTRUCTION_VERIFIED = False

PAYLOAD_BINDING_VERIFIED = False

REPLAY_PROTECTION_VERIFIED = False

TRANSPORT_LOCK_VERIFIED = False


# ============================================================
# AUTHORIZATION REPLAY STORE
# ============================================================

CONSUMED_AUTHORIZATION_IDS: Set[str] = set()


# ============================================================
# OUTPUT HELPERS
# ============================================================

LINE = "-" * 76

DOUBLE_LINE = "=" * 76


def section(title: str) -> None:

    print(
        "",
        flush=True,
    )

    print(
        title,
        flush=True,
    )

    print(
        LINE,
        flush=True,
    )


def result(
    label: str,
    passed: bool,
) -> bool:

    global STRUCTURAL_FAILURES

    icon = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<72} {icon}",
        flush=True,
    )

    if not passed:
        STRUCTURAL_FAILURES += 1

    return passed


def informational_result(
    label: str,
    passed: bool,
) -> bool:

    icon = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<72} {icon}",
        flush=True,
    )

    return passed


# ============================================================
# CANONICAL JSON
# ============================================================

def canonical_json(
    value: Dict[str, Any],
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


# ============================================================
# SHA256
# ============================================================

def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8"),
    ).hexdigest()


# ============================================================
# MUTATION PAYLOAD
# ============================================================

def build_leverage_payload() -> Dict[str, Any]:

    return {
        "symbol": SYMBOL,
        "marginType": TARGET_MARGIN_TYPE,
        "longLeverage": str(TARGET_LONG_LEVERAGE),
        "shortLeverage": str(TARGET_SHORT_LEVERAGE),
    }


MUTATION_PAYLOAD = build_leverage_payload()

MUTATION_PAYLOAD_JSON = canonical_json(
    MUTATION_PAYLOAD,
)

MUTATION_PAYLOAD_HASH = sha256_text(
    MUTATION_PAYLOAD_JSON,
)


# ============================================================
# LOCAL AUTHORIZATION SECRET
# ============================================================

LOCAL_AUTHORIZATION_SECRET = secrets.token_bytes(
    32,
)


# ============================================================
# AUTHORIZATION RECORD
# ============================================================

@dataclass(frozen=True)
class MutationAuthorization:

    authorization_id: str

    module_name: str

    method: str

    path: str

    symbol: str

    margin_type: str

    long_leverage: int

    short_leverage: int

    payload_hash: str

    issued_at_ms: int

    expires_at_ms: int

    proof: str


# ============================================================
# AUTHORIZATION PROOF MATERIAL
# ============================================================

def authorization_material(
    authorization_id: str,
    module_name: str,
    method: str,
    path: str,
    symbol: str,
    margin_type: str,
    long_leverage: int,
    short_leverage: int,
    payload_hash: str,
    issued_at_ms: int,
    expires_at_ms: int,
) -> str:

    material = {
        "authorizationId": authorization_id,
        "moduleName": module_name,
        "method": method,
        "path": path,
        "symbol": symbol,
        "marginType": margin_type,
        "longLeverage": long_leverage,
        "shortLeverage": short_leverage,
        "payloadHash": payload_hash,
        "issuedAtMs": issued_at_ms,
        "expiresAtMs": expires_at_ms,
    }

    return canonical_json(
        material,
    )


def generate_authorization_proof(
    material: str,
) -> str:

    return hmac.new(
        LOCAL_AUTHORIZATION_SECRET,
        material.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# ============================================================
# CREATE LOCAL AUTHORIZATION
# ============================================================

def create_mutation_authorization(
    payload: Dict[str, Any],
    *,
    ttl_seconds: int = AUTHORIZATION_TTL_SECONDS,
    override_symbol: Optional[str] = None,
    override_margin_type: Optional[str] = None,
    override_long_leverage: Optional[int] = None,
    override_short_leverage: Optional[int] = None,
) -> MutationAuthorization:

    payload_hash = sha256_text(
        canonical_json(payload),
    )

    issued_at_ms = int(
        time.time() * 1000
    )

    expires_at_ms = (
        issued_at_ms
        + ttl_seconds * 1000
    )

    authorization_id = secrets.token_hex(
        16,
    )

    symbol = (
        override_symbol
        if override_symbol is not None
        else SYMBOL
    )

    margin_type = (
        override_margin_type
        if override_margin_type is not None
        else TARGET_MARGIN_TYPE
    )

    long_leverage = (
        override_long_leverage
        if override_long_leverage is not None
        else TARGET_LONG_LEVERAGE
    )

    short_leverage = (
        override_short_leverage
        if override_short_leverage is not None
        else TARGET_SHORT_LEVERAGE
    )

    material = authorization_material(
        authorization_id=authorization_id,
        module_name=MODULE_NAME,
        method=LEVERAGE_METHOD,
        path=LEVERAGE_PATH,
        symbol=symbol,
        margin_type=margin_type,
        long_leverage=long_leverage,
        short_leverage=short_leverage,
        payload_hash=payload_hash,
        issued_at_ms=issued_at_ms,
        expires_at_ms=expires_at_ms,
    )

    proof = generate_authorization_proof(
        material,
    )

    return MutationAuthorization(
        authorization_id=authorization_id,
        module_name=MODULE_NAME,
        method=LEVERAGE_METHOD,
        path=LEVERAGE_PATH,
        symbol=symbol,
        margin_type=margin_type,
        long_leverage=long_leverage,
        short_leverage=short_leverage,
        payload_hash=payload_hash,
        issued_at_ms=issued_at_ms,
        expires_at_ms=expires_at_ms,
        proof=proof,
    )


# ============================================================
# AUTHORIZATION VALIDATION
# ============================================================

class AuthorizationError(Exception):
    pass


class AuthorizationReplayError(
    AuthorizationError
):
    pass


def validate_mutation_authorization(
    payload: Dict[str, Any],
    authorization: Optional[MutationAuthorization],
    *,
    consume: bool,
) -> str:

    AUDIT["authorization_requests"] += 1

    try:

        if authorization is None:

            raise AuthorizationError(
                "missing authorization"
            )

        if (
            authorization.authorization_id
            in CONSUMED_AUTHORIZATION_IDS
        ):

            AUDIT[
                "authorization_replays_blocked"
            ] += 1

            raise AuthorizationReplayError(
                "authorization replay blocked"
            )

        now_ms = int(
            time.time() * 1000
        )

        if (
            authorization.expires_at_ms
            <= now_ms
        ):

            raise AuthorizationError(
                "authorization expired"
            )

        if (
            authorization.module_name
            != MODULE_NAME
        ):

            raise AuthorizationError(
                "module binding mismatch"
            )

        if (
            authorization.method
            != LEVERAGE_METHOD
        ):

            raise AuthorizationError(
                "method binding mismatch"
            )

        if (
            authorization.path
            != LEVERAGE_PATH
        ):

            raise AuthorizationError(
                "path binding mismatch"
            )

        if (
            authorization.symbol
            != SYMBOL
        ):

            raise AuthorizationError(
                "symbol binding mismatch"
            )

        if (
            authorization.margin_type
            != TARGET_MARGIN_TYPE
        ):

            raise AuthorizationError(
                "margin-type binding mismatch"
            )

        if (
            authorization.long_leverage
            != TARGET_LONG_LEVERAGE
        ):

            raise AuthorizationError(
                "long-leverage binding mismatch"
            )

        if (
            authorization.short_leverage
            != TARGET_SHORT_LEVERAGE
        ):

            raise AuthorizationError(
                "short-leverage binding mismatch"
            )

        actual_payload_hash = sha256_text(
            canonical_json(payload),
        )

        if not hmac.compare_digest(
            authorization.payload_hash,
            actual_payload_hash,
        ):

            raise AuthorizationError(
                "payload hash mismatch"
            )

        material = authorization_material(
            authorization_id=authorization.authorization_id,
            module_name=authorization.module_name,
            method=authorization.method,
            path=authorization.path,
            symbol=authorization.symbol,
            margin_type=authorization.margin_type,
            long_leverage=authorization.long_leverage,
            short_leverage=authorization.short_leverage,
            payload_hash=authorization.payload_hash,
            issued_at_ms=authorization.issued_at_ms,
            expires_at_ms=authorization.expires_at_ms,
        )

        expected_proof = generate_authorization_proof(
            material,
        )

        if not hmac.compare_digest(
            authorization.proof,
            expected_proof,
        ):

            raise AuthorizationError(
                "invalid authorization proof"
            )

        if consume:

            CONSUMED_AUTHORIZATION_IDS.add(
                authorization.authorization_id,
            )

        AUDIT["authorization_grants"] += 1

        return "authorized locally"

    except AuthorizationError:

        AUDIT["authorization_denials"] += 1

        raise


# ============================================================
# WEEX AUTHENTICATION SIGNATURE
# ============================================================

def generate_weex_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    if query_string:

        message = (
            timestamp
            + method.upper()
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        message = (
            timestamp
            + method.upper()
            + request_path
            + body
        )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest,
    ).decode("utf-8")


def authenticated_headers(
    method: str,
    path: str,
    query_string: str = "",
) -> Dict[str, str]:

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_weex_signature(
        timestamp=timestamp,
        method=method,
        request_path=path,
        query_string=query_string,
        body="",
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }


# ============================================================
# NETWORK READ-ONLY CLIENT
# ============================================================

async def public_get(
    session: aiohttp.ClientSession,
    path: str,
) -> Any:

    print(
        f"R28 UNIT N.3: PUBLIC GET -> {path}",
        flush=True,
    )

    url = (
        WEEX_BASE_URL
        + path
    )

    async with session.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        text = await response.text()

        if response.status < 200 or response.status >= 300:

            raise RuntimeError(
                f"HTTP {response.status}: {text}"
            )

        try:

            return json.loads(
                text,
            )

        except json.JSONDecodeError:

            return text


async def authenticated_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, str]] = None,
) -> Any:

    if not API_KEY:
        raise RuntimeError(
            "WEEX_API_KEY missing"
        )

    if not API_SECRET:
        raise RuntimeError(
            "WEEX_API_SECRET missing"
        )

    if not API_PASSPHRASE:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing"
        )

    params = (
        params
        if params is not None
        else {}
    )

    query_string = urlencode(
        params,
    )

    display_path = path

    if query_string:

        display_path = (
            path
            + "?"
            + query_string
        )

    print(
        "R28 UNIT N.3: "
        f"AUTHENTICATED GET -> {display_path}",
        flush=True,
    )

    headers = authenticated_headers(
        method="GET",
        path=path,
        query_string=query_string,
    )

    url = (
        WEEX_BASE_URL
        + path
    )

    async with session.get(
        url,
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        text = await response.text()

        if response.status < 200 or response.status >= 300:

            raise RuntimeError(
                f"HTTP {response.status}: {text}"
            )

        try:

            return json.loads(
                text,
            )

        except json.JSONDecodeError:

            return text


# ============================================================
# ABSOLUTE NETWORK WRITE BLOCK
# ============================================================

class LocalTransportBlock(Exception):
    pass


async def attempt_authorized_leverage_post(
    payload: Dict[str, Any],
    authorization: MutationAuthorization,
) -> None:

    """
    FINAL N.3 TRANSPORT-BOUNDARY TEST.

    IMPORTANT ORDER:

    1. Fresh authorization must validate successfully.
    2. Authorization is consumed exactly once.
    3. Independent transport lock then blocks POST.
    4. No HTTP POST call exists below the lock.
    """

    AUDIT["local_post_attempts"] += 1

    authorization_result = validate_mutation_authorization(
        payload,
        authorization,
        consume=True,
    )

    if authorization_result != "authorized locally":

        raise AuthorizationError(
            "authorization did not succeed"
        )

    # --------------------------------------------------------
    # HARD WRITE TRANSPORT LOCK
    # --------------------------------------------------------

    if not NETWORK_WRITES_ENABLED:

        AUDIT["local_post_blocks"] += 1

        raise LocalTransportBlock(
            "R28 UNIT N.3 LOCAL TRANSPORT BLOCK: "
            "network write transport locked."
        )

    if not ACCOUNT_WRITES_ENABLED:

        AUDIT["local_post_blocks"] += 1

        raise LocalTransportBlock(
            "R28 UNIT N.3 LOCAL TRANSPORT BLOCK: "
            "account writes disabled."
        )

    if not LEVERAGE_WRITES_ENABLED:

        AUDIT["local_post_blocks"] += 1

        raise LocalTransportBlock(
            "R28 UNIT N.3 LOCAL TRANSPORT BLOCK: "
            "leverage writes disabled."
        )

    if not LEVERAGE_MUTATION_TRANSPORT_ENABLED:

        AUDIT["local_post_blocks"] += 1

        raise LocalTransportBlock(
            "R28 UNIT N.3 LOCAL TRANSPORT BLOCK: "
            "leverage mutation transport disabled."
        )

    # ========================================================
    # UNREACHABLE SAFETY SENTINEL
    # ========================================================
    #
    # THERE IS DELIBERATELY NO aiohttp.post() HERE.
    #
    # Even if a future edit accidentally changes one of the
    # boolean locks above, this unit still refuses to transmit.
    # ========================================================

    raise LocalTransportBlock(
        "R28 UNIT N.3 ABSOLUTE SAFETY BLOCK: "
        "network leverage POST implementation absent."
    )


# ============================================================
# SERVER-TIME PARSER
# ============================================================

def parse_server_time(
    response: Any,
) -> Optional[int]:

    if isinstance(
        response,
        int,
    ):

        return response

    if isinstance(
        response,
        str,
    ):

        stripped = response.strip()

        if stripped.isdigit():

            return int(
                stripped
            )

    if isinstance(
        response,
        dict,
    ):

        candidates = [
            response.get("serverTime"),
            response.get("time"),
            response.get("data"),
        ]

        for candidate in candidates:

            if isinstance(
                candidate,
                int,
            ):

                return candidate

            if (
                isinstance(
                    candidate,
                    str,
                )
                and candidate.isdigit()
            ):

                return int(
                    candidate
                )

            if isinstance(
                candidate,
                dict,
            ):

                nested = (
                    candidate.get("serverTime")
                    or candidate.get("time")
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
                    and nested.isdigit()
                ):

                    return int(
                        nested
                    )

    return None


# ============================================================
# SYMBOL-CONFIG PARSER
# ============================================================

def extract_symbol_config(
    response: Any,
) -> Optional[Dict[str, Any]]:

    data = response

    if isinstance(
        response,
        dict,
    ):

        if "data" in response:

            data = response.get(
                "data"
            )

    if isinstance(
        data,
        dict,
    ):

        if (
            str(
                data.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):

            return data

        return None

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

            if (
                str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ):

                return item

    return None


# ============================================================
# NEGATIVE AUTH TEST HELPER
# ============================================================

def expect_authorization_rejection(
    label: str,
    payload: Dict[str, Any],
    authorization: Optional[MutationAuthorization],
) -> bool:

    try:

        validate_mutation_authorization(
            payload,
            authorization,
            consume=False,
        )

    except AuthorizationError:

        informational_result(
            label,
            True,
        )

        return True

    informational_result(
        label,
        False,
    )

    return False


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_diagnostic() -> bool:

    global STRUCTURAL_FAILURES
    global READINESS_BLOCKERS

    global AUTHORIZATION_CONSTRUCTION_VERIFIED
    global PAYLOAD_BINDING_VERIFIED
    global REPLAY_PROTECTION_VERIFIED
    global TRANSPORT_LOCK_VERIFIED

    STRUCTURAL_FAILURES = 0
    READINESS_BLOCKERS = 0

    print(
        DOUBLE_LINE,
        flush=True,
    )

    print(
        "0F-4H-R28-UNIT-N.3 STARTING",
        flush=True,
    )

    print(
        "EXPLICIT MUTATION AUTHORIZATION / "
        "PAYLOAD BINDING / REPLAY LOCK",
        flush=True,
    )

    print(
        "AUTHENTICATED READ-ONLY ACCOUNT STATE ENABLED",
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
        DOUBLE_LINE,
        flush=True,
    )


    # ========================================================
    # CREDENTIAL STATUS
    # ========================================================

    section(
        "R28 UNIT N.3 CREDENTIAL STATUS"
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

    if not (
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    ):

        READINESS_BLOCKERS += 1


    # ========================================================
    # SAFETY GATES
    # ========================================================

    section(
        "R28 UNIT N.3 ABSOLUTE SAFETY GATES"
    )

    result(
        "Live Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )

    result(
        "Demo Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    result(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    result(
        "Account Writes Disabled",
        ACCOUNT_WRITES_ENABLED is False,
    )

    result(
        "Leverage Writes Disabled",
        LEVERAGE_WRITES_ENABLED is False,
    )

    result(
        "Leverage Mutation Transport Disabled",
        LEVERAGE_MUTATION_TRANSPORT_ENABLED is False,
    )

    result(
        "Production Explicit Authorization Disabled",
        PRODUCTION_EXPLICIT_AUTHORIZATION_ENABLED
        is False,
    )

    result(
        "Local Authorization Diagnostic Enabled",
        LOCAL_AUTHORIZATION_DIAGNOSTIC_ENABLED
        is True,
    )


    # ========================================================
    # MUTATION TARGET
    # ========================================================

    section(
        "R28 UNIT N.3 MUTATION TARGET"
    )

    print(
        f"  Method = {LEVERAGE_METHOD}",
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
        f"  Margin Type = {TARGET_MARGIN_TYPE}",
        flush=True,
    )

    print(
        "  Target Long Leverage = "
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        "  Target Short Leverage = "
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        "  Payload SHA256 = "
        f"{MUTATION_PAYLOAD_HASH}",
        flush=True,
    )

    result(
        "Target Long Within Local 100x Cap",
        (
            1
            <= TARGET_LONG_LEVERAGE
            <= LOCAL_MAX_LEVERAGE
        ),
    )

    result(
        "Target Short Within Local 100x Cap",
        (
            1
            <= TARGET_SHORT_LEVERAGE
            <= LOCAL_MAX_LEVERAGE
        ),
    )

    result(
        "Leverage Method Is POST",
        LEVERAGE_METHOD == "POST",
    )

    result(
        "Leverage Path Is Contract V3",
        LEVERAGE_PATH.startswith(
            "/capi/v3/"
        ),
    )


    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT_SECONDS,
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
    ) as session:


        # ====================================================
        # SERVER CLOCK
        # ====================================================

        section(
            "R28 UNIT N.3 SERVER-CLOCK VALIDATION"
        )

        try:

            server_response = await public_get(
                session,
                SERVER_TIME_PATH,
            )

            informational_result(
                "WEEX Server Time Read",
                True,
            )

            server_time = parse_server_time(
                server_response,
            )

            result(
                "WEEX Server Time Parseable",
                server_time is not None,
            )

            if server_time is not None:

                local_time = int(
                    time.time() * 1000
                )

                clock_delta = abs(
                    local_time
                    - server_time
                )

                print(
                    "  WEEX Server Time = "
                    f"{server_time}",
                    flush=True,
                )

                print(
                    "  Approx Clock Delta = "
                    f"{clock_delta} ms",
                    flush=True,
                )

        except Exception as exc:

            result(
                "WEEX Server Time Read",
                False,
            )

            print(
                "  Server Time Error = "
                f"{exc}",
                flush=True,
            )


        # ====================================================
        # AUTHENTICATED CONFIG READ
        # ====================================================

        section(
            "R28 UNIT N.3 "
            "AUTHENTICATED CONFIGURATION READ"
        )

        config = None

        try:

            response = await authenticated_get(
                session,
                SYMBOL_CONFIG_PATH,
                {
                    "symbol": SYMBOL,
                },
            )

            informational_result(
                "Authenticated Symbol Config Read",
                True,
            )

            config = extract_symbol_config(
                response,
            )

            result(
                "Observed Symbol Matches BTCUSDT",
                (
                    config is not None
                    and str(
                        config.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    == SYMBOL
                ),
            )

            observed_margin_type = ""

            if config is not None:

                observed_margin_type = str(
                    config.get(
                        "marginType",
                        "",
                    )
                ).upper()

            result(
                "Observed Margin Mode Is ISOLATED",
                (
                    observed_margin_type
                    == TARGET_MARGIN_TYPE
                ),
            )

            if config is not None:

                print(
                    "R28 UNIT N.3 CURRENT SYMBOL CONFIG:",
                    flush=True,
                )

                print(
                    "  Symbol = "
                    f"{config.get('symbol')}",
                    flush=True,
                )

                print(
                    "  Margin Type = "
                    f"{config.get('marginType')}",
                    flush=True,
                )

                print(
                    "  Position Mode = "
                    f"{config.get('separatedType')}",
                    flush=True,
                )

                print(
                    "  Cross Leverage = "
                    f"{config.get('crossLeverage')}x",
                    flush=True,
                )

                print(
                    "  Isolated Long Leverage = "
                    f"{config.get('isolatedLongLeverage')}x",
                    flush=True,
                )

                print(
                    "  Isolated Short Leverage = "
                    f"{config.get('isolatedShortLeverage')}x",
                    flush=True,
                )

        except Exception as exc:

            result(
                "Authenticated Symbol Config Read",
                False,
            )

            print(
                "  Config Read Error = "
                f"{exc}",
                flush=True,
            )


    # ========================================================
    # AUTHORIZATION CONSTRUCTION
    # ========================================================

    section(
        "R28 UNIT N.3 AUTHORIZATION CONSTRUCTION"
    )

    positive_authorization = (
        create_mutation_authorization(
            MUTATION_PAYLOAD,
        )
    )

    construction_checks = []

    construction_checks.append(
        informational_result(
            "Authorization ID Generated",
            bool(
                positive_authorization.authorization_id
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Bound To Module",
            (
                positive_authorization.module_name
                == MODULE_NAME
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Bound To Symbol",
            (
                positive_authorization.symbol
                == SYMBOL
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Bound To Margin Type",
            (
                positive_authorization.margin_type
                == TARGET_MARGIN_TYPE
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Bound To Long Leverage",
            (
                positive_authorization.long_leverage
                == TARGET_LONG_LEVERAGE
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Bound To Short Leverage",
            (
                positive_authorization.short_leverage
                == TARGET_SHORT_LEVERAGE
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Bound To Exact Payload Hash",
            hmac.compare_digest(
                positive_authorization.payload_hash,
                MUTATION_PAYLOAD_HASH,
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Has Expiry",
            (
                positive_authorization.expires_at_ms
                >
                positive_authorization.issued_at_ms
            ),
        )
    )

    construction_checks.append(
        informational_result(
            "Authorization Proof Generated",
            bool(
                positive_authorization.proof
            ),
        )
    )

    AUTHORIZATION_CONSTRUCTION_VERIFIED = all(
        construction_checks
    )

    PAYLOAD_BINDING_VERIFIED = (
        hmac.compare_digest(
            positive_authorization.payload_hash,
            MUTATION_PAYLOAD_HASH,
        )
    )

    if not AUTHORIZATION_CONSTRUCTION_VERIFIED:

        STRUCTURAL_FAILURES += 1

    if not PAYLOAD_BINDING_VERIFIED:

        STRUCTURAL_FAILURES += 1


    # ========================================================
    # NEGATIVE AUTHORIZATION TESTS
    # ========================================================

    section(
        "R28 UNIT N.3 NEGATIVE AUTHORIZATION TESTS"
    )

    negative_results = []


    # --------------------------------------------------------
    # Missing authorization
    # --------------------------------------------------------

    negative_results.append(
        expect_authorization_rejection(
            "Missing Authorization Rejected",
            MUTATION_PAYLOAD,
            None,
        )
    )


    # --------------------------------------------------------
    # Tampered payload
    # --------------------------------------------------------

    tampered_payload = dict(
        MUTATION_PAYLOAD
    )

    tampered_payload[
        "longLeverage"
    ] = "99"

    negative_results.append(
        expect_authorization_rejection(
            "Tampered Payload Rejected",
            tampered_payload,
            positive_authorization,
        )
    )


    # --------------------------------------------------------
    # Wrong symbol
    # --------------------------------------------------------

    wrong_symbol_authorization = (
        create_mutation_authorization(
            MUTATION_PAYLOAD,
            override_symbol="ETHUSDT",
        )
    )

    negative_results.append(
        expect_authorization_rejection(
            "Wrong Symbol Authorization Rejected",
            MUTATION_PAYLOAD,
            wrong_symbol_authorization,
        )
    )


    # --------------------------------------------------------
    # Wrong margin type
    # --------------------------------------------------------

    wrong_margin_authorization = (
        create_mutation_authorization(
            MUTATION_PAYLOAD,
            override_margin_type="CROSSED",
        )
    )

    negative_results.append(
        expect_authorization_rejection(
            "Wrong Margin-Type Authorization Rejected",
            MUTATION_PAYLOAD,
            wrong_margin_authorization,
        )
    )


    # --------------------------------------------------------
    # Wrong long leverage
    # --------------------------------------------------------

    wrong_long_authorization = (
        create_mutation_authorization(
            MUTATION_PAYLOAD,
            override_long_leverage=99,
        )
    )

    negative_results.append(
        expect_authorization_rejection(
            "Wrong Long-Leverage Authorization Rejected",
            MUTATION_PAYLOAD,
            wrong_long_authorization,
        )
    )


    # --------------------------------------------------------
    # Expired authorization
    # --------------------------------------------------------

    expired_authorization = (
        create_mutation_authorization(
            MUTATION_PAYLOAD,
            ttl_seconds=-1,
        )
    )

    negative_results.append(
        expect_authorization_rejection(
            "Expired Authorization Rejected",
            MUTATION_PAYLOAD,
            expired_authorization,
        )
    )


    # --------------------------------------------------------
    # Invalid proof
    # --------------------------------------------------------

    valid_for_invalid_proof = (
        create_mutation_authorization(
            MUTATION_PAYLOAD,
        )
    )

    invalid_proof_authorization = (
        MutationAuthorization(
            authorization_id=(
                valid_for_invalid_proof.authorization_id
            ),
            module_name=(
                valid_for_invalid_proof.module_name
            ),
            method=(
                valid_for_invalid_proof.method
            ),
            path=(
                valid_for_invalid_proof.path
            ),
            symbol=(
                valid_for_invalid_proof.symbol
            ),
            margin_type=(
                valid_for_invalid_proof.margin_type
            ),
            long_leverage=(
                valid_for_invalid_proof.long_leverage
            ),
            short_leverage=(
                valid_for_invalid_proof.short_leverage
            ),
            payload_hash=(
                valid_for_invalid_proof.payload_hash
            ),
            issued_at_ms=(
                valid_for_invalid_proof.issued_at_ms
            ),
            expires_at_ms=(
                valid_for_invalid_proof.expires_at_ms
            ),
            proof="INVALID-PROOF",
        )
    )

    negative_results.append(
        expect_authorization_rejection(
            "Invalid Authorization Proof Rejected",
            MUTATION_PAYLOAD,
            invalid_proof_authorization,
        )
    )

    if not all(
        negative_results
    ):

        STRUCTURAL_FAILURES += 1


    # ========================================================
    # POSITIVE AUTHORIZATION TEST
    # ========================================================

    section(
        "R28 UNIT N.3 "
        "POSITIVE LOCAL AUTHORIZATION TEST"
    )

    exact_authorization_accepted = False

    replay_rejected = False

    try:

        local_result = validate_mutation_authorization(
            MUTATION_PAYLOAD,
            positive_authorization,
            consume=True,
        )

        exact_authorization_accepted = (
            local_result
            == "authorized locally"
        )

        informational_result(
            "Exact Authorization Accepted Locally",
            exact_authorization_accepted,
        )

        print(
            "  Local Authorization Result = "
            f"{local_result}",
            flush=True,
        )

    except AuthorizationError as exc:

        informational_result(
            "Exact Authorization Accepted Locally",
            False,
        )

        print(
            "  Authorization Error = "
            f"{exc}",
            flush=True,
        )


    # --------------------------------------------------------
    # REPLAY SAME AUTHORIZATION
    # --------------------------------------------------------

    try:

        validate_mutation_authorization(
            MUTATION_PAYLOAD,
            positive_authorization,
            consume=True,
        )

        informational_result(
            "Authorization Replay Rejected",
            False,
        )

    except AuthorizationReplayError:

        replay_rejected = True

        informational_result(
            "Authorization Replay Rejected",
            True,
        )

    except AuthorizationError:

        informational_result(
            "Authorization Replay Rejected",
            False,
        )


    REPLAY_PROTECTION_VERIFIED = replay_rejected

    if not exact_authorization_accepted:

        STRUCTURAL_FAILURES += 1

    if not replay_rejected:

        STRUCTURAL_FAILURES += 1


    # ========================================================
    # CORRECTED FINAL TRANSPORT-BOUNDARY TEST
    # ========================================================

    section(
        "R28 UNIT N.3 FINAL TRANSPORT-BOUNDARY TEST"
    )

    # ========================================================
    # IMPORTANT CORRECTION:
    #
    # Generate a completely NEW authorization here.
    #
    # The previous authorization was intentionally consumed by
    # the positive test and replay test.
    #
    # Reusing it here would test the replay lock again rather
    # than independently testing the transport boundary.
    # ========================================================

    transport_authorization = (
        create_mutation_authorization(
            MUTATION_PAYLOAD,
        )
    )

    transport_auth_fresh = (
        transport_authorization.authorization_id
        not in CONSUMED_AUTHORIZATION_IDS
    )

    informational_result(
        "Fresh Transport Authorization Generated",
        transport_auth_fresh,
    )

    transport_blocked = False

    transport_failed_before_lock = False

    try:

        await attempt_authorized_leverage_post(
            MUTATION_PAYLOAD,
            transport_authorization,
        )

        informational_result(
            "Authorized Leverage POST Still Blocked Locally",
            False,
        )

    except LocalTransportBlock as exc:

        transport_blocked = True

        print(
            "R28 UNIT N.3 LOCAL BLOCK:",
            flush=True,
        )

        print(
            f"  {exc}",
            flush=True,
        )

        informational_result(
            "Authorized Leverage POST Still Blocked Locally",
            True,
        )

    except AuthorizationError as exc:

        transport_failed_before_lock = True

        print(
            "R28 UNIT N.3 AUTHORIZATION ERROR:",
            flush=True,
        )

        print(
            f"  {exc}",
            flush=True,
        )

        informational_result(
            "Authorized Leverage POST Still Blocked Locally",
            False,
        )


    transport_authorization_consumed = (
        transport_authorization.authorization_id
        in CONSUMED_AUTHORIZATION_IDS
    )

    informational_result(
        "Fresh Transport Authorization Accepted",
        transport_authorization_consumed,
    )

    TRANSPORT_LOCK_VERIFIED = (
        transport_auth_fresh
        and transport_authorization_consumed
        and transport_blocked
        and not transport_failed_before_lock
    )

    if not TRANSPORT_LOCK_VERIFIED:

        STRUCTURAL_FAILURES += 1


    # ========================================================
    # WRITE-LOCK AUDIT
    # ========================================================

    section(
        "R28 UNIT N.3 WRITE-LOCK AUDIT"
    )

    result(
        "Network POST Count Is Zero",
        AUDIT["network_posts"] == 0,
    )

    result(
        "Network PUT Count Is Zero",
        AUDIT["network_puts"] == 0,
    )

    result(
        "Network PATCH Count Is Zero",
        AUDIT["network_patches"] == 0,
    )

    result(
        "Network DELETE Count Is Zero",
        AUDIT["network_deletes"] == 0,
    )

    result(
        "Account Write Transmission Count Is Zero",
        AUDIT[
            "account_write_transmissions"
        ]
        == 0,
    )

    result(
        "Leverage Change Transmission Count Is Zero",
        AUDIT[
            "leverage_change_transmissions"
        ]
        == 0,
    )

    result(
        "Real Order Transmission Count Is Zero",
        AUDIT[
            "real_order_transmissions"
        ]
        == 0,
    )

    result(
        "Demo Order Transmission Count Is Zero",
        AUDIT[
            "demo_order_transmissions"
        ]
        == 0,
    )

    result(
        "Authorization Replay Was Blocked",
        AUDIT[
            "authorization_replays_blocked"
        ]
        >= 1,
    )


    # ========================================================
    # AUTHORIZATION AUDIT
    # ========================================================

    print(
        "",
        flush=True,
    )

    print(
        "R28 UNIT N.3 AUTHORIZATION AUDIT:",
        flush=True,
    )

    print(
        "  Authorization requests = "
        f"{AUDIT['authorization_requests']}",
        flush=True,
    )

    print(
        "  Authorization grants = "
        f"{AUDIT['authorization_grants']}",
        flush=True,
    )

    print(
        "  Authorization denials = "
        f"{AUDIT['authorization_denials']}",
        flush=True,
    )

    print(
        "  Authorization replays blocked = "
        f"{AUDIT['authorization_replays_blocked']}",
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
        "  Network POSTs = "
        f"{AUDIT['network_posts']}",
        flush=True,
    )

    print(
        "  Leverage change transmissions = "
        f"{AUDIT['leverage_change_transmissions']}",
        flush=True,
    )


    # ========================================================
    # EXECUTION-READINESS ASSESSMENT
    # ========================================================

    section(
        "R28 UNIT N.3 EXECUTION-READINESS ASSESSMENT"
    )

    print(
        "Structural Safety Failures = "
        f"{STRUCTURAL_FAILURES}",
        flush=True,
    )

    print(
        "Readiness Blockers = "
        f"{READINESS_BLOCKERS}",
        flush=True,
    )

    print(
        "Mutation Authorization Construction = "
        + (
            "✅ VERIFIED"
            if AUTHORIZATION_CONSTRUCTION_VERIFIED
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Exact Payload Binding = "
        + (
            "✅ VERIFIED"
            if PAYLOAD_BINDING_VERIFIED
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Authorization Replay Protection = "
        + (
            "✅ VERIFIED"
            if REPLAY_PROTECTION_VERIFIED
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Transport Boundary = "
        + (
            "✅ VERIFIED"
            if TRANSPORT_LOCK_VERIFIED
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY",
        flush=True,
    )


    passed = (
        STRUCTURAL_FAILURES == 0
        and READINESS_BLOCKERS == 0
        and AUTHORIZATION_CONSTRUCTION_VERIFIED
        and PAYLOAD_BINDING_VERIFIED
        and REPLAY_PROTECTION_VERIFIED
        and TRANSPORT_LOCK_VERIFIED
        and AUDIT["network_posts"] == 0
        and AUDIT["network_puts"] == 0
        and AUDIT["network_patches"] == 0
        and AUDIT["network_deletes"] == 0
        and AUDIT[
            "leverage_change_transmissions"
        ]
        == 0
    )

    print(
        "",
        flush=True,
    )

    if passed:

        print(
            "✅ R28 UNIT N.3 DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ MUTATION AUTHORIZATION VERIFIED",
            flush=True,
        )

        print(
            "✅ EXACT PAYLOAD BINDING VERIFIED",
            flush=True,
        )

        print(
            "✅ AUTHORIZATION REPLAY PROTECTION VERIFIED",
            flush=True,
        )

        print(
            "✅ FRESH AUTHORIZATION TRANSPORT TEST VERIFIED",
            flush=True,
        )

        print(
            "🛡 LEVERAGE MUTATION TRANSPORT REMAINS LOCKED",
            flush=True,
        )

        print(
            "🛡 NO NETWORK WRITE WAS TRANSMITTED",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT N.3 DIAGNOSTIC DID NOT PASS",
            flush=True,
        )

    print(
        DOUBLE_LINE,
        flush=True,
    )

    return passed


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request: web.Request,
) -> web.Response:

    return web.json_response(
        {
            "status": "active",
            "module": MODULE_NAME,
            "version": MODULE_VERSION,

            "liveExecution": LIVE_ORDER_EXECUTION,
            "demoExecution": DEMO_ORDER_EXECUTION,

            "networkWritesEnabled": (
                NETWORK_WRITES_ENABLED
            ),

            "accountWritesEnabled": (
                ACCOUNT_WRITES_ENABLED
            ),

            "leverageWritesEnabled": (
                LEVERAGE_WRITES_ENABLED
            ),

            "leverageMutationTransportEnabled": (
                LEVERAGE_MUTATION_TRANSPORT_ENABLED
            ),

            "networkPosts": AUDIT[
                "network_posts"
            ],

            "leverageChangeTransmissions": AUDIT[
                "leverage_change_transmissions"
            ],
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
        app,
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        HEALTH_PORT,
    )

    await site.start()

    print(
        "R28 UNIT N.3: "
        f"HEALTH SERVER ACTIVE ON PORT {HEALTH_PORT}",
        flush=True,
    )

    return runner


# ============================================================
# HEARTBEAT
# ============================================================

async def heartbeat_loop(
    stop_event: asyncio.Event,
):

    heartbeat = 0

    while not stop_event.is_set():

        heartbeat += 1

        print(
            "R28 UNIT N.3: "
            f"HEARTBEAT {heartbeat} ✅ ACTIVE",
            flush=True,
        )

        try:

            await asyncio.wait_for(
                stop_event.wait(),
                timeout=15,
            )

        except asyncio.TimeoutError:

            pass


# ============================================================
# RUNTIME
# ============================================================

async def runtime():

    print(
        "R28 UNIT N.3: RUNTIME STARTING",
        flush=True,
    )

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    def request_shutdown():

        if not stop_event.is_set():

            print(
                "R28 UNIT N.3: SHUTDOWN REQUESTED",
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


    health_runner = await start_health_server()


    try:

        await run_diagnostic()

        print(
            DOUBLE_LINE,
            flush=True,
        )

        print(
            "R28 UNIT N.3: PERSISTENT RUNTIME ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.3: "
            "AUTHENTICATED READ-ONLY LOCKS ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.3: "
            "NETWORK WRITE TRANSPORT LOCKED",
            flush=True,
        )

        print(
            "R28 UNIT N.3: "
            "LEVERAGE MUTATION TRANSPORT LOCKED",
            flush=True,
        )

        print(
            "R28 UNIT N.3: "
            "AUTHORIZATION REPLAY LOCK ACTIVE",
            flush=True,
        )

        await heartbeat_loop(
            stop_event,
        )

    finally:

        try:

            await health_runner.cleanup()

        except Exception:

            pass

        print(
            "R28 UNIT N.3: RUNTIME STOPPED CLEANLY",
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
            "R28 UNIT N.3: KEYBOARD INTERRUPT",
            flush=True,
        )

    except Exception as exc:

        print(
            "R28 UNIT N.3: FATAL ERROR:",
            flush=True,
        )

        print(
            repr(exc),
            flush=True,
        )

        raise
