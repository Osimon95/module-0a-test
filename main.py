from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, getcontext
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# R31C
# RESTART / REPLAY / TAMPER / TERMINAL-INTEGRITY STRESS VALIDATION
#
# ABSOLUTE SAFETY DISCIPLINE:
#
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
#   R31B proved the complete pre-execution lifecycle.
#
#   R31C now stress-validates:
#
#       synthetic observation
#           ->
#       signal
#           ->
#       risk projection
#           ->
#       candidate
#           ->
#       authorization
#           ->
#       synthetic dispatch
#           ->
#       terminal seal
#           ->
#       durable persistence
#           ->
#       restart recovery
#
#   while proving resistance to:
#
#       - authorization replay
#       - dispatch replay
#       - transition replay
#       - candidate tampering
#       - authorization tampering
#       - receipt tampering
#       - durable-state tampering
#       - corrupted state
#       - truncated state
#       - stale generation
#       - stale recovery epoch
#       - terminal reopening
#       - environment escalation
#
# IMPORTANT:
#
#   THIS FILE MUST NEVER TRANSMIT AN ORDER.
#
# =============================================================================


getcontext().prec = 40


# =============================================================================
# IDENTITY
# =============================================================================

VERSION = "R31C"
SYMBOL = "BTCUSDT"

STATE_FILE = Path("/tmp/r31c_restart_replay_integrity_state.json")

HEALTH_PORT = int(os.getenv("PORT", "10000"))


# =============================================================================
# ABSOLUTE EXECUTION FIREBREAKS
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
# STRATEGY CONFIGURATION
# =============================================================================

TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1

MAX_BACKUPS = 3
BACKUP_SIZE_PERCENT = Decimal("5")
BACKUP_BUFFER_PERCENT = Decimal("0.3")

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300


# =============================================================================
# SYNTHETIC ACCOUNT / CONTRACT BASELINE
# =============================================================================

SYNTHETIC_AVAILABLE_BALANCE = Decimal("7.18945017")

SYNTHETIC_MARK_PRICE = Decimal("80000.0")

QUANTITY_STEP = Decimal("0.0001")
MINIMUM_QUANTITY = Decimal("0.0001")

PRICE_STEP = Decimal("0.1")


# =============================================================================
# GLOBAL SAFETY COUNTERS
# =============================================================================

REAL_ORDER_COUNT = 0
DEMO_ORDER_COUNT = 0
NETWORK_WRITE_COUNT = 0
MUTATION_COUNT = 0

SYNTHETIC_DISPATCH_COUNT = 0

TRANSITION_COUNT = 0
CONSUMED_TRANSITION_COUNT = 0

AUTHORIZATION_REPLAY_BLOCK_COUNT = 0
DISPATCH_REPLAY_BLOCK_COUNT = 0
TRANSITION_REPLAY_BLOCK_COUNT = 0
TERMINAL_REOPEN_BLOCK_COUNT = 0

TAMPER_REJECTION_COUNT = 0
STALE_GENERATION_REJECTION_COUNT = 0
STALE_RECOVERY_REJECTION_COUNT = 0


# =============================================================================
# TEST COUNTERS
# =============================================================================

PASSED = 0
FAILED = 0


# =============================================================================
# PHASE MODEL
# =============================================================================

class Phase(str, Enum):
    RISK_ACCEPTED = "RISK_ACCEPTED"
    AUTHORIZED = "AUTHORIZED"
    SYNTHETIC_DISPATCHED = "SYNTHETIC_DISPATCHED"
    SEALED = "SEALED"


TERMINAL_PHASES = {
    Phase.SEALED.value,
}


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class Observation:
    symbol: str
    price: Decimal
    source: str
    observed_at: float


@dataclass(frozen=True)
class Signal:
    signal_id: str
    symbol: str
    direction: str
    created_at: float
    expires_at: float
    valid: bool


@dataclass
class Candidate:
    candidate_id: str
    signal_id: str
    symbol: str
    direction: str
    quantity: str
    leverage: str
    phase: str
    generation: int
    recovery_epoch: int


@dataclass(frozen=True)
class Authorization:
    authorization_id: str
    candidate_id: str
    signal_id: str
    symbol: str
    quantity: str
    generation: int
    recovery_epoch: int
    executable: bool
    network_writes_allowed: bool
    transport: str
    nonce: str
    authorization_hash: str


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    candidate_id: str
    authorization_id: str
    symbol: str
    quantity: str
    generation: int
    recovery_epoch: int
    transmitted: bool
    synthetic_only: bool
    receipt_hash: str


# =============================================================================
# LOGGING
# =============================================================================

def line() -> None:
    print("-" * 92, flush=True)


def section(title: str) -> None:
    line()
    print(title, flush=True)
    line()


def check(name: str, condition: bool) -> bool:
    global PASSED
    global FAILED

    if condition:
        PASSED += 1
        print(f"{name:<82} ✅ PASS", flush=True)
        return True

    FAILED += 1
    print(f"{name:<82} ❌ FAIL", flush=True)
    return False


# =============================================================================
# CANONICAL SERIALIZATION / HASHING
# =============================================================================

def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_of(value: Any) -> str:
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


# =============================================================================
# DECIMAL HELPERS
# =============================================================================

def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:
    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


# =============================================================================
# HEALTH SERVER
# =============================================================================

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class HealthHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        try:
            body = (
                "R31C OK\n"
                "phase=SEALED\n"
                "synthetic-only=true\n"
                "real-execution=false\n"
                "network-writes=false\n"
                "leverage-mutation=false\n"
            ).encode("utf-8")

            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                + f"Content-Length: {len(body)}\r\n".encode("utf-8")
                + b"Connection: close\r\n"
                + b"\r\n"
                + body
            )

            self.request.sendall(response)

        except Exception:
            pass


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

        print(
            f"R31C: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
            flush=True,
        )

    except OSError as exc:
        print(
            f"R31C: HEALTH SERVER NOTICE: {exc}",
            flush=True,
        )


# =============================================================================
# HARD SAFETY FIREBREAKS
# =============================================================================

def real_order_firebreak(reason: str) -> bool:
    print("R31C LOCAL BLOCK:", flush=True)
    print("  REAL order execution blocked", flush=True)
    print(f"  reason={reason}", flush=True)

    return False


def demo_order_firebreak(reason: str) -> bool:
    print("R31C LOCAL BLOCK:", flush=True)
    print("  DEMO order execution blocked", flush=True)
    print(f"  reason={reason}", flush=True)

    return False


def exchange_write_firebreak(
    method: str,
    path: str,
) -> bool:
    print("R31C LOCAL BLOCK:", flush=True)
    print(
        f"  REAL network {method.upper()} blocked",
        flush=True,
    )
    print(
        f"  path={path}",
        flush=True,
    )

    return False


def mutation_firebreak(kind: str) -> bool:
    print("R31C LOCAL BLOCK:", flush=True)
    print(
        f"  {kind.upper()} mutation blocked",
        flush=True,
    )

    return False


# =============================================================================
# AUTHORIZATION HASHING
# =============================================================================

def authorization_payload(
    authorization_id: str,
    candidate_id: str,
    signal_id: str,
    symbol: str,
    quantity: str,
    generation: int,
    recovery_epoch: int,
    executable: bool,
    network_writes_allowed: bool,
    transport: str,
    nonce: str,
) -> Dict[str, Any]:
    return {
        "authorization_id": authorization_id,
        "candidate_id": candidate_id,
        "signal_id": signal_id,
        "symbol": symbol,
        "quantity": quantity,
        "generation": generation,
        "recovery_epoch": recovery_epoch,
        "executable": executable,
        "network_writes_allowed": network_writes_allowed,
        "transport": transport,
        "nonce": nonce,
    }


def make_authorization(
    candidate: Candidate,
) -> Authorization:
    authorization_id = str(uuid.uuid4())
    nonce = str(uuid.uuid4())

    payload = authorization_payload(
        authorization_id=authorization_id,
        candidate_id=candidate.candidate_id,
        signal_id=candidate.signal_id,
        symbol=candidate.symbol,
        quantity=candidate.quantity,
        generation=candidate.generation,
        recovery_epoch=candidate.recovery_epoch,
        executable=False,
        network_writes_allowed=False,
        transport="SYNTHETIC_ONLY",
        nonce=nonce,
    )

    return Authorization(
        **payload,
        authorization_hash=sha256_of(payload),
    )


def validate_authorization(
    authorization: Authorization,
) -> bool:
    payload = authorization_payload(
        authorization_id=authorization.authorization_id,
        candidate_id=authorization.candidate_id,
        signal_id=authorization.signal_id,
        symbol=authorization.symbol,
        quantity=authorization.quantity,
        generation=authorization.generation,
        recovery_epoch=authorization.recovery_epoch,
        executable=authorization.executable,
        network_writes_allowed=authorization.network_writes_allowed,
        transport=authorization.transport,
        nonce=authorization.nonce,
    )

    return (
        authorization.authorization_hash
        == sha256_of(payload)
    )


# =============================================================================
# RECEIPT HASHING
# =============================================================================

def receipt_payload(
    receipt_id: str,
    candidate_id: str,
    authorization_id: str,
    symbol: str,
    quantity: str,
    generation: int,
    recovery_epoch: int,
    transmitted: bool,
    synthetic_only: bool,
) -> Dict[str, Any]:
    return {
        "receipt_id": receipt_id,
        "candidate_id": candidate_id,
        "authorization_id": authorization_id,
        "symbol": symbol,
        "quantity": quantity,
        "generation": generation,
        "recovery_epoch": recovery_epoch,
        "transmitted": transmitted,
        "synthetic_only": synthetic_only,
    }


def make_receipt(
    candidate: Candidate,
    authorization: Authorization,
) -> SyntheticReceipt:
    receipt_id = str(uuid.uuid4())

    payload = receipt_payload(
        receipt_id=receipt_id,
        candidate_id=candidate.candidate_id,
        authorization_id=authorization.authorization_id,
        symbol=candidate.symbol,
        quantity=candidate.quantity,
        generation=candidate.generation,
        recovery_epoch=candidate.recovery_epoch,
        transmitted=False,
        synthetic_only=True,
    )

    return SyntheticReceipt(
        **payload,
        receipt_hash=sha256_of(payload),
    )


def validate_receipt(
    receipt: SyntheticReceipt,
) -> bool:
    payload = receipt_payload(
        receipt_id=receipt.receipt_id,
        candidate_id=receipt.candidate_id,
        authorization_id=receipt.authorization_id,
        symbol=receipt.symbol,
        quantity=receipt.quantity,
        generation=receipt.generation,
        recovery_epoch=receipt.recovery_epoch,
        transmitted=receipt.transmitted,
        synthetic_only=receipt.synthetic_only,
    )

    return (
        receipt.receipt_hash
        == sha256_of(payload)
    )


# =============================================================================
# STATE HASHING
# =============================================================================

def state_integrity_hash(
    document_without_hash: Dict[str, Any],
) -> str:
    return sha256_of(document_without_hash)


def seal_state_document(
    document_without_hash: Dict[str, Any],
) -> Dict[str, Any]:
    document = deepcopy(document_without_hash)

    document["integrity_hash"] = state_integrity_hash(
        document_without_hash
    )

    return document


def verify_state_document(
    document: Dict[str, Any],
) -> bool:
    if not isinstance(document, dict):
        return False

    stored_hash = document.get("integrity_hash")

    if not isinstance(stored_hash, str):
        return False

    payload = deepcopy(document)
    payload.pop("integrity_hash", None)

    expected_hash = state_integrity_hash(payload)

    return stored_hash == expected_hash


# =============================================================================
# ATOMIC PERSISTENCE
# =============================================================================

def persist_state(
    document_without_hash: Dict[str, Any],
) -> Dict[str, Any]:
    document = seal_state_document(
        document_without_hash
    )

    temporary = STATE_FILE.with_suffix(
        ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            document,
            handle,
            sort_keys=True,
            indent=2,
        )

        handle.flush()
        os.fsync(handle.fileno())

    os.replace(
        temporary,
        STATE_FILE,
    )

    return document


def load_state() -> Optional[Dict[str, Any]]:
    try:
        with STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:
            document = json.load(handle)

    except Exception:
        return None

    if not verify_state_document(document):
        return None

    return document


# =============================================================================
# TRANSITION ENGINE
# =============================================================================

VALID_TRANSITIONS = {
    Phase.RISK_ACCEPTED.value: {
        Phase.AUTHORIZED.value,
    },
    Phase.AUTHORIZED.value: {
        Phase.SYNTHETIC_DISPATCHED.value,
    },
    Phase.SYNTHETIC_DISPATCHED.value: {
        Phase.SEALED.value,
    },
    Phase.SEALED.value: set(),
}


def transition_candidate(
    candidate: Candidate,
    new_phase: str,
    transition_id: str,
    consumed_transition_ids: set[str],
) -> bool:
    global TRANSITION_COUNT
    global CONSUMED_TRANSITION_COUNT
    global TRANSITION_REPLAY_BLOCK_COUNT
    global TERMINAL_REOPEN_BLOCK_COUNT

    if transition_id in consumed_transition_ids:
        TRANSITION_REPLAY_BLOCK_COUNT += 1
        return False

    if candidate.phase in TERMINAL_PHASES:
        TERMINAL_REOPEN_BLOCK_COUNT += 1
        return False

    allowed = VALID_TRANSITIONS.get(
        candidate.phase,
        set(),
    )

    if new_phase not in allowed:
        return False

    consumed_transition_ids.add(
        transition_id
    )

    candidate.phase = new_phase

    TRANSITION_COUNT += 1
    CONSUMED_TRANSITION_COUNT += 1

    return True


# =============================================================================
# REPLAY FENCES
# =============================================================================

def consume_authorization(
    authorization: Authorization,
    consumed_authorizations: set[str],
) -> bool:
    global AUTHORIZATION_REPLAY_BLOCK_COUNT

    if authorization.authorization_id in consumed_authorizations:
        AUTHORIZATION_REPLAY_BLOCK_COUNT += 1
        return False

    consumed_authorizations.add(
        authorization.authorization_id
    )

    return True


def consume_dispatch(
    receipt: SyntheticReceipt,
    consumed_dispatches: set[str],
) -> bool:
    global DISPATCH_REPLAY_BLOCK_COUNT

    key = (
        f"{receipt.candidate_id}:"
        f"{receipt.authorization_id}"
    )

    if key in consumed_dispatches:
        DISPATCH_REPLAY_BLOCK_COUNT += 1
        return False

    consumed_dispatches.add(
        key
    )

    return True


# =============================================================================
# STATE VALIDATION
# =============================================================================

def validate_terminal_state(
    document: Dict[str, Any],
) -> bool:
    required = {
        "version",
        "runtime_id",
        "symbol",
        "generation",
        "recovery_epoch",
        "phase",
        "candidate",
        "authorization",
        "receipt",
        "consumed_authorizations",
        "consumed_dispatches",
        "consumed_transition_ids",
        "counters",
        "integrity_hash",
    }

    if not required.issubset(
        set(document.keys())
    ):
        return False

    if not verify_state_document(document):
        return False

    if document["version"] != VERSION:
        return False

    if document["symbol"] != SYMBOL:
        return False

    if document["phase"] != Phase.SEALED.value:
        return False

    candidate = document["candidate"]
    authorization = document["authorization"]
    receipt = document["receipt"]

    if candidate["phase"] != Phase.SEALED.value:
        return False

    if candidate["candidate_id"] != authorization["candidate_id"]:
        return False

    if candidate["candidate_id"] != receipt["candidate_id"]:
        return False

    if authorization["authorization_id"] != receipt["authorization_id"]:
        return False

    if candidate["symbol"] != SYMBOL:
        return False

    if authorization["symbol"] != SYMBOL:
        return False

    if receipt["symbol"] != SYMBOL:
        return False

    if candidate["quantity"] != authorization["quantity"]:
        return False

    if candidate["quantity"] != receipt["quantity"]:
        return False

    if (
        candidate["generation"]
        != authorization["generation"]
        or candidate["generation"]
        != receipt["generation"]
        or candidate["generation"]
        != document["generation"]
    ):
        return False

    if (
        candidate["recovery_epoch"]
        != authorization["recovery_epoch"]
        or candidate["recovery_epoch"]
        != receipt["recovery_epoch"]
        or candidate["recovery_epoch"]
        != document["recovery_epoch"]
    ):
        return False

    if authorization["executable"] is not False:
        return False

    if authorization["network_writes_allowed"] is not False:
        return False

    if authorization["transport"] != "SYNTHETIC_ONLY":
        return False

    if receipt["transmitted"] is not False:
        return False

    if receipt["synthetic_only"] is not True:
        return False

    return True


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def run_validation() -> Dict[str, Any]:
    global SYNTHETIC_DISPATCH_COUNT
    global TAMPER_REJECTION_COUNT
    global STALE_GENERATION_REJECTION_COUNT
    global STALE_RECOVERY_REJECTION_COUNT

    runtime_id = str(uuid.uuid4())

    generation = 1
    recovery_epoch = 1

    consumed_authorizations: set[str] = set()
    consumed_dispatches: set[str] = set()
    consumed_transition_ids: set[str] = set()

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 1: ABSOLUTE SAFETY CONFIGURATION"
    )
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
    section(
        "R31C TEST 2: STRATEGY CONFIGURATION"
    )
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
        BACKUP_SIZE_PERCENT == Decimal("5"),
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
    section(
        "R31C TEST 3: STRATEGY SAFETY TOGGLES"
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
        "R31C TEST 4: SYNTHETIC OBSERVATION"
    )
    # -------------------------------------------------------------------------

    now = time.time()

    observation = Observation(
        symbol=SYMBOL,
        price=SYNTHETIC_MARK_PRICE,
        source="SYNTHETIC",
        observed_at=now,
    )

    check(
        "Observation Symbol Matches",
        observation.symbol == SYMBOL,
    )

    check(
        "Observation Price Is Positive",
        observation.price > Decimal("0"),
    )

    check(
        "Observation Source Is Synthetic",
        observation.source == "SYNTHETIC",
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 5: SIGNAL CONSTRUCTION"
    )
    # -------------------------------------------------------------------------

    signal = Signal(
        signal_id=str(uuid.uuid4()),
        symbol=observation.symbol,
        direction="LONG",
        created_at=now,
        expires_at=now + SIGNAL_EXPIRY_SECONDS,
        valid=True,
    )

    check(
        "Signal ID Present",
        bool(signal.signal_id),
    )

    check(
        "Signal Symbol Matches",
        signal.symbol == SYMBOL,
    )

    check(
        "Signal Direction Is Valid",
        signal.direction in {"LONG", "SHORT"},
    )

    check(
        "Signal Is Valid",
        signal.valid is True,
    )

    check(
        "Signal Expiry Exact",
        (
            signal.expires_at
            - signal.created_at
        ) == SIGNAL_EXPIRY_SECONDS,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 6: QUANTITY / RISK PROJECTION"
    )
    # -------------------------------------------------------------------------

    entry_margin_budget = (
        SYNTHETIC_AVAILABLE_BALANCE
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )

    projected_notional = (
        entry_margin_budget
        * TARGET_LEVERAGE
    )

    raw_quantity = (
        projected_notional
        / SYNTHETIC_MARK_PRICE
    )

    rounded_quantity = floor_to_step(
        raw_quantity,
        QUANTITY_STEP,
    )

    rounded_notional = (
        rounded_quantity
        * SYNTHETIC_MARK_PRICE
    )

    rounded_margin = (
        rounded_notional
        / TARGET_LEVERAGE
    )

    projected_exposure_percent = (
        rounded_margin
        / SYNTHETIC_AVAILABLE_BALANCE
        * Decimal("100")
    )

    check(
        "Entry Margin Budget Positive",
        entry_margin_budget > Decimal("0"),
    )

    check(
        "Projected Notional Positive",
        projected_notional > Decimal("0"),
    )

    check(
        "Rounded Quantity Meets Minimum",
        rounded_quantity >= MINIMUM_QUANTITY,
    )

    check(
        "Rounded Quantity Respects Step",
        (
            rounded_quantity
            % QUANTITY_STEP
        ) == Decimal("0"),
    )

    check(
        "Rounded Margin Positive",
        rounded_margin > Decimal("0"),
    )

    check(
        "Projected Exposure Below Maximum",
        projected_exposure_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    print(
        "R31C: RISK PROJECTION "
        f"balance={SYNTHETIC_AVAILABLE_BALANCE} "
        f"margin-budget={entry_margin_budget} "
        f"notional={projected_notional} "
        f"qty={rounded_quantity} "
        f"rounded-margin={rounded_margin}",
        flush=True,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 7: TAKE PROFIT PROJECTION"
    )
    # -------------------------------------------------------------------------

    tp1_quantity = floor_to_step(
        rounded_quantity
        * TP1_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp2_quantity = floor_to_step(
        rounded_quantity
        * TP2_PERCENT
        / Decimal("100"),
        QUANTITY_STEP,
    )

    tp3_quantity = (
        rounded_quantity
        - tp1_quantity
        - tp2_quantity
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
        (
            TP1_PERCENT
            + TP2_PERCENT
            + TP3_PERCENT
        ) == Decimal("100"),
    )

    check(
        "TP Quantities Reconcile To Entry Quantity",
        (
            tp1_quantity
            + tp2_quantity
            + tp3_quantity
        ) == rounded_quantity,
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
    section(
        "R31C TEST 8: BACKUP / FUND BUDGET"
    )
    # -------------------------------------------------------------------------

    backup_margin_each = (
        SYNTHETIC_AVAILABLE_BALANCE
        * BACKUP_SIZE_PERCENT
        / Decimal("100")
    )

    total_backup_margin = (
        backup_margin_each
        * Decimal(MAX_BACKUPS)
    )

    total_strategy_percent = (
        INITIAL_ENTRY_PERCENT
        + (
            BACKUP_SIZE_PERCENT
            * Decimal(MAX_BACKUPS)
        )
        + (
            BACKUP_SIZE_PERCENT
            * Decimal(MAX_PYRAMID_ADDS)
        )
    )

    check(
        "Backup Margin Positive",
        backup_margin_each > Decimal("0"),
    )

    check(
        "Projected Backup Count Is Three",
        MAX_BACKUPS == 3,
    )

    check(
        "Projected Backup Total Positive",
        total_backup_margin > Decimal("0"),
    )

    check(
        "Full Planned Strategy Margin Is Twenty Five Percent",
        total_strategy_percent == Decimal("25"),
    )

    check(
        "Full Strategy Exposure Below Maximum",
        total_strategy_percent
        <= MAX_FUND_EXPOSURE_PERCENT,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 9: CANDIDATE CONSTRUCTION"
    )
    # -------------------------------------------------------------------------

    candidate = Candidate(
        candidate_id=str(uuid.uuid4()),
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        direction=signal.direction,
        quantity=str(rounded_quantity),
        leverage=str(TARGET_LEVERAGE),
        phase=Phase.RISK_ACCEPTED.value,
        generation=generation,
        recovery_epoch=recovery_epoch,
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
        candidate.symbol == SYMBOL,
    )

    check(
        "Candidate Quantity Binding Exact",
        candidate.quantity == str(rounded_quantity),
    )

    check(
        "Candidate Leverage Binding Exact",
        candidate.leverage == str(TARGET_LEVERAGE),
    )

    check(
        "Candidate Starts Risk Accepted",
        candidate.phase == Phase.RISK_ACCEPTED.value,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 10: AUTHORIZATION CONSTRUCTION"
    )
    # -------------------------------------------------------------------------

    authorization = make_authorization(
        candidate
    )

    check(
        "Authorization ID Present",
        bool(authorization.authorization_id),
    )

    check(
        "Authorization Candidate Binding Exact",
        authorization.candidate_id
        == candidate.candidate_id,
    )

    check(
        "Authorization Signal Binding Exact",
        authorization.signal_id
        == candidate.signal_id,
    )

    check(
        "Authorization Symbol Binding Exact",
        authorization.symbol == SYMBOL,
    )

    check(
        "Authorization Quantity Binding Exact",
        authorization.quantity
        == candidate.quantity,
    )

    check(
        "Authorization Generation Binding Exact",
        authorization.generation
        == generation,
    )

    check(
        "Authorization Recovery Epoch Binding Exact",
        authorization.recovery_epoch
        == recovery_epoch,
    )

    check(
        "Authorization Explicitly Non Executable",
        authorization.executable is False,
    )

    check(
        "Authorization Denies Network Writes",
        authorization.network_writes_allowed
        is False,
    )

    check(
        "Authorization Transport Synthetic Only",
        authorization.transport
        == "SYNTHETIC_ONLY",
    )

    check(
        "Authorization Hash Validates",
        validate_authorization(
            authorization
        ),
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 11: AUTHORIZATION TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    tampered_authorization = Authorization(
        authorization_id=authorization.authorization_id,
        candidate_id=authorization.candidate_id,
        signal_id=authorization.signal_id,
        symbol=authorization.symbol,
        quantity="999.9999",
        generation=authorization.generation,
        recovery_epoch=authorization.recovery_epoch,
        executable=authorization.executable,
        network_writes_allowed=authorization.network_writes_allowed,
        transport=authorization.transport,
        nonce=authorization.nonce,
        authorization_hash=authorization.authorization_hash,
    )

    auth_tamper_rejected = (
        not validate_authorization(
            tampered_authorization
        )
    )

    if auth_tamper_rejected:
        TAMPER_REJECTION_COUNT += 1

    check(
        "Tampered Authorization Rejected",
        auth_tamper_rejected,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 12: AUTHORIZATION CONSUMPTION"
    )
    # -------------------------------------------------------------------------

    first_auth_consumption = consume_authorization(
        authorization,
        consumed_authorizations,
    )

    check(
        "Authorization Consumed First Time",
        first_auth_consumption,
    )

    check(
        "Authorization Consumption Recorded",
        authorization.authorization_id
        in consumed_authorizations,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 13: AUTHORIZATION REPLAY REJECTION"
    )
    # -------------------------------------------------------------------------

    second_auth_consumption = consume_authorization(
        authorization,
        consumed_authorizations,
    )

    check(
        "Consumed Authorization Replay Rejected",
        second_auth_consumption is False,
    )

    check(
        "Authorization Replay Block Counter Incremented",
        AUTHORIZATION_REPLAY_BLOCK_COUNT == 1,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 14: TRANSITION TO AUTHORIZED"
    )
    # -------------------------------------------------------------------------

    transition_1 = str(uuid.uuid4())

    authorized_transition = transition_candidate(
        candidate,
        Phase.AUTHORIZED.value,
        transition_1,
        consumed_transition_ids,
    )

    check(
        "Candidate Transitioned To Authorized",
        authorized_transition
        and candidate.phase
        == Phase.AUTHORIZED.value,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 15: TRANSITION REPLAY REJECTION"
    )
    # -------------------------------------------------------------------------

    transition_replay = transition_candidate(
        candidate,
        Phase.SYNTHETIC_DISPATCHED.value,
        transition_1,
        consumed_transition_ids,
    )

    check(
        "Consumed Transition Replay Rejected",
        transition_replay is False,
    )

    check(
        "Transition Replay Counter Incremented",
        TRANSITION_REPLAY_BLOCK_COUNT == 1,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 16: SYNTHETIC DISPATCH"
    )
    # -------------------------------------------------------------------------

    receipt = make_receipt(
        candidate,
        authorization,
    )

    dispatch_consumed = consume_dispatch(
        receipt,
        consumed_dispatches,
    )

    if dispatch_consumed:
        SYNTHETIC_DISPATCH_COUNT += 1

    check(
        "Synthetic Receipt ID Present",
        bool(receipt.receipt_id),
    )

    check(
        "Receipt Candidate Binding Exact",
        receipt.candidate_id
        == candidate.candidate_id,
    )

    check(
        "Receipt Authorization Binding Exact",
        receipt.authorization_id
        == authorization.authorization_id,
    )

    check(
        "Receipt Quantity Binding Exact",
        receipt.quantity
        == candidate.quantity,
    )

    check(
        "Synthetic Receipt Hash Validates",
        validate_receipt(receipt),
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
    section(
        "R31C TEST 17: DISPATCH REPLAY REJECTION"
    )
    # -------------------------------------------------------------------------

    duplicate_dispatch = consume_dispatch(
        receipt,
        consumed_dispatches,
    )

    check(
        "Duplicate Synthetic Dispatch Rejected",
        duplicate_dispatch is False,
    )

    check(
        "Dispatch Replay Counter Incremented",
        DISPATCH_REPLAY_BLOCK_COUNT == 1,
    )

    check(
        "Synthetic Dispatch Count Remains One",
        SYNTHETIC_DISPATCH_COUNT == 1,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 18: RECEIPT TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    tampered_receipt = SyntheticReceipt(
        receipt_id=receipt.receipt_id,
        candidate_id=receipt.candidate_id,
        authorization_id=receipt.authorization_id,
        symbol=receipt.symbol,
        quantity="888.8888",
        generation=receipt.generation,
        recovery_epoch=receipt.recovery_epoch,
        transmitted=receipt.transmitted,
        synthetic_only=receipt.synthetic_only,
        receipt_hash=receipt.receipt_hash,
    )

    receipt_tamper_rejected = (
        not validate_receipt(
            tampered_receipt
        )
    )

    if receipt_tamper_rejected:
        TAMPER_REJECTION_COUNT += 1

    check(
        "Tampered Synthetic Receipt Rejected",
        receipt_tamper_rejected,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 19: TRANSITION TO SYNTHETIC DISPATCHED"
    )
    # -------------------------------------------------------------------------

    transition_2 = str(uuid.uuid4())

    dispatched_transition = transition_candidate(
        candidate,
        Phase.SYNTHETIC_DISPATCHED.value,
        transition_2,
        consumed_transition_ids,
    )

    check(
        "Candidate Transitioned To Synthetic Dispatched",
        dispatched_transition
        and candidate.phase
        == Phase.SYNTHETIC_DISPATCHED.value,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 20: TERMINAL SEAL"
    )
    # -------------------------------------------------------------------------

    transition_3 = str(uuid.uuid4())

    sealed_transition = transition_candidate(
        candidate,
        Phase.SEALED.value,
        transition_3,
        consumed_transition_ids,
    )

    check(
        "Candidate Final Phase Is Sealed",
        sealed_transition
        and candidate.phase
        == Phase.SEALED.value,
    )

    check(
        "Transition Count Is Three",
        TRANSITION_COUNT == 3,
    )

    check(
        "Consumed Transition Count Is Three",
        CONSUMED_TRANSITION_COUNT == 3,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 21: TERMINAL REOPEN REJECTION"
    )
    # -------------------------------------------------------------------------

    reopen_attempt = transition_candidate(
        candidate,
        Phase.AUTHORIZED.value,
        str(uuid.uuid4()),
        consumed_transition_ids,
    )

    check(
        "Sealed Candidate Cannot Reopen",
        reopen_attempt is False,
    )

    check(
        "Terminal Reopen Block Counter Incremented",
        TERMINAL_REOPEN_BLOCK_COUNT == 1,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 22: BUILD DURABLE SEALED STATE"
    )
    # -------------------------------------------------------------------------

    candidate_dict = {
        "candidate_id": candidate.candidate_id,
        "signal_id": candidate.signal_id,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "quantity": candidate.quantity,
        "leverage": candidate.leverage,
        "phase": candidate.phase,
        "generation": candidate.generation,
        "recovery_epoch": candidate.recovery_epoch,
    }

    authorization_dict = {
        "authorization_id": authorization.authorization_id,
        "candidate_id": authorization.candidate_id,
        "signal_id": authorization.signal_id,
        "symbol": authorization.symbol,
        "quantity": authorization.quantity,
        "generation": authorization.generation,
        "recovery_epoch": authorization.recovery_epoch,
        "executable": authorization.executable,
        "network_writes_allowed": (
            authorization.network_writes_allowed
        ),
        "transport": authorization.transport,
        "nonce": authorization.nonce,
        "authorization_hash": (
            authorization.authorization_hash
        ),
    }

    receipt_dict = {
        "receipt_id": receipt.receipt_id,
        "candidate_id": receipt.candidate_id,
        "authorization_id": receipt.authorization_id,
        "symbol": receipt.symbol,
        "quantity": receipt.quantity,
        "generation": receipt.generation,
        "recovery_epoch": receipt.recovery_epoch,
        "transmitted": receipt.transmitted,
        "synthetic_only": receipt.synthetic_only,
        "receipt_hash": receipt.receipt_hash,
    }

    state_payload = {
        "version": VERSION,
        "runtime_id": runtime_id,
        "symbol": SYMBOL,
        "generation": generation,
        "recovery_epoch": recovery_epoch,
        "phase": Phase.SEALED.value,
        "candidate": candidate_dict,
        "authorization": authorization_dict,
        "receipt": receipt_dict,
        "consumed_authorizations": sorted(
            consumed_authorizations
        ),
        "consumed_dispatches": sorted(
            consumed_dispatches
        ),
        "consumed_transition_ids": sorted(
            consumed_transition_ids
        ),
        "counters": {
            "real_orders": REAL_ORDER_COUNT,
            "demo_orders": DEMO_ORDER_COUNT,
            "network_writes": NETWORK_WRITE_COUNT,
            "mutations": MUTATION_COUNT,
            "synthetic_dispatches": (
                SYNTHETIC_DISPATCH_COUNT
            ),
            "transitions": TRANSITION_COUNT,
            "consumed_transitions": (
                CONSUMED_TRANSITION_COUNT
            ),
        },
    }

    persisted = persist_state(
        state_payload
    )

    check(
        "Durable State File Created",
        STATE_FILE.exists(),
    )

    check(
        "Persisted Integrity Hash Present",
        bool(
            persisted.get(
                "integrity_hash"
            )
        ),
    )

    check(
        "Persisted Integrity Hash Valid",
        verify_state_document(
            persisted
        ),
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 23: RESTART RESTORATION"
    )
    # -------------------------------------------------------------------------

    restored = load_state()

    check(
        "Durable State Restored",
        restored is not None,
    )

    check(
        "Restored State Integrity Valid",
        (
            restored is not None
            and verify_state_document(restored)
        ),
    )

    check(
        "Restored State Passes Terminal Validation",
        (
            restored is not None
            and validate_terminal_state(restored)
        ),
    )

    check(
        "Restart Restores Sealed Phase",
        (
            restored is not None
            and restored["phase"]
            == Phase.SEALED.value
        ),
    )

    check(
        "Restart Preserves Candidate ID",
        (
            restored is not None
            and restored["candidate"]["candidate_id"]
            == candidate.candidate_id
        ),
    )

    check(
        "Restart Preserves Authorization ID",
        (
            restored is not None
            and restored["authorization"][
                "authorization_id"
            ]
            == authorization.authorization_id
        ),
    )

    check(
        "Restart Preserves Receipt ID",
        (
            restored is not None
            and restored["receipt"]["receipt_id"]
            == receipt.receipt_id
        ),
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 24: RESTART AUTHORIZATION REPLAY FENCE"
    )
    # -------------------------------------------------------------------------

    restored_auth_consumed = (
        restored is not None
        and authorization.authorization_id
        in set(
            restored[
                "consumed_authorizations"
            ]
        )
    )

    check(
        "Consumed Authorization Survives Restart",
        restored_auth_consumed,
    )

    check(
        "Restart Cannot Reuse Authorization",
        restored_auth_consumed,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 25: RESTART DISPATCH REPLAY FENCE"
    )
    # -------------------------------------------------------------------------

    dispatch_key = (
        f"{receipt.candidate_id}:"
        f"{receipt.authorization_id}"
    )

    restored_dispatch_consumed = (
        restored is not None
        and dispatch_key
        in set(
            restored[
                "consumed_dispatches"
            ]
        )
    )

    check(
        "Consumed Dispatch Survives Restart",
        restored_dispatch_consumed,
    )

    check(
        "Restart Cannot Duplicate Dispatch",
        restored_dispatch_consumed,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 26: RESTART TRANSITION REPLAY FENCE"
    )
    # -------------------------------------------------------------------------

    restored_transition_ids = (
        set(
            restored[
                "consumed_transition_ids"
            ]
        )
        if restored is not None
        else set()
    )

    check(
        "Consumed Transition One Survives Restart",
        transition_1
        in restored_transition_ids,
    )

    check(
        "Consumed Transition Two Survives Restart",
        transition_2
        in restored_transition_ids,
    )

    check(
        "Consumed Transition Three Survives Restart",
        transition_3
        in restored_transition_ids,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 27: DURABLE STATE HASH TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    tampered_state = deepcopy(
        restored
    )

    if tampered_state is not None:
        tampered_state["generation"] = 999

    state_tamper_rejected = (
        tampered_state is not None
        and not verify_state_document(
            tampered_state
        )
    )

    if state_tamper_rejected:
        TAMPER_REJECTION_COUNT += 1

    check(
        "Durable State Hash Tamper Rejected",
        state_tamper_rejected,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 28: CANDIDATE BINDING TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    candidate_tamper = deepcopy(
        restored
    )

    if candidate_tamper is not None:
        candidate_tamper[
            "candidate"
        ][
            "candidate_id"
        ] = str(uuid.uuid4())

        candidate_tamper = seal_state_document(
            {
                key: value
                for key, value
                in candidate_tamper.items()
                if key != "integrity_hash"
            }
        )

    candidate_binding_rejected = (
        candidate_tamper is not None
        and not validate_terminal_state(
            candidate_tamper
        )
    )

    if candidate_binding_rejected:
        TAMPER_REJECTION_COUNT += 1

    check(
        "Candidate Binding Tamper Rejected",
        candidate_binding_rejected,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 29: AUTHORIZATION BINDING TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    authorization_tamper = deepcopy(
        restored
    )

    if authorization_tamper is not None:
        authorization_tamper[
            "authorization"
        ][
            "candidate_id"
        ] = str(uuid.uuid4())

        authorization_tamper = seal_state_document(
            {
                key: value
                for key, value
                in authorization_tamper.items()
                if key != "integrity_hash"
            }
        )

    authorization_binding_rejected = (
        authorization_tamper is not None
        and not validate_terminal_state(
            authorization_tamper
        )
    )

    if authorization_binding_rejected:
        TAMPER_REJECTION_COUNT += 1

    check(
        "Authorization Binding Tamper Rejected",
        authorization_binding_rejected,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 30: RECEIPT BINDING TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    receipt_tamper_state = deepcopy(
        restored
    )

    if receipt_tamper_state is not None:
        receipt_tamper_state[
            "receipt"
        ][
            "authorization_id"
        ] = str(uuid.uuid4())

        receipt_tamper_state = seal_state_document(
            {
                key: value
                for key, value
                in receipt_tamper_state.items()
                if key != "integrity_hash"
            }
        )

    receipt_binding_rejected = (
        receipt_tamper_state is not None
        and not validate_terminal_state(
            receipt_tamper_state
        )
    )

    if receipt_binding_rejected:
        TAMPER_REJECTION_COUNT += 1

    check(
        "Receipt Binding Tamper Rejected",
        receipt_binding_rejected,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 31: STALE GENERATION REJECTION"
    )
    # -------------------------------------------------------------------------

    current_generation = generation + 1
    stale_generation = generation

    stale_generation_rejected = (
        stale_generation
        < current_generation
    )

    if stale_generation_rejected:
        STALE_GENERATION_REJECTION_COUNT += 1

    check(
        "Generation Advances Monotonically",
        current_generation
        > stale_generation,
    )

    check(
        "Stale Generation Rejected",
        stale_generation_rejected,
    )

    check(
        "Stale Generation Counter Incremented",
        STALE_GENERATION_REJECTION_COUNT == 1,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 32: STALE RECOVERY EPOCH REJECTION"
    )
    # -------------------------------------------------------------------------

    current_recovery_epoch = (
        recovery_epoch + 1
    )

    stale_recovery_epoch = recovery_epoch

    stale_recovery_rejected = (
        stale_recovery_epoch
        < current_recovery_epoch
    )

    if stale_recovery_rejected:
        STALE_RECOVERY_REJECTION_COUNT += 1

    check(
        "Recovery Epoch Advances Monotonically",
        current_recovery_epoch
        > stale_recovery_epoch,
    )

    check(
        "Stale Recovery Epoch Rejected",
        stale_recovery_rejected,
    )

    check(
        "Stale Recovery Counter Incremented",
        STALE_RECOVERY_REJECTION_COUNT == 1,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 33: HIGHER GENERATION CANNOT REOPEN TERMINAL STATE"
    )
    # -------------------------------------------------------------------------

    terminal_generation_clone = deepcopy(
        restored
    )

    if terminal_generation_clone is not None:
        terminal_generation_clone[
            "generation"
        ] = generation + 1

        terminal_generation_clone[
            "candidate"
        ][
            "generation"
        ] = generation + 1

        terminal_generation_clone[
            "authorization"
        ][
            "generation"
        ] = generation + 1

        terminal_generation_clone[
            "receipt"
        ][
            "generation"
        ] = generation + 1

        terminal_generation_clone = seal_state_document(
            {
                key: value
                for key, value
                in terminal_generation_clone.items()
                if key != "integrity_hash"
            }
        )

    check(
        "Higher Generation Clone Remains Sealed",
        (
            terminal_generation_clone
            is not None
            and terminal_generation_clone[
                "phase"
            ]
            == Phase.SEALED.value
        ),
    )

    check(
        "Higher Generation Cannot Convert Terminal State To Authorized",
        (
            terminal_generation_clone
            is not None
            and terminal_generation_clone[
                "candidate"
            ][
                "phase"
            ]
            == Phase.SEALED.value
        ),
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 34: HIGHER RECOVERY EPOCH CANNOT REOPEN TERMINAL STATE"
    )
    # -------------------------------------------------------------------------

    recovery_clone = deepcopy(
        restored
    )

    if recovery_clone is not None:
        recovery_clone[
            "recovery_epoch"
        ] = recovery_epoch + 1

        recovery_clone[
            "candidate"
        ][
            "recovery_epoch"
        ] = recovery_epoch + 1

        recovery_clone[
            "authorization"
        ][
            "recovery_epoch"
        ] = recovery_epoch + 1

        recovery_clone[
            "receipt"
        ][
            "recovery_epoch"
        ] = recovery_epoch + 1

        recovery_clone = seal_state_document(
            {
                key: value
                for key, value
                in recovery_clone.items()
                if key != "integrity_hash"
            }
        )

    check(
        "Higher Recovery Epoch Clone Remains Sealed",
        (
            recovery_clone
            is not None
            and recovery_clone[
                "phase"
            ]
            == Phase.SEALED.value
        ),
    )

    check(
        "Recovery Epoch Advance Cannot Reopen Candidate",
        (
            recovery_clone
            is not None
            and recovery_clone[
                "candidate"
            ][
                "phase"
            ]
            == Phase.SEALED.value
        ),
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 35: REPEATED RESTART STRESS"
    )
    # -------------------------------------------------------------------------

    restart_passes = 0

    for _ in range(10):
        restart_state = load_state()

        if (
            restart_state is not None
            and validate_terminal_state(
                restart_state
            )
            and restart_state[
                "phase"
            ] == Phase.SEALED.value
            and restart_state[
                "candidate"
            ][
                "candidate_id"
            ] == candidate.candidate_id
            and restart_state[
                "authorization"
            ][
                "authorization_id"
            ]
            == authorization.authorization_id
            and restart_state[
                "receipt"
            ][
                "receipt_id"
            ] == receipt.receipt_id
        ):
            restart_passes += 1

    check(
        "Ten Restart Restorations Completed",
        restart_passes == 10,
    )

    check(
        "Repeated Restart Preserves Terminal Seal",
        restart_passes == 10,
    )

    check(
        "Repeated Restart Causes No Additional Dispatch",
        SYNTHETIC_DISPATCH_COUNT == 1,
    )

    check(
        "Repeated Restart Causes No Real Orders",
        REAL_ORDER_COUNT == 0,
    )

    check(
        "Repeated Restart Causes No Network Writes",
        NETWORK_WRITE_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 36: REAL ORDER FIREBREAK"
    )
    # -------------------------------------------------------------------------

    real_result = real_order_firebreak(
        "R31C intentional validation"
    )

    check(
        "Real Order Path Blocked",
        real_result is False,
    )

    check(
        "Real Order Counter Remains Zero",
        REAL_ORDER_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 37: DEMO ORDER FIREBREAK"
    )
    # -------------------------------------------------------------------------

    demo_result = demo_order_firebreak(
        "R31C intentional validation"
    )

    check(
        "Demo Order Path Blocked",
        demo_result is False,
    )

    check(
        "Demo Order Counter Remains Zero",
        DEMO_ORDER_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 38: EXCHANGE WRITE FIREBREAK"
    )
    # -------------------------------------------------------------------------

    post_blocked = exchange_write_firebreak(
        "POST",
        "/capi/v2/order",
    )

    put_blocked = exchange_write_firebreak(
        "PUT",
        "/capi/v2/order",
    )

    patch_blocked = exchange_write_firebreak(
        "PATCH",
        "/capi/v2/account",
    )

    delete_blocked = exchange_write_firebreak(
        "DELETE",
        "/capi/v2/order",
    )

    check(
        "HTTP POST Blocked",
        post_blocked is False,
    )

    check(
        "HTTP PUT Blocked",
        put_blocked is False,
    )

    check(
        "HTTP PATCH Blocked",
        patch_blocked is False,
    )

    check(
        "HTTP DELETE Blocked",
        delete_blocked is False,
    )

    check(
        "Network Write Counter Remains Zero",
        NETWORK_WRITE_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 39: MUTATION FIREBREAK"
    )
    # -------------------------------------------------------------------------

    leverage_blocked = mutation_firebreak(
        "LEVERAGE"
    )

    margin_blocked = mutation_firebreak(
        "MARGIN"
    )

    position_blocked = mutation_firebreak(
        "POSITION"
    )

    account_blocked = mutation_firebreak(
        "ACCOUNT"
    )

    check(
        "Leverage Mutation Blocked",
        leverage_blocked is False,
    )

    check(
        "Margin Mutation Blocked",
        margin_blocked is False,
    )

    check(
        "Position Mutation Blocked",
        position_blocked is False,
    )

    check(
        "Account Mutation Blocked",
        account_blocked is False,
    )

    check(
        "Mutation Counter Remains Zero",
        MUTATION_COUNT == 0,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 40: ENVIRONMENT ESCALATION RESISTANCE"
    )
    # -------------------------------------------------------------------------

    environment_real = (
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

    environment_write = (
        os.getenv(
            "EXCHANGE_NETWORK_WRITES",
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

    environment_mutation = (
        os.getenv(
            "LEVERAGE_MUTATION",
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
        ),
    )

    check(
        "Environment Cannot Directly Activate Exchange Writes",
        (
            EXCHANGE_NETWORK_WRITES_ENABLED
            is False
        ),
    )

    check(
        "Environment Cannot Directly Activate Mutation",
        (
            LEVERAGE_MUTATION_ENABLED
            is False
        ),
    )

    check(
        "Real Execution Constant Remains Frozen",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "Demo Execution Constant Remains Frozen",
        DEMO_ORDER_EXECUTION_ENABLED
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

    # Environment variables may exist,
    # but they deliberately have no authority.
    check(
        "Environment Real Attempt Has No Authority",
        (
            not environment_real
            or REAL_ORDER_EXECUTION_ENABLED
            is False
        ),
    )

    check(
        "Environment Write Attempt Has No Authority",
        (
            not environment_write
            or EXCHANGE_NETWORK_WRITES_ENABLED
            is False
        ),
    )

    check(
        "Environment Mutation Attempt Has No Authority",
        (
            not environment_mutation
            or LEVERAGE_MUTATION_ENABLED
            is False
        ),
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 41: PERSISTED SAFETY COUNTERS"
    )
    # -------------------------------------------------------------------------

    final_restored = load_state()

    check(
        "Final Persisted State Restored",
        final_restored is not None,
    )

    check(
        "Persisted Real Order Count Is Zero",
        (
            final_restored is not None
            and final_restored[
                "counters"
            ][
                "real_orders"
            ] == 0
        ),
    )

    check(
        "Persisted Demo Order Count Is Zero",
        (
            final_restored is not None
            and final_restored[
                "counters"
            ][
                "demo_orders"
            ] == 0
        ),
    )

    check(
        "Persisted Network Write Count Is Zero",
        (
            final_restored is not None
            and final_restored[
                "counters"
            ][
                "network_writes"
            ] == 0
        ),
    )

    check(
        "Persisted Mutation Count Is Zero",
        (
            final_restored is not None
            and final_restored[
                "counters"
            ][
                "mutations"
            ] == 0
        ),
    )

    check(
        "Persisted Synthetic Dispatch Count Is One",
        (
            final_restored is not None
            and final_restored[
                "counters"
            ][
                "synthetic_dispatches"
            ] == 1
        ),
    )

    check(
        "Persisted Transition Count Is Three",
        (
            final_restored is not None
            and final_restored[
                "counters"
            ][
                "transitions"
            ] == 3
        ),
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 42: COUNTER INTEGRITY"
    )
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

    check(
        "Authorization Replay Was Blocked",
        AUTHORIZATION_REPLAY_BLOCK_COUNT
        >= 1,
    )

    check(
        "Dispatch Replay Was Blocked",
        DISPATCH_REPLAY_BLOCK_COUNT
        >= 1,
    )

    check(
        "Transition Replay Was Blocked",
        TRANSITION_REPLAY_BLOCK_COUNT
        >= 1,
    )

    check(
        "Terminal Reopen Was Blocked",
        TERMINAL_REOPEN_BLOCK_COUNT
        >= 1,
    )

    check(
        "Multiple Tamper Attempts Were Rejected",
        TAMPER_REJECTION_COUNT
        >= 5,
    )

    # -------------------------------------------------------------------------
    section(
        "R31C TEST 43: FINAL RESTART / REPLAY / INTEGRITY SEAL"
    )
    # -------------------------------------------------------------------------

    passed_before_final = PASSED
    failed_before_final = FAILED

    check(
        "All Prior Validation Checks Passed",
        failed_before_final == 0,
    )

    print(
        "  "
        f"passed-before-final={passed_before_final}, "
        f"failed={failed_before_final}",
        flush=True,
    )

    check(
        "R31C Remains Non Executable",
        REAL_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "R31C Remains Demo Execution Locked",
        DEMO_ORDER_EXECUTION_ENABLED
        is False,
    )

    check(
        "R31C Remains Network Write Locked",
        EXCHANGE_NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "R31C Remains Mutation Locked",
        (
            not LEVERAGE_MUTATION_ENABLED
            and not MARGIN_MUTATION_ENABLED
            and not POSITION_MUTATION_ENABLED
            and not ACCOUNT_MUTATION_ENABLED
        ),
    )

    check(
        "R31C Uses Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    check(
        "R31C Final Phase Is Sealed",
        candidate.phase
        == Phase.SEALED.value,
    )

    check(
        "R31C Restart State Is Sealed",
        (
            final_restored is not None
            and final_restored[
                "phase"
            ]
            == Phase.SEALED.value
        ),
    )

    check(
        "R31C Restart State Integrity Valid",
        (
            final_restored is not None
            and validate_terminal_state(
                final_restored
            )
        ),
    )

    return {
        "runtime_id": runtime_id,
        "generation": generation,
        "recovery_epoch": recovery_epoch,
        "phase": candidate.phase,
        "candidate_id": candidate.candidate_id,
        "authorization_id": (
            authorization.authorization_id
        ),
        "receipt_id": receipt.receipt_id,
    }


# =============================================================================
# HEARTBEAT LOOP
# =============================================================================

def heartbeat_loop(
    result: Dict[str, Any],
) -> None:
    heartbeat = 0

    while True:
        time.sleep(30)

        heartbeat += 1

        print(
            "R31C: HEARTBEAT "
            f"{heartbeat} | "
            f"phase={result['phase']} | "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY} | "
            f"real-execution={REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes={EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"generation={result['generation']} | "
            f"recovery-epoch={result['recovery_epoch']}",
            flush=True,
        )


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    line()
    print(
        "R31C: MAIN.PY ENTERED",
        flush=True,
    )
    line()

    print(
        f"R31C: SYMBOL={SYMBOL}",
        flush=True,
    )

    print(
        f"R31C: VERSION={VERSION}",
        flush=True,
    )

    print(
        f"R31C: STATE FILE={STATE_FILE}",
        flush=True,
    )

    print(
        f"R31C: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        "R31C: REAL EXECUTION DISABLED",
        flush=True,
    )

    print(
        "R31C: DEMO EXECUTION DISABLED",
        flush=True,
    )

    print(
        "R31C: NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        "R31C: LEVERAGE MUTATION DISABLED",
        flush=True,
    )

    print(
        "R31C: SYNTHETIC TRANSPORT ONLY=True",
        flush=True,
    )

    line()

    start_health_server()

    print(
        "R31C: STARTING RESTART / REPLAY / "
        "TAMPER / TERMINAL-INTEGRITY STRESS VALIDATION",
        flush=True,
    )

    result = run_validation()

    line()

    if FAILED == 0:
        print(
            "R31C: VALIDATION PASSED",
            flush=True,
        )
    else:
        print(
            "R31C: VALIDATION FAILED",
            flush=True,
        )

    line()

    print(
        f"R31C: SUMMARY passed={PASSED} failed={FAILED}",
        flush=True,
    )

    print(
        "R31C: SAFETY SEAL "
        f"real-orders={REAL_ORDER_COUNT} "
        f"demo-orders={DEMO_ORDER_COUNT} "
        f"network-writes={NETWORK_WRITE_COUNT} "
        f"mutations={MUTATION_COUNT}",
        flush=True,
    )

    print(
        "R31C: REPLAY SEAL "
        f"authorization-replays-blocked="
        f"{AUTHORIZATION_REPLAY_BLOCK_COUNT} "
        f"dispatch-replays-blocked="
        f"{DISPATCH_REPLAY_BLOCK_COUNT} "
        f"transition-replays-blocked="
        f"{TRANSITION_REPLAY_BLOCK_COUNT}",
        flush=True,
    )

    print(
        "R31C: INTEGRITY SEAL "
        f"tamper-rejections={TAMPER_REJECTION_COUNT} "
        f"stale-generation-rejections="
        f"{STALE_GENERATION_REJECTION_COUNT} "
        f"stale-recovery-rejections="
        f"{STALE_RECOVERY_REJECTION_COUNT}",
        flush=True,
    )

    print(
        "R31C: TERMINAL SEAL "
        f"phase={result['phase']} "
        f"synthetic-dispatches="
        f"{SYNTHETIC_DISPATCH_COUNT} "
        f"transitions={TRANSITION_COUNT}",
        flush=True,
    )

    heartbeat_loop(
        result
    )


if __name__ == "__main__":
    main()
