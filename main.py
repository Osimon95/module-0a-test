

# ==================================================================================================
# R35Z MAIN.PY
# PURPOSE:
#   CROSS-RESTART REPLAY REJECTION OF THE EXACT R35Y TELEGRAM UPDATE
#
# PROOF TARGET:
#   1. Load the exact durable files created by R35Y.
#   2. Confirm R35Y_SYNTHETIC_UPDATE_000001 already exists before processing.
#   3. Replay that exact update through the PRE-PARSE durable duplicate gate.
#   4. Reject it BEFORE parsing.
#   5. Parse count must remain 0.
#   6. Validation count must remain 0.
#   7. Synthetic decision creation count must remain 0.
#   8. Durable update commits must remain 0.
#   9. Durable decision commits must remain 0.
#  10. R35Y durable files must remain byte-for-byte unchanged.
#  11. Existing R35Y decision hash must remain present and unchanged.
#  12. Absolutely no exchange mutation or order submission is permitted.
#
# IMPORTANT:
#   THIS FILE DOES NOT SEND REAL OR DEMO ORDERS.
#   THIS FILE DOES NOT MUTATE WEEX.
#   THIS FILE DOES NOT MUTATE THE R35Y DURABLE REGISTRIES.
# ==================================================================================================

import os
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# R35Z CONSTANTS
# ==================================================================================================

UNIT = "R35Z"

PORT = int(os.environ.get("PORT", "10000"))

SEPARATOR = "-" * 100

PERSISTENT_DISK_ROOT = "/var/data"

# Deliberately reuse R35Y state.
R35Y_STATE_DIR = os.path.join(
    PERSISTENT_DISK_ROOT,
    "r35y_state",
)

R35Y_DEDUPE_FILE = os.path.join(
    R35Y_STATE_DIR,
    "telegram_processed_updates.json",
)

R35Y_DECISION_FILE = os.path.join(
    R35Y_STATE_DIR,
    "synthetic_decisions.json",
)

TEST_TELEGRAM_UPDATE_ID = "R35Y_SYNTHETIC_UPDATE_000001"

EXPECTED_R35Y_DECISION_HASH = (
    "0eeb44e27e1a85a4f6c3ef89c1f012cb"
    "f26641012199ce7d64c7bb8796bc1071"
)

R35U_REFERENCE_DECISION_HASH = (
    "ada67682fedff8bbac0608cc96805dc42"
    "ea20bab56f3305c8afa06d7ef89cc94"
)

HASH_SERIALIZER = "SORTED_COMPACT_UTF8"


# ==================================================================================================
# ABSOLUTE SAFETY FIREBREAK
# ==================================================================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0


# ==================================================================================================
# TEST COUNTERS
# ==================================================================================================

TELEGRAM_PROCESSING_ATTEMPTS = 0

DUPLICATE_GATE_ENTERED = False
DUPLICATE_DETECTED = False

NEW_UPDATE_ACCEPTED = False
PIPELINE_CONTINUE_RESULT = False

SIGNAL_PARSE_COUNT = 0
SIGNAL_VALIDATION_COUNT = 0
SYNTHETIC_DECISION_CREATION_COUNT = 0

DURABLE_UPDATE_COMMITS = 0
DURABLE_DECISION_COMMITS = 0
DURABLE_REGISTRY_MUTATIONS = 0


# ==================================================================================================
# TEST STATE
# ==================================================================================================

UPDATE_PRESENT_BEFORE_PROCESSING = False
UPDATE_PRESENT_AFTER_PROCESSING = False

EXPECTED_DECISION_HASH_PRESENT_BEFORE = False
EXPECTED_DECISION_HASH_PRESENT_AFTER = False

DEDUPE_FILE_SHA256_BEFORE = None
DEDUPE_FILE_SHA256_AFTER = None

DECISION_FILE_SHA256_BEFORE = None
DECISION_FILE_SHA256_AFTER = None

DEDUPE_FILE_UNCHANGED = False
DECISION_FILE_UNCHANGED = False

R35Y_STATE_DIRECTORY_AVAILABLE = False
R35Y_DEDUPE_FILE_AVAILABLE = False
R35Y_DECISION_FILE_AVAILABLE = False

R35Y_REFERENCE_INTEGRITY_OK = False
PRE_PARSE_REPLAY_REJECTION_OK = False
ZERO_MUTATION_REPLAY_OK = False
ZERO_WRITE_FIREBREAK_OK = False

TEST_STATUS = "NOT_RUN"
FAILURES = []


# ==================================================================================================
# TIME / LOG HELPERS
# ==================================================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def section(title):
    log(SEPARATOR)
    log(title)
    log(SEPARATOR)


def pass_fail(condition):
    return "✅ PASS" if condition else "❌ FAIL"


def result(label, condition):
    print(
        f"{label:<84} {pass_fail(condition)}",
        flush=True,
    )


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            f"{UNIT} OK\n"
            f"TEST_STATUS={TEST_STATUS}\n"
            f"DUPLICATE_DETECTED={DUPLICATE_DETECTED}\n"
            f"SIGNAL_PARSE_COUNT={SIGNAL_PARSE_COUNT}\n"
            f"SYNTHETIC_DECISION_CREATION_COUNT="
            f"{SYNTHETIC_DECISION_CREATION_COUNT}\n"
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
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
        ("0.0.0.0", PORT),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(
        f"{UNIT}: HEALTH SERVER STARTED ON PORT {PORT}"
    )


# ==================================================================================================
# FILE HELPERS
# ==================================================================================================

def file_sha256(path):
    hasher = hashlib.sha256()

    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


def load_json_read_only(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


# ==================================================================================================
# GENERIC DURABLE REGISTRY SEARCH
#
# R35Z deliberately does not assume only one JSON container layout.
#
# This permits verification whether R35Y represented its registry as:
#   - a list,
#   - a dict keyed by update ID,
#   - nested records,
#   - records containing update_id fields,
# without rewriting or normalizing the durable artifact.
# ==================================================================================================

def recursive_contains_exact_value(obj, target):
    if isinstance(obj, dict):

        for key, value in obj.items():

            if str(key) == str(target):
                return True

            if (
                not isinstance(value, (dict, list))
                and str(value) == str(target)
            ):
                return True

            if recursive_contains_exact_value(
                value,
                target,
            ):
                return True

        return False

    if isinstance(obj, list):

        for item in obj:
            if recursive_contains_exact_value(
                item,
                target,
            ):
                return True

        return False

    try:
        return str(obj) == str(target)
    except Exception:
        return False


# ==================================================================================================
# PRE-PARSE DURABLE DUPLICATE GATE
#
# THIS IS THE CENTRAL R35Z TEST.
#
# No parser call is permitted until this gate returns True.
#
# For the exact R35Y replay, the expected result is False.
# ==================================================================================================

def pre_parse_durable_duplicate_gate(
    telegram_update_id,
    durable_dedupe_registry,
):
    global DUPLICATE_GATE_ENTERED
    global DUPLICATE_DETECTED
    global NEW_UPDATE_ACCEPTED

    DUPLICATE_GATE_ENTERED = True

    already_processed = recursive_contains_exact_value(
        durable_dedupe_registry,
        telegram_update_id,
    )

    if already_processed:

        DUPLICATE_DETECTED = True
        NEW_UPDATE_ACCEPTED = False

        log(
            f"{UNIT}: PRE-PARSE DUPLICATE GATE "
            f"REJECTED UPDATE_ID={telegram_update_id}"
        )

        return False

    DUPLICATE_DETECTED = False
    NEW_UPDATE_ACCEPTED = True

    log(
        f"{UNIT}: PRE-PARSE DUPLICATE GATE "
        f"WOULD ACCEPT UPDATE_ID={telegram_update_id}"
    )

    return True


# ==================================================================================================
# DOWNSTREAM PIPELINE SENTINELS
#
# These functions must NOT execute in the successful R35Z test.
# ==================================================================================================

def parse_signal(_telegram_update):
    global SIGNAL_PARSE_COUNT

    SIGNAL_PARSE_COUNT += 1

    raise RuntimeError(
        "R35Z FAILURE: duplicate replay reached SIGNAL PARSER"
    )


def validate_signal(_parsed_signal):
    global SIGNAL_VALIDATION_COUNT

    SIGNAL_VALIDATION_COUNT += 1

    raise RuntimeError(
        "R35Z FAILURE: duplicate replay reached SIGNAL VALIDATOR"
    )


def create_synthetic_decision(_validated_signal):
    global SYNTHETIC_DECISION_CREATION_COUNT

    SYNTHETIC_DECISION_CREATION_COUNT += 1

    raise RuntimeError(
        "R35Z FAILURE: duplicate replay reached "
        "SYNTHETIC DECISION CREATION"
    )


# ==================================================================================================
# SAFETY ASSERTION
# ==================================================================================================

def exchange_write_firebreak():
    raise RuntimeError(
        "R35Z HARD FIREBREAK: "
        "EXCHANGE WRITE TRANSPORT IS DISABLED"
    )


# ==================================================================================================
# TEST EXECUTION
# ==================================================================================================

def run_r35z_tests():

    global TELEGRAM_PROCESSING_ATTEMPTS

    global UPDATE_PRESENT_BEFORE_PROCESSING
    global UPDATE_PRESENT_AFTER_PROCESSING

    global EXPECTED_DECISION_HASH_PRESENT_BEFORE
    global EXPECTED_DECISION_HASH_PRESENT_AFTER

    global DEDUPE_FILE_SHA256_BEFORE
    global DEDUPE_FILE_SHA256_AFTER

    global DECISION_FILE_SHA256_BEFORE
    global DECISION_FILE_SHA256_AFTER

    global DEDUPE_FILE_UNCHANGED
    global DECISION_FILE_UNCHANGED

    global R35Y_STATE_DIRECTORY_AVAILABLE
    global R35Y_DEDUPE_FILE_AVAILABLE
    global R35Y_DECISION_FILE_AVAILABLE

    global R35Y_REFERENCE_INTEGRITY_OK
    global PRE_PARSE_REPLAY_REJECTION_OK
    global ZERO_MUTATION_REPLAY_OK
    global ZERO_WRITE_FIREBREAK_OK

    global PIPELINE_CONTINUE_RESULT

    global TEST_STATUS
    global FAILURES

    section(
        f"{UNIT}: MAIN.PY ENTERED"
    )

    log(
        "PURPOSE=CROSS-RESTART REPLAY REJECTION OF "
        "THE EXACT R35Y TELEGRAM UPDATE BEFORE PARSING"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"EXPECTED_R35Y_DECISION_HASH="
        f"{EXPECTED_R35Y_DECISION_HASH}"
    )

    log(
        f"HASH_SERIALIZER={HASH_SERIALIZER}"
    )

    log(
        f"R35Y_STATE_DIR={R35Y_STATE_DIR}"
    )

    log(
        f"R35Y_DEDUPE_FILE={R35Y_DEDUPE_FILE}"
    )

    log(
        f"R35Y_DECISION_FILE={R35Y_DECISION_FILE}"
    )


    # ==============================================================================================
    # TEST 1: HARD SAFETY CONFIGURATION
    # ==============================================================================================

    section(
        f"{UNIT} TEST 1: HARD SAFETY CONFIGURATION"
    )

    result(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    result(
        "First Real Order Allowed = False",
        FIRST_REAL_ORDER_ALLOWED is False,
    )

    result(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    result(
        "Exchange Mutation Transport Disabled",
        EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
    )

    result(
        "Order Submission Disabled",
        ORDER_SUBMISSION_ENABLED is False,
    )

    result(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    result(
        "Margin Mode Mutation Disabled",
        MARGIN_MODE_MUTATION_ENABLED is False,
    )

    result(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED is False,
    )


    # ==============================================================================================
    # TEST 2: R35Y DURABLE ARTIFACT AVAILABILITY
    # ==============================================================================================

    section(
        f"{UNIT} TEST 2: R35Y DURABLE ARTIFACT AVAILABILITY"
    )

    R35Y_STATE_DIRECTORY_AVAILABLE = os.path.isdir(
        R35Y_STATE_DIR
    )

    R35Y_DEDUPE_FILE_AVAILABLE = os.path.isfile(
        R35Y_DEDUPE_FILE
    )

    R35Y_DECISION_FILE_AVAILABLE = os.path.isfile(
        R35Y_DECISION_FILE
    )

    result(
        "R35Y State Directory Available",
        R35Y_STATE_DIRECTORY_AVAILABLE,
    )

    result(
        "R35Y Durable Dedupe Registry Available",
        R35Y_DEDUPE_FILE_AVAILABLE,
    )

    result(
        "R35Y Durable Decision Registry Available",
        R35Y_DECISION_FILE_AVAILABLE,
    )

    if not R35Y_STATE_DIRECTORY_AVAILABLE:
        FAILURES.append(
            "R35Y_STATE_DIRECTORY_MISSING"
        )

    if not R35Y_DEDUPE_FILE_AVAILABLE:
        FAILURES.append(
            "R35Y_DEDUPE_FILE_MISSING"
        )

    if not R35Y_DECISION_FILE_AVAILABLE:
        FAILURES.append(
            "R35Y_DECISION_FILE_MISSING"
        )

    if FAILURES:
        raise RuntimeError(
            ",".join(FAILURES)
        )


    # ==============================================================================================
    # TEST 3: LOAD R35Y DURABLE REGISTRIES READ-ONLY
    # ==============================================================================================

    section(
        f"{UNIT} TEST 3: LOAD R35Y DURABLE REGISTRIES READ-ONLY"
    )

    r35y_dedupe_registry = load_json_read_only(
        R35Y_DEDUPE_FILE
    )

    r35y_decision_registry = load_json_read_only(
        R35Y_DECISION_FILE
    )

    result(
        "R35Y Durable Dedupe Registry Loaded",
        r35y_dedupe_registry is not None,
    )

    result(
        "R35Y Durable Decision Registry Loaded",
        r35y_decision_registry is not None,
    )


    # ==============================================================================================
    # TEST 4: EXACT PRE-REPLAY R35Y ARTIFACT HASHES
    # ==============================================================================================

    section(
        f"{UNIT} TEST 4: PRE-REPLAY DURABLE FILE HASHES"
    )

    DEDUPE_FILE_SHA256_BEFORE = file_sha256(
        R35Y_DEDUPE_FILE
    )

    DECISION_FILE_SHA256_BEFORE = file_sha256(
        R35Y_DECISION_FILE
    )

    log(
        f"DEDUPE_FILE_SHA256_BEFORE="
        f"{DEDUPE_FILE_SHA256_BEFORE}"
    )

    log(
        f"DECISION_FILE_SHA256_BEFORE="
        f"{DECISION_FILE_SHA256_BEFORE}"
    )

    result(
        "Dedupe File SHA256 Captured",
        bool(DEDUPE_FILE_SHA256_BEFORE),
    )

    result(
        "Decision File SHA256 Captured",
        bool(DECISION_FILE_SHA256_BEFORE),
    )


    # ==============================================================================================
    # TEST 5: R35Y UPDATE MUST ALREADY EXIST BEFORE REPLAY
    # ==============================================================================================

    section(
        f"{UNIT} TEST 5: R35Y UPDATE MUST EXIST BEFORE REPLAY"
    )

    UPDATE_PRESENT_BEFORE_PROCESSING = (
        recursive_contains_exact_value(
            r35y_dedupe_registry,
            TEST_TELEGRAM_UPDATE_ID,
        )
    )

    log(
        f"UPDATE_PRESENT_BEFORE_PROCESSING="
        f"{UPDATE_PRESENT_BEFORE_PROCESSING}"
    )

    result(
        "Exact R35Y Update Present Before Replay",
        UPDATE_PRESENT_BEFORE_PROCESSING,
    )

    if not UPDATE_PRESENT_BEFORE_PROCESSING:
        FAILURES.append(
            "R35Y_UPDATE_NOT_DURABLE_BEFORE_REPLAY"
        )


    # ==============================================================================================
    # TEST 6: EXACT R35Y DECISION HASH MUST ALREADY EXIST
    # ==============================================================================================

    section(
        f"{UNIT} TEST 6: EXACT R35Y DECISION HASH INTEGRITY"
    )

    EXPECTED_DECISION_HASH_PRESENT_BEFORE = (
        recursive_contains_exact_value(
            r35y_decision_registry,
            EXPECTED_R35Y_DECISION_HASH,
        )
    )

    log(
        f"EXPECTED_DECISION_HASH_PRESENT_BEFORE="
        f"{EXPECTED_DECISION_HASH_PRESENT_BEFORE}"
    )

    result(
        "Exact R35Y Decision Hash Present Before Replay",
        EXPECTED_DECISION_HASH_PRESENT_BEFORE,
    )

    R35Y_REFERENCE_INTEGRITY_OK = (
        UPDATE_PRESENT_BEFORE_PROCESSING
        and EXPECTED_DECISION_HASH_PRESENT_BEFORE
    )

    result(
        "R35Y Reference Integrity",
        R35Y_REFERENCE_INTEGRITY_OK,
    )

    if not R35Y_REFERENCE_INTEGRITY_OK:
        FAILURES.append(
            "R35Y_REFERENCE_INTEGRITY_FAILED"
        )


    # ==============================================================================================
    # TEST 7: REPLAY THE EXACT R35Y TELEGRAM UPDATE
    # ==============================================================================================

    section(
        f"{UNIT} TEST 7: EXACT R35Y UPDATE REPLAY"
    )

    synthetic_replay_update = {
        "update_id": TEST_TELEGRAM_UPDATE_ID,
        "source": "R35Z_CROSS_RESTART_REPLAY_TEST",
    }

    TELEGRAM_PROCESSING_ATTEMPTS += 1

    PIPELINE_CONTINUE_RESULT = (
        pre_parse_durable_duplicate_gate(
            TEST_TELEGRAM_UPDATE_ID,
            r35y_dedupe_registry,
        )
    )

    log(
        f"TELEGRAM_PROCESSING_ATTEMPTS="
        f"{TELEGRAM_PROCESSING_ATTEMPTS}"
    )

    log(
        f"DUPLICATE_GATE_ENTERED="
        f"{DUPLICATE_GATE_ENTERED}"
    )

    log(
        f"DUPLICATE_DETECTED="
        f"{DUPLICATE_DETECTED}"
    )

    log(
        f"NEW_UPDATE_ACCEPTED="
        f"{NEW_UPDATE_ACCEPTED}"
    )

    log(
        f"PIPELINE_CONTINUE_RESULT="
        f"{PIPELINE_CONTINUE_RESULT}"
    )

    # If this executes, R35Z must fail.
    if PIPELINE_CONTINUE_RESULT:

        parsed = parse_signal(
            synthetic_replay_update
        )

        validated = validate_signal(
            parsed
        )

        create_synthetic_decision(
            validated
        )


    # ==============================================================================================
    # TEST 8: DUPLICATE MUST HAVE BEEN REJECTED BEFORE PARSE
    # ==============================================================================================

    section(
        f"{UNIT} TEST 8: PRE-PARSE REPLAY REJECTION"
    )

    result(
        "Duplicate Gate Entered",
        DUPLICATE_GATE_ENTERED is True,
    )

    result(
        "Duplicate Detected",
        DUPLICATE_DETECTED is True,
    )

    result(
        "New Update Accepted = False",
        NEW_UPDATE_ACCEPTED is False,
    )

    result(
        "Pipeline Continue Result = False",
        PIPELINE_CONTINUE_RESULT is False,
    )

    result(
        "Telegram Processing Attempts = 1",
        TELEGRAM_PROCESSING_ATTEMPTS == 1,
    )

    result(
        "Signal Parse Count = 0",
        SIGNAL_PARSE_COUNT == 0,
    )

    result(
        "Signal Validation Count = 0",
        SIGNAL_VALIDATION_COUNT == 0,
    )

    result(
        "Synthetic Decision Creation Count = 0",
        SYNTHETIC_DECISION_CREATION_COUNT == 0,
    )

    PRE_PARSE_REPLAY_REJECTION_OK = all(
        [
            DUPLICATE_GATE_ENTERED is True,
            DUPLICATE_DETECTED is True,
            NEW_UPDATE_ACCEPTED is False,
            PIPELINE_CONTINUE_RESULT is False,
            TELEGRAM_PROCESSING_ATTEMPTS == 1,
            SIGNAL_PARSE_COUNT == 0,
            SIGNAL_VALIDATION_COUNT == 0,
            SYNTHETIC_DECISION_CREATION_COUNT == 0,
        ]
    )

    result(
        "Pre-Parse Replay Rejection",
        PRE_PARSE_REPLAY_REJECTION_OK,
    )

    if not PRE_PARSE_REPLAY_REJECTION_OK:
        FAILURES.append(
            "PRE_PARSE_REPLAY_REJECTION_FAILED"
        )


    # ==============================================================================================
    # TEST 9: ZERO DURABLE MUTATIONS DURING REPLAY
    # ==============================================================================================

    section(
        f"{UNIT} TEST 9: ZERO DURABLE REGISTRY MUTATIONS"
    )

    result(
        "Durable Update Commits = 0",
        DURABLE_UPDATE_COMMITS == 0,
    )

    result(
        "Durable Decision Commits = 0",
        DURABLE_DECISION_COMMITS == 0,
    )

    result(
        "Durable Registry Mutations = 0",
        DURABLE_REGISTRY_MUTATIONS == 0,
    )

    ZERO_MUTATION_REPLAY_OK = all(
        [
            DURABLE_UPDATE_COMMITS == 0,
            DURABLE_DECISION_COMMITS == 0,
            DURABLE_REGISTRY_MUTATIONS == 0,
        ]
    )

    result(
        "Zero Durable Mutation Replay",
        ZERO_MUTATION_REPLAY_OK,
    )

    if not ZERO_MUTATION_REPLAY_OK:
        FAILURES.append(
            "DURABLE_REGISTRY_MUTATED_DURING_REPLAY"
        )


    # ==============================================================================================
    # TEST 10: RELOAD DURABLE FILES AFTER REPLAY
    # ==============================================================================================

    section(
        f"{UNIT} TEST 10: POST-REPLAY DURABLE INTEGRITY"
    )

    r35y_dedupe_registry_after = load_json_read_only(
        R35Y_DEDUPE_FILE
    )

    r35y_decision_registry_after = load_json_read_only(
        R35Y_DECISION_FILE
    )

    UPDATE_PRESENT_AFTER_PROCESSING = (
        recursive_contains_exact_value(
            r35y_dedupe_registry_after,
            TEST_TELEGRAM_UPDATE_ID,
        )
    )

    EXPECTED_DECISION_HASH_PRESENT_AFTER = (
        recursive_contains_exact_value(
            r35y_decision_registry_after,
            EXPECTED_R35Y_DECISION_HASH,
        )
    )

    DEDUPE_FILE_SHA256_AFTER = file_sha256(
        R35Y_DEDUPE_FILE
    )

    DECISION_FILE_SHA256_AFTER = file_sha256(
        R35Y_DECISION_FILE
    )

    DEDUPE_FILE_UNCHANGED = (
        DEDUPE_FILE_SHA256_AFTER
        == DEDUPE_FILE_SHA256_BEFORE
    )

    DECISION_FILE_UNCHANGED = (
        DECISION_FILE_SHA256_AFTER
        == DECISION_FILE_SHA256_BEFORE
    )

    log(
        f"UPDATE_PRESENT_AFTER_PROCESSING="
        f"{UPDATE_PRESENT_AFTER_PROCESSING}"
    )

    log(
        f"EXPECTED_DECISION_HASH_PRESENT_AFTER="
        f"{EXPECTED_DECISION_HASH_PRESENT_AFTER}"
    )

    log(
        f"DEDUPE_FILE_SHA256_AFTER="
        f"{DEDUPE_FILE_SHA256_AFTER}"
    )

    log(
        f"DECISION_FILE_SHA256_AFTER="
        f"{DECISION_FILE_SHA256_AFTER}"
    )

    log(
        f"DEDUPE_FILE_UNCHANGED="
        f"{DEDUPE_FILE_UNCHANGED}"
    )

    log(
        f"DECISION_FILE_UNCHANGED="
        f"{DECISION_FILE_UNCHANGED}"
    )

    result(
        "Exact R35Y Update Still Present",
        UPDATE_PRESENT_AFTER_PROCESSING,
    )

    result(
        "Exact R35Y Decision Hash Still Present",
        EXPECTED_DECISION_HASH_PRESENT_AFTER,
    )

    result(
        "Dedupe File Byte-for-Byte Unchanged",
        DEDUPE_FILE_UNCHANGED,
    )

    result(
        "Decision File Byte-for-Byte Unchanged",
        DECISION_FILE_UNCHANGED,
    )

    if not UPDATE_PRESENT_AFTER_PROCESSING:
        FAILURES.append(
            "R35Y_UPDATE_DISAPPEARED_AFTER_REPLAY"
        )

    if not EXPECTED_DECISION_HASH_PRESENT_AFTER:
        FAILURES.append(
            "R35Y_DECISION_HASH_DISAPPEARED_AFTER_REPLAY"
        )

    if not DEDUPE_FILE_UNCHANGED:
        FAILURES.append(
            "DEDUPE_FILE_CHANGED_DURING_REPLAY"
        )

    if not DECISION_FILE_UNCHANGED:
        FAILURES.append(
            "DECISION_FILE_CHANGED_DURING_REPLAY"
        )


    # ==============================================================================================
    # TEST 11: ABSOLUTE EXCHANGE WRITE FIREBREAK
    # ==============================================================================================

    section(
        f"{UNIT} TEST 11: ABSOLUTE EXCHANGE WRITE FIREBREAK"
    )

    result(
        "Exchange Network Writes = 0",
        EXCHANGE_NETWORK_WRITES == 0,
    )

    result(
        "Order Submissions = 0",
        ORDER_SUBMISSIONS == 0,
    )

    result(
        "Leverage Mutations = 0",
        LEVERAGE_MUTATIONS == 0,
    )

    result(
        "Margin Mode Mutations = 0",
        MARGIN_MODE_MUTATIONS == 0,
    )

    result(
        "Position Mutations = 0",
        POSITION_MUTATIONS == 0,
    )

    result(
        "Real Orders Sent = 0",
        REAL_ORDERS_SENT == 0,
    )

    result(
        "Demo Orders Sent = 0",
        DEMO_ORDERS_SENT == 0,
    )

    ZERO_WRITE_FIREBREAK_OK = all(
        [
            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,
            REAL_ORDERS_SENT == 0,
            DEMO_ORDERS_SENT == 0,
            REAL_ORDER_EXECUTION is False,
            FIRST_REAL_ORDER_ALLOWED is False,
            DEMO_ORDER_EXECUTION is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
            ORDER_SUBMISSION_ENABLED is False,
        ]
    )

    result(
        "Zero Write Firebreak",
        ZERO_WRITE_FIREBREAK_OK,
    )

    if not ZERO_WRITE_FIREBREAK_OK:
        FAILURES.append(
            "ZERO_WRITE_FIREBREAK_FAILED"
        )


    # ==============================================================================================
    # FINAL STATUS
    # ==============================================================================================

    required_conditions = [
        R35Y_STATE_DIRECTORY_AVAILABLE,
        R35Y_DEDUPE_FILE_AVAILABLE,
        R35Y_DECISION_FILE_AVAILABLE,
        R35Y_REFERENCE_INTEGRITY_OK,
        UPDATE_PRESENT_BEFORE_PROCESSING,
        DUPLICATE_GATE_ENTERED,
        DUPLICATE_DETECTED,
        NEW_UPDATE_ACCEPTED is False,
        PIPELINE_CONTINUE_RESULT is False,
        SIGNAL_PARSE_COUNT == 0,
        SIGNAL_VALIDATION_COUNT == 0,
        SYNTHETIC_DECISION_CREATION_COUNT == 0,
        DURABLE_UPDATE_COMMITS == 0,
        DURABLE_DECISION_COMMITS == 0,
        DURABLE_REGISTRY_MUTATIONS == 0,
        UPDATE_PRESENT_AFTER_PROCESSING,
        EXPECTED_DECISION_HASH_PRESENT_AFTER,
        DEDUPE_FILE_UNCHANGED,
        DECISION_FILE_UNCHANGED,
        ZERO_WRITE_FIREBREAK_OK,
    ]

    if all(required_conditions) and not FAILURES:
        TEST_STATUS = "PASS"
    else:
        TEST_STATUS = "FAIL"

    section(
        f"{UNIT}: FINAL TEST SUMMARY"
    )

    log(
        "PURPOSE=CROSS-RESTART EXACT R35Y TELEGRAM "
        "UPDATE REPLAY REJECTION BEFORE PARSE"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"EXPECTED_R35Y_DECISION_HASH="
        f"{EXPECTED_R35Y_DECISION_HASH}"
    )

    log(
        f"R35U_REFERENCE_DECISION_HASH="
        f"{R35U_REFERENCE_DECISION_HASH}"
    )

    log(
        f"HASH_SERIALIZER="
        f"{HASH_SERIALIZER}"
    )

    log(
        f"R35Y_DEDUPE_FILE="
        f"{R35Y_DEDUPE_FILE}"
    )

    log(
        f"R35Y_DECISION_FILE="
        f"{R35Y_DECISION_FILE}"
    )

    log(
        f"UPDATE_PRESENT_BEFORE_PROCESSING="
        f"{UPDATE_PRESENT_BEFORE_PROCESSING}"
    )

    log(
        f"EXPECTED_DECISION_HASH_PRESENT_BEFORE="
        f"{EXPECTED_DECISION_HASH_PRESENT_BEFORE}"
    )

    log(
        f"R35Y_REFERENCE_INTEGRITY_OK="
        f"{R35Y_REFERENCE_INTEGRITY_OK}"
    )

    log(
        f"DUPLICATE_GATE_ENTERED="
        f"{DUPLICATE_GATE_ENTERED}"
    )

    log(
        f"DUPLICATE_DETECTED="
        f"{DUPLICATE_DETECTED}"
    )

    log(
        f"NEW_UPDATE_ACCEPTED="
        f"{NEW_UPDATE_ACCEPTED}"
    )

    log(
        f"PIPELINE_CONTINUE_RESULT="
        f"{PIPELINE_CONTINUE_RESULT}"
    )

    log(
        f"TELEGRAM_PROCESSING_ATTEMPTS="
        f"{TELEGRAM_PROCESSING_ATTEMPTS}"
    )

    log(
        f"SIGNAL_PARSE_COUNT="
        f"{SIGNAL_PARSE_COUNT}"
    )

    log(
        f"SIGNAL_VALIDATION_COUNT="
        f"{SIGNAL_VALIDATION_COUNT}"
    )

    log(
        f"SYNTHETIC_DECISION_CREATION_COUNT="
        f"{SYNTHETIC_DECISION_CREATION_COUNT}"
    )

    log(
        f"DURABLE_UPDATE_COMMITS="
        f"{DURABLE_UPDATE_COMMITS}"
    )

    log(
        f"DURABLE_DECISION_COMMITS="
        f"{DURABLE_DECISION_COMMITS}"
    )

    log(
        f"DURABLE_REGISTRY_MUTATIONS="
        f"{DURABLE_REGISTRY_MUTATIONS}"
    )

    log(
        f"UPDATE_PRESENT_AFTER_PROCESSING="
        f"{UPDATE_PRESENT_AFTER_PROCESSING}"
    )

    log(
        f"EXPECTED_DECISION_HASH_PRESENT_AFTER="
        f"{EXPECTED_DECISION_HASH_PRESENT_AFTER}"
    )

    log(
        f"DEDUPE_FILE_SHA256_BEFORE="
        f"{DEDUPE_FILE_SHA256_BEFORE}"
    )

    log(
        f"DEDUPE_FILE_SHA256_AFTER="
        f"{DEDUPE_FILE_SHA256_AFTER}"
    )

    log(
        f"DECISION_FILE_SHA256_BEFORE="
        f"{DECISION_FILE_SHA256_BEFORE}"
    )

    log(
        f"DECISION_FILE_SHA256_AFTER="
        f"{DECISION_FILE_SHA256_AFTER}"
    )

    log(
        f"DEDUPE_FILE_UNCHANGED="
        f"{DEDUPE_FILE_UNCHANGED}"
    )

    log(
        f"DECISION_FILE_UNCHANGED="
        f"{DECISION_FILE_UNCHANGED}"
    )

    log(
        f"PRE_PARSE_REPLAY_REJECTION_OK="
        f"{PRE_PARSE_REPLAY_REJECTION_OK}"
    )

    log(
        f"ZERO_MUTATION_REPLAY_OK="
        f"{ZERO_MUTATION_REPLAY_OK}"
    )

    log(
        f"ZERO_WRITE_FIREBREAK_OK="
        f"{ZERO_WRITE_FIREBREAK_OK}"
    )

    log(
        f"TEST_STATUS="
        f"{TEST_STATUS}"
    )

    log(
        f"FAILURES="
        f"{','.join(FAILURES) if FAILURES else 'NONE'}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        f"LEVERAGE_MUTATIONS="
        f"{LEVERAGE_MUTATIONS}"
    )

    log(
        f"MARGIN_MODE_MUTATIONS="
        f"{MARGIN_MODE_MUTATIONS}"
    )

    log(
        f"POSITION_MUTATIONS="
        f"{POSITION_MUTATIONS}"
    )

    log(
        f"REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )

    log(
        f"DEMO_ORDERS_SENT="
        f"{DEMO_ORDERS_SENT}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"DEMO_ORDER_EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        f"EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED="
        f"{ORDER_SUBMISSION_ENABLED}"
    )


# ==================================================================================================
# HEARTBEAT LOOP
# ==================================================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: HEARTBEAT={heartbeat} "
            f"R35Y_REFERENCE_INTEGRITY_OK="
            f"{R35Y_REFERENCE_INTEGRITY_OK} "
            f"DUPLICATE_DETECTED="
            f"{DUPLICATE_DETECTED} "
            f"NEW_UPDATE_ACCEPTED="
            f"{NEW_UPDATE_ACCEPTED} "
            f"SIGNAL_PARSE_COUNT="
            f"{SIGNAL_PARSE_COUNT} "
            f"SIGNAL_VALIDATION_COUNT="
            f"{SIGNAL_VALIDATION_COUNT} "
            f"SYNTHETIC_DECISION_CREATION_COUNT="
            f"{SYNTHETIC_DECISION_CREATION_COUNT} "
            f"DURABLE_UPDATE_COMMITS="
            f"{DURABLE_UPDATE_COMMITS} "
            f"DURABLE_DECISION_COMMITS="
            f"{DURABLE_DECISION_COMMITS} "
            f"DEDUPE_FILE_UNCHANGED="
            f"{DEDUPE_FILE_UNCHANGED} "
            f"DECISION_FILE_UNCHANGED="
            f"{DECISION_FILE_UNCHANGED} "
            f"TEST_STATUS="
            f"{TEST_STATUS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


# ==================================================================================================
# MAIN
# ==================================================================================================

def main():

    start_health_server()

    try:

        run_r35z_tests()

    except Exception as exc:

        global TEST_STATUS

        TEST_STATUS = "FAIL"

        if str(exc) not in FAILURES:
            FAILURES.append(
                f"{exc.__class__.__name__}:{str(exc)}"
            )

        section(
            f"{UNIT}: ERROR DIAGNOSTIC"
        )

        log(
            f"EXCEPTION_CLASS="
            f"{exc.__class__.__name__}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{str(exc)}"
        )

        log(
            f"TEST_STATUS="
            f"{TEST_STATUS}"
        )

        log(
            f"FAILURES="
            f"{','.join(FAILURES)}"
        )

        log(
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES}"
        )

        log(
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS}"
        )

        log(
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

    heartbeat_loop()


if __name__ == "__main__":
    main()

