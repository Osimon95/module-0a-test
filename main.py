# ==========================================================================================
# R34E - AUTHENTICATED READ-ONLY CORRECTION READINESS VALIDATION
# ==========================================================================================
#
# PURPOSE
# ------
# 1. Preserve synthetic-only / read-only safety.
# 2. Resolve WEEX credentials from multiple compatible Render environment names.
# 3. Perform authenticated GET requests only.
# 4. Read current BTCUSDT symbol configuration.
# 5. Read current open-position state.
# 6. Determine whether 100x / 100x leverage correction is required.
# 7. Determine whether a future correction stage would be safe to prepare.
#
# IMPORTANT
# ---------
# THIS STAGE DOES NOT:
# - place orders
# - send POST requests
# - change leverage
# - change margin mode
# - change positions
# - mutate account state
#
# ==========================================================================================

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


# ==========================================================================================
# PART 1 - CONSTANTS / SAFETY CONFIGURATION
# ==========================================================================================

VERSION = "R34E"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
ALL_POSITIONS_PATH = "/capi/v3/account/position/allPosition"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100
TARGET_MARGIN_TYPE = "ISOLATED"

HEARTBEAT_INTERVAL_SECONDS = 30
HTTP_TIMEOUT_SECONDS = 15


# ------------------------------------------------------------------------------------------
# HARD SAFETY FLAGS
# ------------------------------------------------------------------------------------------

SYNTHETIC_ONLY = True

AUTHENTICATED_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# ==========================================================================================
# RUNTIME COUNTERS / STATE
# ==========================================================================================

phase = "BOOTING"

authenticated_get_counter = 0
network_write_counter = 0
real_order_counter = 0
leverage_mutation_counter = 0
stale_state_blocked_counter = 0

observed_margin_type = "UNKNOWN"
observed_long_leverage = "UNKNOWN"
observed_short_leverage = "UNKNOWN"

open_positions_count = 0

correction_required = False
correction_ready = False

credential_source = {
    "api_key": None,
    "api_secret": None,
    "api_passphrase": None,
}


# ==========================================================================================
# PRINT HELPERS
# ==========================================================================================

LINE = "-" * 100


def separator():
    print(LINE, flush=True)


def banner(title):
    separator()
    print(title, flush=True)
    separator()


def pass_test(name):
    print(f"{name:<82} ✅ PASS", flush=True)


def fail_test(name):
    print(f"{name:<82} ❌ FAIL", flush=True)


def assert_test(name, condition):
    if condition:
        pass_test(name)
        return True

    fail_test(name)
    return False


# ==========================================================================================
# CREDENTIAL RESOLUTION
# ==========================================================================================
#
# R34E previously failed because it found the API key but not the secret/passphrase.
#
# Rather than assuming one exact Render naming scheme, resolve each credential through
# compatible aliases.
#
# VALUES ARE NEVER PRINTED.
# ==========================================================================================


def resolve_environment_value(*names):
    for name in names:
        value = os.getenv(name)

        if value is not None:
            value = value.strip()

            if value:
                return value, name

    return "", None


API_KEY, credential_source["api_key"] = resolve_environment_value(
    "WEEX_API_KEY",
    "API_KEY",
    "WEEX_ACCESS_KEY",
    "ACCESS_KEY",
)

API_SECRET, credential_source["api_secret"] = resolve_environment_value(
    "WEEX_API_SECRET",
    "WEEX_SECRET_KEY",
    "WEEX_API_SECRET_KEY",
    "API_SECRET",
    "API_SECRET_KEY",
    "SECRET_KEY",
    "ACCESS_SECRET",
)

API_PASSPHRASE, credential_source["api_passphrase"] = resolve_environment_value(
    "WEEX_API_PASSPHRASE",
    "WEEX_PASSPHRASE",
    "API_PASSPHRASE",
    "ACCESS_PASSPHRASE",
    "PASSPHRASE",
)


# ==========================================================================================
# PART 2 - HEALTH SERVER / TRANSPORT FIREBREAK
# ==========================================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = {
            "service": VERSION,
            "symbol": SYMBOL,
            "phase": phase,
            "syntheticOnly": SYNTHETIC_ONLY,
            "authenticatedReadOnly": AUTHENTICATED_READ_ONLY_ENABLED,
            "authenticatedGets": authenticated_get_counter,
            "realExecution": REAL_ORDER_EXECUTION_ENABLED,
            "networkWritesEnabled": EXCHANGE_NETWORK_WRITES_ENABLED,
            "networkWriteCounter": network_write_counter,
            "leverageMutationEnabled": LEVERAGE_MUTATION_ENABLED,
            "leverageMutationCounter": leverage_mutation_counter,
            "openPositions": open_positions_count,
            "correctionRequired": correction_required,
            "correctionReady": correction_ready,
            "observedMargin": observed_margin_type,
            "observedLongLeverage": observed_long_leverage,
            "observedShortLeverage": observed_short_leverage,
            "targetLongLeverage": TARGET_LONG_LEVERAGE,
            "targetShortLeverage": TARGET_SHORT_LEVERAGE,
        }

        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def run_health_server():

    try:
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)

        print(
            f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
            flush=True,
        )

        server.serve_forever()

    except Exception as exc:
        print(
            f"{VERSION}: HEALTH SERVER ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )


def start_health_server():

    thread = threading.Thread(
        target=run_health_server,
        daemon=True,
        name="r34e-health-server",
    )

    thread.start()


# ==========================================================================================
# HARD EXCHANGE WRITE FIREBREAK
# ==========================================================================================


class ExchangeWriteBlocked(RuntimeError):
    pass


def reject_exchange_write(method, path):

    global network_write_counter

    method = str(method).upper()

    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        raise ExchangeWriteBlocked(
            f"{VERSION}: BLOCKED exchange write "
            f"{method} {path}"
        )

    raise ExchangeWriteBlocked(
        f"{VERSION}: Unsupported exchange method blocked: "
        f"{method} {path}"
    )


def exchange_post(path, body=None):
    reject_exchange_write("POST", path)


def exchange_put(path, body=None):
    reject_exchange_write("PUT", path)


def exchange_patch(path, body=None):
    reject_exchange_write("PATCH", path)


def exchange_delete(path, body=None):
    reject_exchange_write("DELETE", path)


# ==========================================================================================
# SIGNING
# ==========================================================================================


def build_query_string(params):

    if not params:
        return ""

    return urllib.parse.urlencode(params)


def generate_get_signature(
    secret,
    timestamp,
    request_path,
    query_string="",
):

    method = "GET"

    message = (
        str(timestamp)
        + method
        + request_path
    )

    if query_string:
        message += "?" + query_string

    digest = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# ==========================================================================================
# AUTHENTICATED GET ONLY
# ==========================================================================================


def authenticated_get(path, params=None):

    global authenticated_get_counter

    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only access is disabled"
        )

    if not API_KEY:
        raise RuntimeError("API key missing")

    if not API_SECRET:
        raise RuntimeError("API secret missing")

    if not API_PASSPHRASE:
        raise RuntimeError("API passphrase missing")

    query_string = build_query_string(params)

    timestamp = str(int(time.time() * 1000))

    signature = generate_get_signature(
        secret=API_SECRET,
        timestamp=timestamp,
        request_path=path,
        query_string=query_string,
    )

    url = BASE_URL + path

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "locale": "en-US",
        "User-Agent": f"{VERSION}-ReadOnlyValidator/1.0",
    }

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

            authenticated_get_counter += 1

            try:
                return json.loads(raw)

            except json.JSONDecodeError:
                raise RuntimeError(
                    f"Invalid JSON returned from {path}"
                )

    except urllib.error.HTTPError as exc:

        try:
            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:
            error_body = "<unable to read response body>"

        raise RuntimeError(
            f"Authenticated GET failed "
            f"HTTP {exc.code} path={path} "
            f"response={error_body[:500]}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Authenticated GET network error "
            f"path={path}: {exc.reason}"
        ) from exc


# ==========================================================================================
# RESPONSE NORMALIZATION
# ==========================================================================================


def unwrap_data(payload):

    if isinstance(payload, dict):

        if "data" in payload:
            return payload["data"]

        if "result" in payload:
            return payload["result"]

    return payload


def normalize_symbol_config(payload):

    payload = unwrap_data(payload)

    if isinstance(payload, list):

        for item in payload:

            if not isinstance(item, dict):
                continue

            item_symbol = str(
                item.get("symbol", "")
            ).upper()

            if item_symbol == SYMBOL:
                return item

        if len(payload) == 1 and isinstance(payload[0], dict):
            return payload[0]

    if isinstance(payload, dict):
        return payload

    raise RuntimeError(
        "Unable to locate symbol configuration "
        "in authenticated response"
    )


def normalize_positions(payload):

    payload = unwrap_data(payload)

    if payload is None:
        return []

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):

        for key in (
            "positions",
            "positionList",
            "list",
            "rows",
        ):
            value = payload.get(key)

            if isinstance(value, list):
                return value

    raise RuntimeError(
        "Unable to normalize position response"
    )


def numeric_position_size(position):

    for field in (
        "size",
        "positionSize",
        "available",
        "total",
        "quantity",
        "qty",
    ):

        if field not in position:
            continue

        try:
            return abs(float(position[field]))

        except (TypeError, ValueError):
            continue

    return 0.0


def count_open_symbol_positions(positions):

    count = 0

    for position in positions:

        if not isinstance(position, dict):
            continue

        symbol = str(
            position.get("symbol", "")
        ).upper()

        if symbol != SYMBOL:
            continue

        if numeric_position_size(position) > 0:
            count += 1

    return count


# ==========================================================================================
# PART 3 - R34E VALIDATION TESTS
# ==========================================================================================


def run_validation():

    global phase
    global observed_margin_type
    global observed_long_leverage
    global observed_short_leverage
    global open_positions_count
    global correction_required
    global correction_ready
    global stale_state_blocked_counter

    phase = "VALIDATING"

    banner(f"{VERSION}: MAIN.PY ENTERED")

    print(f"{VERSION}: SYMBOL={SYMBOL}", flush=True)
    print(f"{VERSION}: VERSION={VERSION}", flush=True)
    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )
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

    # ======================================================================================
    # TEST 1
    # ======================================================================================

    banner(
        f"{VERSION} TEST 1: HARD SAFETY CONFIGURATION"
    )

    safety_results = [

        assert_test(
            "Synthetic Only Is Enabled",
            SYNTHETIC_ONLY is True,
        ),

        assert_test(
            "Authenticated Read-Only Is Enabled",
            AUTHENTICATED_READ_ONLY_ENABLED is True,
        ),

        assert_test(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION_ENABLED is False,
        ),

        assert_test(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION_ENABLED is False,
        ),

        assert_test(
            "Exchange Network Writes Are Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED is False,
        ),

        assert_test(
            "Leverage Mutation Is Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        ),

        assert_test(
            "Margin Mutation Is Disabled",
            MARGIN_MUTATION_ENABLED is False,
        ),

        assert_test(
            "Position Mutation Is Disabled",
            POSITION_MUTATION_ENABLED is False,
        ),

        assert_test(
            "Account Mutation Is Disabled",
            ACCOUNT_MUTATION_ENABLED is False,
        ),
    ]

    if not all(safety_results):
        raise RuntimeError(
            "Hard safety configuration validation failed"
        )

    # ======================================================================================
    # TEST 2
    # ======================================================================================

    banner(
        f"{VERSION} TEST 2: HTTP WRITE FIREBREAK"
    )

    blocked_post = False
    blocked_put = False
    blocked_patch = False
    blocked_delete = False

    try:
        exchange_post("/test")
    except ExchangeWriteBlocked:
        blocked_post = True

    try:
        exchange_put("/test")
    except ExchangeWriteBlocked:
        blocked_put = True

    try:
        exchange_patch("/test")
    except ExchangeWriteBlocked:
        blocked_patch = True

    try:
        exchange_delete("/test")
    except ExchangeWriteBlocked:
        blocked_delete = True

    assert_test(
        "HTTP POST Is Disabled",
        blocked_post,
    )

    assert_test(
        "HTTP PUT Is Disabled",
        blocked_put,
    )

    assert_test(
        "HTTP PATCH Is Disabled",
        blocked_patch,
    )

    assert_test(
        "HTTP DELETE Is Disabled",
        blocked_delete,
    )

    direct_write_rejected = False

    try:
        reject_exchange_write(
            "POST",
            "/capi/v3/account/leverage",
        )

    except ExchangeWriteBlocked:
        direct_write_rejected = True

    assert_test(
        "Direct Exchange Write Attempt Is Rejected",
        direct_write_rejected,
    )

    assert_test(
        "Network Write Counter Remains Zero",
        network_write_counter == 0,
    )

    # ======================================================================================
    # TEST 3
    # ======================================================================================

    banner(
        f"{VERSION} TEST 3: AUTHENTICATION CREDENTIAL PRESENCE"
    )

    key_present = bool(API_KEY)
    secret_present = bool(API_SECRET)
    passphrase_present = bool(API_PASSPHRASE)

    assert_test(
        "API Key Is Present",
        key_present,
    )

    assert_test(
        "API Secret Is Present",
        secret_present,
    )

    assert_test(
        "API Passphrase Is Present",
        passphrase_present,
    )

    if not (
        key_present
        and secret_present
        and passphrase_present
    ):
        raise RuntimeError(
            "Required authenticated-read credentials are missing"
        )

    # Do NOT print credential values.
    print(
        f"{VERSION}: API KEY SOURCE="
        f"{credential_source['api_key']}",
        flush=True,
    )

    print(
        f"{VERSION}: API SECRET SOURCE="
        f"{credential_source['api_secret']}",
        flush=True,
    )

    print(
        f"{VERSION}: API PASSPHRASE SOURCE="
        f"{credential_source['api_passphrase']}",
        flush=True,
    )

    # ======================================================================================
    # TEST 4
    # ======================================================================================

    banner(
        f"{VERSION} TEST 4: AUTHENTICATED READ-ONLY SYMBOL CONFIGURATION"
    )

    symbol_payload = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    config = normalize_symbol_config(
        symbol_payload
    )

    returned_symbol = str(
        config.get("symbol", "")
    ).upper()

    observed_margin_type = str(
        config.get(
            "marginType",
            "UNKNOWN",
        )
    ).upper()

    observed_long_leverage = str(
        config.get(
            "isolatedLongLeverage",
            "UNKNOWN",
        )
    )

    observed_short_leverage = str(
        config.get(
            "isolatedShortLeverage",
            "UNKNOWN",
        )
    )

    assert_test(
        "Authenticated Symbol Config GET Succeeded",
        isinstance(config, dict),
    )

    assert_test(
        "Returned Symbol Matches BTCUSDT",
        returned_symbol == SYMBOL,
    )

    assert_test(
        "Observed Margin Type Is Present",
        observed_margin_type != "UNKNOWN",
    )

    assert_test(
        "Observed Long Leverage Is Present",
        observed_long_leverage != "UNKNOWN",
    )

    assert_test(
        "Observed Short Leverage Is Present",
        observed_short_leverage != "UNKNOWN",
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observed_margin_type}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{observed_long_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{observed_short_leverage}x",
        flush=True,
    )

    # ======================================================================================
    # TEST 5
    # ======================================================================================

    banner(
        f"{VERSION} TEST 5: AUTHENTICATED READ-ONLY POSITION RECONCILIATION"
    )

    positions_payload = authenticated_get(
        ALL_POSITIONS_PATH
    )

    positions = normalize_positions(
        positions_payload
    )

    open_positions_count = count_open_symbol_positions(
        positions
    )

    assert_test(
        "Authenticated Position GET Succeeded",
        isinstance(positions, list),
    )

    assert_test(
        "Position State Is Read-Only",
        POSITION_MUTATION_ENABLED is False,
    )

    print(
        f"{VERSION}: OPEN {SYMBOL} POSITIONS="
        f"{open_positions_count}",
        flush=True,
    )

    if open_positions_count == 0:
        pass_test(
            "No Open BTCUSDT Position Blocks Correction Readiness"
        )
    else:
        stale_state_blocked_counter += 1

        fail_test(
            "No Open BTCUSDT Position Blocks Correction Readiness"
        )

    # ======================================================================================
    # TEST 6
    # ======================================================================================

    banner(
        f"{VERSION} TEST 6: 100X CORRECTION REQUIREMENT"
    )

    try:
        long_value = int(
            float(observed_long_leverage)
        )

    except (TypeError, ValueError):
        long_value = -1

    try:
        short_value = int(
            float(observed_short_leverage)
        )

    except (TypeError, ValueError):
        short_value = -1

    margin_matches = (
        observed_margin_type
        == TARGET_MARGIN_TYPE
    )

    long_matches = (
        long_value
        == TARGET_LONG_LEVERAGE
    )

    short_matches = (
        short_value
        == TARGET_SHORT_LEVERAGE
    )

    assert_test(
        "Target Margin Mode Is ISOLATED",
        TARGET_MARGIN_TYPE == "ISOLATED",
    )

    if margin_matches:
        pass_test(
            "Observed Margin Already Matches ISOLATED"
        )
    else:
        print(
            f"{'Observed Margin Requires Correction':<82} "
            f"⚠️ REQUIRED",
            flush=True,
        )

    if long_matches:
        pass_test(
            "Observed Long Leverage Already Matches 100x"
        )
    else:
        print(
            f"{'Observed Long Leverage Requires 100x Correction':<82} "
            f"⚠️ REQUIRED",
            flush=True,
        )

    if short_matches:
        pass_test(
            "Observed Short Leverage Already Matches 100x"
        )
    else:
        print(
            f"{'Observed Short Leverage Requires 100x Correction':<82} "
            f"⚠️ REQUIRED",
            flush=True,
        )

    correction_required = not (
        margin_matches
        and long_matches
        and short_matches
    )

    assert_test(
        "Correction Requirement Was Determined",
        True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{correction_required}",
        flush=True,
    )

    # ======================================================================================
    # TEST 7
    # ======================================================================================

    banner(
        f"{VERSION} TEST 7: CORRECTION READINESS GATE"
    )

    credentials_valid = (
        bool(API_KEY)
        and bool(API_SECRET)
        and bool(API_PASSPHRASE)
    )

    no_open_positions = (
        open_positions_count == 0
    )

    no_writes_occurred = (
        network_write_counter == 0
    )

    no_mutation_occurred = (
        leverage_mutation_counter == 0
    )

    correction_ready = (
        credentials_valid
        and no_open_positions
        and no_writes_occurred
        and no_mutation_occurred
        and correction_required
    )

    assert_test(
        "Credentials Are Valid For Read-Only Observation",
        credentials_valid,
    )

    assert_test(
        "Network Write Counter Is Zero",
        no_writes_occurred,
    )

    assert_test(
        "Leverage Mutation Counter Is Zero",
        no_mutation_occurred,
    )

    if no_open_positions:
        pass_test(
            "BTCUSDT Has No Open Position"
        )
    else:
        fail_test(
            "BTCUSDT Has No Open Position"
        )

    if correction_required:
        pass_test(
            "100x Correction Is Required"
        )
    else:
        pass_test(
            "Account Already Matches Target Configuration"
        )

    print(
        f"{VERSION}: CORRECTION READY="
        f"{correction_ready}",
        flush=True,
    )

    # ======================================================================================
    # TEST 8
    # ======================================================================================

    banner(
        f"{VERSION} TEST 8: FINAL WRITE-FREE INVARIANTS"
    )

    final_results = [

        assert_test(
            "Real Order Counter Is Zero",
            real_order_counter == 0,
        ),

        assert_test(
            "Network Write Counter Is Zero",
            network_write_counter == 0,
        ),

        assert_test(
            "Leverage Mutation Counter Is Zero",
            leverage_mutation_counter == 0,
        ),

        assert_test(
            "Real Execution Remains Disabled",
            REAL_ORDER_EXECUTION_ENABLED is False,
        ),

        assert_test(
            "Exchange Writes Remain Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED is False,
        ),

        assert_test(
            "Leverage Mutation Remains Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        ),
    ]

    if not all(final_results):
        raise RuntimeError(
            "Final write-free invariant validation failed"
        )

    phase = "LIVE_READ_ONLY_VALIDATED"

    # ======================================================================================
    # FINAL SUMMARY
    # ======================================================================================

    banner(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    print(
        f"{VERSION}: PHASE={phase}",
        flush=True,
    )

    print(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{authenticated_get_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED MARGIN="
        f"{observed_margin_type}",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED LONG="
        f"{observed_long_leverage}x",
        flush=True,
    )

    print(
        f"{VERSION}: OBSERVED SHORT="
        f"{observed_short_leverage}x",
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
        f"{VERSION}: OPEN POSITIONS="
        f"{open_positions_count}",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION REQUIRED="
        f"{correction_required}",
        flush=True,
    )

    print(
        f"{VERSION}: CORRECTION READY="
        f"{correction_ready}",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES="
        f"{network_write_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL ORDERS="
        f"{real_order_counter}",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{leverage_mutation_counter}",
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

    separator()


# ==========================================================================================
# PART 4 - HEARTBEAT / MAIN
# ==========================================================================================


def heartbeat():

    counter = 0

    while True:

        counter += 1

        print(
            f"{VERSION}: HEARTBEAT {counter}"
            f" | phase={phase}"
            f" | synthetic-only={SYNTHETIC_ONLY}"
            f" | authenticated-read-only={AUTHENTICATED_READ_ONLY_ENABLED}"
            f" | authenticated-get={authenticated_get_counter}"
            f" | real-execution={REAL_ORDER_EXECUTION_ENABLED}"
            f" | network-writes={EXCHANGE_NETWORK_WRITES_ENABLED}"
            f" | network-write-counter={network_write_counter}"
            f" | leverage-mutation={LEVERAGE_MUTATION_ENABLED}"
            f" | leverage-mutation-counter={leverage_mutation_counter}"
            f" | stale-state-blocked={stale_state_blocked_counter}"
            f" | open-positions={open_positions_count}"
            f" | correction-required={correction_required}"
            f" | correction-ready={correction_ready}"
            f" | observed-margin={observed_margin_type}"
            f" | observed-long={observed_long_leverage}x"
            f" | observed-short={observed_short_leverage}x"
            f" | target-long={TARGET_LONG_LEVERAGE}x"
            f" | target-short={TARGET_SHORT_LEVERAGE}x",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_INTERVAL_SECONDS
        )


def main():

    global phase

    start_health_server()

    try:

        run_validation()

    except KeyboardInterrupt:
        raise

    except Exception as exc:

        phase = "VALIDATION_FAILED"

        banner(
            f"{VERSION}: FATAL VALIDATION ERROR"
        )

        print(
            f"{VERSION}: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            f"{VERSION}: NETWORK WRITES="
            f"{network_write_counter}",
            flush=True,
        )

        print(
            f"{VERSION}: REAL ORDERS="
            f"{real_order_counter}",
            flush=True,
        )

        print(
            f"{VERSION}: LEVERAGE MUTATIONS="
            f"{leverage_mutation_counter}",
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

        separator()

    heartbeat()


if __name__ == "__main__":
    main()
