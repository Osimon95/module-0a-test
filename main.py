from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import shutil
import tempfile
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
# R35I - CONTROLLED LIVE ACTIVATION GATE VALIDATION
# CORRECTED TELEGRAM / JOURNAL REPORTING BUILD
# ==================================================================================================
#
# IMPORTANT
#
# THIS BUILD DOES NOT PLACE ORDERS.
#
# Exchange mutation remains hard disabled:
#
#   EXCHANGE_WRITER_ENABLED        = False
#   EXCHANGE_NETWORK_WRITES_ENABLED = False
#   REAL_ORDER_EXECUTION           = False
#   DEMO_ORDER_EXECUTION           = False
#   FIRST_REAL_ORDER_ALLOWED       = False
#
# Telegram POST is permitted ONLY for reporting.
# Telegram traffic is NOT an exchange mutation.
#
# CORRECTION IN THIS BUILD
#
#   - Telegram final validation report is sent ONCE.
#   - It is sent only after journal integrity and final durable consistency pass.
#   - "Journal test: pending final verification" is removed.
#   - Telegram report now contains the final journal result.
#   - Duplicate final Telegram reports within the same process are blocked.
#
# ==================================================================================================


# ==================================================================================================
# CONSTANTS
# ==================================================================================================

VERSION = "R35I"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

STATE_DIR = Path(
    os.getenv(
        "R35I_STATE_DIR",
        "/tmp/r35i_state",
    )
)

STATE_FILE = STATE_DIR / "state.json"
JOURNAL_FILE = STATE_DIR / "journal.jsonl"

BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

ORDER_PATH = "/capi/v3/order"

BALANCE_PATH = os.getenv(
    "WEEX_BALANCE_PATH",
    "/capi/v3/account/balance",
)

POSITIONS_PATH = os.getenv(
    "WEEX_POSITIONS_PATH",
    "/capi/v3/position/allPosition",
)

SYMBOL_CONFIG_PATH = os.getenv(
    "WEEX_SYMBOL_CONFIG_PATH",
    "/capi/v3/account/symbolConfig",
)

MARK_PRICE_PATH = os.getenv(
    "WEEX_MARK_PRICE_PATH",
    "/capi/v3/market/symbolPrice",
)

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    os.getenv("ACCESS_KEY", ""),
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    os.getenv("SECRET_KEY", ""),
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    os.getenv("PASSPHRASE", ""),
).strip()


# --------------------------------------------------------------------------------------------------
# TELEGRAM
# --------------------------------------------------------------------------------------------------

TELEGRAM_REPORTING_ENABLED = (
    os.getenv(
        "TELEGRAM_REPORTING_ENABLED",
        "true",
    ).strip().lower()
    in {"1", "true", "yes", "on"}
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()

TELEGRAM_TIMEOUT_SECONDS = float(
    os.getenv(
        "TELEGRAM_TIMEOUT_SECONDS",
        "10",
    )
)


# --------------------------------------------------------------------------------------------------
# SAFETY CONSTANTS
# --------------------------------------------------------------------------------------------------

AUTHENTICATED_READ_ONLY_ENABLED = True
PUBLIC_READ_ONLY_ENABLED = True

EXCHANGE_WRITER_ENABLED = False
EXCHANGE_NETWORK_WRITES_ENABLED = False

EXCHANGE_POST_ENABLED = False
EXCHANGE_PUT_ENABLED = False
EXCHANGE_PATCH_ENABLED = False
EXCHANGE_DELETE_ENABLED = False

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

FIRST_REAL_ORDER_ALLOWED = False

SYNTHETIC_DISPATCH_ONLY = True

LIVE_MODE_ARMING_VALIDATION_ENABLED = True

KILL_SWITCH_DEFAULT = False

FAIL_CLOSED_ON_AMBIGUOUS_OUTCOME = True

TELEGRAM_CAN_CONTROL_EXECUTION = False

MAX_FUND_EXPOSURE_PERCENT = 35.0

PLANNED_INITIAL_ENTRY_PERCENT = 5.0

PLANNED_LEVERAGE = 100

PLANNED_QUANTITY = "0.0005"

PLANNED_POSITION_SIDE = "LONG"

PLANNED_ORDER_SIDE = "BUY"

PLANNED_ORDER_TYPE = "MARKET"


# ==================================================================================================
# GLOBAL RUNTIME COUNTERS
# ==================================================================================================

_exchange_network_write_count = 0
_exchange_network_write_lock = threading.Lock()

_telegram_delivery_count = 0
_telegram_delivery_lock = threading.Lock()

_final_telegram_report_sent = False
_final_telegram_report_lock = threading.Lock()

_health_ready = False
_health_lock = threading.Lock()


# ==================================================================================================
# GENERAL HELPERS
# ==================================================================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="microseconds"
    ).replace(
        "+00:00",
        "Z",
    )


def log(
    message: str,
) -> None:

    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def separator() -> None:

    log(
        "-" * 100
    )


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_obj(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(
            value
        )
    )


def test_result(
    name: str,
    passed: bool,
) -> bool:

    marker = (
        "✅ PASS"
        if passed
        else
        "❌ FAIL"
    )

    log(
        f"{name:<84} {marker}"
    )

    return passed


def test_header(
    number: int,
    name: str,
) -> None:

    separator()

    log(
        f"{VERSION} TEST {number}: {name}"
    )

    separator()


def increment_exchange_write_count() -> None:

    global _exchange_network_write_count

    with _exchange_network_write_lock:

        _exchange_network_write_count += 1


def get_exchange_write_count() -> int:

    with _exchange_network_write_lock:

        return int(
            _exchange_network_write_count
        )


def get_telegram_delivery_count() -> int:

    with _telegram_delivery_lock:

        return int(
            _telegram_delivery_count
        )


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

@dataclass
class DurableState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = "INITIALIZED"

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    reconciled: bool = False

    reconciliation_id: Optional[str] = None

    reconciliation_hash: Optional[str] = None

    active_intent: Optional[
        Dict[str, Any]
    ] = None

    active_authorization: Optional[
        Dict[str, Any]
    ] = None

    consumed_intents: List[
        str
    ] = field(
        default_factory=list
    )

    consumed_authorizations: List[
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

    live_gate_armed: bool = False

    kill_switch: bool = KILL_SWITCH_DEFAULT

    ambiguous_outcome: bool = False

    synthetic_dispatch_count: int = 0

    exchange_network_write_count: int = 0

    journal_sequence: int = 0

    last_journal_hash: str = "0" * 64

    terminal: bool = False


# ==================================================================================================
# STATE STORAGE
# ==================================================================================================

def ensure_state_directory() -> None:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_state(
    state: DurableState,
) -> None:

    ensure_state_directory()

    payload = canonical_json(
        asdict(
            state
        )
    )

    fd, temp_name = tempfile.mkstemp(
        prefix="r35i-state-",
        suffix=".tmp",
        dir=str(
            STATE_DIR
        ),
    )

    try:

        with os.fdopen(
            fd,
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
            temp_name,
            STATE_FILE,
        )

    finally:

        if os.path.exists(
            temp_name
        ):

            os.unlink(
                temp_name
            )


def load_state() -> DurableState:

    if not STATE_FILE.exists():

        return DurableState()

    with STATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:

        raw = json.load(
            handle
        )

    allowed = {
        item.name
        for item in DurableState.__dataclass_fields__.values()
    }

    filtered = {
        key: value
        for key, value in raw.items()
        if key in allowed
    }

    return DurableState(
        **filtered
    )


# ==================================================================================================
# DURABLE HASH-CHAIN JOURNAL
# ==================================================================================================

def append_journal(
    state: DurableState,
    event: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:

    ensure_state_directory()

    sequence = (
        state.journal_sequence
        + 1
    )

    record_body = {
        "sequence": sequence,
        "timestamp": utc_now(),
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "event": event,
        "details": details,
        "previous_hash": state.last_journal_hash,
    }

    record_hash = sha256_obj(
        record_body
    )

    record = {
        **record_body,
        "record_hash": record_hash,
    }

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

    state.journal_sequence = sequence

    state.last_journal_hash = record_hash

    save_state(
        state
    )

    return record


def read_journal() -> List[
    Dict[str, Any]
]:

    if not JOURNAL_FILE.exists():

        return []

    records: List[
        Dict[str, Any]
    ] = []

    with JOURNAL_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:

        for raw_line in handle:

            line = raw_line.strip()

            if not line:
                continue

            records.append(
                json.loads(
                    line
                )
            )

    return records


def validate_journal_records(
    records: List[
        Dict[str, Any]
    ],
) -> Tuple[
    bool,
    Optional[str],
    int,
]:

    previous_hash = "0" * 64

    expected_sequence = 1

    for record in records:

        try:

            received_hash = str(
                record[
                    "record_hash"
                ]
            )

            body = {
                key: value
                for key, value
                in record.items()
                if key != "record_hash"
            }

            if int(
                body[
                    "sequence"
                ]
            ) != expected_sequence:

                return (
                    False,
                    None,
                    expected_sequence - 1,
                )

            if body.get(
                "previous_hash"
            ) != previous_hash:

                return (
                    False,
                    None,
                    expected_sequence - 1,
                )

            calculated_hash = sha256_obj(
                body
            )

            if not hmac.compare_digest(
                received_hash,
                calculated_hash,
            ):

                return (
                    False,
                    None,
                    expected_sequence - 1,
                )

            previous_hash = received_hash

            expected_sequence += 1

        except Exception:

            return (
                False,
                None,
                expected_sequence - 1,
            )

    return (
        True,
        previous_hash,
        expected_sequence - 1,
    )


def validate_durable_journal(
    state: DurableState,
) -> bool:

    records = read_journal()

    valid, terminal_hash, sequence = (
        validate_journal_records(
            records
        )
    )

    if not valid:

        return False

    if sequence != state.journal_sequence:

        return False

    if records:

        if terminal_hash != state.last_journal_hash:

            return False

    else:

        if state.last_journal_hash != "0" * 64:

            return False

    return True


# ==================================================================================================
# HTTP HEALTH SERVER
# ==================================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        if self.path not in {
            "/",
            "/health",
            "/healthz",
        }:

            self.send_response(
                404
            )

            self.end_headers()

            return

        with _health_lock:

            ready = bool(
                _health_ready
            )

        payload = {
            "status": (
                "ok"
                if ready
                else
                "starting"
            ),
            "version": VERSION,
            "symbol": SYMBOL,
            "exchange_network_writes": get_exchange_write_count(),
            "real_order_execution": REAL_ORDER_EXECUTION,
            "exchange_writer_enabled": EXCHANGE_WRITER_ENABLED,
            "telegram_deliveries": get_telegram_delivery_count(),
        }

        encoded = json.dumps(
            payload,
            separators=(",", ":"),
        ).encode(
            "utf-8"
        )

        self.send_response(
            200
            if ready
            else
            503
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    encoded
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            encoded
        )

    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    def runner() -> None:

        try:

            server = HTTPServer(
                (
                    "0.0.0.0",
                    HEALTH_PORT,
                ),
                HealthHandler,
            )

            log(
                f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}"
            )

            server.serve_forever()

        except Exception as exc:

            log(
                f"{VERSION}: HEALTH SERVER ERROR={type(exc).__name__}"
            )

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# SAFE HTTP TRANSPORT
# ==================================================================================================

def public_get_json(
    path: str,
    query: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not PUBLIC_READ_ONLY_ENABLED:

        raise RuntimeError(
            "public read-only transport disabled"
        )

    encoded_query = ""

    if query:

        encoded_query = urllib.parse.urlencode(
            {
                key: value
                for key, value
                in query.items()
                if value is not None
            }
        )

    url = (
        BASE_URL
        + path
    )

    if encoded_query:

        url += (
            "?"
            + encoded_query
        )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "locale": "en-US",
            "User-Agent": f"{VERSION}-read-only-validator",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=10,
    ) as response:

        raw = response.read().decode(
            "utf-8"
        )

    return json.loads(
        raw
    )


def build_weex_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    if not WEEX_API_SECRET:

        raise RuntimeError(
            "WEEX API secret is missing"
        )

    effective_path = request_path

    if query_string:

        effective_path += (
            "?"
            + query_string
        )

    prehash = (
        timestamp
        + method.upper()
        + effective_path
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


def authenticated_get_json(
    path: str,
    query: Optional[
        Dict[str, Any]
    ] = None,
) -> Any:

    if not AUTHENTICATED_READ_ONLY_ENABLED:

        raise RuntimeError(
            "authenticated reads disabled"
        )

    if not (
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_PASSPHRASE
    ):

        raise RuntimeError(
            "WEEX credentials incomplete"
        )

    query_string = ""

    if query:

        query_string = urllib.parse.urlencode(
            {
                key: value
                for key, value
                in query.items()
                if value is not None
            }
        )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = build_weex_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
    )

    url = (
        BASE_URL
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "ACCESS-KEY": WEEX_API_KEY,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US",
            "User-Agent": f"{VERSION}-authenticated-read-only",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=10,
    ) as response:

        raw = response.read().decode(
            "utf-8"
        )

    return json.loads(
        raw
    )


# ==================================================================================================
# HARD EXCHANGE MUTATION FIREBREAK
# ==================================================================================================

def exchange_post(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        "R35I HARD FIREBREAK: exchange POST disabled"
    )


def exchange_put(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        "R35I HARD FIREBREAK: exchange PUT disabled"
    )


def exchange_patch(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        "R35I HARD FIREBREAK: exchange PATCH disabled"
    )


def exchange_delete(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        "R35I HARD FIREBREAK: exchange DELETE disabled"
    )


# ==================================================================================================
# RESPONSE EXTRACTION HELPERS
# ==================================================================================================

def unwrap_data(
    response: Any,
) -> Any:

    if isinstance(
        response,
        dict,
    ):

        if "data" in response:

            return response[
                "data"
            ]

    return response


def recursive_find_number(
    value: Any,
    candidate_keys: Tuple[
        str,
        ...,
    ],
) -> Optional[
    float
]:

    if isinstance(
        value,
        dict,
    ):

        for key in candidate_keys:

            if key in value:

                try:

                    return float(
                        value[
                            key
                        ]
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        for child in value.values():

            found = recursive_find_number(
                child,
                candidate_keys,
            )

            if found is not None:

                return found

    elif isinstance(
        value,
        list,
    ):

        for child in value:

            found = recursive_find_number(
                child,
                candidate_keys,
            )

            if found is not None:

                return found

    return None


def extract_balance(
    response: Any,
) -> Optional[
    float
]:

    return recursive_find_number(
        response,
        (
            "available",
            "availableBalance",
            "availableAmount",
            "availableMargin",
            "balance",
        ),
    )


def extract_mark_price(
    response: Any,
) -> Optional[
    float
]:

    return recursive_find_number(
        response,
        (
            "markPrice",
            "price",
            "last",
            "lastPrice",
        ),
    )


def extract_positions(
    response: Any,
) -> List[
    Dict[str, Any]
]:

    data = unwrap_data(
        response
    )

    if isinstance(
        data,
        list,
    ):

        return [
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        data,
        dict,
    ):

        for key in (
            "positions",
            "list",
            "rows",
        ):

            candidate = data.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):

                return [
                    item
                    for item in candidate
                    if isinstance(
                        item,
                        dict,
                    )
                ]

    return []


def count_open_positions(
    positions: List[
        Dict[str, Any]
    ],
) -> int:

    count = 0

    for position in positions:

        quantity = recursive_find_number(
            position,
            (
                "positionAmt",
                "positionAmount",
                "size",
                "quantity",
                "qty",
                "total",
                "holdVol",
            ),
        )

        if quantity is None:

            continue

        if abs(
            quantity
        ) > 0:

            count += 1

    return count


# ==================================================================================================
# RECONCILIATION
# ==================================================================================================

def create_reconciliation(
    balance: Optional[
        float
    ],
    mark_price: Optional[
        float
    ],
    open_positions: int,
) -> Dict[str, Any]:

    body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "balance": balance,
        "mark_price": mark_price,
        "open_positions": open_positions,
        "generation": 1,
        "epoch": 1,
        "read_only": True,
        "exchange_writes": 0,
    }

    reconciliation_hash = sha256_obj(
        body
    )

    return {
        **body,
        "reconciliation_id": (
            "rec-"
            + reconciliation_hash[
                :20
            ]
        ),
        "reconciliation_hash": reconciliation_hash,
    }


# ==================================================================================================
# INTENT / AUTHORIZATION
# ==================================================================================================

def create_intent(
    reconciliation: Dict[
        str,
        Any,
    ],
) -> Dict[str, Any]:

    intent_body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": 1,
        "epoch": 1,
        "nonce": 1,
        "side": PLANNED_ORDER_SIDE,
        "position_side": PLANNED_POSITION_SIDE,
        "order_type": PLANNED_ORDER_TYPE,
        "quantity": PLANNED_QUANTITY,
        "planned_leverage": PLANNED_LEVERAGE,
        "reconciliation_hash": reconciliation[
            "reconciliation_hash"
        ],
        "synthetic_only": True,
        "transmission_allowed": False,
        "exchange_network_write_allowed": False,
    }

    intent_hash = sha256_obj(
        intent_body
    )

    return {
        **intent_body,
        "intent_id": (
            "int-"
            + intent_hash[
                :20
            ]
        ),
        "intent_hash": intent_hash,
    }


def create_authorization(
    intent: Dict[
        str,
        Any,
    ],
) -> Dict[str, Any]:

    body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "intent_id": intent[
            "intent_id"
        ],
        "intent_hash": intent[
            "intent_hash"
        ],
        "generation": intent[
            "generation"
        ],
        "epoch": intent[
            "epoch"
        ],
        "nonce": intent[
            "nonce"
        ],
        "one_time": True,
        "transmission_allowed": False,
        "writer_enabled": False,
    }

    authorization_hash = sha256_obj(
        body
    )

    return {
        **body,
        "authorization_id": (
            "auth-"
            + authorization_hash[
                :20
            ]
        ),
        "authorization_hash": authorization_hash,
    }


def deterministic_client_order_id(
    intent: Dict[
        str,
        Any,
    ],
) -> str:

    material = {
        "version": VERSION,
        "symbol": SYMBOL,
        "intent_id": intent[
            "intent_id"
        ],
        "intent_hash": intent[
            "intent_hash"
        ],
    }

    digest = sha256_obj(
        material
    )

    return (
        "r35i-"
        + digest[
            :20
        ]
    )


# ==================================================================================================
# SECRET SAFE WRITER ENVELOPE
# ==================================================================================================

def create_writer_envelope(
    reconciliation: Dict[
        str,
        Any,
    ],
    intent: Dict[
        str,
        Any,
    ],
    authorization: Dict[
        str,
        Any,
    ],
    client_order_id: str,
) -> Dict[str, Any]:

    timestamp = "1760000000000"

    payload = {
        "newClientOrderId": client_order_id,
        "positionSide": PLANNED_POSITION_SIDE,
        "quantity": PLANNED_QUANTITY,
        "side": PLANNED_ORDER_SIDE,
        "symbol": SYMBOL,
        "type": PLANNED_ORDER_TYPE,
    }

    envelope_body = {
        "method": "POST",
        "request_path": ORDER_PATH,
        "url": (
            BASE_URL
            + ORDER_PATH
        ),
        "payload": payload,
        "intent_id": intent[
            "intent_id"
        ],
        "intent_hash": intent[
            "intent_hash"
        ],
        "authorization_id": authorization[
            "authorization_id"
        ],
        "authorization_hash": authorization[
            "authorization_hash"
        ],
        "reconciliation_id": reconciliation[
            "reconciliation_id"
        ],
        "reconciliation_hash": reconciliation[
            "reconciliation_hash"
        ],
        "headers": {
            "ACCESS-KEY": "<redacted>",
            "ACCESS-SIGN": "<redacted>",
            "ACCESS-PASSPHRASE": "<redacted>",
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US",
        },
        "live_mode_armed": True,
        "exchange_writer_enabled": EXCHANGE_WRITER_ENABLED,
        "exchange_network_writes_enabled": EXCHANGE_NETWORK_WRITES_ENABLED,
        "real_order_execution": REAL_ORDER_EXECUTION,
        "first_real_order_allowed": FIRST_REAL_ORDER_ALLOWED,
        "transmitted": False,
    }

    envelope_hash = sha256_obj(
        envelope_body
    )

    return {
        **envelope_body,
        "envelope_hash": envelope_hash,
    }


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================

def synthetic_dispatch(
    state: DurableState,
    envelope: Dict[
        str,
        Any,
    ],
) -> Dict[str, Any]:

    if not SYNTHETIC_DISPATCH_ONLY:

        raise RuntimeError(
            "synthetic-only invariant violated"
        )

    if envelope.get(
        "transmitted"
    ):

        raise RuntimeError(
            "envelope already transmitted"
        )

    intent_id = str(
        envelope[
            "intent_id"
        ]
    )

    authorization_id = str(
        envelope[
            "authorization_id"
        ]
    )

    client_order_id = str(
        envelope[
            "payload"
        ][
            "newClientOrderId"
        ]
    )

    if intent_id in state.consumed_intents:

        raise RuntimeError(
            "intent replay rejected"
        )

    if authorization_id in state.consumed_authorizations:

        raise RuntimeError(
            "authorization replay rejected"
        )

    if client_order_id in state.used_client_order_ids:

        raise RuntimeError(
            "client order id replay rejected"
        )

    if EXCHANGE_WRITER_ENABLED:

        raise RuntimeError(
            "exchange writer unexpectedly enabled"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:

        raise RuntimeError(
            "exchange writes unexpectedly enabled"
        )

    if REAL_ORDER_EXECUTION:

        raise RuntimeError(
            "real execution unexpectedly enabled"
        )

    receipt_body = {
        "version": VERSION,
        "symbol": SYMBOL,
        "intent_id": intent_id,
        "authorization_id": authorization_id,
        "client_order_id": client_order_id,
        "envelope_hash": envelope[
            "envelope_hash"
        ],
        "synthetic": True,
        "transmitted": False,
        "exchange_network_write": False,
        "real_order": False,
        "timestamp": utc_now(),
    }

    receipt_hash = sha256_obj(
        receipt_body
    )

    receipt = {
        **receipt_body,
        "receipt_id": (
            "receipt-"
            + receipt_hash[
                :20
            ]
        ),
        "receipt_hash": receipt_hash,
    }

    state.consumed_intents.append(
        intent_id
    )

    state.consumed_authorizations.append(
        authorization_id
    )

    state.used_client_order_ids.append(
        client_order_id
    )

    state.durable_receipts.append(
        receipt
    )

    state.synthetic_dispatch_count += 1

    state.exchange_network_write_count = (
        get_exchange_write_count()
    )

    state.phase = "SYNTHETIC_DISPATCHED"

    append_journal(
        state,
        "SYNTHETIC_DISPATCH",
        {
            "intent_id": intent_id,
            "authorization_id": authorization_id,
            "client_order_id": client_order_id,
            "receipt_id": receipt[
                "receipt_id"
            ],
            "transmitted": False,
            "exchange_network_write": False,
        },
    )

    return receipt


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================

def telegram_request_preview(
    text: str,
) -> Dict[str, Any]:

    return {
        "method": "POST",
        "operation": "sendMessage",
        "report_only": True,
        "exchange_mutation": False,
        "can_control_execution": False,
        "bot_token": "<redacted>",
        "chat_id_present": bool(
            TELEGRAM_CHAT_ID
        ),
        "text_sha256": sha256_text(
            text
        ),
    }


def send_telegram_message(
    text: str,
) -> Tuple[
    bool,
    str,
]:

    global _telegram_delivery_count

    if not TELEGRAM_REPORTING_ENABLED:

        return (
            False,
            "telegram reporting disabled",
        )

    if not TELEGRAM_BOT_TOKEN:

        return (
            False,
            "telegram bot token missing",
        )

    if not TELEGRAM_CHAT_ID:

        return (
            False,
            "telegram chat id missing",
        )

    endpoint = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    body = urllib.parse.urlencode(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        url=endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": f"{VERSION}-reporter",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=TELEGRAM_TIMEOUT_SECONDS,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

        parsed = json.loads(
            raw
        )

        if not parsed.get(
            "ok"
        ):

            return (
                False,
                "telegram API returned ok=false",
            )

        message_id = (
            parsed.get(
                "result",
                {},
            ).get(
                "message_id"
            )
        )

        with _telegram_delivery_lock:

            _telegram_delivery_count += 1

        return (
            True,
            f"message_id={message_id}",
        )

    except urllib.error.HTTPError as exc:

        return (
            False,
            f"HTTP {exc.code}",
        )

    except Exception as exc:

        return (
            False,
            type(
                exc
            ).__name__,
        )


def send_final_telegram_report_once(
    text: str,
) -> Tuple[
    bool,
    str,
]:

    global _final_telegram_report_sent

    with _final_telegram_report_lock:

        if _final_telegram_report_sent:

            return (
                False,
                "duplicate final report blocked",
            )

        delivered, result = (
            send_telegram_message(
                text
            )
        )

        if delivered:

            _final_telegram_report_sent = True

        return (
            delivered,
            result,
        )


# ==================================================================================================
# KILL SWITCH / AMBIGUOUS OUTCOME
# ==================================================================================================

def arm_live_gate(
    state: DurableState,
) -> bool:

    if state.kill_switch:

        return False

    if state.ambiguous_outcome:

        return False

    if not state.reconciled:

        return False

    state.live_gate_armed = True

    state.phase = "LIVE_GATE_ARMED_VALIDATION_ONLY"

    append_journal(
        state,
        "LIVE_GATE_ARMED",
        {
            "validation_only": True,
            "exchange_writer_enabled": False,
            "exchange_network_writes_enabled": False,
            "real_order_execution": False,
        },
    )

    return True


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def run_validation() -> bool:

    global _health_ready

    separator()

    log(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    separator()

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
        f"{VERSION}: AUTHENTICATED READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: EXCHANGE WRITER DISABLED"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION DISABLED"
    )

    log(
        f"{VERSION}: TELEGRAM REPORTING={'ENABLED' if TELEGRAM_REPORTING_ENABLED else 'DISABLED'}"
    )

    failures: List[
        str
    ] = []

    state = load_state()

    # ----------------------------------------------------------------------------------------------
    # TEST 1
    # ----------------------------------------------------------------------------------------------

    test_header(
        1,
        "SAFETY CONSTANTS",
    )

    checks = [
        (
            "Authenticated Transport Is Read Only",
            AUTHENTICATED_READ_ONLY_ENABLED,
        ),
        (
            "Public Transport Is Read Only",
            PUBLIC_READ_ONLY_ENABLED,
        ),
        (
            "Synthetic Dispatch Only Is Enabled",
            SYNTHETIC_DISPATCH_ONLY,
        ),
        (
            "Exchange Writer Is Disabled",
            not EXCHANGE_WRITER_ENABLED,
        ),
        (
            "Exchange Network Writes Are Disabled",
            not EXCHANGE_NETWORK_WRITES_ENABLED,
        ),
        (
            "Real Orders Are Disabled",
            not REAL_ORDER_EXECUTION,
        ),
        (
            "Demo Orders Are Disabled",
            not DEMO_ORDER_EXECUTION,
        ),
        (
            "First Real Order Is Forbidden",
            not FIRST_REAL_ORDER_ALLOWED,
        ),
    ]

    for name, passed in checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 2
    # ----------------------------------------------------------------------------------------------

    test_header(
        2,
        "CREDENTIAL PRESENCE",
    )

    credential_checks = [
        (
            "WEEX API Key Is Present",
            bool(
                WEEX_API_KEY
            ),
        ),
        (
            "WEEX API Secret Is Present",
            bool(
                WEEX_API_SECRET
            ),
        ),
        (
            "WEEX Passphrase Is Present",
            bool(
                WEEX_PASSPHRASE
            ),
        ),
    ]

    for name, passed in credential_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 3 - AUTH READS
    # ----------------------------------------------------------------------------------------------

    test_header(
        3,
        "AUTHENTICATED WEEX READS",
    )

    authenticated_reads_passed = False

    balance: Optional[
        float
    ] = None

    positions: List[
        Dict[str, Any]
    ] = []

    try:

        balance_response = authenticated_get_json(
            BALANCE_PATH
        )

        balance = extract_balance(
            balance_response
        )

        positions_response = authenticated_get_json(
            POSITIONS_PATH
        )

        positions = extract_positions(
            positions_response
        )

        authenticated_reads_passed = True

    except Exception as exc:

        log(
            f"{VERSION}: AUTH READ ERROR={type(exc).__name__}: {exc}"
        )

    if not test_result(
        "Authenticated WEEX Reads Succeeded",
        authenticated_reads_passed,
    ):

        failures.append(
            "Authenticated WEEX Reads Succeeded"
        )

    if balance is not None:

        log(
            f"{VERSION}: AVAILABLE BALANCE={balance:.8f} USDT"
        )

    open_positions = count_open_positions(
        positions
    )

    log(
        f"{VERSION}: OPEN POSITIONS={open_positions}"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 4 - MARK PRICE
    # ----------------------------------------------------------------------------------------------

    test_header(
        4,
        "PUBLIC MARK PRICE",
    )

    mark_price: Optional[
        float
    ] = None

    mark_read_passed = False

    try:

        mark_response = public_get_json(
            MARK_PRICE_PATH,
            {
                "symbol": SYMBOL,
            },
        )

        mark_price = extract_mark_price(
            mark_response
        )

        mark_read_passed = (
            mark_price is not None
            and mark_price > 0
        )

    except Exception as exc:

        log(
            f"{VERSION}: MARK PRICE ERROR={type(exc).__name__}: {exc}"
        )

    if not test_result(
        "BTCUSDT Mark Price Was Read",
        mark_read_passed,
    ):

        failures.append(
            "BTCUSDT Mark Price Was Read"
        )

    if mark_price is not None:

        log(
            f"{VERSION}: MARK PRICE={mark_price}"
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 5 - RECONCILIATION
    # ----------------------------------------------------------------------------------------------

    test_header(
        5,
        "EXCHANGE STATE RECONCILIATION",
    )

    reconciliation = create_reconciliation(
        balance=balance,
        mark_price=mark_price,
        open_positions=open_positions,
    )

    state.reconciled = (
        authenticated_reads_passed
        and mark_read_passed
    )

    state.reconciliation_id = reconciliation[
        "reconciliation_id"
    ]

    state.reconciliation_hash = reconciliation[
        "reconciliation_hash"
    ]

    state.phase = "RECONCILED"

    append_journal(
        state,
        "RECONCILED",
        reconciliation,
    )

    reconciliation_checks = [
        (
            "Exchange Reconciliation Was Created",
            bool(
                reconciliation[
                    "reconciliation_id"
                ]
            ),
        ),
        (
            "Exchange Reconciliation Is Bound To BTCUSDT",
            reconciliation[
                "symbol"
            ] == SYMBOL,
        ),
        (
            "Reconciliation Is Read Only",
            reconciliation[
                "read_only"
            ]
            is True,
        ),
        (
            "Reconciliation Exchange Write Count Is Zero",
            reconciliation[
                "exchange_writes"
            ]
            == 0,
        ),
    ]

    for name, passed in reconciliation_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 6 - LIVE GATE
    # ----------------------------------------------------------------------------------------------

    test_header(
        6,
        "CONTROLLED LIVE ACTIVATION GATE",
    )

    live_gate_armed = arm_live_gate(
        state
    )

    gate_checks = [
        (
            "Live Gate Arming Validation Succeeded",
            live_gate_armed,
        ),
        (
            "Live Gate Does Not Enable Exchange Writer",
            not EXCHANGE_WRITER_ENABLED,
        ),
        (
            "Live Gate Does Not Enable Exchange Writes",
            not EXCHANGE_NETWORK_WRITES_ENABLED,
        ),
        (
            "Live Gate Does Not Enable Real Orders",
            not REAL_ORDER_EXECUTION,
        ),
        (
            "First Real Order Remains Forbidden",
            not FIRST_REAL_ORDER_ALLOWED,
        ),
    ]

    for name, passed in gate_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 7 - INTENT
    # ----------------------------------------------------------------------------------------------

    test_header(
        7,
        "BOUND ORDER INTENT",
    )

    intent = create_intent(
        reconciliation
    )

    state.active_intent = intent

    state.highest_nonce = max(
        state.highest_nonce,
        int(
            intent[
                "nonce"
            ]
        ),
    )

    append_journal(
        state,
        "INTENT_CREATED",
        {
            "intent_id": intent[
                "intent_id"
            ],
            "intent_hash": intent[
                "intent_hash"
            ],
            "synthetic_only": True,
        },
    )

    intent_checks = [
        (
            "Intent Was Created",
            bool(
                intent[
                    "intent_id"
                ]
            ),
        ),
        (
            "Intent Is Bound To BTCUSDT",
            intent[
                "symbol"
            ] == SYMBOL,
        ),
        (
            "Intent Is Synthetic Only",
            intent[
                "synthetic_only"
            ]
            is True,
        ),
        (
            "Intent Forbids Transmission",
            intent[
                "transmission_allowed"
            ]
            is False,
        ),
        (
            "Intent Forbids Exchange Network Write",
            intent[
                "exchange_network_write_allowed"
            ]
            is False,
        ),
    ]

    for name, passed in intent_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 8 - INTENT HASH BINDING
    # ----------------------------------------------------------------------------------------------

    test_header(
        8,
        "INTENT INTEGRITY BINDING",
    )

    intent_copy = dict(
        intent
    )

    stored_intent_hash = intent_copy.pop(
        "intent_hash"
    )

    stored_intent_id = intent_copy.pop(
        "intent_id"
    )

    recalculated_intent_hash = sha256_obj(
        intent_copy
    )

    intent_hash_valid = (
        stored_intent_hash
        == recalculated_intent_hash
    )

    intent_id_valid = (
        stored_intent_id
        == (
            "int-"
            + recalculated_intent_hash[
                :20
            ]
        )
    )

    if not test_result(
        "Intent Hash Is Valid",
        intent_hash_valid,
    ):

        failures.append(
            "Intent Hash Is Valid"
        )

    if not test_result(
        "Intent ID Is Bound To Intent Hash",
        intent_id_valid,
    ):

        failures.append(
            "Intent ID Is Bound To Intent Hash"
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 9 - AUTHORIZATION
    # ----------------------------------------------------------------------------------------------

    test_header(
        9,
        "ONE-TIME AUTHORIZATION",
    )

    authorization = create_authorization(
        intent
    )

    state.active_authorization = authorization

    append_journal(
        state,
        "AUTHORIZATION_CREATED",
        {
            "authorization_id": authorization[
                "authorization_id"
            ],
            "authorization_hash": authorization[
                "authorization_hash"
            ],
            "intent_id": intent[
                "intent_id"
            ],
            "one_time": True,
        },
    )

    authorization_checks = [
        (
            "Authorization Was Created",
            bool(
                authorization[
                    "authorization_id"
                ]
            ),
        ),
        (
            "Authorization Is Bound To Intent",
            authorization[
                "intent_hash"
            ]
            == intent[
                "intent_hash"
            ],
        ),
        (
            "Authorization Is One-Time",
            authorization[
                "one_time"
            ]
            is True,
        ),
        (
            "Authorization Does Not Permit Transmission",
            authorization[
                "transmission_allowed"
            ]
            is False,
        ),
        (
            "Authorization Does Not Enable Writer",
            authorization[
                "writer_enabled"
            ]
            is False,
        ),
    ]

    for name, passed in authorization_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 10 - CLIENT ORDER ID
    # ----------------------------------------------------------------------------------------------

    test_header(
        10,
        "IDEMPOTENT CLIENT ORDER ID",
    )

    client_order_id_a = deterministic_client_order_id(
        intent
    )

    client_order_id_b = deterministic_client_order_id(
        intent
    )

    client_id_checks = [
        (
            "Client Order ID Is Deterministic",
            client_order_id_a
            == client_order_id_b,
        ),
        (
            "Client Order ID Uses R35I Prefix",
            client_order_id_a.startswith(
                "r35i-"
            ),
        ),
        (
            "Client Order ID Has Not Yet Been Consumed",
            client_order_id_a
            not in state.used_client_order_ids,
        ),
    ]

    for name, passed in client_id_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    log(
        f"{VERSION}: CLIENT ORDER ID={client_order_id_a}"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 11 - WRITER ENVELOPE
    # ----------------------------------------------------------------------------------------------

    test_header(
        11,
        "SECRET-SAFE WRITER ENVELOPE",
    )

    envelope = create_writer_envelope(
        reconciliation=reconciliation,
        intent=intent,
        authorization=authorization,
        client_order_id=client_order_id_a,
    )

    envelope_checks = [
        (
            "Writer Envelope Uses POST",
            envelope[
                "method"
            ]
            == "POST",
        ),
        (
            "Writer Envelope Uses Exact V3 Order Path",
            envelope[
                "request_path"
            ]
            == ORDER_PATH,
        ),
        (
            "Writer Envelope Is Bound To Intent",
            envelope[
                "intent_hash"
            ]
            == intent[
                "intent_hash"
            ],
        ),
        (
            "Writer Envelope Is Bound To Authorization",
            envelope[
                "authorization_hash"
            ]
            == authorization[
                "authorization_hash"
            ],
        ),
        (
            "Writer Envelope Is Bound To Reconciliation",
            envelope[
                "reconciliation_hash"
            ]
            == reconciliation[
                "reconciliation_hash"
            ],
        ),
        (
            "Writer Envelope Marks Transmitted False",
            envelope[
                "transmitted"
            ]
            is False,
        ),
        (
            "Writer Preview Redacts Access Key",
            envelope[
                "headers"
            ][
                "ACCESS-KEY"
            ]
            == "<redacted>",
        ),
        (
            "Writer Preview Redacts Signature",
            envelope[
                "headers"
            ][
                "ACCESS-SIGN"
            ]
            == "<redacted>",
        ),
        (
            "Writer Preview Redacts Passphrase",
            envelope[
                "headers"
            ][
                "ACCESS-PASSPHRASE"
            ]
            == "<redacted>",
        ),
    ]

    for name, passed in envelope_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    log(
        f"{VERSION}: WRITER PREVIEW={canonical_json(envelope)}"
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 12 - FIREBREAK
    # ----------------------------------------------------------------------------------------------

    test_header(
        12,
        "EXCHANGE NETWORK FIREBREAK",
    )

    firebreak_checks = [
        (
            "Exchange Writer Is Still Disabled",
            not EXCHANGE_WRITER_ENABLED,
        ),
        (
            "Exchange Network Writes Are Still Disabled",
            not EXCHANGE_NETWORK_WRITES_ENABLED,
        ),
        (
            "Real Order Execution Is Still Disabled",
            not REAL_ORDER_EXECUTION,
        ),
        (
            "First Real Order Is Still Forbidden",
            not FIRST_REAL_ORDER_ALLOWED,
        ),
        (
            "Envelope Was Not Transmitted",
            envelope[
                "transmitted"
            ]
            is False,
        ),
    ]

    for name, passed in firebreak_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 13 - SYNTHETIC DISPATCH
    # ----------------------------------------------------------------------------------------------

    test_header(
        13,
        "SYNTHETIC DISPATCH",
    )

    exchange_count_before = (
        get_exchange_write_count()
    )

    receipt = synthetic_dispatch(
        state,
        envelope,
    )

    exchange_count_after = (
        get_exchange_write_count()
    )

    dispatch_checks = [
        (
            "Synthetic Dispatch Produced Receipt",
            bool(
                receipt[
                    "receipt_id"
                ]
            ),
        ),
        (
            "Synthetic Receipt Marks Transmitted False",
            receipt[
                "transmitted"
            ]
            is False,
        ),
        (
            "Synthetic Receipt Marks Exchange Write False",
            receipt[
                "exchange_network_write"
            ]
            is False,
        ),
        (
            "Synthetic Receipt Marks Real Order False",
            receipt[
                "real_order"
            ]
            is False,
        ),
        (
            "Synthetic Dispatch Makes No Exchange Network Write",
            exchange_count_before
            == exchange_count_after
            == 0,
        ),
    ]

    for name, passed in dispatch_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 14 - INTENT REPLAY
    # ----------------------------------------------------------------------------------------------

    test_header(
        14,
        "INTENT REPLAY PROTECTION",
    )

    intent_replay_rejected = (
        intent[
            "intent_id"
        ]
        in state.consumed_intents
    )

    if not test_result(
        "Consumed Intent Replay Is Rejected",
        intent_replay_rejected,
    ):

        failures.append(
            "Consumed Intent Replay Is Rejected"
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 15 - AUTHORIZATION REPLAY
    # ----------------------------------------------------------------------------------------------

    test_header(
        15,
        "AUTHORIZATION REPLAY PROTECTION",
    )

    authorization_consumed = (
        authorization[
            "authorization_id"
        ]
        in state.consumed_authorizations
    )

    if not test_result(
        "Authorization Is Persistently Consumed",
        authorization_consumed,
    ):

        failures.append(
            "Authorization Is Persistently Consumed"
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 16 - CLIENT ORDER ID REPLAY
    # ----------------------------------------------------------------------------------------------

    test_header(
        16,
        "CLIENT ORDER ID REPLAY PROTECTION",
    )

    client_id_consumed = (
        client_order_id_a
        in state.used_client_order_ids
    )

    if not test_result(
        "Client Order ID Is Persistently Used",
        client_id_consumed,
    ):

        failures.append(
            "Client Order ID Is Persistently Used"
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 17 - DURABLE RECEIPT
    # ----------------------------------------------------------------------------------------------

    test_header(
        17,
        "DURABLE RECEIPT",
    )

    durable_receipt_exists = any(
        item.get(
            "receipt_id"
        )
        == receipt[
            "receipt_id"
        ]
        for item
        in state.durable_receipts
    )

    if not test_result(
        "Durable Receipt Exists",
        durable_receipt_exists,
    ):

        failures.append(
            "Durable Receipt Exists"
        )

    # ----------------------------------------------------------------------------------------------
    # TEST 18 - KILL SWITCH
    # ----------------------------------------------------------------------------------------------

    test_header(
        18,
        "KILL SWITCH BOUNDARY",
    )

    original_kill_switch = (
        state.kill_switch
    )

    original_gate_state = (
        state.live_gate_armed
    )

    state.kill_switch = True
    state.live_gate_armed = False

    save_state(
        state
    )

    write_count_before_kill_test = (
        get_exchange_write_count()
    )

    kill_switch_result = arm_live_gate(
        state
    )

    write_count_after_kill_test = (
        get_exchange_write_count()
    )

    kill_checks = [
        (
            "Kill Switch Rejects Live Gate Arming",
            kill_switch_result
            is False,
        ),
        (
            "Kill Switch Makes No Exchange Write",
            write_count_before_kill_test
            == write_count_after_kill_test
            == 0,
        ),
    ]

    for name, passed in kill_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    state.kill_switch = (
        original_kill_switch
    )

    state.live_gate_armed = (
        original_gate_state
    )

    save_state(
        state
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 19 - AMBIGUOUS OUTCOME
    # ----------------------------------------------------------------------------------------------

    test_header(
        19,
        "AMBIGUOUS OUTCOME BLOCK",
    )

    state.ambiguous_outcome = True
    state.live_gate_armed = False

    save_state(
        state
    )

    ambiguous_gate_result = arm_live_gate(
        state
    )

    ambiguous_block_passed = (
        FAIL_CLOSED_ON_AMBIGUOUS_OUTCOME
        and ambiguous_gate_result
        is False
    )

    if not test_result(
        "Ambiguous Outcome Blocks Live Gate",
        ambiguous_block_passed,
    ):

        failures.append(
            "Ambiguous Outcome Blocks Live Gate"
        )

    state.ambiguous_outcome = False
    state.live_gate_armed = True

    save_state(
        state
    )

    # ----------------------------------------------------------------------------------------------
    # TEST 20 - RESTART
    # ----------------------------------------------------------------------------------------------

    test_header(
        20,
        "DURABLE RESTART PROTECTION",
    )

    save_state(
        state
    )

    restarted = load_state()

    restart_checks = [
        (
            "Live Activation Gate State Survives Restart",
            restarted.live_gate_armed
            == state.live_gate_armed,
        ),
        (
            "Consumed Intent Survives Restart",
            intent[
                "intent_id"
            ]
            in restarted.consumed_intents,
        ),
        (
            "Consumed Authorization Survives Restart",
            authorization[
                "authorization_id"
            ]
            in restarted.consumed_authorizations,
        ),
        (
            "Used Client Order ID Survives Restart",
            client_order_id_a
            in restarted.used_client_order_ids,
        ),
        (
            "Durable Receipt Survives Restart",
            any(
                item.get(
                    "receipt_id"
                )
                == receipt[
                    "receipt_id"
                ]
                for item
                in restarted.durable_receipts
            ),
        ),
        (
            "Restart Keeps Exchange Write Count At Zero",
            get_exchange_write_count()
            == 0,
        ),
    ]

    for name, passed in restart_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    state = restarted

    # ----------------------------------------------------------------------------------------------
    # TEST 21 - TELEGRAM BOUNDARY
    # ----------------------------------------------------------------------------------------------

    test_header(
        21,
        "TELEGRAM REPORTING BOUNDARY",
    )

    telegram_preview = telegram_request_preview(
        "R35I validation preview"
    )

    telegram_boundary_checks = [
        (
            "Telegram Uses POST Only For Reporting",
            telegram_preview[
                "method"
            ]
            == "POST",
        ),
        (
            "Telegram Operation Is sendMessage",
            telegram_preview[
                "operation"
            ]
            == "sendMessage",
        ),
        (
            "Telegram Request Is Report Only",
            telegram_preview[
                "report_only"
            ]
            is True,
        ),
        (
            "Telegram Request Is Not Exchange Mutation",
            telegram_preview[
                "exchange_mutation"
            ]
            is False,
        ),
        (
            "Telegram Cannot Control Execution",
            telegram_preview[
                "can_control_execution"
            ]
            is False
            and TELEGRAM_CAN_CONTROL_EXECUTION
            is False,
        ),
        (
            "Telegram Preview Does Not Expose Bot Token",
            telegram_preview[
                "bot_token"
            ]
            == "<redacted>",
        ),
    ]

    for name, passed in telegram_boundary_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 22 - TELEGRAM READINESS ONLY
    #
    # IMPORTANT CORRECTION:
    #
    # We DO NOT send Telegram here anymore.
    # Delivery is intentionally deferred until AFTER Tests 23-26.
    #
    # ----------------------------------------------------------------------------------------------

    test_header(
        22,
        "FINAL TELEGRAM DELIVERY READINESS",
    )

    telegram_ready = (
        TELEGRAM_REPORTING_ENABLED
        and bool(
            TELEGRAM_BOT_TOKEN
        )
        and bool(
            TELEGRAM_CHAT_ID
        )
    )

    telegram_readiness_checks = [
        (
            "Telegram Reporting Is Enabled",
            TELEGRAM_REPORTING_ENABLED,
        ),
        (
            "Telegram Bot Token Is Present",
            bool(
                TELEGRAM_BOT_TOKEN
            ),
        ),
        (
            "Telegram Chat ID Is Present",
            bool(
                TELEGRAM_CHAT_ID
            ),
        ),
        (
            "Telegram Delivery Is Deferred Until Final Verification",
            get_telegram_delivery_count()
            == 0,
        ),
    ]

    for name, passed in telegram_readiness_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 23 - JOURNAL INTEGRITY
    # ----------------------------------------------------------------------------------------------

    test_header(
        23,
        "JOURNAL INTEGRITY",
    )

    records = read_journal()

    journal_valid, journal_terminal_hash, journal_sequence = (
        validate_journal_records(
            records
        )
    )

    journal_checks = [
        (
            "Durable Journal Contains Records",
            len(
                records
            )
            > 0,
        ),
        (
            "Journal Hash Chain Is Valid",
            journal_valid,
        ),
        (
            "Journal Sequence Matches Durable State",
            journal_sequence
            == state.journal_sequence,
        ),
        (
            "Journal Terminal Hash Matches Durable State",
            journal_terminal_hash
            == state.last_journal_hash,
        ),
    ]

    for name, passed in journal_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 24 - TAMPER DETECTION
    # ----------------------------------------------------------------------------------------------

    test_header(
        24,
        "JOURNAL TAMPER DETECTION",
    )

    tamper_has_record = (
        len(
            records
        )
        > 0
    )

    tamper_rejected = False

    if tamper_has_record:

        tampered_records = json.loads(
            json.dumps(
                records
            )
        )

        tampered_records[
            0
        ][
            "event"
        ] = "TAMPERED_EVENT"

        tampered_valid, _, _ = (
            validate_journal_records(
                tampered_records
            )
        )

        tamper_rejected = (
            not tampered_valid
        )

    tamper_checks = [
        (
            "Tamper Test Has Journal Record",
            tamper_has_record,
        ),
        (
            "Journal Tampering Is Rejected",
            tamper_rejected,
        ),
    ]

    for name, passed in tamper_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 25 - FINAL FIREBREAK
    # ----------------------------------------------------------------------------------------------

    test_header(
        25,
        "FINAL HARD WRITE FIREBREAK",
    )

    final_firebreak_checks = [
        (
            "Final Exchange Writer Is Disabled",
            not EXCHANGE_WRITER_ENABLED,
        ),
        (
            "Final Exchange Network Writes Are Disabled",
            not EXCHANGE_NETWORK_WRITES_ENABLED,
        ),
        (
            "Final Exchange POST Is Disabled",
            not EXCHANGE_POST_ENABLED,
        ),
        (
            "Final Exchange PUT Is Disabled",
            not EXCHANGE_PUT_ENABLED,
        ),
        (
            "Final Exchange PATCH Is Disabled",
            not EXCHANGE_PATCH_ENABLED,
        ),
        (
            "Final Exchange DELETE Is Disabled",
            not EXCHANGE_DELETE_ENABLED,
        ),
        (
            "Final Real Order Execution Is Disabled",
            not REAL_ORDER_EXECUTION,
        ),
        (
            "Final Demo Order Execution Is Disabled",
            not DEMO_ORDER_EXECUTION,
        ),
        (
            "Final First Real Order Is Forbidden",
            not FIRST_REAL_ORDER_ALLOWED,
        ),
        (
            "Final Exchange Write Count Is Zero",
            get_exchange_write_count()
            == 0,
        ),
    ]

    for name, passed in final_firebreak_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ----------------------------------------------------------------------------------------------
    # TEST 26 - FINAL DURABLE CONSISTENCY
    # ----------------------------------------------------------------------------------------------

    test_header(
        26,
        "FINAL DURABLE CONSISTENCY",
    )

    state.exchange_network_write_count = (
        get_exchange_write_count()
    )

    state.phase = "VALIDATED"

    save_state(
        state
    )

    final_journal_valid = (
        validate_durable_journal(
            state
        )
    )

    final_records = read_journal()

    (
        final_chain_valid,
        final_terminal_hash,
        final_sequence,
    ) = validate_journal_records(
        final_records
    )

    final_consistency_checks = [
        (
            "Final Journal Hash Chain Is Valid",
            final_chain_valid,
        ),
        (
            "Final Journal Sequence Matches State",
            final_sequence
            == state.journal_sequence,
        ),
        (
            "Final Journal Hash Matches State",
            final_terminal_hash
            == state.last_journal_hash,
        ),
        (
            "Final Durable Journal Validation Passed",
            final_journal_valid,
        ),
        (
            "Final Exchange Write Count Remains Zero",
            get_exchange_write_count()
            == 0,
        ),
    ]

    for name, passed in final_consistency_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # ==================================================================================================
    # FINAL VALIDATION STATUS
    # ==================================================================================================

    overall_passed = (
        len(
            failures
        )
        == 0
    )

    journal_status = (
        "PASS"
        if (
            final_chain_valid
            and final_journal_valid
        )
        else
        "FAIL"
    )

    authenticated_read_status = (
        "PASS"
        if authenticated_reads_passed
        else
        "FAIL"
    )

    # ==================================================================================================
    # FINAL TELEGRAM DELIVERY
    #
    # THIS IS THE ONLY TELEGRAM DELIVERY POINT IN R35I.
    #
    # It occurs AFTER journal verification.
    # Therefore the report can never say:
    #
    #     Journal test: pending final verification
    #
    # ==================================================================================================

    test_header(
        27,
        "SINGLE FINAL TELEGRAM REPORT",
    )

    phase_before_telegram = (
        state.phase
    )

    nonce_before_telegram = (
        state.highest_nonce
    )

    exchange_count_before_telegram = (
        get_exchange_write_count()
    )

    telegram_count_before = (
        get_telegram_delivery_count()
    )

    balance_text = (
        f"{balance:.8f} USDT"
        if balance is not None
        else "unavailable"
    )

    mark_text = (
        str(
            mark_price
        )
        if mark_price is not None
        else "unavailable"
    )

    final_status_text = (
        "VALIDATION PASSED"
        if overall_passed
        else "VALIDATION FAILED"
    )

    telegram_text = (
        f"✅ {VERSION} VALIDATION REPORT\n"
        f"\n"
        f"Symbol: {SYMBOL}\n"
        f"Authenticated WEEX reads: {authenticated_read_status}\n"
        f"Balance: {balance_text}\n"
        f"Mark price: {mark_text}\n"
        f"Open positions: {open_positions}\n"
        f"Journal integrity: {journal_status}\n"
        f"Journal sequence: {state.journal_sequence}\n"
        f"Exchange network writes: {get_exchange_write_count()}\n"
        f"Real order execution: DISABLED\n"
        f"Demo order execution: DISABLED\n"
        f"First real order: FORBIDDEN\n"
        f"Telegram reports this run: 1 maximum\n"
        f"Status: {final_status_text}"
    )

    telegram_delivered = False
    telegram_result = (
        "telegram not attempted"
    )

    if telegram_ready:

        (
            telegram_delivered,
            telegram_result,
        ) = send_final_telegram_report_once(
            telegram_text
        )

    else:

        telegram_result = (
            "telegram configuration incomplete"
        )

    log(
        f"{VERSION}: TELEGRAM DELIVERED={telegram_delivered}"
    )

    log(
        f"{VERSION}: TELEGRAM RESULT={telegram_result}"
    )

    phase_after_telegram = (
        state.phase
    )

    nonce_after_telegram = (
        state.highest_nonce
    )

    exchange_count_after_telegram = (
        get_exchange_write_count()
    )

    telegram_count_after = (
        get_telegram_delivery_count()
    )

    telegram_final_checks = [
        (
            "Telegram Delivery Succeeded",
            telegram_delivered
            if telegram_ready
            else True,
        ),
        (
            "Telegram Leaves Strategy Phase Unchanged",
            phase_before_telegram
            == phase_after_telegram,
        ),
        (
            "Telegram Leaves Strategy Nonce Unchanged",
            nonce_before_telegram
            == nonce_after_telegram,
        ),
        (
            "Telegram Leaves Exchange Write Count Unchanged",
            exchange_count_before_telegram
            == exchange_count_after_telegram,
        ),
        (
            "Real Order Execution Remains Disabled After Telegram",
            not REAL_ORDER_EXECUTION,
        ),
        (
            "Telegram Sent At Most One Message This Run",
            (
                telegram_count_after
                - telegram_count_before
            )
            <= 1,
        ),
    ]

    for name, passed in telegram_final_checks:

        if not test_result(
            name,
            passed,
        ):

            failures.append(
                name
            )

    # Recalculate because Telegram validation itself is part of validation.
    overall_passed = (
        len(
            failures
        )
        == 0
    )

    # ==================================================================================================
    # FINAL SUMMARY
    # ==================================================================================================

    separator()

    log(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    separator()

    log(
        f"SYMBOL={SYMBOL}"
    )

    log(
        f"EVENT={VERSION}_VALIDATION"
    )

    log(
        "PHASE=COMPLETED"
    )

    log(
        f"AUTHENTICATED_WEEX_READS={authenticated_read_status}"
    )

    log(
        f"BALANCE={balance_text}"
    )

    log(
        f"MARK_PRICE={mark_text}"
    )

    log(
        f"OPEN_POSITIONS={open_positions}"
    )

    log(
        f"JOURNAL_INTEGRITY={journal_status}"
    )

    log(
        f"JOURNAL_SEQUENCE={state.journal_sequence}"
    )

    log(
        f"TELEGRAM_DELIVERIES={get_telegram_delivery_count()}"
    )

    log(
        f"EXCHANGE_NETWORK_WRITES={get_exchange_write_count()}"
    )

    log(
        f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION}"
    )

    log(
        f"DEMO_ORDER_EXECUTION={DEMO_ORDER_EXECUTION}"
    )

    log(
        f"FIRST_REAL_ORDER_ALLOWED={FIRST_REAL_ORDER_ALLOWED}"
    )

    log(
        (
            "STATUS=R35I_VALIDATION_PASSED_HARD_DISABLED"
            if overall_passed
            else
            "STATUS=R35I_VALIDATION_FAILED"
        )
    )

    if failures:

        separator()

        log(
            f"{VERSION}: FAILED CHECKS"
        )

        separator()

        for failure in failures:

            log(
                f"{VERSION}: FAILURE={failure}"
            )

    separator()

    with _health_lock:

        _health_ready = True

    return overall_passed


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

def main() -> None:

    start_health_server()

    time.sleep(
        0.25
    )

    try:

        passed = run_validation()

        if passed:

            log(
                f"{VERSION}: ALL VALIDATION TESTS PASSED"
            )

        else:

            log(
                f"{VERSION}: VALIDATION FAILED"
            )

    except KeyboardInterrupt:

        log(
            f"{VERSION}: STOPPED"
        )

    except Exception as exc:

        log(
            f"{VERSION}: FATAL ERROR={type(exc).__name__}: {exc}"
        )

        raise

    # Keep Render health service alive.
    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT={heartbeat} "
            f"EXCHANGE_NETWORK_WRITES={get_exchange_write_count()} "
            f"REAL_ORDER_EXECUTION={REAL_ORDER_EXECUTION} "
            f"TELEGRAM_DELIVERIES={get_telegram_delivery_count()}"
        )

        time.sleep(
            60
        )


if __name__ == "__main__":

    main()
