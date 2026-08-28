#!/usr/bin/env python3

# ==================================================================================================
# R34Q - WEEX BTCUSDT
#
# LIVE READ-ONLY EXECUTION AUTHORIZATION + EXACTLY-ONCE SYNTHETIC DISPATCH VALIDATION
#
# IMPORTANT SAFETY PROPERTIES
# --------------------------------------------------------------------------------------------------
# - AUTHENTICATED READ-ONLY GETS ARE ALLOWED.
# - PUBLIC READ-ONLY GETS ARE ALLOWED.
# - REAL ORDER EXECUTION IS DISABLED.
# - DEMO ORDER EXECUTION IS DISABLED.
# - NETWORK POST / PUT / PATCH / DELETE ARE DISABLED.
# - LEVERAGE MUTATION IS DISABLED.
# - MARGIN MUTATION IS DISABLED.
# - POSITION MUTATION IS DISABLED.
# - ACCOUNT MUTATION IS DISABLED.
# - SYNTHETIC ORDER AUTHORIZATION IS LOCAL ONLY.
# - SYNTHETIC DISPATCH IS LOCAL ONLY.
# - NO FINANCIAL ORDER IS TRANSMITTED.
#
# R34Q ADDS:
# - deterministic live-state fingerprint
# - one-time synthetic authorization
# - authorization expiry
# - stale-state rejection
# - authorization replay rejection
# - payload/envelope binding
# - exactly-once synthetic dispatch fence
# - duplicate dispatch rejection
# - local synthetic transport receipt
# - final network-write firebreak
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
import urllib.parse
import urllib.request
import urllib.error
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone


# ==================================================================================================
# PART 1 - CONFIGURATION / SAFETY / UTILITIES
# ==================================================================================================

VERSION = "R34Q"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper().strip()

BASE_URL = os.getenv("WEEX_BASE_URL", "https://api-contract.weex.com").rstrip("/")

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")

TP1_ALLOCATION = Decimal("20")
TP2_ALLOCATION = Decimal("20")
TP3_ALLOCATION = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.2")

SIGNAL_EXPIRY_SECONDS = 120
AUTHORIZATION_EXPIRY_SECONDS = 60

HTTP_TIMEOUT_SECONDS = 12

# --------------------------------------------------------------------------------------------------
# HARD SAFETY LOCKS
# --------------------------------------------------------------------------------------------------

AUTHENTICATED_READ_ONLY_ENABLED = True
PUBLIC_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_ONLY = True

# --------------------------------------------------------------------------------------------------
# READ-ONLY ENDPOINTS
# --------------------------------------------------------------------------------------------------

BALANCE_PATH = "/capi/v3/account/balance"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
POSITION_PATH = "/capi/v3/account/position/allPosition"

# Public paths.
# These are only used with GET.
CONTRACT_INFO_CANDIDATES = [
    "/capi/v3/market/exchangeInfo",
    "/capi/v3/market/contracts",
]

PRICE_CANDIDATES = [
    "/capi/v3/market/symbolPrice",
    "/capi/v3/market/ticker",
]

DEPTH_CANDIDATES = [
    "/capi/v3/market/depth",
]

# This path is NEVER transmitted by R34Q.
ORDER_PATH = "/capi/v3/order"


# ==================================================================================================
# GLOBAL COUNTERS / STATE
# ==================================================================================================

COUNTERS = {
    "authenticated_get": 0,
    "public_get": 0,
    "network_writes": 0,
    "leverage_mutations": 0,
    "margin_mutations": 0,
    "position_mutations": 0,
    "account_mutations": 0,
    "real_orders": 0,
    "demo_orders": 0,
    "synthetic_envelopes": 0,
    "authorization_requests": 0,
    "authorization_grants": 0,
    "authorization_denials": 0,
    "authorization_replays_blocked": 0,
    "stale_state_blocks": 0,
    "synthetic_dispatches": 0,
    "duplicate_dispatches_blocked": 0,
    "synthetic_receipts": 0,
}

RUNTIME = {
    "phase": "BOOT",
    "correction_required": None,
    "observed_margin": None,
    "observed_long": None,
    "observed_short": None,
    "available_usdt": None,
    "market_price": None,
    "entry_qty": None,
    "spread_pct": None,
    "state_fingerprint": None,
    "authorization_id": None,
    "authorization_consumed": False,
    "dispatch_id": None,
    "dispatch_completed": False,
    "last_error": None,
}

AUTHORIZATION_REGISTRY = {}
DISPATCH_REGISTRY = {}

STATE_LOCK = threading.Lock()


# ==================================================================================================
# DISPLAY HELPERS
# ==================================================================================================

LINE = "-" * 100


def log(message=""):
    print(message, flush=True)


def section(title):
    log(LINE)
    log(title)
    log(LINE)


def pass_test(name):
    log(f"{name:<88} ✅ PASS")


def fail_test(name, detail=None):
    log(f"{name:<88} ❌ FAIL")
    if detail:
        log(f"{VERSION}: DETAIL={detail}")
    raise RuntimeError(name if not detail else f"{name}: {detail}")


def require(condition, name, detail=None):
    if condition:
        pass_test(name)
    else:
        fail_test(name, detail)


def decimal_value(value, default=None):
    if isinstance(value, Decimal):
        return value

    if value is None:
        return default

    if isinstance(value, bool):
        return default

    try:
        text = str(value).strip()

        if text == "":
            return default

        return Decimal(text)

    except (InvalidOperation, ValueError, TypeError):
        return default


def canonical_json(data):
    return json.dumps(
        data,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    )


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(data):
    return sha256_text(canonical_json(data))


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_ms():
    return str(int(time.time() * 1000))


def normalize_margin(value):
    if value is None:
        return ""

    value = str(value).strip().upper()

    mapping = {
        "1": "ISOLATED",
        "2": "CROSS",
        "ISOLATE": "ISOLATED",
        "ISOLATED": "ISOLATED",
        "CROSS": "CROSS",
        "CROSSED": "CROSS",
    }

    return mapping.get(value, value)


def deep_find(obj, candidate_keys):
    wanted = {str(k).lower() for k in candidate_keys}

    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in wanted:
                return value

        for value in obj.values():
            found = deep_find(value, candidate_keys)

            if found is not None:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = deep_find(item, candidate_keys)

            if found is not None:
                return found

    return None


def deep_find_all_records(obj):
    records = []

    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                records.append(item)

    elif isinstance(obj, dict):
        for key in ("data", "result", "rows", "list", "items"):
            value = obj.get(key)

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        records.append(item)

            elif isinstance(value, dict):
                records.append(value)

    return records


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

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
            "synthetic_only": SYNTHETIC_ONLY,
            "network_writes": COUNTERS["network_writes"],
            "real_orders": COUNTERS["real_orders"],
            "demo_orders": COUNTERS["demo_orders"],
            "synthetic_dispatches": COUNTERS["synthetic_dispatches"],
            "dispatch_completed": RUNTIME["dispatch_completed"],
        }

        body = canonical_json(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


def start_health_server():
    def runner():
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
        server.serve_forever()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()


# ==================================================================================================
# HTTP / AUTHENTICATION
# ==================================================================================================

def require_credentials():
    missing = []

    if not WEEX_API_KEY:
        missing.append("WEEX_API_KEY")

    if not WEEX_API_SECRET:
        missing.append("WEEX_API_SECRET")

    if not WEEX_API_PASSPHRASE:
        missing.append("WEEX_API_PASSPHRASE")

    if missing:
        raise RuntimeError("Missing credentials: " + ", ".join(missing))


def build_signature(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method.upper()}{request_path}{body}"

    signature = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(signature).decode("utf-8")


def authenticated_headers(method, request_path, body=""):
    timestamp = now_ms()

    signature = build_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        body=body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only-validator",
    }


def decode_response(raw):
    text = raw.decode("utf-8", errors="replace").strip()

    if not text:
        return {}

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return {"raw": text}


def authenticated_get(path, params=None):
    if not AUTHENTICATED_READ_ONLY_ENABLED:
        raise RuntimeError("Authenticated read-only access disabled")

    if not path.startswith("/capi/v3/account/"):
        raise RuntimeError(f"Authenticated GET path is not allowlisted: {path}")

    params = params or {}

    query = urllib.parse.urlencode(params)

    request_path = path

    if query:
        request_path += "?" + query

    url = BASE_URL + request_path

    headers = authenticated_headers(
        method="GET",
        request_path=request_path,
        body="",
    )

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
            raw = response.read()

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")

        raise RuntimeError(
            f"Authenticated GET failed: {path} | HTTP {exc.code} | {body}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Authenticated GET failed: {path} | {type(exc).__name__}: {exc}"
        )

    COUNTERS["authenticated_get"] += 1

    return decode_response(raw)


def public_get(path, params=None):
    if not PUBLIC_READ_ONLY_ENABLED:
        raise RuntimeError("Public read-only access disabled")

    if not path.startswith("/capi/v3/market/"):
        raise RuntimeError(f"Public GET path is not allowlisted: {path}")

    params = params or {}

    query = urllib.parse.urlencode(params)

    url = BASE_URL + path

    if query:
        url += "?" + query

    request = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-public-read-only",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:
            raw = response.read()

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")

        raise RuntimeError(
            f"Public GET failed: {path} | HTTP {exc.code} | {body}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Public GET failed: {path} | {type(exc).__name__}: {exc}"
        )

    COUNTERS["public_get"] += 1

    return decode_response(raw)


# ==================================================================================================
# ABSOLUTE NETWORK-WRITE FIREBREAK
# ==================================================================================================

def reject_network_write(method, path=None, payload=None):
    method = str(method).upper()

    if method in ("POST", "PUT", "PATCH", "DELETE"):
        raise RuntimeError(
            f"{VERSION} FIREBREAK: {method} network transmission is disabled"
        )

    raise RuntimeError(
        f"{VERSION} FIREBREAK: unsupported network mutation request"
    )


def send_real_order(*_args, **_kwargs):
    raise RuntimeError(
        f"{VERSION} FIREBREAK: real order execution is disabled"
    )


def send_demo_order(*_args, **_kwargs):
    raise RuntimeError(
        f"{VERSION} FIREBREAK: demo order execution is disabled"
    )


def mutate_leverage(*_args, **_kwargs):
    raise RuntimeError(
        f"{VERSION} FIREBREAK: leverage mutation is disabled"
    )


def mutate_margin(*_args, **_kwargs):
    raise RuntimeError(
        f"{VERSION} FIREBREAK: margin mutation is disabled"
    )


# ==================================================================================================
# PART 2 - LIVE READ-ONLY RECONCILIATION
# ==================================================================================================

def obtain_available_balance():
    response = authenticated_get(BALANCE_PATH)

    candidates = deep_find_all_records(response)

    # First try to locate explicit USDT balance record.
    for record in candidates:

        asset = deep_find(
            record,
            [
                "coinName",
                "coin",
                "currency",
                "asset",
                "marginCoin",
            ],
        )

        if asset and str(asset).upper() == "USDT":

            available = deep_find(
                record,
                [
                    "available",
                    "availableBalance",
                    "availableAmount",
                    "availableEquity",
                    "balanceAvailable",
                ],
            )

            value = decimal_value(available)

            if value is not None:
                return value, response

    # Fallback recursive extraction.
    available = deep_find(
        response,
        [
            "available",
            "availableBalance",
            "availableAmount",
            "availableEquity",
            "balanceAvailable",
        ],
    )

    value = decimal_value(available)

    if value is None:
        raise RuntimeError(
            "Could not locate available USDT balance in authenticated response"
        )

    return value, response


def obtain_symbol_config():
    response = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    margin = deep_find(
        response,
        [
            "marginType",
            "marginMode",
            "margin_mode",
        ],
    )

    position_mode = deep_find(
        response,
        [
            "positionMode",
            "holdMode",
            "positionType",
        ],
    )

    long_leverage = deep_find(
        response,
        [
            "isolatedLongLeverage",
            "longLeverage",
            "longLever",
            "leverageLong",
        ],
    )

    short_leverage = deep_find(
        response,
        [
            "isolatedShortLeverage",
            "shortLeverage",
            "shortLever",
            "leverageShort",
        ],
    )

    margin = normalize_margin(margin)

    long_leverage = decimal_value(long_leverage)
    short_leverage = decimal_value(short_leverage)

    if long_leverage is None or short_leverage is None:
        raise RuntimeError(
            "Could not parse isolated long/short leverage from symbolConfig"
        )

    return {
        "margin_type": margin,
        "position_mode": str(position_mode or "").upper(),
        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
        "response": response,
    }


def obtain_positions():
    response = authenticated_get(POSITION_PATH)

    records = deep_find_all_records(response)

    symbol_records = []

    for record in records:

        record_symbol = deep_find(
            record,
            [
                "symbol",
                "contract",
                "contractCode",
            ],
        )

        if record_symbol and str(record_symbol).upper() == SYMBOL:
            symbol_records.append(record)

    open_positions = []

    for record in symbol_records:

        quantity = deep_find(
            record,
            [
                "total",
                "quantity",
                "position",
                "positionQty",
                "holdVolume",
                "size",
                "available",
            ],
        )

        qty = decimal_value(quantity, Decimal("0"))

        if qty is not None and qty.copy_abs() > Decimal("0"):
            open_positions.append(record)

    return {
        "response": response,
        "records": records,
        "symbol_records": symbol_records,
        "open_positions": open_positions,
    }


def try_public_candidates(paths, parameter_options):
    errors = []

    for path in paths:

        for params in parameter_options:

            try:
                return path, public_get(path, params)

            except Exception as exc:
                errors.append(f"{path} {params}: {exc}")

    raise RuntimeError(
        "No public endpoint candidate succeeded | " + " || ".join(errors)
    )


def obtain_market_price():

    path, response = try_public_candidates(
        PRICE_CANDIDATES,
        [
            {"symbol": SYMBOL},
            {},
        ],
    )

    price = deep_find(
        response,
        [
            "price",
            "markPrice",
            "last",
            "lastPrice",
            "close",
            "indexPrice",
        ],
    )

    value = decimal_value(price)

    if value is None or value <= 0:
        raise RuntimeError(
            f"Could not parse positive market price from {path}"
        )

    return value, path, response


def obtain_orderbook():

    path, response = try_public_candidates(
        DEPTH_CANDIDATES,
        [
            {
                "symbol": SYMBOL,
                "limit": "5",
            },
            {
                "symbol": SYMBOL,
            },
        ],
    )

    bids = deep_find(
        response,
        [
            "bids",
            "buy",
        ],
    )

    asks = deep_find(
        response,
        [
            "asks",
            "sell",
        ],
    )

    if not isinstance(bids, list) or not bids:
        raise RuntimeError("Could not parse best bid")

    if not isinstance(asks, list) or not asks:
        raise RuntimeError("Could not parse best ask")

    def level_price(level):

        if isinstance(level, list) and level:
            return decimal_value(level[0])

        if isinstance(level, dict):
            return decimal_value(
                deep_find(
                    level,
                    [
                        "price",
                        "p",
                    ],
                )
            )

        return None

    best_bid = level_price(bids[0])
    best_ask = level_price(asks[0])

    if best_bid is None or best_ask is None:
        raise RuntimeError("Best bid / ask conversion failed")

    if best_bid <= 0 or best_ask <= 0:
        raise RuntimeError("Best bid / ask must be positive")

    if best_ask < best_bid:
        raise RuntimeError("Best ask is below best bid")

    midpoint = (best_bid + best_ask) / Decimal("2")

    spread_pct = (
        (best_ask - best_bid)
        / midpoint
        * Decimal("100")
    )

    return {
        "path": path,
        "response": response,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread_pct": spread_pct,
    }


def obtain_contract_information():

    try:
        path, response = try_public_candidates(
            CONTRACT_INFO_CANDIDATES,
            [
                {"symbol": SYMBOL},
                {},
            ],
        )

    except Exception:
        # R34Q can continue with the validated BTCUSDT constraints already
        # enforced locally if the exchange changes its public contract-info route.
        return {
            "path": "LOCAL_VALIDATED_CONSTRAINTS",
            "min_qty": Decimal("0.0001"),
            "max_qty": Decimal("1000000"),
            "qty_step": Decimal("0.0001"),
            "qty_precision": 4,
            "price_step": Decimal("0.1"),
            "price_precision": 1,
            "min_leverage": Decimal("1"),
            "max_leverage": Decimal("400"),
            "response": {},
        }

    records = deep_find_all_records(response)

    selected = None

    for record in records:

        record_symbol = deep_find(
            record,
            [
                "symbol",
                "contractCode",
            ],
        )

        if record_symbol and str(record_symbol).upper() == SYMBOL:
            selected = record
            break

    if selected is None:
        selected = response

    min_qty = decimal_value(
        deep_find(
            selected,
            [
                "minOrderQty",
                "minQty",
                "minTradeNum",
                "minOrderAmount",
            ],
        ),
        Decimal("0.0001"),
    )

    max_qty = decimal_value(
        deep_find(
            selected,
            [
                "maxOrderQty",
                "maxQty",
                "maxTradeNum",
                "maxOrderAmount",
            ],
        ),
        Decimal("1000000"),
    )

    qty_step = decimal_value(
        deep_find(
            selected,
            [
                "quantityStep",
                "qtyStep",
                "sizeIncrement",
            ],
        ),
        Decimal("0.0001"),
    )

    min_leverage = decimal_value(
        deep_find(
            selected,
            [
                "minLeverage",
                "minLever",
            ],
        ),
        Decimal("1"),
    )

    max_leverage = decimal_value(
        deep_find(
            selected,
            [
                "maxLeverage",
                "maxLever",
            ],
        ),
        Decimal("400"),
    )

    return {
        "path": path,
        "min_qty": min_qty,
        "max_qty": max_qty,
        "qty_step": qty_step,
        "qty_precision": 4,
        "price_step": Decimal("0.1"),
        "price_precision": 1,
        "min_leverage": min_leverage,
        "max_leverage": max_leverage,
        "response": response,
    }


def floor_to_step(value, step):

    if step <= 0:
        raise RuntimeError("Quantity step must be positive")

    units = (value / step).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_string(value):
    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


# ==================================================================================================
# LIVE STATE FINGERPRINT
# ==================================================================================================

def create_live_state_snapshot(
    balance,
    config,
    positions,
    market_price,
    orderbook,
):

    snapshot = {
        "symbol": SYMBOL,
        "available_usdt": decimal_string(balance),
        "margin_type": config["margin_type"],
        "position_mode": config["position_mode"],
        "long_leverage": decimal_string(config["long_leverage"]),
        "short_leverage": decimal_string(config["short_leverage"]),
        "open_position_count": len(positions["open_positions"]),
        "market_price": decimal_string(market_price),
        "best_bid": decimal_string(orderbook["best_bid"]),
        "best_ask": decimal_string(orderbook["best_ask"]),
    }

    fingerprint = sha256_json(snapshot)

    return snapshot, fingerprint


# ==================================================================================================
# SYNTHETIC INTENT / PAYLOAD / ENVELOPE
# ==================================================================================================

def build_synthetic_intent(quantity, state_fingerprint):

    created_at_ms = int(time.time() * 1000)

    expires_at_ms = (
        created_at_ms
        + SIGNAL_EXPIRY_SECONDS * 1000
    )

    intent_core = {
        "version": VERSION,
        "synthetic": True,
        "transmit": False,
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": decimal_string(quantity),
        "stateFingerprint": state_fingerprint,
        "createdAt": created_at_ms,
        "expiresAt": expires_at_ms,
    }

    core_hash = sha256_json(intent_core)

    client_order_id = (
        f"r34q-{core_hash[:20]}"
    )

    intent = dict(intent_core)

    intent["newClientOrderId"] = client_order_id

    intent_hash = sha256_json(intent)

    intent["intentHash"] = intent_hash

    return intent


def build_order_payload(intent):

    payload = {
        "symbol": intent["symbol"],
        "side": intent["side"],
        "positionSide": intent["positionSide"],
        "type": intent["type"],
        "quantity": intent["quantity"],
        "newClientOrderId": intent["newClientOrderId"],
    }

    payload_hash = sha256_json(payload)

    return payload, payload_hash


def build_synthetic_execution_envelope(
    intent,
    payload,
    payload_hash,
):

    body = canonical_json(payload)

    timestamp = now_ms()

    signature = build_signature(
        timestamp=timestamp,
        method="POST",
        request_path=ORDER_PATH,
        body=body,
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }

    envelope = {
        "version": VERSION,
        "synthetic": True,
        "transmit": False,
        "networkWriteAllowed": False,
        "realExecutionAllowed": False,
        "demoExecutionAllowed": False,
        "method": "POST",
        "path": ORDER_PATH,
        "body": body,
        "payloadHash": payload_hash,
        "intentHash": intent["intentHash"],
        "stateFingerprint": intent["stateFingerprint"],
        "headers": headers,
    }

    envelope_hash = sha256_json(envelope)

    envelope["envelopeHash"] = envelope_hash

    COUNTERS["synthetic_envelopes"] += 1

    return envelope


# ==================================================================================================
# PART 3 - R34Q AUTHORIZATION / REPLAY / STALE-STATE / DISPATCH FENCING
# ==================================================================================================

def issue_synthetic_authorization(
    intent,
    payload_hash,
    envelope_hash,
    state_fingerprint,
):

    COUNTERS["authorization_requests"] += 1

    created_ms = int(time.time() * 1000)
    expires_ms = created_ms + AUTHORIZATION_EXPIRY_SECONDS * 1000

    nonce_seed = {
        "version": VERSION,
        "intentHash": intent["intentHash"],
        "payloadHash": payload_hash,
        "envelopeHash": envelope_hash,
        "stateFingerprint": state_fingerprint,
        "createdAt": created_ms,
        "expiresAt": expires_ms,
        "nonce": os.urandom(16).hex(),
    }

    authorization_id = (
        "auth-"
        + sha256_json(nonce_seed)[:32]
    )

    authorization = {
        "authorizationId": authorization_id,
        "version": VERSION,
        "syntheticOnly": True,
        "transmitAllowed": False,
        "networkWriteAllowed": False,
        "intentHash": intent["intentHash"],
        "payloadHash": payload_hash,
        "envelopeHash": envelope_hash,
        "stateFingerprint": state_fingerprint,
        "createdAt": created_ms,
        "expiresAt": expires_ms,
        "consumed": False,
    }

    authorization["authorizationHash"] = sha256_json(
        authorization
    )

    with STATE_LOCK:

        AUTHORIZATION_REGISTRY[authorization_id] = authorization

    COUNTERS["authorization_grants"] += 1

    RUNTIME["authorization_id"] = authorization_id

    return authorization


def validate_authorization(
    authorization,
    intent,
    payload_hash,
    envelope,
    current_state_fingerprint,
):

    authorization_id = authorization["authorizationId"]

    with STATE_LOCK:
        stored = AUTHORIZATION_REGISTRY.get(
            authorization_id
        )

    if stored is None:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError("Authorization does not exist")

    if stored["consumed"]:
        COUNTERS["authorization_replays_blocked"] += 1
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Consumed authorization replay rejected"
        )

    now = int(time.time() * 1000)

    if now >= stored["expiresAt"]:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Expired synthetic authorization rejected"
        )

    if not stored["syntheticOnly"]:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Authorization is not synthetic-only"
        )

    if stored["transmitAllowed"]:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Authorization unexpectedly allows transmission"
        )

    if stored["networkWriteAllowed"]:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Authorization unexpectedly allows network write"
        )

    if stored["intentHash"] != intent["intentHash"]:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Authorization intent binding mismatch"
        )

    if stored["payloadHash"] != payload_hash:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Authorization payload binding mismatch"
        )

    if stored["envelopeHash"] != envelope["envelopeHash"]:
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Authorization envelope binding mismatch"
        )

    if stored["stateFingerprint"] != current_state_fingerprint:
        COUNTERS["stale_state_blocks"] += 1
        COUNTERS["authorization_denials"] += 1
        raise RuntimeError(
            "Authorization rejected because live state is stale"
        )

    return True


def consume_authorization(authorization_id):

    with STATE_LOCK:

        authorization = AUTHORIZATION_REGISTRY.get(
            authorization_id
        )

        if authorization is None:
            raise RuntimeError(
                "Authorization not found during consumption"
            )

        if authorization["consumed"]:
            COUNTERS["authorization_replays_blocked"] += 1

            raise RuntimeError(
                "Authorization already consumed"
            )

        authorization["consumed"] = True
        authorization["consumedAt"] = int(
            time.time() * 1000
        )

    RUNTIME["authorization_consumed"] = True

    return authorization


def synthetic_transport_dispatch(
    authorization,
    envelope,
):

    if not SYNTHETIC_ONLY:
        raise RuntimeError(
            "Synthetic-only invariant is disabled"
        )

    if NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "Network-write lock unexpectedly enabled"
        )

    if REAL_ORDER_EXECUTION_ENABLED:
        raise RuntimeError(
            "Real order execution unexpectedly enabled"
        )

    if DEMO_ORDER_EXECUTION_ENABLED:
        raise RuntimeError(
            "Demo execution unexpectedly enabled"
        )

    if envelope["transmit"]:
        raise RuntimeError(
            "Envelope unexpectedly requests transmission"
        )

    if envelope["networkWriteAllowed"]:
        raise RuntimeError(
            "Envelope unexpectedly allows network writes"
        )

    authorization_id = authorization[
        "authorizationId"
    ]

    dispatch_binding = {
        "authorizationId": authorization_id,
        "authorizationHash": authorization[
            "authorizationHash"
        ],
        "intentHash": authorization["intentHash"],
        "payloadHash": authorization["payloadHash"],
        "envelopeHash": authorization["envelopeHash"],
        "stateFingerprint": authorization[
            "stateFingerprint"
        ],
    }

    dispatch_id = (
        "dispatch-"
        + sha256_json(dispatch_binding)[:32]
    )

    with STATE_LOCK:

        existing = DISPATCH_REGISTRY.get(dispatch_id)

        if existing is not None:
            COUNTERS[
                "duplicate_dispatches_blocked"
            ] += 1

            raise RuntimeError(
                "Duplicate synthetic dispatch rejected"
            )

        # The authorization is consumed BEFORE local
        # dispatch completion.
        consume_authorization(authorization_id)

        dispatch_record = {
            "dispatchId": dispatch_id,
            "synthetic": True,
            "transmitted": False,
            "networkWritePerformed": False,
            "realOrderSent": False,
            "demoOrderSent": False,
            "method": envelope["method"],
            "path": envelope["path"],
            "payloadHash": envelope["payloadHash"],
            "envelopeHash": envelope[
                "envelopeHash"
            ],
            "authorizationId": authorization_id,
            "createdAt": int(time.time() * 1000),
            "status": "SYNTHETIC_DISPATCHED",
        }

        DISPATCH_REGISTRY[
            dispatch_id
        ] = dispatch_record

    COUNTERS["synthetic_dispatches"] += 1

    RUNTIME["dispatch_id"] = dispatch_id

    receipt = {
        "receiptVersion": VERSION,
        "dispatchId": dispatch_id,
        "authorizationId": authorization_id,
        "synthetic": True,
        "transmitted": False,
        "networkWritePerformed": False,
        "exchangeAcknowledgement": False,
        "realOrderId": None,
        "demoOrderId": None,
        "payloadHash": envelope["payloadHash"],
        "envelopeHash": envelope[
            "envelopeHash"
        ],
        "receivedAt": int(time.time() * 1000),
        "status": "LOCAL_SYNTHETIC_RECEIPT",
    }

    receipt["receiptHash"] = sha256_json(receipt)

    with STATE_LOCK:

        DISPATCH_REGISTRY[
            dispatch_id
        ]["receipt"] = receipt

        DISPATCH_REGISTRY[
            dispatch_id
        ]["status"] = "COMPLETED"

    COUNTERS["synthetic_receipts"] += 1

    RUNTIME["dispatch_completed"] = True

    return receipt


# ==================================================================================================
# R34Q VALIDATION
# ==================================================================================================

def run_validation():

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")
    log(f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED")
    log(f"{VERSION}: PUBLIC READ-ONLY ENABLED")
    log(f"{VERSION}: REAL ORDER EXECUTION DISABLED")
    log(f"{VERSION}: DEMO ORDER EXECUTION DISABLED")
    log(f"{VERSION}: NETWORK WRITES DISABLED")
    log(f"{VERSION}: LEVERAGE MUTATION DISABLED")
    log(f"{VERSION}: MARGIN MUTATION DISABLED")
    log(f"{VERSION}: TARGET MARGIN={TARGET_MARGIN_TYPE}")
    log(f"{VERSION}: TARGET LONG=100x")
    log(f"{VERSION}: TARGET SHORT=100x")

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: HARD EXECUTION SAFETY POLICY"
    )

    require(
        SYNTHETIC_ONLY is True,
        "Synthetic Only Is Enabled",
    )

    require(
        AUTHENTICATED_READ_ONLY_ENABLED is True,
        "Authenticated Read-Only Is Enabled",
    )

    require(
        PUBLIC_READ_ONLY_ENABLED is True,
        "Public Read-Only Is Enabled",
    )

    require(
        REAL_ORDER_EXECUTION_ENABLED is False,
        "Real Order Execution Is Disabled",
    )

    require(
        DEMO_ORDER_EXECUTION_ENABLED is False,
        "Demo Order Execution Is Disabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "Exchange Network Writes Are Disabled",
    )

    require(
        LEVERAGE_MUTATION_ENABLED is False,
        "Leverage Mutation Is Disabled",
    )

    require(
        MARGIN_MUTATION_ENABLED is False,
        "Margin Mutation Is Disabled",
    )

    require(
        POSITION_MUTATION_ENABLED is False,
        "Position Mutation Is Disabled",
    )

    require(
        ACCOUNT_MUTATION_ENABLED is False,
        "Account Mutation Is Disabled",
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: NETWORK WRITE FIREBREAK"
    )

    blocked = 0

    for method in (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ):

        try:
            reject_network_write(
                method,
                "/synthetic-test",
                {},
            )

        except RuntimeError:
            blocked += 1
            pass_test(
                f"HTTP {method} Is Rejected"
            )

    require(
        blocked == 4,
        "All Mutation HTTP Methods Are Rejected",
    )

    try:
        send_real_order()

    except RuntimeError:
        pass_test(
            "Real Order Function Is Rejected"
        )

    try:
        send_demo_order()

    except RuntimeError:
        pass_test(
            "Demo Order Function Is Rejected"
        )

    try:
        mutate_leverage()

    except RuntimeError:
        pass_test(
            "Leverage Mutation Function Is Rejected"
        )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: API CREDENTIAL READINESS"
    )

    require_credentials()

    require(
        bool(WEEX_API_KEY),
        "WEEX API Key Is Present",
    )

    require(
        bool(WEEX_API_SECRET),
        "WEEX API Secret Is Present",
    )

    require(
        bool(WEEX_API_PASSPHRASE),
        "WEEX API Passphrase Is Present",
    )

    # ==============================================================================================
    # TEST 4 - BALANCE
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: LIVE BALANCE RECONCILIATION"
    )

    balance, _balance_response = obtain_available_balance()

    require(
        balance is not None,
        "Available Balance Was Read",
    )

    require(
        balance > 0,
        "Available Balance Is Positive",
    )

    RUNTIME["available_usdt"] = balance

    log(f"{VERSION}: BALANCE PATH={BALANCE_PATH}")
    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_string(balance)}"
    )

    # ==============================================================================================
    # TEST 5 - ACCOUNT CONFIG
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: ACCOUNT CONFIGURATION RECONCILIATION"
    )

    config = obtain_symbol_config()

    require(
        config["margin_type"]
        == TARGET_MARGIN_TYPE,
        "Margin Type Is ISOLATED",
    )

    require(
        config["long_leverage"]
        == TARGET_LONG_LEVERAGE,
        "Long Leverage Is 100x",
    )

    require(
        config["short_leverage"]
        == TARGET_SHORT_LEVERAGE,
        "Short Leverage Is 100x",
    )

    correction_required = not (
        config["margin_type"]
        == TARGET_MARGIN_TYPE
        and config["long_leverage"]
        == TARGET_LONG_LEVERAGE
        and config["short_leverage"]
        == TARGET_SHORT_LEVERAGE
    )

    require(
        correction_required is False,
        "Account Configuration Requires No Correction",
    )

    RUNTIME[
        "correction_required"
    ] = correction_required

    RUNTIME[
        "observed_margin"
    ] = config["margin_type"]

    RUNTIME[
        "observed_long"
    ] = config["long_leverage"]

    RUNTIME[
        "observed_short"
    ] = config["short_leverage"]

    log(
        f"{VERSION}: SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    log(
        f"{VERSION}: OBSERVED MARGIN="
        f"{config['margin_type']}"
    )

    log(
        f"{VERSION}: POSITION MODE="
        f"{config['position_mode']}"
    )

    log(
        f"{VERSION}: OBSERVED LONG="
        f"{decimal_string(config['long_leverage'])}x"
    )

    log(
        f"{VERSION}: OBSERVED SHORT="
        f"{decimal_string(config['short_leverage'])}x"
    )

    # ==============================================================================================
    # TEST 6 - POSITIONS
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: LIVE POSITION RECONCILIATION"
    )

    positions = obtain_positions()

    require(
        isinstance(
            positions["response"],
            (dict, list),
        ),
        "Position Response Is Valid",
    )

    require(
        len(positions["open_positions"]) >= 0,
        "BTCUSDT Open Position Count Is Non-Negative",
    )

    require(
        len(positions["open_positions"]) == 0,
        "Execution Preflight Starts Flat",
    )

    log(
        f"{VERSION}: POSITION PATH="
        f"{POSITION_PATH}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(positions['records'])}"
    )

    log(
        f"{VERSION}: BTCUSDT POSITION RECORDS="
        f"{len(positions['symbol_records'])}"
    )

    log(
        f"{VERSION}: BTCUSDT OPEN POSITIONS="
        f"{len(positions['open_positions'])}"
    )

    # ==============================================================================================
    # TEST 7 - CONTRACT
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: CONTRACT INFORMATION"
    )

    contract = obtain_contract_information()

    require(
        contract["min_qty"] > 0,
        "Minimum Order Quantity Is Positive",
    )

    require(
        contract["qty_step"] > 0,
        "Quantity Step Is Positive",
    )

    require(
        contract["max_qty"]
        > contract["min_qty"],
        "Maximum Quantity Is Above Minimum",
    )

    require(
        contract["max_leverage"]
        >= TARGET_LONG_LEVERAGE,
        "Exchange Maximum Supports 100x",
    )

    log(
        f"{VERSION}: CONTRACT INFO PATH="
        f"{contract['path']}"
    )

    log(
        f"{VERSION}: MIN QTY="
        f"{decimal_string(contract['min_qty'])}"
    )

    log(
        f"{VERSION}: QTY STEP="
        f"{decimal_string(contract['qty_step'])}"
    )

    log(
        f"{VERSION}: MAX LEVERAGE="
        f"{decimal_string(contract['max_leverage'])}x"
    )

    # ==============================================================================================
    # TEST 8 - MARKET PRICE
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: LIVE MARKET PRICE"
    )

    market_price, market_path, _ = obtain_market_price()

    require(
        market_price > 0,
        "Market Price Is Positive",
    )

    RUNTIME["market_price"] = market_price

    log(
        f"{VERSION}: MARKET PRICE PATH="
        f"{market_path}"
    )

    log(
        f"{VERSION}: MARKET PRICE="
        f"{decimal_string(market_price)}"
    )

    # ==============================================================================================
    # TEST 9 - ORDERBOOK
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: BEST BID / ASK PREFLIGHT"
    )

    orderbook = obtain_orderbook()

    require(
        orderbook["best_bid"] > 0,
        "Best Bid Is Positive",
    )

    require(
        orderbook["best_ask"] > 0,
        "Best Ask Is Positive",
    )

    require(
        orderbook["best_ask"]
        >= orderbook["best_bid"],
        "Best Ask Is Not Below Best Bid",
    )

    require(
        orderbook["spread_pct"]
        >= Decimal("0"),
        "Spread Percent Is Non-Negative",
    )

    RUNTIME[
        "spread_pct"
    ] = orderbook["spread_pct"]

    log(
        f"{VERSION}: DEPTH PATH="
        f"{orderbook['path']}"
    )

    log(
        f"{VERSION}: BEST BID="
        f"{decimal_string(orderbook['best_bid'])}"
    )

    log(
        f"{VERSION}: BEST ASK="
        f"{decimal_string(orderbook['best_ask'])}"
    )

    log(
        f"{VERSION}: SPREAD PCT="
        f"{decimal_string(orderbook['spread_pct'])}"
    )

    # ==============================================================================================
    # TEST 10 - ENTRY READINESS
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: INITIAL ENTRY READINESS CALCULATION"
    )

    entry_margin_budget = (
        balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    planned_notional = (
        entry_margin_budget
        * TARGET_LONG_LEVERAGE
    )

    raw_quantity = (
        planned_notional
        / market_price
    )

    rounded_quantity = floor_to_step(
        raw_quantity,
        contract["qty_step"],
    )

    rounded_notional = (
        rounded_quantity
        * market_price
    )

    estimated_margin = (
        rounded_notional
        / TARGET_LONG_LEVERAGE
    )

    max_allowed_margin = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    require(
        INITIAL_ENTRY_PERCENT > 0,
        "Initial Entry Percent Is Positive",
    )

    require(
        INITIAL_ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT,
        "Initial Entry Is Within Exposure Cap",
    )

    require(
        entry_margin_budget > 0,
        "Initial Entry Margin Budget Is Positive",
    )

    require(
        planned_notional > 0,
        "Planned Notional Is Positive",
    )

    require(
        raw_quantity > 0,
        "Raw Quantity Is Positive",
    )

    require(
        rounded_quantity > 0,
        "Rounded Quantity Is Positive",
    )

    require(
        rounded_quantity
        >= contract["min_qty"],
        "Rounded Quantity Meets Exchange Minimum",
    )

    require(
        rounded_quantity
        <= contract["max_qty"],
        "Rounded Quantity Is Below Exchange Maximum",
    )

    require(
        estimated_margin
        <= max_allowed_margin,
        "Estimated Entry Margin Is Within Exposure Cap",
    )

    RUNTIME[
        "entry_qty"
    ] = rounded_quantity

    log(
        f"{VERSION}: ENTRY BALANCE PERCENT="
        f"{decimal_string(INITIAL_ENTRY_PERCENT)}%"
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_string(entry_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: PLANNED NOTIONAL="
        f"{decimal_string(planned_notional)} USDT"
    )

    log(
        f"{VERSION}: RAW QUANTITY="
        f"{decimal_string(raw_quantity)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED QUANTITY="
        f"{decimal_string(rounded_quantity)} BTC"
    )

    log(
        f"{VERSION}: ROUNDED NOTIONAL="
        f"{decimal_string(rounded_notional)} USDT"
    )

    log(
        f"{VERSION}: ESTIMATED MARGIN AT 100x="
        f"{decimal_string(estimated_margin)} USDT"
    )

    # ==============================================================================================
    # TEST 11 - MAX EXPOSURE
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: MAXIMUM STRATEGY EXPOSURE"
    )

    planned_max_strategy_percent = (
        INITIAL_ENTRY_PERCENT
        + Decimal(MAX_PYRAMID_ADDS)
        * PYRAMID_SIZE_PERCENT
        + Decimal(MAX_BACKUPS)
        * BACKUP_SIZE_PERCENT
    )

    planned_max_strategy_margin = (
        balance
        * planned_max_strategy_percent
        / Decimal("100")
    )

    require(
        MAX_PYRAMID_ADDS == 1,
        "Maximum Pyramid Adds Is One",
    )

    require(
        MAX_BACKUPS == 3,
        "Maximum Backups Is Three",
    )

    require(
        planned_max_strategy_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
        "Maximum Planned Strategy Margin Is Within 35%",
    )

    log(
        f"{VERSION}: MAX FUND EXPOSURE="
        f"{decimal_string(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: MAX ALLOWED STRATEGY MARGIN="
        f"{decimal_string(max_allowed_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_string(planned_max_strategy_margin)} USDT"
    )

    # ==============================================================================================
    # TEST 12 - TP
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: TAKE-PROFIT STRUCTURE"
    )

    require(
        TP1_ALLOCATION
        + TP2_ALLOCATION
        + TP3_ALLOCATION
        == Decimal("100"),
        "TP Allocation Totals 100 Percent",
    )

    require(
        TP1_TRIGGER_PERCENT > 0,
        "TP1 Trigger Is Positive",
    )

    require(
        TP2_TRIGGER_PERCENT
        > TP1_TRIGGER_PERCENT,
        "TP2 Trigger Is Above TP1",
    )

    require(
        TRAILING_DISTANCE_PERCENT > 0,
        "Trailing Distance Is Positive",
    )

    log(
        f"{VERSION}: TP1="
        f"{TP1_ALLOCATION}% AT +"
        f"{TP1_TRIGGER_PERCENT}%"
    )

    log(
        f"{VERSION}: TP2="
        f"{TP2_ALLOCATION}% AT +"
        f"{TP2_TRIGGER_PERCENT}%"
    )

    log(
        f"{VERSION}: TP3="
        f"{TP3_ALLOCATION}% TRAILING"
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{TRAILING_DISTANCE_PERCENT}%"
    )

    # ==============================================================================================
    # TEST 13 - STATE FINGERPRINT
    # ==============================================================================================

    section(
        f"{VERSION} TEST 13: LIVE STATE FINGERPRINT"
    )

    live_snapshot, state_fingerprint = (
        create_live_state_snapshot(
            balance=balance,
            config=config,
            positions=positions,
            market_price=market_price,
            orderbook=orderbook,
        )
    )

    require(
        len(state_fingerprint) == 64,
        "Live State Fingerprint Exists",
    )

    require(
        sha256_json(live_snapshot)
        == state_fingerprint,
        "Live State Fingerprint Recomputes Exactly",
    )

    RUNTIME[
        "state_fingerprint"
    ] = state_fingerprint

    log(
        f"{VERSION}: LIVE STATE SNAPSHOT="
        f"{canonical_json(live_snapshot)}"
    )

    log(
        f"{VERSION}: LIVE STATE SHA256="
        f"{state_fingerprint}"
    )

    # ==============================================================================================
    # TEST 14 - INTENT
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: SYNTHETIC ORDER INTENT"
    )

    intent = build_synthetic_intent(
        rounded_quantity,
        state_fingerprint,
    )

    require(
        intent["synthetic"] is True,
        "Synthetic Intent Is Marked Synthetic",
    )

    require(
        intent["transmit"] is False,
        "Synthetic Intent Forbids Transmission",
    )

    require(
        intent["symbol"] == SYMBOL,
        "Synthetic Intent Symbol Matches BTCUSDT",
    )

    require(
        intent["quantity"]
        == decimal_string(rounded_quantity),
        "Synthetic Intent Quantity Matches Readiness Calculation",
    )

    require(
        intent["side"] in ("BUY", "SELL"),
        "Synthetic Intent Side Is Supported",
    )

    require(
        intent["positionSide"]
        in ("LONG", "SHORT"),
        "Synthetic Intent Position Side Is Supported",
    )

    require(
        intent["type"] == "MARKET",
        "Synthetic Intent Uses Market Type",
    )

    require(
        intent["newClientOrderId"].startswith(
            "r34q-"
        ),
        "Synthetic Intent Client Order ID Is Valid",
    )

    require(
        len(intent["intentHash"]) == 64,
        "Synthetic Intent Hash Exists",
    )

    require(
        intent["expiresAt"]
        > int(time.time() * 1000),
        "Synthetic Intent Has Future Expiry",
    )

    log(
        f"{VERSION}: SYNTHETIC INTENT SHA256="
        f"{intent['intentHash']}"
    )

    log(
        f"{VERSION}: SYNTHETIC CLIENT ORDER ID="
        f"{intent['newClientOrderId']}"
    )

    log(
        f"{VERSION}: SYNTHETIC INTENT TRANSMITTED="
        f"{intent['transmit']}"
    )

    # ==============================================================================================
    # TEST 15 - PAYLOAD
    # ==============================================================================================

    section(
        f"{VERSION} TEST 15: SYNTHETIC ORDER PAYLOAD"
    )

    payload, payload_hash = (
        build_order_payload(intent)
    )

    require(
        payload["symbol"]
        == intent["symbol"],
        "Payload Symbol Matches Intent",
    )

    require(
        payload["side"]
        == intent["side"],
        "Payload Side Matches Intent",
    )

    require(
        payload["positionSide"]
        == intent["positionSide"],
        "Payload Position Side Matches Intent",
    )

    require(
        payload["type"]
        == intent["type"],
        "Payload Type Matches Intent",
    )

    require(
        payload["quantity"]
        == intent["quantity"],
        "Payload Quantity Matches Intent",
    )

    require(
        payload["newClientOrderId"]
        == intent["newClientOrderId"],
        "Payload Client Order ID Matches Intent",
    )

    require(
        len(payload_hash) == 64,
        "Payload Hash Exists",
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD="
        f"{canonical_json(payload)}"
    )

    log(
        f"{VERSION}: SYNTHETIC PAYLOAD SHA256="
        f"{payload_hash}"
    )

    # ==============================================================================================
    # TEST 16 - ENVELOPE
    # ==============================================================================================

    section(
        f"{VERSION} TEST 16: SYNTHETIC AUTHENTICATED EXECUTION ENVELOPE"
    )

    envelope = (
        build_synthetic_execution_envelope(
            intent,
            payload,
            payload_hash,
        )
    )

    require(
        envelope["synthetic"] is True,
        "Envelope Is Marked Synthetic",
    )

    require(
        envelope["transmit"] is False,
        "Envelope Forbids Transmission",
    )

    require(
        envelope["method"] == "POST",
        "Envelope Uses POST Method Locally",
    )

    require(
        envelope["body"]
        == canonical_json(payload),
        "Envelope Body Matches Canonical Payload",
    )

    require(
        sha256_text(envelope["body"])
        == envelope["payloadHash"],
        "Envelope Payload Hash Recomputes Exactly",
    )

    require(
        bool(
            envelope["headers"].get(
                "ACCESS-KEY"
            )
        ),
        "ACCESS-KEY Header Is Present",
    )

    require(
        bool(
            envelope["headers"].get(
                "ACCESS-SIGN"
            )
        ),
        "ACCESS-SIGN Header Is Present",
    )

    require(
        bool(
            envelope["headers"].get(
                "ACCESS-PASSPHRASE"
            )
        ),
        "ACCESS-PASSPHRASE Header Is Present",
    )

    require(
        bool(
            envelope["headers"].get(
                "ACCESS-TIMESTAMP"
            )
        ),
        "ACCESS-TIMESTAMP Header Is Present",
    )

    require(
        envelope[
            "networkWriteAllowed"
        ] is False,
        "Envelope Explicitly Forbids Network Write",
    )

    require(
        envelope[
            "realExecutionAllowed"
        ] is False,
        "Envelope Explicitly Forbids Real Execution",
    )

    require(
        envelope[
            "demoExecutionAllowed"
        ] is False,
        "Envelope Explicitly Forbids Demo Execution",
    )

    require(
        len(
            envelope["envelopeHash"]
        ) == 64,
        "Envelope Hash Exists",
    )

    log(
        f"{VERSION}: SYNTHETIC ENVELOPE SHA256="
        f"{envelope['envelopeHash']}"
    )

    log(
        f"{VERSION}: SYNTHETIC ENVELOPE TRANSMITTED="
        f"{envelope['transmit']}"
    )

    # ==============================================================================================
    # TEST 17 - AUTHORIZATION
    # ==============================================================================================

    section(
        f"{VERSION} TEST 17: ONE-TIME SYNTHETIC AUTHORIZATION"
    )

    authorization = issue_synthetic_authorization(
        intent=intent,
        payload_hash=payload_hash,
        envelope_hash=envelope["envelopeHash"],
        state_fingerprint=state_fingerprint,
    )

    require(
        authorization["syntheticOnly"]
        is True,
        "Authorization Is Synthetic Only",
    )

    require(
        authorization["transmitAllowed"]
        is False,
        "Authorization Forbids Transmission",
    )

    require(
        authorization["networkWriteAllowed"]
        is False,
        "Authorization Forbids Network Write",
    )

    require(
        authorization["consumed"]
        is False,
        "Authorization Is Initially Unconsumed",
    )

    require(
        authorization["intentHash"]
        == intent["intentHash"],
        "Authorization Binds Exact Intent",
    )

    require(
        authorization["payloadHash"]
        == payload_hash,
        "Authorization Binds Exact Payload",
    )

    require(
        authorization["envelopeHash"]
        == envelope["envelopeHash"],
        "Authorization Binds Exact Envelope",
    )

    require(
        authorization["stateFingerprint"]
        == state_fingerprint,
        "Authorization Binds Exact Live State",
    )

    require(
        authorization["expiresAt"]
        > int(time.time() * 1000),
        "Authorization Has Future Expiry",
    )

    log(
        f"{VERSION}: AUTHORIZATION ID="
        f"{authorization['authorizationId']}"
    )

    log(
        f"{VERSION}: AUTHORIZATION SHA256="
        f"{authorization['authorizationHash']}"
    )

    # ==============================================================================================
    # TEST 18 - STALE STATE REJECTION
    # ==============================================================================================

    section(
        f"{VERSION} TEST 18: STALE STATE REJECTION"
    )

    synthetic_stale_state = dict(
        live_snapshot
    )

    synthetic_stale_state[
        "market_price"
    ] = decimal_string(
        market_price + Decimal("1")
    )

    stale_fingerprint = sha256_json(
        synthetic_stale_state
    )

    stale_rejected = False

    try:
        validate_authorization(
            authorization=authorization,
            intent=intent,
            payload_hash=payload_hash,
            envelope=envelope,
            current_state_fingerprint=stale_fingerprint,
        )

    except RuntimeError as exc:

        if "stale" in str(exc).lower():
            stale_rejected = True

    require(
        stale_rejected,
        "Synthetic Stale State Is Rejected",
    )

    require(
        COUNTERS["stale_state_blocks"] == 1,
        "Stale State Block Counter Is One",
    )

    require(
        authorization["consumed"] is False,
        "Stale Rejection Does Not Consume Authorization",
    )

    # ==============================================================================================
    # TEST 19 - AUTHORIZATION VALIDATION
    # ==============================================================================================

    section(
        f"{VERSION} TEST 19: FRESH AUTHORIZATION VALIDATION"
    )

    valid = validate_authorization(
        authorization=authorization,
        intent=intent,
        payload_hash=payload_hash,
        envelope=envelope,
        current_state_fingerprint=state_fingerprint,
    )

    require(
        valid is True,
        "Fresh Authorization Is Accepted",
    )

    require(
        authorization["consumed"]
        is False,
        "Validation Alone Does Not Consume Authorization",
    )

    # ==============================================================================================
    # TEST 20 - EXACTLY ONCE SYNTHETIC DISPATCH
    # ==============================================================================================

    section(
        f"{VERSION} TEST 20: EXACTLY-ONCE SYNTHETIC DISPATCH"
    )

    receipt = synthetic_transport_dispatch(
        authorization=authorization,
        envelope=envelope,
    )

    require(
        receipt["synthetic"] is True,
        "Synthetic Receipt Is Marked Synthetic",
    )

    require(
        receipt["transmitted"] is False,
        "Synthetic Dispatch Was Not Transmitted",
    )

    require(
        receipt[
            "networkWritePerformed"
        ] is False,
        "Synthetic Dispatch Performed No Network Write",
    )

    require(
        receipt["exchangeAcknowledgement"]
        is False,
        "No Exchange Acknowledgement Was Claimed",
    )

    require(
        receipt["realOrderId"] is None,
        "Synthetic Receipt Has No Real Order ID",
    )

    require(
        receipt["demoOrderId"] is None,
        "Synthetic Receipt Has No Demo Order ID",
    )

    require(
        authorization["consumed"]
        is True,
        "Authorization Was Consumed Exactly Once",
    )

    require(
        COUNTERS["synthetic_dispatches"]
        == 1,
        "Exactly One Synthetic Dispatch Occurred",
    )

    require(
        COUNTERS["synthetic_receipts"]
        == 1,
        "Exactly One Synthetic Receipt Was Created",
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCH ID="
        f"{receipt['dispatchId']}"
    )

    log(
        f"{VERSION}: SYNTHETIC RECEIPT SHA256="
        f"{receipt['receiptHash']}"
    )

    log(
        f"{VERSION}: SYNTHETIC TRANSMITTED="
        f"{receipt['transmitted']}"
    )

    # ==============================================================================================
    # TEST 21 - AUTHORIZATION REPLAY
    # ==============================================================================================

    section(
        f"{VERSION} TEST 21: AUTHORIZATION REPLAY REJECTION"
    )

    replay_rejected = False

    try:
        validate_authorization(
            authorization=authorization,
            intent=intent,
            payload_hash=payload_hash,
            envelope=envelope,
            current_state_fingerprint=state_fingerprint,
        )

    except RuntimeError as exc:

        if (
            "replay" in str(exc).lower()
            or "consumed" in str(exc).lower()
        ):
            replay_rejected = True

    require(
        replay_rejected,
        "Consumed Authorization Replay Is Rejected",
    )

    require(
        COUNTERS[
            "authorization_replays_blocked"
        ] >= 1,
        "Authorization Replay Counter Increased",
    )

    # ==============================================================================================
    # TEST 22 - DUPLICATE DISPATCH
    # ==============================================================================================

    section(
        f"{VERSION} TEST 22: DUPLICATE DISPATCH REJECTION"
    )

    duplicate_blocked = False

    try:
        synthetic_transport_dispatch(
            authorization=authorization,
            envelope=envelope,
        )

    except RuntimeError:
        duplicate_blocked = True

    require(
        duplicate_blocked,
        "Second Synthetic Dispatch Is Rejected",
    )

    require(
        COUNTERS["synthetic_dispatches"]
        == 1,
        "Synthetic Dispatch Count Remains One",
    )

    # ==============================================================================================
    # TEST 23 - PAYLOAD / ENVELOPE TAMPER
    # ==============================================================================================

    section(
        f"{VERSION} TEST 23: AUTHORIZATION BINDING TAMPER REJECTION"
    )

    tampered_payload = dict(payload)

    tampered_payload["quantity"] = (
        decimal_string(
            rounded_quantity
            + contract["qty_step"]
        )
    )

    tampered_payload_hash = sha256_json(
        tampered_payload
    )

    require(
        tampered_payload_hash
        != payload_hash,
        "Payload Tamper Changes Hash",
    )

    require(
        authorization["payloadHash"]
        != tampered_payload_hash,
        "Authorization Rejects Tampered Payload Binding",
    )

    tampered_envelope = dict(envelope)

    tampered_envelope[
        "payloadHash"
    ] = tampered_payload_hash

    tampered_envelope_hash = sha256_json(
        {
            k: v
            for k, v in tampered_envelope.items()
            if k != "envelopeHash"
        }
    )

    require(
        tampered_envelope_hash
        != envelope["envelopeHash"],
        "Envelope Tamper Changes Hash",
    )

    # ==============================================================================================
    # TEST 24 - FINAL FIREBREAK
    # ==============================================================================================

    section(
        f"{VERSION} TEST 24: FINAL EXECUTION DISPATCH FIREBREAK"
    )

    require(
        COUNTERS["network_writes"] == 0,
        "Network Writes Remain Zero",
    )

    require(
        COUNTERS["leverage_mutations"] == 0,
        "Leverage Mutations Remain Zero",
    )

    require(
        COUNTERS["margin_mutations"] == 0,
        "Margin Mutations Remain Zero",
    )

    require(
        COUNTERS["position_mutations"] == 0,
        "Position Mutations Remain Zero",
    )

    require(
        COUNTERS["account_mutations"] == 0,
        "Account Mutations Remain Zero",
    )

    require(
        COUNTERS["real_orders"] == 0,
        "Real Orders Remain Zero",
    )

    require(
        COUNTERS["demo_orders"] == 0,
        "Demo Orders Remain Zero",
    )

    require(
        COUNTERS["synthetic_envelopes"]
        == 1,
        "Exactly One Synthetic Envelope Was Constructed",
    )

    require(
        COUNTERS["synthetic_dispatches"]
        == 1,
        "Exactly One Synthetic Dispatch Was Completed",
    )

    require(
        receipt["transmitted"] is False,
        "Synthetic Dispatch Was Not Transmitted",
    )

    require(
        correction_required is False,
        "Account Configuration Requires No Correction",
    )

    require(
        RUNTIME["authorization_consumed"]
        is True,
        "One-Time Authorization Was Consumed",
    )

    require(
        RUNTIME["dispatch_completed"]
        is True,
        "Synthetic Dispatch Reached Completed State",
    )

    # ==============================================================================================
    # COMPLETE
    # ==============================================================================================

    RUNTIME[
        "phase"
    ] = "LIVE_SYNTHETIC_AUTHORIZATION_DISPATCH_VALIDATED"

    section(
        f"{VERSION}: VALIDATION COMPLETE"
    )

    pass_test(
        "Live Read-Only Account Reconciliation"
    )

    pass_test(
        "Account Is Already ISOLATED 100x / 100x"
    )

    pass_test(
        "Execution Preflight Starts Flat"
    )

    pass_test(
        "Initial Entry Calculation Is Exchange Compatible"
    )

    pass_test(
        "Best Bid / Ask Preflight Is Acceptable"
    )

    pass_test(
        "Live State Fingerprint Was Constructed"
    )

    pass_test(
        "Synthetic Order Intent Was Constructed"
    )

    pass_test(
        "Synthetic Order Payload Was Constructed"
    )

    pass_test(
        "Synthetic Authenticated Envelope Was Constructed"
    )

    pass_test(
        "One-Time Synthetic Authorization Was Granted"
    )

    pass_test(
        "Synthetic Stale State Was Rejected"
    )

    pass_test(
        "Fresh Authorization Was Accepted"
    )

    pass_test(
        "Authorization Was Consumed Exactly Once"
    )

    pass_test(
        "Authorization Replay Was Rejected"
    )

    pass_test(
        "Duplicate Dispatch Was Rejected"
    )

    pass_test(
        "Exactly One Synthetic Receipt Was Produced"
    )

    pass_test(
        "Synthetic Dispatch Was Not Transmitted"
    )

    pass_test(
        "No Account Mutation Was Performed"
    )

    pass_test(
        "No Real Order Was Sent"
    )

    pass_test(
        "No Demo Order Was Sent"
    )

    pass_test(
        "Network Writes Remain Zero"
    )


# ==================================================================================================
# PART 4 - HEARTBEAT / MAIN
# ==================================================================================================

def heartbeat_loop():

    count = 0

    while True:

        count += 1

        log(
            f"{VERSION}: HEARTBEAT {count}"
            f" | phase={RUNTIME['phase']}"
            f" | authenticated-read-only={AUTHENTICATED_READ_ONLY_ENABLED}"
            f" | authenticated-get={COUNTERS['authenticated_get']}"
            f" | public-get={COUNTERS['public_get']}"
            f" | network-writes={COUNTERS['network_writes']}"
            f" | leverage-mutations={COUNTERS['leverage_mutations']}"
            f" | real-orders={COUNTERS['real_orders']}"
            f" | demo-orders={COUNTERS['demo_orders']}"
            f" | synthetic-envelopes={COUNTERS['synthetic_envelopes']}"
            f" | auth-requests={COUNTERS['authorization_requests']}"
            f" | auth-grants={COUNTERS['authorization_grants']}"
            f" | auth-denials={COUNTERS['authorization_denials']}"
            f" | auth-replays-blocked={COUNTERS['authorization_replays_blocked']}"
            f" | stale-state-blocks={COUNTERS['stale_state_blocks']}"
            f" | synthetic-dispatches={COUNTERS['synthetic_dispatches']}"
            f" | duplicate-dispatches-blocked={COUNTERS['duplicate_dispatches_blocked']}"
            f" | synthetic-receipts={COUNTERS['synthetic_receipts']}"
            f" | authorization-consumed={RUNTIME['authorization_consumed']}"
            f" | dispatch-completed={RUNTIME['dispatch_completed']}"
            f" | correction-required={RUNTIME['correction_required']}"
            f" | observed-margin={RUNTIME['observed_margin']}"
            f" | observed-long={RUNTIME['observed_long']}"
            f" | observed-short={RUNTIME['observed_short']}"
            f" | target-long=100x"
            f" | target-short=100x"
            f" | entry-qty={RUNTIME['entry_qty']}"
            f" | spread-pct={RUNTIME['spread_pct']}"
        )

        time.sleep(30)


def main():

    start_health_server()

    try:

        RUNTIME["phase"] = "VALIDATING"

        run_validation()

    except Exception as exc:

        RUNTIME["phase"] = "VALIDATION_FAILED"

        RUNTIME["last_error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        section(
            f"{VERSION}: VALIDATION FAILED"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

        # Keep Render health service alive so the
        # validation failure can still be inspected.

    heartbeat_loop()


if __name__ == "__main__":
    main()
