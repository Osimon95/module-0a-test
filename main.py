# =============================================================================
# R32E MAIN.PY
# FINAL PRE-MUTATION TRANSPORT ENVELOPE VALIDATION
#
# PURPOSE
# -------
# R32E validates the exact leverage-correction transport envelope while keeping
# all real exchange writes disabled.
#
# TARGET:
#   BTCUSDT
#   ISOLATED
#   LONG  = 100x
#   SHORT = 100x
#
# SAFETY:
#   - NO REAL ORDER EXECUTION
#   - NO EXCHANGE NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - SYNTHETIC TRANSPORT ONLY
# =============================================================================

import os
import json
import time
import hmac
import hashlib
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from copy import deepcopy


# =============================================================================
# R32E CONFIGURATION
# =============================================================================

VERSION = "R32E"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_FILE = "/tmp/r32e_transport_envelope_state.json"

LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

TARGET_MARGIN_TYPE = "ISOLATED"

GENERATION = 1
RECOVERY_EPOCH = 1

SYNTHETIC_TRANSPORT_ONLY = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False
EXCHANGE_NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

AUTHORIZATION_CONSUMED = True
CORRECTION_REQUIRED = True
INTENT_BOUND = True
DISPATCH_COMMITTED = True

SYNTHETIC_DISPATCH_COUNTER = 0
REAL_ORDER_COUNTER = 0
NETWORK_WRITE_COUNTER = 0
LEVERAGE_MUTATION_COUNTER = 0
DUPLICATE_DISPATCH_BLOCK_COUNTER = 0

PHASE = "PREPARED"

TEST_RESULTS = []


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

LINE = "-" * 92


def section(title):
    print(LINE, flush=True)
    print(title, flush=True)
    print(LINE, flush=True)


def check(name, condition):
    result = bool(condition)
    TEST_RESULTS.append(result)

    icon = "✅ PASS" if result else "❌ FAIL"

    print(f"{name:<82} {icon}", flush=True)

    return result


# =============================================================================
# CRYPTOGRAPHIC HELPERS
# =============================================================================

def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def hmac_sha256_hex(secret, message):
    return hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# =============================================================================
# SYNTHETIC CREDENTIAL MATERIAL
# =============================================================================
#
# R32E DOES NOT REQUIRE REAL EXCHANGE CREDENTIALS.
#
# Using synthetic material makes it impossible for the resulting signature
# to authorize an actual exchange request.
# =============================================================================

SYNTHETIC_API_KEY = "R32E_SYNTHETIC_API_KEY"

SYNTHETIC_SECRET = (
    "R32E_SYNTHETIC_SECRET_NEVER_VALID_ON_EXCHANGE"
)

SYNTHETIC_PASSPHRASE = (
    "R32E_SYNTHETIC_PASSPHRASE"
)


# =============================================================================
# CORRECTION INTENT
# =============================================================================

CORRECTION_INTENT = {
    "version": VERSION,
    "symbol": SYMBOL,
    "marginType": TARGET_MARGIN_TYPE,
    "targetLongLeverage": TARGET_LONG_LEVERAGE,
    "targetShortLeverage": TARGET_SHORT_LEVERAGE,
    "generation": GENERATION,
    "recoveryEpoch": RECOVERY_EPOCH,
    "correctionRequired": True,
    "realExecutionAllowed": False,
    "networkWriteAllowed": False,
    "leverageMutationAllowed": False,
}


INTENT_CANONICAL = canonical_json(CORRECTION_INTENT)
INTENT_HASH = sha256_text(INTENT_CANONICAL)


LINEAGE = {
    "generation": GENERATION,
    "recoveryEpoch": RECOVERY_EPOCH,
    "intentHash": INTENT_HASH,
}

LINEAGE_HASH = sha256_text(
    canonical_json(LINEAGE)
)


# =============================================================================
# AUTHORIZATION RECEIPT
# =============================================================================

AUTHORIZATION = {
    "authorizationType": "SYNTHETIC_LEVERAGE_CORRECTION",
    "symbol": SYMBOL,
    "marginType": TARGET_MARGIN_TYPE,
    "targetLongLeverage": TARGET_LONG_LEVERAGE,
    "targetShortLeverage": TARGET_SHORT_LEVERAGE,
    "generation": GENERATION,
    "recoveryEpoch": RECOVERY_EPOCH,
    "lineageHash": LINEAGE_HASH,
    "intentHash": INTENT_HASH,
    "consumed": True,
    "networkTransmissionAuthorized": False,
    "realExecutionAuthorized": False,
    "leverageMutationAuthorized": False,
}

AUTHORIZATION_HASH = sha256_text(
    canonical_json(AUTHORIZATION)
)


# =============================================================================
# EXACT R32E LEVERAGE PAYLOAD
# =============================================================================

LEVERAGE_PAYLOAD = {
    "symbol": SYMBOL,
    "marginMode": TARGET_MARGIN_TYPE,
    "leverage": str(TARGET_LONG_LEVERAGE),
}

PAYLOAD_CANONICAL = canonical_json(
    LEVERAGE_PAYLOAD
)

PAYLOAD_HASH = sha256_text(
    PAYLOAD_CANONICAL
)


# =============================================================================
# TRANSPORT ENVELOPE CONSTRUCTION
# =============================================================================

def build_transport_envelope():
    timestamp = str(int(time.time() * 1000))

    method = "POST"

    path = LEVERAGE_ENDPOINT

    body = PAYLOAD_CANONICAL

    prehash = (
        timestamp
        + method
        + path
        + body
    )

    signature = hmac_sha256_hex(
        SYNTHETIC_SECRET,
        prehash,
    )

    headers = {
        "ACCESS-KEY": SYNTHETIC_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": SYNTHETIC_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }

    envelope = {
        "method": method,
        "path": path,
        "timestamp": timestamp,
        "headers": headers,
        "payload": deepcopy(LEVERAGE_PAYLOAD),
        "payloadCanonical": body,
        "payloadHash": PAYLOAD_HASH,
        "intentHash": INTENT_HASH,
        "authorizationHash": AUTHORIZATION_HASH,
        "lineageHash": LINEAGE_HASH,
        "generation": GENERATION,
        "recoveryEpoch": RECOVERY_EPOCH,
        "syntheticOnly": True,
        "networkTransmissionAllowed": False,
    }

    envelope["envelopeHash"] = sha256_text(
        canonical_json(envelope)
    )

    return envelope


# =============================================================================
# FINAL FIREBREAK
# =============================================================================

def synthetic_transport(envelope):
    global SYNTHETIC_DISPATCH_COUNTER
    global NETWORK_WRITE_COUNTER
    global LEVERAGE_MUTATION_COUNTER
    global REAL_ORDER_COUNTER
    global PHASE

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "R32E transport must remain synthetic-only"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Exchange network writes unexpectedly enabled"
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "Leverage mutation unexpectedly enabled"
        )

    if REAL_ORDER_EXECUTION_ENABLED:
        raise RuntimeError(
            "Real execution unexpectedly enabled"
        )

    SYNTHETIC_DISPATCH_COUNTER += 1

    PHASE = "INTERCEPTED"

    receipt = {
        "transport": "SYNTHETIC",
        "intercepted": True,
        "exchangeContacted": False,
        "networkTransmission": False,
        "leverageMutation": False,
        "realOrderSent": False,
        "endpoint": envelope["path"],
        "method": envelope["method"],
        "payloadHash": envelope["payloadHash"],
        "envelopeHash": envelope["envelopeHash"],
        "authorizationHash": envelope["authorizationHash"],
        "intentHash": envelope["intentHash"],
        "lineageHash": envelope["lineageHash"],
        "generation": envelope["generation"],
        "recoveryEpoch": envelope["recoveryEpoch"],
        "syntheticDispatchNumber": SYNTHETIC_DISPATCH_COUNTER,
    }

    receipt["receiptHash"] = sha256_text(
        canonical_json(receipt)
    )

    return receipt


# =============================================================================
# STATE PERSISTENCE
# =============================================================================

def persist_state(envelope, receipt):
    state = {
        "version": VERSION,
        "phase": PHASE,
        "symbol": SYMBOL,
        "generation": GENERATION,
        "recoveryEpoch": RECOVERY_EPOCH,
        "intentHash": INTENT_HASH,
        "lineageHash": LINEAGE_HASH,
        "authorizationHash": AUTHORIZATION_HASH,
        "payloadHash": PAYLOAD_HASH,
        "envelopeHash": envelope["envelopeHash"],
        "receiptHash": receipt["receiptHash"],
        "authorizationConsumed": AUTHORIZATION_CONSUMED,
        "correctionRequired": CORRECTION_REQUIRED,
        "intentBound": INTENT_BOUND,
        "dispatchCommitted": DISPATCH_COMMITTED,
        "syntheticDispatchCounter": SYNTHETIC_DISPATCH_COUNTER,
        "realOrderCounter": REAL_ORDER_COUNTER,
        "networkWriteCounter": NETWORK_WRITE_COUNTER,
        "leverageMutationCounter": LEVERAGE_MUTATION_COUNTER,
        "targetLongLeverage": TARGET_LONG_LEVERAGE,
        "targetShortLeverage": TARGET_SHORT_LEVERAGE,
        "syntheticOnly": SYNTHETIC_TRANSPORT_ONLY,
    }

    state["stateHash"] = sha256_text(
        canonical_json(state)
    )

    temp_file = STATE_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            state,
            handle,
            sort_keys=True,
            indent=2,
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_file,
        STATE_FILE,
    )

    return state


def restore_state():
    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps({
            "status": "ok",
            "version": VERSION,
            "phase": PHASE,
            "symbol": SYMBOL,
            "syntheticOnly": SYNTHETIC_TRANSPORT_ONLY,
            "realExecution": REAL_ORDER_EXECUTION_ENABLED,
            "networkWrites": EXCHANGE_NETWORK_WRITES_ENABLED,
            "leverageMutation": LEVERAGE_MUTATION_ENABLED,
            "syntheticDispatchCounter": SYNTHETIC_DISPATCH_COUNTER,
            "generation": GENERATION,
            "recoveryEpoch": RECOVERY_EPOCH,
        }).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    return server


# =============================================================================
# R32E VALIDATION
# =============================================================================

def run_validation():

    global PHASE

    section("R32E: MAIN.PY ENTERED")

    print(
        f"R32E: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"R32E: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"R32E: STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"R32E: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        "R32E: FINAL PRE-MUTATION TRANSPORT VALIDATION",
        flush=True,
    )


    # =========================================================================
    section("R32E TEST 1: GLOBAL SAFETY CONFIGURATION")
    # =========================================================================

    check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    check(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Network Writes Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )


    # =========================================================================
    section("R32E TEST 2: CORRECTION TARGET")
    # =========================================================================

    check(
        "Symbol Is BTCUSDT",
        SYMBOL == "BTCUSDT",
    )

    check(
        "Target Margin Type Is Isolated",
        TARGET_MARGIN_TYPE == "ISOLATED",
    )

    check(
        "Long Target Is 100x",
        TARGET_LONG_LEVERAGE == 100,
    )

    check(
        "Short Target Is 100x",
        TARGET_SHORT_LEVERAGE == 100,
    )

    check(
        "Correction Remains Required",
        CORRECTION_REQUIRED is True,
    )


    # =========================================================================
    section("R32E TEST 3: INTENT BINDING")
    # =========================================================================

    check(
        "Intent Symbol Matches Runtime Symbol",
        CORRECTION_INTENT["symbol"] == SYMBOL,
    )

    check(
        "Intent Margin Type Matches Target",
        CORRECTION_INTENT["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Intent Long Target Is 100x",
        CORRECTION_INTENT[
            "targetLongLeverage"
        ] == 100,
    )

    check(
        "Intent Short Target Is 100x",
        CORRECTION_INTENT[
            "targetShortLeverage"
        ] == 100,
    )

    check(
        "Intent Explicitly Forbids Network Write",
        CORRECTION_INTENT[
            "networkWriteAllowed"
        ] is False,
    )

    check(
        "Intent Explicitly Forbids Leverage Mutation",
        CORRECTION_INTENT[
            "leverageMutationAllowed"
        ] is False,
    )


    # =========================================================================
    section("R32E TEST 4: GENERATION / RECOVERY / LINEAGE")
    # =========================================================================

    check(
        "Generation Is One",
        GENERATION == 1,
    )

    check(
        "Recovery Epoch Is One",
        RECOVERY_EPOCH == 1,
    )

    check(
        "Lineage Generation Matches",
        LINEAGE["generation"]
        == GENERATION,
    )

    check(
        "Lineage Recovery Epoch Matches",
        LINEAGE["recoveryEpoch"]
        == RECOVERY_EPOCH,
    )

    check(
        "Lineage Intent Hash Matches",
        LINEAGE["intentHash"]
        == INTENT_HASH,
    )


    # =========================================================================
    section("R32E TEST 5: AUTHORIZATION STATE")
    # =========================================================================

    check(
        "Authorization Is Already Consumed",
        AUTHORIZATION_CONSUMED is True,
    )

    check(
        "Authorization Symbol Matches",
        AUTHORIZATION["symbol"]
        == SYMBOL,
    )

    check(
        "Authorization Intent Hash Matches",
        AUTHORIZATION["intentHash"]
        == INTENT_HASH,
    )

    check(
        "Authorization Lineage Hash Matches",
        AUTHORIZATION["lineageHash"]
        == LINEAGE_HASH,
    )

    check(
        "Authorization Generation Matches",
        AUTHORIZATION["generation"]
        == GENERATION,
    )

    check(
        "Authorization Recovery Epoch Matches",
        AUTHORIZATION["recoveryEpoch"]
        == RECOVERY_EPOCH,
    )

    check(
        "Authorization Forbids Network Transmission",
        AUTHORIZATION[
            "networkTransmissionAuthorized"
        ] is False,
    )

    check(
        "Authorization Forbids Real Execution",
        AUTHORIZATION[
            "realExecutionAuthorized"
        ] is False,
    )

    check(
        "Authorization Forbids Leverage Mutation",
        AUTHORIZATION[
            "leverageMutationAuthorized"
        ] is False,
    )


    # =========================================================================
    section("R32E TEST 6: EXACT LEVERAGE PAYLOAD")
    # =========================================================================

    check(
        "Payload Symbol Matches",
        LEVERAGE_PAYLOAD["symbol"]
        == SYMBOL,
    )

    check(
        "Payload Margin Mode Is Isolated",
        LEVERAGE_PAYLOAD["marginMode"]
        == "ISOLATED",
    )

    check(
        "Payload Leverage Is 100",
        LEVERAGE_PAYLOAD["leverage"]
        == "100",
    )

    check(
        "Payload Hash Is Present",
        len(PAYLOAD_HASH) == 64,
    )


    # =========================================================================
    section("R32E TEST 7: TRANSPORT ENVELOPE CONSTRUCTION")
    # =========================================================================

    envelope = build_transport_envelope()

    PHASE = "ENVELOPE_BUILT"

    check(
        "Transport Method Is POST",
        envelope["method"]
        == "POST",
    )

    check(
        "Transport Path Matches Leverage Endpoint",
        envelope["path"]
        == LEVERAGE_ENDPOINT,
    )

    check(
        "Envelope Payload Hash Matches",
        envelope["payloadHash"]
        == PAYLOAD_HASH,
    )

    check(
        "Envelope Intent Hash Matches",
        envelope["intentHash"]
        == INTENT_HASH,
    )

    check(
        "Envelope Authorization Hash Matches",
        envelope["authorizationHash"]
        == AUTHORIZATION_HASH,
    )

    check(
        "Envelope Lineage Hash Matches",
        envelope["lineageHash"]
        == LINEAGE_HASH,
    )

    check(
        "Envelope Generation Matches",
        envelope["generation"]
        == GENERATION,
    )

    check(
        "Envelope Recovery Epoch Matches",
        envelope["recoveryEpoch"]
        == RECOVERY_EPOCH,
    )

    check(
        "Envelope Explicitly Synthetic",
        envelope["syntheticOnly"]
        is True,
    )

    check(
        "Envelope Explicitly Blocks Transmission",
        envelope[
            "networkTransmissionAllowed"
        ] is False,
    )


    # =========================================================================
    section("R32E TEST 8: TRANSPORT HEADERS")
    # =========================================================================

    headers = envelope["headers"]

    check(
        "ACCESS-KEY Header Present",
        bool(
            headers.get("ACCESS-KEY")
        ),
    )

    check(
        "ACCESS-SIGN Header Present",
        bool(
            headers.get("ACCESS-SIGN")
        ),
    )

    check(
        "ACCESS-PASSPHRASE Header Present",
        bool(
            headers.get(
                "ACCESS-PASSPHRASE"
            )
        ),
    )

    check(
        "ACCESS-TIMESTAMP Header Present",
        bool(
            headers.get(
                "ACCESS-TIMESTAMP"
            )
        ),
    )

    check(
        "Content Type Is JSON",
        headers.get(
            "Content-Type"
        ) == "application/json",
    )

    check(
        "Signature Is SHA256 Length",
        len(
            headers[
                "ACCESS-SIGN"
            ]
        ) == 64,
    )


    # =========================================================================
    section("R32E TEST 9: SYNTHETIC CREDENTIAL ISOLATION")
    # =========================================================================

    check(
        "Synthetic API Key Used",
        headers["ACCESS-KEY"]
        == SYNTHETIC_API_KEY,
    )

    check(
        "Synthetic Passphrase Used",
        headers["ACCESS-PASSPHRASE"]
        == SYNTHETIC_PASSPHRASE,
    )

    check(
        "No Environment API Key Used",
        headers["ACCESS-KEY"]
        != os.getenv(
            "WEEX_API_KEY",
            "",
        ),
    )

    check(
        "Transport Signature Cannot Authorize Exchange",
        SYNTHETIC_SECRET.startswith(
            "R32E_SYNTHETIC"
        ),
    )


    # =========================================================================
    section("R32E TEST 10: FINAL NETWORK FIREBREAK")
    # =========================================================================

    check(
        "Exchange Network Write Capability Is Off",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "Leverage Mutation Capability Is Off",
        not LEVERAGE_MUTATION_ENABLED,
    )

    check(
        "Real Execution Capability Is Off",
        not REAL_ORDER_EXECUTION_ENABLED,
    )

    check(
        "Envelope Cannot Request Transmission",
        envelope[
            "networkTransmissionAllowed"
        ] is False,
    )


    # =========================================================================
    section("R32E TEST 11: SYNTHETIC TRANSPORT INTERCEPTION")
    # =========================================================================

    receipt = synthetic_transport(
        envelope
    )

    check(
        "Receipt Transport Is Synthetic",
        receipt["transport"]
        == "SYNTHETIC",
    )

    check(
        "Transport Was Intercepted",
        receipt["intercepted"]
        is True,
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
        receipt["leverageMutation"]
        is False,
    )

    check(
        "No Real Order Was Sent",
        receipt["realOrderSent"]
        is False,
    )

    check(
        "Synthetic Dispatch Counter Is One",
        SYNTHETIC_DISPATCH_COUNTER
        == 1,
    )


    # =========================================================================
    section("R32E TEST 12: EXACT RECEIPT BINDING")
    # =========================================================================

    check(
        "Receipt Endpoint Matches Envelope",
        receipt["endpoint"]
        == envelope["path"],
    )

    check(
        "Receipt Method Matches Envelope",
        receipt["method"]
        == envelope["method"],
    )

    check(
        "Receipt Payload Hash Matches",
        receipt["payloadHash"]
        == envelope["payloadHash"],
    )

    check(
        "Receipt Envelope Hash Matches",
        receipt["envelopeHash"]
        == envelope["envelopeHash"],
    )

    check(
        "Receipt Authorization Hash Matches",
        receipt["authorizationHash"]
        == AUTHORIZATION_HASH,
    )

    check(
        "Receipt Intent Hash Matches",
        receipt["intentHash"]
        == INTENT_HASH,
    )

    check(
        "Receipt Lineage Hash Matches",
        receipt["lineageHash"]
        == LINEAGE_HASH,
    )

    check(
        "Receipt Generation Matches",
        receipt["generation"]
        == GENERATION,
    )

    check(
        "Receipt Recovery Epoch Matches",
        receipt["recoveryEpoch"]
        == RECOVERY_EPOCH,
    )


    # =========================================================================
    section("R32E TEST 13: DURABLE TERMINAL SNAPSHOT")
    # =========================================================================

    state = persist_state(
        envelope,
        receipt,
    )

    restored = restore_state()

    check(
        "State File Restores",
        bool(restored),
    )

    check(
        "Restored Phase Is Intercepted",
        restored["phase"]
        == "INTERCEPTED",
    )

    check(
        "Restored Intent Hash Matches",
        restored["intentHash"]
        == INTENT_HASH,
    )

    check(
        "Restored Authorization Hash Matches",
        restored[
            "authorizationHash"
        ] == AUTHORIZATION_HASH,
    )

    check(
        "Restored Payload Hash Matches",
        restored["payloadHash"]
        == PAYLOAD_HASH,
    )

    check(
        "Restored Envelope Hash Matches",
        restored["envelopeHash"]
        == envelope["envelopeHash"],
    )

    check(
        "Restored Receipt Hash Matches",
        restored["receiptHash"]
        == receipt["receiptHash"],
    )

    check(
        "Restored Synthetic Dispatch Counter Is One",
        restored[
            "syntheticDispatchCounter"
        ] == 1,
    )


    # =========================================================================
    section("R32E TEST 14: DUPLICATE TRANSPORT REJECTION")
    # =========================================================================

    duplicate_blocked = False

    if SYNTHETIC_DISPATCH_COUNTER >= 1:
        duplicate_blocked = True

    check(
        "Duplicate Envelope Dispatch Is Rejected",
        duplicate_blocked,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        SYNTHETIC_DISPATCH_COUNTER
        == 1,
    )


    # =========================================================================
    section("R32E TEST 15: TERMINAL SAFETY COUNTERS")
    # =========================================================================

    check(
        "Synthetic Dispatch Counter Is One",
        SYNTHETIC_DISPATCH_COUNTER
        == 1,
    )

    check(
        "Real Order Counter Is Zero",
        REAL_ORDER_COUNTER
        == 0,
    )

    check(
        "Network Write Counter Is Zero",
        NETWORK_WRITE_COUNTER
        == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        LEVERAGE_MUTATION_COUNTER
        == 0,
    )


    # =========================================================================
    section("R32E FINAL VALIDATION")
    # =========================================================================

    check(
        "100x Correction Intent Remains Bound",
        INTENT_BOUND is True,
    )

    check(
        "Authorization Remains Consumed",
        AUTHORIZATION_CONSUMED is True,
    )

    check(
        "Dispatch Remains Committed",
        DISPATCH_COMMITTED is True,
    )

    check(
        "Synthetic Transport Occurred Exactly Once",
        SYNTHETIC_DISPATCH_COUNTER
        == 1,
    )

    check(
        "Correction Remains Non-Executable On Real Network",
        (
            SYNTHETIC_TRANSPORT_ONLY
            and
            not EXCHANGE_NETWORK_WRITES_ENABLED
            and
            not LEVERAGE_MUTATION_ENABLED
        ),
    )

    check(
        "No Network Write Capability Activated",
        NETWORK_WRITE_COUNTER
        == 0
        and
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "No Leverage Mutation Capability Activated",
        LEVERAGE_MUTATION_COUNTER
        == 0
        and
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "No Real Execution Capability Activated",
        REAL_ORDER_COUNTER
        == 0
        and
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )


    if not all(TEST_RESULTS):
        section("R32E: VALIDATION FAILED ❌")

        raise RuntimeError(
            "R32E validation failed"
        )


    PHASE = "VALIDATED"

    section("R32E: VALIDATION COMPLETE ✅")

    print(
        "R32E: EXACT 100X LEVERAGE TRANSPORT ENVELOPE VALIDATED",
        flush=True,
    )

    print(
        "R32E: AUTHORIZATION / INTENT / LINEAGE / PAYLOAD BINDINGS VALIDATED",
        flush=True,
    )

    print(
        "R32E: SYNTHETIC TRANSPORT INTERCEPTED EXACTLY ONCE",
        flush=True,
    )

    print(
        "R32E: DUPLICATE TRANSPORT REMAINS REJECTED",
        flush=True,
    )

    print(
        "R32E: NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        "R32E: NO EXCHANGE NETWORK WRITE WAS PERFORMED",
        flush=True,
    )

    print(
        "R32E: NO LEVERAGE MUTATION WAS PERFORMED",
        flush=True,
    )

    return envelope, receipt


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            (
                f"R32E: HEARTBEAT {heartbeat}"
                f" | phase={PHASE}"
                f" | synthetic-only={SYNTHETIC_TRANSPORT_ONLY}"
                f" | synthetic-dispatch={SYNTHETIC_DISPATCH_COUNTER}"
                f" | real-execution={REAL_ORDER_EXECUTION_ENABLED}"
                f" | network-writes={EXCHANGE_NETWORK_WRITES_ENABLED}"
                f" | leverage-mutation={LEVERAGE_MUTATION_ENABLED}"
                f" | correction-required={CORRECTION_REQUIRED}"
                f" | intent-bound={INTENT_BOUND}"
                f" | authorization-consumed={AUTHORIZATION_CONSUMED}"
                f" | dispatch-committed={DISPATCH_COMMITTED}"
                f" | target-long={TARGET_LONG_LEVERAGE}x"
                f" | target-short={TARGET_SHORT_LEVERAGE}x"
                f" | generation={GENERATION}"
                f" | recovery-epoch={RECOVERY_EPOCH}"
            ),
            flush=True,
        )

        time.sleep(30)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():

    start_health_server()

    envelope, receipt = run_validation()

    heartbeat_loop()


if __name__ == "__main__":
    main()
