

# ======================================================================================
# R35Y main.py
# PURPOSE:
# NEW TELEGRAM UPDATE -> PRE-PARSE DURABLE GATE -> PARSE -> VALIDATE ->
# EXACTLY ONE DETERMINISTIC SYNTHETIC DECISION -> DURABLE LOCAL COMMIT
#
# SAFETY:
# - NO REAL ORDER EXECUTION
# - NO DEMO ORDER EXECUTION
# - NO EXCHANGE NETWORK WRITES
# - NO LEVERAGE MUTATIONS
# - NO MARGIN MODE MUTATIONS
# - NO POSITION MUTATIONS
#
# R35Y IS THE POSITIVE-ACCEPTANCE COMPLEMENT TO R35X.
#
# EXPECTED FIRST CLEAN RUN:
#   NEW UPDATE ABSENT BEFORE STARTUP
#   DUPLICATE_GATE_RESULT=ACCEPT
#   SIGNAL_PARSE_COUNT=1
#   SIGNAL_VALIDATION_COUNT=1
#   SYNTHETIC_DECISION_CREATION_COUNT=1
#   DURABLE_UPDATE_COMMITS=1
#   DURABLE_DECISION_COMMITS=1
#   TEST_STATUS=PASS
#
# IMPORTANT:
#   R35Y intentionally creates durable state for R35Z.
#   R35Z will replay the same R35Y update after restart and prove rejection.
# ======================================================================================

import os
import sys
import json
import time
import hashlib
import tempfile
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ======================================================================================
# R35Y PART 1/4
# GLOBAL CONFIGURATION + HARD SAFETY FIREBREAK
# ======================================================================================

VERSION = "R35Y"

PURPOSE = (
    "NEW TELEGRAM UPDATE ACCEPTANCE THROUGH PRE-PARSE DURABLE GATE "
    "WITH EXACTLY-ONCE SYNTHETIC DECISION COMMIT"
)

PORT = int(os.environ.get("PORT", "10000"))

PERSISTENT_DISK_ROOT = os.environ.get(
    "PERSISTENT_DISK_ROOT",
    "/var/data"
)

STATE_DIR = os.path.join(
    PERSISTENT_DISK_ROOT,
    "r35y_state"
)

DEDUPE_FILE = os.path.join(
    STATE_DIR,
    "telegram_processed_updates.json"
)

DECISION_FILE = os.path.join(
    STATE_DIR,
    "synthetic_decisions.json"
)

# --------------------------------------------------------------------------------------
# Reference-only R35U durable state.
# R35Y NEVER MUTATES THESE FILES.
# --------------------------------------------------------------------------------------

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

EXPECTED_R35U_UPDATE_ID = "R35U_SYNTHETIC_UPDATE_000001"

EXPECTED_R35U_DECISION_HASH = (
    "ada67682fedff8bbac0608cc96805dc42"
    "ea20bab56f3305c8afa06d7ef89cc94"
)

# --------------------------------------------------------------------------------------
# New R35Y update.
# This exact ID must later be replayed by R35Z.
# --------------------------------------------------------------------------------------

TEST_TELEGRAM_UPDATE_ID = "R35Y_SYNTHETIC_UPDATE_000001"

TEST_TELEGRAM_MESSAGE = (
    "BTCUSDT LONG ENTRY=MARKET "
    "LEVERAGE=100 MARGIN=ISOLATED "
    "TP1=0.5 TP2=1.0 TRAIL=0.2"
)

TEST_CHAT_ID = "R35Y_SYNTHETIC_CHAT"
TEST_MESSAGE_ID = "R35Y_SYNTHETIC_MESSAGE_000001"

# --------------------------------------------------------------------------------------
# Strategy constants preserved from the validated strategy baseline.
# --------------------------------------------------------------------------------------

SYMBOL = "BTCUSDT"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

ENTRY_BALANCE_PERCENT = 5.0

MAX_PYRAMID_ADDS = 1
PYRAMID_PERCENT = 5.0

MAX_BACKUPS = 3
BACKUP_PERCENT = 5.0
BACKUP_BUFFER_PERCENT = 0.3

MAX_FUND_EXPOSURE_PERCENT = 35.0

QTY_STEP = 0.0001
MIN_QTY = 0.0001

TP1_PERCENT = 20
TP1_TRIGGER_PERCENT = 0.5

TP2_PERCENT = 20
TP2_TRIGGER_PERCENT = 1.0

TP3_PERCENT = 60
TRAILING_DISTANCE_PERCENT = 0.20

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True

# --------------------------------------------------------------------------------------
# Absolute execution firebreak.
# --------------------------------------------------------------------------------------

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

# --------------------------------------------------------------------------------------
# Counters.
# --------------------------------------------------------------------------------------

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0

TELEGRAM_PROCESSING_ATTEMPTS = 0
SIGNAL_PARSE_COUNT = 0
SIGNAL_VALIDATION_COUNT = 0
SYNTHETIC_DECISION_CREATION_COUNT = 0

DURABLE_UPDATE_COMMITS = 0
DURABLE_DECISION_COMMITS = 0
DURABLE_REGISTRY_MUTATIONS = 0

DUPLICATE_GATE_ENTERED = False
DUPLICATE_DETECTED = False
DUPLICATE_REJECTED = False
DUPLICATE_REJECTED_BEFORE_PARSE = False

NEW_UPDATE_ACCEPTED = False
PIPELINE_CONTINUE_RESULT = False

TEST_STATUS = "NOT_RUN"

# --------------------------------------------------------------------------------------
# Runtime state.
# --------------------------------------------------------------------------------------

R35U_DURABLE_RECORD_LOADED = False
R35U_DECISION_REGISTRY_LOADED = False
R35U_REFERENCE_INTEGRITY_OK = False

R35Y_DEDUPE_REGISTRY_LOADED = False
R35Y_DECISION_REGISTRY_LOADED = False

UPDATE_PRESENT_BEFORE_PROCESSING = False
UPDATE_PRESENT_AFTER_PROCESSING = False

DECISION_PRESENT_BEFORE_PROCESSING = False
DECISION_PRESENT_AFTER_PROCESSING = False

DECISION_ID = None
DECISION_HASH = None
REPRODUCED_DECISION_HASH = None

DEDUPE_FILE_SHA256_BEFORE = None
DEDUPE_FILE_SHA256_AFTER = None

DECISION_FILE_SHA256_BEFORE = None
DECISION_FILE_SHA256_AFTER = None


# ======================================================================================
# LOGGING
# ======================================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(f"{utc_now()} {message}", flush=True)


def separator():
    log("-" * 100)


def section(title):
    separator()
    log(title)
    separator()


def result(label, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<82} {status}", flush=True)


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            f"{VERSION} OK\n"
            f"TEST_STATUS={TEST_STATUS}\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True
        )

        thread.start()

        log(
            f"{VERSION}: HEALTH SERVER STARTED "
            f"ON PORT {PORT}"
        )

    except Exception as exc:
        log(
            f"{VERSION}: HEALTH SERVER ERROR="
            f"{type(exc).__name__}:{exc}"
        )


# ======================================================================================
# CANONICAL SERIALIZATION / HASHING
# ======================================================================================

def canonical_json_bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_sha256(value):
    return sha256_bytes(
        canonical_json_bytes(value)
    )


def file_sha256(path):
    if not os.path.exists(path):
        return None

    digest = hashlib.sha256()

    with open(path, "rb") as handle:
        while True:
            block = handle.read(65536)

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


# ======================================================================================
# DURABLE JSON FILE HELPERS
# ======================================================================================

def ensure_state_dir():
    os.makedirs(
        STATE_DIR,
        exist_ok=True
    )


def load_json_file(path, default_value):
    if not os.path.exists(path):
        return default_value

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as handle:

        data = json.load(handle)

    return data


def atomic_write_json(path, value):
    global DURABLE_REGISTRY_MUTATIONS

    directory = os.path.dirname(path)

    os.makedirs(
        directory,
        exist_ok=True
    )

    fd, temp_path = tempfile.mkstemp(
        prefix=".r35y-",
        suffix=".tmp",
        dir=directory
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8"
        ) as handle:

            json.dump(
                value,
                handle,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False
            )

            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temp_path,
            path
        )

        DURABLE_REGISTRY_MUTATIONS += 1

    except Exception:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

        raise


def normalize_dedupe_registry(value):
    if not isinstance(value, dict):
        value = {}

    updates = value.get("updates")

    if not isinstance(updates, dict):
        updates = {}

    return {
        "updates": updates
    }


def normalize_decision_registry(value):
    if not isinstance(value, dict):
        value = {}

    decisions = value.get("decisions")

    if not isinstance(decisions, dict):
        decisions = {}

    return {
        "decisions": decisions
    }


# ======================================================================================
# REFERENCE SEARCH HELPERS
# ======================================================================================

def recursively_find_key_or_update_id(
    value,
    target,
    path="$"
):
    matches = []

    if isinstance(value, dict):

        for key, child in value.items():

            child_path = f"{path}.{key}"

            if str(key) == str(target):
                matches.append(
                    (
                        "KEY",
                        child_path
                    )
                )

            if (
                str(key) == "update_id"
                and str(child) == str(target)
            ):
                matches.append(
                    (
                        "VALUE",
                        child_path
                    )
                )

            matches.extend(
                recursively_find_key_or_update_id(
                    child,
                    target,
                    child_path
                )
            )

    elif isinstance(value, list):

        for index, child in enumerate(value):

            matches.extend(
                recursively_find_key_or_update_id(
                    child,
                    target,
                    f"{path}[{index}]"
                )
            )

    return matches


def find_r35u_decision_record(decision_registry):
    if not isinstance(
        decision_registry,
        dict
    ):
        return None, None

    decisions = decision_registry.get(
        "decisions"
    )

    if not isinstance(
        decisions,
        dict
    ):
        return None, None

    for key, record in decisions.items():

        if not isinstance(
            record,
            dict
        ):
            continue

        stored_hash = record.get(
            "decision_hash"
        )

        if (
            stored_hash
            == EXPECTED_R35U_DECISION_HASH
        ):
            return key, record

    return None, None


# ======================================================================================
# R35Y PART 2/4
# SYNTHETIC TELEGRAM PARSER + VALIDATOR + DECISION ENGINE
# ======================================================================================

def build_test_telegram_update():
    return {
        "update_id": TEST_TELEGRAM_UPDATE_ID,
        "message": {
            "message_id": TEST_MESSAGE_ID,
            "chat": {
                "id": TEST_CHAT_ID
            },
            "date": "R35Y_SYNTHETIC_TIME",
            "text": TEST_TELEGRAM_MESSAGE
        }
    }


def parse_signal(update):
    global SIGNAL_PARSE_COUNT

    SIGNAL_PARSE_COUNT += 1

    message = update.get(
        "message",
        {}
    )

    text = message.get(
        "text"
    )

    if not isinstance(text, str):
        raise ValueError(
            "TELEGRAM_MESSAGE_TEXT_MISSING"
        )

    normalized = (
        text.strip()
        .upper()
    )

    if "BTCUSDT" not in normalized:
        raise ValueError(
            "SYMBOL_NOT_FOUND"
        )

    if "LONG" not in normalized:
        raise ValueError(
            "DIRECTION_NOT_FOUND"
        )

    parsed = {
        "symbol": "BTCUSDT",
        "direction": "LONG",
        "entry_type": "MARKET",
        "target_margin_mode": TARGET_MARGIN_MODE,
        "target_long_leverage": TARGET_LONG_LEVERAGE,
        "target_short_leverage": TARGET_SHORT_LEVERAGE,
        "source_update_id": update["update_id"],
        "source_message_id": message.get(
            "message_id"
        ),
        "source_chat_id": message.get(
            "chat",
            {}
        ).get(
            "id"
        )
    }

    return parsed


def validate_signal(parsed):
    global SIGNAL_VALIDATION_COUNT

    SIGNAL_VALIDATION_COUNT += 1

    checks = {
        "symbol_ok":
            parsed.get("symbol")
            == SYMBOL,

        "direction_ok":
            parsed.get("direction")
            in (
                "LONG",
                "SHORT"
            ),

        "entry_type_ok":
            parsed.get("entry_type")
            == "MARKET",

        "margin_mode_ok":
            parsed.get(
                "target_margin_mode"
            )
            == TARGET_MARGIN_MODE,

        "long_leverage_ok":
            parsed.get(
                "target_long_leverage"
            )
            == TARGET_LONG_LEVERAGE,

        "short_leverage_ok":
            parsed.get(
                "target_short_leverage"
            )
            == TARGET_SHORT_LEVERAGE,

        "source_update_ok":
            parsed.get(
                "source_update_id"
            )
            == TEST_TELEGRAM_UPDATE_ID
    }

    valid = all(
        checks.values()
    )

    return valid, checks


def build_decision_payload(parsed):
    return {
        "schema": "R35Y_SYNTHETIC_DECISION_V1",

        "source": {
            "telegram_update_id":
                parsed[
                    "source_update_id"
                ],

            "telegram_message_id":
                parsed[
                    "source_message_id"
                ],

            "telegram_chat_id":
                parsed[
                    "source_chat_id"
                ]
        },

        "signal": {
            "symbol":
                parsed[
                    "symbol"
                ],

            "direction":
                parsed[
                    "direction"
                ],

            "entry_type":
                parsed[
                    "entry_type"
                ]
        },

        "execution_targets": {
            "margin_mode":
                TARGET_MARGIN_MODE,

            "long_leverage":
                TARGET_LONG_LEVERAGE,

            "short_leverage":
                TARGET_SHORT_LEVERAGE
        },

        "risk": {
            "entry_balance_percent":
                ENTRY_BALANCE_PERCENT,

            "max_fund_exposure_percent":
                MAX_FUND_EXPOSURE_PERCENT,

            "max_pyramid_adds":
                MAX_PYRAMID_ADDS,

            "pyramid_percent":
                PYRAMID_PERCENT,

            "max_backups":
                MAX_BACKUPS,

            "backup_percent":
                BACKUP_PERCENT,

            "backup_buffer_percent":
                BACKUP_BUFFER_PERCENT
        },

        "quantity_rules": {
            "qty_step":
                QTY_STEP,

            "min_qty":
                MIN_QTY
        },

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

        "timing": {
            "signal_expiry_seconds":
                SIGNAL_EXPIRY_SECONDS,

            "loss_cooldown_seconds":
                LOSS_COOLDOWN_SECONDS
        },

        "strategy_flags": {
            "one_direction_only":
                ONE_DIRECTION_ONLY,

            "anti_duplicate_orders":
                ANTI_DUPLICATE_ORDERS,

            "trend_reversal_exit":
                TREND_REVERSAL_EXIT,

            "idle_pyramid_cleanup":
                IDLE_PYRAMID_CLEANUP
        },

        "execution_policy": {
            "synthetic_only": True,

            "real_order_execution":
                False,

            "first_real_order_allowed":
                False,

            "demo_order_execution":
                False,

            "exchange_mutation_transport_enabled":
                False,

            "order_submission_enabled":
                False,

            "leverage_mutation_enabled":
                False,

            "margin_mode_mutation_enabled":
                False,

            "position_mutation_enabled":
                False
        }
    }


def create_synthetic_decision(
    parsed
):
    global SYNTHETIC_DECISION_CREATION_COUNT

    SYNTHETIC_DECISION_CREATION_COUNT += 1

    payload = build_decision_payload(
        parsed
    )

    decision_hash = canonical_sha256(
        payload
    )

    decision_id = (
        "r35y-"
        + decision_hash[:20]
    )

    record = {
        "decision_id":
            decision_id,

        "source_update_id":
            TEST_TELEGRAM_UPDATE_ID,

        "payload":
            payload,

        "decision_hash":
            decision_hash,

        "hash_serializer":
            "SORTED_COMPACT_UTF8",

        "synthetic_only":
            True,

        "exchange_network_write":
            False,

        "order_submission":
            False
    }

    return (
        decision_id,
        record
    )


# ======================================================================================
# DURABLE DUPLICATE GATE
# ======================================================================================

def durable_duplicate_gate(
    update_id,
    dedupe_registry
):
    global DUPLICATE_GATE_ENTERED
    global DUPLICATE_DETECTED
    global DUPLICATE_REJECTED
    global DUPLICATE_REJECTED_BEFORE_PARSE
    global NEW_UPDATE_ACCEPTED
    global PIPELINE_CONTINUE_RESULT

    DUPLICATE_GATE_ENTERED = True

    updates = dedupe_registry.get(
        "updates",
        {}
    )

    if update_id in updates:

        DUPLICATE_DETECTED = True
        DUPLICATE_REJECTED = True
        DUPLICATE_REJECTED_BEFORE_PARSE = True

        NEW_UPDATE_ACCEPTED = False
        PIPELINE_CONTINUE_RESULT = False

        return False

    DUPLICATE_DETECTED = False
    DUPLICATE_REJECTED = False
    DUPLICATE_REJECTED_BEFORE_PARSE = False

    NEW_UPDATE_ACCEPTED = True
    PIPELINE_CONTINUE_RESULT = True

    return True


# ======================================================================================
# DURABLE COMMIT
# ======================================================================================

def commit_update_and_decision(
    update,
    decision_id,
    decision_record,
    dedupe_registry,
    decision_registry
):
    global DURABLE_UPDATE_COMMITS
    global DURABLE_DECISION_COMMITS

    update_id = update[
        "update_id"
    ]

    if update_id in dedupe_registry[
        "updates"
    ]:
        raise RuntimeError(
            "UPDATE_BECAME_DUPLICATE_BEFORE_COMMIT"
        )

    if decision_id in decision_registry[
        "decisions"
    ]:
        raise RuntimeError(
            "DECISION_ID_ALREADY_EXISTS"
        )

    # ----------------------------------------------------------------------------------
    # Decision record first.
    #
    # This ensures that an accepted update is never durably marked processed
    # before its deterministic synthetic decision exists.
    # ----------------------------------------------------------------------------------

    new_decision_registry = {
        "decisions": dict(
            decision_registry[
                "decisions"
            ]
        )
    }

    new_decision_registry[
        "decisions"
    ][
        decision_id
    ] = decision_record

    atomic_write_json(
        DECISION_FILE,
        new_decision_registry
    )

    DURABLE_DECISION_COMMITS += 1

    # ----------------------------------------------------------------------------------
    # Then durable Telegram processed-update marker.
    # ----------------------------------------------------------------------------------

    update_record = {
        "update_id":
            update_id,

        "decision_id":
            decision_id,

        "decision_hash":
            decision_record[
                "decision_hash"
            ],

        "status":
            "PROCESSED_SYNTHETICALLY",

        "parser_entered":
            True,

        "validator_entered":
            True,

        "synthetic_decision_created":
            True,

        "exchange_network_writes":
            0,

        "order_submissions":
            0,

        "real_orders_sent":
            0
    }

    new_dedupe_registry = {
        "updates": dict(
            dedupe_registry[
                "updates"
            ]
        )
    }

    new_dedupe_registry[
        "updates"
    ][
        update_id
    ] = update_record

    atomic_write_json(
        DEDUPE_FILE,
        new_dedupe_registry
    )

    DURABLE_UPDATE_COMMITS += 1


# ======================================================================================
# R35Y PART 3/4
# TEST EXECUTION
# ======================================================================================

def run_tests():

    global TEST_STATUS

    global R35U_DURABLE_RECORD_LOADED
    global R35U_DECISION_REGISTRY_LOADED
    global R35U_REFERENCE_INTEGRITY_OK

    global R35Y_DEDUPE_REGISTRY_LOADED
    global R35Y_DECISION_REGISTRY_LOADED

    global UPDATE_PRESENT_BEFORE_PROCESSING
    global UPDATE_PRESENT_AFTER_PROCESSING

    global DECISION_PRESENT_BEFORE_PROCESSING
    global DECISION_PRESENT_AFTER_PROCESSING

    global DECISION_ID
    global DECISION_HASH
    global REPRODUCED_DECISION_HASH

    global DEDUPE_FILE_SHA256_BEFORE
    global DEDUPE_FILE_SHA256_AFTER

    global DECISION_FILE_SHA256_BEFORE
    global DECISION_FILE_SHA256_AFTER

    global TELEGRAM_PROCESSING_ATTEMPTS

    failures = []

    ensure_state_dir()

    # ==================================================================================
    # TEST 1
    # HARD SAFETY CONFIGURATION
    # ==================================================================================

    section(
        "R35Y TEST 1: HARD ZERO-WRITE SAFETY FIREBREAK"
    )

    checks = [
        (
            "Real Order Execution Disabled",
            REAL_ORDER_EXECUTION is False
        ),
        (
            "First Real Order Permission Disabled",
            FIRST_REAL_ORDER_ALLOWED is False
        ),
        (
            "Demo Order Execution Disabled",
            DEMO_ORDER_EXECUTION is False
        ),
        (
            "Exchange Mutation Transport Disabled",
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False
        ),
        (
            "Order Submission Disabled",
            ORDER_SUBMISSION_ENABLED is False
        ),
        (
            "Leverage Mutation Disabled",
            LEVERAGE_MUTATION_ENABLED is False
        ),
        (
            "Margin Mode Mutation Disabled",
            MARGIN_MODE_MUTATION_ENABLED is False
        ),
        (
            "Position Mutation Disabled",
            POSITION_MUTATION_ENABLED is False
        )
    ]

    for label, passed in checks:
        result(
            label,
            passed
        )

        if not passed:
            failures.append(
                label
            )

    # ==================================================================================
    # TEST 2
    # PERSISTENT STORAGE
    # ==================================================================================

    section(
        "R35Y TEST 2: PERSISTENT STORAGE"
    )

    log(
        f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}"
    )
    log(
        f"STATE_DIR={STATE_DIR}"
    )
    log(
        f"DEDUPE_FILE={DEDUPE_FILE}"
    )
    log(
        f"DECISION_FILE={DECISION_FILE}"
    )

    state_ok = os.path.isdir(
        STATE_DIR
    )

    writable_ok = os.access(
        STATE_DIR,
        os.W_OK
    )

    result(
        "R35Y State Directory Available",
        state_ok
    )

    result(
        "R35Y State Directory Writable",
        writable_ok
    )

    if not state_ok:
        failures.append(
            "STATE_DIRECTORY_UNAVAILABLE"
        )

    if not writable_ok:
        failures.append(
            "STATE_DIRECTORY_NOT_WRITABLE"
        )

    # ==================================================================================
    # TEST 3
    # READ R35U REFERENCE STATE WITHOUT MUTATING IT
    # ==================================================================================

    section(
        "R35Y TEST 3: LOAD R35U REFERENCE DURABLE STATE READ-ONLY"
    )

    r35u_dedupe = None
    r35u_decisions = None

    try:
        r35u_dedupe = load_json_file(
            R35U_DEDUPE_FILE,
            None
        )

        R35U_DURABLE_RECORD_LOADED = (
            isinstance(
                r35u_dedupe,
                dict
            )
        )

    except Exception as exc:
        log(
            f"R35U_DEDUPE_LOAD_ERROR="
            f"{type(exc).__name__}:{exc}"
        )

    try:
        r35u_decisions = load_json_file(
            R35U_DECISION_FILE,
            None
        )

        R35U_DECISION_REGISTRY_LOADED = (
            isinstance(
                r35u_decisions,
                dict
            )
        )

    except Exception as exc:
        log(
            f"R35U_DECISION_LOAD_ERROR="
            f"{type(exc).__name__}:{exc}"
        )

    result(
        "R35U Durable Dedupe Registry Loaded",
        R35U_DURABLE_RECORD_LOADED
    )

    result(
        "R35U Durable Decision Registry Loaded",
        R35U_DECISION_REGISTRY_LOADED
    )

    if not R35U_DURABLE_RECORD_LOADED:
        failures.append(
            "R35U_DEDUPE_NOT_AVAILABLE"
        )

    if not R35U_DECISION_REGISTRY_LOADED:
        failures.append(
            "R35U_DECISION_REGISTRY_NOT_AVAILABLE"
        )

    # ==================================================================================
    # TEST 4
    # VERIFY R35U REFERENCE INTEGRITY
    # ==================================================================================

    section(
        "R35Y TEST 4: R35U REFERENCE INTEGRITY"
    )

    r35u_matches = []

    if R35U_DURABLE_RECORD_LOADED:

        r35u_matches = (
            recursively_find_key_or_update_id(
                r35u_dedupe,
                EXPECTED_R35U_UPDATE_ID
            )
        )

    r35u_decision_key = None
    r35u_decision_record = None
    r35u_reproduced_hash = None

    if R35U_DECISION_REGISTRY_LOADED:

        (
            r35u_decision_key,
            r35u_decision_record
        ) = find_r35u_decision_record(
            r35u_decisions
        )

    if isinstance(
        r35u_decision_record,
        dict
    ):

        payload = r35u_decision_record.get(
            "payload"
        )

        if isinstance(
            payload,
            dict
        ):

            r35u_reproduced_hash = (
                canonical_sha256(
                    payload
                )
            )

    r35u_update_found = (
        len(r35u_matches) > 0
    )

    r35u_decision_found = (
        r35u_decision_record
        is not None
    )

    r35u_hash_valid = (
        r35u_reproduced_hash
        == EXPECTED_R35U_DECISION_HASH
    )

    R35U_REFERENCE_INTEGRITY_OK = (
        r35u_update_found
        and
        r35u_decision_found
        and
        r35u_hash_valid
    )

    log(
        f"EXPECTED_R35U_UPDATE_ID="
        f"{EXPECTED_R35U_UPDATE_ID}"
    )

    log(
        f"EXPECTED_R35U_DECISION_HASH="
        f"{EXPECTED_R35U_DECISION_HASH}"
    )

    log(
        f"R35U_REFERENCE_UPDATE_MATCH_COUNT="
        f"{len(r35u_matches)}"
    )

    log(
        f"R35U_REFERENCE_DECISION_ID="
        f"{r35u_decision_key}"
    )

    log(
        f"R35U_REFERENCE_REPRODUCED_HASH="
        f"{r35u_reproduced_hash}"
    )

    result(
        "Original R35U Update Still Present",
        r35u_update_found
    )

    result(
        "Original R35U Decision Still Present",
        r35u_decision_found
    )

    result(
        "Original R35U Decision Hash Still Reproduces Exactly",
        r35u_hash_valid
    )

    if not R35U_REFERENCE_INTEGRITY_OK:
        failures.append(
            "R35U_REFERENCE_INTEGRITY_FAILED"
        )

    # ==================================================================================
    # TEST 5
    # LOAD R35Y REGISTRIES
    # ==================================================================================

    section(
        "R35Y TEST 5: LOAD R35Y DURABLE REGISTRIES"
    )

    try:
        raw_dedupe_registry = load_json_file(
            DEDUPE_FILE,
            {
                "updates": {}
            }
        )

        dedupe_registry = (
            normalize_dedupe_registry(
                raw_dedupe_registry
            )
        )

        R35Y_DEDUPE_REGISTRY_LOADED = True

    except Exception as exc:

        dedupe_registry = {
            "updates": {}
        }

        log(
            f"R35Y_DEDUPE_LOAD_ERROR="
            f"{type(exc).__name__}:{exc}"
        )

    try:
        raw_decision_registry = load_json_file(
            DECISION_FILE,
            {
                "decisions": {}
            }
        )

        decision_registry = (
            normalize_decision_registry(
                raw_decision_registry
            )
        )

        R35Y_DECISION_REGISTRY_LOADED = True

    except Exception as exc:

        decision_registry = {
            "decisions": {}
        }

        log(
            f"R35Y_DECISION_LOAD_ERROR="
            f"{type(exc).__name__}:{exc}"
        )

    result(
        "R35Y Durable Dedupe Registry Loaded",
        R35Y_DEDUPE_REGISTRY_LOADED
    )

    result(
        "R35Y Durable Decision Registry Loaded",
        R35Y_DECISION_REGISTRY_LOADED
    )

    if not R35Y_DEDUPE_REGISTRY_LOADED:
        failures.append(
            "R35Y_DEDUPE_LOAD_FAILED"
        )

    if not R35Y_DECISION_REGISTRY_LOADED:
        failures.append(
            "R35Y_DECISION_LOAD_FAILED"
        )

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

    log(
        f"DEDUPE_FILE_SHA256_BEFORE="
        f"{DEDUPE_FILE_SHA256_BEFORE}"
    )

    log(
        f"DECISION_FILE_SHA256_BEFORE="
        f"{DECISION_FILE_SHA256_BEFORE}"
    )

    # ==================================================================================
    # TEST 6
    # PROVE R35Y UPDATE IS NEW BEFORE PARSING
    # ==================================================================================

    section(
        "R35Y TEST 6: NEW UPDATE PRECONDITION"
    )

    UPDATE_PRESENT_BEFORE_PROCESSING = (
        TEST_TELEGRAM_UPDATE_ID
        in
        dedupe_registry[
            "updates"
        ]
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"UPDATE_PRESENT_BEFORE_PROCESSING="
        f"{UPDATE_PRESENT_BEFORE_PROCESSING}"
    )

    result(
        "R35Y Update Is New Before Processing",
        UPDATE_PRESENT_BEFORE_PROCESSING
        is False
    )

    if UPDATE_PRESENT_BEFORE_PROCESSING:

        failures.append(
            "R35Y_UPDATE_ALREADY_EXISTS"
        )

    # ==================================================================================
    # TEST 7
    # PRE-PARSE DURABLE DUPLICATE GATE
    # ==================================================================================

    section(
        "R35Y TEST 7: PRE-PARSE DURABLE DUPLICATE GATE"
    )

    TELEGRAM_PROCESSING_ATTEMPTS += 1

    gate_continue = durable_duplicate_gate(
        TEST_TELEGRAM_UPDATE_ID,
        dedupe_registry
    )

    log(
        f"DUPLICATE_GATE_INPUT_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        "DUPLICATE_GATE_RESULT="
        + (
            "ACCEPT"
            if gate_continue
            else "REJECT"
        )
    )

    log(
        "DUPLICATE_GATE_REASON="
        + (
            "UPDATE_NOT_PRESENT_IN_DURABLE_REGISTRY"
            if gate_continue
            else
            "UPDATE_ALREADY_PRESENT_IN_DURABLE_REGISTRY"
        )
    )

    log(
        f"PIPELINE_CONTINUE_RESULT="
        f"{PIPELINE_CONTINUE_RESULT}"
    )

    result(
        "Duplicate Gate Entered",
        DUPLICATE_GATE_ENTERED
    )

    result(
        "No Existing R35Y Durable Update Detected",
        DUPLICATE_DETECTED
        is False
    )

    result(
        "New R35Y Update Accepted",
        NEW_UPDATE_ACCEPTED
    )

    result(
        "Pipeline Allowed To Continue",
        PIPELINE_CONTINUE_RESULT
    )

    if not gate_continue:
        failures.append(
            "NEW_UPDATE_REJECTED_BY_DUPLICATE_GATE"
        )

    # ==================================================================================
    # TEST 8
    # PARSE AND VALIDATE EXACTLY ONCE
    # ==================================================================================

    section(
        "R35Y TEST 8: PARSE AND VALIDATE NEW UPDATE EXACTLY ONCE"
    )

    parsed = None
    validation_checks = {}
    signal_valid = False

    if gate_continue:

        try:
            update = (
                build_test_telegram_update()
            )

            parsed = parse_signal(
                update
            )

            (
                signal_valid,
                validation_checks
            ) = validate_signal(
                parsed
            )

        except Exception as exc:

            log(
                f"PIPELINE_ERROR="
                f"{type(exc).__name__}:{exc}"
            )

            failures.append(
                "PARSE_OR_VALIDATION_EXCEPTION"
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
        f"SIGNAL_VALID={signal_valid}"
    )

    for key in sorted(
        validation_checks.keys()
    ):
        log(
            f"VALIDATION_{key.upper()}="
            f"{validation_checks[key]}"
        )

    result(
        "Parser Entered Exactly Once",
        SIGNAL_PARSE_COUNT == 1
    )

    result(
        "Validator Entered Exactly Once",
        SIGNAL_VALIDATION_COUNT == 1
    )

    result(
        "Synthetic Signal Validation Passed",
        signal_valid
    )

    if SIGNAL_PARSE_COUNT != 1:
        failures.append(
            "PARSER_ENTRY_COUNT_INVALID"
        )

    if SIGNAL_VALIDATION_COUNT != 1:
        failures.append(
            "VALIDATOR_ENTRY_COUNT_INVALID"
        )

    if not signal_valid:
        failures.append(
            "SIGNAL_VALIDATION_FAILED"
        )

    # ==================================================================================
    # TEST 9
    # CREATE ONE DETERMINISTIC SYNTHETIC DECISION
    # ==================================================================================

    section(
        "R35Y TEST 9: DETERMINISTIC SYNTHETIC DECISION CREATION"
    )

    decision_record = None

    if (
        gate_continue
        and
        signal_valid
    ):

        (
            DECISION_ID,
            decision_record
        ) = create_synthetic_decision(
            parsed
        )

        DECISION_HASH = (
            decision_record[
                "decision_hash"
            ]
        )

        REPRODUCED_DECISION_HASH = (
            canonical_sha256(
                decision_record[
                    "payload"
                ]
            )
        )

    DECISION_PRESENT_BEFORE_PROCESSING = (
        DECISION_ID
        in
        decision_registry[
            "decisions"
        ]
        if DECISION_ID
        else False
    )

    log(
        f"DECISION_ID="
        f"{DECISION_ID}"
    )

    log(
        f"DECISION_HASH="
        f"{DECISION_HASH}"
    )

    log(
        f"REPRODUCED_DECISION_HASH="
        f"{REPRODUCED_DECISION_HASH}"
    )

    log(
        "DECISION_HASH_SERIALIZER="
        "SORTED_COMPACT_UTF8"
    )

    log(
        f"DECISION_PRESENT_BEFORE_PROCESSING="
        f"{DECISION_PRESENT_BEFORE_PROCESSING}"
    )

    result(
        "Synthetic Decision Created Exactly Once",
        SYNTHETIC_DECISION_CREATION_COUNT
        == 1
    )

    result(
        "Decision Hash Reproduces Exactly",
        (
            DECISION_HASH
            is not None
            and
            DECISION_HASH
            == REPRODUCED_DECISION_HASH
        )
    )

    result(
        "Decision Did Not Exist Before Commit",
        DECISION_PRESENT_BEFORE_PROCESSING
        is False
    )

    if (
        SYNTHETIC_DECISION_CREATION_COUNT
        != 1
    ):
        failures.append(
            "SYNTHETIC_DECISION_COUNT_INVALID"
        )

    if (
        DECISION_HASH
        != REPRODUCED_DECISION_HASH
    ):
        failures.append(
            "DECISION_HASH_REPRODUCTION_FAILED"
        )

    if DECISION_PRESENT_BEFORE_PROCESSING:
        failures.append(
            "DECISION_ALREADY_EXISTED"
        )

    # ==================================================================================
    # TEST 10
    # DURABLE COMMIT
    # ==================================================================================

    section(
        "R35Y TEST 10: EXACTLY-ONCE DURABLE COMMIT"
    )

    if (
        gate_continue
        and
        signal_valid
        and
        decision_record
        is not None
        and
        not failures
    ):

        try:

            commit_update_and_decision(
                update,
                DECISION_ID,
                decision_record,
                dedupe_registry,
                decision_registry
            )

        except Exception as exc:

            log(
                f"DURABLE_COMMIT_ERROR="
                f"{type(exc).__name__}:{exc}"
            )

            failures.append(
                "DURABLE_COMMIT_FAILED"
            )

    log(
        f"DURABLE_DECISION_COMMITS="
        f"{DURABLE_DECISION_COMMITS}"
    )

    log(
        f"DURABLE_UPDATE_COMMITS="
        f"{DURABLE_UPDATE_COMMITS}"
    )

    log(
        f"DURABLE_REGISTRY_MUTATIONS="
        f"{DURABLE_REGISTRY_MUTATIONS}"
    )

    result(
        "Exactly One Durable Decision Commit",
        DURABLE_DECISION_COMMITS
        == 1
    )

    result(
        "Exactly One Durable Update Commit",
        DURABLE_UPDATE_COMMITS
        == 1
    )

    result(
        "Exactly Two Local Registry File Mutations",
        DURABLE_REGISTRY_MUTATIONS
        == 2
    )

    if DURABLE_DECISION_COMMITS != 1:
        failures.append(
            "DURABLE_DECISION_COMMIT_COUNT_INVALID"
        )

    if DURABLE_UPDATE_COMMITS != 1:
        failures.append(
            "DURABLE_UPDATE_COMMIT_COUNT_INVALID"
        )

    if DURABLE_REGISTRY_MUTATIONS != 2:
        failures.append(
            "DURABLE_REGISTRY_MUTATION_COUNT_INVALID"
        )

    # ==================================================================================
    # TEST 11
    # READ BACK DURABLE STATE
    # ==================================================================================

    section(
        "R35Y TEST 11: DURABLE READ-BACK VERIFICATION"
    )

    final_dedupe_registry = normalize_dedupe_registry(
        load_json_file(
            DEDUPE_FILE,
            {
                "updates": {}
            }
        )
    )

    final_decision_registry = normalize_decision_registry(
        load_json_file(
            DECISION_FILE,
            {
                "decisions": {}
            }
        )
    )

    UPDATE_PRESENT_AFTER_PROCESSING = (
        TEST_TELEGRAM_UPDATE_ID
        in
        final_dedupe_registry[
            "updates"
        ]
    )

    DECISION_PRESENT_AFTER_PROCESSING = (
        DECISION_ID
        in
        final_decision_registry[
            "decisions"
        ]
        if DECISION_ID
        else False
    )

    stored_update_record = (
        final_dedupe_registry[
            "updates"
        ].get(
            TEST_TELEGRAM_UPDATE_ID
        )
    )

    stored_decision_record = (
        final_decision_registry[
            "decisions"
        ].get(
            DECISION_ID
        )
        if DECISION_ID
        else None
    )

    stored_decision_hash = None
    stored_payload_hash = None

    if isinstance(
        stored_decision_record,
        dict
    ):

        stored_decision_hash = (
            stored_decision_record.get(
                "decision_hash"
            )
        )

        stored_payload = (
            stored_decision_record.get(
                "payload"
            )
        )

        if isinstance(
            stored_payload,
            dict
        ):

            stored_payload_hash = (
                canonical_sha256(
                    stored_payload
                )
            )

    update_links_to_decision = (
        isinstance(
            stored_update_record,
            dict
        )
        and
        stored_update_record.get(
            "decision_id"
        )
        == DECISION_ID
        and
        stored_update_record.get(
            "decision_hash"
        )
        == DECISION_HASH
    )

    log(
        f"UPDATE_PRESENT_AFTER_PROCESSING="
        f"{UPDATE_PRESENT_AFTER_PROCESSING}"
    )

    log(
        f"DECISION_PRESENT_AFTER_PROCESSING="
        f"{DECISION_PRESENT_AFTER_PROCESSING}"
    )

    log(
        f"STORED_DECISION_HASH="
        f"{stored_decision_hash}"
    )

    log(
        f"STORED_PAYLOAD_REPRODUCED_HASH="
        f"{stored_payload_hash}"
    )

    result(
        "R35Y Update Persisted Durably",
        UPDATE_PRESENT_AFTER_PROCESSING
    )

    result(
        "R35Y Decision Persisted Durably",
        DECISION_PRESENT_AFTER_PROCESSING
    )

    result(
        "Durable Update Links To Exact Decision",
        update_links_to_decision
    )

    result(
        "Durable Decision Hash Matches Original",
        stored_decision_hash
        == DECISION_HASH
    )

    result(
        "Durable Payload Reproduces Decision Hash",
        (
            stored_payload_hash
            == DECISION_HASH
        )
    )

    if not UPDATE_PRESENT_AFTER_PROCESSING:
        failures.append(
            "UPDATE_DURABILITY_FAILED"
        )

    if not DECISION_PRESENT_AFTER_PROCESSING:
        failures.append(
            "DECISION_DURABILITY_FAILED"
        )

    if not update_links_to_decision:
        failures.append(
            "UPDATE_DECISION_LINK_FAILED"
        )

    if stored_decision_hash != DECISION_HASH:
        failures.append(
            "STORED_DECISION_HASH_MISMATCH"
        )

    if stored_payload_hash != DECISION_HASH:
        failures.append(
            "STORED_PAYLOAD_HASH_MISMATCH"
        )

    # ==================================================================================
    # TEST 12
    # FILE HASHES AFTER COMMIT
    # ==================================================================================

    section(
        "R35Y TEST 12: PERSISTED FILE HASH VERIFICATION"
    )

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

    log(
        f"DEDUPE_FILE_SHA256_AFTER="
        f"{DEDUPE_FILE_SHA256_AFTER}"
    )

    log(
        f"DECISION_FILE_SHA256_AFTER="
        f"{DECISION_FILE_SHA256_AFTER}"
    )

    dedupe_exists = (
        DEDUPE_FILE_SHA256_AFTER
        is not None
    )

    decision_exists = (
        DECISION_FILE_SHA256_AFTER
        is not None
    )

    result(
        "R35Y Dedupe File Exists Durably",
        dedupe_exists
    )

    result(
        "R35Y Decision File Exists Durably",
        decision_exists
    )

    if not dedupe_exists:
        failures.append(
            "DEDUPE_FILE_NOT_DURABLE"
        )

    if not decision_exists:
        failures.append(
            "DECISION_FILE_NOT_DURABLE"
        )

    # ==================================================================================
    # TEST 13
    # IMMEDIATE SECOND GATE CHECK IN MEMORY
    #
    # IMPORTANT:
    # We do NOT invoke parser again.
    # We merely prove that the newly persisted update is now classified duplicate.
    # ==================================================================================

    section(
        "R35Y TEST 13: POST-COMMIT DUPLICATE VISIBILITY"
    )

    persisted_updates = (
        final_dedupe_registry[
            "updates"
        ]
    )

    immediate_duplicate_visible = (
        TEST_TELEGRAM_UPDATE_ID
        in
        persisted_updates
    )

    log(
        f"POST_COMMIT_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"POST_COMMIT_DUPLICATE_VISIBLE="
        f"{immediate_duplicate_visible}"
    )

    result(
        "Committed Update Is Now Visible To Future Duplicate Gate",
        immediate_duplicate_visible
    )

    result(
        "Parser Was Still Entered Only Once",
        SIGNAL_PARSE_COUNT == 1
    )

    result(
        "Validator Was Still Entered Only Once",
        SIGNAL_VALIDATION_COUNT == 1
    )

    result(
        "Decision Was Still Created Only Once",
        SYNTHETIC_DECISION_CREATION_COUNT
        == 1
    )

    if not immediate_duplicate_visible:
        failures.append(
            "POST_COMMIT_DUPLICATE_NOT_VISIBLE"
        )

    # ==================================================================================
    # TEST 14
    # R35U REFERENCE FILES REMAIN UNTOUCHED BY R35Y
    # ==================================================================================

    section(
        "R35Y TEST 14: R35U REFERENCE REMAINS READ-ONLY"
    )

    r35u_final_update_found = False
    r35u_final_hash_valid = False

    try:

        final_r35u_dedupe = load_json_file(
            R35U_DEDUPE_FILE,
            None
        )

        final_r35u_matches = (
            recursively_find_key_or_update_id(
                final_r35u_dedupe,
                EXPECTED_R35U_UPDATE_ID
            )
        )

        r35u_final_update_found = (
            len(final_r35u_matches)
            > 0
        )

    except Exception:
        pass

    try:

        final_r35u_decisions = load_json_file(
            R35U_DECISION_FILE,
            None
        )

        (
            _,
            final_r35u_record
        ) = find_r35u_decision_record(
            final_r35u_decisions
        )

        if isinstance(
            final_r35u_record,
            dict
        ):

            final_payload = (
                final_r35u_record.get(
                    "payload"
                )
            )

            if isinstance(
                final_payload,
                dict
            ):

                final_hash = canonical_sha256(
                    final_payload
                )

                r35u_final_hash_valid = (
                    final_hash
                    == EXPECTED_R35U_DECISION_HASH
                )

    except Exception:
        pass

    result(
        "R35U Original Durable Update Still Present",
        r35u_final_update_found
    )

    result(
        "R35U Original Decision Hash Still Valid",
        r35u_final_hash_valid
    )

    if not r35u_final_update_found:
        failures.append(
            "R35U_REFERENCE_UPDATE_CHANGED"
        )

    if not r35u_final_hash_valid:
        failures.append(
            "R35U_REFERENCE_DECISION_CHANGED"
        )

    # ==================================================================================
    # TEST 15
    # FINAL ZERO EXCHANGE WRITE FIREBREAK
    # ==================================================================================

    section(
        "R35Y TEST 15: FINAL ZERO-WRITE FIREBREAK"
    )

    zero_write_checks = [
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
        )
    ]

    for label, passed in zero_write_checks:

        result(
            label,
            passed
        )

        if not passed:
            failures.append(
                label
            )

    zero_write_firebreak_ok = all(
        passed
        for _, passed
        in zero_write_checks
    )

    # ==================================================================================
    # FINAL STATUS
    # ==================================================================================

    TEST_STATUS = (
        "PASS"
        if len(failures) == 0
        else "FAIL"
    )

    section(
        "R35Y: FINAL TEST SUMMARY"
    )

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"R35U_REFERENCE_UPDATE_ID="
        f"{EXPECTED_R35U_UPDATE_ID}"
    )

    log(
        f"R35U_REFERENCE_DECISION_HASH="
        f"{EXPECTED_R35U_DECISION_HASH}"
    )

    log(
        f"R35U_REFERENCE_INTEGRITY_OK="
        f"{R35U_REFERENCE_INTEGRITY_OK}"
    )

    log(
        f"R35Y_DEDUPE_FILE="
        f"{DEDUPE_FILE}"
    )

    log(
        f"R35Y_DECISION_FILE="
        f"{DECISION_FILE}"
    )

    log(
        f"UPDATE_PRESENT_BEFORE_PROCESSING="
        f"{UPDATE_PRESENT_BEFORE_PROCESSING}"
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
        f"R35Y_DECISION_ID="
        f"{DECISION_ID}"
    )

    log(
        f"R35Y_STORED_DECISION_HASH="
        f"{DECISION_HASH}"
    )

    log(
        f"R35Y_REPRODUCED_DECISION_HASH="
        f"{REPRODUCED_DECISION_HASH}"
    )

    log(
        "R35Y_HASH_SERIALIZER="
        "SORTED_COMPACT_UTF8"
    )

    log(
        f"DURABLE_DECISION_COMMITS="
        f"{DURABLE_DECISION_COMMITS}"
    )

    log(
        f"DURABLE_UPDATE_COMMITS="
        f"{DURABLE_UPDATE_COMMITS}"
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
        f"DECISION_PRESENT_AFTER_PROCESSING="
        f"{DECISION_PRESENT_AFTER_PROCESSING}"
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
        f"ZERO_WRITE_FIREBREAK_OK="
        f"{zero_write_firebreak_ok}"
    )

    log(
        f"TEST_STATUS="
        f"{TEST_STATUS}"
    )

    if failures:

        log(
            "FAILURES="
            + ",".join(
                failures
            )
        )

    else:

        log(
            "FAILURES=NONE"
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

    return TEST_STATUS == "PASS"


# ======================================================================================
# R35Y PART 4/4
# MAIN + HEARTBEAT
# ======================================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"R35U_REFERENCE_INTEGRITY_OK="
            f"{R35U_REFERENCE_INTEGRITY_OK} "
            f"NEW_UPDATE_ACCEPTED="
            f"{NEW_UPDATE_ACCEPTED} "
            f"UPDATE_PRESENT_AFTER_PROCESSING="
            f"{UPDATE_PRESENT_AFTER_PROCESSING} "
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


def main():

    start_health_server()

    separator()
    log(
        f"{VERSION}: MAIN.PY ENTERED"
    )
    separator()

    log(
        f"{VERSION}: PURPOSE={PURPOSE}"
    )

    log(
        f"{VERSION}: TEST UPDATE="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: TARGET MARGIN MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"{VERSION}: TARGET LONG LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"{VERSION}: TARGET SHORT LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: FIRST REAL ORDER ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION="
        f"{DEMO_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: EXCHANGE MUTATION TRANSPORT ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"{VERSION}: ORDER SUBMISSION ENABLED="
        f"{ORDER_SUBMISSION_ENABLED}"
    )

    log(
        f"{VERSION}: PERSISTENT DISK ROOT="
        f"{PERSISTENT_DISK_ROOT}"
    )

    log(
        f"{VERSION}: STATE DIR="
        f"{STATE_DIR}"
    )

    try:

        run_tests()

    except Exception as exc:

        global TEST_STATUS

        TEST_STATUS = "FAIL"

        separator()

        log(
            f"{VERSION}: UNHANDLED TEST EXCEPTION="
            f"{type(exc).__name__}:{exc}"
        )

        separator()

        import traceback

        traceback.print_exc()

    heartbeat_loop()


if __name__ == "__main__":
    main()

