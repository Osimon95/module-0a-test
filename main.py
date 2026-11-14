
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



# ============================================================
# START COMPLETE UNIT 4 V6
# DYNAMIC WEEX MARKET ANALYSIS
# ZERO INDENTATION
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error

UNIT_4_V5_TUNING = {
    "common": {
        "direction_votes_required": 2,
        "market_age_seconds_max": 120.0,
        "candle_age_seconds_max": 120.0,
    },
    "breakout": {
        "enabled": True,
        "developing_candidate_enabled": True,
        "lookback_candles": 20,
        "proximity_atr": 0.50,
        "confirmation_atr": 0.10,
        "maximum_extension_atr": 3.0,
        "minimum_atr_percent": 0.0,
        "direction_votes_required": 2,
        "fast_momentum_minutes": 5,
        "slow_momentum_minutes": 15,
        "require_fast_momentum": True,
        "require_slow_momentum": False,
    },
    "structure": {
        "enabled": True,
        "ema_alignment_mode": "EARLY",
        "direction_votes_required": 2,
        "minimum_ema_separation_percent": 0.0,
        "pullback_tolerance_atr": 0.75,
        "allow_continuation_entry": True,
        "maximum_extension_atr": 2.0,
        "fast_momentum_minutes": 5,
        "slow_momentum_minutes": 15,
        "require_fast_momentum": True,
        "require_slow_momentum": True,
    },
    "scalp": {
        "enabled": True,
        "require_sideways_market": True,
        "range_lookback_candles": 20,
        "ema_compression_atr_max": 0.70,
        "range_atr_max": 8.0,
        "momentum_atr_max": 1.50,
        "preliminary_ema_separation_percent": 0.03,
        "preliminary_move_5m_percent": 0.015,
        "quality_threshold": 70.0,
        "minimum_fee_coverage_multiplier": 2.0,
    },
}


def unit_4_v5_number(value, name):
    if isinstance(value, bool):
        raise RuntimeError("UNIT 4 INVALID NUMBER: " + name)
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError("UNIT 4 INVALID NUMBER: " + name) from exc
    if not math.isfinite(result):
        raise RuntimeError("UNIT 4 NONFINITE NUMBER: " + name)
    return result


def unit_4_v5_positive(value, name, allow_zero=True):
    result = unit_4_v5_number(value, name)
    if result < 0 or (result == 0 and not allow_zero):
        raise RuntimeError("UNIT 4 INVALID RANGE: " + name)
    return result


def unit_4_v5_integer(value, name, minimum, maximum):
    result = unit_4_v5_number(value, name)
    if not result.is_integer() or not minimum <= result <= maximum:
        raise RuntimeError("UNIT 4 INVALID INTEGER: " + name)
    return int(result)


def unit_4_v5_ema(prices, period):
    if len(prices) < period:
        raise RuntimeError("UNIT 4 INSUFFICIENT EMA HISTORY")
    current = sum(prices[:period]) / period
    alpha = 2.0 / (period + 1.0)
    for price in prices[period:]:
        current = alpha * price + (1 - alpha) * current
    return current


def unit_4_v5_same_direction(move, direction):
    if direction == "LONG":
        return move > 0
    if direction == "SHORT":
        return move < 0
    return False


def unit_4_v5_normalize_candles(rows, market_time_ms):
    if not isinstance(rows, list):
        raise RuntimeError("UNIT 4 INVALID KLINE RESPONSE")

    candles = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 7:
            raise RuntimeError("UNIT 4 INVALID KLINE ROW")
        candle = {
            "open_time_ms": int(row[0]),
            "open": unit_4_v5_number(row[1], "OPEN"),
            "high": unit_4_v5_number(row[2], "HIGH"),
            "low": unit_4_v5_number(row[3], "LOW"),
            "close": unit_4_v5_number(row[4], "CLOSE"),
            "volume": unit_4_v5_number(row[5], "VOLUME"),
            "close_time_ms": int(row[6]),
        }
        if not (
            0 < candle["low"]
            <= min(candle["open"], candle["close"])
            <= max(candle["open"], candle["close"])
            <= candle["high"]
        ):
            raise RuntimeError("UNIT 4 INVALID OHLC DATA")
        if candle["volume"] < 0 or candle["close_time_ms"] <= candle["open_time_ms"]:
            raise RuntimeError("UNIT 4 INVALID CANDLE DATA")
        candles.append(candle)

    candles.sort(key=lambda item: item["open_time_ms"])

    for i in range(1, len(candles)):
        if (
            candles[i]["open_time_ms"] - candles[i - 1]["open_time_ms"]
        ) != 60000:
            raise RuntimeError("UNIT 4 CANDLE GAP OR DUPLICATE")

    closed = [
        candle for candle in candles
        if candle["close_time_ms"] <= market_time_ms
    ]
    if len(closed) < 200:
        raise RuntimeError("UNIT 4 INSUFFICIENT CLOSED HISTORY")
    return candles, closed


def fresh_reconstruction_unit_4():
    print("=" * 80, flush=True)
    print("FRESH RECONSTRUCTION UNIT 4 V6 START", flush=True)

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    tuning = UNIT_4_V5_TUNING

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 CONFIG MISSING")
    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 MARKET SNAPSHOT MISSING")

    exchange = config.get("exchange", {})
    qualification = config.get("qualification", {})
    safety = config.get("safety", {})

    if not all(
        isinstance(section, dict)
        for section in (exchange, qualification, safety)
    ):
        raise RuntimeError("UNIT 4 CONFIG STRUCTURE INVALID")

    # Unit 3 is authoritative for the public-data symbol.
    market_symbol = str(market.get("symbol") or "").strip().upper()

    if not market_symbol:
        raise RuntimeError("UNIT 4 MARKET SYMBOL MISSING")

    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError("UNIT 4 UNIT 3 HANDOVER INVALID")

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or safety.get("public_market_data_read_enabled") is not True
    ):
        raise RuntimeError("UNIT 4 PUBLIC MARKET CONFIG INVALID")

    b = tuning["breakout"]
    s = tuning["structure"]
    p = tuning["scalp"]
    c = tuning["common"]

    max_age = unit_4_v5_positive(
        c["market_age_seconds_max"], "MARKET AGE LIMIT", False
    )
    max_candle_age = unit_4_v5_positive(
        c["candle_age_seconds_max"], "CANDLE AGE LIMIT", False
    )

    market_time_ms = int(
        unit_4_v5_positive(
            market["exchange_time_ms"], "MARKET TIMESTAMP", False
        )
    )
    live_mark = unit_4_v5_positive(
        market["price"], "MARK PRICE", False
    )

    current_time_ms = int(time.time() * 1000)
    if not 0 <= current_time_ms - market_time_ms <= max_age * 1000:
        raise RuntimeError("UNIT 4 STALE UNIT 3 MARK PRICE")

    base_url = str(
        exchange.get("contract_base_url")
        or "https://api-contract.weex.com"
    ).rstrip("/")

    endpoint = "/capi/v3/market/markPriceKlines"
    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "interval": "1m",
        "limit": 300,
    })

    request = urllib.request.Request(
        base_url + endpoint + "?" + query,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit4-Dynamic-V6",
        }
    )

    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            http_status = response.getcode()
            payload = response.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise RuntimeError("UNIT 4 WEEX CANDLE REQUEST FAILED") from exc

    latency_ms = (time.monotonic() - started) * 1000.0

    if http_status != 200:
        raise RuntimeError("UNIT 4 WEEX HTTP STATUS NOT 200")

    try:
        rows = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError("UNIT 4 WEEX JSON INVALID") from exc

    candles, closed = unit_4_v5_normalize_candles(
        rows, market_time_ms
    )

    latest = closed[-1]
    previous = closed[-2]
    candle_age_seconds = (
        market_time_ms - latest["close_time_ms"]
    ) / 1000.0

    if not 0 <= candle_age_seconds <= max_candle_age:
        raise RuntimeError("UNIT 4 CLOSED CANDLE STALE")

    prices = [item["close"] for item in closed]
    ema19 = unit_4_v5_ema(prices, 19)
    ema50 = unit_4_v5_ema(prices, 50)
    ema100 = unit_4_v5_ema(prices, 100)
    ema200 = unit_4_v5_ema(prices, 200)


    
    latest_close = latest["close"]
    previous_close = previous["close"]
    separation = abs(ema19 - ema50) / ema50 * 100.0

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"
    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"
    else:
        ema_structure = "MIXED"

    moves = {}
    for period in (1, 5, 15, 30, 60, 120):
        reference = prices[-period - 1]
        moves[period] = (
            latest_close - reference
        ) / reference * 100.0

    true_ranges = []
    for i in range(1, len(closed)):
        candle = closed[i]
        previous_price = closed[i - 1]["close"]
        true_ranges.append(max(
            candle["high"] - candle["low"],
            abs(candle["high"] - previous_price),
            abs(candle["low"] - previous_price)
        ))

    atr14 = sum(true_ranges[-14:]) / 14.0
    if atr14 <= 0:
        raise RuntimeError("UNIT 4 ATR14 INVALID")

    atr_percent = atr14 / latest_close * 100.0

    ema_vote = (
        "LONG" if ema19 > ema50
        else "SHORT" if ema19 < ema50
        else "NONE"
    )
    momentum_sum = moves[5] + moves[15]
    momentum_vote = (
        "LONG" if momentum_sum > 0
        else "SHORT" if momentum_sum < 0
        else "NONE"
    )
    price_vote = (
        "LONG" if latest_close > ema19
        else "SHORT" if latest_close < ema19
        else "NONE"
    )

    votes = (ema_vote, momentum_vote, price_vote)
    long_votes = votes.count("LONG")
    short_votes = votes.count("SHORT")

    common_votes_required = unit_4_v5_integer(
        c["direction_votes_required"],
        "COMMON DIRECTION VOTES", 1, 3
    )

    direction = "NONE"
    if (
        long_votes >= common_votes_required
        and long_votes > short_votes
    ):
        direction = "LONG"
    elif (
        short_votes >= common_votes_required
        and short_votes > long_votes
    ):
        direction = "SHORT"

    def votes_sufficient(side, required):
        count = long_votes if side == "LONG" else short_votes
        return count >= unit_4_v5_integer(
            required, "STRATEGY DIRECTION VOTES", 1, 3
        )

    def momentum_at(period):
        period = unit_4_v5_integer(
            period, "MOMENTUM PERIOD", 1, 120
        )
        if period not in moves:
            raise RuntimeError("UNIT 4 UNSUPPORTED MOMENTUM PERIOD")
        return moves[period]

    # BREAKOUT
    breakout_lookback = unit_4_v5_integer(
        b["lookback_candles"], "BREAKOUT LOOKBACK", 2, 45
    )
    reference_candles = closed[-breakout_lookback - 1:-1]
    support = min(item["low"] for item in reference_candles)
    resistance = max(item["high"] for item in reference_candles)

    proximity = unit_4_v5_positive(
        b["proximity_atr"], "BREAKOUT PROXIMITY"
    )
    confirmation = unit_4_v5_positive(
        b["confirmation_atr"], "BREAKOUT CONFIRMATION"
    )
    breakout_max_extension = unit_4_v5_positive(
        b["maximum_extension_atr"], "BREAKOUT EXTENSION", False
    )
    breakout_atr_min = unit_4_v5_positive(
        b["minimum_atr_percent"], "BREAKOUT MIN ATR"
    )

    def breakout_eligible(side):
        fast_ok = (
            not b["require_fast_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["fast_momentum_minutes"]), side
            )
        )
        slow_ok = (
            not b["require_slow_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["slow_momentum_minutes"]), side
            )
        )
        return bool(
            b["enabled"]
            and direction == side
            and votes_sufficient(side, b["direction_votes_required"])
            and fast_ok and slow_ok
            and atr_percent >= breakout_atr_min
        )

    breakout_long_eligible = breakout_eligible("LONG")
    breakout_short_eligible = breakout_eligible("SHORT")

    long_breakout_distance = (
        latest_close - resistance
    ) / atr14
    short_breakout_distance = (
        support - latest_close
    ) / atr14

    breakout_confirmed_long = bool(
        breakout_long_eligible
        and confirmation < long_breakout_distance
        <= breakout_max_extension
    )
    breakout_confirmed_short = bool(
        breakout_short_eligible
        and confirmation < short_breakout_distance
        <= breakout_max_extension
    )

    breakout_developing_long = bool(
        b["developing_candidate_enabled"]
        and breakout_long_eligible
        and -proximity <= long_breakout_distance <= confirmation
    )
    breakout_developing_short = bool(
        b["developing_candidate_enabled"]
        and breakout_short_eligible
        and -proximity <= short_breakout_distance <= confirmation
    )

    # STRUCTURE
    alignment = str(s["ema_alignment_mode"]).upper()
    if alignment not in ("STRICT", "EARLY"):
        raise RuntimeError("UNIT 4 INVALID STRUCTURE ALIGNMENT MODE")

    structure_side = "NONE"
    if alignment == "STRICT":
        if ema19 > ema50 > ema200:
            structure_side = "LONG"
        elif ema19 < ema50 < ema200:
            structure_side = "SHORT"
    else:
        if ema19 > ema50:
            structure_side = "LONG"
        elif ema19 < ema50:
            structure_side = "SHORT"

    structure_min_separation = unit_4_v5_positive(
        s["minimum_ema_separation_percent"],
        "STRUCTURE MIN EMA SEPARATION"
    )
    structure_pullback = unit_4_v5_positive(
        s["pullback_tolerance_atr"], "STRUCTURE PULLBACK"
    )
    structure_max_extension = unit_4_v5_positive(
        s["maximum_extension_atr"],
        "STRUCTURE MAX EXTENSION", False
    )

    fast_structure_move = momentum_at(
        s["fast_momentum_minutes"]
    )
    slow_structure_move = momentum_at(
        s["slow_momentum_minutes"]
    )

    def structure_eligible(side):
        fast_ok = (
            not s["require_fast_momentum"]
            or unit_4_v5_same_direction(
                fast_structure_move, side
            )
        )
        slow_ok = (
            not s["require_slow_momentum"]
            or unit_4_v5_same_direction(
                slow_structure_move, side
            )
        )
        signed_distance = (
            latest_close - ema19
            if side == "LONG"
            else ema19 - latest_close
        ) / atr14
        pullback_ok = (
            abs(signed_distance) <= structure_pullback
        )
        continuation_ok = (
            s["allow_continuation_entry"]
            and 0 <= signed_distance <= structure_max_extension
        )
        return bool(
            s["enabled"]
            and structure_side == side
            and direction == side
            and votes_sufficient(side, s["direction_votes_required"])
            and fast_ok and slow_ok
            and separation >= structure_min_separation
            and abs(signed_distance) <= structure_max_extension
            and (pullback_ok or continuation_ok)
        )

    structure_developing_long = structure_eligible("LONG")
    structure_developing_short = structure_eligible("SHORT")

    structure_fast_confirmed = unit_4_v5_same_direction(
        fast_structure_move, structure_side
    )
    structure_slow_confirmed = unit_4_v5_same_direction(
        slow_structure_move, structure_side
    )

    # SCALP / SIDEWAYS
    scalp_lookback = unit_4_v5_integer(
        p["range_lookback_candles"], "SCALP LOOKBACK", 2, 45
    )
    scalp_history = closed[-scalp_lookback - 1:-1]
    scalp_high = max(item["high"] for item in scalp_history)
    scalp_low = min(item["low"] for item in scalp_history)

    ema_cluster = (
        max(ema19, ema50, ema100, ema200)
        - min(ema19, ema50, ema100, ema200)
    )
    compression_atr = ema_cluster / atr14
    scalp_range_atr = (scalp_high - scalp_low) / atr14
    momentum15_atr = abs(latest_close - prices[-16]) / atr14

    higher_mode_developing = any((
        breakout_confirmed_long,
        breakout_confirmed_short,
        breakout_developing_long,
        breakout_developing_short,
        structure_developing_long,
        structure_developing_short,
    ))

    sideways_candidate = bool(
        p["enabled"]
        and compression_atr <= unit_4_v5_positive(
            p["ema_compression_atr_max"], "SCALP EMA COMPRESSION"
        )
        and scalp_range_atr <= unit_4_v5_positive(
            p["range_atr_max"], "SCALP RANGE"
        )
        and momentum15_atr <= unit_4_v5_positive(
            p["momentum_atr_max"], "SCALP MOMENTUM"
        )
        and not higher_mode_developing
    )

    price_extension_atr = abs(latest_close - ema19) / atr14
    price_overextended = (
        price_extension_atr > structure_max_extension
    )

    # Preserve downstream qualification settings.
    common_cfg = qualification.setdefault("common", {})
    breakout_cfg = qualification.setdefault("breakout", {})
    structure_cfg = qualification.setdefault("structure", {})
    scalp_cfg = qualification.setdefault("scalp", {})

    common_cfg["direction_votes_required"] = common_votes_required

    breakout_cfg.update({
        "enabled": bool(b["enabled"]),
        "developing_candidate_enabled":
            bool(b["developing_candidate_enabled"]),
        "support_resistance_lookback": breakout_lookback,
        "developing_proximity_atr": proximity,
        "confirmation_distance_atr": confirmation,
        "max_price_extension_atr": breakout_max_extension,
        "minimum_atr_percent": breakout_atr_min,
        "direction_votes_required": b["direction_votes_required"],
        "fast_momentum_minutes": b["fast_momentum_minutes"],
        "slow_momentum_minutes": b["slow_momentum_minutes"],
        "require_fast_momentum": b["require_fast_momentum"],
        "require_slow_momentum": b["require_slow_momentum"],
    })

    structure_cfg.update({
        "enabled": bool(s["enabled"]),
        "ema_alignment_mode": alignment,
        "direction_votes_required": s["direction_votes_required"],
        "minimum_ema_separation_percent":
            structure_min_separation,
        "pullback_tolerance_atr": structure_pullback,
        "allow_continuation_entry":
            bool(s["allow_continuation_entry"]),
        "max_price_extension_atr": structure_max_extension,
        "fast_momentum_minutes": s["fast_momentum_minutes"],
        "slow_momentum_minutes": s["slow_momentum_minutes"],
        "require_fast_momentum": s["require_fast_momentum"],
        "require_slow_momentum": s["require_slow_momentum"],
    })

    scalp_cfg.update({
        "enabled": bool(p["enabled"]),
        "require_sideways_market":
            bool(p["require_sideways_market"]),
        "ema_compression_atr_max": p["ema_compression_atr_max"],
        "range20_atr_max": p["range_atr_max"],
        "momentum15_atr_multiplier_max": p["momentum_atr_max"],
        "preliminary_ema_separation_percent":
            p["preliminary_ema_separation_percent"],
        "preliminary_move_5m_percent":
            p["preliminary_move_5m_percent"],
        "quality_threshold": p["quality_threshold"],
        "minimum_fee_coverage_multiplier":
            p["minimum_fee_coverage_multiplier"],
    })

    # Unit 5 and downstream handover.
    snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": market_symbol,
        "interval": "1m",
        "price_type": "MARK",
        "live_mark_price": live_mark,
        "previous_close": previous_close,
        "latest_close": latest_close,
        "latest_open_time_ms": latest["open_time_ms"],
        "latest_close_time_ms": latest["close_time_ms"],
        "exchange_time_ms": market_time_ms,
        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,
        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,
        "short_term_move_pct": moves[1],
        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],
        "recent_closed_klines": [
            dict(item) for item in closed[-60:]
        ],
        "candle_count": len(candles),
        "closed_candle_count": len(closed),
        "newest_returned_candle_closed":
            candles[-1]["close_time_ms"] <= market_time_ms,
        "source": "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",
        "atr14": atr14,
        "atr_percent": atr_percent,
        "support20": support,
        "resistance20": resistance,
        "range20_atr_ratio": (resistance - support) / atr14,
        "near_resistance":
            latest_close >= resistance - proximity * atr14,
        "near_support":
            latest_close <= support + proximity * atr14,
        "breakout_confirmed_long": breakout_confirmed_long,
        "breakout_confirmed_short": breakout_confirmed_short,
        "breakout_developing_long": breakout_developing_long,
        "breakout_developing_short": breakout_developing_short,
        "structure_developing_long": structure_developing_long,
        "structure_developing_short": structure_developing_short,
        "structure_trend_direction": structure_side,
        "structure_ema_alignment_mode": alignment,
        "structure_momentum_fast_confirmed":
            structure_fast_confirmed,
        "structure_momentum_slow_confirmed":
            structure_slow_confirmed,
        "sideways_candidate": sideways_candidate,
        "direction_long_votes": long_votes,
        "direction_short_votes": short_votes,
        "direction_evidence": direction,
        "ema_cluster_height": ema_cluster,
        "ema_compression_atr": compression_atr,
        "scalp_range_atr": scalp_range_atr,
        "scalp_momentum_atr": momentum15_atr,
        "scalp_preliminary_ema_min_pct":
            p["preliminary_ema_separation_percent"],
        "scalp_preliminary_move_min_pct":
            p["preliminary_move_5m_percent"],
        "price_extension_cluster": price_extension_atr,
        "price_overextended": price_overextended,
        "strategy_evidence_version": "U4_HYBRID_V2",
        "qualification_tuning_revision":
            "UNIT4_V6_DYNAMIC_SYMBOL",
        "qualification_settings": {
            "breakout_lookback": breakout_lookback,
            "breakout_proximity_atr": proximity,
            "breakout_confirmation_atr": confirmation,
            "structure_pullback_atr": structure_pullback,
            "structure_max_extension_atr":
                structure_max_extension,
            "structure_ema_alignment_mode": alignment,
            "scalp_compression_atr":
                p["ema_compression_atr_max"],
            "scalp_range_atr": p["range_atr_max"],
            "scalp_momentum_atr": p["momentum_atr_max"],
        },
        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
    }

    print("UNIT 4 MARKET SYMBOL =", market_symbol, flush=True)
    print("UNIT 4 HTTP STATUS =", http_status, flush=True)
    print("UNIT 4 REQUEST LATENCY MS =", round(latency_ms, 2), flush=True)
    print("UNIT 4 CLOSED CANDLES =", len(closed), flush=True)
    print("UNIT 4 ATR14 =", round(atr14, 6), flush=True)
    print("UNIT 4 EMA19 =", round(ema19, 6), flush=True)
    print("UNIT 4 EMA50 =", round(ema50, 6), flush=True)
    print("UNIT 4 EMA100 =", round(ema100, 6), flush=True)
    print("UNIT 4 EMA200 =", round(ema200, 6), flush=True)
    print("UNIT 4 DIRECTION =", direction, flush=True)
    print(
        "UNIT 4 DIRECTION VOTES =",
        long_votes, "/", short_votes, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMED LONG =",
        breakout_confirmed_long, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMED SHORT =",
        breakout_confirmed_short, flush=True
    )
    print(
        "UNIT 4 STRUCTURE TREND SIDE =",
        structure_side, flush=True
    )
    print(
        "UNIT 4 SCALP SIDEWAYS =",
        sideways_candidate, flush=True
    )
    print(
        "UNIT 4 TO UNIT 5 HANDOVER = READY",
        flush=True
    )
    print("UNIT 4 EXCHANGE WRITE = NONE", flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return snapshot


FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)

# ============================================================
# END COMPLETE UNIT 4 V6
# UNIT 5 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 5 V10
# DYNAMIC HYBRID CLASSIFICATION AND FEE COVERAGE
# UNIT 4 -> UNIT 5 -> UNIT 6
# ============================================================

import math


def unit_5_v10_number(value, name):
    if isinstance(value, bool):
        raise RuntimeError("UNIT 5 INVALID " + name)
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError("UNIT 5 INVALID " + name) from exc
    if not math.isfinite(result):
        raise RuntimeError("UNIT 5 NONFINITE " + name)
    return result


def unit_5_v10_direction(value):
    if value > 0:
        return "LONG"
    if value < 0:
        return "SHORT"
    return "NONE"


def unit_5_v10_side_matches(value, side):
    if side == "LONG":
        return value > 0
    if side == "SHORT":
        return value < 0
    return False


def unit_5_v10_settings(config, group):
    qualification = config.get("qualification", {})
    if not isinstance(qualification, dict):
        return {}
    section = qualification.get(group, {})
    return section if isinstance(section, dict) else {}


def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot
):
    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 5 V10 START",
        flush=True
    )

    config = unit_2_config
    analysis = unit_4_snapshot

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 5 CONFIG UNAVAILABLE")
    if not isinstance(analysis, dict):
        raise RuntimeError("UNIT 5 ANALYSIS UNAVAILABLE")

    common = unit_5_v10_settings(config, "common")
    b = unit_5_v10_settings(config, "breakout")
    s = unit_5_v10_settings(config, "structure")
    p = unit_5_v10_settings(config, "scalp")

    symbol = str(
        analysis.get("symbol") or ""
    ).strip().upper()

    if not symbol:
        raise RuntimeError("UNIT 5 SYMBOL UNAVAILABLE")

    def n(key, default=None):
        value = analysis.get(key, default)
        if value is None:
            raise RuntimeError("UNIT 5 MISSING " + key)
        return unit_5_v10_number(value, key)

    def setting(section, key, default):
        return unit_5_v10_number(
            section.get(key, default), key
        )

    def enabled(section):
        return bool(section.get("enabled", True))

    price = n("live_mark_price")
    previous_close = n("previous_close")
    latest_close = n("latest_close")

    ema19 = n("ema19")
    ema50 = n("ema50")
    ema200 = n("ema200")
    atr14 = n("atr14")

    separation = n("ema19_50_separation_pct", 0)

    moves = {
        period: n("move_%sm_pct" % period, 0)
        for period in (1, 5, 15, 30, 60, 120)
    }

    directions = {
        period: unit_5_v10_direction(value)
        for period, value in moves.items()
    }

    long_votes = int(n("direction_long_votes", 0))
    short_votes = int(n("direction_short_votes", 0))

    direction_evidence = str(
        analysis.get("direction_evidence", "NONE")
    ).upper()

    if direction_evidence not in (
        "LONG", "SHORT", "NONE"
    ):
        direction_evidence = "NONE"

    ema_direction = unit_5_v10_direction(
        ema19 - ema50
    )

    structure_direction = str(
        analysis.get(
            "structure_trend_direction", "NONE"
        )
    ).upper()

    if structure_direction not in ("LONG", "SHORT"):
        structure_direction = "NONE"

    if structure_direction == "NONE":
        structure_direction = ema_direction

    structure_move = moves[15]
    breakout_move = moves[5]
    scalp_move = moves[1]

    scalp_direction = directions[1]

    if scalp_direction == "NONE":
        scalp_direction = directions[5]

    breakout_long = bool(
        analysis.get(
            "breakout_confirmed_long", False
        )
    )
    breakout_short = bool(
        analysis.get(
            "breakout_confirmed_short", False
        )
    )

    developing_long = bool(
        analysis.get(
            "breakout_developing_long", False
        )
    )
    developing_short = bool(
        analysis.get(
            "breakout_developing_short", False
        )
    )

    structure_long = bool(
        analysis.get(
            "structure_developing_long", False
        )
    )
    structure_short = bool(
        analysis.get(
            "structure_developing_short", False
        )
    )

    sideways = bool(
        analysis.get("sideways_candidate", False)
    )

    higher_mode_developing = any((
        breakout_long,
        breakout_short,
        developing_long,
        developing_short,
        structure_long,
        structure_short
    ))

    # ========================================================
    # BREAKOUT CLASSIFICATION
    # ========================================================

    if breakout_long or developing_long:
        breakout_direction = "LONG"
    elif breakout_short or developing_short:
        breakout_direction = "SHORT"
    else:
        breakout_direction = "NONE"

    required_breakout_votes = int(
        setting(
            b, "direction_votes_required", 2
        )
    )

    required_structure_votes = int(
        setting(
            s, "direction_votes_required", 2
        )
    )

    def votes_ok(side, minimum):
        count = (
            long_votes if side == "LONG"
            else short_votes
        )
        return count >= minimum

    def momentum_ok(section, side):
        fast_period = int(
            setting(
                section,
                "fast_momentum_minutes",
                5
            )
        )
        slow_period = int(
            setting(
                section,
                "slow_momentum_minutes",
                15
            )
        )

        fast = moves.get(
            fast_period, moves[5]
        )
        slow = moves.get(
            slow_period, moves[15]
        )

        fast_required = bool(
            section.get(
                "require_fast_momentum", True
            )
        )
        slow_required = bool(
            section.get(
                "require_slow_momentum", False
            )
        )

        return (
            (
                not fast_required
                or unit_5_v10_side_matches(
                    fast, side
                )
            )
            and
            (
                not slow_required
                or unit_5_v10_side_matches(
                    slow, side
                )
            )
        )

    breakout_ready = bool(
        enabled(b)
        and breakout_direction != "NONE"
        and (
            (
                breakout_direction == "LONG"
                and breakout_long
            )
            or
            (
                breakout_direction == "SHORT"
                and breakout_short
            )
        )
        and votes_ok(
            breakout_direction,
            required_breakout_votes
        )
        and momentum_ok(
            b, breakout_direction
        )
    )

    breakout_developing = bool(
        enabled(b)
        and not breakout_ready
        and breakout_direction != "NONE"
        and (
            developing_long
            or developing_short
            or breakout_long
            or breakout_short
        )
    )

    # ========================================================
    # STRUCTURE CLASSIFICATION
    # ========================================================

    structure_candidate = bool(
        enabled(s)
        and (
            structure_long
            or structure_short
        )
    )

    structure_ready = bool(
        structure_candidate
        and structure_direction != "NONE"
        and votes_ok(
            structure_direction,
            required_structure_votes
        )
        and momentum_ok(
            s, structure_direction
        )
        and not bool(
            analysis.get(
                "price_overextended", False
            )
        )
    )

    structure_developing = bool(
        structure_candidate
        and not structure_ready
    )

    # ========================================================
    # SCALP CLASSIFICATION
    # ========================================================

    scalp_quality_minimum = setting(
        p, "quality_threshold", 70
    )

    price_weight = setting(
        p,
        "price_action_weight_percent",
        50
    )

    price_weight = max(
        0.0, min(100.0, price_weight)
    )

    atr_percent = n(
        "atr_percent", 0.01
    )

    momentum_strength = min(
        100.0,
        abs(moves[5]) / max(
            atr_percent, 0.000001
        ) * 50.0
    )

    ema_strength = min(
        100.0,
        separation / max(
            setting(
                p,
                "preliminary_ema_separation_percent",
                0.03
            ),
            0.000001
        ) * 50.0
    )

    scalp_quality = (
        momentum_strength
        * price_weight / 100.0
        + ema_strength
        * (100.0 - price_weight) / 100.0
    )

    scalp_quality = min(
        100.0, scalp_quality
    )

    scalp_ready = bool(
        enabled(p)
        and (
            sideways
            or not bool(
                p.get(
                    "require_sideways_market",
                    True
                )
            )
        )
        and not higher_mode_developing
        and scalp_direction != "NONE"
        and scalp_quality
            >= scalp_quality_minimum
    )

    # ========================================================
    # FEE CONFIGURATION
    # NO PREMATURE FEE COVERAGE CALCULATION
    # ========================================================

    fee_per_side = setting(
        p,
        "taker_fee_percent_per_side",
        0.08
    )

    round_trip_fee = (
        fee_per_side * 2.0
    )

    fee_multiplier = setting(
        p,
        "minimum_fee_coverage_multiplier",
        2.0
    )

    required_fee_coverage = (
        round_trip_fee * fee_multiplier
    )

    # ========================================================
    # HYBRID CANDIDATE SELECTION
    # ========================================================

    priority = common.get(
        "mode_priority",
        (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP"
        )
    )

    if isinstance(priority, str):
        priority = [
            item.strip().upper()
            for item in priority.split(",")
            if item.strip()
        ]

    candidate_mode = "NONE"
    candidate_stage = "REJECTED"
    direction = "NONE"
    qualified = False
    reason = "NO_QUALIFIED_CANDIDATE"

    # Prefer qualified candidates before developing ones.
    # This prevents an unfinished breakout from suppressing
    # an already-qualified structure signal.

    for mode in priority:
        mode = str(mode).upper()

        if mode == "BREAKOUT" and breakout_ready:
            candidate_mode = "BREAKOUT"
            candidate_stage = "QUALIFIED"
            direction = breakout_direction
            qualified = True
            reason = "BREAKOUT_CONFIRMED"
            break

        elif mode == "STRUCTURE" and structure_ready:
            candidate_mode = "STRUCTURE"
            candidate_stage = "QUALIFIED"
            direction = structure_direction
            qualified = True
            reason = "STRUCTURE_CONFIRMED"
            break

        elif mode == "SCALP" and scalp_ready:
            candidate_mode = "SCALP"
            candidate_stage = "PENDING_UNIT_6"
            direction = scalp_direction
            reason = "SCALP_QUALITY_PENDING_UNIT_6"
            break

    if candidate_mode == "NONE":

        if breakout_developing:
            candidate_mode = "BREAKOUT"
            candidate_stage = "DEVELOPING"
            direction = breakout_direction
            reason = "BREAKOUT_DEVELOPING"

        elif structure_developing:
            candidate_mode = "STRUCTURE"
            candidate_stage = "DEVELOPING"
            direction = structure_direction
            reason = "STRUCTURE_DEVELOPING"

        elif enabled(p) and not sideways:
            reason = "SCALP_NOT_SIDEWAYS_MARKET"

        elif enabled(p):
            reason = "SCALP_QUALIFICATION_PENDING"

    active_mode = (
        candidate_mode
        if qualified
        else "NONE"
    )

    # ========================================================
    # CORRECTED MODE-SPECIFIC FEE COVERAGE
    # ========================================================

    if candidate_mode == "BREAKOUT":
        estimated_move = abs(
            breakout_move
        )

    elif candidate_mode == "STRUCTURE":
        estimated_move = abs(
            structure_move
        )

    elif candidate_mode == "SCALP":
        estimated_move = abs(
            scalp_move
        )

    else:
        estimated_move = 0.0

    fee_coverage = bool(
        estimated_move
        >= required_fee_coverage
    )

    estimated_fee_surplus = (
        estimated_move - round_trip_fee
    )

    fee_coverage_ratio = (
        estimated_move / round_trip_fee
        if round_trip_fee > 0
        else 0.0
    )

    # Fee coverage is informational here.
    # Unit 6 may apply its own adjustable admission rules.
    # No qualified candidate is cancelled in Unit 5 solely
    # because this historical movement estimate is low.

    # ========================================================
    # ORIGINAL 42-FIELD HANDOVER
    # ========================================================

    short_move = moves[1]

    ema_structure = analysis.get(
        "ema_structure", "MIXED"
    )

    candidate = {
        "symbol": symbol,
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": reason,
        "live_mark_price": price,
        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,
        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,
        "ema_direction": ema_direction,
        "momentum_direction": directions[1],
        "direction_agreement": (
            structure_direction != "NONE"
        ),
        "short_term_move_pct": short_move,
        "absolute_short_term_move_pct": abs(
            short_move
        ),
        "previous_close": previous_close,
        "latest_close": latest_close,
        "price_above_ema19": price > ema19,
        "price_above_ema50": price > ema50,
        "price_above_ema200": price > ema200,
        "latest_close_above_previous": (
            latest_close > previous_close
        ),
        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],
        "momentum_1m_direction": directions[1],
        "momentum_5m_direction": directions[5],
        "momentum_15m_direction": directions[15],
        "momentum_30m_direction": directions[30],
        "momentum_60m_direction": directions[60],
        "momentum_120m_direction": directions[120],
        "scalp_direction": scalp_direction,
        "scalp_move_pct": scalp_move,
        "scalp_1m_support": (
            unit_5_v10_side_matches(
                moves[1], scalp_direction
            )
        ),
        "structure_direction": structure_direction,
        "structure_move_pct": structure_move,
        "breakout_direction": breakout_direction,
        "breakout_move_pct": breakout_move,
        "breakout_fast_support": (
            momentum_ok(
                b, breakout_direction
            )
            if breakout_direction != "NONE"
            else False
        ),
    }

    # ========================================================
    # EXTENDED UNIT 6 HANDOVER
    # ========================================================

    candidate.update({
        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,
        "higher_mode_developing":
            higher_mode_developing,
        "breakout_candidate": bool(
            breakout_ready
            or breakout_developing
        ),
        "structure_candidate":
            structure_candidate,
        "breakout_ready": breakout_ready,
        "structure_ready": structure_ready,
        "scalp_ready": scalp_ready,
        "sideways_context": sideways,
        "direction_evidence":
            direction_evidence,
        "scalp_quality_minimum":
            scalp_quality_minimum,
        "scalp_quality_score":
            scalp_quality,
        "scalp_price_weight_percent":
            price_weight,
        "estimated_round_trip_fee_pct":
            round_trip_fee,
        "scalp_minimum_fee_coverage":
            fee_multiplier,
        "fee_coverage_pass":
            fee_coverage,
        "estimated_move_percent":
            estimated_move,
        "required_fee_coverage_percent":
            required_fee_coverage,
        "estimated_fee_surplus_percent":
            estimated_fee_surplus,
        "fee_coverage_ratio":
            fee_coverage_ratio,
        "fee_coverage_mode":
            candidate_mode,
        "fee_coverage_policy":
            "DIAGNOSTIC_ONLY",
        "atr14": atr14,
        "candle_data_fresh": True,
        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
        "strategy_evidence_version":
            "U5_HYBRID_ADJUSTABLE_V3",
        "unit_4_evidence_version":
            analysis.get(
                "strategy_evidence_version",
                "U4_HYBRID_V2"
            ),
        "qualification_tuning_revision":
            "UNIT5_V10_DYNAMIC",
        "classification_revision":
            "V10_DYNAMIC",
        "candidate_protected": (
            candidate_stage == "DEVELOPING"
        ),
        "classification_source":
            "UNIT5_V10_DYNAMIC",
        "original_unit5_qualified":
            qualified,
        "symbol_source":
            "UNIT4_ANALYSIS_SNAPSHOT",
        "unit_4_qualification_revision":
            analysis.get(
                "qualification_tuning_revision"
            ),
        "execution_symbol_ready":
            bool(
                analysis.get(
                    "execution_symbol_ready",
                    False
                )
            ),
    })

    exchange_time = analysis.get(
        "exchange_time_ms"
    )
    close_time = analysis.get(
        "latest_close_time_ms"
    )

    if exchange_time is not None and close_time is not None:
        candidate["candidate_age_seconds"] = (
            unit_5_v10_number(
                exchange_time, "exchange_time_ms"
            )
            - unit_5_v10_number(
                close_time, "latest_close_time_ms"
            )
        ) / 1000.0
    else:
        candidate["candidate_age_seconds"] = None

    # ========================================================
    # UNIT 5 EXECUTION REPORT
    # ========================================================

    print(
        "UNIT 5 MARKET SYMBOL =",
        symbol, flush=True
    )
    print(
        "UNIT 5 MODE =",
        candidate_mode, flush=True
    )
    print(
        "UNIT 5 STAGE =",
        candidate_stage, flush=True
    )
    print(
        "UNIT 5 DIRECTION =",
        direction, flush=True
    )
    print(
        "UNIT 5 QUALIFIED =",
        qualified, flush=True
    )
    print(
        "UNIT 5 REASON =",
        reason, flush=True
    )
    print(
        "UNIT 5 BREAKOUT READY =",
        breakout_ready, flush=True
    )
    print(
        "UNIT 5 STRUCTURE READY =",
        structure_ready, flush=True
    )
    print(
        "UNIT 5 SCALP READY =",
        scalp_ready, flush=True
    )
    print(
        "UNIT 5 FEE COVERAGE MODE =",
        candidate_mode, flush=True
    )
    print(
        "UNIT 5 ESTIMATED MOVE % =",
        round(estimated_move, 6),
        flush=True
    )
    print(
        "UNIT 5 ROUND TRIP FEE % =",
        round(round_trip_fee, 6),
        flush=True
    )
    print(
        "UNIT 5 REQUIRED COVERAGE % =",
        round(required_fee_coverage, 6),
        flush=True
    )
    print(
        "UNIT 5 FEE COVERAGE =",
        fee_coverage, flush=True
    )
    print(
        "UNIT 5 FEE COVERAGE POLICY =",
        "DIAGNOSTIC_ONLY",
        flush=True
    )
    print(
        "UNIT 5 TO UNIT 6 HANDOVER = READY",
        flush=True
    )
    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return candidate


# ============================================================
# UNIT 5 DETERMINISTIC VALIDATION
# ============================================================

def unit_5_validation_v10():
    config = {
        "qualification": {
            "common": {
                "mode_priority": (
                    "BREAKOUT",
                    "STRUCTURE",
                    "SCALP"
                )
            },
            "breakout": {
                "enabled": True
            },
            "structure": {
                "enabled": True
            },
            "scalp": {
                "enabled": True
            }
        }
    }

    snapshot = {
        "symbol": "ETHUSDT",
        "live_mark_price": 2000.0,
        "previous_close": 1999.0,
        "latest_close": 2000.0,
        "ema19": 1998.0,
        "ema50": 1995.0,
        "ema200": 1980.0,
        "atr14": 5.0,
        "atr_percent": 0.25,
        "ema19_50_separation_pct": 0.15,
        "move_1m_pct": 0.05,
        "move_5m_pct": 0.20,
        "move_15m_pct": 0.40,
        "move_30m_pct": 0.50,
        "move_60m_pct": 0.80,
        "move_120m_pct": 1.0,
        "direction_long_votes": 3,
        "direction_short_votes": 0,
        "direction_evidence": "LONG",
        "structure_trend_direction": "LONG",
        "structure_developing_long": True,
        "structure_developing_short": False,
        "breakout_confirmed_long": False,
        "breakout_confirmed_short": False,
        "breakout_developing_long": False,
        "breakout_developing_short": False,
        "sideways_candidate": False,
        "price_overextended": False,
        "exchange_time_ms": 120000,
        "latest_close_time_ms": 60000,
        "strategy_evidence_version":
            "U4_HYBRID_V2",
        "qualification_tuning_revision":
            "UNIT4_V6_DYNAMIC_SYMBOL",
    }

    result = fresh_reconstruction_unit_5(
        config, snapshot
    )

    return bool(
        result["symbol"] == "ETHUSDT"
        and result["candidate_mode"] == "STRUCTURE"
        and result["candidate_stage"] == "QUALIFIED"
        and result["direction"] == "LONG"
        and result["read_only"] is True
        and result["trade_authorized"] is False
        and result["fee_coverage_mode"] == "STRUCTURE"
        and result["estimated_move_percent"] == 0.40
        and result["fee_coverage_pass"] is True
        and result["strategy_evidence_version"]
            == "U5_HYBRID_ADJUSTABLE_V3"
    )


FRESH_UNIT_5_VALIDATION_READY = (
    unit_5_validation_v10()
)

if not FRESH_UNIT_5_VALIDATION_READY:
    raise RuntimeError(
        "UNIT 5 V10 VALIDATION FAILED"
    )

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
)

# ============================================================
# END COMPLETE UNIT 5 V10
# UNIT 6 FOLLOWS AT ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 6 V11 REPLACEMENT
# DYNAMIC HYBRID SIGNAL + NET PROFIT ASSESSMENT
# UNIT 4 V6 -> UNIT 5 V10 -> UNIT 6 -> UNIT 7
# NO EXCHANGE ORDERS IN THIS UNIT
# ============================================================

import os
import math
import copy


def unit_6_v11_number(value, name, default=None):
    if value is None:
        value = default
    if isinstance(value, bool):
        raise ValueError("UNIT 6 INVALID " + name)
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            "UNIT 6 INVALID " + name
        ) from exc
    if not math.isfinite(value):
        raise ValueError(
            "UNIT 6 NONFINITE " + name
        )
    return value


def unit_6_v11_side(value):
    if value > 0:
        return "LONG"
    if value < 0:
        return "SHORT"
    return "NONE"


def unit_6_v11_clamp(value, low, high):
    return max(low, min(high, value))


def unit_6_v11_env_number(name, default):
    return unit_6_v11_number(
        os.getenv(name, str(default)),
        name
    )


def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate
):
    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 6 V11 START",
        flush=True
    )

    if not all(isinstance(x, dict) for x in (
        unit_2_config,
        unit_4_analysis,
        unit_5_candidate
    )):
        raise RuntimeError(
            "UNIT 6 INVALID HANDOVER INPUT"
        )

    config = unit_2_config
    analysis = unit_4_analysis
    candidate = unit_5_candidate

    strategy = config.get("strategy", {})
    qualification = config.get(
        "qualification", {}
    )
    scalp = qualification.get("scalp", {})

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 6 STRATEGY INVALID"
        )
    if not isinstance(qualification, dict):
        qualification = {}
    if not isinstance(scalp, dict):
        scalp = {}

    symbol = str(
        candidate.get("symbol", "")
    ).strip().upper()

    analysis_symbol = str(
        analysis.get("symbol", "")
    ).strip().upper()

    if not symbol or symbol != analysis_symbol:
        raise RuntimeError(
            "UNIT 6 MARKET SYMBOL MISMATCH"
        )

    def a(key, default=None):
        return unit_6_v11_number(
            analysis.get(key), key, default
        )

    def c(key, default=None):
        return unit_6_v11_number(
            candidate.get(key), key, default
        )

    price = a("latest_close")
    mark = a("live_mark_price")
    ema19 = a("ema19")
    ema50 = a("ema50")
    ema100 = a("ema100")
    ema200 = a("ema200")
    atr = a("atr14")

    if min(
        price, mark, ema19, ema50,
        ema100, ema200, atr
    ) <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID MARKET VALUES"
        )

    atr_pct = atr / mark * 100.0

    move_1m = a("move_1m_pct", 0)
    move_5m = a("move_5m_pct", 0)
    move_15m = a("move_15m_pct", 0)

    # ========================================================
    # 6.1 CANDIDATE CLASSIFICATION
    # ========================================================

    mode = str(
        candidate.get(
            "candidate_mode", "NONE"
        )
    ).upper()

    stage = str(
        candidate.get(
            "candidate_stage", "REJECTED"
        )
    ).upper()

    side = str(
        candidate.get(
            "direction", "NONE"
        )
    ).upper()

    valid_modes = (
        "NONE", "BREAKOUT",
        "STRUCTURE", "SCALP"
    )

    if mode not in valid_modes:
        raise RuntimeError(
            "UNIT 6 INVALID STRATEGY MODE"
        )

    if side not in (
        "NONE", "LONG", "SHORT"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID DIRECTION"
        )

    breakout_ready = bool(
        candidate.get(
            "breakout_ready", False
        )
    )

    structure_ready = bool(
        candidate.get(
            "structure_ready", False
        )
    )

    scalp_ready = bool(
        candidate.get(
            "scalp_ready", False
        )
    )

    higher_developing = bool(
        candidate.get(
            "higher_mode_developing", False
        )
    )

    market_confirmed = bool(
        candidate.get("qualified", False)
        and stage == "QUALIFIED"
        and side in ("LONG", "SHORT")
        and (
            (mode == "BREAKOUT" and breakout_ready)
            or
            (mode == "STRUCTURE" and structure_ready)
        )
    )

    # ========================================================
    # 6.2 FRESHNESS
    # ========================================================

    max_age = unit_6_v11_number(
        config.get(
            "market_data_policy", {}
        ).get(
            "max_market_age_seconds", 120
        ),
        "MAX_MARKET_AGE"
    )

    age = candidate.get(
        "candidate_age_seconds"
    )

    if age is None:
        age_ok = False
        age_value = None
    else:
        age_value = unit_6_v11_number(
            age, "CANDIDATE_AGE"
        )
        age_ok = (
            0 <= age_value <= max_age
        )

    fresh = bool(
        candidate.get(
            "candle_data_fresh", True
        )
        and age_ok
    )

    # ========================================================
    # 6.3 SCALP PERSISTENCE AND QUALITY
    # ========================================================

    scalp_side = str(
        candidate.get(
            "scalp_direction",
            candidate.get(
                "scalp_direction_candidate",
                "NONE"
            )
        )
    ).upper()

    if scalp_side not in (
        "LONG", "SHORT", "NONE"
    ):
        scalp_side = "NONE"

    directions = (
        unit_6_v11_side(move_1m),
        unit_6_v11_side(move_5m),
        unit_6_v11_side(move_15m)
    )

    persistence_window = 3

    persistence_required = int(
        unit_6_v11_number(
            scalp.get(
                "persistence_required", 2
            ),
            "PERSISTENCE_REQUIRED"
        )
    )

    persistence_required = max(
        1, min(3, persistence_required)
    )

    confirmations = sum(
        d == scalp_side
        for d in directions
    ) if scalp_side != "NONE" else 0

    persistence_pass = (
        confirmations >= persistence_required
    )

    sideways = bool(
        analysis.get(
            "sideways_candidate", False
        )
    )

    sideways_required = bool(
        scalp.get(
            "require_sideways_market", True
        )
    )

    sideways_pass = (
        sideways or not sideways_required
    )

    momentum_conflict = bool(
        scalp_side != "NONE"
        and directions[1] not in (
            scalp_side, "NONE"
        )
    )

    ema_separation_pct = (
        abs(ema19 - ema50) / ema50 * 100
    )

    compression_atr = a(
        "ema_compression_atr",
        abs(ema19 - ema50) / atr
    )

    compression_limit = unit_6_v11_number(
        scalp.get(
            "ema_compression_atr_max", 0.7
        ),
        "COMPRESSION_LIMIT"
    )

    ema_compressed = (
        compression_atr <= compression_limit
    )

    extension_atr = (
        abs(price - ema19) / atr
    )

    spike_ratio = (
        abs(move_1m)
        / max(
            abs(move_5m) / 5.0,
            0.000001
        )
    )

    extreme_extension = (
        extension_atr > 1.5
    )
    extreme_spike = spike_ratio > 2.0
    late_impulse = bool(
        extreme_extension and extreme_spike
    )

    price_action_score = 0.0
    persistence_score = 0.0
    location_score = 0.0
    ema_score = 0.0
    volatility_score = 0.0

    if scalp_side in ("LONG", "SHORT"):

        if directions[1] == scalp_side:
            price_action_score += 15
        if directions[0] == scalp_side:
            price_action_score += 10

        min_move = unit_6_v11_number(
            scalp.get(
                "preliminary_move_5m_percent",
                0.015
            ),
            "MIN_SCALP_MOVE"
        )

        if abs(move_5m) >= min_move:
            price_action_score += 5

        persistence_score = (
            20.0 * confirmations / 3.0
        )

        if (
            (scalp_side == "LONG" and price >= ema19)
            or
            (scalp_side == "SHORT" and price <= ema19)
        ):
            location_score += 10

        if (
            (scalp_side == "LONG" and price >= ema100)
            or
            (scalp_side == "SHORT" and price <= ema100)
        ):
            location_score += 5

        if ema_compressed:
            ema_score += 10

        if (
            (scalp_side == "LONG" and ema19 >= ema50)
            or
            (scalp_side == "SHORT" and ema19 <= ema50)
        ):
            ema_score += 5

        if not extreme_extension:
            volatility_score += 10
        if not extreme_spike:
            volatility_score += 5
        if not late_impulse:
            volatility_score += 5

    quality_score = round(
        unit_6_v11_clamp(
            price_action_score
            + persistence_score
            + location_score
            + ema_score
            + volatility_score,
            0, 100
        ),
        2
    )

    quality_minimum = unit_6_v11_number(
        scalp.get(
            "quality_threshold", 70
        ),
        "QUALITY_MINIMUM"
    )

    quality_pass = (
        quality_score >= quality_minimum
    )

    quality_details = {
        "price_action_score":
            price_action_score,
        "persistence_score":
            round(persistence_score, 2),
        "ema_location_score":
            location_score,
        "ema_quality_score":
            ema_score,
        "volatility_score":
            volatility_score,
        "extreme_extension":
            extreme_extension,
        "extreme_spike":
            extreme_spike,
        "late_impulse":
            late_impulse,
        "ema_separation_pct":
            ema_separation_pct
    }

    scalp_market_confirmed = bool(
        mode == "SCALP"
        and stage == "PENDING_UNIT_6"
        and scalp_ready
        and scalp_side in ("LONG", "SHORT")
        and not higher_developing
        and sideways_pass
        and persistence_pass
        and not momentum_conflict
        and not late_impulse
        and quality_pass
    )

    if scalp_market_confirmed:
        market_confirmed = True
        side = scalp_side

    # ========================================================
    # 6.4 ADJUSTABLE LEVERAGE
    # READ CONFIGURATION, NEVER MUTATE WEEX LEVERAGE
    # ========================================================

    leverage_key = (
        "WEEX_LEVERAGE_LONG"
        if side == "LONG"
        else "WEEX_LEVERAGE_SHORT"
        if side == "SHORT"
        else None
    )

    leverage = None
    leverage_ready = False

    if leverage_key is not None:
        raw_leverage = os.getenv(
            leverage_key
        )

        if raw_leverage is not None:
            leverage = unit_6_v11_number(
                raw_leverage, leverage_key
            )
            leverage_ready = (
                0 < leverage <= 200
            )

    # ========================================================
    # 6.5 CONFIGURED NET ROI TARGETS
    # ========================================================

    tp1_roi = unit_6_v11_number(
        strategy.get(
            "tp1_net_roi_floor_percent",
            10.0
        ),
        "TP1_NET_ROI"
    )

    tp2_roi = unit_6_v11_number(
        strategy.get(
            "tp2_net_roi_floor_percent",
            30.0
        ),
        "TP2_NET_ROI"
    )

    if tp1_roi < 0 or tp2_roi < tp1_roi:
        raise RuntimeError(
            "UNIT 6 INVALID TP ROI CONFIGURATION"
        )

    # ========================================================
    # 6.6 COST MODEL
    # Percentages refer to position notional.
    # ========================================================

    round_trip_fee = c(
        "estimated_round_trip_fee_pct",
        0.16
    )

    extra_cost = unit_6_v11_env_number(
        "UNIT6_EXTRA_COST_PCT",
        0.0
    )

    if round_trip_fee < 0 or extra_cost < 0:
        raise RuntimeError(
            "UNIT 6 NEGATIVE COST CONFIGURATION"
        )

    total_cost = (
        round_trip_fee + extra_cost
    )

    # ========================================================
    # 6.7 PROJECTED MOVEMENT
    #
    # This is a configurable ATR-based screening estimate,
    # not a prediction or guaranteed remaining movement.
    # ========================================================

    atr_multiplier = unit_6_v11_env_number(
        "UNIT6_ATR_PROJECTION_MULTIPLIER",
        2.0
    )

    if atr_multiplier <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID ATR MULTIPLIER"
        )

    estimated_move = (
        atr_pct * atr_multiplier
    )

    # Also retain historical movement for comparison.
    if mode == "BREAKOUT":
        historical_move = abs(
            c("breakout_move_pct", move_5m)
        )
    elif mode == "STRUCTURE":
        historical_move = abs(
            c("structure_move_pct", move_15m)
        )
    elif mode == "SCALP":
        historical_move = abs(
            c("scalp_move_pct", move_1m)
        )
    else:
        historical_move = 0.0
        estimated_move = 0.0

    # ========================================================
    # 6.8 NET PROFIT ASSESSMENT
    # ========================================================

    estimated_net_roi = None
    required_tp1_move = None
    required_tp2_move = None

    fee_coverage_pass = None
    tp1_profit_pass = False
    tp2_profit_pass = False
    profit_qualified = False

    if (
        mode != "NONE"
        and leverage_ready
    ):
        estimated_net_roi = (
            (estimated_move - total_cost)
            * leverage
        )

        required_tp1_move = (
            total_cost + tp1_roi / leverage
        )

        required_tp2_move = (
            total_cost + tp2_roi / leverage
        )

        fee_coverage_pass = (
            estimated_move > total_cost
        )

        tp1_profit_pass = (
            estimated_net_roi >= tp1_roi
        )

        tp2_profit_pass = (
            estimated_net_roi >= tp2_roi
        )

        profit_qualified = (
            fee_coverage_pass
            and tp1_profit_pass
        )

    # ========================================================
    # 6.9 ADMISSION ARBITRATION
    # ========================================================

    execution_intent = False
    signal_qualified = False
    active_mode = "NONE"
    direction = "NONE"

    admission_reason = (
        "NO_ACCEPTABLE_CANDIDATE"
    )

    if not fresh:
        admission_reason = (
            "MARKET_EVIDENCE_STALE"
        )

    elif not market_confirmed:
        admission_reason = str(
            candidate.get(
                "qualification_reason",
                "MARKET_NOT_CONFIRMED"
            )
        )

    elif not leverage_ready:
        admission_reason = (
            "LEVERAGE_CONFIGURATION_PENDING"
        )

    elif not fee_coverage_pass:
        admission_reason = (
            "ESTIMATED_MOVEMENT_BELOW_COST"
        )

    elif not tp1_profit_pass:
        admission_reason = (
            "ESTIMATED_NET_ROI_BELOW_TP1"
        )

    else:
        execution_intent = True
        signal_qualified = True
        active_mode = mode
        direction = side
        admission_reason = (
            "NET_PROFIT_SCREEN_PASSED"
        )

    # ========================================================
    # 6.10 UNIT 7 OUTPUT CONTRACT
    # ========================================================

    result = {
        "symbol": symbol,
        "execution_intent":
            execution_intent,
        "signal_qualified":
            signal_qualified,
        "active_mode": active_mode,
        "direction": direction,
        "admission_reason":
            admission_reason,

        "candidate_mode": mode,
        "candidate_stage": stage,
        "market_confirmed":
            market_confirmed,
        "profit_qualified":
            profit_qualified,
        "entry_qualified":
            signal_qualified,

        "unit_5_reason":
            candidate.get(
                "qualification_reason",
                "UNKNOWN"
            ),

        "higher_mode_developing":
            higher_developing,

        "unit_5_evidence_version":
            candidate.get(
                "strategy_evidence_version"
            ),
        "unit_4_evidence_version":
            analysis.get(
                "strategy_evidence_version"
            ),

        "classification_version":
            "UNIT6_V9_ADJUSTABLE",
        "classification_revision":
            "UNIT6_V11_NET_PROFIT",

        "market_data_fresh": fresh,

        "leverage_target": None,
        "leverage_regime":
            "WEEX_EXCHANGE_SETTING",
        "configured_leverage":
            leverage,
        "leverage_source":
            leverage_key,
        "leverage_configured":
            leverage_ready,

        "sideways_regime": sideways,
        "ema_compressed": ema_compressed,
        "compression_threshold_pct":
            compression_limit,

        "momentum_conflict":
            momentum_conflict,
        "persistence_window":
            persistence_window,
        "persistence_required":
            persistence_required,
        "persistence_confirmations":
            confirmations,
        "persistence_directions":
            directions,
        "persistence_pass":
            persistence_pass,

        "fifteen_minute_support_pass":
            directions[2] == scalp_side,

        "scalp_quality_score":
            quality_score,
        "scalp_quality_minimum":
            quality_minimum,
        "scalp_quality_pass":
            quality_pass,
        "scalp_quality_details":
            quality_details,

        "estimated_move_pct":
            estimated_move,
        "historical_move_pct":
            historical_move,
        "estimated_round_trip_fee_pct":
            round_trip_fee,
        "additional_cost_pct":
            extra_cost,
        "total_cost_pct":
            total_cost,
        "required_move_pct":
            required_tp1_move,
        "required_tp1_move_pct":
            required_tp1_move,
        "required_tp2_move_pct":
            required_tp2_move,
        "estimated_net_roi_pct":
            estimated_net_roi,
        "tp1_net_roi_target_pct":
            tp1_roi,
        "tp2_net_roi_target_pct":
            tp2_roi,
        "tp1_profit_qualified":
            tp1_profit_pass,
        "tp2_profit_qualified":
            tp2_profit_pass,
        "fee_coverage_pass":
            fee_coverage_pass,
        "fee_estimate_verified": False,
        "projection_method":
            "ATR_MULTIPLIER_HEURISTIC",

        "position_sizing_performed": False,
        "order_payload_created": False,
        "exchange_write": False,
        "read_only": True,
        "trade_authorized": False
    }

    # ========================================================
    # 6.11 RENDER DIAGNOSTICS
    # ========================================================

    print(
        "UNIT 6 SYMBOL =", symbol,
        flush=True
    )
    print(
        "UNIT 6 MARKET MODE =", mode,
        flush=True
    )
    print(
        "UNIT 6 MARKET CONFIRMED =",
        market_confirmed, flush=True
    )
    print(
        "UNIT 6 DIRECTION =", side,
        flush=True
    )
    print(
        "UNIT 6 MARKET DATA FRESH =",
        fresh, flush=True
    )
    print(
        "UNIT 6 LEVERAGE =",
        leverage, flush=True
    )
    print(
        "UNIT 6 ATR % =",
        round(atr_pct, 6), flush=True
    )
    print(
        "UNIT 6 PROJECTED MOVE % =",
        round(estimated_move, 6),
        flush=True
    )
    print(
        "UNIT 6 PROJECTION METHOD =",
        "ATR_MULTIPLIER_HEURISTIC",
        flush=True
    )
    print(
        "UNIT 6 ROUND TRIP COST % =",
        round(total_cost, 6),
        flush=True
    )
    print(
        "UNIT 6 ESTIMATED NET ROI % =",
        estimated_net_roi, flush=True
    )
    print(
        "UNIT 6 TP1 NET ROI TARGET % =",
        tp1_roi, flush=True
    )
    print(
        "UNIT 6 TP2 NET ROI TARGET % =",
        tp2_roi, flush=True
    )
    print(
        "UNIT 6 TP1 PROFIT SCREEN =",
        tp1_profit_pass, flush=True
    )
    print(
        "UNIT 6 TP2 PROFIT SCREEN =",
        tp2_profit_pass, flush=True
    )
    print(
        "UNIT 6 SCALP QUALITY =",
        quality_score, flush=True
    )
    print(
        "UNIT 6 SCALP PERSISTENCE =",
        confirmations, "/",
        persistence_required,
        flush=True
    )
    print(
        "UNIT 6 SIGNAL QUALIFIED =",
        signal_qualified, flush=True
    )
    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent, flush=True
    )
    print(
        "UNIT 6 ADMISSION REASON =",
        admission_reason, flush=True
    )
    print(
        "UNIT 6 TO UNIT 7 HANDOVER = READY",
        flush=True
    )
    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# 6.12 DETERMINISTIC VALIDATION
# ============================================================

def unit_6_validation_v11():
    cfg = {
        "strategy": {
            "tp1_net_roi_floor_percent": 10,
            "tp2_net_roi_floor_percent": 30
        },
        "qualification": {
            "scalp": {}
        },
        "market_data_policy": {
            "max_market_age_seconds": 120
        }
    }

    analysis = {
        "symbol": "AVAXUSDT",
        "latest_close": 8.2,
        "live_mark_price": 8.2,
        "ema19": 8.18,
        "ema50": 8.16,
        "ema100": 8.1,
        "ema200": 8.0,
        "atr14": 0.01,
        "move_1m_pct": 0.05,
        "move_5m_pct": 0.10,
        "move_15m_pct": 0.20,
        "sideways_candidate": False
    }

    candidate = {
        "symbol": "AVAXUSDT",
        "candidate_mode": "STRUCTURE",
        "candidate_stage": "QUALIFIED",
        "direction": "LONG",
        "qualified": True,
        "structure_ready": True,
        "breakout_ready": False,
        "scalp_ready": False,
        "higher_mode_developing": False,
        "candle_data_fresh": True,
        "candidate_age_seconds": 5,
        "estimated_round_trip_fee_pct": 0.16,
        "qualification_reason":
            "STRUCTURE_CONFIRMED"
    }

    # Tests do not submit orders.
    old_long = os.environ.get(
        "WEEX_LEVERAGE_LONG"
    )

    try:
        os.environ[
            "WEEX_LEVERAGE_LONG"
        ] = "10"

        output = fresh_reconstruction_unit_6(
            copy.deepcopy(cfg),
            copy.deepcopy(analysis),
            copy.deepcopy(candidate)
        )

        assert output["symbol"] == "AVAXUSDT"
        assert output["market_confirmed"] is True
        assert output["order_payload_created"] is False
        assert output["exchange_write"] is False
        assert output["classification_revision"] == (
            "UNIT6_V11_NET_PROFIT"
        )
        
        # TP1 IS REQUIRED; TP2 IS NOT AN ENTRY GATE.
        old_multiplier = os.environ.get(
            "UNIT6_ATR_PROJECTION_MULTIPLIER"
        )

        try:
            # Strong projected movement:
            # enough for TP1, below TP2.
            os.environ[
                "UNIT6_ATR_PROJECTION_MULTIPLIER"
            ] = "20"

            tp1_case = fresh_reconstruction_unit_6(
                copy.deepcopy(cfg),
                copy.deepcopy(analysis),
                copy.deepcopy(candidate)
            )

            assert tp1_case["market_confirmed"] is True
            assert tp1_case["tp1_profit_qualified"] is True
            assert tp1_case["tp2_profit_qualified"] is False
            assert tp1_case["signal_qualified"] is True
            assert tp1_case["execution_intent"] is True
            assert tp1_case["admission_reason"] == (
                "NET_PROFIT_SCREEN_PASSED"
            )

            # Insufficient projected movement:
            # signal is valid but TP1 cannot be met.
            os.environ[
                "UNIT6_ATR_PROJECTION_MULTIPLIER"
            ] = "2"

            below_tp1 = fresh_reconstruction_unit_6(
                copy.deepcopy(cfg),
                copy.deepcopy(analysis),
                copy.deepcopy(candidate)
            )

            assert below_tp1["market_confirmed"] is True
            assert below_tp1["tp1_profit_qualified"] is False
            assert below_tp1["signal_qualified"] is False
            assert below_tp1["execution_intent"] is False
            assert below_tp1["admission_reason"] == (
                "ESTIMATED_NET_ROI_BELOW_TP1"
            )

            print(
                "UNIT 6 TP1 ENTRY TEST = PASS",
                flush=True
            )
            print(
                "UNIT 6 TP2 NOT ENTRY GATE = PASS",
                flush=True
            )

        finally:
            if old_multiplier is None:
                os.environ.pop(
                    "UNIT6_ATR_PROJECTION_MULTIPLIER",
                    None
                )
            else:
                os.environ[
                    "UNIT6_ATR_PROJECTION_MULTIPLIER"
                ] = old_multiplier

        
        # TP1 ENTRY PROFITABILITY REGRESSION TEST
        # No exchange orders are submitted.

        old_projection = os.environ.get(
            "UNIT6_ATR_PROJECTION_MULTIPLIER"
        )

        try:
            # Case A: Projected net ROI reaches TP1
            # but does not reach TP2.
            os.environ[
                "UNIT6_ATR_PROJECTION_MULTIPLIER"
            ] = "20"

            profitable = fresh_reconstruction_unit_6(
                copy.deepcopy(cfg),
                copy.deepcopy(analysis),
                copy.deepcopy(candidate)
            )

            assert profitable["market_confirmed"] is True
            assert profitable["tp1_profit_qualified"] is True
            assert profitable["tp2_profit_qualified"] is False
            assert profitable["signal_qualified"] is True
            assert profitable["execution_intent"] is True
            assert profitable["admission_reason"] == (
                "NET_PROFIT_SCREEN_PASSED"
            )

            # Case B: Valid market signal but projected
            # net ROI cannot reach TP1.
            os.environ[
                "UNIT6_ATR_PROJECTION_MULTIPLIER"
            ] = "2"

            insufficient = fresh_reconstruction_unit_6(
                copy.deepcopy(cfg),
                copy.deepcopy(analysis),
                copy.deepcopy(candidate)
            )

            assert insufficient["market_confirmed"] is True
            assert insufficient["tp1_profit_qualified"] is False
            assert insufficient["signal_qualified"] is False
            assert insufficient["execution_intent"] is False
            assert insufficient["admission_reason"] == (
                "ESTIMATED_NET_ROI_BELOW_TP1"
            )

        finally:
            if old_projection is None:
                os.environ.pop(
                    "UNIT6_ATR_PROJECTION_MULTIPLIER",
                    None
                )
            else:
                os.environ[
                    "UNIT6_ATR_PROJECTION_MULTIPLIER"
                ] = old_projection


        idle = copy.deepcopy(candidate)
        idle.update({
            "candidate_mode": "NONE",
            "candidate_stage": "REJECTED",
            "direction": "NONE",
            "qualified": False,
            "structure_ready": False
        })

        idle_output = fresh_reconstruction_unit_6(
            cfg, analysis, idle
        )

        assert idle_output[
            "execution_intent"
        ] is False

        assert idle_output[
            "active_mode"
        ] == "NONE"

    finally:
        if old_long is None:
            os.environ.pop(
                "WEEX_LEVERAGE_LONG", None
            )
        else:
            os.environ[
                "WEEX_LEVERAGE_LONG"
            ] = old_long

    print(
        "UNIT 6 V11 VALIDATION = PASS",
        flush=True
    )
    return True


FRESH_UNIT_6_VALIDATION_READY = (
    unit_6_validation_v11()
)

FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )
)

# ============================================================
# END COMPLETE UNIT 6 V11 REPLACEMENT
# UNIT 7 STARTS AT ZERO INDENTATION
# ============================================================
