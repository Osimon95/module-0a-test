

import os
import sys
import json
import time
import uuid
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# R35R — TELEGRAM CROSS-DEPLOY DURABILITY PROOF
#
# PURPOSE
# -------
# Prove that persistent state written to the Render persistent disk survives a completely new
# deployment.
#
# DEPLOYMENT A:
#   - No previous R35R marker exists.
#   - Create marker atomically under /var/data/r35r_state.
#   - Report:
#         TELEGRAM_LOCAL_DURABLE=True
#         TELEGRAM_CROSS_DEPLOY_DURABLE=False
#         CROSS_DEPLOY_PROOF=PENDING_REDEPLOY
#
# DEPLOYMENT B:
#   - SAME UNCHANGED main.py is redeployed.
#   - Previous marker must still exist.
#   - Verify marker integrity.
#   - Report:
#         TELEGRAM_LOCAL_DURABLE=True
#         TELEGRAM_CROSS_DEPLOY_DURABLE=True
#         CROSS_DEPLOY_PROOF=PASS
#
# SAFETY
# ------
# No WEEX authenticated reads.
# No public market reads.
# No order submission.
# No exchange mutation.
# No leverage mutation.
# No margin mode mutation.
# No position mutation.
# No real order path.
# ==================================================================================================


VERSION = "R35R"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

PERSISTENT_DISK_ROOT = "/var/data"
STATE_DIR = os.path.join(PERSISTENT_DISK_ROOT, "r35r_state")

MARKER_FILE = os.path.join(
    STATE_DIR,
    "telegram_cross_deploy_marker.json"
)

HEARTBEAT_INTERVAL_SECONDS = 30


# --------------------------------------------------------------------------------------------------
# HARD SAFETY FLAGS
# --------------------------------------------------------------------------------------------------

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

AUTHENTICATED_WEEX_READS = 0
PUBLIC_MARKET_GETS = 0

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0


# --------------------------------------------------------------------------------------------------
# GLOBAL RESULT STATE
# --------------------------------------------------------------------------------------------------

telegram_local_durable = False
telegram_cross_deploy_durable = False

marker_seen_before_startup = False
marker_created_this_startup = False
marker_integrity_ok = False

marker_id = None
marker_created_at = None
marker_sha256 = None

cross_deploy_proof = "NOT_RUN"
test_status = "NOT_RUN"

failure_stage = None
exception_class = None
exception_message = None


# --------------------------------------------------------------------------------------------------
# LOGGING
# --------------------------------------------------------------------------------------------------

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{utc_now()} {message}", flush=True)


def separator():
    log("-" * 100)


# --------------------------------------------------------------------------------------------------
# HEALTH SERVER
# --------------------------------------------------------------------------------------------------

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/health", "/healthz"):
            payload = {
                "version": VERSION,
                "status": "running",
                "telegram_local_durable": telegram_local_durable,
                "telegram_cross_deploy_durable": telegram_cross_deploy_durable,
                "cross_deploy_proof": cross_deploy_proof,
                "test_status": test_status,
                "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
                "order_submissions": ORDER_SUBMISSIONS,
                "real_order_execution": REAL_ORDER_EXECUTION,
            }

            body = json.dumps(
                payload,
                sort_keys=True
            ).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.send_header(
                "Content-Length",
                str(len(body))
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
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True
        )

        thread.start()

        log(
            f"{VERSION}: HEALTH SERVER STARTED ON PORT "
            f"{HEALTH_PORT}"
        )

        return True

    except Exception as exc:
        log(
            f"{VERSION}: HEALTH SERVER FAILED: "
            f"{type(exc).__name__}: {exc}"
        )

        return False


# --------------------------------------------------------------------------------------------------
# HASHING
# --------------------------------------------------------------------------------------------------

def canonical_json_bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def calculate_marker_payload_hash(marker):
    payload = {
        "schema": marker["schema"],
        "version": marker["version"],
        "marker_id": marker["marker_id"],
        "created_at": marker["created_at"],
        "purpose": marker["purpose"],
    }

    return sha256_hex(
        canonical_json_bytes(payload)
    )


# --------------------------------------------------------------------------------------------------
# DURABLE FILE HELPERS
# --------------------------------------------------------------------------------------------------

def fsync_directory(path):
    """
    Attempt to fsync directory metadata after atomic rename.

    Some filesystems/platforms may not support directory fsync.
    On Linux/Render this should normally work.
    """

    flags = os.O_RDONLY

    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY

    fd = os.open(
        path,
        flags
    )

    try:
        os.fsync(fd)

    finally:
        os.close(fd)


def ensure_state_directory():
    global telegram_local_durable

    os.makedirs(
        STATE_DIR,
        exist_ok=True
    )

    if not os.path.isdir(STATE_DIR):
        raise RuntimeError(
            "STATE_DIR was not created"
        )

    telegram_local_durable = True


def atomic_write_json(path, payload):
    directory = os.path.dirname(path)

    os.makedirs(
        directory,
        exist_ok=True
    )

    temp_path = (
        path
        + ".tmp."
        + uuid.uuid4().hex
    )

    encoded = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True
        )
        + "\n"
    ).encode("utf-8")

    try:
        with open(
            temp_path,
            "wb"
        ) as handle:

            handle.write(encoded)
            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temp_path,
            path
        )

        fsync_directory(
            directory
        )

    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


def read_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as handle:

        return json.load(handle)


# --------------------------------------------------------------------------------------------------
# MARKER CREATION
# --------------------------------------------------------------------------------------------------

def build_new_marker():

    marker = {
        "schema": 1,
        "version": VERSION,
        "marker_id": uuid.uuid4().hex,
        "created_at": utc_now(),
        "purpose": (
            "telegram_cross_deploy_durability_proof"
        ),
    }

    marker["payload_sha256"] = (
        calculate_marker_payload_hash(
            marker
        )
    )

    return marker


# --------------------------------------------------------------------------------------------------
# MARKER VALIDATION
# --------------------------------------------------------------------------------------------------

def validate_existing_marker(marker):

    required_fields = (
        "schema",
        "version",
        "marker_id",
        "created_at",
        "purpose",
        "payload_sha256",
    )

    for field in required_fields:
        if field not in marker:
            raise RuntimeError(
                f"Existing marker missing field: {field}"
            )

    if marker["schema"] != 1:
        raise RuntimeError(
            "Existing marker schema mismatch"
        )

    if marker["version"] != VERSION:
        raise RuntimeError(
            "Existing marker version mismatch"
        )

    if marker["purpose"] != (
        "telegram_cross_deploy_durability_proof"
    ):
        raise RuntimeError(
            "Existing marker purpose mismatch"
        )

    expected_hash = (
        calculate_marker_payload_hash(
            marker
        )
    )

    observed_hash = (
        marker["payload_sha256"]
    )

    if expected_hash != observed_hash:
        raise RuntimeError(
            "Existing marker integrity hash mismatch"
        )

    return True


# --------------------------------------------------------------------------------------------------
# LOCAL DURABILITY VERIFICATION
# --------------------------------------------------------------------------------------------------

def verify_marker_readback(expected_marker):

    observed = read_json(
        MARKER_FILE
    )

    if observed != expected_marker:
        raise RuntimeError(
            "Marker read-back differs from marker written"
        )

    validate_existing_marker(
        observed
    )

    return True


# --------------------------------------------------------------------------------------------------
# CROSS-DEPLOY TEST
# --------------------------------------------------------------------------------------------------

def run_cross_deploy_test():

    global telegram_local_durable
    global telegram_cross_deploy_durable

    global marker_seen_before_startup
    global marker_created_this_startup
    global marker_integrity_ok

    global marker_id
    global marker_created_at
    global marker_sha256

    global cross_deploy_proof
    global test_status

    global failure_stage
    global exception_class
    global exception_message

    try:

        # ==========================================================================================
        # TEST 1 — PERSISTENT DISK ROOT
        # ==========================================================================================

        separator()
        log(
            f"{VERSION} TEST 1: "
            f"PERSISTENT DISK ROOT"
        )
        separator()

        log(
            f"PERSISTENT_DISK_ROOT="
            f"{PERSISTENT_DISK_ROOT}"
        )

        log(
            f"STATE_DIR="
            f"{STATE_DIR}"
        )

        log(
            f"MARKER_FILE="
            f"{MARKER_FILE}"
        )

        failure_stage = (
            "ENSURE_STATE_DIRECTORY"
        )

        ensure_state_directory()

        log(
            "STATE_DIRECTORY_AVAILABLE=True"
        )

        log(
            f"TELEGRAM_LOCAL_DURABLE="
            f"{telegram_local_durable}"
        )


        # ==========================================================================================
        # TEST 2 — PRE-STARTUP MARKER DETECTION
        # ==========================================================================================

        separator()
        log(
            f"{VERSION} TEST 2: "
            f"PRE-STARTUP MARKER DETECTION"
        )
        separator()

        marker_seen_before_startup = (
            os.path.isfile(
                MARKER_FILE
            )
        )

        log(
            f"MARKER_SEEN_BEFORE_STARTUP="
            f"{marker_seen_before_startup}"
        )


        # ==========================================================================================
        # BRANCH A — MARKER ALREADY EXISTS
        #
        # This means this deployment has inherited marker state from an earlier deployment.
        # ==========================================================================================

        if marker_seen_before_startup:

            separator()
            log(
                f"{VERSION} TEST 3: "
                f"EXISTING MARKER INTEGRITY"
            )
            separator()

            failure_stage = (
                "READ_EXISTING_MARKER"
            )

            existing_marker = read_json(
                MARKER_FILE
            )

            failure_stage = (
                "VALIDATE_EXISTING_MARKER"
            )

            marker_integrity_ok = (
                validate_existing_marker(
                    existing_marker
                )
            )

            marker_id = (
                existing_marker["marker_id"]
            )

            marker_created_at = (
                existing_marker["created_at"]
            )

            marker_sha256 = (
                existing_marker["payload_sha256"]
            )

            log(
                f"MARKER_ID="
                f"{marker_id}"
            )

            log(
                f"MARKER_CREATED_AT="
                f"{marker_created_at}"
            )

            log(
                f"MARKER_SHA256="
                f"{marker_sha256}"
            )

            log(
                f"MARKER_INTEGRITY_OK="
                f"{marker_integrity_ok}"
            )

            marker_created_this_startup = False

            telegram_cross_deploy_durable = True

            cross_deploy_proof = "PASS"
            test_status = "PASS"

            failure_stage = None


        # ==========================================================================================
        # BRANCH B — FIRST DEPLOYMENT
        #
        # No marker exists yet. Create one. This deployment alone cannot prove cross-deployment
        # durability, so result intentionally remains PENDING_REDEPLOY.
        # ==========================================================================================

        else:

            separator()
            log(
                f"{VERSION} TEST 3: "
                f"CREATE DURABLE MARKER"
            )
            separator()

            failure_stage = (
                "BUILD_NEW_MARKER"
            )

            new_marker = (
                build_new_marker()
            )

            marker_id = (
                new_marker["marker_id"]
            )

            marker_created_at = (
                new_marker["created_at"]
            )

            marker_sha256 = (
                new_marker["payload_sha256"]
            )

            log(
                f"NEW_MARKER_ID="
                f"{marker_id}"
            )

            log(
                f"NEW_MARKER_CREATED_AT="
                f"{marker_created_at}"
            )

            log(
                f"NEW_MARKER_SHA256="
                f"{marker_sha256}"
            )


            # --------------------------------------------------------------------------------------
            # Durable atomic write
            # --------------------------------------------------------------------------------------

            failure_stage = (
                "ATOMIC_WRITE_MARKER"
            )

            atomic_write_json(
                MARKER_FILE,
                new_marker
            )

            marker_created_this_startup = True

            log(
                "MARKER_CREATED_THIS_STARTUP=True"
            )


            # --------------------------------------------------------------------------------------
            # Immediate same-deployment read-back
            # --------------------------------------------------------------------------------------

            failure_stage = (
                "VERIFY_LOCAL_READBACK"
            )

            marker_integrity_ok = (
                verify_marker_readback(
                    new_marker
                )
            )

            telegram_local_durable = True

            log(
                f"MARKER_LOCAL_READBACK_OK="
                f"{marker_integrity_ok}"
            )

            log(
                f"TELEGRAM_LOCAL_DURABLE="
                f"{telegram_local_durable}"
            )


            # --------------------------------------------------------------------------------------
            # Important:
            #
            # This deployment cannot certify its own cross-deploy persistence.
            # A second Render deployment must see this exact file.
            # --------------------------------------------------------------------------------------

            telegram_cross_deploy_durable = False

            cross_deploy_proof = (
                "PENDING_REDEPLOY"
            )

            test_status = (
                "PENDING_REDEPLOY"
            )

            failure_stage = None


        # ==========================================================================================
        # TEST 4 — HARD SAFETY FIREBREAK
        # ==========================================================================================

        separator()
        log(
            f"{VERSION} TEST 4: "
            f"HARD SAFETY FIREBREAK"
        )
        separator()

        safety_invariants_ok = all(
            [
                REAL_ORDER_EXECUTION is False,
                FIRST_REAL_ORDER_ALLOWED is False,
                DEMO_ORDER_EXECUTION is False,

                EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
                ORDER_SUBMISSION_ENABLED is False,

                LEVERAGE_MUTATION_ENABLED is False,
                MARGIN_MODE_MUTATION_ENABLED is False,
                POSITION_MUTATION_ENABLED is False,

                AUTHENTICATED_WEEX_READS == 0,
                PUBLIC_MARKET_GETS == 0,

                EXCHANGE_NETWORK_WRITES == 0,
                ORDER_SUBMISSIONS == 0,

                LEVERAGE_MUTATIONS == 0,
                MARGIN_MODE_MUTATIONS == 0,
                POSITION_MUTATIONS == 0,
            ]
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
            f"AUTHENTICATED_WEEX_READS="
            f"{AUTHENTICATED_WEEX_READS}"
        )

        log(
            f"PUBLIC_MARKET_GETS="
            f"{PUBLIC_MARKET_GETS}"
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
            f"SAFETY_INVARIANTS_OK="
            f"{safety_invariants_ok}"
        )

        if not safety_invariants_ok:
            raise RuntimeError(
                "Hard safety invariant failure"
            )


        # ==========================================================================================
        # FINAL REPORT
        # ==========================================================================================

        separator()
        log(
            f"{VERSION}: "
            f"TELEGRAM CROSS-DEPLOY DURABILITY RESULT"
        )
        separator()

        log(
            f"PERSISTENT_DISK_ROOT="
            f"{PERSISTENT_DISK_ROOT}"
        )

        log(
            f"STATE_DIR="
            f"{STATE_DIR}"
        )

        log(
            f"MARKER_FILE="
            f"{MARKER_FILE}"
        )

        log(
            f"MARKER_SEEN_BEFORE_STARTUP="
            f"{marker_seen_before_startup}"
        )

        log(
            f"MARKER_CREATED_THIS_STARTUP="
            f"{marker_created_this_startup}"
        )

        log(
            f"MARKER_INTEGRITY_OK="
            f"{marker_integrity_ok}"
        )

        log(
            f"MARKER_ID="
            f"{marker_id}"
        )

        log(
            f"MARKER_CREATED_AT="
            f"{marker_created_at}"
        )

        log(
            f"MARKER_SHA256="
            f"{marker_sha256}"
        )

        log(
            f"TELEGRAM_LOCAL_DURABLE="
            f"{telegram_local_durable}"
        )

        log(
            f"TELEGRAM_CROSS_DEPLOY_DURABLE="
            f"{telegram_cross_deploy_durable}"
        )

        log(
            f"CROSS_DEPLOY_PROOF="
            f"{cross_deploy_proof}"
        )

        log(
            f"TEST_STATUS="
            f"{test_status}"
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
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        log(
            "REAL_ORDER_PATH=ABSENT"
        )

        log(
            "MUTATION_PATH=ABSENT"
        )

        return True


    except Exception as exc:

        exception_class = (
            type(exc).__name__
        )

        exception_message = str(exc)

        telegram_cross_deploy_durable = False

        cross_deploy_proof = "FAIL"
        test_status = "FAIL"

        separator()
        log(
            f"{VERSION}: ERROR DIAGNOSTIC"
        )
        separator()

        log(
            f"FAILURE_STAGE="
            f"{failure_stage}"
        )

        log(
            f"EXCEPTION_CLASS="
            f"{exception_class}"
        )

        log(
            f"EXCEPTION_MESSAGE="
            f"{exception_message}"
        )

        log(
            f"TELEGRAM_LOCAL_DURABLE="
            f"{telegram_local_durable}"
        )

        log(
            f"TELEGRAM_CROSS_DEPLOY_DURABLE="
            f"{telegram_cross_deploy_durable}"
        )

        log(
            f"CROSS_DEPLOY_PROOF="
            f"{cross_deploy_proof}"
        )

        log(
            f"TEST_STATUS="
            f"{test_status}"
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
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        return False


# --------------------------------------------------------------------------------------------------
# HEARTBEAT
# --------------------------------------------------------------------------------------------------

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"TELEGRAM_LOCAL_DURABLE={telegram_local_durable} "
            f"TELEGRAM_CROSS_DEPLOY_DURABLE={telegram_cross_deploy_durable} "
            f"MARKER_SEEN_BEFORE_STARTUP={marker_seen_before_startup} "
            f"MARKER_CREATED_THIS_STARTUP={marker_created_this_startup} "
            f"MARKER_INTEGRITY_OK={marker_integrity_ok} "
            f"CROSS_DEPLOY_PROOF={cross_deploy_proof} "
            f"TEST_STATUS={test_status} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )

        time.sleep(
            HEARTBEAT_INTERVAL_SECONDS
        )


# --------------------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------------------

def main():

    start_health_server()

    separator()
    log(
        f"{VERSION}: MAIN.PY ENTERED"
    )
    separator()

    log(
        f"{VERSION}: PURPOSE="
        f"TELEGRAM CROSS-DEPLOY DURABILITY PROOF"
    )

    log(
        f"{VERSION}: NO WEEX NETWORK CALLS"
    )

    log(
        f"{VERSION}: NO EXCHANGE MUTATIONS"
    )

    log(
        f"{VERSION}: NO ORDER SUBMISSION"
    )

    log(
        f"{VERSION}: PERSISTENT DISK ROOT="
        f"{PERSISTENT_DISK_ROOT}"
    )

    log(
        f"{VERSION}: STATE DIR="
        f"{STATE_DIR}"
    )

    log(
        f"{VERSION}: MARKER FILE="
        f"{MARKER_FILE}"
    )

    run_cross_deploy_test()

    heartbeat_loop()


if __name__ == "__main__":
    main()
