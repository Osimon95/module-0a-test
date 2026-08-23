# ============================================================
# 0F-4H-R28-UNIT-B
# STANDALONE EXECUTION INTENT + ORDER STATE MACHINE VALIDATION
#
# IMPORTANT:
# - NO WEEX CONNECTION
# - NO API KEYS REQUIRED
# - NO TELEGRAM REQUIRED
# - NO DEMO ORDER TRANSMISSION
# - NO REAL ORDER TRANSMISSION
# ============================================================

import asyncio
import hashlib
import json
import os
import time
import uuid

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional, Set, Tuple


# ============================================================
# MODULE IDENTITY
# ============================================================

MODULE_NAME = "0F-4H-R28-UNIT-B"


# ============================================================
# ABSOLUTE EXECUTION SAFETY FLAGS
# ============================================================

LIVE_ORDER_EXECUTION = False

DEMO_ORDER_EXECUTION = False

HARD_REAL_POST_LOCK = True

HARD_DEMO_POST_LOCK = True


# ============================================================
# TEST CONFIGURATION
# ============================================================

TEST_SYMBOL = "BTCUSDT"

TEST_SIDE = "BUY"

TEST_POSITION_SIDE = "LONG"

TEST_QUANTITY = Decimal("0.0005")

TEST_LEVERAGE = 100


# ============================================================
# ORDER STATES
# ============================================================

STATE_CREATED = "CREATED"

STATE_VALIDATED = "VALIDATED"

STATE_SHADOW_COMMITTED = "SHADOW_COMMITTED"

STATE_DEMO_PENDING = "DEMO_PENDING"

STATE_DEMO_ACCEPTED = "DEMO_ACCEPTED"

STATE_DEMO_REJECTED = "DEMO_REJECTED"

STATE_LIVE_PENDING = "LIVE_PENDING"

STATE_LIVE_ACCEPTED = "LIVE_ACCEPTED"

STATE_LIVE_REJECTED = "LIVE_REJECTED"

STATE_REJECTED = "REJECTED"

STATE_CANCELLED = "CANCELLED"


# ============================================================
# TERMINAL STATES
# ============================================================

TERMINAL_STATES: Set[str] = {
    STATE_DEMO_ACCEPTED,
    STATE_DEMO_REJECTED,
    STATE_LIVE_ACCEPTED,
    STATE_LIVE_REJECTED,
    STATE_REJECTED,
    STATE_CANCELLED,
}


# ============================================================
# VALID STATE TRANSITIONS
# ============================================================

VALID_TRANSITIONS: Dict[str, Set[str]] = {

    STATE_CREATED: {
        STATE_VALIDATED,
        STATE_REJECTED,
        STATE_CANCELLED,
    },

    STATE_VALIDATED: {
        STATE_SHADOW_COMMITTED,
        STATE_REJECTED,
        STATE_CANCELLED,
    },

    STATE_SHADOW_COMMITTED: {
        STATE_DEMO_PENDING,
        STATE_LIVE_PENDING,
        STATE_REJECTED,
        STATE_CANCELLED,
    },

    STATE_DEMO_PENDING: {
        STATE_DEMO_ACCEPTED,
        STATE_DEMO_REJECTED,
        STATE_CANCELLED,
    },

    STATE_LIVE_PENDING: {
        STATE_LIVE_ACCEPTED,
        STATE_LIVE_REJECTED,
        STATE_CANCELLED,
    },

    STATE_DEMO_ACCEPTED: set(),

    STATE_DEMO_REJECTED: set(),

    STATE_LIVE_ACCEPTED: set(),

    STATE_LIVE_REJECTED: set(),

    STATE_REJECTED: set(),

    STATE_CANCELLED: set(),
}


# ============================================================
# EXECUTION INTENT MODEL
# ============================================================

@dataclass(frozen=True)
class ExecutionIntent:

    intent_id: str

    signal_id: str

    symbol: str

    side: str

    position_side: str

    quantity: Decimal

    leverage: int

    client_order_id: str

    created_ms: int


# ============================================================
# ORDER STATE RECORD
# ============================================================

@dataclass
class OrderStateRecord:

    intent_id: str

    state: str

    updated_ms: int


# ============================================================
# IN-MEMORY SAFETY REGISTRY
# ============================================================

SEEN_INTENT_IDS: Set[str] = set()

SEEN_CLIENT_ORDER_IDS: Set[str] = set()

ORDER_STATES: Dict[str, OrderStateRecord] = {}


# ============================================================
# HASH HELPER
# ============================================================

def sha256_hex(
    value: str,
) -> str:

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# CURRENT TIME
# ============================================================

def now_ms() -> int:

    return int(
        time.time()
        * 1000
    )


# ============================================================
# CLIENT ORDER ID
# ============================================================

def create_client_order_id(
    signal_id: str,
) -> str:

    base = (
        f"{MODULE_NAME}|"
        f"{signal_id}|"
        f"{uuid.uuid4().hex}"
    )

    digest = sha256_hex(
        base
    )

    return (
        "R28B-"
        + digest[:24]
    )


# ============================================================
# EXECUTION INTENT CREATION
# ============================================================

def build_execution_intent(
    signal_id: str,
    symbol: str,
    side: str,
    position_side: str,
    quantity: Decimal,
    leverage: int,
) -> ExecutionIntent:

    signal_id = (
        signal_id
        .strip()
    )

    symbol = (
        symbol
        .strip()
        .upper()
    )

    side = (
        side
        .strip()
        .upper()
    )

    position_side = (
        position_side
        .strip()
        .upper()
    )

    if not signal_id:

        raise ValueError(
            "signal_id cannot be empty"
        )

    if not symbol:

        raise ValueError(
            "symbol cannot be empty"
        )

    if side not in {
        "BUY",
        "SELL",
    }:

        raise ValueError(
            f"Invalid side: {side}"
        )

    if position_side not in {
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "Invalid position_side: "
            f"{position_side}"
        )

    if quantity <= 0:

        raise ValueError(
            "quantity must be greater than zero"
        )

    if leverage <= 0:

        raise ValueError(
            "leverage must be greater than zero"
        )

    client_order_id = (
        create_client_order_id(
            signal_id
        )
    )

    intent_material = "|".join(
        [
            MODULE_NAME,
            signal_id,
            symbol,
            side,
            position_side,
            str(quantity),
            str(leverage),
            client_order_id,
        ]
    )

    intent_id = sha256_hex(
        intent_material
    )

    return ExecutionIntent(
        intent_id=intent_id,
        signal_id=signal_id,
        symbol=symbol,
        side=side,
        position_side=position_side,
        quantity=quantity,
        leverage=leverage,
        client_order_id=client_order_id,
        created_ms=now_ms(),
    )


# ============================================================
# INTENT VALIDATION
# ============================================================

def validate_execution_intent(
    intent: ExecutionIntent,
) -> Tuple[
    bool,
    str,
]:

    if not intent.intent_id:

        return (
            False,
            "missing intent_id",
        )

    if not intent.signal_id:

        return (
            False,
            "missing signal_id",
        )

    if not intent.symbol:

        return (
            False,
            "missing symbol",
        )

    if intent.side not in {
        "BUY",
        "SELL",
    }:

        return (
            False,
            "invalid side",
        )

    if intent.position_side not in {
        "LONG",
        "SHORT",
    }:

        return (
            False,
            "invalid position side",
        )

    if intent.quantity <= 0:

        return (
            False,
            "invalid quantity",
        )
