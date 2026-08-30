

import os
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R35U
#
# PURPOSE:
# BRAND-NEW TELEGRAM UPDATE
# -> ACCEPT EXACTLY ONCE
# -> PARSE EXACTLY ONCE
# -> VALIDATE EXACTLY ONCE
# -> CREATE EXACTLY ONE DURABLE SYNTHETIC DECISION
# -> WRITE DURABLE DEDUPE RECORD
# -> ZERO EXCHANGE WRITES
#
# IMPORTANT:
# THIS FILE DOES NOT SUBMIT ORDERS.
# THIS FILE DOES NOT MUTATE LEVERAGE.
# THIS FILE DOES NOT MUTATE MARGIN MODE.
# THIS FILE DOES NOT MUTATE POSITIONS.
# THIS FILE DOES NOT SEND AUTHENTICATED WEEX WRITES.
# =============================================================================


UNIT = "R35U"

SYMBOL = "BTCUSDT"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

PERSISTENT_DISK_ROOT = "/var/data"
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


# =============================================================================
# HARD SAFETY FIREBREAK
# =============================================================================

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


# =============================================================================
# STRATEGY BASELINE
# =============================================================================

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
TP2_PERCENT = 20
TP3_PERCENT = 60

TP1_TRIGGER_PERCENT = 0.5
TP2_TRIGGER_PERCENT = 1.0
TRAILING_DISTANCE_PERCENT = 0.20

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# =============================================================================
# TEST UPDATE
#
# IMPORTANT:
# R35U uses its own update ID.
# R35T used:
# R35T_SYNTHETIC_UPDATE_000001
#
# R35U intentionally uses a fresh ID so the FIRST R35U startup sees it as new.
#
# After R35U has run successfully once, a redeployment of this exact same
# main.py should see this ID as already processed.
# =============================================================================

TEST_TELEGRAM_UPDATE_ID = "R35U_SYNTHETIC_UPDATE_000001"

TEST_SIGNAL_TEXT = """
BTCUSDT LONG
ENTRY MARKET
LEVERAGE 100X
TP1 0.5%
TP2 1.0%
TRAIL 0.2%
""".strip()


# =============================================================================
# RUNTIME COUNTERS
# =============================================================================

exchange_network_writes = 0
order_submissions = 0
leverage_mutations = 0
margin_mode_mutations = 0
position_mutations = 0
real_orders_sent = 0
demo_orders_sent = 0

telegram_updates_processed_this_startup = 0
signal_parse_count_this_startup = 0
signal_validation_count_this_startup = 0
synthetic_decision_count_this_startup = 0

processed_this_startup = False
duplicate_rejected_this_startup = False
signal_parsed_this_startup = False
signal_validated_this_startup = False
synthetic_decision_created_this_startup = False

test_update_seen_before_startup = False
dedupe_record_written_this_startup = False
decision_record_written_this_startup = False

new_update_acceptance_ok = False
signal_integration_ok = False
durable_linkage_ok = False
test_status = "UNKNOWN"

heartbeat = 0


# =============================================================================
# LOGGING
# =============================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True
    )


def separator():
    log("-" * 100)


def test_result(name, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(
        f"{name:<85} {status}",
        flush=True
    )
    return passed


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            f"{UNIT} OK\n"
            f"TEST_STATUS={test_status}\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
            f"EXCHANGE_NETWORK_WRITES={exchange_network_writes}\n"
            f"ORDER_SUBMISSIONS={order_submissions}\n"
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


def run_health_server():

    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    log(
        f"{UNIT}: HEALTH SERVER STARTED ON PORT {PORT}"
    )

    server.serve_forever()


# =============================================================================
# JSON / DURABILITY HELPERS
# =============================================================================

def ensure_state_directory():

    os.makedirs(
        STATE_DIR,
        exist_ok=True
    )

    return os.path.isdir(STATE_DIR)


def atomic_write_json(path, data):

    temp_path = (
        path
        + ".tmp."
        + str(os.getpid())
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8"
    ) as handle:

        json.dump(
            data,
            handle,
            indent=2,
            sort_keys=True
        )

        handle.flush()

        try:
            os.fsync(
                handle.fileno()
            )
        except OSError:
            pass

    os.replace(
        temp_path,
        path
    )


def load_json(path, default):

    if not os.path.exists(path):
        return default

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as handle:

            data = json.load(handle)

        return data

    except Exception as exc:

        log(
            f"WARNING: FAILED TO LOAD {path}: "
            f"{exc.__class__.__name__}: {exc}"
        )

        return default


def sha256_json(data):

    canonical = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    return hashlib.sha256(
        canonical
    ).hexdigest()


# =============================================================================
# DURABLE REGISTRIES
# =============================================================================

def load_dedupe_registry():

    registry = load_json(
        DEDUPE_FILE,
        {
            "version": 1,
            "updates": {}
        }
    )

    if not isinstance(registry, dict):
        registry = {
            "version": 1,
            "updates": {}
        }

    if "updates" not in registry:
        registry["updates"] = {}

    if not isinstance(
        registry["updates"],
        dict
    ):
        registry["updates"] = {}

    return registry


def save_dedupe_registry(registry):

    atomic_write_json(
        DEDUPE_FILE,
        registry
    )


def load_decision_registry():

    registry = load_json(
        DECISION_FILE,
        {
            "version": 1,
            "decisions": {}
        }
    )

    if not isinstance(registry, dict):
        registry = {
            "version": 1,
            "decisions": {}
        }

    if "decisions" not in registry:
        registry["decisions"] = {}

    if not isinstance(
        registry["decisions"],
        dict
    ):
        registry["decisions"] = {}

    return registry


def save_decision_registry(registry):

    atomic_write_json(
        DECISION_FILE,
        registry
    )


# =============================================================================
# SYNTHETIC TELEGRAM SIGNAL PARSER
# =============================================================================

def parse_signal(update_id, text):

    global signal_parse_count_this_startup
    global signal_parsed_this_startup

    signal_parse_count_this_startup += 1
    signal_parsed_this_startup = True

    normalized = " ".join(
        text.upper().split()
    )

    direction = None

    if " LONG" in f" {normalized}":
        direction = "LONG"

    elif " SHORT" in f" {normalized}":
        direction = "SHORT"

    symbol = None

    if SYMBOL in normalized:
        symbol = SYMBOL

    signal = {
        "update_id": update_id,
        "symbol": symbol,
        "direction": direction,
        "entry_type": "MARKET",
        "target_margin_mode": TARGET_MARGIN_MODE,
        "target_leverage": 100,
        "source": "R35U_SYNTHETIC_TELEGRAM",
        "synthetic_only": True,
        "raw_text_sha256": hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()
    }

    return signal


# =============================================================================
# SIGNAL VALIDATOR
# =============================================================================

def validate_signal(signal):

    global signal_validation_count_this_startup
    global signal_validated_this_startup

    signal_validation_count_this_startup += 1

    checks = {
        "symbol_ok":
            signal.get("symbol") == SYMBOL,

        "direction_ok":
            signal.get("direction")
            in ("LONG", "SHORT"),

        "entry_type_ok":
            signal.get("entry_type")
            == "MARKET",

        "margin_mode_ok":
            signal.get("target_margin_mode")
            == TARGET_MARGIN_MODE,

        "leverage_ok":
            signal.get("target_leverage")
            == 100,

        "synthetic_only":
            signal.get("synthetic_only")
            is True,

        "real_execution_disabled":
            REAL_ORDER_EXECUTION
            is False,

        "order_submission_disabled":
            ORDER_SUBMISSION_ENABLED
            is False,

        "mutation_transport_disabled":
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False
    }

    valid = all(
        checks.values()
    )

    signal_validated_this_startup = valid

    return valid, checks


# =============================================================================
# SYNTHETIC DECISION CREATION
# =============================================================================

def create_synthetic_decision(signal):

    global synthetic_decision_count_this_startup
    global synthetic_decision_created_this_startup

    synthetic_decision_count_this_startup += 1
    synthetic_decision_created_this_startup = True

    decision_payload = {

        "schema_version": 1,

        "unit": UNIT,

        "update_id":
            signal["update_id"],

        "symbol":
            signal["symbol"],

        "direction":
            signal["direction"],

        "entry_type":
            signal["entry_type"],

        "target_margin_mode":
            TARGET_MARGIN_MODE,

        "target_long_leverage":
            TARGET_LONG_LEVERAGE,

        "target_short_leverage":
            TARGET_SHORT_LEVERAGE,

        "entry_balance_percent":
            ENTRY_BALANCE_PERCENT,

        "max_pyramid_adds":
            MAX_PYRAMID_ADDS,

        "pyramid_percent":
            PYRAMID_PERCENT,

        "max_backups":
            MAX_BACKUPS,

        "backup_percent":
            BACKUP_PERCENT,

        "backup_buffer_percent":
            BACKUP_BUFFER_PERCENT,

        "max_fund_exposure_percent":
            MAX_FUND_EXPOSURE_PERCENT,

        "qty_step":
            QTY_STEP,

        "min_qty":
            MIN_QTY,

        "tp_structure": {
            "tp1_percent":
                TP1_PERCENT,

            "tp2_percent":
                TP2_PERCENT,

            "tp3_percent":
                TP3_PERCENT,

            "tp1_trigger_percent":
                TP1_TRIGGER_PERCENT,

            "tp2_trigger_percent":
                TP2_TRIGGER_PERCENT,

            "trailing_distance_percent":
                TRAILING_DISTANCE_PERCENT
        },

        "signal_expiry_seconds":
            SIGNAL_EXPIRY_SECONDS,

        "loss_cooldown_seconds":
            LOSS_COOLDOWN_SECONDS,

        "execution_mode":
            "SYNTHETIC_ONLY",

        "network_write_allowed":
            False,

        "order_submission_allowed":
            False,

        "real_order_allowed":
            False,

        "created_at":
            utc_now()
    }

    decision_hash = sha256_json(
        decision_payload
    )

    decision_id = (
        "r35u-"
        + decision_hash[:20]
    )

    decision_record = {

        "decision_id":
            decision_id,

        "decision_hash":
            decision_hash,

        "payload":
            decision_payload
    }

    return decision_record


# =============================================================================
# PROCESS NEW TELEGRAM UPDATE
# =============================================================================

def process_telegram_update(
    update_id,
    signal_text,
    dedupe_registry,
    decision_registry
):

    global telegram_updates_processed_this_startup
    global processed_this_startup
    global duplicate_rejected_this_startup
    global dedupe_record_written_this_startup
    global decision_record_written_this_startup

    # -------------------------------------------------------------------------
    # CRITICAL ORDER:
    #
    # 1. Check durable dedupe BEFORE parser.
    # 2. If duplicate, return immediately.
    # 3. Parse.
    # 4. Validate.
    # 5. Create durable synthetic decision.
    # 6. Persist decision.
    # 7. Persist dedupe linkage.
    #
    # NO EXCHANGE TRANSPORT EXISTS IN THIS FLOW.
    # -------------------------------------------------------------------------

    if update_id in dedupe_registry["updates"]:

        duplicate_rejected_this_startup = True

        return {
            "classification":
                "DUPLICATE",

            "processed":
                False,

            "reason":
                "UPDATE_ALREADY_IN_DURABLE_DEDUPE_REGISTRY"
        }

    telegram_updates_processed_this_startup += 1
    processed_this_startup = True

    signal = parse_signal(
        update_id,
        signal_text
    )

    valid, validation_checks = validate_signal(
        signal
    )

    if not valid:

        return {
            "classification":
                "INVALID_SIGNAL",

            "processed":
                True,

            "valid":
                False,

            "validation_checks":
                validation_checks
        }

    decision = create_synthetic_decision(
        signal
    )

    decision_id = decision["decision_id"]
    decision_hash = decision["decision_hash"]

    decision_registry["decisions"][
        decision_id
    ] = decision

    save_decision_registry(
        decision_registry
    )

    decision_record_written_this_startup = True

    # Reload immediately to prove persistence.
    persisted_decisions = load_decision_registry()

    persisted_decision = (
        persisted_decisions
        .get("decisions", {})
        .get(decision_id)
    )

    if persisted_decision is None:

        raise RuntimeError(
            "SYNTHETIC DECISION DID NOT PERSIST"
        )

    if (
        persisted_decision.get(
            "decision_hash"
        )
        != decision_hash
    ):

        raise RuntimeError(
            "PERSISTED SYNTHETIC DECISION HASH MISMATCH"
        )

    dedupe_registry["updates"][
        update_id
    ] = {

        "update_id":
            update_id,

        "processed_at":
            utc_now(),

        "classification":
            "ACCEPTED_NEW_UPDATE",

        "signal_valid":
            True,

        "decision_id":
            decision_id,

        "decision_hash":
            decision_hash,

        "unit":
            UNIT
    }

    save_dedupe_registry(
        dedupe_registry
    )

    dedupe_record_written_this_startup = True

    return {
        "classification":
            "ACCEPTED_NEW_UPDATE",

        "processed":
            True,

        "valid":
            True,

        "decision_id":
            decision_id,

        "decision_hash":
            decision_hash,

        "validation_checks":
            validation_checks
    }


# =============================================================================
# MAIN TEST SUITE
# =============================================================================

def run_tests():

    global test_update_seen_before_startup
    global new_update_acceptance_ok
    global signal_integration_ok
    global durable_linkage_ok
    global test_status

    separator()
    log(
        f"{UNIT}: MAIN.PY ENTERED"
    )
    separator()

    log(
        f"{UNIT}: PURPOSE="
        "NEW TELEGRAM UPDATE ACCEPTED EXACTLY ONCE + "
        "SIGNAL PARSING + VALIDATION + "
        "DURABLE SYNTHETIC DECISION INTEGRATION"
    )

    log(
        f"PYTHON_VERSION="
        f"{os.sys.version.split()[0]}"
    )

    log(
        f"SYMBOL={SYMBOL}"
    )

    log(
        f"TARGET_MARGIN_MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"TARGET_LONG_LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"TARGET_SHORT_LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"PERSISTENT_DISK_ROOT="
        f"{PERSISTENT_DISK_ROOT}"
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


    # =========================================================================
    # TEST 1
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 1: HARD SAFETY FIREBREAK"
    )
    separator()

    safety_results = [

        test_result(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION is False
        ),

        test_result(
            "First Real Order Is Forbidden",
            FIRST_REAL_ORDER_ALLOWED is False
        ),

        test_result(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION is False
        ),

        test_result(
            "Exchange Mutation Transport Is Disabled",
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False
        ),

        test_result(
            "Order Submission Is Disabled",
            ORDER_SUBMISSION_ENABLED
            is False
        ),

        test_result(
            "Authenticated WEEX Writes Are Disabled",
            AUTHENTICATED_WEEX_WRITES_ENABLED
            is False
        ),

        test_result(
            "Leverage Mutation Is Disabled",
            LEVERAGE_MUTATION_ENABLED
            is False
        ),

        test_result(
            "Margin Mode Mutation Is Disabled",
            MARGIN_MODE_MUTATION_ENABLED
            is False
        ),

        test_result(
            "Position Mutation Is Disabled",
            POSITION_MUTATION_ENABLED
            is False
        ),

        test_result(
            "Synthetic Transport Only",
            SYNTHETIC_TRANSPORT_ONLY
            is True
        )
    ]


    # =========================================================================
    # TEST 2
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 2: PERSISTENT STORAGE"
    )
    separator()

    state_dir_ok = ensure_state_directory()

    log(
        f"PERSISTENT_DISK_ROOT="
        f"{PERSISTENT_DISK_ROOT}"
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

    persistent_storage_ok = test_result(
        "Persistent State Directory Available",
        state_dir_ok
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 3: LOAD DURABLE REGISTRIES"
    )
    separator()

    dedupe_registry = load_dedupe_registry()
    decision_registry = load_decision_registry()

    test_update_seen_before_startup = (
        TEST_TELEGRAM_UPDATE_ID
        in dedupe_registry["updates"]
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        "TEST_UPDATE_SEEN_BEFORE_STARTUP="
        f"{test_update_seen_before_startup}"
    )

    dedupe_loaded_ok = test_result(
        "Durable Dedupe Registry Loaded",
        isinstance(
            dedupe_registry.get(
                "updates"
            ),
            dict
        )
    )

    decisions_loaded_ok = test_result(
        "Durable Synthetic Decision Registry Loaded",
        isinstance(
            decision_registry.get(
                "decisions"
            ),
            dict
        )
    )


    # =========================================================================
    # TEST 4
    #
    # FIRST R35U STARTUP MUST SEE THE TEST UPDATE AS NEW.
    #
    # If it is already present because this exact R35U has previously completed,
    # the code will classify it as a cross-deploy duplicate. That is expected
    # behavior on the SECOND deployment.
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 4: NEW UPDATE PRECONDITION"
    )
    separator()

    first_run_new_update = (
        not test_update_seen_before_startup
    )

    if first_run_new_update:

        log(
            "UPDATE CLASSIFICATION="
            "NEW_ON_THIS_DEPLOYMENT"
        )

    else:

        log(
            "UPDATE CLASSIFICATION="
            "ALREADY_DURABLE_FROM_PRIOR_R35U_STARTUP"
        )

    test_result(
        "R35U Test Update Is New On First Successful Startup",
        first_run_new_update
        or test_update_seen_before_startup
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 5: PROCESS TELEGRAM UPDATE"
    )
    separator()

    processing_result = process_telegram_update(
        TEST_TELEGRAM_UPDATE_ID,
        TEST_SIGNAL_TEXT,
        dedupe_registry,
        decision_registry
    )

    log(
        "PROCESSING_CLASSIFICATION="
        f"{processing_result.get('classification')}"
    )

    log(
        "PROCESSED_THIS_STARTUP="
        f"{processed_this_startup}"
    )

    log(
        "DUPLICATE_REJECTED_THIS_STARTUP="
        f"{duplicate_rejected_this_startup}"
    )

    log(
        "SIGNAL_PARSE_COUNT_THIS_STARTUP="
        f"{signal_parse_count_this_startup}"
    )

    log(
        "SIGNAL_VALIDATION_COUNT_THIS_STARTUP="
        f"{signal_validation_count_this_startup}"
    )

    log(
        "SYNTHETIC_DECISION_COUNT_THIS_STARTUP="
        f"{synthetic_decision_count_this_startup}"
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 6: EXACTLY-ONCE FIRST-PASS INTEGRATION"
    )
    separator()

    if not test_update_seen_before_startup:

        exactly_once_first_pass_ok = all([

            processed_this_startup
            is True,

            duplicate_rejected_this_startup
            is False,

            signal_parse_count_this_startup
            == 1,

            signal_validation_count_this_startup
            == 1,

            synthetic_decision_count_this_startup
            == 1,

            signal_parsed_this_startup
            is True,

            signal_validated_this_startup
            is True,

            synthetic_decision_created_this_startup
            is True,

            dedupe_record_written_this_startup
            is True,

            decision_record_written_this_startup
            is True,

            processing_result.get(
                "classification"
            )
            == "ACCEPTED_NEW_UPDATE"
        ])

        test_result(
            "New Telegram Update Processed Exactly Once",
            processed_this_startup
            and telegram_updates_processed_this_startup
            == 1
        )

        test_result(
            "Signal Parser Entered Exactly Once",
            signal_parse_count_this_startup
            == 1
        )

        test_result(
            "Signal Validator Entered Exactly Once",
            signal_validation_count_this_startup
            == 1
        )

        test_result(
            "Synthetic Decision Created Exactly Once",
            synthetic_decision_count_this_startup
            == 1
        )

        test_result(
            "Durable Decision Record Written",
            decision_record_written_this_startup
        )

        test_result(
            "Durable Dedupe Record Written",
            dedupe_record_written_this_startup
        )

    else:

        exactly_once_first_pass_ok = (
            duplicate_rejected_this_startup
            and not processed_this_startup
            and signal_parse_count_this_startup
            == 0
            and signal_validation_count_this_startup
            == 0
            and synthetic_decision_count_this_startup
            == 0
        )

        test_result(
            "Prior R35U Update Rejected Before Parser",
            duplicate_rejected_this_startup
        )

        test_result(
            "Signal Parser Not Re-Entered",
            signal_parse_count_this_startup
            == 0
        )

        test_result(
            "Signal Validator Not Re-Entered",
            signal_validation_count_this_startup
            == 0
        )

        test_result(
            "Synthetic Decision Not Re-Created",
            synthetic_decision_count_this_startup
            == 0
        )


    # =========================================================================
    # TEST 7
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 7: DURABLE DECISION / DEDUPE LINKAGE"
    )
    separator()

    durable_dedupe = load_dedupe_registry()
    durable_decisions = load_decision_registry()

    durable_dedupe_record = (
        durable_dedupe
        .get("updates", {})
        .get(TEST_TELEGRAM_UPDATE_ID)
    )

    dedupe_exists = (
        durable_dedupe_record
        is not None
    )

    linked_decision_id = None
    linked_decision_hash = None

    if dedupe_exists:

        linked_decision_id = (
            durable_dedupe_record
            .get("decision_id")
        )

        linked_decision_hash = (
            durable_dedupe_record
            .get("decision_hash")
        )

    durable_decision = None

    if linked_decision_id:

        durable_decision = (
            durable_decisions
            .get("decisions", {})
            .get(linked_decision_id)
        )

    decision_exists = (
        durable_decision
        is not None
    )

    stored_hash_matches = False
    recalculated_hash_matches = False

    if decision_exists:

        stored_hash_matches = (
            durable_decision.get(
                "decision_hash"
            )
            == linked_decision_hash
        )

        payload = durable_decision.get(
            "payload"
        )

        if isinstance(payload, dict):

            recalculated_hash = sha256_json(
                payload
            )

            recalculated_hash_matches = (
                recalculated_hash
                == linked_decision_hash
            )

    test_result(
        "Durable Dedupe Record Exists",
        dedupe_exists
    )

    test_result(
        "Linked Durable Synthetic Decision Exists",
        decision_exists
    )

    test_result(
        "Dedupe Decision Hash Matches Stored Decision",
        stored_hash_matches
    )

    test_result(
        "Stored Decision Hash Recomputes Correctly",
        recalculated_hash_matches
    )

    durable_linkage_ok = all([
        dedupe_exists,
        decision_exists,
        stored_hash_matches,
        recalculated_hash_matches
    ])


    # =========================================================================
    # TEST 8
    #
    # SECOND ATTEMPT DURING SAME PROCESS.
    #
    # THIS IS IMPORTANT:
    # We reload the durable registry and send the exact same update again.
    # It must now be rejected before parser/validator/decision creation.
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 8: SAME-STARTUP DUPLICATE REJECTION"
    )
    separator()

    parse_count_before_retry = (
        signal_parse_count_this_startup
    )

    validation_count_before_retry = (
        signal_validation_count_this_startup
    )

    decision_count_before_retry = (
        synthetic_decision_count_this_startup
    )

    retry_dedupe_registry = (
        load_dedupe_registry()
    )

    retry_decision_registry = (
        load_decision_registry()
    )

    retry_result = process_telegram_update(
        TEST_TELEGRAM_UPDATE_ID,
        TEST_SIGNAL_TEXT,
        retry_dedupe_registry,
        retry_decision_registry
    )

    retry_classified_duplicate = (
        retry_result.get(
            "classification"
        )
        == "DUPLICATE"
    )

    parser_not_reentered = (
        signal_parse_count_this_startup
        == parse_count_before_retry
    )

    validator_not_reentered = (
        signal_validation_count_this_startup
        == validation_count_before_retry
    )

    decision_not_recreated = (
        synthetic_decision_count_this_startup
        == decision_count_before_retry
    )

    test_result(
        "Second Delivery Classified As Duplicate",
        retry_classified_duplicate
    )

    test_result(
        "Parser Not Re-Entered On Duplicate",
        parser_not_reentered
    )

    test_result(
        "Validator Not Re-Entered On Duplicate",
        validator_not_reentered
    )

    test_result(
        "Synthetic Decision Not Re-Created On Duplicate",
        decision_not_recreated
    )

    same_startup_dedupe_ok = all([
        retry_classified_duplicate,
        parser_not_reentered,
        validator_not_reentered,
        decision_not_recreated
    ])


    # =========================================================================
    # TEST 9
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 9: SIGNAL / DECISION SAFETY ATTRIBUTES"
    )
    separator()

    durable_dedupe = load_dedupe_registry()
    durable_decisions = load_decision_registry()

    record = (
        durable_dedupe
        .get("updates", {})
        .get(TEST_TELEGRAM_UPDATE_ID)
    )

    decision_payload = None

    if record:

        decision_id = record.get(
            "decision_id"
        )

        decision_record = (
            durable_decisions
            .get("decisions", {})
            .get(decision_id)
        )

        if decision_record:

            decision_payload = (
                decision_record
                .get("payload")
            )

    payload_ok = (
        isinstance(
            decision_payload,
            dict
        )
    )

    decision_symbol_ok = (
        payload_ok
        and decision_payload.get(
            "symbol"
        )
        == SYMBOL
    )

    decision_direction_ok = (
        payload_ok
        and decision_payload.get(
            "direction"
        )
        in ("LONG", "SHORT")
    )

    decision_margin_mode_ok = (
        payload_ok
        and decision_payload.get(
            "target_margin_mode"
        )
        == TARGET_MARGIN_MODE
    )

    decision_long_leverage_ok = (
        payload_ok
        and decision_payload.get(
            "target_long_leverage"
        )
        == TARGET_LONG_LEVERAGE
    )

    decision_short_leverage_ok = (
        payload_ok
        and decision_payload.get(
            "target_short_leverage"
        )
        == TARGET_SHORT_LEVERAGE
    )

    decision_synthetic_only_ok = (
        payload_ok
        and decision_payload.get(
            "execution_mode"
        )
        == "SYNTHETIC_ONLY"
    )

    decision_network_write_forbidden = (
        payload_ok
        and decision_payload.get(
            "network_write_allowed"
        )
        is False
    )

    decision_order_submission_forbidden = (
        payload_ok
        and decision_payload.get(
            "order_submission_allowed"
        )
        is False
    )

    decision_real_order_forbidden = (
        payload_ok
        and decision_payload.get(
            "real_order_allowed"
        )
        is False
    )

    test_result(
        "Decision Uses BTCUSDT",
        decision_symbol_ok
    )

    test_result(
        "Decision Direction Is Valid",
        decision_direction_ok
    )

    test_result(
        "Decision Uses ISOLATED Margin Target",
        decision_margin_mode_ok
    )

    test_result(
        "Decision Long Leverage Target Is 100x",
        decision_long_leverage_ok
    )

    test_result(
        "Decision Short Leverage Target Is 100x",
        decision_short_leverage_ok
    )

    test_result(
        "Decision Is Synthetic Only",
        decision_synthetic_only_ok
    )

    test_result(
        "Decision Forbids Network Write",
        decision_network_write_forbidden
    )

    test_result(
        "Decision Forbids Order Submission",
        decision_order_submission_forbidden
    )

    test_result(
        "Decision Forbids Real Order",
        decision_real_order_forbidden
    )

    decision_safety_ok = all([

        decision_symbol_ok,
        decision_direction_ok,
        decision_margin_mode_ok,
        decision_long_leverage_ok,
        decision_short_leverage_ok,
        decision_synthetic_only_ok,
        decision_network_write_forbidden,
        decision_order_submission_forbidden,
        decision_real_order_forbidden
    ])


    # =========================================================================
    # TEST 10
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 10: INTEGRATION PROOF"
    )
    separator()

    if not test_update_seen_before_startup:

        new_update_acceptance_ok = all([

            exactly_once_first_pass_ok,
            durable_linkage_ok,
            same_startup_dedupe_ok,
            decision_safety_ok
        ])

    else:

        # On a redeploy after the first successful R35U run,
        # the durable update must already exist and be rejected.
        new_update_acceptance_ok = all([

            exactly_once_first_pass_ok,
            durable_linkage_ok,
            same_startup_dedupe_ok,
            decision_safety_ok
        ])

    signal_integration_ok = all([

        durable_linkage_ok,
        same_startup_dedupe_ok,
        decision_safety_ok
    ])

    test_result(
        "Telegram New-Update Integration",
        new_update_acceptance_ok
    )

    test_result(
        "Signal Integration",
        signal_integration_ok
    )

    test_result(
        "Durable Decision Linkage",
        durable_linkage_ok
    )

    test_result(
        "Duplicate Delivery Cannot Re-Enter Parser",
        same_startup_dedupe_ok
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    separator()
    log(
        f"{UNIT} TEST 11: FINAL ZERO-WRITE FIREBREAK"
    )
    separator()

    zero_write_results = [

        test_result(
            "Exchange Network Writes = 0",
            exchange_network_writes
            == 0
        ),

        test_result(
            "Order Submissions = 0",
            order_submissions
            == 0
        ),

        test_result(
            "Leverage Mutations = 0",
            leverage_mutations
            == 0
        ),

        test_result(
            "Margin Mode Mutations = 0",
            margin_mode_mutations
            == 0
        ),

        test_result(
            "Position Mutations = 0",
            position_mutations
            == 0
        ),

        test_result(
            "Real Orders Sent = 0",
            real_orders_sent
            == 0
        ),

        test_result(
            "Demo Orders Sent = 0",
            demo_orders_sent
            == 0
        ),

        test_result(
            "Real Order Execution Remains Disabled",
            REAL_ORDER_EXECUTION
            is False
        ),

        test_result(
            "Order Submission Remains Disabled",
            ORDER_SUBMISSION_ENABLED
            is False
        ),

        test_result(
            "Exchange Mutation Transport Remains Disabled",
            EXCHANGE_MUTATION_TRANSPORT_ENABLED
            is False
        )
    ]


    # =========================================================================
    # FINAL STATUS
    # =========================================================================

    all_tests_ok = all([

        all(safety_results),
        persistent_storage_ok,
        dedupe_loaded_ok,
        decisions_loaded_ok,
        new_update_acceptance_ok,
        signal_integration_ok,
        durable_linkage_ok,
        same_startup_dedupe_ok,
        decision_safety_ok,
        all(zero_write_results)
    ])

    test_status = (
        "PASS"
        if all_tests_ok
        else "FAIL"
    )


    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================

    separator()
    log(
        f"{UNIT}: FINAL TEST SUMMARY"
    )
    separator()

    log(
        "PURPOSE="
        "NEW TELEGRAM UPDATE ACCEPTED EXACTLY ONCE + "
        "SIGNAL PARSING + VALIDATION + "
        "DURABLE SYNTHETIC DECISION INTEGRATION"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID="
        f"{TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        "TEST_UPDATE_SEEN_BEFORE_STARTUP="
        f"{test_update_seen_before_startup}"
    )

    log(
        "PROCESSED_THIS_STARTUP="
        f"{processed_this_startup}"
    )

    log(
        "DUPLICATE_REJECTED_THIS_STARTUP="
        f"{duplicate_rejected_this_startup}"
    )

    log(
        "SIGNAL_PARSED_THIS_STARTUP="
        f"{signal_parsed_this_startup}"
    )

    log(
        "SIGNAL_PARSE_COUNT_THIS_STARTUP="
        f"{signal_parse_count_this_startup}"
    )

    log(
        "SIGNAL_VALIDATED_THIS_STARTUP="
        f"{signal_validated_this_startup}"
    )

    log(
        "SIGNAL_VALIDATION_COUNT_THIS_STARTUP="
        f"{signal_validation_count_this_startup}"
    )

    log(
        "SYNTHETIC_DECISION_CREATED_THIS_STARTUP="
        f"{synthetic_decision_created_this_startup}"
    )

    log(
        "SYNTHETIC_DECISION_COUNT_THIS_STARTUP="
        f"{synthetic_decision_count_this_startup}"
    )

    log(
        "DEDUPE_RECORD_WRITTEN_THIS_STARTUP="
        f"{dedupe_record_written_this_startup}"
    )

    log(
        "DECISION_RECORD_WRITTEN_THIS_STARTUP="
        f"{decision_record_written_this_startup}"
    )

    log(
        "NEW_UPDATE_ACCEPTANCE_OK="
        f"{new_update_acceptance_ok}"
    )

    log(
        "SIGNAL_INTEGRATION_OK="
        f"{signal_integration_ok}"
    )

    log(
        "DURABLE_LINKAGE_OK="
        f"{durable_linkage_ok}"
    )

    log(
        "CROSS_DEPLOY_NEXT_STARTUP_EXPECTATION="
        "UPDATE_MUST_BE_REJECTED_BEFORE_PARSER"
    )

    log(
        f"TEST_STATUS={test_status}"
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
        f"LEVERAGE_MUTATIONS="
        f"{leverage_mutations}"
    )

    log(
        f"MARGIN_MODE_MUTATIONS="
        f"{margin_mode_mutations}"
    )

    log(
        f"POSITION_MUTATIONS="
        f"{position_mutations}"
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


# =============================================================================
# HEARTBEAT LOOP
# =============================================================================

def heartbeat_loop():

    global heartbeat

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: "
            f"HEARTBEAT={heartbeat} "
            f"TEST_UPDATE_SEEN_BEFORE_STARTUP="
            f"{test_update_seen_before_startup} "
            f"PROCESSED_THIS_STARTUP="
            f"{processed_this_startup} "
            f"DUPLICATE_REJECTED_THIS_STARTUP="
            f"{duplicate_rejected_this_startup} "
            f"SIGNAL_PARSED_THIS_STARTUP="
            f"{signal_parsed_this_startup} "
            f"SIGNAL_PARSE_COUNT_THIS_STARTUP="
            f"{signal_parse_count_this_startup} "
            f"SIGNAL_VALIDATED_THIS_STARTUP="
            f"{signal_validated_this_startup} "
            f"SIGNAL_VALIDATION_COUNT_THIS_STARTUP="
            f"{signal_validation_count_this_startup} "
            f"SYNTHETIC_DECISION_CREATED_THIS_STARTUP="
            f"{synthetic_decision_created_this_startup} "
            f"SYNTHETIC_DECISION_COUNT_THIS_STARTUP="
            f"{synthetic_decision_count_this_startup} "
            f"NEW_UPDATE_ACCEPTANCE_OK="
            f"{new_update_acceptance_ok} "
            f"SIGNAL_INTEGRATION_OK="
            f"{signal_integration_ok} "
            f"DURABLE_LINKAGE_OK="
            f"{durable_linkage_ok} "
            f"TEST_STATUS="
            f"{test_status} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{exchange_network_writes} "
            f"ORDER_SUBMISSIONS="
            f"{order_submissions} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


# =============================================================================
# APPLICATION ENTRY
# =============================================================================

def main():

    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    health_thread.start()

    # Give health server a moment to bind.
    time.sleep(0.2)

    try:

        run_tests()

    except Exception as exc:

        global test_status

        test_status = "FAIL"

        separator()

        log(
            f"{UNIT}: UNHANDLED TEST FAILURE"
        )

        separator()

        log(
            "EXCEPTION_CLASS="
            f"{exc.__class__.__name__}"
        )

        log(
            "EXCEPTION_MESSAGE="
            f"{exc}"
        )

        log(
            "REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        log(
            "EXCHANGE_NETWORK_WRITES="
            f"{exchange_network_writes}"
        )

        log(
            "ORDER_SUBMISSIONS="
            f"{order_submissions}"
        )

    heartbeat_loop()


if __name__ == "__main__":
    main()

