

#!/usr/bin/env python3
# =============================================================================
# R35Q - FINAL READ-ONLY ACTIVATION ENVIRONMENT RECONCILIATION
#
# PURPOSE
#   Consolidate the proven R35P diagnostics into one final live-environment
#   readiness check.
#
# HARD SAFETY BOUNDARY
#   - GET requests only.
#   - No order endpoint exists in this file.
#   - No leverage/margin/position mutation endpoint exists in this file.
#   - No POST/PUT/PATCH/DELETE transport exists in this file.
#   - REAL_ORDER_EXECUTION is permanently False.
#
# EXPECTED SUCCESS RESULT
#   ACTIVATION_ENV=READY
#   BLOCKERS=NONE
#   R35P_DIAGNOSTICS_COMPLETE=True
#   R35Q_RECONCILIATION_OK=True
#   EXCHANGE_NETWORK_WRITES=0
#   ORDER_SUBMISSIONS=0
# =============================================================================

import base64
import hashlib
import hmac
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# IDENTITY / TARGET
# =============================================================================

UNIT = "R35Q"
SYMBOL = "BTCUSDT"
ASSET = "USDT"

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"

BALANCE_PATH = "/capi/v3/account/balance"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
POSITION_PATH = "/capi/v3/account/position/singlePosition"
MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = 100.0
TARGET_SHORT_LEVERAGE = 100.0

ENTRY_PERCENT = 5.0
MAX_FUND_EXPOSURE_PERCENT = 35.0
MAX_PYRAMID_ADDS = 1
PYRAMID_PERCENT = 5.0
MAX_BACKUPS = 3
BACKUP_PERCENT = 5.0

QTY_STEP = 0.0001
MIN_QTY = 0.0001

TP1_PERCENT = 20.0
TP2_PERCENT = 20.0
TP3_PERCENT = 60.0
TP1_TRIGGER_PERCENT = 0.5
TP2_TRIGGER_PERCENT = 1.0
TRAILING_DISTANCE_PERCENT = 0.20

HTTP_TIMEOUT_SECONDS = 15
HEARTBEAT_SECONDS = 30

LINE = "-" * 100


# =============================================================================
# HARD FIREBREAKS
# =============================================================================

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

AUTHENTICATED_WEEX_READS = 0
PUBLIC_MARKET_GETS = 0


# =============================================================================
# ENVIRONMENT
# =============================================================================

WEEX_API_KEY = os.environ.get("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.environ.get("WEEX_API_SECRET", "").strip()
WEEX_API_PASSPHRASE = os.environ.get("WEEX_API_PASSPHRASE", "").strip()

CREDENTIALS_PRESENT = bool(
    WEEX_API_KEY and WEEX_API_SECRET and WEEX_API_PASSPHRASE
)

PORT = int(os.environ.get("PORT", "10000"))

PERSISTENT_DISK_ROOT = Path(
    os.environ.get("PERSISTENT_DISK_ROOT", "/var/data")
)
STATE_DIR = Path(
    os.environ.get("STATE_DIR", str(PERSISTENT_DISK_ROOT / "r35q_state"))
)
DURABLE_MARKER_FILE = STATE_DIR / "cross_deploy_marker.json"


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in ("/", "/health", "/healthz"):
            payload = json.dumps(
                {
                    "status": "ok",
                    "unit": UNIT,
                    "real_order_execution": REAL_ORDER_EXECUTION,
                    "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
                }
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def start_health_server() -> None:
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log(f"{UNIT}: HEALTH SERVER STARTED ON PORT {PORT}")


# =============================================================================
# LOGGING
# =============================================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str = "") -> None:
    print(f"{utc_now()} {message}", flush=True)


def section(title: str) -> None:
    log(LINE)
    log(title)
    log(LINE)


def emit(key: str, value: Any) -> None:
    log(f"{key}={value}")


# =============================================================================
# GENERIC HELPERS
# =============================================================================

def safe_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def nearly_equal(
    a: Optional[float],
    b: float,
    eps: float = 1e-9,
) -> bool:
    return a is not None and abs(a - b) <= eps


def floor_to_step(value: float, step: float) -> float:
    if step <= 0:
        raise ValueError("step must be positive")

    units = int((value + 1e-15) / step)
    return round(units * step, 12)


def json_decode(data: bytes) -> Any:
    text = data.decode("utf-8", errors="replace")

    if not text:
        return None

    return json.loads(text)


def extract_api_error(
    payload: Any,
) -> Tuple[Optional[Any], Optional[str]]:

    if isinstance(payload, dict):
        code = payload.get("code")

        message = (
            payload.get("msg")
            or payload.get("message")
            or payload.get("error")
        )

        return (
            code,
            str(message) if message is not None else None,
        )

    return None, None


# =============================================================================
# ABSOLUTE GET-ONLY TRANSPORT
# =============================================================================

def assert_method_is_read_only(method: str) -> None:
    if method.upper() != "GET":
        raise RuntimeError(
            f"{UNIT} FIREBREAK: NON-GET METHOD BLOCKED: {method}"
        )


def request_get(
    path: str,
    query: Optional[Dict[str, str]] = None,
    authenticated: bool = False,
) -> Tuple[int, Any]:

    global AUTHENTICATED_WEEX_READS
    global PUBLIC_MARKET_GETS

    method = "GET"

    assert_method_is_read_only(method)

    query_string = urllib.parse.urlencode(query or {})

    url = WEEX_CONTRACT_BASE + path

    if query_string:
        url += "?" + query_string

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"{UNIT}-read-only-reconciliation/1.0",
    }

    if authenticated:

        if not CREDENTIALS_PRESENT:
            raise RuntimeError(
                "WEEX API credentials are missing"
            )

        timestamp = str(int(time.time() * 1000))

        signing_text = (
            timestamp
            + method
            + path
        )

        if query_string:
            signing_text += "?" + query_string

        digest = hmac.new(
            WEEX_API_SECRET.encode("utf-8"),
            signing_text.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        signature = base64.b64encode(
            digest
        ).decode("utf-8")

        headers.update(
            {
                "ACCESS-KEY": WEEX_API_KEY,
                "ACCESS-SIGN": signature,
                "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
                "ACCESS-TIMESTAMP": timestamp,
                "locale": "en-US",
            }
        )

    req = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            req,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            status = int(
                response.getcode()
            )

            payload = json_decode(
                response.read()
            )

    except urllib.error.HTTPError as exc:

        status = int(exc.code)

        raw = exc.read()

        try:
            payload = json_decode(raw)

        except Exception:
            payload = {
                "message": raw.decode(
                    "utf-8",
                    errors="replace",
                )
            }

    if authenticated:
        AUTHENTICATED_WEEX_READS += 1

    else:
        PUBLIC_MARKET_GETS += 1

    return status, payload


# =============================================================================
# DURABLE LOCAL STATE CHECK
# =============================================================================

def check_durable_state() -> Dict[str, Any]:

    result: Dict[str, Any] = {
        "local_durable": False,
        "cross_deploy_durable": False,
        "seen_count": 0,
        "path": str(DURABLE_MARKER_FILE),
        "error": None,
    }

    try:

        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        previous: Dict[str, Any] = {}

        if DURABLE_MARKER_FILE.exists():

            try:

                with DURABLE_MARKER_FILE.open(
                    "r",
                    encoding="utf-8",
                ) as handle:

                    loaded = json.load(handle)

                    if isinstance(loaded, dict):
                        previous = loaded

            except Exception:
                previous = {}

        previous_seen_count = int(
            previous.get("seen_count", 0) or 0
        )

        seen_count = previous_seen_count + 1

        marker = {
            "unit": UNIT,
            "marker_family": "R35_TELEGRAM_DEDUPE_DURABILITY",
            "seen_count": seen_count,
            "updated_at_utc": utc_now(),
        }

        temp_file = DURABLE_MARKER_FILE.with_suffix(
            ".tmp"
        )

        with temp_file.open(
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                marker,
                handle,
                sort_keys=True,
                indent=2,
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.replace(
            temp_file,
            DURABLE_MARKER_FILE,
        )

        result["local_durable"] = (
            DURABLE_MARKER_FILE.exists()
        )

        result["seen_count"] = seen_count

        result["cross_deploy_durable"] = (
            previous_seen_count >= 1
        )

    except Exception as exc:

        result["error"] = (
            f"{exc.__class__.__name__}: {exc}"
        )

    return result


# =============================================================================
# LIVE READS
# =============================================================================

def read_balance() -> Dict[str, Any]:

    result = {
        "http_status": None,
        "read_ok": False,
        "available_usdt": None,
        "total_usdt": None,
        "error_code": None,
        "error_message": None,
    }

    try:

        status, payload = request_get(
            BALANCE_PATH,
            authenticated=True,
        )

        result["http_status"] = status

        code, message = extract_api_error(
            payload
        )

        result["error_code"] = code
        result["error_message"] = message

        if status != 200:
            return result

        if not isinstance(payload, list):
            return result

        for row in payload:

            if not isinstance(row, dict):
                continue

            if (
                str(
                    row.get(
                        "asset",
                        "",
                    )
                ).upper()
                != ASSET
            ):
                continue

            available = safe_float(
                row.get(
                    "availableBalance"
                )
            )

            total = safe_float(
                row.get(
                    "balance"
                )
            )

            result["available_usdt"] = (
                available
            )

            result["total_usdt"] = total

            result["read_ok"] = (
                available is not None
                and available >= 0
            )

            return result

        result["error_message"] = (
            "USDT balance row not found"
        )

    except Exception as exc:

        result["error_message"] = (
            f"{exc.__class__.__name__}: {exc}"
        )

    return result


def read_symbol_config() -> Dict[str, Any]:

    result = {
        "http_status": None,
        "read_ok": False,
        "symbol": None,
        "symbol_match": False,
        "margin_mode": None,
        "margin_match": False,
        "separated_type": None,
        "cross_leverage": None,
        "long_leverage": None,
        "long_match": False,
        "short_leverage": None,
        "short_match": False,
        "config_ok": False,
        "error_code": None,
        "error_message": None,
    }

    try:

        status, payload = request_get(
            SYMBOL_CONFIG_PATH,
            query={
                "symbol": SYMBOL,
            },
            authenticated=True,
        )

        result["http_status"] = status

        code, message = extract_api_error(
            payload
        )

        result["error_code"] = code
        result["error_message"] = message

        if status != 200:
            return result

        if isinstance(payload, list):
            rows = payload

        elif isinstance(payload, dict):
            rows = [payload]

        else:
            return result

        row = None

        for candidate in rows:

            if not isinstance(
                candidate,
                dict,
            ):
                continue

            if (
                str(
                    candidate.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ):

                row = candidate
                break

        if row is None:

            result["error_message"] = (
                "BTCUSDT symbol config not found"
            )

            return result

        observed_symbol = str(
            row.get(
                "symbol",
                "",
            )
        ).upper()

        margin_mode = str(
            row.get(
                "marginType",
                "",
            )
        ).upper()

        long_leverage = safe_float(
            row.get(
                "isolatedLongLeverage"
            )
        )

        short_leverage = safe_float(
            row.get(
                "isolatedShortLeverage"
            )
        )

        cross_leverage = safe_float(
            row.get(
                "crossLeverage"
            )
        )

        result["read_ok"] = True
        result["symbol"] = observed_symbol

        result["symbol_match"] = (
            observed_symbol == SYMBOL
        )

        result["margin_mode"] = (
            margin_mode
        )

        result["margin_match"] = (
            margin_mode
            == TARGET_MARGIN_MODE
        )

        result["separated_type"] = (
            row.get(
                "separatedType"
            )
        )

        result["cross_leverage"] = (
            cross_leverage
        )

        result["long_leverage"] = (
            long_leverage
        )

        result["long_match"] = (
            nearly_equal(
                long_leverage,
                TARGET_LONG_LEVERAGE,
            )
        )

        result["short_leverage"] = (
            short_leverage
        )

        result["short_match"] = (
            nearly_equal(
                short_leverage,
                TARGET_SHORT_LEVERAGE,
            )
        )

        result["config_ok"] = bool(
            result["read_ok"]
            and result["symbol_match"]
            and result["margin_match"]
            and result["long_match"]
            and result["short_match"]
        )

    except Exception as exc:

        result["error_message"] = (
            f"{exc.__class__.__name__}: {exc}"
        )

    return result


def read_position() -> Dict[str, Any]:

    result = {
        "http_status": None,
        "read_ok": False,
        "position_rows": 0,
        "nonzero_position_rows": 0,
        "long_qty": 0.0,
        "short_qty": 0.0,
        "flat": False,
        "error_code": None,
        "error_message": None,
    }

    try:

        status, payload = request_get(
            POSITION_PATH,
            query={
                "symbol": SYMBOL,
            },
            authenticated=True,
        )

        result["http_status"] = status

        code, message = extract_api_error(
            payload
        )

        result["error_code"] = code
        result["error_message"] = message

        if status != 200:
            return result

        if payload is None:
            rows = []

        elif isinstance(payload, list):
            rows = payload

        elif isinstance(payload, dict):
            rows = [payload]

        else:

            result["error_message"] = (
                "Unexpected position response type"
            )

            return result

        long_qty = 0.0
        short_qty = 0.0
        nonzero_rows = 0
        btc_rows = 0

        for row in rows:

            if not isinstance(
                row,
                dict,
            ):
                continue

            row_symbol = str(
                row.get(
                    "symbol",
                    "",
                )
            ).upper()

            if (
                row_symbol
                and row_symbol != SYMBOL
            ):
                continue

            btc_rows += 1

            qty = abs(
                safe_float(
                    row.get(
                        "size"
                    )
                )
                or 0.0
            )

            side = str(
                row.get(
                    "side",
                    "",
                )
            ).upper()

            if qty > 0:
                nonzero_rows += 1

            if side == "LONG":
                long_qty += qty

            elif side == "SHORT":
                short_qty += qty

            elif qty > 0:

                # Unknown non-zero side must
                # prevent a flat verdict.
                long_qty += qty

        result["read_ok"] = True

        result["position_rows"] = (
            btc_rows
        )

        result["nonzero_position_rows"] = (
            nonzero_rows
        )

        result["long_qty"] = (
            long_qty
        )

        result["short_qty"] = (
            short_qty
        )

        result["flat"] = (
            nonzero_rows == 0
            and long_qty == 0.0
            and short_qty == 0.0
        )

    except Exception as exc:

        result["error_message"] = (
            f"{exc.__class__.__name__}: {exc}"
        )

    return result


def read_mark_price() -> Dict[str, Any]:

    result = {
        "http_status": None,
        "read_ok": False,
        "symbol": None,
        "price": None,
        "error_code": None,
        "error_message": None,
    }

    try:

        status, payload = request_get(
            MARK_PRICE_PATH,
            query={
                "symbol": SYMBOL,
                "priceType": "MARK",
            },
            authenticated=False,
        )

        result["http_status"] = status

        code, message = extract_api_error(
            payload
        )

        result["error_code"] = code
        result["error_message"] = message

        if status != 200:
            return result

        if not isinstance(
            payload,
            dict,
        ):
            return result

        symbol = str(
            payload.get(
                "symbol",
                "",
            )
        ).upper()

        price = safe_float(
            payload.get(
                "price"
            )
        )

        result["symbol"] = symbol
        result["price"] = price

        result["read_ok"] = bool(
            symbol == SYMBOL
            and price is not None
            and price > 0
        )

    except Exception as exc:

        result["error_message"] = (
            f"{exc.__class__.__name__}: {exc}"
        )

    return result


# =============================================================================
# STRATEGY READINESS PROJECTION
# PURE CALCULATION ONLY
# =============================================================================

def calculate_strategy_projection(
    available_balance: Optional[float],
    mark_price: Optional[float],
) -> Dict[str, Any]:

    result = {
        "calculation_ok": False,
        "entry_margin_budget": None,
        "entry_notional": None,
        "raw_entry_qty": None,
        "rounded_entry_qty": None,
        "rounded_entry_notional": None,
        "estimated_entry_margin": None,
        "max_allowed_strategy_margin": None,
        "planned_max_strategy_margin": None,
        "planned_exposure_within_cap": False,
        "tp_sum_ok": False,
    }

    if (
        available_balance is None
        or available_balance <= 0
        or mark_price is None
        or mark_price <= 0
    ):
        return result

    entry_margin_budget = (
        available_balance
        * ENTRY_PERCENT
        / 100.0
    )

    entry_notional = (
        entry_margin_budget
        * TARGET_LONG_LEVERAGE
    )

    raw_entry_qty = (
        entry_notional
        / mark_price
    )

    rounded_entry_qty = (
        floor_to_step(
            raw_entry_qty,
            QTY_STEP,
        )
    )

    if (
        rounded_entry_qty
        < MIN_QTY
    ):
        rounded_entry_qty = 0.0

    rounded_entry_notional = (
        rounded_entry_qty
        * mark_price
    )

    if rounded_entry_qty > 0:

        estimated_entry_margin = (
            rounded_entry_notional
            / TARGET_LONG_LEVERAGE
        )

    else:
        estimated_entry_margin = 0.0

    max_allowed_strategy_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / 100.0
    )

    planned_margin_percent = (
        ENTRY_PERCENT
        + (
            MAX_PYRAMID_ADDS
            * PYRAMID_PERCENT
        )
        + (
            MAX_BACKUPS
            * BACKUP_PERCENT
        )
    )

    planned_max_strategy_margin = (
        available_balance
        * planned_margin_percent
        / 100.0
    )

    planned_exposure_within_cap = (
        planned_max_strategy_margin
        <= max_allowed_strategy_margin
        + 1e-12
    )

    tp_sum_ok = nearly_equal(
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT,
        100.0,
    )

    result["calculation_ok"] = (
        rounded_entry_qty
        >= MIN_QTY
    )

    result["entry_margin_budget"] = (
        entry_margin_budget
    )

    result["entry_notional"] = (
        entry_notional
    )

    result["raw_entry_qty"] = (
        raw_entry_qty
    )

    result["rounded_entry_qty"] = (
        rounded_entry_qty
    )

    result["rounded_entry_notional"] = (
        rounded_entry_notional
    )

    result["estimated_entry_margin"] = (
        estimated_entry_margin
    )

    result["max_allowed_strategy_margin"] = (
        max_allowed_strategy_margin
    )

    result["planned_max_strategy_margin"] = (
        planned_max_strategy_margin
    )

    result["planned_exposure_within_cap"] = (
        planned_exposure_within_cap
    )

    result["tp_sum_ok"] = (
        tp_sum_ok
    )

    return result


# =============================================================================
# SAFETY ASSERTION
# =============================================================================

def safety_invariants_ok() -> bool:

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


# =============================================================================
# MAIN RECONCILIATION
# =============================================================================

def main() -> None:

    start_health_server()

    section(
        f"{UNIT}: MAIN.PY ENTERED"
    )

    emit(
        "SYMBOL",
        SYMBOL,
    )

    emit(
        "WEEX_CONTRACT_BASE",
        WEEX_CONTRACT_BASE,
    )

    emit(
        "BALANCE_PATH",
        BALANCE_PATH,
    )

    emit(
        "SYMBOL_CONFIG_PATH",
        SYMBOL_CONFIG_PATH,
    )

    emit(
        "POSITION_PATH",
        POSITION_PATH,
    )

    emit(
        "MARK_PRICE_PATH",
        MARK_PRICE_PATH,
    )

    emit(
        "TARGET_MARGIN_MODE",
        TARGET_MARGIN_MODE,
    )

    emit(
        "TARGET_LONG_LEVERAGE",
        f"{TARGET_LONG_LEVERAGE:.0f}x",
    )

    emit(
        "TARGET_SHORT_LEVERAGE",
        f"{TARGET_SHORT_LEVERAGE:.0f}x",
    )

    section(
        f"{UNIT}: HARD WRITE FIREBREAK"
    )

    emit(
        "REAL_ORDER_EXECUTION",
        REAL_ORDER_EXECUTION,
    )

    emit(
        "FIRST_REAL_ORDER_ALLOWED",
        FIRST_REAL_ORDER_ALLOWED,
    )

    emit(
        "DEMO_ORDER_EXECUTION",
        DEMO_ORDER_EXECUTION,
    )

    emit(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED",
        EXCHANGE_MUTATION_TRANSPORT_ENABLED,
    )

    emit(
        "ORDER_SUBMISSION_ENABLED",
        ORDER_SUBMISSION_ENABLED,
    )

    emit(
        "LEVERAGE_MUTATION_ENABLED",
        LEVERAGE_MUTATION_ENABLED,
    )

    emit(
        "MARGIN_MODE_MUTATION_ENABLED",
        MARGIN_MODE_MUTATION_ENABLED,
    )

    emit(
        "POSITION_MUTATION_ENABLED",
        POSITION_MUTATION_ENABLED,
    )

    emit(
        "EXCHANGE_NETWORK_WRITES",
        EXCHANGE_NETWORK_WRITES,
    )

    emit(
        "ORDER_SUBMISSIONS",
        ORDER_SUBMISSIONS,
    )

    emit(
        "LEVERAGE_MUTATIONS",
        LEVERAGE_MUTATIONS,
    )

    emit(
        "MARGIN_MODE_MUTATIONS",
        MARGIN_MODE_MUTATIONS,
    )

    emit(
        "POSITION_MUTATIONS",
        POSITION_MUTATIONS,
    )

    emit(
        "SAFETY_INVARIANTS_OK",
        safety_invariants_ok(),
    )

    section(
        f"{UNIT}: CREDENTIAL CHECK"
    )

    emit(
        "WEEX_API_KEY_PRESENT",
        bool(WEEX_API_KEY),
    )

    emit(
        "WEEX_API_SECRET_PRESENT",
        bool(WEEX_API_SECRET),
    )

    emit(
        "WEEX_API_PASSPHRASE_PRESENT",
        bool(WEEX_API_PASSPHRASE),
    )

    emit(
        "CREDENTIALS_PRESENT",
        CREDENTIALS_PRESENT,
    )

    section(
        f"{UNIT}: DURABLE STATE CHECK"
    )

    durable = (
        check_durable_state()
    )

    emit(
        "PERSISTENT_DISK_ROOT",
        PERSISTENT_DISK_ROOT,
    )

    emit(
        "STATE_DIR",
        STATE_DIR,
    )

    emit(
        "DURABLE_MARKER_FILE",
        durable["path"],
    )

    emit(
        "TELEGRAM_LOCAL_DURABLE",
        durable["local_durable"],
    )

    emit(
        "TELEGRAM_CROSS_DEPLOY_DURABLE",
        durable[
            "cross_deploy_durable"
        ],
    )

    emit(
        "DURABLE_MARKER_SEEN_COUNT",
        durable[
            "seen_count"
        ],
    )

    emit(
        "DURABILITY_ERROR",
        durable["error"],
    )

    section(
        f"{UNIT}: LIVE READ-ONLY RECONCILIATION"
    )

    if CREDENTIALS_PRESENT:

        balance = (
            read_balance()
        )

        config = (
            read_symbol_config()
        )

        position = (
            read_position()
        )

    else:

        missing = {
            "http_status": None,
            "read_ok": False,
            "error_code": None,
            "error_message":
                "WEEX API credentials are missing",
        }

        balance = {
            **missing,
            "available_usdt": None,
            "total_usdt": None,
        }

        config = {
            **missing,
            "symbol": None,
            "symbol_match": False,
            "margin_mode": None,
            "margin_match": False,
            "separated_type": None,
            "cross_leverage": None,
            "long_leverage": None,
            "long_match": False,
            "short_leverage": None,
            "short_match": False,
            "config_ok": False,
        }

        position = {
            **missing,
            "position_rows": 0,
            "nonzero_position_rows": 0,
            "long_qty": 0.0,
            "short_qty": 0.0,
            "flat": False,
        }

    mark = (
        read_mark_price()
    )

    emit(
        "BALANCE_HTTP_STATUS",
        balance["http_status"],
    )

    emit(
        "BALANCE_READ_OK",
        balance["read_ok"],
    )

    emit(
        "AVAILABLE_USDT",
        balance["available_usdt"],
    )

    emit(
        "TOTAL_USDT",
        balance["total_usdt"],
    )

    emit(
        "BALANCE_ERROR_CODE",
        balance["error_code"],
    )

    emit(
        "BALANCE_ERROR_MESSAGE",
        balance["error_message"],
    )

    emit(
        "MARK_PRICE_HTTP_STATUS",
        mark["http_status"],
    )

    emit(
        "MARK_PRICE_READ_OK",
        mark["read_ok"],
    )

    emit(
        "MARK_PRICE_SYMBOL",
        mark["symbol"],
    )

    emit(
        "MARK_PRICE",
        mark["price"],
    )

    emit(
        "MARK_PRICE_ERROR_CODE",
        mark["error_code"],
    )

    emit(
        "MARK_PRICE_ERROR_MESSAGE",
        mark["error_message"],
    )

    emit(
        "POSITION_HTTP_STATUS",
        position["http_status"],
    )

    emit(
        "POSITION_READ_OK",
        position["read_ok"],
    )

    emit(
        "BTCUSDT_POSITION_ROWS",
        position["position_rows"],
    )

    emit(
        "BTCUSDT_NONZERO_POSITION_ROWS",
        position[
            "nonzero_position_rows"
        ],
    )

    emit(
        "BTCUSDT_LONG_QTY",
        position["long_qty"],
    )

    emit(
        "BTCUSDT_SHORT_QTY",
        position["short_qty"],
    )

    emit(
        "BTCUSDT_FLAT",
        position["flat"],
    )

    emit(
        "POSITION_ERROR_CODE",
        position["error_code"],
    )

    emit(
        "POSITION_ERROR_MESSAGE",
        position["error_message"],
    )

    emit(
        "SYMBOL_CONFIG_HTTP_STATUS",
        config["http_status"],
    )

    emit(
        "SYMBOL_CONFIG_READ_OK",
        config["read_ok"],
    )

    emit(
        "OBSERVED_SYMBOL",
        config["symbol"],
    )

    emit(
        "SYMBOL_MATCH",
        config["symbol_match"],
    )

    emit(
        "OBSERVED_MARGIN_MODE",
        config["margin_mode"],
    )

    emit(
        "TARGET_MARGIN_MODE",
        TARGET_MARGIN_MODE,
    )

    emit(
        "MARGIN_MODE_MATCH",
        config["margin_match"],
    )

    emit(
        "OBSERVED_SEPARATED_TYPE",
        config["separated_type"],
    )

    emit(
        "OBSERVED_CROSS_LEVERAGE",
        config["cross_leverage"],
    )

    emit(
        "OBSERVED_LONG_LEVERAGE",
        config["long_leverage"],
    )

    emit(
        "TARGET_LONG_LEVERAGE",
        int(
            TARGET_LONG_LEVERAGE
        ),
    )

    emit(
        "LONG_LEVERAGE_MATCH",
        config["long_match"],
    )

    emit(
        "OBSERVED_SHORT_LEVERAGE",
        config["short_leverage"],
    )

    emit(
        "TARGET_SHORT_LEVERAGE",
        int(
            TARGET_SHORT_LEVERAGE
        ),
    )

    emit(
        "SHORT_LEVERAGE_MATCH",
        config["short_match"],
    )

    emit(
        "CONFIG_RECONCILIATION_OK",
        config["config_ok"],
    )

    emit(
        "SYMBOL_CONFIG_ERROR_CODE",
        config["error_code"],
    )

    emit(
        "SYMBOL_CONFIG_ERROR_MESSAGE",
        config["error_message"],
    )

    section(
        f"{UNIT}: STRATEGY READINESS PROJECTION"
    )

    projection = (
        calculate_strategy_projection(
            balance[
                "available_usdt"
            ],
            mark["price"],
        )
    )

    emit(
        "ENTRY_PERCENT",
        ENTRY_PERCENT,
    )

    emit(
        "ENTRY_MARGIN_BUDGET",
        projection[
            "entry_margin_budget"
        ],
    )

    emit(
        "ENTRY_NOTIONAL_AT_100X",
        projection[
            "entry_notional"
        ],
    )

    emit(
        "RAW_ENTRY_QTY",
        projection[
            "raw_entry_qty"
        ],
    )

    emit(
        "ROUNDED_ENTRY_QTY",
        projection[
            "rounded_entry_qty"
        ],
    )

    emit(
        "ROUNDED_ENTRY_NOTIONAL",
        projection[
            "rounded_entry_notional"
        ],
    )

    emit(
        "ESTIMATED_ENTRY_MARGIN",
        projection[
            "estimated_entry_margin"
        ],
    )

    emit(
        "QTY_STEP",
        QTY_STEP,
    )

    emit(
        "MIN_QTY",
        MIN_QTY,
    )

    emit(
        "MAX_PYRAMID_ADDS",
        MAX_PYRAMID_ADDS,
    )

    emit(
        "PYRAMID_PERCENT",
        PYRAMID_PERCENT,
    )

    emit(
        "MAX_BACKUPS",
        MAX_BACKUPS,
    )

    emit(
        "BACKUP_PERCENT",
        BACKUP_PERCENT,
    )

    emit(
        "MAX_FUND_EXPOSURE_PERCENT",
        MAX_FUND_EXPOSURE_PERCENT,
    )

    emit(
        "MAX_ALLOWED_STRATEGY_MARGIN",
        projection[
            "max_allowed_strategy_margin"
        ],
    )

    emit(
        "PLANNED_MAX_STRATEGY_MARGIN",
        projection[
            "planned_max_strategy_margin"
        ],
    )

    emit(
        "PLANNED_EXPOSURE_WITHIN_CAP",
        projection[
            "planned_exposure_within_cap"
        ],
    )

    emit(
        "TP1_PERCENT",
        TP1_PERCENT,
    )

    emit(
        "TP1_TRIGGER_PERCENT",
        TP1_TRIGGER_PERCENT,
    )

    emit(
        "TP2_PERCENT",
        TP2_PERCENT,
    )

    emit(
        "TP2_TRIGGER_PERCENT",
        TP2_TRIGGER_PERCENT,
    )

    emit(
        "TP3_PERCENT",
        TP3_PERCENT,
    )

    emit(
        "TRAILING_DISTANCE_PERCENT",
        TRAILING_DISTANCE_PERCENT,
    )

    emit(
        "TP_ALLOCATION_SUM_OK",
        projection[
            "tp_sum_ok"
        ],
    )

    emit(
        "STRATEGY_CALCULATION_OK",
        projection[
            "calculation_ok"
        ],
    )

    section(
        f"{UNIT}: FINAL ACTIVATION ENV RECONCILIATION"
    )

    blockers: List[str] = []

    if not CREDENTIALS_PRESENT:

        blockers.append(
            "CREDENTIALS_MISSING"
        )

    if not balance["read_ok"]:

        blockers.append(
            "BALANCE_READ_FAILED"
        )

    if not mark["read_ok"]:

        blockers.append(
            "MARK_PRICE_READ_FAILED"
        )

    if not position["read_ok"]:

        blockers.append(
            "POSITION_RECONCILIATION_FAILED"
        )

    elif not position["flat"]:

        blockers.append(
            "BTCUSDT_NOT_FLAT"
        )

    if not config["read_ok"]:

        blockers.append(
            "SYMBOL_CONFIG_READ_FAILED"
        )

    else:

        if not config["symbol_match"]:

            blockers.append(
                "SYMBOL_MISMATCH"
            )

        if not config["margin_match"]:

            blockers.append(
                "MARGIN_MODE_MISMATCH"
            )

        if not config["long_match"]:

            blockers.append(
                "LONG_LEVERAGE_MISMATCH"
            )

        if not config["short_match"]:

            blockers.append(
                "SHORT_LEVERAGE_MISMATCH"
            )

    if not durable["local_durable"]:

        blockers.append(
            "TELEGRAM_DEDUPE_LOCAL_STORAGE_FAILED"
        )

    if not durable[
        "cross_deploy_durable"
    ]:

        blockers.append(
            "TELEGRAM_DEDUPE_NOT_CROSS_DEPLOY_DURABLE"
        )

    if not projection[
        "calculation_ok"
    ]:

        blockers.append(
            "ENTRY_SIZE_INVALID"
        )

    if not projection[
        "planned_exposure_within_cap"
    ]:

        blockers.append(
            "MAX_EXPOSURE_EXCEEDED"
        )

    if not projection[
        "tp_sum_ok"
    ]:

        blockers.append(
            "TP_ALLOCATION_INVALID"
        )

    if not safety_invariants_ok():

        blockers.append(
            "SAFETY_INVARIANT_FAILURE"
        )

    r35q_reconciliation_ok = (
        len(blockers) == 0
    )

    if r35q_reconciliation_ok:

        activation_env = "READY"

    else:

        activation_env = "MISMATCH"

    r35p_diagnostics_complete = True

    emit(
        "R35P_DIAGNOSTICS_COMPLETE",
        r35p_diagnostics_complete,
    )

    emit(
        "ACTIVATION_ENV",
        activation_env,
    )

    emit(
        "R35Q_RECONCILIATION_OK",
        r35q_reconciliation_ok,
    )

    emit(
        "BLOCKERS",
        (
            "NONE"
            if not blockers
            else ",".join(blockers)
        ),
    )

    emit(
        "REAL_ORDER_EXECUTION",
        REAL_ORDER_EXECUTION,
    )

    emit(
        "FIRST_REAL_ORDER_ALLOWED",
        FIRST_REAL_ORDER_ALLOWED,
    )

    emit(
        "DEMO_ORDER_EXECUTION",
        DEMO_ORDER_EXECUTION,
    )

    emit(
        "EXCHANGE_MUTATION_TRANSPORT_ENABLED",
        EXCHANGE_MUTATION_TRANSPORT_ENABLED,
    )

    emit(
        "ORDER_SUBMISSION_ENABLED",
        ORDER_SUBMISSION_ENABLED,
    )

    emit(
        "LEVERAGE_MUTATION_ENABLED",
        LEVERAGE_MUTATION_ENABLED,
    )

    emit(
        "MARGIN_MODE_MUTATION_ENABLED",
        MARGIN_MODE_MUTATION_ENABLED,
    )

    emit(
        "POSITION_MUTATION_ENABLED",
        POSITION_MUTATION_ENABLED,
    )

    emit(
        "AUTHENTICATED_WEEX_READS",
        AUTHENTICATED_WEEX_READS,
    )

    emit(
        "PUBLIC_MARKET_GETS",
        PUBLIC_MARKET_GETS,
    )

    emit(
        "EXCHANGE_NETWORK_WRITES",
        EXCHANGE_NETWORK_WRITES,
    )

    emit(
        "ORDER_SUBMISSIONS",
        ORDER_SUBMISSIONS,
    )

    emit(
        "LEVERAGE_MUTATIONS",
        LEVERAGE_MUTATIONS,
    )

    emit(
        "MARGIN_MODE_MUTATIONS",
        MARGIN_MODE_MUTATIONS,
    )

    emit(
        "POSITION_MUTATIONS",
        POSITION_MUTATIONS,
    )

    emit(
        "SAFETY_INVARIANTS_OK",
        safety_invariants_ok(),
    )

    emit(
        "TEST_STATUS",
        (
            "PASS"
            if r35q_reconciliation_ok
            else "FAIL"
        ),
    )

    emit(
        "EXECUTION_PERMISSION",
        "NOT_GRANTED",
    )

    emit(
        "REAL_ORDER_PATH",
        "ABSENT",
    )

    emit(
        "MUTATION_PATH",
        "ABSENT",
    )

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{UNIT}: HEARTBEAT={heartbeat} "
            f"ACTIVATION_ENV={activation_env} "
            f"R35Q_RECONCILIATION_OK={r35q_reconciliation_ok} "
            f"BALANCE_READ_OK={balance['read_ok']} "
            f"MARK_PRICE_READ_OK={mark['read_ok']} "
            f"BTCUSDT_FLAT={position['flat']} "
            f"CONFIG_RECONCILIATION_OK={config['config_ok']} "
            f"TELEGRAM_LOCAL_DURABLE={durable['local_durable']} "
            f"TELEGRAM_CROSS_DEPLOY_DURABLE={durable['cross_deploy_durable']} "
            f"AUTHENTICATED_WEEX_READS={AUTHENTICATED_WEEX_READS} "
            f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION} "
            f"SAFETY_INVARIANTS_OK={safety_invariants_ok()}"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


if __name__ == "__main__":
    main()

