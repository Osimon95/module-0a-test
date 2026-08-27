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
