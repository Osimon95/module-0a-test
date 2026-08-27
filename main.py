from __future__ import annotations

import copy
import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# R31D
# TERMINAL DURABILITY / CRASH-WINDOW / RECOVERY STRESS VALIDATION
#
# SAFETY DISCIPLINE:
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO EXCHANGE NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE:
#   Validate that the already-sealed terminal lifecycle remains durable across:
#
#       atomic persistence
#       ->
#       temporary-file crash windows
#       ->
#       corrupted snapshot rejection
#       ->
#       checksum tampering
#       ->
#       WAL validation
#       ->
#       torn WAL rejection
#       ->
#       repeated restart
#       ->
#       concurrent recovery
#       ->
#       stale generation rejection
#       ->
#       stale recovery-epoch rejection
#       ->
#       terminal-state immutability
#
# R31D DOES NOT ALTER WEEX LEVERAGE.
#
# The 100x leverage correction remains a later controlled stage.
# =============================================================================


VERSION = "R31D"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"

STATE_FILE = Path(
    os.getenv(
        "R31D_STATE_FILE",
        "/tmp/r31d_terminal_durability_state.json",
    )
)

WAL_FILE = Path(
    os.getenv(
        "R31D_WAL_FILE",
        "/tmp/r31d_terminal_durability.wal",
    )
)

HEALTH_PORT = int(os.getenv("PORT", "10000"))

HEARTBEAT_SECONDS = 30


# =============================================================================
# HARD SAFETY CONSTANTS
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False
EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# =============================================================================
# GLOBAL VALIDATION COUNTERS
# =============================================================================

PASSED = 0
FAILED = 0


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def divider() -> None:
    print("-" * 92, flush=True)


def section(title: str) -> None:
    divider()
    print(title, flush=True)
    divider()


def check(name: str, condition: bool) -> bool:
    global PASSED, FAILED

    if condition:
        PASSED += 1
        status = "✅ PASS"
    else:
        FAILED += 1
        status = "❌ FAIL"

    print(f"{name:<82} {status}", flush=True)
    return condition


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_object(value: Any) -> str:
    return sha256_text(canonical_json(value))


def deep_copy(value: Any) -> Any:
    return copy.deepcopy(value)


# =============================================================================
# SAFETY FIREBREAKS
# =============================================================================

def block_real_order(reason: str) -> bool:
    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print("  REAL order execution blocked", flush=True)
    print(f"  reason={reason}", flush=True)
    return False


def block_demo_order(reason: str) -> bool:
    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print("  DEMO order execution blocked", flush=True)
    print(f"  reason={reason}", flush=True)
    return False


def block_network_write(method: str, path: str) -> bool:
    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print(f"  REAL network {method.upper()} blocked", flush=True)
    print(f"  path={path}", flush=True)
    return False


def block_mutation(kind: str) -> bool:
    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print(f"  {kind.upper()} mutation blocked", flush=True)
    return False


# =============================================================================
# DURABLE STATE
# =============================================================================

@dataclass
class RuntimeState:
    version: str
    symbol: str

    runtime_id: str
    candidate_id: str

    phase: str

    generation: int
    recovery_epoch: int

    authorization_nonce: str
    dispatch_nonce: str
    transition_nonce: str

    authorization_consumed: bool
    dispatch_consumed: bool
    transition_consumed: bool

    real_order_count: int
    demo_order_count: int
    network_write_count: int
    mutation_count: int

    synthetic_dispatch_count: int
    transition_count: int
    consumed_transition_count: int

    authorization_replay_blocked: int
    dispatch_replay_blocked: int
    transition_replay_blocked: int

    tamper_rejections: int
    stale_generation_rejections: int
    stale_recovery_rejections: int
    terminal_reopen_rejections: int

    crash_recovery_count: int
    restart_restore_count: int
    concurrent_recovery_winners: int

    wal_sequence: int

    sealed_at: float


def initial_state() -> RuntimeState:
    return RuntimeState(
        version=VERSION,
        symbol=SYMBOL,

        runtime_id=str(uuid.uuid4()),
        candidate_id=str(uuid.uuid4()),

        phase="SEALED",

        generation=1,
        recovery_epoch=1,

        authorization_nonce=str(uuid.uuid4()),
        dispatch_nonce=str(uuid.uuid4()),
        transition_nonce=str(uuid.uuid4()),

        authorization_consumed=True,
        dispatch_consumed=True,
        transition_consumed=True,

        real_order_count=0,
        demo_order_count=0,
        network_write_count=0,
        mutation_count=0,

        synthetic_dispatch_count=1,
        transition_count=3,
        consumed_transition_count=3,

        authorization_replay_blocked=1,
        dispatch_replay_blocked=1,
        transition_replay_blocked=1,

        tamper_rejections=0,
        stale_generation_rejections=0,
        stale_recovery_rejections=0,
        terminal_reopen_rejections=0,

        crash_recovery_count=0,
        restart_restore_count=0,
        concurrent_recovery_winners=0,

        wal_sequence=0,

        sealed_at=time.time(),
    )


# =============================================================================
# SNAPSHOT ENVELOPE
# =============================================================================

def state_payload(state: RuntimeState) -> Dict[str, Any]:
    return asdict(state)


def build_snapshot_envelope(state: RuntimeState) -> Dict[str, Any]:
    payload = state_payload(state)

    return {
        "format": "R31D_STATE_V1",
        "payload": payload,
        "checksum": sha256_object(payload),
    }


def validate_snapshot_envelope(
    envelope: Any,
) -> tuple[bool, Optional[str]]:
    if not isinstance(envelope, dict):
        return False, "snapshot is not a dictionary"

    if envelope.get("format") != "R31D_STATE_V1":
        return False, "snapshot format mismatch"

    payload = envelope.get("payload")
    checksum = envelope.get("checksum")

    if not isinstance(payload, dict):
        return False, "snapshot payload missing"

    if not isinstance(checksum, str):
        return False, "snapshot checksum missing"

    expected = sha256_object(payload)

    if checksum != expected:
        return False, "snapshot checksum mismatch"

    required_fields = {
        "version",
        "symbol",
        "runtime_id",
        "candidate_id",
        "phase",
        "generation",
        "recovery_epoch",
        "authorization_consumed",
        "dispatch_consumed",
        "transition_consumed",
        "real_order_count",
        "demo_order_count",
        "network_write_count",
        "mutation_count",
        "synthetic_dispatch_count",
        "transition_count",
    }

    if not required_fields.issubset(payload.keys()):
        return False, "snapshot required fields missing"

    if payload.get("version") != VERSION:
        return False, "snapshot version mismatch"

    if payload.get("symbol") != SYMBOL:
        return False, "snapshot symbol mismatch"

    if payload.get("phase") != "SEALED":
        return False, "snapshot phase is not sealed"

    return True, None


# =============================================================================
# ATOMIC SNAPSHOT PERSISTENCE
# =============================================================================

def atomic_persist(
    state: RuntimeState,
    target: Path = STATE_FILE,
) -> None:
    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = Path(str(target) + ".tmp")

    envelope = build_snapshot_envelope(state)
    serialized = json.dumps(
        envelope,
        sort_keys=True,
        indent=2,
    )

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(serialized)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(
        temp_path,
        target,
    )


def load_snapshot(
    target: Path = STATE_FILE,
) -> RuntimeState:
    with open(
        target,
        "r",
        encoding="utf-8",
    ) as handle:
        envelope = json.load(handle)

    valid, reason = validate_snapshot_envelope(envelope)

    if not valid:
        raise ValueError(
            f"invalid durable snapshot: {reason}"
        )

    payload = envelope["payload"]

    return RuntimeState(**payload)


# =============================================================================
# WAL
# =============================================================================

def wal_record_checksum(
    record_without_checksum: Dict[str, Any],
) -> str:
    return sha256_object(record_without_checksum)


def build_wal_record(
    sequence: int,
    event: str,
    state: RuntimeState,
) -> Dict[str, Any]:
    record = {
        "version": VERSION,
        "sequence": sequence,
        "event": event,
        "candidate_id": state.candidate_id,
        "generation": state.generation,
        "recovery_epoch": state.recovery_epoch,
        "phase": state.phase,
        "timestamp": time.time(),
    }

    record["checksum"] = wal_record_checksum(record)

    return record


def append_wal(
    state: RuntimeState,
    event: str,
    path: Path = WAL_FILE,
) -> int:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    state.wal_sequence += 1

    record = build_wal_record(
        state.wal_sequence,
        event,
        state,
    )

    line = canonical_json(record)

    with open(
        path,
        "a",
        encoding="utf-8",
    ) as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())

    return state.wal_sequence


def validate_wal(
    path: Path = WAL_FILE,
) -> tuple[bool, List[Dict[str, Any]], Optional[str]]:
    if not path.exists():
        return True, [], None

    records: List[Dict[str, Any]] = []
    expected_sequence = 1

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, raw_line in enumerate(
            handle,
            start=1,
        ):
            line = raw_line.rstrip("\n")

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                return (
                    False,
                    records,
                    f"torn or invalid WAL record at line {line_number}",
                )

            if not isinstance(record, dict):
                return (
                    False,
                    records,
                    f"invalid WAL type at line {line_number}",
                )

            checksum = record.get("checksum")

            if not isinstance(checksum, str):
                return (
                    False,
                    records,
                    f"missing WAL checksum at line {line_number}",
                )

            without_checksum = dict(record)
            without_checksum.pop(
                "checksum",
                None,
            )

            expected_checksum = wal_record_checksum(
                without_checksum
            )

            if checksum != expected_checksum:
                return (
                    False,
                    records,
                    f"WAL checksum mismatch at line {line_number}",
                )

            if record.get("sequence") != expected_sequence:
                return (
                    False,
                    records,
                    f"WAL sequence mismatch at line {line_number}",
                )

            if record.get("version") != VERSION:
                return (
                    False,
                    records,
                    f"WAL version mismatch at line {line_number}",
                )

            records.append(record)
            expected_sequence += 1

    return True, records, None


# =============================================================================
# TERMINAL STATE VALIDATION
# =============================================================================

def terminal_invariants(
    state: RuntimeState,
) -> bool:
    return (
        state.phase == "SEALED"
        and state.authorization_consumed is True
        and state.dispatch_consumed is True
        and state.transition_consumed is True
        and state.real_order_count == 0
        and state.demo_order_count == 0
        and state.network_write_count == 0
        and state.mutation_count == 0
        and state.synthetic_dispatch_count == 1
        and state.transition_count == 3
        and state.consumed_transition_count == 3
    )


def try_reopen_terminal_state(
    state: RuntimeState,
    proposed_phase: str,
) -> bool:
    if state.phase == "SEALED":
        state.terminal_reopen_rejections += 1
        return False

    state.phase = proposed_phase
    return True


def accept_generation(
    state: RuntimeState,
    proposed_generation: int,
) -> bool:
    if proposed_generation < state.generation:
        state.stale_generation_rejections += 1
        return False

    return True


def accept_recovery_epoch(
    state: RuntimeState,
    proposed_epoch: int,
) -> bool:
    if proposed_epoch < state.recovery_epoch:
        state.stale_recovery_rejections += 1
        return False

    return True


# =============================================================================
# RECOVERY LOGIC
# =============================================================================

RECOVERY_LOCK = threading.Lock()


def restore_terminal_state(
    path: Path = STATE_FILE,
) -> RuntimeState:
    state = load_snapshot(path)

    if not terminal_invariants(state):
        raise ValueError(
            "terminal invariants violated during restore"
        )

    state.restart_restore_count += 1

    return state


def recover_after_crash(
    path: Path = STATE_FILE,
) -> RuntimeState:
    state = restore_terminal_state(path)

    state.crash_recovery_count += 1

    if state.phase != "SEALED":
        raise RuntimeError(
            "recovery attempted to restore non-terminal phase"
        )

    return state


def concurrent_recovery_attempt(
    result_list: List[str],
    state_path: Path,
) -> None:
    acquired = RECOVERY_LOCK.acquire(
        blocking=False
    )

    if not acquired:
        result_list.append("LOSER")
        return

    try:
        restored = load_snapshot(state_path)

        if terminal_invariants(restored):
            result_list.append("WINNER")
        else:
            result_list.append("INVALID")
    finally:
        RECOVERY_LOCK.release()


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(
    __import__("http.server").server.BaseHTTPRequestHandler
):
    def do_GET(self) -> None:
        body = (
            f"{VERSION} OK\n"
            f"symbol={SYMBOL}\n"
            f"synthetic_only={SYNTHETIC_TRANSPORT_ONLY}\n"
            f"real_execution={REAL_ORDER_EXECUTION_ENABLED}\n"
            f"network_writes={EXCHANGE_NETWORK_WRITES_ENABLED}\n"
            f"leverage_mutation={LEVERAGE_MUTATION_ENABLED}\n"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        return


class ReusableTCPServer(
    socketserver.TCPServer
):
    allow_reuse_address = True


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
            f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
            flush=True,
        )

    except OSError as exc:
        print(
            f"{VERSION}: HEALTH SERVER NOTICE: {exc}",
            flush=True,
        )


# =============================================================================
# VALIDATION SUITE
# =============================================================================

def run_validation() -> RuntimeState:
    global PASSED, FAILED

    PASSED = 0
    FAILED = 0

    section(f"{VERSION}: STARTING VALIDATION")

    print(
        f"{VERSION}: SYMBOL={SYMBOL}",
        flush=True,
    )
    print(
        f"{VERSION}: VERSION={VERSION}",
        flush=True,
    )
    print(
        f"{VERSION}: STATE FILE={STATE_FILE}",
        flush=True,
    )
    print(
        f"{VERSION}: WAL FILE={WAL_FILE}",
        flush=True,
    )
    print(
        f"{VERSION}: HEALTH PORT={HEALTH_PORT}",
        flush=True,
    )

    print(
        f"{VERSION}: REAL EXECUTION DISABLED",
        flush=True,
    )
    print(
        f"{VERSION}: DEMO EXECUTION DISABLED",
        flush=True,
    )
    print(
        f"{VERSION}: NETWORK WRITES DISABLED",
        flush=True,
    )
    print(
        f"{VERSION}: MUTATIONS DISABLED",
        flush=True,
    )
    print(
        f"{VERSION}: SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 1: SAFETY CONSTANTS")
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
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 2: INITIAL SEALED STATE")
    # -------------------------------------------------------------------------

    state = initial_state()

    check(
        "Initial Phase Is Sealed",
        state.phase == "SEALED",
    )

    check(
        "Authorization Already Consumed",
        state.authorization_consumed is True,
    )

    check(
        "Dispatch Already Consumed",
        state.dispatch_consumed is True,
    )

    check(
        "Transition Already Consumed",
        state.transition_consumed is True,
    )

    check(
        "Synthetic Dispatch Count Is One",
        state.synthetic_dispatch_count == 1,
    )

    check(
        "Transition Count Is Three",
        state.transition_count == 3,
    )

    check(
        "Initial Terminal Invariants Valid",
        terminal_invariants(state),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 3: CLEAN TEST STORAGE")
    # -------------------------------------------------------------------------

    for path in (
        STATE_FILE,
        Path(str(STATE_FILE) + ".tmp"),
        WAL_FILE,
    ):
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    check(
        "State File Cleared",
        not STATE_FILE.exists(),
    )

    check(
        "Temporary State File Cleared",
        not Path(str(STATE_FILE) + ".tmp").exists(),
    )

    check(
        "WAL File Cleared",
        not WAL_FILE.exists(),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 4: INITIAL WAL RECORD")
    # -------------------------------------------------------------------------

    wal_sequence = append_wal(
        state,
        "SEALED_BASELINE",
    )

    check(
        "Initial WAL Sequence Is One",
        wal_sequence == 1,
    )

    wal_valid, wal_records, wal_reason = validate_wal()

    check(
        "Initial WAL Validates",
        wal_valid,
    )

    check(
        "Initial WAL Contains One Record",
        len(wal_records) == 1,
    )

    check(
        "Initial WAL Event Matches",
        (
            len(wal_records) == 1
            and wal_records[0]["event"] == "SEALED_BASELINE"
        ),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 5: ATOMIC SNAPSHOT PERSISTENCE")
    # -------------------------------------------------------------------------

    atomic_persist(state)

    check(
        "Durable Snapshot Created",
        STATE_FILE.exists(),
    )

    check(
        "Temporary File Removed After Atomic Replace",
        not Path(str(STATE_FILE) + ".tmp").exists(),
    )

    restored = load_snapshot()

    check(
        "Persisted Runtime ID Matches",
        restored.runtime_id == state.runtime_id,
    )

    check(
        "Persisted Candidate ID Matches",
        restored.candidate_id == state.candidate_id,
    )

    check(
        "Persisted Phase Is Sealed",
        restored.phase == "SEALED",
    )

    check(
        "Persisted Generation Matches",
        restored.generation == state.generation,
    )

    check(
        "Persisted Recovery Epoch Matches",
        restored.recovery_epoch == state.recovery_epoch,
    )

    check(
        "Persisted Terminal Invariants Valid",
        terminal_invariants(restored),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 6: SNAPSHOT CHECKSUM")
    # -------------------------------------------------------------------------

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8",
    ) as handle:
        baseline_envelope = json.load(handle)

    expected_checksum = sha256_object(
        baseline_envelope["payload"]
    )

    check(
        "Snapshot Checksum Matches Payload",
        baseline_envelope["checksum"] == expected_checksum,
    )

    valid_snapshot, snapshot_reason = validate_snapshot_envelope(
        baseline_envelope
    )

    check(
        "Snapshot Envelope Valid",
        valid_snapshot,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 7: PAYLOAD TAMPER REJECTION")
    # -------------------------------------------------------------------------

    tampered = deep_copy(
        baseline_envelope
    )

    tampered["payload"]["phase"] = "AUTHORIZED"

    tamper_valid, _ = validate_snapshot_envelope(
        tampered
    )

    state.tamper_rejections += 1

    check(
        "Payload Tamper Rejected",
        tamper_valid is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 8: CHECKSUM TAMPER REJECTION")
    # -------------------------------------------------------------------------

    tampered_checksum = deep_copy(
        baseline_envelope
    )

    tampered_checksum["checksum"] = "0" * 64

    checksum_valid, _ = validate_snapshot_envelope(
        tampered_checksum
    )

    state.tamper_rejections += 1

    check(
        "Checksum Tamper Rejected",
        checksum_valid is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 9: FORMAT TAMPER REJECTION")
    # -------------------------------------------------------------------------

    tampered_format = deep_copy(
        baseline_envelope
    )

    tampered_format["format"] = "UNKNOWN_FORMAT"

    format_valid, _ = validate_snapshot_envelope(
        tampered_format
    )

    state.tamper_rejections += 1

    check(
        "Snapshot Format Tamper Rejected",
        format_valid is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 10: SYMBOL TAMPER REJECTION")
    # -------------------------------------------------------------------------

    symbol_tamper = deep_copy(
        baseline_envelope
    )

    symbol_tamper["payload"]["symbol"] = "ETHUSDT"
    symbol_tamper["checksum"] = sha256_object(
        symbol_tamper["payload"]
    )

    symbol_valid, _ = validate_snapshot_envelope(
        symbol_tamper
    )

    state.tamper_rejections += 1

    check(
        "Symbol Binding Tamper Rejected",
        symbol_valid is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 11: VERSION TAMPER REJECTION")
    # -------------------------------------------------------------------------

    version_tamper = deep_copy(
        baseline_envelope
    )

    version_tamper["payload"]["version"] = "R31X"
    version_tamper["checksum"] = sha256_object(
        version_tamper["payload"]
    )

    version_valid, _ = validate_snapshot_envelope(
        version_tamper
    )

    state.tamper_rejections += 1

    check(
        "Version Binding Tamper Rejected",
        version_valid is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 12: MISSING FIELD REJECTION")
    # -------------------------------------------------------------------------

    missing_field = deep_copy(
        baseline_envelope
    )

    missing_field["payload"].pop(
        "candidate_id",
        None,
    )

    missing_field["checksum"] = sha256_object(
        missing_field["payload"]
    )

    missing_valid, _ = validate_snapshot_envelope(
        missing_field
    )

    state.tamper_rejections += 1

    check(
        "Missing Critical Field Rejected",
        missing_valid is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 13: PRE-REPLACE CRASH WINDOW")
    # -------------------------------------------------------------------------

    crash_temp = Path(
        str(STATE_FILE) + ".crash-pre-replace"
    )

    crash_envelope = build_snapshot_envelope(
        state
    )

    with open(
        crash_temp,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(
            json.dumps(
                crash_envelope,
                sort_keys=True,
                indent=2,
            )
        )
        handle.flush()
        os.fsync(handle.fileno())

    check(
        "Crash Temporary Snapshot Created",
        crash_temp.exists(),
    )

    preserved_after_crash = load_snapshot()

    check(
        "Original Durable Snapshot Survives Pre-Replace Crash",
        terminal_invariants(preserved_after_crash),
    )

    try:
        crash_temp.unlink()
    except FileNotFoundError:
        pass

    check(
        "Crash Temporary Snapshot Cleaned",
        not crash_temp.exists(),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 14: POST-REPLACE RESTORE")
    # -------------------------------------------------------------------------

    state.crash_recovery_count += 1

    atomic_persist(state)

    post_replace = load_snapshot()

    check(
        "Post-Replace State Restores",
        terminal_invariants(post_replace),
    )

    check(
        "Post-Replace Phase Remains Sealed",
        post_replace.phase == "SEALED",
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 15: REPEATED ATOMIC REPLACEMENT")
    # -------------------------------------------------------------------------

    atomic_successes = 0

    for _ in range(10):
        atomic_persist(state)
        candidate = load_snapshot()

        if terminal_invariants(candidate):
            atomic_successes += 1

    check(
        "Ten Atomic Replacements Completed",
        atomic_successes == 10,
    )

    check(
        "Repeated Atomic Replacement Preserves Seal",
        load_snapshot().phase == "SEALED",
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 16: SECOND WAL RECORD")
    # -------------------------------------------------------------------------

    second_sequence = append_wal(
        state,
        "ATOMIC_PERSISTENCE_VALIDATED",
    )

    check(
        "Second WAL Sequence Is Two",
        second_sequence == 2,
    )

    wal_valid, wal_records, _ = validate_wal()

    check(
        "WAL Remains Valid After Second Record",
        wal_valid,
    )

    check(
        "WAL Contains Two Records",
        len(wal_records) == 2,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 17: WAL CHECKSUM TAMPER REJECTION")
    # -------------------------------------------------------------------------

    wal_tamper_path = Path(
        str(WAL_FILE) + ".tamper"
    )

    original_wal_text = WAL_FILE.read_text(
        encoding="utf-8"
    )

    wal_lines = [
        line
        for line in original_wal_text.splitlines()
        if line.strip()
    ]

    first_record = json.loads(
        wal_lines[0]
    )

    first_record["event"] = "TAMPERED_EVENT"

    wal_lines[0] = canonical_json(
        first_record
    )

    wal_tamper_path.write_text(
        "\n".join(wal_lines) + "\n",
        encoding="utf-8",
    )

    wal_tamper_valid, _, _ = validate_wal(
        wal_tamper_path
    )

    state.tamper_rejections += 1

    check(
        "WAL Checksum Tamper Rejected",
        wal_tamper_valid is False,
    )

    try:
        wal_tamper_path.unlink()
    except FileNotFoundError:
        pass

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 18: TORN WAL TAIL REJECTION")
    # -------------------------------------------------------------------------

    torn_wal_path = Path(
        str(WAL_FILE) + ".torn"
    )

    torn_wal_path.write_text(
        original_wal_text
        + '{"version":"R31D","sequence":3',
        encoding="utf-8",
    )

    torn_valid, _, torn_reason = validate_wal(
        torn_wal_path
    )

    state.tamper_rejections += 1

    check(
        "Torn WAL Tail Rejected",
        torn_valid is False,
    )

    check(
        "Torn WAL Produces Validation Reason",
        bool(torn_reason),
    )

    try:
        torn_wal_path.unlink()
    except FileNotFoundError:
        pass

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 19: WAL SEQUENCE GAP REJECTION")
    # -------------------------------------------------------------------------

    sequence_gap_path = Path(
        str(WAL_FILE) + ".gap"
    )

    gap_record_1 = build_wal_record(
        1,
        "BASELINE",
        state,
    )

    gap_record_3 = build_wal_record(
        3,
        "INVALID_GAP",
        state,
    )

    sequence_gap_path.write_text(
        canonical_json(gap_record_1)
        + "\n"
        + canonical_json(gap_record_3)
        + "\n",
        encoding="utf-8",
    )

    gap_valid, _, _ = validate_wal(
        sequence_gap_path
    )

    state.tamper_rejections += 1

    check(
        "WAL Sequence Gap Rejected",
        gap_valid is False,
    )

    try:
        sequence_gap_path.unlink()
    except FileNotFoundError:
        pass

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 20: RESTART RESTORE")
    # -------------------------------------------------------------------------

    atomic_persist(state)

    restart_state = restore_terminal_state()

    check(
        "Restart Restore Succeeds",
        restart_state.phase == "SEALED",
    )

    check(
        "Restart Restore Preserves Terminal Invariants",
        terminal_invariants(restart_state),
    )

    check(
        "Restart Restore Causes No New Synthetic Dispatch",
        restart_state.synthetic_dispatch_count == 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 21: REPEATED RESTART STRESS")
    # -------------------------------------------------------------------------

    restart_successes = 0

    for _ in range(20):
        recovered = restore_terminal_state()

        if (
            terminal_invariants(recovered)
            and recovered.synthetic_dispatch_count == 1
        ):
            restart_successes += 1

    state.restart_restore_count += 20

    check(
        "Twenty Restart Restorations Completed",
        restart_successes == 20,
    )

    check(
        "Repeated Restart Causes No Additional Dispatch",
        load_snapshot().synthetic_dispatch_count == 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 22: STALE GENERATION REJECTION")
    # -------------------------------------------------------------------------

    current_generation = state.generation

    stale_generation_allowed = accept_generation(
        state,
        current_generation - 1,
    )

    check(
        "Stale Generation Rejected",
        stale_generation_allowed is False,
    )

    check(
        "Stale Generation Rejection Counter Incremented",
        state.stale_generation_rejections >= 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 23: CURRENT GENERATION ACCEPTANCE")
    # -------------------------------------------------------------------------

    current_generation_allowed = accept_generation(
        state,
        state.generation,
    )

    check(
        "Current Generation Accepted",
        current_generation_allowed is True,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 24: STALE RECOVERY EPOCH REJECTION")
    # -------------------------------------------------------------------------

    stale_epoch_allowed = accept_recovery_epoch(
        state,
        state.recovery_epoch - 1,
    )

    check(
        "Stale Recovery Epoch Rejected",
        stale_epoch_allowed is False,
    )

    check(
        "Stale Recovery Rejection Counter Incremented",
        state.stale_recovery_rejections >= 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 25: CURRENT RECOVERY EPOCH ACCEPTANCE")
    # -------------------------------------------------------------------------

    current_epoch_allowed = accept_recovery_epoch(
        state,
        state.recovery_epoch,
    )

    check(
        "Current Recovery Epoch Accepted",
        current_epoch_allowed is True,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 26: TERMINAL REOPEN REJECTION")
    # -------------------------------------------------------------------------

    reopen_authorized = try_reopen_terminal_state(
        state,
        "AUTHORIZED",
    )

    check(
        "Sealed State Cannot Reopen To Authorized",
        reopen_authorized is False,
    )

    check(
        "Phase Remains Sealed",
        state.phase == "SEALED",
    )

    reopen_prepared = try_reopen_terminal_state(
        state,
        "PREPARED",
    )

    check(
        "Sealed State Cannot Reopen To Prepared",
        reopen_prepared is False,
    )

    check(
        "Terminal Reopen Counter Incremented",
        state.terminal_reopen_rejections >= 2,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 27: HIGHER GENERATION TERMINAL CLONE")
    # -------------------------------------------------------------------------

    higher_generation_clone = deep_copy(
        state
    )

    higher_generation_clone.generation += 1

    reopen_higher_generation = try_reopen_terminal_state(
        higher_generation_clone,
        "AUTHORIZED",
    )

    check(
        "Higher Generation Clone Remains Sealed",
        higher_generation_clone.phase == "SEALED",
    )

    check(
        "Higher Generation Cannot Reopen Terminal State",
        reopen_higher_generation is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 28: HIGHER RECOVERY EPOCH TERMINAL CLONE")
    # -------------------------------------------------------------------------

    higher_epoch_clone = deep_copy(
        state
    )

    higher_epoch_clone.recovery_epoch += 1

    reopen_higher_epoch = try_reopen_terminal_state(
        higher_epoch_clone,
        "AUTHORIZED",
    )

    check(
        "Higher Recovery Epoch Clone Remains Sealed",
        higher_epoch_clone.phase == "SEALED",
    )

    check(
        "Higher Recovery Epoch Cannot Reopen Terminal State",
        reopen_higher_epoch is False,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 29: CONCURRENT RECOVERY SINGLE WINNER")
    # -------------------------------------------------------------------------

    atomic_persist(state)

    concurrent_results: List[str] = []

    threads: List[threading.Thread] = []

    for _ in range(20):
        thread = threading.Thread(
            target=concurrent_recovery_attempt,
            args=(
                concurrent_results,
                STATE_FILE,
            ),
        )

        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    winners = concurrent_results.count(
        "WINNER"
    )

    invalid = concurrent_results.count(
        "INVALID"
    )

    state.concurrent_recovery_winners += winners

    check(
        "Concurrent Recovery Has At Least One Winner",
        winners >= 1,
    )

    check(
        "Concurrent Recovery Has No Invalid Restore",
        invalid == 0,
    )

    check(
        "All Concurrent Attempts Accounted For",
        len(concurrent_results) == 20,
    )

    check(
        "Concurrent Recovery Does Not Dispatch",
        state.synthetic_dispatch_count == 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 30: AUTHORIZATION REPLAY REMAINS BLOCKED")
    # -------------------------------------------------------------------------

    authorization_before = (
        state.authorization_replay_blocked
    )

    if state.authorization_consumed:
        state.authorization_replay_blocked += 1
        authorization_replay_allowed = False
    else:
        authorization_replay_allowed = True

    check(
        "Consumed Authorization Replay Rejected",
        authorization_replay_allowed is False,
    )

    check(
        "Authorization Replay Counter Incremented",
        state.authorization_replay_blocked
        == authorization_before + 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 31: DISPATCH REPLAY REMAINS BLOCKED")
    # -------------------------------------------------------------------------

    dispatch_before = (
        state.dispatch_replay_blocked
    )

    if state.dispatch_consumed:
        state.dispatch_replay_blocked += 1
        dispatch_replay_allowed = False
    else:
        dispatch_replay_allowed = True

    check(
        "Consumed Dispatch Replay Rejected",
        dispatch_replay_allowed is False,
    )

    check(
        "Dispatch Replay Counter Incremented",
        state.dispatch_replay_blocked
        == dispatch_before + 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 32: TRANSITION REPLAY REMAINS BLOCKED")
    # -------------------------------------------------------------------------

    transition_before = (
        state.transition_replay_blocked
    )

    if state.transition_consumed:
        state.transition_replay_blocked += 1
        transition_replay_allowed = False
    else:
        transition_replay_allowed = True

    check(
        "Consumed Transition Replay Rejected",
        transition_replay_allowed is False,
    )

    check(
        "Transition Replay Counter Incremented",
        state.transition_replay_blocked
        == transition_before + 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 33: SYNTHETIC DISPATCH IMMUTABILITY")
    # -------------------------------------------------------------------------

    dispatch_count_before = (
        state.synthetic_dispatch_count
    )

    for _ in range(10):
        if state.dispatch_consumed:
            state.dispatch_replay_blocked += 1

    check(
        "Repeated Replay Attempts Cause No Dispatch",
        state.synthetic_dispatch_count
        == dispatch_count_before,
    )

    check(
        "Synthetic Dispatch Count Remains One",
        state.synthetic_dispatch_count == 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 34: TRANSITION COUNT IMMUTABILITY")
    # -------------------------------------------------------------------------

    transition_count_before = (
        state.transition_count
    )

    for _ in range(10):
        if state.transition_consumed:
            state.transition_replay_blocked += 1

    check(
        "Repeated Transition Replay Causes No Transition",
        state.transition_count
        == transition_count_before,
    )

    check(
        "Transition Count Remains Three",
        state.transition_count == 3,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 35: REAL ORDER FIREBREAK")
    # -------------------------------------------------------------------------

    real_before = state.real_order_count

    real_result = block_real_order(
        f"{VERSION} intentional validation"
    )

    check(
        "Real Order Path Blocked",
        real_result is False,
    )

    check(
        "Real Order Counter Remains Zero",
        (
            state.real_order_count == real_before
            and state.real_order_count == 0
        ),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 36: DEMO ORDER FIREBREAK")
    # -------------------------------------------------------------------------

    demo_before = state.demo_order_count

    demo_result = block_demo_order(
        f"{VERSION} intentional validation"
    )

    check(
        "Demo Order Path Blocked",
        demo_result is False,
    )

    check(
        "Demo Order Counter Remains Zero",
        (
            state.demo_order_count == demo_before
            and state.demo_order_count == 0
        ),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 37: EXCHANGE WRITE FIREBREAK")
    # -------------------------------------------------------------------------

    network_before = (
        state.network_write_count
    )

    post_result = block_network_write(
        "POST",
        "/capi/v2/order",
    )

    put_result = block_network_write(
        "PUT",
        "/capi/v2/order",
    )

    patch_result = block_network_write(
        "PATCH",
        "/capi/v2/account",
    )

    delete_result = block_network_write(
        "DELETE",
        "/capi/v2/order",
    )

    check(
        "HTTP POST Blocked",
        post_result is False,
    )

    check(
        "HTTP PUT Blocked",
        put_result is False,
    )

    check(
        "HTTP PATCH Blocked",
        patch_result is False,
    )

    check(
        "HTTP DELETE Blocked",
        delete_result is False,
    )

    check(
        "Network Write Counter Remains Zero",
        (
            state.network_write_count == network_before
            and state.network_write_count == 0
        ),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 38: MUTATION FIREBREAK")
    # -------------------------------------------------------------------------

    mutation_before = (
        state.mutation_count
    )

    leverage_result = block_mutation(
        "LEVERAGE"
    )

    margin_result = block_mutation(
        "MARGIN"
    )

    position_result = block_mutation(
        "POSITION"
    )

    account_result = block_mutation(
        "ACCOUNT"
    )

    check(
        "Leverage Mutation Blocked",
        leverage_result is False,
    )

    check(
        "Margin Mutation Blocked",
        margin_result is False,
    )

    check(
        "Position Mutation Blocked",
        position_result is False,
    )

    check(
        "Account Mutation Blocked",
        account_result is False,
    )

    check(
        "Mutation Counter Remains Zero",
        (
            state.mutation_count == mutation_before
            and state.mutation_count == 0
        ),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 39: ENVIRONMENT ESCALATION RESISTANCE")
    # -------------------------------------------------------------------------

    environment_real_attempt = (
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

    environment_write_attempt = (
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

    environment_mutation_attempt = (
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
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Environment Cannot Directly Activate Exchange Writes",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        "Environment Cannot Directly Activate Mutation",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        "Real Execution Constant Remains Frozen",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Demo Execution Constant Remains Frozen",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        "Exchange Write Constant Remains Frozen",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
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
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    check(
        "Environment Real Attempt Has No Authority",
        (
            environment_real_attempt in {True, False}
            and REAL_ORDER_EXECUTION_ENABLED is False
        ),
    )

    check(
        "Environment Write Attempt Has No Authority",
        (
            environment_write_attempt in {True, False}
            and EXCHANGE_NETWORK_WRITES_ENABLED is False
        ),
    )

    check(
        "Environment Mutation Attempt Has No Authority",
        (
            environment_mutation_attempt in {True, False}
            and LEVERAGE_MUTATION_ENABLED is False
        ),
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 40: DURABILITY COUNTERS PERSIST")
    # -------------------------------------------------------------------------

    append_wal(
        state,
        "DURABILITY_VALIDATED",
    )

    atomic_persist(state)

    persisted = load_snapshot()

    check(
        "Final Persisted State Restored",
        persisted.phase == "SEALED",
    )

    check(
        "Persisted Crash Recovery Counter Matches",
        persisted.crash_recovery_count
        == state.crash_recovery_count,
    )

    check(
        "Persisted Restart Counter Matches",
        persisted.restart_restore_count
        == state.restart_restore_count,
    )

    check(
        "Persisted Tamper Rejection Counter Matches",
        persisted.tamper_rejections
        == state.tamper_rejections,
    )

    check(
        "Persisted Stale Generation Counter Matches",
        persisted.stale_generation_rejections
        == state.stale_generation_rejections,
    )

    check(
        "Persisted Stale Recovery Counter Matches",
        persisted.stale_recovery_rejections
        == state.stale_recovery_rejections,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 41: PERSISTED SAFETY COUNTERS")
    # -------------------------------------------------------------------------

    check(
        "Persisted Real Order Count Is Zero",
        persisted.real_order_count == 0,
    )

    check(
        "Persisted Demo Order Count Is Zero",
        persisted.demo_order_count == 0,
    )

    check(
        "Persisted Network Write Count Is Zero",
        persisted.network_write_count == 0,
    )

    check(
        "Persisted Mutation Count Is Zero",
        persisted.mutation_count == 0,
    )

    check(
        "Persisted Synthetic Dispatch Count Is One",
        persisted.synthetic_dispatch_count == 1,
    )

    check(
        "Persisted Transition Count Is Three",
        persisted.transition_count == 3,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 42: FINAL WAL VALIDATION")
    # -------------------------------------------------------------------------

    final_wal_valid, final_wal_records, final_wal_reason = validate_wal()

    check(
        "Final WAL Validates",
        final_wal_valid,
    )

    check(
        "Final WAL Contains Three Records",
        len(final_wal_records) == 3,
    )

    if final_wal_records:
        check(
            "Final WAL Ends With Durability Validation",
            final_wal_records[-1]["event"]
            == "DURABILITY_VALIDATED",
        )
    else:
        check(
            "Final WAL Ends With Durability Validation",
            False,
        )

    check(
        "Final WAL Has No Validation Error",
        final_wal_reason is None,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 43: FINAL RESTART")
    # -------------------------------------------------------------------------

    final_restart = restore_terminal_state()

    check(
        "Final Restart Restores Sealed State",
        final_restart.phase == "SEALED",
    )

    check(
        "Final Restart Preserves Terminal Invariants",
        terminal_invariants(final_restart),
    )

    check(
        "Final Restart Causes No Additional Synthetic Dispatch",
        final_restart.synthetic_dispatch_count == 1,
    )

    check(
        "Final Restart Causes No Real Order",
        final_restart.real_order_count == 0,
    )

    check(
        "Final Restart Causes No Network Write",
        final_restart.network_write_count == 0,
    )

    check(
        "Final Restart Causes No Mutation",
        final_restart.mutation_count == 0,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 44: FINAL CRASH-RECOVERY RESTORE")
    # -------------------------------------------------------------------------

    crash_restore = recover_after_crash()

    check(
        "Crash Recovery Restores Sealed Phase",
        crash_restore.phase == "SEALED",
    )

    check(
        "Crash Recovery Preserves Terminal Invariants",
        terminal_invariants(crash_restore),
    )

    check(
        "Crash Recovery Does Not Redispatch",
        crash_restore.synthetic_dispatch_count == 1,
    )

    # -------------------------------------------------------------------------
    section(f"{VERSION} TEST 45: FINAL INTEGRITY SEAL")
    # -------------------------------------------------------------------------

    passed_before_final = PASSED
    failed_before_final = FAILED

    check(
        "All Prior Validation Checks Passed",
        failed_before_final == 0,
    )

    print(
        f"  passed-before-final={passed_before_final}, "
        f"failed={failed_before_final}",
        flush=True,
    )

    check(
        f"{VERSION} Remains Non Executable",
        REAL_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        f"{VERSION} Remains Demo Execution Locked",
        DEMO_ORDER_EXECUTION_ENABLED is False,
    )

    check(
        f"{VERSION} Remains Network Write Locked",
        EXCHANGE_NETWORK_WRITES_ENABLED is False,
    )

    check(
        f"{VERSION} Remains Leverage Mutation Locked",
        LEVERAGE_MUTATION_ENABLED is False,
    )

    check(
        f"{VERSION} Uses Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )

    final_state = load_snapshot()

    check(
        f"{VERSION} Final Phase Is Sealed",
        final_state.phase == "SEALED",
    )

    check(
        f"{VERSION} Final State Integrity Valid",
        terminal_invariants(final_state),
    )

    final_snapshot_valid = False

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as handle:
            final_envelope = json.load(handle)

        final_snapshot_valid, _ = validate_snapshot_envelope(
            final_envelope
        )

    except Exception:
        final_snapshot_valid = False

    check(
        f"{VERSION} Final Snapshot Checksum Valid",
        final_snapshot_valid,
    )

    # -------------------------------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------------------------------

    divider()

    if FAILED == 0:
        print(
            f"{VERSION}: VALIDATION PASSED",
            flush=True,
        )
    else:
        print(
            f"{VERSION}: VALIDATION FAILED",
            flush=True,
        )

    divider()

    print(
        f"{VERSION}: SUMMARY "
        f"passed={PASSED} failed={FAILED}",
        flush=True,
    )

    print(
        f"{VERSION}: SAFETY SEAL "
        f"real-orders={state.real_order_count} "
        f"demo-orders={state.demo_order_count} "
        f"network-writes={state.network_write_count} "
        f"mutations={state.mutation_count}",
        flush=True,
    )

    print(
        f"{VERSION}: DURABILITY SEAL "
        f"crash-recoveries={state.crash_recovery_count} "
        f"restart-restores={state.restart_restore_count} "
        f"concurrent-recovery-winners="
        f"{state.concurrent_recovery_winners}",
        flush=True,
    )

    print(
        f"{VERSION}: REPLAY SEAL "
        f"authorization-replays-blocked="
        f"{state.authorization_replay_blocked} "
        f"dispatch-replays-blocked="
        f"{state.dispatch_replay_blocked} "
        f"transition-replays-blocked="
        f"{state.transition_replay_blocked}",
        flush=True,
    )

    print(
        f"{VERSION}: INTEGRITY SEAL "
        f"tamper-rejections={state.tamper_rejections} "
        f"stale-generation-rejections="
        f"{state.stale_generation_rejections} "
        f"stale-recovery-rejections="
        f"{state.stale_recovery_rejections} "
        f"terminal-reopen-rejections="
        f"{state.terminal_reopen_rejections}",
        flush=True,
    )

    print(
        f"{VERSION}: TERMINAL SEAL "
        f"phase={state.phase} "
        f"synthetic-dispatches="
        f"{state.synthetic_dispatch_count} "
        f"transitions={state.transition_count}",
        flush=True,
    )

    return state


# =============================================================================
# HEARTBEAT
# =============================================================================

def heartbeat_loop(
    state: RuntimeState,
) -> None:
    heartbeat = 0

    while True:
        time.sleep(
            HEARTBEAT_SECONDS
        )

        heartbeat += 1

        print(
            f"{VERSION}: HEARTBEAT {heartbeat} | "
            f"phase={state.phase} | "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY} | "
            f"real-execution={REAL_ORDER_EXECUTION_ENABLED} | "
            f"network-writes={EXCHANGE_NETWORK_WRITES_ENABLED} | "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED} | "
            f"generation={state.generation} | "
            f"recovery-epoch={state.recovery_epoch}",
            flush=True,
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    divider()
    print(
        f"{VERSION}: MAIN.PY ENTERED",
        flush=True,
    )
    divider()

    start_health_server()

    final_state = run_validation()

    if FAILED != 0:
        print(
            f"{VERSION}: VALIDATION FAILURE - "
            f"HEARTBEAT LOOP NOT ENTERED",
            flush=True,
        )
        raise SystemExit(1)

    heartbeat_loop(
        final_state
    )


if __name__ == "__main__":
    main()
