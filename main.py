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
from pathlib import Path
from typing import Any, Dict, Optional


# =============================================================================
# R29 UNIT B
# READ-ONLY STRATEGY / RUNTIME INTEGRATION
#
# SAFETY DISCIPLINE:
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE:
#   Read-only/synthetic observations
#       ->
#   strategy signal
#       ->
#   risk projection
#       ->
#   frozen non-executable decision envelope
#       ->
#   synthetic receipt
#       ->
#   durable restart-safe runtime state
# =============================================================================


getcontext().prec = 40


# =============================================================================
# PART 1 — CONSTANTS / SAFETY LOCKS
# =============================================================================


MODULE_NAME = "R29 UNIT B"
STATE_VERSION = 1

HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_PATH = Path(
    os.getenv(
        "R29_UNIT_B_STATE_PATH",
        "r29_unit_b_state.json",
    )
)


# -----------------------------------------------------------------------------
# ABSOLUTE EXECUTION LOCKS
# -----------------------------------------------------------------------------


LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

ACCOUNT_MUTATION_ENABLED = False

WEBSOCKET_WRITES_ENABLED = False


# -----------------------------------------------------------------------------
# STRATEGY BASELINE
# -----------------------------------------------------------------------------


SYMBOL = os.getenv(
    "R29_SYMBOL",
    "BTCUSDT",
).strip().upper()

MARGIN_MODE = "ISOLATED"

PLANNED_LEVERAGE = 100

INITIAL_ENTRY_PERCENT = Decimal("5")

PYRAMID_PERCENT = Decimal("5")

BACKUP_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1

MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

SIGNAL_EXPIRY_SECONDS = 120

LOSS_COOLDOWN_SECONDS = 300


# -----------------------------------------------------------------------------
# LOCAL QUANTITY CONSTRAINTS
# -----------------------------------------------------------------------------


QTY_STEP = Decimal("0.0001")

MIN_QTY = Decimal("0.0001")


# -----------------------------------------------------------------------------
# SAFETY COUNTERS
# -----------------------------------------------------------------------------


REAL_WRITE_COUNT = 0

DEMO_WRITE_COUNT = 0

NETWORK_WRITE_COUNT = 0

WEBSOCKET_WRITE_COUNT = 0

SYNTHETIC_DISPATCH_COUNT = 0


# -----------------------------------------------------------------------------
# DIAGNOSTIC COUNTERS
# -----------------------------------------------------------------------------


PASS_ASSERTIONS = 0

TEST_GROUPS = 0


SEP = "-" * 92


print(f"{MODULE_NAME}: MAIN.PY ENTERED")
print(f"{MODULE_NAME}: IMPORTS COMPLETE")
print(f"{MODULE_NAME}: CONSTANTS INITIALIZED")


# =============================================================================
# PART 2 — DATA MODELS / UTILITY FUNCTIONS
# =============================================================================


class LocalBlock(RuntimeError):
    pass


class DecisionState(str, Enum):

    OBSERVED = "OBSERVED"

    VALIDATED = "VALIDATED"

    SIZED = "SIZED"

    FROZEN = "FROZEN"


@dataclass(frozen=True)
class MarketObservation:

    symbol: str

    mark_price: str

    observed_ms: int

    source: str = "SYNTHETIC_READ_ONLY"


@dataclass(frozen=True)
class AccountObservation:

    available_usdt: str

    position_count: int

    observed_ms: int

    source: str = "SYNTHETIC_READ_ONLY"


@dataclass(frozen=True)
class StrategySignal:

    signal_id: str

    symbol: str

    direction: str

    confidence: str

    created_ms: int

    expires_ms: int


@dataclass(frozen=True)
class RiskProjection:

    available_usdt: str

    allocation_percent: str

    margin_budget: str

    leverage: int

    planned_notional: str

    raw_quantity: str

    rounded_quantity: str

    projected_notional: str

    projected_margin: str

    max_fund_exposure_percent: str


@dataclass(frozen=True)
class DecisionEnvelope:

    decision_id: str

    signal_id: str

    symbol: str

    direction: str

    side: str

    position_side: str

    margin_mode: str

    leverage: int

    quantity: str

    state: str

    executable: bool

    synthetic_only: bool

    payload_hash: str

    config_fingerprint: str

    created_ms: int


@dataclass
class RuntimeState:

    version: int

    runtime_id: str

    generation: int

    recovery_epoch: int

    boot_count: int

    config_fingerprint: str

    last_decision_id: Optional[str] = None

    last_decision_hash: Optional[str] = None

    real_order_count: int = 0

    demo_order_count: int = 0

    network_write_count: int = 0

    websocket_write_count: int = 0

    synthetic_dispatch_count: int = 0

    event_sequence: int = 0

    integrity_seal: str = ""


# -----------------------------------------------------------------------------
# TIME
# -----------------------------------------------------------------------------


def now_ms() -> int:

    return int(time.time() * 1000)


# -----------------------------------------------------------------------------
# CANONICAL SERIALIZATION
# -----------------------------------------------------------------------------


def stable_json(value: Any) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(value: Any) -> str:

    if not isinstance(value, str):

        value = stable_json(value)

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


# -----------------------------------------------------------------------------
# DECIMAL HELPERS
# -----------------------------------------------------------------------------


def dec(value: Any) -> Decimal:

    return Decimal(str(value))


def fmt(value: Decimal) -> str:

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = text.rstrip("0").rstrip(".")

    return text or "0"


def floor_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


# -----------------------------------------------------------------------------
# ASSERTION HELPERS
# -----------------------------------------------------------------------------


def require(
    condition: bool,
    message: str,
) -> None:

    if not condition:

        raise LocalBlock(message)


def pass_check(
    label: str,
    condition: bool,
) -> None:

    global PASS_ASSERTIONS

    require(
        condition,
        label,
    )

    PASS_ASSERTIONS += 1

    print(
        f"{label:<84} ✅ PASS"
    )


def expect_block(
    label: str,
    fn,
    expected: str,
) -> None:

    global PASS_ASSERTIONS

    try:

        fn()

    except LocalBlock as exc:

        print(
            f"{MODULE_NAME} LOCAL BLOCK:"
        )

        print(
            f"  {exc}"
        )

        require(
            expected in str(exc),
            f"unexpected block reason: {exc}",
        )

        PASS_ASSERTIONS += 1

        print(
            f"{label:<84} ✅ PASS"
        )

        return

    raise AssertionError(
        f"{label}: expected LocalBlock"
    )


def test_header(
    number: int,
    title: str,
) -> None:

    global TEST_GROUPS

    TEST_GROUPS += 1

    print(SEP)

    print(
        f"{MODULE_NAME} TEST {number}: {title}"
    )

    print(SEP)


# -----------------------------------------------------------------------------
# CONFIGURATION BINDING
# -----------------------------------------------------------------------------


def config_dict() -> Dict[str, Any]:

    return {

        "symbol":
            SYMBOL,

        "margin_mode":
            MARGIN_MODE,

        "planned_leverage":
            PLANNED_LEVERAGE,

        "initial_entry_percent":
            fmt(
                INITIAL_ENTRY_PERCENT
            ),

        "pyramid_percent":
            fmt(
                PYRAMID_PERCENT
            ),

        "backup_percent":
            fmt(
                BACKUP_PERCENT
            ),

        "max_pyramid_adds":
            MAX_PYRAMID_ADDS,

        "max_backups":
            MAX_BACKUPS,

        "max_fund_exposure_percent":
            fmt(
                MAX_FUND_EXPOSURE_PERCENT
            ),

        "signal_expiry_seconds":
            SIGNAL_EXPIRY_SECONDS,

        "loss_cooldown_seconds":
            LOSS_COOLDOWN_SECONDS,

        "qty_step":
            fmt(
                QTY_STEP
            ),

        "min_qty":
            fmt(
                MIN_QTY
            ),

        "live_order_execution":
            LIVE_ORDER_EXECUTION,

        "demo_order_execution":
            DEMO_ORDER_EXECUTION,

        "network_writes_enabled":
            NETWORK_WRITES_ENABLED,

        "synthetic_transport_only":
            SYNTHETIC_TRANSPORT_ONLY,
    }


def config_fingerprint() -> str:

    return sha256_hex(
        config_dict()
    )


# -----------------------------------------------------------------------------
# DURABLE STATE
# -----------------------------------------------------------------------------


def state_payload(
    state: RuntimeState,
) -> Dict[str, Any]:

    payload = asdict(
        state
    )

    payload.pop(
        "integrity_seal",
        None,
    )

    return payload


def state_seal(
    state: RuntimeState,
) -> str:

    return sha256_hex(
        state_payload(
            state
        )
    )


def validate_state(
    state: RuntimeState,
) -> None:

    require(
        state.version == STATE_VERSION,
        "runtime state version mismatch",
    )

    require(
        bool(
            state.runtime_id
        ),
        "runtime id missing",
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
        state.config_fingerprint
        ==
        config_fingerprint(),
        "runtime configuration fingerprint mismatch",
    )

    require(
        state.integrity_seal
        ==
        state_seal(
            state
        ),
        "runtime state integrity seal mismatch",
    )

    require(
        state.real_order_count == 0,
        "real order counter nonzero",
    )

    require(
        state.demo_order_count == 0,
        "demo order counter nonzero",
    )

    require(
        state.network_write_count == 0,
        "network write counter nonzero",
    )

    require(
        state.websocket_write_count == 0,
        "websocket write counter nonzero",
    )


def persist_state(
    state: RuntimeState,
    path: Path = STATE_PATH,
) -> None:

    state.integrity_seal = state_seal(
        state
    )

    data = stable_json(
        asdict(
            state
        )
    ).encode(
        "utf-8"
    )

    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    tmp.write_bytes(
        data
    )

    os.replace(
        tmp,
        path,
    )


def load_state(
    path: Path = STATE_PATH,
) -> RuntimeState:

    raw = json.loads(
        path.read_text(
            "utf-8"
        )
    )

    state = RuntimeState(
        **raw
    )

    validate_state(
        state
    )

    return state


def boot_runtime(
    path: Path = STATE_PATH,
) -> RuntimeState:

    if path.exists():

        prior = load_state(
            path
        )

        state = RuntimeState(

            version=
                STATE_VERSION,

            runtime_id=
                prior.runtime_id,

            generation=
                prior.generation,

            recovery_epoch=
                prior.recovery_epoch + 1,

            boot_count=
                prior.boot_count + 1,

            config_fingerprint=
                config_fingerprint(),

            last_decision_id=
                prior.last_decision_id,

            last_decision_hash=
                prior.last_decision_hash,

            real_order_count=
                prior.real_order_count,

            demo_order_count=
                prior.demo_order_count,

            network_write_count=
                prior.network_write_count,

            websocket_write_count=
                prior.websocket_write_count,

            synthetic_dispatch_count=
                prior.synthetic_dispatch_count,

            event_sequence=
                prior.event_sequence + 1,
        )

    else:

        state = RuntimeState(

            version=
                STATE_VERSION,

            runtime_id=
                str(
                    uuid.uuid4()
                ),

            generation=
                1,

            recovery_epoch=
                1,

            boot_count=
                1,

            config_fingerprint=
                config_fingerprint(),

            event_sequence=
                1,
        )

    persist_state(
        state,
        path,
    )

    return state


# =============================================================================
# PART 3 — READ-ONLY STRATEGY / DECISION ENGINE
# =============================================================================


def validate_market(
    obs: MarketObservation,
) -> None:

    require(
        obs.symbol == SYMBOL,
        "market observation symbol mismatch",
    )

    require(
        dec(
            obs.mark_price
        ) > 0,
        "mark price must be positive",
    )

    require(
        obs.source
        ==
        "SYNTHETIC_READ_ONLY",
        "market observation source not read-only",
    )


def validate_account(
    obs: AccountObservation,
) -> None:

    require(
        dec(
            obs.available_usdt
        ) >= 0,
        "available balance cannot be negative",
    )

    require(
        obs.position_count >= 0,
        "position count cannot be negative",
    )

    require(
        obs.source
        ==
        "SYNTHETIC_READ_ONLY",
        "account observation source not read-only",
    )


# -----------------------------------------------------------------------------
# SIGNAL CREATION / VALIDATION
# -----------------------------------------------------------------------------


def make_signal(
    direction: str,
    age_seconds: int = 0,
) -> StrategySignal:

    direction = (
        direction
        .upper()
        .strip()
    )

    require(
        direction
        in
        {
            "LONG",
            "SHORT",
        },
        "invalid strategy direction",
    )

    created = (
        now_ms()
        -
        age_seconds * 1000
    )

    material = {

        "symbol":
            SYMBOL,

        "direction":
            direction,

        "created_ms":
            created,

        "nonce":
            str(
                uuid.uuid4()
            ),
    }

    return StrategySignal(

        signal_id=
            sha256_hex(
                material
            )[:32],

        symbol=
            SYMBOL,

        direction=
            direction,

        confidence=
            "1.0",

        created_ms=
            created,

        expires_ms=
            created
            +
            SIGNAL_EXPIRY_SECONDS * 1000,
    )


def validate_signal(
    signal: StrategySignal,
    current_ms: Optional[int] = None,
) -> None:

    if current_ms is None:

        current_ms = now_ms()

    require(
        signal.symbol == SYMBOL,
        "signal symbol mismatch",
    )

    require(
        signal.direction
        in
        {
            "LONG",
            "SHORT",
        },
        "invalid strategy direction",
    )

    require(
        signal.created_ms
        <=
        current_ms,
        "signal timestamp is in future",
    )

    require(
        current_ms
        <=
        signal.expires_ms,
        "strategy signal expired",
    )


# -----------------------------------------------------------------------------
# RISK PROJECTION
# -----------------------------------------------------------------------------


def project_initial_risk(
    account: AccountObservation,
    market: MarketObservation,
) -> RiskProjection:

    validate_account(
        account
    )

    validate_market(
        market
    )

    available = dec(
        account.available_usdt
    )

    price = dec(
        market.mark_price
    )

    allocation = (
        INITIAL_ENTRY_PERCENT
    )

    margin_budget = (
        available
        *
        allocation
        /
        Decimal("100")
    )

    planned_notional = (
        margin_budget
        *
        Decimal(
            PLANNED_LEVERAGE
        )
    )

    raw_qty = (
        planned_notional
        /
        price
    )

    rounded_qty = floor_step(
        raw_qty,
        QTY_STEP,
    )

    require(
        rounded_qty
        >=
        MIN_QTY,
        "projected quantity below exchange minimum",
    )

    projected_notional = (
        rounded_qty
        *
        price
    )

    projected_margin = (
        projected_notional
        /
        Decimal(
            PLANNED_LEVERAGE
        )
    )

    if available > 0:

        exposure_percent = (
            projected_margin
            /
            available
            *
            Decimal("100")
        )

    else:

        exposure_percent = Decimal("0")

    require(
        exposure_percent
        <=
        MAX_FUND_EXPOSURE_PERCENT,
        "projected fund exposure exceeds local cap",
    )

    return RiskProjection(

        available_usdt=
            fmt(
                available
            ),

        allocation_percent=
            fmt(
                allocation
            ),

        margin_budget=
            fmt(
                margin_budget
            ),

        leverage=
            PLANNED_LEVERAGE,

        planned_notional=
            fmt(
                planned_notional
            ),

        raw_quantity=
            fmt(
                raw_qty
            ),

        rounded_quantity=
            fmt(
                rounded_qty
            ),

        projected_notional=
            fmt(
                projected_notional
            ),

        projected_margin=
            fmt(
                projected_margin
            ),

        max_fund_exposure_percent=
            fmt(
                MAX_FUND_EXPOSURE_PERCENT
            ),
    )


# -----------------------------------------------------------------------------
# FROZEN DECISION ENVELOPE
# -----------------------------------------------------------------------------


def build_decision(
    signal: StrategySignal,
    risk: RiskProjection,
) -> DecisionEnvelope:

    validate_signal(
        signal
    )

    if signal.direction == "LONG":

        side = "BUY"

        position_side = "LONG"

    else:

        side = "SELL"

        position_side = "SHORT"

    payload = {

        "signal_id":
            signal.signal_id,

        "symbol":
            signal.symbol,

        "direction":
            signal.direction,

        "side":
            side,

        "position_side":
            position_side,

        "margin_mode":
            MARGIN_MODE,

        "leverage":
            PLANNED_LEVERAGE,

        "quantity":
            risk.rounded_quantity,

        "executable":
            False,

        "synthetic_only":
            True,
    }

    payload_hash = sha256_hex(
        payload
    )

    decision_id = sha256_hex(
        {
            "payload_hash":
                payload_hash,

            "config":
                config_fingerprint(),
        }
    )[:32]

    return DecisionEnvelope(

        decision_id=
            decision_id,

        signal_id=
            signal.signal_id,

        symbol=
            signal.symbol,

        direction=
            signal.direction,

        side=
            side,

        position_side=
            position_side,

        margin_mode=
            MARGIN_MODE,

        leverage=
            PLANNED_LEVERAGE,

        quantity=
            risk.rounded_quantity,

        state=
            DecisionState.FROZEN.value,

        executable=
            False,

        synthetic_only=
            True,

        payload_hash=
            payload_hash,

        config_fingerprint=
            config_fingerprint(),

        created_ms=
            now_ms(),
    )


def validate_decision(
    decision: DecisionEnvelope,
) -> None:

    require(
        decision.symbol == SYMBOL,
        "decision symbol mismatch",
    )

    require(
        decision.margin_mode
        ==
        MARGIN_MODE,
        "decision margin mode mismatch",
    )

    require(
        decision.leverage
        ==
        PLANNED_LEVERAGE,
        "decision leverage mismatch",
    )

    require(
        dec(
            decision.quantity
        )
        >=
        MIN_QTY,
        "decision quantity below minimum",
    )

    require(
        decision.executable is False,
        "decision unexpectedly executable",
    )

    require(
        decision.synthetic_only is True,
        "decision not synthetic-only",
    )

    require(
        decision.state
        ==
        DecisionState.FROZEN.value,
        "decision not frozen",
    )

    require(
        decision.config_fingerprint
        ==
        config_fingerprint(),
        "decision configuration fingerprint mismatch",
    )


# -----------------------------------------------------------------------------
# HARD WRITE FIREBREAKS
# -----------------------------------------------------------------------------


def real_http_write(
    *_args,
    **_kwargs,
):

    global REAL_WRITE_COUNT
    global NETWORK_WRITE_COUNT

    REAL_WRITE_COUNT += 1

    NETWORK_WRITE_COUNT += 1

    raise LocalBlock(
        "REAL network write blocked"
    )


def demo_http_write(
    *_args,
    **_kwargs,
):

    global DEMO_WRITE_COUNT
    global NETWORK_WRITE_COUNT

    DEMO_WRITE_COUNT += 1

    NETWORK_WRITE_COUNT += 1

    raise LocalBlock(
        "DEMO network write blocked"
    )


def websocket_write(
    *_args,
    **_kwargs,
):

    global WEBSOCKET_WRITE_COUNT
    global NETWORK_WRITE_COUNT

    WEBSOCKET_WRITE_COUNT += 1

    NETWORK_WRITE_COUNT += 1

    raise LocalBlock(
        "WebSocket write blocked"
    )


def leverage_mutation(
    *_args,
    **_kwargs,
):

    raise LocalBlock(
        "leverage mutation disabled"
    )


def margin_mutation(
    *_args,
    **_kwargs,
):

    raise LocalBlock(
        "margin mutation disabled"
    )


def position_mutation(
    *_args,
    **_kwargs,
):

    raise LocalBlock(
        "position mutation disabled"
    )


def account_mutation(
    *_args,
    **_kwargs,
):

    raise LocalBlock(
        "account mutation disabled"
    )


# -----------------------------------------------------------------------------
# SYNTHETIC TRANSPORT
# -----------------------------------------------------------------------------


def synthetic_transport(
    decision: DecisionEnvelope,
) -> Dict[str, Any]:

    global SYNTHETIC_DISPATCH_COUNT

    validate_decision(
        decision
    )

    SYNTHETIC_DISPATCH_COUNT += 1

    return {

        "accepted":
            True,

        "transmitted":
            False,

        "transport":
            "SYNTHETIC_ONLY",

        "decision_id":
            decision.decision_id,

        "payload_hash":
            decision.payload_hash,

        "dispatch_sequence":
            SYNTHETIC_DISPATCH_COUNT,
    }


# -----------------------------------------------------------------------------
# TEST FILE CLEANUP
# -----------------------------------------------------------------------------


def clean_temp_state(
    path: Path,
) -> None:

    candidates = (

        path,

        path.with_suffix(
            path.suffix + ".tmp"
        ),
    )

    for candidate in candidates:

        try:

            candidate.unlink()

        except FileNotFoundError:

            pass


print(f"{MODULE_NAME}: PART 2 DEFINITIONS LOADED")
print(f"{MODULE_NAME}: PART 3 DEFINITIONS LOADED")


# =============================================================================
# PART 4 — DIAGNOSTICS / HEALTH SERVER / MAIN
# =============================================================================


def run_diagnostics() -> RuntimeState:

    global REAL_WRITE_COUNT

    global DEMO_WRITE_COUNT

    global NETWORK_WRITE_COUNT

    global WEBSOCKET_WRITE_COUNT

    global SYNTHETIC_DISPATCH_COUNT


    REAL_WRITE_COUNT = 0

    DEMO_WRITE_COUNT = 0

    NETWORK_WRITE_COUNT = 0

    WEBSOCKET_WRITE_COUNT = 0

    SYNTHETIC_DISPATCH_COUNT = 0


    test_path = Path(
        "r29_unit_b_test_state.json"
    )

    clean_temp_state(
        test_path
    )


    # =========================================================================
    # TEST 1
    # =========================================================================


    test_header(
        1,
        "R29 SAFETY CONFIGURATION",
    )


    pass_check(
        "Real Order Execution Disabled",
        LIVE_ORDER_EXECUTION is False,
    )


    pass_check(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION is False,
    )


    pass_check(
        "Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )


    pass_check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )


    pass_check(
        "WebSocket Writes Disabled",
        WEBSOCKET_WRITES_ENABLED is False,
    )


    # =========================================================================
    # TEST 2
    # =========================================================================


    test_header(
        2,
        "STRATEGY CONFIGURATION BINDING",
    )


    cfg = config_dict()

    fp = config_fingerprint()


    pass_check(
        "Strategy Symbol Bound",
        cfg["symbol"] == SYMBOL,
    )


    pass_check(
        "Margin Mode Is Isolated",
        cfg["margin_mode"] == "ISOLATED",
    )


    pass_check(
        "Planned Leverage Is 100x",
        cfg["planned_leverage"] == 100,
    )


    pass_check(
        "Initial Allocation Is Five Percent",
        cfg["initial_entry_percent"] == "5",
    )


    pass_check(
        "Maximum Fund Exposure Is Thirty Five Percent",
        cfg["max_fund_exposure_percent"] == "35",
    )


    pass_check(
        "Configuration Fingerprint Established",
        len(fp) == 64,
    )


    # =========================================================================
    # TEST 3
    # =========================================================================


    test_header(
        3,
        "READ-ONLY MARKET OBSERVATION",
    )


    market = MarketObservation(

        SYMBOL,

        "79357.4",

        now_ms(),
    )


    validate_market(
        market
    )


    pass_check(
        "Market Observation Accepted",
        True,
    )


    pass_check(
        "Market Source Is Synthetic Read-Only",
        market.source
        ==
        "SYNTHETIC_READ_ONLY",
    )


    expect_block(

        "Wrong Market Symbol Rejected",

        lambda:
            validate_market(
                MarketObservation(
                    "ETHUSDT",
                    "79357.4",
                    now_ms(),
                )
            ),

        "symbol mismatch",
    )


    expect_block(

        "Nonpositive Mark Price Rejected",

        lambda:
            validate_market(
                MarketObservation(
                    SYMBOL,
                    "0",
                    now_ms(),
                )
            ),

        "positive",
    )


    # =========================================================================
    # TEST 4
    # =========================================================================


    test_header(
        4,
        "READ-ONLY ACCOUNT OBSERVATION",
    )


    account = AccountObservation(

        "7.18945017",

        0,

        now_ms(),
    )


    validate_account(
        account
    )


    pass_check(
        "Account Observation Accepted",
        True,
    )


    pass_check(
        "Observed Position Count Is Zero",
        account.position_count == 0,
    )


    expect_block(

        "Negative Available Balance Rejected",

        lambda:
            validate_account(
                AccountObservation(
                    "-1",
                    0,
                    now_ms(),
                )
            ),

        "negative",
    )


    # =========================================================================
    # TEST 5
    # =========================================================================


    test_header(
        5,
        "STRATEGY SIGNAL VALIDATION",
    )


    long_signal = make_signal(
        "LONG"
    )


    short_signal = make_signal(
        "SHORT"
    )


    validate_signal(
        long_signal
    )


    validate_signal(
        short_signal
    )


    pass_check(
        "Long Signal Accepted",
        long_signal.direction == "LONG",
    )


    pass_check(
        "Short Signal Accepted",
        short_signal.direction == "SHORT",
    )


    expect_block(

        "Expired Signal Rejected",

        lambda:
            validate_signal(
                make_signal(
                    "LONG",
                    SIGNAL_EXPIRY_SECONDS + 1,
                )
            ),

        "expired",
    )


    expect_block(

        "Invalid Direction Rejected",

        lambda:
            make_signal(
                "FLAT"
            ),

        "invalid strategy direction",
    )


    # =========================================================================
    # TEST 6
    # =========================================================================


    test_header(
        6,
        "INITIAL ENTRY RISK PROJECTION",
    )


    risk = project_initial_risk(
        account,
        market,
    )


    pass_check(
        "Margin Budget Is Positive",
        dec(
            risk.margin_budget
        ) > 0,
    )


    pass_check(
        "Planned Notional Is Positive",
        dec(
            risk.planned_notional
        ) > 0,
    )


    pass_check(
        "Quantity Rounded To Step",
        dec(
            risk.rounded_quantity
        )
        %
        QTY_STEP
        ==
        0,
    )


    pass_check(
        "Rounded Quantity Meets Minimum",
        dec(
            risk.rounded_quantity
        )
        >=
        MIN_QTY,
    )


    pass_check(
        "Projected Margin Is Within Fund Cap",
        dec(
            risk.projected_margin
        )
        <=
        (
            dec(
                account.available_usdt
            )
            *
            MAX_FUND_EXPOSURE_PERCENT
            /
            Decimal("100")
        ),
    )


    # =========================================================================
    # TEST 7
    # =========================================================================


    test_header(
        7,
        "LONG DECISION ENVELOPE",
    )


    long_decision = build_decision(
        long_signal,
        risk,
    )


    validate_decision(
        long_decision
    )


    pass_check(
        "Long Decision Uses BUY",
        long_decision.side == "BUY",
    )


    pass_check(
        "Long Decision Uses LONG Position Side",
        long_decision.position_side == "LONG",
    )


    pass_check(
        "Long Decision Is Non-Executable",
        long_decision.executable is False,
    )


    pass_check(
        "Long Decision Is Frozen",
        long_decision.state == "FROZEN",
    )


    pass_check(
        "Long Decision Payload Hash Established",
        len(
            long_decision.payload_hash
        )
        ==
        64,
    )


    # =========================================================================
    # TEST 8
    # =========================================================================


    test_header(
        8,
        "SHORT DECISION ENVELOPE",
    )


    short_decision = build_decision(
        short_signal,
        risk,
    )


    validate_decision(
        short_decision
    )


    pass_check(
        "Short Decision Uses SELL",
        short_decision.side == "SELL",
    )


    pass_check(
        "Short Decision Uses SHORT Position Side",
        short_decision.position_side == "SHORT",
    )


    pass_check(
        "Short Decision Is Non-Executable",
        short_decision.executable is False,
    )


    pass_check(
        "Short Decision Is Synthetic-Only",
        short_decision.synthetic_only is True,
    )


    # =========================================================================
    # TEST 9
    # =========================================================================


    test_header(
        9,
        "DECISION TAMPER REJECTION",
    )


    tampered = DecisionEnvelope(
        **{
            **asdict(
                long_decision
            ),

            "executable":
                True,
        }
    )


    expect_block(

        "Executable Decision Rejected",

        lambda:
            validate_decision(
                tampered
            ),

        "unexpectedly executable",
    )


    tampered_cfg = DecisionEnvelope(
        **{
            **asdict(
                long_decision
            ),

            "config_fingerprint":
                "0" * 64,
        }
    )


    expect_block(

        "Wrong Configuration Binding Rejected",

        lambda:
            validate_decision(
                tampered_cfg
            ),

        "fingerprint mismatch",
    )


    # =========================================================================
    # TEST 10
    # =========================================================================


    test_header(
        10,
        "REAL/DEMO/WEBSOCKET WRITE FIREBREAKS",
    )


    before = (

        REAL_WRITE_COUNT,

        DEMO_WRITE_COUNT,

        NETWORK_WRITE_COUNT,

        WEBSOCKET_WRITE_COUNT,
    )


    expect_block(

        "Real HTTP Write Blocked",

        real_http_write,

        "REAL network write blocked",
    )


    expect_block(

        "Demo HTTP Write Blocked",

        demo_http_write,

        "DEMO network write blocked",
    )


    expect_block(

        "WebSocket Write Blocked",

        websocket_write,

        "WebSocket write blocked",
    )


    pass_check(
        "Firebreak Interception Counters Advanced",
        (
            REAL_WRITE_COUNT,
            DEMO_WRITE_COUNT,
            NETWORK_WRITE_COUNT,
            WEBSOCKET_WRITE_COUNT,
        )
        !=
        before,
    )


    # Interception counters are reset.
    #
    # The calls above are local safety probes.
    # No network call was transmitted.


    REAL_WRITE_COUNT = 0

    DEMO_WRITE_COUNT = 0

    NETWORK_WRITE_COUNT = 0

    WEBSOCKET_WRITE_COUNT = 0


    # =========================================================================
    # TEST 11
    # =========================================================================


    test_header(
        11,
        "ACCOUNT MUTATION FIREBREAKS",
    )


    expect_block(

        "Leverage Mutation Blocked",

        leverage_mutation,

        "leverage mutation disabled",
    )


    expect_block(

        "Margin Mutation Blocked",

        margin_mutation,

        "margin mutation disabled",
    )


    expect_block(

        "Position Mutation Blocked",

        position_mutation,

        "position mutation disabled",
    )


    expect_block(

        "Account Mutation Blocked",

        account_mutation,

        "account mutation disabled",
    )


    # =========================================================================
    # TEST 12
    # =========================================================================


    test_header(
        12,
        "SYNTHETIC DECISION TRANSPORT",
    )


    receipt = synthetic_transport(
        long_decision
    )


    pass_check(
        "Synthetic Receipt Accepted",
        receipt["accepted"] is True,
    )


    pass_check(
        "Synthetic Receipt Reports No Transmission",
        receipt["transmitted"] is False,
    )


    pass_check(
        "Synthetic Transport Exact",
        receipt["transport"]
        ==
        "SYNTHETIC_ONLY",
    )


    pass_check(
        "Decision ID Preserved",
        receipt["decision_id"]
        ==
        long_decision.decision_id,
    )


    pass_check(
        "Decision Payload Hash Preserved",
        receipt["payload_hash"]
        ==
        long_decision.payload_hash,
    )


    pass_check(
        "Exactly One Synthetic Dispatch Added",
        SYNTHETIC_DISPATCH_COUNT == 1,
    )


    # =========================================================================
    # TEST 13
    # =========================================================================


    test_header(
        13,
        "DURABLE RUNTIME STATE",
    )


    state = boot_runtime(
        test_path
    )


    state.last_decision_id = (
        long_decision.decision_id
    )


    state.last_decision_hash = (
        long_decision.payload_hash
    )


    state.synthetic_dispatch_count = (
        SYNTHETIC_DISPATCH_COUNT
    )


    state.event_sequence += 1


    persist_state(
        state,
        test_path,
    )


    restored = load_state(
        test_path
    )


    pass_check(
        "Durable Runtime State Created",
        test_path.exists(),
    )


    pass_check(
        "Runtime ID Restored",
        restored.runtime_id
        ==
        state.runtime_id,
    )


    pass_check(
        "Decision ID Restored",
        restored.last_decision_id
        ==
        long_decision.decision_id,
    )


    pass_check(
        "Decision Hash Restored",
        restored.last_decision_hash
        ==
        long_decision.payload_hash,
    )


    pass_check(
        "Synthetic Dispatch Count Restored",
        restored.synthetic_dispatch_count
        ==
        1,
    )


    # =========================================================================
    # TEST 14
    # =========================================================================


    test_header(
        14,
        "RUNTIME STATE TAMPER REJECTION",
    )


    raw = json.loads(
        test_path.read_text(
            "utf-8"
        )
    )


    raw["generation"] += 99


    test_path.write_text(

        stable_json(
            raw
        ),

        "utf-8",
    )


    expect_block(

        "Tampered Runtime State Rejected",

        lambda:
            load_state(
                test_path
            ),

        "integrity seal mismatch",
    )


    persist_state(
        state,
        test_path,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================


    test_header(
        15,
        "RESTART CONTINUITY",
    )


    restarted = boot_runtime(
        test_path
    )


    pass_check(
        "Runtime Identity Survives Restart",
        restarted.runtime_id
        ==
        state.runtime_id,
    )


    pass_check(
        "Generation Survives Same-Configuration Restart",
        restarted.generation
        ==
        state.generation,
    )


    pass_check(
        "Recovery Epoch Advances On Restart",
        restarted.recovery_epoch
        ==
        state.recovery_epoch + 1,
    )


    pass_check(
        "Boot Counter Advances On Restart",
        restarted.boot_count
        ==
        state.boot_count + 1,
    )


    pass_check(
        "Decision Binding Survives Restart",
        restarted.last_decision_id
        ==
        long_decision.decision_id,
    )


    pass_check(
        "Real Order Counter Remains Zero",
        restarted.real_order_count == 0,
    )


    pass_check(
        "Demo Order Counter Remains Zero",
        restarted.demo_order_count == 0,
    )


    pass_check(
        "Network Write Counter Remains Zero",
        restarted.network_write_count == 0,
    )


    # =========================================================================
    # TEST 16
    # =========================================================================


    test_header(
        16,
        "TERMINAL UNIT B SAFETY INVARIANTS",
    )


    final = load_state(
        test_path
    )


    pass_check(
        "Final Durable Runtime State Validates",
        True,
    )


    pass_check(
        "Strategy Decision Layer Is Non-Executable",
        (
            long_decision.executable is False
            and
            short_decision.executable is False
        ),
    )


    pass_check(
        "Real Order Execution Remains Disabled",
        LIVE_ORDER_EXECUTION is False,
    )


    pass_check(
        "Demo Order Execution Remains Disabled",
        DEMO_ORDER_EXECUTION is False,
    )


    pass_check(
        "All Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED is False,
    )


    pass_check(
        "Synthetic Transport Remains Exclusive",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )


    pass_check(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )


    pass_check(
        "Margin Mutation Remains Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )


    pass_check(
        "Position Mutation Remains Disabled",
        POSITION_MUTATION_ENABLED is False,
    )


    pass_check(
        "Account Mutation Remains Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )


    pass_check(
        "Final Real Order Count Is Zero",
        final.real_order_count == 0,
    )


    pass_check(
        "Final Demo Order Count Is Zero",
        final.demo_order_count == 0,
    )


    pass_check(
        "Final Network Write Count Is Zero",
        final.network_write_count == 0,
    )


    # Remove disposable diagnostic state.


    clean_temp_state(
        test_path
    )


    # =========================================================================
    # SERVICE RUNTIME STATE
    # =========================================================================


    service_state = boot_runtime(
        STATE_PATH
    )


    service_state.last_decision_id = (
        long_decision.decision_id
    )


    service_state.last_decision_hash = (
        long_decision.payload_hash
    )


    # Diagnostic synthetic transport does not represent a pending
    # service execution.


    service_state.synthetic_dispatch_count = 0


    service_state.real_order_count = 0

    service_state.demo_order_count = 0

    service_state.network_write_count = 0

    service_state.websocket_write_count = 0


    service_state.event_sequence += 1


    persist_state(
        service_state,
        STATE_PATH,
    )


    return service_state


# =============================================================================
# HEALTH SERVER
# =============================================================================


class HealthHandler(
    socketserver.BaseRequestHandler
):

    def handle(self) -> None:

        try:

            self.request.recv(
                2048
            )


            body = stable_json(
                {

                    "ok":
                        True,

                    "module":
                        MODULE_NAME,

                    "synthetic_only":
                        SYNTHETIC_TRANSPORT_ONLY,

                    "network_writes":
                        NETWORK_WRITES_ENABLED,

                    "real_orders":
                        LIVE_ORDER_EXECUTION,

                    "demo_orders":
                        DEMO_ORDER_EXECUTION,
                }
            ).encode(
                "utf-8"
            )


            response = (

                b"HTTP/1.1 200 OK\r\n"

                b"Content-Type: application/json\r\n"

                +
                (
                    f"Content-Length: "
                    f"{len(body)}\r\n"
                ).encode(
                    "ascii"
                )

                +
                b"Connection: close\r\n\r\n"

                +
                body
            )


            self.request.sendall(
                response
            )

        except Exception:

            pass


class ThreadingTCPServer(
    socketserver.ThreadingTCPServer
):

    allow_reuse_address = True

    daemon_threads = True


def start_health_server() -> ThreadingTCPServer:

    server = ThreadingTCPServer(

        (
            "0.0.0.0",
            HEALTH_PORT,
        ),

        HealthHandler,
    )


    thread = threading.Thread(

        target=
            server.serve_forever,

        daemon=
            True,
    )


    thread.start()


    return server


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:

    print(SEP)

    print(
        f"{MODULE_NAME}: STARTING DIAGNOSTICS"
    )

    print(SEP)


    state = run_diagnostics()


    print(SEP)

    print(
        f"{MODULE_NAME}: ALL DIAGNOSTICS PASSED"
    )

    print(SEP)


    print(
        "NO REAL ORDER WAS SENT"
    )


    print(
        "NO DEMO ORDER WAS SENT"
    )


    print(
        "NO NETWORK WRITE WAS ATTEMPTED"
    )


    print(
        f"{MODULE_NAME}: "
        f"TEST GROUPS EXECUTED = "
        f"{TEST_GROUPS}"
    )


    print(
        f"{MODULE_NAME}: "
        f"PASS ASSERTIONS = "
        f"{PASS_ASSERTIONS}"
    )


    server = start_health_server()


    print(
        f"{MODULE_NAME}: "
        f"HEALTH SERVER LISTENING ON PORT "
        f"{HEALTH_PORT}"
    )


    heartbeat = 1


    try:

        while True:

            print(

                f"{MODULE_NAME}: "
                f"HEARTBEAT {heartbeat} | "

                f"synthetic-only="
                f"{SYNTHETIC_TRANSPORT_ONLY} | "

                f"network-writes="
                f"{NETWORK_WRITES_ENABLED} | "

                f"generation="
                f"{state.generation} | "

                f"recovery-epoch="
                f"{state.recovery_epoch}"
            )


            heartbeat += 1


            time.sleep(
                30
            )

    except KeyboardInterrupt:

        pass

    finally:

        server.shutdown()

        server.server_close()


if __name__ == "__main__":

    main()
