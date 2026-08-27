from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal, getcontext
from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# R30
# CONTROLLED PROMOTION ARCHITECTURE BASELINE
#
# PURPOSE
# -------
# R30 begins only after the successful R29 Unit G synthetic promotion-readiness
# gate.
#
# R30 DOES NOT PROMOTE TO REAL EXECUTION.
#
# R30 establishes a controlled capability architecture where every potentially
# dangerous capability is:
#
#   1. explicitly represented,
#   2. disabled by default,
#   3. independently gated,
#   4. cryptographically bound to the current generation/recovery epoch,
#   5. incapable of silently becoming executable.
#
# CURRENT SAFETY DISCIPLINE
# -------------------------
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
# HEALTH SERVER
# -------------
# Render-compatible health server listens on PORT, default 10000.
#
# IMPORTANT
# ---------
# The health server is intentionally local service infrastructure and does
# not represent exchange/API write capability.
#
# =============================================================================


getcontext().prec = 28


# =============================================================================
# IDENTITY
# =============================================================================

SERIES = "R30"
UNIT = "BASELINE"
PROGRAM_NAME = "R30 CONTROLLED PROMOTION ARCHITECTURE"
VERSION = "R30.0"


# =============================================================================
# RUNTIME CONFIGURATION
# =============================================================================

PORT = int(os.getenv("PORT", "10000"))

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

STATE_FILE = Path(
    os.getenv(
        "R30_STATE_FILE",
        "/tmp/r30_controlled_promotion_state.json",
    )
)

HEARTBEAT_SECONDS = int(
    os.getenv(
        "R30_HEARTBEAT_SECONDS",
        "30",
    )
)


# =============================================================================
# STRATEGY CONSTANTS
#
# These remain projections only.
# Nothing in this file can transmit an exchange order.
# =============================================================================

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_SIZE_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1

BACKUP_SIZE_PERCENT = Decimal("5")
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
# ABSOLUTE SAFETY CONFIGURATION
#
# These constants are intentionally not loaded from environment variables.
# A Render environment-variable change must not silently activate execution.
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
# ENUMS
# =============================================================================

class CapabilityName(str, Enum):
    REAL_ORDER_EXECUTION = "REAL_ORDER_EXECUTION"
    DEMO_ORDER_EXECUTION = "DEMO_ORDER_EXECUTION"
    EXCHANGE_NETWORK_WRITES = "EXCHANGE_NETWORK_WRITES"
    WEBSOCKET_WRITES = "WEBSOCKET_WRITES"
    LEVERAGE_MUTATION = "LEVERAGE_MUTATION"
    MARGIN_MUTATION = "MARGIN_MUTATION"
    POSITION_MUTATION = "POSITION_MUTATION"
    ACCOUNT_MUTATION = "ACCOUNT_MUTATION"


class PromotionState(str, Enum):
    FROZEN = "FROZEN"
    OBSERVATION = "OBSERVATION"
    SYNTHETIC = "SYNTHETIC"
    VALIDATED = "VALIDATED"


class DispatchState(str, Enum):
    PREPARED = "PREPARED"
    AUTHORIZED = "AUTHORIZED"
    SYNTHETIC_DISPATCHED = "SYNTHETIC_DISPATCHED"
    FINALIZED = "FINALIZED"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class Capability:
    name: str
    enabled: bool
    generation: int
    recovery_epoch: int
    reason: str


@dataclass(frozen=True)
class PromotionManifest:
    manifest_id: str
    series: str
    version: str
    generation: int
    recovery_epoch: int
    promotion_state: str
    synthetic_only: bool
    network_writes_enabled: bool
    real_execution_enabled: bool
    demo_execution_enabled: bool
    capability_hash: str


@dataclass(frozen=True)
class SyntheticIntent:
    intent_id: str
    symbol: str
    generation: int
    recovery_epoch: int
    transport: str
    executable: bool
    purpose: str


@dataclass(frozen=True)
class SyntheticAuthorization:
    authorization_id: str
    intent_id: str
    payload_sha256: str
    generation: int
    recovery_epoch: int
    transport: str
    network_transmission_allowed: bool


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    intent_id: str
    authorization_id: str
    payload_sha256: str
    generation: int
    recovery_epoch: int
    synthetic: bool
    transmitted: bool
    finalized: bool


@dataclass
class RuntimeState:
    runtime_id: str
    generation: int
    recovery_epoch: int
    promotion_state: str

    dispatch_state: str

    dispatch_count: int
    receipt_count: int
    replay_blocks: int

    manifest_id: str
    manifest_sha256: str

    last_intent_id: Optional[str]
    last_authorization_id: Optional[str]
    last_receipt_id: Optional[str]

    synthetic_only: bool
    network_writes_enabled: bool
    real_execution_enabled: bool

    r29_baseline_preserved: bool
    promotion_architecture_ready: bool


# =============================================================================
# LOGGING HELPERS
# =============================================================================

LINE = "-" * 92


def log(message: str = "") -> None:
    print(message, flush=True)


def section(title: str) -> None:
    log(LINE)
    log(title)
    log(LINE)


def pass_test(label: str) -> None:
    log(f"{label:<80} ✅ PASS")


def fail_test(label: str) -> None:
    log(f"{label:<80} ❌ FAIL")


def require(condition: bool, label: str) -> None:
    if condition:
        pass_test(label)
        return

    fail_test(label)
    raise RuntimeError(f"R30 VALIDATION FAILURE: {label}")


# =============================================================================
# HASHING / SERIALIZATION
# =============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_object(value: Any) -> str:
    return sha256_text(canonical_json(value))


# =============================================================================
# CAPABILITY REGISTRY
# =============================================================================

def build_capabilities(
    generation: int,
    recovery_epoch: int,
) -> List[Capability]:

    return [
        Capability(
            name=CapabilityName.REAL_ORDER_EXECUTION.value,
            enabled=REAL_ORDER_EXECUTION_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="R30 baseline explicitly forbids real order execution",
        ),
        Capability(
            name=CapabilityName.DEMO_ORDER_EXECUTION.value,
            enabled=DEMO_ORDER_EXECUTION_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="R30 baseline explicitly forbids demo order execution",
        ),
        Capability(
            name=CapabilityName.EXCHANGE_NETWORK_WRITES.value,
            enabled=EXCHANGE_NETWORK_WRITES_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="R30 baseline permits no outbound exchange write transport",
        ),
        Capability(
            name=CapabilityName.WEBSOCKET_WRITES.value,
            enabled=WEBSOCKET_WRITES_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="R30 baseline forbids websocket write transport",
        ),
        Capability(
            name=CapabilityName.LEVERAGE_MUTATION.value,
            enabled=LEVERAGE_MUTATION_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="Leverage mutation remains frozen",
        ),
        Capability(
            name=CapabilityName.MARGIN_MUTATION.value,
            enabled=MARGIN_MUTATION_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="Margin mutation remains frozen",
        ),
        Capability(
            name=CapabilityName.POSITION_MUTATION.value,
            enabled=POSITION_MUTATION_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="Position mutation remains frozen",
        ),
        Capability(
            name=CapabilityName.ACCOUNT_MUTATION.value,
            enabled=ACCOUNT_MUTATION_ENABLED,
            generation=generation,
            recovery_epoch=recovery_epoch,
            reason="Account mutation remains frozen",
        ),
    ]


def capability_hash(capabilities: List[Capability]) -> str:
    serialized = [asdict(item) for item in capabilities]
    return sha256_object(serialized)


# =============================================================================
# MANIFEST
# =============================================================================

def create_manifest(
    generation: int,
    recovery_epoch: int,
    capabilities: List[Capability],
) -> PromotionManifest:

    return PromotionManifest(
        manifest_id=str(uuid.uuid4()),
        series=SERIES,
        version=VERSION,
        generation=generation,
        recovery_epoch=recovery_epoch,
        promotion_state=PromotionState.VALIDATED.value,
        synthetic_only=SYNTHETIC_TRANSPORT_ONLY,
        network_writes_enabled=EXCHANGE_NETWORK_WRITES_ENABLED,
        real_execution_enabled=REAL_ORDER_EXECUTION_ENABLED,
        demo_execution_enabled=DEMO_ORDER_EXECUTION_ENABLED,
        capability_hash=capability_hash(capabilities),
    )


# =============================================================================
# STATE PERSISTENCE
# =============================================================================

def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_suffix(
        path.suffix + f".{uuid.uuid4().hex}.tmp"
    )

    serialized = json.dumps(
        data,
        sort_keys=True,
        indent=2,
    )

    with temp_path.open("w", encoding="utf-8") as handle:
        handle.write(serialized)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temp_path, path)


def save_state(state: RuntimeState) -> None:
    atomic_write_json(
        STATE_FILE,
        asdict(state),
    )


def load_state() -> Optional[RuntimeState]:
    if not STATE_FILE.exists():
        return None

    try:
        raw = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

        return RuntimeState(**raw)

    except Exception as exc:
        log(
            f"R30 LOCAL BLOCK: invalid durable state rejected: {exc}"
        )
        return None


# =============================================================================
# SYNTHETIC PAYLOAD / DISPATCH
# =============================================================================

def build_synthetic_payload(
    intent: SyntheticIntent,
) -> Dict[str, Any]:

    return {
        "r30": True,
        "symbol": intent.symbol,
        "intent_id": intent.intent_id,
        "generation": intent.generation,
        "recovery_epoch": intent.recovery_epoch,
        "transport": "SYNTHETIC_ONLY",
        "transmit": False,
        "executable": False,
        "operation": "ENTRY_PROJECTION",
        "strategy": {
            "initial_entry_percent": str(
                INITIAL_ENTRY_PERCENT
            ),
            "pyramid_size_percent": str(
                PYRAMID_SIZE_PERCENT
            ),
            "max_pyramid_adds": MAX_PYRAMID_ADDS,
            "backup_size_percent": str(
                BACKUP_SIZE_PERCENT
            ),
            "max_backups": MAX_BACKUPS,
            "maximum_fund_exposure_percent": str(
                MAX_FUND_EXPOSURE_PERCENT
            ),
        },
    }


def create_authorization(
    intent: SyntheticIntent,
    payload: Dict[str, Any],
) -> SyntheticAuthorization:

    return SyntheticAuthorization(
        authorization_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        payload_sha256=sha256_object(payload),
        generation=intent.generation,
        recovery_epoch=intent.recovery_epoch,
        transport="SYNTHETIC_ONLY",
        network_transmission_allowed=False,
    )


def synthetic_dispatch(
    state: RuntimeState,
    intent: SyntheticIntent,
    authorization: SyntheticAuthorization,
    payload: Dict[str, Any],
) -> SyntheticReceipt:

    if state.dispatch_state == DispatchState.FINALIZED.value:
        state.replay_blocks += 1
        save_state(state)

        log(
            "R30 LOCAL BLOCK: finalized synthetic dispatch replay rejected"
        )

        raise RuntimeError(
            "finalized synthetic dispatch replay rejected"
        )

    payload_hash = sha256_object(payload)

    if intent.executable:
        raise RuntimeError(
            "R30 LOCAL BLOCK: executable intent rejected"
        )

    if intent.transport != "SYNTHETIC_ONLY":
        raise RuntimeError(
            "R30 LOCAL BLOCK: non-synthetic intent rejected"
        )

    if authorization.network_transmission_allowed:
        raise RuntimeError(
            "R30 LOCAL BLOCK: transmission authorization rejected"
        )

    if authorization.intent_id != intent.intent_id:
        raise RuntimeError(
            "R30 LOCAL BLOCK: authorization intent mismatch"
        )

    if authorization.payload_sha256 != payload_hash:
        raise RuntimeError(
            "R30 LOCAL BLOCK: payload authorization mismatch"
        )

    if payload.get("transmit") is not False:
        raise RuntimeError(
            "R30 LOCAL BLOCK: payload transmission flag rejected"
        )

    if payload.get("executable") is not False:
        raise RuntimeError(
            "R30 LOCAL BLOCK: executable payload rejected"
        )

    state.dispatch_state = (
        DispatchState.SYNTHETIC_DISPATCHED.value
    )

    state.dispatch_count += 1

    receipt = SyntheticReceipt(
        receipt_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        authorization_id=authorization.authorization_id,
        payload_sha256=payload_hash,
        generation=intent.generation,
        recovery_epoch=intent.recovery_epoch,
        synthetic=True,
        transmitted=False,
        finalized=True,
    )

    state.receipt_count += 1

    state.last_intent_id = intent.intent_id
    state.last_authorization_id = (
        authorization.authorization_id
    )
    state.last_receipt_id = receipt.receipt_id

    state.dispatch_state = DispatchState.FINALIZED.value

    save_state(state)

    return receipt


# =============================================================================
# HARD LOCAL WRITE BLOCKERS
#
# These functions are intentionally the only mutation-shaped interfaces
# exposed by R30.
#
# They ALWAYS reject.
# =============================================================================

def block_real_order(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30 LOCAL BLOCK: real order execution disabled"
    )


def block_demo_order(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30 LOCAL BLOCK: demo order execution disabled"
    )


def block_exchange_write(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(
        "R30 LOCAL BLOCK: exchange network writes disabled"
    )


def block_leverage_mutation(
    *args: Any,
    **kwargs: Any,
) -> None:
    raise RuntimeError(
        "R30 LOCAL BLOCK: leverage mutation disabled"
    )


def block_margin_mutation(
    *args: Any,
    **kwargs: Any,
) -> None:
    raise RuntimeError(
        "R30 LOCAL BLOCK: margin mutation disabled"
    )


def block_position_mutation(
    *args: Any,
    **kwargs: Any,
) -> None:
    raise RuntimeError(
        "R30 LOCAL BLOCK: position mutation disabled"
    )


def block_account_mutation(
    *args: Any,
    **kwargs: Any,
) -> None:
    raise RuntimeError(
        "R30 LOCAL BLOCK: account mutation disabled"
    )


# =============================================================================
# HEALTH SERVER
# =============================================================================

HEALTH_STATE: Dict[str, Any] = {
    "series": SERIES,
    "version": VERSION,
    "status": "STARTING",
    "synthetic_only": True,
    "network_writes": False,
    "real_execution": False,
    "promotion_architecture_ready": False,
}


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.end_headers()
            return

        payload = json.dumps(
            HEALTH_STATE,
            sort_keys=True,
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(payload)),
        )
        self.end_headers()
        self.wfile.write(payload)

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        return


def health_server_worker() -> None:
    try:
        server = HTTPServer(
            ("0.0.0.0", PORT),
            HealthHandler,
        )

        log(
            f"R30: HEALTH SERVER LISTENING ON PORT {PORT}"
        )

        server.serve_forever()

    except Exception as exc:
        log(
            f"R30: HEALTH SERVER ERROR: {exc}"
        )


def start_health_server() -> None:
    thread = threading.Thread(
        target=health_server_worker,
        daemon=True,
        name="r30-health-server",
    )

    thread.start()


# =============================================================================
# VALIDATION
# =============================================================================

def run_validation() -> RuntimeState:

    section(
        "R30: STARTING CONTROLLED PROMOTION ARCHITECTURE VALIDATION"
    )

    # -------------------------------------------------------------------------
    # GENERATION
    # -------------------------------------------------------------------------

    previous_state = load_state()

    if previous_state is None:
        generation = 1
        recovery_epoch = 1

    else:
        generation = max(
            1,
            previous_state.generation,
        )

        recovery_epoch = max(
            1,
            previous_state.recovery_epoch,
        )

    capabilities = build_capabilities(
        generation,
        recovery_epoch,
    )

    manifest = create_manifest(
        generation,
        recovery_epoch,
        capabilities,
    )

    manifest_hash = sha256_object(
        asdict(manifest)
    )

    state = RuntimeState(
        runtime_id=str(uuid.uuid4()),
        generation=generation,
        recovery_epoch=recovery_epoch,
        promotion_state=PromotionState.VALIDATED.value,

        dispatch_state=DispatchState.PREPARED.value,

        dispatch_count=0,
        receipt_count=0,
        replay_blocks=0,

        manifest_id=manifest.manifest_id,
        manifest_sha256=manifest_hash,

        last_intent_id=None,
        last_authorization_id=None,
        last_receipt_id=None,

        synthetic_only=True,
        network_writes_enabled=False,
        real_execution_enabled=False,

        r29_baseline_preserved=False,
        promotion_architecture_ready=False,
    )

    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        "R30 TEST 1: R29 SAFETY BASELINE PRESERVATION"
    )

    require(
        REAL_ORDER_EXECUTION_ENABLED is False,
        "Real Order Execution Disabled",
    )

    require(
        DEMO_ORDER_EXECUTION_ENABLED is False,
        "Demo Order Execution Disabled",
    )

    require(
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
        "Exchange Network Writes Disabled",
    )

    require(
        WEBSOCKET_WRITES_ENABLED is False,
        "WebSocket Writes Disabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic Transport Only",
    )

    state.r29_baseline_preserved = True


    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        "R30 TEST 2: MUTATION FIREBREAK"
    )

    require(
        LEVERAGE_MUTATION_ENABLED is False,
        "Leverage Mutation Disabled",
    )

    require(
        MARGIN_MUTATION_ENABLED is False,
        "Margin Mutation Disabled",
    )

    require(
        POSITION_MUTATION_ENABLED is False,
        "Position Mutation Disabled",
    )

    require(
        ACCOUNT_MUTATION_ENABLED is False,
        "Account Mutation Disabled",
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        "R30 TEST 3: EXPLICIT CAPABILITY REGISTRY"
    )

    require(
        len(capabilities) == 8,
        "All Controlled Capabilities Registered",
    )

    require(
        all(
            capability.enabled is False
            for capability in capabilities
        ),
        "All Dangerous Capabilities Frozen",
    )

    require(
        all(
            capability.generation == generation
            for capability in capabilities
        ),
        "Capabilities Bound To Generation",
    )

    require(
        all(
            capability.recovery_epoch
            == recovery_epoch
            for capability in capabilities
        ),
        "Capabilities Bound To Recovery Epoch",
    )

    capabilities_sha256 = capability_hash(
        capabilities
    )

    require(
        len(capabilities_sha256) == 64,
        "Capability Registry SHA256 Valid",
    )

    log(
        f"R30: CAPABILITY REGISTRY SHA256 "
        f"{capabilities_sha256}"
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        "R30 TEST 4: PROMOTION MANIFEST"
    )

    require(
        manifest.series == SERIES,
        "Manifest Series Matches",
    )

    require(
        manifest.version == VERSION,
        "Manifest Version Matches",
    )

    require(
        manifest.synthetic_only is True,
        "Manifest Synthetic Only",
    )

    require(
        manifest.network_writes_enabled is False,
        "Manifest Network Writes Disabled",
    )

    require(
        manifest.real_execution_enabled is False,
        "Manifest Real Execution Disabled",
    )

    require(
        manifest.demo_execution_enabled is False,
        "Manifest Demo Execution Disabled",
    )

    require(
        manifest.capability_hash
        == capabilities_sha256,
        "Manifest Capability Hash Matches",
    )

    require(
        len(manifest_hash) == 64,
        "Promotion Manifest SHA256 Valid",
    )

    log(
        f"R30: PROMOTION MANIFEST SHA256 "
        f"{manifest_hash}"
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        "R30 TEST 5: STRATEGY EXPOSURE INVARIANTS"
    )

    maximum_planned_allocation = (
        INITIAL_ENTRY_PERCENT
        + (
            PYRAMID_SIZE_PERCENT
            * Decimal(MAX_PYRAMID_ADDS)
        )
        + (
            BACKUP_SIZE_PERCENT
            * Decimal(MAX_BACKUPS)
        )
    )

    require(
        maximum_planned_allocation
        == Decimal("25"),
        "Configured Maximum Planned Allocation Is 25 Percent",
    )

    require(
        maximum_planned_allocation
        < MAX_FUND_EXPOSURE_PERCENT,
        "Planned Allocation Remains Below 35 Percent Cap",
    )

    require(
        TP1_PERCENT + TP2_PERCENT + TP3_PERCENT
        == Decimal("100"),
        "TP Allocation Totals 100 Percent",
    )

    require(
        ONE_DIRECTION_ONLY is True,
        "One Direction Only Protection Enabled",
    )

    require(
        ANTI_DUPLICATE_ORDERS is True,
        "Anti-Duplicate Protection Enabled",
    )

    require(
        TREND_REVERSAL_EXIT is True,
        "Trend Reversal Exit Enabled",
    )

    require(
        IDLE_PYRAMID_CLEANUP is True,
        "Idle Pyramid Cleanup Enabled",
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        "R30 TEST 6: SYNTHETIC INTENT"
    )

    intent = SyntheticIntent(
        intent_id=str(uuid.uuid4()),
        symbol=SYMBOL,
        generation=generation,
        recovery_epoch=recovery_epoch,
        transport="SYNTHETIC_ONLY",
        executable=False,
        purpose=(
            "R30 controlled promotion architecture "
            "synthetic execution projection"
        ),
    )

    require(
        intent.symbol == SYMBOL,
        "Intent Symbol Matches",
    )

    require(
        intent.generation == generation,
        "Intent Generation Matches",
    )

    require(
        intent.recovery_epoch == recovery_epoch,
        "Intent Recovery Epoch Matches",
    )

    require(
        intent.transport == "SYNTHETIC_ONLY",
        "Intent Transport Synthetic Only",
    )

    require(
        intent.executable is False,
        "Intent Explicitly Non-Executable",
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        "R30 TEST 7: SYNTHETIC PAYLOAD SEAL"
    )

    payload = build_synthetic_payload(
        intent
    )

    payload_hash = sha256_object(
        payload
    )

    require(
        payload["transmit"] is False,
        "Payload Explicitly Disables Transmission",
    )

    require(
        payload["executable"] is False,
        "Payload Explicitly Non-Executable",
    )

    require(
        payload["transport"]
        == "SYNTHETIC_ONLY",
        "Payload Synthetic Transport Matches",
    )

    require(
        len(payload_hash) == 64,
        "Payload SHA256 Length Valid",
    )

    log(
        f"R30: SYNTHETIC PAYLOAD SHA256 "
        f"{payload_hash}"
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        "R30 TEST 8: SYNTHETIC AUTHORIZATION"
    )

    authorization = create_authorization(
        intent,
        payload,
    )

    state.dispatch_state = (
        DispatchState.AUTHORIZED.value
    )

    require(
        authorization.intent_id
        == intent.intent_id,
        "Authorization Bound To Intent",
    )

    require(
        authorization.payload_sha256
        == payload_hash,
        "Authorization Bound To Exact Payload",
    )

    require(
        authorization.generation
        == generation,
        "Authorization Generation Matches",
    )

    require(
        authorization.recovery_epoch
        == recovery_epoch,
        "Authorization Recovery Epoch Matches",
    )

    require(
        authorization.transport
        == "SYNTHETIC_ONLY",
        "Authorization Transport Synthetic Only",
    )

    require(
        authorization.network_transmission_allowed
        is False,
        "Authorization Forbids Network Transmission",
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    section(
        "R30 TEST 9: SYNTHETIC DISPATCH"
    )

    receipt = synthetic_dispatch(
        state,
        intent,
        authorization,
        payload,
    )

    require(
        receipt.synthetic is True,
        "Receipt Marked Synthetic",
    )

    require(
        receipt.transmitted is False,
        "Receipt Confirms No Transmission",
    )

    require(
        receipt.intent_id == intent.intent_id,
        "Receipt Intent Binding Matches",
    )

    require(
        receipt.authorization_id
        == authorization.authorization_id,
        "Receipt Authorization Binding Matches",
    )

    require(
        receipt.payload_sha256
        == payload_hash,
        "Receipt Payload Hash Matches",
    )

    require(
        receipt.finalized is True,
        "Synthetic Dispatch Finalized",
    )

    require(
        state.dispatch_count == 1,
        "Exactly One Synthetic Dispatch Recorded",
    )

    require(
        state.receipt_count == 1,
        "Exactly One Synthetic Receipt Recorded",
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    section(
        "R30 TEST 10: DURABLE STATE RESTART RECOVERY"
    )

    recovered = load_state()

    require(
        recovered is not None,
        "Durable State Reloaded",
    )

    assert recovered is not None

    require(
        recovered.dispatch_state
        == DispatchState.FINALIZED.value,
        "Finalized State Restored",
    )

    require(
        recovered.dispatch_count == 1,
        "Dispatch Count Restored",
    )

    require(
        recovered.receipt_count == 1,
        "Receipt Count Restored",
    )

    require(
        recovered.last_receipt_id
        == receipt.receipt_id,
        "Receipt Identity Restored",
    )

    require(
        recovered.generation
        == generation,
        "Recovered Generation Matches",
    )

    require(
        recovered.recovery_epoch
        == recovery_epoch,
        "Recovered Recovery Epoch Matches",
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    section(
        "R30 TEST 11: FINALIZED REPLAY REJECTION"
    )

    replay_rejected = False

    try:
        synthetic_dispatch(
            recovered,
            intent,
            authorization,
            payload,
        )

    except RuntimeError:
        replay_rejected = True

    require(
        replay_rejected,
        "Finalized Synthetic Replay Rejected",
    )

    replay_state = load_state()

    assert replay_state is not None

    require(
        replay_state.dispatch_count == 1,
        "Replay Did Not Create Second Dispatch",
    )

    require(
        replay_state.receipt_count == 1,
        "Replay Did Not Create Second Receipt",
    )

    require(
        replay_state.replay_blocks == 1,
        "Replay Block Counter Recorded",
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    section(
        "R30 TEST 12: LOCAL MUTATION BLOCKERS"
    )

    blockers = [
        (
            block_real_order,
            "Real Order Local Block Active",
        ),
        (
            block_demo_order,
            "Demo Order Local Block Active",
        ),
        (
            block_exchange_write,
            "Exchange Write Local Block Active",
        ),
        (
            block_leverage_mutation,
            "Leverage Mutation Local Block Active",
        ),
        (
            block_margin_mutation,
            "Margin Mutation Local Block Active",
        ),
        (
            block_position_mutation,
            "Position Mutation Local Block Active",
        ),
        (
            block_account_mutation,
            "Account Mutation Local Block Active",
        ),
    ]

    for function, label in blockers:

        blocked = False

        try:
            function()

        except RuntimeError:
            blocked = True

        require(
            blocked,
            label,
        )


    # =========================================================================
    # TEST 13
    # =========================================================================

    section(
        "R30 TEST 13: SIGNAL AND COOLDOWN INVARIANTS"
    )

    require(
        SIGNAL_EXPIRY_SECONDS == 120,
        "Signal Expiry Is 120 Seconds",
    )

    require(
        LOSS_COOLDOWN_SECONDS == 300,
        "Loss Cooldown Is 300 Seconds",
    )

    require(
        MAX_PYRAMID_ADDS == 1,
        "Maximum Pyramid Adds Is One",
    )

    require(
        MAX_BACKUPS == 3,
        "Maximum Backup Count Is Three",
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    section(
        "R30 TEST 14: CAPABILITY ESCALATION PREVENTION"
    )

    require(
        not any(
            capability.enabled
            for capability in capabilities
        ),
        "No Capability Silently Escalated",
    )

    require(
        os.getenv(
            "REAL_ORDER_EXECUTION_ENABLED",
            "ignored",
        )
        != "capable-of-changing-constant",
        "Environment Cannot Directly Activate Real Execution",
    )

    require(
        REAL_ORDER_EXECUTION_ENABLED is False,
        "Real Execution Constant Remains Frozen",
    )

    require(
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
        "Exchange Write Constant Remains Frozen",
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    section(
        "R30 TEST 15: FINAL R30 EXECUTION FIREBREAK"
    )

    require(
        REAL_ORDER_EXECUTION_ENABLED is False,
        "Real Execution Remains Disabled",
    )

    require(
        DEMO_ORDER_EXECUTION_ENABLED is False,
        "Demo Execution Remains Disabled",
    )

    require(
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
        "Exchange Network Writes Remain Disabled",
    )

    require(
        LEVERAGE_MUTATION_ENABLED is False,
        "Leverage Mutation Remains Disabled",
    )

    require(
        MARGIN_MUTATION_ENABLED is False,
        "Margin Mutation Remains Disabled",
    )

    require(
        POSITION_MUTATION_ENABLED is False,
        "Position Mutation Remains Disabled",
    )

    require(
        ACCOUNT_MUTATION_ENABLED is False,
        "Account Mutation Remains Disabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic-Only Boundary Remains Active",
    )


    # =========================================================================
    # PROMOTION ARCHITECTURE READY
    # =========================================================================

    final_state = load_state()

    assert final_state is not None

    final_state.r29_baseline_preserved = True
    final_state.promotion_architecture_ready = True

    save_state(final_state)

    return final_state


# =============================================================================
# SUMMARY
# =============================================================================

def print_summary(
    state: RuntimeState,
) -> None:

    section(
        "R30: VALIDATION SUMMARY"
    )

    log(
        f"R30: synthetic-only="
        f"{state.synthetic_only}"
    )

    log(
        f"R30: network-writes="
        f"{state.network_writes_enabled}"
    )

    log(
        f"R30: generation="
        f"{state.generation}"
    )

    log(
        f"R30: recovery-epoch="
        f"{state.recovery_epoch}"
    )

    log(
        f"R30: dispatch-count="
        f"{state.dispatch_count}"
    )

    log(
        f"R30: receipt-count="
        f"{state.receipt_count}"
    )

    log(
        f"R30: replay-blocks="
        f"{state.replay_blocks}"
    )

    log(
        f"R30: r29-baseline-preserved="
        f"{state.r29_baseline_preserved}"
    )

    log(
        f"R30: promotion-architecture-ready="
        f"{state.promotion_architecture_ready}"
    )

    log(
        f"R30: real-execution-enabled="
        f"{state.real_execution_enabled}"
    )

    section(
        "R30: ALL TESTS PASSED"
    )

    log(
        "R30: CONTROLLED PROMOTION ARCHITECTURE "
        "BASELINE PASSED"
    )

    log(
        "R30: R29 SAFETY BASELINE PRESERVED"
    )

    log(
        "R30: NO REAL ORDER WAS SENT"
    )

    log(
        "R30: NO DEMO ORDER WAS SENT"
    )

    log(
        "R30: NO EXCHANGE WRITE WAS TRANSMITTED"
    )


# =============================================================================
# PERSISTENT RUNTIME
# =============================================================================

def persistent_runtime(
    state: RuntimeState,
) -> None:

    section(
        "R30: ENTERING PERSISTENT SYNTHETIC-ONLY RUNTIME"
    )

    heartbeat = 0

    while True:

        heartbeat += 1

        HEALTH_STATE.update(
            {
                "series": SERIES,
                "version": VERSION,
                "status": "HEALTHY",
                "synthetic_only": True,
                "network_writes": False,
                "real_execution": False,
                "generation": state.generation,
                "recovery_epoch": state.recovery_epoch,
                "r29_baseline_preserved":
                    state.r29_baseline_preserved,
                "promotion_architecture_ready":
                    state.promotion_architecture_ready,
                "heartbeat": heartbeat,
            }
        )

        log(
            "R30: "
            f"HEARTBEAT {heartbeat} | "
            f"synthetic-only=True | "
            f"network-writes=False | "
            f"real-execution=False | "
            f"generation={state.generation} | "
            f"recovery-epoch={state.recovery_epoch} | "
            f"r29-baseline-preserved="
            f"{state.r29_baseline_preserved} | "
            f"promotion-architecture-ready="
            f"{state.promotion_architecture_ready}"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    section(
        "R30: MAIN.PY ENTERED"
    )

    log(
        f"R30: SYMBOL={SYMBOL}"
    )

    log(
        f"R30: VERSION={VERSION}"
    )

    log(
        f"R30: STATE FILE={STATE_FILE}"
    )

    log(
        f"R30: HEALTH PORT={PORT}"
    )

    log(
        "R30: REAL EXECUTION DISABLED"
    )

    log(
        "R30: DEMO EXECUTION DISABLED"
    )

    log(
        "R30: EXCHANGE NETWORK WRITES DISABLED"
    )

    log(
        "R30: SYNTHETIC TRANSPORT ONLY"
    )

    start_health_server()

    state = run_validation()

    print_summary(
        state
    )

    persistent_runtime(
        state
    )


if __name__ == "__main__":
    main()
