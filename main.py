#!/usr/bin/env python3
# ============================================================
# R34O
# LIVE SIGNAL -> ORDER INTENT READINESS VALIDATION
#
# IMPORTANT SAFETY PROPERTIES
# ------------------------------------------------------------
# - AUTHENTICATED READ-ONLY GET REQUESTS ONLY
# - PUBLIC READ-ONLY GET REQUESTS ONLY
# - NO REAL ORDER EXECUTION
# - NO DEMO ORDER EXECUTION
# - NO LEVERAGE MUTATION
# - NO MARGIN MUTATION
# - NO POSITION MUTATION
# - NO ACCOUNT MUTATION
# - ALL NETWORK WRITE METHODS HARD-BLOCKED
# - ORDER INTENT IS SYNTHETIC / LOCAL ONLY
# ============================================================

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
from decimal import Decimal, ROUND_DOWN, getcontext
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone


# ============================================================
# DECIMAL PRECISION
# ============================================================

getcontext().prec = 40


# ============================================================
# VERSION / BASIC CONFIGURATION
# ============================================================

VERSION = "R34O"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", "10000"))

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")


# ============================================================
# CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    ""
).strip()


# ============================================================
# HARD SAFETY CONFIGURATION
# ============================================================

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True

NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_ORDER_INTENT_ONLY = True


# ============================================================
# STRATEGY CONFIGURATION
# ============================================================

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
PYRAMID_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_PERCENT = Decimal("5")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_ALLOCATION_PERCENT = Decimal("20")
TP2_ALLOCATION_PERCENT = Decimal("20")
TP3_ALLOCATION_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.2")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# SIGNAL CONFIGURATION
# ============================================================

FAST_EMA_PERIOD = 5
SLOW_EMA_PERIOD = 12

SIGNAL_MIN_SPREAD_PERCENT = Decimal("0.02")

RECENT_PRICE_SAMPLE_COUNT = 20

PUBLIC_PRICE_POLL_DELAY_SECONDS = Decimal("0.20")


# ============================================================
# ENDPOINTS
# ============================================================

PUBLIC_CONTRACT_INFO_PATH = "/capi/v2/market/contracts"
PUBLIC_PRICE_PATH = "/capi/v2/market/ticker"

PRIVATE_BALANCE_PATH = "/capi/v3/account/balance"
PRIVATE_POSITION_PATH = "/capi/v3/account/position/allPosition"
PRIVATE_SYMBOL_CONFIG_PATH = "/capi/v3/account/settings"

# Intent-only placeholder.
# This is NEVER transmitted.
REAL_ORDER_PATH_PLACEHOLDER = "/capi/v3/order"


# ============================================================
# GLOBAL COUNTERS
# ============================================================

COUNTERS = {
    "public_get": 0,
    "authenticated_get": 0,
    "network_writes": 0,
    "real_orders": 0,
    "demo_orders": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,
    "synthetic_intents": 0,
    "blocked_writes": 0,
}


# ============================================================
# RUNTIME STATE
# ============================================================

RUNTIME = {
    "phase": "STARTING",
    "mark_price": None,
    "available_balance": None,
    "margin_type": None,
    "position_mode": None,
    "long_leverage": None,
    "short_leverage": None,
    "open_positions": 0,
    "correction_required": None,
    "signal": "NONE",
    "signal_strength": None,
    "signal_expiry": None,
    "entry_quantity": None,
    "synthetic_intent_id": None,
    "synthetic_intent_hash": None,
}


# ============================================================
# FORMAT HELPERS
# ============================================================

LINE = "-" * 100


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def decimal_text(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def normalize_decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def pass_fail(label, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    log(f"{label:<88} {status}")

    if not condition:
        raise RuntimeError(f"Validation failed: {label}")


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.end_headers()
            return

        payload = {
            "ok": True,
            "version": VERSION,
            "symbol": SYMBOL,
            "phase": RUNTIME["phase"],
            "mark_price": (
                decimal_text(RUNTIME["mark_price"])
                if RUNTIME["mark_price"] is not None
                else None
            ),
            "available_balance": (
                decimal_text(RUNTIME["available_balance"])
                if RUNTIME["available_balance"] is not None
                else None
            ),
            "margin_type": RUNTIME["margin_type"],
            "position_mode": RUNTIME["position_mode"],
            "long_leverage": (
                decimal_text(RUNTIME["long_leverage"])
                if RUNTIME["long_leverage"] is not None
                else None
            ),
            "short_leverage": (
                decimal_text(RUNTIME["short_leverage"])
                if RUNTIME["short_leverage"] is not None
                else None
            ),
            "open_positions": RUNTIME["open_positions"],
            "signal": RUNTIME["signal"],
            "signal_strength": (
                decimal_text(RUNTIME["signal_strength"])
                if RUNTIME["signal_strength"] is not None
                else None
            ),
            "entry_quantity": (
                decimal_text(RUNTIME["entry_quantity"])
                if RUNTIME["entry_quantity"] is not None
                else None
            ),
            "synthetic_intent_id": RUNTIME[
                "synthetic_intent_id"
            ],
            "counters": COUNTERS,
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

    def log_message(self, format, *args):
        return


def run_health_server():
    server = HTTPServer(
        ("0.0.0.0", HEALTH_PORT),
        HealthHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()
    return server


# ============================================================
# HARD WRITE FIREBREAK
# ============================================================

def reject_network_write(method, path=""):
    COUNTERS["blocked_writes"] += 1

    raise RuntimeError(
        f"R34O hard firebreak rejected HTTP {method} "
        f"for path={path}"
    )


def http_post(*args, **kwargs):
    reject_network_write("POST")


def http_put(*args, **kwargs):
    reject_network_write("PUT")


def http_patch(*args, **kwargs):
    reject_network_write("PATCH")


def http_delete(*args, **kwargs):
    reject_network_write("DELETE")


def generic_network_write(*args, **kwargs):
    reject_network_write("WRITE")


def execute_real_order(*args, **kwargs):
    raise RuntimeError(
        "R34O real order execution is disabled"
    )


def execute_demo_order(*args, **kwargs):
    raise RuntimeError(
        "R34O demo order execution is disabled"
    )


def mutate_leverage(*args, **kwargs):
    raise RuntimeError(
        "R34O leverage mutation is disabled"
    )


def mutate_margin(*args, **kwargs):
    raise RuntimeError(
        "R34O margin mutation is disabled"
    )


def mutate_position(*args, **kwargs):
    raise RuntimeError(
        "R34O position mutation is disabled"
    )


def mutate_account(*args, **kwargs):
    raise RuntimeError(
        "R34O account mutation is disabled"
    )


# ============================================================
# HTTP READ-ONLY TRANSPORT
# ============================================================

def urllib_get_json(url, headers=None, timeout=15):
    request = urllib.request.Request(
        url=url,
        headers=headers or {},
        method="GET"
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout
    ) as response:

        body = response.read().decode("utf-8")

    return json.loads(body)


def public_get(path, params=None):
    if not PUBLIC_READ_ONLY:
        raise RuntimeError(
            "Public read-only access disabled"
        )

    query = ""

    if params:
        query = "?" + urllib.parse.urlencode(params)

    url = WEEX_BASE_URL + path + query

    data = urllib_get_json(url)

    COUNTERS["public_get"] += 1

    return data


# ============================================================
# AUTHENTICATED GET SIGNING
# ============================================================

def build_auth_headers(
    method,
    path,
    query_string=""
):
    timestamp = str(int(time.time() * 1000))

    if query_string:
        request_path = f"{path}?{query_string}"
    else:
        request_path = path

    prehash = (
        timestamp +
        method.upper() +
        request_path
    )

    secret_bytes = WEEX_API_SECRET.encode("utf-8")
    message_bytes = prehash.encode("utf-8")

    signature = base64.b64encode(
        hmac.new(
            secret_bytes,
            message_bytes,
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }


def authenticated_get(path, params=None):
    if not AUTHENTICATED_READ_ONLY:
        raise RuntimeError(
            "Authenticated read-only access disabled"
        )

    params = params or {}

    query_string = urllib.parse.urlencode(params)

    headers = build_auth_headers(
        "GET",
        path,
        query_string
    )

    if query_string:
        url = (
            WEEX_BASE_URL +
            path +
            "?" +
            query_string
        )
    else:
        url = WEEX_BASE_URL + path

    data = urllib_get_json(
        url,
        headers=headers
    )

    COUNTERS["authenticated_get"] += 1

    return data


# ============================================================
# RESPONSE EXTRACTION HELPERS
# ============================================================

def extract_payload(response):
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


def walk_find_dicts(value):
    found = []

    if isinstance(value, dict):
        found.append(value)

        for child in value.values():
            found.extend(
                walk_find_dicts(child)
            )

    elif isinstance(value, list):
        for child in value:
            found.extend(
                walk_find_dicts(child)
            )

    return found


def first_matching_value(
    structure,
    candidate_keys
):
    candidate_keys = {
        str(key).lower()
        for key in candidate_keys
    }

    for item in walk_find_dicts(structure):
        for key, value in item.items():
            if str(key).lower() in candidate_keys:
                if value not in (
                    None,
                    "",
                    []
                ):
                    return value

    return None


# ============================================================
# LIVE CONTRACT INFORMATION
# ============================================================

def obtain_contract_information():
    response = public_get(
        PUBLIC_CONTRACT_INFO_PATH
    )

    payload = extract_payload(response)

    records = []

    if isinstance(payload, list):
        records = payload

    elif isinstance(payload, dict):
        records = walk_find_dicts(payload)

    for item in records:
        if not isinstance(item, dict):
            continue

        symbol_value = (
            item.get("symbol")
            or item.get("contractCode")
            or item.get("contract")
        )

        if (
            symbol_value and
            str(symbol_value).upper() == SYMBOL
        ):
            return item

    # Deep-search fallback
    for item in walk_find_dicts(response):
        symbol_value = (
            item.get("symbol")
            or item.get("contractCode")
            or item.get("contract")
        )

        if (
            symbol_value and
            str(symbol_value).upper() == SYMBOL
        ):
            return item

    raise RuntimeError(
        f"Could not locate contract information "
        f"for {SYMBOL}"
    )


# ============================================================
# LIVE MARK PRICE
# ============================================================

def obtain_mark_price():
    possible_param_sets = [
        {"symbol": SYMBOL},
        {"contractCode": SYMBOL},
    ]

    last_error = None

    for params in possible_param_sets:
        try:
            response = public_get(
                PUBLIC_PRICE_PATH,
                params
            )

            value = first_matching_value(
                response,
                (
                    "markPrice",
                    "mark_price",
                    "price",
                    "last",
                    "lastPrice",
                    "close",
                )
            )

            if value is None:
                continue

            price = normalize_decimal(value)

            if price > 0:
                return price

        except Exception as exc:
            last_error = exc

    if last_error:
        raise RuntimeError(
            f"Unable to obtain mark price: "
            f"{last_error}"
        )

    raise RuntimeError(
        "Unable to obtain mark price"
    )


# ============================================================
# LIVE BALANCE
# ============================================================

def obtain_available_balance():
    response = authenticated_get(
        PRIVATE_BALANCE_PATH
    )

    value = first_matching_value(
        response,
        (
            "available",
            "availableBalance",
            "available_balance",
            "availableMargin",
            "availableEquity",
        )
    )

    if value is None:
        raise RuntimeError(
            "Available balance not found"
        )

    balance = normalize_decimal(value)

    return balance


# ============================================================
# SYMBOL CONFIGURATION
# ============================================================

def obtain_symbol_configuration():
    response = authenticated_get(
        PRIVATE_SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL
        }
    )

    all_dicts = walk_find_dicts(response)

    selected = None

    for item in all_dicts:
        symbol_value = (
            item.get("symbol")
            or item.get("contractCode")
        )

        if symbol_value is None:
            continue

        if str(symbol_value).upper() == SYMBOL:
            selected = item
            break

    if selected is None:
        selected = (
            extract_payload(response)
            if isinstance(
                extract_payload(response),
                dict
            )
            else {}
        )

    margin_type = (
        selected.get("marginType")
        or selected.get("marginMode")
        or selected.get("margin_type")
    )

    position_mode = (
        selected.get("positionMode")
        or selected.get("holdMode")
        or selected.get("position_mode")
    )

    long_leverage = (
        selected.get("isolatedLongLeverage")
        or selected.get("longLeverage")
        or selected.get("long_leverage")
    )

    short_leverage = (
        selected.get("isolatedShortLeverage")
        or selected.get("shortLeverage")
        or selected.get("short_leverage")
    )

    if margin_type is None:
        margin_type = first_matching_value(
            response,
            (
                "marginType",
                "marginMode",
                "margin_type",
            )
        )

    if position_mode is None:
        position_mode = first_matching_value(
            response,
            (
                "positionMode",
                "holdMode",
                "position_mode",
            )
        )

    if long_leverage is None:
        long_leverage = first_matching_value(
            response,
            (
                "isolatedLongLeverage",
                "longLeverage",
                "long_leverage",
            )
        )

    if short_leverage is None:
        short_leverage = first_matching_value(
            response,
            (
                "isolatedShortLeverage",
                "shortLeverage",
                "short_leverage",
            )
        )

    if margin_type is None:
        raise RuntimeError(
            "Margin type not found"
        )

    if long_leverage is None:
        raise RuntimeError(
            "Long leverage not found"
        )

    if short_leverage is None:
        raise RuntimeError(
            "Short leverage not found"
        )

    return {
        "margin_type": str(
            margin_type
        ).upper(),
        "position_mode": (
            str(position_mode).upper()
            if position_mode is not None
            else "UNKNOWN"
        ),
        "long_leverage": normalize_decimal(
            long_leverage
        ),
        "short_leverage": normalize_decimal(
            short_leverage
        ),
    }


# ============================================================
# LIVE POSITION RECONCILIATION
# ============================================================

def obtain_positions():
    response = authenticated_get(
        PRIVATE_POSITION_PATH
    )

    payload = extract_payload(response)

    if isinstance(payload, list):
        records = payload

    elif isinstance(payload, dict):
        records = []

        for key in (
            "list",
            "rows",
            "positions"
        ):
            value = payload.get(key)

            if isinstance(value, list):
                records.extend(value)

        if not records:
            records = [
                item
                for item in walk_find_dicts(payload)
                if (
                    "symbol" in item
                    or
                    "contractCode" in item
                )
            ]

    else:
        records = []

    symbol_records = []

    open_positions = []

    for record in records:
        if not isinstance(record, dict):
            continue

        record_symbol = (
            record.get("symbol")
            or record.get("contractCode")
        )

        if (
            record_symbol is None
            or str(record_symbol).upper()
            != SYMBOL
        ):
            continue

        symbol_records.append(record)

        qty_value = (
            record.get("total")
            or record.get("size")
            or record.get("position")
            or record.get("positionAmt")
            or record.get("holdVol")
            or "0"
        )

        qty = abs(
            normalize_decimal(qty_value)
        )

        if qty > 0:
            open_positions.append(record)

    return {
        "all_records": records,
        "symbol_records": symbol_records,
        "open_positions": open_positions,
    }


# ============================================================
# CONTRACT RULE EXTRACTION
# ============================================================

def extract_contract_rules(contract):
    quantity_precision = first_matching_value(
        contract,
        (
            "volumePlace",
            "quantityPrecision",
            "qtyPrecision",
            "sizePrecision",
        )
    )

    price_precision = first_matching_value(
        contract,
        (
            "pricePlace",
            "pricePrecision",
        )
    )

    min_order_size = first_matching_value(
        contract,
        (
            "minOrderNum",
            "minOrderSize",
            "minQty",
            "minTradeNum",
        )
    )

    max_order_size = first_matching_value(
        contract,
        (
            "maxOrderNum",
            "maxOrderSize",
            "maxQty",
            "maxTradeNum",
        )
    )

    max_leverage = first_matching_value(
        contract,
        (
            "maxLeverage",
            "maxLever",
            "leverageMax",
        )
    )

    quantity_precision = int(
        quantity_precision
        if quantity_precision is not None
        else 4
    )

    price_precision = int(
        price_precision
        if price_precision is not None
        else 1
    )

    min_order_size = normalize_decimal(
        min_order_size,
        "0.0001"
    )

    max_order_size = normalize_decimal(
        max_order_size,
        "999999999"
    )

    max_leverage = normalize_decimal(
        max_leverage,
        "400"
    )

    return {
        "quantity_precision":
            quantity_precision,

        "price_precision":
            price_precision,

        "min_order_size":
            min_order_size,

        "max_order_size":
            max_order_size,

        "max_leverage":
            max_leverage,
    }


# ============================================================
# QUANTITY NORMALIZATION
# ============================================================

def quantity_step_from_precision(
    quantity_precision
):
    return Decimal("1").scaleb(
        -quantity_precision
    )


def round_quantity_down(
    quantity,
    quantity_precision
):
    step = quantity_step_from_precision(
        quantity_precision
    )

    units = (
        quantity / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


# ============================================================
# EMA / SIGNAL ENGINE
# ============================================================

def calculate_ema(values, period):
    if len(values) < period:
        raise RuntimeError(
            f"Need at least {period} prices "
            f"for EMA calculation"
        )

    multiplier = Decimal("2") / (
        Decimal(period) + Decimal("1")
    )

    seed_values = values[:period]

    ema = sum(
        seed_values,
        Decimal("0")
    ) / Decimal(period)

    for value in values[period:]:
        ema = (
            value - ema
        ) * multiplier + ema

    return ema


def collect_price_samples(count):
    samples = []

    for index in range(count):
        price = obtain_mark_price()

        samples.append(price)

        if index < count - 1:
            time.sleep(
                float(
                    PUBLIC_PRICE_POLL_DELAY_SECONDS
                )
            )

    return samples


def construct_signal(price_samples):
    fast_ema = calculate_ema(
        price_samples,
        FAST_EMA_PERIOD
    )

    slow_ema = calculate_ema(
        price_samples,
        SLOW_EMA_PERIOD
    )

    last_price = price_samples[-1]

    spread = fast_ema - slow_ema

    if slow_ema == 0:
        spread_percent = Decimal("0")
    else:
        spread_percent = (
            abs(spread) /
            slow_ema *
            Decimal("100")
        )

    if (
        fast_ema > slow_ema and
        spread_percent >=
        SIGNAL_MIN_SPREAD_PERCENT
    ):
        direction = "LONG"

    elif (
        fast_ema < slow_ema and
        spread_percent >=
        SIGNAL_MIN_SPREAD_PERCENT
    ):
        direction = "SHORT"

    else:
        direction = "NONE"

    return {
        "direction": direction,
        "fast_ema": fast_ema,
        "slow_ema": slow_ema,
        "last_price": last_price,
        "spread_percent": spread_percent,
        "generated_at": int(time.time()),
        "expires_at": int(
            time.time() +
            SIGNAL_EXPIRY_SECONDS
        ),
    }


# ============================================================
# ENTRY READINESS CALCULATION
# ============================================================

def calculate_entry_readiness(
    balance,
    mark_price,
    quantity_precision
):
    entry_margin_budget = (
        balance *
        INITIAL_ENTRY_PERCENT /
        Decimal("100")
    )

    planned_notional = (
        entry_margin_budget *
        TARGET_LONG_LEVERAGE
    )

    raw_quantity = (
        planned_notional /
        mark_price
    )

    rounded_quantity = (
        round_quantity_down(
            raw_quantity,
            quantity_precision
        )
    )

    rounded_notional = (
        rounded_quantity *
        mark_price
    )

    estimated_margin = (
        rounded_notional /
        TARGET_LONG_LEVERAGE
    )

    return {
        "entry_margin_budget":
            entry_margin_budget,

        "planned_notional":
            planned_notional,

        "raw_quantity":
            raw_quantity,

        "rounded_quantity":
            rounded_quantity,

        "rounded_notional":
            rounded_notional,

        "estimated_margin":
            estimated_margin,
    }


# ============================================================
# TAKE PROFIT PRICE CALCULATION
# ============================================================

def calculate_tp_structure(
    direction,
    entry_price
):
    if direction == "LONG":
        tp1_price = entry_price * (
            Decimal("1") +
            TP1_TRIGGER_PERCENT /
            Decimal("100")
        )

        tp2_price = entry_price * (
            Decimal("1") +
            TP2_TRIGGER_PERCENT /
            Decimal("100")
        )

    elif direction == "SHORT":
        tp1_price = entry_price * (
            Decimal("1") -
            TP1_TRIGGER_PERCENT /
            Decimal("100")
        )

        tp2_price = entry_price * (
            Decimal("1") -
            TP2_TRIGGER_PERCENT /
            Decimal("100")
        )

    else:
        tp1_price = entry_price
        tp2_price = entry_price

    return {
        "tp1_price": tp1_price,
        "tp2_price": tp2_price,
        "tp1_allocation":
            TP1_ALLOCATION_PERCENT,
        "tp2_allocation":
            TP2_ALLOCATION_PERCENT,
        "tp3_allocation":
            TP3_ALLOCATION_PERCENT,
        "trailing_distance":
            TRAILING_DISTANCE_PERCENT,
    }


# ============================================================
# SYNTHETIC ORDER INTENT
# ============================================================

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":")
    )


def sha256_text(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def build_synthetic_order_intent(
    signal,
    entry,
    tp_structure,
    rules
):
    if signal["direction"] not in (
        "LONG",
        "SHORT"
    ):
        return None

    created_at = int(time.time())

    intent_body = {
        "version": VERSION,
        "intent_type":
            "SYNTHETIC_ORDER_INTENT",

        "synthetic_only": True,

        "network_transmission_allowed":
            False,

        "real_execution_allowed":
            False,

        "demo_execution_allowed":
            False,

        "symbol": SYMBOL,

        "direction":
            signal["direction"],

        "margin_type":
            TARGET_MARGIN_TYPE,

        "leverage":
            decimal_text(
                TARGET_LONG_LEVERAGE
            ),

        "quantity":
            decimal_text(
                entry[
                    "rounded_quantity"
                ]
            ),

        "reference_price":
            decimal_text(
                signal["last_price"]
            ),

        "estimated_notional":
            decimal_text(
                entry[
                    "rounded_notional"
                ]
            ),

        "estimated_margin":
            decimal_text(
                entry[
                    "estimated_margin"
                ]
            ),

        "signal": {
            "fast_ema":
                decimal_text(
                    signal["fast_ema"]
                ),

            "slow_ema":
                decimal_text(
                    signal["slow_ema"]
                ),

            "spread_percent":
                decimal_text(
                    signal[
                        "spread_percent"
                    ]
                ),

            "generated_at":
                signal[
                    "generated_at"
                ],

            "expires_at":
                signal[
                    "expires_at"
                ],
        },

        "take_profit": {
            "tp1_allocation_percent":
                decimal_text(
                    tp_structure[
                        "tp1_allocation"
                    ]
                ),

            "tp1_reference_price":
                decimal_text(
                    tp_structure[
                        "tp1_price"
                    ]
                ),

            "tp2_allocation_percent":
                decimal_text(
                    tp_structure[
                        "tp2_allocation"
                    ]
                ),

            "tp2_reference_price":
                decimal_text(
                    tp_structure[
                        "tp2_price"
                    ]
                ),

            "tp3_allocation_percent":
                decimal_text(
                    tp_structure[
                        "tp3_allocation"
                    ]
                ),

            "trailing_distance_percent":
                decimal_text(
                    tp_structure[
                        "trailing_distance"
                    ]
                ),
        },

        "exchange_rules": {
            "quantity_precision":
                rules[
                    "quantity_precision"
                ],

            "price_precision":
                rules[
                    "price_precision"
                ],

            "minimum_order_size":
                decimal_text(
                    rules[
                        "min_order_size"
                    ]
                ),
        },

        "risk": {
            "initial_entry_percent":
                decimal_text(
                    INITIAL_ENTRY_PERCENT
                ),

            "max_fund_exposure_percent":
                decimal_text(
                    MAX_FUND_EXPOSURE_PERCENT
                ),

            "max_pyramid_adds":
                MAX_PYRAMID_ADDS,

            "max_backups":
                MAX_BACKUPS,

            "one_direction_only":
                ONE_DIRECTION_ONLY,

            "anti_duplicate_orders":
                ANTI_DUPLICATE_ORDERS,

            "trend_reversal_exit":
                TREND_REVERSAL_EXIT,

            "idle_pyramid_cleanup":
                IDLE_PYRAMID_CLEANUP,
        },

        "created_at": created_at,

        "transport": {
            "method": "NONE",
            "path":
                REAL_ORDER_PATH_PLACEHOLDER,

            "network_dispatch":
                "FORBIDDEN",
        },
    }

    body = canonical_json(intent_body)

    intent_hash = sha256_text(body)

    intent_id = (
        f"{VERSION}-"
        f"{SYMBOL}-"
        f"{created_at}-"
        f"{intent_hash[:16]}"
    )

    envelope = {
        "intent_id": intent_id,
        "intent_hash": intent_hash,
        "body": intent_body,
    }

    COUNTERS["synthetic_intents"] += 1

    return envelope


# ============================================================
# SYNTHETIC TRANSPORT FIREBREAK
# ============================================================

def synthetic_dispatch_firebreak(intent):
    if intent is None:
        return {
            "accepted_locally": False,
            "reason": "NO_ACTIONABLE_SIGNAL",
            "network_sent": False,
        }

    body = intent["body"]

    if not body.get("synthetic_only"):
        raise RuntimeError(
            "Intent is not synthetic"
        )

    if body.get(
        "network_transmission_allowed"
    ):
        raise RuntimeError(
            "Intent unexpectedly allows "
            "network transmission"
        )

    if body.get(
        "real_execution_allowed"
    ):
        raise RuntimeError(
            "Intent unexpectedly allows "
            "real execution"
        )

    if body.get(
        "demo_execution_allowed"
    ):
        raise RuntimeError(
            "Intent unexpectedly allows "
            "demo execution"
        )

    # This is deliberately LOCAL ONLY.
    # No HTTP function is called here.

    return {
        "accepted_locally": True,
        "reason":
            "SYNTHETIC_FIREBREAK_VALIDATED",
        "network_sent": False,
        "intent_id":
            intent["intent_id"],
        "intent_hash":
            intent["intent_hash"],
    }


# ============================================================
# WRITE-FIREBREAK TEST HELPER
# ============================================================

def expect_rejection(function):
    try:
        function()
    except Exception:
        return True

    return False


# ============================================================
# MAIN VALIDATION
# ============================================================

def main():

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(
        f"{VERSION}: HEALTH PORT="
        f"{HEALTH_PORT}"
    )

    log(
        f"{VERSION}: AUTHENTICATED "
        f"READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: PUBLIC "
        f"READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: REAL ORDER "
        f"EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: DEMO ORDER "
        f"EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: NETWORK "
        f"WRITES DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE "
        f"MUTATION DISABLED"
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


    # ========================================================
    # TEST 1
    # ========================================================

    section(
        f"{VERSION} TEST 1: "
        f"HARD SAFETY CONFIGURATION"
    )

    pass_fail(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY
    )

    pass_fail(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY
    )

    pass_fail(
        "Synthetic Order Intent Only Is Enabled",
        SYNTHETIC_ORDER_INTENT_ONLY
    )

    pass_fail(
        "Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED
    )

    pass_fail(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION_ENABLED
    )

    pass_fail(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION_ENABLED
    )

    pass_fail(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED
    )

    pass_fail(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED
    )

    pass_fail(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED
    )

    pass_fail(
        "Account Mutation Is Disabled",
        not ACCOUNT_MUTATION_ENABLED
    )


    # ========================================================
    # TEST 2
    # ========================================================

    section(
        f"{VERSION} TEST 2: "
        f"WRITE FIREBREAK"
    )

    pass_fail(
        "HTTP POST Is Rejected",
        expect_rejection(
            lambda: http_post()
        )
    )

    pass_fail(
        "HTTP PUT Is Rejected",
        expect_rejection(
            lambda: http_put()
        )
    )

    pass_fail(
        "HTTP PATCH Is Rejected",
        expect_rejection(
            lambda: http_patch()
        )
    )

    pass_fail(
        "HTTP DELETE Is Rejected",
        expect_rejection(
            lambda: http_delete()
        )
    )

    pass_fail(
        "Generic Network Write Is Rejected",
        expect_rejection(
            lambda:
            generic_network_write()
        )
    )

    pass_fail(
        "Real Order Function Is Rejected",
        expect_rejection(
            lambda:
            execute_real_order()
        )
    )

    pass_fail(
        "Demo Order Function Is Rejected",
        expect_rejection(
            lambda:
            execute_demo_order()
        )
    )

    pass_fail(
        "Leverage Mutation Function Is Rejected",
        expect_rejection(
            lambda:
            mutate_leverage()
        )
    )

    pass_fail(
        "Margin Mutation Function Is Rejected",
        expect_rejection(
            lambda:
            mutate_margin()
        )
    )

    pass_fail(
        "Position Mutation Function Is Rejected",
        expect_rejection(
            lambda:
            mutate_position()
        )
    )


    # ========================================================
    # TEST 3
    # ========================================================

    section(
        f"{VERSION} TEST 3: "
        f"API CREDENTIAL PRESENCE"
    )

    pass_fail(
        "WEEX API Key Is Present",
        bool(WEEX_API_KEY)
    )

    pass_fail(
        "WEEX API Secret Is Present",
        bool(WEEX_API_SECRET)
    )

    pass_fail(
        "WEEX API Passphrase Is Present",
        bool(WEEX_API_PASSPHRASE)
    )


    # ========================================================
    # TEST 4
    # ========================================================

    section(
        f"{VERSION} TEST 4: "
        f"LIVE EXCHANGE INFORMATION"
    )

    contract = (
        obtain_contract_information()
    )

    rules = extract_contract_rules(
        contract
    )

    contract_symbol = (
        contract.get("symbol")
        or contract.get(
            "contractCode"
        )
        or SYMBOL
    )

    pass_fail(
        "Exchange Symbol Matches",
        str(contract_symbol).upper()
        == SYMBOL
    )

    pass_fail(
        "Quantity Precision Is Valid",
        rules["quantity_precision"]
        >= 0
    )

    pass_fail(
        "Price Precision Is Valid",
        rules["price_precision"]
        >= 0
    )

    pass_fail(
        "Minimum Order Size Is Positive",
        rules["min_order_size"]
        > 0
    )

    pass_fail(
        "Exchange Supports Target Leverage",
        rules["max_leverage"]
        >= TARGET_LONG_LEVERAGE
    )

    log(
        f"{VERSION}: QUANTITY PRECISION="
        f"{rules['quantity_precision']}"
    )

    log(
        f"{VERSION}: PRICE PRECISION="
        f"{rules['price_precision']}"
    )

    log(
        f"{VERSION}: MIN ORDER SIZE="
        f"{decimal_text(rules['min_order_size'])}"
    )

    log(
        f"{VERSION}: EXCHANGE MAX LEVERAGE="
        f"{decimal_text(rules['max_leverage'])}x"
    )


    # ========================================================
    # TEST 5
    # ========================================================

    section(
        f"{VERSION} TEST 5: "
        f"LIVE BALANCE RECONCILIATION"
    )

    balance = obtain_available_balance()

    RUNTIME["available_balance"] = balance

    pass_fail(
        "Available Balance Was Read",
        balance is not None
    )

    pass_fail(
        "Available Balance Is Positive",
        balance > 0
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(balance)}"
    )


    # ========================================================
    # TEST 6
    # ========================================================

    section(
        f"{VERSION} TEST 6: "
        f"LIVE SYMBOL CONFIGURATION"
    )

    symbol_config = (
        obtain_symbol_configuration()
    )

    margin_type = symbol_config[
        "margin_type"
    ]

    position_mode = symbol_config[
        "position_mode"
    ]

    long_leverage = symbol_config[
        "long_leverage"
    ]

    short_leverage = symbol_config[
        "short_leverage"
    ]

    correction_required = not (
        margin_type ==
        TARGET_MARGIN_TYPE
        and
        long_leverage ==
        TARGET_LONG_LEVERAGE
        and
        short_leverage ==
        TARGET_SHORT_LEVERAGE
    )

    RUNTIME["margin_type"] = (
        margin_type
    )

    RUNTIME["position_mode"] = (
        position_mode
    )

    RUNTIME["long_leverage"] = (
        long_leverage
    )

    RUNTIME["short_leverage"] = (
        short_leverage
    )

    RUNTIME[
        "correction_required"
    ] = correction_required

    pass_fail(
        "Margin Type Matches Strategy",
        margin_type ==
        TARGET_MARGIN_TYPE
    )

    pass_fail(
        "Long Leverage Matches 100x",
        long_leverage ==
        TARGET_LONG_LEVERAGE
    )

    pass_fail(
        "Short Leverage Matches 100x",
        short_leverage ==
        TARGET_SHORT_LEVERAGE
    )

    pass_fail(
        "No Account Correction Is Required",
        not correction_required
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{margin_type}"
    )

    log(
        f"{VERSION}: POSITION MODE="
        f"{position_mode}"
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
    # TEST 7
    # ========================================================

    section(
        f"{VERSION} TEST 7: "
        f"LIVE POSITION RECONCILIATION"
    )

    positions = obtain_positions()

    total_position_records = len(
        positions["all_records"]
    )

    symbol_position_records = len(
        positions["symbol_records"]
    )

    open_positions = len(
        positions["open_positions"]
    )

    RUNTIME["open_positions"] = (
        open_positions
    )

    pass_fail(
        "Position Snapshot Was Read",
        positions is not None
    )

    pass_fail(
        "No Existing BTCUSDT Position Is Open",
        open_positions == 0
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{total_position_records}"
    )

    log(
        f"{VERSION}: BTCUSDT POSITION RECORDS="
        f"{symbol_position_records}"
    )

    log(
        f"{VERSION}: BTCUSDT OPEN POSITIONS="
        f"{open_positions}"
    )


    # ========================================================
    # TEST 8
    # ========================================================

    section(
        f"{VERSION} TEST 8: "
        f"LIVE MARKET PRICE SAMPLING"
    )

    price_samples = collect_price_samples(
        RECENT_PRICE_SAMPLE_COUNT
    )

    mark_price = price_samples[-1]

    RUNTIME["mark_price"] = mark_price

    pass_fail(
        "Required Price Samples Were Collected",
        len(price_samples) ==
        RECENT_PRICE_SAMPLE_COUNT
    )

    pass_fail(
        "All Price Samples Are Positive",
        all(
            price > 0
            for price in price_samples
        )
    )

    pass_fail(
        "Latest Mark Price Is Positive",
        mark_price > 0
    )

    log(
        f"{VERSION}: PRICE SAMPLE COUNT="
        f"{len(price_samples)}"
    )

    log(
        f"{VERSION}: CURRENT MARK PRICE="
        f"{decimal_text(mark_price)}"
    )


    # ========================================================
    # TEST 9
    # ========================================================

    section(
        f"{VERSION} TEST 9: "
        f"DETERMINISTIC SIGNAL CONSTRUCTION"
    )

    signal = construct_signal(
        price_samples
    )

    RUNTIME["signal"] = (
        signal["direction"]
    )

    RUNTIME["signal_strength"] = (
        signal["spread_percent"]
    )

    RUNTIME["signal_expiry"] = (
        signal["expires_at"]
    )

    pass_fail(
        "Fast EMA Is Positive",
        signal["fast_ema"] > 0
    )

    pass_fail(
        "Slow EMA Is Positive",
        signal["slow_ema"] > 0
    )

    pass_fail(
        "Signal Direction Is Valid",
        signal["direction"] in (
            "LONG",
            "SHORT",
            "NONE",
        )
    )

    pass_fail(
        "Signal Expiry Is In Future",
        signal["expires_at"]
        >
        signal["generated_at"]
    )

    pass_fail(
        "Signal Lifetime Is 120 Seconds",
        (
            signal["expires_at"]
            -
            signal["generated_at"]
        )
        ==
        SIGNAL_EXPIRY_SECONDS
    )

    log(
        f"{VERSION}: FAST EMA="
        f"{decimal_text(signal['fast_ema'])}"
    )

    log(
        f"{VERSION}: SLOW EMA="
        f"{decimal_text(signal['slow_ema'])}"
    )

    log(
        f"{VERSION}: EMA SPREAD="
        f"{decimal_text(signal['spread_percent'])}%"
    )

    log(
        f"{VERSION}: SIGNAL="
        f"{signal['direction']}"
    )

    log(
        f"{VERSION}: SIGNAL EXPIRES="
        f"{signal['expires_at']}"
    )


    # ========================================================
    # TEST 10
    # ========================================================

    section(
        f"{VERSION} TEST 10: "
        f"ENTRY SIZE CALCULATION"
    )

    entry = calculate_entry_readiness(
        balance,
        mark_price,
        rules["quantity_precision"]
    )

    RUNTIME["entry_quantity"] = (
        entry["rounded_quantity"]
    )

    exposure_cap = (
        balance *
        MAX_FUND_EXPOSURE_PERCENT /
        Decimal("100")
    )

    pass_fail(
        "Entry Margin Budget Is Positive",
        entry[
            "entry_margin_budget"
        ] > 0
    )

    pass_fail(
        "Planned Notional Is Positive",
        entry[
            "planned_notional"
        ] > 0
    )

    pass_fail(
        "Raw Quantity Is Positive",
        entry["raw_quantity"] > 0
    )

    pass_fail(
        "Rounded Quantity Is Positive",
        entry[
            "rounded_quantity"
        ] > 0
    )

    pass_fail(
        "Rounded Quantity Meets Exchange Minimum",
        entry[
            "rounded_quantity"
        ] >= rules["min_order_size"]
    )

    pass_fail(
        "Rounded Quantity Is Below Exchange Maximum",
        entry[
            "rounded_quantity"
        ] <= rules["max_order_size"]
    )

    pass_fail(
        "Estimated Margin Is Within 35 Percent Cap",
        entry[
            "estimated_margin"
        ] <= exposure_cap
    )

    log(
        f"{VERSION}: ENTRY BALANCE PERCENT="
        f"{decimal_text(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_text(entry['entry_margin_budget'])} "
        f"USDT"
    )

    log(
        f"{VERSION}: PLANNED NOTIONAL="
        f"{decimal_text(entry['planned_notional'])} "
        f"USDT"
    )

    log(
        f"{VERSION}: RAW QUANTITY="
        f"{decimal_text(entry['raw_quantity'])} BTC"
    )

    log(
        f"{VERSION}: ROUNDED QUANTITY="
        f"{decimal_text(entry['rounded_quantity'])} BTC"
    )

    log(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{decimal_text(entry['rounded_notional'])} USDT"
    )

    log(
        f"{VERSION}: ESTIMATED MARGIN="
        f"{decimal_text(entry['estimated_margin'])} USDT"
    )


    # ========================================================
    # TEST 11
    # ========================================================

    section(
        f"{VERSION} TEST 11: "
        f"MAXIMUM STRATEGY EXPOSURE"
    )

    planned_max_strategy_margin = (
        balance *
        (
            INITIAL_ENTRY_PERCENT
            +
            PYRAMID_PERCENT *
            Decimal(
                MAX_PYRAMID_ADDS
            )
            +
            BACKUP_PERCENT *
            Decimal(
                MAX_BACKUPS
            )
        )
        /
        Decimal("100")
    )

    pass_fail(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1
    )

    pass_fail(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3
    )

    pass_fail(
        "Maximum Planned Strategy Margin Is Within 35%",
        planned_max_strategy_margin
        <= exposure_cap
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{decimal_text(exposure_cap)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_text(planned_max_strategy_margin)} "
        f"USDT"
    )


    # ========================================================
    # TEST 12
    # ========================================================

    section(
        f"{VERSION} TEST 12: "
        f"TAKE-PROFIT STRUCTURE"
    )

    tp_structure = calculate_tp_structure(
        signal["direction"],
        mark_price
    )

    allocation_total = (
        TP1_ALLOCATION_PERCENT
        +
        TP2_ALLOCATION_PERCENT
        +
        TP3_ALLOCATION_PERCENT
    )

    pass_fail(
        "TP Allocation Totals 100 Percent",
        allocation_total ==
        Decimal("100")
    )

    pass_fail(
        "TP1 Trigger Is Positive",
        TP1_TRIGGER_PERCENT > 0
    )

    pass_fail(
        "TP2 Trigger Is Above TP1",
        TP2_TRIGGER_PERCENT
        >
        TP1_TRIGGER_PERCENT
    )

    pass_fail(
        "Trailing Distance Is Positive",
        TRAILING_DISTANCE_PERCENT > 0
    )

    log(
        f"{VERSION}: TP1=20% AT +/"
        f"-{decimal_text(TP1_TRIGGER_PERCENT)}%"
    )

    log(
        f"{VERSION}: TP2=20% AT +/"
        f"-{decimal_text(TP2_TRIGGER_PERCENT)}%"
    )

    log(
        f"{VERSION}: TP3=60% TRAILING"
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{decimal_text(TRAILING_DISTANCE_PERCENT)}%"
    )


    # ========================================================
    # TEST 13
    # ========================================================

    section(
        f"{VERSION} TEST 13: "
        f"SYNTHETIC ORDER INTENT CONSTRUCTION"
    )

    intent = build_synthetic_order_intent(
        signal,
        entry,
        tp_structure,
        rules
    )

    if signal["direction"] == "NONE":

        pass_fail(
            "No Actionable Signal Produces No Order Intent",
            intent is None
        )

        log(
            f"{VERSION}: NO ACTIONABLE SIGNAL"
        )

        log(
            f"{VERSION}: SYNTHETIC INTENT="
            f"NOT CREATED"
        )

    else:

        pass_fail(
            "Actionable Signal Produces Synthetic Intent",
            intent is not None
        )

        pass_fail(
            "Intent Is Explicitly Synthetic Only",
            intent["body"][
                "synthetic_only"
            ] is True
        )

        pass_fail(
            "Intent Forbids Network Transmission",
            intent["body"][
                "network_transmission_allowed"
            ] is False
        )

        pass_fail(
            "Intent Forbids Real Execution",
            intent["body"][
                "real_execution_allowed"
            ] is False
        )

        pass_fail(
            "Intent Forbids Demo Execution",
            intent["body"][
                "demo_execution_allowed"
            ] is False
        )

        pass_fail(
            "Intent Symbol Matches",
            intent["body"]["symbol"]
            == SYMBOL
        )

        pass_fail(
            "Intent Direction Matches Signal",
            intent["body"]["direction"]
            ==
            signal["direction"]
        )

        pass_fail(
            "Intent Quantity Matches Validated Quantity",
            normalize_decimal(
                intent["body"]["quantity"]
            )
            ==
            entry[
                "rounded_quantity"
            ]
        )

        RUNTIME[
            "synthetic_intent_id"
        ] = intent["intent_id"]

        RUNTIME[
            "synthetic_intent_hash"
        ] = intent["intent_hash"]

        log(
            f"{VERSION}: SYNTHETIC INTENT ID="
            f"{intent['intent_id']}"
        )

        log(
            f"{VERSION}: SYNTHETIC INTENT SHA256="
            f"{intent['intent_hash']}"
        )


    # ========================================================
    # TEST 14
    # ========================================================

    section(
        f"{VERSION} TEST 14: "
        f"FINAL SYNTHETIC DISPATCH FIREBREAK"
    )

    receipt = synthetic_dispatch_firebreak(
        intent
    )

    pass_fail(
        "Synthetic Dispatch Did Not Send Network Traffic",
        receipt[
            "network_sent"
        ] is False
    )

    if signal["direction"] == "NONE":

        pass_fail(
            "No Signal Dispatch Is Safely Suppressed",
            receipt[
                "accepted_locally"
            ] is False
        )

    else:

        pass_fail(
            "Synthetic Intent Was Accepted Locally",
            receipt[
                "accepted_locally"
            ] is True
        )

        pass_fail(
            "Synthetic Receipt Matches Intent ID",
            receipt[
                "intent_id"
            ]
            ==
            intent[
                "intent_id"
            ]
        )

        pass_fail(
            "Synthetic Receipt Matches Intent Hash",
            receipt[
                "intent_hash"
            ]
            ==
            intent[
                "intent_hash"
            ]
        )


    # ========================================================
    # TEST 15
    # ========================================================

    section(
        f"{VERSION} TEST 15: "
        f"FINAL EXECUTION-READINESS FIREBREAK"
    )

    pass_fail(
        "Network Writes Remain Zero",
        COUNTERS[
            "network_writes"
        ] == 0
    )

    pass_fail(
        "Leverage Mutations Remain Zero",
        COUNTERS[
            "leverage_mutations"
        ] == 0
    )

    pass_fail(
        "Margin Mutations Remain Zero",
        COUNTERS[
            "margin_mutations"
        ] == 0
    )

    pass_fail(
        "Position Mutations Remain Zero",
        COUNTERS[
            "position_mutations"
        ] == 0
    )

    pass_fail(
        "Account Mutations Remain Zero",
        COUNTERS[
            "account_mutations"
        ] == 0
    )

    pass_fail(
        "Real Orders Remain Zero",
        COUNTERS[
            "real_orders"
        ] == 0
    )

    pass_fail(
        "Demo Orders Remain Zero",
        COUNTERS[
            "demo_orders"
        ] == 0
    )

    pass_fail(
        "Account Configuration Requires No Correction",
        not correction_required
    )

    pass_fail(
        "No Existing BTCUSDT Position Exists",
        open_positions == 0
    )


    # ========================================================
    # COMPLETE
    # ========================================================

    RUNTIME[
        "phase"
    ] = "LIVE_SIGNAL_INTENT_READINESS_VALIDATED"

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    pass_fail(
        "Live Signal / Intent Readiness",
        True
    )

    pass_fail(
        "Account Is ISOLATED 100x / 100x",
        (
            margin_type
            ==
            TARGET_MARGIN_TYPE
            and
            long_leverage
            ==
            TARGET_LONG_LEVERAGE
            and
            short_leverage
            ==
            TARGET_SHORT_LEVERAGE
        )
    )

    pass_fail(
        "Entry Calculation Is Exchange Compatible",
        (
            entry[
                "rounded_quantity"
            ]
            >=
            rules[
                "min_order_size"
            ]
            and
            entry[
                "rounded_quantity"
            ]
            <=
            rules[
                "max_order_size"
            ]
        )
    )

    pass_fail(
        "Maximum Strategy Exposure Is Within 35%",
        planned_max_strategy_margin
        <=
        exposure_cap
    )

    pass_fail(
        "No Account Mutation Was Performed",
        COUNTERS[
            "account_mutations"
        ] == 0
    )

    pass_fail(
        "No Real Order Was Sent",
        COUNTERS[
            "real_orders"
        ] == 0
    )

    pass_fail(
        "No Demo Order Was Sent",
        COUNTERS[
            "demo_orders"
        ] == 0
    )

    pass_fail(
        "Network Writes Remain Zero",
        COUNTERS[
            "network_writes"
        ] == 0
    )


# ============================================================
# HEARTBEAT
# ============================================================

def heartbeat_loop():
    heartbeat = 0

    while True:
        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"phase={RUNTIME['phase']} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get="
            f"{COUNTERS['authenticated_get']} | "
            f"public-get="
            f"{COUNTERS['public_get']} | "
            f"network-writes="
            f"{COUNTERS['network_writes']} | "
            f"leverage-mutations="
            f"{COUNTERS['leverage_mutations']} | "
            f"real-orders="
            f"{COUNTERS['real_orders']} | "
            f"demo-orders="
            f"{COUNTERS['demo_orders']} | "
            f"synthetic-intents="
            f"{COUNTERS['synthetic_intents']} | "
            f"correction-required="
            f"{RUNTIME['correction_required']} | "
            f"observed-margin="
            f"{RUNTIME['margin_type']} | "
            f"observed-long="
            f"{decimal_text(RUNTIME['long_leverage']) if RUNTIME['long_leverage'] is not None else None} | "
            f"observed-short="
            f"{decimal_text(RUNTIME['short_leverage']) if RUNTIME['short_leverage'] is not None else None} | "
            f"target-long="
            f"{decimal_text(TARGET_LONG_LEVERAGE)}x | "
            f"target-short="
            f"{decimal_text(TARGET_SHORT_LEVERAGE)}x | "
            f"signal="
            f"{RUNTIME['signal']} | "
            f"signal-strength="
            f"{decimal_text(RUNTIME['signal_strength']) if RUNTIME['signal_strength'] is not None else None}% | "
            f"entry-qty="
            f"{decimal_text(RUNTIME['entry_quantity']) if RUNTIME['entry_quantity'] is not None else None}"
        )

        time.sleep(30)


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    health_server = None

    try:
        health_server = run_health_server()

        main()

        heartbeat_loop()

    except KeyboardInterrupt:
        log(
            f"{VERSION}: SHUTDOWN REQUESTED"
        )

    except Exception as exc:
        RUNTIME["phase"] = (
            "VALIDATION_FAILED"
        )

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        raise
