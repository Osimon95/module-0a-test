

# =============================================================================
# R35W MAIN.PY
# PURPOSE:
#   FORENSIC DURABLE-REGISTRY COMPATIBILITY INSPECTION
#
# GOALS:
#   1. Load the durable R35U dedupe registry.
#   2. Load the durable R35U decision registry.
#   3. Print exact raw keys and record structures.
#   4. Discover how R35U stored:
#        R35U_SYNTHETIC_UPDATE_000001
#   5. Locate the original R35U synthetic decision.
#   6. Attempt deterministic canonical JSON/hash variants.
#   7. Determine which representation reproduces the stored decision hash.
#
# ABSOLUTE SAFETY:
#   - NO TELEGRAM PROCESSING
#   - NO SIGNAL PARSER
#   - NO SIGNAL VALIDATOR
#   - NO DECISION CREATION
#   - NO EXCHANGE WRITES
#   - NO ORDER SUBMISSION
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MODE MUTATION
#   - NO POSITION MUTATION
#   - NO REAL ORDER
#   - NO DEMO ORDER
# =============================================================================

import os
import json
import time
import hashlib
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R35W IDENTIFICATION
# =============================================================================

UNIT = "R35W"

PURPOSE = (
    "FORENSIC DURABLE-REGISTRY COMPATIBILITY INSPECTION: "
    "DISCOVER EXACT R35U DEDUPE REPRESENTATION + "
    "REPRODUCE ORIGINAL R35U DECISION HASH WITHOUT PROCESSING UPDATE"
)

TEST_TELEGRAM_UPDATE_ID = "R35U_SYNTHETIC_UPDATE_000001"

EXPECTED_ORIGINAL_DECISION_HASH = (
    "ada67682fedff8bbac0608cc96805dc42ea20bab56f3305c8afa06d7ef89cc94"
)


# =============================================================================
# HARD SAFETY FIREBREAK
# =============================================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

TELEGRAM_PROCESSING_ENABLED = False
SIGNAL_PARSER_ENABLED = False
SIGNAL_VALIDATOR_ENABLED = False
SYNTHETIC_DECISION_CREATION_ENABLED = False

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


# =============================================================================
# STORAGE CONFIGURATION
# =============================================================================

PERSISTENT_DISK_ROOT = os.getenv("PERSISTENT_DISK_ROOT", "/var/data")

R35U_STATE_DIR = os.path.join(
    PERSISTENT_DISK_ROOT,
    "r35u_state",
)

# R35W itself writes nothing into R35U.
R35W_STATE_DIR = os.path.join(
    PERSISTENT_DISK_ROOT,
    "r35w_state",
)

# Candidate filenames.
# We deliberately search several plausible names because R35W's job is to
# discover exactly what R35U persisted rather than assuming R35V's schema.
DEDUPE_FILENAME_CANDIDATES = [
    "telegram_dedupe_registry.json",
    "dedupe_registry.json",
    "telegram_cross_deploy_dedupe_registry.json",
    "telegram_cross_deploy_registry.json",
    "telegram_cross_deploy_marker.json",
    "telegram_update_registry.json",
    "processed_updates.json",
    "processed_telegram_updates.json",
]

DECISION_FILENAME_CANDIDATES = [
    "decision_registry.json",
    "synthetic_decision_registry.json",
    "telegram_decision_registry.json",
    "telegram_cross_deploy_decision_registry.json",
    "decisions.json",
    "synthetic_decisions.json",
]


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

SEPARATOR = "-" * 100


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{utc_now()} {message}", flush=True)


def section(title):
    log(SEPARATOR)
    log(title)
    log(SEPARATOR)


def result(label, ok):
    mark = "✅ PASS" if ok else "❌ FAIL"
    print(f"{label:<85} {mark}", flush=True)


def safe_repr(value, max_len=6000):
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            default=str,
        )
    except Exception:
        text = repr(value)

    if len(text) > max_len:
        return text[:max_len] + "\n...[TRUNCATED]"

    return text


# =============================================================================
# HASH HELPERS
# =============================================================================

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_default(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def canonical_ascii(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def canonical_spaced(value):
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )


def canonical_unsorted(value):
    return json.dumps(
        value,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def canonical_pretty(value):
    return json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def canonical_pretty_ascii(value):
    return json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        default=str,
    )


# =============================================================================
# FILE HELPERS
# =============================================================================

def read_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_state_files():
    files = []

    if not os.path.isdir(R35U_STATE_DIR):
        return files

    for root, dirs, names in os.walk(R35U_STATE_DIR):
        dirs.sort()
        names.sort()

        for name in names:
            path = os.path.join(root, name)
            files.append(path)

    return files


def discover_json_files():
    discovered = []

    for path in list_state_files():
        if path.lower().endswith(".json"):
            discovered.append(path)

    return discovered


def candidate_score(path, candidate_names):
    basename = os.path.basename(path).lower()

    score = 0

    for candidate in candidate_names:
        candidate = candidate.lower()

        if basename == candidate:
            score += 100

        if candidate.replace(".json", "") in basename:
            score += 25

    return score


def choose_best_file(paths, candidate_names, keyword_groups):
    scored = []

    for path in paths:
        basename = os.path.basename(path).lower()

        score = candidate_score(path, candidate_names)

        for keyword in keyword_groups:
            if keyword.lower() in basename:
                score += 10

        scored.append((score, path))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    if not scored:
        return None

    if scored[0][0] <= 0:
        return None

    return scored[0][1]


# =============================================================================
# RECURSIVE SEARCH HELPERS
# =============================================================================

def recursive_find_exact_value(obj, target, path="$"):
    matches = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}"

            if key == target:
                matches.append(
                    {
                        "match_type": "DICT_KEY",
                        "path": child_path,
                        "value": value,
                    }
                )

            if value == target:
                matches.append(
                    {
                        "match_type": "DICT_VALUE",
                        "path": child_path,
                        "value": value,
                    }
                )

            matches.extend(
                recursive_find_exact_value(
                    value,
                    target,
                    child_path,
                )
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            child_path = f"{path}[{index}]"

            if value == target:
                matches.append(
                    {
                        "match_type": "LIST_VALUE",
                        "path": child_path,
                        "value": value,
                    }
                )

            matches.extend(
                recursive_find_exact_value(
                    value,
                    target,
                    child_path,
                )
            )

    return matches


def recursive_find_hash(obj, target_hash, path="$"):
    matches = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}"

            if isinstance(value, str) and value == target_hash:
                matches.append(
                    {
                        "path": child_path,
                        "key": key,
                        "value": value,
                    }
                )

            matches.extend(
                recursive_find_hash(
                    value,
                    target_hash,
                    child_path,
                )
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            child_path = f"{path}[{index}]"

            if isinstance(value, str) and value == target_hash:
                matches.append(
                    {
                        "path": child_path,
                        "key": index,
                        "value": value,
                    }
                )

            matches.extend(
                recursive_find_hash(
                    value,
                    target_hash,
                    child_path,
                )
            )

    return matches


def collect_dict_nodes(obj, path="$"):
    nodes = []

    if isinstance(obj, dict):
        nodes.append((path, obj))

        for key, value in obj.items():
            nodes.extend(
                collect_dict_nodes(
                    value,
                    f"{path}.{key}",
                )
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            nodes.extend(
                collect_dict_nodes(
                    value,
                    f"{path}[{index}]",
                )
            )

    return nodes


# =============================================================================
# DECISION-HASH CANDIDATE GENERATOR
# =============================================================================

HASH_FIELD_NAMES = {
    "hash",
    "sha256",
    "decision_hash",
    "decision_sha256",
    "payload_hash",
    "record_hash",
    "integrity_hash",
}


def remove_hash_fields(value):
    if isinstance(value, dict):
        output = {}

        for key, child in value.items():
            if str(key).lower() in HASH_FIELD_NAMES:
                continue

            output[key] = remove_hash_fields(child)

        return output

    if isinstance(value, list):
        return [
            remove_hash_fields(child)
            for child in value
        ]

    return value


def candidate_payloads(decision_registry):
    candidates = []

    candidates.append(
        (
            "$",
            "FULL_REGISTRY",
            decision_registry,
        )
    )

    for path, node in collect_dict_nodes(decision_registry):
        candidates.append(
            (
                path,
                "DICT_NODE",
                node,
            )
        )

        stripped = remove_hash_fields(node)

        if stripped != node:
            candidates.append(
                (
                    path,
                    "DICT_NODE_WITH_HASH_FIELDS_REMOVED",
                    stripped,
                )
            )

        for field_name in [
            "decision",
            "payload",
            "record",
            "data",
            "synthetic_decision",
            "decision_payload",
            "body",
        ]:
            if field_name in node:
                candidates.append(
                    (
                        f"{path}.{field_name}",
                        f"FIELD_{field_name}",
                        node[field_name],
                    )
                )

    unique = []
    seen = set()

    for path, label, payload in candidates:
        try:
            marker = canonical_default(payload)
        except Exception:
            marker = repr(payload)

        composite = (
            path,
            label,
            marker,
        )

        if composite in seen:
            continue

        seen.add(composite)
        unique.append(
            (
                path,
                label,
                payload,
            )
        )

    return unique


def test_hash_variants(payload):
    variants = []

    serializers = [
        (
            "SORTED_COMPACT_UTF8",
            canonical_default,
        ),
        (
            "SORTED_COMPACT_ASCII",
            canonical_ascii,
        ),
        (
            "SORTED_DEFAULT_SPACING_UTF8",
            canonical_spaced,
        ),
        (
            "UNSORTED_COMPACT_UTF8",
            canonical_unsorted,
        ),
        (
            "SORTED_PRETTY_UTF8",
            canonical_pretty,
        ),
        (
            "SORTED_PRETTY_ASCII",
            canonical_pretty_ascii,
        ),
    ]

    for serializer_name, serializer in serializers:
        try:
            serialized = serializer(payload)
            digest = sha256_text(serialized)

            variants.append(
                {
                    "serializer": serializer_name,
                    "serialized": serialized,
                    "sha256": digest,
                }
            )

            # Some programs accidentally hash a trailing newline.
            newline_digest = sha256_text(serialized + "\n")

            variants.append(
                {
                    "serializer": serializer_name + "_TRAILING_NEWLINE",
                    "serialized": serialized + "\n",
                    "sha256": newline_digest,
                }
            )

        except Exception as exc:
            variants.append(
                {
                    "serializer": serializer_name,
                    "error": repr(exc),
                }
            )

    return variants


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = b"R35W OK\n"

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_health_server():
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler,
    )

    log(
        f"{UNIT}: HEALTH SERVER STARTED ON PORT {port}"
    )

    server.serve_forever()


# =============================================================================
# MAIN FORENSIC TEST
# =============================================================================

def main():

    global EXCHANGE_NETWORK_WRITES
    global ORDER_SUBMISSIONS
    global LEVERAGE_MUTATIONS
    global MARGIN_MODE_MUTATIONS
    global POSITION_MUTATIONS
    global REAL_ORDERS_SENT
    global DEMO_ORDERS_SENT

    global TELEGRAM_PROCESSING_ATTEMPTS
    global SIGNAL_PARSE_COUNT
    global SIGNAL_VALIDATION_COUNT
    global SYNTHETIC_DECISION_CREATION_COUNT

    # -------------------------------------------------------------------------
    # START HEALTH SERVER
    # -------------------------------------------------------------------------

    threading.Thread(
        target=run_health_server,
        daemon=True,
    ).start()

    time.sleep(0.2)

    # -------------------------------------------------------------------------
    # STARTUP
    # -------------------------------------------------------------------------

    section(
        f"{UNIT}: MAIN.PY ENTERED"
    )

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID={TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"EXPECTED_ORIGINAL_DECISION_HASH={EXPECTED_ORIGINAL_DECISION_HASH}"
    )

    log(
        f"PERSISTENT_DISK_ROOT={PERSISTENT_DISK_ROOT}"
    )

    log(
        f"R35U_STATE_DIR={R35U_STATE_DIR}"
    )

    log(
        f"R35W_STATE_DIR={R35W_STATE_DIR}"
    )

    # -------------------------------------------------------------------------
    # TEST 1
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 1: HARD ZERO-WRITE FIREBREAK"
    )

    result(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    result(
        "First Real Order Not Allowed",
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

    result(
        "Telegram Processing Disabled",
        TELEGRAM_PROCESSING_ENABLED is False,
    )

    result(
        "Signal Parser Disabled",
        SIGNAL_PARSER_ENABLED is False,
    )

    result(
        "Signal Validator Disabled",
        SIGNAL_VALIDATOR_ENABLED is False,
    )

    result(
        "Synthetic Decision Creation Disabled",
        SYNTHETIC_DECISION_CREATION_ENABLED is False,
    )

    # -------------------------------------------------------------------------
    # TEST 2
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 2: R35U PERSISTENT STATE DIRECTORY"
    )

    state_dir_exists = os.path.isdir(
        R35U_STATE_DIR
    )

    result(
        "R35U State Directory Exists",
        state_dir_exists,
    )

    all_files = list_state_files()

    log(
        f"R35U_STATE_FILE_COUNT={len(all_files)}"
    )

    for index, path in enumerate(
        all_files,
        start=1,
    ):
        try:
            size = os.path.getsize(path)
        except Exception:
            size = -1

        log(
            f"R35U_STATE_FILE_{index}={path} SIZE={size}"
        )

    result(
        "R35U State Directory Contains Files",
        len(all_files) > 0,
    )

    # -------------------------------------------------------------------------
    # TEST 3
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 3: DISCOVER JSON REGISTRIES"
    )

    json_files = discover_json_files()

    log(
        f"R35U_JSON_FILE_COUNT={len(json_files)}"
    )

    dedupe_file = choose_best_file(
        json_files,
        DEDUPE_FILENAME_CANDIDATES,
        [
            "dedupe",
            "telegram",
            "update",
            "marker",
        ],
    )

    decision_file = choose_best_file(
        json_files,
        DECISION_FILENAME_CANDIDATES,
        [
            "decision",
            "synthetic",
        ],
    )

    log(
        f"DISCOVERED_DEDUPE_FILE={dedupe_file}"
    )

    log(
        f"DISCOVERED_DECISION_FILE={decision_file}"
    )

    result(
        "Dedupe Registry File Discovered",
        dedupe_file is not None,
    )

    result(
        "Decision Registry File Discovered",
        decision_file is not None,
    )

    # -------------------------------------------------------------------------
    # TEST 4
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 4: LOAD DISCOVERED R35U REGISTRIES"
    )

    dedupe_registry = None
    decision_registry = None

    dedupe_load_ok = False
    decision_load_ok = False

    if dedupe_file:

        try:
            dedupe_registry = read_json_file(
                dedupe_file
            )

            dedupe_load_ok = True

        except Exception as exc:

            log(
                f"DEDUPE_LOAD_EXCEPTION_CLASS={exc.__class__.__name__}"
            )

            log(
                f"DEDUPE_LOAD_EXCEPTION_MESSAGE={exc}"
            )

    if decision_file:

        try:
            decision_registry = read_json_file(
                decision_file
            )

            decision_load_ok = True

        except Exception as exc:

            log(
                f"DECISION_LOAD_EXCEPTION_CLASS={exc.__class__.__name__}"
            )

            log(
                f"DECISION_LOAD_EXCEPTION_MESSAGE={exc}"
            )

    result(
        "R35U Durable Dedupe Registry Loaded",
        dedupe_load_ok,
    )

    result(
        "R35U Durable Decision Registry Loaded",
        decision_load_ok,
    )

    # -------------------------------------------------------------------------
    # TEST 5
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 5: RAW DEDUPE REGISTRY FORENSICS"
    )

    dedupe_key_discovered = False
    dedupe_matches = []

    if dedupe_load_ok:

        log(
            "R35U_DEDUPE_REGISTRY_RAW_BEGIN"
        )

        print(
            safe_repr(
                dedupe_registry,
                max_len=20000,
            ),
            flush=True,
        )

        log(
            "R35U_DEDUPE_REGISTRY_RAW_END"
        )

        if isinstance(
            dedupe_registry,
            dict,
        ):

            top_keys = list(
                dedupe_registry.keys()
            )

            log(
                f"DEDUPE_TOP_LEVEL_KEY_COUNT={len(top_keys)}"
            )

            for index, key in enumerate(
                top_keys,
                start=1,
            ):
                log(
                    f"DEDUPE_TOP_LEVEL_KEY_{index}={repr(key)}"
                )

        dedupe_matches = recursive_find_exact_value(
            dedupe_registry,
            TEST_TELEGRAM_UPDATE_ID,
        )

        dedupe_key_discovered = (
            len(dedupe_matches) > 0
        )

        log(
            f"DEDUPE_TEST_UPDATE_MATCH_COUNT={len(dedupe_matches)}"
        )

        for index, match in enumerate(
            dedupe_matches,
            start=1,
        ):

            log(
                f"DEDUPE_MATCH_{index}_TYPE={match['match_type']}"
            )

            log(
                f"DEDUPE_MATCH_{index}_PATH={match['path']}"
            )

            log(
                f"DEDUPE_MATCH_{index}_VALUE={safe_repr(match['value'])}"
            )

    result(
        "Expected R35U Telegram Update Representation Discovered",
        dedupe_key_discovered,
    )

    # -------------------------------------------------------------------------
    # TEST 6
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 6: RAW DECISION REGISTRY FORENSICS"
    )

    original_hash_found_in_registry = False

    if decision_load_ok:

        log(
            "R35U_DECISION_REGISTRY_RAW_BEGIN"
        )

        print(
            safe_repr(
                decision_registry,
                max_len=30000,
            ),
            flush=True,
        )

        log(
            "R35U_DECISION_REGISTRY_RAW_END"
        )

        hash_locations = recursive_find_hash(
            decision_registry,
            EXPECTED_ORIGINAL_DECISION_HASH,
        )

        original_hash_found_in_registry = (
            len(hash_locations) > 0
        )

        log(
            f"EXPECTED_DECISION_HASH_LOCATION_COUNT={len(hash_locations)}"
        )

        for index, location in enumerate(
            hash_locations,
            start=1,
        ):

            log(
                f"EXPECTED_HASH_LOCATION_{index}_PATH={location['path']}"
            )

            log(
                f"EXPECTED_HASH_LOCATION_{index}_KEY={location['key']}"
            )

    result(
        "Original R35U Stored Decision Hash Found",
        original_hash_found_in_registry,
    )

    # -------------------------------------------------------------------------
    # TEST 7
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 7: DECISION HASH REPRODUCTION SEARCH"
    )

    stored_hash_reproduced = False
    winning_match = None
    hash_attempt_count = 0

    if decision_load_ok:

        candidates = candidate_payloads(
            decision_registry
        )

        log(
            f"HASH_CANDIDATE_PAYLOAD_COUNT={len(candidates)}"
        )

        for candidate_index, (
            candidate_path,
            candidate_label,
            payload,
        ) in enumerate(
            candidates,
            start=1,
        ):

            variants = test_hash_variants(
                payload
            )

            for variant in variants:

                if "sha256" not in variant:
                    continue

                hash_attempt_count += 1

                digest = variant["sha256"]

                if digest == EXPECTED_ORIGINAL_DECISION_HASH:

                    stored_hash_reproduced = True

                    winning_match = {
                        "candidate_index": candidate_index,
                        "candidate_path": candidate_path,
                        "candidate_label": candidate_label,
                        "serializer": variant["serializer"],
                        "sha256": digest,
                        "serialized": variant["serialized"],
                    }

                    break

            if stored_hash_reproduced:
                break

    log(
        f"HASH_REPRODUCTION_ATTEMPT_COUNT={hash_attempt_count}"
    )

    result(
        "Stored Decision Hash Reproduced",
        stored_hash_reproduced,
    )

    if winning_match:

        log(
            f"HASH_MATCH_CANDIDATE_INDEX={winning_match['candidate_index']}"
        )

        log(
            f"HASH_MATCH_CANDIDATE_PATH={winning_match['candidate_path']}"
        )

        log(
            f"HASH_MATCH_CANDIDATE_LABEL={winning_match['candidate_label']}"
        )

        log(
            f"HASH_MATCH_SERIALIZER={winning_match['serializer']}"
        )

        log(
            f"HASH_MATCH_SHA256={winning_match['sha256']}"
        )

        log(
            "HASH_MATCH_CANONICAL_SERIALIZATION_BEGIN"
        )

        print(
            winning_match["serialized"],
            flush=True,
        )

        log(
            "HASH_MATCH_CANONICAL_SERIALIZATION_END"
        )

    # -------------------------------------------------------------------------
    # TEST 8
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 8: RAW JSON FILE BYTE HASHES"
    )

    raw_file_hashes = {}

    for label, path in [
        (
            "DEDUPE",
            dedupe_file,
        ),
        (
            "DECISION",
            decision_file,
        ),
    ]:

        if not path:
            continue

        try:

            raw_text = read_text_file(
                path
            )

            raw_hash = sha256_text(
                raw_text
            )

            raw_file_hashes[label] = (
                raw_hash
            )

            log(
                f"{label}_RAW_FILE_SHA256={raw_hash}"
            )

            log(
                f"{label}_RAW_FILE_CHARACTER_COUNT={len(raw_text)}"
            )

        except Exception as exc:

            log(
                f"{label}_RAW_FILE_HASH_EXCEPTION={repr(exc)}"
            )

    result(
        "Dedupe Raw File SHA256 Calculated",
        "DEDUPE" in raw_file_hashes,
    )

    result(
        "Decision Raw File SHA256 Calculated",
        "DECISION" in raw_file_hashes,
    )

    # -------------------------------------------------------------------------
    # TEST 9
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 9: CONFIRM ZERO PIPELINE ENTRY"
    )

    result(
        "Telegram Processing Was Never Attempted",
        TELEGRAM_PROCESSING_ATTEMPTS == 0,
    )

    result(
        "Parser Entry Count Remains Zero",
        SIGNAL_PARSE_COUNT == 0,
    )

    result(
        "Validator Entry Count Remains Zero",
        SIGNAL_VALIDATION_COUNT == 0,
    )

    result(
        "Synthetic Decision Creation Count Remains Zero",
        SYNTHETIC_DECISION_CREATION_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    # TEST 10
    # -------------------------------------------------------------------------

    section(
        "R35W TEST 10: FINAL ZERO-WRITE FIREBREAK"
    )

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

    # -------------------------------------------------------------------------
    # FINAL STATUS
    # -------------------------------------------------------------------------

    R35W_DEDUPE_REGISTRY_RAW_READ_OK = (
        dedupe_load_ok
    )

    R35W_EXPECTED_UPDATE_KEY_DISCOVERED = (
        dedupe_key_discovered
    )

    R35W_DEDUPE_SCHEMA_IDENTIFIED = (
        dedupe_load_ok
        and dedupe_key_discovered
    )

    R35W_DECISION_RAW_READ_OK = (
        decision_load_ok
    )

    R35W_STORED_HASH_REPRODUCED = (
        stored_hash_reproduced
    )

    R35W_PROCESSING_ATTEMPTS = (
        TELEGRAM_PROCESSING_ATTEMPTS
        + SIGNAL_PARSE_COUNT
        + SIGNAL_VALIDATION_COUNT
        + SYNTHETIC_DECISION_CREATION_COUNT
    )

    ZERO_WRITE_FIREBREAK_OK = all(
        [
            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,
            REAL_ORDERS_SENT == 0,
            DEMO_ORDERS_SENT == 0,
            REAL_ORDER_EXECUTION is False,
            FIRST_REAL_ORDER_ALLOWED is False,
            DEMO_ORDER_EXECUTION is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
            ORDER_SUBMISSION_ENABLED is False,
        ]
    )

    TEST_STATUS = (
        "PASS"
        if (
            R35W_DEDUPE_REGISTRY_RAW_READ_OK
            and R35W_EXPECTED_UPDATE_KEY_DISCOVERED
            and R35W_DEDUPE_SCHEMA_IDENTIFIED
            and R35W_DECISION_RAW_READ_OK
            and R35W_STORED_HASH_REPRODUCED
            and R35W_PROCESSING_ATTEMPTS == 0
            and ZERO_WRITE_FIREBREAK_OK
        )
        else "FAIL"
    )

    section(
        "R35W: FINAL TEST SUMMARY"
    )

    log(
        f"PURPOSE={PURPOSE}"
    )

    log(
        f"TEST_TELEGRAM_UPDATE_ID={TEST_TELEGRAM_UPDATE_ID}"
    )

    log(
        f"EXPECTED_ORIGINAL_DECISION_HASH={EXPECTED_ORIGINAL_DECISION_HASH}"
    )

    log(
        f"DISCOVERED_DEDUPE_FILE={dedupe_file}"
    )

    log(
        f"DISCOVERED_DECISION_FILE={decision_file}"
    )

    log(
        f"R35W_DEDUPE_REGISTRY_RAW_READ_OK={R35W_DEDUPE_REGISTRY_RAW_READ_OK}"
    )

    log(
        f"R35W_EXPECTED_UPDATE_KEY_DISCOVERED={R35W_EXPECTED_UPDATE_KEY_DISCOVERED}"
    )

    log(
        f"R35W_DEDUPE_SCHEMA_IDENTIFIED={R35W_DEDUPE_SCHEMA_IDENTIFIED}"
    )

    log(
        f"R35W_DECISION_RAW_READ_OK={R35W_DECISION_RAW_READ_OK}"
    )

    log(
        f"ORIGINAL_STORED_DECISION_HASH_FOUND={original_hash_found_in_registry}"
    )

    log(
        f"R35W_STORED_HASH_REPRODUCED={R35W_STORED_HASH_REPRODUCED}"
    )

    if winning_match:

        log(
            f"WINNING_HASH_PATH={winning_match['candidate_path']}"
        )

        log(
            f"WINNING_HASH_SERIALIZER={winning_match['serializer']}"
        )

    log(
        f"R35W_PROCESSING_ATTEMPTS={R35W_PROCESSING_ATTEMPTS}"
    )

    log(
        f"TELEGRAM_PROCESSING_ATTEMPTS={TELEGRAM_PROCESSING_ATTEMPTS}"
    )

    log(
        f"SIGNAL_PARSE_COUNT={SIGNAL_PARSE_COUNT}"
    )

    log(
        f"SIGNAL_VALIDATION_COUNT={SIGNAL_VALIDATION_COUNT}"
    )

    log(
        f"SYNTHETIC_DECISION_CREATION_COUNT={SYNTHETIC_DECISION_CREATION_COUNT}"
    )

    log(
        f"ZERO_WRITE_FIREBREAK_OK={ZERO_WRITE_FIREBREAK_OK}"
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
        f"EXCHANGE_MUTATION_TRANSPORT_ENABLED={EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )

    log(
        f"ORDER_SUBMISSION_ENABLED={ORDER_SUBMISSION_ENABLED}"
    )

    # -------------------------------------------------------------------------
    # HEARTBEAT
    # -------------------------------------------------------------------------

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: "
            f"HEARTBEAT={heartbeat} "
            f"DEDUPE_RAW_READ_OK={R35W_DEDUPE_REGISTRY_RAW_READ_OK} "
            f"EXPECTED_UPDATE_DISCOVERED={R35W_EXPECTED_UPDATE_KEY_DISCOVERED} "
            f"DEDUPE_SCHEMA_IDENTIFIED={R35W_DEDUPE_SCHEMA_IDENTIFIED} "
            f"DECISION_RAW_READ_OK={R35W_DECISION_RAW_READ_OK} "
            f"STORED_HASH_REPRODUCED={R35W_STORED_HASH_REPRODUCED} "
            f"PROCESSING_ATTEMPTS={R35W_PROCESSING_ATTEMPTS} "
            f"TEST_STATUS={TEST_STATUS} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    main()

