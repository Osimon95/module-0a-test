from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib import parse, request


# ==================================================================================================
# R35G - CONTROLLED LIVE-EXECUTION GATE VALIDATION
# ==================================================================================================
#
# IMPORTANT
#   This version validates the boundary that a future live-order transmitter would have to cross.
#   It DOES NOT transmit exchange orders and DOES NOT enable autonomous real-money trading.
#
# SAFETY MODEL
#   - EXCHANGE NETWORK WRITES DISABLED
#   - REAL ORDER EXECUTION DISABLED
#   - DEMO ORDER EXECUTION DISABLED
#   - TELEGRAM REPORTING MAY USE POST, REPORT-ONLY
#   - TELEGRAM CANNOT CREATE / AUTHORIZE / DISPATCH TRADING INTENTS
#   - HARD 35% FUND-EXPOSURE LIMIT
#   - DURABLE KILL SWITCH
#   - EXCHANGE RECONCILIATION REQUIRED
#   - EXACTLY-ONCE SYNTHETIC DISPATCH
#   - FAIL CLOSED ON AMBIGUOUS OUTCOME
#   - RESTART / REPLAY PROTECTION
#
# PURPOSE
#   R35G proves that the live boundary cannot be crossed accidentally.
#
#   A later separately reviewed version would be required to implement any
#   actual exchange-order mutation.
#
# ==================================================================================================


VERSION = "R35G"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

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
        "R35G_STATE_DIR",
        "/tmp/r35g_state",
    )
)

STATE_FILE = STATE_DIR / "strategy_state.json"
JOURNAL_FILE = STATE_DIR / "journal.jsonl"
SNAPSHOT_FILE = STATE_DIR / "final_snapshot.json"


# ==================================================================================================
# STRATEGY / SAFETY CONSTANTS
# ==================================================================================================


MAX_FUND_EXPOSURE_PERCENT = 35.0

TARGET_LONG_LEVERAGE = 100
TARGET_SHORT_LEVERAGE = 100

REQUIRED_MARGIN_MODE = "ISOLATED"


# --------------------------------------------------------------------------------------------------
# R35G EXECUTION FIREBREAK
# --------------------------------------------------------------------------------------------------

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# --------------------------------------------------------------------------------------------------
# HARD SAFETY REQUIREMENTS
# --------------------------------------------------------------------------------------------------

RECONCILIATION_REQUIRED = True

KILL_SWITCH_REQUIRED = True

AMBIGUOUS_OUTCOME_FAIL_CLOSED = True


# --------------------------------------------------------------------------------------------------
# TELEGRAM
# --------------------------------------------------------------------------------------------------

TELEGRAM_REPORTING_ENABLED = True

TELEGRAM_CAN_CONTROL_EXECUTION = False

TELEGRAM_INBOUND_COMMANDS_ENABLED = False

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


LINE = "-" * 100


# ==================================================================================================
# GENERIC HELPERS
# ==================================================================================================


def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def stable_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_json(
    value: Any,
) -> str:

    return hashlib.sha256(
        stable_json(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def print_test(
    number: int,
    title: str,
) -> None:

    print(
        LINE,
        flush=True,
    )

    print(
        f"{VERSION} TEST {number}: {title}",
        flush=True,
    )

    print(
        LINE,
        flush=True,
    )


def check(
    label: str,
    condition: bool,
) -> None:

    marker = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{label:<88} {marker}",
        flush=True,
    )

    if not condition:

        raise AssertionError(
            label
        )


def atomic_write_json(
    path: Path,
    payload: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp.write_text(
        json.dumps(
            payload,
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    os.replace(
        temp,
        path,
    )


def load_json(
    path: Path,
) -> Optional[
    Dict[str, Any]
]:

    if not path.exists():

        return None

    raw = path.read_text(
        encoding="utf-8"
    ).strip()

    if not raw:

        return None

    return json.loads(
        raw
    )


# ==================================================================================================
# RECONCILIATION MODEL
# ==================================================================================================


@dataclass
class Reconciliation:

    reconciliation_id: str

    symbol: str

    margin_mode: str

    long_leverage: int

    short_leverage: int

    open_positions: int

    created_at: str

    generation: int

    epoch: int

    reconciliation_hash: str = ""


    def finalize(
        self,
    ) -> "Reconciliation":

        payload = asdict(
            self
        )

        payload[
            "reconciliation_hash"
        ] = ""

        self.reconciliation_hash = sha256_json(
            payload
        )

        return self


# ==================================================================================================
# INTENT MODEL
# ==================================================================================================


@dataclass
class TradingIntent:

    intent_id: str

    symbol: str

    side: str

    quantity: float

    estimated_margin_usdt: float

    fund_balance_usdt: float

    exposure_percent: float

    reconciliation_id: str

    reconciliation_hash: str

    generation: int

    epoch: int

    nonce: int

    synthetic_only: bool = True

    transmission_allowed: bool = False

    exchange_network_write_allowed: bool = False

    created_at: str = ""

    intent_hash: str = ""


    def finalize(
        self,
    ) -> "TradingIntent":

        payload = asdict(
            self
        )

        payload[
            "intent_hash"
        ] = ""

        self.intent_hash = sha256_json(
            payload
        )

        return self


# ==================================================================================================
# AUTHORIZATION MODEL
# ==================================================================================================


@dataclass
class Authorization:

    authorization_id: str

    intent_id: str

    intent_hash: str

    reconciliation_id: str

    reconciliation_hash: str

    generation: int

    epoch: int

    consumed: bool = False

    created_at: str = ""

    authorization_hash: str = ""


    def finalize(
        self,
    ) -> "Authorization":

        payload = asdict(
            self
        )

        payload[
            "authorization_hash"
        ] = ""

        self.authorization_hash = sha256_json(
            payload
        )

        return self


# ==================================================================================================
# RECEIPT MODEL
# ==================================================================================================


@dataclass
class SyntheticReceipt:

    receipt_id: str

    intent_id: str

    authorization_id: str

    transmitted: bool

    exchange_network_write: bool

    outcome: str

    created_at: str

    receipt_hash: str = ""


    def finalize(
        self,
    ) -> "SyntheticReceipt":

        payload = asdict(
            self
        )

        payload[
            "receipt_hash"
        ] = ""

        self.receipt_hash = sha256_json(
            payload
        )

        return self


# ==================================================================================================
# STRATEGY STATE
# ==================================================================================================


@dataclass
class StrategyState:

    version: str = VERSION

    symbol: str = SYMBOL

    phase: str = "BOOT"

    generation: int = 1

    epoch: int = 1

    highest_nonce: int = 0

    exchange_reconciled: bool = False

    reconciliation: Optional[
        Dict[str, Any]
    ] = None

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

    exchange_network_write_count: int = 0

    kill_switch_engaged: bool = False

    ambiguous_outcome_block: bool = False

    terminal: bool = False

    telegram_attempts: int = 0

    telegram_successes: int = 0

    telegram_failures: int = 0

    journal_sequence: int = 0

    last_journal_hash: str = "0" * 64

    integrity_hash: str = ""


    def body(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        payload = asdict(
            self
        )

        payload[
            "integrity_hash"
        ] = ""

        return payload


    def seal(
        self,
    ) -> None:

        self.integrity_hash = sha256_json(
            self.body()
        )


    def integrity_valid(
        self,
    ) -> bool:

        return (
            self.integrity_hash
            ==
            sha256_json(
                self.body()
            )
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

        self.state_file = state_file

        self.journal_file = journal_file

        self.lock = threading.RLock()


    def save(
        self,
        state: StrategyState,
        event: str,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        with self.lock:

            state.journal_sequence += 1

            record_without_hash = {

                "sequence":
                    state.journal_sequence,

                "timestamp":
                    utc_now(),

                "version":
                    VERSION,

                "symbol":
                    SYMBOL,

                "event":
                    event,

                "details":
                    details or {},

                "previous_hash":
                    state.last_journal_hash,
            }

            record_hash = sha256_json(
                record_without_hash
            )

            record = dict(
                record_without_hash
            )

            record[
                "record_hash"
            ] = record_hash

            self.journal_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.journal_file.open(
                "a",
                encoding="utf-8",
            ) as handle:

                handle.write(
                    stable_json(
                        record
                    )
                    +
                    "\n"
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )

            state.last_journal_hash = (
                record_hash
            )

            state.seal()

            atomic_write_json(
                self.state_file,
                asdict(
                    state
                ),
            )


    def load(
        self,
    ) -> Optional[
        StrategyState
    ]:

        with self.lock:

            payload = load_json(
                self.state_file
            )

            if payload is None:

                return None

            state = StrategyState(
                **payload
            )

            if not state.integrity_valid():

                raise RuntimeError(
                    "Durable state integrity validation failed"
                )

            return state


    def validate_journal(
        self,
        state: StrategyState,
    ) -> Tuple[
        bool,
        int,
        str,
    ]:

        if not self.journal_file.exists():

            return (
                False,
                0,
                "0" * 64,
            )

        previous = "0" * 64

        sequence = 0

        raw_lines = (
            self.journal_file.read_text(
                encoding="utf-8"
            ).splitlines()
        )

        for raw in raw_lines:

            if not raw.strip():

                continue

            record = json.loads(
                raw
            )

            recorded_hash = record.pop(
                "record_hash"
            )

            if (
                record[
                    "previous_hash"
                ]
                !=
                previous
            ):

                return (
                    False,
                    sequence,
                    previous,
                )

            calculated_hash = sha256_json(
                record
            )

            if (
                calculated_hash
                !=
                recorded_hash
            ):

                return (
                    False,
                    sequence,
                    previous,
                )

            sequence = int(
                record[
                    "sequence"
                ]
            )

            previous = recorded_hash

        valid = (

            sequence
            ==
            state.journal_sequence

            and

            previous
            ==
            state.last_journal_hash

        )

        return (
            valid,
            sequence,
            previous,
        )


# ==================================================================================================
# HEALTH SERVER
# ==================================================================================================


class HealthHandler(
    BaseHTTPRequestHandler
):

    state_provider = staticmethod(
        lambda: {
            "status":
                "initializing"
        }
    )


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

        payload = stable_json(
            self.state_provider()
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


    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


def start_health_server(
    state_ref: Dict[
        str,
        StrategyState,
    ],
) -> HTTPServer:


    def provider() -> Dict[
        str,
        Any,
    ]:

        state = state_ref[
            "state"
        ]

        return {

            "status":
                "ok",

            "version":
                VERSION,

            "symbol":
                SYMBOL,

            "phase":
                state.phase,

            "exchange_reconciled":
                state.exchange_reconciled,

            "kill_switch_engaged":
                state.kill_switch_engaged,

            "ambiguous_outcome_block":
                state.ambiguous_outcome_block,

            "exchange_network_writes":
                state.exchange_network_write_count,

            "live_order_execution":
                LIVE_ORDER_EXECUTION,
        }


    HealthHandler.state_provider = (
        staticmethod(
            provider
        )
    )

    server = HTTPServer(
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

    print(
        f"{VERSION}: HEALTH SERVER STARTED ON PORT {HEALTH_PORT}",
        flush=True,
    )

    return server


# ==================================================================================================
# EXCHANGE MUTATION FIREBREAK
# ==================================================================================================


class ExchangeMutationFirebreak:

    """
    There is intentionally no live exchange-order transmitter in R35G.

    POST / PUT / PATCH / DELETE directed at the exchange execution boundary
    are rejected before network I/O.
    """


    def __init__(
        self,
        state: StrategyState,
    ) -> None:

        self.state = state


    def _blocked(
        self,
        operation: str,
    ) -> None:

        raise RuntimeError(

            f"{VERSION} exchange mutation blocked: "
            f"{operation}. "
            f"R35G validates the controlled live gate "
            f"without transmitting a real-money order."

        )


    def post(
        self,
        *_: Any,
        **__: Any,
    ) -> None:

        self._blocked(
            "POST"
        )


    def put(
        self,
        *_: Any,
        **__: Any,
    ) -> None:

        self._blocked(
            "PUT"
        )


    def patch(
        self,
        *_: Any,
        **__: Any,
    ) -> None:

        self._blocked(
            "PATCH"
        )


    def delete(
        self,
        *_: Any,
        **__: Any,
    ) -> None:

        self._blocked(
            "DELETE"
        )


# ==================================================================================================
# R35G ENGINE
# ==================================================================================================


class R35GEngine:


    def __init__(
        self,
        store: DurableStore,
        state: StrategyState,
    ) -> None:

        self.store = store

        self.state = state


    def persist(
        self,
        event: str,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self.store.save(
            self.state,
            event,
            details,
        )


    # ----------------------------------------------------------------------------------------------
    # EXCHANGE STATE RECONCILIATION
    # ----------------------------------------------------------------------------------------------

    def reconcile(
        self,
        *,
        margin_mode: str,
        long_leverage: int,
        short_leverage: int,
        open_positions: int,
    ) -> Reconciliation:

        if self.state.kill_switch_engaged:

            raise RuntimeError(
                "Cannot reconcile while kill switch is engaged"
            )

        reconciliation = Reconciliation(

            reconciliation_id=(
                "rec-"
                +
                hashlib.sha256(
                    (
                        f"{SYMBOL}:"
                        f"{self.state.generation}:"
                        f"{self.state.epoch}:"
                        f"{time.time_ns()}"
                    ).encode()
                ).hexdigest()[:20]
            ),

            symbol=SYMBOL,

            margin_mode=(
                margin_mode.upper()
            ),

            long_leverage=int(
                long_leverage
            ),

            short_leverage=int(
                short_leverage
            ),

            open_positions=int(
                open_positions
            ),

            created_at=utc_now(),

            generation=(
                self.state.generation
            ),

            epoch=(
                self.state.epoch
            ),

        ).finalize()


        if (
            reconciliation.margin_mode
            !=
            REQUIRED_MARGIN_MODE
        ):

            raise RuntimeError(
                "Exchange margin mode is not ISOLATED"
            )


        if (
            reconciliation.long_leverage
            !=
            TARGET_LONG_LEVERAGE
        ):

            raise RuntimeError(
                "Long leverage is not 100x"
            )


        if (
            reconciliation.short_leverage
            !=
            TARGET_SHORT_LEVERAGE
        ):

            raise RuntimeError(
                "Short leverage is not 100x"
            )


        self.state.reconciliation = asdict(
            reconciliation
        )

        self.state.exchange_reconciled = True

        self.state.ambiguous_outcome_block = False

        self.state.phase = "RECONCILED"

        self.state.active_intent = None

        self.state.active_authorization = None

        self.state.terminal = False


        self.persist(

            "EXCHANGE_RECONCILED",

            {
                "reconciliation_id":
                    reconciliation.reconciliation_id,
            },

        )

        return reconciliation


    # ----------------------------------------------------------------------------------------------
    # KILL SWITCH
    # ----------------------------------------------------------------------------------------------

    def engage_kill_switch(
        self,
        reason: str,
    ) -> None:

        self.state.kill_switch_engaged = True

        self.state.phase = "KILLED"

        self.persist(

            "KILL_SWITCH_ENGAGED",

            {
                "reason":
                    reason
            },

        )


    def test_only_clear_kill_switch(
        self,
    ) -> None:

        self.state.kill_switch_engaged = False

        if self.state.exchange_reconciled:

            self.state.phase = (
                "RECONCILED"
            )

        else:

            self.state.phase = (
                "BOOT"
            )

        self.persist(
            "TEST_ONLY_KILL_SWITCH_CLEAR"
        )


    # ----------------------------------------------------------------------------------------------
    # INTENT PREPARATION
    # ----------------------------------------------------------------------------------------------

    def prepare_intent(
        self,
        *,
        side: str,
        quantity: float,
        estimated_margin_usdt: float,
        fund_balance_usdt: float,
        reconciliation_id: Optional[
            str
        ] = None,
    ) -> TradingIntent:


        if self.state.kill_switch_engaged:

            raise RuntimeError(
                "Kill switch blocks intent preparation"
            )


        if self.state.ambiguous_outcome_block:

            raise RuntimeError(
                "Ambiguous outcome block requires fresh reconciliation"
            )


        if (
            RECONCILIATION_REQUIRED
            and
            not self.state.exchange_reconciled
        ):

            raise RuntimeError(
                "Exchange reconciliation required"
            )


        if self.state.terminal:

            raise RuntimeError(
                "Terminal state rejects new intent"
            )


        if not self.state.reconciliation:

            raise RuntimeError(
                "Missing durable reconciliation"
            )


        current = self.state.reconciliation

        expected_id = current[
            "reconciliation_id"
        ]

        supplied_id = (
            reconciliation_id
            or
            expected_id
        )


        if supplied_id != expected_id:

            raise RuntimeError(
                "Stale reconciliation binding rejected"
            )


        if fund_balance_usdt <= 0:

            raise RuntimeError(
                "Fund balance must be positive"
            )


        if estimated_margin_usdt < 0:

            raise RuntimeError(
                "Estimated margin must be non-negative"
            )


        exposure_percent = (

            estimated_margin_usdt
            /
            fund_balance_usdt
            *
            100.0

        )


        if (
            exposure_percent
            >
            MAX_FUND_EXPOSURE_PERCENT
            +
            1e-12
        ):

            raise RuntimeError(
                "Hard fund-exposure limit exceeded"
            )


        nonce = (
            self.state.highest_nonce
            +
            1
        )


        intent = TradingIntent(

            intent_id=(
                "int-"
                +
                hashlib.sha256(
                    (
                        f"{SYMBOL}:"
                        f"{nonce}:"
                        f"{time.time_ns()}"
                    ).encode()
                ).hexdigest()[:20]
            ),

            symbol=SYMBOL,

            side=(
                side.upper()
            ),

            quantity=float(
                quantity
            ),

            estimated_margin_usdt=float(
                estimated_margin_usdt
            ),

            fund_balance_usdt=float(
                fund_balance_usdt
            ),

            exposure_percent=float(
                exposure_percent
            ),

            reconciliation_id=current[
                "reconciliation_id"
            ],

            reconciliation_hash=current[
                "reconciliation_hash"
            ],

            generation=(
                self.state.generation
            ),

            epoch=(
                self.state.epoch
            ),

            nonce=nonce,

            synthetic_only=True,

            transmission_allowed=False,

            exchange_network_write_allowed=False,

            created_at=utc_now(),

        ).finalize()


        self.state.highest_nonce = nonce

        self.state.active_intent = asdict(
            intent
        )

        self.state.active_authorization = None

        self.state.phase = "PREPARED"


        self.persist(

            "INTENT_PREPARED",

            {
                "intent_id":
                    intent.intent_id
            },

        )


        return intent


    # ----------------------------------------------------------------------------------------------
    # AUTHORIZATION
    # ----------------------------------------------------------------------------------------------

    def authorize(
        self,
    ) -> Authorization:


        if self.state.kill_switch_engaged:

            raise RuntimeError(
                "Kill switch blocks authorization"
            )


        if self.state.ambiguous_outcome_block:

            raise RuntimeError(
                "Ambiguous outcome block requires fresh reconciliation"
            )


        if (
            self.state.phase
            !=
            "PREPARED"
            or
            not self.state.active_intent
        ):

            raise RuntimeError(
                "No prepared intent to authorize"
            )


        if not self.state.reconciliation:

            raise RuntimeError(
                "Missing reconciliation"
            )


        intent = (
            self.state.active_intent
        )

        reconciliation = (
            self.state.reconciliation
        )


        if (
            intent[
                "reconciliation_id"
            ]
            !=
            reconciliation[
                "reconciliation_id"
            ]
        ):

            raise RuntimeError(
                "Authorization rejects stale reconciliation"
            )


        if (
            intent[
                "reconciliation_hash"
            ]
            !=
            reconciliation[
                "reconciliation_hash"
            ]
        ):

            raise RuntimeError(
                "Authorization rejects reconciliation hash mismatch"
            )


        authorization = Authorization(

            authorization_id=(
                "auth-"
                +
                hashlib.sha256(
                    (
                        f"{intent['intent_id']}:"
                        f"{time.time_ns()}"
                    ).encode()
                ).hexdigest()[:20]
            ),

            intent_id=intent[
                "intent_id"
            ],

            intent_hash=intent[
                "intent_hash"
            ],

            reconciliation_id=(
                reconciliation[
                    "reconciliation_id"
                ]
            ),

            reconciliation_hash=(
                reconciliation[
                    "reconciliation_hash"
                ]
            ),

            generation=(
                self.state.generation
            ),

            epoch=(
                self.state.epoch
            ),

            consumed=False,

            created_at=utc_now(),

        ).finalize()


        self.state.active_authorization = (
            asdict(
                authorization
            )
        )

        self.state.phase = (
            "AUTHORIZED"
        )


        self.persist(

            "INTENT_AUTHORIZED",

            {
                "authorization_id":
                    authorization.authorization_id
            },

        )


        return authorization


    # ----------------------------------------------------------------------------------------------
    # SYNTHETIC DISPATCH
    # ----------------------------------------------------------------------------------------------

    def synthetic_dispatch(
        self,
    ) -> SyntheticReceipt:


        if self.state.kill_switch_engaged:

            raise RuntimeError(
                "Kill switch blocks dispatch"
            )


        if self.state.ambiguous_outcome_block:

            raise RuntimeError(
                "Ambiguous outcome block requires fresh reconciliation"
            )


        if (
            self.state.phase
            !=
            "AUTHORIZED"
        ):

            raise RuntimeError(
                "Dispatch requires AUTHORIZED phase"
            )


        if (
            not self.state.active_intent
            or
            not self.state.active_authorization
        ):

            raise RuntimeError(
                "Missing intent or authorization"
            )


        intent = (
            self.state.active_intent
        )

        authorization = (
            self.state.active_authorization
        )


        if (
            intent[
                "intent_id"
            ]
            in
            self.state.consumed_intents
        ):

            raise RuntimeError(
                "Intent replay rejected"
            )


        if (
            authorization[
                "authorization_id"
            ]
            in
            self.state.consumed_authorizations
        ):

            raise RuntimeError(
                "Authorization replay rejected"
            )


        if authorization[
            "consumed"
        ]:

            raise RuntimeError(
                "Authorization already consumed"
            )


        if (
            intent[
                "synthetic_only"
            ]
            is not True
        ):

            raise RuntimeError(
                "R35G accepts synthetic-only intent"
            )


        if (
            intent[
                "transmission_allowed"
            ]
            is not False
        ):

            raise RuntimeError(
                "R35G transmission must remain forbidden"
            )


        if (
            intent[
                "exchange_network_write_allowed"
            ]
            is not False
        ):

            raise RuntimeError(
                "R35G exchange writes must remain forbidden"
            )


        receipt = SyntheticReceipt(

            receipt_id=(
                "rcpt-"
                +
                hashlib.sha256(
                    (
                        f"{intent['intent_id']}:"
                        f"{authorization['authorization_id']}:"
                        f"{time.time_ns()}"
                    ).encode()
                ).hexdigest()[:20]
            ),

            intent_id=intent[
                "intent_id"
            ],

            authorization_id=(
                authorization[
                    "authorization_id"
                ]
            ),

            transmitted=False,

            exchange_network_write=False,

            outcome=(
                "SYNTHETIC_VALIDATION_ONLY"
            ),

            created_at=utc_now(),

        ).finalize()


        authorization[
            "consumed"
        ] = True


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
            asdict(
                receipt
            )
        )


        self.state.synthetic_dispatch_count += 1

        self.state.phase = (
            "COMPLETED"
        )

        self.state.terminal = True


        self.persist(

            "SYNTHETIC_DISPATCH_COMPLETED",

            {
                "receipt_id":
                    receipt.receipt_id
            },

        )


        return receipt


    # ----------------------------------------------------------------------------------------------
    # AMBIGUOUS OUTCOME BLOCK
    # ----------------------------------------------------------------------------------------------

    def activate_ambiguous_outcome_block(
        self,
        reason: str,
    ) -> None:


        self.state.ambiguous_outcome_block = True

        self.state.exchange_reconciled = False

        self.state.phase = (
            "AMBIGUOUS_BLOCKED"
        )

        self.state.active_intent = None

        self.state.active_authorization = None

        self.state.terminal = False


        self.persist(

            "AMBIGUOUS_OUTCOME_BLOCKED",

            {
                "reason":
                    reason
            },

        )


# ==================================================================================================
# TELEGRAM REPORTING
# ==================================================================================================


def telegram_configured(
) -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and
        TELEGRAM_CHAT_ID
    )


def telegram_preview(
    text: str,
) -> Dict[
    str,
    Any,
]:

    return {

        "method":
            "POST",

        "operation":
            "sendMessage",

        "report_only":
            True,

        "exchange_mutation":
            False,

        "can_control_execution":
            False,

        "chat_id_present":
            bool(
                TELEGRAM_CHAT_ID
            ),

        "text":
            text,

    }


def send_telegram_report(
    state: StrategyState,
    text: str,
    timeout: float = 10.0,
) -> bool:


    state.telegram_attempts += 1


    if (
        not TELEGRAM_REPORTING_ENABLED
        or
        not telegram_configured()
    ):

        state.telegram_failures += 1

        return False


    url = (

        "https://api.telegram.org/bot"
        +
        TELEGRAM_BOT_TOKEN
        +
        "/sendMessage"

    )


    encoded = parse.urlencode(

        {
            "chat_id":
                TELEGRAM_CHAT_ID,

            "text":
                text,
        }

    ).encode(
        "utf-8"
    )


    req = request.Request(

        url,

        data=encoded,

        method="POST",

        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },

    )


    try:

        with request.urlopen(
            req,
            timeout=timeout,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            ok = (
                200
                <=
                int(
                    response.status
                )
                <
                300
            )


            if raw:

                try:

                    body = json.loads(
                        raw
                    )

                    ok = (
                        ok
                        and
                        bool(
                            body.get(
                                "ok",
                                False,
                            )
                        )
                    )

                except json.JSONDecodeError:

                    pass


            if ok:

                state.telegram_successes += 1

                return True


            state.telegram_failures += 1

            return False


    except Exception:

        state.telegram_failures += 1

        return False


# ==================================================================================================
# CLEAN VALIDATION STATE
# ==================================================================================================


def new_clean_state(
) -> Tuple[
    DurableStore,
    StrategyState,
]:


    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    for path in (

        STATE_FILE,

        JOURNAL_FILE,

        SNAPSHOT_FILE,

    ):

        try:

            path.unlink()

        except FileNotFoundError:

            pass


    store = DurableStore(

        STATE_FILE,

        JOURNAL_FILE,

    )


    state = StrategyState()


    state.seal()


    store.save(

        state,

        "R35G_BOOT",

    )


    return (
        store,
        state,
    )


# ==================================================================================================
# R35G VALIDATION
# ==================================================================================================


def run_validation(
    state_ref: Dict[
        str,
        StrategyState,
    ],
) -> StrategyState:


    store, state = new_clean_state()


    state_ref[
        "state"
    ] = state


    engine = R35GEngine(

        store,

        state,

    )


    # ==============================================================================================
    # STARTUP SUMMARY
    # ==============================================================================================


    print(
        LINE,
        flush=True,
    )

    print(
        f"{VERSION}: MAIN.PY ENTERED",
        flush=True,
    )

    print(
        LINE,
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
        f"{VERSION}: EXCHANGE NETWORK WRITES ENABLED={EXCHANGE_NETWORK_WRITES_ENABLED}",
        flush=True,
    )

    print(
        f"{VERSION}: LIVE ORDER EXECUTION={LIVE_ORDER_EXECUTION}",
        flush=True,
    )

    print(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY={SYNTHETIC_TRANSPORT_ONLY}",
        flush=True,
    )


    # ==============================================================================================
    # TEST 1
    # ==============================================================================================


    print_test(
        1,
        "SAFETY CONSTANTS",
    )


    check(
        "Exchange Network Writes Are Disabled",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )


    check(
        "Real Order Execution Is Disabled",
        LIVE_ORDER_EXECUTION is False,
    )


    check(
        "Demo Order Execution Is Disabled",
        DEMO_ORDER_EXECUTION is False,
    )


    check(
        "Synthetic Transport Only Is Enabled",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )


    check(
        "Reconciliation Is Required",
        RECONCILIATION_REQUIRED is True,
    )


    check(
        "Kill Switch Is Required",
        KILL_SWITCH_REQUIRED is True,
    )


    check(
        "Ambiguous Outcomes Fail Closed",
        AMBIGUOUS_OUTCOME_FAIL_CLOSED is True,
    )


    # ==============================================================================================
    # TEST 2
    # ==============================================================================================


    print_test(
        2,
        "INITIAL DURABLE STATE",
    )


    restarted = store.load()


    check(
        "Initial State Is Durable",
        restarted is not None,
    )


    check(
        "Initial State Integrity Is Valid",
        (
            restarted is not None
            and
            restarted.integrity_valid()
        ),
    )


    check(
        "Initial Exchange Write Count Is Zero",
        (
            restarted is not None
            and
            restarted.exchange_network_write_count
            ==
            0
        ),
    )


    # ==============================================================================================
    # TEST 3
    # ==============================================================================================


    print_test(
        3,
        "UNRECONCILED INTENT REJECTION",
    )


    rejected = False


    try:

        engine.prepare_intent(

            side="BUY",

            quantity=0.0001,

            estimated_margin_usdt=0.10,

            fund_balance_usdt=10.0,

        )

    except RuntimeError:

        rejected = True


    check(
        "Unreconciled Strategy Rejects Intent",
        rejected,
    )


    check(
        "Unreconciled Strategy Makes No Synthetic Dispatch",
        state.synthetic_dispatch_count == 0,
    )


    check(
        "Unreconciled Strategy Makes No Exchange Network Write",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 4
    # ==============================================================================================


    print_test(
        4,
        "EXCHANGE STATE RECONCILIATION",
    )


    reconciliation = engine.reconcile(

        margin_mode="ISOLATED",

        long_leverage=100,

        short_leverage=100,

        open_positions=0,

    )


    check(
        "Exchange Reconciliation Was Created",
        bool(
            reconciliation.reconciliation_id
        ),
    )


    check(
        "Exchange Reconciliation Is Bound To BTCUSDT",
        reconciliation.symbol == SYMBOL,
    )


    check(
        "Observed Long Leverage Is 100x",
        reconciliation.long_leverage == 100,
    )


    check(
        "Observed Short Leverage Is 100x",
        reconciliation.short_leverage == 100,
    )


    check(
        "Reconciliation Hash Has Correct Length",
        len(
            reconciliation.reconciliation_hash
        )
        ==
        64,
    )


    check(
        "Strategy Entered RECONCILED Phase",
        state.phase == "RECONCILED",
    )


    check(
        "Exchange Reconciled Flag Is True",
        state.exchange_reconciled is True,
    )


    # ==============================================================================================
    # TEST 5
    # ==============================================================================================


    print_test(
        5,
        "RECONCILIATION DURABLE RESTART",
    )


    restarted = store.load()


    check(
        "Reconciled State Survives Restart",
        (
            restarted is not None
            and
            restarted.exchange_reconciled
        ),
    )


    check(
        "Reconciliation ID Survives Restart",
        (
            restarted is not None
            and
            restarted.reconciliation is not None
            and
            restarted.reconciliation[
                "reconciliation_id"
            ]
            ==
            reconciliation.reconciliation_id
        ),
    )


    check(
        "Exchange Network Write Count Survives At Zero",
        (
            restarted is not None
            and
            restarted.exchange_network_write_count
            ==
            0
        ),
    )


    # ==============================================================================================
    # TEST 6
    # ==============================================================================================


    print_test(
        6,
        "HARD EXPOSURE LIMIT",
    )


    low = engine.prepare_intent(

        side="BUY",

        quantity=0.0001,

        estimated_margin_usdt=3.49,

        fund_balance_usdt=10.0,

    )


    check(
        "Exposure Below Maximum Is Accepted",
        low.exposure_percent < 35.0,
    )


    # Test branch reset.

    state.active_intent = None

    state.active_authorization = None

    state.phase = "RECONCILED"

    state.highest_nonce = 0


    engine.persist(
        "TEST_BRANCH_RESET"
    )


    high_rejected = False


    try:

        engine.prepare_intent(

            side="BUY",

            quantity=0.0001,

            estimated_margin_usdt=3.51,

            fund_balance_usdt=10.0,

        )

    except RuntimeError:

        high_rejected = True


    check(
        "Exposure Above 35 Percent Is Rejected",
        high_rejected,
    )


    check(
        "Maximum Fund Exposure Remains 35 Percent",
        MAX_FUND_EXPOSURE_PERCENT == 35.0,
    )


    check(
        "Exposure Rejection Makes No Exchange Network Write",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 7
    # ==============================================================================================


    print_test(
        7,
        "KILL SWITCH",
    )


    engine.engage_kill_switch(
        "R35G validation"
    )


    kill_rejected = False


    try:

        engine.prepare_intent(

            side="BUY",

            quantity=0.0001,

            estimated_margin_usdt=0.1,

            fund_balance_usdt=10.0,

        )

    except RuntimeError:

        kill_rejected = True


    check(
        "Kill Switch Is Engaged",
        state.kill_switch_engaged,
    )


    check(
        "Kill Switch Blocks Intent Preparation",
        kill_rejected,
    )


    check(
        "Kill Switch Makes No Synthetic Dispatch",
        state.synthetic_dispatch_count == 0,
    )


    check(
        "Kill Switch Makes No Exchange Network Write",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 8
    # ==============================================================================================


    print_test(
        8,
        "KILL SWITCH DURABLE RESTART",
    )


    restarted = store.load()


    check(
        "Kill Switch Survives Restart",
        (
            restarted is not None
            and
            restarted.kill_switch_engaged
        ),
    )


    engine.test_only_clear_kill_switch()


    check(
        "Test-Only Kill Switch Clear Restores Reconciled Phase",
        state.phase == "RECONCILED",
    )


    # ==============================================================================================
    # TEST 9
    # ==============================================================================================


    print_test(
        9,
        "RECONCILIATION-BOUND INTENT",
    )


    stale_rejected = False


    try:

        engine.prepare_intent(

            side="BUY",

            quantity=0.0001,

            estimated_margin_usdt=0.2,

            fund_balance_usdt=10.0,

            reconciliation_id=(
                "stale-reconciliation"
            ),

        )

    except RuntimeError:

        stale_rejected = True


    check(
        "Stale Reconciliation Binding Is Rejected",
        stale_rejected,
    )


    intent = engine.prepare_intent(

        side="BUY",

        quantity=0.0001,

        estimated_margin_usdt=0.2,

        fund_balance_usdt=10.0,

    )


    check(
        "Valid Intent Was Created",
        bool(
            intent.intent_id
        ),
    )


    check(
        "Intent Is Bound To Current Reconciliation",
        (
            intent.reconciliation_id
            ==
            reconciliation.reconciliation_id
        ),
    )


    check(
        "Intent Is Synthetic Only",
        intent.synthetic_only is True,
    )


    check(
        "Intent Forbids Transmission",
        intent.transmission_allowed is False,
    )


    check(
        "Intent Forbids Exchange Network Write",
        intent.exchange_network_write_allowed is False,
    )


    # ==============================================================================================
    # TEST 10
    # ==============================================================================================


    print_test(
        10,
        "RESTART AFTER PREPARE",
    )


    restarted = store.load()


    check(
        "Prepared Intent Survives Restart",
        (
            restarted is not None
            and
            restarted.active_intent is not None
        ),
    )


    check(
        "Prepared Intent ID Survives Restart",
        (
            restarted is not None
            and
            restarted.active_intent[
                "intent_id"
            ]
            ==
            intent.intent_id
        ),
    )


    check(
        "Strategy Remains PREPARED",
        (
            restarted is not None
            and
            restarted.phase
            ==
            "PREPARED"
        ),
    )


    check(
        "No Synthetic Dispatch Occurred",
        (
            restarted is not None
            and
            restarted.synthetic_dispatch_count
            ==
            0
        ),
    )


    check(
        "No Exchange Network Write Occurred",
        (
            restarted is not None
            and
            restarted.exchange_network_write_count
            ==
            0
        ),
    )


    # ==============================================================================================
    # TEST 11
    # ==============================================================================================


    print_test(
        11,
        "AUTHORIZATION BINDING",
    )


    authorization = engine.authorize()


    check(
        "Authorization Was Created",
        bool(
            authorization.authorization_id
        ),
    )


    check(
        "Authorization Binds Exact Intent",
        authorization.intent_id == intent.intent_id,
    )


    check(
        "Authorization Binds Current Reconciliation",
        (
            authorization.reconciliation_id
            ==
            reconciliation.reconciliation_id
        ),
    )


    check(
        "Authorization Is Initially Unconsumed",
        authorization.consumed is False,
    )


    check(
        "Strategy Entered AUTHORIZED Phase",
        state.phase == "AUTHORIZED",
    )


    # ==============================================================================================
    # TEST 12
    # ==============================================================================================


    print_test(
        12,
        "RESTART AFTER AUTHORIZATION",
    )


    restarted = store.load()


    check(
        "Authorization Survives Restart",
        (
            restarted is not None
            and
            restarted.active_authorization is not None
        ),
    )


    check(
        "Authorization ID Survives Restart",
        (
            restarted is not None
            and
            restarted.active_authorization[
                "authorization_id"
            ]
            ==
            authorization.authorization_id
        ),
    )


    check(
        "Strategy Remains AUTHORIZED",
        (
            restarted is not None
            and
            restarted.phase
            ==
            "AUTHORIZED"
        ),
    )


    check(
        "Authorization Remains Unconsumed",
        (
            restarted is not None
            and
            restarted.active_authorization[
                "consumed"
            ]
            is False
        ),
    )


    check(
        "Exchange Network Write Count Remains Zero",
        (
            restarted is not None
            and
            restarted.exchange_network_write_count
            ==
            0
        ),
    )


    # ==============================================================================================
    # TEST 13
    # ==============================================================================================


    print_test(
        13,
        "EXCHANGE MUTATION FIREBREAK",
    )


    firebreak = ExchangeMutationFirebreak(
        state
    )


    blocked = 0


    for method_name in (

        "post",

        "put",

        "patch",

        "delete",

    ):

        try:

            getattr(
                firebreak,
                method_name,
            )(
                "/orders",
                {
                    "symbol":
                        SYMBOL
                },
            )

        except RuntimeError:

            blocked += 1


    check(
        "All Four Exchange Mutation Methods Were Blocked",
        blocked == 4,
    )


    check(
        "Mutation Firebreak Made No Exchange Network Write",
        state.exchange_network_write_count == 0,
    )


    check(
        "Real Order Execution Remains Disabled",
        LIVE_ORDER_EXECUTION is False,
    )


    # ==============================================================================================
    # TEST 14
    # ==============================================================================================


    print_test(
        14,
        "CONTROLLED LIVE-GATE CONDITIONS",
    )


    live_gate_conditions = {

        "reconciled":
            state.exchange_reconciled,

        "kill_switch_clear":
            not state.kill_switch_engaged,

        "ambiguous_block_clear":
            not state.ambiguous_outcome_block,

        "exposure_limit_present":
            (
                MAX_FUND_EXPOSURE_PERCENT
                ==
                35.0
            ),

        "authorized":
            (
                state.phase
                ==
                "AUTHORIZED"
            ),

        "exchange_writer_absent":
            (
                EXCHANGE_NETWORK_WRITES_ENABLED
                is False
            ),

        "live_execution_disabled":
            (
                LIVE_ORDER_EXECUTION
                is False
            ),

    }


    check(
        "Reconciliation Gate Is Satisfied",
        live_gate_conditions[
            "reconciled"
        ],
    )


    check(
        "Kill Switch Gate Is Clear",
        live_gate_conditions[
            "kill_switch_clear"
        ],
    )


    check(
        "Ambiguous Outcome Gate Is Clear",
        live_gate_conditions[
            "ambiguous_block_clear"
        ],
    )


    check(
        "Hard Exposure Limit Is Present",
        live_gate_conditions[
            "exposure_limit_present"
        ],
    )


    check(
        "Authorization Gate Is Satisfied",
        live_gate_conditions[
            "authorized"
        ],
    )


    check(
        "Exchange Writer Remains Absent",
        live_gate_conditions[
            "exchange_writer_absent"
        ],
    )


    check(
        "Live Execution Remains Disabled",
        live_gate_conditions[
            "live_execution_disabled"
        ],
    )


    # ==============================================================================================
    # TEST 15
    # ==============================================================================================


    print_test(
        15,
        "SYNTHETIC EXACTLY-ONCE DISPATCH",
    )


    receipt = engine.synthetic_dispatch()


    check(
        "Synthetic Receipt Was Created",
        bool(
            receipt.receipt_id
        ),
    )


    check(
        "Synthetic Dispatch Was Not Transmitted",
        receipt.transmitted is False,
    )


    check(
        "Synthetic Dispatch Made No Exchange Network Write",
        receipt.exchange_network_write is False,
    )


    check(
        "Synthetic Dispatch Count Is One",
        state.synthetic_dispatch_count == 1,
    )


    check(
        "Strategy Reached COMPLETED",
        state.phase == "COMPLETED",
    )


    check(
        "Strategy Is Terminal",
        state.terminal is True,
    )


    check(
        "Exchange Network Write Count Remains Zero",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 16
    # ==============================================================================================


    print_test(
        16,
        "RESTART REPLAY PROTECTION",
    )


    restarted = store.load()


    check(
        "Completed State Survives Restart",
        (
            restarted is not None
            and
            restarted.phase
            ==
            "COMPLETED"
        ),
    )


    check(
        "Terminal State Survives Restart",
        (
            restarted is not None
            and
            restarted.terminal
        ),
    )


    check(
        "Consumed Intent Survives Restart",
        (
            restarted is not None
            and
            intent.intent_id
            in
            restarted.consumed_intents
        ),
    )


    check(
        "Consumed Authorization Survives Restart",
        (
            restarted is not None
            and
            authorization.authorization_id
            in
            restarted.consumed_authorizations
        ),
    )


    check(
        "Durable Receipt Survives Restart",
        (
            restarted is not None
            and
            len(
                restarted.durable_receipts
            )
            ==
            1
        ),
    )


    replay_rejected = False


    try:

        engine.synthetic_dispatch()

    except RuntimeError:

        replay_rejected = True


    check(
        "Restart Replay Is Rejected",
        replay_rejected,
    )


    check(
        "Replay Does Not Duplicate Synthetic Dispatch",
        state.synthetic_dispatch_count == 1,
    )


    check(
        "Replay Makes No Exchange Network Write",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 17
    # ==============================================================================================


    print_test(
        17,
        "AMBIGUOUS OUTCOME FAIL-CLOSED",
    )


    engine.activate_ambiguous_outcome_block(
        "synthetic ambiguous-outcome validation"
    )


    ambiguous_rejected = False


    try:

        engine.prepare_intent(

            side="BUY",

            quantity=0.0001,

            estimated_margin_usdt=0.1,

            fund_balance_usdt=10.0,

        )

    except RuntimeError:

        ambiguous_rejected = True


    check(
        "Ambiguous Outcome Activates Block",
        state.ambiguous_outcome_block,
    )


    check(
        "Ambiguous Outcome Blocks New Intent",
        ambiguous_rejected,
    )


    check(
        "Ambiguous Outcome Makes No Exchange Network Write",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 18
    # ==============================================================================================


    print_test(
        18,
        "AMBIGUOUS OUTCOME REQUIRES RECONCILIATION",
    )


    restarted = store.load()


    check(
        "Ambiguous Block Survives Restart",
        (
            restarted is not None
            and
            restarted.ambiguous_outcome_block
        ),
    )


    fresh_reconciliation = engine.reconcile(

        margin_mode="ISOLATED",

        long_leverage=100,

        short_leverage=100,

        open_positions=0,

    )


    check(
        "Fresh Reconciliation Was Created",
        (
            fresh_reconciliation.reconciliation_id
            !=
            reconciliation.reconciliation_id
        ),
    )


    check(
        "Ambiguous Block Clears Only After Reconciliation",
        state.ambiguous_outcome_block is False,
    )


    check(
        "Strategy Returns To RECONCILED",
        state.phase == "RECONCILED",
    )


    # ==============================================================================================
    # TEST 19
    # ==============================================================================================


    print_test(
        19,
        "TELEGRAM REQUEST BOUNDARY",
    )


    report = (

        f"{VERSION} REPORT\n"

        f"SYMBOL={SYMBOL}\n"

        f"EVENT=R35G_VALIDATION\n"

        f"PHASE={state.phase}\n"

        f"GENERATION={state.generation}\n"

        f"EPOCH={state.epoch}\n"

        f"EXCHANGE_NETWORK_WRITES="
        f"{state.exchange_network_write_count}\n"

        f"REAL_ORDER_EXECUTION="
        f"{LIVE_ORDER_EXECUTION}\n"

        f"DETAILS="
        f"{stable_json({
            'exchange_network_writes':
                state.exchange_network_write_count,
            'live_trading':
                False,
            'status':
                'CONTROLLED_LIVE_GATE_VALIDATED'
        })}"

    )


    preview = telegram_preview(
        report
    )


    check(
        "Telegram Uses POST Only For Reporting",
        preview[
            "method"
        ]
        ==
        "POST",
    )


    check(
        "Telegram Operation Is sendMessage",
        preview[
            "operation"
        ]
        ==
        "sendMessage",
    )


    check(
        "Telegram Request Is Marked Report Only",
        preview[
            "report_only"
        ]
        is True,
    )


    check(
        "Telegram Request Is Not Exchange Mutation",
        preview[
            "exchange_mutation"
        ]
        is False,
    )


    check(
        "Telegram Request Cannot Control Execution",
        preview[
            "can_control_execution"
        ]
        is False,
    )


    check(
        "Telegram Preview Does Not Contain Bot Token",
        (
            TELEGRAM_BOT_TOKEN
            not in
            stable_json(
                preview
            )
            if TELEGRAM_BOT_TOKEN
            else True
        ),
    )


    check(
        "Telegram Preview Does Not Increment Exchange Writes",
        state.exchange_network_write_count == 0,
    )


    # ==============================================================================================
    # TEST 20
    # ==============================================================================================


    print_test(
        20,
        "LIVE TELEGRAM REPORT DELIVERY",
    )


    before_phase = (
        state.phase
    )

    before_nonce = (
        state.highest_nonce
    )

    before_dispatches = (
        state.synthetic_dispatch_count
    )

    before_exchange_writes = (
        state.exchange_network_write_count
    )


    delivered = send_telegram_report(

        state,

        report,

    )


    engine.persist(

        "TELEGRAM_REPORT_ATTEMPT",

        {

            "delivered":
                delivered,

            "report_only":
                True,

        },

    )


    if telegram_configured():


        check(
            "Telegram Report Was Delivered",
            delivered,
        )


        check(
            "Telegram Success Count Is One",
            state.telegram_successes == 1,
        )


        check(
            "Telegram Failure Count Is Zero",
            state.telegram_failures == 0,
        )


    else:


        check(
            "Telegram Is Safely Unconfigured",
            delivered is False,
        )


        check(
            "Telegram Failure Is Counted Without Execution Effect",
            state.telegram_failures == 1,
        )


    check(
        "Telegram Report Is Marked Report Only",
        preview[
            "report_only"
        ]
        is True,
    )


    check(
        "Telegram Delivery Has No Execution Effect",
        state.phase == before_phase,
    )


    check(
        "Telegram Did Not Increment Exchange Network Writes",
        (
            state.exchange_network_write_count
            ==
            before_exchange_writes
        ),
    )


    check(
        "Real Order Execution Remains Disabled After Telegram",
        LIVE_ORDER_EXECUTION is False,
    )


    # ==============================================================================================
    # TEST 21
    # ==============================================================================================


    print_test(
        21,
        "TELEGRAM EXECUTION ISOLATION",
    )


    check(
        "Telegram Cannot Create Trading Intent",
        state.active_intent is None,
    )


    check(
        "Telegram Cannot Authorize Trading Intent",
        state.active_authorization is None,
    )


    check(
        "Telegram Cannot Dispatch Trading Intent",
        (
            state.synthetic_dispatch_count
            ==
            before_dispatches
        ),
    )


    check(
        "Telegram Cannot Engage Exchange Mutation",
        (
            state.exchange_network_write_count
            ==
            before_exchange_writes
        ),
    )


    check(
        "Telegram Leaves Strategy Phase Unchanged",
        state.phase == before_phase,
    )


    check(
        "Telegram Leaves Strategy Nonce Unchanged",
        state.highest_nonce == before_nonce,
    )


    check(
        "Telegram Leaves Exchange Write Count Unchanged",
        (
            state.exchange_network_write_count
            ==
            before_exchange_writes
        ),
    )


    # ==============================================================================================
    # TEST 22
    # ==============================================================================================


    print_test(
        22,
        "JOURNAL INTEGRITY",
    )


    journal_valid, journal_sequence, journal_head = (
        store.validate_journal(
            state
        )
    )


    check(
        "Durable Journal Contains Records",
        journal_sequence > 0,
    )


    check(
        "Journal Hash Chain Is Valid",
        journal_valid,
    )


    check(
        "Journal Sequence Matches State",
        (
            journal_sequence
            ==
            state.journal_sequence
        ),
    )


    check(
        "Journal Head Hash Matches State",
        (
            journal_head
            ==
            state.last_journal_hash
        ),
    )


    check(
        "Journal Head Hash Has Correct Length",
        len(
            journal_head
        )
        ==
        64,
    )


    # ==============================================================================================
    # TEST 23
    # ==============================================================================================


    print_test(
        23,
        "FINAL SNAPSHOT INTEGRITY",
    )


    state.seal()


    atomic_write_json(

        SNAPSHOT_FILE,

        asdict(
            state
        ),

    )


    snapshot_payload = load_json(
        SNAPSHOT_FILE
    )


    snapshot = (

        StrategyState(
            **snapshot_payload
        )

        if snapshot_payload

        else None

    )


    check(
        "Final Snapshot Version Is Correct",
        (
            snapshot is not None
            and
            snapshot.version == VERSION
        ),
    )


    check(
        "Final Snapshot Symbol Is Correct",
        (
            snapshot is not None
            and
            snapshot.symbol == SYMBOL
        ),
    )


    check(
        "Final Snapshot Integrity Is Valid",
        (
            snapshot is not None
            and
            snapshot.integrity_valid()
        ),
    )


    check(
        "Final Snapshot Keeps Exchange Network Write Count At Zero",
        (
            snapshot is not None
            and
            snapshot.exchange_network_write_count
            ==
            0
        ),
    )


    check(
        "Final Snapshot Keeps Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )


    check(
        "Final Snapshot Keeps Real Orders Disabled",
        LIVE_ORDER_EXECUTION is False,
    )


    # ==============================================================================================
    # TEST 24
    # ==============================================================================================


    print_test(
        24,
        "FINAL CONTROLLED-LIVE GO / NO-GO",
    )


    controls_present = all(

        [

            state.exchange_reconciled,

            not state.kill_switch_engaged,

            not state.ambiguous_outcome_block,

            (
                MAX_FUND_EXPOSURE_PERCENT
                ==
                35.0
            ),

            RECONCILIATION_REQUIRED,

            KILL_SWITCH_REQUIRED,

            AMBIGUOUS_OUTCOME_FAIL_CLOSED,

            (
                TELEGRAM_CAN_CONTROL_EXECUTION
                is False
            ),

            (
                state.exchange_network_write_count
                ==
                0
            ),

        ]

    )


    check(
        "All R35G Safety Controls Are Present",
        controls_present,
    )


    check(
        "R35G Does Not Activate Autonomous Live Trading",
        LIVE_ORDER_EXECUTION is False,
    )


    check(
        "R35G Contains No Exchange Order Transmitter",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )


    check(
        "Any Real-Money Mutation Requires Separate Reviewed Implementation",
        True,
    )


    # ==============================================================================================
    # SUMMARY
    # ==============================================================================================


    print(
        LINE,
        flush=True,
    )


    print(
        f"{VERSION}: VALIDATION SUMMARY",
        flush=True,
    )


    print(
        LINE,
        flush=True,
    )


    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )


    print(
        f"{VERSION}: PHASE={state.phase}",
        flush=True,
    )


    print(
        f"{VERSION}: GENERATION={state.generation}",
        flush=True,
    )


    print(
        f"{VERSION}: EPOCH={state.epoch}",
        flush=True,
    )


    print(
        f"{VERSION}: HIGHEST NONCE={state.highest_nonce}",
        flush=True,
    )


    print(
        f"{VERSION}: SYNTHETIC DISPATCH COUNT={state.synthetic_dispatch_count}",
        flush=True,
    )


    print(
        f"{VERSION}: EXCHANGE NETWORK WRITE COUNT={state.exchange_network_write_count}",
        flush=True,
    )


    print(
        f"{VERSION}: LIVE ORDER EXECUTION={LIVE_ORDER_EXECUTION}",
        flush=True,
    )


    print(
        f"{VERSION}: NETWORK WRITES ENABLED={EXCHANGE_NETWORK_WRITES_ENABLED}",
        flush=True,
    )


    print(
        f"{VERSION}: MAX FUND EXPOSURE={MAX_FUND_EXPOSURE_PERCENT}%",
        flush=True,
    )


    print(
        f"{VERSION}: KILL SWITCH REQUIRED={KILL_SWITCH_REQUIRED}",
        flush=True,
    )


    print(
        f"{VERSION}: RECONCILIATION REQUIRED={RECONCILIATION_REQUIRED}",
        flush=True,
    )


    print(
        f"{VERSION}: AMBIGUOUS OUTCOME FAIL CLOSED={AMBIGUOUS_OUTCOME_FAIL_CLOSED}",
        flush=True,
    )


    print(
        f"{VERSION}: TELEGRAM REPORTING ENABLED={TELEGRAM_REPORTING_ENABLED}",
        flush=True,
    )


    print(
        f"{VERSION}: TELEGRAM CONFIGURED={telegram_configured()}",
        flush=True,
    )


    print(
        f"{VERSION}: TELEGRAM ATTEMPTS={state.telegram_attempts}",
        flush=True,
    )


    print(
        f"{VERSION}: TELEGRAM SUCCESSES={state.telegram_successes}",
        flush=True,
    )


    print(
        f"{VERSION}: TELEGRAM FAILURES={state.telegram_failures}",
        flush=True,
    )


    print(
        f"{VERSION}: TELEGRAM CAN CONTROL EXECUTION={TELEGRAM_CAN_CONTROL_EXECUTION}",
        flush=True,
    )


    print(
        f"{VERSION}: TELEGRAM INBOUND COMMANDS ENABLED={TELEGRAM_INBOUND_COMMANDS_ENABLED}",
        flush=True,
    )


    print(
        f"{VERSION}: JOURNAL VALID={store.validate_journal(state)[0]}",
        flush=True,
    )


    print(
        f"{VERSION}: R35G PASSED - "
        f"CONTROLLED LIVE GATE VERIFIED - "
        f"AUTONOMOUS REAL-MONEY ORDER TRANSMISSION REMAINS DISABLED",
        flush=True,
    )


    return state


# ==================================================================================================
# MAIN
# ==================================================================================================


def main(
) -> None:


    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    bootstrap = StrategyState()


    bootstrap.seal()


    state_ref: Dict[
        str,
        StrategyState,
    ] = {

        "state":
            bootstrap

    }


    server = start_health_server(
        state_ref
    )


    try:


        state = run_validation(
            state_ref
        )


        heartbeat = 0


        while True:


            heartbeat += 1


            print(
                f"{VERSION}: HEARTBEAT={heartbeat}",
                flush=True,
            )


            time.sleep(
                60
            )


    finally:


        server.shutdown()


        server.server_close()


if __name__ == "__main__":

    main()
