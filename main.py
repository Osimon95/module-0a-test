# ==================================================================================================
# R35D - CRASH-WINDOW RECOVERY ACROSS GENERATION ADVANCEMENT
# ==================================================================================================
#
# SAFETY MODEL
#
#   - SYNTHETIC TRANSPORT ONLY
#   - NO POST
#   - NO PUT
#   - NO PATCH
#   - NO DELETE
#   - NO REAL ORDER
#   - NO DEMO ORDER
#   - NO LEVERAGE CHANGE
#   - NO MARGIN CHANGE
#   - NO POSITION CHANGE
#   - NO ACCOUNT MUTATION
#   - NETWORK WRITE COUNT MUST REMAIN ZERO
#
# R35D validates:
#
#   GENERATION 1 PREPARE
#       ↓
#   GENERATION 1 AUTHORIZE
#       ↓
#   GENERATION 1 SYNTHETIC DISPATCH
#       ↓
#   GENERATION 1 COMPLETE
#       ↓
#   DURABLE RESTART
#       ↓
#   GENERATION ADVANCE 1 → 2
#       ↓
#   CRASH WINDOWS AROUND GENERATION 2 PREPARE / AUTHORIZE / DISPATCH
#       ↓
#   STALE GENERATION / STALE EPOCH / STALE AUTHORIZATION REJECTION
#       ↓
#   EXACTLY-ONCE SYNTHETIC RECOVERY
#       ↓
#   FINAL JOURNAL + SNAPSHOT INTEGRITY
#
# ==================================================================================================

from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import time
from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


VERSION = "R35D"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
HEALTH_PORT = int(os.getenv("PORT", "10000"))

STATE_DIR = Path(
    os.getenv(
        "R35D_STATE_DIR",
        "/tmp/r35d_state",
    )
)

SNAPSHOT_PATH = STATE_DIR / "snapshot.json"
JOURNAL_PATH = STATE_DIR / "journal.jsonl"

ZERO_HASH = "0" * 64

SYNTHETIC_TRANSPORT_ONLY = True

NETWORK_WRITES_ENABLED = False
REAL_ORDERS_ENABLED = False
DEMO_ORDERS_ENABLED = False

PHASE_EMPTY = "EMPTY"
PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

SEPARATOR = "-" * 100


# ==================================================================================================
# UTILITIES
# ==================================================================================================


def canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def stable_hash(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(value)
    )


def atomic_write_json(
    path: Path,
    payload: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            payload,
            handle,
            sort_keys=True,
            separators=(",", ":"),
        )

        handle.flush()

        os.fsync(
            handle.fileno()
        )

    os.replace(
        temp_path,
        path,
    )


def print_header(
    title: str,
) -> None:

    print(
        SEPARATOR,
        flush=True,
    )

    print(
        title,
        flush=True,
    )

    print(
        SEPARATOR,
        flush=True,
    )


def check(
    label: str,
    condition: bool,
) -> None:

    status = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{label:<84} {status}",
        flush=True,
    )

    if not condition:
        raise AssertionError(
            label
        )


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

            body = json.dumps(
                {
                    "ok": True,
                    "version": VERSION,
                    "symbol": SYMBOL,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
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
                    len(body)
                ),
            )

            self.end_headers()

            self.wfile.write(
                body
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

    def runner() -> None:

        server = HTTPServer(
            (
                "0.0.0.0",
                HEALTH_PORT,
            ),
            HealthHandler,
        )

        server.serve_forever()

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()

    print(
        f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}",
        flush=True,
    )


# ==================================================================================================
# DURABLE DATA STRUCTURES
# ==================================================================================================


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = PHASE_EMPTY

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

    journal_sequence: int = 0

    last_journal_hash: str = ZERO_HASH

    snapshot_integrity: str = ""

    def payload_without_integrity(
        self,
    ) -> Dict[str, Any]:

        payload = asdict(
            self
        )

        payload.pop(
            "snapshot_integrity",
            None,
        )

        return payload

    def refresh_integrity(
        self,
    ) -> None:

        self.snapshot_integrity = stable_hash(
            self.payload_without_integrity()
        )

    def integrity_is_valid(
        self,
    ) -> bool:

        return (
            self.snapshot_integrity
            == stable_hash(
                self.payload_without_integrity()
            )
        )


# ==================================================================================================
# DURABLE STORE
# ==================================================================================================


class DurableStore:

    def __init__(
        self,
        state_dir: Path,
    ) -> None:

        self.state_dir = state_dir

        self.snapshot_path = (
            state_dir
            / "snapshot.json"
        )

        self.journal_path = (
            state_dir
            / "journal.jsonl"
        )

        self.state_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def reset(
        self,
    ) -> None:

        if self.state_dir.exists():

            shutil.rmtree(
                self.state_dir
            )

        self.state_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_snapshot(
        self,
        state: StrategyState,
    ) -> None:

        state.refresh_integrity()

        atomic_write_json(
            self.snapshot_path,
            asdict(state),
        )

    def load_snapshot(
        self,
    ) -> StrategyState:

        with self.snapshot_path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            payload = json.load(
                handle
            )

        state = StrategyState(
            **payload
        )

        if not state.integrity_is_valid():

            raise RuntimeError(
                "Snapshot integrity validation failed"
            )

        if state.version != VERSION:

            raise RuntimeError(
                "Snapshot version mismatch"
            )

        if state.symbol != SYMBOL:

            raise RuntimeError(
                "Snapshot symbol mismatch"
            )

        return state

    def append_journal(
        self,
        state: StrategyState,
        event: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        next_sequence = (
            state.journal_sequence
            + 1
        )

        record_core = {

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "sequence":
                next_sequence,

            "event":
                event,

            "generation":
                state.generation,

            "epoch":
                state.epoch,

            "previous_hash":
                state.last_journal_hash,

            "data":
                data,
        }

        record_hash = stable_hash(
            record_core
        )

        record = dict(
            record_core
        )

        record[
            "record_hash"
        ] = record_hash

        with self.journal_path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                canonical_json(
                    record
                )
                + "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        state.journal_sequence = (
            next_sequence
        )

        state.last_journal_hash = (
            record_hash
        )

        return record

    def read_journal(
        self,
    ) -> List[
        Dict[str, Any]
    ]:

        if not self.journal_path.exists():

            return []

        records: List[
            Dict[str, Any]
        ] = []

        with self.journal_path.open(
            "r",
            encoding="utf-8",
        ) as handle:

            for line in handle:

                line = line.strip()

                if line:

                    records.append(
                        json.loads(
                            line
                        )
                    )

        return records

    def validate_journal(
        self,
        state: StrategyState,
    ) -> Tuple[
        bool,
        str,
    ]:

        records = (
            self.read_journal()
        )

        previous_hash = (
            ZERO_HASH
        )

        for (
            expected_sequence,
            record,
        ) in enumerate(
            records,
            start=1,
        ):

            if (
                record.get(
                    "sequence"
                )
                != expected_sequence
            ):

                return (
                    False,
                    "sequence mismatch",
                )

            if (
                record.get(
                    "previous_hash"
                )
                != previous_hash
            ):

                return (
                    False,
                    "previous hash mismatch",
                )

            supplied_hash = (
                record.get(
                    "record_hash"
                )
            )

            core = dict(
                record
            )

            core.pop(
                "record_hash",
                None,
            )

            calculated_hash = (
                stable_hash(
                    core
                )
            )

            if (
                supplied_hash
                != calculated_hash
            ):

                return (
                    False,
                    "record hash mismatch",
                )

            if (
                len(
                    str(
                        supplied_hash
                    )
                )
                != 64
            ):

                return (
                    False,
                    "invalid record hash length",
                )

            previous_hash = (
                supplied_hash
            )

        if (
            len(records)
            != state.journal_sequence
        ):

            return (
                False,
                "state sequence mismatch",
            )

        if (
            previous_hash
            != state.last_journal_hash
        ):

            return (
                False,
                "state journal head mismatch",
            )

        return (
            True,
            "ok",
        )


# ==================================================================================================
# SYNTHETIC STRATEGY ENGINE
# ==================================================================================================


class StrategyEngine:

    def __init__(
        self,
        store: DurableStore,
        state: Optional[
            StrategyState
        ] = None,
    ) -> None:

        self.store = store

        self.state = (
            state
            if state is not None
            else StrategyState()
        )

    def persist(
        self,
    ) -> None:

        self.store.save_snapshot(
            self.state
        )

    def journal(
        self,
        event: str,
        data: Dict[str, Any],
    ) -> None:

        self.store.append_journal(
            self.state,
            event,
            data,
        )

        self.persist()

    def next_nonce(
        self,
    ) -> int:

        self.state.highest_nonce += 1

        return (
            self.state.highest_nonce
        )

    def prepare_intent(
        self,
        label: str,
    ) -> Dict[str, Any]:

        if self.state.terminal:

            raise RuntimeError(
                "Terminal strategy rejects new intent"
            )

        if (
            self.state.active_intent
            is not None
        ):

            raise RuntimeError(
                "Active intent already exists"
            )

        nonce = (
            self.next_nonce()
        )

        intent_core = {

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "label":
                label,

            "generation":
                self.state.generation,

            "epoch":
                self.state.epoch,

            "nonce":
                nonce,

            "synthetic_only":
                True,

            "transmit":
                False,

            "network_write":
                False,
        }

        intent = dict(
            intent_core
        )

        intent[
            "intent_id"
        ] = stable_hash(
            intent_core
        )

        self.state.active_intent = (
            intent
        )

        self.state.active_authorization = (
            None
        )

        self.state.phase = (
            PHASE_PREPARED
        )

        self.journal(
            "INTENT_PREPARED",
            {
                "intent_id":
                    intent[
                        "intent_id"
                    ],

                "nonce":
                    nonce,
            },
        )

        return intent

    def authorize(
        self,
        intent: Dict[str, Any],
    ) -> Dict[str, Any]:

        self._validate_current_intent(
            intent
        )

        if (
            self.state.phase
            != PHASE_PREPARED
        ):

            raise RuntimeError(
                "Strategy is not PREPARED"
            )

        authorization_core = {

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "generation":
                intent[
                    "generation"
                ],

            "epoch":
                intent[
                    "epoch"
                ],

            "nonce":
                intent[
                    "nonce"
                ],

            "intent_id":
                intent[
                    "intent_id"
                ],

            "synthetic_only":
                True,

            "network_write":
                False,

            "consumed":
                False,
        }

        authorization = dict(
            authorization_core
        )

        authorization[
            "authorization_id"
        ] = stable_hash(
            authorization_core
        )

        self.state.active_authorization = (
            authorization
        )

        self.state.phase = (
            PHASE_AUTHORIZED
        )

        self.journal(
            "AUTHORIZED",
            {
                "intent_id":
                    intent[
                        "intent_id"
                    ],

                "authorization_id":
                    authorization[
                        "authorization_id"
                    ],
            },
        )

        return authorization

    def synthetic_dispatch(
        self,
        intent: Dict[str, Any],
        authorization: Dict[str, Any],
    ) -> Dict[str, Any]:

        self._validate_current_intent(
            intent
        )

        self._validate_current_authorization(
            intent,
            authorization,
        )

        if (
            intent[
                "intent_id"
            ]
            in self.state.consumed_intents
        ):

            raise RuntimeError(
                "Consumed intent replay rejected"
            )

        if (
            authorization[
                "authorization_id"
            ]
            in self.state.consumed_authorizations
        ):

            raise RuntimeError(
                "Consumed authorization replay rejected"
            )

        if self.state.phase not in (
            PHASE_AUTHORIZED,
            PHASE_DISPATCHED,
        ):

            raise RuntimeError(
                "Strategy is not authorized for dispatch"
            )

        receipt_core = {

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "generation":
                intent[
                    "generation"
                ],

            "epoch":
                intent[
                    "epoch"
                ],

            "nonce":
                intent[
                    "nonce"
                ],

            "intent_id":
                intent[
                    "intent_id"
                ],

            "authorization_id":
                authorization[
                    "authorization_id"
                ],

            "synthetic_only":
                True,

            "transmitted":
                False,

            "network_write":
                False,
        }

        receipt = dict(
            receipt_core
        )

        receipt[
            "receipt_id"
        ] = stable_hash(
            receipt_core
        )

        self.state.phase = (
            PHASE_DISPATCHED
        )

        self.journal(
            "DISPATCHED",
            {
                "intent_id":
                    intent[
                        "intent_id"
                    ],

                "authorization_id":
                    authorization[
                        "authorization_id"
                    ],

                "receipt_id":
                    receipt[
                        "receipt_id"
                    ],
            },
        )

        self.state.consumed_intents.append(
            intent[
                "intent_id"
            ]
        )

        self.state.consumed_authorizations.append(
            authorization[
                "authorization_id"
            ]
        )

        self.state.durable_receipts.append(
            receipt
        )

        self.state.synthetic_dispatch_count += 1

        self.state.active_authorization = (
            dict(
                authorization
            )
        )

        self.state.active_authorization[
            "consumed"
        ] = True

        self.state.phase = (
            PHASE_COMPLETED
        )

        self.state.terminal = True

        self.journal(
            "COMPLETED",
            {
                "intent_id":
                    intent[
                        "intent_id"
                    ],

                "authorization_id":
                    authorization[
                        "authorization_id"
                    ],

                "receipt_id":
                    receipt[
                        "receipt_id"
                    ],
            },
        )

        return receipt

    def advance_generation(
        self,
    ) -> None:

        if not self.state.terminal:

            raise RuntimeError(
                "Generation advance requires terminal state"
            )

        old_generation = (
            self.state.generation
        )

        old_epoch = (
            self.state.epoch
        )

        self.state.generation += 1

        self.state.epoch += 1

        self.state.phase = (
            PHASE_EMPTY
        )

        self.state.active_intent = (
            None
        )

        self.state.active_authorization = (
            None
        )

        self.state.terminal = False

        self.journal(
            "GENERATION_ADVANCED",
            {
                "from_generation":
                    old_generation,

                "to_generation":
                    self.state.generation,

                "from_epoch":
                    old_epoch,

                "to_epoch":
                    self.state.epoch,
            },
        )

    def _validate_current_intent(
        self,
        intent: Dict[str, Any],
    ) -> None:

        if (
            intent.get(
                "generation"
            )
            != self.state.generation
        ):

            raise RuntimeError(
                "Stale generation intent rejected"
            )

        if (
            intent.get(
                "epoch"
            )
            != self.state.epoch
        ):

            raise RuntimeError(
                "Stale epoch intent rejected"
            )

        if (
            intent.get(
                "symbol"
            )
            != SYMBOL
        ):

            raise RuntimeError(
                "Wrong symbol intent rejected"
            )

        if (
            intent.get(
                "synthetic_only"
            )
            is not True
        ):

            raise RuntimeError(
                "Non-synthetic intent rejected"
            )

        if (
            intent.get(
                "transmit"
            )
            is not False
        ):

            raise RuntimeError(
                "Transmit-enabled intent rejected"
            )

        if (
            intent.get(
                "network_write"
            )
            is not False
        ):

            raise RuntimeError(
                "Network-write-enabled intent rejected"
            )

        if (
            self.state.active_intent
            is None
        ):

            raise RuntimeError(
                "No active intent"
            )

        if (
            intent.get(
                "intent_id"
            )
            != self.state.active_intent.get(
                "intent_id"
            )
        ):

            raise RuntimeError(
                "Intent binding mismatch"
            )

        core = dict(
            intent
        )

        supplied_id = core.pop(
            "intent_id",
            None,
        )

        if (
            supplied_id
            != stable_hash(
                core
            )
        ):

            raise RuntimeError(
                "Intent integrity mismatch"
            )

    def _validate_current_authorization(
        self,
        intent: Dict[str, Any],
        authorization: Dict[str, Any],
    ) -> None:

        if (
            authorization.get(
                "generation"
            )
            != self.state.generation
        ):

            raise RuntimeError(
                "Stale authorization generation rejected"
            )

        if (
            authorization.get(
                "epoch"
            )
            != self.state.epoch
        ):

            raise RuntimeError(
                "Stale authorization epoch rejected"
            )

        if (
            authorization.get(
                "intent_id"
            )
            != intent.get(
                "intent_id"
            )
        ):

            raise RuntimeError(
                "Authorization intent binding mismatch"
            )

        if (
            authorization.get(
                "nonce"
            )
            != intent.get(
                "nonce"
            )
        ):

            raise RuntimeError(
                "Authorization nonce binding mismatch"
            )

        if (
            authorization.get(
                "synthetic_only"
            )
            is not True
        ):

            raise RuntimeError(
                "Non-synthetic authorization rejected"
            )

        if (
            authorization.get(
                "network_write"
            )
            is not False
        ):

            raise RuntimeError(
                "Network-write authorization rejected"
            )

        if (
            self.state.active_authorization
            is None
        ):

            raise RuntimeError(
                "No active authorization"
            )

        if (
            authorization.get(
                "authorization_id"
            )
            != self.state.active_authorization.get(
                "authorization_id"
            )
        ):

            raise RuntimeError(
                "Authorization binding mismatch"
            )

        core = dict(
            authorization
        )

        supplied_id = core.pop(
            "authorization_id",
            None,
        )

        if (
            supplied_id
            != stable_hash(
                core
            )
        ):

            raise RuntimeError(
                "Authorization integrity mismatch"
            )


# ==================================================================================================
# CRASH / RESTART HELPERS
# ==================================================================================================


def restart_engine(
    store: DurableStore,
) -> StrategyEngine:

    restored = (
        store.load_snapshot()
    )

    return StrategyEngine(
        store,
        restored,
    )


def clone_dict(
    value: Dict[str, Any],
) -> Dict[str, Any]:

    return json.loads(
        json.dumps(
            value
        )
    )


def expect_rejection(
    callable_obj,
) -> bool:

    try:

        callable_obj()

    except Exception:

        return True

    return False


# ==================================================================================================
# R35D VALIDATION
# ==================================================================================================


def run_validation() -> None:

    store = DurableStore(
        STATE_DIR
    )

    store.reset()

    engine = StrategyEngine(
        store
    )

    engine.persist()


    # --------------------------------------------------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 1: SAFETY CONSTANTS"
    )

    check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    check(
        "Network Writes Are Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Real Orders Are Disabled",
        REAL_ORDERS_ENABLED
        is False,
    )

    check(
        "Demo Orders Are Disabled",
        DEMO_ORDERS_ENABLED
        is False,
    )

    check(
        "Initial Network Write Count Is Zero",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 2: INITIAL DURABLE STATE"
    )

    check(
        "Initial Generation Is One",
        engine.state.generation
        == 1,
    )

    check(
        "Initial Epoch Is One",
        engine.state.epoch
        == 1,
    )

    check(
        "Initial Nonce Is Zero",
        engine.state.highest_nonce
        == 0,
    )

    check(
        "Initial Strategy Is Nonterminal",
        engine.state.terminal
        is False,
    )

    check(
        "Initial Phase Is EMPTY",
        engine.state.phase
        == PHASE_EMPTY,
    )

    check(
        "Initial Snapshot Integrity Is Valid",
        engine.state.integrity_is_valid(),
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 3: GENERATION ONE INTENT PREPARATION"
    )

    g1_intent = (
        engine.prepare_intent(
            "GENERATION_ONE"
        )
    )

    check(
        "Generation One Intent Was Created",
        bool(
            g1_intent.get(
                "intent_id"
            )
        ),
    )

    check(
        "Generation One Intent Is Synthetic Only",
        g1_intent[
            "synthetic_only"
        ]
        is True,
    )

    check(
        "Generation One Intent Forbids Transmission",
        g1_intent[
            "transmit"
        ]
        is False,
    )

    check(
        "Generation One Intent Forbids Network Write",
        g1_intent[
            "network_write"
        ]
        is False,
    )

    check(
        "Generation One Intent Is Bound To Generation One",
        g1_intent[
            "generation"
        ]
        == 1,
    )

    check(
        "Generation One Intent Is Bound To Epoch One",
        g1_intent[
            "epoch"
        ]
        == 1,
    )

    check(
        "Strategy Phase Is PREPARED",
        engine.state.phase
        == PHASE_PREPARED,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 4: GENERATION ONE AUTHORIZATION"
    )

    g1_auth = (
        engine.authorize(
            g1_intent
        )
    )

    check(
        "Generation One Authorization Was Created",
        bool(
            g1_auth.get(
                "authorization_id"
            )
        ),
    )

    check(
        "Authorization Binds Exact Generation One Intent",
        g1_auth[
            "intent_id"
        ]
        == g1_intent[
            "intent_id"
        ],
    )

    check(
        "Generation One Authorization Is Initially Unconsumed",
        g1_auth[
            "consumed"
        ]
        is False,
    )

    check(
        "Generation One Authorization Is Synthetic Only",
        g1_auth[
            "synthetic_only"
        ]
        is True,
    )

    check(
        "Generation One Authorization Forbids Network Write",
        g1_auth[
            "network_write"
        ]
        is False,
    )

    check(
        "Strategy Phase Is AUTHORIZED",
        engine.state.phase
        == PHASE_AUTHORIZED,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 5
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 5: GENERATION ONE SYNTHETIC DISPATCH"
    )

    g1_receipt = (
        engine.synthetic_dispatch(
            g1_intent,
            g1_auth,
        )
    )

    check(
        "Generation One Synthetic Receipt Was Created",
        bool(
            g1_receipt.get(
                "receipt_id"
            )
        ),
    )

    check(
        "Generation One Dispatch Was Not Transmitted",
        g1_receipt[
            "transmitted"
        ]
        is False,
    )

    check(
        "Generation One Dispatch Made No Network Write",
        g1_receipt[
            "network_write"
        ]
        is False,
    )

    check(
        "Synthetic Dispatch Count Is One",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Generation One Strategy Reached COMPLETED",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    check(
        "Generation One Strategy Is Terminal",
        engine.state.terminal
        is True,
    )

    check(
        "Strategy Network Write Count Is Zero",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 6
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 6: GENERATION ONE DURABLE RESTART"
    )

    engine = restart_engine(
        store
    )

    check(
        "Generation One Terminal State Survives Restart",
        engine.state.terminal
        is True,
    )

    check(
        "Generation One COMPLETED Phase Survives Restart",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    check(
        "Generation One Consumed Intent Survives Restart",
        g1_intent[
            "intent_id"
        ]
        in engine.state.consumed_intents,
    )

    check(
        "Generation One Consumed Authorization Survives Restart",
        g1_auth[
            "authorization_id"
        ]
        in engine.state.consumed_authorizations,
    )

    check(
        "Generation One Receipt Survives Restart",
        any(
            receipt[
                "receipt_id"
            ]
            == g1_receipt[
                "receipt_id"
            ]
            for receipt
            in engine.state.durable_receipts
        ),
    )

    check(
        "Generation One Dispatch Count Survives Restart",
        engine.state.synthetic_dispatch_count
        == 1,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 7
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 7: GENERATION ADVANCE"
    )

    engine.advance_generation()

    check(
        "Generation Advanced From One To Two",
        engine.state.generation
        == 2,
    )

    check(
        "Epoch Advanced From One To Two",
        engine.state.epoch
        == 2,
    )

    check(
        "Generation Two Starts Nonterminal",
        engine.state.terminal
        is False,
    )

    check(
        "Generation Two Starts With No Active Intent",
        engine.state.active_intent
        is None,
    )

    check(
        "Generation Two Starts With No Active Authorization",
        engine.state.active_authorization
        is None,
    )

    check(
        "Generation One Receipt Is Preserved",
        any(
            receipt[
                "receipt_id"
            ]
            == g1_receipt[
                "receipt_id"
            ]
            for receipt
            in engine.state.durable_receipts
        ),
    )

    check(
        "Generation One Consumed Intent Is Preserved",
        g1_intent[
            "intent_id"
        ]
        in engine.state.consumed_intents,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 8
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 8: CRASH WINDOW A - RESTART AFTER GENERATION ADVANCE"
    )

    engine = restart_engine(
        store
    )

    check(
        "Generation Two Survives Immediate Restart",
        engine.state.generation
        == 2,
    )

    check(
        "Epoch Two Survives Immediate Restart",
        engine.state.epoch
        == 2,
    )

    check(
        "Generation Two Remains Nonterminal",
        engine.state.terminal
        is False,
    )

    check(
        "Generation Two Remains EMPTY",
        engine.state.phase
        == PHASE_EMPTY,
    )

    check(
        "Generation One Receipt Still Exists",
        any(
            receipt[
                "receipt_id"
            ]
            == g1_receipt[
                "receipt_id"
            ]
            for receipt
            in engine.state.durable_receipts
        ),
    )

    check(
        "Synthetic Dispatch Count Remains One",
        engine.state.synthetic_dispatch_count
        == 1,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 9
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 9: STALE GENERATION ONE ARTIFACT REJECTION"
    )

    check(
        "Generation One Intent Is Rejected In Generation Two",
        expect_rejection(
            lambda:
                engine.authorize(
                    g1_intent
                )
        ),
    )

    check(
        "Generation Remains Two",
        engine.state.generation
        == 2,
    )

    check(
        "Epoch Remains Two",
        engine.state.epoch
        == 2,
    )

    check(
        "Synthetic Dispatch Count Remains One",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 10
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 10: GENERATION TWO INTENT PREPARATION"
    )

    g2_intent = (
        engine.prepare_intent(
            "GENERATION_TWO"
        )
    )

    check(
        "Generation Two Intent Was Created",
        bool(
            g2_intent.get(
                "intent_id"
            )
        ),
    )

    check(
        "Generation Two Intent Is Bound To Generation Two",
        g2_intent[
            "generation"
        ]
        == 2,
    )

    check(
        "Generation Two Intent Is Bound To Epoch Two",
        g2_intent[
            "epoch"
        ]
        == 2,
    )

    check(
        "Generation Two Nonce Is Monotonically Higher",
        g2_intent[
            "nonce"
        ]
        > g1_intent[
            "nonce"
        ],
    )

    check(
        "Generation Two Intent Is Synthetic Only",
        g2_intent[
            "synthetic_only"
        ]
        is True,
    )

    check(
        "Generation Two Intent Forbids Transmission",
        g2_intent[
            "transmit"
        ]
        is False,
    )

    check(
        "Generation Two Intent Forbids Network Write",
        g2_intent[
            "network_write"
        ]
        is False,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 11
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 11: CRASH WINDOW B - RESTART AFTER PREPARE"
    )

    engine = restart_engine(
        store
    )

    check(
        "Prepared Generation Two Intent Survives Restart",
        engine.state.active_intent
        is not None,
    )

    check(
        "Prepared Intent ID Survives Restart",
        engine.state.active_intent[
            "intent_id"
        ]
        == g2_intent[
            "intent_id"
        ],
    )

    check(
        "Generation Two Remains PREPARED",
        engine.state.phase
        == PHASE_PREPARED,
    )

    check(
        "Generation Two Remains Nonterminal",
        engine.state.terminal
        is False,
    )

    check(
        "No Additional Synthetic Dispatch Occurred",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 12
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 12: STALE EPOCH TAMPER REJECTION"
    )

    stale_epoch_intent = clone_dict(
        g2_intent
    )

    stale_epoch_intent[
        "epoch"
    ] = 1

    stale_core = dict(
        stale_epoch_intent
    )

    stale_core.pop(
        "intent_id",
        None,
    )

    stale_epoch_intent[
        "intent_id"
    ] = stable_hash(
        stale_core
    )

    check(
        "Stale Epoch Intent Is Rejected",
        expect_rejection(
            lambda:
                engine.authorize(
                    stale_epoch_intent
                )
        ),
    )

    check(
        "Current Epoch Remains Two",
        engine.state.epoch
        == 2,
    )

    check(
        "No Synthetic Dispatch Occurred During Epoch Rejection",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    check(
        "No Network Write Occurred During Epoch Rejection",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 13
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 13: GENERATION TWO AUTHORIZATION"
    )

    g2_auth = (
        engine.authorize(
            g2_intent
        )
    )

    check(
        "Generation Two Authorization Was Created",
        bool(
            g2_auth.get(
                "authorization_id"
            )
        ),
    )

    check(
        "Generation Two Authorization Binds Exact Intent",
        g2_auth[
            "intent_id"
        ]
        == g2_intent[
            "intent_id"
        ],
    )

    check(
        "Generation Two Authorization Is Bound To Generation Two",
        g2_auth[
            "generation"
        ]
        == 2,
    )

    check(
        "Generation Two Authorization Is Bound To Epoch Two",
        g2_auth[
            "epoch"
        ]
        == 2,
    )

    check(
        "Generation Two Authorization Is Initially Unconsumed",
        g2_auth[
            "consumed"
        ]
        is False,
    )

    check(
        "Strategy Phase Is AUTHORIZED",
        engine.state.phase
        == PHASE_AUTHORIZED,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 14
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 14: CRASH WINDOW C - RESTART AFTER AUTHORIZATION"
    )

    engine = restart_engine(
        store
    )

    check(
        "Authorized Generation Two Intent Survives Restart",
        engine.state.active_intent[
            "intent_id"
        ]
        == g2_intent[
            "intent_id"
        ],
    )

    check(
        "Generation Two Authorization Survives Restart",
        engine.state.active_authorization[
            "authorization_id"
        ]
        == g2_auth[
            "authorization_id"
        ],
    )

    check(
        "Generation Two Remains AUTHORIZED",
        engine.state.phase
        == PHASE_AUTHORIZED,
    )

    check(
        "Authorization Remains Unconsumed Before Dispatch",
        engine.state.active_authorization[
            "consumed"
        ]
        is False,
    )

    check(
        "Synthetic Dispatch Count Is Still One",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Network Write Count Is Still Zero",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 15
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 15: STALE GENERATION ONE AUTHORIZATION REJECTION"
    )

    forged_g1_auth = clone_dict(
        g1_auth
    )

    check(
        "Generation One Authorization Is Rejected In Generation Two",
        expect_rejection(
            lambda:
                engine.synthetic_dispatch(
                    g2_intent,
                    forged_g1_auth,
                )
        ),
    )

    check(
        "Synthetic Dispatch Count Still One",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Network Write Count Still Zero",
        engine.state.network_write_count
        == 0,
    )

    check(
        "Generation Two Strategy Remains Nonterminal",
        engine.state.terminal
        is False,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 16
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 16: AUTHORIZATION BINDING TAMPER REJECTION"
    )

    forged_auth = clone_dict(
        g2_auth
    )

    forged_auth[
        "intent_id"
    ] = g1_intent[
        "intent_id"
    ]

    forged_core = dict(
        forged_auth
    )

    forged_core.pop(
        "authorization_id",
        None,
    )

    forged_auth[
        "authorization_id"
    ] = stable_hash(
        forged_core
    )

    check(
        "Forged Authorization Binding Is Rejected",
        expect_rejection(
            lambda:
                engine.synthetic_dispatch(
                    g2_intent,
                    forged_auth,
                )
        ),
    )

    check(
        "Synthetic Dispatch Count Remains One",
        engine.state.synthetic_dispatch_count
        == 1,
    )

    check(
        "Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )

    check(
        "Valid Authorization Is Still Active",
        engine.state.active_authorization[
            "authorization_id"
        ]
        == g2_auth[
            "authorization_id"
        ],
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 17
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 17: GENERATION TWO SYNTHETIC DISPATCH"
    )

    g2_receipt = (
        engine.synthetic_dispatch(
            g2_intent,
            g2_auth,
        )
    )

    check(
        "Generation Two Synthetic Receipt Was Created",
        bool(
            g2_receipt.get(
                "receipt_id"
            )
        ),
    )

    check(
        "Generation Two Dispatch Was Not Transmitted",
        g2_receipt[
            "transmitted"
        ]
        is False,
    )

    check(
        "Generation Two Dispatch Made No Network Write",
        g2_receipt[
            "network_write"
        ]
        is False,
    )

    check(
        "Synthetic Dispatch Count Is Two",
        engine.state.synthetic_dispatch_count
        == 2,
    )

    check(
        "Generation Two Strategy Reached COMPLETED",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    check(
        "Generation Two Strategy Is Terminal",
        engine.state.terminal
        is True,
    )

    check(
        "Strategy Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 18
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 18: CRASH WINDOW D - RESTART AFTER COMPLETION"
    )

    engine = restart_engine(
        store
    )

    check(
        "Generation Two Survives Completion Restart",
        engine.state.generation
        == 2,
    )

    check(
        "Epoch Two Survives Completion Restart",
        engine.state.epoch
        == 2,
    )

    check(
        "Generation Two Terminal State Survives Restart",
        engine.state.terminal
        is True,
    )

    check(
        "Generation Two COMPLETED Phase Survives Restart",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    check(
        "Both Consumed Intents Survive Restart",
        len(
            engine.state.consumed_intents
        )
        == 2,
    )

    check(
        "Both Consumed Authorizations Survive Restart",
        len(
            engine.state.consumed_authorizations
        )
        == 2,
    )

    check(
        "Both Durable Receipts Survive Restart",
        len(
            engine.state.durable_receipts
        )
        == 2,
    )

    check(
        "Synthetic Dispatch Count Two Survives Restart",
        engine.state.synthetic_dispatch_count
        == 2,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 19
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 19: RESTART REPLAY PROTECTION"
    )

    check(
        "Restart Replay Of Generation Two Is Rejected",
        expect_rejection(
            lambda:
                engine.synthetic_dispatch(
                    g2_intent,
                    g2_auth,
                )
        ),
    )

    check(
        "Restart Does Not Duplicate Synthetic Dispatch",
        engine.state.synthetic_dispatch_count
        == 2,
    )

    check(
        "Restart Makes No Network Write",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 20
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 20: STALE GENERATION ONE REPLAY AFTER SECOND COMPLETION"
    )

    check(
        "Generation One Replay Remains Rejected",
        expect_rejection(
            lambda:
                engine.synthetic_dispatch(
                    g1_intent,
                    g1_auth,
                )
        ),
    )

    check(
        "Synthetic Dispatch Count Remains Two",
        engine.state.synthetic_dispatch_count
        == 2,
    )

    check(
        "Network Write Count Remains Zero",
        engine.state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 21
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 21: TERMINAL IMMUTABILITY"
    )

    check(
        "Terminal Strategy Rejects New Intent",
        expect_rejection(
            lambda:
                engine.prepare_intent(
                    "FORBIDDEN_AFTER_TERMINAL"
                )
        ),
    )

    check(
        "Terminal State Remains True",
        engine.state.terminal
        is True,
    )

    check(
        "Terminal Phase Remains COMPLETED",
        engine.state.phase
        == PHASE_COMPLETED,
    )

    check(
        "Generation Remains Two",
        engine.state.generation
        == 2,
    )

    check(
        "Epoch Remains Two",
        engine.state.epoch
        == 2,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 22
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 22: JOURNAL INTEGRITY"
    )

    records = (
        store.read_journal()
    )

    (
        valid_journal,
        journal_reason,
    ) = store.validate_journal(
        engine.state
    )

    check(
        "Durable Journal Contains Records",
        len(records)
        > 0,
    )

    check(
        "Journal Sequence Matches State",
        len(records)
        == engine.state.journal_sequence,
    )

    check(
        "Journal Head Hash Matches State",
        records[
            -1
        ][
            "record_hash"
        ]
        == engine.state.last_journal_hash,
    )

    check(
        "Every Journal Hash Has Correct Length",
        all(
            len(
                record[
                    "record_hash"
                ]
            )
            == 64
            for record
            in records
        ),
    )

    check(
        "Every Previous Journal Hash Has Correct Length",
        all(
            len(
                record[
                    "previous_hash"
                ]
            )
            == 64
            for record
            in records
        ),
    )

    check(
        "Journal Hash Chain Is Valid",
        valid_journal,
    )

    if not valid_journal:

        raise RuntimeError(
            journal_reason
        )


    # --------------------------------------------------------------------------------------------------
    # TEST 23
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 23: JOURNAL EVENT COUNTS"
    )

    generation_advances = sum(
        1
        for record
        in records
        if record[
            "event"
        ]
        == "GENERATION_ADVANCED"
    )

    prepared_events = sum(
        1
        for record
        in records
        if record[
            "event"
        ]
        == "INTENT_PREPARED"
    )

    authorization_events = sum(
        1
        for record
        in records
        if record[
            "event"
        ]
        == "AUTHORIZED"
    )

    dispatch_events = sum(
        1
        for record
        in records
        if record[
            "event"
        ]
        == "DISPATCHED"
    )

    completed_events = sum(
        1
        for record
        in records
        if record[
            "event"
        ]
        == "COMPLETED"
    )

    check(
        "Journal Contains Exactly One Generation Advance",
        generation_advances
        == 1,
    )

    check(
        "Journal Contains Exactly Two Intent Preparations",
        prepared_events
        == 2,
    )

    check(
        "Journal Contains Exactly Two Authorizations",
        authorization_events
        == 2,
    )

    check(
        "Journal Contains Exactly Two Synthetic Dispatches",
        dispatch_events
        == 2,
    )

    check(
        "Journal Contains Exactly Two Completed Dispatches",
        completed_events
        == 2,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 24
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 24: FINAL SNAPSHOT INTEGRITY"
    )

    final_state = (
        store.load_snapshot()
    )

    check(
        "Final Snapshot Version Is Correct",
        final_state.version
        == VERSION,
    )

    check(
        "Final Snapshot Symbol Is Correct",
        final_state.symbol
        == SYMBOL,
    )

    check(
        "Final Snapshot Integrity Is Valid",
        final_state.integrity_is_valid(),
    )

    check(
        "Final Snapshot Generation Is Two",
        final_state.generation
        == 2,
    )

    check(
        "Final Snapshot Epoch Is Two",
        final_state.epoch
        == 2,
    )

    check(
        "Final Snapshot Nonce Is Two",
        final_state.highest_nonce
        == 2,
    )

    check(
        "Final Snapshot Contains Two Consumed Intents",
        len(
            final_state.consumed_intents
        )
        == 2,
    )

    check(
        "Final Snapshot Contains Two Consumed Authorizations",
        len(
            final_state.consumed_authorizations
        )
        == 2,
    )

    check(
        "Final Snapshot Contains Two Durable Receipts",
        len(
            final_state.durable_receipts
        )
        == 2,
    )

    check(
        "Final Snapshot Dispatch Count Is Two",
        final_state.synthetic_dispatch_count
        == 2,
    )

    check(
        "Final Snapshot Network Write Count Is Zero",
        final_state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 25
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 25: CROSS-GENERATION RECOVERY BINDINGS"
    )

    check(
        "Generation One Receipt Remains Bound To Generation One",
        g1_receipt[
            "generation"
        ]
        == 1,
    )

    check(
        "Generation One Receipt Remains Bound To Epoch One",
        g1_receipt[
            "epoch"
        ]
        == 1,
    )

    check(
        "Generation Two Receipt Is Bound To Generation Two",
        g2_receipt[
            "generation"
        ]
        == 2,
    )

    check(
        "Generation Two Receipt Is Bound To Epoch Two",
        g2_receipt[
            "epoch"
        ]
        == 2,
    )

    check(
        "Generation Two Nonce Is Greater Than Generation One Nonce",
        g2_intent[
            "nonce"
        ]
        > g1_intent[
            "nonce"
        ],
    )

    check(
        "Generation One And Two Intent IDs Differ",
        g1_intent[
            "intent_id"
        ]
        != g2_intent[
            "intent_id"
        ],
    )

    check(
        "Generation One And Two Authorization IDs Differ",
        g1_auth[
            "authorization_id"
        ]
        != g2_auth[
            "authorization_id"
        ],
    )

    check(
        "Generation One And Two Receipt IDs Differ",
        g1_receipt[
            "receipt_id"
        ]
        != g2_receipt[
            "receipt_id"
        ],
    )


    # --------------------------------------------------------------------------------------------------
    # TEST 26
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D TEST 26: FINAL SAFETY FIREBREAK"
    )

    check(
        "Synthetic Transport Remains Enabled",
        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    check(
        "Network Writes Remain Disabled",
        NETWORK_WRITES_ENABLED
        is False,
    )

    check(
        "Real Orders Remain Disabled",
        REAL_ORDERS_ENABLED
        is False,
    )

    check(
        "Demo Orders Remain Disabled",
        DEMO_ORDERS_ENABLED
        is False,
    )

    check(
        "Final Strategy Network Write Count Is Zero",
        final_state.network_write_count
        == 0,
    )


    # --------------------------------------------------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------------------------------------------------

    print_header(
        "R35D: VALIDATION SUMMARY"
    )

    print(
        "Crash-window recovery across generation advancement validated.",
        flush=True,
    )

    print(
        "Generation 1 durable completion preserved.",
        flush=True,
    )

    print(
        "Generation 2 prepared / authorized / completed restart windows preserved.",
        flush=True,
    )

    print(
        "Stale generation, stale epoch, stale authorization and replay attempts rejected.",
        flush=True,
    )

    print(
        "Exactly two synthetic dispatches were durably recorded.",
        flush=True,
    )

    print(
        "Network write count remained zero.",
        flush=True,
    )

    print(
        f"{VERSION}: VALIDATION PASSED",
        flush=True,
    )


# ==================================================================================================
# MAIN
# ==================================================================================================


def main() -> None:

    start_health_server()

    print(
        SEPARATOR,
        flush=True,
    )

    print(
        f"{VERSION}: MAIN.PY ENTERED",
        flush=True,
    )

    print(
        SEPARATOR,
        flush=True,
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

    print(
        f"{VERSION}: REAL ORDERS DISABLED",
        flush=True,
    )

    print(
        f"{VERSION}: DEMO ORDERS DISABLED",
        flush=True,
    )

    run_validation()

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            f"{VERSION}: HEARTBEAT={heartbeat} | "
            f"SYNTHETIC_ONLY={SYNTHETIC_TRANSPORT_ONLY} | "
            f"NETWORK_WRITES_ENABLED={NETWORK_WRITES_ENABLED}",
            flush=True,
        )

        time.sleep(
            60
        )


if __name__ == "__main__":

    main()
