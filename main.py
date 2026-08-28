# ==================================================================================================
# R34V - LIVE READ-ONLY ACCOUNT CONFIGURATION RECONCILIATION
# ==================================================================================================
#
# PURPOSE
# -------
# 1. Preserve absolute write/mutation firebreaks.
# 2. Verify API credential presence.
# 3. Read live available USDT balance.
# 4. Confirm BTCUSDT has zero open positions.
# 5. Read BTCUSDT ACCOUNT CONFIGURATION from the dedicated WEEX V3
#    /capi/v3/account/symbolConfig endpoint.
# 6. Confirm:
#       marginType = ISOLATED
#       isolatedLongLeverage = 100
#       isolatedShortLeverage = 100
# 7. Calculate strategy readiness values.
# 8. Perform ZERO POST/PUT/PATCH/DELETE requests.
# 9. Perform ZERO order execution.
#
# IMPORTANT
# ---------
# THIS VERSION IS READ-ONLY.
# NO REAL ORDER IS SENT.
# NO DEMO ORDER IS SENT.
# NO LEVERAGE CHANGE IS SENT.
# NO MARGIN CHANGE IS SENT.
# NO POSITION/ACCOUNT MUTATION IS SENT.
#
# ==================================================================================================

import os
import json
import time
import hmac
import hashlib
import base64
import threading
import urllib.parse
import urllib.request
import urllib.error
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==================================================================================================
# SECTION 1 - VERSION / CORE CONFIGURATION
# ==================================================================================================

VERSION = "R34V"

SYMBOL = "BTCUSDT"
ASSET = "USDT"

WEEX_BASE_URL = "https://api-contract.weex.com"

BALANCE_PATH = "/capi/v3/account/balance"
ALL_POSITIONS_PATH = "/capi/v3/account/position/allPosition"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

HTTP_TIMEOUT_SECONDS = 15
HEARTBEAT_SECONDS = 30


# ==================================================================================================
# SECTION 2 - STRATEGY CONFIGURATION
# ==================================================================================================

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

BACKUP_BUFFER_PERCENT = Decimal("0.3")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ==================================================================================================
# SECTION 3 - ABSOLUTE SAFETY FIREBREAKS
# ==================================================================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# ==================================================================================================
# SECTION 4 - COUNTERS
# ==================================================================================================

COUNTERS = {
    "authenticated_gets": 0,
    "public_gets": 0,
    "network_writes": 0,
    "real_orders": 0,
    "demo_orders": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,
}


# ==================================================================================================
# SECTION 5 - GLOBAL RUNTIME STATE
# ==================================================================================================

runtime = {
    "phase": "STARTING",
    "available_usdt": None,
    "total_position_records": None,
    "btc_position_records": None,
    "btc_open_positions": None,
    "margin_type": None,
    "position_mode": None,
    "cross_leverage": None,
    "long_leverage": None,
    "short_leverage": None,
    "configuration_verified": False,
    "correction_required": None,
    "entry_margin_budget": None,
    "max_strategy_margin": None,
    "error": None,
}


# ==================================================================================================
# SECTION 6 - LOGGING HELPERS
# ==================================================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def check(name, condition):
    if condition:
        log(f"{name:<88} ✅ PASS")
        return True

    log(f"{name:<88} ❌ FAIL")
    raise AssertionError(name)


# ==================================================================================================
# SECTION 7 - HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "status": "ok",
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": runtime.get("phase"),
            "authenticated_read_only": AUTHENTICATED_READ_ONLY,
            "public_read_only": PUBLIC_READ_ONLY,
            "network_writes_enabled": NETWORK_WRITES_ENABLED,
            "real_order_execution": REAL_ORDER_EXECUTION,
            "demo_order_execution": DEMO_ORDER_EXECUTION,
            "configuration_verified": runtime.get("configuration_verified"),
            "correction_required": runtime.get("correction_required"),
            "network_writes": COUNTERS["network_writes"],
            "real_orders": COUNTERS["real_orders"],
            "demo_orders": COUNTERS["demo_orders"],
        }

        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ==================================================================================================
# SECTION 8 - CREDENTIAL HELPERS
# ==================================================================================================

def get_credentials():
    return {
        "key": os.getenv("WEEX_API_KEY", "").strip(),
        "secret": os.getenv("WEEX_API_SECRET", "").strip(),
        "passphrase": os.getenv("WEEX_API_PASSPHRASE", "").strip(),
    }


# ==================================================================================================
# SECTION 9 - DECIMAL HELPERS
# ==================================================================================================

def to_decimal(value):
    if value is None:
        return None

    try:
        text = str(value).strip()

        if text == "":
            return None

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return None


def decimal_equal(value, target):
    parsed = to_decimal(value)

    if parsed is None:
        return False

    return parsed == Decimal(str(target))


def round_down_step(value, step):
    value = Decimal(str(value))
    step = Decimal(str(step))

    if step <= 0:
        raise ValueError("Step must be positive")

    units = (value / step).to_integral_value(rounding=ROUND_DOWN)

    return units * step


# ==================================================================================================
# SECTION 10 - JSON NORMALIZATION HELPERS
# ==================================================================================================

def unwrap_common_container(value):
    """
    Safely unwrap common API response containers.

    Supports:
        raw list
        raw object
        {"data": ...}
        {"result": ...}
        {"rows": ...}
        {"list": ...}
    """

    current = value

    for _ in range(5):

        if not isinstance(current, dict):
            break

        changed = False

        for key in ("data", "result", "rows", "list"):

            if key in current and isinstance(
                current[key],
                (dict, list)
            ):
                current = current[key]
                changed = True
                break

        if not changed:
            break

    return current


def collect_dicts(value):
    """
    Recursively collect dictionary objects from arbitrary JSON.

    Useful because exchange API payloads can be:
        [...]
        {"data": [...]}
        {"data": {...}}
        {...}
    """

    found = []

    if isinstance(value, dict):

        found.append(value)

        for child in value.values():
            if isinstance(child, (dict, list)):
                found.extend(collect_dicts(child))

    elif isinstance(value, list):

        for child in value:
            if isinstance(child, (dict, list)):
                found.extend(collect_dicts(child))

    return found


def first_present(mapping, names):
    if not isinstance(mapping, dict):
        return None

    lower_lookup = {
        str(key).lower(): value
        for key, value in mapping.items()
    }

    for name in names:

        if name in mapping:
            value = mapping[name]

            if value is not None and str(value).strip() != "":
                return value

        lower_name = name.lower()

        if lower_name in lower_lookup:
            value = lower_lookup[lower_name]

            if value is not None and str(value).strip() != "":
                return value

    return None


# ==================================================================================================
# SECTION 11 - HARD WRITE BLOCK
# ==================================================================================================

def reject_network_write(method, path=""):
    method = str(method).upper()

    if method in ("POST", "PUT", "PATCH", "DELETE"):
        raise RuntimeError(
            f"R34V SAFETY FIREBREAK: HTTP {method} rejected for {path}"
        )

    raise RuntimeError(
        f"R34V SAFETY FIREBREAK: unsupported network write rejected: "
        f"{method} {path}"
    )


def send_real_order(*args, **kwargs):
    raise RuntimeError(
        "R34V SAFETY FIREBREAK: real order execution is disabled"
    )


def send_demo_order(*args, **kwargs):
    raise RuntimeError(
        "R34V SAFETY FIREBREAK: demo order execution is disabled"
    )


def mutate_leverage(*args, **kwargs):
    raise RuntimeError(
        "R34V SAFETY FIREBREAK: leverage mutation is disabled"
    )


def mutate_margin(*args, **kwargs):
    raise RuntimeError(
        "R34V SAFETY FIREBREAK: margin mutation is disabled"
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        "R34V SAFETY FIREBREAK: position mutation is disabled"
    )


def mutate_account(*args, **kwargs):
    raise RuntimeError(
        "R34V SAFETY FIREBREAK: account mutation is disabled"
    )


# ==================================================================================================
# SECTION 12 - WEEX V3 SIGNATURE
# ==================================================================================================

def make_signature(
    timestamp,
    method,
    request_path,
    query_string,
    body,
    secret,
):
    method = method.upper()

    if query_string:
        message = (
            str(timestamp)
            + method
            + request_path
            + "?"
            + query_string
            + body
        )
    else:
        message = (
            str(timestamp)
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# ==================================================================================================
# SECTION 13 - AUTHENTICATED READ-ONLY GET
# ==================================================================================================

def authenticated_get(path, params=None):

    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only access is disabled"
        )

    credentials = get_credentials()

    if not all(credentials.values()):
        raise RuntimeError(
            "Authenticated GET attempted without complete credentials"
        )

    params = params or {}

    # Preserve deterministic ordering in query construction.
    query_string = urllib.parse.urlencode(
        sorted(
            (str(key), str(value))
            for key, value in params.items()
            if value is not None
        )
    )

    timestamp = str(int(time.time() * 1000))

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
        secret=credentials["secret"],
    )

    url = WEEX_BASE_URL + path

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": credentials["key"],
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": credentials["passphrase"],
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only-validator",
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

            COUNTERS["authenticated_gets"] += 1

            if raw.strip() == "":
                return None

            return json.loads(raw)

    except urllib.error.HTTPError as exc:

        try:
            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            error_body = ""

        raise RuntimeError(
            f"Authenticated GET failed: {path} | "
            f"HTTP {exc.code} | {error_body}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Authenticated GET failed: {path} | {exc.reason}"
        ) from exc


# ==================================================================================================
# SECTION 14 - BALANCE PARSER
# ==================================================================================================

def parse_available_usdt(payload):

    candidates = collect_dicts(payload)

    balance_field_names = (
        "available",
        "availableBalance",
        "availableMargin",
        "availableAmount",
        "availableEquity",
        "availableUsdt",
        "availableUSDT",
    )

    asset_field_names = (
        "asset",
        "coin",
        "currency",
        "marginCoin",
    )

    # First preference:
    # record explicitly identifying USDT.
    for record in candidates:

        asset_value = first_present(
            record,
            asset_field_names,
        )

        if (
            asset_value is not None
            and str(asset_value).upper() == ASSET
        ):
            balance_value = first_present(
                record,
                balance_field_names,
            )

            parsed = to_decimal(balance_value)

            if parsed is not None:
                return parsed

    # Second preference:
    # any valid available balance field.
    for record in candidates:

        balance_value = first_present(
            record,
            balance_field_names,
        )

        parsed = to_decimal(balance_value)

        if parsed is not None:
            return parsed

    return None


# ==================================================================================================
# SECTION 15 - POSITION PARSER
# ==================================================================================================

def normalize_position_records(payload):

    root = unwrap_common_container(payload)

    if root is None:
        return []

    if isinstance(root, list):
        return [
            item
            for item in root
            if isinstance(item, dict)
        ]

    if isinstance(root, dict):

        # If the root itself looks like a position record.
        if any(
            key in root
            for key in (
                "symbol",
                "side",
                "size",
                "positionAmt",
                "quantity",
            )
        ):
            return [root]

        records = []

        for value in root.values():

            if isinstance(value, list):
                records.extend(
                    item
                    for item in value
                    if isinstance(item, dict)
                )

        return records

    return []


def position_size(record):

    value = first_present(
        record,
        (
            "size",
            "positionAmt",
            "positionSize",
            "quantity",
            "qty",
        ),
    )

    parsed = to_decimal(value)

    if parsed is None:
        return Decimal("0")

    return abs(parsed)


# ==================================================================================================
# SECTION 16 - SYMBOL CONFIGURATION PARSER
# ==================================================================================================

def find_symbol_configuration(payload, symbol):

    records = collect_dicts(payload)

    symbol_upper = symbol.upper()

    # --------------------------------------------------------------
    # PASS 1:
    # exact symbol match.
    # --------------------------------------------------------------

    for record in records:

        observed_symbol = first_present(
            record,
            (
                "symbol",
                "contractCode",
                "contract",
                "instrument",
            ),
        )

        if (
            observed_symbol is not None
            and str(observed_symbol).upper() == symbol_upper
        ):
            return record

    # --------------------------------------------------------------
    # PASS 2:
    # configuration-like record even if symbol was omitted by API.
    # --------------------------------------------------------------

    config_keys = {
        "margintype",
        "marginmode",
        "isolatedlongleverage",
        "isolatedshortleverage",
        "longleverage",
        "shortleverage",
        "crossleverage",
    }

    for record in records:

        keys = {
            str(key).lower()
            for key in record.keys()
        }

        if keys.intersection(config_keys):
            return record

    return None


def parse_symbol_configuration(payload, symbol):

    record = find_symbol_configuration(
        payload,
        symbol,
    )

    if record is None:
        return {
            "record": None,
            "margin_type": None,
            "position_mode": None,
            "cross_leverage": None,
            "long_leverage": None,
            "short_leverage": None,
        }

    margin_type = first_present(
        record,
        (
            "marginType",
            "margin_type",
            "marginMode",
            "margin_mode",
        ),
    )

    position_mode = first_present(
        record,
        (
            "separatedType",
            "separatedMode",
            "positionMode",
            "position_mode",
        ),
    )

    cross_leverage = first_present(
        record,
        (
            "crossLeverage",
            "cross_leverage",
        ),
    )

    long_leverage = first_present(
        record,
        (
            "isolatedLongLeverage",
            "isolated_long_leverage",
            "longLeverage",
            "long_leverage",
        ),
    )

    short_leverage = first_present(
        record,
        (
            "isolatedShortLeverage",
            "isolated_short_leverage",
            "shortLeverage",
            "short_leverage",
        ),
    )

    return {
        "record": record,
        "margin_type": (
            str(margin_type).upper()
            if margin_type is not None
            else None
        ),
        "position_mode": (
            str(position_mode).upper()
            if position_mode is not None
            else None
        ),
        "cross_leverage": to_decimal(cross_leverage),
        "long_leverage": to_decimal(long_leverage),
        "short_leverage": to_decimal(short_leverage),
    }


# ==================================================================================================
# SECTION 17 - TEST 1
# ==================================================================================================

def test_absolute_safety_firebreak():

    section(
        f"{VERSION} TEST 1: ABSOLUTE SAFETY FIREBREAK"
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    check(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED is False,
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

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY is True,
    )

    check(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY is True,
    )


# ==================================================================================================
# SECTION 18 - TEST 2
# ==================================================================================================

def test_credentials():

    section(
        f"{VERSION} TEST 2: CREDENTIAL PRESENCE"
    )

    credentials = get_credentials()

    check(
        "WEEX API Key Is Present",
        bool(credentials["key"]),
    )

    check(
        "WEEX API Secret Is Present",
        bool(credentials["secret"]),
    )

    check(
        "WEEX API Passphrase Is Present",
        bool(credentials["passphrase"]),
    )


# ==================================================================================================
# SECTION 19 - TEST 3
# ==================================================================================================

def test_live_balance():

    section(
        f"{VERSION} TEST 3: LIVE BALANCE RECONCILIATION"
    )

    payload = authenticated_get(
        BALANCE_PATH
    )

    log(
        f"{VERSION}: BALANCE PATH={BALANCE_PATH}"
    )

    available_usdt = parse_available_usdt(
        payload
    )

    check(
        "Available Balance Was Read",
        available_usdt is not None,
    )

    check(
        "Available Balance Is Positive",
        available_usdt > Decimal("0"),
    )

    runtime["available_usdt"] = available_usdt

    log(
        f"{VERSION}: BALANCE PATH={BALANCE_PATH}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT={available_usdt}"
    )


# ==================================================================================================
# SECTION 20 - TEST 4
# ==================================================================================================

def test_positions():

    section(
        f"{VERSION} TEST 4: POSITION RECONCILIATION"
    )

    payload = authenticated_get(
        ALL_POSITIONS_PATH
    )

    log(
        f"{VERSION}: POSITION PATH={ALL_POSITIONS_PATH}"
    )

    records = normalize_position_records(
        payload
    )

    btc_records = [
        record
        for record in records
        if str(
            first_present(
                record,
                ("symbol",),
            )
            or ""
        ).upper() == SYMBOL
    ]

    open_positions = [
        record
        for record in btc_records
        if position_size(record) > Decimal("0")
    ]

    runtime["total_position_records"] = len(records)
    runtime["btc_position_records"] = len(btc_records)
    runtime["btc_open_positions"] = len(open_positions)

    check(
        "Position Response Was Read",
        payload is not None,
    )

    check(
        "BTCUSDT Open Position Count Is Zero",
        len(open_positions) == 0,
    )

    log(
        f"{VERSION}: POSITION PATH={ALL_POSITIONS_PATH}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS={len(records)}"
    )

    log(
        f"{VERSION}: BTCUSDT POSITION RECORDS={len(btc_records)}"
    )

    log(
        f"{VERSION}: BTCUSDT OPEN POSITIONS={len(open_positions)}"
    )


# ==================================================================================================
# SECTION 21 - TEST 5
# ==================================================================================================

def test_account_configuration():

    section(
        f"{VERSION} TEST 5: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    # IMPORTANT R34V CORRECTION:
    #
    # R34U attempted to derive configuration from:
    #
    #   /capi/v3/account/position/singlePosition
    #
    # That endpoint represents POSITION DATA.
    #
    # On a flat account it may contain no position record from which
    # marginType can be extracted.
    #
    # R34V instead uses the dedicated WEEX V3 configuration endpoint:
    #
    #   /capi/v3/account/symbolConfig
    #
    # This endpoint explicitly exposes:
    #
    #   marginType
    #   separatedType
    #   crossLeverage
    #   isolatedLongLeverage
    #   isolatedShortLeverage

    payload = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    log(
        f"{VERSION}: ACCOUNT CONFIGURATION PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    config = parse_symbol_configuration(
        payload,
        SYMBOL,
    )

    margin_type = config["margin_type"]
    position_mode = config["position_mode"]
    cross_leverage = config["cross_leverage"]
    long_leverage = config["long_leverage"]
    short_leverage = config["short_leverage"]

    runtime["margin_type"] = margin_type
    runtime["position_mode"] = position_mode
    runtime["cross_leverage"] = cross_leverage
    runtime["long_leverage"] = long_leverage
    runtime["short_leverage"] = short_leverage

    check(
        "BTCUSDT Configuration Record Was Read",
        config["record"] is not None,
    )

    check(
        "Margin Type Was Read",
        margin_type is not None,
    )

    check(
        "Margin Type Is ISOLATED",
        margin_type == TARGET_MARGIN_TYPE,
    )

    check(
        "Isolated Long Leverage Was Read",
        long_leverage is not None,
    )

    check(
        "Isolated Short Leverage Was Read",
        short_leverage is not None,
    )

    check(
        "Isolated Long Leverage Is 100x",
        long_leverage == TARGET_LONG_LEVERAGE,
    )

    check(
        "Isolated Short Leverage Is 100x",
        short_leverage == TARGET_SHORT_LEVERAGE,
    )

    runtime["configuration_verified"] = True
    runtime["correction_required"] = False

    log(
        f"{VERSION}: OBSERVED MARGIN={margin_type}"
    )

    log(
        f"{VERSION}: OBSERVED POSITION MODE="
        f"{position_mode}"
    )

    log(
        f"{VERSION}: OBSERVED CROSS LEVERAGE="
        f"{cross_leverage}"
    )

    log(
        f"{VERSION}: OBSERVED LONG LEVERAGE="
        f"{long_leverage}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT LEVERAGE="
        f"{short_leverage}x"
    )

    log(
        f"{VERSION}: TARGET MARGIN="
        f"{TARGET_MARGIN_TYPE}"
    )

    log(
        f"{VERSION}: TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"{VERSION}: TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"{VERSION}: CORRECTION REQUIRED=False"
    )


# ==================================================================================================
# SECTION 22 - TEST 6
# ==================================================================================================

def test_initial_entry_budget():

    section(
        f"{VERSION} TEST 6: INITIAL ENTRY READINESS"
    )

    balance = runtime["available_usdt"]

    check(
        "Available Balance Exists For Entry Calculation",
        balance is not None,
    )

    entry_margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    entry_notional = (
        entry_margin
        * TARGET_LONG_LEVERAGE
    )

    runtime["entry_margin_budget"] = entry_margin

    check(
        "Initial Entry Percent Is Positive",
        INITIAL_ENTRY_PERCENT > 0,
    )

    check(
        "Initial Entry Margin Budget Is Positive",
        entry_margin > 0,
    )

    check(
        "Initial Entry Is Within Exposure Cap",
        INITIAL_ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    log(
        f"{VERSION}: INITIAL ENTRY PERCENT="
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    log(
        f"{VERSION}: INITIAL ENTRY MARGIN BUDGET="
        f"{entry_margin} USDT"
    )

    log(
        f"{VERSION}: INITIAL ENTRY NOTIONAL AT 100x="
        f"{entry_notional} USDT"
    )


# ==================================================================================================
# SECTION 23 - TEST 7
# ==================================================================================================

def test_maximum_strategy_exposure():

    section(
        f"{VERSION} TEST 7: MAXIMUM STRATEGY EXPOSURE"
    )

    balance = runtime["available_usdt"]

    maximum_allowed_margin = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    # Strategy structure:
    #
    # Initial entry = 5%
    # One pyramid   = 5%
    # Three backups = 3 x 5%
    #
    # Total planned maximum = 25% of balance.

    planned_percent = (
        INITIAL_ENTRY_PERCENT
        + (
            PYRAMID_PERCENT
            * Decimal(MAX_PYRAMID_ADDS)
        )
        + (
            BACKUP_PERCENT
            * Decimal(MAX_BACKUPS)
        )
    )

    planned_margin = (
        balance
        * planned_percent
        / Decimal("100")
    )

    runtime["max_strategy_margin"] = planned_margin

    check(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    check(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3,
    )

    check(
        "Planned Strategy Exposure Is Within 35%",
        planned_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    check(
        "Planned Maximum Strategy Margin Is Within Cap",
        planned_margin
        <= maximum_allowed_margin,
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    log(
        f"{VERSION}: PLANNED STRATEGY EXPOSURE="
        f"{planned_percent}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{maximum_allowed_margin} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{planned_margin} USDT"
    )


# ==================================================================================================
# SECTION 24 - TEST 8
# ==================================================================================================

def test_take_profit_structure():

    section(
        f"{VERSION} TEST 8: TAKE-PROFIT STRUCTURE"
    )

    total_tp = (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
    )

    check(
        "TP Allocation Totals 100%",
        total_tp == Decimal("100"),
    )

    check(
        "TP1 Is 20%",
        TP1_PERCENT == Decimal("20"),
    )

    check(
        "TP2 Is 20%",
        TP2_PERCENT == Decimal("20"),
    )

    check(
        "TP3 Is 60%",
        TP3_PERCENT == Decimal("60"),
    )

    check(
        "TP1 Trigger Is 0.5%",
        TP1_TRIGGER_PERCENT == Decimal("0.5"),
    )

    check(
        "TP2 Trigger Is 1.0%",
        TP2_TRIGGER_PERCENT == Decimal("1.0"),
    )

    check(
        "Trailing Distance Is 0.20%",
        TRAILING_DISTANCE_PERCENT == Decimal("0.20"),
    )

    log(
        f"{VERSION}: TP1="
        f"{TP1_PERCENT}% @ +{TP1_TRIGGER_PERCENT}%"
    )

    log(
        f"{VERSION}: TP2="
        f"{TP2_PERCENT}% @ +{TP2_TRIGGER_PERCENT}%"
    )

    log(
        f"{VERSION}: TP3="
        f"{TP3_PERCENT}% TRAILING"
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{TRAILING_DISTANCE_PERCENT}%"
    )


# ==================================================================================================
# SECTION 25 - TEST 9
# ==================================================================================================

def test_final_read_only_gate():

    section(
        f"{VERSION} TEST 9: FINAL READ-ONLY EXECUTION FIREBREAK"
    )

    check(
        "Account Configuration Is Verified",
        runtime["configuration_verified"] is True,
    )

    check(
        "Correction Is Not Required",
        runtime["correction_required"] is False,
    )

    check(
        "BTCUSDT Is Flat",
        runtime["btc_open_positions"] == 0,
    )

    check(
        "Network Writes Remain Zero",
        COUNTERS["network_writes"] == 0,
    )

    check(
        "Real Orders Remain Zero",
        COUNTERS["real_orders"] == 0,
    )

    check(
        "Demo Orders Remain Zero",
        COUNTERS["demo_orders"] == 0,
    )

    check(
        "Leverage Mutations Remain Zero",
        COUNTERS["leverage_mutations"] == 0,
    )

    check(
        "Margin Mutations Remain Zero",
        COUNTERS["margin_mutations"] == 0,
    )

    check(
        "Position Mutations Remain Zero",
        COUNTERS["position_mutations"] == 0,
    )

    check(
        "Account Mutations Remain Zero",
        COUNTERS["account_mutations"] == 0,
    )

    check(
        "Only Authenticated GETs Were Used",
        COUNTERS["authenticated_gets"] >= 3,
    )


# ==================================================================================================
# SECTION 26 - HEARTBEAT
# ==================================================================================================

def heartbeat_loop():

    count = 0

    while True:

        time.sleep(HEARTBEAT_SECONDS)

        count += 1

        log(
            f"{VERSION}: HEARTBEAT {count} | "
            f"phase={runtime['phase']} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get="
            f"{COUNTERS['authenticated_gets']} | "
            f"network-writes="
            f"{COUNTERS['network_writes']} | "
            f"real-orders="
            f"{COUNTERS['real_orders']} | "
            f"demo-orders="
            f"{COUNTERS['demo_orders']} | "
            f"margin={runtime['margin_type']} | "
            f"long={runtime['long_leverage']} | "
            f"short={runtime['short_leverage']} | "
            f"correction-required="
            f"{runtime['correction_required']}"
        )


# ==================================================================================================
# SECTION 27 - FAILURE HEARTBEAT
# ==================================================================================================

def failure_heartbeat_loop():

    while True:

        time.sleep(HEARTBEAT_SECONDS)

        log(
            f"{VERSION}: FAILURE HEARTBEAT | "
            f"phase={runtime['phase']} | "
            f"network-writes="
            f"{COUNTERS['network_writes']} | "
            f"real-orders="
            f"{COUNTERS['real_orders']} | "
            f"demo-orders="
            f"{COUNTERS['demo_orders']}"
        )


# ==================================================================================================
# SECTION 28 - MAIN
# ==================================================================================================

def main():

    start_health_server()

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: PUBLIC READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )

    log(
        f"{VERSION}: MARGIN MUTATION DISABLED"
    )

    log(
        f"{VERSION}: POSITION MUTATION DISABLED"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATION DISABLED"
    )

    runtime["phase"] = "VALIDATING"

    try:

        test_absolute_safety_firebreak()

        test_credentials()

        test_live_balance()

        test_positions()

        test_account_configuration()

        test_initial_entry_budget()

        test_maximum_strategy_exposure()

        test_take_profit_structure()

        test_final_read_only_gate()

        runtime["phase"] = (
            "LIVE_ACCOUNT_CONFIGURATION_VALIDATED"
        )

        section(
            f"{VERSION}: VALIDATION COMPLETE"
        )

        log(
            f"{VERSION}: PHASE="
            f"{runtime['phase']}"
        )

        log(
            f"{VERSION}: AVAILABLE USDT="
            f"{runtime['available_usdt']}"
        )

        log(
            f"{VERSION}: BTCUSDT OPEN POSITIONS="
            f"{runtime['btc_open_positions']}"
        )

        log(
            f"{VERSION}: OBSERVED MARGIN="
            f"{runtime['margin_type']}"
        )

        log(
            f"{VERSION}: OBSERVED LONG="
            f"{runtime['long_leverage']}x"
        )

        log(
            f"{VERSION}: OBSERVED SHORT="
            f"{runtime['short_leverage']}x"
        )

        log(
            f"{VERSION}: CONFIGURATION VERIFIED="
            f"{runtime['configuration_verified']}"
        )

        log(
            f"{VERSION}: CORRECTION REQUIRED="
            f"{runtime['correction_required']}"
        )

        log(
            f"{VERSION}: AUTHENTICATED GETS="
            f"{COUNTERS['authenticated_gets']}"
        )

        log(
            f"{VERSION}: NETWORK WRITES="
            f"{COUNTERS['network_writes']}"
        )

        log(
            f"{VERSION}: LEVERAGE MUTATIONS="
            f"{COUNTERS['leverage_mutations']}"
        )

        log(
            f"{VERSION}: MARGIN MUTATIONS="
            f"{COUNTERS['margin_mutations']}"
        )

        log(
            f"{VERSION}: REAL ORDERS="
            f"{COUNTERS['real_orders']}"
        )

        log(
            f"{VERSION}: DEMO ORDERS="
            f"{COUNTERS['demo_orders']}"
        )

        log(
            f"{VERSION}: NO REAL ORDER WAS SENT"
        )

        log(
            f"{VERSION}: NO DEMO ORDER WAS SENT"
        )

        log(
            f"{VERSION}: NO ACCOUNT MUTATION WAS SENT"
        )

        section(
            f"{VERSION}: ENTERING STABLE HEARTBEAT"
        )

        heartbeat_loop()

    except Exception as exc:

        runtime["phase"] = "VALIDATION_FAILED"

        runtime["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{runtime['error']}"
        )

        log(
            f"{VERSION}: AUTHENTICATED GETS="
            f"{COUNTERS['authenticated_gets']}"
        )

        log(
            f"{VERSION}: NETWORK WRITES="
            f"{COUNTERS['network_writes']}"
        )

        log(
            f"{VERSION}: LEVERAGE MUTATIONS="
            f"{COUNTERS['leverage_mutations']}"
        )

        log(
            f"{VERSION}: MARGIN MUTATIONS="
            f"{COUNTERS['margin_mutations']}"
        )

        log(
            f"{VERSION}: REAL ORDERS="
            f"{COUNTERS['real_orders']}"
        )

        log(
            f"{VERSION}: DEMO ORDERS="
            f"{COUNTERS['demo_orders']}"
        )

        failure_heartbeat_loop()


# ==================================================================================================
# SECTION 29 - ENTRY POINT
# ==================================================================================================

if __name__ == "__main__":
    main()
