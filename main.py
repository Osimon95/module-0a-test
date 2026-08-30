

from __future__ import annotations

import json
import os
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
# R35P-E
# SINGLE TEST:
#   WEEX PUBLIC V2 BTCUSDT MARK-PRICE READ
#
# PURPOSE:
#   Prove or disprove that the R35P-D HTTP 400 failure was caused specifically
#   by using the canonical/V3 symbol "BTCUSDT" on the legacy V2 ticker endpoint.
#
# THIS UNIT CHANGES ONE THING ONLY:
#
#   Canonical bot symbol:
#       BTCUSDT
#
#   V2 market API symbol:
#       cmt_btcusdt
#
#   Endpoint:
#       GET /capi/v2/market/ticker?symbol=cmt_btcusdt
#
# EXPECTED SUCCESS RESPONSE:
#   {
#       "symbol": "cmt_btcusdt",
#       ...
#       "markPrice": "<positive numeric value>",
#       ...
#   }
#
# SAFETY:
#   - PUBLIC GET ONLY
#   - NO AUTHENTICATED WEEX REQUEST
#   - NO POST
#   - NO PUT
#   - NO PATCH
#   - NO DELETE
#   - NO ORDER SUBMISSION
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MODE MUTATION
#   - NO POSITION MUTATION
#   - REAL ORDER EXECUTION HARD DISABLED
#   - FIRST REAL ORDER HARD FORBIDDEN
#
# DO NOT PROMOTE BEYOND R35P-E UNLESS THIS SINGLE TEST PASSES.
# ==================================================================================================


VERSION = "R35P-E"

# --------------------------------------------------------------------------------------------------
# CANONICAL BOT SYMBOL
# --------------------------------------------------------------------------------------------------

SYMBOL = "BTCUSDT"

# --------------------------------------------------------------------------------------------------
# LEGACY WEEX CONTRACT V2 MARKET SYMBOL
# --------------------------------------------------------------------------------------------------
#
# IMPORTANT:
#   DO NOT replace SYMBOL globally with this value.
#
#   BTCUSDT remains the bot's canonical symbol.
#   cmt_btcusdt is used ONLY where the WEEX V2 contract API requires it.
# --------------------------------------------------------------------------------------------------

V2_MARKET_SYMBOL = "cmt_btcusdt"


# --------------------------------------------------------------------------------------------------
# WEEX PUBLIC CONTRACT API
# --------------------------------------------------------------------------------------------------

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"
MARK_PRICE_PATH = "/capi/v2/market/ticker"

HTTP_TIMEOUT_SECONDS = 15


# --------------------------------------------------------------------------------------------------
# HEALTH SERVER
# --------------------------------------------------------------------------------------------------

PORT = int(os.getenv("PORT", "10000"))


# --------------------------------------------------------------------------------------------------
# HEARTBEAT
# --------------------------------------------------------------------------------------------------

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
# TEST STATE
# ==================================================================================================

DNS_OK = False
DNS_IP: Optional[str] = None
DNS_ERROR: Optional[str] = None

REQUEST_ATTEMPTED = False
HTTP_READ_OK = False
HTTP_STATUS: Optional[int] = None
CONTENT_TYPE: Optional[str] = None
RESPONSE_BYTES = 0

RAW_BODY_PREVIEW: Optional[str] = None

JSON_PARSE_OK = False
RESPONSE_TYPE: Optional[str] = None
RESPONSE_KEYS: Optional[list[str]] = None

RESPONSE_SYMBOL: Optional[str] = None
RESPONSE_SYMBOL_MATCH = False

BTCUSDT_MARK_PRICE_FOUND = False
MARK_PRICE: Optional[float] = None
MARK_PRICE_RAW: Any = None
MARK_PRICE_FIELD: Optional[str] = None
MARK_PRICE_NUMERIC = False
MARK_PRICE_POSITIVE = False
MARK_PRICE_RESPONSE_SHAPE: Optional[str] = None

FAILURE_STAGE: Optional[str] = None
EXCEPTION_CLASS: Optional[str] = None
EXCEPTION_MESSAGE: Optional[str] = None

PUBLIC_MARK_PRICE_READ_OK = False
TEST_STATUS = "NOT_RUN"


# ==================================================================================================
# LOGGING
# ==================================================================================================

LINE = "-" * 100


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str = "") -> None:
    print(f"{utc_now()} {message}", flush=True)


def section(title: str) -> None:
    log(LINE)
    log(title)
    log(LINE)


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
                "v2_market_symbol": V2_MARKET_SYMBOL,
                "public_mark_price_read_ok": PUBLIC_MARK_PRICE_READ_OK,
                "mark_price": MARK_PRICE,
                "test_status": TEST_STATUS,
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

    def runner() -> None:
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        log(f"{VERSION}: HEALTH SERVER STARTED ON PORT {PORT}")
        server.serve_forever()

    thread = threading.Thread(
        target=runner,
        daemon=True,
        name="health-server",
    )
    thread.start()


# ==================================================================================================
# SAFETY VALIDATION
# ==================================================================================================

def safety_invariants_ok() -> bool:
    return all(
        [
            REAL_ORDER_EXECUTION is False,
            FIRST_REAL_ORDER_ALLOWED is False,
            DEMO_ORDER_EXECUTION is False,
            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,
            AUTHENTICATED_WEEX_READS == 0,
        ]
    )


# ==================================================================================================
# DNS TEST
# ==================================================================================================

def test_dns() -> Tuple[bool, Optional[str], Optional[str]]:

    try:
        ip = socket.gethostbyname("api-contract.weex.com")
        return True, ip, None

    except Exception as exc:
        return False, None, f"{exc.__class__.__name__}: {exc}"


# ==================================================================================================
# SAFE PUBLIC HTTP GET
# ==================================================================================================

def public_http_get(url: str) -> Tuple[
    bool,
    Optional[int],
    Optional[str],
    bytes,
    Optional[BaseException],
]:
    """
    Performs exactly one PUBLIC HTTP GET.

    This function cannot submit orders and does not use authentication.
    """

    global PUBLIC_MARKET_GETS
    global REQUEST_ATTEMPTED

    REQUEST_ATTEMPTED = True
    PUBLIC_MARKET_GETS += 1

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-public-diagnostic",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            status = int(response.status)

            content_type = response.headers.get(
                "Content-Type",
                "",
            )

            body = response.read()

            return (
                200 <= status < 300,
                status,
                content_type,
                body,
                None,
            )

    except urllib.error.HTTPError as exc:

        # IMPORTANT:
        # HTTPError may still contain a useful JSON body from WEEX.
        try:
            body = exc.read()
        except Exception:
            body = b""

        content_type = None

        try:
            content_type = exc.headers.get("Content-Type")
        except Exception:
            pass

        return (
            False,
            int(exc.code),
            content_type,
            body,
            exc,
        )

    except Exception as exc:

        return (
            False,
            None,
            None,
            b"",
            exc,
        )


# ==================================================================================================
# JSON PARSER
# ==================================================================================================

def parse_json_body(body: bytes) -> Tuple[
    bool,
    Optional[Any],
    Optional[BaseException],
]:

    try:
        text = body.decode("utf-8", errors="replace").strip()

        if not text:
            raise ValueError("Response body is empty")

        parsed = json.loads(text)

        return True, parsed, None

    except Exception as exc:
        return False, None, exc


# ==================================================================================================
# MARK PRICE EXTRACTION
# ==================================================================================================

def extract_mark_price(
    payload: Any,
) -> Tuple[
    bool,
    Optional[float],
    Any,
    Optional[str],
    bool,
    bool,
    Optional[str],
    Optional[str],
]:
    """
    R35P-E intentionally expects the documented V2 single-ticker shape:

        {
            "symbol": "cmt_btcusdt",
            ...
            "markPrice": "..."
        }

    We do not silently accept unrelated fields such as lastPrice.
    """

    response_symbol: Optional[str] = None

    if not isinstance(payload, dict):
        return (
            False,
            None,
            None,
            None,
            False,
            False,
            type(payload).__name__,
            response_symbol,
        )

    response_symbol_raw = payload.get("symbol")

    if response_symbol_raw is not None:
        response_symbol = str(response_symbol_raw)

    if "markPrice" not in payload:
        return (
            False,
            None,
            None,
            None,
            False,
            False,
            "dict",
            response_symbol,
        )

    raw_value = payload.get("markPrice")

    try:
        numeric_value = float(raw_value)
        numeric = True
    except (TypeError, ValueError):
        numeric_value = None
        numeric = False

    positive = bool(
        numeric
        and numeric_value is not None
        and numeric_value > 0
    )

    found = bool(
        raw_value is not None
        and numeric
        and positive
    )

    return (
        found,
        numeric_value,
        raw_value,
        "markPrice",
        numeric,
        positive,
        "dict",
        response_symbol,
    )


# ==================================================================================================
# SINGLE R35P-E TEST
# ==================================================================================================

def run_single_test() -> None:

    global DNS_OK
    global DNS_IP
    global DNS_ERROR

    global HTTP_READ_OK
    global HTTP_STATUS
    global CONTENT_TYPE
    global RESPONSE_BYTES
    global RAW_BODY_PREVIEW

    global JSON_PARSE_OK
    global RESPONSE_TYPE
    global RESPONSE_KEYS

    global RESPONSE_SYMBOL
    global RESPONSE_SYMBOL_MATCH

    global BTCUSDT_MARK_PRICE_FOUND
    global MARK_PRICE
    global MARK_PRICE_RAW
    global MARK_PRICE_FIELD
    global MARK_PRICE_NUMERIC
    global MARK_PRICE_POSITIVE
    global MARK_PRICE_RESPONSE_SHAPE

    global FAILURE_STAGE
    global EXCEPTION_CLASS
    global EXCEPTION_MESSAGE

    global PUBLIC_MARK_PRICE_READ_OK
    global TEST_STATUS

    # ----------------------------------------------------------------------------------------------
    # EXACT URL
    # ----------------------------------------------------------------------------------------------

    query = urllib.parse.urlencode(
        {
            "symbol": V2_MARKET_SYMBOL,
        }
    )

    endpoint = (
        f"{WEEX_CONTRACT_BASE}"
        f"{MARK_PRICE_PATH}"
        f"?{query}"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST HEADER
    # ----------------------------------------------------------------------------------------------

    section(f"{VERSION}: BEGIN SINGLE TEST")

    section(f"{VERSION}: V2 SYMBOL TRANSLATION")

    log(f"CANONICAL_SYMBOL={SYMBOL}")
    log(f"V2_MARKET_SYMBOL={V2_MARKET_SYMBOL}")
    log(f"CANONICAL_SYMBOL_UNCHANGED={SYMBOL == 'BTCUSDT'}")
    log(
        "ONLY_TEST_VARIABLE="
        "R35P-D used BTCUSDT; R35P-E uses cmt_btcusdt on same V2 ticker endpoint"
    )

    section(f"{VERSION}: RAW PUBLIC MARK PRICE DIAGNOSTIC")

    log("TEST=RAW_PUBLIC_V2_BTCUSDT_MARK_PRICE_READ")
    log(f"SYMBOL={SYMBOL}")
    log(f"V2_MARKET_SYMBOL={V2_MARKET_SYMBOL}")
    log(f"ENDPOINT={endpoint}")
    log("METHOD=GET")
    log("AUTHENTICATION=NONE_PUBLIC_MARKET_DATA")

    # ----------------------------------------------------------------------------------------------
    # DNS
    # ----------------------------------------------------------------------------------------------

    section(f"{VERSION}: DNS")

    DNS_OK, DNS_IP, DNS_ERROR = test_dns()

    log(f"DNS_OK={DNS_OK}")
    log(f"DNS_IP={DNS_IP}")
    log(f"DNS_ERROR={DNS_ERROR}")

    if not DNS_OK:
        FAILURE_STAGE = "DNS"

        section(f"{VERSION}: ERROR DIAGNOSTIC")

        log(f"FAILURE_STAGE={FAILURE_STAGE}")
        log("EXCEPTION_CLASS=DNS_RESOLUTION_FAILED")
        log(f"EXCEPTION_MESSAGE={DNS_ERROR}")

        TEST_STATUS = "FAIL"

        report_result()
        return

    # ----------------------------------------------------------------------------------------------
    # PUBLIC GET
    # ----------------------------------------------------------------------------------------------

    section(f"{VERSION}: PUBLIC HTTP GET")

    (
        HTTP_READ_OK,
        HTTP_STATUS,
        CONTENT_TYPE,
        body,
        http_exception,
    ) = public_http_get(endpoint)

    RESPONSE_BYTES = len(body)

    log(f"REQUEST_ATTEMPTED={REQUEST_ATTEMPTED}")
    log(f"HTTP_READ_OK={HTTP_READ_OK}")
    log(f"HTTP_STATUS={HTTP_STATUS}")
    log(f"CONTENT_TYPE={CONTENT_TYPE}")
    log(f"RESPONSE_BYTES={RESPONSE_BYTES}")

    # ----------------------------------------------------------------------------------------------
    # RAW RESPONSE
    # ----------------------------------------------------------------------------------------------

    section(f"{VERSION}: RAW RESPONSE")

    RAW_BODY_PREVIEW = body.decode(
        "utf-8",
        errors="replace",
    )

    if len(RAW_BODY_PREVIEW) > 2000:
        RAW_BODY_PREVIEW = RAW_BODY_PREVIEW[:2000] + "...[TRUNCATED]"

    log(f"RAW_BODY_PREVIEW={RAW_BODY_PREVIEW}")

    # ----------------------------------------------------------------------------------------------
    # PARSE JSON EVEN WHEN HTTP STATUS IS NON-2XX
    #
    # This improves R35P-D behavior because WEEX's error JSON is still useful diagnostic data.
    # ----------------------------------------------------------------------------------------------

    section(f"{VERSION}: RESPONSE SHAPE")

    JSON_PARSE_OK, payload, json_exception = parse_json_body(body)

    if JSON_PARSE_OK:
        RESPONSE_TYPE = type(payload).__name__

        if isinstance(payload, dict):
            RESPONSE_KEYS = list(payload.keys())

        else:
            RESPONSE_KEYS = None

    else:
        RESPONSE_TYPE = None
        RESPONSE_KEYS = None

    log(f"JSON_PARSE_OK={JSON_PARSE_OK}")
    log(f"RESPONSE_TYPE={RESPONSE_TYPE}")
    log(f"RESPONSE_KEYS={RESPONSE_KEYS}")

    # ----------------------------------------------------------------------------------------------
    # MARK PRICE EXTRACTION
    # ----------------------------------------------------------------------------------------------

    section(f"{VERSION}: BTCUSDT MARK PRICE EXTRACTION")

    if JSON_PARSE_OK:

        (
            BTCUSDT_MARK_PRICE_FOUND,
            MARK_PRICE,
            MARK_PRICE_RAW,
            MARK_PRICE_FIELD,
            MARK_PRICE_NUMERIC,
            MARK_PRICE_POSITIVE,
            MARK_PRICE_RESPONSE_SHAPE,
            RESPONSE_SYMBOL,
        ) = extract_mark_price(payload)

    else:

        BTCUSDT_MARK_PRICE_FOUND = False
        MARK_PRICE = None
        MARK_PRICE_RAW = None
        MARK_PRICE_FIELD = None
        MARK_PRICE_NUMERIC = False
        MARK_PRICE_POSITIVE = False
        MARK_PRICE_RESPONSE_SHAPE = None
        RESPONSE_SYMBOL = None

    RESPONSE_SYMBOL_MATCH = (
        RESPONSE_SYMBOL is not None
        and RESPONSE_SYMBOL.lower() == V2_MARKET_SYMBOL.lower()
    )

    log(f"CANONICAL_SYMBOL={SYMBOL}")
    log(f"REQUEST_SYMBOL={V2_MARKET_SYMBOL}")
    log(f"RESPONSE_SYMBOL={RESPONSE_SYMBOL}")
    log(f"RESPONSE_SYMBOL_MATCH={RESPONSE_SYMBOL_MATCH}")

    log(f"BTCUSDT_MARK_PRICE_FOUND={BTCUSDT_MARK_PRICE_FOUND}")
    log(f"MARK_PRICE={MARK_PRICE}")
    log(f"MARK_PRICE_RAW={MARK_PRICE_RAW}")
    log(f"MARK_PRICE_FIELD={MARK_PRICE_FIELD}")
    log(f"MARK_PRICE_NUMERIC={MARK_PRICE_NUMERIC}")
    log(f"MARK_PRICE_POSITIVE={MARK_PRICE_POSITIVE}")
    log(f"MARK_PRICE_RESPONSE_SHAPE={MARK_PRICE_RESPONSE_SHAPE}")

    # ----------------------------------------------------------------------------------------------
    # ERROR DIAGNOSTIC
    # ----------------------------------------------------------------------------------------------

    if not HTTP_READ_OK:

        FAILURE_STAGE = "HTTP_GET"

        if http_exception is not None:
            EXCEPTION_CLASS = http_exception.__class__.__name__
            EXCEPTION_MESSAGE = str(http_exception)

        else:
            EXCEPTION_CLASS = "UNKNOWN_HTTP_FAILURE"
            EXCEPTION_MESSAGE = "HTTP request failed"

    elif not JSON_PARSE_OK:

        FAILURE_STAGE = "JSON_PARSE"

        if json_exception is not None:
            EXCEPTION_CLASS = json_exception.__class__.__name__
            EXCEPTION_MESSAGE = str(json_exception)

    elif not RESPONSE_SYMBOL_MATCH:

        FAILURE_STAGE = "SYMBOL_RECONCILIATION"
        EXCEPTION_CLASS = "UnexpectedResponseSymbol"
        EXCEPTION_MESSAGE = (
            f"Expected {V2_MARKET_SYMBOL}, "
            f"received {RESPONSE_SYMBOL}"
        )

    elif not BTCUSDT_MARK_PRICE_FOUND:

        FAILURE_STAGE = "MARK_PRICE_EXTRACTION"
        EXCEPTION_CLASS = "MarkPriceNotFound"
        EXCEPTION_MESSAGE = (
            "Documented V2 markPrice field was not found "
            "as a positive numeric value"
        )

    else:

        FAILURE_STAGE = None
        EXCEPTION_CLASS = None
        EXCEPTION_MESSAGE = None

    section(f"{VERSION}: ERROR DIAGNOSTIC")

    log(f"FAILURE_STAGE={FAILURE_STAGE}")
    log(f"EXCEPTION_CLASS={EXCEPTION_CLASS}")
    log(f"EXCEPTION_MESSAGE={EXCEPTION_MESSAGE}")

    # ----------------------------------------------------------------------------------------------
    # FINAL PASS CONDITION
    # ----------------------------------------------------------------------------------------------

    PUBLIC_MARK_PRICE_READ_OK = all(
        [
            DNS_OK,
            REQUEST_ATTEMPTED,
            HTTP_READ_OK,
            HTTP_STATUS == 200,
            JSON_PARSE_OK,
            RESPONSE_SYMBOL_MATCH,
            BTCUSDT_MARK_PRICE_FOUND,
            MARK_PRICE_FIELD == "markPrice",
            MARK_PRICE_NUMERIC,
            MARK_PRICE_POSITIVE,
            safety_invariants_ok(),
        ]
    )

    TEST_STATUS = (
        "PASS"
        if PUBLIC_MARK_PRICE_READ_OK
        else "FAIL"
    )

    report_result()


# ==================================================================================================
# RESULT REPORT
# ==================================================================================================

def report_result() -> None:

    section(f"{VERSION}: SAFETY")

    log(f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS}")
    log(f"AUTHENTICATED_WEEX_READS={AUTHENTICATED_WEEX_READS}")

    log(f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}")
    log(f"ORDER_SUBMISSIONS={ORDER_SUBMISSIONS}")
    log(f"LEVERAGE_MUTATIONS={LEVERAGE_MUTATIONS}")
    log(f"MARGIN_MODE_MUTATIONS={MARGIN_MODE_MUTATIONS}")
    log(f"POSITION_MUTATIONS={POSITION_MUTATIONS}")

    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log(f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}")

    log(f"SAFETY_INVARIANTS_OK={safety_invariants_ok()}")

    section(f"{VERSION} RESULT")

    log("TEST=RAW_PUBLIC_V2_BTCUSDT_MARK_PRICE_READ")

    log(f"CANONICAL_SYMBOL={SYMBOL}")
    log(f"V2_MARKET_SYMBOL={V2_MARKET_SYMBOL}")

    log(f"DNS_OK={DNS_OK}")
    log(f"REQUEST_ATTEMPTED={REQUEST_ATTEMPTED}")

    log(f"HTTP_READ_OK={HTTP_READ_OK}")
    log(f"HTTP_STATUS={HTTP_STATUS}")

    log(f"JSON_PARSE_OK={JSON_PARSE_OK}")

    log(f"RESPONSE_SYMBOL={RESPONSE_SYMBOL}")
    log(f"RESPONSE_SYMBOL_MATCH={RESPONSE_SYMBOL_MATCH}")

    log(f"BTCUSDT_MARK_PRICE_FOUND={BTCUSDT_MARK_PRICE_FOUND}")
    log(f"MARK_PRICE={MARK_PRICE}")
    log(f"MARK_PRICE_FIELD={MARK_PRICE_FIELD}")

    log(f"MARK_PRICE_NUMERIC={MARK_PRICE_NUMERIC}")
    log(f"MARK_PRICE_POSITIVE={MARK_PRICE_POSITIVE}")

    log(
        f"PUBLIC_MARK_PRICE_READ_OK="
        f"{PUBLIC_MARK_PRICE_READ_OK}"
    )

    log(f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS}")
    log(
        f"AUTHENTICATED_WEEX_READS="
        f"{AUTHENTICATED_WEEX_READS}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}")
    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(f"STATUS={TEST_STATUS}")

    if TEST_STATUS == "PASS":
        log("ROOT_CAUSE_CONFIRMED=R35P-D_USED_WRONG_SYMBOL_FORMAT_FOR_V2_TICKER")
        log("R35P-D_SYMBOL=BTCUSDT")
        log("R35P-E_V2_SYMBOL=cmt_btcusdt")
        log("NEXT_UNIT=R35P-F")
    else:
        log("ROOT_CAUSE_CONFIRMED=False")
        log("NEXT_UNIT=STOP_AND_DIAGNOSE_R35P-E")

    log(LINE)


# ==================================================================================================
# HEARTBEAT LOOP
# ==================================================================================================

def heartbeat_loop() -> None:

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"PUBLIC_MARK_PRICE_READ_OK={PUBLIC_MARK_PRICE_READ_OK} "
            f"MARK_PRICE={MARK_PRICE} "
            f"MARK_PRICE_FIELD={MARK_PRICE_FIELD} "
            f"RESPONSE_SYMBOL={RESPONSE_SYMBOL} "
            f"TEST_STATUS={TEST_STATUS} "
            f"PUBLIC_MARKET_GETS={PUBLIC_MARKET_GETS} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )

        time.sleep(HEARTBEAT_SECONDS)


# ==================================================================================================
# MAIN
# ==================================================================================================

def main() -> None:

    start_health_server()

    # Give Render health thread a brief opportunity to start.
    time.sleep(0.20)

    section(f"{VERSION}: MAIN.PY ENTERED")

    log(f"{VERSION}: CANONICAL SYMBOL={SYMBOL}")
    log(f"{VERSION}: V2 MARKET SYMBOL={V2_MARKET_SYMBOL}")

    log(
        f"{VERSION}: WEEX CONTRACT BASE="
        f"{WEEX_CONTRACT_BASE}"
    )

    log(
        f"{VERSION}: MARK PRICE PATH="
        f"{MARK_PRICE_PATH}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: FIRST REAL ORDER ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"{VERSION}: EXCHANGE NETWORK WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"{VERSION}: PUBLIC MARKET GETS="
        f"{PUBLIC_MARKET_GETS}"
    )

    log(
        f"{VERSION}: AUTHENTICATED READS="
        f"{AUTHENTICATED_WEEX_READS}"
    )

    # ------------------------------------------------------------------------------------------------
    # ONE AND ONLY ONE EXCHANGE TEST
    # ------------------------------------------------------------------------------------------------

    run_single_test()

    # ------------------------------------------------------------------------------------------------
    # REMAIN ALIVE FOR RENDER
    # ------------------------------------------------------------------------------------------------

    heartbeat_loop()


# ==================================================================================================
# ENTRYPOINT
# ==================================================================================================

if __name__ == "__main__":
    main()
