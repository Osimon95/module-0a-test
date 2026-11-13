
# ============================================================
# WEEX BOT - UNIT 1
# ORIGINAL 22524-LINE WORKING MODEL
# RUNTIME FOUNDATION
# ZERO INDENTATION
# ============================================================

# ============================================================
# STANDARD LIBRARY IMPORTS
# ============================================================

import json
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timezone


# ============================================================
# SHARED LOGGER
# ============================================================

def log(message):

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    print(
        timestamp,
        message,
        flush=True,
    )


# ============================================================
# RECONSTRUCTION UNIT 1
# RUNTIME FOUNDATION
# ============================================================

def fresh_reconstruction_unit_1():

    print(
        "=" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 1 START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 1 PURPOSE
    #
    # Unit 1 proves only that:
    #
    # - main.py starts
    # - required standard-library components are available
    # - no exchange operation occurs inside Unit 1
    #
    # Unit 1 does NOT claim that later units perform no HTTP.
    # --------------------------------------------------------

    print(
        "PASS: MAIN.PY STARTED SUCCESSFULLY",
        flush=True,
    )

    print(
        "PASS: PYTHON STANDARD LIBRARY AVAILABLE",
        flush=True,
    )

    print(
        "PASS: JSON MODULE AVAILABLE",
        flush=True,
    )

    print(
        "PASS: URLLIB MODULE AVAILABLE",
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT-LOCAL SAFETY
    # --------------------------------------------------------

    print(
        "UNIT 1 EXCHANGE CONNECTION = NONE",
        flush=True,
    )

    print(
        "UNIT 1 HTTP REQUEST = NONE",
        flush=True,
    )

    print(
        "UNIT 1 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 1 REAL ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 1 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "-" * 80,
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 1 RESULT = PASS"
    )

    print(
        "=" * 80,
        flush=True,
    )

    return True


# ============================================================
# RUN UNIT 1
# ============================================================

FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)


# ============================================================
# END COMPLETE UNIT 1
# UNIT 2 TO FOLLOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 2 V15
# WEEX CENTRAL CONFIGURATION
# DYNAMIC SYMBOL + GROUPED RENDER SETTINGS
# E0 + B1-B5 + TP1/TP2/TP3 + ATR BUFFER
# ============================================================

import os
import re
import math
from decimal import Decimal, InvalidOperation


def unit_2_v9_number(value, name, allow_zero=False):
    if isinstance(value, bool):
        raise RuntimeError("UNIT 2 INVALID " + name)
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError("UNIT 2 INVALID " + name) from exc
    if not number.is_finite():
        raise RuntimeError("UNIT 2 NONFINITE " + name)
    if number < 0 or (number == 0 and not allow_zero):
        raise RuntimeError("UNIT 2 INVALID RANGE " + name)
    return number


def unit_2_v15_setting(name, default, aliases=(), allow_zero=False):
    value = os.getenv(name)
    if value is None or not value.strip():
        for alias in aliases:
            value = os.getenv(alias)
            if value is not None and value.strip():
                break
        else:
            value = default
    return unit_2_v9_number(value, name, allow_zero)


def unit_2_v15_group(name, defaults, aliases=None):
    aliases = aliases or {}
    result = dict(defaults)
    raw = os.getenv(name, "").strip()

    if raw:
        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue
            separator = ":" if ":" in item else "="
            if separator not in item:
                raise RuntimeError(
                    "UNIT 2 INVALID GROUP ITEM " + item
                )
            key, value = item.split(separator, 1)
            key = key.strip().upper()
            if key not in defaults:
                raise RuntimeError(
                    "UNIT 2 UNKNOWN " + name + " KEY " + key
                )
            result[key] = unit_2_v9_number(
                value, name + "_" + key
            )
    else:
        for key, legacy_names in aliases.items():
            for legacy in legacy_names:
                value = os.getenv(legacy)
                if value is not None and value.strip():
                    result[key] = unit_2_v9_number(
                        value, legacy
                    )
                    break
    return result


# Compatibility with earlier Unit 2 versions.
unit_2_v13_group = unit_2_v15_group
unit_2_v14_group = unit_2_v15_group


def unit_2_v14_symbol(value):
    symbol = str(value or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{2,25}USDT", symbol):
        raise RuntimeError(
            "UNIT 2 INVALID WEEX SYMBOL: " + symbol
        )
    return symbol


def unit_2_v14_symbol_decision(
    requested_symbol,
    active_symbol,
    contract_supported=None,
    position_flat=None,
    orders_clear=None
):
    requested = unit_2_v14_symbol(requested_symbol)
    active = (
        unit_2_v14_symbol(active_symbol)
        if active_symbol else None
    )

    decision = {
        "requested_symbol": requested,
        "active_symbol": active,
        "pending_symbol": None,
        "activate": False,
        "persist_required": False,
        "notification_required": False,
        "status": "VERIFICATION_PENDING",
        "reason": "EXCHANGE_RECONCILIATION_REQUIRED",
    }

    if contract_supported is False:
        decision.update({
            "status": "REJECTED",
            "reason": "UNSUPPORTED_DEMO_CONTRACT",
            "notification_required": True,
        })
    elif contract_supported is not True:
        pass
    elif position_flat is None or orders_clear is None:
        decision["reason"] = "POSITION_OR_ORDER_STATE_UNKNOWN"
    elif requested == active:
        decision.update({
            "status": "ALREADY_ACTIVE",
            "reason": "CONFIRMED_ACTIVE_SYMBOL",
        })
    elif position_flat is False or orders_clear is False:
        decision.update({
            "status": "ACCEPTED_QUEUED",
            "reason": "EXISTING_EXPOSURE_OR_ORDERS",
            "pending_symbol": requested,
            "persist_required": True,
            "notification_required": True,
        })
    else:
        decision.update({
            "status": "ACCEPTED_ACTIVATE",
            "reason": "SUPPORTED_AND_ACCOUNT_FLAT",
            "activate": True,
            "persist_required": True,
            "notification_required": True,
        })

    return decision


def unit_2_v14_symbol_message(decision):
    return (
        "WEEX DEMO SYMBOL SWITCH\n"
        "Requested: " + str(decision["requested_symbol"]) + "\n"
        "Status: " + str(decision["status"]) + "\n"
        "Reason: " + str(decision["reason"])
    )


def unit_2_v14_atr_backup_buffer(
    atr14, market_price, multiplier=1.0
):
    atr = unit_2_v9_number(atr14, "ATR14")
    price = unit_2_v9_number(market_price, "MARKET_PRICE")
    factor = unit_2_v9_number(multiplier, "ATR_MULTIPLIER")
    percent = atr / price * Decimal("100") * factor
    return {
        "atr_buffer_percent": float(percent),
        "long_factor": float(1 + percent / 100),
        "short_factor": float(1 - percent / 100),
    }


unit_2_v13_atr_backup_buffer = unit_2_v14_atr_backup_buffer
unit_2_v12_atr_backup_buffer = unit_2_v14_atr_backup_buffer
unit_2_v11_atr_backup_buffer = unit_2_v14_atr_backup_buffer


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print("FRESH RECONSTRUCTION UNIT 2 V15 START", flush=True)

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError("UNIT 2 UNIT 1 NOT READY")

    requested_symbol = unit_2_v14_symbol(
        os.getenv("WEEX_SYMBOL", "BTCUSDT")
    )

    e0_margin = unit_2_v15_setting(
        "INITIAL_ENTRY_MARGIN_USDT", "0.5",
        aliases=("ENTRY_FIXED_USDT",)
    )
    backup_percent = unit_2_v15_setting(
        "BACKUP_MARGIN_PERCENT", "0.5"
    )
    buffer_percent = unit_2_v15_setting(
        "BACKUP_BUFFER_PERCENT", "0.3"
    )
    cap_percent = unit_2_v15_setting(
        "EXPOSURE_CAP_PERCENT", "50"
    )

    if backup_percent > 100 or cap_percent > 100:
        raise RuntimeError("UNIT 2 PERCENT EXCEEDS 100")
    if buffer_percent >= 100:
        raise RuntimeError("UNIT 2 INVALID BACKUP BUFFER")

    allocations = unit_2_v15_group(
        "TP_ALLOCATION_PERCENT",
        {
            "TP1": Decimal("10"),
            "TP2": Decimal("20"),
            "TP3": Decimal("70"),
        },
        aliases={
            "TP1": ("TP1_ALLOCATION_PERCENT",),
            "TP2": ("TP2_ALLOCATION_PERCENT",),
            "TP3": ("TP3_ALLOCATION_PERCENT",),
        }
    )

    # TP3 is the remainder of TP1 and TP2.
    # Explicit TP3 must agree with that remainder.
    raw_allocation = os.getenv(
        "TP_ALLOCATION_PERCENT", ""
    ).upper()
    explicit_tp3 = bool(
        re.search(r"(?:^|,)\s*TP3\s*[:=]", raw_allocation)
    ) or (
        not raw_allocation.strip()
        and bool(os.getenv("TP3_ALLOCATION_PERCENT", "").strip())
    )

    remaining = (
        Decimal("100")
        - allocations["TP1"]
        - allocations["TP2"]
    )
    if remaining <= 0:
        raise RuntimeError("UNIT 2 INVALID TP ALLOCATION")
    if explicit_tp3 and allocations["TP3"] != remaining:
        raise RuntimeError("UNIT 2 TP3 ALLOCATION MISMATCH")
    allocations["TP3"] = remaining

    roi = unit_2_v15_group(
        "TP_NET_ROI_PERCENT",
        {
            "TP1": Decimal("20"),
            "TP2": Decimal("40"),
        },
        aliases={
            "TP1": (
                "TP1_NET_ROI_FLOOR_PERCENT",
                "TP1_NET_ROI_PERCENT",
            ),
            "TP2": (
                "TP2_NET_ROI_FLOOR_PERCENT",
                "TP2_NET_ROI_PERCENT",
            ),
        }
    )

    trailing = unit_2_v15_group(
        "TP_TRAILING_PERCENT",
        {
            "REF": Decimal("0.20"),
            "MIN": Decimal("0.10"),
            "MAX": Decimal("0.40"),
        },
        aliases={
            "REF": ("TP3_TRAILING_REFERENCE_PERCENT",),
            "MIN": ("TP3_TRAILING_MIN_PERCENT",),
            "MAX": ("TP3_TRAILING_MAX_PERCENT",),
        }
    )

    if roi["TP2"] <= roi["TP1"]:
        raise RuntimeError("UNIT 2 TP2 MUST EXCEED TP1")
    if not (
        trailing["MIN"] <= trailing["REF"] <= trailing["MAX"]
    ):
        raise RuntimeError("UNIT 2 INVALID TRAILING RANGE")

    # Public market-data selection is independent of
    # exchange-confirmed execution authorization.
    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url": "https://api-contract.weex.com",
        "requested_symbol": requested_symbol,
        "market_symbol": requested_symbol,
        "demo_order_symbol": None,
        "active_symbol": None,
        "active_symbol_confirmed": False,
        "symbol_switch_status": "RECONCILIATION_REQUIRED",
        "symbol_switch_mode": "AUTO_DEFERRED",
        "symbol_switch_requires_flat": True,
        "symbol_switch_requires_orders_clear": True,
        "symbol_switch_requires_demo_support": True,
        "symbol_switch_state_storage": "SQLITE",
        "symbol_switch_notification": "TELEGRAM",
        "symbol_switch_decision_function":
            "unit_2_v14_symbol_decision",
        "symbol_switch_message_function":
            "unit_2_v14_symbol_message",
    }

    # Unit 2 itself performs configuration only.
    # These local flags are not global DEMO-order gates.
    safety = {
        "public_market_data_read_enabled": True,
        "demo_account_balance_read_enabled": True,
        "authenticated_api_enabled": False,
        "account_access_enabled": False,
        "position_access_enabled": False,
        "order_endpoint_access_enabled": False,
        "demo_order_submission_enabled": False,
        "real_order_submission_enabled": False,
        "exchange_mutation_enabled": False,
        "leverage_mutation_enabled": False,
        "margin_mode_mutation_enabled": False,
        "position_mode_mutation_enabled": False,
    }

    strategy = {
        "initial_fixed_usdt": float(e0_margin),
        "initial_margin_percent": 5.0,
        "backup_margin_percent": float(backup_percent),
        "backup_buffer_percent": float(buffer_percent),
        "backup_buffer_mode": "ATR_DYNAMIC",
        "backup_buffer_ready": False,
        "max_backups": 5,
        "backup_sizing_mode": "PERCENT_AVAILABLE_BALANCE",
        "backup_trigger_reference": "FRESH_WEEX_LIQUIDATION_PRICE",
        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",
        "backup_long_liquidation_factor":
            float(1 + buffer_percent / 100),
        "backup_short_liquidation_factor":
            float(1 - buffer_percent / 100),
        "exposure_cap_percent": float(cap_percent),
        "exposure_cap_max_percent": 100.0,
        "exposure_cap_basis": "TRADING_ACCOUNT_EQUITY",
        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,
        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,
        "tp1_allocation_percent": float(allocations["TP1"]),
        "tp2_allocation_percent": float(allocations["TP2"]),
        "tp3_allocation_percent": float(allocations["TP3"]),
        "tp1_net_roi_floor_percent": float(roi["TP1"]),
        "tp2_net_roi_floor_percent": float(roi["TP2"]),
        "tp1_tp2_min_roi_separation_percent":
            float(roi["TP2"] - roi["TP1"]),
        "tp3_trailing_reference_percent":
            float(trailing["REF"]),
        "tp3_trailing_min_percent":
            float(trailing["MIN"]),
        "tp3_trailing_max_percent":
            float(trailing["MAX"]),
        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,
        "one_direction_only": True,
        "one_direction_only_scope": "NEW_ENTRIES",
        "hedge_direction_independent": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,
    }

    # Contract precision is provisional until WEEX
    # supplies symbol-specific exchange metadata.
    market_precision = {
        "quantity_step": None,
        "minimum_quantity": None,
        "price_step": None,
        "source": "EXCHANGE_METADATA_PENDING",
    }

    # Preserve the established qualification contract.
    qualification = {
        "common": {
            "mode_priority": ("BREAKOUT", "STRUCTURE", "SCALP"),
            "direction_votes_required": 2,
            "direction_votes_total": 3,
            "use_closed_candles": True,
            "protect_developing_candidates": True,
            "arbitrate_before_scalp": True,
            "scalp_requires_higher_modes_clear": True,
            "signal_expiry_seconds": 120,
            "candidate_expiry_seconds": 120,
            "spike_count_rejection_above": 2,
            "reject_late_impulse_entry": True,
        },
        "breakout": {
            "enabled": True,
            "priority": 1,
            "early_detection_enabled": True,
            "developing_candidate_enabled": True,
            "support_resistance_lookback": 20,
            "developing_proximity_atr": 0.50,
            "confirmation_distance_atr": 0.10,
            "direction_votes_required": 2,
            "momentum_lookback_fast": 5,
            "momentum_lookback_slow": 15,
            "require_momentum_confirmation": True,
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "retest_mandatory": False,
            "allow_preconfirmation": True,
            "minimum_atr_percent": 0.0,
            "max_price_extension_atr": 3.0,
            "spike_rejection_enabled": True,
            "max_spike_count": 2,
            "false_breakout_rejection": True,
            "volume_confirmation_enabled": False,
            "minimum_volume_ratio": 1.20,
            "candidate_expiry_seconds": 120,
        },
        "structure": {
            "enabled": True,
            "priority": 2,
            "early_detection_enabled": True,
            "developing_candidate_enabled": True,
            "ema_fast_period": 19,
            "ema_middle_period": 50,
            "ema_slow_period": 200,
            "direction_votes_required": 2,
            "momentum_lookback_minutes": 15,
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "allow_pullback_entry": True,
            "allow_continuation_entry": True,
            "pullback_tolerance_atr": 0.75,
            "max_price_extension_atr": 2.0,
            "minimum_ema_separation_percent": 0.0,
            "retest_mandatory": False,
            "reject_trend_exhaustion": True,
            "candidate_expiry_seconds": 120,
        },
        "scalp": {
            "enabled": True,
            "priority": 3,
            "sideways_preferred": True,
            "require_sideways_market": True,
            "protect_developing_higher_modes": True,
            "quality_threshold": 70.0,
            "price_action_weight_percent": 50.0,
            "other_factors_weight_percent": 50.0,
            "direction_votes_required": 2,
            "direction_votes_total": 3,
            "max_ema_extension_clusters": 1.5,
            "max_spike_count": 2,
            "reject_late_impulse": True,
            "early_entry_enabled": True,
            "ema_compression_atr_max": 0.70,
            "range20_atr_max": 8.0,
            "momentum15_atr_multiplier_max": 1.5,
            "fee_aware_enabled": True,
            "estimated_taker_fee_percent": 0.08,
            "estimated_slippage_percent": 0.0,
            "include_entry_fee": True,
            "include_exit_fee": True,
            "minimum_fee_coverage_multiplier": 2.0,
            "require_positive_estimated_net": True,
            "minimum_net_roi_percent": 2.0,
        },
    }

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
        "qualification": qualification,
    }

    print("UNIT 2 REQUESTED SYMBOL =", requested_symbol, flush=True)
    print("UNIT 2 MARKET DATA SYMBOL =", exchange["market_symbol"], flush=True)
    print("UNIT 2 ACTIVE SYMBOL = UNCONFIRMED", flush=True)
    print("UNIT 2 SYMBOL SWITCH MODE = AUTO_DEFERRED", flush=True)
    print("UNIT 2 SYMBOL RECONCILIATION = REQUIRED", flush=True)
    print("UNIT 2 INITIAL ENTRY MARGIN =", e0_margin, flush=True)
    print(
        "UNIT 2 TP ALLOCATION =",
        allocations["TP1"], "/",
        allocations["TP2"], "/",
        allocations["TP3"],
        flush=True
    )
    print(
        "UNIT 2 TP NET ROI =",
        roi["TP1"], "/", roi["TP2"],
        flush=True
    )
    print(
        "UNIT 2 TP3 TRAILING =",
        trailing["REF"], "/",
        trailing["MIN"], "/",
        trailing["MAX"],
        flush=True
    )
    print("UNIT 2 BACKUP MARGIN % =", backup_percent, flush=True)
    print("UNIT 2 BACKUP BUFFER MODE = ATR_DYNAMIC", flush=True)
    print("UNIT 2 EXPOSURE CAP % =", cap_percent, flush=True)
    print("UNIT 2 SYMBOL SWITCH EXECUTION = DOWNSTREAM", flush=True)
    print("UNIT 2 EXCHANGE WRITE = NONE", flush=True)
    print("FRESH RECONSTRUCTION UNIT 2 RESULT = PASS", flush=True)

    return config


# ============================================================
# UNIT 2 V15 EXECUTION AND UNIT 3 HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = fresh_reconstruction_unit_2()

FRESH_UNIT_2_OPTIMIZATION_READY = (
    isinstance(FRESH_RECONSTRUCTION_CONFIG, dict)
    and FRESH_RECONSTRUCTION_CONFIG.get(
        "execution_environment"
    ) == "DEMO"
    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get("strategy"),
        dict
    )
    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get("qualification"),
        dict
    )
    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("anti_duplicate_orders") is True
    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("max_backups") == 5
)

if not FRESH_UNIT_2_OPTIMIZATION_READY:
    raise RuntimeError("UNIT 2 V15 CONFIGURATION FAILED")

print(
    "UNIT 2 V15 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 2 V15
# UNIT 3 FOLLOWS
# ============================================================


# ============================================================
# START COMPLETE UNIT 3 V3 REPLACEMENT
# WEEX V3 LIVE MARK PRICE
# SYMBOL-SWITCH COMPATIBLE
# PRESERVES UNIT 4 SNAPSHOT CONTRACT
# ZERO INDENTATION
# ============================================================

import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request


# ============================================================
# 1. SYMBOL VALIDATION
# ============================================================

def unit_3_normalize_symbol(value):
    symbol = str(value or "").strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9]{2,25}USDT",
        symbol
    ):
        raise ValueError(
            "UNIT 3 INVALID SYMBOL: " + symbol
        )

    return symbol


# ============================================================
# 2. RESOLVE MARKET-DATA SYMBOL
#
# Requested symbol does not automatically
# become the execution symbol.
#
# Until the downstream coordinator confirms
# activation, retain the existing market
# symbol strictly for public data.
# ============================================================

def unit_3_resolve_symbol(config):

    exchange = config.get("exchange", {})

        requested = unit_3_normalize_symbol(
        exchange.get("requested_symbol")
        or os.getenv("WEEX_SYMBOL", "")
    )

    confirmed = (
        exchange.get("active_symbol_confirmed")
        is True
    )

    if confirmed:
        active = exchange.get(
            "active_symbol"
        ) or exchange.get("market_symbol")

        active = unit_3_normalize_symbol(active)

        return {
            "requested_symbol": requested,
            "market_symbol": active,
            "activation_confirmed": True,
            "market_source": "CONFIRMED_ACTIVE",
            "execution_symbol_ready": True,
        }

    # Preserve the established public-data
    # bootstrap symbol from Unit 2.
    # Do not silently promote requested ETHUSDT
    # to an executable active symbol.

    bootstrap = unit_3_normalize_symbol(
        exchange.get("market_symbol", "BTCUSDT")
    )

    return {
        "requested_symbol": requested,
        "market_symbol": bootstrap,
        "activation_confirmed": False,
        "market_source": "REQUESTED_PUBLIC_DATA_ONLY",
        "execution_symbol_ready": False,
    }


# ============================================================
# 3. MARKET RESPONSE VALIDATION
# ============================================================

def unit_3_validate_mark_payload(
    payload,
    expected_symbol,
    received_time_ms,
    max_age_ms=120000,
    future_tolerance_ms=15000
):

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE TYPE"
        )

    expected = unit_3_normalize_symbol(
        expected_symbol
    )

    actual = str(
        payload.get("symbol", "")
    ).strip().upper()

    if actual != expected:
        raise RuntimeError(
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )

    try:
        price = float(payload.get("price"))
    except (
        TypeError,
        ValueError,
        OverflowError
    ) as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET PRICE"
        ) from exc

    if not math.isfinite(price) or price <= 0:
        raise RuntimeError(
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )

    raw_timestamp = payload.get("time")

    if (
        isinstance(raw_timestamp, bool)
        or raw_timestamp is None
    ):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )

    try:
        timestamp = int(raw_timestamp)
    except (
        TypeError,
        ValueError,
        OverflowError
    ) as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET TIMESTAMP"
        ) from exc

    if timestamp <= 0:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )

    age_ms = int(received_time_ms) - timestamp

    if age_ms < -future_tolerance_ms:
        raise RuntimeError(
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE"
        )

    if age_ms > max_age_ms:
        raise RuntimeError(
            "UNIT 3 STALE MARKET DATA"
        )

    return {
        "price": price,
        "exchange_time_ms": timestamp,
        "market_age_ms": age_ms,
    }


# ============================================================
# 4. UNIT 3 DETERMINISTIC TESTS
# NO EXCHANGE REQUESTS
# ============================================================

def unit_3_validation_tests_v3():

    now_ms = 1800000000000

    sample = {
        "symbol": "ETHUSDT",
        "price": "3000.50",
        "time": now_ms - 1000,
    }

    passed = 0
    failed = 0

    def check(name, condition):
        nonlocal passed, failed

        if condition:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 3 TEST",
            name,
            "=",
            "PASS" if condition else "FAIL",
            flush=True
        )

    def rejects(payload):
        try:
            unit_3_validate_mark_payload(
                payload,
                "ETHUSDT",
                now_ms
            )
        except RuntimeError:
            return True

        return False

    valid = unit_3_validate_mark_payload(
        sample,
        "ETHUSDT",
        now_ms
    )

    check(
        "ETH SYMBOL",
        valid["price"] == 3000.50
    )

    check(
        "TIMESTAMP",
        valid["market_age_ms"] == 1000
    )

    check(
        "WRONG SYMBOL",
        rejects({
            **sample,
            "symbol": "BTCUSDT"
        })
    )

    check(
        "ZERO PRICE",
        rejects({
            **sample,
            "price": "0"
        })
    )

    check(
        "INVALID PRICE",
        rejects({
            **sample,
            "price": "nan"
        })
    )

    check(
        "STALE DATA",
        rejects({
            **sample,
            "time": now_ms - 130000
        })
    )

    check(
        "FUTURE TIMESTAMP",
        rejects({
            **sample,
            "time": now_ms + 20000
        })
    )

    check(
        "MISSING TIMESTAMP",
        rejects({
            "symbol": "ETHUSDT",
            "price": "3000.50"
        })
    )

    bootstrap = unit_3_resolve_symbol({
        "exchange": {
            "requested_symbol": "ETHUSDT",
            "market_symbol": "BTCUSDT",
            "active_symbol_confirmed": False,
        }
    })

    check(
        "UNCONFIRMED SWITCH PRESERVES BOOTSTRAP",
        bootstrap["market_symbol"] == "BTCUSDT"
        and not bootstrap["execution_symbol_ready"]
    )

    activated = unit_3_resolve_symbol({
        "exchange": {
            "requested_symbol": "ETHUSDT",
            "market_symbol": "BTCUSDT",
            "active_symbol": "ETHUSDT",
            "active_symbol_confirmed": True,
        }
    })

    check(
        "CONFIRMED SWITCH USES ETH",
        activated["market_symbol"] == "ETHUSDT"
        and activated["execution_symbol_ready"]
    )

    print(
        "UNIT 3 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 3 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 3 V3 VALIDATION FAILED"
        )

    return True


# Preserve the older test entry point.
unit_3_validation_tests_v2 = (
    unit_3_validation_tests_v3
)


# ============================================================
# 5. LIVE PUBLIC WEEX MARKET READ
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 3 V3 START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 INVALID CONFIGURATION"
        )

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE CONFIG"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 EXCHANGE NOT WEEX"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 API VERSION MISMATCH"
        )

    resolved = unit_3_resolve_symbol(config)

    requested_symbol = resolved[
        "requested_symbol"
    ]

    market_symbol = resolved[
        "market_symbol"
    ]

    activation_confirmed = resolved[
        "activation_confirmed"
    ]

    base_url = exchange.get(
        "contract_base_url",
        "https://api-contract.weex.com"
    )

    if (
        not isinstance(base_url, str)
        or not base_url.startswith(
            "https://api-contract.weex.com"
        )
        or base_url.rstrip("/")
        != "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT 3 INVALID WEEX BASE URL"
        )

    endpoint = "/capi/v3/market/symbolPrice"

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": "MARK",
    })

    url = (
        base_url.rstrip("/")
        + endpoint
        + "?"
        + query
    )

    print(
        "UNIT 3 REQUESTED SYMBOL =",
        requested_symbol,
        flush=True
    )

    print(
        "UNIT 3 MARKET DATA SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 3 SYMBOL SOURCE =",
        resolved["market_source"],
        flush=True
    )

    print(
        "UNIT 3 ACTIVE SYMBOL CONFIRMED =",
        activation_confirmed,
        flush=True
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent":
                "WEEX-Hybrid-Market-Data-V3",
        }
    )

    started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            status = response.getcode()

            body = response.read().decode(
                "utf-8"
            )

    except urllib.error.HTTPError as exc:
        print(
            "UNIT 3 HTTP ERROR =",
            exc.code,
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 MARKET HTTP FAILURE"
        ) from exc

    except urllib.error.URLError as exc:
        print(
            "UNIT 3 CONNECTION ERROR =",
            str(exc.reason),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 MARKET CONNECTION FAILURE"
        ) from exc

    received_ms = int(time.time() * 1000)

    latency_ms = round(
        (time.monotonic() - started) * 1000,
        2
    )

    if status != 200:
        raise RuntimeError(
            "UNIT 3 UNEXPECTED HTTP STATUS"
        )

    if not body:
        raise RuntimeError(
            "UNIT 3 EMPTY MARKET RESPONSE"
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET JSON"
        ) from exc

    validated = unit_3_validate_mark_payload(
        payload,
        market_symbol,
        received_ms
    )

    # ========================================================
    # PRESERVE ORIGINAL EIGHT-FIELD UNIT 4 INTERFACE
    # ========================================================

    market_snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": market_symbol,
        "price": validated["price"],
        "price_type": "MARK",
        "exchange_time_ms":
            validated["exchange_time_ms"],
        "source": "WEEX_V3_PUBLIC_MARK_PRICE",
        "read_only": True,
    }

    # Additional non-breaking metadata.
    market_snapshot.update({
        "requested_symbol": requested_symbol,
        "market_age_ms":
            validated["market_age_ms"],
        "request_latency_ms": latency_ms,
        "symbol_activation_confirmed":
            activation_confirmed,
        "execution_symbol_ready":
            resolved["execution_symbol_ready"],
        "symbol_source":
            resolved["market_source"],
    })

    print(
        "UNIT 3 HTTP STATUS =",
        status,
        flush=True
    )

    print(
        "UNIT 3 LIVE MARK SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 3 LIVE MARK PRICE =",
        validated["price"],
        flush=True
    )

    print(
        "UNIT 3 MARKET AGE MS =",
        validated["market_age_ms"],
        flush=True
    )

    print(
        "UNIT 3 REQUEST LATENCY MS =",
        latency_ms,
        flush=True
    )

    print(
        "UNIT 3 EXECUTION SYMBOL READY =",
        resolved["execution_symbol_ready"],
        flush=True
    )

    print(
        "UNIT 3 HANDOVER READY FOR UNIT 4 = TRUE",
        flush=True
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# 6. STARTUP VALIDATION
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v3()
)


# ============================================================
# 7. LIVE MARKET READ
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3 V3 REPLACEMENT
# UNIT 4 FOLLOWS
# ZERO INDENTATION
# ============================================================
