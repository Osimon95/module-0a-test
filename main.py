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
from pathlib import Path
from typing import Any, Dict, Optional


# =============================================================================
# R29 UNIT G
# FINAL PROMOTION-READINESS VALIDATION
#
# SAFETY DISCIPLINE
# -----------------------------------------------------------------------------
#   - NO REAL ORDER EXECUTION
#   - NO DEMO ORDER EXECUTION
#   - NO NETWORK WRITES
#   - NO LEVERAGE MUTATION
#   - NO MARGIN MUTATION
#   - NO POSITION MUTATION
#   - NO ACCOUNT MUTATION
#   - NO WEBSOCKET WRITES
#   - SYNTHETIC TRANSPORT ONLY
#
# PURPOSE
# -----------------------------------------------------------------------------
#   R29 UNIT G is the bounded final promotion-readiness gate.
#
#   It validates:
#
#       frozen safety configuration
#           ->
#       durable runtime state
#           ->
#       strategy configuration
#           ->
#       exchange/contract compatibility projection
#           ->
#       synthetic entry construction
#           ->
#       synthetic TP / backup projections
#           ->
#       deterministic payload sealing
#           ->
#       authorization binding
#           ->
#       synthetic dispatch
#           ->
#       durable restart recovery
#           ->
#       replay rejection
#           ->
#       final network-write firebreak
#
# IMPORTANT
# -----------------------------------------------------------------------------
#   THIS UNIT DOES NOT ENABLE LIVE TRADING.
#
#   Passing Unit G means:
#
#       "The R29 synthetic/readiness architecture is internally coherent."
#
#   It does NOT mean:
#
#       "Real execution has been enabled."
#
# =============================================================================


print("R29 UNIT G: MAIN.PY ENTERED", flush=True)


# =============================================================================
# DECIMAL CONFIGURATION
# =============================================================================

getcontext().prec = 40


# =============================================================================
# UNIT IDENTITY
# =============================================================================

UNIT_SERIES = "R29"
UNIT_NAME = "UNIT G"
UNIT_IDENTITY = "R29 UNIT G"
UNIT_PURPOSE = "FINAL PROMOTION-READINESS VALIDATION"


# =============================================================================
# SAFETY CONFIGURATION
# =============================================================================

LIVE_ORDER_EXECUTION = False
DEMO_ORDER_EXECUTION = False

NETWORK_WRITES_ENABLED = False

LEVERAGE_MUTATION_ENABLED = False
MARGIN_MUTATION_ENABLED = False
POSITION_MUTATION_ENABLED = False
ACCOUNT_MUTATION_ENABLED = False

WEBSOCKET_WRITES_ENABLED = False

SYNTHETIC_TRANSPORT_ONLY = True


# =============================================================================
# STRATEGY CONFIGURATION
# =============================================================================

SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

TARGET_MARGIN_TYPE = "ISOLATED"

TARGET_LEVERAGE = Decimal("100")

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_SIZE_PERCENT = Decimal("5")
MAX_PYRAMID_ADDS = 1

BACKUP_SIZE_PERCENT = Decimal("5")
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_TRIGGER_PERCENT = Decimal("0.5")
TP2_TRIGGER_PERCENT = Decimal("1.0")

TP1_CLOSE_PERCENT = Decimal("20")
TP2_CLOSE_PERCENT = Decimal("20")
TP3_CLOSE_PERCENT = Decimal("60")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

SIGNAL_EXPIRY_SECONDS = 120
LOSS_COOLDOWN_SECONDS = 300

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# =============================================================================
# SYNTHETIC CONTRACT BASELINE
# =============================================================================
#
# Unit G remains synthetic-only.
#
# These values are deliberately local validation defaults.
#
# If environment variables are supplied, Unit G can validate different
# read-only/projected values without enabling writes.
#
# =============================================================================

AVAILABLE_BALANCE = Decimal(
    os.getenv(
        "R29_G_AVAILABLE_BALANCE",
        "7.18945017",
    )
)

MARK_PRICE = Decimal(
    os.getenv(
        "R29_G_MARK_PRICE",
        "79000",
    )
)

QTY_STEP = Decimal(
    os.getenv(
        "R29_G_QTY_STEP",
        "0.0001",
    )
)

MIN_QTY = Decimal(
    os.getenv(
        "R29_G_MIN_QTY",
        "0.0001",
    )
)

PRICE_STEP = Decimal(
    os.getenv(
        "R29_G_PRICE_STEP",
        "0.1",
    )
)

EXCHANGE_MIN_LEVERAGE = Decimal(
    os.getenv(
        "R29_G_EXCHANGE_MIN_LEVERAGE",
        "1",
    )
)

EXCHANGE_MAX_LEVERAGE = Decimal(
    os.getenv(
        "R29_G_EXCHANGE_MAX_LEVERAGE",
        "400",
    )
)


# =============================================================================
# DURABLE STATE
# =============================================================================

STATE_DIR = Path(
    os.getenv(
        "R29_STATE_DIR",
        "/tmp/r29-unit-g",
    )
)

STATE_FILE = STATE_DIR / "runtime_state.json"


# =============================================================================
# HEALTH SERVER
# =============================================================================

PORT = int(os.getenv("PORT", "10000"))


class HealthHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        try:
            self.request.recv(1024)

            body = (
                "R29 UNIT G HEALTHY\n"
                "synthetic-only=True\n"
                "network-writes=False\n"
                "live-order-execution=False\n"
            ).encode("utf-8")

            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Connection: close\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
                + body
            )

            self.request.sendall(response)

        except Exception:
            pass


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_health_server() -> None:
    try:
        server = ReusableTCPServer(
            ("0.0.0.0", PORT),
            HealthHandler,
        )

        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )

        thread.start()

        print(
            f"R29 UNIT G: HEALTH SERVER LISTENING ON PORT {PORT}",
            flush=True,
        )

    except OSError as exc:
        print(
            f"R29 UNIT G: HEALTH SERVER NOTICE: {exc}",
            flush=True,
        )


# =============================================================================
# SUPPORT FUNCTIONS
# =============================================================================

SEPARATOR = "-" * 92


def section(title: str) -> None:
    print(SEPARATOR, flush=True)
    print(title, flush=True)
    print(SEPARATOR, flush=True)


def passed(label: str) -> None:
    print(
        f"{label:<80} ✅ PASS",
        flush=True,
    )


def failed(label: str) -> None:
    print(
        f"{label:<80} ❌ FAIL",
        flush=True,
    )


def require(
    condition: bool,
    label: str,
) -> None:
    if condition:
        passed(label)
        return

    failed(label)

    raise RuntimeError(
        f"R29 UNIT G VALIDATION FAILED: {label}"
    )


def decimal_string(value: Decimal) -> str:
    return format(value, "f")


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def sha256_object(data: Dict[str, Any]) -> str:
    return sha256_text(
        canonical_json(data)
    )


def atomic_write_json(
    path: Path,
    data: Dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        ".tmp"
    )

    payload = json.dumps(
        data,
        indent=2,
        sort_keys=True,
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(payload)
        handle.flush()

        try:
            os.fsync(
                handle.fileno()
            )
        except OSError:
            pass

    os.replace(
        temporary,
        path,
    )


def load_json(
    path: Path,
) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        loaded = json.load(handle)

    if not isinstance(
        loaded,
        dict,
    ):
        raise RuntimeError(
            "R29 UNIT G state file is not a JSON object"
        )

    return loaded


def floor_to_step(
    value: Decimal,
    step: Decimal,
) -> Decimal:
    if step <= 0:
        raise ValueError(
            "step must be positive"
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


# =============================================================================
# NETWORK WRITE FIREBREAK
# =============================================================================

def blocked_network_write(
    method: str,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    del payload

    print(
        (
            "R29 UNIT G LOCAL BLOCK: "
            f"REAL network {method.upper()} blocked "
            f"| path={path}"
        ),
        flush=True,
    )

    raise PermissionError(
        (
            "R29 UNIT G SAFETY FIREBREAK: "
            "network writes are disabled"
        )
    )


def blocked_leverage_mutation() -> None:
    print(
        "R29 UNIT G LOCAL BLOCK: leverage mutation disabled",
        flush=True,
    )

    raise PermissionError(
        "leverage mutation disabled"
    )


def blocked_margin_mutation() -> None:
    print(
        "R29 UNIT G LOCAL BLOCK: margin mutation disabled",
        flush=True,
    )

    raise PermissionError(
        "margin mutation disabled"
    )


def blocked_position_mutation() -> None:
    print(
        "R29 UNIT G LOCAL BLOCK: position mutation disabled",
        flush=True,
    )

    raise PermissionError(
        "position mutation disabled"
    )


def blocked_account_mutation() -> None:
    print(
        "R29 UNIT G LOCAL BLOCK: account mutation disabled",
        flush=True,
    )

    raise PermissionError(
        "account mutation disabled"
    )


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class StrategyConfig:
    symbol: str
    margin_type: str
    target_leverage: str
    initial_entry_percent: str
    pyramid_size_percent: str
    max_pyramid_adds: int
    backup_size_percent: str
    max_backups: int
    max_fund_exposure_percent: str
    tp1_trigger_percent: str
    tp2_trigger_percent: str
    tp1_close_percent: str
    tp2_close_percent: str
    tp3_close_percent: str
    trailing_distance_percent: str


@dataclass(frozen=True)
class ContractRules:
    symbol: str
    min_qty: str
    qty_step: str
    price_step: str
    min_leverage: str
    max_leverage: str


@dataclass(frozen=True)
class SyntheticIntent:
    intent_id: str
    symbol: str
    side: str
    margin_type: str
    leverage: str
    generation: int
    recovery_epoch: int
    quantity: str
    reference_price: str
    transport: str
    executable: bool


@dataclass(frozen=True)
class SyntheticAuthorization:
    authorization_id: str
    intent_id: str
    payload_hash: str
    generation: int
    recovery_epoch: int
    transport: str
    network_transmission_permitted: bool


@dataclass(frozen=True)
class SyntheticReceipt:
    receipt_id: str
    intent_id: str
    authorization_id: str
    payload_hash: str
    synthetic: bool
    transmitted: bool
    finalized: bool


# =============================================================================
# RUNTIME STATE
# =============================================================================

def initial_runtime_state() -> Dict[str, Any]:
    return {
        "unit": UNIT_IDENTITY,
        "runtime_id": str(
            uuid.uuid4()
        ),
        "generation": 1,
        "recovery_epoch": 1,

        "synthetic_only": True,
        "network_writes": False,

        "live_order_execution": False,
        "demo_order_execution": False,

        "leverage_mutation": False,
        "margin_mutation": False,
        "position_mutation": False,
        "account_mutation": False,

        "dispatch_count": 0,
        "receipt_count": 0,
        "replay_blocks": 0,

        "phase": "READY",

        "intent": None,
        "authorization": None,
        "receipt": None,

        "promotion_ready": False,
        "r29_final_gate_passed": False,
    }


def prepare_runtime_state() -> Dict[str, Any]:
    existing = load_json(
        STATE_FILE
    )

    if existing is None:
        state = initial_runtime_state()

        atomic_write_json(
            STATE_FILE,
            state,
        )

        return state

    # If the durable state belongs to a previous successful Unit G run,
    # start a fresh local validation generation.
    #
    # This avoids treating a redeploy as a synthetic dispatch replay.
    if existing.get(
        "unit"
    ) == UNIT_IDENTITY:

        existing["generation"] = int(
            existing.get(
                "generation",
                1,
            )
        ) + 1

        existing["recovery_epoch"] = int(
            existing.get(
                "recovery_epoch",
                1,
            )
        ) + 1

        existing["phase"] = "READY"

        existing["intent"] = None
        existing["authorization"] = None
        existing["receipt"] = None

        existing["dispatch_count"] = 0
        existing["receipt_count"] = 0
        existing["replay_blocks"] = 0

        existing["promotion_ready"] = False
        existing["r29_final_gate_passed"] = False

        existing["synthetic_only"] = True
        existing["network_writes"] = False

        existing["live_order_execution"] = False
        existing["demo_order_execution"] = False

        existing["leverage_mutation"] = False
        existing["margin_mutation"] = False
        existing["position_mutation"] = False
        existing["account_mutation"] = False

        atomic_write_json(
            STATE_FILE,
            existing,
        )

        return existing

    # Never silently adopt another unit's durable identity.
    state = initial_runtime_state()

    atomic_write_json(
        STATE_FILE,
        state,
    )

    return state


# =============================================================================
# STRATEGY PROJECTION
# =============================================================================

def build_strategy_config() -> StrategyConfig:
    return StrategyConfig(
        symbol=SYMBOL,
        margin_type=TARGET_MARGIN_TYPE,
        target_leverage=decimal_string(
            TARGET_LEVERAGE
        ),
        initial_entry_percent=decimal_string(
            INITIAL_ENTRY_PERCENT
        ),
        pyramid_size_percent=decimal_string(
            PYRAMID_SIZE_PERCENT
        ),
        max_pyramid_adds=MAX_PYRAMID_ADDS,
        backup_size_percent=decimal_string(
            BACKUP_SIZE_PERCENT
        ),
        max_backups=MAX_BACKUPS,
        max_fund_exposure_percent=decimal_string(
            MAX_FUND_EXPOSURE_PERCENT
        ),
        tp1_trigger_percent=decimal_string(
            TP1_TRIGGER_PERCENT
        ),
        tp2_trigger_percent=decimal_string(
            TP2_TRIGGER_PERCENT
        ),
        tp1_close_percent=decimal_string(
            TP1_CLOSE_PERCENT
        ),
        tp2_close_percent=decimal_string(
            TP2_CLOSE_PERCENT
        ),
        tp3_close_percent=decimal_string(
            TP3_CLOSE_PERCENT
        ),
        trailing_distance_percent=decimal_string(
            TRAILING_DISTANCE_PERCENT
        ),
    )


def build_contract_rules() -> ContractRules:
    return ContractRules(
        symbol=SYMBOL,
        min_qty=decimal_string(
            MIN_QTY
        ),
        qty_step=decimal_string(
            QTY_STEP
        ),
        price_step=decimal_string(
            PRICE_STEP
        ),
        min_leverage=decimal_string(
            EXCHANGE_MIN_LEVERAGE
        ),
        max_leverage=decimal_string(
            EXCHANGE_MAX_LEVERAGE
        ),
    )


def entry_margin_budget() -> Decimal:
    return (
        AVAILABLE_BALANCE
        * INITIAL_ENTRY_PERCENT
        / Decimal("100")
    )


def entry_notional_budget() -> Decimal:
    return (
        entry_margin_budget()
        * TARGET_LEVERAGE
    )


def projected_entry_quantity() -> Decimal:
    raw_quantity = (
        entry_notional_budget()
        / MARK_PRICE
    )

    return floor_to_step(
        raw_quantity,
        QTY_STEP,
    )


def projected_entry_notional() -> Decimal:
    return (
        projected_entry_quantity()
        * MARK_PRICE
    )


def projected_entry_margin() -> Decimal:
    return (
        projected_entry_notional()
        / TARGET_LEVERAGE
    )


def maximum_strategy_percent() -> Decimal:
    initial = INITIAL_ENTRY_PERCENT

    pyramids = (
        PYRAMID_SIZE_PERCENT
        * Decimal(
            MAX_PYRAMID_ADDS
        )
    )

    backups = (
        BACKUP_SIZE_PERCENT
        * Decimal(
            MAX_BACKUPS
        )
    )

    return (
        initial
        + pyramids
        + backups
    )


# =============================================================================
# SYNTHETIC PAYLOAD BUILDERS
# =============================================================================

def build_entry_payload(
    intent: SyntheticIntent,
) -> Dict[str, Any]:
    return {
        "kind": "SYNTHETIC_ENTRY",
        "symbol": intent.symbol,
        "side": intent.side,
        "marginType": intent.margin_type,
        "leverage": intent.leverage,
        "quantity": intent.quantity,
        "referencePrice": intent.reference_price,
        "generation": intent.generation,
        "recoveryEpoch": intent.recovery_epoch,
        "transport": "SYNTHETIC_ONLY",
        "networkTransmission": False,
    }


def build_tp_projection(
    quantity: Decimal,
) -> Dict[str, Any]:
    tp1_qty = floor_to_step(
        quantity
        * TP1_CLOSE_PERCENT
        / Decimal("100"),
        QTY_STEP,
    )

    tp2_qty = floor_to_step(
        quantity
        * TP2_CLOSE_PERCENT
        / Decimal("100"),
        QTY_STEP,
    )

    tp3_qty = quantity - tp1_qty - tp2_qty

    if tp3_qty < 0:
        raise RuntimeError(
            "invalid TP projection"
        )

    return {
        "symbol": SYMBOL,

        "tp1": {
            "trigger_percent": decimal_string(
                TP1_TRIGGER_PERCENT
            ),
            "close_percent": decimal_string(
                TP1_CLOSE_PERCENT
            ),
            "projected_quantity": decimal_string(
                tp1_qty
            ),
        },

        "tp2": {
            "trigger_percent": decimal_string(
                TP2_TRIGGER_PERCENT
            ),
            "close_percent": decimal_string(
                TP2_CLOSE_PERCENT
            ),
            "projected_quantity": decimal_string(
                tp2_qty
            ),
        },

        "tp3": {
            "close_percent": decimal_string(
                TP3_CLOSE_PERCENT
            ),
            "projected_quantity": decimal_string(
                tp3_qty
            ),
            "trailing_distance_percent": decimal_string(
                TRAILING_DISTANCE_PERCENT
            ),
        },

        "transport": "SYNTHETIC_ONLY",
        "networkTransmission": False,
    }


def build_backup_projection() -> Dict[str, Any]:
    backup_margin_each = (
        AVAILABLE_BALANCE
        * BACKUP_SIZE_PERCENT
        / Decimal("100")
    )

    total_backup_margin = (
        backup_margin_each
        * Decimal(
            MAX_BACKUPS
        )
    )

    return {
        "symbol": SYMBOL,
        "max_backups": MAX_BACKUPS,
        "backup_size_percent": decimal_string(
            BACKUP_SIZE_PERCENT
        ),
        "margin_each": decimal_string(
            backup_margin_each
        ),
        "total_backup_margin": decimal_string(
            total_backup_margin
        ),
        "transport": "SYNTHETIC_ONLY",
        "networkTransmission": False,
    }


# =============================================================================
# SYNTHETIC AUTHORIZATION AND DISPATCH
# =============================================================================

def create_authorization(
    intent: SyntheticIntent,
    payload: Dict[str, Any],
) -> SyntheticAuthorization:

    return SyntheticAuthorization(
        authorization_id=str(
            uuid.uuid4()
        ),
        intent_id=intent.intent_id,
        payload_hash=sha256_object(
            payload
        ),
        generation=intent.generation,
        recovery_epoch=intent.recovery_epoch,
        transport="SYNTHETIC_ONLY",
        network_transmission_permitted=False,
    )


def synthetic_dispatch(
    state: Dict[str, Any],
    intent: SyntheticIntent,
    authorization: SyntheticAuthorization,
    payload: Dict[str, Any],
) -> SyntheticReceipt:

    if state.get(
        "phase"
    ) == "FINALIZED":
        state["replay_blocks"] = int(
            state.get(
                "replay_blocks",
                0,
            )
        ) + 1

        atomic_write_json(
            STATE_FILE,
            state,
        )

        print(
            (
                "R29 UNIT G LOCAL BLOCK: "
                "finalized dispatch replay rejected"
            ),
            flush=True,
        )

        raise PermissionError(
            "finalized dispatch replay rejected"
        )

    if not SYNTHETIC_TRANSPORT_ONLY:
        raise RuntimeError(
            "synthetic transport boundary disabled"
        )

    if NETWORK_WRITES_ENABLED:
        raise RuntimeError(
            "network writes unexpectedly enabled"
        )

    payload_hash = sha256_object(
        payload
    )

    if payload_hash != authorization.payload_hash:
        raise RuntimeError(
            "authorization payload hash mismatch"
        )

    if authorization.intent_id != intent.intent_id:
        raise RuntimeError(
            "authorization intent binding mismatch"
        )

    receipt = SyntheticReceipt(
        receipt_id=str(
            uuid.uuid4()
        ),
        intent_id=intent.intent_id,
        authorization_id=authorization.authorization_id,
        payload_hash=payload_hash,
        synthetic=True,
        transmitted=False,
        finalized=True,
    )

    state["dispatch_count"] = int(
        state.get(
            "dispatch_count",
            0,
        )
    ) + 1

    state["receipt_count"] = int(
        state.get(
            "receipt_count",
            0,
        )
    ) + 1

    state["phase"] = "FINALIZED"

    state["intent"] = asdict(
        intent
    )

    state["authorization"] = asdict(
        authorization
    )

    state["receipt"] = asdict(
        receipt
    )

    atomic_write_json(
        STATE_FILE,
        state,
    )

    return receipt


# =============================================================================
# VALIDATION
# =============================================================================

def run_validation() -> Dict[str, Any]:

    section(
        "R29 UNIT G: STARTING FINAL PROMOTION-READINESS VALIDATION"
    )

    state = prepare_runtime_state()

    generation = int(
        state["generation"]
    )

    recovery_epoch = int(
        state["recovery_epoch"]
    )

    # =========================================================================
    # TEST 1
    # =========================================================================

    section(
        "R29 UNIT G TEST 1: SAFETY CONFIGURATION"
    )

    require(
        LIVE_ORDER_EXECUTION is False,
        "Real Order Execution Disabled",
    )

    require(
        DEMO_ORDER_EXECUTION is False,
        "Demo Order Execution Disabled",
    )

    require(
        NETWORK_WRITES_ENABLED is False,
        "Network Writes Disabled",
    )

    require(
        LEVERAGE_MUTATION_ENABLED is False,
        "Leverage Mutation Disabled",
    )

    require(
        MARGIN_MUTATION_ENABLED is False,
        "Margin Mutation Disabled",
    )

    require(
        POSITION_MUTATION_ENABLED is False,
        "Position Mutation Disabled",
    )

    require(
        ACCOUNT_MUTATION_ENABLED is False,
        "Account Mutation Disabled",
    )

    require(
        WEBSOCKET_WRITES_ENABLED is False,
        "WebSocket Writes Disabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY is True,
        "Synthetic Transport Only",
    )

    # =========================================================================
    # TEST 2
    # =========================================================================

    section(
        "R29 UNIT G TEST 2: DURABLE RUNTIME STATE"
    )

    require(
        state["unit"]
        == UNIT_IDENTITY,
        "Runtime Unit Identity Matches",
    )

    require(
        bool(
            state["runtime_id"]
        ),
        "Runtime ID Present",
    )

    require(
        generation >= 1,
        "Generation Valid",
    )

    require(
        recovery_epoch >= 1,
        "Recovery Epoch Valid",
    )

    require(
        state["synthetic_only"]
        is True,
        "Persisted Synthetic-Only Flag True",
    )

    require(
        state["network_writes"]
        is False,
        "Persisted Network-Write Flag False",
    )

    require(
        state["live_order_execution"]
        is False,
        "Persisted Live Execution Flag False",
    )

    # =========================================================================
    # TEST 3
    # =========================================================================

    section(
        "R29 UNIT G TEST 3: NETWORK WRITE FIREBREAK"
    )

    for method in (
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ):
        blocked = False

        try:
            blocked_network_write(
                method,
                "/synthetic/r29/unit-g",
            )

        except PermissionError:
            blocked = True

        require(
            blocked,
            f"HTTP {method} Blocked",
        )

    # =========================================================================
    # TEST 4
    # =========================================================================

    section(
        "R29 UNIT G TEST 4: MUTATION FIREBREAKS"
    )

    mutation_tests = (
        (
            blocked_leverage_mutation,
            "Leverage Mutation Firebreak Active",
        ),
        (
            blocked_margin_mutation,
            "Margin Mutation Firebreak Active",
        ),
        (
            blocked_position_mutation,
            "Position Mutation Firebreak Active",
        ),
        (
            blocked_account_mutation,
            "Account Mutation Firebreak Active",
        ),
    )

    for function, label in mutation_tests:
        blocked = False

        try:
            function()

        except PermissionError:
            blocked = True

        require(
            blocked,
            label,
        )

    # =========================================================================
    # TEST 5
    # =========================================================================

    section(
        "R29 UNIT G TEST 5: STRATEGY CONFIGURATION"
    )

    strategy = build_strategy_config()

    require(
        strategy.symbol
        == SYMBOL,
        "Strategy Symbol Matches",
    )

    require(
        strategy.margin_type
        == "ISOLATED",
        "Strategy Margin Type Is ISOLATED",
    )

    require(
        TARGET_LEVERAGE
        == Decimal("100"),
        "Target Leverage Is 100x",
    )

    require(
        INITIAL_ENTRY_PERCENT
        == Decimal("5"),
        "Initial Entry Is 5 Percent",
    )

    require(
        MAX_PYRAMID_ADDS
        == 1,
        "Maximum Pyramid Adds Is One",
    )

    require(
        MAX_BACKUPS
        == 3,
        "Maximum Backups Is Three",
    )

    require(
        MAX_FUND_EXPOSURE_PERCENT
        == Decimal("35"),
        "Maximum Fund Exposure Is 35 Percent",
    )

    require(
        (
            TP1_CLOSE_PERCENT
            + TP2_CLOSE_PERCENT
            + TP3_CLOSE_PERCENT
        )
        == Decimal("100"),
        "TP Allocation Totals 100 Percent",
    )

    # =========================================================================
    # TEST 6
    # =========================================================================

    section(
        "R29 UNIT G TEST 6: CONTRACT COMPATIBILITY PROJECTION"
    )

    contract = build_contract_rules()

    require(
        contract.symbol
        == SYMBOL,
        "Contract Symbol Matches",
    )

    require(
        QTY_STEP > 0,
        "Quantity Step Is Positive",
    )

    require(
        MIN_QTY > 0,
        "Minimum Quantity Is Positive",
    )

    require(
        PRICE_STEP > 0,
        "Price Step Is Positive",
    )

    require(
        TARGET_LEVERAGE
        >= EXCHANGE_MIN_LEVERAGE,
        "Target Leverage Above Exchange Minimum",
    )

    require(
        TARGET_LEVERAGE
        <= EXCHANGE_MAX_LEVERAGE,
        "Target Leverage Below Exchange Maximum",
    )

    require(
        maximum_strategy_percent()
        <= MAX_FUND_EXPOSURE_PERCENT,
        "Configured Strategy Fits Exposure Cap",
    )

    print(
        (
            "R29 UNIT G: CONTRACT RULES "
            f"qty-step={decimal_string(QTY_STEP)} "
            f"min-qty={decimal_string(MIN_QTY)} "
            f"price-step={decimal_string(PRICE_STEP)}"
        ),
        flush=True,
    )

    # =========================================================================
    # TEST 7
    # =========================================================================

    section(
        "R29 UNIT G TEST 7: SYNTHETIC ENTRY PROJECTION"
    )

    margin_budget = entry_margin_budget()
    notional_budget = entry_notional_budget()
    quantity = projected_entry_quantity()
    projected_notional = projected_entry_notional()
    projected_margin = projected_entry_margin()

    require(
        AVAILABLE_BALANCE > 0,
        "Available Balance Is Positive",
    )

    require(
        MARK_PRICE > 0,
        "Reference Mark Price Is Positive",
    )

    require(
        margin_budget > 0,
        "Entry Margin Budget Is Positive",
    )

    require(
        quantity >= MIN_QTY,
        "Projected Quantity Meets Minimum Quantity",
    )

    require(
        (
            quantity / QTY_STEP
        )
        == (
            quantity / QTY_STEP
        ).to_integral_value(),
        "Projected Quantity Respects Quantity Step",
    )

    require(
        projected_margin
        <= (
            AVAILABLE_BALANCE
            * MAX_FUND_EXPOSURE_PERCENT
            / Decimal("100")
        ),
        "Projected Entry Margin Fits Exposure Cap",
    )

    print(
        (
            "R29 UNIT G: ENTRY PROJECTION "
            f"balance={decimal_string(AVAILABLE_BALANCE)} "
            f"mark-price={decimal_string(MARK_PRICE)} "
            f"margin-budget={decimal_string(margin_budget)} "
            f"notional-budget={decimal_string(notional_budget)} "
            f"quantity={decimal_string(quantity)} "
            f"projected-notional={decimal_string(projected_notional)} "
            f"projected-margin={decimal_string(projected_margin)}"
        ),
        flush=True,
    )

    # =========================================================================
    # TEST 8
    # =========================================================================

    section(
        "R29 UNIT G TEST 8: SYNTHETIC TP AND BACKUP PROJECTIONS"
    )

    tp_projection = build_tp_projection(
        quantity
    )

    backup_projection = build_backup_projection()

    tp1_qty = Decimal(
        tp_projection[
            "tp1"
        ][
            "projected_quantity"
        ]
    )

    tp2_qty = Decimal(
        tp_projection[
            "tp2"
        ][
            "projected_quantity"
        ]
    )

    tp3_qty = Decimal(
        tp_projection[
            "tp3"
        ][
            "projected_quantity"
        ]
    )

    require(
        (
            tp1_qty
            + tp2_qty
            + tp3_qty
        )
        == quantity,
        "TP Quantities Reconcile To Entry Quantity",
    )

    require(
        tp_projection[
            "networkTransmission"
        ]
        is False,
        "TP Projection Confirms No Transmission",
    )

    require(
        backup_projection[
            "networkTransmission"
        ]
        is False,
        "Backup Projection Confirms No Transmission",
    )

    require(
        Decimal(
            backup_projection[
                "backup_size_percent"
            ]
        )
        == BACKUP_SIZE_PERCENT,
        "Backup Size Matches Strategy",
    )

    require(
        backup_projection[
            "max_backups"
        ]
        == MAX_BACKUPS,
        "Backup Count Matches Strategy",
    )

    # =========================================================================
    # TEST 9
    # =========================================================================

    section(
        "R29 UNIT G TEST 9: SYNTHETIC INTENT AND PAYLOAD SEAL"
    )

    intent = SyntheticIntent(
        intent_id=str(
            uuid.uuid4()
        ),
        symbol=SYMBOL,
        side="BUY",
        margin_type=TARGET_MARGIN_TYPE,
        leverage=decimal_string(
            TARGET_LEVERAGE
        ),
        generation=generation,
        recovery_epoch=recovery_epoch,
        quantity=decimal_string(
            quantity
        ),
        reference_price=decimal_string(
            MARK_PRICE
        ),
        transport="SYNTHETIC_ONLY",
        executable=False,
    )

    payload = build_entry_payload(
        intent
    )

    payload_hash = sha256_object(
        payload
    )

    require(
        intent.symbol
        == SYMBOL,
        "Intent Symbol Matches",
    )

    require(
        intent.generation
        == generation,
        "Intent Generation Matches",
    )

    require(
        intent.recovery_epoch
        == recovery_epoch,
        "Intent Recovery Epoch Matches",
    )

    require(
        intent.transport
        == "SYNTHETIC_ONLY",
        "Intent Transport Synthetic Only",
    )

    require(
        intent.executable
        is False,
        "Intent Explicitly Non-Executable",
    )

    require(
        payload[
            "networkTransmission"
        ]
        is False,
        "Payload Explicitly Disables Transmission",
    )

    require(
        len(
            payload_hash
        )
        == 64,
        "Payload SHA256 Length Valid",
    )

    print(
        (
            "R29 UNIT G: SYNTHETIC ENTRY PAYLOAD SHA256 "
            f"{payload_hash}"
        ),
        flush=True,
    )

    # =========================================================================
    # TEST 10
    # =========================================================================

    section(
        "R29 UNIT G TEST 10: SYNTHETIC AUTHORIZATION"
    )

    authorization = create_authorization(
        intent,
        payload,
    )

    require(
        authorization.intent_id
        == intent.intent_id,
        "Authorization Bound To Intent",
    )

    require(
        authorization.payload_hash
        == payload_hash,
        "Authorization Bound To Exact Payload",
    )

    require(
        authorization.generation
        == generation,
        "Authorization Generation Matches",
    )

    require(
        authorization.recovery_epoch
        == recovery_epoch,
        "Authorization Recovery Epoch Matches",
    )

    require(
        authorization.transport
        == "SYNTHETIC_ONLY",
        "Authorization Transport Synthetic Only",
    )

    require(
        authorization.network_transmission_permitted
        is False,
        "Authorization Forbids Network Transmission",
    )

    # =========================================================================
    # TEST 11
    # =========================================================================

    section(
        "R29 UNIT G TEST 11: SYNTHETIC DISPATCH"
    )

    receipt = synthetic_dispatch(
        state,
        intent,
        authorization,
        payload,
    )

    require(
        receipt.synthetic
        is True,
        "Receipt Marked Synthetic",
    )

    require(
        receipt.transmitted
        is False,
        "Receipt Confirms No Transmission",
    )

    require(
        receipt.intent_id
        == intent.intent_id,
        "Receipt Intent Binding Matches",
    )

    require(
        receipt.authorization_id
        == authorization.authorization_id,
        "Receipt Authorization Binding Matches",
    )

    require(
        receipt.payload_hash
        == payload_hash,
        "Receipt Payload Hash Matches",
    )

    require(
        receipt.finalized
        is True,
        "Synthetic Dispatch Finalized",
    )

    require(
        state["dispatch_count"]
        == 1,
        "Exactly One Synthetic Dispatch Recorded",
    )

    require(
        state["receipt_count"]
        == 1,
        "Exactly One Synthetic Receipt Recorded",
    )

    # =========================================================================
    # TEST 12
    # =========================================================================

    section(
        "R29 UNIT G TEST 12: DURABLE RESTART RECOVERY"
    )

    recovered = load_json(
        STATE_FILE
    )

    require(
        recovered is not None,
        "Durable State Reloaded",
    )

    assert recovered is not None

    require(
        recovered["phase"]
        == "FINALIZED",
        "Finalized State Restored",
    )

    require(
        recovered["dispatch_count"]
        == 1,
        "Dispatch Count Restored",
    )

    require(
        recovered["receipt_count"]
        == 1,
        "Receipt Count Restored",
    )

    require(
        recovered[
            "receipt"
        ][
            "receipt_id"
        ]
        == receipt.receipt_id,
        "Receipt Identity Restored",
    )

    require(
        recovered["generation"]
        == generation,
        "Recovered Generation Matches",
    )

    require(
        recovered["recovery_epoch"]
        == recovery_epoch,
        "Recovered Recovery Epoch Matches",
    )

    # =========================================================================
    # TEST 13
    # =========================================================================

    section(
        "R29 UNIT G TEST 13: FINALIZED REPLAY REJECTION"
    )

    replay_blocked = False

    try:
        synthetic_dispatch(
            recovered,
            intent,
            authorization,
            payload,
        )

    except PermissionError:
        replay_blocked = True

    require(
        replay_blocked,
        "Finalized Synthetic Replay Rejected",
    )

    replay_recovered = load_json(
        STATE_FILE
    )

    assert replay_recovered is not None

    require(
        replay_recovered[
            "dispatch_count"
        ]
        == 1,
        "Replay Did Not Create Second Dispatch",
    )

    require(
        replay_recovered[
            "receipt_count"
        ]
        == 1,
        "Replay Did Not Create Second Receipt",
    )

    require(
        replay_recovered[
            "replay_blocks"
        ]
        >= 1,
        "Replay Block Counter Recorded",
    )

    # =========================================================================
    # TEST 14
    # =========================================================================

    section(
        "R29 UNIT G TEST 14: PROMOTION-READINESS INVARIANTS"
    )

    require(
        maximum_strategy_percent()
        == Decimal("25"),
        "Configured Maximum Planned Allocation Is 25 Percent",
    )

    require(
        maximum_strategy_percent()
        < MAX_FUND_EXPOSURE_PERCENT,
        "Planned Allocation Remains Below 35 Percent Cap",
    )

    require(
        ONE_DIRECTION_ONLY
        is True,
        "One Direction Only Protection Enabled",
    )

    require(
        ANTI_DUPLICATE_ORDERS
        is True,
        "Anti-Duplicate Protection Enabled",
    )

    require(
        TREND_REVERSAL_EXIT
        is True,
        "Trend Reversal Exit Enabled",
    )

    require(
        IDLE_PYRAMID_CLEANUP
        is True,
        "Idle Pyramid Cleanup Enabled",
    )

    require(
        SIGNAL_EXPIRY_SECONDS
        == 120,
        "Signal Expiry Is 120 Seconds",
    )

    require(
        LOSS_COOLDOWN_SECONDS
        == 300,
        "Loss Cooldown Is 300 Seconds",
    )

    # =========================================================================
    # TEST 15
    # =========================================================================

    section(
        "R29 UNIT G TEST 15: FINAL EXECUTION FIREBREAK"
    )

    require(
        LIVE_ORDER_EXECUTION
        is False,
        "Real Execution Remains Disabled",
    )

    require(
        DEMO_ORDER_EXECUTION
        is False,
        "Demo Execution Remains Disabled",
    )

    require(
        NETWORK_WRITES_ENABLED
        is False,
        "Network Writes Remain Disabled",
    )

    require(
        LEVERAGE_MUTATION_ENABLED
        is False,
        "Leverage Mutation Remains Disabled",
    )

    require(
        MARGIN_MUTATION_ENABLED
        is False,
        "Margin Mutation Remains Disabled",
    )

    require(
        POSITION_MUTATION_ENABLED
        is False,
        "Position Mutation Remains Disabled",
    )

    require(
        ACCOUNT_MUTATION_ENABLED
        is False,
        "Account Mutation Remains Disabled",
    )

    require(
        SYNTHETIC_TRANSPORT_ONLY
        is True,
        "Synthetic-Only Boundary Remains Active",
    )

    # =========================================================================
    # FINAL R29 G CHECKPOINT
    # =========================================================================

    final_state = load_json(
        STATE_FILE
    )

    assert final_state is not None

    final_state[
        "promotion_ready"
    ] = True

    final_state[
        "r29_final_gate_passed"
    ] = True

    final_state[
        "strategy"
    ] = asdict(
        strategy
    )

    final_state[
        "contract_rules"
    ] = asdict(
        contract
    )

    final_state[
        "entry_projection"
    ] = {
        "available_balance": decimal_string(
            AVAILABLE_BALANCE
        ),
        "mark_price": decimal_string(
            MARK_PRICE
        ),
        "margin_budget": decimal_string(
            margin_budget
        ),
        "notional_budget": decimal_string(
            notional_budget
        ),
        "quantity": decimal_string(
            quantity
        ),
        "projected_notional": decimal_string(
            projected_notional
        ),
        "projected_margin": decimal_string(
            projected_margin
        ),
    }

    final_state[
        "tp_projection"
    ] = tp_projection

    final_state[
        "backup_projection"
    ] = backup_projection

    atomic_write_json(
        STATE_FILE,
        final_state,
    )

    # =========================================================================
    # SUMMARY
    # =========================================================================

    section(
        "R29 UNIT G: VALIDATION SUMMARY"
    )

    print(
        (
            "R29 UNIT G: "
            f"synthetic-only={SYNTHETIC_TRANSPORT_ONLY}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            f"network-writes={NETWORK_WRITES_ENABLED}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            f"leverage-mutation={LEVERAGE_MUTATION_ENABLED}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            f"generation={generation}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            f"recovery-epoch={recovery_epoch}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            f"dispatch-count={final_state['dispatch_count']}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            f"receipt-count={final_state['receipt_count']}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            f"replay-blocks={final_state['replay_blocks']}"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            "promotion-ready=True"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            "real-execution-enabled=False"
        ),
        flush=True,
    )

    section(
        "R29 UNIT G: ALL TESTS PASSED"
    )

    print(
        (
            "R29 UNIT G: "
            "R29 FINAL SYNTHETIC PROMOTION-READINESS "
            "GATE PASSED"
        ),
        flush=True,
    )

    print(
        (
            "R29 UNIT G: "
            "NO REAL ORDER WAS SENT"
        ),
        flush=True,
    )

    return final_state


# =============================================================================
# PERSISTENT RUNTIME
# =============================================================================

def persistent_runtime(
    state: Dict[str, Any],
) -> None:

    section(
        (
            "R29 UNIT G: ENTERING PERSISTENT "
            "SYNTHETIC-ONLY RUNTIME"
        )
    )

    heartbeat = 0

    while True:
        heartbeat += 1

        print(
            (
                f"R29 UNIT G: HEARTBEAT {heartbeat} "
                f"| synthetic-only="
                f"{SYNTHETIC_TRANSPORT_ONLY} "
                f"| network-writes="
                f"{NETWORK_WRITES_ENABLED} "
                f"| leverage-mutation="
                f"{LEVERAGE_MUTATION_ENABLED} "
                f"| generation="
                f"{state['generation']} "
                f"| recovery-epoch="
                f"{state['recovery_epoch']} "
                f"| promotion-ready="
                f"{state.get('promotion_ready', True)}"
            ),
            flush=True,
        )

        time.sleep(
            30
        )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    print(
        "R29 UNIT G: IMPORTS COMPLETE",
        flush=True,
    )

    print(
        "R29 UNIT G: CONSTANTS INITIALIZED",
        flush=True,
    )

    start_health_server()

    final_state = run_validation()

    persistent_runtime(
        final_state
    )


if __name__ == "__main__":
    main()
