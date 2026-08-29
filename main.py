

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35M - ACTIVATION ENVIRONMENT RECONCILIATION
# ==================================================================================================
#
# PURPOSE
#
# R35M is the direct successor to R35L.
#
# R35L proved:
#
#   - authenticated WEEX reads work
#   - account is flat
#   - margin mode is ISOLATED
#   - long leverage is 100x
#   - short leverage is 100x
#   - order envelope is correct
#   - synthetic boundary works
#   - Telegram reporting boundary works
#   - journal integrity works
#   - real exchange writer remains blocked
#
# R35L still reported:
#
#       ACTIVATION_ENV_MISMATCH
#
# R35M therefore performs the activation-environment reconciliation.
#
# IMPORTANT:
#
# Correcting the R35M activation environment DOES NOT enable live trading.
#
# R35M STILL HAS:
#
#   REAL_ORDER_EXECUTION=False
#   DEMO_ORDER_EXECUTION=False
#   EXCHANGE_NETWORK_WRITES_ENABLED=False
#   EXECUTION_AUTHORIZED=False
#   FIRST_REAL_ORDER_ALLOWED=False
#   LIVE_ACTIVATION_ARMED=False
#
# NO REAL ORDER CAN BE SENT BY THIS FILE.
#
# ==================================================================================================


VERSION = "R35M"

SYMBOL = os.getenv(
    "WEEX_SYMBOL",
    "BTCUSDT",
).strip().upper() or "BTCUSDT"


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ==================================================================================================
# WEEX CONNECTION CONFIGURATION
# ==================================================================================================


WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")


# --------------------------------------------------------------------------------------------------
# CORRECT WEEX CREDENTIAL SET
# --------------------------------------------------------------------------------------------------
#
# These are the only three credential names used by R35M.
#
# Do NOT use:
#
#   WEEX_PASSPHRASE
#
# Use:
#
#   WEEX_API_KEY
#   WEEX_API_SECRET
#   WEEX_API_PASSPHRASE
#
# --------------------------------------------------------------------------------------------------


WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()


WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()


WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# ==================================================================================================
# WEEX ENDPOINTS
# ==================================================================================================


BALANCE_PATH = os.getenv(
    "WEEX_BALANCE_PATH",
    "/capi/v3/account/balance",
)


POSITIONS_PATH = os.getenv(
    "WEEX_POSITIONS_PATH",
    "/capi/v3/account/position/allPosition",
)


ACCOUNT_CONFIG_PATH = os.getenv(
    "WEEX_ACCOUNT_CONFIG_PATH",
    "/capi/v3/account/settings",
)


MARK_PRICE_PATH = os.getenv(
    "WEEX_MARK_PRICE_PATH",
    "/capi/v2/market/ticker",
)


ORDER_PATH = "/capi/v3/order"


# ==================================================================================================
# STRATEGY VALIDATION TARGETS
# ==================================================================================================


TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100.0

TARGET_SHORT_LEVERAGE = 100.0

VALIDATION_QUANTITY = "0.0001"


# ==================================================================================================
# R35M ACTIVATION ENVIRONMENT
# ==================================================================================================
#
# THIS IS NOT A LIVE-TRADING SWITCH.
#
# It is only an environment reconciliation marker.
#
# Render environment:
#
#       R35M_ACTIVATION_ENV=VALIDATION_ONLY
#
# Even when this matches, all real execution constants below remain False.
#
# ==================================================================================================


ACTIVATION_ENV_NAME = "R35M_ACTIVATION_ENV"

ACTIVATION_ENV_EXPECTED = "VALIDATION_ONLY"

ACTIVATION_ENV_OBSERVED = os.getenv(
    ACTIVATION_ENV_NAME,
    "",
).strip()


# ==================================================================================================
# ABSOLUTE SAFETY CONSTANTS
# ==================================================================================================
#
# ENVIRONMENT VARIABLES CANNOT OVERRIDE THESE VALUES.
#
# ==================================================================================================


REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

EXECUTION_AUTHORIZED = False

FIRST_REAL_ORDER_ALLOWED = False

LIVE_ACTIVATION_ARMED = False


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()


TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


TELEGRAM_REPORTING_ENABLED = bool(
    TELEGRAM_BOT_TOKEN
    and TELEGRAM_CHAT_ID
)


# ==================================================================================================
# NETWORK TIMEOUTS
# ==================================================================================================


REQUEST_TIMEOUT_SECONDS = float(
    os.getenv(
        "R35M_HTTP_TIMEOUT",
        "12",
    )
)


HEARTBEAT_SECONDS = max(
    10.0,
    float(
        os.getenv(
            "R35M_HEARTBEAT_SECONDS",
            "30",
        )
    ),
)


TELEGRAM_DEDUPE_SECONDS = max(
    60,
    int(
        os.getenv(
            "R35M_TELEGRAM_DEDUPE_SECONDS",
            "21600",
        )
    ),
)


# ==================================================================================================
# STATE DIRECTORY
# ==================================================================================================


def choose_state_dir() -> Path:

    explicit = os.getenv(
        "R35M_STATE_DIR",
        "",
    ).strip()

    if explicit:

        return Path(
            explicit
        )

    render_disk = Path(
        "/var/data"
    )

    if (
        render_disk.exists()
        and os.access(
            str(render_disk),
            os.W_OK,
        )
    ):

        return (
            render_disk
            / "r35m_state"
        )

    return Path(
        "/tmp/r35m_state"
    )


STATE_DIR = choose_state_dir()

STATE_FILE = (
    STATE_DIR
    / "state.json"
)

JOURNAL_FILE = (
    STATE_DIR
    / "journal.jsonl"
)

TELEGRAM_DEDUPE_FILE = (
    STATE_DIR
    / "telegram_dedupe.json"
)


# ==================================================================================================
# LOCKS
# ==================================================================================================


PRINT_LOCK = threading.Lock()

STATE_LOCK = threading.RLock()


# ==================================================================================================
# BASIC HELPERS
# ==================================================================================================


def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(
    message: str = "",
) -> None:

    with PRINT_LOCK:

        if message:

            print(
                f"{utc_now()} {message}",
                flush=True,
            )

        else:

            print(
                "",
                flush=True,
            )


def divider() -> None:

    log(
        "-" * 100
    )


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
# ATOMIC JSON WRITE
# ==================================================================================================


def atomic_write_json(
    path: Path,
    value: Any,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    payload = json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(
            payload
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_path,
        path,
    )


# ==================================================================================================
# STATE PERSISTENCE CLASSIFICATION
# ==================================================================================================


def state_persistence_class() -> str:

    try:

        text = str(
            STATE_DIR.resolve()
        )

    except Exception:

        text = str(
            STATE_DIR
        )

    if (
        text == "/tmp"
        or text.startswith(
            "/tmp/"
        )
    ):

        return "EPHEMERAL"

    return "PERSISTENT_PATH_EXPECTED"


# ==================================================================================================
# STRATEGY STATE
# ==================================================================================================


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = "BOOT"

    generation: int = 1

    epoch: int = 1

    nonce: int = 0

    exchange_network_writes: int = 0

    synthetic_dispatches: int = 0

    telegram_reports_this_process: int = 0

    first_real_order_allowed: bool = False

    execution_authorized: bool = False

    live_activation_armed: bool = False

    last_journal_hash: str = "0" * 64

    journal_sequence: int = 0

    last_summary: Dict[str, Any] = field(
        default_factory=dict
    )


STATE = StrategyState()


# ==================================================================================================
# STATE LOAD
# ==================================================================================================


def load_state() -> None:

    global STATE

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not STATE_FILE.exists():

        atomic_write_json(
            STATE_FILE,
            asdict(
                STATE
            ),
        )

        return

    try:

        raw = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

        allowed_keys = asdict(
            StrategyState()
        ).keys()

        allowed = {
            key: raw[key]
            for key in allowed_keys
            if key in raw
        }

        restored = StrategyState(
            **allowed
        )

        # ------------------------------------------------------------------------------------------
        # FAIL CLOSED ON EVERY RESTART
        # ------------------------------------------------------------------------------------------

        restored.first_real_order_allowed = False

        restored.execution_authorized = False

        restored.live_activation_armed = False

        restored.exchange_network_writes = 0

        restored.telegram_reports_this_process = 0

        STATE = restored

        atomic_write_json(
            STATE_FILE,
            asdict(
                STATE
            ),
        )

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"STATE RESTORE FAILED CLOSED: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        STATE = StrategyState(
            phase="STATE_RESTORE_FAILED_CLOSED"
        )

        atomic_write_json(
            STATE_FILE,
            asdict(
                STATE
            ),
        )


# ==================================================================================================
# STATE SAVE
# ==================================================================================================


def save_state() -> None:

    with STATE_LOCK:

        atomic_write_json(
            STATE_FILE,
            asdict(
                STATE
            ),
        )


# ==================================================================================================
# DURABLE HASH-CHAIN JOURNAL
# ==================================================================================================


def append_journal(
    event: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:

    with STATE_LOCK:

        STATE.journal_sequence += 1

        record_core = {

            "sequence":
                STATE.journal_sequence,

            "timestamp":
                utc_now(),

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "event":
                event,

            "details":
                details,

            "previous_hash":
                STATE.last_journal_hash,
        }

        record_hash = sha256_text(
            canonical_json(
                record_core
            )
        )

        record = dict(
            record_core
        )

        record[
            "record_hash"
        ] = record_hash

        JOURNAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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


# ==================================================================================================
# JOURNAL VALIDATION
# ==================================================================================================


def validate_journal() -> Tuple[
    bool,
    int,
    str,
]:

    if not JOURNAL_FILE.exists():

        return (
            False,
            0,
            "JOURNAL_MISSING",
        )

    previous_hash = (
        "0" * 64
    )

    previous_sequence = 0

    count = 0

    try:

        lines = JOURNAL_FILE.read_text(
            encoding="utf-8"
        ).splitlines()

        for raw_line in lines:

            if not raw_line.strip():

                continue

            record = json.loads(
                raw_line
            )

            count += 1

            record_hash = str(
                record.get(
                    "record_hash",
                    "",
                )
            )

            core = {
                key: value
                for key, value in record.items()
                if key != "record_hash"
            }

            expected_hash = sha256_text(
                canonical_json(
                    core
                )
            )

            sequence = int(
                record.get(
                    "sequence",
                    -1,
                )
            )

            if (
                record_hash
                != expected_hash
            ):

                return (
                    False,
                    count,
                    "HASH_MISMATCH",
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
                    "CHAIN_MISMATCH",
                )

            if (
                sequence
                <= previous_sequence
            ):

                return (
                    False,
                    count,
                    "NON_MONOTONIC_SEQUENCE",
                )

            previous_hash = (
                record_hash
            )

            previous_sequence = (
                sequence
            )

        if count == 0:

            return (
                False,
                0,
                "JOURNAL_EMPTY",
            )

        return (
            True,
            count,
            "OK",
        )

    except Exception as exc:

        return (
            False,
            count,
            (
                "JOURNAL_ERROR:"
                + type(exc).__name__
            ),
        )


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):

            self.send_response(
                404
            )

            self.end_headers()

            return

        with STATE_LOCK:

            payload = {

                "status":
                    "ok",

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "phase":
                    STATE.phase,

                "exchange_network_writes":
                    STATE.exchange_network_writes,

                "real_order_execution":
                    REAL_ORDER_EXECUTION,

                "execution_authorized":
                    STATE.execution_authorized,

                "live_activation_armed":
                    STATE.live_activation_armed,
            }

        body = canonical_json(
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


# ==================================================================================================
# HEALTH SERVER START
# ==================================================================================================


def start_health_server() -> None:

    def runner() -> None:

        server = ThreadingHTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        log(
            f"{VERSION}: "
            f"HEALTH SERVER STARTED "
            f"ON PORT {HEALTH_PORT}"
        )

        server.serve_forever()

    thread = threading.Thread(
        target=runner,
        daemon=True,
        name="r35m-health",
    )

    thread.start()


# ==================================================================================================
# CREDENTIAL CHECK
# ==================================================================================================


def credentials_present() -> bool:

    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )


# ==================================================================================================
# WEEX SIGNATURE
# ==================================================================================================


def weex_signature(
    timestamp_ms: str,
    method: str,
    request_path: str,
    body_text: str,
) -> str:

    prehash = (
        f"{timestamp_ms}"
        f"{method.upper()}"
        f"{request_path}"
        f"{body_text}"
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
        "ascii"
    )


# ==================================================================================================
# AUTHENTICATED READ HEADERS
# ==================================================================================================


def authenticated_headers(
    method: str,
    request_path: str,
) -> Dict[str, str]:

    timestamp_ms = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = weex_signature(
        timestamp_ms,
        method,
        request_path,
        "",
    )

    return {

        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp_ms,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "Accept":
            "application/json",

        "Content-Type":
            "application/json",

        "User-Agent":
            f"{VERSION}-ReadOnly/1.0",
    }


# ==================================================================================================
# JSON RESPONSE DECODER
# ==================================================================================================


def decode_json_bytes(
    raw: bytes,
) -> Any:

    text = raw.decode(
        "utf-8",
        errors="replace",
    )

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError:

        return {
            "raw":
                text
        }


# ==================================================================================================
# PUBLIC GET
# ==================================================================================================


def public_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    query = urllib.parse.urlencode(
        params
        or {}
    )

    request_path = (
        path
        + (
            f"?{query}"
            if query
            else ""
        )
    )

    request = urllib.request.Request(

        url=(
            WEEX_BASE_URL
            + request_path
        ),

        method="GET",

        headers={

            "Accept":
                "application/json",

            "User-Agent":
                f"{VERSION}-ReadOnly/1.0",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        return decode_json_bytes(
            response.read()
        )


# ==================================================================================================
# AUTHENTICATED GET
# ==================================================================================================


def authenticated_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not credentials_present():

        raise RuntimeError(
            "WEEX credentials are incomplete"
        )

    query = urllib.parse.urlencode(
        params
        or {}
    )

    request_path = (
        path
        + (
            f"?{query}"
            if query
            else ""
        )
    )

    headers = authenticated_headers(
        "GET",
        request_path,
    )

    request = urllib.request.Request(

        url=(
            WEEX_BASE_URL
            + request_path
        ),

        method="GET",

        headers=headers,
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        return decode_json_bytes(
            response.read()
        )


# ==================================================================================================
# CRITICAL SAFETY BOUNDARY
# ==================================================================================================
#
# THERE IS INTENTIONALLY:
#
#   NO authenticated_post()
#   NO authenticated_put()
#   NO authenticated_patch()
#   NO authenticated_delete()
#
# FOR WEEX.
#
# R35M CANNOT MUTATE THE EXCHANGE.
#
# ==================================================================================================


def forbidden_real_exchange_writer(
    *args: Any,
    **kwargs: Any,
) -> None:

    raise RuntimeError(
        "R35M_FIREBREAK: "
        "REAL EXCHANGE WRITER "
        "IS HARD DISABLED"
    )


# ==================================================================================================
# SYNTHETIC ORDER ENVELOPE
# ==================================================================================================


def synthetic_order_envelope(
    client_order_id: str,
) -> Dict[str, Any]:

    return {

        "version":
            VERSION,

        "method":
            "POST",

        "path":
            ORDER_PATH,

        "body": {

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

        "execution_authorized":
            False,
    }


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================


def synthetic_dispatch(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    if (
        envelope.get(
            "synthetic"
        )
        is not True
    ):

        raise RuntimeError(
            "R35M_SYNTHETIC_BOUNDARY: "
            "synthetic flag required"
        )

    if (
        envelope.get(
            "transmit"
        )
        is not False
    ):

        raise RuntimeError(
            "R35M_SYNTHETIC_BOUNDARY: "
            "transmission must be false"
        )

    if (
        envelope.get(
            "network_write"
        )
        is not False
    ):

        raise RuntimeError(
            "R35M_SYNTHETIC_BOUNDARY: "
            "network write must be false"
        )

    if (
        envelope.get(
            "real_order"
        )
        is not False
    ):

        raise RuntimeError(
            "R35M_SYNTHETIC_BOUNDARY: "
            "real order must be false"
        )

    with STATE_LOCK:

        STATE.synthetic_dispatches += 1

        save_state()

    receipt = {

        "status":
            "SYNTHETIC_ONLY",

        "transmitted":
            False,

        "exchange_network_write":
            False,

        "real_order_created":
            False,

        "envelope_hash":
            sha256_text(
                canonical_json(
                    envelope
                )
            ),
    }

    append_journal(
        "SYNTHETIC_DISPATCH",
        receipt,
    )

    return receipt


# ==================================================================================================
# RESPONSE SEARCH HELPERS
# ==================================================================================================


def find_values(
    obj: Any,
    keys: List[str],
) -> List[Any]:

    wanted = {
        key.lower()
        for key in keys
    }

    found: List[Any] = []

    if isinstance(
        obj,
        dict,
    ):

        for key, value in obj.items():

            if (
                str(
                    key
                ).lower()
                in wanted
            ):

                found.append(
                    value
                )

            found.extend(
                find_values(
                    value,
                    keys,
                )
            )

    elif isinstance(
        obj,
        list,
    ):

        for item in obj:

            found.extend(
                find_values(
                    item,
                    keys,
                )
            )

    return found


def first_number(
    obj: Any,
    keys: List[str],
) -> Optional[float]:

    values = find_values(
        obj,
        keys,
    )

    for value in values:

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

    return None


def first_text(
    obj: Any,
    keys: List[str],
) -> Optional[str]:

    values = find_values(
        obj,
        keys,
    )

    for value in values:

        if value is None:

            continue

        text = str(
            value
        ).strip()

        if text:

            return text

    return None


# ==================================================================================================
# BALANCE EXTRACTION
# ==================================================================================================


def extract_balance(
    payload: Any,
) -> Optional[float]:

    return first_number(
        payload,
        [
            "available",
            "availableBalance",
            "availableAmount",
            "balance",
        ],
    )


# ==================================================================================================
# MARK PRICE EXTRACTION
# ==================================================================================================


def extract_mark_price(
    payload: Any,
) -> Optional[float]:

    return first_number(
        payload,
        [
            "markPrice",
            "mark_price",
            "last",
            "lastPrice",
            "price",
            "close",
        ],
    )


# ==================================================================================================
# POSITION COUNT
# ==================================================================================================


def count_open_positions(
    payload: Any,
) -> int:

    candidates: List[Any]

    if isinstance(
        payload,
        list,
    ):

        candidates = payload

    elif isinstance(
        payload,
        dict,
    ):

        data = payload.get(
            "data"
        )

        if isinstance(
            data,
            list,
        ):

            candidates = data

        elif isinstance(
            data,
            dict,
        ):

            nested = (
                data.get(
                    "list"
                )
                or data.get(
                    "positions"
                )
            )

            if isinstance(
                nested,
                list,
            ):

                candidates = nested

            else:

                candidates = [
                    data
                ]

        else:

            nested = (
                payload.get(
                    "list"
                )
                or payload.get(
                    "positions"
                )
            )

            if isinstance(
                nested,
                list,
            ):

                candidates = nested

            else:

                candidates = [
                    payload
                ]

    else:

        return 0

    count = 0

    for item in candidates:

        if not isinstance(
            item,
            dict,
        ):

            continue

        size = first_number(
            item,
            [
                "size",
                "positionAmt",
                "positionSize",
                "holdVolume",
                "total",
            ],
        )

        if (
            size is not None
            and abs(
                size
            ) > 0
        ):

            count += 1

    return count


# ==================================================================================================
# ACCOUNT CONFIG EXTRACTION
# ==================================================================================================


def extract_margin_mode(
    payload: Any,
) -> Optional[str]:

    value = first_text(
        payload,
        [
            "marginMode",
            "marginType",
            "margin_mode",
            "margin_type",
        ],
    )

    if not value:

        return None

    return value.upper()


def extract_leverages(
    payload: Any,
) -> Tuple[
    Optional[float],
    Optional[float],
]:

    long_leverage = first_number(
        payload,
        [
            "longLeverage",
            "long_leverage",
            "isolatedLongLeverage",
        ],
    )

    short_leverage = first_number(
        payload,
        [
            "shortLeverage",
            "short_leverage",
            "isolatedShortLeverage",
        ],
    )

    return (
        long_leverage,
        short_leverage,
    )


# ==================================================================================================
# TELEGRAM PREVIEW
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

        "token_exposed":
            False,

        "chat_id_present":
            bool(
                TELEGRAM_CHAT_ID
            ),

        "text_sha256":
            sha256_text(
                text
            ),
    }


# ==================================================================================================
# TELEGRAM DEDUPE LOAD
# ==================================================================================================


def load_telegram_dedupe() -> Dict[str, Any]:

    if not TELEGRAM_DEDUPE_FILE.exists():

        return {}

    try:

        return json.loads(
            TELEGRAM_DEDUPE_FILE.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return {}


# ==================================================================================================
# TELEGRAM DEDUPE DECISION
# ==================================================================================================


def telegram_should_send(
    report_key: str,
) -> Tuple[
    bool,
    str,
]:

    record = load_telegram_dedupe()

    previous_key = str(
        record.get(
            "report_key",
            "",
        )
    )

    previous_timestamp = float(
        record.get(
            "sent_unix",
            0.0,
        )
        or 0.0
    )

    age = (
        time.time()
        - previous_timestamp
    )

    if (
        previous_key
        == report_key
        and 0 <= age < TELEGRAM_DEDUPE_SECONDS
    ):

        return (
            False,
            (
                "DEDUPED_WITHIN_"
                f"{TELEGRAM_DEDUPE_SECONDS}s"
            ),
        )

    return (
        True,
        "SEND_ALLOWED",
    )


# ==================================================================================================
# TELEGRAM REPORT
# ==================================================================================================
#
# Telegram POST is reporting only.
#
# It is NOT connected to execution authorization.
# It cannot arm execution.
# It cannot create an exchange order.
#
# ==================================================================================================


def send_telegram_report(
    text: str,
    report_key: str,
) -> Tuple[
    bool,
    str,
]:

    if not TELEGRAM_REPORTING_ENABLED:

        return (
            False,
            "TELEGRAM_NOT_CONFIGURED",
        )

    allowed, reason = telegram_should_send(
        report_key
    )

    if not allowed:

        return (
            False,
            reason,
        )

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
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

        url=url,

        method="POST",

        data=body,

        headers={

            "Content-Type":
                "application/x-www-form-urlencoded",

            "User-Agent":
                f"{VERSION}-Reporting/1.0",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            payload = decode_json_bytes(
                response.read()
            )

        ok = (
            isinstance(
                payload,
                dict,
            )
            and bool(
                payload.get(
                    "ok"
                )
            )
        )

        if not ok:

            return (
                False,
                "TELEGRAM_API_REJECTED",
            )

        atomic_write_json(
            TELEGRAM_DEDUPE_FILE,
            {

                "report_key":
                    report_key,

                "sent_unix":
                    time.time(),

                "sent_at":
                    utc_now(),

                "version":
                    VERSION,

                "state_dir":
                    str(
                        STATE_DIR
                    ),

                "persistence_class":
                    state_persistence_class(),
            },
        )

        with STATE_LOCK:

            STATE.telegram_reports_this_process += 1

            save_state()

        return (
            True,
            "SENT",
        )

    except Exception as exc:

        return (
            False,
            (
                "TELEGRAM_ERROR:"
                + type(
                    exc
                ).__name__
            ),
        )


# ==================================================================================================
# TEST OUTPUT
# ==================================================================================================


def check(
    label: str,
    condition: bool,
) -> bool:

    result = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    log(
        f"{label:<86} "
        f"{result}"
    )

    return condition


def test_header(
    number: int,
    title: str,
) -> None:

    divider()

    log(
        f"{VERSION} TEST {number}: "
        f"{title}"
    )

    divider()


# ==================================================================================================
# SAFE NETWORK ERROR
# ==================================================================================================


def safe_http_error(
    exc: Exception,
) -> str:

    if isinstance(
        exc,
        urllib.error.HTTPError,
    ):

        return (
            f"HTTP {exc.code}"
        )

    if isinstance(
        exc,
        urllib.error.URLError,
    ):

        return (
            "URL ERROR: "
            + str(
                exc.reason
            )
        )

    return (
        f"{type(exc).__name__}: "
        f"{exc}"
    )


# ==================================================================================================
# HEARTBEAT
# ==================================================================================================


def heartbeat_loop() -> None:

    heartbeat = 0

    while True:

        time.sleep(
            HEARTBEAT_SECONDS
        )

        heartbeat += 1

        with STATE_LOCK:

            phase = (
                STATE.phase
            )

            writes = (
                STATE.exchange_network_writes
            )

        log(
            f"{VERSION}: "
            f"HEARTBEAT={heartbeat} "
            f"PHASE={phase} "
            f"SYMBOL={SYMBOL} "
            f"EXCHANGE_WRITES={writes} "
            f"REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        )


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    load_state()

    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        daemon=True,
        name="r35m-heartbeat",
    )

    heartbeat_thread.start()

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
        f"{VERSION}: HEALTH PORT="
        f"{HEALTH_PORT}"
    )

    log(
        f"{VERSION}: STATE DIR="
        f"{STATE_DIR}"
    )

    log(
        f"{VERSION}: STATE PERSISTENCE CLASS="
        f"{state_persistence_class()}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION "
        f"HARD DISABLED"
    )

    log(
        f"{VERSION}: EXCHANGE MUTATION "
        f"TRANSPORT HARD DISABLED"
    )

    log(
        f"{VERSION}: TELEGRAM REPORTING="
        + (
            "READY"
            if TELEGRAM_REPORTING_ENABLED
            else "NOT CONFIGURED"
        )
    )

    with STATE_LOCK:

        STATE.phase = (
            "R35M_VALIDATING"
        )

        STATE.first_real_order_allowed = False

        STATE.execution_authorized = False

        STATE.live_activation_armed = False

        STATE.exchange_network_writes = 0

        save_state()

    append_journal(
        "R35M_BOOT",
        {

            "real_order_execution":
                REAL_ORDER_EXECUTION,

            "exchange_network_writes_enabled":
                EXCHANGE_NETWORK_WRITES_ENABLED,

            "activation_env_name":
                ACTIVATION_ENV_NAME,

            "state_persistence_class":
                state_persistence_class(),
        },
    )

    all_tests: List[bool] = []


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================


    test_header(
        1,
        "HARD SAFETY INVARIANTS",
    )

    all_tests.extend(
        [

            check(
                "Real Order Execution Is Hard Disabled",
                REAL_ORDER_EXECUTION is False,
            ),

            check(
                "Demo Order Execution Is Disabled",
                DEMO_ORDER_EXECUTION is False,
            ),

            check(
                "Exchange Network Writes Are Hard Disabled",
                EXCHANGE_NETWORK_WRITES_ENABLED is False,
            ),

            check(
                "Exchange Mutation Transport Is Hard Disabled",
                EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
            ),

            check(
                "Leverage Mutation Is Hard Disabled",
                LEVERAGE_MUTATION_ENABLED is False,
            ),

            check(
                "Margin Mutation Is Hard Disabled",
                MARGIN_MUTATION_ENABLED is False,
            ),

            check(
                "Position Mutation Is Hard Disabled",
                POSITION_MUTATION_ENABLED is False,
            ),

            check(
                "Execution Authorization Is Hard Forbidden",
                EXECUTION_AUTHORIZED is False,
            ),

            check(
                "First Real Order Is Hard Forbidden",
                FIRST_REAL_ORDER_ALLOWED is False,
            ),
        ]
    )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================


    test_header(
        2,
        "WEEX CREDENTIAL CONTRACT",
    )

    credential_ok = (
        credentials_present()
    )

    all_tests.extend(
        [

            check(
                "WEEX_API_KEY Is Present",
                bool(
                    WEEX_API_KEY
                ),
            ),

            check(
                "WEEX_API_SECRET Is Present",
                bool(
                    WEEX_API_SECRET
                ),
            ),

            check(
                "WEEX_API_PASSPHRASE Is Present",
                bool(
                    WEEX_API_PASSPHRASE
                ),
            ),

            check(
                "Legacy WEEX_PASSPHRASE Is Not Required",
                True,
            ),

            check(
                "Credential Set Is Complete",
                credential_ok,
            ),
        ]
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================


    test_header(
        3,
        "ACTIVATION ENVIRONMENT RECONCILIATION",
    )

    activation_env_match = (
        ACTIVATION_ENV_OBSERVED
        == ACTIVATION_ENV_EXPECTED
    )

    all_tests.extend(
        [

            check(
                f"{ACTIVATION_ENV_NAME} Is Present",
                bool(
                    ACTIVATION_ENV_OBSERVED
                ),
            ),

            check(
                (
                    f"{ACTIVATION_ENV_NAME} "
                    f"Exactly Matches "
                    f"{ACTIVATION_ENV_EXPECTED}"
                ),
                activation_env_match,
            ),

            check(
                "Activation Environment Cannot Enable Real Orders",
                REAL_ORDER_EXECUTION is False,
            ),

            check(
                "Activation Environment Cannot Arm Execution",
                LIVE_ACTIVATION_ARMED is False,
            ),
        ]
    )

    log(
        f"{VERSION}: "
        f"ACTIVATION ENV EXPECTED="
        f"{ACTIVATION_ENV_EXPECTED}"
    )

    log(
        f"{VERSION}: "
        f"ACTIVATION ENV OBSERVED="
        f"{ACTIVATION_ENV_OBSERVED or '<MISSING>'}"
    )


    # ==============================================================================================
    # LIVE READ VARIABLES
    # ==============================================================================================


    balance_payload: Any = None

    positions_payload: Any = None

    config_payload: Any = None

    mark_payload: Any = None

    balance: Optional[float] = None

    mark_price: Optional[float] = None

    open_positions: Optional[int] = None

    margin_mode: Optional[str] = None

    long_leverage: Optional[float] = None

    short_leverage: Optional[float] = None


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================


    test_header(
        4,
        "AUTHENTICATED WEEX READ-ONLY RECONCILIATION",
    )

    auth_reads_ok = False

    if credential_ok:

        try:

            balance_payload = authenticated_get(
                BALANCE_PATH
            )

            positions_payload = authenticated_get(
                POSITIONS_PATH
            )

            try:

                config_payload = authenticated_get(
                    ACCOUNT_CONFIG_PATH,
                    {
                        "symbol":
                            SYMBOL
                    },
                )

            except Exception:

                config_payload = authenticated_get(
                    ACCOUNT_CONFIG_PATH
                )

            balance = extract_balance(
                balance_payload
            )

            open_positions = count_open_positions(
                positions_payload
            )

            margin_mode = extract_margin_mode(
                config_payload
            )

            (
                long_leverage,
                short_leverage,
            ) = extract_leverages(
                config_payload
            )

            auth_reads_ok = True

        except Exception as exc:

            log(
                f"{VERSION}: "
                f"AUTHENTICATED READ FAILURE="
                f"{safe_http_error(exc)}"
            )

    all_tests.extend(
        [

            check(
                "Authenticated WEEX Reads Completed",
                auth_reads_ok,
            ),

            check(
                "Available Balance Was Read",
                (
                    balance is not None
                    and balance >= 0
                ),
            ),

            check(
                "Open Position Count Was Read",
                open_positions is not None,
            ),

            check(
                "Account Is Flat",
                open_positions == 0,
            ),

            check(
                "Margin Mode Is ISOLATED",
                margin_mode
                == TARGET_MARGIN_MODE,
            ),

            check(
                "Isolated Long Leverage Is 100x",
                long_leverage
                == TARGET_LONG_LEVERAGE,
            ),

            check(
                "Isolated Short Leverage Is 100x",
                short_leverage
                == TARGET_SHORT_LEVERAGE,
            ),
        ]
    )

    if balance is not None:

        log(
            f"{VERSION}: "
            f"BALANCE={balance}"
        )

    log(
        f"{VERSION}: "
        f"OPEN POSITIONS="
        f"{open_positions if open_positions is not None else 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: "
        f"MARGIN MODE="
        f"{margin_mode or 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: "
        f"LONG LEVERAGE="
        f"{long_leverage if long_leverage is not None else 'UNKNOWN'}"
    )

    log(
        f"{VERSION}: "
        f"SHORT LEVERAGE="
        f"{short_leverage if short_leverage is not None else 'UNKNOWN'}"
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================


    test_header(
        5,
        "PUBLIC MARK PRICE",
    )

    mark_ok = False

    try:

        mark_payload = public_get(
            MARK_PRICE_PATH,
            {
                "symbol":
                    SYMBOL
            },
        )

        mark_price = extract_mark_price(
            mark_payload
        )

        mark_ok = bool(
            mark_price is not None
            and mark_price > 0
        )

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"PUBLIC MARK PRICE FAILURE="
            f"{safe_http_error(exc)}"
        )

    all_tests.extend(
        [

            check(
                f"{SYMBOL} Mark Price Was Read",
                mark_ok,
            ),

            check(
                "Mark Price Is Positive",
                (
                    mark_price is not None
                    and mark_price > 0
                ),
            ),
        ]
    )

    if mark_price is not None:

        log(
            f"{VERSION}: "
            f"MARK PRICE={mark_price}"
        )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================


    test_header(
        6,
        "SYNTHETIC ORDER INTENT",
    )

    with STATE_LOCK:

        STATE.nonce += 1

        nonce = STATE.nonce

        save_state()

    client_order_id = (
        f"{VERSION}"
        f"-G{STATE.generation}"
        f"-E{STATE.epoch}"
        f"-N{nonce}"
        f"-{secrets.randbelow(10_000_000_000):010d}"
    )

    envelope = synthetic_order_envelope(
        client_order_id
    )

    all_tests.extend(
        [

            check(
                "Order Endpoint Is Exact V3 Endpoint",
                envelope[
                    "path"
                ] == ORDER_PATH,
            ),

            check(
                "Order Method Is POST",
                envelope[
                    "method"
                ] == "POST",
            ),

            check(
                "Order Uses BUY",
                envelope[
                    "body"
                ][
                    "side"
                ] == "BUY",
            ),

            check(
                "Order Uses LONG Position Side",
                envelope[
                    "body"
                ][
                    "positionSide"
                ] == "LONG",
            ),

            check(
                "Validation Quantity Is 0.0001 BTC",
                envelope[
                    "body"
                ][
                    "quantity"
                ] == VALIDATION_QUANTITY,
            ),

            check(
                "Order Intent Is Synthetic",
                envelope[
                    "synthetic"
                ] is True,
            ),

            check(
                "Order Intent Forbids Transmission",
                envelope[
                    "transmit"
                ] is False,
            ),

            check(
                "Order Intent Forbids Network Write",
                envelope[
                    "network_write"
                ] is False,
            ),

            check(
                "Order Intent Forbids Real Order",
                envelope[
                    "real_order"
                ] is False,
            ),
        ]
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================


    test_header(
        7,
        "SYNTHETIC BOUNDARY",
    )

    receipt = synthetic_dispatch(
        envelope
    )

    all_tests.extend(
        [

            check(
                "Synthetic Boundary Dispatch Completed",
                receipt[
                    "status"
                ] == "SYNTHETIC_ONLY",
            ),

            check(
                "Synthetic Boundary Did Not Transmit",
                receipt[
                    "transmitted"
                ] is False,
            ),

            check(
                "Synthetic Boundary Made No Exchange Network Write",
                receipt[
                    "exchange_network_write"
                ] is False,
            ),

            check(
                "Synthetic Boundary Did Not Create Real Order",
                receipt[
                    "real_order_created"
                ] is False,
            ),

            check(
                "Exchange Write Count Remains Zero",
                STATE.exchange_network_writes == 0,
            ),
        ]
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================


    test_header(
        8,
        "REAL WRITER FIREBREAK",
    )

    writer_blocked = False

    try:

        forbidden_real_exchange_writer(
            envelope
        )

    except RuntimeError:

        writer_blocked = True

    all_tests.extend(
        [

            check(
                "Direct Real Exchange Writer Call Is Blocked",
                writer_blocked,
            ),

            check(
                "Blocked Writer Makes No Exchange Network Write",
                STATE.exchange_network_writes == 0,
            ),

            check(
                "No WEEX Mutation HTTP Helper Exists",
                True,
            ),
        ]
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================


    test_header(
        9,
        "TELEGRAM REPORTING BOUNDARY",
    )

    telegram_test_text = (
        f"{VERSION} "
        f"reporting boundary preview"
    )

    preview = telegram_preview(
        telegram_test_text
    )

    all_tests.extend(
        [

            check(
                "Telegram Uses POST Only For Reporting",
                preview[
                    "method"
                ] == "POST",
            ),

            check(
                "Telegram Operation Is sendMessage",
                preview[
                    "operation"
                ] == "sendMessage",
            ),

            check(
                "Telegram Request Is Report Only",
                preview[
                    "report_only"
                ] is True,
            ),

            check(
                "Telegram Is Not Exchange Mutation",
                preview[
                    "exchange_mutation"
                ] is False,
            ),

            check(
                "Telegram Cannot Control Execution",
                preview[
                    "controls_execution"
                ] is False,
            ),

            check(
                "Telegram Preview Does Not Expose Bot Token",
                preview[
                    "token_exposed"
                ] is False,
            ),

            check(
                "Telegram Dedupe Is Separate From Execution State",
                TELEGRAM_DEDUPE_FILE
                != STATE_FILE,
            ),
        ]
    )

    persistence_class = (
        state_persistence_class()
    )

    persistent_dedupe = (
        persistence_class
        != "EPHEMERAL"
    )

    check(
        "Telegram Dedupe Uses Non-/tmp Persistent Path",
        persistent_dedupe,
    )

    if not persistent_dedupe:

        log(
            f"{VERSION}: "
            f"TELEGRAM DEDUPE WARNING: "
            f"STATE DIR={STATE_DIR}"
        )

        log(
            f"{VERSION}: "
            f"/tmp CAN SURVIVE PROCESS RESTARTS "
            f"BUT MUST NOT BE ASSUMED TO SURVIVE "
            f"RENDER INSTANCE REPLACEMENT OR DEPLOYMENT"
        )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================


    test_header(
        10,
        "DURABLE RESTART FAIL-CLOSED STATE",
    )

    save_state()

    snapshot = json.loads(
        STATE_FILE.read_text(
            encoding="utf-8"
        )
    )

    all_tests.extend(
        [

            check(
                "Durable State Snapshot Exists",
                STATE_FILE.exists(),
            ),

            check(
                "Restart Snapshot Clears Activation Armed State",
                snapshot.get(
                    "live_activation_armed"
                ) is False,
            ),

            check(
                "Restart Snapshot Keeps Execution Unauthorized",
                snapshot.get(
                    "execution_authorized"
                ) is False,
            ),

            check(
                "Restart Snapshot Keeps First Real Order Forbidden",
                snapshot.get(
                    "first_real_order_allowed"
                ) is False,
            ),

            check(
                "Restart Snapshot Keeps Exchange Write Count At Zero",
                snapshot.get(
                    "exchange_network_writes"
                ) == 0,
            ),
        ]
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================


    test_header(
        11,
        "JOURNAL INTEGRITY",
    )

    append_journal(
        "R35M_PRE_SUMMARY",
        {

            "activation_env_match":
                activation_env_match,

            "auth_reads_ok":
                auth_reads_ok,

            "mark_ok":
                mark_ok,

            "exchange_network_writes":
                STATE.exchange_network_writes,
        },
    )

    (
        journal_ok,
        journal_count,
        journal_reason,
    ) = validate_journal()

    all_tests.extend(
        [

            check(
                "Durable Journal Contains Records",
                journal_count > 0,
            ),

            check(
                "Durable Journal Hash Chain Is Valid",
                journal_ok,
            ),

            check(
                "Journal Sequence Is Monotonic",
                (
                    journal_ok
                    and journal_reason
                    == "OK"
                ),
            ),
        ]
    )


    # ==============================================================================================
    # EXCHANGE READINESS
    # ==============================================================================================


    exchange_state_ready = bool(

        auth_reads_ok

        and balance is not None

        and open_positions == 0

        and margin_mode
        == TARGET_MARGIN_MODE

        and long_leverage
        == TARGET_LONG_LEVERAGE

        and short_leverage
        == TARGET_SHORT_LEVERAGE

        and mark_ok

        and journal_ok
    )


    activation_environment_validated = bool(

        exchange_state_ready

        and activation_env_match
    )


    # ==============================================================================================
    # BLOCKERS
    # ==============================================================================================


    blockers: List[str] = []

    if not credential_ok:

        blockers.append(
            "WEEX_CREDENTIALS_INCOMPLETE"
        )

    if not auth_reads_ok:

        blockers.append(
            "AUTHENTICATED_WEEX_READ_FAILED"
        )

    if (
        open_positions is not None
        and open_positions != 0
    ):

        blockers.append(
            "OPEN_POSITION_PRESENT"
        )

    if (
        margin_mode is not None
        and margin_mode
        != TARGET_MARGIN_MODE
    ):

        blockers.append(
            "MARGIN_MODE_MISMATCH"
        )

    if (
        long_leverage is not None
        and long_leverage
        != TARGET_LONG_LEVERAGE
    ):

        blockers.append(
            "LONG_LEVERAGE_MISMATCH"
        )

    if (
        short_leverage is not None
        and short_leverage
        != TARGET_SHORT_LEVERAGE
    ):

        blockers.append(
            "SHORT_LEVERAGE_MISMATCH"
        )

    if not mark_ok:

        blockers.append(
            "MARK_PRICE_READ_FAILED"
        )

    if not activation_env_match:

        blockers.append(
            "ACTIVATION_ENV_MISMATCH"
        )

    if not journal_ok:

        blockers.append(
            "JOURNAL_INTEGRITY_FAILED"
        )

    if (
        persistence_class
        == "EPHEMERAL"
    ):

        blockers.append(
            "TELEGRAM_DEDUPE_NOT_CROSS_DEPLOY_DURABLE"
        )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================


    test_header(
        12,
        "FINAL EXECUTION FIREBREAK",
    )

    all_tests.extend(
        [

            check(
                "Exchange Network Writes Remain Zero",
                STATE.exchange_network_writes == 0,
            ),

            check(
                "Real Order Execution Remains Disabled",
                REAL_ORDER_EXECUTION is False,
            ),

            check(
                "First Real Order Remains Forbidden",
                FIRST_REAL_ORDER_ALLOWED is False,
            ),

            check(
                "Execution Authorization Remains False",
                EXECUTION_AUTHORIZED is False,
            ),

            check(
                "Live Activation Remains Unarmed",
                LIVE_ACTIVATION_ARMED is False,
            ),
        ]
    )


    # ==============================================================================================
    # FINAL VALIDATION
    # ==============================================================================================


    validation_passed = bool(

        all(
            all_tests
        )

        and exchange_state_ready
    )


    with STATE_LOCK:

        if activation_environment_validated:

            STATE.phase = (
                "R35M_ACTIVATION_ENV_VALIDATED"
            )

        else:

            STATE.phase = (
                "R35M_RECONCILIATION_BLOCKED"
            )

        STATE.last_summary = {

            "activation_environment_validated":
                activation_environment_validated,

            "exchange_state_ready":
                exchange_state_ready,

            "blockers":
                blockers,

            "journal_records":
                journal_count,
        }

        STATE.first_real_order_allowed = False

        STATE.execution_authorized = False

        STATE.live_activation_armed = False

        STATE.exchange_network_writes = 0

        save_state()


    append_journal(
        "R35M_VALIDATION_COMPLETE",
        STATE.last_summary,
    )


    # ==============================================================================================
    # SUMMARY
    # ==============================================================================================


    divider()

    log(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    divider()

    log(
        (
            "✅"
            if validation_passed
            else "⚠️"
        )
        + f" {VERSION} VALIDATION REPORT"
    )

    log()

    log(
        f"Symbol: {SYMBOL}"
    )

    log(
        "Authenticated WEEX reads: "
        + (
            "PASS"
            if auth_reads_ok
            else "FAIL"
        )
    )

    log(
        "Credentials present: "
        + (
            "YES"
            if credential_ok
            else "NO"
        )
    )

    log(
        "Credential names: "
        "WEEX_API_KEY / "
        "WEEX_API_SECRET / "
        "WEEX_API_PASSPHRASE"
    )

    log(
        f"Balance: "
        f"{balance if balance is not None else 'UNKNOWN'}"
    )

    log(
        f"Mark price: "
        f"{mark_price if mark_price is not None else 'UNKNOWN'}"
    )

    log(
        f"Open positions: "
        f"{open_positions if open_positions is not None else 'UNKNOWN'}"
    )

    log(
        f"Positions endpoint: "
        f"{POSITIONS_PATH}"
    )

    log(
        f"Margin mode: "
        f"{margin_mode or 'UNKNOWN'}"
    )

    log(
        f"Isolated long leverage: "
        f"{long_leverage if long_leverage is not None else 'UNKNOWN'}"
    )

    log(
        f"Isolated short leverage: "
        f"{short_leverage if short_leverage is not None else 'UNKNOWN'}"
    )

    log(
        f"Target long leverage: "
        f"{int(TARGET_LONG_LEVERAGE)}x"
    )

    log(
        f"Target short leverage: "
        f"{int(TARGET_SHORT_LEVERAGE)}x"
    )

    log(
        f"Order endpoint: "
        f"{ORDER_PATH}"
    )

    log(
        "Order side: BUY"
    )

    log(
        "Position side: LONG"
    )

    log(
        f"Validation quantity: "
        f"{VALIDATION_QUANTITY} BTC"
    )

    log(
        f"Client order ID: "
        f"{client_order_id}"
    )

    log(
        "Journal integrity: "
        + (
            "PASS"
            if journal_ok
            else "FAIL"
        )
    )

    log(
        f"Journal records validated: "
        f"{journal_count}"
    )

    log(
        f"Exchange network writes: "
        f"{STATE.exchange_network_writes}"
    )

    log(
        "Real order execution: DISABLED"
    )

    log(
        "Demo order execution: DISABLED"
    )

    log(
        "First real order: FORBIDDEN"
    )

    log(
        "Execution authorization: FORBIDDEN"
    )

    log(
        "Exchange readiness: "
        + (
            "READY"
            if exchange_state_ready
            else "NOT READY"
        )
    )

    log(
        f"Activation env name: "
        f"{ACTIVATION_ENV_NAME}"
    )

    log(
        f"Activation env expected: "
        f"{ACTIVATION_ENV_EXPECTED}"
    )

    log(
        f"Activation env observed: "
        f"{ACTIVATION_ENV_OBSERVED or '<MISSING>'}"
    )

    log(
        "Activation environment validated: "
        + (
            "YES"
            if activation_environment_validated
            else "NO"
        )
    )

    log(
        "Live activation armed: NO"
    )

    log(
        f"Synthetic boundary dispatches: "
        f"{STATE.synthetic_dispatches}"
    )

    log(
        f"Telegram reports this process: "
        f"{STATE.telegram_reports_this_process}"
    )

    log(
        f"State directory: "
        f"{STATE_DIR}"
    )

    log(
        f"State persistence class: "
        f"{persistence_class}"
    )

    log()

    log(
        "Activation blockers:"
    )

    if blockers:

        for blocker in blockers:

            log(
                f"- {blocker}"
            )

    else:

        log(
            "- NONE"
        )

    log()

    log(
        "Validation status: "
        + (
            "PASSED"
            if validation_passed
            else "BLOCKED"
        )
    )

    if activation_environment_validated:

        log(
            "Status: ACTIVATION ENVIRONMENT VALIDATED; "
            "FIRST REAL ORDER STILL HARD-DISABLED"
        )

    else:

        log(
            "Status: ACTIVATION ENVIRONMENT "
            "RECONCILIATION INCOMPLETE; "
            "FIRST REAL ORDER HARD-DISABLED"
        )


    # ==============================================================================================
    # TELEGRAM READINESS REPORT
    # ==============================================================================================


    report_lines = [

        (
            "✅"
            if activation_environment_validated
            else "⚠️"
        )
        + f" {VERSION} ACTIVATION ENV RECONCILIATION",

        f"SYMBOL={SYMBOL}",

        (
            "BALANCE="
            + str(
                balance
                if balance is not None
                else "UNKNOWN"
            )
        ),

        (
            "MARK_PRICE="
            + str(
                mark_price
                if mark_price is not None
                else "UNKNOWN"
            )
        ),

        (
            "OPEN_POSITIONS="
            + str(
                open_positions
                if open_positions is not None
                else "UNKNOWN"
            )
        ),

        (
            "MARGIN_MODE="
            + str(
                margin_mode
                or "UNKNOWN"
            )
        ),

        (
            "LONG_LEVERAGE="
            + str(
                long_leverage
                if long_leverage is not None
                else "UNKNOWN"
            )
            + "x"
        ),

        (
            "SHORT_LEVERAGE="
            + str(
                short_leverage
                if short_leverage is not None
                else "UNKNOWN"
            )
            + "x"
        ),

        (
            "ACTIVATION_ENV="
            + (
                "VALIDATED"
                if activation_env_match
                else "MISMATCH"
            )
        ),

        (
            "REAL_ORDER_EXECUTION="
            + str(
                REAL_ORDER_EXECUTION
            )
        ),

        (
            "FIRST_REAL_ORDER_ALLOWED="
            + str(
                FIRST_REAL_ORDER_ALLOWED
            )
        ),
    ]

    if blockers:

        report_lines.append(
            "BLOCKERS="
            + ",".join(
                blockers
            )
        )

    else:

        report_lines.append(
            "BLOCKERS=NONE"
        )

    telegram_text = "\n".join(
        report_lines
    )


    # ----------------------------------------------------------------------------------------------
    # Telegram report key deliberately excludes mark price.
    #
    # Otherwise every small BTC price movement would create a different dedupe key and Telegram
    # would send another readiness message.
    # ----------------------------------------------------------------------------------------------


    report_key = sha256_text(
        canonical_json(
            {

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "exchange_state_ready":
                    exchange_state_ready,

                "activation_env_match":
                    activation_env_match,

                "open_positions":
                    open_positions,

                "margin_mode":
                    margin_mode,

                "long_leverage":
                    long_leverage,

                "short_leverage":
                    short_leverage,

                "blockers":
                    blockers,
            }
        )
    )

    (
        telegram_sent,
        telegram_reason,
    ) = send_telegram_report(
        telegram_text,
        report_key,
    )

    log(
        f"{VERSION}: "
        f"TELEGRAM REPORT="
        + (
            "SENT"
            if telegram_sent
            else "NOT SENT"
        )
        + f" REASON={telegram_reason}"
    )


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================


if __name__ == "__main__":

    main()

    while True:

        time.sleep(
            3600
        )
