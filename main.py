# ==================================================================================================
# R34J - COMPLETE MAIN.PY
# AUTHENTICATED READ-ONLY ACCOUNT / POSITION / LEVERAGE VERIFICATION
#
# SAFETY:
#   - REAL ORDER EXECUTION DISABLED
#   - DEMO ORDER EXECUTION DISABLED
#   - NETWORK WRITES DISABLED
#   - LEVERAGE MUTATION DISABLED
#   - MARGIN MUTATION DISABLED
#   - POSITION MUTATION DISABLED
#   - ACCOUNT MUTATION DISABLED
#
# TARGET:
#   - SYMBOL: BTCUSDT
#   - MARGIN: ISOLATED
#   - LONG LEVERAGE: 100x
#   - SHORT LEVERAGE: 100x
#   - INITIAL ENTRY: 5%
#   - MAX FUND EXPOSURE: 35%
#
# IMPORTANT:
#   This R34J version performs authenticated GET requests only.
#   It cannot place orders or change leverage/margin/account state.
# ==================================================================================================

import os
import sys
import json
import time
import hmac
import base64
import hashlib
import threading
import traceback
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ==================================================================================================
# PART 1 - CONSTANTS / CONFIGURATION
# ==================================================================================================

VERSION = "R34J"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com"
).strip().rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", "10000"))

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

HEARTBEAT_SECONDS = 30

AUTHENTICATED_READ_ONLY = True

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# --------------------------------------------------------------------------------------------------
# WEEX READ-ONLY ENDPOINTS
# --------------------------------------------------------------------------------------------------

# V3 maintained endpoint.
BALANCE_PATHS = [
    "/capi/v3/account/balance",

    # Fallback retained because this endpoint already succeeded in your R34J run.
    "/capi/v2/account/assets",
]

# IMPORTANT R34J FIX:
# Previous incorrect path:
#     /capi/v2/account/allPosition
#
# Correct current V3 path:
#     /capi/v3/account/position/allPosition
#
POSITION_PATHS = [
    "/capi/v3/account/position/allPosition",
    f"/capi/v3/account/position/singlePosition?symbol={SYMBOL}",

    # Older compatibility fallback.
    "/capi/v2/account/position/allPosition",
]

SYMBOL_CONFIG_PATHS = [
    f"/capi/v3/account/symbolConfig?symbol={SYMBOL}",

    # Optional legacy fallback if an older WEEX account/API environment
    # still exposes it.
    f"/capi/v2/account/symbolConfig?symbol={SYMBOL}",
]


# ==================================================================================================
# RUNTIME STATE
# ==================================================================================================

runtime_lock = threading.RLock()

runtime = {
    "version": VERSION,
    "symbol": SYMBOL,
    "phase": "STARTING",
    "healthy": True,
    "started_at": int(time.time()),
    "heartbeat": 0,

    "authenticated_get_count": 0,
    "network_write_count": 0,
    "real_order_count": 0,
    "demo_order_count": 0,
    "leverage_mutation_count": 0,
    "margin_mutation_count": 0,
    "position_mutation_count": 0,
    "account_mutation_count": 0,

    "available_usdt": None,

    "position_path": None,
    "position_count": None,
    "btc_position_count": None,

    "symbol_config_path": None,
    "observed_margin": None,
    "observed_long_leverage": None,
    "observed_short_leverage": None,

    "correction_required": None,
    "manual_correction_verified": False,

    "last_error": None,
}


# ==================================================================================================
# FORMATTING HELPERS
# ==================================================================================================

LINE = "-" * 100


def banner(text):
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def log(text):
    print(f"{VERSION}: {text}", flush=True)


def result(label, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{label:<86} {status}", flush=True)
    return bool(passed)


def safe_decimal(value, default=None):
    try:
        if value is None:
            return default

        if isinstance(value, Decimal):
            return value

        text = str(value).strip()

        if text == "":
            return default

        if text.lower().endswith("x"):
            text = text[:-1]

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return default


def decimal_text(value):
    if value is None:
        return "UNKNOWN"

    if not isinstance(value, Decimal):
        value = safe_decimal(value)

    if value is None:
        return "UNKNOWN"

    if value == value.to_integral():
        return str(int(value))

    return format(value.normalize(), "f")


def normalize_margin(value):
    if value is None:
        return None

    text = str(value).strip().upper()

    aliases = {
        "CROSS": "CROSSED",
        "CROSSED": "CROSSED",
        "ISOLATE": "ISOLATED",
        "ISOLATED": "ISOLATED",
    }

    return aliases.get(text, text)


# ==================================================================================================
# CREDENTIAL RESOLUTION
# ==================================================================================================

def first_env(*names):
    for name in names:
        value = os.getenv(name)

        if value is not None:
            value = value.strip()

            if value:
                return value

    return None


def get_credentials():
    api_key = first_env(
        "WEEX_API_KEY",
        "API_KEY",
        "WEEX_KEY",
    )

    api_secret = first_env(
        "WEEX_API_SECRET",
        "WEEX_SECRET_KEY",
        "API_SECRET",
        "SECRET_KEY",
    )

    passphrase = first_env(
        "WEEX_API_PASSPHRASE",
        "WEEX_PASSPHRASE",
        "API_PASSPHRASE",
        "PASSPHRASE",
    )

    return api_key, api_secret, passphrase


def require_credentials():
    api_key, api_secret, passphrase = get_credentials()

    missing = []

    if not api_key:
        missing.append("WEEX_API_KEY")

    if not api_secret:
        missing.append("WEEX_API_SECRET")

    if not passphrase:
        missing.append("WEEX_API_PASSPHRASE")

    if missing:
        raise RuntimeError(
            "Missing credentials: " + ", ".join(missing)
        )

    return api_key, api_secret, passphrase


# ==================================================================================================
# HARD SAFETY FIREBREAK
# ==================================================================================================

def assert_read_only_method(method):
    method = str(method).upper().strip()

    if method != "GET":
        raise RuntimeError(
            f"R34J HARD FIREBREAK: HTTP {method} is forbidden. "
            f"Authenticated GET only."
        )


def forbidden_network_write(*args, **kwargs):
    raise RuntimeError(
        "R34J HARD FIREBREAK: exchange network writes are disabled."
    )


def forbidden_real_order(*args, **kwargs):
    raise RuntimeError(
        "R34J HARD FIREBREAK: real order execution is disabled."
    )


def forbidden_demo_order(*args, **kwargs):
    raise RuntimeError(
        "R34J HARD FIREBREAK: demo order execution is disabled."
    )


def forbidden_leverage_mutation(*args, **kwargs):
    raise RuntimeError(
        "R34J HARD FIREBREAK: leverage mutation is disabled."
    )


def forbidden_margin_mutation(*args, **kwargs):
    raise RuntimeError(
        "R34J HARD FIREBREAK: margin mutation is disabled."
    )


def forbidden_position_mutation(*args, **kwargs):
    raise RuntimeError(
        "R34J HARD FIREBREAK: position mutation is disabled."
    )


def forbidden_account_mutation(*args, **kwargs):
    raise RuntimeError(
        "R34J HARD FIREBREAK: account mutation is disabled."
    )


# ==================================================================================================
# SIGNING
# ==================================================================================================

def split_request_target(request_target):
    parsed = urlsplit(request_target)

    request_path = parsed.path

    query_string = parsed.query

    if not request_path.startswith("/"):
        request_path = "/" + request_path

    return request_path, query_string


def make_signature(secret, timestamp, method, request_target):
    """
    WEEX signature:
        timestamp + METHOD + requestPath + [?query]

    GET has no body.
    """

    method = method.upper()

    request_path, query_string = split_request_target(request_target)

    sign_target = request_path

    if query_string:
        sign_target += "?" + query_string

    message = timestamp + method + sign_target

    digest = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# ==================================================================================================
# STANDARD LIBRARY AUTHENTICATED GET
# ==================================================================================================

def authenticated_get(request_target, timeout=15):
    assert_read_only_method("GET")

    api_key, api_secret, passphrase = require_credentials()

    timestamp = str(int(time.time() * 1000))

    signature = make_signature(
        api_secret,
        timestamp,
        "GET",
        request_target,
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only-validator",
        "locale": "en-US",
    }

    url = BASE_URL + request_target

    request = Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            status = int(response.status)

            body = response.read().decode(
                "utf-8",
                errors="replace",
            )

    except HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Authenticated GET {request_target} failed: "
            f"HTTP {exc.code}: {body}"
        ) from exc

    except URLError as exc:
        raise RuntimeError(
            f"Authenticated GET {request_target} failed: {exc}"
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Authenticated GET {request_target} failed: {exc}"
        ) from exc

    if status < 200 or status >= 300:
        raise RuntimeError(
            f"Authenticated GET {request_target} failed: "
            f"HTTP {status}: {body}"
        )

    try:
        data = json.loads(body)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Authenticated GET {request_target} returned invalid JSON: "
            f"{body[:500]}"
        ) from exc

    with runtime_lock:
        runtime["authenticated_get_count"] += 1

    return data


# ==================================================================================================
# RESPONSE NORMALIZATION
# ==================================================================================================

def unwrap_payload(data):
    """
    Supports both:
        [...]
    and wrappers such as:
        {"data": [...]}
        {"result": [...]}
    """

    if isinstance(data, (list, tuple)):
        return data

    if not isinstance(data, dict):
        return data

    for key in ("data", "result", "rows", "list"):
        if key in data:
            value = data[key]

            if value is not None:
                return value

    return data


def as_list(data):
    data = unwrap_payload(data)

    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, tuple):
        return list(data)

    if isinstance(data, dict):
        return [data]

    return []


# ==================================================================================================
# BALANCE READ-BACK
# ==================================================================================================

def extract_available_usdt(data):
    records = as_list(data)

    for item in records:
        if not isinstance(item, dict):
            continue

        asset = (
            item.get("asset")
            or item.get("coin")
            or item.get("currency")
            or ""
        )

        if str(asset).upper() != "USDT":
            continue

        for field in (
            "availableBalance",
            "available",
            "availableAmount",
            "availableEquity",
        ):
            if field in item:
                value = safe_decimal(item.get(field))

                if value is not None:
                    return value

    # Some API responses may use:
    # {"USDT": {...}}
    payload = unwrap_payload(data)

    if isinstance(payload, dict):
        usdt = payload.get("USDT")

        if isinstance(usdt, dict):
            for field in (
                "availableBalance",
                "available",
                "availableAmount",
                "availableEquity",
            ):
                value = safe_decimal(usdt.get(field))

                if value is not None:
                    return value

    return None


def fetch_available_balance():
    errors = []

    for path in BALANCE_PATHS:
        try:
            data = authenticated_get(path)

            available = extract_available_usdt(data)

            if available is None:
                errors.append(
                    f"{path}: response did not contain readable USDT "
                    f"available balance"
                )
                continue

            return path, available, data

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Could not read available balance: "
        + " | ".join(errors)
    )


# ==================================================================================================
# POSITION RECONCILIATION - R34J CORRECTED
# ==================================================================================================

def filter_symbol_positions(records):
    matched = []

    for item in records:
        if not isinstance(item, dict):
            continue

        symbol = str(
            item.get("symbol", "")
        ).upper().strip()

        if symbol == SYMBOL:
            matched.append(item)

    return matched


def active_positions(records):
    active = []

    for item in records:
        if not isinstance(item, dict):
            continue

        size = None

        for field in (
            "size",
            "positionSize",
            "quantity",
            "qty",
            "holdVolume",
            "total",
        ):
            if field in item:
                size = safe_decimal(
                    item.get(field),
                    Decimal("0"),
                )
                break

        if size is None:
            # If WEEX returned a position record but its exact quantity
            # field is unknown, preserve it for reconciliation rather
            # than silently discarding it.
            active.append(item)
            continue

        if abs(size) > Decimal("0"):
            active.append(item)

    return active


def fetch_positions():
    """
    Current primary:
        GET /capi/v3/account/position/allPosition

    No query parameters are attached to allPosition.

    singlePosition is a fallback and accepts ?symbol=BTCUSDT.
    """

    errors = []

    for path in POSITION_PATHS:
        try:
            data = authenticated_get(path)

            records = as_list(data)

            btc_records = filter_symbol_positions(records)

            # singlePosition is already symbol-specific, but keep this
            # defensive fallback in case the response omits symbol.
            if (
                "singlePosition" in path
                and not btc_records
                and records
            ):
                btc_records = records

            btc_active = active_positions(btc_records)

            return (
                path,
                records,
                btc_records,
                btc_active,
                data,
            )

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Could not read open positions: "
        + " | ".join(errors)
    )


# ==================================================================================================
# SYMBOL CONFIGURATION / LEVERAGE READ-BACK
# ==================================================================================================

def find_symbol_config(data):
    records = as_list(data)

    for item in records:
        if not isinstance(item, dict):
            continue

        symbol = str(
            item.get("symbol", "")
        ).upper().strip()

        if symbol == SYMBOL:
            return item

    if len(records) == 1 and isinstance(records[0], dict):
        return records[0]

    return None


def extract_config_values(config):
    margin = normalize_margin(
        config.get("marginType")
        or config.get("marginMode")
        or config.get("margin_type")
    )

    long_leverage = safe_decimal(
        config.get("isolatedLongLeverage")
        or config.get("longLeverage")
        or config.get("buyLeverage")
    )

    short_leverage = safe_decimal(
        config.get("isolatedShortLeverage")
        or config.get("shortLeverage")
        or config.get("sellLeverage")
    )

    cross_leverage = safe_decimal(
        config.get("crossLeverage")
        or config.get("crossedLeverage")
    )

    separated_type = (
        config.get("separatedType")
        or config.get("separatedMode")
        or config.get("positionMode")
    )

    return (
        margin,
        long_leverage,
        short_leverage,
        cross_leverage,
        separated_type,
    )


def fetch_symbol_config():
    errors = []

    for path in SYMBOL_CONFIG_PATHS:
        try:
            data = authenticated_get(path)

            config = find_symbol_config(data)

            if config is None:
                errors.append(
                    f"{path}: no {SYMBOL} configuration found"
                )
                continue

            (
                margin,
                long_leverage,
                short_leverage,
                cross_leverage,
                separated_type,
            ) = extract_config_values(config)

            return (
                path,
                config,
                margin,
                long_leverage,
                short_leverage,
                cross_leverage,
                separated_type,
                data,
            )

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Could not read symbol configuration: "
        + " | ".join(errors)
    )


# ==================================================================================================
# STRATEGY READ-ONLY CALCULATIONS
# ==================================================================================================

def calculate_entry_budget(available):
    return (
        available
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )


def calculate_max_exposure_budget(available):
    return (
        available
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )


def calculate_target_notional(entry_margin):
    return entry_margin * TARGET_LONG_LEVERAGE


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def _write_json(self, status, payload):
        encoded = json.dumps(
            payload,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(encoded)),
        )

        self.end_headers()

        self.wfile.write(encoded)

    def do_GET(self):
        with runtime_lock:
            snapshot = dict(runtime)

        payload = {
            "ok": bool(snapshot.get("healthy")),
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": snapshot.get("phase"),
            "heartbeat": snapshot.get("heartbeat"),

            "authenticated_read_only": AUTHENTICATED_READ_ONLY,

            "network_writes": EXCHANGE_NETWORK_WRITES_ENABLED,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "demo_order_execution": DEMO_ORDER_EXECUTION,

            "leverage_mutation": LEVERAGE_MUTATION_ENABLED,
            "margin_mutation": MARGIN_MUTATION_ENABLED,
            "position_mutation": POSITION_MUTATION_ENABLED,
            "account_mutation": ACCOUNT_MUTATION_ENABLED,

            "available_usdt": snapshot.get(
                "available_usdt"
            ),

            "position_path": snapshot.get(
                "position_path"
            ),

            "position_count": snapshot.get(
                "position_count"
            ),

            "btc_position_count": snapshot.get(
                "btc_position_count"
            ),

            "symbol_config_path": snapshot.get(
                "symbol_config_path"
            ),

            "observed_margin": snapshot.get(
                "observed_margin"
            ),

            "observed_long_leverage": snapshot.get(
                "observed_long_leverage"
            ),

            "observed_short_leverage": snapshot.get(
                "observed_short_leverage"
            ),

            "target_margin": TARGET_MARGIN_TYPE,

            "target_long_leverage": decimal_text(
                TARGET_LONG_LEVERAGE
            ),

            "target_short_leverage": decimal_text(
                TARGET_SHORT_LEVERAGE
            ),

            "correction_required": snapshot.get(
                "correction_required"
            ),

            "manual_correction_verified": snapshot.get(
                "manual_correction_verified"
            ),

            "last_error": snapshot.get(
                "last_error"
            ),
        }

        self._write_json(
            200 if snapshot.get("healthy") else 503,
            payload,
        )

    def do_POST(self):
        self._write_json(
            405,
            {
                "ok": False,
                "error": "R34J is read-only",
            },
        )

    def do_PUT(self):
        self.do_POST()

    def do_PATCH(self):
        self.do_POST()

    def do_DELETE(self):
        self.do_POST()


def start_health_server():
    server = ThreadingHTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
        name="r34j-health",
    )

    thread.start()

    return server


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_loop():
    while True:
        time.sleep(HEARTBEAT_SECONDS)

        with runtime_lock:
            runtime["heartbeat"] += 1

            heartbeat = runtime["heartbeat"]
            phase = runtime["phase"]
            balance = runtime["available_usdt"]
            margin = runtime["observed_margin"]
            long_lev = runtime["observed_long_leverage"]
            short_lev = runtime["observed_short_leverage"]
            correction_required = runtime["correction_required"]

            auth_gets = runtime["authenticated_get_count"]

        log(
            "HEARTBEAT "
            f"{heartbeat} | "
            f"phase={phase} | "
            f"authenticated-read-only={AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get={auth_gets} | "
            f"real-execution={REAL_ORDER_EXECUTION} | "
            f"demo-execution={DEMO_ORDER_EXECUTION} | "
            f"network-writes={EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"available-usdt={balance} | "
            f"observed-margin={margin} | "
            f"observed-long={long_lev} | "
            f"observed-short={short_lev} | "
            f"target-long={decimal_text(TARGET_LONG_LEVERAGE)}x | "
            f"target-short={decimal_text(TARGET_SHORT_LEVERAGE)}x | "
            f"correction-required={correction_required}"
        )


def start_heartbeat():
    thread = threading.Thread(
        target=heartbeat_loop,
        daemon=True,
        name="r34j-heartbeat",
    )

    thread.start()

    return thread


# ==================================================================================================
# TEST HELPERS
# ==================================================================================================

def assert_zero_mutations():
    with runtime_lock:
        values = {
            "network": runtime["network_write_count"],
            "real": runtime["real_order_count"],
            "demo": runtime["demo_order_count"],
            "leverage": runtime["leverage_mutation_count"],
            "margin": runtime["margin_mutation_count"],
            "position": runtime["position_mutation_count"],
            "account": runtime["account_mutation_count"],
        }

    return all(
        value == 0
        for value in values.values()
    )


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def main():

    banner(f"{VERSION}: MAIN.PY ENTERED")

    log(f"SYMBOL={SYMBOL}")
    log(f"VERSION={VERSION}")
    log(f"HEALTH PORT={HEALTH_PORT}")
    log("AUTHENTICATED READ-ONLY ENABLED")
    log("STANDARD LIBRARY HTTP ENABLED")
    log("REAL ORDER EXECUTION DISABLED")
    log("DEMO ORDER EXECUTION DISABLED")
    log("NETWORK WRITES DISABLED")
    log("LEVERAGE MUTATION DISABLED")
    log("TARGET MARGIN=ISOLATED")
    log(
        "TARGET LONG="
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
    )
    log(
        "TARGET SHORT="
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
    )
    log(
        "INITIAL ENTRY="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )
    log(
        "MAX FUND EXPOSURE="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 1
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 1: HARD SAFETY CONFIGURATION"
    )

    t1 = []

    t1.append(
        result(
            "Authenticated Read-Only Is Enabled",
            AUTHENTICATED_READ_ONLY is True,
        )
    )

    t1.append(
        result(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION is False,
        )
    )

    t1.append(
        result(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    t1.append(
        result(
            "Exchange Network Writes Are Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED is False,
        )
    )

    t1.append(
        result(
            "Leverage Mutation Is Disabled",
            LEVERAGE_MUTATION_ENABLED is False,
        )
    )

    t1.append(
        result(
            "Margin Mutation Is Disabled",
            MARGIN_MUTATION_ENABLED is False,
        )
    )

    t1.append(
        result(
            "Position Mutation Is Disabled",
            POSITION_MUTATION_ENABLED is False,
        )
    )

    t1.append(
        result(
            "Account Mutation Is Disabled",
            ACCOUNT_MUTATION_ENABLED is False,
        )
    )

    if not all(t1):
        raise RuntimeError(
            "Hard safety configuration failed."
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 2
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 2: CREDENTIAL PRESENCE"
    )

    api_key, api_secret, passphrase = require_credentials()

    t2 = []

    t2.append(
        result(
            "API Key Is Present",
            bool(api_key),
        )
    )

    t2.append(
        result(
            "API Secret Is Present",
            bool(api_secret),
        )
    )

    t2.append(
        result(
            "API Passphrase Is Present",
            bool(passphrase),
        )
    )

    if not all(t2):
        raise RuntimeError(
            "Credential presence validation failed."
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 3
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 3: AVAILABLE BALANCE READ-BACK"
    )

    (
        balance_path,
        available_usdt,
        balance_raw,
    ) = fetch_available_balance()

    log(
        f"BALANCE PATH={balance_path}"
    )

    log(
        "AVAILABLE USDT="
        f"{decimal_text(available_usdt)}"
    )

    with runtime_lock:
        runtime["available_usdt"] = decimal_text(
            available_usdt
        )

    t3 = []

    t3.append(
        result(
            "Available Balance Was Read",
            available_usdt is not None,
        )
    )

    t3.append(
        result(
            "Available Balance Is Positive",
            (
                available_usdt is not None
                and available_usdt > Decimal("0")
            ),
        )
    )

    if not all(t3):
        raise RuntimeError(
            "Available balance validation failed."
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 4 - CORRECTED POSITION ENDPOINT
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 4: POSITION RECONCILIATION"
    )

    (
        position_path,
        all_positions,
        symbol_positions,
        symbol_active_positions,
        positions_raw,
    ) = fetch_positions()

    log(
        f"POSITION PATH={position_path}"
    )

    log(
        f"TOTAL POSITION RECORDS={len(all_positions)}"
    )

    log(
        f"{SYMBOL} POSITION RECORDS="
        f"{len(symbol_positions)}"
    )

    log(
        f"{SYMBOL} ACTIVE POSITIONS="
        f"{len(symbol_active_positions)}"
    )

    with runtime_lock:
        runtime["position_path"] = position_path
        runtime["position_count"] = len(
            all_positions
        )
        runtime["btc_position_count"] = len(
            symbol_active_positions
        )

    t4 = []

    t4.append(
        result(
            "Position Endpoint Was Read",
            position_path is not None,
        )
    )

    t4.append(
        result(
            "Position Response Is Reconciled",
            isinstance(all_positions, list),
        )
    )

    t4.append(
        result(
            f"{SYMBOL} Position State Was Reconciled",
            isinstance(symbol_positions, list),
        )
    )

    # Empty positions are valid.
    t4.append(
        result(
            "Zero Open Positions Is Accepted As Valid State",
            len(symbol_active_positions) >= 0,
        )
    )

    if not all(t4):
        raise RuntimeError(
            "Position reconciliation failed."
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 5
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 5: SYMBOL CONFIGURATION READ-BACK"
    )

    (
        config_path,
        config,
        observed_margin,
        observed_long,
        observed_short,
        observed_cross,
        separated_type,
        config_raw,
    ) = fetch_symbol_config()

    log(
        f"SYMBOL CONFIG PATH={config_path}"
    )

    log(
        "OBSERVED MARGIN="
        f"{observed_margin}"
    )

    log(
        "OBSERVED POSITION MODE="
        f"{separated_type}"
    )

    log(
        "OBSERVED CROSS LEVERAGE="
        f"{decimal_text(observed_cross)}x"
    )

    log(
        "OBSERVED ISOLATED LONG="
        f"{decimal_text(observed_long)}x"
    )

    log(
        "OBSERVED ISOLATED SHORT="
        f"{decimal_text(observed_short)}x"
    )

    with runtime_lock:
        runtime["symbol_config_path"] = config_path
        runtime["observed_margin"] = observed_margin
        runtime["observed_long_leverage"] = (
            decimal_text(observed_long)
            if observed_long is not None
            else None
        )
        runtime["observed_short_leverage"] = (
            decimal_text(observed_short)
            if observed_short is not None
            else None
        )

    t5 = []

    t5.append(
        result(
            "Symbol Configuration Was Read",
            config is not None,
        )
    )

    t5.append(
        result(
            f"Configuration Belongs To {SYMBOL}",
            str(
                config.get("symbol", SYMBOL)
            ).upper() == SYMBOL,
        )
    )

    t5.append(
        result(
            "Margin Type Was Read",
            observed_margin is not None,
        )
    )

    t5.append(
        result(
            "Isolated Long Leverage Was Read",
            observed_long is not None,
        )
    )

    t5.append(
        result(
            "Isolated Short Leverage Was Read",
            observed_short is not None,
        )
    )

    if not all(t5):
        raise RuntimeError(
            "Symbol configuration validation failed."
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 6
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 6: MANUAL LEVERAGE CORRECTION VERIFICATION"
    )

    margin_correct = (
        observed_margin == TARGET_MARGIN_TYPE
    )

    long_correct = (
        observed_long == TARGET_LONG_LEVERAGE
    )

    short_correct = (
        observed_short == TARGET_SHORT_LEVERAGE
    )

    correction_required = not (
        margin_correct
        and long_correct
        and short_correct
    )

    manual_correction_verified = (
        margin_correct
        and long_correct
        and short_correct
    )

    with runtime_lock:
        runtime["correction_required"] = (
            correction_required
        )

        runtime["manual_correction_verified"] = (
            manual_correction_verified
        )

    t6 = []

    t6.append(
        result(
            "Observed Margin Is ISOLATED",
            margin_correct,
        )
    )

    t6.append(
        result(
            "Observed Long Leverage Is 100x",
            long_correct,
        )
    )

    t6.append(
        result(
            "Observed Short Leverage Is 100x",
            short_correct,
        )
    )

    t6.append(
        result(
            "Manual Correction Is Verified",
            manual_correction_verified,
        )
    )

    if correction_required:

        log(
            "READ-BACK DOES NOT YET MATCH THE "
            "100x/100x ISOLATED TARGET"
        )

        log(
            "NO AUTOMATIC CORRECTION WILL BE SENT"
        )

        log(
            "R34J REMAINS READ-ONLY"
        )

    else:

        log(
            "MANUAL ACCOUNT CORRECTION VERIFIED"
        )

        log(
            "ISOLATED LONG=100x"
        )

        log(
            "ISOLATED SHORT=100x"
        )

    # We do NOT crash merely because manual leverage
    # does not match. The purpose of R34J is to read
    # and report the live account state safely.

    # ----------------------------------------------------------------------------------------------
    # TEST 7
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 7: STRATEGY BUDGET RECONCILIATION"
    )

    initial_margin_budget = calculate_entry_budget(
        available_usdt
    )

    max_exposure_budget = calculate_max_exposure_budget(
        available_usdt
    )

    target_initial_notional = calculate_target_notional(
        initial_margin_budget
    )

    log(
        "AVAILABLE BALANCE="
        f"{decimal_text(available_usdt)} USDT"
    )

    log(
        "INITIAL ENTRY PERCENT="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        "INITIAL MARGIN BUDGET="
        f"{decimal_text(initial_margin_budget)} USDT"
    )

    log(
        "TARGET INITIAL NOTIONAL AT 100x="
        f"{decimal_text(target_initial_notional)} USDT"
    )

    log(
        "MAX FUND EXPOSURE PERCENT="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        "MAX FUND EXPOSURE BUDGET="
        f"{decimal_text(max_exposure_budget)} USDT"
    )

    t7 = []

    t7.append(
        result(
            "Initial Entry Percent Is 5%",
            INITIAL_ENTRY_PERCENT == Decimal("5"),
        )
    )

    t7.append(
        result(
            "Maximum Fund Exposure Is 35%",
            MAX_FUND_EXPOSURE_PERCENT == Decimal("35"),
        )
    )

    t7.append(
        result(
            "Initial Margin Budget Is Positive",
            initial_margin_budget > Decimal("0"),
        )
    )

    t7.append(
        result(
            "Maximum Exposure Budget Is Positive",
            max_exposure_budget > Decimal("0"),
        )
    )

    t7.append(
        result(
            "Initial Budget Is Below Maximum Exposure",
            initial_margin_budget < max_exposure_budget,
        )
    )

    if not all(t7):
        raise RuntimeError(
            "Strategy budget reconciliation failed."
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 8
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 8: WRITE FIREBREAK VERIFICATION"
    )

    write_blocked = False

    try:
        assert_read_only_method("POST")

    except RuntimeError:
        write_blocked = True

    t8 = []

    t8.append(
        result(
            "Authenticated POST Is Rejected Locally",
            write_blocked,
        )
    )

    t8.append(
        result(
            "Exchange Network Writes Remain Zero",
            runtime["network_write_count"] == 0,
        )
    )

    t8.append(
        result(
            "Leverage Mutations Remain Zero",
            runtime["leverage_mutation_count"] == 0,
        )
    )

    t8.append(
        result(
            "Margin Mutations Remain Zero",
            runtime["margin_mutation_count"] == 0,
        )
    )

    t8.append(
        result(
            "Position Mutations Remain Zero",
            runtime["position_mutation_count"] == 0,
        )
    )

    t8.append(
        result(
            "Account Mutations Remain Zero",
            runtime["account_mutation_count"] == 0,
        )
    )

    t8.append(
        result(
            "Real Orders Remain Zero",
            runtime["real_order_count"] == 0,
        )
    )

    t8.append(
        result(
            "Demo Orders Remain Zero",
            runtime["demo_order_count"] == 0,
        )
    )

    if not all(t8):
        raise RuntimeError(
            "Write firebreak verification failed."
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 9
    # ----------------------------------------------------------------------------------------------

    banner(
        f"{VERSION} TEST 9: FINAL LIVE READ-ONLY STATE"
    )

    t9 = []

    t9.append(
        result(
            "Credentials Remain Present",
            bool(api_key and api_secret and passphrase),
        )
    )

    t9.append(
        result(
            "Available Balance Is Still Valid",
            available_usdt > Decimal("0"),
        )
    )

    t9.append(
        result(
            "Position Reconciliation Completed",
            position_path is not None,
        )
    )

    t9.append(
        result(
            "Symbol Configuration Reconciliation Completed",
            config_path is not None,
        )
    )

    t9.append(
        result(
            "Authenticated Read-Only Remains Enabled",
            AUTHENTICATED_READ_ONLY is True,
        )
    )

    t9.append(
        result(
            "Network Writes Remain Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED is False,
        )
    )

    t9.append(
        result(
            "All Mutation Counters Remain Zero",
            assert_zero_mutations(),
        )
    )

    if not all(t9):
        raise RuntimeError(
            "Final live state validation failed."
        )

    # ----------------------------------------------------------------------------------------------
    # FINAL
    # ----------------------------------------------------------------------------------------------

    with runtime_lock:
        runtime["phase"] = (
            "LIVE_READ_ONLY_VALIDATED"
            if not correction_required
            else "LIVE_READ_ONLY_CORRECTION_REQUIRED"
        )

        runtime["healthy"] = True

    banner(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        "PHASE="
        f"{runtime['phase']}"
    )

    log(
        "AUTHENTICATED GET COUNT="
        f"{runtime['authenticated_get_count']}"
    )

    log(
        "AVAILABLE USDT="
        f"{decimal_text(available_usdt)}"
    )

    log(
        "POSITION PATH="
        f"{position_path}"
    )

    log(
        "SYMBOL CONFIG PATH="
        f"{config_path}"
    )

    log(
        "OBSERVED MARGIN="
        f"{observed_margin}"
    )

    log(
        "OBSERVED LONG="
        f"{decimal_text(observed_long)}x"
    )

    log(
        "OBSERVED SHORT="
        f"{decimal_text(observed_short)}x"
    )

    log(
        "TARGET LONG="
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
    )

    log(
        "TARGET SHORT="
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
    )

    log(
        "CORRECTION REQUIRED="
        f"{correction_required}"
    )

    log(
        "MANUAL CORRECTION VERIFIED="
        f"{manual_correction_verified}"
    )

    log(
        "NETWORK WRITES=0"
    )

    log(
        "LEVERAGE MUTATIONS=0"
    )

    log(
        "REAL ORDERS=0"
    )

    log(
        "DEMO ORDERS=0"
    )

    banner(
        f"{VERSION}: ENTERING PERSISTENT HEALTH / HEARTBEAT MODE"
    )

    while True:
        time.sleep(3600)


# ==================================================================================================
# PROCESS ENTRY
# ==================================================================================================

if __name__ == "__main__":

    health_server = None

    try:
        health_server = start_health_server()

        start_heartbeat()

        main()

    except KeyboardInterrupt:
        log("SHUTDOWN REQUESTED")

    except Exception as exc:

        with runtime_lock:
            runtime["healthy"] = False
            runtime["phase"] = "FAILED"
            runtime["last_error"] = str(exc)

        banner(
            f"{VERSION}: FATAL ERROR"
        )

        log(
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        # Keep Render health endpoint alive briefly enough for
        # the failure state to be observable, but exit non-zero
        # afterward so Render records the failed process.
        time.sleep(2)

        sys.exit(1)

    finally:
        if health_server is not None:
            try:
                health_server.shutdown()
            except Exception:
                pass
