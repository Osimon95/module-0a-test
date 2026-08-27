from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import socketserver
import threading
import time
import urllib.parse
import urllib.request
import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_DOWN, getcontext
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

getcontext().prec = 28

print("R29 UNIT D: MAIN.PY ENTERED", flush=True)

# =============================================================================
# R29 UNIT D
# LIVE READ-ONLY SNAPSHOT / READINESS / DECISION-CYCLE VALIDATION
#
# CORRECTED COPY/PASTE VERSION
# PART 1 OF 4
#
# SAFETY:
#   - REAL ORDER EXECUTION DISABLED
#   - DEMO ORDER EXECUTION DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - WEBSOCKET WRITES DISABLED
#   - LEVERAGE MUTATION DISABLED
#   - MARGIN MUTATION DISABLED
#   - POSITION MUTATION DISABLED
#   - ACCOUNT MUTATION DISABLED
#   - GET-ONLY NETWORK ALLOWLIST
#   - SYNTHETIC TRANSPORT ONLY
#
# R29 UNIT D INCREMENT OVER UNIT C:
#   - COHERENT LIVE SNAPSHOT BINDING
#   - SNAPSHOT FRESHNESS / SKEW VALIDATION
#   - FLAT-POSITION READINESS GATE
#   - ISOLATED-MARGIN READINESS GATE
#   - LONG/SHORT 100X READINESS OBSERVATION
#   - READ-ONLY RISK PROJECTION
#   - FROZEN NON-EXECUTABLE DECISION CYCLE
#   - SYNTHETIC DECISION RECEIPT
#   - DECISION REPLAY REJECTION
#   - STALE DECISION REJECTION
#   - DURABLE UNIT D RUNTIME STATE
#   - RESTART CONTINUITY
# =============================================================================

print("R29 UNIT D: IMPORTS COMPLETE", flush=True)

UNIT_NAME = "R29 UNIT D"

CONTRACT_HOST = "https://api-contract.weex.com"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()
ASSET = os.getenv("ASSET", "USDT").strip().upper()

API_KEY = os.getenv("WEEX_API_KEY", "").strip()
SECRET_KEY = os.getenv("WEEX_SECRET_KEY", "").strip()
PASSPHRASE = os.getenv("WEEX_PASSPHRASE", "").strip()

PLANNED_MARGIN_TYPE = "ISOLATED"
PLANNED_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")
PYRAMID_SIZE_PERCENT = Decimal("5")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

SNAPSHOT_MAX_SKEW_SECONDS = 8
HTTP_TIMEOUT_SECONDS = 12
HEARTBEAT_SECONDS = 30

HEALTH_PORT = int(os.getenv("PORT", "10000"))

# =============================================================================
# ABSOLUTE SAFETY SWITCHES
#
# These are deliberately hard-coded constants.
# They are NOT environment-controlled.
# =============================================================================

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

WEBSOCKET_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

# =============================================================================
# GET-ONLY ENDPOINTS
# =============================================================================

MARK_PRICE_PATH = "/capi/v3/market/symbolPrice"
EXCHANGE_INFO_PATH = "/capi/v3/market/exchangeInfo"

BALANCE_PATH = "/capi/v3/account/balance"
POSITIONS_PATH = "/capi/v3/account/position/allPosition"
SYMBOL_CONFIG_PATH = "/capi/v3/account/symbolConfig"

GET_ALLOWLIST = {
    MARK_PRICE_PATH,
    EXCHANGE_INFO_PATH,
    BALANCE_PATH,
    POSITIONS_PATH,
    SYMBOL_CONFIG_PATH,
}

WRITE_METHODS = {
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}

print("R29 UNIT D: CONSTANTS INITIALIZED", flush=True)

# =============================================================================
# OUTPUT / ASSERTION HELPERS
# =============================================================================

LINE = "-" * 92

PASS_ASSERTIONS = 0
TEST_GROUPS = 0


def banner(text: str) -> None:
    print(LINE, flush=True)
    print(text, flush=True)
    print(LINE, flush=True)


def passed(label: str, condition: bool) -> None:
    global PASS_ASSERTIONS

    if not condition:
        raise AssertionError(label)

    PASS_ASSERTIONS += 1

    print(
        f"{label:<82} ✅ PASS",
        flush=True,
    )


def test_header(number: int, title: str) -> None:
    global TEST_GROUPS

    TEST_GROUPS += 1

    banner(
        f"{UNIT_NAME} TEST {number}: {title}"
    )


def local_block(reason: str) -> None:
    print(
        f"{UNIT_NAME} LOCAL BLOCK:",
        flush=True,
    )

    print(
        f"  {reason}",
        flush=True,
    )


def require(condition: bool, reason: str) -> None:
    if not condition:
        local_block(reason)
        raise ValueError(reason)


def expect_block(label: str, fn) -> None:
    try:
        fn()

    except Exception:
        passed(
            label,
            True,
        )
        return

    raise AssertionError(label)


# =============================================================================
# GENERIC HELPERS
# =============================================================================

def d(
    value: Any,
    default: str = "0",
) -> Decimal:

    if value is None or value == "":
        return Decimal(default)

    return Decimal(str(value))


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_obj(value: Any) -> str:
    encoded = canonical_json(value).encode("utf-8")

    return hashlib.sha256(
        encoded
    ).hexdigest()


def now_ms() -> int:
    return int(
        time.time() * 1000
    )


def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    require(
        step > 0,
        "step must be positive",
    )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def choose_state_path() -> Path:
    configured = os.getenv(
        "R29_STATE_PATH",
        "",
    ).strip()

    if configured:
        return Path(configured)

    persistent_dir = Path("/var/data")

    if (
        persistent_dir.exists()
        and persistent_dir.is_dir()
    ):
        return (
            persistent_dir
            / "r29_unit_d_state.json"
        )

    return Path(
        "/tmp/r29_unit_d_state.json"
    )


STATE_PATH = choose_state_path()


# =============================================================================
# IMMUTABLE LIVE OBSERVATION RECORDS
# =============================================================================

@dataclass(frozen=True)
class MarketObservation:
    symbol: str
    mark_price: str
    observed_at_ms: int
    source_path: str
    read_only: bool
    observation_hash: str


@dataclass(frozen=True)
class ContractRules:
    symbol: str
    qty_step: str
    min_qty: str
    price_step: str
    observed_at_ms: int
    source_path: str
    rules_hash: str


@dataclass(frozen=True)
class AccountObservation:
    asset: str
    balance: str
    available_balance: str
    open_symbol_positions: int
    observed_at_ms: int
    balance_source_path: str
    positions_source_path: str
    observation_hash: str


@dataclass(frozen=True)
class SymbolConfiguration:
    symbol: str
    margin_type: str
    separated_type: str
    cross_leverage: str
    isolated_long_leverage: str
    isolated_short_leverage: str
    observed_at_ms: int
    source_path: str
    config_hash: str


# =============================================================================
# UNIT D SNAPSHOT / READINESS RECORDS
# =============================================================================

@dataclass(frozen=True)
class LiveSnapshot:
    snapshot_id: str

    symbol: str
    asset: str

    market_hash: str
    rules_hash: str
    account_hash: str
    symbol_config_hash: str

    first_observed_at_ms: int
    last_observed_at_ms: int

    skew_ms: int
    captured_at_ms: int

    snapshot_hash: str


@dataclass(frozen=True)
class ReadinessAssessment:
    symbol: str

    flat_position_gate: bool
    margin_mode_gate: bool

    long_leverage_gate: bool
    short_leverage_gate: bool

    balance_gate: bool
    rules_gate: bool
    snapshot_fresh_gate: bool

    execution_ready: bool
    mutation_required: bool

    assessment_hash: str


@dataclass(frozen=True)
class RiskProjection:
    available_balance: str

    entry_percent: str
    margin_budget: str

    planned_leverage: str
    planned_notional: str

    raw_quantity: str
    rounded_quantity: str

    projected_notional: str
    projected_margin: str

    max_fund_exposure_percent: str

    projection_hash: str


@dataclass(frozen=True)
class FrozenDecision:
    decision_id: str

    snapshot_hash: str
    readiness_hash: str
    projection_hash: str

    symbol: str

    side: str
    position_side: str

    quantity: str

    executable: bool
    synthetic_only: bool

    hold_reason: str

    created_at_ms: int
    expires_at_ms: int

    decision_hash: str


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str

    decision_id: str
    decision_hash: str

    transport: str
    transmitted: bool

    network_write_count: int

    created_at_ms: int

    receipt_hash: str


@dataclass
class RuntimeState:
    unit: str

    runtime_id: str

    generation: int
    recovery_epoch: int
    boot_count: int

    created_at_ms: int
    updated_at_ms: int

    snapshot_hash: str
    readiness_hash: str
    projection_hash: str
    decision_hash: str
    receipt_hash: str

    last_decision_id: str

    real_order_count: int
    demo_order_count: int
    network_write_count: int

    live_read_count: int
    synthetic_dispatch_count: int


# =============================================================================
# STRICT GET-ONLY NETWORK TRANSPORT
# =============================================================================

class ReadOnlyTransport:

    def __init__(self) -> None:
        self.live_read_count = 0

        self.real_write_blocks = 0
        self.demo_write_blocks = 0

        self.websocket_write_blocks = 0

        self.leverage_mutation_blocks = 0
        self.margin_mutation_blocks = 0
        self.position_mutation_blocks = 0
        self.account_mutation_blocks = 0

    @staticmethod
    def _assert_host(host: str) -> None:
        require(
            host == CONTRACT_HOST,
            "contract host is not allowlisted",
        )

    @staticmethod
    def _assert_get_path(path: str) -> None:
        require(
            path in GET_ALLOWLIST,
            "GET path is not allowlisted",
        )

    @staticmethod
    def _query_string(
        params: Optional[Dict[str, Any]],
    ) -> str:

        if not params:
            return ""

        clean = {
            key: value
            for key, value in params.items()
            if value is not None
        }

        return urllib.parse.urlencode(
            clean
        )

    def _build_url(
        self,
        path: str,
        params: Optional[Dict[str, Any]],
    ) -> str:

        self._assert_host(
            CONTRACT_HOST
        )

        self._assert_get_path(
            path
        )

        query = self._query_string(
            params
        )

        if query:
            return (
                CONTRACT_HOST
                + path
                + "?"
                + query
            )

        return (
            CONTRACT_HOST
            + path
        )

    @staticmethod
    def _decode_response(
        response,
    ) -> Any:

        raw = response.read().decode(
            "utf-8"
        )

        require(
            bool(raw),
            "empty HTTP response",
        )

        return json.loads(raw)

    def public_get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:

        url = self._build_url(
            path,
            params,
        )

        request = urllib.request.Request(
            url=url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": "R29-UNIT-D-READ-ONLY",
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            payload = self._decode_response(
                response
            )

        self.live_read_count += 1

        return payload

    @staticmethod
    def _signature(
        timestamp: str,
        method: str,
        path: str,
        query_string: str,
        body: str = "",
    ) -> str:

        require(
            bool(SECRET_KEY),
            "WEEX secret key missing",
        )

        request_path = path

        if query_string:
            request_path += (
                "?"
                + query_string
            )

        prehash = (
            timestamp
            + method.upper()
            + request_path
            + body
        )

        digest = hmac.new(
            SECRET_KEY.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(
            digest
        ).decode("utf-8")

    def private_get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:

        require(
            bool(API_KEY),
            "WEEX API key missing",
        )

        require(
            bool(SECRET_KEY),
            "WEEX secret key missing",
        )

        require(
            bool(PASSPHRASE),
            "WEEX passphrase missing",
        )

        self._assert_host(
            CONTRACT_HOST
        )

        self._assert_get_path(
            path
        )

        query_string = self._query_string(
            params
        )

        timestamp = str(
            now_ms()
        )

        signature = self._signature(
            timestamp=timestamp,
            method="GET",
            path=path,
            query_string=query_string,
            body="",
        )

        url = (
            CONTRACT_HOST
            + path
        )

        if query_string:
            url += (
                "?"
                + query_string
            )

        headers = {
            "Accept": "application/json",
            "User-Agent": "R29-UNIT-D-READ-ONLY",
            "ACCESS-KEY": API_KEY,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": PASSPHRASE,
            "ACCESS-TIMESTAMP": timestamp,
        }

        request = urllib.request.Request(
            url=url,
            method="GET",
            headers=headers,
        )

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
        ) as response:

            payload = self._decode_response(
                response
            )

        self.live_read_count += 1

        return payload

    def real_write(
        self,
        method: str,
        path: str,
        payload: Any,
    ) -> None:

        self.real_write_blocks += 1

        local_block(
            "REAL network write blocked"
        )

        raise RuntimeError(
            "REAL network write blocked"
        )

    def demo_write(
        self,
        method: str,
        path: str,
        payload: Any,
    ) -> None:

        self.demo_write_blocks += 1

        local_block(
            "DEMO network write blocked"
        )

        raise RuntimeError(
            "DEMO network write blocked"
        )

    def websocket_write(
        self,
        payload: Any,
    ) -> None:

        self.websocket_write_blocks += 1

        local_block(
            "WebSocket write blocked"
        )

        raise RuntimeError(
            "WebSocket write blocked"
        )

    def mutate_leverage(
        self,
        payload: Any,
    ) -> None:

        self.leverage_mutation_blocks += 1

        local_block(
            "leverage mutation disabled"
        )

        raise RuntimeError(
            "leverage mutation disabled"
        )

    def mutate_margin(
        self,
        payload: Any,
    ) -> None:

        self.margin_mutation_blocks += 1

        local_block(
            "margin mutation disabled"
        )

        raise RuntimeError(
            "margin mutation disabled"
        )

    def mutate_position(
        self,
        payload: Any,
    ) -> None:

        self.position_mutation_blocks += 1

        local_block(
            "position mutation disabled"
        )

        raise RuntimeError(
            "position mutation disabled"
        )

    def mutate_account(
        self,
        payload: Any,
    ) -> None:

        self.account_mutation_blocks += 1

        local_block(
            "account mutation disabled"
        )

        raise RuntimeError(
            "account mutation disabled"
        )


TRANSPORT = ReadOnlyTransport()

print(
    "R29 UNIT D: PART 1 DEFINITIONS LOADED",
    flush=True,
)

# =============================================================================
# END R29 UNIT D - PART 1 OF 4
#
# PASTE PART 2 IMMEDIATELY BELOW THIS LINE.
# DO NOT ADD INDENTATION AT THE JOIN.
# =============================================================================
# =============================================================================
# R29 UNIT D
# LIVE READ-ONLY SNAPSHOT / READINESS / DECISION-CYCLE VALIDATION
#
# CORRECTED COPY/PASTE VERSION
# PART 2 OF 4
#
# CONTINUES DIRECTLY FROM PART 1.
# ZERO-INDENTATION JOIN.
# =============================================================================


# =============================================================================
# API RESPONSE NORMALIZATION
# =============================================================================

def unwrap_payload(
    payload: Any,
) -> Any:

    if not isinstance(
        payload,
        dict,
    ):
        return payload

    for key in (
        "data",
        "result",
    ):
        if key in payload:
            return payload[key]

    return payload


def first_dict(
    value: Any,
) -> Dict[str, Any]:

    value = unwrap_payload(
        value
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    if isinstance(
        value,
        list,
    ):
        for item in value:
            if isinstance(
                item,
                dict,
            ):
                return item

    return {}


def extract_number(
    mapping: Dict[str, Any],
    keys: Iterable[str],
    default: str = "0",
) -> Decimal:

    for key in keys:
        if key not in mapping:
            continue

        value = mapping.get(
            key
        )

        if value in (
            None,
            "",
        ):
            continue

        try:
            return d(
                value
            )

        except Exception:
            continue

    return d(
        default
    )


def extract_text(
    mapping: Dict[str, Any],
    keys: Iterable[str],
    default: str = "",
) -> str:

    for key in keys:
        if key not in mapping:
            continue

        value = mapping.get(
            key
        )

        if value is None:
            continue

        text = str(
            value
        ).strip()

        if text:
            return text

    return default


def recursive_dicts(
    value: Any,
) -> Iterable[Dict[str, Any]]:

    if isinstance(
        value,
        dict,
    ):
        yield value

        for child in value.values():
            yield from recursive_dicts(
                child
            )

    elif isinstance(
        value,
        list,
    ):
        for child in value:
            yield from recursive_dicts(
                child
            )


def find_symbol_mapping(
    payload: Any,
    symbol: str,
) -> Dict[str, Any]:

    wanted = symbol.upper()

    fallback: Dict[str, Any] = {}

    for item in recursive_dicts(
        payload
    ):
        if not fallback:
            fallback = item

        observed_symbol = extract_text(
            item,
            (
                "symbol",
                "contractCode",
                "contract",
                "instId",
            ),
            "",
        ).upper()

        if observed_symbol == wanted:
            return item

    return fallback


def normalize_margin_type(
    value: Any,
) -> str:

    text = str(
        value or ""
    ).strip().upper()

    aliases = {
        "ISOLATED": "ISOLATED",
        "FIXED": "ISOLATED",
        "SEPARATED": "ISOLATED",
        "CROSS": "CROSS",
        "CROSSED": "CROSS",
    }

    return aliases.get(
        text,
        text,
    )


# =============================================================================
# LIVE PUBLIC MARKET OBSERVATION
# =============================================================================

def observe_market() -> MarketObservation:

    payload = TRANSPORT.public_get(
        MARK_PRICE_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    mapping = find_symbol_mapping(
        payload,
        SYMBOL,
    )

    observed_symbol = extract_text(
        mapping,
        (
            "symbol",
            "contractCode",
        ),
        SYMBOL,
    ).upper()

    mark_price = extract_number(
        mapping,
        (
            "markPrice",
            "price",
            "indexPrice",
            "lastPrice",
            "last",
        ),
    )

    require(
        observed_symbol == SYMBOL,
        "market observation symbol mismatch",
    )

    require(
        mark_price > 0,
        "market mark price is not positive",
    )

    observed_at = now_ms()

    body = {
        "symbol": observed_symbol,
        "mark_price": str(mark_price),
        "observed_at_ms": observed_at,
        "source_path": MARK_PRICE_PATH,
        "read_only": True,
    }

    observation_hash = sha256_obj(
        body
    )

    return MarketObservation(
        symbol=observed_symbol,
        mark_price=str(mark_price),
        observed_at_ms=observed_at,
        source_path=MARK_PRICE_PATH,
        read_only=True,
        observation_hash=observation_hash,
    )


# =============================================================================
# LIVE PUBLIC CONTRACT RULE OBSERVATION
# =============================================================================

def observe_contract_rules() -> ContractRules:

    payload = TRANSPORT.public_get(
        EXCHANGE_INFO_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    mapping = find_symbol_mapping(
        payload,
        SYMBOL,
    )

    observed_symbol = extract_text(
        mapping,
        (
            "symbol",
            "contractCode",
        ),
        SYMBOL,
    ).upper()

    qty_step = extract_number(
        mapping,
        (
            "quantityStep",
            "qtyStep",
            "stepSize",
            "sizeStep",
            "volumePlace",
        ),
    )

    min_qty = extract_number(
        mapping,
        (
            "minOrderQty",
            "minQty",
            "minTradeNum",
            "minTradeAmount",
            "minSize",
        ),
    )

    price_step = extract_number(
        mapping,
        (
            "priceStep",
            "tickSize",
            "priceTick",
            "priceEndStep",
        ),
    )

    # Unit C already established the current BTCUSDT contract rules.
    # These fallbacks only normalize API schema variations where the
    # exchange supplies decimal precision rather than the explicit step.
    if qty_step <= 0:
        quantity_precision = extract_number(
            mapping,
            (
                "quantityPrecision",
                "qtyPrecision",
                "volumePlace",
            ),
            "-1",
        )

        if quantity_precision >= 0:
            qty_step = Decimal("1").scaleb(
                -int(quantity_precision)
            )

    if min_qty <= 0:
        min_qty = qty_step

    if price_step <= 0:
        price_precision = extract_number(
            mapping,
            (
                "pricePrecision",
                "pricePlace",
            ),
            "-1",
        )

        if price_precision >= 0:
            price_step = Decimal("1").scaleb(
                -int(price_precision)
            )

    require(
        observed_symbol == SYMBOL,
        "contract rules symbol mismatch",
    )

    require(
        qty_step > 0,
        "quantity step is not positive",
    )

    require(
        min_qty > 0,
        "minimum quantity is not positive",
    )

    require(
        price_step > 0,
        "price step is not positive",
    )

    observed_at = now_ms()

    body = {
        "symbol": observed_symbol,
        "qty_step": str(qty_step),
        "min_qty": str(min_qty),
        "price_step": str(price_step),
        "observed_at_ms": observed_at,
        "source_path": EXCHANGE_INFO_PATH,
    }

    rules_hash = sha256_obj(
        body
    )

    return ContractRules(
        symbol=observed_symbol,
        qty_step=str(qty_step),
        min_qty=str(min_qty),
        price_step=str(price_step),
        observed_at_ms=observed_at,
        source_path=EXCHANGE_INFO_PATH,
        rules_hash=rules_hash,
    )


# =============================================================================
# PRIVATE ACCOUNT OBSERVATION
# =============================================================================

def _find_asset_mapping(
    payload: Any,
    asset: str,
) -> Dict[str, Any]:

    wanted = asset.upper()

    fallback: Dict[str, Any] = {}

    for item in recursive_dicts(
        payload
    ):
        if not fallback:
            fallback = item

        observed_asset = extract_text(
            item,
            (
                "coin",
                "asset",
                "currency",
                "marginCoin",
            ),
            "",
        ).upper()

        if observed_asset == wanted:
            return item

    return fallback


def _position_size(
    mapping: Dict[str, Any],
) -> Decimal:

    return extract_number(
        mapping,
        (
            "size",
            "positionAmt",
            "positionAmount",
            "total",
            "holdVol",
            "available",
            "quantity",
            "qty",
        ),
    )


def _count_open_symbol_positions(
    payload: Any,
    symbol: str,
) -> int:

    wanted = symbol.upper()

    count = 0

    for item in recursive_dicts(
        payload
    ):
        observed_symbol = extract_text(
            item,
            (
                "symbol",
                "contractCode",
                "contract",
            ),
            "",
        ).upper()

        if observed_symbol != wanted:
            continue

        size = abs(
            _position_size(
                item
            )
        )

        if size > 0:
            count += 1

    return count


def observe_account() -> AccountObservation:

    balance_payload = TRANSPORT.private_get(
        BALANCE_PATH,
        {
            "coin": ASSET,
        },
    )

    positions_payload = TRANSPORT.private_get(
        POSITIONS_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    balance_mapping = _find_asset_mapping(
        balance_payload,
        ASSET,
    )

    observed_asset = extract_text(
        balance_mapping,
        (
            "coin",
            "asset",
            "currency",
            "marginCoin",
        ),
        ASSET,
    ).upper()

    balance = extract_number(
        balance_mapping,
        (
            "balance",
            "equity",
            "accountEquity",
            "total",
            "walletBalance",
        ),
    )

    available_balance = extract_number(
        balance_mapping,
        (
            "available",
            "availableBalance",
            "availableEquity",
            "free",
            "maxAvailable",
        ),
    )

    open_positions = _count_open_symbol_positions(
        positions_payload,
        SYMBOL,
    )

    require(
        observed_asset == ASSET,
        "account asset mismatch",
    )

    require(
        balance >= 0,
        "account balance is negative",
    )

    require(
        available_balance >= 0,
        "available balance is negative",
    )

    require(
        open_positions >= 0,
        "position count is negative",
    )

    observed_at = now_ms()

    body = {
        "asset": observed_asset,
        "balance": str(balance),
        "available_balance": str(
            available_balance
        ),
        "open_symbol_positions": open_positions,
        "observed_at_ms": observed_at,
        "balance_source_path": BALANCE_PATH,
        "positions_source_path": POSITIONS_PATH,
    }

    observation_hash = sha256_obj(
        body
    )

    return AccountObservation(
        asset=observed_asset,
        balance=str(balance),
        available_balance=str(
            available_balance
        ),
        open_symbol_positions=open_positions,
        observed_at_ms=observed_at,
        balance_source_path=BALANCE_PATH,
        positions_source_path=POSITIONS_PATH,
        observation_hash=observation_hash,
    )


# =============================================================================
# PRIVATE SYMBOL CONFIGURATION OBSERVATION
# =============================================================================

def observe_symbol_configuration() -> SymbolConfiguration:

    payload = TRANSPORT.private_get(
        SYMBOL_CONFIG_PATH,
        {
            "symbol": SYMBOL,
        },
    )

    mapping = find_symbol_mapping(
        payload,
        SYMBOL,
    )

    observed_symbol = extract_text(
        mapping,
        (
            "symbol",
            "contractCode",
        ),
        SYMBOL,
    ).upper()

    margin_type = normalize_margin_type(
        extract_text(
            mapping,
            (
                "marginType",
                "marginMode",
                "margin_mode",
            ),
            "",
        )
    )

    separated_type = extract_text(
        mapping,
        (
            "positionMode",
            "positionType",
            "holdMode",
            "separatedType",
        ),
        "",
    ).upper()

    cross_leverage = extract_number(
        mapping,
        (
            "crossLeverage",
            "crossMarginLeverage",
            "leverage",
        ),
    )

    isolated_long = extract_number(
        mapping,
        (
            "isolatedLongLeverage",
            "longLeverage",
            "fixedLongLeverage",
        ),
    )

    isolated_short = extract_number(
        mapping,
        (
            "isolatedShortLeverage",
            "shortLeverage",
            "fixedShortLeverage",
        ),
    )

    require(
        observed_symbol == SYMBOL,
        "symbol configuration symbol mismatch",
    )

    require(
        margin_type in {
            "ISOLATED",
            "CROSS",
        },
        "unrecognized margin type",
    )

    require(
        isolated_long > 0,
        "isolated long leverage is not positive",
    )

    require(
        isolated_short > 0,
        "isolated short leverage is not positive",
    )

    observed_at = now_ms()

    body = {
        "symbol": observed_symbol,
        "margin_type": margin_type,
        "separated_type": separated_type,
        "cross_leverage": str(
            cross_leverage
        ),
        "isolated_long_leverage": str(
            isolated_long
        ),
        "isolated_short_leverage": str(
            isolated_short
        ),
        "observed_at_ms": observed_at,
        "source_path": SYMBOL_CONFIG_PATH,
    }

    config_hash = sha256_obj(
        body
    )

    return SymbolConfiguration(
        symbol=observed_symbol,
        margin_type=margin_type,
        separated_type=separated_type,
        cross_leverage=str(
            cross_leverage
        ),
        isolated_long_leverage=str(
            isolated_long
        ),
        isolated_short_leverage=str(
            isolated_short
        ),
        observed_at_ms=observed_at,
        source_path=SYMBOL_CONFIG_PATH,
        config_hash=config_hash,
    )


# =============================================================================
# COHERENT LIVE SNAPSHOT CONSTRUCTION
# =============================================================================

def build_live_snapshot(
    market: MarketObservation,
    rules: ContractRules,
    account: AccountObservation,
    config: SymbolConfiguration,
) -> LiveSnapshot:

    require(
        market.symbol == SYMBOL,
        "market snapshot symbol mismatch",
    )

    require(
        rules.symbol == SYMBOL,
        "rules snapshot symbol mismatch",
    )

    require(
        config.symbol == SYMBOL,
        "configuration snapshot symbol mismatch",
    )

    require(
        account.asset == ASSET,
        "account snapshot asset mismatch",
    )

    timestamps = [
        market.observed_at_ms,
        rules.observed_at_ms,
        account.observed_at_ms,
        config.observed_at_ms,
    ]

    first_observed = min(
        timestamps
    )

    last_observed = max(
        timestamps
    )

    skew_ms = (
        last_observed
        - first_observed
    )

    require(
        skew_ms
        <= SNAPSHOT_MAX_SKEW_SECONDS * 1000,
        "live snapshot observation skew too large",
    )

    snapshot_id = str(
        uuid.uuid4()
    )

    captured_at = now_ms()

    body = {
        "snapshot_id": snapshot_id,
        "symbol": SYMBOL,
        "asset": ASSET,
        "market_hash": market.observation_hash,
        "rules_hash": rules.rules_hash,
        "account_hash": account.observation_hash,
        "symbol_config_hash": config.config_hash,
        "first_observed_at_ms": first_observed,
        "last_observed_at_ms": last_observed,
        "skew_ms": skew_ms,
        "captured_at_ms": captured_at,
    }

    snapshot_hash = sha256_obj(
        body
    )

    return LiveSnapshot(
        snapshot_id=snapshot_id,
        symbol=SYMBOL,
        asset=ASSET,
        market_hash=market.observation_hash,
        rules_hash=rules.rules_hash,
        account_hash=account.observation_hash,
        symbol_config_hash=config.config_hash,
        first_observed_at_ms=first_observed,
        last_observed_at_ms=last_observed,
        skew_ms=skew_ms,
        captured_at_ms=captured_at,
        snapshot_hash=snapshot_hash,
    )


def validate_snapshot_freshness(
    snapshot: LiveSnapshot,
    reference_ms: Optional[int] = None,
) -> None:

    if reference_ms is None:
        reference_ms = now_ms()

    age_ms = (
        reference_ms
        - snapshot.last_observed_at_ms
    )

    require(
        age_ms >= 0,
        "snapshot timestamp is in the future",
    )

    require(
        age_ms
        <= SIGNAL_EXPIRY_SECONDS * 1000,
        "live snapshot is stale",
    )

    require(
        snapshot.skew_ms
        <= SNAPSHOT_MAX_SKEW_SECONDS * 1000,
        "snapshot skew exceeds limit",
    )


# =============================================================================
# READINESS ASSESSMENT
# =============================================================================

def build_readiness_assessment(
    snapshot: LiveSnapshot,
    account: AccountObservation,
    rules: ContractRules,
    config: SymbolConfiguration,
) -> ReadinessAssessment:

    validate_snapshot_freshness(
        snapshot
    )

    flat_position_gate = (
        account.open_symbol_positions == 0
    )

    margin_mode_gate = (
        config.margin_type
        == PLANNED_MARGIN_TYPE
    )

    long_leverage_gate = (
        d(
            config.isolated_long_leverage
        )
        >= PLANNED_LEVERAGE
    )

    short_leverage_gate = (
        d(
            config.isolated_short_leverage
        )
        >= PLANNED_LEVERAGE
    )

    balance_gate = (
        d(
            account.available_balance
        )
        > 0
    )

    rules_gate = (
        d(
            rules.qty_step
        )
        > 0
        and d(
            rules.min_qty
        )
        > 0
        and d(
            rules.price_step
        )
        > 0
    )

    snapshot_fresh_gate = True

    # Unit D does not execute even if all observations become ready.
    # This boolean is only an observational readiness result.
    execution_ready = all(
        (
            flat_position_gate,
            margin_mode_gate,
            long_leverage_gate,
            short_leverage_gate,
            balance_gate,
            rules_gate,
            snapshot_fresh_gate,
        )
    )

    mutation_required = not (
        margin_mode_gate
        and long_leverage_gate
        and short_leverage_gate
    )

    body = {
        "symbol": SYMBOL,
        "flat_position_gate": flat_position_gate,
        "margin_mode_gate": margin_mode_gate,
        "long_leverage_gate": long_leverage_gate,
        "short_leverage_gate": short_leverage_gate,
        "balance_gate": balance_gate,
        "rules_gate": rules_gate,
        "snapshot_fresh_gate": snapshot_fresh_gate,
        "execution_ready": execution_ready,
        "mutation_required": mutation_required,
        "snapshot_hash": snapshot.snapshot_hash,
    }

    assessment_hash = sha256_obj(
        body
    )

    return ReadinessAssessment(
        symbol=SYMBOL,
        flat_position_gate=flat_position_gate,
        margin_mode_gate=margin_mode_gate,
        long_leverage_gate=long_leverage_gate,
        short_leverage_gate=short_leverage_gate,
        balance_gate=balance_gate,
        rules_gate=rules_gate,
        snapshot_fresh_gate=snapshot_fresh_gate,
        execution_ready=execution_ready,
        mutation_required=mutation_required,
        assessment_hash=assessment_hash,
    )


# =============================================================================
# READ-ONLY INITIAL ENTRY RISK PROJECTION
# =============================================================================

def build_risk_projection(
    market: MarketObservation,
    account: AccountObservation,
    rules: ContractRules,
) -> RiskProjection:

    available_balance = d(
        account.available_balance
    )

    mark_price = d(
        market.mark_price
    )

    qty_step = d(
        rules.qty_step
    )

    min_qty = d(
        rules.min_qty
    )

    require(
        available_balance > 0,
        "available balance must be positive",
    )

    require(
        mark_price > 0,
        "mark price must be positive",
    )

    margin_budget = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    planned_notional = (
        margin_budget
        * PLANNED_LEVERAGE
    )

    raw_quantity = (
        planned_notional
        / mark_price
    )

    rounded_quantity = floor_to_step(
        raw_quantity,
        qty_step,
    )

    # If downward rounding falls below the contract minimum,
    # Unit D projects the minimum quantity rather than attempting
    # any exchange action.
    if rounded_quantity < min_qty:
        rounded_quantity = min_qty

    projected_notional = (
        rounded_quantity
        * mark_price
    )

    projected_margin = (
        projected_notional
        / PLANNED_LEVERAGE
    )

    max_allowed_margin = (
        available_balance
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    require(
        margin_budget > 0,
        "margin budget is not positive",
    )

    require(
        planned_notional > 0,
        "planned notional is not positive",
    )

    require(
        rounded_quantity >= min_qty,
        "rounded quantity is below minimum",
    )

    require(
        projected_margin
        <= max_allowed_margin,
        "projected margin exceeds fund exposure cap",
    )

    body = {
        "available_balance": str(
            available_balance
        ),
        "entry_percent": str(
            INITIAL_ENTRY_PERCENT
        ),
        "margin_budget": str(
            margin_budget
        ),
        "planned_leverage": str(
            PLANNED_LEVERAGE
        ),
        "planned_notional": str(
            planned_notional
        ),
        "raw_quantity": str(
            raw_quantity
        ),
        "rounded_quantity": str(
            rounded_quantity
        ),
        "projected_notional": str(
            projected_notional
        ),
        "projected_margin": str(
            projected_margin
        ),
        "max_fund_exposure_percent": str(
            MAX_FUND_EXPOSURE_PERCENT
        ),
    }

    projection_hash = sha256_obj(
        body
    )

    return RiskProjection(
        available_balance=str(
            available_balance
        ),
        entry_percent=str(
            INITIAL_ENTRY_PERCENT
        ),
        margin_budget=str(
            margin_budget
        ),
        planned_leverage=str(
            PLANNED_LEVERAGE
        ),
        planned_notional=str(
            planned_notional
        ),
        raw_quantity=str(
            raw_quantity
        ),
        rounded_quantity=str(
            rounded_quantity
        ),
        projected_notional=str(
            projected_notional
        ),
        projected_margin=str(
            projected_margin
        ),
        max_fund_exposure_percent=str(
            MAX_FUND_EXPOSURE_PERCENT
        ),
        projection_hash=projection_hash,
    )


# =============================================================================
# FROZEN DECISION CONSTRUCTION
# =============================================================================

def determine_hold_reason(
    readiness: ReadinessAssessment,
) -> str:

    if not readiness.snapshot_fresh_gate:
        return "SNAPSHOT_NOT_FRESH"

    if not readiness.flat_position_gate:
        return "POSITION_NOT_FLAT"

    if not readiness.balance_gate:
        return "BALANCE_NOT_READY"

    if not readiness.rules_gate:
        return "CONTRACT_RULES_NOT_READY"

    if not readiness.margin_mode_gate:
        return "MARGIN_MODE_NOT_READY"

    if (
        not readiness.long_leverage_gate
        or not readiness.short_leverage_gate
    ):
        return "LEVERAGE_NOT_READY"

    # Even if all observational gates pass,
    # Unit D is deliberately non-executable.
    return "UNIT_D_EXECUTION_DISABLED"


def build_frozen_decision(
    snapshot: LiveSnapshot,
    readiness: ReadinessAssessment,
    projection: RiskProjection,
) -> FrozenDecision:

    created_at = now_ms()

    expires_at = (
        created_at
        + SIGNAL_EXPIRY_SECONDS * 1000
    )

    hold_reason = determine_hold_reason(
        readiness
    )

    decision_id = str(
        uuid.uuid4()
    )

    body = {
        "decision_id": decision_id,
        "snapshot_hash": snapshot.snapshot_hash,
        "readiness_hash": readiness.assessment_hash,
        "projection_hash": projection.projection_hash,
        "symbol": SYMBOL,
        "side": "BUY",
        "position_side": "LONG",
        "quantity": projection.rounded_quantity,
        "executable": False,
        "synthetic_only": True,
        "hold_reason": hold_reason,
        "created_at_ms": created_at,
        "expires_at_ms": expires_at,
    }

    decision_hash = sha256_obj(
        body
    )

    return FrozenDecision(
        decision_id=decision_id,
        snapshot_hash=snapshot.snapshot_hash,
        readiness_hash=readiness.assessment_hash,
        projection_hash=projection.projection_hash,
        symbol=SYMBOL,
        side="BUY",
        position_side="LONG",
        quantity=projection.rounded_quantity,
        executable=False,
        synthetic_only=True,
        hold_reason=hold_reason,
        created_at_ms=created_at,
        expires_at_ms=expires_at,
        decision_hash=decision_hash,
    )


def validate_frozen_decision(
    decision: FrozenDecision,
    snapshot: LiveSnapshot,
    readiness: ReadinessAssessment,
    projection: RiskProjection,
    reference_ms: Optional[int] = None,
) -> None:

    if reference_ms is None:
        reference_ms = now_ms()

    require(
        decision.symbol == SYMBOL,
        "decision symbol mismatch",
    )

    require(
        decision.side == "BUY",
        "decision side mismatch",
    )

    require(
        decision.position_side == "LONG",
        "decision position side mismatch",
    )

    require(
        decision.snapshot_hash
        == snapshot.snapshot_hash,
        "decision snapshot binding mismatch",
    )

    require(
        decision.readiness_hash
        == readiness.assessment_hash,
        "decision readiness binding mismatch",
    )

    require(
        decision.projection_hash
        == projection.projection_hash,
        "decision projection binding mismatch",
    )

    require(
        decision.executable is False,
        "decision unexpectedly executable",
    )

    require(
        decision.synthetic_only is True,
        "decision is not synthetic-only",
    )

    require(
        bool(
            decision.hold_reason
        ),
        "decision hold reason missing",
    )

    require(
        reference_ms
        <= decision.expires_at_ms,
        "decision is stale",
    )

    body = {
        "decision_id": decision.decision_id,
        "snapshot_hash": decision.snapshot_hash,
        "readiness_hash": decision.readiness_hash,
        "projection_hash": decision.projection_hash,
        "symbol": decision.symbol,
        "side": decision.side,
        "position_side": decision.position_side,
        "quantity": decision.quantity,
        "executable": decision.executable,
        "synthetic_only": decision.synthetic_only,
        "hold_reason": decision.hold_reason,
        "created_at_ms": decision.created_at_ms,
        "expires_at_ms": decision.expires_at_ms,
    }

    require(
        sha256_obj(
            body
        )
        == decision.decision_hash,
        "decision integrity hash mismatch",
    )


print(
    "R29 UNIT D: PART 2 DEFINITIONS LOADED",
    flush=True,
)

# =============================================================================
# END R29 UNIT D - PART 2 OF 4
#
# PASTE PART 3 IMMEDIATELY BELOW THIS LINE.
# DO NOT ADD INDENTATION AT THE JOIN.
# =============================================================================
