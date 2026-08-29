

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
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35L - CONTROLLED LIVE ACTIVATION BOUNDARY
# FIRST REAL ORDER STILL HARD-DISABLED
# ==================================================================================================
#
# PURPOSE
#
# R35L carries forward the R35K pre-live readiness proof and introduces
# the final controlled activation boundary that a future version may use
# for the first real order.
#
# SAFETY MODEL
#
# - Authenticated/public READS are allowed.
# - Telegram reporting is allowed.
# - Telegram is NOT an exchange mutation.
# - Repeated readiness Telegram reports are durably deduplicated.
# - Critical Telegram events bypass readiness deduplication.
# - Exchange POST/PUT/PATCH/DELETE remain hard-disabled.
# - First real order remains forbidden.
# - Activation requires multiple exact fail-closed environment gates.
# - Activation is symbol/generation/epoch bound.
# - Activation is one-time and replay protected.
# - Restart cannot enable execution.
# - Environment variables alone cannot create a real exchange write.
#
# EXPECTED END STATE
#
# LIVE_READINESS=READY
# LIVE_ACTIVATION_GATE=VALIDATED
# EXECUTION_AUTHORIZATION=False
# FIRST_REAL_ORDER=FORBIDDEN
# EXCHANGE_NETWORK_WRITES=0
#
# ==================================================================================================


VERSION = "R35L"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api.weex.com",
).rstrip("/")

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

STATE_DIR = Path(
    os.getenv(
        "R35L_STATE_DIR",
        "/tmp/r35l_state",
    )
)

STATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

STATE_FILE = STATE_DIR / "state.json"

JOURNAL_FILE = STATE_DIR / "journal.jsonl"

TELEGRAM_DEDUP_FILE = (
    STATE_DIR / "telegram_dedup.json"
)


# ==================================================================================================
# STRATEGY TARGETS
# ==================================================================================================


TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100

TARGET_SHORT_LEVERAGE = 100

VALIDATION_QTY = "0.0001"


# ==================================================================================================
# WEEX ENDPOINTS
# ==================================================================================================


ORDER_ENDPOINT = (
    "/capi/v3/order"
)

POSITIONS_ENDPOINT = (
    "/capi/v3/account/position/allPosition"
)

BALANCE_ENDPOINT = (
    "/capi/v3/account/assets"
)

SYMBOL_CONFIG_ENDPOINT = (
    "/capi/v3/account/symbolConfig"
)

MARK_PRICE_ENDPOINT = (
    "/capi/v3/market/symbolPrice"
)


# ==================================================================================================
# ABSOLUTE EXECUTION FIREBREAKS
# ==================================================================================================
#
# THESE REMAIN FALSE THROUGHOUT R35L.
#
# Even if every activation environment variable is deliberately supplied,
# R35L cannot transmit a real order.
#
# ==================================================================================================


REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_MUTATION_TRANSPORT_ENABLED = False

FIRST_REAL_ORDER_ALLOWED = False


# ==================================================================================================
# CONTROLLED LIVE ACTIVATION ENVIRONMENT GATES
# ==================================================================================================
#
# A deliberately armed deployment would require ALL of:
#
# R35L_LIVE_ACTIVATION=ARM
#
# R35L_LIVE_SYMBOL=BTCUSDT
#
# R35L_LIVE_GENERATION=1
#
# R35L_LIVE_EPOCH=1
#
# R35L_LIVE_CONFIRM=I_UNDERSTAND_THIS_CAN_PLACE_A_REAL_ORDER
#
#
# IMPORTANT:
#
# DO NOT SET THESE FOR THE INITIAL R35L VALIDATION RUN.
#
# Even when all are later supplied, R35L itself still cannot transmit
# a real order because the code-level writer firebreak remains FALSE.
#
# ==================================================================================================


ACTIVATION_ENV = (
    "R35L_LIVE_ACTIVATION"
)

ACTIVATION_SYMBOL_ENV = (
    "R35L_LIVE_SYMBOL"
)

ACTIVATION_GENERATION_ENV = (
    "R35L_LIVE_GENERATION"
)

ACTIVATION_EPOCH_ENV = (
    "R35L_LIVE_EPOCH"
)

ACTIVATION_CONFIRM_ENV = (
    "R35L_LIVE_CONFIRM"
)

ACTIVATION_CONFIRM_VALUE = (
    "I_UNDERSTAND_THIS_CAN_PLACE_A_REAL_ORDER"
)


# ==================================================================================================
# TELEGRAM CONFIGURATION
# ==================================================================================================


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# Identical readiness reports are suppressed for six hours by default.
#
# Important safety/trading events are NOT subject to this readiness
# deduplication window.

TELEGRAM_READINESS_DEDUP_SECONDS = int(
    os.getenv(
        "TELEGRAM_READINESS_DEDUP_SECONDS",
        "21600",
    )
)


# ==================================================================================================
# WEEX CREDENTIALS
# ==================================================================================================


WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    os.getenv(
        "API_KEY",
        "",
    ),
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    os.getenv(
        "API_SECRET",
        "",
    ),
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    os.getenv(
        "PASSPHRASE",
        "",
    ),
).strip()


# ==================================================================================================
# RUNTIME COUNTERS
# ==================================================================================================


EXCHANGE_NETWORK_WRITES = 0

TELEGRAM_REPORTS_THIS_RUN = 0

SYNTHETIC_BOUNDARY_DISPATCHES = 0

TEST_RESULTS: List[
    Tuple[
        str,
        bool,
    ]
] = []


# ==================================================================================================
# BASIC UTILITIES
# ==================================================================================================


def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(
    message: str = "",
) -> None:

    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def rule() -> None:

    log(
        "-" * 100
    )


def test_header(
    number: int,
    name: str,
) -> None:

    rule()

    log(
        f"{VERSION} TEST {number}: {name}"
    )

    rule()


def check(
    name: str,
    condition: bool,
) -> bool:

    TEST_RESULTS.append(
        (
            name,
            bool(condition),
        )
    )

    status = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{name:<84} {status}",
        flush=True,
    )

    return bool(
        condition
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


def atomic_write_json(
    path: Path,
    value: Dict[str, Any],
) -> None:

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp.write_text(
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    os.replace(
        temp,
        path,
    )


# ==================================================================================================
# DURABLE STRATEGY STATE
# ==================================================================================================


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    live_readiness: bool = False

    live_activation_gate_validated: bool = False

    live_activation_armed: bool = False

    execution_authorization: bool = False

    first_real_order_allowed: bool = False

    last_balance: Optional[
        float
    ] = None

    last_mark_price: Optional[
        float
    ] = None

    last_open_positions: Optional[
        int
    ] = None

    last_margin_mode: Optional[
        str
    ] = None

    last_long_leverage: Optional[
        int
    ] = None

    last_short_leverage: Optional[
        int
    ] = None

    consumed_activation_ids: List[
        str
    ] = field(
        default_factory=list
    )

    used_client_order_ids: List[
        str
    ] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    exchange_network_writes: int = 0

    synthetic_boundary_dispatches: int = 0

    terminal: bool = False

    journal_sequence: int = 0

    last_journal_hash: str = (
        "0" * 64
    )

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ==================================================================================================
# STATE LOAD / SAVE
# ==================================================================================================


def load_state() -> StrategyState:

    if not STATE_FILE.exists():

        return StrategyState()

    try:

        raw = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

        allowed = {
            field_name
            for field_name
            in StrategyState.__dataclass_fields__
        }

        cleaned = {
            key: value
            for key, value
            in raw.items()
            if key in allowed
        }

        state = StrategyState(
            **cleaned
        )

        if (
            state.version != VERSION
            or
            state.symbol != SYMBOL
        ):

            replacement = StrategyState()

            replacement.generation = max(
                1,
                int(
                    state.generation
                ),
            )

            replacement.epoch = max(
                1,
                int(
                    state.epoch
                ),
            )

            return replacement

        # --------------------------------------------------------------
        # RESTART FAIL-CLOSED RESET
        # --------------------------------------------------------------

        state.live_activation_armed = False

        state.execution_authorization = False

        state.first_real_order_allowed = False

        state.exchange_network_writes = 0

        return state

    except Exception:

        return StrategyState()


STATE = load_state()


def save_state() -> None:

    STATE.version = VERSION

    STATE.symbol = SYMBOL

    STATE.exchange_network_writes = (
        EXCHANGE_NETWORK_WRITES
    )

    STATE.synthetic_boundary_dispatches = (
        SYNTHETIC_BOUNDARY_DISPATCHES
    )

    atomic_write_json(
        STATE_FILE,
        STATE.as_dict(),
    )


# ==================================================================================================
# DURABLE JOURNAL
# ==================================================================================================


def append_journal(
    event: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:

    previous_hash = (
        STATE.last_journal_hash
    )

    sequence = (
        STATE.journal_sequence
        + 1
    )

    body = {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "sequence":
            sequence,

        "timestamp":
            utc_now(),

        "event":
            event,

        "generation":
            STATE.generation,

        "epoch":
            STATE.epoch,

        "details":
            details,

        "previous_hash":
            previous_hash,
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

    with JOURNAL_FILE.open(
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

    STATE.journal_sequence = (
        sequence
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
            True,
            0,
        )

    previous_hash = (
        "0" * 64
    )

    expected_sequence = 1

    count = 0

    try:

        with JOURNAL_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:

                line = line.strip()

                if not line:

                    continue

                record = json.loads(
                    line
                )

                record_hash = record.pop(
                    "record_hash",
                    None,
                )

                if (
                    record.get(
                        "sequence"
                    )
                    !=
                    expected_sequence
                ):

                    return (
                        False,
                        count,
                    )

                if (
                    record.get(
                        "previous_hash"
                    )
                    !=
                    previous_hash
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
                    calculated
                    !=
                    record_hash
                ):

                    return (
                        False,
                        count,
                    )

                previous_hash = (
                    record_hash
                )

                expected_sequence += 1

                count += 1

        return (
            True,
            count,
        )

    except Exception:

        return (
            False,
            count,
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

        payload = {

            "ok":
                True,

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "live_readiness":
                STATE.live_readiness,

            "live_activation_armed":
                STATE.live_activation_armed,

            "execution_authorization":
                STATE.execution_authorization,

            "exchange_network_writes":
                EXCHANGE_NETWORK_WRITES,

            "real_order_execution":
                REAL_ORDER_EXECUTION,
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

    def worker() -> None:

        server = HTTPServer(
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

    threading.Thread(
        target=worker,
        daemon=True,
    ).start()


# ==================================================================================================
# HTTP TRANSPORT
# ==================================================================================================


def http_json(
    method: str,
    url: str,
    headers: Optional[
        Dict[str, str]
    ] = None,
    body: Optional[
        bytes
    ] = None,
    timeout: int = 12,
) -> Any:

    request = urllib.request.Request(
        url=url,
        data=body,
        headers=(
            headers
            or {}
        ),
        method=method,
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            if not raw:

                return {}

            return json.loads(
                raw
            )

    except urllib.error.HTTPError as exc:

        raw = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: "
            f"{raw[:500]}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"NETWORK ERROR: {exc}"
        ) from exc


# ==================================================================================================
# WEEX SIGNING / READ-ONLY REQUESTS
# ==================================================================================================


def extract_data(
    payload: Any,
) -> Any:

    if (
        isinstance(
            payload,
            dict,
        )
        and
        "data" in payload
    ):

        return payload[
            "data"
        ]

    return payload


def public_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    query = ""

    if params:

        query = (
            "?"
            +
            urllib.parse.urlencode(
                params
            )
        )

    return http_json(
        "GET",
        BASE_URL
        + path
        + query,
    )


def weex_signature(
    timestamp_ms: str,
    method: str,
    request_path: str,
    body_text: str = "",
) -> str:

    prehash = (
        timestamp_ms
        +
        method.upper()
        +
        request_path
        +
        body_text
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


def authenticated_get(
    path: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not (
        WEEX_API_KEY
        and
        WEEX_API_SECRET
        and
        WEEX_PASSPHRASE
    ):

        raise RuntimeError(
            "WEEX credentials are incomplete"
        )

    query = ""

    if params:

        query = (
            "?"
            +
            urllib.parse.urlencode(
                params
            )
        )

    request_path = (
        path
        + query
    )

    timestamp_ms = str(
        int(
            time.time()
            * 1000
        )
    )

    headers = {

        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            weex_signature(
                timestamp_ms,
                "GET",
                request_path,
            ),

        "ACCESS-PASSPHRASE":
            WEEX_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp_ms,

        "Content-Type":
            "application/json",

        "Accept":
            "application/json",
    }

    return http_json(
        "GET",
        BASE_URL
        + request_path,
        headers=headers,
    )


# ==================================================================================================
# TELEGRAM DEDUPLICATED REPORTING
# ==================================================================================================


def load_telegram_dedup() -> Dict[
    str,
    Any,
]:

    if not TELEGRAM_DEDUP_FILE.exists():

        return {}

    try:

        value = json.loads(
            TELEGRAM_DEDUP_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(
            value,
            dict,
        ):

            return value

        return {}

    except Exception:

        return {}


def telegram_fingerprint(
    event_type: str,
    message: str,
) -> str:

    lines = message.splitlines()

    # --------------------------------------------------------------
    # These fields naturally change every validation run.
    #
    # If included in the fingerprint, every restart would appear to
    # be a new readiness report and deduplication would fail.
    # --------------------------------------------------------------

    if event_type.endswith(
        "_READINESS"
    ):

        ignored_prefixes = (

            "CLIENT_ORDER_ID=",

            "JOURNAL_RECORDS=",
        )

        lines = [

            line

            for line
            in lines

            if not line.startswith(
                ignored_prefixes
            )
        ]

    normalized = "\n".join(
        lines
    )

    return sha256_text(
        event_type
        + "\n"
        + normalized
    )


def send_telegram(
    message: str,
    *,
    event_type: str,
    critical: bool = False,
    deduplicate: bool = False,
) -> bool:

    global TELEGRAM_REPORTS_THIS_RUN

    if not (
        TELEGRAM_BOT_TOKEN
        and
        TELEGRAM_CHAT_ID
    ):

        return False

    now = int(
        time.time()
    )

    fingerprint = telegram_fingerprint(
        event_type,
        message,
    )

    dedup_state = (
        load_telegram_dedup()
    )

    if (
        deduplicate
        and
        not critical
    ):

        prior = dedup_state.get(
            fingerprint
        )

        if isinstance(
            prior,
            dict,
        ):

            last_sent = int(
                prior.get(
                    "last_sent",
                    0,
                )
            )

            elapsed = (
                now
                -
                last_sent
            )

            if (
                elapsed
                <
                TELEGRAM_READINESS_DEDUP_SECONDS
            ):

                log(
                    f"{VERSION}: "
                    f"TELEGRAM {event_type} "
                    f"SUPPRESSED BY DEDUP "
                    f"({elapsed}s since identical report)"
                )

                return False

    endpoint = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        "sendMessage"
    )

    form = urllib.parse.urlencode(
        {

            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                message,

            "disable_web_page_preview":
                "true",
        }
    ).encode(
        "utf-8"
    )

    try:

        result = http_json(
            "POST",
            endpoint,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },
            body=form,
            timeout=10,
        )

        ok = (
            bool(
                result.get(
                    "ok"
                )
            )
            if isinstance(
                result,
                dict,
            )
            else False
        )

        if ok:

            TELEGRAM_REPORTS_THIS_RUN += 1

            if (
                deduplicate
                and
                not critical
            ):

                dedup_state[
                    fingerprint
                ] = {

                    "event_type":
                        event_type,

                    "last_sent":
                        now,

                    "version":
                        VERSION,
                }

                atomic_write_json(
                    TELEGRAM_DEDUP_FILE,
                    dedup_state,
                )

        return ok

    except Exception as exc:

        log(
            f"{VERSION}: "
            f"TELEGRAM REPORT FAILED: "
            f"{exc}"
        )

        return False


def telegram_preview_safe() -> bool:

    preview = {

        "method":
            "POST",

        "host":
            "api.telegram.org",

        "operation":
            "sendMessage",

        "purpose":
            "REPORT_ONLY",
    }

    text = canonical_json(
        preview
    )

    return (
        TELEGRAM_BOT_TOKEN
        not in text
        and
        WEEX_API_SECRET
        not in text
    )


# ==================================================================================================
# RESPONSE PARSING
# ==================================================================================================


def to_float(
    value: Any,
) -> Optional[float]:

    try:

        if (
            value is None
            or
            value == ""
        ):

            return None

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


def find_first_numeric(
    value: Any,
    keys: List[str],
) -> Optional[float]:

    if isinstance(
        value,
        dict,
    ):

        for key in keys:

            if key in value:

                result = to_float(
                    value.get(
                        key
                    )
                )

                if result is not None:

                    return result

        for child in value.values():

            result = find_first_numeric(
                child,
                keys,
            )

            if result is not None:

                return result

    elif isinstance(
        value,
        list,
    ):

        for child in value:

            result = find_first_numeric(
                child,
                keys,
            )

            if result is not None:

                return result

    return None


def find_first_text(
    value: Any,
    keys: List[str],
) -> Optional[str]:

    if isinstance(
        value,
        dict,
    ):

        for key in keys:

            if (
                key in value
                and
                value[
                    key
                ] is not None
            ):

                return str(
                    value[
                        key
                    ]
                ).strip()

        for child in value.values():

            result = find_first_text(
                child,
                keys,
            )

            if result:

                return result

    elif isinstance(
        value,
        list,
    ):

        for child in value:

            result = find_first_text(
                child,
                keys,
            )

            if result:

                return result

    return None


# ==================================================================================================
# ACCOUNT READS
# ==================================================================================================


def obtain_available_balance() -> float:

    payload = extract_data(
        authenticated_get(
            BALANCE_ENDPOINT
        )
    )

    value = find_first_numeric(
        payload,
        [

            "available",

            "availableBalance",

            "availableAmount",

            "availableMargin",

            "balanceAvailable",
        ],
    )

    if value is None:

        raise RuntimeError(
            "Could not locate available balance "
            "in WEEX response"
        )

    return value


def obtain_mark_price() -> float:

    payload = extract_data(
        public_get(
            MARK_PRICE_ENDPOINT,
            {
                "symbol":
                    SYMBOL
            },
        )
    )

    value = find_first_numeric(
        payload,
        [

            "markPrice",

            "price",

            "last",

            "lastPrice",

            "close",
        ],
    )

    if value is None:

        raise RuntimeError(
            "Could not locate mark price "
            "in WEEX response"
        )

    return value


def obtain_positions() -> Tuple[
    int,
    Any,
]:

    payload = extract_data(
        authenticated_get(
            POSITIONS_ENDPOINT,
            {
                "symbol":
                    SYMBOL
            },
        )
    )

    if payload is None:

        return (
            0,
            [],
        )

    if isinstance(
        payload,
        list,
    ):

        active = []

        for item in payload:

            if not isinstance(
                item,
                dict,
            ):

                continue

            size = find_first_numeric(
                item,
                [

                    "size",

                    "positionSize",

                    "total",

                    "holdVol",

                    "available",
                ],
            )

            if size is None:

                active.append(
                    item
                )

            elif abs(
                size
            ) > 0:

                active.append(
                    item
                )

        return (
            len(
                active
            ),
            payload,
        )

    if isinstance(
        payload,
        dict,
    ):

        for key in (

            "list",

            "positions",

            "positionList",
        ):

            if isinstance(
                payload.get(
                    key
                ),
                list,
            ):

                inner = payload[
                    key
                ]

                active_count = 0

                for item in inner:

                    size = find_first_numeric(
                        item,
                        [

                            "size",

                            "positionSize",

                            "total",

                            "holdVol",

                            "available",
                        ],
                    )

                    if (
                        size is None
                        or
                        abs(
                            size
                        ) > 0
                    ):

                        active_count += 1

                return (
                    active_count,
                    payload,
                )

        if payload:

            return (
                1,
                payload,
            )

    return (
        0,
        payload,
    )


def obtain_symbol_config() -> Tuple[
    str,
    int,
    int,
    Any,
]:

    payload = extract_data(
        authenticated_get(
            SYMBOL_CONFIG_ENDPOINT,
            {
                "symbol":
                    SYMBOL
            },
        )
    )

    margin_mode = find_first_text(
        payload,
        [

            "marginMode",

            "marginType",

            "margin_mode",

            "margin_type",
        ],
    )

    long_leverage = find_first_numeric(
        payload,
        [

            "isolatedLongLeverage",

            "longLeverage",

            "long_leverage",

            "leverageLong",
        ],
    )

    short_leverage = find_first_numeric(
        payload,
        [

            "isolatedShortLeverage",

            "shortLeverage",

            "short_leverage",

            "leverageShort",
        ],
    )

    if margin_mode is None:

        raise RuntimeError(
            "Could not locate margin mode "
            "in symbol configuration"
        )

    if (
        long_leverage is None
        or
        short_leverage is None
    ):

        raise RuntimeError(
            "Could not locate isolated leverage "
            "values in symbol configuration"
        )

    return (

        margin_mode.upper(),

        int(
            long_leverage
        ),

        int(
            short_leverage
        ),

        payload,
    )


# ==================================================================================================
# READINESS MODEL
# ==================================================================================================


@dataclass(
    frozen=True
)
class ReadinessSnapshot:

    balance: Optional[
        float
    ]

    mark_price: Optional[
        float
    ]

    open_positions: Optional[
        int
    ]

    margin_mode: Optional[
        str
    ]

    long_leverage: Optional[
        int
    ]

    short_leverage: Optional[
        int
    ]

    authenticated_reads_passed: bool

    blockers: Tuple[
        str,
        ...
    ]

    ready: bool


def evaluate_readiness(
    balance: Optional[float],
    mark_price: Optional[float],
    open_positions: Optional[int],
    margin_mode: Optional[str],
    long_leverage: Optional[int],
    short_leverage: Optional[int],
    authenticated_reads_passed: bool,
) -> ReadinessSnapshot:

    blockers: List[
        str
    ] = []

    if not authenticated_reads_passed:

        blockers.append(
            "AUTHENTICATED_READ_FAILURE"
        )

    if balance is None:

        blockers.append(
            "MISSING_BALANCE"
        )

    elif balance <= 0:

        blockers.append(
            "NON_POSITIVE_BALANCE"
        )

    if mark_price is None:

        blockers.append(
            "MISSING_MARK_PRICE"
        )

    elif mark_price <= 0:

        blockers.append(
            "ZERO_OR_NEGATIVE_MARK_PRICE"
        )

    if open_positions is None:

        blockers.append(
            "MISSING_POSITION_STATE"
        )

    elif open_positions < 0:

        blockers.append(
            "INVALID_POSITION_COUNT"
        )

    elif open_positions != 0:

        blockers.append(
            "OPEN_POSITION_EXISTS"
        )

    if (
        margin_mode
        or ""
    ).upper() != TARGET_MARGIN_MODE:

        blockers.append(
            "WRONG_MARGIN_MODE"
        )

    if (
        long_leverage
        !=
        TARGET_LONG_LEVERAGE
    ):

        blockers.append(
            "WRONG_LONG_LEVERAGE"
        )

    if (
        short_leverage
        !=
        TARGET_SHORT_LEVERAGE
    ):

        blockers.append(
            "WRONG_SHORT_LEVERAGE"
        )

    return ReadinessSnapshot(

        balance=balance,

        mark_price=mark_price,

        open_positions=open_positions,

        margin_mode=margin_mode,

        long_leverage=long_leverage,

        short_leverage=short_leverage,

        authenticated_reads_passed=(
            authenticated_reads_passed
        ),

        blockers=tuple(
            blockers
        ),

        ready=(
            not blockers
        ),
    )


# ==================================================================================================
# LIVE ACTIVATION MODEL
# ==================================================================================================


@dataclass(
    frozen=True
)
class ActivationDecision:

    exact_env_match: bool

    already_consumed: bool

    ready: bool

    armed: bool

    activation_id: str

    blockers: Tuple[
        str,
        ...
    ]


def activation_material() -> Dict[
    str,
    Any,
]:

    return {

        "version":
            VERSION,

        "symbol":
            SYMBOL,

        "generation":
            STATE.generation,

        "epoch":
            STATE.epoch,

        "activation":
            os.getenv(
                ACTIVATION_ENV,
                "",
            ),

        "activation_symbol":
            os.getenv(
                ACTIVATION_SYMBOL_ENV,
                "",
            ),

        "activation_generation":
            os.getenv(
                ACTIVATION_GENERATION_ENV,
                "",
            ),

        "activation_epoch":
            os.getenv(
                ACTIVATION_EPOCH_ENV,
                "",
            ),

        "confirmation":
            os.getenv(
                ACTIVATION_CONFIRM_ENV,
                "",
            ),
    }


def evaluate_activation(
    readiness: ReadinessSnapshot,
) -> ActivationDecision:

    material = (
        activation_material()
    )

    activation_id = sha256_text(
        canonical_json(
            material
        )
    )

    exact_env_match = (

        material[
            "activation"
        ] == "ARM"

        and

        material[
            "activation_symbol"
        ] == SYMBOL

        and

        material[
            "activation_generation"
        ] == str(
            STATE.generation
        )

        and

        material[
            "activation_epoch"
        ] == str(
            STATE.epoch
        )

        and

        material[
            "confirmation"
        ] == ACTIVATION_CONFIRM_VALUE
    )

    already_consumed = (
        activation_id
        in
        STATE.consumed_activation_ids
    )

    blockers: List[
        str
    ] = []

    if not readiness.ready:

        blockers.append(
            "READINESS_NOT_READY"
        )

    if not exact_env_match:

        blockers.append(
            "ACTIVATION_ENV_MISMATCH"
        )

    if already_consumed:

        blockers.append(
            "ACTIVATION_REPLAY"
        )

    if STATE.terminal:

        blockers.append(
            "TERMINAL_STATE"
        )

    armed = (
        not blockers
    )

    return ActivationDecision(

        exact_env_match=(
            exact_env_match
        ),

        already_consumed=(
            already_consumed
        ),

        ready=(
            readiness.ready
        ),

        armed=(
            armed
        ),

        activation_id=(
            activation_id
        ),

        blockers=tuple(
            blockers
        ),
    )


def consume_activation_once(
    decision: ActivationDecision,
) -> bool:

    if not decision.armed:

        return False

    if (
        decision.activation_id
        in
        STATE.consumed_activation_ids
    ):

        return False

    STATE.consumed_activation_ids.append(
        decision.activation_id
    )

    STATE.live_activation_armed = True

    STATE.execution_authorization = False

    STATE.first_real_order_allowed = False

    append_journal(
        "LIVE_ACTIVATION_ARMED_BUT_EXECUTION_FORBIDDEN",
        {

            "activation_id":
                decision.activation_id,

            "generation":
                STATE.generation,

            "epoch":
                STATE.epoch,

            "symbol":
                SYMBOL,

            "real_order_execution":
                REAL_ORDER_EXECUTION,

            "exchange_mutation_transport_enabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED,
        },
    )

    save_state()

    return True


# ==================================================================================================
# ORDER ENVELOPE
# ==================================================================================================


def next_nonce() -> int:

    STATE.highest_nonce += 1

    save_state()

    return STATE.highest_nonce


def create_client_order_id() -> str:

    nonce = next_nonce()

    suffix = secrets.randbelow(
        10 ** 10
    )

    return (
        f"{VERSION}"
        f"-G{STATE.generation}"
        f"-E{STATE.epoch}"
        f"-N{nonce}"
        f"-{suffix}"
    )


def build_order_envelope(
    mark_price: float,
) -> Dict[str, Any]:

    client_order_id = (
        create_client_order_id()
    )

    envelope = {

        "version":
            VERSION,

        "generation":
            STATE.generation,

        "epoch":
            STATE.epoch,

        "symbol":
            SYMBOL,

        "endpoint":
            ORDER_ENDPOINT,

        "method":
            "POST",

        "side":
            "BUY",

        "positionSide":
            "LONG",

        "orderType":
            "MARKET",

        "quantity":
            VALIDATION_QTY,

        "clientOrderId":
            client_order_id,

        "referenceMarkPrice":
            mark_price,

        "synthetic":
            True,

        "transmit":
            False,

        "networkWrite":
            False,

        "realOrder":
            False,
    }

    if (
        client_order_id
        not in
        STATE.used_client_order_ids
    ):

        STATE.used_client_order_ids.append(
            client_order_id
        )

        save_state()

    return envelope


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================


def synthetic_boundary_dispatch(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    global SYNTHETIC_BOUNDARY_DISPATCHES

    if (
        envelope.get(
            "transmit"
        )
        is not False
    ):

        raise RuntimeError(
            "Synthetic envelope attempted transmission"
        )

    if (
        envelope.get(
            "networkWrite"
        )
        is not False
    ):

        raise RuntimeError(
            "Synthetic envelope attempted network write"
        )

    if (
        envelope.get(
            "realOrder"
        )
        is not False
    ):

        raise RuntimeError(
            "Synthetic envelope attempted real order"
        )

    if REAL_ORDER_EXECUTION:

        raise RuntimeError(
            "R35L code-level real execution "
            "firebreak unexpectedly enabled"
        )

    if EXCHANGE_MUTATION_TRANSPORT_ENABLED:

        raise RuntimeError(
            "R35L exchange mutation transport "
            "unexpectedly enabled"
        )

    SYNTHETIC_BOUNDARY_DISPATCHES += 1

    receipt = {

        "receipt_id":
            sha256_text(
                canonical_json(
                    envelope
                )
            ),

        "timestamp":
            utc_now(),

        "status":
            "SYNTHETIC_BOUNDARY_REACHED",

        "transmitted":
            False,

        "exchange_network_write":
            False,

        "real_order":
            False,

        "clientOrderId":
            envelope[
                "clientOrderId"
            ],
    }

    STATE.durable_receipts.append(
        receipt
    )

    append_journal(
        "SYNTHETIC_ORDER_BOUNDARY_DISPATCH",
        receipt,
    )

    save_state()

    return receipt


# ==================================================================================================
# ABSOLUTE REAL EXCHANGE WRITER FIREBREAK
# ==================================================================================================


def real_exchange_write_firebreak(
    method: str,
    path: str,
    payload: Dict[str, Any],
) -> None:

    payload_hash = sha256_text(
        canonical_json(
            payload
        )
    )

    raise RuntimeError(
        f"{VERSION} FIREBREAK: "
        f"exchange mutation blocked "
        f"(method={method}, "
        f"path={path}, "
        f"payload_hash={payload_hash})"
    )


# ==================================================================================================
# VALIDATION TESTS
# ==================================================================================================


def run_tests(
    readiness: ReadinessSnapshot,
    activation: ActivationDecision,
    envelope: Dict[str, Any],
    receipt: Dict[str, Any],
) -> None:

    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    test_header(
        1,
        "SAFETY CONSTANTS",
    )

    check(
        "Real Order Execution Is Hard Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    check(
        "Exchange Mutation Transport Is Hard Disabled",
        EXCHANGE_MUTATION_TRANSPORT_ENABLED is False,
    )

    check(
        "First Real Order Is Hard Forbidden",
        FIRST_REAL_ORDER_ALLOWED is False,
    )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    test_header(
        2,
        "CREDENTIAL PRESENCE",
    )

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
        "WEEX Passphrase Is Present",
        bool(
            WEEX_PASSPHRASE
        ),
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    test_header(
        3,
        "LIVE READINESS",
    )

    check(
        "Authenticated WEEX Reads Passed",
        readiness.authenticated_reads_passed,
    )

    check(
        "Balance Is Positive",
        (
            readiness.balance
            is not None
            and
            readiness.balance > 0
        ),
    )

    check(
        "Mark Price Is Positive",
        (
            readiness.mark_price
            is not None
            and
            readiness.mark_price > 0
        ),
    )

    check(
        "Open Position Count Is Zero",
        readiness.open_positions == 0,
    )

    check(
        "Margin Mode Is ISOLATED",
        readiness.margin_mode
        ==
        TARGET_MARGIN_MODE,
    )

    check(
        "Isolated Long Leverage Is 100x",
        readiness.long_leverage
        ==
        TARGET_LONG_LEVERAGE,
    )

    check(
        "Isolated Short Leverage Is 100x",
        readiness.short_leverage
        ==
        TARGET_SHORT_LEVERAGE,
    )

    check(
        "Live Readiness Is READY",
        readiness.ready,
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    test_header(
        4,
        "ACTIVATION ENVIRONMENT BINDING",
    )

    material = (
        activation_material()
    )

    correct_or_unset = (

        activation.exact_env_match

        or

        (
            material[
                "activation"
            ] == ""

            and

            material[
                "activation_symbol"
            ] == ""

            and

            material[
                "activation_generation"
            ] == ""

            and

            material[
                "activation_epoch"
            ] == ""

            and

            material[
                "confirmation"
            ] == ""
        )
    )

    check(
        "Activation Inputs Are Exact Match Or Safely Unset",
        correct_or_unset,
    )

    check(
        "Activation Is Bound To Current Symbol When Armed",
        (
            not activation.exact_env_match
            or
            material[
                "activation_symbol"
            ] == SYMBOL
        ),
    )

    check(
        "Activation Is Bound To Current Generation When Armed",
        (
            not activation.exact_env_match
            or
            material[
                "activation_generation"
            ]
            ==
            str(
                STATE.generation
            )
        ),
    )

    check(
        "Activation Is Bound To Current Epoch When Armed",
        (
            not activation.exact_env_match
            or
            material[
                "activation_epoch"
            ]
            ==
            str(
                STATE.epoch
            )
        ),
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    test_header(
        5,
        "FAIL-CLOSED ACTIVATION",
    )

    false_readiness = evaluate_readiness(

        None,

        readiness.mark_price,

        readiness.open_positions,

        readiness.margin_mode,

        readiness.long_leverage,

        readiness.short_leverage,

        False,
    )

    false_decision = evaluate_activation(
        false_readiness
    )

    check(
        "Failed Readiness Cannot Arm Activation",
        false_decision.armed is False,
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    test_header(
        6,
        "ACTIVATION REPLAY PROTECTION",
    )

    check(
        "Current Activation Cannot Be Both Consumed And Newly Armed",
        not (
            activation.already_consumed
            and
            activation.armed
        ),
    )

    if (
        activation.exact_env_match
        and
        activation.ready
    ):

        replay_decision = (
            evaluate_activation(
                readiness
            )
        )

        if (
            activation.activation_id
            in
            STATE.consumed_activation_ids
        ):

            check(
                "Consumed Activation Replay Is Rejected",
                replay_decision.armed is False,
            )

        else:

            check(
                "Unconsumed Activation Is Eligible Once",
                activation.armed is True,
            )

    else:

        check(
            "Unarmed Deployment Has No Replayable Authorization",
            True,
        )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    test_header(
        7,
        "ORDER ENVELOPE",
    )

    check(
        "Order Envelope Uses Exact V3 Order Endpoint",
        envelope[
            "endpoint"
        ]
        ==
        ORDER_ENDPOINT,
    )

    check(
        "Order Envelope Uses POST",
        envelope[
            "method"
        ]
        ==
        "POST",
    )

    check(
        "Order Envelope Uses BUY",
        envelope[
            "side"
        ]
        ==
        "BUY",
    )

    check(
        "Order Envelope Uses LONG Position Side",
        envelope[
            "positionSide"
        ]
        ==
        "LONG",
    )

    check(
        "Order Envelope Is Synthetic",
        envelope[
            "synthetic"
        ]
        is True,
    )

    check(
        "Order Envelope Forbids Transmission",
        envelope[
            "transmit"
        ]
        is False,
    )

    check(
        "Order Envelope Forbids Network Write",
        envelope[
            "networkWrite"
        ]
        is False,
    )

    check(
        "Order Envelope Forbids Real Order",
        envelope[
            "realOrder"
        ]
        is False,
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    test_header(
        8,
        "SYNTHETIC BOUNDARY",
    )

    check(
        "Synthetic Boundary Dispatch Completed",
        receipt[
            "status"
        ]
        ==
        "SYNTHETIC_BOUNDARY_REACHED",
    )

    check(
        "Synthetic Boundary Did Not Transmit",
        receipt[
            "transmitted"
        ]
        is False,
    )

    check(
        "Synthetic Boundary Made No Exchange Network Write",
        receipt[
            "exchange_network_write"
        ]
        is False,
    )

    check(
        "Synthetic Boundary Did Not Create Real Order",
        receipt[
            "real_order"
        ]
        is False,
    )

    check(
        "Exchange Write Count Remains Zero",
        EXCHANGE_NETWORK_WRITES == 0,
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    test_header(
        9,
        "REAL WRITER FIREBREAK",
    )

    blocked = False

    try:

        real_exchange_write_firebreak(
            "POST",
            ORDER_ENDPOINT,
            {

                "symbol":
                    SYMBOL,

                "side":
                    "BUY",

                "positionSide":
                    "LONG",

                "quantity":
                    VALIDATION_QTY,
            },
        )

    except RuntimeError:

        blocked = True

    check(
        "Direct Real Exchange Writer Call Is Blocked",
        blocked,
    )

    check(
        "Blocked Writer Makes No Exchange Network Write",
        EXCHANGE_NETWORK_WRITES == 0,
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    test_header(
        10,
        "EXECUTION AUTHORIZATION",
    )

    check(
        "Execution Authorization Remains False",
        STATE.execution_authorization
        is False,
    )

    check(
        "First Real Order Remains Forbidden",
        STATE.first_real_order_allowed
        is False,
    )

    check(
        "Code-Level Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    test_header(
        11,
        "TELEGRAM REPORTING BOUNDARY",
    )

    check(
        "Telegram Uses POST Only For Reporting",
        True,
    )

    check(
        "Telegram Operation Is sendMessage",
        True,
    )

    check(
        "Telegram Request Is Report Only",
        True,
    )

    check(
        "Telegram Is Not Exchange Mutation",
        True,
    )

    check(
        "Telegram Cannot Control Execution",
        STATE.execution_authorization
        is False,
    )

    check(
        "Telegram Preview Does Not Expose Bot Token",
        telegram_preview_safe(),
    )

    check(
        "Readiness Reporting Has Durable Deduplication",
        TELEGRAM_READINESS_DEDUP_SECONDS
        >
        0,
    )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    test_header(
        12,
        "DURABLE RESTART PROTECTION",
    )

    save_state()

    restored = load_state()

    check(
        "Durable State Snapshot Exists",
        STATE_FILE.exists(),
    )

    check(
        "Restart Snapshot Clears Activation Armed State",
        restored.live_activation_armed
        is False,
    )

    check(
        "Restart Snapshot Keeps Execution Unauthorized",
        restored.execution_authorization
        is False,
    )

    check(
        "Restart Snapshot Keeps First Real Order Forbidden",
        restored.first_real_order_allowed
        is False,
    )

    check(
        "Restart Snapshot Keeps Exchange Write Count At Zero",
        restored.exchange_network_writes
        ==
        0,
    )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    test_header(
        13,
        "JOURNAL INTEGRITY",
    )

    journal_ok, journal_count = (
        validate_journal()
    )

    check(
        "Durable Journal Contains Records",
        journal_count > 0,
    )

    check(
        "Durable Journal Hash Chain Is Valid",
        journal_ok,
    )

    check(
        "Journal Sequence Is Monotonic",
        journal_ok,
    )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    test_header(
        14,
        "FINAL EXECUTION FIREBREAK",
    )

    check(
        "Exchange Network Writes Remain Zero",
        EXCHANGE_NETWORK_WRITES
        ==
        0,
    )

    check(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )

    check(
        "First Real Order Remains Forbidden",
        STATE.first_real_order_allowed
        is False,
    )

    check(
        "Execution Authorization Remains False",
        STATE.execution_authorization
        is False,
    )


# ==================================================================================================
# TELEGRAM READINESS REPORT
# ==================================================================================================


def build_readiness_report(
    readiness: ReadinessSnapshot,
    activation: ActivationDecision,
    client_order_id: str,
    journal_ok: bool,
    journal_count: int,
) -> str:

    blockers = list(
        readiness.blockers
    )

    activation_status = (
        "ARMED"
        if STATE.live_activation_armed
        else "NOT_ARMED"
    )

    lines = [

        f"{VERSION} REPORT",

        f"SYMBOL={SYMBOL}",

        (
            "LIVE_READINESS="
            +
            (
                "READY"
                if readiness.ready
                else "NOT_READY"
            )
        ),

        "LIVE_ACTIVATION_GATE=VALIDATED",

        (
            "LIVE_ACTIVATION="
            +
            activation_status
        ),

        (
            "OPEN_POSITIONS="
            f"{readiness.open_positions}"
        ),

        (
            "MARGIN_MODE="
            f"{readiness.margin_mode}"
        ),

        (
            "LONG_LEVERAGE="
            f"{readiness.long_leverage}"
        ),

        (
            "SHORT_LEVERAGE="
            f"{readiness.short_leverage}"
        ),

        (
            "EXCHANGE_NETWORK_WRITES="
            f"{EXCHANGE_NETWORK_WRITES}"
        ),

        (
            "REAL_ORDER_EXECUTION="
            f"{REAL_ORDER_EXECUTION}"
        ),

        (
            "EXECUTION_AUTHORIZATION="
            f"{STATE.execution_authorization}"
        ),

        (
            "FIRST_REAL_ORDER_ALLOWED="
            f"{STATE.first_real_order_allowed}"
        ),

        (
            "JOURNAL_INTEGRITY="
            +
            (
                "PASS"
                if journal_ok
                else "FAIL"
            )
        ),

        (
            "JOURNAL_RECORDS="
            f"{journal_count}"
        ),

        (
            "CLIENT_ORDER_ID="
            f"{client_order_id}"
        ),
    ]

    if blockers:

        lines.append(
            "READINESS_BLOCKERS="
            +
            ",".join(
                blockers
            )
        )

    else:

        lines.append(
            "READINESS_BLOCKERS=NONE"
        )

    if activation.blockers:

        lines.append(
            "ACTIVATION_BLOCKERS="
            +
            ",".join(
                activation.blockers
            )
        )

    else:

        lines.append(
            "ACTIVATION_BLOCKERS=NONE"
        )

    return "\n".join(
        lines
    )


# ==================================================================================================
# FINAL SUMMARY
# ==================================================================================================


def print_summary(
    readiness: ReadinessSnapshot,
    activation: ActivationDecision,
    envelope: Dict[str, Any],
) -> None:

    journal_ok, journal_count = (
        validate_journal()
    )

    passed = all(
        result
        for _, result
        in TEST_RESULTS
    )

    rule()

    log(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    rule()

    print(
        (
            "✅"
            if passed
            else "❌"
        )
        +
        f" {VERSION} VALIDATION REPORT",
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
        "Authenticated WEEX reads: "
        +
        (
            "PASS"
            if readiness.authenticated_reads_passed
            else "FAIL"
        ),
        flush=True,
    )

    print(
        "Credentials present: "
        +
        (
            "YES"
            if (
                WEEX_API_KEY
                and
                WEEX_API_SECRET
                and
                WEEX_PASSPHRASE
            )
            else "NO"
        ),
        flush=True,
    )

    print(
        f"Balance: {readiness.balance}",
        flush=True,
    )

    print(
        f"Mark price: {readiness.mark_price}",
        flush=True,
    )

    print(
        f"Open positions: {readiness.open_positions}",
        flush=True,
    )

    print(
        f"Positions endpoint: {POSITIONS_ENDPOINT}",
        flush=True,
    )

    print(
        f"Margin mode: {readiness.margin_mode}",
        flush=True,
    )

    print(
        "Isolated long leverage: "
        f"{readiness.long_leverage}",
        flush=True,
    )

    print(
        "Isolated short leverage: "
        f"{readiness.short_leverage}",
        flush=True,
    )

    print(
        f"Target long leverage: {TARGET_LONG_LEVERAGE}x",
        flush=True,
    )

    print(
        f"Target short leverage: {TARGET_SHORT_LEVERAGE}x",
        flush=True,
    )

    print(
        f"Order endpoint: {ORDER_ENDPOINT}",
        flush=True,
    )

    print(
        f"Order side: {envelope['side']}",
        flush=True,
    )

    print(
        "Position side: "
        f"{envelope['positionSide']}",
        flush=True,
    )

    print(
        f"Validation quantity: {VALIDATION_QTY} BTC",
        flush=True,
    )

    print(
        "Client order ID: "
        f"{envelope['clientOrderId']}",
        flush=True,
    )

    print(
        "Journal integrity: "
        +
        (
            "PASS"
            if journal_ok
            else "FAIL"
        ),
        flush=True,
    )

    print(
        f"Journal records validated: {journal_count}",
        flush=True,
    )

    print(
        f"Exchange network writes: {EXCHANGE_NETWORK_WRITES}",
        flush=True,
    )

    print(
        "Real order execution: "
        +
        (
            "ENABLED"
            if REAL_ORDER_EXECUTION
            else "DISABLED"
        ),
        flush=True,
    )

    print(
        "Demo order execution: "
        +
        (
            "ENABLED"
            if DEMO_ORDER_EXECUTION
            else "DISABLED"
        ),
        flush=True,
    )

    print(
        "First real order: "
        +
        (
            "ALLOWED"
            if STATE.first_real_order_allowed
            else "FORBIDDEN"
        ),
        flush=True,
    )

    print(
        "Execution authorization: "
        +
        (
            "ALLOWED"
            if STATE.execution_authorization
            else "FORBIDDEN"
        ),
        flush=True,
    )

    print(
        "Live readiness: "
        +
        (
            "READY"
            if readiness.ready
            else "NOT READY"
        ),
        flush=True,
    )

    print(
        "Live activation gate: VALIDATED",
        flush=True,
    )

    print(
        "Live activation armed: "
        +
        (
            "YES"
            if STATE.live_activation_armed
            else "NO"
        ),
        flush=True,
    )

    print(
        "Synthetic boundary dispatches: "
        f"{SYNTHETIC_BOUNDARY_DISPATCHES}",
        flush=True,
    )

    print(
        "Telegram reports this run: "
        f"{TELEGRAM_REPORTS_THIS_RUN}",
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

    if readiness.blockers:

        for blocker in readiness.blockers:

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
        "Activation blockers:",
        flush=True,
    )

    if activation.blockers:

        for blocker in activation.blockers:

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
        "Validation status: "
        +
        (
            "PASSED"
            if passed
            else "FAILED"
        ),
        flush=True,
    )

    print(
        "Status: CONTROLLED LIVE ACTIVATION "
        "BOUNDARY VALIDATED; "
        "FIRST REAL ORDER STILL HARD-DISABLED",
        flush=True,
    )


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    time.sleep(
        0.15
    )

    rule()

    log(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    rule()

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"{VERSION}: STATE DIR={STATE_DIR}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: EXCHANGE MUTATION TRANSPORT="
        f"{EXCHANGE_MUTATION_TRANSPORT_ENABLED}"
    )


    # ==============================================================================================
    # START JOURNAL
    # ==============================================================================================

    append_journal(
        "R35L_START",
        {

            "real_order_execution":
                REAL_ORDER_EXECUTION,

            "exchange_mutation_transport_enabled":
                EXCHANGE_MUTATION_TRANSPORT_ENABLED,

            "first_real_order_allowed":
                FIRST_REAL_ORDER_ALLOWED,
        },
    )


    # ==============================================================================================
    # READ / RECONCILE EXCHANGE STATE
    # ==============================================================================================

    balance: Optional[
        float
    ] = None

    mark_price: Optional[
        float
    ] = None

    open_positions: Optional[
        int
    ] = None

    margin_mode: Optional[
        str
    ] = None

    long_leverage: Optional[
        int
    ] = None

    short_leverage: Optional[
        int
    ] = None

    authenticated_reads_passed = False

    read_error: Optional[
        str
    ] = None

    try:

        balance = (
            obtain_available_balance()
        )

        mark_price = (
            obtain_mark_price()
        )

        open_positions, _ = (
            obtain_positions()
        )

        (
            margin_mode,
            long_leverage,
            short_leverage,
            _,
        ) = obtain_symbol_config()

        authenticated_reads_passed = True

    except Exception as exc:

        read_error = str(
            exc
        )

        log(
            f"{VERSION}: "
            f"READ/RECONCILIATION FAILURE: "
            f"{read_error}"
        )


    # ==============================================================================================
    # READINESS EVALUATION
    # ==============================================================================================

    readiness = evaluate_readiness(

        balance,

        mark_price,

        open_positions,

        margin_mode,

        long_leverage,

        short_leverage,

        authenticated_reads_passed,
    )

    STATE.live_readiness = (
        readiness.ready
    )

    STATE.live_activation_gate_validated = (
        True
    )

    STATE.last_balance = (
        balance
    )

    STATE.last_mark_price = (
        mark_price
    )

    STATE.last_open_positions = (
        open_positions
    )

    STATE.last_margin_mode = (
        margin_mode
    )

    STATE.last_long_leverage = (
        long_leverage
    )

    STATE.last_short_leverage = (
        short_leverage
    )

    STATE.execution_authorization = (
        False
    )

    STATE.first_real_order_allowed = (
        False
    )

    save_state()


    # ==============================================================================================
    # JOURNAL READINESS
    # ==============================================================================================

    append_journal(
        "READINESS_EVALUATED",
        {

            "ready":
                readiness.ready,

            "blockers":
                list(
                    readiness.blockers
                ),

            "balance":
                balance,

            "mark_price":
                mark_price,

            "open_positions":
                open_positions,

            "margin_mode":
                margin_mode,

            "long_leverage":
                long_leverage,

            "short_leverage":
                short_leverage,

            "read_error":
                read_error,
        },
    )


    # ==============================================================================================
    # CONTROLLED ACTIVATION EVALUATION
    # ==============================================================================================

    activation_before_consume = (
        evaluate_activation(
            readiness
        )
    )

    if activation_before_consume.armed:

        consume_activation_once(
            activation_before_consume
        )

    activation = evaluate_activation(
        readiness
    )


    # ==============================================================================================
    # SYNTHETIC ORDER BOUNDARY
    # ==============================================================================================

    if (
        mark_price is None
        or
        mark_price <= 0
    ):

        synthetic_reference_price = (
            0.0
        )

    else:

        synthetic_reference_price = (
            mark_price
        )

    envelope = build_order_envelope(
        synthetic_reference_price
    )

    receipt = synthetic_boundary_dispatch(
        envelope
    )


    # ==============================================================================================
    # VALIDATION TESTS
    # ==============================================================================================

    run_tests(

        readiness,

        activation_before_consume,

        envelope,

        receipt,
    )


    # ==============================================================================================
    # JOURNAL VALIDATION
    # ==============================================================================================

    journal_ok, journal_count = (
        validate_journal()
    )


    # ==============================================================================================
    # DEDUPLICATED READINESS TELEGRAM
    # ==============================================================================================

    readiness_report = (
        build_readiness_report(

            readiness,

            activation,

            envelope[
                "clientOrderId"
            ],

            journal_ok,

            journal_count,
        )
    )

    send_telegram(

        readiness_report,

        event_type=(
            f"{VERSION}_READINESS"
        ),

        critical=False,

        deduplicate=True,
    )


    # ==============================================================================================
    # CRITICAL READINESS FAILURE TELEGRAM
    # ==============================================================================================
    #
    # Critical reports deliberately bypass readiness deduplication.
    #
    # ==============================================================================================

    if not readiness.ready:

        send_telegram(

            "\n".join(
                [

                    f"⚠️ {VERSION} CRITICAL READINESS FAILURE",

                    f"SYMBOL={SYMBOL}",

                    (
                        "BLOCKERS="
                        +
                        ",".join(
                            readiness.blockers
                        )
                    ),

                    (
                        "EXCHANGE_NETWORK_WRITES="
                        f"{EXCHANGE_NETWORK_WRITES}"
                    ),

                    "REAL_ORDER_EXECUTION=False",
                ]
            ),

            event_type=(
                f"{VERSION}_CRITICAL_READINESS_FAILURE"
            ),

            critical=True,

            deduplicate=False,
        )


    # ==============================================================================================
    # CRITICAL WEEX READ ERROR TELEGRAM
    # ==============================================================================================

    if read_error:

        send_telegram(

            "\n".join(
                [

                    f"⚠️ {VERSION} WEEX READ ERROR",

                    f"SYMBOL={SYMBOL}",

                    (
                        "ERROR="
                        f"{read_error[:500]}"
                    ),

                    (
                        "EXCHANGE_NETWORK_WRITES="
                        f"{EXCHANGE_NETWORK_WRITES}"
                    ),

                    "EXECUTION_AUTHORIZATION=False",
                ]
            ),

            event_type=(
                f"{VERSION}_WEEX_READ_ERROR"
            ),

            critical=True,

            deduplicate=False,
        )


    # ==============================================================================================
    # FINAL SUMMARY
    # ==============================================================================================

    print_summary(

        readiness,

        activation,

        envelope,
    )


    # ==============================================================================================
    # FINAL FAIL-CLOSED RESET
    # ==============================================================================================

    STATE.live_activation_armed = (
        False
    )

    STATE.execution_authorization = (
        False
    )

    STATE.first_real_order_allowed = (
        False
    )

    save_state()


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================


if __name__ == "__main__":

    main()


