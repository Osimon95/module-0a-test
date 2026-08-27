from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# =============================================================================
# R31A
# CONTROLLED PROMOTION GATE / STATE-MACHINE BASELINE
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
#   R30.1 safety baseline
#       ->
#   bounded promotion state machine
#       ->
#   synthetic approval / commit / rollback transitions
#       ->
#   replay resistance
#       ->
#   durable restart-safe state
#       ->
#   final non-executable readiness seal
# =============================================================================


VERSION = "R31A"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"
HEALTH_PORT = int(os.getenv("PORT", "10000"))
STATE_FILE = Path(
    os.getenv(
        "R31A_STATE_FILE",
        "/tmp/r31a_promotion_gate_state.json",
    )
)


# =============================================================================
# FROZEN EXECUTION SAFETY CONSTANTS
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
# STRATEGY CONSTRAINTS PRESERVED FROM R30.1
# =============================================================================

TARGET_LEVERAGE = 100

INITIAL_ENTRY_PERCENT = 5

MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = 5

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = 5

MAX_FUND_EXPOSURE_PERCENT = 35

TP1_ALLOCATION_PERCENT = 20
TP2_ALLOCATION_PERCENT = 20
TP3_ALLOCATION_PERCENT = 60

TP1_TRIGGER_PERCENT = 0.5
TP2_TRIGGER_PERCENT = 1.0
TRAILING_DISTANCE_PERCENT = 0.20

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

HEARTBEAT_SECONDS = 30


# =============================================================================
# FORMATTING / TEST ACCOUNTING
# =============================================================================

WIDTH = 92

passed = 0
failed = 0


def line() -> None:
    print("-" * WIDTH, flush=True)


def section(title: str) -> None:
    line()
    print(title, flush=True)
    line()


def check(name: str, condition: bool) -> None:
    global passed
    global failed

    if condition:
        passed += 1
        marker = "✅ PASS"
    else:
        failed += 1
        marker = "❌ FAIL"

    print(
        f"{name:<80} {marker}",
        flush=True,
    )


# =============================================================================
# SAFETY EXCEPTION
# =============================================================================

class SafetyViolation(RuntimeError):
    pass


# =============================================================================
# HARD LOCAL EXECUTION FIREBREAKS
# =============================================================================

def real_order(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: "
        "real order execution is disabled"
    )


def demo_order(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: "
        "demo order execution is disabled"
    )


# =============================================================================
# HARD NETWORK WRITE FIREBREAKS
# =============================================================================

def http_post(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: HTTP POST is disabled"
    )


def http_put(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: HTTP PUT is disabled"
    )


def http_patch(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: HTTP PATCH is disabled"
    )


def http_delete(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: HTTP DELETE is disabled"
    )


# =============================================================================
# HARD MUTATION FIREBREAKS
# =============================================================================

def mutate_leverage(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: "
        "leverage mutation is disabled"
    )


def mutate_margin(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: "
        "margin mutation is disabled"
    )


def mutate_position(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: "
        "position mutation is disabled"
    )


def mutate_account(
    *_: Any,
    **__: Any,
) -> None:
    raise SafetyViolation(
        "R31A local firebreak: "
        "account mutation is disabled"
    )


# =============================================================================
# PROMOTION PHASES
# =============================================================================

class PromotionPhase(str, Enum):
    BASELINE = "BASELINE"
    CANDIDATE = "CANDIDATE"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    SEALED = "SEALED"


# =============================================================================
# ALLOWED PROMOTION TRANSITIONS
# =============================================================================

ALLOWED_TRANSITIONS: Dict[
    PromotionPhase,
    Set[PromotionPhase],
] = {
    PromotionPhase.BASELINE: {
        PromotionPhase.CANDIDATE,
    },

    PromotionPhase.CANDIDATE: {
        PromotionPhase.REVIEWED,
        PromotionPhase.ROLLED_BACK,
    },

    PromotionPhase.REVIEWED: {
        PromotionPhase.APPROVED,
        PromotionPhase.ROLLED_BACK,
    },

    PromotionPhase.APPROVED: {
        PromotionPhase.COMMITTED,
        PromotionPhase.ROLLED_BACK,
    },

    PromotionPhase.COMMITTED: {
        PromotionPhase.SEALED,
        PromotionPhase.ROLLED_BACK,
    },

    PromotionPhase.ROLLED_BACK: set(),

    PromotionPhase.SEALED: set(),
}


# =============================================================================
# HASH / CANONICAL SERIALIZATION
# =============================================================================

def canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def stable_digest(
    value: Any,
) -> str:
    return sha256_text(
        canonical_json(value)
    )


# =============================================================================
# PROMOTION POLICY
# =============================================================================

@dataclass(frozen=True)
class PromotionPolicy:
    symbol: str

    target_leverage: int

    initial_entry_percent: int

    max_pyramid_adds: int
    pyramid_size_percent: int

    max_backups: int
    backup_size_percent: int

    max_fund_exposure_percent: int

    synthetic_only: bool

    real_execution_enabled: bool
    demo_execution_enabled: bool

    exchange_network_writes_enabled: bool

    leverage_mutation_enabled: bool


# =============================================================================
# PROMOTION CANDIDATE
# =============================================================================

@dataclass(frozen=True)
class PromotionCandidate:
    candidate_id: str

    generation: int
    recovery_epoch: int

    policy_digest: str

    created_at_ms: int

    nonce: str

    executable: bool = False

    transport: str = "synthetic"


# =============================================================================
# PROMOTION RECEIPT
# =============================================================================

@dataclass(frozen=True)
class PromotionReceipt:
    candidate_id: str

    from_phase: str
    to_phase: str

    transition_id: str

    transmitted: bool

    network_write: bool

    order_created: bool

    mutation_performed: bool

    receipt_digest: str


# =============================================================================
# RUNTIME STATE
# =============================================================================

@dataclass
class RuntimeState:
    runtime_id: str

    generation: int = 1

    recovery_epoch: int = 1

    phase: str = PromotionPhase.BASELINE.value

    candidate_id: Optional[str] = None

    candidate_digest: Optional[str] = None

    committed_candidate_id: Optional[str] = None

    transition_counter: int = 0

    synthetic_dispatch_count: int = 0

    real_order_count: int = 0

    demo_order_count: int = 0

    network_write_count: int = 0

    mutation_count: int = 0

    consumed_transition_ids: List[str] = field(
        default_factory=list
    )

    sealed: bool = False


STATE_LOCK = threading.RLock()


# =============================================================================
# NEW RUNTIME STATE
# =============================================================================

def new_runtime_state() -> RuntimeState:
    return RuntimeState(
        runtime_id=str(uuid.uuid4())
    )


# =============================================================================
# STATE SERIALIZATION
# =============================================================================

def state_payload(
    state: RuntimeState,
) -> Dict[str, Any]:

    payload = asdict(state)

    payload["state_digest"] = stable_digest(
        payload
    )

    return payload


# =============================================================================
# ATOMIC STATE PERSISTENCE
# =============================================================================

def persist_state(
    state: RuntimeState,
) -> None:

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = state_payload(state)

    temp_file = STATE_FILE.with_suffix(
        STATE_FILE.suffix + ".tmp"
    )

    temp_file.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    os.replace(
        temp_file,
        STATE_FILE,
    )


# =============================================================================
# STATE RESTORE
# =============================================================================

def load_state() -> Optional[RuntimeState]:

    if not STATE_FILE.exists():
        return None

    raw = json.loads(
        STATE_FILE.read_text(
            encoding="utf-8"
        )
    )

    expected_digest = raw.pop(
        "state_digest",
        None,
    )

    actual_digest = stable_digest(raw)

    if expected_digest != actual_digest:
        raise SafetyViolation(
            "R31A durable state digest mismatch"
        )

    return RuntimeState(**raw)


# =============================================================================
# BUILD FROZEN PROMOTION POLICY
# =============================================================================

def build_policy() -> PromotionPolicy:

    return PromotionPolicy(
        symbol=SYMBOL,

        target_leverage=TARGET_LEVERAGE,

        initial_entry_percent=INITIAL_ENTRY_PERCENT,

        max_pyramid_adds=MAX_PYRAMID_ADDS,

        pyramid_size_percent=PYRAMID_SIZE_PERCENT,

        max_backups=MAX_BACKUPS,

        backup_size_percent=BACKUP_SIZE_PERCENT,

        max_fund_exposure_percent=
        MAX_FUND_EXPOSURE_PERCENT,

        synthetic_only=
        SYNTHETIC_TRANSPORT_ONLY,

        real_execution_enabled=
        REAL_ORDER_EXECUTION_ENABLED,

        demo_execution_enabled=
        DEMO_ORDER_EXECUTION_ENABLED,

        exchange_network_writes_enabled=
        EXCHANGE_NETWORK_WRITES_ENABLED,

        leverage_mutation_enabled=
        LEVERAGE_MUTATION_ENABLED,
    )


# =============================================================================
# BUILD PROMOTION CANDIDATE
# =============================================================================

def build_candidate(
    state: RuntimeState,
    policy: PromotionPolicy,
) -> PromotionCandidate:

    now_ms = int(
        time.time() * 1000
    )

    policy_digest = stable_digest(
        asdict(policy)
    )

    nonce = uuid.uuid4().hex

    candidate_seed = {
        "runtime_id":
        state.runtime_id,

        "generation":
        state.generation,

        "recovery_epoch":
        state.recovery_epoch,

        "policy_digest":
        policy_digest,

        "created_at_ms":
        now_ms,

        "nonce":
        nonce,
    }

    candidate_id = stable_digest(
        candidate_seed
    )

    return PromotionCandidate(
        candidate_id=
        candidate_id,

        generation=
        state.generation,

        recovery_epoch=
        state.recovery_epoch,

        policy_digest=
        policy_digest,

        created_at_ms=
        now_ms,

        nonce=
        nonce,

        executable=False,

        transport="synthetic",
    )


# =============================================================================
# TRANSITION ID
# =============================================================================

def transition_id_for(
    state: RuntimeState,
    candidate: PromotionCandidate,
    from_phase: PromotionPhase,
    to_phase: PromotionPhase,
) -> str:

    return stable_digest(
        {
            "runtime_id":
            state.runtime_id,

            "candidate_id":
            candidate.candidate_id,

            "generation":
            state.generation,

            "recovery_epoch":
            state.recovery_epoch,

            "from_phase":
            from_phase.value,

            "to_phase":
            to_phase.value,

            "transition_counter":
            state.transition_counter + 1,
        }
    )


# =============================================================================
# CANDIDATE BINDING VALIDATION
# =============================================================================

def validate_candidate_binding(
    state: RuntimeState,
    candidate: PromotionCandidate,
) -> None:

    if candidate.executable:
        raise SafetyViolation(
            "Executable promotion candidate rejected"
        )

    if candidate.transport != "synthetic":
        raise SafetyViolation(
            "Non-synthetic transport rejected"
        )

    if (
        candidate.generation
        != state.generation
    ):
        raise SafetyViolation(
            "Candidate generation mismatch"
        )

    if (
        candidate.recovery_epoch
        != state.recovery_epoch
    ):
        raise SafetyViolation(
            "Candidate recovery epoch mismatch"
        )

    if state.candidate_id not in (
        None,
        candidate.candidate_id,
    ):
        raise SafetyViolation(
            "Different candidate already bound"
        )


# =============================================================================
# SYNTHETIC PROMOTION TRANSITION
# =============================================================================

def synthetic_transition(
    state: RuntimeState,
    candidate: PromotionCandidate,
    to_phase: PromotionPhase,
    forced_transition_id: Optional[str] = None,
) -> PromotionReceipt:

    with STATE_LOCK:

        validate_candidate_binding(
            state,
            candidate,
        )

        from_phase = PromotionPhase(
            state.phase
        )

        allowed = ALLOWED_TRANSITIONS[
            from_phase
        ]

        if to_phase not in allowed:
            raise SafetyViolation(
                "Illegal promotion transition "
                f"{from_phase.value}"
                "->"
                f"{to_phase.value}"
            )

        transition_id = (
            forced_transition_id
            or transition_id_for(
                state,
                candidate,
                from_phase,
                to_phase,
            )
        )

        if (
            transition_id
            in state.consumed_transition_ids
        ):
            raise SafetyViolation(
                "Promotion transition replay rejected"
            )

        # -------------------------------------------------------------
        # R31A TRANSPORT IS SYNTHETIC ONLY.
        #
        # NO EXCHANGE REQUEST IS MADE HERE.
        # -------------------------------------------------------------

        transmitted = False

        network_write = False

        order_created = False

        mutation_performed = False

        state.transition_counter += 1

        state.synthetic_dispatch_count += 1

        state.consumed_transition_ids.append(
            transition_id
        )

        state.phase = to_phase.value

        state.candidate_id = (
            candidate.candidate_id
        )

        state.candidate_digest = stable_digest(
            asdict(candidate)
        )

        if (
            to_phase
            == PromotionPhase.COMMITTED
        ):
            state.committed_candidate_id = (
                candidate.candidate_id
            )

        if (
            to_phase
            == PromotionPhase.SEALED
        ):
            state.sealed = True

        receipt_base = {
            "candidate_id":
            candidate.candidate_id,

            "from_phase":
            from_phase.value,

            "to_phase":
            to_phase.value,

            "transition_id":
            transition_id,

            "transmitted":
            transmitted,

            "network_write":
            network_write,

            "order_created":
            order_created,

            "mutation_performed":
            mutation_performed,
        }

        receipt = PromotionReceipt(
            **receipt_base,

            receipt_digest=
            stable_digest(
                receipt_base
            ),
        )

        persist_state(state)

        return receipt


# =============================================================================
# STATE CLONE
# =============================================================================

def clone_state(
    state: RuntimeState,
) -> RuntimeState:

    return RuntimeState(
        **json.loads(
            json.dumps(
                asdict(state)
            )
        )
    )


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(
    socketserver.BaseRequestHandler
):

    def handle(self) -> None:

        response_body = (
            f"{VERSION} OK "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED}\n"
        ).encode("utf-8")

        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            + (
                f"Content-Length: "
                f"{len(response_body)}\r\n"
            ).encode("ascii")
            + b"Connection: close\r\n"
            + b"\r\n"
            + response_body
        )

        self.request.sendall(
            response
        )


class ReusableTCPServer(
    socketserver.TCPServer
):
    allow_reuse_address = True


def start_health_server() -> None:

    def worker() -> None:

        with ReusableTCPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        ) as server:

            print(
                f"{VERSION}: "
                "HEALTH SERVER LISTENING "
                f"ON PORT {HEALTH_PORT}",
                flush=True,
            )

            server.serve_forever(
                poll_interval=0.5
            )

    thread = threading.Thread(
        target=worker,
        name="r31a-health",
        daemon=True,
    )

    thread.start()


# =============================================================================
# TEST HELPERS
# =============================================================================

def blocked(
    callable_obj: Any,
) -> bool:

    try:
        callable_obj()

    except SafetyViolation:
        return True

    return False


def frozen_environment_resistance() -> bool:

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

    # Environment value is deliberately irrelevant.
    # The code-level execution constant remains frozen False.

    return (
        REAL_ORDER_EXECUTION_ENABLED
        is False
        and (
            environment_attempt
            or not environment_attempt
        )
    )


# =============================================================================
# R31A VALIDATION
# =============================================================================

def run_validation(
    state: RuntimeState,
) -> RuntimeState:

    global passed
    global failed

    passed = 0
    failed = 0


    # =========================================================================
    # MAIN ENTRY REPORT
    # =========================================================================

    section(
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
        "REAL EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        "DEMO EXECUTION DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        "EXCHANGE NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: "
        "SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )


    # =========================================================================
    # TEST 1
    # SAFETY CONFIGURATION
    # =========================================================================

    section(
        f"{VERSION} TEST 1: "
        "SAFETY CONFIGURATION"
    )

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


    # =========================================================================
    # TEST 2
    # STRATEGY CONSTRAINTS
    # =========================================================================

    section(
        f"{VERSION} TEST 2: "
        "STRATEGY CONSTRAINTS"
    )

    policy = build_policy()

    check(
        "Strategy Symbol Matches Runtime Symbol",
        policy.symbol == SYMBOL,
    )

    check(
        "Target Leverage Is 100x",
        policy.target_leverage == 100,
    )

    check(
        "Initial Entry Is Five Percent",
        policy.initial_entry_percent == 5,
    )

    check(
        "Maximum Pyramid Adds Is One",
        policy.max_pyramid_adds == 1,
    )

    check(
        "Pyramid Size Is Five Percent",
        policy.pyramid_size_percent == 5,
    )

    check(
        "Maximum Backup Count Is Three",
        policy.max_backups == 3,
    )

    check(
        "Backup Size Is Five Percent",
        policy.backup_size_percent == 5,
    )

    check(
        "Maximum Fund Exposure Is "
        "Thirty Five Percent",
        (
            policy.max_fund_exposure_percent
            == 35
        ),
    )

    check(
        "Take Profit Distribution "
        "Reconciles To 100 Percent",
        (
            TP1_ALLOCATION_PERCENT
            + TP2_ALLOCATION_PERCENT
            + TP3_ALLOCATION_PERCENT
            == 100
        ),
    )


    # =========================================================================
    # TEST 3
    # SAFETY FEATURE TOGGLES
    # =========================================================================

    section(
        f"{VERSION} TEST 3: "
        "SAFETY FEATURE TOGGLES"
    )

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


    # =========================================================================
    # TEST 4
    # LOCAL EXECUTION FIREBREAK
    # =========================================================================

    section(
        f"{VERSION} TEST 4: "
        "LOCAL EXECUTION FIREBREAK"
    )

    check(
        "Real Order Function Is "
        "Locally Blocked",
        blocked(real_order),
    )

    check(
        "Demo Order Function Is "
        "Locally Blocked",
        blocked(demo_order),
    )


    # =========================================================================
    # TEST 5
    # NETWORK WRITE FIREBREAK
    # =========================================================================

    section(
        f"{VERSION} TEST 5: "
        "NETWORK WRITE FIREBREAK"
    )

    check(
        "HTTP POST Blocked",
        blocked(http_post),
    )

    check(
        "HTTP PUT Blocked",
        blocked(http_put),
    )

    check(
        "HTTP PATCH Blocked",
        blocked(http_patch),
    )

    check(
        "HTTP DELETE Blocked",
        blocked(http_delete),
    )


    # =========================================================================
    # TEST 6
    # MUTATION FIREBREAK
    # =========================================================================

    section(
        f"{VERSION} TEST 6: "
        "MUTATION FIREBREAK"
    )

    check(
        "Leverage Mutation Blocked",
        blocked(mutate_leverage),
    )

    check(
        "Margin Mutation Blocked",
        blocked(mutate_margin),
    )

    check(
        "Position Mutation Blocked",
        blocked(mutate_position),
    )

    check(
        "Account Mutation Blocked",
        blocked(mutate_account),
    )


    # =========================================================================
    # TEST 7
    # PROMOTION POLICY SEAL
    # =========================================================================

    section(
        f"{VERSION} TEST 7: "
        "PROMOTION POLICY SEAL"
    )

    policy_digest = stable_digest(
        asdict(policy)
    )

    check(
        "Promotion Policy Digest "
        "Is SHA256 Length",
        len(policy_digest) == 64,
    )

    check(
        "Promotion Policy Remains "
        "Synthetic Only",
        policy.synthetic_only,
    )

    check(
        "Promotion Policy Cannot "
        "Execute Real Orders",
        (
            policy.real_execution_enabled
            is False
        ),
    )

    check(
        "Promotion Policy Cannot "
        "Execute Demo Orders",
        (
            policy.demo_execution_enabled
            is False
        ),
    )

    check(
        "Promotion Policy Cannot "
        "Write To Exchange",
        (
            policy.exchange_network_writes_enabled
            is False
        ),
    )

    check(
        "Promotion Policy Cannot "
        "Mutate Leverage",
        (
            policy.leverage_mutation_enabled
            is False
        ),
    )


    # =========================================================================
    # BUILD FRESH BOUNDED VALIDATION STATE
    # =========================================================================

    test_state = RuntimeState(
        runtime_id=state.runtime_id,

        generation=max(
            1,
            state.generation,
        ),

        recovery_epoch=max(
            1,
            state.recovery_epoch,
        ),
    )


    # =========================================================================
    # TEST 8
    # CANDIDATE CONSTRUCTION
    # =========================================================================

    section(
        f"{VERSION} TEST 8: "
        "CANDIDATE CONSTRUCTION"
    )

    candidate = build_candidate(
        test_state,
        policy,
    )

    check(
        "Candidate ID Is SHA256 Length",
        len(candidate.candidate_id) == 64,
    )

    check(
        "Candidate Policy Digest Matches",
        (
            candidate.policy_digest
            == policy_digest
        ),
    )

    check(
        "Candidate Generation Matches",
        (
            candidate.generation
            == test_state.generation
        ),
    )

    check(
        "Candidate Recovery Epoch Matches",
        (
            candidate.recovery_epoch
            == test_state.recovery_epoch
        ),
    )

    check(
        "Candidate Is Non Executable",
        candidate.executable is False,
    )

    check(
        "Candidate Uses Synthetic Transport",
        candidate.transport == "synthetic",
    )

    check(
        "Candidate Nonce Is Present",
        bool(candidate.nonce),
    )


    # =========================================================================
    # TEST 9
    # BASELINE -> CANDIDATE
    # =========================================================================

    section(
        f"{VERSION} TEST 9: "
        "BASELINE TO CANDIDATE"
    )

    receipt_candidate = synthetic_transition(
        test_state,
        candidate,
        PromotionPhase.CANDIDATE,
    )

    check(
        "Phase Advanced To Candidate",
        test_state.phase == "CANDIDATE",
    )

    check(
        "Candidate Transition "
        "Not Transmitted",
        not receipt_candidate.transmitted,
    )

    check(
        "Candidate Transition "
        "Performed No Network Write",
        not receipt_candidate.network_write,
    )

    check(
        "Candidate Transition "
        "Created No Order",
        not receipt_candidate.order_created,
    )

    check(
        "Candidate Transition "
        "Performed No Mutation",
        (
            not receipt_candidate
            .mutation_performed
        ),
    )

    check(
        "Candidate Transition "
        "Receipt Digest Valid",
        (
            len(
                receipt_candidate
                .receipt_digest
            )
            == 64
        ),
    )


    # =========================================================================
    # TEST 10
    # CANDIDATE -> REVIEWED
    # =========================================================================

    section(
        f"{VERSION} TEST 10: "
        "CANDIDATE TO REVIEWED"
    )

    receipt_reviewed = synthetic_transition(
        test_state,
        candidate,
        PromotionPhase.REVIEWED,
    )

    check(
        "Phase Advanced To Reviewed",
        test_state.phase == "REVIEWED",
    )

    check(
        "Reviewed Transition "
        "Not Transmitted",
        not receipt_reviewed.transmitted,
    )

    check(
        "Reviewed Transition "
        "Performed No Network Write",
        not receipt_reviewed.network_write,
    )

    check(
        "Reviewed Transition "
        "Created No Order",
        not receipt_reviewed.order_created,
    )

    check(
        "Reviewed Transition "
        "Performed No Mutation",
        (
            not receipt_reviewed
            .mutation_performed
        ),
    )


    # =========================================================================
    # TEST 11
    # REVIEWED -> APPROVED
    # =========================================================================

    section(
        f"{VERSION} TEST 11: "
        "REVIEWED TO APPROVED"
    )

    receipt_approved = synthetic_transition(
        test_state,
        candidate,
        PromotionPhase.APPROVED,
    )

    check(
        "Phase Advanced To Approved",
        test_state.phase == "APPROVED",
    )

    check(
        "Approved Transition "
        "Not Transmitted",
        not receipt_approved.transmitted,
    )

    check(
        "Approved Transition "
        "Performed No Network Write",
        not receipt_approved.network_write,
    )

    check(
        "Approved Transition "
        "Created No Order",
        not receipt_approved.order_created,
    )

    check(
        "Approved Transition "
        "Performed No Mutation",
        (
            not receipt_approved
            .mutation_performed
        ),
    )


    # =========================================================================
    # TEST 12
    # APPROVED -> COMMITTED
    # =========================================================================

    section(
        f"{VERSION} TEST 12: "
        "APPROVED TO COMMITTED"
    )

    receipt_committed = synthetic_transition(
        test_state,
        candidate,
        PromotionPhase.COMMITTED,
    )

    check(
        "Phase Advanced To Committed",
        test_state.phase == "COMMITTED",
    )

    check(
        "Committed Candidate ID Bound",
        (
            test_state.committed_candidate_id
            == candidate.candidate_id
        ),
    )

    check(
        "Commit Not Transmitted",
        not receipt_committed.transmitted,
    )

    check(
        "Commit Performed "
        "No Network Write",
        not receipt_committed.network_write,
    )

    check(
        "Commit Created No Order",
        not receipt_committed.order_created,
    )

    check(
        "Commit Performed No Mutation",
        (
            not receipt_committed
            .mutation_performed
        ),
    )


    # =========================================================================
    # TEST 13
    # COMMITTED -> SEALED
    # =========================================================================

    section(
        f"{VERSION} TEST 13: "
        "COMMITTED TO SEALED"
    )

    receipt_sealed = synthetic_transition(
        test_state,
        candidate,
        PromotionPhase.SEALED,
    )

    check(
        "Phase Advanced To Sealed",
        test_state.phase == "SEALED",
    )

    check(
        "Runtime Promotion Seal Set",
        test_state.sealed,
    )

    check(
        "Seal Not Transmitted",
        not receipt_sealed.transmitted,
    )

    check(
        "Seal Performed "
        "No Network Write",
        not receipt_sealed.network_write,
    )

    check(
        "Seal Created No Order",
        not receipt_sealed.order_created,
    )

    check(
        "Seal Performed No Mutation",
        (
            not receipt_sealed
            .mutation_performed
        ),
    )


    # =========================================================================
    # TEST 14
    # TERMINAL STATE IMMUTABILITY
    # =========================================================================

    section(
        f"{VERSION} TEST 14: "
        "TERMINAL STATE IMMUTABILITY"
    )

    terminal_rejected = False

    try:
        synthetic_transition(
            test_state,
            candidate,
            PromotionPhase.ROLLED_BACK,
        )

    except SafetyViolation:
        terminal_rejected = True

    check(
        "Sealed State Rejects "
        "Further Transition",
        terminal_rejected,
    )

    check(
        "Sealed Phase Remains Unchanged",
        test_state.phase == "SEALED",
    )

    check(
        "Sealed Candidate Binding "
        "Remains Intact",
        (
            test_state.candidate_id
            == candidate.candidate_id
        ),
    )


    # =========================================================================
    # TEST 15
    # REPLAY REJECTION
    # =========================================================================

    section(
        f"{VERSION} TEST 15: "
        "REPLAY REJECTION"
    )

    replay_state = RuntimeState(
        runtime_id=str(
            uuid.uuid4()
        ),

        generation=1,

        recovery_epoch=1,
    )

    replay_candidate = build_candidate(
        replay_state,
        policy,
    )

    replay_receipt = synthetic_transition(
        replay_state,
        replay_candidate,
        PromotionPhase.CANDIDATE,
    )

    replay_probe = clone_state(
        replay_state
    )

    replay_probe.phase = (
        PromotionPhase.BASELINE.value
    )

    replay_probe.candidate_id = None

    replay_probe.candidate_digest = None

    replay_rejected = False

    try:
        synthetic_transition(
            replay_probe,
            replay_candidate,
            PromotionPhase.CANDIDATE,
            forced_transition_id=(
                replay_receipt.transition_id
            ),
        )

    except SafetyViolation:
        replay_rejected = True

    check(
        "Consumed Promotion Transition "
        "Replay Rejected",
        replay_rejected,
    )

    check(
        "Replay Probe Real Order "
        "Counter Is Zero",
        (
            replay_probe.real_order_count
            == 0
        ),
    )

    check(
        "Replay Probe Network Write "
        "Counter Is Zero",
        (
            replay_probe.network_write_count
            == 0
        ),
    )


    # =========================================================================
    # TEST 16
    # ILLEGAL TRANSITION REJECTION
    # =========================================================================

    section(
        f"{VERSION} TEST 16: "
        "ILLEGAL TRANSITION REJECTION"
    )

    illegal_state = RuntimeState(
        runtime_id=str(
            uuid.uuid4()
        )
    )

    illegal_candidate = build_candidate(
        illegal_state,
        policy,
    )

    illegal_rejected = False

    try:
        synthetic_transition(
            illegal_state,
            illegal_candidate,
            PromotionPhase.APPROVED,
        )

    except SafetyViolation:
        illegal_rejected = True

    check(
        "Baseline Cannot Skip "
        "Directly To Approved",
        illegal_rejected,
    )

    check(
        "Illegal Transition Leaves "
        "Baseline Intact",
        (
            illegal_state.phase
            == "BASELINE"
        ),
    )


    # =========================================================================
    # TEST 17
    # STALE GENERATION REJECTION
    # =========================================================================

    section(
        f"{VERSION} TEST 17: "
        "STALE GENERATION REJECTION"
    )

    stale_generation_state = RuntimeState(
        runtime_id=str(
            uuid.uuid4()
        ),

        generation=2,

        recovery_epoch=1,
    )

    stale_generation_candidate = (
        PromotionCandidate(
            candidate_id=
            candidate.candidate_id,

            generation=1,

            recovery_epoch=1,

            policy_digest=
            candidate.policy_digest,

            created_at_ms=
            candidate.created_at_ms,

            nonce=
            candidate.nonce,
        )
    )

    stale_generation_rejected = False

    try:
        synthetic_transition(
            stale_generation_state,
            stale_generation_candidate,
            PromotionPhase.CANDIDATE,
        )

    except SafetyViolation:
        stale_generation_rejected = True

    check(
        "Stale Generation Candidate "
        "Rejected",
        stale_generation_rejected,
    )

    check(
        "Stale Generation State "
        "Remains Baseline",
        (
            stale_generation_state.phase
            == "BASELINE"
        ),
    )


    # =========================================================================
    # TEST 18
    # STALE RECOVERY EPOCH REJECTION
    # =========================================================================

    section(
        f"{VERSION} TEST 18: "
        "STALE RECOVERY EPOCH REJECTION"
    )

    stale_epoch_state = RuntimeState(
        runtime_id=str(
            uuid.uuid4()
        ),

        generation=1,

        recovery_epoch=2,
    )

    stale_epoch_candidate = (
        PromotionCandidate(
            candidate_id=
            candidate.candidate_id,

            generation=1,

            recovery_epoch=1,

            policy_digest=
            candidate.policy_digest,

            created_at_ms=
            candidate.created_at_ms,

            nonce=
            candidate.nonce,
        )
    )

    stale_epoch_rejected = False

    try:
        synthetic_transition(
            stale_epoch_state,
            stale_epoch_candidate,
            PromotionPhase.CANDIDATE,
        )

    except SafetyViolation:
        stale_epoch_rejected = True

    check(
        "Stale Recovery Epoch "
        "Candidate Rejected",
        stale_epoch_rejected,
    )

    check(
        "Stale Recovery Epoch State "
        "Remains Baseline",
        (
            stale_epoch_state.phase
            == "BASELINE"
        ),
    )


    # =========================================================================
    # TEST 19
    # ROLLBACK PATH
    # =========================================================================

    section(
        f"{VERSION} TEST 19: "
        "ROLLBACK PATH"
    )

    rollback_state = RuntimeState(
        runtime_id=str(
            uuid.uuid4()
        )
    )

    rollback_candidate = build_candidate(
        rollback_state,
        policy,
    )

    synthetic_transition(
        rollback_state,
        rollback_candidate,
        PromotionPhase.CANDIDATE,
    )

    rollback_receipt = synthetic_transition(
        rollback_state,
        rollback_candidate,
        PromotionPhase.ROLLED_BACK,
    )

    check(
        "Candidate Can Roll Back",
        (
            rollback_state.phase
            == "ROLLED_BACK"
        ),
    )

    check(
        "Rollback Is Terminal",
        (
            len(
                ALLOWED_TRANSITIONS[
                    PromotionPhase
                    .ROLLED_BACK
                ]
            )
            == 0
        ),
    )

    check(
        "Rollback Not Transmitted",
        not rollback_receipt.transmitted,
    )

    check(
        "Rollback Performed "
        "No Network Write",
        not rollback_receipt.network_write,
    )

    check(
        "Rollback Created No Order",
        not rollback_receipt.order_created,
    )

    check(
        "Rollback Performed No Mutation",
        (
            not rollback_receipt
            .mutation_performed
        ),
    )


    # =========================================================================
    # TEST 20
    # DURABLE STATE PERSISTENCE
    # =========================================================================

    section(
        f"{VERSION} TEST 20: "
        "DURABLE STATE PERSISTENCE"
    )

    persist_state(
        test_state
    )

    restored = load_state()

    check(
        "Durable State File Created",
        STATE_FILE.exists(),
    )

    check(
        "Durable State Restored",
        restored is not None,
    )

    check(
        "Persisted Runtime ID Matches",
        (
            restored is not None
            and restored.runtime_id
            == test_state.runtime_id
        ),
    )

    check(
        "Persisted Generation Matches",
        (
            restored is not None
            and restored.generation
            == test_state.generation
        ),
    )

    check(
        "Persisted Recovery Epoch Matches",
        (
            restored is not None
            and restored.recovery_epoch
            == test_state.recovery_epoch
        ),
    )

    check(
        "Persisted Phase Is Sealed",
        (
            restored is not None
            and restored.phase
            == PromotionPhase.SEALED.value
        ),
    )

    check(
        "Persisted Candidate ID Matches",
        (
            restored is not None
            and restored.candidate_id
            == candidate.candidate_id
        ),
    )

    check(
        "Persisted Real Order Counter "
        "Is Zero",
        (
            restored is not None
            and restored.real_order_count
            == 0
        ),
    )

    check(
        "Persisted Network Write Counter "
        "Is Zero",
        (
            restored is not None
            and restored.network_write_count
            == 0
        ),
    )

    check(
        "Persisted Mutation Counter "
        "Is Zero",
        (
            restored is not None
            and restored.mutation_count
            == 0
        ),
    )


    # =========================================================================
    # TEST 21
    # RESTART / TERMINAL RECOVERY SEAL
    # =========================================================================

    section(
        f"{VERSION} TEST 21: "
        "RESTART / TERMINAL RECOVERY SEAL"
    )

    restart_rejected = False

    if restored is not None:

        try:
            synthetic_transition(
                restored,
                candidate,
                PromotionPhase.ROLLED_BACK,
            )

        except SafetyViolation:
            restart_rejected = True

    check(
        "Restart Cannot Reopen "
        "Sealed Promotion",
        restart_rejected,
    )

    check(
        "Restart Restores Terminal Seal",
        (
            restored is not None
            and restored.sealed
        ),
    )

    check(
        "Restart Preserves "
        "Committed Candidate",
        (
            restored is not None
            and (
                restored
                .committed_candidate_id
                == candidate.candidate_id
            )
        ),
    )


    # =========================================================================
    # TEST 22
    # ENVIRONMENT ESCALATION RESISTANCE
    # =========================================================================

    section(
        f"{VERSION} TEST 22: "
        "ENVIRONMENT ESCALATION RESISTANCE"
    )

    check(
        "Environment Cannot Directly "
        "Activate Real Execution",
        frozen_environment_resistance(),
    )

    check(
        "Real Execution Constant "
        "Remains Frozen",
        (
            REAL_ORDER_EXECUTION_ENABLED
            is False
        ),
    )

    check(
        "Demo Execution Constant "
        "Remains Frozen",
        (
            DEMO_ORDER_EXECUTION_ENABLED
            is False
        ),
    )

    check(
        "Exchange Write Constant "
        "Remains Frozen",
        (
            EXCHANGE_NETWORK_WRITES_ENABLED
            is False
        ),
    )

    check(
        "Mutation Constants "
        "Remain Frozen",
        (
            not LEVERAGE_MUTATION_ENABLED
            and not MARGIN_MUTATION_ENABLED
            and not POSITION_MUTATION_ENABLED
            and not ACCOUNT_MUTATION_ENABLED
        ),
    )

    check(
        "Synthetic Transport Constant "
        "Remains Frozen",
        (
            SYNTHETIC_TRANSPORT_ONLY
            is True
        ),
    )


    # =========================================================================
    # TEST 23
    # COUNTER INTEGRITY
    # =========================================================================

    section(
        f"{VERSION} TEST 23: "
        "COUNTER INTEGRITY"
    )

    check(
        "Real Order Count Is Zero",
        (
            test_state.real_order_count
            == 0
        ),
    )

    check(
        "Demo Order Count Is Zero",
        (
            test_state.demo_order_count
            == 0
        ),
    )

    check(
        "Network Write Count Is Zero",
        (
            test_state.network_write_count
            == 0
        ),
    )

    check(
        "Mutation Count Is Zero",
        (
            test_state.mutation_count
            == 0
        ),
    )

    check(
        "Synthetic Dispatch Count "
        "Matches Lifecycle",
        (
            test_state
            .synthetic_dispatch_count
            == 5
        ),
    )

    check(
        "Transition Counter "
        "Matches Lifecycle",
        (
            test_state
            .transition_counter
            == 5
        ),
    )

    check(
        "Consumed Transition Count "
        "Matches Lifecycle",
        (
            len(
                test_state
                .consumed_transition_ids
            )
            == 5
        ),
    )


    # =========================================================================
    # TEST 24
    # FINAL R31A READINESS SEAL
    # =========================================================================

    section(
        f"{VERSION} TEST 24: "
        "FINAL R31A READINESS SEAL"
    )

    passed_before_final = passed

    failed_before_final = failed

    check(
        "All Prior Validation "
        "Checks Passed",
        failed_before_final == 0,
    )

    print(
        "  passed-before-final="
        f"{passed_before_final}, "
        f"failed={failed_before_final}",
        flush=True,
    )

    check(
        "R31A Remains Non Executable",
        (
            not REAL_ORDER_EXECUTION_ENABLED
        ),
    )

    check(
        "R31A Remains Network "
        "Write Locked",
        (
            not EXCHANGE_NETWORK_WRITES_ENABLED
        ),
    )

    check(
        "R31A Remains Mutation Locked",
        (
            not LEVERAGE_MUTATION_ENABLED
        ),
    )

    check(
        "R31A Final Phase Is Sealed",
        (
            test_state.phase
            == "SEALED"
        ),
    )


    # =========================================================================
    # PERSIST FINAL VALIDATED SEALED STATE
    # =========================================================================

    persist_state(
        test_state
    )


    # =========================================================================
    # FINAL REPORT
    # =========================================================================

    line()

    if failed == 0:

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
        f"passed={passed} "
        f"failed={failed}",
        flush=True,
    )

    print(
        f"{VERSION}: SAFETY SEAL "
        f"real-orders="
        f"{test_state.real_order_count} "
        f"demo-orders="
        f"{test_state.demo_order_count} "
        f"network-writes="
        f"{test_state.network_write_count} "
        f"mutations="
        f"{test_state.mutation_count}",
        flush=True,
    )

    print(
        f"{VERSION}: PROMOTION SEAL "
        f"phase="
        f"{test_state.phase} "
        f"synthetic-dispatches="
        f"{test_state.synthetic_dispatch_count} "
        f"transitions="
        f"{test_state.transition_counter}",
        flush=True,
    )

    if failed != 0:
        raise SystemExit(1)

    return test_state


# =============================================================================
# HEARTBEAT LOOP
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
            f"{VERSION}: "
            f"HEARTBEAT {heartbeat} | "
            f"phase={state.phase} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"real-execution="
            f"{REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes="
            f"{EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation="
            f"{LEVERAGE_MUTATION_ENABLED} | "
            f"generation="
            f"{state.generation} | "
            f"recovery-epoch="
            f"{state.recovery_epoch}",
            flush=True,
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    start_health_server()

    try:

        existing = load_state()

    except Exception as exc:

        print(
            f"{VERSION}: "
            "EXISTING STATE REJECTED; "
            "STARTING SAFE BASELINE: "
            f"{exc}",
            flush=True,
        )

        existing = None


    # =========================================================================
    # FIRST DEPLOY
    # =========================================================================

    if existing is None:

        state = new_runtime_state()


    # =========================================================================
    # REDEPLOY / RESTART
    #
    # A SEALED TERMINAL CANDIDATE IS NEVER REOPENED.
    #
    # INSTEAD:
    #
    #   generation      += 1
    #   recovery_epoch  += 1
    #
    # A FRESH BOUNDED SYNTHETIC VALIDATION LIFECYCLE IS THEN CREATED.
    # =========================================================================

    else:

        state = RuntimeState(
            runtime_id=
            existing.runtime_id,

            generation=max(
                1,
                existing.generation + 1,
            ),

            recovery_epoch=max(
                1,
                existing.recovery_epoch + 1,
            ),
        )


    # =========================================================================
    # RUN VALIDATION
    # =========================================================================

    validated_state = run_validation(
        state
    )


    # =========================================================================
    # REMAIN ALIVE FOR RENDER
    # =========================================================================

    heartbeat_loop(
        validated_state
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
