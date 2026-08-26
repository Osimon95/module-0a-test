# ============================================================================
# R28 UNIT N.40
# CROSS-GENERATION COMPACTION CRASH RECOVERY + TERMINAL CLOSURE
#
# COMPLETE COPY/PASTE VERSION
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.40 INCREMENT OVER N.39:
#   - CRASH AFTER COMPACTION BEGIN
#   - CRASH AFTER CHECKPOINT CREATION
#   - CRASH AFTER MANIFEST PUBLICATION
#   - RESTART RECONCILIATION OF INCOMPLETE COMPACTION
#   - GENERATION ADVANCE FENCING DURING COMPACTION
#   - CRASH IMMEDIATELY AFTER GENERATION ADVANCE
#   - CROSS-GENERATION FINALIZED-FENCE PRESERVATION
#   - HISTORICAL CHECKPOINT / MANIFEST VERIFICATION
#   - STALE CROSS-GENERATION AUTHORITY REJECTION
#   - WAL / CHECKPOINT / MANIFEST TAMPER REJECTION
#   - MULTI-RESTART TERMINAL VALIDATION
#
# CLOSURE RULE:
#   IF THIS UNIT PASSES CLEANLY, R28 HARDENING IS COMPLETE.
#   DO NOT AUTOMATICALLY CREATE N.41.
# ============================================================================

import copy
import hashlib
import json
import os
import tempfile
import threading
import time

from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# ============================================================================
# SECTION 1
# UNIT IDENTITY + SAFETY POLICY
# ============================================================================

UNIT = "R28 UNIT N.40"

PORT = int(
    os.environ.get(
        "PORT",
        "10000",
    )
)

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

TRANSPORT_METHOD = "POST"

TRANSPORT_PATH = "/capi/v2/account/leverage"

TRANSPORT_PAYLOAD = {
    "symbol": "BTCUSDT",
    "marginMode": "ISOLATED",
    "leverage": "100",
}

SEP = "-" * 92


# ============================================================================
# SECTION 2
# GENERIC HELPERS
# ============================================================================

def canonical(
    obj: Any,
) -> str:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(
    text: str,
) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def seal_dict(
    d: Dict[str, Any],
    exclude: str = "seal",
) -> str:
    body = {
        k: v
        for k, v in d.items()
        if k != exclude
    }

    return sha256_text(
        canonical(body)
    )


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(message)


def banner(
    text: str,
) -> None:
    print(
        SEP,
        flush=True,
    )

    print(
        text,
        flush=True,
    )

    print(
        SEP,
        flush=True,
    )


PASS_ASSERTIONS = 0


def passed(
    label: str,
) -> None:
    global PASS_ASSERTIONS

    PASS_ASSERTIONS += 1

    print(
        f"{label:<84} ✅ PASS",
        flush=True,
    )


def expect_block(
    label: str,
    needle: str,
    fn,
) -> None:
    try:
        fn()

    except Exception as exc:
        print(
            f"{UNIT} LOCAL BLOCK:",
            flush=True,
        )

        print(
            f"  {exc}",
            flush=True,
        )

        require(
            needle in str(exc),
            f"unexpected rejection reason: {exc}",
        )

        passed(label)

        return

    raise AssertionError(
        f"{label}: expected rejection"
    )


# ============================================================================
# SECTION 3
# WAL RECORD
# ============================================================================

@dataclass
class WalRecord:
    seq: int

    kind: str

    payload: Dict[str, Any]

    prev_hash: str

    record_hash: str = ""

    def finalize(
        self,
    ) -> None:
        material = {
            "seq": self.seq,
            "kind": self.kind,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
        }

        self.record_hash = sha256_text(
            canonical(material)
        )


# ============================================================================
# SECTION 4
# CHECKPOINT MODEL
# ============================================================================

@dataclass
class Checkpoint:
    checkpoint_id: str

    sequence: int

    generation: int

    lineage: str

    recovery_epoch: int

    parent_checkpoint_id: Optional[str]

    parent_checkpoint_hash: Optional[str]

    wal_final_hash: str

    finalized_promotions: List[str]

    finalized_receipts: List[str]

    seal: str = ""

    def reseal(
        self,
    ) -> None:
        self.seal = seal_dict(
            asdict(self)
        )


# ============================================================================
# SECTION 5
# MANIFEST MODEL
# ============================================================================

@dataclass
class Manifest:
    active_checkpoint_id: str

    active_checkpoint_hash: str

    active_sequence: int

    generation: int

    lineage: str

    recovery_epoch: int

    seal: str = ""

    def reseal(
        self,
    ) -> None:
        self.seal = seal_dict(
            asdict(self)
        )


# ============================================================================
# SECTION 6
# DURABLE STATE MODEL
# ============================================================================

@dataclass
class DurableState:
    generation: int = 1

    lineage: str = "lineage-1"

    recovery_epoch: int = 1

    wal_seq: int = 0

    wal_final_hash: str = "GENESIS"

    finalized_promotions: Set[str] = field(
        default_factory=set
    )

    finalized_receipts: Set[str] = field(
        default_factory=set
    )

    active_checkpoint_id: Optional[str] = None

    active_checkpoint_hash: Optional[str] = None

    active_checkpoint_sequence: int = 0

    compaction_in_progress: bool = False

    pending_checkpoint_id: Optional[str] = None

    pending_manifest_id: Optional[str] = None

    pending_generation_advance: bool = False

    synthetic_dispatch_count: int = 0


# ============================================================================
# SECTION 7
# SYNTHETIC TRANSPORT
# ============================================================================

class SyntheticTransport:

    def __init__(
        self,
    ) -> None:
        self.dispatches: List[
            Dict[str, Any]
        ] = []

    def post(
        self,
        path: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        require(
            SYNTHETIC_TRANSPORT_ONLY,
            "synthetic transport disabled",
        )

        require(
            not REAL_POST_ENABLED,
            "real POST unexpectedly enabled",
        )

        require(
            not DEMO_POST_ENABLED,
            "demo POST unexpectedly enabled",
        )

        require(
            not NETWORK_WRITES_ENABLED,
            "network writes unexpectedly enabled",
        )

        require(
            path == TRANSPORT_PATH,
            "transport path mismatch",
        )

        require(
            payload == TRANSPORT_PAYLOAD,
            "transport payload mismatch",
        )

        receipt = {
            "synthetic": True,
            "transmitted": False,
            "method": TRANSPORT_METHOD,
            "path": path,
            "payload_hash": sha256_text(
                canonical(payload)
            ),
            "receipt_id": (
                f"receipt-"
                f"{len(self.dispatches) + 1}"
            ),
        }

        self.dispatches.append(
            copy.deepcopy(receipt)
        )

        return receipt


# ============================================================================
# SECTION 8
# DURABLE ENGINE
# ============================================================================

class Engine:

    def __init__(
        self,
        root: Path,
    ) -> None:

        self.root = root

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.state = DurableState()

        self.wal: List[
            WalRecord
        ] = []

        self.checkpoints: Dict[
            str,
            Checkpoint,
        ] = {}

        self.manifests: Dict[
            str,
            Manifest,
        ] = {}

        self.transport = SyntheticTransport()


    # ========================================================================
    # DURABLE FILE PATHS
    # ========================================================================

    @property
    def state_path(
        self,
    ) -> Path:
        return (
            self.root
            / "state.json"
        )


    @property
    def wal_path(
        self,
    ) -> Path:
        return (
            self.root
            / "wal.json"
        )


    @property
    def checkpoint_path(
        self,
    ) -> Path:
        return (
            self.root
            / "checkpoints.json"
        )


    @property
    def manifest_path(
        self,
    ) -> Path:
        return (
            self.root
            / "manifests.json"
        )


    # ========================================================================
    # STATE SERIALIZATION
    # ========================================================================

    def _state_dict(
        self,
    ) -> Dict[str, Any]:

        d = asdict(
            self.state
        )

        d[
            "finalized_promotions"
        ] = sorted(
            self.state.finalized_promotions
        )

        d[
            "finalized_receipts"
        ] = sorted(
            self.state.finalized_receipts
        )

        return d


    # ========================================================================
    # DURABLE PERSISTENCE
    # ========================================================================

    def persist(
        self,
    ) -> None:

        self.state_path.write_text(
            canonical(
                self._state_dict()
            ),
            encoding="utf-8",
        )

        self.wal_path.write_text(
            canonical(
                [
                    asdict(x)
                    for x in self.wal
                ]
            ),
            encoding="utf-8",
        )

        self.checkpoint_path.write_text(
            canonical(
                {
                    k: asdict(v)
                    for k, v
                    in self.checkpoints.items()
                }
            ),
            encoding="utf-8",
        )

        self.manifest_path.write_text(
            canonical(
                {
                    k: asdict(v)
                    for k, v
                    in self.manifests.items()
                }
            ),
            encoding="utf-8",
        )


    # ========================================================================
    # DURABLE RESTORE
    # ========================================================================

    @classmethod
    def restore(
        cls,
        root: Path,
    ) -> "Engine":

        e = cls(root)

        sd = json.loads(
            e.state_path.read_text(
                encoding="utf-8"
            )
        )

        sd[
            "finalized_promotions"
        ] = set(
            sd[
                "finalized_promotions"
            ]
        )

        sd[
            "finalized_receipts"
        ] = set(
            sd[
                "finalized_receipts"
            ]
        )

        e.state = DurableState(
            **sd
        )

        raw_wal = json.loads(
            e.wal_path.read_text(
                encoding="utf-8"
            )
        )

        e.wal = [
            WalRecord(**x)
            for x
            in raw_wal
        ]

        raw_cp = json.loads(
            e.checkpoint_path.read_text(
                encoding="utf-8"
            )
        )

        e.checkpoints = {
            k: Checkpoint(**v)
            for k, v
            in raw_cp.items()
        }

        raw_m = json.loads(
            e.manifest_path.read_text(
                encoding="utf-8"
            )
        )

        e.manifests = {
            k: Manifest(**v)
            for k, v
            in raw_m.items()
        }

        return e


    # ========================================================================
    # WAL APPEND
    # ========================================================================

    def append_wal(
        self,
        kind: str,
        payload: Dict[str, Any],
    ) -> WalRecord:

        self.state.wal_seq += 1

        rec = WalRecord(
            seq=self.state.wal_seq,
            kind=kind,
            payload=copy.deepcopy(
                payload
            ),
            prev_hash=(
                self.state.wal_final_hash
            ),
        )

        rec.finalize()

        self.wal.append(
            rec
        )

        self.state.wal_final_hash = (
            rec.record_hash
        )

        self.persist()

        return rec


    # ========================================================================
    # WAL VALIDATION
    # ========================================================================

    def validate_wal(
        self,
    ) -> None:

        prev = "GENESIS"

        expected_seq = 1

        for rec in self.wal:

            require(
                rec.seq
                == expected_seq,
                "WAL sequence mismatch",
            )

            require(
                rec.prev_hash
                == prev,
                "WAL previous hash mismatch",
            )

            expected = WalRecord(
                rec.seq,
                rec.kind,
                rec.payload,
                rec.prev_hash,
            )

            expected.finalize()

            require(
                rec.record_hash
                == expected.record_hash,
                "WAL record hash mismatch",
            )

            prev = (
                rec.record_hash
            )

            expected_seq += 1

        require(
            self.state.wal_seq
            == len(self.wal),
            "WAL length mismatch",
        )

        require(
            self.state.wal_final_hash
            == prev,
            "WAL final hash mismatch",
        )


    # ========================================================================
    # SYNTHETIC PROMOTION FINALIZATION
    # ========================================================================

    def finalize_promotion(
        self,
        promotion_id: str,
    ) -> str:

        require(
            promotion_id
            not in
            self.state.finalized_promotions,
            "promotion already finalized",
        )

        self.append_wal(
            "PROMOTION_FINALIZED",
            {
                "promotion_id":
                    promotion_id,

                "generation":
                    self.state.generation,

                "lineage":
                    self.state.lineage,

                "recovery_epoch":
                    self.state.recovery_epoch,
            },
        )

        receipt = (
            self.transport.post(
                TRANSPORT_PATH,
                TRANSPORT_PAYLOAD,
            )
        )

        self.state.synthetic_dispatch_count += 1

        self.state.finalized_promotions.add(
            promotion_id
        )

        self.state.finalized_receipts.add(
            receipt["receipt_id"]
        )

        self.append_wal(
            "RECEIPT_FINALIZED",
            {
                "promotion_id":
                    promotion_id,

                "receipt_id":
                    receipt["receipt_id"],

                "generation":
                    self.state.generation,
            },
        )

        self.persist()

        return receipt[
            "receipt_id"
        ]


    # ========================================================================
    # BEGIN COMPACTION
    # ========================================================================

    def begin_compaction(
        self,
    ) -> str:

        require(
            not self.state.compaction_in_progress,
            "compaction already active",
        )

        self.state.compaction_in_progress = True

        cp_id = (
            f"cp-"
            f"{self.state.generation}-"
            f"{self.state.wal_seq}"
        )

        self.state.pending_checkpoint_id = (
            cp_id
        )

        self.append_wal(
            "COMPACTION_BEGIN",
            {
                "checkpoint_id":
                    cp_id
            },
        )

        self.persist()

        return cp_id


    # ========================================================================
    # CHECKPOINT CONSTRUCTION
    # ========================================================================

    def build_checkpoint(
        self,
        cp_id: str,
    ) -> Checkpoint:

        require(
            self.state.compaction_in_progress,
            "compaction not active",
        )

        require(
            cp_id
            ==
            self.state.pending_checkpoint_id,
            "pending checkpoint mismatch",
        )

        parent_id = (
            self.state.active_checkpoint_id
        )

        parent_hash = (
            self.state.active_checkpoint_hash
        )

        cp = Checkpoint(
            checkpoint_id=cp_id,

            sequence=(
                self.state.wal_seq
            ),

            generation=(
                self.state.generation
            ),

            lineage=(
                self.state.lineage
            ),

            recovery_epoch=(
                self.state.recovery_epoch
            ),

            parent_checkpoint_id=(
                parent_id
            ),

            parent_checkpoint_hash=(
                parent_hash
            ),

            wal_final_hash=(
                self.state.wal_final_hash
            ),

            finalized_promotions=sorted(
                self.state.finalized_promotions
            ),

            finalized_receipts=sorted(
                self.state.finalized_receipts
            ),
        )

        cp.reseal()

        self.checkpoints[
            cp_id
        ] = cp

        self.persist()

        return cp


    # ========================================================================
    # CHECKPOINT VALIDATION
    # ========================================================================

    def validate_checkpoint(
        self,
        cp: Checkpoint,
        allow_historical: bool = False,
    ) -> None:

        require(
            cp.seal
            ==
            seal_dict(
                asdict(cp)
            ),
            "checkpoint integrity seal mismatch",
        )

        if not allow_historical:

            require(
                cp.generation
                ==
                self.state.generation,
                "checkpoint generation mismatch",
            )

            require(
                cp.lineage
                ==
                self.state.lineage,
                "checkpoint lineage mismatch",
            )

            require(
                cp.recovery_epoch
                ==
                self.state.recovery_epoch,
                "checkpoint recovery epoch mismatch",
            )

        if cp.parent_checkpoint_id:

            require(
                cp.parent_checkpoint_id
                in self.checkpoints,
                "checkpoint parent missing",
            )

            parent = self.checkpoints[
                cp.parent_checkpoint_id
            ]

            require(
                cp.parent_checkpoint_hash
                ==
                parent.seal,
                "checkpoint parent hash mismatch",
            )


    # ========================================================================
    # MANIFEST PUBLICATION
    # ========================================================================

    def publish_manifest(
        self,
        cp: Checkpoint,
    ) -> Manifest:

        self.validate_checkpoint(
            cp
        )

        m = Manifest(
            active_checkpoint_id=(
                cp.checkpoint_id
            ),

            active_checkpoint_hash=(
                cp.seal
            ),

            active_sequence=(
                cp.sequence
            ),

            generation=(
                cp.generation
            ),

            lineage=(
                cp.lineage
            ),

            recovery_epoch=(
                cp.recovery_epoch
            ),
        )

        m.reseal()

        mid = (
            f"manifest-"
            f"{cp.checkpoint_id}"
        )

        self.manifests[
            mid
        ] = m

        self.state.pending_manifest_id = (
            mid
        )

        self.persist()

        return m


    # ========================================================================
    # MANIFEST VALIDATION
    # ========================================================================

    def validate_manifest(
        self,
        m: Manifest,
        allow_historical: bool = False,
    ) -> None:

        require(
            m.seal
            ==
            seal_dict(
                asdict(m)
            ),
            "manifest integrity seal mismatch",
        )

        require(
            m.active_checkpoint_id
            in self.checkpoints,
            "manifest checkpoint missing",
        )

        cp = self.checkpoints[
            m.active_checkpoint_id
        ]

        require(
            m.active_checkpoint_hash
            ==
            cp.seal,
            "manifest checkpoint hash mismatch",
        )

        require(
            m.active_sequence
            ==
            cp.sequence,
            "manifest checkpoint sequence mismatch",
        )

        if not allow_historical:

            require(
                m.generation
                ==
                self.state.generation,
                "manifest generation mismatch",
            )

            require(
                m.lineage
                ==
                self.state.lineage,
                "manifest lineage mismatch",
            )

            require(
                m.recovery_epoch
                ==
                self.state.recovery_epoch,
                "manifest recovery epoch mismatch",
            )


    # ========================================================================
    # COMPACTION FINALIZATION
    # ========================================================================

    def finalize_compaction(
        self,
        m: Manifest,
    ) -> None:

        require(
            self.state.compaction_in_progress,
            "compaction not active",
        )

        self.validate_manifest(
            m
        )

        self.state.active_checkpoint_id = (
            m.active_checkpoint_id
        )

        self.state.active_checkpoint_hash = (
            m.active_checkpoint_hash
        )

        self.state.active_checkpoint_sequence = (
            m.active_sequence
        )

        self.state.compaction_in_progress = False

        self.state.pending_checkpoint_id = None

        self.state.pending_manifest_id = None

        self.append_wal(
            "COMPACTION_FINALIZED",
            {
                "checkpoint_id":
                    m.active_checkpoint_id
            },
        )

        self.persist()


    # ========================================================================
    # STANDARD COMPACTION
    # ========================================================================

    def compact(
        self,
    ) -> Checkpoint:

        cp_id = (
            self.begin_compaction()
        )

        cp = (
            self.build_checkpoint(
                cp_id
            )
        )

        m = (
            self.publish_manifest(
                cp
            )
        )

        self.finalize_compaction(
            m
        )

        return cp


    # ========================================================================
    # INCOMPLETE COMPACTION RECOVERY
    # ========================================================================

    def recover_incomplete_compaction(
        self,
    ) -> None:

        if not self.state.compaction_in_progress:
            return

        cp_id = (
            self.state.pending_checkpoint_id
        )

        require(
            cp_id is not None,
            "pending checkpoint missing",
        )

        cp = self.checkpoints.get(
            cp_id
        )

        if cp is None:

            cp = (
                self.build_checkpoint(
                    cp_id
                )
            )

        else:

            self.validate_checkpoint(
                cp
            )

        m = None

        if self.state.pending_manifest_id:

            m = self.manifests.get(
                self.state.pending_manifest_id
            )

            require(
                m is not None,
                "pending manifest missing",
            )

            self.validate_manifest(
                m
            )

        if m is None:

            m = (
                self.publish_manifest(
                    cp
                )
            )

        self.finalize_compaction(
            m
        )


    # ========================================================================
    # GENERATION ADVANCE
    # ========================================================================

    def advance_generation(
        self,
    ) -> None:

        require(
            not self.state.compaction_in_progress,
            "cannot advance generation during compaction",
        )

        old_generation = (
            self.state.generation
        )

        old_lineage = (
            self.state.lineage
        )

        old_epoch = (
            self.state.recovery_epoch
        )

        self.state.generation += 1

        self.state.recovery_epoch += 1

        self.state.lineage = sha256_text(
            (
                f"{old_lineage}|"
                f"{old_generation}|"
                f"{self.state.generation}|"
                f"{self.state.recovery_epoch}"
            )
        )[:24]

        self.append_wal(
            "GENERATION_ADVANCE",
            {
                "from_generation":
                    old_generation,

                "to_generation":
                    self.state.generation,

                "from_recovery_epoch":
                    old_epoch,

                "to_recovery_epoch":
                    self.state.recovery_epoch,

                "new_lineage":
                    self.state.lineage,
            },
        )

        self.persist()


    # ========================================================================
    # COMPLETE DURABLE STATE VALIDATION
    # ========================================================================

    def validate_complete_state(
        self,
    ) -> None:

        self.validate_wal()

        require(
            self.state.active_checkpoint_id
            in self.checkpoints,
            "active checkpoint missing",
        )

        cp = self.checkpoints[
            self.state.active_checkpoint_id
        ]

        require(
            cp.seal
            ==
            self.state.active_checkpoint_hash,
            "active checkpoint hash mismatch",
        )

        require(
            self.state.active_checkpoint_sequence
            <=
            self.state.wal_seq,
            "active checkpoint sequence rollback",
        )

        require(
            self.state.finalized_promotions.issuperset(
                cp.finalized_promotions
            ),
            "promotion fence loss",
        )

        require(
            self.state.finalized_receipts.issuperset(
                cp.finalized_receipts
            ),
            "receipt fence loss",
        )

        for c in self.checkpoints.values():

            self.validate_checkpoint(
                c,
                allow_historical=True,
            )

        for m in self.manifests.values():

            self.validate_manifest(
                m,
                allow_historical=True,
            )


# ============================================================================
# SECTION 9
# N.39-STYLE BASELINE CONSTRUCTION
# ============================================================================

def make_baseline(
    root: Path,
) -> Engine:

    e = Engine(
        root
    )

    e.persist()

    e.finalize_promotion(
        "promotion-1"
    )

    e.compact()

    e.finalize_promotion(
        "promotion-2"
    )

    e.compact()

    e.finalize_promotion(
        "promotion-3"
    )

    e.compact()

    e.advance_generation()

    e.finalize_promotion(
        "promotion-4"
    )

    e.compact()

    return e


# ============================================================================
# SECTION 10
# N.40 DIAGNOSTIC SUITE
# ============================================================================

def run_tests(
) -> None:

    banner(
        f"{UNIT}: "
        "CROSS-GENERATION COMPACTION "
        "CRASH RECOVERY + TERMINAL CLOSURE"
    )

    print(
        "SAFETY: REAL POST DISABLED | "
        "DEMO POST DISABLED | "
        "ALL NETWORK WRITES DISABLED",
        flush=True,
    )

    print(
        "MODE: SYNTHETIC TRANSPORT ONLY",
        flush=True,
    )

    with tempfile.TemporaryDirectory(
        prefix="r28-n40-"
    ) as td:

        root = Path(td)

        e = make_baseline(
            root
        )


        # ====================================================================
        # TEST 1
        # N.39 BASELINE RESTORE
        # ====================================================================

        banner(
            f"{UNIT} TEST 1: "
            "N.39 BASELINE RESTORES"
        )

        e = Engine.restore(
            root
        )

        e.validate_complete_state()

        passed(
            "N.39 Baseline Durable State Restored"
        )

        passed(
            "Baseline WAL Integrity Validates"
        )


        # ====================================================================
        # TEST 2
        # CRASH AFTER COMPACTION BEGIN
        # ====================================================================

        banner(
            f"{UNIT} TEST 2: "
            "CRASH AFTER COMPACTION BEGIN"
        )

        cp_id = (
            e.begin_compaction()
        )

        crashed = Engine.restore(
            root
        )

        require(
            crashed.state.compaction_in_progress,
            "compaction intent did not survive restart",
        )

        crashed.recover_incomplete_compaction()

        require(
            not crashed.state.compaction_in_progress,
            "compaction did not finalize after restart",
        )

        passed(
            "Compaction Intent Survived Restart"
        )

        passed(
            "Crash After Compaction Begin Recovered"
        )


        # ====================================================================
        # TEST 3
        # CRASH AFTER CHECKPOINT CREATION
        # ====================================================================

        banner(
            f"{UNIT} TEST 3: "
            "CRASH AFTER CHECKPOINT CREATION"
        )

        e = crashed

        cp_id = (
            e.begin_compaction()
        )

        cp = (
            e.build_checkpoint(
                cp_id
            )
        )

        before = (
            cp.seal
        )

        e = Engine.restore(
            root
        )

        require(
            cp_id
            in e.checkpoints,
            "checkpoint missing after restart",
        )

        require(
            e.checkpoints[
                cp_id
            ].seal
            ==
            before,
            "checkpoint changed across restart",
        )

        e.recover_incomplete_compaction()

        passed(
            "Prepared Checkpoint Survived Restart"
        )

        passed(
            "Crash After Checkpoint Creation Recovered"
        )


        # ====================================================================
        # TEST 4
        # CRASH AFTER MANIFEST PUBLICATION
        # ====================================================================

        banner(
            f"{UNIT} TEST 4: "
            "CRASH AFTER MANIFEST PUBLICATION"
        )

        cp_id = (
            e.begin_compaction()
        )

        cp = (
            e.build_checkpoint(
                cp_id
            )
        )

        m = (
            e.publish_manifest(
                cp
            )
        )

        mid = (
            e.state.pending_manifest_id
        )

        e = Engine.restore(
            root
        )

        require(
            mid
            in e.manifests,
            "published manifest missing after restart",
        )

        e.recover_incomplete_compaction()

        require(
            e.state.active_checkpoint_id
            ==
            cp_id,
            "published checkpoint not activated",
        )

        passed(
            "Published Manifest Survived Restart"
        )

        passed(
            "Crash After Manifest Publication Recovered"
        )


        # ====================================================================
        # TEST 5
        # SECOND RESTART
        # ====================================================================

        banner(
            f"{UNIT} TEST 5: "
            "SECOND RESTART AFTER RECOVERY"
        )

        e = Engine.restore(
            root
        )

        e.validate_complete_state()

        passed(
            "Recovered Compaction Survives Second Restart"
        )

        passed(
            "Recovered Durable State Validates"
        )


        # ====================================================================
        # TEST 6
        # GENERATION ADVANCE BLOCKED DURING COMPACTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 6: "
            "GENERATION ADVANCE BLOCKED DURING RECOVERY WINDOW"
        )

        cp_id = (
            e.begin_compaction()
        )

        expect_block(
            "Generation Advance During Compaction Rejected",
            "cannot advance generation during compaction",
            e.advance_generation,
        )

        e.recover_incomplete_compaction()


        # ====================================================================
        # TEST 7
        # GENERATION ADVANCE AFTER RECOVERY
        # ====================================================================

        banner(
            f"{UNIT} TEST 7: "
            "GENERATION ADVANCE AFTER RECOVERY"
        )

        old_gen = (
            e.state.generation
        )

        old_lin = (
            e.state.lineage
        )

        old_epoch = (
            e.state.recovery_epoch
        )

        e.advance_generation()

        require(
            e.state.generation
            ==
            old_gen + 1,
            "generation did not advance exactly once",
        )

        require(
            e.state.lineage
            !=
            old_lin,
            "lineage did not change",
        )

        require(
            e.state.recovery_epoch
            ==
            old_epoch + 1,
            "recovery epoch did not advance exactly once",
        )

        passed(
            "Generation Advanced Exactly Once"
        )

        passed(
            "Lineage Changed Exactly Once"
        )

        passed(
            "Recovery Epoch Advanced Exactly Once"
        )


        # ====================================================================
        # TEST 8
        # CRASH IMMEDIATELY AFTER GENERATION ADVANCE
        # ====================================================================

        banner(
            f"{UNIT} TEST 8: "
            "CRASH IMMEDIATELY AFTER GENERATION ADVANCE"
        )

        generation_snapshot = (
            e.state.generation
        )

        lineage_snapshot = (
            e.state.lineage
        )

        epoch_snapshot = (
            e.state.recovery_epoch
        )

        e = Engine.restore(
            root
        )

        require(
            e.state.generation
            ==
            generation_snapshot,
            "generation rollback after restart",
        )

        require(
            e.state.lineage
            ==
            lineage_snapshot,
            "lineage rollback after restart",
        )

        require(
            e.state.recovery_epoch
            ==
            epoch_snapshot,
            "recovery epoch rollback after restart",
        )

        passed(
            "Advanced Generation Survived Restart"
        )

        passed(
            "Advanced Lineage Survived Restart"
        )

        passed(
            "Advanced Recovery Epoch Survived Restart"
        )


        # ====================================================================
        # TEST 9
        # OLD FENCES SURVIVE NEW GENERATION
        # ====================================================================

        banner(
            f"{UNIT} TEST 9: "
            "OLD FINALIZED FENCES SURVIVE NEW GENERATION"
        )

        for pid in (
            "promotion-1",
            "promotion-2",
            "promotion-3",
            "promotion-4",
        ):

            require(
                pid
                in
                e.state.finalized_promotions,
                f"missing finalized fence {pid}",
            )

        passed(
            "All Historical Promotion Fences Preserved"
        )


        # ====================================================================
        # TEST 10
        # HISTORICAL REPLAY REJECTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 10: "
            "OLD PROMOTION REPLAY REJECTED"
        )

        expect_block(
            "Historical Finalized Promotion Replay Rejected",
            "promotion already finalized",
            lambda: e.finalize_promotion(
                "promotion-2"
            ),
        )


        # ====================================================================
        # TEST 11
        # NEW GENERATION CONTINUITY
        # ====================================================================

        banner(
            f"{UNIT} TEST 11: "
            "NEW-GENERATION TRANSACTION CONTINUITY"
        )

        dispatches_before = (
            e.state.synthetic_dispatch_count
        )

        receipt = (
            e.finalize_promotion(
                "promotion-5"
            )
        )

        require(
            "promotion-5"
            in
            e.state.finalized_promotions,
            "new promotion not finalized",
        )

        require(
            receipt
            in
            e.state.finalized_receipts,
            "new receipt not finalized",
        )

        require(
            e.state.synthetic_dispatch_count
            ==
            dispatches_before + 1,
            "synthetic dispatch count mismatch",
        )

        passed(
            "New Generation Promotion Finalized"
        )

        passed(
            "New Generation Receipt Finalized"
        )

        passed(
            "Exactly One Synthetic Dispatch Added"
        )


        # ====================================================================
        # TEST 12
        # NEW GENERATION COMPACTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 12: "
            "NEW-GENERATION COMPACTION"
        )

        parent_id = (
            e.state.active_checkpoint_id
        )

        parent_hash = (
            e.state.active_checkpoint_hash
        )

        cp_new = (
            e.compact()
        )

        require(
            cp_new.generation
            ==
            e.state.generation,
            "new checkpoint generation mismatch",
        )

        require(
            cp_new.lineage
            ==
            e.state.lineage,
            "new checkpoint lineage mismatch",
        )

        require(
            cp_new.recovery_epoch
            ==
            e.state.recovery_epoch,
            "new checkpoint recovery epoch mismatch",
        )

        require(
            cp_new.parent_checkpoint_id
            ==
            parent_id,
            "cross-generation checkpoint parent mismatch",
        )

        require(
            cp_new.parent_checkpoint_hash
            ==
            parent_hash,
            "cross-generation parent hash mismatch",
        )

        passed(
            "New Generation Compaction Finalized"
        )

        passed(
            "Cross-Generation Checkpoint Parent Preserved"
        )

        passed(
            "Cross-Generation Checkpoint Parent Hash Preserved"
        )


        # ====================================================================
        # TEST 13
        # HISTORICAL CHECKPOINT VERIFICATION
        # ====================================================================

        banner(
            f"{UNIT} TEST 13: "
            "HISTORICAL CHECKPOINT REMAINS VERIFIABLE"
        )

        historical = [
            c
            for c
            in e.checkpoints.values()
            if c.generation
            <
            e.state.generation
        ]

        require(
            historical,
            "no historical checkpoint found",
        )

        for cp in historical:

            e.validate_checkpoint(
                cp,
                allow_historical=True,
            )

        passed(
            "Historical Checkpoints Remain Integrity Verifiable"
        )


        # ====================================================================
        # TEST 14
        # STALE CHECKPOINT REJECTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 14: "
            "STALE CHECKPOINT CANNOT BECOME CURRENT"
        )

        old_cp = (
            historical[-1]
        )

        expect_block(
            "Stale Cross-Generation Checkpoint Rejected",
            "checkpoint generation mismatch",
            lambda: e.validate_checkpoint(
                old_cp
            ),
        )


        # ====================================================================
        # TEST 15
        # HISTORICAL MANIFEST VERIFICATION
        # ====================================================================

        banner(
            f"{UNIT} TEST 15: "
            "HISTORICAL MANIFEST REMAINS VERIFIABLE"
        )

        old_manifests = [
            m
            for m
            in e.manifests.values()
            if m.generation
            <
            e.state.generation
        ]

        require(
            old_manifests,
            "no historical manifest found",
        )

        for man in old_manifests:

            e.validate_manifest(
                man,
                allow_historical=True,
            )

        passed(
            "Historical Manifests Remain Integrity Verifiable"
        )


        # ====================================================================
        # TEST 16
        # STALE MANIFEST REJECTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 16: "
            "STALE MANIFEST CANNOT BECOME CURRENT"
        )

        expect_block(
            "Stale Cross-Generation Manifest Rejected",
            "manifest generation mismatch",
            lambda: e.validate_manifest(
                old_manifests[-1]
            ),
        )


        # ====================================================================
        # TEST 17
        # CHECKPOINT TAMPER REJECTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 17: "
            "CHECKPOINT TAMPER REJECTION"
        )

        victim = copy.deepcopy(
            cp_new
        )

        victim.finalized_promotions.append(
            "forged-promotion"
        )

        expect_block(
            "Tampered Checkpoint Rejected",
            "checkpoint integrity seal mismatch",
            lambda: e.validate_checkpoint(
                victim,
                allow_historical=True,
            ),
        )


        # ====================================================================
        # TEST 18
        # MANIFEST TAMPER REJECTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 18: "
            "MANIFEST TAMPER REJECTION"
        )

        active_manifest = max(
            e.manifests.values(),
            key=lambda x:
                x.active_sequence,
        )

        victim_m = copy.deepcopy(
            active_manifest
        )

        victim_m.active_sequence += 1

        expect_block(
            "Tampered Manifest Rejected",
            "manifest integrity seal mismatch",
            lambda: e.validate_manifest(
                victim_m,
                allow_historical=True,
            ),
        )


        # ====================================================================
        # TEST 19
        # WAL HASH TAMPER REJECTION
        # ====================================================================

        banner(
            f"{UNIT} TEST 19: "
            "WAL HASH TAMPER REJECTION"
        )

        victim_e = Engine.restore(
            root
        )

        victim_e.wal[
            -1
        ].payload[
            "tampered"
        ] = True

        expect_block(
            "Tampered WAL Record Rejected",
            "WAL record hash mismatch",
            victim_e.validate_wal,
        )


        # ====================================================================
        # TEST 20
        # GLOBAL WAL SEQUENCE MONOTONICITY
        # ====================================================================

        banner(
            f"{UNIT} TEST 20: "
            "GLOBAL WAL SEQUENCE MONOTONICITY"
        )

        e = Engine.restore(
            root
        )

        seqs = [
            r.seq
            for r
            in e.wal
        ]

        require(
            seqs
            ==
            list(
                range(
                    1,
                    len(seqs) + 1,
                )
            ),
            "global WAL sequence is not contiguous",
        )

        require(
            e.state.wal_seq
            ==
            seqs[-1],
            "state WAL sequence mismatch",
        )

        passed(
            "Global WAL Sequence Never Reset"
        )

        passed(
            "State WAL Sequence Matches Journal Tail"
        )


        # ====================================================================
        # TEST 21
        # ACTIVE CHECKPOINT CONTAINS ALL FENCES
        # ====================================================================

        banner(
            f"{UNIT} TEST 21: "
            "FINALIZED FENCES PRESENT IN ACTIVE CHECKPOINT"
        )

        active_cp = e.checkpoints[
            e.state.active_checkpoint_id
        ]

        require(
            set(
                active_cp.finalized_promotions
            )
            ==
            e.state.finalized_promotions,
            "promotion fences missing from active checkpoint",
        )

        require(
            set(
                active_cp.finalized_receipts
            )
            ==
            e.state.finalized_receipts,
            "receipt fences missing from active checkpoint",
        )

        passed(
            "All Promotion Fences Present In Active Checkpoint"
        )

        passed(
            "All Receipt Fences Present In Active Checkpoint"
        )


        # ====================================================================
        # TEST 22
        # THREE CONSECUTIVE RESTARTS
        # ====================================================================

        banner(
            f"{UNIT} TEST 22: "
            "FINAL MULTI-RESTART STABILITY"
        )

        e.persist()

        for _ in range(3):

            e = Engine.restore(
                root
            )

            e.validate_complete_state()

        passed(
            "Final State Survives Three Consecutive Restarts"
        )

        passed(
            "Checkpoint Ancestry Survives Three Consecutive Restarts"
        )


        # ====================================================================
        # TEST 23
        # SYNTHETIC TRANSPORT POLICY
        # ====================================================================

        banner(
            f"{UNIT} TEST 23: "
            "SYNTHETIC TRANSPORT EXACTNESS"
        )

        require(
            all(
                x["synthetic"]
                for x
                in e.transport.dispatches
            )
            if e.transport.dispatches
            else True,
            "non-synthetic dispatch detected",
        )

        require(
            not REAL_POST_ENABLED,
            "real POST enabled",
        )

        require(
            not DEMO_POST_ENABLED,
            "demo POST enabled",
        )

        require(
            not NETWORK_WRITES_ENABLED,
            "network writes enabled",
        )

        passed(
            "Real POST Disabled"
        )

        passed(
            "Demo POST Disabled"
        )

        passed(
            "All Network Writes Disabled"
        )

        passed(
            "Synthetic Transport Only"
        )


        # ====================================================================
        # TEST 24
        # TERMINAL VALIDATION
        # ====================================================================

        banner(
            f"{UNIT} TEST 24: "
            "TERMINAL DURABLE STATE VALIDATION"
        )

        e.validate_complete_state()

        passed(
            "Complete Durable State Validates"
        )

        passed(
            "WAL Final Hash Matches Journal"
        )

        passed(
            "Checkpoint And Manifest Ancestry Validate"
        )


        # ====================================================================
        # FINAL N.40 RESULT
        # ====================================================================

        banner(
            f"{UNIT}: ALL DIAGNOSTICS PASSED"
        )

        print(
            "NO REAL ORDER WAS SENT",
            flush=True,
        )

        print(
            "NO DEMO ORDER WAS SENT",
            flush=True,
        )

        print(
            "NO NETWORK WRITE WAS ATTEMPTED",
            flush=True,
        )

        print(
            f"{UNIT}: TEST GROUPS EXECUTED = 24",
            flush=True,
        )

        print(
            f"{UNIT}: PASS ASSERTIONS = "
            f"{PASS_ASSERTIONS}",
            flush=True,
        )


# ============================================================================
# SECTION 11
# HEALTH SERVER
# ============================================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self,
    ):

        body = canonical(
            {
                "unit":
                    UNIT,

                "status":
                    "ok",

                "synthetic_only":
                    SYNTHETIC_TRANSPORT_ONLY,

                "network_writes":
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
                len(body)
            ),
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


# ============================================================================
# SECTION 12
# START HEALTH SERVER
# ============================================================================

def start_health_server(
) -> None:

    server = HTTPServer(
        (
            "0.0.0.0",
            PORT,
        ),
        HealthHandler,
    )

    t = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    t.start()

    print(
        f"{UNIT}: "
        f"HEALTH SERVER LISTENING ON PORT {PORT}",
        flush=True,
    )


# ============================================================================
# SECTION 13
# HEARTBEAT
# ============================================================================

def heartbeat_loop(
) -> None:

    n = 1

    while True:

        print(
            f"{UNIT}: HEARTBEAT {n} | "
            f"synthetic-only="
            f"{SYNTHETIC_TRANSPORT_ONLY} | "
            f"network-writes="
            f"{NETWORK_WRITES_ENABLED}",
            flush=True,
        )

        n += 1

        time.sleep(
            30
        )


# ============================================================================
# SECTION 14
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":

    run_tests()

    start_health_server()

    heartbeat_loop()
