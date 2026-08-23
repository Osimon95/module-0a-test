# ============================================================
# 0F-4H-R28-UNIT-F
# RESTART / REPLAY / IDEMPOTENCY SAFETY VALIDATION
#
# STANDALONE TEST UNIT
#
# NO EXCHANGE CONNECTION
# REAL ORDER TRANSMISSION DISABLED
# DEMO ORDER TRANSMISSION DISABLED
# NETWORK ACCESS DISABLED
# ============================================================

from __future__ import annotations

import hashlib
import json
import time

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional, Set


# ============================================================
# MODULE IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-F"


# ============================================================
# ABSOLUTE EXECUTION LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_ACCESS_ENABLED = False

HARD_REAL_POST_LOCK = True
HARD_DEMO_POST_LOCK = True


# ============================================================
# SAFETY COUNTERS
# ============================================================

REAL_POST_CALLED = False
DEMO_POST_CALLED = False
NETWORK_CALLED = False


# ============================================================
# HELPERS
# ============================================================

def stable_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_hex(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def decimal_string(
    value: Decimal,
) -> str:

    normalized = value.normalize()

    text = format(
        normalized,
        "f",
    )

    if "." in text:

        text = text.rstrip("0").rstrip(".")

    return text


def status_icon(
    passed: bool,
) -> str:

    return "✅ PASS" if passed else "❌ FAIL"


# ============================================================
# EXECUTION STATES
# ============================================================

class ExecutionState(
    str,
    Enum,
):

    CREATED = "CREATED"

    VALIDATED = "VALIDATED"

    SHADOW_COMMITTED = (
        "SHADOW_COMMITTED"
    )

    DEMO_PENDING = "DEMO_PENDING"

    DEMO_ACCEPTED = "DEMO_ACCEPTED"

    DEMO_REJECTED = "DEMO_REJECTED"

    COMPLETED = "COMPLETED"

    REJECTED = "REJECTED"


# ============================================================
# TERMINAL STATES
# ============================================================

TERMINAL_STATES = {

    ExecutionState.DEMO_ACCEPTED,

    ExecutionState.DEMO_REJECTED,

    ExecutionState.COMPLETED,

    ExecutionState.REJECTED,
}


# ============================================================
# EXECUTION INTENT
# ============================================================

@dataclass(
    frozen=True
)
class ExecutionIntent:

    signal_id: str

    symbol: str

    side: str

    position_side: str

    quantity: Decimal

    leverage: int

    client_order_id: str

    intent_id: str


# ============================================================
# SHADOW COMMIT
# ============================================================

@dataclass(
    frozen=True
)
class ShadowCommit:

    intent_id: str

    payload_fingerprint: str

    intent_fingerprint: str

    request_fingerprint: str

    commit_token: str


# ============================================================
# EXECUTION RECORD
# ============================================================

@dataclass
class ExecutionRecord:

    signal_id: str

    intent_id: str

    commit_token: str

    state: ExecutionState

    generation: int = 1


# ============================================================
# PERSISTED SNAPSHOT
# ============================================================

@dataclass(
    frozen=True
)
class PersistedSnapshot:

    payload: str

    checksum: str


# ============================================================
# EXECUTION STORE
# ============================================================

class ExecutionStore:

    def __init__(
        self,
    ) -> None:

        self.seen_signals: Set[str] = set()

        self.seen_intents: Set[str] = set()

        self.seen_commits: Set[str] = set()

        self.records: Dict[
            str,
            ExecutionRecord,
        ] = {}


# ============================================================
# BUILD EXECUTION INTENT
# ============================================================

def build_execution_intent(
    signal_id: str,
    symbol: str,
    side: str,
    position_side: str,
    quantity: Decimal,
    leverage: int,
) -> ExecutionIntent:

    signal_id = (
        signal_id
        .strip()
    )

    symbol = (
        symbol
        .strip()
        .upper()
    )

    side = (
        side
        .strip()
        .upper()
    )

    position_side = (
        position_side
        .strip()
        .upper()
    )

    if not signal_id:

        raise ValueError(
            "signal_id cannot be empty"
        )

    if not symbol:

        raise ValueError(
            "symbol cannot be empty"
        )

    if side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            f"Invalid side: {side}"
        )

    if position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "Invalid position_side: "
            f"{position_side}"
        )

    if quantity <= 0:

        raise ValueError(
            "quantity must be positive"
        )

    if leverage <= 0:

        raise ValueError(
            "leverage must be positive"
        )

    if leverage > 100:

        raise ValueError(
            "leverage exceeds local "
            "100x safety limit"
        )

    canonical = "|".join(
        [
            signal_id,
            symbol,
            side,
            position_side,
            decimal_string(
                quantity
            ),
            str(
                leverage
            ),
        ]
    )

    intent_id = sha256_hex(
        "R28-INTENT|"
        + canonical
    )

    client_order_id = (
        "R28"
        + intent_id[:24]
    )

    return ExecutionIntent(
        signal_id=signal_id,
        symbol=symbol,
        side=side,
        position_side=position_side,
        quantity=quantity,
        leverage=leverage,
        client_order_id=client_order_id,
        intent_id=intent_id,
    )


# ============================================================
# BUILD EXECUTION PAYLOAD
# ============================================================

def build_execution_payload(
    intent: ExecutionIntent,
) -> Dict[str, Any]:

    return {
        "symbol": intent.symbol,
        "side": intent.side,
        "positionSide": (
            intent.position_side
        ),
        "quantity": decimal_string(
            intent.quantity
        ),
        "leverage": intent.leverage,
        "clientOrderId": (
            intent.client_order_id
        ),
        "intentId": (
            intent.intent_id
        ),
    }


# ============================================================
# INTENT FINGERPRINT
# ============================================================

def calculate_intent_fingerprint(
    intent: ExecutionIntent,
) -> str:

    canonical = "|".join(
        [
            intent.intent_id,
            intent.signal_id,
            intent.symbol,
            intent.side,
            intent.position_side,
            decimal_string(
                intent.quantity
            ),
            str(
                intent.leverage
            ),
            intent.client_order_id,
        ]
    )

    return sha256_hex(
        canonical
    )


# ============================================================
# BUILD SHADOW COMMIT
# ============================================================

def build_shadow_commit(
    intent: ExecutionIntent,
    payload: Dict[str, Any],
) -> ShadowCommit:

    expected_payload = (
        build_execution_payload(
            intent
        )
    )

    if payload != expected_payload:

        raise ValueError(
            "Payload does not match "
            "execution intent"
        )

    canonical_payload = stable_json(
        payload
    )

    payload_fingerprint = (
        sha256_hex(
            canonical_payload
        )
    )

    request_fingerprint = (
        sha256_hex(
            "POST|"
            "/capi/v3/order"
            "|"
            + canonical_payload
        )
    )

    intent_fingerprint = (
        calculate_intent_fingerprint(
            intent
        )
    )

    commit_token = sha256_hex(
        "|".join(
            [
                intent.intent_id,
                payload_fingerprint,
                request_fingerprint,
                intent_fingerprint,
            ]
        )
    )

    return ShadowCommit(
        intent_id=intent.intent_id,
        payload_fingerprint=(
            payload_fingerprint
        ),
        intent_fingerprint=(
            intent_fingerprint
        ),
        request_fingerprint=(
            request_fingerprint
        ),
        commit_token=(
            commit_token
        ),
    )


# ============================================================
# VERIFY SHADOW COMMIT
# ============================================================

def verify_shadow_commit(
    intent: ExecutionIntent,
    payload: Dict[str, Any],
    commit: ShadowCommit,
) -> bool:

    expected = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    return (
        expected
        ==
        commit
    )


# ============================================================
# CREATE EXECUTION RECORD
# ============================================================

def create_execution_record(
    store: ExecutionStore,
    intent: ExecutionIntent,
    commit: ShadowCommit,
) -> ExecutionRecord:

    if intent.signal_id in (
        store.seen_signals
    ):

        raise RuntimeError(
            "Duplicate signal replay rejected"
        )

    if intent.intent_id in (
        store.seen_intents
    ):

        raise RuntimeError(
            "Duplicate intent replay rejected"
        )

    if commit.commit_token in (
        store.seen_commits
    ):

        raise RuntimeError(
            "Duplicate shadow commit replay "
            "rejected"
        )

    if (
        commit.intent_id
        !=
        intent.intent_id
    ):

        raise RuntimeError(
            "Shadow commit intent mismatch"
        )

    record = ExecutionRecord(
        signal_id=intent.signal_id,
        intent_id=intent.intent_id,
        commit_token=(
            commit.commit_token
        ),
        state=(
            ExecutionState
            .SHADOW_COMMITTED
        ),
        generation=1,
    )

    store.seen_signals.add(
        intent.signal_id
    )

    store.seen_intents.add(
        intent.intent_id
    )

    store.seen_commits.add(
        commit.commit_token
    )

    store.records[
        intent.intent_id
    ] = record

    return record


# ============================================================
# STATE TRANSITION
# ============================================================

VALID_TRANSITIONS = {

    ExecutionState.CREATED: {
        ExecutionState.VALIDATED,
        ExecutionState.REJECTED,
    },

    ExecutionState.VALIDATED: {
        ExecutionState.SHADOW_COMMITTED,
        ExecutionState.REJECTED,
    },

    ExecutionState.SHADOW_COMMITTED: {
        ExecutionState.DEMO_PENDING,
        ExecutionState.REJECTED,
    },

    ExecutionState.DEMO_PENDING: {
        ExecutionState.DEMO_ACCEPTED,
        ExecutionState.DEMO_REJECTED,
    },

    ExecutionState.DEMO_ACCEPTED: set(),

    ExecutionState.DEMO_REJECTED: set(),

    ExecutionState.COMPLETED: set(),

    ExecutionState.REJECTED: set(),
}


def transition_state(
    record: ExecutionRecord,
    target_state: ExecutionState,
) -> None:

    if record.state in TERMINAL_STATES:

        raise RuntimeError(
            "Terminal execution state "
            "cannot transition"
        )

    allowed = (
        VALID_TRANSITIONS
        .get(
            record.state,
            set(),
        )
    )

    if target_state not in allowed:

        raise RuntimeError(
            "Invalid execution state "
            f"transition: "
            f"{record.state.value} -> "
            f"{target_state.value}"
        )

    record.state = target_state


# ============================================================
# PERSIST EXECUTION STORE
# ============================================================

def persist_execution_store(
    store: ExecutionStore,
) -> PersistedSnapshot:

    data = {

        "seen_signals": sorted(
            store.seen_signals
        ),

        "seen_intents": sorted(
            store.seen_intents
        ),

        "seen_commits": sorted(
            store.seen_commits
        ),

        "records": {

            intent_id: {

                "signal_id": (
                    record.signal_id
                ),

                "intent_id": (
                    record.intent_id
                ),

                "commit_token": (
                    record.commit_token
                ),

                "state": (
                    record.state.value
                ),

                "generation": (
                    record.generation
                ),
            }

            for (
                intent_id,
                record,
            )

            in sorted(
                store.records.items()
            )
        },
    }

    payload = stable_json(
        data
    )

    checksum = sha256_hex(
        "R28-PERSISTED-STATE|"
        + payload
    )

    return PersistedSnapshot(
        payload=payload,
        checksum=checksum,
    )


# ============================================================
# RESTORE EXECUTION STORE
# ============================================================

def restore_execution_store(
    snapshot: PersistedSnapshot,
) -> ExecutionStore:

    expected_checksum = sha256_hex(
        "R28-PERSISTED-STATE|"
        + snapshot.payload
    )

    if (
        snapshot.checksum
        !=
        expected_checksum
    ):

        raise RuntimeError(
            "Persisted state checksum "
            "validation failed"
        )

    try:

        raw = json.loads(
            snapshot.payload
        )

    except Exception as exc:

        raise RuntimeError(
            "Persisted state JSON invalid"
        ) from exc

    required_keys = {
        "seen_signals",
        "seen_intents",
        "seen_commits",
        "records",
    }

    if (
        set(
            raw.keys()
        )
        !=
        required_keys
    ):

        raise RuntimeError(
            "Persisted state schema invalid"
        )

    store = ExecutionStore()

    store.seen_signals = set(
        raw[
            "seen_signals"
        ]
    )

    store.seen_intents = set(
        raw[
            "seen_intents"
        ]
    )

    store.seen_commits = set(
        raw[
            "seen_commits"
        ]
    )

    records_raw = raw[
        "records"
    ]

    if not isinstance(
        records_raw,
        dict,
    ):

        raise RuntimeError(
            "Persisted records invalid"
        )

    for (
        intent_id,
        record_raw,
    ) in records_raw.items():

        if (
            record_raw.get(
                "intent_id"
            )
            !=
            intent_id
        ):

            raise RuntimeError(
                "Persisted intent index "
                "mismatch"
            )

        try:

            state = ExecutionState(
                record_raw[
                    "state"
                ]
            )

        except Exception as exc:

            raise RuntimeError(
                "Persisted execution state "
                "invalid"
            ) from exc

        record = ExecutionRecord(

            signal_id=record_raw[
                "signal_id"
            ],

            intent_id=record_raw[
                "intent_id"
            ],

            commit_token=record_raw[
                "commit_token"
            ],

            state=state,

            generation=int(
                record_raw[
                    "generation"
                ]
            ) + 1,
        )

        if (
            record.signal_id
            not in
            store.seen_signals
        ):

            raise RuntimeError(
                "Persisted signal index "
                "inconsistent"
            )

        if (
            record.intent_id
            not in
            store.seen_intents
        ):

            raise RuntimeError(
                "Persisted intent index "
                "inconsistent"
            )

        if (
            record.commit_token
            not in
            store.seen_commits
        ):

            raise RuntimeError(
                "Persisted commit index "
                "inconsistent"
            )

        store.records[
            intent_id
        ] = record

    return store


# ============================================================
# REAL POST — ABSOLUTELY BLOCKED
# ============================================================

def real_order_post(
    *args: Any,
    **kwargs: Any,
) -> None:

    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise RuntimeError(
        "R28 UNIT F HARD SAFETY LOCK: "
        "REAL ORDER POST BLOCKED"
    )


# ============================================================
# DEMO POST — ABSOLUTELY BLOCKED
# ============================================================

def demo_order_post(
    *args: Any,
    **kwargs: Any,
) -> None:

    global DEMO_POST_CALLED

    DEMO_POST_CALLED = True

    raise RuntimeError(
        "R28 UNIT F HARD SAFETY LOCK: "
        "DEMO ORDER POST BLOCKED"
    )


# ============================================================
# NETWORK ACCESS — ABSOLUTELY BLOCKED
# ============================================================

def network_request(
    *args: Any,
    **kwargs: Any,
) -> None:

    global NETWORK_CALLED

    NETWORK_CALLED = True

    raise RuntimeError(
        "R28 UNIT F HARD SAFETY LOCK: "
        "NETWORK ACCESS BLOCKED"
    )


# ============================================================
# TEST 1
# DUPLICATE SIGNAL REPLAY
# ============================================================

def test_duplicate_signal_replay(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-001"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = build_shadow_commit(
        intent,
        payload,
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    fake_intent = (
        ExecutionIntent(
            signal_id=(
                intent.signal_id
            ),
            symbol="ETHUSDT",
            side="BUY",
            position_side="LONG",
            quantity=Decimal(
                "0.001"
            ),
            leverage=50,
            client_order_id=(
                "DIFFERENT"
            ),
            intent_id=(
                "DIFFERENT-INTENT"
            ),
        )
    )

    fake_payload = (
        build_execution_payload(
            fake_intent
        )
    )

    fake_commit = (
        build_shadow_commit(
            fake_intent,
            fake_payload,
        )
    )

    try:

        create_execution_record(
            store,
            fake_intent,
            fake_commit,
        )

    except RuntimeError as exc:

        return (
            "Duplicate signal"
            in str(
                exc
            )
        )

    return False


# ============================================================
# TEST 2
# DUPLICATE INTENT REPLAY
# ============================================================

def test_duplicate_intent_replay(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-002"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = build_shadow_commit(
        intent,
        payload,
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    store.seen_signals.remove(
        intent.signal_id
    )

    try:

        create_execution_record(
            store,
            intent,
            commit,
        )

    except RuntimeError as exc:

        return (
            "Duplicate intent"
            in str(
                exc
            )
        )

    return False


# ============================================================
# TEST 3
# DUPLICATE SHADOW COMMIT
# ============================================================

def test_duplicate_shadow_commit(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-003"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = build_shadow_commit(
        intent,
        payload,
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    store.seen_signals.remove(
        intent.signal_id
    )

    store.seen_intents.remove(
        intent.intent_id
    )

    try:

        create_execution_record(
            store,
            intent,
            commit,
        )

    except RuntimeError as exc:

        return (
            "Duplicate shadow commit"
            in str(
                exc
            )
        )

    return False


# ============================================================
# TEST 4
# RESTART STATE RESTORATION
# ============================================================

def test_restart_state_restoration(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-004"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = build_shadow_commit(
        intent,
        payload,
    )

    original_record = (
        create_execution_record(
            store,
            intent,
            commit,
        )
    )

    snapshot = (
        persist_execution_store(
            store
        )
    )

    restored = (
        restore_execution_store(
            snapshot
        )
    )

    restored_record = (
        restored.records.get(
            intent.intent_id
        )
    )

    if restored_record is None:

        return False

    return (

        restored_record.signal_id
        ==
        original_record.signal_id

        and

        restored_record.intent_id
        ==
        original_record.intent_id

        and

        restored_record.commit_token
        ==
        original_record.commit_token

        and

        restored_record.state
        ==
        original_record.state

        and

        restored_record.generation
        ==
        2
    )


# ============================================================
# TEST 5
# REPLAY AFTER RESTART
# ============================================================

def test_replay_after_restart(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-005"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = build_shadow_commit(
        intent,
        payload,
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    snapshot = (
        persist_execution_store(
            store
        )
    )

    restarted_store = (
        restore_execution_store(
            snapshot
        )
    )

    try:

        create_execution_record(
            restarted_store,
            intent,
            commit,
        )

    except RuntimeError as exc:

        return (
            "Duplicate signal"
            in str(
                exc
            )
        )

    return False


# ============================================================
# TEST 6
# TERMINAL STATE REPLAY REJECTION
# ============================================================

def test_terminal_state_replay(
) -> bool:

    record = ExecutionRecord(
        signal_id="terminal-signal",
        intent_id="terminal-intent",
        commit_token="terminal-commit",
        state=(
            ExecutionState
            .DEMO_REJECTED
        ),
    )

    try:

        transition_state(
            record,
            ExecutionState.DEMO_PENDING,
        )

    except RuntimeError as exc:

        return (
            "Terminal execution state"
            in str(
                exc
            )
        )

    return False


# ============================================================
# TEST 7
# CORRUPTED SNAPSHOT REJECTION
# ============================================================

def test_corrupted_snapshot_rejected(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-007"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    snapshot = (
        persist_execution_store(
            store
        )
    )

    corrupted = (
        PersistedSnapshot(
            payload=(
                snapshot.payload
                + "TAMPERED"
            ),
            checksum=(
                snapshot.checksum
            ),
        )
    )

    try:

        restore_execution_store(
            corrupted
        )

    except RuntimeError as exc:

        return (
            "checksum"
            in str(
                exc
            ).lower()
        )

    return False


# ============================================================
# TEST 8
# INTERNAL STATE INCONSISTENCY REJECTION
# ============================================================

def test_inconsistent_state_rejected(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-008"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    snapshot = (
        persist_execution_store(
            store
        )
    )

    raw = json.loads(
        snapshot.payload
    )

    raw[
        "seen_signals"
    ] = []

    tampered_payload = stable_json(
        raw
    )

    tampered_snapshot = (
        PersistedSnapshot(

            payload=(
                tampered_payload
            ),

            checksum=sha256_hex(
                "R28-PERSISTED-STATE|"
                + tampered_payload
            ),
        )
    )

    try:

        restore_execution_store(
            tampered_snapshot
        )

    except RuntimeError as exc:

        return (
            "inconsistent"
            in str(
                exc
            ).lower()
        )

    return False


# ============================================================
# TEST 9
# DETERMINISTIC SNAPSHOT
# ============================================================

def test_deterministic_snapshot(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-009"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    snapshot_1 = (
        persist_execution_store(
            store
        )
    )

    snapshot_2 = (
        persist_execution_store(
            store
        )
    )

    return (
        snapshot_1
        ==
        snapshot_2
    )


# ============================================================
# TEST 10
# DETERMINISTIC RESTORE
# ============================================================

def test_deterministic_restore(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-010"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    snapshot = (
        persist_execution_store(
            store
        )
    )

    restored_1 = (
        restore_execution_store(
            snapshot
        )
    )

    restored_2 = (
        restore_execution_store(
            snapshot
        )
    )

    snapshot_1 = (
        persist_execution_store(
            restored_1
        )
    )

    snapshot_2 = (
        persist_execution_store(
            restored_2
        )
    )

    return (
        snapshot_1
        ==
        snapshot_2
    )


# ============================================================
# TEST 11
# SHADOW COMMIT SURVIVES RESTART
# ============================================================

def test_shadow_commit_survives_restart(
) -> bool:

    store = ExecutionStore()

    intent = build_execution_intent(
        signal_id=(
            "unit-f-signal-011"
        ),
        symbol="BTCUSDT",
        side="BUY",
        position_side="LONG",
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    payload = (
        build_execution_payload(
            intent
        )
    )

    commit = (
        build_shadow_commit(
            intent,
            payload,
        )
    )

    create_execution_record(
        store,
        intent,
        commit,
    )

    snapshot = (
        persist_execution_store(
            store
        )
    )

    restored = (
        restore_execution_store(
            snapshot
        )
    )

    record = (
        restored.records[
            intent.intent_id
        ]
    )

    return (

        record.commit_token
        ==
        commit.commit_token

        and

        verify_shadow_commit(
            intent,
            payload,
            commit,
        )
    )


# ============================================================
# TEST 12
# NETWORK / ORDER LOCKS
# ============================================================

def test_execution_locks(
) -> bool:

    global REAL_POST_CALLED
    global DEMO_POST_CALLED
    global NETWORK_CALLED

    REAL_POST_CALLED = False
    DEMO_POST_CALLED = False
    NETWORK_CALLED = False

    real_blocked = False

    demo_blocked = False

    network_blocked = False

    try:

        real_order_post()

    except RuntimeError:

        real_blocked = True

    try:

        demo_order_post()

    except RuntimeError:

        demo_blocked = True

    try:

        network_request()

    except RuntimeError:

        network_blocked = True

    calls_detected = (
        REAL_POST_CALLED
        and
        DEMO_POST_CALLED
        and
        NETWORK_CALLED
    )

    # Reset diagnostic counters.
    #
    # These calls were deliberate blocked-call
    # tests only. No external request occurred.

    REAL_POST_CALLED = False

    DEMO_POST_CALLED = False

    NETWORK_CALLED = False

    return (
        real_blocked
        and
        demo_blocked
        and
        network_blocked
        and
        calls_detected
        and
        HARD_REAL_POST_LOCK
        and
        HARD_DEMO_POST_LOCK
        and
        not LIVE_ORDER_EXECUTION
        and
        not DEMO_ORDER_EXECUTION
        and
        not NETWORK_ACCESS_ENABLED
    )


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================

def final_safety_assertions(
) -> bool:

    return all(
        [
            LIVE_ORDER_EXECUTION
            is False,

            DEMO_ORDER_EXECUTION
            is False,

            NETWORK_ACCESS_ENABLED
            is False,

            HARD_REAL_POST_LOCK
            is True,

            HARD_DEMO_POST_LOCK
            is True,

            REAL_POST_CALLED
            is False,

            DEMO_POST_CALLED
            is False,

            NETWORK_CALLED
            is False,
        ]
    )


# ============================================================
# COMPLETE UNIT F DIAGNOSTIC
# ============================================================

def run_unit_f_diagnostic(
) -> Dict[str, bool]:

    results = {

        "Duplicate Signal Replay Rejected":
            test_duplicate_signal_replay(),

        "Duplicate Intent Replay Rejected":
            test_duplicate_intent_replay(),

        "Duplicate Shadow Commit Rejected":
            test_duplicate_shadow_commit(),

        "Restart State Restored":
            test_restart_state_restoration(),

        "Replay After Restart Rejected":
            test_replay_after_restart(),

        "Terminal State Replay Rejected":
            test_terminal_state_replay(),

        "Corrupted Snapshot Rejected":
            test_corrupted_snapshot_rejected(),

        "Inconsistent State Rejected":
            test_inconsistent_state_rejected(),

        "Deterministic Snapshot":
            test_deterministic_snapshot(),

        "Deterministic Restore":
            test_deterministic_restore(),

        "Shadow Commit Survives Restart":
            test_shadow_commit_survives_restart(),

        "Execution Locks Active":
            test_execution_locks(),
    }

    results[
        "Final Safety Assertions"
    ] = final_safety_assertions()

    return results


# ============================================================
# PRINT HEADER
# ============================================================

def print_header(
) -> None:

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "STANDALONE RESTART / REPLAY / "
        "IDEMPOTENCY SAFETY VALIDATION"
    )

    print(
        "EXECUTION INTENT -> PAYLOAD -> "
        "SHADOW COMMIT -> PERSISTENCE"
    )

    print(
        "-> RESTART -> REPLAY PROTECTION"
    )

    print(
        "NO EXCHANGE CONNECTION"
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED"
    )

    print(
        "DEMO ORDER TRANSMISSION DISABLED"
    )

    print(
        "NETWORK ACCESS DISABLED"
    )

    print(
        "=" * 60
    )


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    results: Dict[str, bool],
) -> None:

    print(
        "R28 UNIT F RESTART / "
        "IDEMPOTENCY GATES"
    )

    print(
        "-" * 60
    )

    for (
        name,
        passed,
    ) in results.items():

        print(
            f"{name:<42} "
            f"{status_icon(passed)}"
        )

    print(
        "-" * 60
    )


# ============================================================
# MAIN
# ============================================================

def main(
) -> None:

    print_header()

    try:

        results = (
            run_unit_f_diagnostic()
        )

        print_results(
            results
        )

        all_passed = all(
            results.values()
        )

        if not all_passed:

            failed = [

                name

                for (
                    name,
                    passed,
                )

                in results.items()

                if not passed
            ]

            print()

            print(
                "❌ R28 UNIT F "
                "DIAGNOSTIC FAILED"
            )

            print(
                "FAILED GATES:"
            )

            for name in failed:

                print(
                    f" - {name}"
                )

            print(
                "=" * 60
            )

            raise SystemExit(
                1
            )

        print()

        print(
            "✅ R28 UNIT F DIAGNOSTIC PASSED"
        )

        print(
            "✅ RESTART STATE SAFETY VALIDATED"
        )

        print(
            "✅ SIGNAL / INTENT / SHADOW "
            "REPLAY PROTECTION VALIDATED"
        )

        print(
            "✅ PERSISTED STATE INTEGRITY "
            "VALIDATED"
        )

        print(
            "✅ IDEMPOTENT RECOVERY VALIDATED"
        )

        print(
            "✅ UNIT F READY FOR INTEGRATION"
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE"
        )

        print(
            "=" * 60
        )

    except Exception as exc:

        print()

        print(
            "❌ R28 UNIT F FATAL ERROR"
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            "🛡 REAL ORDER TRANSMISSION "
            "REMAINS DISABLED"
        )

        print(
            "🛡 DEMO ORDER TRANSMISSION "
            "REMAINS DISABLED"
        )

        print(
            "🛡 NETWORK ACCESS REMAINS "
            "DISABLED"
        )

        print(
            "=" * 60
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()

    
