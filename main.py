import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone


# =============================================================================
# R34E
# FINAL LIVE-STATE RECONCILIATION + STALE-STATE / TOCTOU READINESS
#
# SAFETY MODEL:
#   - AUTHENTICATED GET ONLY
#   - NO POST
#   - NO PUT
#   - NO PATCH
#   - NO DELETE
#   - NO REAL ORDERS
#   - NO DEMO ORDERS
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#
# PURPOSE:
#   1. Read live BTCUSDT symbol configuration.
#   2. Confirm ISOLATED margin configuration.
#   3. Confirm current long/short leverage.
#   4. Construct the exact proposed 100x/100x correction locally.
#   5. Bind the proposed correction to the first live state snapshot.
#   6. Perform a second authenticated live read.
#   7. Reject readiness if live configuration changed between reads.
#   8. Read current positions without modifying anything.
#   9. Produce a final PRE-MUTATION readiness seal.
#
# IMPORTANT:
#   THIS FILE DOES NOT PERFORM THE LEVERAGE CORRECTION.
# =============================================================================


VERSION = "R34E"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
POSITIONS_PATH = "/capi/v3/account/position/allPosition"

# This is retained only as a canonical target identifier.
# There is NO transport function in this program that can POST to it.
LEVERAGE_CORRECTION_PATH = "/capi/v3/account/leverage"

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = "100"
TARGET_SHORT_LEVERAGE = "100"

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))
HEARTBEAT_SECONDS = int(os.getenv("HEARTBEAT_SECONDS", "30"))

HTTP_TIMEOUT_SECONDS = 15


# =============================================================================
# ABSOLUTE SAFETY CONSTANTS
# =============================================================================

SYNTHETIC_ONLY = True
AUTHENTICATED_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

HTTP_POST_ENABLED = False
HTTP_PUT_ENABLED = False
HTTP_PATCH_ENABLED = False
HTTP_DELETE_ENABLED = False


# =============================================================================
# CREDENTIALS
# =============================================================================

API_KEY = (
    os.getenv("WEEX_API_KEY")
    or os.getenv("API_KEY")
    or ""
).strip()

API_SECRET = (
    os.getenv("WEEX_API_SECRET")
    or os.getenv("API_SECRET")
    or ""
).strip()

API_PASSPHRASE = (
    os.getenv("WEEX_API_PASSPHRASE")
    or os.getenv("API_PASSPHRASE")
    or ""
).strip()


# =============================================================================
# RUNTIME STATE
# =============================================================================

runtime = {
    "phase": "STARTING",

    "tests_passed": 0,
    "tests_failed": 0,

    "authenticated_gets": 0,

    "network_writes": 0,
    "real_orders": 0,
    "demo_orders": 0,

    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "synthetic_authorizations": 0,
    "synthetic_dispatches": 0,

    "stale_state_blocks": 0,
    "toctou_matches": 0,

    "observed_margin": "UNKNOWN",
    "observed_long": "UNKNOWN",
    "observed_short": "UNKNOWN",

    "second_margin": "UNKNOWN",
    "second_long": "UNKNOWN",
    "second_short": "UNKNOWN",

    "correction_required": False,
    "correction_ready": False,

    "positions_checked": False,
    "open_positions": 0,

    "snapshot_hash": "",
    "second_snapshot_hash": "",
    "correction_payload_hash": "",
    "readiness_hash": "",

    "heartbeat": 0,
}

runtime_lock = threading.Lock()


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

WIDTH = 100


def line():
    print("-" * WIDTH, flush=True)


def section(title):
    line()
    print(title, flush=True)
    line()


def check(label, condition):
    passed = bool(condition)

    with runtime_lock:
        if passed:
            runtime["tests_passed"] += 1
        else:
            runtime["tests_failed"] += 1

    result = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{label:<78} {result}",
        flush=True,
    )

    return passed


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.end_headers()
            return

        with runtime_lock:
            payload = {
                "status": "ok",
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": runtime["phase"],
                "authenticated_read_only": AUTHENTICATED_READ_ONLY_ENABLED,
                "network_writes": runtime["network_writes"],
                "leverage_mutations": runtime["leverage_mutations"],
                "correction_required": runtime["correction_required"],
                "correction_ready": runtime["correction_ready"],
                "observed_margin": runtime["observed_margin"],
                "observed_long": runtime["observed_long"],
                "observed_short": runtime["observed_short"],
                "target_long": TARGET_LONG_LEVERAGE,
                "target_short": TARGET_SHORT_LEVERAGE,
            }

        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():

    def serve():
        try:
            server = HTTPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            )

            print(
                f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:
            print(
                f"{VERSION}: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=serve,
        daemon=True,
    )

    thread.start()


# =============================================================================
# SIGNATURE
# =============================================================================

def create_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    method = method.upper()

    if query_string:
        message = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )
    else:
        message = (
            timestamp
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# =============================================================================
# THE ONLY AUTHENTICATED NETWORK TRANSPORT
#
# GET ONLY.
#
# There is deliberately no authenticated POST implementation in R34E.
# =============================================================================

def authenticated_get(request_path, params=None):

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only transport disabled"
        )

    if not API_KEY:
        raise RuntimeError(
            "WEEX API key is missing"
        )

    if not API_SECRET:
        raise RuntimeError(
            "WEEX API secret is missing"
        )

    if not API_PASSPHRASE:
        raise RuntimeError(
            "WEEX API passphrase is missing"
        )

    if not request_path.startswith("/"):
        raise RuntimeError(
            "Invalid request path"
        )

    params = params or {}

    query_string = urllib.parse.urlencode(params)

    timestamp = str(int(time.time() * 1000))

    signature = create_signature(
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-READ-ONLY",
    }

    url = BASE_URL + request_path

    if query_string:
        url += "?" + query_string

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode("utf-8")

            with runtime_lock:
                runtime["authenticated_gets"] += 1

            if not raw:
                return None

            return json.loads(raw)

    except urllib.error.HTTPError as exc:

        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = str(exc)

        raise RuntimeError(
            f"Authenticated GET failed HTTP {exc.code}: {detail}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Authenticated GET connection failure: {exc}"
        )


# =============================================================================
# HARD WRITE FIREBREAK
# =============================================================================

def blocked_exchange_write(
    method,
    path,
    payload=None,
):
    method = str(method).upper()

    raise RuntimeError(
        f"{VERSION} WRITE FIREBREAK: "
        f"{method} {path} rejected. "
        f"All exchange writes are disabled."
    )


# =============================================================================
# SYMBOL CONFIG NORMALIZATION
# =============================================================================

def find_symbol_config(response):

    if response is None:
        raise RuntimeError(
            "Symbol configuration response was empty"
        )

    candidates = []

    if isinstance(response, list):
        candidates = response

    elif isinstance(response, dict):

        if response.get("symbol"):
            candidates = [response]

        elif isinstance(response.get("data"), list):
            candidates = response["data"]

        elif isinstance(response.get("data"), dict):
            candidates = [response["data"]]

        elif isinstance(response.get("result"), list):
            candidates = response["result"]

        elif isinstance(response.get("result"), dict):
            candidates = [response["result"]]

    for item in candidates:

        if not isinstance(item, dict):
            continue

        item_symbol = str(
            item.get("symbol", "")
        ).upper()

        if item_symbol == SYMBOL:
            return item

    if len(candidates) == 1 and isinstance(candidates[0], dict):
        return candidates[0]

    raise RuntimeError(
        f"Could not locate symbol configuration for {SYMBOL}"
    )


def normalize_symbol_config(config):

    margin_type = str(
        config.get("marginType", "")
    ).upper()

    long_leverage = str(
        config.get("isolatedLongLeverage", "")
    )

    short_leverage = str(
        config.get("isolatedShortLeverage", "")
    )

    separated_type = str(
        config.get(
            "separatedType",
            config.get("separatedMode", ""),
        )
    ).upper()

    return {
        "symbol": SYMBOL,
        "marginType": margin_type,
        "separatedType": separated_type,
        "isolatedLongLeverage": long_leverage,
        "isolatedShortLeverage": short_leverage,
    }


def snapshot_hash(config):
    return sha256_text(
        canonical_json(config)
    )


# =============================================================================
# POSITION NORMALIZATION
# =============================================================================

def extract_positions(response):

    if response is None:
        return []

    if isinstance(response, list):
        return response

    if isinstance(response, dict):

        if isinstance(response.get("data"), list):
            return response["data"]

        if isinstance(response.get("result"), list):
            return response["result"]

        if response.get("symbol"):
            return [response]

    return []


def position_size(position):

    for key in (
        "size",
        "quantity",
        "positionAmt",
        "positionSize",
    ):
        if key in position:
            try:
                return abs(float(position[key]))
            except Exception:
                pass

    return 0.0


# =============================================================================
# LOCAL CORRECTION INTENT
# =============================================================================

def construct_correction_payload():

    return {
        "symbol": SYMBOL,
        "marginType": TARGET_MARGIN_TYPE,
        "isolatedLongLeverage": TARGET_LONG_LEVERAGE,
        "isolatedShortLeverage": TARGET_SHORT_LEVERAGE,
    }


# =============================================================================
# READINESS RECORD
# =============================================================================

def build_readiness_record(
    first_snapshot,
    second_snapshot,
    correction_payload,
    open_positions,
):

    return {
        "version": VERSION,
        "timestamp": utc_timestamp(),

        "symbol": SYMBOL,

        "firstSnapshotHash": snapshot_hash(first_snapshot),
        "secondSnapshotHash": snapshot_hash(second_snapshot),

        "liveStateStable": first_snapshot == second_snapshot,

        "observedMarginType": second_snapshot["marginType"],
        "observedLongLeverage":
            second_snapshot["isolatedLongLeverage"],
        "observedShortLeverage":
            second_snapshot["isolatedShortLeverage"],

        "targetMarginType": TARGET_MARGIN_TYPE,
        "targetLongLeverage": TARGET_LONG_LEVERAGE,
        "targetShortLeverage": TARGET_SHORT_LEVERAGE,

        "correctionRequired": (
            second_snapshot["marginType"] != TARGET_MARGIN_TYPE
            or second_snapshot["isolatedLongLeverage"]
            != TARGET_LONG_LEVERAGE
            or second_snapshot["isolatedShortLeverage"]
            != TARGET_SHORT_LEVERAGE
        ),

        "openPositions": open_positions,

        "correctionPayloadHash":
            sha256_text(
                canonical_json(correction_payload)
            ),

        "endpoint": LEVERAGE_CORRECTION_PATH,

        "syntheticOnly": True,
        "networkWrite": False,
        "exchangeMutation": False,

        "realExecutionEnabled": False,
        "leverageMutationEnabled": False,
    }


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def run_validation():

    section(f"{VERSION}: MAIN.PY ENTERED")

    print(f"{VERSION}: SYMBOL={SYMBOL}", flush=True)
    print(f"{VERSION}: VERSION={VERSION}", flush=True)
    print(f"{VERSION}: BASE URL={BASE_URL}", flush=True)
    print(f"{VERSION}: HEALTH PORT={HEALTH_PORT}", flush=True)

    print(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED",
        flush=True,
    )

    print(
        f"{VERSION}: STANDARD LIBRARY HTTP ENABLED",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG={TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT={TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )


    # =========================================================================
    section("R34E TEST 1: ABSOLUTE SAFETY CONFIGURATION")
    # =========================================================================

    check(
        "Synthetic Only Is Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED is True,
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )


    # =========================================================================
    section("R34E TEST 2: HTTP WRITE FIREBREAK")
    # =========================================================================

    check(
        "HTTP POST Is Disabled",
        HTTP_POST_ENABLED is False,
    )

    check(
        "HTTP PUT Is Disabled",
        HTTP_PUT_ENABLED is False,
    )

    check(
        "HTTP PATCH Is Disabled",
        HTTP_PATCH_ENABLED is False,
    )

    check(
        "HTTP DELETE Is Disabled",
        HTTP_DELETE_ENABLED is False,
    )

    blocked = False

    try:
        blocked_exchange_write(
            "POST",
            LEVERAGE_CORRECTION_PATH,
            {},
        )
    except RuntimeError:
        blocked = True

    check(
        "Direct Exchange Write Attempt Is Rejected",
        blocked,
    )

    check(
        "Network Write Counter Remains Zero",
        runtime["network_writes"] == 0,
    )


    # =========================================================================
    section("R34E TEST 3: AUTHENTICATION CREDENTIAL PRESENCE")
    # =========================================================================

    check(
        "API Key Is Present",
        bool(API_KEY),
    )

    check(
        "API Secret Is Present",
        bool(API_SECRET),
    )

    check(
        "API Passphrase Is Present",
        bool(API_PASSPHRASE),
    )

    if not API_KEY or not API_SECRET or not API_PASSPHRASE:
        raise RuntimeError(
            "Required authenticated-read credentials are missing"
        )


    # =========================================================================
    section("R34E TEST 4: FIRST LIVE SYMBOL CONFIGURATION SNAPSHOT")
    # =========================================================================

    first_response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {"symbol": SYMBOL},
    )

    first_raw_config = find_symbol_config(
        first_response
    )

    first_snapshot = normalize_symbol_config(
        first_raw_config
    )

    first_hash = snapshot_hash(
        first_snapshot
    )

    with runtime_lock:
        runtime["observed_margin"] = (
            first_snapshot["marginType"]
        )
        runtime["observed_long"] = (
            first_snapshot["isolatedLongLeverage"]
        )
        runtime["observed_short"] = (
            first_snapshot["isolatedShortLeverage"]
        )
        runtime["snapshot_hash"] = first_hash

    print(
        f"{VERSION}: FIRST LIVE SNAPSHOT="
        f"{canonical_json(first_snapshot)}",
        flush=True,
    )

    print(
        f"{VERSION}: FIRST SNAPSHOT SHA256={first_hash}",
        flush=True,
    )

    check(
        "Live Symbol Matches Requested Symbol",
        first_snapshot["symbol"] == SYMBOL,
    )

    check(
        "Observed Margin Type Is Present",
        bool(first_snapshot["marginType"]),
    )

    check(
        "Observed Long Leverage Is Present",
        bool(first_snapshot["isolatedLongLeverage"]),
    )

    check(
        "Observed Short Leverage Is Present",
        bool(first_snapshot["isolatedShortLeverage"]),
    )

    check(
        "Observed Margin Is ISOLATED",
        first_snapshot["marginType"]
        == TARGET_MARGIN_TYPE,
    )


    # =========================================================================
    section("R34E TEST 5: LIVE CORRECTION REQUIREMENT")
    # =========================================================================

    correction_required = (
        first_snapshot["marginType"]
        != TARGET_MARGIN_TYPE

        or first_snapshot["isolatedLongLeverage"]
        != TARGET_LONG_LEVERAGE

        or first_snapshot["isolatedShortLeverage"]
        != TARGET_SHORT_LEVERAGE
    )

    with runtime_lock:
        runtime["correction_required"] = (
            correction_required
        )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{first_snapshot['marginType']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{first_snapshot['isolatedLongLeverage']}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{first_snapshot['isolatedShortLeverage']}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    check(
        "100x / 100x Correction Is Still Required",
        correction_required,
    )


    # =========================================================================
    section("R34E TEST 6: CANONICAL CORRECTION PAYLOAD")
    # =========================================================================

    correction_payload = (
        construct_correction_payload()
    )

    correction_body = canonical_json(
        correction_payload
    )

    correction_payload_hash = sha256_text(
        correction_body
    )

    with runtime_lock:
        runtime["correction_payload_hash"] = (
            correction_payload_hash
        )

    print(
        f"{VERSION}: CORRECTION ENDPOINT="
        f"{LEVERAGE_CORRECTION_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: CANONICAL PAYLOAD="
        f"{correction_body}",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION PAYLOAD SHA256="
        f"{correction_payload_hash}",
        flush=True,
    )

    check(
        "Correction Endpoint Is Exact V3 Endpoint",
        LEVERAGE_CORRECTION_PATH
        == "/capi/v3/account/leverage",
    )

    check(
        "Correction Payload Symbol Matches",
        correction_payload["symbol"] == SYMBOL,
    )

    check(
        "Correction Payload Margin Is ISOLATED",
        correction_payload["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Correction Payload Long Target Is Exactly 100x",
        correction_payload["isolatedLongLeverage"]
        == "100",
    )

    check(
        "Correction Payload Short Target Is Exactly 100x",
        correction_payload["isolatedShortLeverage"]
        == "100",
    )


    # =========================================================================
    section("R34E TEST 7: FIRST-SNAPSHOT BINDING")
    # =========================================================================

    correction_intent = {
        "version": VERSION,
        "symbol": SYMBOL,

        "sourceSnapshotHash": first_hash,

        "observedMargin":
            first_snapshot["marginType"],

        "observedLongLeverage":
            first_snapshot["isolatedLongLeverage"],

        "observedShortLeverage":
            first_snapshot["isolatedShortLeverage"],

        "targetMargin": TARGET_MARGIN_TYPE,
        "targetLongLeverage":
            TARGET_LONG_LEVERAGE,
        "targetShortLeverage":
            TARGET_SHORT_LEVERAGE,

        "payloadHash":
            correction_payload_hash,

        "endpoint":
            LEVERAGE_CORRECTION_PATH,

        "syntheticOnly": True,
        "networkWrite": False,
        "mutation": False,
    }

    correction_intent_hash = sha256_text(
        canonical_json(correction_intent)
    )

    print(
        f"{VERSION}: CORRECTION INTENT SHA256="
        f"{correction_intent_hash}",
        flush=True,
    )

    check(
        "Correction Intent Binds First Snapshot",
        correction_intent["sourceSnapshotHash"]
        == first_hash,
    )

    check(
        "Correction Intent Binds Payload Hash",
        correction_intent["payloadHash"]
        == correction_payload_hash,
    )

    check(
        "Correction Intent Declares Synthetic Only",
        correction_intent["syntheticOnly"]
        is True,
    )

    check(
        "Correction Intent Declares No Network Write",
        correction_intent["networkWrite"]
        is False,
    )

    check(
        "Correction Intent Declares No Mutation",
        correction_intent["mutation"]
        is False,
    )


    # =========================================================================
    section("R34E TEST 8: READ-ONLY POSITION RECONCILIATION")
    # =========================================================================

    positions_response = authenticated_get(
        POSITIONS_PATH
    )

    positions = extract_positions(
        positions_response
    )

    symbol_positions = []

    for position in positions:

        if not isinstance(position, dict):
            continue

        position_symbol = str(
            position.get("symbol", "")
        ).upper()

        if position_symbol == SYMBOL:
            symbol_positions.append(position)

    open_positions = sum(
        1
        for position in symbol_positions
        if position_size(position) > 0
    )

    with runtime_lock:
        runtime["positions_checked"] = True
        runtime["open_positions"] = open_positions

    print(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(symbol_positions)}",
        flush=True,
    )

    print(
        f"{VERSION}: {SYMBOL} OPEN POSITIONS="
        f"{open_positions}",
        flush=True,
    )

    check(
        "Position Reconciliation Completed",
        runtime["positions_checked"] is True,
    )

    check(
        "Position Read Caused No Network Write",
        runtime["network_writes"] == 0,
    )

    check(
        "Position Read Caused No Position Mutation",
        runtime["position_mutations"] == 0,
    )


    # =========================================================================
    section("R34E TEST 9: SECOND LIVE SYMBOL CONFIGURATION SNAPSHOT")
    # =========================================================================

    second_response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {"symbol": SYMBOL},
    )

    second_raw_config = find_symbol_config(
        second_response
    )

    second_snapshot = normalize_symbol_config(
        second_raw_config
    )

    second_hash = snapshot_hash(
        second_snapshot
    )

    with runtime_lock:

        runtime["second_margin"] = (
            second_snapshot["marginType"]
        )

        runtime["second_long"] = (
            second_snapshot["isolatedLongLeverage"]
        )

        runtime["second_short"] = (
            second_snapshot["isolatedShortLeverage"]
        )

        runtime["second_snapshot_hash"] = (
            second_hash
        )

    print(
        f"{VERSION}: SECOND LIVE SNAPSHOT="
        f"{canonical_json(second_snapshot)}",
        flush=True,
    )

    print(
        f"{VERSION}: SECOND SNAPSHOT SHA256="
        f"{second_hash}",
        flush=True,
    )

    check(
        "Second Snapshot Symbol Matches",
        second_snapshot["symbol"] == SYMBOL,
    )

    check(
        "Second Snapshot Margin Is ISOLATED",
        second_snapshot["marginType"]
        == TARGET_MARGIN_TYPE,
    )


    # =========================================================================
    section("R34E TEST 10: TOCTOU / STALE-STATE PROTECTION")
    # =========================================================================

    state_unchanged = (
        first_snapshot == second_snapshot
    )

    if state_unchanged:

        with runtime_lock:
            runtime["toctou_matches"] += 1

    else:

        with runtime_lock:
            runtime["stale_state_blocks"] += 1

    check(
        "First And Second Live Snapshots Match",
        state_unchanged,
    )

    check(
        "First And Second Snapshot Hashes Match",
        first_hash == second_hash,
    )

    check(
        "Margin Type Did Not Change Between Reads",
        first_snapshot["marginType"]
        == second_snapshot["marginType"],
    )

    check(
        "Long Leverage Did Not Change Between Reads",
        first_snapshot["isolatedLongLeverage"]
        == second_snapshot["isolatedLongLeverage"],
    )

    check(
        "Short Leverage Did Not Change Between Reads",
        first_snapshot["isolatedShortLeverage"]
        == second_snapshot["isolatedShortLeverage"],
    )

    check(
        "No Stale-State Block Was Required",
        runtime["stale_state_blocks"] == 0,
    )

    if not state_unchanged:
        raise RuntimeError(
            "R34E STALE-STATE FIREBREAK: "
            "live account configuration changed between reads"
        )


    # =========================================================================
    section("R34E TEST 11: SECOND-SNAPSHOT CORRECTION REQUIREMENT")
    # =========================================================================

    second_correction_required = (
        second_snapshot["marginType"]
        != TARGET_MARGIN_TYPE

        or second_snapshot["isolatedLongLeverage"]
        != TARGET_LONG_LEVERAGE

        or second_snapshot["isolatedShortLeverage"]
        != TARGET_SHORT_LEVERAGE
    )

    check(
        "Correction Is Still Required After Reconciliation",
        second_correction_required,
    )

    check(
        "Second Snapshot Still Targets ISOLATED",
        second_snapshot["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    check(
        "Long Target Remains Exactly 100x",
        TARGET_LONG_LEVERAGE == "100",
    )

    check(
        "Short Target Remains Exactly 100x",
        TARGET_SHORT_LEVERAGE == "100",
    )


    # =========================================================================
    section("R34E TEST 12: PRE-MUTATION READINESS RECORD")
    # =========================================================================

    readiness_record = build_readiness_record(
        first_snapshot=first_snapshot,
        second_snapshot=second_snapshot,
        correction_payload=correction_payload,
        open_positions=open_positions,
    )

    readiness_hash = sha256_text(
        canonical_json(readiness_record)
    )

    with runtime_lock:
        runtime["readiness_hash"] = (
            readiness_hash
        )

    print(
        f"{VERSION}: READINESS SHA256="
        f"{readiness_hash}",
        flush=True,
    )

    check(
        "Readiness Record Binds Stable Live State",
        readiness_record["liveStateStable"]
        is True,
    )

    check(
        "Readiness Record Binds Correction Requirement",
        readiness_record["correctionRequired"]
        is True,
    )

    check(
        "Readiness Record Declares Synthetic Only",
        readiness_record["syntheticOnly"]
        is True,
    )

    check(
        "Readiness Record Declares No Network Write",
        readiness_record["networkWrite"]
        is False,
    )

    check(
        "Readiness Record Declares No Exchange Mutation",
        readiness_record["exchangeMutation"]
        is False,
    )

    check(
        "Readiness Record Binds Exact V3 Endpoint",
        readiness_record["endpoint"]
        == LEVERAGE_CORRECTION_PATH,
    )

    check(
        "Readiness Payload Hash Matches Canonical Payload",
        readiness_record["correctionPayloadHash"]
        == correction_payload_hash,
    )


    # =========================================================================
    section("R34E TEST 13: TERMINAL WRITE-LOCK COUNTERS")
    # =========================================================================

    check(
        "Authenticated GET Counter Is Three",
        runtime["authenticated_gets"] == 3,
    )

    check(
        "Network Write Counter Is Zero",
        runtime["network_writes"] == 0,
    )

    check(
        "Real Order Counter Is Zero",
        runtime["real_orders"] == 0,
    )

    check(
        "Demo Order Counter Is Zero",
        runtime["demo_orders"] == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        runtime["leverage_mutations"] == 0,
    )

    check(
        "Margin Mutation Counter Is Zero",
        runtime["margin_mutations"] == 0,
    )

    check(
        "Position Mutation Counter Is Zero",
        runtime["position_mutations"] == 0,
    )

    check(
        "Account Mutation Counter Is Zero",
        runtime["account_mutations"] == 0,
    )


    # =========================================================================
    section("R34E TEST 14: FINAL PRE-MUTATION SAFETY SEAL")
    # =========================================================================

    final_ready = (
        SYNTHETIC_ONLY is True
        and AUTHENTICATED_READ_ONLY_ENABLED is True

        and REAL_ORDER_EXECUTION_ENABLED is False
        and DEMO_ORDER_EXECUTION_ENABLED is False

        and EXCHANGE_NETWORK_WRITES_ENABLED is False

        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
        and ACCOUNT_MUTATION_ENABLED is False

        and HTTP_POST_ENABLED is False
        and HTTP_PUT_ENABLED is False
        and HTTP_PATCH_ENABLED is False
        and HTTP_DELETE_ENABLED is False

        and state_unchanged

        and second_snapshot["marginType"]
        == TARGET_MARGIN_TYPE

        and second_correction_required

        and runtime["network_writes"] == 0
        and runtime["leverage_mutations"] == 0
        and runtime["real_orders"] == 0
    )

    with runtime_lock:
        runtime["correction_ready"] = final_ready

        if final_ready:
            runtime["phase"] = (
                "PRE_MUTATION_READINESS_VALIDATED"
            )
        else:
            runtime["phase"] = (
                "PRE_MUTATION_READINESS_REJECTED"
            )

    check(
        "Synthetic-Only Mode Remains Enabled",
        SYNTHETIC_ONLY is True,
    )

    check(
        "Authenticated Read-Only Remains Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED is True,
    )

    check(
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Network Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "HTTP POST Remains Disabled",
        HTTP_POST_ENABLED is False,
    )

    check(
        "HTTP PUT Remains Disabled",
        HTTP_PUT_ENABLED is False,
    )

    check(
        "HTTP PATCH Remains Disabled",
        HTTP_PATCH_ENABLED is False,
    )

    check(
        "HTTP DELETE Remains Disabled",
        HTTP_DELETE_ENABLED is False,
    )

    check(
        "Exact V3 Leverage Endpoint Remains Bound",
        LEVERAGE_CORRECTION_PATH
        == "/capi/v3/account/leverage",
    )

    check(
        "Exact 100x Long Target Remains Bound",
        TARGET_LONG_LEVERAGE == "100",
    )

    check(
        "Exact 100x Short Target Remains Bound",
        TARGET_SHORT_LEVERAGE == "100",
    )

    check(
        "Live State Remained Stable Across Reconciliation",
        state_unchanged,
    )

    check(
        "Final Pre-Mutation Readiness Is Validated",
        final_ready,
    )


    # =========================================================================
    section("R34E VALIDATION SUMMARY")
    # =========================================================================

    print(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{runtime['authenticated_gets']}",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES="
        f"{runtime['network_writes']}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDERS="
        f"{runtime['real_orders']}",
        flush=True,
    )

    print(
        f"{VERSION}: DEMO ORDERS="
        f"{runtime['demo_orders']}",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{runtime['leverage_mutations']}",
        flush=True,
    )

    print(
        f"{VERSION}: MARGIN MUTATIONS="
        f"{runtime['margin_mutations']}",
        flush=True,
    )

    print(
        f"{VERSION}: POSITION MUTATIONS="
        f"{runtime['position_mutations']}",
        flush=True,
    )

    print(
        f"{VERSION}: ACCOUNT MUTATIONS="
        f"{runtime['account_mutations']}",
        flush=True,
    )

    print(
        f"{VERSION}: TOCTOU MATCHES="
        f"{runtime['toctou_matches']}",
        flush=True,
    )

    print(
        f"{VERSION}: STALE STATE BLOCKS="
        f"{runtime['stale_state_blocks']}",
        flush=True,
    )

    print(
        f"{VERSION}: OPEN POSITIONS="
        f"{runtime['open_positions']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{runtime['second_margin']}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{runtime['second_long']}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{runtime['second_short']}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{second_correction_required}",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION READY="
        f"{runtime['correction_ready']}",
        flush=True,
    )

    print(
        f"{VERSION}: ENDPOINT="
        f"{LEVERAGE_CORRECTION_PATH}",
        flush=True,
    )

    print(
        f"{VERSION}: FIRST SNAPSHOT HASH="
        f"{first_hash}",
        flush=True,
    )

    print(
        f"{VERSION}: SECOND SNAPSHOT HASH="
        f"{second_hash}",
        flush=True,
    )

    print(
        f"{VERSION}: PAYLOAD HASH="
        f"{correction_payload_hash}",
        flush=True,
    )

    print(
        f"{VERSION}: READINESS HASH="
        f"{readiness_hash}",
        flush=True,
    )

    print(
        f"{VERSION}: TESTS PASSED="
        f"{runtime['tests_passed']}",
        flush=True,
    )

    print(
        f"{VERSION}: TESTS FAILED="
        f"{runtime['tests_failed']}",
        flush=True,
    )

    print(
        f"{VERSION}: PHASE="
        f"{runtime['phase']}",
        flush=True,
    )

    result = (
        "PASSED"
        if runtime["tests_failed"] == 0
        else "FAILED"
    )

    print(
        f"{VERSION}: RESULT={result}",
        flush=True,
    )

    print(
        f"{VERSION}: NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: NO EXCHANGE WRITE WAS SENT",
        flush=True,
    )

    print(
        f"{VERSION}: NO LEVERAGE MUTATION WAS PERFORMED",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE LEVERAGE POST REMAINS DISABLED",
        flush=True,
    )

    line()

    if runtime["tests_failed"] != 0:
        raise RuntimeError(
            f"{VERSION} validation failed with "
            f"{runtime['tests_failed']} failed checks"
        )


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop():

    while True:

        with runtime_lock:

            runtime["heartbeat"] += 1

            heartbeat = runtime["heartbeat"]
            phase = runtime["phase"]

            authenticated_gets = (
                runtime["authenticated_gets"]
            )

            network_writes = (
                runtime["network_writes"]
            )

            leverage_mutations = (
                runtime["leverage_mutations"]
            )

            correction_required = (
                runtime["correction_required"]
            )

            correction_ready = (
                runtime["correction_ready"]
            )

            observed_margin = (
                runtime["second_margin"]
                if runtime["second_margin"]
                != "UNKNOWN"
                else runtime["observed_margin"]
            )

            observed_long = (
                runtime["second_long"]
                if runtime["second_long"]
                != "UNKNOWN"
                else runtime["observed_long"]
            )

            observed_short = (
                runtime["second_short"]
                if runtime["second_short"]
                != "UNKNOWN"
                else runtime["observed_short"]
            )

            open_positions = (
                runtime["open_positions"]
            )

            stale_blocks = (
                runtime["stale_state_blocks"]
            )

        print(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"phase={phase} | "
            f"synthetic-only={SYNTHETIC_ONLY} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED} | "
            f"authenticated-get={authenticated_gets} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"network-write-counter={network_writes} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"leverage-mutation-counter="
            f"{leverage_mutations} | "
            f"stale-state-blocked={stale_blocks} | "
            f"open-positions={open_positions} | "
            f"correction-required="
            f"{correction_required} | "
            f"correction-ready="
            f"{correction_ready} | "
            f"observed-margin={observed_margin} | "
            f"observed-long={observed_long}x | "
            f"observed-short={observed_short}x | "
            f"target-long={TARGET_LONG_LEVERAGE}x | "
            f"target-short={TARGET_SHORT_LEVERAGE}x",
            flush=True,
        )

        time.sleep(HEARTBEAT_SECONDS)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():

    start_health_server()

    try:
        run_validation()

    except Exception as exc:

        with runtime_lock:
            runtime["phase"] = "VALIDATION_FAILED"

        section(f"{VERSION}: FATAL VALIDATION ERROR")

        print(
            f"{VERSION}: {type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            f"{VERSION}: NETWORK WRITES="
            f"{runtime['network_writes']}",
            flush=True,
        )

        print(
            f"{VERSION}: REAL ORDERS="
            f"{runtime['real_orders']}",
            flush=True,
        )

        print(
            f"{VERSION}: LEVERAGE MUTATIONS="
            f"{runtime['leverage_mutations']}",
            flush=True,
        )

        print(
            f"{VERSION}: NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            f"{VERSION}: NO EXCHANGE WRITE WAS SENT",
            flush=True,
        )

        print(
            f"{VERSION}: NO LEVERAGE MUTATION WAS PERFORMED",
            flush=True,
        )

        line()

    heartbeat_loop()


if __name__ == "__main__":
    main()
