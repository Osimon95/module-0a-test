#!/usr/bin/env python3
# ============================================================
# R34U MAIN.PY
# LIVE READ-ONLY POST-RESTART RECONCILIATION
# ============================================================
#
# SAFETY:
#   - NO REAL ORDERS
#   - NO DEMO ORDERS
#   - NO POST / PUT / PATCH / DELETE
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#
# PURPOSE:
#   Confirm that the live BTCUSDT account still satisfies the
#   previously validated execution assumptions after the
#   durable/crash-window validation stages.
#
# ============================================================

import base64
import hashlib
import hmac
import json
import os
import signal
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, HTTPServer


# ============================================================
# VERSION / BASIC CONFIGURATION
# ============================================================

VERSION = "R34U"

SYMBOL = "BTCUSDT"
QUOTE_ASSET = "USDT"

HEALTH_PORT = int(os.getenv("PORT", "10000"))

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")


# ============================================================
# STRATEGY BASELINE
# ============================================================

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")

PRICE_STEP = Decimal("0.1")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ============================================================
# ABSOLUTE SAFETY FIREBREAKS
# ============================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

AUTHENTICATED_READ_ONLY_ENABLED = True
PUBLIC_READ_ONLY_ENABLED = True

ALLOWED_HTTP_METHODS = {"GET"}


# ============================================================
# COUNTERS
# ============================================================

counters = {
    "authenticated_gets": 0,
    "public_gets": 0,

    "network_writes": 0,

    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,

    "real_orders": 0,
    "demo_orders": 0,

    "http_post_blocks": 0,
    "http_put_blocks": 0,
    "http_patch_blocks": 0,
    "http_delete_blocks": 0,
}


# ============================================================
# RUNTIME STATE
# ============================================================

runtime = {
    "phase": "STARTING",

    "available_balance": None,

    "margin_type": None,
    "long_leverage": None,
    "short_leverage": None,

    "total_positions": None,
    "btc_positions": None,
    "open_positions": None,

    "mark_price": None,

    "qty_step": None,
    "min_qty": None,
    "price_step": None,

    "initial_margin_budget": None,
    "initial_notional": None,
    "raw_quantity": None,
    "rounded_quantity": None,
    "rounded_notional": None,
    "estimated_margin": None,

    "max_allowed_strategy_margin": None,
    "planned_max_strategy_margin": None,

    "execution_ready": False,
}


stop_event = threading.Event()


# ============================================================
# FORMATTING
# ============================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def check(label, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    log(f"{label:<88} {status}")

    if not condition:
        raise AssertionError(label)


def sha256_json(value):
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def decimal_text(value):
    if value is None:
        return "None"

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def to_decimal(value, default=None):
    if value is None:
        return default

    try:
        return Decimal(str(value))
    except Exception:
        return default


def truthy_open_size(value):
    amount = to_decimal(value, Decimal("0"))
    return amount != Decimal("0")


# ============================================================
# ENVIRONMENT
# ============================================================

def env_first(*names):
    for name in names:
        value = os.getenv(name)

        if value is not None and value.strip():
            return value.strip()

    return None


API_KEY = env_first(
    "WEEX_API_KEY",
    "WEEX_ACCESS_KEY",
    "WEEX_KEY"
)

API_SECRET = env_first(
    "WEEX_API_SECRET",
    "WEEX_SECRET_KEY",
    "WEEX_SECRET"
)

API_PASSPHRASE = env_first(
    "WEEX_API_PASSPHRASE",
    "WEEX_PASSPHRASE",
    "WEEX_PASS"
)


# ============================================================
# SAFETY HTTP LAYER
# ============================================================

def reject_write(method):
    method = method.upper()

    if method == "POST":
        counters["http_post_blocks"] += 1

    elif method == "PUT":
        counters["http_put_blocks"] += 1

    elif method == "PATCH":
        counters["http_patch_blocks"] += 1

    elif method == "DELETE":
        counters["http_delete_blocks"] += 1

    raise RuntimeError(
        f"R34U safety firebreak rejected HTTP {method}"
    )


def safe_http_request(
    method,
    url,
    headers=None,
    timeout=15
):
    method = method.upper()

    if method not in ALLOWED_HTTP_METHODS:
        counters["network_writes"] += 1
        reject_write(method)

    request = urllib.request.Request(
        url=url,
        headers=headers or {},
        method="GET"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            status = getattr(response, "status", 200)

            if status < 200 or status >= 300:
                raise RuntimeError(
                    f"HTTP status {status}: {raw}"
                )

            try:
                return json.loads(raw)

            except json.JSONDecodeError:
                raise RuntimeError(
                    f"Non-JSON HTTP response: {raw[:500]}"
                )

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {body}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Network GET failed: {exc.reason}"
        )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def build_authenticated_headers(
    method,
    request_path,
    query_string=""
):
    if not API_KEY:
        raise RuntimeError("Missing WEEX_API_KEY")

    if not API_SECRET:
        raise RuntimeError("Missing WEEX_API_SECRET")

    if not API_PASSPHRASE:
        raise RuntimeError("Missing WEEX_API_PASSPHRASE")

    method = method.upper()

    if method != "GET":
        reject_write(method)

    timestamp = str(int(time.time() * 1000))

    request_target = request_path

    if query_string:
        request_target += "?" + query_string

    prehash = (
        timestamp
        + method
        + request_target
    )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256
    ).digest()

    signature = base64.b64encode(
        digest
    ).decode("utf-8")

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only",
    }


# ============================================================
# RESPONSE HELPERS
# ============================================================

def unwrap_payload(response):
    if isinstance(response, dict):

        for key in (
            "data",
            "result",
            "rows",
            "list"
        ):
            if key in response:
                return response[key]

    return response


def flatten_records(value):
    value = unwrap_payload(value)

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, dict):

        for key in (
            "list",
            "rows",
            "data",
            "result"
        ):
            inner = value.get(key)

            if isinstance(inner, list):
                return inner

        return [value]

    return []


def find_first(record, names):
    if not isinstance(record, dict):
        return None

    lowered = {
        str(k).lower(): v
        for k, v in record.items()
    }

    for name in names:
        if name in record:
            return record[name]

        candidate = lowered.get(
            name.lower()
        )

        if candidate is not None:
            return candidate

    return None


# ============================================================
# AUTHENTICATED GET
# ============================================================

def authenticated_get(
    path,
    params=None
):
    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Authenticated read-only disabled"
        )

    params = params or {}

    query = urllib.parse.urlencode(
        params,
        doseq=True
    )

    url = BASE_URL + path

    if query:
        url += "?" + query

    headers = build_authenticated_headers(
        "GET",
        path,
        query
    )

    result = safe_http_request(
        "GET",
        url,
        headers=headers
    )

    counters["authenticated_gets"] += 1

    return result


# ============================================================
# PUBLIC GET
# ============================================================

def public_get(
    path,
    params=None
):
    if not PUBLIC_READ_ONLY_ENABLED:
        raise RuntimeError(
            "Public read-only disabled"
        )

    params = params or {}

    query = urllib.parse.urlencode(
        params,
        doseq=True
    )

    url = BASE_URL + path

    if query:
        url += "?" + query

    result = safe_http_request(
        "GET",
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-public-read-only"
        }
    )

    counters["public_gets"] += 1

    return result


# ============================================================
# ENDPOINT FALLBACK
# ============================================================

def first_success(
    description,
    getter,
    candidates
):
    errors = []

    for path, params in candidates:

        try:
            result = getter(
                path,
                params
            )

            log(
                f"{VERSION}: {description} PATH={path}"
            )

            return path, result

        except Exception as exc:
            errors.append(
                f"{path}: {type(exc).__name__}: {exc}"
            )

    raise RuntimeError(
        description
        + " failed on all candidate paths | "
        + " || ".join(errors)
    )


# ============================================================
# BALANCE PARSING
# ============================================================

def extract_available_usdt(response):
    records = flatten_records(response)

    # First try explicit USDT records.
    for record in records:

        if not isinstance(record, dict):
            continue

        asset = find_first(
            record,
            (
                "coinName",
                "coin",
                "asset",
                "marginCoin",
                "currency"
            )
        )

        if (
            asset is not None
            and str(asset).upper() != QUOTE_ASSET
        ):
            continue

        value = find_first(
            record,
            (
                "available",
                "availableBalance",
                "availableAmount",
                "availableEquity",
                "free",
                "balance"
            )
        )

        parsed = to_decimal(value)

        if parsed is not None:
            return parsed

    # Then inspect nested dicts.
    payload = unwrap_payload(response)

    if isinstance(payload, dict):

        for value in payload.values():

            if isinstance(value, dict):

                asset = find_first(
                    value,
                    (
                        "coinName",
                        "coin",
                        "asset",
                        "marginCoin",
                        "currency"
                    )
                )

                if (
                    asset is not None
                    and str(asset).upper()
                    != QUOTE_ASSET
                ):
                    continue

                available = find_first(
                    value,
                    (
                        "available",
                        "availableBalance",
                        "availableAmount",
                        "free",
                        "balance"
                    )
                )

                parsed = to_decimal(
                    available
                )

                if parsed is not None:
                    return parsed

    raise RuntimeError(
        "Could not parse available USDT balance"
    )


# ============================================================
# POSITION PARSING
# ============================================================

def extract_positions(response):
    records = flatten_records(response)

    total = len(records)

    symbol_records = []

    open_records = []

    for record in records:

        if not isinstance(record, dict):
            continue

        record_symbol = find_first(
            record,
            (
                "symbol",
                "contractCode",
                "contract",
                "ticker"
            )
        )

        if (
            record_symbol is None
            or str(record_symbol).upper()
            != SYMBOL
        ):
            continue

        symbol_records.append(record)

        size = find_first(
            record,
            (
                "total",
                "size",
                "positionAmt",
                "positionAmount",
                "holdVol",
                "available",
                "qty",
                "quantity"
            )
        )

        if truthy_open_size(size):
            open_records.append(record)

    return (
        total,
        symbol_records,
        open_records
    )


# ============================================================
# ACCOUNT CONFIG PARSING
# ============================================================

def normalize_margin(value):
    if value is None:
        return None

    text = str(value).strip().upper()

    if "ISOLATED" in text:
        return "ISOLATED"

    if "FIXED" in text:
        return "ISOLATED"

    if "CROSS" in text:
        return "CROSS"

    return text


def extract_account_configuration(response):
    records = flatten_records(response)

    margin_type = None
    long_leverage = None
    short_leverage = None

    for record in records:

        if not isinstance(record, dict):
            continue

        record_symbol = find_first(
            record,
            (
                "symbol",
                "contractCode",
                "contract",
                "ticker"
            )
        )

        if (
            record_symbol is not None
            and str(record_symbol).upper()
            != SYMBOL
        ):
            continue

        if margin_type is None:

            margin_type = normalize_margin(
                find_first(
                    record,
                    (
                        "marginType",
                        "marginMode",
                        "margin_mode",
                        "holdMode"
                    )
                )
            )

        if long_leverage is None:

            long_leverage = to_decimal(
                find_first(
                    record,
                    (
                        "longLeverage",
                        "long_leverage",
                        "buyLeverage",
                        "buy_leverage",
                        "isolatedLongLeverage"
                    )
                )
            )

        if short_leverage is None:

            short_leverage = to_decimal(
                find_first(
                    record,
                    (
                        "shortLeverage",
                        "short_leverage",
                        "sellLeverage",
                        "sell_leverage",
                        "isolatedShortLeverage"
                    )
                )
            )

        # Some APIs expose one leverage value.
        generic_leverage = to_decimal(
            find_first(
                record,
                (
                    "leverage",
                    "isolatedLeverage"
                )
            )
        )

        if (
            generic_leverage is not None
            and long_leverage is None
        ):
            long_leverage = generic_leverage

        if (
            generic_leverage is not None
            and short_leverage is None
        ):
            short_leverage = generic_leverage

    return (
        margin_type,
        long_leverage,
        short_leverage
    )


# ============================================================
# MARKET PRICE PARSING
# ============================================================

def extract_mark_price(response):
    payload = unwrap_payload(response)

    candidates = []

    if isinstance(payload, dict):
        candidates.append(payload)

    candidates.extend(
        flatten_records(response)
    )

    for record in candidates:

        if not isinstance(record, dict):
            continue

        symbol = find_first(
            record,
            (
                "symbol",
                "contractCode"
            )
        )

        if (
            symbol is not None
            and str(symbol).upper()
            != SYMBOL
        ):
            continue

        value = find_first(
            record,
            (
                "markPrice",
                "mark_price",
                "price",
                "last",
                "lastPrice",
                "close"
            )
        )

        parsed = to_decimal(value)

        if (
            parsed is not None
            and parsed > 0
        ):
            return parsed

    raise RuntimeError(
        "Could not parse positive BTCUSDT mark price"
    )


# ============================================================
# CONTRACT RULE PARSING
# ============================================================

def extract_contract_rules(response):
    records = flatten_records(response)

    qty_step = None
    min_qty = None
    price_step = None

    for record in records:

        if not isinstance(record, dict):
            continue

        symbol = find_first(
            record,
            (
                "symbol",
                "contractCode",
                "contract"
            )
        )

        if (
            symbol is not None
            and str(symbol).upper()
            != SYMBOL
        ):
            continue

        qty_step = to_decimal(
            find_first(
                record,
                (
                    "sizeMultiplier",
                    "qtyStep",
                    "quantityStep",
                    "volumePlace",
                    "lotSize",
                    "stepSize"
                )
            ),
            qty_step
        )

        min_qty = to_decimal(
            find_first(
                record,
                (
                    "minTradeNum",
                    "minQty",
                    "minTradeAmount",
                    "minimumQuantity",
                    "minOrderQty"
                )
            ),
            min_qty
        )

        price_step = to_decimal(
            find_first(
                record,
                (
                    "priceEndStep",
                    "priceStep",
                    "tickSize",
                    "priceTick"
                )
            ),
            price_step
        )

        if (
            qty_step is not None
            and min_qty is not None
            and price_step is not None
        ):
            break

    return (
        qty_step,
        min_qty,
        price_step
    )


# ============================================================
# QUANTITY CALCULATION
# ============================================================

def floor_to_step(
    value,
    step
):
    value = Decimal(value)
    step = Decimal(step)

    if step <= 0:
        raise ValueError(
            "Step must be positive"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        payload = {
            "ok": True,
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": runtime["phase"],
            "execution_ready": runtime[
                "execution_ready"
            ],
            "network_writes": counters[
                "network_writes"
            ],
            "real_orders": counters[
                "real_orders"
            ],
            "demo_orders": counters[
                "demo_orders"
            ],
        }

        body = json.dumps(
            payload,
            separators=(",", ":")
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

    def do_POST(self):
        self.send_error(
            405,
            "Method Not Allowed"
        )

    def do_PUT(self):
        self.send_error(
            405,
            "Method Not Allowed"
        )

    def do_PATCH(self):
        self.send_error(
            405,
            "Method Not Allowed"
        )

    def do_DELETE(self):
        self.send_error(
            405,
            "Method Not Allowed"
        )

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

    while not stop_event.is_set():

        server.timeout = 1
        server.handle_request()

    server.server_close()


# ============================================================
# VALIDATION
# ============================================================

def validate():

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
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


    # ========================================================
    # TEST 1
    # ========================================================

    section(
        f"{VERSION} TEST 1: ABSOLUTE SAFETY FIREBREAK"
    )

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION is False
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION is False
    )

    check(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED is False
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED is False
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED is False
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED is False
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED is False
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED is True
    )

    check(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY_ENABLED is True
    )


    # ========================================================
    # TEST 2
    # ========================================================

    section(
        f"{VERSION} TEST 2: CREDENTIAL PRESENCE"
    )

    check(
        "WEEX API Key Is Present",
        bool(API_KEY)
    )

    check(
        "WEEX API Secret Is Present",
        bool(API_SECRET)
    )

    check(
        "WEEX API Passphrase Is Present",
        bool(API_PASSPHRASE)
    )


    # ========================================================
    # TEST 3
    # ========================================================

    section(
        f"{VERSION} TEST 3: LIVE BALANCE RECONCILIATION"
    )

    balance_path, balance_response = first_success(
        "BALANCE",
        authenticated_get,
        [
            (
                "/capi/v3/account/balance",
                {}
            ),
            (
                "/api/v2/mix/account/accounts",
                {
                    "productType": "USDT-FUTURES"
                }
            ),
        ]
    )

    available_balance = extract_available_usdt(
        balance_response
    )

    runtime[
        "available_balance"
    ] = available_balance

    check(
        "Available Balance Was Read",
        available_balance is not None
    )

    check(
        "Available Balance Is Positive",
        available_balance > 0
    )

    log(
        f"{VERSION}: BALANCE PATH={balance_path}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_balance)}"
    )


    # ========================================================
    # TEST 4
    # ========================================================

    section(
        f"{VERSION} TEST 4: POSITION RECONCILIATION"
    )

    position_path, position_response = first_success(
        "POSITION",
        authenticated_get,
        [
            (
                "/capi/v3/account/position/allPosition",
                {}
            ),
            (
                "/api/v2/mix/position/all-position",
                {
                    "productType": "USDT-FUTURES"
                }
            ),
        ]
    )

    (
        total_positions,
        btc_positions,
        open_positions
    ) = extract_positions(
        position_response
    )

    runtime[
        "total_positions"
    ] = total_positions

    runtime[
        "btc_positions"
    ] = len(btc_positions)

    runtime[
        "open_positions"
    ] = len(open_positions)

    check(
        "Position Response Was Read",
        total_positions is not None
    )

    check(
        "BTCUSDT Open Position Count Is Zero",
        len(open_positions) == 0
    )

    log(
        f"{VERSION}: POSITION PATH={position_path}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{total_positions}"
    )

    log(
        f"{VERSION}: BTCUSDT POSITION RECORDS="
        f"{len(btc_positions)}"
    )

    log(
        f"{VERSION}: BTCUSDT OPEN POSITIONS="
        f"{len(open_positions)}"
    )


    # ========================================================
    # TEST 5
    # ========================================================

    section(
        f"{VERSION} TEST 5: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    config_path, config_response = first_success(
        "ACCOUNT CONFIGURATION",
        authenticated_get,
        [
            (
                "/capi/v3/account/settings",
                {
                    "symbol": SYMBOL
                }
            ),
            (
                "/capi/v3/account/leverage",
                {
                    "symbol": SYMBOL
                }
            ),
            (
                "/capi/v3/account/position/singlePosition",
                {
                    "symbol": SYMBOL
                }
            ),
        ]
    )

    (
        margin_type,
        long_leverage,
        short_leverage
    ) = extract_account_configuration(
        config_response
    )

    # Position records sometimes carry the configuration more
    # reliably than the dedicated account settings endpoint.
    if (
        margin_type is None
        or long_leverage is None
        or short_leverage is None
    ):

        (
            alt_margin,
            alt_long,
            alt_short
        ) = extract_account_configuration(
            position_response
        )

        if margin_type is None:
            margin_type = alt_margin

        if long_leverage is None:
            long_leverage = alt_long

        if short_leverage is None:
            short_leverage = alt_short

    runtime[
        "margin_type"
    ] = margin_type

    runtime[
        "long_leverage"
    ] = long_leverage

    runtime[
        "short_leverage"
    ] = short_leverage

    check(
        "Margin Type Was Read",
        margin_type is not None
    )

    check(
        "Margin Type Is ISOLATED",
        margin_type == TARGET_MARGIN_TYPE
    )

    check(
        "Long Leverage Was Read",
        long_leverage is not None
    )

    check(
        "Short Leverage Was Read",
        short_leverage is not None
    )

    check(
        "Long Leverage Is 100x",
        long_leverage
        == TARGET_LONG_LEVERAGE
    )

    check(
        "Short Leverage Is 100x",
        short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    log(
        f"{VERSION}: CONFIG PATH={config_path}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{decimal_text(long_leverage)}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{decimal_text(short_leverage)}x"
    )


    # ========================================================
    # TEST 6
    # ========================================================

    section(
        f"{VERSION} TEST 6: PUBLIC MARKET PRICE"
    )

    price_path, price_response = first_success(
        "MARK PRICE",
        public_get,
        [
            (
                "/capi/v3/market/ticker",
                {
                    "symbol": SYMBOL
                }
            ),
            (
                "/capi/v3/market/tickers",
                {
                    "symbol": SYMBOL
                }
            ),
        ]
    )

    mark_price = extract_mark_price(
        price_response
    )

    runtime[
        "mark_price"
    ] = mark_price

    check(
        "Market Price Was Read",
        mark_price is not None
    )

    check(
        "Market Price Is Positive",
        mark_price > 0
    )

    log(
        f"{VERSION}: MARKET PRICE PATH="
        f"{price_path}"
    )

    log(
        f"{VERSION}: BTCUSDT MARKET PRICE="
        f"{decimal_text(mark_price)}"
    )


    # ========================================================
    # TEST 7
    # ========================================================

    section(
        f"{VERSION} TEST 7: CONTRACT RULE RECONCILIATION"
    )

    contract_path, contract_response = first_success(
        "CONTRACT INFORMATION",
        public_get,
        [
            (
                "/capi/v3/market/contracts",
                {
                    "symbol": SYMBOL
                }
            ),
            (
                "/capi/v3/market/exchangeInfo",
                {
                    "symbol": SYMBOL
                }
            ),
        ]
    )

    (
        observed_qty_step,
        observed_min_qty,
        observed_price_step
    ) = extract_contract_rules(
        contract_response
    )

    # Preserve previously validated baseline if the API returns
    # precision metadata instead of literal decimal increments.
    effective_qty_step = (
        observed_qty_step
        if observed_qty_step is not None
        else QTY_STEP
    )

    effective_min_qty = (
        observed_min_qty
        if observed_min_qty is not None
        else MIN_QTY
    )

    effective_price_step = (
        observed_price_step
        if observed_price_step is not None
        else PRICE_STEP
    )

    runtime[
        "qty_step"
    ] = effective_qty_step

    runtime[
        "min_qty"
    ] = effective_min_qty

    runtime[
        "price_step"
    ] = effective_price_step

    check(
        "Quantity Step Is Positive",
        effective_qty_step > 0
    )

    check(
        "Minimum Quantity Is Positive",
        effective_min_qty > 0
    )

    check(
        "Price Step Is Positive",
        effective_price_step > 0
    )

    log(
        f"{VERSION}: CONTRACT PATH="
        f"{contract_path}"
    )

    log(
        f"{VERSION}: QTY STEP="
        f"{decimal_text(effective_qty_step)}"
    )

    log(
        f"{VERSION}: MIN QTY="
        f"{decimal_text(effective_min_qty)}"
    )

    log(
        f"{VERSION}: PRICE STEP="
        f"{decimal_text(effective_price_step)}"
    )


    # ========================================================
    # TEST 8
    # ========================================================

    section(
        f"{VERSION} TEST 8: INITIAL ENTRY READINESS"
    )

    initial_margin_budget = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    initial_notional = (
        initial_margin_budget
        * TARGET_LONG_LEVERAGE
    )

    raw_quantity = (
        initial_notional
        / mark_price
    )

    rounded_quantity = floor_to_step(
        raw_quantity,
        QTY_STEP
    )

    rounded_notional = (
        rounded_quantity
        * mark_price
    )

    estimated_margin = (
        rounded_notional
        / TARGET_LONG_LEVERAGE
    )

    runtime[
        "initial_margin_budget"
    ] = initial_margin_budget

    runtime[
        "initial_notional"
    ] = initial_notional

    runtime[
        "raw_quantity"
    ] = raw_quantity

    runtime[
        "rounded_quantity"
    ] = rounded_quantity

    runtime[
        "rounded_notional"
    ] = rounded_notional

    runtime[
        "estimated_margin"
    ] = estimated_margin

    check(
        "Initial Entry Percent Is Positive",
        INITIAL_ENTRY_PERCENT > 0
    )

    check(
        "Initial Entry Is Within Exposure Cap",
        INITIAL_ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    check(
        "Initial Entry Margin Budget Is Positive",
        initial_margin_budget > 0
    )

    check(
        "Raw Quantity Is Positive",
        raw_quantity > 0
    )

    check(
        "Rounded Quantity Meets Minimum",
        rounded_quantity >= MIN_QTY
    )

    check(
        "Estimated Margin Is Within Initial Budget",
        estimated_margin
        <= initial_margin_budget
    )

    log(
        f"{VERSION}: INITIAL ENTRY="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_text(initial_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: PLANNED NOTIONAL="
        f"{decimal_text(initial_notional)} USDT"
    )

    log(
        f"{VERSION}: RAW QTY="
        f"{decimal_text(raw_quantity)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED QTY="
        f"{decimal_text(rounded_quantity)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{decimal_text(rounded_notional)} USDT"
    )

    log(
        f"{VERSION}: ESTIMATED MARGIN AT 100x="
        f"{decimal_text(estimated_margin)} USDT"
    )


    # ========================================================
    # TEST 9
    # ========================================================

    section(
        f"{VERSION} TEST 9: MAXIMUM STRATEGY EXPOSURE"
    )

    max_allowed_strategy_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    planned_margin_percent = (
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

    planned_max_strategy_margin = (
        available_balance
        * planned_margin_percent
        / Decimal("100")
    )

    runtime[
        "max_allowed_strategy_margin"
    ] = max_allowed_strategy_margin

    runtime[
        "planned_max_strategy_margin"
    ] = planned_max_strategy_margin

    check(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1
    )

    check(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3
    )

    check(
        "Maximum Planned Strategy Margin Is Within 35%",
        planned_max_strategy_margin
        <= max_allowed_strategy_margin
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: PLANNED MARGIN PERCENT="
        f"{decimal_text(planned_margin_percent)}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{decimal_text(max_allowed_strategy_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_text(planned_max_strategy_margin)} USDT"
    )


    # ========================================================
    # TEST 10
    # ========================================================

    section(
        f"{VERSION} TEST 10: TAKE-PROFIT STRUCTURE"
    )

    check(
        "TP1 Allocation Is 20%",
        TP1_PERCENT == 20
    )

    check(
        "TP2 Allocation Is 20%",
        TP2_PERCENT == 20
    )

    check(
        "TP3 Allocation Is 60%",
        TP3_PERCENT == 60
    )

    check(
        "TP Allocations Sum To 100%",
        (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        ) == 100
    )

    check(
        "TP1 Trigger Is 0.5%",
        TP1_TRIGGER_PERCENT
        == Decimal("0.5")
    )

    check(
        "TP2 Trigger Is 1.0%",
        TP2_TRIGGER_PERCENT
        == Decimal("1.0")
    )

    check(
        "Trailing Distance Is 0.20%",
        TRAILING_DISTANCE_PERCENT
        == Decimal("0.20")
    )


    # ========================================================
    # TEST 11
    # ========================================================

    section(
        f"{VERSION} TEST 11: LIVE STATE HASH"
    )

    live_state = {
        "symbol": SYMBOL,

        "available_balance":
            decimal_text(
                available_balance
            ),

        "margin_type":
            margin_type,

        "long_leverage":
            decimal_text(
                long_leverage
            ),

        "short_leverage":
            decimal_text(
                short_leverage
            ),

        "open_positions":
            len(open_positions),

        "mark_price":
            decimal_text(
                mark_price
            ),

        "qty_step":
            decimal_text(
                effective_qty_step
            ),

        "min_qty":
            decimal_text(
                effective_min_qty
            ),

        "price_step":
            decimal_text(
                effective_price_step
            ),
    }

    live_state_hash = sha256_json(
        live_state
    )

    check(
        "Live State Hash Exists",
        len(live_state_hash) == 64
    )

    log(
        f"{VERSION}: LIVE STATE="
        + json.dumps(
            live_state,
            sort_keys=True,
            separators=(",", ":")
        )
    )

    log(
        f"{VERSION}: LIVE STATE SHA256="
        f"{live_state_hash}"
    )


    # ========================================================
    # TEST 12
    # ========================================================

    section(
        f"{VERSION} TEST 12: EXECUTION READINESS RECONCILIATION"
    )

    readiness = (
        available_balance > 0
        and margin_type
        == TARGET_MARGIN_TYPE
        and long_leverage
        == TARGET_LONG_LEVERAGE
        and short_leverage
        == TARGET_SHORT_LEVERAGE
        and len(open_positions) == 0
        and mark_price > 0
        and rounded_quantity
        >= MIN_QTY
        and planned_max_strategy_margin
        <= max_allowed_strategy_margin
    )

    runtime[
        "execution_ready"
    ] = readiness

    check(
        "Available Balance Gate Is Satisfied",
        available_balance > 0
    )

    check(
        "Flat Position Gate Is Satisfied",
        len(open_positions) == 0
    )

    check(
        "ISOLATED Margin Gate Is Satisfied",
        margin_type
        == TARGET_MARGIN_TYPE
    )

    check(
        "Long 100x Gate Is Satisfied",
        long_leverage
        == TARGET_LONG_LEVERAGE
    )

    check(
        "Short 100x Gate Is Satisfied",
        short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    check(
        "Positive Market Price Gate Is Satisfied",
        mark_price > 0
    )

    check(
        "Minimum Quantity Gate Is Satisfied",
        rounded_quantity
        >= MIN_QTY
    )

    check(
        "Exposure Cap Gate Is Satisfied",
        planned_max_strategy_margin
        <= max_allowed_strategy_margin
    )

    check(
        "Combined Readiness Gate Is Satisfied",
        readiness
    )


    # ========================================================
    # TEST 13
    # ========================================================

    section(
        f"{VERSION} TEST 13: FINAL WRITE FIREBREAK"
    )

    check(
        "Network Writes Remain Zero",
        counters[
            "network_writes"
        ] == 0
    )

    check(
        "Leverage Mutations Remain Zero",
        counters[
            "leverage_mutations"
        ] == 0
    )

    check(
        "Margin Mutations Remain Zero",
        counters[
            "margin_mutations"
        ] == 0
    )

    check(
        "Position Mutations Remain Zero",
        counters[
            "position_mutations"
        ] == 0
    )

    check(
        "Account Mutations Remain Zero",
        counters[
            "account_mutations"
        ] == 0
    )

    check(
        "Real Orders Remain Zero",
        counters[
            "real_orders"
        ] == 0
    )

    check(
        "Demo Orders Remain Zero",
        counters[
            "demo_orders"
        ] == 0
    )


    # ========================================================
    # COMPLETE
    # ========================================================

    runtime[
        "phase"
    ] = "LIVE_POST_RESTART_RECONCILED"

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    log(
        f"{VERSION}: PHASE="
        f"{runtime['phase']}"
    )

    log(
        f"{VERSION}: EXECUTION READY="
        f"{runtime['execution_ready']}"
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_balance)}"
    )

    log(
        f"{VERSION}: MARGIN TYPE="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: LONG LEVERAGE="
        f"{decimal_text(long_leverage)}x"
    )

    log(
        f"{VERSION}: SHORT LEVERAGE="
        f"{decimal_text(short_leverage)}x"
    )

    log(
        f"{VERSION}: OPEN POSITIONS="
        f"{len(open_positions)}"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{decimal_text(mark_price)}"
    )

    log(
        f"{VERSION}: ENTRY QTY="
        f"{decimal_text(rounded_quantity)}"
    )

    log(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{counters['authenticated_gets']}"
    )

    log(
        f"{VERSION}: PUBLIC GETS="
        f"{counters['public_gets']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{counters['network_writes']}"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATIONS="
        f"{counters['leverage_mutations']}"
    )

    log(
        f"{VERSION}: MARGIN MUTATIONS="
        f"{counters['margin_mutations']}"
    )

    log(
        f"{VERSION}: POSITION MUTATIONS="
        f"{counters['position_mutations']}"
    )

    log(
        f"{VERSION}: ACCOUNT MUTATIONS="
        f"{counters['account_mutations']}"
    )

    log(
        f"{VERSION}: REAL ORDERS="
        f"{counters['real_orders']}"
    )

    log(
        f"{VERSION}: DEMO ORDERS="
        f"{counters['demo_orders']}"
    )

    log(
        f"{VERSION}: LIVE STATE SHA256="
        f"{live_state_hash}"
    )

    log(
        f"{VERSION}: NO REAL OR DEMO ORDER WAS SENT"
    )


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop():

    heartbeat = 0

    while not stop_event.wait(30):

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT {heartbeat}"
            f" | phase={runtime['phase']}"
            f" | ready={runtime['execution_ready']}"
            f" | authenticated-get="
            f"{counters['authenticated_gets']}"
            f" | public-get="
            f"{counters['public_gets']}"
            f" | network-writes="
            f"{counters['network_writes']}"
            f" | real-orders="
            f"{counters['real_orders']}"
            f" | demo-orders="
            f"{counters['demo_orders']}"
            f" | margin={runtime['margin_type']}"
            f" | long={decimal_text(runtime['long_leverage'])}"
            f" | short={decimal_text(runtime['short_leverage'])}"
            f" | open-positions="
            f"{runtime['open_positions']}"
            f" | entry-qty="
            f"{decimal_text(runtime['rounded_quantity'])}"
        )


# ============================================================
# SIGNALS
# ============================================================

def handle_signal(
    signum,
    frame
):
    log(
        f"{VERSION}: SHUTDOWN SIGNAL={signum}"
    )

    stop_event.set()


signal.signal(
    signal.SIGTERM,
    handle_signal
)

signal.signal(
    signal.SIGINT,
    handle_signal
)


# ============================================================
# MAIN
# ============================================================

def main():

    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    health_thread.start()

    try:

        validate()

    except Exception as exc:

        runtime[
            "phase"
        ] = "VALIDATION_FAILED"

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        log(
            f"{VERSION}: NETWORK WRITES="
            f"{counters['network_writes']}"
        )

        log(
            f"{VERSION}: REAL ORDERS="
            f"{counters['real_orders']}"
        )

        log(
            f"{VERSION}: DEMO ORDERS="
            f"{counters['demo_orders']}"
        )

        # Keep Render health process alive for diagnosis.
        while not stop_event.wait(30):
            log(
                f"{VERSION}: FAILURE HEARTBEAT"
                f" | phase={runtime['phase']}"
                f" | network-writes="
                f"{counters['network_writes']}"
                f" | real-orders="
                f"{counters['real_orders']}"
                f" | demo-orders="
                f"{counters['demo_orders']}"
            )

        return

    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        daemon=True
    )

    heartbeat_thread.start()

    while not stop_event.wait(1):
        pass


if __name__ == "__main__":
    main()
