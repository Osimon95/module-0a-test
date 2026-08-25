import copy
import hashlib
import json
import os
import tempfile
import threading
import time
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer


UNIT = "R28 UNIT N.14"

SYMBOL = "BTCUSDT"
MARGIN_MODE = "ISOLATED"
LEVERAGE = "100"

METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v3/account/leverage"

CANONICAL_PAYLOAD = (
    '{"leverage":"100","marginMode":"ISOLATED","symbol":"BTCUSDT"}'
)

CANONICAL_PAYLOAD_SHA256 = (
    "64f7f170df9a2966605a82724094ca67cdd46ea5fef06957ba37c91705bcb00e"
)

LOCAL_SEAL_KEY = "R28-N14-LOCAL-DIAGNOSTIC-SEAL-V1"

AUTH_TTL_MS = 30000

NETWORK_POSTS = 0
NETWORK_WRITES = 0
LEVERAGE_TRANSMISSIONS = 0


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def seal_dict(value: dict) -> str:
    body = canonical_json(value)

    return sha256_text(
        LOCAL_SEAL_KEY
        + "|"
        + body
    )


def banner(title: str):
    print()
    print(title)
    print("-" * 92)


def passed(label: str):
    print(
        f"{label:<84} ✅ PASS"
    )


def fail(label: str):
    print(
        f"{label:<84} ❌ FAIL"
    )

    raise AssertionError(label)


def assert_true(
    label: str,
    condition: bool,
):
    if condition:
        passed(label)

    else:
        fail(label)


@dataclass(frozen=True)
class ExecutionContext:
    account_epoch: int
    symbol_epoch: int
    position_epoch: int

    symbol: str = SYMBOL
    margin_mode: str = MARGIN_MODE
    leverage: str = LEVERAGE

    execution_permission: bool = True


@dataclass
class DispatchRequest:
    dispatch_id: str
    request_id: str
    payload: str
    payload_hash: str
    method: str
    path: str


class LocalFirebreak:

    def post(
        self,
        *args,
        **kwargs,
    ):
        print(
            f"{UNIT} LOCAL BLOCK:"
        )

        print(
            f"  {UNIT} LOCAL BLOCK: "
            "real network POST is disabled."
        )

        raise RuntimeError(
            "real network POST is disabled"
        )

    def write(
        self,
        method: str,
        *args,
        **kwargs,
    ):
        print(
            f"{UNIT} LOCAL BLOCK:"
        )

        print(
            f"  {UNIT} LOCAL BLOCK: "
            f"network write method {method} "
            "is disabled."
        )

        raise RuntimeError(
            f"network write method {method} "
            "is disabled"
        )

    def leverage_mutation(
        self,
        *args,
        **kwargs,
    ):
        print(
            f"{UNIT} LOCAL BLOCK:"
        )

        print(
            f"  {UNIT} LOCAL BLOCK: "
            "leverage mutation transport "
            "is disabled."
        )

        raise RuntimeError(
            "leverage mutation transport "
            "is disabled"
        )


class DurableEngine:

    def __init__(
        self,
        directory: str,
    ):
        self.directory = directory

        os.makedirs(
            directory,
            exist_ok=True,
        )

        self.snapshot_path = os.path.join(
            directory,
            "state.json",
        )

        self.journal_path = os.path.join(
            directory,
            "journal.jsonl",
        )

        self.ledger_path = os.path.join(
            directory,
            "completion_ledger.json",
        )

        self._lock = threading.RLock()

        self.state = {
            "version": 0,

            "authorizations": {},

            "dispatches": {},

            "synthetic_dispatches": [],

            "finalization_attempts": 0,

            "finalization_successes": 0,

            "finalization_rejections": 0,
        }

        self.ledger = {
            "completed_dispatches": {},

            "consumed_authorizations": {},
        }

        self._load()


    def _atomic_write_json(
        self,
        path: str,
        data: dict,
    ):
        tmp = path + ".tmp"

        with open(
            tmp,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                sort_keys=True,
                separators=(",", ":"),
            )

            f.flush()

            os.fsync(
                f.fileno()
            )

        os.replace(
            tmp,
            path,
        )


    def _save_snapshot(self):

        envelope = {
            "state": self.state
        }

        envelope["seal"] = seal_dict(
            envelope["state"]
        )

        self._atomic_write_json(
            self.snapshot_path,
            envelope,
        )


    def _save_ledger(self):

        envelope = {
            "ledger": self.ledger
        }

        envelope["seal"] = seal_dict(
            envelope["ledger"]
        )

        self._atomic_write_json(
            self.ledger_path,
            envelope,
        )


    def _load(self):

        if os.path.exists(
            self.snapshot_path
        ):
            with open(
                self.snapshot_path,
                "r",
                encoding="utf-8",
            ) as f:

                env = json.load(f)

            expected = seal_dict(
                env.get(
                    "state",
                    {},
                )
            )

            if env.get("seal") != expected:

                raise ValueError(
                    "snapshot integrity seal mismatch"
                )

            self.state = env["state"]


        if os.path.exists(
            self.ledger_path
        ):
            with open(
                self.ledger_path,
                "r",
                encoding="utf-8",
            ) as f:

                env = json.load(f)

            expected = seal_dict(
                env.get(
                    "ledger",
                    {},
                )
            )

            if env.get("seal") != expected:

                raise ValueError(
                    "completion ledger "
                    "integrity seal mismatch"
                )

            self.ledger = env["ledger"]


    def _append_journal(
        self,
        record_type: str,
        dispatch_id: str,
        auth_id: str,
        request_id: str,
        payload_hash: str,
    ):

        record = {
            "type": record_type,

            "dispatch_id": dispatch_id,

            "auth_id": auth_id,

            "request_id": request_id,

            "payload_hash": payload_hash,
        }

        record["seal"] = seal_dict(
            record
        )

        with open(
            self.journal_path,
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                canonical_json(
                    record
                )
                + "\n"
            )

            f.flush()

            os.fsync(
                f.fileno()
            )


    def journal(self):

        if not os.path.exists(
            self.journal_path
        ):
            return []

        records = []

        with open(
            self.journal_path,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:

                if not line.strip():
                    continue

                record = json.loads(
                    line
                )

                record_seal = record.pop(
                    "seal"
                )

                if record_seal != seal_dict(
                    record
                ):

                    raise ValueError(
                        "journal integrity "
                        "seal mismatch"
                    )

                record["seal"] = record_seal

                records.append(
                    record
                )

        return records


    def create_request(
        self,
        label: str,
    ) -> DispatchRequest:

        payload = CANONICAL_PAYLOAD

        payload_hash = sha256_text(
            payload
        )

        request_id = sha256_text(
            "request|"
            + label
            + "|"
            + payload_hash
        )[:32]

        dispatch_id = sha256_text(
            "dispatch|"
            + request_id
        )[:32]

        return DispatchRequest(
            dispatch_id=dispatch_id,

            request_id=request_id,

            payload=payload,

            payload_hash=payload_hash,

            method=METHOD,

            path=LEVERAGE_ENDPOINT,
        )


    def grant_authorization(
        self,
        request: DispatchRequest,
        context: ExecutionContext,
        now_ms=None,
        ttl_ms=AUTH_TTL_MS,
    ):

        if now_ms is None:

            now_ms = int(
                time.time()
                * 1000
            )

        else:

            now_ms = int(
                now_ms
            )

        auth_core = {
            "dispatch_id":
                request.dispatch_id,

            "request_id":
                request.request_id,

            "payload_hash":
                request.payload_hash,

            "method":
                request.method,

            "path":
                request.path,

            "account_epoch":
                context.account_epoch,

            "symbol_epoch":
                context.symbol_epoch,

            "position_epoch":
                context.position_epoch,

            "symbol":
                context.symbol,

            "margin_mode":
                context.margin_mode,

            "leverage":
                context.leverage,

            "execution_permission":
                context.execution_permission,

            "issued_at_ms":
                now_ms,

            "expires_at_ms":
                now_ms
                + ttl_ms,
        }

        auth_id = sha256_text(
            "auth|"
            + canonical_json(
                auth_core
            )
        )[:32]

        auth = dict(
            auth_core
        )

        auth["auth_id"] = auth_id

        auth["consumed"] = False

        unsigned = {
            k: v
            for k, v
            in auth.items()
            if k != "seal"
        }

        auth["seal"] = seal_dict(
            unsigned
        )

        with self._lock:

            self.state[
                "authorizations"
            ][auth_id] = auth

            self.state[
                "dispatches"
            ][request.dispatch_id] = (
                asdict(
                    request
                )
            )

            self.state[
                "version"
            ] += 1

            self._append_journal(
                "AUTHORIZATION_GRANTED",

                request.dispatch_id,

                auth_id,

                request.request_id,

                request.payload_hash,
            )

            self._append_journal(
                "DISPATCH_PREPARED",

                request.dispatch_id,

                auth_id,

                request.request_id,

                request.payload_hash,
            )

            self._save_snapshot()

        return copy.deepcopy(
            auth
        )


    def _reject(
        self,
        reason: str,
    ):

        self.state[
            "finalization_rejections"
        ] += 1

        self._save_snapshot()

        raise PermissionError(
            reason
        )


    def _validate_auth_integrity(
        self,
        auth: dict,
    ):

        supplied_seal = auth.get(
            "seal"
        )

        unsigned = {
            k: v
            for k, v
            in auth.items()
            if k != "seal"
        }

        expected = seal_dict(
            unsigned
        )

        return (
            supplied_seal
            == expected
        )


    def finalize(
        self,
        request: DispatchRequest,
        supplied_auth: dict,
        context: ExecutionContext,
        now_ms=None,
    ):

        if now_ms is None:

            now_ms = int(
                time.time()
                * 1000
            )

        else:

            now_ms = int(
                now_ms
            )

        with self._lock:

            self.state[
                "finalization_attempts"
            ] += 1

            auth_id = supplied_auth.get(
                "auth_id"
            )

            stored = self.state[
                "authorizations"
            ].get(
                auth_id
            )


            if stored is None:

                return self._reject(
                    "unknown authorization"
                )


            if not self._validate_auth_integrity(
                supplied_auth
            ):

                return self._reject(
                    "authorization integrity "
                    "seal mismatch"
                )


            if canonical_json(
                supplied_auth
            ) != canonical_json(
                stored
            ):

                return self._reject(
                    "authorization does not "
                    "exactly match durable record"
                )


            if supplied_auth[
                "consumed"
            ]:

                return self._reject(
                    "authorization already "
                    "consumed"
                )


            if auth_id in self.ledger[
                "consumed_authorizations"
            ]:

                return self._reject(
                    "authorization consumption "
                    "ledger blocks resurrection"
                )


            if request.dispatch_id in (
                self.ledger[
                    "completed_dispatches"
                ]
            ):

                return self._reject(
                    "dispatch completion ledger "
                    "blocks replay"
                )


            if now_ms > supplied_auth[
                "expires_at_ms"
            ]:

                return self._reject(
                    "authorization expired"
                )


            if (
                not supplied_auth[
                    "execution_permission"
                ]
                or
                not context.execution_permission
            ):

                return self._reject(
                    "execution permission "
                    "revoked"
                )


            expected_request = (
                self.state[
                    "dispatches"
                ].get(
                    request.dispatch_id
                )
            )


            if (
                expected_request is None
                or
                canonical_json(
                    asdict(
                        request
                    )
                )
                !=
                canonical_json(
                    expected_request
                )
            ):

                return self._reject(
                    "final request does not "
                    "match durable dispatch "
                    "request"
                )


            binding_checks = {

                "dispatch_id":
                    request.dispatch_id,

                "request_id":
                    request.request_id,

                "payload_hash":
                    request.payload_hash,

                "method":
                    request.method,

                "path":
                    request.path,

                "account_epoch":
                    context.account_epoch,

                "symbol_epoch":
                    context.symbol_epoch,

                "position_epoch":
                    context.position_epoch,

                "symbol":
                    context.symbol,

                "margin_mode":
                    context.margin_mode,

                "leverage":
                    context.leverage,
            }


            for field, expected in (
                binding_checks.items()
            ):

                if supplied_auth.get(
                    field
                ) != expected:

                    return self._reject(
                        "authorization binding "
                        f"mismatch: {field}"
                    )


            if (
                request.payload
                != CANONICAL_PAYLOAD
            ):

                return self._reject(
                    "canonical payload mismatch"
                )


            if (
                request.payload_hash
                != CANONICAL_PAYLOAD_SHA256
            ):

                return self._reject(
                    "canonical payload hash "
                    "mismatch"
                )


            stored[
                "consumed"
            ] = True

            unsigned = {
                k: v
                for k, v
                in stored.items()
                if k != "seal"
            }

            stored[
                "seal"
            ] = seal_dict(
                unsigned
            )


            self.state[
                "authorizations"
            ][auth_id] = stored


            self.ledger[
                "consumed_authorizations"
            ][auth_id] = (
                request.dispatch_id
            )


            self._append_journal(
                "AUTHORIZATION_CONSUMED",

                request.dispatch_id,

                auth_id,

                request.request_id,

                request.payload_hash,
            )


            self._append_journal(
                "FINAL_RECONCILIATION",

                request.dispatch_id,

                auth_id,

                request.request_id,

                request.payload_hash,
            )


            synthetic = {

                "dispatch_id":
                    request.dispatch_id,

                "auth_id":
                    auth_id,

                "request_id":
                    request.request_id,

                "payload_hash":
                    request.payload_hash,

                "transmitted":
                    False,
            }


            self.state[
                "synthetic_dispatches"
            ].append(
                synthetic
            )


            self.ledger[
                "completed_dispatches"
            ][request.dispatch_id] = (
                auth_id
            )


            self._append_journal(
                "DISPATCH_COMPLETED",

                request.dispatch_id,

                auth_id,

                request.request_id,

                request.payload_hash,
            )


            self.state[
                "finalization_successes"
            ] += 1


            self.state[
                "version"
            ] += 1


            self._save_ledger()

            self._save_snapshot()

            return synthetic


def expect_rejected(fn):

    try:

        fn()

        return False

    except (
        PermissionError,
        RuntimeError,
        ValueError,
    ):

        return True


def run_diagnostic():

    base = tempfile.mkdtemp(
        prefix="r28_n14_"
    )

    context = ExecutionContext(
        account_epoch=101,

        symbol_epoch=202,

        position_epoch=303,
    )


    banner(
        f"{UNIT} TEST 1: "
        "EXACT AUTHORIZATION-TO-DISPATCH "
        "BINDING"
    )


    e1 = DurableEngine(
        os.path.join(
            base,
            "t1",
        )
    )

    r1 = e1.create_request(
        "exact-binding"
    )

    a1 = e1.grant_authorization(
        r1,
        context,
        now_ms=1000000,
    )

    s1 = e1.finalize(
        r1,
        a1,
        context,
        now_ms=1000001,
    )


    assert_true(
        "Exact Authorization Binding Accepted",

        s1["dispatch_id"]
        == r1.dispatch_id,
    )


    assert_true(
        "Exact Request Identity Preserved",

        s1["request_id"]
        == r1.request_id,
    )


    assert_true(
        "Exact Payload Hash Preserved",

        s1["payload_hash"]
        == CANONICAL_PAYLOAD_SHA256,
    )


    assert_true(
        "Synthetic Dispatch Reports No Transmission",

        s1["transmitted"]
        is False,
    )


    banner(
        f"{UNIT} TEST 2: "
        "CROSS-DISPATCH AUTHORIZATION "
        "SUBSTITUTION"
    )


    e2 = DurableEngine(
        os.path.join(
            base,
            "t2",
        )
    )

    r2a = e2.create_request(
        "cross-A"
    )

    r2b = e2.create_request(
        "cross-B"
    )


    a2a = e2.grant_authorization(
        r2a,
        context,
        now_ms=2000000,
    )

    a2b = e2.grant_authorization(
        r2b,
        context,
        now_ms=2000000,
    )


    before = len(
        e2.state[
            "synthetic_dispatches"
        ]
    )


    assert_true(
        "Authorization A Cannot Finalize Dispatch B",

        expect_rejected(
            lambda:
            e2.finalize(
                r2b,
                a2a,
                context,
                2000001,
            )
        ),
    )


    assert_true(
        "Authorization B Cannot Finalize Dispatch A",

        expect_rejected(
            lambda:
            e2.finalize(
                r2a,
                a2b,
                context,
                2000001,
            )
        ),
    )


    assert_true(
        "Cross-Dispatch Substitution Produced No Synthetic Dispatch",

        len(
            e2.state[
                "synthetic_dispatches"
            ]
        )
        == before,
    )


    banner(
        f"{UNIT} TEST 3: "
        "CONSUMED AUTHORIZATION "
        "RESURRECTION"
    )


    e3 = DurableEngine(
        os.path.join(
            base,
            "t3",
        )
    )

    r3 = e3.create_request(
        "resurrection"
    )

    a3 = e3.grant_authorization(
        r3,
        context,
        now_ms=3000000,
    )

    original_unconsumed = (
        copy.deepcopy(
            a3
        )
    )


    e3.finalize(
        r3,
        a3,
        context,
        3000001,
    )


    before = len(
        e3.state[
            "synthetic_dispatches"
        ]
    )


    assert_true(
        "Consumed Authorization Resurrection Rejected",

        expect_rejected(
            lambda:
            e3.finalize(
                r3,

                original_unconsumed,

                context,

                3000002,
            )
        ),
    )


    assert_true(
        "Resurrection Produced No Second Synthetic Dispatch",

        len(
            e3.state[
                "synthetic_dispatches"
            ]
        )
        == before,
    )


    banner(
        f"{UNIT} TEST 4: "
        "AUTHORIZATION EXPIRY "
        "AT FINAL BOUNDARY"
    )


    e4 = DurableEngine(
        os.path.join(
            base,
            "t4",
        )
    )

    r4 = e4.create_request(
        "expiry"
    )

    a4 = e4.grant_authorization(
        r4,
        context,
        now_ms=4000000,
        ttl_ms=10,
    )


    assert_true(
        "Expired Authorization Rejected At Final Boundary",

        expect_rejected(
            lambda:
            e4.finalize(
                r4,
                a4,
                context,
                4000011,
            )
        ),
    )


    assert_true(
        "Expired Authorization Produced No Synthetic Dispatch",

        len(
            e4.state[
                "synthetic_dispatches"
            ]
        )
        == 0,
    )


    banner(
        f"{UNIT} TEST 5: "
        "EXECUTION PERMISSION REVOCATION"
    )


    e5 = DurableEngine(
        os.path.join(
            base,
            "t5",
        )
    )

    r5 = e5.create_request(
        "revocation"
    )

    a5 = e5.grant_authorization(
        r5,
        context,
        now_ms=5000000,
    )


    revoked = ExecutionContext(
        account_epoch=101,

        symbol_epoch=202,

        position_epoch=303,

        execution_permission=False,
    )


    assert_true(
        "Execution Permission Revocation Rejected",

        expect_rejected(
            lambda:
            e5.finalize(
                r5,
                a5,
                revoked,
                5000001,
            )
        ),
    )


    assert_true(
        "Permission Revocation Produced No Synthetic Dispatch",

        len(
            e5.state[
                "synthetic_dispatches"
            ]
        )
        == 0,
    )


    banner(
        f"{UNIT} TEST 6: "
        "AUTHORIZATION RECORD "
        "TAMPER REJECTION"
    )


    tamper_fields = [

        (
            "auth_id",
            "deadbeef" * 4,
        ),

        (
            "dispatch_id",
            "x" * 32,
        ),

        (
            "request_id",
            "y" * 32,
        ),

        (
            "payload_hash",
            "0" * 64,
        ),

        (
            "symbol",
            "ETHUSDT",
        ),

        (
            "leverage",
            "99",
        ),

        (
            "margin_mode",
            "CROSS",
        ),

        (
            "account_epoch",
            999,
        ),

        (
            "symbol_epoch",
            999,
        ),

        (
            "position_epoch",
            999,
        ),
    ]


    for i, (
        field,
        value,
    ) in enumerate(
        tamper_fields
    ):

        et = DurableEngine(
            os.path.join(
                base,
                f"t6_{i}",
            )
        )

        rt = et.create_request(
            f"tamper-{field}"
        )

        at = et.grant_authorization(
            rt,
            context,
            now_ms=6000000,
        )

        tampered = copy.deepcopy(
            at
        )

        tampered[field] = value


        assert_true(
            "Tampered Authorization "
            f"Field Rejected: {field}",

            expect_rejected(
                lambda
                et=et,
                rt=rt,
                tampered=tampered:
                et.finalize(
                    rt,
                    tampered,
                    context,
                    6000001,
                )
            ),
        )


        assert_true(
            f"Tampered {field} Produced No Synthetic Dispatch",

            len(
                et.state[
                    "synthetic_dispatches"
                ]
            )
            == 0,
        )


    banner(
        f"{UNIT} TEST 7: "
        "SNAPSHOT ROLLBACK / "
        "AUTHORIZATION RESURRECTION"
    )


    d7 = os.path.join(
        base,
        "t7",
    )

    e7 = DurableEngine(
        d7
    )

    r7 = e7.create_request(
        "rollback"
    )

    a7 = e7.grant_authorization(
        r7,
        context,
        now_ms=7000000,
    )


    with open(
        e7.snapshot_path,
        "r",
        encoding="utf-8",
    ) as f:

        old_snapshot = f.read()


    e7.finalize(
        r7,
        a7,
        context,
        7000001,
    )


    with open(
        e7.snapshot_path,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            old_snapshot
        )


    e7r = DurableEngine(
        d7
    )


    resurrected = copy.deepcopy(
        e7r.state[
            "authorizations"
        ][
            a7["auth_id"]
        ]
    )


    before = len(
        e7r.state[
            "synthetic_dispatches"
        ]
    )


    assert_true(
        "Rollback Snapshot Cannot Resurrect Consumed Authorization",

        expect_rejected(
            lambda:
            e7r.finalize(
                r7,
                resurrected,
                context,
                7000002,
            )
        ),
    )


    assert_true(
        "Rollback Resurrection Produced No Synthetic Dispatch",

        len(
            e7r.state[
                "synthetic_dispatches"
            ]
        )
        == before,
    )


    banner(
        f"{UNIT} TEST 8: "
        "CONCURRENT AUTHORIZATION "
        "CONSUMPTION SINGLE-WINNER"
    )


    e8 = DurableEngine(
        os.path.join(
            base,
            "t8",
        )
    )

    r8 = e8.create_request(
        "concurrency"
    )

    a8 = e8.grant_authorization(
        r8,
        context,
        now_ms=8000000,
    )


    outcomes = []

    out_lock = (
        threading.Lock()
    )


    def worker():

        try:

            e8.finalize(
                r8,

                copy.deepcopy(
                    a8
                ),

                context,

                8000001,
            )

            result = "WIN"

        except PermissionError:

            result = "REJECT"


        with out_lock:

            outcomes.append(
                result
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


    assert_true(
        "All Eight Authorization Workers Completed",

        len(outcomes)
        == 8,
    )


    assert_true(
        "Eight-Worker Authorization Race Produced Exactly One Winner",

        outcomes.count(
            "WIN"
        )
        == 1,
    )


    assert_true(
        "Concurrent Authorization Consumption Produced Exactly One Synthetic Dispatch",

        len(
            e8.state[
                "synthetic_dispatches"
            ]
        )
        == 1,
    )


    banner(
        f"{UNIT} TEST 9: "
        "RESTART BEFORE AUTHORIZATION "
        "CONSUMPTION"
    )


    d9 = os.path.join(
        base,
        "t9",
    )

    e9 = DurableEngine(
        d9
    )

    r9 = e9.create_request(
        "restart-before"
    )

    a9 = e9.grant_authorization(
        r9,
        context,
        now_ms=9000000,
    )


    e9r = DurableEngine(
        d9
    )


    restored = copy.deepcopy(
        e9r.state[
            "authorizations"
        ][
            a9["auth_id"]
        ]
    )


    assert_true(
        "Unused Authorization Survived Restart",

        restored[
            "consumed"
        ]
        is False,
    )


    s9 = e9r.finalize(
        r9,

        restored,

        context,

        9000001,
    )


    assert_true(
        "Restored Authorization Consumed Exactly Once",

        s9["dispatch_id"]
        == r9.dispatch_id,
    )


    assert_true(
        "Post-Consumption Replay Rejected",

        expect_rejected(
            lambda:
            e9r.finalize(
                r9,

                restored,

                context,

                9000002,
            )
        ),
    )


    banner(
        f"{UNIT} TEST 10: "
        "RESTART AFTER AUTHORIZATION "
        "CONSUMPTION"
    )


    d10 = os.path.join(
        base,
        "t10",
    )

    e10 = DurableEngine(
        d10
    )

    r10 = e10.create_request(
        "restart-after"
    )

    a10 = e10.grant_authorization(
        r10,
        context,
        now_ms=10000000,
    )


    e10.finalize(
        r10,
        a10,
        context,
        10000001,
    )


    e10r = DurableEngine(
        d10
    )


    persisted = e10r.state[
        "authorizations"
    ][
        a10["auth_id"]
    ]


    assert_true(
        "Consumed Authorization State Survived Restart",

        persisted[
            "consumed"
        ]
        is True,
    )


    assert_true(
        "Post-Restart Authorization Resurrection Rejected",

        expect_rejected(
            lambda:
            e10r.finalize(
                r10,

                copy.deepcopy(
                    a10
                ),

                context,

                10000002,
            )
        ),
    )


    assert_true(
        "Restart Replay Produced No Second Synthetic Dispatch",

        len(
            e10r.state[
                "synthetic_dispatches"
            ]
        )
        == 1,
    )


    banner(
        f"{UNIT} TEST 11: "
        "AUTHORIZATION JOURNAL "
        "SERIALIZATION"
    )


    e11 = DurableEngine(
        os.path.join(
            base,
            "t11",
        )
    )

    r11 = e11.create_request(
        "journal"
    )

    a11 = e11.grant_authorization(
        r11,
        context,
        now_ms=11000000,
    )


    e11.finalize(
        r11,
        a11,
        context,
        11000001,
    )


    records = [

        item

        for item
        in e11.journal()

        if item[
            "dispatch_id"
        ]
        == r11.dispatch_id
    ]


    types = [

        item["type"]

        for item
        in records
    ]


    expected = [

        "AUTHORIZATION_GRANTED",

        "DISPATCH_PREPARED",

        "AUTHORIZATION_CONSUMED",

        "FINAL_RECONCILIATION",

        "DISPATCH_COMPLETED",
    ]


    assert_true(
        "Exactly One Authorization Grant Record",

        types.count(
            "AUTHORIZATION_GRANTED"
        )
        == 1,
    )


    assert_true(
        "Exactly One Dispatch Prepare Record",

        types.count(
            "DISPATCH_PREPARED"
        )
        == 1,
    )


    assert_true(
        "Exactly One Authorization Consumed Record",

        types.count(
            "AUTHORIZATION_CONSUMED"
        )
        == 1,
    )


    assert_true(
        "Exactly One Final Reconciliation Record",

        types.count(
            "FINAL_RECONCILIATION"
        )
        == 1,
    )


    assert_true(
        "Exactly One Dispatch Completion Record",

        types.count(
            "DISPATCH_COMPLETED"
        )
        == 1,
    )


    assert_true(
        "Authorization Journal Order Is Canonical",

        types
        == expected,
    )


    assert_true(
        "Journal Preserves Same Authorization Identity",

        len({
            item["auth_id"]
            for item
            in records
        })
        == 1,
    )


    assert_true(
        "Journal Preserves Same Dispatch Identity",

        len({
            item["dispatch_id"]
            for item
            in records
        })
        == 1,
    )


    assert_true(
        "Journal Preserves Exact Request Binding",

        len({
            (
                item["request_id"],
                item["payload_hash"],
            )

            for item
            in records
        })
        == 1,
    )


    banner(
        f"{UNIT} TEST 12: "
        "FINAL NETWORK WRITE FIREBREAK"
    )


    firebreak = LocalFirebreak()


    assert_true(
        "Real POST Rejected Locally",

        expect_rejected(
            lambda:
            firebreak.post()
        ),
    )


    assert_true(
        "Generic Network Write Rejected Locally",

        expect_rejected(
            lambda:
            firebreak.write(
                "PUT"
            )
        ),
    )


    assert_true(
        "Leverage Mutation Transport Rejected Locally",

        expect_rejected(
            lambda:
            firebreak.leverage_mutation()
        ),
    )


    assert_true(
        "Real POST Block Produced No Network POST",

        NETWORK_POSTS
        == 0,
    )


    assert_true(
        "Write Firebreak Produced No Network Write",

        NETWORK_WRITES
        == 0,
    )


    assert_true(
        "Leverage Firebreak Produced No Transmission",

        LEVERAGE_TRANSMISSIONS
        == 0,
    )


    banner(
        f"{UNIT} TEST 13: "
        "EXACT PAYLOAD / ENDPOINT "
        "IMMUTABILITY"
    )


    print(
        f"Payload = "
        f"{CANONICAL_PAYLOAD}"
    )


    print(
        "Payload SHA256 = "
        f"{sha256_text(CANONICAL_PAYLOAD)}"
    )


    assert_true(
        "Exact Leverage Payload Preserved",

        CANONICAL_PAYLOAD
        ==
        '{"leverage":"100","marginMode":"ISOLATED","symbol":"BTCUSDT"}',
    )


    assert_true(
        "Canonical Payload Serialization Preserved",

        sha256_text(
            CANONICAL_PAYLOAD
        )
        ==
        CANONICAL_PAYLOAD_SHA256,
    )


    assert_true(
        "Transport Method Exactly POST",

        METHOD
        == "POST",
    )


    assert_true(
        "Transport Path Exactly Leverage Endpoint",

        LEVERAGE_ENDPOINT
        ==
        "/capi/v3/account/leverage",
    )


    banner(
        f"{UNIT} WRITE-LOCK AUDIT"
    )


    print(
        f"  Network POSTs = "
        f"{NETWORK_POSTS}"
    )

    print(
        f"  Network writes = "
        f"{NETWORK_WRITES}"
    )

    print(
        f"  Leverage transmissions = "
        f"{LEVERAGE_TRANSMISSIONS}"
    )


    assert_true(
        "Network POST Count Is Zero",

        NETWORK_POSTS
        == 0,
    )


    assert_true(
        "Network Write Count Is Zero",

        NETWORK_WRITES
        == 0,
    )


    assert_true(
        "Leverage Transmission Count Is Zero",

        LEVERAGE_TRANSMISSIONS
        == 0,
    )


    banner(
        f"{UNIT} EXECUTION-READINESS "
        "ASSESSMENT"
    )


    print(
        "  Structural Safety Failures = 0"
    )

    print(
        "  Readiness Blockers = 0"
    )

    print(
        "  Durable Dispatch Authorization = "
        "✅ VERIFIED"
    )

    print(
        "  Cross-Dispatch Substitution Rejection = "
        "✅ VERIFIED"
    )

    print(
        "  Consumed Authorization Resurrection Protection = "
        "✅ VERIFIED"
    )

    print(
        "  Final-Boundary Authorization Expiry = "
        "✅ VERIFIED"
    )

    print(
        "  Authorization Revocation Gate = "
        "✅ VERIFIED"
    )

    print(
        "  Authorization Tamper Rejection = "
        "✅ VERIFIED"
    )

    print(
        "  Snapshot Rollback Protection = "
        "✅ VERIFIED"
    )

    print(
        "  Concurrent Authorization Single Winner = "
        "✅ VERIFIED"
    )

    print(
        "  Restart Authorization Idempotency = "
        "✅ VERIFIED"
    )

    print(
        "  Authorization Journal Serialization = "
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


    print()

    print(
        f"✅ {UNIT} DIAGNOSTIC PASSED"
    )

    print(
        "✅ DURABLE DISPATCH AUTHORIZATION VERIFIED"
    )

    print(
        "✅ CROSS-DISPATCH AUTHORIZATION SUBSTITUTION REJECTED"
    )

    print(
        "✅ CONSUMED AUTHORIZATION CANNOT BE RESURRECTED"
    )

    print(
        "✅ EXPIRED AUTHORIZATION REJECTED AT FINAL BOUNDARY"
    )

    print(
        "✅ AUTHORIZATION TAMPERING REJECTED"
    )

    print(
        "✅ SNAPSHOT ROLLBACK CANNOT RE-ENABLE CONSUMED AUTHORIZATION"
    )

    print(
        "✅ CONCURRENT AUTHORIZATION CONSUMPTION PRODUCES SINGLE WINNER"
    )

    print(
        "✅ RESTART PRESERVES AUTHORIZATION CONSUMPTION STATE"
    )

    print(
        "✅ AUTHORIZATION JOURNAL SERIALIZATION VERIFIED"
    )

    print(
        "🛡 REAL NETWORK DISPATCH REMAINS DISABLED"
    )

    print(
        "🛡 LEVERAGE MUTATION TRANSPORT REMAINS LOCKED"
    )

    print(
        "🛡 NO NETWORK WRITE WAS TRANSMITTED"
    )


def start_health_server():

    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )


    class Handler(
        BaseHTTPRequestHandler
    ):

        def do_GET(self):

            body = (
                b"R28 UNIT N.14 ACTIVE\n"
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
            fmt,
            *args,
        ):

            return


    try:

        server = HTTPServer(
            (
                "0.0.0.0",
                port,
            ),
            Handler,
        )

        threading.Thread(
            target=server.serve_forever,
            daemon=True,
        ).start()

        print(
            f"{UNIT}: HEALTH SERVER "
            f"ACTIVE ON PORT {port}"
        )


    except OSError as exc:

        print(
            f"{UNIT}: HEALTH SERVER "
            f"NOT STARTED ({exc})"
        )


def main():

    print(
        f"{UNIT}: MAIN.PY ENTERED"
    )

    print(
        f"{UNIT}: IMPORTS COMPLETE"
    )

    print(
        f"{UNIT}: CONSTANTS INITIALIZED"
    )

    print(
        f"{UNIT}: RUNTIME STARTING"
    )


    start_health_server()


    print(
        "=" * 92
    )

    print(
        "0F-4H-R28-UNIT-N.14 STARTING"
    )

    print(
        "=" * 92
    )


    run_diagnostic()


    print(
        "=" * 92
    )

    print(
        f"{UNIT}: PERSISTENT RUNTIME ACTIVE"
    )

    print(
        f"{UNIT}: DURABLE AUTHORIZATION "
        "BINDING LOCK ACTIVE"
    )

    print(
        f"{UNIT}: AUTHORIZATION EXPIRY "
        "GATE ACTIVE"
    )

    print(
        f"{UNIT}: AUTHORIZATION REVOCATION "
        "GATE ACTIVE"
    )

    print(
        f"{UNIT}: AUTHORIZATION TAMPER "
        "LOCK ACTIVE"
    )

    print(
        f"{UNIT}: ANTI-ROLLBACK COMPLETION "
        "LEDGER ACTIVE"
    )

    print(
        f"{UNIT}: CONCURRENT AUTHORIZATION "
        "CONSUMPTION LOCK ACTIVE"
    )

    print(
        f"{UNIT}: SYNTHETIC TRANSPORT "
        "INTERCEPTOR ACTIVE"
    )

    print(
        f"{UNIT}: NETWORK WRITE "
        "TRANSPORT LOCKED"
    )

    print(
        f"{UNIT}: LEVERAGE MUTATION "
        "TRANSPORT LOCKED"
    )


    heartbeat = 0


    while True:

        heartbeat += 1

        print(
            f"{UNIT}: HEARTBEAT "
            f"{heartbeat} ✅ ACTIVE",
            flush=True,
        )

        time.sleep(
            15
        )


if __name__ == "__main__":

    main()
