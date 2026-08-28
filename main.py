

import base64
import hashlib
import hmac
import json
import os
import signal
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, ROUND_DOWN
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ==================================================================================================
# R34Z - LIVE READ-ONLY STATE + COMPLETE SYNTHETIC STRATEGY LIFECYCLE + DURABLE RECOVERY VALIDATION
# ==================================================================================================
#
# SAFETY MODEL
#
#   - AUTHENTICATED GET ONLY
#   - PUBLIC GET ONLY
#   - NO POST
#   - NO PUT
#   - NO PATCH
#   - NO DELETE
#   - NO REAL ORDER
#   - NO DEMO ORDER
#   - NO LEVERAGE CHANGE
#   - NO MARGIN CHANGE
#   - NO POSITION CHANGE
#   - NO ACCOUNT MUTATION
#   - SYNTHETIC DISPATCH ONLY
#
# IMPORTANT R34Z CORRECTION
#
#   Quantity normalization ALWAYS rounds DOWN to the exchange quantity step.
#   This prevents step-size rounding from increasing actual margin above the intended entry budget.
#
# ==================================================================================================

VERSION = "R34Z"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper().strip()
BASE_URL = os.getenv("WEEX_BASE_URL", "https://api-contract.weex.com").rstrip("/")
HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))
STATE_DIR = Path(os.getenv("R34Z_STATE_DIR", "/tmp/r34z_state"))
STATE_FILE = STATE_DIR / "strategy_state.json"

API_KEY = os.getenv("WEEX_API_KEY", "").strip()
API_SECRET = os.getenv("WEEX_API_SECRET", "").strip()
API_PASSPHRASE = os.getenv("WEEX_API_PASSPHRASE", "").strip()

AUTHENTICATED_READ_ONLY = True
PUBLIC_READ_ONLY = True
SYNTHETIC_TRANSPORT_ONLY = True
NETWORK_WRITES_ENABLED = False
REAL_ORDERS_ENABLED = False
DEMO_ORDERS_ENABLED = False

TARGET_MARGIN_TYPE = "ISOLATED"
TARGET_LEVERAGE = Decimal("100")
INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_SIZE_PERCENT = Decimal("5")
BACKUP_SIZE_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")
TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.2")

BALANCE_PATH = "/capi/v3/account/balance"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"
POSITION_PATH = "/capi/v3/account/position/allPosition"
MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"
EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"

READ_ONLY_PUBLIC_PATHS = {
    MARK_PRICE_PATH,
    EXCHANGE_INFO_PATH,
}

READ_ONLY_AUTH_PATHS = {
    BALANCE_PATH,
    SYMBOL_CONFIG_PATH,
    POSITION_PATH,
}

SEPARATOR = "-" * 100

STOP_EVENT = threading.Event()

COUNTERS = {
    "public_get": 0,
    "authenticated_get": 0,
    "network_writes": 0,
    "synthetic_dispatches": 0,
    "replays_blocked": 0,
}


def log(message: str = "") -> None:
    print(message, flush=True)


def section(title: str) -> None:
    log(SEPARATOR)
    log(title)
    log(SEPARATOR)


def check(label: str, condition: bool) -> None:
    if not condition:
        log(f"{label:<92} ❌ FAIL")
        raise AssertionError(label)

    log(f"{label:<92} ✅ PASS")


def decimal_text(value: Decimal) -> str:
    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(value: Any) -> str:
    encoded = canonical_json(value).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def extract_data(payload: Any) -> Any:
    if isinstance(payload, dict):

        for key in (
            "data",
            "result",
        ):

            if key in payload:
                return payload[key]

    return payload


def first_dict(value: Any) -> Dict[str, Any]:
    value = extract_data(value)

    if isinstance(value, dict):
        return value

    if isinstance(value, list):

        for item in value:

            if isinstance(item, dict):
                return item

    return {}


def recursive_find_number(
    value: Any,
    keys: Tuple[str, ...],
) -> Decimal | None:

    if isinstance(value, dict):

        for key, item in value.items():

            if key in keys:

                try:
                    return Decimal(str(item))

                except Exception:
                    pass

        for item in value.values():

            found = recursive_find_number(
                item,
                keys,
            )

            if found is not None:
                return found

    elif isinstance(value, list):

        for item in value:

            found = recursive_find_number(
                item,
                keys,
            )

            if found is not None:
                return found

    return None


def canonical_query(
    params: Dict[str, Any] | None,
) -> str:

    if not params:
        return ""

    clean = [
        (
            str(key),
            str(value),
        )
        for key, value in params.items()
        if value is not None
    ]

    clean.sort(
        key=lambda item: item[0]
    )

    return urllib.parse.urlencode(clean)


def make_auth_headers(
    method: str,
    request_path_with_query: str,
    body: str = "",
) -> Dict[str, str]:

    timestamp = str(
        int(time.time() * 1000)
    )

    prehash = (
        f"{timestamp}"
        f"{method.upper()}"
        f"{request_path_with_query}"
        f"{body}"
    )

    digest = hmac.new(
        API_SECRET.encode("utf-8"),
        prehash.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    signature_value = base64.b64encode(
        digest
    ).decode("ascii")

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature_value,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{VERSION}-read-only-validation",
    }


def http_get(
    path: str,
    params: Dict[str, Any] | None = None,
    authenticated: bool = False,
) -> Any:

    if authenticated:

        if path not in READ_ONLY_AUTH_PATHS:

            raise RuntimeError(
                f"Authenticated GET path is not allowlisted: {path}"
            )

    else:

        if path not in READ_ONLY_PUBLIC_PATHS:

            raise RuntimeError(
                f"Public GET path is not allowlisted: {path}"
            )

    query = canonical_query(params)

    request_path = (
        path
        + (
            f"?{query}"
            if query
            else ""
        )
    )

    url = BASE_URL + request_path

    if authenticated:

        headers = make_auth_headers(
            "GET",
            request_path,
        )

    else:

        headers = {
            "Accept": "application/json",
            "User-Agent": f"{VERSION}-public-read-only-validation",
        }

    request = urllib.request.Request(
        url=url,
        headers=headers,
        method="GET",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

            result = json.loads(raw)

    except urllib.error.HTTPError as exc:

        body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"GET failed: {path} | "
            f"HTTP {exc.code}: {body}"
        ) from exc

    except Exception as exc:

        raise RuntimeError(
            f"GET failed: {path} | "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    if authenticated:
        COUNTERS["authenticated_get"] += 1

    else:
        COUNTERS["public_get"] += 1

    return result


def authenticated_get(
    path: str,
    params: Dict[str, Any] | None = None,
) -> Any:

    if not AUTHENTICATED_READ_ONLY:

        raise RuntimeError(
            "Authenticated read-only transport is disabled"
        )

    return http_get(
        path,
        params=params,
        authenticated=True,
    )


def public_get(
    path: str,
    params: Dict[str, Any] | None = None,
) -> Any:

    if not PUBLIC_READ_ONLY:

        raise RuntimeError(
            "Public read-only transport is disabled"
        )

    return http_get(
        path,
        params=params,
        authenticated=False,
    )


def reject_network_write(
    method: str,
    path: str = "",
) -> None:

    method = method.upper().strip()

    if method in {
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    }:

        raise RuntimeError(
            f"{VERSION} WRITE FIREBREAK: "
            f"HTTP {method} is disabled "
            f"for {path or '/'}"
        )

    raise RuntimeError(
        f"{VERSION} WRITE FIREBREAK: "
        "generic network write is disabled"
    )


def real_order(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        f"{VERSION} WRITE FIREBREAK: "
        "real orders are disabled"
    )


def demo_order(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        f"{VERSION} WRITE FIREBREAK: "
        "demo orders are disabled"
    )


def mutate_leverage(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        f"{VERSION} WRITE FIREBREAK: "
        "leverage mutation is disabled"
    )


def mutate_margin(
    *_args: Any,
    **_kwargs: Any,
) -> None:

    raise RuntimeError(
        f"{VERSION} WRITE FIREBREAK: "
        "margin mutation is disabled"
    )


def normalize_quantity_down(
    raw_qty: Decimal,
    step: Decimal,
    min_qty: Decimal,
) -> Decimal:

    if (
        raw_qty <= 0
        or step <= 0
        or min_qty <= 0
    ):

        raise ValueError(
            "raw quantity, step and minimum "
            "quantity must be positive"
        )

    steps = (
        raw_qty / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    normalized = steps * step

    if normalized < min_qty:
        return Decimal("0")

    return normalized


def parse_balance(
    payload: Any,
) -> Decimal:

    data = extract_data(payload)

    candidates: List[
        Dict[str, Any]
    ] = []

    if isinstance(data, list):

        candidates = [
            item
            for item in data
            if isinstance(item, dict)
        ]

    elif isinstance(data, dict):

        candidates = [data]

        for key in (
            "list",
            "balances",
            "assets",
        ):

            sub = data.get(key)

            if isinstance(sub, list):

                candidates.extend(
                    [
                        item
                        for item in sub
                        if isinstance(
                            item,
                            dict,
                        )
                    ]
                )

    preferred = []

    for item in candidates:

        coin = str(
            item.get("coin")
            or item.get("asset")
            or item.get("marginCoin")
            or ""
        ).upper()

        if coin in {
            "USDT",
            "USDT-SUSDT",
            "SUSDT",
        }:

            preferred.append(item)

    candidates = (
        preferred
        or candidates
    )

    keys = (
        "available",
        "availableBalance",
        "availableMargin",
        "availableAmount",
        "balance",
        "equity",
    )

    for item in candidates:

        for key in keys:

            if key in item:

                try:
                    return Decimal(
                        str(item[key])
                    )

                except Exception:
                    pass

    found = recursive_find_number(
        data,
        keys,
    )

    if found is None:

        raise RuntimeError(
            "Unable to parse available "
            f"balance from response: {payload}"
        )

    return found


def parse_symbol_config(
    payload: Any,
) -> Dict[str, Any]:

    data = extract_data(payload)

    records: List[
        Dict[str, Any]
    ] = []

    if isinstance(data, list):

        records = [
            item
            for item in data
            if isinstance(item, dict)
        ]

    elif isinstance(data, dict):

        records = [data]

        for key in (
            "list",
            "symbols",
        ):

            sub = data.get(key)

            if isinstance(sub, list):

                records.extend(
                    [
                        item
                        for item in sub
                        if isinstance(
                            item,
                            dict,
                        )
                    ]
                )

    for record in records:

        if (
            str(
                record.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):

            return record

    if records:
        return records[0]

    raise RuntimeError(
        "Unable to parse symbol "
        f"configuration from response: {payload}"
    )


def parse_positions(
    payload: Any,
) -> List[Dict[str, Any]]:

    data = extract_data(payload)

    if isinstance(data, list):

        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, dict):

        for key in (
            "list",
            "positions",
            "positionList",
        ):

            sub = data.get(key)

            if isinstance(sub, list):

                return [
                    item
                    for item in sub
                    if isinstance(
                        item,
                        dict,
                    )
                ]

        if data:
            return [data]

    return []


def position_is_open(
    position: Dict[str, Any],
) -> bool:

    keys = (
        "positionAmt",
        "size",
        "position",
        "holdVol",
        "total",
        "available",
    )

    for key in keys:

        if key in position:

            try:

                return (
                    Decimal(
                        str(
                            position[key]
                        )
                    )
                    != 0
                )

            except Exception:
                continue

    return False


def parse_mark_price(
    payload: Any,
) -> Decimal:

    keys = (
        "markPrice",
        "price",
        "last",
        "lastPrice",
        "indexPrice",
    )

    found = recursive_find_number(
        extract_data(payload),
        keys,
    )

    if found is None:

        raise RuntimeError(
            "Unable to parse market price "
            f"from response: {payload}"
        )

    return found


def parse_contract_info(
    payload: Any,
) -> Tuple[
    Decimal,
    Decimal,
    Decimal,
]:

    data = extract_data(payload)

    records: List[
        Dict[str, Any]
    ] = []

    if isinstance(data, list):

        records = [
            item
            for item in data
            if isinstance(item, dict)
        ]

    elif isinstance(data, dict):

        records = [data]

        for key in (
            "symbols",
            "list",
            "contracts",
        ):

            sub = data.get(key)

            if isinstance(sub, list):

                records.extend(
                    [
                        item
                        for item in sub
                        if isinstance(
                            item,
                            dict,
                        )
                    ]
                )

    record: Dict[
        str,
        Any,
    ] = {}

    for candidate in records:

        if (
            str(
                candidate.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):

            record = candidate
            break

    if (
        not record
        and records
    ):

        record = records[0]

    min_qty = recursive_find_number(
        record,
        (
            "minQty",
            "minOrderQty",
            "minOrderSize",
            "minTradeNum",
        ),
    )

    qty_step = recursive_find_number(
        record,
        (
            "qtyStep",
            "stepSize",
            "quantityStep",
            "sizeMultiplier",
        ),
    )

    price_step = recursive_find_number(
        record,
        (
            "priceStep",
            "tickSize",
            "priceTick",
        ),
    )

    qty_precision = recursive_find_number(
        record,
        (
            "quantityPrecision",
            "qtyPrecision",
            "volumePlace",
        ),
    )

    price_precision = recursive_find_number(
        record,
        (
            "pricePrecision",
            "pricePlace",
        ),
    )

    if (
        qty_step is None
        and qty_precision is not None
    ):

        qty_step = Decimal(
            "1"
        ).scaleb(
            -int(
                qty_precision
            )
        )

    if (
        min_qty is None
        and qty_step is not None
    ):

        min_qty = qty_step

    if (
        price_step is None
        and price_precision is not None
    ):

        price_step = Decimal(
            "1"
        ).scaleb(
            -int(
                price_precision
            )
        )

    if min_qty is None:
        min_qty = Decimal(
            "0.0001"
        )

    if qty_step is None:
        qty_step = Decimal(
            "0.0001"
        )

    if price_step is None:
        price_step = Decimal(
            "0.1"
        )

    return (
        min_qty,
        qty_step,
        price_step,
    )


def new_state(
    balance: Decimal,
    price: Decimal,
    quantity: Decimal,
) -> Dict[str, Any]:

    return {
        "version": VERSION,
        "symbol": SYMBOL,
        "phase": "READY",
        "initial_entry_completed": False,
        "pyramid_count": 0,
        "backup_count": 0,
        "tp1_completed": False,
        "tp2_completed": False,
        "trailing_armed": False,
        "trailing_reference": None,
        "tp3_completed": False,
        "terminal_completed": False,
        "balance": decimal_text(
            balance
        ),
        "reference_price": decimal_text(
            price
        ),
        "quantity": decimal_text(
            quantity
        ),
        "consumed_intents": [],
        "dispatch_receipts": [],
        "updated_at_ms": int(
            time.time() * 1000
        ),
    }


def state_envelope(
    state: Dict[str, Any],
) -> Dict[str, Any]:

    clean = dict(state)

    clean.pop(
        "integrity_sha256",
        None,
    )

    clean[
        "integrity_sha256"
    ] = sha256_json(clean)

    return clean


def save_state(
    state: Dict[str, Any],
) -> None:

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    state[
        "updated_at_ms"
    ] = int(
        time.time() * 1000
    )

    envelope = state_envelope(
        state
    )

    temp_file = STATE_FILE.with_suffix(
        ".tmp"
    )

    with temp_file.open(
        "w",
        encoding="utf-8",
    ) as file_handle:

        json.dump(
            envelope,
            file_handle,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )

        file_handle.flush()

        os.fsync(
            file_handle.fileno()
        )

    os.replace(
        temp_file,
        STATE_FILE,
    )


def load_state() -> Dict[str, Any]:

    with STATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file_handle:

        envelope = json.load(
            file_handle
        )

    stored_hash = envelope.get(
        "integrity_sha256"
    )

    clean = dict(envelope)

    clean.pop(
        "integrity_sha256",
        None,
    )

    if (
        not stored_hash
        or stored_hash
        != sha256_json(clean)
    ):

        raise RuntimeError(
            "State integrity check failed"
        )

    return clean


def make_intent(
    kind: str,
    sequence: int,
    quantity: Decimal,
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    intent = {
        "version": VERSION,
        "symbol": SYMBOL,
        "kind": kind,
        "sequence": sequence,
        "quantity": decimal_text(
            quantity
        ),
        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,
    }

    if extra:
        intent.update(extra)

    intent[
        "intent_id"
    ] = hashlib.sha256(
        canonical_json(
            intent
        ).encode(
            "utf-8"
        )
    ).hexdigest()[:24]

    return intent


def synthetic_dispatch(
    state: Dict[str, Any],
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    if not SYNTHETIC_TRANSPORT_ONLY:

        raise RuntimeError(
            "Synthetic transport is not enabled"
        )

    if (
        NETWORK_WRITES_ENABLED
        or REAL_ORDERS_ENABLED
        or DEMO_ORDERS_ENABLED
    ):

        raise RuntimeError(
            "Unsafe execution flag is enabled"
        )

    if (
        intent.get(
            "transmission_allowed"
        )
        is not False
        or intent.get(
            "network_write_allowed"
        )
        is not False
    ):

        raise RuntimeError(
            "Synthetic intent permits "
            "transmission or network write"
        )

    intent_id = str(
        intent["intent_id"]
    )

    if intent_id in state[
        "consumed_intents"
    ]:

        COUNTERS[
            "replays_blocked"
        ] += 1

        raise RuntimeError(
            "Consumed synthetic intent "
            f"replay rejected: {intent_id}"
        )

    receipt = {
        "intent_id": intent_id,
        "kind": intent["kind"],
        "synthetic_only": True,
        "transmitted": False,
        "network_write": False,
        "completed": True,
        "receipt_sha256": sha256_json(
            intent
        ),
        "completed_at_ms": int(
            time.time() * 1000
        ),
    }

    state[
        "consumed_intents"
    ].append(
        intent_id
    )

    state[
        "dispatch_receipts"
    ].append(
        receipt
    )

    COUNTERS[
        "synthetic_dispatches"
    ] += 1

    save_state(state)

    return receipt


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

        body = json.dumps(
            {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "authenticated_read_only": AUTHENTICATED_READ_ONLY,
                "public_read_only": PUBLIC_READ_ONLY,
                "synthetic_transport_only": SYNTHETIC_TRANSPORT_ONLY,
                "network_writes": COUNTERS[
                    "network_writes"
                ],
                "synthetic_dispatches": COUNTERS[
                    "synthetic_dispatches"
                ],
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
        _format: str,
        *_args: Any,
    ) -> None:

        return


def start_health_server(
) -> ThreadingHTTPServer:

    server = ThreadingHTTPServer(
        (
            "0.0.0.0",
            HEALTH_PORT,
        ),
        HealthHandler,
    )

    threading.Thread(
        target=server.serve_forever,
        daemon=True,
    ).start()

    return server


def expect_rejection(
    label: str,
    func,
) -> None:

    rejected = False

    try:
        func()

    except Exception:
        rejected = True

    check(
        label,
        rejected,
    )


def run_validation(
) -> Dict[str, Any]:

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

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
        f"{VERSION}: PUBLIC READ-ONLY ENABLED"
    )

    log(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    section(
        f"{VERSION} TEST 1: SAFETY CONSTANTS"
    )

    check(
        "Authenticated Transport Is Read Only",
        AUTHENTICATED_READ_ONLY,
    )

    check(
        "Public Transport Is Read Only",
        PUBLIC_READ_ONLY,
    )

    check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    check(
        "Network Writes Are Disabled",
        not NETWORK_WRITES_ENABLED,
    )

    check(
        "Real Orders Are Disabled",
        not REAL_ORDERS_ENABLED,
    )

    check(
        "Demo Orders Are Disabled",
        not DEMO_ORDERS_ENABLED,
    )

    section(
        f"{VERSION} TEST 2: API CREDENTIALS"
    )

    check(
        "WEEX API Key Is Present",
        bool(API_KEY),
    )

    check(
        "WEEX API Secret Is Present",
        bool(API_SECRET),
    )

    check(
        "WEEX API Passphrase Is Present",
        bool(
            API_PASSPHRASE
        ),
    )

    section(
        f"{VERSION} TEST 3: LIVE BALANCE"
    )

    balance_payload = authenticated_get(
        BALANCE_PATH
    )

    available_balance = parse_balance(
        balance_payload
    )

    check(
        "Available Balance Was Read",
        available_balance is not None,
    )

    check(
        "Available Balance Is Positive",
        available_balance > 0,
    )

    log(
        f"{VERSION}: AVAILABLE USDT="
        f"{decimal_text(available_balance)}"
    )

    section(
        f"{VERSION} TEST 4: LIVE ACCOUNT CONFIGURATION"
    )

    config_payload = authenticated_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    symbol_config = parse_symbol_config(
        config_payload
    )

    check(
        "Symbol Configuration Was Read",
        bool(symbol_config),
    )

    log(
        f"{VERSION}: SYMBOL CONFIG="
        f"{canonical_json(symbol_config)}"
    )

    section(
        f"{VERSION} TEST 5: LIVE POSITION STATE"
    )

    positions_payload = authenticated_get(
        POSITION_PATH
    )

    positions = parse_positions(
        positions_payload
    )

    symbol_positions = [
        position
        for position in positions
        if str(
            position.get(
                "symbol",
                "",
            )
        ).upper()
        == SYMBOL
    ]

    open_symbol_positions = [
        position
        for position in symbol_positions
        if position_is_open(
            position
        )
    ]

    check(
        "Position Endpoint Was Read",
        positions_payload is not None,
    )

    check(
        "Position Records Were Parsed",
        isinstance(
            positions,
            list,
        ),
    )

    log(
        f"{VERSION}: POSITION ENDPOINT="
        f"{POSITION_PATH}"
    )

    log(
        f"{VERSION}: TOTAL POSITION RECORDS="
        f"{len(positions)}"
    )

    log(
        f"{VERSION}: {SYMBOL} POSITION RECORDS="
        f"{len(symbol_positions)}"
    )

    log(
        f"{VERSION}: {SYMBOL} OPEN POSITIONS="
        f"{len(open_symbol_positions)}"
    )

    section(
        f"{VERSION} TEST 6: LIVE MARKET PRICE"
    )

    price_payload = public_get(
        MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    mark_price = parse_mark_price(
        price_payload
    )

    check(
        "Market Price Was Read",
        mark_price is not None,
    )

    check(
        "Market Price Is Positive",
        mark_price > 0,
    )

    log(
        f"{VERSION}: MARKET PRICE PATH="
        f"{MARK_PRICE_PATH}"
    )

    log(
        f"{VERSION}: MARK PRICE="
        f"{decimal_text(mark_price)}"
    )

    section(
        f"{VERSION} TEST 7: LIVE CONTRACT INFORMATION"
    )

    exchange_payload = public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    (
        min_qty,
        qty_step,
        price_step,
    ) = parse_contract_info(
        exchange_payload
    )

    check(
        "Exchange Information Was Read",
        exchange_payload is not None,
    )

    check(
        "Minimum Quantity Is Positive",
        min_qty > 0,
    )

    check(
        "Quantity Step Is Positive",
        qty_step > 0,
    )

    check(
        "Price Step Is Positive",
        price_step > 0,
    )

    log(
        f"{VERSION}: MIN QTY="
        f"{decimal_text(min_qty)}"
    )

    log(
        f"{VERSION}: QTY STEP="
        f"{decimal_text(qty_step)}"
    )

    log(
        f"{VERSION}: PRICE STEP="
        f"{decimal_text(price_step)}"
    )

    section(
        f"{VERSION} TEST 8: STRATEGY BUDGET"
    )

    entry_margin_budget = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    raw_qty = (
        entry_margin_budget
        * TARGET_LEVERAGE
        / mark_price
    )

    normalized_qty = normalize_quantity_down(
        raw_qty,
        qty_step,
        min_qty,
    )

    normalized_notional = (
        normalized_qty
        * mark_price
    )

    normalized_margin = (
        normalized_notional
        / TARGET_LEVERAGE
    )

    planned_max_strategy_margin = (
        available_balance
        * (
            INITIAL_ENTRY_PERCENT
            + (
                PYRAMID_SIZE_PERCENT
                * MAX_PYRAMID_ADDS
            )
            + (
                BACKUP_SIZE_PERCENT
                * MAX_BACKUPS
            )
        )
        / Decimal("100")
    )

    max_allowed_strategy_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    check(
        "Initial Entry Margin Budget Is Positive",
        entry_margin_budget > 0,
    )

    check(
        "Normalized Quantity Is Positive",
        normalized_qty > 0,
    )

    check(
        "Normalized Quantity Meets Minimum",
        normalized_qty >= min_qty,
    )

    check(
        "Normalized Margin Does Not Exceed 5% Entry Budget",
        normalized_margin
        <= entry_margin_budget,
    )

    check(
        "Planned Maximum Strategy Margin Is Within 35%",
        planned_max_strategy_margin
        <= max_allowed_strategy_margin,
    )

    log(
        f"{VERSION}: ENTRY MARGIN BUDGET="
        f"{decimal_text(entry_margin_budget)} USDT"
    )

    log(
        f"{VERSION}: RAW QTY="
        f"{decimal_text(raw_qty)} BTC"
    )

    log(
        f"{VERSION}: NORMALIZED QTY="
        f"{decimal_text(normalized_qty)} BTC"
    )

    log(
        f"{VERSION}: NORMALIZED MARGIN="
        f"{decimal_text(normalized_margin)} USDT"
    )

    log(
        f"{VERSION}: PLANNED MAX STRATEGY MARGIN="
        f"{decimal_text(planned_max_strategy_margin)} USDT"
    )

    state = new_state(
        available_balance,
        mark_price,
        normalized_qty,
    )

    save_state(
        state
    )

    section(
        f"{VERSION} TEST 9: INITIAL SYNTHETIC ENTRY"
    )

    initial_intent = make_intent(
        "INITIAL_ENTRY",
        1,
        normalized_qty,
    )

    initial_receipt = synthetic_dispatch(
        state,
        initial_intent,
    )

    state[
        "initial_entry_completed"
    ] = True

    state[
        "phase"
    ] = "INITIAL_ENTRY_COMPLETED"

    save_state(
        state
    )

    check(
        "Initial Synthetic Dispatch Completed",
        initial_receipt[
            "completed"
        ],
    )

    check(
        "Initial Dispatch Was Not Transmitted",
        not initial_receipt[
            "transmitted"
        ],
    )

    check(
        "Initial Dispatch Made No Network Write",
        not initial_receipt[
            "network_write"
        ],
    )

    section(
        f"{VERSION} TEST 10: PYRAMID STATE TRANSITION"
    )

    first_pyramid_eligible = (
        state[
            "initial_entry_completed"
        ]
        and state[
            "pyramid_count"
        ]
        < MAX_PYRAMID_ADDS
    )

    check(
        "First Pyramid Add Is Eligible",
        first_pyramid_eligible,
    )

    pyramid_intent = make_intent(
        "PYRAMID",
        1,
        normalized_qty,
    )

    pyramid_receipt = synthetic_dispatch(
        state,
        pyramid_intent,
    )

    state[
        "pyramid_count"
    ] += 1

    state[
        "phase"
    ] = "PYRAMID_COMPLETED"

    save_state(
        state
    )

    check(
        "Pyramid Synthetic Dispatch Completed",
        pyramid_receipt[
            "completed"
        ],
    )

    check(
        "Pyramid Count Is One",
        state[
            "pyramid_count"
        ]
        == 1,
    )

    check(
        "Second Pyramid Add Is Rejected",
        state[
            "pyramid_count"
        ]
        >= MAX_PYRAMID_ADDS,
    )

    section(
        f"{VERSION} TEST 11: BACKUP STATE TRANSITIONS"
    )

    for backup_no in range(
        1,
        MAX_BACKUPS + 1,
    ):

        eligible = (
            state[
                "backup_count"
            ]
            < MAX_BACKUPS
        )

        check(
            f"Backup {backup_no} Is Eligible",
            eligible,
        )

        backup_intent = make_intent(
            "BACKUP",
            backup_no,
            normalized_qty,
        )

        backup_receipt = synthetic_dispatch(
            state,
            backup_intent,
        )

        state[
            "backup_count"
        ] += 1

        state[
            "phase"
        ] = (
            f"BACKUP_{backup_no}_COMPLETED"
        )

        save_state(
            state
        )

        check(
            f"Backup {backup_no} Synthetic Dispatch Completed",
            backup_receipt[
                "completed"
            ],
        )

    check(
        "Backup Count Is Three",
        state[
            "backup_count"
        ]
        == MAX_BACKUPS,
    )

    check(
        "Fourth Backup Is Rejected",
        state[
            "backup_count"
        ]
        >= MAX_BACKUPS,
    )

    section(
        f"{VERSION} TEST 12: TP1 STATE TRANSITION"
    )

    tp1_qty = normalize_quantity_down(
        normalized_qty
        * TP1_PERCENT
        / Decimal("100"),
        qty_step,
        min_qty,
    )

    if tp1_qty == 0:
        tp1_qty = min_qty

    tp1_intent = make_intent(
        "TP1",
        1,
        tp1_qty,
        {
            "reduce_only": True,
        },
    )

    tp1_receipt = synthetic_dispatch(
        state,
        tp1_intent,
    )

    state[
        "tp1_completed"
    ] = True

    state[
        "phase"
    ] = "TP1_COMPLETED"

    save_state(
        state
    )

    check(
        "TP1 Synthetic Dispatch Completed",
        tp1_receipt[
            "completed"
        ],
    )

    check(
        "TP1 Was Not Transmitted",
        not tp1_receipt[
            "transmitted"
        ],
    )

    check(
        "TP1 State Is Completed",
        state[
            "tp1_completed"
        ],
    )

    section(
        f"{VERSION} TEST 13: TP2 STATE TRANSITION"
    )

    tp2_qty = normalize_quantity_down(
        normalized_qty
        * TP2_PERCENT
        / Decimal("100"),
        qty_step,
        min_qty,
    )

    if tp2_qty == 0:
        tp2_qty = min_qty

    tp2_intent = make_intent(
        "TP2",
        1,
        tp2_qty,
        {
            "reduce_only": True,
        },
    )

    tp2_receipt = synthetic_dispatch(
        state,
        tp2_intent,
    )

    state[
        "tp2_completed"
    ] = True

    state[
        "phase"
    ] = "TP2_COMPLETED"

    save_state(
        state
    )

    check(
        "TP2 Synthetic Dispatch Completed",
        tp2_receipt[
            "completed"
        ],
    )

    check(
        "TP2 Was Not Transmitted",
        not tp2_receipt[
            "transmitted"
        ],
    )

    check(
        "TP2 State Is Completed",
        state[
            "tp2_completed"
        ],
    )

    section(
        f"{VERSION} TEST 14: TRAILING ARM"
    )

    trailing_reference = (
        mark_price
        * (
            Decimal("1")
            + (
                TP2_TRIGGER_PERCENT
                / Decimal("100")
            )
        )
    )

    state[
        "trailing_armed"
    ] = bool(
        state[
            "tp1_completed"
        ]
        and state[
            "tp2_completed"
        ]
    )

    state[
        "trailing_reference"
    ] = decimal_text(
        trailing_reference
    )

    state[
        "phase"
    ] = "TRAILING_ARMED"

    save_state(
        state
    )

    check(
        "Trailing Is Armed After TP1 And TP2",
        state[
            "trailing_armed"
        ],
    )

    check(
        "Trailing Distance Is Positive",
        TRAILING_DISTANCE_PERCENT > 0,
    )

    check(
        "Trailing Reference Price Is Positive",
        trailing_reference > 0,
    )

    log(
        f"{VERSION}: TRAILING DISTANCE="
        f"{decimal_text(TRAILING_DISTANCE_PERCENT)}%"
    )

    log(
        f"{VERSION}: TRAILING REFERENCE="
        f"{decimal_text(trailing_reference)}"
    )

    section(
        f"{VERSION} TEST 15: TP3 / TRAILING EXIT"
    )

    tp3_qty = normalize_quantity_down(
        normalized_qty
        * TP3_PERCENT
        / Decimal("100"),
        qty_step,
        min_qty,
    )

    if tp3_qty == 0:
        tp3_qty = min_qty

    tp3_intent = make_intent(
        "TP3_TRAILING_EXIT",
        1,
        tp3_qty,
        {
            "reduce_only": True,
        },
    )

    tp3_receipt = synthetic_dispatch(
        state,
        tp3_intent,
    )

    state[
        "tp3_completed"
    ] = True

    state[
        "phase"
    ] = "TP3_COMPLETED"

    save_state(
        state
    )

    check(
        "TP3 Synthetic Dispatch Completed",
        tp3_receipt[
            "completed"
        ],
    )

    check(
        "TP3 Was Not Transmitted",
        not tp3_receipt[
            "transmitted"
        ],
    )

    check(
        "TP3 State Is Completed",
        state[
            "tp3_completed"
        ],
    )

    section(
        f"{VERSION} TEST 16: TERMINAL STRATEGY EXIT"
    )

    terminal_intent = make_intent(
        "TERMINAL_EXIT",
        1,
        min_qty,
        {
            "reduce_only": True,
        },
    )

    terminal_receipt = synthetic_dispatch(
        state,
        terminal_intent,
    )

    state[
        "terminal_completed"
    ] = True

    state[
        "phase"
    ] = "TERMINAL"

    save_state(
        state
    )

    check(
        "Terminal Synthetic Dispatch Completed",
        terminal_receipt[
            "completed"
        ],
    )

    check(
        "Terminal Dispatch Was Not Transmitted",
        not terminal_receipt[
            "transmitted"
        ],
    )

    check(
        "Terminal State Is Completed",
        state[
            "terminal_completed"
        ],
    )

    section(
        f"{VERSION} TEST 17: COMPLETE STATE MACHINE"
    )

    check(
        "Initial Entry Completed",
        state[
            "initial_entry_completed"
        ],
    )

    check(
        "Exactly One Pyramid Completed",
        state[
            "pyramid_count"
        ]
        == 1,
    )

    check(
        "Exactly Three Backups Completed",
        state[
            "backup_count"
        ]
        == 3,
    )

    check(
        "TP1 Completed",
        state[
            "tp1_completed"
        ],
    )

    check(
        "TP2 Completed",
        state[
            "tp2_completed"
        ],
    )

    check(
        "Trailing Was Armed",
        state[
            "trailing_armed"
        ],
    )

    check(
        "TP3 Completed",
        state[
            "tp3_completed"
        ],
    )

    check(
        "Terminal Exit Completed",
        state[
            "terminal_completed"
        ],
    )

    check(
        "Final Strategy Phase Is Terminal",
        state[
            "phase"
        ]
        == "TERMINAL",
    )

    section(
        f"{VERSION} TEST 18: DURABLE LOCAL SNAPSHOT"
    )

    check(
        "State File Exists",
        STATE_FILE.exists(),
    )

    saved = load_state()

    check(
        "Saved State Integrity Is Valid",
        isinstance(
            saved,
            dict,
        ),
    )

    check(
        "Saved Symbol Is Exact",
        saved[
            "symbol"
        ]
        == SYMBOL,
    )

    check(
        "Saved Pyramid Count Is One",
        saved[
            "pyramid_count"
        ]
        == 1,
    )

    check(
        "Saved Backup Count Is Three",
        saved[
            "backup_count"
        ]
        == 3,
    )

    check(
        "Saved Terminal State Is Complete",
        saved[
            "terminal_completed"
        ]
        and saved[
            "phase"
        ]
        == "TERMINAL",
    )

    log(
        f"{VERSION}: STATE FILE="
        f"{STATE_FILE}"
    )

    section(
        f"{VERSION} TEST 19: RESTART RESTORE"
    )

    restored = load_state()

    check(
        "Restart State Was Restored",
        bool(restored),
    )

    check(
        "Restart Integrity Is Valid",
        restored[
            "symbol"
        ]
        == SYMBOL
        and restored[
            "version"
        ]
        == VERSION,
    )

    check(
        "Consumed Intents Survived Restart",
        restored[
            "consumed_intents"
        ]
        == state[
            "consumed_intents"
        ],
    )

    check(
        "Dispatch Receipts Survived Restart",
        restored[
            "dispatch_receipts"
        ]
        == state[
            "dispatch_receipts"
        ],
    )

    check(
        "Terminal State Survived Restart",
        restored[
            "terminal_completed"
        ]
        and restored[
            "phase"
        ]
        == "TERMINAL",
    )

    section(
        f"{VERSION} TEST 20: RESTART REPLAY REJECTION"
    )

    before_dispatches = len(
        restored[
            "dispatch_receipts"
        ]
    )

    replay_rejected = False

    try:

        synthetic_dispatch(
            restored,
            initial_intent,
        )

    except RuntimeError:

        replay_rejected = True

    check(
        "Consumed Initial Intent Replay Is Rejected",
        replay_rejected,
    )

    check(
        "Replay Produced No Additional Dispatch",
        len(
            restored[
                "dispatch_receipts"
            ]
        )
        == before_dispatches,
    )

    section(
        f"{VERSION} TEST 21: SYNTHETIC RECOVERY DISPATCH"
    )

    recovery_state = load_state()

    recovery_intent = make_intent(
        "RECOVERY_PROBE",
        1,
        min_qty,
        {
            "recovery_only": True,
            "terminal_state_preserved": True,
        },
    )

    recovery_receipt = synthetic_dispatch(
        recovery_state,
        recovery_intent,
    )

    recovery_state[
        "phase"
    ] = "TERMINAL"

    recovery_state[
        "terminal_completed"
    ] = True

    save_state(
        recovery_state
    )

    check(
        "Recovery Dispatch Is Synthetic Only",
        recovery_receipt[
            "synthetic_only"
        ],
    )

    check(
        "Recovery Dispatch Was Not Transmitted",
        not recovery_receipt[
            "transmitted"
        ],
    )

    check(
        "Recovery Dispatch Made No Network Write",
        not recovery_receipt[
            "network_write"
        ],
    )

    section(
        f"{VERSION} TEST 22: WRITE FIREBREAK"
    )

    expect_rejection(
        "HTTP POST Is Rejected",
        lambda: reject_network_write(
            "POST",
            "/capi/v3/order",
        ),
    )

    expect_rejection(
        "HTTP PUT Is Rejected",
        lambda: reject_network_write(
            "PUT",
            "/capi/v3/order",
        ),
    )

    expect_rejection(
        "HTTP PATCH Is Rejected",
        lambda: reject_network_write(
            "PATCH",
            "/capi/v3/order",
        ),
    )

    expect_rejection(
        "HTTP DELETE Is Rejected",
        lambda: reject_network_write(
            "DELETE",
            "/capi/v3/order",
        ),
    )

    expect_rejection(
        "Generic Network Write Is Rejected",
        lambda: reject_network_write(
            "WRITE",
            "/",
        ),
    )

    expect_rejection(
        "Real Order Function Is Rejected",
        lambda: real_order(),
    )

    expect_rejection(
        "Demo Order Function Is Rejected",
        lambda: demo_order(),
    )

    expect_rejection(
        "Leverage Mutation Function Is Rejected",
        lambda: mutate_leverage(),
    )

    expect_rejection(
        "Margin Mutation Function Is Rejected",
        lambda: mutate_margin(),
    )

    check(
        "Network Write Counter Remains Zero",
        COUNTERS[
            "network_writes"
        ]
        == 0,
    )

    section(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    check(
        "All Live Network Activity Was GET Only",
        COUNTERS[
            "network_writes"
        ]
        == 0,
    )

    check(
        "Strategy Lifecycle Reached Terminal",
        recovery_state[
            "phase"
        ]
        == "TERMINAL",
    )

    check(
        "Replay Protection Is Active",
        COUNTERS[
            "replays_blocked"
        ]
        >= 1,
    )

    check(
        "Synthetic Dispatches Were Local Only",
        all(
            not receipt[
                "transmitted"
            ]
            for receipt
            in recovery_state[
                "dispatch_receipts"
            ]
        ),
    )

    check(
        "Corrected Entry Margin Stayed Within 5% Budget",
        normalized_margin
        <= entry_margin_budget,
    )

    log(
        f"{VERSION}: AUTHENTICATED GETS="
        f"{COUNTERS['authenticated_get']}"
    )

    log(
        f"{VERSION}: PUBLIC GETS="
        f"{COUNTERS['public_get']}"
    )

    log(
        f"{VERSION}: SYNTHETIC DISPATCHES="
        f"{COUNTERS['synthetic_dispatches']}"
    )

    log(
        f"{VERSION}: NETWORK WRITES="
        f"{COUNTERS['network_writes']}"
    )

    log(
        f"{VERSION}: REPLAYS BLOCKED="
        f"{COUNTERS['replays_blocked']}"
    )

    log(
        f"{VERSION}: CORRECTED NORMALIZED QTY="
        f"{decimal_text(normalized_qty)} BTC"
    )

    log(
        f"{VERSION}: CORRECTED NORMALIZED MARGIN="
        f"{decimal_text(normalized_margin)} USDT"
    )

    log(
        f"{VERSION}: COMPLETE - NO REAL ORDER WAS SENT"
    )

    log(
        SEPARATOR
    )

    return recovery_state


def heartbeat_loop() -> None:

    heartbeat = 0

    while not STOP_EVENT.wait(
        30
    ):

        heartbeat += 1

        phase = "UNKNOWN"

        try:

            if STATE_FILE.exists():

                phase = str(
                    load_state().get(
                        "phase",
                        "UNKNOWN",
                    )
                )

        except Exception:

            phase = (
                "STATE_READ_ERROR"
            )

        log(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"phase={phase} | "
            f"authenticated-read-only={AUTHENTICATED_READ_ONLY} | "
            f"authenticated-get={COUNTERS['authenticated_get']} | "
            f"public-get={COUNTERS['public_get']} | "
            f"network-writes={COUNTERS['network_writes']} | "
            f"synthetic-dispatches={COUNTERS['synthetic_dispatches']} | "
            f"real-orders=0 | "
            f"demo-orders=0"
        )


def handle_signal(
    _signum: int,
    _frame: Any,
) -> None:

    STOP_EVENT.set()


def main() -> None:

    signal.signal(
        signal.SIGTERM,
        handle_signal,
    )

    signal.signal(
        signal.SIGINT,
        handle_signal,
    )

    server = start_health_server()

    try:

        run_validation()

        heartbeat_loop()

    except Exception as exc:

        section(
            f"{VERSION}: ERROR"
        )

        log(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}"
        )

        raise

    finally:

        server.shutdown()

        server.server_close()


if __name__ == "__main__":
    main()
