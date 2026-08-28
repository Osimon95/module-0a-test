# ==================================================================================================
# R35C - DURABLE GENERATION ADVANCE + EPOCH FENCING + RESTART REPLAY VALIDATION
# ==================================================================================================
#
# SAFETY MODEL
#
#   - SYNTHETIC TRANSPORT ONLY
#   - NO NETWORK WRITES
#   - NO REAL ORDERS
#   - NO DEMO ORDERS
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#
# R35C extends R35B with:
#
#   GENERATION 1
#       ↓
#   PREPARED
#       ↓
#   AUTHORIZED
#       ↓
#   SYNTHETIC DISPATCH
#       ↓
#   COMPLETED
#       ↓
#   DURABLE RESTART
#       ↓
#   GENERATION ADVANCE
#       ↓
#   EPOCH ADVANCE
#       ↓
#   STALE GENERATION / EPOCH REJECTION
#       ↓
#   GENERATION 2 PREPARATION
#       ↓
#   ONE-TIME AUTHORIZATION
#       ↓
#   SECOND SYNTHETIC DISPATCH
#       ↓
#   EXACTLY-ONCE REPLAY PROTECTION
#       ↓
#   DURABLE RESTART
#       ↓
#   JOURNAL HASH-CHAIN VALIDATION
#       ↓
#   FINAL SNAPSHOT INTEGRITY
#
# ==================================================================================================

from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import time
import traceback

from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional


# ==================================================================================================
# CONFIGURATION
# ==================================================================================================

VERSION = "R35C"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
)

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

STATE_DIR = os.getenv(
    "STATE_DIR",
    "/tmp/r35c_state",
)

STATE_FILE = os.path.join(
    STATE_DIR,
    "strategy_state.json",
)

JOURNAL_FILE = os.path.join(
    STATE_DIR,
    "strategy_journal.jsonl",
)


# ==================================================================================================
# HARD SAFETY CONSTANTS
# ==================================================================================================

SYNTHETIC_TRANSPORT_ONLY = True

NETWORK_WRITES_ENABLED = False

REAL_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False

ACCOUNT_MUTATION_ENABLED = False


# ==================================================================================================
# STRATEGY PHASES
# ==================================================================================================

PHASE_PREPARED = "PREPARED"

PHASE_AUTHORIZED = "AUTHORIZED"

PHASE_DISPATCHED = "DISPATCHED"

PHASE_COMPLETED = "COMPLETED"


# ==================================================================================================
# OUTPUT HELPERS
# ==================================================================================================

LINE = "-" * 100


def log(
    message: str,
) -> None:

    print(
        message,
        flush=True,
    )


def section(
    title: str,
) -> None:

    log(LINE)

    log(title)

    log(LINE)


# ==================================================================================================
# TEST TRACKING
# ==================================================================================================

PASSED = 0

FAILED = 0


def check(
    description: str,
    condition: bool,
) -> None:

    global PASSED
    global FAILED

    if condition:

        PASSED += 1

        result = "✅ PASS"

    else:

        FAILED += 1

        result = "❌ FAIL"

    log(
        f"{description:<86}{result}"
    )


# ==================================================================================================
# CANONICAL JSON / HASH HELPERS
# ==================================================================================================

def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_object(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(
            value
        )
    )


# ==================================================================================================
# DURABLE STATE
# ==================================================================================================

@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: Optional[str] = None

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    active_intent: Optional[
        Dict[str, Any]
    ] = None

    active_authorization: Optional[
        Dict[str, Any]
    ] = None

    consumed_intents: List[
        str
    ] = field(
        default_factory=list
    )

    consumed_authorizations: List[
        str
    ] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    synthetic_dispatch_count: int = 0

    network_write_count: int = 0

    terminal: bool = False

    last_journal_hash: str = "0" * 64

    journal_sequence: int = 0

    state_hash: str = ""

    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(
            self
        )


# ==================================================================================================
# STATE INTEGRITY
# ==================================================================================================

def state_payload_without_hash(
    state: StrategyState,
) -> Dict[str, Any]:

    payload = state.as_dict()

    payload.pop(
        "state_hash",
        None,
    )

    return payload


def compute_state_hash(
    state: StrategyState,
) -> str:

    return sha256_object(
        state_payload_without_hash(
            state
        )
    )


def refresh_state_hash(
    state: StrategyState,
) -> None:

    state.state_hash = compute_state_hash(
        state
    )


def verify_state_integrity(
    state: StrategyState,
) -> bool:

    return (
        state.state_hash
        ==
        compute_state_hash(
            state
        )
    )


# ==================================================================================================
# DURABLE STORAGE
# ==================================================================================================

def ensure_state_dir() -> None:

    os.makedirs(
        STATE_DIR,
        exist_ok=True,
    )


def reset_state_dir() -> None:

    if os.path.isdir(
        STATE_DIR
    ):

        shutil.rmtree(
            STATE_DIR
        )

    ensure_state_dir()


def save_state(
    state: StrategyState,
) -> None:

    ensure_state_dir()

    refresh_state_hash(
        state
    )

    temporary_file = (
        STATE_FILE
        +
        ".tmp"
    )

    with open(
        temporary_file,
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            state.as_dict(),
            handle,
            sort_keys=True,
            indent=2,
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temporary_file,
        STATE_FILE,
    )


def load_state() -> StrategyState:

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as handle:

        payload = json.load(
            handle
        )

    state = StrategyState(
        **payload
    )

    if not verify_state_integrity(
        state
    ):

        raise RuntimeError(
            "Durable state integrity check failed"
        )

    return state


# ==================================================================================================
# JOURNAL
# ==================================================================================================

def append_journal(
    state: StrategyState,
    event: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    ensure_state_dir()

    sequence = (
        state.journal_sequence
        +
        1
    )

    previous_hash = state.last_journal_hash

    record_without_hash = {
        "sequence": sequence,
        "version": VERSION,
        "symbol": SYMBOL,
        "generation": state.generation,
        "epoch": state.epoch,
        "event": event,
        "payload": payload,
        "previous_hash": previous_hash,
    }

    record_hash = sha256_object(
        record_without_hash
    )

    record = dict(
        record_without_hash
    )

    record["hash"] = record_hash

    with open(
        JOURNAL_FILE,
        "a",
        encoding="utf-8",
    ) as handle:

        handle.write(
            canonical_json(
                record
            )
            +
            "\n"
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    state.journal_sequence = sequence

    state.last_journal_hash = record_hash

    return record


def read_journal() -> List[
    Dict[str, Any]
]:

    if not os.path.isfile(
        JOURNAL_FILE
    ):

        return []

    records: List[
        Dict[str, Any]
    ] = []

    with open(
        JOURNAL_FILE,
        "r",
        encoding="utf-8",
    ) as handle:

        for line in handle:

            line = line.strip()

            if not line:

                continue

            records.append(
                json.loads(
                    line
                )
            )

    return records


def validate_journal_hash_chain(
    records: List[
        Dict[str, Any]
    ],
) -> bool:

    expected_previous_hash = "0" * 64

    expected_sequence = 1

    for record in records:

        if record.get(
            "sequence"
        ) != expected_sequence:

            return False

        if record.get(
            "previous_hash"
        ) != expected_previous_hash:

            return False

        stored_hash = record.get(
            "hash"
        )

        record_without_hash = dict(
            record
        )

        record_without_hash.pop(
            "hash",
            None,
        )

        calculated_hash = sha256_object(
            record_without_hash
        )

        if stored_hash != calculated_hash:

            return False

        expected_previous_hash = stored_hash

        expected_sequence += 1

    return True


# ==================================================================================================
# INTENT CREATION
# ==================================================================================================

def prepare_intent(
    state: StrategyState,
    purpose: str,
) -> Dict[str, Any]:

    if state.terminal:

        raise RuntimeError(
            "Terminal strategy cannot prepare a new intent"
        )

    state.highest_nonce += 1

    intent_core = {
        "version": VERSION,
        "symbol": SYMBOL,
        "purpose": purpose,
        "generation": state.generation,
        "epoch": state.epoch,
        "nonce": state.highest_nonce,
        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,
    }

    intent_id = sha256_object(
        intent_core
    )

    intent = dict(
        intent_core
    )

    intent["intent_id"] = intent_id

    state.active_intent = intent

    state.active_authorization = None

    state.phase = PHASE_PREPARED

    append_journal(
        state,
        "INTENT_PREPARED",
        {
            "intent_id": intent_id,
            "nonce": state.highest_nonce,
        },
    )

    save_state(
        state
    )

    return intent


# ==================================================================================================
# AUTHORIZATION
# ==================================================================================================

def authorize_intent(
    state: StrategyState,
    intent: Dict[str, Any],
) -> Dict[str, Any]:

    if state.terminal:

        raise RuntimeError(
            "Terminal strategy cannot authorize an intent"
        )

    if state.active_intent is None:

        raise RuntimeError(
            "No active intent"
        )

    if (
        state.active_intent.get(
            "intent_id"
        )
        !=
        intent.get(
            "intent_id"
        )
    ):

        raise RuntimeError(
            "Intent does not match active durable intent"
        )

    intent_id = intent[
        "intent_id"
    ]

    if intent_id in state.consumed_intents:

        raise RuntimeError(
            "Consumed intent replay rejected"
        )

    if (
        intent.get(
            "generation"
        )
        !=
        state.generation
    ):

        raise RuntimeError(
            "Stale generation intent rejected"
        )

    if (
        intent.get(
            "epoch"
        )
        !=
        state.epoch
    ):

        raise RuntimeError(
            "Stale epoch intent rejected"
        )

    authorization_core = {
        "version": VERSION,
        "symbol": SYMBOL,
        "intent_id": intent_id,
        "generation": state.generation,
        "epoch": state.epoch,
        "nonce": intent[
            "nonce"
        ],
        "synthetic_only": True,
        "transmission_allowed": False,
        "network_write_allowed": False,
        "consumed": False,
    }

    authorization_id = sha256_object(
        authorization_core
    )

    authorization = dict(
        authorization_core
    )

    authorization[
        "authorization_id"
    ] = authorization_id

    state.active_authorization = authorization

    state.phase = PHASE_AUTHORIZED

    append_journal(
        state,
        "INTENT_AUTHORIZED",
        {
            "intent_id": intent_id,
            "authorization_id": authorization_id,
        },
    )

    save_state(
        state
    )

    return authorization


# ==================================================================================================
# SYNTHETIC DISPATCH
# ==================================================================================================

def synthetic_dispatch(
    state: StrategyState,
    intent: Dict[str, Any],
    authorization: Dict[str, Any],
) -> Dict[str, Any]:

    if not SYNTHETIC_TRANSPORT_ONLY:

        raise RuntimeError(
            "Synthetic transport firebreak disabled"
        )

    if NETWORK_WRITES_ENABLED:

        raise RuntimeError(
            "Network write firebreak violated"
        )

    if REAL_ORDER_EXECUTION:

        raise RuntimeError(
            "Real order execution must remain disabled"
        )

    if DEMO_ORDER_EXECUTION:

        raise RuntimeError(
            "Demo order execution must remain disabled"
        )

    if state.terminal:

        raise RuntimeError(
            "Terminal strategy cannot dispatch"
        )

    intent_id = intent[
        "intent_id"
    ]

    authorization_id = authorization[
        "authorization_id"
    ]

    if intent_id in state.consumed_intents:

        raise RuntimeError(
            "Consumed intent replay rejected"
        )

    if authorization_id in state.consumed_authorizations:

        raise RuntimeError(
            "Consumed authorization replay rejected"
        )

    if (
        intent.get(
            "generation"
        )
        !=
        state.generation
    ):

        raise RuntimeError(
            "Dispatch rejected due to stale generation"
        )

    if (
        authorization.get(
            "generation"
        )
        !=
        state.generation
    ):

        raise RuntimeError(
            "Authorization generation mismatch"
        )

    if (
        intent.get(
            "epoch"
        )
        !=
        state.epoch
    ):

        raise RuntimeError(
            "Dispatch rejected due to stale epoch"
        )

    if (
        authorization.get(
            "epoch"
        )
        !=
        state.epoch
    ):

        raise RuntimeError(
            "Authorization epoch mismatch"
        )

    if (
        authorization.get(
            "intent_id"
        )
        !=
        intent_id
    ):

        raise RuntimeError(
            "Authorization does not bind exact intent"
        )

    state.phase = PHASE_DISPATCHED

    append_journal(
        state,
        "SYNTHETIC_DISPATCH_PREPARED",
        {
            "intent_id": intent_id,
            "authorization_id": authorization_id,
        },
    )

    receipt_core = {
        "version": VERSION,
        "symbol": SYMBOL,
        "intent_id": intent_id,
        "authorization_id": authorization_id,
        "generation": state.generation,
        "epoch": state.epoch,
        "nonce": intent[
            "nonce"
        ],
        "synthetic_only": True,
        "transmitted": False,
        "network_write": False,
    }

    receipt_id = sha256_object(
        receipt_core
    )

    receipt = dict(
        receipt_core
    )

    receipt[
        "receipt_id"
    ] = receipt_id

    authorization[
        "consumed"
    ] = True

    state.consumed_intents.append(
        intent_id
    )

    state.consumed_authorizations.append(
        authorization_id
    )

    state.synthetic_dispatch_count += 1

    state.durable_receipts.append(
        receipt
    )

    state.active_intent = None

    state.active_authorization = None

    state.phase = PHASE_COMPLETED

    state.terminal = True

    append_journal(
        state,
        "SYNTHETIC_DISPATCH_COMPLETED",
        {
            "intent_id": intent_id,
            "authorization_id": authorization_id,
            "receipt_id": receipt_id,
        },
    )

    save_state(
        state
    )

    return receipt


# ==================================================================================================
# GENERATION ADVANCE
# ==================================================================================================

def advance_generation(
    state: StrategyState,
) -> StrategyState:

    if not state.terminal:

        raise RuntimeError(
            "Generation advance requires terminal prior generation"
        )

    previous_generation = state.generation

    previous_epoch = state.epoch

    state.generation += 1

    state.epoch += 1

    state.phase = None

    state.active_intent = None

    state.active_authorization = None

    state.terminal = False

    append_journal(
        state,
        "GENERATION_ADVANCED",
        {
            "previous_generation": previous_generation,
            "new_generation": state.generation,
            "previous_epoch": previous_epoch,
            "new_epoch": state.epoch,
        },
    )

    save_state(
        state
    )

    return state


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ) -> None:

        if self.path in (
            "/",
            "/health",
            "/healthz",
        ):

            payload = json.dumps(
                {
                    "status": "ok",
                    "version": VERSION,
                    "symbol": SYMBOL,
                    "synthetic_transport_only": SYNTHETIC_TRANSPORT_ONLY,
                    "network_writes_enabled": NETWORK_WRITES_ENABLED,
                }
            ).encode(
                "utf-8"
            )

            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                "application/json",
            )

            self.send_header(
                "Content-Length",
                str(
                    len(
                        payload
                    )
                ),
            )

            self.end_headers()

            self.wfile.write(
                payload
            )

            return

        self.send_response(
            404
        )

        self.end_headers()

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server() -> None:

    def worker() -> None:

        try:

            server = HTTPServer(
                (
                    "0.0.0.0",
                    HEALTH_PORT,
                ),
                HealthHandler,
            )

            log(
                f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}"
            )

            server.serve_forever()

        except Exception as exc:

            log(
                f"{VERSION}: HEALTH SERVER ERROR={type(exc).__name__}: {exc}"
            )

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()


# ==================================================================================================
# MAIN VALIDATION
# ==================================================================================================

def run_validation() -> None:

    reset_state_dir()

    section(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    log(
        f"{VERSION}: SYMBOL={SYMBOL}"
    )

    log(
        f"{VERSION}: VERSION={VERSION}"
    )

    log(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}"
    )

    log(
        f"{VERSION}: STATE DIR={STATE_DIR}"
    )

    log(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY"
    )

    log(
        f"{VERSION}: NETWORK WRITES DISABLED"
    )

    log(
        f"{VERSION}: REAL ORDERS DISABLED"
    )

    log(
        f"{VERSION}: DEMO ORDERS DISABLED"
    )

    log(
        f"{VERSION}: LEVERAGE MUTATION DISABLED"
    )

    log(
        f"{VERSION}: MARGIN MUTATION DISABLED"
    )

    log(
        f"{VERSION}: POSITION MUTATION DISABLED"
    )


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    section(
        f"{VERSION} TEST 1: SAFETY CONSTANTS"
    )

    check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    check(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Real Orders Are Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "Demo Orders Are Disabled",
        DEMO_ORDER_EXECUTION is False,
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


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    section(
        f"{VERSION} TEST 2: INITIAL DURABLE STATE"
    )

    state = StrategyState()

    save_state(
        state
    )

    check(
        "Initial Generation Is One",
        state.generation == 1,
    )

    check(
        "Initial Epoch Is One",
        state.epoch == 1,
    )

    check(
        "Initial Nonce Is Zero",
        state.highest_nonce == 0,
    )

    check(
        "No Active Intent Initially",
        state.active_intent is None,
    )

    check(
        "No Active Authorization Initially",
        state.active_authorization is None,
    )

    check(
        "Strategy Is Initially Nonterminal",
        state.terminal is False,
    )

    check(
        "Initial Durable State Integrity Is Valid",
        verify_state_integrity(
            state
        ),
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    section(
        f"{VERSION} TEST 3: GENERATION ONE INTENT PREPARATION"
    )

    intent_one = prepare_intent(
        state,
        "GENERATION_ONE_SYNTHETIC_VALIDATION",
    )

    check(
        "Generation One Intent Was Created",
        bool(
            intent_one
        ),
    )

    check(
        "Generation One Intent Is Synthetic Only",
        intent_one[
            "synthetic_only"
        ] is True,
    )

    check(
        "Generation One Intent Forbids Transmission",
        intent_one[
            "transmission_allowed"
        ] is False,
    )

    check(
        "Generation One Intent Forbids Network Write",
        intent_one[
            "network_write_allowed"
        ] is False,
    )

    check(
        "Generation One Intent Is Bound To Generation One",
        intent_one[
            "generation"
        ] == 1,
    )

    check(
        "Generation One Intent Is Bound To Epoch One",
        intent_one[
            "epoch"
        ] == 1,
    )

    check(
        "Strategy Phase Is PREPARED",
        state.phase == PHASE_PREPARED,
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    section(
        f"{VERSION} TEST 4: GENERATION ONE AUTHORIZATION"
    )

    authorization_one = authorize_intent(
        state,
        intent_one,
    )

    check(
        "Generation One Authorization Was Created",
        bool(
            authorization_one
        ),
    )

    check(
        "Authorization Binds Exact Generation One Intent",
        authorization_one[
            "intent_id"
        ]
        ==
        intent_one[
            "intent_id"
        ],
    )

    check(
        "Generation One Authorization Is Initially Unconsumed",
        authorization_one[
            "consumed"
        ] is False,
    )

    check(
        "Generation One Authorization Is Synthetic Only",
        authorization_one[
            "synthetic_only"
        ] is True,
    )

    check(
        "Generation One Authorization Forbids Network Write",
        authorization_one[
            "network_write_allowed"
        ] is False,
    )

    check(
        "Strategy Phase Is AUTHORIZED",
        state.phase == PHASE_AUTHORIZED,
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    section(
        f"{VERSION} TEST 5: GENERATION ONE SYNTHETIC DISPATCH"
    )

    receipt_one = synthetic_dispatch(
        state,
        intent_one,
        authorization_one,
    )

    check(
        "Generation One Synthetic Receipt Was Created",
        bool(
            receipt_one
        ),
    )

    check(
        "Generation One Dispatch Was Not Transmitted",
        receipt_one[
            "transmitted"
        ] is False,
    )

    check(
        "Generation One Dispatch Made No Network Write",
        receipt_one[
            "network_write"
        ] is False,
    )

    check(
        "Synthetic Dispatch Count Is One",
        state.synthetic_dispatch_count == 1,
    )

    check(
        "Generation One Strategy Reached COMPLETED",
        state.phase == PHASE_COMPLETED,
    )

    check(
        "Generation One Strategy Is Terminal",
        state.terminal is True,
    )

    check(
        "Strategy Network Write Count Is Zero",
        state.network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    section(
        f"{VERSION} TEST 6: GENERATION ONE REPLAY REJECTION"
    )

    replay_rejected = False

    try:

        synthetic_dispatch(
            state,
            intent_one,
            authorization_one,
        )

    except RuntimeError:

        replay_rejected = True

    check(
        "Consumed Generation One Intent Replay Is Rejected",
        replay_rejected,
    )

    check(
        "Synthetic Dispatch Count Remains One",
        state.synthetic_dispatch_count == 1,
    )

    check(
        "Network Write Count Remains Zero",
        state.network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    section(
        f"{VERSION} TEST 7: GENERATION ONE DURABLE RESTART"
    )

    restarted_one = load_state()

    check(
        "Generation One Terminal State Survives Restart",
        restarted_one.terminal is True,
    )

    check(
        "Generation One COMPLETED Phase Survives Restart",
        restarted_one.phase == PHASE_COMPLETED,
    )

    check(
        "Generation One Consumed Intent Survives Restart",
        intent_one[
            "intent_id"
        ]
        in
        restarted_one.consumed_intents,
    )

    check(
        "Generation One Receipt Survives Restart",
        any(
            receipt.get(
                "receipt_id"
            )
            ==
            receipt_one.get(
                "receipt_id"
            )
            for receipt in restarted_one.durable_receipts
        ),
    )

    check(
        "Generation One Dispatch Count Survives Restart",
        restarted_one.synthetic_dispatch_count == 1,
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    section(
        f"{VERSION} TEST 8: GENERATION ADVANCE"
    )

    advance_generation(
        restarted_one
    )

    check(
        "Generation Advanced From One To Two",
        restarted_one.generation == 2,
    )

    check(
        "Epoch Advanced From One To Two",
        restarted_one.epoch == 2,
    )

    check(
        "Generation Two Starts Nonterminal",
        restarted_one.terminal is False,
    )

    check(
        "Generation Two Starts With No Active Intent",
        restarted_one.active_intent is None,
    )

    check(
        "Generation Two Starts With No Active Authorization",
        restarted_one.active_authorization is None,
    )

    check(
        "Prior Durable Receipt Is Preserved",
        len(
            restarted_one.durable_receipts
        ) == 1,
    )

    check(
        "Prior Consumed Intent Is Preserved",
        len(
            restarted_one.consumed_intents
        ) == 1,
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    section(
        f"{VERSION} TEST 9: STALE GENERATION REJECTION"
    )

    stale_generation_rejected = False

    try:

        authorize_intent(
            restarted_one,
            intent_one,
        )

    except RuntimeError:

        stale_generation_rejected = True

    check(
        "Generation One Intent Is Rejected In Generation Two",
        stale_generation_rejected,
    )

    check(
        "Generation Remains Two",
        restarted_one.generation == 2,
    )

    check(
        "Epoch Remains Two",
        restarted_one.epoch == 2,
    )

    check(
        "Synthetic Dispatch Count Remains One",
        restarted_one.synthetic_dispatch_count == 1,
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    section(
        f"{VERSION} TEST 10: GENERATION TWO INTENT PREPARATION"
    )

    intent_two = prepare_intent(
        restarted_one,
        "GENERATION_TWO_SYNTHETIC_VALIDATION",
    )

    check(
        "Generation Two Intent Was Created",
        bool(
            intent_two
        ),
    )

    check(
        "Generation Two Intent Is Bound To Generation Two",
        intent_two[
            "generation"
        ] == 2,
    )

    check(
        "Generation Two Intent Is Bound To Epoch Two",
        intent_two[
            "epoch"
        ] == 2,
    )

    check(
        "Generation Two Nonce Is Monotonically Higher",
        intent_two[
            "nonce"
        ]
        >
        intent_one[
            "nonce"
        ],
    )

    check(
        "Generation Two Intent Is Synthetic Only",
        intent_two[
            "synthetic_only"
        ] is True,
    )

    check(
        "Generation Two Intent Forbids Transmission",
        intent_two[
            "transmission_allowed"
        ] is False,
    )

    check(
        "Generation Two Intent Forbids Network Write",
        intent_two[
            "network_write_allowed"
        ] is False,
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    section(
        f"{VERSION} TEST 11: STALE EPOCH TAMPER REJECTION"
    )

    stale_epoch_intent = dict(
        intent_two
    )

    stale_epoch_intent[
        "epoch"
    ] = 1

    stale_epoch_rejected = False

    original_active_intent = restarted_one.active_intent

    restarted_one.active_intent = stale_epoch_intent

    try:

        authorize_intent(
            restarted_one,
            stale_epoch_intent,
        )

    except RuntimeError:

        stale_epoch_rejected = True

    restarted_one.active_intent = original_active_intent

    check(
        "Stale Epoch Intent Is Rejected",
        stale_epoch_rejected,
    )

    check(
        "Current Epoch Remains Two",
        restarted_one.epoch == 2,
    )

    check(
        "No Synthetic Dispatch Occurred During Epoch Rejection",
        restarted_one.synthetic_dispatch_count == 1,
    )

    check(
        "No Network Write Occurred During Epoch Rejection",
        restarted_one.network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    section(
        f"{VERSION} TEST 12: GENERATION TWO AUTHORIZATION"
    )

    authorization_two = authorize_intent(
        restarted_one,
        intent_two,
    )

    check(
        "Generation Two Authorization Was Created",
        bool(
            authorization_two
        ),
    )

    check(
        "Generation Two Authorization Binds Exact Intent",
        authorization_two[
            "intent_id"
        ]
        ==
        intent_two[
            "intent_id"
        ],
    )

    check(
        "Generation Two Authorization Is Bound To Generation Two",
        authorization_two[
            "generation"
        ] == 2,
    )

    check(
        "Generation Two Authorization Is Bound To Epoch Two",
        authorization_two[
            "epoch"
        ] == 2,
    )

    check(
        "Generation Two Authorization Is Initially Unconsumed",
        authorization_two[
            "consumed"
        ] is False,
    )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    section(
        f"{VERSION} TEST 13: AUTHORIZATION BINDING TAMPER REJECTION"
    )

    forged_authorization = dict(
        authorization_two
    )

    forged_authorization[
        "intent_id"
    ] = intent_one[
        "intent_id"
    ]

    forged_auth_rejected = False

    try:

        synthetic_dispatch(
            restarted_one,
            intent_two,
            forged_authorization,
        )

    except RuntimeError:

        forged_auth_rejected = True

    check(
        "Forged Authorization Binding Is Rejected",
        forged_auth_rejected,
    )

    check(
        "Synthetic Dispatch Count Still One",
        restarted_one.synthetic_dispatch_count == 1,
    )

    check(
        "Network Write Count Still Zero",
        restarted_one.network_write_count == 0,
    )

    check(
        "Strategy Is Still Nonterminal Before Valid Dispatch",
        restarted_one.terminal is False,
    )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    section(
        f"{VERSION} TEST 14: GENERATION TWO SYNTHETIC DISPATCH"
    )

    receipt_two = synthetic_dispatch(
        restarted_one,
        intent_two,
        authorization_two,
    )

    check(
        "Generation Two Synthetic Receipt Was Created",
        bool(
            receipt_two
        ),
    )

    check(
        "Generation Two Dispatch Was Not Transmitted",
        receipt_two[
            "transmitted"
        ] is False,
    )

    check(
        "Generation Two Dispatch Made No Network Write",
        receipt_two[
            "network_write"
        ] is False,
    )

    check(
        "Synthetic Dispatch Count Is Two",
        restarted_one.synthetic_dispatch_count == 2,
    )

    check(
        "Generation Two Strategy Reached COMPLETED",
        restarted_one.phase == PHASE_COMPLETED,
    )

    check(
        "Generation Two Strategy Is Terminal",
        restarted_one.terminal is True,
    )

    check(
        "Strategy Network Write Count Remains Zero",
        restarted_one.network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    section(
        f"{VERSION} TEST 15: GENERATION TWO REPLAY REJECTION"
    )

    second_replay_rejected = False

    try:

        synthetic_dispatch(
            restarted_one,
            intent_two,
            authorization_two,
        )

    except RuntimeError:

        second_replay_rejected = True

    check(
        "Consumed Generation Two Intent Replay Is Rejected",
        second_replay_rejected,
    )

    check(
        "Synthetic Dispatch Count Remains Two",
        restarted_one.synthetic_dispatch_count == 2,
    )

    check(
        "Network Write Count Remains Zero",
        restarted_one.network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    section(
        f"{VERSION} TEST 16: SECOND DURABLE RESTART"
    )

    final_state = load_state()

    check(
        "Generation Two Survives Restart",
        final_state.generation == 2,
    )

    check(
        "Epoch Two Survives Restart",
        final_state.epoch == 2,
    )

    check(
        "Terminal State Survives Second Restart",
        final_state.terminal is True,
    )

    check(
        "COMPLETED Phase Survives Second Restart",
        final_state.phase == PHASE_COMPLETED,
    )

    check(
        "Both Consumed Intents Survive Restart",
        len(
            final_state.consumed_intents
        ) == 2,
    )

    check(
        "Both Consumed Authorizations Survive Restart",
        len(
            final_state.consumed_authorizations
        ) == 2,
    )

    check(
        "Both Durable Receipts Survive Restart",
        len(
            final_state.durable_receipts
        ) == 2,
    )

    check(
        "Synthetic Dispatch Count Two Survives Restart",
        final_state.synthetic_dispatch_count == 2,
    )


    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    section(
        f"{VERSION} TEST 17: RESTART REPLAY PROTECTION"
    )

    restart_replay_rejected = False

    try:

        synthetic_dispatch(
            final_state,
            intent_two,
            authorization_two,
        )

    except RuntimeError:

        restart_replay_rejected = True

    check(
        "Restart Replay Is Rejected",
        restart_replay_rejected,
    )

    check(
        "Restart Does Not Duplicate Synthetic Dispatch",
        final_state.synthetic_dispatch_count == 2,
    )

    check(
        "Restart Makes No Network Write",
        final_state.network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    section(
        f"{VERSION} TEST 18: TERMINAL IMMUTABILITY"
    )

    terminal_intent_rejected = False

    try:

        prepare_intent(
            final_state,
            "ILLEGAL_TERMINAL_INTENT",
        )

    except RuntimeError:

        terminal_intent_rejected = True

    check(
        "Terminal Strategy Rejects New Intent",
        terminal_intent_rejected,
    )

    check(
        "Terminal State Remains True",
        final_state.terminal is True,
    )

    check(
        "Terminal Phase Remains COMPLETED",
        final_state.phase == PHASE_COMPLETED,
    )

    check(
        "Generation Remains Two",
        final_state.generation == 2,
    )

    check(
        "Epoch Remains Two",
        final_state.epoch == 2,
    )


    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    section(
        f"{VERSION} TEST 19: JOURNAL INTEGRITY"
    )

    records = read_journal()

    check(
        "Durable Journal Contains Records",
        len(
            records
        ) > 0,
    )

    check(
        "Journal Sequence Matches State",
        len(
            records
        )
        ==
        final_state.journal_sequence,
    )

    check(
        "Journal Head Hash Matches State",
        (
            records[-1][
                "hash"
            ]
            if records
            else
            "0" * 64
        )
        ==
        final_state.last_journal_hash,
    )

    check(
        "Every Journal Hash Has Correct Length",
        all(
            len(
                record.get(
                    "hash",
                    "",
                )
            )
            == 64
            for record in records
        ),
    )

    check(
        "Every Previous Journal Hash Has Correct Length",
        all(
            len(
                record.get(
                    "previous_hash",
                    "",
                )
            )
            == 64
            for record in records
        ),
    )


    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    section(
        f"{VERSION} TEST 20: JOURNAL HASH CHAIN"
    )

    journal_valid = validate_journal_hash_chain(
        records
    )

    check(
        "Journal Hash Chain Is Valid",
        journal_valid,
    )

    generation_advance_records = [
        record
        for record in records
        if record.get(
            "event"
        )
        ==
        "GENERATION_ADVANCED"
    ]

    check(
        "Journal Contains Exactly One Generation Advance",
        len(
            generation_advance_records
        ) == 1,
    )

    completed_records = [
        record
        for record in records
        if record.get(
            "event"
        )
        ==
        "SYNTHETIC_DISPATCH_COMPLETED"
    ]

    check(
        "Journal Contains Exactly Two Completed Dispatches",
        len(
            completed_records
        ) == 2,
    )


    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    section(
        f"{VERSION} TEST 21: FINAL SNAPSHOT INTEGRITY"
    )

    check(
        "Final Snapshot Version Is Correct",
        final_state.version == VERSION,
    )

    check(
        "Final Snapshot Symbol Is Correct",
        final_state.symbol == SYMBOL,
    )

    check(
        "Final Snapshot Integrity Is Valid",
        verify_state_integrity(
            final_state
        ),
    )

    check(
        "Final Snapshot Generation Is Two",
        final_state.generation == 2,
    )

    check(
        "Final Snapshot Epoch Is Two",
        final_state.epoch == 2,
    )

    check(
        "Final Snapshot Nonce Is Two",
        final_state.highest_nonce == 2,
    )

    check(
        "Final Snapshot Contains Two Consumed Intents",
        len(
            final_state.consumed_intents
        ) == 2,
    )

    check(
        "Final Snapshot Contains Two Consumed Authorizations",
        len(
            final_state.consumed_authorizations
        ) == 2,
    )

    check(
        "Final Snapshot Contains Two Durable Receipts",
        len(
            final_state.durable_receipts
        ) == 2,
    )

    check(
        "Final Snapshot Dispatch Count Is Two",
        final_state.synthetic_dispatch_count == 2,
    )


    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    section(
        f"{VERSION} TEST 22: GENERATION MONOTONICITY"
    )

    check(
        "Generation Two Is Greater Than Generation One",
        final_state.generation
        >
        intent_one[
            "generation"
        ],
    )

    check(
        "Epoch Two Is Greater Than Epoch One",
        final_state.epoch
        >
        intent_one[
            "epoch"
        ],
    )

    check(
        "Second Intent Nonce Is Greater Than First Intent Nonce",
        intent_two[
            "nonce"
        ]
        >
        intent_one[
            "nonce"
        ],
    )

    check(
        "Generation One Receipt Remains Bound To Generation One",
        receipt_one[
            "generation"
        ] == 1,
    )

    check(
        "Generation Two Receipt Is Bound To Generation Two",
        receipt_two[
            "generation"
        ] == 2,
    )

    check(
        "Generation One Receipt Remains Bound To Epoch One",
        receipt_one[
            "epoch"
        ] == 1,
    )

    check(
        "Generation Two Receipt Is Bound To Epoch Two",
        receipt_two[
            "epoch"
        ] == 2,
    )


    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    section(
        f"{VERSION} TEST 23: FINAL SAFETY FIREBREAK"
    )

    check(
        "Synthetic Transport Remains Enabled",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    check(
        "Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Real Order Execution Remains Disabled",
        REAL_ORDER_EXECUTION is False,
    )

    check(
        "Demo Order Execution Remains Disabled",
        DEMO_ORDER_EXECUTION is False,
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
        "Strategy Remains Terminal",
        final_state.terminal is True,
    )

    check(
        "Strategy Network Write Count Is Zero",
        final_state.network_write_count == 0,
    )

    check(
        "Exactly Two Synthetic Dispatches Exist",
        final_state.synthetic_dispatch_count == 2,
    )

    check(
        "Durable Journal Remains Valid",
        validate_journal_hash_chain(
            read_journal()
        ),
    )


    # ==============================================================================================
    # SUMMARY
    # ==============================================================================================

    section(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    log(
        f"{VERSION}: PASSED={PASSED}"
    )

    log(
        f"{VERSION}: FAILED={FAILED}"
    )

    if FAILED == 0:

        log(
            f"{VERSION}: RESULT=✅ ALL VALIDATIONS PASSED"
        )

    else:

        log(
            f"{VERSION}: RESULT=❌ VALIDATION FAILURE"
        )

    log(
        LINE
    )


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

def main() -> None:

    start_health_server()

    time.sleep(
        0.5
    )

    try:

        run_validation()

    except Exception as exc:

        section(
            f"{VERSION}: FATAL ERROR"
        )

        log(
            f"{VERSION}: ERROR={type(exc).__name__}: {exc}"
        )

        traceback.print_exc()

    heartbeat = 0

    while True:

        heartbeat += 1

        log(
            f"{VERSION}: HEARTBEAT {heartbeat}"
        )

        time.sleep(
            30
        )


if __name__ == "__main__":

    main()
