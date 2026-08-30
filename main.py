

#!/usr/bin/env python3

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


# ======================================================================================
# R36B.2
#
# PURPOSE:
#   EXACT R36A DURABLE UPDATE-ID EXTRACTION + R36B LOOKUP RECONCILIATION
#
# SAFETY:
#   - READ ONLY
#   - NO TELEGRAM CONSUMPTION
#   - NO SIGNAL PARSING
#   - NO EXCHANGE REQUESTS
#   - NO ORDER SUBMISSIONS
#   - NO LEVERAGE / MARGIN / POSITION MUTATIONS
#   - NO PERSISTENT STATE MODIFICATION
#
# This stage diagnoses the original R36B failure:
#
#   UPDATE_SEEN_BEFORE_STARTUP=False
#   CROSS_RESTART_REPLAY_REJECTION_OK=False
#
# R36B.1 proved:
#   - /var/data exists
#   - JSON files are readable
#   - R36A durable files exist
#   - R36B durable files do not exist
#   - expected R36B update id was not exposed
#
# R36B.2 now:
#   1. Opens exact R36A registry files.
#   2. Extracts every update-like ID.
#   3. Determines which IDs are shared between dedupe + decision registries.
#   4. Identifies the strongest R36A durable update-ID candidate.
#   5. Compares that with likely R36B lookup IDs.
#   6. Prints the exact value R36B should use.
#
# ======================================================================================


STAGE = "R36B.2"

PERSISTENT_DISK_ROOT = Path("/var/data")
R36A_STATE_DIR = PERSISTENT_DISK_ROOT / "r36a_state"

R36A_DEDUPE_FILE = R36A_STATE_DIR / "telegram_processed_updates.json"
R36A_DECISION_FILE = R36A_STATE_DIR / "synthetic_decisions.json"

# Optional explicit comparison value.
#
# If you later expose the original R36B expected ID as an environment variable,
# R36B.2 will compare against it automatically.
ENV_EXPECTED_ID = (
    os.environ.get("R36B_EXPECTED_UPDATE_ID")
    or os.environ.get("EXPECTED_UPDATE_ID")
    or os.environ.get("TEST_TELEGRAM_UPDATE_ID")
)

# Likely historical IDs. These are comparison candidates ONLY.
# They are never written anywhere.
LIKELY_R36B_IDS = [
    "R36B_SYNTHETIC_UPDATE_000001",
    "R36A_SYNTHETIC_UPDATE_000001",
]


# ======================================================================================
# HARD SAFETY FIREBREAK COUNTERS
# ======================================================================================

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

PERSISTENT_STATE_MODIFIED = False
SIGNAL_PARSE_ATTEMPTED = False
TELEGRAM_UPDATE_CONSUMED = False
EXCHANGE_REQUEST_ATTEMPTED = False


# ======================================================================================
# DISPLAY HELPERS
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
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<85} {status}", flush=True)


# ======================================================================================
# HEALTH SERVER
# ======================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (
            f"{STAGE} OK\n"
            f"MODE=READ_ONLY_IDENTITY_RECONCILIATION\n"
            f"REAL_ORDER_EXECUTION=False\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))

    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )
        thread.start()

        log(f"{STAGE}: HEALTH SERVER STARTED ON PORT {port}")
        return True

    except Exception as exc:
        log(
            f"{STAGE}: HEALTH SERVER START FAILED "
            f"{type(exc).__name__}: {exc}"
        )
        return False


# ======================================================================================
# READ-ONLY JSON FUNCTIONS
# ======================================================================================

def read_json_file(path):
    """
    READ ONLY.

    Never creates, modifies, truncates, renames, or deletes anything.
    """

    if not path.exists():
        return None, f"FILE_NOT_FOUND:{path}"

    if not path.is_file():
        return None, f"NOT_A_FILE:{path}"

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle), None

    except Exception as exc:
        return None, f"{type(exc).__name__}:{exc}"


def normalize_scalar(value):
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (str, int)):
        text = str(value).strip()

        if text:
            return text

    return None


UPDATE_KEY_HINTS = (
    "update_id",
    "telegram_update_id",
    "telegramupdateid",
    "test_update_id",
    "test_telegram_update_id",
    "source_update_id",
    "telegram_id",
    "dedupe_id",
)


def key_looks_like_update_id(key):
    normalized = (
        str(key)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if normalized in UPDATE_KEY_HINTS:
        return True

    if "update" in normalized and "id" in normalized:
        return True

    return False


def value_looks_like_update_id(value):
    text = normalize_scalar(value)

    if text is None:
        return False

    upper = text.upper()

    # Strong stage-specific synthetic identifiers.
    if "R36A" in upper and "UPDATE" in upper:
        return True

    if "R36B" in upper and "UPDATE" in upper:
        return True

    # Generic test identifiers used through earlier stages.
    if "SYNTHETIC_UPDATE" in upper:
        return True

    if "TELEGRAM" in upper and "UPDATE" in upper:
        return True

    return False


def extract_update_ids(value):
    """
    Recursively extracts probable update IDs from arbitrary JSON structures.

    Handles:
      - dict fields like {"update_id": "..."}
      - dicts keyed directly by update id
      - lists of records
      - nested registry structures
    """

    found = set()

    def walk(node):
        if isinstance(node, dict):

            for key, item in node.items():

                # Case 1:
                # {
                #   "update_id": "R36A_SYNTHETIC_UPDATE_000001"
                # }
                if key_looks_like_update_id(key):
                    scalar = normalize_scalar(item)

                    if scalar:
                        found.add(scalar)

                # Case 2:
                # {
                #   "R36A_SYNTHETIC_UPDATE_000001": {...}
                # }
                if value_looks_like_update_id(key):
                    found.add(str(key).strip())

                # Case 3:
                # other scalar values containing obvious update IDs
                scalar = normalize_scalar(item)

                if scalar and value_looks_like_update_id(scalar):
                    found.add(scalar)

                walk(item)

        elif isinstance(node, list):

            for item in node:
                walk(item)

        else:
            scalar = normalize_scalar(node)

            if scalar and value_looks_like_update_id(scalar):
                found.add(scalar)

    walk(value)

    return sorted(found)


def count_exact_occurrences(node, target):
    if target is None:
        return 0

    count = 0

    def walk(value):
        nonlocal count

        if isinstance(value, dict):
            for key, item in value.items():

                if str(key) == target:
                    count += 1

                scalar = normalize_scalar(item)

                if scalar == target:
                    count += 1

                walk(item)

        elif isinstance(value, list):
            for item in value:
                walk(item)

        else:
            scalar = normalize_scalar(value)

            if scalar == target:
                count += 1

    walk(node)

    return count


# ======================================================================================
# MAIN TEST
# ======================================================================================

def main():

    start_health_server()

    section(f"{STAGE}: MAIN.PY ENTERED")

    log(
        f"{STAGE}: PURPOSE="
        "EXACT R36A DURABLE UPDATE-ID EXTRACTION + "
        "R36B LOOKUP RECONCILIATION"
    )

    log("TEST_MODE=READ_ONLY_IDENTITY_RECONCILIATION")

    log(f"PYTHON_VERSION={sys.version.split()[0]}")

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")
    log(f"R36A_STATE_DIR={R36A_STATE_DIR}")

    log(f"R36A_DEDUPE_FILE={R36A_DEDUPE_FILE}")
    log(f"R36A_DECISION_FILE={R36A_DECISION_FILE}")

    log(f"ENV_EXPECTED_ID={ENV_EXPECTED_ID}")

    log("REAL_ORDER_EXECUTION=False")
    log("DEMO_ORDER_EXECUTION=False")
    log("EXCHANGE_MUTATION_TRANSPORT_ENABLED=False")
    log("ORDER_SUBMISSION_ENABLED=False")

    # ==================================================================================
    # TEST 1
    # HARD SAFETY FIREBREAK
    # ==================================================================================

    section(f"{STAGE} TEST 1: HARD SAFETY FIREBREAK")

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

    # ==================================================================================
    # TEST 2
    # PERSISTENT DISK VISIBILITY
    # ==================================================================================

    section(f"{STAGE} TEST 2: R36A PERSISTENT STATE VISIBILITY")

    persistent_disk_available = (
        PERSISTENT_DISK_ROOT.exists()
        and PERSISTENT_DISK_ROOT.is_dir()
    )

    r36a_state_available = (
        R36A_STATE_DIR.exists()
        and R36A_STATE_DIR.is_dir()
    )

    dedupe_exists = R36A_DEDUPE_FILE.exists()
    decision_exists = R36A_DECISION_FILE.exists()

    log(
        f"PERSISTENT_DISK_AVAILABLE="
        f"{persistent_disk_available}"
    )

    log(
        f"R36A_STATE_DIR_AVAILABLE="
        f"{r36a_state_available}"
    )

    log(
        f"R36A_DEDUPE_FILE_EXISTS="
        f"{dedupe_exists}"
    )

    log(
        f"R36A_DECISION_FILE_EXISTS="
        f"{decision_exists}"
    )

    result(
        "Persistent Disk Available",
        persistent_disk_available,
    )

    result(
        "R36A State Directory Available",
        r36a_state_available,
    )

    result(
        "R36A Telegram Dedupe Registry Present",
        dedupe_exists,
    )

    result(
        "R36A Synthetic Decision Registry Present",
        decision_exists,
    )

    # ==================================================================================
    # TEST 3
    # READ EXACT R36A REGISTRIES
    # ==================================================================================

    section(f"{STAGE} TEST 3: LOAD EXACT R36A DURABLE REGISTRIES")

    dedupe_json, dedupe_error = read_json_file(
        R36A_DEDUPE_FILE
    )

    decision_json, decision_error = read_json_file(
        R36A_DECISION_FILE
    )

    dedupe_readable = dedupe_error is None
    decision_readable = decision_error is None

    log(f"DEDUPE_READ_ERROR={dedupe_error}")
    log(f"DECISION_READ_ERROR={decision_error}")

    result(
        "R36A Durable Dedupe Registry Readable",
        dedupe_readable,
    )

    result(
        "R36A Durable Decision Registry Readable",
        decision_readable,
    )

    # ==================================================================================
    # TEST 4
    # EXACT UPDATE-ID EXTRACTION
    # ==================================================================================

    section(f"{STAGE} TEST 4: EXTRACT R36A DURABLE UPDATE IDS")

    dedupe_ids = (
        extract_update_ids(dedupe_json)
        if dedupe_readable
        else []
    )

    decision_ids = (
        extract_update_ids(decision_json)
        if decision_readable
        else []
    )

    union_ids = sorted(
        set(dedupe_ids) | set(decision_ids)
    )

    shared_ids = sorted(
        set(dedupe_ids) & set(decision_ids)
    )

    log(
        f"R36A_DEDUPE_UPDATE_ID_COUNT="
        f"{len(dedupe_ids)}"
    )

    for index, update_id in enumerate(
        dedupe_ids,
        start=1,
    ):
        log(
            f"R36A_DEDUPE_UPDATE_ID_{index}="
            f"{update_id}"
        )

    log(
        f"R36A_DECISION_UPDATE_ID_COUNT="
        f"{len(decision_ids)}"
    )

    for index, update_id in enumerate(
        decision_ids,
        start=1,
    ):
        log(
            f"R36A_DECISION_UPDATE_ID_{index}="
            f"{update_id}"
        )

    log(
        f"R36A_UNIQUE_UPDATE_ID_COUNT="
        f"{len(union_ids)}"
    )

    for index, update_id in enumerate(
        union_ids,
        start=1,
    ):
        log(
            f"R36A_UNIQUE_UPDATE_ID_{index}="
            f"{update_id}"
        )

    log(
        f"R36A_SHARED_UPDATE_ID_COUNT="
        f"{len(shared_ids)}"
    )

    for index, update_id in enumerate(
        shared_ids,
        start=1,
    ):
        log(
            f"R36A_SHARED_UPDATE_ID_{index}="
            f"{update_id}"
        )

    result(
        "At Least One R36A Durable Update ID Found",
        len(union_ids) > 0,
    )

    # ==================================================================================
    # TEST 5
    # STRONGEST DURABLE ID CANDIDATE
    # ==================================================================================

    section(f"{STAGE} TEST 5: DETERMINE CANONICAL R36A UPDATE ID")

    canonical_update_id = None
    canonical_reason = None

    # Strongest proof:
    # same update ID appears in both dedupe and decision registries.
    if len(shared_ids) == 1:

        canonical_update_id = shared_ids[0]
        canonical_reason = (
            "EXACTLY_ONE_ID_SHARED_BY_DEDUPE_AND_DECISION_REGISTRIES"
        )

    elif len(shared_ids) > 1:

        r36a_shared = [
            item
            for item in shared_ids
            if "R36A" in item.upper()
        ]

        if len(r36a_shared) == 1:
            canonical_update_id = r36a_shared[0]
            canonical_reason = (
                "ONE_R36A_PREFIXED_ID_SHARED_BY_BOTH_REGISTRIES"
            )

    # Next strongest:
    # exactly one R36A-prefixed ID across the two registries.
    if canonical_update_id is None:

        r36a_union = [
            item
            for item in union_ids
            if "R36A" in item.upper()
        ]

        if len(r36a_union) == 1:
            canonical_update_id = r36a_union[0]
            canonical_reason = (
                "EXACTLY_ONE_R36A_PREFIXED_DURABLE_UPDATE_ID"
            )

    # Final fallback:
    # exactly one total ID.
    if canonical_update_id is None:

        if len(union_ids) == 1:
            canonical_update_id = union_ids[0]
            canonical_reason = (
                "EXACTLY_ONE_DURABLE_UPDATE_ID_TOTAL"
            )

    log(
        f"CANONICAL_R36A_UPDATE_ID="
        f"{canonical_update_id}"
    )

    log(
        f"CANONICAL_SELECTION_REASON="
        f"{canonical_reason}"
    )

    result(
        "Canonical R36A Update ID Determined",
        canonical_update_id is not None,
    )

    # ==================================================================================
    # TEST 6
    # EXACT OCCURRENCE VERIFICATION
    # ==================================================================================

    section(f"{STAGE} TEST 6: EXACT CANONICAL ID OCCURRENCE")

    dedupe_exact_count = (
        count_exact_occurrences(
            dedupe_json,
            canonical_update_id,
        )
        if dedupe_readable
        else 0
    )

    decision_exact_count = (
        count_exact_occurrences(
            decision_json,
            canonical_update_id,
        )
        if decision_readable
        else 0
    )

    total_exact_count = (
        dedupe_exact_count
        + decision_exact_count
    )

    log(
        f"CANONICAL_ID_DEDUPE_EXACT_COUNT="
        f"{dedupe_exact_count}"
    )

    log(
        f"CANONICAL_ID_DECISION_EXACT_COUNT="
        f"{decision_exact_count}"
    )

    log(
        f"CANONICAL_ID_TOTAL_EXACT_COUNT="
        f"{total_exact_count}"
    )

    result(
        "Canonical ID Exists In Durable State",
        canonical_update_id is not None
        and total_exact_count > 0,
    )

    # ==================================================================================
    # TEST 7
    # R36B LOOKUP RECONCILIATION
    # ==================================================================================

    section(f"{STAGE} TEST 7: R36B LOOKUP IDENTITY RECONCILIATION")

    comparison_ids = []

    if ENV_EXPECTED_ID:
        comparison_ids.append(
            (
                "ENV_EXPECTED_ID",
                ENV_EXPECTED_ID,
            )
        )

    for candidate in LIKELY_R36B_IDS:
        comparison_ids.append(
            (
                "LIKELY_SOURCE_ID",
                candidate,
            )
        )

    seen_comparison_ids = set()

    exact_match_names = []

    for source, candidate in comparison_ids:

        if candidate in seen_comparison_ids:
            continue

        seen_comparison_ids.add(candidate)

        matches_canonical = (
            canonical_update_id is not None
            and candidate == canonical_update_id
        )

        exists_in_dedupe = (
            candidate in dedupe_ids
        )

        exists_in_decision = (
            candidate in decision_ids
        )

        exists_anywhere = (
            exists_in_dedupe
            or exists_in_decision
        )

        log(
            f"COMPARE_SOURCE={source} "
            f"CANDIDATE={candidate} "
            f"MATCHES_CANONICAL={matches_canonical} "
            f"EXISTS_IN_DEDUPE={exists_in_dedupe} "
            f"EXISTS_IN_DECISION={exists_in_decision} "
            f"EXISTS_ANYWHERE={exists_anywhere}"
        )

        if matches_canonical:
            exact_match_names.append(candidate)

    r36b_synthetic_exists = (
        "R36B_SYNTHETIC_UPDATE_000001"
        in union_ids
    )

    r36a_synthetic_exists = (
        "R36A_SYNTHETIC_UPDATE_000001"
        in union_ids
    )

    log(
        f"R36B_SYNTHETIC_UPDATE_000001_DURABLE="
        f"{r36b_synthetic_exists}"
    )

    log(
        f"R36A_SYNTHETIC_UPDATE_000001_DURABLE="
        f"{r36a_synthetic_exists}"
    )

    # ==================================================================================
    # TEST 8
    # DIAGNOSIS
    # ==================================================================================

    section(f"{STAGE} TEST 8: PRIMARY DIAGNOSIS")

    if canonical_update_id is None:

        diagnosis = (
            "CANONICAL_R36A_UPDATE_ID_COULD_NOT_BE_DETERMINED"
        )

        recommended_r36b_expected_id = None

        r36b_lookup_fix_required = False

    else:

        recommended_r36b_expected_id = (
            canonical_update_id
        )

        if (
            ENV_EXPECTED_ID
            and ENV_EXPECTED_ID
            == canonical_update_id
        ):

            diagnosis = (
                "EXPOSED_R36B_EXPECTED_ID_MATCHES_"
                "R36A_DURABLE_UPDATE_ID"
            )

            r36b_lookup_fix_required = False

        elif ENV_EXPECTED_ID:

            diagnosis = (
                "R36B_EXPECTED_ID_MISMATCH_CONFIRMED"
            )

            r36b_lookup_fix_required = True

        elif r36b_synthetic_exists is False:

            diagnosis = (
                "R36B_LOOKUP_MUST_USE_EXISTING_R36A_"
                "DURABLE_UPDATE_ID_NOT_NEW_R36B_ID"
            )

            r36b_lookup_fix_required = True

        else:

            diagnosis = (
                "CANONICAL_ID_FOUND_EXPOSE_ORIGINAL_"
                "R36B_EXPECTED_ID_FOR_FINAL_COMPARISON"
            )

            r36b_lookup_fix_required = True

    log(
        f"PRIMARY_DIAGNOSIS="
        f"{diagnosis}"
    )

    log(
        f"RECOMMENDED_R36B_EXPECTED_UPDATE_ID="
        f"{recommended_r36b_expected_id}"
    )

    log(
        f"R36B_LOOKUP_FIX_REQUIRED="
        f"{r36b_lookup_fix_required}"
    )

    # This is the most important output of R36B.2.
    log(LINE)

    log(
        "COPY_THIS_VALUE_INTO_R36B_EXPECTED_UPDATE_ID="
        f"{recommended_r36b_expected_id}"
    )

    log(LINE)

    # ==================================================================================
    # TEST 9
    # ZERO-WRITE VERIFICATION
    # ==================================================================================

    section(f"{STAGE} TEST 9: ZERO-WRITE VERIFICATION")

    result(
        "Exchange Network Writes = 0",
        EXCHANGE_NETWORK_WRITES == 0,
    )

    result(
        "Order Submissions = 0",
        ORDER_SUBMISSIONS == 0,
    )

    result(
        "Leverage Mutations = 0",
        LEVERAGE_MUTATIONS == 0,
    )

    result(
        "Margin Mode Mutations = 0",
        MARGIN_MODE_MUTATIONS == 0,
    )

    result(
        "Position Mutations = 0",
        POSITION_MUTATIONS == 0,
    )

    result(
        "Real Orders Sent = 0",
        REAL_ORDERS_SENT == 0,
    )

    result(
        "Demo Orders Sent = 0",
        DEMO_ORDERS_SENT == 0,
    )

    result(
        "Persistent State Not Modified",
        PERSISTENT_STATE_MODIFIED is False,
    )

    result(
        "Signal Parsing Not Attempted",
        SIGNAL_PARSE_ATTEMPTED is False,
    )

    result(
        "Telegram Update Not Consumed",
        TELEGRAM_UPDATE_CONSUMED is False,
    )

    result(
        "Exchange Request Not Attempted",
        EXCHANGE_REQUEST_ATTEMPTED is False,
    )

    # ==================================================================================
    # FINAL STATUS
    # ==================================================================================

    diagnostic_test_status = (
        persistent_disk_available
        and r36a_state_available
        and dedupe_readable
        and decision_readable
        and canonical_update_id is not None
        and total_exact_count > 0
        and EXCHANGE_NETWORK_WRITES == 0
        and ORDER_SUBMISSIONS == 0
        and REAL_ORDERS_SENT == 0
        and DEMO_ORDERS_SENT == 0
        and PERSISTENT_STATE_MODIFIED is False
        and SIGNAL_PARSE_ATTEMPTED is False
        and TELEGRAM_UPDATE_CONSUMED is False
        and EXCHANGE_REQUEST_ATTEMPTED is False
    )

    section(f"{STAGE}: FINAL DIAGNOSTIC SUMMARY")

    log(
        "TEST_MODE="
        "READ_ONLY_IDENTITY_RECONCILIATION"
    )

    log(
        f"PERSISTENT_DISK_AVAILABLE="
        f"{persistent_disk_available}"
    )

    log(
        f"R36A_DEDUPE_REGISTRY_READABLE="
        f"{dedupe_readable}"
    )

    log(
        f"R36A_DECISION_REGISTRY_READABLE="
        f"{decision_readable}"
    )

    log(
        f"R36A_DEDUPE_UPDATE_ID_COUNT="
        f"{len(dedupe_ids)}"
    )

    log(
        f"R36A_DECISION_UPDATE_ID_COUNT="
        f"{len(decision_ids)}"
    )

    log(
        f"R36A_SHARED_UPDATE_ID_COUNT="
        f"{len(shared_ids)}"
    )

    log(
        f"CANONICAL_R36A_UPDATE_ID="
        f"{canonical_update_id}"
    )

    log(
        f"ENV_EXPECTED_ID="
        f"{ENV_EXPECTED_ID}"
    )

    log(
        f"PRIMARY_DIAGNOSIS="
        f"{diagnosis}"
    )

    log(
        f"RECOMMENDED_R36B_EXPECTED_UPDATE_ID="
        f"{recommended_r36b_expected_id}"
    )

    log(
        f"R36B_LOOKUP_FIX_REQUIRED="
        f"{r36b_lookup_fix_required}"
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
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"PERSISTENT_STATE_MODIFIED="
        f"{PERSISTENT_STATE_MODIFIED}"
    )

    log(
        f"SIGNAL_PARSE_ATTEMPTED="
        f"{SIGNAL_PARSE_ATTEMPTED}"
    )

    log(
        f"TELEGRAM_UPDATE_CONSUMED="
        f"{TELEGRAM_UPDATE_CONSUMED}"
    )

    log(
        f"EXCHANGE_REQUEST_ATTEMPTED="
        f"{EXCHANGE_REQUEST_ATTEMPTED}"
    )

    log(
        f"DIAGNOSTIC_TEST_STATUS="
        f"{'PASS' if diagnostic_test_status else 'FAIL'}"
    )

    log(LINE)

    # ==================================================================================
    # HEARTBEAT
    # ==================================================================================

    heartbeat = 0

    while True:

        time.sleep(30)

        heartbeat += 1

        log(
            f"{STAGE}: "
            f"HEARTBEAT={heartbeat} "
            f"DIAGNOSTIC_TEST_STATUS="
            f"{'PASS' if diagnostic_test_status else 'FAIL'} "
            f"CANONICAL_R36A_UPDATE_ID="
            f"{canonical_update_id} "
            f"R36B_LOOKUP_FIX_REQUIRED="
            f"{r36b_lookup_fix_required} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )


if __name__ == "__main__":
    main()

