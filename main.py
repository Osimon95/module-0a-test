from __future__ import annotations

import hashlib
import json
import os
import socketserver
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_DOWN, getcontext
from enum import Enum
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# R31B
# FINAL PRE-EXECUTION INTEGRATION / READINESS VALIDATION
#
# SAFETY DISCIPLINE:
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO EXCHANGE NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE:
#
#   observation
#       ->
#   signal
#       ->
#   strategy decision
#       ->
#   risk gate
#       ->
#   quantity projection
#       ->
#   TP / backup projection
#       ->
#   candidate
#       ->
#   authorization envelope
#       ->
#   synthetic dispatch
#       ->
#   durable seal
#       ->
#   restart-safe recovery
#
# R31B MUST NOT TRANSMIT AN ORDER.
# =============================================================================


getcontext().prec = 28


# =============================================================================
# IDENTITY
# =============================================================================

VERSION = "R31B"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper() or "BTCUSDT"

STATE_FILE = Path(
    os.getenv(
        "R31B_STATE_FILE",
        "/tmp/r31b_pre_execution_readiness_state.json",
    )
)

HEALTH_PORT = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "10000")))

HEARTBEAT_SECONDS = 30


# =============================================================================
# ABSOLUTE SAFETY CONSTANTS
# =============================================================================

REAL_ORDER_EXECUTION_ENABLED = False
DEMO_ORDER_EXECUTION_ENABLED = False

EXCHANGE_NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

WEBSOCKET_WRITES_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# =============================================================================
# STRATEGY CONSTANTS
# =============================================================================

TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_PERCENT = Decimal("5")
BACKUP_PERCENT = Decimal("5")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

BACKUP_BUFFER_PERCENT = Decimal("0.3")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")
TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# =============================================================================
# SYNTHETIC CONTRACT RULES
# =============================================================================

QTY_STEP = Decimal("0.0001")
MIN_QTY = Decimal("0.0001")
PRICE_STEP = Decimal("0.1")

SYNTHETIC_AVAILABLE_BALANCE = Decimal(
    os.getenv("R31B_SYNTHETIC_BALANCE", "7.18945017")
)

SYNTHETIC_MARK_PRICE = Decimal(
    os.getenv("R31B_SYNTHETIC_MARK_PRICE", "80000")
)


# =============================================================================
# ENUMS
# =============================================================================

class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalStrength(str, Enum):
    WEAK = "WEAK"
    NORMAL = "NORMAL"
    STRONG = "STRONG"


class CandidatePhase(str, Enum):
    CREATED = "CREATED"
    RISK_ACCEPTED = "RISK_ACCEPTED"
    AUTHORIZED = "AUTHORIZED"
    SYNTHETICALLY_DISPATCHED = "SYNTHETICALLY_DISPATCHED"
    SEALED = "SEALED"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class MarketObservation:
    symbol: str
    mark_price: str
    timestamp: int
    source: str


@dataclass(frozen=True)
class StrategySignal:
    signal_id: str
    symbol: str
    direction: str
    strength: str
    observed_price: str
    created_at: int
    expires_at: int


@dataclass(frozen=True)
class RiskProjection:
    available_balance: str
    entry_margin_budget: str
    target_leverage: str
    projected_notional: str
    raw_quantity: str
    rounded_quantity: str
    rounded_notional: str
    rounded_margin: str
    exposure_percent: str
    accepted: bool
    reason: str


@dataclass(frozen=True)
class TakeProfitProjection:
    tp1_quantity: str
    tp2_quantity: str
    tp3_quantity: str
    reconciled_quantity: str
    trigger_1_percent: str
    trigger_2_percent: str
    trailing_distance_percent: str


@dataclass(frozen=True)
class BackupProjection:
    max_backups: int
    backup_percent: str
    backup_buffer_percent: str
    projected_backup_margin_each: str
    projected_backup_total_margin: str


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    signal_id: str
    symbol: str
    direction: str
    quantity: str
    mark_price: str
    target_leverage: str
    phase: str
    created_at: int


@dataclass(frozen=True)
class AuthorizationEnvelope:
    authorization_id: str
    candidate_id: str
    symbol: str
    direction: str
    quantity: str
    leverage: str
    transport: str
    executable: bool
    network_writes_allowed: bool
    created_at: int
    payload_hash: str


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    authorization_id: str
    candidate_id: str
    transmitted: bool
    synthetic_only: bool
    transport: str
    created_at: int


@dataclass
class RuntimeState:
    version: str
    runtime_id: str
    generation: int
    recovery_epoch: int
    phase: str
    candidate_id: str
    authorization_id: str
    synthetic_receipt_id: str

    real_order_count: int
    demo_order_count: int
    network_write_count: int
    mutation_count: int

    synthetic_dispatch_count: int
    transition_count: int
    consumed_transition_count: int

    sealed: bool
    state_hash: str


# =============================================================================
# COUNTERS
# =============================================================================

REAL_ORDER_COUNT = 0
DEMO_ORDER_COUNT = 0
NETWORK_WRITE_COUNT = 0
MUTATION_COUNT = 0

SYNTHETIC_DISPATCH_COUNT = 0
TRANSITION_COUNT = 0
CONSUMED_TRANSITION_COUNT = 0


# =============================================================================
# TEST TRACKING
# =============================================================================

PASSED = 0
FAILED = 0


def line() -> None:
    print("-" * 92, flush=True)


def section(title: str) -> None:
    line()
    print(title, flush=True)
    line()


def check(name: str, condition: bool) -> None:
    global PASSED, FAILED

    if condition:
        PASSED += 1
        result = "✅ PASS"
    else:
        FAILED += 1
        result = "❌ FAIL"

    print(f"{name:<78} {result}", flush=True)


# =============================================================================
# BASIC HELPERS
# =============================================================================

def now_ts() -> int:
    return int(time.time())


def decimal_string(value: Decimal) -> str:
    return format(value, "f")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )


def quantize_down(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        raise ValueError("step must be positive")

    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


def regardless_environment(_: bool) -> bool:
    """
    Environment state is deliberately ignored.

    This function exists only to make escalation-resistance tests explicit.
    """
    return True


# =============================================================================
# HARD SAFETY BLOCKS
# =============================================================================

class SafetyViolation(RuntimeError):
    pass


def block_real_order(reason: str = "") -> None:
    global REAL_ORDER_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print("  REAL order execution blocked", flush=True)

    if reason:
        print(f"  reason={reason}", flush=True)

    raise SafetyViolation("real order execution disabled")


def block_demo_order(reason: str = "") -> None:
    global DEMO_ORDER_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print("  DEMO order execution blocked", flush=True)

    if reason:
        print(f"  reason={reason}", flush=True)

    raise SafetyViolation("demo order execution disabled")


def block_network_write(method: str, path: str) -> None:
    global NETWORK_WRITE_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print(f"  REAL network {method.upper()} blocked", flush=True)
    print(f"  path={path}", flush=True)

    raise SafetyViolation("exchange network writes disabled")


def block_mutation(kind: str) -> None:
    global MUTATION_COUNT

    print(f"{VERSION} LOCAL BLOCK:", flush=True)
    print(f"  {kind} mutation blocked", flush=True)

    raise SafetyViolation(f"{kind} mutation disabled")


# =============================================================================
# HEALTH SERVER
# =============================================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        if self.path in {"/", "/health", "/healthz"}:
            payload = json.dumps(
                {
                    "status": "ok",
                    "version": VERSION,
                    "symbol": SYMBOL,
                    "synthetic_only": SYNTHETIC_TRANSPORT_ONLY,
                    "real_execution": REAL_ORDER_EXECUTION_ENABLED,
                    "network_writes": EXCHANGE_NETWORK_WRITES_ENABLED,
                    "leverage_mutation": LEVERAGE_MUTATION_ENABLED,
                }
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_health_server() -> None:

    def serve() -> None:
        try:
            with ReusableTCPServer(
                ("0.0.0.0", HEALTH_PORT),
                HealthHandler,
            ) as server:

                print(
                    f"{VERSION}: HEALTH SERVER LISTENING ON PORT {HEALTH_PORT}",
                    flush=True,
                )

                server.serve_forever()

        except Exception as exc:
            print(
                f"{VERSION}: HEALTH SERVER ERROR: {exc}",
                flush=True,
            )

    thread = threading.Thread(
        target=serve,
        daemon=True,
    )

    thread.start()
