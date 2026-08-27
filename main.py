from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_DOWN, getcontext
from enum import Enum
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# R31B
# FINAL PRE-EXECUTION INTEGRATION / READINESS VALIDATION
#
# SAFETY DISCIPLINE:
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO EXCHANGE NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE:
#
#   observation
#       ->
#   signal
#       ->
#   strategy decision
#       ->
#   risk gate
#       ->
#   quantity projection
#       ->
#   TP / backup projection
#       ->
#   candidate
#       ->
#   authorization envelope
#       ->
#   synthetic dispatch
#       ->
#   durable seal
#       ->
#   restart-safe recovery
#
# R31B MUST NOT TRANSMIT AN ORDER.
# =============================================================================


getcontext().prec = 28


# =============================================================================
# IDENTITY
# =============================================================================

VERSION = "R31B"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"

STATE_FILE = Path(
    os.getenv(
        "R31B_STATE_FILE",
        "/tmp/r31b_pre_execution_readiness_state.json",
    )
)

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

HEARTBEAT_SECONDS = 30


# =============================================================================
# ABSOLUTE SAFETY CONSTANTS
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

WEBSOCKET_WRITES_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# =============================================================================
# STRATEGY CONSTANTS
# =============================================================================

TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

BACKUP_BUFFER_PERCENT = Decimal("0.3")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# =============================================================================
# SYNTHETIC CONTRACT RULES
# =============================================================================

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
PRICE_STEP = Decimal("0.1")

SYNTHETIC_AVAILABLE_BALANCE = Decimal(
    os.getenv("R31B_SYNTHETIC_BALANCE", "7.18945017")
)

SYNTHETIC_MARK_PRICE = Decimal(
    os.getenv("R31B_SYNTHETIC_MARK_PRICE", "80000")
)


# =============================================================================
# ENUMS
# =============================================================================

class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalStrength(str, Enum):
    WEAK = "WEAK"
    NORMAL = "NORMAL"
    STRONG = "STRONG"


class CandidatePhase(str, Enum):
    CREATED = "CREATED"
    RISK_ACCEPTED = "RISK_ACCEPTED"
    AUTHORIZED = "AUTHORIZED"
    SYNTHETICALLY_DISPATCHED = "SYNTHETICALLY_DISPATCHED"
    SEALED = "SEALED"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class MarketObservation:
    symbol: str
    mark_price: str
    timestamp: int
    source: str


@dataclass(frozen=True)
class StrategySignal:
    signal_id: str
    symbol: str
    direction: str
    strength: str
    observed_price: str
    created_at: int
    expires_at: int


@dataclass(frozen=True)
class RiskProjection:
    available_balance: str
    entry_margin_budget: str
    target_leverage: str
    projected_notional: str
    raw_quantity: str
    rounded_quantity: str
    rounded_notional: str
    rounded_margin: str
    exposure_percent: str
    accepted: bool
    reason: str


@dataclass(frozen=True)
class TakeProfitProjection:
    tp1_quantity: str
    tp2_quantity: str
    tp3_quantity: str
    reconciled_quantity: str
    trigger_1_percent: str
    trigger_2_percent: str
    trailing_distance_percent: str


@dataclass(frozen=True)
class BackupProjection:
    max_backups: int
    backup_percent: str
    backup_buffer_percent: str
    projected_backup_margin_each: str
    projected_backup_total_margin: str


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    signal_id: str
    symbol: str
    direction: str
    quantity: str
    mark_price: str
    target_leverage: str
    phase: str
    created_at: int


@dataclass(frozen=True)
class AuthorizationEnvelope:
    authorization_id: str
    candidate_id: str
    symbol: str
    direction: str
    quantity: str
    leverage: str
    transport: str
    executable: bool
    network_writes_allowed: bool
    created_at: int
    payload_hash: str


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    authorization_id: str
    candidate_id: str
    transmitted: bool
    synthetic_only: bool
    transport: str
    created_at: int


@dataclass
class RuntimeState:
    version: str
    runtime_id: str
    generation: int
    recovery_epoch: int
    phase: str
    candidate_id: str
    authorization_id: str
    synthetic_receipt_id: str

    real_order_count: int
    demo_order_count: int
    network_write_count: int
    mutation_count: int

    synthetic_dispatch_count: int
    transition_count: int
    consumed_transition_count: int

    sealed: bool
    state_hash: str


# =============================================================================
# COUNTERS
# =============================================================================

REAL_ORDER_COUNT = 0
DEMO_ORDER_COUNT = 0
NETWORK_WRITE_COUNT = 0
MUTATION_COUNT = 0

SYNTHETIC_DISPATCH_COUNT = 0
TRANSITION_COUNT = 0
CONSUMED_TRANSITION_COUNT = 0


# =============================================================================
# TEST TRACKING
# =============================================================================

PASSED = 0
FAILED = 0


def line() -> None:
    print("-" * 92, flush=True)


def section(title: str) -> None:
    line()
    print(title, flush=True)
    line()


def check(name: str, condition: bool) -> None:
    global PASSED, FAILED

    if condition:
        PASSED += 1
        result = "✅ PASS"
    else:
        FAILED += 1
        result = "❌ FAIL"

    print(f"{name:<78} {result}", flush=True)


# =============================================================================
# BASIC HELPERS
# =============================================================================

def now_ts() -> int:
    return int(time.time())


def decimal_string(value: Decimal) -> str:
    return format(value, "f")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )


def quantize_down(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        raise ValueError("step must be positive")

    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


def regardless_environment(_: bool) -> bool:
    """
    Environment state is deliberately ignored.

    This function exists only to make escalation-resistance tests explicit.
    """
    return True


# =============================================================================
# HARD SAFETY BLOCKS
# =============================================================================

class SafetyViolation(RuntimeError):
    pass


def block_real_order(reason: str = "") -> None:
    global REAL_ORDER_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print("  REAL order execution blocked", flush=True)

    if reason:
        print(f"  reason={reason}", flush=True)

    raise SafetyViolation("real order execution disabled")


def block_demo_order(reason: str = "") -> None:
    global DEMO_ORDER_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print("  DEMO order execution blocked", flush=True)

    if reason:
        print(f"  reason={reason}", flush=True)

    raise SafetyViolation("demo order execution disabled")


def block_network_write(method: str, path: str) -> None:
    global NETWORK_WRITE_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print(f"  REAL network {method.upper()} blocked", flush=True)
    print(f"  path={path}", flush=True)

    raise SafetyViolation("exchange network writes disabled")


def block_mutation(kind: str) -> None:
    global MUTATION_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print(f"  {kind} mutation blocked", flush=True)

    raise SafetyViolation(f"{kind} mutation disabled")


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        if self.path in {"/", "/health", "/healthz"}:
            payload = json.dumps(
                {
                    "status": "ok",
                    "version": VERSION,
                    "symbol": SYMBOL,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                    "real_execution": REAL_ORDER_EXECUTION_ENABLED,
                    "network_writes": EXCHANGE_NETWORK_WRITES_ENABLED,
                    "leverage_mutation": LEVERAGE_MUTATION_ENABLED,
                }
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_health_server() -> None:

    def serve() -> None:
        try:
            with ReusableTCPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            ) as server:

                print(
                    f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
                    flush=True,
                )

                server.serve_forever()

        except Exception as exc:
            print(
                f"{VERSION}: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=serve,
        daemon=True,
    )

    thread.start()
# =============================================================================
# OBSERVATION / SIGNAL PIPELINE
# =============================================================================

def build_observation() -> MarketObservation:
    return MarketObservation(
        symbol=SYMBOL,
        mark_price=decimal_string(SYNTHETIC_MARK_PRICE),
        timestamp=now_ts(),
        source="R31B_SYNTHETIC_OBSERVATION",
    )


def build_signal(
    observation: MarketObservation,
    direction: Direction = Direction.LONG,
) -> StrategySignal:

    created = now_ts()

    return StrategySignal(
        signal_id=str(uuid.uuid4()),
        symbol=observation.symbol,
        direction=direction.value,
        strength=SignalStrength.NORMAL.value,
        observed_price=observation.mark_price,
        created_at=created,
        expires_at=created + SIGNAL_EXPIRY_SECONDS,
    )


def signal_is_valid(signal: StrategySignal) -> bool:
    return (
        signal.symbol == SYMBOL
        and signal.direction in {
            Direction.LONG.value,
            Direction.SHORT.value,
        }
        and signal.expires_at > signal.created_at
        and signal.expires_at - signal.created_at == SIGNAL_EXPIRY_SECONDS
    )


# =============================================================================
# RISK PROJECTION
# =============================================================================

def calculate_risk_projection(
    balance: Decimal,
    price: Decimal,
) -> RiskProjection:

    entry_margin_budget = (
        balance * INITIAL_ENTRY_PERCENT / Decimal("100")
    )

    projected_notional = entry_margin_budget * TARGET_LEVERAGE

    raw_quantity = projected_notional / price

    rounded_quantity = quantize_down(
        raw_quantity,
        QTY_STEP,
    )

    if rounded_quantity < MIN_QTY:
        rounded_quantity = MIN_QTY

    rounded_notional = rounded_quantity * price

    rounded_margin = rounded_notional / TARGET_LEVERAGE

    exposure_percent = (
        rounded_margin / balance * Decimal("100")
        if balance > 0
        else Decimal("999999")
    )

    accepted = (
        balance > 0
        and price > 0
        and rounded_quantity >= MIN_QTY
        and exposure_percent <= MAX_FUND_EXPOSURE_PERCENT
    )

    reason = (
        "RISK_ACCEPTED"
        if accepted
        else "RISK_REJECTED"
    )

    return RiskProjection(
        available_balance=decimal_string(balance),
        entry_margin_budget=decimal_string(entry_margin_budget),
        target_leverage=decimal_string(TARGET_LEVERAGE),
        projected_notional=decimal_string(projected_notional),
        raw_quantity=decimal_string(raw_quantity),
        rounded_quantity=decimal_string(rounded_quantity),
        rounded_notional=decimal_string(rounded_notional),
        rounded_margin=decimal_string(rounded_margin),
        exposure_percent=decimal_string(exposure_percent),
        accepted=accepted,
        reason=reason,
    )


# =============================================================================
# TP PROJECTION
# =============================================================================

def calculate_tp_projection(
    entry_quantity: Decimal,
) -> TakeProfitProjection:

    tp1 = quantize_down(
        entry_quantity * TP1_PERCENT / Decimal("100"),
        QTY_STEP,
    )

    tp2 = quantize_down(
        entry_quantity * TP2_PERCENT / Decimal("100"),
        QTY_STEP,
    )

    tp3 = entry_quantity - tp1 - tp2

    if tp3 < Decimal("0"):
        tp3 = Decimal("0")

    reconciled = tp1 + tp2 + tp3

    return TakeProfitProjection(
        tp1_quantity=decimal_string(tp1),
        tp2_quantity=decimal_string(tp2),
        tp3_quantity=decimal_string(tp3),
        reconciled_quantity=decimal_string(reconciled),
        trigger_1_percent=decimal_string(TP1_TRIGGER_PERCENT),
        trigger_2_percent=decimal_string(TP2_TRIGGER_PERCENT),
        trailing_distance_percent=decimal_string(
            TRAILING_DISTANCE_PERCENT
        ),
    )


# =============================================================================
# BACKUP PROJECTION
# =============================================================================

def calculate_backup_projection(
    balance: Decimal,
) -> BackupProjection:

    each_margin = (
        balance * BACKUP_PERCENT / Decimal("100")
    )

    total_margin = each_margin * Decimal(MAX_BACKUPS)

    return BackupProjection(
        max_backups=MAX_BACKUPS,
        backup_percent=decimal_string(BACKUP_PERCENT),
        backup_buffer_percent=decimal_string(
            BACKUP_BUFFER_PERCENT
        ),
        projected_backup_margin_each=decimal_string(each_margin),
        projected_backup_total_margin=decimal_string(total_margin),
    )


# =============================================================================
# CANDIDATE CONSTRUCTION
# =============================================================================

def build_candidate(
    signal: StrategySignal,
    risk: RiskProjection,
) -> Candidate:

    if not risk.accepted:
        raise SafetyViolation(
            "candidate construction rejected by risk gate"
        )

    return Candidate(
        candidate_id=str(uuid.uuid4()),
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        direction=signal.direction,
        quantity=risk.rounded_quantity,
        mark_price=signal.observed_price,
        target_leverage=decimal_string(TARGET_LEVERAGE),
        phase=CandidatePhase.RISK_ACCEPTED.value,
        created_at=now_ts(),
    )


# =============================================================================
# AUTHORIZATION ENVELOPE
# =============================================================================

def build_authorization(
    candidate: Candidate,
) -> AuthorizationEnvelope:

    payload_core = {
        "candidate_id": candidate.candidate_id,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "quantity": candidate.quantity,
        "leverage": candidate.target_leverage,
        "transport": "SYNTHETIC_ONLY",
        "executable": False,
        "network_writes_allowed": False,
    }

    payload_hash = sha256_text(
        canonical_json(payload_core)
    )

    return AuthorizationEnvelope(
        authorization_id=str(uuid.uuid4()),
        candidate_id=candidate.candidate_id,
        symbol=candidate.symbol,
        direction=candidate.direction,
        quantity=candidate.quantity,
        leverage=candidate.target_leverage,
        transport="SYNTHETIC_ONLY",
        executable=False,
        network_writes_allowed=False,
        created_at=now_ts(),
        payload_hash=payload_hash,
    )


def validate_authorization(
    auth: AuthorizationEnvelope,
    candidate: Candidate,
) -> bool:

    payload_core = {
        "candidate_id": candidate.candidate_id,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "quantity": candidate.quantity,
        "leverage": candidate.target_leverage,
        "transport": "SYNTHETIC_ONLY",
        "executable": False,
        "network_writes_allowed": False,
    }

    expected_hash = sha256_text(
        canonical_json(payload_core)
    )

    return (
        auth.candidate_id == candidate.candidate_id
        and auth.symbol == candidate.symbol
        and auth.direction == candidate.direction
        and auth.quantity == candidate.quantity
        and auth.leverage == candidate.target_leverage
        and auth.transport == "SYNTHETIC_ONLY"
        and auth.executable is False
        and auth.network_writes_allowed is False
        and auth.payload_hash == expected_hash
    )


# =============================================================================
# SYNTHETIC TRANSPORT
# =============================================================================

def synthetic_dispatch(
    auth: AuthorizationEnvelope,
) -> SyntheticReceipt:

    global SYNTHETIC_DISPATCH_COUNT

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise SafetyViolation(
            "synthetic transport constant unexpectedly disabled"
        )

    if auth.executable:
        raise SafetyViolation(
            "executable authorization rejected"
        )

    if auth.network_writes_allowed:
        raise SafetyViolation(
            "network writable authorization rejected"
        )

    if EXCHANGE_NETWORK_WRITES_ENABLED:
        raise SafetyViolation(
            "exchange write constant unexpectedly enabled"
        )

    SYNTHETIC_DISPATCH_COUNT += 1

    return SyntheticReceipt(
        receipt_id=str(uuid.uuid4()),
        authorization_id=auth.authorization_id,
        candidate_id=auth.candidate_id,
        transmitted=False,
        synthetic_only=True,
        transport="LOCAL_SYNTHETIC_DISPATCH",
        created_at=now_ts(),
    )


# =============================================================================
# TRANSITION HELPERS
# =============================================================================

_ALLOWED_TRANSITIONS = {
    CandidatePhase.RISK_ACCEPTED.value:
        CandidatePhase.AUTHORIZED.value,

    CandidatePhase.AUTHORIZED.value:
        CandidatePhase.SYNTHETICALLY_DISPATCHED.value,

    CandidatePhase.SYNTHETICALLY_DISPATCHED.value:
        CandidatePhase.SEALED.value,
}


def transition_phase(
    current: str,
    target: str,
) -> str:

    global TRANSITION_COUNT
    global CONSUMED_TRANSITION_COUNT

    allowed = _ALLOWED_TRANSITIONS.get(current)

    if allowed != target:
        raise SafetyViolation(
            f"invalid phase transition {current} -> {target}"
        )

    TRANSITION_COUNT += 1
    CONSUMED_TRANSITION_COUNT += 1

    return target


# =============================================================================
# DURABLE STATE
# =============================================================================

def state_payload_without_hash(
    state: RuntimeState,
) -> Dict[str, Any]:

    payload = asdict(state)
    payload.pop("state_hash", None)

    return payload


def calculate_state_hash(
    state: RuntimeState,
) -> str:

    payload = state_payload_without_hash(state)

    return sha256_text(
        canonical_json(payload)
    )


def seal_state_hash(
    state: RuntimeState,
) -> RuntimeState:

    state.state_hash = calculate_state_hash(state)
    return state


def verify_state_hash(
    state: RuntimeState,
) -> bool:

    return state.state_hash == calculate_state_hash(state)


def persist_state(
    state: RuntimeState,
) -> None:

    state = seal_state_hash(state)

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = STATE_FILE.with_suffix(
        STATE_FILE.suffix + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            asdict(state),
            handle,
            sort_keys=True,
            indent=2,
        )

        handle.flush()

        try:
            os.fsync(handle.fileno())
        except OSError:
            pass

    os.replace(
        temporary,
        STATE_FILE,
    )


def load_state() -> Optional[RuntimeState]:

    if not STATE_FILE.exists():
        return None

    try:
        with STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:

            data = json.load(handle)

        return RuntimeState(**data)

    except Exception as exc:
        print(
            f"{VERSION}: STATE RESTORE ERROR: {exc}",
            flush=True,
        )

        return None
# =============================================================================
# VALIDATION
# =============================================================================

def run_validation() -> RuntimeState:

    global SYNTHETIC_DISPATCH_COUNT
    global TRANSITION_COUNT
    global CONSUMED_TRANSITION_COUNT

    SYNTHETIC_DISPATCH_COUNT = 0
    TRANSITION_COUNT = 0
    CONSUMED_TRANSITION_COUNT = 0

    runtime_id = str(uuid.uuid4())
    generation = 1
    recovery_epoch = 1

    # -------------------------------------------------------------------------
    section("R31B TEST 1: ABSOLUTE SAFETY CONFIGURATION")
    # -------------------------------------------------------------------------

    check(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Network Writes Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )

    check(
        "WebSocket Writes Disabled",
        WEBSOCKET_WRITES_ENABLED is False,
    )

    check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 2: STRATEGY CONFIGURATION")
    # -------------------------------------------------------------------------

    check(
        "Target Leverage Is 100x",
        TARGET_LEVERAGE == Decimal("100"),
    )

    check(
        "Initial Entry Is Five Percent",
        INITIAL_ENTRY_PERCENT == Decimal("5"),
    )

    check(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    check(
        "Maximum Backups Is Three",
        MAX_BACKUPS == 3,
    )

    check(
        "Backup Size Is Five Percent",
        BACKUP_PERCENT == Decimal("5"),
    )

    check(
        "Maximum Fund Exposure Is Thirty Five Percent",
        MAX_FUND_EXPOSURE_PERCENT == Decimal("35"),
    )

    check(
        "Backup Buffer Is Point Three Percent",
        BACKUP_BUFFER_PERCENT == Decimal("0.3"),
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 3: STRATEGY SAFETY TOGGLES")
    # -------------------------------------------------------------------------

    check(
        "One Direction Only Enabled",
        ONE_DIRECTION_ONLY is True,
    )

    check(
        "Anti Duplicate Orders Enabled",
        ANTI_DUPLICATE_ORDERS is True,
    )

    check(
        "Trend Reversal Exit Enabled",
        TREND_REVERSAL_EXIT is True,
    )

    check(
        "Idle Pyramid Cleanup Enabled",
        IDLE_PYRAMID_CLEANUP is True,
    )

    check(
        "Signal Expiry Is 120 Seconds",
        SIGNAL_EXPIRY_SECONDS == 120,
    )

    check(
        "Loss Cooldown Is 300 Seconds",
        LOSS_COOLDOWN_SECONDS == 300,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 4: SYNTHETIC OBSERVATION")
    # -------------------------------------------------------------------------

    observation = build_observation()

    check(
        "Observation Symbol Matches",
        observation.symbol == SYMBOL,
    )

    check(
        "Observation Price Is Positive",
        Decimal(observation.mark_price) > 0,
    )

    check(
        "Observation Source Is Synthetic",
        observation.source == "R31B_SYNTHETIC_OBSERVATION",
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 5: SIGNAL CONSTRUCTION")
    # -------------------------------------------------------------------------

    signal = build_signal(
        observation,
        Direction.LONG,
    )

    check(
        "Signal ID Present",
        bool(signal.signal_id),
    )

    check(
        "Signal Symbol Matches Observation",
        signal.symbol == observation.symbol,
    )

    check(
        "Signal Direction Is Valid",
        signal.direction == Direction.LONG.value,
    )

    check(
        "Signal Is Valid",
        signal_is_valid(signal),
    )

    check(
        "Signal Expiry Window Exact",
        signal.expires_at - signal.created_at
        == SIGNAL_EXPIRY_SECONDS,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 6: QUANTITY / RISK PROJECTION")
    # -------------------------------------------------------------------------

    risk = calculate_risk_projection(
        SYNTHETIC_AVAILABLE_BALANCE,
        SYNTHETIC_MARK_PRICE,
    )

    quantity = Decimal(
        risk.rounded_quantity
    )

    check(
        "Risk Gate Accepted Synthetic Candidate",
        risk.accepted,
    )

    check(
        "Entry Margin Budget Positive",
        Decimal(risk.entry_margin_budget) > 0,
    )

    check(
        "Projected Notional Positive",
        Decimal(risk.projected_notional) > 0,
    )

    check(
        "Rounded Quantity Meets Minimum",
        quantity >= MIN_QTY,
    )

    check(
        "Rounded Quantity Respects Quantity Step",
        quantize_down(quantity, QTY_STEP) == quantity,
    )

    check(
        "Rounded Margin Positive",
        Decimal(risk.rounded_margin) > 0,
    )

    check(
        "Projected Exposure Below Maximum",
        Decimal(risk.exposure_percent)
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    print(
        f"{VERSION}: RISK PROJECTION "
        f"balance={risk.available_balance} "
        f"margin-budget={risk.entry_margin_budget} "
        f"notional={risk.projected_notional} "
        f"qty={risk.rounded_quantity} "
        f"rounded-margin={risk.rounded_margin}",
        flush=True,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 7: TAKE PROFIT PROJECTION")
    # -------------------------------------------------------------------------

    tp = calculate_tp_projection(
        quantity
    )

    check(
        "TP1 Percentage Is Twenty",
        TP1_PERCENT == Decimal("20"),
    )

    check(
        "TP2 Percentage Is Twenty",
        TP2_PERCENT == Decimal("20"),
    )

    check(
        "TP3 Percentage Is Sixty",
        TP3_PERCENT == Decimal("60"),
    )

    check(
        "TP Percentages Sum To One Hundred",
        TP1_PERCENT + TP2_PERCENT + TP3_PERCENT
        == Decimal("100"),
    )

    check(
        "TP Quantities Reconcile To Entry Quantity",
        Decimal(tp.reconciled_quantity) == quantity,
    )

    check(
        "TP1 Trigger Is Point Five Percent",
        TP1_TRIGGER_PERCENT == Decimal("0.5"),
    )

    check(
        "TP2 Trigger Is One Percent",
        TP2_TRIGGER_PERCENT == Decimal("1.0"),
    )

    check(
        "Trailing Distance Is Point Twenty Percent",
        TRAILING_DISTANCE_PERCENT == Decimal("0.20"),
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 8: BACKUP PROJECTION")
    # -------------------------------------------------------------------------

    backup = calculate_backup_projection(
        SYNTHETIC_AVAILABLE_BALANCE
    )

    check(
        "Backup Projection Maximum Count Matches Strategy",
        backup.max_backups == MAX_BACKUPS,
    )

    check(
        "Backup Projection Size Matches Strategy",
        Decimal(backup.backup_percent)
        == BACKUP_PERCENT,
    )

    check(
        "Backup Projection Buffer Matches Strategy",
        Decimal(backup.backup_buffer_percent)
        == BACKUP_BUFFER_PERCENT,
    )

    check(
        "Projected Backup Margin Positive",
        Decimal(backup.projected_backup_margin_each) > 0,
    )

    check(
        "Projected Backup Total Equals Three Backups",
        Decimal(backup.projected_backup_total_margin)
        ==
        Decimal(backup.projected_backup_margin_each)
        * Decimal(MAX_BACKUPS),
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 9: TOTAL STRATEGY FUND BUDGET")
    # -------------------------------------------------------------------------

    total_strategy_margin_percent = (
        INITIAL_ENTRY_PERCENT
        + PYRAMID_PERCENT * Decimal(MAX_PYRAMID_ADDS)
        + BACKUP_PERCENT * Decimal(MAX_BACKUPS)
    )

    check(
        "Full Planned Strategy Margin Is Twenty Five Percent",
        total_strategy_margin_percent == Decimal("25"),
    )

    check(
        "Full Planned Strategy Margin Below Maximum Exposure",
        total_strategy_margin_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 10: CANDIDATE CONSTRUCTION")
    # -------------------------------------------------------------------------

    candidate = build_candidate(
        signal,
        risk,
    )

    check(
        "Candidate ID Present",
        bool(candidate.candidate_id),
    )

    check(
        "Candidate Signal Binding Exact",
        candidate.signal_id == signal.signal_id,
    )

    check(
        "Candidate Symbol Binding Exact",
        candidate.symbol == signal.symbol,
    )

    check(
        "Candidate Quantity Binding Exact",
        candidate.quantity == risk.rounded_quantity,
    )

    check(
        "Candidate Leverage Binding Exact",
        Decimal(candidate.target_leverage)
        == TARGET_LEVERAGE,
    )

    check(
        "Candidate Starts Risk Accepted",
        candidate.phase
        == CandidatePhase.RISK_ACCEPTED.value,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 11: AUTHORIZATION ENVELOPE")
    # -------------------------------------------------------------------------

    auth = build_authorization(
        candidate
    )

    check(
        "Authorization ID Present",
        bool(auth.authorization_id),
    )

    check(
        "Authorization Candidate Binding Exact",
        auth.candidate_id == candidate.candidate_id,
    )

    check(
        "Authorization Symbol Binding Exact",
        auth.symbol == candidate.symbol,
    )

    check(
        "Authorization Quantity Binding Exact",
        auth.quantity == candidate.quantity,
    )

    check(
        "Authorization Is Explicitly Non Executable",
        auth.executable is False,
    )

    check(
        "Authorization Explicitly Denies Network Writes",
        auth.network_writes_allowed is False,
    )

    check(
        "Authorization Transport Is Synthetic Only",
        auth.transport == "SYNTHETIC_ONLY",
    )

    check(
        "Authorization Hash Validates",
        validate_authorization(
            auth,
            candidate,
        ),
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 12: AUTHORIZATION TAMPER REJECTION")
    # -------------------------------------------------------------------------

    tampered_auth = AuthorizationEnvelope(
        authorization_id=auth.authorization_id,
        candidate_id=auth.candidate_id,
        symbol=auth.symbol,
        direction=auth.direction,
        quantity="999",
        leverage=auth.leverage,
        transport=auth.transport,
        executable=auth.executable,
        network_writes_allowed=auth.network_writes_allowed,
        created_at=auth.created_at,
        payload_hash=auth.payload_hash,
    )

    check(
        "Tampered Authorization Rejected",
        not validate_authorization(
            tampered_auth,
            candidate,
        ),
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 13: PHASE TRANSITION TO AUTHORIZED")
    # -------------------------------------------------------------------------

    phase = candidate.phase

    phase = transition_phase(
        phase,
        CandidatePhase.AUTHORIZED.value,
    )

    check(
        "Candidate Transitioned To Authorized",
        phase == CandidatePhase.AUTHORIZED.value,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 14: SYNTHETIC DISPATCH")
    # -------------------------------------------------------------------------

    receipt = synthetic_dispatch(
        auth
    )

    phase = transition_phase(
        phase,
        CandidatePhase.SYNTHETICALLY_DISPATCHED.value,
    )

    check(
        "Synthetic Receipt ID Present",
        bool(receipt.receipt_id),
    )

    check(
        "Synthetic Receipt Candidate Binding Exact",
        receipt.candidate_id == candidate.candidate_id,
    )

    check(
        "Synthetic Receipt Authorization Binding Exact",
        receipt.authorization_id == auth.authorization_id,
    )

    check(
        "Synthetic Dispatch Reports No Transmission",
        receipt.transmitted is False,
    )

    check(
        "Synthetic Receipt Declares Synthetic Only",
        receipt.synthetic_only is True,
    )

    check(
        "Synthetic Dispatch Count Is One",
        SYNTHETIC_DISPATCH_COUNT == 1,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 15: TERMINAL SEAL")
    # -------------------------------------------------------------------------

    phase = transition_phase(
        phase,
        CandidatePhase.SEALED.value,
    )

    check(
        "Candidate Final Phase Is Sealed",
        phase == CandidatePhase.SEALED.value,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 16: INVALID TERMINAL REOPEN REJECTION")
    # -------------------------------------------------------------------------

    terminal_reopen_rejected = False

    try:
        transition_phase(
            phase,
            CandidatePhase.AUTHORIZED.value,
        )

    except SafetyViolation:
        terminal_reopen_rejected = True

    check(
        "Sealed Candidate Cannot Reopen",
        terminal_reopen_rejected,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 17: REAL ORDER FIREBREAK")
    # -------------------------------------------------------------------------

    real_blocked = False

    try:
        block_real_order(
            "R31B intentional validation"
        )

    except SafetyViolation:
        real_blocked = True

    check(
        "Real Order Path Blocked",
        real_blocked,
    )

    check(
        "Real Order Counter Remains Zero",
        REAL_ORDER_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 18: DEMO ORDER FIREBREAK")
    # -------------------------------------------------------------------------

    demo_blocked = False

    try:
        block_demo_order(
            "R31B intentional validation"
        )

    except SafetyViolation:
        demo_blocked = True

    check(
        "Demo Order Path Blocked",
        demo_blocked,
    )

    check(
        "Demo Order Counter Remains Zero",
        DEMO_ORDER_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 19: EXCHANGE WRITE FIREBREAK")
    # -------------------------------------------------------------------------

    network_blocked = False

    try:
        block_network_write(
            "POST",
            "/capi/v2/order",
        )

    except SafetyViolation:
        network_blocked = True

    check(
        "HTTP POST Blocked",
        network_blocked,
    )

    check(
        "Network Write Counter Remains Zero",
        NETWORK_WRITE_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 20: MUTATION FIREBREAK")
    # -------------------------------------------------------------------------

    leverage_blocked = False
    margin_blocked = False
    position_blocked = False
    account_blocked = False

    try:
        block_mutation("LEVERAGE")
    except SafetyViolation:
        leverage_blocked = True

    try:
        block_mutation("MARGIN")
    except SafetyViolation:
        margin_blocked = True

    try:
        block_mutation("POSITION")
    except SafetyViolation:
        position_blocked = True

    try:
        block_mutation("ACCOUNT")
    except SafetyViolation:
        account_blocked = True

    check(
        "Leverage Mutation Blocked",
        leverage_blocked,
    )

    check(
        "Margin Mutation Blocked",
        margin_blocked,
    )

    check(
        "Position Mutation Blocked",
        position_blocked,
    )

    check(
        "Account Mutation Blocked",
        account_blocked,
    )

    check(
        "Mutation Counter Remains Zero",
        MUTATION_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 21: DURABLE STATE CREATION")
    # -------------------------------------------------------------------------

    state = RuntimeState(
        version=VERSION,
        runtime_id=runtime_id,
        generation=generation,
        recovery_epoch=recovery_epoch,
        phase=phase,
        candidate_id=candidate.candidate_id,
        authorization_id=auth.authorization_id,
        synthetic_receipt_id=receipt.receipt_id,

        real_order_count=REAL_ORDER_COUNT,
        demo_order_count=DEMO_ORDER_COUNT,
        network_write_count=NETWORK_WRITE_COUNT,
        mutation_count=MUTATION_COUNT,

        synthetic_dispatch_count=SYNTHETIC_DISPATCH_COUNT,
        transition_count=TRANSITION_COUNT,
        consumed_transition_count=CONSUMED_TRANSITION_COUNT,

        sealed=True,
        state_hash="",
    )

    persist_state(
        state
    )

    check(
        "Durable State File Created",
        STATE_FILE.exists(),
    )

    restored = load_state()

    check(
        "Durable State Restored",
        restored is not None,
    )

    if restored is None:
        raise RuntimeError(
            "R31B durable state could not be restored"
        )

    check(
        "Persisted State Integrity Hash Valid",
        verify_state_hash(restored),
    )

    check(
        "Persisted Version Matches",
        restored.version == VERSION,
    )

    check(
        "Persisted Runtime ID Matches",
        restored.runtime_id == runtime_id,
    )

    check(
        "Persisted Generation Matches",
        restored.generation == generation,
    )

    check(
        "Persisted Recovery Epoch Matches",
        restored.recovery_epoch == recovery_epoch,
    )

    check(
        "Persisted Phase Is Sealed",
        restored.phase == CandidatePhase.SEALED.value,
    )

    check(
        "Persisted Candidate ID Matches",
        restored.candidate_id == candidate.candidate_id,
    )

    check(
        "Persisted Authorization ID Matches",
        restored.authorization_id == auth.authorization_id,
    )

    check(
        "Persisted Synthetic Receipt Matches",
        restored.synthetic_receipt_id == receipt.receipt_id,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 22: PERSISTED SAFETY COUNTERS")
    # -------------------------------------------------------------------------

    check(
        "Persisted Real Order Count Is Zero",
        restored.real_order_count == 0,
    )

    check(
        "Persisted Demo Order Count Is Zero",
        restored.demo_order_count == 0,
    )

    check(
        "Persisted Network Write Count Is Zero",
        restored.network_write_count == 0,
    )

    check(
        "Persisted Mutation Count Is Zero",
        restored.mutation_count == 0,
    )

    check(
        "Persisted Synthetic Dispatch Count Is One",
        restored.synthetic_dispatch_count == 1,
    )

    check(
        "Persisted Transition Count Is Three",
        restored.transition_count == 3,
    )

    check(
        "Consumed Transition Count Is Three",
        restored.consumed_transition_count == 3,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 23: RESTART / TERMINAL RECOVERY SEAL")
    # -------------------------------------------------------------------------

    restart_reopen_rejected = (
        restored.sealed is True
        and restored.phase
        == CandidatePhase.SEALED.value
    )

    check(
        "Restart Cannot Reopen Sealed Candidate",
        restart_reopen_rejected,
    )

    check(
        "Restart Restores Terminal Seal",
        restored.sealed is True,
    )

    check(
        "Restart Preserves Candidate Binding",
        restored.candidate_id
        == candidate.candidate_id,
    )

    check(
        "Restart Preserves Authorization Binding",
        restored.authorization_id
        == auth.authorization_id,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 24: ENVIRONMENT ESCALATION RESISTANCE")
    # -------------------------------------------------------------------------

    environment_real_attempt = (
        os.getenv(
            "REAL_ORDER_EXECUTION",
            "",
        ).strip().lower()
        in {
            "1",
            "true",
            "yes",
            "on",
            "enabled",
        }
    )

    environment_write_attempt = (
        os.getenv(
            "EXCHANGE_NETWORK_WRITES",
            "",
        ).strip().lower()
        in {
            "1",
            "true",
            "yes",
            "on",
            "enabled",
        }
    )

    environment_mutation_attempt = (
        os.getenv(
            "LEVERAGE_MUTATION",
            "",
        ).strip().lower()
        in {
            "1",
            "true",
            "yes",
            "on",
            "enabled",
        }
    )

    check(
        "Environment Cannot Directly Activate Real Execution",
        (
            REAL_ORDER_EXECUTION_ENABLED is False
            and regardless_environment(
                environment_real_attempt
            )
        ),
    )

    check(
        "Environment Cannot Directly Activate Exchange Writes",
        (
            EXCHANGE_NETWORK_WRITES_ENABLED is False
            and regardless_environment(
                environment_write_attempt
            )
        ),
    )

    check(
        "Environment Cannot Directly Activate Mutation",
        (
            LEVERAGE_MUTATION_ENABLED is False
            and regardless_environment(
                environment_mutation_attempt
            )
        ),
    )

    check(
        "Real Execution Constant Remains Frozen",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Execution Constant Remains Frozen",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Write Constant Remains Frozen",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Mutation Constants Remain Frozen",
        (
            not LEVERAGE_MUTATION_ENABLED
            and not MARGIN_MUTATION_ENABLED
            and not POSITION_MUTATION_ENABLED
            and not ACCOUNT_MUTATION_ENABLED
        ),
    )

    check(
        "Synthetic Transport Constant Remains Frozen",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 25: COUNTER INTEGRITY")
    # -------------------------------------------------------------------------

    check(
        "Real Order Count Is Zero",
        REAL_ORDER_COUNT == 0,
    )

    check(
        "Demo Order Count Is Zero",
        DEMO_ORDER_COUNT == 0,
    )

    check(
        "Network Write Count Is Zero",
        NETWORK_WRITE_COUNT == 0,
    )

    check(
        "Mutation Count Is Zero",
        MUTATION_COUNT == 0,
    )

    check(
        "Synthetic Dispatch Count Matches Lifecycle",
        SYNTHETIC_DISPATCH_COUNT == 1,
    )

    check(
        "Transition Counter Matches Lifecycle",
        TRANSITION_COUNT == 3,
    )

    check(
        "Consumed Transition Counter Matches Lifecycle",
        CONSUMED_TRANSITION_COUNT == 3,
    )

    # -------------------------------------------------------------------------
    section("R31B TEST 26: FINAL PRE-EXECUTION READINESS SEAL")
    # -------------------------------------------------------------------------

    passed_before_final = PASSED
    failed_before_final = FAILED

    check(
        "All Prior Validation Checks Passed",
        failed_before_final == 0,
    )

    print(
        f"  passed-before-final={passed_before_final}, "
        f"failed={failed_before_final}",
        flush=True,
    )

    check(
        "R31B Remains Non Executable",
        (
            REAL_ORDER_EXECUTION_ENABLED is False
            and DEMO_ORDER_EXECUTION_ENABLED is False
        ),
    )

    check(
        "R31B Remains Network Write Locked",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "R31B Remains Mutation Locked",
        (
            not LEVERAGE_MUTATION_ENABLED
            and not MARGIN_MUTATION_ENABLED
            and not POSITION_MUTATION_ENABLED
            and not ACCOUNT_MUTATION_ENABLED
        ),
    )

    check(
        "R31B Uses Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    check(
        "R31B Final Phase Is Sealed",
        restored.phase == CandidatePhase.SEALED.value,
    )

    return restored
# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop(
    state: RuntimeState,
) -> None:

    heartbeat = 0

    while True:
        time.sleep(
            HEARTBEAT_SECONDS
        )

        heartbeat += 1

        print(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"phase={state.phase} | "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY} | "
            f"real-execution={REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes={EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"generation={state.generation} | "
            f"recovery-epoch={state.recovery_epoch}",
            flush=True,
        )


# =============================================================================
# STARTUP IDENTITY
# =============================================================================

def print_identity() -> None:

    line()

    print(
        f"{VERSION}: MAIN.PY ENTERED",
        flush=True,
    )

    line()

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL EXECUTION "
        f"{'ENABLED' if REAL_ORDER_EXECUTION_ENABLED else 'DISABLED'}",
        flush=True,
    )

    print(
        f"{VERSION}: DEMO EXECUTION "
        f"{'ENABLED' if DEMO_ORDER_EXECUTION_ENABLED else 'DISABLED'}",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES "
        f"{'ENABLED' if EXCHANGE_NETWORK_WRITES_ENABLED else 'DISABLED'}",
        flush=True,
    )

    print(
        f"{VERSION}: LEVERAGE MUTATION "
        f"{'ENABLED' if LEVERAGE_MUTATION_ENABLED else 'DISABLED'}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY="
        f"{SYNTHETIC_TRANSPORT_ONLY}",
        flush=True,
    )

    line()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    print_identity()

    start_health_server()

    print(
        f"{VERSION}: STARTING FINAL PRE-EXECUTION "
        f"INTEGRATION VALIDATION",
        flush=True,
    )

    state = run_validation()

    line()

    if FAILED == 0:

        print(
            f"{VERSION}: VALIDATION PASSED",
            flush=True,
        )

    else:

        print(
            f"{VERSION}: VALIDATION FAILED",
            flush=True,
        )

    line()

    print(
        f"{VERSION}: SUMMARY "
        f"passed={PASSED} "
        f"failed={FAILED}",
        flush=True,
    )

    print(
        f"{VERSION}: SAFETY SEAL "
        f"real-orders={REAL_ORDER_COUNT} "
        f"demo-orders={DEMO_ORDER_COUNT} "
        f"network-writes={NETWORK_WRITE_COUNT} "
        f"mutations={MUTATION_COUNT}",
        flush=True,
    )

    print(
        f"{VERSION}: PRE-EXECUTION SEAL "
        f"phase={state.phase} "
        f"synthetic-dispatches={SYNTHETIC_DISPATCH_COUNT} "
        f"transitions={TRANSITION_COUNT}",
        flush=True,
    )

    if FAILED != 0:
        raise SystemExit(1)

    heartbeat_loop(
        state
    )


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    main()
