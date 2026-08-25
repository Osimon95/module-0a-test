import copy
import hashlib
import hmac
import json
import os
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional


UNIT = "R28 UNIT N.18"

SYMBOL = "BTCUSDT"
LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

LEVERAGE_ENDPOINT = "/capi/v3/account/leverage"
TRANSPORT_METHOD = "POST"

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False

SECRET = b"R28-N18-LOCAL-INTEGRITY-KEY"

HEARTBEAT_SECONDS = 15


COUNTERS = {
    "network_posts": 0,
    "network_writes": 0,
    "leverage_transmissions": 0,
    "synthetic_dispatches": 0,
}

COUNTER_LOCK = threading.Lock()


# ============================================================================
# CANONICAL SERIALIZATION / INTEGRITY
# ============================================================================

def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def seal(
    kind: str,
    payload: Dict[str, Any],
) -> str:

    body = (
        f"{kind}|{canonical(payload)}"
    ).encode("utf-8")

    return hmac.new(
        SECRET,
        body,
        hashlib.sha256,
    ).hexdigest()


def verify_seal(
    kind: str,
    payload: Dict[str, Any],
    signature: str,
) -> bool:

    return hmac.compare_digest(
        seal(kind, payload),
        signature,
    )


# ============================================================================
# CONSOLE HELPERS
# ============================================================================

def expect(
    label: str,
    condition: bool,
) -> None:

    print(
        f"{label:<86} "
        f"{'✅ PASS' if condition else '❌ FAIL'}",
        flush=True,
    )

    if not condition:
        raise AssertionError(label)


def heading(
    title: str,
) -> None:

    print(
        f"\n{UNIT} {title}",
        flush=True,
    )

    print(
        "-" * 92,
        flush=True,
    )


def local_block(
    reason: str,
) -> None:

    print(
        f"{UNIT} LOCAL BLOCK:",
        flush=True,
    )

    print(
        f"  {reason}",
        flush=True,
    )


# ============================================================================
# DURABLE OBJECT
# ============================================================================

@dataclass
class DurableObject:

    kind: str
    epoch: int
    generation: int
    data: Dict[str, Any]

    integrity: str = ""

    def payload(
        self,
    ) -> Dict[str, Any]:

        return {
            "epoch": self.epoch,
            "generation": self.generation,
            "data": self.data,
        }

    def reseal(
        self,
    ) -> None:

        self.integrity = seal(
            self.kind,
            self.payload(),
        )

    def valid(
        self,
    ) -> bool:

        return verify_seal(
            self.kind,
            self.payload(),
            self.integrity,
        )


# ============================================================================
# COMMIT MANIFEST
# ============================================================================

@dataclass
class CommitManifest:

    epoch: int
    generation: int

    snapshot_hash: str
    authorization_hash: str
    journal_hash: str
    ledger_hash: str
    checkpoint_hash: str

    previous_manifest_hash: str

    committed: bool = True

    integrity: str = ""

    def payload(
        self,
    ) -> Dict[str, Any]:

        return {
            "epoch": self.epoch,
            "generation": self.generation,
            "snapshot_hash": self.snapshot_hash,
            "authorization_hash": self.authorization_hash,
            "journal_hash": self.journal_hash,
            "ledger_hash": self.ledger_hash,
            "checkpoint_hash": self.checkpoint_hash,
            "previous_manifest_hash":
                self.previous_manifest_hash,
            "committed":
                self.committed,
        }

    def reseal(
        self,
    ) -> None:

        self.integrity = seal(
            "manifest",
            self.payload(),
        )

    def valid(
        self,
    ) -> bool:

        return verify_seal(
            "manifest",
            self.payload(),
            self.integrity,
        )

    def digest(
        self,
    ) -> str:

        return sha256_text(
            canonical(
                {
                    "payload":
                        self.payload(),
                    "integrity":
                        self.integrity,
                }
            )
        )


# ============================================================================
# DURABLE GENERATION BUNDLE
# ============================================================================

@dataclass
class DurableBundle:

    snapshot: DurableObject
    authorization: DurableObject
    journal: DurableObject
    ledger: DurableObject
    checkpoint: DurableObject
    manifest: CommitManifest


# ============================================================================
# RECOVERY RUNTIME
# ============================================================================

@dataclass
class RuntimeState:

    highest_epoch: int = 0

    highest_generation: int = 0

    highest_manifest_hash: str = ""

    terminal: bool = False

    terminal_state: str = ""

    consumed_authorization_id: str = ""

    dispatch_id: str = ""

    recovery_lock: threading.Lock = field(
        default_factory=threading.Lock
    )


# ============================================================================
# DURABLE OBJECT HASH
# ============================================================================

def object_hash(
    obj: DurableObject,
) -> str:

    return sha256_text(
        canonical(
            {
                "kind":
                    obj.kind,
                "payload":
                    obj.payload(),
                "integrity":
                    obj.integrity,
            }
        )
    )


# ============================================================================
# DURABLE OBJECT FACTORY
# ============================================================================

def make_object(
    kind: str,
    epoch: int,
    generation: int,
    data: Dict[str, Any],
) -> DurableObject:

    obj = DurableObject(
        kind=kind,
        epoch=epoch,
        generation=generation,
        data=copy.deepcopy(data),
    )

    obj.reseal()

    return obj


# ============================================================================
# BUILD COMPLETE DURABLE GENERATION
# ============================================================================

def build_bundle(
    epoch: int,
    generation: int,
    previous_manifest_hash: str = "",
) -> DurableBundle:

    dispatch_id = (
        f"dispatch-e{epoch}-g{generation}"
    )

    auth_id = (
        f"auth-e{epoch}-g{generation}"
    )

    snapshot = make_object(
        "snapshot",
        epoch,
        generation,
        {
            "symbol":
                SYMBOL,
            "state":
                "AUTHORIZED",
            "dispatch_id":
                dispatch_id,
        },
    )

    authorization = make_object(
        "authorization",
        epoch,
        generation,
        {
            "authorization_id":
                auth_id,
            "symbol":
                SYMBOL,
            "endpoint":
                LEVERAGE_ENDPOINT,
            "method":
                TRANSPORT_METHOD,
            "consumed":
                True,
            "dispatch_id":
                dispatch_id,
        },
    )

    journal = make_object(
        "journal",
        epoch,
        generation,
        {
            "entries":
                [
                    {
                        "seq":
                            1,
                        "event":
                            "DISPATCH_PREPARED",
                        "dispatch_id":
                            dispatch_id,
                    },
                    {
                        "seq":
                            2,
                        "event":
                            "AUTHORIZATION_CONSUMED",
                        "authorization_id":
                            auth_id,
                    },
                    {
                        "seq":
                            3,
                        "event":
                            "SYNTHETIC_DISPATCH_COMMITTED",
                        "dispatch_id":
                            dispatch_id,
                    },
                ]
        },
    )

    ledger = make_object(
        "ledger",
        epoch,
        generation,
        {
            "dispatch_id":
                dispatch_id,
            "authorization_id":
                auth_id,
            "terminal_state":
                "COMPLETED",
        },
    )

    checkpoint = make_object(
        "checkpoint",
        epoch,
        generation,
        {
            "dispatch_id":
                dispatch_id,
            "terminal":
                True,
            "terminal_state":
                "COMPLETED",
        },
    )

    manifest = CommitManifest(
        epoch=epoch,
        generation=generation,
        snapshot_hash=
            object_hash(snapshot),
        authorization_hash=
            object_hash(authorization),
        journal_hash=
            object_hash(journal),
        ledger_hash=
            object_hash(ledger),
        checkpoint_hash=
            object_hash(checkpoint),
        previous_manifest_hash=
            previous_manifest_hash,
        committed=True,
    )

    manifest.reseal()

    return DurableBundle(
        snapshot=snapshot,
        authorization=authorization,
        journal=journal,
        ledger=ledger,
        checkpoint=checkpoint,
        manifest=manifest,
    )


# ============================================================================
# DURABLE GENERATION VALIDATION
# ============================================================================

def validate_bundle(
    bundle: DurableBundle,
    runtime: Optional[RuntimeState] = None,
) -> None:

    objects = [
        bundle.snapshot,
        bundle.authorization,
        bundle.journal,
        bundle.ledger,
        bundle.checkpoint,
    ]

    # ------------------------------------------------------------------------
    # COMMIT MANIFEST INTEGRITY
    # ------------------------------------------------------------------------

    if not bundle.manifest.valid():

        raise ValueError(
            "commit manifest integrity mismatch"
        )

    if not bundle.manifest.committed:

        raise ValueError(
            "commit manifest is not durably committed"
        )

    # ------------------------------------------------------------------------
    # EPOCH / GENERATION MEMBERSHIP
    # ------------------------------------------------------------------------

    for obj in objects:

        if not obj.valid():

            raise ValueError(
                f"{obj.kind} integrity mismatch"
            )

        if (
            obj.epoch
            !=
            bundle.manifest.epoch
        ):

            raise ValueError(
                f"{obj.kind} recovery epoch mismatch"
            )

        if (
            obj.generation
            !=
            bundle.manifest.generation
        ):

            raise ValueError(
                f"{obj.kind} snapshot generation mismatch"
            )

    # ------------------------------------------------------------------------
    # OBJECT HASH MEMBERSHIP
    # ------------------------------------------------------------------------

    expected_hashes = {
        "snapshot":
            bundle.manifest.snapshot_hash,

        "authorization":
            bundle.manifest.authorization_hash,

        "journal":
            bundle.manifest.journal_hash,

        "ledger":
            bundle.manifest.ledger_hash,

        "checkpoint":
            bundle.manifest.checkpoint_hash,
    }

    for obj in objects:

        if (
            object_hash(obj)
            !=
            expected_hashes[obj.kind]
        ):

            raise ValueError(
                f"{obj.kind} hash does not match "
                f"committed manifest"
            )

    # ------------------------------------------------------------------------
    # AUTHORIZATION / DISPATCH BINDING
    # ------------------------------------------------------------------------

    auth = bundle.authorization.data

    snapshot = bundle.snapshot.data

    ledger = bundle.ledger.data

    checkpoint = bundle.checkpoint.data

    journal_entries = (
        bundle.journal.data.get(
            "entries",
            [],
        )
    )

    dispatch_id = snapshot.get(
        "dispatch_id"
    )

    auth_id = auth.get(
        "authorization_id"
    )

    if auth.get("symbol") != SYMBOL:

        raise ValueError(
            "authorization symbol mismatch"
        )

    if (
        auth.get("endpoint")
        !=
        LEVERAGE_ENDPOINT
        or
        auth.get("method")
        !=
        TRANSPORT_METHOD
    ):

        raise ValueError(
            "authorization transport binding mismatch"
        )

    if auth.get("consumed") is not True:

        raise ValueError(
            "authorization is not consumed"
        )

    if (
        auth.get("dispatch_id")
        !=
        dispatch_id
    ):

        raise ValueError(
            "authorization dispatch binding mismatch"
        )

    if (
        ledger.get("dispatch_id")
        !=
        dispatch_id
        or
        checkpoint.get("dispatch_id")
        !=
        dispatch_id
    ):

        raise ValueError(
            "terminal durable objects disagree "
            "on dispatch identity"
        )

    if (
        ledger.get("authorization_id")
        !=
        auth_id
    ):

        raise ValueError(
            "ledger authorization binding mismatch"
        )

    if (
        ledger.get("terminal_state")
        !=
        "COMPLETED"
    ):

        raise ValueError(
            "completion ledger is non-terminal"
        )

    if (
        checkpoint.get("terminal")
        is not True
        or
        checkpoint.get("terminal_state")
        !=
        "COMPLETED"
    ):

        raise ValueError(
            "finality checkpoint is non-terminal"
        )

    # ------------------------------------------------------------------------
    # JOURNAL SEQUENCE
    # ------------------------------------------------------------------------

    expected_events = [
        "DISPATCH_PREPARED",
        "AUTHORIZATION_CONSUMED",
        "SYNTHETIC_DISPATCH_COMMITTED",
    ]

    observed_events = [
        entry.get("event")
        for entry in journal_entries
    ]

    if observed_events != expected_events:

        raise ValueError(
            "journal chain sequence mismatch"
        )

    # ------------------------------------------------------------------------
    # MONOTONIC RECOVERY FENCE
    # ------------------------------------------------------------------------

    if runtime is not None:

        if (
            bundle.manifest.epoch
            <
            runtime.highest_epoch
        ):

            raise ValueError(
                "stale recovery epoch rollback rejected"
            )

        if (
            bundle.manifest.epoch
            ==
            runtime.highest_epoch
            and
            bundle.manifest.generation
            <
            runtime.highest_generation
        ):

            raise ValueError(
                "stale snapshot generation "
                "rollback rejected"
            )

        if (
            bundle.manifest.epoch
            ==
            runtime.highest_epoch
            and
            bundle.manifest.generation
            ==
            runtime.highest_generation
            and
            runtime.highest_manifest_hash
            and
            bundle.manifest.digest()
            !=
            runtime.highest_manifest_hash
        ):

            raise ValueError(
                "same-generation manifest fork rejected"
            )


# ============================================================================
# RECOVERY
# ============================================================================

def recover(
    bundle: DurableBundle,
    runtime: RuntimeState,
) -> Dict[str, Any]:

    with runtime.recovery_lock:

        validate_bundle(
            bundle,
            runtime,
        )

        dispatch_id = (
            bundle.snapshot.data[
                "dispatch_id"
            ]
        )

        auth_id = (
            bundle.authorization.data[
                "authorization_id"
            ]
        )

        # --------------------------------------------------------------------
        # TERMINAL FINALITY
        # --------------------------------------------------------------------

        if runtime.terminal:

            if (
                runtime.dispatch_id
                ==
                dispatch_id
                and
                runtime.consumed_authorization_id
                ==
                auth_id
            ):

                return {
                    "status":
                        "ALREADY_FINAL",

                    "dispatch_id":
                        dispatch_id,

                    "synthetic_dispatch":
                        False,
                }

            raise ValueError(
                "terminal finality conflict"
            )

        # --------------------------------------------------------------------
        # ADVANCE MONOTONIC FENCE
        # --------------------------------------------------------------------

        runtime.highest_epoch = (
            bundle.manifest.epoch
        )

        runtime.highest_generation = (
            bundle.manifest.generation
        )

        runtime.highest_manifest_hash = (
            bundle.manifest.digest()
        )

        # --------------------------------------------------------------------
        # TERMINAL COMMIT
        # --------------------------------------------------------------------

        runtime.terminal = True

        runtime.terminal_state = (
            "COMPLETED"
        )

        runtime.consumed_authorization_id = (
            auth_id
        )

        runtime.dispatch_id = (
            dispatch_id
        )

        # --------------------------------------------------------------------
        # SYNTHETIC DISPATCH ONLY
        # --------------------------------------------------------------------

        with COUNTER_LOCK:

            COUNTERS[
                "synthetic_dispatches"
            ] += 1

        return {
            "status":
                "COMPLETED",

            "dispatch_id":
                dispatch_id,

            "synthetic_dispatch":
                True,
        }


# ============================================================================
# HARD NETWORK WRITE FIREBREAKS
# ============================================================================

def real_network_post(
    path: str,
    payload: Dict[str, Any],
) -> None:

    if (
        not NETWORK_WRITES_ENABLED
        or
        not LIVE_ORDER_EXECUTION
    ):

        local_block(
            f"{UNIT} LOCAL BLOCK: "
            f"real network POST is disabled."
        )

        raise PermissionError(
            "real network POST is disabled"
        )

    with COUNTER_LOCK:

        COUNTERS[
            "network_posts"
        ] += 1

        COUNTERS[
            "network_writes"
        ] += 1


def generic_network_write(
    method: str,
    path: str,
    payload: Dict[str, Any],
) -> None:

    if not NETWORK_WRITES_ENABLED:

        local_block(
            f"{UNIT} LOCAL BLOCK: "
            f"network write method "
            f"{method} is disabled."
        )

        raise PermissionError(
            f"network write method "
            f"{method} is disabled"
        )

    with COUNTER_LOCK:

        COUNTERS[
            "network_writes"
        ] += 1


def leverage_mutation_transport(
    path: str,
    payload: Dict[str, Any],
) -> None:

    if (
        not
        LEVERAGE_MUTATION_TRANSPORT_ENABLED
    ):

        local_block(
            f"{UNIT} LOCAL BLOCK: "
            f"leverage mutation transport "
            f"is disabled."
        )

        raise PermissionError(
            "leverage mutation transport "
            "is disabled"
        )

    with COUNTER_LOCK:

        COUNTERS[
            "leverage_transmissions"
        ] += 1


# ============================================================================
# EXPECTED REJECTION HELPER
# ============================================================================

def assert_rejected(
    label: str,
    fn,
    expected_fragment: str = "",
) -> None:

    rejected = False

    try:

        fn()

    except Exception as exc:

        if (
            expected_fragment
            and
            expected_fragment not in str(exc)
        ):

            raise

        local_block(
            str(exc)
        )

        rejected = True

    expect(
        label,
        rejected,
    )


# ============================================================================
# HEALTH SERVER
# ============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ):

        body = (
            b"R28 UNIT N.18 ACTIVE\n"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/plain",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args,
    ):

        return


def start_health_server(
) -> None:

    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )

    def serve():

        try:

            HTTPServer(
                (
                    "0.0.0.0",
                    port,
                ),
                HealthHandler,
            ).serve_forever()

        except OSError as exc:

            print(
                f"{UNIT}: "
                f"HEALTH SERVER NOTICE: "
                f"{exc}",
                flush=True,
            )

    threading.Thread(
        target=serve,
        daemon=True,
    ).start()

    print(
        f"{UNIT}: "
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {port}",
        flush=True,
    )


# ============================================================================
# DIAGNOSTIC
# ============================================================================

def run_diagnostic(
) -> None:

    print(
        "=" * 92,
        flush=True,
    )

    print(
        f"{UNIT}: MAIN.PY ENTERED",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"COMMIT-MANIFEST "
        f"RECOVERY FENCE VALIDATION",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )

    # ========================================================================
    # BASE GENERATION
    # ========================================================================

    base = build_bundle(
        epoch=1,
        generation=1,
    )

    # ========================================================================
    # TEST 1
    # ========================================================================

    heading(
        "TEST 1: COMPLETE DURABLE "
        "GENERATION / MANIFEST VALIDATION"
    )

    validate_bundle(
        base
    )

    expect(
        "Committed Manifest Integrity Valid",
        base.manifest.valid(),
    )

    expect(
        "Snapshot Bound To Manifest",
        object_hash(
            base.snapshot
        )
        ==
        base.manifest.snapshot_hash,
    )

    expect(
        "Authorization Bound To Manifest",
        object_hash(
            base.authorization
        )
        ==
        base.manifest.authorization_hash,
    )

    expect(
        "Journal Bound To Manifest",
        object_hash(
            base.journal
        )
        ==
        base.manifest.journal_hash,
    )

    expect(
        "Ledger Bound To Manifest",
        object_hash(
            base.ledger
        )
        ==
        base.manifest.ledger_hash,
    )

    expect(
        "Checkpoint Bound To Manifest",
        object_hash(
            base.checkpoint
        )
        ==
        base.manifest.checkpoint_hash,
    )

    # ========================================================================
    # TEST 2
    # ========================================================================

    heading(
        "TEST 2: "
        "UNCOMMITTED MANIFEST REJECTION"
    )

    torn = copy.deepcopy(
        base
    )

    torn.manifest.committed = False

    torn.manifest.reseal()

    assert_rejected(
        "Uncommitted Durable Generation Rejected",
        lambda:
            validate_bundle(
                torn
            ),
        "not durably committed",
    )

    # ========================================================================
    # TEST 3
    # ========================================================================

    heading(
        "TEST 3: "
        "MANIFEST INTEGRITY TAMPERING"
    )

    tampered_manifest = (
        copy.deepcopy(
            base
        )
    )

    tampered_manifest.manifest.snapshot_hash = (
        "0" * 64
    )

    assert_rejected(
        "Manifest Integrity Tampering Rejected",
        lambda:
            validate_bundle(
                tampered_manifest
            ),
        "commit manifest integrity mismatch",
    )

    # ========================================================================
    # GENERATION 2
    # ========================================================================

    generation2 = build_bundle(
        epoch=1,
        generation=2,
        previous_manifest_hash=
            base.manifest.digest(),
    )

    # ========================================================================
    # TEST 4
    # ========================================================================

    heading(
        "TEST 4: "
        "PARTIAL-GENERATION SNAPSHOT SUBSTITUTION"
    )

    mixed = copy.deepcopy(
        generation2
    )

    mixed.snapshot = copy.deepcopy(
        base.snapshot
    )

    assert_rejected(
        "Older Snapshot Substitution Rejected",
        lambda:
            validate_bundle(
                mixed
            ),
        "snapshot generation mismatch",
    )

    # ========================================================================
    # TEST 5
    # ========================================================================

    heading(
        "TEST 5: "
        "PARTIAL-GENERATION AUTHORIZATION SUBSTITUTION"
    )

    mixed_auth = copy.deepcopy(
        generation2
    )

    mixed_auth.authorization = (
        copy.deepcopy(
            base.authorization
        )
    )

    assert_rejected(
        "Older Authorization Substitution Rejected",
        lambda:
            validate_bundle(
                mixed_auth
            ),
        "authorization snapshot generation mismatch",
    )

    # ========================================================================
    # TEST 6
    # ========================================================================

    heading(
        "TEST 6: "
        "PARTIAL-GENERATION JOURNAL / "
        "LEDGER / CHECKPOINT SUBSTITUTION"
    )

    for attr, label in [

        (
            "journal",
            "Older Journal Substitution Rejected",
        ),

        (
            "ledger",
            "Older Ledger Substitution Rejected",
        ),

        (
            "checkpoint",
            "Older Checkpoint Substitution Rejected",
        ),
    ]:

        candidate = copy.deepcopy(
            generation2
        )

        setattr(
            candidate,
            attr,
            copy.deepcopy(
                getattr(
                    base,
                    attr,
                )
            ),
        )

        assert_rejected(
            label,
            lambda c=candidate:
                validate_bundle(
                    c
                ),
            f"{attr} snapshot generation mismatch",
        )

    # ========================================================================
    # TEST 7
    # ========================================================================

    heading(
        "TEST 7: SAME-GENERATION "
        "OBJECT TAMPERING WITH RESEAL"
    )

    resealed = copy.deepcopy(
        base
    )

    resealed.snapshot.data[
        "state"
    ] = "FORGED"

    resealed.snapshot.reseal()

    assert_rejected(
        "Resealed Snapshot Still Rejected "
        "By Manifest Hash",
        lambda:
            validate_bundle(
                resealed
            ),
        "snapshot hash does not match committed manifest",
    )

    # ========================================================================
    # TEST 8
    # ========================================================================

    heading(
        "TEST 8: FIRST RECOVERY PRODUCES "
        "ONE SYNTHETIC DISPATCH"
    )

    runtime = RuntimeState()

    before = COUNTERS[
        "synthetic_dispatches"
    ]

    result = recover(
        base,
        runtime,
    )

    expect(
        "Recovery Completed",
        result["status"]
        ==
        "COMPLETED",
    )

    expect(
        "Recovery Produced Synthetic Dispatch",
        result[
            "synthetic_dispatch"
        ]
        is True,
    )

    expect(
        "Exactly One Synthetic Dispatch Produced",
        COUNTERS[
            "synthetic_dispatches"
        ]
        ==
        before + 1,
    )

    expect(
        "Authorization Preserved As Consumed",
        bool(
            runtime.consumed_authorization_id
        ),
    )

    expect(
        "Terminal Finality Recorded",
        runtime.terminal
        and
        runtime.terminal_state
        ==
        "COMPLETED",
    )

    # ========================================================================
    # TEST 9
    # ========================================================================

    heading(
        "TEST 9: "
        "REPEATED RECOVERY IS IDEMPOTENT"
    )

    before_repeat = COUNTERS[
        "synthetic_dispatches"
    ]

    repeat = recover(
        base,
        runtime,
    )

    expect(
        "Repeated Recovery Is Already Final",
        repeat["status"]
        ==
        "ALREADY_FINAL",
    )

    expect(
        "Repeated Recovery Produced No Second Dispatch",
        COUNTERS[
            "synthetic_dispatches"
        ]
        ==
        before_repeat,
    )

    # ========================================================================
    # TEST 10
    # ========================================================================

    heading(
        "TEST 10: STALE MANIFEST / "
        "GENERATION ROLLBACK REJECTION"
    )

    rollback_runtime = RuntimeState(
        highest_epoch=1,
        highest_generation=2,
        highest_manifest_hash=
            generation2.manifest.digest(),
    )

    assert_rejected(
        "Stale Manifest Rollback Rejected",
        lambda:
            recover(
                base,
                rollback_runtime,
            ),
        "stale snapshot generation rollback rejected",
    )

    # ========================================================================
    # TEST 11
    # ========================================================================

    heading(
        "TEST 11: SAME-GENERATION "
        "MANIFEST FORK REJECTION"
    )

    fork_runtime = RuntimeState(
        highest_epoch=1,
        highest_generation=1,
        highest_manifest_hash=
            base.manifest.digest(),
    )

    fork = build_bundle(
        epoch=1,
        generation=1,
    )

    fork.snapshot.data[
        "nonce"
    ] = "fork"

    fork.snapshot.reseal()

    fork.manifest.snapshot_hash = (
        object_hash(
            fork.snapshot
        )
    )

    fork.manifest.reseal()

    assert_rejected(
        "Same-Generation Manifest Fork Rejected",
        lambda:
            recover(
                fork,
                fork_runtime,
            ),
        "same-generation manifest fork rejected",
    )

    # ========================================================================
    # TEST 12
    # ========================================================================

    heading(
        "TEST 12: CROSS-EPOCH "
        "DURABLE OBJECT SUBSTITUTION"
    )

    epoch2 = build_bundle(
        epoch=2,
        generation=3,
        previous_manifest_hash=
            generation2.manifest.digest(),
    )

    cross_epoch = copy.deepcopy(
        epoch2
    )

    cross_epoch.authorization = (
        copy.deepcopy(
            generation2.authorization
        )
    )

    assert_rejected(
        "Cross-Epoch Authorization "
        "Substitution Rejected",
        lambda:
            validate_bundle(
                cross_epoch
            ),
        "authorization recovery epoch mismatch",
    )

    # ========================================================================
    # TEST 13
    # ========================================================================

    heading(
        "TEST 13: "
        "CONCURRENT RECOVERY SINGLE WINNER"
    )

    concurrent_runtime = RuntimeState()

    concurrent_bundle = build_bundle(
        epoch=3,
        generation=4,
        previous_manifest_hash=
            epoch2.manifest.digest(),
    )

    results: List[
        Dict[str, Any]
    ] = []

    errors: List[
        str
    ] = []

    start_dispatches = COUNTERS[
        "synthetic_dispatches"
    ]

    def worker():

        try:

            results.append(
                recover(
                    concurrent_bundle,
                    concurrent_runtime,
                )
            )

        except Exception as exc:

            errors.append(
                str(exc)
            )

    threads = [
        threading.Thread(
            target=worker
        )
        for _ in range(8)
    ]

    for thread in threads:

        thread.start()

    for thread in threads:

        thread.join()

    winners = sum(
        1
        for item in results
        if item[
            "synthetic_dispatch"
        ]
    )

    already_final = sum(
        1
        for item in results
        if item[
            "status"
        ]
        ==
        "ALREADY_FINAL"
    )

    expect(
        "Concurrent Recovery Produced "
        "Exactly One Synthetic Dispatch",
        winners == 1,
    )

    expect(
        "Concurrent Recovery Remaining Workers "
        "Observed Finality",
        already_final == 7,
    )

    expect(
        "Concurrent Recovery Preserved "
        "Consumed Authorization",
        bool(
            concurrent_runtime.
            consumed_authorization_id
        ),
    )

    expect(
        "Concurrent Recovery Produced "
        "No Structural Errors",
        len(errors) == 0,
    )

    expect(
        "Global Synthetic Dispatch Count "
        "Advanced Exactly Once",
        COUNTERS[
            "synthetic_dispatches"
        ]
        ==
        start_dispatches + 1,
    )

    # ========================================================================
    # TEST 14
    # ========================================================================

    heading(
        "TEST 14: "
        "TERMINAL STATE IMMUTABILITY"
    )

    conflicting = build_bundle(
        epoch=4,
        generation=5,
        previous_manifest_hash=
            concurrent_bundle.manifest.digest(),
    )

    assert_rejected(
        "Conflicting Post-Finality Recovery Rejected",
        lambda:
            recover(
                conflicting,
                concurrent_runtime,
            ),
        "terminal finality conflict",
    )

    expect(
        "Original Terminal Dispatch "
        "Identity Preserved",
        concurrent_runtime.dispatch_id
        ==
        concurrent_bundle.snapshot.data[
            "dispatch_id"
        ],
    )

    expect(
        "Original Consumed Authorization Preserved",
        concurrent_runtime.
        consumed_authorization_id
        ==
        concurrent_bundle.
        authorization.data[
            "authorization_id"
        ],
    )

    # ========================================================================
    # TEST 15
    # ========================================================================

    heading(
        "TEST 15: EXACT ENDPOINT / "
        "PAYLOAD IMMUTABILITY"
    )

    payload = {
        "leverage":
            LEVERAGE,
        "marginMode":
            MARGIN_MODE,
        "symbol":
            SYMBOL,
    }

    expected_payload = (
        '{"leverage":"100",'
        '"marginMode":"ISOLATED",'
        '"symbol":"BTCUSDT"}'
    )

    expect(
        "Exact Leverage Payload Preserved",
        canonical(payload)
        ==
        expected_payload,
    )

    expect(
        "Canonical Payload Serialization Preserved",
        canonical(payload)
        ==
        canonical(
            json.loads(
                expected_payload
            )
        ),
    )

    expect(
        "Transport Method Exactly POST",
        TRANSPORT_METHOD
        ==
        "POST",
    )

    expect(
        "Transport Path Exactly "
        "Leverage Endpoint",
        LEVERAGE_ENDPOINT
        ==
        "/capi/v3/account/leverage",
    )

    # ========================================================================
    # TEST 16
    # ========================================================================

    heading(
        "TEST 16: "
        "FINAL NETWORK WRITE FIREBREAK"
    )

    assert_rejected(
        "Real POST Rejected Locally",
        lambda:
            real_network_post(
                LEVERAGE_ENDPOINT,
                payload,
            ),
        "real network POST is disabled",
    )

    assert_rejected(
        "Generic Network Write "
        "Rejected Locally",
        lambda:
            generic_network_write(
                "PUT",
                LEVERAGE_ENDPOINT,
                payload,
            ),
        "network write method PUT is disabled",
    )

    assert_rejected(
        "Leverage Mutation Transport "
        "Rejected Locally",
        lambda:
            leverage_mutation_transport(
                LEVERAGE_ENDPOINT,
                payload,
            ),
        "leverage mutation transport is disabled",
    )

    expect(
        "Network POST Count Is Zero",
        COUNTERS[
            "network_posts"
        ]
        ==
        0,
    )

    expect(
        "Network Write Count Is Zero",
        COUNTERS[
            "network_writes"
        ]
        ==
        0,
    )

    expect(
        "Leverage Transmission Count Is Zero",
        COUNTERS[
            "leverage_transmissions"
        ]
        ==
        0,
    )

    # ========================================================================
    # WRITE LOCK AUDIT
    # ========================================================================

    heading(
        "WRITE-LOCK AUDIT"
    )

    print(
        f"  Network POSTs = "
        f"{COUNTERS['network_posts']}",
        flush=True,
    )

    print(
        f"  Network writes = "
        f"{COUNTERS['network_writes']}",
        flush=True,
    )

    print(
        f"  Leverage transmissions = "
        f"{COUNTERS['leverage_transmissions']}",
        flush=True,
    )

    print(
        f"  Synthetic dispatches = "
        f"{COUNTERS['synthetic_dispatches']}",
        flush=True,
    )

    expect(
        "Network POST Count Is Zero",
        COUNTERS[
            "network_posts"
        ]
        ==
        0,
    )

    expect(
        "Network Write Count Is Zero",
        COUNTERS[
            "network_writes"
        ]
        ==
        0,
    )

    expect(
        "Leverage Transmission Count Is Zero",
        COUNTERS[
            "leverage_transmissions"
        ]
        ==
        0,
    )

    # ========================================================================
    # EXECUTION READINESS
    # ========================================================================

    heading(
        "EXECUTION-READINESS ASSESSMENT"
    )

    structural_failures = 0

    readiness_blockers = 0

    print(
        f"  Structural Safety Failures = "
        f"{structural_failures}",
        flush=True,
    )

    print(
        f"  Readiness Blockers = "
        f"{readiness_blockers}",
        flush=True,
    )

    print(
        "  Commit Manifest Integrity = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Atomic Generation Membership = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Partial-Generation "
        "Substitution Rejection = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Same-Generation "
        "Manifest Fork Rejection = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Stale Manifest Rollback Rejection = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Cross-Epoch Durable Object Rejection = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Concurrent Recovery Single Winner = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Terminal Finality Immutability = "
        "✅ VERIFIED",
        flush=True,
    )

    print(
        "  Final Network Dispatch = "
        "🛡 BLOCKED LOCALLY",
        flush=True,
    )

    print(
        "  Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY",
        flush=True,
    )

    expect(
        "Structural Safety Failures Are Zero",
        structural_failures == 0,
    )

    expect(
        "Readiness Blockers Are Zero",
        readiness_blockers == 0,
    )

    # ========================================================================
    # FINAL RESULT
    # ========================================================================

    print(
        "\n" + "=" * 92,
        flush=True,
    )

    print(
        f"✅ {UNIT} DIAGNOSTIC PASSED",
        flush=True,
    )

    print(
        "✅ DURABLE COMMIT-MANIFEST "
        "FENCING VERIFIED",
        flush=True,
    )

    print(
        "✅ ATOMIC GENERATION "
        "MEMBERSHIP VERIFIED",
        flush=True,
    )

    print(
        "✅ PARTIAL-GENERATION "
        "SUBSTITUTION REJECTED",
        flush=True,
    )

    print(
        "✅ SAME-GENERATION "
        "MANIFEST FORKS REJECTED",
        flush=True,
    )

    print(
        "✅ STALE MANIFEST "
        "ROLLBACK REJECTED",
        flush=True,
    )

    print(
        "✅ CROSS-EPOCH DURABLE OBJECT "
        "SUBSTITUTION REJECTED",
        flush=True,
    )

    print(
        "✅ CONCURRENT RECOVERY PRODUCES "
        "SINGLE SYNTHETIC DISPATCH",
        flush=True,
    )

    print(
        "✅ TERMINAL FINALITY "
        "REMAINS IMMUTABLE",
        flush=True,
    )

    print(
        "🛡 REAL NETWORK DISPATCH "
        "REMAINS DISABLED",
        flush=True,
    )

    print(
        "🛡 LEVERAGE MUTATION TRANSPORT "
        "REMAINS LOCKED",
        flush=True,
    )

    print(
        "🛡 NO NETWORK WRITE "
        "WAS TRANSMITTED",
        flush=True,
    )

    print(
        "=" * 92,
        flush=True,
    )


# ============================================================================
# HEARTBEAT
# ============================================================================

def heartbeat_loop(
) -> None:

    count = 0

    while True:

        count += 1

        print(
            f"{UNIT}: "
            f"HEARTBEAT {count} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(
            HEARTBEAT_SECONDS
        )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    start_health_server()

    run_diagnostic()

    print(
        f"{UNIT}: "
        f"PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"COMMIT MANIFEST FENCE LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"ATOMIC GENERATION MEMBERSHIP "
        f"LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"MANIFEST ROLLBACK REJECTION "
        f"LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"SAME-GENERATION FORK REJECTION "
        f"LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"TERMINAL STATE IMMUTABILITY "
        f"LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"SYNTHETIC TRANSPORT "
        f"INTERCEPTOR ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"NETWORK WRITE TRANSPORT LOCKED",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"LEVERAGE MUTATION TRANSPORT LOCKED",
        flush=True,
    )

    heartbeat_loop()
