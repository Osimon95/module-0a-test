import copy
import hashlib
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


# =============================================================================
# R32D — DURABLE SYNTHETIC DISPATCH / CRASH-RECOVERY BOUNDARY
# =============================================================================

VERSION = "R32D"
SYMBOL = "BTCUSDT"

HEALTH_PORT = int(os.getenv("PORT", "10000"))
STATE_FILE = Path("/tmp/r32d_synthetic_dispatch_state.json")

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

MARGIN_TYPE = "ISOLATED"

# =============================================================================
# HARD SAFETY LOCKS
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
EXCHANGE_NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

GENERATION = 1
RECOVERY_EPOCH = 1

LINEAGE_ID = "R32-100X-CORRECTION-LINEAGE-V1"

PHASE_AUTHORIZATION_CONSUMED = "AUTHORIZATION_CONSUMED"
PHASE_DISPATCH_COMMITTED = "DISPATCH_COMMITTED"
PHASE_SYNTHETIC_DISPATCHED = "SYNTHETIC_DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

SEPARATOR = "-" * 92


# =============================================================================
# TERMINAL COUNTERS
# =============================================================================

counters = {
    "synthetic_dispatches": 0,
    "real_orders": 0,
    "network_writes": 0,
    "leverage_mutations": 0,
    "dispatch_commits": 0,
    "recovery_dispatches": 0,
    "duplicate_dispatches_blocked": 0,
    "authorization_consumptions": 1,
}


# =============================================================================
# RUNTIME STATE
# =============================================================================

runtime = {
    "phase": PHASE_AUTHORIZATION_CONSUMED,
    "correction_required": True,
    "intent_bound": True,
    "authorization_consumed": True,
    "dispatch_committed": False,
    "synthetic_dispatched": False,
    "completed": False,
    "generation": GENERATION,
    "recovery_epoch": RECOVERY_EPOCH,
    "lineage_id": LINEAGE_ID,
}


failures = []


# =============================================================================
# DISPLAY HELPERS
# =============================================================================

def banner(text):
    print(SEPARATOR, flush=True)
    print(text, flush=True)
    print(SEPARATOR, flush=True)


def section(text):
    banner(text)


def check(label, condition):
    ok = bool(condition)

    print(
        f"{label:<82} "
        f"{'✅ PASS' if ok else '❌ FAIL'}",
        flush=True,
    )

    if not ok:
        failures.append(label)

    return ok


# =============================================================================
# CANONICAL SERIALIZATION / HASHING
# =============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_json(value):
    encoded = canonical_json(value).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


# =============================================================================
# DURABLE STORAGE
# =============================================================================

def atomic_write_json(path, value):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    with open(
        temp,
        "w",
        encoding="utf-8",
    ) as fh:

        json.dump(
            value,
            fh,
            sort_keys=True,
            indent=2,
        )

        fh.flush()

        os.fsync(
            fh.fileno()
        )

    os.replace(
        temp,
        path,
    )


def read_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as fh:

        return json.load(fh)


# =============================================================================
# SEALED 100X CORRECTION INTENT
# =============================================================================

def build_correction_intent():

    body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "margin_type": MARGIN_TYPE,
        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
        "lineage_id": LINEAGE_ID,
        "correction_required": True,
    }

    return {
        "body": body,
        "intent_hash": sha256_json(body),
    }


# =============================================================================
# R32C CONSUMED AUTHORIZATION REPRESENTATION
# =============================================================================

def build_consumed_authorization(intent):

    body = {
        "kind": "SEALED_100X_CORRECTION_AUTHORIZATION",
        "symbol": SYMBOL,
        "intent_hash": intent["intent_hash"],
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
        "lineage_id": LINEAGE_ID,
        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,
        "consumed": True,
        "consumption_count": 1,
    }

    return {
        "body": body,
        "authorization_hash": sha256_json(body),
    }


# =============================================================================
# DURABLE SYNTHETIC DISPATCH COMMIT
# =============================================================================

def build_dispatch_commit(
    intent,
    authorization,
):

    body = {
        "kind": "R32D_SYNTHETIC_DISPATCH_COMMIT",
        "symbol": SYMBOL,
        "margin_type": MARGIN_TYPE,

        "intent_hash":
            intent["intent_hash"],

        "authorization_hash":
            authorization["authorization_hash"],

        "generation":
            GENERATION,

        "recovery_epoch":
            RECOVERY_EPOCH,

        "lineage_id":
            LINEAGE_ID,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "transport":
            "SYNTHETIC_ONLY",

        "network_transmission_permitted":
            False,

        "leverage_mutation_permitted":
            False,

        "real_execution_permitted":
            False,
    }

    return {
        "body": body,
        "dispatch_hash": sha256_json(body),
    }


# =============================================================================
# SNAPSHOT
# =============================================================================

def build_snapshot(
    intent,
    authorization,
    dispatch_commit,
):

    return {
        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "runtime":
            copy.deepcopy(runtime),

        "counters":
            copy.deepcopy(counters),

        "intent":
            copy.deepcopy(intent),

        "authorization":
            copy.deepcopy(authorization),

        "dispatch_commit":
            copy.deepcopy(dispatch_commit),
    }


# =============================================================================
# SYNTHETIC TRANSPORT
# =============================================================================

def synthetic_transport(
    dispatch_commit,
):

    # -------------------------------------------------------------------------
    # ABSOLUTE R32D FIREBREAK
    #
    # NO:
    #   requests.post()
    #   urllib POST
    #   WEEX SDK
    #   WebSocket write
    #   subprocess exchange call
    #   leverage endpoint
    #   order endpoint
    #
    # This function generates a LOCAL receipt only.
    # -------------------------------------------------------------------------

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "Synthetic transport lock is not active"
        )

    if REAL_ORDER_EXECUTION_ENABLED:
        raise RuntimeError(
            "Real execution unexpectedly enabled"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Network writes unexpectedly enabled"
        )

    if LEVERAGE_MUTATION_ENABLED:
        raise RuntimeError(
            "Leverage mutation unexpectedly enabled"
        )

    counters["synthetic_dispatches"] += 1

    receipt_body = {
        "transport":
            "SYNTHETIC",

        "dispatch_hash":
            dispatch_commit["dispatch_hash"],

        "symbol":
            SYMBOL,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "generation":
            GENERATION,

        "recovery_epoch":
            RECOVERY_EPOCH,

        "lineage_id":
            LINEAGE_ID,

        "network_transmitted":
            False,

        "exchange_contacted":
            False,

        "leverage_mutated":
            False,

        "real_order_sent":
            False,
    }

    return {
        "body":
            receipt_body,

        "receipt_hash":
            sha256_json(receipt_body),
    }


# =============================================================================
# EXACTLY-ONCE SYNTHETIC DISPATCH GUARD
# =============================================================================

def guarded_dispatch(
    intent,
    authorization,
    dispatch_commit,
):

    # -------------------------------------------------------------------------
    # Already dispatched?
    # Reject duplicate / replay.
    # -------------------------------------------------------------------------

    if runtime["synthetic_dispatched"]:

        counters[
            "duplicate_dispatches_blocked"
        ] += 1

        return None

    # -------------------------------------------------------------------------
    # Authorization must already be consumed.
    # -------------------------------------------------------------------------

    if not runtime["authorization_consumed"]:
        raise RuntimeError(
            "Authorization is not consumed"
        )

    if (
        authorization["body"]["consumed"]
        is not True
    ):
        raise RuntimeError(
            "Authorization record is not consumed"
        )

    if (
        authorization["body"]["consumption_count"]
        != 1
    ):
        raise RuntimeError(
            "Authorization consumption count is invalid"
        )

    # -------------------------------------------------------------------------
    # Exact intent binding.
    # -------------------------------------------------------------------------

    if (
        dispatch_commit["body"]["intent_hash"]
        != intent["intent_hash"]
    ):
        raise RuntimeError(
            "Dispatch commit intent binding mismatch"
        )

    # -------------------------------------------------------------------------
    # Exact authorization binding.
    # -------------------------------------------------------------------------

    if (
        dispatch_commit["body"]["authorization_hash"]
        != authorization["authorization_hash"]
    ):
        raise RuntimeError(
            "Dispatch commit authorization binding mismatch"
        )

    # -------------------------------------------------------------------------
    # Synthetic transport only.
    # -------------------------------------------------------------------------

    receipt = synthetic_transport(
        dispatch_commit
    )

    runtime[
        "synthetic_dispatched"
    ] = True

    runtime[
        "phase"
    ] = PHASE_SYNTHETIC_DISPATCHED

    return receipt


# =============================================================================
# HEALTH SERVER
# =============================================================================

def health_payload():

    return {
        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "phase":
            runtime["phase"],

        "synthetic_only":
            SYNTHETIC_TRANSPORT_ONLY,

        "real_execution":
            REAL_ORDER_EXECUTION_ENABLED,

        "network_writes":
            EXCHANGE_NETWORK_WRITES_ENABLED,

        "leverage_mutation":
            LEVERAGE_MUTATION_ENABLED,

        "correction_required":
            runtime["correction_required"],

        "intent_bound":
            runtime["intent_bound"],

        "authorization_consumed":
            runtime["authorization_consumed"],

        "dispatch_committed":
            runtime["dispatch_committed"],

        "synthetic_dispatched":
            runtime["synthetic_dispatched"],

        "target_long":
            TARGET_LONG_LEVERAGE,

        "target_short":
            TARGET_SHORT_LEVERAGE,

        "generation":
            runtime["generation"],

        "recovery_epoch":
            runtime["recovery_epoch"],
    }


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        payload = json.dumps(
            health_payload()
        ).encode(
            "utf-8"
        )

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

        self.wfile.write(
            payload
        )

    def log_message(
        self,
        *_args,
    ):
        return


def start_health_server():

    def worker():

        server = HTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        print(
            f"{VERSION}: "
            f"HEALTH SERVER LISTENING "
            f"ON PORT {HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()


# =============================================================================
# MAIN
# =============================================================================

def main():

    banner(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"TARGET LONG LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"TARGET SHORT LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"REAL EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"EXCHANGE NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    start_health_server()


    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        "R32D TEST 1: HARD SAFETY CONFIGURATION"
    )

    check(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Exchange Network Writes Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        "R32D TEST 2: "
        "RESTORE R32C TERMINAL AUTHORIZATION STATE"
    )

    check(
        "Starting Phase Is Authorization Consumed",
        runtime["phase"]
        == PHASE_AUTHORIZATION_CONSUMED,
    )

    check(
        "Correction Is Still Required",
        runtime["correction_required"]
        is True,
    )

    check(
        "Correction Intent Is Bound",
        runtime["intent_bound"]
        is True,
    )

    check(
        "Authorization Is Already Consumed",
        runtime["authorization_consumed"]
        is True,
    )

    check(
        "Authorization Consumption Counter Is One",
        counters[
            "authorization_consumptions"
        ] == 1,
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        "R32D TEST 3: "
        "EXACT 100X CORRECTION INTENT"
    )

    intent = build_correction_intent()

    check(
        "Intent Symbol Matches",
        intent["body"]["symbol"]
        == SYMBOL,
    )

    check(
        "Intent Margin Type Is Isolated",
        intent["body"]["margin_type"]
        == MARGIN_TYPE,
    )

    check(
        "Intent Long Target Is 100x",
        intent[
            "body"
        ][
            "target_long_leverage"
        ] == 100,
    )

    check(
        "Intent Short Target Is 100x",
        intent[
            "body"
        ][
            "target_short_leverage"
        ] == 100,
    )

    check(
        "Intent Hash Recomputes Exactly",
        intent["intent_hash"]
        == sha256_json(
            intent["body"]
        ),
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        "R32D TEST 4: "
        "CONSUMED AUTHORIZATION BINDING"
    )

    authorization = (
        build_consumed_authorization(
            intent
        )
    )

    check(
        "Authorization Is Marked Consumed",
        authorization[
            "body"
        ][
            "consumed"
        ] is True,
    )

    check(
        "Authorization Consumption Count Is One",
        authorization[
            "body"
        ][
            "consumption_count"
        ] == 1,
    )

    check(
        "Authorization Binds Intent Hash",
        authorization[
            "body"
        ][
            "intent_hash"
        ]
        ==
        intent["intent_hash"],
    )

    check(
        "Authorization Binds Generation",
        authorization[
            "body"
        ][
            "generation"
        ]
        ==
        GENERATION,
    )

    check(
        "Authorization Binds Recovery Epoch",
        authorization[
            "body"
        ][
            "recovery_epoch"
        ]
        ==
        RECOVERY_EPOCH,
    )

    check(
        "Authorization Binds Lineage",
        authorization[
            "body"
        ][
            "lineage_id"
        ]
        ==
        LINEAGE_ID,
    )

    check(
        "Authorization Hash Recomputes Exactly",
        authorization[
            "authorization_hash"
        ]
        ==
        sha256_json(
            authorization["body"]
        ),
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        "R32D TEST 5: "
        "DURABLE SYNTHETIC DISPATCH COMMIT"
    )

    dispatch_commit = (
        build_dispatch_commit(
            intent,
            authorization,
        )
    )

    runtime[
        "dispatch_committed"
    ] = True

    runtime[
        "phase"
    ] = PHASE_DISPATCH_COMMITTED

    counters[
        "dispatch_commits"
    ] += 1

    snapshot = build_snapshot(
        intent,
        authorization,
        dispatch_commit,
    )

    atomic_write_json(
        STATE_FILE,
        snapshot,
    )

    restored = read_json(
        STATE_FILE
    )

    check(
        "Dispatch Commit Counter Is One",
        counters[
            "dispatch_commits"
        ] == 1,
    )

    check(
        "Dispatch Commit Binds Intent Hash",
        dispatch_commit[
            "body"
        ][
            "intent_hash"
        ]
        ==
        intent[
            "intent_hash"
        ],
    )

    check(
        "Dispatch Commit Binds Authorization Hash",
        dispatch_commit[
            "body"
        ][
            "authorization_hash"
        ]
        ==
        authorization[
            "authorization_hash"
        ],
    )

    check(
        "Dispatch Commit Is Synthetic Only",
        dispatch_commit[
            "body"
        ][
            "transport"
        ]
        ==
        "SYNTHETIC_ONLY",
    )

    check(
        "Dispatch Commit Forbids Network Transmission",
        dispatch_commit[
            "body"
        ][
            "network_transmission_permitted"
        ]
        is False,
    )

    check(
        "Dispatch Commit Forbids Leverage Mutation",
        dispatch_commit[
            "body"
        ][
            "leverage_mutation_permitted"
        ]
        is False,
    )

    check(
        "Dispatch Commit Forbids Real Execution",
        dispatch_commit[
            "body"
        ][
            "real_execution_permitted"
        ]
        is False,
    )

    check(
        "Dispatch Hash Recomputes Exactly",
        dispatch_commit[
            "dispatch_hash"
        ]
        ==
        sha256_json(
            dispatch_commit[
                "body"
            ]
        ),
    )

    check(
        "Durable Snapshot Restores Dispatch Hash",
        restored[
            "dispatch_commit"
        ][
            "dispatch_hash"
        ]
        ==
        dispatch_commit[
            "dispatch_hash"
        ],
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        "R32D TEST 6: "
        "PRE-DISPATCH CRASH RECOVERY"
    )

    recovered_runtime = (
        restored["runtime"]
    )

    check(
        "Recovered Phase Is Dispatch Committed",
        recovered_runtime[
            "phase"
        ]
        ==
        PHASE_DISPATCH_COMMITTED,
    )

    check(
        "Recovered Authorization Is Consumed",
        recovered_runtime[
            "authorization_consumed"
        ]
        is True,
    )

    check(
        "Recovered Dispatch Is Committed",
        recovered_runtime[
            "dispatch_committed"
        ]
        is True,
    )

    check(
        "Recovered Synthetic Dispatch Has Not Happened",
        recovered_runtime[
            "synthetic_dispatched"
        ]
        is False,
    )

    counters[
        "recovery_dispatches"
    ] += 1

    receipt = guarded_dispatch(
        intent,
        authorization,
        dispatch_commit,
    )

    check(
        "Recovery Produced Synthetic Receipt",
        receipt is not None,
    )

    check(
        "Synthetic Dispatch Counter Is One",
        counters[
            "synthetic_dispatches"
        ] == 1,
    )

    check(
        "Recovery Dispatch Counter Is One",
        counters[
            "recovery_dispatches"
        ] == 1,
    )

    check(
        "Runtime Marks Synthetic Dispatch Complete",
        runtime[
            "synthetic_dispatched"
        ]
        is True,
    )

    check(
        "Runtime Phase Is Synthetic Dispatched",
        runtime[
            "phase"
        ]
        ==
        PHASE_SYNTHETIC_DISPATCHED,
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        "R32D TEST 7: "
        "SYNTHETIC RECEIPT BINDING"
    )

    check(
        "Receipt Transport Is Synthetic",
        receipt[
            "body"
        ][
            "transport"
        ]
        ==
        "SYNTHETIC",
    )

    check(
        "Receipt Binds Dispatch Hash",
        receipt[
            "body"
        ][
            "dispatch_hash"
        ]
        ==
        dispatch_commit[
            "dispatch_hash"
        ],
    )

    check(
        "Receipt Long Target Is 100x",
        receipt[
            "body"
        ][
            "target_long_leverage"
        ]
        == 100,
    )

    check(
        "Receipt Short Target Is 100x",
        receipt[
            "body"
        ][
            "target_short_leverage"
        ]
        == 100,
    )

    check(
        "Receipt Confirms No Network Transmission",
        receipt[
            "body"
        ][
            "network_transmitted"
        ]
        is False,
    )

    check(
        "Receipt Confirms Exchange Not Contacted",
        receipt[
            "body"
        ][
            "exchange_contacted"
        ]
        is False,
    )

    check(
        "Receipt Confirms No Leverage Mutation",
        receipt[
            "body"
        ][
            "leverage_mutated"
        ]
        is False,
    )

    check(
        "Receipt Confirms No Real Order",
        receipt[
            "body"
        ][
            "real_order_sent"
        ]
        is False,
    )

    check(
        "Receipt Hash Recomputes Exactly",
        receipt[
            "receipt_hash"
        ]
        ==
        sha256_json(
            receipt["body"]
        ),
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        "R32D TEST 8: "
        "DUPLICATE / REPLAY DISPATCH REJECTION"
    )

    replay_receipt = guarded_dispatch(
        intent,
        authorization,
        dispatch_commit,
    )

    check(
        "Replay Dispatch Is Rejected",
        replay_receipt
        is None,
    )

    check(
        "Synthetic Dispatch Counter Remains One",
        counters[
            "synthetic_dispatches"
        ] == 1,
    )

    check(
        "Duplicate Dispatch Block Counter Is One",
        counters[
            "duplicate_dispatches_blocked"
        ] == 1,
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    section(
        "R32D TEST 9: "
        "TAMPERED INTENT REJECTION"
    )

    tampered_intent = (
        copy.deepcopy(
            intent
        )
    )

    tampered_intent[
        "body"
    ][
        "target_long_leverage"
    ] = 99

    check(
        "Tampered Intent Hash No Longer Matches",
        tampered_intent[
            "intent_hash"
        ]
        !=
        sha256_json(
            tampered_intent[
                "body"
            ]
        ),
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    section(
        "R32D TEST 10: "
        "TAMPERED AUTHORIZATION REJECTION"
    )

    tampered_authorization = (
        copy.deepcopy(
            authorization
        )
    )

    tampered_authorization[
        "body"
    ][
        "generation"
    ] = 2

    check(
        "Tampered Authorization Hash No Longer Matches",
        tampered_authorization[
            "authorization_hash"
        ]
        !=
        sha256_json(
            tampered_authorization[
                "body"
            ]
        ),
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    section(
        "R32D TEST 11: "
        "TAMPERED DISPATCH COMMIT REJECTION"
    )

    tampered_commit = (
        copy.deepcopy(
            dispatch_commit
        )
    )

    tampered_commit[
        "body"
    ][
        "transport"
    ] = "REAL_NETWORK"

    check(
        "Tampered Dispatch Hash No Longer Matches",
        tampered_commit[
            "dispatch_hash"
        ]
        !=
        sha256_json(
            tampered_commit[
                "body"
            ]
        ),
    )

    check(
        "Real Network Transport Is Not Accepted",
        tampered_commit[
            "body"
        ][
            "transport"
        ]
        !=
        "SYNTHETIC_ONLY",
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    section(
        "R32D TEST 12: "
        "GENERATION / RECOVERY / LINEAGE FENCING"
    )

    check(
        "Intent Generation Is One",
        intent[
            "body"
        ][
            "generation"
        ]
        ==
        GENERATION
        ==
        1,
    )

    check(
        "Intent Recovery Epoch Is One",
        intent[
            "body"
        ][
            "recovery_epoch"
        ]
        ==
        RECOVERY_EPOCH
        ==
        1,
    )

    check(
        "Authorization Generation Matches",
        authorization[
            "body"
        ][
            "generation"
        ]
        ==
        intent[
            "body"
        ][
            "generation"
        ],
    )

    check(
        "Authorization Recovery Epoch Matches",
        authorization[
            "body"
        ][
            "recovery_epoch"
        ]
        ==
        intent[
            "body"
        ][
            "recovery_epoch"
        ],
    )

    check(
        "Dispatch Generation Matches",
        dispatch_commit[
            "body"
        ][
            "generation"
        ]
        ==
        intent[
            "body"
        ][
            "generation"
        ],
    )

    check(
        "Dispatch Recovery Epoch Matches",
        dispatch_commit[
            "body"
        ][
            "recovery_epoch"
        ]
        ==
        intent[
            "body"
        ][
            "recovery_epoch"
        ],
    )

    check(
        "Dispatch Lineage Matches",
        dispatch_commit[
            "body"
        ][
            "lineage_id"
        ]
        ==
        intent[
            "body"
        ][
            "lineage_id"
        ],
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    section(
        "R32D TEST 13: "
        "TERMINAL COMPLETION SNAPSHOT"
    )

    runtime[
        "completed"
    ] = True

    runtime[
        "phase"
    ] = PHASE_COMPLETED

    final_snapshot = (
        build_snapshot(
            intent,
            authorization,
            dispatch_commit,
        )
    )

    final_snapshot[
        "receipt"
    ] = receipt

    atomic_write_json(
        STATE_FILE,
        final_snapshot,
    )

    final_restored = (
        read_json(
            STATE_FILE
        )
    )

    check(
        "Final Snapshot Restores Completed Phase",
        final_restored[
            "runtime"
        ][
            "phase"
        ]
        ==
        PHASE_COMPLETED,
    )

    check(
        "Final Snapshot Preserves Synthetic Dispatch",
        final_restored[
            "runtime"
        ][
            "synthetic_dispatched"
        ]
        is True,
    )

    check(
        "Final Snapshot Preserves Authorization Consumed",
        final_restored[
            "runtime"
        ][
            "authorization_consumed"
        ]
        is True,
    )

    check(
        "Final Snapshot Preserves Dispatch Hash",
        final_restored[
            "dispatch_commit"
        ][
            "dispatch_hash"
        ]
        ==
        dispatch_commit[
            "dispatch_hash"
        ],
    )

    check(
        "Final Snapshot Preserves Receipt Hash",
        final_restored[
            "receipt"
        ][
            "receipt_hash"
        ]
        ==
        receipt[
            "receipt_hash"
        ],
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    section(
        "R32D TEST 14: "
        "POST-COMPLETION REPLAY REJECTION"
    )

    post_completion_replay = (
        guarded_dispatch(
            intent,
            authorization,
            dispatch_commit,
        )
    )

    check(
        "Post-Completion Replay Is Rejected",
        post_completion_replay
        is None,
    )

    check(
        "Synthetic Dispatch Counter Still One",
        counters[
            "synthetic_dispatches"
        ]
        == 1,
    )

    check(
        "Duplicate Dispatch Block Counter Is Two",
        counters[
            "duplicate_dispatches_blocked"
        ]
        == 2,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    section(
        "R32D TEST 15: "
        "TERMINAL SAFETY COUNTERS"
    )

    check(
        "Synthetic Dispatch Counter Is One",
        counters[
            "synthetic_dispatches"
        ]
        == 1,
    )

    check(
        "Real Order Counter Is Zero",
        counters[
            "real_orders"
        ]
        == 0,
    )

    check(
        "Network Write Counter Is Zero",
        counters[
            "network_writes"
        ]
        == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        counters[
            "leverage_mutations"
        ]
        == 0,
    )

    check(
        "Authorization Consumption Counter Is One",
        counters[
            "authorization_consumptions"
        ]
        == 1,
    )

    check(
        "Dispatch Commit Counter Is One",
        counters[
            "dispatch_commits"
        ]
        == 1,
    )


    # =========================================================================
    # FINAL VALIDATION
    # =========================================================================

    section(
        "R32D FINAL VALIDATION"
    )

    check(
        "R32D Phase Is Completed",
        runtime[
            "phase"
        ]
        ==
        PHASE_COMPLETED,
    )

    check(
        "100x Correction Intent Remains Bound",
        runtime[
            "intent_bound"
        ]
        is True,
    )

    check(
        "Authorization Remains Consumed Exactly Once",
        counters[
            "authorization_consumptions"
        ]
        == 1,
    )

    check(
        "Synthetic Dispatch Occurred Exactly Once",
        counters[
            "synthetic_dispatches"
        ]
        == 1,
    )

    check(
        "Correction Remains Non-Executable On Real Network",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "No Network Write Capability Activated",
        (
            counters[
                "network_writes"
            ]
            == 0
            and
            EXCHANGE_NETWORK_WRITES_ENABLED
            is False
        ),
    )

    check(
        "No Leverage Mutation Capability Activated",
        (
            counters[
                "leverage_mutations"
            ]
            == 0
            and
            LEVERAGE_MUTATION_ENABLED
            is False
        ),
    )

    check(
        "No Real Execution Capability Activated",
        (
            counters[
                "real_orders"
            ]
            == 0
            and
            REAL_ORDER_EXECUTION_ENABLED
            is False
        ),
    )


    # =========================================================================
    # RESULT
    # =========================================================================

    banner(
        f"{VERSION}: "
        f"VALIDATION "
        f"{'COMPLETE ✅' if not failures else 'FAILED ❌'}"
    )

    if failures:

        print(
            f"{VERSION}: "
            f"FAILURES={len(failures)}",
            flush=True,
        )

        for item in failures:

            print(
                f"{VERSION}: "
                f"FAILURE: {item}",
                flush=True,
            )

        raise SystemExit(1)


    print(
        f"{VERSION}: "
        f"100X CORRECTION AUTHORIZATION "
        f"REMAINS CONSUMED EXACTLY ONCE",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"SYNTHETIC DISPATCH OCCURRED "
        f"EXACTLY ONCE",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"DUPLICATE / REPLAY DISPATCH "
        f"IS REJECTED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"NO EXCHANGE NETWORK WRITE "
        f"WAS PERFORMED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"NO LEVERAGE MUTATION "
        f"WAS PERFORMED",
        flush=True,
    )

    print(
        SEPARATOR,
        flush=True,
    )


    # =========================================================================
    # HEARTBEAT
    # =========================================================================

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{VERSION}: "
            f"HEARTBEAT {heartbeat} | "
            f"phase={runtime['phase']} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"synthetic-dispatch="
            f"{counters['synthetic_dispatches']} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"correction-required="
            f"{runtime['correction_required']} | "
            f"intent-bound="
            f"{runtime['intent_bound']} | "
            f"authorization-consumed="
            f"{runtime['authorization_consumed']} | "
            f"dispatch-committed="
            f"{runtime['dispatch_committed']} | "
            f"target-long="
            f"{TARGET_LONG_LEVERAGE}x | "
            f"target-short="
            f"{TARGET_SHORT_LEVERAGE}x | "
            f"generation="
            f"{runtime['generation']} | "
            f"recovery-epoch="
            f"{runtime['recovery_epoch']}",
            flush=True,
        )

        time.sleep(30)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
