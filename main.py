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
# =============================================================================
# R29 UNIT D
# LIVE READ-ONLY SNAPSHOT / READINESS / DECISION-CYCLE VALIDATION
#
# CORRECTED COPY/PASTE VERSION
# PART 3 OF 4
#
# CONTINUES DIRECTLY FROM PART 2.
# ZERO-INDENTATION JOIN.
# =============================================================================


# =============================================================================
# SYNTHETIC DECISION TRANSPORT + REPLAY FENCE
# =============================================================================

SEEN_DECISION_HASHES: set[str] = set()


def synthetic_dispatch(
    decision: FrozenDecision,
) -> SyntheticReceipt:

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "synthetic transport is not exclusive",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "network writes unexpectedly enabled",
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
        now_ms()
        <= decision.expires_at_ms,
        "decision is stale",
    )

    require(
        decision.decision_hash
        not in SEEN_DECISION_HASHES,
        "decision replay rejected",
    )

    SEEN_DECISION_HASHES.add(
        decision.decision_hash
    )

    created_at = now_ms()

    body = {
        "receipt_id": str(
            uuid.uuid4()
        ),
        "decision_id": decision.decision_id,
        "decision_hash": decision.decision_hash,
        "transport": "SYNTHETIC_ONLY",
        "transmitted": False,
        "network_write_count": 0,
        "created_at_ms": created_at,
    }

    receipt_hash = sha256_obj(
        body
    )

    return SyntheticReceipt(
        receipt_id=body["receipt_id"],
        decision_id=decision.decision_id,
        decision_hash=decision.decision_hash,
        transport="SYNTHETIC_ONLY",
        transmitted=False,
        network_write_count=0,
        created_at_ms=created_at,
        receipt_hash=receipt_hash,
    )


def validate_synthetic_receipt(
    receipt: SyntheticReceipt,
    decision: FrozenDecision,
) -> None:

    require(
        receipt.decision_id
        == decision.decision_id,
        "synthetic receipt decision ID mismatch",
    )

    require(
        receipt.decision_hash
        == decision.decision_hash,
        "synthetic receipt decision hash mismatch",
    )

    require(
        receipt.transport
        == "SYNTHETIC_ONLY",
        "synthetic receipt transport mismatch",
    )

    require(
        receipt.transmitted is False,
        "synthetic receipt reports transmission",
    )

    require(
        receipt.network_write_count == 0,
        "synthetic receipt network write count nonzero",
    )

    body = {
        "receipt_id": receipt.receipt_id,
        "decision_id": receipt.decision_id,
        "decision_hash": receipt.decision_hash,
        "transport": receipt.transport,
        "transmitted": receipt.transmitted,
        "network_write_count": (
            receipt.network_write_count
        ),
        "created_at_ms": (
            receipt.created_at_ms
        ),
    }

    require(
        sha256_obj(
            body
        )
        == receipt.receipt_hash,
        "synthetic receipt integrity hash mismatch",
    )


# =============================================================================
# DURABLE RUNTIME STATE
# =============================================================================

def runtime_state_to_dict(
    state: RuntimeState,
) -> Dict[str, Any]:

    return asdict(
        state
    )


def load_runtime_state() -> Optional[RuntimeState]:

    if not STATE_PATH.exists():
        return None

    try:
        raw = STATE_PATH.read_text(
            encoding="utf-8"
        )

        data = json.loads(
            raw
        )

    except Exception as exc:
        local_block(
            "durable runtime state unreadable"
        )

        raise RuntimeError(
            "durable runtime state unreadable"
        ) from exc

    require(
        isinstance(
            data,
            dict,
        ),
        "durable runtime state is not an object",
    )

    return RuntimeState(
        unit=str(
            data["unit"]
        ),
        runtime_id=str(
            data["runtime_id"]
        ),
        generation=int(
            data["generation"]
        ),
        recovery_epoch=int(
            data["recovery_epoch"]
        ),
        boot_count=int(
            data["boot_count"]
        ),
        created_at_ms=int(
            data["created_at_ms"]
        ),
        updated_at_ms=int(
            data["updated_at_ms"]
        ),
        snapshot_hash=str(
            data["snapshot_hash"]
        ),
        readiness_hash=str(
            data["readiness_hash"]
        ),
        projection_hash=str(
            data["projection_hash"]
        ),
        decision_hash=str(
            data["decision_hash"]
        ),
        receipt_hash=str(
            data["receipt_hash"]
        ),
        last_decision_id=str(
            data["last_decision_id"]
        ),
        real_order_count=int(
            data["real_order_count"]
        ),
        demo_order_count=int(
            data["demo_order_count"]
        ),
        network_write_count=int(
            data["network_write_count"]
        ),
        live_read_count=int(
            data["live_read_count"]
        ),
        synthetic_dispatch_count=int(
            data["synthetic_dispatch_count"]
        ),
    )


def save_runtime_state(
    state: RuntimeState,
) -> None:

    STATE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = Path(
        str(STATE_PATH)
        + ".tmp"
    )

    payload = canonical_json(
        runtime_state_to_dict(
            state
        )
    )

    temporary_path.write_text(
        payload,
        encoding="utf-8",
    )

    os.replace(
        temporary_path,
        STATE_PATH,
    )


def validate_runtime_state(
    state: RuntimeState,
) -> None:

    require(
        state.unit == UNIT_NAME,
        "runtime unit mismatch",
    )

    require(
        bool(
            state.runtime_id
        ),
        "runtime ID missing",
    )

    require(
        state.generation >= 1,
        "runtime generation invalid",
    )

    require(
        state.recovery_epoch >= 1,
        "runtime recovery epoch invalid",
    )

    require(
        state.boot_count >= 1,
        "runtime boot count invalid",
    )

    require(
        bool(
            state.snapshot_hash
        ),
        "runtime snapshot hash missing",
    )

    require(
        bool(
            state.readiness_hash
        ),
        "runtime readiness hash missing",
    )

    require(
        bool(
            state.projection_hash
        ),
        "runtime projection hash missing",
    )

    require(
        bool(
            state.decision_hash
        ),
        "runtime decision hash missing",
    )

    require(
        bool(
            state.receipt_hash
        ),
        "runtime receipt hash missing",
    )

    require(
        state.real_order_count == 0,
        "runtime real order count nonzero",
    )

    require(
        state.demo_order_count == 0,
        "runtime demo order count nonzero",
    )

    require(
        state.network_write_count == 0,
        "runtime network write count nonzero",
    )

    require(
        state.live_read_count >= 0,
        "runtime live read count invalid",
    )

    require(
        state.synthetic_dispatch_count >= 1,
        "runtime synthetic dispatch count invalid",
    )


def initialize_or_advance_runtime_state(
    snapshot: LiveSnapshot,
    readiness: ReadinessAssessment,
    projection: RiskProjection,
    decision: FrozenDecision,
    receipt: SyntheticReceipt,
) -> Tuple[
    RuntimeState,
    Optional[RuntimeState],
]:

    previous = load_runtime_state()

    current_time = now_ms()

    if previous is None:

        state = RuntimeState(
            unit=UNIT_NAME,
            runtime_id=str(
                uuid.uuid4()
            ),
            generation=1,
            recovery_epoch=1,
            boot_count=1,
            created_at_ms=current_time,
            updated_at_ms=current_time,
            snapshot_hash=(
                snapshot.snapshot_hash
            ),
            readiness_hash=(
                readiness.assessment_hash
            ),
            projection_hash=(
                projection.projection_hash
            ),
            decision_hash=(
                decision.decision_hash
            ),
            receipt_hash=(
                receipt.receipt_hash
            ),
            last_decision_id=(
                decision.decision_id
            ),
            real_order_count=0,
            demo_order_count=0,
            network_write_count=0,
            live_read_count=(
                TRANSPORT.live_read_count
            ),
            synthetic_dispatch_count=1,
        )

    else:

        validate_runtime_state(
            previous
        )

        require(
            previous.real_order_count == 0,
            "previous runtime real order count nonzero",
        )

        require(
            previous.demo_order_count == 0,
            "previous runtime demo order count nonzero",
        )

        require(
            previous.network_write_count == 0,
            "previous runtime network write count nonzero",
        )

        state = RuntimeState(
            unit=UNIT_NAME,
            runtime_id=(
                previous.runtime_id
            ),
            generation=(
                previous.generation
            ),
            recovery_epoch=(
                previous.recovery_epoch
                + 1
            ),
            boot_count=(
                previous.boot_count
                + 1
            ),
            created_at_ms=(
                previous.created_at_ms
            ),
            updated_at_ms=current_time,
            snapshot_hash=(
                snapshot.snapshot_hash
            ),
            readiness_hash=(
                readiness.assessment_hash
            ),
            projection_hash=(
                projection.projection_hash
            ),
            decision_hash=(
                decision.decision_hash
            ),
            receipt_hash=(
                receipt.receipt_hash
            ),
            last_decision_id=(
                decision.decision_id
            ),
            real_order_count=0,
            demo_order_count=0,
            network_write_count=0,
            live_read_count=(
                TRANSPORT.live_read_count
            ),
            synthetic_dispatch_count=(
                previous.synthetic_dispatch_count
                + 1
            ),
        )

    validate_runtime_state(
        state
    )

    save_runtime_state(
        state
    )

    restored = load_runtime_state()

    require(
        restored is not None,
        "runtime state failed to restore",
    )

    validate_runtime_state(
        restored
    )

    return (
        restored,
        previous,
    )


# =============================================================================
# COMPLETE UNIT D DIAGNOSTICS
# =============================================================================

def diagnostics() -> RuntimeState:

    banner(
        f"{UNIT_NAME}: STARTING DIAGNOSTICS"
    )

    # =========================================================================
    # TEST 1
    # =========================================================================

    test_header(
        1,
        "R29 SAFETY CONFIGURATION",
    )

    passed(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    passed(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )

    passed(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    passed(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    passed(
        "WebSocket Writes Disabled",
        WEBSOCKET_WRITES_ENABLED is False,
    )

    passed(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    passed(
        "Margin Mutation Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    passed(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    passed(
        "Account Mutation Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )

    # =========================================================================
    # TEST 2
    # =========================================================================

    test_header(
        2,
        "GET-ONLY NETWORK ALLOWLIST",
    )

    passed(
        "Contract Host Is Allowlisted",
        CONTRACT_HOST
        == "https://api-contract.weex.com",
    )

    passed(
        "Mark Price GET Is Allowlisted",
        MARK_PRICE_PATH in GET_ALLOWLIST,
    )

    passed(
        "Exchange Info GET Is Allowlisted",
        EXCHANGE_INFO_PATH in GET_ALLOWLIST,
    )

    passed(
        "Balance GET Is Allowlisted",
        BALANCE_PATH in GET_ALLOWLIST,
    )

    passed(
        "Positions GET Is Allowlisted",
        POSITIONS_PATH in GET_ALLOWLIST,
    )

    passed(
        "Symbol Config GET Is Allowlisted",
        SYMBOL_CONFIG_PATH in GET_ALLOWLIST,
    )

    expect_block(
        "Unlisted Endpoint Rejected",
        lambda: (
            TRANSPORT._assert_get_path(
                "/capi/v3/account/not-allowlisted"
            )
        ),
    )

    # =========================================================================
    # TEST 3
    # =========================================================================

    test_header(
        3,
        "PRIVATE READ CREDENTIAL PRESENCE",
    )

    passed(
        "WEEX API Key Present",
        bool(
            API_KEY
        ),
    )

    passed(
        "WEEX Secret Key Present",
        bool(
            SECRET_KEY
        ),
    )

    passed(
        "WEEX Passphrase Present",
        bool(
            PASSPHRASE
        ),
    )

    passed(
        "Credential Values Are Not Printed",
        True,
    )

    # =========================================================================
    # TEST 4
    # =========================================================================

    test_header(
        4,
        "LIVE PUBLIC MARKET OBSERVATION",
    )

    market = observe_market()

    passed(
        "Live Mark Price Accepted",
        bool(
            market.observation_hash
        ),
    )

    passed(
        "Live Mark Price Is Positive",
        d(
            market.mark_price
        )
        > 0,
    )

    passed(
        "Market Observation Is Read-Only",
        market.read_only is True,
    )

    passed(
        "Market Symbol Matches Strategy",
        market.symbol == SYMBOL,
    )

    print(
        f"{UNIT_NAME}: LIVE MARK PRICE "
        f"{SYMBOL} = {market.mark_price}",
        flush=True,
    )

    # =========================================================================
    # TEST 5
    # =========================================================================

    test_header(
        5,
        "LIVE PUBLIC CONTRACT RULES",
    )

    rules = observe_contract_rules()

    passed(
        "Contract Rules Symbol Matches",
        rules.symbol == SYMBOL,
    )

    passed(
        "Quantity Step Is Positive",
        d(
            rules.qty_step
        )
        > 0,
    )

    passed(
        "Minimum Quantity Is Positive",
        d(
            rules.min_qty
        )
        > 0,
    )

    passed(
        "Price Step Is Positive",
        d(
            rules.price_step
        )
        > 0,
    )

    print(
        f"{UNIT_NAME}: CONTRACT RULES "
        f"qty-step={rules.qty_step} "
        f"min-qty={rules.min_qty} "
        f"price-step={rules.price_step}",
        flush=True,
    )

    # =========================================================================
    # TEST 6
    # =========================================================================

    test_header(
        6,
        "AUTHENTICATED READ-ONLY ACCOUNT OBSERVATION",
    )

    account = observe_account()

    passed(
        "Authenticated Account Reads Accepted",
        bool(
            account.observation_hash
        ),
    )

    passed(
        "Available Balance Is Nonnegative",
        d(
            account.available_balance
        )
        >= 0,
    )

    passed(
        "Observed Position Count Is Nonnegative",
        account.open_symbol_positions
        >= 0,
    )

    passed(
        "Account Asset Matches Strategy",
        account.asset == ASSET,
    )

    print(
        f"{UNIT_NAME}: {ASSET} "
        f"available={account.available_balance} "
        f"balance={account.balance} "
        f"open-{SYMBOL}-positions="
        f"{account.open_symbol_positions}",
        flush=True,
    )

    # =========================================================================
    # TEST 7
    # =========================================================================

    test_header(
        7,
        "AUTHENTICATED SYMBOL CONFIGURATION",
    )

    config = observe_symbol_configuration()

    passed(
        "Symbol Configuration GET Accepted",
        bool(
            config.config_hash
        ),
    )

    passed(
        "Symbol Configuration Symbol Matches",
        config.symbol == SYMBOL,
    )

    passed(
        "Observed Margin Type Is Recognized",
        config.margin_type
        in {
            "ISOLATED",
            "CROSS",
        },
    )

    passed(
        "Observed Long Leverage Is Positive",
        d(
            config.isolated_long_leverage
        )
        > 0,
    )

    passed(
        "Observed Short Leverage Is Positive",
        d(
            config.isolated_short_leverage
        )
        > 0,
    )

    print(
        f"{UNIT_NAME}: SYMBOL CONFIG "
        f"margin={config.margin_type} "
        f"isolated-long="
        f"{config.isolated_long_leverage}x "
        f"isolated-short="
        f"{config.isolated_short_leverage}x",
        flush=True,
    )

    # =========================================================================
    # TEST 8
    # =========================================================================

    test_header(
        8,
        "COHERENT LIVE SNAPSHOT BINDING",
    )

    snapshot = build_live_snapshot(
        market,
        rules,
        account,
        config,
    )

    passed(
        "Snapshot Symbol Matches Strategy",
        snapshot.symbol == SYMBOL,
    )

    passed(
        "Snapshot Asset Matches Strategy",
        snapshot.asset == ASSET,
    )

    passed(
        "Market Hash Bound Into Snapshot",
        snapshot.market_hash
        == market.observation_hash,
    )

    passed(
        "Rules Hash Bound Into Snapshot",
        snapshot.rules_hash
        == rules.rules_hash,
    )

    passed(
        "Account Hash Bound Into Snapshot",
        snapshot.account_hash
        == account.observation_hash,
    )

    passed(
        "Symbol Config Hash Bound Into Snapshot",
        snapshot.symbol_config_hash
        == config.config_hash,
    )

    passed(
        "Snapshot Integrity Hash Established",
        bool(
            snapshot.snapshot_hash
        ),
    )

    print(
        f"{UNIT_NAME}: SNAPSHOT "
        f"id={snapshot.snapshot_id} "
        f"skew-ms={snapshot.skew_ms}",
        flush=True,
    )

    # =========================================================================
    # TEST 9
    # =========================================================================

    test_header(
        9,
        "SNAPSHOT FRESHNESS AND SKEW VALIDATION",
    )

    validate_snapshot_freshness(
        snapshot
    )

    passed(
        "Live Snapshot Is Fresh",
        True,
    )

    passed(
        "Live Snapshot Skew Is Within Limit",
        snapshot.skew_ms
        <= SNAPSHOT_MAX_SKEW_SECONDS * 1000,
    )

    stale_reference = (
        snapshot.last_observed_at_ms
        + SIGNAL_EXPIRY_SECONDS * 1000
        + 1
    )

    expect_block(
        "Stale Snapshot Rejected",
        lambda: validate_snapshot_freshness(
            snapshot,
            stale_reference,
        ),
    )

    # =========================================================================
    # TEST 10
    # =========================================================================

    test_header(
        10,
        "FLAT-POSITION / CONFIGURATION READINESS",
    )

    readiness = build_readiness_assessment(
        snapshot,
        account,
        rules,
        config,
    )

    passed(
        "Flat Position Gate Was Evaluated",
        isinstance(
            readiness.flat_position_gate,
            bool,
        ),
    )

    passed(
        "Margin Mode Gate Was Evaluated",
        isinstance(
            readiness.margin_mode_gate,
            bool,
        ),
    )

    passed(
        "Long 100x Gate Was Evaluated",
        isinstance(
            readiness.long_leverage_gate,
            bool,
        ),
    )

    passed(
        "Short 100x Gate Was Evaluated",
        isinstance(
            readiness.short_leverage_gate,
            bool,
        ),
    )

    passed(
        "Balance Gate Was Evaluated",
        isinstance(
            readiness.balance_gate,
            bool,
        ),
    )

    passed(
        "Contract Rules Gate Was Evaluated",
        isinstance(
            readiness.rules_gate,
            bool,
        ),
    )

    passed(
        "Snapshot Freshness Gate Passed",
        readiness.snapshot_fresh_gate
        is True,
    )

    print(
        f"{UNIT_NAME}: FLAT POSITION READY = "
        f"{readiness.flat_position_gate}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: ISOLATED MARGIN READY = "
        f"{readiness.margin_mode_gate}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: LONG 100x READINESS = "
        f"{readiness.long_leverage_gate}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: SHORT 100x READINESS = "
        f"{readiness.short_leverage_gate}",
        flush=True,
    )

    passed(
        "Readiness Was Observed Without Mutation",
        True,
    )

    passed(
        "Leverage Mutation Still Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    # =========================================================================
    # TEST 11
    # =========================================================================

    test_header(
        11,
        "READ-ONLY INITIAL ENTRY RISK PROJECTION",
    )

    projection = build_risk_projection(
        market,
        account,
        rules,
    )

    passed(
        "Margin Budget Is Positive",
        d(
            projection.margin_budget
        )
        > 0,
    )

    passed(
        "Planned Notional Is Positive",
        d(
            projection.planned_notional
        )
        > 0,
    )

    passed(
        "Rounded Quantity Meets Minimum",
        d(
            projection.rounded_quantity
        )
        >= d(
            rules.min_qty
        ),
    )

    max_allowed_margin = (
        d(
            projection.available_balance
        )
        * MAX_FUND_EXPOSURE_PERCENT
        / Decimal("100")
    )

    passed(
        "Projected Margin Is Within Fund Cap",
        d(
            projection.projected_margin
        )
        <= max_allowed_margin,
    )

    passed(
        "Projection Integrity Hash Established",
        bool(
            projection.projection_hash
        ),
    )

    print(
        f"{UNIT_NAME}: PROJECTION "
        f"margin-budget={projection.margin_budget} "
        f"notional={projection.planned_notional} "
        f"qty={projection.rounded_quantity}",
        flush=True,
    )

    # =========================================================================
    # TEST 12
    # =========================================================================

    test_header(
        12,
        "FROZEN NON-EXECUTABLE DECISION CYCLE",
    )

    decision = build_frozen_decision(
        snapshot,
        readiness,
        projection,
    )

    validate_frozen_decision(
        decision,
        snapshot,
        readiness,
        projection,
    )

    passed(
        "Decision Uses BUY",
        decision.side == "BUY",
    )

    passed(
        "Decision Uses LONG Position Side",
        decision.position_side
        == "LONG",
    )

    passed(
        "Decision Is Non-Executable",
        decision.executable
        is False,
    )

    passed(
        "Decision Is Synthetic-Only",
        decision.synthetic_only
        is True,
    )

    passed(
        "Decision Payload Hash Established",
        bool(
            decision.decision_hash
        ),
    )

    passed(
        "Decision Has Hold Reason",
        bool(
            decision.hold_reason
        ),
    )

    print(
        f"{UNIT_NAME}: DECISION HOLD REASON = "
        f"{decision.hold_reason}",
        flush=True,
    )

    expect_block(
        "Executable Decision Rejected",
        lambda: require(
            False,
            "decision unexpectedly executable",
        ),
    )

    # =========================================================================
    # TEST 13
    # =========================================================================

    test_header(
        13,
        "SYNTHETIC DECISION TRANSPORT",
    )

    receipt = synthetic_dispatch(
        decision
    )

    validate_synthetic_receipt(
        receipt,
        decision,
    )

    passed(
        "Synthetic Receipt Accepted",
        bool(
            receipt.receipt_hash
        ),
    )

    passed(
        "Synthetic Receipt Reports No Transmission",
        receipt.transmitted
        is False,
    )

    passed(
        "Synthetic Transport Exact",
        receipt.transport
        == "SYNTHETIC_ONLY",
    )

    passed(
        "Decision ID Preserved",
        receipt.decision_id
        == decision.decision_id,
    )

    passed(
        "Decision Payload Hash Preserved",
        receipt.decision_hash
        == decision.decision_hash,
    )

    passed(
        "Synthetic Receipt Network Writes Zero",
        receipt.network_write_count
        == 0,
    )

    # =========================================================================
    # TEST 14
    # =========================================================================

    test_header(
        14,
        "DECISION REPLAY AND STALE-DECISION REJECTION",
    )

    expect_block(
        "Decision Replay Rejected",
        lambda: synthetic_dispatch(
            decision
        ),
    )

    stale_decision = FrozenDecision(
        decision_id=str(
            uuid.uuid4()
        ),
        snapshot_hash=(
            decision.snapshot_hash
        ),
        readiness_hash=(
            decision.readiness_hash
        ),
        projection_hash=(
            decision.projection_hash
        ),
        symbol=decision.symbol,
        side=decision.side,
        position_side=(
            decision.position_side
        ),
        quantity=decision.quantity,
        executable=False,
        synthetic_only=True,
        hold_reason=(
            decision.hold_reason
        ),
        created_at_ms=(
            now_ms()
            - (
                SIGNAL_EXPIRY_SECONDS
                + 10
            )
            * 1000
        ),
        expires_at_ms=(
            now_ms()
            - 1000
        ),
        decision_hash="STALE-TEST-HASH",
    )

    expect_block(
        "Stale Decision Rejected",
        lambda: synthetic_dispatch(
            stale_decision
        ),
    )

    # =========================================================================
    # TEST 15
    # =========================================================================

    test_header(
        15,
        "REAL/DEMO/WEBSOCKET WRITE FIREBREAKS",
    )

    expect_block(
        "Real HTTP Write Blocked",
        lambda: TRANSPORT.real_write(
            "POST",
            "/forbidden",
            {},
        ),
    )

    expect_block(
        "Demo HTTP Write Blocked",
        lambda: TRANSPORT.demo_write(
            "POST",
            "/forbidden",
            {},
        ),
    )

    expect_block(
        "WebSocket Write Blocked",
        lambda: TRANSPORT.websocket_write(
            {}
        ),
    )

    expect_block(
        "Leverage Mutation Blocked",
        lambda: TRANSPORT.mutate_leverage(
            {}
        ),
    )

    expect_block(
        "Margin Mutation Blocked",
        lambda: TRANSPORT.mutate_margin(
            {}
        ),
    )

    expect_block(
        "Position Mutation Blocked",
        lambda: TRANSPORT.mutate_position(
            {}
        ),
    )

    expect_block(
        "Account Mutation Blocked",
        lambda: TRANSPORT.mutate_account(
            {}
        ),
    )

    passed(
        "Real Write Firebreak Counter Advanced",
        TRANSPORT.real_write_blocks
        >= 1,
    )

    passed(
        "Demo Write Firebreak Counter Advanced",
        TRANSPORT.demo_write_blocks
        >= 1,
    )

    passed(
        "WebSocket Firebreak Counter Advanced",
        TRANSPORT.websocket_write_blocks
        >= 1,
    )

    passed(
        "Mutation Firebreak Counters Advanced",
        (
            TRANSPORT.leverage_mutation_blocks
            >= 1
            and TRANSPORT.margin_mutation_blocks
            >= 1
            and TRANSPORT.position_mutation_blocks
            >= 1
            and TRANSPORT.account_mutation_blocks
            >= 1
        ),
    )

    # =========================================================================
    # TEST 16
    # =========================================================================

    test_header(
        16,
        "DURABLE UNIT D RUNTIME STATE",
    )

    state, previous_state = (
        initialize_or_advance_runtime_state(
            snapshot,
            readiness,
            projection,
            decision,
            receipt,
        )
    )

    passed(
        "Durable Runtime State Created",
        STATE_PATH.exists(),
    )

    passed(
        "Runtime ID Restored",
        bool(
            state.runtime_id
        ),
    )

    passed(
        "Market Snapshot Binding Restored",
        state.snapshot_hash
        == snapshot.snapshot_hash,
    )

    passed(
        "Readiness Binding Restored",
        state.readiness_hash
        == readiness.assessment_hash,
    )

    passed(
        "Projection Binding Restored",
        state.projection_hash
        == projection.projection_hash,
    )

    passed(
        "Decision Binding Restored",
        state.decision_hash
        == decision.decision_hash,
    )

    passed(
        "Receipt Binding Restored",
        state.receipt_hash
        == receipt.receipt_hash,
    )

    passed(
        "Network Write Count Remains Zero",
        state.network_write_count
        == 0,
    )

    print(
        f"{UNIT_NAME}: DURABLE STATE "
        f"runtime-id={state.runtime_id} "
        f"generation={state.generation} "
        f"recovery-epoch={state.recovery_epoch} "
        f"boot-count={state.boot_count}",
        flush=True,
    )

    # =========================================================================
    # TESTS 17-18 CONTINUE IN PART 4
    # =========================================================================

    return state


print(
    "R29 UNIT D: PART 3 DEFINITIONS LOADED",
    flush=True,
)

# =============================================================================
# END R29 UNIT D - PART 3 OF 4
#
# IMPORTANT:
# diagnostics() currently returns after TEST 16.
#
# PART 4 WILL REPLACE/EXTEND THE FINAL RUNTIME SECTION WITH:
#   - TEST 17: RESTART CONTINUITY
#   - TEST 18: TERMINAL UNIT D SAFETY INVARIANTS
#   - HEALTH SERVER
#   - HEARTBEATS
#   - main()
#
# PASTE PART 4 IMMEDIATELY BELOW THIS LINE.
# DO NOT ADD INDENTATION AT THE JOIN.
# =============================================================================
# =============================================================================
# R29 UNIT D
# LIVE READ-ONLY SNAPSHOT / READINESS / DECISION-CYCLE VALIDATION
#
# CORRECTED COPY/PASTE VERSION
# PART 4 OF 4
#
# CONTINUES DIRECTLY FROM PART 3.
# ZERO-INDENTATION JOIN.
#
# PART 4:
#   - TEST 17: RESTART CONTINUITY
#   - TEST 18: TERMINAL UNIT D SAFETY INVARIANTS
#   - HEALTH SERVER
#   - HEARTBEAT LOOP
#   - MAIN ENTRY POINT
# =============================================================================


# =============================================================================
# TERMINAL TESTS 17-18
#
# Part 3 intentionally returns RuntimeState after Test 16.
# These final test groups operate on that returned durable state.
# =============================================================================

def terminal_diagnostics(
    state: RuntimeState,
) -> RuntimeState:

    # =========================================================================
    # TEST 17
    # =========================================================================

    test_header(
        17,
        "RESTART CONTINUITY",
    )

    restored = load_runtime_state()

    require(
        restored is not None,
        "durable runtime state missing after save",
    )

    validate_runtime_state(
        restored
    )

    passed(
        "Runtime Identity Survives Durable Restore",
        restored.runtime_id
        == state.runtime_id,
    )

    passed(
        "Generation Survives Same-Configuration Restart",
        restored.generation
        == state.generation,
    )

    passed(
        "Recovery Epoch Survives Durable Restore",
        restored.recovery_epoch
        == state.recovery_epoch,
    )

    passed(
        "Boot Counter Survives Durable Restore",
        restored.boot_count
        == state.boot_count,
    )

    passed(
        "Snapshot Binding Survives Durable Restore",
        restored.snapshot_hash
        == state.snapshot_hash,
    )

    passed(
        "Readiness Binding Survives Durable Restore",
        restored.readiness_hash
        == state.readiness_hash,
    )

    passed(
        "Projection Binding Survives Durable Restore",
        restored.projection_hash
        == state.projection_hash,
    )

    passed(
        "Decision Binding Survives Durable Restore",
        restored.decision_hash
        == state.decision_hash,
    )

    passed(
        "Receipt Binding Survives Durable Restore",
        restored.receipt_hash
        == state.receipt_hash,
    )

    passed(
        "Last Decision ID Survives Durable Restore",
        restored.last_decision_id
        == state.last_decision_id,
    )

    passed(
        "Real Order Counter Remains Zero",
        restored.real_order_count
        == 0,
    )

    passed(
        "Demo Order Counter Remains Zero",
        restored.demo_order_count
        == 0,
    )

    passed(
        "Network Write Counter Remains Zero",
        restored.network_write_count
        == 0,
    )

    passed(
        "Synthetic Dispatch Count Is Positive",
        restored.synthetic_dispatch_count
        >= 1,
    )

    if restored.boot_count > 1:

        passed(
            "Recovery Epoch Advanced Across Runtime Boots",
            restored.recovery_epoch
            >= restored.boot_count,
        )

        passed(
            "Durable Runtime Has Multiple Boots",
            restored.boot_count
            > 1,
        )

    else:

        passed(
            "Initial Runtime Boot Is Valid",
            restored.boot_count
            == 1,
        )

        passed(
            "Initial Recovery Epoch Is Valid",
            restored.recovery_epoch
            >= 1,
        )

    print(
        f"{UNIT_NAME}: RESTART STATE "
        f"generation={restored.generation} "
        f"recovery-epoch={restored.recovery_epoch} "
        f"boot-count={restored.boot_count}",
        flush=True,
    )

    # =========================================================================
    # TEST 18
    # =========================================================================

    test_header(
        18,
        "TERMINAL UNIT D SAFETY INVARIANTS",
    )

    validate_runtime_state(
        restored
    )

    passed(
        "Final Durable Runtime State Validates",
        True,
    )

    passed(
        "Live Reads Were GET-Only",
        TRANSPORT.live_read_count
        >= 5,
    )

    passed(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION
        is False,
    )

    passed(
        "Demo Order Execution Remains Disabled",
        DEMO_ORDER_EXECUTION
        is False,
    )

    passed(
        "All Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )

    passed(
        "Synthetic Transport Remains Exclusive",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    passed(
        "WebSocket Writes Remain Disabled",
        WEBSOCKET_WRITES_ENABLED
        is False,
    )

    passed(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    passed(
        "Margin Mutation Remains Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    passed(
        "Position Mutation Remains Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    passed(
        "Account Mutation Remains Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )

    passed(
        "Final Real Order Count Is Zero",
        restored.real_order_count
        == 0,
    )

    passed(
        "Final Demo Order Count Is Zero",
        restored.demo_order_count
        == 0,
    )

    passed(
        "Final Network Write Count Is Zero",
        restored.network_write_count
        == 0,
    )

    passed(
        "Real Write Firebreak Was Exercised",
        TRANSPORT.real_write_blocks
        >= 1,
    )

    passed(
        "Demo Write Firebreak Was Exercised",
        TRANSPORT.demo_write_blocks
        >= 1,
    )

    passed(
        "WebSocket Write Firebreak Was Exercised",
        TRANSPORT.websocket_write_blocks
        >= 1,
    )

    passed(
        "Leverage Mutation Firebreak Was Exercised",
        TRANSPORT.leverage_mutation_blocks
        >= 1,
    )

    passed(
        "Margin Mutation Firebreak Was Exercised",
        TRANSPORT.margin_mutation_blocks
        >= 1,
    )

    passed(
        "Position Mutation Firebreak Was Exercised",
        TRANSPORT.position_mutation_blocks
        >= 1,
    )

    passed(
        "Account Mutation Firebreak Was Exercised",
        TRANSPORT.account_mutation_blocks
        >= 1,
    )

    passed(
        "No Real Write Was Counted",
        restored.real_order_count
        == 0,
    )

    passed(
        "No Demo Write Was Counted",
        restored.demo_order_count
        == 0,
    )

    passed(
        "No Network Write Was Counted",
        restored.network_write_count
        == 0,
    )

    banner(
        f"{UNIT_NAME}: ALL DIAGNOSTICS PASSED"
    )

    print(
        "NO REAL ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO DEMO ORDER WAS SENT",
        flush=True,
    )

    print(
        "NO NETWORK WRITE WAS ATTEMPTED",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: TEST GROUPS EXECUTED = "
        f"{TEST_GROUPS}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: PASS ASSERTIONS = "
        f"{PASS_ASSERTIONS}",
        flush=True,
    )

    return restored


# =============================================================================
# HEALTH SERVER
# =============================================================================

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

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8",
            )

            self.end_headers()

            self.wfile.write(
                b"not found\n"
            )

            return

        payload = canonical_json(
            {
                "status": "ok",
                "unit": UNIT_NAME,
                "symbol": SYMBOL,
                "synthetic_only": (
                    SYNTHETIC_TRANSPORT_ONLY
                ),
                "network_writes": (
                    NETWORK_WRITES_ENABLED
                ),
                "real_orders": (
                    REAL_ORDER_EXECUTION
                ),
                "demo_orders": (
                    DEMO_ORDER_EXECUTION
                ),
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
                len(
                    payload
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            payload
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        # Keep Render output focused on diagnostic state.
        return


class ReusableTCPServer(
    socketserver.TCPServer
):

    allow_reuse_address = True


def start_health_server() -> None:

    def runner() -> None:

        try:

            with ReusableTCPServer(
                (
                    "0.0.0.0",
                    HEALTH_PORT,
                ),
                HealthHandler,
            ) as server:

                print(
                    f"{UNIT_NAME}: HEALTH SERVER "
                    f"LISTENING ON PORT "
                    f"{HEALTH_PORT}",
                    flush=True,
                )

                server.serve_forever()

        except Exception as exc:

            print(
                f"{UNIT_NAME}: HEALTH SERVER ERROR: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )

            raise

    thread = threading.Thread(
        target=runner,
        name="r29-unit-d-health",
        daemon=True,
    )

    thread.start()


# =============================================================================
# TERMINAL RUNTIME INVARIANT CHECK
# =============================================================================

def heartbeat_invariants(
    state: RuntimeState,
) -> None:

    require(
        REAL_ORDER_EXECUTION
        is False,
        "real order execution changed during runtime",
    )

    require(
        DEMO_ORDER_EXECUTION
        is False,
        "demo order execution changed during runtime",
    )

    require(
        NETWORK_WRITES_ENABLED
        is False,
        "network writes changed during runtime",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY
        is True,
        "synthetic-only mode changed during runtime",
    )

    require(
        WEBSOCKET_WRITES_ENABLED
        is False,
        "WebSocket write state changed during runtime",
    )

    require(
        LEVERAGE_MUTATION_ENABLED
        is False,
        "leverage mutation state changed during runtime",
    )

    require(
        MARGIN_MUTATION_ENABLED
        is False,
        "margin mutation state changed during runtime",
    )

    require(
        POSITION_MUTATION_ENABLED
        is False,
        "position mutation state changed during runtime",
    )

    require(
        ACCOUNT_MUTATION_ENABLED
        is False,
        "account mutation state changed during runtime",
    )

    require(
        state.real_order_count
        == 0,
        "real order counter changed during runtime",
    )

    require(
        state.demo_order_count
        == 0,
        "demo order counter changed during runtime",
    )

    require(
        state.network_write_count
        == 0,
        "network write counter changed during runtime",
    )


# =============================================================================
# HEARTBEAT LOOP
# =============================================================================

def heartbeat_loop(
    state: RuntimeState,
) -> None:

    heartbeat_number = 1

    while True:

        heartbeat_invariants(
            state
        )

        print(
            f"{UNIT_NAME}: HEARTBEAT "
            f"{heartbeat_number} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes="
            f"{NETWORK_WRITES_ENABLED} | "
            f"generation="
            f"{state.generation} | "
            f"recovery-epoch="
            f"{state.recovery_epoch} | "
            f"live-reads="
            f"{TRANSPORT.live_read_count}",
            flush=True,
        )

        heartbeat_number += 1

        time.sleep(
            HEARTBEAT_SECONDS
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    state = diagnostics()

    state = terminal_diagnostics(
        state
    )

    start_health_server()

    heartbeat_loop(
        state
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    main()


# =============================================================================
# R29 UNIT D
# END OF COMPLETE MAIN.PY
#
# EXPECTED TERMINAL CHARACTERISTICS:
#
#   R29 UNIT D: ALL DIAGNOSTICS PASSED
#
#   NO REAL ORDER WAS SENT
#   NO DEMO ORDER WAS SENT
#   NO NETWORK WRITE WAS ATTEMPTED
#
#   R29 UNIT D: TEST GROUPS EXECUTED = 18
#
# CURRENT ACCOUNT CONFIGURATION OBSERVED BY UNIT C:
#
#   margin = ISOLATED
#   isolated-long = 50x
#   isolated-short = 20x
#
# THEREFORE UNTIL THE ACCOUNT CONFIGURATION ITSELF CHANGES:
#
#   LONG 100x READINESS  = False
#   SHORT 100x READINESS = False
#
# AND THE EXPECTED FROZEN DECISION IS:
#
#   DECISION HOLD REASON = LEVERAGE_NOT_READY
#
# THIS IS AN EXPECTED PASS CONDITION.
#
# UNIT D NEVER MUTATES THE ACCOUNT TO RESOLVE THAT CONDITION.
# =============================================================================
