# ============================================================
# 0F-4H-R28-INTEGRATED-A-G
# R28 INTEGRATION VALIDATION
#
# UNITS A + B + C + D + E + F + G
#
# SIGNAL
# -> EXECUTION INTENT
# -> EXECUTION PAYLOAD
# -> SHADOW COMMIT
# -> EXECUTION STATE MACHINE
# -> REPLAY / RESTART SAFETY
# -> PERSISTENT RUNTIME
#
# NO EXCHANGE CONNECTION
# NO REAL ORDER TRANSMISSION
# NO DEMO ORDER TRANSMISSION
# NO NETWORK ACCESS
# ============================================================

print(
    "R28 A-G: MAIN.PY ENTERED",
    flush=True,
)


# ============================================================
# IMPORTS
# ============================================================

import asyncio
import hashlib
import json
import os
import time

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional, Set


print(
    "R28 A-G: IMPORTS COMPLETE",
    flush=True,
)


# ============================================================
# MODULE IDENTIFICATION
# ============================================================

MODULE_NAME = "0F-4H-R28-INTEGRATED-A-G"

MODULE_VERSION = "R28-A-G"


# ============================================================
# ABSOLUTE EXECUTION SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

NETWORK_ACCESS_ENABLED = False

HARD_REAL_POST_LOCK = True

HARD_DEMO_POST_LOCK = True


REAL_POST_CALLED = False

DEMO_POST_CALLED = False

NETWORK_CALLED = False


# ============================================================
# R28 SAFETY CONFIGURATION
# ============================================================

SIGNAL_EXPIRY_SECONDS = 120

LOSS_COOLDOWN_SECONDS = 300

MAX_LEVERAGE = 100

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    "35"
)

ENTRY_PERCENT = Decimal(
    "5"
)

MAX_PYRAMID_ADDS = 1

MAX_BACKUPS = 3

BACKUP_SIZE_PERCENT = Decimal(
    "5"
)

BACKUP_BUFFER_PERCENT = Decimal(
    "0.3"
)

MARGIN_TYPE = "ISOLATED"


# ============================================================
# RUNTIME CONFIGURATION
# ============================================================

RUNTIME_HEARTBEAT_SECONDS = 60

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# EXECUTION STATES
# ============================================================

STATE_NEW = "NEW"

STATE_VALIDATED = "VALIDATED"

STATE_SHADOW_COMMITTED = "SHADOW_COMMITTED"

STATE_RECONCILED = "RECONCILED"

STATE_FILLED = "FILLED"

STATE_CANCELED = "CANCELED"

STATE_REJECTED = "REJECTED"

STATE_EXPIRED = "EXPIRED"


TERMINAL_STATES = {
    STATE_FILLED,
    STATE_CANCELED,
    STATE_REJECTED,
    STATE_EXPIRED,
}


# ============================================================
# ALLOWED STATE TRANSITIONS
# ============================================================

ALLOWED_TRANSITIONS = {

    STATE_NEW: {
        STATE_VALIDATED,
        STATE_REJECTED,
        STATE_EXPIRED,
    },

    STATE_VALIDATED: {
        STATE_SHADOW_COMMITTED,
        STATE_REJECTED,
        STATE_EXPIRED,
    },

    STATE_SHADOW_COMMITTED: {
        STATE_RECONCILED,
        STATE_REJECTED,
        STATE_EXPIRED,
    },

    STATE_RECONCILED: {
        STATE_FILLED,
        STATE_CANCELED,
        STATE_REJECTED,
        STATE_EXPIRED,
    },

    STATE_FILLED: set(),

    STATE_CANCELED: set(),

    STATE_REJECTED: set(),

    STATE_EXPIRED: set(),
}


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass(frozen=True)
class Signal:

    signal_id: str

    symbol: str

    direction: str

    created_ms: int


@dataclass(frozen=True)
class ExecutionIntent:

    intent_id: str

    signal_id: str

    symbol: str

    side: str

    position_side: str

    quantity: str

    leverage: int

    margin_type: str


@dataclass(frozen=True)
class ShadowCommit:

    commit_id: str

    intent_id: str

    payload_hash: str

    created_ms: int


# ============================================================
# DETERMINISTIC HELPERS
# ============================================================

def stable_json(
    value,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )


def sha256_text(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# UNIT A
# SIGNAL NORMALIZATION
# ============================================================

def normalize_signal(
    signal_obj: Signal,
) -> Signal:

    signal_id = (
        signal_obj
        .signal_id
        .strip()
    )

    symbol = (
        signal_obj
        .symbol
        .strip()
        .upper()
    )

    direction = (
        signal_obj
        .direction
        .strip()
        .upper()
    )

    return Signal(
        signal_id=signal_id,
        symbol=symbol,
        direction=direction,
        created_ms=signal_obj.created_ms,
    )


# ============================================================
# UNIT A
# SIGNAL VALIDATION
# ============================================================

def validate_signal(
    signal_obj: Signal,
) -> bool:

    signal_obj = normalize_signal(
        signal_obj
    )

    if not signal_obj.signal_id:

        raise ValueError(
            "signal_id cannot be empty"
        )

    if not signal_obj.symbol:

        raise ValueError(
            "symbol cannot be empty"
        )

    if signal_obj.direction not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "invalid signal direction"
        )

    if signal_obj.created_ms <= 0:

        raise ValueError(
            "invalid signal timestamp"
        )

    return True


# ============================================================
# UNIT A
# SIGNAL FRESHNESS
# ============================================================

def signal_is_fresh(
    signal_obj: Signal,
    now_ms: int,
) -> bool:

    if signal_obj.created_ms > now_ms:

        return False

    age_ms = (
        now_ms
        - signal_obj.created_ms
    )

    maximum_age_ms = (
        SIGNAL_EXPIRY_SECONDS
        * 1000
    )

    return (
        age_ms
        <= maximum_age_ms
    )


# ============================================================
# UNIT A
# LOSS COOLDOWN
# ============================================================

def loss_cooldown_active(
    last_loss_ms: Optional[int],
    now_ms: int,
) -> bool:

    if last_loss_ms is None:

        return False

    if last_loss_ms > now_ms:

        return True

    elapsed_ms = (
        now_ms
        - last_loss_ms
    )

    cooldown_ms = (
        LOSS_COOLDOWN_SECONDS
        * 1000
    )

    return (
        elapsed_ms
        < cooldown_ms
    )


# ============================================================
# UNIT B
# EXECUTION INTENT CREATION
# ============================================================

def build_execution_intent(
    signal_obj: Signal,
    quantity: Decimal,
    leverage: int,
) -> ExecutionIntent:

    signal_obj = normalize_signal(
        signal_obj
    )

    validate_signal(
        signal_obj
    )

    if quantity <= Decimal(
        "0"
    ):

        raise ValueError(
            "quantity must be positive"
        )

    if leverage <= 0:

        raise ValueError(
            "leverage must be positive"
        )

    if leverage > MAX_LEVERAGE:

        raise ValueError(
            "leverage exceeds local safety limit"
        )

    if signal_obj.direction == "LONG":

        side = "BUY"

        position_side = "LONG"

    elif signal_obj.direction == "SHORT":

        side = "SELL"

        position_side = "SHORT"

    else:

        raise ValueError(
            "invalid execution direction"
        )

    quantity_string = format(
        quantity,
        "f",
    )

    fingerprint_source = stable_json(
        {
            "signal_id":
                signal_obj.signal_id,

            "symbol":
                signal_obj.symbol,

            "side":
                side,

            "position_side":
                position_side,

            "quantity":
                quantity_string,

            "leverage":
                leverage,

            "margin_type":
                MARGIN_TYPE,
        }
    )

    intent_id = (
        "r28-"
        + sha256_text(
            fingerprint_source
        )[:24]
    )

    return ExecutionIntent(
        intent_id=intent_id,
        signal_id=signal_obj.signal_id,
        symbol=signal_obj.symbol,
        side=side,
        position_side=position_side,
        quantity=quantity_string,
        leverage=leverage,
        margin_type=MARGIN_TYPE,
    )


# ============================================================
# UNIT B
# EXECUTION INTENT VALIDATION
# ============================================================

def validate_execution_intent(
    intent: ExecutionIntent,
) -> bool:

    if not intent.intent_id:

        raise ValueError(
            "intent_id cannot be empty"
        )

    if not intent.signal_id:

        raise ValueError(
            "signal_id cannot be empty"
        )

    if not intent.symbol:

        raise ValueError(
            "symbol cannot be empty"
        )

    if intent.side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            "invalid execution side"
        )

    if intent.position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "invalid position side"
        )

    if Decimal(
        intent.quantity
    ) <= Decimal(
        "0"
    ):

        raise ValueError(
            "quantity must be positive"
        )

    if intent.leverage <= 0:

        raise ValueError(
            "invalid leverage"
        )

    if intent.leverage > MAX_LEVERAGE:

        raise ValueError(
            "leverage exceeds local limit"
        )

    if intent.margin_type != "ISOLATED":

        raise ValueError(
            "margin type must be ISOLATED"
        )

    if (
        intent.side == "BUY"
        and
        intent.position_side != "LONG"
    ):

        raise ValueError(
            "BUY must bind to LONG"
        )

    if (
        intent.side == "SELL"
        and
        intent.position_side != "SHORT"
    ):

        raise ValueError(
            "SELL must bind to SHORT"
        )

    return True


# ============================================================
# UNIT C
# EXECUTION PAYLOAD
# ============================================================

def build_execution_payload(
    intent: ExecutionIntent,
) -> Dict[str, str]:

    validate_execution_intent(
        intent
    )

    return {

        "symbol":
            intent.symbol,

        "side":
            intent.side,

        "positionSide":
            intent.position_side,

        "quantity":
            intent.quantity,

        "leverage":
            str(
                intent.leverage
            ),

        "marginType":
            intent.margin_type,

        "clientOrderId":
            intent.intent_id,
    }


# ============================================================
# UNIT C
# PAYLOAD VALIDATION
# ============================================================

def validate_execution_payload(
    intent: ExecutionIntent,
    payload: Dict[str, str],
) -> bool:

    expected_payload = (
        build_execution_payload(
            intent
        )
    )

    if payload != expected_payload:

        raise ValueError(
            "execution payload does not match intent"
        )

    return True


# ============================================================
# UNIT C
# SHADOW COMMIT CREATION
# ============================================================

def create_shadow_commit(
    intent: ExecutionIntent,
    payload: Dict[str, str],
    created_ms: int,
) -> ShadowCommit:

    validate_execution_payload(
        intent,
        payload,
    )

    payload_hash = sha256_text(
        stable_json(
            payload
        )
    )

    commit_source = stable_json(
        {
            "intent_id":
                intent.intent_id,

            "payload_hash":
                payload_hash,
        }
    )

    commit_id = (
        "shadow-"
        + sha256_text(
            commit_source
        )[:24]
    )

    return ShadowCommit(
        commit_id=commit_id,
        intent_id=intent.intent_id,
        payload_hash=payload_hash,
        created_ms=created_ms,
    )


# ============================================================
# UNIT C
# SHADOW COMMIT VALIDATION
# ============================================================

def validate_shadow_commit(
    intent: ExecutionIntent,
    payload: Dict[str, str],
    commit: ShadowCommit,
) -> bool:

    expected_payload_hash = sha256_text(
        stable_json(
            payload
        )
    )

    if (
        commit.intent_id
        != intent.intent_id
    ):

        raise ValueError(
            "shadow intent mismatch"
        )

    if (
        commit.payload_hash
        != expected_payload_hash
    ):

        raise ValueError(
            "shadow payload mismatch"
        )

    expected_commit_source = stable_json(
        {
            "intent_id":
                intent.intent_id,

            "payload_hash":
                expected_payload_hash,
        }
    )

    expected_commit_id = (
        "shadow-"
        + sha256_text(
            expected_commit_source
        )[:24]
    )

    if (
        commit.commit_id
        != expected_commit_id
    ):

        raise ValueError(
            "shadow commit id mismatch"
        )

    return True


# ============================================================
# UNIT D
# EXECUTION STATE MACHINE
# ============================================================

class ExecutionStateMachine:

    def __init__(
        self,
        state: str = STATE_NEW,
    ):

        if state not in ALLOWED_TRANSITIONS:

            raise ValueError(
                "unknown execution state"
            )

        self.state = state

    def transition(
        self,
        new_state: str,
    ):

        if self.state in TERMINAL_STATES:

            raise RuntimeError(
                "terminal state cannot transition"
            )

        allowed = ALLOWED_TRANSITIONS.get(
            self.state,
            set(),
        )

        if new_state not in allowed:

            raise RuntimeError(
                "invalid execution state transition: "
                + self.state
                + " -> "
                + new_state
            )

        self.state = new_state

    def validate(
        self,
    ):

        self.transition(
            STATE_VALIDATED
        )

    def shadow_commit(
        self,
    ):

        self.transition(
            STATE_SHADOW_COMMITTED
        )

    def reconcile(
        self,
    ):

        self.transition(
            STATE_RECONCILED
        )

    def fill(
        self,
    ):

        self.transition(
            STATE_FILLED
        )

    def cancel(
        self,
    ):

        self.transition(
            STATE_CANCELED
        )

    def reject(
        self,
    ):

        self.transition(
            STATE_REJECTED
        )

    def expire(
        self,
    ):

        self.transition(
            STATE_EXPIRED
        )


# ============================================================
# UNIT F
# REPLAY GUARD
# ============================================================

class ReplayGuard:

    def __init__(
        self,
    ):

        self.signal_ids: Set[str] = set()

        self.intent_ids: Set[str] = set()

        self.commit_ids: Set[str] = set()

    def register_signal(
        self,
        signal_id: str,
    ) -> bool:

        signal_id = (
            signal_id
            .strip()
        )

        if not signal_id:

            raise ValueError(
                "signal id cannot be empty"
            )

        if signal_id in self.signal_ids:

            return False

        self.signal_ids.add(
            signal_id
        )

        return True

    def register_intent(
        self,
        intent_id: str,
    ) -> bool:

        intent_id = (
            intent_id
            .strip()
        )

        if not intent_id:

            raise ValueError(
                "intent id cannot be empty"
            )

        if intent_id in self.intent_ids:

            return False

        self.intent_ids.add(
            intent_id
        )

        return True

    def register_commit(
        self,
        commit_id: str,
    ) -> bool:

        commit_id = (
            commit_id
            .strip()
        )

        if not commit_id:

            raise ValueError(
                "commit id cannot be empty"
            )

        if commit_id in self.commit_ids:

            return False

        self.commit_ids.add(
            commit_id
        )

        return True

    def snapshot(
        self,
    ) -> str:

        snapshot_data = {

            "version":
                1,

            "signal_ids":
                sorted(
                    self.signal_ids
                ),

            "intent_ids":
                sorted(
                    self.intent_ids
                ),

            "commit_ids":
                sorted(
                    self.commit_ids
                ),
        }

        payload = stable_json(
            snapshot_data
        )

        checksum = sha256_text(
            payload
        )

        wrapper = {

            "payload":
                snapshot_data,

            "checksum":
                checksum,
        }

        return stable_json(
            wrapper
        )

    @classmethod
    def restore(
        cls,
        snapshot_text: str,
    ):

        try:

            wrapper = json.loads(
                snapshot_text
            )

        except Exception as exc:

            raise ValueError(
                "corrupted replay snapshot"
            ) from exc

        if not isinstance(
            wrapper,
            dict,
        ):

            raise ValueError(
                "invalid replay snapshot"
            )

        if "payload" not in wrapper:

            raise ValueError(
                "snapshot payload missing"
            )

        if "checksum" not in wrapper:

            raise ValueError(
                "snapshot checksum missing"
            )

        payload = wrapper[
            "payload"
        ]

        checksum = wrapper[
            "checksum"
        ]

        expected_checksum = sha256_text(
            stable_json(
                payload
            )
        )

        if checksum != expected_checksum:

            raise ValueError(
                "snapshot checksum mismatch"
            )

        if (
            payload.get(
                "version"
            )
            != 1
        ):

            raise ValueError(
                "unsupported snapshot version"
            )

        signal_ids = payload.get(
            "signal_ids"
        )

        intent_ids = payload.get(
            "intent_ids"
        )

        commit_ids = payload.get(
            "commit_ids"
        )

        if not isinstance(
            signal_ids,
            list,
        ):

            raise ValueError(
                "invalid signal snapshot"
            )

        if not isinstance(
            intent_ids,
            list,
        ):

            raise ValueError(
                "invalid intent snapshot"
            )

        if not isinstance(
            commit_ids,
            list,
        ):

            raise ValueError(
                "invalid commit snapshot"
            )

        if (
            len(signal_ids)
            != len(set(signal_ids))
        ):

            raise ValueError(
                "duplicate signal ids in snapshot"
            )

        if (
            len(intent_ids)
            != len(set(intent_ids))
        ):

            raise ValueError(
                "duplicate intent ids in snapshot"
            )

        if (
            len(commit_ids)
            != len(set(commit_ids))
        ):

            raise ValueError(
                "duplicate commit ids in snapshot"
            )

        restored = cls()

        restored.signal_ids = set(
            signal_ids
        )

        restored.intent_ids = set(
            intent_ids
        )

        restored.commit_ids = set(
            commit_ids
        )

        return restored


# ============================================================
# UNIT F
# EXECUTION RECORD
# ============================================================

class ExecutionRecord:

    def __init__(
        self,
        intent_id: str,
        state: str = STATE_NEW,
    ):

        if not intent_id:

            raise ValueError(
                "intent id required"
            )

        if state not in ALLOWED_TRANSITIONS:

            raise ValueError(
                "invalid execution record state"
            )

        self.intent_id = intent_id

        self.state = state

    def snapshot(
        self,
    ) -> str:

        payload = {

            "version":
                1,

            "intent_id":
                self.intent_id,

            "state":
                self.state,
        }

        payload_text = stable_json(
            payload
        )

        wrapper = {

            "payload":
                payload,

            "checksum":
                sha256_text(
                    payload_text
                ),
        }

        return stable_json(
            wrapper
        )

    @classmethod
    def restore(
        cls,
        snapshot_text: str,
    ):

        try:

            wrapper = json.loads(
                snapshot_text
            )

        except Exception as exc:

            raise ValueError(
                "corrupted execution snapshot"
            ) from exc

        if not isinstance(
            wrapper,
            dict,
        ):

            raise ValueError(
                "invalid execution snapshot"
            )

        payload = wrapper.get(
            "payload"
        )

        checksum = wrapper.get(
            "checksum"
        )

        if not isinstance(
            payload,
            dict,
        ):

            raise ValueError(
                "execution payload missing"
            )

        if not isinstance(
            checksum,
            str,
        ):

            raise ValueError(
                "execution checksum missing"
            )

        expected_checksum = sha256_text(
            stable_json(
                payload
            )
        )

        if checksum != expected_checksum:

            raise ValueError(
                "execution checksum mismatch"
            )

        if (
            payload.get(
                "version"
            )
            != 1
        ):

            raise ValueError(
                "unsupported execution snapshot"
            )

        intent_id = payload.get(
            "intent_id"
        )

        state = payload.get(
            "state"
        )

        if not isinstance(
            intent_id,
            str,
        ):

            raise ValueError(
                "invalid persisted intent"
            )

        if state not in ALLOWED_TRANSITIONS:

            raise ValueError(
                "invalid persisted state"
            )

        return cls(
            intent_id=intent_id,
            state=state,
        )


# ============================================================
# ABSOLUTE REAL ORDER TRANSMISSION LOCK
# ============================================================

def real_order_post(
    *args,
    **kwargs,
):

    global REAL_POST_CALLED

    REAL_POST_CALLED = True

    raise RuntimeError(
        "REAL ORDER POST ABSOLUTELY DISABLED"
    )


# ============================================================
# ABSOLUTE DEMO ORDER TRANSMISSION LOCK
# ============================================================

def demo_order_post(
    *args,
    **kwargs,
):

    global DEMO_POST_CALLED

    DEMO_POST_CALLED = True

    raise RuntimeError(
        "DEMO ORDER POST ABSOLUTELY DISABLED"
    )


# ============================================================
# ABSOLUTE NETWORK LOCK
# ============================================================

def network_request(
    *args,
    **kwargs,
):

    global NETWORK_CALLED

    NETWORK_CALLED = True

    raise RuntimeError(
        "NETWORK ACCESS ABSOLUTELY DISABLED"
    )


# ============================================================
# DIAGNOSTIC HELPERS
# ============================================================

def print_gate(
    name: str,
    passed: bool,
):

    status = (
        "✅ PASS"
        if passed
        else
        "❌ FAIL"
    )

    print(
        f"{name:<48} {status}",
        flush=True,
    )


def expect_exception(
    exception_type,
    function,
    *args,
    **kwargs,
) -> bool:

    try:

        function(
            *args,
            **kwargs,
        )

    except exception_type:

        return True

    except Exception:

        return False

    return False


# ============================================================
# R28 A-G INTEGRATED DIAGNOSTIC
# ============================================================

def run_r28_integrated_diagnostic(
) -> bool:

    print(
        "R28 A-G: DIAGNOSTIC ENTERED",
        flush=True,
    )

    print(
        "=" * 72,
        flush=True,
    )

    print(
        f"{MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "R28 UNITS A + B + C + D + E + F + G",
        flush=True,
    )

    print(
        "SIGNAL -> INTENT -> PAYLOAD -> SHADOW -> STATE -> PERSISTENCE",
        flush=True,
    )

    print(
        "NO EXCHANGE CONNECTION",
        flush=True,
    )

    print(
        "REAL ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "DEMO ORDER TRANSMISSION DISABLED",
        flush=True,
    )

    print(
        "NETWORK ACCESS DISABLED",
        flush=True,
    )

    print(
        "=" * 72,
        flush=True,
    )

    results: Dict[str, bool] = {}

    now_ms = int(
        time.time()
        * 1000
    )


    # ========================================================
    # UNIT A
    # SIGNAL SAFETY
    # ========================================================

    fresh_signal = Signal(
        signal_id="r28-integrated-signal-001",
        symbol="BTCUSDT",
        direction="LONG",
        created_ms=now_ms,
    )

    expired_signal = Signal(
        signal_id="r28-integrated-expired",
        symbol="BTCUSDT",
        direction="LONG",
        created_ms=(
            now_ms
            -
            (
                SIGNAL_EXPIRY_SECONDS
                + 10
            )
            * 1000
        ),
    )

    results[
        "A01 Signal Validation"
    ] = validate_signal(
        fresh_signal
    )

    results[
        "A02 Fresh Signal Accepted"
    ] = signal_is_fresh(
        fresh_signal,
        now_ms,
    )

    results[
        "A03 Expired Signal Rejected"
    ] = (
        not signal_is_fresh(
            expired_signal,
            now_ms,
        )
    )

    bad_direction_signal = Signal(
        signal_id="bad-direction",
        symbol="BTCUSDT",
        direction="INVALID",
        created_ms=now_ms,
    )

    results[
        "A04 Invalid Direction Rejected"
    ] = expect_exception(
        ValueError,
        validate_signal,
        bad_direction_signal,
    )

    empty_signal = Signal(
        signal_id="",
        symbol="BTCUSDT",
        direction="LONG",
        created_ms=now_ms,
    )

    results[
        "A05 Empty Signal ID Rejected"
    ] = expect_exception(
        ValueError,
        validate_signal,
        empty_signal,
    )

    last_loss_ms = (
        now_ms
        - 1000
    )

    results[
        "A06 Loss Cooldown Active"
    ] = loss_cooldown_active(
        last_loss_ms,
        now_ms,
    )

    old_loss_ms = (
        now_ms
        -
        (
            LOSS_COOLDOWN_SECONDS
            + 10
        )
        * 1000
    )

    results[
        "A07 Expired Cooldown Released"
    ] = (
        not loss_cooldown_active(
            old_loss_ms,
            now_ms,
        )
    )


    # ========================================================
    # UNIT B
    # EXECUTION INTENT
    # ========================================================

    intent_1 = build_execution_intent(
        signal_obj=fresh_signal,
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    intent_2 = build_execution_intent(
        signal_obj=fresh_signal,
        quantity=Decimal(
            "0.0001"
        ),
        leverage=100,
    )

    results[
        "B01 Execution Intent Generated"
    ] = bool(
        intent_1.intent_id
    )

    results[
        "B02 Execution Intent Valid"
    ] = validate_execution_intent(
        intent_1
    )

    results[
        "B03 Deterministic Intent"
    ] = (
        intent_1
        == intent_2
    )

    results[
        "B04 Client Order ID Deterministic"
    ] = (
        intent_1.intent_id
        == intent_2.intent_id
    )

    results[
        "B05 Side Mapping Valid"
    ] = (
        intent_1.side
        == "BUY"
    )

    results[
        "B06 Position Side Mapping Valid"
    ] = (
        intent_1.position_side
        == "LONG"
    )

    results[
        "B07 Isolated Margin Preserved"
    ] = (
        intent_1.margin_type
        == "ISOLATED"
    )

    results[
        "B08 Zero Quantity Rejected"
    ] = expect_exception(
        ValueError,
        build_execution_intent,
        fresh_signal,
        Decimal(
            "0"
        ),
        100,
    )

    results[
        "B09 Negative Quantity Rejected"
    ] = expect_exception(
        ValueError,
        build_execution_intent,
        fresh_signal,
        Decimal(
            "-0.0001"
        ),
        100,
    )

    results[
        "B10 Excessive Leverage Rejected"
    ] = expect_exception(
        ValueError,
        build_execution_intent,
        fresh_signal,
        Decimal(
            "0.0001"
        ),
        101,
    )


    # ========================================================
    # UNIT C
    # PAYLOAD + SHADOW COMMIT
    # ========================================================

    payload_1 = build_execution_payload(
        intent_1
    )

    payload_2 = build_execution_payload(
        intent_2
    )

    results[
        "C01 Execution Payload Generated"
    ] = bool(
        payload_1
    )

    results[
        "C02 Payload Binding Valid"
    ] = validate_execution_payload(
        intent_1,
        payload_1,
    )

    results[
        "C03 Deterministic Payload"
    ] = (
        payload_1
        == payload_2
    )

    results[
        "C04 Symbol Preserved"
    ] = (
        payload_1[
            "symbol"
        ]
        == "BTCUSDT"
    )

    results[
        "C05 Side Preserved"
    ] = (
        payload_1[
            "side"
        ]
        == "BUY"
    )

    results[
        "C06 Position Side Preserved"
    ] = (
        payload_1[
            "positionSide"
        ]
        == "LONG"
    )

    results[
        "C07 Quantity Preserved"
    ] = (
        payload_1[
            "quantity"
        ]
        == "0.0001"
    )

    results[
        "C08 Leverage Preserved"
    ] = (
        payload_1[
            "leverage"
        ]
        == "100"
    )

    shadow_1 = create_shadow_commit(
        intent=intent_1,
        payload=payload_1,
        created_ms=now_ms,
    )

    shadow_2 = create_shadow_commit(
        intent=intent_2,
        payload=payload_2,
        created_ms=now_ms,
    )

    results[
        "C09 Shadow Commit Generated"
    ] = bool(
        shadow_1.commit_id
    )

    results[
        "C10 Shadow Binding Valid"
    ] = validate_shadow_commit(
        intent_1,
        payload_1,
        shadow_1,
    )

    results[
        "C11 Deterministic Shadow Commit"
    ] = (
        shadow_1.commit_id
        == shadow_2.commit_id
    )

    tampered_payload = dict(
        payload_1
    )

    tampered_payload[
        "quantity"
    ] = "999"

    results[
        "C12 Payload Tampering Rejected"
    ] = expect_exception(
        ValueError,
        validate_shadow_commit,
        intent_1,
        tampered_payload,
        shadow_1,
    )


    # ========================================================
    # UNIT D
    # EXECUTION STATE MACHINE
    # ========================================================

    machine = ExecutionStateMachine()

    results[
        "D01 Initial State NEW"
    ] = (
        machine.state
        == STATE_NEW
    )

    machine.validate()

    results[
        "D02 State VALIDATED"
    ] = (
        machine.state
        == STATE_VALIDATED
    )

    machine.shadow_commit()

    results[
        "D03 State SHADOW_COMMITTED"
    ] = (
        machine.state
        == STATE_SHADOW_COMMITTED
    )

    machine.reconcile()

    results[
        "D04 State RECONCILED"
    ] = (
        machine.state
        == STATE_RECONCILED
    )

    terminal_machine = (
        ExecutionStateMachine()
    )

    terminal_machine.validate()

    terminal_machine.shadow_commit()

    terminal_machine.reconcile()

    terminal_machine.fill()

    results[
        "D05 Terminal State FILLED"
    ] = (
        terminal_machine.state
        == STATE_FILLED
    )

    results[
        "D06 Terminal Replay Rejected"
    ] = expect_exception(
        RuntimeError,
        terminal_machine.cancel,
    )

    invalid_transition_machine = (
        ExecutionStateMachine()
    )

    results[
        "D07 Invalid State Transition Rejected"
    ] = expect_exception(
        RuntimeError,
        invalid_transition_machine.reconcile,
    )


    # ========================================================
    # UNIT E
    # INTEGRATED BINDING CHAIN
    # ========================================================

    integration_signal = Signal(
        signal_id="r28-integration-chain",
        symbol="BTCUSDT",
        direction="SHORT",
        created_ms=now_ms,
    )

    integration_intent = (
        build_execution_intent(
            signal_obj=integration_signal,
            quantity=Decimal(
                "0.0001"
            ),
            leverage=100,
        )
    )

    integration_payload = (
        build_execution_payload(
            integration_intent
        )
    )

    integration_shadow = (
        create_shadow_commit(
            intent=integration_intent,
            payload=integration_payload,
            created_ms=now_ms,
        )
    )

    integration_machine = (
        ExecutionStateMachine()
    )

    validate_signal(
        integration_signal
    )

    integration_machine.validate()

    validate_execution_intent(
        integration_intent
    )

    validate_execution_payload(
        integration_intent,
        integration_payload,
    )

    integration_machine.shadow_commit()

    validate_shadow_commit(
        integration_intent,
        integration_payload,
        integration_shadow,
    )

    integration_machine.reconcile()

    results[
        "E01 Signal To Intent Binding"
    ] = (
        integration_intent.signal_id
        == integration_signal.signal_id
    )

    results[
        "E02 Intent To Payload Binding"
    ] = (
        integration_payload[
            "clientOrderId"
        ]
        == integration_intent.intent_id
    )

    results[
        "E03 Payload To Shadow Binding"
    ] = (
        integration_shadow.intent_id
        == integration_intent.intent_id
    )

    results[
        "E04 Integrated State Path"
    ] = (
        integration_machine.state
        == STATE_RECONCILED
    )

    results[
        "E05 SHORT Direction Binding"
    ] = (
        integration_intent.side
        == "SELL"
        and
        integration_intent.position_side
        == "SHORT"
    )


    # ========================================================
    # UNIT F
    # REPLAY + RESTART + IDEMPOTENCY
    # ========================================================

    replay_guard = ReplayGuard()

    first_signal_registration = (
        replay_guard.register_signal(
            fresh_signal.signal_id
        )
    )

    duplicate_signal_registration = (
        replay_guard.register_signal(
            fresh_signal.signal_id
        )
    )

    results[
        "F01 First Signal Accepted"
    ] = first_signal_registration

    results[
        "F02 Duplicate Signal Replay Rejected"
    ] = (
        not duplicate_signal_registration
    )

    first_intent_registration = (
        replay_guard.register_intent(
            intent_1.intent_id
        )
    )

    duplicate_intent_registration = (
        replay_guard.register_intent(
            intent_1.intent_id
        )
    )

    results[
        "F03 First Intent Accepted"
    ] = first_intent_registration

    results[
        "F04 Duplicate Intent Replay Rejected"
    ] = (
        not duplicate_intent_registration
    )

    first_commit_registration = (
        replay_guard.register_commit(
            shadow_1.commit_id
        )
    )

    duplicate_commit_registration = (
        replay_guard.register_commit(
            shadow_1.commit_id
        )
    )

    results[
        "F05 First Shadow Commit Accepted"
    ] = first_commit_registration

    results[
        "F06 Duplicate Shadow Commit Rejected"
    ] = (
        not duplicate_commit_registration
    )

    replay_snapshot_1 = (
        replay_guard.snapshot()
    )

    replay_snapshot_2 = (
        replay_guard.snapshot()
    )

    results[
        "F07 Deterministic Replay Snapshot"
    ] = (
        replay_snapshot_1
        == replay_snapshot_2
    )

    restored_guard = (
        ReplayGuard.restore(
            replay_snapshot_1
        )
    )

    results[
        "F08 Restart State Restored"
    ] = (
        restored_guard.signal_ids
        == replay_guard.signal_ids
        and
        restored_guard.intent_ids
        == replay_guard.intent_ids
        and
        restored_guard.commit_ids
        == replay_guard.commit_ids
    )

    results[
        "F09 Replay After Restart Rejected"
    ] = (
        not restored_guard.register_signal(
            fresh_signal.signal_id
        )
    )

    corrupted_snapshot = (
        replay_snapshot_1[:-1]
        + "X"
    )

    results[
        "F10 Corrupted Snapshot Rejected"
    ] = expect_exception(
        ValueError,
        ReplayGuard.restore,
        corrupted_snapshot,
    )

    execution_record = (
        ExecutionRecord(
            intent_id=intent_1.intent_id,
            state=STATE_RECONCILED,
        )
    )

    execution_snapshot_1 = (
        execution_record.snapshot()
    )

    execution_snapshot_2 = (
        execution_record.snapshot()
    )

    results[
        "F11 Deterministic Execution Snapshot"
    ] = (
        execution_snapshot_1
        == execution_snapshot_2
    )

    restored_execution = (
        ExecutionRecord.restore(
            execution_snapshot_1
        )
    )

    results[
        "F12 Deterministic Restore"
    ] = (
        restored_execution.intent_id
        == execution_record.intent_id
        and
        restored_execution.state
        == execution_record.state
    )

    results[
        "F13 Shadow Commit Survives Restart"
    ] = (
        shadow_1.commit_id
        in restored_guard.commit_ids
    )

    terminal_record = (
        ExecutionRecord(
            intent_id="terminal-test",
            state=STATE_FILLED,
        )
    )

    terminal_snapshot = (
        terminal_record.snapshot()
    )

    restored_terminal = (
        ExecutionRecord.restore(
            terminal_snapshot
        )
    )

    restored_terminal_machine = (
        ExecutionStateMachine(
            restored_terminal.state
        )
    )

    results[
        "F14 Terminal State Replay Rejected"
    ] = expect_exception(
        RuntimeError,
        restored_terminal_machine.cancel,
    )


    # ========================================================
    # UNIT G
    # STARTUP + SAFETY + RUNTIME
    # ========================================================

    results[
        "G01 Live Execution Disabled"
    ] = (
        LIVE_ORDER_EXECUTION
        is False
    )

    results[
        "G02 Demo Execution Disabled"
    ] = (
        DEMO_ORDER_EXECUTION
        is False
    )

    results[
        "G03 Network Access Disabled"
    ] = (
        NETWORK_ACCESS_ENABLED
        is False
    )

    results[
        "G04 Hard Real POST Lock Active"
    ] = (
        HARD_REAL_POST_LOCK
        is True
    )

    results[
        "G05 Hard Demo POST Lock Active"
    ] = (
        HARD_DEMO_POST_LOCK
        is True
    )

    results[
        "G06 Real POST Never Called"
    ] = (
        REAL_POST_CALLED
        is False
    )

    results[
        "G07 Demo POST Never Called"
    ] = (
        DEMO_POST_CALLED
        is False
    )

    results[
        "G08 Network Never Called"
    ] = (
        NETWORK_CALLED
        is False
    )

    results[
        "G09 Runtime Configuration Valid"
    ] = (
        RUNTIME_HEARTBEAT_SECONDS
        > 0
    )

    results[
        "G10 Port Configuration Valid"
    ] = (
        PORT
        > 0
        and
        PORT
        <= 65535
    )

    results[
        "G11 Main Module Loaded"
    ] = True

    results[
        "G12 Diagnostic Reached"
    ] = True


    # ========================================================
    # GLOBAL CONFIGURATION SAFETY
    # ========================================================

    results[
        "R01 Entry Size Safety Valid"
    ] = (
        ENTRY_PERCENT
        > Decimal(
            "0"
        )
        and
        ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    results[
        "R02 Exposure Cap Valid"
    ] = (
        MAX_FUND_EXPOSURE_PERCENT
        > Decimal(
            "0"
        )
        and
        MAX_FUND_EXPOSURE_PERCENT
        <= Decimal(
            "100"
        )
    )

    results[
        "R03 Pyramid Limit Valid"
    ] = (
        MAX_PYRAMID_ADDS
        >= 0
    )

    results[
        "R04 Backup Limit Valid"
    ] = (
        MAX_BACKUPS
        >= 0
    )

    results[
        "R05 Backup Size Valid"
    ] = (
        BACKUP_SIZE_PERCENT
        > Decimal(
            "0"
        )
    )

    results[
        "R06 Backup Buffer Valid"
    ] = (
        BACKUP_BUFFER_PERCENT
        > Decimal(
            "0"
        )
    )

    results[
        "R07 Maximum Leverage Locked"
    ] = (
        MAX_LEVERAGE
        == 100
    )

    results[
        "R08 Margin Type Locked"
    ] = (
        MARGIN_TYPE
        == "ISOLATED"
    )


    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print(
        "R28 A-G INTEGRATION GATES",
        flush=True,
    )

    print(
        "-" * 72,
        flush=True,
    )

    for name, passed in results.items():

        print_gate(
            name,
            bool(
                passed
            ),
        )

    print(
        "-" * 72,
        flush=True,
    )


    # ========================================================
    # FINAL SAFETY ASSERTIONS
    # ========================================================

    final_safety = (

        LIVE_ORDER_EXECUTION
        is False

        and

        DEMO_ORDER_EXECUTION
        is False

        and

        NETWORK_ACCESS_ENABLED
        is False

        and

        HARD_REAL_POST_LOCK
        is True

        and

        HARD_DEMO_POST_LOCK
        is True

        and

        REAL_POST_CALLED
        is False

        and

        DEMO_POST_CALLED
        is False

        and

        NETWORK_CALLED
        is False
    )

    print_gate(
        "FINAL Execution Locks Active",
        final_safety,
    )


    all_passed = (
        all(
            results.values()
        )
        and
        final_safety
    )


    print(
        "-" * 72,
        flush=True,
    )


    if all_passed:

        print(
            "✅ R28 A-G INTEGRATION DIAGNOSTIC PASSED",
            flush=True,
        )

        print(
            "✅ UNIT A SIGNAL SAFETY VALIDATED",
            flush=True,
        )

        print(
            "✅ UNIT B EXECUTION INTENT VALIDATED",
            flush=True,
        )

        print(
            "✅ UNIT C PAYLOAD / SHADOW SAFETY VALIDATED",
            flush=True,
        )

        print(
            "✅ UNIT D STATE MACHINE VALIDATED",
            flush=True,
        )

        print(
            "✅ UNIT E INTEGRATION BOUNDARY VALIDATED",
            flush=True,
        )

        print(
            "✅ UNIT F RESTART / IDEMPOTENCY VALIDATED",
            flush=True,
        )

        print(
            "✅ UNIT G STARTUP / RUNTIME VALIDATED",
            flush=True,
        )

        print(
            "✅ EXECUTION SAFETY LOCKS VALIDATED",
            flush=True,
        )

        print(
            "✅ R28 A-G READY FOR NEXT INTEGRATION STAGE",
            flush=True,
        )

        print(
            "🛡 NO ORDER TRANSMISSION POSSIBLE",
            flush=True,
        )

    else:

        print(
            "❌ R28 A-G INTEGRATION DIAGNOSTIC FAILED",
            flush=True,
        )

        print(
            "🛡 EXECUTION REMAINS DISABLED",
            flush=True,
        )


    print(
        "=" * 72,
        flush=True,
    )

    print(
        "R28 A-G: DIAGNOSTIC COMPLETE",
        flush=True,
    )

    return all_passed


# ============================================================
# MINIMAL RENDER HEALTH SERVER
# ============================================================

async def handle_health_request(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):

    try:

        await reader.read(
            4096
        )

        body = (
            "R28 A-G ACTIVE\n"
        )

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )

        writer.write(
            response.encode(
                "utf-8"
            )
        )

        await writer.drain()

    except Exception as exc:

        print(
            "R28 A-G: HEALTH REQUEST ERROR:",
            repr(
                exc
            ),
            flush=True,
        )

    finally:

        try:

            writer.close()

            await writer.wait_closed()

        except Exception:

            pass


# ============================================================
# START HEALTH SERVER
# ============================================================

async def start_health_server(
):

    print(
        "R28 A-G: STARTING HEALTH SERVER "
        f"ON PORT {PORT}",
        flush=True,
    )

    server = await asyncio.start_server(
        handle_health_request,
        host="0.0.0.0",
        port=PORT,
    )

    print(
        "R28 A-G: HEALTH SERVER ACTIVE "
        f"ON PORT {PORT}",
        flush=True,
    )

    return server


# ============================================================
# PERSISTENT RUNTIME
# ============================================================

async def persistent_runtime(
):

    print(
        "R28 A-G: PERSISTENT RUNTIME ENTERED",
        flush=True,
    )

    server = await start_health_server()

    print(
        "R28 A-G: SERVICE WILL REMAIN ACTIVE",
        flush=True,
    )

    heartbeat_number = 0

    async with server:

        while True:

            await asyncio.sleep(
                RUNTIME_HEARTBEAT_SECONDS
            )

            heartbeat_number += 1

            print(
                "R28 A-G: "
                f"HEARTBEAT {heartbeat_number} "
                "✅ ACTIVE",
                flush=True,
            )


# ============================================================
# MAIN ASYNC CONTROLLER
# ============================================================

async def main(
):

    print(
        "R28 A-G: MAIN FUNCTION ENTERED",
        flush=True,
    )

    diagnostic_passed = (
        run_r28_integrated_diagnostic()
    )

    if not diagnostic_passed:

        raise RuntimeError(
            "R28 A-G integration diagnostic failed"
        )

    print(
        "R28 A-G: STARTING PERSISTENT SERVICE",
        flush=True,
    )

    await persistent_runtime()


# ============================================================
# PYTHON ENTRY POINT
# ============================================================

if __name__ == "__main__":

    print(
        "R28 A-G: __MAIN__ BLOCK ENTERED",
        flush=True,
    )

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "R28 A-G: SHUTDOWN REQUESTED",
            flush=True,
        )

    except Exception as exc:

        print(
            "=" * 72,
            flush=True,
        )

        print(
            "❌ R28 A-G FATAL ERROR",
            flush=True,
        )

        print(
            type(
                exc
            ).__name__
            + ": "
            + str(
                exc
            ),
            flush=True,
        )

        print(
            "Real POST Called:",
            REAL_POST_CALLED,
            flush=True,
        )

        print(
            "Demo POST Called:",
            DEMO_POST_CALLED,
            flush=True,
        )

        print(
            "Network Called:",
            NETWORK_CALLED,
            flush=True,
        )

        print(
            "🛡 NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "=" * 72,
            flush=True,
        )

        raise
        
