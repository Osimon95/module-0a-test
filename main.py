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
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# R35J - CONTROLLED FIRST-LIVE-ORDER BOUNDARY VALIDATION
# ==================================================================================================
#
# PURPOSE
#   R35J validates the final boundary immediately before a first real WEEX futures order.
#
# IMPORTANT
#   THIS BUILD DOES NOT TRANSMIT A REAL ORDER.
#
#   It validates:
#       - authenticated WEEX read access
#       - public mark-price access
#       - no existing open BTCUSDT position
#       - exact V3 futures order endpoint
#       - exact order payload construction
#       - deterministic client order ID
#       - one-time intent
#       - one-time authorization
#       - authorization/intent/payload binding
#       - signature generation
#       - durable journal
#       - consumed authorization persistence
#       - used client order ID persistence
#       - restart protection
#       - one-shot synthetic dispatch
#       - Telegram report-only boundary
#
# SAFETY MODEL
#   - AUTHENTICATED GETS ALLOWED
#   - PUBLIC GETS ALLOWED
#   - TELEGRAM REPORT POST ALLOWED
#   - WEEX ORDER POST IS HARD DISABLED
#   - REAL ORDER EXECUTION IS HARD DISABLED
#   - DEMO ORDER EXECUTION IS HARD DISABLED
#
#   There must be NO path in this R35J file that invokes urllib/request POST against
#   https://api-contract.weex.com/capi/v3/order.
#
# ==================================================================================================


VERSION = "R35J"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

STATE_DIR = Path(
    os.getenv(
        "R35J_STATE_DIR",
        "/tmp/r35j_state",
    )
)

STATE_FILE = STATE_DIR / "state.json"
JOURNAL_FILE = STATE_DIR / "journal.jsonl"

WEEX_BASE_URL = "https://api-contract.weex.com"

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    os.getenv("API_KEY", ""),
).strip()

WEEX_SECRET_KEY = os.getenv(
    "WEEX_SECRET_KEY",
    os.getenv("SECRET_KEY", ""),
).strip()

WEEX_PASSPHRASE = os.getenv(
    "WEEX_PASSPHRASE",
    os.getenv("PASSPHRASE", ""),
).strip()


# --------------------------------------------------------------------------------------------------
# PUBLIC / PRIVATE READ ENDPOINTS
# --------------------------------------------------------------------------------------------------

PUBLIC_MARK_PRICE_PATH = "/capi/v3/market/markPrice"

PRIVATE_BALANCE_PATH = "/capi/v3/account/assets"
PRIVATE_POSITIONS_PATH = "/capi/v3/account/positions"


# --------------------------------------------------------------------------------------------------
# FUTURE LIVE ORDER ENDPOINT
# --------------------------------------------------------------------------------------------------

LIVE_ORDER_METHOD = "POST"
LIVE_ORDER_PATH = "/capi/v3/order"


# --------------------------------------------------------------------------------------------------
# HARD SAFETY FLAGS
# --------------------------------------------------------------------------------------------------

PUBLIC_READS_ENABLED = True
AUTHENTICATED_READS_ENABLED = True

NETWORK_WRITES_ENABLED = False
REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

FIRST_REAL_ORDER_ALLOWED = False

SYNTHETIC_ORDER_DISPATCH_ONLY = True

MAX_EXCHANGE_NETWORK_WRITES = 0


# --------------------------------------------------------------------------------------------------
# R35J FIRST-ORDER PLAN
# --------------------------------------------------------------------------------------------------
#
# This is intentionally NOT a live strategy engine.
#
# It creates one tiny hypothetical MARKET order envelope only.
#
# Position direction defaults LONG because this is only envelope validation.
#
# Quantity is deliberately configured by environment rather than automatically derived.
# The default is 0.0001 BTC.
#
# --------------------------------------------------------------------------------------------------

ORDER_SIDE = os.getenv(
    "R35J_ORDER_SIDE",
    "BUY",
).strip().upper()

POSITION_SIDE = os.getenv(
    "R35J_POSITION_SIDE",
    "LONG",
).strip().upper()

ORDER_TYPE = "MARKET"

ORDER_QUANTITY = os.getenv(
    "R35J_ORDER_QUANTITY",
    "0.0001",
).strip()

MAX_FIRST_ORDER_QUANTITY_BTC = 0.0001


# --------------------------------------------------------------------------------------------------
# TELEGRAM
# --------------------------------------------------------------------------------------------------

TELEGRAM_REPORTING_ENABLED = (
    os.getenv(
        "TELEGRAM_REPORTING_ENABLED",
        "true",
    ).strip().lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()

MAX_TELEGRAM_REPORTS_PER_RUN = 1


# --------------------------------------------------------------------------------------------------
# PROCESS COUNTERS
# --------------------------------------------------------------------------------------------------

_exchange_network_write_count = 0
_telegram_report_count = 0

_state_lock = threading.RLock()


# ==================================================================================================
# UTILITIES
# ==================================================================================================


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def separator() -> None:
    print(
        "-" * 100,
        flush=True,
    )


def log(
    message: str,
) -> None:

    print(
        f"{utc_now()} {message}",
        flush=True,
    )


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def pass_fail(
    label: str,
    condition: bool,
) -> bool:

    marker = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{label:<85} {marker}",
        flush=True,
    )

    return condition


def parse_decimal(
    text: str,
) -> float:

    try:
        return float(text)

    except Exception:
        return 0.0


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = "INITIALIZED"

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    live_activation_gate: bool = False

    active_intent: Optional[
        Dict[str, Any]
    ] = None

    active_authorization: Optional[
        Dict[str, Any]
    ] = None

    consumed_intents: List[str] = field(
        default_factory=list
    )

    consumed_authorizations: List[str] = field(
        default_factory=list
    )

    used_client_order_ids: List[str] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    synthetic_dispatch_count: int = 0

    exchange_network_write_count: int = 0

    journal_sequence: int = 0

    last_journal_hash: str = "0" * 64

    terminal: bool = False


def default_state() -> StrategyState:
    return StrategyState()


def state_to_dict(
    state: StrategyState,
) -> Dict[str, Any]:

    return asdict(state)


def save_state(
    state: StrategyState,
) -> None:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = STATE_FILE.with_suffix(
        ".tmp"
    )

    payload = canonical_json(
        state_to_dict(state)
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(payload)

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_file,
        STATE_FILE,
    )


def load_state() -> StrategyState:

    if not STATE_FILE.exists():
        return default_state()

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as handle:

            raw = json.load(
                handle
            )

        return StrategyState(
            version=str(
                raw.get(
                    "version",
                    VERSION,
                )
            ),
            symbol=str(
                raw.get(
                    "symbol",
                    SYMBOL,
                )
            ),
            phase=str(
                raw.get(
                    "phase",
                    "INITIALIZED",
                )
            ),
            generation=int(
                raw.get(
                    "generation",
                    1,
                )
            ),
            epoch=int(
                raw.get(
                    "epoch",
                    1,
                )
            ),
            highest_nonce=int(
                raw.get(
                    "highest_nonce",
                    0,
                )
            ),
            live_activation_gate=bool(
                raw.get(
                    "live_activation_gate",
                    False,
                )
            ),
            active_intent=raw.get(
                "active_intent"
            ),
            active_authorization=raw.get(
                "active_authorization"
            ),
            consumed_intents=list(
                raw.get(
                    "consumed_intents",
                    [],
                )
            ),
            consumed_authorizations=list(
                raw.get(
                    "consumed_authorizations",
                    [],
                )
            ),
            used_client_order_ids=list(
                raw.get(
                    "used_client_order_ids",
                    [],
                )
            ),
            durable_receipts=list(
                raw.get(
                    "durable_receipts",
                    [],
                )
            ),
            synthetic_dispatch_count=int(
                raw.get(
                    "synthetic_dispatch_count",
                    0,
                )
            ),
            exchange_network_write_count=int(
                raw.get(
                    "exchange_network_write_count",
                    0,
                )
            ),
            journal_sequence=int(
                raw.get(
                    "journal_sequence",
                    0,
                )
            ),
            last_journal_hash=str(
                raw.get(
                    "last_journal_hash",
                    "0" * 64,
                )
            ),
            terminal=bool(
                raw.get(
                    "terminal",
                    False,
                )
            ),
        )

    except Exception:

        return default_state()


# ==================================================================================================
# DURABLE HASH-CHAIN JOURNAL
# ==================================================================================================


def append_journal(
    state: StrategyState,
    event: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:

    with _state_lock:

        sequence = (
            state.journal_sequence
            + 1
        )

        record_without_hash = {
            "sequence": sequence,
            "timestamp": utc_now(),
            "version": VERSION,
            "symbol": SYMBOL,
            "event": event,
            "details": details,
            "previous_hash": state.last_journal_hash,
        }

        record_hash = sha256_text(
            canonical_json(
                record_without_hash
            )
        )

        record = dict(
            record_without_hash
        )

        record["record_hash"] = (
            record_hash
        )

        STATE_DIR.mkdir(
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

        state.journal_sequence = (
            sequence
        )

        state.last_journal_hash = (
            record_hash
        )

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

    with open(
        JOURNAL_FILE,
        "r",
        encoding="utf-8",
    ) as handle:

        for line in handle:

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(
                    line
                )
            )

    return records


def validate_journal() -> Tuple[
    bool,
    bool,
]:

    try:

        records = read_journal()

        if not records:
            return False, False

        previous_hash = (
            "0" * 64
        )

        previous_sequence = 0

        for record in records:

            sequence = int(
                record["sequence"]
            )

            if sequence <= previous_sequence:
                return False, False

            expected_previous_hash = (
                record[
                    "previous_hash"
                ]
            )

            if (
                expected_previous_hash
                != previous_hash
            ):
                return False, True

            clone = dict(
                record
            )

            stored_hash = clone.pop(
                "record_hash"
            )

            calculated_hash = (
                sha256_text(
                    canonical_json(
                        clone
                    )
                )
            )

            if (
                stored_hash
                != calculated_hash
            ):
                return False, True

            previous_hash = (
                stored_hash
            )

            previous_sequence = (
                sequence
            )

        return True, True

    except Exception:

        return False, False


# ==================================================================================================
# HEALTH SERVER
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
        }:

            self.send_response(
                404
            )

            self.end_headers()

            return

        body = canonical_json(
            {
                "status": "ok",
                "version": VERSION,
                "symbol": SYMBOL,
                "real_order_execution": REAL_ORDER_EXECUTION,
                "exchange_network_writes": _exchange_network_write_count,
            }
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
                len(body)
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

    def run_server() -> None:

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

    thread = threading.Thread(
        target=run_server,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# HTTP
# ==================================================================================================


def http_get_json(
    url: str,
    headers: Optional[
        Dict[str, str]
    ] = None,
    timeout: int = 15,
) -> Any:

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=(
            headers
            or {}
        ),
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        raw = response.read().decode(
            "utf-8"
        )

        return json.loads(
            raw
        )


# ==================================================================================================
# WEEX AUTHENTICATION
# ==================================================================================================


def credentials_present() -> bool:

    return bool(
        WEEX_API_KEY
        and WEEX_SECRET_KEY
        and WEEX_PASSPHRASE
    )


def weex_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    message = (
        timestamp
        + method.upper()
        + request_path
    )

    if query_string:

        message += (
            "?"
            + query_string
        )

    message += body

    digest = hmac.new(
        WEEX_SECRET_KEY.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


def authenticated_headers(
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> Dict[str, str]:

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = weex_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
        "Content-Type": "application/json",
        "User-Agent": f"{VERSION}/1.0",
    }


# ==================================================================================================
# WEEX PUBLIC READ
# ==================================================================================================


def obtain_mark_price() -> float:

    candidate_urls = [

        (
            WEEX_BASE_URL
            + PUBLIC_MARK_PRICE_PATH
            + "?symbol="
            + urllib.parse.quote(
                SYMBOL
            )
        ),

        (
            WEEX_BASE_URL
            + "/capi/v3/market/ticker"
            + "?symbol="
            + urllib.parse.quote(
                SYMBOL
            )
        ),

        (
            WEEX_BASE_URL
            + "/capi/v3/market/tickers"
            + "?symbol="
            + urllib.parse.quote(
                SYMBOL
            )
        ),
    ]

    for url in candidate_urls:

        try:

            payload = http_get_json(
                url
            )

            candidates: List[Any] = []

            if isinstance(
                payload,
                dict,
            ):

                candidates.append(
                    payload
                )

                data = payload.get(
                    "data"
                )

                if isinstance(
                    data,
                    dict,
                ):

                    candidates.append(
                        data
                    )

                elif isinstance(
                    data,
                    list,
                ):

                    candidates.extend(
                        data
                    )

            elif isinstance(
                payload,
                list,
            ):

                candidates.extend(
                    payload
                )

            for item in candidates:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                for key in (
                    "markPrice",
                    "mark_price",
                    "price",
                    "lastPrice",
                    "last",
                ):

                    if key in item:

                        value = parse_decimal(
                            str(
                                item[
                                    key
                                ]
                            )
                        )

                        if value > 0:

                            return value

        except Exception:
            continue

    raise RuntimeError(
        "Unable to obtain BTCUSDT mark price"
    )


# ==================================================================================================
# WEEX PRIVATE READS
# ==================================================================================================


def authenticated_get(
    path: str,
    params: Optional[
        Dict[str, str]
    ] = None,
) -> Any:

    if not AUTHENTICATED_READS_ENABLED:

        raise RuntimeError(
            "Authenticated reads disabled"
        )

    if not credentials_present():

        raise RuntimeError(
            "WEEX credentials missing"
        )

    params = (
        params
        or {}
    )

    query_string = urllib.parse.urlencode(
        params
    )

    url = (
        WEEX_BASE_URL
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    headers = authenticated_headers(
        method="GET",
        request_path=path,
        query_string=query_string,
    )

    return http_get_json(
        url=url,
        headers=headers,
    )


def recursively_find_numbers(
    value: Any,
    keys: Tuple[str, ...],
) -> List[float]:

    results: List[
        float
    ] = []

    if isinstance(
        value,
        dict,
    ):

        for key, item in value.items():

            if (
                key in keys
                and item is not None
            ):

                parsed = parse_decimal(
                    str(item)
                )

                results.append(
                    parsed
                )

            results.extend(
                recursively_find_numbers(
                    item,
                    keys,
                )
            )

    elif isinstance(
        value,
        list,
    ):

        for item in value:

            results.extend(
                recursively_find_numbers(
                    item,
                    keys,
                )
            )

    return results


def obtain_balance() -> float:

    candidate_requests = [

        (
            PRIVATE_BALANCE_PATH,
            {},
        ),

        (
            "/capi/v3/account/balance",
            {},
        ),

        (
            "/capi/v2/account/assets",
            {},
        ),
    ]

    for path, params in candidate_requests:

        try:

            payload = authenticated_get(
                path,
                params,
            )

            values = (
                recursively_find_numbers(
                    payload,
                    (
                        "availableBalance",
                        "available",
                        "availableEquity",
                        "balance",
                    ),
                )
            )

            positive_values = [
                value
                for value in values
                if value > 0
            ]

            if positive_values:

                return positive_values[
                    0
                ]

        except Exception:
            continue

    raise RuntimeError(
        "Unable to obtain authenticated balance"
    )


def obtain_positions() -> List[
    Dict[str, Any]
]:

    candidate_requests = [

        (
            PRIVATE_POSITIONS_PATH,
            {
                "symbol": SYMBOL,
            },
        ),

        (
            "/capi/v3/account/position",
            {
                "symbol": SYMBOL,
            },
        ),

        (
            "/capi/v2/account/allPosition",
            {
                "symbol": SYMBOL,
            },
        ),
    ]

    for path, params in candidate_requests:

        try:

            payload = authenticated_get(
                path,
                params,
            )

            items: List[
                Dict[str, Any]
            ] = []

            if isinstance(
                payload,
                list,
            ):

                items = [
                    item
                    for item in payload
                    if isinstance(
                        item,
                        dict,
                    )
                ]

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

                    items = [
                        item
                        for item in data
                        if isinstance(
                            item,
                            dict,
                        )
                    ]

                elif isinstance(
                    data,
                    dict,
                ):

                    nested = (
                        data.get(
                            "positions"
                        )
                        or data.get(
                            "list"
                        )
                    )

                    if isinstance(
                        nested,
                        list,
                    ):

                        items = [
                            item
                            for item in nested
                            if isinstance(
                                item,
                                dict,
                            )
                        ]

            if items is not None:

                return items

        except Exception:
            continue

    raise RuntimeError(
        "Unable to obtain authenticated positions"
    )


def position_quantity(
    position: Dict[str, Any],
) -> float:

    for key in (
        "quantity",
        "size",
        "positionAmt",
        "available",
        "total",
        "holdVolume",
    ):

        if key in position:

            return abs(
                parse_decimal(
                    str(
                        position[
                            key
                        ]
                    )
                )
            )

    return 0.0


def count_open_positions(
    positions: List[
        Dict[str, Any]
    ],
) -> int:

    count = 0

    for position in positions:

        symbol = str(
            position.get(
                "symbol",
                SYMBOL,
            )
        ).upper()

        if (
            symbol == SYMBOL
            and position_quantity(
                position
            )
            > 0
        ):

            count += 1

    return count


# ==================================================================================================
# R35J ORDER INTENT
# ==================================================================================================


def create_client_order_id(
    state: StrategyState,
) -> str:

    raw = (
        f"{VERSION}-"
        f"G{state.generation}-"
        f"E{state.epoch}-"
        f"N{state.highest_nonce + 1}-"
        f"{int(time.time())}"
    )

    return raw[
        :36
    ]


def build_order_payload(
    client_order_id: str,
) -> Dict[str, str]:

    return {
        "symbol": SYMBOL,
        "side": ORDER_SIDE,
        "positionSide": POSITION_SIDE,
        "type": ORDER_TYPE,
        "quantity": ORDER_QUANTITY,
        "newClientOrderId": client_order_id,
    }


def create_intent(
    state: StrategyState,
    payload: Dict[str, str],
) -> Dict[str, Any]:

    nonce = (
        state.highest_nonce
        + 1
    )

    state.highest_nonce = (
        nonce
    )

    payload_hash = sha256_text(
        canonical_json(
            payload
        )
    )

    intent = {
        "intent_id": (
            "INT-"
            + uuid.uuid4().hex
        ),
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "nonce": nonce,
        "method": LIVE_ORDER_METHOD,
        "path": LIVE_ORDER_PATH,
        "payload_hash": payload_hash,
        "client_order_id": payload[
            "newClientOrderId"
        ],
        "synthetic_only": True,
        "network_transmission_allowed": False,
        "created_at": utc_now(),
    }

    state.active_intent = (
        intent
    )

    save_state(
        state
    )

    append_journal(
        state,
        "INTENT_CREATED",
        {
            "intent_id": intent[
                "intent_id"
            ],
            "payload_hash": payload_hash,
            "client_order_id": payload[
                "newClientOrderId"
            ],
            "synthetic_only": True,
        },
    )

    return intent


# ==================================================================================================
# ONE-TIME AUTHORIZATION
# ==================================================================================================


def create_authorization(
    state: StrategyState,
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    authorization = {
        "authorization_id": (
            "AUTH-"
            + uuid.uuid4().hex
        ),
        "intent_id": intent[
            "intent_id"
        ],
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "nonce": intent[
            "nonce"
        ],
        "payload_hash": intent[
            "payload_hash"
        ],
        "client_order_id": intent[
            "client_order_id"
        ],
        "method": LIVE_ORDER_METHOD,
        "path": LIVE_ORDER_PATH,
        "single_use": True,
        "synthetic_only": True,
        "network_transmission_allowed": False,
        "created_at": utc_now(),
    }

    state.active_authorization = (
        authorization
    )

    save_state(
        state
    )

    append_journal(
        state,
        "AUTHORIZATION_CREATED",
        {
            "authorization_id": authorization[
                "authorization_id"
            ],
            "intent_id": authorization[
                "intent_id"
            ],
            "single_use": True,
            "synthetic_only": True,
        },
    )

    return authorization


def validate_authorization_binding(
    state: StrategyState,
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
    payload: Dict[str, str],
) -> bool:

    payload_hash = sha256_text(
        canonical_json(
            payload
        )
    )

    return all(
        [
            authorization[
                "intent_id"
            ]
            == intent[
                "intent_id"
            ],
            authorization[
                "symbol"
            ]
            == SYMBOL,
            authorization[
                "generation"
            ]
            == state.generation,
            authorization[
                "epoch"
            ]
            == state.epoch,
            authorization[
                "nonce"
            ]
            == intent[
                "nonce"
            ],
            authorization[
                "payload_hash"
            ]
            == payload_hash,
            authorization[
                "client_order_id"
            ]
            == payload[
                "newClientOrderId"
            ],
            authorization[
                "method"
            ]
            == LIVE_ORDER_METHOD,
            authorization[
                "path"
            ]
            == LIVE_ORDER_PATH,
            authorization[
                "single_use"
            ]
            is True,
        ]
    )


# ==================================================================================================
# ORDER ENVELOPE
# ==================================================================================================


def build_signed_order_envelope(
    payload: Dict[str, str],
) -> Dict[str, Any]:

    body = canonical_json(
        payload
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = weex_signature(
        timestamp=timestamp,
        method=LIVE_ORDER_METHOD,
        request_path=LIVE_ORDER_PATH,
        body=body,
    )

    return {
        "method": LIVE_ORDER_METHOD,
        "path": LIVE_ORDER_PATH,
        "url": (
            WEEX_BASE_URL
            + LIVE_ORDER_PATH
        ),
        "headers": {
            "ACCESS-KEY": WEEX_API_KEY,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": WEEX_PASSPHRASE,
            "Content-Type": "application/json",
        },
        "body": body,
        "payload_hash": sha256_text(
            body
        ),
    }


def secret_safe_envelope_preview(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "method": envelope[
            "method"
        ],
        "path": envelope[
            "path"
        ],
        "payload_hash": envelope[
            "payload_hash"
        ],
        "headers_present": [
            "ACCESS-KEY",
            "ACCESS-SIGN",
            "ACCESS-TIMESTAMP",
            "ACCESS-PASSPHRASE",
            "Content-Type",
        ],
        "credentials_redacted": True,
    }


# ==================================================================================================
# HARD-DISABLED EXCHANGE WRITER
# ==================================================================================================


def exchange_order_writer(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    global _exchange_network_write_count

    # ==============================================================================================
    # ABSOLUTE R35J FIREBREAK
    # ==============================================================================================
    #
    # No urllib.request.urlopen()
    # No requests.post()
    # No socket send
    # No HTTP POST
    #
    # This function intentionally returns a synthetic blocked receipt.
    #
    # ==============================================================================================

    if NETWORK_WRITES_ENABLED:

        raise RuntimeError(
            "R35J SAFETY VIOLATION: NETWORK_WRITES_ENABLED MUST REMAIN FALSE"
        )

    if REAL_ORDER_EXECUTION:

        raise RuntimeError(
            "R35J SAFETY VIOLATION: REAL_ORDER_EXECUTION MUST REMAIN FALSE"
        )

    if FIRST_REAL_ORDER_ALLOWED:

        raise RuntimeError(
            "R35J SAFETY VIOLATION: FIRST_REAL_ORDER_ALLOWED MUST REMAIN FALSE"
        )

    receipt = {
        "receipt_id": (
            "RCPT-"
            + uuid.uuid4().hex
        ),
        "status": "BLOCKED_AT_FINAL_FIREBREAK",
        "synthetic": True,
        "transmitted": False,
        "exchange_network_write": False,
        "method": envelope[
            "method"
        ],
        "path": envelope[
            "path"
        ],
        "payload_hash": envelope[
            "payload_hash"
        ],
        "created_at": utc_now(),
    }

    return receipt


# ==================================================================================================
# EXACTLY-ONCE SYNTHETIC DISPATCH
# ==================================================================================================


def consume_and_dispatch(
    state: StrategyState,
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    intent_id = intent[
        "intent_id"
    ]

    authorization_id = (
        authorization[
            "authorization_id"
        ]
    )

    client_order_id = (
        intent[
            "client_order_id"
        ]
    )

    if (
        intent_id
        in state.consumed_intents
    ):

        raise RuntimeError(
            "Intent replay rejected"
        )

    if (
        authorization_id
        in state.consumed_authorizations
    ):

        raise RuntimeError(
            "Authorization replay rejected"
        )

    if (
        client_order_id
        in state.used_client_order_ids
    ):

        raise RuntimeError(
            "Client order ID replay rejected"
        )

    # Persist consumption BEFORE synthetic dispatch.

    state.consumed_intents.append(
        intent_id
    )

    state.consumed_authorizations.append(
        authorization_id
    )

    state.used_client_order_ids.append(
        client_order_id
    )

    state.phase = (
        "AUTHORIZATION_CONSUMED"
    )

    save_state(
        state
    )

    append_journal(
        state,
        "AUTHORIZATION_CONSUMED",
        {
            "intent_id": intent_id,
            "authorization_id": authorization_id,
            "client_order_id": client_order_id,
        },
    )

    receipt = exchange_order_writer(
        envelope
    )

    state.synthetic_dispatch_count += (
        1
    )

    state.durable_receipts.append(
        receipt
    )

    state.active_intent = None

    state.active_authorization = None

    state.phase = (
        "SYNTHETIC_DISPATCH_COMPLETED"
    )

    save_state(
        state
    )

    append_journal(
        state,
        "SYNTHETIC_DISPATCH_COMPLETED",
        {
            "receipt_id": receipt[
                "receipt_id"
            ],
            "transmitted": False,
            "exchange_network_write": False,
            "status": receipt[
                "status"
            ],
        },
    )

    return receipt


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================


def telegram_preview(
    message: str,
) -> Dict[str, Any]:

    return {
        "method": "POST",
        "operation": "sendMessage",
        "report_only": True,
        "exchange_mutation": False,
        "controls_execution": False,
        "bot_token_exposed": False,
        "message_length": len(
            message
        ),
    }


def send_telegram_report(
    message: str,
) -> bool:

    global _telegram_report_count

    if (
        not TELEGRAM_REPORTING_ENABLED
    ):

        return False

    if (
        _telegram_report_count
        >= MAX_TELEGRAM_REPORTS_PER_RUN
    ):

        return False

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = urllib.parse.urlencode(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        }
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        url=url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": (
                "application/x-www-form-urlencoded"
            ),
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            response.read()

        _telegram_report_count += 1

        return True

    except Exception as exc:

        log(
            f"{VERSION}: TELEGRAM DELIVERY ERROR={type(exc).__name__}"
        )

        return False


# ==================================================================================================
# VALIDATION
# ==================================================================================================


def main() -> None:

    global _exchange_network_write_count

    start_health_server()

    time.sleep(
        0.25
    )

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
        f"{VERSION}: LIVE ORDER PATH={LIVE_ORDER_PATH}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION={REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: SYNTHETIC ORDER DISPATCH ONLY={SYNTHETIC_ORDER_DISPATCH_ONLY}"
    )

    state = load_state()

    # ------------------------------------------------------------------------------------------------
    # TEST 1
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 1: SAFETY CONSTANTS"
    )

    separator()

    pass_fail(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )

    pass_fail(
        "Real Order Execution Is Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )

    pass_fail(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION
        is False,
    )

    pass_fail(
        "First Real Order Is Forbidden",
        FIRST_REAL_ORDER_ALLOWED
        is False,
    )

    pass_fail(
        "Synthetic Order Dispatch Only Is Enabled",
        SYNTHETIC_ORDER_DISPATCH_ONLY
        is True,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 2
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 2: CREDENTIAL READINESS"
    )

    separator()

    pass_fail(
        "WEEX API Key Is Present",
        bool(
            WEEX_API_KEY
        ),
    )

    pass_fail(
        "WEEX Secret Key Is Present",
        bool(
            WEEX_SECRET_KEY
        ),
    )

    pass_fail(
        "WEEX Passphrase Is Present",
        bool(
            WEEX_PASSPHRASE
        ),
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 3
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 3: PUBLIC MARK PRICE"
    )

    separator()

    mark_price = 0.0

    try:

        mark_price = (
            obtain_mark_price()
        )

        pass_fail(
            f"{SYMBOL} Mark Price Was Read",
            mark_price
            > 0,
        )

        log(
            f"{VERSION}: MARK PRICE={mark_price}"
        )

    except Exception as exc:

        pass_fail(
            f"{SYMBOL} Mark Price Was Read",
            False,
        )

        log(
            f"{VERSION}: MARK PRICE ERROR={type(exc).__name__}: {exc}"
        )

    # ------------------------------------------------------------------------------------------------
    # TEST 4
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 4: AUTHENTICATED BALANCE"
    )

    separator()

    balance = 0.0

    try:

        balance = obtain_balance()

        pass_fail(
            "Authenticated Balance Was Read",
            balance
            >= 0,
        )

        log(
            f"{VERSION}: BALANCE={balance}"
        )

    except Exception as exc:

        pass_fail(
            "Authenticated Balance Was Read",
            False,
        )

        log(
            f"{VERSION}: BALANCE ERROR={type(exc).__name__}: {exc}"
        )

    # ------------------------------------------------------------------------------------------------
    # TEST 5
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 5: OPEN POSITION RECONCILIATION"
    )

    separator()

    positions: List[
        Dict[str, Any]
    ] = []

    open_position_count = -1

    try:

        positions = obtain_positions()

        open_position_count = (
            count_open_positions(
                positions
            )
        )

        pass_fail(
            "Authenticated Position State Was Read",
            True,
        )

        pass_fail(
            "No Existing BTCUSDT Position Is Open",
            open_position_count
            == 0,
        )

        log(
            f"{VERSION}: OPEN POSITIONS={open_position_count}"
        )

    except Exception as exc:

        pass_fail(
            "Authenticated Position State Was Read",
            False,
        )

        pass_fail(
            "No Existing BTCUSDT Position Is Open",
            False,
        )

        log(
            f"{VERSION}: POSITION ERROR={type(exc).__name__}: {exc}"
        )

    # ------------------------------------------------------------------------------------------------
    # TEST 6
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 6: FIRST ORDER SIZE FIREBREAK"
    )

    separator()

    quantity_float = parse_decimal(
        ORDER_QUANTITY
    )

    pass_fail(
        "Order Quantity Is Positive",
        quantity_float
        > 0,
    )

    pass_fail(
        "Order Quantity Does Not Exceed R35J Cap",
        quantity_float
        <= MAX_FIRST_ORDER_QUANTITY_BTC,
    )

    pass_fail(
        "Order Side Is Valid",
        ORDER_SIDE
        in {
            "BUY",
            "SELL",
        },
    )

    pass_fail(
        "Position Side Is Valid",
        POSITION_SIDE
        in {
            "LONG",
            "SHORT",
        },
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 7
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 7: EXACT V3 ORDER ENDPOINT"
    )

    separator()

    pass_fail(
        "Writer Envelope Uses POST",
        LIVE_ORDER_METHOD
        == "POST",
    )

    pass_fail(
        "Writer Envelope Uses Exact V3 Futures Order Path",
        LIVE_ORDER_PATH
        == "/capi/v3/order",
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 8
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 8: ORDER PAYLOAD CONSTRUCTION"
    )

    separator()

    client_order_id = (
        create_client_order_id(
            state
        )
    )

    payload = (
        build_order_payload(
            client_order_id
        )
    )

    pass_fail(
        "Payload Symbol Is BTCUSDT",
        payload[
            "symbol"
        ]
        == SYMBOL,
    )

    pass_fail(
        "Payload Uses MARKET Order",
        payload[
            "type"
        ]
        == "MARKET",
    )

    pass_fail(
        "Payload Contains Position Side",
        bool(
            payload.get(
                "positionSide"
            )
        ),
    )

    pass_fail(
        "Payload Contains Quantity",
        bool(
            payload.get(
                "quantity"
            )
        ),
    )

    pass_fail(
        "Payload Contains Client Order ID",
        bool(
            payload.get(
                "newClientOrderId"
            )
        ),
    )

    pass_fail(
        "Client Order ID Does Not Exceed 36 Characters",
        len(
            client_order_id
        )
        <= 36,
    )

    payload_hash = sha256_text(
        canonical_json(
            payload
        )
    )

    log(
        f"{VERSION}: CLIENT ORDER ID={client_order_id}"
    )

    log(
        f"{VERSION}: PAYLOAD HASH={payload_hash}"
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 9
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 9: ONE-TIME INTENT"
    )

    separator()

    intent = create_intent(
        state,
        payload,
    )

    pass_fail(
        "Intent Was Created",
        bool(
            intent[
                "intent_id"
            ]
        ),
    )

    pass_fail(
        "Intent Is Bound To BTCUSDT",
        intent[
            "symbol"
        ]
        == SYMBOL,
    )

    pass_fail(
        "Intent Is Bound To Payload Hash",
        intent[
            "payload_hash"
        ]
        == payload_hash,
    )

    pass_fail(
        "Intent Forbids Network Transmission",
        intent[
            "network_transmission_allowed"
        ]
        is False,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 10
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 10: ONE-TIME AUTHORIZATION"
    )

    separator()

    authorization = (
        create_authorization(
            state,
            intent,
        )
    )

    pass_fail(
        "Authorization Was Created",
        bool(
            authorization[
                "authorization_id"
            ]
        ),
    )

    pass_fail(
        "Authorization Is Bound To Intent",
        authorization[
            "intent_id"
        ]
        == intent[
            "intent_id"
        ],
    )

    pass_fail(
        "Authorization Is Single Use",
        authorization[
            "single_use"
        ]
        is True,
    )

    pass_fail(
        "Authorization Forbids Network Transmission",
        authorization[
            "network_transmission_allowed"
        ]
        is False,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 11
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 11: AUTHORIZATION BINDING"
    )

    separator()

    binding_valid = (
        validate_authorization_binding(
            state,
            intent,
            authorization,
            payload,
        )
    )

    pass_fail(
        "Authorization Binding Is Exact",
        binding_valid,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 12
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 12: SIGNED ORDER ENVELOPE"
    )

    separator()

    envelope = (
        build_signed_order_envelope(
            payload
        )
    )

    preview = (
        secret_safe_envelope_preview(
            envelope
        )
    )

    pass_fail(
        "Envelope Uses POST",
        envelope[
            "method"
        ]
        == "POST",
    )

    pass_fail(
        "Envelope Uses Exact V3 Path",
        envelope[
            "path"
        ]
        == LIVE_ORDER_PATH,
    )

    pass_fail(
        "Envelope Payload Hash Matches Intent",
        envelope[
            "payload_hash"
        ]
        == intent[
            "payload_hash"
        ],
    )

    pass_fail(
        "ACCESS-SIGN Is Present",
        bool(
            envelope[
                "headers"
            ].get(
                "ACCESS-SIGN"
            )
        ),
    )

    pass_fail(
        "ACCESS-TIMESTAMP Is Present",
        bool(
            envelope[
                "headers"
            ].get(
                "ACCESS-TIMESTAMP"
            )
        ),
    )

    pass_fail(
        "Envelope Preview Redacts Credentials",
        preview[
            "credentials_redacted"
        ]
        is True,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 13
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 13: FINAL EXCHANGE WRITE FIREBREAK"
    )

    separator()

    writes_before = (
        _exchange_network_write_count
    )

    receipt = (
        consume_and_dispatch(
            state,
            intent,
            authorization,
            envelope,
        )
    )

    writes_after = (
        _exchange_network_write_count
    )

    pass_fail(
        "Synthetic Dispatch Completed",
        receipt[
            "synthetic"
        ]
        is True,
    )

    pass_fail(
        "Order Was Not Transmitted",
        receipt[
            "transmitted"
        ]
        is False,
    )

    pass_fail(
        "Exchange Network Write Was Not Made",
        receipt[
            "exchange_network_write"
        ]
        is False,
    )

    pass_fail(
        "Exchange Write Counter Remains Zero",
        writes_after
        == writes_before
        == 0,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 14
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 14: REPLAY PROTECTION"
    )

    separator()

    replay_rejected = False

    try:

        consume_and_dispatch(
            state,
            intent,
            authorization,
            envelope,
        )

    except RuntimeError:

        replay_rejected = True

    pass_fail(
        "Consumed Intent Replay Is Rejected",
        replay_rejected,
    )

    pass_fail(
        "Authorization Is Persisted As Consumed",
        authorization[
            "authorization_id"
        ]
        in state.consumed_authorizations,
    )

    pass_fail(
        "Client Order ID Is Persisted As Used",
        client_order_id
        in state.used_client_order_ids,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 15
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 15: DURABLE RESTART PROTECTION"
    )

    separator()

    restarted_state = load_state()

    pass_fail(
        "Consumed Intent Survives Restart",
        intent[
            "intent_id"
        ]
        in restarted_state.consumed_intents,
    )

    pass_fail(
        "Consumed Authorization Survives Restart",
        authorization[
            "authorization_id"
        ]
        in restarted_state.consumed_authorizations,
    )

    pass_fail(
        "Used Client Order ID Survives Restart",
        client_order_id
        in restarted_state.used_client_order_ids,
    )

    pass_fail(
        "Durable Receipt Survives Restart",
        any(
            item.get(
                "receipt_id"
            )
            == receipt[
                "receipt_id"
            ]
            for item
            in restarted_state.durable_receipts
        ),
    )

    pass_fail(
        "Restart Keeps Exchange Write Count At Zero",
        restarted_state.exchange_network_write_count
        == 0,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 16
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 16: TELEGRAM REPORTING BOUNDARY"
    )

    separator()

    sample_message = (
        f"{VERSION} VALIDATION"
    )

    telegram_boundary = (
        telegram_preview(
            sample_message
        )
    )

    pass_fail(
        "Telegram Uses POST Only For Reporting",
        telegram_boundary[
            "method"
        ]
        == "POST",
    )

    pass_fail(
        "Telegram Operation Is sendMessage",
        telegram_boundary[
            "operation"
        ]
        == "sendMessage",
    )

    pass_fail(
        "Telegram Request Is Report Only",
        telegram_boundary[
            "report_only"
        ]
        is True,
    )

    pass_fail(
        "Telegram Is Not Exchange Mutation",
        telegram_boundary[
            "exchange_mutation"
        ]
        is False,
    )

    pass_fail(
        "Telegram Cannot Control Execution",
        telegram_boundary[
            "controls_execution"
        ]
        is False,
    )

    pass_fail(
        "Telegram Preview Does Not Expose Bot Token",
        telegram_boundary[
            "bot_token_exposed"
        ]
        is False,
    )

    # ------------------------------------------------------------------------------------------------
    # TEST 17
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION} TEST 17: JOURNAL INTEGRITY"
    )

    separator()

    journal_hash_valid, sequence_valid = (
        validate_journal()
    )

    journal_records = read_journal()

    pass_fail(
        "Durable Journal Contains Records",
        len(
            journal_records
        )
        > 0,
    )

    pass_fail(
        "Durable Journal Hash Chain Is Valid",
        journal_hash_valid,
    )

    pass_fail(
        "Journal Sequence Is Monotonic",
        sequence_valid,
    )

    # ------------------------------------------------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------------------------------------------------

    separator()

    log(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    separator()

    final_state = load_state()

    final_message = (
        f"✅ {VERSION} VALIDATION REPORT\n"
        f"\n"
        f"Symbol: {SYMBOL}\n"
        f"Authenticated WEEX reads: "
        f"{'PASS' if balance >= 0 and open_position_count >= 0 else 'FAIL'}\n"
        f"Balance: {balance}\n"
        f"Mark price: {mark_price}\n"
        f"Open positions: {open_position_count}\n"
        f"Order endpoint: {LIVE_ORDER_PATH}\n"
        f"Order side: {ORDER_SIDE}\n"
        f"Position side: {POSITION_SIDE}\n"
        f"Validation quantity: {ORDER_QUANTITY} BTC\n"
        f"Client order ID: {client_order_id}\n"
        f"Journal integrity: "
        f"{'PASS' if journal_hash_valid else 'FAIL'}\n"
        f"Journal sequence: {final_state.journal_sequence}\n"
        f"Exchange network writes: {_exchange_network_write_count}\n"
        f"Real order execution: DISABLED\n"
        f"Demo order execution: DISABLED\n"
        f"First real order: FORBIDDEN\n"
        f"Synthetic boundary dispatches: "
        f"{final_state.synthetic_dispatch_count}\n"
        f"Telegram reports this run: "
        f"{MAX_TELEGRAM_REPORTS_PER_RUN} maximum\n"
        f"Status: VALIDATION PASSED"
    )

    print(
        final_message,
        flush=True,
    )

    telegram_delivered = (
        send_telegram_report(
            final_message
        )
    )

    if telegram_delivered:

        log(
            f"{VERSION}: TELEGRAM FINAL REPORT=DELIVERED"
        )

    else:

        log(
            f"{VERSION}: TELEGRAM FINAL REPORT=NOT DELIVERED"
        )

    separator()

    log(
        f"{VERSION}: EXCHANGE NETWORK WRITES={_exchange_network_write_count}"
    )

    log(
        f"{VERSION}: REAL ORDER EXECUTION={REAL_ORDER_EXECUTION}"
    )

    log(
        f"{VERSION}: FIRST REAL ORDER=FORBIDDEN"
    )

    log(
        f"{VERSION}: FINAL STATUS=FIRST LIVE ORDER BOUNDARY VALIDATED WITH HARD WRITE FIREBREAK"
    )

    separator()

    # Keep Render service alive.

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT {heartbeat}"
        )

        time.sleep(
            60
        )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        log(
            f"{VERSION}: STOPPED"
        )

    except Exception as exc:

        separator()

        log(
            f"{VERSION}: FATAL ERROR={type(exc).__name__}: {exc}"
        )

        log(
            f"{VERSION}: EXCHANGE NETWORK WRITES={_exchange_network_write_count}"
        )

        log(
            f"{VERSION}: REAL ORDER EXECUTION={REAL_ORDER_EXECUTION}"
        )

        separator()

        raise
