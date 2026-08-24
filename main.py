# ============================================================
# 0F-4H-R28-UNIT-N.4
# CONTROLLED LEVERAGE-MUTATION TRANSPORT PREFLIGHT
#
# PURPOSE
# ------------------------------------------------------------
# Validate the complete transport preparation chain for:
#
#   POST /capi/v3/account/leverage
#
# WITHOUT transmitting the mutation.
#
# THIS UNIT:
#   ✅ performs public server-time GET
#   ✅ performs authenticated symbol-config GET
#   ✅ validates current BTCUSDT configuration
#   ✅ constructs exact leverage payload
#   ✅ constructs exact WEEX POST signature
#   ✅ constructs explicit local authorization
#   ✅ binds authorization to exact payload SHA256
#   ✅ validates authorization expiry
#   ✅ validates replay protection
#   ✅ constructs final HTTP headers
#   ✅ validates final URL / method / body / headers
#   ✅ reaches the transport boundary
#   ✅ blocks the POST locally
#   ✅ proves network POST count remains zero
#
# THIS UNIT DOES NOT:
#   ❌ change leverage
#   ❌ send any POST request
#   ❌ place any order
#   ❌ modify account state
#   ❌ enable live execution
#
# ============================================================

print(
    "R28 UNIT N.4: MAIN.PY ENTERED",
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
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Set, Tuple

print(
    "R28 UNIT N.4: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-N.4"
MODULE_VERSION = "R28-N.4"

SYMBOL = "BTCUSDT"

API_BASE_URL = "https://api-contract.weex.com"

SERVER_TIME_PATH = "/capi/v3/market/time"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

LEVERAGE_METHOD = "POST"
LEVERAGE_PATH = "/capi/v3/account/leverage"

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = "100"
TARGET_SHORT_LEVERAGE = "100"

LOCAL_MAX_LEVERAGE = Decimal("100")

REQUEST_TIMEOUT_SECONDS = 10
AUTHORIZATION_TTL_SECONDS = 30

HEARTBEAT_INTERVAL_SECONDS = 15

print(
    "R28 UNIT N.4: CONSTANTS INITIALIZED",
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

PUBLIC_GET_ENABLED = True
AUTHENTICATED_READ_ONLY_GET_ENABLED = True

# Absolute transport rule:
#
# No function in this program is permitted to send POST / PUT /
# PATCH / DELETE traffic.
#
# N.4 is a PREFLIGHT unit only.

ALLOW_NETWORK_POST = False
ALLOW_NETWORK_PUT = False
ALLOW_NETWORK_PATCH = False
ALLOW_NETWORK_DELETE = False


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
    or ""
).strip()


# ============================================================
# RUNTIME STATE
# ============================================================

shutdown_event = threading.Event()

network_get_count = 0

network_post_count = 0
network_put_count = 0
network_patch_count = 0
network_delete_count = 0

account_write_transmission_count = 0
leverage_change_transmission_count = 0

real_order_transmission_count = 0
demo_order_transmission_count = 0

local_post_attempt_count = 0
local_post_block_count = 0

authorization_request_count = 0
authorization_grant_count = 0
authorization_denial_count = 0
authorization_replay_block_count = 0

used_authorization_ids: Set[str] = set()

structural_safety_failures = 0
readiness_blockers = 0


# ============================================================
# FORMATTING
# ============================================================

WIDTH = 76


def separator() -> None:
    print(
        "-" * WIDTH,
        flush=True,
    )


def major_separator() -> None:
    print(
        "=" * WIDTH,
        flush=True,
    )


def result(
    label: str,
    passed: bool,
) -> bool:
    global structural_safety_failures

    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<68}{status}",
        flush=True,
    )

    if not passed:
        structural_safety_failures += 1

    return passed


def readiness_result(
    label: str,
    passed: bool,
) -> bool:
    global readiness_blockers

    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<68}{status}",
        flush=True,
    )

    if not passed:
        readiness_blockers += 1

    return passed


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        body = (
            b"R28 UNIT N.4 ACTIVE\n"
            b"LEVERAGE MUTATION TRANSPORT LOCKED\n"
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

    except ValueError:
        port = 10000

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
        f"R28 UNIT N.4: HEALTH SERVER ACTIVE ON PORT {port}",
        flush=True,
    )


# ============================================================
# JSON / HASH HELPERS
# ============================================================

def canonical_json(
    value: Dict[str, Any],
) -> str:

    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=False,
        ensure_ascii=False,
    )


def sha256_hex(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


# ============================================================
# WEEX SIGNATURE
# ============================================================

def create_weex_signature(
    timestamp_ms: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    if query_string:

        prehash = (
            timestamp_ms
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        prehash = (
            timestamp_ms
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def authenticated_headers(
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
    timestamp_ms: Optional[str] = None,
) -> Dict[str, str]:

    if timestamp_ms is None:
        timestamp_ms = str(
            int(time.time() * 1000)
        )

    signature = create_weex_signature(
        timestamp_ms=timestamp_ms,
        method=method,
        request_path=path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "Content-Type": "application/json",
    }


# ============================================================
# NETWORK READ-ONLY GET
# ============================================================

def public_get_json(
    path: str,
    query_string: str = "",
) -> Any:

    global network_get_count

    if not PUBLIC_GET_ENABLED:
        raise RuntimeError(
            "Public GET disabled."
        )

    url = API_BASE_URL + path

    if query_string:
        url += "?" + query_string

    print(
        f"R28 UNIT N.4: PUBLIC GET -> "
        f"{path}"
        + (
            f"?{query_string}"
            if query_string
            else ""
        ),
        flush=True,
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Content-Type": "application/json",
            "User-Agent": MODULE_NAME,
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            network_get_count += 1

            return json.loads(raw)

    except urllib.error.HTTPError as exc:

        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {body}"
        )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Network GET failed: {exc}"
        )


def authenticated_get_json(
    path: str,
    query_string: str = "",
) -> Any:

    global network_get_count

    if not AUTHENTICATED_READ_ONLY_GET_ENABLED:
        raise RuntimeError(
            "Authenticated GET disabled."
        )

    timestamp_ms = str(
        int(time.time() * 1000)
    )

    headers = authenticated_headers(
        method="GET",
        path=path,
        query_string=query_string,
        body="",
        timestamp_ms=timestamp_ms,
    )

    url = API_BASE_URL + path

    if query_string:
        url += "?" + query_string

    print(
        f"R28 UNIT N.4: AUTHENTICATED GET -> "
        f"{path}"
        + (
            f"?{query_string}"
            if query_string
            else ""
        ),
        flush=True,
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            network_get_count += 1

            return json.loads(raw)

    except urllib.error.HTTPError as exc:

        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {body}"
        )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Authenticated GET failed: {exc}"
        )


# ============================================================
# SERVER TIME PARSER
# ============================================================

def extract_server_time(
    response: Any,
) -> Optional[int]:

    candidates = []

    if isinstance(response, int):
        candidates.append(response)

    if isinstance(response, str):
        candidates.append(response)

    if isinstance(response, dict):

        for key in (
            "serverTime",
            "time",
            "timestamp",
            "requestTime",
        ):
            if key in response:
                candidates.append(
                    response[key]
                )

        data = response.get("data")

        if isinstance(data, dict):

            for key in (
                "serverTime",
                "time",
                "timestamp",
                "requestTime",
            ):
                if key in data:
                    candidates.append(
                        data[key]
                    )

        elif data is not None:
            candidates.append(data)

    for candidate in candidates:

        try:

            parsed = int(candidate)

            if parsed > 1_000_000_000_000:
                return parsed

        except (
            TypeError,
            ValueError,
        ):
            pass

    return None


# ============================================================
# SYMBOL CONFIG PARSER
# ============================================================

def find_symbol_config(
    response: Any,
) -> Optional[Dict[str, Any]]:

    records = []

    if isinstance(response, list):
        records = response

    elif isinstance(response, dict):

        data = response.get("data")

        if isinstance(data, list):
            records = data

        elif isinstance(data, dict):
            records = [data]

        else:
            records = [response]

    for record in records:

        if not isinstance(
            record,
            dict,
        ):
            continue

        if str(
            record.get(
                "symbol",
                "",
            )
        ).upper() == SYMBOL:

            return record

    return None


# ============================================================
# LEVERAGE PAYLOAD
# ============================================================

def build_leverage_payload() -> Dict[str, str]:

    return {
        "symbol": SYMBOL,
        "marginType": TARGET_MARGIN_TYPE,
        "isolatedLongLeverage": TARGET_LONG_LEVERAGE,
        "isolatedShortLeverage": TARGET_SHORT_LEVERAGE,
    }


# ============================================================
# LOCAL MUTATION AUTHORIZATION
# ============================================================

@dataclass(frozen=True)
class MutationAuthorization:
    authorization_id: str
    module_name: str
    method: str
    path: str
    symbol: str
    margin_type: str
    long_leverage: str
    short_leverage: str
    payload_sha256: str
    issued_at_ms: int
    expires_at_ms: int
    proof: str


def authorization_material(
    authorization_id: str,
    issued_at_ms: int,
    expires_at_ms: int,
    payload_hash: str,
) -> str:

    return "|".join(
        [
            authorization_id,
            MODULE_NAME,
            LEVERAGE_METHOD,
            LEVERAGE_PATH,
            SYMBOL,
            TARGET_MARGIN_TYPE,
            TARGET_LONG_LEVERAGE,
            TARGET_SHORT_LEVERAGE,
            payload_hash,
            str(issued_at_ms),
            str(expires_at_ms),
        ]
    )


def create_local_authorization(
    payload_body: str,
) -> MutationAuthorization:

    issued_at_ms = int(
        time.time() * 1000
    )

    expires_at_ms = (
        issued_at_ms
        + AUTHORIZATION_TTL_SECONDS
        * 1000
    )

    payload_hash = sha256_hex(
        payload_body
    )

    authorization_seed = (
        MODULE_NAME
        + "|"
        + payload_hash
        + "|"
        + str(issued_at_ms)
        + "|"
        + os.urandom(16).hex()
    )

    authorization_id = sha256_hex(
        authorization_seed
    )

    material = authorization_material(
        authorization_id=authorization_id,
        issued_at_ms=issued_at_ms,
        expires_at_ms=expires_at_ms,
        payload_hash=payload_hash,
    )

    proof = hmac.new(
        API_SECRET.encode("utf-8"),
        material.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return MutationAuthorization(
        authorization_id=authorization_id,
        module_name=MODULE_NAME,
        method=LEVERAGE_METHOD,
        path=LEVERAGE_PATH,
        symbol=SYMBOL,
        margin_type=TARGET_MARGIN_TYPE,
        long_leverage=TARGET_LONG_LEVERAGE,
        short_leverage=TARGET_SHORT_LEVERAGE,
        payload_sha256=payload_hash,
        issued_at_ms=issued_at_ms,
        expires_at_ms=expires_at_ms,
        proof=proof,
    )


def validate_local_authorization(
    authorization: Optional[
        MutationAuthorization
    ],
    payload_body: str,
    consume: bool = True,
) -> Tuple[bool, str]:

    global authorization_request_count
    global authorization_grant_count
    global authorization_denial_count
    global authorization_replay_block_count

    authorization_request_count += 1

    if authorization is None:

        authorization_denial_count += 1

        return (
            False,
            "missing authorization",
        )

    if (
        authorization.authorization_id
        in used_authorization_ids
    ):

        authorization_denial_count += 1
        authorization_replay_block_count += 1

        return (
            False,
            "authorization replay blocked",
        )

    now_ms = int(
        time.time() * 1000
    )

    if now_ms > authorization.expires_at_ms:

        authorization_denial_count += 1

        return (
            False,
            "authorization expired",
        )

    expected_payload_hash = sha256_hex(
        payload_body
    )

    checks = [
        (
            authorization.module_name
            == MODULE_NAME
        ),
        (
            authorization.method
            == LEVERAGE_METHOD
        ),
        (
            authorization.path
            == LEVERAGE_PATH
        ),
        (
            authorization.symbol
            == SYMBOL
        ),
        (
            authorization.margin_type
            == TARGET_MARGIN_TYPE
        ),
        (
            authorization.long_leverage
            == TARGET_LONG_LEVERAGE
        ),
        (
            authorization.short_leverage
            == TARGET_SHORT_LEVERAGE
        ),
        (
            authorization.payload_sha256
            == expected_payload_hash
        ),
    ]

    if not all(checks):

        authorization_denial_count += 1

        return (
            False,
            "authorization binding mismatch",
        )

    material = authorization_material(
        authorization_id=(
            authorization.authorization_id
        ),
        issued_at_ms=(
            authorization.issued_at_ms
        ),
        expires_at_ms=(
            authorization.expires_at_ms
        ),
        payload_hash=(
            authorization.payload_sha256
        ),
    )

    expected_proof = hmac.new(
        API_SECRET.encode("utf-8"),
        material.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        authorization.proof,
        expected_proof,
    ):

        authorization_denial_count += 1

        return (
            False,
            "invalid authorization proof",
        )

    if consume:

        used_authorization_ids.add(
            authorization.authorization_id
        )

    authorization_grant_count += 1

    return (
        True,
        "authorized locally",
    )


# ============================================================
# FINAL TRANSPORT ENVELOPE
# ============================================================

@dataclass(frozen=True)
class TransportEnvelope:
    method: str
    url: str
    path: str
    body: str
    body_sha256: str
    timestamp_ms: str
    headers: Dict[str, str]


def build_transport_envelope(
    payload_body: str,
) -> TransportEnvelope:

    timestamp_ms = str(
        int(time.time() * 1000)
    )

    headers = authenticated_headers(
        method=LEVERAGE_METHOD,
        path=LEVERAGE_PATH,
        query_string="",
        body=payload_body,
        timestamp_ms=timestamp_ms,
    )

    return TransportEnvelope(
        method=LEVERAGE_METHOD,
        url=(
            API_BASE_URL
            + LEVERAGE_PATH
        ),
        path=LEVERAGE_PATH,
        body=payload_body,
        body_sha256=sha256_hex(
            payload_body
        ),
        timestamp_ms=timestamp_ms,
        headers=headers,
    )


# ============================================================
# HARD WRITE TRANSPORT BLOCK
# ============================================================

def blocked_post_transport(
    envelope: TransportEnvelope,
    authorization: MutationAuthorization,
) -> None:

    global local_post_attempt_count
    global local_post_block_count

    local_post_attempt_count += 1

    authorized, reason = (
        validate_local_authorization(
            authorization=authorization,
            payload_body=envelope.body,
            consume=True,
        )
    )

    if not authorized:

        raise RuntimeError(
            "R28 UNIT N.4 LOCAL AUTHORIZATION BLOCK: "
            + reason
        )

    # ========================================================
    # ABSOLUTE TRANSPORT INTERLOCK
    # ========================================================
    #
    # Even a correctly signed and correctly authorized request
    # is NOT permitted to cross the network boundary in N.4.
    #
    # No urllib Request is constructed here.
    # No socket write is attempted.
    # No POST is transmitted.
    # ========================================================

    if (
        not NETWORK_WRITES_ENABLED
        or not ACCOUNT_WRITES_ENABLED
        or not LEVERAGE_WRITES_ENABLED
        or not LEVERAGE_MUTATION_TRANSPORT_ENABLED
        or not ALLOW_NETWORK_POST
    ):

        local_post_block_count += 1

        raise RuntimeError(
            "R28 UNIT N.4 LOCAL TRANSPORT BLOCK: "
            "network write transport locked."
        )

    # This branch must remain unreachable in Unit N.4.

    raise RuntimeError(
        "R28 UNIT N.4 SAFETY VIOLATION: "
        "write transport unexpectedly reachable."
    )


# ============================================================
# DIAGNOSTIC
# ============================================================

def run_diagnostic() -> None:

    global readiness_blockers

    major_separator()

    print(
        "0F-4H-R28-UNIT-N.4 STARTING",
        flush=True,
    )

    print(
        "CONTROLLED LEVERAGE-MUTATION TRANSPORT PREFLIGHT",
        flush=True,
    )

    print(
        "AUTHENTICATED READ-ONLY ACCOUNT STATE ENABLED",
        flush=True,
    )

    print(
        "SIGNED POST ENVELOPE CONSTRUCTION ENABLED",
        flush=True,
    )

    print(
        "ACTUAL NETWORK POST TRANSPORT HARD-LOCKED",
        flush=True,
    )

    print(
        "NO LEVERAGE CHANGE WILL BE TRANSMITTED",
        flush=True,
    )

    major_separator()

    print()

    # ========================================================
    # CREDENTIAL STATUS
    # ========================================================

    print(
        "R28 UNIT N.4 CREDENTIAL STATUS",
        flush=True,
    )

    separator()

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

    credentials_present = bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )

    readiness_result(
        "Required API Credentials Present",
        credentials_present,
    )

    print()

    # ========================================================
    # ABSOLUTE SAFETY GATES
    # ========================================================

    print(
        "R28 UNIT N.4 ABSOLUTE SAFETY GATES",
        flush=True,
    )

    separator()

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
        LEVERAGE_MUTATION_TRANSPORT_ENABLED
        is False,
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

    result(
        "Network POST Hard Lock Active",
        ALLOW_NETWORK_POST is False,
    )

    result(
        "Network PUT Hard Lock Active",
        ALLOW_NETWORK_PUT is False,
    )

    result(
        "Network PATCH Hard Lock Active",
        ALLOW_NETWORK_PATCH is False,
    )

    result(
        "Network DELETE Hard Lock Active",
        ALLOW_NETWORK_DELETE is False,
    )

    print()

    # ========================================================
    # TARGET PAYLOAD
    # ========================================================

    payload = build_leverage_payload()

    payload_body = canonical_json(
        payload
    )

    payload_hash = sha256_hex(
        payload_body
    )

    print(
        "R28 UNIT N.4 MUTATION PREFLIGHT TARGET",
        flush=True,
    )

    separator()

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
        f"  Margin Type = "
        f"{TARGET_MARGIN_TYPE}",
        flush=True,
    )

    print(
        f"  Target Long Leverage = "
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Target Short Leverage = "
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Exact JSON Body = "
        f"{payload_body}",
        flush=True,
    )

    print(
        f"  Payload SHA256 = "
        f"{payload_hash}",
        flush=True,
    )

    try:

        long_leverage = Decimal(
            TARGET_LONG_LEVERAGE
        )

        short_leverage = Decimal(
            TARGET_SHORT_LEVERAGE
        )

        leverage_parseable = True

    except InvalidOperation:

        long_leverage = Decimal("0")
        short_leverage = Decimal("0")

        leverage_parseable = False

    readiness_result(
        "Target Leverages Parseable",
        leverage_parseable,
    )

    readiness_result(
        "Target Long Leverage Positive",
        long_leverage > 0,
    )

    readiness_result(
        "Target Short Leverage Positive",
        short_leverage > 0,
    )

    readiness_result(
        "Target Long Within Local 100x Cap",
        (
            long_leverage
            <= LOCAL_MAX_LEVERAGE
        ),
    )

    readiness_result(
        "Target Short Within Local 100x Cap",
        (
            short_leverage
            <= LOCAL_MAX_LEVERAGE
        ),
    )

    readiness_result(
        "Leverage Method Is POST",
        LEVERAGE_METHOD == "POST",
    )

    readiness_result(
        "Leverage Path Is Contract V3",
        (
            LEVERAGE_PATH
            == "/capi/v3/account/leverage"
        ),
    )

    readiness_result(
        "Target Margin Mode Is ISOLATED",
        TARGET_MARGIN_TYPE
        == "ISOLATED",
    )

    print()

    # ========================================================
    # SERVER CLOCK
    # ========================================================

    print(
        "R28 UNIT N.4 SERVER-CLOCK VALIDATION",
        flush=True,
    )

    separator()

    server_time_ms = None

    if credentials_present:

        try:

            time_response = public_get_json(
                SERVER_TIME_PATH
            )

            result(
                "WEEX Server Time Read",
                True,
            )

            server_time_ms = (
                extract_server_time(
                    time_response
                )
            )

            result(
                "WEEX Server Time Parseable",
                server_time_ms
                is not None,
            )

            if server_time_ms is not None:

                local_time_ms = int(
                    time.time() * 1000
                )

                clock_delta_ms = abs(
                    local_time_ms
                    - server_time_ms
                )

                print(
                    f"  WEEX Server Time = "
                    f"{server_time_ms}",
                    flush=True,
                )

                print(
                    f"  Approx Clock Delta = "
                    f"{clock_delta_ms} ms",
                    flush=True,
                )

                readiness_result(
                    "Clock Delta Within 30 Seconds",
                    clock_delta_ms
                    <= 30_000,
                )

        except Exception as exc:

            result(
                "WEEX Server Time Read",
                False,
            )

            print(
                f"  ERROR: {exc}",
                flush=True,
            )

            readiness_blockers += 1

    else:

        print(
            "  SKIPPED: credentials missing",
            flush=True,
        )

        readiness_blockers += 1

    print()

    # ========================================================
    # AUTHENTICATED CONFIG READ
    # ========================================================

    print(
        "R28 UNIT N.4 AUTHENTICATED CONFIGURATION READ",
        flush=True,
    )

    separator()

    symbol_config = None

    if credentials_present:

        try:

            query_string = urllib.parse.urlencode(
                {
                    "symbol": SYMBOL,
                }
            )

            config_response = (
                authenticated_get_json(
                    SYMBOL_CONFIG_PATH,
                    query_string,
                )
            )

            result(
                "Authenticated Symbol Config Read",
                True,
            )

            symbol_config = find_symbol_config(
                config_response
            )

            result(
                "BTCUSDT Symbol Config Located",
                symbol_config
                is not None,
            )

        except Exception as exc:

            result(
                "Authenticated Symbol Config Read",
                False,
            )

            print(
                f"  ERROR: {exc}",
                flush=True,
            )

            readiness_blockers += 1

    if symbol_config is not None:

        observed_symbol = str(
            symbol_config.get(
                "symbol",
                "",
            )
        ).upper()

        observed_margin_type = str(
            symbol_config.get(
                "marginType",
                "",
            )
        ).upper()

        observed_position_mode = str(
            symbol_config.get(
                "separatedType",
                symbol_config.get(
                    "separatedMode",
                    "",
                ),
            )
        ).upper()

        cross_leverage = str(
            symbol_config.get(
                "crossLeverage",
                "",
            )
        )

        isolated_long = str(
            symbol_config.get(
                "isolatedLongLeverage",
                "",
            )
        )

        isolated_short = str(
            symbol_config.get(
                "isolatedShortLeverage",
                "",
            )
        )

        readiness_result(
            "Observed Symbol Matches BTCUSDT",
            observed_symbol
            == SYMBOL,
        )

        readiness_result(
            "Observed Margin Mode Is ISOLATED",
            observed_margin_type
            == TARGET_MARGIN_TYPE,
        )

        print(
            "R28 UNIT N.4 CURRENT SYMBOL CONFIG:",
            flush=True,
        )

        print(
            f"  Symbol = {observed_symbol}",
            flush=True,
        )

        print(
            f"  Margin Type = "
            f"{observed_margin_type}",
            flush=True,
        )

        print(
            f"  Position Mode = "
            f"{observed_position_mode}",
            flush=True,
        )

        print(
            f"  Cross Leverage = "
            f"{cross_leverage}x",
            flush=True,
        )

        print(
            f"  Isolated Long Leverage = "
            f"{isolated_long}x",
            flush=True,
        )

        print(
            f"  Isolated Short Leverage = "
            f"{isolated_short}x",
            flush=True,
        )

        already_target = (
            isolated_long
            == TARGET_LONG_LEVERAGE
            and isolated_short
            == TARGET_SHORT_LEVERAGE
        )

        print(
            "  Mutation Required = "
            + (
                "NO"
                if already_target
                else "YES"
            ),
            flush=True,
        )

    print()

    # ========================================================
    # AUTHORIZATION CONSTRUCTION
    # ========================================================

    print(
        "R28 UNIT N.4 AUTHORIZATION CONSTRUCTION",
        flush=True,
    )

    separator()

    authorization = (
        create_local_authorization(
            payload_body
        )
    )

    result(
        "Authorization ID Generated",
        bool(
            authorization.authorization_id
        ),
    )

    result(
        "Authorization Bound To Module",
        (
            authorization.module_name
            == MODULE_NAME
        ),
    )

    result(
        "Authorization Bound To POST",
        (
            authorization.method
            == LEVERAGE_METHOD
        ),
    )

    result(
        "Authorization Bound To Exact Path",
        (
            authorization.path
            == LEVERAGE_PATH
        ),
    )

    result(
        "Authorization Bound To Symbol",
        (
            authorization.symbol
            == SYMBOL
        ),
    )

    result(
        "Authorization Bound To Margin Type",
        (
            authorization.margin_type
            == TARGET_MARGIN_TYPE
        ),
    )

    result(
        "Authorization Bound To Long Leverage",
        (
            authorization.long_leverage
            == TARGET_LONG_LEVERAGE
        ),
    )

    result(
        "Authorization Bound To Short Leverage",
        (
            authorization.short_leverage
            == TARGET_SHORT_LEVERAGE
        ),
    )

    result(
        "Authorization Bound To Exact Payload Hash",
        (
            authorization.payload_sha256
            == payload_hash
        ),
    )

    result(
        "Authorization Has Expiry",
        (
            authorization.expires_at_ms
            > authorization.issued_at_ms
        ),
    )

    result(
        "Authorization Proof Generated",
        bool(
            authorization.proof
        ),
    )

    print()

    # ========================================================
    # FINAL SIGNED TRANSPORT ENVELOPE
    # ========================================================

    print(
        "R28 UNIT N.4 SIGNED TRANSPORT ENVELOPE",
        flush=True,
    )

    separator()

    envelope = build_transport_envelope(
        payload_body
    )

    print(
        f"  Method = {envelope.method}",
        flush=True,
    )

    print(
        f"  URL = {envelope.url}",
        flush=True,
    )

    print(
        f"  Timestamp = "
        f"{envelope.timestamp_ms}",
        flush=True,
    )

    print(
        f"  Body SHA256 = "
        f"{envelope.body_sha256}",
        flush=True,
    )

    print(
        "  ACCESS-KEY = "
        + (
            "✅ PRESENT"
            if envelope.headers.get(
                "ACCESS-KEY"
            )
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  ACCESS-SIGN = "
        + (
            "✅ GENERATED"
            if envelope.headers.get(
                "ACCESS-SIGN"
            )
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  ACCESS-PASSPHRASE = "
        + (
            "✅ PRESENT"
            if envelope.headers.get(
                "ACCESS-PASSPHRASE"
            )
            else "❌ MISSING"
        ),
        flush=True,
    )

    print(
        "  ACCESS-TIMESTAMP = "
        + (
            "✅ PRESENT"
            if envelope.headers.get(
                "ACCESS-TIMESTAMP"
            )
            else "❌ MISSING"
        ),
        flush=True,
    )

    readiness_result(
        "Transport Method Exactly POST",
        envelope.method == "POST",
    )

    readiness_result(
        "Transport Path Exactly Leverage Endpoint",
        (
            envelope.path
            == LEVERAGE_PATH
        ),
    )

    readiness_result(
        "Transport URL Host Locked To WEEX Contract API",
        envelope.url.startswith(
            "https://api-contract.weex.com/"
        ),
    )

    readiness_result(
        "Transport Body Exactly Matches Authorized Payload",
        envelope.body
        == payload_body,
    )

    readiness_result(
        "Transport Body Hash Matches Authorization",
        (
            envelope.body_sha256
            == authorization.payload_sha256
        ),
    )

    readiness_result(
        "Transport Signature Generated",
        bool(
            envelope.headers.get(
                "ACCESS-SIGN"
            )
        ),
    )

    readiness_result(
        "Transport Timestamp Generated",
        bool(
            envelope.headers.get(
                "ACCESS-TIMESTAMP"
            )
        ),
    )

    print()

    # ========================================================
    # PRE-TRANSPORT AUTHORIZATION CHECK
    # ========================================================

    print(
        "R28 UNIT N.4 PRE-TRANSPORT AUTHORIZATION TEST",
        flush=True,
    )

    separator()

    preflight_authorized, preflight_reason = (
        validate_local_authorization(
            authorization=authorization,
            payload_body=payload_body,
            consume=False,
        )
    )

    result(
        "Exact Transport Authorization Accepted",
        preflight_authorized,
    )

    print(
        f"  Authorization Result = "
        f"{preflight_reason}",
        flush=True,
    )

    print()

    # ========================================================
    # FINAL TRANSPORT BOUNDARY
    # ========================================================

    print(
        "R28 UNIT N.4 FINAL TRANSPORT-BOUNDARY TEST",
        flush=True,
    )

    separator()

    transport_was_blocked = False

    try:

        blocked_post_transport(
            envelope=envelope,
            authorization=authorization,
        )

    except RuntimeError as exc:

        message = str(exc)

        print(
            "R28 UNIT N.4 LOCAL BLOCK:",
            flush=True,
        )

        print(
            f"  {message}",
            flush=True,
        )

        transport_was_blocked = (
            "network write transport locked"
            in message
        )

    result(
        "Authorized Signed Leverage POST Blocked Locally",
        transport_was_blocked,
    )

    result(
        "Authorization Consumed At Transport Boundary",
        (
            authorization.authorization_id
            in used_authorization_ids
        ),
    )

    # ========================================================
    # REPLAY CHECK
    # ========================================================

    replay_allowed, replay_reason = (
        validate_local_authorization(
            authorization=authorization,
            payload_body=payload_body,
            consume=True,
        )
    )

    result(
        "Transport Authorization Replay Rejected",
        replay_allowed is False,
    )

    print(
        f"  Replay Result = "
        f"{replay_reason}",
        flush=True,
    )

    print()

    # ========================================================
    # WRITE LOCK AUDIT
    # ========================================================

    print(
        "R28 UNIT N.4 WRITE-LOCK AUDIT",
        flush=True,
    )

    separator()

    result(
        "Network POST Count Is Zero",
        network_post_count == 0,
    )

    result(
        "Network PUT Count Is Zero",
        network_put_count == 0,
    )

    result(
        "Network PATCH Count Is Zero",
        network_patch_count == 0,
    )

    result(
        "Network DELETE Count Is Zero",
        network_delete_count == 0,
    )

    result(
        "Account Write Transmission Count Is Zero",
        account_write_transmission_count
        == 0,
    )

    result(
        "Leverage Change Transmission Count Is Zero",
        leverage_change_transmission_count
        == 0,
    )

    result(
        "Real Order Transmission Count Is Zero",
        real_order_transmission_count
        == 0,
    )

    result(
        "Demo Order Transmission Count Is Zero",
        demo_order_transmission_count
        == 0,
    )

    result(
        "Exactly One Local POST Attempt Occurred",
        local_post_attempt_count == 1,
    )

    result(
        "Exactly One Local POST Block Occurred",
        local_post_block_count == 1,
    )

    result(
        "Authorization Replay Was Blocked",
        authorization_replay_block_count
        >= 1,
    )

    print()

    # ========================================================
    # AUDIT COUNTERS
    # ========================================================

    print(
        "R28 UNIT N.4 TRANSPORT AUDIT:",
        flush=True,
    )

    print(
        f"  Network GETs = "
        f"{network_get_count}",
        flush=True,
    )

    print(
        f"  Authorization requests = "
        f"{authorization_request_count}",
        flush=True,
    )

    print(
        f"  Authorization grants = "
        f"{authorization_grant_count}",
        flush=True,
    )

    print(
        f"  Authorization denials = "
        f"{authorization_denial_count}",
        flush=True,
    )

    print(
        f"  Authorization replays blocked = "
        f"{authorization_replay_block_count}",
        flush=True,
    )

    print(
        f"  Local POST attempts = "
        f"{local_post_attempt_count}",
        flush=True,
    )

    print(
        f"  Local POST blocks = "
        f"{local_post_block_count}",
        flush=True,
    )

    print(
        f"  Network POSTs = "
        f"{network_post_count}",
        flush=True,
    )

    print(
        f"  Leverage change transmissions = "
        f"{leverage_change_transmission_count}",
        flush=True,
    )

    print()

    # ========================================================
    # READINESS ASSESSMENT
    # ========================================================

    print(
        "R28 UNIT N.4 EXECUTION-READINESS ASSESSMENT",
        flush=True,
    )

    separator()

    print(
        f"Structural Safety Failures = "
        f"{structural_safety_failures}",
        flush=True,
    )

    print(
        f"Readiness Blockers = "
        f"{readiness_blockers}",
        flush=True,
    )

    authorization_verified = (
        preflight_authorized
    )

    payload_binding_verified = (
        envelope.body_sha256
        == authorization.payload_sha256
    )

    signing_verified = bool(
        envelope.headers.get(
            "ACCESS-SIGN"
        )
    )

    transport_boundary_verified = (
        transport_was_blocked
        and network_post_count == 0
    )

    replay_verified = (
        replay_allowed is False
    )

    print(
        "Exact Payload Construction = "
        + (
            "✅ VERIFIED"
            if payload_binding_verified
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "WEEX Signature Construction = "
        + (
            "✅ VERIFIED"
            if signing_verified
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Mutation Authorization = "
        + (
            "✅ VERIFIED"
            if authorization_verified
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Authorization Replay Protection = "
        + (
            "✅ VERIFIED"
            if replay_verified
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Transport Boundary = "
        + (
            "✅ VERIFIED"
            if transport_boundary_verified
            else "❌ FAILED"
        ),
        flush=True,
    )

    print(
        "Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY",
        flush=True,
    )

    overall_pass = (
        structural_safety_failures == 0
        and readiness_blockers == 0
        and authorization_verified
        and payload_binding_verified
        and signing_verified
        and transport_boundary_verified
        and replay_verified
        and network_post_count == 0
        and leverage_change_transmission_count == 0
    )

    print()

    if overall_pass:

        print(
            "✅ R28 UNIT N.4 DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ EXACT LEVERAGE PAYLOAD PREFLIGHT VERIFIED",
            flush=True,
        )

        print(
            "✅ WEEX POST SIGNATURE CONSTRUCTION VERIFIED",
            flush=True,
        )

        print(
            "✅ AUTHORIZATION / PAYLOAD BINDING VERIFIED",
            flush=True,
        )

        print(
            "✅ TRANSPORT ENVELOPE VERIFIED",
            flush=True,
        )

        print(
            "✅ AUTHORIZATION REPLAY LOCK VERIFIED",
            flush=True,
        )

        print(
            "✅ WRITE TRANSPORT BOUNDARY VERIFIED",
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
            "❌ R28 UNIT N.4 DIAGNOSTIC FAILED",
            flush=True,
        )

        print(
            "🛡 WRITE TRANSPORT REMAINS LOCKED",
            flush=True,
        )

        print(
            "🛡 NO NETWORK WRITE WAS TRANSMITTED",
            flush=True,
        )

    major_separator()


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop() -> None:

    counter = 1

    while not shutdown_event.is_set():

        print(
            f"R28 UNIT N.4: HEARTBEAT "
            f"{counter} ✅ ACTIVE",
            flush=True,
        )

        counter += 1

        shutdown_event.wait(
            HEARTBEAT_INTERVAL_SECONDS
        )


# ============================================================
# SIGNAL HANDLING
# ============================================================

def handle_shutdown(
    signum: int,
    frame: Any,
) -> None:

    print(
        "R28 UNIT N.4: SHUTDOWN REQUESTED",
        flush=True,
    )

    shutdown_event.set()


signal.signal(
    signal.SIGTERM,
    handle_shutdown,
)

signal.signal(
    signal.SIGINT,
    handle_shutdown,
)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print(
        "R28 UNIT N.4: RUNTIME STARTING",
        flush=True,
    )

    start_health_server()

    run_diagnostic()

    major_separator()

    print(
        "R28 UNIT N.4: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT N.4: AUTHENTICATED READ-ONLY LOCKS ACTIVE",
        flush=True,
    )

    print(
        "R28 UNIT N.4: SIGNED POST PREFLIGHT AVAILABLE",
        flush=True,
    )

    print(
        "R28 UNIT N.4: NETWORK WRITE TRANSPORT LOCKED",
        flush=True,
    )

    print(
        "R28 UNIT N.4: LEVERAGE MUTATION TRANSPORT LOCKED",
        flush=True,
    )

    print(
        "R28 UNIT N.4: AUTHORIZATION REPLAY LOCK ACTIVE",
        flush=True,
    )

    heartbeat_loop()

    print(
        "R28 UNIT N.4: RUNTIME STOPPED CLEANLY",
        flush=True,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print(
            "R28 UNIT N.4: FATAL ERROR",
            flush=True,
        )

        print(
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        sys.exit(1)
