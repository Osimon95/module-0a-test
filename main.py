#!/usr/bin/env python3

import os
import time
import json
import hmac
import hashlib
import base64
import threading

from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler, HTTPServer


STAGE = "R36F.15.7"

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com"
).rstrip("/")

API_KEY = os.getenv(
    "WEEX_API_KEY",
    ""
).strip()

API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    ""
).strip()

API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    ""
).strip()

DEMO_SYMBOL = os.getenv(
    "R36F157_DEMO_SYMBOL",
    "BTCSUSDT"
).strip().upper()

TARGET_ORDER_ID = os.getenv(
    "R36F157_TARGET_ORDER_ID",
    "792989056504955607"
).strip()

TARGET_CLIENT_ID = os.getenv(
    "R36F157_TARGET_CLIENT_ID",
    "R36F8-LONG-D14-0001"
).strip()

ENTRY_PRICE = float(
    os.getenv(
        "R36F157_ENTRY_PRICE",
        "77229.3"
    )
)

TP_PRICE = float(
    os.getenv(
        "R36F157_TP_PRICE",
        "77280.4"
    )
)

SL_PRICE = float(
    os.getenv(
        "R36F157_SL_PRICE",
        "76879.1"
    )
)

TARGET_QTY = float(
    os.getenv(
        "R36F157_TARGET_QTY",
        "0.0004"
    )
)

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)

ORDER_HISTORY_ENDPOINT = "/capi/v3/sim/order/history"
POSITIONS_ENDPOINT = "/capi/v3/sim/position/allPosition"

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
WRITE_TRANSPORT_ENABLED = False

ALLOWED_HTTP_METHODS = {"GET"}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    print(now_iso(), message, flush=True)


def line():
    print("-" * 100, flush=True)


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def safe_int(value):
    try:
        return int(value)
    except Exception:
        return 0


def upper(value):
    return str(value or "").strip().upper()


def normalize_rows(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "data",
            "rows",
            "records",
            "orders",
            "items",
            "list",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return value

    return []


def make_signature(timestamp, method, request_path, query_string=""):
    message = str(timestamp) + method.upper() + request_path

    if query_string:
        message += "?" + query_string

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def weex_get(request_path, params=None):
    if "GET" not in ALLOWED_HTTP_METHODS:
        raise RuntimeError("GET_TRANSPORT_DISABLED")

    if not request_path.startswith("/capi/v3/sim/"):
        raise RuntimeError("NON_DEMO_ENDPOINT_BLOCKED")

    params = params or {}

    query_string = urlencode(params)

    timestamp = str(int(time.time() * 1000))

    signature = make_signature(
        timestamp,
        "GET",
        request_path,
        query_string,
    )

    url = BASE_URL + request_path

    if query_string:
        url += "?" + query_string

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }

    request = Request(
        url,
        method="GET",
        headers=headers,
    )

    try:
        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            status = response.status

    except HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            "WEEX GET HTTP "
            + str(exc.code)
            + ": "
            + body
        )

    except URLError as exc:
        raise RuntimeError(
            "WEEX GET NETWORK ERROR: "
            + str(exc)
        )

    try:
        parsed = json.loads(body)

    except Exception:
        parsed = body

    return status, parsed


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = json.dumps(
            {
                "stage": STAGE,
                "status": "running",
                "write_transport": False,
                "real_execution": False,
                "demo_execution": False,
            }
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():

    def run():
        server = HTTPServer(
            (
                "0.0.0.0",
                PORT,
            ),
            HealthHandler,
        )

        log(
            STAGE
            + ": HEALTH SERVER STARTED ON PORT "
            + str(PORT)
        )

        server.serve_forever()

    thread = threading.Thread(
        target=run,
        daemon=True,
    )

    thread.start()


def order_id(row):
    return str(
        row.get("orderId")
        or row.get("order_id")
        or ""
    ).strip()


def client_id(row):
    return str(
        row.get("clientOrderId")
        or row.get("client_order_id")
        or ""
    ).strip()


def order_time(row):
    return safe_int(
        row.get("time")
        or row.get("createTime")
        or 0
    )


def update_time(row):
    return safe_int(
        row.get("updateTime")
        or order_time(row)
    )


def order_side(row):
    return upper(
        row.get("side")
    )


def position_side(row):
    return upper(
        row.get("positionSide")
        or row.get("position_side")
    )


def order_status(row):
    return upper(
        row.get("status")
    )


def order_symbol(row):
    return upper(
        row.get("symbol")
    )


def executed_qty(row):
    return safe_float(
        row.get("executedQty")
    )


def average_price(row):
    return safe_float(
        row.get("avgPrice")
    )


def is_filled(row):
    return (
        order_status(row) == "FILLED"
        and executed_qty(row) > 0
    )


def is_long_closing_candidate(
    row,
    entry_update_time,
):

    if order_symbol(row) != DEMO_SYMBOL:
        return False

    if update_time(row) < entry_update_time:
        return False

    if not is_filled(row):
        return False

    side = order_side(row)
    pos_side = position_side(row)

    if side == "SELL":
        return True

    if (
        pos_side == "LONG"
        and side in (
            "SELL",
            "CLOSE",
        )
    ):
        return True

    return False


def classify_exit_price(exit_price):
    if exit_price <= 0:
        return "EXIT_PRICE_UNAVAILABLE"

    entry_to_tp = abs(
        TP_PRICE - ENTRY_PRICE
    )

    entry_to_sl = abs(
        ENTRY_PRICE - SL_PRICE
    )

    tolerance = max(
        5.0,
        min(
            entry_to_tp,
            entry_to_sl,
        ) * 0.25,
    )

    tp_distance = abs(
        exit_price - TP_PRICE
    )

    sl_distance = abs(
        exit_price - SL_PRICE
    )

    if (
        exit_price >= TP_PRICE
        or tp_distance <= tolerance
    ):
        return "TP_EXIT_PLAUSIBLE"

    if (
        exit_price <= SL_PRICE
        or sl_distance <= tolerance
    ):
        return "SL_EXIT_PLAUSIBLE"

    return "MANUAL_OR_OTHER_EXIT_PLAUSIBLE"


def position_size(row):
    for key in (
        "size",
        "positionAmt",
        "positionQty",
        "qty",
        "quantity",
        "available",
        "total",
    ):
        if key in row:
            value = abs(
                safe_float(
                    row.get(key)
                )
            )

            if value > 0:
                return value

    return 0.0


def inspect_positions(rows):
    active = []
    matching = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        size = position_size(row)

        if size <= 0:
            continue

        active.append(row)

        symbol = upper(
            row.get("symbol")
        )

        direction = upper(
            row.get("side")
            or row.get("positionSide")
            or row.get("position_side")
        )

        if (
            symbol == DEMO_SYMBOL
            and direction == "LONG"
        ):
            matching.append(row)

    return active, matching


def run_test():

    line()

    log(
        STAGE
        + " DEMO LIFECYCLE + PROTECTION PLAUSIBILITY START"
    )

    log(
        STAGE
        + " TARGET ORDER ID = "
        + TARGET_ORDER_ID
    )

    log(
        STAGE
        + " TARGET CLIENT ID = "
        + TARGET_CLIENT_ID
    )

    log(
        STAGE
        + " SYMBOL = "
        + DEMO_SYMBOL
    )

    log(
        STAGE
        + " KNOWN ENTRY PRICE = "
        + str(ENTRY_PRICE)
    )

    log(
        STAGE
        + " JOURNALED TP PRICE = "
        + str(TP_PRICE)
    )

    log(
        STAGE
        + " JOURNALED SL PRICE = "
        + str(SL_PRICE)
    )

    line()

    log(
        "PASS: REAL_ORDER_EXECUTION_DISABLED"
    )

    log(
        "PASS: DEMO_ORDER_EXECUTION_DISABLED"
    )

    log(
        "PASS: WRITE_TRANSPORT_DISABLED"
    )

    log(
        "PASS: ONLY_GET_TRANSPORT_ALLOWED"
    )

    if not (
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    ):
        log(
            "R36F.15.7 FINAL STATUS = FAIL"
        )

        log(
            "R36F.15.7 REASON = WEEX_CREDENTIALS_MISSING"
        )

        return

    log(
        "PASS: WEEX_CREDENTIALS_PRESENT"
    )

    line()

    try:
        result = weex_get(
            ORDER_HISTORY_ENDPOINT,
            {
                "symbol": DEMO_SYMBOL,
                "limit": 1000,
                "page": 0,
            },
        )

        history_status = result[0]
        history_data = result[1]

        log(
            "R36F.15.7 DEMO ORDER HISTORY HTTP = "
            + str(history_status)
        )

        history_rows = normalize_rows(
            history_data
        )

        log(
            "R36F.15.7 DEMO ORDER HISTORY ROWS = "
            + str(
                len(history_rows)
            )
        )

    except Exception as exc:
        log(
            "R36F.15.7 DEMO ORDER HISTORY READ = FAIL"
        )

        log(
            "R36F.15.7 ERROR = "
            + str(exc)
        )

        log(
            "R36F.15.7 NEW DEMO ORDER ALLOWED = False"
        )

        log(
            "R36F.15.7 FINAL STATUS = FAIL_CLOSED"
        )

        return

    target = None

    for row in history_rows:
        if not isinstance(row, dict):
            continue

        if (
            order_id(row) == TARGET_ORDER_ID
            or client_id(row) == TARGET_CLIENT_ID
        ):
            target = row
            break

    target_found = target is not None

    log(
        "R36F.15.7 TARGET ORDER FOUND = "
        + str(target_found)
    )

    if not target_found:
        log(
            "R36F.15.7 LIFECYCLE CLASSIFICATION = POSITION_LIFECYCLE_UNRESOLVED"
        )

        log(
            "R36F.15.7 TP_SL_PLAUSIBILITY_CLASSIFICATION = NO_EXIT_ORDER_EVIDENCE"
        )

        log(
            "R36F.15.7 DUPLICATE ENTRY BLOCKED = True"
        )

        log(
            "R36F.15.7 NEW DEMO ORDER ALLOWED = False"
        )

        log(
            "R36F.15.7 FINAL STATUS = PASS_FAIL_CLOSED"
        )

        return

    entry_update_time = update_time(
        target
    )

    log(
        "R36F.15.7 ENTRY ORDER STATUS = "
        + order_status(target)
    )

    log(
        "R36F.15.7 ENTRY ORDER EXECUTED QTY = "
        + str(
            executed_qty(target)
        )
    )

    log(
        "R36F.15.7 ENTRY ORDER AVG PRICE = "
        + str(
            average_price(target)
        )
    )

    log(
        "R36F.15.7 ENTRY ORDER TIME = "
        + str(
            order_time(target)
        )
    )

    log(
        "R36F.15.7 ENTRY ORDER UPDATE TIME = "
        + str(
            entry_update_time
        )
    )

    line()

    later_rows = []

    for row in history_rows:
        if not isinstance(row, dict):
            continue

        if order_id(row) == TARGET_ORDER_ID:
            continue

        if order_symbol(row) != DEMO_SYMBOL:
            continue

        if update_time(row) >= entry_update_time:
            later_rows.append(row)

    later_rows.sort(
        key=update_time
    )

    log(
        "R36F.15.7 ORDERS AT_OR_AFTER ENTRY = "
        + str(
            len(later_rows)
        )
    )

    closing_candidates = []

    for row in later_rows:
        if is_long_closing_candidate(
            row,
            entry_update_time,
        ):
            closing_candidates.append(row)

            log(
                "R36F.15.7 CLOSING CANDIDATE ORDER ID = "
                + order_id(row)
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE CLIENT ID = "
                + client_id(row)
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE SIDE = "
                + order_side(row)
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE POSITION SIDE = "
                + position_side(row)
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE STATUS = "
                + order_status(row)
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE QTY = "
                + str(
                    executed_qty(row)
                )
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE AVG PRICE = "
                + str(
                    average_price(row)
                )
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE UPDATE TIME = "
                + str(
                    update_time(row)
                )
            )

            log(
                "R36F.15.7 CLOSING CANDIDATE PRICE CLASSIFICATION = "
                + classify_exit_price(
                    average_price(row)
                )
            )

            line()

    log(
        "R36F.15.7 CLOSING CANDIDATE COUNT = "
        + str(
            len(closing_candidates)
        )
    )

    try:
        result = weex_get(
            POSITIONS_ENDPOINT
        )

        position_status = result[0]
        position_data = result[1]

        log(
            "R36F.15.7 DEMO POSITION HTTP = "
            + str(position_status)
        )

        position_rows = normalize_rows(
            position_data
        )

        log(
            "R36F.15.7 DEMO POSITION ROWS = "
            + str(
                len(position_rows)
            )
        )

        position_read_ok = True

    except Exception as exc:
        log(
            "R36F.15.7 DEMO POSITION READ = FAIL"
        )

        log(
            "R36F.15.7 ERROR = "
            + str(exc)
        )

        position_rows = []
        position_read_ok = False

    active_positions, matching_positions = inspect_positions(
        position_rows
    )

    log(
        "R36F.15.7 ACTIVE DEMO POSITION COUNT = "
        + str(
            len(active_positions)
        )
    )

    log(
        "R36F.15.7 MATCHING LONG POSITION COUNT = "
        + str(
            len(matching_positions)
        )
    )

    position_still_open = (
        len(matching_positions) > 0
    )

    line()

    log(
        "R36F.15.7 CHECK A = DEMO LIFECYCLE RECONSTRUCTION"
    )

    if not position_read_ok:
        lifecycle = (
            "POSITION_LIFECYCLE_UNRESOLVED"
        )

        lifecycle_verified = False

    elif position_still_open:
        lifecycle = (
            "POSITION_STILL_OPEN"
        )

        lifecycle_verified = True

    elif closing_candidates:
        lifecycle = (
            "PROTECTIVE_EXIT_EVIDENCE_FOUND"
        )

        lifecycle_verified = True

    elif (
        is_filled(target)
        and not position_still_open
    ):
        lifecycle = (
            "POSITION_CLOSED_BUT_CAUSE_UNVERIFIED"
        )

        lifecycle_verified = False

    else:
        lifecycle = (
            "POSITION_LIFECYCLE_UNRESOLVED"
        )

        lifecycle_verified = False

    log(
        "R36F.15.7 LIFECYCLE CLASSIFICATION = "
        + lifecycle
    )

    log(
        "R36F.15.7 LIFECYCLE FULLY VERIFIED = "
        + str(
            lifecycle_verified
        )
    )

    line()

    log(
        "R36F.15.7 CHECK B = TP_SL_TRIGGER_PLAUSIBILITY"
    )

    plausibility = (
        "NO_EXIT_ORDER_EVIDENCE"
    )

    chosen_exit = None

    if closing_candidates:
        chosen_exit = closing_candidates[0]

        exit_price = average_price(
            chosen_exit
        )

        plausibility = classify_exit_price(
            exit_price
        )

        log(
            "R36F.15.7 SELECTED EXIT ORDER ID = "
            + order_id(
                chosen_exit
            )
        )

        log(
            "R36F.15.7 SELECTED EXIT AVG PRICE = "
            + str(
                exit_price
            )
        )

        log(
            "R36F.15.7 SELECTED EXIT EXECUTED QTY = "
            + str(
                executed_qty(
                    chosen_exit
                )
            )
        )

    log(
        "R36F.15.7 TP_SL_PLAUSIBILITY_CLASSIFICATION = "
        + plausibility
    )

    log(
        "R36F.15.7 TP EXECUTION VERIFIED = False"
    )

    log(
        "R36F.15.7 SL EXECUTION VERIFIED = False"
    )

    log(
        "R36F.15.7 PLAUSIBILITY_IS_NOT_EXCHANGE_PROOF = True"
    )

    line()

    if position_still_open:
        duplicate_block_reason = (
            "POSITION_ALREADY_EXISTS"
        )

    elif lifecycle in (
        "POSITION_CLOSED_BUT_CAUSE_UNVERIFIED",
        "POSITION_LIFECYCLE_UNRESOLVED",
    ):
        duplicate_block_reason = (
            "PRIOR_FILLED_ORDER_LIFECYCLE_NOT_CONCLUSIVELY_RECONCILED"
        )

    elif closing_candidates:
        duplicate_block_reason = (
            "PRIOR_DEMO_TRADE_RECONCILED_BUT_NEW_ENTRY_REQUIRES_NEW_AUTHORIZATION"
        )

    else:
        duplicate_block_reason = (
            "FAIL_CLOSED_UNKNOWN_STATE"
        )

    log(
        "R36F.15.7 DUPLICATE ENTRY BLOCKED = True"
    )

    log(
        "R36F.15.7 DUPLICATE BLOCK REASON = "
        + duplicate_block_reason
    )

    log(
        "R36F.15.7 NEW DEMO ORDER ALLOWED = False"
    )

    log(
        "R36F.15.7 REAL MONEY EXECUTION = False"
    )

    log(
        "R36F.15.7 DEMO ORDER EXECUTION = False"
    )

    log(
        "R36F.15.7 WRITE TRANSPORT = False"
    )

    line()

    log(
        "R36F.15.7 CHECK_A_COMPLETE = True"
    )

    log(
        "R36F.15.7 CHECK_B_COMPLETE = True"
    )

    log(
        "R36F.15.7 FINAL STATUS = PASS"
    )

    log(
        "R36F.15.7 TEST COMPLETE"
    )

    line()


def main():
    start_health_server()

    time.sleep(0.25)

    try:
        run_test()

    except Exception as exc:
        line()

        log(
            "R36F.15.7 UNHANDLED TEST ERROR = "
            + repr(exc)
        )

        log(
            "R36F.15.7 DUPLICATE ENTRY BLOCKED = True"
        )

        log(
            "R36F.15.7 NEW DEMO ORDER ALLOWED = False"
        )

        log(
            "R36F.15.7 REAL MONEY EXECUTION = False"
        )

        log(
            "R36F.15.7 FINAL STATUS = FAIL_CLOSED"
        )

        line()

    heartbeat = 0

    while True:
        heartbeat += 1

        log(
            "HEARTBEAT stage="
            + STAGE
            + " status=PASS"
            + " count="
            + str(heartbeat)
            + " write_transport=False"
            + " real_execution=False"
            + " demo_execution=False"
        )

        time.sleep(60)


if __name__ == "__main__":
    main()
