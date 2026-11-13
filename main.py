
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
# START COMPLETE UNIT 2 V14
# WEEX DEMO - CENTRAL CONFIGURATION
# GROUPED RENDER VARIABLES
# DEFERRED SYMBOL SWITCHING
# ATR-DYNAMIC BACKUP CONFIGURATION
# ORIGINAL DOWNSTREAM INTERFACES PRESERVED
# ZERO INDENTATION
# ============================================================

import os
import re
from decimal import Decimal, InvalidOperation


# ============================================================
# 1. NUMERIC CONFIGURATION HELPERS
# ============================================================

def unit_2_v9_number(value, name, allow_zero=False):
    if isinstance(value, bool):
        raise ValueError("INVALID " + name)

    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("INVALID " + name) from exc

    if not number.is_finite():
        raise ValueError("NONFINITE " + name)

    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError("INVALID RANGE " + name)

    return number


def unit_2_v14_setting(
    name,
    default,
    aliases=(),
    allow_zero=False
):
    value = os.getenv(name)

    if value is None or not value.strip():
        for alias in aliases:
            candidate = os.getenv(alias)
            if candidate is not None and candidate.strip():
                value = candidate
                break

    if value is None or not value.strip():
        value = str(default)

    return unit_2_v9_number(
        value, name, allow_zero
    )


# ============================================================
# 2. GROUPED RENDER PARSER
# ============================================================

def unit_2_v14_group(
    env_name,
    defaults,
    aliases=None
):
    aliases = aliases or {}
    result = {}

    for key, default in defaults.items():
        legacy_name = aliases.get(key)

        if legacy_name:
            result[key] = unit_2_v14_setting(
                legacy_name,
                default,
                allow_zero=True
            )
        else:
            result[key] = unit_2_v9_number(
                default, key, allow_zero=True
            )

    raw = os.getenv(env_name, "").strip()

    if not raw:
        return result

    supplied = set()
    explicit_tp3 = None

    for entry in raw.split(","):
        entry = entry.strip()

        if not entry:
            continue

        if ":" in entry:
            key, value = entry.split(":", 1)
        elif "=" in entry:
            key, value = entry.split("=", 1)
        else:
            raise ValueError(
                env_name + " INVALID ENTRY: " + entry
            )

        key = key.strip().upper()

        allowed = set(defaults)

        if env_name == "TP_ALLOCATION_PERCENT":
            allowed.add("TP3")

        if key not in allowed:
            raise ValueError(
                env_name + " UNKNOWN KEY: " + key
            )

        if key in supplied:
            raise ValueError(
                env_name + " DUPLICATE KEY: " + key
            )

        supplied.add(key)

        number = unit_2_v9_number(
            value,
            env_name + "." + key,
            allow_zero=True
        )

        if key == "TP3":
            explicit_tp3 = number
        else:
            result[key] = number

    # TP3 is always derived from TP1 and TP2.
    # A legacy TP3 value is accepted but cannot
    # create a competing configuration source.

    if explicit_tp3 is not None:
        derived = (
            Decimal("100")
            - result["TP1"]
            - result["TP2"]
        )

        if explicit_tp3 != derived:
            print(
                "UNIT 2 LEGACY TP3 OVERRIDDEN =",
                explicit_tp3,
                "DERIVED TP3 =",
                derived,
                flush=True
            )

    return result


# Preserve earlier grouped parser interface.
unit_2_v13_group = unit_2_v14_group


# ============================================================
# 3. SYMBOL NORMALIZATION
# ============================================================

def unit_2_v14_symbol(value):
    symbol = str(value or "").strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9]{2,25}USDT",
        symbol
    ):
        raise ValueError(
            "INVALID REQUESTED SYMBOL: " + symbol
        )

    return symbol


# ============================================================
# 4. PURE SYMBOL-SWITCH DECISION FUNCTION
#
# This function never calls WEEX or Telegram.
#
# It consumes VERIFIED exchange facts supplied
# by the existing account/contract adapter.
#
# The coordinator must persist and apply the
# returned decision atomically.
# ============================================================

def unit_2_v14_symbol_decision(
    requested_symbol,
    active_symbol,
    contract_supported=None,
    position_flat=None,
    orders_clear=None
):
    requested = unit_2_v14_symbol(
        requested_symbol
    )

    active = (
        unit_2_v14_symbol(active_symbol)
        if active_symbol else None
    )

    base = {
        "requested_symbol": requested,
        "active_symbol": active,
        "pending_symbol": None,
        "activate": False,
        "persist_required": False,
        "notification_required": False,
        "notification_status": None,
        "status": None,
        "reason": None,
    }

    def decision(
        status,
        reason,
        pending=None,
        activate=False,
        persist=False,
        notify=False
    ):
        return {
            **base,
            "pending_symbol": pending,
            "activate": activate,
            "persist_required": persist,
            "notification_required": notify,
            "notification_status": status,
            "status": status,
            "reason": reason,
        }

    # A request for the active symbol does not
    # require a new exchange order or switch.

    if active == requested:
        return decision(
            "ALREADY_ACTIVE",
            "REQUESTED_SYMBOL_ALREADY_ACTIVE"
        )

    # Unknown verification is not rejection.
    # It must not be treated as position flat.

    if contract_supported is None:
        return decision(
            "VERIFICATION_PENDING",
            "DEMO_CONTRACT_NOT_YET_VERIFIED",
            pending=requested
        )

    if contract_supported is False:
        return decision(
            "REJECTED",
            "UNSUPPORTED_WEEX_DEMO_CONTRACT",
            notify=True
        )

    # Contract support must come from an actual
    # verified demo-futures contract lookup.

    if contract_supported is not True:
        return decision(
            "VERIFICATION_PENDING",
            "INVALID_CONTRACT_VERIFICATION",
            pending=requested
        )

    if position_flat is None or orders_clear is None:
        return decision(
            "VERIFICATION_PENDING",
            "POSITION_OR_ORDER_STATUS_UNKNOWN",
            pending=requested
        )

    # Existing exposure or unresolved orders:
    # queue the request, preserve active symbol.

    if position_flat is False or orders_clear is False:
        return decision(
            "ACCEPTED_QUEUED",
            "EXISTING_EXPOSURE_OR_PENDING_ORDERS",
            pending=requested,
            persist=True,
            notify=True
        )

    # Only confirmed flat and clear conditions
    # can permit activation.

    if position_flat is True and orders_clear is True:
        return decision(
            "ACCEPTED_ACTIVATE",
            "SUPPORTED_AND_EXCHANGE_CONFIRMED_FLAT",
            activate=True,
            persist=True,
            notify=True
        )

    return decision(
        "VERIFICATION_PENDING",
        "INVALID_POSITION_VERIFICATION",
        pending=requested
    )


# ============================================================
# 5. TELEGRAM MESSAGE BUILDER
#
# Existing Telegram sender is responsible
# for delivery and retry.
# ============================================================

def unit_2_v14_symbol_message(decision):
    status = decision.get("status", "UNKNOWN")
    requested = decision.get(
        "requested_symbol", "UNKNOWN"
    )
    active = decision.get(
        "active_symbol"
    ) or "UNRESOLVED"

    reason = decision.get("reason", "UNKNOWN")

    return (
        "WEEX DEMO SYMBOL SWITCH\n"
        "Requested: " + requested + "\n"
        "Previous active: " + active + "\n"
        "Status: " + status + "\n"
        "Reason: " + reason
    )


# ============================================================
# 6. ATR-DYNAMIC BACKUP BUFFER
# ============================================================

def unit_2_v14_atr_backup_buffer(
    atr14,
    market_price,
    multiplier=1.0
):
    atr = unit_2_v9_number(
        atr14, "ATR14"
    )

    price = unit_2_v9_number(
        market_price, "MARKET_PRICE"
    )

    factor = unit_2_v9_number(
        multiplier, "ATR_MULTIPLIER"
    )

    buffer_percent = (
        atr / price
        * Decimal("100")
        * factor
    )

    if buffer_percent >= Decimal("100"):
        raise ValueError(
            "ATR BUFFER OUTSIDE VALID RANGE"
        )

    return {
        "mode": "ATR_DYNAMIC",
        "atr14": float(atr),
        "market_price": float(price),
        "atr_percent": float(
            atr / price * Decimal("100")
        ),
        "atr_multiplier": float(factor),
        "backup_buffer_percent":
            float(buffer_percent),
        "backup_long_liquidation_factor":
            float(
                Decimal("1")
                + buffer_percent / Decimal("100")
            ),
        "backup_short_liquidation_factor":
            float(
                Decimal("1")
                - buffer_percent / Decimal("100")
            ),
    }


unit_2_v13_atr_backup_buffer = (
    unit_2_v14_atr_backup_buffer
)
unit_2_v12_atr_backup_buffer = (
    unit_2_v14_atr_backup_buffer
)
unit_2_v11_atr_backup_buffer = (
    unit_2_v14_atr_backup_buffer
)


# ============================================================
# 7. CENTRAL CONFIGURATION
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 2 V14 START",
        flush=True
    )

    requested_symbol = unit_2_v14_symbol(
        os.getenv("WEEX_SYMBOL", "BTCUSDT")
    )

    # Unit 2 cannot infer the confirmed active
    # symbol from the Render request.
    #
    # BTC values below are legacy bootstrap
    # compatibility fields only.
    #
    # The SQLite/exchange coordinator must
    # restore the real active symbol before
    # new-entry execution.

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",

        "requested_symbol": requested_symbol,

        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",

        "symbol_switch_status":
            "BOOTSTRAP_RECONCILIATION_REQUIRED",

        "active_symbol_confirmed": False,
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

    # --------------------------------------------------------
    # INDEPENDENT RENDER SETTINGS
    # --------------------------------------------------------

    initial_margin = unit_2_v14_setting(
        "INITIAL_ENTRY_MARGIN_USDT",
        "0.5",
        aliases=("ENTRY_FIXED_USDT",)
    )

    backup_margin = unit_2_v14_setting(
        "BACKUP_MARGIN_PERCENT",
        "0.5"
    )

    exposure_cap = unit_2_v14_setting(
        "EXPOSURE_CAP_PERCENT",
        "50"
    )

    if backup_margin > 100:
        raise ValueError(
            "BACKUP MARGIN EXCEEDS 100%"
        )

    if exposure_cap > 100:
        raise ValueError(
            "EXPOSURE CAP EXCEEDS 100%"
        )

    # --------------------------------------------------------
    # GROUPED TP ALLOCATION
    # --------------------------------------------------------

    allocation = unit_2_v14_group(
        "TP_ALLOCATION_PERCENT",
        {
            "TP1": "10",
            "TP2": "20",
        },
        {
            "TP1": "TP1_ALLOCATION_PERCENT",
            "TP2": "TP2_ALLOCATION_PERCENT",
        }
    )

    tp1_allocation = allocation["TP1"]
    tp2_allocation = allocation["TP2"]

    tp3_allocation = (
        Decimal("100")
        - tp1_allocation
        - tp2_allocation
    )

    if min(
        tp1_allocation,
        tp2_allocation,
        tp3_allocation
    ) <= 0:
        raise ValueError(
            "INVALID TP ALLOCATION"
        )

    # --------------------------------------------------------
    # GROUPED TP NET ROI
    # --------------------------------------------------------

    roi = unit_2_v14_group(
        "TP_NET_ROI_PERCENT",
        {
            "TP1": "20",
            "TP2": "40",
        },
        {
            "TP1": "TP1_NET_ROI_FLOOR_PERCENT",
            "TP2": "TP2_NET_ROI_FLOOR_PERCENT",
        }
    )

    tp1_roi = roi["TP1"]
    tp2_roi = roi["TP2"]

    if tp1_roi <= 0 or tp2_roi <= tp1_roi:
        raise ValueError(
            "INVALID TP NET ROI TARGETS"
        )

    # --------------------------------------------------------
    # GROUPED TP3 TRAILING
    # --------------------------------------------------------

    trailing = unit_2_v14_group(
        "TP_TRAILING_PERCENT",
        {
            "REF": "0.20",
            "MIN": "0.10",
            "MAX": "0.40",
        }
    )

    if not (
        Decimal("0") < trailing["MIN"]
        <= trailing["REF"]
        <= trailing["MAX"]
    ):
        raise ValueError(
            "INVALID TP3 TRAILING SETTINGS"
        )

    # --------------------------------------------------------
    # LEGACY BACKUP BUFFER COMPATIBILITY
    # --------------------------------------------------------

    legacy_buffer = unit_2_v14_setting(
        "BACKUP_BUFFER_PERCENT",
        "0.3"
    )

    if legacy_buffer >= 100:
        raise ValueError(
            "INVALID LEGACY BACKUP BUFFER"
        )

    # --------------------------------------------------------
    # STRATEGY
    # --------------------------------------------------------

    strategy = {
        "initial_fixed_usdt":
            float(initial_margin),

        "initial_margin_percent": 5.0,

        "backup_margin_percent":
            float(backup_margin),

        "backup_buffer_percent":
            float(legacy_buffer),

        "backup_buffer_mode": "ATR_DYNAMIC",
        "backup_buffer_atr_multiplier": 1.0,
        "backup_buffer_calculation":
            "unit_2_v14_atr_backup_buffer",
        "backup_buffer_ready": False,

        "max_backups": 5,
        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "backup_long_liquidation_factor":
            float(
                Decimal("1")
                + legacy_buffer / Decimal("100")
            ),

        "backup_short_liquidation_factor":
            float(
                Decimal("1")
                - legacy_buffer / Decimal("100")
            ),

        "exposure_cap_percent":
            float(exposure_cap),

        "exposure_cap_max_percent": 100.0,
        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        "tp1_allocation_percent":
            float(tp1_allocation),

        "tp2_allocation_percent":
            float(tp2_allocation),

        "tp3_allocation_percent":
            float(tp3_allocation),

        "tp1_net_roi_floor_percent":
            float(tp1_roi),

        "tp2_net_roi_floor_percent":
            float(tp2_roi),

        "tp1_tp2_min_roi_separation_percent":
            float(tp2_roi - tp1_roi),

        "tp3_trailing_reference_percent":
            float(trailing["REF"]),

        "tp3_trailing_min_percent":
            float(trailing["MIN"]),

        "tp3_trailing_max_percent":
            float(trailing["MAX"]),

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,

        "one_direction_only": True,
        "entry_direction_lock_scope":
            "NEW_ENTRIES_ONLY",

        "hedge_direction_independent": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,
    }

    # --------------------------------------------------------
    # MARKET PRECISION FALLBACK
    # --------------------------------------------------------

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # --------------------------------------------------------
    # ORIGINAL SIGNAL QUALIFICATION SETTINGS
    # --------------------------------------------------------

    qualification = {
        "common": {
            "mode_priority": (
                "BREAKOUT", "STRUCTURE", "SCALP"
            ),
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

    # --------------------------------------------------------
    # UNIT-LOCAL CAPABILITIES
    # --------------------------------------------------------

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

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
        "qualification": qualification,
    }

    # --------------------------------------------------------
    # CONFIGURATION REPORT
    # --------------------------------------------------------

    print(
        "UNIT 2 REQUESTED SYMBOL =",
        requested_symbol,
        flush=True
    )

    print(
        "UNIT 2 SYMBOL SWITCH MODE = AUTO_DEFERRED",
        flush=True
    )

    print(
        "UNIT 2 ACTIVE SYMBOL = BOOTSTRAP_UNCONFIRMED",
        flush=True
    )

    print(
        "UNIT 2 SYMBOL RECONCILIATION = REQUIRED",
        flush=True
    )

    print(
        "UNIT 2 INITIAL ENTRY MARGIN =",
        initial_margin,
        flush=True
    )

    print(
        "UNIT 2 TP ALLOCATION =",
        tp1_allocation, "/",
        tp2_allocation, "/",
        tp3_allocation,
        flush=True
    )

    print(
        "UNIT 2 TP NET ROI =",
        tp1_roi, "/",
        tp2_roi,
        flush=True
    )

    print(
        "UNIT 2 TP3 TRAILING =",
        trailing["REF"], "/",
        trailing["MIN"], "/",
        trailing["MAX"],
        flush=True
    )

    print(
        "UNIT 2 BACKUP MARGIN % =",
        backup_margin,
        flush=True
    )

    print(
        "UNIT 2 BACKUP BUFFER MODE = ATR_DYNAMIC",
        flush=True
    )

    print(
        "UNIT 2 EXPOSURE CAP % =",
        exposure_cap,
        flush=True
    )

    print(
        "UNIT 2 SYMBOL SWITCH EXECUTION = DOWNSTREAM",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS",
        flush=True
    )

    return config


# ============================================================
# 8. UNIT 2 EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# 9. UNIT 3 COMPATIBILITY
# ============================================================

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
    raise RuntimeError(
        "UNIT 2 CONFIGURATION CONTRACT FAILED"
    )

print(
    "UNIT 2 V14 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)


# ============================================================
# END COMPLETE UNIT 2 V14
# UNIT 3 FOLLOWS
# ZERO INDENTATION
# ============================================================


