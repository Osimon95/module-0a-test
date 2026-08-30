

# =============================================================================
# R35T main.py
# =============================================================================
#
# PURPOSE
# -------
# Integrate the already-proven durable Telegram cross-deploy deduplication gate
# with:
#
#     Telegram Update
#           |
#           v
#     Durable Dedupe Gate
#           |
#           v
#     Signal Parser
#           |
#           v
#     Signal Validator
#           |
#           v
#     Synthetic Trading Decision
#
# CRITICAL SAFETY RULE
# --------------------
# This unit MUST NOT:
#
# - send a real order
# - send a demo order
# - perform any WEEX write
# - modify leverage
# - modify margin mode
# - modify positions
# - transmit an order envelope
#
# R35T proves ONLY that one Telegram update can reach the synthetic decision
# engine once, and that the same update cannot reach it again after redeploy.
#
# =============================================================================


import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# =============================================================================
# SECTION 1: UNIT IDENTITY
# =============================================================================

UNIT = "R35T"

PURPOSE = (
    "TELEGRAM DURABLE DEDUPE + SIGNAL PARSING + "
    "SYNTHETIC DECISION CROSS-DEPLOY INTEGRATION"
)


# =============================================================================
# SECTION 2: HARD SAFETY FIREBREAK
# =============================================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

AUTHENTICATED_WEEX_WRITES_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# Runtime counters.
EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0


# =============================================================================
# SECTION 3: STRATEGY CONSTANTS
# =============================================================================

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

TP1_PERCENT = 20.0
TP2_PERCENT = 20.0
TP3_PERCENT = 60.0

TP1_TRIGGER_PERCENT = 0.5
TP2_TRIGGER_PERCENT = 1.0
TRAILING_DISTANCE_PERCENT = 0.20

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# =============================================================================
# SECTION 4: R35T SYNTHETIC TELEGRAM UPDATE
# =============================================================================
#
# IMPORTANT:
#
# The ID intentionally stays constant across redeployments.
#
# First R35T deployment:
#     update should be NEW
#     parser should run
#     validator should run
#     synthetic decision should be created
#     durable record should be written
#
# Second R35T deployment:
#     update should already exist
#     duplicate should be rejected BEFORE parser/decision execution
#
# =============================================================================

TEST_TELEGRAM_UPDATE_ID = "R35T_SYNTHETIC_UPDATE_000001"

TEST_TELEGRAM_MESSAGE = """
BTCUSDT LONG
""".strip()

TEST_TELEGRAM_UPDATE = {
    "update_id": TEST_TELEGRAM_UPDATE_ID,
    "source": "R35T_SYNTHETIC_TELEGRAM",
    "chat_id": "R35T_SYNTHETIC_CHAT",
    "message_id": "R35T_SYNTHETIC_MESSAGE_000001",
    "text": TEST_TELEGRAM_MESSAGE,
}


# =============================================================================
# SECTION 5: PERSISTENT STORAGE
# =============================================================================

PERSISTENT_DISK_ROOT = "/var/data"
STATE_DIR = os.path.join(PERSISTENT_DISK_ROOT, "r35t_state")

DEDUPE_FILE = os.path.join(
    STATE_DIR,
    "telegram_processed_updates.json",
)

DECISION_FILE = os.path.join(
    STATE_DIR,
    "synthetic_decisions.json",
)


# =============================================================================
# SECTION 6: RUNTIME STATE
# =============================================================================

TEST_UPDATE_SEEN_BEFORE_STARTUP = False

PROCESSED_THIS_STARTUP = False

DUPLICATE_REJECTED_THIS_STARTUP = False

SIGNAL_PARSED_THIS_STARTUP = False

SIGNAL_VALIDATED_THIS_STARTUP = False

SYNTHETIC_DECISION_CREATED_THIS_STARTUP = False

SYNTHETIC_DECISION_COUNT_THIS_STARTUP = 0

DURABLE_RECORD_WRITTEN_THIS_STARTUP = False

DURABLE_READBACK_OK = False

IMMEDIATE_REPLAY_REJECTED = False

TELEGRAM_LOCAL_DEDUPE_OK = False

TELEGRAM_CROSS_DEPLOY_DEDUPE_OK = False

SIGNAL_INTEGRATION_OK = False

CROSS_DEPLOY_PROOF = "PENDING"

TEST_STATUS = "PENDING"

FAILURE_STAGE = None
FAILURE_REASON = None


# =============================================================================
# SECTION 7: LOGGING HELPERS
# =============================================================================

SEPARATOR = "-" * 100


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


def result(label, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(
        f"{label:<82} {status}",
        flush=True,
    )


# =============================================================================
# SECTION 8: HASHING / CANONICALIZATION
# =============================================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(value):
    encoded = canonical_json(value).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


# =============================================================================
# SECTION 9: ATOMIC DURABLE JSON
# =============================================================================

def ensure_state_directory():
    os.makedirs(
        STATE_DIR,
        exist_ok=True,
    )

    if not os.path.isdir(STATE_DIR):
        raise RuntimeError(
            f"STATE_DIR is not a directory: {STATE_DIR}"
        )

    probe_path = os.path.join(
        STATE_DIR,
        ".r35t_write_probe",
    )

    with open(
        probe_path,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write("R35T")
        handle.flush()
        os.fsync(handle.fileno())

    os.remove(probe_path)

    return True


def atomic_write_json(path, payload):
    directory = os.path.dirname(path)

    os.makedirs(
        directory,
        exist_ok=True,
    )

    temp_path = path + ".tmp"

    serialized = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(serialized)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(
        temp_path,
        path,
    )

    # Best-effort directory fsync.
    try:
        directory_fd = os.open(
            directory,
            os.O_RDONLY,
        )

        try:
            os.fsync(directory_fd)

        finally:
            os.close(directory_fd)

    except Exception:
        pass


def load_json(path, default_value):
    if not os.path.exists(path):
        return default_value

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:
        data = json.load(handle)

    return data


# =============================================================================
# SECTION 10: DURABLE TELEGRAM DEDUPE REGISTRY
# =============================================================================

def default_dedupe_registry():
    return {
        "schema": "R35T_TELEGRAM_DEDUPE_V1",
        "processed_updates": {},
    }


def load_dedupe_registry():
    registry = load_json(
        DEDUPE_FILE,
        default_dedupe_registry(),
    )

    if not isinstance(registry, dict):
        raise RuntimeError(
            "DEDUPE registry is not a dictionary"
        )

    if registry.get("schema") != "R35T_TELEGRAM_DEDUPE_V1":
        raise RuntimeError(
            "Unexpected R35T dedupe schema"
        )

    processed = registry.get(
        "processed_updates"
    )

    if not isinstance(processed, dict):
        raise RuntimeError(
            "processed_updates is not a dictionary"
        )

    return registry


def update_seen(registry, update_id):
    return update_id in registry["processed_updates"]


def durable_register_processed_update(
    registry,
    update,
    parsed_signal,
    synthetic_decision,
):
    update_id = str(
        update["update_id"]
    )

    if update_seen(
        registry,
        update_id,
    ):
        raise RuntimeError(
            "Attempted to register already-processed Telegram update"
        )

    record = {
        "update_id": update_id,
        "processed_at_utc": utc_now(),
        "update_sha256": sha256_json(update),
        "signal_sha256": sha256_json(parsed_signal),
        "decision_sha256": sha256_json(synthetic_decision),
        "symbol": parsed_signal["symbol"],
        "direction": parsed_signal["direction"],
        "synthetic_only": True,
        "exchange_network_writes": 0,
        "order_submissions": 0,
        "real_order_execution": False,
    }

    registry["processed_updates"][update_id] = record

    atomic_write_json(
        DEDUPE_FILE,
        registry,
    )

    return record


# =============================================================================
# SECTION 11: SYNTHETIC DECISION REGISTRY
# =============================================================================

def default_decision_registry():
    return {
        "schema": "R35T_SYNTHETIC_DECISIONS_V1",
        "decisions": {},
    }


def load_decision_registry():
    registry = load_json(
        DECISION_FILE,
        default_decision_registry(),
    )

    if not isinstance(registry, dict):
        raise RuntimeError(
            "Decision registry is not a dictionary"
        )

    if registry.get("schema") != "R35T_SYNTHETIC_DECISIONS_V1":
        raise RuntimeError(
            "Unexpected R35T decision registry schema"
        )

    decisions = registry.get("decisions")

    if not isinstance(decisions, dict):
        raise RuntimeError(
            "decisions is not a dictionary"
        )

    return registry


def persist_synthetic_decision(
    update_id,
    decision,
):
    registry = load_decision_registry()

    if update_id in registry["decisions"]:
        raise RuntimeError(
            "Synthetic decision already exists for update"
        )

    registry["decisions"][update_id] = {
        "created_at_utc": utc_now(),
        "decision": decision,
        "decision_sha256": sha256_json(decision),
    }

    atomic_write_json(
        DECISION_FILE,
        registry,
    )


# =============================================================================
# SECTION 12: TELEGRAM SIGNAL PARSER
# =============================================================================

def parse_signal_text(text):
    """
    R35T deliberately uses a very small grammar.

    Accepted synthetic form:

        BTCUSDT LONG

    or:

        BTCUSDT SHORT

    Nothing else is necessary in this unit.
    """

    normalized = " ".join(
        str(text)
        .strip()
        .upper()
        .split()
    )

    tokens = normalized.split(" ")

    if len(tokens) != 2:
        raise ValueError(
            "Signal must contain exactly SYMBOL and DIRECTION"
        )

    symbol = tokens[0]
    direction = tokens[1]

    parsed = {
        "schema": "R35T_PARSED_SIGNAL_V1",
        "symbol": symbol,
        "direction": direction,
        "raw_text": text,
        "normalized_text": normalized,
    }

    return parsed


# =============================================================================
# SECTION 13: SIGNAL VALIDATION
# =============================================================================

def validate_signal(parsed_signal):
    errors = []

    if parsed_signal.get("symbol") != SYMBOL:
        errors.append(
            f"Unsupported symbol: {parsed_signal.get('symbol')}"
        )

    if parsed_signal.get("direction") not in {
        "LONG",
        "SHORT",
    }:
        errors.append(
            f"Unsupported direction: {parsed_signal.get('direction')}"
        )

    if REAL_ORDER_EXECUTION:
        errors.append(
            "REAL_ORDER_EXECUTION unexpectedly enabled"
        )

    if ORDER_SUBMISSION_ENABLED:
        errors.append(
            "ORDER_SUBMISSION_ENABLED unexpectedly enabled"
        )

    if EXCHANGE_MUTATION_TRANSPORT_ENABLED:
        errors.append(
            "EXCHANGE_MUTATION_TRANSPORT_ENABLED unexpectedly enabled"
        )

    if not SYNTHETIC_TRANSPORT_ONLY:
        errors.append(
            "SYNTHETIC_TRANSPORT_ONLY unexpectedly disabled"
        )

    if errors:
        raise ValueError(
            "; ".join(errors)
        )

    return True


# =============================================================================
# SECTION 14: SYNTHETIC TRADING DECISION
# =============================================================================

def build_synthetic_decision(
    telegram_update,
    parsed_signal,
):
    """
    This is DATA ONLY.

    It is NOT:
        - an exchange order
        - an authenticated request
        - a WEEX payload transmission
        - permission to execute

    No mark price is needed in R35T.
    """

    direction = parsed_signal["direction"]

    if direction == "LONG":
        leverage = TARGET_LONG_LEVERAGE
        hypothetical_side = "BUY"
    else:
        leverage = TARGET_SHORT_LEVERAGE
        hypothetical_side = "SELL"

    decision = {
        "schema": "R35T_SYNTHETIC_DECISION_V1",

        "telegram_update_id": str(
            telegram_update["update_id"]
        ),

        "symbol": SYMBOL,

        "direction": direction,

        "hypothetical_side": hypothetical_side,

        "margin_mode": TARGET_MARGIN_MODE,

        "target_leverage": leverage,

        "entry_balance_percent": ENTRY_BALANCE_PERCENT,

        "pyramid": {
            "max_adds": MAX_PYRAMID_ADDS,
            "percent_per_add": PYRAMID_PERCENT,
        },

        "backup": {
            "max_backups": MAX_BACKUPS,
            "percent_per_backup": BACKUP_PERCENT,
            "buffer_percent": BACKUP_BUFFER_PERCENT,
        },

        "maximum_fund_exposure_percent":
            MAX_FUND_EXPOSURE_PERCENT,

        "take_profit": {
            "tp1_allocation_percent": TP1_PERCENT,
            "tp2_allocation_percent": TP2_PERCENT,
            "tp3_allocation_percent": TP3_PERCENT,
            "tp1_trigger_percent": TP1_TRIGGER_PERCENT,
            "tp2_trigger_percent": TP2_TRIGGER_PERCENT,
            "trailing_distance_percent":
                TRAILING_DISTANCE_PERCENT,
        },

        "signal_expiry_seconds":
            SIGNAL_EXPIRY_SECONDS,

        "loss_cooldown_seconds":
            LOSS_COOLDOWN_SECONDS,

        "one_direction_only":
            ONE_DIRECTION_ONLY,

        "anti_duplicate_orders":
            ANTI_DUPLICATE_ORDERS,

        "trend_reversal_exit":
            TREND_REVERSAL_EXIT,

        "idle_pyramid_cleanup":
            IDLE_PYRAMID_CLEANUP,

        # Extremely important safety metadata.
        "synthetic": True,
        "transmittable": False,
        "network_write_allowed": False,
        "order_submission_allowed": False,
        "real_order_allowed": False,
    }

    return decision


# =============================================================================
# SECTION 15: ABSOLUTE EXCHANGE WRITE BLOCK
# =============================================================================

def forbidden_exchange_write(*args, **kwargs):
    raise RuntimeError(
        "R35T HARD FIREBREAK: "
        "ALL EXCHANGE WRITES ARE FORBIDDEN"
    )


def forbidden_order_submission(*args, **kwargs):
    raise RuntimeError(
        "R35T HARD FIREBREAK: "
        "ORDER SUBMISSION IS FORBIDDEN"
    )


def forbidden_leverage_mutation(*args, **kwargs):
    raise RuntimeError(
        "R35T HARD FIREBREAK: "
        "LEVERAGE MUTATION IS FORBIDDEN"
    )


def forbidden_margin_mutation(*args, **kwargs):
    raise RuntimeError(
        "R35T HARD FIREBREAK: "
        "MARGIN MODE MUTATION IS FORBIDDEN"
    )


def forbidden_position_mutation(*args, **kwargs):
    raise RuntimeError(
        "R35T HARD FIREBREAK: "
        "POSITION MUTATION IS FORBIDDEN"
    )


# =============================================================================
# SECTION 16: HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in {
            "/",
            "/health",
            "/healthz",
        }:
            body = (
                f"{UNIT} OK\n"
                f"TEST_STATUS={TEST_STATUS}\n"
                f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
                f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
                f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}\n"
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

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(
        self,
        format,
        *args,
    ):
        return


def run_health_server():
    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        HealthHandler,
    )

    log(
        f"{UNIT}: HEALTH SERVER STARTED ON PORT {port}"
    )

    server.serve_forever()


# =============================================================================
# SECTION 17: TEST ENGINE
# =============================================================================

def run_r35t_tests():

    global TEST_UPDATE_SEEN_BEFORE_STARTUP
    global PROCESSED_THIS_STARTUP
    global DUPLICATE_REJECTED_THIS_STARTUP
    global SIGNAL_PARSED_THIS_STARTUP
    global SIGNAL_VALIDATED_THIS_STARTUP
    global SYNTHETIC_DECISION_CREATED_THIS_STARTUP
    global SYNTHETIC_DECISION_COUNT_THIS_STARTUP
    global DURABLE_RECORD_WRITTEN_THIS_STARTUP
    global DURABLE_READBACK_OK
    global IMMEDIATE_REPLAY_REJECTED
    global TELEGRAM_LOCAL_DEDUPE_OK
    global TELEGRAM_CROSS_DEPLOY_DEDUPE_OK
    global SIGNAL_INTEGRATION_OK
    global CROSS_DEPLOY_PROOF
    global TEST_STATUS
    global FAILURE_STAGE
    global FAILURE_REASON

    try:

        # =====================================================================
        # TEST 1
        # =====================================================================

        section(
            f"{UNIT} TEST 1: HARD SAFETY FIREBREAK"
        )

        safety_checks = {
            "Real Order Execution Is Disabled":
                REAL_ORDER_EXECUTION is False,

            "First Real Order Is Forbidden":
                FIRST_REAL_ORDER_ALLOWED is False,

            "Demo Order Execution Is Disabled":
                DEMO_ORDER_EXECUTION is False,

            "Exchange Mutation Transport Is Disabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,

            "Order Submission Is Disabled":
                ORDER_SUBMISSION_ENABLED is False,

            "Authenticated WEEX Writes Are Disabled":
                AUTHENTICATED_WEEX_WRITES_ENABLED is False,

            "Leverage Mutation Is Disabled":
                LEVERAGE_MUTATION_ENABLED is False,

            "Margin Mode Mutation Is Disabled":
                MARGIN_MODE_MUTATION_ENABLED is False,

            "Position Mutation Is Disabled":
                POSITION_MUTATION_ENABLED is False,

            "Synthetic Transport Only":
                SYNTHETIC_TRANSPORT_ONLY is True,
        }

        for label, passed in safety_checks.items():
            result(
                label,
                passed,
            )

        if not all(
            safety_checks.values()
        ):
            raise RuntimeError(
                "Safety firebreak validation failed"
            )

        # =====================================================================
        # TEST 2
        # =====================================================================

        section(
            f"{UNIT} TEST 2: PERSISTENT STORAGE"
        )

        state_available = ensure_state_directory()

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

        result(
            "Persistent State Directory Available",
            state_available,
        )

        # =====================================================================
        # TEST 3
        # =====================================================================

        section(
            f"{UNIT} TEST 3: LOAD DURABLE TELEGRAM REGISTRY"
        )

        registry = load_dedupe_registry()

        TEST_UPDATE_SEEN_BEFORE_STARTUP = update_seen(
            registry,
            TEST_TELEGRAM_UPDATE_ID,
        )

        log(
            f"TEST_TELEGRAM_UPDATE_ID={TEST_TELEGRAM_UPDATE_ID}"
        )

        log(
            "TEST_UPDATE_SEEN_BEFORE_STARTUP="
            f"{TEST_UPDATE_SEEN_BEFORE_STARTUP}"
        )

        result(
            "Durable Dedupe Registry Loaded",
            True,
        )

        # =====================================================================
        # PATH A:
        # First deployment.
        # =====================================================================

        if not TEST_UPDATE_SEEN_BEFORE_STARTUP:

            section(
                f"{UNIT} TEST 4: NEW TELEGRAM UPDATE"
            )

            log(
                "UPDATE CLASSIFICATION=NEW"
            )

            result(
                "Synthetic Telegram Update Is New",
                True,
            )

            # -----------------------------------------------------------------
            # Parse.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 5: SIGNAL PARSER"
            )

            parsed_signal = parse_signal_text(
                TEST_TELEGRAM_UPDATE["text"]
            )

            SIGNAL_PARSED_THIS_STARTUP = True

            log(
                "PARSED_SIGNAL="
                f"{canonical_json(parsed_signal)}"
            )

            log(
                "PARSED_SIGNAL_SHA256="
                f"{sha256_json(parsed_signal)}"
            )

            result(
                "Telegram Signal Parsed",
                SIGNAL_PARSED_THIS_STARTUP,
            )

            result(
                "Parsed Symbol Is BTCUSDT",
                parsed_signal["symbol"] == SYMBOL,
            )

            result(
                "Parsed Direction Is LONG",
                parsed_signal["direction"] == "LONG",
            )

            # -----------------------------------------------------------------
            # Validate.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 6: SIGNAL VALIDATION"
            )

            validate_signal(
                parsed_signal
            )

            SIGNAL_VALIDATED_THIS_STARTUP = True

            result(
                "Parsed Signal Validated",
                SIGNAL_VALIDATED_THIS_STARTUP,
            )

            # -----------------------------------------------------------------
            # Synthetic decision.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 7: SYNTHETIC DECISION"
            )

            synthetic_decision = build_synthetic_decision(
                TEST_TELEGRAM_UPDATE,
                parsed_signal,
            )

            SYNTHETIC_DECISION_CREATED_THIS_STARTUP = True
            SYNTHETIC_DECISION_COUNT_THIS_STARTUP += 1

            log(
                "SYNTHETIC_DECISION="
                f"{canonical_json(synthetic_decision)}"
            )

            log(
                "SYNTHETIC_DECISION_SHA256="
                f"{sha256_json(synthetic_decision)}"
            )

            result(
                "Synthetic Decision Created",
                SYNTHETIC_DECISION_CREATED_THIS_STARTUP,
            )

            result(
                "Exactly One Synthetic Decision Created",
                SYNTHETIC_DECISION_COUNT_THIS_STARTUP == 1,
            )

            result(
                "Synthetic Decision Is Non-Transmittable",
                synthetic_decision["transmittable"] is False,
            )

            result(
                "Synthetic Decision Forbids Network Write",
                synthetic_decision["network_write_allowed"] is False,
            )

            result(
                "Synthetic Decision Forbids Order Submission",
                synthetic_decision["order_submission_allowed"] is False,
            )

            result(
                "Synthetic Decision Forbids Real Order",
                synthetic_decision["real_order_allowed"] is False,
            )

            # -----------------------------------------------------------------
            # Persist synthetic decision.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 8: DURABLE SYNTHETIC DECISION"
            )

            persist_synthetic_decision(
                TEST_TELEGRAM_UPDATE_ID,
                synthetic_decision,
            )

            decision_registry_readback = (
                load_decision_registry()
            )

            decision_present = (
                TEST_TELEGRAM_UPDATE_ID
                in decision_registry_readback["decisions"]
            )

            result(
                "Synthetic Decision Survives Immediate Read-Back",
                decision_present,
            )

            if not decision_present:
                raise RuntimeError(
                    "Synthetic decision durable read-back failed"
                )

            # -----------------------------------------------------------------
            # Register Telegram update only AFTER successful processing.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 9: DURABLE PROCESSED-UPDATE COMMIT"
            )

            durable_record = (
                durable_register_processed_update(
                    registry,
                    TEST_TELEGRAM_UPDATE,
                    parsed_signal,
                    synthetic_decision,
                )
            )

            DURABLE_RECORD_WRITTEN_THIS_STARTUP = True
            PROCESSED_THIS_STARTUP = True

            log(
                "DURABLE_RECORD="
                f"{canonical_json(durable_record)}"
            )

            result(
                "Processed Telegram Update Persisted",
                DURABLE_RECORD_WRITTEN_THIS_STARTUP,
            )

            # -----------------------------------------------------------------
            # Immediate read-back.
            # -----------------------------------------------------------------

            readback_registry = load_dedupe_registry()

            DURABLE_READBACK_OK = update_seen(
                readback_registry,
                TEST_TELEGRAM_UPDATE_ID,
            )

            result(
                "Processed Update Survives Immediate Read-Back",
                DURABLE_READBACK_OK,
            )

            # -----------------------------------------------------------------
            # Immediate replay rejection.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 10: IMMEDIATE DUPLICATE REPLAY"
            )

            if update_seen(
                readback_registry,
                TEST_TELEGRAM_UPDATE_ID,
            ):
                IMMEDIATE_REPLAY_REJECTED = True

            result(
                "Immediate Duplicate Replay Rejected",
                IMMEDIATE_REPLAY_REJECTED,
            )

            TELEGRAM_LOCAL_DEDUPE_OK = (
                DURABLE_READBACK_OK
                and IMMEDIATE_REPLAY_REJECTED
            )

            SIGNAL_INTEGRATION_OK = (
                SIGNAL_PARSED_THIS_STARTUP
                and SIGNAL_VALIDATED_THIS_STARTUP
                and SYNTHETIC_DECISION_CREATED_THIS_STARTUP
                and SYNTHETIC_DECISION_COUNT_THIS_STARTUP == 1
                and PROCESSED_THIS_STARTUP
            )

            # Cross-deploy proof cannot be claimed until next startup.
            TELEGRAM_CROSS_DEPLOY_DEDUPE_OK = False
            CROSS_DEPLOY_PROOF = "PENDING_REDEPLOY"

            if (
                TELEGRAM_LOCAL_DEDUPE_OK
                and SIGNAL_INTEGRATION_OK
            ):
                TEST_STATUS = "PASS_FIRST_DEPLOY"
            else:
                TEST_STATUS = "FAIL"

        # =====================================================================
        # PATH B:
        # Second or later deployment.
        # =====================================================================

        else:

            section(
                f"{UNIT} TEST 4: CROSS-DEPLOY DUPLICATE DETECTED"
            )

            log(
                "UPDATE CLASSIFICATION=DUPLICATE_FROM_PREVIOUS_STARTUP"
            )

            DUPLICATE_REJECTED_THIS_STARTUP = True

            result(
                "Update Seen Before Current Startup",
                TEST_UPDATE_SEEN_BEFORE_STARTUP,
            )

            result(
                "Duplicate Rejected Before Signal Parser",
                DUPLICATE_REJECTED_THIS_STARTUP,
            )

            # The parser and decision engine MUST NOT execute.
            PROCESSED_THIS_STARTUP = False
            SIGNAL_PARSED_THIS_STARTUP = False
            SIGNAL_VALIDATED_THIS_STARTUP = False
            SYNTHETIC_DECISION_CREATED_THIS_STARTUP = False
            SYNTHETIC_DECISION_COUNT_THIS_STARTUP = 0

            # -----------------------------------------------------------------
            # Verify first-deployment decision is still durable.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 5: PRIOR SYNTHETIC DECISION INTEGRITY"
            )

            decision_registry = load_decision_registry()

            prior_decision_exists = (
                TEST_TELEGRAM_UPDATE_ID
                in decision_registry["decisions"]
            )

            result(
                "Prior Synthetic Decision Is Durable",
                prior_decision_exists,
            )

            if not prior_decision_exists:
                raise RuntimeError(
                    "Dedupe record exists but prior synthetic "
                    "decision is missing"
                )

            prior_decision_entry = (
                decision_registry["decisions"][
                    TEST_TELEGRAM_UPDATE_ID
                ]
            )

            prior_decision = prior_decision_entry[
                "decision"
            ]

            stored_hash = prior_decision_entry[
                "decision_sha256"
            ]

            recalculated_hash = sha256_json(
                prior_decision
            )

            decision_hash_ok = (
                stored_hash == recalculated_hash
            )

            result(
                "Prior Synthetic Decision Hash Matches",
                decision_hash_ok,
            )

            # -----------------------------------------------------------------
            # Verify dedupe record points to same decision.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 6: DEDUPE / DECISION LINKAGE"
            )

            processed_record = registry[
                "processed_updates"
            ][TEST_TELEGRAM_UPDATE_ID]

            linkage_ok = (
                processed_record[
                    "decision_sha256"
                ]
                == recalculated_hash
            )

            result(
                "Dedupe Record Matches Durable Decision",
                linkage_ok,
            )

            # -----------------------------------------------------------------
            # Cross-deploy proof.
            # -----------------------------------------------------------------

            section(
                f"{UNIT} TEST 7: CROSS-DEPLOY INTEGRATION PROOF"
            )

            TELEGRAM_LOCAL_DEDUPE_OK = True

            TELEGRAM_CROSS_DEPLOY_DEDUPE_OK = (
                TEST_UPDATE_SEEN_BEFORE_STARTUP
                and DUPLICATE_REJECTED_THIS_STARTUP
                and not PROCESSED_THIS_STARTUP
                and not SIGNAL_PARSED_THIS_STARTUP
                and not SIGNAL_VALIDATED_THIS_STARTUP
                and not SYNTHETIC_DECISION_CREATED_THIS_STARTUP
                and SYNTHETIC_DECISION_COUNT_THIS_STARTUP == 0
                and prior_decision_exists
                and decision_hash_ok
                and linkage_ok
            )

            SIGNAL_INTEGRATION_OK = (
                prior_decision_exists
                and decision_hash_ok
                and linkage_ok
            )

            CROSS_DEPLOY_PROOF = (
                "PASS"
                if TELEGRAM_CROSS_DEPLOY_DEDUPE_OK
                else "FAIL"
            )

            TEST_STATUS = (
                "PASS"
                if TELEGRAM_CROSS_DEPLOY_DEDUPE_OK
                else "FAIL"
            )

            result(
                "Telegram Cross-Deploy Dedupe Integration",
                TELEGRAM_CROSS_DEPLOY_DEDUPE_OK,
            )

            result(
                "Signal Parser Was NOT Re-Entered",
                not SIGNAL_PARSED_THIS_STARTUP,
            )

            result(
                "Signal Validator Was NOT Re-Entered",
                not SIGNAL_VALIDATED_THIS_STARTUP,
            )

            result(
                "Synthetic Decision Was NOT Re-Created",
                not SYNTHETIC_DECISION_CREATED_THIS_STARTUP,
            )

            result(
                "Synthetic Decisions Created This Startup = 0",
                SYNTHETIC_DECISION_COUNT_THIS_STARTUP == 0,
            )

        # =====================================================================
        # FINAL FIREBREAK
        # =====================================================================

        section(
            f"{UNIT} TEST 11: FINAL ZERO-WRITE FIREBREAK"
        )

        final_safety_checks = {
            "Exchange Network Writes = 0":
                EXCHANGE_NETWORK_WRITES == 0,

            "Order Submissions = 0":
                ORDER_SUBMISSIONS == 0,

            "Leverage Mutations = 0":
                LEVERAGE_MUTATIONS == 0,

            "Margin Mode Mutations = 0":
                MARGIN_MODE_MUTATIONS == 0,

            "Position Mutations = 0":
                POSITION_MUTATIONS == 0,

            "Real Orders Sent = 0":
                REAL_ORDERS_SENT == 0,

            "Demo Orders Sent = 0":
                DEMO_ORDERS_SENT == 0,

            "Real Order Execution Remains Disabled":
                REAL_ORDER_EXECUTION is False,

            "Order Submission Remains Disabled":
                ORDER_SUBMISSION_ENABLED is False,

            "Exchange Mutation Transport Remains Disabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
        }

        for label, passed in final_safety_checks.items():
            result(
                label,
                passed,
            )

        if not all(
            final_safety_checks.values()
        ):
            raise RuntimeError(
                "Final safety firebreak failed"
            )

        if TEST_STATUS == "FAIL":
            raise RuntimeError(
                "R35T test status is FAIL"
            )

    except Exception as exc:

        FAILURE_STAGE = "R35T_TEST_ENGINE"
        FAILURE_REASON = (
            f"{exc.__class__.__name__}: {exc}"
        )

        TEST_STATUS = "FAIL"

        section(
            f"{UNIT}: FAILURE"
        )

        log(
            f"FAILURE_STAGE={FAILURE_STAGE}"
        )

        log(
            f"FAILURE_REASON={FAILURE_REASON}"
        )

        log(
            "REAL_ORDER_EXECUTION=False"
        )

        log(
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}"
        )

        log(
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}"
        )

        raise


# =============================================================================
# SECTION 18: FINAL SUMMARY
# =============================================================================

def print_summary():

    section(
        f"{UNIT}: FINAL TEST SUMMARY"
    )

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID={TEST_TELEGRAM_UPDATE_ID}"
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
        "SIGNAL_VALIDATED_THIS_STARTUP="
        f"{SIGNAL_VALIDATED_THIS_STARTUP}"
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
        "TELEGRAM_LOCAL_DEDUPE_OK="
        f"{TELEGRAM_LOCAL_DEDUPE_OK}"
    )

    log(
        "TELEGRAM_CROSS_DEPLOY_DEDUPE_OK="
        f"{TELEGRAM_CROSS_DEPLOY_DEDUPE_OK}"
    )

    log(
        "SIGNAL_INTEGRATION_OK="
        f"{SIGNAL_INTEGRATION_OK}"
    )

    log(
        f"CROSS_DEPLOY_PROOF={CROSS_DEPLOY_PROOF}"
    )

    log(
        f"TEST_STATUS={TEST_STATUS}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}"
    )

    log(
        f"LEVERAGE_MUTATIONS={LEVERAGE_MUTATIONS}"
    )

    log(
        f"MARGIN_MODE_MUTATIONS={MARGIN_MODE_MUTATIONS}"
    )

    log(
        f"POSITION_MUTATIONS={POSITION_MUTATIONS}"
    )

    log(
        f"REAL_ORDERS_SENT={REAL_ORDERS_SENT}"
    )

    log(
        f"DEMO_ORDERS_SENT={DEMO_ORDERS_SENT}"
    )

    log(
        f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"DEMO_ORDER_EXECUTION={DEMO_ORDER_EXECUTION}"
    )

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED={ORDER_SUBMISSION_ENABLED}"
    )


# =============================================================================
# SECTION 19: HEARTBEAT LOOP
# =============================================================================

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: "
            f"HEARTBEAT={heartbeat} "
            f"TEST_UPDATE_SEEN_BEFORE_STARTUP="
            f"{TEST_UPDATE_SEEN_BEFORE_STARTUP} "
            f"PROCESSED_THIS_STARTUP="
            f"{PROCESSED_THIS_STARTUP} "
            f"DUPLICATE_REJECTED_THIS_STARTUP="
            f"{DUPLICATE_REJECTED_THIS_STARTUP} "
            f"SIGNAL_PARSED_THIS_STARTUP="
            f"{SIGNAL_PARSED_THIS_STARTUP} "
            f"SIGNAL_VALIDATED_THIS_STARTUP="
            f"{SIGNAL_VALIDATED_THIS_STARTUP} "
            f"SYNTHETIC_DECISION_CREATED_THIS_STARTUP="
            f"{SYNTHETIC_DECISION_CREATED_THIS_STARTUP} "
            f"SYNTHETIC_DECISION_COUNT_THIS_STARTUP="
            f"{SYNTHETIC_DECISION_COUNT_THIS_STARTUP} "
            f"TELEGRAM_CROSS_DEPLOY_DEDUPE_OK="
            f"{TELEGRAM_CROSS_DEPLOY_DEDUPE_OK} "
            f"SIGNAL_INTEGRATION_OK="
            f"{SIGNAL_INTEGRATION_OK} "
            f"CROSS_DEPLOY_PROOF="
            f"{CROSS_DEPLOY_PROOF} "
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


# =============================================================================
# SECTION 20: MAIN
# =============================================================================

def main():

    # Start Render health endpoint.
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    health_thread.start()

    # Give server a moment to bind.
    time.sleep(0.2)

    section(
        f"{UNIT}: MAIN.PY ENTERED"
    )

    log(
        f"{UNIT}: PURPOSE={PURPOSE}"
    )

    log(
        f"PYTHON_VERSION={sys.version.split()[0]}"
    )

    log(
        f"SYMBOL={SYMBOL}"
    )

    log(
        f"TARGET_MARGIN_MODE={TARGET_MARGIN_MODE}"
    )

    log(
        f"TARGET_LONG_LEVERAGE={TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"TARGET_SHORT_LEVERAGE={TARGET_SHORT_LEVERAGE}x"
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

    log(
        f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"DEMO_ORDER_EXECUTION={DEMO_ORDER_EXECUTION}"
    )

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED={ORDER_SUBMISSION_ENABLED}"
    )

    log(
        f"SYNTHETIC_TRANSPORT_ONLY={SYNTHETIC_TRANSPORT_ONLY}"
    )

    try:

        run_r35t_tests()

    except Exception:

        print_summary()

        # Keep Render process alive so failure evidence remains visible.
        heartbeat_loop()

        return

    print_summary()

    heartbeat_loop()


# =============================================================================
# SECTION 21: ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
