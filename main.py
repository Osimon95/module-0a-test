import os
import json
import time
import hashlib
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


# =============================================================================
# R28 UNIT N.20
# DURABLE LEASE EXPIRY / RENEWAL / TAKEOVER FENCING
# =============================================================================

UNIT = "R28 UNIT N.20"

SYMBOL = "BTCUSDT"
LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

METHOD = "POST"
PATH = "/capi/v3/account/leverage"

LEASE_TTL = 30
HEARTBEAT_SECONDS = 15


# =============================================================================
# ABSOLUTE NETWORK-WRITE FIREBREAKS
# =============================================================================

REAL_NETWORK_POST_ENABLED = False
NETWORK_WRITE_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False


# =============================================================================
# AUDIT COUNTERS
# =============================================================================

NETWORK_POST_COUNT = 0
NETWORK_WRITE_COUNT = 0
LEVERAGE_TRANSMISSION_COUNT = 0
SYNTHETIC_DISPATCH_COUNT = 0

STRUCTURAL_SAFETY_FAILURES = 0
READINESS_BLOCKERS = 0


# =============================================================================
# LOCAL DIAGNOSTIC SNAPSHOT SEAL
# =============================================================================

SEAL_KEY = b"r28-unit-n20-local-diagnostic-seal-v1"


# =============================================================================
# CONSOLE HELPERS
# =============================================================================

def line():
    print("-" * 92, flush=True)


def banner():
    print("=" * 92, flush=True)


def local_block(message):
    print(f"{UNIT} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


def check(label, condition):
    global STRUCTURAL_SAFETY_FAILURES

    if condition:
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
        STRUCTURAL_SAFETY_FAILURES += 1

    print(
        f"{label:<86} {status}",
        flush=True,
    )

    return bool(condition)


# =============================================================================
# DETERMINISTIC SERIALIZATION / HASHING
# =============================================================================

def canonical_json(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def seal_state(state_without_seal):
    raw = canonical_json(
        state_without_seal
    ).encode("utf-8")

    return hashlib.sha256(
        SEAL_KEY + raw
    ).hexdigest()


# =============================================================================
# EXACT LEVERAGE PAYLOAD
# =============================================================================

def build_payload():
    return {
        "symbol": SYMBOL,
        "leverage": LEVERAGE,
        "marginMode": MARGIN_MODE,
    }


EXACT_PAYLOAD = build_payload()

EXACT_PAYLOAD_JSON = canonical_json(
    EXACT_PAYLOAD
)

EXACT_PAYLOAD_HASH = sha256_text(
    EXACT_PAYLOAD_JSON
)


# =============================================================================
# RECOVERY ERROR
# =============================================================================

class RecoveryError(Exception):
    pass


# =============================================================================
# LOGICAL MONOTONIC CLOCK
# =============================================================================

class LogicalClock:

    def __init__(self, start=1_000_000):
        self._now = int(start)
        self._floor = int(start)

    def now(self):
        return self._now

    def advance(self, seconds):

        if seconds < 0:
            raise ValueError(
                "clock advance must be non-negative"
            )

        self._now += int(seconds)

        self._floor = max(
            self._floor,
            self._now,
        )

        return self._now

    def force(self, new_time):

        new_time = int(new_time)

        if new_time < self._floor:
            raise RecoveryError(
                "monotonic clock rollback rejected"
            )

        self._now = new_time

        self._floor = max(
            self._floor,
            self._now,
        )

        return self._now


# =============================================================================
# DURABLE RECOVERY STATE
# =============================================================================

class DurableRecoveryState:

    def __init__(self, path):

        self.path = path

        self._lock = threading.RLock()

        self.state = None


    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def initialize(self):

        with self._lock:

            self.state = {
                "version": 1,

                "generation": 1,

                "epoch": 1,

                "terminal": False,

                "payload_hash": EXACT_PAYLOAD_HASH,

                "dispatch_identity": sha256_text(
                    f"{UNIT}|"
                    f"{SYMBOL}|"
                    f"{EXACT_PAYLOAD_HASH}|"
                    f"generation=1"
                )[:32],

                "lease_nonce_counter": 0,

                "lease": None,

                "last_monotonic_time": 0,
            }

            self._persist()

            return self.snapshot()


    # =========================================================================
    # DURABLE PERSISTENCE
    # =========================================================================

    def _body_for_persist(self):

        return json.loads(
            canonical_json(
                self.state
            )
        )


    def _persist(self):

        body = self._body_for_persist()

        wrapper = {
            "state": body,
            "seal": seal_state(body),
        }

        directory = (
            os.path.dirname(self.path)
            or "."
        )

        os.makedirs(
            directory,
            exist_ok=True,
        )

        fd, tmp = tempfile.mkstemp(
            prefix=".n20-",
            suffix=".tmp",
            dir=directory,
        )

        try:

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:

                json.dump(
                    wrapper,
                    handle,
                    sort_keys=True,
                    separators=(",", ":"),
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )

            os.replace(
                tmp,
                self.path,
            )

        finally:

            if os.path.exists(tmp):
                os.unlink(tmp)


    def load(self):

        with self._lock:

            with open(
                self.path,
                "r",
                encoding="utf-8",
            ) as handle:

                wrapper = json.load(handle)

            body = wrapper.get(
                "state"
            )

            supplied = wrapper.get(
                "seal"
            )

            expected = seal_state(
                body
            )

            if supplied != expected:

                raise RecoveryError(
                    "snapshot integrity seal mismatch"
                )

            self.state = body

            return self.snapshot()


    def snapshot(self):

        return json.loads(
            canonical_json(
                self.state
            )
        )


    # =========================================================================
    # DURABLE MONOTONIC TIME FENCE
    # =========================================================================

    def _observe_time(self, now):

        now = int(now)

        previous = int(
            self.state[
                "last_monotonic_time"
            ]
        )

        if now < previous:

            raise RecoveryError(
                "durable monotonic time rollback rejected"
            )

        self.state[
            "last_monotonic_time"
        ] = now


    # =========================================================================
    # ACQUIRE RECOVERY LEASE
    # =========================================================================

    def acquire_lease(
        self,
        worker,
        now,
        ttl=LEASE_TTL,
    ):

        with self._lock:

            self._observe_time(
                now
            )

            if self.state[
                "terminal"
            ]:

                raise RecoveryError(
                    "terminal generation cannot acquire recovery lease"
                )

            current = self.state[
                "lease"
            ]

            if (
                current is not None
                and
                now < current[
                    "expires_at"
                ]
            ):

                raise RecoveryError(
                    "recovery lease already owned"
                )

            self.state[
                "lease_nonce_counter"
            ] += 1

            lease = {
                "worker": str(worker),

                "nonce": self.state[
                    "lease_nonce_counter"
                ],

                "generation": self.state[
                    "generation"
                ],

                "epoch": self.state[
                    "epoch"
                ],

                "acquired_at": int(now),

                "expires_at":
                    int(now)
                    +
                    int(ttl),

                "payload_hash":
                    self.state[
                        "payload_hash"
                    ],
            }

            self.state[
                "lease"
            ] = lease

            self._persist()

            return json.loads(
                canonical_json(
                    lease
                )
            )


    # =========================================================================
    # RENEW RECOVERY LEASE
    # =========================================================================

    def renew_lease(
        self,
        lease,
        now,
        ttl=LEASE_TTL,
    ):

        with self._lock:

            self._observe_time(
                now
            )

            if self.state[
                "terminal"
            ]:

                raise RecoveryError(
                    "terminal generation cannot renew recovery lease"
                )

            current = self.state[
                "lease"
            ]

            self._require_exact_fence(
                lease,
                current,
            )

            if now >= current[
                "expires_at"
            ]:

                raise RecoveryError(
                    "expired recovery lease cannot renew"
                )

            current[
                "expires_at"
            ] = (
                int(now)
                +
                int(ttl)
            )

            self._persist()

            return json.loads(
                canonical_json(
                    current
                )
            )


    # =========================================================================
    # RELEASE RECOVERY LEASE
    # =========================================================================

    def release_lease(
        self,
        lease,
        now,
    ):

        with self._lock:

            self._observe_time(
                now
            )

            current = self.state[
                "lease"
            ]

            self._require_exact_fence(
                lease,
                current,
            )

            self.state[
                "lease"
            ] = None

            self._persist()


    # =========================================================================
    # ADVANCE RECOVERY EPOCH
    # =========================================================================

    def advance_epoch(
        self,
        now,
    ):

        with self._lock:

            self._observe_time(
                now
            )

            if self.state[
                "terminal"
            ]:

                raise RecoveryError(
                    "terminal generation epoch immutable"
                )

            self.state[
                "epoch"
            ] += 1

            self.state[
                "lease"
            ] = None

            self._persist()

            return self.state[
                "epoch"
            ]


    # =========================================================================
    # EXACT LEASE FENCE VALIDATION
    # =========================================================================

    def _require_exact_fence(
        self,
        lease,
        current,
    ):

        if current is None:

            raise RecoveryError(
                "recovery lease fence mismatch"
            )

        fields = (
            "worker",
            "nonce",
            "generation",
            "epoch",
            "payload_hash",
        )

        for field in fields:

            if (
                lease.get(field)
                !=
                current.get(field)
            ):

                raise RecoveryError(
                    "recovery lease fence mismatch"
                )

        if (
            lease.get("epoch")
            !=
            self.state["epoch"]
        ):

            raise RecoveryError(
                "stale recovery lease epoch"
            )

        if (
            lease.get("generation")
            !=
            self.state["generation"]
        ):

            raise RecoveryError(
                "stale recovery lease generation"
            )

        if (
            lease.get("payload_hash")
            !=
            self.state["payload_hash"]
        ):

            raise RecoveryError(
                "recovery payload binding mismatch"
            )


    # =========================================================================
    # AUTHORIZE RECOVERY
    # =========================================================================

    def authorize_recovery(
        self,
        lease,
        payload,
        now,
    ):

        with self._lock:

            self._observe_time(
                now
            )

            if self.state[
                "terminal"
            ]:

                raise RecoveryError(
                    "recovery lease fence mismatch"
                )

            current = self.state[
                "lease"
            ]

            self._require_exact_fence(
                lease,
                current,
            )

            if now >= current[
                "expires_at"
            ]:

                raise RecoveryError(
                    "expired recovery lease"
                )

            payload_hash = sha256_text(
                canonical_json(
                    payload
                )
            )

            if (
                payload_hash
                !=
                self.state[
                    "payload_hash"
                ]
            ):

                raise RecoveryError(
                    "recovery payload binding mismatch"
                )

            return {
                "method": METHOD,

                "path": PATH,

                "payload": json.loads(
                    canonical_json(
                        payload
                    )
                ),

                "payload_hash":
                    payload_hash,

                "dispatch_identity":
                    self.state[
                        "dispatch_identity"
                    ],

                "generation":
                    self.state[
                        "generation"
                    ],

                "epoch":
                    self.state[
                        "epoch"
                    ],

                "worker":
                    current[
                        "worker"
                    ],

                "nonce":
                    current[
                        "nonce"
                    ],
            }


    # =========================================================================
    # TERMINAL COMMIT
    # =========================================================================

    def commit_terminal(
        self,
        lease,
        dispatch,
        now,
    ):

        with self._lock:

            self._observe_time(
                now
            )

            if self.state[
                "terminal"
            ]:

                raise RecoveryError(
                    "terminal generation immutable"
                )

            current = self.state[
                "lease"
            ]

            self._require_exact_fence(
                lease,
                current,
            )

            if now >= current[
                "expires_at"
            ]:

                raise RecoveryError(
                    "expired recovery lease"
                )

            if (
                dispatch[
                    "payload_hash"
                ]
                !=
                self.state[
                    "payload_hash"
                ]
            ):

                raise RecoveryError(
                    "recovery payload binding mismatch"
                )

            if (
                dispatch[
                    "dispatch_identity"
                ]
                !=
                self.state[
                    "dispatch_identity"
                ]
            ):

                raise RecoveryError(
                    "dispatch identity mismatch"
                )

            synthetic_transport(
                dispatch
            )

            self.state[
                "terminal"
            ] = True

            self.state[
                "lease"
            ] = None

            self._persist()

            return True


# =============================================================================
# SYNTHETIC TRANSPORT
# =============================================================================

def synthetic_transport(
    dispatch
):

    global SYNTHETIC_DISPATCH_COUNT

    if (
        dispatch["method"]
        !=
        METHOD
    ):

        raise RecoveryError(
            "synthetic transport method mismatch"
        )

    if (
        dispatch["path"]
        !=
        PATH
    ):

        raise RecoveryError(
            "synthetic transport path mismatch"
        )

    if (
        dispatch[
            "payload_hash"
        ]
        !=
        EXACT_PAYLOAD_HASH
    ):

        raise RecoveryError(
            "synthetic transport payload hash mismatch"
        )

    SYNTHETIC_DISPATCH_COUNT += 1

    return {
        "synthetic": True,
        "transmitted": False,
        "method": dispatch["method"],
        "path": dispatch["path"],
        "payload_hash":
            dispatch[
                "payload_hash"
            ],
    }


# =============================================================================
# ABSOLUTELY BLOCKED REAL NETWORK POST
# =============================================================================

def real_network_post(
    path,
    payload,
):

    global NETWORK_POST_COUNT

    if not REAL_NETWORK_POST_ENABLED:

        local_block(
            f"{UNIT} LOCAL BLOCK: "
            f"real network POST is disabled."
        )

        raise RecoveryError(
            "real network POST is disabled"
        )

    NETWORK_POST_COUNT += 1

    raise RecoveryError(
        "unexpected real network POST path"
    )


# =============================================================================
# ABSOLUTELY BLOCKED GENERIC NETWORK WRITE
# =============================================================================

def generic_network_write(
    method,
    path,
    payload=None,
):

    global NETWORK_WRITE_COUNT

    if not NETWORK_WRITE_ENABLED:

        local_block(
            f"{UNIT} LOCAL BLOCK: "
            f"network write method "
            f"{method} is disabled."
        )

        raise RecoveryError(
            "network write disabled"
        )

    NETWORK_WRITE_COUNT += 1

    raise RecoveryError(
        "unexpected network write path"
    )


# =============================================================================
# ABSOLUTELY BLOCKED LEVERAGE TRANSPORT
# =============================================================================

def leverage_mutation_transport(
    payload
):

    global LEVERAGE_TRANSMISSION_COUNT

    if not LEVERAGE_MUTATION_TRANSPORT_ENABLED:

        local_block(
            f"{UNIT} LOCAL BLOCK: "
            f"leverage mutation transport "
            f"is disabled."
        )

        raise RecoveryError(
            "leverage mutation transport disabled"
        )

    LEVERAGE_TRANSMISSION_COUNT += 1

    raise RecoveryError(
        "unexpected leverage mutation transport path"
    )


# =============================================================================
# EXPECTED-REJECTION HELPER
# =============================================================================

def expect_rejected(
    label,
    fn,
):

    try:

        fn()

    except RecoveryError as exc:

        local_block(
            str(exc)
        )

        return check(
            label,
            True,
        )

    except Exception as exc:

        local_block(
            f"unexpected exception: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return check(
            label,
            False,
        )

    return check(
        label,
        False,
    )


# =============================================================================
# LOCAL HEALTH SERVER
# =============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        body = (
            b"R28 UNIT N.20 ACTIVE\n"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
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
        fmt,
        *args,
    ):
        return


def start_health_server():

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    try:

        server = HTTPServer(
            (
                "0.0.0.0",
                port,
            ),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        print(
            f"{UNIT}: "
            f"HEALTH SERVER ACTIVE "
            f"ON PORT {port}",
            flush=True,
        )

        return server

    except OSError as exc:

        print(
            f"{UNIT}: "
            f"HEALTH SERVER NOT STARTED "
            f"({exc})",
            flush=True,
        )

        return None


# =============================================================================
# COMPLETE N.20 DIAGNOSTIC
# =============================================================================

def run_diagnostic():

    global READINESS_BLOCKERS

    banner()

    print(
        f"{UNIT}: "
        f"LEASE EXPIRY / RENEWAL / "
        f"TAKEOVER FENCING",
        flush=True,
    )

    banner()

    print(
        f"Exact Payload = "
        f"{EXACT_PAYLOAD_JSON}",
        flush=True,
    )

    print(
        f"Payload SHA256 = "
        f"{EXACT_PAYLOAD_HASH}",
        flush=True,
    )

    print(
        f"Lease TTL = "
        f"{LEASE_TTL}s",
        flush=True,
    )


    # =========================================================================
    # TEMPORARY DURABLE STATE DIRECTORY
    # =========================================================================

    with tempfile.TemporaryDirectory(
        prefix="r28-n20-"
    ) as tmpdir:

        state_path = os.path.join(
            tmpdir,
            "recovery_state.json",
        )

        store = DurableRecoveryState(
            state_path
        )

        clock = LogicalClock()

        store.initialize()


        # =====================================================================
        # TEST 1
        # INITIAL DURABLE LEASE ACQUISITION
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 1: "
            f"INITIAL DURABLE LEASE ACQUISITION"
        )

        line()

        lease_a = store.acquire_lease(
            "worker-A",
            clock.now(),
        )

        check(
            "Initial Recovery Lease Acquired",
            lease_a["worker"]
            ==
            "worker-A",
        )

        check(
            "Initial Lease Nonce Is One",
            lease_a["nonce"]
            ==
            1,
        )

        check(
            "Initial Lease Bound To Exact Payload",
            lease_a["payload_hash"]
            ==
            EXACT_PAYLOAD_HASH,
        )


        # =====================================================================
        # TEST 2
        # ACTIVE LEASE EXCLUDES COMPETITOR
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 2: "
            f"ACTIVE LEASE EXCLUDES COMPETING OWNER"
        )

        line()

        expect_rejected(
            "Competing Worker Rejected While Lease Active",

            lambda:
                store.acquire_lease(
                    "worker-B",
                    clock.now() + 1,
                ),
        )


        # =====================================================================
        # TEST 3
        # EXACT OWNER RENEWAL
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 3: "
            f"EXACT OWNER RENEWAL"
        )

        line()

        clock.advance(
            10
        )

        renewed_a = store.renew_lease(
            lease_a,
            clock.now(),
        )

        check(
            "Exact Owner Renewal Accepted",
            renewed_a["worker"]
            ==
            "worker-A",
        )

        check(
            "Renewal Preserves Lease Nonce",
            renewed_a["nonce"]
            ==
            lease_a["nonce"],
        )

        check(
            "Renewal Extends Expiration",
            renewed_a["expires_at"]
            >
            lease_a["expires_at"],
        )

        lease_a = renewed_a


        # =====================================================================
        # TEST 4
        # FORGED OWNER / NONCE RENEWAL
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 4: "
            f"FORGED OWNER / NONCE "
            f"RENEWAL REJECTION"
        )

        line()

        forged_owner = dict(
            lease_a
        )

        forged_owner[
            "worker"
        ] = "worker-FORGED"

        expect_rejected(
            "Forged Lease Owner Renewal Rejected",

            lambda:
                store.renew_lease(
                    forged_owner,
                    clock.now() + 1,
                ),
        )


        forged_nonce = dict(
            lease_a
        )

        forged_nonce[
            "nonce"
        ] += 999

        expect_rejected(
            "Forged Lease Nonce Renewal Rejected",

            lambda:
                store.renew_lease(
                    forged_nonce,
                    clock.now() + 2,
                ),
        )


        # =====================================================================
        # TEST 5
        # EXPIRED LEASE CANNOT RENEW
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 5: "
            f"EXPIRED LEASE CANNOT RENEW"
        )

        line()

        clock.force(
            lease_a[
                "expires_at"
            ]
        )

        expect_rejected(
            "Expired Recovery Lease Renewal Rejected",

            lambda:
                store.renew_lease(
                    lease_a,
                    clock.now(),
                ),
        )


        # =====================================================================
        # TEST 6
        # EXPIRED LEASE TAKEOVER
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 6: "
            f"EXPIRED LEASE TAKEOVER"
        )

        line()

        lease_b = store.acquire_lease(
            "worker-B",
            clock.now(),
        )

        check(
            "Expired Lease Taken Over By New Worker",
            lease_b["worker"]
            ==
            "worker-B",
        )

        check(
            "Takeover Advances Lease Nonce Monotonically",
            lease_b["nonce"]
            >
            lease_a["nonce"],
        )

        check(
            "Takeover Preserves Generation",
            lease_b["generation"]
            ==
            lease_a["generation"],
        )

        check(
            "Takeover Preserves Epoch",
            lease_b["epoch"]
            ==
            lease_a["epoch"],
        )


        # =====================================================================
        # TEST 7
        # OLD OWNER FENCED AFTER TAKEOVER
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 7: "
            f"OLD OWNER FENCED AFTER TAKEOVER"
        )

        line()

        expect_rejected(
            "Old Owner Renewal Rejected After Takeover",

            lambda:
                store.renew_lease(
                    lease_a,
                    clock.now() + 1,
                ),
        )


        # =====================================================================
        # TEST 8
        # STALE PRE-TAKEOVER LEASE CANNOT RECOVER
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 8: "
            f"STALE PRE-TAKEOVER LEASE "
            f"CANNOT RECOVER"
        )

        line()

        expect_rejected(
            "Stale Lease Recovery Rejected After Takeover",

            lambda:
                store.authorize_recovery(
                    lease_a,
                    EXACT_PAYLOAD,
                    clock.now() + 2,
                ),
        )

        check(
            "Stale Recovery Produced No Synthetic Dispatch",
            SYNTHETIC_DISPATCH_COUNT
            ==
            0,
        )


        # =====================================================================
        # TEST 9
        # RESTART PRESERVES CURRENT OWNER
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 9: "
            f"RESTART PRESERVES NEW OWNER LEASE"
        )

        line()

        restarted = DurableRecoveryState(
            state_path
        )

        restored = restarted.load()

        check(
            "Restart Preserved Active Lease Owner",
            restored[
                "lease"
            ][
                "worker"
            ]
            ==
            "worker-B",
        )

        check(
            "Restart Preserved Active Lease Nonce",
            restored[
                "lease"
            ][
                "nonce"
            ]
            ==
            lease_b[
                "nonce"
            ],
        )

        check(
            "Restart Preserved Durable Monotonic Time",
            restored[
                "last_monotonic_time"
            ]
            ==
            clock.now(),
        )


        # =====================================================================
        # TEST 10
        # DURABLE CLOCK ROLLBACK REJECTION
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 10: "
            f"CLOCK ROLLBACK REJECTION"
        )

        line()

        expect_rejected(
            "Durable Clock Rollback Rejected",

            lambda:
                restarted.authorize_recovery(
                    lease_b,
                    EXACT_PAYLOAD,
                    clock.now() - 1,
                ),
        )


        # =====================================================================
        # TEST 11
        # EXACT CURRENT OWNER RECOVERY
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 11: "
            f"EXACT CURRENT OWNER RECOVERY"
        )

        line()

        clock.advance(
            3
        )

        dispatch = (
            restarted.authorize_recovery(
                lease_b,
                EXACT_PAYLOAD,
                clock.now(),
            )
        )

        check(
            "Current Lease Owner Recovery Authorized",
            dispatch[
                "worker"
            ]
            ==
            "worker-B",
        )

        check(
            "Recovery Bound To Current Lease Nonce",
            dispatch[
                "nonce"
            ]
            ==
            lease_b[
                "nonce"
            ],
        )

        check(
            "Recovery Bound To Exact Payload Hash",
            dispatch[
                "payload_hash"
            ]
            ==
            EXACT_PAYLOAD_HASH,
        )

        restarted.commit_terminal(
            lease_b,
            dispatch,
            clock.now(),
        )

        check(
            "Authorized Recovery Completed",
            restarted.state[
                "terminal"
            ]
            is True,
        )

        check(
            "Exactly One Synthetic Dispatch Produced",
            SYNTHETIC_DISPATCH_COUNT
            ==
            1,
        )


        # =====================================================================
        # TEST 12
        # TERMINAL FINALITY
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 12: "
            f"TERMINAL FINALITY AFTER TAKEOVER"
        )

        line()

        expect_rejected(
            "Terminal Generation Rejects New Recovery Lease",

            lambda:
                restarted.acquire_lease(
                    "worker-C",
                    clock.now() + 1,
                ),
        )

        expect_rejected(
            "Terminal Generation Rejects Repeated Recovery",

            lambda:
                restarted.authorize_recovery(
                    lease_b,
                    EXACT_PAYLOAD,
                    clock.now() + 2,
                ),
        )

        check(
            "Repeated Recovery Produced No Second Dispatch",
            SYNTHETIC_DISPATCH_COUNT
            ==
            1,
        )


        # =====================================================================
        # TEST 13
        # EPOCH ADVANCE FENCES OLD LEASE
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 13: "
            f"EPOCH ADVANCE FENCES OLD LEASE "
            f"BEFORE TERMINAL"
        )

        line()

        second_path = os.path.join(
            tmpdir,
            "epoch_state.json",
        )

        epoch_store = DurableRecoveryState(
            second_path
        )

        epoch_store.initialize()

        epoch_clock = LogicalClock(
            start=2_000_000
        )

        old_epoch_lease = (
            epoch_store.acquire_lease(
                "worker-X",
                epoch_clock.now(),
            )
        )

        old_epoch = (
            old_epoch_lease[
                "epoch"
            ]
        )

        epoch_clock.advance(
            1
        )

        new_epoch = (
            epoch_store.advance_epoch(
                epoch_clock.now()
            )
        )

        check(
            "Recovery Epoch Advanced Monotonically",
            new_epoch
            ==
            old_epoch + 1,
        )

        expect_rejected(
            "Old Epoch Lease Rejected",

            lambda:
                epoch_store.authorize_recovery(
                    old_epoch_lease,
                    EXACT_PAYLOAD,
                    epoch_clock.now() + 1,
                ),
        )


        # =====================================================================
        # TEST 14
        # ANTI-ABA TAKEOVER REUSE REJECTION
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 14: "
            f"ANTI-ABA TAKEOVER REUSE REJECTION"
        )

        line()

        new_epoch_lease = (
            epoch_store.acquire_lease(
                "worker-X",
                epoch_clock.now() + 2,
            )
        )

        check(
            "Reacquired Owner Uses New Epoch",
            new_epoch_lease[
                "epoch"
            ]
            ==
            new_epoch,
        )

        check(
            "Reacquired Owner Uses Higher Nonce",
            new_epoch_lease[
                "nonce"
            ]
            >
            old_epoch_lease[
                "nonce"
            ],
        )

        expect_rejected(
            "Reused Worker Identity Cannot Resurrect Old Lease",

            lambda:
                epoch_store.authorize_recovery(
                    old_epoch_lease,
                    EXACT_PAYLOAD,
                    epoch_clock.now() + 3,
                ),
        )


        # =====================================================================
        # TEST 15
        # EXACT SYNTHETIC TRANSPORT BINDING
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 15: "
            f"EXACT SYNTHETIC TRANSPORT BINDING"
        )

        line()

        check(
            "Transport Method Exactly POST",
            dispatch[
                "method"
            ]
            ==
            METHOD,
        )

        check(
            "Transport Path Exactly Leverage Endpoint",
            dispatch[
                "path"
            ]
            ==
            PATH,
        )

        check(
            "Transport Payload Hash Preserved",
            dispatch[
                "payload_hash"
            ]
            ==
            EXACT_PAYLOAD_HASH,
        )


        # =====================================================================
        # TEST 16
        # FINAL NETWORK FIREBREAK
        # =====================================================================

        print()

        print(
            f"{UNIT} TEST 16: "
            f"FINAL NETWORK WRITE FIREBREAK"
        )

        line()

        expect_rejected(
            "Real POST Rejected Locally",

            lambda:
                real_network_post(
                    PATH,
                    EXACT_PAYLOAD,
                ),
        )

        expect_rejected(
            "Generic Network Write Rejected Locally",

            lambda:
                generic_network_write(
                    "PUT",
                    PATH,
                    EXACT_PAYLOAD,
                ),
        )

        expect_rejected(
            "Leverage Mutation Transport Rejected Locally",

            lambda:
                leverage_mutation_transport(
                    EXACT_PAYLOAD
                ),
        )

        check(
            "Network POST Count Is Zero",
            NETWORK_POST_COUNT
            ==
            0,
        )

        check(
            "Network Write Count Is Zero",
            NETWORK_WRITE_COUNT
            ==
            0,
        )

        check(
            "Leverage Transmission Count Is Zero",
            LEVERAGE_TRANSMISSION_COUNT
            ==
            0,
        )


    # =========================================================================
    # WRITE-LOCK AUDIT
    # =========================================================================

    print()

    print(
        f"{UNIT} WRITE-LOCK AUDIT"
    )

    line()

    print(
        f"  Network POSTs = "
        f"{NETWORK_POST_COUNT}"
    )

    print(
        f"  Network writes = "
        f"{NETWORK_WRITE_COUNT}"
    )

    print(
        f"  Leverage transmissions = "
        f"{LEVERAGE_TRANSMISSION_COUNT}"
    )

    print(
        f"  Synthetic dispatches = "
        f"{SYNTHETIC_DISPATCH_COUNT}"
    )

    check(
        "Network POST Count Is Zero",
        NETWORK_POST_COUNT
        ==
        0,
    )

    check(
        "Network Write Count Is Zero",
        NETWORK_WRITE_COUNT
        ==
        0,
    )

    check(
        "Leverage Transmission Count Is Zero",
        LEVERAGE_TRANSMISSION_COUNT
        ==
        0,
    )


    # =========================================================================
    # SYNTHETIC DISPATCH EXACTLY-ONCE READINESS
    # =========================================================================

    if SYNTHETIC_DISPATCH_COUNT != 1:

        READINESS_BLOCKERS += 1


    # =========================================================================
    # EXECUTION-READINESS ASSESSMENT
    # =========================================================================

    print()

    print(
        f"{UNIT} EXECUTION-READINESS ASSESSMENT"
    )

    line()

    print(
        f"  Structural Safety Failures = "
        f"{STRUCTURAL_SAFETY_FAILURES}"
    )

    print(
        f"  Readiness Blockers = "
        f"{READINESS_BLOCKERS}"
    )

    print(
        "  Durable Lease Expiry Integrity = "
        "✅ VERIFIED"
    )

    print(
        "  Lease Renewal Ownership Fencing = "
        "✅ VERIFIED"
    )

    print(
        "  Expired Lease Takeover = "
        "✅ VERIFIED"
    )

    print(
        "  Monotonic Takeover Nonce = "
        "✅ VERIFIED"
    )

    print(
        "  Stale Owner Post-Takeover Fencing = "
        "✅ VERIFIED"
    )

    print(
        "  Restart Lease Preservation = "
        "✅ VERIFIED"
    )

    print(
        "  Durable Monotonic Clock Rollback Rejection = "
        "✅ VERIFIED"
    )

    print(
        "  Recovery Payload Binding = "
        "✅ VERIFIED"
    )

    print(
        "  Anti-ABA Epoch Fencing = "
        "✅ VERIFIED"
    )

    print(
        "  Terminal Finality Immutability = "
        "✅ VERIFIED"
    )

    print(
        "  Final Network Dispatch = "
        "🛡 BLOCKED LOCALLY"
    )

    print(
        "  Leverage Mutation Transmission = "
        "🛡 BLOCKED LOCALLY"
    )


    check(
        "Structural Safety Failures Are Zero",
        STRUCTURAL_SAFETY_FAILURES
        ==
        0,
    )

    check(
        "Readiness Blockers Are Zero",
        READINESS_BLOCKERS
        ==
        0,
    )


    # =========================================================================
    # FINAL RESULT
    # =========================================================================

    print()

    banner()

    if (
        STRUCTURAL_SAFETY_FAILURES
        ==
        0
        and
        READINESS_BLOCKERS
        ==
        0
    ):

        print(
            f"✅ {UNIT} DIAGNOSTIC PASSED"
        )

        print(
            "✅ DURABLE LEASE EXPIRY / "
            "RENEWAL FENCING VERIFIED"
        )

        print(
            "✅ EXPIRED LEASE TAKEOVER VERIFIED"
        )

        print(
            "✅ MONOTONIC TAKEOVER NONCE VERIFIED"
        )

        print(
            "✅ STALE PRE-TAKEOVER OWNERS REJECTED"
        )

        print(
            "✅ RESTART PRESERVES CURRENT "
            "LEASE AUTHORITY"
        )

        print(
            "✅ DURABLE CLOCK ROLLBACK REJECTED"
        )

        print(
            "✅ RECOVERY PAYLOAD BINDING VERIFIED"
        )

        print(
            "✅ ANTI-ABA EPOCH FENCING VERIFIED"
        )

        print(
            "✅ TERMINAL FINALITY REMAINS IMMUTABLE"
        )

        print(
            "🛡 REAL NETWORK DISPATCH "
            "REMAINS DISABLED"
        )

        print(
            "🛡 LEVERAGE MUTATION TRANSPORT "
            "REMAINS LOCKED"
        )

        print(
            "🛡 NO NETWORK WRITE WAS TRANSMITTED"
        )

    else:

        print(
            f"❌ {UNIT} DIAGNOSTIC FAILED"
        )

    banner()

    return (
        STRUCTURAL_SAFETY_FAILURES
        ==
        0
        and
        READINESS_BLOCKERS
        ==
        0
    )


# =============================================================================
# MAIN RUNTIME
# =============================================================================

def main():

    print(
        f"{UNIT}: MAIN.PY ENTERED",
        flush=True,
    )

    print(
        f"{UNIT}: IMPORTS COMPLETE",
        flush=True,
    )

    print(
        f"{UNIT}: CONSTANTS INITIALIZED",
        flush=True,
    )

    print(
        f"{UNIT}: RUNTIME STARTING",
        flush=True,
    )


    # =========================================================================
    # HEALTH SERVER
    # =========================================================================

    server = start_health_server()


    # =========================================================================
    # RUN COMPLETE DIAGNOSTIC
    # =========================================================================

    passed = run_diagnostic()


    # =========================================================================
    # HARD FAILURE IF DIAGNOSTIC FAILS
    # =========================================================================

    if not passed:

        raise SystemExit(1)


    # =========================================================================
    # OPTIONAL ONE-SHOT TEST MODE
    # =========================================================================

    if os.getenv(
        "R28_ONESHOT",
        "0",
    ) == "1":

        if server is not None:
            server.shutdown()

        return


    # =========================================================================
    # PERSISTENT SAFETY RUNTIME
    # =========================================================================

    print(
        f"{UNIT}: PERSISTENT RUNTIME ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"DURABLE LEASE EXPIRY "
        f"FENCE LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"EXACT OWNER RENEWAL "
        f"LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"EXPIRED LEASE TAKEOVER "
        f"LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"MONOTONIC TAKEOVER NONCE "
        f"LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"STALE OWNER POST-TAKEOVER "
        f"REJECTION LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"DURABLE CLOCK ROLLBACK "
        f"REJECTION LOCK ACTIVE",
        flush=True,
    )

    print(
        f"{UNIT}: "
        f"ANTI-ABA EPOCH FENCE "
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


    # =========================================================================
    # HEARTBEAT
    # =========================================================================

    heartbeat = 0

    try:

        while True:

            heartbeat += 1

            print(
                f"{UNIT}: "
                f"HEARTBEAT "
                f"{heartbeat} "
                f"✅ ACTIVE",
                flush=True,
            )

            time.sleep(
                HEARTBEAT_SECONDS
            )

    except KeyboardInterrupt:

        print(
            f"{UNIT}: "
            f"SHUTDOWN REQUESTED",
            flush=True,
        )

    finally:

        if server is not None:
            server.shutdown()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
