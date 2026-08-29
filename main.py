

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
# R35K - FINAL PRE-LIVE AUTHENTICATED RECONCILIATION / FAIL-CLOSED GATE
# ==================================================================================================
#
# PURPOSE
#
# R35K closes the readiness gap discovered in R35J:
#
#     Authenticated WEEX reads: FAIL
#     Balance: 0.0
#     Mark price: 0.0
#     Open positions: -1
#
# R35K requires REAL, SUCCESSFUL, CURRENT exchange observations before a future live execution stage
# can become eligible.
#
# R35K DOES NOT PLACE ORDERS.
#
# SAFETY MODEL
#
#   - PUBLIC GET READS ONLY
#   - AUTHENTICATED GET READS ONLY
#   - NO EXCHANGE POST
#   - NO EXCHANGE PUT
#   - NO EXCHANGE PATCH
#   - NO EXCHANGE DELETE
#   - REAL ORDER EXECUTION DISABLED
#   - DEMO ORDER EXECUTION DISABLED
#   - FIRST REAL ORDER FORBIDDEN
#   - TELEGRAM POST IS REPORTING ONLY
#   - TELEGRAM CANNOT CONTROL EXECUTION
#   - FAIL CLOSED ON ANY AMBIGUOUS ACCOUNT STATE
#   - FAIL CLOSED ON ANY AUTHENTICATED READ FAILURE
#   - FAIL CLOSED ON INVALID / ZERO MARK PRICE
#   - FAIL CLOSED ON INVALID BALANCE
#   - FAIL CLOSED ON POSITION RECONCILIATION FAILURE
#   - FAIL CLOSED ON SYMBOL CONFIGURATION FAILURE
#   - FAIL CLOSED IF MARGIN MODE IS NOT ISOLATED
#   - FAIL CLOSED IF REQUIRED LEVERAGE IS NOT VERIFIED
#
# IMPORTANT
#
# R35K may prove PRE-LIVE READINESS.
# It does NOT authorize live trading.
#
# ==================================================================================================


VERSION = "R35K"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

HEALTH_PORT = int(os.getenv("PORT", "10000"))

WEEX_BASE_URL = os.getenv(
    "WEEX_BASE_URL",
    "https://api-contract.weex.com",
).rstrip("/")

API_KEY = os.getenv("WEEX_API_KEY", "").strip()
API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

STATE_DIR = Path(
    os.getenv(
        "R35K_STATE_DIR",
        "/tmp/r35k_state",
    )
)

STATE_FILE = STATE_DIR / "state.json"
JOURNAL_FILE = STATE_DIR / "journal.jsonl"

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv(
        "REQUEST_TIMEOUT_SECONDS",
        "12",
    )
)

HEARTBEAT_SECONDS = int(
    os.getenv(
        "HEARTBEAT_SECONDS",
        "60",
    )
)

TARGET_MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = int(
    os.getenv(
        "TARGET_LONG_LEVERAGE",
        "100",
    )
)

TARGET_SHORT_LEVERAGE = int(
    os.getenv(
        "TARGET_SHORT_LEVERAGE",
        "100",
    )
)

VALIDATION_QTY_BTC = float(
    os.getenv(
        "VALIDATION_QTY_BTC",
        "0.0001",
    )
)

ORDER_ENDPOINT = "/capi/v3/order"

# --------------------------------------------------------------------------------------------------
# ABSOLUTE EXECUTION FIREBREAK
# --------------------------------------------------------------------------------------------------

EXCHANGE_NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

FIRST_REAL_ORDER_ALLOWED = False

LIVE_EXECUTION_AUTHORIZED = False

ALLOW_LEVERAGE_MUTATION = False

ALLOW_MARGIN_MUTATION = False

ALLOW_POSITION_MUTATION = False

ALLOW_ORDER_MUTATION = False


# ==================================================================================================
# LOGGING
# ==================================================================================================


LINE = "-" * 100


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str = "") -> None:
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


def section(title: str) -> None:
    log(LINE)
    log(title)
    log(LINE)


def result(
    name: str,
    passed: bool,
) -> bool:

    status = "✅ PASS" if passed else "❌ FAIL"

    print(
        f"{name:<84} {status}",
        flush=True,
    )

    return passed


# ==================================================================================================
# DATA MODELS
# ==================================================================================================


@dataclass
class ExchangeObservation:

    authenticated_reads_ok: bool = False

    credentials_present: bool = False

    balance_read_ok: bool = False

    mark_price_read_ok: bool = False

    positions_read_ok: bool = False

    symbol_config_read_ok: bool = False

    available_balance: Optional[float] = None

    mark_price: Optional[float] = None

    open_positions: Optional[int] = None

    margin_mode: Optional[str] = None

    isolated_long_leverage: Optional[int] = None

    isolated_short_leverage: Optional[int] = None

    position_mode: Optional[str] = None

    raw_balance_response: Optional[Any] = None

    raw_positions_response: Optional[Any] = None

    raw_symbol_config_response: Optional[Any] = None

    raw_mark_price_response: Optional[Any] = None

    failure_reasons: List[str] = field(
        default_factory=list
    )


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    phase: str = "BOOT"

    terminal: bool = False

    live_readiness: bool = False

    execution_authorized: bool = False

    exchange_network_writes: int = 0

    synthetic_boundary_dispatches: int = 0

    telegram_reports_this_run: int = 0

    last_journal_hash: str = "0" * 64

    journal_sequence: int = 0

    observation: Dict[str, Any] = field(
        default_factory=dict
    )

    failure_reasons: List[str] = field(
        default_factory=list
    )

    created_at: str = field(
        default_factory=utc_now
    )

    updated_at: str = field(
        default_factory=utc_now
    )


STATE_LOCK = threading.RLock()

STATE = StrategyState()


# ==================================================================================================
# DURABLE FILE HELPERS
# ==================================================================================================


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

    temp_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(serialized)

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_path,
        path,
    )


def save_state() -> None:

    with STATE_LOCK:

        STATE.updated_at = utc_now()

        atomic_write_json(
            STATE_FILE,
            asdict(STATE),
        )


def load_previous_state() -> Optional[Dict[str, Any]]:

    if not STATE_FILE.exists():
        return None

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as handle:

            data = json.load(
                handle
            )

        if not isinstance(
            data,
            dict,
        ):
            return None

        return data

    except Exception as exc:

        log(
            f"R35K: PREVIOUS STATE READ FAILED: "
            f"{type(exc).__name__}: {exc}"
        )

        return None


# ==================================================================================================
# JOURNAL
# ==================================================================================================


def canonical_json(
    payload: Dict[str, Any],
) -> str:

    return json.dumps(
        payload,
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


def append_journal(
    event: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    global STATE

    ensure_state_dir()

    with STATE_LOCK:

        STATE.journal_sequence += 1

        record = {
            "sequence": STATE.journal_sequence,
            "timestamp": utc_now(),
            "version": VERSION,
            "symbol": SYMBOL,
            "generation": STATE.generation,
            "epoch": STATE.epoch,
            "event": event,
            "details": details or {},
            "previous_hash": STATE.last_journal_hash,
        }

        record_hash = sha256_text(
            canonical_json(record)
        )

        full_record = dict(
            record
        )

        full_record["record_hash"] = record_hash

        with open(
            JOURNAL_FILE,
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                canonical_json(
                    full_record
                )
                + "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        STATE.last_journal_hash = record_hash

        save_state()

        return full_record


def validate_journal() -> Tuple[
    bool,
    int,
    Optional[str],
]:

    if not JOURNAL_FILE.exists():

        return (
            False,
            0,
            "journal file missing",
        )

    expected_previous_hash = "0" * 64

    expected_sequence = 1

    count = 0

    try:

        with open(
            JOURNAL_FILE,
            "r",
            encoding="utf-8",
        ) as handle:

            for raw_line in handle:

                line = raw_line.strip()

                if not line:
                    continue

                record = json.loads(
                    line
                )

                stored_hash = record.get(
                    "record_hash"
                )

                if not isinstance(
                    stored_hash,
                    str,
                ):
                    return (
                        False,
                        count,
                        "journal record hash missing",
                    )

                unsigned_record = dict(
                    record
                )

                unsigned_record.pop(
                    "record_hash",
                    None,
                )

                calculated_hash = sha256_text(
                    canonical_json(
                        unsigned_record
                    )
                )

                if stored_hash != calculated_hash:

                    return (
                        False,
                        count,
                        "journal record hash mismatch",
                    )

                if record.get(
                    "previous_hash"
                ) != expected_previous_hash:

                    return (
                        False,
                        count,
                        "journal previous hash mismatch",
                    )

                if record.get(
                    "sequence"
                ) != expected_sequence:

                    return (
                        False,
                        count,
                        "journal sequence mismatch",
                    )

                expected_previous_hash = stored_hash

                expected_sequence += 1

                count += 1

        return (
            count > 0,
            count,
            None,
        )

    except Exception as exc:

        return (
            False,
            count,
            f"{type(exc).__name__}: {exc}",
        )


# ==================================================================================================
# HTTP HELPERS
# ==================================================================================================


def decode_json_response(
    raw: bytes,
) -> Any:

    text = raw.decode(
        "utf-8",
        errors="replace",
    )

    if not text.strip():
        return {}

    return json.loads(
        text
    )


def public_get(
    path: str,
    query: Optional[Dict[str, Any]] = None,
) -> Any:

    if not path.startswith("/"):
        raise ValueError(
            "public path must start with /"
        )

    encoded_query = ""

    if query:

        encoded_query = urllib.parse.urlencode(
            query
        )

    url = WEEX_BASE_URL + path

    if encoded_query:
        url += "?" + encoded_query

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": f"{VERSION}/1.0",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        return decode_json_response(
            response.read()
        )


# ==================================================================================================
# WEEX AUTHENTICATION
# ==================================================================================================


def credentials_present() -> bool:

    return bool(
        API_KEY
        and API_SECRET
        and API_PASSPHRASE
    )


def build_weex_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    path_with_query = request_path

    if query_string:

        path_with_query += (
            "?" + query_string
        )

    prehash = (
        timestamp
        + method
        + path_with_query
        + body
    )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


def authenticated_get(
    path: str,
    query: Optional[Dict[str, Any]] = None,
) -> Any:

    if not credentials_present():

        raise RuntimeError(
            "WEEX credentials are incomplete"
        )

    if not path.startswith("/"):

        raise ValueError(
            "authenticated path must start with /"
        )

    encoded_query = ""

    if query:

        encoded_query = urllib.parse.urlencode(
            query
        )

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = build_weex_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=encoded_query,
        body="",
    )

    url = WEEX_BASE_URL + path

    if encoded_query:

        url += (
            "?" + encoded_query
        )

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}/1.0",
    }

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers=headers,
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        return decode_json_response(
            response.read()
        )


# ==================================================================================================
# JSON EXTRACTION HELPERS
# ==================================================================================================


def unwrap_data(
    payload: Any,
) -> Any:

    if isinstance(
        payload,
        dict,
    ):

        if "data" in payload:

            return payload[
                "data"
            ]

    return payload


def safe_float(
    value: Any,
) -> Optional[float]:

    if value is None:
        return None

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


def safe_int(
    value: Any,
) -> Optional[int]:

    if value is None:
        return None

    try:

        return int(
            float(
                value
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


def recursive_find_first(
    payload: Any,
    keys: List[str],
) -> Any:

    lowered = {
        key.lower()
        for key in keys
    }

    if isinstance(
        payload,
        dict,
    ):

        for key, value in payload.items():

            if str(
                key
            ).lower() in lowered:

                return value

        for value in payload.values():

            found = recursive_find_first(
                value,
                keys,
            )

            if found is not None:
                return found

    elif isinstance(
        payload,
        list,
    ):

        for item in payload:

            found = recursive_find_first(
                item,
                keys,
            )

            if found is not None:
                return found

    return None


# ==================================================================================================
# EXCHANGE READS
# ==================================================================================================


def read_mark_price() -> Tuple[
    bool,
    Optional[float],
    Any,
    Optional[str],
]:

    candidate_endpoints = [
        (
            "/capi/v2/market/ticker",
            {"symbol": SYMBOL},
        ),
        (
            "/capi/v3/market/ticker",
            {"symbol": SYMBOL},
        ),
        (
            "/capi/v2/market/symbolPrice",
            {"symbol": SYMBOL},
        ),
        (
            "/capi/v3/market/symbolPrice",
            {"symbol": SYMBOL},
        ),
    ]

    last_error: Optional[str] = None

    last_payload: Any = None

    for path, query in candidate_endpoints:

        try:

            payload = public_get(
                path,
                query,
            )

            last_payload = payload

            value = recursive_find_first(
                payload,
                [
                    "markPrice",
                    "mark_price",
                    "price",
                    "lastPrice",
                    "last",
                    "close",
                ],
            )

            price = safe_float(
                value
            )

            if (
                price is not None
                and price > 0
            ):

                return (
                    True,
                    price,
                    payload,
                    None,
                )

        except Exception as exc:

            last_error = (
                f"{path}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

    return (
        False,
        None,
        last_payload,
        last_error
        or "no positive mark price found",
    )


def read_balance() -> Tuple[
    bool,
    Optional[float],
    Any,
    Optional[str],
]:

    candidate_endpoints = [
        (
            "/capi/v2/account/assets",
            {},
        ),
        (
            "/capi/v3/account/assets",
            {},
        ),
        (
            "/capi/v2/account/balance",
            {},
        ),
        (
            "/capi/v3/account/balance",
            {},
        ),
    ]

    last_error: Optional[str] = None

    last_payload: Any = None

    for path, query in candidate_endpoints:

        try:

            payload = authenticated_get(
                path,
                query,
            )

            last_payload = payload

            data = unwrap_data(
                payload
            )

            balance = extract_usdt_balance(
                data
            )

            if balance is not None:

                return (
                    True,
                    balance,
                    payload,
                    None,
                )

        except Exception as exc:

            last_error = (
                f"{path}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

    return (
        False,
        None,
        last_payload,
        last_error
        or "USDT balance not found",
    )


def extract_usdt_balance(
    data: Any,
) -> Optional[float]:

    if isinstance(
        data,
        list,
    ):

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            coin = str(
                item.get(
                    "coin",
                    item.get(
                        "asset",
                        item.get(
                            "currency",
                            "",
                        ),
                    ),
                )
            ).upper()

            if coin == "USDT":

                for key in [
                    "available",
                    "availableBalance",
                    "available_balance",
                    "balance",
                    "equity",
                ]:

                    value = safe_float(
                        item.get(
                            key
                        )
                    )

                    if value is not None:

                        return value

    if isinstance(
        data,
        dict,
    ):

        direct_coin = str(
            data.get(
                "coin",
                data.get(
                    "asset",
                    data.get(
                        "currency",
                        "",
                    ),
                ),
            )
        ).upper()

        if direct_coin in (
            "",
            "USDT",
        ):

            for key in [
                "available",
                "availableBalance",
                "available_balance",
                "balance",
                "equity",
            ]:

                value = safe_float(
                    data.get(
                        key
                    )
                )

                if value is not None:

                    return value

        for value in data.values():

            result_value = extract_usdt_balance(
                value
            )

            if result_value is not None:

                return result_value

    return None


def read_positions() -> Tuple[
    bool,
    Optional[int],
    Any,
    Optional[str],
]:

    candidate_endpoints = [
        (
            "/capi/v2/account/allPosition",
            {},
        ),
        (
            "/capi/v3/account/allPosition",
            {},
        ),
        (
            "/capi/v2/position/allPosition",
            {},
        ),
    ]

    last_error: Optional[str] = None

    last_payload: Any = None

    for path, query in candidate_endpoints:

        try:

            payload = authenticated_get(
                path,
                query,
            )

            last_payload = payload

            count = count_open_positions(
                unwrap_data(
                    payload
                )
            )

            if count is not None:

                return (
                    True,
                    count,
                    payload,
                    None,
                )

        except Exception as exc:

            last_error = (
                f"{path}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

    return (
        False,
        None,
        last_payload,
        last_error
        or "positions could not be reconciled",
    )


def count_open_positions(
    data: Any,
) -> Optional[int]:

    if isinstance(
        data,
        dict,
    ):

        for key in [
            "list",
            "positions",
            "positionList",
            "rows",
        ]:

            if key in data:

                return count_open_positions(
                    data[
                        key
                    ]
                )

        symbol_value = str(
            data.get(
                "symbol",
                "",
            )
        ).upper()

        if symbol_value:

            qty = recursive_find_first(
                data,
                [
                    "positionQty",
                    "positionAmt",
                    "holdVol",
                    "total",
                    "size",
                    "qty",
                    "position",
                ],
            )

            qty_float = safe_float(
                qty
            )

            if qty_float is None:

                return 0

            return (
                1
                if abs(
                    qty_float
                ) > 0
                else 0
            )

    if isinstance(
        data,
        list,
    ):

        count = 0

        for item in data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            item_symbol = str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()

            if (
                item_symbol
                and item_symbol != SYMBOL
            ):
                continue

            qty = recursive_find_first(
                item,
                [
                    "positionQty",
                    "positionAmt",
                    "holdVol",
                    "total",
                    "size",
                    "qty",
                    "position",
                ],
            )

            qty_float = safe_float(
                qty
            )

            if (
                qty_float is not None
                and abs(
                    qty_float
                ) > 0
            ):

                count += 1

        return count

    return None


def read_symbol_config() -> Tuple[
    bool,
    Optional[Dict[str, Any]],
    Any,
    Optional[str],
]:

    candidate_endpoints = [
        (
            "/capi/v2/account/symbolConfig",
            {"symbol": SYMBOL},
        ),
        (
            "/capi/v3/account/symbolConfig",
            {"symbol": SYMBOL},
        ),
    ]

    last_error: Optional[str] = None

    last_payload: Any = None

    for path, query in candidate_endpoints:

        try:

            payload = authenticated_get(
                path,
                query,
            )

            last_payload = payload

            config = parse_symbol_config(
                unwrap_data(
                    payload
                )
            )

            if config is not None:

                return (
                    True,
                    config,
                    payload,
                    None,
                )

        except Exception as exc:

            last_error = (
                f"{path}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

    return (
        False,
        None,
        last_payload,
        last_error
        or "symbol config not found",
    )


def parse_symbol_config(
    data: Any,
) -> Optional[Dict[str, Any]]:

    candidates: List[Dict[str, Any]] = []

    if isinstance(
        data,
        dict,
    ):

        candidates.append(
            data
        )

        for value in data.values():

            if isinstance(
                value,
                dict,
            ):
                candidates.append(
                    value
                )

            elif isinstance(
                value,
                list,
            ):

                for item in value:

                    if isinstance(
                        item,
                        dict,
                    ):
                        candidates.append(
                            item
                        )

    elif isinstance(
        data,
        list,
    ):

        candidates.extend(
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        )

    if not candidates:

        return None

    selected: Optional[
        Dict[str, Any]
    ] = None

    for item in candidates:

        item_symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if item_symbol == SYMBOL:

            selected = item

            break

    if selected is None:

        selected = candidates[
            0
        ]

    margin_mode = recursive_find_first(
        selected,
        [
            "marginType",
            "marginMode",
            "margin_mode",
        ],
    )

    long_leverage = recursive_find_first(
        selected,
        [
            "isolatedLongLeverage",
            "longLeverage",
            "isolated_long_leverage",
        ],
    )

    short_leverage = recursive_find_first(
        selected,
        [
            "isolatedShortLeverage",
            "shortLeverage",
            "isolated_short_leverage",
        ],
    )

    position_mode = recursive_find_first(
        selected,
        [
            "positionMode",
            "position_mode",
            "holdMode",
        ],
    )

    return {
        "margin_mode": (
            str(
                margin_mode
            ).upper()
            if margin_mode is not None
            else None
        ),
        "isolated_long_leverage": safe_int(
            long_leverage
        ),
        "isolated_short_leverage": safe_int(
            short_leverage
        ),
        "position_mode": (
            str(
                position_mode
            ).upper()
            if position_mode is not None
            else None
        ),
    }


# ==================================================================================================
# RECONCILIATION
# ==================================================================================================


def perform_exchange_reconciliation() -> ExchangeObservation:

    observation = ExchangeObservation()

    observation.credentials_present = credentials_present()

    if not observation.credentials_present:

        observation.failure_reasons.append(
            "WEEX credentials are incomplete"
        )

        return observation

    (
        mark_ok,
        mark_price,
        mark_raw,
        mark_error,
    ) = read_mark_price()

    observation.mark_price_read_ok = mark_ok
    observation.mark_price = mark_price
    observation.raw_mark_price_response = mark_raw

    if not mark_ok:

        observation.failure_reasons.append(
            "mark price read failed: "
            + str(
                mark_error
            )
        )

    (
        balance_ok,
        balance,
        balance_raw,
        balance_error,
    ) = read_balance()

    observation.balance_read_ok = balance_ok
    observation.available_balance = balance
    observation.raw_balance_response = balance_raw

    if not balance_ok:

        observation.failure_reasons.append(
            "authenticated balance read failed: "
            + str(
                balance_error
            )
        )

    (
        positions_ok,
        open_positions,
        positions_raw,
        positions_error,
    ) = read_positions()

    observation.positions_read_ok = positions_ok
    observation.open_positions = open_positions
    observation.raw_positions_response = positions_raw

    if not positions_ok:

        observation.failure_reasons.append(
            "authenticated position read failed: "
            + str(
                positions_error
            )
        )

    (
        config_ok,
        config,
        config_raw,
        config_error,
    ) = read_symbol_config()

    observation.symbol_config_read_ok = config_ok
    observation.raw_symbol_config_response = config_raw

    if config_ok and config:

        observation.margin_mode = config.get(
            "margin_mode"
        )

        observation.isolated_long_leverage = config.get(
            "isolated_long_leverage"
        )

        observation.isolated_short_leverage = config.get(
            "isolated_short_leverage"
        )

        observation.position_mode = config.get(
            "position_mode"
        )

    else:

        observation.failure_reasons.append(
            "authenticated symbol config read failed: "
            + str(
                config_error
            )
        )

    observation.authenticated_reads_ok = (
        observation.credentials_present
        and observation.balance_read_ok
        and observation.positions_read_ok
        and observation.symbol_config_read_ok
    )

    return observation


# ==================================================================================================
# FAIL-CLOSED LIVE READINESS EVALUATION
# ==================================================================================================


def evaluate_live_readiness(
    observation: ExchangeObservation,
) -> Tuple[
    bool,
    List[str],
]:

    failures: List[str] = []

    if not observation.credentials_present:

        failures.append(
            "credentials not present"
        )

    if not observation.authenticated_reads_ok:

        failures.append(
            "authenticated WEEX reconciliation incomplete"
        )

    if not observation.balance_read_ok:

        failures.append(
            "balance read not verified"
        )

    if observation.available_balance is None:

        failures.append(
            "available balance is unknown"
        )

    elif observation.available_balance < 0:

        failures.append(
            "available balance is invalid"
        )

    if not observation.mark_price_read_ok:

        failures.append(
            "mark price read not verified"
        )

    if observation.mark_price is None:

        failures.append(
            "mark price is unknown"
        )

    elif observation.mark_price <= 0:

        failures.append(
            "mark price is not positive"
        )

    if not observation.positions_read_ok:

        failures.append(
            "positions are not reconciled"
        )

    if observation.open_positions is None:

        failures.append(
            "open position count is unknown"
        )

    elif observation.open_positions < 0:

        failures.append(
            "open position count is invalid"
        )

    if not observation.symbol_config_read_ok:

        failures.append(
            "symbol configuration is not reconciled"
        )

    if observation.margin_mode != TARGET_MARGIN_MODE:

        failures.append(
            f"margin mode is "
            f"{observation.margin_mode!r}, "
            f"required={TARGET_MARGIN_MODE}"
        )

    if (
        observation.isolated_long_leverage
        != TARGET_LONG_LEVERAGE
    ):

        failures.append(
            "isolated long leverage is "
            f"{observation.isolated_long_leverage!r}, "
            f"required={TARGET_LONG_LEVERAGE}"
        )

    if (
        observation.isolated_short_leverage
        != TARGET_SHORT_LEVERAGE
    ):

        failures.append(
            "isolated short leverage is "
            f"{observation.isolated_short_leverage!r}, "
            f"required={TARGET_SHORT_LEVERAGE}"
        )

    # Execution is intentionally still prohibited in R35K.
    #
    # Therefore live_readiness means:
    #
    #     "exchange observations satisfy prerequisites"
    #
    # NOT:
    #
    #     "orders may now be sent"

    ready = len(
        failures
    ) == 0

    return (
        ready,
        failures,
    )


# ==================================================================================================
# SYNTHETIC FUTURE ORDER ENVELOPE
# ==================================================================================================


def next_nonce() -> int:

    with STATE_LOCK:

        STATE.highest_nonce += 1

        save_state()

        return STATE.highest_nonce


def create_validation_client_order_id(
    nonce: int,
) -> str:

    suffix = int(
        time.time()
    )

    return (
        f"{VERSION}-"
        f"G{STATE.generation}-"
        f"E{STATE.epoch}-"
        f"N{nonce}-"
        f"{suffix}"
    )


def build_synthetic_order_envelope(
    client_order_id: str,
) -> Dict[str, Any]:

    return {
        "method": "POST",
        "path": ORDER_ENDPOINT,
        "exchange": "WEEX",
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "orderType": "MARKET",
        "quantity": f"{VALIDATION_QTY_BTC:.4f}",
        "clientOrderId": client_order_id,
        "synthetic": True,
        "transmissionAllowed": False,
        "networkWriteAllowed": False,
        "realOrderAllowed": False,
        "demoOrderAllowed": False,
        "generation": STATE.generation,
        "epoch": STATE.epoch,
    }


def synthetic_boundary_dispatch(
    envelope: Dict[str, Any],
) -> Dict[str, Any]:

    if envelope.get(
        "transmissionAllowed"
    ) is not False:

        raise RuntimeError(
            "R35K synthetic envelope unexpectedly allows transmission"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:

        raise RuntimeError(
            "R35K exchange network write flag unexpectedly enabled"
        )

    if REAL_ORDER_EXECUTION:

        raise RuntimeError(
            "R35K real order execution unexpectedly enabled"
        )

    if FIRST_REAL_ORDER_ALLOWED:

        raise RuntimeError(
            "R35K first real order unexpectedly allowed"
        )

    with STATE_LOCK:

        STATE.synthetic_boundary_dispatches += 1

        save_state()

    receipt = {
        "timestamp": utc_now(),
        "status": "SYNTHETIC_ONLY",
        "transmitted": False,
        "exchangeNetworkWrite": False,
        "clientOrderId": envelope.get(
            "clientOrderId"
        ),
        "path": envelope.get(
            "path"
        ),
        "method": envelope.get(
            "method"
        ),
    }

    append_journal(
        "SYNTHETIC_BOUNDARY_DISPATCH",
        receipt,
    )

    return receipt


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================


def telegram_configured() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


def telegram_preview() -> Dict[str, Any]:

    return {
        "method": "POST",
        "service": "TELEGRAM",
        "operation": "sendMessage",
        "purpose": "REPORT_ONLY",
        "exchangeMutation": False,
        "executionControl": False,
        "botTokenExposed": False,
    }


def send_telegram_report(
    text: str,
) -> bool:

    with STATE_LOCK:

        if STATE.telegram_reports_this_run >= 1:

            log(
                "R35K: TELEGRAM REPORT SUPPRESSED "
                "(ONE REPORT MAXIMUM)"
            )

            return False

    if not telegram_configured():

        log(
            "R35K: TELEGRAM FINAL REPORT=SKIPPED "
            "(NOT CONFIGURED)"
        )

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = urllib.parse.urlencode(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
        }
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        url=url,
        data=payload,
        method="POST",
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded",
            "User-Agent":
                f"{VERSION}/1.0",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:

            response.read()

        with STATE_LOCK:

            STATE.telegram_reports_this_run += 1

            save_state()

        log(
            "R35K: TELEGRAM FINAL REPORT=DELIVERED"
        )

        return True

    except Exception as exc:

        log(
            "R35K: TELEGRAM FINAL REPORT=FAILED: "
            f"{type(exc).__name__}: {exc}"
        )

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
                "status": "ok",
                "version": VERSION,
                "symbol": SYMBOL,
                "phase": STATE.phase,
                "live_readiness": STATE.live_readiness,
                "execution_authorized":
                    STATE.execution_authorized,
                "exchange_network_writes":
                    STATE.exchange_network_writes,
                "real_order_execution":
                    REAL_ORDER_EXECUTION,
                "first_real_order_allowed":
                    FIRST_REAL_ORDER_ALLOWED,
            }

        raw = json.dumps(
            payload,
            separators=(",", ":"),
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
                    raw
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            raw
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    server = HTTPServer(
        (
            "0.0.0.0",
            HEALTH_PORT,
        ),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    log(
        f"R35K: HEALTH SERVER STARTED "
        f"ON PORT {HEALTH_PORT}"
    )


# ==================================================================================================
# TESTS
# ==================================================================================================


def run_validation() -> Tuple[
    bool,
    str,
]:

    global STATE

    all_tests: List[bool] = []

    section(
        "R35K TEST 1: HARD SAFETY CONSTANTS"
    )

    all_tests.append(
        result(
            "Exchange Network Writes Are Disabled",
            EXCHANGE_NETWORK_WRITES_ENABLED is False,
        )
    )

    all_tests.append(
        result(
            "Real Order Execution Is Disabled",
            REAL_ORDER_EXECUTION is False,
        )
    )

    all_tests.append(
        result(
            "Demo Order Execution Is Disabled",
            DEMO_ORDER_EXECUTION is False,
        )
    )

    all_tests.append(
        result(
            "First Real Order Is Forbidden",
            FIRST_REAL_ORDER_ALLOWED is False,
        )
    )

    all_tests.append(
        result(
            "Live Execution Authorization Is Disabled",
            LIVE_EXECUTION_AUTHORIZED is False,
        )
    )

    all_tests.append(
        result(
            "Order Mutation Is Disabled",
            ALLOW_ORDER_MUTATION is False,
        )
    )

    all_tests.append(
        result(
            "Leverage Mutation Is Disabled",
            ALLOW_LEVERAGE_MUTATION is False,
        )
    )

    all_tests.append(
        result(
            "Margin Mutation Is Disabled",
            ALLOW_MARGIN_MUTATION is False,
        )
    )

    all_tests.append(
        result(
            "Position Mutation Is Disabled",
            ALLOW_POSITION_MUTATION is False,
        )
    )

    section(
        "R35K TEST 2: CREDENTIAL PRESENCE"
    )

    creds_ok = credentials_present()

    all_tests.append(
        result(
            "WEEX API Key Is Present",
            bool(
                API_KEY
            ),
        )
    )

    all_tests.append(
        result(
            "WEEX API Secret Is Present",
            bool(
                API_SECRET
            ),
        )
    )

    all_tests.append(
        result(
            "WEEX API Passphrase Is Present",
            bool(
                API_PASSPHRASE
            ),
        )
    )

    all_tests.append(
        result(
            "Complete Authenticated Read Credential Set Is Present",
            creds_ok,
        )
    )

    section(
        "R35K TEST 3: CURRENT EXCHANGE RECONCILIATION"
    )

    observation = perform_exchange_reconciliation()

    all_tests.append(
        result(
            "Public Mark Price Read Succeeded",
            observation.mark_price_read_ok,
        )
    )

    all_tests.append(
        result(
            "Mark Price Is Positive",
            (
                observation.mark_price is not None
                and observation.mark_price > 0
            ),
        )
    )

    all_tests.append(
        result(
            "Authenticated Balance Read Succeeded",
            observation.balance_read_ok,
        )
    )

    all_tests.append(
        result(
            "Available Balance Was Parsed",
            observation.available_balance is not None,
        )
    )

    all_tests.append(
        result(
            "Authenticated Positions Read Succeeded",
            observation.positions_read_ok,
        )
    )

    all_tests.append(
        result(
            "Open Position Count Was Reconciled",
            (
                observation.open_positions is not None
                and observation.open_positions >= 0
            ),
        )
    )

    all_tests.append(
        result(
            "Authenticated Symbol Configuration Read Succeeded",
            observation.symbol_config_read_ok,
        )
    )

    all_tests.append(
        result(
            "All Required Authenticated Reads Succeeded",
            observation.authenticated_reads_ok,
        )
    )

    log(
        f"R35K: AVAILABLE BALANCE="
        f"{observation.available_balance}"
    )

    log(
        f"R35K: MARK PRICE="
        f"{observation.mark_price}"
    )

    log(
        f"R35K: OPEN POSITIONS="
        f"{observation.open_positions}"
    )

    log(
        f"R35K: MARGIN MODE="
        f"{observation.margin_mode}"
    )

    log(
        f"R35K: ISOLATED LONG LEVERAGE="
        f"{observation.isolated_long_leverage}"
    )

    log(
        f"R35K: ISOLATED SHORT LEVERAGE="
        f"{observation.isolated_short_leverage}"
    )

    log(
        f"R35K: POSITION MODE="
        f"{observation.position_mode}"
    )

    section(
        "R35K TEST 4: MARGIN MODE RECONCILIATION"
    )

    all_tests.append(
        result(
            "Observed Margin Mode Is ISOLATED",
            observation.margin_mode == TARGET_MARGIN_MODE,
        )
    )

    section(
        "R35K TEST 5: LONG LEVERAGE RECONCILIATION"
    )

    all_tests.append(
        result(
            f"Observed Isolated Long Leverage Is {TARGET_LONG_LEVERAGE}x",
            (
                observation.isolated_long_leverage
                == TARGET_LONG_LEVERAGE
            ),
        )
    )

    section(
        "R35K TEST 6: SHORT LEVERAGE RECONCILIATION"
    )

    all_tests.append(
        result(
            f"Observed Isolated Short Leverage Is {TARGET_SHORT_LEVERAGE}x",
            (
                observation.isolated_short_leverage
                == TARGET_SHORT_LEVERAGE
            ),
        )
    )

    section(
        "R35K TEST 7: FAIL-CLOSED READINESS GATE"
    )

    (
        live_readiness,
        readiness_failures,
    ) = evaluate_live_readiness(
        observation
    )

    with STATE_LOCK:

        STATE.phase = (
            "PRE_LIVE_RECONCILED"
            if live_readiness
            else "PRE_LIVE_BLOCKED"
        )

        STATE.live_readiness = live_readiness

        STATE.execution_authorized = False

        STATE.observation = {
            "authenticated_reads_ok":
                observation.authenticated_reads_ok,
            "credentials_present":
                observation.credentials_present,
            "balance_read_ok":
                observation.balance_read_ok,
            "mark_price_read_ok":
                observation.mark_price_read_ok,
            "positions_read_ok":
                observation.positions_read_ok,
            "symbol_config_read_ok":
                observation.symbol_config_read_ok,
            "available_balance":
                observation.available_balance,
            "mark_price":
                observation.mark_price,
            "open_positions":
                observation.open_positions,
            "margin_mode":
                observation.margin_mode,
            "isolated_long_leverage":
                observation.isolated_long_leverage,
            "isolated_short_leverage":
                observation.isolated_short_leverage,
            "position_mode":
                observation.position_mode,
        }

        STATE.failure_reasons = list(
            readiness_failures
        )

        save_state()

    all_tests.append(
        result(
            "Readiness Gate Produced Deterministic Boolean State",
            isinstance(
                live_readiness,
                bool,
            ),
        )
    )

    all_tests.append(
        result(
            "Execution Authorization Remains False Regardless Of Readiness",
            STATE.execution_authorized is False,
        )
    )

    if live_readiness:

        all_tests.append(
            result(
                "All Pre-Live Exchange Preconditions Are Verified",
                True,
            )
        )

    else:

        # A blocked readiness result is the correct fail-closed behavior
        # when exchange observations are incomplete or incorrect.
        #
        # It is NOT considered an execution safety failure.

        all_tests.append(
            result(
                "Failed Pre-Live Preconditions Block Execution",
                STATE.execution_authorized is False,
            )
        )

        for failure in readiness_failures:

            log(
                f"R35K: READINESS BLOCKER: {failure}"
            )

    append_journal(
        "PRE_LIVE_RECONCILIATION",
        {
            "live_readiness":
                live_readiness,
            "execution_authorized":
                False,
            "failure_reasons":
                readiness_failures,
            "balance":
                observation.available_balance,
            "mark_price":
                observation.mark_price,
            "open_positions":
                observation.open_positions,
            "margin_mode":
                observation.margin_mode,
            "isolated_long_leverage":
                observation.isolated_long_leverage,
            "isolated_short_leverage":
                observation.isolated_short_leverage,
        },
    )

    section(
        "R35K TEST 8: ZERO-WRITE GUARANTEE"
    )

    all_tests.append(
        result(
            "Exchange Write Count Is Zero Before Synthetic Boundary",
            STATE.exchange_network_writes == 0,
        )
    )

    all_tests.append(
        result(
            "Readiness Reconciliation Makes No Exchange Mutation",
            STATE.exchange_network_writes == 0,
        )
    )

    section(
        "R35K TEST 9: FUTURE ORDER ENVELOPE CONSTRUCTION"
    )

    nonce = next_nonce()

    client_order_id = create_validation_client_order_id(
        nonce
    )

    envelope = build_synthetic_order_envelope(
        client_order_id
    )

    all_tests.append(
        result(
            "Order Envelope Uses POST",
            envelope.get(
                "method"
            ) == "POST",
        )
    )

    all_tests.append(
        result(
            "Order Envelope Uses Exact V3 Order Path",
            envelope.get(
                "path"
            ) == ORDER_ENDPOINT,
        )
    )

    all_tests.append(
        result(
            "Order Envelope Is Bound To BTCUSDT",
            envelope.get(
                "symbol"
            ) == SYMBOL,
        )
    )

    all_tests.append(
        result(
            "Order Envelope Uses BUY",
            envelope.get(
                "side"
            ) == "BUY",
        )
    )

    all_tests.append(
        result(
            "Order Envelope Uses LONG Position Side",
            envelope.get(
                "positionSide"
            ) == "LONG",
        )
    )

    all_tests.append(
        result(
            "Order Envelope Is Synthetic",
            envelope.get(
                "synthetic"
            ) is True,
        )
    )

    all_tests.append(
        result(
            "Order Envelope Forbids Transmission",
            envelope.get(
                "transmissionAllowed"
            ) is False,
        )
    )

    all_tests.append(
        result(
            "Order Envelope Forbids Network Write",
            envelope.get(
                "networkWriteAllowed"
            ) is False,
        )
    )

    all_tests.append(
        result(
            "Order Envelope Forbids Real Order",
            envelope.get(
                "realOrderAllowed"
            ) is False,
        )
    )

    section(
        "R35K TEST 10: SYNTHETIC BOUNDARY DISPATCH"
    )

    receipt = synthetic_boundary_dispatch(
        envelope
    )

    all_tests.append(
        result(
            "Synthetic Boundary Dispatch Completed",
            receipt.get(
                "status"
            ) == "SYNTHETIC_ONLY",
        )
    )

    all_tests.append(
        result(
            "Synthetic Dispatch Did Not Transmit",
            receipt.get(
                "transmitted"
            ) is False,
        )
    )

    all_tests.append(
        result(
            "Synthetic Dispatch Made No Exchange Network Write",
            receipt.get(
                "exchangeNetworkWrite"
            ) is False,
        )
    )

    all_tests.append(
        result(
            "Exchange Write Count Remains Zero After Synthetic Dispatch",
            STATE.exchange_network_writes == 0,
        )
    )

    section(
        "R35K TEST 11: READ FAILURE CANNOT AUTHORIZE EXECUTION"
    )

    deliberately_failed = ExchangeObservation(
        authenticated_reads_ok=False,
        credentials_present=True,
        balance_read_ok=False,
        mark_price_read_ok=True,
        positions_read_ok=True,
        symbol_config_read_ok=True,
        available_balance=None,
        mark_price=75000.0,
        open_positions=0,
        margin_mode="ISOLATED",
        isolated_long_leverage=100,
        isolated_short_leverage=100,
    )

    (
        failed_ready,
        _,
    ) = evaluate_live_readiness(
        deliberately_failed
    )

    all_tests.append(
        result(
            "Missing Balance Forces Readiness False",
            failed_ready is False,
        )
    )

    all_tests.append(
        result(
            "Missing Balance Cannot Enable Execution",
            STATE.execution_authorized is False,
        )
    )

    section(
        "R35K TEST 12: ZERO MARK PRICE CANNOT AUTHORIZE EXECUTION"
    )

    zero_mark = ExchangeObservation(
        authenticated_reads_ok=True,
        credentials_present=True,
        balance_read_ok=True,
        mark_price_read_ok=True,
        positions_read_ok=True,
        symbol_config_read_ok=True,
        available_balance=10.0,
        mark_price=0.0,
        open_positions=0,
        margin_mode="ISOLATED",
        isolated_long_leverage=100,
        isolated_short_leverage=100,
    )

    (
        zero_mark_ready,
        _,
    ) = evaluate_live_readiness(
        zero_mark
    )

    all_tests.append(
        result(
            "Zero Mark Price Forces Readiness False",
            zero_mark_ready is False,
        )
    )

    section(
        "R35K TEST 13: INVALID POSITION STATE CANNOT AUTHORIZE EXECUTION"
    )

    invalid_position = ExchangeObservation(
        authenticated_reads_ok=True,
        credentials_present=True,
        balance_read_ok=True,
        mark_price_read_ok=True,
        positions_read_ok=True,
        symbol_config_read_ok=True,
        available_balance=10.0,
        mark_price=75000.0,
        open_positions=-1,
        margin_mode="ISOLATED",
        isolated_long_leverage=100,
        isolated_short_leverage=100,
    )

    (
        invalid_position_ready,
        _,
    ) = evaluate_live_readiness(
        invalid_position
    )

    all_tests.append(
        result(
            "Negative Position Count Forces Readiness False",
            invalid_position_ready is False,
        )
    )

    section(
        "R35K TEST 14: WRONG LEVERAGE CANNOT AUTHORIZE EXECUTION"
    )

    wrong_leverage = ExchangeObservation(
        authenticated_reads_ok=True,
        credentials_present=True,
        balance_read_ok=True,
        mark_price_read_ok=True,
        positions_read_ok=True,
        symbol_config_read_ok=True,
        available_balance=10.0,
        mark_price=75000.0,
        open_positions=0,
        margin_mode="ISOLATED",
        isolated_long_leverage=50,
        isolated_short_leverage=20,
    )

    (
        wrong_leverage_ready,
        _,
    ) = evaluate_live_readiness(
        wrong_leverage
    )

    all_tests.append(
        result(
            "Wrong Long/Short Leverage Forces Readiness False",
            wrong_leverage_ready is False,
        )
    )

    section(
        "R35K TEST 15: WRONG MARGIN MODE CANNOT AUTHORIZE EXECUTION"
    )

    wrong_margin = ExchangeObservation(
        authenticated_reads_ok=True,
        credentials_present=True,
        balance_read_ok=True,
        mark_price_read_ok=True,
        positions_read_ok=True,
        symbol_config_read_ok=True,
        available_balance=10.0,
        mark_price=75000.0,
        open_positions=0,
        margin_mode="CROSS",
        isolated_long_leverage=100,
        isolated_short_leverage=100,
    )

    (
        wrong_margin_ready,
        _,
    ) = evaluate_live_readiness(
        wrong_margin
    )

    all_tests.append(
        result(
            "Wrong Margin Mode Forces Readiness False",
            wrong_margin_ready is False,
        )
    )

    section(
        "R35K TEST 16: DURABLE RESTART PROTECTION"
    )

    save_state()

    previous = load_previous_state()

    all_tests.append(
        result(
            "Durable State Snapshot Exists",
            isinstance(
                previous,
                dict,
            ),
        )
    )

    all_tests.append(
        result(
            "Restart Snapshot Keeps Execution Unauthorized",
            bool(
                previous
            )
            and previous.get(
                "execution_authorized"
            ) is False,
        )
    )

    all_tests.append(
        result(
            "Restart Snapshot Keeps Exchange Write Count At Zero",
            bool(
                previous
            )
            and previous.get(
                "exchange_network_writes"
            ) == 0,
        )
    )

    section(
        "R35K TEST 17: TELEGRAM REPORTING BOUNDARY"
    )

    telegram_boundary = telegram_preview()

    all_tests.append(
        result(
            "Telegram Uses POST Only For Reporting",
            telegram_boundary.get(
                "method"
            ) == "POST",
        )
    )

    all_tests.append(
        result(
            "Telegram Operation Is sendMessage",
            telegram_boundary.get(
                "operation"
            ) == "sendMessage",
        )
    )

    all_tests.append(
        result(
            "Telegram Request Is Report Only",
            telegram_boundary.get(
                "purpose"
            ) == "REPORT_ONLY",
        )
    )

    all_tests.append(
        result(
            "Telegram Is Not Exchange Mutation",
            telegram_boundary.get(
                "exchangeMutation"
            ) is False,
        )
    )

    all_tests.append(
        result(
            "Telegram Cannot Control Execution",
            telegram_boundary.get(
                "executionControl"
            ) is False,
        )
    )

    all_tests.append(
        result(
            "Telegram Preview Does Not Expose Bot Token",
            telegram_boundary.get(
                "botTokenExposed"
            ) is False,
        )
    )

    section(
        "R35K TEST 18: JOURNAL INTEGRITY"
    )

    (
        journal_ok,
        journal_count,
        journal_error,
    ) = validate_journal()

    all_tests.append(
        result(
            "Durable Journal Contains Records",
            journal_count > 0,
        )
    )

    all_tests.append(
        result(
            "Durable Journal Hash Chain Is Valid",
            journal_ok,
        )
    )

    all_tests.append(
        result(
            "Journal Sequence Is Monotonic",
            journal_ok,
        )
    )

    if journal_error:

        log(
            f"R35K: JOURNAL ERROR={journal_error}"
        )

    section(
        "R35K TEST 19: FINAL EXECUTION FIREBREAK"
    )

    all_tests.append(
        result(
            "Exchange Network Writes Remain Zero",
            STATE.exchange_network_writes == 0,
        )
    )

    all_tests.append(
        result(
            "Real Order Execution Remains Disabled",
            REAL_ORDER_EXECUTION is False,
        )
    )

    all_tests.append(
        result(
            "First Real Order Remains Forbidden",
            FIRST_REAL_ORDER_ALLOWED is False,
        )
    )

    all_tests.append(
        result(
            "Execution Authorization Remains False",
            STATE.execution_authorized is False,
        )
    )

    append_journal(
        "R35K_VALIDATION_COMPLETED",
        {
            "live_readiness":
                STATE.live_readiness,
            "execution_authorized":
                STATE.execution_authorized,
            "exchange_network_writes":
                STATE.exchange_network_writes,
            "real_order_execution":
                REAL_ORDER_EXECUTION,
            "first_real_order_allowed":
                FIRST_REAL_ORDER_ALLOWED,
        },
    )

    # ------------------------------------------------------------------------------------------------
    # VALIDATION SEMANTICS
    #
    # A real exchange readiness blocker must NOT make the safety framework itself "fail".
    #
    # R35K has two independent outcomes:
    #
    # 1. SAFETY VALIDATION
    #    Did every prohibited pathway remain prohibited?
    #
    # 2. LIVE READINESS
    #    Did current real exchange state satisfy every prerequisite?
    #
    # This means:
    #
    #     VALIDATION PASSED + LIVE READINESS BLOCKED
    #
    # is a valid and desirable fail-closed result.
    # ------------------------------------------------------------------------------------------------

    safety_critical = [
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
        REAL_ORDER_EXECUTION is False,
        DEMO_ORDER_EXECUTION is False,
        FIRST_REAL_ORDER_ALLOWED is False,
        LIVE_EXECUTION_AUTHORIZED is False,
        STATE.exchange_network_writes == 0,
        STATE.execution_authorized is False,
        receipt.get(
            "transmitted"
        ) is False,
        receipt.get(
            "exchangeNetworkWrite"
        ) is False,
        journal_ok,
    ]

    validation_passed = all(
        safety_critical
    )

    if validation_passed:

        if STATE.live_readiness:

            status = (
                "PRE-LIVE RECONCILIATION VERIFIED "
                "WITH EXECUTION STILL HARD DISABLED"
            )

        else:

            status = (
                "PRE-LIVE READINESS BLOCKED FAIL-CLOSED "
                "WITH ZERO EXCHANGE WRITES"
            )

    else:

        status = (
            "R35K SAFETY VALIDATION FAILED"
        )

    report_lines = [
        "✅ R35K VALIDATION REPORT"
        if validation_passed
        else "❌ R35K VALIDATION REPORT",
        "",
        f"Symbol: {SYMBOL}",
        (
            "Authenticated WEEX reads: PASS"
            if observation.authenticated_reads_ok
            else "Authenticated WEEX reads: FAIL"
        ),
        (
            "Credentials present: YES"
            if observation.credentials_present
            else "Credentials present: NO"
        ),
        (
            f"Balance: {observation.available_balance}"
        ),
        (
            f"Mark price: {observation.mark_price}"
        ),
        (
            f"Open positions: {observation.open_positions}"
        ),
        (
            f"Margin mode: {observation.margin_mode}"
        ),
        (
            "Isolated long leverage: "
            f"{observation.isolated_long_leverage}"
        ),
        (
            "Isolated short leverage: "
            f"{observation.isolated_short_leverage}"
        ),
        (
            f"Target long leverage: "
            f"{TARGET_LONG_LEVERAGE}x"
        ),
        (
            f"Target short leverage: "
            f"{TARGET_SHORT_LEVERAGE}x"
        ),
        (
            f"Order endpoint: {ORDER_ENDPOINT}"
        ),
        "Order side: BUY",
        "Position side: LONG",
        (
            f"Validation quantity: "
            f"{VALIDATION_QTY_BTC:.4f} BTC"
        ),
        (
            f"Client order ID: "
            f"{client_order_id}"
        ),
        (
            "Journal integrity: PASS"
            if journal_ok
            else "Journal integrity: FAIL"
        ),
        (
            f"Journal records validated: "
            f"{journal_count}"
        ),
        (
            f"Exchange network writes: "
            f"{STATE.exchange_network_writes}"
        ),
        (
            "Real order execution: DISABLED"
        ),
        (
            "Demo order execution: DISABLED"
        ),
        (
            "First real order: FORBIDDEN"
        ),
        (
            "Execution authorization: FORBIDDEN"
        ),
        (
            "Live readiness: "
            + (
                "PASS"
                if STATE.live_readiness
                else "BLOCKED"
            )
        ),
        (
            "Synthetic boundary dispatches: "
            f"{STATE.synthetic_boundary_dispatches}"
        ),
        (
            "Telegram reports this run: "
            f"{STATE.telegram_reports_this_run} maximum before final report"
        ),
    ]

    if readiness_failures:

        report_lines.append(
            ""
        )

        report_lines.append(
            "Readiness blockers:"
        )

        for failure in readiness_failures:

            report_lines.append(
                f"- {failure}"
            )

    report_lines.extend(
        [
            "",
            (
                "Validation status: PASSED"
                if validation_passed
                else "Validation status: FAILED"
            ),
            (
                f"Status: {status}"
            ),
        ]
    )

    report_text = "\n".join(
        report_lines
    )

    section(
        "R35K: VALIDATION SUMMARY"
    )

    print(
        report_text,
        flush=True,
    )

    return (
        validation_passed,
        report_text,
    )


# ==================================================================================================
# STARTUP
# ==================================================================================================


def initialize_state() -> None:

    global STATE

    ensure_state_dir()

    previous = load_previous_state()

    if previous:

        previous_generation = safe_int(
            previous.get(
                "generation"
            )
        )

        previous_epoch = safe_int(
            previous.get(
                "epoch"
            )
        )

        # R35K starts a fresh validation run while preserving monotonic lineage.
        #
        # It never restores a previous execution authorization.

        STATE.generation = max(
            previous_generation or 1,
            1,
        )

        STATE.epoch = max(
            previous_epoch or 1,
            1,
        )

        STATE.execution_authorized = False

        STATE.exchange_network_writes = 0

        STATE.telegram_reports_this_run = 0

        STATE.synthetic_boundary_dispatches = 0

        STATE.live_readiness = False

        STATE.failure_reasons = []

    else:

        STATE = StrategyState()

    STATE.phase = "INITIALIZED"

    STATE.execution_authorized = False

    STATE.exchange_network_writes = 0

    STATE.updated_at = utc_now()

    save_state()


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    section(
        "R35K: MAIN.PY ENTERED"
    )

    log(
        f"R35K: SYMBOL={SYMBOL}"
    )

    log(
        f"R35K: VERSION={VERSION}"
    )

    log(
        f"R35K: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"R35K: STATE DIR={STATE_DIR}"
    )

    log(
        f"R35K: WEEX BASE URL={WEEX_BASE_URL}"
    )

    log(
        "R35K: AUTHENTICATED READ-ONLY RECONCILIATION ENABLED"
    )

    log(
        "R35K: EXCHANGE NETWORK WRITES=DISABLED"
    )

    log(
        "R35K: REAL ORDER EXECUTION=DISABLED"
    )

    log(
        "R35K: DEMO ORDER EXECUTION=DISABLED"
    )

    log(
        "R35K: FIRST REAL ORDER=FORBIDDEN"
    )

    initialize_state()

    append_journal(
        "R35K_STARTED",
        {
            "symbol": SYMBOL,
            "exchange_network_writes":
                STATE.exchange_network_writes,
            "real_order_execution":
                REAL_ORDER_EXECUTION,
            "first_real_order_allowed":
                FIRST_REAL_ORDER_ALLOWED,
        },
    )

    try:

        (
            validation_passed,
            report_text,
        ) = run_validation()

    except Exception as exc:

        with STATE_LOCK:

            STATE.phase = "FAILED_CLOSED"

            STATE.live_readiness = False

            STATE.execution_authorized = False

            STATE.exchange_network_writes = 0

            STATE.failure_reasons.append(
                f"{type(exc).__name__}: {exc}"
            )

            save_state()

        append_journal(
            "R35K_FATAL_FAIL_CLOSED",
            {
                "error_type":
                    type(exc).__name__,
                "error":
                    str(exc),
                "exchange_network_writes":
                    0,
                "execution_authorized":
                    False,
            },
        )

        section(
            "R35K: FATAL VALIDATION ERROR"
        )

        log(
            f"R35K: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        log(
            "R35K: LIVE READINESS=BLOCKED"
        )

        log(
            "R35K: EXCHANGE NETWORK WRITES=0"
        )

        log(
            "R35K: REAL ORDER EXECUTION=False"
        )

        log(
            "R35K: FIRST REAL ORDER=FORBIDDEN"
        )

        validation_passed = False

        report_text = (
            "❌ R35K VALIDATION REPORT\n\n"
            f"Symbol: {SYMBOL}\n"
            "Live readiness: BLOCKED\n"
            "Execution authorization: FORBIDDEN\n"
            "Exchange network writes: 0\n"
            "Real order execution: DISABLED\n"
            "First real order: FORBIDDEN\n"
            f"Error: {type(exc).__name__}: {exc}\n"
            "Status: FAILED CLOSED"
        )

    send_telegram_report(
        report_text
    )

    section(
        "R35K: FINAL SAFETY STATE"
    )

    log(
        f"R35K: LIVE READINESS="
        f"{STATE.live_readiness}"
    )

    log(
        f"R35K: EXECUTION AUTHORIZED="
        f"{STATE.execution_authorized}"
    )

    log(
        f"R35K: EXCHANGE NETWORK WRITES="
        f"{STATE.exchange_network_writes}"
    )

    log(
        f"R35K: REAL ORDER EXECUTION="
        f"{REAL_ORDER_EXECUTION}"
    )

    log(
        "R35K: FIRST REAL ORDER=FORBIDDEN"
    )

    if validation_passed:

        if STATE.live_readiness:

            log(
                "R35K: FINAL STATUS="
                "PRE-LIVE AUTHENTICATED RECONCILIATION VERIFIED "
                "WITH HARD WRITE FIREBREAK"
            )

        else:

            log(
                "R35K: FINAL STATUS="
                "PRE-LIVE READINESS BLOCKED FAIL-CLOSED "
                "WITH HARD WRITE FIREBREAK"
            )

    else:

        log(
            "R35K: FINAL STATUS="
            "VALIDATION FAILED CLOSED"
        )

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"R35K: HEARTBEAT {heartbeat}"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


if __name__ == "__main__":

    main()
