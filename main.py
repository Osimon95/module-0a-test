
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



# ============================================================
# WEEX REVERSIBLE ATR HEDGE BOT
# COMPLETE UNIT 3 V3
# WEEX V3 LIVE MARK PRICE + FRESHNESS VALIDATION
#
# ADAPTED FROM ORIGINAL 17,208-LINE MODEL
# COMPATIBLE WITH UNIT 2 V12
# PRESERVES ORIGINAL UNIT 4 HANDOVER
#
# PUBLIC MARKET DATA ONLY IN THIS UNIT
# DEMO ORDER EXECUTION BELONGS TO LATER UNITS
# ZERO INDENTATION
# ============================================================

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request


# ============================================================
# 3.1 VALIDATE WEEX MARKET RESPONSE
# PURE VALIDATION - NO HTTP REQUEST
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

    if payload.get("symbol") != expected_symbol:
        raise RuntimeError(
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )

    try:
        price = float(payload.get("price"))
    except (TypeError, ValueError, OverflowError):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET PRICE"
        )

    if not math.isfinite(price) or price <= 0:
        raise RuntimeError(
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )

    timestamp = payload.get("time")

    if (
        not isinstance(timestamp, int)
        or isinstance(timestamp, bool)
        or timestamp <= 0
    ):
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
# 3.2 ORIGINAL VALIDATION TESTS
# SYNTHETIC INPUTS - NO EXCHANGE REQUEST
# ============================================================

def unit_3_validation_tests_v2():

    print("=" * 80, flush=True)
    print(
        "UNIT 3 OPTIMIZATION VALIDATION V3 START",
        flush=True
    )

    now_ms = 1800000000000

    valid_payload = {
        "symbol": "BTCUSDT",
        "price": "80000.5",
        "time": now_ms - 1000,
    }

    passed = 0
    failed = 0

    def check(name, condition):

        nonlocal passed, failed

        verdict = "PASS" if condition else "FAIL"

        if condition:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 3 TEST:",
            name,
            "=",
            verdict,
            flush=True
        )

    def rejected(payload, expected_error):

        try:
            unit_3_validate_mark_payload(
                payload,
                "BTCUSDT",
                now_ms
            )
        except RuntimeError as exc:
            return str(exc) == expected_error

        return False

    validated = unit_3_validate_mark_payload(
        valid_payload,
        "BTCUSDT",
        now_ms
    )

    check(
        "VALID MARK PRICE",
        validated["price"] == 80000.5
    )

    check(
        "VALID EXCHANGE TIMESTAMP",
        validated["exchange_time_ms"] == now_ms - 1000
    )

    check(
        "VALID DATA AGE",
        validated["market_age_ms"] == 1000
    )

    check(
        "REJECT WRONG SYMBOL",
        rejected(
            {**valid_payload, "symbol": "ETHUSDT"},
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )
    )

    check(
        "REJECT ZERO PRICE",
        rejected(
            {**valid_payload, "price": "0"},
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NEGATIVE PRICE",
        rejected(
            {**valid_payload, "price": "-1"},
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NONNUMERIC PRICE",
        rejected(
            {**valid_payload, "price": "invalid"},
            "UNIT 3 INVALID MARKET PRICE"
        )
    )

    check(
        "REJECT NONFINITE PRICE",
        rejected(
            {**valid_payload, "price": "nan"},
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT STALE DATA",
        rejected(
            {**valid_payload, "time": now_ms - 130000},
            "UNIT 3 STALE MARKET DATA"
        )
    )

    check(
        "REJECT FUTURE TIMESTAMP",
        rejected(
            {**valid_payload, "time": now_ms + 20000},
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE"
        )
    )

    check(
        "REJECT MISSING TIMESTAMP",
        rejected(
            {
                "symbol": "BTCUSDT",
                "price": "80000.5",
            },
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )
    )

    check(
        "REJECT INVALID PAYLOAD",
        rejected(
            [],
            "UNIT 3 INVALID RESPONSE TYPE"
        )
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
            "UNIT 3 OPTIMIZATION VALIDATION FAILED"
        )

    print(
        "UNIT 3 OPTIMIZATION VALIDATION RESULT = PASS",
        flush=True
    )

    print(
        "UNIT 3 TEST EXCHANGE WRITE = NONE",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# 3.3 REAL WEEX V3 PUBLIC MARK-PRICE RETRIEVAL
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 3 V3 START")

    # --------------------------------------------------------
    # VALIDATE PREVIOUS UNITS
    # --------------------------------------------------------

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 1 NOT READY"
        )

    if FRESH_UNIT_2_OPTIMIZATION_READY is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 NOT READY"
        )

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 INVALID UNIT 2 CONFIGURATION"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE CONFIG"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 3 INVALID SAFETY CONFIG"
        )

    # --------------------------------------------------------
    # PRESERVE ORIGINAL EXCHANGE SETTINGS
    # --------------------------------------------------------

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 INVALID API VERSION"
        )

    base_url = exchange.get(
        "contract_base_url"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID CONTRACT BASE URL"
        )

    market_symbol = exchange.get(
        "market_symbol"
    )

    if market_symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 INVALID MARKET SYMBOL"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 3 INVALID EXECUTION ENVIRONMENT"
        )

    if (
        safety.get("public_market_data_read_enabled")
        is not True
    ):
        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
        )

    # --------------------------------------------------------
    # UNIT-LOCAL READ-ONLY CONTRACT
    # THIS DOES NOT DISABLE LATER DEMO ORDER EXECUTION
    # --------------------------------------------------------

    forbidden = (
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    )

    for key in forbidden:

        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 3 UNSAFE CONFIGURATION: " + key
            )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 V12 CONFIGURATION",
        flush=True
    )

    print(
        "PASS: UNIT 3 PUBLIC MARKET READ SAFETY",
        flush=True
    )

    # ========================================================
    # 3.4 WEEX PUBLIC API REQUEST
    # ========================================================

    endpoint = "/capi/v3/market/symbolPrice"
    price_type = "MARK"

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": price_type,
    })

    request_url = (
        base_url + endpoint + "?" + query
    )

    request = urllib.request.Request(
        url=request_url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent":
                "WEEX-Hybrid-Market-Data-V3",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 3 NON-READ-ONLY HTTP REQUEST"
        )

    print(
        "PASS: UNIT 3 ENDPOINT = WEEX V3 SYMBOL PRICE",
        flush=True
    )

    print(
        "PASS: UNIT 3 HTTP METHOD = GET",
        flush=True
    )

    print(
        "PASS: UNIT 3 PRICE TYPE = MARK",
        flush=True
    )

    # ========================================================
    # 3.5 MAKE REQUEST AND MEASURE LATENCY
    # ========================================================

    request_start = time.monotonic()

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw_body = (
                response.read()
                .decode("utf-8")
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:
            error_body = (
                exc.read()
                .decode("utf-8")
            )
        except Exception:
            pass

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            error_body[:500],
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX MARKET HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX CONNECTION FAILED"
        ) from exc

    except Exception as exc:

        print(
            "UNIT 3 UNEXPECTED REQUEST ERROR =",
            repr(exc),
            flush=True
        )

        raise

    received_time_ms = int(
        time.time() * 1000
    )

    latency_ms = round(
        (time.monotonic() - request_start) * 1000,
        2
    )

    # ========================================================
    # 3.6 VALIDATE ACTUAL EXCHANGE RESPONSE
    # ========================================================

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 INVALID HTTP STATUS"
        )

    if not raw_body:
        raise RuntimeError(
            "UNIT 3 EMPTY MARKET RESPONSE"
        )

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET JSON"
        ) from exc

    validated = unit_3_validate_mark_payload(
        payload=payload,
        expected_symbol=market_symbol,
        received_time_ms=received_time_ms
    )

    live_price = validated["price"]

    exchange_time_ms = validated[
        "exchange_time_ms"
    ]

    market_age_ms = validated[
        "market_age_ms"
    ]

    # ========================================================
    # 3.7 ORIGINAL UNIT 3 -> UNIT 4 HANDOVER
    # PRESERVE ALL EIGHT FIELDS
    # ========================================================

    market_snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": market_symbol,
        "price": live_price,
        "price_type": price_type,
        "exchange_time_ms": exchange_time_ms,
        "source": "WEEX_V3_PUBLIC_MARK_PRICE",
        "read_only": True,
    }

    required_fields = (
        "exchange",
        "api_version",
        "symbol",
        "price",
        "price_type",
        "exchange_time_ms",
        "source",
        "read_only",
    )

    if any(
        key not in market_snapshot
        for key in required_fields
    ):
        raise RuntimeError(
            "UNIT 3 MARKET SNAPSHOT INCOMPLETE"
        )

    # ========================================================
    # 3.8 LIVE RESULT REPORT
    # ========================================================

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True
    )

    print(
        "PASS: UNIT 3 LIVE BTC MARK PRICE =",
        live_price,
        flush=True
    )

    print(
        "PASS: UNIT 3 MARKET TIMESTAMP =",
        exchange_time_ms,
        flush=True
    )

    print(
        "UNIT 3 MARKET AGE MS =",
        market_age_ms,
        flush=True
    )

    print(
        "UNIT 3 REQUEST LATENCY MS =",
        latency_ms,
        flush=True
    )

    print(
        "UNIT 3 MAXIMUM MARKET AGE MS = 120000",
        flush=True
    )

    print(
        "PASS: UNIT 3 MARKET DATA FRESHNESS = TRUE",
        flush=True
    )

    print(
        "PASS: UNIT 3 NORMALIZED MARKET SNAPSHOT",
        flush=True
    )

    print(
        "PASS: UNIT 3 HANDOVER READY FOR UNIT 4",
        flush=True
    )

    print(
        "UNIT 3 LEVERAGE API READ = NONE",
        flush=True
    )

    print(
        "UNIT 3 LEVERAGE API WRITE = NONE",
        flush=True
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 3 V3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# 3.9 RUN VALIDATION TESTS
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v2()
)


# ============================================================
# 3.10 PERFORM REAL WEEX MARKET REQUEST
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3 V3
# UNIT 4 FOLLOWS
# ============================================================



# START COMPLETE UNIT 4 V5 REPLACEMENT
# WEEX MARK DATA + EMA + ATR + ADJUSTABLE STRATEGIES
# ONE COMPLETE UNIT / ZERO INDENTATION
# NO SEPARATE ADAPTER / NO ORDER SUBMISSION
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error


# ============================================================
# 4.1 CENTRAL ADJUSTABLE QUALIFICATION PARAMETERS
# ============================================================
# Change values here to tune strategy sensitivity.
# These settings are also published into Unit 2's
# qualification configuration for downstream units.
#
# EARLY structure uses EMA19/50 direction.
# STRICT structure uses EMA19/50/200 alignment.
#
# SCALP remains subordinate to developing or qualified
# BREAKOUT and STRUCTURE candidates.
# ============================================================

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


# ============================================================
# 4.2 GENERAL VALIDATION HELPERS
# ============================================================

def unit_4_v5_number(value, name):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 4 INVALID NUMBER: " + name
        )

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID NUMBER: " + name
        ) from exc

    if not math.isfinite(result):
        raise RuntimeError(
            "UNIT 4 NONFINITE NUMBER: " + name
        )

    return result


def unit_4_v5_positive(value, name, allow_zero=True):

    result = unit_4_v5_number(value, name)

    if result < 0 or (result == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 4 INVALID RANGE: " + name
        )

    return result


def unit_4_v5_integer(value, name, minimum, maximum):

    result = unit_4_v5_number(value, name)

    if (
        not result.is_integer()
        or not minimum <= result <= maximum
    ):
        raise RuntimeError(
            "UNIT 4 INVALID INTEGER: " + name
        )

    return int(result)


def unit_4_v5_ema(prices, period):

    if len(prices) < period:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT EMA HISTORY"
        )

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


# ============================================================
# 4.3 VALIDATE CLOSED WEEX CANDLES
# ============================================================

def unit_4_v5_normalize_candles(rows, market_time_ms):

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 4 INVALID KLINE RESPONSE"
        )

    candles = []

    for row in rows:

        if not isinstance(row, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 INVALID KLINE ROW"
            )

        if len(row) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE KLINE ROW"
            )

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
            raise RuntimeError(
                "UNIT 4 INVALID OHLC DATA"
            )

        if (
            candle["volume"] < 0
            or candle["close_time_ms"]
            <= candle["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE DATA"
            )

        candles.append(candle)

    candles.sort(
        key=lambda item: item["open_time_ms"]
    )

    for i in range(1, len(candles)):

        if (
            candles[i]["open_time_ms"]
            - candles[i - 1]["open_time_ms"]
        ) != 60000:
            raise RuntimeError(
                "UNIT 4 CANDLE GAP OR DUPLICATE"
            )

    closed = [
        c for c in candles
        if c["close_time_ms"] <= market_time_ms
    ]

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED HISTORY"
        )

    return candles, closed


# ============================================================
# 4.4 COMPLETE UNIT 4 MARKET ANALYSIS
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)
    print("UNIT 4 COMPLETE ADJUSTABLE V5 START", flush=True)

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    tuning = UNIT_4_V5_TUNING

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 CONFIG MISSING")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 MARKET SNAPSHOT MISSING")

    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != "BTCUSDT"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 3 HANDOVER INVALID"
        )

    exchange = config.get("exchange", {})
    qualification = config.get("qualification", {})
    safety = config.get("safety", {})

    if not all(
        isinstance(section, dict)
        for section in (exchange, qualification, safety)
    ):
        raise RuntimeError(
            "UNIT 4 CONFIG STRUCTURE INVALID"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or safety.get(
            "public_market_data_read_enabled"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 4 EXCHANGE CONFIG INVALID"
        )

    if tuple(
        qualification.get("common", {}).get(
            "mode_priority", ()
        )
    ) != ("BREAKOUT", "STRUCTURE", "SCALP"):
        raise RuntimeError(
            "UNIT 4 MODE PRIORITY INVALID"
        )

    b = tuning["breakout"]
    s = tuning["structure"]
    p = tuning["scalp"]
    c = tuning["common"]

    max_age = unit_4_v5_positive(
        c["market_age_seconds_max"],
        "MARKET AGE LIMIT",
        False
    )

    max_candle_age = unit_4_v5_positive(
        c["candle_age_seconds_max"],
        "CANDLE AGE LIMIT",
        False
    )

    market_time_ms = int(
        unit_4_v5_positive(
            market["exchange_time_ms"],
            "MARKET TIMESTAMP",
            False
        )
    )

    live_mark = unit_4_v5_positive(
        market["price"], "MARK PRICE", False
    )

    current_time_ms = int(time.time() * 1000)

    if not (
        0 <= current_time_ms - market_time_ms
        <= max_age * 1000
    ):
        raise RuntimeError(
            "UNIT 4 STALE UNIT 3 MARK PRICE"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 WEEX BASE URL INVALID"
        )

    # ========================================================
    # LIVE PUBLIC MARK-PRICE CANDLES
    # ========================================================

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 300,
    })

    request = urllib.request.Request(
        base_url + endpoint + "?" + query,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit4-Adjustable-V5",
        }
    )

    started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            http_status = response.getcode()
            payload = response.read().decode("utf-8")

    except (urllib.error.HTTPError,
            urllib.error.URLError) as exc:
        raise RuntimeError(
            "UNIT 4 WEEX CANDLE REQUEST FAILED"
        ) from exc

    latency_ms = (
        time.monotonic() - started
    ) * 1000.0

    if http_status != 200:
        raise RuntimeError(
            "UNIT 4 WEEX HTTP STATUS NOT 200"
        )

    try:
        rows = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 WEEX JSON INVALID"
        ) from exc

    candles, closed = unit_4_v5_normalize_candles(
        rows, market_time_ms
    )

    latest = closed[-1]
    previous = closed[-2]

    candle_age_seconds = (
        market_time_ms - latest["close_time_ms"]
    ) / 1000.0

    if not (
        0 <= candle_age_seconds <= max_candle_age
    ):
        raise RuntimeError(
            "UNIT 4 CLOSED CANDLE STALE"
        )

    prices = [item["close"] for item in closed]

    ema19 = unit_4_v5_ema(prices, 19)
    ema50 = unit_4_v5_ema(prices, 50)
    ema100 = unit_4_v5_ema(prices, 100)
    ema200 = unit_4_v5_ema(prices, 200)

    latest_close = latest["close"]
    previous_close = previous["close"]

    separation = abs(
        ema19 - ema50
    ) / ema50 * 100.0

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

    # ========================================================
    # ATR14
    # ========================================================

    true_ranges = []

    for i in range(1, len(closed)):

        item = closed[i]
        previous_price = closed[i - 1]["close"]

        true_ranges.append(max(
            item["high"] - item["low"],
            abs(item["high"] - previous_price),
            abs(item["low"] - previous_price)
        ))

    atr14 = sum(true_ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError(
            "UNIT 4 ATR14 INVALID"
        )

    atr_percent = (
        atr14 / latest_close
    ) * 100.0

    # ========================================================
    # DIRECTION VOTES
    # ========================================================

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
        "COMMON DIRECTION VOTES",
        1, 3
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

        count = (
            long_votes if side == "LONG"
            else short_votes
        )

        return count >= unit_4_v5_integer(
            required,
            "STRATEGY DIRECTION VOTES",
            1, 3
        )

    def momentum_at(period):

        period = unit_4_v5_integer(
            period,
            "MOMENTUM PERIOD",
            1, 120
        )

        if period not in moves:
            raise RuntimeError(
                "UNIT 4 UNSUPPORTED MOMENTUM PERIOD"
            )

        return moves[period]

    # ========================================================
    # ADJUSTABLE BREAKOUT
    # ========================================================

    breakout_lookback = unit_4_v5_integer(
        b["lookback_candles"],
        "BREAKOUT LOOKBACK",
        2, 45
    )

    reference_candles = closed[
        -breakout_lookback - 1:-1
    ]

    support = min(
        item["low"] for item in reference_candles
    )

    resistance = max(
        item["high"] for item in reference_candles
    )

    proximity = unit_4_v5_positive(
        b["proximity_atr"],
        "BREAKOUT PROXIMITY"
    )

    confirmation = unit_4_v5_positive(
        b["confirmation_atr"],
        "BREAKOUT CONFIRMATION"
    )

    breakout_max_extension = unit_4_v5_positive(
        b["maximum_extension_atr"],
        "BREAKOUT EXTENSION",
        False
    )

    breakout_atr_min = unit_4_v5_positive(
        b["minimum_atr_percent"],
        "BREAKOUT MIN ATR"
    )

    def breakout_eligible(side):

        fast_ok = (
            not b["require_fast_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["fast_momentum_minutes"]),
                side
            )
        )

        slow_ok = (
            not b["require_slow_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["slow_momentum_minutes"]),
                side
            )
        )

        return bool(
            b["enabled"]
            and direction == side
            and votes_sufficient(
                side, b["direction_votes_required"]
            )
            and fast_ok
            and slow_ok
            and atr_percent >= breakout_atr_min
        )
