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
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode


# ==================================================================================================
# R35P-C - RAW SYMBOL CONFIG / MARGIN MODE / LEVERAGE READ
# ==================================================================================================
#
# PURPOSE
#   Test exactly one thing:
#       Can this deployment perform an authenticated READ-ONLY WEEX V3 symbolConfig request for
#       BTCUSDT and correctly extract:
#           - marginType
#           - isolatedLongLeverage
#           - isolatedShortLeverage
#
# SAFETY
#   - GET only
#   - no POST / PUT / PATCH / DELETE
#   - no order submission
#   - no leverage mutation
#   - no margin-mode mutation
#   - no position mutation
#   - real order execution hard disabled
#   - first real order hard forbidden
#
# IMPORTANT
#   This unit deliberately does NOT:
#       - read positions
#       - read market price
#       - test Telegram
#       - make an activation decision
#       - change margin mode
#       - change leverage
#       - submit any order
# ==================================================================================================


VERSION = "R35P-C"
SYMBOL = "BTCUSDT"
HEALTH_PORT = int(os.getenv("PORT", "10000"))

WEEX_CONTRACT_BASE = "https://api-contract.weex.com"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

TARGET_MARGIN_MODE = "ISOLATED"
TARGET_LONG_LEVERAGE = "100"
TARGET_SHORT_LEVERAGE = "100"

REAL_ORDER_EXECUTION = False
FIRST_REAL_ORDER_ALLOWED = False

PUBLIC_MARKET_GETS = 0
AUTHENTICATED_WEEX_READS = 0
EXCHANGE_NETWORK_WRITES = 0
ORDER_SUBMISSIONS = 0
LEVERAGE_MUTATIONS = 0
MARGIN_MODE_MUTATIONS = 0
POSITION_MUTATIONS = 0

HEARTBEAT_SECONDS = 30


def utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def log(message: str = "") -> None:
    print(f"{utc_now()} {message}", flush=True)


def line() -> None:
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
                "exchange_network_writes": EXCHANGE_NETWORK_WRITES,
            }
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
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log(f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}")


# ==================================================================================================
# STRICT READ-ONLY WEEX AUTHENTICATION
# ==================================================================================================


def generate_signature(
    secret: str,
    timestamp_ms: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:
    method = method.upper()

    if query_string:
        prehash = f"{timestamp_ms}{method}{request_path}?{query_string}{body}"
    else:
        prehash = f"{timestamp_ms}{method}{request_path}{body}"

    digest = hmac.new(
        secret.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def authenticated_get(
    request_path: str,
    params: Dict[str, str],
    api_key: str,
    api_secret: str,
    api_passphrase: str,
    timeout_seconds: int = 15,
) -> Tuple[int, str, str]:
    global AUTHENTICATED_WEEX_READS

    method = "GET"

    if method != "GET":
        raise RuntimeError("R35P-C SAFETY VIOLATION: only GET is permitted")

    query_string = urlencode(params)
    timestamp_ms = str(int(time.time() * 1000))

    signature = generate_signature(
        secret=api_secret,
        timestamp_ms=timestamp_ms,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    url = f"{WEEX_CONTRACT_BASE}{request_path}?{query_string}"

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp_ms,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "locale": "en-US",
        "User-Agent": f"{VERSION}/1.0",
    }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    AUTHENTICATED_WEEX_READS += 1

    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        status = int(response.status)
        content_type = response.headers.get("Content-Type", "")
        body = response.read().decode("utf-8", errors="replace")
        return status, content_type, body


# ==================================================================================================
# RESPONSE PARSING
# ==================================================================================================


def normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def row_symbol_present(row: Dict[str, Any]) -> bool:
    return bool(str(row.get("symbol", "")).strip())


def find_btcusdt_config(
    payload: Any,
) -> Tuple[Optional[Dict[str, Any]], str, int]:

    if isinstance(payload, list):
        rows: List[Dict[str, Any]] = [
            row for row in payload if isinstance(row, dict)
        ]

        for row in rows:
            if normalize_symbol(row.get("symbol")) == SYMBOL:
                return row, "list", len(rows)

        if len(rows) == 1 and not row_symbol_present(rows[0]):
            return rows[0], "list", len(rows)

        return None, "list", len(rows)

    if isinstance(payload, dict):
        if normalize_symbol(payload.get("symbol")) == SYMBOL:
            return payload, "dict", 1

        data = payload.get("data")

        if isinstance(data, list):
            rows = [
                row for row in data
                if isinstance(row, dict)
            ]

            for row in rows:
                if normalize_symbol(row.get("symbol")) == SYMBOL:
                    return row, "dict.data.list", len(rows)

            return None, "dict.data.list", len(rows)

        if isinstance(data, dict):
            if normalize_symbol(data.get("symbol")) in ("", SYMBOL):
                return data, "dict.data.dict", 1

        if any(
            key in payload
            for key in (
                "marginType",
                "isolatedLongLeverage",
                "isolatedShortLeverage",
            )
        ):
            return payload, "dict", 1

        return None, "dict", 0

    return None, type(payload).__name__, 0


def clean_value(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()

    if text == "":
        return None

    if text.endswith(".0"):
        try:
            as_float = float(text)

            if as_float.is_integer():
                return str(int(as_float))

        except ValueError:
            pass

    return text


# ==================================================================================================
# SINGLE TEST
# ==================================================================================================


def run_test() -> Dict[str, Any]:
    api_key = os.getenv("WEEX_API_KEY", "").strip()
    api_secret = os.getenv("WEEX_API_SECRET", "").strip()
    api_passphrase = os.getenv(
        "WEEX_API_PASSPHRASE",
        "",
    ).strip()

    all_credentials_present = bool(
        api_key
        and api_secret
        and api_passphrase
    )

    request_attempted = False
    http_read_ok = False
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    response_bytes = 0
    raw_body = ""

    json_parse_ok = False
    parsed_payload: Any = None
    response_type = "UNKNOWN"

    symbol_config_response_parsed = False
    symbol_config_response_shape = "UNKNOWN"
    total_config_rows = 0
    btc_config: Optional[Dict[str, Any]] = None

    observed_symbol: Optional[str] = None
    margin_mode: Optional[str] = None
    separated_type: Optional[str] = None
    cross_leverage: Optional[str] = None
    long_leverage: Optional[str] = None
    short_leverage: Optional[str] = None

    margin_mode_match = False
    long_leverage_match = False
    short_leverage_match = False

    dns_ok = False
    dns_ip: Optional[str] = None
    dns_error: Optional[str] = None

    failure_stage: Optional[str] = None
    exception_class: Optional[str] = None
    exception_message: Optional[str] = None

    line()
    log(f"{VERSION}: RAW SYMBOL CONFIG DIAGNOSTIC")
    line()

    log("TEST=RAW_AUTHENTICATED_BTCUSDT_SYMBOL_CONFIG_READ")
    log(f"SYMBOL={SYMBOL}")
    log(
        "ENDPOINT="
        f"{WEEX_CONTRACT_BASE}"
        f"{SYMBOL_CONFIG_PATH}"
        f"?symbol={SYMBOL}"
    )
    log("METHOD=GET")
    log("AUTHENTICATION=WEEX_V3_USER_DATA")

    # ==============================================================================================
    # CREDENTIAL PRESENCE
    # ==============================================================================================

    line()
    log(f"{VERSION}: CREDENTIAL PRESENCE")
    line()

    log(f"WEEX_API_KEY_PRESENT={bool(api_key)}")
    log(f"WEEX_API_SECRET_PRESENT={bool(api_secret)}")
    log(
        "WEEX_API_PASSPHRASE_PRESENT="
        f"{bool(api_passphrase)}"
    )
    log(
        "ALL_REQUIRED_CREDENTIALS_PRESENT="
        f"{all_credentials_present}"
    )

    # ==============================================================================================
    # DNS
    # ==============================================================================================

    line()
    log(f"{VERSION}: DNS")
    line()

    try:
        dns_ip = socket.gethostbyname(
            "api-contract.weex.com"
        )
        dns_ok = True

    except Exception as exc:
        dns_ok = False
        dns_error = str(exc)

        failure_stage = "DNS"
        exception_class = exc.__class__.__name__
        exception_message = str(exc)

    log(f"DNS_OK={dns_ok}")
    log(f"DNS_IP={dns_ip}")
    log(f"DNS_ERROR={dns_error}")

    # ==============================================================================================
    # AUTHENTICATED GET
    # ==============================================================================================

    line()
    log(f"{VERSION}: AUTHENTICATED HTTP GET")
    line()

    if not all_credentials_present:
        failure_stage = failure_stage or "CREDENTIALS"
        exception_class = (
            exception_class
            or "MissingCredentials"
        )
        exception_message = (
            exception_message
            or (
                "WEEX_API_KEY, WEEX_API_SECRET and "
                "WEEX_API_PASSPHRASE are required"
            )
        )

    elif not dns_ok:
        pass

    else:
        try:
            request_attempted = True

            (
                http_status,
                content_type,
                raw_body,
            ) = authenticated_get(
                request_path=SYMBOL_CONFIG_PATH,
                params={"symbol": SYMBOL},
                api_key=api_key,
                api_secret=api_secret,
                api_passphrase=api_passphrase,
            )

            response_bytes = len(
                raw_body.encode("utf-8")
            )

            http_read_ok = (
                http_status == 200
            )

            if not http_read_ok:
                failure_stage = "HTTP_STATUS"

        except urllib.error.HTTPError as exc:
            request_attempted = True

            http_status = int(exc.code)

            content_type = (
                exc.headers.get(
                    "Content-Type",
                    "",
                )
                if exc.headers
                else ""
            )

            raw_body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

            response_bytes = len(
                raw_body.encode("utf-8")
            )

            failure_stage = "HTTP_ERROR"
            exception_class = (
                exc.__class__.__name__
            )
            exception_message = str(exc)

        except Exception as exc:
            request_attempted = True
            failure_stage = "HTTP_REQUEST"
            exception_class = (
                exc.__class__.__name__
            )
            exception_message = str(exc)

    log(f"REQUEST_ATTEMPTED={request_attempted}")
    log(f"HTTP_READ_OK={http_read_ok}")
    log(f"HTTP_STATUS={http_status}")
    log(f"CONTENT_TYPE={content_type}")
    log(f"RESPONSE_BYTES={response_bytes}")

    # ==============================================================================================
    # RAW RESPONSE
    # ==============================================================================================

    line()
    log(f"{VERSION}: RAW RESPONSE")
    line()

    raw_preview = (
        raw_body[:4000]
        if raw_body
        else ""
    )

    log(
        f"RAW_BODY_PREVIEW={raw_preview}"
    )

    # ==============================================================================================
    # JSON
    # ==============================================================================================

    line()
    log(f"{VERSION}: RESPONSE SHAPE")
    line()

    if raw_body:
        try:
            parsed_payload = json.loads(
                raw_body
            )

            json_parse_ok = True
            response_type = (
                type(parsed_payload).__name__
            )

        except Exception as exc:
            if failure_stage is None:
                failure_stage = "JSON_PARSE"
                exception_class = (
                    exc.__class__.__name__
                )
                exception_message = str(exc)

    elif http_read_ok:
        failure_stage = (
            failure_stage
            or "EMPTY_RESPONSE"
        )

    log(f"JSON_PARSE_OK={json_parse_ok}")
    log(f"RESPONSE_TYPE={response_type}")

    if isinstance(parsed_payload, dict):
        keys = ",".join(
            sorted(
                str(k)
                for k
                in parsed_payload.keys()
            )
        )

        log(f"RESPONSE_KEYS={keys}")

    else:
        log("RESPONSE_KEYS=N/A")

    # ==============================================================================================
    # SYMBOL CONFIG STRUCTURE
    # ==============================================================================================

    line()
    log(f"{VERSION}: SYMBOL CONFIG STRUCTURE")
    line()

    if json_parse_ok:
        (
            btc_config,
            symbol_config_response_shape,
            total_config_rows,
        ) = find_btcusdt_config(
            parsed_payload
        )

        symbol_config_response_parsed = (
            isinstance(
                parsed_payload,
                (list, dict),
            )
        )

    log(
        "SYMBOL_CONFIG_RESPONSE_PARSED="
        f"{symbol_config_response_parsed}"
    )

    log(
        "SYMBOL_CONFIG_RESPONSE_SHAPE="
        f"{symbol_config_response_shape}"
    )

    log(
        "TOTAL_RESPONSE_CONFIG_ROWS="
        f"{total_config_rows}"
    )

    log(
        "BTCUSDT_CONFIG_FOUND="
        f"{btc_config is not None}"
    )

    # ==============================================================================================
    # FIELD EXTRACTION
    # ==============================================================================================

    line()
    log(f"{VERSION}: BTCUSDT CONFIG EXTRACTION")
    line()

    if btc_config is not None:
        observed_symbol = clean_value(
            btc_config.get("symbol")
        )

        margin_mode = clean_value(
            btc_config.get("marginType")
        )

        separated_type = clean_value(
            btc_config.get("separatedType")
        )

        cross_leverage = clean_value(
            btc_config.get("crossLeverage")
        )

        long_leverage = clean_value(
            btc_config.get(
                "isolatedLongLeverage"
            )
        )

        short_leverage = clean_value(
            btc_config.get(
                "isolatedShortLeverage"
            )
        )

        if margin_mode is not None:
            margin_mode = (
                margin_mode.upper()
            )

        margin_mode_match = (
            margin_mode
            == TARGET_MARGIN_MODE
        )

        long_leverage_match = (
            long_leverage
            == TARGET_LONG_LEVERAGE
        )

        short_leverage_match = (
            short_leverage
            == TARGET_SHORT_LEVERAGE
        )

    log(
        f"OBSERVED_SYMBOL={observed_symbol}"
    )

    log(
        f"MARGIN_MODE={margin_mode}"
    )

    log(
        f"SEPARATED_TYPE={separated_type}"
    )

    log(
        f"CROSS_LEVERAGE={cross_leverage}"
    )

    log(
        f"LONG_LEVERAGE={long_leverage}"
    )

    log(
        f"SHORT_LEVERAGE={short_leverage}"
    )

    log(
        f"TARGET_MARGIN_MODE="
        f"{TARGET_MARGIN_MODE}"
    )

    log(
        f"TARGET_LONG_LEVERAGE="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"TARGET_SHORT_LEVERAGE="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{margin_mode_match}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{long_leverage_match}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{short_leverage_match}"
    )

    config_read_ok = (
        http_read_ok
        and json_parse_ok
        and symbol_config_response_parsed
        and btc_config is not None
        and margin_mode is not None
        and long_leverage is not None
        and short_leverage is not None
    )

    # ==============================================================================================
    # ERROR DIAGNOSTIC
    # ==============================================================================================

    line()
    log(f"{VERSION}: ERROR DIAGNOSTIC")
    line()

    if (
        not config_read_ok
        and failure_stage is None
    ):
        failure_stage = (
            "SYMBOL_CONFIG_EXTRACTION"
        )

        exception_class = (
            "ConfigExtractionFailure"
        )

        exception_message = (
            "HTTP/JSON read succeeded but "
            "BTCUSDT margin/leverage fields "
            "were not fully extracted"
        )

    log(
        f"FAILURE_STAGE={failure_stage}"
    )

    log(
        f"EXCEPTION_CLASS={exception_class}"
    )

    log(
        "EXCEPTION_MESSAGE="
        f"{exception_message}"
    )

    # ==============================================================================================
    # SAFETY
    # ==============================================================================================

    line()
    log(f"{VERSION}: SAFETY")
    line()

    safety_invariants_ok = (
        PUBLIC_MARKET_GETS == 0
        and EXCHANGE_NETWORK_WRITES == 0
        and ORDER_SUBMISSIONS == 0
        and LEVERAGE_MUTATIONS == 0
        and MARGIN_MODE_MUTATIONS == 0
        and POSITION_MUTATIONS == 0
        and REAL_ORDER_EXECUTION is False
        and FIRST_REAL_ORDER_ALLOWED is False
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
        f"{safety_invariants_ok}"
    )

    status = (
        "PASS"
        if config_read_ok
        and safety_invariants_ok
        else "FAIL"
    )

    # ==============================================================================================
    # RESULT
    # ==============================================================================================

    line()
    log(f"{VERSION} RESULT")
    line()

    log(
        "TEST="
        "RAW_AUTHENTICATED_BTCUSDT_"
        "SYMBOL_CONFIG_READ"
    )

    log(f"DNS_OK={dns_ok}")

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
        f"JSON_PARSE_OK="
        f"{json_parse_ok}"
    )

    log(
        "SYMBOL_CONFIG_RESPONSE_PARSED="
        f"{symbol_config_response_parsed}"
    )

    log(
        "SYMBOL_CONFIG_RESPONSE_SHAPE="
        f"{symbol_config_response_shape}"
    )

    log(
        "AUTHENTICATED_SYMBOL_CONFIG_READ_OK="
        f"{config_read_ok}"
    )

    log(
        f"MARGIN_MODE="
        f"{margin_mode}"
    )

    log(
        f"LONG_LEVERAGE="
        f"{long_leverage}"
    )

    log(
        f"SHORT_LEVERAGE="
        f"{short_leverage}"
    )

    log(
        f"MARGIN_MODE_MATCH="
        f"{margin_mode_match}"
    )

    log(
        f"LONG_LEVERAGE_MATCH="
        f"{long_leverage_match}"
    )

    log(
        f"SHORT_LEVERAGE_MATCH="
        f"{short_leverage_match}"
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

    log(f"STATUS={status}")

    if status == "PASS":
        log(
            "NEXT_UNIT="
            "R35P-D_RAW_PUBLIC_MARK_PRICE_READ"
        )
    else:
        log(
            "NEXT_UNIT="
            "STOP_AND_DIAGNOSE_R35P-C"
        )

    line()

    return {
        "status": status,
        "config_read_ok": config_read_ok,
        "margin_mode": margin_mode,
        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
        "margin_mode_match": margin_mode_match,
        "long_leverage_match": long_leverage_match,
        "short_leverage_match": short_leverage_match,
        "safety_invariants_ok": safety_invariants_ok,
    }


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:
    start_health_server()

    time.sleep(0.2)

    line()
    log(f"{VERSION}: MAIN.PY ENTERED")
    line()

    log(f"{VERSION}: SYMBOL={SYMBOL}")
    log(f"{VERSION}: VERSION={VERSION}")
    log(
        f"{VERSION}: HEALTH PORT="
        f"{HEALTH_PORT}"
    )

    log(
        f"{VERSION}: TEST SCOPE="
        "AUTHENTICATED BTCUSDT "
        "SYMBOL CONFIG READ ONLY"
    )

    log(
        f"{VERSION}: WEEX CONTRACT BASE="
        f"{WEEX_CONTRACT_BASE}"
    )

    log(
        f"{VERSION}: SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}"
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

    line()
    log(f"{VERSION}: BEGIN SINGLE TEST")
    line()

    result = run_test()

    heartbeat = 0

    while True:
        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT={heartbeat} "
            f"AUTH_SYMBOL_CONFIG_READ_OK="
            f"{result['config_read_ok']} "
            f"MARGIN_MODE="
            f"{result['margin_mode']} "
            f"LONG_LEVERAGE="
            f"{result['long_leverage']} "
            f"SHORT_LEVERAGE="
            f"{result['short_leverage']} "
            f"TEST_STATUS="
            f"{result['status']} "
            f"EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


if __name__ == "__main__":
    main()
