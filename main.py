

import os
import json
import time
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


# =====================================================================
# R36B.1
# PURPOSE:
# READ-ONLY PERSISTENT STATE DIAGNOSTIC FOR FAILED R36B CROSS-RESTART
# TELEGRAM UPDATE REPLAY REJECTION.
#
# HARD SAFETY:
# - NO EXCHANGE NETWORK WRITES
# - NO ORDER SUBMISSIONS
# - NO LEVERAGE MUTATIONS
# - NO MARGIN MODE MUTATIONS
# - NO POSITION MUTATIONS
# - NO DEMO ORDERS
# - NO REAL ORDERS
# - NO PERSISTENT STATE MODIFICATION
#
# R36B FAILURE BEING DIAGNOSED:
# UPDATE_SEEN_BEFORE_STARTUP=False
# DUPLICATE_DETECTED=False
# SIGNAL_PARSE_COUNT=0
# CROSS_RESTART_REPLAY_REJECTION_OK=False
# =====================================================================


STAGE = "R36B.1"

PERSISTENT_DISK_ROOT = Path("/var/data")

# Diagnostic only.
# We deliberately do not assume one exact R36A/R36B directory.
LIKELY_STATE_NAMES = (
    "r36a",
    "r36b",
    "r35u",
    "r35y",
    "telegram",
    "dedupe",
    "processed",
    "decision",
    "registry",
    "state",
)

MAX_FILE_BYTES_TO_READ = 2_000_000
MAX_PRINTED_UPDATE_IDS = 100

# Safety counters.
EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
REAL_ORDERS_SENT = 0
DEMO_ORDERS_SENT = 0

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False
EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

# Diagnostic counters.
JSON_FILES_FOUND = 0
JSON_FILES_READABLE = 0
JSON_FILES_INVALID = 0
UPDATE_LIKE_IDS_FOUND = 0

HEARTBEAT = 0

SEP = "-" * 100


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{utc_now()} {message}", flush=True)


def result(label, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<82} {status}", flush=True)


# =====================================================================
# HEALTH SERVER
# =====================================================================


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = (
            f"{STAGE} OK\n"
            f"TEST_STATUS=DIAGNOSTIC\n"
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_health_server():
    port = int(os.environ.get("PORT", "10000"))

    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        log(f"{STAGE}: HEALTH SERVER STARTED ON PORT {port}")
        server.serve_forever()
    except Exception as exc:
        log(
            f"{STAGE}: HEALTH SERVER ERROR "
            f"{exc.__class__.__name__}: {exc}"
        )


# =====================================================================
# READ-ONLY HELPERS
# =====================================================================


def safe_file_size(path):
    try:
        return path.stat().st_size
    except Exception:
        return None


def safe_mtime(path):
    try:
        return datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()
    except Exception:
        return None


def interesting_path(path):
    text = str(path).lower()
    return any(token in text for token in LIKELY_STATE_NAMES)


def recursively_extract_ids(value, location="$", findings=None):
    """
    Searches JSON structures for strings/values associated with keys
    that look like Telegram/update/dedupe/replay identifiers.

    READ ONLY.
    """

    if findings is None:
        findings = []

    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            child_location = f"{location}.{key}"

            interesting_key = any(
                marker in key_text
                for marker in (
                    "update_id",
                    "updateid",
                    "telegram_update",
                    "telegram_id",
                    "dedupe",
                    "duplicate",
                    "replay",
                    "processed_update",
                    "processed_updates",
                    "marker_id",
                    "decision_id",
                )
            )

            if interesting_key:
                if isinstance(child, (str, int, float, bool)):
                    findings.append(
                        {
                            "location": child_location,
                            "value": str(child),
                        }
                    )

                elif isinstance(child, list):
                    for index, item in enumerate(child):
                        if isinstance(item, (str, int, float, bool)):
                            findings.append(
                                {
                                    "location": (
                                        f"{child_location}[{index}]"
                                    ),
                                    "value": str(item),
                                }
                            )

                elif isinstance(child, dict):
                    # Common durable registry format:
                    # {
                    #   "R36A_SYNTHETIC_UPDATE_...": {...}
                    # }
                    for nested_key in child.keys():
                        findings.append(
                            {
                                "location": (
                                    f"{child_location}.<key>"
                                ),
                                "value": str(nested_key),
                            }
                        )

            recursively_extract_ids(
                child,
                child_location,
                findings,
            )

    elif isinstance(value, list):
        for index, item in enumerate(value):
            recursively_extract_ids(
                item,
                f"{location}[{index}]",
                findings,
            )

    return findings


def collect_string_values(value, findings=None):
    """
    Collect strings that themselves look like R36/R35 synthetic update IDs.
    """

    if findings is None:
        findings = []

    if isinstance(value, dict):
        for key, child in value.items():
            key_s = str(key)

            if (
                "UPDATE" in key_s.upper()
                or "R36" in key_s.upper()
                or "R35" in key_s.upper()
            ):
                findings.append(key_s)

            collect_string_values(child, findings)

    elif isinstance(value, list):
        for item in value:
            collect_string_values(item, findings)

    elif isinstance(value, str):
        text = value.upper()

        if (
            "SYNTHETIC_UPDATE" in text
            or "R36A" in text
            or "R36B" in text
            or "R35Y_SYNTHETIC_UPDATE" in text
            or "R35U_SYNTHETIC_UPDATE" in text
        ):
            findings.append(value)

    return findings


def discover_json_files():
    if not PERSISTENT_DISK_ROOT.exists():
        return []

    found = []

    try:
        for path in PERSISTENT_DISK_ROOT.rglob("*.json"):
            if path.is_file():
                found.append(path)
    except Exception as exc:
        log(
            f"{STAGE}: JSON DISCOVERY ERROR "
            f"{exc.__class__.__name__}: {exc}"
        )

    return sorted(found, key=lambda p: str(p))


def read_json_file(path):
    global JSON_FILES_READABLE
    global JSON_FILES_INVALID

    size = safe_file_size(path)

    if size is None:
        return None, "STAT_FAILED"

    if size > MAX_FILE_BYTES_TO_READ:
        return None, f"SKIPPED_TOO_LARGE_{size}_BYTES"

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        JSON_FILES_READABLE += 1
        return data, None

    except Exception as exc:
        JSON_FILES_INVALID += 1
        return None, f"{exc.__class__.__name__}: {exc}"


def determine_expected_update_id():
    """
    R36B.1 intentionally does not hard-code an invented identifier.

    If R36B supplied its expected replay ID through an environment variable,
    we compare against it.

    Otherwise we diagnose all durable IDs that actually exist.
    """

    candidates = (
        "R36B_EXPECTED_UPDATE_ID",
        "R36_EXPECTED_UPDATE_ID",
        "TEST_TELEGRAM_UPDATE_ID",
        "TEST_UPDATE_ID",
        "EXPECTED_UPDATE_ID",
    )

    for name in candidates:
        value = os.environ.get(name)

        if value:
            return name, value

    return None, None


# =====================================================================
# DIAGNOSTIC
# =====================================================================


def run_diagnostic():
    global JSON_FILES_FOUND
    global UPDATE_LIKE_IDS_FOUND

    log(SEP)
    log(f"{STAGE}: MAIN.PY ENTERED")
    log(SEP)

    log(
        f"{STAGE}: PURPOSE="
        "READ-ONLY R36B CROSS-RESTART PERSISTENCE DIAGNOSTIC"
    )

    log(
        f"{STAGE}: FAILURE_UNDER_INVESTIGATION="
        "UPDATE_SEEN_BEFORE_STARTUP_FALSE"
    )

    # -----------------------------------------------------------------
    # TEST 1: HARD SAFETY FIREBREAK
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 1: HARD SAFETY FIREBREAK")
    log(SEP)

    result(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    result(
        "First Real Order Forbidden",
        FIRST_REAL_ORDER_ALLOWED is False,
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

    # -----------------------------------------------------------------
    # TEST 2: PERSISTENT DISK
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 2: PERSISTENT DISK DISCOVERY")
    log(SEP)

    log(f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}")
    log(
        f"PERSISTENT_DISK_EXISTS="
        f"{PERSISTENT_DISK_ROOT.exists()}"
    )

    log(
        f"PERSISTENT_DISK_IS_DIRECTORY="
        f"{PERSISTENT_DISK_ROOT.is_dir()}"
    )

    disk_ok = (
        PERSISTENT_DISK_ROOT.exists()
        and PERSISTENT_DISK_ROOT.is_dir()
    )

    result("Persistent Disk Available", disk_ok)

    # -----------------------------------------------------------------
    # TEST 3: DIRECTORY INVENTORY
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 3: STATE DIRECTORY INVENTORY")
    log(SEP)

    directories = []

    if disk_ok:
        try:
            directories = sorted(
                [
                    item
                    for item in PERSISTENT_DISK_ROOT.iterdir()
                    if item.is_dir()
                ],
                key=lambda p: str(p),
            )
        except Exception as exc:
            log(
                f"DIRECTORY_INVENTORY_ERROR="
                f"{exc.__class__.__name__}: {exc}"
            )

    log(f"TOP_LEVEL_DIRECTORY_COUNT={len(directories)}")

    for directory in directories:
        marker = (
            "LIKELY_R36_STATE"
            if interesting_path(directory)
            else "OTHER"
        )

        log(
            f"STATE_DIRECTORY={directory} "
            f"CLASSIFICATION={marker}"
        )

    # -----------------------------------------------------------------
    # TEST 4: JSON FILE INVENTORY
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 4: JSON FILE INVENTORY")
    log(SEP)

    json_files = discover_json_files()
    JSON_FILES_FOUND = len(json_files)

    log(f"JSON_FILES_FOUND={JSON_FILES_FOUND}")

    for path in json_files:
        log(
            f"JSON_FILE={path} "
            f"SIZE_BYTES={safe_file_size(path)} "
            f"MODIFIED_UTC={safe_mtime(path)} "
            f"LIKELY_RELEVANT={interesting_path(path)}"
        )

    result(
        "At Least One Persistent JSON File Found",
        JSON_FILES_FOUND > 0,
    )

    # -----------------------------------------------------------------
    # TEST 5: EXPECTED R36B REPLAY UPDATE ID
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 5: EXPECTED REPLAY IDENTIFIER")
    log(SEP)

    env_name, expected_update_id = determine_expected_update_id()

    log(f"EXPECTED_UPDATE_ID_ENV_SOURCE={env_name}")
    log(f"EXPECTED_UPDATE_ID={expected_update_id}")
    log(
        "EXPECTED_UPDATE_ID_AVAILABLE="
        f"{expected_update_id is not None}"
    )

    if expected_update_id is None:
        log(
            "DIAGNOSTIC_NOTE=NO_EXPECTED_UPDATE_ID_WAS_HARD_CODED_"
            "IN_R36B1_TO_AVOID_INVENTING_AN_ID"
        )

    # -----------------------------------------------------------------
    # TEST 6: READ DURABLE REGISTRIES
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 6: DURABLE JSON CONTENT INSPECTION")
    log(SEP)

    all_findings = []
    exact_matches = []

    for path in json_files:
        data, error = read_json_file(path)

        if error is not None:
            log(
                f"JSON_READ path={path} "
                f"STATUS=SKIPPED_OR_FAILED "
                f"REASON={error}"
            )
            continue

        log(
            f"JSON_READ path={path} STATUS=OK "
            f"ROOT_TYPE={type(data).__name__}"
        )

        structured = recursively_extract_ids(data)
        string_values = collect_string_values(data)

        seen_local = set()

        for item in structured:
            signature = (
                item["location"],
                item["value"],
            )

            if signature in seen_local:
                continue

            seen_local.add(signature)

            finding = {
                "file": str(path),
                "location": item["location"],
                "value": item["value"],
            }

            all_findings.append(finding)

        for value in string_values:
            signature = ("<string-or-key>", str(value))

            if signature in seen_local:
                continue

            seen_local.add(signature)

            all_findings.append(
                {
                    "file": str(path),
                    "location": "<string-or-key>",
                    "value": str(value),
                }
            )

    # Deduplicate globally.
    unique_findings = []
    seen_global = set()

    for finding in all_findings:
        signature = (
            finding["file"],
            finding["location"],
            finding["value"],
        )

        if signature in seen_global:
            continue

        seen_global.add(signature)
        unique_findings.append(finding)

    UPDATE_LIKE_IDS_FOUND = len(unique_findings)

    log(
        f"UPDATE_LIKE_ID_FINDING_COUNT="
        f"{UPDATE_LIKE_IDS_FOUND}"
    )

    for index, finding in enumerate(
        unique_findings[:MAX_PRINTED_UPDATE_IDS],
        start=1,
    ):
        log(
            f"UPDATE_ID_FINDING_{index} "
            f"FILE={finding['file']} "
            f"LOCATION={finding['location']} "
            f"VALUE={finding['value']}"
        )

        if (
            expected_update_id is not None
            and finding["value"] == expected_update_id
        ):
            exact_matches.append(finding)

    if UPDATE_LIKE_IDS_FOUND > MAX_PRINTED_UPDATE_IDS:
        log(
            "UPDATE_ID_OUTPUT_TRUNCATED=True "
            f"PRINTED={MAX_PRINTED_UPDATE_IDS} "
            f"TOTAL={UPDATE_LIKE_IDS_FOUND}"
        )

    # -----------------------------------------------------------------
    # TEST 7: CROSS-RESTART LOOKUP DIAGNOSIS
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 7: CROSS-RESTART LOOKUP DIAGNOSIS")
    log(SEP)

    log(f"JSON_FILES_READABLE={JSON_FILES_READABLE}")
    log(f"JSON_FILES_INVALID={JSON_FILES_INVALID}")

    r36a_files = [
        path
        for path in json_files
        if "r36a" in str(path).lower()
    ]

    r36b_files = [
        path
        for path in json_files
        if "r36b" in str(path).lower()
    ]

    log(f"R36A_JSON_FILE_COUNT={len(r36a_files)}")
    log(f"R36B_JSON_FILE_COUNT={len(r36b_files)}")

    for path in r36a_files:
        log(f"R36A_JSON_FILE={path}")

    for path in r36b_files:
        log(f"R36B_JSON_FILE={path}")

    exact_match_found = len(exact_matches) > 0

    log(f"EXPECTED_UPDATE_EXACT_MATCH_FOUND={exact_match_found}")
    log(f"EXPECTED_UPDATE_EXACT_MATCH_COUNT={len(exact_matches)}")

    for finding in exact_matches:
        log(
            f"EXPECTED_UPDATE_MATCH_FILE={finding['file']} "
            f"LOCATION={finding['location']}"
        )

    # Diagnostic classification.
    if expected_update_id is None:
        diagnosis = (
            "EXPECTED_R36B_UPDATE_ID_NOT_EXPOSED_TO_R36B1; "
            "USE_PRINTED_DURABLE_IDS_TO_COMPARE_WITH_R36B_SOURCE"
        )

    elif exact_match_found:
        diagnosis = (
            "EXPECTED_UPDATE_EXISTS_ON_DISK; "
            "R36B_LOOKUP_PATH_OR_REGISTRY_FORMAT_IS_LIKELY_WRONG"
        )

    elif len(r36a_files) == 0:
        diagnosis = (
            "NO_R36A_JSON_STATE_FOUND_UNDER_VAR_DATA; "
            "R36A_MAY_HAVE_WRITTEN_TO_A_DIFFERENT_DIRECTORY_OR_NOT_PERSISTED"
        )

    else:
        diagnosis = (
            "R36A_STATE_EXISTS_BUT_EXPECTED_UPDATE_ID_NOT_FOUND; "
            "LIKELY_UPDATE_ID_MISMATCH_OR_R36A_DID_NOT_COMMIT_THE_EXPECTED_ID"
        )

    log(f"PRIMARY_DIAGNOSIS={diagnosis}")

    # -----------------------------------------------------------------
    # TEST 8: ZERO-WRITE VERIFICATION
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE} TEST 8: ZERO-WRITE VERIFICATION")
    log(SEP)

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

    # -----------------------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------------------

    log(SEP)
    log(f"{STAGE}: FINAL DIAGNOSTIC SUMMARY")
    log(SEP)

    log("TEST_MODE=READ_ONLY_DIAGNOSTIC")
    log(f"PERSISTENT_DISK_AVAILABLE={disk_ok}")
    log(f"JSON_FILES_FOUND={JSON_FILES_FOUND}")
    log(f"JSON_FILES_READABLE={JSON_FILES_READABLE}")
    log(f"UPDATE_LIKE_IDS_FOUND={UPDATE_LIKE_IDS_FOUND}")
    log(f"R36A_JSON_FILE_COUNT={len(r36a_files)}")
    log(f"R36B_JSON_FILE_COUNT={len(r36b_files)}")
    log(f"EXPECTED_UPDATE_ID={expected_update_id}")
    log(f"EXPECTED_UPDATE_EXACT_MATCH_FOUND={exact_match_found}")
    log(f"PRIMARY_DIAGNOSIS={diagnosis}")

    log(f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}")
    log(f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}")
    log(f"LEVERAGE_MUTATIONS={LEVERAGE_MUTATIONS}")
    log(f"MARGIN_MODE_MUTATIONS={MARGIN_MODE_MUTATIONS}")
    log(f"POSITION_MUTATIONS={POSITION_MUTATIONS}")
    log(f"REAL_ORDERS_SENT={REAL_ORDERS_SENT}")
    log(f"DEMO_ORDERS_SENT={DEMO_ORDERS_SENT}")
    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")

    log("PERSISTENT_STATE_MODIFIED=False")
    log("SIGNAL_PARSE_ATTEMPTED=False")
    log("TELEGRAM_UPDATE_CONSUMED=False")
    log("EXCHANGE_REQUEST_ATTEMPTED=False")

    # Diagnostic run itself is considered successful if it safely inspected
    # the disk. This does NOT declare the original R36B test fixed.
    diagnostic_status = "PASS" if disk_ok else "FAIL"

    log(f"R36B_ORIGINAL_TEST_FIXED=False")
    log(f"DIAGNOSTIC_TEST_STATUS={diagnostic_status}")

    log(SEP)


# =====================================================================
# HEARTBEAT
# =====================================================================


def heartbeat_loop():
    global HEARTBEAT

    while True:
        time.sleep(30)
        HEARTBEAT += 1

        log(
            f"{STAGE}: HEARTBEAT={HEARTBEAT} "
            f"DIAGNOSTIC_TEST_STATUS="
            f"{'PASS' if PERSISTENT_DISK_ROOT.exists() else 'FAIL'} "
            f"JSON_FILES_FOUND={JSON_FILES_FOUND} "
            f"JSON_FILES_READABLE={JSON_FILES_READABLE} "
            f"UPDATE_LIKE_IDS_FOUND={UPDATE_LIKE_IDS_FOUND} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )


# =====================================================================
# ENTRY
# =====================================================================


if __name__ == "__main__":
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )
    health_thread.start()

    try:
        run_diagnostic()

    except Exception as exc:
        log(SEP)
        log(f"{STAGE}: UNHANDLED DIAGNOSTIC ERROR")
        log(
            f"EXCEPTION_CLASS={exc.__class__.__name__}"
        )
        log(f"EXCEPTION_MESSAGE={exc}")
        log("EXCHANGE_NETWORK_WRITES=0")
        log("ORDER_SUBMISSIONS=0")
        log("REAL_ORDER_EXECUTION=False")
        log("DIAGNOSTIC_TEST_STATUS=FAIL")
        log(SEP)

    heartbeat_loop()

