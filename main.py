

import os
import json
import time
import hashlib
import tempfile
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ======================================================================================
# R35S
# TELEGRAM DURABLE DEDUPLICATION CROSS-DEPLOY TEST
#
# PURPOSE:
#   1. Use /var/data persistent storage.
#   2. Maintain a production-style processed Telegram update registry.
#   3. Present the SAME synthetic Telegram update_id on every deployment.
#   4. First deployment:
#        - update is unseen
#        - update is accepted exactly once
#        - update_id is durably committed
#   5. Next deployment:
#        - same update_id is already present before processing
#        - update is rejected as duplicate
#        - processing count remains zero
#   6. Prove dedupe state survives Render deployment.
#
# IMPORTANT:
#   - NO Telegram API request is made.
#   - NO WEEX request is made.
#   - NO exchange mutation code exists.
#   - NO real order path exists.
# ======================================================================================


VERSION = "R35S"

PERSISTENT_DISK_ROOT = "/var/data"
STATE_DIR = os.path.join(PERSISTENT_DISK_ROOT, "r35s_state")

DEDUPE_FILE = os.path.join(
    STATE_DIR,
    "telegram_processed_updates.json",
)

# Stable on purpose.
# The exact same update ID must be presented after redeployment.
TEST_TELEGRAM_UPDATE_ID = "R35S_SYNTHETIC_UPDATE_000001"

HEARTBEAT_SECONDS = 30
MAX_DEDUPE_RECORDS = 10000


# ======================================================================================
# HARD SAFETY FIREBREAK
# ======================================================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

TELEGRAM_NETWORK_TRANSPORT_ENABLED = False

AUTHENTICATED_WEEX_READS = 0
PUBLIC_MARKET_GETS = 0

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

TELEGRAM_NETWORK_REQUESTS = 0

SYNTHETIC_UPDATES_PRESENTED = 0
SYNTHETIC_UPDATES_PROCESSED = 0
DUPLICATE_UPDATES_REJECTED = 0


# ======================================================================================
# LOGGING
# ======================================================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{utc_now()} {message}", flush=True)


def separator():
    log("-" * 100)


def section(title):
    separator()
    log(title)
    separator()


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/health", "/healthz"):
            body = (
                f"{VERSION} OK\n"
                f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
                f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
                f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}\n"
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))

    server = HTTPServer(("0.0.0.0", port), HealthHandler)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(f"{VERSION}: HEALTH SERVER STARTED ON PORT {port}")


# ======================================================================================
# FILE / HASH HELPERS
# ======================================================================================

def canonical_json_bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_json(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def atomic_write_json(path, value):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    fd, temporary_path = tempfile.mkstemp(
        prefix=".r35s_",
        suffix=".tmp",
        dir=directory,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(
                value,
                handle,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            )

            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, path)

        # Best-effort directory fsync.
        try:
            directory_fd = os.open(directory, os.O_RDONLY)

            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)

        except Exception:
            pass

    finally:
        if os.path.exists(temporary_path):
            try:
                os.unlink(temporary_path)
            except Exception:
                pass


def read_json_file(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


# ======================================================================================
# DURABLE TELEGRAM DEDUPE REGISTRY
# ======================================================================================

def empty_registry():
    return {
        "schema": "r35s.telegram.dedupe.v1",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "processed_updates": {},
    }


def validate_registry_structure(registry):
    if not isinstance(registry, dict):
        raise ValueError("Registry is not a JSON object")

    if registry.get("schema") != "r35s.telegram.dedupe.v1":
        raise ValueError("Unexpected registry schema")

    updates = registry.get("processed_updates")

    if not isinstance(updates, dict):
        raise ValueError("processed_updates is not a dictionary")

    return True


def load_registry():
    if not os.path.exists(DEDUPE_FILE):
        return empty_registry(), False

    registry = read_json_file(DEDUPE_FILE)
    validate_registry_structure(registry)

    return registry, True


def update_seen(registry, update_id):
    key = str(update_id)
    return key in registry["processed_updates"]


def prune_registry(registry):
    updates = registry["processed_updates"]

    if len(updates) <= MAX_DEDUPE_RECORDS:
        return

    ordered = sorted(
        updates.items(),
        key=lambda item: item[1].get("processed_at", ""),
    )

    excess = len(ordered) - MAX_DEDUPE_RECORDS

    for key, _ in ordered[:excess]:
        updates.pop(key, None)


def commit_processed_update(registry, update_id):
    key = str(update_id)

    if key in registry["processed_updates"]:
        raise RuntimeError(
            "Attempted to commit an already processed Telegram update"
        )

    registry["processed_updates"][key] = {
        "update_id": key,
        "processed_at": utc_now(),
        "source": "R35S_SYNTHETIC_TEST",
    }

    registry["updated_at"] = utc_now()

    prune_registry(registry)

    atomic_write_json(DEDUPE_FILE, registry)


# ======================================================================================
# SAFETY VALIDATION
# ======================================================================================

def safety_invariants_ok():
    return all([
        REAL_ORDER_EXECUTION is False,
        FIRST_REAL_ORDER_ALLOWED is False,
        DEMO_ORDER_EXECUTION is False,

        EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
        ORDER_SUBMISSION_ENABLED is False,
        LEVERAGE_MUTATION_ENABLED is False,
        MARGIN_MODE_MUTATION_ENABLED is False,
        POSITION_MUTATION_ENABLED is False,

        TELEGRAM_NETWORK_TRANSPORT_ENABLED is False,

        AUTHENTICATED_WEEX_READS == 0,
        PUBLIC_MARKET_GETS == 0,

        EXCHANGE_NETWORK_WRITES == 0,
        ORDER_SUBMISSIONS == 0,
        LEVERAGE_MUTATIONS == 0,
        MARGIN_MODE_MUTATIONS == 0,
        POSITION_MUTATIONS == 0,

        TELEGRAM_NETWORK_REQUESTS == 0,
    ])


# ======================================================================================
# MAIN TEST
# ======================================================================================

def run_test():
    global SYNTHETIC_UPDATES_PRESENTED
    global SYNTHETIC_UPDATES_PROCESSED
    global DUPLICATE_UPDATES_REJECTED

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(
        f"{VERSION}: PURPOSE=TELEGRAM DURABLE DEDUPE "
        f"CROSS-DEPLOY REJECTION"
    )

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")
    log(f"STATE_DIR={STATE_DIR}")
    log(f"DEDUPE_FILE={DEDUPE_FILE}")
    log(f"TEST_TELEGRAM_UPDATE_ID={TEST_TELEGRAM_UPDATE_ID}")

    os.makedirs(STATE_DIR, exist_ok=True)

    # ==================================================================================
    # TEST 1 — PERSISTENT STORAGE
    # ==================================================================================

    section(f"{VERSION} TEST 1: PERSISTENT STORAGE")

    log(f"PERSISTENT_DISK_ROOT_EXISTS={os.path.isdir(PERSISTENT_DISK_ROOT)}")
    log(f"STATE_DIR_EXISTS={os.path.isdir(STATE_DIR)}")
    log(f"DEDUPE_FILE_EXISTS_BEFORE_STARTUP={os.path.exists(DEDUPE_FILE)}")

    persistent_storage_ok = (
        os.path.isdir(PERSISTENT_DISK_ROOT)
        and os.path.isdir(STATE_DIR)
    )

    log(f"PERSISTENT_STORAGE_OK={persistent_storage_ok}")

    # ==================================================================================
    # TEST 2 — LOAD DURABLE REGISTRY
    # ==================================================================================

    section(f"{VERSION} TEST 2: LOAD DURABLE TELEGRAM DEDUPE REGISTRY")

    registry, registry_seen_before_startup = load_registry()

    registry_integrity_ok = validate_registry_structure(registry)

    registry_hash_before = sha256_json(registry)

    records_before = len(registry["processed_updates"])

    update_seen_before_startup = update_seen(
        registry,
        TEST_TELEGRAM_UPDATE_ID,
    )

    log(f"REGISTRY_SEEN_BEFORE_STARTUP={registry_seen_before_startup}")
    log(f"REGISTRY_INTEGRITY_OK={registry_integrity_ok}")
    log(f"REGISTRY_RECORDS_BEFORE={records_before}")
    log(f"REGISTRY_SHA256_BEFORE={registry_hash_before}")

    log(
        "TEST_UPDATE_SEEN_BEFORE_STARTUP="
        f"{update_seen_before_startup}"
    )

    # ==================================================================================
    # TEST 3 — PRESENT SAME TELEGRAM UPDATE
    # ==================================================================================

    section(f"{VERSION} TEST 3: PRESENT SYNTHETIC TELEGRAM UPDATE")

    SYNTHETIC_UPDATES_PRESENTED += 1

    log(f"SYNTHETIC_UPDATE_ID={TEST_TELEGRAM_UPDATE_ID}")
    log(f"SYNTHETIC_UPDATES_PRESENTED={SYNTHETIC_UPDATES_PRESENTED}")

    processed_this_startup = False
    duplicate_rejected_this_startup = False

    if update_seen_before_startup:

        # --------------------------------------------------------------------------
        # DUPLICATE PATH
        #
        # Critical rule:
        # The business-processing function is NOT entered.
        # --------------------------------------------------------------------------

        DUPLICATE_UPDATES_REJECTED += 1
        duplicate_rejected_this_startup = True

        log("DEDUPE_DECISION=REJECT_DUPLICATE")
        log("BUSINESS_PROCESSING_ENTERED=False")
        log("DURABLE_COMMIT_REQUIRED=False")

    else:

        # --------------------------------------------------------------------------
        # FIRST-SEEN PATH
        #
        # This simulates exactly one successful processing event.
        # No Telegram or WEEX network call occurs.
        # --------------------------------------------------------------------------

        log("DEDUPE_DECISION=ACCEPT_FIRST_SEEN")
        log("BUSINESS_PROCESSING_ENTERED=True")

        SYNTHETIC_UPDATES_PROCESSED += 1
        processed_this_startup = True

        commit_processed_update(
            registry,
            TEST_TELEGRAM_UPDATE_ID,
        )

        log("DURABLE_COMMIT_REQUIRED=True")
        log("DURABLE_COMMIT_COMPLETED=True")

    log(
        f"SYNTHETIC_UPDATES_PROCESSED="
        f"{SYNTHETIC_UPDATES_PROCESSED}"
    )

    log(
        f"DUPLICATE_UPDATES_REJECTED="
        f"{DUPLICATE_UPDATES_REJECTED}"
    )

    # ==================================================================================
    # TEST 4 — READ-BACK DURABLE STATE
    # ==================================================================================

    section(f"{VERSION} TEST 4: DURABLE READ-BACK")

    registry_after, registry_exists_after = load_registry()

    registry_after_integrity_ok = validate_registry_structure(
        registry_after
    )

    registry_hash_after = sha256_json(registry_after)

    records_after = len(
        registry_after["processed_updates"]
    )

    update_present_after = update_seen(
        registry_after,
        TEST_TELEGRAM_UPDATE_ID,
    )

    log(f"REGISTRY_EXISTS_AFTER={registry_exists_after}")
    log(f"REGISTRY_INTEGRITY_AFTER={registry_after_integrity_ok}")
    log(f"REGISTRY_RECORDS_AFTER={records_after}")
    log(f"REGISTRY_SHA256_AFTER={registry_hash_after}")
    log(f"TEST_UPDATE_PRESENT_AFTER={update_present_after}")

    durable_commit_verified = (
        registry_exists_after
        and registry_after_integrity_ok
        and update_present_after
    )

    log(f"DURABLE_COMMIT_VERIFIED={durable_commit_verified}")

    # ==================================================================================
    # TEST 5 — SAME-PROCESS DUPLICATE REPLAY
    #
    # Even on first deployment we can prove immediate replay rejection.
    # Cross-deploy proof requires update_seen_before_startup=True.
    # ==================================================================================

    section(f"{VERSION} TEST 5: IMMEDIATE DUPLICATE REPLAY")

    replay_registry, _ = load_registry()

    replay_seen = update_seen(
        replay_registry,
        TEST_TELEGRAM_UPDATE_ID,
    )

    replay_business_processing_entered = False

    if replay_seen:
        replay_rejected = True
    else:
        replay_rejected = False
        replay_business_processing_entered = True

    log(f"REPLAY_UPDATE_SEEN={replay_seen}")
    log(f"REPLAY_REJECTED={replay_rejected}")
    log(
        "REPLAY_BUSINESS_PROCESSING_ENTERED="
        f"{replay_business_processing_entered}"
    )

    local_dedupe_ok = (
        durable_commit_verified
        and replay_seen
        and replay_rejected
        and not replay_business_processing_entered
    )

    log(f"TELEGRAM_LOCAL_DEDUPE_OK={local_dedupe_ok}")

    # ==================================================================================
    # TEST 6 — HARD SAFETY FIREBREAK
    # ==================================================================================

    section(f"{VERSION} TEST 6: HARD SAFETY FIREBREAK")

    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log(f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}")
    log(f"DEMO_ORDER_EXECUTION={DEMO_ORDER_EXECUTION}")

    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(f"ORDER_SUBMISSION_ENABLED={ORDER_SUBMISSION_ENABLED}")
    log(f"LEVERAGE_MUTATION_ENABLED={LEVERAGE_MUTATION_ENABLED}")
    log(f"MARGIN_MODE_MUTATION_ENABLED={MARGIN_MODE_MUTATION_ENABLED}")
    log(f"POSITION_MUTATION_ENABLED={POSITION_MUTATION_ENABLED}")

    log(
        "TELEGRAM_NETWORK_TRANSPORT_ENABLED="
        f"{TELEGRAM_NETWORK_TRANSPORT_ENABLED}"
    )

    log(f"AUTHENTICATED_WEEX_READS={AUTHENTICATED_WEEX_READS}")
    log(f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS}")

    log(f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}")
    log(f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}")
    log(f"LEVERAGE_MUTATIONS={LEVERAGE_MUTATIONS}")
    log(f"MARGIN_MODE_MUTATIONS={MARGIN_MODE_MUTATIONS}")
    log(f"POSITION_MUTATIONS={POSITION_MUTATIONS}")

    log(f"TELEGRAM_NETWORK_REQUESTS={TELEGRAM_NETWORK_REQUESTS}")

    safety_ok = safety_invariants_ok()

    log(f"SAFETY_INVARIANTS_OK={safety_ok}")

    # ==================================================================================
    # FINAL CROSS-DEPLOY EVALUATION
    # ==================================================================================

    section(
        f"{VERSION}: TELEGRAM DURABLE DEDUPE "
        f"CROSS-DEPLOY RESULT"
    )

    # First deployment:
    #   update_seen_before_startup=False
    #   creates durable baseline
    #
    # Second deployment:
    #   update_seen_before_startup=True
    #   rejects duplicate without processing
    #
    # Therefore cross-deploy proof is only PASS when state already existed
    # before this process started.

    telegram_cross_deploy_dedupe_ok = all([
        persistent_storage_ok,
        registry_integrity_ok,
        registry_after_integrity_ok,
        durable_commit_verified,
        local_dedupe_ok,
        safety_ok,

        update_seen_before_startup is True,
        processed_this_startup is False,
        duplicate_rejected_this_startup is True,

        SYNTHETIC_UPDATES_PROCESSED == 0,
        DUPLICATE_UPDATES_REJECTED == 1,
    ])

    if telegram_cross_deploy_dedupe_ok:
        cross_deploy_proof = "PASS"
        test_status = "PASS"

    elif (
        not update_seen_before_startup
        and processed_this_startup
        and durable_commit_verified
        and local_dedupe_ok
        and safety_ok
    ):
        cross_deploy_proof = "BASELINE_CREATED"
        test_status = "REDEPLOY_REQUIRED"

    else:
        cross_deploy_proof = "FAIL"
        test_status = "FAIL"

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")
    log(f"STATE_DIR={STATE_DIR}")
    log(f"DEDUPE_FILE={DEDUPE_FILE}")

    log(f"TEST_UPDATE_ID={TEST_TELEGRAM_UPDATE_ID}")

    log(
        "TEST_UPDATE_SEEN_BEFORE_STARTUP="
        f"{update_seen_before_startup}"
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
        f"TELEGRAM_LOCAL_DURABLE="
        f"{durable_commit_verified}"
    )

    log(
        f"TELEGRAM_LOCAL_DEDUPE_OK="
        f"{local_dedupe_ok}"
    )

    log(
        "TELEGRAM_CROSS_DEPLOY_DEDUPE_OK="
        f"{telegram_cross_deploy_dedupe_ok}"
    )

    log(f"CROSS_DEPLOY_PROOF={cross_deploy_proof}")
    log(f"TEST_STATUS={test_status}")

    log(f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}")
    log(f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}")
    log(f"TELEGRAM_NETWORK_REQUESTS={TELEGRAM_NETWORK_REQUESTS}")

    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log("REAL_ORDER_PATH=ABSENT")
    log("MUTATION_PATH=ABSENT")
    log("TELEGRAM_NETWORK_PATH=ABSENT")

    return {
        "test_status": test_status,
        "cross_deploy_proof": cross_deploy_proof,
        "update_seen_before_startup": update_seen_before_startup,
        "processed_this_startup": processed_this_startup,
        "duplicate_rejected_this_startup": duplicate_rejected_this_startup,
        "telegram_cross_deploy_dedupe_ok": telegram_cross_deploy_dedupe_ok,
    }


# ======================================================================================
# ENTRY POINT
# ======================================================================================

def main():
    start_health_server()

    try:
        result = run_test()

    except Exception as exc:
        section(f"{VERSION}: FATAL TEST ERROR")

        log(f"EXCEPTION_CLASS={type(exc).__name__}")
        log(f"EXCEPTION_MESSAGE={exc}")

        log("TEST_STATUS=FAIL")

        log(f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}")
        log(f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}")
        log(f"TELEGRAM_NETWORK_REQUESTS={TELEGRAM_NETWORK_REQUESTS}")

        log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
        log("REAL_ORDER_PATH=ABSENT")
        log("MUTATION_PATH=ABSENT")
        log("TELEGRAM_NETWORK_PATH=ABSENT")

        result = {
            "test_status": "FAIL",
            "cross_deploy_proof": "FAIL",
            "update_seen_before_startup": False,
            "processed_this_startup": False,
            "duplicate_rejected_this_startup": False,
            "telegram_cross_deploy_dedupe_ok": False,
        }

    heartbeat = 0

    while True:
        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT={heartbeat} "
            f"TEST_UPDATE_SEEN_BEFORE_STARTUP="
            f"{result['update_seen_before_startup']} "
            f"PROCESSED_THIS_STARTUP="
            f"{result['processed_this_startup']} "
            f"DUPLICATE_REJECTED_THIS_STARTUP="
            f"{result['duplicate_rejected_this_startup']} "
            f"TELEGRAM_CROSS_DEPLOY_DEDUPE_OK="
            f"{result['telegram_cross_deploy_dedupe_ok']} "
            f"CROSS_DEPLOY_PROOF="
            f"{result['cross_deploy_proof']} "
            f"TEST_STATUS="
            f"{result['test_status']} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(HEARTBEAT_SECONDS)


if __name__ == "__main__":
    main()

