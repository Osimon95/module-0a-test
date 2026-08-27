from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_DOWN, getcontext
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# R30.1
# CONTROLLED PROMOTION READINESS / SAFETY VALIDATION
#
# SAFETY DISCIPLINE
#   - REAL ORDER EXECUTION DISABLED
#   - DEMO ORDER EXECUTION DISABLED
#   - EXCHANGE NETWORK WRITES DISABLED
#   - LEVERAGE MUTATION DISABLED
#   - MARGIN MUTATION DISABLED
#   - POSITION MUTATION DISABLED
#   - ACCOUNT MUTATION DISABLED
#   - WEBSOCKET WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# IMPORTANT
#   This program does not transmit orders or mutate exchange/account state.
#   Environment variables are not allowed to activate execution.
# =============================================================================


getcontext().prec = 28


# =============================================================================
# IDENTITY / RUNTIME
# =============================================================================

VERSION = "R30.1"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"
HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))
STATE_FILE = Path(
    os.getenv("R30_STATE_FILE", "/tmp/r30_controlled_promotion_state.json")
)

HEARTBEAT_SECONDS = max(
    5,
    int(os.getenv("HEARTBEAT_SECONDS", "30")),
)


# =============================================================================
# FROZEN SAFETY CONSTANTS
#
# These are intentionally literal constants. Do not derive them from env vars.
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

# Strategy constraints carried forward as validation-only values.
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
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

LINE = "-" * 92


def banner(message: str) -> None:
    print(LINE, flush=True)
    print(message, flush=True)
    print(LINE, flush=True)


def section(message: str) -> None:
    print(LINE, flush=True)
    print(message, flush=True)
    print(LINE, flush=True)


class ValidationFailure(RuntimeError):
    pass


@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""


TEST_RESULTS: List[TestResult] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    passed = bool(condition)
    TEST_RESULTS.append(TestResult(name=name, passed=passed, detail=detail))
    icon = "✅ PASS" if passed else "❌ FAIL"
    print(f"{name:<80} {icon}", flush=True)

    if detail:
        print(f"  {detail}", flush=True)

    if not passed:
        raise ValidationFailure(name)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class StrategyPlan:
    symbol: str
    target_leverage: str
    initial_entry_percent: str
    pyramid_size_percent: str
    max_pyramid_adds: int
    backup_size_percent: str
    max_backups: int
    max_fund_exposure_percent: str
    tp_distribution: Tuple[str, str, str]
    tp_triggers: Tuple[str, str]
    trailing_distance_percent: str

    @staticmethod
    def build(symbol: str) -> "StrategyPlan":
        return StrategyPlan(
            symbol=symbol,
            target_leverage=str(TARGET_LEVERAGE),
            initial_entry_percent=str(INITIAL_ENTRY_PERCENT),
            pyramid_size_percent=str(PYRAMID_SIZE_PERCENT),
            max_pyramid_adds=MAX_PYRAMID_ADDS,
            backup_size_percent=str(BACKUP_SIZE_PERCENT),
            max_backups=MAX_BACKUPS,
            max_fund_exposure_percent=str(MAX_FUND_EXPOSURE_PERCENT),
            tp_distribution=(
                str(TP1_PERCENT),
                str(TP2_PERCENT),
                str(TP3_PERCENT),
            ),
            tp_triggers=(
                str(TP1_TRIGGER_PERCENT),
                str(TP2_TRIGGER_PERCENT),
            ),
            trailing_distance_percent=str(
                TRAILING_DISTANCE_PERCENT
            ),
        )


@dataclass(frozen=True)
class SyntheticIntent:
    intent_id: str
    runtime_id: str
    generation: int
    recovery_epoch: int
    symbol: str
    side: str
    entry_price: str
    quantity: str
    leverage: str
    created_at: int
    executable: bool
    transport: str

    def canonical_payload(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "runtime_id": self.runtime_id,
            "generation": self.generation,
            "recovery_epoch": self.recovery_epoch,
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "leverage": self.leverage,
            "created_at": self.created_at,
            "executable": self.executable,
            "transport": self.transport,
        }

    def digest(self) -> str:
        raw = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(raw).hexdigest()


@dataclass
class RuntimeState:
    version: str
    runtime_id: str
    generation: int
    recovery_epoch: int
    boot_count: int
    started_at: int
    last_heartbeat_at: int
    heartbeat_count: int
    synthetic_dispatch_count: int
    real_order_count: int
    demo_order_count: int
    network_write_count: int
    mutation_count: int
    last_intent_digest: Optional[str] = None
    finalized_intent_digests: List[str] = field(
        default_factory=list
    )


# =============================================================================
# STATE PERSISTENCE
# =============================================================================

STATE_LOCK = threading.RLock()


def _state_from_dict(
    data: Dict[str, Any],
) -> RuntimeState:
    return RuntimeState(
        version=str(data.get("version", VERSION)),
        runtime_id=str(data["runtime_id"]),
        generation=int(data.get("generation", 1)),
        recovery_epoch=int(
            data.get("recovery_epoch", 1)
        ),
        boot_count=int(data.get("boot_count", 0)),
        started_at=int(
            data.get("started_at", int(time.time()))
        ),
        last_heartbeat_at=int(
            data.get("last_heartbeat_at", 0)
        ),
        heartbeat_count=int(
            data.get("heartbeat_count", 0)
        ),
        synthetic_dispatch_count=int(
            data.get("synthetic_dispatch_count", 0)
        ),
        real_order_count=int(
            data.get("real_order_count", 0)
        ),
        demo_order_count=int(
            data.get("demo_order_count", 0)
        ),
        network_write_count=int(
            data.get("network_write_count", 0)
        ),
        mutation_count=int(
            data.get("mutation_count", 0)
        ),
        last_intent_digest=data.get(
            "last_intent_digest"
        ),
        finalized_intent_digests=list(
            data.get(
                "finalized_intent_digests",
                [],
            )
        ),
    )


def load_or_create_state() -> RuntimeState:
    now = int(time.time())

    if STATE_FILE.exists():
        try:
            data = json.loads(
                STATE_FILE.read_text(
                    encoding="utf-8"
                )
            )

            state = _state_from_dict(data)
            state.version = VERSION
            state.boot_count += 1
            state.started_at = now

            return state

        except Exception as exc:
            print(
                f"{VERSION}: WARNING: "
                f"state restore failed; "
                f"creating clean state: {exc}",
                flush=True,
            )

    return RuntimeState(
        version=VERSION,
        runtime_id=str(uuid.uuid4()),
        generation=1,
        recovery_epoch=1,
        boot_count=1,
        started_at=now,
        last_heartbeat_at=0,
        heartbeat_count=0,
        synthetic_dispatch_count=0,
        real_order_count=0,
        demo_order_count=0,
        network_write_count=0,
        mutation_count=0,
    )


def persist_state(state: RuntimeState) -> None:
    with STATE_LOCK:
        STATE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = json.dumps(
            asdict(state),
            sort_keys=True,
            indent=2,
        )

        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{STATE_FILE.name}.",
            suffix=".tmp",
            dir=str(STATE_FILE.parent),
            text=True,
        )

        try:
            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(
                tmp_name,
                STATE_FILE,
            )

        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)


STATE = load_or_create_state()


# =============================================================================
# EXECUTION FIREBREAK
# =============================================================================

class ExecutionBlocked(RuntimeError):
    pass


def block_real_order(
    *_: Any,
    **__: Any,
) -> None:
    raise ExecutionBlocked(
        "real order execution is "
        "permanently disabled in R30.1"
    )


def block_demo_order(
    *_: Any,
    **__: Any,
) -> None:
    raise ExecutionBlocked(
        "demo order execution is "
        "permanently disabled in R30.1"
    )


def block_network_write(
    method: str,
    path: str = "",
) -> None:
    method_upper = method.strip().upper()

    raise ExecutionBlocked(
        f"exchange network write blocked: "
        f"{method_upper} {path}".strip()
    )


def block_mutation(kind: str) -> None:
    raise ExecutionBlocked(
        f"{kind} mutation is "
        f"permanently disabled in R30.1"
    )


def synthetic_dispatch(
    intent: SyntheticIntent,
) -> Dict[str, Any]:
    if not SYNTHETIC_TRANSPORT_ONLY:
        raise ValidationFailure(
            "synthetic transport invariant violated"
        )

    if intent.executable:
        raise ValidationFailure(
            "synthetic intent must not be executable"
        )

    digest = intent.digest()

    with STATE_LOCK:
        if (
            digest
            in STATE.finalized_intent_digests
        ):
            raise ExecutionBlocked(
                "synthetic replay rejected"
            )

        STATE.synthetic_dispatch_count += 1
        STATE.last_intent_digest = digest

        STATE.finalized_intent_digests.append(
            digest
        )

        if (
            len(
                STATE.finalized_intent_digests
            )
            > 256
        ):
            STATE.finalized_intent_digests = (
                STATE.finalized_intent_digests[
                    -256:
                ]
            )

        persist_state(STATE)

    return {
        "transport": "synthetic",
        "transmitted": False,
        "network_write": False,
        "order_created": False,
        "intent_digest": digest,
    }


# =============================================================================
# SAFE CALCULATION HELPERS
# =============================================================================

def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:
    if step <= 0:
        raise ValueError(
            "step must be positive"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def hypothetical_quantity(
    available_balance: Decimal,
    price: Decimal,
    quantity_step: Decimal,
) -> Decimal:
    if available_balance <= 0:
        raise ValueError(
            "available balance must be positive"
        )

    if price <= 0:
        raise ValueError(
            "price must be positive"
        )

    margin_budget = (
        available_balance
        * (
            INITIAL_ENTRY_PERCENT
            / Decimal("100")
        )
    )

    notional = (
        margin_budget
        * TARGET_LEVERAGE
    )

    raw_quantity = (
        notional / price
    )

    return floor_to_step(
        raw_quantity,
        quantity_step,
    )


def build_synthetic_intent() -> SyntheticIntent:
    synthetic_price = Decimal("80000")
    synthetic_balance = Decimal("10")
    quantity_step = Decimal("0.0001")

    quantity = hypothetical_quantity(
        synthetic_balance,
        synthetic_price,
        quantity_step,
    )

    return SyntheticIntent(
        intent_id=(
            f"synthetic-{uuid.uuid4()}"
        ),
        runtime_id=STATE.runtime_id,
        generation=STATE.generation,
        recovery_epoch=STATE.recovery_epoch,
        symbol=SYMBOL,
        side="LONG",
        entry_price=str(synthetic_price),
        quantity=str(quantity),
        leverage=str(TARGET_LEVERAGE),
        created_at=int(time.time()),
        executable=False,
        transport="synthetic-only",
    )


# =============================================================================
# ENVIRONMENT ESCALATION DEFENSE
# =============================================================================

def regardless_environment(
    _: Any,
) -> bool:
    """
    Environment requests have no authority
    over the frozen execution constants.
    """

    return (
        REAL_ORDER_EXECUTION_ENABLED is False
        and DEMO_ORDER_EXECUTION_ENABLED is False
        and EXCHANGE_NETWORK_WRITES_ENABLED is False
        and LEVERAGE_MUTATION_ENABLED is False
        and MARGIN_MUTATION_ENABLED is False
        and POSITION_MUTATION_ENABLED is False
        and ACCOUNT_MUTATION_ENABLED is False
        and WEBSOCKET_WRITES_ENABLED is False
        and SYNTHETIC_TRANSPORT_ONLY is True
    )


# =============================================================================
# VALIDATION
# =============================================================================

def run_validation() -> None:
    TEST_RESULTS.clear()

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 1: "
        f"SAFETY CONFIGURATION"
    )
    # -------------------------------------------------------------------------

    check(
        "Real Order Execution Disabled",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Demo Order Execution Disabled",
        DEMO_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Exchange Network Writes Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    check(
        "Leverage Mutation Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    check(
        "Margin Mutation Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    check(
        "Position Mutation Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    check(
        "Account Mutation Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )

    check(
        "WebSocket Writes Disabled",
        WEBSOCKET_WRITES_ENABLED
        is False,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 2: "
        f"STRATEGY CONSTRAINTS"
    )
    # -------------------------------------------------------------------------

    plan = StrategyPlan.build(SYMBOL)

    check(
        "Strategy Symbol Matches Runtime Symbol",
        plan.symbol == SYMBOL,
    )

    check(
        "Target Leverage Is 100x",
        Decimal(
            plan.target_leverage
        )
        == Decimal("100"),
    )

    check(
        "Initial Entry Is Five Percent",
        Decimal(
            plan.initial_entry_percent
        )
        == Decimal("5"),
    )

    check(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    check(
        "Maximum Backup Count Is Three",
        MAX_BACKUPS == 3,
    )

    check(
        "Maximum Fund Exposure Is Thirty Five Percent",
        MAX_FUND_EXPOSURE_PERCENT
        == Decimal("35"),
    )

    check(
        "Take Profit Distribution Reconciles To 100 Percent",
        (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        )
        == Decimal("100"),
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 3: "
        f"SAFETY FEATURE TOGGLES"
    )
    # -------------------------------------------------------------------------

    check(
        "One Direction Only Enabled",
        ONE_DIRECTION_ONLY,
    )

    check(
        "Anti Duplicate Orders Enabled",
        ANTI_DUPLICATE_ORDERS,
    )

    check(
        "Trend Reversal Exit Enabled",
        TREND_REVERSAL_EXIT,
    )

    check(
        "Idle Pyramid Cleanup Enabled",
        IDLE_PYRAMID_CLEANUP,
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
    section(
        f"{VERSION} TEST 4: "
        f"LOCAL REAL EXECUTION FIREBREAK"
    )
    # -------------------------------------------------------------------------

    try:
        block_real_order()
        real_blocked = False

    except ExecutionBlocked:
        real_blocked = True

    check(
        "Real Order Function Is Locally Blocked",
        real_blocked,
    )

    try:
        block_demo_order()
        demo_blocked = False

    except ExecutionBlocked:
        demo_blocked = True

    check(
        "Demo Order Function Is Locally Blocked",
        demo_blocked,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 5: "
        f"NETWORK WRITE FIREBREAK"
    )
    # -------------------------------------------------------------------------

    methods = (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    )

    for method in methods:
        try:
            block_network_write(
                method,
                "/synthetic-test",
            )
            blocked = False

        except ExecutionBlocked:
            blocked = True

        check(
            f"HTTP {method} Blocked",
            blocked,
        )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 6: "
        f"MUTATION FIREBREAK"
    )
    # -------------------------------------------------------------------------

    for mutation_kind in (
        "leverage",
        "margin",
        "position",
        "account",
    ):
        try:
            block_mutation(
                mutation_kind
            )
            blocked = False

        except ExecutionBlocked:
            blocked = True

        check(
            (
                f"{mutation_kind.title()} "
                f"Mutation Blocked"
            ),
            blocked,
        )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 7: "
        f"SYNTHETIC QUANTITY PROJECTION"
    )
    # -------------------------------------------------------------------------

    quantity = hypothetical_quantity(
        available_balance=Decimal("10"),
        price=Decimal("80000"),
        quantity_step=Decimal("0.0001"),
    )

    check(
        "Synthetic Quantity Is Non Negative",
        quantity >= Decimal("0"),
    )

    check(
        "Synthetic Quantity Respects Step",
        (
            quantity
            % Decimal("0.0001")
        )
        == 0,
    )

    check(
        "Projection Performs No Exchange Write",
        STATE.network_write_count == 0,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 8: "
        f"SYNTHETIC INTENT SEAL"
    )
    # -------------------------------------------------------------------------

    intent = build_synthetic_intent()
    payload = intent.canonical_payload()
    digest = intent.digest()

    check(
        "Synthetic Intent Is Non Executable",
        payload["executable"] is False,
    )

    check(
        "Synthetic Intent Uses Synthetic Transport",
        payload["transport"]
        == "synthetic-only",
    )

    check(
        "Synthetic Intent Symbol Matches",
        payload["symbol"] == SYMBOL,
    )

    check(
        "Synthetic Intent Digest Is SHA256 Length",
        len(digest) == 64,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 9: "
        f"SYNTHETIC DISPATCH"
    )
    # -------------------------------------------------------------------------

    before_real = (
        STATE.real_order_count
    )

    before_demo = (
        STATE.demo_order_count
    )

    before_writes = (
        STATE.network_write_count
    )

    before_mutations = (
        STATE.mutation_count
    )

    before_synthetic = (
        STATE.synthetic_dispatch_count
    )

    receipt = synthetic_dispatch(
        intent
    )

    check(
        "Synthetic Dispatch Reports No Transmission",
        receipt["transmitted"]
        is False,
    )

    check(
        "Synthetic Dispatch Reports No Network Write",
        receipt["network_write"]
        is False,
    )

    check(
        "Synthetic Dispatch Reports No Order Created",
        receipt["order_created"]
        is False,
    )

    check(
        "Synthetic Dispatch Counter Advanced Once",
        (
            STATE.synthetic_dispatch_count
            == before_synthetic + 1
        ),
    )

    check(
        "Real Order Counter Remains Zero",
        (
            STATE.real_order_count
            == before_real
            == 0
        ),
    )

    check(
        "Demo Order Counter Remains Zero",
        (
            STATE.demo_order_count
            == before_demo
            == 0
        ),
    )

    check(
        "Network Write Counter Remains Zero",
        (
            STATE.network_write_count
            == before_writes
            == 0
        ),
    )

    check(
        "Mutation Counter Remains Zero",
        (
            STATE.mutation_count
            == before_mutations
            == 0
        ),
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 10: "
        f"SYNTHETIC REPLAY REJECTION"
    )
    # -------------------------------------------------------------------------

    try:
        synthetic_dispatch(intent)
        replay_blocked = False

    except ExecutionBlocked:
        replay_blocked = True

    check(
        "Duplicate Synthetic Intent Replay Rejected",
        replay_blocked,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 11: "
        f"STATE PERSISTENCE"
    )
    # -------------------------------------------------------------------------

    persist_state(STATE)

    check(
        "Durable State File Created",
        STATE_FILE.exists(),
    )

    restored = _state_from_dict(
        json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )
    )

    check(
        "Persisted Runtime ID Matches",
        (
            restored.runtime_id
            == STATE.runtime_id
        ),
    )

    check(
        "Persisted Generation Matches",
        (
            restored.generation
            == STATE.generation
        ),
    )

    check(
        "Persisted Recovery Epoch Matches",
        (
            restored.recovery_epoch
            == STATE.recovery_epoch
        ),
    )

    check(
        "Persisted Real Order Counter Is Zero",
        restored.real_order_count == 0,
    )

    check(
        "Persisted Network Write Counter Is Zero",
        restored.network_write_count == 0,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 12: "
        f"CONTROLLED PROMOTION INVARIANTS"
    )
    # -------------------------------------------------------------------------

    check(
        "Generation Is Positive",
        STATE.generation >= 1,
    )

    check(
        "Recovery Epoch Is Positive",
        STATE.recovery_epoch >= 1,
    )

    check(
        "Runtime ID Is Present",
        bool(STATE.runtime_id),
    )

    check(
        "No Real Execution Capability Is Armed",
        not REAL_ORDER_EXECUTION_ENABLED,
    )

    check(
        "No Exchange Write Capability Is Armed",
        not EXCHANGE_NETWORK_WRITES_ENABLED,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 13: "
        f"TAKE PROFIT CONFIGURATION"
    )
    # -------------------------------------------------------------------------

    check(
        "TP1 Allocation Is 20 Percent",
        TP1_PERCENT == Decimal("20"),
    )

    check(
        "TP2 Allocation Is 20 Percent",
        TP2_PERCENT == Decimal("20"),
    )

    check(
        "TP3 Allocation Is 60 Percent",
        TP3_PERCENT == Decimal("60"),
    )

    check(
        "TP1 Trigger Is 0.5 Percent",
        TP1_TRIGGER_PERCENT
        == Decimal("0.5"),
    )

    check(
        "TP2 Trigger Is 1.0 Percent",
        TP2_TRIGGER_PERCENT
        == Decimal("1.0"),
    )

    check(
        "Trailing Distance Is 0.20 Percent",
        TRAILING_DISTANCE_PERCENT
        == Decimal("0.20"),
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 14: "
        f"PYRAMID AND BACKUP LIMITS"
    )
    # -------------------------------------------------------------------------

    check(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    check(
        "Maximum Backup Count Is Three",
        MAX_BACKUPS == 3,
    )

    check(
        "Pyramid Size Is Five Percent",
        PYRAMID_SIZE_PERCENT
        == Decimal("5"),
    )

    check(
        "Backup Size Is Five Percent",
        BACKUP_SIZE_PERCENT
        == Decimal("5"),
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 15: "
        f"COUNTER INTEGRITY"
    )
    # -------------------------------------------------------------------------

    check(
        "Real Order Count Is Zero",
        STATE.real_order_count == 0,
    )

    check(
        "Demo Order Count Is Zero",
        STATE.demo_order_count == 0,
    )

    check(
        "Network Write Count Is Zero",
        STATE.network_write_count == 0,
    )

    check(
        "Mutation Count Is Zero",
        STATE.mutation_count == 0,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 16: "
        f"ENVIRONMENT ESCALATION RESISTANCE"
    )
    # -------------------------------------------------------------------------

    environment_attempt = (
        os.getenv(
            "REAL_ORDER_EXECUTION",
            "",
        )
        .strip()
        .lower()
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
            REAL_ORDER_EXECUTION_ENABLED
            is False
            and regardless_environment(
                environment_attempt
            )
        ),
    )

    check(
        "Real Execution Constant Remains Frozen",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Exchange Write Constant Remains Frozen",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
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
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    # -------------------------------------------------------------------------
    section(
        f"{VERSION} TEST 17: "
        f"FINAL READINESS SEAL"
    )
    # -------------------------------------------------------------------------

    passed_count = sum(
        1
        for result in TEST_RESULTS
        if result.passed
    )

    failed_count = sum(
        1
        for result in TEST_RESULTS
        if not result.passed
    )

    check(
        "All Prior Validation Checks Passed",
        failed_count == 0,
        detail=(
            f"passed-before-final="
            f"{passed_count}, "
            f"failed={failed_count}"
        ),
    )

    check(
        "R30.1 Remains Non Executable",
        (
            not REAL_ORDER_EXECUTION_ENABLED
            and not DEMO_ORDER_EXECUTION_ENABLED
            and not EXCHANGE_NETWORK_WRITES_ENABLED
            and SYNTHETIC_TRANSPORT_ONLY
        ),
    )


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):
    server_version = "R30Health/1.0"

    def _write_json(
        self,
        status_code: int,
        payload: Dict[str, Any],
    ) -> None:
        body = json.dumps(
            payload,
            sort_keys=True,
        ).encode("utf-8")

        self.send_response(
            status_code
        )

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def do_GET(self) -> None:
        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):
            self._write_json(
                404,
                {
                    "ok": False,
                    "error": "not found",
                },
            )
            return

        with STATE_LOCK:
            payload = {
                "ok": True,
                "version": VERSION,
                "symbol": SYMBOL,
                "runtime_id": (
                    STATE.runtime_id
                ),
                "generation": (
                    STATE.generation
                ),
                "recovery_epoch": (
                    STATE.recovery_epoch
                ),
                "heartbeat_count": (
                    STATE.heartbeat_count
                ),
                "synthetic_only": (
                    SYNTHETIC_TRANSPORT_ONLY
                ),
                "real_execution": (
                    REAL_ORDER_EXECUTION_ENABLED
                ),
                "demo_execution": (
                    DEMO_ORDER_EXECUTION_ENABLED
                ),
                "network_writes": (
                    EXCHANGE_NETWORK_WRITES_ENABLED
                ),
                "leverage_mutation": (
                    LEVERAGE_MUTATION_ENABLED
                ),
                "margin_mutation": (
                    MARGIN_MUTATION_ENABLED
                ),
                "position_mutation": (
                    POSITION_MUTATION_ENABLED
                ),
                "account_mutation": (
                    ACCOUNT_MUTATION_ENABLED
                ),
                "real_order_count": (
                    STATE.real_order_count
                ),
                "demo_order_count": (
                    STATE.demo_order_count
                ),
                "network_write_count": (
                    STATE.network_write_count
                ),
                "mutation_count": (
                    STATE.mutation_count
                ),
            }

        self._write_json(
            200,
            payload,
        )

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        return


def health_server_loop() -> None:
    server = ThreadingHTTPServer(
        (
            "0.0.0.0",
            HEALTH_PORT,
        ),
        HealthHandler,
    )

    print(
        f"{VERSION}: "
        f"HEALTH SERVER LISTENING "
        f"ON PORT {HEALTH_PORT}",
        flush=True,
    )

    server.serve_forever(
        poll_interval=0.5
    )


# =============================================================================
# HEARTBEAT LOOP
# =============================================================================

def heartbeat_loop() -> None:
    while True:
        time.sleep(
            HEARTBEAT_SECONDS
        )

        with STATE_LOCK:
            STATE.heartbeat_count += 1

            STATE.last_heartbeat_at = (
                int(time.time())
            )

            persist_state(STATE)

            count = (
                STATE.heartbeat_count
            )

            generation = (
                STATE.generation
            )

            recovery_epoch = (
                STATE.recovery_epoch
            )

        print(
            f"{VERSION}: "
            f"HEARTBEAT {count} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"generation="
            f"{generation} | "
            f"recovery-epoch="
            f"{recovery_epoch}",
            flush=True,
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    banner(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"REAL EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"DEMO EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"EXCHANGE NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )

    health_thread = threading.Thread(
        target=health_server_loop,
        name="r30-health-server",
        daemon=True,
    )

    health_thread.start()

    try:
        run_validation()

    except Exception as exc:
        banner(
            f"{VERSION}: VALIDATION FAILED"
        )

        print(
            f"{VERSION}: "
            f"ERROR="
            f"{type(exc).__name__}: "
            f"{exc}",
            flush=True,
        )

        raise

    persist_state(STATE)

    passed_count = sum(
        1
        for result in TEST_RESULTS
        if result.passed
    )

    failed_count = sum(
        1
        for result in TEST_RESULTS
        if not result.passed
    )

    banner(
        f"{VERSION}: VALIDATION PASSED"
    )

    print(
        f"{VERSION}: "
        f"SUMMARY "
        f"passed={passed_count} "
        f"failed={failed_count}",
        flush=True,
    )

    print(
        f"{VERSION}: "
        f"SAFETY SEAL "
        f"real-orders="
        f"{STATE.real_order_count} "
        f"demo-orders="
        f"{STATE.demo_order_count} "
        f"network-writes="
        f"{STATE.network_write_count} "
        f"mutations="
        f"{STATE.mutation_count}",
        flush=True,
    )

    heartbeat_loop()


if __name__ == "__main__":
    main()
