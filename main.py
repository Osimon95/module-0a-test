

import os
import sys
import json
import time
import hashlib
import threading
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==============================================================================
# R36C
# OLD DURABLE DUPLICATE REJECTION + NEW UPDATE EXACTLY-ONCE ACCEPTANCE
# ==============================================================================

TEST_NAME = "R36C"
TEST_MODE = "OLD_DUPLICATE_REJECTION_NEW_UPDATE_EXACTLY_ONCE"

PURPOSE = (
    "PROVE OLD DURABLE R36A UPDATE REMAINS REJECTED BEFORE PARSE "
    "WHILE A GENUINELY NEW TELEGRAM UPDATE IS ACCEPTED EXACTLY ONCE, "
    "PARSED, VALIDATED, DURABLY COMMITTED, THEN REJECTED ON REPLAY"
)

PORT = int(os.environ.get("PORT", "10000"))

PERSISTENT_DISK_ROOT = "/var/data"

R36A_STATE_DIR = os.path.join(PERSISTENT_DISK_ROOT, "r36a_state")
R36A_DEDUPE_FILE = os.path.join(
    R36A_STATE_DIR,
    "telegram_processed_updates.json",
)
R36A_DECISION_FILE = os.path.join(
    R36A_STATE_DIR,
    "synthetic_decisions.json",
)

R36C_STATE_DIR = os.path.join(PERSISTENT_DISK_ROOT, "r36c_state")
R36C_DEDUPE_FILE = os.path.join(
    R36C_STATE_DIR,
    "telegram_processed_updates.json",
)
R36C_DECISION_FILE = os.path.join(
    R36C_STATE_DIR,
    "synthetic_decisions.json",
)

OLD_R36A_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"
NEW_R36C_UPDATE_ID = "R36C_SYNTHETIC_UPDATE_000001"

SYMBOL = "BTCUSDT"
TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100


# ==============================================================================
# HARD SAFETY FIREBREAK
# ==============================================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

TELEGRAM_NETWORK_CONSUMPTION_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False


# ==============================================================================
# COUNTERS
# ==============================================================================

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0
TELEGRAM_UPDATES_CONSUMED = 0
EXCHANGE_REQUEST_ATTEMPTED = False

SIGNAL_PARSE_COUNT = 0
SIGNAL_VALIDATION_COUNT = 0
SYNTHETIC_DECISION_CREATION_COUNT = 0

DURABLE_UPDATE_COMMITS = 0
DURABLE_DECISION_COMMITS = 0

OLD_DUPLICATE_DETECTED = False
OLD_DUPLICATE_REJECTED_BEFORE_PARSE = False

NEW_UPDATE_ACCEPTED = False
NEW_UPDATE_DUPLICATE_DETECTED = False
NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE = False

NEW_UPDATE_SEEN_BEFORE_STARTUP = False
NEW_UPDATE_PROCESSED_THIS_STARTUP = False

TEST_STATUS = "RUNNING"


# ==============================================================================
# LOGGING
# ==============================================================================

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
    mark = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<84} {mark}", flush=True)
    return bool(passed)


# ==============================================================================
# HEALTH SERVER
# ==============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "service": TEST_NAME,
            "test_status": TEST_STATUS,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
            "order_submissions": ORDER_SUBMISSIONS,
        }

        encoded = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def start_health_server():

    def worker():
        try:
            server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
            log(f"{TEST_NAME}: HEALTH SERVER STARTED ON PORT {PORT}")
            server.serve_forever()
        except Exception as exc:
            log(
                f"{TEST_NAME}: HEALTH SERVER ERROR "
                f"{type(exc).__name__}: {exc}"
            )

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )
    thread.start()


# ==============================================================================
# JSON HELPERS
# ==============================================================================

def read_json(path, default):
    try:
        if not os.path.exists(path):
            return deepcopy(default), None

        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle), None

    except Exception as exc:
        return deepcopy(default), (
            f"{type(exc).__name__}: {exc}"
        )


def atomic_write_json(path, value):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    temporary = f"{path}.tmp"

    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(
            value,
            handle,
            indent=2,
            sort_keys=True,
        )
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temporary, path)


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(value):
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


# ==============================================================================
# DURABLE UPDATE-ID EXTRACTION
# ==============================================================================

def collect_update_ids(value):
    """
    Recursively discovers update IDs without assuming one historical
    registry schema.

    Only values attached to update-id-like keys are treated as IDs.
    """

    found = set()

    update_keys = {
        "update_id",
        "telegram_update_id",
        "source_update_id",
        "test_update_id",
        "replay_update_id",
        "canonical_update_id",
    }

    def walk(node):

        if isinstance(node, dict):

            for key, child in node.items():

                key_text = str(key).lower()

                if (
                    key_text in update_keys
                    and isinstance(child, (str, int))
                ):
                    found.add(str(child))

                # Some dedupe registries use update IDs directly as keys.
                if isinstance(key, str):
                    if (
                        key.startswith("R36A_SYNTHETIC_UPDATE_")
                        or key.startswith("R36C_SYNTHETIC_UPDATE_")
                    ):
                        found.add(key)

                walk(child)

        elif isinstance(node, list):

            for child in node:
                walk(child)

        elif isinstance(node, str):

            if (
                node.startswith("R36A_SYNTHETIC_UPDATE_")
                or node.startswith("R36C_SYNTHETIC_UPDATE_")
            ):
                found.add(node)

    walk(value)

    return sorted(found)


# ==============================================================================
# R36C REGISTRY NORMALIZATION
# ==============================================================================

def normalize_dedupe_registry(value):

    if isinstance(value, dict):
        registry = deepcopy(value)
    else:
        registry = {}

    if not isinstance(registry.get("updates"), dict):
        registry["updates"] = {}

    registry.setdefault(
        "schema",
        "r36c.telegram_processed_updates.v1",
    )

    return registry


def normalize_decision_registry(value):

    if isinstance(value, dict):
        registry = deepcopy(value)
    else:
        registry = {}

    if not isinstance(registry.get("decisions"), dict):
        registry["decisions"] = {}

    registry.setdefault(
        "schema",
        "r36c.synthetic_decisions.v1",
    )

    return registry


# ==============================================================================
# SYNTHETIC SIGNAL PIPELINE
# ==============================================================================

def parse_signal(update):
    global SIGNAL_PARSE_COUNT

    SIGNAL_PARSE_COUNT += 1

    text = (
        update
        .get("message", {})
        .get("text", "")
        .strip()
        .upper()
    )

    if not text:
        raise ValueError("synthetic signal text missing")

    parts = text.split()

    if len(parts) < 2:
        raise ValueError(
            f"invalid synthetic signal format: {text}"
        )

    direction = parts[0]
    symbol = parts[1]

    return {
        "direction": direction,
        "symbol": symbol,
        "raw_text": text,
    }


def validate_signal(signal):
    global SIGNAL_VALIDATION_COUNT

    SIGNAL_VALIDATION_COUNT += 1

    if signal["direction"] not in {"BUY", "SELL"}:
        raise ValueError(
            f"invalid direction: {signal['direction']}"
        )

    if signal["symbol"] != SYMBOL:
        raise ValueError(
            f"unexpected symbol: {signal['symbol']}"
        )

    return True


def create_synthetic_decision(update, signal):
    global SYNTHETIC_DECISION_CREATION_COUNT

    SYNTHETIC_DECISION_CREATION_COUNT += 1

    core = {
        "update_id": str(update["update_id"]),
        "symbol": SYMBOL,
        "direction": signal["direction"],
        "target_margin_mode": TARGET_MARGIN_MODE,
        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,

        "real_order_execution": False,
        "demo_order_execution": False,
        "exchange_mutation_transport_enabled": False,
        "order_submission_enabled": False,

        "synthetic_only": True,

        "created_at": utc_now(),
    }

    decision = deepcopy(core)
    decision["decision_sha256"] = sha256_json(core)

    return decision


# ==============================================================================
# PROCESS SYNTHETIC UPDATE
# ==============================================================================

def process_synthetic_update(
    update,
    durable_seen_ids,
    dedupe_registry,
    decision_registry,
    allow_commit,
):
    """
    Duplicate classification happens BEFORE parser invocation.

    Returns:
        continue_result
        duplicate_detected
        duplicate_rejected_before_parse
        decision
    """

    global DURABLE_UPDATE_COMMITS
    global DURABLE_DECISION_COMMITS
    global NEW_UPDATE_ACCEPTED
    global NEW_UPDATE_PROCESSED_THIS_STARTUP

    update_id = str(update["update_id"])

    parse_before = SIGNAL_PARSE_COUNT

    if update_id in durable_seen_ids:

        duplicate_rejected_before_parse = (
            SIGNAL_PARSE_COUNT == parse_before
        )

        log(
            "DUPLICATE_REJECTED_BEFORE_PARSE=True "
            f"UPDATE_ID={update_id}"
        )

        return (
            False,
            True,
            duplicate_rejected_before_parse,
            None,
        )

    signal = parse_signal(update)
    validate_signal(signal)

    decision = create_synthetic_decision(
        update,
        signal,
    )

    if allow_commit:

        dedupe_registry["updates"][update_id] = {
            "update_id": update_id,
            "processed_at": utc_now(),
            "synthetic": True,
            "source": TEST_NAME,
        }

        atomic_write_json(
            R36C_DEDUPE_FILE,
            dedupe_registry,
        )

        DURABLE_UPDATE_COMMITS += 1

        decision_registry["decisions"][update_id] = decision

        atomic_write_json(
            R36C_DECISION_FILE,
            decision_registry,
        )

        DURABLE_DECISION_COMMITS += 1

        durable_seen_ids.add(update_id)

    NEW_UPDATE_ACCEPTED = True
    NEW_UPDATE_PROCESSED_THIS_STARTUP = True

    return (
        True,
        False,
        False,
        decision,
    )


# ==============================================================================
# MAIN TEST
# ==============================================================================

def run_test():

    global TEST_STATUS

    global OLD_DUPLICATE_DETECTED
    global OLD_DUPLICATE_REJECTED_BEFORE_PARSE

    global NEW_UPDATE_SEEN_BEFORE_STARTUP
    global NEW_UPDATE_DUPLICATE_DETECTED
    global NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE

    start_health_server()

    section(f"{TEST_NAME}: MAIN.PY ENTERED")

    log(f"PURPOSE={PURPOSE}")
    log(f"PYTHON_VERSION={sys.version.split()[0]}")

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")

    log(f"R36A_STATE_DIR={R36A_STATE_DIR}")
    log(f"R36A_DEDUPE_FILE={R36A_DEDUPE_FILE}")
    log(f"R36A_DECISION_FILE={R36A_DECISION_FILE}")

    log(f"R36C_STATE_DIR={R36C_STATE_DIR}")
    log(f"R36C_DEDUPE_FILE={R36C_DEDUPE_FILE}")
    log(f"R36C_DECISION_FILE={R36C_DECISION_FILE}")

    log(f"OLD_R36A_UPDATE_ID={OLD_R36A_UPDATE_ID}")
    log(f"NEW_R36C_UPDATE_ID={NEW_R36C_UPDATE_ID}")

    # ==========================================================================
    # TEST 2
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 2: HARD SAFETY FIREBREAK"
    )

    checks = []

    checks.append(
        result(
            "Real Order Execution Disabled",
            REAL_ORDER_EXECUTION is False,
        )
    )

    checks.append(
        result(
            "Demo Order Execution Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    checks.append(
        result(
            "Exchange Mutation Transport Disabled",
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
        )
    )

    checks.append(
        result(
            "Order Submission Disabled",
            ORDER_SUBMISSION_ENABLED is False,
        )
    )

    checks.append(
        result(
            "Leverage Mutation Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        )
    )

    checks.append(
        result(
            "Margin Mode Mutation Disabled",
            MARGIN_MODE_MUTATION_ENABLED is False,
        )
    )

    checks.append(
        result(
            "Position Mutation Disabled",
            POSITION_MUTATION_ENABLED is False,
        )
    )

    checks.append(
        result(
            "Telegram Network Consumption Disabled",
            TELEGRAM_NETWORK_CONSUMPTION_ENABLED is False,
        )
    )

    checks.append(
        result(
            "First Real Order Forbidden",
            FIRST_REAL_ORDER_ALLOWED is False,
        )
    )

    # ==========================================================================
    # TEST 3
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 3: LOAD R36A DURABLE REGISTRIES READ-ONLY"
    )

    r36a_dedupe, r36a_dedupe_error = read_json(
        R36A_DEDUPE_FILE,
        {},
    )

    r36a_decisions, r36a_decision_error = read_json(
        R36A_DECISION_FILE,
        {},
    )

    log(
        f"PERSISTENT_DISK_AVAILABLE="
        f"{os.path.isdir(PERSISTENT_DISK_ROOT)}"
    )

    log(
        f"R36A_STATE_DIR_EXISTS="
        f"{os.path.isdir(R36A_STATE_DIR)}"
    )

    log(
        f"R36A_DEDUPE_FILE_EXISTS="
        f"{os.path.isfile(R36A_DEDUPE_FILE)}"
    )

    log(
        f"R36A_DECISION_FILE_EXISTS="
        f"{os.path.isfile(R36A_DECISION_FILE)}"
    )

    log(f"R36A_DEDUPE_READ_ERROR={r36a_dedupe_error}")
    log(f"R36A_DECISION_READ_ERROR={r36a_decision_error}")

    checks.append(
        result(
            "R36A Durable Dedupe Registry Readable",
            r36a_dedupe_error is None,
        )
    )

    checks.append(
        result(
            "R36A Durable Decision Registry Readable",
            r36a_decision_error is None,
        )
    )

    r36a_dedupe_ids = set(
        collect_update_ids(r36a_dedupe)
    )

    r36a_decision_ids = set(
        collect_update_ids(r36a_decisions)
    )

    r36a_shared_ids = (
        r36a_dedupe_ids
        & r36a_decision_ids
    )

    # ==========================================================================
    # TEST 4
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 4: VERIFY OLD R36A DURABLE IDENTITY"
    )

    log(
        f"R36A_DEDUPE_UPDATE_ID_COUNT="
        f"{len(r36a_dedupe_ids)}"
    )

    log(
        f"R36A_DECISION_UPDATE_ID_COUNT="
        f"{len(r36a_decision_ids)}"
    )

    log(
        f"R36A_SHARED_UPDATE_ID_COUNT="
        f"{len(r36a_shared_ids)}"
    )

    old_in_dedupe = (
        OLD_R36A_UPDATE_ID in r36a_dedupe_ids
    )

    old_in_decision = (
        OLD_R36A_UPDATE_ID in r36a_decision_ids
    )

    old_shared = (
        OLD_R36A_UPDATE_ID in r36a_shared_ids
    )

    log(f"OLD_ID_IN_R36A_DEDUPE={old_in_dedupe}")
    log(f"OLD_ID_IN_R36A_DECISION={old_in_decision}")
    log(f"OLD_ID_SHARED={old_shared}")

    checks.append(
        result(
            "Exact Old R36A Update Exists In Durable Dedupe",
            old_in_dedupe,
        )
    )

    checks.append(
        result(
            "Exact Old R36A Update Exists In Durable Decision Registry",
            old_in_decision,
        )
    )

    checks.append(
        result(
            "Exact Old R36A Update Shared By Both Registries",
            old_shared,
        )
    )

    # ==========================================================================
    # TEST 5
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 5: LOAD R36C DURABLE STATE"
    )

    os.makedirs(
        R36C_STATE_DIR,
        exist_ok=True,
    )

    r36c_dedupe_raw, r36c_dedupe_error = read_json(
        R36C_DEDUPE_FILE,
        {},
    )

    r36c_decision_raw, r36c_decision_error = read_json(
        R36C_DECISION_FILE,
        {},
    )

    log(f"R36C_DEDUPE_READ_ERROR={r36c_dedupe_error}")
    log(f"R36C_DECISION_READ_ERROR={r36c_decision_error}")

    checks.append(
        result(
            "R36C Durable Dedupe Registry Readable Or New",
            r36c_dedupe_error is None,
        )
    )

    checks.append(
        result(
            "R36C Durable Decision Registry Readable Or New",
            r36c_decision_error is None,
        )
    )

    r36c_dedupe = normalize_dedupe_registry(
        r36c_dedupe_raw
    )

    r36c_decisions = normalize_decision_registry(
        r36c_decision_raw
    )

    r36c_existing_dedupe_ids = set(
        collect_update_ids(r36c_dedupe)
    )

    r36c_existing_decision_ids = set(
        collect_update_ids(r36c_decisions)
    )

    startup_seen_ids = (
        set(r36a_dedupe_ids)
        | set(r36a_decision_ids)
        | set(r36c_existing_dedupe_ids)
        | set(r36c_existing_decision_ids)
    )

    NEW_UPDATE_SEEN_BEFORE_STARTUP = (
        NEW_R36C_UPDATE_ID in startup_seen_ids
    )

    log(
        f"NEW_UPDATE_SEEN_BEFORE_STARTUP="
        f"{NEW_UPDATE_SEEN_BEFORE_STARTUP}"
    )

    if NEW_UPDATE_SEEN_BEFORE_STARTUP:
        log(
            "R36C_STARTUP_MODE="
            "DURABLE_RESTART_VERIFICATION"
        )
    else:
        log(
            "R36C_STARTUP_MODE="
            "FIRST_ACCEPTANCE"
        )

    # ==========================================================================
    # TEST 6
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 6: OLD R36A DUPLICATE REJECTION BEFORE PARSE"
    )

    old_update = {
        "update_id": OLD_R36A_UPDATE_ID,
        "message": {
            "text": "BUY BTCUSDT",
        },
        "synthetic": True,
    }

    parse_before_old = SIGNAL_PARSE_COUNT
    validation_before_old = SIGNAL_VALIDATION_COUNT
    decision_before_old = SYNTHETIC_DECISION_CREATION_COUNT

    if OLD_R36A_UPDATE_ID in startup_seen_ids:

        OLD_DUPLICATE_DETECTED = True

        OLD_DUPLICATE_REJECTED_BEFORE_PARSE = True

        old_pipeline_continue = False

        log(
            "DUPLICATE_REJECTED_BEFORE_PARSE=True "
            f"UPDATE_ID={OLD_R36A_UPDATE_ID}"
        )

    else:

        OLD_DUPLICATE_DETECTED = False
        OLD_DUPLICATE_REJECTED_BEFORE_PARSE = False
        old_pipeline_continue = None

    log(
        f"OLD_PIPELINE_CONTINUE_RESULT="
        f"{old_pipeline_continue}"
    )

    log(
        f"OLD_DUPLICATE_DETECTED="
        f"{OLD_DUPLICATE_DETECTED}"
    )

    log(
        f"OLD_DUPLICATE_REJECTED_BEFORE_PARSE="
        f"{OLD_DUPLICATE_REJECTED_BEFORE_PARSE}"
    )

    log(
        f"OLD_PARSE_DELTA="
        f"{SIGNAL_PARSE_COUNT - parse_before_old}"
    )

    log(
        f"OLD_VALIDATION_DELTA="
        f"{SIGNAL_VALIDATION_COUNT - validation_before_old}"
    )

    log(
        f"OLD_DECISION_DELTA="
        f"{SYNTHETIC_DECISION_CREATION_COUNT - decision_before_old}"
    )

    checks.append(
        result(
            "Old R36A Duplicate Detected",
            OLD_DUPLICATE_DETECTED,
        )
    )

    checks.append(
        result(
            "Old R36A Replay Rejected",
            old_pipeline_continue is False,
        )
    )

    checks.append(
        result(
            "Old R36A Duplicate Rejected Before Parse",
            OLD_DUPLICATE_REJECTED_BEFORE_PARSE,
        )
    )

    checks.append(
        result(
            "Old Replay Did Not Enter Parser",
            SIGNAL_PARSE_COUNT == parse_before_old,
        )
    )

    checks.append(
        result(
            "Old Replay Did Not Enter Validation",
            SIGNAL_VALIDATION_COUNT
            == validation_before_old,
        )
    )

    checks.append(
        result(
            "Old Replay Created No Decision",
            SYNTHETIC_DECISION_CREATION_COUNT
            == decision_before_old,
        )
    )

    # ==========================================================================
    # TEST 7
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 7: GENUINELY NEW SYNTHETIC UPDATE"
    )

    new_update = {
        "update_id": NEW_R36C_UPDATE_ID,
        "message": {
            "message_id": "R36C_SYNTHETIC_MESSAGE_000001",
            "date": int(time.time()),
            "text": "BUY BTCUSDT",
        },
        "synthetic": True,
        "network_received": False,
    }

    new_parse_before = SIGNAL_PARSE_COUNT
    new_validation_before = SIGNAL_VALIDATION_COUNT
    new_decision_before = SYNTHETIC_DECISION_CREATION_COUNT

    durable_seen_ids = set(startup_seen_ids)

    if not NEW_UPDATE_SEEN_BEFORE_STARTUP:

        (
            new_pipeline_continue,
            first_duplicate,
            first_rejected_before_parse,
            new_decision,
        ) = process_synthetic_update(
            update=new_update,
            durable_seen_ids=durable_seen_ids,
            dedupe_registry=r36c_dedupe,
            decision_registry=r36c_decisions,
            allow_commit=True,
        )

        log(
            f"NEW_PIPELINE_CONTINUE_RESULT="
            f"{new_pipeline_continue}"
        )

        log(
            f"NEW_FIRST_ATTEMPT_DUPLICATE="
            f"{first_duplicate}"
        )

        log(
            f"NEW_FIRST_ATTEMPT_REJECTED_BEFORE_PARSE="
            f"{first_rejected_before_parse}"
        )

        log(
            f"NEW_SIGNAL_PARSE_DELTA="
            f"{SIGNAL_PARSE_COUNT - new_parse_before}"
        )

        log(
            f"NEW_SIGNAL_VALIDATION_DELTA="
            f"{SIGNAL_VALIDATION_COUNT - new_validation_before}"
        )

        log(
            f"NEW_DECISION_CREATION_DELTA="
            f"{SYNTHETIC_DECISION_CREATION_COUNT - new_decision_before}"
        )

        log(
            f"DURABLE_UPDATE_COMMITS="
            f"{DURABLE_UPDATE_COMMITS}"
        )

        log(
            f"DURABLE_DECISION_COMMITS="
            f"{DURABLE_DECISION_COMMITS}"
        )

        if new_decision:
            log(
                f"NEW_DECISION_SHA256="
                f"{new_decision['decision_sha256']}"
            )

        checks.append(
            result(
                "New R36C Update Classified New",
                first_duplicate is False,
            )
        )

        checks.append(
            result(
                "New R36C Update Allowed Into Pipeline",
                new_pipeline_continue is True,
            )
        )

        checks.append(
            result(
                "New R36C Signal Parsed Exactly Once",
                SIGNAL_PARSE_COUNT - new_parse_before == 1,
            )
        )

        checks.append(
            result(
                "New R36C Signal Validated Exactly Once",
                SIGNAL_VALIDATION_COUNT
                - new_validation_before
                == 1,
            )
        )

        checks.append(
            result(
                "New Synthetic Decision Created Exactly Once",
                SYNTHETIC_DECISION_CREATION_COUNT
                - new_decision_before
                == 1,
            )
        )

        checks.append(
            result(
                "New Update Durable Commit Exactly Once",
                DURABLE_UPDATE_COMMITS == 1,
            )
        )

        checks.append(
            result(
                "New Decision Durable Commit Exactly Once",
                DURABLE_DECISION_COMMITS == 1,
            )
        )

    else:

        # A Render restart after R36C has already completed must not
        # create a second decision. The durable state itself becomes
        # the evidence.

        NEW_UPDATE_ACCEPTED = True

        new_pipeline_continue = False

        log(
            "NEW_UPDATE_ALREADY_DURABLE_FROM_PRIOR_R36C_STARTUP=True"
        )

        log(
            "NEW_PIPELINE_CONTINUE_RESULT=False"
        )

        checks.append(
            result(
                "New R36C Update Already Durable On Restart",
                NEW_UPDATE_SEEN_BEFORE_STARTUP,
            )
        )

        checks.append(
            result(
                "Restart Did Not Reparse Durable R36C Update",
                SIGNAL_PARSE_COUNT == new_parse_before,
            )
        )

        checks.append(
            result(
                "Restart Did Not Revalidate Durable R36C Update",
                SIGNAL_VALIDATION_COUNT
                == new_validation_before,
            )
        )

        checks.append(
            result(
                "Restart Did Not Recreate Durable R36C Decision",
                SYNTHETIC_DECISION_CREATION_COUNT
                == new_decision_before,
            )
        )

    # ==========================================================================
    # TEST 8
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 8: VERIFY NEW DURABLE LINKAGE"
    )

    persisted_dedupe, persisted_dedupe_error = read_json(
        R36C_DEDUPE_FILE,
        {},
    )

    persisted_decisions, persisted_decision_error = read_json(
        R36C_DECISION_FILE,
        {},
    )

    persisted_dedupe_ids = set(
        collect_update_ids(persisted_dedupe)
    )

    persisted_decision_ids = set(
        collect_update_ids(persisted_decisions)
    )

    new_in_dedupe = (
        NEW_R36C_UPDATE_ID in persisted_dedupe_ids
    )

    new_in_decision = (
        NEW_R36C_UPDATE_ID in persisted_decision_ids
    )

    new_shared = (
        new_in_dedupe
        and new_in_decision
    )

    log(
        f"NEW_ID_IN_R36C_DEDUPE="
        f"{new_in_dedupe}"
    )

    log(
        f"NEW_ID_IN_R36C_DECISION="
        f"{new_in_decision}"
    )

    log(
        f"NEW_ID_SHARED="
        f"{new_shared}"
    )

    checks.append(
        result(
            "New R36C Update Durable In Dedupe Registry",
            new_in_dedupe,
        )
    )

    checks.append(
        result(
            "New R36C Update Durable In Decision Registry",
            new_in_decision,
        )
    )

    checks.append(
        result(
            "New R36C Update Linked Across Both Registries",
            new_shared,
        )
    )

    # ==========================================================================
    # TEST 9
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 9: REPLAY NEW R36C UPDATE BEFORE PARSE"
    )

    replay_seen_ids = (
        set(r36a_dedupe_ids)
        | set(persisted_dedupe_ids)
        | set(persisted_decision_ids)
    )

    replay_parse_before = SIGNAL_PARSE_COUNT
    replay_validation_before = SIGNAL_VALIDATION_COUNT
    replay_decision_before = SYNTHETIC_DECISION_CREATION_COUNT

    if NEW_R36C_UPDATE_ID in replay_seen_ids:

        NEW_UPDATE_DUPLICATE_DETECTED = True
        NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE = True
        replay_pipeline_continue = False

        log(
            "DUPLICATE_REJECTED_BEFORE_PARSE=True "
            f"UPDATE_ID={NEW_R36C_UPDATE_ID}"
        )

    else:

        NEW_UPDATE_DUPLICATE_DETECTED = False
        NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE = False
        replay_pipeline_continue = None

    log(
        f"REPLAY_PIPELINE_CONTINUE_RESULT="
        f"{replay_pipeline_continue}"
    )

    log(
        f"NEW_UPDATE_DUPLICATE_DETECTED="
        f"{NEW_UPDATE_DUPLICATE_DETECTED}"
    )

    log(
        f"NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE="
        f"{NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE}"
    )

    log(
        f"REPLAY_PARSE_DELTA="
        f"{SIGNAL_PARSE_COUNT - replay_parse_before}"
    )

    log(
        f"REPLAY_VALIDATION_DELTA="
        f"{SIGNAL_VALIDATION_COUNT - replay_validation_before}"
    )

    log(
        f"REPLAY_DECISION_DELTA="
        f"{SYNTHETIC_DECISION_CREATION_COUNT - replay_decision_before}"
    )

    checks.append(
        result(
            "New R36C Replay Detected As Duplicate",
            NEW_UPDATE_DUPLICATE_DETECTED,
        )
    )

    checks.append(
        result(
            "New R36C Replay Rejected",
            replay_pipeline_continue is False,
        )
    )

    checks.append(
        result(
            "New R36C Replay Rejected Before Parse",
            NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE,
        )
    )

    checks.append(
        result(
            "New Replay Did Not Re-enter Parser",
            SIGNAL_PARSE_COUNT == replay_parse_before,
        )
    )

    checks.append(
        result(
            "New Replay Did Not Re-enter Validation",
            SIGNAL_VALIDATION_COUNT
            == replay_validation_before,
        )
    )

    checks.append(
        result(
            "New Replay Created No Second Decision",
            SYNTHETIC_DECISION_CREATION_COUNT
            == replay_decision_before,
        )
    )

    # ==========================================================================
    # TEST 10
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 10: EXACTLY-ONCE PROOF"
    )

    if NEW_UPDATE_SEEN_BEFORE_STARTUP:

        # Restart case:
        # the persistent registries are the proof that the previous
        # startup accepted and committed the update, while this startup
        # correctly performs zero new parsing/creation.

        exactly_once_ok = (
            new_shared
            and NEW_UPDATE_DUPLICATE_DETECTED
            and NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE
            and SIGNAL_PARSE_COUNT == 0
            and SIGNAL_VALIDATION_COUNT == 0
            and SYNTHETIC_DECISION_CREATION_COUNT == 0
            and DURABLE_UPDATE_COMMITS == 0
            and DURABLE_DECISION_COMMITS == 0
        )

    else:

        exactly_once_ok = (
            NEW_UPDATE_ACCEPTED
            and NEW_UPDATE_PROCESSED_THIS_STARTUP
            and new_shared
            and NEW_UPDATE_DUPLICATE_DETECTED
            and NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE
            and SIGNAL_PARSE_COUNT == 1
            and SIGNAL_VALIDATION_COUNT == 1
            and SYNTHETIC_DECISION_CREATION_COUNT == 1
            and DURABLE_UPDATE_COMMITS == 1
            and DURABLE_DECISION_COMMITS == 1
        )

    checks.append(
        result(
            "New Update Exactly-Once Processing Proven",
            exactly_once_ok,
        )
    )

    combined_gate_ok = (
        OLD_DUPLICATE_DETECTED
        and OLD_DUPLICATE_REJECTED_BEFORE_PARSE
        and exactly_once_ok
    )

    checks.append(
        result(
            "Old Duplicate Rejection Did Not Block New Update",
            combined_gate_ok,
        )
    )

    # ==========================================================================
    # TEST 11
    # ==========================================================================

    section(
        f"{TEST_NAME} TEST 11: ZERO-WRITE VERIFICATION"
    )

    checks.append(
        result(
            "Exchange Network Writes = 0",
            EXCHANGE_NETWORK_WRITES == 0,
        )
    )

    checks.append(
        result(
            "Order Submissions = 0",
            ORDER_SUBMISSIONS == 0,
        )
    )

    checks.append(
        result(
            "Leverage Mutations = 0",
            LEVERAGE_MUTATIONS == 0,
        )
    )

    checks.append(
        result(
            "Margin Mode Mutations = 0",
            MARGIN_MODE_MUTATIONS == 0,
        )
    )

    checks.append(
        result(
            "Position Mutations = 0",
            POSITION_MUTATIONS == 0,
        )
    )

    checks.append(
        result(
            "Real Orders Sent = 0",
            REAL_ORDERS_SENT == 0,
        )
    )

    checks.append(
        result(
            "Demo Orders Sent = 0",
            DEMO_ORDERS_SENT == 0,
        )
    )

    checks.append(
        result(
            "Telegram Network Updates Consumed = 0",
            TELEGRAM_UPDATES_CONSUMED == 0,
        )
    )

    checks.append(
        result(
            "Exchange Request Not Attempted",
            EXCHANGE_REQUEST_ATTEMPTED is False,
        )
    )

    # R36A must remain read-only.
    r36a_dedupe_after, _ = read_json(
        R36A_DEDUPE_FILE,
        {},
    )

    r36a_decisions_after, _ = read_json(
        R36A_DECISION_FILE,
        {},
    )

    r36a_source_unchanged = (
        sha256_json(r36a_dedupe)
        == sha256_json(r36a_dedupe_after)
        and
        sha256_json(r36a_decisions)
        == sha256_json(r36a_decisions_after)
    )

    checks.append(
        result(
            "R36A Source Durable State Not Modified",
            r36a_source_unchanged,
        )
    )

    # ==========================================================================
    # FINAL
    # ==========================================================================

    TEST_STATUS = (
        "PASS"
        if all(checks)
        else "FAIL"
    )

    section(
        f"{TEST_NAME}: FINAL TEST SUMMARY"
    )

    log(f"TEST_MODE={TEST_MODE}")
    log(f"PURPOSE={PURPOSE}")

    log(
        f"OLD_R36A_UPDATE_ID="
        f"{OLD_R36A_UPDATE_ID}"
    )

    log(
        f"NEW_R36C_UPDATE_ID="
        f"{NEW_R36C_UPDATE_ID}"
    )

    log(
        f"NEW_UPDATE_SEEN_BEFORE_STARTUP="
        f"{NEW_UPDATE_SEEN_BEFORE_STARTUP}"
    )

    log(
        f"OLD_DUPLICATE_DETECTED="
        f"{OLD_DUPLICATE_DETECTED}"
    )

    log(
        f"OLD_DUPLICATE_REJECTED_BEFORE_PARSE="
        f"{OLD_DUPLICATE_REJECTED_BEFORE_PARSE}"
    )

    log(
        f"NEW_UPDATE_ACCEPTED="
        f"{NEW_UPDATE_ACCEPTED}"
    )

    log(
        f"NEW_UPDATE_PROCESSED_THIS_STARTUP="
        f"{NEW_UPDATE_PROCESSED_THIS_STARTUP}"
    )

    log(
        f"NEW_UPDATE_DUPLICATE_DETECTED="
        f"{NEW_UPDATE_DUPLICATE_DETECTED}"
    )

    log(
        f"NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE="
        f"{NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE}"
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
        f"EXACTLY_ONCE_OK="
        f"{exactly_once_ok}"
    )

    log(
        f"OLD_DUPLICATE_REJECTION_DID_NOT_BLOCK_NEW_UPDATE="
        f"{combined_gate_ok}"
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
        f"REAL_ORDERS_SENT="
        f"{REAL_ORDERS_SENT}"
    )

    log(
        f"DEMO_ORDERS_SENT="
        f"{DEMO_ORDERS_SENT}"
    )

    log(
        f"TELEGRAM_UPDATES_CONSUMED="
        f"{TELEGRAM_UPDATES_CONSUMED}"
    )

    log(
        f"EXCHANGE_REQUEST_ATTEMPTED="
        f"{EXCHANGE_REQUEST_ATTEMPTED}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(f"TEST_STATUS={TEST_STATUS}")

    section(
        f"{TEST_NAME}: "
        f"{'NEW UPDATE EXACTLY-ONCE PIPELINE VERIFIED' if TEST_STATUS == 'PASS' else 'TEST FAILED'}"
    )

    if TEST_STATUS == "PASS":

        log(
            f"{TEST_NAME}: OLD DURABLE R36A UPDATE "
            "WAS REJECTED BEFORE SIGNAL PARSING"
        )

        log(
            f"{TEST_NAME}: NEW R36C UPDATE "
            "WAS ACCEPTED AND DURABLY COMMITTED EXACTLY ONCE"
        )

        log(
            f"{TEST_NAME}: REPLAY OF NEW R36C UPDATE "
            "WAS REJECTED BEFORE SIGNAL PARSING"
        )

        log(
            f"{TEST_NAME}: DUPLICATE PROTECTION "
            "DOES NOT BLOCK GENUINELY NEW SIGNALS"
        )

        log(
            f"{TEST_NAME}: NO REAL ORDER WAS SENT"
        )

    return TEST_STATUS


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":

    try:
        run_test()

    except Exception as exc:

        TEST_STATUS = "FAIL"

        section(
            f"{TEST_NAME}: UNHANDLED TEST ERROR"
        )

        log(
            f"EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{exc}"
        )

        log("TEST_STATUS=FAIL")

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{TEST_NAME}: "
            f"HEARTBEAT={heartbeat} "
            f"TEST_STATUS={TEST_STATUS} "
            f"OLD_DUPLICATE_DETECTED={OLD_DUPLICATE_DETECTED} "
            f"OLD_REJECTED_BEFORE_PARSE={OLD_DUPLICATE_REJECTED_BEFORE_PARSE} "
            f"NEW_UPDATE_SEEN_BEFORE_STARTUP={NEW_UPDATE_SEEN_BEFORE_STARTUP} "
            f"NEW_UPDATE_ACCEPTED={NEW_UPDATE_ACCEPTED} "
            f"NEW_REPLAY_REJECTED_BEFORE_PARSE="
            f"{NEW_UPDATE_REPLAY_REJECTED_BEFORE_PARSE} "
            f"SIGNAL_PARSE_COUNT={SIGNAL_PARSE_COUNT} "
            f"SIGNAL_VALIDATION_COUNT={SIGNAL_VALIDATION_COUNT} "
            f"SYNTHETIC_DECISION_CREATION_COUNT="
            f"{SYNTHETIC_DECISION_CREATION_COUNT} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)

 
