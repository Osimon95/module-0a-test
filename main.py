

# ======================================================================================
# R35X MAIN.PY
# PURPOSE:
# EXACT R35U-COMPATIBLE DURABLE DUPLICATE-GATE INTEGRATION
#
# R35X PROVES:
# 1. Existing R35U dedupe registry can be loaded read-only.
# 2. Existing R35U decision registry can be loaded read-only.
# 3. The original R35U decision payload reproduces its stored decision hash using:
#       SHA256(SORTED_COMPACT_UTF8(payload))
# 4. The known R35U Telegram update reaches the duplicate gate.
# 5. The duplicate is rejected BEFORE parsing.
# 6. Parser count remains zero.
# 7. Validator count remains zero.
# 8. Synthetic decision creation count remains zero.
# 9. Durable registries are NOT modified.
# 10. Exchange writes/orders/mutations remain zero.
#
# SAFETY:
# REAL ORDER EXECUTION = DISABLED
# DEMO ORDER EXECUTION = DISABLED
# EXCHANGE NETWORK WRITES = DISABLED
# ORDER SUBMISSION = DISABLED
# LEVERAGE MUTATION = DISABLED
# MARGIN MODE MUTATION = DISABLED
# POSITION MUTATION = DISABLED
#
# IMPORTANT:
# R35X DOES NOT WRITE TO THE R35U REGISTRIES.
# ======================================================================================

import os
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ======================================================================================
# PART 1/4
# CONSTANTS + HARD SAFETY FIREBREAK
# ======================================================================================

UNIT = "R35X"

TEST_UPDATE_ID = "R35U_SYNTHETIC_UPDATE_000001"

EXPECTED_ORIGINAL_DECISION_HASH = (
    "ada67682fedff8bbac0608cc96805dc42"
    "ea20bab56f3305c8afa06d7ef89cc94"
)

PERSISTENT_DISK_ROOT = "/var/data"

R35U_STATE_DIR = os.path.join(
    PERSISTENT_DISK_ROOT,
    "r35u_state"
)

R35U_DEDUPE_FILE = os.path.join(
    R35U_STATE_DIR,
    "telegram_processed_updates.json"
)

R35U_DECISION_FILE = os.path.join(
    R35U_STATE_DIR,
    "synthetic_decisions.json"
)

HEALTH_PORT = int(os.environ.get("PORT", "10000"))

HEARTBEAT_SECONDS = 30


# --------------------------------------------------------------------------------------
# ABSOLUTE EXECUTION FIREBREAK
# --------------------------------------------------------------------------------------

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# --------------------------------------------------------------------------------------
# COUNTERS
# --------------------------------------------------------------------------------------

R35X_PROCESSING_ATTEMPTS = 0
TELEGRAM_PROCESSING_ATTEMPTS = 0

SIGNAL_PARSE_COUNT = 0
SIGNAL_VALIDATION_COUNT = 0
SYNTHETIC_DECISION_CREATION_COUNT = 0

DURABLE_REGISTRY_MUTATIONS = 0

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0


# --------------------------------------------------------------------------------------
# RESULT FLAGS
# --------------------------------------------------------------------------------------

R35U_DEDUPE_REGISTRY_LOADED = False
R35U_DECISION_REGISTRY_LOADED = False

R35U_UPDATE_FOUND = False
R35U_UPDATE_LOCATION = None

R35U_DECISION_RECORD_FOUND = False
R35U_DECISION_PAYLOAD_FOUND = False

R35U_STORED_DECISION_HASH = None
R35U_REPRODUCED_DECISION_HASH = None

R35U_DECISION_HASH_VALID = False

DUPLICATE_GATE_ENTERED = False
DUPLICATE_DETECTED = False
DUPLICATE_REJECTED = False
DUPLICATE_REJECTED_BEFORE_PARSE = False

DEDUPE_FILE_UNCHANGED = False
DECISION_FILE_UNCHANGED = False

ZERO_WRITE_FIREBREAK_OK = False
TEST_STATUS = "NOT_RUN"


# ======================================================================================
# LOGGING
# ======================================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True
    )


def line():
    log("-" * 100)


def section(title):
    line()
    log(title)
    line()


def pass_fail(label, condition):
    mark = "✅ PASS" if condition else "❌ FAIL"
    print(
        f"{label:<82} {mark}",
        flush=True
    )


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        body = (
            f"{UNIT} alive\n"
            f"test_status={TEST_STATUS}\n"
            f"duplicate_detected={DUPLICATE_DETECTED}\n"
            f"duplicate_rejected={DUPLICATE_REJECTED}\n"
            f"signal_parse_count={SIGNAL_PARSE_COUNT}\n"
            f"exchange_network_writes={EXCHANGE_NETWORK_WRITES}\n"
            f"order_submissions={ORDER_SUBMISSIONS}\n"
            f"real_order_execution={REAL_ORDER_EXECUTION}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():

    try:
        server = HTTPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True
        )

        thread.start()

        log(
            f"{UNIT}: HEALTH SERVER STARTED "
            f"ON PORT {HEALTH_PORT}"
        )

    except Exception as exc:

        log(
            f"{UNIT}: HEALTH SERVER ERROR "
            f"{type(exc).__name__}: {exc}"
        )


# ======================================================================================
# PART 2/4
# READ-ONLY DURABLE REGISTRY FORENSICS
# ======================================================================================

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):

    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def load_json_read_only(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def canonical_payload_bytes(payload):

    text = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    return text.encode("utf-8")


def payload_sha256(payload):

    return sha256_bytes(
        canonical_payload_bytes(payload)
    )


# --------------------------------------------------------------------------------------
# RECURSIVE JSON SEARCH
# --------------------------------------------------------------------------------------

def json_path_key(base, key):

    if base == "$":
        return f"$.{key}"

    return f"{base}.{key}"


def json_path_index(base, index):

    return f"{base}[{index}]"


def find_exact_string_locations(
    obj,
    target,
    path="$"
):

    matches = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            key_path = json_path_key(
                path,
                str(key)
            )

            if str(key) == target:

                matches.append({
                    "kind": "KEY",
                    "path": key_path,
                    "value": value
                })

            if isinstance(value, str):

                if value == target:

                    matches.append({
                        "kind": "VALUE",
                        "path": key_path,
                        "value": value
                    })

            matches.extend(
                find_exact_string_locations(
                    value,
                    target,
                    key_path
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            item_path = json_path_index(
                path,
                i
            )

            if isinstance(value, str):

                if value == target:

                    matches.append({
                        "kind": "VALUE",
                        "path": item_path,
                        "value": value
                    })

            matches.extend(
                find_exact_string_locations(
                    value,
                    target,
                    item_path
                )
            )

    return matches


# --------------------------------------------------------------------------------------
# FIND DECISION RECORD THAT CONTAINS BOTH:
#   payload
#   decision_hash
#
# THEN VERIFY THE EXACT R35U HASH ALGORITHM DISCOVERED BY R35W.
# --------------------------------------------------------------------------------------

def find_valid_r35u_decision_record(
    obj,
    path="$"
):

    candidates = []

    if isinstance(obj, dict):

        if (
            "payload" in obj
            and isinstance(obj.get("payload"), dict)
            and "decision_hash" in obj
        ):

            payload = obj.get("payload")
            stored_hash = str(
                obj.get("decision_hash")
            )

            reproduced_hash = payload_sha256(
                payload
            )

            candidates.append({
                "path": path,
                "payload_path": (
                    f"{path}.payload"
                ),
                "hash_path": (
                    f"{path}.decision_hash"
                ),
                "payload": payload,
                "stored_hash": stored_hash,
                "reproduced_hash": reproduced_hash,
                "update_id": payload.get(
                    "update_id"
                )
            })

        for key, value in obj.items():

            child_path = json_path_key(
                path,
                str(key)
            )

            candidates.extend(
                find_valid_r35u_decision_record(
                    value,
                    child_path
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            child_path = json_path_index(
                path,
                i
            )

            candidates.extend(
                find_valid_r35u_decision_record(
                    value,
                    child_path
                )
            )

    return candidates


# ======================================================================================
# DURABLE DUPLICATE GATE
# ======================================================================================

def durable_duplicate_gate(
    update_id,
    dedupe_registry
):

    global R35X_PROCESSING_ATTEMPTS
    global TELEGRAM_PROCESSING_ATTEMPTS

    global DUPLICATE_GATE_ENTERED
    global DUPLICATE_DETECTED
    global DUPLICATE_REJECTED
    global DUPLICATE_REJECTED_BEFORE_PARSE

    global SIGNAL_PARSE_COUNT
    global SIGNAL_VALIDATION_COUNT
    global SYNTHETIC_DECISION_CREATION_COUNT

    R35X_PROCESSING_ATTEMPTS += 1
    TELEGRAM_PROCESSING_ATTEMPTS += 1

    DUPLICATE_GATE_ENTERED = True

    log(
        f"DUPLICATE_GATE_INPUT_UPDATE_ID="
        f"{update_id}"
    )

    # ------------------------------------------------------------------
    # THIS SEARCH IS READ-ONLY.
    #
    # It checks whether the exact update ID already exists anywhere
    # in the durable R35U dedupe representation.
    # ------------------------------------------------------------------

    matches = find_exact_string_locations(
        dedupe_registry,
        update_id
    )

    if matches:

        DUPLICATE_DETECTED = True
        DUPLICATE_REJECTED = True

        # --------------------------------------------------------------
        # CRITICAL TEST:
        # RETURN IMMEDIATELY.
        #
        # Nothing below this gate is allowed to execute.
        # --------------------------------------------------------------

        DUPLICATE_REJECTED_BEFORE_PARSE = (
            SIGNAL_PARSE_COUNT == 0
            and SIGNAL_VALIDATION_COUNT == 0
            and SYNTHETIC_DECISION_CREATION_COUNT == 0
        )

        log(
            "DUPLICATE_GATE_RESULT=REJECT"
        )

        log(
            "DUPLICATE_GATE_REASON="
            "UPDATE_ALREADY_PRESENT_IN_DURABLE_REGISTRY"
        )

        log(
            f"DUPLICATE_MATCH_COUNT="
            f"{len(matches)}"
        )

        for i, match in enumerate(
            matches,
            start=1
        ):

            log(
                f"DUPLICATE_MATCH_{i}_KIND="
                f"{match['kind']}"
            )

            log(
                f"DUPLICATE_MATCH_{i}_PATH="
                f"{match['path']}"
            )

        return False

    # ------------------------------------------------------------------
    # THIS BRANCH MUST NOT EXECUTE IN R35X.
    #
    # We deliberately DO NOT implement parsing here.
    # If the durable gate fails to recognize the update,
    # the test fails safely instead of continuing.
    # ------------------------------------------------------------------

    DUPLICATE_DETECTED = False
    DUPLICATE_REJECTED = False
    DUPLICATE_REJECTED_BEFORE_PARSE = False

    log(
        "DUPLICATE_GATE_RESULT=NOT_DUPLICATE"
    )

    log(
        "R35X_SAFETY_ABORT="
        "TEST_UPDATE_WOULD_HAVE_ENTERED_PARSER"
    )

    return False


# ======================================================================================
# PART 3/4
# TEST EXECUTION
# ======================================================================================

def run_r35x():

    global R35U_DEDUPE_REGISTRY_LOADED
    global R35U_DECISION_REGISTRY_LOADED

    global R35U_UPDATE_FOUND
    global R35U_UPDATE_LOCATION

    global R35U_DECISION_RECORD_FOUND
    global R35U_DECISION_PAYLOAD_FOUND

    global R35U_STORED_DECISION_HASH
    global R35U_REPRODUCED_DECISION_HASH
    global R35U_DECISION_HASH_VALID

    global DEDUPE_FILE_UNCHANGED
    global DECISION_FILE_UNCHANGED

    global ZERO_WRITE_FIREBREAK_OK
    global TEST_STATUS

    start_health_server()

    section(
        f"{UNIT}: MAIN.PY ENTERED"
    )

    log(
        "PURPOSE="
        "EXACT R35U-COMPATIBLE DURABLE "
        "DUPLICATE-GATE INTEGRATION"
    )

    log(
        f"TEST_UPDATE_ID="
        f"{TEST_UPDATE_ID}"
    )

    log(
        f"EXPECTED_ORIGINAL_DECISION_HASH="
        f"{EXPECTED_ORIGINAL_DECISION_HASH}"
    )

    log(
        f"PERSISTENT_DISK_ROOT="
        f"{PERSISTENT_DISK_ROOT}"
    )

    log(
        f"R35U_STATE_DIR="
        f"{R35U_STATE_DIR}"
    )

    log(
        f"R35U_DEDUPE_FILE="
        f"{R35U_DEDUPE_FILE}"
    )

    log(
        f"R35U_DECISION_FILE="
        f"{R35U_DECISION_FILE}"
    )

    section(
        f"{UNIT}: HARD SAFETY FIREBREAK"
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

    log(
        f"LEVERAGE_MUTATION_ENABLED="
        f"{LEVERAGE_MUTATION_ENABLED}"
    )

    log(
        f"MARGIN_MODE_MUTATION_ENABLED="
        f"{MARGIN_MODE_MUTATION_ENABLED}"
    )

    log(
        f"POSITION_MUTATION_ENABLED="
        f"{POSITION_MUTATION_ENABLED}"
    )

    log(
        f"SYNTHETIC_TRANSPORT_ONLY="
        f"{SYNTHETIC_TRANSPORT_ONLY}"
    )


    # ==================================================================================
    # TEST 1
    # EXISTING DURABLE FILES
    # ==================================================================================

    section(
        f"{UNIT} TEST 1: EXISTING R35U DURABLE FILES"
    )

    dedupe_exists = os.path.isfile(
        R35U_DEDUPE_FILE
    )

    decision_exists = os.path.isfile(
        R35U_DECISION_FILE
    )

    pass_fail(
        "R35U Dedupe Registry Exists",
        dedupe_exists
    )

    pass_fail(
        "R35U Decision Registry Exists",
        decision_exists
    )

    if not (
        dedupe_exists
        and decision_exists
    ):

        TEST_STATUS = "FAIL"

        log(
            "R35X_ABORT="
            "REQUIRED_R35U_DURABLE_FILE_MISSING"
        )

        return


    # ==================================================================================
    # TEST 2
    # SNAPSHOT ORIGINAL FILE BYTE HASHES
    # ==================================================================================

    section(
        f"{UNIT} TEST 2: PRE-TEST RAW FILE HASH SNAPSHOT"
    )

    try:

        dedupe_hash_before = sha256_file(
            R35U_DEDUPE_FILE
        )

        decision_hash_before = sha256_file(
            R35U_DECISION_FILE
        )

        log(
            f"DEDUPE_FILE_SHA256_BEFORE="
            f"{dedupe_hash_before}"
        )

        log(
            f"DECISION_FILE_SHA256_BEFORE="
            f"{decision_hash_before}"
        )

        pass_fail(
            "Pre-Test Dedupe File Hash Captured",
            bool(dedupe_hash_before)
        )

        pass_fail(
            "Pre-Test Decision File Hash Captured",
            bool(decision_hash_before)
        )

    except Exception as exc:

        TEST_STATUS = "FAIL"

        log(
            f"PRE_TEST_FILE_HASH_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        return


    # ==================================================================================
    # TEST 3
    # READ R35U DEDUPE REGISTRY
    # ==================================================================================

    section(
        f"{UNIT} TEST 3: LOAD R35U DEDUPE REGISTRY READ-ONLY"
    )

    try:

        dedupe_registry = load_json_read_only(
            R35U_DEDUPE_FILE
        )

        R35U_DEDUPE_REGISTRY_LOADED = True

    except Exception as exc:

        dedupe_registry = None

        log(
            f"R35U_DEDUPE_LOAD_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

    pass_fail(
        "R35U Durable Dedupe Registry Loaded",
        R35U_DEDUPE_REGISTRY_LOADED
    )

    if not R35U_DEDUPE_REGISTRY_LOADED:

        TEST_STATUS = "FAIL"
        return


    # ==================================================================================
    # TEST 4
    # LOCATE ORIGINAL UPDATE
    # ==================================================================================

    section(
        f"{UNIT} TEST 4: LOCATE ORIGINAL R35U UPDATE"
    )

    update_matches = find_exact_string_locations(
        dedupe_registry,
        TEST_UPDATE_ID
    )

    R35U_UPDATE_FOUND = (
        len(update_matches) > 0
    )

    if R35U_UPDATE_FOUND:

        R35U_UPDATE_LOCATION = (
            update_matches[0]["path"]
        )

    log(
        f"R35U_UPDATE_MATCH_COUNT="
        f"{len(update_matches)}"
    )

    if R35U_UPDATE_LOCATION:

        log(
            f"R35U_UPDATE_LOCATION="
            f"{R35U_UPDATE_LOCATION}"
        )

    pass_fail(
        "Original R35U Telegram Update Found",
        R35U_UPDATE_FOUND
    )

    if not R35U_UPDATE_FOUND:

        TEST_STATUS = "FAIL"
        return


    # ==================================================================================
    # TEST 5
    # LOAD DECISION REGISTRY
    # ==================================================================================

    section(
        f"{UNIT} TEST 5: LOAD R35U DECISION REGISTRY READ-ONLY"
    )

    try:

        decision_registry = load_json_read_only(
            R35U_DECISION_FILE
        )

        R35U_DECISION_REGISTRY_LOADED = True

    except Exception as exc:

        decision_registry = None

        log(
            f"R35U_DECISION_LOAD_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

    pass_fail(
        "R35U Durable Decision Registry Loaded",
        R35U_DECISION_REGISTRY_LOADED
    )

    if not R35U_DECISION_REGISTRY_LOADED:

        TEST_STATUS = "FAIL"
        return


    # ==================================================================================
    # TEST 6
    # EXACT R35U HASH REPRODUCTION
    # ==================================================================================

    section(
        f"{UNIT} TEST 6: EXACT R35U DECISION HASH VERIFICATION"
    )

    decision_candidates = (
        find_valid_r35u_decision_record(
            decision_registry
        )
    )

    log(
        f"DECISION_RECORD_CANDIDATE_COUNT="
        f"{len(decision_candidates)}"
    )

    winning_candidate = None

    for candidate in decision_candidates:

        if (
            candidate["update_id"]
            == TEST_UPDATE_ID
        ):

            if (
                candidate["stored_hash"]
                == EXPECTED_ORIGINAL_DECISION_HASH
            ):

                winning_candidate = candidate
                break

    if winning_candidate is None:

        # Secondary exact-hash search in case
        # the historical payload does not expose update_id
        # in the expected place.

        for candidate in decision_candidates:

            if (
                candidate["stored_hash"]
                == EXPECTED_ORIGINAL_DECISION_HASH
            ):

                winning_candidate = candidate
                break


    if winning_candidate:

        R35U_DECISION_RECORD_FOUND = True
        R35U_DECISION_PAYLOAD_FOUND = True

        R35U_STORED_DECISION_HASH = (
            winning_candidate[
                "stored_hash"
            ]
        )

        R35U_REPRODUCED_DECISION_HASH = (
            winning_candidate[
                "reproduced_hash"
            ]
        )

        log(
            f"WINNING_DECISION_RECORD_PATH="
            f"{winning_candidate['path']}"
        )

        log(
            f"WINNING_PAYLOAD_PATH="
            f"{winning_candidate['payload_path']}"
        )

        log(
            f"WINNING_HASH_PATH="
            f"{winning_candidate['hash_path']}"
        )

        log(
            "WINNING_HASH_SERIALIZER="
            "SORTED_COMPACT_UTF8"
        )

        log(
            f"R35U_STORED_DECISION_HASH="
            f"{R35U_STORED_DECISION_HASH}"
        )

        log(
            f"R35U_REPRODUCED_DECISION_HASH="
            f"{R35U_REPRODUCED_DECISION_HASH}"
        )

        R35U_DECISION_HASH_VALID = (
            R35U_STORED_DECISION_HASH
            == EXPECTED_ORIGINAL_DECISION_HASH
            and
            R35U_REPRODUCED_DECISION_HASH
            == EXPECTED_ORIGINAL_DECISION_HASH
        )


    pass_fail(
        "Original R35U Decision Record Found",
        R35U_DECISION_RECORD_FOUND
    )

    pass_fail(
        "Original R35U Decision Payload Found",
        R35U_DECISION_PAYLOAD_FOUND
    )

    pass_fail(
        "Stored R35U Decision Hash Matches Expected",
        (
            R35U_STORED_DECISION_HASH
            == EXPECTED_ORIGINAL_DECISION_HASH
        )
    )

    pass_fail(
        "R35U Payload Reproduces Stored Decision Hash",
        R35U_DECISION_HASH_VALID
    )

    if not R35U_DECISION_HASH_VALID:

        TEST_STATUS = "FAIL"
        return


    # ==================================================================================
    # TEST 7
    # PRODUCTION-STYLE PRE-PARSE DUPLICATE GATE
    # ==================================================================================

    section(
        f"{UNIT} TEST 7: PRE-PARSE DURABLE DUPLICATE GATE"
    )

    processing_result = durable_duplicate_gate(
        TEST_UPDATE_ID,
        dedupe_registry
    )

    log(
        f"PIPELINE_CONTINUE_RESULT="
        f"{processing_result}"
    )

    pass_fail(
        "Duplicate Gate Entered",
        DUPLICATE_GATE_ENTERED
    )

    pass_fail(
        "Existing Durable Update Detected",
        DUPLICATE_DETECTED
    )

    pass_fail(
        "Duplicate Rejected",
        DUPLICATE_REJECTED
    )

    pass_fail(
        "Duplicate Rejected Before Parser",
        DUPLICATE_REJECTED_BEFORE_PARSE
    )


    # ==================================================================================
    # TEST 8
    # CONFIRM PIPELINE NEVER ADVANCED
    # ==================================================================================

    section(
        f"{UNIT} TEST 8: CONFIRM ZERO DOWNSTREAM PIPELINE ENTRY"
    )

    pass_fail(
        "Telegram Processing Attempt Count = 1",
        TELEGRAM_PROCESSING_ATTEMPTS == 1
    )

    pass_fail(
        "Parser Entry Count Remains Zero",
        SIGNAL_PARSE_COUNT == 0
    )

    pass_fail(
        "Validator Entry Count Remains Zero",
        SIGNAL_VALIDATION_COUNT == 0
    )

    pass_fail(
        "Synthetic Decision Creation Count Remains Zero",
        SYNTHETIC_DECISION_CREATION_COUNT == 0
    )


    # ==================================================================================
    # TEST 9
    # PROVE REGISTRIES WERE NOT MUTATED
    # ==================================================================================

    section(
        f"{UNIT} TEST 9: DURABLE REGISTRY IMMUTABILITY"
    )

    try:

        dedupe_hash_after = sha256_file(
            R35U_DEDUPE_FILE
        )

        decision_hash_after = sha256_file(
            R35U_DECISION_FILE
        )

        log(
            f"DEDUPE_FILE_SHA256_AFTER="
            f"{dedupe_hash_after}"
        )

        log(
            f"DECISION_FILE_SHA256_AFTER="
            f"{decision_hash_after}"
        )

        DEDUPE_FILE_UNCHANGED = (
            dedupe_hash_before
            == dedupe_hash_after
        )

        DECISION_FILE_UNCHANGED = (
            decision_hash_before
            == decision_hash_after
        )

    except Exception as exc:

        log(
            f"POST_TEST_FILE_HASH_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        DEDUPE_FILE_UNCHANGED = False
        DECISION_FILE_UNCHANGED = False


    pass_fail(
        "R35U Dedupe Registry Byte-Identical",
        DEDUPE_FILE_UNCHANGED
    )

    pass_fail(
        "R35U Decision Registry Byte-Identical",
        DECISION_FILE_UNCHANGED
    )

    pass_fail(
        "Durable Registry Mutation Count = 0",
        DURABLE_REGISTRY_MUTATIONS == 0
    )


    # ==================================================================================
    # TEST 10
    # FINAL ZERO-WRITE FIREBREAK
    # ==================================================================================

    section(
        f"{UNIT} TEST 10: FINAL ZERO-WRITE FIREBREAK"
    )

    pass_fail(
        "Exchange Network Writes = 0",
        EXCHANGE_NETWORK_WRITES == 0
    )

    pass_fail(
        "Order Submissions = 0",
        ORDER_SUBMISSIONS == 0
    )

    pass_fail(
        "Leverage Mutations = 0",
        LEVERAGE_MUTATIONS == 0
    )

    pass_fail(
        "Margin Mode Mutations = 0",
        MARGIN_MODE_MUTATIONS == 0
    )

    pass_fail(
        "Position Mutations = 0",
        POSITION_MUTATIONS == 0
    )

    pass_fail(
        "Real Orders Sent = 0",
        REAL_ORDERS_SENT == 0
    )

    pass_fail(
        "Demo Orders Sent = 0",
        DEMO_ORDERS_SENT == 0
    )


    ZERO_WRITE_FIREBREAK_OK = all([
        EXCHANGE_NETWORK_WRITES == 0,
        ORDER_SUBMISSIONS == 0,
        LEVERAGE_MUTATIONS == 0,
        MARGIN_MODE_MUTATIONS == 0,
        POSITION_MUTATIONS == 0,
        REAL_ORDERS_SENT == 0,
        DEMO_ORDERS_SENT == 0,
        DURABLE_REGISTRY_MUTATIONS == 0
    ])


    # ==================================================================================
    # FINAL RESULT
    # ==================================================================================

    all_required = all([

        R35U_DEDUPE_REGISTRY_LOADED,

        R35U_DECISION_REGISTRY_LOADED,

        R35U_UPDATE_FOUND,

        R35U_DECISION_RECORD_FOUND,

        R35U_DECISION_PAYLOAD_FOUND,

        R35U_DECISION_HASH_VALID,

        DUPLICATE_GATE_ENTERED,

        DUPLICATE_DETECTED,

        DUPLICATE_REJECTED,

        DUPLICATE_REJECTED_BEFORE_PARSE,

        TELEGRAM_PROCESSING_ATTEMPTS == 1,

        SIGNAL_PARSE_COUNT == 0,

        SIGNAL_VALIDATION_COUNT == 0,

        SYNTHETIC_DECISION_CREATION_COUNT == 0,

        DEDUPE_FILE_UNCHANGED,

        DECISION_FILE_UNCHANGED,

        ZERO_WRITE_FIREBREAK_OK
    ])

    TEST_STATUS = (
        "PASS"
        if all_required
        else "FAIL"
    )


    # ==================================================================================
    # PART 4/4
    # FINAL TEST SUMMARY
    # ==================================================================================

    section(
        f"{UNIT}: FINAL TEST SUMMARY"
    )

    log(
        "PURPOSE="
        "EXACT R35U-COMPATIBLE DURABLE "
        "DUPLICATE-GATE INTEGRATION"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_UPDATE_ID}"
    )

    log(
        f"EXPECTED_ORIGINAL_DECISION_HASH="
        f"{EXPECTED_ORIGINAL_DECISION_HASH}"
    )

    log(
        f"R35U_DEDUPE_FILE="
        f"{R35U_DEDUPE_FILE}"
    )

    log(
        f"R35U_DECISION_FILE="
        f"{R35U_DECISION_FILE}"
    )

    log(
        f"R35U_DURABLE_RECORD_LOADED="
        f"{R35U_DEDUPE_REGISTRY_LOADED}"
    )

    log(
        f"R35U_DECISION_REGISTRY_LOADED="
        f"{R35U_DECISION_REGISTRY_LOADED}"
    )

    log(
        f"R35U_EXPECTED_UPDATE_DISCOVERED="
        f"{R35U_UPDATE_FOUND}"
    )

    log(
        f"R35U_DECISION_RECORD_FOUND="
        f"{R35U_DECISION_RECORD_FOUND}"
    )

    log(
        f"R35U_DECISION_HASH_VALID="
        f"{R35U_DECISION_HASH_VALID}"
    )

    log(
        f"R35U_STORED_DECISION_HASH="
        f"{R35U_STORED_DECISION_HASH}"
    )

    log(
        f"R35U_REPRODUCED_DECISION_HASH="
        f"{R35U_REPRODUCED_DECISION_HASH}"
    )

    log(
        "R35U_HASH_SERIALIZER="
        "SORTED_COMPACT_UTF8"
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
        f"DUPLICATE_REJECTED="
        f"{DUPLICATE_REJECTED}"
    )

    log(
        f"DUPLICATE_REJECTED_BEFORE_PARSE="
        f"{DUPLICATE_REJECTED_BEFORE_PARSE}"
    )

    log(
        f"R35X_PROCESSING_ATTEMPTS="
        f"{R35X_PROCESSING_ATTEMPTS}"
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
        f"DEDUPE_FILE_UNCHANGED="
        f"{DEDUPE_FILE_UNCHANGED}"
    )

    log(
        f"DECISION_FILE_UNCHANGED="
        f"{DECISION_FILE_UNCHANGED}"
    )

    log(
        f"DURABLE_REGISTRY_MUTATIONS="
        f"{DURABLE_REGISTRY_MUTATIONS}"
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


# ======================================================================================
# HEARTBEAT
# ======================================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: "
            f"HEARTBEAT={heartbeat} "
            f"R35U_DURABLE_RECORD_LOADED="
            f"{R35U_DEDUPE_REGISTRY_LOADED} "
            f"R35U_DECISION_HASH_VALID="
            f"{R35U_DECISION_HASH_VALID} "
            f"DUPLICATE_DETECTED="
            f"{DUPLICATE_DETECTED} "
            f"DUPLICATE_REJECTED="
            f"{DUPLICATE_REJECTED} "
            f"DUPLICATE_REJECTED_BEFORE_PARSE="
            f"{DUPLICATE_REJECTED_BEFORE_PARSE} "
            f"TELEGRAM_PROCESSING_ATTEMPTS="
            f"{TELEGRAM_PROCESSING_ATTEMPTS} "
            f"SIGNAL_PARSE_COUNT="
            f"{SIGNAL_PARSE_COUNT} "
            f"TEST_STATUS="
            f"{TEST_STATUS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# ======================================================================================
# ENTRY POINT
# ======================================================================================

if __name__ == "__main__":

    try:

        run_r35x()

    except Exception as exc:

        TEST_STATUS = "FAIL"

        section(
            f"{UNIT}: UNHANDLED TEST ERROR"
        )

        log(
            f"EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{exc}"
        )

    heartbeat_loop()

