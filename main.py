

# ============================================================
# R36A main.py
# PURPOSE:
# NEW TELEGRAM UPDATE ACCEPTED EXACTLY ONCE AFTER RESTART
#
# SAFETY:
# - NO REAL ORDERS
# - NO DEMO ORDERS
# - NO EXCHANGE NETWORK WRITES
# - NO LEVERAGE MUTATIONS
# - NO MARGIN MODE MUTATIONS
# - NO POSITION MUTATIONS
#
# EXPECTED RESULT:
# - New Telegram update is not present before processing
# - Update passes dedupe gate
# - Signal parsed exactly once
# - Signal validated exactly once
# - Synthetic decision created exactly once
# - Update committed exactly once
# - Decision committed exactly once
# - Deterministic decision hash reproduced
# - Second processing attempt rejected as duplicate
# - No additional parse/validation/decision creation on replay
# - Persistent files unchanged during replay
# ============================================================

import os
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ============================================================
# R36A CONFIGURATION
# ============================================================

R36A_VERSION = "R36A"

PURPOSE = (
    "NEW TELEGRAM UPDATE ACCEPTED EXACTLY ONCE AFTER RESTART "
    "WITH DETERMINISTIC SYNTHETIC DECISION"
)

PORT = int(os.environ.get("PORT", "10000"))

PERSISTENT_DISK_ROOT = "/var/data"
STATE_DIR = os.path.join(
    PERSISTENT_DISK_ROOT,
    "r36a_state"
)

DEDUPE_FILE = os.path.join(
    STATE_DIR,
    "telegram_processed_updates.json"
)

DECISION_FILE = os.path.join(
    STATE_DIR,
    "synthetic_decisions.json"
)

TEST_TELEGRAM_UPDATE_ID = "R36A_SYNTHETIC_UPDATE_000001"

HASH_SERIALIZER = "SORTED_COMPACT_UTF8"


# ============================================================
# STRATEGY BASELINE
# ============================================================

SYMBOL = "BTCUSDT"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

ENTRY_BALANCE_PERCENT = 5.0
PYRAMID_PERCENT = 5.0
MAX_PYRAMID_ADDS = 1

BACKUP_PERCENT = 5.0
MAX_BACKUPS = 3
BACKUP_BUFFER_PERCENT = 0.3

MAX_FUND_EXPOSURE_PERCENT = 35.0

TP1_PERCENT = 20
TP1_TRIGGER_PERCENT = 0.5

TP2_PERCENT = 20
TP2_TRIGGER_PERCENT = 1.0

TP3_PERCENT = 60
TRAILING_DISTANCE_PERCENT = 0.20

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

QTY_STEP = 0.0001
MIN_QTY = 0.0001
PRICE_STEP = 0.1

MAX_QTY_PRECISION = 4
MAX_PRICE_PRECISION = 1


# ============================================================
# SAFETY FIREBREAKS
# ============================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# ============================================================
# COUNTERS
# ============================================================

TELEGRAM_PROCESSING_ATTEMPTS = 0

SIGNAL_PARSE_COUNT = 0
SIGNAL_VALIDATION_COUNT = 0

SYNTHETIC_DECISION_CREATION_COUNT = 0

DURABLE_UPDATE_COMMITS = 0
DURABLE_DECISION_COMMITS = 0

DURABLE_REGISTRY_MUTATIONS = 0

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0

LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0


# ============================================================
# RESULT STATE
# ============================================================

UPDATE_PRESENT_BEFORE_PROCESSING = None
UPDATE_PRESENT_AFTER_FIRST_PROCESSING = None
UPDATE_PRESENT_AFTER_REPLAY = None

NEW_UPDATE_ACCEPTED = None
FIRST_PIPELINE_CONTINUE_RESULT = None

FIRST_DECISION_HASH = None
STORED_DECISION_HASH = None

FIRST_PROCESSING_OK = False

REPLAY_DUPLICATE_DETECTED = False
REPLAY_PIPELINE_CONTINUE_RESULT = None

REPLAY_PRE_PARSE_REJECTION_OK = False
REPLAY_ZERO_MUTATION_OK = False

DEDUPE_FILE_SHA256_AFTER_FIRST = None
DEDUPE_FILE_SHA256_AFTER_REPLAY = None

DECISION_FILE_SHA256_AFTER_FIRST = None
DECISION_FILE_SHA256_AFTER_REPLAY = None

DEDUPE_FILE_UNCHANGED_ON_REPLAY = False
DECISION_FILE_UNCHANGED_ON_REPLAY = False

DETERMINISTIC_DECISION_HASH_OK = False

ZERO_WRITE_FIREBREAK_OK = False

TEST_STATUS = "NOT_RUN"

FAILURES = []


# ============================================================
# TIME / LOGGING
# ============================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True
    )


def separator():
    log("-" * 100)


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = (
            f"{R36A_VERSION} OK\n"
            f"TEST_STATUS={TEST_STATUS}\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(payload))
        )
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def run_health_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    log(
        f"{R36A_VERSION}: "
        f"HEALTH SERVER STARTED ON PORT {PORT}"
    )

    server.serve_forever()


# ============================================================
# FILE HELPERS
# ============================================================

def ensure_state_dir():
    os.makedirs(
        STATE_DIR,
        exist_ok=True
    )


def atomic_write_json(path, data):

    global DURABLE_REGISTRY_MUTATIONS

    temp_path = path + ".tmp"

    serialized = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    encoded = serialized.encode("utf-8")

    with open(
        temp_path,
        "wb"
    ) as f:
        f.write(encoded)
        f.flush()
        os.fsync(f.fileno())

    os.replace(
        temp_path,
        path
    )

    try:
        dir_fd = os.open(
            os.path.dirname(path),
            os.O_DIRECTORY
        )

        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

    except Exception:
        pass

    DURABLE_REGISTRY_MUTATIONS += 1


def load_json_file(path, default):

    if not os.path.exists(path):
        return default

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            value = json.load(f)

            return value

    except Exception:
        return default


def file_sha256(path):

    if not os.path.exists(path):
        return None

    h = hashlib.sha256()

    with open(
        path,
        "rb"
    ) as f:

        while True:

            chunk = f.read(8192)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


# ============================================================
# DETERMINISTIC SERIALIZATION
# ============================================================

def canonical_json_bytes(value):

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def sha256_object(value):

    return hashlib.sha256(
        canonical_json_bytes(value)
    ).hexdigest()


# ============================================================
# REGISTRY HELPERS
# ============================================================

def load_processed_updates():

    value = load_json_file(
        DEDUPE_FILE,
        {}
    )

    if not isinstance(value, dict):
        return {}

    return value


def load_decisions():

    value = load_json_file(
        DECISION_FILE,
        {}
    )

    if not isinstance(value, dict):
        return {}

    return value


def update_already_processed(update_id):

    registry = load_processed_updates()

    return update_id in registry


def commit_processed_update(
    update_id,
    decision_hash
):

    global DURABLE_UPDATE_COMMITS

    registry = load_processed_updates()

    if update_id in registry:
        return False

    registry[update_id] = {
        "update_id": update_id,
        "decision_hash": decision_hash,
        "status": "PROCESSED"
    }

    atomic_write_json(
        DEDUPE_FILE,
        registry
    )

    DURABLE_UPDATE_COMMITS += 1

    return True


def commit_decision(
    decision_hash,
    decision
):

    global DURABLE_DECISION_COMMITS

    registry = load_decisions()

    if decision_hash in registry:

        existing = registry[
            decision_hash
        ]

        if existing == decision:
            return False

        raise RuntimeError(
            "DECISION_HASH_COLLISION_OR_MUTATION"
        )

    registry[decision_hash] = decision

    atomic_write_json(
        DECISION_FILE,
        registry
    )

    DURABLE_DECISION_COMMITS += 1

    return True


# ============================================================
# SYNTHETIC TELEGRAM UPDATE
# ============================================================

def build_test_telegram_update():

    return {
        "update_id": TEST_TELEGRAM_UPDATE_ID,

        "message": {
            "message_id":
                "R36A_SYNTHETIC_MESSAGE_000001",

            "date":
                "2026-08-30T00:00:00+00:00",

            "chat": {
                "id": "R36A_SYNTHETIC_CHAT",
                "type": "private"
            },

            "from": {
                "id":
                    "R36A_SYNTHETIC_SENDER",

                "is_bot":
                    False
            },

            "text":
                "BTCUSDT LONG"
        },

        "synthetic": True
    }


# ============================================================
# SIGNAL PARSER
# ============================================================

def parse_signal(update):

    global SIGNAL_PARSE_COUNT

    SIGNAL_PARSE_COUNT += 1

    message = update.get(
        "message",
        {}
    )

    text = str(
        message.get(
            "text",
            ""
        )
    ).strip().upper()

    tokens = text.split()

    symbol = None
    direction = None

    for token in tokens:

        if token in (
            "BTCUSDT",
            "BTC/USDT",
            "BTC-USDT"
        ):
            symbol = "BTCUSDT"

        if token in (
            "LONG",
            "BUY"
        ):
            direction = "LONG"

        elif token in (
            "SHORT",
            "SELL"
        ):
            direction = "SHORT"

    return {
        "symbol": symbol,
        "direction": direction,
        "raw_text": text
    }


# ============================================================
# SIGNAL VALIDATION
# ============================================================

def validate_signal(signal):

    global SIGNAL_VALIDATION_COUNT

    SIGNAL_VALIDATION_COUNT += 1

    if signal.get("symbol") != SYMBOL:
        return False

    if signal.get(
        "direction"
    ) not in (
        "LONG",
        "SHORT"
    ):
        return False

    return True


# ============================================================
# DETERMINISTIC SYNTHETIC DECISION
# ============================================================

def create_synthetic_decision(
    update_id,
    signal
):

    global SYNTHETIC_DECISION_CREATION_COUNT

    SYNTHETIC_DECISION_CREATION_COUNT += 1

    direction = signal[
        "direction"
    ]

    side = (
        "BUY"
        if direction == "LONG"
        else "SELL"
    )

    decision = {

        "schema":
            "R36A_SYNTHETIC_DECISION_V1",

        "telegram_update_id":
            update_id,

        "symbol":
            SYMBOL,

        "direction":
            direction,

        "side":
            side,

        "margin_mode":
            TARGET_MARGIN_MODE,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "entry_balance_percent":
            ENTRY_BALANCE_PERCENT,

        "pyramid": {
            "percent":
                PYRAMID_PERCENT,

            "max_adds":
                MAX_PYRAMID_ADDS
        },

        "backup": {
            "percent":
                BACKUP_PERCENT,

            "max_backups":
                MAX_BACKUPS,

            "buffer_percent":
                BACKUP_BUFFER_PERCENT
        },

        "max_fund_exposure_percent":
            MAX_FUND_EXPOSURE_PERCENT,

        "tp_structure": {

            "tp1_percent":
                TP1_PERCENT,

            "tp1_trigger_percent":
                TP1_TRIGGER_PERCENT,

            "tp2_percent":
                TP2_PERCENT,

            "tp2_trigger_percent":
                TP2_TRIGGER_PERCENT,

            "tp3_percent":
                TP3_PERCENT,

            "trailing_distance_percent":
                TRAILING_DISTANCE_PERCENT
        },

        "signal_expiry_seconds":
            SIGNAL_EXPIRY_SECONDS,

        "loss_cooldown_seconds":
            LOSS_COOLDOWN_SECONDS,

        "quantity_rules": {

            "qty_step":
                QTY_STEP,

            "min_qty":
                MIN_QTY,

            "qty_precision":
                MAX_QTY_PRECISION
        },

        "price_rules": {

            "price_step":
                PRICE_STEP,

            "price_precision":
                MAX_PRICE_PRECISION
        },

        "execution": {

            "synthetic_transport_only":
                True,

            "exchange_network_write_allowed":
                False,

            "order_submission_allowed":
                False,

            "real_order_execution":
                False,

            "demo_order_execution":
                False
        }
    }

    return decision


# ============================================================
# UPDATE PROCESSING PIPELINE
# ============================================================

def process_telegram_update(update):

    global TELEGRAM_PROCESSING_ATTEMPTS

    global NEW_UPDATE_ACCEPTED

    global FIRST_PIPELINE_CONTINUE_RESULT

    global REPLAY_DUPLICATE_DETECTED

    TELEGRAM_PROCESSING_ATTEMPTS += 1

    update_id = update.get(
        "update_id"
    )

    if not update_id:

        return {
            "continued": False,
            "reason": "MISSING_UPDATE_ID"
        }

    # --------------------------------------------------------
    # DEDUPE GATE MUST EXECUTE BEFORE PARSING
    # --------------------------------------------------------

    if update_already_processed(
        update_id
    ):

        REPLAY_DUPLICATE_DETECTED = True

        return {
            "continued": False,
            "reason": "DUPLICATE_UPDATE"
        }

    NEW_UPDATE_ACCEPTED = True

    # --------------------------------------------------------
    # PARSE
    # --------------------------------------------------------

    signal = parse_signal(
        update
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if not validate_signal(
        signal
    ):

        return {
            "continued": False,
            "reason":
                "SIGNAL_VALIDATION_FAILED"
        }

    # --------------------------------------------------------
    # CREATE SYNTHETIC DECISION
    # --------------------------------------------------------

    decision = create_synthetic_decision(
        update_id,
        signal
    )

    decision_hash = sha256_object(
        decision
    )

    # --------------------------------------------------------
    # COMMIT DECISION FIRST
    # --------------------------------------------------------

    decision_committed = (
        commit_decision(
            decision_hash,
            decision
        )
    )

    if not decision_committed:

        raise RuntimeError(
            "EXPECTED_NEW_DECISION_COMMIT"
        )

    # --------------------------------------------------------
    # COMMIT UPDATE DEDUPE MARKER
    # --------------------------------------------------------

    update_committed = (
        commit_processed_update(
            update_id,
            decision_hash
        )
    )

    if not update_committed:

        raise RuntimeError(
            "EXPECTED_NEW_UPDATE_COMMIT"
        )

    return {
        "continued": True,
        "reason": "ACCEPTED",
        "signal": signal,
        "decision": decision,
        "decision_hash": decision_hash
    }


# ============================================================
# SAFETY CHECK
# ============================================================

def zero_write_firebreak_ok():

    return all([
        REAL_ORDER_EXECUTION is False,

        FIRST_REAL_ORDER_ALLOWED
        is False,

        DEMO_ORDER_EXECUTION
        is False,

        EXCHANGE_MUTATION_TRANSPORT_ENABLED
        is False,

        ORDER_SUBMISSION_ENABLED
        is False,

        LEVERAGE_MUTATION_ENABLED
        is False,

        MARGIN_MODE_MUTATION_ENABLED
        is False,

        POSITION_MUTATION_ENABLED
        is False,

        SYNTHETIC_TRANSPORT_ONLY
        is True,

        EXCHANGE_NETWORK_WRITES == 0,
        ORDER_SUBMISSIONS == 0,

        LEVERAGE_MUTATIONS == 0,
        MARGIN_MODE_MUTATIONS == 0,
        POSITION_MUTATIONS == 0,

        REAL_ORDERS_SENT == 0,
        DEMO_ORDERS_SENT == 0
    ])


# ============================================================
# TEST RUNNER
# ============================================================

def run_tests():

    global UPDATE_PRESENT_BEFORE_PROCESSING
    global UPDATE_PRESENT_AFTER_FIRST_PROCESSING
    global UPDATE_PRESENT_AFTER_REPLAY

    global FIRST_PIPELINE_CONTINUE_RESULT

    global FIRST_DECISION_HASH
    global STORED_DECISION_HASH

    global FIRST_PROCESSING_OK

    global REPLAY_PIPELINE_CONTINUE_RESULT

    global REPLAY_PRE_PARSE_REJECTION_OK
    global REPLAY_ZERO_MUTATION_OK

    global DEDUPE_FILE_SHA256_AFTER_FIRST
    global DEDUPE_FILE_SHA256_AFTER_REPLAY

    global DECISION_FILE_SHA256_AFTER_FIRST
    global DECISION_FILE_SHA256_AFTER_REPLAY

    global DEDUPE_FILE_UNCHANGED_ON_REPLAY
    global DECISION_FILE_UNCHANGED_ON_REPLAY

    global DETERMINISTIC_DECISION_HASH_OK

    global ZERO_WRITE_FIREBREAK_OK

    global TEST_STATUS
    global FAILURES

    ensure_state_dir()

    separator()
    log(
        f"{R36A_VERSION}: MAIN.PY ENTERED"
    )
    separator()

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"HASH_SERIALIZER="
        f"{HASH_SERIALIZER}"
    )

    log(
        f"PERSISTENT_DISK_ROOT="
        f"{PERSISTENT_DISK_ROOT}"
    )

    log(
        f"STATE_DIR={STATE_DIR}"
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
    log(
        "R36A TEST 1: SAFETY FIREBREAK"
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
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED="
        f"{ORDER_SUBMISSION_ENABLED}"
    )

    log(
        f"SYNTHETIC_TRANSPORT_ONLY="
        f"{SYNTHETIC_TRANSPORT_ONLY}"
    )

    # --------------------------------------------------------
    # This is intentionally a NEW update.
    #
    # If an old R36A state from an earlier successful deploy
    # is still present, stop rather than deleting evidence.
    # --------------------------------------------------------

    separator()
    log(
        "R36A TEST 2: NEW UPDATE PRECONDITION"
    )
    separator()

    UPDATE_PRESENT_BEFORE_PROCESSING = (
        update_already_processed(
            TEST_TELEGRAM_UPDATE_ID
        )
    )

    log(
        "UPDATE_PRESENT_BEFORE_PROCESSING="
        f"{UPDATE_PRESENT_BEFORE_PROCESSING}"
    )

    if UPDATE_PRESENT_BEFORE_PROCESSING:

        FAILURES.append(
            "R36A_TEST_UPDATE_ALREADY_EXISTS"
        )

        TEST_STATUS = "FAIL"

        print_final_summary()

        return

    test_update = (
        build_test_telegram_update()
    )

    # --------------------------------------------------------
    # FIRST PROCESSING
    # --------------------------------------------------------

    separator()
    log(
        "R36A TEST 3: FIRST PROCESSING"
    )
    separator()

    parse_before = (
        SIGNAL_PARSE_COUNT
    )

    validation_before = (
        SIGNAL_VALIDATION_COUNT
    )

    decision_creation_before = (
        SYNTHETIC_DECISION_CREATION_COUNT
    )

    update_commits_before = (
        DURABLE_UPDATE_COMMITS
    )

    decision_commits_before = (
        DURABLE_DECISION_COMMITS
    )

    first_result = (
        process_telegram_update(
            test_update
        )
    )

    FIRST_PIPELINE_CONTINUE_RESULT = (
        first_result.get(
            "continued"
        )
    )

    FIRST_DECISION_HASH = (
        first_result.get(
            "decision_hash"
        )
    )

    log(
        f"NEW_UPDATE_ACCEPTED="
        f"{NEW_UPDATE_ACCEPTED}"
    )

    log(
        "FIRST_PIPELINE_CONTINUE_RESULT="
        f"{FIRST_PIPELINE_CONTINUE_RESULT}"
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
        "SYNTHETIC_DECISION_CREATION_COUNT="
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
        f"FIRST_DECISION_HASH="
        f"{FIRST_DECISION_HASH}"
    )

    parse_delta = (
        SIGNAL_PARSE_COUNT
        - parse_before
    )

    validation_delta = (
        SIGNAL_VALIDATION_COUNT
        - validation_before
    )

    decision_creation_delta = (
        SYNTHETIC_DECISION_CREATION_COUNT
        - decision_creation_before
    )

    update_commit_delta = (
        DURABLE_UPDATE_COMMITS
        - update_commits_before
    )

    decision_commit_delta = (
        DURABLE_DECISION_COMMITS
        - decision_commits_before
    )

    FIRST_PROCESSING_OK = all([
        NEW_UPDATE_ACCEPTED is True,

        FIRST_PIPELINE_CONTINUE_RESULT
        is True,

        parse_delta == 1,

        validation_delta == 1,

        decision_creation_delta == 1,

        update_commit_delta == 1,

        decision_commit_delta == 1,

        isinstance(
            FIRST_DECISION_HASH,
            str
        ),

        len(
            FIRST_DECISION_HASH
            or ""
        ) == 64
    ])

    log(
        f"FIRST_PROCESSING_OK="
        f"{FIRST_PROCESSING_OK}"
    )

    # --------------------------------------------------------
    # VERIFY DURABLE STATE
    # --------------------------------------------------------

    separator()
    log(
        "R36A TEST 4: DURABLE STATE VERIFICATION"
    )
    separator()

    UPDATE_PRESENT_AFTER_FIRST_PROCESSING = (
        update_already_processed(
            TEST_TELEGRAM_UPDATE_ID
        )
    )

    processed_registry = (
        load_processed_updates()
    )

    stored_update_record = (
        processed_registry.get(
            TEST_TELEGRAM_UPDATE_ID,
            {}
        )
    )

    STORED_DECISION_HASH = (
        stored_update_record.get(
            "decision_hash"
        )
    )

    decision_registry = (
        load_decisions()
    )

    stored_decision = (
        decision_registry.get(
            STORED_DECISION_HASH
        )
    )

    recomputed_hash = None

    if isinstance(
        stored_decision,
        dict
    ):

        recomputed_hash = (
            sha256_object(
                stored_decision
            )
        )

    DETERMINISTIC_DECISION_HASH_OK = all([
        FIRST_DECISION_HASH
        is not None,

        STORED_DECISION_HASH
        == FIRST_DECISION_HASH,

        recomputed_hash
        == FIRST_DECISION_HASH
    ])

    log(
        "UPDATE_PRESENT_AFTER_FIRST_PROCESSING="
        f"{UPDATE_PRESENT_AFTER_FIRST_PROCESSING}"
    )

    log(
        f"STORED_DECISION_HASH="
        f"{STORED_DECISION_HASH}"
    )

    log(
        f"RECOMPUTED_DECISION_HASH="
        f"{recomputed_hash}"
    )

    log(
        "DETERMINISTIC_DECISION_HASH_OK="
        f"{DETERMINISTIC_DECISION_HASH_OK}"
    )

    DEDUPE_FILE_SHA256_AFTER_FIRST = (
        file_sha256(
            DEDUPE_FILE
        )
    )

    DECISION_FILE_SHA256_AFTER_FIRST = (
        file_sha256(
            DECISION_FILE
        )
    )

    log(
        "DEDUPE_FILE_SHA256_AFTER_FIRST="
        f"{DEDUPE_FILE_SHA256_AFTER_FIRST}"
    )

    log(
        "DECISION_FILE_SHA256_AFTER_FIRST="
        f"{DECISION_FILE_SHA256_AFTER_FIRST}"
    )

    # --------------------------------------------------------
    # SECOND PROCESSING ATTEMPT
    #
    # Must stop BEFORE parse.
    # --------------------------------------------------------

    separator()
    log(
        "R36A TEST 5: SAME-STARTUP REPLAY REJECTION BEFORE PARSE"
    )
    separator()

    parse_before_replay = (
        SIGNAL_PARSE_COUNT
    )

    validation_before_replay = (
        SIGNAL_VALIDATION_COUNT
    )

    decision_before_replay = (
        SYNTHETIC_DECISION_CREATION_COUNT
    )

    update_commits_before_replay = (
        DURABLE_UPDATE_COMMITS
    )

    decision_commits_before_replay = (
        DURABLE_DECISION_COMMITS
    )

    registry_mutations_before_replay = (
        DURABLE_REGISTRY_MUTATIONS
    )

    replay_result = (
        process_telegram_update(
            test_update
        )
    )

    REPLAY_PIPELINE_CONTINUE_RESULT = (
        replay_result.get(
            "continued"
        )
    )

    log(
        "REPLAY_DUPLICATE_DETECTED="
        f"{REPLAY_DUPLICATE_DETECTED}"
    )

    log(
        "REPLAY_PIPELINE_CONTINUE_RESULT="
        f"{REPLAY_PIPELINE_CONTINUE_RESULT}"
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
        "SYNTHETIC_DECISION_CREATION_COUNT="
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

    REPLAY_PRE_PARSE_REJECTION_OK = all([
        REPLAY_DUPLICATE_DETECTED
        is True,

        REPLAY_PIPELINE_CONTINUE_RESULT
        is False,

        SIGNAL_PARSE_COUNT
        == parse_before_replay,

        SIGNAL_VALIDATION_COUNT
        == validation_before_replay,

        SYNTHETIC_DECISION_CREATION_COUNT
        == decision_before_replay
    ])

    REPLAY_ZERO_MUTATION_OK = all([
        DURABLE_UPDATE_COMMITS
        == update_commits_before_replay,

        DURABLE_DECISION_COMMITS
        == decision_commits_before_replay,

        DURABLE_REGISTRY_MUTATIONS
        == registry_mutations_before_replay
    ])

    # --------------------------------------------------------
    # VERIFY FILES DID NOT CHANGE DURING REPLAY
    # --------------------------------------------------------

    separator()
    log(
        "R36A TEST 6: REPLAY FILE IMMUTABILITY"
    )
    separator()

    UPDATE_PRESENT_AFTER_REPLAY = (
        update_already_processed(
            TEST_TELEGRAM_UPDATE_ID
        )
    )

    DEDUPE_FILE_SHA256_AFTER_REPLAY = (
        file_sha256(
            DEDUPE_FILE
        )
    )

    DECISION_FILE_SHA256_AFTER_REPLAY = (
        file_sha256(
            DECISION_FILE
        )
    )

    DEDUPE_FILE_UNCHANGED_ON_REPLAY = (
        DEDUPE_FILE_SHA256_AFTER_FIRST
        ==
        DEDUPE_FILE_SHA256_AFTER_REPLAY
    )

    DECISION_FILE_UNCHANGED_ON_REPLAY = (
        DECISION_FILE_SHA256_AFTER_FIRST
        ==
        DECISION_FILE_SHA256_AFTER_REPLAY
    )

    log(
        "UPDATE_PRESENT_AFTER_REPLAY="
        f"{UPDATE_PRESENT_AFTER_REPLAY}"
    )

    log(
        "DEDUPE_FILE_SHA256_AFTER_REPLAY="
        f"{DEDUPE_FILE_SHA256_AFTER_REPLAY}"
    )

    log(
        "DECISION_FILE_SHA256_AFTER_REPLAY="
        f"{DECISION_FILE_SHA256_AFTER_REPLAY}"
    )

    log(
        "DEDUPE_FILE_UNCHANGED_ON_REPLAY="
        f"{DEDUPE_FILE_UNCHANGED_ON_REPLAY}"
    )

    log(
        "DECISION_FILE_UNCHANGED_ON_REPLAY="
        f"{DECISION_FILE_UNCHANGED_ON_REPLAY}"
    )

    log(
        "REPLAY_PRE_PARSE_REJECTION_OK="
        f"{REPLAY_PRE_PARSE_REJECTION_OK}"
    )

    log(
        "REPLAY_ZERO_MUTATION_OK="
        f"{REPLAY_ZERO_MUTATION_OK}"
    )

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    separator()
    log(
        "R36A TEST 7: ZERO WRITE FIREBREAK"
    )
    separator()

    ZERO_WRITE_FIREBREAK_OK = (
        zero_write_firebreak_ok()
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

    # --------------------------------------------------------
    # FINAL ASSERTIONS
    # --------------------------------------------------------

    FAILURES = []

    if UPDATE_PRESENT_BEFORE_PROCESSING:
        FAILURES.append(
            "UPDATE_ALREADY_PRESENT_BEFORE"
        )

    if not FIRST_PROCESSING_OK:
        FAILURES.append(
            "FIRST_PROCESSING_FAILED"
        )

    if not UPDATE_PRESENT_AFTER_FIRST_PROCESSING:
        FAILURES.append(
            "UPDATE_NOT_DURABLY_COMMITTED"
        )

    if not DETERMINISTIC_DECISION_HASH_OK:
        FAILURES.append(
            "DECISION_HASH_NOT_DETERMINISTIC"
        )

    if not REPLAY_PRE_PARSE_REJECTION_OK:
        FAILURES.append(
            "REPLAY_NOT_REJECTED_BEFORE_PARSE"
        )

    if not REPLAY_ZERO_MUTATION_OK:
        FAILURES.append(
            "REPLAY_MUTATED_REGISTRY"
        )

    if not DEDUPE_FILE_UNCHANGED_ON_REPLAY:
        FAILURES.append(
            "DEDUPE_FILE_CHANGED_ON_REPLAY"
        )

    if not DECISION_FILE_UNCHANGED_ON_REPLAY:
        FAILURES.append(
            "DECISION_FILE_CHANGED_ON_REPLAY"
        )

    if not ZERO_WRITE_FIREBREAK_OK:
        FAILURES.append(
            "WRITE_FIREBREAK_FAILED"
        )

    TEST_STATUS = (
        "PASS"
        if not FAILURES
        else "FAIL"
    )

    print_final_summary()


# ============================================================
# FINAL SUMMARY
# ============================================================

def print_final_summary():

    separator()
    log(
        f"{R36A_VERSION}: FINAL TEST SUMMARY"
    )
    separator()

    checks = [

        (
            "New Update Absent Before Processing",
            UPDATE_PRESENT_BEFORE_PROCESSING
            is False
        ),

        (
            "New Update Accepted",
            NEW_UPDATE_ACCEPTED
            is True
        ),

        (
            "First Pipeline Continued",
            FIRST_PIPELINE_CONTINUE_RESULT
            is True
        ),

        (
            "Signal Parsed Exactly Once",
            SIGNAL_PARSE_COUNT == 1
        ),

        (
            "Signal Validated Exactly Once",
            SIGNAL_VALIDATION_COUNT == 1
        ),

        (
            "Synthetic Decision Created Exactly Once",
            SYNTHETIC_DECISION_CREATION_COUNT
            == 1
        ),

        (
            "Durable Update Commit Exactly Once",
            DURABLE_UPDATE_COMMITS == 1
        ),

        (
            "Durable Decision Commit Exactly Once",
            DURABLE_DECISION_COMMITS == 1
        ),

        (
            "Deterministic Decision Hash",
            DETERMINISTIC_DECISION_HASH_OK
        ),

        (
            "Replay Duplicate Detected",
            REPLAY_DUPLICATE_DETECTED
            is True
        ),

        (
            "Replay Rejected Before Parse",
            REPLAY_PRE_PARSE_REJECTION_OK
        ),

        (
            "Replay Registry Mutation Zero",
            REPLAY_ZERO_MUTATION_OK
        ),

        (
            "Dedupe File Unchanged On Replay",
            DEDUPE_FILE_UNCHANGED_ON_REPLAY
        ),

        (
            "Decision File Unchanged On Replay",
            DECISION_FILE_UNCHANGED_ON_REPLAY
        ),

        (
            "Exchange Network Writes = 0",
            EXCHANGE_NETWORK_WRITES == 0
        ),

        (
            "Order Submissions = 0",
            ORDER_SUBMISSIONS == 0
        ),

        (
            "Leverage Mutations = 0",
            LEVERAGE_MUTATIONS == 0
        ),

        (
            "Margin Mode Mutations = 0",
            MARGIN_MODE_MUTATIONS == 0
        ),

        (
            "Position Mutations = 0",
            POSITION_MUTATIONS == 0
        ),

        (
            "Real Orders Sent = 0",
            REAL_ORDERS_SENT == 0
        ),

        (
            "Demo Orders Sent = 0",
            DEMO_ORDERS_SENT == 0
        ),

        (
            "Zero Write Firebreak",
            ZERO_WRITE_FIREBREAK_OK
        )
    ]

    for name, passed in checks:

        status = (
            "✅ PASS"
            if passed
            else "❌ FAIL"
        )

        print(
            f"{name:<80} {status}",
            flush=True
        )

    separator()

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"DECISION_HASH="
        f"{FIRST_DECISION_HASH}"
    )

    log(
        f"STORED_DECISION_HASH="
        f"{STORED_DECISION_HASH}"
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
        "SYNTHETIC_DECISION_CREATION_COUNT="
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
        f"TEST_STATUS={TEST_STATUS}"
    )

    log(
        "FAILURES="
        + (
            ",".join(FAILURES)
            if FAILURES
            else "NONE"
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
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED="
        f"{ORDER_SUBMISSION_ENABLED}"
    )

    separator()


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        time.sleep(30)

        heartbeat += 1

        log(
            f"{R36A_VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"UPDATE_PRESENT_BEFORE="
            f"{UPDATE_PRESENT_BEFORE_PROCESSING} "
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
            f"DETERMINISTIC_DECISION_HASH_OK="
            f"{DETERMINISTIC_DECISION_HASH_OK} "
            f"REPLAY_DUPLICATE_DETECTED="
            f"{REPLAY_DUPLICATE_DETECTED} "
            f"REPLAY_PRE_PARSE_REJECTION_OK="
            f"{REPLAY_PRE_PARSE_REJECTION_OK} "
            f"DEDUPE_FILE_UNCHANGED_ON_REPLAY="
            f"{DEDUPE_FILE_UNCHANGED_ON_REPLAY} "
            f"DECISION_FILE_UNCHANGED_ON_REPLAY="
            f"{DECISION_FILE_UNCHANGED_ON_REPLAY} "
            f"TEST_STATUS="
            f"{TEST_STATUS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    health_thread.start()

    time.sleep(0.2)

    try:

        run_tests()

    except Exception as exc:

        global TEST_STATUS

        TEST_STATUS = "FAIL"

        FAILURES.append(
            f"UNHANDLED_EXCEPTION:"
            f"{type(exc).__name__}:"
            f"{exc}"
        )

        separator()

        log(
            f"{R36A_VERSION}: "
            f"UNHANDLED EXCEPTION"
        )

        log(
            f"EXCEPTION_CLASS="
            f"{type(exc).__name__}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{exc}"
        )

        print_final_summary()

    heartbeat_loop()


if __name__ == "__main__":
    main()

