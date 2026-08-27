#!/usr/bin/env python3

# =============================================================================
# R29 UNIT A
# INTEGRATED RUNTIME BASELINE
#
# PURPOSE
# -------
# Establish the first integrated runtime baseline after completion of the
# R28 synthetic durability/recovery validation sequence.
#
# THIS UNIT DOES NOT:
#   - place real orders
#   - place demo orders
#   - perform exchange POST requests
#   - perform exchange PUT requests
#   - perform exchange PATCH requests
#   - perform exchange DELETE requests
#   - mutate leverage
#   - mutate margin mode
#   - mutate positions
#   - mutate account state
#
# SAFETY POSTURE
# --------------
# REAL_ORDER_EXECUTION      = False
# DEMO_ORDER_EXECUTION      = False
# NETWORK_WRITES_ENABLED    = False
# SYNTHETIC_TRANSPORT_ONLY  = True
#
# R29 UNIT A validates:
#   1. Runtime boot
#   2. Configuration loading
#   3. Strategy/risk envelope
#   4. Runtime fingerprint
#   5. Durable baseline state
#   6. Atomic persistence
#   7. Restart restore
#   8. Integrity seal verification
#   9. Write firebreak
#  10. Synthetic transport
#  11. No accidental exchange mutation
#  12. Runtime generation continuity
#  13. Recovery epoch continuity
#  14. Safety invariants
#  15. Health server configuration
#  16. Final integrated baseline validation
#
# =============================================================================

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import os
import signal
import sys
import tempfile
import threading
import time
import traceback
import uuid

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# R29 UNIT A: MAIN.PY ENTERED
# =============================================================================

print("R29 UNIT A: MAIN.PY ENTERED", flush=True)


# =============================================================================
# CONSTANTS
# =============================================================================

UNIT_NAME = "R29 UNIT A"
UNIT_DESCRIPTION = "INTEGRATED RUNTIME BASELINE"

SEPARATOR = "-" * 92

DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_DEMO_SYMBOL = "BTCSUSDT"

DEFAULT_MARGIN_TYPE = "ISOLATED"
DEFAULT_POSITION_MODE = "COMBINED"

DEFAULT_PLANNED_LEVERAGE = 100

DEFAULT_INITIAL_ENTRY_PERCENT = 5.0
DEFAULT_PYRAMID_SIZE_PERCENT = 5.0
DEFAULT_MAX_PYRAMID_ADDS = 1

DEFAULT_BACKUP_SIZE_PERCENT = 5.0
DEFAULT_MAX_BACKUPS = 3
DEFAULT_BACKUP_BUFFER_PERCENT = 0.3

DEFAULT_MAX_FUND_EXPOSURE_PERCENT = 35.0

DEFAULT_TP1_PERCENT = 20.0
DEFAULT_TP2_PERCENT = 20.0
DEFAULT_TP3_PERCENT = 60.0

DEFAULT_TP1_TRIGGER_PERCENT = 0.5
DEFAULT_TP2_TRIGGER_PERCENT = 1.0
DEFAULT_TRAILING_DISTANCE_PERCENT = 0.20

DEFAULT_SIGNAL_EXPIRY_SECONDS = 120
DEFAULT_LOSS_COOLDOWN_SECONDS = 300

DEFAULT_HEALTH_PORT = 10000
DEFAULT_HEARTBEAT_SECONDS = 30

STATE_SCHEMA_VERSION = 1
CONFIG_SCHEMA_VERSION = 1

STATE_FILE_NAME = "r29_unit_a_state.json"

REAL_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False
NETWORK_WRITES_ENABLED = False
SYNTHETIC_TRANSPORT_ONLY = True

ALLOW_HTTP_POST = False
ALLOW_HTTP_PUT = False
ALLOW_HTTP_PATCH = False
ALLOW_HTTP_DELETE = False

ALLOW_WEBSOCKET_WRITES = False

ALLOW_LEVERAGE_MUTATION = False
ALLOW_MARGIN_MUTATION = False
ALLOW_POSITION_MUTATION = False
ALLOW_ACCOUNT_MUTATION = False

ALLOW_REAL_EXCHANGE_MUTATION = False
ALLOW_DEMO_EXCHANGE_MUTATION = False

HEALTH_SERVER_ENABLED = True


print("R29 UNIT A: IMPORTS COMPLETE", flush=True)
print("R29 UNIT A: CONSTANTS INITIALIZED", flush=True)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class R29Error(Exception):
    """Base exception for R29 Unit A."""


class ValidationError(R29Error):
    """Raised when an invariant fails."""


class IntegrityError(R29Error):
    """Raised when durable state integrity validation fails."""


class NetworkWriteBlocked(R29Error):
    """Raised whenever code attempts a network mutation."""


class SyntheticTransportError(R29Error):
    """Raised when synthetic transport validation fails."""


# =============================================================================
# BASIC HELPERS
# =============================================================================


def utc_timestamp() -> float:
    return time.time()


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)

    if raw is None:
        return default

    value = raw.strip().lower()

    if value in ("1", "true", "yes", "y", "on"):
        return True

    if value in ("0", "false", "no", "n", "off"):
        return False

    raise ValidationError(
        f"invalid boolean environment value for {name}: {raw!r}"
    )


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name)

    if raw is None:
        return default

    try:
        return int(raw)
    except ValueError as exc:
        raise ValidationError(
            f"invalid integer environment value for {name}: {raw!r}"
        ) from exc


def env_float(name: str, default: float) -> float:
    raw = os.getenv(name)

    if raw is None:
        return default

    try:
        return float(raw)
    except ValueError as exc:
        raise ValidationError(
            f"invalid float environment value for {name}: {raw!r}"
        ) from exc


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def print_header(title: str) -> None:
    print(SEPARATOR, flush=True)
    print(title, flush=True)
    print(SEPARATOR, flush=True)


def print_pass(label: str) -> None:
    print(f"{label:<82} ✅ PASS", flush=True)


def print_local_block(message: str) -> None:
    print(f"{UNIT_NAME} LOCAL BLOCK:", flush=True)
    print(f"  {message}", flush=True)


# =============================================================================
# CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class RuntimeConfig:
    config_schema_version: int

    symbol: str
    demo_symbol: str

    margin_type: str
    position_mode: str

    planned_leverage: int

    initial_entry_percent: float

    pyramid_size_percent: float
    max_pyramid_adds: int

    backup_size_percent: float
    max_backups: int
    backup_buffer_percent: float

    max_fund_exposure_percent: float

    tp1_percent: float
    tp2_percent: float
    tp3_percent: float

    tp1_trigger_percent: float
    tp2_trigger_percent: float
    trailing_distance_percent: float

    signal_expiry_seconds: int
    loss_cooldown_seconds: int

    one_direction_only: bool
    anti_duplicate_orders: bool
    trend_reversal_exit: bool
    idle_pyramid_cleanup: bool

    health_port: int
    heartbeat_seconds: int

    real_order_execution: bool
    demo_order_execution: bool
    network_writes_enabled: bool
    synthetic_transport_only: bool

    allow_http_post: bool
    allow_http_put: bool
    allow_http_patch: bool
    allow_http_delete: bool

    allow_websocket_writes: bool

    allow_leverage_mutation: bool
    allow_margin_mutation: bool
    allow_position_mutation: bool
    allow_account_mutation: bool

    allow_real_exchange_mutation: bool
    allow_demo_exchange_mutation: bool

    @classmethod
    def load(cls) -> "RuntimeConfig":
        return cls(
            config_schema_version=CONFIG_SCHEMA_VERSION,

            symbol=os.getenv(
                "SYMBOL",
                DEFAULT_SYMBOL,
            ).strip().upper(),

            demo_symbol=os.getenv(
                "DEMO_SYMBOL",
                DEFAULT_DEMO_SYMBOL,
            ).strip().upper(),

            margin_type=os.getenv(
                "MARGIN_TYPE",
                DEFAULT_MARGIN_TYPE,
            ).strip().upper(),

            position_mode=os.getenv(
                "POSITION_MODE",
                DEFAULT_POSITION_MODE,
            ).strip().upper(),

            planned_leverage=env_int(
                "PLANNED_LEVERAGE",
                DEFAULT_PLANNED_LEVERAGE,
            ),

            initial_entry_percent=env_float(
                "INITIAL_ENTRY_PERCENT",
                DEFAULT_INITIAL_ENTRY_PERCENT,
            ),

            pyramid_size_percent=env_float(
                "PYRAMID_SIZE_PERCENT",
                DEFAULT_PYRAMID_SIZE_PERCENT,
            ),

            max_pyramid_adds=env_int(
                "MAX_PYRAMID_ADDS",
                DEFAULT_MAX_PYRAMID_ADDS,
            ),

            backup_size_percent=env_float(
                "BACKUP_SIZE_PERCENT",
                DEFAULT_BACKUP_SIZE_PERCENT,
            ),

            max_backups=env_int(
                "MAX_BACKUPS",
                DEFAULT_MAX_BACKUPS,
            ),

            backup_buffer_percent=env_float(
                "BACKUP_BUFFER_PERCENT",
                DEFAULT_BACKUP_BUFFER_PERCENT,
            ),

            max_fund_exposure_percent=env_float(
                "MAX_FUND_EXPOSURE_PERCENT",
                DEFAULT_MAX_FUND_EXPOSURE_PERCENT,
            ),

            tp1_percent=env_float(
                "TP1_PERCENT",
                DEFAULT_TP1_PERCENT,
            ),

            tp2_percent=env_float(
                "TP2_PERCENT",
                DEFAULT_TP2_PERCENT,
            ),

            tp3_percent=env_float(
                "TP3_PERCENT",
                DEFAULT_TP3_PERCENT,
            ),

            tp1_trigger_percent=env_float(
                "TP1_TRIGGER_PERCENT",
                DEFAULT_TP1_TRIGGER_PERCENT,
            ),

            tp2_trigger_percent=env_float(
                "TP2_TRIGGER_PERCENT",
                DEFAULT_TP2_TRIGGER_PERCENT,
            ),

            trailing_distance_percent=env_float(
                "TRAILING_DISTANCE_PERCENT",
                DEFAULT_TRAILING_DISTANCE_PERCENT,
            ),

            signal_expiry_seconds=env_int(
                "SIGNAL_EXPIRY_SECONDS",
                DEFAULT_SIGNAL_EXPIRY_SECONDS,
            ),

            loss_cooldown_seconds=env_int(
                "LOSS_COOLDOWN_SECONDS",
                DEFAULT_LOSS_COOLDOWN_SECONDS,
            ),

            one_direction_only=env_bool(
                "ONE_DIRECTION_ONLY",
                True,
            ),

            anti_duplicate_orders=env_bool(
                "ANTI_DUPLICATE_ORDERS",
                True,
            ),

            trend_reversal_exit=env_bool(
                "TREND_REVERSAL_EXIT",
                True,
            ),

            idle_pyramid_cleanup=env_bool(
                "IDLE_PYRAMID_CLEANUP",
                True,
            ),

            health_port=env_int(
                "PORT",
                DEFAULT_HEALTH_PORT,
            ),

            heartbeat_seconds=env_int(
                "HEARTBEAT_SECONDS",
                DEFAULT_HEARTBEAT_SECONDS,
            ),

            # -----------------------------------------------------------------
            # These are intentionally fixed safety values.
            # Environment variables CANNOT activate writes in R29 Unit A.
            # -----------------------------------------------------------------

            real_order_execution=REAL_ORDER_EXECUTION,
            demo_order_execution=DEMO_ORDER_EXECUTION,
            network_writes_enabled=NETWORK_WRITES_ENABLED,
            synthetic_transport_only=SYNTHETIC_TRANSPORT_ONLY,

            allow_http_post=ALLOW_HTTP_POST,
            allow_http_put=ALLOW_HTTP_PUT,
            allow_http_patch=ALLOW_HTTP_PATCH,
            allow_http_delete=ALLOW_HTTP_DELETE,

            allow_websocket_writes=ALLOW_WEBSOCKET_WRITES,

            allow_leverage_mutation=ALLOW_LEVERAGE_MUTATION,
            allow_margin_mutation=ALLOW_MARGIN_MUTATION,
            allow_position_mutation=ALLOW_POSITION_MUTATION,
            allow_account_mutation=ALLOW_ACCOUNT_MUTATION,

            allow_real_exchange_mutation=ALLOW_REAL_EXCHANGE_MUTATION,
            allow_demo_exchange_mutation=ALLOW_DEMO_EXCHANGE_MUTATION,
        )

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    def fingerprint_payload(self) -> Dict[str, Any]:
        return self.to_dict()

    def fingerprint(self) -> str:
        return sha256_object(self.fingerprint_payload())


# =============================================================================
# CONFIG VALIDATION
# =============================================================================


def validate_config(config: RuntimeConfig) -> None:
    require(
        bool(config.symbol),
        "symbol missing",
    )

    require(
        config.margin_type == "ISOLATED",
        "R29 Unit A requires ISOLATED planned margin type",
    )

    require(
        config.position_mode in ("COMBINED", "HEDGE", "ONE_WAY"),
        "unsupported planned position mode",
    )

    require(
        1 <= config.planned_leverage <= 100,
        "planned leverage exceeds R29 local safety envelope",
    )

    require(
        0 < config.initial_entry_percent <= 5.0,
        "initial entry percentage exceeds R29 baseline limit",
    )

    require(
        0 <= config.pyramid_size_percent <= 5.0,
        "pyramid size exceeds R29 baseline limit",
    )

    require(
        0 <= config.max_pyramid_adds <= 1,
        "too many pyramid additions",
    )

    require(
        0 <= config.backup_size_percent <= 5.0,
        "backup size exceeds R29 baseline limit",
    )

    require(
        0 <= config.max_backups <= 3,
        "too many backup entries",
    )

    require(
        0 <= config.backup_buffer_percent <= 5.0,
        "invalid backup buffer",
    )

    require(
        0 < config.max_fund_exposure_percent <= 35.0,
        "fund exposure exceeds configured hard baseline",
    )

    tp_total = (
        config.tp1_percent
        + config.tp2_percent
        + config.tp3_percent
    )

    require(
        abs(tp_total - 100.0) < 1e-9,
        "TP allocation does not total 100 percent",
    )

    require(
        config.tp1_trigger_percent > 0,
        "invalid TP1 trigger",
    )

    require(
        config.tp2_trigger_percent >
        config.tp1_trigger_percent,
        "TP2 trigger must exceed TP1 trigger",
    )

    require(
        config.trailing_distance_percent > 0,
        "invalid trailing distance",
    )

    require(
        config.signal_expiry_seconds > 0,
        "signal expiry must be positive",
    )

    require(
        config.loss_cooldown_seconds >= 0,
        "loss cooldown cannot be negative",
    )

    require(
        1 <= config.health_port <= 65535,
        "invalid health server port",
    )

    require(
        config.heartbeat_seconds >= 1,
        "heartbeat interval must be at least one second",
    )

    # -------------------------------------------------------------------------
    # Absolute Unit A safety invariants
    # -------------------------------------------------------------------------

    require(
        config.real_order_execution is False,
        "real order execution must remain disabled",
    )

    require(
        config.demo_order_execution is False,
        "demo order execution must remain disabled",
    )

    require(
        config.network_writes_enabled is False,
        "network writes must remain disabled",
    )

    require(
        config.synthetic_transport_only is True,
        "synthetic transport must remain enabled",
    )

    require(
        config.allow_http_post is False,
        "HTTP POST must remain disabled",
    )

    require(
        config.allow_http_put is False,
        "HTTP PUT must remain disabled",
    )

    require(
        config.allow_http_patch is False,
        "HTTP PATCH must remain disabled",
    )

    require(
        config.allow_http_delete is False,
        "HTTP DELETE must remain disabled",
    )

    require(
        config.allow_websocket_writes is False,
        "WebSocket writes must remain disabled",
    )

    require(
        config.allow_leverage_mutation is False,
        "leverage mutation must remain disabled",
    )

    require(
        config.allow_margin_mutation is False,
        "margin mutation must remain disabled",
    )

    require(
        config.allow_position_mutation is False,
        "position mutation must remain disabled",
    )

    require(
        config.allow_account_mutation is False,
        "account mutation must remain disabled",
    )

    require(
        config.allow_real_exchange_mutation is False,
        "real exchange mutation must remain disabled",
    )

    require(
        config.allow_demo_exchange_mutation is False,
        "demo exchange mutation must remain disabled",
    )


# =============================================================================
# DURABLE STATE
# =============================================================================


@dataclass
class DurableRuntimeState:
    schema_version: int

    runtime_id: str
    generation: int
    recovery_epoch: int

    boot_count: int

    created_at: float
    last_boot_at: float
    last_persisted_at: float

    config_fingerprint: str

    phase: str

    synthetic_dispatch_count: int

    real_network_write_attempts: int
    demo_network_write_attempts: int
    blocked_network_write_attempts: int

    real_orders_sent: int
    demo_orders_sent: int

    last_event_sequence: int

    historical_runtime_fingerprints: List[str] = field(
        default_factory=list
    )

    integrity_seal: str = ""

    def integrity_payload(self) -> Dict[str, Any]:
        payload = dataclasses.asdict(self)
        payload.pop("integrity_seal", None)
        return payload

    def compute_integrity_seal(self) -> str:
        return sha256_object(self.integrity_payload())

    def seal(self) -> None:
        self.integrity_seal = self.compute_integrity_seal()

    def validate_integrity(self) -> None:
        expected = self.compute_integrity_seal()

        if self.integrity_seal != expected:
            raise IntegrityError(
                "runtime state integrity seal mismatch"
            )

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(
        cls,
        payload: Dict[str, Any],
    ) -> "DurableRuntimeState":

        state = cls(
            schema_version=int(payload["schema_version"]),
            runtime_id=str(payload["runtime_id"]),
            generation=int(payload["generation"]),
            recovery_epoch=int(payload["recovery_epoch"]),
            boot_count=int(payload["boot_count"]),
            created_at=float(payload["created_at"]),
            last_boot_at=float(payload["last_boot_at"]),
            last_persisted_at=float(
                payload["last_persisted_at"]
            ),
            config_fingerprint=str(
                payload["config_fingerprint"]
            ),
            phase=str(payload["phase"]),
            synthetic_dispatch_count=int(
                payload["synthetic_dispatch_count"]
            ),
            real_network_write_attempts=int(
                payload["real_network_write_attempts"]
            ),
            demo_network_write_attempts=int(
                payload["demo_network_write_attempts"]
            ),
            blocked_network_write_attempts=int(
                payload["blocked_network_write_attempts"]
            ),
            real_orders_sent=int(
                payload["real_orders_sent"]
            ),
            demo_orders_sent=int(
                payload["demo_orders_sent"]
            ),
            last_event_sequence=int(
                payload["last_event_sequence"]
            ),
            historical_runtime_fingerprints=list(
                payload.get(
                    "historical_runtime_fingerprints",
                    [],
                )
            ),
            integrity_seal=str(
                payload["integrity_seal"]
            ),
        )

        return state


# =============================================================================
# STATE STORE
# =============================================================================


class AtomicStateStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def exists(self) -> bool:
        return self.path.exists()

    def save(
        self,
        state: DurableRuntimeState,
    ) -> None:

        state.last_persisted_at = utc_timestamp()
        state.seal()

        payload = state.to_dict()

        encoded = json.dumps(
            payload,
            sort_keys=True,
            indent=2,
        )

        temp_path: Optional[Path] = None

        try:
            fd, raw_temp_path = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=str(self.path.parent),
                text=True,
            )

            temp_path = Path(raw_temp_path)

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                handle.write(encoded)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())

            os.replace(
                temp_path,
                self.path,
            )

            try:
                dir_fd = os.open(
                    str(self.path.parent),
                    os.O_DIRECTORY,
                )

                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)

            except (
                AttributeError,
                OSError,
            ):
                # Directory fsync is not supported identically
                # on every environment. File replacement remains atomic.
                pass

        finally:
            if (
                temp_path is not None
                and temp_path.exists()
            ):
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    def load(self) -> DurableRuntimeState:
        if not self.path.exists():
            raise FileNotFoundError(
                str(self.path)
            )

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            payload = json.load(handle)

        state = DurableRuntimeState.from_dict(
            payload
        )

        state.validate_integrity()

        require(
            state.schema_version ==
            STATE_SCHEMA_VERSION,
            "runtime state schema mismatch",
        )

        return state


# =============================================================================
# NETWORK WRITE FIREBREAK
# =============================================================================


@dataclass
class WriteAttempt:
    method: str
    target: str
    environment: str
    payload_hash: str
    timestamp: float


class NetworkWriteFirebreak:
    MUTATING_METHODS = {
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    }

    def __init__(
        self,
        state: DurableRuntimeState,
    ):
        self.state = state
        self.blocked_attempts: List[
            WriteAttempt
        ] = []

    def guard_http(
        self,
        method: str,
        target: str,
        payload: Optional[
            Dict[str, Any]
        ] = None,
        environment: str = "REAL",
    ) -> None:

        method_upper = method.strip().upper()
        environment_upper = (
            environment.strip().upper()
        )

        if method_upper not in self.MUTATING_METHODS:
            return

        payload_hash = sha256_object(
            payload or {}
        )

        attempt = WriteAttempt(
            method=method_upper,
            target=target,
            environment=environment_upper,
            payload_hash=payload_hash,
            timestamp=utc_timestamp(),
        )

        self.blocked_attempts.append(
            attempt
        )

        self.state.blocked_network_write_attempts += 1

        if environment_upper == "REAL":
            self.state.real_network_write_attempts += 1

        elif environment_upper == "DEMO":
            self.state.demo_network_write_attempts += 1

        raise NetworkWriteBlocked(
            f"{environment_upper} network "
            f"{method_upper} blocked"
        )

    def guard_websocket_write(
        self,
        channel: str,
        payload: Dict[str, Any],
    ) -> None:

        payload_hash = sha256_object(
            payload
        )

        self.blocked_attempts.append(
            WriteAttempt(
                method="WEBSOCKET_WRITE",
                target=channel,
                environment="REAL",
                payload_hash=payload_hash,
                timestamp=utc_timestamp(),
            )
        )

        self.state.blocked_network_write_attempts += 1
        self.state.real_network_write_attempts += 1

        raise NetworkWriteBlocked(
            "WebSocket write blocked"
        )


# =============================================================================
# SYNTHETIC TRANSPORT
# =============================================================================


@dataclass(frozen=True)
class SyntheticEnvelope:
    envelope_id: str
    action: str
    symbol: str
    payload: Dict[str, Any]
    payload_hash: str
    config_fingerprint: str
    generation: int
    recovery_epoch: int
    event_sequence: int
    created_at: float


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    envelope_id: str
    accepted: bool
    transmitted: bool
    transport: str
    payload_hash: str
    generation: int
    recovery_epoch: int
    event_sequence: int
    created_at: float


class SyntheticTransport:
    def __init__(
        self,
        state: DurableRuntimeState,
        config: RuntimeConfig,
    ):
        self.state = state
        self.config = config
        self.receipts: List[
            SyntheticReceipt
        ] = []

    def dispatch(
        self,
        action: str,
        payload: Dict[str, Any],
    ) -> Tuple[
        SyntheticEnvelope,
        SyntheticReceipt,
    ]:

        require(
            self.config.synthetic_transport_only,
            "synthetic transport disabled",
        )

        require(
            not self.config.network_writes_enabled,
            "network writes unexpectedly enabled",
        )

        self.state.last_event_sequence += 1

        event_sequence = (
            self.state.last_event_sequence
        )

        payload_copy = copy.deepcopy(
            payload
        )

        payload_hash = sha256_object(
            payload_copy
        )

        envelope = SyntheticEnvelope(
            envelope_id=str(uuid.uuid4()),
            action=action,
            symbol=self.config.symbol,
            payload=payload_copy,
            payload_hash=payload_hash,
            config_fingerprint=(
                self.config.fingerprint()
            ),
            generation=self.state.generation,
            recovery_epoch=(
                self.state.recovery_epoch
            ),
            event_sequence=event_sequence,
            created_at=utc_timestamp(),
        )

        receipt = SyntheticReceipt(
            receipt_id=str(uuid.uuid4()),
            envelope_id=envelope.envelope_id,
            accepted=True,
            transmitted=False,
            transport="SYNTHETIC_ONLY",
            payload_hash=payload_hash,
            generation=self.state.generation,
            recovery_epoch=(
                self.state.recovery_epoch
            ),
            event_sequence=event_sequence,
            created_at=utc_timestamp(),
        )

        self.state.synthetic_dispatch_count += 1

        self.receipts.append(
            receipt
        )

        return envelope, receipt


# =============================================================================
# INTEGRATED RUNTIME
# =============================================================================


class IntegratedRuntime:
    def __init__(
        self,
        config: RuntimeConfig,
        store: AtomicStateStore,
    ):
        self.config = config
        self.store = store

        self.restored_existing_state = False

        self.state = self._load_or_create_state()

        self.firebreak = NetworkWriteFirebreak(
            self.state
        )

        self.synthetic_transport = SyntheticTransport(
            self.state,
            self.config,
        )

    def _load_or_create_state(
        self,
    ) -> DurableRuntimeState:

        fingerprint = (
            self.config.fingerprint()
        )

        if self.store.exists():
            state = self.store.load()

            self.restored_existing_state = True

            old_fingerprint = (
                state.config_fingerprint
            )

            if (
                old_fingerprint
                != fingerprint
            ):
                if (
                    old_fingerprint
                    not in
                    state.historical_runtime_fingerprints
                ):
                    state.historical_runtime_fingerprints.append(
                        old_fingerprint
                    )

                state.config_fingerprint = (
                    fingerprint
                )

                # Configuration changes represent a new
                # local runtime generation.
                state.generation += 1

                # A new boot/recovery authority epoch
                # accompanies the generation transition.
                state.recovery_epoch += 1

            else:
                # Even with the same configuration,
                # every actual restart advances recovery
                # epoch monotonically.
                state.recovery_epoch += 1

            state.boot_count += 1
            state.last_boot_at = utc_timestamp()
            state.phase = "BOOTSTRAPPED"

            state.seal()

            return state

        now = utc_timestamp()

        state = DurableRuntimeState(
            schema_version=STATE_SCHEMA_VERSION,
            runtime_id=str(uuid.uuid4()),
            generation=1,
            recovery_epoch=1,
            boot_count=1,
            created_at=now,
            last_boot_at=now,
            last_persisted_at=now,
            config_fingerprint=fingerprint,
            phase="BOOTSTRAPPED",
            synthetic_dispatch_count=0,
            real_network_write_attempts=0,
            demo_network_write_attempts=0,
            blocked_network_write_attempts=0,
            real_orders_sent=0,
            demo_orders_sent=0,
            last_event_sequence=0,
            historical_runtime_fingerprints=[],
            integrity_seal="",
        )

        state.seal()

        return state

    def persist(self) -> None:
        self.store.save(
            self.state
        )

    def validate(self) -> None:
        validate_config(
            self.config
        )

        self.state.validate_integrity()

        require(
            self.state.schema_version ==
            STATE_SCHEMA_VERSION,
            "runtime state schema invalid",
        )

        require(
            self.state.runtime_id,
            "runtime ID missing",
        )

        require(
            self.state.generation >= 1,
            "runtime generation invalid",
        )

        require(
            self.state.recovery_epoch >= 1,
            "recovery epoch invalid",
        )

        require(
            self.state.boot_count >= 1,
            "boot count invalid",
        )

        require(
            self.state.config_fingerprint ==
            self.config.fingerprint(),
            "runtime config fingerprint mismatch",
        )

        require(
            self.state.real_orders_sent == 0,
            "real order count must remain zero",
        )

        require(
            self.state.demo_orders_sent == 0,
            "demo order count must remain zero",
        )


# =============================================================================
# TEST HARNESS
# =============================================================================


class DiagnosticHarness:
    def __init__(self):
        self.test_groups = 0
        self.pass_assertions = 0

    def group(
        self,
        number: int,
        title: str,
    ) -> None:

        self.test_groups += 1

        print_header(
            f"{UNIT_NAME} TEST {number}: {title}"
        )

    def passed(
        self,
        label: str,
    ) -> None:

        self.pass_assertions += 1
        print_pass(label)

    def check(
        self,
        condition: bool,
        label: str,
        failure_message: Optional[str] = None,
    ) -> None:

        if not condition:
            raise ValidationError(
                failure_message
                or label
            )

        self.passed(label)


# =============================================================================
# HEALTH SERVER
# =============================================================================


class HealthState:
    def __init__(self):
        self.lock = threading.Lock()

        self.runtime_ready = False
        self.diagnostics_passed = False

        self.unit = UNIT_NAME

        self.runtime_id = ""
        self.generation = 0
        self.recovery_epoch = 0
        self.boot_count = 0

        self.synthetic_only = True
        self.network_writes = False

        self.real_orders_sent = 0
        self.demo_orders_sent = 0

        self.synthetic_dispatch_count = 0

        self.last_event_sequence = 0

        self.heartbeat = 0

        self.started_at = utc_timestamp()

    def update_from_runtime(
        self,
        runtime: IntegratedRuntime,
    ) -> None:

        with self.lock:
            self.runtime_id = (
                runtime.state.runtime_id
            )

            self.generation = (
                runtime.state.generation
            )

            self.recovery_epoch = (
                runtime.state.recovery_epoch
            )

            self.boot_count = (
                runtime.state.boot_count
            )

            self.synthetic_only = (
                runtime.config.synthetic_transport_only
            )

            self.network_writes = (
                runtime.config.network_writes_enabled
            )

            self.real_orders_sent = (
                runtime.state.real_orders_sent
            )

            self.demo_orders_sent = (
                runtime.state.demo_orders_sent
            )

            self.synthetic_dispatch_count = (
                runtime.state.synthetic_dispatch_count
            )

            self.last_event_sequence = (
                runtime.state.last_event_sequence
            )

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "ok": True,
                "unit": self.unit,
                "runtime_ready": self.runtime_ready,
                "diagnostics_passed": self.diagnostics_passed,
                "runtime_id": self.runtime_id,
                "generation": self.generation,
                "recovery_epoch": self.recovery_epoch,
                "boot_count": self.boot_count,
                "synthetic_only": self.synthetic_only,
                "network_writes": self.network_writes,
                "real_orders_sent": self.real_orders_sent,
                "demo_orders_sent": self.demo_orders_sent,
                "synthetic_dispatch_count": (
                    self.synthetic_dispatch_count
                ),
                "last_event_sequence": (
                    self.last_event_sequence
                ),
                "heartbeat": self.heartbeat,
                "uptime_seconds": (
                    utc_timestamp()
                    - self.started_at
                ),
            }


HEALTH_STATE = HealthState()


class HealthRequestHandler(
    BaseHTTPRequestHandler
):
    def do_GET(self) -> None:
        if self.path not in (
            "/",
            "/health",
            "/healthz",
        ):
            self.send_response(404)
            self.end_headers()
            return

        payload = canonical_json(
            HEALTH_STATE.snapshot()
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(payload)),
        )

        self.end_headers()

        self.wfile.write(payload)

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        # Keep Render logs clean.
        return


# =============================================================================
# GLOBAL RUNTIME CONTROL
# =============================================================================


STOP_EVENT = threading.Event()


def install_signal_handlers() -> None:
    def handle_signal(
        signum: int,
        frame: Any,
    ) -> None:
        del frame

        print(
            f"{UNIT_NAME}: RECEIVED SIGNAL {signum}",
            flush=True,
        )

        STOP_EVENT.set()

    for sig in (
        signal.SIGTERM,
        signal.SIGINT,
    ):
        try:
            signal.signal(
                sig,
                handle_signal,
            )
        except Exception:
            pass


# =============================================================================
# STATE DIRECTORY
# =============================================================================


def resolve_state_path() -> Path:
    configured = os.getenv(
        "R29_STATE_FILE"
    )

    if configured:
        return Path(
            configured
        ).expanduser().resolve()

    data_dir = os.getenv(
        "R29_DATA_DIR",
        "./r29_runtime",
    )

    return (
        Path(data_dir)
        .expanduser()
        .resolve()
        / STATE_FILE_NAME
    )


# =============================================================================
# DIAGNOSTICS
# =============================================================================


def run_diagnostics(
    runtime: IntegratedRuntime,
    harness: DiagnosticHarness,
) -> None:

    config = runtime.config
    state = runtime.state
    store = runtime.store

    # =========================================================================
    # TEST 1
    # =========================================================================

    harness.group(
        1,
        "INTEGRATED RUNTIME BOOT",
    )

    harness.check(
        bool(state.runtime_id),
        "Runtime ID Established",
    )

    harness.check(
        state.generation >= 1,
        "Runtime Generation Established",
    )

    harness.check(
        state.recovery_epoch >= 1,
        "Recovery Epoch Established",
    )

    harness.check(
        state.boot_count >= 1,
        "Boot Counter Established",
    )

    # =========================================================================
    # TEST 2
    # =========================================================================

    harness.group(
        2,
        "STRATEGY CONFIGURATION BASELINE",
    )

    harness.check(
        config.symbol == DEFAULT_SYMBOL,
        "Primary Symbol Is BTCUSDT",
    )

    harness.check(
        config.margin_type == "ISOLATED",
        "Planned Margin Type Is ISOLATED",
    )

    harness.check(
        config.planned_leverage == 100,
        "Planned Leverage Is 100x",
    )

    harness.check(
        config.initial_entry_percent == 5.0,
        "Initial Entry Allocation Is 5 Percent",
    )

    harness.check(
        config.max_pyramid_adds == 1,
        "Maximum Pyramid Adds Is One",
    )

    harness.check(
        config.max_backups == 3,
        "Maximum Backup Entries Is Three",
    )

    harness.check(
        config.max_fund_exposure_percent == 35.0,
        "Maximum Fund Exposure Is 35 Percent",
    )

    # =========================================================================
    # TEST 3
    # =========================================================================

    harness.group(
        3,
        "TAKE-PROFIT AND TRAILING BASELINE",
    )

    harness.check(
        config.tp1_percent == 20.0,
        "TP1 Allocation Is 20 Percent",
    )

    harness.check(
        config.tp2_percent == 20.0,
        "TP2 Allocation Is 20 Percent",
    )

    harness.check(
        config.tp3_percent == 60.0,
        "TP3 Allocation Is 60 Percent",
    )

    harness.check(
        abs(
            config.tp1_percent
            + config.tp2_percent
            + config.tp3_percent
            - 100.0
        ) < 1e-9,
        "Take-Profit Allocation Totals 100 Percent",
    )

    harness.check(
        config.trailing_distance_percent == 0.20,
        "Trailing Distance Is 0.20 Percent",
    )

    # =========================================================================
    # TEST 4
    # =========================================================================

    harness.group(
        4,
        "RISK AND SIGNAL SAFETY BASELINE",
    )

    harness.check(
        config.signal_expiry_seconds == 120,
        "Signal Expiry Is 120 Seconds",
    )

    harness.check(
        config.loss_cooldown_seconds == 300,
        "Loss Cooldown Is 300 Seconds",
    )

    harness.check(
        config.one_direction_only,
        "One-Direction Safety Enabled",
    )

    harness.check(
        config.anti_duplicate_orders,
        "Anti-Duplicate Protection Enabled",
    )

    harness.check(
        config.trend_reversal_exit,
        "Trend-Reversal Exit Enabled",
    )

    harness.check(
        config.idle_pyramid_cleanup,
        "Idle Pyramid Cleanup Enabled",
    )

    # =========================================================================
    # TEST 5
    # =========================================================================

    harness.group(
        5,
        "RUNTIME CONFIGURATION FINGERPRINT",
    )

    fingerprint_a = (
        config.fingerprint()
    )

    fingerprint_b = (
        sha256_object(
            config.fingerprint_payload()
        )
    )

    harness.check(
        fingerprint_a ==
        fingerprint_b,
        "Configuration Fingerprint Deterministic",
    )

    harness.check(
        state.config_fingerprint ==
        fingerprint_a,
        "Durable State Bound To Current Configuration",
    )

    # =========================================================================
    # TEST 6
    # =========================================================================

    harness.group(
        6,
        "DURABLE BASELINE STATE",
    )

    runtime.validate()

    harness.passed(
        "Integrated Runtime State Validates"
    )

    harness.check(
        state.phase ==
        "BOOTSTRAPPED",
        "Runtime Phase Is BOOTSTRAPPED",
    )

    harness.check(
        state.real_orders_sent == 0,
        "Real Order Counter Is Zero",
    )

    harness.check(
        state.demo_orders_sent == 0,
        "Demo Order Counter Is Zero",
    )

    # =========================================================================
    # TEST 7
    # =========================================================================

    harness.group(
        7,
        "ATOMIC STATE PERSISTENCE",
    )

    runtime.persist()

    harness.check(
        store.exists(),
        "Durable State File Created",
    )

    persisted = store.load()

    harness.check(
        persisted.runtime_id ==
        state.runtime_id,
        "Persisted Runtime ID Matches",
    )

    harness.check(
        persisted.generation ==
        state.generation,
        "Persisted Generation Matches",
    )

    harness.check(
        persisted.recovery_epoch ==
        state.recovery_epoch,
        "Persisted Recovery Epoch Matches",
    )

    # =========================================================================
    # TEST 8
    # =========================================================================

    harness.group(
        8,
        "DURABLE STATE INTEGRITY SEAL",
    )

    persisted.validate_integrity()

    harness.passed(
        "Persisted Runtime Integrity Seal Validates"
    )

    tampered_payload = (
        persisted.to_dict()
    )

    tampered_payload[
        "generation"
    ] += 100

    tampered_state = (
        DurableRuntimeState.from_dict(
            tampered_payload
        )
    )

    tamper_rejected = False

    try:
        tampered_state.validate_integrity()

    except IntegrityError as exc:
        print_local_block(
            str(exc)
        )

        tamper_rejected = True

    harness.check(
        tamper_rejected,
        "Tampered Runtime State Rejected",
    )

    # =========================================================================
    # TEST 9
    # =========================================================================

    harness.group(
        9,
        "HTTP WRITE FIREBREAK",
    )

    blocked_methods = (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    )

    for method in blocked_methods:
        was_blocked = False

        try:
            runtime.firebreak.guard_http(
                method=method,
                target="/synthetic/test",
                payload={
                    "symbol": config.symbol,
                    "test": True,
                },
                environment="REAL",
            )

        except NetworkWriteBlocked as exc:
            print_local_block(
                str(exc)
            )

            was_blocked = True

        harness.check(
            was_blocked,
            f"HTTP {method} Blocked",
        )

    # =========================================================================
    # TEST 10
    # =========================================================================

    harness.group(
        10,
        "DEMO WRITE FIREBREAK",
    )

    demo_blocked = False

    try:
        runtime.firebreak.guard_http(
            method="POST",
            target="/demo/order",
            payload={
                "symbol": config.demo_symbol,
                "side": "BUY",
            },
            environment="DEMO",
        )

    except NetworkWriteBlocked as exc:
        print_local_block(
            str(exc)
        )

        demo_blocked = True

    harness.check(
        demo_blocked,
        "Demo Order POST Blocked",
    )

    harness.check(
        state.demo_orders_sent == 0,
        "No Demo Order Was Sent",
    )

    # =========================================================================
    # TEST 11
    # =========================================================================

    harness.group(
        11,
        "WEBSOCKET WRITE FIREBREAK",
    )

    websocket_blocked = False

    try:
        runtime.firebreak.guard_websocket_write(
            channel="private-order-channel",
            payload={
                "op": "order",
                "symbol": config.symbol,
            },
        )

    except NetworkWriteBlocked as exc:
        print_local_block(
            str(exc)
        )

        websocket_blocked = True

    harness.check(
        websocket_blocked,
        "WebSocket Mutation Blocked",
    )

    # =========================================================================
    # TEST 12
    # =========================================================================

    harness.group(
        12,
        "SYNTHETIC TRANSPORT BASELINE",
    )

    synthetic_payload = {
        "operation":
            "R29_RUNTIME_BASELINE_PROBE",

        "symbol":
            config.symbol,

        "marginType":
            config.margin_type,

        "plannedLeverage":
            str(config.planned_leverage),

        "networkWrite":
            False,
    }

    before_dispatches = (
        state.synthetic_dispatch_count
    )

    envelope, receipt = (
        runtime.synthetic_transport.dispatch(
            action=(
                "R29_RUNTIME_BASELINE_PROBE"
            ),
            payload=synthetic_payload,
        )
    )

    harness.check(
        receipt.accepted,
        "Synthetic Receipt Accepted",
    )

    harness.check(
        receipt.transmitted is False,
        "Synthetic Receipt Reports No Transmission",
    )

    harness.check(
        receipt.transport ==
        "SYNTHETIC_ONLY",
        "Synthetic Transport Exact",
    )

    harness.check(
        receipt.payload_hash ==
        envelope.payload_hash,
        "Synthetic Payload Hash Preserved",
    )

    harness.check(
        state.synthetic_dispatch_count ==
        before_dispatches + 1,
        "Exactly One Synthetic Dispatch Added",
    )

    # =========================================================================
    # TEST 13
    # =========================================================================

    harness.group(
        13,
        "GENERATION AND RECOVERY CONTINUITY",
    )

    harness.check(
        state.generation >= 1,
        "Generation Is Monotonic Positive",
    )

    harness.check(
        state.recovery_epoch >= 1,
        "Recovery Epoch Is Monotonic Positive",
    )

    harness.check(
        state.boot_count >= 1,
        "Boot Count Is Monotonic Positive",
    )

    harness.check(
        state.last_event_sequence >= 1,
        "Integrated Event Sequence Established",
    )

    # =========================================================================
    # TEST 14
    # =========================================================================

    harness.group(
        14,
        "FINAL SAFETY INVARIANTS",
    )

    harness.check(
        config.real_order_execution is False,
        "Real Order Execution Disabled",
    )

    harness.check(
        config.demo_order_execution is False,
        "Demo Order Execution Disabled",
    )

    harness.check(
        config.network_writes_enabled is False,
        "All Network Writes Disabled",
    )

    harness.check(
        config.synthetic_transport_only is True,
        "Synthetic Transport Only",
    )

    harness.check(
        config.allow_leverage_mutation is False,
        "Leverage Mutation Disabled",
    )

    harness.check(
        config.allow_margin_mutation is False,
        "Margin Mutation Disabled",
    )

    harness.check(
        config.allow_position_mutation is False,
        "Position Mutation Disabled",
    )

    harness.check(
        config.allow_account_mutation is False,
        "Account Mutation Disabled",
    )

    # =========================================================================
    # TEST 15
    # =========================================================================

    harness.group(
        15,
        "RESTART-RESTORABLE INTEGRATED SNAPSHOT",
    )

    runtime.persist()

    before_restart = (
        runtime.store.load()
    )

    simulated_restart_runtime = (
        IntegratedRuntime(
            config=config,
            store=store,
        )
    )

    after_restart = (
        simulated_restart_runtime.state
    )

    harness.check(
        after_restart.runtime_id ==
        before_restart.runtime_id,
        "Runtime Identity Survives Restart",
    )

    harness.check(
        after_restart.generation ==
        before_restart.generation,
        "Generation Survives Same-Configuration Restart",
    )

    harness.check(
        after_restart.recovery_epoch ==
        before_restart.recovery_epoch + 1,
        "Recovery Epoch Advances On Restart",
    )

    harness.check(
        after_restart.boot_count ==
        before_restart.boot_count + 1,
        "Boot Counter Advances On Restart",
    )

    harness.check(
        after_restart.config_fingerprint ==
        config.fingerprint(),
        "Configuration Binding Survives Restart",
    )

    harness.check(
        after_restart.real_orders_sent == 0,
        "Real Order Counter Remains Zero After Restart",
    )

    harness.check(
        after_restart.demo_orders_sent == 0,
        "Demo Order Counter Remains Zero After Restart",
    )

    # Commit the simulated restart state as the
    # authoritative Unit A state for subsequent boot.
    simulated_restart_runtime.persist()

    # Synchronize current runtime object so health data
    # accurately represents the final durable state.
    runtime.state = (
        simulated_restart_runtime.state
    )

    runtime.firebreak.state = (
        runtime.state
    )

    runtime.synthetic_transport.state = (
        runtime.state
    )

    # =========================================================================
    # TEST 16
    # =========================================================================

    harness.group(
        16,
        "TERMINAL INTEGRATED BASELINE VALIDATION",
    )

    runtime.state.phase = (
        "R29_UNIT_A_VALIDATED"
    )

    runtime.persist()

    final_state = (
        runtime.store.load()
    )

    final_state.validate_integrity()

    harness.passed(
        "Final Durable Runtime State Validates"
    )

    harness.check(
        final_state.phase ==
        "R29_UNIT_A_VALIDATED",
        "Integrated Runtime Baseline Finalized",
    )

    harness.check(
        final_state.config_fingerprint ==
        config.fingerprint(),
        "Final Configuration Fingerprint Validates",
    )

    harness.check(
        final_state.real_orders_sent == 0,
        "Final Real Order Count Is Zero",
    )

    harness.check(
        final_state.demo_orders_sent == 0,
        "Final Demo Order Count Is Zero",
    )

    harness.check(
        config.network_writes_enabled is False,
        "Final Network Write Firebreak Active",
    )

    # Update runtime reference to exact terminal durable state.
    runtime.state = final_state
    runtime.firebreak.state = final_state
    runtime.synthetic_transport.state = (
        final_state
    )


# =============================================================================
# HEALTH SERVER START
# =============================================================================


def start_health_server(
    port: int,
) -> ThreadingHTTPServer:

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        HealthRequestHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
        name="r29-health-server",
    )

    thread.start()

    return server


# =============================================================================
# HEARTBEAT LOOP
# =============================================================================


def heartbeat_loop(
    runtime: IntegratedRuntime,
) -> None:

    heartbeat_number = 0

    interval = (
        runtime.config.heartbeat_seconds
    )

    while not STOP_EVENT.is_set():
        heartbeat_number += 1

        HEALTH_STATE.update_from_runtime(
            runtime
        )

        with HEALTH_STATE.lock:
            HEALTH_STATE.heartbeat = (
                heartbeat_number
            )

        print(
            f"{UNIT_NAME}: HEARTBEAT "
            f"{heartbeat_number} | "
            f"synthetic-only="
            f"{runtime.config.synthetic_transport_only} | "
            f"network-writes="
            f"{runtime.config.network_writes_enabled}",
            flush=True,
        )

        STOP_EVENT.wait(
            interval
        )


# =============================================================================
# MAIN
# =============================================================================


def main() -> int:
    install_signal_handlers()

    state_path = (
        resolve_state_path()
    )

    config = (
        RuntimeConfig.load()
    )

    validate_config(
        config
    )

    print_header(
        f"{UNIT_NAME}: {UNIT_DESCRIPTION}"
    )

    print(
        f"Symbol: {config.symbol}",
        flush=True,
    )

    print(
        f"Demo Symbol: {config.demo_symbol}",
        flush=True,
    )

    print(
        f"Planned Margin Type: "
        f"{config.margin_type}",
        flush=True,
    )

    print(
        f"Planned Leverage: "
        f"{config.planned_leverage}x",
        flush=True,
    )

    print(
        f"Initial Entry: "
        f"{config.initial_entry_percent}%",
        flush=True,
    )

    print(
        f"Max Pyramid Adds: "
        f"{config.max_pyramid_adds}",
        flush=True,
    )

    print(
        f"Max Backups: "
        f"{config.max_backups}",
        flush=True,
    )

    print(
        f"Max Fund Exposure: "
        f"{config.max_fund_exposure_percent}%",
        flush=True,
    )

    print(
        f"State File: {state_path}",
        flush=True,
    )

    print(
        "Real Order Execution: DISABLED",
        flush=True,
    )

    print(
        "Demo Order Execution: DISABLED",
        flush=True,
    )

    print(
        "Network Writes: DISABLED",
        flush=True,
    )

    print(
        "Synthetic Transport: ENABLED",
        flush=True,
    )

    store = AtomicStateStore(
        state_path
    )

    runtime = IntegratedRuntime(
        config=config,
        store=store,
    )

    HEALTH_STATE.update_from_runtime(
        runtime
    )

    HEALTH_STATE.runtime_ready = True

    harness = DiagnosticHarness()

    try:
        run_diagnostics(
            runtime,
            harness,
        )

    except Exception as exc:
        print_header(
            f"{UNIT_NAME}: DIAGNOSTIC FAILURE"
        )

        print(
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        traceback.print_exc()

        try:
            runtime.persist()
        except Exception:
            traceback.print_exc()

        return 1

    HEALTH_STATE.update_from_runtime(
        runtime
    )

    HEALTH_STATE.diagnostics_passed = (
        True
    )

    print_header(
        f"{UNIT_NAME}: ALL DIAGNOSTICS PASSED"
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
        f"{UNIT_NAME}: TEST GROUPS EXECUTED = "
        f"{harness.test_groups}",
        flush=True,
    )

    print(
        f"{UNIT_NAME}: PASS ASSERTIONS = "
        f"{harness.pass_assertions}",
        flush=True,
    )

    if not HEALTH_SERVER_ENABLED:
        return 0

    try:
        server = start_health_server(
            config.health_port
        )

    except OSError as exc:
        print(
            f"{UNIT_NAME}: HEALTH SERVER FAILED: "
            f"{exc}",
            flush=True,
        )

        return 1

    print(
        f"{UNIT_NAME}: HEALTH SERVER LISTENING "
        f"ON PORT {config.health_port}",
        flush=True,
    )

    try:
        heartbeat_loop(
            runtime
        )

    finally:
        try:
            runtime.persist()
        except Exception:
            traceback.print_exc()

        server.shutdown()
        server.server_close()

    print(
        f"{UNIT_NAME}: SHUTDOWN COMPLETE",
        flush=True,
    )

    return 0


# =============================================================================
# ENTRYPOINT
# =============================================================================


if __name__ == "__main__":
    sys.exit(main())
