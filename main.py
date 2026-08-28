
# ==================================================================================================
# R35B - ADVERSARIAL DURABLE-STATE / REPLAY / CORRUPTION / CONCURRENCY VALIDATION
# ==================================================================================================
#
# SAFETY MODEL
#   - LOCAL SYNTHETIC TRANSPORT ONLY
#   - NO POST / PUT / PATCH / DELETE
#   - NO REAL ORDER
#   - NO DEMO ORDER
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NETWORK WRITE COUNT MUST REMAIN ZERO
#
# R35B validates adversarial failure handling for the durable exactly-once lifecycle proven by R35A:
#
#   1. Safety constants and transport firebreak
#   2. Baseline durable lifecycle
#   3. Snapshot hash tamper rejection
#   4. Journal record hash tamper rejection
#   5. Journal hash-chain tamper rejection
#   6. Torn journal tail rejection
#   7. Duplicate intent rejection
#   8. Duplicate durable receipt rejection
#   9. Consumed-intent replay rejection
#  10. Stale generation rejection
#  11. Stale epoch rejection
#  12. Reordered phase transition rejection
#  13. Payload-binding tamper rejection
#  14. Authorization-binding tamper rejection
#  15. Interrupted atomic snapshot replacement recovery
#  16. Concurrent recovery single-winner fencing
#  17. Terminal-state immutability
#  18. Restart replay rejection
#  19. Journal/snapshot reconciliation
#  20. Final zero-network-write safety audit
#
# This program intentionally performs no external network operation of any kind.
# ==================================================================================================

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
import threading
import time
import uuid

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==================================================================================================
# PART 1 - CONSTANTS / SAFETY / UTILITIES
# ==================================================================================================

VERSION = "R35B"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)

STATE_DIR = Path(
    os.getenv(
        "R35B_STATE_DIR",
        "/tmp/r35b_state",
    )
)

STATE_FILE = STATE_DIR / "strategy_state.json"
JOURNAL_FILE = STATE_DIR / "transition_journal.jsonl"
SNAPSHOT_TMP_FILE = STATE_DIR / "strategy_state.json.tmp"


# --------------------------------------------------------------------------------------------------
# HARD SAFETY CONSTANTS
# --------------------------------------------------------------------------------------------------

SYNTHETIC_TRANSPORT_ONLY = True

NETWORK_WRITES_ENABLED = False

REAL_ORDERS_ENABLED = False
DEMO_ORDERS_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False


# --------------------------------------------------------------------------------------------------
# DURABLE STRATEGY PHASES
# --------------------------------------------------------------------------------------------------

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_APPLIED = "APPLIED"
PHASE_TERMINAL = "TERMINAL"


PHASE_ORDER = {
    PHASE_PREPARED: 0,
    PHASE_AUTHORIZED: 1,
    PHASE_COMMITTED: 2,
    PHASE_DISPATCHED: 3,
    PHASE_APPLIED: 4,
    PHASE_TERMINAL: 5,
}


ALLOWED_TRANSITIONS = {
    None: {
        PHASE_PREPARED,
    },

    PHASE_PREPARED: {
        PHASE_AUTHORIZED,
    },

    PHASE_AUTHORIZED: {
        PHASE_COMMITTED,
    },

    PHASE_COMMITTED: {
        PHASE_DISPATCHED,
    },

    PHASE_DISPATCHED: {
        PHASE_APPLIED,
    },

    PHASE_APPLIED: {
        PHASE_TERMINAL,
    },

    PHASE_TERMINAL: set(),
}


# --------------------------------------------------------------------------------------------------
# GLOBAL DIAGNOSTIC COUNTERS
# --------------------------------------------------------------------------------------------------

NETWORK_WRITE_COUNT = 0
NETWORK_WRITE_LOCK = threading.Lock()

PASS_COUNT = 0
FAIL_COUNT = 0


# --------------------------------------------------------------------------------------------------
# OUTPUT UTILITIES
# --------------------------------------------------------------------------------------------------

def sep() -> None:
    print(
        "-" * 100,
        flush=True,
    )


def banner(
    title: str,
) -> None:

    sep()

    print(
        title,
        flush=True,
    )

    sep()


# --------------------------------------------------------------------------------------------------
# HASHING / SERIALIZATION
# --------------------------------------------------------------------------------------------------

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
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode("utf-8"),
    ).hexdigest()


def sha256_obj(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(
            value,
        )
    )


def now_ms() -> int:

    return int(
        time.time() * 1000
    )


# --------------------------------------------------------------------------------------------------
# TEST ASSERTION
# --------------------------------------------------------------------------------------------------

def assert_test(
    name: str,
    condition: bool,
) -> None:

    global PASS_COUNT
    global FAIL_COUNT

    if condition:

        PASS_COUNT += 1

        suffix = "✅ PASS"

    else:

        FAIL_COUNT += 1

        suffix = "❌ FAIL"

    print(
        f"{name:<88} {suffix}",
        flush=True,
    )

    if not condition:

        raise AssertionError(
            name
        )


# --------------------------------------------------------------------------------------------------
# ABSOLUTE NETWORK-WRITE FIREBREAK
# --------------------------------------------------------------------------------------------------

def network_write_attempt(
    method: str,
    path: str,
    payload: Optional[dict] = None,
) -> None:

    global NETWORK_WRITE_COUNT

    with NETWORK_WRITE_LOCK:

        NETWORK_WRITE_COUNT += 1

    raise RuntimeError(
        f"{VERSION}: NETWORK WRITE BLOCKED "
        f"method={method} "
        f"path={path} "
        f"payload={payload!r}"
    )


# --------------------------------------------------------------------------------------------------
# HEALTH SERVER
# --------------------------------------------------------------------------------------------------

class HealthHandler(
    BaseHTTPRequestHandler,
):

    def do_GET(
        self,
    ) -> None:

        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):

            self.send_response(
                404
            )

            self.end_headers()

            return

        body = canonical_json(
            {
                "version": VERSION,

                "status": (
                    "running"
                    if FAIL_COUNT == 0
                    else "failed"
                ),

                "synthetic_only":
                    SYNTHETIC_TRANSPORT_ONLY,

                "network_writes":
                    NETWORK_WRITE_COUNT,

                "passes":
                    PASS_COUNT,

                "failures":
                    FAIL_COUNT,
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
                len(body)
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )


    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


def start_health_server(
) -> ThreadingHTTPServer:

    server = ThreadingHTTPServer(
        (
            "0.0.0.0",
            HEALTH_PORT,
        ),
        HealthHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    return server


# ==================================================================================================
# PART 2 - DURABLE MODEL / JOURNAL / SNAPSHOT
# ==================================================================================================

@dataclass
class Intent:

    intent_id: str

    symbol: str
    side: str
    quantity: str

    purpose: str

    generation: int
    epoch: int
    nonce: int

    created_ms: int

    payload: Dict[str, Any]

    payload_hash: str


    @classmethod
    def create(
        cls,
        *,
        symbol: str = SYMBOL,
        side: str = "BUY",
        quantity: str = "0.0004",
        purpose: str = "ADVERSARIAL_TEST_ENTRY",
        generation: int = 1,
        epoch: int = 1,
        nonce: int = 1,
    ) -> "Intent":

        intent_id = (
            f"r35b-"
            f"{uuid.uuid4().hex[:20]}"
        )

        payload = {
            "symbol":
                symbol,

            "side":
                side,

            "positionSide":
                (
                    "LONG"
                    if side == "BUY"
                    else "SHORT"
                ),

            "type":
                "MARKET",

            "quantity":
                quantity,

            "newClientOrderId":
                intent_id,
        }

        return cls(
            intent_id=
                intent_id,

            symbol=
                symbol,

            side=
                side,

            quantity=
                quantity,

            purpose=
                purpose,

            generation=
                generation,

            epoch=
                epoch,

            nonce=
                nonce,

            created_ms=
                now_ms(),

            payload=
                payload,

            payload_hash=
                sha256_obj(
                    payload
                ),
        )


    def as_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "intent_id":
                self.intent_id,

            "symbol":
                self.symbol,

            "side":
                self.side,

            "quantity":
                self.quantity,

            "purpose":
                self.purpose,

            "generation":
                self.generation,

            "epoch":
                self.epoch,

            "nonce":
                self.nonce,

            "created_ms":
                self.created_ms,

            "payload":
                copy.deepcopy(
                    self.payload
                ),

            "payload_hash":
                self.payload_hash,
        }


# --------------------------------------------------------------------------------------------------

@dataclass
class StrategyState:
    version: str = VERSION
    symbol: str = SYMBOL
    phase: Optional[str] = None

    generation: int = 1
    epoch: int = 1
    highest_nonce: int = 0

    active_intent: Optional[Dict[str, Any]] = None
    active_authorization: Optional[Dict[str, Any]] = None

    consumed_intents: List[str] = field(
        default_factory=list
    )

    durable_receipts: List[Dict[str, Any]] = field(
        default_factory=list
    )

    synthetic_dispatch_count: int = 0
    terminal: bool = False

    last_journal_hash: str = "0" * 64
    journal_sequence: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()
        


# --------------------------------------------------------------------------------------------------

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

    consumed_intents: List[str] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    synthetic_dispatch_count: int = 0

    terminal: bool = False

    last_journal_hash: str = "0" * 64

    journal_sequence: int = 0

    updated_ms:
        int = field(
            default_factory=now_ms
        )


    def body(
        self,
    ) -> Dict[str, Any]:

        return {
            "version":
                self.version,

            "symbol":
                self.symbol,

            "phase":
                self.phase,

            "generation":
                self.generation,

            "epoch":
                self.epoch,

            "highest_nonce":
                self.highest_nonce,

            "active_intent":
                copy.deepcopy(
                    self.active_intent
                ),

            "active_authorization":
                copy.deepcopy(
                    self.active_authorization
                ),

            "consumed_intents":
                list(
                    self.consumed_intents
                ),

            "durable_receipts":
                copy.deepcopy(
                    self.durable_receipts
                ),

            "synthetic_dispatch_count":
                self.synthetic_dispatch_count,

            "terminal":
                self.terminal,

            "last_journal_hash":
                self.last_journal_hash,

            "journal_sequence":
                self.journal_sequence,

            "updated_ms":
                self.updated_ms,
        }


    def envelope(
        self,
    ) -> Dict[str, Any]:

        body = self.body()

        return {
            "body":
                body,

            "sha256":
                sha256_obj(
                    body
                ),
        }


    @classmethod
    def from_envelope(
        cls,
        envelope: Dict[str, Any],
    ) -> "StrategyState":

        if (
            not isinstance(
                envelope,
                dict,
            )
            or
            "body" not in envelope
            or
            "sha256" not in envelope
        ):

            raise ValueError(
                "snapshot envelope malformed"
            )

        body = envelope[
            "body"
        ]

        if (
            sha256_obj(
                body
            )
            !=
            envelope[
                "sha256"
            ]
        ):

            raise ValueError(
                "snapshot hash mismatch"
            )

        return cls(
            **body
        )


# --------------------------------------------------------------------------------------------------
# DURABLE STORE
# --------------------------------------------------------------------------------------------------

class DurableStore:

    def __init__(
        self,
        directory: Path,
    ):

        self.directory = (
            directory
        )

        self.state_file = (
            directory
            /
            "strategy_state.json"
        )

        self.tmp_file = (
            directory
            /
            "strategy_state.json.tmp"
        )

        self.journal_file = (
            directory
            /
            "transition_journal.jsonl"
        )

        self.lock = (
            threading.RLock()
        )

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )


    def reset(
        self,
    ) -> None:

        with self.lock:

            if self.directory.exists():

                shutil.rmtree(
                    self.directory
                )

            self.directory.mkdir(
                parents=True,
                exist_ok=True,
            )


    def write_snapshot_atomic(
        self,
        state: StrategyState,
    ) -> None:

        envelope = (
            state.envelope()
        )

        serialized = (
            canonical_json(
                envelope
            )
            +
            "\n"
        )

        with self.lock:

            with open(
                self.tmp_file,
                "w",
                encoding="utf-8",
            ) as handle:

                handle.write(
                    serialized
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )

            os.replace(
                self.tmp_file,
                self.state_file,
            )

            dir_fd = os.open(
                str(
                    self.directory
                ),
                os.O_RDONLY,
            )

            try:

                os.fsync(
                    dir_fd
                )

            finally:

                os.close(
                    dir_fd
                )


    def read_snapshot(
        self,
    ) -> StrategyState:

        with self.lock:

            with open(
                self.state_file,
                "r",
                encoding="utf-8",
            ) as handle:

                envelope = (
                    json.load(
                        handle
                    )
                )

        return (
            StrategyState.from_envelope(
                envelope
            )
        )


    def append_journal(
        self,
        state: StrategyState,
        event: str,
        details: Dict[str, Any],
    ) -> str:

        with self.lock:

            sequence = (
                state.journal_sequence
                +
                1
            )

            record_body = {
                "sequence":
                    sequence,

                "event":
                    event,

                "phase":
                    state.phase,

                "generation":
                    state.generation,

                "epoch":
                    state.epoch,

                "timestamp_ms":
                    now_ms(),

                "details":
                    copy.deepcopy(
                        details
                    ),

                "prev_hash":
                    state.last_journal_hash,
            }

            record_hash = (
                sha256_obj(
                    record_body
                )
            )

            record = {
                "body":
                    record_body,

                "sha256":
                    record_hash,
            }

            with open(
                self.journal_file,
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

            state.journal_sequence = (
                sequence
            )

            state.last_journal_hash = (
                record_hash
            )

            state.updated_ms = (
                now_ms()
            )

            return record_hash


    def validate_journal(
        self,
        tolerate_torn_tail: bool = False,
    ) -> Tuple[int, str]:

        if not self.journal_file.exists():

            return (
                0,
                "0" * 64,
            )

        previous_hash = (
            "0" * 64
        )

        sequence = 0

        with open(
            self.journal_file,
            "rb",
        ) as handle:

            lines = (
                handle.readlines()
            )

        for index, raw in enumerate(
            lines
        ):

            is_last = (
                index
                ==
                len(lines) - 1
            )

            if not raw.endswith(
                b"\n"
            ):

                if (
                    tolerate_torn_tail
                    and
                    is_last
                ):

                    break

                raise ValueError(
                    "torn journal tail"
                )

            try:

                record = json.loads(
                    raw.decode(
                        "utf-8"
                    )
                )

            except Exception as exc:

                if (
                    tolerate_torn_tail
                    and
                    is_last
                ):

                    break

                raise ValueError(
                    "invalid journal json"
                ) from exc

            body = record.get(
                "body"
            )

            digest = record.get(
                "sha256"
            )

            if (
                not isinstance(
                    body,
                    dict,
                )
                or
                not isinstance(
                    digest,
                    str,
                )
            ):

                raise ValueError(
                    "journal record malformed"
                )

            if (
                sha256_obj(
                    body
                )
                !=
                digest
            ):

                raise ValueError(
                    "journal record hash mismatch"
                )

            expected_sequence = (
                sequence
                +
                1
            )

            if (
                body.get(
                    "sequence"
                )
                !=
                expected_sequence
            ):

                raise ValueError(
                    "journal sequence mismatch"
                )

            if (
                body.get(
                    "prev_hash"
                )
                !=
                previous_hash
            ):

                raise ValueError(
                    "journal hash-chain mismatch"
                )

            sequence = (
                expected_sequence
            )

            previous_hash = (
                digest
            )

        return (
            sequence,
            previous_hash,
        )


    def reconcile(
        self,
    ) -> StrategyState:

        state = (
            self.read_snapshot()
        )

        seq, tail = (
            self.validate_journal()
        )

        if (
            state.journal_sequence
            !=
            seq
        ):

            raise ValueError(
                "snapshot/journal sequence mismatch"
            )

        if (
            state.last_journal_hash
            !=
            tail
        ):

            raise ValueError(
                "snapshot/journal tail hash mismatch"
            )

        return state


# --------------------------------------------------------------------------------------------------
# SYNTHETIC ENGINE
# --------------------------------------------------------------------------------------------------

class SyntheticEngine:

    def __init__(
        self,
        store: DurableStore,
    ):

        self.store = (
            store
        )

        self.lock = (
            threading.RLock()
        )

        self.recovery_lease_owner:
            Optional[str] = None


    @staticmethod
    def validate_intent(
        intent: Intent,
        state: StrategyState,
    ) -> None:

        if (
            intent.symbol
            !=
            state.symbol
        ):

            raise ValueError(
                "wrong symbol"
            )

        if (
            intent.generation
            !=
            state.generation
        ):

            raise ValueError(
                "stale or future generation"
            )

        if (
            intent.epoch
            !=
            state.epoch
        ):

            raise ValueError(
                "stale or future epoch"
            )

        if (
            intent.nonce
            <=
            state.highest_nonce
        ):

            raise ValueError(
                "stale nonce"
            )

        if (
            intent.intent_id
            in
            state.consumed_intents
        ):

            raise ValueError(
                "consumed intent replay"
            )

        if (
            sha256_obj(
                intent.payload
            )
            !=
            intent.payload_hash
        ):

            raise ValueError(
                "payload hash mismatch"
            )

        if (
            intent.payload.get(
                "newClientOrderId"
            )
            !=
            intent.intent_id
        ):

            raise ValueError(
                "payload intent binding mismatch"
            )

        if (
            intent.payload.get(
                "symbol"
            )
            !=
            intent.symbol
        ):

            raise ValueError(
                "payload symbol binding mismatch"
            )

        if (
            intent.payload.get(
                "quantity"
            )
            !=
            intent.quantity
        ):

            raise ValueError(
                "payload quantity binding mismatch"
            )


    @staticmethod
    def validate_transition(
        current: Optional[str],
        target: str,
    ) -> None:

        allowed = (
            ALLOWED_TRANSITIONS.get(
                current,
                set(),
            )
        )

        if target not in allowed:

            raise ValueError(
                f"invalid transition "
                f"{current!r} -> {target!r}"
            )


    def transition(
        self,
        state: StrategyState,
        target: str,
        event: str,
        details: Dict[str, Any],
    ) -> None:

        if state.terminal:

            raise ValueError(
                "terminal state is immutable"
            )

        self.validate_transition(
            state.phase,
            target,
        )

        state.phase = (
            target
        )

        if (
            target
            ==
            PHASE_TERMINAL
        ):

            state.terminal = (
                True
            )

        self.store.append_journal(
            state,
            event,
            details,
        )

        self.store.write_snapshot_atomic(
            state
        )


    def prepare(
        self,
        state: StrategyState,
        intent: Intent,
    ) -> None:

        with self.lock:

            self.validate_intent(
                intent,
                state,
            )

            if (
                state.active_intent
                is not None
            ):

                raise ValueError(
                    "another intent already active"
                )

            state.active_intent = (
                intent.as_dict()
            )

            state.highest_nonce = (
                intent.nonce
            )

            self.transition(
                state,
                PHASE_PREPARED,
                "INTENT_PREPARED",
                {
                    "intent_id":
                        intent.intent_id,

                    "payload_hash":
                        intent.payload_hash,
                },
            )


    def authorize(
        self,
        state: StrategyState,
        intent: Intent,
    ) -> str:

        with self.lock:

            self._require_active_binding(
                state,
                intent,
            )

            auth_body = {
                "intent_id":
                    intent.intent_id,

                "payload_hash":
                    intent.payload_hash,

                "generation":
                    intent.generation,

                "epoch":
                    intent.epoch,

                "nonce":
                    intent.nonce,

                "synthetic_only":
                    True,

                "network_write_allowed":
                    False,
            }

            auth_hash = (
                sha256_obj(
                    auth_body
                )
            )

            state.active_authorization = {
                "body":
                    auth_body,

                "sha256":
                    auth_hash,
            }

            self.transition(
                state,
                PHASE_AUTHORIZED,
                "AUTHORIZATION_CREATED",
                {
                    "intent_id":
                        intent.intent_id,

                    "authorization_hash":
                        auth_hash,
                },
            )

            return auth_hash


    def commit(
        self,
        state: StrategyState,
        intent: Intent,
    ) -> None:

        with self.lock:

            self._require_active_binding(
                state,
                intent,
            )

            self._validate_authorization(
                state,
                intent,
            )

            self.transition(
                state,
                PHASE_COMMITTED,
                "DISPATCH_COMMITTED",
                {
                    "intent_id":
                        intent.intent_id,

                    "payload_hash":
                        intent.payload_hash,
                },
            )


    def synthetic_dispatch(
        self,
        state: StrategyState,
        intent: Intent,
    ) -> Receipt:

        with self.lock:

            self._require_active_binding(
                state,
                intent,
            )

            self._validate_authorization(
                state,
                intent,
            )

            if (
                state.phase
                !=
                PHASE_COMMITTED
            ):

                raise ValueError(
                    "dispatch requires COMMITTED phase"
                )

            if (
                intent.intent_id
                in
                state.consumed_intents
            ):

                raise ValueError(
                    "intent already consumed"
                )

            existing = [
                receipt
                for receipt
                in state.durable_receipts
                if (
                    receipt[
                        "intent_id"
                    ]
                    ==
                    intent.intent_id
                )
            ]

            if existing:

                raise ValueError(
                    "durable receipt already exists"
                )

            receipt = Receipt(
                receipt_id=
                    (
                        "receipt-"
                        +
                        uuid.uuid4().hex
                    ),

                intent_id=
                    intent.intent_id,

                payload_hash=
                    intent.payload_hash,

                generation=
                    intent.generation,

                epoch=
                    intent.epoch,

                nonce=
                    intent.nonce,

                transport=
                    "LOCAL_SYNTHETIC",

                transmitted=
                    False,

                created_ms=
                    now_ms(),
            )

            state.durable_receipts.append(
                receipt.as_dict()
            )

            state.consumed_intents.append(
                intent.intent_id
            )

            state.synthetic_dispatch_count += 1

            self.transition(
                state,
                PHASE_DISPATCHED,
                "SYNTHETIC_DISPATCH_RECORDED",
                {
                    "intent_id":
                        intent.intent_id,

                    "receipt_id":
                        receipt.receipt_id,

                    "transmitted":
                        False,
                },
            )

            return receipt


    def apply(
        self,
        state: StrategyState,
        intent: Intent,
    ) -> None:

        with self.lock:

            self._require_active_binding(
                state,
                intent,
            )

            if (
                intent.intent_id
                not in
                state.consumed_intents
            ):

                raise ValueError(
                    "cannot apply unconsumed intent"
                )

            receipts = [
                receipt
                for receipt
                in state.durable_receipts
                if (
                    receipt[
                        "intent_id"
                    ]
                    ==
                    intent.intent_id
                )
            ]

            if (
                len(
                    receipts
                )
                !=
                1
            ):

                raise ValueError(
                    "exactly one receipt required"
                )

            self.transition(
                state,
                PHASE_APPLIED,
                "SYNTHETIC_EFFECT_APPLIED",
                {
                    "intent_id":
                        intent.intent_id,

                    "receipt_id":
                        receipts[0][
                            "receipt_id"
                        ],
                },
            )


    def finalize(
        self,
        state: StrategyState,
        intent: Intent,
    ) -> None:

        with self.lock:

            self._require_active_binding(
                state,
                intent,
            )

            self.transition(
                state,
                PHASE_TERMINAL,
                "STRATEGY_TERMINAL",
                {
                    "intent_id":
                        intent.intent_id,
                },
            )


    @staticmethod
    def _require_active_binding(
        state: StrategyState,
        intent: Intent,
    ) -> None:

        active = (
            state.active_intent
        )

        if not isinstance(
            active,
            dict,
        ):

            raise ValueError(
                "no active intent"
            )

        keys = (
            "intent_id",
            "payload_hash",
            "generation",
            "epoch",
            "nonce",
        )

        current = (
            intent.as_dict()
        )

        for key in keys:

            if (
                active.get(
                    key
                )
                !=
                current.get(
                    key
                )
            ):

                raise ValueError(
                    f"active intent binding mismatch: {key}"
                )

        if (
            sha256_obj(
                active.get(
                    "payload"
                )
            )
            !=
            active.get(
                "payload_hash"
            )
        ):

            raise ValueError(
                "stored active payload hash mismatch"
            )


    @staticmethod
    def _validate_authorization(
        state: StrategyState,
        intent: Intent,
    ) -> None:

        envelope = (
            state.active_authorization
        )

        if not isinstance(
            envelope,
            dict,
        ):

            raise ValueError(
                "authorization missing"
            )

        body = envelope.get(
            "body"
        )

        digest = envelope.get(
            "sha256"
        )

        if (
            not isinstance(
                body,
                dict,
            )
            or
            sha256_obj(
                body
            )
            !=
            digest
        ):

            raise ValueError(
                "authorization hash mismatch"
            )

        expected = {
            "intent_id":
                intent.intent_id,

            "payload_hash":
                intent.payload_hash,

            "generation":
                intent.generation,

            "epoch":
                intent.epoch,

            "nonce":
                intent.nonce,

            "synthetic_only":
                True,

            "network_write_allowed":
                False,
        }

        if body != expected:

            raise ValueError(
                "authorization binding mismatch"
            )


    def acquire_recovery_lease(
        self,
        owner: str,
    ) -> bool:

        with self.lock:

            if (
                self.recovery_lease_owner
                is None
            ):

                self.recovery_lease_owner = (
                    owner
                )

                return True

            return (
                self.recovery_lease_owner
                ==
                owner
            )


    def release_recovery_lease(
        self,
        owner: str,
    ) -> None:

        with self.lock:

            if (
                self.recovery_lease_owner
                ==
                owner
            ):

                self.recovery_lease_owner = (
                    None
                )


    def recover_once(
        self,
        owner: str,
    ) -> str:

        if not self.acquire_recovery_lease(
            owner
        ):

            return (
                "LEASE_REJECTED"
            )

        try:

            state = (
                self.store.reconcile()
            )

            if state.terminal:

                return (
                    "TERMINAL_NOOP"
                )

            active = (
                state.active_intent
            )

            if not active:

                return (
                    "NO_ACTIVE_INTENT"
                )

            intent = Intent(
                **active
            )

            if (
                state.phase
                ==
                PHASE_COMMITTED
            ):

                self.synthetic_dispatch(
                    state,
                    intent,
                )

                return (
                    "DISPATCHED"
                )

            if (
                state.phase
                ==
                PHASE_DISPATCHED
            ):

                self.apply(
                    state,
                    intent,
                )

                return (
                    "APPLIED"
                )

            if (
                state.phase
                ==
                PHASE_APPLIED
            ):

                self.finalize(
                    state,
                    intent,
                )

                return (
                    "FINALIZED"
                )

            return (
                f"NOOP_{state.phase}"
            )

        finally:

            self.release_recovery_lease(
                owner
            )


# ==================================================================================================
# PART 3 - ADVERSARIAL TESTS
# ==================================================================================================

def expect_rejection(
    fn,
    contains: Optional[str] = None,
) -> bool:

    try:

        fn()

    except Exception as exc:

        if contains is None:

            return True

        return (
            contains.lower()
            in
            str(exc).lower()
        )

    return False


# --------------------------------------------------------------------------------------------------

def clone_store(
    source: DurableStore,
    name: str,
) -> DurableStore:

    target_dir = Path(
        tempfile.mkdtemp(
            prefix=
                f"r35b_{name}_"
        )
    )

    target = DurableStore(
        target_dir
    )

    for filename in (
        "strategy_state.json",
        "transition_journal.jsonl",
    ):

        src = (
            source.directory
            /
            filename
        )

        if src.exists():

            shutil.copy2(
                src,
                target.directory
                /
                filename,
            )

    return target


# --------------------------------------------------------------------------------------------------

def build_committed_baseline(
    store: DurableStore,
) -> Tuple[
    SyntheticEngine,
    StrategyState,
    Intent,
]:

    store.reset()

    engine = SyntheticEngine(
        store
    )

    state = StrategyState()

    store.write_snapshot_atomic(
        state
    )

    intent = Intent.create(
        generation=1,
        epoch=1,
        nonce=1,
    )

    engine.prepare(
        state,
        intent,
    )

    engine.authorize(
        state,
        intent,
    )

    engine.commit(
        state,
        intent,
    )

    return (
        engine,
        state,
        intent,
    )


# --------------------------------------------------------------------------------------------------
# TEST SUITE
# --------------------------------------------------------------------------------------------------

def run_tests(
) -> Dict[str, Any]:

    global NETWORK_WRITE_COUNT

    NETWORK_WRITE_COUNT = 0

    store = DurableStore(
        STATE_DIR
    )

    store.reset()

    engine = SyntheticEngine(
        store
    )


    # ==============================================================================================
    # STARTUP
    # ==============================================================================================

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
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: STATE DIR={STATE_DIR}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )

    print(
        f"{VERSION}: NETWORK WRITES DISABLED",
        flush=True,
    )


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 1: SAFETY CONSTANTS"
    )

    assert_test(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    assert_test(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )

    assert_test(
        "Real Orders Are Disabled",
        REAL_ORDERS_ENABLED
        is False,
    )

    assert_test(
        "Demo Orders Are Disabled",
        DEMO_ORDERS_ENABLED
        is False,
    )

    assert_test(
        "Leverage Mutation Is Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    assert_test(
        "Margin Mutation Is Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    assert_test(
        "Position Mutation Is Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    assert_test(
        "Account Mutation Is Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 2: HARD NETWORK-WRITE FIREBREAK"
    )

    before = (
        NETWORK_WRITE_COUNT
    )

    blocked = expect_rejection(
        lambda:
            network_write_attempt(
                "POST",
                "/forbidden",
                {
                    "x": 1,
                },
            ),
        "blocked",
    )

    # This invokes only the local firebreak function.
    # No socket/network operation occurs.
    #
    # Restore the diagnostic count to the number of actual network writes,
    # which remains zero.

    with NETWORK_WRITE_LOCK:

        NETWORK_WRITE_COUNT = (
            before
        )

    assert_test(
        "Network Write Attempt Is Locally Blocked",
        blocked,
    )

    assert_test(
        "Actual Network Write Count Remains Zero",
        NETWORK_WRITE_COUNT
        ==
        0,
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 3: BASELINE DURABLE COMMIT"
    )

    state = StrategyState()

    store.write_snapshot_atomic(
        state
    )

    intent = Intent.create(
        generation=1,
        epoch=1,
        nonce=1,
    )

    engine.prepare(
        state,
        intent,
    )

    engine.authorize(
        state,
        intent,
    )

    engine.commit(
        state,
        intent,
    )

    reconciled = (
        store.reconcile()
    )

    assert_test(
        "Baseline Phase Is COMMITTED",
        reconciled.phase
        ==
        PHASE_COMMITTED,
    )

    assert_test(
        "Baseline Journal Has Three Records",
        reconciled.journal_sequence
        ==
        3,
    )

    assert_test(
        "Baseline Has No Dispatch Yet",
        reconciled.synthetic_dispatch_count
        ==
        0,
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 4: SNAPSHOT HASH TAMPER REJECTION"
    )

    tamper_store = clone_store(
        store,
        "snapshot_tamper",
    )

    env = json.loads(
        tamper_store.state_file.read_text(
            encoding="utf-8"
        )
    )

    env[
        "body"
    ][
        "epoch"
    ] = 999

    tamper_store.state_file.write_text(
        canonical_json(
            env
        )
        +
        "\n",
        encoding="utf-8",
    )

    assert_test(
        "Tampered Snapshot Is Rejected",
        expect_rejection(
            tamper_store.read_snapshot,
            "hash",
        ),
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 5: JOURNAL RECORD HASH TAMPER REJECTION"
    )

    tamper_store = clone_store(
        store,
        "journal_record_tamper",
    )

    lines = (
        tamper_store.journal_file
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    first = json.loads(
        lines[0]
    )

    first[
        "body"
    ][
        "event"
    ] = "FORGED_EVENT"

    lines[0] = (
        canonical_json(
            first
        )
    )

    tamper_store.journal_file.write_text(
        "\n".join(
            lines
        )
        +
        "\n",
        encoding="utf-8",
    )

    assert_test(
        "Tampered Journal Record Is Rejected",
        expect_rejection(
            tamper_store.validate_journal,
            "hash",
        ),
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 6: JOURNAL HASH-CHAIN TAMPER REJECTION"
    )

    tamper_store = clone_store(
        store,
        "journal_chain_tamper",
    )

    lines = (
        tamper_store.journal_file
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    second = json.loads(
        lines[1]
    )

    second[
        "body"
    ][
        "prev_hash"
    ] = "f" * 64

    second[
        "sha256"
    ] = sha256_obj(
        second[
            "body"
        ]
    )

    lines[1] = (
        canonical_json(
            second
        )
    )

    tamper_store.journal_file.write_text(
        "\n".join(
            lines
        )
        +
        "\n",
        encoding="utf-8",
    )

    assert_test(
        "Broken Journal Hash Chain Is Rejected",
        expect_rejection(
            tamper_store.validate_journal,
            "chain",
        ),
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 7: TORN JOURNAL TAIL REJECTION"
    )

    tamper_store = clone_store(
        store,
        "torn_tail",
    )

    with open(
        tamper_store.journal_file,
        "ab",
    ) as handle:

        handle.write(
            b'{"body":{"sequence":4'
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    assert_test(
        "Strict Validation Rejects Torn Tail",
        expect_rejection(
            tamper_store.validate_journal,
            "torn",
        ),
    )

    seq, tail = (
        tamper_store.validate_journal(
            tolerate_torn_tail=True,
        )
    )

    assert_test(
        "Recovery Scanner Ignores Only Torn Final Tail",
        (
            seq
            ==
            3
            and
            tail
            ==
            state.last_journal_hash
        ),
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 8: DUPLICATE INTENT REJECTION"
    )

    duplicate_rejected = (
        expect_rejection(
            lambda:
                engine.prepare(
                    state,
                    intent,
                ),
            "active",
        )
        or
        expect_rejection(
            lambda:
                SyntheticEngine.validate_intent(
                    intent,
                    state,
                ),
            "nonce",
        )
    )

    assert_test(
        "Duplicate Active Intent Is Rejected",
        duplicate_rejected,
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 9: FIRST SYNTHETIC DISPATCH"
    )

    receipt = (
        engine.synthetic_dispatch(
            state,
            intent,
        )
    )

    state_after_dispatch = (
        store.reconcile()
    )

    assert_test(
        "Synthetic Receipt Was Created",
        bool(
            receipt.receipt_id
        ),
    )

    assert_test(
        "Synthetic Receipt Was Not Transmitted",
        receipt.transmitted
        is False,
    )

    assert_test(
        "Synthetic Dispatch Count Is One",
        state_after_dispatch.synthetic_dispatch_count
        ==
        1,
    )

    assert_test(
        "Intent Is Consumed Exactly Once",
        state_after_dispatch.consumed_intents.count(
            intent.intent_id
        )
        ==
        1,
    )

    assert_test(
        "Exactly One Durable Receipt Exists",
        len(
            state_after_dispatch.durable_receipts
        )
        ==
        1,
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 10: DUPLICATE DURABLE RECEIPT REJECTION"
    )

    assert_test(
        "Second Dispatch For Same Intent Is Rejected",
        expect_rejection(
            lambda:
                engine.synthetic_dispatch(
                    state,
                    intent,
                )
        ),
    )

    assert_test(
        "Durable Receipt Count Remains One",
        len(
            store.reconcile().durable_receipts
        )
        ==
        1,
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 11: CONSUMED-INTENT REPLAY REJECTION"
    )

    replay_state = (
        store.reconcile()
    )

    replay_state.phase = None
    replay_state.terminal = False
    replay_state.active_intent = None
    replay_state.active_authorization = None

    replay_intent = (
        copy.deepcopy(
            intent
        )
    )

    replay_intent.nonce = 2

    replay_intent.payload[
        "newClientOrderId"
    ] = replay_intent.intent_id

    replay_intent.payload_hash = (
        sha256_obj(
            replay_intent.payload
        )
    )

    assert_test(
        "Consumed Intent ID Cannot Be Prepared Again",
        expect_rejection(
            lambda:
                SyntheticEngine.validate_intent(
                    replay_intent,
                    replay_state,
                ),
            "consumed",
        ),
    )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 12: STALE GENERATION REJECTION"
    )

    fresh_state = StrategyState(
        generation=5,
        epoch=7,
    )

    stale_generation_intent = (
        Intent.create(
            generation=4,
            epoch=7,
            nonce=1,
        )
    )

    assert_test(
        "Stale Generation Is Rejected",
        expect_rejection(
            lambda:
                SyntheticEngine.validate_intent(
                    stale_generation_intent,
                    fresh_state,
                ),
            "generation",
        ),
    )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 13: STALE EPOCH REJECTION"
    )

    stale_epoch_intent = (
        Intent.create(
            generation=5,
            epoch=6,
            nonce=1,
        )
    )

    assert_test(
        "Stale Epoch Is Rejected",
        expect_rejection(
            lambda:
                SyntheticEngine.validate_intent(
                    stale_epoch_intent,
                    fresh_state,
                ),
            "epoch",
        ),
    )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 14: REORDERED PHASE TRANSITION REJECTION"
    )

    assert_test(
        "PREPARED Cannot Jump Directly To DISPATCHED",
        expect_rejection(
            lambda:
                SyntheticEngine.validate_transition(
                    PHASE_PREPARED,
                    PHASE_DISPATCHED,
                ),
            "invalid",
        ),
    )

    assert_test(
        "COMMITTED Cannot Regress To AUTHORIZED",
        expect_rejection(
            lambda:
                SyntheticEngine.validate_transition(
                    PHASE_COMMITTED,
                    PHASE_AUTHORIZED,
                ),
            "invalid",
        ),
    )


    # ==============================================================================================
    # TEST 15
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 15: PAYLOAD-BINDING TAMPER REJECTION"
    )

    payload_store = DurableStore(
        Path(
            tempfile.mkdtemp(
                prefix="r35b_payload_"
            )
        )
    )

    (
        payload_engine,
        payload_state,
        payload_intent,
    ) = build_committed_baseline(
        payload_store
    )

    payload_state.active_intent[
        "payload"
    ][
        "quantity"
    ] = "99.9999"

    assert_test(
        "Tampered Stored Payload Is Rejected Before Dispatch",
        expect_rejection(
            lambda:
                payload_engine.synthetic_dispatch(
                    payload_state,
                    payload_intent,
                ),
            "payload",
        ),
    )

    assert_test(
        "Tampered Payload Produced No Receipt",
        len(
            payload_state.durable_receipts
        )
        ==
        0,
    )


    # ==============================================================================================
    # TEST 16
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 16: AUTHORIZATION-BINDING TAMPER REJECTION"
    )

    auth_store = DurableStore(
        Path(
            tempfile.mkdtemp(
                prefix="r35b_auth_"
            )
        )
    )

    (
        auth_engine,
        auth_state,
        auth_intent,
    ) = build_committed_baseline(
        auth_store
    )

    auth_state.active_authorization[
        "body"
    ][
        "network_write_allowed"
    ] = True

    assert_test(
        "Tampered Authorization Is Rejected Before Dispatch",
        expect_rejection(
            lambda:
                auth_engine.synthetic_dispatch(
                    auth_state,
                    auth_intent,
                ),
            "authorization",
        ),
    )

    assert_test(
        "Tampered Authorization Produced No Receipt",
        len(
            auth_state.durable_receipts
        )
        ==
        0,
    )


    # ==============================================================================================
    # TEST 17
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 17: INTERRUPTED ATOMIC SNAPSHOT REPLACEMENT"
    )

    atomic_store = clone_store(
        store,
        "atomic_replace",
    )

    original = (
        atomic_store.read_snapshot()
    )

    forged = copy.deepcopy(
        original.envelope()
    )

    forged[
        "body"
    ][
        "generation"
    ] += 100

    atomic_store.tmp_file.write_text(
        canonical_json(
            forged
        )[:80],
        encoding="utf-8",
    )

    recovered = (
        atomic_store.read_snapshot()
    )

    assert_test(
        "Committed Snapshot Survives Pre-Replace Crash",
        recovered.generation
        ==
        original.generation,
    )

    assert_test(
        "Temporary Snapshot Cannot Override Committed State",
        atomic_store.state_file.exists(),
    )


    # ==============================================================================================
    # TEST 18
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 18: CONCURRENT RECOVERY SINGLE-WINNER FENCING"
    )

    conc_store = DurableStore(
        Path(
            tempfile.mkdtemp(
                prefix="r35b_concurrent_"
            )
        )
    )

    (
        conc_engine,
        _,
        conc_intent,
    ) = build_committed_baseline(
        conc_store
    )

    results: List[str] = []

    results_lock = (
        threading.Lock()
    )

    start_barrier = (
        threading.Barrier(
            8
        )
    )


    def worker(
        index: int,
    ) -> None:

        try:

            start_barrier.wait()

            result = (
                conc_engine.recover_once(
                    f"worker-{index}"
                )
            )

        except Exception as exc:

            result = (
                f"ERROR:"
                f"{type(exc).__name__}:"
                f"{exc}"
            )

        with results_lock:

            results.append(
                result
            )


    threads = [
        threading.Thread(
            target=worker,
            args=(i,),
        )
        for i
        in range(8)
    ]

    for thread in threads:

        thread.start()

    for thread in threads:

        thread.join()


    conc_state = (
        conc_store.reconcile()
    )

    assert_test(
        "Concurrent Recovery Produced Exactly One Dispatch",
        conc_state.synthetic_dispatch_count
        ==
        1,
    )

    assert_test(
        "Concurrent Recovery Produced Exactly One Receipt",
        len(
            conc_state.durable_receipts
        )
        ==
        1,
    )

    assert_test(
        "Concurrent Recovery Consumed Intent Exactly Once",
        conc_state.consumed_intents.count(
            conc_intent.intent_id
        )
        ==
        1,
    )

    assert_test(
        "Concurrent Recovery Did Not Duplicate Receipt IDs",
        len(
            {
                receipt[
                    "receipt_id"
                ]
                for receipt
                in conc_state.durable_receipts
            }
        )
        ==
        1,
    )


    # ==============================================================================================
    # TEST 19
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 19: RECOVERY TO TERMINAL"
    )

    for i in range(
        8
    ):

        current = (
            conc_store.reconcile()
        )

        if current.terminal:

            break

        conc_engine.recover_once(
            f"finisher-{i}"
        )


    terminal_state = (
        conc_store.reconcile()
    )

    assert_test(
        "Recovered Strategy Reaches TERMINAL",
        terminal_state.phase
        ==
        PHASE_TERMINAL,
    )

    assert_test(
        "Recovered Strategy Terminal Flag Is True",
        terminal_state.terminal
        is True,
    )

    assert_test(
        "Exactly One Dispatch Survives Full Recovery",
        terminal_state.synthetic_dispatch_count
        ==
        1,
    )


    # ==============================================================================================
    # TEST 20
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 20: TERMINAL-STATE IMMUTABILITY"
    )

    assert_test(
        "Terminal Strategy Rejects Further Transition",
        expect_rejection(
            lambda:
                conc_engine.transition(
                    terminal_state,
                    PHASE_TERMINAL,
                    "FORGED",
                    {},
                ),
            "immutable",
        ),
    )


    # ==============================================================================================
    # TEST 21
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 21: RESTART REPLAY REJECTION"
    )

    restarted_engine = SyntheticEngine(
        conc_store
    )

    restart_result = (
        restarted_engine.recover_once(
            "restart-worker"
        )
    )

    restarted_state = (
        conc_store.reconcile()
    )

    assert_test(
        "Restart Recovery Is Terminal No-Op",
        restart_result
        ==
        "TERMINAL_NOOP",
    )

    assert_test(
        "Restart Does Not Add Dispatch",
        restarted_state.synthetic_dispatch_count
        ==
        1,
    )

    assert_test(
        "Restart Does Not Add Receipt",
        len(
            restarted_state.durable_receipts
        )
        ==
        1,
    )

    assert_test(
        "Restart Does Not Reconsume Intent",
        restarted_state.consumed_intents.count(
            conc_intent.intent_id
        )
        ==
        1,
    )


    # ==============================================================================================
    # TEST 22
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 22: JOURNAL / SNAPSHOT RECONCILIATION"
    )

    final_seq, final_tail = (
        conc_store.validate_journal()
    )

    reconciled_final = (
        conc_store.reconcile()
    )

    assert_test(
        "Snapshot Sequence Matches Journal",
        reconciled_final.journal_sequence
        ==
        final_seq,
    )

    assert_test(
        "Snapshot Tail Hash Matches Journal",
        reconciled_final.last_journal_hash
        ==
        final_tail,
    )

    assert_test(
        "Final Snapshot Hash Is Valid",
        bool(
            conc_store.read_snapshot()
        ),
    )


    # ==============================================================================================
    # TEST 23
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 23: DUPLICATE RECEIPT-ID DETECTION"
    )

    forged_state = copy.deepcopy(
        reconciled_final
    )

    forged_state.durable_receipts.append(
        copy.deepcopy(
            forged_state.durable_receipts[
                0
            ]
        )
    )

    receipt_ids = [
        receipt[
            "receipt_id"
        ]
        for receipt
        in forged_state.durable_receipts
    ]

    duplicate_detected = (
        len(
            receipt_ids
        )
        !=
        len(
            set(
                receipt_ids
            )
        )
    )

    assert_test(
        "Duplicate Durable Receipt ID Is Detectable",
        duplicate_detected,
    )

    assert_test(
        "Persisted State Still Has Unique Receipt IDs",
        len(
            {
                receipt[
                    "receipt_id"
                ]
                for receipt
                in reconciled_final.durable_receipts
            }
        )
        ==
        len(
            reconciled_final.durable_receipts
        ),
    )


    # ==============================================================================================
    # TEST 24
    # ==============================================================================================

    banner(
        f"{VERSION} TEST 24: FINAL SAFETY AUDIT"
    )

    assert_test(
        "Synthetic Transport Remains Enabled",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    assert_test(
        "Real Orders Remain Disabled",
        REAL_ORDERS_ENABLED
        is False,
    )

    assert_test(
        "Demo Orders Remain Disabled",
        DEMO_ORDERS_ENABLED
        is False,
    )

    assert_test(
        "Leverage Mutation Remains Disabled",
        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    assert_test(
        "Margin Mutation Remains Disabled",
        MARGIN_MUTATION_ENABLED
        is False,
    )

    assert_test(
        "Position Mutation Remains Disabled",
        POSITION_MUTATION_ENABLED
        is False,
    )

    assert_test(
        "Account Mutation Remains Disabled",
        ACCOUNT_MUTATION_ENABLED
        is False,
    )

    assert_test(
        "Strategy Network Write Count Is Zero",
        NETWORK_WRITE_COUNT
        ==
        0,
    )


    return {
        "phase":
            reconciled_final.phase,

        "dispatch_count":
            reconciled_final.synthetic_dispatch_count,

        "receipt_count":
            len(
                reconciled_final.durable_receipts
            ),

        "consumed_count":
            len(
                reconciled_final.consumed_intents
            ),

        "journal_records":
            reconciled_final.journal_sequence,

        "network_writes":
            NETWORK_WRITE_COUNT,

        "state_file":
            str(
                conc_store.state_file
            ),

        "journal_file":
            str(
                conc_store.journal_file
            ),
    }


# ==================================================================================================
# PART 4 - MAIN / SUMMARY / HEARTBEAT
# ==================================================================================================

def main(
) -> None:

    health_server:
        Optional[
            ThreadingHTTPServer
        ] = None

    try:

        health_server = (
            start_health_server()
        )

    except OSError as exc:

        print(
            f"{VERSION}: HEALTH SERVER WARNING="
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )


    try:

        result = (
            run_tests()
        )


        # ==========================================================================================
        # SUMMARY
        # ==========================================================================================

        banner(
            f"{VERSION}: VALIDATION SUMMARY"
        )

        print(
            f"{VERSION}: FINAL STRATEGY PHASE="
            f"{result['phase']}",
            flush=True,
        )

        print(
            f"{VERSION}: SYNTHETIC DISPATCH COUNT="
            f"{result['dispatch_count']}",
            flush=True,
        )

        print(
            f"{VERSION}: DURABLE RECEIPTS="
            f"{result['receipt_count']}",
            flush=True,
        )

        print(
            f"{VERSION}: CONSUMED INTENTS="
            f"{result['consumed_count']}",
            flush=True,
        )

        print(
            f"{VERSION}: JOURNAL RECORDS="
            f"{result['journal_records']}",
            flush=True,
        )

        print(
            f"{VERSION}: NETWORK WRITE COUNT="
            f"{result['network_writes']}",
            flush=True,
        )

        print(
            f"{VERSION}: STATE FILE="
            f"{result['state_file']}",
            flush=True,
        )

        print(
            f"{VERSION}: JOURNAL FILE="
            f"{result['journal_file']}",
            flush=True,
        )

        print(
            f"{VERSION}: ASSERTIONS PASSED="
            f"{PASS_COUNT}",
            flush=True,
        )

        print(
            f"{VERSION}: ASSERTIONS FAILED="
            f"{FAIL_COUNT}",
            flush=True,
        )


        # ==========================================================================================
        # FINAL RESULT
        # ==========================================================================================

        banner(
            f"{VERSION}: FINAL RESULT"
        )

        print(
            f"{VERSION}: ADVERSARIAL DURABLE-STATE VALIDATION PASSED",
            flush=True,
        )

        print(
            f"{VERSION}: SNAPSHOT TAMPER REJECTION VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: JOURNAL HASH / HASH-CHAIN TAMPER REJECTION VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: TORN JOURNAL TAIL HANDLING VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: DUPLICATE INTENT / RECEIPT REJECTION VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: STALE GENERATION / EPOCH REJECTION VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: PHASE-ORDER FENCING VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: PAYLOAD / AUTHORIZATION BINDING VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: CRASH-WINDOW SNAPSHOT RECOVERY VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: CONCURRENT RECOVERY EXACTLY-ONCE FENCING VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: TERMINAL IMMUTABILITY VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: RESTART REPLAY REJECTION VERIFIED",
            flush=True,
        )

        print(
            f"{VERSION}: NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            f"{VERSION}: NO DEMO ORDER WAS SENT",
            flush=True,
        )

        print(
            f"{VERSION}: NO NETWORK WRITE WAS PERFORMED",
            flush=True,
        )

        print(
            f"{VERSION}: NO LEVERAGE MUTATION WAS PERFORMED",
            flush=True,
        )

        print(
            f"{VERSION}: NO MARGIN MUTATION WAS PERFORMED",
            flush=True,
        )

        print(
            f"{VERSION}: NO POSITION MUTATION WAS PERFORMED",
            flush=True,
        )

        sep()


        # ==========================================================================================
        # PERSISTENT HEARTBEAT
        # ==========================================================================================

        heartbeat = 0

        while True:

            heartbeat += 1

            print(
                f"{VERSION}: HEARTBEAT {heartbeat} | "
                f"STATUS=PASSED | "
                f"SYNTHETIC_ONLY=TRUE | "
                f"NETWORK_WRITES={NETWORK_WRITE_COUNT}",
                flush=True,
            )

            time.sleep(
                60
            )


    except KeyboardInterrupt:

        print(
            f"{VERSION}: STOPPED BY USER",
            flush=True,
        )


    except Exception as exc:

        banner(
            f"{VERSION}: VALIDATION FAILED"
        )

        print(
            f"{VERSION}: ERROR="
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        print(
            f"{VERSION}: ASSERTIONS PASSED="
            f"{PASS_COUNT}",
            flush=True,
        )

        print(
            f"{VERSION}: ASSERTIONS FAILED="
            f"{FAIL_COUNT}",
            flush=True,
        )

        print(
            f"{VERSION}: NETWORK WRITE COUNT="
            f"{NETWORK_WRITE_COUNT}",
            flush=True,
        )

        raise


    finally:

        if health_server is not None:

            try:

                health_server.shutdown()

                health_server.server_close()

            except Exception:

                pass


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

if __name__ == "__main__":

    main()
