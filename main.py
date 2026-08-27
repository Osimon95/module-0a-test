import os
import json
import time
import hmac
import hashlib
import base64
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from decimal import Decimal, ROUND_DOWN, ROUND_UP


# ==================================================================================================
# R34J - POST-CORRECTION STRATEGY / ACCOUNT READINESS RECONCILIATION
# ==================================================================================================

VERSION = "R34J"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")

API_KEY = os.getenv("WEEX_API_KEY", "").strip()
API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

HEALTH_PORT = int(os.getenv("PORT", "10000"))

TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_SIZE_PERCENT = Decimal("5")
BACKUP_SIZE_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ==================================================================================================
# HARD SAFETY POLICY
# ==================================================================================================

AUTHENTICATED_READ_ONLY = True

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

network_write_counter = 0
real_order_counter = 0
demo_order_counter = 0
leverage_mutation_counter = 0

authenticated_get_counter = 0

phase = "BOOTING"

readiness_verified = False
readiness_blockers = []

latest_state = {}

heartbeat_counter = 0


# ==================================================================================================
# FORMAT HELPERS
# ==================================================================================================

LINE = "-" * 100


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def pass_line(label):
    log(f"{label:<82} ✅ PASS")


def fail_line(label):
    log(f"{label:<82} ❌ FAIL")


def bool_line(label, condition):
    if condition:
        pass_line(label)
    else:
        fail_line(label)


def decimal_value(value, default="0"):
    try:
        if value is None:
            return Decimal(default)

        text = str(value).strip()

        if not text:
            return Decimal(default)

        text = text.lower().replace("x", "")

        return Decimal(text)

    except Exception:
        return Decimal(default)


def normalize_margin(value):
    if value is None:
        return ""

    text = str(value).strip().upper()

    mappings = {
        "1": "ISOLATED",
        "ISOLATE": "ISOLATED",
        "ISOLATED": "ISOLATED",
        "FIXED": "ISOLATED",
        "2": "CROSS",
        "CROSSED": "CROSS",
        "CROSS": "CROSS",
    }

    return mappings.get(text, text)


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )


def sha256_json(data):
    return hashlib.sha256(
        canonical_json(data).encode("utf-8")
    ).hexdigest()


# ==================================================================================================
# SAFETY BOUNDARY
# ==================================================================================================

def assert_write_disabled():
    assert NETWORK_WRITES_ENABLED is False
    assert REAL_ORDER_EXECUTION is False
    assert DEMO_ORDER_EXECUTION is False
    assert LEVERAGE_MUTATION_ENABLED is False
    assert MARGIN_MUTATION_ENABLED is False
    assert POSITION_MUTATION_ENABLED is False
    assert ACCOUNT_MUTATION_ENABLED is False


def forbidden_network_write(*args, **kwargs):
    global network_write_counter

    raise RuntimeError(
        "R34J SAFETY BLOCK: exchange network writes are disabled"
    )


def forbidden_real_order(*args, **kwargs):
    global real_order_counter

    raise RuntimeError(
        "R34J SAFETY BLOCK: real order execution is disabled"
    )


def forbidden_demo_order(*args, **kwargs):
    global demo_order_counter

    raise RuntimeError(
        "R34J SAFETY BLOCK: demo order execution is disabled"
    )


# ==================================================================================================
# AUTHENTICATED GET SIGNING
# ==================================================================================================

def require_credentials():
    missing = []

    if not API_KEY:
        missing.append("WEEX_API_KEY")

    if not API_SECRET:
        missing.append("WEEX_API_SECRET")

    if not API_PASSPHRASE:
        missing.append("WEEX_API_PASSPHRASE")

    if missing:
        raise RuntimeError(
            "Missing credentials: " + ", ".join(missing)
        )


def make_signature(timestamp_ms, method, request_path, body=""):
    prehash = (
        str(timestamp_ms)
        + method.upper()
        + request_path
        + body
    )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def authenticated_get(path):
    global authenticated_get_counter

    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only transport disabled"
        )

    if not path.startswith("/"):
        raise RuntimeError("Invalid API path")

    require_credentials()

    timestamp_ms = str(int(time.time() * 1000))

    signature = make_signature(
        timestamp_ms=timestamp_ms,
        method="GET",
        request_path=path,
        body=""
    )

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "Content-Type": "application/json",
        "User-Agent": f"{VERSION}/read-only",
    }

    request = urllib.request.Request(
        BASE_URL + path,
        method="GET",
        headers=headers
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            authenticated_get_counter += 1

            if not raw.strip():
                return {}

            return json.loads(raw)

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"Authenticated GET {path} failed: "
            f"HTTP {exc.code}: {body}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Authenticated GET {path} failed: {exc}"
        )


# ==================================================================================================
# FLEXIBLE RESPONSE EXTRACTION
# ==================================================================================================

def unwrap_response(payload):
    if not isinstance(payload, dict):
        return payload

    for key in ("data", "result"):
        value = payload.get(key)

        if value is not None:
            return value

    return payload


def find_first_dict(payload):
    value = unwrap_response(payload)

    if isinstance(value, dict):
        return value

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return item

    return {}


def search_dict_value(obj, keys):
    if not isinstance(obj, dict):
        return None

    lowered = {
        str(key).lower(): value
        for key, value in obj.items()
    }

    for candidate in keys:
        key = candidate.lower()

        if key in lowered:
            return lowered[key]

    return None


def extract_list(payload):
    payload = unwrap_response(payload)

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):

        for key in (
            "list",
            "rows",
            "items",
            "positions",
            "positionList",
        ):

            value = payload.get(key)

            if isinstance(value, list):
                return value

    return []


# ==================================================================================================
# ACCOUNT STATE PARSING
# ==================================================================================================

def extract_available_usdt(payload):
    root = unwrap_response(payload)

    candidates = []

    if isinstance(root, list):
        candidates = root

    elif isinstance(root, dict):

        nested = None

        for key in (
            "list",
            "assets",
            "balances",
            "accountList",
        ):
            value = root.get(key)

            if isinstance(value, list):
                nested = value
                break

        if nested is not None:
            candidates = nested

        else:
            candidates = [root]

    for item in candidates:

        if not isinstance(item, dict):
            continue

        coin = search_dict_value(
            item,
            [
                "coin",
                "currency",
                "asset",
                "marginCoin",
            ]
        )

        if coin is not None:

            if str(coin).upper() not in (
                "USDT",
                "SUSDT",
            ):
                continue

        available = search_dict_value(
            item,
            [
                "available",
                "availableBalance",
                "availableAmount",
                "availableMargin",
                "free",
                "balance",
            ]
        )

        if available is not None:
            return decimal_value(available)

    return Decimal("0")


def extract_position_count(payload):
    positions = extract_list(payload)

    active = 0

    for item in positions:

        if not isinstance(item, dict):
            continue

        qty = search_dict_value(
            item,
            [
                "size",
                "positionAmt",
                "positionSize",
                "holdVol",
                "total",
                "available",
            ]
        )

        qty_decimal = abs(decimal_value(qty))

        if qty_decimal > 0:
            active += 1

    return active


def extract_symbol_config(payload):
    root = unwrap_response(payload)

    target = {}

    if isinstance(root, list):

        for item in root:

            if not isinstance(item, dict):
                continue

            symbol = search_dict_value(
                item,
                [
                    "symbol",
                    "contractCode",
                ]
            )

            if str(symbol).upper() == SYMBOL:
                target = item
                break

    elif isinstance(root, dict):

        list_candidate = None

        for key in (
            "list",
            "rows",
            "items",
        ):

            value = root.get(key)

            if isinstance(value, list):
                list_candidate = value
                break

        if list_candidate:

            for item in list_candidate:

                if not isinstance(item, dict):
                    continue

                symbol = search_dict_value(
                    item,
                    [
                        "symbol",
                        "contractCode",
                    ]
                )

                if str(symbol).upper() == SYMBOL:
                    target = item
                    break

        else:
            target = root

    margin_mode = normalize_margin(
        search_dict_value(
            target,
            [
                "marginType",
                "marginMode",
                "margin_mode",
            ]
        )
    )

    long_leverage = decimal_value(
        search_dict_value(
            target,
            [
                "isolatedLongLeverage",
                "longLeverage",
                "long_leverage",
            ]
        )
    )

    short_leverage = decimal_value(
        search_dict_value(
            target,
            [
                "isolatedShortLeverage",
                "shortLeverage",
                "short_leverage",
            ]
        )
    )

    position_mode = search_dict_value(
        target,
        [
            "positionMode",
            "holdMode",
            "position_mode",
        ]
    )

    return {
        "margin_mode": margin_mode,
        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
        "position_mode": str(position_mode or "").upper(),
        "raw": target,
    }


# ==================================================================================================
# CONTRACT / SYMBOL CONSTRAINT PARSING
# ==================================================================================================

def extract_contract_constraints(payload):
    root = unwrap_response(payload)

    target = {}

    if isinstance(root, list):

        for item in root:

            if not isinstance(item, dict):
                continue

            symbol = search_dict_value(
                item,
                [
                    "symbol",
                    "contractCode",
                ]
            )

            if str(symbol).upper() == SYMBOL:
                target = item
                break

    elif isinstance(root, dict):

        for key in (
            "list",
            "rows",
            "items",
        ):

            value = root.get(key)

            if isinstance(value, list):

                for item in value:

                    if not isinstance(item, dict):
                        continue

                    symbol = search_dict_value(
                        item,
                        [
                            "symbol",
                            "contractCode",
                        ]
                    )

                    if str(symbol).upper() == SYMBOL:
                        target = item
                        break

                if target:
                    break

        if not target:
            target = root

    min_qty = decimal_value(
        search_dict_value(
            target,
            [
                "minOrderQty",
                "minQty",
                "minTradeNum",
                "minOrderAmount",
                "minVolume",
            ]
        )
    )

    qty_step = decimal_value(
        search_dict_value(
            target,
            [
                "qtyStep",
                "quantityStep",
                "sizeStep",
                "stepSize",
            ]
        )
    )

    qty_precision = search_dict_value(
        target,
        [
            "qtyPrecision",
            "quantityPrecision",
            "volumePlace",
            "sizePrecision",
        ]
    )

    price_precision = search_dict_value(
        target,
        [
            "pricePrecision",
            "pricePlace",
        ]
    )

    price_step = decimal_value(
        search_dict_value(
            target,
            [
                "priceStep",
                "tickSize",
            ]
        )
    )

    min_leverage = decimal_value(
        search_dict_value(
            target,
            [
                "minLeverage",
                "minLever",
            ]
        ),
        default="1"
    )

    max_leverage = decimal_value(
        search_dict_value(
            target,
            [
                "maxLeverage",
                "maxLever",
            ]
        )
    )

    try:
        qty_precision_int = int(qty_precision)

    except Exception:
        qty_precision_int = 4

    try:
        price_precision_int = int(price_precision)

    except Exception:
        price_precision_int = 1

    if qty_step <= 0:
        qty_step = Decimal(
            "1"
        ).scaleb(-qty_precision_int)

    return {
        "min_qty": min_qty,
        "qty_step": qty_step,
        "qty_precision": qty_precision_int,
        "price_precision": price_precision_int,
        "price_step": price_step,
        "min_leverage": min_leverage,
        "max_leverage": max_leverage,
        "raw": target,
    }


# ==================================================================================================
# PUBLIC MARK PRICE
# ==================================================================================================

def public_get(path):
    request = urllib.request.Request(
        BASE_URL + path,
        method="GET",
        headers={
            "User-Agent": f"{VERSION}/public-read-only"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            if not raw.strip():
                return {}

            return json.loads(raw)

    except Exception as exc:
        raise RuntimeError(
            f"Public GET {path} failed: {exc}"
        )


def extract_price(payload):
    root = unwrap_response(payload)

    candidates = []

    if isinstance(root, list):
        candidates = root

    elif isinstance(root, dict):
        candidates = [root]

        for key in (
            "list",
            "rows",
            "items",
        ):

            value = root.get(key)

            if isinstance(value, list):
                candidates = value
                break

    for item in candidates:

        if not isinstance(item, dict):
            continue

        symbol = search_dict_value(
            item,
            [
                "symbol",
                "contractCode",
            ]
        )

        if symbol is not None:

            if str(symbol).upper() != SYMBOL:
                continue

        price = search_dict_value(
            item,
            [
                "price",
                "markPrice",
                "last",
                "lastPrice",
                "close",
            ]
        )

        value = decimal_value(price)

        if value > 0:
            return value

    return Decimal("0")


def obtain_mark_price():
    paths = [
        f"/capi/v2/market/ticker?symbol={SYMBOL}",
        f"/capi/v2/market/tickers?symbol={SYMBOL}",
        f"/capi/v1/market/ticker?symbol={SYMBOL}",
    ]

    errors = []

    for path in paths:

        try:

            payload = public_get(path)

            price = extract_price(payload)

            if price > 0:
                return price

        except Exception as exc:
            errors.append(str(exc))

    raise RuntimeError(
        "Unable to obtain mark price: "
        + " | ".join(errors)
    )


# ==================================================================================================
# QUANTITY / EXPOSURE CALCULATIONS
# ==================================================================================================

def floor_to_step(value, step):
    if step <= 0:
        return value

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def ceil_to_step(value, step):
    if step <= 0:
        return value

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_UP
    )

    return units * step


def calculate_trade_plan(
    available_balance,
    mark_price,
    constraints,
):
    entry_margin_budget = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    planned_notional = (
        entry_margin_budget
        * TARGET_LONG_LEVERAGE
    )

    raw_qty = Decimal("0")

    if mark_price > 0:
        raw_qty = planned_notional / mark_price

    qty_step = constraints["qty_step"]

    rounded_down_qty = floor_to_step(
        raw_qty,
        qty_step,
    )

    minimum_valid_qty = max(
        constraints["min_qty"],
        qty_step,
    )

    execution_candidate_qty = rounded_down_qty

    if (
        execution_candidate_qty > 0
        and execution_candidate_qty < minimum_valid_qty
    ):
        execution_candidate_qty = minimum_valid_qty

    if (
        execution_candidate_qty == 0
        and raw_qty > 0
    ):
        execution_candidate_qty = ceil_to_step(
            minimum_valid_qty,
            qty_step,
        )

    execution_notional = (
        execution_candidate_qty
        * mark_price
    )

    execution_margin_100x = (
        execution_notional
        / TARGET_LONG_LEVERAGE
        if TARGET_LONG_LEVERAGE > 0
        else Decimal("0")
    )

    actual_margin_percent = (
        execution_margin_100x
        / available_balance
        * Decimal("100")
        if available_balance > 0
        else Decimal("0")
    )

    maximum_margin_budget = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    theoretical_total_strategy_percent = (
        INITIAL_ENTRY_PERCENT
        + (
            PYRAMID_SIZE_PERCENT
            * Decimal(MAX_PYRAMID_ADDS)
        )
        + (
            BACKUP_SIZE_PERCENT
            * Decimal(MAX_BACKUPS)
        )
    )

    theoretical_total_margin = (
        available_balance
        * theoretical_total_strategy_percent
        / Decimal("100")
    )

    return {
        "entry_margin_budget": entry_margin_budget,
        "planned_notional": planned_notional,
        "raw_qty": raw_qty,
        "rounded_down_qty": rounded_down_qty,
        "execution_candidate_qty": execution_candidate_qty,
        "execution_notional": execution_notional,
        "execution_margin_100x": execution_margin_100x,
        "actual_margin_percent": actual_margin_percent,
        "maximum_margin_budget": maximum_margin_budget,
        "theoretical_total_strategy_percent":
            theoretical_total_strategy_percent,
        "theoretical_total_margin":
            theoretical_total_margin,
    }


# ==================================================================================================
# LIVE READ-ONLY RECONCILIATION
# ==================================================================================================

def fetch_balance():
    candidate_paths = [
        "/capi/v2/account/assets",
        "/capi/v2/account/balance",
    ]

    errors = []

    for path in candidate_paths:

        try:
            payload = authenticated_get(path)

            balance = extract_available_usdt(payload)

            if balance >= 0:
                return balance, payload, path

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Could not read account balance: "
        + " | ".join(errors)
    )


def fetch_positions():
    candidate_paths = [
        f"/capi/v2/account/allPosition?symbol={SYMBOL}",
        "/capi/v2/account/allPosition",
    ]

    errors = []

    for path in candidate_paths:

        try:

            payload = authenticated_get(path)

            count = extract_position_count(payload)

            return count, payload, path

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Could not read open positions: "
        + " | ".join(errors)
    )


def fetch_symbol_config():
    candidate_paths = [
        f"/capi/v2/account/symbolConfig?symbol={SYMBOL}",
        "/capi/v2/account/symbolConfig",
    ]

    errors = []

    for path in candidate_paths:

        try:

            payload = authenticated_get(path)

            config = extract_symbol_config(
                payload
            )

            if (
                config["margin_mode"]
                or config["long_leverage"] > 0
                or config["short_leverage"] > 0
            ):
                return config, payload, path

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Could not read symbol configuration: "
        + " | ".join(errors)
    )


def fetch_contract_constraints():
    candidate_paths = [
        f"/capi/v2/market/contracts?symbol={SYMBOL}",
        "/capi/v2/market/contracts",
        f"/capi/v1/market/contracts?symbol={SYMBOL}",
    ]

    errors = []

    for path in candidate_paths:

        try:

            payload = public_get(path)

            constraints = (
                extract_contract_constraints(
                    payload
                )
            )

            if constraints["qty_step"] > 0:
                return (
                    constraints,
                    payload,
                    path,
                )

        except Exception as exc:
            errors.append(
                f"{path}: {exc}"
            )

    raise RuntimeError(
        "Could not read contract constraints: "
        + " | ".join(errors)
    )


# ==================================================================================================
# VALIDATION
# ==================================================================================================

def evaluate_readiness(state):
    blockers = []

    if state["available_balance"] <= 0:
        blockers.append(
            "available USDT balance is zero"
        )

    if state["margin_mode"] != TARGET_MARGIN_MODE:
        blockers.append(
            f"margin mode is {state['margin_mode']} "
            f"instead of {TARGET_MARGIN_MODE}"
        )

    if (
        state["long_leverage"]
        != TARGET_LONG_LEVERAGE
    ):
        blockers.append(
            f"long leverage is "
            f"{state['long_leverage']}x "
            f"instead of 100x"
        )

    if (
        state["short_leverage"]
        != TARGET_SHORT_LEVERAGE
    ):
        blockers.append(
            f"short leverage is "
            f"{state['short_leverage']}x "
            f"instead of 100x"
        )

    if state["open_positions"] != 0:
        blockers.append(
            f"{state['open_positions']} "
            f"open position(s) detected"
        )

    if state["mark_price"] <= 0:
        blockers.append(
            "mark price unavailable"
        )

    max_lev = state["max_leverage"]

    if (
        max_lev > 0
        and TARGET_LONG_LEVERAGE > max_lev
    ):
        blockers.append(
            f"100x exceeds exchange maximum "
            f"{max_lev}x"
        )

    min_lev = state["min_leverage"]

    if (
        min_lev > 0
        and TARGET_LONG_LEVERAGE < min_lev
    ):
        blockers.append(
            f"100x is below exchange minimum "
            f"{min_lev}x"
        )

    candidate_qty = state[
        "execution_candidate_qty"
    ]

    if candidate_qty <= 0:
        blockers.append(
            "calculated candidate quantity "
            "is zero"
        )

    if (
        state["min_qty"] > 0
        and candidate_qty < state["min_qty"]
    ):
        blockers.append(
            "candidate quantity below "
            "exchange minimum"
        )

    if (
        state[
            "theoretical_total_strategy_percent"
        ]
        > MAX_FUND_EXPOSURE_PERCENT
    ):
        blockers.append(
            "strategy exposure exceeds "
            "configured maximum"
        )

    if (
        state["execution_margin_100x"]
        > state["maximum_margin_budget"]
    ):
        blockers.append(
            "candidate initial trade exceeds "
            "maximum margin exposure"
        )

    if NETWORK_WRITES_ENABLED:
        blockers.append(
            "network write lock is not active"
        )

    if REAL_ORDER_EXECUTION:
        blockers.append(
            "real order execution is enabled"
        )

    if DEMO_ORDER_EXECUTION:
        blockers.append(
            "demo order execution is enabled"
        )

    return blockers


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):
            self.send_response(404)
            self.end_headers()
            return

        payload = {
            "status": "ok",
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": phase,
            "authenticated_read_only":
                AUTHENTICATED_READ_ONLY,
            "authenticated_get_counter":
                authenticated_get_counter,
            "network_writes_enabled":
                NETWORK_WRITES_ENABLED,
            "network_write_counter":
                network_write_counter,
            "real_order_execution":
                REAL_ORDER_EXECUTION,
            "real_order_counter":
                real_order_counter,
            "demo_order_execution":
                DEMO_ORDER_EXECUTION,
            "demo_order_counter":
                demo_order_counter,
            "leverage_mutation_enabled":
                LEVERAGE_MUTATION_ENABLED,
            "leverage_mutation_counter":
                leverage_mutation_counter,
            "readiness_verified":
                readiness_verified,
            "readiness_blockers":
                readiness_blockers,
            "state":
                latest_state,
            "timestamp":
                utc_now(),
        }

        body = json.dumps(
            payload,
            default=str
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

    def log_message(
        self,
        format,
        *args
    ):
        return


def run_health_server():

    server = HTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler
    )

    server.serve_forever()


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================

def heartbeat_loop():

    global heartbeat_counter

    while True:

        time.sleep(30)

        heartbeat_counter += 1

        state = latest_state.copy()

        log()
        log(LINE)

        log(
            f"{VERSION}: HEARTBEAT "
            f"{heartbeat_counter} | "
            f"phase={phase} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get="
            f"{authenticated_get_counter} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION} | "
            f"network-writes="
            f"{NETWORK_WRITES_ENABLED} | "
            f"network-write-counter="
            f"{network_write_counter} | "
            f"real-orders="
            f"{real_order_counter} | "
            f"readiness-verified="
            f"{readiness_verified} | "
            f"balance="
            f"{state.get('available_balance', 'NA')} | "
            f"margin="
            f"{state.get('margin_mode', 'NA')} | "
            f"long="
            f"{state.get('long_leverage', 'NA')}x | "
            f"short="
            f"{state.get('short_leverage', 'NA')}x | "
            f"positions="
            f"{state.get('open_positions', 'NA')} | "
            f"mark-price="
            f"{state.get('mark_price', 'NA')} | "
            f"candidate-qty="
            f"{state.get('execution_candidate_qty', 'NA')} | "
            f"strategy-exposure="
            f"{state.get('theoretical_total_strategy_percent', 'NA')}%"
        )


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def main():

    global phase
    global readiness_verified
    global readiness_blockers
    global latest_state

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
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: DEMO ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )

    log(
        f"{VERSION}: TARGET MARGIN="
        f"{TARGET_MARGIN_MODE}"
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
        f"{VERSION}: INITIAL ENTRY="
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: HARD SAFETY CONFIGURATION"
    )

    assert_write_disabled()

    bool_line(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY
    )

    bool_line(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION
    )

    bool_line(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION
    )

    bool_line(
        "Exchange Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED
    )

    bool_line(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED
    )

    bool_line(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED
    )

    bool_line(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED
    )

    bool_line(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION_ENABLED
    )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: CREDENTIAL PRESENCE"
    )

    bool_line(
        "API Key Is Present",
        bool(API_KEY)
    )

    bool_line(
        "API Secret Is Present",
        bool(API_SECRET)
    )

    bool_line(
        "API Passphrase Is Present",
        bool(API_PASSPHRASE)
    )

    require_credentials()


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: AVAILABLE BALANCE READ-BACK"
    )

    (
        available_balance,
        balance_payload,
        balance_path,
    ) = fetch_balance()

    log(
        f"{VERSION}: BALANCE PATH="
        f"{balance_path}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{available_balance}"
    )

    bool_line(
        "Available Balance Was Read",
        available_balance >= 0
    )

    bool_line(
        "Available Balance Is Positive",
        available_balance > 0
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: POSITION RECONCILIATION"
    )

    (
        open_positions,
        position_payload,
        position_path,
    ) = fetch_positions()

    log(
        f"{VERSION}: POSITION PATH="
        f"{position_path}"
    )

    log(
        f"{VERSION}: OPEN POSITIONS="
        f"{open_positions}"
    )

    bool_line(
        "Open Position Count Was Read",
        open_positions >= 0
    )

    bool_line(
        "No Open Positions Exist",
        open_positions == 0
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: 100x CORRECTION RECONFIRMATION"
    )

    (
        symbol_config,
        config_payload,
        config_path,
    ) = fetch_symbol_config()

    margin_mode = symbol_config[
        "margin_mode"
    ]

    long_leverage = symbol_config[
        "long_leverage"
    ]

    short_leverage = symbol_config[
        "short_leverage"
    ]

    position_mode = symbol_config[
        "position_mode"
    ]

    log(
        f"{VERSION}: SYMBOL CONFIG PATH="
        f"{config_path}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_mode}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{long_leverage}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{short_leverage}x"
    )

    log(
        f"{VERSION}: POSITION MODE="
        f"{position_mode or 'UNKNOWN'}"
    )

    bool_line(
        "Margin Mode Is ISOLATED",
        margin_mode == TARGET_MARGIN_MODE
    )

    bool_line(
        "Long Leverage Is 100x",
        long_leverage
        == TARGET_LONG_LEVERAGE
    )

    bool_line(
        "Short Leverage Is 100x",
        short_leverage
        == TARGET_SHORT_LEVERAGE
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: CONTRACT CONSTRAINTS"
    )

    (
        constraints,
        contract_payload,
        contract_path,
    ) = fetch_contract_constraints()

    log(
        f"{VERSION}: CONTRACT PATH="
        f"{contract_path}"
    )

    log(
        f"{VERSION}: MIN QTY="
        f"{constraints['min_qty']}"
    )

    log(
        f"{VERSION}: QTY STEP="
        f"{constraints['qty_step']}"
    )

    log(
        f"{VERSION}: QTY PRECISION="
        f"{constraints['qty_precision']}"
    )

    log(
        f"{VERSION}: PRICE STEP="
        f"{constraints['price_step']}"
    )

    log(
        f"{VERSION}: PRICE PRECISION="
        f"{constraints['price_precision']}"
    )

    log(
        f"{VERSION}: MIN LEVERAGE="
        f"{constraints['min_leverage']}x"
    )

    log(
        f"{VERSION}: MAX LEVERAGE="
        f"{constraints['max_leverage']}x"
    )

    bool_line(
        "Quantity Step Is Positive",
        constraints["qty_step"] > 0
    )

    bool_line(
        "Target Leverage Meets Minimum",
        (
            constraints["min_leverage"] <= 0
            or TARGET_LONG_LEVERAGE
            >= constraints["min_leverage"]
        )
    )

    bool_line(
        "Target Leverage Does Not Exceed Maximum",
        (
            constraints["max_leverage"] <= 0
            or TARGET_LONG_LEVERAGE
            <= constraints["max_leverage"]
        )
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: PUBLIC MARK PRICE"
    )

    mark_price = obtain_mark_price()

    log(
        f"{VERSION}: MARK PRICE="
        f"{mark_price}"
    )

    bool_line(
        "Mark Price Is Positive",
        mark_price > 0
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: INITIAL ENTRY SIZING"
    )

    trade_plan = calculate_trade_plan(
        available_balance,
        mark_price,
        constraints,
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{trade_plan['entry_margin_budget']} USDT"
    )

    log(
        f"{VERSION}: PLANNED 100x NOTIONAL="
        f"{trade_plan['planned_notional']} USDT"
    )

    log(
        f"{VERSION}: RAW QTY="
        f"{trade_plan['raw_qty']} BTC"
    )

    log(
        f"{VERSION}: ROUNDED-DOWN QTY="
        f"{trade_plan['rounded_down_qty']} BTC"
    )

    log(
        f"{VERSION}: EXECUTION CANDIDATE QTY="
        f"{trade_plan['execution_candidate_qty']} BTC"
    )

    log(
        f"{VERSION}: EXECUTION CANDIDATE NOTIONAL="
        f"{trade_plan['execution_notional']} USDT"
    )

    log(
        f"{VERSION}: EXECUTION MARGIN AT 100x="
        f"{trade_plan['execution_margin_100x']} USDT"
    )

    log(
        f"{VERSION}: ACTUAL INITIAL MARGIN PERCENT="
        f"{trade_plan['actual_margin_percent']}%"
    )

    bool_line(
        "Initial Entry Margin Budget Is Positive",
        trade_plan[
            "entry_margin_budget"
        ] > 0
    )

    bool_line(
        "Candidate Quantity Is Positive",
        trade_plan[
            "execution_candidate_qty"
        ] > 0
    )

    bool_line(
        "Candidate Quantity Meets Minimum",
        (
            constraints["min_qty"] <= 0
            or trade_plan[
                "execution_candidate_qty"
            ] >= constraints["min_qty"]
        )
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: TOTAL STRATEGY EXPOSURE"
    )

    total_strategy_percent = (
        trade_plan[
            "theoretical_total_strategy_percent"
        ]
    )

    total_strategy_margin = (
        trade_plan[
            "theoretical_total_margin"
        ]
    )

    maximum_margin_budget = (
        trade_plan[
            "maximum_margin_budget"
        ]
    )

    log(
        f"{VERSION}: INITIAL ENTRY="
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    log(
        f"{VERSION}: PYRAMID COUNT="
        f"{MAX_PYRAMID_ADDS}"
    )

    log(
        f"{VERSION}: PYRAMID EACH="
        f"{PYRAMID_SIZE_PERCENT}%"
    )

    log(
        f"{VERSION}: BACKUP COUNT="
        f"{MAX_BACKUPS}"
    )

    log(
        f"{VERSION}: BACKUP EACH="
        f"{BACKUP_SIZE_PERCENT}%"
    )

    log(
        f"{VERSION}: THEORETICAL TOTAL="
        f"{total_strategy_percent}%"
    )

    log(
        f"{VERSION}: THEORETICAL TOTAL MARGIN="
        f"{total_strategy_margin} USDT"
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    log(
        f"{VERSION}: MAX MARGIN BUDGET="
        f"{maximum_margin_budget} USDT"
    )

    bool_line(
        "Total Strategy Exposure Is Within Maximum",
        total_strategy_percent
        <= MAX_FUND_EXPOSURE_PERCENT
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: TP DISTRIBUTION"
    )

    tp_total = (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
    )

    log(
        f"{VERSION}: TP1="
        f"{TP1_PERCENT}%"
    )

    log(
        f"{VERSION}: TP2="
        f"{TP2_PERCENT}%"
    )

    log(
        f"{VERSION}: TP3="
        f"{TP3_PERCENT}%"
    )

    log(
        f"{VERSION}: TP TOTAL="
        f"{tp_total}%"
    )

    log(
        f"{VERSION}: TP1 TRIGGER="
        f"{TP1_TRIGGER_PERCENT}%"
    )

    log(
        f"{VERSION}: TP2 TRIGGER="
        f"{TP2_TRIGGER_PERCENT}%"
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{TRAILING_DISTANCE_PERCENT}%"
    )

    bool_line(
        "TP Distribution Totals 100 Percent",
        tp_total == Decimal("100")
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: CONSOLIDATED READINESS STATE"
    )

    state = {
        "version": VERSION,
        "symbol": SYMBOL,

        "available_balance":
            available_balance,

        "margin_mode":
            margin_mode,

        "long_leverage":
            long_leverage,

        "short_leverage":
            short_leverage,

        "position_mode":
            position_mode,

        "open_positions":
            open_positions,

        "mark_price":
            mark_price,

        "min_qty":
            constraints["min_qty"],

        "qty_step":
            constraints["qty_step"],

        "qty_precision":
            constraints["qty_precision"],

        "price_step":
            constraints["price_step"],

        "price_precision":
            constraints["price_precision"],

        "min_leverage":
            constraints["min_leverage"],

        "max_leverage":
            constraints["max_leverage"],

        **trade_plan,
    }

    blockers = evaluate_readiness(
        state
    )

    readiness_blockers = blockers

    readiness_verified = (
        len(blockers) == 0
    )

    state["readiness_verified"] = (
        readiness_verified
    )

    state["readiness_blockers"] = (
        blockers
    )

    latest_state = {
        key: (
            str(value)
            if isinstance(value, Decimal)
            else value
        )
        for key, value in state.items()
    }

    state_hash = sha256_json(
        latest_state
    )

    log(
        f"{VERSION}: READINESS STATE SHA256="
        f"{state_hash}"
    )

    bool_line(
        "100x Long State Is Ready",
        long_leverage
        == TARGET_LONG_LEVERAGE
    )

    bool_line(
        "100x Short State Is Ready",
        short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    bool_line(
        "ISOLATED Margin State Is Ready",
        margin_mode
        == TARGET_MARGIN_MODE
    )

    bool_line(
        "No Position Conflict Exists",
        open_positions == 0
    )

    bool_line(
        "Sizing Is Valid",
        trade_plan[
            "execution_candidate_qty"
        ] > 0
    )

    bool_line(
        "Exposure Is Within Policy",
        total_strategy_percent
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    bool_line(
        "No Readiness Blockers Remain",
        len(blockers) == 0
    )

    if blockers:

        log()
        log(
            f"{VERSION}: READINESS BLOCKERS:"
        )

        for index, blocker in enumerate(
            blockers,
            start=1
        ):

            log(
                f"{VERSION}: BLOCKER "
                f"{index}: {blocker}"
            )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: TERMINAL SAFETY COUNTERS"
    )

    bool_line(
        "Network Writes Remain Zero",
        network_write_counter == 0
    )

    bool_line(
        "Leverage Mutations Remain Zero",
        leverage_mutation_counter == 0
    )

    bool_line(
        "Real Orders Remain Zero",
        real_order_counter == 0
    )

    bool_line(
        "Demo Orders Remain Zero",
        demo_order_counter == 0
    )

    bool_line(
        "Real Execution Remains Disabled",
        not REAL_ORDER_EXECUTION
    )

    bool_line(
        "Exchange Writes Remain Disabled",
        not NETWORK_WRITES_ENABLED
    )


    # ==============================================================================================
    # FINAL
    # ==============================================================================================

    if readiness_verified:
        phase = (
            "POST_CORRECTION_READINESS_VERIFIED"
        )

    else:
        phase = (
            "POST_CORRECTION_READINESS_BLOCKED"
        )

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        f"{VERSION}: PHASE={phase}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{authenticated_get_counter}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{available_balance}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_mode}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{long_leverage}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{short_leverage}x"
    )

    log(
        f"{VERSION}: OPEN POSITIONS="
        f"{open_positions}"
    )

    log(
        f"{VERSION}: MARK PRICE="
        f"{mark_price}"
    )

    log(
        f"{VERSION}: CANDIDATE QTY="
        f"{trade_plan['execution_candidate_qty']} BTC"
    )

    log(
        f"{VERSION}: INITIAL MARGIN="
        f"{trade_plan['execution_margin_100x']} USDT"
    )

    log(
        f"{VERSION}: STRATEGY EXPOSURE="
        f"{total_strategy_percent}%"
    )

    log(
        f"{VERSION}: MAX EXPOSURE="
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    log(
        f"{VERSION}: READINESS VERIFIED="
        f"{readiness_verified}"
    )

    log(
        f"{VERSION}: READINESS BLOCKERS="
        f"{len(blockers)}"
    )

    log(
        f"{VERSION}: STATE SHA256="
        f"{state_hash}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{network_write_counter}"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{leverage_mutation_counter}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{real_order_counter}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{demo_order_counter}"
    )

    if readiness_verified:

        log(
            f"{VERSION}: POST-CORRECTION "
            f"STRATEGY / ACCOUNT READINESS VERIFIED"
        )

    else:

        log(
            f"{VERSION}: POST-CORRECTION "
            f"READINESS IS BLOCKED"
        )

    log(
        f"{VERSION}: NO REAL ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO DEMO ORDER WAS SENT"
    )

    log(
        f"{VERSION}: NO EXCHANGE WRITE WAS SENT"
    )

    log(
        f"{VERSION}: NO LEVERAGE MUTATION "
        f"WAS PERFORMED"
    )

    section("")

    heartbeat_loop()


# ==================================================================================================
# STARTUP
# ==================================================================================================

if __name__ == "__main__":

    threading.Thread(
        target=run_health_server,
        daemon=True
    ).start()

    main()
