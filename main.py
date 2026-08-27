from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


# =============================================================================
# R32C
# SEALED CORRECTION AUTHORIZATION / SINGLE-CONSUMPTION VALIDATION
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
#   - NO CORRECTION TRANSMISSION
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE:
#
#   R32B SEALED 100X CORRECTION INTENT
#               |
#               v
#   EXACT INTENT VALIDATION
#               |
#               v
#   AUTHORIZATION REQUEST
#               |
#               v
#   AUTHORIZATION BINDING
#               |
#               v
#   SINGLE CONSUMPTION
#               |
#               v
#   REPLAY / STALE / TAMPER REJECTION
#               |
#               v
#   SYNTHETIC AUTHORIZATION RECEIPT
#
# IMPORTANT:
#   R32C DOES NOT TRANSMIT A LEVERAGE CHANGE.
#   R32C DOES NOT CALL ANY WEEX WRITE ENDPOINT.
#   R32C DOES NOT MUTATE ACCOUNT LEVERAGE.
#
# =============================================================================


VERSION = "R32C"
SYMBOL = "BTCUSDT"
MARGIN_MODE = "ISOLATED"

OBSERVED_LONG_LEVERAGE = 50
OBSERVED_SHORT_LEVERAGE = 20

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

GENERATION = 1
RECOVERY_EPOCH = 1

STATE_FILE = Path(
    os.getenv(
        "R32C_STATE_FILE",
        "/tmp/r32c_correction_authorization_state.json",
    )
)

HEALTH_PORT = int(os.getenv("PORT", "10000"))


# =============================================================================
# ABSOLUTE SAFETY LOCKS
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False
WEBSOCKET_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

CORRECTION_TRANSMISSION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# =============================================================================
# PHASES
# =============================================================================

PHASE_SEALED_INTENT = "SEALED_CORRECTION_INTENT"
PHASE_AUTHORIZATION_REQUESTED = "AUTHORIZATION_REQUESTED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_AUTHORIZATION_CONSUMED = "AUTHORIZATION_CONSUMED"


# =============================================================================
# COUNTERS
# =============================================================================

synthetic_dispatch_counter = 0
real_order_counter = 0
network_write_counter = 0
leverage_mutation_counter = 0

authorization_request_counter = 0
authorization_grant_counter = 0
authorization_consumption_counter = 0

authorization_denial_counter = 0
authorization_replay_rejection_counter = 0


# =============================================================================
# BASIC UTILITIES
# =============================================================================

def separator() -> None:
    print("-" * 92, flush=True)


def section(title: str) -> None:
    separator()
    print(title, flush=True)
    separator()


def check(name: str, condition: bool) -> None:
    if condition:
        print(f"{name:<80} ✅ PASS", flush=True)
        return

    print(f"{name:<80} ❌ FAIL", flush=True)
    raise AssertionError(name)


def canonical_json(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_data(data: Any) -> str:
    return hashlib.sha256(
        canonical_json(data).encode("utf-8")
    ).hexdigest()


def derive_lineage(
    symbol: str,
    generation: int,
    recovery_epoch: int,
) -> str:
    material = {
        "symbol": symbol,
        "generation": generation,
        "recovery_epoch": recovery_epoch,
        "purpose": "100x-leverage-correction",
    }
    return sha256_data(material)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True)
class CorrectionIntent:
    version: str

    intent_id: str

    symbol: str
    margin_mode: str

    observed_long_leverage: int
    observed_short_leverage: int

    target_long_leverage: int
    target_short_leverage: int

    generation: int
    recovery_epoch: int
    lineage: str

    synthetic_only: bool
    network_writes_enabled: bool
    leverage_mutation_enabled: bool

    correction_required: bool


@dataclass(frozen=True)
class AuthorizationRequest:
    request_id: str

    intent_id: str
    intent_hash: str

    symbol: str
    margin_mode: str

    target_long_leverage: int
    target_short_leverage: int

    generation: int
    recovery_epoch: int
    lineage: str

    authorization_nonce: str


@dataclass(frozen=True)
class AuthorizationGrant:
    authorization_id: str

    request_id: str

    intent_id: str
    intent_hash: str

    symbol: str
    margin_mode: str

    target_long_leverage: int
    target_short_leverage: int

    generation: int
    recovery_epoch: int
    lineage: str

    authorization_nonce: str

    single_use: bool
    synthetic_only: bool

    network_writes_enabled: bool
    leverage_mutation_enabled: bool


@dataclass
class RuntimeState:
    version: str

    phase: str

    generation: int
    recovery_epoch: int
    lineage: str

    intent_id: str
    intent_hash: str

    authorization_request_id: Optional[str]
    authorization_id: Optional[str]
    authorization_nonce: Optional[str]

    authorization_consumed: bool

    synthetic_dispatch_counter: int
    real_order_counter: int
    network_write_counter: int
    leverage_mutation_counter: int

    state_integrity_hash: str = ""


# =============================================================================
# R32B-COMPATIBLE CORRECTION INTENT
# =============================================================================

def build_correction_intent() -> CorrectionIntent:
    lineage = derive_lineage(
        SYMBOL,
        GENERATION,
        RECOVERY_EPOCH,
    )

    return CorrectionIntent(
        version=VERSION,
        intent_id=uuid.uuid4().hex,

        symbol=SYMBOL,
        margin_mode=MARGIN_MODE,

        observed_long_leverage=OBSERVED_LONG_LEVERAGE,
        observed_short_leverage=OBSERVED_SHORT_LEVERAGE,

        target_long_leverage=TARGET_LONG_LEVERAGE,
        target_short_leverage=TARGET_SHORT_LEVERAGE,

        generation=GENERATION,
        recovery_epoch=RECOVERY_EPOCH,
        lineage=lineage,

        synthetic_only=True,
        network_writes_enabled=False,
        leverage_mutation_enabled=False,

        correction_required=True,
    )


def intent_material(intent: CorrectionIntent) -> Dict[str, Any]:
    return asdict(intent)


def calculate_intent_hash(
    intent: CorrectionIntent,
) -> str:
    return sha256_data(
        intent_material(intent)
    )


# =============================================================================
# INTENT VALIDATION
# =============================================================================

def validate_exact_intent(
    intent: CorrectionIntent,
    expected_hash: str,
    generation: int,
    recovery_epoch: int,
    lineage: str,
) -> bool:

    if calculate_intent_hash(intent) != expected_hash:
        return False

    if intent.symbol != SYMBOL:
        return False

    if intent.margin_mode != MARGIN_MODE:
        return False

    if intent.target_long_leverage != 100:
        return False

    if intent.target_short_leverage != 100:
        return False

    if intent.generation != generation:
        return False

    if intent.recovery_epoch != recovery_epoch:
        return False

    if intent.lineage != lineage:
        return False

    if not intent.correction_required:
        return False

    if not intent.synthetic_only:
        return False

    if intent.network_writes_enabled:
        return False

    if intent.leverage_mutation_enabled:
        return False

    return True


# =============================================================================
# AUTHORIZATION REQUEST
# =============================================================================

def create_authorization_request(
    intent: CorrectionIntent,
    intent_hash: str,
) -> AuthorizationRequest:

    global authorization_request_counter
    authorization_request_counter += 1

    return AuthorizationRequest(
        request_id=uuid.uuid4().hex,

        intent_id=intent.intent_id,
        intent_hash=intent_hash,

        symbol=intent.symbol,
        margin_mode=intent.margin_mode,

        target_long_leverage=intent.target_long_leverage,
        target_short_leverage=intent.target_short_leverage,

        generation=intent.generation,
        recovery_epoch=intent.recovery_epoch,
        lineage=intent.lineage,

        authorization_nonce=uuid.uuid4().hex,
    )


# =============================================================================
# AUTHORIZATION REQUEST VALIDATION
# =============================================================================

def validate_authorization_request(
    request: AuthorizationRequest,
    intent: CorrectionIntent,
    expected_intent_hash: str,
) -> bool:

    if request.intent_id != intent.intent_id:
        return False

    if request.intent_hash != expected_intent_hash:
        return False

    if request.symbol != intent.symbol:
        return False

    if request.margin_mode != intent.margin_mode:
        return False

    if request.target_long_leverage != 100:
        return False

    if request.target_short_leverage != 100:
        return False

    if request.generation != intent.generation:
        return False

    if request.recovery_epoch != intent.recovery_epoch:
        return False

    if request.lineage != intent.lineage:
        return False

    if not request.authorization_nonce:
        return False

    return True


# =============================================================================
# AUTHORIZATION GRANT
# =============================================================================

def issue_authorization(
    request: AuthorizationRequest,
    intent: CorrectionIntent,
    expected_intent_hash: str,
) -> Optional[AuthorizationGrant]:

    global authorization_grant_counter
    global authorization_denial_counter

    valid = validate_authorization_request(
        request,
        intent,
        expected_intent_hash,
    )

    if not valid:
        authorization_denial_counter += 1
        return None

    authorization_grant_counter += 1

    return AuthorizationGrant(
        authorization_id=uuid.uuid4().hex,

        request_id=request.request_id,

        intent_id=request.intent_id,
        intent_hash=request.intent_hash,

        symbol=request.symbol,
        margin_mode=request.margin_mode,

        target_long_leverage=request.target_long_leverage,
        target_short_leverage=request.target_short_leverage,

        generation=request.generation,
        recovery_epoch=request.recovery_epoch,
        lineage=request.lineage,

        authorization_nonce=request.authorization_nonce,

        single_use=True,
        synthetic_only=True,

        network_writes_enabled=False,
        leverage_mutation_enabled=False,
    )


# =============================================================================
# AUTHORIZATION GRANT VALIDATION
# =============================================================================

def validate_authorization_grant(
    grant: AuthorizationGrant,
    request: AuthorizationRequest,
    intent: CorrectionIntent,
    expected_intent_hash: str,
) -> bool:

    if grant.request_id != request.request_id:
        return False

    if grant.intent_id != intent.intent_id:
        return False

    if grant.intent_hash != expected_intent_hash:
        return False

    if grant.symbol != SYMBOL:
        return False

    if grant.margin_mode != MARGIN_MODE:
        return False

    if grant.target_long_leverage != 100:
        return False

    if grant.target_short_leverage != 100:
        return False

    if grant.generation != intent.generation:
        return False

    if grant.recovery_epoch != intent.recovery_epoch:
        return False

    if grant.lineage != intent.lineage:
        return False

    if grant.authorization_nonce != request.authorization_nonce:
        return False

    if not grant.single_use:
        return False

    if not grant.synthetic_only:
        return False

    if grant.network_writes_enabled:
        return False

    if grant.leverage_mutation_enabled:
        return False

    return True


# =============================================================================
# STATE INTEGRITY
# =============================================================================

def state_hash_material(
    state: RuntimeState,
) -> Dict[str, Any]:

    data = asdict(state)
    data.pop("state_integrity_hash", None)

    return data


def calculate_state_integrity_hash(
    state: RuntimeState,
) -> str:
    return sha256_data(
        state_hash_material(state)
    )


def seal_state(
    state: RuntimeState,
) -> RuntimeState:

    state.state_integrity_hash = (
        calculate_state_integrity_hash(state)
    )

    return state


def validate_state_integrity(
    state: RuntimeState,
) -> bool:

    expected = calculate_state_integrity_hash(state)

    return (
        state.state_integrity_hash == expected
    )


def persist_state(
    state: RuntimeState,
) -> None:

    seal_state(state)

    payload = asdict(state)

    temporary = STATE_FILE.with_suffix(".tmp")

    temporary.write_text(
        json.dumps(
            payload,
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    os.replace(
        temporary,
        STATE_FILE,
    )


def restore_state() -> RuntimeState:

    payload = json.loads(
        STATE_FILE.read_text(
            encoding="utf-8"
        )
    )

    state = RuntimeState(**payload)

    if not validate_state_integrity(state):
        raise RuntimeError(
            "R32C state integrity validation failed"
        )

    return state


# =============================================================================
# SINGLE-CONSUMPTION AUTHORIZATION
# =============================================================================

def consume_authorization(
    state: RuntimeState,
    grant: AuthorizationGrant,
    request: AuthorizationRequest,
    intent: CorrectionIntent,
    expected_intent_hash: str,
) -> bool:

    global authorization_consumption_counter
    global authorization_replay_rejection_counter

    if state.authorization_consumed:
        authorization_replay_rejection_counter += 1
        return False

    if state.phase != PHASE_AUTHORIZED:
        return False

    if not validate_state_integrity(state):
        return False

    if not validate_authorization_grant(
        grant,
        request,
        intent,
        expected_intent_hash,
    ):
        return False

    if state.authorization_id != grant.authorization_id:
        return False

    if state.authorization_request_id != grant.request_id:
        return False

    if state.authorization_nonce != grant.authorization_nonce:
        return False

    if state.intent_id != grant.intent_id:
        return False

    if state.intent_hash != grant.intent_hash:
        return False

    if state.generation != grant.generation:
        return False

    if state.recovery_epoch != grant.recovery_epoch:
        return False

    if state.lineage != grant.lineage:
        return False

    # ---------------------------------------------------------------------
    # IMPORTANT:
    #
    # "Consumption" here means ONLY:
    #
    #   The authorization token has been logically consumed.
    #
    # It DOES NOT mean:
    #   - leverage changed
    #   - request transmitted
    #   - POST sent
    #   - exchange contacted
    # ---------------------------------------------------------------------

    state.authorization_consumed = True
    state.phase = PHASE_AUTHORIZATION_CONSUMED

    authorization_consumption_counter += 1

    persist_state(state)

    return True


# =============================================================================
# SYNTHETIC AUTHORIZATION RECEIPT
# =============================================================================

def build_synthetic_receipt(
    state: RuntimeState,
    grant: AuthorizationGrant,
) -> Dict[str, Any]:

    return {
        "version": VERSION,

        "transport": "SYNTHETIC",

        "intent_id": state.intent_id,
        "intent_hash": state.intent_hash,

        "authorization_id": grant.authorization_id,

        "symbol": grant.symbol,
        "margin_mode": grant.margin_mode,

        "target_long_leverage": (
            grant.target_long_leverage
        ),

        "target_short_leverage": (
            grant.target_short_leverage
        ),

        "authorization_consumed": (
            state.authorization_consumed
        ),

        "network_transmission": False,
        "leverage_mutation": False,

        "exchange_contacted": False,

        "generation": state.generation,
        "recovery_epoch": state.recovery_epoch,
        "lineage": state.lineage,
    }


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(
    socketserver.StreamRequestHandler
):

    def handle(self) -> None:

        try:
            self.request.recv(2048)

            body = (
                b"R32C OK\n"
                b"synthetic-only=true\n"
                b"network-writes=false\n"
                b"leverage-mutation=false\n"
            )

            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Connection: close\r\n"
                + (
                    f"Content-Length: {len(body)}\r\n"
                ).encode()
                + b"\r\n"
                + body
            )

            self.request.sendall(response)

        except Exception:
            pass


class ReusableTCPServer(
    socketserver.TCPServer
):
    allow_reuse_address = True


def start_health_server() -> None:

    def runner() -> None:

        with ReusableTCPServer(
            ("0.0.0.0", HEALTH_PORT),
            HealthHandler,
        ) as server:

            print(
                f"R32C: HEALTH SERVER LISTENING "
                f"ON PORT {HEALTH_PORT}",
                flush=True,
            )

            server.serve_forever()

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()


# =============================================================================
# STARTUP
# =============================================================================

section("R32C: MAIN.PY ENTERED")

print(
    f"R32C: SYMBOL={SYMBOL}",
    flush=True,
)

print(
    f"R32C: VERSION={VERSION}",
    flush=True,
)

print(
    f"R32C: STATE FILE={STATE_FILE}",
    flush=True,
)

print(
    f"R32C: HEALTH PORT={HEALTH_PORT}",
    flush=True,
)

print(
    "R32C: OBSERVED LEVERAGE "
    f"long={OBSERVED_LONG_LEVERAGE}x "
    f"short={OBSERVED_SHORT_LEVERAGE}x",
    flush=True,
)

print(
    "R32C: TARGET LEVERAGE "
    f"long={TARGET_LONG_LEVERAGE}x "
    f"short={TARGET_SHORT_LEVERAGE}x",
    flush=True,
)

print(
    "R32C: REAL EXECUTION DISABLED",
    flush=True,
)

print(
    "R32C: NETWORK WRITES DISABLED",
    flush=True,
)

print(
    "R32C: LEVERAGE MUTATION DISABLED",
    flush=True,
)

print(
    "R32C: SYNTHETIC TRANSPORT ONLY",
    flush=True,
)


start_health_server()


# =============================================================================
# TEST 1
# =============================================================================

section(
    "R32C TEST 1: HARD SAFETY CONFIGURATION"
)

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
    "Correction Transmission Disabled",
    CORRECTION_TRANSMISSION_ENABLED is False,
)

check(
    "Synthetic Transport Only",
    SYNTHETIC_TRANSPORT_ONLY is True,
)


# =============================================================================
# TEST 2
# =============================================================================

section(
    "R32C TEST 2: SEALED 100X INTENT CONSTRUCTION"
)

intent = build_correction_intent()

intent_hash = calculate_intent_hash(
    intent
)

check(
    "Intent Symbol Matches",
    intent.symbol == SYMBOL,
)

check(
    "Intent Margin Mode Is Isolated",
    intent.margin_mode == MARGIN_MODE,
)

check(
    "Intent Long Target Is 100x",
    intent.target_long_leverage == 100,
)

check(
    "Intent Short Target Is 100x",
    intent.target_short_leverage == 100,
)

check(
    "Correction Requirement Is True",
    intent.correction_required is True,
)

check(
    "Intent Is Synthetic Only",
    intent.synthetic_only is True,
)

check(
    "Intent Network Writes Disabled",
    intent.network_writes_enabled is False,
)

check(
    "Intent Leverage Mutation Disabled",
    intent.leverage_mutation_enabled is False,
)

print(
    f"R32C: INTENT ID={intent.intent_id}",
    flush=True,
)

print(
    f"R32C: INTENT HASH={intent_hash}",
    flush=True,
)


# =============================================================================
# TEST 3
# =============================================================================

section(
    "R32C TEST 3: EXACT INTENT VALIDATION"
)

check(
    "Exact Intent Accepted",
    validate_exact_intent(
        intent,
        intent_hash,
        GENERATION,
        RECOVERY_EPOCH,
        intent.lineage,
    ),
)


# =============================================================================
# TEST 4
# =============================================================================

section(
    "R32C TEST 4: AUTHORIZATION REQUEST CONSTRUCTION"
)

request = create_authorization_request(
    intent,
    intent_hash,
)

check(
    "Authorization Request ID Present",
    bool(request.request_id),
)

check(
    "Authorization Request Intent ID Matches",
    request.intent_id == intent.intent_id,
)

check(
    "Authorization Request Hash Matches",
    request.intent_hash == intent_hash,
)

check(
    "Authorization Request Symbol Matches",
    request.symbol == SYMBOL,
)

check(
    "Authorization Request Long Target Is 100x",
    request.target_long_leverage == 100,
)

check(
    "Authorization Request Short Target Is 100x",
    request.target_short_leverage == 100,
)

check(
    "Authorization Nonce Present",
    bool(request.authorization_nonce),
)


# =============================================================================
# TEST 5
# =============================================================================

section(
    "R32C TEST 5: AUTHORIZATION REQUEST BINDING"
)

check(
    "Exact Authorization Request Accepted",
    validate_authorization_request(
        request,
        intent,
        intent_hash,
    ),
)


# =============================================================================
# TEST 6
# =============================================================================

section(
    "R32C TEST 6: INTENT TAMPER REJECTION"
)

tampered_intent_data = asdict(intent)

tampered_intent_data[
    "target_long_leverage"
] = 99

tampered_intent = CorrectionIntent(
    **tampered_intent_data
)

check(
    "Tampered 99x Intent Rejected",
    not validate_exact_intent(
        tampered_intent,
        intent_hash,
        GENERATION,
        RECOVERY_EPOCH,
        intent.lineage,
    ),
)


# =============================================================================
# TEST 7
# =============================================================================

section(
    "R32C TEST 7: AUTHORIZATION REQUEST TAMPER REJECTION"
)

tampered_request_data = asdict(request)

tampered_request_data[
    "target_short_leverage"
] = 99

tampered_request = AuthorizationRequest(
    **tampered_request_data
)

check(
    "Tampered Authorization Request Rejected",
    not validate_authorization_request(
        tampered_request,
        intent,
        intent_hash,
    ),
)


# =============================================================================
# TEST 8
# =============================================================================

section(
    "R32C TEST 8: STALE GENERATION / EPOCH REJECTION"
)

stale_generation_data = asdict(
    request
)

stale_generation_data[
    "generation"
] = 0

stale_generation_request = (
    AuthorizationRequest(
        **stale_generation_data
    )
)

check(
    "Stale Generation Authorization Rejected",
    not validate_authorization_request(
        stale_generation_request,
        intent,
        intent_hash,
    ),
)


stale_epoch_data = asdict(
    request
)

stale_epoch_data[
    "recovery_epoch"
] = 0

stale_epoch_request = (
    AuthorizationRequest(
        **stale_epoch_data
    )
)

check(
    "Stale Recovery Epoch Authorization Rejected",
    not validate_authorization_request(
        stale_epoch_request,
        intent,
        intent_hash,
    ),
)


# =============================================================================
# TEST 9
# =============================================================================

section(
    "R32C TEST 9: SYMBOL / MARGIN / LINEAGE REJECTION"
)

wrong_symbol_data = asdict(
    request
)

wrong_symbol_data[
    "symbol"
] = "ETHUSDT"

wrong_symbol_request = (
    AuthorizationRequest(
        **wrong_symbol_data
    )
)

check(
    "Wrong Symbol Authorization Rejected",
    not validate_authorization_request(
        wrong_symbol_request,
        intent,
        intent_hash,
    ),
)


wrong_margin_data = asdict(
    request
)

wrong_margin_data[
    "margin_mode"
] = "CROSS"

wrong_margin_request = (
    AuthorizationRequest(
        **wrong_margin_data
    )
)

check(
    "Wrong Margin Authorization Rejected",
    not validate_authorization_request(
        wrong_margin_request,
        intent,
        intent_hash,
    ),
)


wrong_lineage_data = asdict(
    request
)

wrong_lineage_data[
    "lineage"
] = "forged-lineage"

wrong_lineage_request = (
    AuthorizationRequest(
        **wrong_lineage_data
    )
)

check(
    "Wrong Lineage Authorization Rejected",
    not validate_authorization_request(
        wrong_lineage_request,
        intent,
        intent_hash,
    ),
)


# =============================================================================
# TEST 10
# =============================================================================

section(
    "R32C TEST 10: SINGLE-USE AUTHORIZATION GRANT"
)

grant = issue_authorization(
    request,
    intent,
    intent_hash,
)

check(
    "Authorization Grant Created",
    grant is not None,
)

assert grant is not None

check(
    "Authorization Is Single Use",
    grant.single_use is True,
)

check(
    "Authorization Is Synthetic Only",
    grant.synthetic_only is True,
)

check(
    "Authorization Network Writes Disabled",
    grant.network_writes_enabled is False,
)

check(
    "Authorization Leverage Mutation Disabled",
    grant.leverage_mutation_enabled is False,
)

check(
    "Authorization Grant Exact Binding Validates",
    validate_authorization_grant(
        grant,
        request,
        intent,
        intent_hash,
    ),
)

print(
    f"R32C: AUTHORIZATION ID="
    f"{grant.authorization_id}",
    flush=True,
)


# =============================================================================
# TEST 11
# =============================================================================

section(
    "R32C TEST 11: AUTHORIZATION GRANT TAMPER REJECTION"
)

tampered_grant_data = asdict(
    grant
)

tampered_grant_data[
    "target_long_leverage"
] = 101

tampered_grant = AuthorizationGrant(
    **tampered_grant_data
)

check(
    "Tampered 101x Grant Rejected",
    not validate_authorization_grant(
        tampered_grant,
        request,
        intent,
        intent_hash,
    ),
)


nonce_tamper_data = asdict(
    grant
)

nonce_tamper_data[
    "authorization_nonce"
] = "forged-nonce"

nonce_tampered_grant = (
    AuthorizationGrant(
        **nonce_tamper_data
    )
)

check(
    "Authorization Nonce Tamper Rejected",
    not validate_authorization_grant(
        nonce_tampered_grant,
        request,
        intent,
        intent_hash,
    ),
)


# =============================================================================
# TEST 12
# =============================================================================

section(
    "R32C TEST 12: DURABLE AUTHORIZED STATE"
)

state = RuntimeState(
    version=VERSION,

    phase=PHASE_AUTHORIZED,

    generation=GENERATION,
    recovery_epoch=RECOVERY_EPOCH,
    lineage=intent.lineage,

    intent_id=intent.intent_id,
    intent_hash=intent_hash,

    authorization_request_id=(
        request.request_id
    ),

    authorization_id=(
        grant.authorization_id
    ),

    authorization_nonce=(
        grant.authorization_nonce
    ),

    authorization_consumed=False,

    synthetic_dispatch_counter=0,
    real_order_counter=0,
    network_write_counter=0,
    leverage_mutation_counter=0,
)

persist_state(state)

check(
    "Persisted State Exists",
    STATE_FILE.exists(),
)

check(
    "Authorized State Integrity Validates",
    validate_state_integrity(state),
)

check(
    "State Phase Is Authorized",
    state.phase == PHASE_AUTHORIZED,
)

check(
    "Authorization Initially Unconsumed",
    state.authorization_consumed is False,
)


# =============================================================================
# TEST 13
# =============================================================================

section(
    "R32C TEST 13: RESTART BEFORE CONSUMPTION"
)

restored_before = restore_state()

check(
    "Restart Restores Authorized Phase",
    restored_before.phase == PHASE_AUTHORIZED,
)

check(
    "Restart Preserves Intent ID",
    restored_before.intent_id
    == intent.intent_id,
)

check(
    "Restart Preserves Intent Hash",
    restored_before.intent_hash
    == intent_hash,
)

check(
    "Restart Preserves Authorization ID",
    restored_before.authorization_id
    == grant.authorization_id,
)

check(
    "Restart Preserves Authorization Nonce",
    restored_before.authorization_nonce
    == grant.authorization_nonce,
)

check(
    "Restart Preserves Unconsumed State",
    restored_before.authorization_consumed
    is False,
)


# =============================================================================
# TEST 14
# =============================================================================

section(
    "R32C TEST 14: AUTHORIZATION SINGLE CONSUMPTION"
)

consumed = consume_authorization(
    restored_before,
    grant,
    request,
    intent,
    intent_hash,
)

check(
    "Authorization Consumed Successfully",
    consumed is True,
)

check(
    "Authorization Consumption Count Is One",
    authorization_consumption_counter == 1,
)

check(
    "Phase Advanced To Authorization Consumed",
    (
        restored_before.phase
        == PHASE_AUTHORIZATION_CONSUMED
    ),
)

check(
    "Authorization Marked Consumed",
    (
        restored_before.authorization_consumed
        is True
    ),
)


# =============================================================================
# TEST 15
# =============================================================================

section(
    "R32C TEST 15: SAME-RUNTIME REPLAY REJECTION"
)

replay_result = consume_authorization(
    restored_before,
    grant,
    request,
    intent,
    intent_hash,
)

check(
    "Consumed Authorization Replay Rejected",
    replay_result is False,
)

check(
    "Consumption Counter Remains One",
    authorization_consumption_counter == 1,
)

check(
    "Replay Rejection Counter Increased",
    authorization_replay_rejection_counter
    >= 1,
)


# =============================================================================
# TEST 16
# =============================================================================

section(
    "R32C TEST 16: RESTART AFTER CONSUMPTION"
)

restored_after = restore_state()

check(
    "Restart Restores Consumed Phase",
    (
        restored_after.phase
        == PHASE_AUTHORIZATION_CONSUMED
    ),
)

check(
    "Restart Preserves Consumed Flag",
    restored_after.authorization_consumed
    is True,
)

check(
    "Restart Preserves Authorization ID",
    restored_after.authorization_id
    == grant.authorization_id,
)

check(
    "Restart Preserves Intent Hash",
    restored_after.intent_hash
    == intent_hash,
)


# =============================================================================
# TEST 17
# =============================================================================

section(
    "R32C TEST 17: POST-RESTART REPLAY REJECTION"
)

post_restart_replay = consume_authorization(
    restored_after,
    grant,
    request,
    intent,
    intent_hash,
)

check(
    "Post-Restart Authorization Replay Rejected",
    post_restart_replay is False,
)

check(
    "Authorization Consumption Remains Exactly Once",
    authorization_consumption_counter == 1,
)


# =============================================================================
# TEST 18
# =============================================================================

section(
    "R32C TEST 18: DURABLE STATE TAMPER REJECTION"
)

tampered_state = deepcopy(
    restored_after
)

tampered_state.intent_hash = (
    "0" * 64
)

check(
    "Tampered State Integrity Rejected",
    not validate_state_integrity(
        tampered_state
    ),
)


# =============================================================================
# TEST 19
# =============================================================================

section(
    "R32C TEST 19: SYNTHETIC AUTHORIZATION RECEIPT"
)

receipt = build_synthetic_receipt(
    restored_after,
    grant,
)

check(
    "Receipt Transport Is Synthetic",
    receipt["transport"]
    == "SYNTHETIC",
)

check(
    "Receipt Confirms Authorization Consumed",
    receipt["authorization_consumed"]
    is True,
)

check(
    "Receipt Confirms No Network Transmission",
    receipt["network_transmission"]
    is False,
)

check(
    "Receipt Confirms No Leverage Mutation",
    receipt["leverage_mutation"]
    is False,
)

check(
    "Receipt Confirms Exchange Not Contacted",
    receipt["exchange_contacted"]
    is False,
)

check(
    "Receipt Long Target Is 100x",
    receipt["target_long_leverage"]
    == 100,
)

check(
    "Receipt Short Target Is 100x",
    receipt["target_short_leverage"]
    == 100,
)


# =============================================================================
# TEST 20
# =============================================================================

section(
    "R32C TEST 20: TERMINAL SAFETY COUNTERS"
)

check(
    "Synthetic Dispatch Counter Is Zero",
    synthetic_dispatch_counter == 0,
)

check(
    "Real Order Counter Is Zero",
    real_order_counter == 0,
)

check(
    "Network Write Counter Is Zero",
    network_write_counter == 0,
)

check(
    "Leverage Mutation Counter Is Zero",
    leverage_mutation_counter == 0,
)

check(
    "Authorization Request Counter Is One",
    authorization_request_counter == 1,
)

check(
    "Authorization Grant Counter Is One",
    authorization_grant_counter == 1,
)

check(
    "Authorization Consumption Counter Is One",
    authorization_consumption_counter == 1,
)


# =============================================================================
# FINAL VALIDATION
# =============================================================================

section(
    "R32C FINAL VALIDATION"
)

final_state = restore_state()

check(
    "R32C Phase Is Authorization Consumed",
    (
        final_state.phase
        == PHASE_AUTHORIZATION_CONSUMED
    ),
)

check(
    "100x Correction Intent Remains Bound",
    final_state.intent_hash
    == intent_hash,
)

check(
    "Authorization Was Consumed Exactly Once",
    final_state.authorization_consumed
    is True,
)

check(
    "Correction Remains Non-Executable",
    CORRECTION_TRANSMISSION_ENABLED
    is False,
)

check(
    "No Network Write Capability Activated",
    EXCHANGE_NETWORK_WRITES_ENABLED
    is False,
)

check(
    "No Leverage Mutation Capability Activated",
    LEVERAGE_MUTATION_ENABLED
    is False,
)

check(
    "No Real Execution Capability Activated",
    REAL_ORDER_EXECUTION_ENABLED
    is False,
)


separator()

print(
    "R32C: VALIDATION COMPLETE ✅",
    flush=True,
)

print(
    "R32C: SEALED 100X CORRECTION "
    "AUTHORIZATION WAS CONSUMED EXACTLY ONCE",
    flush=True,
)

print(
    "R32C: AUTHORIZATION REPLAY IS REJECTED",
    flush=True,
)

print(
    "R32C: NO REAL ORDER WAS SENT",
    flush=True,
)

print(
    "R32C: NO EXCHANGE NETWORK WRITE "
    "WAS PERFORMED",
    flush=True,
)

print(
    "R32C: NO LEVERAGE MUTATION "
    "WAS PERFORMED",
    flush=True,
)

separator()


# =============================================================================
# HEARTBEAT LOOP
# =============================================================================

heartbeat = 0

while True:

    heartbeat += 1

    try:
        current = restore_state()

        phase = current.phase

        consumed = (
            current.authorization_consumed
        )

    except Exception as exc:

        phase = "STATE_ERROR"
        consumed = False

        print(
            "R32C: STATE RESTORE ERROR "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

    print(
        f"R32C: HEARTBEAT {heartbeat} | "
        f"phase={phase} | "
        f"synthetic-only=True | "
        f"real-execution=False | "
        f"network-writes=False | "
        f"leverage-mutation=False | "
        f"correction-required=True | "
        f"intent-bound=True | "
        f"authorization-consumed="
        f"{consumed} | "
        f"target-long=100x | "
        f"target-short=100x | "
        f"generation={GENERATION} | "
        f"recovery-epoch={RECOVERY_EPOCH}",
        flush=True,
    )

    time.sleep(30)
