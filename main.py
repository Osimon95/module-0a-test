# ============================================================================
# R28 UNIT N.33
# DURABLE CHECKPOINT PROMOTION + GENERATION / LINEAGE FENCING
# + FINALIZED-PROMOTION REPLAY REJECTION
#
# CORRECTED COPY/PASTE VERSION
# SINGLE COMPLETE MAIN.PY
#
# SAFETY:
#   - REAL POST DISABLED
#   - DEMO POST DISABLED
#   - ALL NETWORK WRITES DISABLED
#   - SYNTHETIC TRANSPORT ONLY
#
# N.33 INCREMENT OVER N.32:
#   - DURABLE CHECKPOINT PROMOTION INTENTS
#   - PROMOTION GENERATION / LINEAGE / EPOCH BINDING
#   - PENDING PROMOTION RECOVERY AFTER RESTART
#   - FINALIZED PROMOTION ID FENCING
#   - FINALIZED PROMOTION REPLAY REJECTION
#   - STALE PROMOTION GENERATION REJECTION
#   - STALE PROMOTION LINEAGE REJECTION
#   - MANIFEST / CHECKPOINT AUTHORITY PRESERVATION
#
# IMPORTANT TEST-22 CORRECTION:
#   - A replay of an already-finalized promotion is expected to fail with:
#       "promotion intent already finalized"
#     rather than:
#       "pending promotion missing"
# ============================================================================

print("R28 UNIT N.33: MAIN.PY ENTERED", flush=True)

import copy
import hashlib
import hmac
import json
import os
import threading
import time
import uuid

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, List, Optional, Set


print("R28 UNIT N.33: IMPORTS COMPLETE", flush=True)


# ============================================================================
# GLOBAL CONSTANTS
# ============================================================================

UNIT_NAME = "R28 UNIT N.33"
UNIT_VERSION = "N.33"

SYMBOL = "BTCUSDT"
MARGIN_MODE = "ISOLATED"
LEVERAGE = "100"

LEVERAGE_ENDPOINT = "/capi/v2/account/leverage"
HTTP_METHOD = "POST"

REAL_POST_ENABLED = False
DEMO_POST_ENABLED = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

INTEGRITY_KEY = b"R28-N33-LOCAL-INTEGRITY-KEY"
PROMOTION_KEY = b"R28-N33-PROMOTION-KEY"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_COMMITTED = "COMMITTED"
PHASE_DISPATCHED = "DISPATCHED"
PHASE_COMPLETED = "COMPLETED"

print("R28 UNIT N.33: CONSTANTS INITIALIZED", flush=True)


# ============================================================================
# EXCEPTIONS / DIAGNOSTIC HELPERS
# ============================================================================

class LocalBlock(RuntimeError):
    pass


class ValidationFailure(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalBlock(message)


def separator() -> None:
    print("-" * 92, flush=True)


def test_header(number: int, name: str) -> None:
    separator()
    print(f"{UNIT_NAME} TEST {number}: {name}", flush=True)
    separator()


def pass_line(label: str) -> None:
    print(f"{label:<76} ✅ PASS", flush=True)


def fail_line(label: str) -> None:
    print(f"{label:<76} ❌ FAIL", flush=True)
    raise ValidationFailure(label)


def assert_true(label: str, condition: bool) -> None:
    if condition:
        pass_line(label)
    else:
        fail_line(label)


def expect_local_block(
    label: str,
    fn: Callable[[], Any],
    expected_substring: str,
) -> None:
    try:
        fn()

    except LocalBlock as exc:
        print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
        print(f"  {exc}", flush=True)

        if expected_substring not in str(exc):
            fail_line(
                f"{label} "
                f"(expected '{expected_substring}', got '{exc}')"
            )

        pass_line(label)
        return

    fail_line(f"{label} (expected LocalBlock)")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def hmac_hex(key: bytes, value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")

    return hmac.new(
        key,
        payload,
        hashlib.sha256,
    ).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


# ============================================================================
# DURABLE WAL RECORD
# ============================================================================

@dataclass
class WalRecord:
    sequence: int
    record_type: str
    generation: int
    lineage_id: str
    recovery_epoch: int
    payload_hash: str
    previous_hash: str
    record_hash: str = ""

    def body(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "record_type": self.record_type,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "payload_hash": self.payload_hash,
            "previous_hash": self.previous_hash,
        }

    def seal(self) -> None:
        self.record_hash = sha256_text(
            canonical_json(
                self.body()
            )
        )

    def validate(self) -> None:
        require(
            self.record_hash
            == sha256_text(
                canonical_json(
                    self.body()
                )
            ),
            "WAL record hash mismatch",
        )


# ============================================================================
# DURABLE CHECKPOINT
# ============================================================================

@dataclass
class Checkpoint:
    checkpoint_id: str
    slot: str
    sequence: int
    generation: int
    lineage_id: str
    recovery_epoch: int
    wal_length: int
    wal_final_hash: str
    payload_hash: str
    state_digest: str
    integrity_seal: str = ""

    def body(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "slot": self.slot,
            "sequence": self.sequence,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "wal_length": self.wal_length,
            "wal_final_hash": self.wal_final_hash,
            "payload_hash": self.payload_hash,
            "state_digest": self.state_digest,
        }

    def seal(self) -> None:
        self.integrity_seal = hmac_hex(
            INTEGRITY_KEY,
            self.body(),
        )

    def validate_seal(self) -> None:
        require(
            hmac.compare_digest(
                self.integrity_seal,
                hmac_hex(
                    INTEGRITY_KEY,
                    self.body(),
                ),
            ),
            "checkpoint integrity seal mismatch",
        )


# ============================================================================
# COMMITTED MANIFEST
# ============================================================================

@dataclass
class Manifest:
    manifest_id: str
    slot: str
    checkpoint_id: str
    checkpoint_sequence: int
    generation: int
    lineage_id: str
    recovery_epoch: int
    manifest_sequence: int
    integrity_seal: str = ""

    def body(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "slot": self.slot,
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_sequence": self.checkpoint_sequence,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "manifest_sequence": self.manifest_sequence,
        }

    def seal(self) -> None:
        self.integrity_seal = hmac_hex(
            INTEGRITY_KEY,
            self.body(),
        )

    def validate_seal(self) -> None:
        require(
            hmac.compare_digest(
                self.integrity_seal,
                hmac_hex(
                    INTEGRITY_KEY,
                    self.body(),
                ),
            ),
            "committed manifest integrity seal mismatch",
        )


# ============================================================================
# PROMOTION INTENT
# ============================================================================

@dataclass
class PromotionIntent:
    promotion_id: str
    checkpoint_id: str
    checkpoint_slot: str
    checkpoint_sequence: int
    expected_manifest_sequence: int
    generation: int
    lineage_id: str
    recovery_epoch: int
    payload_hash: str
    created_nonce: int
    integrity_seal: str = ""

    def body(self) -> Dict[str, Any]:
        return {
            "promotion_id": self.promotion_id,
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_slot": self.checkpoint_slot,
            "checkpoint_sequence": self.checkpoint_sequence,
            "expected_manifest_sequence": self.expected_manifest_sequence,
            "generation": self.generation,
            "lineage_id": self.lineage_id,
            "recovery_epoch": self.recovery_epoch,
            "payload_hash": self.payload_hash,
            "created_nonce": self.created_nonce,
        }

    def seal(self) -> None:
        self.integrity_seal = hmac_hex(
            PROMOTION_KEY,
            self.body(),
        )

    def validate_seal(self) -> None:
        require(
            hmac.compare_digest(
                self.integrity_seal,
                hmac_hex(
                    PROMOTION_KEY,
                    self.body(),
                ),
            ),
            "promotion intent integrity seal mismatch",
        )


# ============================================================================
# SYNTHETIC TRANSPORT RECEIPT
# ============================================================================

@dataclass
class SyntheticReceipt:
    receipt_id: str
    method: str
    path: str
    payload_hash: str
    synthetic: bool
    network_transmitted: bool


# ============================================================================
# DURABLE STATE
# ============================================================================

@dataclass
class DurableState:
    generation: int = 1

    lineage_id: str = field(
        default_factory=lambda: new_id("lineage")
    )

    recovery_epoch: int = 1
    nonce: int = 0

    wal: List[WalRecord] = field(
        default_factory=list
    )

    checkpoints: Dict[str, Checkpoint] = field(
        default_factory=dict
    )

    committed_manifest: Optional[Manifest] = None

    manifest_sequence: int = 0

    pending_promotions: Dict[str, PromotionIntent] = field(
        default_factory=dict
    )

    finalized_promotion_ids: Set[str] = field(
        default_factory=set
    )

    synthetic_receipts: List[SyntheticReceipt] = field(
        default_factory=list
    )

    def clone(self) -> "DurableState":
        return copy.deepcopy(self)


# ============================================================================
# R28 UNIT N.33 ENGINE
# ============================================================================

class N33Engine:

    def __init__(
        self,
        state: Optional[DurableState] = None,
    ) -> None:

        if state is None:
            self.state = DurableState()
        else:
            self.state = state.clone()

        self._lock = threading.RLock()


    # =========================================================================
    # PAYLOAD
    # =========================================================================

    @property
    def payload(self) -> Dict[str, str]:
        return {
            "symbol": SYMBOL,
            "marginMode": MARGIN_MODE,
            "leverage": LEVERAGE,
        }


    @property
    def payload_hash(self) -> str:
        return sha256_text(
            canonical_json(
                self.payload
            )
        )


    # =========================================================================
    # SNAPSHOT / RESTORE
    # =========================================================================

    def snapshot(self) -> DurableState:

        with self._lock:
            return self.state.clone()


    @classmethod
    def restore_state(
        cls,
        state: DurableState,
    ) -> "N33Engine":

        engine = cls(state)

        engine.validate_durable_state()

        return engine


    # =========================================================================
    # WAL APPEND
    # =========================================================================

    def append_wal(
        self,
        record_type: str,
    ) -> WalRecord:

        with self._lock:

            if self.state.wal:
                previous_hash = (
                    self.state.wal[-1].record_hash
                )
            else:
                previous_hash = "0" * 64

            record = WalRecord(
                sequence=len(self.state.wal) + 1,
                record_type=record_type,
                generation=self.state.generation,
                lineage_id=self.state.lineage_id,
                recovery_epoch=self.state.recovery_epoch,
                payload_hash=self.payload_hash,
                previous_hash=previous_hash,
            )

            record.seal()

            self.state.wal.append(record)

            return copy.deepcopy(record)


    # =========================================================================
    # WAL VALIDATION
    # =========================================================================

    def validate_wal(self) -> None:

        expected_previous = "0" * 64

        for index, record in enumerate(
            self.state.wal,
            start=1,
        ):

            record.validate()

            require(
                record.sequence == index,
                "WAL sequence mismatch",
            )

            require(
                record.previous_hash
                == expected_previous,
                "WAL chain mismatch",
            )

            require(
                record.generation
                == self.state.generation,
                "WAL generation mismatch",
            )

            require(
                record.lineage_id
                == self.state.lineage_id,
                "WAL lineage mismatch",
            )

            require(
                record.recovery_epoch
                == self.state.recovery_epoch,
                "WAL recovery epoch mismatch",
            )

            require(
                record.payload_hash
                == self.payload_hash,
                "WAL payload hash mismatch",
            )

            expected_previous = (
                record.record_hash
            )


    # =========================================================================
    # CHECKPOINT CREATION
    # =========================================================================

    def create_checkpoint(
        self,
        slot: str,
    ) -> Checkpoint:

        with self._lock:

            require(
                slot in ("A", "B"),
                "invalid checkpoint slot",
            )

            self.append_wal(
                f"CHECKPOINT_{slot}"
            )

            self.state.nonce += 1

            state_digest = sha256_text(
                canonical_json(
                    {
                        "generation":
                            self.state.generation,

                        "lineage_id":
                            self.state.lineage_id,

                        "recovery_epoch":
                            self.state.recovery_epoch,

                        "nonce":
                            self.state.nonce,
                    }
                )
            )

            checkpoint = Checkpoint(
                checkpoint_id=new_id(
                    "checkpoint"
                ),

                slot=slot,

                sequence=len(
                    self.state.wal
                ),

                generation=
                    self.state.generation,

                lineage_id=
                    self.state.lineage_id,

                recovery_epoch=
                    self.state.recovery_epoch,

                wal_length=len(
                    self.state.wal
                ),

                wal_final_hash=
                    self.state.wal[-1].record_hash,

                payload_hash=
                    self.payload_hash,

                state_digest=
                    state_digest,
            )

            checkpoint.seal()

            self.state.checkpoints[
                slot
            ] = checkpoint

            return copy.deepcopy(
                checkpoint
            )


    # =========================================================================
    # CHECKPOINT VALIDATION
    # =========================================================================

    def _validate_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> None:

        checkpoint.validate_seal()

        require(
            checkpoint.slot
            in ("A", "B"),
            "invalid checkpoint slot",
        )

        require(
            checkpoint.generation
            == self.state.generation,
            "checkpoint generation mismatch",
        )

        require(
            checkpoint.lineage_id
            == self.state.lineage_id,
            "checkpoint lineage mismatch",
        )

        require(
            checkpoint.recovery_epoch
            == self.state.recovery_epoch,
            "checkpoint recovery epoch mismatch",
        )

        require(
            checkpoint.payload_hash
            == self.payload_hash,
            "checkpoint payload hash mismatch",
        )

        require(
            checkpoint.wal_length
            == checkpoint.sequence,
            "checkpoint WAL length mismatch",
        )

        require(
            checkpoint.wal_length
            <= len(self.state.wal),
            "checkpoint WAL length mismatch",
        )

        if checkpoint.wal_length > 0:

            wal_record = self.state.wal[
                checkpoint.wal_length - 1
            ]

            require(
                wal_record.record_hash
                == checkpoint.wal_final_hash,
                "checkpoint WAL final hash mismatch",
            )


    # =========================================================================
    # MANIFEST VALIDATION
    # =========================================================================

    def _validate_manifest(
        self,
        manifest: Manifest,
    ) -> Checkpoint:

        manifest.validate_seal()

        require(
            manifest.slot
            in self.state.checkpoints,
            "manifest checkpoint missing",
        )

        checkpoint = (
            self.state.checkpoints[
                manifest.slot
            ]
        )

        self._validate_checkpoint(
            checkpoint
        )

        require(
            checkpoint.checkpoint_id
            == manifest.checkpoint_id,
            "manifest/checkpoint identity mismatch",
        )

        require(
            checkpoint.sequence
            == manifest.checkpoint_sequence,
            "manifest/checkpoint sequence mismatch",
        )

        require(
            manifest.generation
            == self.state.generation,
            "manifest generation mismatch",
        )

        require(
            manifest.lineage_id
            == self.state.lineage_id,
            "manifest lineage mismatch",
        )

        require(
            manifest.recovery_epoch
            == self.state.recovery_epoch,
            "manifest recovery epoch mismatch",
        )

        require(
            manifest.manifest_sequence
            == self.state.manifest_sequence,
            "manifest sequence rollback detected",
        )

        return checkpoint


    # =========================================================================
    # PREPARE PROMOTION
    # =========================================================================

    def prepare_promotion(
        self,
        slot: str,
    ) -> PromotionIntent:

        with self._lock:

            require(
                slot in self.state.checkpoints,
                "promotion checkpoint missing",
            )

            checkpoint = (
                self.state.checkpoints[
                    slot
                ]
            )

            self._validate_checkpoint(
                checkpoint
            )

            if (
                self.state.committed_manifest
                is not None
            ):

                current = (
                    self._validate_manifest(
                        self.state.committed_manifest
                    )
                )

                require(
                    checkpoint.sequence
                    > current.sequence,
                    (
                        "promotion checkpoint "
                        "is not newer than "
                        "committed authority"
                    ),
                )

            self.state.nonce += 1

            intent = PromotionIntent(
                promotion_id=new_id(
                    "promotion"
                ),

                checkpoint_id=
                    checkpoint.checkpoint_id,

                checkpoint_slot=
                    checkpoint.slot,

                checkpoint_sequence=
                    checkpoint.sequence,

                expected_manifest_sequence=
                    self.state.manifest_sequence + 1,

                generation=
                    self.state.generation,

                lineage_id=
                    self.state.lineage_id,

                recovery_epoch=
                    self.state.recovery_epoch,

                payload_hash=
                    self.payload_hash,

                created_nonce=
                    self.state.nonce,
            )

            intent.seal()

            self.state.pending_promotions[
                intent.promotion_id
            ] = copy.deepcopy(
                intent
            )

            return copy.deepcopy(
                intent
            )


    # =========================================================================
    # N.33 PROMOTION INTENT VALIDATION
    # =========================================================================

    def _n33_validate_promotion_intent(
        self,
        intent: PromotionIntent,
    ) -> Checkpoint:

        # --------------------------------------------------------------------
        # IMPORTANT N.33 FINALIZED-ID FENCE
        #
        # This check deliberately occurs BEFORE pending promotion lookup.
        #
        # Therefore a replay of a previously committed promotion must report:
        #
        #   "promotion intent already finalized"
        #
        # and NOT:
        #
        #   "pending promotion missing"
        # --------------------------------------------------------------------

        require(
            intent.promotion_id
            not in self.state.finalized_promotion_ids,
            "promotion intent already finalized",
        )

        require(
            intent.promotion_id
            in self.state.pending_promotions,
            "pending promotion missing",
        )

        durable_intent = (
            self.state.pending_promotions[
                intent.promotion_id
            ]
        )

        durable_intent.validate_seal()
        intent.validate_seal()

        require(
            durable_intent == intent,
            "promotion intent durable copy mismatch",
        )

        require(
            intent.generation
            == self.state.generation,
            "promotion intent generation mismatch",
        )

        require(
            intent.lineage_id
            == self.state.lineage_id,
            "promotion intent lineage mismatch",
        )

        require(
            intent.recovery_epoch
            == self.state.recovery_epoch,
            "promotion intent recovery epoch mismatch",
        )

        require(
            intent.payload_hash
            == self.payload_hash,
            "promotion intent payload hash mismatch",
        )

        require(
            intent.expected_manifest_sequence
            == self.state.manifest_sequence + 1,
            "promotion manifest sequence mismatch",
        )

        require(
            intent.checkpoint_slot
            in self.state.checkpoints,
            "promotion checkpoint missing",
        )

        checkpoint = (
            self.state.checkpoints[
                intent.checkpoint_slot
            ]
        )

        self._validate_checkpoint(
            checkpoint
        )

        require(
            checkpoint.checkpoint_id
            == intent.checkpoint_id,
            "promotion checkpoint identity mismatch",
        )

        require(
            checkpoint.sequence
            == intent.checkpoint_sequence,
            "promotion checkpoint sequence mismatch",
        )

        require(
            checkpoint.generation
            == intent.generation,
            "promotion checkpoint generation mismatch",
        )

        require(
            checkpoint.lineage_id
            == intent.lineage_id,
            "promotion checkpoint lineage mismatch",
        )

        require(
            checkpoint.recovery_epoch
            == intent.recovery_epoch,
            "promotion checkpoint recovery epoch mismatch",
        )

        if (
            self.state.committed_manifest
            is not None
        ):

            current = self._validate_manifest(
                self.state.committed_manifest
            )

            require(
                checkpoint.sequence
                > current.sequence,
                (
                    "promotion checkpoint "
                    "is not newer than "
                    "committed authority"
                ),
            )

        return checkpoint


    # =========================================================================
    # COMMIT PROMOTION
    # =========================================================================

    def commit_promotion(
        self,
        intent: PromotionIntent,
    ) -> Manifest:

        with self._lock:

            checkpoint = (
                self._n33_validate_promotion_intent(
                    intent
                )
            )

            new_manifest_sequence = (
                self.state.manifest_sequence
                + 1
            )

            require(
                new_manifest_sequence
                == intent.expected_manifest_sequence,
                "promotion manifest sequence mismatch",
            )

            manifest = Manifest(
                manifest_id=new_id(
                    "manifest"
                ),

                slot=
                    checkpoint.slot,

                checkpoint_id=
                    checkpoint.checkpoint_id,

                checkpoint_sequence=
                    checkpoint.sequence,

                generation=
                    self.state.generation,

                lineage_id=
                    self.state.lineage_id,

                recovery_epoch=
                    self.state.recovery_epoch,

                manifest_sequence=
                    new_manifest_sequence,
            )

            manifest.seal()

            # ----------------------------------------------------------------
            # DURABLE AUTHORITY COMMIT
            # ----------------------------------------------------------------

            self.state.manifest_sequence = (
                new_manifest_sequence
            )

            self.state.committed_manifest = (
                manifest
            )

            # ----------------------------------------------------------------
            # FINALIZED PROMOTION FENCE
            # ----------------------------------------------------------------

            self.state.finalized_promotion_ids.add(
                intent.promotion_id
            )

            self.state.pending_promotions.pop(
                intent.promotion_id,
                None,
            )

            # ----------------------------------------------------------------
            # WAL RECORD
            # ----------------------------------------------------------------

            self.append_wal(
                "PROMOTION_COMMITTED"
            )

            return copy.deepcopy(
                manifest
            )


    # =========================================================================
    # RECOVER PENDING PROMOTIONS
    # =========================================================================

    def recover_pending_promotions(
        self,
    ) -> List[Manifest]:

        with self._lock:

            recovered: List[Manifest] = []

            promotion_ids = list(
                self.state.pending_promotions.keys()
            )

            for promotion_id in promotion_ids:

                intent = copy.deepcopy(
                    self.state.pending_promotions[
                        promotion_id
                    ]
                )

                manifest = self.commit_promotion(
                    intent
                )

                recovered.append(
                    manifest
                )

            return recovered


    # =========================================================================
    # SYNTHETIC TRANSPORT FIREBREAK
    # =========================================================================

    def synthetic_dispatch(
        self,
    ) -> SyntheticReceipt:

        require(
            SYNTHETIC_TRANSPORT_ONLY,
            "synthetic transport policy disabled",
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

        receipt = SyntheticReceipt(
            receipt_id=new_id(
                "receipt"
            ),

            method=
                HTTP_METHOD,

            path=
                LEVERAGE_ENDPOINT,

            payload_hash=
                self.payload_hash,

            synthetic=True,

            network_transmitted=False,
        )

        self.state.synthetic_receipts.append(
            receipt
        )

        return copy.deepcopy(
            receipt
        )


    # =========================================================================
    # GENERATION ADVANCE
    # =========================================================================

    def advance_generation(
        self,
    ) -> None:

        with self._lock:

            require(
                not self.state.pending_promotions,
                (
                    "cannot advance generation "
                    "with pending promotion"
                ),
            )

            self.state.generation += 1

            self.state.lineage_id = new_id(
                "lineage"
            )

            self.state.recovery_epoch += 1

            self.state.nonce += 1

            # New generation establishes a new WAL/checkpoint authority chain.

            self.state.wal = []

            self.state.checkpoints = {}

            self.state.committed_manifest = None

            self.state.manifest_sequence = 0

            # IMPORTANT:
            #
            # finalized_promotion_ids intentionally survives generation
            # transition so historical promotion IDs cannot become valid
            # again through an ABA-style generation rollover.


    # =========================================================================
    # COMPLETE DURABLE STATE VALIDATION
    # =========================================================================

    def validate_durable_state(
        self,
    ) -> None:

        with self._lock:

            require(
                self.state.generation >= 1,
                "invalid generation",
            )

            require(
                bool(
                    self.state.lineage_id
                ),
                "lineage missing",
            )

            require(
                self.state.recovery_epoch >= 1,
                "invalid recovery epoch",
            )

            require(
                self.state.manifest_sequence >= 0,
                "invalid manifest sequence",
            )

            self.validate_wal()

            for checkpoint in (
                self.state.checkpoints.values()
            ):

                self._validate_checkpoint(
                    checkpoint
                )

            if (
                self.state.committed_manifest
                is not None
            ):

                self._validate_manifest(
                    self.state.committed_manifest
                )

            for (
                promotion_id,
                intent,
            ) in (
                self.state.pending_promotions.items()
            ):

                require(
                    promotion_id
                    == intent.promotion_id,
                    "pending promotion key mismatch",
                )

                require(
                    promotion_id
                    not in self.state.finalized_promotion_ids,
                    "pending promotion already finalized",
                )

                intent.validate_seal()

                require(
                    intent.generation
                    == self.state.generation,
                    "promotion intent generation mismatch",
                )

                require(
                    intent.lineage_id
                    == self.state.lineage_id,
                    "promotion intent lineage mismatch",
                )

                require(
                    intent.recovery_epoch
                    == self.state.recovery_epoch,
                    "promotion intent recovery epoch mismatch",
                )


print(
    "R28 UNIT N.33: ENGINE DEFINITIONS LOADED",
    flush=True,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

def build_test_engine() -> N33Engine:

    engine = N33Engine()

    engine.append_wal(
        "BOOTSTRAP"
    )

    return engine


def prepare_initial_authority(
    engine: N33Engine,
) -> Manifest:

    checkpoint = engine.create_checkpoint(
        "A"
    )

    intent = engine.prepare_promotion(
        checkpoint.slot
    )

    return engine.commit_promotion(
        intent
    )


def prepare_valid_promotion(
    engine: N33Engine,
) -> PromotionIntent:

    if (
        engine.state.committed_manifest
        is None
    ):

        prepare_initial_authority(
            engine
        )

    current_slot = (
        engine.state.committed_manifest.slot
    )

    if current_slot == "A":
        next_slot = "B"
    else:
        next_slot = "A"

    checkpoint = engine.create_checkpoint(
        next_slot
    )

    return engine.prepare_promotion(
        checkpoint.slot
    )


# ============================================================================
# R28 UNIT N.33 TEST 1
# INITIAL STATE
# ============================================================================

def test_01_initial_state() -> None:

    test_header(
        1,
        "INITIAL STATE",
    )

    engine = build_test_engine()

    assert_true(
        "Initial Generation Is One",
        engine.state.generation == 1,
    )

    assert_true(
        "Initial Recovery Epoch Is One",
        engine.state.recovery_epoch == 1,
    )

    assert_true(
        "Lineage Established",
        bool(
            engine.state.lineage_id
        ),
    )

    assert_true(
        "Payload Hash Established",
        len(
            engine.payload_hash
        ) == 64,
    )


# ============================================================================
# R28 UNIT N.33 TEST 2
# WAL VALIDATION
# ============================================================================

def test_02_wal_validation() -> None:

    test_header(
        2,
        "WAL VALIDATION",
    )

    engine = build_test_engine()

    engine.append_wal(
        "SECOND"
    )

    engine.validate_wal()

    assert_true(
        "WAL Contains Two Records",
        len(
            engine.state.wal
        ) == 2,
    )

    assert_true(
        "WAL Final Hash Established",
        len(
            engine.state.wal[-1].record_hash
        ) == 64,
    )


# ============================================================================
# R28 UNIT N.33 TEST 3
# CHECKPOINT CREATION
# ============================================================================

def test_03_checkpoint_creation() -> None:

    test_header(
        3,
        "CHECKPOINT CREATION",
    )

    engine = build_test_engine()

    checkpoint = (
        engine.create_checkpoint(
            "A"
        )
    )

    engine._validate_checkpoint(
        checkpoint
    )

    assert_true(
        "Checkpoint Stored In Slot A",
        "A"
        in engine.state.checkpoints,
    )

    assert_true(
        "Checkpoint WAL Length Bound",
        checkpoint.wal_length
        == len(
            engine.state.wal
        ),
    )


# ============================================================================
# R28 UNIT N.33 TEST 4
# CHECKPOINT TAMPER REJECTION
# ============================================================================

def test_04_checkpoint_tamper_rejection() -> None:

    test_header(
        4,
        "CHECKPOINT TAMPER REJECTION",
    )

    engine = build_test_engine()

    checkpoint = (
        engine.create_checkpoint(
            "A"
        )
    )

    tampered = copy.deepcopy(
        checkpoint
    )

    tampered.sequence += 1

    expect_local_block(
        "Tampered Checkpoint Rejected",

        lambda:
            engine._validate_checkpoint(
                tampered
            ),

        "checkpoint integrity seal mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 5
# INITIAL MANIFEST PROMOTION
# ============================================================================

def test_05_initial_manifest_promotion() -> None:

    test_header(
        5,
        "INITIAL MANIFEST PROMOTION",
    )

    engine = build_test_engine()

    checkpoint = (
        engine.create_checkpoint(
            "A"
        )
    )

    intent = (
        engine.prepare_promotion(
            "A"
        )
    )

    manifest = (
        engine.commit_promotion(
            intent
        )
    )

    assert_true(
        "Committed Manifest Points To Checkpoint",

        manifest.checkpoint_id
        == checkpoint.checkpoint_id,
    )

    assert_true(
        "Manifest Sequence Is One",

        engine.state.manifest_sequence
        == 1,
    )

    assert_true(
        "Promotion Removed From Pending Set",

        intent.promotion_id
        not in engine.state.pending_promotions,
    )

    assert_true(
        "Promotion Added To Finalized Fence",

        intent.promotion_id
        in engine.state.finalized_promotion_ids,
    )


# ============================================================================
# R28 UNIT N.33 TEST 6
# MANIFEST INTEGRITY
# ============================================================================

def test_06_manifest_integrity() -> None:

    test_header(
        6,
        "MANIFEST INTEGRITY",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    engine.validate_durable_state()

    assert_true(
        "Committed Manifest Present",

        engine.state.committed_manifest
        is not None,
    )


# ============================================================================
# R28 UNIT N.33 TEST 7
# MANIFEST TAMPER REJECTION
# ============================================================================

def test_07_manifest_tamper_rejection() -> None:

    test_header(
        7,
        "MANIFEST TAMPER REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    tampered = copy.deepcopy(
        engine.state.committed_manifest
    )

    assert tampered is not None

    tampered.manifest_sequence += 1

    expect_local_block(
        "Tampered Committed Manifest Rejected",

        lambda:
            engine._validate_manifest(
                tampered
            ),

        "committed manifest integrity seal mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 8
# NEWER CHECKPOINT PROMOTION
# ============================================================================

def test_08_newer_checkpoint_promotion() -> None:

    test_header(
        8,
        "NEWER CHECKPOINT PROMOTION",
    )

    engine = build_test_engine()

    first = prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    second = engine.commit_promotion(
        intent
    )

    assert_true(
        "Promotion Advances Checkpoint Sequence",

        second.checkpoint_sequence
        > first.checkpoint_sequence,
    )

    assert_true(
        "Manifest Sequence Advances Monotonically",

        second.manifest_sequence
        == first.manifest_sequence + 1,
    )


# ============================================================================
# R28 UNIT N.33 TEST 9
# PENDING PROMOTION SURVIVES RESTART
# ============================================================================

def test_09_pending_promotion_survives_restart() -> None:

    test_header(
        9,
        "PENDING PROMOTION SURVIVES RESTART",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    restarted = N33Engine.restore_state(
        engine.snapshot()
    )

    assert_true(
        "Pending Promotion Intent Survives Restart",

        intent.promotion_id
        in restarted.state.pending_promotions,
    )


# ============================================================================
# R28 UNIT N.33 TEST 10
# PENDING PROMOTION COMMITS AFTER RESTART
# ============================================================================

def test_10_pending_promotion_commits_after_restart() -> None:

    test_header(
        10,
        "PENDING PROMOTION COMMITS AFTER RESTART",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    restarted = N33Engine.restore_state(
        engine.snapshot()
    )

    manifests = (
        restarted.recover_pending_promotions()
    )

    assert_true(
        "Exactly One Pending Promotion Recovered",

        len(
            manifests
        ) == 1,
    )

    assert_true(
        "Recovered Promotion Finalized",

        intent.promotion_id
        in restarted.state.finalized_promotion_ids,
    )


# ============================================================================
# R28 UNIT N.33 TEST 11
# PROMOTION INTEGRITY TAMPER REJECTION
# ============================================================================

def test_11_promotion_integrity_tamper_rejection() -> None:

    test_header(
        11,
        "PROMOTION INTEGRITY TAMPER REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    tampered = copy.deepcopy(
        intent
    )

    tampered.checkpoint_sequence += 1

    expect_local_block(
        "Tampered Promotion Intent Rejected",

        lambda:
            engine.commit_promotion(
                tampered
            ),

        "promotion intent integrity seal mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 12
# PROMOTION CHECKPOINT IDENTITY REJECTION
# ============================================================================

def test_12_promotion_checkpoint_identity_rejection() -> None:

    test_header(
        12,
        "PROMOTION CHECKPOINT IDENTITY REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    durable = (
        engine.state.pending_promotions[
            intent.promotion_id
        ]
    )

    durable.checkpoint_id = new_id(
        "forged-checkpoint"
    )

    durable.seal()

    intent = copy.deepcopy(
        durable
    )

    expect_local_block(
        "Wrong Promotion Checkpoint Identity Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion checkpoint identity mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 13
# PROMOTION CHECKPOINT SEQUENCE REJECTION
# ============================================================================

def test_13_promotion_checkpoint_sequence_rejection() -> None:

    test_header(
        13,
        "PROMOTION CHECKPOINT SEQUENCE REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    durable = (
        engine.state.pending_promotions[
            intent.promotion_id
        ]
    )

    durable.checkpoint_sequence += 1

    durable.seal()

    intent = copy.deepcopy(
        durable
    )

    expect_local_block(
        "Wrong Promotion Checkpoint Sequence Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion checkpoint sequence mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 14
# PROMOTION MANIFEST SEQUENCE REJECTION
# ============================================================================

def test_14_promotion_manifest_sequence_rejection() -> None:

    test_header(
        14,
        "PROMOTION MANIFEST SEQUENCE REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    durable = (
        engine.state.pending_promotions[
            intent.promotion_id
        ]
    )

    durable.expected_manifest_sequence += 1

    durable.seal()

    intent = copy.deepcopy(
        durable
    )

    expect_local_block(
        "Wrong Promotion Manifest Sequence Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion manifest sequence mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 15
# PROMOTION PAYLOAD HASH REJECTION
# ============================================================================

def test_15_promotion_payload_hash_rejection() -> None:

    test_header(
        15,
        "PROMOTION PAYLOAD HASH REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    durable = (
        engine.state.pending_promotions[
            intent.promotion_id
        ]
    )

    durable.payload_hash = "f" * 64

    durable.seal()

    intent = copy.deepcopy(
        durable
    )

    expect_local_block(
        "Wrong Promotion Payload Hash Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion intent payload hash mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 16
# PROMOTION RECOVERY EPOCH REJECTION
# ============================================================================

def test_16_promotion_recovery_epoch_rejection() -> None:

    test_header(
        16,
        "PROMOTION RECOVERY EPOCH REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    durable = (
        engine.state.pending_promotions[
            intent.promotion_id
        ]
    )

    durable.recovery_epoch += 1

    durable.seal()

    intent = copy.deepcopy(
        durable
    )

    expect_local_block(
        "Wrong Promotion Recovery Epoch Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion intent recovery epoch mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 17
# MISSING PENDING PROMOTION REJECTION
# ============================================================================

def test_17_missing_pending_promotion_rejection() -> None:

    test_header(
        17,
        "MISSING PENDING PROMOTION REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    engine.state.pending_promotions.pop(
        intent.promotion_id
    )

    expect_local_block(
        "Missing Pending Promotion Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "pending promotion missing",
    )


# ============================================================================
# R28 UNIT N.33 TEST 18
# STALE PROMOTION GENERATION REJECTION
# ============================================================================

def test_18_stale_promotion_generation_rejection() -> None:

    test_header(
        18,
        "STALE PROMOTION GENERATION REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    durable = (
        engine.state.pending_promotions[
            intent.promotion_id
        ]
    )

    durable.generation -= 1

    durable.seal()

    intent = copy.deepcopy(
        durable
    )

    expect_local_block(
        "Wrong Generation Promotion Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion intent generation mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 19
# STALE PROMOTION LINEAGE REJECTION
# ============================================================================

def test_19_stale_promotion_lineage_rejection() -> None:

    test_header(
        19,
        "STALE PROMOTION LINEAGE REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    durable = (
        engine.state.pending_promotions[
            intent.promotion_id
        ]
    )

    durable.lineage_id = new_id(
        "stale-lineage"
    )

    durable.seal()

    intent = copy.deepcopy(
        durable
    )

    expect_local_block(
        "Wrong Lineage Promotion Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion intent lineage mismatch",
    )


# ============================================================================
# R28 UNIT N.33 TEST 20
# FINALIZED PROMOTION SURVIVES RESTART
# ============================================================================

def test_20_finalized_promotion_survives_restart() -> None:

    test_header(
        20,
        "FINALIZED PROMOTION SURVIVES RESTART",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    engine.commit_promotion(
        intent
    )

    restarted = N33Engine.restore_state(
        engine.snapshot()
    )

    assert_true(
        "Finalized Promotion Fence Survives Restart",

        intent.promotion_id
        in restarted.state.finalized_promotion_ids,
    )

    assert_true(
        "Finalized Promotion Is Not Pending After Restart",

        intent.promotion_id
        not in restarted.state.pending_promotions,
    )


# ============================================================================
# R28 UNIT N.33 TEST 21
# FINALIZED AUTHORITY SURVIVES RESTART
# ============================================================================

def test_21_finalized_authority_survives_restart() -> None:

    test_header(
        21,
        "FINALIZED AUTHORITY SURVIVES RESTART",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    manifest = engine.commit_promotion(
        intent
    )

    restarted = N33Engine.restore_state(
        engine.snapshot()
    )

    recovered = (
        restarted.state.committed_manifest
    )

    assert_true(
        "Committed Manifest Survives Restart",

        recovered is not None,
    )

    assert_true(
        "Committed Authority Sequence Preserved",

        recovered is not None
        and
        recovered.manifest_sequence
        == manifest.manifest_sequence,
    )

    assert_true(
        "Committed Authority Checkpoint Preserved",

        recovered is not None
        and
        recovered.checkpoint_id
        == manifest.checkpoint_id,
    )


# ============================================================================
# R28 UNIT N.33 TEST 22
# FINALIZED PROMOTION REPLAY REJECTION
#
# CORRECTED:
#   Expected LocalBlock:
#       "promotion intent already finalized"
#
# NOT:
#       "pending promotion missing"
# ============================================================================

def test_22_promotion_replay_rejection() -> None:

    test_header(
        22,
        "FINALIZED PROMOTION REPLAY REJECTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    promotion_intent = (
        prepare_valid_promotion(
            engine
        )
    )

    engine.commit_promotion(
        promotion_intent
    )

    expect_local_block(
        "Finalized Promotion Replay Rejected",

        lambda:
            engine.commit_promotion(
                promotion_intent
            ),

        "promotion intent already finalized",
    )


# ============================================================================
# R28 UNIT N.33 TEST 23
# FINALIZED PROMOTION REPLAY REJECTION AFTER RESTART
# ============================================================================

def test_23_finalized_replay_rejected_after_restart() -> None:

    test_header(
        23,
        "FINALIZED PROMOTION REPLAY REJECTION AFTER RESTART",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    engine.commit_promotion(
        intent
    )

    restarted = N33Engine.restore_state(
        engine.snapshot()
    )

    expect_local_block(
        "Restarted Finalized Promotion Replay Rejected",

        lambda:
            restarted.commit_promotion(
                intent
            ),

        "promotion intent already finalized",
    )


# ============================================================================
# R28 UNIT N.33 TEST 24
# SYNTHETIC TRANSPORT FIREBREAK
# ============================================================================

def test_24_synthetic_transport_firebreak() -> None:

    test_header(
        24,
        "SYNTHETIC TRANSPORT FIREBREAK",
    )

    engine = build_test_engine()

    receipt = engine.synthetic_dispatch()

    assert_true(
        "Dispatch Is Synthetic",
        receipt.synthetic,
    )

    assert_true(
        "No Network Transmission Occurred",

        receipt.network_transmitted
        is False,
    )

    assert_true(
        "Transport Method Exactly POST",

        receipt.method
        == "POST",
    )

    assert_true(
        "Transport Path Exactly Leverage Endpoint",

        receipt.path
        == LEVERAGE_ENDPOINT,
    )

    assert_true(
        "Transport Payload Hash Preserved",

        receipt.payload_hash
        == engine.payload_hash,
    )


# ============================================================================
# R28 UNIT N.33 TEST 25
# GENERATION / LINEAGE ADVANCE
# ============================================================================

def test_25_generation_advance() -> None:

    test_header(
        25,
        "GENERATION / LINEAGE ADVANCE",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    old_generation = (
        engine.state.generation
    )

    old_lineage = (
        engine.state.lineage_id
    )

    old_epoch = (
        engine.state.recovery_epoch
    )

    engine.advance_generation()

    assert_true(
        "Generation Advanced Monotonically",

        engine.state.generation
        == old_generation + 1,
    )

    assert_true(
        "Lineage Changed On Generation Advance",

        engine.state.lineage_id
        != old_lineage,
    )

    assert_true(
        "Recovery Epoch Advanced Monotonically",

        engine.state.recovery_epoch
        == old_epoch + 1,
    )


# ============================================================================
# R28 UNIT N.33 TEST 26
# GENERATION ADVANCE BLOCKED BY PENDING PROMOTION
# ============================================================================

def test_26_generation_advance_blocked_by_pending_promotion() -> None:

    test_header(
        26,
        "GENERATION ADVANCE BLOCKED BY PENDING PROMOTION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    prepare_valid_promotion(
        engine
    )

    expect_local_block(
        "Generation Advance With Pending Promotion Rejected",

        engine.advance_generation,

        "cannot advance generation with pending promotion",
    )


# ============================================================================
# R28 UNIT N.33 TEST 27
# FINALIZED FENCE SURVIVES GENERATION ADVANCE
# ============================================================================

def test_27_finalized_fence_survives_generation_advance() -> None:

    test_header(
        27,
        "FINALIZED FENCE SURVIVES GENERATION ADVANCE",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    engine.commit_promotion(
        intent
    )

    engine.advance_generation()

    assert_true(
        "Finalized Promotion ID Preserved Across Generation",

        intent.promotion_id
        in engine.state.finalized_promotion_ids,
    )


# ============================================================================
# R28 UNIT N.33 TEST 28
# OLD FINALIZED INTENT REPLAY AFTER GENERATION ADVANCE
# ============================================================================

def test_28_old_finalized_intent_replay_after_generation_advance() -> None:

    test_header(
        28,
        "OLD FINALIZED INTENT REPLAY AFTER GENERATION ADVANCE",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    engine.commit_promotion(
        intent
    )

    engine.advance_generation()

    expect_local_block(
        "Old Finalized Promotion Replay Still Rejected",

        lambda:
            engine.commit_promotion(
                intent
            ),

        "promotion intent already finalized",
    )


# ============================================================================
# R28 UNIT N.33 TEST 29
# FULL DURABLE STATE VALIDATION
# ============================================================================

def test_29_durable_state_validation() -> None:

    test_header(
        29,
        "FULL DURABLE STATE VALIDATION",
    )

    engine = build_test_engine()

    prepare_initial_authority(
        engine
    )

    intent = prepare_valid_promotion(
        engine
    )

    engine.commit_promotion(
        intent
    )

    engine.validate_durable_state()

    pass_line(
        "Complete Durable State Validates"
    )


# ============================================================================
# R28 UNIT N.33 TEST 30
# FINAL NETWORK WRITE POLICY
# ============================================================================

def test_30_network_write_policy() -> None:

    test_header(
        30,
        "FINAL NETWORK WRITE POLICY",
    )

    assert_true(
        "Real POST Disabled",
        REAL_POST_ENABLED is False,
    )

    assert_true(
        "Demo POST Disabled",
        DEMO_POST_ENABLED is False,
    )

    assert_true(
        "All Network Writes Disabled",
        NETWORK_WRITES_ENABLED is False,
    )

    assert_true(
        "Synthetic Transport Only",
        SYNTHETIC_TRANSPORT_ONLY is True,
    )


# ============================================================================
# DIAGNOSTIC RUNNER
# ============================================================================

def run_all_diagnostics() -> None:

    print(
        "",
        flush=True,
    )

    separator()

    print(
        f"{UNIT_NAME}: STARTING DIAGNOSTICS",
        flush=True,
    )

    separator()

    tests = [
        test_01_initial_state,
        test_02_wal_validation,
        test_03_checkpoint_creation,
        test_04_checkpoint_tamper_rejection,
        test_05_initial_manifest_promotion,
        test_06_manifest_integrity,
        test_07_manifest_tamper_rejection,
        test_08_newer_checkpoint_promotion,
        test_09_pending_promotion_survives_restart,
        test_10_pending_promotion_commits_after_restart,
        test_11_promotion_integrity_tamper_rejection,
        test_12_promotion_checkpoint_identity_rejection,
        test_13_promotion_checkpoint_sequence_rejection,
        test_14_promotion_manifest_sequence_rejection,
        test_15_promotion_payload_hash_rejection,
        test_16_promotion_recovery_epoch_rejection,
        test_17_missing_pending_promotion_rejection,
        test_18_stale_promotion_generation_rejection,
        test_19_stale_promotion_lineage_rejection,
        test_20_finalized_promotion_survives_restart,
        test_21_finalized_authority_survives_restart,
        test_22_promotion_replay_rejection,
        test_23_finalized_replay_rejected_after_restart,
        test_24_synthetic_transport_firebreak,
        test_25_generation_advance,
        test_26_generation_advance_blocked_by_pending_promotion,
        test_27_finalized_fence_survives_generation_advance,
        test_28_old_finalized_intent_replay_after_generation_advance,
        test_29_durable_state_validation,
        test_30_network_write_policy,
    ]

    for test in tests:
        test()

    print(
        "",
        flush=True,
    )

    separator()

    print(
        f"{UNIT_NAME}: ALL DIAGNOSTICS PASSED",
        flush=True,
    )

    separator()

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
        "",
        flush=True,
    )


# ============================================================================
# OPTIONAL HEALTH SERVER
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:

        if self.path in (
            "/",
            "/health",
            "/healthz",
        ):

            body = json.dumps(
                {
                    "unit":
                        UNIT_NAME,

                    "version":
                        UNIT_VERSION,

                    "status":
                        "ok",

                    "real_post":
                        REAL_POST_ENABLED,

                    "demo_post":
                        DEMO_POST_ENABLED,

                    "network_writes":
                        NETWORK_WRITES_ENABLED,

                    "synthetic_only":
                        SYNTHETIC_TRANSPORT_ONLY,
                },
                sort_keys=True,
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

            return

        self.send_response(
            404
        )

        self.end_headers()


    def log_message(
        self,
        fmt: str,
        *args: Any,
    ) -> None:

        return


# ============================================================================
# HEALTH SERVER STARTUP
# ============================================================================

def start_health_server() -> None:

    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )

    def runner() -> None:

        try:

            server = HTTPServer(
                (
                    "0.0.0.0",
                    port,
                ),
                HealthHandler,
            )

            print(
                (
                    f"{UNIT_NAME}: "
                    f"HEALTH SERVER LISTENING "
                    f"ON PORT {port}"
                ),
                flush=True,
            )

            server.serve_forever()

        except Exception as exc:

            print(
                (
                    f"{UNIT_NAME}: "
                    f"HEALTH SERVER ERROR: "
                    f"{exc}"
                ),
                flush=True,
            )

    thread = threading.Thread(
        target=runner,
        daemon=True,
        name="n33-health-server",
    )

    thread.start()


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:

    run_all_diagnostics()

    start_health_server()

    heartbeat = 0

    while True:

        heartbeat += 1

        print(
            (
                f"{UNIT_NAME}: "
                f"HEARTBEAT {heartbeat} "
                f"| synthetic-only="
                f"{SYNTHETIC_TRANSPORT_ONLY} "
                f"| network-writes="
                f"{NETWORK_WRITES_ENABLED}"
            ),
            flush=True,
        )

        time.sleep(
            30
        )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
