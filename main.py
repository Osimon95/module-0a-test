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
from typing import Any, Dict, Optional


# =============================================================================
# R32B
# 100X LEVERAGE CORRECTION INTENT CONSTRUCTION + DURABLE BINDING
#
# SAFETY DISCIPLINE
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
# PURPOSE
#   R32A established that a leverage correction is required while remaining
#   SEALED_READ_ONLY. R32B converts that fact into a deterministic, durable,
#   tamper-evident correction intent for 100x isolated leverage.
#
#   R32B DOES NOT SEND THE CORRECTION TO WEEX.
# =============================================================================

VERSION = "R32B"
SYMBOL = "BTCUSDT"
MARGIN_MODE = "ISOLATED"

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

# R32A-observed baseline carried forward.
OBSERVED_LONG_LEVERAGE = 50
OBSERVED_SHORT_LEVERAGE = 20

HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_FILE = Path(
    os.getenv(
        "R32B_STATE_FILE",
        "/tmp/r32b_correction_intent_state.json",
    )
)

HEARTBEAT_SECONDS = 30


# =============================================================================
# HARD-FROZEN SAFETY CONFIGURATION
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

CORRECTION_TRANSMISSION_ENABLED = False


# =============================================================================
# PHASES
# =============================================================================

PHASE_BUILDING = "BUILDING_CORRECTION_INTENT"
PHASE_BOUND = "CORRECTION_INTENT_BOUND"
PHASE_SEALED = "SEALED_CORRECTION_INTENT"


LINE = "-" * 92


# =============================================================================
# LOGGING
# =============================================================================

def log(message: str = "") -> None:
    print(message, flush=True)


def section(title: str) -> None:
    log(LINE)
    log(title)
    log(LINE)


def check(label: str, condition: bool) -> None:
    marker = "✅ PASS" if condition else "❌ FAIL"

    log(
        f"{label:<78} {marker}"
    )

    if not condition:
        raise AssertionError(label)


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


def sha256_json(value: Any) -> str:
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


# =============================================================================
# DURABLE JSON STATE
# =============================================================================

def atomic_write_json(
    path: Path,
    value: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    payload = json.dumps(
        value,
        sort_keys=True,
        indent=2,
    )

    with temp.open(
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(payload)

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp,
        path,
    )


def read_json(
    path: Path,
) -> Optional[Dict[str, Any]]:

    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:

        data = json.load(handle)

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "state file must contain a JSON object"
        )

    return data


# =============================================================================
# CORRECTION INTENT
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

    correction_required: bool

    generation: int

    recovery_epoch: int

    lineage_id: str

    synthetic_only: bool

    real_execution_enabled: bool

    network_writes_enabled: bool

    leverage_mutation_enabled: bool

    def binding_material(
        self,
    ) -> Dict[str, Any]:

        return {

            "version":
                self.version,

            "intent_id":
                self.intent_id,

            "symbol":
                self.symbol,

            "margin_mode":
                self.margin_mode,

            "observed_long_leverage":
                self.observed_long_leverage,

            "observed_short_leverage":
                self.observed_short_leverage,

            "target_long_leverage":
                self.target_long_leverage,

            "target_short_leverage":
                self.target_short_leverage,

            "correction_required":
                self.correction_required,

            "generation":
                self.generation,

            "recovery_epoch":
                self.recovery_epoch,

            "lineage_id":
                self.lineage_id,

            "synthetic_only":
                self.synthetic_only,

            "real_execution_enabled":
                self.real_execution_enabled,

            "network_writes_enabled":
                self.network_writes_enabled,

            "leverage_mutation_enabled":
                self.leverage_mutation_enabled,
        }

    def binding_hash(
        self,
    ) -> str:

        return sha256_json(
            self.binding_material()
        )


# =============================================================================
# RUNTIME STATE
# =============================================================================

@dataclass
class RuntimeState:

    version: str

    phase: str

    generation: int

    recovery_epoch: int

    lineage_id: str

    correction_required: bool

    intent: Dict[str, Any]

    intent_hash: str

    consumed: bool

    synthetic_dispatch_count: int

    real_order_count: int

    network_write_count: int

    leverage_mutation_count: int

    created_at_unix: int

    def integrity_material(
        self,
    ) -> Dict[str, Any]:

        return asdict(self)

    def integrity_hash(
        self,
    ) -> str:

        return sha256_json(
            self.integrity_material()
        )


# =============================================================================
# EXCEPTIONS
# =============================================================================

class RejectedIntent(Exception):
    pass


# =============================================================================
# R32B CORRECTION INTENT ENGINE
# =============================================================================

class CorrectionIntentEngine:

    def __init__(
        self,
        state_file: Path,
    ) -> None:

        self.state_file = state_file

        self._lock = threading.Lock()

        self.state: Optional[
            RuntimeState
        ] = None

        self.state_integrity_hash: Optional[
            str
        ] = None


    # =========================================================================
    # BUILD NEW INTENT
    # =========================================================================

    def build_new(
        self,
    ) -> RuntimeState:

        correction_required = (

            OBSERVED_LONG_LEVERAGE
            !=
            TARGET_LONG_LEVERAGE

            or

            OBSERVED_SHORT_LEVERAGE
            !=
            TARGET_SHORT_LEVERAGE
        )

        if not correction_required:

            raise RejectedIntent(
                "no leverage correction is required"
            )

        lineage_id = uuid.uuid4().hex

        intent = CorrectionIntent(

            version=VERSION,

            intent_id=uuid.uuid4().hex,

            symbol=SYMBOL,

            margin_mode=MARGIN_MODE,

            observed_long_leverage=
                OBSERVED_LONG_LEVERAGE,

            observed_short_leverage=
                OBSERVED_SHORT_LEVERAGE,

            target_long_leverage=
                TARGET_LONG_LEVERAGE,

            target_short_leverage=
                TARGET_SHORT_LEVERAGE,

            correction_required=True,

            generation=1,

            recovery_epoch=1,

            lineage_id=lineage_id,

            synthetic_only=
                SYNTHETIC_TRANSPORT_ONLY,

            real_execution_enabled=
                REAL_ORDER_EXECUTION_ENABLED,

            network_writes_enabled=
                EXCHANGE_NETWORK_WRITES_ENABLED,

            leverage_mutation_enabled=
                LEVERAGE_MUTATION_ENABLED,
        )

        state = RuntimeState(

            version=VERSION,

            phase=PHASE_SEALED,

            generation=1,

            recovery_epoch=1,

            lineage_id=lineage_id,

            correction_required=True,

            intent=intent.binding_material(),

            intent_hash=intent.binding_hash(),

            consumed=False,

            synthetic_dispatch_count=0,

            real_order_count=0,

            network_write_count=0,

            leverage_mutation_count=0,

            created_at_unix=int(
                time.time()
            ),
        )

        self.state = state

        self.state_integrity_hash = (
            state.integrity_hash()
        )

        self.persist()

        return state


    # =========================================================================
    # PERSIST
    # =========================================================================

    def persist(
        self,
    ) -> None:

        if self.state is None:

            raise RuntimeError(
                "cannot persist empty state"
            )

        envelope = {

            "state":
                asdict(self.state),

            "state_integrity_hash":
                self.state.integrity_hash(),
        }

        atomic_write_json(
            self.state_file,
            envelope,
        )

        self.state_integrity_hash = (
            envelope[
                "state_integrity_hash"
            ]
        )


    # =========================================================================
    # RESTORE
    # =========================================================================

    def restore(
        self,
    ) -> RuntimeState:

        envelope = read_json(
            self.state_file
        )

        if envelope is None:
            return self.build_new()

        raw_state = envelope.get(
            "state"
        )

        expected_hash = envelope.get(
            "state_integrity_hash"
        )

        if not isinstance(
            raw_state,
            dict,
        ):

            raise RejectedIntent(
                "invalid persisted state envelope"
            )

        if not isinstance(
            expected_hash,
            str,
        ):

            raise RejectedIntent(
                "invalid persisted state integrity hash"
            )

        state = RuntimeState(
            **raw_state
        )

        actual_hash = (
            state.integrity_hash()
        )

        if actual_hash != expected_hash:

            raise RejectedIntent(
                "persisted state integrity mismatch"
            )

        self.validate_state(
            state
        )

        self.state = state

        self.state_integrity_hash = (
            expected_hash
        )

        return state


    # =========================================================================
    # STATE VALIDATION
    # =========================================================================

    @staticmethod
    def validate_state(
        state: RuntimeState,
    ) -> None:

        if state.version != VERSION:

            raise RejectedIntent(
                "wrong version"
            )

        if state.phase != PHASE_SEALED:

            raise RejectedIntent(
                "state is not sealed"
            )

        intent = state.intent

        required = {

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "margin_mode":
                MARGIN_MODE,

            "target_long_leverage":
                TARGET_LONG_LEVERAGE,

            "target_short_leverage":
                TARGET_SHORT_LEVERAGE,

            "correction_required":
                True,

            "generation":
                state.generation,

            "recovery_epoch":
                state.recovery_epoch,

            "lineage_id":
                state.lineage_id,

            "synthetic_only":
                True,

            "real_execution_enabled":
                False,

            "network_writes_enabled":
                False,

            "leverage_mutation_enabled":
                False,
        }

        for key, expected in required.items():

            if intent.get(key) != expected:

                raise RejectedIntent(
                    f"intent binding mismatch: {key}"
                )

        if (
            sha256_json(intent)
            !=
            state.intent_hash
        ):

            raise RejectedIntent(
                "intent hash mismatch"
            )

        if state.consumed:

            raise RejectedIntent(
                "R32B intent must remain unconsumed"
            )

        if (
            state.synthetic_dispatch_count
            !=
            0
        ):

            raise RejectedIntent(
                "R32B cannot dispatch"
            )

        if state.real_order_count != 0:

            raise RejectedIntent(
                "real order counter must remain zero"
            )

        if state.network_write_count != 0:

            raise RejectedIntent(
                "network write counter must remain zero"
            )

        if (
            state.leverage_mutation_count
            !=
            0
        ):

            raise RejectedIntent(
                "leverage mutation counter must remain zero"
            )


    # =========================================================================
    # CANDIDATE VALIDATION
    # =========================================================================

    def validate_candidate(
        self,
        candidate: Dict[str, Any],
    ) -> bool:

        if self.state is None:

            raise RuntimeError(
                "engine state is not initialized"
            )

        try:

            if (
                sha256_json(candidate)
                !=
                self.state.intent_hash
            ):

                raise RejectedIntent(
                    "candidate hash mismatch"
                )

            for key in (

                "symbol",

                "margin_mode",

                "target_long_leverage",

                "target_short_leverage",

                "generation",

                "recovery_epoch",

                "lineage_id",

                "intent_id",
            ):

                if (
                    candidate.get(key)
                    !=
                    self.state.intent.get(key)
                ):

                    raise RejectedIntent(
                        f"candidate binding mismatch: {key}"
                    )

            if (
                candidate.get(
                    "synthetic_only"
                )
                is not True
            ):

                raise RejectedIntent(
                    "candidate is not synthetic-only"
                )

            if (
                candidate.get(
                    "network_writes_enabled"
                )
                is not False
            ):

                raise RejectedIntent(
                    "candidate attempts network writes"
                )

            if (
                candidate.get(
                    "leverage_mutation_enabled"
                )
                is not False
            ):

                raise RejectedIntent(
                    "candidate attempts leverage mutation"
                )

            return True

        except RejectedIntent:

            return False


    # =========================================================================
    # SYNTHETIC PREVIEW
    # =========================================================================

    def synthetic_preview(
        self,
    ) -> Dict[str, Any]:

        if self.state is None:

            raise RuntimeError(
                "engine state is not initialized"
            )

        return {

            "transport":
                "SYNTHETIC_ONLY",

            "transmitted":
                False,

            "mutation_performed":
                False,

            "symbol":
                self.state.intent[
                    "symbol"
                ],

            "margin_mode":
                self.state.intent[
                    "margin_mode"
                ],

            "target_long_leverage":
                self.state.intent[
                    "target_long_leverage"
                ],

            "target_short_leverage":
                self.state.intent[
                    "target_short_leverage"
                ],

            "intent_hash":
                self.state.intent_hash,
        }


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(
    socketserver.BaseRequestHandler
):

    def handle(
        self,
    ) -> None:

        try:

            self.request.recv(
                1024
            )

            body = b"R32B OK\n"

            response = (

                b"HTTP/1.1 200 OK\r\n"

                b"Content-Type: text/plain\r\n"

                +
                f"Content-Length: {len(body)}\r\n".encode(
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


class ReusableTCPServer(
    socketserver.TCPServer
):

    allow_reuse_address = True


def start_health_server() -> None:

    def run() -> None:

        try:

            with ReusableTCPServer(
                (
                    "0.0.0.0",
                    HEALTH_PORT,
                ),
                HealthHandler,
            ) as server:

                log(
                    f"{VERSION}: "
                    f"HEALTH SERVER LISTENING "
                    f"ON PORT {HEALTH_PORT}"
                )

                server.serve_forever()

        except OSError as exc:

            log(
                f"{VERSION}: "
                f"HEALTH SERVER WARNING: "
                f"{exc}"
            )

    thread = threading.Thread(
        target=run,
        name="r32b-health",
        daemon=True,
    )

    thread.start()


# =============================================================================
# VALIDATION
# =============================================================================

def run_validation(
    engine: CorrectionIntentEngine,
) -> None:

    state = engine.state

    if state is None:

        raise RuntimeError(
            "state unavailable"
        )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 1: HARD SAFETY CONFIGURATION"
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

    check(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    check(
        "Correction Transmission Disabled",
        CORRECTION_TRANSMISSION_ENABLED
        is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 2: CORRECTION REQUIREMENT"
    )
    # -------------------------------------------------------------------------

    check(
        "Observed Long Leverage Is 50x",
        OBSERVED_LONG_LEVERAGE
        ==
        50,
    )

    check(
        "Observed Short Leverage Is 20x",
        OBSERVED_SHORT_LEVERAGE
        ==
        20,
    )

    check(
        "Target Long Leverage Is 100x",
        TARGET_LONG_LEVERAGE
        ==
        100,
    )

    check(
        "Target Short Leverage Is 100x",
        TARGET_SHORT_LEVERAGE
        ==
        100,
    )

    check(
        "Correction Requirement Is True",
        state.correction_required
        is True,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 3: 100X CORRECTION INTENT CONSTRUCTION"
    )
    # -------------------------------------------------------------------------

    intent = state.intent

    check(
        "Intent Version Matches R32B",
        intent["version"]
        ==
        VERSION,
    )

    check(
        "Intent Symbol Matches",
        intent["symbol"]
        ==
        SYMBOL,
    )

    check(
        "Intent Margin Mode Is Isolated",
        intent["margin_mode"]
        ==
        MARGIN_MODE,
    )

    check(
        "Intent Long Target Is 100x",
        intent[
            "target_long_leverage"
        ]
        ==
        100,
    )

    check(
        "Intent Short Target Is 100x",
        intent[
            "target_short_leverage"
        ]
        ==
        100,
    )

    check(
        "Intent Is Synthetic Only",
        intent[
            "synthetic_only"
        ]
        is True,
    )

    check(
        "Intent Has Network Writes Disabled",
        intent[
            "network_writes_enabled"
        ]
        is False,
    )

    check(
        "Intent Has Leverage Mutation Disabled",
        intent[
            "leverage_mutation_enabled"
        ]
        is False,
    )

    log(
        f"R32B: CORRECTION INTENT ID="
        f"{intent['intent_id']}"
    )

    log(
        f"R32B: CORRECTION INTENT HASH="
        f"{state.intent_hash}"
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 4: GENERATION / RECOVERY / LINEAGE BINDING"
    )
    # -------------------------------------------------------------------------

    check(
        "Generation Is One",
        state.generation
        ==
        1,
    )

    check(
        "Recovery Epoch Is One",
        state.recovery_epoch
        ==
        1,
    )

    check(
        "Intent Generation Matches State",
        intent["generation"]
        ==
        state.generation,
    )

    check(
        "Intent Recovery Epoch Matches State",
        intent["recovery_epoch"]
        ==
        state.recovery_epoch,
    )

    check(
        "Intent Lineage Matches State",
        intent["lineage_id"]
        ==
        state.lineage_id,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 5: EXACT HASH BINDING"
    )
    # -------------------------------------------------------------------------

    check(
        "Canonical Intent Hash Validates",
        sha256_json(intent)
        ==
        state.intent_hash,
    )

    check(
        "Exact Candidate Accepted",
        engine.validate_candidate(
            dict(intent)
        )
        is True,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 6: TARGET LEVERAGE TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    tampered = dict(intent)

    tampered[
        "target_long_leverage"
    ] = 99

    check(
        "Tampered 99x Long Target Rejected",
        engine.validate_candidate(
            tampered
        )
        is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 7: SYMBOL / MARGIN BINDING TAMPER REJECTION"
    )
    # -------------------------------------------------------------------------

    wrong_symbol = dict(intent)

    wrong_symbol[
        "symbol"
    ] = "ETHUSDT"

    check(
        "Wrong Symbol Rejected",
        engine.validate_candidate(
            wrong_symbol
        )
        is False,
    )

    wrong_margin = dict(intent)

    wrong_margin[
        "margin_mode"
    ] = "CROSS"

    check(
        "Wrong Margin Mode Rejected",
        engine.validate_candidate(
            wrong_margin
        )
        is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 8: STALE GENERATION / EPOCH REJECTION"
    )
    # -------------------------------------------------------------------------

    stale_generation = dict(
        intent
    )

    stale_generation[
        "generation"
    ] = 0

    check(
        "Stale Generation Rejected",
        engine.validate_candidate(
            stale_generation
        )
        is False,
    )

    stale_epoch = dict(
        intent
    )

    stale_epoch[
        "recovery_epoch"
    ] = 0

    check(
        "Stale Recovery Epoch Rejected",
        engine.validate_candidate(
            stale_epoch
        )
        is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 9: SAFETY FLAG ESCALATION REJECTION"
    )
    # -------------------------------------------------------------------------

    network_escalation = dict(
        intent
    )

    network_escalation[
        "network_writes_enabled"
    ] = True

    check(
        "Network Write Escalation Rejected",
        engine.validate_candidate(
            network_escalation
        )
        is False,
    )

    mutation_escalation = dict(
        intent
    )

    mutation_escalation[
        "leverage_mutation_enabled"
    ] = True

    check(
        "Leverage Mutation Escalation Rejected",
        engine.validate_candidate(
            mutation_escalation
        )
        is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 10: SYNTHETIC CORRECTION PREVIEW"
    )
    # -------------------------------------------------------------------------

    preview = (
        engine.synthetic_preview()
    )

    check(
        "Preview Transport Is Synthetic",
        preview["transport"]
        ==
        "SYNTHETIC_ONLY",
    )

    check(
        "Preview Confirms No Transmission",
        preview["transmitted"]
        is False,
    )

    check(
        "Preview Confirms No Mutation",
        preview[
            "mutation_performed"
        ]
        is False,
    )

    check(
        "Preview Long Target Is 100x",
        preview[
            "target_long_leverage"
        ]
        ==
        100,
    )

    check(
        "Preview Short Target Is 100x",
        preview[
            "target_short_leverage"
        ]
        ==
        100,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 11: DURABLE STATE INTEGRITY"
    )
    # -------------------------------------------------------------------------

    persisted = read_json(
        STATE_FILE
    )

    check(
        "Persisted State Exists",
        persisted
        is not None,
    )

    assert persisted is not None

    raw = persisted[
        "state"
    ]

    restored_for_hash = (
        RuntimeState(
            **raw
        )
    )

    check(
        "Persisted State Integrity Hash Validates",
        restored_for_hash.integrity_hash()
        ==
        persisted[
            "state_integrity_hash"
        ],
    )

    check(
        "Persisted Phase Is Sealed",
        raw["phase"]
        ==
        PHASE_SEALED,
    )

    check(
        "Persisted Intent Hash Matches",
        raw["intent_hash"]
        ==
        state.intent_hash,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 12: RESTART RESTORE"
    )
    # -------------------------------------------------------------------------

    restarted = (
        CorrectionIntentEngine(
            STATE_FILE
        )
    )

    restored = (
        restarted.restore()
    )

    check(
        "Restart Restores Sealed Phase",
        restored.phase
        ==
        PHASE_SEALED,
    )

    check(
        "Restart Preserves Intent Hash",
        restored.intent_hash
        ==
        state.intent_hash,
    )

    check(
        "Restart Preserves Intent ID",
        restored.intent[
            "intent_id"
        ]
        ==
        intent[
            "intent_id"
        ],
    )

    check(
        "Restart Preserves Generation",
        restored.generation
        ==
        state.generation,
    )

    check(
        "Restart Preserves Recovery Epoch",
        restored.recovery_epoch
        ==
        state.recovery_epoch,
    )

    check(
        "Restart Preserves Lineage",
        restored.lineage_id
        ==
        state.lineage_id,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B TEST 13: TERMINAL SAFETY COUNTERS"
    )
    # -------------------------------------------------------------------------

    check(
        "Synthetic Dispatch Counter Is Zero",
        state.synthetic_dispatch_count
        ==
        0,
    )

    check(
        "Real Order Counter Is Zero",
        state.real_order_count
        ==
        0,
    )

    check(
        "Network Write Counter Is Zero",
        state.network_write_count
        ==
        0,
    )

    check(
        "Leverage Mutation Counter Is Zero",
        state.leverage_mutation_count
        ==
        0,
    )

    check(
        "Intent Remains Unconsumed",
        state.consumed
        is False,
    )


    # -------------------------------------------------------------------------
    section(
        "R32B FINAL VALIDATION"
    )
    # -------------------------------------------------------------------------

    check(
        "R32B Phase Is Sealed Correction Intent",
        state.phase
        ==
        PHASE_SEALED,
    )

    check(
        "100x Correction Intent Is Bound",
        (
            state.intent[
                "target_long_leverage"
            ]
            ==
            100

            and

            state.intent[
                "target_short_leverage"
            ]
            ==
            100
        ),
    )

    check(
        "Correction Is Still Non-Executable",
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

    log(LINE)

    log(
        "R32B: VALIDATION COMPLETE ✅"
    )

    log(
        "R32B: 100X CORRECTION INTENT "
        "IS SEALED, DURABLE, AND NON-EXECUTABLE"
    )

    log(
        "R32B: NO REAL ORDER WAS SENT"
    )

    log(
        "R32B: NO EXCHANGE NETWORK WRITE WAS PERFORMED"
    )

    log(
        "R32B: NO LEVERAGE MUTATION WAS PERFORMED"
    )

    log(LINE)


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    section(
        "R32B: MAIN.PY ENTERED"
    )

    log(
        f"R32B: SYMBOL={SYMBOL}"
    )

    log(
        f"R32B: VERSION={VERSION}"
    )

    log(
        f"R32B: STATE FILE={STATE_FILE}"
    )

    log(
        f"R32B: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        "R32B: OBSERVED LEVERAGE "
        f"long={OBSERVED_LONG_LEVERAGE}x "
        f"short={OBSERVED_SHORT_LEVERAGE}x"
    )

    log(
        "R32B: TARGET LEVERAGE "
        f"long={TARGET_LONG_LEVERAGE}x "
        f"short={TARGET_SHORT_LEVERAGE}x"
    )

    log(
        "R32B: REAL EXECUTION DISABLED"
    )

    log(
        "R32B: NETWORK WRITES DISABLED"
    )

    log(
        "R32B: LEVERAGE MUTATION DISABLED"
    )

    log(
        "R32B: SYNTHETIC TRANSPORT ONLY"
    )


    # =========================================================================
    # START HEALTH SERVER
    # =========================================================================

    start_health_server()


    # =========================================================================
    # RESTORE OR CREATE SEALED INTENT
    # =========================================================================

    engine = CorrectionIntentEngine(
        STATE_FILE
    )

    try:

        state = engine.restore()

    except Exception as exc:

        log(
            "R32B: EXISTING STATE REJECTED: "
            f"{exc}"
        )

        # Fail closed.
        # Never silently replace a corrupted
        # or tampered correction intent.
        raise


    # =========================================================================
    # VALIDATION
    # =========================================================================

    run_validation(
        engine
    )


    # =========================================================================
    # PERSISTENT SEALED RUNTIME
    # =========================================================================

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"R32B: HEARTBEAT {heartbeat} | "
            f"phase={state.phase} | "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY} | "
            f"real-execution={REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes={EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"correction-required={state.correction_required} | "
            f"intent-bound={bool(state.intent_hash)} | "
            f"target-long={state.intent['target_long_leverage']}x | "
            f"target-short={state.intent['target_short_leverage']}x | "
            f"generation={state.generation} | "
            f"recovery-epoch={state.recovery_epoch}"
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
