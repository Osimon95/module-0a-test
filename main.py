
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
# START COMPLETE UNIT 2 V13
# WEEX DEMO CENTRAL CONFIGURATION
# GROUPED RENDER SETTINGS
# ATR-DYNAMIC BACKUP BUFFER
# ORIGINAL DOWNSTREAM KEYS PRESERVED
# ZERO INDENTATION
# ============================================================

import os
import re
from decimal import Decimal, InvalidOperation


# ============================================================
# NUMERIC UTILITIES
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


def unit_2_v13_setting(
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
# GROUPED RENDER VALUE PARSER
#
# Example:
# TP_ALLOCATION_PERCENT=TP1:10, TP2:20
#
# Also accepts:
# TP1=10,TP2=20
#
# No extra dependencies or packages.
# ============================================================

def unit_2_v13_group(
    env_name,
    defaults,
    aliases=None
):
    aliases = aliases or {}
    result = {}

    for key, default in defaults.items():
        legacy_key = aliases.get(key)

        if legacy_key:
            result[key] = unit_2_v13_setting(
                legacy_key,
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
        value = value.strip()

        if key not in defaults:
            raise ValueError(
                env_name + " UNKNOWN KEY: " + key
            )

        if key in supplied:
            raise ValueError(
                env_name + " DUPLICATE KEY: " + key
            )

        supplied.add(key)

        result[key] = unit_2_v9_number(
            value,
            env_name + "." + key,
            allow_zero=True
        )

    return result


# ============================================================
# PURE ATR-DYNAMIC BACKUP BUFFER
#
# Calculated only when fresh ATR14 and price
# are available. No global mutation.
# ============================================================

def unit_2_v13_atr_backup_buffer(
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

    atr_percent = (
        atr / price * Decimal("100")
    )

    buffer_percent = atr_percent * factor

    if buffer_percent >= Decimal("100"):
        raise ValueError(
            "ATR BUFFER OUTSIDE VALID PRICE RANGE"
        )

    return {
        "mode": "ATR_DYNAMIC",
        "atr14": float(atr),
        "market_price": float(price),
        "atr_percent": float(atr_percent),
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


# Preserve previous helper names.
unit_2_v12_atr_backup_buffer = (
    unit_2_v13_atr_backup_buffer
)

unit_2_v11_atr_backup_buffer = (
    unit_2_v13_atr_backup_buffer
)


# ============================================================
# CENTRAL CONFIGURATION
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 2 V13 START",
        flush=True
    )

    # --------------------------------------------------------
    # SYMBOL REQUEST
    # --------------------------------------------------------

    requested_symbol = os.getenv(
        "WEEX_SYMBOL", "BTCUSDT"
    ).strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9]{2,25}USDT",
        requested_symbol
    ):
        raise ValueError(
            "INVALID WEEX_SYMBOL: " + requested_symbol
        )

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",

        "requested_symbol": requested_symbol,

        # Original BTC configuration remains
        # until the existing symbol controller
        # reconciles the requested symbol.
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",

        "symbol_switch_status":
            "PENDING_VERIFICATION"
            if requested_symbol != "BTCUSDT"
            else "CURRENT_CONFIGURATION",
    }

    # --------------------------------------------------------
    # INDEPENDENT RENDER SETTINGS
    # --------------------------------------------------------

    initial_margin = unit_2_v13_setting(
        "INITIAL_ENTRY_MARGIN_USDT",
        "0.5",
        aliases=("ENTRY_FIXED_USDT",)
    )

    backup_margin = unit_2_v13_setting(
        "BACKUP_MARGIN_PERCENT",
        "0.5"
    )

    exposure_cap = unit_2_v13_setting(
        "EXPOSURE_CAP_PERCENT",
        "50"
    )

    if backup_margin > 100:
        raise ValueError(
            "BACKUP_MARGIN_PERCENT EXCEEDS 100"
        )

    if exposure_cap > 100:
        raise ValueError(
            "EXPOSURE_CAP_PERCENT EXCEEDS 100"
        )

    # --------------------------------------------------------
    # GROUP 1: TAKE-PROFIT ALLOCATION
    #
    # TP_ALLOCATION_PERCENT=TP1:10, TP2:20
    #
    # TP3 is automatically calculated.
    # --------------------------------------------------------

    allocation = unit_2_v13_group(
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

    if (
        tp1_allocation <= 0
        or tp2_allocation <= 0
        or tp3_allocation <= 0
    ):
        raise ValueError(
            "TP ALLOCATIONS MUST BE POSITIVE "
            "AND TOTAL 100"
        )

    # --------------------------------------------------------
    # GROUP 2: NET ROI PROFIT TARGETS
    #
    # TP_NET_ROI_PERCENT=TP1:20, TP2:40
    # --------------------------------------------------------

    roi = unit_2_v13_group(
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
            "TP2 ROI MUST EXCEED POSITIVE TP1 ROI"
        )

    # --------------------------------------------------------
    # GROUP 3: TP3 TRAILING
    #
    # Optional:
    # TP_TRAILING_PERCENT=REF:0.20, MIN:0.10, MAX:0.40
    # --------------------------------------------------------

    trailing = unit_2_v13_group(
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
            "INVALID TP TRAILING RANGE"
        )

    # --------------------------------------------------------
    # ATR BACKUP COMPATIBILITY
    #
    # Legacy value retained for old consumers.
    # It is not an ATR-derived trigger.
    # --------------------------------------------------------

    legacy_buffer = unit_2_v13_setting(
        "BACKUP_BUFFER_PERCENT",
        "0.3"
    )

    if legacy_buffer >= 100:
        raise ValueError(
            "INVALID LEGACY BACKUP BUFFER"
        )

    # --------------------------------------------------------
    # STRATEGY
    #
    # All established downstream keys remain.
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
            "unit_2_v13_atr_backup_buffer",
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
    # ORIGINAL PRECISION FALLBACK
    # --------------------------------------------------------

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # --------------------------------------------------------
    # ORIGINAL HYBRID QUALIFICATION CONTRACT
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

    # --------------------------------------------------------
    # UNIT 2 LOCAL CAPABILITIES
    #
    # These must not become global vetoes
    # on authorized demo execution.
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
    # STARTUP REPORT
    # --------------------------------------------------------

    print(
        "UNIT 2 REQUESTED SYMBOL =",
        requested_symbol,
        flush=True
    )

    print(
        "UNIT 2 INITIAL ENTRY MARGIN =",
        initial_margin,
        flush=True
    )

    print(
        "UNIT 2 TP ALLOCATION =",
        tp1_allocation,
        "/",
        tp2_allocation,
        "/",
        tp3_allocation,
        flush=True
    )

    print(
        "UNIT 2 TP NET ROI =",
        tp1_roi,
        "/",
        tp2_roi,
        flush=True
    )

    print(
        "UNIT 2 TP3 TRAILING =",
        trailing["REF"],
        "/",
        trailing["MIN"],
        "/",
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
        "UNIT 2 ATR BUFFER READY = False",
        flush=True
    )

    print(
        "UNIT 2 EXPOSURE CAP % =",
        exposure_cap,
        flush=True
    )

    print(
        "UNIT 2 DEMO EXECUTION = DOWNSTREAM",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS",
        flush=True
    )

    return config


# ============================================================
# RUN UNIT 2
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# UNIT 3 COMPATIBILITY
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
    "UNIT 2 V13 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)


# ============================================================
# END COMPLETE UNIT 2 V13
# UNIT 3 FOLLOWS
# ZERO INDENTATION
# ============================================================

