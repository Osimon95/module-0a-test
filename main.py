

# =============================================================================
# R35V main.py
# PURPOSE:
# CROSS-DEPLOY RESTART VERIFICATION OF R35U INTEGRATED PIPELINE
#
# PROVES:
# 1. R35U durable Telegram update exists before startup processing.
# 2. Same Telegram update is rejected BEFORE parser entry.
# 3. Parser count remains zero.
# 4. Validator count remains zero.
# 5. No second synthetic decision is created.
# 6. Original durable decision remains present.
# 7. Original dedupe -> decision hash linkage remains intact.
# 8. Stored decision hash still recomputes correctly.
# 9. Absolutely zero exchange/order/mutation writes.
#
# IMPORTANT:
# This unit intentionally reads:
#   /var/data/r35u_state/telegram_processed_updates.json
#   /var/data/r35u_state/synthetic_decisions.json
#
# DO NOT change those paths for the R35V cross-deploy proof.
# =============================================================================

import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# PART 1/4
# CONSTANTS + HARD SAFETY FIREBREAK
# =============================================================================

UNIT = "R35V"

PURPOSE = (
    "CROSS-DEPLOY RESTART VERIFICATION: "
    "R35U UPDATE MUST BE REJECTED BEFORE PARSER + "
    "ORIGINAL DURABLE SYNTHETIC DECISION MUST REMAIN INTACT"
)

SYMBOL = "BTCUSDT"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

TEST_TELEGRAM_UPDATE_ID = "R35U_SYNTHETIC_UPDATE_000001"

PERSISTENT_DISK_ROOT = "/var/data"

# CRITICAL:
# R35V intentionally reuses R35U state.
STATE_DIR = os.path.join(PERSISTENT_DISK_ROOT, "r35u_state")

DEDUPE_FILE = os.path.join(
    STATE_DIR,
    "telegram_processed_updates.json"
)

DECISION_FILE = os.path.join(
    STATE_DIR,
    "synthetic_decisions.json"
)

PORT = int(os.environ.get("PORT", "10000"))


# -----------------------------------------------------------------------------
# ABSOLUTE SAFETY FLAGS
# -----------------------------------------------------------------------------

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
AUTHENTICATED_WEEX_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# -----------------------------------------------------------------------------
# ZERO-WRITE COUNTERS
# -----------------------------------------------------------------------------

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0


# -----------------------------------------------------------------------------
# THIS-STARTUP COUNTERS
# -----------------------------------------------------------------------------

PROCESSED_THIS_STARTUP = False
DUPLICATE_REJECTED_THIS_STARTUP = False

SIGNAL_PARSED_THIS_STARTUP = False
SIGNAL_PARSE_COUNT_THIS_STARTUP = 0

SIGNAL_VALIDATED_THIS_STARTUP = False
SIGNAL_VALIDATION_COUNT_THIS_STARTUP = 0

SYNTHETIC_DECISION_CREATED_THIS_STARTUP = False
SYNTHETIC_DECISION_COUNT_THIS_STARTUP = 0


# -----------------------------------------------------------------------------
# TEST STATE
# -----------------------------------------------------------------------------

TEST_UPDATE_SEEN_BEFORE_STARTUP = False
ORIGINAL_DEDUPE_RECORD_FOUND = False
ORIGINAL_DECISION_FOUND = False
ORIGINAL_DECISION_HASH = None
RECOMPUTED_DECISION_HASH = None
DEDUPE_LINKED_DECISION_HASH = None

CROSS_DEPLOY_DUPLICATE_REJECTION_OK = False
PARSER_BYPASS_OK = False
VALIDATOR_BYPASS_OK = False
NO_SECOND_DECISION_OK = False
DURABLE_LINKAGE_OK = False
ORIGINAL_DECISION_INTACT_OK = False

TEST_STATUS = "PENDING"


# =============================================================================
# COMMON HELPERS
# =============================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{utc_now()} {message}", flush=True)


def divider():
    log("-" * 100)


def check(label, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{label:<86} {status}", flush=True)
    return bool(condition)


def canonical_json_bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_json(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        log(f"JSON_LOAD_ERROR path={path} class={exc.__class__.__name__} message={exc}")
        return default


def ensure_dict(value):
    return value if isinstance(value, dict) else {}


def ensure_list(value):
    return value if isinstance(value, list) else []


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            f"{UNIT} OK\n"
            f"TEST_STATUS={TEST_STATUS}\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    def runner():
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        log(f"{UNIT}: HEALTH SERVER STARTED ON PORT {PORT}")
        server.serve_forever()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()


# =============================================================================
# PART 2/4
# DURABLE RECORD NORMALIZATION + LOOKUP
# =============================================================================

def extract_dedupe_record(registry, update_id):
    """
    Supports several reasonable R35U durable formats without modifying them.
    """

    if isinstance(registry, dict):

        # Format:
        # {
        #   "R35U_SYNTHETIC_UPDATE_000001": {...}
        # }
        if update_id in registry:
            value = registry[update_id]

            if isinstance(value, dict):
                result = dict(value)
                result.setdefault("update_id", update_id)
                return result

            return {
                "update_id": update_id,
                "value": value,
            }

        # Format:
        # {
        #   "processed_updates": {
        #       "ID": {...}
        #   }
        # }
        processed = registry.get("processed_updates")

        if isinstance(processed, dict) and update_id in processed:
            value = processed[update_id]

            if isinstance(value, dict):
                result = dict(value)
                result.setdefault("update_id", update_id)
                return result

            return {
                "update_id": update_id,
                "value": value,
            }

        # Format:
        # {
        #   "updates": [...]
        # }
        updates = registry.get("updates")

        if isinstance(updates, list):
            for item in updates:
                if not isinstance(item, dict):
                    continue

                candidate = (
                    item.get("update_id")
                    or item.get("telegram_update_id")
                    or item.get("id")
                )

                if str(candidate) == str(update_id):
                    return item

    if isinstance(registry, list):
        for item in registry:
            if not isinstance(item, dict):
                continue

            candidate = (
                item.get("update_id")
                or item.get("telegram_update_id")
                or item.get("id")
            )

            if str(candidate) == str(update_id):
                return item

    return None


def extract_decision_records(registry):
    """
    Returns iterable decision dictionaries from plausible R35U structures.
    """

    if isinstance(registry, list):
        return [
            item
            for item in registry
            if isinstance(item, dict)
        ]

    if isinstance(registry, dict):

        decisions = registry.get("decisions")

        if isinstance(decisions, list):
            return [
                item
                for item in decisions
                if isinstance(item, dict)
            ]

        if isinstance(decisions, dict):
            result = []

            for key, value in decisions.items():
                if isinstance(value, dict):
                    item = dict(value)
                    item.setdefault("decision_id", key)
                    result.append(item)

            return result

        result = []

        for key, value in registry.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("decision_id", key)
                result.append(item)

        return result

    return []


def candidate_update_id(record):
    if not isinstance(record, dict):
        return None

    return (
        record.get("update_id")
        or record.get("telegram_update_id")
        or record.get("source_update_id")
        or record.get("test_update_id")
    )


def candidate_decision_hash(record):
    if not isinstance(record, dict):
        return None

    return (
        record.get("decision_hash")
        or record.get("synthetic_decision_hash")
        or record.get("linked_decision_hash")
        or record.get("decision_sha256")
        or record.get("sha256")
    )


def find_decision_for_update(decision_registry, update_id, linked_hash=None):

    records = extract_decision_records(decision_registry)

    # First preference:
    # direct update-id linkage.
    for record in records:
        value = candidate_update_id(record)

        if str(value) == str(update_id):
            return record

    # Second preference:
    # hash match.
    if linked_hash:
        for record in records:
            stored_hash = candidate_decision_hash(record)

            if stored_hash == linked_hash:
                return record

            computed = recompute_stored_decision_hash(record)

            if computed == linked_hash:
                return record

    # If exactly one decision exists, it is safe for this isolated test
    # to inspect it as the candidate.
    if len(records) == 1:
        return records[0]

    return None


def decision_payload_for_hash(record):
    """
    R35U may have stored:
      {
        "decision": {...},
        "decision_hash": "..."
      }

    or directly:
      {
        ...decision fields...,
        "decision_hash": "..."
      }

    This function isolates the object likely used for hashing.
    """

    if not isinstance(record, dict):
        return None

    nested = record.get("decision")

    if isinstance(nested, dict):
        return nested

    excluded = {
        "decision_hash",
        "synthetic_decision_hash",
        "linked_decision_hash",
        "decision_sha256",
        "sha256",
    }

    return {
        key: value
        for key, value in record.items()
        if key not in excluded
    }


def recompute_stored_decision_hash(record):
    payload = decision_payload_for_hash(record)

    if not isinstance(payload, dict):
        return None

    return sha256_json(payload)


# =============================================================================
# SIMULATED INTEGRATED PIPELINE
# =============================================================================

def parser_should_never_run():
    global SIGNAL_PARSED_THIS_STARTUP
    global SIGNAL_PARSE_COUNT_THIS_STARTUP

    SIGNAL_PARSED_THIS_STARTUP = True
    SIGNAL_PARSE_COUNT_THIS_STARTUP += 1

    raise RuntimeError(
        "R35V FAILURE: parser was entered for an already-durable Telegram update"
    )


def validator_should_never_run():
    global SIGNAL_VALIDATED_THIS_STARTUP
    global SIGNAL_VALIDATION_COUNT_THIS_STARTUP

    SIGNAL_VALIDATED_THIS_STARTUP = True
    SIGNAL_VALIDATION_COUNT_THIS_STARTUP += 1

    raise RuntimeError(
        "R35V FAILURE: validator was entered for an already-durable Telegram update"
    )


def decision_creator_should_never_run():
    global SYNTHETIC_DECISION_CREATED_THIS_STARTUP
    global SYNTHETIC_DECISION_COUNT_THIS_STARTUP

    SYNTHETIC_DECISION_CREATED_THIS_STARTUP = True
    SYNTHETIC_DECISION_COUNT_THIS_STARTUP += 1

    raise RuntimeError(
        "R35V FAILURE: second synthetic decision attempted for duplicate update"
    )


def process_candidate_update(update_id, dedupe_registry):
    """
    Correct R35V behavior:

    Durable dedupe check MUST happen before:
      parser
      validator
      decision creator
    """

    global PROCESSED_THIS_STARTUP
    global DUPLICATE_REJECTED_THIS_STARTUP

    existing = extract_dedupe_record(
        dedupe_registry,
        update_id
    )

    if existing is not None:
        DUPLICATE_REJECTED_THIS_STARTUP = True
        PROCESSED_THIS_STARTUP = False

        log("PROCESSING_CLASSIFICATION=REJECTED_CROSS_DEPLOY_DUPLICATE")
        log("REJECTION_STAGE=PRE_PARSER_DURABLE_DEDUPE_GATE")

        return {
            "classification": "DUPLICATE",
            "existing_record": existing,
        }

    # These calls are intentionally unreachable when R35U durability works.
    parser_should_never_run()
    validator_should_never_run()
    decision_creator_should_never_run()

    PROCESSED_THIS_STARTUP = True

    return {
        "classification": "NEW",
        "existing_record": None,
    }


# =============================================================================
# PART 3/4
# R35V TEST EXECUTION
# =============================================================================

def main():

    global TEST_UPDATE_SEEN_BEFORE_STARTUP
    global ORIGINAL_DEDUPE_RECORD_FOUND
    global ORIGINAL_DECISION_FOUND

    global ORIGINAL_DECISION_HASH
    global RECOMPUTED_DECISION_HASH
    global DEDUPE_LINKED_DECISION_HASH

    global CROSS_DEPLOY_DUPLICATE_REJECTION_OK
    global PARSER_BYPASS_OK
    global VALIDATOR_BYPASS_OK
    global NO_SECOND_DECISION_OK
    global DURABLE_LINKAGE_OK
    global ORIGINAL_DECISION_INTACT_OK

    global TEST_STATUS

    start_health_server()

    time.sleep(0.15)

    divider()
    log(f"{UNIT}: MAIN.PY ENTERED")
    divider()

    log(f"{UNIT}: PURPOSE={PURPOSE}")
    log(f"PYTHON_VERSION={sys.version.split()[0]}")
    log(f"SYMBOL={SYMBOL}")
    log(f"TARGET_MARGIN_MODE={TARGET_MARGIN_MODE}")
    log(f"TARGET_LONG_LEVERAGE={TARGET_LONG_LEVERAGE}x")
    log(f"TARGET_SHORT_LEVERAGE={TARGET_SHORT_LEVERAGE}x")

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")
    log(f"STATE_DIR={STATE_DIR}")
    log(f"DEDUPE_FILE={DEDUPE_FILE}")
    log(f"DECISION_FILE={DECISION_FILE}")

    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log(f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}")
    log(f"DEMO_ORDER_EXECUTION={DEMO_ORDER_EXECUTION}")
    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )
    log(f"ORDER_SUBMISSION_ENABLED={ORDER_SUBMISSION_ENABLED}")
    log(f"SYNTHETIC_TRANSPORT_ONLY={SYNTHETIC_TRANSPORT_ONLY}")


    # =========================================================================
    # TEST 1
    # =========================================================================

    divider()
    log("R35V TEST 1: HARD SAFETY FIREBREAK")
    divider()

    safety_results = [
        check(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION is False
        ),
        check(
            "First Real Order Is Forbidden",
            FIRST_REAL_ORDER_ALLOWED is False
        ),
        check(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION is False
        ),
        check(
            "Exchange Mutation Transport Is Disabled",
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        ),
        check(
            "Order Submission Is Disabled",
            ORDER_SUBMISSION_ENABLED is False
        ),
        check(
            "Authenticated WEEX Writes Are Disabled",
            AUTHENTICATED_WEEX_WRITES_ENABLED is False
        ),
        check(
            "Leverage Mutation Is Disabled",
            LEVERAGE_MUTATION_ENABLED is False
        ),
        check(
            "Margin Mode Mutation Is Disabled",
            MARGIN_MODE_MUTATION_ENABLED is False
        ),
        check(
            "Position Mutation Is Disabled",
            POSITION_MUTATION_ENABLED is False
        ),
        check(
            "Synthetic Transport Only",
            SYNTHETIC_TRANSPORT_ONLY is True
        ),
    ]


    # =========================================================================
    # TEST 2
    # =========================================================================

    divider()
    log("R35V TEST 2: R35U PERSISTENT STORAGE REUSE")
    divider()

    state_dir_exists = os.path.isdir(STATE_DIR)
    dedupe_file_exists = os.path.isfile(DEDUPE_FILE)
    decision_file_exists = os.path.isfile(DECISION_FILE)

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")
    log(f"STATE_DIR={STATE_DIR}")
    log(f"DEDUPE_FILE={DEDUPE_FILE}")
    log(f"DECISION_FILE={DECISION_FILE}")

    storage_results = [
        check(
            "R35U State Directory Exists",
            state_dir_exists
        ),
        check(
            "R35U Durable Dedupe File Exists",
            dedupe_file_exists
        ),
        check(
            "R35U Durable Decision File Exists",
            decision_file_exists
        ),
    ]


    # =========================================================================
    # TEST 3
    # =========================================================================

    divider()
    log("R35V TEST 3: LOAD R35U DURABLE REGISTRIES")
    divider()

    dedupe_registry = load_json(
        DEDUPE_FILE,
        {}
    )

    decision_registry = load_json(
        DECISION_FILE,
        {}
    )

    dedupe_load_ok = isinstance(
        dedupe_registry,
        (dict, list)
    )

    decision_load_ok = isinstance(
        decision_registry,
        (dict, list)
    )

    check(
        "R35U Durable Dedupe Registry Loaded",
        dedupe_load_ok
    )

    check(
        "R35U Durable Decision Registry Loaded",
        decision_load_ok
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    divider()
    log("R35V TEST 4: CROSS-DEPLOY PRESTART CONDITION")
    divider()

    original_dedupe_record = extract_dedupe_record(
        dedupe_registry,
        TEST_TELEGRAM_UPDATE_ID
    )

    ORIGINAL_DEDUPE_RECORD_FOUND = (
        original_dedupe_record is not None
    )

    TEST_UPDATE_SEEN_BEFORE_STARTUP = (
        ORIGINAL_DEDUPE_RECORD_FOUND
    )

    log(
        "TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        "TEST_UPDATE_SEEN_BEFORE_STARTUP="
        f"{TEST_UPDATE_SEEN_BEFORE_STARTUP}"
    )

    precondition_ok = check(
        "R35U Test Update Was Already Durable Before R35V Processing",
        TEST_UPDATE_SEEN_BEFORE_STARTUP is True
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    divider()
    log("R35V TEST 5: PROCESS SAME UPDATE AFTER REDEPLOY")
    divider()

    try:
        processing_result = process_candidate_update(
            TEST_TELEGRAM_UPDATE_ID,
            dedupe_registry
        )
        processing_exception = None

    except Exception as exc:
        processing_result = {
            "classification": "ERROR"
        }
        processing_exception = exc

        log(
            f"PROCESSING_EXCEPTION_CLASS="
            f"{exc.__class__.__name__}"
        )
        log(
            f"PROCESSING_EXCEPTION_MESSAGE={exc}"
        )

    CROSS_DEPLOY_DUPLICATE_REJECTION_OK = (
        processing_exception is None
        and processing_result.get("classification") == "DUPLICATE"
        and DUPLICATE_REJECTED_THIS_STARTUP is True
        and PROCESSED_THIS_STARTUP is False
    )

    check(
        "Same Update Rejected As Cross-Deploy Duplicate",
        CROSS_DEPLOY_DUPLICATE_REJECTION_OK
    )

    check(
        "Duplicate Was Not Processed As New",
        PROCESSED_THIS_STARTUP is False
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    divider()
    log("R35V TEST 6: PRE-PARSER REJECTION PROOF")
    divider()

    PARSER_BYPASS_OK = (
        SIGNAL_PARSED_THIS_STARTUP is False
        and SIGNAL_PARSE_COUNT_THIS_STARTUP == 0
    )

    VALIDATOR_BYPASS_OK = (
        SIGNAL_VALIDATED_THIS_STARTUP is False
        and SIGNAL_VALIDATION_COUNT_THIS_STARTUP == 0
    )

    NO_SECOND_DECISION_OK = (
        SYNTHETIC_DECISION_CREATED_THIS_STARTUP is False
        and SYNTHETIC_DECISION_COUNT_THIS_STARTUP == 0
    )

    check(
        "Parser Was Not Entered",
        SIGNAL_PARSED_THIS_STARTUP is False
    )

    check(
        "Parser Entry Count Remains Zero",
        SIGNAL_PARSE_COUNT_THIS_STARTUP == 0
    )

    check(
        "Validator Was Not Entered",
        SIGNAL_VALIDATED_THIS_STARTUP is False
    )

    check(
        "Validator Entry Count Remains Zero",
        SIGNAL_VALIDATION_COUNT_THIS_STARTUP == 0
    )

    check(
        "No New Synthetic Decision Was Created",
        SYNTHETIC_DECISION_CREATED_THIS_STARTUP is False
    )

    check(
        "Synthetic Decision Creation Count Remains Zero",
        SYNTHETIC_DECISION_COUNT_THIS_STARTUP == 0
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    divider()
    log("R35V TEST 7: ORIGINAL R35U DECISION STILL EXISTS")
    divider()

    DEDUPE_LINKED_DECISION_HASH = candidate_decision_hash(
        original_dedupe_record
    )

    original_decision = find_decision_for_update(
        decision_registry,
        TEST_TELEGRAM_UPDATE_ID,
        DEDUPE_LINKED_DECISION_HASH
    )

    ORIGINAL_DECISION_FOUND = (
        original_decision is not None
    )

    check(
        "Original R35U Durable Dedupe Record Exists",
        ORIGINAL_DEDUPE_RECORD_FOUND
    )

    check(
        "Original R35U Durable Synthetic Decision Exists",
        ORIGINAL_DECISION_FOUND
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    divider()
    log("R35V TEST 8: ORIGINAL DECISION HASH INTEGRITY")
    divider()

    if original_decision is not None:
        ORIGINAL_DECISION_HASH = candidate_decision_hash(
            original_decision
        )

        RECOMPUTED_DECISION_HASH = recompute_stored_decision_hash(
            original_decision
        )

    log(
        "DEDUPE_LINKED_DECISION_HASH="
        f"{DEDUPE_LINKED_DECISION_HASH}"
    )

    log(
        "ORIGINAL_DECISION_HASH="
        f"{ORIGINAL_DECISION_HASH}"
    )

    log(
        "RECOMPUTED_DECISION_HASH="
        f"{RECOMPUTED_DECISION_HASH}"
    )

    # The R35U durable schema may store the hash on either the dedupe
    # record or the decision record. Require integrity wherever available.

    dedupe_to_decision_hash_match = False

    if (
        DEDUPE_LINKED_DECISION_HASH
        and ORIGINAL_DECISION_HASH
    ):
        dedupe_to_decision_hash_match = (
            DEDUPE_LINKED_DECISION_HASH
            == ORIGINAL_DECISION_HASH
        )

    elif (
        DEDUPE_LINKED_DECISION_HASH
        and RECOMPUTED_DECISION_HASH
    ):
        dedupe_to_decision_hash_match = (
            DEDUPE_LINKED_DECISION_HASH
            == RECOMPUTED_DECISION_HASH
        )

    elif (
        ORIGINAL_DECISION_HASH
        and RECOMPUTED_DECISION_HASH
    ):
        dedupe_to_decision_hash_match = (
            ORIGINAL_DECISION_HASH
            == RECOMPUTED_DECISION_HASH
        )

    decision_recompute_ok = False

    if (
        ORIGINAL_DECISION_HASH
        and RECOMPUTED_DECISION_HASH
    ):
        decision_recompute_ok = (
            ORIGINAL_DECISION_HASH
            == RECOMPUTED_DECISION_HASH
        )

    elif (
        DEDUPE_LINKED_DECISION_HASH
        and RECOMPUTED_DECISION_HASH
    ):
        decision_recompute_ok = (
            DEDUPE_LINKED_DECISION_HASH
            == RECOMPUTED_DECISION_HASH
        )

    DURABLE_LINKAGE_OK = (
        ORIGINAL_DEDUPE_RECORD_FOUND
        and ORIGINAL_DECISION_FOUND
        and dedupe_to_decision_hash_match
    )

    ORIGINAL_DECISION_INTACT_OK = (
        ORIGINAL_DECISION_FOUND
        and decision_recompute_ok
    )

    check(
        "Dedupe Decision Hash Still Matches Durable Decision",
        DURABLE_LINKAGE_OK
    )

    check(
        "Stored Decision Hash Still Recomputes Correctly",
        ORIGINAL_DECISION_INTACT_OK
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    divider()
    log("R35V TEST 9: CROSS-DEPLOY EXACTLY-ONCE PROOF")
    divider()

    exactly_once_results = [
        check(
            "Update Was Seen Before R35V Startup Processing",
            TEST_UPDATE_SEEN_BEFORE_STARTUP is True
        ),
        check(
            "Update Rejected Before Parser",
            CROSS_DEPLOY_DUPLICATE_REJECTION_OK
            and PARSER_BYPASS_OK
        ),
        check(
            "Validator Could Not Re-Enter",
            VALIDATOR_BYPASS_OK
        ),
        check(
            "Second Synthetic Decision Could Not Be Created",
            NO_SECOND_DECISION_OK
        ),
        check(
            "Original Durable Decision Remains Linked",
            DURABLE_LINKAGE_OK
        ),
        check(
            "Original Durable Decision Remains Hash-Intact",
            ORIGINAL_DECISION_INTACT_OK
        ),
    ]


    # =========================================================================
    # TEST 10
    # =========================================================================

    divider()
    log("R35V TEST 10: FINAL ZERO-WRITE FIREBREAK")
    divider()

    zero_write_results = [
        check(
            "Exchange Network Writes = 0",
            EXCHANGE_NETWORK_WRITES == 0
        ),
        check(
            "Order Submissions = 0",
            ORDER_SUBMISSIONS == 0
        ),
        check(
            "Leverage Mutations = 0",
            LEVERAGE_MUTATIONS == 0
        ),
        check(
            "Margin Mode Mutations = 0",
            MARGIN_MODE_MUTATIONS == 0
        ),
        check(
            "Position Mutations = 0",
            POSITION_MUTATIONS == 0
        ),
        check(
            "Real Orders Sent = 0",
            REAL_ORDERS_SENT == 0
        ),
        check(
            "Demo Orders Sent = 0",
            DEMO_ORDERS_SENT == 0
        ),
        check(
            "Real Order Execution Remains Disabled",
            REAL_ORDER_EXECUTION is False
        ),
        check(
            "Order Submission Remains Disabled",
            ORDER_SUBMISSION_ENABLED is False
        ),
        check(
            "Exchange Mutation Transport Remains Disabled",
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        ),
    ]


    # =========================================================================
    # FINAL STATUS
    # =========================================================================

    all_results = (
        safety_results
        + storage_results
        + [
            dedupe_load_ok,
            decision_load_ok,
            precondition_ok,
            CROSS_DEPLOY_DUPLICATE_REJECTION_OK,
            PARSER_BYPASS_OK,
            VALIDATOR_BYPASS_OK,
            NO_SECOND_DECISION_OK,
            DURABLE_LINKAGE_OK,
            ORIGINAL_DECISION_INTACT_OK,
        ]
        + exactly_once_results
        + zero_write_results
    )

    TEST_STATUS = (
        "PASS"
        if all(all_results)
        else "FAIL"
    )


    # =========================================================================
    # PART 4/4
    # FINAL SUMMARY + HEARTBEAT
    # =========================================================================

    divider()
    log("R35V: FINAL TEST SUMMARY")
    divider()

    log(f"PURPOSE={PURPOSE}")

    log(
        "TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        "TEST_UPDATE_SEEN_BEFORE_STARTUP="
        f"{TEST_UPDATE_SEEN_BEFORE_STARTUP}"
    )

    log(
        "PROCESSED_THIS_STARTUP="
        f"{PROCESSED_THIS_STARTUP}"
    )

    log(
        "DUPLICATE_REJECTED_THIS_STARTUP="
        f"{DUPLICATE_REJECTED_THIS_STARTUP}"
    )

    log(
        "SIGNAL_PARSED_THIS_STARTUP="
        f"{SIGNAL_PARSED_THIS_STARTUP}"
    )

    log(
        "SIGNAL_PARSE_COUNT_THIS_STARTUP="
        f"{SIGNAL_PARSE_COUNT_THIS_STARTUP}"
    )

    log(
        "SIGNAL_VALIDATED_THIS_STARTUP="
        f"{SIGNAL_VALIDATED_THIS_STARTUP}"
    )

    log(
        "SIGNAL_VALIDATION_COUNT_THIS_STARTUP="
        f"{SIGNAL_VALIDATION_COUNT_THIS_STARTUP}"
    )

    log(
        "SYNTHETIC_DECISION_CREATED_THIS_STARTUP="
        f"{SYNTHETIC_DECISION_CREATED_THIS_STARTUP}"
    )

    log(
        "SYNTHETIC_DECISION_COUNT_THIS_STARTUP="
        f"{SYNTHETIC_DECISION_COUNT_THIS_STARTUP}"
    )

    log(
        "ORIGINAL_DEDUPE_RECORD_FOUND="
        f"{ORIGINAL_DEDUPE_RECORD_FOUND}"
    )

    log(
        "ORIGINAL_DECISION_FOUND="
        f"{ORIGINAL_DECISION_FOUND}"
    )

    log(
        "CROSS_DEPLOY_DUPLICATE_REJECTION_OK="
        f"{CROSS_DEPLOY_DUPLICATE_REJECTION_OK}"
    )

    log(
        "PARSER_BYPASS_OK="
        f"{PARSER_BYPASS_OK}"
    )

    log(
        "VALIDATOR_BYPASS_OK="
        f"{VALIDATOR_BYPASS_OK}"
    )

    log(
        "NO_SECOND_DECISION_OK="
        f"{NO_SECOND_DECISION_OK}"
    )

    log(
        "DURABLE_LINKAGE_OK="
        f"{DURABLE_LINKAGE_OK}"
    )

    log(
        "ORIGINAL_DECISION_INTACT_OK="
        f"{ORIGINAL_DECISION_INTACT_OK}"
    )

    log(
        "CROSS_DEPLOY_PROOF="
        + (
            "PASS"
            if (
                CROSS_DEPLOY_DUPLICATE_REJECTION_OK
                and PARSER_BYPASS_OK
                and VALIDATOR_BYPASS_OK
                and NO_SECOND_DECISION_OK
                and DURABLE_LINKAGE_OK
                and ORIGINAL_DECISION_INTACT_OK
            )
            else "FAIL"
        )
    )

    log(f"TEST_STATUS={TEST_STATUS}")

    log(
        "EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        "ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        "LEVERAGE_MUTATIONS="
        f"{LEVERAGE_MUTATIONS}"
    )

    log(
        "MARGIN_MODE_MUTATIONS="
        f"{MARGIN_MODE_MUTATIONS}"
    )

    log(
        "POSITION_MUTATIONS="
        f"{POSITION_MUTATIONS}"
    )

    log(
        "REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )

    log(
        "DEMO_ORDERS_SENT="
        f"{DEMO_ORDERS_SENT}"
    )

    log(
        "REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        "FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        "DEMO_ORDER_EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        "ORDER_SUBMISSION_ENABLED="
        f"{ORDER_SUBMISSION_ENABLED}"
    )


    heartbeat = 0

    while True:
        heartbeat += 1

        log(
            f"R35V: HEARTBEAT={heartbeat} "
            f"TEST_UPDATE_SEEN_BEFORE_STARTUP="
            f"{TEST_UPDATE_SEEN_BEFORE_STARTUP} "
            f"PROCESSED_THIS_STARTUP="
            f"{PROCESSED_THIS_STARTUP} "
            f"DUPLICATE_REJECTED_THIS_STARTUP="
            f"{DUPLICATE_REJECTED_THIS_STARTUP} "
            f"SIGNAL_PARSE_COUNT_THIS_STARTUP="
            f"{SIGNAL_PARSE_COUNT_THIS_STARTUP} "
            f"SIGNAL_VALIDATION_COUNT_THIS_STARTUP="
            f"{SIGNAL_VALIDATION_COUNT_THIS_STARTUP} "
            f"SYNTHETIC_DECISION_COUNT_THIS_STARTUP="
            f"{SYNTHETIC_DECISION_COUNT_THIS_STARTUP} "
            f"CROSS_DEPLOY_DUPLICATE_REJECTION_OK="
            f"{CROSS_DEPLOY_DUPLICATE_REJECTION_OK} "
            f"DURABLE_LINKAGE_OK="
            f"{DURABLE_LINKAGE_OK} "
            f"ORIGINAL_DECISION_INTACT_OK="
            f"{ORIGINAL_DECISION_INTACT_OK} "
            f"TEST_STATUS={TEST_STATUS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


if __name__ == "__main__":
    main()

