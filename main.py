
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
# WEEX BOT - UNIT 2
# ADAPTED CENTRAL CONFIGURATION V1
#
# PRIMARY SOURCE: TESTED 17248-LINE MODEL
# HEDGE SOURCE: 16414-LINE MODEL
#
# PRESERVE ORIGINAL UNIT INTERFACES
# UNIVERSAL COIN - DEFAULT NEAR
# MANUAL LEVERAGE - RENDER CONFIGURATION
# ONE ATR HEDGE / RECOVERY CYCLE
# B1-B5 ONLY AFTER FAILED RECOVERY
# DEMO EXECUTION BELONGS TO LATER UNITS
# REAL CASH DISABLED
# ZERO INDENTATION
# ============================================================

import os
import math
from decimal import Decimal, InvalidOperation


# ============================================================
# 2.1 ORIGINAL NUMBER VALIDATION INTERFACE
# ============================================================

def unit_2_v9_number(value, name, allow_zero=False):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 2 INVALID " + name)

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 2 INVALID " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 2 NONFINITE " + name
        )

    if number < 0 or (
        number == 0 and not allow_zero
    ):
        raise RuntimeError(
            "UNIT 2 INVALID RANGE " + name
        )

    return number


def unit_2_adapted_env_number(
    name, default, minimum=None, maximum=None
):

    raw = os.getenv(name, str(default)).strip()

    value = unit_2_v9_number(
        raw, name, allow_zero=(minimum == 0)
    )

    if minimum is not None:
        if value < Decimal(str(minimum)):
            raise RuntimeError(
                "UNIT 2 BELOW MINIMUM: " + name
            )

    if maximum is not None:
        if value > Decimal(str(maximum)):
            raise RuntimeError(
                "UNIT 2 ABOVE MAXIMUM: " + name
            )

    return value


def unit_2_adapted_bool(name, default):

    raw = os.getenv(
        name, "TRUE" if default else "FALSE"
    ).strip().upper()

    if raw in ("TRUE", "1", "YES", "ON"):
        return True

    if raw in ("FALSE", "0", "NO", "OFF"):
        return False

    raise RuntimeError(
        "UNIT 2 INVALID BOOLEAN: " + name
    )


def unit_2_adapted_require(condition, message):

    if not condition:
        raise RuntimeError(
            "UNIT 2 CONFIG INVALID: " + message
        )


# ============================================================
# 2.2 COMPLETE UNIT 2
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)

    log("ADAPTED WORKING MODEL UNIT 2 START")

    require = unit_2_adapted_require

    require(
        FRESH_RECONSTRUCTION_UNIT_1_READY is True,
        "UNIT 1 NOT READY"
    )

    # ========================================================
    # 2.3 UNIVERSAL SYMBOL CONFIGURATION
    # ========================================================

    symbol = os.getenv(
        "WEEX_SYMBOL",
        os.getenv("TRADING_SYMBOL", "NEARUSDT")
    ).strip().upper()

    require(
        symbol.endswith("USDT")
        and symbol[:-4].isalnum()
        and len(symbol) > 4,
        "INVALID MARKET SYMBOL"
    )

    base_coin = symbol[:-4]

    demo_candidate = (
        base_coin + "SUSDT"
    )

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",

        "market_symbol": symbol,
        "base_coin": base_coin,
        "quote_coin": "USDT",

        # Candidate only until verified by exchange.
        "demo_order_symbol": None,
        "demo_symbol_candidate": demo_candidate,
        "demo_symbol_verified": False,

        "contract_precision_verified": False,
        "contract_value_verified": False,
    }

    # ========================================================
    # 2.4 ENTRY MARGIN
    # PRESERVE ORIGINAL ENVIRONMENT VARIABLE
    # ========================================================

    margin_names = (
        "INITIAL_ENTRY_MARGIN_USDT",
        "ENTRY_MARGIN_USDT",
        "ENTRY_FIXED_USDT",
    )

    margin_raw = None
    margin_source = "DEFAULT"

    for name in margin_names:

        value = os.getenv(name)

        if value is not None and value.strip():
            margin_raw = value.strip()
            margin_source = name
            break

    if margin_raw is None:
        margin_raw = "0.5"

    initial_margin = unit_2_v9_number(
        margin_raw, "INITIAL ENTRY MARGIN"
    )

    # ========================================================
    # 2.5 EXPOSURE CAP
    # ========================================================

    exposure_cap = unit_2_adapted_env_number(
        "EXPOSURE_CAP_PERCENT",
        "100",
        0.000001,
        100
    )

    # ========================================================
    # 2.6 MANUAL LEVERAGE
    # PRESERVE BOTH PREVIOUS ENVIRONMENT NAMING FORMS
    # ========================================================

    def leverage_setting(primary, legacy):

        raw = os.getenv(primary)

        if raw is None or not raw.strip():
            raw = os.getenv(legacy)

        require(
            raw is not None and bool(raw.strip()),
            "MISSING LEVERAGE: " + primary
        )

        value = unit_2_v9_number(
            raw.strip(), primary
        )

        require(
            value <= Decimal("200"),
            "LEVERAGE ABOVE CONFIGURED LIMIT"
        )

        return value

    long_leverage = leverage_setting(
        "WEEX_LEVERAGE_LONG",
        "WEEX_DEMO_LONG_LEVERAGE"
    )

    short_leverage = leverage_setting(
        "WEEX_LEVERAGE_SHORT",
        "WEEX_DEMO_SHORT_LEVERAGE"
    )

    leverage = {
        "source": "RENDER_MANUAL_CONFIGURATION",
        "long": float(long_leverage),
        "short": float(short_leverage),

        "read_from_weex": False,
        "write_to_weex": False,
        "automatic_sync": False,

        "exchange_setting_required": True,
        "position_side_specific": True,
    }

    # ========================================================
    # 2.7 ORIGINAL UNIT-LOCAL SAFETY CONTRACT
    #
    # FALSE HERE MEANS UNIT 2 DOES NOT EXECUTE ORDERS.
    # IT DOES NOT BLOCK AUTHORIZED DEMO EXECUTION
    # IN UNIT 12 OR POSITION MANAGEMENT UNITS.
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
    # 2.8 ORIGINAL STRATEGY CONFIGURATION
    # PRESERVE EXISTING KEYS AND MEANINGS
    # ========================================================

    backup_percent = unit_2_adapted_env_number(
        "BACKUP_MARGIN_PERCENT",
        "0.5",
        0.000001,
        100
    )

    buffer_percent = unit_2_adapted_env_number(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
        0.000001,
        99.999
    )

    tp1_roi = unit_2_adapted_env_number(
        "TP1_NET_ROI_PERCENT",
        "20",
        0.000001
    )

    tp2_roi = unit_2_adapted_env_number(
        "TP2_NET_ROI_PERCENT",
        "40",
        0.000001
    )

    require(
        tp2_roi > tp1_roi,
        "TP2 MUST EXCEED TP1"
    )

    strategy = {
        "initial_fixed_usdt": float(initial_margin),
        "initial_margin_percent": 5.0,

        "initial_margin_mode": "FIXED_USDT",
        "fixed_margin_usdt": float(initial_margin),
        "entry_margin_usdt": float(initial_margin),
        "configured_margin_usdt": float(initial_margin),
        "margin_source": margin_source,

        "backup_margin_percent": float(backup_percent),
        "backup_buffer_percent": float(buffer_percent),
        "max_backups": 5,

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        # Preserve tested model factor definitions.
        "backup_long_liquidation_factor": float(
            Decimal("1")
            + buffer_percent / Decimal("100")
        ),

        "backup_short_liquidation_factor": float(
            Decimal("1")
            - buffer_percent / Decimal("100")
        ),

        "exposure_cap_percent": float(exposure_cap),
        "exposure_cap_max_percent": 100.0,
        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_open_hedge_margin": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        "tp1_net_roi_floor_percent": float(tp1_roi),
        "tp2_net_roi_floor_percent": float(tp2_roi),

        "tp1_tp2_min_roi_separation_percent":
            float(tp2_roi - tp1_roi),

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,

        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,
    }

    # ========================================================
    # 2.9 ONE-CYCLE REVERSIBLE ATR HEDGE
    # ADAPTED FROM 16414-LINE MODEL
    # ========================================================

    hedge = {
        "enabled": True,

        # Actual authorization belongs to later units.
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

        "h1_atr_multiplier": 1.0,
        "h1_original_fraction": 0.50,
        "h1_opposite_fraction": 0.50,

        "h2_atr_multiplier": 2.0,
        "h2_original_fraction": 0.0,
        "h2_opposite_fraction": 1.0,

        "r1_atr_multiplier": 1.0,
        "r1_original_fraction": 0.50,
        "r1_opposite_fraction": 0.50,

        "r2_atr_multiplier": 0.0,
        "r2_original_fraction": 1.0,
        "r2_opposite_fraction": 0.0,

        "reversible": True,

        # Latest strategy: only one hedge/recovery cycle.
        "repeatable": False,
        "maximum_recovery_cycles": 1,

        "quantity_step_aware": True,
        "minimum_quantity_required": True,
        "confirmed_fill_required": True,
        "position_reconciliation_required": True,
        "anti_duplicate_orders": True,

        "required_position_mode": "HEDGE",
        "allow_simultaneous_long_short": True,
        "change_exchange_position_mode": False,

        "conventional_stop_loss_enabled": False,

        "bot_mode_independent": True,
        "real_cash_enabled": False,
    }

    strategy["hedge"] = hedge

    # ========================================================
    # 2.10 CONDITIONAL B1-B5
    # ORIGINAL BACKUP SYSTEM PRESERVED
    # ACTIVATION MOVED AFTER FAILED HEDGE RECOVERY
    # ========================================================

    backup_recovery = {
        "enabled": True,
        "maximum_backups": 5,

        "activation":
            "AFTER_FAILED_FIRST_HEDGE_RECOVERY",

        "hedge_cycles_before_backup": 1,

        "require_confirmed_hedge_cycle": True,
        "require_failed_recovery": True,

        "sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "margin_percent": float(backup_percent),

        "trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "respect_exposure_cap": True,
        "require_available_margin": True,
        "require_exchange_quantity_compliance": True,
        "require_confirmed_fill": True,

        "maximum_exposure_percent":
            float(exposure_cap),

        "real_cash_enabled": False,
    }

    strategy["backup_recovery"] = backup_recovery

    # ========================================================
    # 2.11 TRADE BALANCE / PROFIT PROTECTION
    # ========================================================

    strategy["profit_protection"] = {
        "before_tp1":
            "ONE_ATR_HEDGE_THEN_CONDITIONAL_BACKUPS",

        "after_tp1":
            "DYNAMIC_BREAK_EVEN",

        "after_tp2":
            "DYNAMIC_PROFIT_TRAILING",

        "protect_secured_tp1_profit": True,
        "include_entry_fee": True,
        "include_exit_fee": True,
        "include_funding_when_known": True,

        "net_roi_based": True,
    }

    # ========================================================
    # 2.12 MARKET PRECISION
    #
    # NEVER USE BTC PRECISION AS VERIFIED NEAR PRECISION.
    # UNIT 7/8 MUST RESOLVE THE ACTUAL DEMO CONTRACT.
    # ========================================================

    market_precision = {
        "quantity_step": None,
        "minimum_quantity": None,
        "price_step": None,

        "verified": False,
        "source": "PENDING_DEMO_CONTRACT_VERIFICATION",
    }

    # ========================================================
    # 2.13 ORIGINAL HYBRID QUALIFICATION CONTRACT
    # PRESERVED FROM TESTED MODEL
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
    # 2.14 COMPLETE ORIGINAL CONFIGURATION HANDOVER
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
        "qualification": qualification,
        "leverage": leverage,
    }

    # ========================================================
    # 2.15 CONFIGURATION VALIDATION
    # ========================================================

    require(
        config["execution_environment"] == "DEMO",
        "DEMO ENVIRONMENT"
    )

    require(
        initial_margin > 0,
        "ENTRY MARGIN"
    )

    require(
        Decimal("0") < exposure_cap <= Decimal("100"),
        "EXPOSURE CAP"
    )

    require(
        strategy["max_backups"] == 5,
        "BACKUP COUNT"
    )

    require(
        "backup_multipliers" not in strategy,
        "OBSOLETE BACKUP MULTIPLIERS"
    )

    require(
        "leverage_target" not in strategy,
        "HARDCODED LEVERAGE"
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
        qualification["common"]["mode_priority"]
        == ("BREAKOUT", "STRUCTURE", "SCALP"),
        "STRATEGY PRIORITY"
    )

    require(
        hedge["maximum_recovery_cycles"] == 1,
        "HEDGE CYCLE LIMIT"
    )

    for stage in ("h1", "h2", "r1", "r2"):

        original = hedge[
            stage + "_original_fraction"
        ]

        opposite = hedge[
            stage + "_opposite_fraction"
        ]

        require(
            abs(original + opposite - 1.0) < 1e-12,
            "HEDGE STAGE ALLOCATION " + stage
        )

    require(
        safety["real_order_submission_enabled"] is False,
        "REAL CASH DISABLED"
    )

    # ========================================================
    # 2.16 STARTUP REPORT
    # ========================================================

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True
    )

    print(
        "MARKET SYMBOL =",
        symbol,
        flush=True
    )

    print(
        "DEMO SYMBOL CANDIDATE =",
        demo_candidate,
        flush=True
    )

    print(
        "DEMO SYMBOL VERIFIED =",
        exchange["demo_symbol_verified"],
        flush=True
    )

    print(
        "INITIAL MARGIN USDT =",
        float(initial_margin),
        flush=True
    )

    print(
        "INITIAL MARGIN SOURCE =",
        margin_source,
        flush=True
    )

    print(
        "LONG LEVERAGE =",
        float(long_leverage),
        flush=True
    )

    print(
        "SHORT LEVERAGE =",
        float(short_leverage),
        flush=True
    )

    print(
        "EXPOSURE CAP PERCENT =",
        float(exposure_cap),
        flush=True
    )

    print(
        "TP1 NET ROI TARGET =",
        float(tp1_roi),
        flush=True
    )

    print(
        "TP2 NET ROI TARGET =",
        float(tp2_roi),
        flush=True
    )

    print(
        "HEDGE MAXIMUM RECOVERY CYCLES = 1",
        flush=True
    )

    print(
        "BACKUP ACTIVATION =",
        backup_recovery["activation"],
        flush=True
    )

    print(
        "BACKUP COUNT = 5",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "REAL CASH EXECUTION = DISABLED",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return config


# ============================================================
# 2.17 ORIGINAL CONFIGURATION GLOBAL
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# 2.18 ORIGINAL UNIT 2 -> UNIT 3 READINESS INTERFACE
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

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("hedge", {}).get(
        "maximum_recovery_cycles"
    ) == 1
)

if not FRESH_UNIT_2_OPTIMIZATION_READY:

    raise RuntimeError(
        "UNIT 2 ADAPTED OPTIMIZATION READINESS FAILED"
    )

print(
    "UNIT 2 ADAPTED OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)


# ============================================================
# END COMPLETE ADAPTED UNIT 2
# UNIT 3 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 3 ADAPTED V3
# PRIMARY SOURCE: TESTED 17248-LINE MODEL
# WEEX V3 MARK PRICE + FRESHNESS VALIDATION
# UNIVERSAL SYMBOL FROM UNIT 2
# ORIGINAL UNIT 4 HANDOVER PRESERVED
# ZERO INDENTATION
# PUBLIC MARKET READ ONLY
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error


# ============================================================
# 3.1 ORIGINAL MARKET DATA VALIDATION INTERFACE
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
# 3.2 ORIGINAL DETERMINISTIC VALIDATION TESTS
# UNIVERSAL SYMBOL ADAPTATION
# NO HTTP REQUEST
# ============================================================

def unit_3_validation_tests_v2():

    print("=" * 80, flush=True)

    print(
        "UNIT 3 OPTIMIZATION VALIDATION V2 START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 TEST CONFIG MISSING"
        )

    exchange = config.get("exchange", {})

    symbol = exchange.get("market_symbol")

    if not isinstance(symbol, str) or not symbol:
        raise RuntimeError(
            "UNIT 3 TEST SYMBOL MISSING"
        )

    now_ms = 1800000000000

    valid_payload = {
        "symbol": symbol,
        "price": "3.8005",
        "time": now_ms - 1000,
    }

    passed = 0
    failed = 0

    def check(name, condition):

        nonlocal passed, failed

        if condition:
            passed += 1
            verdict = "PASS"
        else:
            failed += 1
            verdict = "FAIL"

        print(
            "UNIT 3 TEST:",
            name,
            "=",
            verdict,
            flush=True
        )

    def rejected(payload, reason):

        try:
            unit_3_validate_mark_payload(
                payload,
                symbol,
                now_ms
            )

        except RuntimeError as exc:
            return str(exc) == reason

        return False

    result = unit_3_validate_mark_payload(
        valid_payload,
        symbol,
        now_ms
    )

    check(
        "VALID MARK PRICE",
        result["price"] == 3.8005
    )

    check(
        "VALID EXCHANGE TIMESTAMP",
        result["exchange_time_ms"] == now_ms - 1000
    )

    check(
        "VALID DATA AGE",
        result["market_age_ms"] == 1000
    )

    wrong_symbol = (
        "BTCUSDT"
        if symbol != "BTCUSDT"
        else "ETHUSDT"
    )

    check(
        "REJECT WRONG SYMBOL",
        rejected(
            {
                **valid_payload,
                "symbol": wrong_symbol
            },
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )
    )

    check(
        "REJECT ZERO PRICE",
        rejected(
            {
                **valid_payload,
                "price": "0"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NEGATIVE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "-1"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NONNUMERIC PRICE",
        rejected(
            {
                **valid_payload,
                "price": "invalid"
            },
            "UNIT 3 INVALID MARKET PRICE"
        )
    )

    check(
        "REJECT NONFINITE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "nan"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT STALE DATA",
        rejected(
            {
                **valid_payload,
                "time": now_ms - 130000
            },
            "UNIT 3 STALE MARKET DATA"
        )
    )

    check(
        "REJECT FUTURE TIMESTAMP",
        rejected(
            {
                **valid_payload,
                "time": now_ms + 20000
            },
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE"
        )
    )

    check(
        "REJECT MISSING TIMESTAMP",
        rejected(
            {
                "symbol": symbol,
                "price": "3.8005"
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
# 3.3 ACTUAL WEEX V3 PUBLIC MARKET DATA READ
# PRESERVE TESTED MODEL REQUEST METHOD
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)

    log("FRESH RECONSTRUCTION UNIT 3 START")

    if FRESH_UNIT_2_OPTIMIZATION_READY is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 VALIDATION NOT READY"
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

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 INVALID API VERSION"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID CONTRACT BASE URL"
        )

    # ========================================================
    # UNIVERSAL SYMBOL ADAPTATION
    # ORIGINAL MODEL USED HARDCODED BTCUSDT
    # ========================================================

    market_symbol = exchange.get("market_symbol")

    if (
        not isinstance(market_symbol, str)
        or not market_symbol.endswith("USDT")
        or len(market_symbol) <= 4
    ):
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

    # ========================================================
    # PRESERVE ORIGINAL UNIT 3 READ-ONLY SAFETY
    # THESE FLAGS APPLY TO UNIT 3 ONLY
    # ========================================================

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
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True
    )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True
    )

    # ========================================================
    # ORIGINAL TESTED WEEX V3 ENDPOINT
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
                "WEEX-Hybrid-Market-Data-V2",
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

    print(
        "UNIT 3 REQUESTED SYMBOL =",
        market_symbol,
        flush=True
    )

    # ========================================================
    # MEASURE ACTUAL REQUEST LATENCY
    # DO NOT REUSE PREVIOUS DATA AFTER FAILURE
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
    # ORIGINAL UNIT 3 -> UNIT 4 HANDOVER
    # PRESERVE ALL EIGHT EXISTING SNAPSHOT FIELDS
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
    # ACTUAL WEEX RESPONSE REPORT
    # ========================================================

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True
    )

    print(
        "PASS: UNIT 3 LIVE MARK PRICE SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "PASS: UNIT 3 LIVE MARK PRICE =",
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
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# 3.4 RUN ORIGINAL VALIDATION TESTS FIRST
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v2()
)


# ============================================================
# 3.5 RUN ACTUAL WEEX PUBLIC MARKET READ SECOND
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3 ADAPTED V3
# UNIT 4 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE UNIT 4 V5 NEAR ADAPTATION
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
# END UNIT 4 PART 1
# PART 2 CONTINUES BELOW THIS LINE
# DO NOT DEPLOY YET
# ============================================================


# ============================================================
# UNIT 4 PART 2 OF 2
# COMPLETE EXECUTABLE MARKET ANALYSIS
# CONTINUES DIRECTLY FROM PART 1
# ZERO INDENTATION
# ============================================================

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

    exchange = config.get("exchange", {})
    qualification = config.get("qualification", {})
    safety = config.get("safety", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, qualification, safety)
    ):
        raise RuntimeError("UNIT 4 CONFIG STRUCTURE INVALID")

    market_symbol = exchange.get("market_symbol")

    if (
        not isinstance(market_symbol, str)
        or not market_symbol.endswith("USDT")
        or len(market_symbol) <= 4
    ):
        raise RuntimeError("UNIT 4 INVALID CONFIGURED SYMBOL")

    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != market_symbol
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError("UNIT 4 UNIT 3 HANDOVER INVALID")

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or safety.get("public_market_data_read_enabled") is not True
    ):
        raise RuntimeError("UNIT 4 EXCHANGE CONFIG INVALID")

    if tuple(
        qualification.get("common", {}).get("mode_priority", ())
    ) != ("BREAKOUT", "STRUCTURE", "SCALP"):
        raise RuntimeError("UNIT 4 MODE PRIORITY INVALID")

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

    market_time_ms = int(unit_4_v5_positive(
        market["exchange_time_ms"], "MARKET TIMESTAMP", False
    ))

    live_mark = unit_4_v5_positive(
        market["price"], "MARK PRICE", False
    )

    current_time_ms = int(time.time() * 1000)

    if not (
        -15000 <= current_time_ms - market_time_ms
        <= max_age * 1000
    ):
        raise RuntimeError("UNIT 4 STALE UNIT 3 MARK PRICE")

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError("UNIT 4 WEEX BASE URL INVALID")

    # ========================================================
    # LIVE WEEX V3 PUBLIC MARK-PRICE CANDLES
    # ========================================================

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
            "User-Agent": "WEEX-Unit4-Adjustable-V5",
        }
    )

    if request.get_method() != "GET" or request.data is not None:
        raise RuntimeError("UNIT 4 HTTP SAFETY FAILURE")

    started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            http_status = response.getcode()
            payload = response.read().decode("utf-8")

    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise RuntimeError(
            "UNIT 4 WEEX CANDLE REQUEST FAILED"
        ) from exc

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

    if not (0 <= candle_age_seconds <= max_candle_age):
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
            (latest_close - reference) / reference * 100.0
        )

    # ========================================================
    # ATR14 - AVERAGE TRUE RANGE
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
        raise RuntimeError("UNIT 4 ATR14 INVALID")

    atr_percent = atr14 / latest_close * 100.0

    # ========================================================
    # THREE DIRECTION VOTES
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
            raise RuntimeError(
                "UNIT 4 UNSUPPORTED MOMENTUM PERIOD"
            )

        return moves[period]

    # ========================================================
    # BREAKOUT - DEVELOPING AND CONFIRMED
    # ========================================================

    breakout_lookback = unit_4_v5_integer(
        b["lookback_candles"], "BREAKOUT LOOKBACK", 2, 45
    )

    reference_candles = closed[
        -breakout_lookback - 1:-1
    ]

    support = min(x["low"] for x in reference_candles)
    resistance = max(x["high"] for x in reference_candles)

    proximity = unit_4_v5_positive(
        b["proximity_atr"], "BREAKOUT PROXIMITY"
    )

    confirmation = unit_4_v5_positive(
        b["confirmation_atr"], "BREAKOUT CONFIRMATION"
    )

    breakout_max_extension = unit_4_v5_positive(
        b["maximum_extension_atr"],
        "BREAKOUT EXTENSION", False
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
            and votes_sufficient(
                side, b["direction_votes_required"]
            )
            and fast_ok
            and slow_ok
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

    # ========================================================
    # STRUCTURE - EMA19/50/200 + MOMENTUM
    # ========================================================

    alignment = str(s["ema_alignment_mode"]).upper()

    if alignment not in ("STRICT", "EARLY"):
        raise RuntimeError(
            "UNIT 4 INVALID STRUCTURE ALIGNMENT MODE"
        )

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
        s["pullback_tolerance_atr"],
        "STRUCTURE PULLBACK"
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
            and votes_sufficient(
                side, s["direction_votes_required"]
            )
            and fast_ok
            and slow_ok
            and separation >= structure_min_separation
            and abs(signed_distance) <= structure_max_extension
            and (pullback_ok or continuation_ok)
        )

    structure_developing_long = structure_eligible("LONG")
    structure_developing_short = structure_eligible("SHORT")

    structure_fast_confirmed = (
        unit_4_v5_same_direction(
            fast_structure_move, structure_side
        )
    )

    structure_slow_confirmed = (
        unit_4_v5_same_direction(
            slow_structure_move, structure_side
        )
    )

    # ========================================================
    # SCALP - SIDEWAYS ONLY
    # PROTECT DEVELOPING BREAKOUT AND STRUCTURE
    # ========================================================

    scalp_lookback = unit_4_v5_integer(
        p["range_lookback_candles"],
        "SCALP LOOKBACK", 2, 45
    )

    scalp_history = closed[-scalp_lookback - 1:-1]

    scalp_high = max(x["high"] for x in scalp_history)
    scalp_low = min(x["low"] for x in scalp_history)

    ema_cluster = (
        max(ema19, ema50, ema100, ema200)
        - min(ema19, ema50, ema100, ema200)
    )

    compression_atr = ema_cluster / atr14

    scalp_range_atr = (
        scalp_high - scalp_low
    ) / atr14

    momentum15_atr = (
        abs(latest_close - prices[-16]) / atr14
    )

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
            p["ema_compression_atr_max"],
            "SCALP EMA COMPRESSION"
        )
        and scalp_range_atr <= unit_4_v5_positive(
            p["range_atr_max"],
            "SCALP RANGE"
        )
        and momentum15_atr <= unit_4_v5_positive(
            p["momentum_atr_max"],
            "SCALP MOMENTUM"
        )
        and not higher_mode_developing
    )

    price_extension_atr = (
        abs(latest_close - ema19) / atr14
    )

    price_overextended = bool(
        price_extension_atr > structure_max_extension
    )

    # ========================================================
    # PUBLISH ADJUSTABLES TO UNITS 5 AND 6
    # ========================================================

    common_cfg = qualification["common"]
    breakout_cfg = qualification["breakout"]
    structure_cfg = qualification["structure"]
    scalp_cfg = qualification["scalp"]

    common_cfg["direction_votes_required"] = (
        common_votes_required
    )

    breakout_cfg.update({
        "enabled": bool(b["enabled"]),
        "developing_candidate_enabled": bool(
            b["developing_candidate_enabled"]
        ),
        "support_resistance_lookback": breakout_lookback,
        "developing_proximity_atr": proximity,
        "confirmation_distance_atr": confirmation,
        "max_price_extension_atr": breakout_max_extension,
        "minimum_atr_percent": breakout_atr_min,
        "direction_votes_required":
            b["direction_votes_required"],
        "fast_momentum_minutes":
            b["fast_momentum_minutes"],
        "slow_momentum_minutes":
            b["slow_momentum_minutes"],
        "require_fast_momentum":
            b["require_fast_momentum"],
        "require_slow_momentum":
            b["require_slow_momentum"],
    })

    structure_cfg.update({
        "enabled": bool(s["enabled"]),
        "ema_alignment_mode": alignment,
        "direction_votes_required":
            s["direction_votes_required"],
        "minimum_ema_separation_percent":
            structure_min_separation,
        "pullback_tolerance_atr": structure_pullback,
        "allow_continuation_entry":
            bool(s["allow_continuation_entry"]),
        "max_price_extension_atr":
            structure_max_extension,
        "fast_momentum_minutes":
            s["fast_momentum_minutes"],
        "slow_momentum_minutes":
            s["slow_momentum_minutes"],
        "require_fast_momentum":
            s["require_fast_momentum"],
        "require_slow_momentum":
            s["require_slow_momentum"],
    })

    scalp_cfg.update({
        "enabled": bool(p["enabled"]),
        "require_sideways_market":
            bool(p["require_sideways_market"]),
        "ema_compression_atr_max":
            p["ema_compression_atr_max"],
        "range20_atr_max": p["range_atr_max"],
        "momentum15_atr_multiplier_max":
            p["momentum_atr_max"],
        "preliminary_ema_separation_percent":
            p["preliminary_ema_separation_percent"],
        "preliminary_move_5m_percent":
            p["preliminary_move_5m_percent"],
        "quality_threshold":
            p["quality_threshold"],
        "minimum_fee_coverage_multiplier":
            p["minimum_fee_coverage_multiplier"],
    })

    # ========================================================
    # ORIGINAL UNIT 4 -> UNIT 5 EVIDENCE HANDOVER
    # ========================================================

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

        "newest_returned_candle_closed": (
            candles[-1]["close_time_ms"] <= market_time_ms
        ),

        "source": "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "atr14": atr14,
        "atr_percent": atr_percent,

        "support20": support,
        "resistance20": resistance,

        "range20_atr_ratio": (
            resistance - support
        ) / atr14,

        "near_resistance": bool(
            latest_close >= resistance - proximity * atr14
        ),

        "near_support": bool(
            latest_close <= support + proximity * atr14
        ),

        "breakout_confirmed_long":
            breakout_confirmed_long,
        "breakout_confirmed_short":
            breakout_confirmed_short,

        "breakout_developing_long":
            breakout_developing_long,
        "breakout_developing_short":
            breakout_developing_short,

        "structure_developing_long":
            structure_developing_long,
        "structure_developing_short":
            structure_developing_short,

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
            "UNIT4_V5_FULLY_INTEGRATED",

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

    # ========================================================
    # VERIFY DOWNSTREAM INPUTS
    # ========================================================

    required_fields = (
        "strategy_evidence_version",
        "exchange_time_ms",
        "latest_close_time_ms",
        "latest_close",
        "ema19",
        "ema50",
        "ema200",
        "atr14",
        "move_5m_pct",
        "move_15m_pct",
        "direction_evidence",
        "direction_long_votes",
        "direction_short_votes",
        "breakout_confirmed_long",
        "breakout_confirmed_short",
        "breakout_developing_long",
        "breakout_developing_short",
        "structure_developing_long",
        "structure_developing_short",
        "sideways_candidate",
        "price_overextended",
        "structure_trend_direction",
        "scalp_preliminary_ema_min_pct",
        "scalp_preliminary_move_min_pct",
    )

    missing = [
        key for key in required_fields
        if key not in snapshot
    ]

    if missing:
        raise RuntimeError(
            "UNIT 4 HANDOVER MISSING: " + str(missing)
        )

    # ========================================================
    # RENDER LOG REPORT
    # ========================================================

    print("UNIT 4 MARKET SYMBOL =", market_symbol, flush=True)
    print("UNIT 4 HTTP STATUS =", http_status, flush=True)

    print(
        "UNIT 4 REQUEST LATENCY MS =",
        round(latency_ms, 2), flush=True
    )

    print(
        "UNIT 4 CLOSED CANDLES =",
        len(closed), flush=True
    )

    print("UNIT 4 ATR14 =", round(atr14, 4), flush=True)
    print("UNIT 4 DIRECTION =", direction, flush=True)

    print(
        "UNIT 4 DIRECTION VOTES =",
        long_votes, "/", short_votes, flush=True
    )

    print(
        "UNIT 4 BREAKOUT PROXIMITY ATR =",
        proximity, flush=True
    )

    print(
        "UNIT 4 BREAKOUT CONFIRMATION ATR =",
        confirmation, flush=True
    )

    for name, value in (
        ("BREAKOUT CONFIRMED LONG", breakout_confirmed_long),
        ("BREAKOUT CONFIRMED SHORT", breakout_confirmed_short),
        ("BREAKOUT DEVELOPING LONG", breakout_developing_long),
        ("BREAKOUT DEVELOPING SHORT", breakout_developing_short),
        ("STRUCTURE DEVELOPING LONG", structure_developing_long),
        ("STRUCTURE DEVELOPING SHORT", structure_developing_short),
    ):
        print("UNIT 4", name, "=", value, flush=True)

    print(
        "UNIT 4 STRUCTURE EMA MODE =",
        alignment, flush=True
    )

    print(
        "UNIT 4 STRUCTURE TREND SIDE =",
        structure_side, flush=True
    )

    print(
        "UNIT 4 SCALP QUALITY TARGET =",
        p["quality_threshold"], flush=True
    )

    print(
        "UNIT 4 SCALP SIDEWAYS =",
        sideways_candidate, flush=True
    )

    print(
        "UNIT 4 SCALP MIN MOVE 5M % =",
        p["preliminary_move_5m_percent"], flush=True
    )

    print(
        "UNIT 4 PRICE OVEREXTENDED =",
        price_overextended, flush=True
    )

    print(
        "UNIT 4 EVIDENCE VERSION =",
        snapshot["strategy_evidence_version"], flush=True
    )

    print(
        "UNIT 4 TUNING REVISION =",
        snapshot["qualification_tuning_revision"], flush=True
    )

    print(
        "PASS: UNIT 4 COMPLETE CORE AND ADAPTER",
        flush=True
    )

    print(
        "PASS: UNIT 4 TO UNIT 5 HANDOVER",
        flush=True
    )

    print("UNIT 4 EXCHANGE WRITE = NONE", flush=True)

    print(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 4 ADAPTER RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return snapshot


# ============================================================
# 4.5 SINGLE EXECUTION CALL
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END COMPLETE UNIT 4 V5 NEAR ADAPTATION
# UNIT 5 FOLLOWS
# ZERO INDENTATION
# ============================================================
