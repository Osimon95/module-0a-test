# =====================================================================================
# R34H main.py
# FINAL ARMING + ONE-SHOT COMMIT GATE
#
# PURPOSE
# -------
# 1. Preserve the validated R34G correction:
#       BTCUSDT
#       ISOLATED
#       observed long  = 50x
#       observed short = 20x
#       target long    = 100x
#       target short   = 100x
#
# 2. Introduce an explicit FINAL ARMING TOKEN.
#
# 3. Bind that token to:
#       - fresh state
#       - exact payload
#       - exact envelope
#       - generation
#       - nonce
#
# 4. Consume the arming token exactly once.
#
# 5. Perform ONE synthetic commit.
#
# 6. Verify replay / stale / tamper rejection.
#
# 7. KEEP REAL HTTP POST PHYSICALLY ABSENT.
#
# IMPORTANT
# ---------
# This build CANNOT mutate exchange leverage.
# This build CANNOT send a real order.
# This build CANNOT perform an exchange network write.
# =====================================================================================

import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer


# =====================================================================================
# R34H CONSTANTS
# =====================================================================================

VERSION = "R34H"
SYMBOL = "BTCUSDT"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

MARGIN_TYPE = "ISOLATED"

OBSERVED_LONG_LEVERAGE = 50
OBSERVED_SHORT_LEVERAGE = 20

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

LEVERAGE_PATH = "/capi/v3/account/leverage"

SYNTHETIC_ONLY = True
AUTHENTICATED_READ_ONLY = True

REAL_ORDER_EXECUTION = False
EXCHANGE_NETWORK_WRITES = False
LEVERAGE_MUTATION_ENABLED = False

FINAL_ARMING_REQUIRED = True

HEARTBEAT_SECONDS = 30

STATE_MAX_AGE_SECONDS = 120

SEPARATOR = "-" * 100


# =====================================================================================
# R34H COUNTERS
# =====================================================================================

COUNTERS = {
    "authenticated_gets": 4,

    "real_orders": 0,
    "network_writes": 0,
    "leverage_mutations": 0,

    "synthetic_dispatches": 0,
    "synthetic_commits": 0,

    "duplicate_dispatch_blocks": 0,
    "duplicate_commit_blocks": 0,

    "stale_state_blocks": 0,
    "payload_tamper_blocks": 0,
    "envelope_tamper_blocks": 0,

    "arming_tokens_created": 0,
    "arming_tokens_consumed": 0,
    "arming_replay_blocks": 0,

    "unauthorized_commit_blocks": 0,
}


# =====================================================================================
# R34H RUNTIME STATE
# =====================================================================================

RUNTIME = {
    "phase": "BOOT",

    "generation": 1,

    "fresh_state_validated": False,
    "correction_required": False,
    "correction_ready": False,

    "pre_write_gate_validated": False,
    "final_arming_validated": False,
    "commit_gate_validated": False,

    "authorization_consumed": False,
    "arming_token_consumed": False,
    "synthetic_commit_complete": False,

    "initial_state_hash": "",
    "payload_hash": "",
    "envelope_hash": "",
    "authorization_hash": "",
    "arming_hash": "",
    "commit_hash": "",
    "receipt_hash": "",

    "open_positions": 0,
}


# =====================================================================================
# BASIC UTILITIES
# =====================================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def object_hash(value):
    return sha256_text(canonical_json(value))


def now_ms():
    return int(time.time() * 1000)


def print_header(title):
    print(SEPARATOR, flush=True)
    print(title, flush=True)
    print(SEPARATOR, flush=True)


def pass_line(label):
    print(f"{label:<85} ✅ PASS", flush=True)


def fail_line(label):
    print(f"{label:<85} ❌ FAIL", flush=True)
    raise AssertionError(label)


def check(label, condition):
    if condition:
        pass_line(label)
    else:
        fail_line(label)


# =====================================================================================
# ABSOLUTE WRITE FIREBREAK
# =====================================================================================

def real_http_post(*args, **kwargs):
    """
    R34H intentionally contains NO implementation capable of transmitting
    an exchange POST.

    Calling this function always fails closed.
    """

    COUNTERS["network_writes"] += 0
    COUNTERS["leverage_mutations"] += 0

    raise RuntimeError(
        "R34H HARD FIREBREAK: real HTTP POST does not exist in this build"
    )


def mutate_exchange_leverage(*args, **kwargs):
    """
    Explicit local mutation blocker.
    """

    COUNTERS["leverage_mutations"] += 0

    raise RuntimeError(
        "R34H HARD FIREBREAK: leverage mutation is disabled"
    )


def send_real_order(*args, **kwargs):
    """
    Explicit real-order blocker.
    """

    COUNTERS["real_orders"] += 0

    raise RuntimeError(
        "R34H HARD FIREBREAK: real order execution is disabled"
    )


# =====================================================================================
# HEALTH SERVER
# =====================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = {
            "status": "ok",
            "version": VERSION,
            "phase": RUNTIME["phase"],

            "symbol": SYMBOL,

            "synthetic_only": SYNTHETIC_ONLY,
            "authenticated_read_only": AUTHENTICATED_READ_ONLY,

            "real_execution": REAL_ORDER_EXECUTION,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
            "leverage_mutation": LEVERAGE_MUTATION_ENABLED,

            "observed_margin": MARGIN_TYPE,
            "observed_long": OBSERVED_LONG_LEVERAGE,
            "observed_short": OBSERVED_SHORT_LEVERAGE,

            "target_long": TARGET_LONG_LEVERAGE,
            "target_short": TARGET_SHORT_LEVERAGE,

            "correction_required": RUNTIME["correction_required"],
            "correction_ready": RUNTIME["correction_ready"],

            "fresh_state": RUNTIME["fresh_state_validated"],

            "pre_write_gate": RUNTIME["pre_write_gate_validated"],
            "final_arming": RUNTIME["final_arming_validated"],
            "commit_gate": RUNTIME["commit_gate_validated"],

            "synthetic_commit_complete":
                RUNTIME["synthetic_commit_complete"],

            "network_write_counter":
                COUNTERS["network_writes"],

            "leverage_mutation_counter":
                COUNTERS["leverage_mutations"],

            "real_order_counter":
                COUNTERS["real_orders"],
        }

        encoded = canonical_json(body).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(encoded))
        )
        self.end_headers()

        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def start_health_server():

    def worker():
        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler
        )
        server.serve_forever()

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()


# =====================================================================================
# R34H LIVE-STATE SNAPSHOT
#
# R34G already authenticated and reconciled the state.
#
# R34H consumes that validated state representation and tests the final
# local arming / commit boundary.
# =====================================================================================

def build_live_state():

    return {
        "version": VERSION,
        "symbol": SYMBOL,

        "marginType": MARGIN_TYPE,

        "isolatedLongLeverage":
            OBSERVED_LONG_LEVERAGE,

        "isolatedShortLeverage":
            OBSERVED_SHORT_LEVERAGE,

        "openPositions": 0,

        "generation":
            RUNTIME["generation"],

        "retrievedAt":
            int(time.time()),

        "source":
            "R34G_VALIDATED_AUTHENTICATED_STATE",

        "authenticated":
            True,

        "readOnly":
            True,
    }


def state_is_fresh(state):

    age = int(time.time()) - state["retrievedAt"]

    return (
        age >= 0
        and
        age <= STATE_MAX_AGE_SECONDS
    )


# =====================================================================================
# EXACT V3 CORRECTION PAYLOAD
# =====================================================================================

def build_payload():

    return {
        "symbol":
            SYMBOL,

        "marginType":
            MARGIN_TYPE,

        "isolatedLongLeverage":
            str(TARGET_LONG_LEVERAGE),

        "isolatedShortLeverage":
            str(TARGET_SHORT_LEVERAGE),
    }


# =====================================================================================
# OFFLINE SIGNATURE
# =====================================================================================

def build_offline_signature(
    timestamp,
    method,
    path,
    body,
):

    secret = os.getenv(
        "WEEX_API_SECRET",
        "R34H_OFFLINE_SYNTHETIC_SECRET"
    )

    prehash = (
        str(timestamp)
        +
        method.upper()
        +
        path
        +
        body
    )

    return hmac.new(
        secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# =====================================================================================
# OFFLINE ENVELOPE
# =====================================================================================

def build_envelope(
    live_state,
    payload,
):

    payload_body = canonical_json(payload)

    timestamp = now_ms()

    signature = build_offline_signature(
        timestamp=timestamp,
        method="POST",
        path=LEVERAGE_PATH,
        body=payload_body,
    )

    return {
        "method":
            "POST",

        "path":
            LEVERAGE_PATH,

        "transport":
            "SYNTHETIC_ONLY",

        "payload":
            payload,

        "payloadHash":
            object_hash(payload),

        "liveStateHash":
            object_hash(live_state),

        "headers": {
            "ACCESS-KEY":
                os.getenv(
                    "WEEX_API_KEY",
                    "R34H_PRESENT"
                ),

            "ACCESS-SIGN":
                signature,

            "ACCESS-PASSPHRASE":
                os.getenv(
                    "WEEX_API_PASSPHRASE",
                    "R34H_PRESENT"
                ),

            "ACCESS-TIMESTAMP":
                str(timestamp),
        },

        "networkWriteAllowed":
            False,

        "leverageMutationAllowed":
            False,

        "realExecutionAllowed":
            False,
    }


# =====================================================================================
# PRE-WRITE AUTHORIZATION
# =====================================================================================

def build_authorization(
    live_state,
    payload,
    envelope,
):

    return {
        "version":
            VERSION,

        "type":
            "PRE_WRITE_AUTHORIZATION",

        "generation":
            RUNTIME["generation"],

        "nonce":
            secrets.token_hex(16),

        "createdAt":
            now_ms(),

        "consumed":
            False,

        "syntheticOnly":
            True,

        "networkWriteAllowed":
            False,

        "mutationAllowed":
            False,

        "liveStateHash":
            object_hash(live_state),

        "payloadHash":
            object_hash(payload),

        "envelopeHash":
            object_hash(envelope),
    }


def validate_authorization(
    authorization,
    live_state,
    payload,
    envelope,
):

    if authorization["consumed"]:
        return False

    if not authorization["syntheticOnly"]:
        return False

    if authorization["networkWriteAllowed"]:
        return False

    if authorization["mutationAllowed"]:
        return False

    if (
        authorization["generation"]
        !=
        RUNTIME["generation"]
    ):
        return False

    if (
        authorization["liveStateHash"]
        !=
        object_hash(live_state)
    ):
        return False

    if (
        authorization["payloadHash"]
        !=
        object_hash(payload)
    ):
        return False

    if (
        authorization["envelopeHash"]
        !=
        object_hash(envelope)
    ):
        return False

    return True


# =====================================================================================
# FINAL ARMING TOKEN
# =====================================================================================

def create_final_arming_token(
    live_state,
    payload,
    envelope,
    authorization,
):

    token = {
        "version":
            VERSION,

        "type":
            "FINAL_ARMING_TOKEN",

        "generation":
            RUNTIME["generation"],

        "nonce":
            secrets.token_hex(32),

        "createdAt":
            now_ms(),

        "consumed":
            False,

        "syntheticOnly":
            True,

        "liveStateHash":
            object_hash(live_state),

        "payloadHash":
            object_hash(payload),

        "envelopeHash":
            object_hash(envelope),

        "authorizationHash":
            object_hash(authorization),

        "networkWriteAllowed":
            False,

        "leverageMutationAllowed":
            False,

        "realOrderAllowed":
            False,
    }

    COUNTERS["arming_tokens_created"] += 1

    return token


def validate_final_arming_token(
    token,
    live_state,
    payload,
    envelope,
    authorization,
):

    if token["consumed"]:
        return False

    if not token["syntheticOnly"]:
        return False

    if token["networkWriteAllowed"]:
        return False

    if token["leverageMutationAllowed"]:
        return False

    if token["realOrderAllowed"]:
        return False

    if (
        token["generation"]
        !=
        RUNTIME["generation"]
    ):
        return False

    if (
        token["liveStateHash"]
        !=
        object_hash(live_state)
    ):
        return False

    if (
        token["payloadHash"]
        !=
        object_hash(payload)
    ):
        return False

    if (
        token["envelopeHash"]
        !=
        object_hash(envelope)
    ):
        return False

    if (
        token["authorizationHash"]
        !=
        object_hash(authorization)
    ):
        return False

    return True


# =====================================================================================
# SYNTHETIC COMMIT
# =====================================================================================

def synthetic_commit(
    live_state,
    payload,
    envelope,
    authorization,
    arming_token,
):

    if authorization["consumed"]:
        COUNTERS[
            "duplicate_commit_blocks"
        ] += 1

        raise RuntimeError(
            "authorization already consumed"
        )

    if arming_token["consumed"]:
        COUNTERS[
            "arming_replay_blocks"
        ] += 1

        raise RuntimeError(
            "final arming token already consumed"
        )

    if not state_is_fresh(live_state):
        COUNTERS[
            "stale_state_blocks"
        ] += 1

        raise RuntimeError(
            "live state is stale"
        )

    if not validate_authorization(
        authorization,
        live_state,
        payload,
        envelope,
    ):
        COUNTERS[
            "unauthorized_commit_blocks"
        ] += 1

        raise RuntimeError(
            "authorization validation failed"
        )

    if not validate_final_arming_token(
        arming_token,
        live_state,
        payload,
        envelope,
        authorization,
    ):
        COUNTERS[
            "unauthorized_commit_blocks"
        ] += 1

        raise RuntimeError(
            "final arming validation failed"
        )

    # -----------------------------------------------------------------
    # ONE-TIME CONSUMPTION
    # -----------------------------------------------------------------

    authorization["consumed"] = True

    arming_token["consumed"] = True

    RUNTIME["authorization_consumed"] = True
    RUNTIME["arming_token_consumed"] = True

    COUNTERS[
        "arming_tokens_consumed"
    ] += 1

    # -----------------------------------------------------------------
    # SYNTHETIC COMMIT ONLY
    # -----------------------------------------------------------------

    commit = {
        "version":
            VERSION,

        "type":
            "SYNTHETIC_FINAL_COMMIT",

        "generation":
            RUNTIME["generation"],

        "symbol":
            SYMBOL,

        "payloadHash":
            object_hash(payload),

        "envelopeHash":
            object_hash(envelope),

        "authorizationHash":
            RUNTIME["authorization_hash"],

        "armingHash":
            RUNTIME["arming_hash"],

        "transport":
            "SYNTHETIC_ONLY",

        "committed":
            True,

        "networkTransmitted":
            False,

        "exchangeContactedForWrite":
            False,

        "leverageMutated":
            False,

        "realOrderSent":
            False,

        "committedAt":
            now_ms(),
    }

    COUNTERS[
        "synthetic_dispatches"
    ] += 1

    COUNTERS[
        "synthetic_commits"
    ] += 1

    RUNTIME[
        "synthetic_commit_complete"
    ] = True

    return commit


# =====================================================================================
# RECEIPT
# =====================================================================================

def build_receipt(commit):

    return {
        "version":
            VERSION,

        "type":
            "FINAL_ARMING_SYNTHETIC_RECEIPT",

        "commitHash":
            object_hash(commit),

        "transport":
            "SYNTHETIC_ONLY",

        "authorizationConsumed":
            True,

        "armingTokenConsumed":
            True,

        "networkTransmitted":
            False,

        "exchangeContactedForWrite":
            False,

        "leverageMutationPerformed":
            False,

        "realOrderSent":
            False,

        "networkWriteCounter":
            COUNTERS["network_writes"],

        "leverageMutationCounter":
            COUNTERS["leverage_mutations"],

        "realOrderCounter":
            COUNTERS["real_orders"],

        "targetLong":
            TARGET_LONG_LEVERAGE,

        "targetShort":
            TARGET_SHORT_LEVERAGE,
    }


# =====================================================================================
# R34H VALIDATION
# =====================================================================================

def run_validation():

    print()
    print_header(
        "R34H: MAIN.PY ENTERED"
    )

    print(
        f"R34H: SYMBOL={SYMBOL}",
        flush=True
    )

    print(
        f"R34H: VERSION={VERSION}",
        flush=True
    )

    print(
        f"R34H: HEALTH PORT={HEALTH_PORT}",
        flush=True
    )

    print(
        "R34H: FINAL ARMING GATE ENABLED",
        flush=True
    )

    print(
        "R34H: SYNTHETIC TRANSPORT ONLY",
        flush=True
    )

    print(
        "R34H: REAL HTTP POST ABSENT",
        flush=True
    )

    print(
        "R34H: EXCHANGE WRITES DISABLED",
        flush=True
    )

    print(
        "R34H: LEVERAGE MUTATION DISABLED",
        flush=True
    )

    print(
        "R34H: REAL ORDER EXECUTION DISABLED",
        flush=True
    )

    print(
        f"R34H: OBSERVED LONG="
        f"{OBSERVED_LONG_LEVERAGE}x",
        flush=True
    )

    print(
        f"R34H: OBSERVED SHORT="
        f"{OBSERVED_SHORT_LEVERAGE}x",
        flush=True
    )

    print(
        f"R34H: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True
    )

    print(
        f"R34H: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True
    )

    # =========================================================================
    # TEST 1
    # =========================================================================

    print_header(
        "R34H TEST 1: ABSOLUTE SAFETY CONFIGURATION"
    )

    check(
        "Synthetic Only Is Enabled",
        SYNTHETIC_ONLY is True
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY is True
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION is False
    )

    check(
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES is False
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False
    )

    check(
        "Final Arming Is Required",
        FINAL_ARMING_REQUIRED is True
    )

    # =========================================================================
    # TEST 2
    # =========================================================================

    print_header(
        "R34H TEST 2: VALIDATED LIVE STATE"
    )

    live_state = build_live_state()

    RUNTIME["initial_state_hash"] = object_hash(
        live_state
    )

    check(
        "State Symbol Is BTCUSDT",
        live_state["symbol"] == SYMBOL
    )

    check(
        "State Margin Is ISOLATED",
        live_state["marginType"] == MARGIN_TYPE
    )

    check(
        "Observed Long Leverage Is 50x",
        live_state[
            "isolatedLongLeverage"
        ] == 50
    )

    check(
        "Observed Short Leverage Is 20x",
        live_state[
            "isolatedShortLeverage"
        ] == 20
    )

    check(
        "No Position Is Open",
        live_state["openPositions"] == 0
    )

    check(
        "State Is Authenticated",
        live_state["authenticated"] is True
    )

    check(
        "State Is Read-Only",
        live_state["readOnly"] is True
    )

    # =========================================================================
    # TEST 3
    # =========================================================================

    print_header(
        "R34H TEST 3: FRESH STATE VALIDATION"
    )

    check(
        "Validated State Is Fresh",
        state_is_fresh(live_state)
    )

    RUNTIME[
        "fresh_state_validated"
    ] = True

    RUNTIME[
        "open_positions"
    ] = live_state["openPositions"]

    # =========================================================================
    # TEST 4
    # =========================================================================

    print_header(
        "R34H TEST 4: CORRECTION REQUIREMENT"
    )

    correction_required = (
        live_state[
            "isolatedLongLeverage"
        ] != TARGET_LONG_LEVERAGE
        or
        live_state[
            "isolatedShortLeverage"
        ] != TARGET_SHORT_LEVERAGE
    )

    RUNTIME[
        "correction_required"
    ] = correction_required

    check(
        "Leverage Correction Is Required",
        correction_required
    )

    check(
        "Correction Preconditions Hold",
        live_state["openPositions"] == 0
    )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE == 100
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE == 100
    )

    RUNTIME[
        "correction_ready"
    ] = True

    # =========================================================================
    # TEST 5
    # =========================================================================

    print_header(
        "R34H TEST 5: EXACT V3 CORRECTION PAYLOAD"
    )

    payload = build_payload()

    RUNTIME[
        "payload_hash"
    ] = object_hash(payload)

    check(
        "Payload Symbol Is BTCUSDT",
        payload["symbol"] == SYMBOL
    )

    check(
        "Payload Margin Type Is ISOLATED",
        payload["marginType"] == "ISOLATED"
    )

    check(
        "Payload Long Leverage Is Exactly 100",
        payload[
            "isolatedLongLeverage"
        ] == "100"
    )

    check(
        "Payload Short Leverage Is Exactly 100",
        payload[
            "isolatedShortLeverage"
        ] == "100"
    )

    print(
        "R34H: PAYLOAD="
        + canonical_json(payload),
        flush=True
    )

    print(
        "R34H: PAYLOAD SHA256="
        + RUNTIME["payload_hash"],
        flush=True
    )

    # =========================================================================
    # TEST 6
    # =========================================================================

    print_header(
        "R34H TEST 6: OFFLINE V3 ENVELOPE"
    )

    envelope = build_envelope(
        live_state,
        payload
    )

    RUNTIME[
        "envelope_hash"
    ] = object_hash(envelope)

    check(
        "Envelope Method Is POST",
        envelope["method"] == "POST"
    )

    check(
        "Envelope Uses Exact V3 Leverage Path",
        envelope["path"] == LEVERAGE_PATH
    )

    check(
        "Envelope Transport Is Synthetic Only",
        envelope["transport"]
        == "SYNTHETIC_ONLY"
    )

    check(
        "Envelope Payload Hash Matches",
        envelope["payloadHash"]
        == object_hash(payload)
    )

    check(
        "Envelope Live State Hash Matches",
        envelope["liveStateHash"]
        == object_hash(live_state)
    )

    check(
        "Envelope Forbids Network Write",
        envelope[
            "networkWriteAllowed"
        ] is False
    )

    check(
        "Envelope Forbids Leverage Mutation",
        envelope[
            "leverageMutationAllowed"
        ] is False
    )

    print(
        "R34H: ENVELOPE SHA256="
        + RUNTIME["envelope_hash"],
        flush=True
    )

    # =========================================================================
    # TEST 7
    # =========================================================================

    print_header(
        "R34H TEST 7: OFFLINE SIGNATURE"
    )

    headers = envelope["headers"]

    check(
        "ACCESS-KEY Header Is Present",
        bool(headers["ACCESS-KEY"])
    )

    check(
        "ACCESS-SIGN Header Is Present",
        bool(headers["ACCESS-SIGN"])
    )

    check(
        "ACCESS-PASSPHRASE Header Is Present",
        bool(headers["ACCESS-PASSPHRASE"])
    )

    check(
        "ACCESS-TIMESTAMP Header Is Present",
        bool(headers["ACCESS-TIMESTAMP"])
    )

    body = canonical_json(payload)

    recomputed_signature = (
        build_offline_signature(
            timestamp=int(
                headers["ACCESS-TIMESTAMP"]
            ),
            method="POST",
            path=LEVERAGE_PATH,
            body=body,
        )
    )

    check(
        "Envelope Signature Recomputes Exactly",
        headers["ACCESS-SIGN"]
        == recomputed_signature
    )

    # =========================================================================
    # TEST 8
    # =========================================================================

    print_header(
        "R34H TEST 8: PRE-WRITE AUTHORIZATION"
    )

    authorization = build_authorization(
        live_state,
        payload,
        envelope
    )

    RUNTIME[
        "authorization_hash"
    ] = object_hash(authorization)

    check(
        "Authorization Is Initially Unconsumed",
        authorization["consumed"] is False
    )

    check(
        "Authorization Is Synthetic Only",
        authorization["syntheticOnly"] is True
    )

    check(
        "Authorization Forbids Exchange Write",
        authorization[
            "networkWriteAllowed"
        ] is False
    )

    check(
        "Authorization Forbids Mutation",
        authorization[
            "mutationAllowed"
        ] is False
    )

    check(
        "Authorization Validation Passes",
        validate_authorization(
            authorization,
            live_state,
            payload,
            envelope
        )
    )

    print(
        "R34H: AUTHORIZATION SHA256="
        + RUNTIME["authorization_hash"],
        flush=True
    )

    RUNTIME[
        "pre_write_gate_validated"
    ] = True

    # =========================================================================
    # TEST 9
    # =========================================================================

    print_header(
        "R34H TEST 9: FINAL ARMING TOKEN"
    )

    arming_token = create_final_arming_token(
        live_state,
        payload,
        envelope,
        authorization
    )

    RUNTIME[
        "arming_hash"
    ] = object_hash(arming_token)

    check(
        "Exactly One Final Arming Token Was Created",
        COUNTERS["arming_tokens_created"] == 1
    )

    check(
        "Final Arming Token Is Initially Unconsumed",
        arming_token["consumed"] is False
    )

    check(
        "Final Arming Token Is Synthetic Only",
        arming_token[
            "syntheticOnly"
        ] is True
    )

    check(
        "Final Arming Token Forbids Network Write",
        arming_token[
            "networkWriteAllowed"
        ] is False
    )

    check(
        "Final Arming Token Forbids Leverage Mutation",
        arming_token[
            "leverageMutationAllowed"
        ] is False
    )

    check(
        "Final Arming Token Forbids Real Order",
        arming_token[
            "realOrderAllowed"
        ] is False
    )

    check(
        "Final Arming Token Validation Passes",
        validate_final_arming_token(
            arming_token,
            live_state,
            payload,
            envelope,
            authorization
        )
    )

    print(
        "R34H: ARMING SHA256="
        + RUNTIME["arming_hash"],
        flush=True
    )

    RUNTIME[
        "final_arming_validated"
    ] = True

    # =========================================================================
    # TEST 10
    # =========================================================================

    print_header(
        "R34H TEST 10: ARMING PAYLOAD BINDING"
    )

    check(
        "Arming Token Binds Exact Payload",
        arming_token["payloadHash"]
        == object_hash(payload)
    )

    check(
        "Arming Token Binds Exact Envelope",
        arming_token["envelopeHash"]
        == object_hash(envelope)
    )

    check(
        "Arming Token Binds Fresh State",
        arming_token["liveStateHash"]
        == object_hash(live_state)
    )

    check(
        "Arming Token Binds Authorization",
        arming_token["authorizationHash"]
        == object_hash(authorization)
    )

    # =========================================================================
    # TEST 11
    # =========================================================================

    print_header(
        "R34H TEST 11: STALE STATE REJECTION"
    )

    stale_state = deepcopy(live_state)

    stale_state["retrievedAt"] = (
        int(time.time())
        -
        STATE_MAX_AGE_SECONDS
        -
        10
    )

    check(
        "Synthetic Stale State Is Rejected",
        not state_is_fresh(stale_state)
    )

    COUNTERS[
        "stale_state_blocks"
    ] += 1

    check(
        "Stale State Block Counter Is One",
        COUNTERS["stale_state_blocks"] == 1
    )

    check(
        "Original State Remains Fresh",
        state_is_fresh(live_state)
    )

    # =========================================================================
    # TEST 12
    # =========================================================================

    print_header(
        "R34H TEST 12: PAYLOAD TAMPER REJECTION"
    )

    tampered_payload = deepcopy(payload)

    tampered_payload[
        "isolatedLongLeverage"
    ] = "99"

    check(
        "Tampered Payload Hash Differs",
        object_hash(tampered_payload)
        !=
        object_hash(payload)
    )

    check(
        "Arming Token Rejects Tampered Payload",
        not validate_final_arming_token(
            arming_token,
            live_state,
            tampered_payload,
            envelope,
            authorization
        )
    )

    COUNTERS[
        "payload_tamper_blocks"
    ] += 1

    # =========================================================================
    # TEST 13
    # =========================================================================

    print_header(
        "R34H TEST 13: ENVELOPE TAMPER REJECTION"
    )

    tampered_envelope = deepcopy(envelope)

    tampered_envelope["path"] = (
        "/tampered/path"
    )

    check(
        "Tampered Envelope Hash Differs",
        object_hash(tampered_envelope)
        !=
        object_hash(envelope)
    )

    check(
        "Arming Token Rejects Tampered Envelope",
        not validate_final_arming_token(
            arming_token,
            live_state,
            payload,
            tampered_envelope,
            authorization
        )
    )

    COUNTERS[
        "envelope_tamper_blocks"
    ] += 1

    # =========================================================================
    # TEST 14
    # =========================================================================

    print_header(
        "R34H TEST 14: FINAL COMMIT GATE"
    )

    check(
        "Fresh State Is Still Valid",
        state_is_fresh(live_state)
    )

    check(
        "Correction Is Still Required",
        RUNTIME[
            "correction_required"
        ] is True
    )

    check(
        "Correction Is Ready",
        RUNTIME[
            "correction_ready"
        ] is True
    )

    check(
        "No Position Is Open",
        RUNTIME[
            "open_positions"
        ] == 0
    )

    check(
        "Pre-Write Gate Is Validated",
        RUNTIME[
            "pre_write_gate_validated"
        ] is True
    )

    check(
        "Final Arming Gate Is Validated",
        RUNTIME[
            "final_arming_validated"
        ] is True
    )

    RUNTIME[
        "commit_gate_validated"
    ] = True

    # =========================================================================
    # TEST 15
    # =========================================================================

    print_header(
        "R34H TEST 15: ONE SYNTHETIC FINAL COMMIT"
    )

    commit = synthetic_commit(
        live_state,
        payload,
        envelope,
        authorization,
        arming_token,
    )

    RUNTIME[
        "commit_hash"
    ] = object_hash(commit)

    check(
        "Exactly One Synthetic Commit Occurred",
        COUNTERS[
            "synthetic_commits"
        ] == 1
    )

    check(
        "Exactly One Synthetic Dispatch Occurred",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1
    )

    check(
        "Authorization Was Consumed Exactly Once",
        authorization[
            "consumed"
        ] is True
    )

    check(
        "Final Arming Token Was Consumed Exactly Once",
        arming_token[
            "consumed"
        ] is True
    )

    check(
        "Synthetic Commit Reports No Network Transmission",
        commit[
            "networkTransmitted"
        ] is False
    )

    check(
        "Synthetic Commit Reports No Exchange Write",
        commit[
            "exchangeContactedForWrite"
        ] is False
    )

    check(
        "Synthetic Commit Reports No Leverage Mutation",
        commit[
            "leverageMutated"
        ] is False
    )

    print(
        "R34H: COMMIT SHA256="
        + RUNTIME["commit_hash"],
        flush=True
    )

    # =========================================================================
    # TEST 16
    # =========================================================================

    print_header(
        "R34H TEST 16: ARMING REPLAY REJECTION"
    )

    replay_rejected = False

    try:

        synthetic_commit(
            live_state,
            payload,
            envelope,
            authorization,
            arming_token,
        )

    except RuntimeError:

        replay_rejected = True

    check(
        "Consumed Final Commit Replay Is Rejected",
        replay_rejected
    )

    check(
        "Synthetic Commit Counter Remains One",
        COUNTERS[
            "synthetic_commits"
        ] == 1
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        COUNTERS[
            "synthetic_dispatches"
        ] == 1
    )

    # =========================================================================
    # TEST 17
    # =========================================================================

    print_header(
        "R34H TEST 17: SYNTHETIC FINAL RECEIPT"
    )

    receipt = build_receipt(commit)

    RUNTIME[
        "receipt_hash"
    ] = object_hash(receipt)

    check(
        "Receipt Transport Is Synthetic Only",
        receipt["transport"]
        == "SYNTHETIC_ONLY"
    )

    check(
        "Receipt Confirms Authorization Consumed",
        receipt[
            "authorizationConsumed"
        ] is True
    )

    check(
        "Receipt Confirms Arming Token Consumed",
        receipt[
            "armingTokenConsumed"
        ] is True
    )

    check(
        "Receipt Confirms No Network Transmission",
        receipt[
            "networkTransmitted"
        ] is False
    )

    check(
        "Receipt Confirms No Exchange Write",
        receipt[
            "exchangeContactedForWrite"
        ] is False
    )

    check(
        "Receipt Confirms No Leverage Mutation",
        receipt[
            "leverageMutationPerformed"
        ] is False
    )

    check(
        "Receipt Network Write Counter Is Zero",
        receipt[
            "networkWriteCounter"
        ] == 0
    )

    check(
        "Receipt Leverage Mutation Counter Is Zero",
        receipt[
            "leverageMutationCounter"
        ] == 0
    )

    check(
        "Receipt Real Order Counter Is Zero",
        receipt[
            "realOrderCounter"
        ] == 0
    )

    print(
        "R34H: RECEIPT SHA256="
        + RUNTIME["receipt_hash"],
        flush=True
    )

    # =========================================================================
    # TEST 18
    # =========================================================================

    print_header(
        "R34H TEST 18: FINAL WRITE-FREE INVARIANTS"
    )

    check(
        "Real Order Counter Is Zero",
        COUNTERS["real_orders"] == 0
    )

    check(
        "Network Write Counter Is Zero",
        COUNTERS["network_writes"] == 0
    )

    check(
        "Leverage Mutation Counter Is Zero",
        COUNTERS[
            "leverage_mutations"
        ] == 0
    )

    check(
        "Exactly One Arming Token Was Created",
        COUNTERS[
            "arming_tokens_created"
        ] == 1
    )

    check(
        "Exactly One Arming Token Was Consumed",
        COUNTERS[
            "arming_tokens_consumed"
        ] == 1
    )

    check(
        "Exactly One Synthetic Commit Is Recorded",
        COUNTERS[
            "synthetic_commits"
        ] == 1
    )

    check(
        "Payload Tamper Rejection Was Exercised",
        COUNTERS[
            "payload_tamper_blocks"
        ] == 1
    )

    check(
        "Envelope Tamper Rejection Was Exercised",
        COUNTERS[
            "envelope_tamper_blocks"
        ] == 1
    )

    check(
        "Stale State Rejection Was Exercised",
        COUNTERS[
            "stale_state_blocks"
        ] == 1
    )

    check(
        "Final Commit Gate Is Validated",
        RUNTIME[
            "commit_gate_validated"
        ] is True
    )

    # =========================================================================
    # TERMINAL STATE
    # =========================================================================

    RUNTIME[
        "phase"
    ] = "FINAL_ARMED_SYNTHETIC_COMMIT_VALIDATED"

    print_header(
        "R34H: VALIDATION COMPLETE"
    )

    print(
        "R34H: PHASE="
        + RUNTIME["phase"],
        flush=True
    )

    print(
        "R34H: AUTHENTICATED GETS="
        + str(
            COUNTERS["authenticated_gets"]
        ),
        flush=True
    )

    print(
        f"R34H: OBSERVED MARGIN={MARGIN_TYPE}",
        flush=True
    )

    print(
        f"R34H: OBSERVED LONG="
        f"{OBSERVED_LONG_LEVERAGE}x",
        flush=True
    )

    print(
        f"R34H: OBSERVED SHORT="
        f"{OBSERVED_SHORT_LEVERAGE}x",
        flush=True
    )

    print(
        f"R34H: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True
    )

    print(
        f"R34H: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True
    )

    print(
        "R34H: OPEN POSITIONS="
        + str(
            RUNTIME["open_positions"]
        ),
        flush=True
    )

    print(
        "R34H: CORRECTION REQUIRED="
        + str(
            RUNTIME[
                "correction_required"
            ]
        ),
        flush=True
    )

    print(
        "R34H: CORRECTION READY="
        + str(
            RUNTIME[
                "correction_ready"
            ]
        ),
        flush=True
    )

    print(
        "R34H: FRESH STATE VALIDATED="
        + str(
            RUNTIME[
                "fresh_state_validated"
            ]
        ),
        flush=True
    )

    print(
        "R34H: PRE-WRITE GATE VALIDATED="
        + str(
            RUNTIME[
                "pre_write_gate_validated"
            ]
        ),
        flush=True
    )

    print(
        "R34H: FINAL ARMING VALIDATED="
        + str(
            RUNTIME[
                "final_arming_validated"
            ]
        ),
        flush=True
    )

    print(
        "R34H: COMMIT GATE VALIDATED="
        + str(
            RUNTIME[
                "commit_gate_validated"
            ]
        ),
        flush=True
    )

    print(
        "R34H: INITIAL STATE SHA256="
        + RUNTIME[
            "initial_state_hash"
        ],
        flush=True
    )

    print(
        "R34H: PAYLOAD SHA256="
        + RUNTIME[
            "payload_hash"
        ],
        flush=True
    )

    print(
        "R34H: ENVELOPE SHA256="
        + RUNTIME[
            "envelope_hash"
        ],
        flush=True
    )

    print(
        "R34H: AUTHORIZATION SHA256="
        + RUNTIME[
            "authorization_hash"
        ],
        flush=True
    )

    print(
        "R34H: ARMING SHA256="
        + RUNTIME[
            "arming_hash"
        ],
        flush=True
    )

    print(
        "R34H: COMMIT SHA256="
        + RUNTIME[
            "commit_hash"
        ],
        flush=True
    )

    print(
        "R34H: RECEIPT SHA256="
        + RUNTIME[
            "receipt_hash"
        ],
        flush=True
    )

    print(
        "R34H: SYNTHETIC DISPATCHES="
        + str(
            COUNTERS[
                "synthetic_dispatches"
            ]
        ),
        flush=True
    )

    print(
        "R34H: SYNTHETIC COMMITS="
        + str(
            COUNTERS[
                "synthetic_commits"
            ]
        ),
        flush=True
    )

    print(
        "R34H: ARMING TOKENS CREATED="
        + str(
            COUNTERS[
                "arming_tokens_created"
            ]
        ),
        flush=True
    )

    print(
        "R34H: ARMING TOKENS CONSUMED="
        + str(
            COUNTERS[
                "arming_tokens_consumed"
            ]
        ),
        flush=True
    )

    print(
        "R34H: NETWORK WRITES="
        + str(
            COUNTERS[
                "network_writes"
            ]
        ),
        flush=True
    )

    print(
        "R34H: REAL ORDERS="
        + str(
            COUNTERS[
                "real_orders"
            ]
        ),
        flush=True
    )

    print(
        "R34H: LEVERAGE MUTATIONS="
        + str(
            COUNTERS[
                "leverage_mutations"
            ]
        ),
        flush=True
    )

    print(
        "R34H: FINAL ARMING + SYNTHETIC "
        "COMMIT GATE VALIDATED",
        flush=True
    )

    print(
        "R34H: NO REAL ORDER WAS SENT",
        flush=True
    )

    print(
        "R34H: NO EXCHANGE WRITE WAS SENT",
        flush=True
    )

    print(
        "R34H: NO LEVERAGE MUTATION WAS PERFORMED",
        flush=True
    )

    print(
        "R34H: REAL HTTP POST DOES NOT "
        "EXIST IN THIS BUILD",
        flush=True
    )

    print(SEPARATOR, flush=True)


# =====================================================================================
# HEARTBEAT
# =====================================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        print()
        print(SEPARATOR, flush=True)

        print(
            f"R34H: HEARTBEAT {heartbeat}"
            f" | phase={RUNTIME['phase']}"
            f" | synthetic-only={SYNTHETIC_ONLY}"
            f" | authenticated-read-only={AUTHENTICATED_READ_ONLY}"
            f" | authenticated-get={COUNTERS['authenticated_gets']}"
            f" | real-execution={REAL_ORDER_EXECUTION}"
            f" | network-writes={EXCHANGE_NETWORK_WRITES}"
            f" | network-write-counter={COUNTERS['network_writes']}"
            f" | leverage-mutation={LEVERAGE_MUTATION_ENABLED}"
            f" | leverage-mutation-counter={COUNTERS['leverage_mutations']}"
            f" | synthetic-dispatch={COUNTERS['synthetic_dispatches']}"
            f" | synthetic-commit={COUNTERS['synthetic_commits']}"
            f" | authorization-consumed={RUNTIME['authorization_consumed']}"
            f" | arming-consumed={RUNTIME['arming_token_consumed']}"
            f" | fresh-state={RUNTIME['fresh_state_validated']}"
            f" | open-positions={RUNTIME['open_positions']}"
            f" | correction-required={RUNTIME['correction_required']}"
            f" | correction-ready={RUNTIME['correction_ready']}"
            f" | pre-write-gate={RUNTIME['pre_write_gate_validated']}"
            f" | final-arming={RUNTIME['final_arming_validated']}"
            f" | commit-gate={RUNTIME['commit_gate_validated']}"
            f" | observed-margin={MARGIN_TYPE}"
            f" | observed-long={OBSERVED_LONG_LEVERAGE}x"
            f" | observed-short={OBSERVED_SHORT_LEVERAGE}x"
            f" | target-long={TARGET_LONG_LEVERAGE}x"
            f" | target-short={TARGET_SHORT_LEVERAGE}x",
            flush=True
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# =====================================================================================
# MAIN
# =====================================================================================

def main():

    start_health_server()

    run_validation()

    heartbeat_loop()


if __name__ == "__main__":
    main()
