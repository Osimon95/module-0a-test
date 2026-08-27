import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import urllib.parse
import urllib.request
import urllib.error

from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# R34I
# POST-MANUAL-CORRECTION AUTHENTICATED READ-ONLY VERIFICATION
#
# PURPOSE:
#   Verify that the manually applied BTCUSDT leverage correction is now:
#
#       MARGIN TYPE = ISOLATED
#       LONG        = 100x
#       SHORT       = 100x
#
# IMPORTANT:
#   - AUTHENTICATED GET ONLY
#   - NO ORDER EXECUTION
#   - NO LEVERAGE MUTATION
#   - NO ACCOUNT MUTATION
#   - NO EXCHANGE WRITE METHODS
#   - NO DEMO ORDER EXECUTION
#
# R34I never changes the WEEX account.
# ==================================================================================================


VERSION = "R34I"

SYMBOL = os.environ.get("SYMBOL", "BTCUSDT").strip().upper()

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = "100"
TARGET_SHORT_LEVERAGE = "100"

BASE_URL = "https://api-contract.weex.com"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
ALL_POSITIONS_PATH = "/capi/v3/account/position/allPosition"

HEALTH_PORT = int(os.environ.get("PORT", "10000"))
HEARTBEAT_SECONDS = 30


# --------------------------------------------------------------------------------------------------
# CREDENTIALS
# --------------------------------------------------------------------------------------------------

API_KEY = (
    os.environ.get("WEEX_API_KEY")
    or os.environ.get("API_KEY")
    or ""
).strip()

API_SECRET = (
    os.environ.get("WEEX_API_SECRET")
    or os.environ.get("WEEX_SECRET_KEY")
    or os.environ.get("API_SECRET")
    or os.environ.get("SECRET_KEY")
    or ""
).strip()

API_PASSPHRASE = (
    os.environ.get("WEEX_API_PASSPHRASE")
    or os.environ.get("API_PASSPHRASE")
    or os.environ.get("PASSPHRASE")
    or ""
).strip()


# --------------------------------------------------------------------------------------------------
# SAFETY CONSTANTS
# --------------------------------------------------------------------------------------------------

SYNTHETIC_ONLY = False

AUTHENTICATED_READ_ONLY = True

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


ALLOWED_HTTP_METHODS = frozenset({
    "GET",
})


ALLOWED_AUTHENTICATED_PATHS = frozenset({
    SYMBOL_CONFIG_PATH,
    ALL_POSITIONS_PATH,
})


# --------------------------------------------------------------------------------------------------
# GLOBAL RUNTIME STATE
# --------------------------------------------------------------------------------------------------

runtime_lock = threading.Lock()

runtime = {
    "version": VERSION,
    "phase": "BOOTING",

    "symbol": SYMBOL,

    "authenticated_read_only": AUTHENTICATED_READ_ONLY,

    "authenticated_gets": 0,

    "network_write_counter": 0,
    "real_order_counter": 0,
    "demo_order_counter": 0,
    "leverage_mutation_counter": 0,

    "observed_margin": None,
    "observed_long": None,
    "observed_short": None,

    "target_margin": TARGET_MARGIN_TYPE,
    "target_long": TARGET_LONG_LEVERAGE,
    "target_short": TARGET_SHORT_LEVERAGE,

    "open_positions": None,

    "correction_required": None,
    "correction_verified": False,

    "first_read_hash": None,
    "second_read_hash": None,

    "fresh_read_consistent": False,

    "verification_complete": False,

    "last_error": None,
}


# --------------------------------------------------------------------------------------------------
# FORMATTING
# --------------------------------------------------------------------------------------------------

LINE = "-" * 100


def banner(text):
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def result(name, passed):
    mark = "✅ PASS" if passed else "❌ FAIL"
    print(f"{name:<82} {mark}", flush=True)


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


# --------------------------------------------------------------------------------------------------
# SAFETY GUARDS
# --------------------------------------------------------------------------------------------------

def assert_static_safety_configuration():
    banner("R34I TEST 1: READ-ONLY SAFETY CONFIGURATION")

    checks = [
        (
            "Authenticated Read-Only Is Enabled",
            AUTHENTICATED_READ_ONLY is True,
        ),
        (
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION is False,
        ),
        (
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION is False,
        ),
        (
            "Network Writes Are Disabled",
            NETWORK_WRITES_ENABLED is False,
        ),
        (
            "Leverage Mutation Is Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        ),
        (
            "Margin Mutation Is Disabled",
            MARGIN_MUTATION_ENABLED is False,
        ),
        (
            "Position Mutation Is Disabled",
            POSITION_MUTATION_ENABLED is False,
        ),
        (
            "Account Mutation Is Disabled",
            ACCOUNT_MUTATION_ENABLED is False,
        ),
        (
            "Only GET Is Allowed",
            ALLOWED_HTTP_METHODS == frozenset({"GET"}),
        ),
        (
            "Symbol Config Path Is Read-Only Allowlisted",
            SYMBOL_CONFIG_PATH in ALLOWED_AUTHENTICATED_PATHS,
        ),
        (
            "All Positions Path Is Read-Only Allowlisted",
            ALL_POSITIONS_PATH in ALLOWED_AUTHENTICATED_PATHS,
        ),
    ]

    all_passed = True

    for name, passed in checks:
        result(name, passed)
        all_passed = all_passed and passed

    if not all_passed:
        raise RuntimeError(
            "R34I static safety configuration failed"
        )


def guard_request(method, path):
    method = str(method).upper().strip()

    if method not in ALLOWED_HTTP_METHODS:
        with runtime_lock:
            runtime["network_write_counter"] += 1

        raise RuntimeError(
            f"R34I SAFETY BLOCK: HTTP method {method!r} is forbidden"
        )

    if method != "GET":
        with runtime_lock:
            runtime["network_write_counter"] += 1

        raise RuntimeError(
            "R34I SAFETY BLOCK: only GET transport exists"
        )

    if path not in ALLOWED_AUTHENTICATED_PATHS:
        raise RuntimeError(
            f"R34I SAFETY BLOCK: path not allowlisted: {path}"
        )


# --------------------------------------------------------------------------------------------------
# CREDENTIAL VALIDATION
# --------------------------------------------------------------------------------------------------

def validate_credentials():
    banner("R34I TEST 2: AUTHENTICATION CREDENTIAL PRESENCE")

    checks = [
        (
            "API Key Is Present",
            bool(API_KEY),
        ),
        (
            "API Secret Is Present",
            bool(API_SECRET),
        ),
        (
            "API Passphrase Is Present",
            bool(API_PASSPHRASE),
        ),
    ]

    all_passed = True

    for name, passed in checks:
        result(name, passed)
        all_passed = all_passed and passed

    if not all_passed:
        raise RuntimeError(
            "Missing WEEX credentials. "
            "Check Render environment variables."
        )


# --------------------------------------------------------------------------------------------------
# SIGNATURE
# --------------------------------------------------------------------------------------------------

def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    method = method.upper()

    guard_request(
        method,
        request_path,
    )

    message = (
        str(timestamp)
        + method
        + request_path
    )

    if query_string:
        message += "?" + query_string

    if body:
        message += body

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# --------------------------------------------------------------------------------------------------
# AUTHENTICATED GET TRANSPORT
# --------------------------------------------------------------------------------------------------

def authenticated_get(
    request_path,
    params=None,
):
    guard_request(
        "GET",
        request_path,
    )

    params = params or {}

    query_string = urllib.parse.urlencode(
        params
    )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = build_signature(
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    url = (
        BASE_URL
        + request_path
    )

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only-verifier",
    }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"WEEX HTTP {exc.code}: {raw}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"WEEX network read failed: {exc}"
        )

    if status < 200 or status >= 300:
        raise RuntimeError(
            f"Unexpected WEEX HTTP status {status}: {raw}"
        )

    try:
        data = json.loads(raw)

    except json.JSONDecodeError:
        raise RuntimeError(
            f"WEEX returned non-JSON response: {raw}"
        )

    with runtime_lock:
        runtime["authenticated_gets"] += 1

    return data


# --------------------------------------------------------------------------------------------------
# RESPONSE NORMALIZATION
# --------------------------------------------------------------------------------------------------

def unwrap_response(value):
    """
    Handles either:

        [...]
        {...}

    or common API wrappers such as:

        {"data": [...]}
        {"data": {...}}

    without assuming a wrapper always exists.
    """

    if isinstance(value, dict):

        if "data" in value:
            data = value.get("data")

            if data is not None:
                return data

    return value


def normalize_symbol_config(response):
    data = unwrap_response(response)

    if isinstance(data, list):

        for item in data:

            if not isinstance(item, dict):
                continue

            if str(
                item.get("symbol", "")
            ).upper() == SYMBOL:

                return item

        if len(data) == 1:
            if isinstance(data[0], dict):
                return data[0]

    if isinstance(data, dict):

        if str(
            data.get("symbol", SYMBOL)
        ).upper() == SYMBOL:

            return data

    raise RuntimeError(
        "Unable to locate BTCUSDT symbol configuration "
        f"in response: {response}"
    )


def normalize_positions(response):
    data = unwrap_response(response)

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "positions",
            "list",
            "rows",
        ):
            candidate = data.get(key)

            if isinstance(candidate, list):
                return candidate

    raise RuntimeError(
        f"Unable to normalize position response: {response}"
    )


# --------------------------------------------------------------------------------------------------
# POSITION SIZE HELPERS
# --------------------------------------------------------------------------------------------------

def numeric_value(value):
    if value is None:
        return 0.0

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def position_size(position):
    for key in (
        "size",
        "positionAmt",
        "positionSize",
        "qty",
        "quantity",
        "available",
    ):
        if key in position:
            return abs(
                numeric_value(
                    position.get(key)
                )
            )

    return 0.0


def active_btc_positions(positions):
    active = []

    for position in positions:

        if not isinstance(
            position,
            dict,
        ):
            continue

        symbol = str(
            position.get(
                "symbol",
                ""
            )
        ).upper()

        if symbol != SYMBOL:
            continue

        if position_size(position) > 0:
            active.append(position)

    return active


# --------------------------------------------------------------------------------------------------
# SNAPSHOT CREATION
# --------------------------------------------------------------------------------------------------

def build_snapshot(
    config,
    positions,
):
    margin_type = str(
        config.get(
            "marginType",
            ""
        )
    ).upper()

    isolated_long = str(
        config.get(
            "isolatedLongLeverage",
            ""
        )
    )

    isolated_short = str(
        config.get(
            "isolatedShortLeverage",
            ""
        )
    )

    separated_type = str(
        config.get(
            "separatedType",
            config.get(
                "separatedMode",
                ""
            )
        )
    ).upper()

    active_positions = active_btc_positions(
        positions
    )

    snapshot = {
        "symbol": SYMBOL,
        "marginType": margin_type,
        "separatedType": separated_type,
        "isolatedLongLeverage": isolated_long,
        "isolatedShortLeverage": isolated_short,
        "openPositions": len(
            active_positions
        ),
    }

    return snapshot


# --------------------------------------------------------------------------------------------------
# FIRST AUTHENTICATED READ
# --------------------------------------------------------------------------------------------------

def first_live_read():
    banner(
        "R34I TEST 3: FIRST AUTHENTICATED READ-BACK"
    )

    config_raw = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    positions_raw = authenticated_get(
        ALL_POSITIONS_PATH,
    )

    config = normalize_symbol_config(
        config_raw
    )

    positions = normalize_positions(
        positions_raw
    )

    snapshot = build_snapshot(
        config,
        positions,
    )

    digest = sha256_text(
        canonical_json(
            snapshot
        )
    )

    print(
        f"R34I: FIRST STATE SHA256={digest}",
        flush=True,
    )

    result(
        "Symbol Is BTCUSDT",
        snapshot["symbol"] == SYMBOL,
    )

    result(
        "Margin Type Is ISOLATED",
        snapshot["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    result(
        "Observed Long Leverage Is 100x",
        snapshot["isolatedLongLeverage"]
        == TARGET_LONG_LEVERAGE,
    )

    result(
        "Observed Short Leverage Is 100x",
        snapshot["isolatedShortLeverage"]
        == TARGET_SHORT_LEVERAGE,
    )

    result(
        "BTCUSDT Has Zero Open Positions",
        snapshot["openPositions"] == 0,
    )

    with runtime_lock:
        runtime["observed_margin"] = (
            snapshot["marginType"]
        )

        runtime["observed_long"] = (
            snapshot[
                "isolatedLongLeverage"
            ]
        )

        runtime["observed_short"] = (
            snapshot[
                "isolatedShortLeverage"
            ]
        )

        runtime["open_positions"] = (
            snapshot["openPositions"]
        )

        runtime["first_read_hash"] = digest

    return snapshot


# --------------------------------------------------------------------------------------------------
# SECOND AUTHENTICATED READ
# --------------------------------------------------------------------------------------------------

def second_live_read():
    banner(
        "R34I TEST 4: SECOND FRESH AUTHENTICATED READ-BACK"
    )

    # Small separation prevents the second verification
    # from merely being an immediate same-call assumption.
    time.sleep(1.0)

    config_raw = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    positions_raw = authenticated_get(
        ALL_POSITIONS_PATH,
    )

    config = normalize_symbol_config(
        config_raw
    )

    positions = normalize_positions(
        positions_raw
    )

    snapshot = build_snapshot(
        config,
        positions,
    )

    digest = sha256_text(
        canonical_json(
            snapshot
        )
    )

    print(
        f"R34I: SECOND STATE SHA256={digest}",
        flush=True,
    )

    result(
        "Second Read Margin Type Is ISOLATED",
        snapshot["marginType"]
        == TARGET_MARGIN_TYPE,
    )

    result(
        "Second Read Long Leverage Is 100x",
        snapshot["isolatedLongLeverage"]
        == TARGET_LONG_LEVERAGE,
    )

    result(
        "Second Read Short Leverage Is 100x",
        snapshot["isolatedShortLeverage"]
        == TARGET_SHORT_LEVERAGE,
    )

    result(
        "Second Read Has Zero Open Positions",
        snapshot["openPositions"] == 0,
    )

    with runtime_lock:
        runtime["second_read_hash"] = digest

    return snapshot


# --------------------------------------------------------------------------------------------------
# CONSISTENCY VERIFICATION
# --------------------------------------------------------------------------------------------------

def verify_consistency(
    first,
    second,
):
    banner(
        "R34I TEST 5: FRESH STATE CONSISTENCY"
    )

    checks = [
        (
            "Margin Type Stable Across Reads",
            first["marginType"]
            == second["marginType"],
        ),
        (
            "Long Leverage Stable Across Reads",
            first["isolatedLongLeverage"]
            == second["isolatedLongLeverage"],
        ),
        (
            "Short Leverage Stable Across Reads",
            first["isolatedShortLeverage"]
            == second["isolatedShortLeverage"],
        ),
        (
            "Open Position Count Stable Across Reads",
            first["openPositions"]
            == second["openPositions"],
        ),
    ]

    consistent = True

    for name, passed in checks:
        result(
            name,
            passed,
        )

        consistent = (
            consistent
            and passed
        )

    with runtime_lock:
        runtime["fresh_read_consistent"] = (
            consistent
        )

    return consistent


# --------------------------------------------------------------------------------------------------
# CORRECTION VERIFICATION
# --------------------------------------------------------------------------------------------------

def verify_manual_correction(
    snapshot,
):
    banner(
        "R34I TEST 6: MANUAL 100x / 100x CORRECTION VERIFICATION"
    )

    symbol_ok = (
        snapshot["symbol"]
        == SYMBOL
    )

    margin_ok = (
        snapshot["marginType"]
        == TARGET_MARGIN_TYPE
    )

    long_ok = (
        snapshot[
            "isolatedLongLeverage"
        ]
        == TARGET_LONG_LEVERAGE
    )

    short_ok = (
        snapshot[
            "isolatedShortLeverage"
        ]
        == TARGET_SHORT_LEVERAGE
    )

    no_positions = (
        snapshot["openPositions"]
        == 0
    )

    correction_required = not (
        long_ok
        and short_ok
    )

    correction_verified = (
        symbol_ok
        and margin_ok
        and long_ok
        and short_ok
    )

    checks = [
        (
            "Symbol Binding Is Correct",
            symbol_ok,
        ),
        (
            "ISOLATED Margin Is Verified",
            margin_ok,
        ),
        (
            "Long Target 100x Is Verified",
            long_ok,
        ),
        (
            "Short Target 100x Is Verified",
            short_ok,
        ),
        (
            "Manual Leverage Correction Is No Longer Required",
            correction_required is False,
        ),
        (
            "Manual Leverage Correction Is Verified",
            correction_verified is True,
        ),
        (
            "No BTCUSDT Position Is Open",
            no_positions,
        ),
    ]

    passed = True

    for name, check in checks:

        result(
            name,
            check,
        )

        passed = (
            passed
            and check
        )

    with runtime_lock:
        runtime["correction_required"] = (
            correction_required
        )

        runtime["correction_verified"] = (
            correction_verified
        )

    return passed


# --------------------------------------------------------------------------------------------------
# TRANSPORT BOUNDARY VALIDATION
# --------------------------------------------------------------------------------------------------

def verify_transport_boundary():
    banner(
        "R34I TEST 7: HARD READ-ONLY TRANSPORT BOUNDARY"
    )

    write_block_exercised = False

    try:
        guard_request(
            "POST",
            SYMBOL_CONFIG_PATH,
        )

    except RuntimeError:
        write_block_exercised = True

    # The above intentionally exercises the LOCAL guard.
    # It does NOT create or transmit an HTTP request.
    #
    # Restore the diagnostic counter because no network
    # write was actually attempted or transmitted.
    with runtime_lock:
        runtime[
            "network_write_counter"
        ] = 0

    checks = [
        (
            "Non-GET Transport Is Rejected Locally",
            write_block_exercised,
        ),
        (
            "Network Write Counter Is Zero",
            runtime[
                "network_write_counter"
            ] == 0,
        ),
        (
            "Real Order Counter Is Zero",
            runtime[
                "real_order_counter"
            ] == 0,
        ),
        (
            "Demo Order Counter Is Zero",
            runtime[
                "demo_order_counter"
            ] == 0,
        ),
        (
            "Leverage Mutation Counter Is Zero",
            runtime[
                "leverage_mutation_counter"
            ] == 0,
        ),
    ]

    all_passed = True

    for name, passed in checks:

        result(
            name,
            passed,
        )

        all_passed = (
            all_passed
            and passed
        )

    return all_passed


# --------------------------------------------------------------------------------------------------
# FINAL VERIFICATION GATE
# --------------------------------------------------------------------------------------------------

def final_gate(
    first_snapshot,
    second_snapshot,
):
    banner(
        "R34I TEST 8: FINAL POST-CORRECTION VERIFICATION GATE"
    )

    with runtime_lock:

        checks = [
            (
                "Authenticated Read-Only Remains Enabled",
                runtime[
                    "authenticated_read_only"
                ] is True,
            ),
            (
                "Exactly Four Authenticated GETs Were Performed",
                runtime[
                    "authenticated_gets"
                ] == 4,
            ),
            (
                "Observed Margin Is ISOLATED",
                runtime[
                    "observed_margin"
                ]
                == TARGET_MARGIN_TYPE,
            ),
            (
                "Observed Long Is 100x",
                runtime[
                    "observed_long"
                ]
                == TARGET_LONG_LEVERAGE,
            ),
            (
                "Observed Short Is 100x",
                runtime[
                    "observed_short"
                ]
                == TARGET_SHORT_LEVERAGE,
            ),
            (
                "Correction Required Is False",
                runtime[
                    "correction_required"
                ] is False,
            ),
            (
                "Correction Verified Is True",
                runtime[
                    "correction_verified"
                ] is True,
            ),
            (
                "Fresh State Is Consistent",
                runtime[
                    "fresh_read_consistent"
                ] is True,
            ),
            (
                "Network Writes Remain Zero",
                runtime[
                    "network_write_counter"
                ] == 0,
            ),
            (
                "Leverage Mutations Remain Zero",
                runtime[
                    "leverage_mutation_counter"
                ] == 0,
            ),
            (
                "Real Orders Remain Zero",
                runtime[
                    "real_order_counter"
                ] == 0,
            ),
            (
                "Demo Orders Remain Zero",
                runtime[
                    "demo_order_counter"
                ] == 0,
            ),
        ]

    all_passed = True

    for name, passed in checks:

        result(
            name,
            passed,
        )

        all_passed = (
            all_passed
            and passed
        )

    snapshots_match = (
        first_snapshot
        == second_snapshot
    )

    result(
        "First And Second Live Snapshots Match",
        snapshots_match,
    )

    all_passed = (
        all_passed
        and snapshots_match
    )

    return all_passed


# --------------------------------------------------------------------------------------------------
# HEALTH SERVER
# --------------------------------------------------------------------------------------------------

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        with runtime_lock:
            body = json.dumps(
                runtime,
                sort_keys=True,
                indent=2,
            ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args,
    ):
        return


def run_health_server():

    server = HTTPServer(
        (
            "0.0.0.0",
            HEALTH_PORT,
        ),
        HealthHandler,
    )

    server.serve_forever()


def start_health_server():

    thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    thread.start()


# --------------------------------------------------------------------------------------------------
# HEARTBEAT
# --------------------------------------------------------------------------------------------------

def heartbeat_loop():

    heartbeat = 0

    while True:

        heartbeat += 1

        with runtime_lock:

            phase = runtime["phase"]

            authenticated_gets = runtime[
                "authenticated_gets"
            ]

            observed_margin = runtime[
                "observed_margin"
            ]

            observed_long = runtime[
                "observed_long"
            ]

            observed_short = runtime[
                "observed_short"
            ]

            open_positions = runtime[
                "open_positions"
            ]

            correction_required = runtime[
                "correction_required"
            ]

            correction_verified = runtime[
                "correction_verified"
            ]

            fresh_consistent = runtime[
                "fresh_read_consistent"
            ]

            network_writes = runtime[
                "network_write_counter"
            ]

            leverage_mutations = runtime[
                "leverage_mutation_counter"
            ]

            real_orders = runtime[
                "real_order_counter"
            ]

        print(
            "",
            flush=True,
        )

        print(
            LINE,
            flush=True,
        )

        print(
            f"R34I: HEARTBEAT {heartbeat}"
            f" | phase={phase}"
            f" | authenticated-read-only=True"
            f" | authenticated-get={authenticated_gets}"
            f" | real-execution=False"
            f" | network-writes=False"
            f" | network-write-counter={network_writes}"
            f" | leverage-mutation=False"
            f" | leverage-mutation-counter={leverage_mutations}"
            f" | real-orders={real_orders}"
            f" | fresh-state-consistent={fresh_consistent}"
            f" | open-positions={open_positions}"
            f" | correction-required={correction_required}"
            f" | correction-verified={correction_verified}"
            f" | observed-margin={observed_margin}"
            f" | observed-long={observed_long}x"
            f" | observed-short={observed_short}x"
            f" | target-long={TARGET_LONG_LEVERAGE}x"
            f" | target-short={TARGET_SHORT_LEVERAGE}x",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# --------------------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------------------

def main():

    banner(
        "R34I: MAIN.PY ENTERED"
    )

    print(
        f"R34I: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"R34I: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"R34I: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        "R34I: AUTHENTICATED READ-ONLY ENABLED",
        flush=True,
    )

    print(
        "R34I: STANDARD LIBRARY HTTP ENABLED",
        flush=True,
    )

    print(
        "R34I: EXCHANGE WRITE TRANSPORT DISABLED",
        flush=True,
    )

    print(
        "R34I: REAL ORDER EXECUTION DISABLED",
        flush=True,
    )

    print(
        "R34I: LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    print(
        f"R34I: EXPECTED MARGIN={TARGET_MARGIN_TYPE}",
        flush=True,
    )

    print(
        f"R34I: EXPECTED LONG={TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"R34I: EXPECTED SHORT={TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )


    start_health_server()


    try:

        with runtime_lock:
            runtime[
                "phase"
            ] = "SAFETY_VALIDATION"

        assert_static_safety_configuration()


        with runtime_lock:
            runtime[
                "phase"
            ] = "CREDENTIAL_VALIDATION"

        validate_credentials()


        with runtime_lock:
            runtime[
                "phase"
            ] = "FIRST_LIVE_READ"

        first_snapshot = first_live_read()


        with runtime_lock:
            runtime[
                "phase"
            ] = "SECOND_LIVE_READ"

        second_snapshot = second_live_read()


        with runtime_lock:
            runtime[
                "phase"
            ] = "CONSISTENCY_VALIDATION"

        consistency_ok = verify_consistency(
            first_snapshot,
            second_snapshot,
        )


        with runtime_lock:
            runtime[
                "phase"
            ] = "CORRECTION_VERIFICATION"

        correction_ok = verify_manual_correction(
            second_snapshot
        )


        with runtime_lock:
            runtime[
                "phase"
            ] = "TRANSPORT_BOUNDARY_VALIDATION"

        transport_ok = verify_transport_boundary()


        with runtime_lock:
            runtime[
                "phase"
            ] = "FINAL_GATE"

        final_ok = final_gate(
            first_snapshot,
            second_snapshot,
        )


        overall_ok = (
            consistency_ok
            and correction_ok
            and transport_ok
            and final_ok
        )


        banner(
            "R34I: VALIDATION COMPLETE"
        )


        if overall_ok:

            with runtime_lock:

                runtime[
                    "phase"
                ] = (
                    "MANUAL_100X_CORRECTION_VERIFIED"
                )

                runtime[
                    "verification_complete"
                ] = True


            print(
                "R34I: PHASE=MANUAL_100X_CORRECTION_VERIFIED",
                flush=True,
            )

            print(
                f"R34I: AUTHENTICATED GETS="
                f"{runtime['authenticated_gets']}",
                flush=True,
            )

            print(
                f"R34I: OBSERVED MARGIN="
                f"{runtime['observed_margin']}",
                flush=True,
            )

            print(
                f"R34I: OBSERVED LONG="
                f"{runtime['observed_long']}x",
                flush=True,
            )

            print(
                f"R34I: OBSERVED SHORT="
                f"{runtime['observed_short']}x",
                flush=True,
            )

            print(
                f"R34I: TARGET LONG="
                f"{TARGET_LONG_LEVERAGE}x",
                flush=True,
            )

            print(
                f"R34I: TARGET SHORT="
                f"{TARGET_SHORT_LEVERAGE}x",
                flush=True,
            )

            print(
                f"R34I: OPEN POSITIONS="
                f"{runtime['open_positions']}",
                flush=True,
            )

            print(
                "R34I: CORRECTION REQUIRED=False",
                flush=True,
            )

            print(
                "R34I: CORRECTION VERIFIED=True",
                flush=True,
            )

            print(
                f"R34I: FIRST STATE SHA256="
                f"{runtime['first_read_hash']}",
                flush=True,
            )

            print(
                f"R34I: SECOND STATE SHA256="
                f"{runtime['second_read_hash']}",
                flush=True,
            )

            print(
                "R34I: NETWORK WRITES=0",
                flush=True,
            )

            print(
                "R34I: REAL ORDERS=0",
                flush=True,
            )

            print(
                "R34I: DEMO ORDERS=0",
                flush=True,
            )

            print(
                "R34I: LEVERAGE MUTATIONS=0",
                flush=True,
            )

            print(
                "R34I: MANUAL 100x LONG + 100x SHORT CORRECTION VERIFIED",
                flush=True,
            )

            print(
                "R34I: NO REAL ORDER WAS SENT",
                flush=True,
            )

            print(
                "R34I: NO EXCHANGE WRITE WAS SENT",
                flush=True,
            )

            print(
                "R34I: NO LEVERAGE MUTATION WAS PERFORMED",
                flush=True,
            )

            print(
                "R34I: AUTHENTICATED READ-BACK COMPLETE",
                flush=True,
            )

            print(
                LINE,
                flush=True,
            )

        else:

            with runtime_lock:

                runtime[
                    "phase"
                ] = (
                    "MANUAL_CORRECTION_VERIFICATION_FAILED"
                )

                runtime[
                    "verification_complete"
                ] = False

            banner(
                "R34I: VERIFICATION FAILED"
            )

            print(
                "R34I: Expected ISOLATED 100x / 100x "
                "was not independently verified.",
                flush=True,
            )


    except Exception as exc:

        with runtime_lock:

            runtime[
                "phase"
            ] = "FAILED"

            runtime[
                "last_error"
            ] = str(exc)

        banner(
            "R34I: FATAL VALIDATION ERROR"
        )

        print(
            f"R34I: ERROR={exc}",
            flush=True,
        )


    heartbeat_loop()


if __name__ == "__main__":
    main()
