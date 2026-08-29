from __future__ import annotations

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
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ==================================================================================================
# R35K - PRE-LIVE READINESS RECONCILIATION (NO LIVE EXECUTION)
# ==================================================================================================
#
# PURPOSE
#   Validate current authenticated WEEX account state immediately before any future live-order stage.
#
# IMPORTANT CORRECTION IN THIS BUILD
#   - Uses current WEEX V3 positions endpoint:
#       GET /capi/v3/account/position/allPosition
#   - A successful empty list [] is a VALID reconciled state and means OPEN POSITIONS = 0.
#   - A transport/auth/parse failure remains UNKNOWN (None) and therefore FAILS CLOSED.
#
# SAFETY MODEL
#   - AUTHENTICATED READS ONLY
#   - EXCHANGE NETWORK WRITES DISABLED
#   - REAL ORDERS DISABLED
#   - DEMO ORDERS DISABLED
#   - FIRST REAL ORDER FORBIDDEN
#   - LIVE EXECUTION AUTHORIZATION DISABLED
#   - NO ORDER / LEVERAGE / MARGIN / POSITION MUTATION
#   - SYNTHETIC ORDER BOUNDARY ONLY
#   - TELEGRAM MAY REPORT ONLY; IT CANNOT CONTROL EXECUTION
# ==================================================================================================

VERSION = "R35K"

SYMBOL = (
    os.getenv(
        "SYMBOL",
        "BTCUSDT",
    ).strip().upper()
    or "BTCUSDT"
)

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

STATE_DIR = Path(
    os.getenv(
        "R35K_STATE_DIR",
        "/tmp/r35k_state",
    )
)

STATE_FILE = (
    STATE_DIR
    / "state.json"
)

JOURNAL_FILE = (
    STATE_DIR
    / "journal.jsonl"
)

WEEX_BASE_URL = (
    os.getenv(
        "WEEX_BASE_URL",
        "https://api-contract.weex.com",
    ).rstrip("/")
)

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
)

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
)

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
)

TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100

TARGET_SHORT_LEVERAGE = 100

VALIDATION_QUANTITY = "0.0001"

MARK_PRICE_PATH = (
    "/capi/v3/market/symbolPrice"
)

BALANCE_PATH = (
    "/capi/v3/account/balance"
)

POSITIONS_PATH = (
    "/capi/v3/account/position/allPosition"
)

SYMBOL_CONFIG_PATH = (
    "/capi/v3/account/symbolConfig"
)

ORDER_PATH = (
    "/capi/v3/order"
)

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv(
        "R35K_HTTP_TIMEOUT",
        "12",
    )
)

# ==================================================================================================
# HARD SAFETY CONSTANTS
# ==================================================================================================

EXCHANGE_NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION_ENABLED = False

DEMO_ORDER_EXECUTION_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False

LIVE_EXECUTION_AUTHORIZATION_ENABLED = False

ORDER_MUTATION_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

# ==================================================================================================
# TELEGRAM REPORTING ONLY
# ==================================================================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
)

TELEGRAM_REPORTING_ENABLED = bool(
    TELEGRAM_BOT_TOKEN
    and TELEGRAM_CHAT_ID
)

# ==================================================================================================
# RUNTIME STATE
# ==================================================================================================

PRINT_LOCK = threading.Lock()

STATE_LOCK = threading.RLock()

EXCHANGE_WRITE_COUNT = 0

SYNTHETIC_DISPATCH_COUNT = 0

TELEGRAM_REPORT_COUNT = 0

TEST_RESULTS: List[
    Tuple[str, bool]
] = []


# ==================================================================================================
# BASIC HELPERS
# ==================================================================================================

def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(
    message: str,
) -> None:

    with PRINT_LOCK:

        print(
            f"{utc_now()} {message}",
            flush=True,
        )


def divider() -> None:

    log(
        "-" * 100
    )


def section(
    title: str,
) -> None:

    divider()

    log(
        title
    )

    divider()


def check(
    label: str,
    condition: bool,
) -> bool:

    condition = bool(
        condition
    )

    TEST_RESULTS.append(
        (
            label,
            condition,
        )
    )

    icon = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    with PRINT_LOCK:

        print(
            f"{label:<84} {icon}",
            flush=True,
        )

    return condition


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

@dataclass
class DurableState:

    version: str = VERSION

    symbol: str = SYMBOL

    generation: int = 1

    epoch: int = 1

    nonce: int = 0

    execution_authorized: bool = False

    exchange_write_count: int = 0

    synthetic_dispatch_count: int = 0

    telegram_report_count: int = 0

    last_journal_hash: str = (
        "0" * 64
    )

    journal_sequence: int = 0

    live_readiness: bool = False

    readiness_blockers: List[str] = field(
        default_factory=list
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


STATE = DurableState()


def ensure_state_dir() -> None:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def atomic_write_json(
    path: Path,
    payload: Dict[str, Any],
) -> None:

    ensure_state_dir()

    tmp = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    data = json.dumps(
        payload,
        sort_keys=True,
        indent=2,
    )

    with open(
        tmp,
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(
            data
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        tmp,
        path,
    )


def save_state() -> None:

    with STATE_LOCK:

        STATE.execution_authorized = False

        STATE.exchange_write_count = (
            EXCHANGE_WRITE_COUNT
        )

        STATE.synthetic_dispatch_count = (
            SYNTHETIC_DISPATCH_COUNT
        )

        STATE.telegram_report_count = (
            TELEGRAM_REPORT_COUNT
        )

        atomic_write_json(
            STATE_FILE,
            STATE.as_dict(),
        )


def load_previous_state() -> Optional[
    DurableState
]:

    if not STATE_FILE.exists():

        return None

    try:

        raw = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

        restored = DurableState()

        for key in (
            restored.as_dict().keys()
        ):

            if key in raw:

                setattr(
                    restored,
                    key,
                    raw[key],
                )

        # Never restore authorization.
        restored.execution_authorized = False

        # Never restore exchange write state.
        restored.exchange_write_count = 0

        return restored

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"PREVIOUS STATE LOAD FAILED CLOSED: "
            f"{type(exc).__name__}"
        )

        return None


# ==================================================================================================
# JOURNAL
# ==================================================================================================

def append_journal(
    event: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:

    with STATE_LOCK:

        ensure_state_dir()

        STATE.journal_sequence += 1

        body = {

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "sequence":
                STATE.journal_sequence,

            "event":
                event,

            "timestamp":
                utc_now(),

            "details":
                details,

            "previous_hash":
                STATE.last_journal_hash,
        }

        record_hash = sha256_text(
            canonical_json(
                body
            )
        )

        record = dict(
            body
        )

        record[
            "record_hash"
        ] = record_hash

        with open(
            JOURNAL_FILE,
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                canonical_json(
                    record
                )
                + "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        STATE.last_journal_hash = (
            record_hash
        )

        save_state()

        return record


def validate_journal() -> Tuple[
    bool,
    int,
]:

    if not JOURNAL_FILE.exists():

        return (
            False,
            0,
        )

    previous_hash = (
        "0" * 64
    )

    expected_sequence = 1

    count = 0

    try:

        lines = (
            JOURNAL_FILE
            .read_text(
                encoding="utf-8"
            )
            .splitlines()
        )

        for raw_line in lines:

            if not raw_line.strip():

                continue

            record = json.loads(
                raw_line
            )

            supplied_hash = record.pop(
                "record_hash",
                None,
            )

            if (
                record.get(
                    "previous_hash"
                )
                != previous_hash
            ):

                return (
                    False,
                    count,
                )

            if (
                record.get(
                    "sequence"
                )
                != expected_sequence
            ):

                return (
                    False,
                    count,
                )

            calculated = sha256_text(
                canonical_json(
                    record
                )
            )

            if (
                supplied_hash
                != calculated
            ):

                return (
                    False,
                    count,
                )

            previous_hash = (
                supplied_hash
            )

            expected_sequence += 1

            count += 1

        return (
            count > 0,
            count,
        )

    except Exception:

        return (
            False,
            count,
        )


# ==================================================================================================
# HTTP / SIGNING
# ==================================================================================================

def build_query(
    params: Optional[
        Dict[str, Any]
    ],
) -> str:

    if not params:

        return ""

    clean = [

        (
            str(key),
            str(value),
        )

        for key, value
        in params.items()

        if value is not None
    ]

    return urllib.parse.urlencode(
        clean
    )


def make_signature(
    timestamp_ms: str,
    method: str,
    request_path_with_query: str,
    body: str = "",
) -> str:

    prehash = (
        timestamp_ms
        + method.upper()
        + request_path_with_query
        + body
    )

    digest = hmac.new(

        WEEX_API_SECRET.encode(
            "utf-8"
        ),

        prehash.encode(
            "utf-8"
        ),

        hashlib.sha256,

    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


def authenticated_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Tuple[
    bool,
    Any,
    str,
]:

    """
    Authenticated WEEX GET only.

    This function cannot issue:
    POST
    PUT
    PATCH
    DELETE
    """

    if not (
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    ):

        return (
            False,
            None,
            "missing credentials",
        )

    query = build_query(
        params
    )

    request_path = (
        path
        + (
            "?"
            + query
            if query
            else ""
        )
    )

    timestamp_ms = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = make_signature(
        timestamp_ms,
        "GET",
        request_path,
        "",
    )

    headers = {

        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp_ms,

        "Content-Type":
            "application/json",

        "Accept":
            "application/json",

        "User-Agent":
            f"{VERSION}-read-only-validator/1.0",
    }

    request = urllib.request.Request(

        WEEX_BASE_URL
        + request_path,

        headers=headers,

        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            text = response.read().decode(
                "utf-8"
            )

            payload = (
                json.loads(
                    text
                )
                if text
                else None
            )

            return (
                True,
                payload,
                "",
            )

    except urllib.error.HTTPError as exc:

        try:

            error_body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            error_body = ""

        return (
            False,
            None,
            (
                f"HTTP {exc.code}: "
                f"{error_body[:500]}"
            ),
        )

    except Exception as exc:

        return (
            False,
            None,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )


def public_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Tuple[
    bool,
    Any,
    str,
]:

    query = build_query(
        params
    )

    request_path = (
        path
        + (
            "?"
            + query
            if query
            else ""
        )
    )

    request = urllib.request.Request(

        WEEX_BASE_URL
        + request_path,

        headers={

            "Accept":
                "application/json",

            "User-Agent":
                f"{VERSION}-validator/1.0",
        },

        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            text = response.read().decode(
                "utf-8"
            )

            payload = (
                json.loads(
                    text
                )
                if text
                else None
            )

            return (
                True,
                payload,
                "",
            )

    except urllib.error.HTTPError as exc:

        try:

            error_body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

        except Exception:

            error_body = ""

        return (
            False,
            None,
            (
                f"HTTP {exc.code}: "
                f"{error_body[:500]}"
            ),
        )

    except Exception as exc:

        return (
            False,
            None,
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )


# ==================================================================================================
# RESPONSE PARSING
# ==================================================================================================

def unwrap_list(
    payload: Any,
) -> Optional[
    List[Any]
]:

    """
    Accept either a direct list or common API list wrappers.

    IMPORTANT:
    malformed data is NOT converted to [].
    """

    if isinstance(
        payload,
        list,
    ):

        return payload

    if isinstance(
        payload,
        dict,
    ):

        for key in (

            "data",
            "result",
            "rows",
            "list",

        ):

            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return value

    return None


# ==================================================================================================
# PUBLIC MARK PRICE
# ==================================================================================================

def obtain_mark_price() -> Tuple[
    bool,
    Optional[float],
    str,
]:

    ok, payload, error = public_get(

        MARK_PRICE_PATH,

        {
            "symbol":
                SYMBOL,

            "priceType":
                "MARK",
        },
    )

    if not ok:

        return (
            False,
            None,
            error,
        )

    try:

        if isinstance(
            payload,
            dict,
        ):

            price = float(
                payload[
                    "price"
                ]
            )

            return (
                price > 0,
                price,
                "",
            )

        return (
            False,
            None,
            "unexpected mark-price payload",
        )

    except Exception as exc:

        return (
            False,
            None,
            (
                "mark-price parse error: "
                f"{exc}"
            ),
        )


# ==================================================================================================
# BALANCE RECONCILIATION
# ==================================================================================================

def obtain_available_balance() -> Tuple[
    bool,
    Optional[float],
    str,
]:

    ok, payload, error = authenticated_get(
        BALANCE_PATH
    )

    if not ok:

        return (
            False,
            None,
            error,
        )

    rows = unwrap_list(
        payload
    )

    if rows is None:

        return (
            False,
            None,
            "unexpected balance payload",
        )

    try:

        for row in rows:

            if (
                isinstance(
                    row,
                    dict,
                )
                and str(
                    row.get(
                        "asset",
                        "",
                    )
                ).upper()
                == "USDT"
            ):

                value = float(
                    row[
                        "availableBalance"
                    ]
                )

                return (
                    value >= 0,
                    value,
                    "",
                )

        return (
            False,
            None,
            "USDT balance not found",
        )

    except Exception as exc:

        return (
            False,
            None,
            (
                "balance parse error: "
                f"{exc}"
            ),
        )


# ==================================================================================================
# CORRECTED POSITION RECONCILIATION
# ==================================================================================================

def obtain_positions() -> Tuple[
    bool,
    Optional[
        List[
            Dict[str, Any]
        ]
    ],
    Optional[int],
    str,
]:

    """
    R35K CORRECTED POSITION RECONCILIATION.

    Current WEEX V3 endpoint:

        GET /capi/v3/account/position/allPosition

    IMPORTANT SEMANTICS:

        HTTP/authentication failure
            -> positions_ok=False
            -> open_positions=None
            -> FAIL CLOSED

        Invalid/malformed response
            -> positions_ok=False
            -> open_positions=None
            -> FAIL CLOSED

        Successful response []
            -> positions_ok=True
            -> open_positions=0
            -> FULLY RECONCILED

        Successful response with BTCUSDT positions
            -> count actual nonzero exposures
    """

    ok, payload, error = authenticated_get(
        POSITIONS_PATH
    )

    if not ok:

        return (
            False,
            None,
            None,
            error,
        )

    rows = unwrap_list(
        payload
    )

    # Critical safety distinction:
    # None = invalid/unknown.
    # []   = valid zero-position response.
    if rows is None:

        return (
            False,
            None,
            None,
            (
                "unexpected positions payload; "
                "expected list"
            ),
        )

    parsed: List[
        Dict[str, Any]
    ] = []

    try:

        for row in rows:

            if not isinstance(
                row,
                dict,
            ):

                return (
                    False,
                    None,
                    None,
                    (
                        "position row "
                        "is not an object"
                    ),
                )

            row_symbol = str(
                row.get(
                    "symbol",
                    "",
                )
            ).upper()

            # Ignore other symbols.
            if row_symbol != SYMBOL:

                continue

            size_raw = row.get(
                "size",
                "0",
            )

            size = float(
                size_raw
            )

            if size < 0:

                return (
                    False,
                    None,
                    None,
                    (
                        "negative position "
                        "size is invalid"
                    ),
                )

            # Only count actual exposure.
            if size > 0:

                parsed.append(
                    row
                )

        return (
            True,
            parsed,
            len(
                parsed
            ),
            "",
        )

    except Exception as exc:

        return (
            False,
            None,
            None,
            (
                "positions parse error: "
                f"{exc}"
            ),
        )


# ==================================================================================================
# SYMBOL CONFIGURATION
# ==================================================================================================

def obtain_symbol_config() -> Tuple[
    bool,
    Optional[
        Dict[str, Any]
    ],
    str,
]:

    ok, payload, error = authenticated_get(

        SYMBOL_CONFIG_PATH,

        {
            "symbol":
                SYMBOL
        },
    )

    if not ok:

        return (
            False,
            None,
            error,
        )

    rows = unwrap_list(
        payload
    )

    if rows is None:

        return (
            False,
            None,
            (
                "unexpected "
                "symbol-config payload"
            ),
        )

    for row in rows:

        if (
            isinstance(
                row,
                dict,
            )
            and str(
                row.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):

            return (
                True,
                row,
                "",
            )

    return (
        False,
        None,
        (
            "symbol configuration "
            f"for {SYMBOL} not found"
        ),
    )


def parse_int(
    value: Any,
) -> Optional[int]:

    try:

        return int(
            float(
                str(
                    value
                )
            )
        )

    except Exception:

        return None


# ==================================================================================================
# READINESS GATE
# ==================================================================================================

def calculate_readiness(
    credentials_ok: bool,
    mark_ok: bool,
    mark_price: Optional[float],
    balance_ok: bool,
    balance: Optional[float],
    positions_ok: bool,
    open_positions: Optional[int],
    config_ok: bool,
    margin_mode: Optional[str],
    long_leverage: Optional[int],
    short_leverage: Optional[int],
) -> Tuple[
    bool,
    List[str],
]:

    blockers: List[
        str
    ] = []

    all_reads = (

        credentials_ok

        and mark_ok

        and balance_ok

        and positions_ok

        and config_ok
    )

    if not all_reads:

        blockers.append(
            (
                "authenticated WEEX "
                "reconciliation incomplete"
            )
        )

    if (
        mark_price is None
        or mark_price <= 0
    ):

        blockers.append(
            (
                "mark price is "
                "unavailable or invalid"
            )
        )

    if (
        balance is None
        or balance < 0
    ):

        blockers.append(
            (
                "available balance is "
                "unavailable or invalid"
            )
        )

    if not positions_ok:

        blockers.append(
            (
                "positions are "
                "not reconciled"
            )
        )

    if open_positions is None:

        blockers.append(
            (
                "open position "
                "count is unknown"
            )
        )

    elif open_positions < 0:

        blockers.append(
            (
                "open position "
                "count is invalid"
            )
        )

    elif open_positions > 0:

        blockers.append(
            (
                f"account has "
                f"{open_positions} open "
                f"{SYMBOL} position(s)"
            )
        )

    if (
        margin_mode
        != TARGET_MARGIN_MODE
    ):

        blockers.append(
            (
                "margin mode is not "
                f"{TARGET_MARGIN_MODE}"
            )
        )

    if (
        long_leverage
        != TARGET_LONG_LEVERAGE
    ):

        blockers.append(
            (
                "isolated long leverage "
                f"is not "
                f"{TARGET_LONG_LEVERAGE}x"
            )
        )

    if (
        short_leverage
        != TARGET_SHORT_LEVERAGE
    ):

        blockers.append(
            (
                "isolated short leverage "
                f"is not "
                f"{TARGET_SHORT_LEVERAGE}x"
            )
        )

    return (
        len(
            blockers
        ) == 0,
        blockers,
    )


# ==================================================================================================
# FUTURE ORDER ENVELOPE - SYNTHETIC ONLY
# ==================================================================================================

def build_future_order_envelope(
    client_order_id: str,
) -> Dict[str, Any]:

    return {

        "method":
            "POST",

        "path":
            ORDER_PATH,

        "payload": {

            "symbol":
                SYMBOL,

            "side":
                "BUY",

            "positionSide":
                "LONG",

            "type":
                "MARKET",

            "quantity":
                VALIDATION_QUANTITY,

            "newClientOrderId":
                client_order_id,
        },

        "synthetic":
            True,

        "transmit":
            False,

        "network_write":
            False,

        "real_order":
            False,
    }


def synthetic_dispatch(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    global SYNTHETIC_DISPATCH_COUNT

    if (
        envelope.get(
            "transmit"
        )
        is not False
    ):

        raise RuntimeError(
            (
                "synthetic envelope "
                "attempted transmission"
            )
        )

    if (
        envelope.get(
            "network_write"
        )
        is not False
    ):

        raise RuntimeError(
            (
                "synthetic envelope "
                "attempted network write"
            )
        )

    if (
        envelope.get(
            "real_order"
        )
        is not False
    ):

        raise RuntimeError(
            (
                "synthetic envelope "
                "attempted real order"
            )
        )

    if (
        EXCHANGE_NETWORK_WRITES_ENABLED
        or REAL_ORDER_EXECUTION_ENABLED
    ):

        raise RuntimeError(
            (
                "hard safety "
                "constants violated"
            )
        )

    SYNTHETIC_DISPATCH_COUNT += 1

    return {

        "status":
            "SYNTHETIC_ONLY",

        "transmitted":
            False,

        "exchange_network_write":
            False,

        "envelope_hash":
            sha256_text(
                canonical_json(
                    envelope
                )
            ),
    }


# ==================================================================================================
# TELEGRAM REPORTING BOUNDARY
# ==================================================================================================

def telegram_preview(
    text: str,
) -> Dict[str, Any]:

    return {

        "method":
            "POST",

        "operation":
            "sendMessage",

        "report_only":
            True,

        "exchange_mutation":
            False,

        "controls_execution":
            False,

        "chat_id":
            (
                TELEGRAM_CHAT_ID
                if TELEGRAM_CHAT_ID
                else "<unset>"
            ),

        "text":
            text,

        "bot_token":
            "<redacted>",
    }


def send_telegram_report(
    text: str,
) -> bool:

    """
    Optional reporting only.

    This POST goes to Telegram.
    It can never mutate WEEX.
    It can never authorize execution.
    """

    global TELEGRAM_REPORT_COUNT

    if not TELEGRAM_REPORTING_ENABLED:

        return False

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
    )

    body = urllib.parse.urlencode(
        {
            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                text,
        }
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(

        url,

        data=body,

        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },

        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            ok = (
                200
                <= int(
                    response.status
                )
                < 300
            )

        if ok:

            TELEGRAM_REPORT_COUNT += 1

        return ok

    except Exception:

        return False


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        payload = {

            "ok":
                True,

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "exchange_network_writes":
                EXCHANGE_WRITE_COUNT,

            "real_order_execution":
                False,

            "execution_authorized":
                False,
        }

        body = json.dumps(
            payload
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    body
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    def runner() -> None:

        server = HTTPServer(

            (
                "0.0.0.0",
                HEALTH_PORT,
            ),

            HealthHandler,
        )

        log(
            (
                f"{VERSION}: "
                "HEALTH SERVER STARTED "
                f"ON PORT {HEALTH_PORT}"
            )
        )

        server.serve_forever()

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def main() -> None:

    global STATE

    ensure_state_dir()

    previous = load_previous_state()

    if previous is not None:

        STATE.generation = max(
            1,
            int(
                previous.generation
            ),
        )

        STATE.epoch = max(
            1,
            int(
                previous.epoch
            ),
        )

        STATE.nonce = max(
            0,
            int(
                previous.nonce
            ),
        )

        STATE.execution_authorized = False

        STATE.exchange_write_count = 0

        STATE.last_journal_hash = str(
            previous.last_journal_hash
        )

        STATE.journal_sequence = int(
            previous.journal_sequence
        )

    start_health_server()

    time.sleep(
        0.01
    )

    divider()

    log(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    divider()

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        (
            f"{VERSION}: "
            f"HEALTH PORT={HEALTH_PORT}"
        )
    )

    log(
        (
            f"{VERSION}: "
            f"STATE DIR={STATE_DIR}"
        )
    )

    log(
        (
            f"{VERSION}: "
            f"WEEX BASE URL={WEEX_BASE_URL}"
        )
    )

    log(
        (
            f"{VERSION}: "
            "AUTHENTICATED READ-ONLY "
            "RECONCILIATION ENABLED"
        )
    )

    log(
        (
            f"{VERSION}: "
            "EXCHANGE NETWORK WRITES=DISABLED"
        )
    )

    log(
        (
            f"{VERSION}: "
            "REAL ORDER EXECUTION=DISABLED"
        )
    )

    log(
        (
            f"{VERSION}: "
            "DEMO ORDER EXECUTION=DISABLED"
        )
    )

    log(
        (
            f"{VERSION}: "
            "FIRST REAL ORDER=FORBIDDEN"
        )
    )

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 1: "
            "HARD SAFETY CONSTANTS"
        )
    )

    check(
        "Exchange Network Writes Are Disabled",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    check(
        "Real Order Execution Is Disabled",
        not REAL_ORDER_EXECUTION_ENABLED,
    )

    check(
        "Demo Order Execution Is Disabled",
        not DEMO_ORDER_EXECUTION_ENABLED,
    )

    check(
        "First Real Order Is Forbidden",
        not FIRST_REAL_ORDER_ALLOWED,
    )

    check(
        "Live Execution Authorization Is Disabled",
        not LIVE_EXECUTION_AUTHORIZATION_ENABLED,
    )

    check(
        "Order Mutation Is Disabled",
        not ORDER_MUTATION_ENABLED,
    )

    check(
        "Leverage Mutation Is Disabled",
        not LEVERAGE_MUTATION_ENABLED,
    )

    check(
        "Margin Mutation Is Disabled",
        not MARGIN_MUTATION_ENABLED,
    )

    check(
        "Position Mutation Is Disabled",
        not POSITION_MUTATION_ENABLED,
    )

    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 2: "
            "CREDENTIAL PRESENCE"
        )
    )

    key_ok = bool(
        WEEX_API_KEY
    )

    secret_ok = bool(
        WEEX_API_SECRET
    )

    passphrase_ok = bool(
        WEEX_API_PASSPHRASE
    )

    credentials_ok = (
        key_ok
        and secret_ok
        and passphrase_ok
    )

    check(
        "WEEX API Key Is Present",
        key_ok,
    )

    check(
        "WEEX API Secret Is Present",
        secret_ok,
    )

    check(
        "WEEX API Passphrase Is Present",
        passphrase_ok,
    )

    check(
        "Complete Authenticated Read Credential Set Is Present",
        credentials_ok,
    )

    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 3: "
            "CURRENT EXCHANGE RECONCILIATION"
        )
    )

    (
        mark_ok,
        mark_price,
        mark_error,
    ) = obtain_mark_price()

    (
        balance_ok,
        available_balance,
        balance_error,
    ) = obtain_available_balance()

    (
        positions_ok,
        positions,
        open_positions,
        positions_error,
    ) = obtain_positions()

    (
        config_ok,
        config,
        config_error,
    ) = obtain_symbol_config()

    margin_mode = (

        str(
            config.get(
                "marginType",
                "",
            )
        ).upper()

        if config

        else None
    )

    long_leverage = (

        parse_int(
            config.get(
                "isolatedLongLeverage"
            )
        )

        if config

        else None
    )

    short_leverage = (

        parse_int(
            config.get(
                "isolatedShortLeverage"
            )
        )

        if config

        else None
    )

    position_mode = None

    if config:

        position_mode = (
            config.get(
                "separatedType"
            )
            or config.get(
                "separatedMode"
            )
        )

    check(
        "Public Mark Price Read Succeeded",
        mark_ok,
    )

    check(
        "Mark Price Is Positive",
        (
            mark_price is not None
            and mark_price > 0
        ),
    )

    check(
        "Authenticated Balance Read Succeeded",
        balance_ok,
    )

    check(
        "Available Balance Was Parsed",
        available_balance is not None,
    )

    check(
        "Authenticated Positions Read Succeeded",
        positions_ok,
    )

    check(
        "Open Position Count Was Reconciled",
        (
            open_positions is not None
            and open_positions >= 0
        ),
    )

    check(
        "Authenticated Symbol Configuration Read Succeeded",
        config_ok,
    )

    all_required_reads = (

        credentials_ok

        and mark_ok

        and balance_ok

        and positions_ok

        and config_ok
    )

    check(
        "All Required Authenticated Reads Succeeded",
        all_required_reads,
    )

    if not mark_ok:

        log(
            (
                f"{VERSION}: "
                f"MARK PRICE READ ERROR="
                f"{mark_error}"
            )
        )

    if not balance_ok:

        log(
            (
                f"{VERSION}: "
                f"BALANCE READ ERROR="
                f"{balance_error}"
            )
        )

    if not positions_ok:

        log(
            (
                f"{VERSION}: "
                f"POSITIONS READ ERROR="
                f"{positions_error}"
            )
        )

        log(
            (
                f"{VERSION}: "
                "POSITIONS ENDPOINT="
                f"{POSITIONS_PATH}"
            )
        )

    if not config_ok:

        log(
            (
                f"{VERSION}: "
                f"SYMBOL CONFIG READ ERROR="
                f"{config_error}"
            )
        )

    log(
        (
            f"{VERSION}: "
            "AVAILABLE BALANCE="
            f"{available_balance}"
        )
    )

    log(
        (
            f"{VERSION}: "
            "MARK PRICE="
            f"{mark_price}"
        )
    )

    log(
        (
            f"{VERSION}: "
            "OPEN POSITIONS="
            f"{open_positions}"
        )
    )

    log(
        (
            f"{VERSION}: "
            "MARGIN MODE="
            f"{margin_mode}"
        )
    )

    log(
        (
            f"{VERSION}: "
            "ISOLATED LONG LEVERAGE="
            f"{long_leverage}"
        )
    )

    log(
        (
            f"{VERSION}: "
            "ISOLATED SHORT LEVERAGE="
            f"{short_leverage}"
        )
    )

    log(
        (
            f"{VERSION}: "
            "POSITION MODE="
            f"{position_mode}"
        )
    )

    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 4: "
            "MARGIN MODE RECONCILIATION"
        )
    )

    check(
        "Observed Margin Mode Is ISOLATED",
        (
            margin_mode
            == TARGET_MARGIN_MODE
        ),
    )

    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 5: "
            "LONG LEVERAGE RECONCILIATION"
        )
    )

    check(
        "Observed Isolated Long Leverage Is 100x",
        (
            long_leverage
            == TARGET_LONG_LEVERAGE
        ),
    )

    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 6: "
            "SHORT LEVERAGE RECONCILIATION"
        )
    )

    check(
        "Observed Isolated Short Leverage Is 100x",
        (
            short_leverage
            == TARGET_SHORT_LEVERAGE
        ),
    )

    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 7: "
            "FAIL-CLOSED READINESS GATE"
        )
    )

    (
        live_readiness,
        blockers,
    ) = calculate_readiness(

        credentials_ok,

        mark_ok,

        mark_price,

        balance_ok,

        available_balance,

        positions_ok,

        open_positions,

        config_ok,

        margin_mode,

        long_leverage,

        short_leverage,
    )

    STATE.live_readiness = (
        live_readiness
    )

    STATE.readiness_blockers = (
        blockers
    )

    # Live execution remains forbidden,
    # even when readiness becomes TRUE.
    STATE.execution_authorized = False

    check(
        "Readiness Gate Produced Deterministic Boolean State",
        isinstance(
            live_readiness,
            bool,
        ),
    )

    check(
        "Execution Authorization Remains False Regardless Of Readiness",
        (
            STATE.execution_authorized
            is False
        ),
    )

    if live_readiness:

        check(
            "All Pre-Live Preconditions Are Reconciled",
            True,
        )

        log(
            (
                f"{VERSION}: "
                "LIVE READINESS=READY "
                "(EXECUTION STILL FORBIDDEN)"
            )
        )

    else:

        check(
            "Failed Pre-Live Preconditions Block Execution",
            (
                STATE.execution_authorized
                is False
            ),
        )

        for blocker in blockers:

            log(
                (
                    f"{VERSION}: "
                    "READINESS BLOCKER: "
                    f"{blocker}"
                )
            )

    append_journal(

        "READINESS_RECONCILIATION",

        {

            "live_readiness":
                live_readiness,

            "blockers":
                blockers,

            "open_positions":
                open_positions,

            "positions_endpoint":
                POSITIONS_PATH,

            "margin_mode":
                margin_mode,

            "isolated_long_leverage":
                long_leverage,

            "isolated_short_leverage":
                short_leverage,

            "exchange_network_writes":
                EXCHANGE_WRITE_COUNT,

            "execution_authorized":
                False,
        },
    )

    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 8: "
            "ZERO-WRITE GUARANTEE"
        )
    )

    check(
        "Exchange Write Count Is Zero Before Synthetic Boundary",
        EXCHANGE_WRITE_COUNT == 0,
    )

    check(
        "Readiness Reconciliation Makes No Exchange Mutation",
        EXCHANGE_WRITE_COUNT == 0,
    )

    # ==============================================================================================
    # CREATE SYNTHETIC ORDER ENVELOPE
    # ==============================================================================================

    STATE.nonce += 1

    client_order_id = (

        f"{VERSION}"
        f"-G{STATE.generation}"
        f"-E{STATE.epoch}"
        f"-N{STATE.nonce}"
        f"-{int(time.time())}"
    )

    envelope = (
        build_future_order_envelope(
            client_order_id
        )
    )

    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 9: "
            "FUTURE ORDER ENVELOPE CONSTRUCTION"
        )
    )

    check(
        "Order Envelope Uses POST",
        (
            envelope[
                "method"
            ]
            == "POST"
        ),
    )

    check(
        "Order Envelope Uses Exact V3 Order Path",
        (
            envelope[
                "path"
            ]
            == ORDER_PATH
        ),
    )

    check(
        "Order Envelope Is Bound To BTCUSDT",
        (
            envelope[
                "payload"
            ][
                "symbol"
            ]
            == SYMBOL
        ),
    )

    check(
        "Order Envelope Uses BUY",
        (
            envelope[
                "payload"
            ][
                "side"
            ]
            == "BUY"
        ),
    )

    check(
        "Order Envelope Uses LONG Position Side",
        (
            envelope[
                "payload"
            ][
                "positionSide"
            ]
            == "LONG"
        ),
    )

    check(
        "Order Envelope Is Synthetic",
        (
            envelope[
                "synthetic"
            ]
            is True
        ),
    )

    check(
        "Order Envelope Forbids Transmission",
        (
            envelope[
                "transmit"
            ]
            is False
        ),
    )

    check(
        "Order Envelope Forbids Network Write",
        (
            envelope[
                "network_write"
            ]
            is False
        ),
    )

    check(
        "Order Envelope Forbids Real Order",
        (
            envelope[
                "real_order"
            ]
            is False
        ),
    )

    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 10: "
            "SYNTHETIC BOUNDARY DISPATCH"
        )
    )

    receipt = synthetic_dispatch(
        envelope
    )

    append_journal(
        "SYNTHETIC_ORDER_BOUNDARY",
        receipt,
    )

    check(
        "Synthetic Boundary Dispatch Completed",
        (
            receipt[
                "status"
            ]
            == "SYNTHETIC_ONLY"
        ),
    )

    check(
        "Synthetic Dispatch Did Not Transmit",
        (
            receipt[
                "transmitted"
            ]
            is False
        ),
    )

    check(
        "Synthetic Dispatch Made No Exchange Network Write",
        (
            receipt[
                "exchange_network_write"
            ]
            is False
        ),
    )

    check(
        "Exchange Write Count Remains Zero After Synthetic Dispatch",
        EXCHANGE_WRITE_COUNT == 0,
    )

    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 11: "
            "READ FAILURE CANNOT AUTHORIZE EXECUTION"
        )
    )

    (
        simulated_ready,
        _,
    ) = calculate_readiness(

        credentials_ok,

        True,

        1.0,

        False,

        None,

        True,

        0,

        True,

        TARGET_MARGIN_MODE,

        TARGET_LONG_LEVERAGE,

        TARGET_SHORT_LEVERAGE,
    )

    check(
        "Missing Balance Forces Readiness False",
        simulated_ready is False,
    )

    check(
        "Missing Balance Cannot Enable Execution",
        (
            STATE.execution_authorized
            is False
        ),
    )

    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 12: "
            "ZERO MARK PRICE CANNOT AUTHORIZE EXECUTION"
        )
    )

    (
        simulated_ready,
        _,
    ) = calculate_readiness(

        credentials_ok,

        True,

        0.0,

        True,

        1.0,

        True,

        0,

        True,

        TARGET_MARGIN_MODE,

        TARGET_LONG_LEVERAGE,

        TARGET_SHORT_LEVERAGE,
    )

    check(
        "Zero Mark Price Forces Readiness False",
        simulated_ready is False,
    )

    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 13: "
            "INVALID POSITION STATE CANNOT AUTHORIZE EXECUTION"
        )
    )

    (
        simulated_ready,
        _,
    ) = calculate_readiness(

        credentials_ok,

        True,

        1.0,

        True,

        1.0,

        True,

        -1,

        True,

        TARGET_MARGIN_MODE,

        TARGET_LONG_LEVERAGE,

        TARGET_SHORT_LEVERAGE,
    )

    check(
        "Negative Position Count Forces Readiness False",
        simulated_ready is False,
    )

    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 14: "
            "WRONG LEVERAGE CANNOT AUTHORIZE EXECUTION"
        )
    )

    (
        simulated_ready,
        _,
    ) = calculate_readiness(

        credentials_ok,

        True,

        1.0,

        True,

        1.0,

        True,

        0,

        True,

        TARGET_MARGIN_MODE,

        50,

        20,
    )

    check(
        "Wrong Long/Short Leverage Forces Readiness False",
        simulated_ready is False,
    )

    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 15: "
            "WRONG MARGIN MODE CANNOT AUTHORIZE EXECUTION"
        )
    )

    (
        simulated_ready,
        _,
    ) = calculate_readiness(

        credentials_ok,

        True,

        1.0,

        True,

        1.0,

        True,

        0,

        True,

        "CROSSED",

        TARGET_LONG_LEVERAGE,

        TARGET_SHORT_LEVERAGE,
    )

    check(
        "Wrong Margin Mode Forces Readiness False",
        simulated_ready is False,
    )

    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 16: "
            "DURABLE RESTART PROTECTION"
        )
    )

    save_state()

    restored = (
        load_previous_state()
    )

    check(
        "Durable State Snapshot Exists",
        STATE_FILE.exists(),
    )

    check(
        "Restart Snapshot Keeps Execution Unauthorized",
        (
            restored is not None
            and restored.execution_authorized
            is False
        ),
    )

    check(
        "Restart Snapshot Keeps Exchange Write Count At Zero",
        (
            restored is not None
            and restored.exchange_write_count
            == 0
        ),
    )

    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 17: "
            "TELEGRAM REPORTING BOUNDARY"
        )
    )

    preview = telegram_preview(
        (
            f"{VERSION} "
            f"readiness={live_readiness}"
        )
    )

    check(
        "Telegram Uses POST Only For Reporting",
        (
            preview[
                "method"
            ]
            == "POST"
        ),
    )

    check(
        "Telegram Operation Is sendMessage",
        (
            preview[
                "operation"
            ]
            == "sendMessage"
        ),
    )

    check(
        "Telegram Request Is Report Only",
        (
            preview[
                "report_only"
            ]
            is True
        ),
    )

    check(
        "Telegram Is Not Exchange Mutation",
        (
            preview[
                "exchange_mutation"
            ]
            is False
        ),
    )

    check(
        "Telegram Cannot Control Execution",
        (
            preview[
                "controls_execution"
            ]
            is False
        ),
    )

    check(
        "Telegram Preview Does Not Expose Bot Token",
        (
            TELEGRAM_BOT_TOKEN
            not in canonical_json(
                preview
            )
            if TELEGRAM_BOT_TOKEN
            else True
        ),
    )

    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 18: "
            "JOURNAL INTEGRITY"
        )
    )

    (
        journal_ok,
        journal_records,
    ) = validate_journal()

    check(
        "Durable Journal Contains Records",
        journal_records > 0,
    )

    check(
        "Durable Journal Hash Chain Is Valid",
        journal_ok,
    )

    check(
        "Journal Sequence Is Monotonic",
        journal_ok,
    )

    append_journal(

        "FINAL_FIREBREAK",

        {

            "exchange_network_writes":
                EXCHANGE_WRITE_COUNT,

            "real_order_execution":
                False,

            "first_real_order":
                False,

            "execution_authorized":
                False,
        },
    )

    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    section(
        (
            f"{VERSION} TEST 19: "
            "FINAL EXECUTION FIREBREAK"
        )
    )

    check(
        "Exchange Network Writes Remain Zero",
        EXCHANGE_WRITE_COUNT == 0,
    )

    check(
        "Real Order Execution Remains Disabled",
        (
            REAL_ORDER_EXECUTION_ENABLED
            is False
        ),
    )

    check(
        "First Real Order Remains Forbidden",
        (
            FIRST_REAL_ORDER_ALLOWED
            is False
        ),
    )

    check(
        "Execution Authorization Remains False",
        (
            STATE.execution_authorized
            is False
        ),
    )

    # ==============================================================================================
    # OPTIONAL FINAL TELEGRAM REPORT
    # ==============================================================================================

    report_lines = [

        f"{VERSION} REPORT",

        f"SYMBOL={SYMBOL}",

        (
            "LIVE_READINESS="
            + (
                "READY"
                if live_readiness
                else "BLOCKED"
            )
        ),

        (
            "OPEN_POSITIONS="
            f"{open_positions}"
        ),

        (
            "MARGIN_MODE="
            f"{margin_mode}"
        ),

        (
            "LONG_LEVERAGE="
            f"{long_leverage}"
        ),

        (
            "SHORT_LEVERAGE="
            f"{short_leverage}"
        ),

        (
            "EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_WRITE_COUNT}"
        ),

        "REAL_ORDER_EXECUTION=False",

        "EXECUTION_AUTHORIZATION=False",
    ]

    send_telegram_report(
        "\n".join(
            report_lines
        )
    )

    save_state()

    # ==============================================================================================
    # FINAL JOURNAL CHECK
    # ==============================================================================================

    (
        journal_ok,
        journal_records,
    ) = validate_journal()

    validation_passed = all(
        result
        for _, result
        in TEST_RESULTS
    )

    # ==============================================================================================
    # SUMMARY
    # ==============================================================================================

    section(
        (
            f"{VERSION}: "
            "VALIDATION SUMMARY"
        )
    )

    print(
        f"✅ {VERSION} VALIDATION REPORT",
        flush=True,
    )

    print(
        "",
        flush=True,
    )

    print(
        f"Symbol: {SYMBOL}",
        flush=True,
    )

    print(
        (
            "Authenticated WEEX reads: "
            + (
                "PASS"
                if all_required_reads
                else "FAIL"
            )
        ),
        flush=True,
    )

    print(
        (
            "Credentials present: "
            + (
                "YES"
                if credentials_ok
                else "NO"
            )
        ),
        flush=True,
    )

    print(
        (
            "Balance: "
            f"{available_balance}"
        ),
        flush=True,
    )

    print(
        (
            "Mark price: "
            f"{mark_price}"
        ),
        flush=True,
    )

    print(
        (
            "Open positions: "
            f"{open_positions}"
        ),
        flush=True,
    )

    print(
        (
            "Positions endpoint: "
            f"{POSITIONS_PATH}"
        ),
        flush=True,
    )

    print(
        (
            "Margin mode: "
            f"{margin_mode}"
        ),
        flush=True,
    )

    print(
        (
            "Isolated long leverage: "
            f"{long_leverage}"
        ),
        flush=True,
    )

    print(
        (
            "Isolated short leverage: "
            f"{short_leverage}"
        ),
        flush=True,
    )

    print(
        (
            "Target long leverage: "
            f"{TARGET_LONG_LEVERAGE}x"
        ),
        flush=True,
    )

    print(
        (
            "Target short leverage: "
            f"{TARGET_SHORT_LEVERAGE}x"
        ),
        flush=True,
    )

    print(
        (
            "Order endpoint: "
            f"{ORDER_PATH}"
        ),
        flush=True,
    )

    print(
        "Order side: BUY",
        flush=True,
    )

    print(
        "Position side: LONG",
        flush=True,
    )

    print(
        (
            "Validation quantity: "
            f"{VALIDATION_QUANTITY} BTC"
        ),
        flush=True,
    )

    print(
        (
            "Client order ID: "
            f"{client_order_id}"
        ),
        flush=True,
    )

    print(
        (
            "Journal integrity: "
            + (
                "PASS"
                if journal_ok
                else "FAIL"
            )
        ),
        flush=True,
    )

    print(
        (
            "Journal records validated: "
            f"{journal_records}"
        ),
        flush=True,
    )

    print(
        (
            "Exchange network writes: "
            f"{EXCHANGE_WRITE_COUNT}"
        ),
        flush=True,
    )

    print(
        "Real order execution: DISABLED",
        flush=True,
    )

    print(
        "Demo order execution: DISABLED",
        flush=True,
    )

    print(
        "First real order: FORBIDDEN",
        flush=True,
    )

    print(
        "Execution authorization: FORBIDDEN",
        flush=True,
    )

    print(
        (
            "Live readiness: "
            + (
                "READY"
                if live_readiness
                else "BLOCKED"
            )
        ),
        flush=True,
    )

    print(
        (
            "Synthetic boundary dispatches: "
            f"{SYNTHETIC_DISPATCH_COUNT}"
        ),
        flush=True,
    )

    print(
        (
            "Telegram reports this run: "
            f"{TELEGRAM_REPORT_COUNT}"
        ),
        flush=True,
    )

    print(
        "",
        flush=True,
    )

    print(
        "Readiness blockers:",
        flush=True,
    )

    if blockers:

        for blocker in blockers:

            print(
                f"- {blocker}",
                flush=True,
            )

    else:

        print(
            "- NONE",
            flush=True,
        )

    print(
        "",
        flush=True,
    )

    print(
        (
            "Validation status: "
            + (
                "PASSED"
                if validation_passed
                else "FAILED"
            )
        ),
        flush=True,
    )

    if (
        validation_passed
        and live_readiness
    ):

        print(
            (
                "Status: PRE-LIVE READINESS VALIDATED "
                "WITH EXECUTION STILL HARD-DISABLED"
            ),
            flush=True,
        )

    elif validation_passed:

        print(
            (
                "Status: PRE-LIVE READINESS BLOCKED "
                "FAIL-CLOSED WITH ZERO EXCHANGE WRITES"
            ),
            flush=True,
        )

    else:

        print(
            (
                "Status: R35K VALIDATION FAILED; "
                "EXECUTION REMAINS HARD-DISABLED"
            ),
            flush=True,
        )


# ==================================================================================================
# ENTRY
# ==================================================================================================

if __name__ == "__main__":

    main()
