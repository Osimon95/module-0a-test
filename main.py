#!/usr/bin/env python3

# =============================================================================
# R33F
# PRE-LIVE LEVERAGE MUTATION BOUNDARY VALIDATION
#
# PURPOSE
# -------
# Validate the complete 100x leverage correction boundary immediately before
# any future consideration of a real authenticated leverage mutation.
#
# IMPORTANT SAFETY GUARANTEES
# ---------------------------
# - REAL ORDER EXECUTION IS DISABLED
# - REAL EXCHANGE NETWORK WRITES ARE DISABLED
# - REAL LEVERAGE MUTATION IS DISABLED
# - ALL POST TRANSPORT IS SYNTHETIC / INTERCEPTED LOCALLY
# - NO REAL ORDER IS SENT
# - NO LEVERAGE CHANGE IS PERFORMED
#
# TARGET
# ------
# BTCUSDT
# ISOLATED
# LONG  = 100x
# SHORT = 100x
#
# OBSERVED BASELINE USED BY THIS VALIDATOR
# ----------------------------------------
# LONG  = 50x
# SHORT = 20x
#
# =============================================================================

import os
import json
import time
import hmac
import hashlib
import tempfile
import threading
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional


# =============================================================================
# R33F CONFIGURATION
# =============================================================================

VERSION = "R33F"

SYMBOL = "BTCUSDT"

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

# Previously observed read-only account state.
OBSERVED_LONG_LEVERAGE = 50
OBSERVED_SHORT_LEVERAGE = 20

GENERATION = 1
RECOVERY_EPOCH = 1

STATE_FILE = "/tmp/r33f_pre_live_boundary_state.json"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

# ---------------------------------------------------------------------------
# HARD SAFETY LOCKS
# ---------------------------------------------------------------------------

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

# ---------------------------------------------------------------------------
# EXACT LEVERAGE MUTATION CONTRACT UNDER VALIDATION
# ---------------------------------------------------------------------------

LEVERAGE_HTTP_METHOD = "POST"

LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

# These credentials are NEVER transmitted.
#
# Environment values may exist in Render, but R33F deliberately does not
# require them for real networking.
#
# Synthetic signing falls back to deterministic local values if credentials
# are unavailable.
API_KEY = os.getenv("WEEX_API_KEY", "")
API_SECRET = os.getenv("WEEX_API_SECRET", "")
API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "")


# =============================================================================
# GLOBAL COUNTERS
# =============================================================================

synthetic_dispatch_counter = 0
duplicate_dispatch_block_counter = 0

real_order_counter = 0
network_write_counter = 0
leverage_mutation_counter = 0

authorization_grant_counter = 0
authorization_consumption_counter = 0

test_pass_counter = 0
test_fail_counter = 0


# =============================================================================
# PRINT HELPERS
# =============================================================================

LINE = "-" * 92


def section(title: str) -> None:
    print(LINE, flush=True)
    print(title, flush=True)
    print(LINE, flush=True)


def check(label: str, condition: bool) -> None:
    global test_pass_counter
    global test_fail_counter

    status = "✅ PASS" if condition else "❌ FAIL"

    print(f"{label:<80} {status}", flush=True)

    if condition:
        test_pass_counter += 1
    else:
        test_fail_counter += 1


# =============================================================================
# CANONICAL SERIALIZATION
# =============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(value: Any) -> str:
    if isinstance(value, bytes):
        raw = value

    elif isinstance(value, str):
        raw = value.encode("utf-8")

    else:
        raw = canonical_json(value).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


# =============================================================================
# DURABLE STATE
# =============================================================================

@dataclass
class R33FState:
    version: str

    phase: str

    symbol: str

    generation: int
    recovery_epoch: int

    observed_long_leverage: int
    observed_short_leverage: int

    target_long_leverage: int
    target_short_leverage: int

    correction_required: bool

    intent_bound: bool

    authorization_granted: bool
    authorization_consumed: bool

    dispatch_committed: bool
    synthetic_transport_completed: bool

    intent_hash: str
    authorization_hash: str
    payload_hash: str
    envelope_hash: str
    receipt_hash: str

    synthetic_dispatch_counter: int

    real_order_counter: int
    network_write_counter: int
    leverage_mutation_counter: int


def atomic_write_json(path: str, payload: Dict[str, Any]) -> None:
    directory = os.path.dirname(path) or "."

    os.makedirs(directory, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(
        prefix=".r33f-",
        suffix=".tmp",
        dir=directory,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(
                payload,
                handle,
                sort_keys=True,
                separators=(",", ":"),
            )

            handle.flush()

            os.fsync(handle.fileno())

        os.replace(temp_path, path)

    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def save_state(state: R33FState) -> None:
    atomic_write_json(
        STATE_FILE,
        asdict(state),
    )


def load_state() -> Optional[R33FState]:
    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as handle:

            data = json.load(handle)

        return R33FState(**data)

    except Exception:
        return None


# =============================================================================
# HEALTH SERVER
# =============================================================================

health_state = {
    "version": VERSION,
    "phase": "STARTING",
    "synthetic_only": True,
    "real_execution": False,
    "network_writes": False,
    "leverage_mutation": False,
}


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.end_headers()
            return

        payload = canonical_json(health_state).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(payload)),
        )

        self.end_headers()

        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def start_health_server() -> None:

    def run_server():
        try:
            server = HTTPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            )

            print(
                f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"{VERSION}: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=run_server,
        daemon=True,
    )

    thread.start()


# =============================================================================
# SYNTHETIC ACCOUNT SNAPSHOT
# =============================================================================

def obtain_account_snapshot() -> Dict[str, Any]:
    """
    R33F does not contact WEEX.

    This represents the last known account-state assumptions that must be
    revalidated again before any future live mutation stage.
    """

    return {
        "symbol": SYMBOL,

        "marginType": TARGET_MARGIN_TYPE,

        "positionMode": "COMBINED",

        "isolatedLongLeverage": OBSERVED_LONG_LEVERAGE,

        "isolatedShortLeverage": OBSERVED_SHORT_LEVERAGE,

        "generation": GENERATION,

        "recoveryEpoch": RECOVERY_EPOCH,

        "source": "R33F_SYNTHETIC_BASELINE",
    }


# =============================================================================
# CORRECTION INTENT
# =============================================================================

def build_correction_intent(
    snapshot: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "version": VERSION,

        "intentType": "LEVERAGE_CORRECTION",

        "symbol": SYMBOL,

        "marginType": TARGET_MARGIN_TYPE,

        "currentLongLeverage":
            snapshot["isolatedLongLeverage"],

        "currentShortLeverage":
            snapshot["isolatedShortLeverage"],

        "targetLongLeverage":
            TARGET_LONG_LEVERAGE,

        "targetShortLeverage":
            TARGET_SHORT_LEVERAGE,

        "generation":
            snapshot["generation"],

        "recoveryEpoch":
            snapshot["recoveryEpoch"],

        "realExecutionAllowed":
            False,

        "networkWriteAllowed":
            False,

        "leverageMutationAllowed":
            False,
    }


# =============================================================================
# AUTHORIZATION
# =============================================================================

def issue_authorization(
    intent: Dict[str, Any],
    intent_hash: str,
) -> Dict[str, Any]:

    global authorization_grant_counter

    authorization_grant_counter += 1

    authorization = {
        "version": VERSION,

        "authorizationType":
            "SYNTHETIC_LEVERAGE_CORRECTION",

        "intentHash":
            intent_hash,

        "symbol":
            intent["symbol"],

        "marginType":
            intent["marginType"],

        "generation":
            intent["generation"],

        "recoveryEpoch":
            intent["recoveryEpoch"],

        "targetLongLeverage":
            intent["targetLongLeverage"],

        "targetShortLeverage":
            intent["targetShortLeverage"],

        "transport":
            "SYNTHETIC_ONLY",

        "singleUse":
            True,
    }

    return authorization


# =============================================================================
# PAYLOAD
# =============================================================================

def build_leverage_payload() -> Dict[str, Any]:
    """
    Exact R33F leverage payload under synthetic validation.

    No network transport is performed.
    """

    return {
        "symbol": SYMBOL,

        "marginMode": TARGET_MARGIN_TYPE,

        "leverage": str(TARGET_LONG_LEVERAGE),
    }


# =============================================================================
# SYNTHETIC SIGNATURE
# =============================================================================

def synthetic_secret() -> str:
    """
    Never requires or exposes a production secret.

    If an environment secret exists, it may be used locally for HMAC
    computation only. Nothing is transmitted.
    """

    if API_SECRET:
        return API_SECRET

    return "R33F_LOCAL_SYNTHETIC_SIGNING_SECRET"


def create_signature(
    timestamp_ms: str,
    method: str,
    endpoint: str,
    payload: Dict[str, Any],
) -> str:

    body = canonical_json(payload)

    signing_string = (
        timestamp_ms
        + method.upper()
        + endpoint
        + body
    )

    return hmac.new(
        synthetic_secret().encode("utf-8"),
        signing_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# =============================================================================
# TRANSPORT ENVELOPE
# =============================================================================

def build_transport_envelope(
    authorization: Dict[str, Any],
    authorization_hash: str,
    payload: Dict[str, Any],
    payload_hash: str,
) -> Dict[str, Any]:

    timestamp_ms = str(int(time.time() * 1000))

    signature = create_signature(
        timestamp_ms,
        LEVERAGE_HTTP_METHOD,
        LEVERAGE_ENDPOINT,
        payload,
    )

    return {
        "transportMode":
            "SYNTHETIC_INTERCEPT",

        "method":
            LEVERAGE_HTTP_METHOD,

        "endpoint":
            LEVERAGE_ENDPOINT,

        "timestamp":
            timestamp_ms,

        "headers": {
            "ACCESS-KEY":
                API_KEY
                if API_KEY
                else "R33F_SYNTHETIC_KEY",

            "ACCESS-PASSPHRASE":
                API_PASSPHRASE
                if API_PASSPHRASE
                else "R33F_SYNTHETIC_PASSPHRASE",

            "ACCESS-TIMESTAMP":
                timestamp_ms,

            "ACCESS-SIGN":
                signature,
        },

        "payload":
            payload,

        "payloadHash":
            payload_hash,

        "authorizationHash":
            authorization_hash,

        "generation":
            authorization["generation"],

        "recoveryEpoch":
            authorization["recoveryEpoch"],

        "realNetworkAllowed":
            False,
    }


# =============================================================================
# AUTHORIZATION CONSUMPTION
# =============================================================================

consumed_authorizations = set()


def consume_authorization(
    authorization_hash: str,
) -> bool:

    global authorization_consumption_counter

    if authorization_hash in consumed_authorizations:
        return False

    consumed_authorizations.add(
        authorization_hash
    )

    authorization_consumption_counter += 1

    return True


# =============================================================================
# SYNTHETIC TRANSPORT FIREBREAK
# =============================================================================

dispatched_envelopes = set()


def synthetic_dispatch(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    global synthetic_dispatch_counter
    global duplicate_dispatch_block_counter

    envelope_hash = sha256_hex(envelope)

    if envelope_hash in dispatched_envelopes:

        duplicate_dispatch_block_counter += 1

        raise RuntimeError(
            "R33F duplicate synthetic transport rejected"
        )

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "Synthetic-only transport invariant violated"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Exchange network write capability must remain disabled"
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "Leverage mutation capability must remain disabled"
        )

    dispatched_envelopes.add(
        envelope_hash
    )

    synthetic_dispatch_counter += 1

    receipt = {
        "version":
            VERSION,

        "transport":
            "SYNTHETIC_INTERCEPT",

        "status":
            "INTERCEPTED",

        "method":
            envelope["method"],

        "endpoint":
            envelope["endpoint"],

        "envelopeHash":
            envelope_hash,

        "payloadHash":
            envelope["payloadHash"],

        "authorizationHash":
            envelope["authorizationHash"],

        "generation":
            envelope["generation"],

        "recoveryEpoch":
            envelope["recoveryEpoch"],

        "exchangeContacted":
            False,

        "networkTransmission":
            False,

        "leverageMutationPerformed":
            False,

        "realOrderSent":
            False,

        "syntheticDispatchCounter":
            synthetic_dispatch_counter,
    }

    return receipt


# =============================================================================
# BINDING VALIDATION
# =============================================================================

def lineage_matches(
    snapshot: Dict[str, Any],
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
    envelope: Dict[str, Any],
) -> bool:

    return (
        snapshot["symbol"]
        == intent["symbol"]
        == authorization["symbol"]
        == SYMBOL

        and

        snapshot["marginType"]
        == intent["marginType"]
        == authorization["marginType"]
        == TARGET_MARGIN_TYPE

        and

        snapshot["generation"]
        == intent["generation"]
        == authorization["generation"]
        == envelope["generation"]

        and

        snapshot["recoveryEpoch"]
        == intent["recoveryEpoch"]
        == authorization["recoveryEpoch"]
        == envelope["recoveryEpoch"]
    )


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def run_validation():

    global synthetic_dispatch_counter

    section(
        "R33F: MAIN.PY ENTERED"
    )

    print(
        f"R33F: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"R33F: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"R33F: STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"R33F: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        "R33F: REAL EXECUTION DISABLED",
        flush=True,
    )

    print(
        "R33F: EXCHANGE NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        "R33F: LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    print(
        "R33F: SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )

    print(
        f"R33F: OBSERVED LEVERAGE "
        f"long={OBSERVED_LONG_LEVERAGE}x "
        f"short={OBSERVED_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"R33F: TARGET LEVERAGE "
        f"long={TARGET_LONG_LEVERAGE}x "
        f"short={TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    # =========================================================================
    section(
        "R33F TEST 1: HARD SAFETY CONFIGURATION"
    )
    # =========================================================================

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )

    check(
        "Synthetic Transport Is Mandatory",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    # =========================================================================
    section(
        "R33F TEST 2: BASELINE ACCOUNT STATE"
    )
    # =========================================================================

    snapshot = obtain_account_snapshot()

    check(
        "Snapshot Symbol Is BTCUSDT",
        snapshot["symbol"] == SYMBOL,
    )

    check(
        "Snapshot Margin Type Is Isolated",
        snapshot["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Observed Long Leverage Is 50x",
        snapshot["isolatedLongLeverage"]
        == OBSERVED_LONG_LEVERAGE,
    )

    check(
        "Observed Short Leverage Is 20x",
        snapshot["isolatedShortLeverage"]
        == OBSERVED_SHORT_LEVERAGE,
    )

    # =========================================================================
    section(
        "R33F TEST 3: CORRECTION REQUIREMENT"
    )
    # =========================================================================

    correction_required = (
        snapshot["isolatedLongLeverage"]
        != TARGET_LONG_LEVERAGE

        or

        snapshot["isolatedShortLeverage"]
        != TARGET_SHORT_LEVERAGE
    )

    check(
        "100x Correction Is Required",
        correction_required,
    )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE == 100,
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE == 100,
    )

    # =========================================================================
    section(
        "R33F TEST 4: CORRECTION INTENT BINDING"
    )
    # =========================================================================

    intent = build_correction_intent(
        snapshot
    )

    intent_hash = sha256_hex(
        intent
    )

    check(
        "Intent Symbol Is Bound",
        intent["symbol"] == SYMBOL,
    )

    check(
        "Intent Margin Type Is Bound",
        intent["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Intent Target Long Is 100x",
        intent["targetLongLeverage"]
        == 100,
    )

    check(
        "Intent Target Short Is 100x",
        intent["targetShortLeverage"]
        == 100,
    )

    check(
        "Intent Generation Matches",
        intent["generation"]
        == GENERATION,
    )

    check(
        "Intent Recovery Epoch Matches",
        intent["recoveryEpoch"]
        == RECOVERY_EPOCH,
    )

    check(
        "Intent Hash Exists",
        len(intent_hash) == 64,
    )

    # =========================================================================
    section(
        "R33F TEST 5: AUTHORIZATION BINDING"
    )
    # =========================================================================

    authorization = issue_authorization(
        intent,
        intent_hash,
    )

    authorization_hash = sha256_hex(
        authorization
    )

    check(
        "Authorization Binds Exact Intent Hash",
        authorization["intentHash"]
        == intent_hash,
    )

    check(
        "Authorization Symbol Matches",
        authorization["symbol"]
        == SYMBOL,
    )

    check(
        "Authorization Margin Type Matches",
        authorization["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Authorization Long Target Is 100x",
        authorization["targetLongLeverage"]
        == 100,
    )

    check(
        "Authorization Short Target Is 100x",
        authorization["targetShortLeverage"]
        == 100,
    )

    check(
        "Authorization Is Single Use",
        authorization["singleUse"]
        is True,
    )

    # =========================================================================
    section(
        "R33F TEST 6: EXACT LEVERAGE PAYLOAD"
    )
    # =========================================================================

    payload = build_leverage_payload()

    payload_hash = sha256_hex(
        payload
    )

    check(
        "Payload Symbol Is Exact",
        payload["symbol"]
        == SYMBOL,
    )

    check(
        "Payload Margin Mode Is Exact",
        payload["marginMode"]
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Payload Leverage Is Exactly 100",
        payload["leverage"]
        == "100",
    )

    check(
        "Payload Hash Exists",
        len(payload_hash)
        == 64,
    )

    # =========================================================================
    section(
        "R33F TEST 7: EXACT TRANSPORT CONTRACT"
    )
    # =========================================================================

    check(
        "Transport Method Is POST",
        LEVERAGE_HTTP_METHOD
        == "POST",
    )

    check(
        "Configured Endpoint Is Exact",
        LEVERAGE_ENDPOINT
        == "/capi/v2/account/leverage",
    )

    check(
        "Transport Is Still Synthetic Only",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    # =========================================================================
    section(
        "R33F TEST 8: TRANSPORT ENVELOPE"
    )
    # =========================================================================

    envelope = build_transport_envelope(
        authorization,
        authorization_hash,
        payload,
        payload_hash,
    )

    envelope_hash = sha256_hex(
        envelope
    )

    check(
        "Envelope Method Matches",
        envelope["method"]
        == LEVERAGE_HTTP_METHOD,
    )

    check(
        "Envelope Endpoint Matches",
        envelope["endpoint"]
        == LEVERAGE_ENDPOINT,
    )

    check(
        "Envelope Payload Hash Matches",
        envelope["payloadHash"]
        == payload_hash,
    )

    check(
        "Envelope Authorization Hash Matches",
        envelope["authorizationHash"]
        == authorization_hash,
    )

    check(
        "Envelope Contains Signature",
        bool(
            envelope["headers"]["ACCESS-SIGN"]
        ),
    )

    check(
        "Envelope Blocks Real Network",
        envelope["realNetworkAllowed"]
        is False,
    )

    # =========================================================================
    section(
        "R33F TEST 9: GENERATION / RECOVERY / LINEAGE BINDING"
    )
    # =========================================================================

    check(
        "Complete Lineage Matches",
        lineage_matches(
            snapshot,
            intent,
            authorization,
            envelope,
        ),
    )

    check(
        "Envelope Generation Matches State",
        envelope["generation"]
        == GENERATION,
    )

    check(
        "Envelope Recovery Epoch Matches State",
        envelope["recoveryEpoch"]
        == RECOVERY_EPOCH,
    )

    # =========================================================================
    section(
        "R33F TEST 10: STALE GENERATION REJECTION"
    )
    # =========================================================================

    stale_envelope = dict(
        envelope
    )

    stale_envelope["generation"] = (
        GENERATION - 1
    )

    check(
        "Stale Generation Is Rejected",
        not lineage_matches(
            snapshot,
            intent,
            authorization,
            stale_envelope,
        ),
    )

    stale_epoch_envelope = dict(
        envelope
    )

    stale_epoch_envelope[
        "recoveryEpoch"
    ] = RECOVERY_EPOCH - 1

    check(
        "Stale Recovery Epoch Is Rejected",
        not lineage_matches(
            snapshot,
            intent,
            authorization,
            stale_epoch_envelope,
        ),
    )

    # =========================================================================
    section(
        "R33F TEST 11: AUTHORIZATION CONSUMPTION"
    )
    # =========================================================================

    first_consumption = consume_authorization(
        authorization_hash
    )

    second_consumption = consume_authorization(
        authorization_hash
    )

    check(
        "Authorization Consumed Exactly Once",
        first_consumption
        is True,
    )

    check(
        "Authorization Replay Is Rejected",
        second_consumption
        is False,
    )

    check(
        "Authorization Consumption Counter Is One",
        authorization_consumption_counter
        == 1,
    )

    # =========================================================================
    section(
        "R33F TEST 12: SYNTHETIC TRANSPORT INTERCEPTION"
    )
    # =========================================================================

    receipt = synthetic_dispatch(
        envelope
    )

    receipt_hash = sha256_hex(
        receipt
    )

    check(
        "Synthetic Transport Was Intercepted",
        receipt["status"]
        == "INTERCEPTED",
    )

    check(
        "Exchange Was Not Contacted",
        receipt["exchangeContacted"]
        is False,
    )

    check(
        "No Network Transmission Occurred",
        receipt["networkTransmission"]
        is False,
    )

    check(
        "No Leverage Mutation Occurred",
        receipt["leverageMutationPerformed"]
        is False,
    )

    check(
        "No Real Order Was Sent",
        receipt["realOrderSent"]
        is False,
    )

    check(
        "Synthetic Dispatch Counter Is One",
        synthetic_dispatch_counter
        == 1,
    )

    # =========================================================================
    section(
        "R33F TEST 13: DUPLICATE TRANSPORT REJECTION"
    )
    # =========================================================================

    duplicate_rejected = False

    try:
        synthetic_dispatch(
            envelope
        )

    except RuntimeError:
        duplicate_rejected = True

    check(
        "Duplicate Envelope Dispatch Is Rejected",
        duplicate_rejected,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        synthetic_dispatch_counter
        == 1,
    )

    check(
        "Duplicate Dispatch Block Counter Is One",
        duplicate_dispatch_block_counter
        == 1,
    )

    # =========================================================================
    section(
        "R33F TEST 14: DURABLE TERMINAL SNAPSHOT"
    )
    # =========================================================================

    terminal_state = R33FState(
        version=VERSION,

        phase="PRE_LIVE_VALIDATED",

        symbol=SYMBOL,

        generation=GENERATION,

        recovery_epoch=RECOVERY_EPOCH,

        observed_long_leverage=
            OBSERVED_LONG_LEVERAGE,

        observed_short_leverage=
            OBSERVED_SHORT_LEVERAGE,

        target_long_leverage=
            TARGET_LONG_LEVERAGE,

        target_short_leverage=
            TARGET_SHORT_LEVERAGE,

        correction_required=
            correction_required,

        intent_bound=True,

        authorization_granted=True,

        authorization_consumed=True,

        dispatch_committed=True,

        synthetic_transport_completed=True,

        intent_hash=
            intent_hash,

        authorization_hash=
            authorization_hash,

        payload_hash=
            payload_hash,

        envelope_hash=
            envelope_hash,

        receipt_hash=
            receipt_hash,

        synthetic_dispatch_counter=
            synthetic_dispatch_counter,

        real_order_counter=
            real_order_counter,

        network_write_counter=
            network_write_counter,

        leverage_mutation_counter=
            leverage_mutation_counter,
    )

    save_state(
        terminal_state
    )

    restored = load_state()

    check(
        "State File Restores",
        restored is not None,
    )

    if restored is not None:

        check(
            "Restored Phase Is Pre-Live Validated",
            restored.phase
            == "PRE_LIVE_VALIDATED",
        )

        check(
            "Restored Intent Hash Matches",
            restored.intent_hash
            == intent_hash,
        )

        check(
            "Restored Authorization Hash Matches",
            restored.authorization_hash
            == authorization_hash,
        )

        check(
            "Restored Payload Hash Matches",
            restored.payload_hash
            == payload_hash,
        )

        check(
            "Restored Envelope Hash Matches",
            restored.envelope_hash
            == envelope_hash,
        )

        check(
            "Restored Receipt Hash Matches",
            restored.receipt_hash
            == receipt_hash,
        )

        check(
            "Restored Synthetic Dispatch Counter Is One",
            restored.synthetic_dispatch_counter
            == 1,
        )

        check(
            "Restored Network Write Counter Is Zero",
            restored.network_write_counter
            == 0,
        )

        check(
            "Restored Mutation Counter Is Zero",
            restored.leverage_mutation_counter
            == 0,
        )

    # =========================================================================
    section(
        "R33F TEST 15: TERMINAL SAFETY COUNTERS"
    )
    # =========================================================================

    check(
        "Synthetic Dispatch Counter Is One",
        synthetic_dispatch_counter
        == 1,
    )

    check(
        "Real Order Counter Is Zero",
        real_order_counter
        == 0,
    )

    check(
        "Network Write Counter Is Zero",
        network_write_counter
        == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        leverage_mutation_counter
        == 0,
    )

    # =========================================================================
    section(
        "R33F FINAL VALIDATION"
    )
    # =========================================================================

    check(
        "100x Correction Remains Required",
        correction_required,
    )

    check(
        "100x Correction Intent Remains Bound",
        terminal_state.intent_bound,
    )

    check(
        "Authorization Remains Consumed",
        terminal_state.authorization_consumed,
    )

    check(
        "Dispatch Remains Committed",
        terminal_state.dispatch_committed,
    )

    check(
        "Synthetic Transport Occurred Exactly Once",
        synthetic_dispatch_counter
        == 1,
    )

    check(
        "Correction Remains Non-Executable On Real Network",
        (
            SYNTHETIC_TRANSPORT_ONLY
            and
            not EXCHANGE_NETWORK_WRITES_ENABLED
        ),
    )

    check(
        "No Network Write Capability Activated",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "No Leverage Mutation Capability Activated",
        not LEVERAGE_MUTATION_ENABLED,
    )

    check(
        "No Real Execution Capability Activated",
        not REAL_ORDER_EXECUTION_ENABLED,
    )

    # =========================================================================
    # FINAL STATUS
    # =========================================================================

    if test_fail_counter == 0:

        health_state.update({
            "version":
                VERSION,

            "phase":
                "PRE_LIVE_VALIDATED",

            "synthetic_only":
                True,

            "synthetic_dispatch":
                synthetic_dispatch_counter,

            "real_execution":
                False,

            "network_writes":
                False,

            "leverage_mutation":
                False,

            "correction_required":
                correction_required,

            "intent_bound":
                True,

            "authorization_consumed":
                True,

            "dispatch_committed":
                True,

            "target_long":
                TARGET_LONG_LEVERAGE,

            "target_short":
                TARGET_SHORT_LEVERAGE,

            "generation":
                GENERATION,

            "recovery_epoch":
                RECOVERY_EPOCH,
        })

        section(
            "R33F: VALIDATION COMPLETE ✅"
        )

        print(
            "R33F: PRE-LIVE 100X LEVERAGE MUTATION BOUNDARY VALIDATED",
            flush=True,
        )

        print(
            "R33F: EXACT INTENT / AUTHORIZATION / PAYLOAD / ENVELOPE BINDINGS VALIDATED",
            flush=True,
        )

        print(
            "R33F: GENERATION / RECOVERY / LINEAGE BINDINGS VALIDATED",
            flush=True,
        )

        print(
            "R33F: SYNTHETIC TRANSPORT INTERCEPTED EXACTLY ONCE",
            flush=True,
        )

        print(
            "R33F: DUPLICATE TRANSPORT REMAINS REJECTED",
            flush=True,
        )

        print(
            "R33F: NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "R33F: NO EXCHANGE NETWORK WRITE WAS PERFORMED",
            flush=True,
        )

        print(
            "R33F: NO LEVERAGE MUTATION WAS PERFORMED",
            flush=True,
        )

    else:

        health_state.update({
            "version":
                VERSION,

            "phase":
                "VALIDATION_FAILED",

            "synthetic_only":
                True,

            "real_execution":
                False,

            "network_writes":
                False,

            "leverage_mutation":
                False,

            "failed_tests":
                test_fail_counter,
        })

        section(
            "R33F: VALIDATION FAILED ❌"
        )

        print(
            f"R33F: FAILED TESTS={test_fail_counter}",
            flush=True,
        )


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"R33F: HEARTBEAT {heartbeat} | "
            f"phase={health_state.get('phase')} | "
            f"synthetic-only=True | "
            f"synthetic-dispatch={synthetic_dispatch_counter} | "
            f"real-execution={REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes={EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"correction-required="
            f"{health_state.get('correction_required', True)} | "
            f"intent-bound="
            f"{health_state.get('intent_bound', False)} | "
            f"authorization-consumed="
            f"{health_state.get('authorization_consumed', False)} | "
            f"dispatch-committed="
            f"{health_state.get('dispatch_committed', False)} | "
            f"target-long={TARGET_LONG_LEVERAGE}x | "
            f"target-short={TARGET_SHORT_LEVERAGE}x | "
            f"generation={GENERATION} | "
            f"recovery-epoch={RECOVERY_EPOCH}",
            flush=True,
        )

        time.sleep(30)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():

    start_health_server()

    run_validation()

    heartbeat_loop()


if __name__ == "__main__":
    main()
