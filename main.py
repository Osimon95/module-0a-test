import os
import json
import time
import copy
import hmac
import hashlib
import threading
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Any, Optional


# =============================================================================
# R28 UNIT N.16
# DURABLE TERMINAL RECONCILIATION + FINALITY CHECKPOINT
# =============================================================================

UNIT = "R28 UNIT N.16"

SYMBOL = "BTCUSDT"
LEVERAGE = "100"
MARGIN_MODE = "ISOLATED"

METHOD = "POST"
LEVERAGE_ENDPOINT = "/capi/v3/account/setLeverage"


# =============================================================================
# HARD SAFETY LOCKS
# =============================================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
LEVERAGE_MUTATION_TRANSPORT_ENABLED = False


# =============================================================================
# LOCAL DIAGNOSTIC SEAL
# =============================================================================

SEAL_KEY = b"r28-n16-local-diagnostic-key"


# =============================================================================
# AUDIT COUNTERS
# =============================================================================

AUDIT = {
    "network_posts": 0,
    "network_writes": 0,
    "leverage_transmissions": 0,
    "synthetic_dispatches": 0,
    "reconciliations": 0,
    "finality_checkpoints": 0,
}


STORE_LOCK = threading.RLock()


# =============================================================================
# BASIC HELPERS
# =============================================================================

def canonical(obj: Any) -> str:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(
        text.encode()
    ).hexdigest()


def seal(obj: Dict[str, Any]) -> str:
    body = canonical(obj)

    return hmac.new(
        SEAL_KEY,
        body.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_seal(
    obj: Dict[str, Any],
    signature: str,
) -> bool:

    return hmac.compare_digest(
        seal(obj),
        signature,
    )


def banner(title: str):

    print()

    print(title)

    print("-" * 92)


def check(
    name: str,
    condition: bool,
):

    result = (
        "✅ PASS"
        if condition
        else "❌ FAIL"
    )

    print(
        f"{name:<82} {result}"
    )

    if not condition:
        raise AssertionError(name)


def local_block(message: str):

    print(
        f"{UNIT} LOCAL BLOCK:"
    )

    print(
        f"  {message}"
    )


# =============================================================================
# HARD NETWORK FIREBREAKS
# =============================================================================

def forbidden_post(
    *args,
    **kwargs,
):

    local_block(
        f"{UNIT} LOCAL BLOCK: "
        "real network POST is disabled."
    )

    raise PermissionError(
        "real network POST disabled"
    )


def forbidden_write(
    method: str,
    *args,
    **kwargs,
):

    local_block(
        f"{UNIT} LOCAL BLOCK: "
        f"network write method {method} "
        "is disabled."
    )

    raise PermissionError(
        f"network write {method} disabled"
    )


def forbidden_leverage_transport(
    *args,
    **kwargs,
):

    local_block(
        f"{UNIT} LOCAL BLOCK: "
        "leverage mutation transport "
        "is disabled."
    )

    raise PermissionError(
        "leverage mutation transport disabled"
    )


# =============================================================================
# DURABLE DISPATCH IDENTITY
# =============================================================================

@dataclass(frozen=True)
class DispatchIdentity:

    dispatch_id: str

    authorization_id: str

    intent_id: str

    request_id: str

    symbol: str

    payload_hash: str


# =============================================================================
# DURABLE RUNTIME RECORD
# =============================================================================

@dataclass
class RuntimeRecord:

    identity: DispatchIdentity

    authorization_consumed: bool = False

    synthetic_dispatched: bool = False

    reconciled: bool = False

    terminal_state: Optional[str] = None

    completion_ledger_written: bool = False

    finality_checkpoint_written: bool = False

    checkpoint_hash: Optional[str] = None

    generation: int = 0


# =============================================================================
# DURABLE STORE
# =============================================================================

class DurableStore:

    def __init__(self):

        self.records: Dict[
            str,
            RuntimeRecord,
        ] = {}

        self.journal = []

        self.completion_ledger: Dict[
            str,
            Dict[str, Any],
        ] = {}

        self.finality_checkpoints: Dict[
            str,
            Dict[str, Any],
        ] = {}


    # -------------------------------------------------------------------------
    # JOURNAL
    # -------------------------------------------------------------------------

    def _journal(
        self,
        event: str,
        record: RuntimeRecord,
    ):

        entry_body = {

            "seq":
                len(self.journal) + 1,

            "event":
                event,

            "dispatch_id":
                record.identity.dispatch_id,

            "authorization_id":
                record.identity.authorization_id,

            "intent_id":
                record.identity.intent_id,

            "request_id":
                record.identity.request_id,

            "payload_hash":
                record.identity.payload_hash,

            "generation":
                record.generation,
        }

        self.journal.append(
            {
                "body":
                    entry_body,

                "seal":
                    seal(entry_body),
            }
        )


    # -------------------------------------------------------------------------
    # CREATE DISPATCH RECORD
    # -------------------------------------------------------------------------

    def create(
        self,
        record: RuntimeRecord,
    ):

        with STORE_LOCK:

            did = (
                record
                .identity
                .dispatch_id
            )

            if did in self.records:

                raise ValueError(
                    "duplicate dispatch identity"
                )

            self.records[did] = (
                copy.deepcopy(record)
            )

            self._journal(
                "DISPATCH_CREATED",
                self.records[did],
            )


    # -------------------------------------------------------------------------
    # AUTHORIZATION CONSUMPTION
    # -------------------------------------------------------------------------

    def consume_authorization(
        self,
        dispatch_id: str,
    ):

        with STORE_LOCK:

            r = self.records[
                dispatch_id
            ]

            if r.authorization_consumed:

                raise ValueError(
                    "authorization replay blocked"
                )

            r.authorization_consumed = True

            r.generation += 1

            self._journal(
                "AUTHORIZATION_CONSUMED",
                r,
            )


    # -------------------------------------------------------------------------
    # SYNTHETIC DISPATCH
    # -------------------------------------------------------------------------

    def synthetic_dispatch(
        self,
        dispatch_id: str,
    ):

        with STORE_LOCK:

            r = self.records[
                dispatch_id
            ]

            if not r.authorization_consumed:

                raise ValueError(
                    "authorization must be "
                    "consumed before dispatch"
                )

            if r.synthetic_dispatched:

                raise ValueError(
                    "synthetic dispatch "
                    "replay blocked"
                )

            r.synthetic_dispatched = True

            r.generation += 1

            AUDIT[
                "synthetic_dispatches"
            ] += 1

            self._journal(
                "SYNTHETIC_DISPATCHED",
                r,
            )


    # -------------------------------------------------------------------------
    # TERMINAL RECONCILIATION
    # -------------------------------------------------------------------------

    def reconcile(
        self,
        dispatch_id: str,
        terminal_state: str = "COMPLETED",
    ):

        with STORE_LOCK:

            r = self.records[
                dispatch_id
            ]

            if not r.synthetic_dispatched:

                raise ValueError(
                    "cannot reconcile "
                    "before dispatch"
                )

            if r.reconciled:

                if (
                    r.terminal_state
                    != terminal_state
                ):

                    raise ValueError(
                        "terminal state "
                        "mutation rejected"
                    )

                return

            valid_terminal_states = {
                "COMPLETED",
                "REJECTED",
                "CANCELED",
                "EXPIRED",
            }

            if (
                terminal_state
                not in valid_terminal_states
            ):

                raise ValueError(
                    "invalid terminal state"
                )

            r.reconciled = True

            r.terminal_state = (
                terminal_state
            )

            r.generation += 1

            AUDIT[
                "reconciliations"
            ] += 1

            self._journal(
                "RECONCILED",
                r,
            )


    # -------------------------------------------------------------------------
    # COMPLETION LEDGER
    # -------------------------------------------------------------------------

    def write_completion_ledger(
        self,
        dispatch_id: str,
    ):

        with STORE_LOCK:

            r = self.records[
                dispatch_id
            ]

            if (
                not r.reconciled
                or r.terminal_state is None
            ):

                raise ValueError(
                    "completion ledger "
                    "requires reconciliation"
                )

            body = {

                "dispatch_id":
                    r.identity.dispatch_id,

                "authorization_id":
                    r.identity.authorization_id,

                "intent_id":
                    r.identity.intent_id,

                "request_id":
                    r.identity.request_id,

                "payload_hash":
                    r.identity.payload_hash,

                "terminal_state":
                    r.terminal_state,
            }

            existing = (
                self
                .completion_ledger
                .get(dispatch_id)
            )

            if existing is not None:

                if (
                    existing["body"] != body
                    or not verify_seal(
                        existing["body"],
                        existing["seal"],
                    )
                ):

                    raise ValueError(
                        "completion ledger "
                        "conflict or tamper detected"
                    )

                r.completion_ledger_written = True

                return

            self.completion_ledger[
                dispatch_id
            ] = {

                "body":
                    body,

                "seal":
                    seal(body),
            }

            r.completion_ledger_written = True

            r.generation += 1

            self._journal(
                "COMPLETION_LEDGER_WRITTEN",
                r,
            )


    # -------------------------------------------------------------------------
    # FINALITY CHECKPOINT
    # -------------------------------------------------------------------------

    def write_finality_checkpoint(
        self,
        dispatch_id: str,
    ):

        with STORE_LOCK:

            r = self.records[
                dispatch_id
            ]

            if not r.completion_ledger_written:

                raise ValueError(
                    "finality checkpoint "
                    "requires completion ledger"
                )

            ledger = (
                self
                .completion_ledger
                .get(dispatch_id)
            )

            if (
                not ledger
                or not verify_seal(
                    ledger["body"],
                    ledger["seal"],
                )
            ):

                raise ValueError(
                    "completion ledger "
                    "integrity failure"
                )

            body = {

                "dispatch_id":
                    r.identity.dispatch_id,

                "authorization_id":
                    r.identity.authorization_id,

                "intent_id":
                    r.identity.intent_id,

                "request_id":
                    r.identity.request_id,

                "payload_hash":
                    r.identity.payload_hash,

                "terminal_state":
                    r.terminal_state,

                "ledger_seal":
                    ledger["seal"],

                "journal_tail":
                    (
                        self.journal[-1]["seal"]
                        if self.journal
                        else None
                    ),
            }

            checkpoint_hash = (
                sha256_text(
                    canonical(body)
                )
            )

            existing = (
                self
                .finality_checkpoints
                .get(dispatch_id)
            )

            if existing is not None:

                if (
                    existing["body"]
                    != body
                    or
                    existing[
                        "checkpoint_hash"
                    ]
                    != checkpoint_hash
                ):

                    raise ValueError(
                        "finality checkpoint "
                        "conflict"
                    )

                if not verify_seal(
                    existing["body"],
                    existing["seal"],
                ):

                    raise ValueError(
                        "finality checkpoint "
                        "tamper detected"
                    )

                r.finality_checkpoint_written = True

                r.checkpoint_hash = (
                    checkpoint_hash
                )

                return

            self.finality_checkpoints[
                dispatch_id
            ] = {

                "body":
                    body,

                "checkpoint_hash":
                    checkpoint_hash,

                "seal":
                    seal(body),
            }

            r.finality_checkpoint_written = True

            r.checkpoint_hash = (
                checkpoint_hash
            )

            r.generation += 1

            AUDIT[
                "finality_checkpoints"
            ] += 1

            self._journal(
                "FINALITY_CHECKPOINT_WRITTEN",
                r,
            )


    # -------------------------------------------------------------------------
    # STRUCTURAL VALIDATION
    # -------------------------------------------------------------------------

    def validate_record(
        self,
        dispatch_id: str,
    ):

        with STORE_LOCK:

            r = self.records[
                dispatch_id
            ]


            # -------------------------------------------------------------
            # STATE DEPENDENCY VALIDATION
            # -------------------------------------------------------------

            if (
                r.synthetic_dispatched
                and
                not r.authorization_consumed
            ):

                raise ValueError(
                    "dispatch exists without "
                    "consumed authorization"
                )


            if (
                r.reconciled
                and
                not r.synthetic_dispatched
            ):

                raise ValueError(
                    "reconciliation exists "
                    "without dispatch"
                )


            if (
                r.completion_ledger_written
                and
                not r.reconciled
            ):

                raise ValueError(
                    "completion ledger exists "
                    "without reconciliation"
                )


            if (
                r.finality_checkpoint_written
                and
                not r.completion_ledger_written
            ):

                raise ValueError(
                    "finality checkpoint exists "
                    "without completion ledger"
                )


            # -------------------------------------------------------------
            # COMPLETION LEDGER VALIDATION
            # -------------------------------------------------------------

            if r.completion_ledger_written:

                ledger = (
                    self
                    .completion_ledger
                    .get(dispatch_id)
                )

                if not ledger:

                    raise ValueError(
                        "record says ledger exists "
                        "but ledger is missing"
                    )


                if not verify_seal(
                    ledger["body"],
                    ledger["seal"],
                ):

                    raise ValueError(
                        "completion ledger "
                        "seal mismatch"
                    )


                expected = {

                    "dispatch_id":
                        r.identity.dispatch_id,

                    "authorization_id":
                        r.identity.authorization_id,

                    "intent_id":
                        r.identity.intent_id,

                    "request_id":
                        r.identity.request_id,

                    "payload_hash":
                        r.identity.payload_hash,

                    "terminal_state":
                        r.terminal_state,
                }


                if ledger["body"] != expected:

                    raise ValueError(
                        "completion ledger "
                        "binding mismatch"
                    )


            # -------------------------------------------------------------
            # FINALITY CHECKPOINT VALIDATION
            # -------------------------------------------------------------

            if r.finality_checkpoint_written:

                cp = (
                    self
                    .finality_checkpoints
                    .get(dispatch_id)
                )

                if not cp:

                    raise ValueError(
                        "record says checkpoint "
                        "exists but checkpoint "
                        "is missing"
                    )


                if not verify_seal(
                    cp["body"],
                    cp["seal"],
                ):

                    raise ValueError(
                        "finality checkpoint "
                        "seal mismatch"
                    )


                expected_hash = (
                    sha256_text(
                        canonical(
                            cp["body"]
                        )
                    )
                )


                if (
                    cp["checkpoint_hash"]
                    != expected_hash
                ):

                    raise ValueError(
                        "finality checkpoint "
                        "hash mismatch"
                    )


                if (
                    cp["body"][
                        "dispatch_id"
                    ]
                    !=
                    r.identity.dispatch_id
                ):

                    raise ValueError(
                        "checkpoint dispatch "
                        "substitution detected"
                    )


                if (
                    cp["body"][
                        "payload_hash"
                    ]
                    !=
                    r.identity.payload_hash
                ):

                    raise ValueError(
                        "checkpoint payload "
                        "substitution detected"
                    )


                ledger = (
                    self
                    .completion_ledger[
                        dispatch_id
                    ]
                )


                if (
                    cp["body"][
                        "ledger_seal"
                    ]
                    !=
                    ledger["seal"]
                ):

                    raise ValueError(
                        "checkpoint/ledger "
                        "chain broken"
                    )


            # -------------------------------------------------------------
            # JOURNAL INTEGRITY
            # -------------------------------------------------------------

            for entry in self.journal:

                if not verify_seal(
                    entry["body"],
                    entry["seal"],
                ):

                    raise ValueError(
                        "journal integrity failure"
                    )


    # -------------------------------------------------------------------------
    # SNAPSHOT
    # -------------------------------------------------------------------------

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        with STORE_LOCK:

            body = {

                "records": {

                    did: {

                        "identity":
                            asdict(
                                r.identity
                            ),

                        "authorization_consumed":
                            r.authorization_consumed,

                        "synthetic_dispatched":
                            r.synthetic_dispatched,

                        "reconciled":
                            r.reconciled,

                        "terminal_state":
                            r.terminal_state,

                        "completion_ledger_written":
                            r.completion_ledger_written,

                        "finality_checkpoint_written":
                            r.finality_checkpoint_written,

                        "checkpoint_hash":
                            r.checkpoint_hash,

                        "generation":
                            r.generation,
                    }

                    for did, r
                    in sorted(
                        self.records.items()
                    )
                },


                "journal":
                    copy.deepcopy(
                        self.journal
                    ),


                "completion_ledger":
                    copy.deepcopy(
                        self.completion_ledger
                    ),


                "finality_checkpoints":
                    copy.deepcopy(
                        self.finality_checkpoints
                    ),
            }


            return {

                "body":
                    body,

                "seal":
                    seal(body),
            }


    # -------------------------------------------------------------------------
    # RESTORE
    # -------------------------------------------------------------------------

    @classmethod
    def restore(
        cls,
        snapshot: Dict[str, Any],
    ):

        if not verify_seal(
            snapshot["body"],
            snapshot["seal"],
        ):

            raise ValueError(
                "snapshot integrity seal mismatch"
            )


        s = cls()

        body = snapshot["body"]


        s.journal = (
            copy.deepcopy(
                body["journal"]
            )
        )


        s.completion_ledger = (
            copy.deepcopy(
                body[
                    "completion_ledger"
                ]
            )
        )


        s.finality_checkpoints = (
            copy.deepcopy(
                body[
                    "finality_checkpoints"
                ]
            )
        )


        for did, raw in (
            body["records"].items()
        ):

            ident = DispatchIdentity(
                **raw["identity"]
            )


            s.records[did] = (
                RuntimeRecord(

                    identity=
                        ident,

                    authorization_consumed=
                        raw[
                            "authorization_consumed"
                        ],

                    synthetic_dispatched=
                        raw[
                            "synthetic_dispatched"
                        ],

                    reconciled=
                        raw[
                            "reconciled"
                        ],

                    terminal_state=
                        raw[
                            "terminal_state"
                        ],

                    completion_ledger_written=
                        raw[
                            "completion_ledger_written"
                        ],

                    finality_checkpoint_written=
                        raw[
                            "finality_checkpoint_written"
                        ],

                    checkpoint_hash=
                        raw[
                            "checkpoint_hash"
                        ],

                    generation=
                        raw[
                            "generation"
                        ],
                )
            )


            s.validate_record(
                did
            )


        return s


    # -------------------------------------------------------------------------
    # CRASH RECOVERY
    # -------------------------------------------------------------------------

    def recover(
        self,
        dispatch_id: str,
    ):

        with STORE_LOCK:

            self.validate_record(
                dispatch_id
            )


            r = self.records[
                dispatch_id
            ]


            # -------------------------------------------------------------
            # ALREADY FINAL
            # -------------------------------------------------------------

            if r.finality_checkpoint_written:

                return "ALREADY_FINAL"


            # -------------------------------------------------------------
            # LEDGER EXISTS
            # -------------------------------------------------------------

            if r.completion_ledger_written:

                self.write_finality_checkpoint(
                    dispatch_id
                )

                return (
                    "CHECKPOINT_RESTORED"
                )


            # -------------------------------------------------------------
            # RECONCILIATION EXISTS
            # -------------------------------------------------------------

            if r.reconciled:

                self.write_completion_ledger(
                    dispatch_id
                )

                self.write_finality_checkpoint(
                    dispatch_id
                )

                return (
                    "LEDGER_AND_CHECKPOINT_RESTORED"
                )


            # -------------------------------------------------------------
            # DISPATCH EXISTS
            # -------------------------------------------------------------

            if r.synthetic_dispatched:

                self.reconcile(
                    dispatch_id,
                    "COMPLETED",
                )

                self.write_completion_ledger(
                    dispatch_id
                )

                self.write_finality_checkpoint(
                    dispatch_id
                )

                return (
                    "RECONCILIATION_FINALIZED"
                )


            # -------------------------------------------------------------
            # AUTHORIZATION CONSUMED
            # -------------------------------------------------------------

            if r.authorization_consumed:

                self.synthetic_dispatch(
                    dispatch_id
                )

                self.reconcile(
                    dispatch_id,
                    "COMPLETED",
                )

                self.write_completion_ledger(
                    dispatch_id
                )

                self.write_finality_checkpoint(
                    dispatch_id
                )

                return (
                    "DISPATCH_AND_FINALITY_RECOVERED"
                )


            raise ValueError(
                "pre-authorization state "
                "cannot synthesize execution"
            )


# =============================================================================
# IDENTITY GENERATOR
# =============================================================================

def make_identity(
    tag: str,
) -> DispatchIdentity:

    payload = {
        "leverage":
            LEVERAGE,

        "marginMode":
            MARGIN_MODE,

        "symbol":
            SYMBOL,
    }


    payload_hash = (
        sha256_text(
            canonical(payload)
        )
    )


    root = (
        sha256_text(
            f"{UNIT}|"
            f"{tag}|"
            f"{payload_hash}"
        )
    )


    return DispatchIdentity(

        dispatch_id=
            f"dsp-{root[:20]}",

        authorization_id=
            f"auth-{root[20:40]}",

        intent_id=
            f"int-{root[40:56]}",

        request_id=
            f"req-{root[56:64]}",

        symbol=
            SYMBOL,

        payload_hash=
            payload_hash,
    )


# =============================================================================
# CREATE FULLY FINALIZED STORE
# =============================================================================

def finalized_store(
    tag: str = "base",
):

    s = DurableStore()


    ident = make_identity(
        tag
    )


    r = RuntimeRecord(
        identity=ident
    )


    s.create(
        r
    )


    s.consume_authorization(
        ident.dispatch_id
    )


    s.synthetic_dispatch(
        ident.dispatch_id
    )


    s.reconcile(
        ident.dispatch_id
    )


    s.write_completion_ledger(
        ident.dispatch_id
    )


    s.write_finality_checkpoint(
        ident.dispatch_id
    )


    s.validate_record(
        ident.dispatch_id
    )


    return (
        s,
        ident.dispatch_id,
    )


# =============================================================================
# MAIN DIAGNOSTIC
# =============================================================================

def run_diagnostic():

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
        "=" * 92
    )

    print(
        f"{UNIT}: "
        "DURABLE TERMINAL RECONCILIATION "
        "/ FINALITY CHECKPOINT"
    )

    print(
        "=" * 92
    )


    # =========================================================================
    # EXACT PAYLOAD
    # =========================================================================

    banner(
        f"{UNIT} EXACT PAYLOAD"
    )


    payload = {

        "leverage":
            LEVERAGE,

        "marginMode":
            MARGIN_MODE,

        "symbol":
            SYMBOL,
    }


    payload_json = (
        canonical(payload)
    )


    payload_hash = (
        sha256_text(
            payload_json
        )
    )


    print(
        f"Payload = {payload_json}"
    )


    print(
        f"Payload SHA256 = "
        f"{payload_hash}"
    )


    check(
        "Exact Leverage Payload Preserved",

        payload_json
        ==
        '{"leverage":"100","marginMode":"ISOLATED","symbol":"BTCUSDT"}',
    )


    check(
        "Expected Payload SHA256 Preserved",

        payload_hash
        ==
        "64f7f170df9a2966605a82724094ca67cdd46ea5fef06957ba37c91705bcb00e",
    )


    # =========================================================================
    # TEST 1
    # =========================================================================

    banner(
        f"{UNIT} TEST 1: "
        "FINALITY CHECKPOINT CREATION"
    )


    s, did = finalized_store(
        "t1"
    )


    cp = (
        s.finality_checkpoints[
            did
        ]
    )


    check(
        "Completion Ledger Written Before Checkpoint",

        s.records[
            did
        ].completion_ledger_written,
    )


    check(
        "Finality Checkpoint Written",

        s.records[
            did
        ].finality_checkpoint_written,
    )


    check(
        "Finality Checkpoint Hash Present",

        bool(
            cp[
                "checkpoint_hash"
            ]
        ),
    )


    check(
        "Finality Checkpoint Seal Valid",

        verify_seal(
            cp["body"],
            cp["seal"],
        ),
    )


    # =========================================================================
    # TEST 2
    # =========================================================================

    banner(
        f"{UNIT} TEST 2: "
        "COMPLETED FINALITY REPLAY REJECTION"
    )


    before = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    result = s.recover(
        did
    )


    after = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    check(
        "Completed Recovery Returns Already Final",

        result
        ==
        "ALREADY_FINAL",
    )


    check(
        "Completed Finality Produced No Redispatch",

        before == after,
    )


    # =========================================================================
    # TEST 3
    # =========================================================================

    banner(
        f"{UNIT} TEST 3: "
        "CHECKPOINT TAMPER REJECTION"
    )


    tampered = (
        s.snapshot()
    )


    tampered[
        "body"
    ][
        "finality_checkpoints"
    ][
        did
    ][
        "body"
    ][
        "terminal_state"
    ] = "REJECTED"


    tampered[
        "seal"
    ] = seal(
        tampered["body"]
    )


    rejected = False


    try:

        DurableStore.restore(
            tampered
        )

    except ValueError:

        rejected = True


    check(
        "Tampered Finality Checkpoint Rejected",

        rejected,
    )


    # =========================================================================
    # TEST 4
    # =========================================================================

    banner(
        f"{UNIT} TEST 4: "
        "CHECKPOINT HASH TAMPER REJECTION"
    )


    tampered = (
        s.snapshot()
    )


    tampered[
        "body"
    ][
        "finality_checkpoints"
    ][
        did
    ][
        "checkpoint_hash"
    ] = "0" * 64


    tampered[
        "seal"
    ] = seal(
        tampered["body"]
    )


    rejected = False


    try:

        DurableStore.restore(
            tampered
        )

    except ValueError:

        rejected = True


    check(
        "Tampered Finality Hash Rejected",

        rejected,
    )


    # =========================================================================
    # TEST 5
    # =========================================================================

    banner(
        f"{UNIT} TEST 5: "
        "CHECKPOINT / LEDGER "
        "CHAIN-BREAK REJECTION"
    )


    tampered = (
        s.snapshot()
    )


    tampered[
        "body"
    ][
        "finality_checkpoints"
    ][
        did
    ][
        "body"
    ][
        "ledger_seal"
    ] = "f" * 64


    tampered_cp = (
        tampered[
            "body"
        ][
            "finality_checkpoints"
        ][
            did
        ]
    )


    tampered_cp[
        "checkpoint_hash"
    ] = sha256_text(
        canonical(
            tampered_cp["body"]
        )
    )


    tampered_cp[
        "seal"
    ] = seal(
        tampered_cp["body"]
    )


    tampered[
        "seal"
    ] = seal(
        tampered["body"]
    )


    rejected = False


    try:

        DurableStore.restore(
            tampered
        )

    except ValueError:

        rejected = True


    check(
        "Broken Ledger-To-Checkpoint Chain Rejected",

        rejected,
    )


    # =========================================================================
    # TEST 6
    # =========================================================================

    banner(
        f"{UNIT} TEST 6: "
        "CROSS-DISPATCH "
        "CHECKPOINT SUBSTITUTION"
    )


    s2, did2 = (
        finalized_store(
            "t6-other"
        )
    )


    snap = s.snapshot()


    foreign_cp = (
        copy.deepcopy(
            s2.finality_checkpoints[
                did2
            ]
        )
    )


    snap[
        "body"
    ][
        "finality_checkpoints"
    ][
        did
    ] = foreign_cp


    snap[
        "seal"
    ] = seal(
        snap["body"]
    )


    rejected = False


    try:

        DurableStore.restore(
            snap
        )

    except ValueError:

        rejected = True


    check(
        "Cross-Dispatch Finality Substitution Rejected",

        rejected,
    )


    # =========================================================================
    # TEST 7
    # =========================================================================

    banner(
        f"{UNIT} TEST 7: "
        "POST-RECONCILIATION "
        "CRASH RECOVERY"
    )


    rstore = DurableStore()


    rid = make_identity(
        "t7"
    )


    rstore.create(
        RuntimeRecord(
            identity=rid
        )
    )


    rstore.consume_authorization(
        rid.dispatch_id
    )


    rstore.synthetic_dispatch(
        rid.dispatch_id
    )


    rstore.reconcile(
        rid.dispatch_id
    )


    snap = (
        rstore.snapshot()
    )


    restored = (
        DurableStore.restore(
            snap
        )
    )


    before = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    result = (
        restored.recover(
            rid.dispatch_id
        )
    )


    after = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    check(
        "Post-Reconciliation Recovery Rebuilt Ledger And Checkpoint",

        result
        ==
        "LEDGER_AND_CHECKPOINT_RESTORED",
    )


    check(
        "Post-Reconciliation Recovery Produced No Redispatch",

        before == after,
    )


    check(
        "Recovered Finality Checkpoint Present",

        restored.records[
            rid.dispatch_id
        ].finality_checkpoint_written,
    )


    # =========================================================================
    # TEST 8
    # =========================================================================

    banner(
        f"{UNIT} TEST 8: "
        "POST-LEDGER CRASH RECOVERY"
    )


    lstore = DurableStore()


    lid = make_identity(
        "t8"
    )


    lstore.create(
        RuntimeRecord(
            identity=lid
        )
    )


    lstore.consume_authorization(
        lid.dispatch_id
    )


    lstore.synthetic_dispatch(
        lid.dispatch_id
    )


    lstore.reconcile(
        lid.dispatch_id
    )


    lstore.write_completion_ledger(
        lid.dispatch_id
    )


    restored = (
        DurableStore.restore(
            lstore.snapshot()
        )
    )


    before = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    result = (
        restored.recover(
            lid.dispatch_id
        )
    )


    after = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    check(
        "Post-Ledger Recovery Restored Checkpoint",

        result
        ==
        "CHECKPOINT_RESTORED",
    )


    check(
        "Post-Ledger Recovery Produced No Redispatch",

        before == after,
    )


    # =========================================================================
    # TEST 9
    # =========================================================================

    banner(
        f"{UNIT} TEST 9: "
        "POST-DISPATCH "
        "CRASH FINALIZATION"
    )


    dstore = DurableStore()


    xid = make_identity(
        "t9"
    )


    dstore.create(
        RuntimeRecord(
            identity=xid
        )
    )


    dstore.consume_authorization(
        xid.dispatch_id
    )


    dstore.synthetic_dispatch(
        xid.dispatch_id
    )


    restored = (
        DurableStore.restore(
            dstore.snapshot()
        )
    )


    before = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    result = (
        restored.recover(
            xid.dispatch_id
        )
    )


    after = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    check(
        "Post-Dispatch Recovery Finalized Reconciliation",

        result
        ==
        "RECONCILIATION_FINALIZED",
    )


    check(
        "Post-Dispatch Recovery Produced No Second Dispatch",

        before == after,
    )


    # =========================================================================
    # TEST 10
    # =========================================================================

    banner(
        f"{UNIT} TEST 10: "
        "POST-AUTHORIZATION CRASH "
        "SINGLE SYNTHETIC DISPATCH"
    )


    astore = DurableStore()


    aid = make_identity(
        "t10"
    )


    astore.create(
        RuntimeRecord(
            identity=aid
        )
    )


    astore.consume_authorization(
        aid.dispatch_id
    )


    restored = (
        DurableStore.restore(
            astore.snapshot()
        )
    )


    before = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    result = (
        restored.recover(
            aid.dispatch_id
        )
    )


    after = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    check(
        "Post-Authorization Recovery Completed",

        result
        ==
        "DISPATCH_AND_FINALITY_RECOVERED",
    )


    check(
        "Post-Authorization Recovery Produced Exactly One Dispatch",

        after - before == 1,
    )


    again_before = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    again = restored.recover(
        aid.dispatch_id
    )


    again_after = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    check(
        "Repeated Recovery Is Already Final",

        again
        ==
        "ALREADY_FINAL",
    )


    check(
        "Repeated Recovery Produced No Second Dispatch",

        again_before
        ==
        again_after,
    )


    # =========================================================================
    # TEST 11
    # =========================================================================

    banner(
        f"{UNIT} TEST 11: "
        "TERMINAL STATE IMMUTABILITY"
    )


    tstore, tid = (
        finalized_store(
            "t11"
        )
    )


    rejected = False


    try:

        tstore.reconcile(
            tid,
            "REJECTED",
        )

    except ValueError:

        rejected = True


    check(
        "Terminal State Mutation Rejected",

        rejected,
    )


    check(
        "Original Terminal State Preserved",

        tstore.records[
            tid
        ].terminal_state
        ==
        "COMPLETED",
    )


    # =========================================================================
    # TEST 12
    # =========================================================================

    banner(
        f"{UNIT} TEST 12: "
        "CONCURRENT FINALITY RECOVERY "
        "SINGLE-WINNER"
    )


    cstore = DurableStore()


    cid = make_identity(
        "t12"
    )


    cstore.create(
        RuntimeRecord(
            identity=cid
        )
    )


    cstore.consume_authorization(
        cid.dispatch_id
    )


    snapshot = (
        cstore.snapshot()
    )


    restored = (
        DurableStore.restore(
            snapshot
        )
    )


    start_dispatches = (
        AUDIT[
            "synthetic_dispatches"
        ]
    )


    results = []

    errors = []


    def worker():

        try:

            results.append(
                restored.recover(
                    cid.dispatch_id
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


    for t in threads:

        t.start()


    for t in threads:

        t.join()


    dispatch_delta = (

        AUDIT[
            "synthetic_dispatches"
        ]

        -

        start_dispatches
    )


    check(
        "Concurrent Recovery Produced Exactly One Synthetic Dispatch",

        dispatch_delta == 1,
    )


    check(
        "Concurrent Recovery Final State Is Final",

        restored.records[
            cid.dispatch_id
        ].finality_checkpoint_written,
    )


    check(
        "Concurrent Recovery Preserved Consumed Authorization",

        restored.records[
            cid.dispatch_id
        ].authorization_consumed,
    )


    check(
        "Concurrent Recovery Produced No Structural Errors",

        len(errors) == 0,
    )


    # =========================================================================
    # TEST 13
    # =========================================================================

    banner(
        f"{UNIT} TEST 13: "
        "IMPOSSIBLE FINALITY STATE REJECTION"
    )


    istore, iid = (
        finalized_store(
            "t13"
        )
    )


    bad = (
        istore.snapshot()
    )


    bad[
        "body"
    ][
        "records"
    ][
        iid
    ][
        "completion_ledger_written"
    ] = False


    bad[
        "body"
    ][
        "records"
    ][
        iid
    ][
        "finality_checkpoint_written"
    ] = True


    bad[
        "seal"
    ] = seal(
        bad["body"]
    )


    rejected = False


    try:

        DurableStore.restore(
            bad
        )

    except ValueError as exc:

        local_block(
            str(exc)
        )

        rejected = True


    check(
        "Checkpoint-Without-Ledger State Rejected",

        rejected,
    )


    # =========================================================================
    # TEST 14
    # =========================================================================

    banner(
        f"{UNIT} TEST 14: "
        "JOURNAL INTEGRITY"
    )


    jstore, jid = (
        finalized_store(
            "t14"
        )
    )


    jsnap = (
        jstore.snapshot()
    )


    jsnap[
        "body"
    ][
        "journal"
    ][
        0
    ][
        "body"
    ][
        "event"
    ] = "FORGED_EVENT"


    jsnap[
        "seal"
    ] = seal(
        jsnap["body"]
    )


    rejected = False


    try:

        DurableStore.restore(
            jsnap
        )

    except ValueError:

        rejected = True


    check(
        "Journal Entry Tampering Rejected",

        rejected,
    )


    # =========================================================================
    # TEST 15
    # =========================================================================

    banner(
        f"{UNIT} TEST 15: "
        "FINAL NETWORK WRITE FIREBREAK"
    )


    post_blocked = False

    write_blocked = False

    leverage_blocked = False


    try:

        forbidden_post(
            LEVERAGE_ENDPOINT,
            payload,
        )

    except PermissionError:

        post_blocked = True


    try:

        forbidden_write(
            "PUT",
            "/forbidden",
        )

    except PermissionError:

        write_blocked = True


    try:

        forbidden_leverage_transport(
            payload
        )

    except PermissionError:

        leverage_blocked = True


    check(
        "Real POST Rejected Locally",

        post_blocked,
    )


    check(
        "Generic Network Write Rejected Locally",

        write_blocked,
    )


    check(
        "Leverage Mutation Transport Rejected Locally",

        leverage_blocked,
    )


    check(
        "Network POST Count Is Zero",

        AUDIT[
            "network_posts"
        ] == 0,
    )


    check(
        "Network Write Count Is Zero",

        AUDIT[
            "network_writes"
        ] == 0,
    )


    check(
        "Leverage Transmission Count Is Zero",

        AUDIT[
            "leverage_transmissions"
        ] == 0,
    )


    # =========================================================================
    # TEST 16
    # =========================================================================

    banner(
        f"{UNIT} TEST 16: "
        "EXACT ENDPOINT / PAYLOAD IMMUTABILITY"
    )


    check(
        "Exact Leverage Payload Preserved",

        canonical(payload)
        ==
        '{"leverage":"100","marginMode":"ISOLATED","symbol":"BTCUSDT"}',
    )


    check(
        "Canonical Payload Serialization Preserved",

        sha256_text(
            canonical(payload)
        )
        ==
        "64f7f170df9a2966605a82724094ca67cdd46ea5fef06957ba37c91705bcb00e",
    )


    check(
        "Transport Method Exactly POST",

        METHOD
        ==
        "POST",
    )


    check(
        "Transport Path Exactly Leverage Endpoint",

        LEVERAGE_ENDPOINT
        ==
        "/capi/v3/account/setLeverage",
    )


    # =========================================================================
    # WRITE LOCK AUDIT
    # =========================================================================

    banner(
        f"{UNIT} WRITE-LOCK AUDIT"
    )


    print(
        f"  Network POSTs = "
        f"{AUDIT['network_posts']}"
    )


    print(
        f"  Network writes = "
        f"{AUDIT['network_writes']}"
    )


    print(
        f"  Leverage transmissions = "
        f"{AUDIT['leverage_transmissions']}"
    )


    check(
        "Network POST Count Is Zero",

        AUDIT[
            "network_posts"
        ] == 0,
    )


    check(
        "Network Write Count Is Zero",

        AUDIT[
            "network_writes"
        ] == 0,
    )


    check(
        "Leverage Transmission Count Is Zero",

        AUDIT[
            "leverage_transmissions"
        ] == 0,
    )


    # =========================================================================
    # FINAL EXECUTION READINESS ASSESSMENT
    # =========================================================================

    banner(
        f"{UNIT} EXECUTION-READINESS ASSESSMENT"
    )


    print(
        "  Structural Safety Failures = 0"
    )


    print(
        "  Readiness Blockers = 0"
    )


    print(
        "  Finality Checkpoint Integrity = "
        "✅ VERIFIED"
    )


    print(
        "  Ledger-To-Checkpoint Binding = "
        "✅ VERIFIED"
    )


    print(
        "  Terminal State Immutability = "
        "✅ VERIFIED"
    )


    print(
        "  Post-Authorization Recovery = "
        "✅ VERIFIED"
    )


    print(
        "  Post-Dispatch Recovery = "
        "✅ VERIFIED"
    )


    print(
        "  Post-Reconciliation Recovery = "
        "✅ VERIFIED"
    )


    print(
        "  Post-Ledger Recovery = "
        "✅ VERIFIED"
    )


    print(
        "  Concurrent Recovery Single Dispatch = "
        "✅ VERIFIED"
    )


    print(
        "  Cross-Dispatch Substitution Rejection = "
        "✅ VERIFIED"
    )


    print(
        "  Journal Integrity = "
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


    # =========================================================================
    # FINAL RESULT
    # =========================================================================

    print()


    print(
        f"✅ {UNIT} DIAGNOSTIC PASSED"
    )


    print(
        "✅ DURABLE TERMINAL "
        "RECONCILIATION VERIFIED"
    )


    print(
        "✅ FINALITY CHECKPOINT "
        "INTEGRITY VERIFIED"
    )


    print(
        "✅ LEDGER-TO-CHECKPOINT "
        "CHAIN VERIFIED"
    )


    print(
        "✅ TERMINAL STATE "
        "IMMUTABILITY VERIFIED"
    )


    print(
        "✅ CRASH-WINDOW FINALITY "
        "RECOVERY VERIFIED"
    )


    print(
        "✅ CONCURRENT RECOVERY PRODUCES "
        "SINGLE SYNTHETIC DISPATCH"
    )


    print(
        "✅ CROSS-DISPATCH FINALITY "
        "SUBSTITUTION REJECTED"
    )


    print(
        "✅ JOURNAL TAMPERING REJECTED"
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
        "🛡 NO NETWORK WRITE "
        "WAS TRANSMITTED"
    )


    print(
        "=" * 92
    )


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        body = json.dumps(
            {
                "status":
                    "ok",

                "unit":
                    UNIT,

                "network_writes_enabled":
                    NETWORK_WRITES_ENABLED,

                "leverage_mutation_transport_enabled":
                    LEVERAGE_MUTATION_TRANSPORT_ENABLED,
            }
        ).encode()


        self.send_response(
            200
        )


        self.send_header(
            "Content-Type",
            "application/json",
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


# =============================================================================
# START HEALTH SERVER
# =============================================================================

def start_health_server():

    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )


    server = HTTPServer(
        (
            "0.0.0.0",
            port,
        ),
        HealthHandler,
    )


    thread = threading.Thread(
        target=
            server.serve_forever,

        daemon=True,
    )


    thread.start()


    print(
        f"{UNIT}: "
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {port}"
    )


# =============================================================================
# PERSISTENT HEARTBEAT
# =============================================================================

def heartbeat_forever():

    n = 1


    print(
        f"{UNIT}: "
        "PERSISTENT RUNTIME ACTIVE"
    )


    print(
        f"{UNIT}: "
        "FINALITY CHECKPOINT LOCK ACTIVE"
    )


    print(
        f"{UNIT}: "
        "COMPLETION LEDGER CHAIN LOCK ACTIVE"
    )


    print(
        f"{UNIT}: "
        "TERMINAL STATE IMMUTABILITY "
        "LOCK ACTIVE"
    )


    print(
        f"{UNIT}: "
        "RESTART IDEMPOTENCY LOCK ACTIVE"
    )


    print(
        f"{UNIT}: "
        "SYNTHETIC TRANSPORT "
        "INTERCEPTOR ACTIVE"
    )


    print(
        f"{UNIT}: "
        "NETWORK WRITE TRANSPORT LOCKED"
    )


    print(
        f"{UNIT}: "
        "LEVERAGE MUTATION "
        "TRANSPORT LOCKED"
    )


    while True:

        print(
            f"{UNIT}: "
            f"HEARTBEAT {n} "
            "✅ ACTIVE",
            flush=True,
        )


        n += 1


        time.sleep(
            15
        )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    print(
        f"{UNIT}: RUNTIME STARTING"
    )


    start_health_server()


    run_diagnostic()


    heartbeat_forever()
