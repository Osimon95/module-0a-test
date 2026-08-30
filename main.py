

from __future__ import annotations

import base64
import hashlib
import hmac
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
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35P-B - RAW AUTHENTICATED BTCUSDT POSITION READ
# ==================================================================================================
#
# PURPOSE
#
#   Test exactly ONE previously failing component:
#
#       Can this deployment perform an authenticated WEEX V3 read of the
#       BTCUSDT position endpoint and determine whether BTCUSDT is flat?
#
#   R35P-B intentionally does NOT test:
#
#       - mark price
#       - account balance
#       - margin mode reconciliation
#       - leverage reconciliation
#       - Telegram durability
#       - activation readiness
#       - strategy execution
#       - order placement
#
# SAFETY
#
#   - GET ONLY
#   - ONE authenticated WEEX read
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
# EXPECTED SUCCESS CASE
#
#   HTTP_STATUS=200
#   JSON_PARSE_OK=True
#   POSITION_RESPONSE_PARSED=True
#   BTCUSDT_POSITION_ROWS=<number>
#   BTCUSDT_OPEN_POSITION_COUNT=0
#   BTCUSDT_FLAT=True
#   EXCHANGE_NETWORK_WRITES=0
#   STATUS=PASS
#
# IMPORTANT
#
#   A successful authenticated read and a flat account are two separate facts.
#
#   For example:
#
#       AUTHENTICATED_POSITION_READ_OK=True
#       BTCUSDT_FLAT=False
#
#   would mean the endpoint works but a real position exists.
#
#   Conversely:
#
#       AUTHENTICATED_POSITION_READ_OK=False
#       BTCUSDT_FLAT=UNKNOWN
#
#   means we are NOT allowed to claim the account is non-flat merely because
#   the read failed.
#
# ==================================================================================================


VERSION = "R35P-B"

SYMBOL = "BTCUSDT"

HEALTH_PORT = int(os.environ.get("PORT", "10000"))

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"

POSITION_PATH = "/capi/v3/account/position/singlePosition"

REQUEST_METHOD = "GET"

REQUEST_TIMEOUT_SECONDS = 15


# ==================================================================================================
# HARD SAFETY FIREBREAKS
# ==================================================================================================


REAL_ORDER_EXECUTION = False

FIRST_REAL_ORDER_ALLOWED = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False


PUBLIC_MARKET_GETS = 0

AUTHENTICATED_WEEX_READS = 0

EXCHANGE_NETWORK_WRITES = 0

ORDER_SUBMISSIONS = 0

LEVERAGE_MUTATIONS = 0

MARGIN_MODE_MUTATIONS = 0

POSITION_MUTATIONS = 0


# ==================================================================================================
# RUNTIME RESULT STATE
# ==================================================================================================


TEST_STATUS = "NOT_RUN"

AUTHENTICATED_POSITION_READ_OK = False

BTCUSDT_FLAT: Optional[bool] = None

BTCUSDT_OPEN_POSITION_COUNT: Optional[int] = None

BTCUSDT_POSITION_ROWS: Optional[int] = None


# ==================================================================================================
# LOGGING
# ==================================================================================================


SEPARATOR = "-" * 100


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str = "") -> None:
    print(f"{utc_now()} {message}", flush=True)


def section(title: str) -> None:
    log(SEPARATOR)
    log(title)
    log(SEPARATOR)


def bool_text(value: Optional[bool]) -> str:
    if value is None:
        return "UNKNOWN"
    return str(value)


def value_text(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    return str(value)


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        body = (
            f"{VERSION} OK\n"
            f"SYMBOL={SYMBOL}\n"
            f"TEST_STATUS={TEST_STATUS}\n"
            f"AUTHENTICATED_POSITION_READ_OK={AUTHENTICATED_POSITION_READ_OK}\n"
            f"BTCUSDT_FLAT={bool_text(BTCUSDT_FLAT)}\n"
            f"BTCUSDT_OPEN_POSITION_COUNT={value_text(BTCUSDT_OPEN_POSITION_COUNT)}\n"
            f"EXCHANGE_NETWORK_WRITES={EXCHANGE_NETWORK_WRITES}\n"
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def start_health_server() -> None:

    try:
        server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)

        thread = threading.Thread(
            target=server.serve_forever,
            name="r35p-b-health",
            daemon=True,
        )

        thread.start()

        log(
            f"{VERSION}: HEALTH SERVER STARTED ON PORT "
            f"{HEALTH_PORT}"
        )

    except Exception as exc:
        log(
            f"{VERSION}: HEALTH SERVER ERROR "
            f"{exc.__class__.__name__}: {exc}"
        )


# ==================================================================================================
# ENVIRONMENT
# ==================================================================================================


def read_credentials() -> Tuple[str, str, str]:

    api_key = os.environ.get("WEEX_API_KEY", "").strip()

    api_secret = os.environ.get(
        "WEEX_API_SECRET",
        "",
    ).strip()

    api_passphrase = os.environ.get(
        "WEEX_API_PASSPHRASE",
        "",
    ).strip()

    return (
        api_key,
        api_secret,
        api_passphrase,
    )


# ==================================================================================================
# SIGNATURE
# ==================================================================================================
#
# WEEX authenticated GET signature:
#
#     timestamp
#     + METHOD
#     + request_path
#     + "?"
#     + query_string
#
# HMAC-SHA256 with WEEX_API_SECRET, then Base64.
#
# No request body exists for this GET.
#
# ==================================================================================================


def create_signature(
    secret: str,
    timestamp_ms: str,
    method: str,
    request_path: str,
    query_string: str,
) -> str:

    method = method.upper()

    if query_string:
        prehash = (
            timestamp_ms
            + method
            + request_path
            + "?"
            + query_string
        )
    else:
        prehash = (
            timestamp_ms
            + method
            + request_path
        )

    digest = hmac.new(
        secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


# ==================================================================================================
# RAW POSITION RESPONSE NORMALIZATION
# ==================================================================================================


def normalize_position_rows(payload: Any) -> Tuple[List[Dict[str, Any]], str]:
    """
    Accept the documented list response while also diagnosing possible
    wrapper shapes without falsely treating an unreadable structure as flat.
    """

    if isinstance(payload, list):

        rows = [
            item
            for item in payload
            if isinstance(item, dict)
        ]

        return rows, "list"

    if isinstance(payload, dict):

        # Defensive handling only.
        #
        # R35P-B prints the exact response keys so that if WEEX wraps the
        # documented list in another object in this account/environment we
        # can see the actual shape rather than silently guessing.

        possible_keys = (
            "data",
            "positions",
            "position",
            "result",
            "list",
        )

        for key in possible_keys:

            candidate = payload.get(key)

            if isinstance(candidate, list):

                rows = [
                    item
                    for item in candidate
                    if isinstance(item, dict)
                ]

                return rows, f"dict.{key}"

            if isinstance(candidate, dict):

                return [candidate], f"dict.{key}"

        # A dictionary that itself looks like a position row.
        if (
            "symbol" in payload
            or "size" in payload
            or "side" in payload
        ):
            return [payload], "dict.position_object"

    raise ValueError(
        "Position response does not contain a recognized position structure"
    )


# ==================================================================================================
# SIZE PARSING
# ==================================================================================================


def parse_position_size(position: Dict[str, Any]) -> float:

    raw_size = position.get("size")

    if raw_size is None:
        raise ValueError(
            "Position row is missing required field 'size'"
        )

    if isinstance(raw_size, bool):
        raise ValueError(
            f"Invalid position size type: bool ({raw_size})"
        )

    try:
        size = float(raw_size)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Position size is not numeric: {raw_size!r}"
        ) from exc

    return size


# ==================================================================================================
# POSITION ANALYSIS
# ==================================================================================================


def analyze_btcusdt_positions(
    rows: List[Dict[str, Any]],
) -> Dict[str, Any]:

    btc_rows: List[Dict[str, Any]] = []

    for row in rows:

        row_symbol = str(
            row.get("symbol", "")
        ).upper().strip()

        if row_symbol == SYMBOL:
            btc_rows.append(row)

    open_rows: List[Dict[str, Any]] = []

    row_diagnostics: List[Dict[str, Any]] = []

    for index, row in enumerate(btc_rows, start=1):

        size = parse_position_size(row)

        is_open = abs(size) > 0.0

        if is_open:
            open_rows.append(row)

        row_diagnostics.append(
            {
                "index": index,
                "symbol": row.get("symbol"),
                "side": row.get("side"),
                "size": row.get("size"),
                "numeric_size": size,
                "is_open": is_open,
            }
        )

    return {
        "all_rows_count": len(rows),
        "btcusdt_rows_count": len(btc_rows),
        "open_position_count": len(open_rows),
        "flat": len(open_rows) == 0,
        "rows": row_diagnostics,
    }


# ==================================================================================================
# AUTHENTICATED GET
# ==================================================================================================


def authenticated_position_get(
    api_key: str,
    api_secret: str,
    api_passphrase: str,
) -> Dict[str, Any]:

    global AUTHENTICATED_WEEX_READS

    # Exactly one query parameter.
    query_string = urllib.parse.urlencode(
        {
            "symbol": SYMBOL,
        }
    )

    timestamp_ms = str(
        int(time.time() * 1000)
    )

    signature = create_signature(
        secret=api_secret,
        timestamp_ms=timestamp_ms,
        method=REQUEST_METHOD,
        request_path=POSITION_PATH,
        query_string=query_string,
    )

    url = (
        WEEX_CONTRACT_BASE
        + POSITION_PATH
        + "?"
        + query_string
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}/1.0",
    }

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    AUTHENTICATED_WEEX_READS += 1

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        status = response.getcode()

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        raw_bytes = response.read()

    raw_text = raw_bytes.decode(
        "utf-8",
        errors="replace",
    )

    return {
        "url": url,
        "status": status,
        "content_type": content_type,
        "raw_bytes": raw_bytes,
        "raw_text": raw_text,
    }


# ==================================================================================================
# SAFETY CHECK
# ==================================================================================================


def safety_invariants_ok() -> bool:

    return all(
        [
            REAL_ORDER_EXECUTION is False,
            FIRST_REAL_ORDER_ALLOWED is False,
            DEMO_ORDER_EXECUTION is False,
            EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
            EXCHANGE_NETWORK_WRITES == 0,
            ORDER_SUBMISSIONS == 0,
            LEVERAGE_MUTATIONS == 0,
            MARGIN_MODE_MUTATIONS == 0,
            POSITION_MUTATIONS == 0,
        ]
    )


# ==================================================================================================
# SINGLE R35P-B TEST
# ==================================================================================================


def run_single_test() -> None:

    global TEST_STATUS
    global AUTHENTICATED_POSITION_READ_OK
    global BTCUSDT_FLAT
    global BTCUSDT_OPEN_POSITION_COUNT
    global BTCUSDT_POSITION_ROWS

    TEST_STATUS = "RUNNING"

    api_key, api_secret, api_passphrase = read_credentials()

    credentials_present = all(
        [
            bool(api_key),
            bool(api_secret),
            bool(api_passphrase),
        ]
    )

    # ----------------------------------------------------------------------------------------------
    # TEST IDENTIFICATION
    # ----------------------------------------------------------------------------------------------

    section(
        f"{VERSION}: RAW POSITION DIAGNOSTIC"
    )

    log("TEST=RAW_AUTHENTICATED_BTCUSDT_POSITION_READ")

    log(f"SYMBOL={SYMBOL}")

    log(
        f"ENDPOINT="
        f"{WEEX_CONTRACT_BASE}"
        f"{POSITION_PATH}"
        f"?symbol={SYMBOL}"
    )

    log("METHOD=GET")

    log("AUTHENTICATION=WEEX_V3_USER_DATA")

    # ----------------------------------------------------------------------------------------------
    # CREDENTIAL PRESENCE
    # ----------------------------------------------------------------------------------------------

    section(
        f"{VERSION}: CREDENTIAL PRESENCE"
    )

    log(
        f"WEEX_API_KEY_PRESENT="
        f"{bool(api_key)}"
    )

    log(
        f"WEEX_API_SECRET_PRESENT="
        f"{bool(api_secret)}"
    )

    log(
        f"WEEX_API_PASSPHRASE_PRESENT="
        f"{bool(api_passphrase)}"
    )

    log(
        f"ALL_REQUIRED_CREDENTIALS_PRESENT="
        f"{credentials_present}"
    )

    # Never print credentials.
    # Never print signature.
    # Never print the HMAC prehash.

    if not credentials_present:

        TEST_STATUS = "FAIL"

        section(
            f"{VERSION}: RESULT"
        )

        log(
            "TEST="
            "RAW_AUTHENTICATED_BTCUSDT_POSITION_READ"
        )

        log(
            "AUTHENTICATED_POSITION_READ_OK=False"
        )

        log(
            "BTCUSDT_POSITION_ROWS=UNKNOWN"
        )

        log(
            "BTCUSDT_OPEN_POSITION_COUNT=UNKNOWN"
        )

        log(
            "BTCUSDT_FLAT=UNKNOWN"
        )

        log(
            "FAILURE_STAGE=CREDENTIAL_PRESENCE"
        )

        log(
            "EXCEPTION_CLASS=None"
        )

        log(
            "EXCEPTION_MESSAGE="
            "Missing one or more required WEEX credentials"
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

        log("STATUS=FAIL")

        return

    # ----------------------------------------------------------------------------------------------
    # DNS
    # ----------------------------------------------------------------------------------------------

    section(
        f"{VERSION}: DNS"
    )

    dns_ok = False

    dns_ip: Optional[str] = None

    dns_error: Optional[str] = None

    try:

        dns_ip = socket.gethostbyname(
            "api-contract.weex.com"
        )

        dns_ok = True

    except Exception as exc:

        dns_error = (
            f"{exc.__class__.__name__}: {exc}"
        )

    log(
        f"DNS_OK={dns_ok}"
    )

    log(
        f"DNS_IP={value_text(dns_ip)}"
    )

    log(
        f"DNS_ERROR={dns_error}"
    )

    # ----------------------------------------------------------------------------------------------
    # HTTP / AUTHENTICATED READ
    # ----------------------------------------------------------------------------------------------

    section(
        f"{VERSION}: AUTHENTICATED HTTP GET"
    )

    request_attempted = False

    http_read_ok = False

    http_status: Optional[int] = None

    content_type: Optional[str] = None

    response_bytes: Optional[int] = None

    raw_body: Optional[str] = None

    exception_class: Optional[str] = None

    exception_message: Optional[str] = None

    failure_stage: Optional[str] = None

    json_parse_ok = False

    payload: Any = None

    response_type: Optional[str] = None

    response_keys: Optional[List[str]] = None

    position_response_parsed = False

    response_shape: Optional[str] = None

    try:

        request_attempted = True

        response = authenticated_position_get(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
        )

        http_status = response["status"]

        content_type = response["content_type"]

        raw_body = response["raw_text"]

        response_bytes = len(
            response["raw_bytes"]
        )

        http_read_ok = (
            200 <= int(http_status) < 300
        )

        log(
            f"REQUEST_ATTEMPTED="
            f"{request_attempted}"
        )

        log(
            f"HTTP_READ_OK="
            f"{http_read_ok}"
        )

        log(
            f"HTTP_STATUS="
            f"{http_status}"
        )

        log(
            f"CONTENT_TYPE="
            f"{content_type}"
        )

        log(
            f"RESPONSE_BYTES="
            f"{response_bytes}"
        )

        # ------------------------------------------------------------------------------------------
        # RAW RESPONSE
        # ------------------------------------------------------------------------------------------

        section(
            f"{VERSION}: RAW RESPONSE"
        )

        preview = (
            raw_body[:2000]
            if raw_body is not None
            else ""
        )

        log(
            f"RAW_BODY_PREVIEW={preview}"
        )

        # ------------------------------------------------------------------------------------------
        # JSON PARSE
        # ------------------------------------------------------------------------------------------

        section(
            f"{VERSION}: RESPONSE SHAPE"
        )

        try:

            payload = json.loads(
                raw_body
            )

            json_parse_ok = True

            response_type = type(
                payload
            ).__name__

            if isinstance(payload, dict):

                response_keys = sorted(
                    str(key)
                    for key in payload.keys()
                )

            log(
                f"JSON_PARSE_OK="
                f"{json_parse_ok}"
            )

            log(
                f"RESPONSE_TYPE="
                f"{response_type}"
            )

            log(
                "RESPONSE_KEYS="
                + (
                    json.dumps(
                        response_keys,
                        separators=(",", ":"),
                    )
                    if response_keys is not None
                    else "N/A"
                )
            )

        except Exception as exc:

            failure_stage = "JSON_PARSE"

            exception_class = (
                exc.__class__.__name__
            )

            exception_message = str(exc)

            log(
                "JSON_PARSE_OK=False"
            )

            log(
                "RESPONSE_TYPE=UNKNOWN"
            )

            log(
                "RESPONSE_KEYS=UNKNOWN"
            )

            raise

        # ------------------------------------------------------------------------------------------
        # POSITION STRUCTURE
        # ------------------------------------------------------------------------------------------

        section(
            f"{VERSION}: POSITION STRUCTURE"
        )

        rows, response_shape = normalize_position_rows(
            payload
        )

        position_response_parsed = True

        log(
            "POSITION_RESPONSE_PARSED=True"
        )

        log(
            f"POSITION_RESPONSE_SHAPE="
            f"{response_shape}"
        )

        log(
            f"TOTAL_RESPONSE_POSITION_ROWS="
            f"{len(rows)}"
        )

        # ------------------------------------------------------------------------------------------
        # BTCUSDT ANALYSIS
        # ------------------------------------------------------------------------------------------

        analysis = analyze_btcusdt_positions(
            rows
        )

        BTCUSDT_POSITION_ROWS = int(
            analysis["btcusdt_rows_count"]
        )

        BTCUSDT_OPEN_POSITION_COUNT = int(
            analysis["open_position_count"]
        )

        BTCUSDT_FLAT = bool(
            analysis["flat"]
        )

        AUTHENTICATED_POSITION_READ_OK = True

        section(
            f"{VERSION}: BTCUSDT POSITION EXTRACTION"
        )

        log(
            f"BTCUSDT_POSITION_ROWS="
            f"{BTCUSDT_POSITION_ROWS}"
        )

        log(
            f"BTCUSDT_OPEN_POSITION_COUNT="
            f"{BTCUSDT_OPEN_POSITION_COUNT}"
        )

        log(
            f"BTCUSDT_FLAT="
            f"{BTCUSDT_FLAT}"
        )

        # Print only non-secret position fields.
        #
        # This is diagnostic account state, not credential material.

        for row in analysis["rows"]:

            log(
                "POSITION_ROW="
                + json.dumps(
                    row,
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )

    except urllib.error.HTTPError as exc:

        http_status = exc.code

        failure_stage = "HTTP_AUTHENTICATED_READ"

        exception_class = (
            exc.__class__.__name__
        )

        exception_message = str(exc)

        try:

            raw_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:

            raw_body = None

        response_bytes = (
            len(raw_body.encode("utf-8"))
            if raw_body is not None
            else 0
        )

        log(
            f"REQUEST_ATTEMPTED="
            f"{request_attempted}"
        )

        log(
            "HTTP_READ_OK=False"
        )

        log(
            f"HTTP_STATUS="
            f"{http_status}"
        )

        section(
            f"{VERSION}: HTTP ERROR BODY"
        )

        log(
            "RAW_BODY_PREVIEW="
            + (
                raw_body[:2000]
                if raw_body
                else ""
            )
        )

    except urllib.error.URLError as exc:

        failure_stage = "NETWORK_READ"

        exception_class = (
            exc.__class__.__name__
        )

        exception_message = str(exc)

        log(
            f"REQUEST_ATTEMPTED="
            f"{request_attempted}"
        )

        log(
            "HTTP_READ_OK=False"
        )

        log(
            "HTTP_STATUS=UNKNOWN"
        )

    except Exception as exc:

        if failure_stage is None:
            failure_stage = "POSITION_RESPONSE_PROCESSING"

        if exception_class is None:
            exception_class = (
                exc.__class__.__name__
            )

        if exception_message is None:
            exception_message = str(exc)

    # ----------------------------------------------------------------------------------------------
    # ERROR DIAGNOSTIC
    # ----------------------------------------------------------------------------------------------

    section(
        f"{VERSION}: ERROR DIAGNOSTIC"
    )

    log(
        f"FAILURE_STAGE="
        f"{failure_stage}"
    )

    log(
        f"EXCEPTION_CLASS="
        f"{exception_class}"
    )

    log(
        f"EXCEPTION_MESSAGE="
        f"{exception_message}"
    )

    # ----------------------------------------------------------------------------------------------
    # SAFETY
    # ----------------------------------------------------------------------------------------------

    safety_ok = safety_invariants_ok()

    section(
        f"{VERSION}: SAFETY"
    )

    log(
        f"PUBLIC_MARKET_GETS="
        f"{PUBLIC_MARKET_GETS}"
    )

    log(
        f"AUTHENTICATED_WEEX_READS="
        f"{AUTHENTICATED_WEEX_READS}"
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

    # ----------------------------------------------------------------------------------------------
    # FINAL TEST STATUS
    # ----------------------------------------------------------------------------------------------
    #
    # PASS requires:
    #
    #   - DNS works
    #   - HTTP authenticated read succeeds
    #   - JSON parses
    #   - response structure can be understood
    #   - BTCUSDT position state can be calculated
    #   - account is flat
    #   - all exchange-write counters remain zero
    #
    # IMPORTANT:
    #
    #   If the authenticated read succeeds but BTCUSDT is genuinely non-flat,
    #   status becomes POSITION_PRESENT rather than pretending the read failed.
    #
    # ----------------------------------------------------------------------------------------------

    if (
        dns_ok
        and http_read_ok
        and json_parse_ok
        and position_response_parsed
        and AUTHENTICATED_POSITION_READ_OK
        and BTCUSDT_FLAT is True
        and safety_ok
    ):

        TEST_STATUS = "PASS"

    elif (
        dns_ok
        and http_read_ok
        and json_parse_ok
        and position_response_parsed
        and AUTHENTICATED_POSITION_READ_OK
        and BTCUSDT_FLAT is False
        and safety_ok
    ):

        TEST_STATUS = "POSITION_PRESENT"

    else:

        TEST_STATUS = "FAIL"

    # ----------------------------------------------------------------------------------------------
    # RESULT
    # ----------------------------------------------------------------------------------------------

    section(
        f"{VERSION} RESULT"
    )

    log(
        "TEST="
        "RAW_AUTHENTICATED_BTCUSDT_POSITION_READ"
    )

    log(
        f"DNS_OK="
        f"{dns_ok}"
    )

    log(
        f"REQUEST_ATTEMPTED="
        f"{request_attempted}"
    )

    log(
        f"HTTP_READ_OK="
        f"{http_read_ok}"
    )

    log(
        f"HTTP_STATUS="
        f"{value_text(http_status)}"
    )

    log(
        f"JSON_PARSE_OK="
        f"{json_parse_ok}"
    )

    log(
        f"POSITION_RESPONSE_PARSED="
        f"{position_response_parsed}"
    )

    log(
        f"POSITION_RESPONSE_SHAPE="
        f"{value_text(response_shape)}"
    )

    log(
        f"AUTHENTICATED_POSITION_READ_OK="
        f"{AUTHENTICATED_POSITION_READ_OK}"
    )

    log(
        f"BTCUSDT_POSITION_ROWS="
        f"{value_text(BTCUSDT_POSITION_ROWS)}"
    )

    log(
        f"BTCUSDT_OPEN_POSITION_COUNT="
        f"{value_text(BTCUSDT_OPEN_POSITION_COUNT)}"
    )

    log(
        f"BTCUSDT_FLAT="
        f"{bool_text(BTCUSDT_FLAT)}"
    )

    log(
        f"AUTHENTICATED_WEEX_READS="
        f"{AUTHENTICATED_WEEX_READS}"
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

    log(
        f"STATUS="
        f"{TEST_STATUS}"
    )

    if TEST_STATUS == "PASS":

        log(
            "NEXT_UNIT="
            "R35P-C_RAW_SYMBOL_CONFIG_MARGIN_MODE_READ"
        )

    elif TEST_STATUS == "POSITION_PRESENT":

        log(
            "NEXT_ACTION="
            "STOP_AND_INSPECT_REAL_BTCUSDT_POSITION"
        )

    else:

        log(
            "NEXT_ACTION="
            "DIAGNOSE_R35P-B_FAILURE_ONLY"
        )

    log(SEPARATOR)


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================


def heartbeat_loop() -> None:

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"AUTH_POSITION_READ_OK="
            f"{AUTHENTICATED_POSITION_READ_OK} "
            f"BTCUSDT_FLAT="
            f"{bool_text(BTCUSDT_FLAT)} "
            f"OPEN_POSITIONS="
            f"{value_text(BTCUSDT_OPEN_POSITION_COUNT)} "
            f"TEST_STATUS="
            f"{TEST_STATUS} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(30)


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    # Give the health-server log a moment to appear first,
    # matching the diagnostic sequence used in R35P-A.
    time.sleep(0.2)

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(
        f"{VERSION}: SYMBOL="
        f"{SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION="
        f"{VERSION}"
    )

    log(
        f"{VERSION}: HEALTH PORT="
        f"{HEALTH_PORT}"
    )

    log(
        f"{VERSION}: TEST SCOPE="
        f"AUTHENTICATED BTCUSDT POSITION READ ONLY"
    )

    log(
        f"{VERSION}: WEEX CONTRACT BASE="
        f"{WEEX_CONTRACT_BASE}"
    )

    log(
        f"{VERSION}: POSITION PATH="
        f"{POSITION_PATH}"
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

    section(
        f"{VERSION}: BEGIN SINGLE TEST"
    )

    run_single_test()

    heartbeat_loop()


if __name__ == "__main__":
    main()

