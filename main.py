

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer


# ======================================================================================
# R36B.3
# CORRECTED CROSS-RESTART TELEGRAM UPDATE REPLAY REJECTION
#
# PURPOSE:
#   1. Load durable R36A Telegram dedupe state.
#   2. Load durable R36A synthetic decision state.
#   3. Use the EXISTING R36A durable update ID.
#   4. Attempt a synthetic replay of that exact update.
#   5. Reject the replay BEFORE signal parsing.
#   6. Prove zero exchange writes / zero order submissions.
#
# IMPORTANT:
#   THIS FILE DOES NOT SEND REAL ORDERS.
#   THIS FILE DOES NOT SEND DEMO ORDERS.
#   THIS FILE DOES NOT MUTATE EXCHANGE STATE.
#   THIS FILE DOES NOT CONSUME REAL TELEGRAM UPDATES.
# ======================================================================================


VERSION = "R36B.3"

PURPOSE = (
    "CORRECTED CROSS-RESTART EXACT R36A TELEGRAM UPDATE "
    "REPLAY REJECTION BEFORE PARSE"
)

EXPECTED_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"

PERSISTENT_DISK_ROOT = Path("/var/data")
R36A_STATE_DIR = PERSISTENT_DISK_ROOT / "r36a_state"

R36A_DEDUPE_FILE = R36A_STATE_DIR / "telegram_processed_updates.json"
R36A_DECISION_FILE = R36A_STATE_DIR / "synthetic_decisions.json"

PORT = int(os.environ.get("PORT", "10000"))


# ======================================================================================
# HARD SAFETY FIREBREAK
# ======================================================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

TELEGRAM_NETWORK_CONSUMPTION_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False


# ======================================================================================
# COUNTERS
# ======================================================================================

exchange_network_writes = 0
order_submissions = 0
real_orders_sent = 0
demo_orders_sent = 0

leverage_mutations = 0
margin_mode_mutations = 0
position_mutations = 0

signal_parse_count = 0
signal_validation_count = 0
synthetic_decision_creation_count = 0

telegram_updates_consumed = 0

persistent_state_modified = False
exchange_request_attempted = False


# ======================================================================================
# TEST STATE
# ======================================================================================

dedupe_registry_readable = False
decision_registry_readable = False

dedupe_read_error = None
decision_read_error = None

dedupe_data = None
decision_data = None

canonical_update_id = None

update_seen_before_startup = False
duplicate_detected = False
duplicate_rejected_before_parse = False

cross_restart_replay_rejection_ok = False

test_status = "FAIL"

heartbeat = 0


# ======================================================================================
# LOGGING
# ======================================================================================

LINE = "-" * 100


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{utc_now()} {message}", flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def result(label, passed):
    symbol = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<84} {symbol}", flush=True)


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = json.dumps(
            {
                "service": VERSION,
                "status": test_status,
                "purpose": PURPOSE,
                "expected_update_id": EXPECTED_UPDATE_ID,
                "canonical_update_id": canonical_update_id,
                "update_seen_before_startup": update_seen_before_startup,
                "duplicate_detected": duplicate_detected,
                "signal_parse_count": signal_parse_count,
                "cross_restart_replay_rejection_ok": (
                    cross_restart_replay_rejection_ok
                ),
                "exchange_network_writes": exchange_network_writes,
                "order_submissions": order_submissions,
                "real_order_execution": REAL_ORDER_EXECUTION,
            },
            sort_keys=True,
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def run_health_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        log(f"{VERSION}: HEALTH SERVER STARTED ON PORT {PORT}")
        server.serve_forever()
    except Exception as exc:
        log(
            f"{VERSION}: HEALTH SERVER ERROR="
            f"{type(exc).__name__}: {exc}"
        )


# ======================================================================================
# READ-ONLY JSON
# ======================================================================================

def read_json_read_only(path):
    """
    Reads an existing JSON file only.

    This function intentionally contains:
      - no mkdir
      - no file creation
      - no file writes
      - no temporary files
      - no atomic replacements
    """

    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ======================================================================================
# UPDATE-ID EXTRACTION
# ======================================================================================

UPDATE_ID_VALUE_KEYS = {
    "update_id",
    "telegram_update_id",
    "telegramUpdateId",
    "telegramUpdateID",
    "source_update_id",
    "source_telegram_update_id",
    "test_update_id",
}


def normalize_id(value):
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return str(value)

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

        # Prevent JSON field names themselves from being treated as IDs.
        if value in UPDATE_ID_VALUE_KEYS:
            return None

        return value

    return None


def extract_update_ids(obj):
    """
    Extracts UPDATE-ID VALUES only.

    R36B.2 showed that generic recursive string scanning could accidentally
    classify the literal field name 'telegram_update_id' as an ID.

    R36B.3 therefore only accepts values attached to known ID fields, plus
    keys of dictionary-shaped registries when those keys themselves resemble
    real update identifiers.
    """

    found = set()

    def walk(value):

        if isinstance(value, dict):

            for key, child in value.items():

                # ----------------------------------------------------------
                # Known update-ID fields: inspect VALUE, never field name.
                # ----------------------------------------------------------
                if key in UPDATE_ID_VALUE_KEYS:

                    if isinstance(child, (str, int)) and not isinstance(
                        child, bool
                    ):
                        normalized = normalize_id(child)

                        if normalized is not None:
                            found.add(normalized)

                    elif isinstance(child, list):

                        for item in child:
                            normalized = normalize_id(item)

                            if normalized is not None:
                                found.add(normalized)

                # ----------------------------------------------------------
                # Some registries may use the actual update ID as dict key.
                # Only accept keys that look like real update identities.
                # ----------------------------------------------------------
                key_text = str(key).strip()

                if (
                    key_text.startswith("R36A_SYNTHETIC_UPDATE_")
                    or key_text.startswith("R35")
                    or key_text.isdigit()
                ):
                    normalized_key = normalize_id(key_text)

                    if normalized_key is not None:
                        found.add(normalized_key)

                walk(child)

        elif isinstance(value, list):

            for item in value:
                walk(item)

    walk(obj)

    return sorted(found)


# ======================================================================================
# DEDUPE LOOKUP
# ======================================================================================

def update_exists_in_registry(update_id, registry):
    """
    Exact identity test against all extracted update IDs.

    No state is modified.
    """

    ids = extract_update_ids(registry)

    return update_id in ids


# ======================================================================================
# SYNTHETIC REPLAY ENVELOPE
# ======================================================================================

def build_replay_update(update_id):
    """
    Construct an in-memory synthetic representation of the SAME durable R36A
    update.

    It is deliberately NOT a live Telegram poll result.
    """

    return {
        "update_id": update_id,
        "message": {
            "message_id": "R36B3_SYNTHETIC_REPLAY_MESSAGE",
            "text": (
                "R36B.3 synthetic replay payload. "
                "THIS TEXT MUST NEVER REACH THE SIGNAL PARSER."
            ),
            "chat": {
                "id": "R36B3_SYNTHETIC_CHAT"
            },
        },
        "_synthetic_test": True,
        "_network_received": False,
        "_purpose": (
            "CROSS_RESTART_DUPLICATE_REJECTION_BEFORE_SIGNAL_PARSE"
        ),
    }


# ======================================================================================
# SIGNAL PARSER TRIPWIRE
# ======================================================================================

def parse_signal(_telegram_update):
    """
    This function MUST NOT execute during a successful R36B.3 test.
    """

    global signal_parse_count

    signal_parse_count += 1

    raise RuntimeError(
        "R36B.3 SAFETY FAILURE: SIGNAL PARSER WAS REACHED FOR "
        "A DURABLE DUPLICATE UPDATE"
    )


# ======================================================================================
# REPLAY PIPELINE
# ======================================================================================

def process_telegram_update(telegram_update):
    """
    Correct processing order:

        update received in-memory
                 |
                 v
        obtain update identity
                 |
                 v
        durable dedupe lookup
                 |
          +------+------+
          |             |
       duplicate        new
          |             |
          v             v
       REJECT        parse signal

    R36B.3 only tests the duplicate branch.
    """

    global duplicate_detected
    global duplicate_rejected_before_parse

    update_id = normalize_id(telegram_update.get("update_id"))

    if update_id is None:
        raise RuntimeError("Synthetic replay has no usable update_id")

    # ------------------------------------------------------------------
    # FIRST PIPELINE BOUNDARY:
    # durable dedupe lookup BEFORE parser
    # ------------------------------------------------------------------

    if update_exists_in_registry(update_id, dedupe_data):

        duplicate_detected = True
        duplicate_rejected_before_parse = True

        log(
            f"DUPLICATE_REJECTED_BEFORE_PARSE=True "
            f"UPDATE_ID={update_id}"
        )

        return False

    # ------------------------------------------------------------------
    # If this line is reached, dedupe protection failed.
    # ------------------------------------------------------------------

    parse_signal(telegram_update)

    return True


# ======================================================================================
# MAIN TEST
# ======================================================================================

def run_test():

    global dedupe_registry_readable
    global decision_registry_readable

    global dedupe_read_error
    global decision_read_error

    global dedupe_data
    global decision_data

    global canonical_update_id

    global update_seen_before_startup
    global duplicate_detected
    global duplicate_rejected_before_parse

    global cross_restart_replay_rejection_ok
    global test_status


    # ==================================================================================
    # TEST 1
    # ==================================================================================

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(f"PURPOSE={PURPOSE}")
    log(f"PYTHON_VERSION={sys.version.split()[0]}")

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")
    log(f"R36A_STATE_DIR={R36A_STATE_DIR}")

    log(f"R36A_DEDUPE_FILE={R36A_DEDUPE_FILE}")
    log(f"R36A_DECISION_FILE={R36A_DECISION_FILE}")

    log(f"EXPECTED_UPDATE_ID={EXPECTED_UPDATE_ID}")


    # ==================================================================================
    # TEST 2
    # ==================================================================================

    section(f"{VERSION} TEST 2: HARD SAFETY FIREBREAK")

    result(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION is False,
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

    result(
        "Telegram Network Consumption Disabled",
        TELEGRAM_NETWORK_CONSUMPTION_ENABLED is False,
    )

    result(
        "First Real Order Forbidden",
        FIRST_REAL_ORDER_ALLOWED is False,
    )


    # ==================================================================================
    # TEST 3
    # ==================================================================================

    section(f"{VERSION} TEST 3: LOAD R36A DURABLE REGISTRIES READ-ONLY")

    log(
        f"PERSISTENT_DISK_AVAILABLE="
        f"{PERSISTENT_DISK_ROOT.exists()}"
    )

    log(
        f"R36A_STATE_DIR_EXISTS="
        f"{R36A_STATE_DIR.exists()}"
    )

    log(
        f"R36A_DEDUPE_FILE_EXISTS="
        f"{R36A_DEDUPE_FILE.exists()}"
    )

    log(
        f"R36A_DECISION_FILE_EXISTS="
        f"{R36A_DECISION_FILE.exists()}"
    )

    try:
        dedupe_data = read_json_read_only(R36A_DEDUPE_FILE)
        dedupe_registry_readable = True

    except Exception as exc:

        dedupe_read_error = (
            f"{type(exc).__name__}: {exc}"
        )

    try:
        decision_data = read_json_read_only(R36A_DECISION_FILE)
        decision_registry_readable = True

    except Exception as exc:

        decision_read_error = (
            f"{type(exc).__name__}: {exc}"
        )

    log(f"DEDUPE_READ_ERROR={dedupe_read_error}")
    log(f"DECISION_READ_ERROR={decision_read_error}")

    result(
        "R36A Durable Dedupe Registry Readable",
        dedupe_registry_readable,
    )

    result(
        "R36A Durable Decision Registry Readable",
        decision_registry_readable,
    )


    # ==================================================================================
    # TEST 4
    # ==================================================================================

    section(f"{VERSION} TEST 4: EXTRACT DURABLE R36A UPDATE IDS")

    if dedupe_registry_readable:
        dedupe_ids = extract_update_ids(dedupe_data)
    else:
        dedupe_ids = []

    if decision_registry_readable:
        decision_ids = extract_update_ids(decision_data)
    else:
        decision_ids = []

    shared_ids = sorted(
        set(dedupe_ids).intersection(decision_ids)
    )

    log(f"R36A_DEDUPE_UPDATE_ID_COUNT={len(dedupe_ids)}")

    for index, value in enumerate(dedupe_ids, start=1):
        log(
            f"R36A_DEDUPE_UPDATE_ID_{index}="
            f"{value}"
        )

    log(
        f"R36A_DECISION_UPDATE_ID_COUNT="
        f"{len(decision_ids)}"
    )

    for index, value in enumerate(decision_ids, start=1):
        log(
            f"R36A_DECISION_UPDATE_ID_{index}="
            f"{value}"
        )

    log(
        f"R36A_SHARED_UPDATE_ID_COUNT="
        f"{len(shared_ids)}"
    )

    for index, value in enumerate(shared_ids, start=1):
        log(
            f"R36A_SHARED_UPDATE_ID_{index}="
            f"{value}"
        )

    result(
        "At Least One Shared Durable R36A Update ID Found",
        len(shared_ids) >= 1,
    )


    # ==================================================================================
    # TEST 5
    # ==================================================================================

    section(f"{VERSION} TEST 5: CANONICAL ID RECONCILIATION")

    expected_in_dedupe = (
        EXPECTED_UPDATE_ID in dedupe_ids
    )

    expected_in_decision = (
        EXPECTED_UPDATE_ID in decision_ids
    )

    expected_shared = (
        EXPECTED_UPDATE_ID in shared_ids
    )

    if expected_shared:
        canonical_update_id = EXPECTED_UPDATE_ID

    elif len(shared_ids) == 1:
        canonical_update_id = shared_ids[0]

    else:
        canonical_update_id = None

    log(f"EXPECTED_UPDATE_ID={EXPECTED_UPDATE_ID}")

    log(
        f"EXPECTED_ID_IN_DEDUPE="
        f"{expected_in_dedupe}"
    )

    log(
        f"EXPECTED_ID_IN_DECISION="
        f"{expected_in_decision}"
    )

    log(
        f"EXPECTED_ID_SHARED="
        f"{expected_shared}"
    )

    log(
        f"CANONICAL_R36A_UPDATE_ID="
        f"{canonical_update_id}"
    )

    log(
        f"CANONICAL_MATCHES_EXPECTED="
        f"{canonical_update_id == EXPECTED_UPDATE_ID}"
    )

    result(
        "Correct R36A Expected Update ID Found In Dedupe",
        expected_in_dedupe,
    )

    result(
        "Correct R36A Expected Update ID Found In Decision Registry",
        expected_in_decision,
    )

    result(
        "Correct R36A Expected Update ID Shared By Both Registries",
        expected_shared,
    )

    result(
        "Canonical R36A Update ID Matches Corrected R36B Lookup",
        canonical_update_id == EXPECTED_UPDATE_ID,
    )


    # ==================================================================================
    # TEST 6
    # ==================================================================================

    section(
        f"{VERSION} TEST 6: STARTUP DURABLE DUPLICATE CLASSIFICATION"
    )

    if canonical_update_id is not None:

        update_seen_before_startup = update_exists_in_registry(
            canonical_update_id,
            dedupe_data,
        )

    else:
        update_seen_before_startup = False

    log(
        f"TEST_UPDATE_ID="
        f"{canonical_update_id}"
    )

    log(
        f"UPDATE_SEEN_BEFORE_STARTUP="
        f"{update_seen_before_startup}"
    )

    result(
        "Exact R36A Update Seen Before Startup",
        update_seen_before_startup,
    )


    # ==================================================================================
    # TEST 7
    # ==================================================================================

    section(
        f"{VERSION} TEST 7: EXACT CROSS-RESTART SYNTHETIC REPLAY"
    )

    pipeline_continue_result = None
    replay_error = None

    if canonical_update_id is not None:

        replay_update = build_replay_update(
            canonical_update_id
        )

        log(
            f"REPLAY_UPDATE_ID="
            f"{replay_update['update_id']}"
        )

        log(
            f"REPLAY_IS_SYNTHETIC="
            f"{replay_update['_synthetic_test']}"
        )

        log(
            f"REPLAY_NETWORK_RECEIVED="
            f"{replay_update['_network_received']}"
        )

        try:

            pipeline_continue_result = (
                process_telegram_update(
                    replay_update
                )
            )

        except Exception as exc:

            replay_error = (
                f"{type(exc).__name__}: {exc}"
            )

    else:

        replay_error = (
            "NO_CANONICAL_R36A_UPDATE_ID"
        )

    log(
        f"PIPELINE_CONTINUE_RESULT="
        f"{pipeline_continue_result}"
    )

    log(
        f"REPLAY_ERROR="
        f"{replay_error}"
    )

    log(
        f"DUPLICATE_DETECTED="
        f"{duplicate_detected}"
    )

    log(
        f"DUPLICATE_REJECTED_BEFORE_PARSE="
        f"{duplicate_rejected_before_parse}"
    )

    log(
        f"SIGNAL_PARSE_COUNT="
        f"{signal_parse_count}"
    )

    log(
        f"SIGNAL_VALIDATION_COUNT="
        f"{signal_validation_count}"
    )

    log(
        f"SYNTHETIC_DECISION_CREATION_COUNT="
        f"{synthetic_decision_creation_count}"
    )

    result(
        "Synthetic Replay Attempt Completed Without Exception",
        replay_error is None,
    )

    result(
        "Duplicate Detected",
        duplicate_detected,
    )

    result(
        "Replay Rejected",
        pipeline_continue_result is False,
    )

    result(
        "Duplicate Rejected Before Signal Parse",
        duplicate_rejected_before_parse,
    )

    result(
        "Signal Parser Was Not Entered",
        signal_parse_count == 0,
    )

    result(
        "Signal Validation Was Not Entered",
        signal_validation_count == 0,
    )

    result(
        "No New Synthetic Decision Was Created",
        synthetic_decision_creation_count == 0,
    )


    # ==================================================================================
    # TEST 8
    # ==================================================================================

    section(
        f"{VERSION} TEST 8: CROSS-RESTART REPLAY REJECTION PROOF"
    )

    cross_restart_replay_rejection_ok = all(
        [
            dedupe_registry_readable,
            decision_registry_readable,
            expected_in_dedupe,
            expected_in_decision,
            expected_shared,
            canonical_update_id == EXPECTED_UPDATE_ID,
            update_seen_before_startup,
            duplicate_detected,
            duplicate_rejected_before_parse,
            pipeline_continue_result is False,
            replay_error is None,
            signal_parse_count == 0,
            signal_validation_count == 0,
            synthetic_decision_creation_count == 0,
        ]
    )

    log(
        f"CROSS_RESTART_REPLAY_REJECTION_OK="
        f"{cross_restart_replay_rejection_ok}"
    )

    result(
        "Cross-Restart Exact Replay Rejection Proven",
        cross_restart_replay_rejection_ok,
    )


    # ==================================================================================
    # TEST 9
    # ==================================================================================

    section(f"{VERSION} TEST 9: ZERO-WRITE VERIFICATION")

    result(
        "Exchange Network Writes = 0",
        exchange_network_writes == 0,
    )

    result(
        "Order Submissions = 0",
        order_submissions == 0,
    )

    result(
        "Leverage Mutations = 0",
        leverage_mutations == 0,
    )

    result(
        "Margin Mode Mutations = 0",
        margin_mode_mutations == 0,
    )

    result(
        "Position Mutations = 0",
        position_mutations == 0,
    )

    result(
        "Real Orders Sent = 0",
        real_orders_sent == 0,
    )

    result(
        "Demo Orders Sent = 0",
        demo_orders_sent == 0,
    )

    result(
        "Persistent State Not Modified",
        persistent_state_modified is False,
    )

    result(
        "Telegram Network Updates Consumed = 0",
        telegram_updates_consumed == 0,
    )

    result(
        "Exchange Request Not Attempted",
        exchange_request_attempted is False,
    )


    # ==================================================================================
    # FINAL STATUS
    # ==================================================================================

    hard_zero_write_ok = all(
        [
            exchange_network_writes == 0,
            order_submissions == 0,
            leverage_mutations == 0,
            margin_mode_mutations == 0,
            position_mutations == 0,
            real_orders_sent == 0,
            demo_orders_sent == 0,
            persistent_state_modified is False,
            telegram_updates_consumed == 0,
            exchange_request_attempted is False,
        ]
    )

    final_ok = all(
        [
            cross_restart_replay_rejection_ok,
            hard_zero_write_ok,
            REAL_ORDER_EXECUTION is False,
            DEMO_ORDER_EXECUTION is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
            ORDER_SUBMISSION_ENABLED is False,
            FIRST_REAL_ORDER_ALLOWED is False,
        ]
    )

    test_status = "PASS" if final_ok else "FAIL"


    # ==================================================================================
    # FINAL SUMMARY
    # ==================================================================================

    section(f"{VERSION}: FINAL TEST SUMMARY")

    log(
        "TEST_MODE="
        "CORRECTED_CROSS_RESTART_REPLAY_REJECTION"
    )

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"EXPECTED_UPDATE_ID="
        f"{EXPECTED_UPDATE_ID}"
    )

    log(
        f"CANONICAL_R36A_UPDATE_ID="
        f"{canonical_update_id}"
    )

    log(
        f"UPDATE_SEEN_BEFORE_STARTUP="
        f"{update_seen_before_startup}"
    )

    log(
        f"DUPLICATE_DETECTED="
        f"{duplicate_detected}"
    )

    log(
        f"DUPLICATE_REJECTED_BEFORE_PARSE="
        f"{duplicate_rejected_before_parse}"
    )

    log(
        f"SIGNAL_PARSE_COUNT="
        f"{signal_parse_count}"
    )

    log(
        f"SIGNAL_VALIDATION_COUNT="
        f"{signal_validation_count}"
    )

    log(
        f"SYNTHETIC_DECISION_CREATION_COUNT="
        f"{synthetic_decision_creation_count}"
    )

    log(
        f"CROSS_RESTART_REPLAY_REJECTION_OK="
        f"{cross_restart_replay_rejection_ok}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{exchange_network_writes}"
    )

    log(
        f"ORDER_SUBMISSIONS="
        f"{order_submissions}"
    )

    log(
        f"REAL_ORDERS_SENT="
        f"{real_orders_sent}"
    )

    log(
        f"DEMO_ORDERS_SENT="
        f"{demo_orders_sent}"
    )

    log(
        f"PERSISTENT_STATE_MODIFIED="
        f"{persistent_state_modified}"
    )

    log(
        f"TELEGRAM_UPDATES_CONSUMED="
        f"{telegram_updates_consumed}"
    )

    log(
        f"EXCHANGE_REQUEST_ATTEMPTED="
        f"{exchange_request_attempted}"
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
        f"TEST_STATUS="
        f"{test_status}"
    )

    log(LINE)

    if test_status == "PASS":

        log(
            f"{VERSION}: CORRECTED CROSS-RESTART REPLAY "
            f"REJECTION VERIFIED"
        )

        log(
            f"{VERSION}: EXACT DURABLE R36A UPDATE WAS "
            f"REJECTED BEFORE SIGNAL PARSING"
        )

        log(
            f"{VERSION}: NO REAL ORDER WAS SENT"
        )

    else:

        log(
            f"{VERSION}: TEST FAILED - DO NOT ADVANCE "
            f"TO ANY EXECUTION STAGE"
        )

    log(LINE)


# ======================================================================================
# HEARTBEAT
# ======================================================================================

def heartbeat_loop():

    global heartbeat

    while True:

        time.sleep(30)

        heartbeat += 1

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"TEST_STATUS={test_status} "
            f"UPDATE_SEEN_BEFORE_STARTUP={update_seen_before_startup} "
            f"DUPLICATE_DETECTED={duplicate_detected} "
            f"SIGNAL_PARSE_COUNT={signal_parse_count} "
            f"CROSS_RESTART_REPLAY_REJECTION_OK="
            f"{cross_restart_replay_rejection_ok} "
            f"EXCHANGE_NETWORK_WRITES={exchange_network_writes} "
            f"ORDER_SUBMISSIONS={order_submissions} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )


# ======================================================================================
# ENTRYPOINT
# ======================================================================================

if __name__ == "__main__":

    Thread(
        target=run_health_server,
        daemon=True,
    ).start()

    try:

        run_test()

    except Exception as exc:

        test_status = "FAIL"

        section(f"{VERSION}: UNHANDLED TEST ERROR")

        log(
            f"EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{exc}"
        )

        log(
            "NO EXECUTION SHOULD BE ENABLED."
        )

        log(LINE)

    heartbeat_loop()

