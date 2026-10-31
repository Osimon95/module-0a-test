
# ============================================================
# WEEX 15-UNIT REVERSIBLE ATR HEDGE MODEL
# UNIT 1 V2 - RUNTIME FOUNDATION
#
# PRESERVED FROM ORIGINAL WORKING MODEL
# NO BACKUP SYSTEM
# ZERO INDENTATION
# ============================================================

# ============================================================
# STANDARD LIBRARY IMPORTS
# ============================================================

import os
import json
import time
import math
import hmac
import hashlib
import base64
import threading
import urllib.error
import urllib.parse
import urllib.request

from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone


# ============================================================
# SHARED LOGGER
# PRESERVES ORIGINAL log(message) INTERFACE
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
# UNIT 1 - RUNTIME FOUNDATION
# ============================================================

def fresh_reconstruction_unit_1():

    print("=" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 1 V2 START"
    )

    print("-" * 80, flush=True)

    # --------------------------------------------------------
    # VERIFY REQUIRED STANDARD LIBRARY FUNCTIONS
    # --------------------------------------------------------

    required_modules = {
        "JSON": json,
        "OS": os,
        "TIME": time,
        "MATH": math,
        "HMAC": hmac,
        "HASHLIB": hashlib,
        "BASE64": base64,
        "THREADING": threading,
        "URLLIB": urllib.request,
        "DECIMAL": Decimal,
    }

    for name, module in required_modules.items():

        if module is None:
            raise RuntimeError(
                "UNIT 1 MODULE UNAVAILABLE: " + name
            )

        print(
            "PASS: UNIT 1 MODULE =",
            name,
            flush=True,
        )

    # --------------------------------------------------------
    # EXECUTION ENVIRONMENT
    # NO EXCHANGE ACCESS IN UNIT 1
    # --------------------------------------------------------

    execution_environment = "DEMO"

    if execution_environment != "DEMO":
        raise RuntimeError(
            "UNIT 1 INVALID EXECUTION ENVIRONMENT"
        )

    print(
        "PASS: EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    # --------------------------------------------------------
    # PRESERVE BOT MODE RESPONSIBILITY
    # UNIT 12 CONTROLS NEW INITIAL ENTRIES
    # EXISTING POSITION MANAGEMENT IS INDEPENDENT
    # --------------------------------------------------------

    print(
        "BOT_MODE AUTHORITY = UNIT 12 NEW INITIAL ENTRIES",
        flush=True,
    )

    print(
        "EXISTING POSITION MANAGEMENT = INDEPENDENT",
        flush=True,
    )

    # --------------------------------------------------------
    # UNIT 1 EXCHANGE SAFETY BOUNDARY
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

    # --------------------------------------------------------
    # UNIT 1 DOES NOT IMPLEMENT:
    #
    # MARKET ANALYSIS
    # ENTRY DECISIONS
    # STOP LOSS
    # HEDGE EXECUTION
    # TAKE PROFIT
    # ORDER SUBMISSION
    #
    # THESE REMAIN RESPONSIBILITIES OF LATER UNITS
    # --------------------------------------------------------

    print(
        "PASS: UNIT 1 RUNTIME FOUNDATION READY",
        flush=True,
    )

    log(
        "FRESH RECONSTRUCTION UNIT 1 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# RUN UNIT 1
# ============================================================

FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)


if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:

    raise RuntimeError(
        "UNIT 1 STARTUP VALIDATION FAILED"
    )


# ============================================================
# END COMPLETE UNIT 1 V2
# UNIT 2 FOLLOWS
# ============================================================



# ============================================================
# WEEX REVERSIBLE ATR HEDGE BOT
# COMPLETE UNIT 2 V12 REPLACEMENT
#
# ORIGINAL 17208-LINE MODEL INTERFACES PRESERVED
# ORIGINAL RENDER ENVIRONMENT NAMES PRESERVED
#
# MANUAL LONG / SHORT LEVERAGE
# EXPOSURE CAP DEFAULT 100%
# REVERSIBLE ATR H1 / H2 / R1 / R2
# NO BACKUP SYSTEM
# ZERO INDENTATION
# ============================================================

import os
from decimal import Decimal, InvalidOperation


# ============================================================
# 2.1 SHARED NUMBER VALIDATION
# ============================================================

def unit_2_v12_number(value, name, allow_zero=False):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 2 INVALID " + name)

    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RuntimeError(
            "UNIT 2 INVALID " + name
        ) from exc

    if not result.is_finite():
        raise RuntimeError(
            "UNIT 2 NONFINITE " + name
        )

    if result < 0 or (
        result == 0 and not allow_zero
    ):
        raise RuntimeError(
            "UNIT 2 INVALID RANGE " + name
        )

    return result


def unit_2_v12_require(condition, message):

    if not condition:
        raise RuntimeError(
            "UNIT 2 CONFIG INVALID: " + message
        )


# ============================================================
# 2.2 COMPLETE UNIT 2
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 V12 START")

    require = unit_2_v12_require
    number = unit_2_v12_number

    require(
        FRESH_RECONSTRUCTION_UNIT_1_READY is True,
        "UNIT 1 NOT READY"
    )

    # ========================================================
    # 2.3 ORIGINAL ENTRY MARGIN VARIABLE PRECEDENCE
    #
    # 1. INITIAL_ENTRY_MARGIN_USDT
    # 2. ENTRY_FIXED_USDT
    # 3. DEFAULT 0.5
    # ========================================================

    primary_margin = os.getenv(
        "INITIAL_ENTRY_MARGIN_USDT"
    )

    secondary_margin = os.getenv(
        "ENTRY_FIXED_USDT"
    )

    if primary_margin and primary_margin.strip():

        margin_raw = primary_margin.strip()
        margin_source = "INITIAL_ENTRY_MARGIN_USDT"

    elif secondary_margin and secondary_margin.strip():

        margin_raw = secondary_margin.strip()
        margin_source = "ENTRY_FIXED_USDT"

    else:

        margin_raw = "0.5"
        margin_source = "DEFAULT_0_5"

    initial_margin = number(
        margin_raw,
        "INITIAL ENTRY MARGIN"
    )

    # ========================================================
    # 2.4 EXPOSURE CAP
    #
    # ORIGINAL ENVIRONMENT VARIABLE PRESERVED
    # DEFAULT 100%
    # VALID RANGE ABOVE 0% THROUGH 100%
    # ========================================================

    exposure_cap = number(
        os.getenv(
            "EXPOSURE_CAP_PERCENT",
            "100"
        ),
        "EXPOSURE CAP"
    )

    require(
        Decimal("0") < exposure_cap <= Decimal("100"),
        "EXPOSURE CAP OUTSIDE 0-100%"
    )

    # ========================================================
    # 2.5 MANUAL LONG AND SHORT LEVERAGE
    #
    # ORIGINAL RENDER VARIABLE NAMES PRESERVED
    #
    # SET LEVERAGE MANUALLY ON WEEX DEMO FIRST.
    # ENTER MATCHING VALUES IN RENDER.
    #
    # NO WEEX LEVERAGE API READ
    # NO WEEX LEVERAGE API WRITE
    # ========================================================

    long_raw = os.getenv(
        "WEEX_DEMO_LONG_LEVERAGE"
    )

    short_raw = os.getenv(
        "WEEX_DEMO_SHORT_LEVERAGE"
    )

    require(
        long_raw is not None and bool(long_raw.strip()),
        "MISSING WEEX_DEMO_LONG_LEVERAGE"
    )

    require(
        short_raw is not None and bool(short_raw.strip()),
        "MISSING WEEX_DEMO_SHORT_LEVERAGE"
    )

    long_leverage = number(
        long_raw.strip(),
        "LONG LEVERAGE"
    )

    short_leverage = number(
        short_raw.strip(),
        "SHORT LEVERAGE"
    )

    # Match original Unit 8 local leverage ceiling.
    require(
        long_leverage <= Decimal("200"),
        "LONG LEVERAGE ABOVE 200"
    )

    require(
        short_leverage <= Decimal("200"),
        "SHORT LEVERAGE ABOVE 200"
    )

    leverage = {
        "source": "RENDER_MANUAL_CONFIGURATION",

        "long": float(long_leverage),
        "short": float(short_leverage),

        "long_environment":
            "WEEX_DEMO_LONG_LEVERAGE",

        "short_environment":
            "WEEX_DEMO_SHORT_LEVERAGE",

        "read_from_weex": False,
        "write_to_weex": False,
        "automatic_sync": False,

        "exchange_setting_required": True,
        "position_side_specific": True,
    }

    # ========================================================
    # 2.6 EXCHANGE CONFIGURATION
    # ORIGINAL WEEX V3 CONTRACT PRESERVED
    # ========================================================

    exchange = {
        "name": "WEEX",
        "api_version": "V3",

        "contract_base_url":
            "https://api-contract.weex.com",

        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
    }

    # ========================================================
    # 2.7 UNIT-LOCAL API SAFETY
    #
    # UNIT 2 ONLY CONFIGURES.
    # UNIT 12 AND POSITION MANAGEMENT UNITS WILL
    # HANDLE EXECUTABLE DEMO ORDER SUBMISSIONS.
    # ========================================================

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

    # ========================================================
    # 2.8 CENTRAL STRATEGY
    # PRESERVE ORIGINAL QUALIFICATION AND TP SETTINGS
    # ========================================================

    strategy = {
        "initial_fixed_usdt": float(initial_margin),
        "initial_margin_percent": 5.0,

        "exposure_cap_percent": float(exposure_cap),
        "exposure_cap_max_percent": 100.0,
        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_open_hedge_margin": True,
        "exposure_includes_pending_margin": True,

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,
        "tp1_tp2_min_roi_separation_percent": 5.0,

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,

        # Restricts initial signal selection,
        # not hedge-mode position management.
        "one_direction_only": True,

        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,
    }

    # ========================================================
    # 2.9 REVERSIBLE ATR HEDGE
    # ========================================================

    hedge = {
        "enabled": True,

        # Later units enable actual demo execution.
        "execution_enabled": False,

        "mode": "REVERSIBLE_ATR_TWO_STAGE",
        "environment": "DEMO",

        "atr_source": "UNIT_4_ATR14",
        "atr_period": 14,

        "atr_capture": "ORIGINAL_ENTRY",
        "atr_frozen_per_cycle": True,

        "entry_reference": "ORIGINAL_ENTRY_PRICE",
        "direction_reference": "ORIGINAL_SIDE",
        "quantity_reference": "ORIGINAL_FILLED_QUANTITY",

        # Stage H1 - adverse 1 ATR
        "h1_atr_multiplier": 1.0,
        "h1_original_fraction": 0.50,
        "h1_opposite_fraction": 0.50,

        # Stage H2 - adverse 2 ATR
        "h2_atr_multiplier": 2.0,
        "h2_original_fraction": 0.00,
        "h2_opposite_fraction": 1.00,

        # Recovery R1 - back to adverse 1 ATR
        "r1_atr_multiplier": 1.0,
        "r1_original_fraction": 0.50,
        "r1_opposite_fraction": 0.50,

        # Recovery R2 - original entry
        "r2_atr_multiplier": 0.0,
        "r2_original_fraction": 1.00,
        "r2_opposite_fraction": 0.00,

        "reversible": True,
        "repeatable": True,

        "quantity_step_aware": True,
        "minimum_quantity_required": True,

        "confirmed_fill_required": True,
        "position_reconciliation_required": True,
        "anti_duplicate_orders": True,

        "required_position_mode": "HEDGE",
        "allow_simultaneous_long_short": True,
        "change_exchange_position_mode": False,

        "conventional_stop_loss_enabled": False,
        "emergency_close_enabled": False,
        "liquidation_protection_enabled": False,

        "bot_mode_independent": True,
        "real_cash_enabled": False,
    }

    strategy["hedge"] = hedge

    # ========================================================
    # 2.10 MARKET PRECISION
    # ORIGINAL MODEL VALUES PRESERVED
    # ========================================================

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # ========================================================
    # 2.11 ORIGINAL STRATEGY QUALIFICATION CONTRACT
    # ========================================================

    qualification = {

        "common": {
            "mode_priority":
                ("BREAKOUT", "STRUCTURE", "SCALP"),

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

    # ========================================================
    # 2.12 COMPLETE CONFIGURATION HANDOVER
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",

        "safety": safety,
        "leverage": leverage,
        "strategy": strategy,
        "market_precision": market_precision,
        "qualification": qualification,
    }

    # ========================================================
    # 2.13 COMPLETE VALIDATION
    # ========================================================

    require(initial_margin > 0, "INITIAL MARGIN")
    require(
        Decimal("0") < exposure_cap <= Decimal("100"),
        "EXPOSURE CAP"
    )

    require(
        Decimal("0") < long_leverage <= Decimal("200"),
        "LONG LEVERAGE"
    )

    require(
        Decimal("0") < short_leverage <= Decimal("200"),
        "SHORT LEVERAGE"
    )

    require(
        leverage["read_from_weex"] is False
        and leverage["write_to_weex"] is False,
        "MANUAL LEVERAGE POLICY"
    )

    require(
        sum(
            strategy[key]
            for key in (
                "tp1_allocation_percent",
                "tp2_allocation_percent",
                "tp3_allocation_percent",
            )
        ) == 100.0,
        "TP ALLOCATION"
    )

    require(
        strategy["tp1_net_roi_floor_percent"] >= 5.0,
        "TP1 ROI FLOOR"
    )

    require(
        strategy["tp2_net_roi_floor_percent"] >= 10.0,
        "TP2 ROI FLOOR"
    )

    require(
        0 < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"],
        "TP3 TRAILING RANGE"
    )

    require(
        hedge["h1_atr_multiplier"] == 1.0,
        "H1 ATR"
    )

    require(
        hedge["h2_atr_multiplier"] == 2.0,
        "H2 ATR"
    )

    for stage in ("h1", "h2", "r1", "r2"):

        original = hedge[
            stage + "_original_fraction"
        ]

        opposite = hedge[
            stage + "_opposite_fraction"
        ]

        require(
            0 <= original <= 1,
            stage.upper() + " ORIGINAL"
        )

        require(
            0 <= opposite <= 1,
            stage.upper() + " OPPOSITE"
        )

        require(
            abs(original + opposite - 1.0) < 1e-12,
            stage.upper() + " ALLOCATION"
        )

    require(
        qualification["common"]["mode_priority"]
        == ("BREAKOUT", "STRUCTURE", "SCALP"),
        "MODE PRIORITY"
    )

    require(
        qualification["scalp"]["quality_threshold"]
        == 70.0,
        "SCALP QUALITY"
    )

    require(
        strategy["anti_duplicate_orders"] is True,
        "ANTI DUPLICATE"
    )

    require(
        all(
            market_precision[key] > 0
            for key in (
                "quantity_step",
                "minimum_quantity",
                "price_step",
            )
        ),
        "MARKET PRECISION"
    )

    require(
        safety["real_order_submission_enabled"] is False,
        "REAL CASH DISABLED"
    )

    obsolete_keys = (
        "max_backups",
        "backup_margin_percent",
        "backup_buffer_percent",
        "backup_sizing_mode",
        "backup_trigger_reference",
        "backup_trigger_recalculation",
        "backup_long_liquidation_factor",
        "backup_short_liquidation_factor",
        "backup_multipliers",
        "progressive_backup_funding",
        "full_ladder_reservation_required",
        "exposure_includes_filled_backups",
    )

    require(
        all(
            key not in strategy
            for key in obsolete_keys
        ),
        "OLD BACKUP CONFIGURATION FOUND"
    )

    # ========================================================
    # 2.14 STARTUP REPORT
    # ========================================================

    print("PASS: UNIT 2 CONFIGURATION CREATED",
          flush=True)

    print("PASS: EXCHANGE = WEEX V3",
          flush=True)

    print("PASS: ENVIRONMENT = DEMO",
          flush=True)

    print("DEMO SYMBOL = BTCSUSDT",
          flush=True)

    print(
        "ENTRY MARGIN USDT =",
        float(initial_margin),
        flush=True
    )

    print(
        "ENTRY MARGIN SOURCE =",
        margin_source,
        flush=True
    )

    print(
        "EXPOSURE CAP PERCENT =",
        float(exposure_cap),
        flush=True
    )

    print("EXPOSURE CAP MAXIMUM = 100%",
          flush=True)

    print(
        "LONG LEVERAGE RENDER =",
        float(long_leverage),
        flush=True
    )

    print(
        "SHORT LEVERAGE RENDER =",
        float(short_leverage),
        flush=True
    )

    print(
        "LEVERAGE SOURCE = RENDER MANUAL",
        flush=True
    )

    print("LEVERAGE API READ = NONE",
          flush=True)

    print("LEVERAGE API WRITE = NONE",
          flush=True)

    print(
        "HEDGE MODE =",
        hedge["mode"],
        flush=True
    )

    print("H1 = 1 ATR | 50 ORIGINAL / 50 OPPOSITE",
          flush=True)

    print("H2 = 2 ATR | 0 ORIGINAL / 100 OPPOSITE",
          flush=True)

    print("R1 = 1 ATR | 50 ORIGINAL / 50 OPPOSITE",
          flush=True)

    print("R2 = ENTRY | 100 ORIGINAL / 0 OPPOSITE",
          flush=True)

    print("ATR14 = FROZEN AT ORIGINAL ENTRY",
          flush=True)

    print("STOP LOSS = DISABLED",
          flush=True)

    print("EMERGENCY CLOSE = DISABLED",
          flush=True)

    print("LIQUIDATION PROTECTION = DISABLED",
          flush=True)

    print("OLD BACKUPS = NONE",
          flush=True)

    print("TP ALLOCATION = 10 / 20 / 70",
          flush=True)

    print("SCALP QUALITY = 70",
          flush=True)

    print("HEDGE DEMO EXECUTION = PENDING INTEGRATION",
          flush=True)

    print("REAL CASH EXECUTION = DISABLED",
          flush=True)

    print("UNIT 2 EXCHANGE WRITE = NONE",
          flush=True)

    print("UNIT 2 V12 RESULT = PASS",
          flush=True)

    print("=" * 80, flush=True)

    return config


# ============================================================
# 2.15 RUN UNIT 2
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# 2.16 UNIT 2 -> UNIT 3 READINESS CONTRACT
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

    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get("leverage"),
        dict
    )

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("anti_duplicate_orders") is True

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("hedge", {}).get("enabled") is True

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("hedge", {}).get("mode")
    == "REVERSIBLE_ATR_TWO_STAGE"

    and FRESH_RECONSTRUCTION_CONFIG[
        "leverage"
    ].get("source")
    == "RENDER_MANUAL_CONFIGURATION"
)

if not FRESH_UNIT_2_OPTIMIZATION_READY:

    raise RuntimeError(
        "UNIT 2 V12 OPTIMIZATION READINESS FAILED"
    )

print(
    "UNIT 2 V12 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 2 V12
# UNIT 3 FOLLOWS
# ============================================================
