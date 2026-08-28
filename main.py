# =====================================================================================
# R34M main.py
#
# WEEX AUTHENTICATED READ-ONLY LIVE ACCOUNT RECONCILIATION
#
# PURPOSE
# -------
# 1. Validate required environment variables.
# 2. Validate the official WEEX Contract REST hostname.
# 3. Perform authenticated READ-ONLY GET requests.
# 4. Read live USDT available balance.
# 5. Read live BTCUSDT positions.
# 6. Read live BTCUSDT symbol configuration.
# 7. Confirm isolated leverage configuration.
# 8. Preserve hard safety locks:
#
#       NETWORK WRITES            = 0
#       REAL ORDERS               = 0
#       DEMO ORDERS               = 0
#       LEVERAGE MUTATIONS        = 0
#       MARGIN MUTATIONS          = 0
#       POSITION MUTATIONS        = 0
#       ACCOUNT MUTATIONS         = 0
#
# IMPORTANT
# ---------
# THIS FILE DOES NOT SEND POST/PUT/PATCH/DELETE REQUESTS.
# THIS FILE DOES NOT PLACE ORDERS.
# THIS FILE DOES NOT CHANGE LEVERAGE.
#
# VERSION: R34M
# =====================================================================================


# =====================================================================================
# PART 1 — IMPORTS
# =====================================================================================

import base64
import hashlib
import hmac
import json
import os
import socket
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional, Tuple


# =====================================================================================
# PART 2 — CONSTANTS
# =====================================================================================

VERSION = "R34M"

SYMBOL = os.environ.get(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

PORT = int(
    os.environ.get(
        "PORT",
        "10000",
    )
)


# -------------------------------------------------------------------------------------
# OFFICIAL WEEX CONTRACT REST DOMAIN
# -------------------------------------------------------------------------------------

WEEX_BASE_URL = "https://api-contract.weex.com"

EXPECTED_WEEX_HOST = "api-contract.weex.com"


# -------------------------------------------------------------------------------------
# WEEX V3 READ-ONLY ENDPOINTS
# -------------------------------------------------------------------------------------

BALANCE_PATH = "/capi/v3/account/balance"

POSITION_PATH = "/capi/v3/account/position/allPosition"

SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"


# -------------------------------------------------------------------------------------
# TARGET STRATEGY CONFIGURATION
# -------------------------------------------------------------------------------------

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100

TARGET_SHORT_LEVERAGE = 100


# -------------------------------------------------------------------------------------
# HARD SAFETY CONFIGURATION
# -------------------------------------------------------------------------------------

AUTHENTICATED_READ_ONLY_ENABLED = True

PUBLIC_READ_ONLY_ENABLED = True

REAL_ORDER_EXECUTION_ENABLED = False

DEMO_ORDER_EXECUTION_ENABLED = False

NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

ACCOUNT_MUTATION_ENABLED = False


# -------------------------------------------------------------------------------------
# HTTP CONFIGURATION
# -------------------------------------------------------------------------------------

HTTP_TIMEOUT_SECONDS = 15

DNS_RETRY_COUNT = 3

DNS_RETRY_DELAY_SECONDS = 2

USER_AGENT = "R34M-WEEX-ReadOnly/1.0"


# -------------------------------------------------------------------------------------
# HEARTBEAT
# -------------------------------------------------------------------------------------

HEARTBEAT_INTERVAL_SECONDS = 30


# =====================================================================================
# PART 3 — ENVIRONMENT VARIABLES
# =====================================================================================


def first_nonempty_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)

        if value is not None:
            value = value.strip()

            if value:
                return value

    return ""


WEEX_API_KEY = first_nonempty_env(
    "WEEX_API_KEY",
    "WEEX_KEY",
    "API_KEY",
)

WEEX_API_SECRET = first_nonempty_env(
    "WEEX_API_SECRET",
    "WEEX_SECRET_KEY",
    "WEEX_SECRET",
    "API_SECRET",
)

WEEX_API_PASSPHRASE = first_nonempty_env(
    "WEEX_API_PASSPHRASE",
    "WEEX_PASSPHRASE",
    "API_PASSPHRASE",
)


# =====================================================================================
# PART 4 — GLOBAL STATE
# =====================================================================================

STATE_LOCK = threading.Lock()

STATE: Dict[str, Any] = {
    "version": VERSION,

    "symbol": SYMBOL,

    "phase": "STARTING",

    "validation_complete": False,

    "validation_passed": False,

    "available_usdt": None,

    "position_count": None,

    "symbol_config_found": False,

    "observed_margin_type": None,

    "observed_position_mode": None,

    "observed_cross_leverage": None,

    "observed_long_leverage": None,

    "observed_short_leverage": None,

    "correction_required": None,

    "authenticated_get_count": 0,

    "public_get_count": 0,

    "network_writes": 0,

    "real_orders": 0,

    "demo_orders": 0,

    "leverage_mutations": 0,

    "margin_mutations": 0,

    "position_mutations": 0,

    "account_mutations": 0,

    "heartbeat": 0,

    "last_error": None,
}


# =====================================================================================
# PART 5 — OUTPUT HELPERS
# =====================================================================================

LINE = "-" * 100


def banner(text: str) -> None:
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def log(text: str) -> None:
    print(
        f"{VERSION}: {text}",
        flush=True,
    )


def pass_line(name: str) -> None:
    print(
        f"{name:<84} ✅ PASS",
        flush=True,
    )


def fail_line(name: str) -> None:
    print(
        f"{name:<84} ❌ FAIL",
        flush=True,
    )


def check(
    name: str,
    condition: bool,
) -> None:

    if condition:
        pass_line(name)
        return

    fail_line(name)

    raise RuntimeError(
        f"Validation check failed: {name}"
    )


# =====================================================================================
# PART 6 — SAFE STATE HELPERS
# =====================================================================================


def set_state(
    key: str,
    value: Any,
) -> None:

    with STATE_LOCK:
        STATE[key] = value


def increment_state(
    key: str,
    amount: int = 1,
) -> None:

    with STATE_LOCK:
        STATE[key] = int(
            STATE.get(
                key,
                0,
            )
        ) + amount


def snapshot_state() -> Dict[str, Any]:
    with STATE_LOCK:
        return dict(STATE)


# =====================================================================================
# PART 7 — HEALTH SERVER
# =====================================================================================


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:

        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):
            self.send_response(404)

            self.end_headers()

            return

        snapshot = snapshot_state()

        body = json.dumps(
            snapshot,
            sort_keys=True,
            default=str,
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


    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    def worker() -> None:

        try:

            server = HTTPServer(
                (
                    "0.0.0.0",
                    PORT,
                ),
                HealthHandler,
            )

            log(
                f"HEALTH SERVER LISTENING ON PORT {PORT}"
            )

            server.serve_forever()

        except Exception as exc:

            log(
                "HEALTH SERVER ERROR="
                f"{type(exc).__name__}: {exc}"
            )


    thread = threading.Thread(
        target=worker,
        name="r34m-health-server",
        daemon=True,
    )

    thread.start()


# =====================================================================================
# PART 8 — HEARTBEAT
# =====================================================================================


def heartbeat_worker() -> None:

    while True:

        time.sleep(
            HEARTBEAT_INTERVAL_SECONDS
        )

        increment_state(
            "heartbeat"
        )

        snapshot = snapshot_state()

        log(
            "HEARTBEAT "
            f"{snapshot['heartbeat']} | "
            f"phase={snapshot['phase']} | "
            f"authenticated-read-only="
            f"{AUTHENTICATED_READ_ONLY_ENABLED} | "
            f"authenticated-get="
            f"{snapshot['authenticated_get_count']} | "
            f"network-writes="
            f"{snapshot['network_writes']} | "
            f"leverage-mutations="
            f"{snapshot['leverage_mutations']} | "
            f"real-orders="
            f"{snapshot['real_orders']} | "
            f"demo-orders="
            f"{snapshot['demo_orders']} | "
            f"correction-required="
            f"{snapshot['correction_required']} | "
            f"observed-margin="
            f"{snapshot['observed_margin_type']} | "
            f"observed-long="
            f"{snapshot['observed_long_leverage']} | "
            f"observed-short="
            f"{snapshot['observed_short_leverage']} | "
            f"target-long="
            f"{TARGET_LONG_LEVERAGE}x | "
            f"target-short="
            f"{TARGET_SHORT_LEVERAGE}x"
        )


def start_heartbeat() -> None:

    thread = threading.Thread(
        target=heartbeat_worker,
        name="r34m-heartbeat",
        daemon=True,
    )

    thread.start()


# =====================================================================================
# PART 9 — CREDENTIAL VALIDATION
# =====================================================================================


def validate_credentials() -> None:

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

    if missing:

        raise RuntimeError(
            "Missing credentials: "
            + ", ".join(missing)
        )


# =====================================================================================
# PART 10 — HOST VALIDATION
# =====================================================================================


def validate_base_url() -> None:

    parsed = urllib.parse.urlparse(
        WEEX_BASE_URL
    )

    check(
        "WEEX Base URL Is Official Contract REST Host",
        WEEX_BASE_URL
        == "https://api-contract.weex.com",
    )

    check(
        "WEEX API Scheme Is HTTPS",
        parsed.scheme == "https",
    )

    check(
        "WEEX API Hostname Is Exact",
        parsed.hostname
        == EXPECTED_WEEX_HOST,
    )

    check(
        "WEEX API Base URL Contains No Query",
        parsed.query == "",
    )

    check(
        "WEEX API Base URL Contains No Fragment",
        parsed.fragment == "",
    )

    check(
        "WEEX API Base URL Contains No Unexpected Path",
        parsed.path in (
            "",
            "/",
        ),
    )

    log(
        f"WEEX BASE URL={WEEX_BASE_URL}"
    )

    log(
        f"WEEX HOST={parsed.hostname}"
    )


# =====================================================================================
# PART 11 — DNS TEST
# =====================================================================================


def resolve_weex_host() -> List[str]:

    last_error: Optional[Exception] = None

    for attempt in range(
        1,
        DNS_RETRY_COUNT + 1,
    ):

        try:

            records = socket.getaddrinfo(
                EXPECTED_WEEX_HOST,
                443,
                type=socket.SOCK_STREAM,
            )

            addresses = []

            for record in records:

                sockaddr = record[4]

                if not sockaddr:
                    continue

                address = sockaddr[0]

                if (
                    address
                    and
                    address not in addresses
                ):
                    addresses.append(
                        address
                    )

            if not addresses:

                raise RuntimeError(
                    "DNS returned no addresses"
                )

            return addresses

        except Exception as exc:

            last_error = exc

            log(
                "DNS RESOLUTION ATTEMPT "
                f"{attempt}/{DNS_RETRY_COUNT} "
                f"FAILED: "
                f"{type(exc).__name__}: {exc}"
            )

            if attempt < DNS_RETRY_COUNT:

                time.sleep(
                    DNS_RETRY_DELAY_SECONDS
                )

    raise RuntimeError(
        "Unable to resolve WEEX hostname "
        f"{EXPECTED_WEEX_HOST}: "
        f"{last_error}"
    )


# =====================================================================================
# PART 12 — SIGNATURE
# =====================================================================================


def make_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    if query_string:

        message = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        message = (
            timestamp
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    signature = base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )

    return signature


# =====================================================================================
# PART 13 — QUERY HELPERS
# =====================================================================================


def encode_query(
    parameters: Optional[
        Dict[str, Any]
    ] = None,
) -> str:

    if not parameters:
        return ""

    cleaned = {}

    for key, value in parameters.items():

        if value is None:
            continue

        cleaned[str(key)] = str(value)

    return urllib.parse.urlencode(
        cleaned
    )


# =====================================================================================
# PART 14 — AUTHENTICATED READ-ONLY GET
# =====================================================================================


AUTHENTICATED_GET_ALLOWLIST = {
    BALANCE_PATH,
    POSITION_PATH,
    SYMBOL_CONFIG_PATH,
}


def authenticated_get(
    path: str,
    parameters: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not AUTHENTICATED_READ_ONLY_ENABLED:

        raise RuntimeError(
            "Authenticated read-only access "
            "is disabled"
        )

    if not path.startswith("/"):

        raise RuntimeError(
            "Authenticated GET path must "
            f"start with '/': {path}"
        )

    if path not in AUTHENTICATED_GET_ALLOWLIST:

        raise RuntimeError(
            "Authenticated GET path is "
            f"not allowlisted: {path}"
        )

    # -------------------------------------------------------------------------
    # GET ONLY
    # -------------------------------------------------------------------------

    method = "GET"

    query_string = encode_query(
        parameters
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = make_signature(
        timestamp=timestamp,
        method=method,
        request_path=path,
        query_string=query_string,
        body="",
    )

    if query_string:

        url = (
            WEEX_BASE_URL
            + path
            + "?"
            + query_string
        )

    else:

        url = (
            WEEX_BASE_URL
            + path
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
            "application/json",

        "Accept":
            "application/json",

        "User-Agent":
            USER_AGENT,
    }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            status = getattr(
                response,
                "status",
                200,
            )

            raw = response.read().decode(
                "utf-8"
            )

        if status < 200 or status >= 300:

            raise RuntimeError(
                f"Unexpected HTTP status "
                f"{status}"
            )

        try:

            payload = json.loads(
                raw
            )

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                "WEEX returned invalid JSON: "
                + raw[:500]
            ) from exc

        increment_state(
            "authenticated_get_count"
        )

        return payload

    except urllib.error.HTTPError as exc:

        try:

            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:

            error_body = ""

        raise RuntimeError(
            "Authenticated GET failed: "
            f"{path} | "
            f"HTTP {exc.code} | "
            f"{error_body}"
        ) from exc

    except urllib.error.URLError as exc:

        reason = getattr(
            exc,
            "reason",
            exc,
        )

        raise RuntimeError(
            "Authenticated GET failed: "
            f"{path} | "
            f"{reason}"
        ) from exc

    except socket.gaierror as exc:

        raise RuntimeError(
            "Authenticated GET DNS resolution "
            "failed: "
            f"{EXPECTED_WEEX_HOST} | "
            f"{exc}"
        ) from exc

    except TimeoutError as exc:

        raise RuntimeError(
            "Authenticated GET timed out: "
            f"{path}"
        ) from exc


# =====================================================================================
# PART 15 — PUBLIC READ-ONLY GET
# =====================================================================================


PUBLIC_GET_ALLOWLIST = {
    EXCHANGE_INFO_PATH,
}


def public_get(
    path: str,
    parameters: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not PUBLIC_READ_ONLY_ENABLED:

        raise RuntimeError(
            "Public read-only access "
            "is disabled"
        )

    if path not in PUBLIC_GET_ALLOWLIST:

        raise RuntimeError(
            "Public GET path is not "
            f"allowlisted: {path}"
        )

    query_string = encode_query(
        parameters
    )

    if query_string:

        url = (
            WEEX_BASE_URL
            + path
            + "?"
            + query_string
        )

    else:

        url = (
            WEEX_BASE_URL
            + path
        )

    request = urllib.request.Request(
        url=url,
        headers={
            "Accept":
                "application/json",

            "User-Agent":
                USER_AGENT,
        },
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

        payload = json.loads(
            raw
        )

        increment_state(
            "public_get_count"
        )

        return payload

    except urllib.error.HTTPError as exc:

        try:

            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

        except Exception:

            body = ""

        raise RuntimeError(
            "Public GET failed: "
            f"{path} | "
            f"HTTP {exc.code} | "
            f"{body}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "Public GET failed: "
            f"{path} | "
            f"{exc}"
        ) from exc


# =====================================================================================
# PART 16 — RESPONSE NORMALIZATION
# =====================================================================================


def unwrap_payload(
    payload: Any,
) -> Any:

    if isinstance(
        payload,
        dict,
    ):

        if (
            "data" in payload
            and
            payload["data"] is not None
        ):

            return payload[
                "data"
            ]

    return payload


def ensure_list(
    payload: Any,
) -> List[Any]:

    payload = unwrap_payload(
        payload
    )

    if payload is None:
        return []

    if isinstance(
        payload,
        list,
    ):
        return payload

    if isinstance(
        payload,
        dict,
    ):
        return [
            payload
        ]

    raise RuntimeError(
        "Unexpected WEEX response type: "
        f"{type(payload).__name__}"
    )


# =====================================================================================
# PART 17 — NUMERIC HELPERS
# =====================================================================================


def safe_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:

    if value is None:
        return default

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def safe_int(
    value: Any,
    default: Optional[int] = None,
) -> Optional[int]:

    if value is None:
        return default

    try:
        return int(
            float(value)
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


# =====================================================================================
# PART 18 — BALANCE RECONCILIATION
# =====================================================================================


def read_available_usdt() -> float:

    payload = authenticated_get(
        BALANCE_PATH
    )

    balances = ensure_list(
        payload
    )

    for item in balances:

        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get(
                "asset",
                "",
            )
        ).upper()

        if asset != "USDT":
            continue

        available = safe_float(
            item.get(
                "availableBalance"
            )
        )

        if available is None:

            available = safe_float(
                item.get(
                    "available"
                )
            )

        if available is None:

            raise RuntimeError(
                "USDT balance record did not "
                "contain an available balance"
            )

        set_state(
            "available_usdt",
            available,
        )

        return available

    raise RuntimeError(
        "USDT balance record was not "
        "found in WEEX response"
    )


# =====================================================================================
# PART 19 — POSITION RECONCILIATION
# =====================================================================================


def read_positions() -> List[Dict[str, Any]]:

    payload = authenticated_get(
        POSITION_PATH
    )

    positions_raw = ensure_list(
        payload
    )

    positions: List[
        Dict[str, Any]
    ] = []

    for item in positions_raw:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol != SYMBOL:
            continue

        positions.append(
            item
        )

    set_state(
        "position_count",
        len(positions),
    )

    return positions


# =====================================================================================
# PART 20 — SYMBOL CONFIGURATION RECONCILIATION
# =====================================================================================


def read_symbol_config() -> Dict[str, Any]:

    payload = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol":
                SYMBOL,
        },
    )

    configs = ensure_list(
        payload
    )

    for item in configs:

        if not isinstance(
            item,
            dict,
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol != SYMBOL:
            continue

        set_state(
            "symbol_config_found",
            True,
        )

        return item

    raise RuntimeError(
        f"Symbol configuration for {SYMBOL} "
        "was not found"
    )


# =====================================================================================
# PART 21 — SAFETY ASSERTIONS
# =====================================================================================


def validate_write_lock() -> None:

    check(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Exchange Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    check(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    check(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )

    snapshot = snapshot_state()

    check(
        "Network Write Counter Is Zero",
        snapshot[
            "network_writes"
        ] == 0,
    )

    check(
        "Real Order Counter Is Zero",
        snapshot[
            "real_orders"
        ] == 0,
    )

    check(
        "Demo Order Counter Is Zero",
        snapshot[
            "demo_orders"
        ] == 0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        snapshot[
            "leverage_mutations"
        ] == 0,
    )

    check(
        "Margin Mutation Counter Is Zero",
        snapshot[
            "margin_mutations"
        ] == 0,
    )

    check(
        "Position Mutation Counter Is Zero",
        snapshot[
            "position_mutations"
        ] == 0,
    )

    check(
        "Account Mutation Counter Is Zero",
        snapshot[
            "account_mutations"
        ] == 0,
    )


# =====================================================================================
# PART 22 — VALIDATION
# =====================================================================================


def run_validation() -> None:

    # ---------------------------------------------------------------------------------
    # TEST 1
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 1: HARD READ-ONLY SAFETY CONFIGURATION"
    )

    check(
        "Authenticated Read-Only Is Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED
        is True,
    )

    check(
        "Public Read-Only Is Enabled",
        PUBLIC_READ_ONLY_ENABLED
        is True,
    )

    validate_write_lock()


    # ---------------------------------------------------------------------------------
    # TEST 2
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 2: CREDENTIAL PRESENCE"
    )

    validate_credentials()

    check(
        "WEEX API Key Is Present",
        bool(
            WEEX_API_KEY
        ),
    )

    check(
        "WEEX API Secret Is Present",
        bool(
            WEEX_API_SECRET
        ),
    )

    check(
        "WEEX API Passphrase Is Present",
        bool(
            WEEX_API_PASSPHRASE
        ),
    )


    # ---------------------------------------------------------------------------------
    # TEST 2A
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 2A: WEEX API HOST INTEGRITY"
    )

    validate_base_url()


    # ---------------------------------------------------------------------------------
    # TEST 2B
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 2B: WEEX DNS RESOLUTION"
    )

    addresses = resolve_weex_host()

    check(
        "WEEX Hostname Resolved",
        len(addresses) > 0,
    )

    log(
        "DNS ADDRESSES="
        + ", ".join(
            addresses[:5]
        )
    )


    # ---------------------------------------------------------------------------------
    # TEST 3
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 3: LIVE BALANCE RECONCILIATION"
    )

    available_usdt = read_available_usdt()

    log(
        f"BALANCE PATH={BALANCE_PATH}"
    )

    log(
        "AVAILABLE USDT="
        f"{available_usdt:.8f}"
    )

    check(
        "Available Balance Was Read",
        available_usdt
        is not None,
    )

    check(
        "Available Balance Is Non-Negative",
        available_usdt
        >= 0,
    )


    # ---------------------------------------------------------------------------------
    # TEST 4
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 4: POSITION RECONCILIATION"
    )

    positions = read_positions()

    log(
        f"POSITION PATH={POSITION_PATH}"
    )

    log(
        f"{SYMBOL} POSITION COUNT="
        f"{len(positions)}"
    )

    check(
        "Position Response Was Read",
        positions
        is not None,
    )

    if len(
        positions
    ) == 0:

        log(
            f"{SYMBOL}: NO OPEN POSITIONS"
        )

    else:

        for index, position in enumerate(
            positions,
            start=1,
        ):

            log(
                "POSITION "
                f"{index} | "
                f"side="
                f"{position.get('side')} | "
                f"marginType="
                f"{position.get('marginType')} | "
                f"leverage="
                f"{position.get('leverage')} | "
                f"size="
                f"{position.get('size')}"
            )


    # ---------------------------------------------------------------------------------
    # TEST 5
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 5: SYMBOL CONFIGURATION RECONCILIATION"
    )

    symbol_config = read_symbol_config()

    margin_type = str(
        symbol_config.get(
            "marginType",
            "",
        )
    ).upper()

    position_mode = str(
        symbol_config.get(
            "separatedType",
            symbol_config.get(
                "separatedMode",
                "",
            ),
        )
    ).upper()

    cross_leverage = safe_int(
        symbol_config.get(
            "crossLeverage"
        )
    )

    long_leverage = safe_int(
        symbol_config.get(
            "isolatedLongLeverage"
        )
    )

    short_leverage = safe_int(
        symbol_config.get(
            "isolatedShortLeverage"
        )
    )

    set_state(
        "observed_margin_type",
        margin_type,
    )

    set_state(
        "observed_position_mode",
        position_mode,
    )

    set_state(
        "observed_cross_leverage",
        cross_leverage,
    )

    set_state(
        "observed_long_leverage",
        long_leverage,
    )

    set_state(
        "observed_short_leverage",
        short_leverage,
    )

    log(
        f"SYMBOL CONFIG PATH="
        f"{SYMBOL_CONFIG_PATH}"
    )

    log(
        f"SYMBOL={SYMBOL}"
    )

    log(
        f"MARGIN TYPE={margin_type}"
    )

    log(
        f"POSITION MODE={position_mode}"
    )

    log(
        f"CROSS LEVERAGE="
        f"{cross_leverage}x"
    )

    log(
        f"ISOLATED LONG LEVERAGE="
        f"{long_leverage}x"
    )

    log(
        f"ISOLATED SHORT LEVERAGE="
        f"{short_leverage}x"
    )

    check(
        "Symbol Configuration Was Found",
        bool(
            symbol_config
        ),
    )


    # ---------------------------------------------------------------------------------
    # TEST 6
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 6: TARGET CONFIGURATION RECONCILIATION"
    )

    margin_matches = (
        margin_type
        == TARGET_MARGIN_TYPE
    )

    long_matches = (
        long_leverage
        == TARGET_LONG_LEVERAGE
    )

    short_matches = (
        short_leverage
        == TARGET_SHORT_LEVERAGE
    )

    correction_required = not (
        margin_matches
        and
        long_matches
        and
        short_matches
    )

    set_state(
        "correction_required",
        correction_required,
    )

    check(
        "Target Margin Type Is ISOLATED",
        TARGET_MARGIN_TYPE
        == "ISOLATED",
    )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE
        == 100,
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE
        == 100,
    )

    if margin_matches:
        pass_line(
            "Observed Margin Matches Target"
        )

    else:
        fail_line(
            "Observed Margin Matches Target"
        )

    if long_matches:
        pass_line(
            "Observed Long Leverage Matches Target"
        )

    else:
        fail_line(
            "Observed Long Leverage Matches Target"
        )

    if short_matches:
        pass_line(
            "Observed Short Leverage Matches Target"
        )

    else:
        fail_line(
            "Observed Short Leverage Matches Target"
        )

    log(
        "CORRECTION REQUIRED="
        f"{correction_required}"
    )


    # ---------------------------------------------------------------------------------
    # TEST 7
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 7: AUTHENTICATED READ-ONLY TRANSPORT AUDIT"
    )

    snapshot = snapshot_state()

    check(
        "Authenticated GET Counter Is At Least Three",
        snapshot[
            "authenticated_get_count"
        ] >= 3,
    )

    check(
        "No Network Write Was Performed",
        snapshot[
            "network_writes"
        ] == 0,
    )

    check(
        "No Real Order Was Performed",
        snapshot[
            "real_orders"
        ] == 0,
    )

    check(
        "No Demo Order Was Performed",
        snapshot[
            "demo_orders"
        ] == 0,
    )

    check(
        "No Leverage Mutation Was Performed",
        snapshot[
            "leverage_mutations"
        ] == 0,
    )


    # ---------------------------------------------------------------------------------
    # TEST 8
    # ---------------------------------------------------------------------------------

    banner(
        "R34M TEST 8: FINAL SAFETY RECONCILIATION"
    )

    validate_write_lock()

    check(
        "Authenticated Read-Only Remains Enabled",
        AUTHENTICATED_READ_ONLY_ENABLED
        is True,
    )

    check(
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Demo Execution Remains Disabled",
        DEMO_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )


    # ---------------------------------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------------------------------

    set_state(
        "phase",
        "LIVE_READ_ONLY_VALIDATED",
    )

    set_state(
        "validation_complete",
        True,
    )

    set_state(
        "validation_passed",
        True,
    )

    banner(
        "R34M: VALIDATION COMPLETE"
    )

    final_snapshot = snapshot_state()

    log(
        f"SYMBOL={SYMBOL}"
    )

    log(
        f"AVAILABLE USDT="
        f"{final_snapshot['available_usdt']}"
    )

    log(
        f"OPEN {SYMBOL} POSITIONS="
        f"{final_snapshot['position_count']}"
    )

    log(
        "OBSERVED MARGIN="
        f"{final_snapshot['observed_margin_type']}"
    )

    log(
        "OBSERVED LONG="
        f"{final_snapshot['observed_long_leverage']}x"
    )

    log(
        "OBSERVED SHORT="
        f"{final_snapshot['observed_short_leverage']}x"
    )

    log(
        "TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        "TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x"
    )

    log(
        "CORRECTION REQUIRED="
        f"{final_snapshot['correction_required']}"
    )

    log(
        "NETWORK WRITES="
        f"{final_snapshot['network_writes']}"
    )

    log(
        "REAL ORDERS="
        f"{final_snapshot['real_orders']}"
    )

    log(
        "DEMO ORDERS="
        f"{final_snapshot['demo_orders']}"
    )

    log(
        "LEVERAGE MUTATIONS="
        f"{final_snapshot['leverage_mutations']}"
    )


# =====================================================================================
# PART 23 — FAILURE HANDLER
# =====================================================================================


def validation_failure(
    exc: Exception,
) -> None:

    set_state(
        "phase",
        "VALIDATION_FAILED",
    )

    set_state(
        "validation_complete",
        True,
    )

    set_state(
        "validation_passed",
        False,
    )

    set_state(
        "last_error",
        (
            f"{type(exc).__name__}: "
            f"{exc}"
        ),
    )

    banner(
        "R34M: VALIDATION FAILED"
    )

    log(
        "ERROR="
        f"{type(exc).__name__}: "
        f"{exc}"
    )

    snapshot = snapshot_state()

    log(
        "NETWORK WRITES="
        f"{snapshot['network_writes']}"
    )

    log(
        "REAL ORDERS="
        f"{snapshot['real_orders']}"
    )

    log(
        "DEMO ORDERS="
        f"{snapshot['demo_orders']}"
    )

    log(
        "LEVERAGE MUTATIONS="
        f"{snapshot['leverage_mutations']}"
    )


# =====================================================================================
# PART 24 — STARTUP
# =====================================================================================


def print_startup() -> None:

    banner(
        "R34M: MAIN.PY ENTERED"
    )

    log(
        f"SYMBOL={SYMBOL}"
    )

    log(
        f"VERSION={VERSION}"
    )

    log(
        f"HEALTH PORT={PORT}"
    )

    log(
        "WEEX CONTRACT HOST="
        f"{WEEX_BASE_URL}"
    )

    log(
        "AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        "PUBLIC READ-ONLY ENABLED"
    )

    log(
        "REAL ORDER EXECUTION DISABLED"
    )

    log(
        "DEMO ORDER EXECUTION DISABLED"
    )

    log(
        "NETWORK WRITES DISABLED"
    )

    log(
        "LEVERAGE MUTATION DISABLED"
    )

    log(
        "MARGIN MUTATION DISABLED"
    )

    log(
        f"TARGET MARGIN="
        f"{TARGET_MARGIN_TYPE}"
    )

    log(
        f"TARGET LONG="
        f"{TARGET_LONG_LEVERAGE}x"
    )

    log(
        f"TARGET SHORT="
        f"{TARGET_SHORT_LEVERAGE}x"
    )


# =====================================================================================
# PART 25 — MAIN
# =====================================================================================


def main() -> None:

    print_startup()

    start_health_server()

    start_heartbeat()

    set_state(
        "phase",
        "VALIDATING",
    )

    try:

        run_validation()

    except Exception as exc:

        validation_failure(
            exc
        )

        traceback.print_exc()

        # Keep the Render health service alive so the diagnostic state
        # remains available instead of repeatedly restarting immediately.

    while True:

        time.sleep(
            60
        )


# =====================================================================================
# PART 26 — ENTRY POINT
# =====================================================================================


if __name__ == "__main__":
    main()
