
#!/usr/bin/env python3

"""
R36F.15.5 - STANDALONE DEMO RECONCILIATION TEST UNIT

PURPOSE
-------
Test reconciliation of the already accepted WEEX demo order:

    792989056504955607

WITHOUT modifying the frozen R36F.15.4.1 baseline.

THIS TEST UNIT IS STRICTLY READ-ONLY.

IT CAN:
    - Read WEEX demo order history
    - Locate the accepted demo order
    - Read WEEX demo positions
    - Match order -> symbol -> direction -> active position
    - Determine whether a second entry MUST be blocked
    - Inspect returned order fields for TP/SL information if WEEX supplies them
    - Produce explicit reconciliation PASS/FAIL diagnostics

IT CANNOT:
    - Place orders
    - Cancel orders
    - Close positions
    - Modify leverage
    - Modify margin mode
    - Add TP
    - Add SL
    - Create backup orders
    - Write to production trading endpoints
    - Create another demo trade

R36F.15.5 TEST PRINCIPLE
------------------------
If an active position or still-active opening order exists:

    DUPLICATE ENTRY BLOCKED = TRUE

No Telegram BUY/SELL environment command is required for this test.

After this standalone test passes, its reconciliation logic can be
merged into the proven R36F.15.4.1 60-second reevaluation loop.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError



# ============================================================
# R36F.15.5 IDENTIFICATION
# ============================================================

STAGE = "R36F.15.5"

TARGET_DEMO_ORDER_ID = str(
    os.getenv(
        "R36F155_TARGET_DEMO_ORDER_ID",
        "792989056504955607"
    )
).strip()

WEEX_BASE_URL = os.getenv(
    "WEEX_CONTRACT_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")


# ============================================================
# WEEX CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv("WEEX_API_KEY", "").strip()
WEEX_API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()

if not WEEX_API_SECRET:
    WEEX_API_SECRET = os.getenv("WEEX_SECRET_KEY", "").strip()

if not WEEX_API_SECRET:
    WEEX_API_SECRET = os.getenv("WEEX_SECRET", "").strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    ""
).strip()

if not WEEX_API_PASSPHRASE:
    WEEX_API_PASSPHRASE = os.getenv(
        "WEEX_PASSPHRASE",
        ""
    ).strip()


# ============================================================
# DOCUMENTED WEEX DEMO READ ENDPOINTS
# ============================================================

DEMO_ORDER_HISTORY_PATH = "/capi/v3/sim/order/history"

DEMO_ALL_POSITIONS_PATH = "/capi/v3/sim/position/allPosition"


# ============================================================
# ABSOLUTE WRITE LOCK
# ============================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
WRITE_TRANSPORT_ENABLED = False
PRODUCTION_MUTATION_ENABLED = False

ALLOWED_HTTP_METHODS = {"GET"}


# ============================================================
# OUTPUT HELPERS
# ============================================================

def utc_now():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def log(message=""):
    print(
        f"{utc_now()} {message}",
        flush=True
    )


def separator():
    print("-" * 100, flush=True)


def pass_log(name, detail=None):
    log(f"PASS: {name}")

    if detail is not None:
        log(f"      {detail}")


def fail_log(name, detail=None):
    log(f"FAIL: {name}")

    if detail is not None:
        log(f"      {detail}")


def diagnostic(name, condition, detail=None):
    if condition:
        pass_log(name, detail)
    else:
        fail_log(name, detail)

    return bool(condition)


# ============================================================
# HEALTH SERVER FOR RENDER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps(
            {
                "stage": STAGE,
                "status": "RUNNING",
                "mode": "READ_ONLY_RECONCILIATION_TEST",
                "targetDemoOrderId": TARGET_DEMO_ORDER_ID,
                "realExecution": False,
                "demoExecution": False,
                "writeTransport": False
            },
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


def start_health_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    def runner():
        server = HTTPServer(
            ("0.0.0.0", port),
            HealthHandler
        )

        log(
            f"{STAGE}: HEALTH SERVER STARTED ON PORT {port}"
        )

        server.serve_forever()

    thread = threading.Thread(
        target=runner,
        daemon=True
    )

    thread.start()


# ============================================================
# WEEX V3 SIGNATURE
# ============================================================

def make_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body=""
):

    method = method.upper()

    if method not in ALLOWED_HTTP_METHODS:
        raise RuntimeError(
            f"WRITE METHOD BLOCKED: {method}"
        )

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
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ============================================================
# AUTHENTICATED READ-ONLY WEEX GET
# ============================================================



def weex_get(path, params=None):

    if not path.startswith("/capi/v3/sim/"):
        raise RuntimeError(
            "NON-DEMO ENDPOINT BLOCKED BY R36F.15.5 TEST UNIT: "
            + path
        )

    params = params or {}

    query_string = urlencode(
        params,
        doseq=True
    )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body=""
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }

    url = WEEX_BASE_URL + path

    if query_string:
        url = url + "?" + query_string

    log(
        f"{STAGE} READ GET {path}"
    )

    request = Request(
        url=url,
        headers=headers,
        method="GET"
    )

    try:

        with urlopen(
            request,
            timeout=20
        ) as response:

            http_status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            try:
                data = json.loads(raw)

            except Exception:
                data = None

            return {
                "ok": http_status == 200,
                "http": http_status,
                "data": data,
                "text": raw,
                "exception_type": None,
                "exception": None
            }

    except HTTPError as exc:

        try:
            raw = exc.read().decode(
                "utf-8",
                errors="replace"
            )

        except Exception:
            raw = str(exc)

        try:
            data = json.loads(raw)

        except Exception:
            data = None

        return {
            "ok": False,
            "http": exc.code,
            "data": data,
            "text": raw,
            "exception_type": "HTTPError",
            "exception": str(exc)
        }

    except URLError as exc:

        return {
            "ok": False,
            "http": None,
            "data": None,
            "text": None,
            "exception_type": "URLError",
            "exception": str(exc)
        }

    except Exception as exc:

        return {
            "ok": False,
            "http": None,
            "data": None,
            "text": None,
            "exception_type": type(exc).__name__,
            "exception": str(exc)
        }

def weex_get(path, params=None):

    if not path.startswith("/capi/v3/sim/"):
        raise RuntimeError(
            "NON-DEMO ENDPOINT BLOCKED BY R36F.15.5 TEST UNIT: "
            + path
        )

    params = params or {}

    query_string = urlencode(
        params,
        doseq=True
    )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body=""
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }

    url = WEEX_BASE_URL + path

    log(
        f"{STAGE} READ GET {path}"
    )

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=20
        )

    except Exception as exc:

        return {
            "ok": False,
            "http": None,
            "data": None,
            "text": None,
            "exception_type": type(exc).__name__,
            "exception": str(exc)
        }

    text = response.text

    try:
        data = response.json()

    except Exception:
        data = None

    return {
        "ok": response.status_code == 200,
        "http": response.status_code,
        "data": data,
        "text": text,
        "exception_type": None,
        "exception": None
    }


# ============================================================
# GENERIC RESPONSE EXTRACTION
# ============================================================

def extract_list(data):

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    possible_keys = (
        "data",
        "list",
        "rows",
        "orders",
        "positions",
        "result"
    )

    for key in possible_keys:

        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):

            for nested_key in (
                "list",
                "rows",
                "orders",
                "positions",
                "data"
            ):

                nested_value = value.get(
                    nested_key
                )

                if isinstance(
                    nested_value,
                    list
                ):
                    return nested_value

    return []


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def safe_upper(value):

    if value is None:
        return ""

    return str(value).strip().upper()


def safe_float(value):

    try:
        return float(value)

    except Exception:
        return 0.0


def get_order_id(order):

    if not isinstance(order, dict):
        return ""

    for key in (
        "orderId",
        "order_id",
        "id"
    ):

        value = order.get(key)

        if value is not None:
            return str(value).strip()

    return ""


def get_symbol(item):

    if not isinstance(item, dict):
        return ""

    return str(
        item.get("symbol", "")
    ).strip()


def get_position_side(item):

    if not isinstance(item, dict):
        return ""

    for key in (
        "positionSide",
        "position_side",
        "side"
    ):

        value = item.get(key)

        value_upper = safe_upper(value)

        if value_upper in (
            "LONG",
            "SHORT"
        ):
            return value_upper

    side = safe_upper(
        item.get("side")
    )

    if side == "BUY":
        return "LONG"

    if side == "SELL":
        return "SHORT"

    return ""


def get_order_status(order):

    if not isinstance(order, dict):
        return "UNKNOWN"

    for key in (
        "status",
        "orderStatus",
        "state"
    ):

        value = order.get(key)

        if value is not None:
            return safe_upper(value)

    return "UNKNOWN"


def get_position_size(position):

    if not isinstance(position, dict):
        return 0.0

    for key in (
        "size",
        "positionAmt",
        "positionSize",
        "quantity",
        "qty"
    ):

        if key in position:
            return abs(
                safe_float(
                    position.get(key)
                )
            )

    return 0.0


# ============================================================
# ORDER LOOKUP
# ============================================================

def find_target_order(order_rows):

    for row in order_rows:

        if get_order_id(row) == TARGET_DEMO_ORDER_ID:
            return row

    return None


# ============================================================
# POSITION MATCHING
# ============================================================

def find_matching_positions(
    position_rows,
    target_symbol,
    target_direction
):

    matches = []

    normalized_symbol = safe_upper(
        target_symbol
    )

    for position in position_rows:

        position_symbol = safe_upper(
            get_symbol(position)
        )

        position_direction = get_position_side(
            position
        )

        size = get_position_size(
            position
        )

        if normalized_symbol:

            if position_symbol != normalized_symbol:
                continue

        if target_direction:

            if position_direction != target_direction:
                continue

        if size <= 0:
            continue

        matches.append(
            position
        )

    return matches


# ============================================================
# PROTECTION FIELD INSPECTION
# ============================================================

def inspect_order_protection_fields(order):

    if not isinstance(order, dict):
        return {
            "tp_field_found": False,
            "tp_value": None,
            "sl_field_found": False,
            "sl_value": None
        }

    tp_keys = (
        "tpTriggerPrice",
        "takeProfitPrice",
        "takeProfit",
        "tpPrice",
        "presetTakeProfitPrice"
    )

    sl_keys = (
        "slTriggerPrice",
        "stopLossPrice",
        "stopLoss",
        "slPrice",
        "presetStopLossPrice"
    )

    tp_field_found = False
    tp_value = None

    sl_field_found = False
    sl_value = None

    for key in tp_keys:

        if key in order:
            tp_field_found = True
            tp_value = order.get(key)
            break

    for key in sl_keys:

        if key in order:
            sl_field_found = True
            sl_value = order.get(key)
            break

    return {
        "tp_field_found": tp_field_found,
        "tp_value": tp_value,
        "sl_field_found": sl_field_found,
        "sl_value": sl_value
    }


# ============================================================
# DUPLICATE ENTRY POLICY
# ============================================================

OPEN_ORDER_STATES = {
    "NEW",
    "OPEN",
    "PENDING",
    "LIVE",
    "PARTIALLY_FILLED",
    "PARTIAL_FILLED",
    "PARTIALLYFILLED",
    "CREATED",
    "ACCEPTED"
}

TERMINAL_ORDER_STATES = {
    "FILLED",
    "CANCELED",
    "CANCELLED",
    "REJECTED",
    "EXPIRED"
}


def evaluate_duplicate_gate(
    order_found,
    order_status,
    active_position_found
):

    if active_position_found:

        return {
            "blocked": True,
            "reason": "POSITION_ALREADY_EXISTS"
        }

    if order_found and order_status in OPEN_ORDER_STATES:

        return {
            "blocked": True,
            "reason": "ENTRY_ORDER_STILL_ACTIVE"
        }

    if (
        order_found
        and order_status == "FILLED"
        and not active_position_found
    ):

        return {
            "blocked": True,
            "reason": "FILLED_ORDER_FOUND_BUT_POSITION_NOT_FOUND_REQUIRES_RECONCILIATION"
        }

    if (
        order_found
        and order_status == "UNKNOWN"
    ):

        return {
            "blocked": True,
            "reason": "ORDER_FOUND_WITH_UNKNOWN_STATUS_CONSERVATIVE_BLOCK"
        }

    return {
        "blocked": False,
        "reason": "NO_ACTIVE_POSITION_OR_ACTIVE_ENTRY_ORDER_FOUND"
    }


# ============================================================
# CREDENTIAL CHECK
# ============================================================

def credentials_ready():

    missing = []

    if not WEEX_API_KEY:
        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_API_SECRET:
        missing.append(
            "WEEX_API_SECRET/WEEX_SECRET_KEY/WEEX_SECRET"
        )

    if not WEEX_API_PASSPHRASE:
        missing.append(
            "WEEX_API_PASSPHRASE/WEEX_PASSPHRASE"
        )

    return missing


# ============================================================
# MAIN RECONCILIATION TEST
# ============================================================

def run_reconciliation_test():

    separator()

    log(
        f"{STAGE}: STANDALONE DEMO ORDER RECONCILIATION TEST"
    )

    log(
        f"{STAGE}: TARGET DEMO ORDER ID = {TARGET_DEMO_ORDER_ID}"
    )

    separator()

    diagnostic(
        "R36F155_REAL_ORDER_EXECUTION_DISABLED",
        REAL_ORDER_EXECUTION is False
    )

    diagnostic(
        "R36F155_DEMO_ORDER_EXECUTION_DISABLED",
        DEMO_ORDER_EXECUTION is False
    )

    diagnostic(
        "R36F155_WRITE_TRANSPORT_DISABLED",
        WRITE_TRANSPORT_ENABLED is False
    )

    diagnostic(
        "R36F155_PRODUCTION_MUTATION_DISABLED",
        PRODUCTION_MUTATION_ENABLED is False
    )

    diagnostic(
        "R36F155_ONLY_HTTP_GET_ALLOWED",
        ALLOWED_HTTP_METHODS == {"GET"}
    )

    missing_credentials = credentials_ready()

    credential_ok = (
        len(missing_credentials) == 0
    )

    diagnostic(
        "R36F155_WEEX_CREDENTIALS_PRESENT",
        credential_ok,
        (
            "all required credential variables available"
            if credential_ok
            else "missing=" + ",".join(missing_credentials)
        )
    )

    if not credential_ok:

        separator()

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = MISSING_WEEX_CREDENTIALS"
        )

        return False

    separator()

    log(
        f"{STAGE} STEP 1: READ DEMO ORDER HISTORY"
    )

    order_history_result = weex_get(
        DEMO_ORDER_HISTORY_PATH,
        {
            "limit": 1000,
            "page": 0
        }
    )

    diagnostic(
        "R36F155_DEMO_ORDER_HISTORY_HTTP_200",
        order_history_result["http"] == 200,
        f"http={order_history_result['http']}"
    )

    if not order_history_result["ok"]:

        log(
            f"{STAGE} ORDER HISTORY RESPONSE = "
            f"{order_history_result['text']}"
        )

        log(
            f"{STAGE} ORDER HISTORY EXCEPTION = "
            f"{order_history_result['exception']}"
        )

        separator()

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = DEMO_ORDER_HISTORY_READ_FAILED"
        )

        return False

    order_rows = extract_list(
        order_history_result["data"]
    )

    log(
        f"{STAGE} DEMO ORDER HISTORY ROWS = {len(order_rows)}"
    )

    target_order = find_target_order(
        order_rows
    )

    order_found = (
        target_order is not None
    )

    diagnostic(
        "R36F155_TARGET_DEMO_ORDER_FOUND",
        order_found,
        f"orderId={TARGET_DEMO_ORDER_ID}"
    )

    if target_order is not None:

        target_symbol = get_symbol(
            target_order
        )

        target_direction = get_position_side(
            target_order
        )

        target_status = get_order_status(
            target_order
        )

        log(
            f"{STAGE} RECONCILED ORDER ID = "
            f"{get_order_id(target_order)}"
        )

        log(
            f"{STAGE} RECONCILED ORDER SYMBOL = "
            f"{target_symbol}"
        )

        log(
            f"{STAGE} RECONCILED ORDER DIRECTION = "
            f"{target_direction}"
        )

        log(
            f"{STAGE} RECONCILED ORDER STATUS = "
            f"{target_status}"
        )

        log(
            f"{STAGE} RECONCILED ORDER TYPE = "
            f"{target_order.get('type')}"
        )

        log(
            f"{STAGE} RECONCILED ORDER ORIGINAL QTY = "
            f"{target_order.get('origQty')}"
        )

        log(
            f"{STAGE} RECONCILED ORDER EXECUTED QTY = "
            f"{target_order.get('executedQty')}"
        )

        log(
            f"{STAGE} RECONCILED ORDER AVG PRICE = "
            f"{target_order.get('avgPrice')}"
        )

        log(
            f"{STAGE} RECONCILED ORDER CLIENT ID = "
            f"{target_order.get('clientOrderId')}"
        )

    else:

        target_symbol = ""
        target_direction = ""
        target_status = "NOT_FOUND"

    separator()

    log(
        f"{STAGE} STEP 2: READ ALL DEMO POSITIONS"
    )

    positions_result = weex_get(
        DEMO_ALL_POSITIONS_PATH
    )

    diagnostic(
        "R36F155_DEMO_POSITIONS_HTTP_200",
        positions_result["http"] == 200,
        f"http={positions_result['http']}"
    )

    if not positions_result["ok"]:

        log(
            f"{STAGE} POSITIONS RESPONSE = "
            f"{positions_result['text']}"
        )

        log(
            f"{STAGE} POSITIONS EXCEPTION = "
            f"{positions_result['exception']}"
        )

        separator()

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = DEMO_POSITION_READ_FAILED"
        )

        return False

    position_rows = extract_list(
        positions_result["data"]
    )

    log(
        f"{STAGE} DEMO POSITION ROWS = "
        f"{len(position_rows)}"
    )

    matching_positions = find_matching_positions(
        position_rows,
        target_symbol,
        target_direction
    )

    active_position_found = (
        len(matching_positions) > 0
    )

    diagnostic(
        "R36F155_MATCHING_ACTIVE_POSITION_FOUND",
        active_position_found,
        (
            f"symbol={target_symbol} "
            f"direction={target_direction}"
        )
    )

    if active_position_found:

        for index, position in enumerate(
            matching_positions,
            start=1
        ):

            log(
                f"{STAGE} MATCHING POSITION {index} ID = "
                f"{position.get('id')}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} SYMBOL = "
                f"{get_symbol(position)}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} SIDE = "
                f"{get_position_side(position)}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} SIZE = "
                f"{get_position_size(position)}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} LEVERAGE = "
                f"{position.get('leverage')}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} MARGIN TYPE = "
                f"{position.get('marginType')}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} "
                f"OPENING ORDER ID = "
                f"{position.get('separatedOpenOrderId')}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} "
                f"OPEN VALUE = "
                f"{position.get('openValue')}"
            )

            log(
                f"{STAGE} MATCHING POSITION {index} "
                f"UNREALIZED PNL = "
                f"{position.get('unrealizePnl')}"
            )

    separator()

    log(
        f"{STAGE} STEP 3: ORDER/POSITION RECONCILIATION"
    )

    order_position_direction_match = (
        order_found
        and active_position_found
        and target_direction
        in ("LONG", "SHORT")
    )

    if order_found and active_position_found:

        diagnostic(
            "R36F155_ORDER_POSITION_DIRECTION_RECONCILED",
            order_position_direction_match,
            (
                f"orderDirection={target_direction} "
                f"positionDirection="
                f"{get_position_side(matching_positions[0])}"
            )
        )

    else:

        log(
            f"{STAGE} ORDER/POSITION DIRECTION MATCH = "
            f"NOT_TESTABLE"
        )

    separator()

    log(
        f"{STAGE} STEP 4: TP/SL READ-BACK INSPECTION"
    )

    protection = inspect_order_protection_fields(
        target_order
    )

    log(
        f"{STAGE} ORDER TP FIELD RETURNED = "
        f"{protection['tp_field_found']}"
    )

    log(
        f"{STAGE} ORDER TP VALUE = "
        f"{protection['tp_value']}"
    )

    log(
        f"{STAGE} ORDER SL FIELD RETURNED = "
        f"{protection['sl_field_found']}"
    )

    log(
        f"{STAGE} ORDER SL VALUE = "
        f"{protection['sl_value']}"
    )

    if (
        protection["tp_field_found"]
        or protection["sl_field_found"]
    ):

        log(
            f"{STAGE} PROTECTION READ-BACK = "
            f"PARTIALLY_OR_FULLY_RETURNED_BY_ORDER_HISTORY"
        )

    else:

        log(
            f"{STAGE} PROTECTION READ-BACK = "
            f"NOT_IN_DOCUMENTED_DEMO_ORDER_HISTORY_RESPONSE"
        )

        log(
            f"{STAGE} PROTECTION VERIFICATION = "
            f"NOT_INFERRED"
        )

        log(
            f"{STAGE} PROTECTION VERIFICATION REASON = "
            f"NO_DOCUMENTED_INDEPENDENT_DEMO_TP_SL_READ_ENDPOINT_USED"
        )

    separator()

    log(
        f"{STAGE} STEP 5: DUPLICATE ENTRY GATE"
    )

    duplicate_gate = evaluate_duplicate_gate(
        order_found=order_found,
        order_status=target_status,
        active_position_found=active_position_found
    )

    duplicate_blocked = (
        duplicate_gate["blocked"]
    )

    log(
        f"{STAGE} DUPLICATE ENTRY BLOCKED = "
        f"{duplicate_blocked}"
    )

    log(
        f"{STAGE} DUPLICATE BLOCK REASON = "
        f"{duplicate_gate['reason']}"
    )

    if active_position_found:

        diagnostic(
            "R36F155_POSITION_ALREADY_EXISTS_BLOCK",
            duplicate_blocked,
            duplicate_gate["reason"]
        )

    separator()

    log(
        f"{STAGE} STEP 6: ZERO-WRITE INVARIANTS"
    )

    diagnostic(
        "R36F155_REAL_MONEY_ZERO_WRITE_INVARIANT",
        REAL_ORDER_EXECUTION is False
        and WRITE_TRANSPORT_ENABLED is False
        and PRODUCTION_MUTATION_ENABLED is False
    )

    diagnostic(
        "R36F155_DEMO_ZERO_WRITE_INVARIANT",
        DEMO_ORDER_EXECUTION is False
    )

    diagnostic(
        "R36F155_HTTP_WRITE_METHODS_UNAVAILABLE",
        ALLOWED_HTTP_METHODS == {"GET"}
    )

    separator()

    order_reconciled = order_found

    position_reconciled = (
        active_position_found
        if target_status == "FILLED"
        else True
    )

    safety_pass = (
        REAL_ORDER_EXECUTION is False
        and DEMO_ORDER_EXECUTION is False
        and WRITE_TRANSPORT_ENABLED is False
        and PRODUCTION_MUTATION_ENABLED is False
        and ALLOWED_HTTP_METHODS == {"GET"}
    )

    reconciliation_pass = (
        order_reconciled
        and safety_pass
        and duplicate_blocked
    )

    log(
        f"{STAGE} TARGET ORDER RECONCILED = "
        f"{order_reconciled}"
    )

    log(
        f"{STAGE} ACTIVE POSITION RECONCILED = "
        f"{active_position_found}"
    )

    log(
        f"{STAGE} POSITION EXPECTATION SATISFIED = "
        f"{position_reconciled}"
    )

    log(
        f"{STAGE} DUPLICATE ENTRY PROTECTION RESULT = "
        f"{'BLOCK' if duplicate_blocked else 'ALLOW'}"
    )

    log(
        f"{STAGE} REAL MONEY EXECUTION = False"
    )

    log(
        f"{STAGE} DEMO ORDER EXECUTION = False"
    )

    log(
        f"{STAGE} WRITE TRANSPORT = False"
    )

    if reconciliation_pass:

        log(
            f"{STAGE} FINAL STATUS = PASS"
        )

        log(
            f"{STAGE} FINAL REASON = "
            f"TARGET_ORDER_RECONCILED_AND_DUPLICATE_ENTRY_BLOCKED"
        )

    else:

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        if not order_found:

            log(
                f"{STAGE} FINAL REASON = "
                f"TARGET_DEMO_ORDER_NOT_FOUND"
            )

        elif not duplicate_blocked:

            log(
                f"{STAGE} FINAL REASON = "
                f"DUPLICATE_ENTRY_NOT_BLOCKED"
            )

        else:

            log(
                f"{STAGE} FINAL REASON = "
                f"RECONCILIATION_REQUIREMENTS_NOT_MET"
            )

    separator()

    log(
        "NO REAL ORDER WAS SENT"
    )

    log(
        "NO DEMO ORDER WAS SENT"
    )

    log(
        "NO POSITION WAS CLOSED"
    )

    log(
        "NO TP/SL ORDER WAS CREATED"
    )

    log(
        "NO PRODUCTION EXCHANGE MUTATION WAS SENT"
    )

    separator()

    return reconciliation_pass


# ============================================================
# MAIN
# ============================================================

def main():

    start_health_server()

    time.sleep(1)

    try:

        result = run_reconciliation_test()

    except Exception as exc:

        separator()

        log(
            f"{STAGE} UNHANDLED TEST EXCEPTION = "
            f"{type(exc).__name__}: {exc}"
        )

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = "
            f"UNHANDLED_TEST_EXCEPTION"
        )

        separator()

        result = False

    log(
        f"{STAGE} TEST COMPLETE = {result}"
    )

    log(
        f"{STAGE} HEALTH SERVER REMAINS RUNNING"
    )

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
