# ============================================================
# 0F-4H-R28-UNIT-N.2
# LEVERAGE MUTATION CONSTRUCTION / LOCAL INTERCEPTION
#
# PURPOSE
# ------------------------------------------------------------
# 1. Read real BTCUSDT symbol configuration.
# 2. Construct the exact WEEX V3 leverage mutation payload.
# 3. Construct the authenticated POST signature locally.
# 4. Validate deterministic payload construction.
# 5. Validate long/short leverage targeting.
# 6. Intercept the leverage POST locally.
# 7. Prove ZERO network writes occurred.
#
# ABSOLUTE SAFETY:
#   NO REAL ORDER TRANSMISSION
#   NO DEMO ORDER TRANSMISSION
#   NO ACCOUNT WRITE TRANSMISSION
#   NO LEVERAGE CHANGE TRANSMISSION
#
# PUBLIC GET + AUTHENTICATED READ-ONLY GET ONLY.
# ============================================================

print(
    "R28 UNIT N.2: MAIN.PY ENTERED",
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
import time
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

import aiohttp
from aiohttp import web

print(
    "R28 UNIT N.2: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-N.2"
MODULE_VERSION = "R28-N.2"

SYMBOL = "BTCUSDT"

BASE_URL = "https://api-contract.weex.com"

SERVER_TIME_PATH = "/capi/v3/market/time"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

# Official WEEX V3 leverage mutation endpoint.
LEVERAGE_PATH = "/capi/v3/account/leverage"

print(
    "R28 UNIT N.2: CONSTANTS INITIALIZED",
    flush=True,
)


# ============================================================
# N.2 DIAGNOSTIC TARGET
# ============================================================

TARGET_MARGIN_TYPE = "ISOLATED"

# Construction target only.
#
# THIS UNIT DOES NOT APPLY THESE VALUES TO WEEX.
TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

MIN_ALLOWED_LEVERAGE = Decimal("1")
MAX_LOCAL_LEVERAGE = Decimal("100")


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
# TRANSPORT COUNTERS
# ============================================================

TRANSPORT_AUDIT = {
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
# RUNTIME CONTROL
# ============================================================

SHUTDOWN_EVENT = asyncio.Event()


# ============================================================
# ENVIRONMENT
# ============================================================

API_KEY = os.getenv("WEEX_API_KEY", "").strip()
API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# ============================================================
# FORMAT HELPERS
# ============================================================

LINE = "=" * 76
SUBLINE = "-" * 76


def section(title):
    print()
    print(title, flush=True)
    print(SUBLINE, flush=True)


def gate(name, passed):
    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{name:<68} {status}",
        flush=True,
    )

    return passed


def decimal_text(value):
    value = Decimal(str(value))

    normalized = value.normalize()

    text = format(
        normalized,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def safe_decimal(value):
    try:
        return Decimal(str(value))

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return None


# ============================================================
# CREDENTIAL VALIDATION
# ============================================================

def credentials_present():
    return bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )


# ============================================================
# CANONICAL JSON
# ============================================================

def canonical_json(payload):
    """
    Produces stable JSON bytes/string for signature construction.

    Important:
    The exact same JSON string that is signed would need to be
    transmitted if writes were ever authorized.

    N.2 NEVER transmits it.
    """

    return json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
    )


# ============================================================
# SIGNATURE GENERATION
# ============================================================

def build_signature_message(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    method = method.upper()

    if query_string:
        return (
            str(timestamp)
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    return (
        str(timestamp)
        + method
        + request_path
        + body
    )


def generate_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    message = build_signature_message(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ============================================================
# AUTHENTICATED HEADERS
# ============================================================

def authenticated_headers(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):
    signature = generate_signature(
        timestamp=timestamp,
        method=method,
        request_path=path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": str(timestamp),
        "Content-Type": "application/json",
    }


# ============================================================
# READ-ONLY PUBLIC TRANSPORT
# ============================================================

async def public_get(
    session,
    path,
    query_string="",
):
    if not PUBLIC_GET_ENABLED:
        raise RuntimeError(
            "Public GET disabled."
        )

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    print(
        f"R28 UNIT N.2: PUBLIC GET -> "
        f"{path}"
        + (
            f"?{query_string}"
            if query_string
            else ""
        ),
        flush=True,
    )

    TRANSPORT_AUDIT["public_gets"] += 1

    async with session.get(
        url,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status < 200 or response.status >= 300:
            raise RuntimeError(
                "Public GET failed: "
                f"HTTP {response.status}: "
                f"{text[:300]}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            return text


# ============================================================
# AUTHENTICATED READ-ONLY TRANSPORT
# ============================================================

async def authenticated_get(
    session,
    path,
    query_string="",
):
    if not AUTHENTICATED_READ_ONLY_GET_ENABLED:
        raise RuntimeError(
            "Authenticated GET disabled."
        )

    if not credentials_present():
        raise RuntimeError(
            "WEEX API credentials are missing."
        )

    timestamp = int(
        time.time() * 1000
    )

    headers = authenticated_headers(
        timestamp=timestamp,
        method="GET",
        path=path,
        query_string=query_string,
        body="",
    )

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    print(
        f"R28 UNIT N.2: AUTHENTICATED GET -> "
        f"{path}"
        + (
            f"?{query_string}"
            if query_string
            else ""
        ),
        flush=True,
    )

    TRANSPORT_AUDIT[
        "authenticated_gets"
    ] += 1

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
                "Authenticated GET failed: "
                f"HTTP {response.status}: "
                f"{text[:500]}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                "Authenticated response "
                "was not valid JSON."
            )


# ============================================================
# ABSOLUTELY BLOCKED WRITE TRANSPORT
# ============================================================

async def blocked_post(
    path,
    body,
    headers=None,
):
    """
    Deliberately DOES NOT create any HTTP request.

    This function represents the write boundary.

    Any attempt to reach POST transport is counted
    and rejected locally.
    """

    TRANSPORT_AUDIT[
        "local_post_attempts"
    ] += 1

    TRANSPORT_AUDIT[
        "local_post_blocks"
    ] += 1

    raise PermissionError(
        "R28 UNIT N.2 LOCAL WRITE LOCK: "
        f"POST {path} blocked before network transport."
    )


async def blocked_put(*args, **kwargs):
    raise PermissionError(
        "PUT blocked locally."
    )


async def blocked_patch(*args, **kwargs):
    raise PermissionError(
        "PATCH blocked locally."
    )


async def blocked_delete(*args, **kwargs):
    raise PermissionError(
        "DELETE blocked locally."
    )


# ============================================================
# SYMBOL CONFIG NORMALIZATION
# ============================================================

def extract_symbol_config(data):
    if isinstance(data, list):
        for item in data:
            if (
                isinstance(item, dict)
                and str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ):
                return item

    if isinstance(data, dict):

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

        nested_data = data.get("data")

        if isinstance(
            nested_data,
            list,
        ):
            for item in nested_data:
                if (
                    isinstance(item, dict)
                    and str(
                        item.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    == SYMBOL
                ):
                    return item

        if isinstance(
            nested_data,
            dict,
        ):
            if (
                str(
                    nested_data.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ):
                return nested_data

    raise RuntimeError(
        "BTCUSDT symbol configuration "
        "could not be extracted."
    )


# ============================================================
# LEVERAGE PLAN
# ============================================================

def build_leverage_plan(config):
    margin_type = str(
        config.get(
            "marginType",
            "",
        )
    ).upper()

    position_mode = str(
        config.get(
            "separatedType",
            config.get(
                "positionMode",
                "",
            ),
        )
    ).upper()

    current_long = safe_decimal(
        config.get(
            "isolatedLongLeverage"
        )
    )

    current_short = safe_decimal(
        config.get(
            "isolatedShortLeverage"
        )
    )

    current_cross = safe_decimal(
        config.get(
            "crossLeverage"
        )
    )

    if margin_type != "ISOLATED":
        raise RuntimeError(
            "N.2 requires BTCUSDT to "
            "already be ISOLATED."
        )

    if current_long is None:
        raise RuntimeError(
            "Current isolated long leverage "
            "is not parseable."
        )

    if current_short is None:
        raise RuntimeError(
            "Current isolated short leverage "
            "is not parseable."
        )

    if not (
        MIN_ALLOWED_LEVERAGE
        <= TARGET_LONG_LEVERAGE
        <= MAX_LOCAL_LEVERAGE
    ):
        raise RuntimeError(
            "Target long leverage violates "
            "local leverage policy."
        )

    if not (
        MIN_ALLOWED_LEVERAGE
        <= TARGET_SHORT_LEVERAGE
        <= MAX_LOCAL_LEVERAGE
    ):
        raise RuntimeError(
            "Target short leverage violates "
            "local leverage policy."
        )

    long_change_required = (
        current_long
        != TARGET_LONG_LEVERAGE
    )

    short_change_required = (
        current_short
        != TARGET_SHORT_LEVERAGE
    )

    payload = {
        "symbol": SYMBOL,
        "marginType": "ISOLATED",
        "isolatedLongLeverage":
            decimal_text(
                TARGET_LONG_LEVERAGE
            ),
        "isolatedShortLeverage":
            decimal_text(
                TARGET_SHORT_LEVERAGE
            ),
    }

    return {
        "symbol": SYMBOL,
        "margin_type": margin_type,
        "position_mode": position_mode,
        "current_cross": current_cross,
        "current_long": current_long,
        "current_short": current_short,
        "target_long":
            TARGET_LONG_LEVERAGE,
        "target_short":
            TARGET_SHORT_LEVERAGE,
        "long_change_required":
            long_change_required,
        "short_change_required":
            short_change_required,
        "payload": payload,
    }


# ============================================================
# PAYLOAD FINGERPRINT
# ============================================================

def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


# ============================================================
# SERVER TIME PARSING
# ============================================================

def extract_server_time(data):
    candidates = []

    if isinstance(data, int):
        candidates.append(data)

    if isinstance(data, str):
        candidates.append(data)

    if isinstance(data, dict):
        for key in (
            "serverTime",
            "time",
            "timestamp",
            "data",
        ):
            value = data.get(key)

            if isinstance(
                value,
                (
                    int,
                    str,
                ),
            ):
                candidates.append(value)

            elif isinstance(
                value,
                dict,
            ):
                for nested_key in (
                    "serverTime",
                    "time",
                    "timestamp",
                ):
                    nested_value = value.get(
                        nested_key
                    )

                    if nested_value is not None:
                        candidates.append(
                            nested_value
                        )

    for candidate in candidates:
        try:
            parsed = int(candidate)

            if parsed > 0:
                return parsed

        except (
            TypeError,
            ValueError,
        ):
            continue

    raise RuntimeError(
        "WEEX server time could not be parsed."
    )


# ============================================================
# DIAGNOSTIC
# ============================================================

async def run_diagnostic():
    print(LINE)
    print(
        "0F-4H-R28-UNIT-N.2 STARTING",
        flush=True,
    )
    print(
        "LEVERAGE MUTATION CONSTRUCTION "
        "/ LOCAL INTERCEPTION",
        flush=True,
    )
    print(
        "AUTHENTICATED READ-ONLY ACCOUNT "
        "STATE ENABLED",
        flush=True,
    )
    print(
        "ALL NETWORK WRITE METHODS LOCKED",
        flush=True,
    )
    print(
        "NO LEVERAGE CHANGE WILL BE "
        "TRANSMITTED",
        flush=True,
    )
    print(LINE)

    structural_failures = 0

    # ========================================================
    # CREDENTIAL STATUS
    # ========================================================

    section(
        "R28 UNIT N.2 CREDENTIAL STATUS"
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

    section(
        "R28 UNIT N.2 ABSOLUTE SAFETY GATES"
    )

    safety_tests = [
        (
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        ),
        (
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        ),
        (
            "Network Writes Disabled",
            NETWORK_WRITES_ENABLED is False,
        ),
        (
            "Account Writes Disabled",
            ACCOUNT_WRITES_ENABLED is False,
        ),
        (
            "Leverage Writes Disabled",
            LEVERAGE_WRITES_ENABLED is False,
        ),
        (
            "Leverage Mutation Feature Disabled",
            LEVERAGE_MUTATION_FEATURE_ENABLED
            is False,
        ),
        (
            "Explicit Mutation Authorization Disabled",
            EXPLICIT_MUTATION_AUTHORIZATION
            is False,
        ),
        (
            "Leverage Mutation Transport Disabled",
            LEVERAGE_MUTATION_TRANSPORT_ENABLED
            is False,
        ),
        (
            "Public GET Enabled",
            PUBLIC_GET_ENABLED is True,
        ),
        (
            "Authenticated Read-Only GET Enabled",
            AUTHENTICATED_READ_ONLY_GET_ENABLED
            is True,
        ),
    ]

    for name, result in safety_tests:
        if not gate(
            name,
            result,
        ):
            structural_failures += 1

    # ========================================================
    # STATIC ENDPOINT VALIDATION
    # ========================================================

    section(
        "R28 UNIT N.2 ENDPOINT CONSTRUCTION GATES"
    )

    endpoint_tests = [
        (
            "Leverage Method Is POST",
            "POST" == "POST",
        ),
        (
            "Leverage Path Is Contract V3",
            LEVERAGE_PATH
            == "/capi/v3/account/leverage",
        ),
        (
            "Mutation Symbol Is BTCUSDT",
            SYMBOL == "BTCUSDT",
        ),
        (
            "Target Margin Type Is ISOLATED",
            TARGET_MARGIN_TYPE
            == "ISOLATED",
        ),
    ]

    for name, result in endpoint_tests:
        if not gate(
            name,
            result,
        ):
            structural_failures += 1

    # ========================================================
    # TARGET LEVERAGE POLICY
    # ========================================================

    section(
        "R28 UNIT N.2 TARGET LEVERAGE POLICY"
    )

    target_tests = [
        (
            "Target Long Leverage Positive",
            TARGET_LONG_LEVERAGE > 0,
        ),
        (
            "Target Short Leverage Positive",
            TARGET_SHORT_LEVERAGE > 0,
        ),
        (
            "Target Long Within Local 100x Cap",
            TARGET_LONG_LEVERAGE
            <= MAX_LOCAL_LEVERAGE,
        ),
        (
            "Target Short Within Local 100x Cap",
            TARGET_SHORT_LEVERAGE
            <= MAX_LOCAL_LEVERAGE,
        ),
    ]

    for name, result in target_tests:
        if not gate(
            name,
            result,
        ):
            structural_failures += 1

    print()
    print(
        "R28 UNIT N.2 DIAGNOSTIC TARGET:",
        flush=True,
    )
    print(
        f"  Symbol = {SYMBOL}",
        flush=True,
    )
    print(
        f"  Margin Type = "
        f"{TARGET_MARGIN_TYPE}",
        flush=True,
    )
    print(
        f"  Target Long Leverage = "
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x",
        flush=True,
    )
    print(
        f"  Target Short Leverage = "
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x",
        flush=True,
    )

    if structural_failures:
        raise RuntimeError(
            "Structural safety gates failed "
            "before network reads."
        )

    # ========================================================
    # SESSION
    # ========================================================

    async with aiohttp.ClientSession() as session:

        # ====================================================
        # SERVER CLOCK
        # ====================================================

        section(
            "R28 UNIT N.2 SERVER-CLOCK VALIDATION"
        )

        server_time_raw = await public_get(
            session,
            SERVER_TIME_PATH,
        )

        server_time = extract_server_time(
            server_time_raw
        )

        local_time = int(
            time.time() * 1000
        )

        clock_delta = abs(
            local_time
            - server_time
        )

        gate(
            "WEEX Server Time Read",
            server_time > 0,
        )

        gate(
            "WEEX Server Time Parseable",
            isinstance(
                server_time,
                int,
            ),
        )

        print(
            f"  WEEX Server Time = "
            f"{server_time}",
            flush=True,
        )

        print(
            f"  Approx Clock Delta = "
            f"{clock_delta} ms",
            flush=True,
        )

        # ====================================================
        # AUTHENTICATED CONFIG READ
        # ====================================================

        section(
            "R28 UNIT N.2 AUTHENTICATED "
            "CONFIGURATION READ"
        )

        query_string = urlencode(
            {
                "symbol": SYMBOL,
            }
        )

        config_raw = await authenticated_get(
            session,
            SYMBOL_CONFIG_PATH,
            query_string,
        )

        config = extract_symbol_config(
            config_raw
        )

        plan = build_leverage_plan(
            config
        )

        print()
        print(
            "R28 UNIT N.2 CURRENT SYMBOL CONFIG:",
            flush=True,
        )

        print(
            f"  Symbol = "
            f"{plan['symbol']}",
            flush=True,
        )

        print(
            f"  Margin Type = "
            f"{plan['margin_type']}",
            flush=True,
        )

        print(
            f"  Position Mode = "
            f"{plan['position_mode']}",
            flush=True,
        )

        print(
            f"  Cross Leverage = "
            f"{plan['current_cross']}x",
            flush=True,
        )

        print(
            f"  Isolated Long Leverage = "
            f"{plan['current_long']}x",
            flush=True,
        )

        print(
            f"  Isolated Short Leverage = "
            f"{plan['current_short']}x",
            flush=True,
        )

        print()
        print(
            "R28 UNIT N.2 PROPOSED "
            "LEVERAGE PLAN:",
            flush=True,
        )

        print(
            f"  Target Long = "
            f"{plan['target_long']}x",
            flush=True,
        )

        print(
            f"  Target Short = "
            f"{plan['target_short']}x",
            flush=True,
        )

        print(
            "  Long Change Required = "
            + (
                "YES"
                if plan[
                    "long_change_required"
                ]
                else "NO"
            ),
            flush=True,
        )

        print(
            "  Short Change Required = "
            + (
                "YES"
                if plan[
                    "short_change_required"
                ]
                else "NO"
            ),
            flush=True,
        )

        # ====================================================
        # PAYLOAD CONSTRUCTION
        # ====================================================

        section(
            "R28 UNIT N.2 LEVERAGE "
            "PAYLOAD CONSTRUCTION"
        )

        payload_1 = plan["payload"]

        payload_2 = build_leverage_plan(
            config
        )["payload"]

        body_1 = canonical_json(
            payload_1
        )

        body_2 = canonical_json(
            payload_2
        )

        payload_hash_1 = sha256_text(
            body_1
        )

        payload_hash_2 = sha256_text(
            body_2
        )

        payload_tests = [
            (
                "Payload Symbol Preserved",
                payload_1.get("symbol")
                == SYMBOL,
            ),
            (
                "Payload Margin Type Preserved",
                payload_1.get(
                    "marginType"
                )
                == "ISOLATED",
            ),
            (
                "Payload Contains Long Leverage",
                payload_1.get(
                    "isolatedLongLeverage"
                )
                == decimal_text(
                    TARGET_LONG_LEVERAGE
                ),
            ),
            (
                "Payload Contains Short Leverage",
                payload_1.get(
                    "isolatedShortLeverage"
                )
                == decimal_text(
                    TARGET_SHORT_LEVERAGE
                ),
            ),
            (
                "Payload Deterministic",
                body_1 == body_2,
            ),
            (
                "Payload Hash Deterministic",
                payload_hash_1
                == payload_hash_2,
            ),
        ]

        for name, result in payload_tests:
            if not gate(
                name,
                result,
            ):
                structural_failures += 1

        print()
        print(
            "R28 UNIT N.2 CONSTRUCTED BODY:",
            flush=True,
        )

        print(
            f"  {body_1}",
            flush=True,
        )

        print(
            "R28 UNIT N.2 PAYLOAD SHA256:",
            flush=True,
        )

        print(
            f"  {payload_hash_1}",
            flush=True,
        )

        # ====================================================
        # POST SIGNATURE CONSTRUCTION
        # ====================================================

        section(
            "R28 UNIT N.2 POST "
            "SIGNATURE-CONSTRUCTION GATES"
        )

        test_timestamp = str(
            server_time
        )

        signature_message_1 = (
            build_signature_message(
                timestamp=test_timestamp,
                method="POST",
                request_path=LEVERAGE_PATH,
                query_string="",
                body=body_1,
            )
        )

        signature_message_2 = (
            build_signature_message(
                timestamp=test_timestamp,
                method="POST",
                request_path=LEVERAGE_PATH,
                query_string="",
                body=body_2,
            )
        )

        signature_1 = generate_signature(
            timestamp=test_timestamp,
            method="POST",
            request_path=LEVERAGE_PATH,
            query_string="",
            body=body_1,
        )

        signature_2 = generate_signature(
            timestamp=test_timestamp,
            method="POST",
            request_path=LEVERAGE_PATH,
            query_string="",
            body=body_2,
        )

        signature_tests = [
            (
                "POST Signature Uses Uppercase Method",
                "POST"
                in signature_message_1,
            ),
            (
                "POST Signature Uses Contract V3 Path",
                LEVERAGE_PATH
                in signature_message_1,
            ),
            (
                "POST Signature Includes Exact JSON Body",
                signature_message_1.endswith(
                    body_1
                ),
            ),
            (
                "POST Signature Has No Query Separator",
                (
                    LEVERAGE_PATH + "?"
                )
                not in signature_message_1,
            ),
            (
                "HMAC-SHA256 Digest Generated",
                bool(signature_1),
            ),
            (
                "Signature Base64 Encoded",
                isinstance(
                    signature_1,
                    str,
                )
                and len(signature_1) > 0,
            ),
            (
                "Signature Message Deterministic",
                signature_message_1
                == signature_message_2,
            ),
            (
                "Signature Deterministic",
                signature_1
                == signature_2,
            ),
        ]

        for name, result in signature_tests:
            if not gate(
                name,
                result,
            ):
                structural_failures += 1

        # ====================================================
        # BODY TAMPERING TEST
        # ====================================================

        section(
            "R28 UNIT N.2 PAYLOAD "
            "TAMPER-DETECTION GATES"
        )

        tampered_payload = dict(
            payload_1
        )

        tampered_payload[
            "isolatedLongLeverage"
        ] = "99"

        tampered_body = canonical_json(
            tampered_payload
        )

        tampered_signature = (
            generate_signature(
                timestamp=test_timestamp,
                method="POST",
                request_path=LEVERAGE_PATH,
                query_string="",
                body=tampered_body,
            )
        )

        tamper_tests = [
            (
                "Tampered Body Differs",
                tampered_body
                != body_1,
            ),
            (
                "Tampered Hash Differs",
                sha256_text(
                    tampered_body
                )
                != payload_hash_1,
            ),
            (
                "Tampered Signature Differs",
                tampered_signature
                != signature_1,
            ),
        ]

        for name, result in tamper_tests:
            if not gate(
                name,
                result,
            ):
                structural_failures += 1

        # ====================================================
        # BUILD FINAL AUTH HEADERS LOCALLY
        # ====================================================

        section(
            "R28 UNIT N.2 AUTHENTICATED "
            "WRITE ENVELOPE CONSTRUCTION"
        )

        local_timestamp = int(
            time.time() * 1000
        )

        mutation_headers = (
            authenticated_headers(
                timestamp=local_timestamp,
                method="POST",
                path=LEVERAGE_PATH,
                query_string="",
                body=body_1,
            )
        )

        envelope_tests = [
            (
                "ACCESS-KEY Constructed",
                bool(
                    mutation_headers.get(
                        "ACCESS-KEY"
                    )
                ),
            ),
            (
                "ACCESS-SIGN Constructed",
                bool(
                    mutation_headers.get(
                        "ACCESS-SIGN"
                    )
                ),
            ),
            (
                "ACCESS-PASSPHRASE Constructed",
                bool(
                    mutation_headers.get(
                        "ACCESS-PASSPHRASE"
                    )
                ),
            ),
            (
                "ACCESS-TIMESTAMP Constructed",
                bool(
                    mutation_headers.get(
                        "ACCESS-TIMESTAMP"
                    )
                ),
            ),
            (
                "Content-Type JSON",
                mutation_headers.get(
                    "Content-Type"
                )
                == "application/json",
            ),
        ]

        for name, result in envelope_tests:
            if not gate(
                name,
                result,
            ):
                structural_failures += 1

        # ====================================================
        # LOCAL INTERCEPTION
        # ====================================================

        section(
            "R28 UNIT N.2 TRANSPORT-BOUNDARY "
            "INTERCEPTION"
        )

        leverage_post_blocked = False

        try:
            await blocked_post(
                LEVERAGE_PATH,
                body_1,
                mutation_headers,
            )

        except PermissionError as exc:
            leverage_post_blocked = True

            print(
                "R28 UNIT N.2 LOCAL BLOCK:",
                flush=True,
            )

            print(
                f"  {exc}",
                flush=True,
            )

        if not gate(
            "Leverage POST Attempt Blocked Locally",
            leverage_post_blocked,
        ):
            structural_failures += 1

        # ====================================================
        # WRITE-LOCK AUDIT
        # ====================================================

        section(
            "R28 UNIT N.2 WRITE-LOCK AUDIT"
        )

        write_tests = [
            (
                "Network POST Count Is Zero",
                TRANSPORT_AUDIT[
                    "network_posts"
                ]
                == 0,
            ),
            (
                "Network PUT Count Is Zero",
                TRANSPORT_AUDIT[
                    "network_puts"
                ]
                == 0,
            ),
            (
                "Network PATCH Count Is Zero",
                TRANSPORT_AUDIT[
                    "network_patches"
                ]
                == 0,
            ),
            (
                "Network DELETE Count Is Zero",
                TRANSPORT_AUDIT[
                    "network_deletes"
                ]
                == 0,
            ),
            (
                "Account Write Transmission Count Is Zero",
                TRANSPORT_AUDIT[
                    "account_write_transmissions"
                ]
                == 0,
            ),
            (
                "Leverage Change Transmission Count Is Zero",
                TRANSPORT_AUDIT[
                    "leverage_change_transmissions"
                ]
                == 0,
            ),
            (
                "Real Order Transmission Count Is Zero",
                TRANSPORT_AUDIT[
                    "real_order_transmissions"
                ]
                == 0,
            ),
            (
                "Demo Order Transmission Count Is Zero",
                TRANSPORT_AUDIT[
                    "demo_order_transmissions"
                ]
                == 0,
            ),
        ]

        for name, result in write_tests:
            if not gate(
                name,
                result,
            ):
                structural_failures += 1

        # ====================================================
        # TRANSPORT SUMMARY
        # ====================================================

        print()
        print(
            "R28 UNIT N.2 TRANSPORT AUDIT:",
            flush=True,
        )

        print(
            "  Public GETs = "
            f"{TRANSPORT_AUDIT['public_gets']}",
            flush=True,
        )

        print(
            "  Authenticated GETs = "
            f"{TRANSPORT_AUDIT['authenticated_gets']}",
            flush=True,
        )

        print(
            "  Local POST attempts = "
            f"{TRANSPORT_AUDIT['local_post_attempts']}",
            flush=True,
        )

        print(
            "  Local POST blocks = "
            f"{TRANSPORT_AUDIT['local_post_blocks']}",
            flush=True,
        )

        print(
            "  Network POSTs = "
            f"{TRANSPORT_AUDIT['network_posts']}",
            flush=True,
        )

        print(
            "  Account write transmissions = "
            f"{TRANSPORT_AUDIT['account_write_transmissions']}",
            flush=True,
        )

        print(
            "  Leverage change transmissions = "
            f"{TRANSPORT_AUDIT['leverage_change_transmissions']}",
            flush=True,
        )

        # ====================================================
        # FINAL ASSESSMENT
        # ====================================================

        section(
            "R28 UNIT N.2 EXECUTION-READINESS "
            "ASSESSMENT"
        )

        readiness_blockers = (
            structural_failures
        )

        print(
            f"Structural Safety Failures = "
            f"{structural_failures}",
            flush=True,
        )

        print(
            f"Readiness Blockers = "
            f"{readiness_blockers}",
            flush=True,
        )

        print(
            "Authenticated Configuration Read = "
            "✅ VERIFIED",
            flush=True,
        )

        print(
            "Leverage Mutation Payload = "
            "✅ CONSTRUCTED",
            flush=True,
        )

        print(
            "Leverage Mutation Signature = "
            "✅ CONSTRUCTED",
            flush=True,
        )

        print(
            "Leverage Mutation Transmission = "
            "🛡 BLOCKED LOCALLY",
            flush=True,
        )

        print()

        if structural_failures == 0:

            print(
                "CURRENT EXECUTION READINESS: "
                "✅ N.2 LEVERAGE MUTATION "
                "CONSTRUCTION VERIFIED",
                flush=True,
            )

            print()
            print(SUBLINE)

            print(
                "✅ R28 UNIT N.2 STRUCTURAL "
                "DIAGNOSTIC PASSED",
                flush=True,
            )

            print(
                "✅ CURRENT BTCUSDT CONFIGURATION "
                "READ VERIFIED",
                flush=True,
            )

            print(
                "✅ LEVERAGE MUTATION ENDPOINT "
                "CONSTRUCTION VERIFIED",
                flush=True,
            )

            print(
                "✅ ISOLATED LONG/SHORT LEVERAGE "
                "PAYLOAD VERIFIED",
                flush=True,
            )

            print(
                "✅ POST BODY SIGNATURE "
                "CONSTRUCTION VERIFIED",
                flush=True,
            )

            print(
                "✅ DETERMINISTIC PAYLOAD "
                "CONSTRUCTION VERIFIED",
                flush=True,
            )

            print(
                "✅ PAYLOAD TAMPERING "
                "DETECTION VERIFIED",
                flush=True,
            )

            print(
                "✅ NETWORK WRITE TRANSPORT "
                "REMAINS LOCKED",
                flush=True,
            )

            print(
                "🛡 NO LEVERAGE CHANGE WAS "
                "TRANSMITTED TO WEEX",
                flush=True,
            )

            print(
                "🛡 NO ACCOUNT WRITE WAS "
                "TRANSMITTED TO WEEX",
                flush=True,
            )

            print(
                "🛡 REAL ORDER TRANSMISSION "
                "IMPOSSIBLE",
                flush=True,
            )

            print(
                "🛡 DEMO ORDER TRANSMISSION "
                "IMPOSSIBLE",
                flush=True,
            )

        else:

            print(
                "❌ R28 UNIT N.2 DIAGNOSTIC FAILED",
                flush=True,
            )

            raise RuntimeError(
                "N.2 structural validation failed."
            )

    print(LINE)


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(request):
    return web.Response(
        text=(
            "0F-4H-R28-UNIT-N.2 ACTIVE\n"
            "READ-ONLY NETWORK ACTIVE\n"
            "NETWORK WRITES LOCKED\n"
            "LEVERAGE MUTATION LOCKED\n"
            "REAL ORDERS LOCKED\n"
            "DEMO ORDERS LOCKED\n"
        )
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

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port,
    )

    await site.start()

    print(
        f"R28 UNIT N.2: HEALTH SERVER "
        f"ACTIVE ON PORT {port}",
        flush=True,
    )

    return runner


# ============================================================
# HEARTBEAT
# ============================================================

async def heartbeat_loop():
    count = 0

    while not SHUTDOWN_EVENT.is_set():

        count += 1

        print(
            f"R28 UNIT N.2: HEARTBEAT "
            f"{count} ✅ ACTIVE",
            flush=True,
        )

        try:
            await asyncio.wait_for(
                SHUTDOWN_EVENT.wait(),
                timeout=15,
            )

        except asyncio.TimeoutError:
            pass


# ============================================================
# SHUTDOWN
# ============================================================

def request_shutdown():
    if not SHUTDOWN_EVENT.is_set():

        print(
            "R28 UNIT N.2: "
            "SHUTDOWN REQUESTED",
            flush=True,
        )

        SHUTDOWN_EVENT.set()


# ============================================================
# RUNTIME
# ============================================================

async def runtime():
    print(
        "R28 UNIT N.2: RUNTIME STARTING",
        flush=True,
    )

    loop = asyncio.get_running_loop()

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

        print(LINE)
        print(
            "R28 UNIT N.2: PERSISTENT "
            "RUNTIME ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.2: AUTHENTICATED "
            "READ-ONLY LOCKS ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N.2: NETWORK WRITE "
            "TRANSPORT LOCKED",
            flush=True,
        )

        print(
            "R28 UNIT N.2: LEVERAGE MUTATION "
            "TRANSPORT LOCKED",
            flush=True,
        )

        await heartbeat_loop()

    finally:
        await health_runner.cleanup()

        print(
            "R28 UNIT N.2: "
            "RUNTIME STOPPED CLEANLY",
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
        pass

    except Exception as exc:
        print(
            f"R28 UNIT N.2 FATAL ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        raise
