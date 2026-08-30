

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
# R35P-A
# MICRO-UNIT: RAW BTCUSDT MARK-PRICE READ
# ==================================================================================================
#
# PURPOSE
#
#   Test exactly ONE previously failing component:
#
#       WEEX PUBLIC BTCUSDT MARK-PRICE READ
#
#   This unit deliberately does NOT:
#
#       - read account balance
#       - read positions
#       - determine whether BTCUSDT is flat
#       - read margin mode
#       - read long leverage
#       - read short leverage
#       - send an order
#       - change leverage
#       - change margin mode
#       - mutate positions
#       - perform any authenticated exchange request
#
#
# PASS CONDITION
#
#   The exact WEEX V3 public endpoint:
#
#       GET /capi/v3/market/symbolPrice
#
#   must return:
#
#       symbol = BTCUSDT
#       price  = positive numeric value
#
#
# SAFETY INVARIANTS
#
#       REAL_ORDER_EXECUTION=False
#       FIRST_REAL_ORDER_ALLOWED=False
#       EXCHANGE_NETWORK_WRITES=0
#
#
# IMPORTANT
#
#   HTTP GET to a PUBLIC MARKET-DATA endpoint is a network READ.
#   It is NOT counted as an exchange network WRITE.
#
# ==================================================================================================


VERSION = "R35P-A"
SYMBOL = "BTCUSDT"

WEEX_CONTRACT_BASE_URL = "https://api-contract.weex.com"
MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"

HEALTH_PORT = int(os.environ.get("PORT", "10000"))

HTTP_TIMEOUT_SECONDS = 15
HEARTBEAT_SECONDS = 30


# ==================================================================================================
# HARD SAFETY FLAGS
# ==================================================================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False

EXCHANGE_NETWORK_WRITES = 0
EXCHANGE_PUBLIC_READS = 0
EXCHANGE_AUTHENTICATED_READS = 0

LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0
ORDER_SUBMISSIONS = 0


# ==================================================================================================
# LOGGING
# ==================================================================================================


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str = "") -> None:
    print(f"{utc_now()} {message}", flush=True)


def separator() -> None:
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
        # Suppress normal HTTP server request logging.
        return


def start_health_server() -> None:

    def runner() -> None:
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)

        log(
            f"{VERSION}: HEALTH SERVER STARTED "
            f"ON PORT {HEALTH_PORT}"
        )

        server.serve_forever()

    thread = threading.Thread(
        target=runner,
        daemon=True,
        name="r35pa-health-server",
    )

    thread.start()


# ==================================================================================================
# SAFE STRING HELPERS
# ==================================================================================================


def safe_preview(value: Any, max_length: int = 500) -> str:
    """
    Produce a bounded printable representation.

    This unit uses a public endpoint only, so the response should contain no
    credentials. The preview is still intentionally bounded.
    """

    try:
        text = json.dumps(
            value,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    except Exception:
        text = str(value)

    if len(text) > max_length:
        return text[:max_length] + "...[TRUNCATED]"

    return text


# ==================================================================================================
# NETWORK DIAGNOSTIC RESULT
# ==================================================================================================


def resolve_host(hostname: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Perform an explicit DNS-resolution diagnostic.

    This is useful because earlier deployments showed intermittent DNS/name
    resolution failures.

    Returns:
        (
            success,
            one_resolved_ip_or_none,
            error_or_none,
        )
    """

    try:
        infos = socket.getaddrinfo(
            hostname,
            443,
            type=socket.SOCK_STREAM,
        )

        addresses = []

        for info in infos:
            sockaddr = info[4]

            if sockaddr:
                address = sockaddr[0]

                if address not in addresses:
                    addresses.append(address)

        if not addresses:
            return (
                False,
                None,
                "DNS_RESOLUTION_RETURNED_NO_ADDRESSES",
            )

        return (
            True,
            addresses[0],
            None,
        )

    except Exception as exc:
        return (
            False,
            None,
            f"{type(exc).__name__}: {exc}",
        )


# ==================================================================================================
# R35P-A PUBLIC MARK-PRICE GET
# ==================================================================================================


def read_raw_mark_price() -> Dict[str, Any]:
    """
    Perform exactly ONE WEEX public market-data request.

    Exact endpoint:

        GET https://api-contract.weex.com/capi/v3/market/symbolPrice
            ?symbol=BTCUSDT
            &priceType=MARK

    No API credentials are used.
    """

    global EXCHANGE_PUBLIC_READS

    result: Dict[str, Any] = {
        "dns_ok": False,
        "dns_ip": None,
        "dns_error": None,

        "request_attempted": False,
        "http_read_ok": False,
        "http_status": None,

        "content_type": None,
        "response_bytes": 0,
        "raw_body_preview": None,

        "json_parse_ok": False,
        "response_type": None,
        "response_keys": [],

        "returned_symbol": None,
        "raw_price": None,
        "mark_price": None,

        "symbol_match": False,
        "price_numeric": False,
        "price_positive": False,

        "exception_class": None,
        "exception_message": None,

        "pass": False,
    }

    hostname = "api-contract.weex.com"

    # ----------------------------------------------------------------------------------------------
    # STEP A1 — DNS
    # ----------------------------------------------------------------------------------------------

    dns_ok, dns_ip, dns_error = resolve_host(hostname)

    result["dns_ok"] = dns_ok
    result["dns_ip"] = dns_ip
    result["dns_error"] = dns_error

    # We do NOT stop here if explicit DNS resolution fails.
    #
    # urllib is allowed to attempt the actual request so that we capture its
    # authoritative transport failure as well.

    # ----------------------------------------------------------------------------------------------
    # STEP A2 — BUILD EXACT URL
    # ----------------------------------------------------------------------------------------------

    query = urllib.parse.urlencode(
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        }
    )

    url = (
        WEEX_CONTRACT_BASE_URL
        + MARK_PRICE_PATH
        + "?"
        + query
    )

    result["url"] = url

    # ----------------------------------------------------------------------------------------------
    # STEP A3 — PREPARE PUBLIC GET
    # ----------------------------------------------------------------------------------------------

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}/1.0",
        },
    )

    result["request_attempted"] = True

    EXCHANGE_PUBLIC_READS += 1

    try:

        # ------------------------------------------------------------------------------------------
        # STEP A4 — PERFORM GET
        # ------------------------------------------------------------------------------------------

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            status = int(
                getattr(response, "status", response.getcode())
            )

            content_type = response.headers.get(
                "Content-Type",
                "",
            )

            raw_bytes = response.read()

        result["http_status"] = status
        result["content_type"] = content_type
        result["response_bytes"] = len(raw_bytes)

        raw_text = raw_bytes.decode(
            "utf-8",
            errors="replace",
        )

        result["raw_body_preview"] = (
            raw_text[:500]
            + (
                "...[TRUNCATED]"
                if len(raw_text) > 500
                else ""
            )
        )

        if status != 200:
            result["exception_class"] = "NON_200_HTTP_STATUS"
            result["exception_message"] = (
                f"Expected HTTP 200 but received HTTP {status}"
            )

            return result

        result["http_read_ok"] = True

        # ------------------------------------------------------------------------------------------
        # STEP A5 — JSON PARSE
        # ------------------------------------------------------------------------------------------

        try:
            payload = json.loads(raw_text)

        except json.JSONDecodeError as exc:

            result["exception_class"] = type(exc).__name__
            result["exception_message"] = str(exc)

            return result

        result["json_parse_ok"] = True
        result["response_type"] = type(payload).__name__

        # ------------------------------------------------------------------------------------------
        # STEP A6 — RESPONSE SHAPE
        # ------------------------------------------------------------------------------------------

        if not isinstance(payload, dict):

            result["exception_class"] = "UNEXPECTED_RESPONSE_TYPE"
            result["exception_message"] = (
                "Expected JSON object but received "
                f"{type(payload).__name__}"
            )

            return result

        result["response_keys"] = sorted(
            str(key)
            for key in payload.keys()
        )

        # ------------------------------------------------------------------------------------------
        # STEP A7 — SYMBOL
        # ------------------------------------------------------------------------------------------

        returned_symbol = payload.get("symbol")

        if returned_symbol is not None:
            returned_symbol = str(returned_symbol)

        result["returned_symbol"] = returned_symbol

        result["symbol_match"] = (
            returned_symbol == SYMBOL
        )

        # ------------------------------------------------------------------------------------------
        # STEP A8 — PRICE FIELD
        # ------------------------------------------------------------------------------------------

        raw_price = payload.get("price")

        result["raw_price"] = raw_price

        try:
            numeric_price = float(raw_price)

            result["price_numeric"] = True
            result["mark_price"] = numeric_price

            if numeric_price > 0:
                result["price_positive"] = True

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            result["price_numeric"] = False
            result["price_positive"] = False

        # ------------------------------------------------------------------------------------------
        # STEP A9 — FINAL PASS
        # ------------------------------------------------------------------------------------------

        result["pass"] = bool(
            result["http_read_ok"]
            and result["json_parse_ok"]
            and result["symbol_match"]
            and result["price_numeric"]
            and result["price_positive"]
        )

        return result

    # ------------------------------------------------------------------------------------------------
    # HTTP ERROR
    # ------------------------------------------------------------------------------------------------

    except urllib.error.HTTPError as exc:

        result["http_status"] = exc.code
        result["exception_class"] = type(exc).__name__
        result["exception_message"] = str(exc)

        try:
            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

            result["raw_body_preview"] = (
                error_body[:500]
                + (
                    "...[TRUNCATED]"
                    if len(error_body) > 500
                    else ""
                )
            )

        except Exception:
            pass

        return result

    # ------------------------------------------------------------------------------------------------
    # URL / DNS / TLS / CONNECTION ERROR
    # ------------------------------------------------------------------------------------------------

    except urllib.error.URLError as exc:

        result["exception_class"] = type(exc).__name__
        result["exception_message"] = str(exc.reason)

        return result

    # ------------------------------------------------------------------------------------------------
    # TIMEOUT
    # ------------------------------------------------------------------------------------------------

    except TimeoutError as exc:

        result["exception_class"] = type(exc).__name__
        result["exception_message"] = str(exc)

        return result

    # ------------------------------------------------------------------------------------------------
    # ANY OTHER READ-SIDE FAILURE
    # ------------------------------------------------------------------------------------------------

    except Exception as exc:

        result["exception_class"] = type(exc).__name__
        result["exception_message"] = str(exc)

        return result


# ==================================================================================================
# SAFETY ASSERTIONS
# ==================================================================================================


def verify_safety_invariants() -> bool:

    checks = [
        REAL_ORDER_EXECUTION is False,
        DEMO_ORDER_EXECUTION is False,
        FIRST_REAL_ORDER_ALLOWED is False,

        EXCHANGE_NETWORK_WRITES == 0,

        EXCHANGE_AUTHENTICATED_READS == 0,

        LEVERAGE_MUTATIONS == 0,
        MARGIN_MODE_MUTATIONS == 0,
        POSITION_MUTATIONS == 0,
        ORDER_SUBMISSIONS == 0,
    ]

    return all(checks)


# ==================================================================================================
# REPORT
# ==================================================================================================


def print_report(result: Dict[str, Any]) -> None:

    separator()
    log(f"{VERSION}: RAW MARK-PRICE DIAGNOSTIC")
    separator()

    log(f"TEST=RAW_MARK_PRICE_READ")
    log(f"SYMBOL={SYMBOL}")

    log(
        "ENDPOINT="
        f"{WEEX_CONTRACT_BASE_URL}{MARK_PRICE_PATH}"
    )

    log("METHOD=GET")
    log("PRICE_TYPE=MARK")

    separator()
    log(f"{VERSION}: DNS")
    separator()

    log(f"DNS_OK={result['dns_ok']}")
    log(f"DNS_IP={result['dns_ip']}")
    log(f"DNS_ERROR={result['dns_error']}")

    separator()
    log(f"{VERSION}: HTTP")
    separator()

    log(
        f"REQUEST_ATTEMPTED="
        f"{result['request_attempted']}"
    )

    log(
        f"HTTP_READ_OK="
        f"{result['http_read_ok']}"
    )

    log(
        f"HTTP_STATUS="
        f"{result['http_status']}"
    )

    log(
        f"CONTENT_TYPE="
        f"{result['content_type']}"
    )

    log(
        f"RESPONSE_BYTES="
        f"{result['response_bytes']}"
    )

    separator()
    log(f"{VERSION}: RESPONSE SHAPE")
    separator()

    log(
        f"JSON_PARSE_OK="
        f"{result['json_parse_ok']}"
    )

    log(
        f"RESPONSE_TYPE="
        f"{result['response_type']}"
    )

    log(
        "RESPONSE_KEYS="
        + safe_preview(result["response_keys"])
    )

    log(
        "RAW_BODY_PREVIEW="
        + str(result["raw_body_preview"])
    )

    separator()
    log(f"{VERSION}: MARK PRICE EXTRACTION")
    separator()

    log(
        f"RETURNED_SYMBOL="
        f"{result['returned_symbol']}"
    )

    log(
        f"SYMBOL_MATCH="
        f"{result['symbol_match']}"
    )

    log(
        f"RAW_PRICE="
        f"{result['raw_price']}"
    )

    log(
        f"MARK_PRICE="
        f"{result['mark_price']}"
    )

    log(
        f"PRICE_NUMERIC="
        f"{result['price_numeric']}"
    )

    log(
        f"PRICE_POSITIVE="
        f"{result['price_positive']}"
    )

    separator()
    log(f"{VERSION}: ERROR DIAGNOSTIC")
    separator()

    log(
        f"EXCEPTION_CLASS="
        f"{result['exception_class']}"
    )

    log(
        f"EXCEPTION_MESSAGE="
        f"{result['exception_message']}"
    )

    separator()
    log(f"{VERSION}: SAFETY")
    separator()

    safety_ok = verify_safety_invariants()

    log(
        f"PUBLIC_MARKET_GETS="
        f"{EXCHANGE_PUBLIC_READS}"
    )

    log(
        f"AUTHENTICATED_WEEX_READS="
        f"{EXCHANGE_AUTHENTICATED_READS}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"ORDER_SUBMISSIONS="
        f"{ORDER_SUBMISSIONS}"
    )

    log(
        f"LEVERAGE_MUTATIONS="
        f"{LEVERAGE_MUTATIONS}"
    )

    log(
        f"MARGIN_MODE_MUTATIONS="
        f"{MARGIN_MODE_MUTATIONS}"
    )

    log(
        f"POSITION_MUTATIONS="
        f"{POSITION_MUTATIONS}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        f"SAFETY_INVARIANTS_OK="
        f"{safety_ok}"
    )

    separator()
    log(f"{VERSION} RESULT")
    separator()

    final_pass = bool(
        result["pass"]
        and safety_ok
        and EXCHANGE_NETWORK_WRITES == 0
    )

    log("TEST=RAW_MARK_PRICE_READ")

    log(
        f"DNS_OK="
        f"{result['dns_ok']}"
    )

    log(
        f"HTTP_READ_OK="
        f"{result['http_read_ok']}"
    )

    log(
        f"JSON_PARSE_OK="
        f"{result['json_parse_ok']}"
    )

    log(
        f"SYMBOL_MATCH="
        f"{result['symbol_match']}"
    )

    log(
        f"MARK_PRICE="
        f"{result['mark_price']}"
    )

    log(
        f"PRICE_POSITIVE="
        f"{result['price_positive']}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES="
        f"{EXCHANGE_NETWORK_WRITES}"
    )

    log(
        f"REAL_ORDER_EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED="
        f"{FIRST_REAL_ORDER_ALLOWED}"
    )

    if final_pass:
        log("STATUS=PASS")
        log(
            "NEXT_UNIT=R35P-B_RAW_POSITION_READ"
        )
    else:
        log("STATUS=FAIL")
        log(
            "NEXT_UNIT=STOP_AND_FIX_R35P-A"
        )

    separator()


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    # Give the health-server thread a very small opportunity to bind before
    # beginning the test.
    time.sleep(0.25)

    separator()
    log(f"{VERSION}: MAIN.PY ENTERED")
    separator()

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(f"{VERSION}: HEALTH PORT={HEALTH_PORT}")

    log(
        f"{VERSION}: TEST SCOPE="
        "PUBLIC BTCUSDT MARK PRICE ONLY"
    )

    log(
        f"{VERSION}: WEEX CONTRACT BASE="
        f"{WEEX_CONTRACT_BASE_URL}"
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
        f"{VERSION}: AUTHENTICATED READS="
        f"{EXCHANGE_AUTHENTICATED_READS}"
    )

    separator()
    log(f"{VERSION}: BEGIN SINGLE TEST")
    separator()

    result = read_raw_mark_price()

    print_report(result)

    # Keep Render service alive after the single diagnostic.
    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT={heartbeat} "
            f"MARK_PRICE={result['mark_price']} "
            f"TEST_STATUS={'PASS' if result['pass'] else 'FAIL'} "
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
        )

        time.sleep(HEARTBEAT_SECONDS)


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================


if __name__ == "__main__":
    main()

