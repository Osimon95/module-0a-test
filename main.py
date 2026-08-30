from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple


# ==================================================================================================
# R35P-D - RAW PUBLIC BTCUSDT MARK PRICE READ
# ==================================================================================================
#
# PURPOSE
#   Isolate exactly one previously failing activation-environment dependency:
#
#       BTCUSDT PUBLIC MARK PRICE READ
#
#   This unit proves, independently of all authenticated account logic:
#
#       DNS
#         ->
#       public HTTP GET
#         ->
#       HTTP response
#         ->
#       JSON parsing
#         ->
#       response-shape recognition
#         ->
#       BTCUSDT mark-price extraction
#         ->
#       positive numeric price validation
#
# SAFETY MODEL
#   - PUBLIC GET ONLY
#   - NO AUTHENTICATED ACCOUNT READ REQUIRED
#   - NO POST
#   - NO PUT
#   - NO PATCH
#   - NO DELETE
#   - NO ORDER SUBMISSION
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MODE MUTATION
#   - NO POSITION MUTATION
#   - NO REAL ORDER EXECUTION
#   - FIRST REAL ORDER HARD FORBIDDEN
#
# SUCCESS CONDITION
#   R35P-D passes only when:
#
#       DNS_OK=True
#       REQUEST_ATTEMPTED=True
#       HTTP_READ_OK=True
#       HTTP_STATUS=200
#       JSON_PARSE_OK=True
#       BTCUSDT_MARK_PRICE_FOUND=True
#       MARK_PRICE_NUMERIC=True
#       MARK_PRICE_POSITIVE=True
#       PUBLIC_MARK_PRICE_READ_OK=True
#       EXCHANGE_NETWORK_WRITES=0
#       REAL_ORDER_EXECUTION=False
#
# NEXT UNIT
#   R35P-E_RAW_POSITION_RECONCILIATION
#
# ==================================================================================================


VERSION = "R35P-D"
SYMBOL = "BTCUSDT"

HEALTH_PORT = 10000

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"

# Public WEEX contract market endpoint.
#
# R35P-D deliberately keeps the endpoint isolated here so that if WEEX changes
# the public response shape, the failure can be diagnosed without contaminating
# account reconciliation.
MARK_PRICE_PATH = "/capi/v2/market/ticker"

HTTP_TIMEOUT_SECONDS = 10.0
HEARTBEAT_SECONDS = 30


# ==================================================================================================
# HARD SAFETY FLAGS
# ==================================================================================================

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False
DEMO_ORDER_EXECUTION = False

EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

PUBLIC_MARKET_GETS = 0
AUTHENTICATED_WEEX_READS = 0


# ==================================================================================================
# LOGGING
# ==================================================================================================


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str = "") -> None:
    print(f"{utc_now()} {message}", flush=True)


def divider() -> None:
    log("-" * 100)


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = json.dumps(
            {
                "status": "ok",
                "version": VERSION,
                "symbol": SYMBOL,
                "real_order_execution": REAL_ORDER_EXECUTION,
                "first_real_order_allowed": FIRST_REAL_ORDER_ALLOWED,
                "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
            },
            separators=(",", ":"),
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def start_health_server() -> None:
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    log(f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}")


# ==================================================================================================
# SAFE PUBLIC HTTP GET
# ==================================================================================================


def safe_public_get(url: str) -> Tuple[bool, Optional[int], Optional[str], Optional[str], Optional[str]]:
    """
    Execute one public GET request.

    Returns:
        (
            success,
            http_status,
            response_body,
            content_type,
            error_message,
        )

    This function cannot perform exchange mutations.
    """

    global PUBLIC_MARKET_GETS

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-read-only-diagnostic",
        },
    )

    try:
        PUBLIC_MARKET_GETS += 1

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:
            status = int(response.status)
            content_type = response.headers.get("Content-Type")
            raw = response.read()
            body = raw.decode("utf-8", errors="replace")

            return (
                200 <= status < 300,
                status,
                body,
                content_type,
                None,
            )

    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""

        return (
            False,
            int(exc.code),
            body,
            exc.headers.get("Content-Type") if exc.headers else None,
            f"HTTPError: {exc}",
        )

    except Exception as exc:
        return (
            False,
            None,
            None,
            None,
            f"{exc.__class__.__name__}: {exc}",
        )


# ==================================================================================================
# MARK PRICE EXTRACTION
# ==================================================================================================


def normalize_symbol(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().upper()


def numeric_price(value: Any) -> Optional[float]:
    if value is None:
        return None

    try:
        result = float(str(value).strip())

        if result <= 0:
            return None

        return result

    except Exception:
        return None


def extract_price_from_dict(row: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    """
    Inspect known public-market price field names.

    R35P-D intentionally reports the field actually used so future response-shape
    changes are immediately visible.
    """

    candidate_fields = (
        "markPrice",
        "mark_price",
        "price",
        "lastPrice",
        "last",
        "close",
        "indexPrice",
    )

    for field in candidate_fields:
        if field in row:
            value = numeric_price(row.get(field))

            if value is not None:
                return value, field

    return None, None


def find_btcusdt_price(
    payload: Any,
) -> Tuple[
    bool,
    Optional[float],
    Optional[str],
    Optional[str],
    int,
]:
    """
    Attempt to locate BTCUSDT and extract a positive public market price.

    Returns:
        (
            symbol_found,
            price,
            price_field,
            response_shape,
            candidate_rows_seen,
        )
    """

    candidate_rows_seen = 0

    # ----------------------------------------------------------------------------------------------
    # Shape 1:
    #
    # [
    #   {
    #       "symbol": "BTCUSDT",
    #       ...
    #   }
    # ]
    # ----------------------------------------------------------------------------------------------

    if isinstance(payload, list):
        for row in payload:
            if not isinstance(row, dict):
                continue

            candidate_rows_seen += 1

            row_symbol = normalize_symbol(
                row.get("symbol")
                or row.get("s")
                or row.get("contract")
                or row.get("contractSymbol")
            )

            if row_symbol == SYMBOL:
                price, field = extract_price_from_dict(row)

                return (
                    True,
                    price,
                    field,
                    "list",
                    candidate_rows_seen,
                )

        # Some public endpoints return a one-row list without symbol.
        if len(payload) == 1 and isinstance(payload[0], dict):
            candidate_rows_seen = max(candidate_rows_seen, 1)

            price, field = extract_price_from_dict(payload[0])

            if price is not None:
                return (
                    True,
                    price,
                    field,
                    "single_row_list_without_symbol",
                    candidate_rows_seen,
                )

        return (
            False,
            None,
            None,
            "list",
            candidate_rows_seen,
        )

    # ----------------------------------------------------------------------------------------------
    # Shape 2:
    #
    # {
    #   "symbol": "BTCUSDT",
    #   "markPrice": ...
    # }
    # ----------------------------------------------------------------------------------------------

    if isinstance(payload, dict):
        candidate_rows_seen += 1

        top_symbol = normalize_symbol(
            payload.get("symbol")
            or payload.get("s")
            or payload.get("contract")
            or payload.get("contractSymbol")
        )

        if top_symbol == SYMBOL:
            price, field = extract_price_from_dict(payload)

            return (
                True,
                price,
                field,
                "dict",
                candidate_rows_seen,
            )

        # ------------------------------------------------------------------------------------------
        # Shape 3:
        #
        # {
        #   "data": [...]
        # }
        #
        # or
        #
        # {
        #   "data": {...}
        # }
        # ------------------------------------------------------------------------------------------

        if "data" in payload:
            data = payload.get("data")

            if isinstance(data, list):
                for row in data:
                    if not isinstance(row, dict):
                        continue

                    candidate_rows_seen += 1

                    row_symbol = normalize_symbol(
                        row.get("symbol")
                        or row.get("s")
                        or row.get("contract")
                        or row.get("contractSymbol")
                    )

                    if row_symbol == SYMBOL:
                        price, field = extract_price_from_dict(row)

                        return (
                            True,
                            price,
                            field,
                            "dict.data.list",
                            candidate_rows_seen,
                        )

                if len(data) == 1 and isinstance(data[0], dict):
                    price, field = extract_price_from_dict(data[0])

                    if price is not None:
                        return (
                            True,
                            price,
                            field,
                            "dict.data.single_row_list_without_symbol",
                            candidate_rows_seen,
                        )

            elif isinstance(data, dict):
                candidate_rows_seen += 1

                row_symbol = normalize_symbol(
                    data.get("symbol")
                    or data.get("s")
                    or data.get("contract")
                    or data.get("contractSymbol")
                )

                if row_symbol == SYMBOL or not row_symbol:
                    price, field = extract_price_from_dict(data)

                    if price is not None:
                        return (
                            True,
                            price,
                            field,
                            "dict.data.dict",
                            candidate_rows_seen,
                        )

        # ------------------------------------------------------------------------------------------
        # Shape 4:
        #
        # {
        #   "result": [...]
        # }
        # ------------------------------------------------------------------------------------------

        if "result" in payload:
            result = payload.get("result")

            if isinstance(result, list):
                for row in result:
                    if not isinstance(row, dict):
                        continue

                    candidate_rows_seen += 1

                    row_symbol = normalize_symbol(
                        row.get("symbol")
                        or row.get("s")
                        or row.get("contract")
                        or row.get("contractSymbol")
                    )

                    if row_symbol == SYMBOL:
                        price, field = extract_price_from_dict(row)

                        return (
                            True,
                            price,
                            field,
                            "dict.result.list",
                            candidate_rows_seen,
                        )

            elif isinstance(result, dict):
                candidate_rows_seen += 1

                row_symbol = normalize_symbol(
                    result.get("symbol")
                    or result.get("s")
                    or result.get("contract")
                    or result.get("contractSymbol")
                )

                if row_symbol == SYMBOL or not row_symbol:
                    price, field = extract_price_from_dict(result)

                    if price is not None:
                        return (
                            True,
                            price,
                            field,
                            "dict.result.dict",
                            candidate_rows_seen,
                        )

        # ------------------------------------------------------------------------------------------
        # Shape 5:
        #
        # No symbol field, but top-level dictionary itself contains price.
        # ------------------------------------------------------------------------------------------

        price, field = extract_price_from_dict(payload)

        if price is not None:
            return (
                True,
                price,
                field,
                "dict_without_symbol",
                candidate_rows_seen,
            )

        return (
            False,
            None,
            None,
            "dict",
            candidate_rows_seen,
        )

    return (
        False,
        None,
        None,
        type(payload).__name__,
        candidate_rows_seen,
    )


# ==================================================================================================
# SAFETY VALIDATION
# ==================================================================================================


def safety_invariants_ok() -> bool:
    return (
        REAL_ORDER_EXECUTION is False
        and FIRST_REAL_ORDER_ALLOWED is False
        and DEMO_ORDER_EXECUTION is False
        and EXCHANGE_NETWORK_WRITES == 0
        and ORDER_SUBMISSIONS == 0
        and LEVERAGE_MUTATIONS == 0
        and MARGIN_MODE_MUTATIONS == 0
        and POSITION_MUTATIONS == 0
        and AUTHENTICATED_WEEX_READS == 0
    )


# ==================================================================================================
# R35P-D SINGLE TEST
# ==================================================================================================


def run_test() -> Dict[str, Any]:
    failure_stage: Optional[str] = None
    exception_class: Optional[str] = None
    exception_message: Optional[str] = None

    dns_ok = False
    dns_ip: Optional[str] = None
    dns_error: Optional[str] = None

    request_attempted = False
    http_read_ok = False
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    response_body: Optional[str] = None
    response_bytes = 0

    json_parse_ok = False
    payload: Any = None

    response_type: Optional[str] = None
    response_keys: Optional[str] = None

    btcusdt_mark_price_found = False
    mark_price: Optional[float] = None
    mark_price_field: Optional[str] = None
    mark_price_numeric = False
    mark_price_positive = False
    mark_price_response_shape: Optional[str] = None
    candidate_rows_seen = 0

    encoded_symbol = urllib.parse.quote(SYMBOL)

    endpoint = (
        f"{WEEX_CONTRACT_BASE}"
        f"{MARK_PRICE_PATH}"
        f"?symbol={encoded_symbol}"
    )

    # ==============================================================================================
    # HEADER
    # ==============================================================================================

    divider()
    log(f"{VERSION}: MAIN.PY ENTERED")
    divider()

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")
    log(f"{VERSION}: TEST SCOPE=RAW PUBLIC BTCUSDT MARK PRICE READ ONLY")
    log(f"{VERSION}: WEEX CONTRACT BASE={WEEX_CONTRACT_BASE}")
    log(f"{VERSION}: MARK PRICE PATH={MARK_PRICE_PATH}")
    log(f"{VERSION}: REAL ORDER EXECUTION={REAL_ORDER_EXECUTION}")
    log(f"{VERSION}: FIRST REAL ORDER ALLOWED={FIRST_REAL_ORDER_ALLOWED}")
    log(f"{VERSION}: EXCHANGE NETWORK WRITES={EXCHANGE_NETWORK_WRITES}")
    log(f"{VERSION}: PUBLIC MARKET GETS={PUBLIC_MARKET_GETS}")
    log(f"{VERSION}: AUTHENTICATED READS={AUTHENTICATED_WEEX_READS}")

    divider()
    log(f"{VERSION}: BEGIN SINGLE TEST")
    divider()

    divider()
    log(f"{VERSION}: RAW PUBLIC MARK PRICE DIAGNOSTIC")
    divider()

    log("TEST=RAW_PUBLIC_BTCUSDT_MARK_PRICE_READ")
    log(f"SYMBOL={SYMBOL}")
    log(f"ENDPOINT={endpoint}")
    log("METHOD=GET")
    log("AUTHENTICATION=NONE_PUBLIC_MARKET_DATA")

    # ==============================================================================================
    # DNS
    # ==============================================================================================

    divider()
    log(f"{VERSION}: DNS")
    divider()

    try:
        dns_ip = socket.gethostbyname(
            urllib.parse.urlparse(WEEX_CONTRACT_BASE).hostname or ""
        )

        dns_ok = bool(dns_ip)

    except Exception as exc:
        dns_ok = False
        dns_error = f"{exc.__class__.__name__}: {exc}"

        failure_stage = "DNS"
        exception_class = exc.__class__.__name__
        exception_message = str(exc)

    log(f"DNS_OK={dns_ok}")
    log(f"DNS_IP={dns_ip}")
    log(f"DNS_ERROR={dns_error}")

    # ==============================================================================================
    # PUBLIC HTTP GET
    # ==============================================================================================

    divider()
    log(f"{VERSION}: PUBLIC HTTP GET")
    divider()

    if dns_ok:
        request_attempted = True

        (
            http_read_ok,
            http_status,
            response_body,
            content_type,
            http_error,
        ) = safe_public_get(endpoint)

        if response_body is not None:
            response_bytes = len(response_body.encode("utf-8"))

        if not http_read_ok:
            failure_stage = "HTTP_GET"

            if http_error:
                parts = http_error.split(":", 1)
                exception_class = parts[0]
                exception_message = parts[1].strip() if len(parts) > 1 else http_error

    else:
        http_error = "DNS resolution failed; HTTP request not attempted."

    log(f"REQUEST_ATTEMPTED={request_attempted}")
    log(f"HTTP_READ_OK={http_read_ok}")
    log(f"HTTP_STATUS={http_status}")
    log(f"CONTENT_TYPE={content_type}")
    log(f"RESPONSE_BYTES={response_bytes}")

    # ==============================================================================================
    # RAW RESPONSE
    # ==============================================================================================

    divider()
    log(f"{VERSION}: RAW RESPONSE")
    divider()

    if response_body is None:
        preview = None
    else:
        preview = response_body[:2000]

    log(f"RAW_BODY_PREVIEW={preview}")

    # ==============================================================================================
    # JSON PARSE
    # ==============================================================================================

    divider()
    log(f"{VERSION}: RESPONSE SHAPE")
    divider()

    if http_read_ok and response_body is not None:
        try:
            payload = json.loads(response_body)

            json_parse_ok = True
            response_type = type(payload).__name__

            if isinstance(payload, dict):
                response_keys = ",".join(str(key) for key in payload.keys())
            else:
                response_keys = "N/A"

        except Exception as exc:
            json_parse_ok = False

            failure_stage = "JSON_PARSE"
            exception_class = exc.__class__.__name__
            exception_message = str(exc)

    log(f"JSON_PARSE_OK={json_parse_ok}")
    log(f"RESPONSE_TYPE={response_type}")
    log(f"RESPONSE_KEYS={response_keys}")

    # ==============================================================================================
    # MARK PRICE EXTRACTION
    # ==============================================================================================

    divider()
    log(f"{VERSION}: BTCUSDT MARK PRICE EXTRACTION")
    divider()

    if json_parse_ok:
        try:
            (
                btcusdt_mark_price_found,
                mark_price,
                mark_price_field,
                mark_price_response_shape,
                candidate_rows_seen,
            ) = find_btcusdt_price(payload)

            mark_price_numeric = isinstance(mark_price, (int, float))

            mark_price_positive = (
                mark_price_numeric
                and mark_price is not None
                and mark_price > 0
            )

            if not btcusdt_mark_price_found:
                failure_stage = "BTCUSDT_MARK_PRICE_NOT_FOUND"

            elif not mark_price_numeric:
                failure_stage = "MARK_PRICE_NOT_NUMERIC"

            elif not mark_price_positive:
                failure_stage = "MARK_PRICE_NOT_POSITIVE"

        except Exception as exc:
            failure_stage = "MARK_PRICE_EXTRACTION"
            exception_class = exc.__class__.__name__
            exception_message = str(exc)

    log(f"BTCUSDT_MARK_PRICE_FOUND={btcusdt_mark_price_found}")
    log(f"MARK_PRICE={mark_price}")
    log(f"MARK_PRICE_FIELD={mark_price_field}")
    log(f"MARK_PRICE_NUMERIC={mark_price_numeric}")
    log(f"MARK_PRICE_POSITIVE={mark_price_positive}")
    log(f"MARK_PRICE_RESPONSE_SHAPE={mark_price_response_shape}")
    log(f"CANDIDATE_ROWS_SEEN={candidate_rows_seen}")

    # ==============================================================================================
    # ERROR DIAGNOSTIC
    # ==============================================================================================

    divider()
    log(f"{VERSION}: ERROR DIAGNOSTIC")
    divider()

    log(f"FAILURE_STAGE={failure_stage}")
    log(f"EXCEPTION_CLASS={exception_class}")
    log(f"EXCEPTION_MESSAGE={exception_message}")

    # ==============================================================================================
    # SAFETY
    # ==============================================================================================

    safety_ok = safety_invariants_ok()

    divider()
    log(f"{VERSION}: SAFETY")
    divider()

    log(f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS}")
    log(f"AUTHENTICATED_WEEX_READS={AUTHENTICATED_WEEX_READS}")
    log(f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}")
    log(f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}")
    log(f"LEVERAGE_MUTATIONS={LEVERAGE_MUTATIONS}")
    log(f"MARGIN_MODE_MUTATIONS={MARGIN_MODE_MUTATIONS}")
    log(f"POSITION_MUTATIONS={POSITION_MUTATIONS}")
    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log(f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}")
    log(f"SAFETY_INVARIANTS_OK={safety_ok}")

    # ==============================================================================================
    # RESULT
    # ==============================================================================================

    public_mark_price_read_ok = (
        dns_ok
        and request_attempted
        and http_read_ok
        and http_status == 200
        and json_parse_ok
        and btcusdt_mark_price_found
        and mark_price_numeric
        and mark_price_positive
    )

    status = (
        "PASS"
        if (
            public_mark_price_read_ok
            and safety_ok
        )
        else "FAIL"
    )

    divider()
    log(f"{VERSION} RESULT")
    divider()

    log("TEST=RAW_PUBLIC_BTCUSDT_MARK_PRICE_READ")
    log(f"DNS_OK={dns_ok}")
    log(f"REQUEST_ATTEMPTED={request_attempted}")
    log(f"HTTP_READ_OK={http_read_ok}")
    log(f"HTTP_STATUS={http_status}")
    log(f"JSON_PARSE_OK={json_parse_ok}")
    log(f"BTCUSDT_MARK_PRICE_FOUND={btcusdt_mark_price_found}")
    log(f"MARK_PRICE={mark_price}")
    log(f"MARK_PRICE_FIELD={mark_price_field}")
    log(f"MARK_PRICE_NUMERIC={mark_price_numeric}")
    log(f"MARK_PRICE_POSITIVE={mark_price_positive}")
    log(f"PUBLIC_MARK_PRICE_READ_OK={public_mark_price_read_ok}")
    log(f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS}")
    log(f"AUTHENTICATED_WEEX_READS={AUTHENTICATED_WEEX_READS}")
    log(f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}")
    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log(f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}")
    log(f"STATUS={status}")

    if status == "PASS":
        log("NEXT_UNIT=R35P-E_RAW_POSITION_RECONCILIATION")
    else:
        log("NEXT_UNIT=STOP_AND_DIAGNOSE_R35P-D")

    divider()

    return {
        "status": status,
        "dns_ok": dns_ok,
        "request_attempted": request_attempted,
        "http_read_ok": http_read_ok,
        "http_status": http_status,
        "json_parse_ok": json_parse_ok,
        "btcusdt_mark_price_found": btcusdt_mark_price_found,
        "mark_price": mark_price,
        "mark_price_field": mark_price_field,
        "mark_price_numeric": mark_price_numeric,
        "mark_price_positive": mark_price_positive,
        "public_mark_price_read_ok": public_mark_price_read_ok,
        "failure_stage": failure_stage,
        "exception_class": exception_class,
        "exception_message": exception_message,
        "safety_invariants_ok": safety_ok,
    }


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:
    start_health_server()

    result = run_test()

    heartbeat = 1

    while True:
        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"PUBLIC_MARK_PRICE_READ_OK={result['public_mark_price_read_ok']} "
            f"MARK_PRICE={result['mark_price']} "
            f"MARK_PRICE_FIELD={result['mark_price_field']} "
            f"TEST_STATUS={result['status']} "
            f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )

        heartbeat += 1
        time.sleep(HEARTBEAT_SECONDS)


if __name__ == "__main__":
    main()
