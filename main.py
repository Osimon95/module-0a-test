# ==================================================================================================
# R35B - DURABLE SYNTHETIC INTENT / AUTHORIZATION / DISPATCH RECOVERY VALIDATION
# ==================================================================================================
#
# SAFETY MODEL
#
#   - SYNTHETIC TRANSPORT ONLY
#   - NETWORK WRITES DISABLED
#   - REAL ORDERS DISABLED
#   - DEMO ORDERS DISABLED
#   - LEVERAGE MUTATION DISABLED
#   - MARGIN MUTATION DISABLED
#   - POSITION MUTATION DISABLED
#
# This program performs local validation only.
# It never sends POST / PUT / PATCH / DELETE requests.
#
# ==================================================================================================

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time

from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional


# ==================================================================================================
# R35B CONSTANTS
# ==================================================================================================

VERSION = "R35B"

SYMBOL = (
    os.getenv(
        "SYMBOL",
        "BTCUSDT",
    ).strip().upper()
    or "BTCUSDT"
)

HEALTH_PORT = int(
    os.getenv(
        "PORT",
        os.getenv(
            "HEALTH_PORT",
            "10000",
        ),
    )
)

STATE_DIR = Path(
    os.getenv(
        "STATE_DIR",
        "/tmp/r35b_state",
    )
)

STATE_FILE = (
    STATE_DIR
    / "strategy_state.json"
)

JOURNAL_FILE = (
    STATE_DIR
    / "journal.jsonl"
)


# ==================================================================================================
# ABSOLUTE SAFETY FLAGS
# ==================================================================================================

SYNTHETIC_TRANSPORT_ONLY = True

NETWORK_WRITES_ENABLED = False

REAL_ORDERS_ENABLED = False

DEMO_ORDERS_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False

MARGIN_MUTATION_ENABLED = False

POSITION_MUTATION_ENABLED = False


ZERO_HASH = (
    "0"
    * 64
)


_PRINT_LOCK = (
    threading.Lock()
)


# ==================================================================================================
# LOGGING
# ==================================================================================================

def log(
    message: str = "",
) -> None:

    with _PRINT_LOCK:

        print(
            message,
            flush=True,
        )


def line() -> None:

    log(
        "-"
        * 100
    )


# ==================================================================================================
# CANONICAL SERIALIZATION
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


def sha256_obj(
    value: Any,
) -> str:

    return sha256_text(
        canonical_json(
            value
        )
    )


# ==================================================================================================
# ATOMIC JSON WRITE
# ==================================================================================================

def atomic_write_json(
    path: Path,
    value: Any,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, temp_name = tempfile.mkstemp(
        prefix=(
            f".{path.name}."
        ),
        suffix=".tmp",
        dir=str(
            path.parent
        ),
    )

    try:

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                value,
                handle,
                sort_keys=True,
                separators=(
                    ",",
                    ":",
                ),
                ensure_ascii=False,
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.replace(
            temp_name,
            path,
        )

        try:

            directory_fd = os.open(
                str(
                    path.parent
                ),
                os.O_DIRECTORY,
            )

        except (
            AttributeError,
            OSError,
        ):

            directory_fd = None

        if directory_fd is not None:

            try:

                os.fsync(
                    directory_fd
                )

            finally:

                os.close(
                    directory_fd
                )

    finally:

        if os.path.exists(
            temp_name
        ):

            os.unlink(
                temp_name
            )


# ==================================================================================================
# STRATEGY STATE
# ==================================================================================================

@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: Optional[str] = None

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    # ----------------------------------------------------------------------------------------------
    # IMPORTANT R35B SYNTAX CORRECTION
    #
    # These annotations are complete Python statements.
    #
    # DO NOT use:
    #
    # active_intent:
    #     Optional[Dict[str, Any]] = None
    #
    # That was the source of the SyntaxError.
    # ----------------------------------------------------------------------------------------------

    active_intent: Optional[
        Dict[
            str,
            Any,
        ]
    ] = None

    active_authorization: Optional[
        Dict[
            str,
            Any,
        ]
    ] = None

    consumed_intents: List[
        str
    ] = field(
        default_factory=list
    )

    durable_receipts: List[
        Dict[
            str,
            Any,
        ]
    ] = field(
        default_factory=list
    )

    synthetic_dispatch_count: int = 0

    terminal: bool = False

    last_journal_hash: str = ZERO_HASH

    journal_sequence: int = 0

    def as_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data: Dict[
            str,
            Any,
        ],
    ) -> "StrategyState":

        return cls(

            version=str(
                data.get(
                    "version",
                    VERSION,
                )
            ),

            symbol=str(
                data.get(
                    "symbol",
                    SYMBOL,
                )
            ),

            phase=data.get(
                "phase"
            ),

            generation=int(
                data.get(
                    "generation",
                    1,
                )
            ),

            epoch=int(
                data.get(
                    "epoch",
                    1,
                )
            ),

            highest_nonce=int(
                data.get(
                    "highest_nonce",
                    0,
                )
            ),

            active_intent=data.get(
                "active_intent"
            ),

            active_authorization=data.get(
                "active_authorization"
            ),

            consumed_intents=list(
                data.get(
                    "consumed_intents",
                    [],
                )
            ),

            durable_receipts=list(
                data.get(
                    "durable_receipts",
                    [],
                )
            ),

            synthetic_dispatch_count=int(
                data.get(
                    "synthetic_dispatch_count",
                    0,
                )
            ),

            terminal=bool(
                data.get(
                    "terminal",
                    False,
                )
            ),

            last_journal_hash=str(
                data.get(
                    "last_journal_hash",
                    ZERO_HASH,
                )
            ),

            journal_sequence=int(
                data.get(
                    "journal_sequence",
                    0,
                )
            ),
        )


# ==================================================================================================
# DURABLE STORE
# ==================================================================================================

class DurableStore:

    def __init__(
        self,
        state_file: Path,
        journal_file: Path,
    ) -> None:

        self.state_file = (
            state_file
        )

        self.journal_file = (
            journal_file
        )

        self.lock = (
            threading.RLock()
        )


    def reset(
        self,
    ) -> None:

        with self.lock:

            self.state_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            for path in (
                self.state_file,
                self.journal_file,
            ):

                try:

                    path.unlink()

                except FileNotFoundError:

                    pass


    def save(
        self,
        state: StrategyState,
    ) -> None:

        with self.lock:

            atomic_write_json(
                self.state_file,
                state.as_dict(),
            )


    def load(
        self,
    ) -> StrategyState:

        with self.lock:

            if not self.state_file.exists():

                return StrategyState()

            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as handle:

                data = json.load(
                    handle
                )

            if not isinstance(
                data,
                dict,
            ):

                raise RuntimeError(
                    "State snapshot is not a JSON object"
                )

            state = StrategyState.from_dict(
                data
            )

            if state.version != VERSION:

                raise RuntimeError(
                    "State version mismatch: "
                    f"expected {VERSION}, "
                    f"got {state.version}"
                )

            if state.symbol != SYMBOL:

                raise RuntimeError(
                    "State symbol mismatch: "
                    f"expected {SYMBOL}, "
                    f"got {state.symbol}"
                )

            return state


    def append_journal(
        self,
        state: StrategyState,
        event_type: str,
        payload: Dict[
            str,
            Any,
        ],
    ) -> Dict[
        str,
        Any,
    ]:

        with self.lock:

            sequence = (
                state.journal_sequence
                + 1
            )

            previous_hash = (
                state.last_journal_hash
            )

            body = {

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "sequence":
                    sequence,

                "event_type":
                    event_type,

                "payload":
                    payload,

                "previous_hash":
                    previous_hash,
            }

            record_hash = (
                sha256_obj(
                    body
                )
            )

            record = {

                **body,

                "record_hash":
                    record_hash,
            }

            self.journal_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.journal_file.open(
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
                sequence
            )

            state.last_journal_hash = (
                record_hash
            )

            self.save(
                state
            )

            return record


    def validate_journal(
        self,
    ) -> List[
        Dict[
            str,
            Any,
        ]
    ]:

        with self.lock:

            if not self.journal_file.exists():

                return []

            records: List[
                Dict[
                    str,
                    Any,
                ]
            ] = []

            expected_previous = (
                ZERO_HASH
            )

            expected_sequence = (
                1
            )

            with self.journal_file.open(
                "r",
                encoding="utf-8",
            ) as handle:

                for raw_line in handle:

                    raw_line = (
                        raw_line.strip()
                    )

                    if not raw_line:

                        continue

                    record = json.loads(
                        raw_line
                    )

                    if not isinstance(
                        record,
                        dict,
                    ):

                        raise RuntimeError(
                            "Journal record is not an object"
                        )

                    body = {

                        "version":
                            record.get(
                                "version"
                            ),

                        "symbol":
                            record.get(
                                "symbol"
                            ),

                        "sequence":
                            record.get(
                                "sequence"
                            ),

                        "event_type":
                            record.get(
                                "event_type"
                            ),

                        "payload":
                            record.get(
                                "payload"
                            ),

                        "previous_hash":
                            record.get(
                                "previous_hash"
                            ),
                    }

                    if body[
                        "version"
                    ] != VERSION:

                        raise RuntimeError(
                            "Journal version mismatch"
                        )

                    if body[
                        "symbol"
                    ] != SYMBOL:

                        raise RuntimeError(
                            "Journal symbol mismatch"
                        )

                    if body[
                        "sequence"
                    ] != expected_sequence:

                        raise RuntimeError(
                            "Journal sequence mismatch"
                        )

                    if body[
                        "previous_hash"
                    ] != expected_previous:

                        raise RuntimeError(
                            "Journal previous-hash mismatch"
                        )

                    calculated_hash = (
                        sha256_obj(
                            body
                        )
                    )

                    if record.get(
                        "record_hash"
                    ) != calculated_hash:

                        raise RuntimeError(
                            "Journal record hash mismatch"
                        )

                    records.append(
                        record
                    )

                    expected_previous = (
                        calculated_hash
                    )

                    expected_sequence += (
                        1
                    )

            return records


# ==================================================================================================
# SYNTHETIC TRANSPORT
# ==================================================================================================

class SyntheticTransport:

    def __init__(
        self,
    ) -> None:

        self.network_write_count = (
            0
        )


    def dispatch(
        self,
        envelope: Dict[
            str,
            Any,
        ],
    ) -> Dict[
        str,
        Any,
    ]:

        if not SYNTHETIC_TRANSPORT_ONLY:

            raise RuntimeError(
                "Synthetic-only transport invariant failed"
            )

        if NETWORK_WRITES_ENABLED:

            raise RuntimeError(
                "Network writes must remain disabled"
            )

        if REAL_ORDERS_ENABLED:

            raise RuntimeError(
                "Real orders must remain disabled"
            )

        if DEMO_ORDERS_ENABLED:

            raise RuntimeError(
                "Demo orders must remain disabled"
            )

        if LEVERAGE_MUTATION_ENABLED:

            raise RuntimeError(
                "Leverage mutation must remain disabled"
            )

        if MARGIN_MUTATION_ENABLED:

            raise RuntimeError(
                "Margin mutation must remain disabled"
            )

        if POSITION_MUTATION_ENABLED:

            raise RuntimeError(
                "Position mutation must remain disabled"
            )

        if envelope.get(
            "synthetic_only"
        ) is not True:

            raise RuntimeError(
                "Envelope is not synthetic-only"
            )

        if envelope.get(
            "transmit"
        ) is not False:

            raise RuntimeError(
                "Envelope transmission flag is not false"
            )

        if envelope.get(
            "network_write"
        ) is not False:

            raise RuntimeError(
                "Envelope network-write flag is not false"
            )

        # ------------------------------------------------------------------------------------------
        # ABSOLUTE FIREBREAK
        #
        # There is intentionally no HTTP client here.
        # There is intentionally no urllib POST.
        # There is intentionally no requests.post().
        # There is intentionally no network mutation.
        # ------------------------------------------------------------------------------------------

        self.network_write_count += (
            0
        )

        receipt_body = {

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "intent_id":
                envelope[
                    "intent_id"
                ],

            "authorization_id":
                envelope[
                    "authorization_id"
                ],

            "payload_hash":
                envelope[
                    "payload_hash"
                ],

            "synthetic_only":
                True,

            "transmitted":
                False,

            "network_write":
                False,
        }

        return {

            **receipt_body,

            "receipt_hash":
                sha256_obj(
                    receipt_body
                ),
        }


# ==================================================================================================
# VALIDATION RESULT
# ==================================================================================================

@dataclass
class TestResult:

    name: str

    passed: bool

    detail: str = ""


class Validator:

    def __init__(
        self,
    ) -> None:

        self.results: List[
            TestResult
        ] = []


    def check(
        self,
        name: str,
        condition: bool,
        detail: str = "",
    ) -> None:

        result = TestResult(
            name=name,
            passed=bool(
                condition
            ),
            detail=detail,
        )

        self.results.append(
            result
        )

        status = (
            "✅ PASS"
            if condition
            else
            "❌ FAIL"
        )

        log(
            f"{name:<88} {status}"
        )

        if detail:

            log(
                f"    {detail}"
            )


    def all_passed(
        self,
    ) -> bool:

        return all(
            result.passed
            for result
            in self.results
        )


# ==================================================================================================
# STRATEGY ENGINE
# ==================================================================================================

class StrategyEngine:

    def __init__(
        self,
        store: DurableStore,
        transport: SyntheticTransport,
    ) -> None:

        self.store = (
            store
        )

        self.transport = (
            transport
        )

        self.lock = (
            threading.RLock()
        )

        self.state = (
            self.store.load()
        )


    def _next_nonce(
        self,
    ) -> int:

        self.state.highest_nonce += (
            1
        )

        return (
            self.state.highest_nonce
        )


    def create_intent(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        with self.lock:

            if self.state.terminal:

                raise RuntimeError(
                    "Terminal strategy cannot create another intent"
                )

            if self.state.active_intent is not None:

                raise RuntimeError(
                    "An active intent already exists"
                )

            nonce = (
                self._next_nonce()
            )

            body = {

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "generation":
                    self.state.generation,

                "epoch":
                    self.state.epoch,

                "nonce":
                    nonce,

                "action":
                    "SYNTHETIC_VALIDATE",

                "synthetic_only":
                    True,

                "transmit":
                    False,

                "network_write":
                    False,
            }

            intent_id = (
                sha256_obj(
                    body
                )
            )

            intent = {

                **body,

                "intent_id":
                    intent_id,
            }

            self.state.active_intent = (
                intent
            )

            self.state.phase = (
                "PREPARED"
            )

            self.store.append_journal(

                self.state,

                "INTENT_PREPARED",

                {

                    "intent_id":
                        intent_id,

                    "nonce":
                        nonce,
                },
            )

            return intent


    def authorize(
        self,
        intent: Dict[
            str,
            Any,
        ],
    ) -> Dict[
        str,
        Any,
    ]:

        with self.lock:

            active = (
                self.state.active_intent
            )

            if active is None:

                raise RuntimeError(
                    "No active intent"
                )

            if active.get(
                "intent_id"
            ) != intent.get(
                "intent_id"
            ):

                raise RuntimeError(
                    "Authorization intent binding mismatch"
                )

            intent_id = str(
                intent[
                    "intent_id"
                ]
            )

            if intent_id in (
                self.state.consumed_intents
            ):

                raise RuntimeError(
                    "Intent has already been consumed"
                )

            auth_body = {

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "generation":
                    self.state.generation,

                "epoch":
                    self.state.epoch,

                "nonce":
                    intent[
                        "nonce"
                    ],

                "intent_id":
                    intent_id,

                "synthetic_only":
                    True,

                "transmit":
                    False,

                "network_write":
                    False,
            }

            authorization_id = (
                sha256_obj(
                    auth_body
                )
            )

            authorization = {

                **auth_body,

                "authorization_id":
                    authorization_id,

                "consumed":
                    False,
            }

            self.state.active_authorization = (
                authorization
            )

            self.state.phase = (
                "AUTHORIZED"
            )

            self.store.append_journal(

                self.state,

                "AUTHORIZATION_GRANTED",

                {

                    "intent_id":
                        intent_id,

                    "authorization_id":
                        authorization_id,
                },
            )

            return authorization


    def dispatch(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        with self.lock:

            intent = (
                self.state.active_intent
            )

            authorization = (
                self.state.active_authorization
            )

            if intent is None:

                raise RuntimeError(
                    "No active intent"
                )

            if authorization is None:

                raise RuntimeError(
                    "No active authorization"
                )

            intent_id = str(
                intent[
                    "intent_id"
                ]
            )

            if intent_id in (
                self.state.consumed_intents
            ):

                raise RuntimeError(
                    "Consumed intent replay rejected"
                )

            if authorization.get(
                "consumed"
            ) is True:

                raise RuntimeError(
                    "Consumed authorization replay rejected"
                )

            if authorization.get(
                "intent_id"
            ) != intent_id:

                raise RuntimeError(
                    "Authorization does not bind active intent"
                )

            payload = {

                "symbol":
                    SYMBOL,

                "operation":
                    "NO_NETWORK_WRITE",

                "generation":
                    self.state.generation,

                "epoch":
                    self.state.epoch,

                "nonce":
                    intent[
                        "nonce"
                    ],
            }

            payload_hash = (
                sha256_obj(
                    payload
                )
            )

            envelope = {

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "intent_id":
                    intent_id,

                "authorization_id":
                    authorization[
                        "authorization_id"
                    ],

                "payload":
                    payload,

                "payload_hash":
                    payload_hash,

                "synthetic_only":
                    True,

                "transmit":
                    False,

                "network_write":
                    False,
            }

            self.store.append_journal(

                self.state,

                "DISPATCH_COMMITTED",

                {

                    "intent_id":
                        intent_id,

                    "authorization_id":
                        authorization[
                            "authorization_id"
                        ],

                    "payload_hash":
                        payload_hash,
                },
            )

            authorization[
                "consumed"
            ] = True

            if intent_id not in (
                self.state.consumed_intents
            ):

                self.state.consumed_intents.append(
                    intent_id
                )

            receipt = (
                self.transport.dispatch(
                    envelope
                )
            )

            self.state.synthetic_dispatch_count += (
                1
            )

            self.state.durable_receipts.append(
                receipt
            )

            self.state.phase = (
                "DISPATCHED"
            )

            self.store.append_journal(

                self.state,

                "SYNTHETIC_DISPATCHED",

                {

                    "intent_id":
                        intent_id,

                    "receipt_hash":
                        receipt[
                            "receipt_hash"
                        ],

                    "transmitted":
                        False,
                },
            )

            self.state.phase = (
                "COMPLETED"
            )

            self.state.terminal = (
                True
            )

            self.store.append_journal(

                self.state,

                "FINALIZED",

                {

                    "intent_id":
                        intent_id,

                    "synthetic_dispatch_count":
                        self.state.synthetic_dispatch_count,

                    "terminal":
                        True,
                },
            )

            return receipt


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================

class HealthHandler(
    BaseHTTPRequestHandler
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

        body = json.dumps(

            {

                "ok":
                    True,

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "synthetic_transport_only":
                    SYNTHETIC_TRANSPORT_ONLY,

                "network_writes_enabled":
                    NETWORK_WRITES_ENABLED,
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
                    body
                )
            ),
        )

        self.end_headers()

        self.wfile.write(
            body
        )


    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:

        return


def start_health_server(
) -> Optional[
    ThreadingHTTPServer
]:

    try:

        server = ThreadingHTTPServer(

            (
                "0.0.0.0",
                HEALTH_PORT,
            ),

            HealthHandler,
        )

    except OSError as exc:

        log(
            f"{VERSION}: "
            "HEALTH SERVER NOT STARTED: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return None

    thread = threading.Thread(

        target=server.serve_forever,

        name="r35b-health",

        daemon=True,
    )

    thread.start()

    log(
        f"{VERSION}: "
        f"HEALTH SERVER STARTED ON PORT "
        f"{HEALTH_PORT}"
    )

    return server


# ==================================================================================================
# R35B VALIDATION
# ==================================================================================================

def run_validation(
) -> bool:

    validator = (
        Validator()
    )

    store = DurableStore(
        STATE_FILE,
        JOURNAL_FILE,
    )

    transport = (
        SyntheticTransport()
    )


    # ------------------------------------------------------------------------------------------------
    # R35B starts with a clean local validation state.
    # ------------------------------------------------------------------------------------------------

    store.reset()


    # ==================================================================================================
    # STARTUP
    # ==================================================================================================

    line()

    log(
        f"{VERSION}: MAIN.PY ENTERED"
    )

    line()

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


    # ==================================================================================================
    # TEST 1
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 1: SAFETY CONSTANTS"
    )

    line()

    validator.check(

        "Synthetic Transport Only Is Enabled",

        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    validator.check(

        "Network Writes Are Disabled",

        NETWORK_WRITES_ENABLED
        is False,
    )

    validator.check(

        "Real Orders Are Disabled",

        REAL_ORDERS_ENABLED
        is False,
    )

    validator.check(

        "Demo Orders Are Disabled",

        DEMO_ORDERS_ENABLED
        is False,
    )

    validator.check(

        "Leverage Mutation Remains Disabled",

        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    validator.check(

        "Margin Mutation Remains Disabled",

        MARGIN_MUTATION_ENABLED
        is False,
    )

    validator.check(

        "Position Mutation Remains Disabled",

        POSITION_MUTATION_ENABLED
        is False,
    )


    # ==================================================================================================
    # TEST 2
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 2: INITIAL DURABLE STATE"
    )

    line()

    engine = StrategyEngine(
        store,
        transport,
    )

    validator.check(

        "Initial Generation Is One",

        engine.state.generation
        == 1,
    )

    validator.check(

        "Initial Epoch Is One",

        engine.state.epoch
        == 1,
    )

    validator.check(

        "Initial Nonce Is Zero",

        engine.state.highest_nonce
        == 0,
    )

    validator.check(

        "No Active Intent Initially",

        engine.state.active_intent
        is None,
    )

    validator.check(

        "No Active Authorization Initially",

        engine.state.active_authorization
        is None,
    )

    validator.check(

        "Strategy Is Initially Nonterminal",

        engine.state.terminal
        is False,
    )


    # ==================================================================================================
    # TEST 3
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 3: INTENT PREPARATION"
    )

    line()

    intent = (
        engine.create_intent()
    )

    validator.check(

        "Intent Was Created",

        isinstance(
            intent,
            dict,
        ),
    )

    validator.check(

        "Intent Is Synthetic Only",

        intent.get(
            "synthetic_only"
        )
        is True,
    )

    validator.check(

        "Intent Forbids Transmission",

        intent.get(
            "transmit"
        )
        is False,
    )

    validator.check(

        "Intent Forbids Network Write",

        intent.get(
            "network_write"
        )
        is False,
    )

    validator.check(

        "Intent Is Bound To Current Generation",

        intent.get(
            "generation"
        )
        == engine.state.generation,
    )

    validator.check(

        "Intent Is Bound To Current Epoch",

        intent.get(
            "epoch"
        )
        == engine.state.epoch,
    )

    validator.check(

        "Strategy Phase Is PREPARED",

        engine.state.phase
        == "PREPARED",
    )


    # ==================================================================================================
    # TEST 4
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 4: ONE-TIME AUTHORIZATION"
    )

    line()

    authorization = (
        engine.authorize(
            intent
        )
    )

    validator.check(

        "Authorization Was Created",

        isinstance(
            authorization,
            dict,
        ),
    )

    validator.check(

        "Authorization Binds Exact Intent",

        authorization.get(
            "intent_id"
        )
        == intent.get(
            "intent_id"
        ),
    )

    validator.check(

        "Authorization Is Initially Unconsumed",

        authorization.get(
            "consumed"
        )
        is False,
    )

    validator.check(

        "Authorization Forbids Transmission",

        authorization.get(
            "transmit"
        )
        is False,
    )

    validator.check(

        "Authorization Forbids Network Write",

        authorization.get(
            "network_write"
        )
        is False,
    )

    validator.check(

        "Strategy Phase Is AUTHORIZED",

        engine.state.phase
        == "AUTHORIZED",
    )


    # ==================================================================================================
    # TEST 5
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 5: SYNTHETIC DISPATCH"
    )

    line()

    receipt = (
        engine.dispatch()
    )

    validator.check(

        "Synthetic Receipt Was Created",

        isinstance(
            receipt,
            dict,
        ),
    )

    validator.check(

        "Synthetic Dispatch Was Not Transmitted",

        receipt.get(
            "transmitted"
        )
        is False,
    )

    validator.check(

        "Synthetic Dispatch Made No Network Write",

        receipt.get(
            "network_write"
        )
        is False,
    )

    validator.check(

        "Synthetic Dispatch Count Is One",

        engine.state.synthetic_dispatch_count
        == 1,
    )

    validator.check(

        "Strategy Reached COMPLETED Phase",

        engine.state.phase
        == "COMPLETED",
    )

    validator.check(

        "Strategy Is Terminal",

        engine.state.terminal
        is True,
    )

    validator.check(

        "Strategy Network Write Count Is Zero",

        transport.network_write_count
        == 0,
    )


    # ==================================================================================================
    # TEST 6
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 6: REPLAY REJECTION"
    )

    line()

    replay_rejected = (
        False
    )

    try:

        engine.dispatch()

    except RuntimeError:

        replay_rejected = (
            True
        )

    validator.check(

        "Consumed Intent Replay Is Rejected",

        replay_rejected,
    )

    validator.check(

        "Synthetic Dispatch Count Remains One",

        engine.state.synthetic_dispatch_count
        == 1,
    )

    validator.check(

        "Strategy Network Write Count Still Zero",

        transport.network_write_count
        == 0,
    )


    # ==================================================================================================
    # TEST 7
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 7: DURABLE RESTART"
    )

    line()

    restarted = StrategyEngine(
        store,
        transport,
    )

    validator.check(

        "Terminal State Survives Restart",

        restarted.state.terminal
        is True,
    )

    validator.check(

        "Completed Phase Survives Restart",

        restarted.state.phase
        == "COMPLETED",
    )

    validator.check(

        "Consumed Intent Survives Restart",

        intent[
            "intent_id"
        ]
        in restarted.state.consumed_intents,
    )

    validator.check(

        "Durable Receipt Survives Restart",

        len(
            restarted.state.durable_receipts
        )
        == 1,
    )

    validator.check(

        "Synthetic Dispatch Count Survives Restart",

        restarted.state.synthetic_dispatch_count
        == 1,
    )


    # ==================================================================================================
    # TEST 8
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 8: RESTART REPLAY PROTECTION"
    )

    line()

    restart_replay_rejected = (
        False
    )

    try:

        restarted.dispatch()

    except RuntimeError:

        restart_replay_rejected = (
            True
        )

    validator.check(

        "Restart Replay Is Rejected",

        restart_replay_rejected,
    )

    validator.check(

        "Restart Does Not Duplicate Synthetic Dispatch",

        restarted.state.synthetic_dispatch_count
        == 1,
    )

    validator.check(

        "Restart Makes No Network Write",

        transport.network_write_count
        == 0,
    )


    # ==================================================================================================
    # TEST 9
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 9: TERMINAL IMMUTABILITY"
    )

    line()

    new_intent_rejected = (
        False
    )

    try:

        restarted.create_intent()

    except RuntimeError:

        new_intent_rejected = (
            True
        )

    validator.check(

        "Terminal Strategy Rejects New Intent",

        new_intent_rejected,
    )

    validator.check(

        "Terminal State Remains True",

        restarted.state.terminal
        is True,
    )

    validator.check(

        "Terminal Phase Remains COMPLETED",

        restarted.state.phase
        == "COMPLETED",
    )


    # ==================================================================================================
    # TEST 10
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 10: JOURNAL INTEGRITY"
    )

    line()

    records = (
        store.validate_journal()
    )

    validator.check(

        "Durable Journal Contains Records",

        len(
            records
        )
        >= 5,
    )

    validator.check(

        "Journal Sequence Matches State",

        len(
            records
        )
        == restarted.state.journal_sequence,
    )

    validator.check(

        "Journal Head Hash Matches State",

        bool(
            records
        )
        and records[
            -1
        ].get(
            "record_hash"
        )
        == restarted.state.last_journal_hash,
    )

    validator.check(

        "Every Journal Hash Has Correct Length",

        all(

            isinstance(
                record.get(
                    "record_hash"
                ),
                str,
            )

            and len(
                record[
                    "record_hash"
                ]
            )
            == 64

            for record
            in records
        ),
    )

    validator.check(

        "Durable Journal Remains Valid",

        bool(
            records
        ),
    )


    # ==================================================================================================
    # TEST 11
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 11: JOURNAL HASH CHAIN"
    )

    line()

    hash_chain_valid = (
        True
    )

    expected_previous = (
        ZERO_HASH
    )

    expected_sequence = (
        1
    )

    for record in records:

        if record.get(
            "previous_hash"
        ) != expected_previous:

            hash_chain_valid = (
                False
            )

            break

        if record.get(
            "sequence"
        ) != expected_sequence:

            hash_chain_valid = (
                False
            )

            break

        body = {

            "version":
                record.get(
                    "version"
                ),

            "symbol":
                record.get(
                    "symbol"
                ),

            "sequence":
                record.get(
                    "sequence"
                ),

            "event_type":
                record.get(
                    "event_type"
                ),

            "payload":
                record.get(
                    "payload"
                ),

            "previous_hash":
                record.get(
                    "previous_hash"
                ),
        }

        calculated = (
            sha256_obj(
                body
            )
        )

        if calculated != record.get(
            "record_hash"
        ):

            hash_chain_valid = (
                False
            )

            break

        expected_previous = (
            calculated
        )

        expected_sequence += (
            1
        )

    validator.check(

        "Journal Hash Chain Is Valid",

        hash_chain_valid,
    )


    # ==================================================================================================
    # TEST 12
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 12: FINAL SNAPSHOT INTEGRITY"
    )

    line()

    snapshot = (
        store.load()
    )

    validator.check(

        "Final Snapshot Version Is Correct",

        snapshot.version
        == VERSION,
    )

    validator.check(

        "Final Snapshot Symbol Is Correct",

        snapshot.symbol
        == SYMBOL,
    )

    validator.check(

        "Final Snapshot Integrity Is Valid",

        snapshot.as_dict()
        == restarted.state.as_dict(),
    )

    validator.check(

        "Final Snapshot Generation Is One",

        snapshot.generation
        == 1,
    )

    validator.check(

        "Final Snapshot Epoch Is One",

        snapshot.epoch
        == 1,
    )

    validator.check(

        "Final Snapshot Nonce Is One",

        snapshot.highest_nonce
        == 1,
    )

    validator.check(

        "Final Snapshot Contains One Consumed Intent",

        len(
            snapshot.consumed_intents
        )
        == 1,
    )

    validator.check(

        "Final Snapshot Contains One Durable Receipt",

        len(
            snapshot.durable_receipts
        )
        == 1,
    )


    # ==================================================================================================
    # TEST 13
    # ==================================================================================================

    line()

    log(
        f"{VERSION} TEST 13: FINAL SAFETY FIREBREAK"
    )

    line()

    validator.check(

        "Synthetic Transport Remains Enabled",

        SYNTHETIC_TRANSPORT_ONLY
        is True,
    )

    validator.check(

        "Network Writes Remain Disabled",

        NETWORK_WRITES_ENABLED
        is False,
    )

    validator.check(

        "Real Order Execution Remains Disabled",

        REAL_ORDERS_ENABLED
        is False,
    )

    validator.check(

        "Demo Order Execution Remains Disabled",

        DEMO_ORDERS_ENABLED
        is False,
    )

    validator.check(

        "Leverage Mutation Remains Disabled",

        LEVERAGE_MUTATION_ENABLED
        is False,
    )

    validator.check(

        "Margin Mutation Remains Disabled",

        MARGIN_MUTATION_ENABLED
        is False,
    )

    validator.check(

        "Position Mutation Remains Disabled",

        POSITION_MUTATION_ENABLED
        is False,
    )

    validator.check(

        "Strategy Remains Terminal",

        snapshot.terminal
        is True,
    )

    validator.check(

        "Strategy Network Write Count Is Zero",

        transport.network_write_count
        == 0,
    )


    # ==================================================================================================
    # R35B SUMMARY
    # ==================================================================================================

    line()

    log(
        f"{VERSION}: VALIDATION SUMMARY"
    )

    line()

    passed = sum(

        1

        for result
        in validator.results

        if result.passed
    )

    failed = sum(

        1

        for result
        in validator.results

        if not result.passed
    )

    log(
        f"{VERSION}: PASSED={passed}"
    )

    log(
        f"{VERSION}: FAILED={failed}"
    )

    if failed == 0:

        log(
            f"{VERSION}: RESULT="
            "✅ ALL VALIDATIONS PASSED"
        )

    else:

        log(
            f"{VERSION}: RESULT="
            "❌ VALIDATION FAILED"
        )

    line()

    return (
        validator.all_passed()
    )


# ==================================================================================================
# MAIN
# ==================================================================================================

def main(
) -> None:

    health_server = (
        start_health_server()
    )

    try:

        success = (
            run_validation()
        )

    except Exception as exc:

        line()

        log(
            f"{VERSION}: "
            f"ERROR="
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        line()

        raise

    if not success:

        raise SystemExit(
            1
        )


    # ==================================================================================================
    # PERSISTENT RENDER SERVICE
    # ==================================================================================================
    #
    # Set:
    #
    #     R35B_KEEP_ALIVE=0
    #
    # if you want the process to exit immediately after validation.
    #
    # Default is persistent because Render web services normally expect
    # the health server to remain available.
    # ==================================================================================================

    keep_alive = (

        os.getenv(
            "R35B_KEEP_ALIVE",
            "1",
        ).strip()

        != "0"
    )

    if keep_alive:

        heartbeat = (
            0
        )

        try:

            while True:

                heartbeat += (
                    1
                )

                log(
                    f"{VERSION}: "
                    f"HEARTBEAT "
                    f"{heartbeat}"
                )

                time.sleep(
                    30
                )

        except KeyboardInterrupt:

            pass

        finally:

            if health_server is not None:

                health_server.shutdown()


# ==================================================================================================
# ENTRY POINT
# ==================================================================================================

if __name__ == "__main__":

    main()
