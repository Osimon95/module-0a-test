# ============================================================
# 0F-4H-R28-UNIT-N
# LEVERAGE MUTATION AUTHORIZATION / WRITE-GATE VALIDATION
#
# PURPOSE:
#   - Read current BTCUSDT configuration using authenticated GET
#   - Detect leverage gap against required configuration
#   - Build hypothetical leverage mutation
#   - Validate strict mutation authorization gates
#   - Validate payload integrity / binding
#   - Validate symbol / margin / leverage scope
#   - Validate replay protection
#   - Prove leverage POST is blocked locally
#   - Prove ZERO network writes occur
#
# IMPORTANT:
#   REAL ORDER TRANSMISSION DISABLED
#   DEMO ORDER TRANSMISSION DISABLED
#   ACCOUNT WRITE TRANSMISSION DISABLED
#   LEVERAGE WRITE TRANSMISSION DISABLED
#
# AUTHENTICATED READ-ONLY GET IS ENABLED
# ============================================================


print(
    "R28 UNIT N: MAIN.PY ENTERED",
    flush=True,
)


# ============================================================
# IMPORTS
# ============================================================

import asyncio
import hashlib
import hmac
import json
import os
import signal
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Set
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


print(
    "R28 UNIT N: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# UNIT IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-N"
MODULE_VERSION = "R28-N"

SYMBOL = "BTCUSDT"

REQUIRED_MARGIN_TYPE = "ISOLATED"

REQUIRED_LONG_LEVERAGE = Decimal("100")
REQUIRED_SHORT_LEVERAGE = Decimal("100")

MAX_ALLOWED_LEVERAGE = Decimal("100")

print(
    "R28 UNIT N: CONSTANTS INITIALIZED",
    flush=True,
)


# ============================================================
# ABSOLUTE EXECUTION SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITE_ENABLED = False
ACCOUNT_WRITE_ENABLED = False
LEVERAGE_WRITE_ENABLED = False

AUTHENTICATED_READ_ONLY_ENABLED = True

REAL_ORDER_TRANSMISSION_ENABLED = False
DEMO_ORDER_TRANSMISSION_ENABLED = False

ALLOW_NETWORK_POST = False
ALLOW_NETWORK_PUT = False
ALLOW_NETWORK_PATCH = False
ALLOW_NETWORK_DELETE = False


# ============================================================
# UNIT N AUTHORIZATION POLICY
# ============================================================

LEVERAGE_MUTATION_FEATURE_ENABLED = False

EXPLICIT_MUTATION_AUTHORIZATION = False

REQUIRE_EXACT_SYMBOL = True
REQUIRE_ISOLATED_MARGIN = True
REQUIRE_EXACT_TARGET_LEVERAGE = True
REQUIRE_PAYLOAD_INTEGRITY = True
REQUIRE_REQUEST_BINDING = True
REQUIRE_NON_REPLAY = True

# Even if this were changed accidentally, the transport layer
# below STILL refuses every network write.
ALLOW_LEVERAGE_MUTATION_TRANSPORT = False


# ============================================================
# WEEX API CONFIGURATION
# ============================================================

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

LEVERAGE_WRITE_PATH = "/capi/v3/account/leverage"

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
    or os.getenv("WEEX_PASSPHRASE")
    or ""
).strip()


# ============================================================
# RUNTIME / HEALTH CONFIG
# ============================================================

PORT = int(os.getenv("PORT", "10000"))

HEARTBEAT_SECONDS = 15

shutdown_event = asyncio.Event()


# ============================================================
# TRANSPORT AUDIT COUNTERS
# ============================================================

network_get_count = 0
network_post_count = 0
network_put_count = 0
network_patch_count = 0
network_delete_count = 0

local_post_attempt_count = 0
local_post_block_count = 0

leverage_post_attempt_count = 0
leverage_post_block_count = 0

account_write_transmission_count = 0
leverage_change_transmission_count = 0

real_order_transmission_count = 0
demo_order_transmission_count = 0


# ============================================================
# AUTHORIZATION AUDIT COUNTERS
# ============================================================

authorization_attempt_count = 0
authorization_grant_count = 0
authorization_rejection_count = 0

accepted_request_ids: Set[str] = set()


# ============================================================
# BASIC HELPERS
# ============================================================

def separator():
    print(
        "-" * 76,
        flush=True,
    )


def print_gate(
    name: str,
    passed: bool,
):
    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{name:<68} {status}",
        flush=True,
    )

    return passed


def safe_decimal(
    value: Any,
) -> Optional[Decimal]:

    if value is None:
        return None

    try:
        text = str(value).strip()

        if not text:
            return None

        return Decimal(text)

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return None


def normalize_margin_type(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(value).strip().upper()


def normalize_symbol(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(value).strip().upper()


# ============================================================
# CREDENTIAL HELPERS
# ============================================================

def credentials_present() -> bool:

    return bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )


def print_credential_status():

    print(
        "R28 UNIT N CREDENTIAL STATUS:",
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
# WEEX SIGNING
# ============================================================

def canonical_query(
    params: Optional[Dict[str, Any]],
) -> str:

    if not params:
        return ""

    clean = {}

    for key, value in params.items():

        if value is None:
            continue

        clean[key] = str(value)

    return urlencode(
        sorted(
            clean.items(),
            key=lambda item: item[0],
        )
    )


def canonical_json_body(
    payload: Optional[Dict[str, Any]],
) -> str:

    if not payload:
        return ""

    return json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    )


def generate_signature(
    timestamp_ms: str,
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    request_path = path

    if query_string:
        request_path += "?" + query_string

    message = (
        timestamp_ms
        + method.upper()
        + request_path
        + body
    )

    return hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def authenticated_headers(
    method: str,
    path: str,
    query_string: str = "",
    body: str = "",
) -> Dict[str, str]:

    timestamp_ms = str(
        int(
            time.time() * 1000
        )
    )

    signature = generate_signature(
        timestamp_ms=timestamp_ms,
        method=method,
        path=path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
    }


# ============================================================
# NETWORK BOUNDARY
# ============================================================

async def authenticated_get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:

    global network_get_count

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated GET disabled locally."
        )

    if not credentials_present():
        raise RuntimeError(
            "Authenticated GET credentials unavailable."
        )

    if path != SYMBOL_CONFIG_PATH:
        raise RuntimeError(
            "Authenticated GET path not allowlisted."
        )

    query_string = canonical_query(params)

    headers = authenticated_headers(
        method="GET",
        path=path,
        query_string=query_string,
        body="",
    )

    url = WEEX_BASE_URL + path

    network_get_count += 1

    print(
        f"R28 UNIT N: AUTHENTICATED GET -> {path}",
        flush=True,
    )

    async with session.get(
        url,
        params=params,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status >= 400:
            raise RuntimeError(
                f"Authenticated GET failed: "
                f"HTTP {response.status}: {text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                "Authenticated GET returned non-JSON response."
            )


# ============================================================
# HARD WRITE TRANSPORT INTERCEPTOR
# ============================================================

async def blocked_network_post(
    path: str,
    payload: Dict[str, Any],
):

    global local_post_attempt_count
    global local_post_block_count
    global leverage_post_attempt_count
    global leverage_post_block_count

    local_post_attempt_count += 1

    if path == LEVERAGE_WRITE_PATH:
        leverage_post_attempt_count += 1

    # --------------------------------------------------------
    # ABSOLUTE LOCAL INTERCEPTION
    #
    # NO aiohttp POST IS CALLED HERE.
    # NO SOCKET WRITE IS ATTEMPTED.
    # --------------------------------------------------------

    local_post_block_count += 1

    if path == LEVERAGE_WRITE_PATH:
        leverage_post_block_count += 1

    raise PermissionError(
        "R28 UNIT N LOCAL WRITE LOCK: "
        "network POST transmission blocked."
    )


async def blocked_network_put(
    *args,
    **kwargs,
):

    raise PermissionError(
        "R28 UNIT N LOCAL WRITE LOCK: PUT blocked."
    )


async def blocked_network_patch(
    *args,
    **kwargs,
):

    raise PermissionError(
        "R28 UNIT N LOCAL WRITE LOCK: PATCH blocked."
    )


async def blocked_network_delete(
    *args,
    **kwargs,
):

    raise PermissionError(
        "R28 UNIT N LOCAL WRITE LOCK: DELETE blocked."
    )


# ============================================================
# SYMBOL CONFIG EXTRACTION
# ============================================================

def unwrap_payload(
    response: Any,
) -> Any:

    if isinstance(response, dict):

        if "data" in response:
            return response["data"]

        return response

    return response


def locate_symbol_record(
    raw_response: Any,
    symbol: str,
) -> Optional[Dict[str, Any]]:

    payload = unwrap_payload(
        raw_response
    )

    if isinstance(payload, dict):

        observed_symbol = normalize_symbol(
            payload.get("symbol")
        )

        if observed_symbol == symbol:
            return payload

        for value in payload.values():

            if isinstance(value, dict):

                if normalize_symbol(
                    value.get("symbol")
                ) == symbol:

                    return value

            if isinstance(value, list):

                for item in value:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    if normalize_symbol(
                        item.get("symbol")
                    ) == symbol:

                        return item

    if isinstance(payload, list):

        for item in payload:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if normalize_symbol(
                item.get("symbol")
            ) == symbol:

                return item

    return None


def first_present(
    record: Dict[str, Any],
    keys,
):

    for key in keys:

        if key in record:

            value = record.get(key)

            if value is not None:
                return value

    return None


def parse_symbol_configuration(
    record: Dict[str, Any],
) -> Dict[str, Any]:

    symbol = normalize_symbol(
        first_present(
            record,
            [
                "symbol",
                "symbolName",
            ],
        )
    )

    margin_type = normalize_margin_type(
        first_present(
            record,
            [
                "marginType",
                "marginMode",
                "margin_type",
            ],
        )
    )

    position_mode = str(
        first_present(
            record,
            [
                "positionMode",
                "positionType",
                "holdMode",
            ],
        )
        or ""
    ).strip().upper()

    cross_leverage = safe_decimal(
        first_present(
            record,
            [
                "crossLeverage",
                "crossMarginLeverage",
                "leverage",
            ],
        )
    )

    isolated_long = safe_decimal(
        first_present(
            record,
            [
                "isolatedLongLeverage",
                "longLeverage",
                "isolatedLongLever",
            ],
        )
    )

    isolated_short = safe_decimal(
        first_present(
            record,
            [
                "isolatedShortLeverage",
                "shortLeverage",
                "isolatedShortLever",
            ],
        )
    )

    return {
        "symbol": symbol,
        "margin_type": margin_type,
        "position_mode": position_mode,
        "cross_leverage": cross_leverage,
        "isolated_long_leverage": isolated_long,
        "isolated_short_leverage": isolated_short,
    }


# ============================================================
# MUTATION PROPOSAL
# ============================================================

@dataclass(frozen=True)
class LeverageMutationProposal:

    symbol: str

    margin_type: str

    isolated_long_leverage: str

    isolated_short_leverage: str

    reason: str


def build_required_proposal() -> LeverageMutationProposal:

    return LeverageMutationProposal(
        symbol=SYMBOL,
        margin_type=REQUIRED_MARGIN_TYPE,
        isolated_long_leverage=str(
            REQUIRED_LONG_LEVERAGE
        ),
        isolated_short_leverage=str(
            REQUIRED_SHORT_LEVERAGE
        ),
        reason=(
            "Align isolated leverage with "
            "R28 required configuration"
        ),
    )


def proposal_payload(
    proposal: LeverageMutationProposal,
) -> Dict[str, str]:

    return {
        "symbol":
            proposal.symbol,

        "marginType":
            proposal.margin_type,

        "isolatedLongLeverage":
            proposal.isolated_long_leverage,

        "isolatedShortLeverage":
            proposal.isolated_short_leverage,
    }


# ============================================================
# PROPOSAL INTEGRITY
# ============================================================

def proposal_digest(
    proposal: LeverageMutationProposal,
) -> str:

    canonical = json.dumps(
        {
            "symbol":
                proposal.symbol,

            "margin_type":
                proposal.margin_type,

            "isolated_long_leverage":
                proposal.isolated_long_leverage,

            "isolated_short_leverage":
                proposal.isolated_short_leverage,

            "reason":
                proposal.reason,
        },
        separators=(",", ":"),
        sort_keys=True,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def request_id_for_proposal(
    proposal: LeverageMutationProposal,
) -> str:

    digest = proposal_digest(
        proposal
    )

    return (
        "R28N-LEV-"
        + digest[:24].upper()
    )


# ============================================================
# AUTHORIZATION RESULT
# ============================================================

@dataclass(frozen=True)
class AuthorizationResult:

    authorized: bool

    reason: str

    request_id: str


# ============================================================
# MUTATION AUTHORIZATION GATE
# ============================================================

def authorize_leverage_mutation(
    proposal: LeverageMutationProposal,
    expected_digest: str,
    explicit_authorization: bool,
    consume_request: bool = False,
) -> AuthorizationResult:

    global authorization_attempt_count
    global authorization_grant_count
    global authorization_rejection_count

    authorization_attempt_count += 1

    request_id = request_id_for_proposal(
        proposal
    )

    # --------------------------------------------------------
    # GATE 1:
    # Mutation feature itself must be enabled.
    # Unit N keeps this FALSE.
    # --------------------------------------------------------

    if not LEVERAGE_MUTATION_FEATURE_ENABLED:

        authorization_rejection_count += 1

        return AuthorizationResult(
            authorized=False,
            reason=(
                "Leverage mutation feature disabled."
            ),
            request_id=request_id,
        )

    # --------------------------------------------------------
    # GATE 2:
    # Explicit authorization required.
    # --------------------------------------------------------

    if not explicit_authorization:

        authorization_rejection_count += 1

        return AuthorizationResult(
            authorized=False,
            reason=(
                "Explicit mutation authorization absent."
            ),
            request_id=request_id,
        )

    # --------------------------------------------------------
    # GATE 3:
    # Payload integrity.
    # --------------------------------------------------------

    if REQUIRE_PAYLOAD_INTEGRITY:

        actual_digest = proposal_digest(
            proposal
        )

        if not hmac.compare_digest(
            actual_digest,
            expected_digest,
        ):

            authorization_rejection_count += 1

            return AuthorizationResult(
                authorized=False,
                reason=(
                    "Proposal integrity validation failed."
                ),
                request_id=request_id,
            )

    # --------------------------------------------------------
    # GATE 4:
    # Exact symbol scope.
    # --------------------------------------------------------

    if REQUIRE_EXACT_SYMBOL:

        if normalize_symbol(
            proposal.symbol
        ) != SYMBOL:

            authorization_rejection_count += 1

            return AuthorizationResult(
                authorized=False,
                reason=(
                    "Mutation symbol outside authorized scope."
                ),
                request_id=request_id,
            )

    # --------------------------------------------------------
    # GATE 5:
    # Isolated margin only.
    # --------------------------------------------------------

    if REQUIRE_ISOLATED_MARGIN:

        if normalize_margin_type(
            proposal.margin_type
        ) != REQUIRED_MARGIN_TYPE:

            authorization_rejection_count += 1

            return AuthorizationResult(
                authorized=False,
                reason=(
                    "Mutation margin type outside "
                    "authorized scope."
                ),
                request_id=request_id,
            )

    # --------------------------------------------------------
    # GATE 6:
    # Valid leverage values.
    # --------------------------------------------------------

    long_leverage = safe_decimal(
        proposal.isolated_long_leverage
    )

    short_leverage = safe_decimal(
        proposal.isolated_short_leverage
    )

    if (
        long_leverage is None
        or short_leverage is None
    ):

        authorization_rejection_count += 1

        return AuthorizationResult(
            authorized=False,
            reason=(
                "Leverage value is not parseable."
            ),
            request_id=request_id,
        )

    if (
        long_leverage <= 0
        or short_leverage <= 0
    ):

        authorization_rejection_count += 1

        return AuthorizationResult(
            authorized=False,
            reason=(
                "Leverage value must be positive."
            ),
            request_id=request_id,
        )

    if (
        long_leverage > MAX_ALLOWED_LEVERAGE
        or short_leverage > MAX_ALLOWED_LEVERAGE
    ):

        authorization_rejection_count += 1

        return AuthorizationResult(
            authorized=False,
            reason=(
                "Leverage exceeds R28 local maximum."
            ),
            request_id=request_id,
        )

    # --------------------------------------------------------
    # GATE 7:
    # Exact expected target.
    # --------------------------------------------------------

    if REQUIRE_EXACT_TARGET_LEVERAGE:

        if (
            long_leverage
            != REQUIRED_LONG_LEVERAGE
            or short_leverage
            != REQUIRED_SHORT_LEVERAGE
        ):

            authorization_rejection_count += 1

            return AuthorizationResult(
                authorized=False,
                reason=(
                    "Requested leverage differs from "
                    "required R28 target."
                ),
                request_id=request_id,
            )

    # --------------------------------------------------------
    # GATE 8:
    # Replay protection.
    # --------------------------------------------------------

    if REQUIRE_NON_REPLAY:

        if request_id in accepted_request_ids:

            authorization_rejection_count += 1

            return AuthorizationResult(
                authorized=False,
                reason=(
                    "Duplicate mutation request rejected."
                ),
                request_id=request_id,
            )

    # --------------------------------------------------------
    # A request could only arrive here if the feature flag
    # were deliberately enabled.
    #
    # Even then NETWORK TRANSPORT REMAINS BLOCKED elsewhere.
    # --------------------------------------------------------

    if consume_request:

        accepted_request_ids.add(
            request_id
        )

    authorization_grant_count += 1

    return AuthorizationResult(
        authorized=True,
        reason=(
            "Local authorization gates satisfied."
        ),
        request_id=request_id,
    )


# ============================================================
# TRANSPORT DISPATCH GATE
# ============================================================

async def dispatch_leverage_mutation(
    proposal: LeverageMutationProposal,
    authorization: AuthorizationResult,
):

    if not authorization.authorized:

        raise PermissionError(
            "Mutation dispatch rejected: "
            + authorization.reason
        )

    if not NETWORK_WRITE_ENABLED:

        raise PermissionError(
            "NETWORK_WRITE_ENABLED is False."
        )

    if not ACCOUNT_WRITE_ENABLED:

        raise PermissionError(
            "ACCOUNT_WRITE_ENABLED is False."
        )

    if not LEVERAGE_WRITE_ENABLED:

        raise PermissionError(
            "LEVERAGE_WRITE_ENABLED is False."
        )

    if not ALLOW_LEVERAGE_MUTATION_TRANSPORT:

        raise PermissionError(
            "Leverage mutation transport disabled."
        )

    if not ALLOW_NETWORK_POST:

        raise PermissionError(
            "Network POST disabled."
        )

    # --------------------------------------------------------
    # Final transport function is STILL locally blocked.
    #
    # No real aiohttp POST exists anywhere in Unit N.
    # --------------------------------------------------------

    await blocked_network_post(
        LEVERAGE_WRITE_PATH,
        proposal_payload(
            proposal
        ),
    )


# ============================================================
# AUTHORIZATION SELF TESTS
# ============================================================

def run_authorization_tests():

    print()
    print(
        "R28 UNIT N AUTHORIZATION-GATE VALIDATION",
        flush=True,
    )

    separator()

    results = []

    base = build_required_proposal()

    base_digest = proposal_digest(
        base
    )

    # ========================================================
    # TEST 1
    # Deterministic proposal
    # ========================================================

    proposal_2 = build_required_proposal()

    results.append(
        print_gate(
            "Deterministic Mutation Proposal",
            base == proposal_2,
        )
    )

    # ========================================================
    # TEST 2
    # Deterministic request ID
    # ========================================================

    results.append(
        print_gate(
            "Deterministic Mutation Request ID",
            request_id_for_proposal(base)
            ==
            request_id_for_proposal(proposal_2),
        )
    )

    # ========================================================
    # TEST 3
    # Correct payload
    # ========================================================

    expected_payload = {
        "symbol":
            "BTCUSDT",

        "marginType":
            "ISOLATED",

        "isolatedLongLeverage":
            "100",

        "isolatedShortLeverage":
            "100",
    }

    results.append(
        print_gate(
            "Exact Required Mutation Payload",
            proposal_payload(base)
            ==
            expected_payload,
        )
    )

    # ========================================================
    # TEST 4
    # Feature-disabled gate
    # ========================================================

    result = authorize_leverage_mutation(
        proposal=base,
        expected_digest=base_digest,
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Feature-Disabled Mutation Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 5
    # Missing explicit authorization
    #
    # Temporarily allow feature through this test layer only.
    # Transport remains disabled.
    # ========================================================

    global LEVERAGE_MUTATION_FEATURE_ENABLED

    original_feature_state = (
        LEVERAGE_MUTATION_FEATURE_ENABLED
    )

    LEVERAGE_MUTATION_FEATURE_ENABLED = True

    result = authorize_leverage_mutation(
        proposal=base,
        expected_digest=base_digest,
        explicit_authorization=False,
    )

    results.append(
        print_gate(
            "Missing Explicit Authorization Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 6
    # Tampered symbol
    # ========================================================

    tampered_symbol = LeverageMutationProposal(
        symbol="ETHUSDT",
        margin_type="ISOLATED",
        isolated_long_leverage="100",
        isolated_short_leverage="100",
        reason=base.reason,
    )

    result = authorize_leverage_mutation(
        proposal=tampered_symbol,
        expected_digest=proposal_digest(
            tampered_symbol
        ),
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Wrong Symbol Mutation Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 7
    # Wrong margin mode
    # ========================================================

    wrong_margin = LeverageMutationProposal(
        symbol="BTCUSDT",
        margin_type="CROSS",
        isolated_long_leverage="100",
        isolated_short_leverage="100",
        reason=base.reason,
    )

    result = authorize_leverage_mutation(
        proposal=wrong_margin,
        expected_digest=proposal_digest(
            wrong_margin
        ),
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Cross-Margin Mutation Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 8
    # Excessive leverage
    # ========================================================

    excessive = LeverageMutationProposal(
        symbol="BTCUSDT",
        margin_type="ISOLATED",
        isolated_long_leverage="101",
        isolated_short_leverage="100",
        reason=base.reason,
    )

    result = authorize_leverage_mutation(
        proposal=excessive,
        expected_digest=proposal_digest(
            excessive
        ),
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Excessive Leverage Mutation Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 9
    # Zero leverage
    # ========================================================

    zero_leverage = LeverageMutationProposal(
        symbol="BTCUSDT",
        margin_type="ISOLATED",
        isolated_long_leverage="0",
        isolated_short_leverage="100",
        reason=base.reason,
    )

    result = authorize_leverage_mutation(
        proposal=zero_leverage,
        expected_digest=proposal_digest(
            zero_leverage
        ),
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Zero Leverage Mutation Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 10
    # Negative leverage
    # ========================================================

    negative_leverage = LeverageMutationProposal(
        symbol="BTCUSDT",
        margin_type="ISOLATED",
        isolated_long_leverage="-1",
        isolated_short_leverage="100",
        reason=base.reason,
    )

    result = authorize_leverage_mutation(
        proposal=negative_leverage,
        expected_digest=proposal_digest(
            negative_leverage
        ),
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Negative Leverage Mutation Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 11
    # Wrong target
    # ========================================================

    wrong_target = LeverageMutationProposal(
        symbol="BTCUSDT",
        margin_type="ISOLATED",
        isolated_long_leverage="50",
        isolated_short_leverage="20",
        reason=base.reason,
    )

    result = authorize_leverage_mutation(
        proposal=wrong_target,
        expected_digest=proposal_digest(
            wrong_target
        ),
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Non-Target Leverage Mutation Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 12
    # Integrity mismatch
    # ========================================================

    result = authorize_leverage_mutation(
        proposal=base,
        expected_digest="0" * 64,
        explicit_authorization=True,
    )

    results.append(
        print_gate(
            "Tampered Mutation Digest Rejected",
            not result.authorized,
        )
    )

    # ========================================================
    # TEST 13
    # Correct local authorization can be recognized when
    # test feature flag is temporarily enabled.
    #
    # THIS DOES NOT ENABLE NETWORK TRANSPORT.
    # ========================================================

    valid_result = authorize_leverage_mutation(
        proposal=base,
        expected_digest=base_digest,
        explicit_authorization=True,
        consume_request=True,
    )

    results.append(
        print_gate(
            "Valid Local Authorization Recognized",
            valid_result.authorized,
        )
    )

    # ========================================================
    # TEST 14
    # Replay
    # ========================================================

    replay_result = authorize_leverage_mutation(
        proposal=base,
        expected_digest=base_digest,
        explicit_authorization=True,
        consume_request=True,
    )

    results.append(
        print_gate(
            "Duplicate Mutation Authorization Rejected",
            not replay_result.authorized,
        )
    )

    # Restore absolute production state.
    LEVERAGE_MUTATION_FEATURE_ENABLED = (
        original_feature_state
    )

    # ========================================================
    # TEST 15
    # Absolute feature state restored
    # ========================================================

    results.append(
        print_gate(
            "Mutation Feature Restored Disabled",
            not LEVERAGE_MUTATION_FEATURE_ENABLED,
        )
    )

    return all(results)


# ============================================================
# WRITE TRANSPORT SELF TEST
# ============================================================

async def run_transport_tests():

    print()
    print(
        "R28 UNIT N TRANSPORT-BOUNDARY VALIDATION",
        flush=True,
    )

    separator()

    results = []

    proposal = build_required_proposal()

    # --------------------------------------------------------
    # We deliberately call the absolute local POST blocker.
    # This proves the lowest write boundary cannot transmit.
    # --------------------------------------------------------

    blocked = False

    try:

        await blocked_network_post(
            LEVERAGE_WRITE_PATH,
            proposal_payload(
                proposal
            ),
        )

    except PermissionError:

        blocked = True

    results.append(
        print_gate(
            "Leverage POST Attempt Blocked Locally",
            blocked,
        )
    )

    results.append(
        print_gate(
            "Network POST Count Is Zero",
            network_post_count == 0,
        )
    )

    results.append(
        print_gate(
            "Network PUT Count Is Zero",
            network_put_count == 0,
        )
    )

    results.append(
        print_gate(
            "Network PATCH Count Is Zero",
            network_patch_count == 0,
        )
    )

    results.append(
        print_gate(
            "Network DELETE Count Is Zero",
            network_delete_count == 0,
        )
    )

    results.append(
        print_gate(
            "Account Write Transmission Count Is Zero",
            account_write_transmission_count == 0,
        )
    )

    results.append(
        print_gate(
            "Leverage Change Transmission Count Is Zero",
            leverage_change_transmission_count == 0,
        )
    )

    results.append(
        print_gate(
            "Real Order Transmission Never Occurred",
            real_order_transmission_count == 0,
        )
    )

    results.append(
        print_gate(
            "Demo Order Transmission Never Occurred",
            demo_order_transmission_count == 0,
        )
    )

    return all(results)


# ============================================================
# ABSOLUTE SAFETY ASSERTIONS
# ============================================================

def run_absolute_safety_assertions():

    print()
    print(
        "R28 UNIT N ABSOLUTE SAFETY GATES",
        flush=True,
    )

    separator()

    results = []

    results.append(
        print_gate(
            "Live Execution Disabled",
            LIVE_ORDER_EXECUTION is False,
        )
    )

    results.append(
        print_gate(
            "Demo Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    results.append(
        print_gate(
            "Network Writes Disabled",
            NETWORK_WRITE_ENABLED is False,
        )
    )

    results.append(
        print_gate(
            "Account Writes Disabled",
            ACCOUNT_WRITE_ENABLED is False,
        )
    )

    results.append(
        print_gate(
            "Leverage Writes Disabled",
            LEVERAGE_WRITE_ENABLED is False,
        )
    )

    results.append(
        print_gate(
            "Network POST Disabled",
            ALLOW_NETWORK_POST is False,
        )
    )

    results.append(
        print_gate(
            "Network PUT Disabled",
            ALLOW_NETWORK_PUT is False,
        )
    )

    results.append(
        print_gate(
            "Network PATCH Disabled",
            ALLOW_NETWORK_PATCH is False,
        )
    )

    results.append(
        print_gate(
            "Network DELETE Disabled",
            ALLOW_NETWORK_DELETE is False,
        )
    )

    results.append(
        print_gate(
            "Leverage Mutation Feature Disabled",
            LEVERAGE_MUTATION_FEATURE_ENABLED
            is False,
        )
    )

    results.append(
        print_gate(
            "Explicit Mutation Authorization Disabled",
            EXPLICIT_MUTATION_AUTHORIZATION
            is False,
        )
    )

    results.append(
        print_gate(
            "Leverage Mutation Transport Disabled",
            ALLOW_LEVERAGE_MUTATION_TRANSPORT
            is False,
        )
    )

    results.append(
        print_gate(
            "Authenticated Read-Only GET Enabled",
            AUTHENTICATED_READ_ONLY_ENABLED
            is True,
        )
    )

    return all(results)


# ============================================================
# READ CURRENT WEEX CONFIGURATION
# ============================================================

async def read_current_configuration():

    if not credentials_present():

        print()
        print(
            "R28 UNIT N: AUTHENTICATED READ SKIPPED",
            flush=True,
        )

        print(
            "Reason: required API credentials are missing.",
            flush=True,
        )

        return None

    async with aiohttp.ClientSession() as session:

        raw = await authenticated_get(
            session=session,
            path=SYMBOL_CONFIG_PATH,
            params={
                "symbol": SYMBOL,
            },
        )

    record = locate_symbol_record(
        raw,
        SYMBOL,
    )

    if record is None:

        raise RuntimeError(
            "BTCUSDT symbol configuration "
            "was not found in WEEX response."
        )

    return parse_symbol_configuration(
        record
    )


# ============================================================
# CONFIGURATION REPORT
# ============================================================

def print_configuration_report(
    config: Dict[str, Any],
):

    print()
    print(
        "R28 UNIT N CURRENT WEEX CONFIGURATION",
        flush=True,
    )

    separator()

    print(
        f"  Symbol = {config['symbol']}",
        flush=True,
    )

    print(
        f"  Margin Type = "
        f"{config['margin_type']}",
        flush=True,
    )

    print(
        f"  Position Mode = "
        f"{config['position_mode'] or 'UNKNOWN'}",
        flush=True,
    )

    print(
        f"  Cross Leverage = "
        f"{config['cross_leverage']}"
        f"x",
        flush=True,
    )

    print(
        f"  Isolated Long Leverage = "
        f"{config['isolated_long_leverage']}"
        f"x",
        flush=True,
    )

    print(
        f"  Isolated Short Leverage = "
        f"{config['isolated_short_leverage']}"
        f"x",
        flush=True,
    )


# ============================================================
# LEVERAGE GAP REPORT
# ============================================================

def analyze_leverage_gap(
    config: Dict[str, Any],
):

    long_current = config[
        "isolated_long_leverage"
    ]

    short_current = config[
        "isolated_short_leverage"
    ]

    long_ready = (
        long_current
        == REQUIRED_LONG_LEVERAGE
    )

    short_ready = (
        short_current
        == REQUIRED_SHORT_LEVERAGE
    )

    print()
    print(
        "R28 UNIT N LEVERAGE READINESS",
        flush=True,
    )

    separator()

    print(
        f"  Required Long = "
        f"{REQUIRED_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Current Long = "
        f"{long_current}x",
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

    print()

    print(
        f"  Required Short = "
        f"{REQUIRED_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"  Current Short = "
        f"{short_current}x",
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

    return (
        long_ready,
        short_ready,
    )


# ============================================================
# PROPOSED MUTATION REPORT
# ============================================================

def print_proposed_mutation():

    proposal = build_required_proposal()

    payload = proposal_payload(
        proposal
    )

    digest = proposal_digest(
        proposal
    )

    request_id = request_id_for_proposal(
        proposal
    )

    print()
    print(
        "R28 UNIT N HYPOTHETICAL MUTATION",
        flush=True,
    )

    separator()

    print(
        f"  Endpoint:",
        flush=True,
    )

    print(
        f"  POST {LEVERAGE_WRITE_PATH}",
        flush=True,
    )

    print()
    print(
        "  Payload:",
        flush=True,
    )

    print(
        "  "
        + json.dumps(
            payload,
            separators=(",", ":"),
        ),
        flush=True,
    )

    print()
    print(
        f"  Request ID = {request_id}",
        flush=True,
    )

    print(
        f"  Proposal Digest = {digest}",
        flush=True,
    )

    print()
    print(
        "  🚫 UNIT N WILL NOT TRANSMIT "
        "THIS REQUEST",
        flush=True,
    )


# ============================================================
# DIAGNOSTIC
# ============================================================

async def run_diagnostic():

    print()
    print(
        "=" * 76,
        flush=True,
    )

    print(
        "0F-4H-R28-UNIT-N STARTING",
        flush=True,
    )

    print(
        "LEVERAGE MUTATION AUTHORIZATION "
        "/ WRITE-GATE VALIDATION",
        flush=True,
    )

    print(
        "AUTHENTICATED READ-ONLY ACCOUNT "
        "STATE ENABLED",
        flush=True,
    )

    print(
        "LEVERAGE MUTATION TRANSPORT DISABLED",
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
        f"R28 UNIT N SYMBOL: {SYMBOL}",
        flush=True,
    )

    print()
    print(
        "R28 UNIT N NETWORK POLICY:",
        flush=True,
    )

    print(
        "  ✅ Authenticated read-only GET enabled",
        flush=True,
    )

    print(
        "  ❌ Account POST disabled",
        flush=True,
    )

    print(
        "  ❌ Leverage POST disabled",
        flush=True,
    )

    print(
        "  ❌ PUT / PATCH / DELETE disabled",
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

    print()

    print_credential_status()

    structural_safety_passed = (
        run_absolute_safety_assertions()
    )

    authorization_tests_passed = (
        run_authorization_tests()
    )

    print_proposed_mutation()

    transport_tests_passed = (
        await run_transport_tests()
    )

    configuration = None

    configuration_read_passed = False

    try:

        configuration = (
            await read_current_configuration()
        )

        configuration_read_passed = (
            configuration is not None
        )

    except Exception as exc:

        print()
        print(
            "R28 UNIT N AUTHENTICATED GET ERROR:",
            flush=True,
        )

        print(
            f"  {type(exc).__name__}: {exc}",
            flush=True,
        )

    readiness_blockers = []

    if configuration is not None:

        print_configuration_report(
            configuration
        )

        print()

        print_gate(
            "Observed Symbol Matches BTCUSDT",
            configuration["symbol"]
            == SYMBOL,
        )

        print_gate(
            "Observed Margin Mode Is ISOLATED",
            configuration["margin_type"]
            == REQUIRED_MARGIN_TYPE,
        )

        print_gate(
            "Current Long Leverage Parseable",
            configuration[
                "isolated_long_leverage"
            ]
            is not None,
        )

        print_gate(
            "Current Short Leverage Parseable",
            configuration[
                "isolated_short_leverage"
            ]
            is not None,
        )

        long_ready, short_ready = (
            analyze_leverage_gap(
                configuration
            )
        )

        if not long_ready:

            readiness_blockers.append(
                "Isolated LONG leverage requires "
                f"{REQUIRED_LONG_LEVERAGE}x; "
                "current value is "
                f"{configuration['isolated_long_leverage']}x."
            )

        if not short_ready:

            readiness_blockers.append(
                "Isolated SHORT leverage requires "
                f"{REQUIRED_SHORT_LEVERAGE}x; "
                "current value is "
                f"{configuration['isolated_short_leverage']}x."
            )

    else:

        readiness_blockers.append(
            "Current WEEX symbol configuration "
            "could not be verified."
        )

    # ========================================================
    # FINAL TRANSPORT AUDIT
    # ========================================================

    print()
    print(
        "R28 UNIT N WRITE-LOCK AUDIT",
        flush=True,
    )

    separator()

    print_gate(
        "Network POST Count Is Zero",
        network_post_count == 0,
    )

    print_gate(
        "Network PUT Count Is Zero",
        network_put_count == 0,
    )

    print_gate(
        "Network PATCH Count Is Zero",
        network_patch_count == 0,
    )

    print_gate(
        "Network DELETE Count Is Zero",
        network_delete_count == 0,
    )

    print_gate(
        "Account Write Transmission Count Is Zero",
        account_write_transmission_count == 0,
    )

    print_gate(
        "Leverage Change Transmission Count Is Zero",
        leverage_change_transmission_count == 0,
    )

    print_gate(
        "Real Order Transmission Count Is Zero",
        real_order_transmission_count == 0,
    )

    print_gate(
        "Demo Order Transmission Count Is Zero",
        demo_order_transmission_count == 0,
    )

    print()
    print(
        "R28 UNIT N AUTHORIZATION AUDIT:",
        flush=True,
    )

    print(
        f"  Authorization attempts = "
        f"{authorization_attempt_count}",
        flush=True,
    )

    print(
        f"  Local authorization grants = "
        f"{authorization_grant_count}",
        flush=True,
    )

    print(
        f"  Authorization rejections = "
        f"{authorization_rejection_count}",
        flush=True,
    )

    print(
        f"  Accepted request IDs = "
        f"{len(accepted_request_ids)}",
        flush=True,
    )

    print()
    print(
        "R28 UNIT N TRANSPORT AUDIT:",
        flush=True,
    )

    print(
        f"  Network GETs = "
        f"{network_get_count}",
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
        f"  Leverage POST attempts = "
        f"{leverage_post_attempt_count}",
        flush=True,
    )

    print(
        f"  Leverage POST blocks = "
        f"{leverage_post_block_count}",
        flush=True,
    )

    print(
        f"  Network POSTs = "
        f"{network_post_count}",
        flush=True,
    )

    print(
        f"  Account write transmissions = "
        f"{account_write_transmission_count}",
        flush=True,
    )

    print(
        f"  Leverage change transmissions = "
        f"{leverage_change_transmission_count}",
        flush=True,
    )

    # ========================================================
    # STRUCTURAL RESULT
    # ========================================================

    structural_failures = 0

    if not structural_safety_passed:
        structural_failures += 1

    if not authorization_tests_passed:
        structural_failures += 1

    if not transport_tests_passed:
        structural_failures += 1

    if network_post_count != 0:
        structural_failures += 1

    if account_write_transmission_count != 0:
        structural_failures += 1

    if leverage_change_transmission_count != 0:
        structural_failures += 1

    if real_order_transmission_count != 0:
        structural_failures += 1

    if demo_order_transmission_count != 0:
        structural_failures += 1

    print()
    print(
        "R28 UNIT N EXECUTION-READINESS ASSESSMENT",
        flush=True,
    )

    separator()

    print(
        f"Structural Safety Failures = "
        f"{structural_failures}",
        flush=True,
    )

    print(
        f"Readiness Blockers = "
        f"{len(readiness_blockers)}",
        flush=True,
    )

    print(
        f"Authenticated Configuration Read = "
        + (
            "✅ PASS"
            if configuration_read_passed
            else "⚠️ NOT VERIFIED"
        ),
        flush=True,
    )

    print()

    if readiness_blockers:

        print(
            "CURRENT EXECUTION READINESS: "
            "🚫 NOT READY",
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
            "CURRENT CONFIGURATION READINESS: "
            "✅ READY",
            flush=True,
        )

    print()

    separator()

    # ========================================================
    # FINAL RESULT
    # ========================================================

    if structural_failures == 0:

        print(
            "✅ R28 UNIT N DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ LEVERAGE MUTATION AUTHORIZATION "
            "BOUNDARY VALIDATED",
            flush=True,
        )

        print(
            "✅ MUTATION PAYLOAD SCOPE VALIDATED",
            flush=True,
        )

        print(
            "✅ MUTATION INTEGRITY BINDING VALIDATED",
            flush=True,
        )

        print(
            "✅ UNAUTHORIZED MUTATION REJECTED",
            flush=True,
        )

        print(
            "✅ TAMPERED MUTATION REJECTED",
            flush=True,
        )

        print(
            "✅ WRONG-SYMBOL MUTATION REJECTED",
            flush=True,
        )

        print(
            "✅ CROSS-MARGIN MUTATION REJECTED",
            flush=True,
        )

        print(
            "✅ EXCESSIVE LEVERAGE MUTATION REJECTED",
            flush=True,
        )

        print(
            "✅ MUTATION REPLAY PROTECTION VALIDATED",
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

        print(
            "✅ LEVERAGE CHANGE TRANSMISSION COUNT = ZERO",
            flush=True,
        )

    else:

        print(
            "❌ R28 UNIT N DIAGNOSTIC FAILED",
            flush=True,
        )

        print(
            "❌ STRUCTURAL SAFETY FAILURE DETECTED",
            flush=True,
        )

    if readiness_blockers:

        print(
            "⚠️ R28 UNIT N DETECTED "
            "CONFIGURATION READINESS BLOCKERS",
            flush=True,
        )

    print(
        "🛡 NO LEVERAGE CHANGE WAS "
        "TRANSMITTED TO WEEX",
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

    return structural_failures == 0


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):

    return web.json_response(
        {
            "status": "ok",
            "module": MODULE_NAME,
            "version": MODULE_VERSION,
            "symbol": SYMBOL,
            "authenticated_read_only": (
                AUTHENTICATED_READ_ONLY_ENABLED
            ),
            "network_write_enabled": (
                NETWORK_WRITE_ENABLED
            ),
            "leverage_write_enabled": (
                LEVERAGE_WRITE_ENABLED
            ),
            "live_order_execution": (
                LIVE_ORDER_EXECUTION
            ),
            "demo_order_execution": (
                DEMO_ORDER_EXECUTION
            ),
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
        PORT,
    )

    await site.start()

    print(
        f"R28 UNIT N: HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}",
        flush=True,
    )

    return runner


# ============================================================
# SHUTDOWN
# ============================================================

def request_shutdown():

    if not shutdown_event.is_set():

        print(
            "R28 UNIT N: SHUTDOWN REQUESTED",
            flush=True,
        )

        shutdown_event.set()


# ============================================================
# PERSISTENT HEARTBEAT
# ============================================================

async def heartbeat_loop():

    counter = 0

    while not shutdown_event.is_set():

        counter += 1

        print(
            f"R28 UNIT N: HEARTBEAT "
            f"{counter} ✅ ACTIVE",
            flush=True,
        )

        try:

            await asyncio.wait_for(
                shutdown_event.wait(),
                timeout=HEARTBEAT_SECONDS,
            )

        except asyncio.TimeoutError:

            pass


# ============================================================
# MAIN RUNTIME
# ============================================================

async def main():

    print(
        "R28 UNIT N: RUNTIME STARTING",
        flush=True,
    )

    loop = asyncio.get_running_loop()

    for sig in (
        signal.SIGINT,
        signal.SIGTERM,
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

    runner = None

    try:

        runner = (
            await start_health_server()
        )

        await run_diagnostic()

        print(
            "R28 UNIT N: PERSISTENT "
            "RUNTIME ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N: AUTHENTICATED "
            "READ-ONLY LOCKS ACTIVE",
            flush=True,
        )

        print(
            "R28 UNIT N: NETWORK WRITE "
            "TRANSPORT LOCKED",
            flush=True,
        )

        print(
            "R28 UNIT N: LEVERAGE MUTATION "
            "TRANSPORT LOCKED",
            flush=True,
        )

        await heartbeat_loop()

    finally:

        if runner is not None:

            await runner.cleanup()

        print(
            "R28 UNIT N: RUNTIME STOPPED CLEANLY",
            flush=True,
        )


# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "R28 UNIT N: KEYBOARD INTERRUPT",
            flush=True,
        )
      
