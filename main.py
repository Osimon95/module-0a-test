

# ============================================================
# R36B main.py
# PURPOSE:
# CROSS-RESTART EXACTLY-ONCE TELEGRAM UPDATE REPLAY REJECTION
#
# This unit:
# 1. Loads the durable R36A dedupe registry.
# 2. Loads the durable R36A decision registry.
# 3. Replays the exact R36A Telegram update ID.
# 4. Requires rejection BEFORE signal parsing.
# 5. Verifies the stored R36A decision hash remains unchanged.
# 6. Verifies both durable registry files remain byte-identical.
# 7. Performs ZERO exchange writes.
# 8. Sends ZERO real or demo orders.
#
# IMPORTANT:
# This test intentionally depends on the durable files created
# by R36A remaining on the persistent Render disk.
# ============================================================

import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ============================================================
# R36B CONFIGURATION
# ============================================================

UNIT = "R36B"

PORT = int(os.environ.get("PORT", "10000"))

PERSISTENT_DISK_ROOT = "/var/data"

# IMPORTANT:
# R36B MUST load the exact durable R36A state.
STATE_DIR = os.path.join(
    PERSISTENT_DISK_ROOT,
    "r36a_state",
)

DEDUPE_FILE = os.path.join(
    STATE_DIR,
    "telegram_dedupe_registry.json",
)

DECISION_FILE = os.path.join(
    STATE_DIR,
    "telegram_decision_registry.json",
)

TEST_TELEGRAM_UPDATE_ID = (
    "R36A_SYNTHETIC_UPDATE_000001"
)

EXPECTED_R36A_DECISION_HASH = (
    "6093c2add383e5cf2489cb6d52d1dea56f91ea63a506490a9f205870150406bc"
)


# ============================================================
# HARD SAFETY FIREBREAKS
# ============================================================

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


# ============================================================
# R36B TEST COUNTERS
# ============================================================

TELEGRAM_PROCESSING_ATTEMPTS = 0

SIGNAL_PARSE_COUNT = 0
SIGNAL_VALIDATION_COUNT = 0
SYNTHETIC_DECISION_CREATION_COUNT = 0

DURABLE_UPDATE_COMMITS = 0
DURABLE_DECISION_COMMITS = 0
DURABLE_REGISTRY_MUTATIONS = 0


# ============================================================
# TEST STATE
# ============================================================

TEST_STATUS = "UNKNOWN"
FAILURES = []

HEARTBEAT = 0

R36A_DEDUPE_REGISTRY = None
R36A_DECISION_REGISTRY = None

DEDUPE_FILE_SHA256_BEFORE = None
DECISION_FILE_SHA256_BEFORE = None

DEDUPE_FILE_SHA256_AFTER = None
DECISION_FILE_SHA256_AFTER = None

STORED_DECISION_HASH = None

UPDATE_SEEN_BEFORE_STARTUP = False
DUPLICATE_DETECTED = False
PIPELINE_CONTINUE_RESULT = None

CROSS_RESTART_REPLAY_REJECTION_OK = False
PRE_PARSE_REJECTION_OK = False
ZERO_MUTATION_OK = False
DECISION_HASH_PRESERVED = False
FILES_UNCHANGED = False
ZERO_WRITE_FIREBREAK_OK = False


# ============================================================
# LOGGING
# ============================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def separator():
    log("-" * 100)


def pass_fail(condition):
    return "✅ PASS" if condition else "❌ FAIL"


def add_failure(name):
    if name not in FAILURES:
        FAILURES.append(name)


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path in ("/", "/health", "/healthz"):

            payload = {
                "unit": UNIT,
                "status": TEST_STATUS,
                "purpose": (
                    "cross_restart_exactly_once_"
                    "telegram_replay_rejection"
                ),
                "real_order_execution": REAL_ORDER_EXECUTION,
                "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
                "order_submissions": ORDER_SUBMISSIONS,
                "heartbeat": HEARTBEAT,
            }

            body = json.dumps(
                payload,
                sort_keys=True,
            ).encode()

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

        else:

            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():

    try:

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
            f"{UNIT}: HEALTH SERVER STARTED "
            f"ON PORT {PORT}"
        )

    except Exception as exc:

        log(
            f"{UNIT}: HEALTH SERVER ERROR="
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# FILE UTILITIES
# ============================================================

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def file_sha256(path):

    with open(path, "rb") as f:
        data = f.read()

    return sha256_bytes(data)


def load_json_file(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# REGISTRY NORMALIZATION / SEARCH
# ============================================================

def registry_contains_update(
    registry,
    update_id,
):
    """
    R36A may store registry data as either:
    - dict keyed by update ID
    - list of records
    - nested dict/list structures

    Search recursively without mutating anything.
    """

    target = str(update_id)

    if isinstance(registry, dict):

        if target in registry:
            return True

        for key, value in registry.items():

            if str(key) == target:
                return True

            if isinstance(
                value,
                (dict, list),
            ):
                if registry_contains_update(
                    value,
                    target,
                ):
                    return True

            elif str(value) == target:
                return True

        return False

    if isinstance(registry, list):

        for item in registry:

            if isinstance(
                item,
                (dict, list),
            ):

                if registry_contains_update(
                    item,
                    target,
                ):
                    return True

            elif str(item) == target:
                return True

        return False

    return str(registry) == target


def find_decision_hash(
    registry,
    update_id,
):
    """
    Attempts to find the R36A decision hash associated
    with the synthetic Telegram update.

    Supports several reasonable registry structures.
    """

    target = str(update_id)

    if isinstance(registry, dict):

        # ---------------------------------------------
        # Case 1:
        # {
        #   "R36A_SYNTHETIC_UPDATE_000001": {
        #       "decision_hash": "..."
        #   }
        # }
        # ---------------------------------------------

        if target in registry:

            value = registry[target]

            if isinstance(value, str):

                if len(value) == 64:
                    return value

            if isinstance(value, dict):

                for field in (
                    "decision_hash",
                    "hash",
                    "sha256",
                ):

                    candidate = value.get(field)

                    if isinstance(
                        candidate,
                        str,
                    ) and len(candidate) == 64:

                        return candidate

        # ---------------------------------------------
        # Case 2:
        # {
        #   "update_id": "...",
        #   "decision_hash": "..."
        # }
        # ---------------------------------------------

        possible_update_id = None

        for field in (
            "update_id",
            "telegram_update_id",
            "test_update_id",
        ):

            if field in registry:

                possible_update_id = str(
                    registry[field]
                )

                break

        if possible_update_id == target:

            for field in (
                "decision_hash",
                "hash",
                "sha256",
            ):

                candidate = registry.get(field)

                if isinstance(
                    candidate,
                    str,
                ) and len(candidate) == 64:

                    return candidate

        # ---------------------------------------------
        # Recursive search
        # ---------------------------------------------

        for value in registry.values():

            if isinstance(
                value,
                (dict, list),
            ):

                result = find_decision_hash(
                    value,
                    target,
                )

                if result:
                    return result

    elif isinstance(registry, list):

        for item in registry:

            if isinstance(
                item,
                (dict, list),
            ):

                result = find_decision_hash(
                    item,
                    target,
                )

                if result:
                    return result

    return None


# ============================================================
# SYNTHETIC PIPELINE
# ============================================================

def parse_signal(_telegram_update):

    global SIGNAL_PARSE_COUNT

    SIGNAL_PARSE_COUNT += 1

    return {
        "parsed": True,
    }


def validate_signal(_parsed_signal):

    global SIGNAL_VALIDATION_COUNT

    SIGNAL_VALIDATION_COUNT += 1

    return True


def create_synthetic_decision(
    _parsed_signal,
):

    global SYNTHETIC_DECISION_CREATION_COUNT

    SYNTHETIC_DECISION_CREATION_COUNT += 1

    return {
        "synthetic": True,
    }


def process_telegram_update(
    telegram_update,
):
    """
    Exact intended R36B control flow:

        durable dedupe check
               |
               v
        duplicate exists?
          YES -> RETURN FALSE
          NO  -> parse

    Since R36A already committed the test update,
    R36B MUST return before parse_signal().
    """

    global TELEGRAM_PROCESSING_ATTEMPTS
    global DUPLICATE_DETECTED

    TELEGRAM_PROCESSING_ATTEMPTS += 1

    update_id = str(
        telegram_update["update_id"]
    )

    # ------------------------------------------------
    # CRITICAL PRE-PARSE DEDUPE BOUNDARY
    # ------------------------------------------------

    already_seen = registry_contains_update(
        R36A_DEDUPE_REGISTRY,
        update_id,
    )

    if already_seen:

        DUPLICATE_DETECTED = True

        return False

    # ------------------------------------------------
    # THESE LINES MUST NEVER RUN IN R36B
    # ------------------------------------------------

    parsed = parse_signal(
        telegram_update
    )

    valid = validate_signal(
        parsed
    )

    if not valid:
        return False

    create_synthetic_decision(
        parsed
    )

    return True


# ============================================================
# R36B TEST EXECUTION
# ============================================================

def run_r36b_tests():

    global TEST_STATUS
    global R36A_DEDUPE_REGISTRY
    global R36A_DECISION_REGISTRY

    global DEDUPE_FILE_SHA256_BEFORE
    global DECISION_FILE_SHA256_BEFORE
    global DEDUPE_FILE_SHA256_AFTER
    global DECISION_FILE_SHA256_AFTER

    global STORED_DECISION_HASH

    global UPDATE_SEEN_BEFORE_STARTUP
    global PIPELINE_CONTINUE_RESULT

    global CROSS_RESTART_REPLAY_REJECTION_OK
    global PRE_PARSE_REJECTION_OK
    global ZERO_MUTATION_OK
    global DECISION_HASH_PRESERVED
    global FILES_UNCHANGED
    global ZERO_WRITE_FIREBREAK_OK

    separator()
    log(f"{UNIT}: MAIN.PY ENTERED")
    separator()

    log(
        "PURPOSE=CROSS-RESTART EXACTLY-ONCE "
        "TELEGRAM REPLAY REJECTION BEFORE PARSE"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"EXPECTED_R36A_DECISION_HASH="
        f"{EXPECTED_R36A_DECISION_HASH}"
    )

    log(
        f"PERSISTENT_DISK_ROOT="
        f"{PERSISTENT_DISK_ROOT}"
    )

    log(
        f"R36A_STATE_DIR="
        f"{STATE_DIR}"
    )

    log(
        f"R36A_DEDUPE_FILE="
        f"{DEDUPE_FILE}"
    )

    log(
        f"R36A_DECISION_FILE="
        f"{DECISION_FILE}"
    )

    separator()

    # ========================================================
    # TEST 1
    # SAFETY CONFIGURATION
    # ========================================================

    log(
        f"{UNIT} TEST 1: "
        "HARD SAFETY CONFIGURATION"
    )

    separator()

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

    safety_ok = (
        REAL_ORDER_EXECUTION is False
        and FIRST_REAL_ORDER_ALLOWED is False
        and DEMO_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MODE_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
    )

    if not safety_ok:
        add_failure(
            "SAFETY_CONFIGURATION_FAILED"
        )

    separator()

    # ========================================================
    # TEST 2
    # R36A DURABLE FILE AVAILABILITY
    # ========================================================

    log(
        f"{UNIT} TEST 2: "
        "R36A DURABLE STATE AVAILABILITY"
    )

    separator()

    state_dir_exists = os.path.isdir(
        STATE_DIR
    )

    dedupe_file_exists = os.path.isfile(
        DEDUPE_FILE
    )

    decision_file_exists = os.path.isfile(
        DECISION_FILE
    )

    log(
        f"R36A_STATE_DIR_EXISTS="
        f"{state_dir_exists}"
    )

    log(
        f"R36A_DEDUPE_FILE_EXISTS="
        f"{dedupe_file_exists}"
    )

    log(
        f"R36A_DECISION_FILE_EXISTS="
        f"{decision_file_exists}"
    )

    if not state_dir_exists:
        add_failure(
            "R36A_STATE_DIR_MISSING"
        )

    if not dedupe_file_exists:
        add_failure(
            "R36A_DEDUPE_FILE_MISSING"
        )

    if not decision_file_exists:
        add_failure(
            "R36A_DECISION_FILE_MISSING"
        )

    if FAILURES:
        final_summary()
        return

    separator()

    # ========================================================
    # TEST 3
    # LOAD R36A DURABLE REGISTRIES
    # ========================================================

    log(
        f"{UNIT} TEST 3: "
        "LOAD R36A DURABLE REGISTRIES"
    )

    separator()

    try:

        DEDUPE_FILE_SHA256_BEFORE = (
            file_sha256(
                DEDUPE_FILE
            )
        )

        DECISION_FILE_SHA256_BEFORE = (
            file_sha256(
                DECISION_FILE
            )
        )

        R36A_DEDUPE_REGISTRY = (
            load_json_file(
                DEDUPE_FILE
            )
        )

        R36A_DECISION_REGISTRY = (
            load_json_file(
                DECISION_FILE
            )
        )

        dedupe_load_ok = True
        decision_load_ok = True

    except Exception as exc:

        dedupe_load_ok = False
        decision_load_ok = False

        log(
            f"DURABLE_REGISTRY_LOAD_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        add_failure(
            "R36A_DURABLE_REGISTRY_LOAD_FAILED"
        )

    log(
        "R36A Durable Dedupe Registry Loaded"
        f"    {pass_fail(dedupe_load_ok)}"
    )

    log(
        "R36A Durable Decision Registry Loaded"
        f"    {pass_fail(decision_load_ok)}"
    )

    log(
        f"DEDUPE_FILE_SHA256_BEFORE="
        f"{DEDUPE_FILE_SHA256_BEFORE}"
    )

    log(
        f"DECISION_FILE_SHA256_BEFORE="
        f"{DECISION_FILE_SHA256_BEFORE}"
    )

    if FAILURES:
        final_summary()
        return

    separator()

    # ========================================================
    # TEST 4
    # VERIFY R36A UPDATE EXISTS BEFORE THIS STARTUP
    # ========================================================

    log(
        f"{UNIT} TEST 4: "
        "CROSS-RESTART DURABLE UPDATE PRESENCE"
    )

    separator()

    UPDATE_SEEN_BEFORE_STARTUP = (
        registry_contains_update(
            R36A_DEDUPE_REGISTRY,
            TEST_TELEGRAM_UPDATE_ID,
        )
    )

    STORED_DECISION_HASH = (
        find_decision_hash(
            R36A_DECISION_REGISTRY,
            TEST_TELEGRAM_UPDATE_ID,
        )
    )

    DECISION_HASH_PRESERVED = (
        STORED_DECISION_HASH
        == EXPECTED_R36A_DECISION_HASH
    )

    log(
        f"UPDATE_SEEN_BEFORE_STARTUP="
        f"{UPDATE_SEEN_BEFORE_STARTUP}"
    )

    log(
        f"STORED_DECISION_HASH="
        f"{STORED_DECISION_HASH}"
    )

    log(
        f"EXPECTED_DECISION_HASH="
        f"{EXPECTED_R36A_DECISION_HASH}"
    )

    log(
        f"DECISION_HASH_PRESERVED="
        f"{DECISION_HASH_PRESERVED}"
    )

    if not UPDATE_SEEN_BEFORE_STARTUP:
        add_failure(
            "R36A_UPDATE_NOT_FOUND_DURABLY"
        )

    if not DECISION_HASH_PRESERVED:
        add_failure(
            "R36A_DECISION_HASH_MISMATCH"
        )

    separator()

    # ========================================================
    # TEST 5
    # CROSS-RESTART REPLAY REJECTION BEFORE PARSE
    # ========================================================

    log(
        f"{UNIT} TEST 5: "
        "CROSS-RESTART REPLAY REJECTION BEFORE PARSE"
    )

    separator()

    replay_update = {
        "update_id":
            TEST_TELEGRAM_UPDATE_ID,

        "message": {
            "text":
                "R36A SYNTHETIC SIGNAL REPLAY"
        },
    }

    PIPELINE_CONTINUE_RESULT = (
        process_telegram_update(
            replay_update
        )
    )

    log(
        f"REPLAY_DUPLICATE_DETECTED="
        f"{DUPLICATE_DETECTED}"
    )

    log(
        f"REPLAY_PIPELINE_CONTINUE_RESULT="
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

    PRE_PARSE_REJECTION_OK = (
        DUPLICATE_DETECTED is True
        and PIPELINE_CONTINUE_RESULT is False
        and TELEGRAM_PROCESSING_ATTEMPTS == 1
        and SIGNAL_PARSE_COUNT == 0
        and SIGNAL_VALIDATION_COUNT == 0
        and SYNTHETIC_DECISION_CREATION_COUNT == 0
    )

    ZERO_MUTATION_OK = (
        DURABLE_UPDATE_COMMITS == 0
        and DURABLE_DECISION_COMMITS == 0
        and DURABLE_REGISTRY_MUTATIONS == 0
    )

    CROSS_RESTART_REPLAY_REJECTION_OK = (
        UPDATE_SEEN_BEFORE_STARTUP
        and PRE_PARSE_REJECTION_OK
        and ZERO_MUTATION_OK
    )

    log(
        f"PRE_PARSE_REJECTION_OK="
        f"{PRE_PARSE_REJECTION_OK}"
    )

    log(
        f"ZERO_MUTATION_OK="
        f"{ZERO_MUTATION_OK}"
    )

    log(
        f"CROSS_RESTART_REPLAY_REJECTION_OK="
        f"{CROSS_RESTART_REPLAY_REJECTION_OK}"
    )

    if not PRE_PARSE_REJECTION_OK:
        add_failure(
            "CROSS_RESTART_PRE_PARSE_REJECTION_FAILED"
        )

    if not ZERO_MUTATION_OK:
        add_failure(
            "CROSS_RESTART_REPLAY_MUTATED_STATE"
        )

    separator()

    # ========================================================
    # TEST 6
    # DURABLE FILE IMMUTABILITY
    # ========================================================

    log(
        f"{UNIT} TEST 6: "
        "CROSS-RESTART REPLAY FILE IMMUTABILITY"
    )

    separator()

    try:

        DEDUPE_FILE_SHA256_AFTER = (
            file_sha256(
                DEDUPE_FILE
            )
        )

        DECISION_FILE_SHA256_AFTER = (
            file_sha256(
                DECISION_FILE
            )
        )

    except Exception as exc:

        log(
            f"POST_REPLAY_FILE_HASH_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        add_failure(
            "POST_REPLAY_FILE_HASH_FAILED"
        )

    dedupe_file_unchanged = (
        DEDUPE_FILE_SHA256_BEFORE
        == DEDUPE_FILE_SHA256_AFTER
    )

    decision_file_unchanged = (
        DECISION_FILE_SHA256_BEFORE
        == DECISION_FILE_SHA256_AFTER
    )

    FILES_UNCHANGED = (
        dedupe_file_unchanged
        and decision_file_unchanged
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
        f"DEDUPE_FILE_UNCHANGED_ON_REPLAY="
        f"{dedupe_file_unchanged}"
    )

    log(
        f"DECISION_FILE_UNCHANGED_ON_REPLAY="
        f"{decision_file_unchanged}"
    )

    log(
        f"FILES_UNCHANGED="
        f"{FILES_UNCHANGED}"
    )

    if not dedupe_file_unchanged:
        add_failure(
            "DEDUPE_FILE_CHANGED_ON_REPLAY"
        )

    if not decision_file_unchanged:
        add_failure(
            "DECISION_FILE_CHANGED_ON_REPLAY"
        )

    separator()

    # ========================================================
    # TEST 7
    # ZERO EXCHANGE WRITE FIREBREAK
    # ========================================================

    log(
        f"{UNIT} TEST 7: "
        "ZERO WRITE FIREBREAK"
    )

    separator()

    ZERO_WRITE_FIREBREAK_OK = (
        EXCHANGE_NETWORK_WRITES == 0
        and ORDER_SUBMISSIONS == 0
        and LEVERAGE_MUTATIONS == 0
        and MARGIN_MODE_MUTATIONS == 0
        and POSITION_MUTATIONS == 0
        and REAL_ORDERS_SENT == 0
        and DEMO_ORDERS_SENT == 0
        and REAL_ORDER_EXECUTION is False
        and FIRST_REAL_ORDER_ALLOWED is False
        and DEMO_ORDER_EXECUTION is False
        and EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        and ORDER_SUBMISSION_ENABLED is False
    )

    log(
        f"ZERO_WRITE_FIREBREAK_OK="
        f"{ZERO_WRITE_FIREBREAK_OK}"
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

    if not ZERO_WRITE_FIREBREAK_OK:
        add_failure(
            "ZERO_WRITE_FIREBREAK_FAILED"
        )

    final_summary()


# ============================================================
# FINAL SUMMARY
# ============================================================

def final_summary():

    global TEST_STATUS

    TEST_STATUS = (
        "PASS"
        if len(FAILURES) == 0
        else "FAIL"
    )

    separator()
    log(f"{UNIT}: FINAL TEST SUMMARY")
    separator()

    summary_checks = [

        (
            "R36A State Directory Exists",
            os.path.isdir(STATE_DIR),
        ),

        (
            "R36A Dedupe Registry Exists",
            os.path.isfile(DEDUPE_FILE),
        ),

        (
            "R36A Decision Registry Exists",
            os.path.isfile(DECISION_FILE),
        ),

        (
            "R36A Update Seen Before Startup",
            UPDATE_SEEN_BEFORE_STARTUP,
        ),

        (
            "R36A Decision Hash Preserved",
            DECISION_HASH_PRESERVED,
        ),

        (
            "Replay Duplicate Detected",
            DUPLICATE_DETECTED,
        ),

        (
            "Replay Rejected Before Parse",
            PRE_PARSE_REJECTION_OK,
        ),

        (
            "Signal Parse Count = 0",
            SIGNAL_PARSE_COUNT == 0,
        ),

        (
            "Signal Validation Count = 0",
            SIGNAL_VALIDATION_COUNT == 0,
        ),

        (
            "Synthetic Decision Creation Count = 0",
            SYNTHETIC_DECISION_CREATION_COUNT == 0,
        ),

        (
            "Durable Update Commit Count = 0",
            DURABLE_UPDATE_COMMITS == 0,
        ),

        (
            "Durable Decision Commit Count = 0",
            DURABLE_DECISION_COMMITS == 0,
        ),

        (
            "Replay Registry Mutation Zero",
            DURABLE_REGISTRY_MUTATIONS == 0,
        ),

        (
            "Dedupe File Unchanged",
            DEDUPE_FILE_SHA256_BEFORE
            == DEDUPE_FILE_SHA256_AFTER
            if DEDUPE_FILE_SHA256_AFTER
            else False,
        ),

        (
            "Decision File Unchanged",
            DECISION_FILE_SHA256_BEFORE
            == DECISION_FILE_SHA256_AFTER
            if DECISION_FILE_SHA256_AFTER
            else False,
        ),

        (
            "Cross Restart Replay Rejection",
            CROSS_RESTART_REPLAY_REJECTION_OK,
        ),

        (
            "Exchange Network Writes = 0",
            EXCHANGE_NETWORK_WRITES == 0,
        ),

        (
            "Order Submissions = 0",
            ORDER_SUBMISSIONS == 0,
        ),

        (
            "Leverage Mutations = 0",
            LEVERAGE_MUTATIONS == 0,
        ),

        (
            "Margin Mode Mutations = 0",
            MARGIN_MODE_MUTATIONS == 0,
        ),

        (
            "Position Mutations = 0",
            POSITION_MUTATIONS == 0,
        ),

        (
            "Real Orders Sent = 0",
            REAL_ORDERS_SENT == 0,
        ),

        (
            "Demo Orders Sent = 0",
            DEMO_ORDERS_SENT == 0,
        ),

        (
            "Zero Write Firebreak",
            ZERO_WRITE_FIREBREAK_OK,
        ),
    ]

    for name, condition in summary_checks:

        print(
            f"{name:<80}"
            f"{pass_fail(condition)}",
            flush=True,
        )

    separator()

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"EXPECTED_R36A_DECISION_HASH="
        f"{EXPECTED_R36A_DECISION_HASH}"
    )

    log(
        f"STORED_DECISION_HASH="
        f"{STORED_DECISION_HASH}"
    )

    log(
        f"UPDATE_SEEN_BEFORE_STARTUP="
        f"{UPDATE_SEEN_BEFORE_STARTUP}"
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
        f"CROSS_RESTART_REPLAY_REJECTION_OK="
        f"{CROSS_RESTART_REPLAY_REJECTION_OK}"
    )

    log(
        f"TEST_STATUS="
        f"{TEST_STATUS}"
    )

    log(
        "FAILURES="
        + (
            "NONE"
            if not FAILURES
            else ",".join(FAILURES)
        )
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

    separator()


# ============================================================
# HEARTBEAT LOOP
# ============================================================

def heartbeat_loop():

    global HEARTBEAT

    while True:

        HEARTBEAT += 1

        log(
            f"{UNIT}: HEARTBEAT={HEARTBEAT} "
            f"TEST_STATUS={TEST_STATUS} "
            f"UPDATE_SEEN_BEFORE_STARTUP="
            f"{UPDATE_SEEN_BEFORE_STARTUP} "
            f"DUPLICATE_DETECTED="
            f"{DUPLICATE_DETECTED} "
            f"SIGNAL_PARSE_COUNT="
            f"{SIGNAL_PARSE_COUNT} "
            f"CROSS_RESTART_REPLAY_REJECTION_OK="
            f"{CROSS_RESTART_REPLAY_REJECTION_OK} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


# ============================================================
# MAIN
# ============================================================

def main():

    start_health_server()

    try:

        run_r36b_tests()

    except Exception as exc:

        global TEST_STATUS

        TEST_STATUS = "FAIL"

        add_failure(
            "UNHANDLED_EXCEPTION"
        )

        separator()

        log(
            f"{UNIT}: UNHANDLED EXCEPTION="
            f"{type(exc).__name__}: {exc}"
        )

        separator()

        final_summary()

    heartbeat_loop()


if __name__ == "__main__":
    main()

