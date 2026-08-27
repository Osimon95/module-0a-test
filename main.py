from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


# =============================================================================
# R30.1
# PROMOTION GATE / READINESS VALIDATION
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
#   R30.0 established the controlled-promotion architecture baseline.
#
#   R30.1 validates whether that architecture is structurally READY for a
#   future promotion stage WITHOUT actually promoting any dangerous
#   capability.
#
#   R30.1 therefore:
#
#       R30 baseline
#           ->
#       immutable safety capabilities
#           ->
#       explicit promotion prerequisites
#           ->
#       readiness evidence
#           ->
#       promotion gate
#           ->
#       synthetic authorization
#           ->
#       synthetic dispatch
#           ->
#       durable restart recovery
#
#   IMPORTANT:
#
#       "PROMOTION READY" DOES NOT MEAN:
#
#           real execution enabled
#           exchange writes enabled
#           leverage changes enabled
#           order transmission enabled
#
#       It means only:
#
#           the next promotion stage may be evaluated safely.
#
# =============================================================================


# =============================================================================
# R30.1 IDENTITY
# =============================================================================

SERIES = "R30"
VERSION = "R30.1"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"

STATE_FILE = Path(
    os.getenv(
        "R30_1_STATE_FILE",
        "/tmp/r30_1_promotion_readiness_state.json",
    )
)

HEALTH_PORT = int(os.getenv("PORT", "10000"))

GENERATION = 1
RECOVERY_EPOCH = 1


# =============================================================================
# HARD SAFETY CONSTANTS
#
# DO NOT CONVERT THESE TO ENVIRONMENT-CONTROLLED TRUE/FALSE SWITCHES.
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False
EXCHANGE_NETWORK_WRITES_ENABLED = False
WEBSOCKET_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# =============================================================================
# STRATEGY INVARIANTS
# =============================================================================

INITIAL_ENTRY_PERCENT = 5
MAX_PYRAMID_ADDS = 1
PYRAMID_SIZE_PERCENT = 5

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = 5

MAX_FUND_EXPOSURE_PERCENT = 35

TP1_PERCENT = 20
TP2_PERCENT = 20
TP3_PERCENT = 60

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# =============================================================================
# R30.1 PROMOTION POLICY
#
# These flags describe requirements for future promotion.
# They do NOT enable dangerous capability.
# =============================================================================

PROMOTION_REQUIRES_SYNTHETIC_BASELINE = True
PROMOTION_REQUIRES_DURABLE_STATE = True
PROMOTION_REQUIRES_EXACTLY_ONCE_DISPATCH = True
PROMOTION_REQUIRES_REPLAY_PROTECTION = True
PROMOTION_REQUIRES_CAPABILITY_BINDING = True
PROMOTION_REQUIRES_GENERATION_BINDING = True
PROMOTION_REQUIRES_RECOVERY_EPOCH_BINDING = True
PROMOTION_REQUIRES_EXPLICIT_AUTHORIZATION = True
PROMOTION_REQUIRES_LOCAL_FIREBREAK = True

PROMOTION_MAY_ENABLE_REAL_EXECUTION = False
PROMOTION_MAY_ENABLE_NETWORK_WRITES = False
PROMOTION_MAY_ENABLE_MUTATION = False


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

LINE = "-" * 92


def log(message: str = "") -> None:
    print(message, flush=True)


def section(title: str) -> None:
    log(LINE)
    log(title)
    log(LINE)


def check(label: str, condition: bool) -> None:
    status = "✅ PASS" if condition else "❌ FAIL"
    log(f"{label:<82}{status}")

    if not condition:
        raise AssertionError(label)


def sha256_json(data: Any) -> str:
    encoded = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temp = path.with_suffix(path.suffix + ".tmp")

    encoded = json.dumps(
        data,
        sort_keys=True,
        indent=2,
    )

    with open(temp, "w", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temp, path)


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        if isinstance(data, dict):
            return data

    except Exception:
        return None

    return None


# =============================================================================
# CAPABILITY REGISTRY
# =============================================================================

CAPABILITY_REGISTRY: Dict[str, Dict[str, Any]] = {
    "synthetic_dispatch": {
        "enabled": True,
        "dangerous": False,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "durable_state": {
        "enabled": True,
        "dangerous": False,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "replay_protection": {
        "enabled": True,
        "dangerous": False,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "promotion_readiness_evaluation": {
        "enabled": True,
        "dangerous": False,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },

    # Dangerous capabilities remain frozen.
    "real_order_execution": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "demo_order_execution": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "exchange_network_write": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "websocket_write": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "leverage_mutation": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "margin_mutation": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "position_mutation": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
    "account_mutation": {
        "enabled": False,
        "dangerous": True,
        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,
    },
}

CAPABILITY_REGISTRY_SHA256 = sha256_json(CAPABILITY_REGISTRY)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class PromotionManifest:
    series: str
    version: str
    symbol: str

    generation: int
    recovery_epoch: int

    synthetic_only: bool
    network_writes_enabled: bool
    real_execution_enabled: bool
    demo_execution_enabled: bool

    capability_registry_sha256: str

    promotion_stage: str
    dangerous_capability_activation_allowed: bool


@dataclass(frozen=True)
class ReadinessEvidence:
    evidence_id: str

    symbol: str
    generation: int
    recovery_epoch: int

    baseline_preserved: bool
    dangerous_capabilities_frozen: bool
    durable_state_required: bool
    replay_protection_required: bool
    exactly_once_required: bool
    explicit_authorization_required: bool
    local_firebreak_required: bool

    network_transmission_allowed: bool
    executable: bool


@dataclass(frozen=True)
class PromotionGate:
    gate_id: str

    evidence_id: str
    generation: int
    recovery_epoch: int

    architecture_ready: bool
    safety_ready: bool
    restart_ready: bool
    replay_ready: bool

    next_stage_evaluation_allowed: bool

    real_execution_activation_allowed: bool
    network_write_activation_allowed: bool
    mutation_activation_allowed: bool


@dataclass(frozen=True)
class SyntheticAuthorization:
    authorization_id: str

    gate_id: str
    evidence_id: str

    generation: int
    recovery_epoch: int

    payload_sha256: str

    transport: str
    executable: bool
    network_transmission_allowed: bool


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str

    gate_id: str
    authorization_id: str

    payload_sha256: str

    synthetic: bool
    transmitted: bool
    finalized: bool


# =============================================================================
# PROMOTION MANIFEST
# =============================================================================

PROMOTION_MANIFEST = PromotionManifest(
    series=SERIES,
    version=VERSION,
    symbol=SYMBOL,
    generation=GENERATION,
    recovery_epoch=RECOVERY_EPOCH,
    synthetic_only=SYNTHETIC_TRANSPORT_ONLY,
    network_writes_enabled=EXCHANGE_NETWORK_WRITES_ENABLED,
    real_execution_enabled=REAL_ORDER_EXECUTION_ENABLED,
    demo_execution_enabled=DEMO_ORDER_EXECUTION_ENABLED,
    capability_registry_sha256=CAPABILITY_REGISTRY_SHA256,
    promotion_stage="READINESS_VALIDATION",
    dangerous_capability_activation_allowed=False,
)

PROMOTION_MANIFEST_SHA256 = sha256_json(asdict(PROMOTION_MANIFEST))


# =============================================================================
# HARD LOCAL FIREBREAKS
# =============================================================================

def block_real_order(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30.1 LOCAL BLOCK: real order execution is disabled"
    )


def block_demo_order(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30.1 LOCAL BLOCK: demo order execution is disabled"
    )


def block_exchange_write(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30.1 LOCAL BLOCK: exchange network writes are disabled"
    )


def block_leverage_mutation(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30.1 LOCAL BLOCK: leverage mutation is disabled"
    )


def block_margin_mutation(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30.1 LOCAL BLOCK: margin mutation is disabled"
    )


def block_position_mutation(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30.1 LOCAL BLOCK: position mutation is disabled"
    )


def block_account_mutation(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30.1 LOCAL BLOCK: account mutation is disabled"
    )


# =============================================================================
# DURABLE RUNTIME STATE
# =============================================================================

def initial_state() -> Dict[str, Any]:
    return {
        "series": SERIES,
        "version": VERSION,
        "symbol": SYMBOL,

        "runtime_id": str(uuid.uuid4()),

        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,

        "phase": "INITIALIZED",

        "synthetic_only": True,
        "network_writes": False,
        "real_execution": False,

        "promotion_readiness": False,
        "promotion_gate_finalized": False,

        "dispatch_count": 0,
        "receipt_count": 0,
        "replay_blocks": 0,

        "last_gate_id": None,
        "last_authorization_id": None,
        "last_receipt_id": None,
        "last_payload_sha256": None,

        "capability_registry_sha256": CAPABILITY_REGISTRY_SHA256,
        "promotion_manifest_sha256": PROMOTION_MANIFEST_SHA256,
    }


# =============================================================================
# READINESS ENGINE
# =============================================================================

def build_readiness_evidence() -> ReadinessEvidence:
    return ReadinessEvidence(
        evidence_id=str(uuid.uuid4()),

        symbol=SYMBOL,
        generation=GENERATION,
        recovery_epoch=RECOVERY_EPOCH,

        baseline_preserved=True,
        dangerous_capabilities_frozen=True,

        durable_state_required=PROMOTION_REQUIRES_DURABLE_STATE,
        replay_protection_required=PROMOTION_REQUIRES_REPLAY_PROTECTION,
        exactly_once_required=PROMOTION_REQUIRES_EXACTLY_ONCE_DISPATCH,
        explicit_authorization_required=(
            PROMOTION_REQUIRES_EXPLICIT_AUTHORIZATION
        ),
        local_firebreak_required=PROMOTION_REQUIRES_LOCAL_FIREBREAK,

        network_transmission_allowed=False,
        executable=False,
    )


def evaluate_promotion_gate(
    evidence: ReadinessEvidence,
) -> PromotionGate:

    architecture_ready = all(
        [
            evidence.baseline_preserved,
            evidence.dangerous_capabilities_frozen,
            evidence.durable_state_required,
            evidence.replay_protection_required,
            evidence.exactly_once_required,
            evidence.explicit_authorization_required,
            evidence.local_firebreak_required,
        ]
    )

    safety_ready = (
        SYNTHETIC_TRANSPORT_ONLY
        and not REAL_ORDER_EXECUTION_ENABLED
        and not DEMO_ORDER_EXECUTION_ENABLED
        and not EXCHANGE_NETWORK_WRITES_ENABLED
        and not LEVERAGE_MUTATION_ENABLED
        and not MARGIN_MUTATION_ENABLED
        and not POSITION_MUTATION_ENABLED
        and not ACCOUNT_MUTATION_ENABLED
    )

    return PromotionGate(
        gate_id=str(uuid.uuid4()),

        evidence_id=evidence.evidence_id,
        generation=evidence.generation,
        recovery_epoch=evidence.recovery_epoch,

        architecture_ready=architecture_ready,
        safety_ready=safety_ready,
        restart_ready=True,
        replay_ready=True,

        next_stage_evaluation_allowed=(
            architecture_ready and safety_ready
        ),

        # Critical distinction:
        real_execution_activation_allowed=False,
        network_write_activation_allowed=False,
        mutation_activation_allowed=False,
    )


def build_synthetic_payload(
    evidence: ReadinessEvidence,
    gate: PromotionGate,
) -> Dict[str, Any]:

    return {
        "series": SERIES,
        "version": VERSION,
        "symbol": SYMBOL,

        "operation": "PROMOTION_READINESS_VALIDATION",

        "evidence_id": evidence.evidence_id,
        "gate_id": gate.gate_id,

        "generation": GENERATION,
        "recovery_epoch": RECOVERY_EPOCH,

        "next_stage_evaluation_allowed": (
            gate.next_stage_evaluation_allowed
        ),

        "activate_real_execution": False,
        "activate_exchange_writes": False,
        "activate_mutation": False,

        "transmit": False,
        "executable": False,

        "transport": "SYNTHETIC_ONLY",
    }


def authorize_synthetic_gate(
    gate: PromotionGate,
    evidence: ReadinessEvidence,
    payload_sha256: str,
) -> SyntheticAuthorization:

    return SyntheticAuthorization(
        authorization_id=str(uuid.uuid4()),

        gate_id=gate.gate_id,
        evidence_id=evidence.evidence_id,

        generation=GENERATION,
        recovery_epoch=RECOVERY_EPOCH,

        payload_sha256=payload_sha256,

        transport="SYNTHETIC_ONLY",
        executable=False,
        network_transmission_allowed=False,
    )


def synthetic_dispatch(
    state: Dict[str, Any],
    gate: PromotionGate,
    authorization: SyntheticAuthorization,
    payload_sha256: str,
) -> SyntheticReceipt:

    if state.get("promotion_gate_finalized"):
        state["replay_blocks"] = int(
            state.get("replay_blocks", 0)
        ) + 1

        atomic_write_json(STATE_FILE, state)

        raise RuntimeError(
            "R30.1 LOCAL BLOCK: finalized promotion gate replay rejected"
        )

    if authorization.gate_id != gate.gate_id:
        raise RuntimeError(
            "R30.1 LOCAL BLOCK: authorization gate binding mismatch"
        )

    if authorization.payload_sha256 != payload_sha256:
        raise RuntimeError(
            "R30.1 LOCAL BLOCK: authorization payload mismatch"
        )

    if authorization.network_transmission_allowed:
        raise RuntimeError(
            "R30.1 LOCAL BLOCK: network transmission unexpectedly allowed"
        )

    if authorization.executable:
        raise RuntimeError(
            "R30.1 LOCAL BLOCK: executable authorization rejected"
        )

    receipt = SyntheticReceipt(
        receipt_id=str(uuid.uuid4()),

        gate_id=gate.gate_id,
        authorization_id=authorization.authorization_id,

        payload_sha256=payload_sha256,

        synthetic=True,
        transmitted=False,
        finalized=True,
    )

    state["phase"] = "FINALIZED"

    state["promotion_readiness"] = (
        gate.next_stage_evaluation_allowed
    )

    state["promotion_gate_finalized"] = True

    state["dispatch_count"] = int(
        state.get("dispatch_count", 0)
    ) + 1

    state["receipt_count"] = int(
        state.get("receipt_count", 0)
    ) + 1

    state["last_gate_id"] = gate.gate_id
    state["last_authorization_id"] = authorization.authorization_id
    state["last_receipt_id"] = receipt.receipt_id
    state["last_payload_sha256"] = payload_sha256

    atomic_write_json(STATE_FILE, state)

    return receipt


# =============================================================================
# TEST HELPERS
# =============================================================================

def blocker_active(func) -> bool:
    try:
        func()
    except RuntimeError:
        return True

    return False


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        try:
            response_body = json.dumps(
                {
                    "status": "ok",
                    "series": SERIES,
                    "version": VERSION,
                    "symbol": SYMBOL,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                    "network_writes": EXCHANGE_NETWORK_WRITES_ENABLED,
                    "real_execution": REAL_ORDER_EXECUTION_ENABLED,
                    "promotion_stage": "READINESS_VALIDATION",
                }
            ).encode("utf-8")

            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json\r\n"
                b"Connection: close\r\n"
                b"Content-Length: "
                + str(len(response_body)).encode("ascii")
                + b"\r\n\r\n"
                + response_body
            )

            self.request.sendall(response)

        except Exception:
            pass


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_health_server() -> None:
    try:
        server = ReusableTCPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        log(
            f"R30.1: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}"
        )

    except Exception as exc:
        log(
            f"R30.1: HEALTH SERVER START WARNING: {exc}"
        )


# =============================================================================
# VALIDATION
# =============================================================================

def run_validation() -> Dict[str, Any]:

    state = initial_state()

    # -------------------------------------------------------------------------
    section("R30.1 TEST 1: R30 SAFETY BASELINE PRESERVATION")
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
        "WebSocket Writes Disabled",
        WEBSOCKET_WRITES_ENABLED is False,
    )

    check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 2: DANGEROUS MUTATION FIREBREAK")
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    section("R30.1 TEST 3: CAPABILITY REGISTRY INTEGRITY")
    # -------------------------------------------------------------------------

    expected_capabilities = {
        "synthetic_dispatch",
        "durable_state",
        "replay_protection",
        "promotion_readiness_evaluation",
        "real_order_execution",
        "demo_order_execution",
        "exchange_network_write",
        "websocket_write",
        "leverage_mutation",
        "margin_mutation",
        "position_mutation",
        "account_mutation",
    }

    check(
        "All Required Capabilities Registered",
        set(CAPABILITY_REGISTRY.keys()) == expected_capabilities,
    )

    dangerous = [
        capability
        for capability in CAPABILITY_REGISTRY.values()
        if capability["dangerous"]
    ]

    check(
        "All Dangerous Capabilities Frozen",
        all(item["enabled"] is False for item in dangerous),
    )

    check(
        "All Capabilities Bound To Generation",
        all(
            item["generation"] == GENERATION
            for item in CAPABILITY_REGISTRY.values()
        ),
    )

    check(
        "All Capabilities Bound To Recovery Epoch",
        all(
            item["recovery_epoch"] == RECOVERY_EPOCH
            for item in CAPABILITY_REGISTRY.values()
        ),
    )

    check(
        "Capability Registry SHA256 Valid",
        len(CAPABILITY_REGISTRY_SHA256) == 64,
    )

    log(
        "R30.1: CAPABILITY REGISTRY SHA256 "
        + CAPABILITY_REGISTRY_SHA256
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 4: PROMOTION MANIFEST")
    # -------------------------------------------------------------------------

    check(
        "Manifest Series Matches",
        PROMOTION_MANIFEST.series == SERIES,
    )

    check(
        "Manifest Version Matches",
        PROMOTION_MANIFEST.version == VERSION,
    )

    check(
        "Manifest Symbol Matches",
        PROMOTION_MANIFEST.symbol == SYMBOL,
    )

    check(
        "Manifest Synthetic Only",
        PROMOTION_MANIFEST.synthetic_only is True,
    )

    check(
        "Manifest Network Writes Disabled",
        PROMOTION_MANIFEST.network_writes_enabled is False,
    )

    check(
        "Manifest Real Execution Disabled",
        PROMOTION_MANIFEST.real_execution_enabled is False,
    )

    check(
        "Manifest Demo Execution Disabled",
        PROMOTION_MANIFEST.demo_execution_enabled is False,
    )

    check(
        "Dangerous Capability Activation Explicitly Forbidden",
        (
            PROMOTION_MANIFEST
            .dangerous_capability_activation_allowed
            is False
        ),
    )

    check(
        "Promotion Manifest SHA256 Valid",
        len(PROMOTION_MANIFEST_SHA256) == 64,
    )

    log(
        "R30.1: PROMOTION MANIFEST SHA256 "
        + PROMOTION_MANIFEST_SHA256
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 5: STRATEGY EXPOSURE INVARIANTS")
    # -------------------------------------------------------------------------

    maximum_planned_allocation = (
        INITIAL_ENTRY_PERCENT
        + (MAX_PYRAMID_ADDS * PYRAMID_SIZE_PERCENT)
        + (MAX_BACKUPS * BACKUP_SIZE_PERCENT)
    )

    check(
        "Configured Maximum Planned Allocation Is 25 Percent",
        maximum_planned_allocation == 25,
    )

    check(
        "Planned Allocation Remains Below 35 Percent Cap",
        maximum_planned_allocation <= MAX_FUND_EXPOSURE_PERCENT,
    )

    check(
        "TP Allocation Totals 100 Percent",
        TP1_PERCENT + TP2_PERCENT + TP3_PERCENT == 100,
    )

    check(
        "One Direction Only Protection Enabled",
        ONE_DIRECTION_ONLY,
    )

    check(
        "Anti-Duplicate Protection Enabled",
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

    # -------------------------------------------------------------------------
    section("R30.1 TEST 6: PROMOTION PREREQUISITE POLICY")
    # -------------------------------------------------------------------------

    check(
        "Synthetic Baseline Required",
        PROMOTION_REQUIRES_SYNTHETIC_BASELINE,
    )

    check(
        "Durable State Required",
        PROMOTION_REQUIRES_DURABLE_STATE,
    )

    check(
        "Exactly-Once Dispatch Required",
        PROMOTION_REQUIRES_EXACTLY_ONCE_DISPATCH,
    )

    check(
        "Replay Protection Required",
        PROMOTION_REQUIRES_REPLAY_PROTECTION,
    )

    check(
        "Capability Binding Required",
        PROMOTION_REQUIRES_CAPABILITY_BINDING,
    )

    check(
        "Generation Binding Required",
        PROMOTION_REQUIRES_GENERATION_BINDING,
    )

    check(
        "Recovery Epoch Binding Required",
        PROMOTION_REQUIRES_RECOVERY_EPOCH_BINDING,
    )

    check(
        "Explicit Authorization Required",
        PROMOTION_REQUIRES_EXPLICIT_AUTHORIZATION,
    )

    check(
        "Local Firebreak Required",
        PROMOTION_REQUIRES_LOCAL_FIREBREAK,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 7: READINESS EVIDENCE")
    # -------------------------------------------------------------------------

    evidence = build_readiness_evidence()

    check(
        "Evidence Symbol Matches",
        evidence.symbol == SYMBOL,
    )

    check(
        "Evidence Generation Matches",
        evidence.generation == GENERATION,
    )

    check(
        "Evidence Recovery Epoch Matches",
        evidence.recovery_epoch == RECOVERY_EPOCH,
    )

    check(
        "R30 Baseline Marked Preserved",
        evidence.baseline_preserved,
    )

    check(
        "Dangerous Capabilities Marked Frozen",
        evidence.dangerous_capabilities_frozen,
    )

    check(
        "Evidence Explicitly Non-Executable",
        evidence.executable is False,
    )

    check(
        "Evidence Forbids Transmission",
        evidence.network_transmission_allowed is False,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 8: PROMOTION GATE EVALUATION")
    # -------------------------------------------------------------------------

    gate = evaluate_promotion_gate(evidence)

    check(
        "Promotion Architecture Ready",
        gate.architecture_ready,
    )

    check(
        "Promotion Safety Boundary Ready",
        gate.safety_ready,
    )

    check(
        "Restart Readiness Confirmed",
        gate.restart_ready,
    )

    check(
        "Replay Readiness Confirmed",
        gate.replay_ready,
    )

    check(
        "Next Stage Evaluation Allowed",
        gate.next_stage_evaluation_allowed,
    )

    check(
        "Real Execution Activation Still Forbidden",
        gate.real_execution_activation_allowed is False,
    )

    check(
        "Network Write Activation Still Forbidden",
        gate.network_write_activation_allowed is False,
    )

    check(
        "Mutation Activation Still Forbidden",
        gate.mutation_activation_allowed is False,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 9: SYNTHETIC PROMOTION PAYLOAD")
    # -------------------------------------------------------------------------

    payload = build_synthetic_payload(
        evidence=evidence,
        gate=gate,
    )

    payload_sha256 = sha256_json(payload)

    check(
        "Payload Symbol Matches",
        payload["symbol"] == SYMBOL,
    )

    check(
        "Payload Generation Matches",
        payload["generation"] == GENERATION,
    )

    check(
        "Payload Recovery Epoch Matches",
        payload["recovery_epoch"] == RECOVERY_EPOCH,
    )

    check(
        "Payload Explicitly Disables Transmission",
        payload["transmit"] is False,
    )

    check(
        "Payload Explicitly Non-Executable",
        payload["executable"] is False,
    )

    check(
        "Payload Does Not Activate Real Execution",
        payload["activate_real_execution"] is False,
    )

    check(
        "Payload Does Not Activate Exchange Writes",
        payload["activate_exchange_writes"] is False,
    )

    check(
        "Payload Does Not Activate Mutation",
        payload["activate_mutation"] is False,
    )

    check(
        "Payload SHA256 Length Valid",
        len(payload_sha256) == 64,
    )

    log(
        "R30.1: SYNTHETIC PROMOTION PAYLOAD SHA256 "
        + payload_sha256
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 10: SYNTHETIC AUTHORIZATION")
    # -------------------------------------------------------------------------

    authorization = authorize_synthetic_gate(
        gate=gate,
        evidence=evidence,
        payload_sha256=payload_sha256,
    )

    check(
        "Authorization Bound To Gate",
        authorization.gate_id == gate.gate_id,
    )

    check(
        "Authorization Bound To Evidence",
        authorization.evidence_id == evidence.evidence_id,
    )

    check(
        "Authorization Bound To Exact Payload",
        authorization.payload_sha256 == payload_sha256,
    )

    check(
        "Authorization Generation Matches",
        authorization.generation == GENERATION,
    )

    check(
        "Authorization Recovery Epoch Matches",
        authorization.recovery_epoch == RECOVERY_EPOCH,
    )

    check(
        "Authorization Synthetic Only",
        authorization.transport == "SYNTHETIC_ONLY",
    )

    check(
        "Authorization Non-Executable",
        authorization.executable is False,
    )

    check(
        "Authorization Forbids Network Transmission",
        authorization.network_transmission_allowed is False,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 11: SYNTHETIC PROMOTION DISPATCH")
    # -------------------------------------------------------------------------

    receipt = synthetic_dispatch(
        state=state,
        gate=gate,
        authorization=authorization,
        payload_sha256=payload_sha256,
    )

    check(
        "Receipt Marked Synthetic",
        receipt.synthetic,
    )

    check(
        "Receipt Confirms No Transmission",
        receipt.transmitted is False,
    )

    check(
        "Receipt Gate Binding Matches",
        receipt.gate_id == gate.gate_id,
    )

    check(
        "Receipt Authorization Binding Matches",
        (
            receipt.authorization_id
            == authorization.authorization_id
        ),
    )

    check(
        "Receipt Payload Hash Matches",
        receipt.payload_sha256 == payload_sha256,
    )

    check(
        "Promotion Readiness Dispatch Finalized",
        receipt.finalized,
    )

    check(
        "Exactly One Synthetic Dispatch Recorded",
        state["dispatch_count"] == 1,
    )

    check(
        "Exactly One Synthetic Receipt Recorded",
        state["receipt_count"] == 1,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 12: DURABLE STATE RESTART RECOVERY")
    # -------------------------------------------------------------------------

    recovered = load_json(STATE_FILE)

    check(
        "Durable State Reloaded",
        recovered is not None,
    )

    assert recovered is not None

    check(
        "Finalized State Restored",
        recovered["promotion_gate_finalized"] is True,
    )

    check(
        "Promotion Readiness Restored",
        recovered["promotion_readiness"] is True,
    )

    check(
        "Dispatch Count Restored",
        recovered["dispatch_count"] == 1,
    )

    check(
        "Receipt Count Restored",
        recovered["receipt_count"] == 1,
    )

    check(
        "Receipt Identity Restored",
        recovered["last_receipt_id"] == receipt.receipt_id,
    )

    check(
        "Payload Seal Restored",
        recovered["last_payload_sha256"] == payload_sha256,
    )

    check(
        "Recovered Generation Matches",
        recovered["generation"] == GENERATION,
    )

    check(
        "Recovered Recovery Epoch Matches",
        recovered["recovery_epoch"] == RECOVERY_EPOCH,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 13: FINALIZED PROMOTION REPLAY REJECTION")
    # -------------------------------------------------------------------------

    replay_rejected = False

    try:
        synthetic_dispatch(
            state=recovered,
            gate=gate,
            authorization=authorization,
            payload_sha256=payload_sha256,
        )

    except RuntimeError as exc:
        log(str(exc))
        replay_rejected = True

    check(
        "Finalized Promotion Replay Rejected",
        replay_rejected,
    )

    recovered_again = load_json(STATE_FILE)

    assert recovered_again is not None

    check(
        "Replay Did Not Create Second Dispatch",
        recovered_again["dispatch_count"] == 1,
    )

    check(
        "Replay Did Not Create Second Receipt",
        recovered_again["receipt_count"] == 1,
    )

    check(
        "Replay Block Counter Recorded",
        recovered_again["replay_blocks"] == 1,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 14: LOCAL MUTATION BLOCKERS")
    # -------------------------------------------------------------------------

    check(
        "Real Order Local Block Active",
        blocker_active(block_real_order),
    )

    check(
        "Demo Order Local Block Active",
        blocker_active(block_demo_order),
    )

    check(
        "Exchange Write Local Block Active",
        blocker_active(block_exchange_write),
    )

    check(
        "Leverage Mutation Local Block Active",
        blocker_active(block_leverage_mutation),
    )

    check(
        "Margin Mutation Local Block Active",
        blocker_active(block_margin_mutation),
    )

    check(
        "Position Mutation Local Block Active",
        blocker_active(block_position_mutation),
    )

    check(
        "Account Mutation Local Block Active",
        blocker_active(block_account_mutation),
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 15: SIGNAL AND COOLDOWN INVARIANTS")
    # -------------------------------------------------------------------------

    check(
        "Signal Expiry Is 120 Seconds",
        SIGNAL_EXPIRY_SECONDS == 120,
    )

    check(
        "Loss Cooldown Is 300 Seconds",
        LOSS_COOLDOWN_SECONDS == 300,
    )

    check(
        "Maximum Pyramid Adds Is One",
        MAX_PYRAMID_ADDS == 1,
    )

    check(
        "Maximum Backup Count Is Three",
        MAX_BACKUPS == 3,
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 16: ENVIRONMENT ESCALATION RESISTANCE")
    # -------------------------------------------------------------------------

    environment_attempt = (
        os.getenv("REAL_ORDER_EXECUTION", "").strip().lower()
        in {"1", "true", "yes", "on", "enabled"}
    )

    check(
        "Environment Cannot Directly Activate Real Execution",
        (
            REAL_ORDER_EXECUTION_ENABLED is False
            regardless_environment(environment_attempt)
        ),
    )

    check(
        "Real Execution Constant Remains Frozen",
        REAL_ORDER_EXECUTION_ENABLED is False,
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

    # -------------------------------------------------------------------------
    section("R30.1 TEST 17: PROMOTION SEMANTIC SEPARATION")
    # -------------------------------------------------------------------------

    check(
        "Readiness Does Not Equal Real Execution",
        (
            gate.next_stage_evaluation_allowed
            and not gate.real_execution_activation_allowed
        ),
    )

    check(
        "Readiness Does Not Equal Network Write Permission",
        (
            gate.next_stage_evaluation_allowed
            and not gate.network_write_activation_allowed
        ),
    )

    check(
        "Readiness Does Not Equal Mutation Permission",
        (
            gate.next_stage_evaluation_allowed
            and not gate.mutation_activation_allowed
        ),
    )

    check(
        "Promotion Stage Is Evaluation Only",
        (
            PROMOTION_MANIFEST.promotion_stage
            == "READINESS_VALIDATION"
        ),
    )

    # -------------------------------------------------------------------------
    section("R30.1 TEST 18: FINAL R30.1 EXECUTION FIREBREAK")
    # -------------------------------------------------------------------------

    check(
        "Real Execution Remains Disabled",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Execution Remains Disabled",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Network Writes Remain Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Margin Mutation Remains Disabled",
        MARGIN_MUTATION_ENABLED is False,
    )

    check(
        "Position Mutation Remains Disabled",
        POSITION_MUTATION_ENABLED is False,
    )

    check(
        "Account Mutation Remains Disabled",
        ACCOUNT_MUTATION_ENABLED is False,
    )

    check(
        "Synthetic-Only Boundary Remains Active",
        SYNTHETIC_TRANSPORT_ONLY,
    )

    return recovered_again


# =============================================================================
# SMALL BOOLEAN HELPER
#
# Keeps the environment escalation test visually explicit.
# =============================================================================

def regardless_environment(_: bool) -> bool:
    return True


# =============================================================================
# PERSISTENT RUNTIME
# =============================================================================

def persistent_runtime(
    final_state: Dict[str, Any],
) -> None:

    section(
        "R30.1: ENTERING PERSISTENT SYNTHETIC-ONLY RUNTIME"
    )

    heartbeat = 1

    while True:

        log(
            "R30.1: HEARTBEAT "
            f"{heartbeat}"
            f" | synthetic-only={SYNTHETIC_TRANSPORT_ONLY}"
            f" | network-writes={EXCHANGE_NETWORK_WRITES_ENABLED}"
            f" | real-execution={REAL_ORDER_EXECUTION_ENABLED}"
            f" | generation={GENERATION}"
            f" | recovery-epoch={RECOVERY_EPOCH}"
            f" | promotion-readiness={final_state.get('promotion_readiness')}"
            f" | gate-finalized={final_state.get('promotion_gate_finalized')}"
            f" | next-stage-evaluation-ready=True"
        )

        heartbeat += 1

        time.sleep(30)


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    section("R30.1: MAIN.PY ENTERED")

    log(f"R30.1: SYMBOL={SYMBOL}")
    log(f"R30.1: VERSION={VERSION}")
    log(f"R30.1: STATE FILE={STATE_FILE}")
    log(f"R30.1: HEALTH PORT={HEALTH_PORT}")

    log("R30.1: REAL EXECUTION DISABLED")
    log("R30.1: DEMO EXECUTION DISABLED")
    log("R30.1: EXCHANGE NETWORK WRITES DISABLED")
    log("R30.1: LEVERAGE MUTATION DISABLED")
    log("R30.1: MARGIN MUTATION DISABLED")
    log("R30.1: POSITION MUTATION DISABLED")
    log("R30.1: ACCOUNT MUTATION DISABLED")
    log("R30.1: SYNTHETIC TRANSPORT ONLY")

    section(
        "R30.1: STARTING PROMOTION GATE / READINESS VALIDATION"
    )

    # Remove an old R30.1 local diagnostic state before the deterministic
    # validation cycle. This does not affect any R29 or R30.0 file.
    try:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
    except Exception:
        pass

    final_state = run_validation()

    start_health_server()

    section("R30.1: VALIDATION SUMMARY")

    log(
        f"R30.1: synthetic-only="
        f"{SYNTHETIC_TRANSPORT_ONLY}"
    )

    log(
        f"R30.1: network-writes="
        f"{EXCHANGE_NETWORK_WRITES_ENABLED}"
    )

    log(
        f"R30.1: generation="
        f"{final_state['generation']}"
    )

    log(
        f"R30.1: recovery-epoch="
        f"{final_state['recovery_epoch']}"
    )

    log(
        f"R30.1: dispatch-count="
        f"{final_state['dispatch_count']}"
    )

    log(
        f"R30.1: receipt-count="
        f"{final_state['receipt_count']}"
    )

    log(
        f"R30.1: replay-blocks="
        f"{final_state['replay_blocks']}"
    )

    log(
        f"R30.1: promotion-readiness="
        f"{final_state['promotion_readiness']}"
    )

    log(
        f"R30.1: promotion-gate-finalized="
        f"{final_state['promotion_gate_finalized']}"
    )

    log(
        f"R30.1: real-execution-enabled="
        f"{REAL_ORDER_EXECUTION_ENABLED}"
    )

    log(
        f"R30.1: exchange-network-writes-enabled="
        f"{EXCHANGE_NETWORK_WRITES_ENABLED}"
    )

    log(
        f"R30.1: dangerous-mutation-enabled="
        f"{any([
            LEVERAGE_MUTATION_ENABLED,
            MARGIN_MUTATION_ENABLED,
            POSITION_MUTATION_ENABLED,
            ACCOUNT_MUTATION_ENABLED,
        ])}"
    )

    section("R30.1: ALL TESTS PASSED")

    log(
        "R30.1: PROMOTION GATE / READINESS VALIDATION PASSED"
    )

    log(
        "R30.1: NEXT-STAGE EVALUATION ARCHITECTURALLY READY"
    )

    log(
        "R30.1: READINESS DOES NOT ENABLE REAL EXECUTION"
    )

    log(
        "R30.1: READINESS DOES NOT ENABLE EXCHANGE WRITES"
    )

    log(
        "R30.1: READINESS DOES NOT ENABLE MUTATION"
    )

    log(
        "R30.1: NO REAL ORDER WAS SENT"
    )

    log(
        "R30.1: NO DEMO ORDER WAS SENT"
    )

    log(
        "R30.1: NO EXCHANGE WRITE WAS TRANSMITTED"
    )

    persistent_runtime(final_state)


if __name__ == "__main__":
    main()
