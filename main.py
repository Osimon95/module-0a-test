
#!/usr/bin/env python3

"""
R36F.15.5
FRESH STANDALONE WEEX DEMO RECONCILIATION TEST UNIT

TARGET:
    Existing accepted WEEX demo order:
    792989056504955607

PURPOSE:
    Prove read-back and duplicate-entry protection BEFORE merging
    reconciliation logic into the frozen R36F.15.4.1 baseline.

STRICT SAFETY:
    - READ ONLY
    - GET requests only
    - NO new demo order
    - NO real order
    - NO close order
    - NO cancel order
    - NO leverage change
    - NO margin-mode change
    - NO TP/SL creation
    - NO production mutation

This standalone unit uses ONLY Python standard-library modules.
There is deliberately NO requests dependency.
"""

import os
import time
import json
import hmac
import hashlib
import base64
import threading

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ============================================================
# STAGE
# ============================================================

STAGE = "R36F.15.5"

TARGET_ORDER_ID = str(
    os.getenv(
        "R36F155_TARGET_DEMO_ORDER_ID",
        "792989056504955607"
    )
).strip()

WEEX_BASE_URL = str(
    os.getenv(
        "WEEX_CONTRACT_BASE_URL",
        "https://api-contract.weex.com"
    )
).strip().rstrip("/")


# ============================================================
# CREDENTIALS
# ============================================================

WEEX_API_KEY = str(
    os.getenv(
        "WEEX_API_KEY",
        ""
    )
).strip()

WEEX_API_SECRET = str(
    os.getenv(
        "WEEX_API_SECRET",
        ""
    )
).strip()

if not WEEX_API_SECRET:
    WEEX_API_SECRET = str(
        os.getenv(
            "WEEX_SECRET_KEY",
            ""
        )
    ).strip()

if not WEEX_API_SECRET:
    WEEX_API_SECRET = str(
        os.getenv(
            "WEEX_SECRET",
            ""
        )
    ).strip()

WEEX_API_PASSPHRASE = str(
    os.getenv(
        "WEEX_API_PASSPHRASE",
        ""
    )
).strip()

if not WEEX_API_PASSPHRASE:
    WEEX_API_PASSPHRASE = str(
        os.getenv(
            "WEEX_PASSPHRASE",
            ""
        )
    ).strip()


# ============================================================
# DOCUMENTED WEEX DEMO READ ENDPOINTS
# ============================================================

DEMO_ORDER_HISTORY_PATH = (
    "/capi/v3/sim/order/history"
)

DEMO_POSITION_PATH = (
    "/capi/v3/sim/position/allPosition"
)


# ============================================================
# HARD SAFETY LOCKS
# ============================================================

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

WRITE_TRANSPORT_ENABLED = False

PRODUCTION_MUTATION_ENABLED = False

ALLOWED_HTTP_METHODS = {
    "GET"
}


# ============================================================
# LOGGING
# ============================================================

def utc_now():

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(message=""):

    print(
        f"{utc_now()} {message}",
        flush=True
    )


def separator():

    print(
        "-" * 100,
        flush=True
    )


def pass_log(name, detail=None):

    log(
        f"PASS: {name}"
    )

    if detail is not None:

        log(
            f"      {detail}"
        )


def fail_log(name, detail=None):

    log(
        f"FAIL: {name}"
    )

    if detail is not None:

        log(
            f"      {detail}"
        )


def diagnostic(
    name,
    condition,
    detail=None
):

    condition = bool(
        condition
    )

    if condition:

        pass_log(
            name,
            detail
        )

    else:

        fail_log(
            name,
            detail
        )

    return condition


# ============================================================
# RENDER HEALTH SERVER
# ============================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        payload = {
            "stage": STAGE,
            "status": "RUNNING",
            "mode": (
                "STANDALONE_READ_ONLY_DEMO_RECONCILIATION"
            ),
            "targetOrderId": TARGET_ORDER_ID,
            "realExecution": False,
            "demoExecution": False,
            "writeTransport": False
        }

        body = json.dumps(
            payload,
            separators=(",", ":")
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(
                len(body)
            )
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args
    ):

        return


def start_health_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    def run_server():

        server = HTTPServer(
            (
                "0.0.0.0",
                port
            ),
            HealthHandler
        )

        log(
            f"{STAGE}: "
            f"HEALTH SERVER STARTED "
            f"ON PORT {port}"
        )

        server.serve_forever()

    thread = threading.Thread(
        target=run_server,
        daemon=True
    )

    thread.start()


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_upper(value):

    if value is None:
        return ""

    return str(
        value
    ).strip().upper()


def safe_float(value):

    try:

        return float(
            value
        )

    except Exception:

        return 0.0


def credentials_missing():

    missing = []

    if not WEEX_API_KEY:

        missing.append(
            "WEEX_API_KEY"
        )

    if not WEEX_API_SECRET:

        missing.append(
            "WEEX_API_SECRET"
        )

    if not WEEX_API_PASSPHRASE:

        missing.append(
            "WEEX_API_PASSPHRASE"
        )

    return missing


# ============================================================
# WEEX SIGNATURE
# ============================================================

def make_signature(
    timestamp,
    method,
    request_path,
    query_string=""
):

    method = str(
        method
    ).upper()

    if method not in ALLOWED_HTTP_METHODS:

        raise RuntimeError(
            f"HTTP METHOD BLOCKED: "
            f"{method}"
        )

    message = (
        str(timestamp)
        + method
        + request_path
    )

    if query_string:

        message += (
            "?"
            + query_string
        )

    signature_bytes = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256
    ).digest()

    return base64.b64encode(
        signature_bytes
    ).decode(
        "utf-8"
    )


# ============================================================
# STRICT READ-ONLY HTTP TRANSPORT
# ============================================================

def weex_get(
    path,
    params=None
):

    if not path.startswith(
        "/capi/v3/sim/"
    ):

        raise RuntimeError(
            "NON-DEMO ENDPOINT BLOCKED: "
            + path
        )

    params = (
        params
        if isinstance(
            params,
            dict
        )
        else {}
    )

    query_string = urlencode(
        params,
        doseq=True
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = make_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string
    )

    headers = {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json"
    }

    url = (
        WEEX_BASE_URL
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    log(
        f"{STAGE} READ GET "
        f"{path}"
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

            status = int(
                response.getcode()
            )

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            try:

                data = json.loads(
                    raw
                )

            except Exception:

                data = None

            return {
                "ok":
                    status == 200,

                "http":
                    status,

                "data":
                    data,

                "text":
                    raw,

                "exception":
                    None,

                "exception_type":
                    None
            }

    except HTTPError as exc:

        try:

            raw = exc.read().decode(
                "utf-8",
                errors="replace"
            )

        except Exception:

            raw = str(
                exc
            )

        try:

            data = json.loads(
                raw
            )

        except Exception:

            data = None

        return {
            "ok":
                False,

            "http":
                int(
                    exc.code
                ),

            "data":
                data,

            "text":
                raw,

            "exception":
                str(exc),

            "exception_type":
                "HTTPError"
        }

    except URLError as exc:

        return {
            "ok":
                False,

            "http":
                None,

            "data":
                None,

            "text":
                None,

            "exception":
                str(exc),

            "exception_type":
                "URLError"
        }

    except Exception as exc:

        return {
            "ok":
                False,

            "http":
                None,

            "data":
                None,

            "text":
                None,

            "exception":
                str(exc),

            "exception_type":
                type(
                    exc
                ).__name__
        }


# ============================================================
# RESPONSE NORMALIZATION
# ============================================================

def extract_rows(data):

    if isinstance(
        data,
        list
    ):

        return data

    if not isinstance(
        data,
        dict
    ):

        return []

    candidates = [
        "data",
        "list",
        "rows",
        "orders",
        "positions",
        "result"
    ]

    for key in candidates:

        value = data.get(
            key
        )

        if isinstance(
            value,
            list
        ):

            return value

        if isinstance(
            value,
            dict
        ):

            for nested_key in [
                "data",
                "list",
                "rows",
                "orders",
                "positions"
            ]:

                nested = value.get(
                    nested_key
                )

                if isinstance(
                    nested,
                    list
                ):

                    return nested

    return []


# ============================================================
# ORDER HELPERS
# ============================================================

def order_id(order):

    if not isinstance(
        order,
        dict
    ):

        return ""

    for key in [
        "orderId",
        "order_id",
        "id"
    ]:

        value = order.get(
            key
        )

        if value is not None:

            return str(
                value
            ).strip()

    return ""


def order_symbol(order):

    if not isinstance(
        order,
        dict
    ):

        return ""

    return str(
        order.get(
            "symbol",
            ""
        )
    ).strip()


def order_direction(order):

    if not isinstance(
        order,
        dict
    ):

        return ""

    position_side = safe_upper(
        order.get(
            "positionSide"
        )
    )

    if position_side in [
        "LONG",
        "SHORT"
    ]:

        return position_side

    side = safe_upper(
        order.get(
            "side"
        )
    )

    if side == "BUY":

        return "LONG"

    if side == "SELL":

        return "SHORT"

    return ""


def order_status(order):

    if not isinstance(
        order,
        dict
    ):

        return "UNKNOWN"

    for key in [
        "status",
        "orderStatus",
        "state"
    ]:

        value = order.get(
            key
        )

        if value is not None:

            return safe_upper(
                value
            )

    return "UNKNOWN"


def find_target_order(rows):

    for row in rows:

        if (
            order_id(row)
            == TARGET_ORDER_ID
        ):

            return row

    return None


# ============================================================
# POSITION HELPERS
# ============================================================

def position_symbol(position):

    if not isinstance(
        position,
        dict
    ):

        return ""

    return str(
        position.get(
            "symbol",
            ""
        )
    ).strip()


def position_side(position):

    if not isinstance(
        position,
        dict
    ):

        return ""

    side = safe_upper(
        position.get(
            "side"
        )
    )

    if side in [
        "LONG",
        "SHORT"
    ]:

        return side

    side = safe_upper(
        position.get(
            "positionSide"
        )
    )

    if side in [
        "LONG",
        "SHORT"
    ]:

        return side

    return ""


def position_size(position):

    if not isinstance(
        position,
        dict
    ):

        return 0.0

    for key in [
        "size",
        "positionSize",
        "positionAmt",
        "quantity",
        "qty"
    ]:

        if key in position:

            return abs(
                safe_float(
                    position.get(
                        key
                    )
                )
            )

    return 0.0


def active_positions(
    rows
):

    active = []

    for row in rows:

        if position_size(
            row
        ) > 0:

            active.append(
                row
            )

    return active


def matching_positions(
    rows,
    symbol,
    direction
):

    result = []

    wanted_symbol = safe_upper(
        symbol
    )

    wanted_direction = safe_upper(
        direction
    )

    for row in rows:

        current_symbol = safe_upper(
            position_symbol(
                row
            )
        )

        current_direction = safe_upper(
            position_side(
                row
            )
        )

        current_size = position_size(
            row
        )

        if current_size <= 0:

            continue

        if (
            wanted_symbol
            and current_symbol
            != wanted_symbol
        ):

            continue

        if (
            wanted_direction
            and current_direction
            != wanted_direction
        ):

            continue

        result.append(
            row
        )

    return result


# ============================================================
# PROTECTION FIELD INSPECTION
# ============================================================

def protection_fields(
    order
):

    result = {
        "tp_field":
            None,

        "tp_value":
            None,

        "sl_field":
            None,

        "sl_value":
            None
    }

    if not isinstance(
        order,
        dict
    ):

        return result

    tp_keys = [
        "tpTriggerPrice",
        "takeProfitPrice",
        "takeProfit",
        "tpPrice",
        "presetTakeProfitPrice"
    ]

    sl_keys = [
        "slTriggerPrice",
        "stopLossPrice",
        "stopLoss",
        "slPrice",
        "presetStopLossPrice"
    ]

    for key in tp_keys:

        if key in order:

            result[
                "tp_field"
            ] = key

            result[
                "tp_value"
            ] = order.get(
                key
            )

            break

    for key in sl_keys:

        if key in order:

            result[
                "sl_field"
            ] = key

            result[
                "sl_value"
            ] = order.get(
                key
            )

            break

    return result


# ============================================================
# DUPLICATE ENTRY GATE
# ============================================================

OPEN_STATES = {
    "NEW",
    "OPEN",
    "PENDING",
    "LIVE",
    "ACCEPTED",
    "CREATED",
    "PARTIALLY_FILLED",
    "PARTIAL_FILLED",
    "PARTIALLYFILLED"
}


def duplicate_gate(
    target_order_found,
    status,
    matching_position_found
):

    if matching_position_found:

        return {
            "blocked":
                True,

            "reason":
                "POSITION_ALREADY_EXISTS"
        }

    if (
        target_order_found
        and status
        in OPEN_STATES
    ):

        return {
            "blocked":
                True,

            "reason":
                "OPEN_ENTRY_ORDER_ALREADY_EXISTS"
        }

    if (
        target_order_found
        and status
        == "FILLED"
    ):

        return {
            "blocked":
                True,

            "reason":
                (
                    "FILLED_ORDER_FOUND_POSITION_REQUIRES_"
                    "CONSERVATIVE_RECONCILIATION"
                )
        }

    if (
        target_order_found
        and status
        == "UNKNOWN"
    ):

        return {
            "blocked":
                True,

            "reason":
                "UNKNOWN_ORDER_STATUS_CONSERVATIVE_BLOCK"
        }

    return {
        "blocked":
            False,

        "reason":
            "NO_EXISTING_ENTRY_OR_POSITION_FOUND"
    }


# ============================================================
# MAIN TEST
# ============================================================

def run_test():

    separator()

    log(
        f"{STAGE}: "
        f"FRESH STANDALONE DEMO "
        f"RECONCILIATION TEST"
    )

    log(
        f"{STAGE}: "
        f"TARGET DEMO ORDER ID = "
        f"{TARGET_ORDER_ID}"
    )

    separator()

    # --------------------------------------------------------
    # SAFETY CHECKS
    # --------------------------------------------------------

    safety_checks = []

    safety_checks.append(
        diagnostic(
            "R36F155_REAL_ORDER_EXECUTION_DISABLED",
            REAL_ORDER_EXECUTION is False
        )
    )

    safety_checks.append(
        diagnostic(
            "R36F155_DEMO_ORDER_EXECUTION_DISABLED",
            DEMO_ORDER_EXECUTION is False
        )
    )

    safety_checks.append(
        diagnostic(
            "R36F155_WRITE_TRANSPORT_DISABLED",
            WRITE_TRANSPORT_ENABLED is False
        )
    )

    safety_checks.append(
        diagnostic(
            "R36F155_PRODUCTION_MUTATION_DISABLED",
            PRODUCTION_MUTATION_ENABLED is False
        )
    )

    safety_checks.append(
        diagnostic(
            "R36F155_ONLY_GET_ALLOWED",
            ALLOWED_HTTP_METHODS
            == {"GET"}
        )
    )

    missing = credentials_missing()

    credentials_ok = (
        len(missing)
        == 0
    )

    safety_checks.append(
        diagnostic(
            "R36F155_WEEX_CREDENTIALS_PRESENT",
            credentials_ok,
            (
                "all required credentials present"
                if credentials_ok
                else "missing="
                + ",".join(
                    missing
                )
            )
        )
    )

    if not credentials_ok:

        separator()

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = "
            f"MISSING_WEEX_CREDENTIALS"
        )

        return False

    # --------------------------------------------------------
    # ORDER HISTORY
    # --------------------------------------------------------

    separator()

    log(
        f"{STAGE} STEP 1: "
        f"READ DEMO ORDER HISTORY"
    )

    order_result = weex_get(
        DEMO_ORDER_HISTORY_PATH,
        {
            "limit":
                1000,

            "page":
                0
        }
    )

    order_http_ok = diagnostic(
        "R36F155_DEMO_ORDER_HISTORY_HTTP_200",
        order_result.get(
            "http"
        ) == 200,
        (
            "http="
            + str(
                order_result.get(
                    "http"
                )
            )
        )
    )

    if not order_http_ok:

        log(
            f"{STAGE} ORDER HISTORY RESPONSE = "
            f"{order_result.get('text')}"
        )

        log(
            f"{STAGE} ORDER HISTORY EXCEPTION TYPE = "
            f"{order_result.get('exception_type')}"
        )

        log(
            f"{STAGE} ORDER HISTORY EXCEPTION = "
            f"{order_result.get('exception')}"
        )

        separator()

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = "
            f"DEMO_ORDER_HISTORY_READ_FAILED"
        )

        return False

    order_rows = extract_rows(
        order_result.get(
            "data"
        )
    )

    log(
        f"{STAGE} DEMO ORDER HISTORY ROWS = "
        f"{len(order_rows)}"
    )

    target_order = find_target_order(
        order_rows
    )

    target_found = (
        target_order
        is not None
    )

    diagnostic(
        "R36F155_TARGET_ORDER_FOUND",
        target_found,
        (
            "target="
            + TARGET_ORDER_ID
        )
    )

    if target_found:

        target_symbol = order_symbol(
            target_order
        )

        target_direction = order_direction(
            target_order
        )

        target_status = order_status(
            target_order
        )

        log(
            f"{STAGE} ORDER ID = "
            f"{order_id(target_order)}"
        )

        log(
            f"{STAGE} ORDER SYMBOL = "
            f"{target_symbol}"
        )

        log(
            f"{STAGE} ORDER SIDE = "
            f"{target_order.get('side')}"
        )

        log(
            f"{STAGE} ORDER POSITION SIDE = "
            f"{target_direction}"
        )

        log(
            f"{STAGE} ORDER STATUS = "
            f"{target_status}"
        )

        log(
            f"{STAGE} ORDER TYPE = "
            f"{target_order.get('type')}"
        )

        log(
            f"{STAGE} ORDER ORIGINAL QTY = "
            f"{target_order.get('origQty')}"
        )

        log(
            f"{STAGE} ORDER EXECUTED QTY = "
            f"{target_order.get('executedQty')}"
        )

        log(
            f"{STAGE} ORDER AVG PRICE = "
            f"{target_order.get('avgPrice')}"
        )

        log(
            f"{STAGE} ORDER CLIENT ID = "
            f"{target_order.get('clientOrderId')}"
        )

    else:

        target_symbol = ""

        target_direction = ""

        target_status = (
            "NOT_FOUND"
        )

    # --------------------------------------------------------
    # POSITIONS
    # --------------------------------------------------------

    separator()

    log(
        f"{STAGE} STEP 2: "
        f"READ DEMO POSITIONS"
    )

    position_result = weex_get(
        DEMO_POSITION_PATH
    )

    position_http_ok = diagnostic(
        "R36F155_DEMO_POSITION_HTTP_200",
        position_result.get(
            "http"
        ) == 200,
        (
            "http="
            + str(
                position_result.get(
                    "http"
                )
            )
        )
    )

    if not position_http_ok:

        log(
            f"{STAGE} POSITION RESPONSE = "
            f"{position_result.get('text')}"
        )

        log(
            f"{STAGE} POSITION EXCEPTION TYPE = "
            f"{position_result.get('exception_type')}"
        )

        log(
            f"{STAGE} POSITION EXCEPTION = "
            f"{position_result.get('exception')}"
        )

        separator()

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = "
            f"DEMO_POSITION_READ_FAILED"
        )

        return False

    position_rows = extract_rows(
        position_result.get(
            "data"
        )
    )

    log(
        f"{STAGE} DEMO POSITION ROWS = "
        f"{len(position_rows)}"
    )

    active = active_positions(
        position_rows
    )

    log(
        f"{STAGE} ACTIVE DEMO POSITIONS = "
        f"{len(active)}"
    )

    if target_found:

        matches = matching_positions(
            position_rows,
            target_symbol,
            target_direction
        )

    else:

        matches = []

    matching_found = (
        len(matches)
        > 0
    )

    diagnostic(
        "R36F155_MATCHING_ACTIVE_POSITION_FOUND",
        matching_found,
        (
            f"symbol={target_symbol} "
            f"direction={target_direction}"
        )
    )

    for index, position in enumerate(
        matches,
        start=1
    ):

        log(
            f"{STAGE} POSITION {index} ID = "
            f"{position.get('id')}"
        )

        log(
            f"{STAGE} POSITION {index} SYMBOL = "
            f"{position_symbol(position)}"
        )

        log(
            f"{STAGE} POSITION {index} SIDE = "
            f"{position_side(position)}"
        )

        log(
            f"{STAGE} POSITION {index} SIZE = "
            f"{position_size(position)}"
        )

        log(
            f"{STAGE} POSITION {index} LEVERAGE = "
            f"{position.get('leverage')}"
        )

        log(
            f"{STAGE} POSITION {index} MARGIN TYPE = "
            f"{position.get('marginType')}"
        )

        log(
            f"{STAGE} POSITION {index} "
            f"OPEN ORDER ID = "
            f"{position.get('separatedOpenOrderId')}"
        )

        log(
            f"{STAGE} POSITION {index} "
            f"OPEN VALUE = "
            f"{position.get('openValue')}"
        )

        log(
            f"{STAGE} POSITION {index} "
            f"UNREALIZED PNL = "
            f"{position.get('unrealizePnl')}"
        )

    # --------------------------------------------------------
    # ORDER/POSITION MATCH
    # --------------------------------------------------------

    separator()

    log(
        f"{STAGE} STEP 3: "
        f"ORDER/POSITION RECONCILIATION"
    )

    if (
        target_found
        and matching_found
    ):

        actual_side = position_side(
            matches[0]
        )

        side_match = (
            safe_upper(
                actual_side
            )
            ==
            safe_upper(
                target_direction
            )
        )

        diagnostic(
            "R36F155_ORDER_POSITION_DIRECTION_MATCH",
            side_match,
            (
                f"order={target_direction} "
                f"position={actual_side}"
            )
        )

    else:

        side_match = False

        log(
            f"{STAGE} "
            f"ORDER_POSITION_DIRECTION_MATCH = "
            f"NOT_TESTABLE"
        )

    # --------------------------------------------------------
    # PROTECTION READ-BACK
    # --------------------------------------------------------

    separator()

    log(
        f"{STAGE} STEP 4: "
        f"ORDER TP/SL FIELD INSPECTION"
    )

    protection = protection_fields(
        target_order
    )

    log(
        f"{STAGE} ORDER TP FIELD = "
        f"{protection['tp_field']}"
    )

    log(
        f"{STAGE} ORDER TP VALUE = "
        f"{protection['tp_value']}"
    )

    log(
        f"{STAGE} ORDER SL FIELD = "
        f"{protection['sl_field']}"
    )

    log(
        f"{STAGE} ORDER SL VALUE = "
        f"{protection['sl_value']}"
    )

    if (
        protection[
            "tp_field"
        ] is None
        and
        protection[
            "sl_field"
        ] is None
    ):

        log(
            f"{STAGE} "
            f"TP_SL_INDEPENDENT_VERIFICATION = "
            f"NOT_AVAILABLE_IN_THIS_READ_ONLY_TEST"
        )

        log(
            f"{STAGE} "
            f"TP_SL_WILL_NOT_BE_INFERRED = True"
        )

    # --------------------------------------------------------
    # DUPLICATE GATE
    # --------------------------------------------------------

    separator()

    log(
        f"{STAGE} STEP 5: "
        f"DUPLICATE ENTRY GATE"
    )

    gate = duplicate_gate(
        target_order_found=target_found,
        status=target_status,
        matching_position_found=matching_found
    )

    duplicate_blocked = bool(
        gate[
            "blocked"
        ]
    )

    log(
        f"{STAGE} DUPLICATE ENTRY BLOCKED = "
        f"{duplicate_blocked}"
    )

    log(
        f"{STAGE} DUPLICATE BLOCK REASON = "
        f"{gate['reason']}"
    )

    # --------------------------------------------------------
    # FINAL SAFETY
    # --------------------------------------------------------

    separator()

    log(
        f"{STAGE} STEP 6: "
        f"ZERO-WRITE FINAL CHECK"
    )

    zero_real = diagnostic(
        "R36F155_REAL_MONEY_ZERO_WRITE",
        (
            REAL_ORDER_EXECUTION
            is False
            and
            PRODUCTION_MUTATION_ENABLED
            is False
        )
    )

    zero_demo = diagnostic(
        "R36F155_DEMO_ZERO_WRITE",
        DEMO_ORDER_EXECUTION
        is False
    )

    transport_safe = diagnostic(
        "R36F155_GET_ONLY_TRANSPORT",
        (
            WRITE_TRANSPORT_ENABLED
            is False
            and
            ALLOWED_HTTP_METHODS
            == {"GET"}
        )
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    separator()

    final_pass = (
        target_found
        and duplicate_blocked
        and zero_real
        and zero_demo
        and transport_safe
    )

    log(
        f"{STAGE} TARGET ORDER FOUND = "
        f"{target_found}"
    )

    log(
        f"{STAGE} TARGET ORDER STATUS = "
        f"{target_status}"
    )

    log(
        f"{STAGE} MATCHING POSITION FOUND = "
        f"{matching_found}"
    )

    log(
        f"{STAGE} DUPLICATE ENTRY BLOCKED = "
        f"{duplicate_blocked}"
    )

    log(
        f"{STAGE} DUPLICATE BLOCK REASON = "
        f"{gate['reason']}"
    )

    log(
        f"{STAGE} REAL EXECUTION = False"
    )

    log(
        f"{STAGE} DEMO EXECUTION = False"
    )

    log(
        f"{STAGE} WRITE TRANSPORT = False"
    )

    if final_pass:

        log(
            f"{STAGE} FINAL STATUS = PASS"
        )

        log(
            f"{STAGE} FINAL REASON = "
            f"EXISTING_DEMO_ORDER_RECONCILED_"
            f"AND_DUPLICATE_ENTRY_BLOCKED"
        )

    else:

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        if not target_found:

            log(
                f"{STAGE} FINAL REASON = "
                f"TARGET_DEMO_ORDER_NOT_FOUND"
            )

        elif not duplicate_blocked:

            log(
                f"{STAGE} FINAL REASON = "
                f"DUPLICATE_ENTRY_GATE_NOT_BLOCKING"
            )

        else:

            log(
                f"{STAGE} FINAL REASON = "
                f"RECONCILIATION_INCOMPLETE"
            )

    separator()

    log(
        "NO REAL ORDER SENT"
    )

    log(
        "NO DEMO ORDER SENT"
    )

    log(
        "NO ORDER CANCEL SENT"
    )

    log(
        "NO POSITION CLOSE SENT"
    )

    log(
        "NO TP/SL MUTATION SENT"
    )

    log(
        "NO PRODUCTION EXCHANGE MUTATION SENT"
    )

    separator()

    return final_pass


# ============================================================
# MAIN
# ============================================================

def main():

    start_health_server()

    time.sleep(
        1
    )

    try:

        result = run_test()

    except Exception as exc:

        separator()

        log(
            f"{STAGE} UNHANDLED EXCEPTION = "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        log(
            f"{STAGE} FINAL STATUS = FAIL"
        )

        log(
            f"{STAGE} FINAL REASON = "
            f"UNHANDLED_TEST_EXCEPTION"
        )

        result = False

        separator()

    log(
        f"{STAGE} TEST COMPLETE = "
        f"{result}"
    )

    log(
        f"{STAGE} HEALTH SERVER "
        f"REMAINS RUNNING"
    )

    heartbeat = 0

    while True:

        time.sleep(
            60
        )

        heartbeat += 1

        log(
            f"HEARTBEAT "
            f"stage={STAGE} "
            f"count={heartbeat} "
            f"read_only=True "
            f"real_execution=False "
            f"demo_execution=False "
            f"write_transport=False"
        )


if __name__ == "__main__":

    main()
