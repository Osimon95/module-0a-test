

import os
import json
import time
import hmac
import hashlib
import socket
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from decimal import Decimal, ROUND_DOWN, InvalidOperation


# ==================================================================================================
# R35P-H
# LIVE READ-ONLY RECONCILIATION + SYNTHETIC ENTRY CALCULATION
#
# SAFETY:
# - NO REAL ORDER EXECUTION
# - NO DEMO ORDER EXECUTION
# - NO EXCHANGE MUTATION TRANSPORT
# - NO ORDER SUBMISSION
# - NO LEVERAGE MUTATION
# - NO MARGIN MODE MUTATION
# - NO POSITION MUTATION
#
# PURPOSE:
# 1. Preserve R35P-G verified symbol reconciliation:
#       canonical strategy symbol = BTCUSDT
#       V2 public market symbol    = cmt_btcusdt
#       V3 authenticated symbol   = BTCUSDT
#
# 2. Read:
#       DNS
#       public mark price
#       balance
#       position
#       symbol configuration
#
# 3. Verify activation environment.
#
# 4. Calculate initial 5% strategy entry using live balance and mark price.
#
# 5. Apply quantity-step / minimum-quantity / exposure checks.
#
# 6. Construct SYNTHETIC order payload only.
#
# 7. Absolutely no exchange write transport exists in this unit.
# ==================================================================================================


VERSION = "R35P-H"

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"

CANONICAL_SYMBOL = "BTCUSDT"
V2_MARKET_SYMBOL = "cmt_btcusdt"
V3_AUTH_SYMBOL = "BTCUSDT"

MARK_PRICE_PATH = "/capi/v2/market/ticker"
BALANCE_PATH = "/capi/v3/account/balance"
POSITION_PATH = "/capi/v3/account/position/singlePosition"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = Decimal("100")
TARGET_SHORT_LEVERAGE = Decimal("100")

ENTRY_BALANCE_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
QTY_PRECISION = 4

PRICE_STEP = Decimal("0.1")
PRICE_PRECISION = 1

MAX_PYRAMID_ADDS = 1
PYRAMID_PERCENT = Decimal("5")

MAX_BACKUPS = 3
BACKUP_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# ==================================================================================================
# HARD SAFETY FIREBREAK
# ==================================================================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False
ORDER_SUBMISSION_ENABLED = False
LEVERAGE_MUTATION_ENABLED = False
MARGIN_MODE_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

PUBLIC_MARKET_GETS = 0
AUTHENTICATED_WEEX_READS = 0

SYNTHETIC_PAYLOADS_CREATED = 0

FAILURE_STAGE = None
EXCEPTION_CLASS = None
EXCEPTION_MESSAGE = None


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

HEALTH_PORT = int(os.getenv("PORT", "10000"))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = (
            f"{VERSION} OK\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    def runner():
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
        server.serve_forever()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    log(f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}")


# ==================================================================================================
# LOGGING
# ==================================================================================================

SEPARATOR = "-" * 100


def now():
    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(f"{now()} {message}", flush=True)


def section(title):
    log(SEPARATOR)
    log(f"{VERSION}: {title}")
    log(SEPARATOR)


# ==================================================================================================
# DECIMAL HELPERS
# ==================================================================================================

def D(value, default=None):
    try:
        if value is None:
            return default
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def decimal_text(value):
    if value is None:
        return "UNKNOWN"

    if not isinstance(value, Decimal):
        value = D(value)

    if value is None:
        return "UNKNOWN"

    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def quantize_down(value, step):
    value = D(value)
    step = D(step)

    if value is None or step is None or step <= 0:
        return None

    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


# ==================================================================================================
# JSON / RESPONSE HELPERS
# ==================================================================================================

def decode_json(raw):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")

    return json.loads(raw)


def find_first_number(obj, candidate_keys):
    if isinstance(obj, dict):
        for key in candidate_keys:
            if key in obj:
                value = D(obj.get(key))
                if value is not None:
                    return value

        for value in obj.values():
            found = find_first_number(value, candidate_keys)
            if found is not None:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = find_first_number(item, candidate_keys)
            if found is not None:
                return found

    return None


def find_first_string(obj, candidate_keys):
    if isinstance(obj, dict):
        for key in candidate_keys:
            if key in obj:
                value = obj.get(key)
                if value is not None:
                    return str(value)

        for value in obj.values():
            found = find_first_string(value, candidate_keys)
            if found is not None:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = find_first_string(item, candidate_keys)
            if found is not None:
                return found

    return None


def list_candidate_records(obj):
    records = []

    if isinstance(obj, list):
        records.extend(obj)

    elif isinstance(obj, dict):
        for key in (
            "data",
            "result",
            "rows",
            "list",
            "positions",
            "assets",
            "balances",
        ):
            value = obj.get(key)

            if isinstance(value, list):
                records.extend(value)

            elif isinstance(value, dict):
                records.append(value)

        if not records:
            records.append(obj)

    return records


# ==================================================================================================
# CREDENTIALS
# ==================================================================================================

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()


def credentials_present():
    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )


# ==================================================================================================
# HTTP GET ONLY
# ==================================================================================================

def public_get(path, params=None):
    global PUBLIC_MARKET_GETS

    params = params or {}

    query = urlencode(params)
    url = WEEX_CONTRACT_BASE + path

    if query:
        url += "?" + query

    req = Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}/1.0",
        },
    )

    with urlopen(req, timeout=15) as response:
        raw = response.read()
        status = response.getcode()

    PUBLIC_MARKET_GETS += 1

    return status, decode_json(raw)


def weex_signature(timestamp, method, request_path, query_string=""):
    prehash = (
        str(timestamp)
        + method.upper()
        + request_path
        + query_string
    )

    return hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def authenticated_get(path, params=None):
    global AUTHENTICATED_WEEX_READS

    if not credentials_present():
        raise RuntimeError("WEEX credentials missing")

    params = params or {}

    query = urlencode(params)

    request_path_for_signature = path

    timestamp = str(int(time.time() * 1000))

    signature = weex_signature(
        timestamp=timestamp,
        method="GET",
        request_path=request_path_for_signature,
        query_string=query,
    )

    url = WEEX_CONTRACT_BASE + path

    if query:
        url += "?" + query

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "User-Agent": f"{VERSION}/1.0",
    }

    req = Request(
        url=url,
        method="GET",
        headers=headers,
    )

    with urlopen(req, timeout=15) as response:
        raw = response.read()
        status = response.getcode()

    AUTHENTICATED_WEEX_READS += 1

    return status, decode_json(raw)


# ==================================================================================================
# PUBLIC MARK PRICE
# ==================================================================================================

def read_mark_price():
    status, payload = public_get(
        MARK_PRICE_PATH,
        {
            "symbol": V2_MARKET_SYMBOL,
        },
    )

    response_symbol = find_first_string(
        payload,
        [
            "symbol",
        ],
    )

    mark_price = find_first_number(
        payload,
        [
            "markPrice",
            "mark_price",
            "price",
            "last",
            "lastPrice",
        ],
    )

    symbol_match = (
        response_symbol is not None
        and response_symbol.lower() == V2_MARKET_SYMBOL.lower()
    )

    ok = (
        status == 200
        and symbol_match
        and mark_price is not None
        and mark_price > 0
    )

    return {
        "status": status,
        "payload": payload,
        "response_symbol": response_symbol,
        "symbol_match": symbol_match,
        "mark_price": mark_price,
        "ok": ok,
    }


# ==================================================================================================
# BALANCE
# ==================================================================================================

def read_balance():
    status, payload = authenticated_get(
        BALANCE_PATH,
        {
            "asset": "USDT",
        },
    )

    records = list_candidate_records(payload)

    selected = None

    for record in records:
        if not isinstance(record, dict):
            continue

        asset = str(
            record.get("asset")
            or record.get("coin")
            or record.get("currency")
            or ""
        ).upper()

        if asset == "USDT":
            selected = record
            break

    if selected is None and records:
        candidate = records[0]
        if isinstance(candidate, dict):
            selected = candidate

    available = None
    total = None
    asset = None

    if selected:
        asset = str(
            selected.get("asset")
            or selected.get("coin")
            or selected.get("currency")
            or "USDT"
        )

        available = find_first_number(
            selected,
            [
                "available",
                "availableBalance",
                "available_balance",
                "free",
                "balanceAvailable",
            ],
        )

        total = find_first_number(
            selected,
            [
                "balance",
                "total",
                "totalBalance",
                "equity",
                "accountEquity",
            ],
        )

    if available is None:
        available = find_first_number(
            payload,
            [
                "available",
                "availableBalance",
                "available_balance",
                "free",
            ],
        )

    if total is None:
        total = find_first_number(
            payload,
            [
                "balance",
                "totalBalance",
                "equity",
                "total",
            ],
        )

    ok = (
        status == 200
        and available is not None
        and available >= 0
    )

    positive = bool(
        available is not None
        and available > 0
    )

    return {
        "status": status,
        "asset": asset or "USDT",
        "available": available,
        "total": total,
        "ok": ok,
        "positive": positive,
        "payload": payload,
    }


# ==================================================================================================
# POSITION
# ==================================================================================================

def position_size(record):
    if not isinstance(record, dict):
        return Decimal("0")

    value = find_first_number(
        record,
        [
            "size",
            "quantity",
            "positionAmt",
            "positionSize",
            "available",
            "holdVol",
            "total",
        ],
    )

    if value is None:
        return Decimal("0")

    return abs(value)


def read_position():
    status, payload = authenticated_get(
        POSITION_PATH,
        {
            "symbol": V3_AUTH_SYMBOL,
        },
    )

    records = list_candidate_records(payload)

    matching = []

    for record in records:
        if not isinstance(record, dict):
            continue

        symbol = str(
            record.get("symbol")
            or record.get("contract")
            or record.get("instrumentId")
            or ""
        ).upper()

        if symbol in ("", V3_AUTH_SYMBOL):
            matching.append(record)

    open_positions = 0

    for record in matching:
        if position_size(record) > 0:
            open_positions += 1

    ok = status == 200

    flat = (
        ok
        and open_positions == 0
    )

    return {
        "status": status,
        "response_count": len(matching),
        "open_positions": open_positions,
        "flat": flat,
        "ok": ok,
        "payload": payload,
    }


# ==================================================================================================
# SYMBOL CONFIGURATION
# ==================================================================================================

def read_symbol_config():
    status, payload = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": V3_AUTH_SYMBOL,
        },
    )

    records = list_candidate_records(payload)

    selected = None

    for record in records:
        if not isinstance(record, dict):
            continue

        symbol = str(
            record.get("symbol")
            or record.get("contract")
            or ""
        ).upper()

        if symbol == V3_AUTH_SYMBOL:
            selected = record
            break

    if selected is None and records:
        candidate = records[0]

        if isinstance(candidate, dict):
            selected = candidate

    selected = selected or {}

    response_symbol = str(
        selected.get("symbol")
        or selected.get("contract")
        or V3_AUTH_SYMBOL
    )

    margin_mode = str(
        selected.get("marginMode")
        or selected.get("marginType")
        or selected.get("margin_mode")
        or ""
    ).upper()

    separated_type = str(
        selected.get("separatedType")
        or selected.get("positionMode")
        or selected.get("holdMode")
        or ""
    ).upper()

    cross_leverage = find_first_number(
        selected,
        [
            "crossLeverage",
            "cross_leverage",
            "crossMarginLeverage",
        ],
    )

    long_leverage = find_first_number(
        selected,
        [
            "longLeverage",
            "long_leverage",
            "longLever",
            "isolatedLongLeverage",
        ],
    )

    short_leverage = find_first_number(
        selected,
        [
            "shortLeverage",
            "short_leverage",
            "shortLever",
            "isolatedShortLeverage",
        ],
    )

    margin_match = margin_mode == TARGET_MARGIN_MODE

    long_match = (
        long_leverage is not None
        and long_leverage == TARGET_LONG_LEVERAGE
    )

    short_match = (
        short_leverage is not None
        and short_leverage == TARGET_SHORT_LEVERAGE
    )

    ok = (
        status == 200
        and margin_mode != ""
        and long_leverage is not None
        and short_leverage is not None
    )

    return {
        "status": status,
        "response_symbol": response_symbol,
        "margin_mode": margin_mode,
        "separated_type": separated_type,
        "cross_leverage": cross_leverage,
        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
        "margin_match": margin_match,
        "long_match": long_match,
        "short_match": short_match,
        "ok": ok,
        "payload": payload,
    }


# ==================================================================================================
# SYNTHETIC ENTRY CALCULATION
# ==================================================================================================

def calculate_initial_entry(available_balance, mark_price):
    balance = D(available_balance)
    price = D(mark_price)

    if balance is None or balance <= 0:
        raise ValueError("Available balance must be positive")

    if price is None or price <= 0:
        raise ValueError("Mark price must be positive")

    margin_budget = (
        balance
        * ENTRY_BALANCE_PERCENT
        / Decimal("100")
    )

    leverage = TARGET_LONG_LEVERAGE

    planned_notional = margin_budget * leverage

    raw_qty = planned_notional / price

    rounded_qty = quantize_down(
        raw_qty,
        QTY_STEP,
    )

    if rounded_qty is None:
        raise ValueError("Quantity rounding failed")

    rounded_notional = rounded_qty * price

    estimated_margin = rounded_notional / leverage

    max_strategy_margin = (
        balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    qty_step_ok = (
        rounded_qty > 0
        and rounded_qty % QTY_STEP == 0
    )

    min_qty_ok = rounded_qty >= MIN_QTY

    margin_within_entry_budget = (
        estimated_margin <= margin_budget
    )

    exposure_cap_ok = (
        estimated_margin <= max_strategy_margin
    )

    entry_sizing_ok = all(
        [
            qty_step_ok,
            min_qty_ok,
            margin_within_entry_budget,
            exposure_cap_ok,
            rounded_notional > 0,
        ]
    )

    return {
        "balance": balance,
        "mark_price": price,
        "entry_percent": ENTRY_BALANCE_PERCENT,
        "margin_budget": margin_budget,
        "leverage": leverage,
        "planned_notional": planned_notional,
        "raw_qty": raw_qty,
        "rounded_qty": rounded_qty,
        "rounded_notional": rounded_notional,
        "estimated_margin": estimated_margin,
        "max_strategy_margin": max_strategy_margin,
        "qty_step_ok": qty_step_ok,
        "min_qty_ok": min_qty_ok,
        "margin_within_entry_budget": margin_within_entry_budget,
        "exposure_cap_ok": exposure_cap_ok,
        "entry_sizing_ok": entry_sizing_ok,
    }


# ==================================================================================================
# SYNTHETIC PAYLOAD ONLY
# ==================================================================================================

def build_synthetic_order_payload(entry):
    global SYNTHETIC_PAYLOADS_CREATED

    if not entry["entry_sizing_ok"]:
        raise RuntimeError(
            "Synthetic payload rejected because entry sizing is invalid"
        )

    client_seed = (
        VERSION
        + "|"
        + CANONICAL_SYMBOL
        + "|"
        + decimal_text(entry["mark_price"])
        + "|"
        + decimal_text(entry["rounded_qty"])
        + "|"
        + decimal_text(entry["balance"])
    )

    client_hash = hashlib.sha256(
        client_seed.encode("utf-8")
    ).hexdigest()[:20]

    client_order_id = (
        "r35ph-"
        + client_hash
    )

    payload = {
        "symbol": V3_AUTH_SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": decimal_text(
            entry["rounded_qty"]
        ),
        "newClientOrderId": client_order_id,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    payload_hash = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    SYNTHETIC_PAYLOADS_CREATED += 1

    return {
        "payload": payload,
        "canonical": canonical,
        "sha256": payload_hash,
    }


# ==================================================================================================
# SAFETY CHECK
# ==================================================================================================

def safety_invariants_ok():
    return all(
        [
            REAL_ORDER_EXECUTION is False,
            FIRST_REAL_ORDER_ALLOWED is False,
            DEMO_ORDER_EXECUTION is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
            ORDER_SUBMISSION_ENABLED is False,
            LEVERAGE_MUTATION_ENABLED is False,
            MARGIN_MODE_MUTATION_ENABLED is False,
            POSITION_MUTATION_ENABLED is False,
            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,
        ]
    )


# ==================================================================================================
# MAIN
# ==================================================================================================

def main():
    global FAILURE_STAGE
    global EXCEPTION_CLASS
    global EXCEPTION_MESSAGE

    start_health_server()

    section("MAIN.PY ENTERED")

    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: CANONICAL_SYMBOL={CANONICAL_SYMBOL}")
    log(f"{VERSION}: V2_MARKET_SYMBOL={V2_MARKET_SYMBOL}")
    log(f"{VERSION}: V3_AUTH_SYMBOL={V3_AUTH_SYMBOL}")
    log(f"{VERSION}: WEEX CONTRACT BASE={WEEX_CONTRACT_BASE}")
    log(f"{VERSION}: MARK PRICE PATH={MARK_PRICE_PATH}")
    log(f"{VERSION}: BALANCE PATH={BALANCE_PATH}")
    log(f"{VERSION}: POSITION PATH={POSITION_PATH}")
    log(f"{VERSION}: SYMBOL CONFIG PATH={SYMBOL_CONFIG_PATH}")

    log(f"{VERSION}: TARGET MARGIN MODE={TARGET_MARGIN_MODE}")
    log(
        f"{VERSION}: TARGET LONG LEVERAGE="
        f"{decimal_text(TARGET_LONG_LEVERAGE)}x"
    )
    log(
        f"{VERSION}: TARGET SHORT LEVERAGE="
        f"{decimal_text(TARGET_SHORT_LEVERAGE)}x"
    )

    log(
        f"{VERSION}: ENTRY BALANCE PERCENT="
        f"{decimal_text(ENTRY_BALANCE_PERCENT)}%"
    )
    log(
        f"{VERSION}: MAX FUND EXPOSURE PERCENT="
        f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
    )

    log(
        f"{VERSION}: QTY STEP="
        f"{decimal_text(QTY_STEP)}"
    )
    log(
        f"{VERSION}: MIN QTY="
        f"{decimal_text(MIN_QTY)}"
    )

    section("HARD WRITE FIREBREAK")

    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log(f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}")
    log(f"DEMO_ORDER_EXECUTION={DEMO_ORDER_EXECUTION}")
    log(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )
    log(f"ORDER_SUBMISSION_ENABLED={ORDER_SUBMISSION_ENABLED}")
    log(f"LEVERAGE_MUTATION_ENABLED={LEVERAGE_MUTATION_ENABLED}")
    log(
        "MARGIN_MODE_MUTATION_ENABLED="
        f"{MARGIN_MODE_MUTATION_ENABLED}"
    )
    log(f"POSITION_MUTATION_ENABLED={POSITION_MUTATION_ENABLED}")

    dns_ok = False
    credentials_ok = False
    public_mark_price_read_ok = False
    balance_read_ok = False
    positive_balance_ok = False
    position_read_ok = False
    flat_ok = False
    symbol_config_read_ok = False
    activation_env_match = False
    authenticated_weex_read_ok = False

    mark_price = None
    available_balance = None
    open_positions = None

    margin_mode = None
    long_leverage = None
    short_leverage = None

    entry = None
    synthetic = None

    entry_calculation_ok = False
    synthetic_payload_ok = False

    try:
        # ==========================================================================================
        # TEST 1
        # ==========================================================================================

        section("TEST 1: DNS")

        FAILURE_STAGE = "DNS"

        host = "api-contract.weex.com"

        log(f"HOST={host}")

        resolved_ip = socket.gethostbyname(host)

        dns_ok = bool(resolved_ip)

        log(f"RESOLVED_IP={resolved_ip}")
        log(f"DNS_OK={dns_ok}")

        # ==========================================================================================
        # TEST 2
        # ==========================================================================================

        section("TEST 2: CREDENTIAL CHECK")

        FAILURE_STAGE = "CREDENTIAL_CHECK"

        credentials_ok = credentials_present()

        log(
            "WEEX_API_KEY_PRESENT="
            f"{bool(WEEX_API_KEY)}"
        )
        log(
            "WEEX_API_SECRET_PRESENT="
            f"{bool(WEEX_API_SECRET)}"
        )
        log(
            "WEEX_API_PASSPHRASE_PRESENT="
            f"{bool(WEEX_API_PASSPHRASE)}"
        )
        log(f"CREDENTIALS_PRESENT={credentials_ok}")

        if not credentials_ok:
            raise RuntimeError(
                "WEEX_API_KEY / WEEX_API_SECRET / "
                "WEEX_API_PASSPHRASE required"
            )

        # ==========================================================================================
        # TEST 3
        # ==========================================================================================

        section("TEST 3: PUBLIC V2 MARK PRICE")

        FAILURE_STAGE = "PUBLIC_MARK_PRICE"

        log(f"CANONICAL_SYMBOL={CANONICAL_SYMBOL}")
        log(f"V2_MARKET_SYMBOL={V2_MARKET_SYMBOL}")
        log(f"PATH={MARK_PRICE_PATH}")

        mark_result = read_mark_price()

        mark_price = mark_result["mark_price"]
        public_mark_price_read_ok = mark_result["ok"]

        log(
            f"HTTP_STATUS="
            f"{mark_result['status']}"
        )
        log(
            f"RESPONSE_SYMBOL="
            f"{mark_result['response_symbol']}"
        )
        log(
            "RESPONSE_SYMBOL_MATCH="
            f"{mark_result['symbol_match']}"
        )
        log(
            f"MARK_PRICE="
            f"{decimal_text(mark_price)}"
        )
        log("MARK_PRICE_FIELD=markPrice")
        log(
            "PUBLIC_MARK_PRICE_READ_OK="
            f"{public_mark_price_read_ok}"
        )

        if not public_mark_price_read_ok:
            raise RuntimeError(
                "Public V2 mark-price validation failed"
            )

        # ==========================================================================================
        # TEST 4
        # ==========================================================================================

        section("TEST 4: AUTHENTICATED BALANCE")

        FAILURE_STAGE = "AUTHENTICATED_BALANCE"

        log(f"PATH={BALANCE_PATH}")

        balance_result = read_balance()

        available_balance = balance_result["available"]

        balance_read_ok = balance_result["ok"]
        positive_balance_ok = balance_result["positive"]

        log(
            f"ASSET="
            f"{balance_result['asset']}"
        )
        log(
            "AVAILABLE_BALANCE="
            f"{decimal_text(available_balance)}"
        )
        log(
            "TOTAL_BALANCE="
            f"{decimal_text(balance_result['total'])}"
        )
        log(
            f"BALANCE_READ_OK="
            f"{balance_read_ok}"
        )
        log(
            f"POSITIVE_BALANCE_OK="
            f"{positive_balance_ok}"
        )

        if not balance_read_ok:
            raise RuntimeError(
                "Authenticated balance read failed"
            )

        if not positive_balance_ok:
            raise RuntimeError(
                "Available USDT balance is not positive"
            )

        # ==========================================================================================
        # TEST 5
        # ==========================================================================================

        section("TEST 5: AUTHENTICATED POSITION")

        FAILURE_STAGE = "AUTHENTICATED_POSITION"

        log(f"CANONICAL_SYMBOL={CANONICAL_SYMBOL}")
        log(f"PATH={POSITION_PATH}")

        position_result = read_position()

        open_positions = position_result["open_positions"]

        position_read_ok = position_result["ok"]
        flat_ok = position_result["flat"]

        log(
            "POSITION_RESPONSE_COUNT="
            f"{position_result['response_count']}"
        )
        log(
            f"OPEN_POSITIONS="
            f"{open_positions}"
        )
        log(f"BTCUSDT_FLAT={flat_ok}")
        log(
            f"POSITION_READ_OK="
            f"{position_read_ok}"
        )

        if not position_read_ok:
            raise RuntimeError(
                "Authenticated position read failed"
            )

        # ==========================================================================================
        # TEST 6
        # ==========================================================================================

        section("TEST 6: AUTHENTICATED SYMBOL CONFIG")

        FAILURE_STAGE = "AUTHENTICATED_SYMBOL_CONFIG"

        log(f"CANONICAL_SYMBOL={CANONICAL_SYMBOL}")
        log(f"PATH={SYMBOL_CONFIG_PATH}")

        config_result = read_symbol_config()

        symbol_config_read_ok = config_result["ok"]

        margin_mode = config_result["margin_mode"]
        long_leverage = config_result["long_leverage"]
        short_leverage = config_result["short_leverage"]

        log(
            "RESPONSE_SYMBOL="
            f"{config_result['response_symbol']}"
        )
        log(f"MARGIN_MODE={margin_mode}")
        log(
            "SEPARATED_TYPE="
            f"{config_result['separated_type']}"
        )
        log(
            "CROSS_LEVERAGE="
            f"{decimal_text(config_result['cross_leverage'])}"
        )
        log(
            "LONG_LEVERAGE="
            f"{decimal_text(long_leverage)}"
        )
        log(
            "SHORT_LEVERAGE="
            f"{decimal_text(short_leverage)}"
        )
        log(
            "MARGIN_MODE_MATCH="
            f"{config_result['margin_match']}"
        )
        log(
            "LONG_LEVERAGE_MATCH="
            f"{config_result['long_match']}"
        )
        log(
            "SHORT_LEVERAGE_MATCH="
            f"{config_result['short_match']}"
        )
        log(
            "SYMBOL_CONFIG_READ_OK="
            f"{symbol_config_read_ok}"
        )

        activation_env_match = all(
            [
                public_mark_price_read_ok,
                balance_read_ok,
                positive_balance_ok,
                position_read_ok,
                flat_ok,
                symbol_config_read_ok,
                config_result["margin_match"],
                config_result["long_match"],
                config_result["short_match"],
            ]
        )

        authenticated_weex_read_ok = all(
            [
                balance_read_ok,
                position_read_ok,
                symbol_config_read_ok,
            ]
        )

        if not activation_env_match:
            raise RuntimeError(
                "R35P-G activation environment reconciliation regressed"
            )

        # ==========================================================================================
        # TEST 7
        # ==========================================================================================

        section("TEST 7: INITIAL ENTRY BUDGET")

        FAILURE_STAGE = "INITIAL_ENTRY_BUDGET"

        entry = calculate_initial_entry(
            available_balance,
            mark_price,
        )

        log(
            "AVAILABLE_BALANCE="
            f"{decimal_text(entry['balance'])}"
        )
        log(
            "ENTRY_BALANCE_PERCENT="
            f"{decimal_text(entry['entry_percent'])}%"
        )
        log(
            "ENTRY_MARGIN_BUDGET="
            f"{decimal_text(entry['margin_budget'])}"
        )
        log(
            "TARGET_LEVERAGE="
            f"{decimal_text(entry['leverage'])}x"
        )
        log(
            "PLANNED_NOTIONAL="
            f"{decimal_text(entry['planned_notional'])}"
        )

        # ==========================================================================================
        # TEST 8
        # ==========================================================================================

        section("TEST 8: BTC QUANTITY CALCULATION")

        FAILURE_STAGE = "QUANTITY_CALCULATION"

        log(
            "MARK_PRICE="
            f"{decimal_text(entry['mark_price'])}"
        )
        log(
            "RAW_QTY="
            f"{decimal_text(entry['raw_qty'])}"
        )
        log(
            "QTY_STEP="
            f"{decimal_text(QTY_STEP)}"
        )
        log(
            "MIN_QTY="
            f"{decimal_text(MIN_QTY)}"
        )
        log(
            "ROUNDED_QTY="
            f"{decimal_text(entry['rounded_qty'])}"
        )
        log(
            "QTY_STEP_OK="
            f"{entry['qty_step_ok']}"
        )
        log(
            "MIN_QTY_OK="
            f"{entry['min_qty_ok']}"
        )

        # ==========================================================================================
        # TEST 9
        # ==========================================================================================

        section("TEST 9: ROUNDED ENTRY EXPOSURE")

        FAILURE_STAGE = "ENTRY_EXPOSURE"

        log(
            "ROUNDED_NOTIONAL="
            f"{decimal_text(entry['rounded_notional'])}"
        )
        log(
            "ESTIMATED_MARGIN_AT_100X="
            f"{decimal_text(entry['estimated_margin'])}"
        )
        log(
            "ENTRY_MARGIN_BUDGET="
            f"{decimal_text(entry['margin_budget'])}"
        )
        log(
            "MARGIN_WITHIN_ENTRY_BUDGET="
            f"{entry['margin_within_entry_budget']}"
        )

        # ==========================================================================================
        # TEST 10
        # ==========================================================================================

        section("TEST 10: MAXIMUM FUND EXPOSURE FIREBREAK")

        FAILURE_STAGE = "MAX_EXPOSURE"

        log(
            "MAX_FUND_EXPOSURE_PERCENT="
            f"{decimal_text(MAX_FUND_EXPOSURE_PERCENT)}%"
        )
        log(
            "MAX_STRATEGY_MARGIN="
            f"{decimal_text(entry['max_strategy_margin'])}"
        )
        log(
            "CURRENT_ENTRY_MARGIN="
            f"{decimal_text(entry['estimated_margin'])}"
        )
        log(
            "EXPOSURE_CAP_OK="
            f"{entry['exposure_cap_ok']}"
        )

        entry_calculation_ok = entry["entry_sizing_ok"]

        log(
            "ENTRY_CALCULATION_OK="
            f"{entry_calculation_ok}"
        )

        if not entry_calculation_ok:
            raise RuntimeError(
                "Initial entry calculation failed safety checks"
            )

        # ==========================================================================================
        # TEST 11
        # ==========================================================================================

        section("TEST 11: SYNTHETIC ORDER PAYLOAD")

        FAILURE_STAGE = "SYNTHETIC_ORDER_PAYLOAD"

        synthetic = build_synthetic_order_payload(
            entry
        )

        payload = synthetic["payload"]

        log("SYNTHETIC_ONLY=True")
        log(f"SYMBOL={payload['symbol']}")
        log(f"SIDE={payload['side']}")
        log(
            f"POSITION_SIDE="
            f"{payload['positionSide']}"
        )
        log(
            f"ORDER_TYPE="
            f"{payload['type']}"
        )
        log(
            f"QUANTITY="
            f"{payload['quantity']}"
        )
        log(
            "NEW_CLIENT_ORDER_ID="
            f"{payload['newClientOrderId']}"
        )
        log(
            "SYNTHETIC_PAYLOAD_JSON="
            f"{synthetic['canonical']}"
        )
        log(
            "SYNTHETIC_PAYLOAD_SHA256="
            f"{synthetic['sha256']}"
        )

        synthetic_payload_ok = all(
            [
                payload["symbol"] == V3_AUTH_SYMBOL,
                payload["side"] == "BUY",
                payload["positionSide"] == "LONG",
                payload["type"] == "MARKET",
                payload["quantity"]
                == decimal_text(entry["rounded_qty"]),
                SYNTHETIC_PAYLOADS_CREATED == 1,
            ]
        )

        log(
            "SYNTHETIC_PAYLOAD_OK="
            f"{synthetic_payload_ok}"
        )

        if not synthetic_payload_ok:
            raise RuntimeError(
                "Synthetic payload validation failed"
            )

        # ==========================================================================================
        # TEST 12
        # ==========================================================================================

        section("TEST 12: NO-TRANSMISSION PROOF")

        FAILURE_STAGE = "NO_TRANSMISSION_PROOF"

        safety_ok = safety_invariants_ok()

        log(
            "REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )
        log(
            "FIRST_REAL_ORDER_ALLOWED="
            f"{FIRST_REAL_ORDER_ALLOWED}"
        )
        log(
            "DEMO_ORDER_EXECUTION="
            f"{DEMO_ORDER_EXECUTION}"
        )
        log(
            "EXCHANGE_MUTATION_TRANSPORT_ENABLED="
            f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
        )
        log(
            "ORDER_SUBMISSION_ENABLED="
            f"{ORDER_SUBMISSION_ENABLED}"
        )
        log(
            "LEVERAGE_MUTATION_ENABLED="
            f"{LEVERAGE_MUTATION_ENABLED}"
        )
        log(
            "MARGIN_MODE_MUTATION_ENABLED="
            f"{MARGIN_MODE_MUTATION_ENABLED}"
        )
        log(
            "POSITION_MUTATION_ENABLED="
            f"{POSITION_MUTATION_ENABLED}"
        )

        log(
            "EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES}"
        )
        log(
            "ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS}"
        )
        log(
            "LEVERAGE_MUTATIONS="
            f"{LEVERAGE_MUTATIONS}"
        )
        log(
            "MARGIN_MODE_MUTATIONS="
            f"{MARGIN_MODE_MUTATIONS}"
        )
        log(
            "POSITION_MUTATIONS="
            f"{POSITION_MUTATIONS}"
        )
        log(
            "SYNTHETIC_PAYLOADS_CREATED="
            f"{SYNTHETIC_PAYLOADS_CREATED}"
        )
        log(
            "SAFETY_INVARIANTS_OK="
            f"{safety_ok}"
        )

        if not safety_ok:
            raise RuntimeError(
                "Write firebreak invariant failed"
            )

        # ==========================================================================================
        # TEST 13
        # ==========================================================================================

        section("TEST 13: COMPOSITE R35P-H GATE")

        FAILURE_STAGE = "COMPOSITE_GATE"

        composite_gate_ready = all(
            [
                dns_ok,
                credentials_ok,
                public_mark_price_read_ok,
                balance_read_ok,
                positive_balance_ok,
                position_read_ok,
                flat_ok,
                symbol_config_read_ok,
                activation_env_match,
                authenticated_weex_read_ok,
                entry_calculation_ok,
                synthetic_payload_ok,
                safety_ok,
            ]
        )

        log(f"DNS_OK={dns_ok}")
        log(
            f"CREDENTIALS_PRESENT="
            f"{credentials_ok}"
        )
        log(
            "PUBLIC_MARK_PRICE_READ_OK="
            f"{public_mark_price_read_ok}"
        )
        log(
            f"MARK_PRICE="
            f"{decimal_text(mark_price)}"
        )
        log(
            f"BALANCE_READ_OK="
            f"{balance_read_ok}"
        )
        log(
            f"POSITIVE_BALANCE_OK="
            f"{positive_balance_ok}"
        )
        log(
            "AVAILABLE_BALANCE="
            f"{decimal_text(available_balance)}"
        )
        log(
            f"POSITION_READ_OK="
            f"{position_read_ok}"
        )
        log(f"OPEN_POSITIONS={open_positions}")
        log(f"BTCUSDT_FLAT={flat_ok}")
        log(
            "SYMBOL_CONFIG_READ_OK="
            f"{symbol_config_read_ok}"
        )
        log(f"MARGIN_MODE={margin_mode}")
        log(
            "LONG_LEVERAGE="
            f"{decimal_text(long_leverage)}"
        )
        log(
            "SHORT_LEVERAGE="
            f"{decimal_text(short_leverage)}"
        )
        log(
            "AUTHENTICATED_WEEX_READ_OK="
            f"{authenticated_weex_read_ok}"
        )
        log(
            "ACTIVATION_ENV_MATCH="
            f"{activation_env_match}"
        )
        log(
            "ENTRY_CALCULATION_OK="
            f"{entry_calculation_ok}"
        )
        log(
            "SYNTHETIC_PAYLOAD_OK="
            f"{synthetic_payload_ok}"
        )
        log(
            "SAFETY_INVARIANTS_OK="
            f"{safety_ok}"
        )
        log(
            "COMPOSITE_R35P_H_GATE_READY="
            f"{composite_gate_ready}"
        )

        test_status = (
            "PASS"
            if composite_gate_ready
            else "FAIL"
        )

        log(f"TEST_STATUS={test_status}")

        if not composite_gate_ready:
            raise RuntimeError(
                "R35P-H composite gate failed"
            )

        FAILURE_STAGE = None
        EXCEPTION_CLASS = None
        EXCEPTION_MESSAGE = None

        # ==========================================================================================
        # RESULT
        # ==========================================================================================

        section("R35P-H RESULT")

        log(
            "TEST="
            "LIVE_ENTRY_CALCULATION_AND_SYNTHETIC_PAYLOAD"
        )

        log(
            f"CANONICAL_SYMBOL="
            f"{CANONICAL_SYMBOL}"
        )
        log(
            f"V2_MARKET_SYMBOL="
            f"{V2_MARKET_SYMBOL}"
        )
        log(
            "V2_MARKET_SYMBOL_FORMAT="
            "cmt_btcusdt"
        )
        log(
            "V3_AUTH_SYMBOL_FORMAT="
            "BTCUSDT"
        )

        log(f"DNS_OK={dns_ok}")
        log(
            f"CREDENTIALS_PRESENT="
            f"{credentials_ok}"
        )

        log(
            "PUBLIC_MARK_PRICE_READ_OK="
            f"{public_mark_price_read_ok}"
        )
        log(
            f"MARK_PRICE="
            f"{decimal_text(mark_price)}"
        )

        log(
            f"BALANCE_READ_OK="
            f"{balance_read_ok}"
        )
        log(
            "AVAILABLE_BALANCE="
            f"{decimal_text(available_balance)}"
        )

        log(
            f"POSITION_READ_OK="
            f"{position_read_ok}"
        )
        log(
            f"OPEN_POSITIONS="
            f"{open_positions}"
        )
        log(f"BTCUSDT_FLAT={flat_ok}")

        log(
            "SYMBOL_CONFIG_READ_OK="
            f"{symbol_config_read_ok}"
        )
        log(
            f"MARGIN_MODE="
            f"{margin_mode}"
        )
        log(
            "LONG_LEVERAGE="
            f"{decimal_text(long_leverage)}"
        )
        log(
            "SHORT_LEVERAGE="
            f"{decimal_text(short_leverage)}"
        )

        log(
            "ACTIVATION_ENV_MATCH="
            f"{activation_env_match}"
        )

        log(
            "ENTRY_BALANCE_PERCENT="
            f"{decimal_text(ENTRY_BALANCE_PERCENT)}"
        )
        log(
            "ENTRY_MARGIN_BUDGET="
            f"{decimal_text(entry['margin_budget'])}"
        )
        log(
            "PLANNED_NOTIONAL="
            f"{decimal_text(entry['planned_notional'])}"
        )
        log(
            "RAW_QTY="
            f"{decimal_text(entry['raw_qty'])}"
        )
        log(
            "ROUNDED_QTY="
            f"{decimal_text(entry['rounded_qty'])}"
        )
        log(
            "ROUNDED_NOTIONAL="
            f"{decimal_text(entry['rounded_notional'])}"
        )
        log(
            "ESTIMATED_MARGIN="
            f"{decimal_text(entry['estimated_margin'])}"
        )
        log(
            "MAX_STRATEGY_MARGIN="
            f"{decimal_text(entry['max_strategy_margin'])}"
        )

        log(
            "ENTRY_CALCULATION_OK="
            f"{entry_calculation_ok}"
        )

        log(
            "SYNTHETIC_CLIENT_ORDER_ID="
            f"{synthetic['payload']['newClientOrderId']}"
        )
        log(
            "SYNTHETIC_PAYLOAD_SHA256="
            f"{synthetic['sha256']}"
        )
        log(
            "SYNTHETIC_PAYLOAD_OK="
            f"{synthetic_payload_ok}"
        )

        log(
            "PUBLIC_MARKET_GETS="
            f"{PUBLIC_MARKET_GETS}"
        )
        log(
            "AUTHENTICATED_WEEX_READS="
            f"{AUTHENTICATED_WEEX_READS}"
        )

        log(
            "EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES}"
        )
        log(
            "ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS}"
        )

        log(
            "REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )
        log(
            "FIRST_REAL_ORDER_ALLOWED="
            f"{FIRST_REAL_ORDER_ALLOWED}"
        )

        log(
            "SAFETY_INVARIANTS_OK="
            f"{safety_ok}"
        )

        log(
            "COMPOSITE_R35P_H_GATE_READY="
            f"{composite_gate_ready}"
        )

        log(f"FAILURE_STAGE={FAILURE_STAGE}")
        log(f"EXCEPTION_CLASS={EXCEPTION_CLASS}")
        log(
            f"EXCEPTION_MESSAGE="
            f"{EXCEPTION_MESSAGE}"
        )

        log("STATUS=PASS")
        log("R35P-G_RECONCILIATION=PRESERVED")
        log("EXECUTION_PERMISSION=NOT_GRANTED")
        log("REAL_ORDER_PATH=ABSENT")
        log("SYNTHETIC_TRANSPORT_ONLY=True")
        log("NEXT_UNIT=R35P-I")

    except Exception as exc:
        if FAILURE_STAGE is None:
            FAILURE_STAGE = "UNKNOWN"

        EXCEPTION_CLASS = type(exc).__name__
        EXCEPTION_MESSAGE = str(exc)

        section("R35P-H ERROR DIAGNOSTIC")

        log(f"FAILURE_STAGE={FAILURE_STAGE}")
        log(
            f"EXCEPTION_CLASS="
            f"{EXCEPTION_CLASS}"
        )
        log(
            f"EXCEPTION_MESSAGE="
            f"{EXCEPTION_MESSAGE}"
        )

        log(
            "PUBLIC_MARKET_GETS="
            f"{PUBLIC_MARKET_GETS}"
        )
        log(
            "AUTHENTICATED_WEEX_READS="
            f"{AUTHENTICATED_WEEX_READS}"
        )

        log(
            "EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES}"
        )
        log(
            "ORDER_SUBMISSIONS="
            f"{ORDER_SUBMISSIONS}"
        )

        log(
            "REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )
        log(
            "FIRST_REAL_ORDER_ALLOWED="
            f"{FIRST_REAL_ORDER_ALLOWED}"
        )

        log(
            "SAFETY_INVARIANTS_OK="
            f"{safety_invariants_ok()}"
        )

        log("STATUS=FAIL")
        log("EXECUTION_PERMISSION=NOT_GRANTED")
        log("REAL_ORDER_PATH=ABSENT")

    # ==============================================================================================
    # HEARTBEAT
    # ==============================================================================================

    heartbeat = 0

    while True:
        heartbeat += 1

        status = (
            "PASS"
            if FAILURE_STAGE is None
            else "FAIL"
        )

        log(
            f"{VERSION}: HEARTBEAT={heartbeat} "
            f"PUBLIC_MARK_PRICE_READ_OK={public_mark_price_read_ok} "
            f"MARK_PRICE={decimal_text(mark_price)} "
            f"BALANCE_READ_OK={balance_read_ok} "
            f"AVAILABLE_BALANCE={decimal_text(available_balance)} "
            f"POSITION_READ_OK={position_read_ok} "
            f"OPEN_POSITIONS={open_positions if open_positions is not None else 'UNKNOWN'} "
            f"BTCUSDT_FLAT={flat_ok} "
            f"SYMBOL_CONFIG_READ_OK={symbol_config_read_ok} "
            f"ACTIVATION_ENV_MATCH={activation_env_match} "
            f"ENTRY_CALCULATION_OK={entry_calculation_ok} "
            f"SYNTHETIC_PAYLOAD_OK={synthetic_payload_ok} "
            f"TEST_STATUS={status} "
            f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS} "
            f"AUTHENTICATED_WEEX_READS={AUTHENTICATED_WEEX_READS} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )

        time.sleep(60)


if __name__ == "__main__":
    main()

