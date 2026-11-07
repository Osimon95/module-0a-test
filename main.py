# ============================================================
# WEEX BOT - UNIT 1
# ORIGINAL WORKING MODEL
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
# START COMPLETE UNIT 2 V10
# 17248 V9 CONFIGURATION PATH + CURRENT MODEL ADAPTER
# UNIVERSAL USDT / WEEX DEMO ONLY
# ZERO INDENTATION
# ============================================================

import os
import re
from decimal import Decimal, InvalidOperation


def unit_2_v9_number(value, name, allow_zero=False):
    if isinstance(value, bool):
        raise RuntimeError("UNIT 2 INVALID " + name)

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError("UNIT 2 INVALID " + name) from exc

    if not number.is_finite():
        raise RuntimeError("UNIT 2 NONFINITE " + name)

    if number < 0 or (number == 0 and not allow_zero):
        raise RuntimeError("UNIT 2 INVALID RANGE " + name)

    return number


def unit_2_env_number(
    names, default, minimum=0, maximum=None
):
    if isinstance(names, str):
        names = (names,)

    selected = "DEFAULT"
    raw = str(default)

    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            raw = value.strip()
            selected = name
            break

    number = unit_2_v9_number(
        raw, selected, allow_zero=(minimum == 0)
    )

    if number < Decimal(str(minimum)):
        raise RuntimeError("UNIT 2 BELOW MINIMUM: " + selected)

    if maximum is not None and number > Decimal(str(maximum)):
        raise RuntimeError("UNIT 2 ABOVE MAXIMUM: " + selected)

    return float(number), selected


def unit_2_env_bool(name, default=False):
    raw = os.getenv(
        name, "true" if default else "false"
    ).strip().lower()

    if raw in ("true", "1", "yes", "on"):
        return True

    if raw in ("false", "0", "no", "off"):
        return False

    raise RuntimeError("UNIT 2 INVALID BOOLEAN " + name)


def unit_2_universal_symbol():
    symbol = os.getenv(
        "WEEX_SYMBOL",
        os.getenv("MARKET_SYMBOL", "BTCUSDT")
    ).strip().upper()

    symbol = symbol.replace("/", "").replace("-", "")

    if not re.fullmatch(r"[A-Z0-9]{2,20}USDT", symbol):
        raise RuntimeError(
            "UNIT 2 INVALID MARKET SYMBOL: " + symbol
        )

    return symbol, symbol[:-4], "USDT"


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print(
        "COMBINED RECONSTRUCTION UNIT 2 V10 START",
        flush=True
    )

    if globals().get(
        "FRESH_RECONSTRUCTION_UNIT_1_READY"
    ) is not True:
        raise RuntimeError("UNIT 2 REQUIRES UNIT 1")

    market_symbol, base_coin, quote_coin = (
        unit_2_universal_symbol()
    )

    bot_mode = os.getenv(
        "BOT_MODE", "PAUSE"
    ).strip().upper()

    if bot_mode not in ("RUN", "PAUSE"):
        raise RuntimeError("UNIT 2 INVALID BOT_MODE")

    entry_margin, entry_source = unit_2_env_number(
        (
            "INITIAL_ENTRY_MARGIN_USDT",
            "ENTRY_MARGIN_USDT",
            "ENTRY_FIXED_USDT"
        ),
        0.5,
        minimum=0.00000001
    )

    long_leverage, long_source = unit_2_env_number(
        (
            "WEEX_LEVERAGE_LONG",
            "WEEX_DEMO_LONG_LEVERAGE"
        ),
        10,
        minimum=0.00000001
    )

    short_leverage, short_source = unit_2_env_number(
        (
            "WEEX_LEVERAGE_SHORT",
            "WEEX_DEMO_SHORT_LEVERAGE"
        ),
        10,
        minimum=0.00000001
    )

    exposure_cap, _ = unit_2_env_number(
        "EXPOSURE_CAP_PERCENT",
        100,
        minimum=0,
        maximum=100
    )

    backup_margin, _ = unit_2_env_number(
        "BACKUP_MARGIN_PERCENT",
        0.5,
        minimum=0,
        maximum=100
    )

    backup_buffer, _ = unit_2_env_number(
        "BACKUP_BUFFER_PERCENT",
        0.3,
        minimum=0,
        maximum=99.999
    )

    tp1_roi, _ = unit_2_env_number(
        "TP1_NET_ROI_PERCENT",
        20,
        minimum=0.00000001
    )

    tp2_roi, _ = unit_2_env_number(
        "TP2_NET_ROI_PERCENT",
        40,
        minimum=0.00000001
    )

    if tp2_roi <= tp1_roi:
        raise RuntimeError("UNIT 2 TP2 MUST EXCEED TP1")

    tp1_allocation, _ = unit_2_env_number(
        "TP1_ALLOCATION_PERCENT",
        10,
        minimum=0,
        maximum=100
    )

    tp2_allocation, _ = unit_2_env_number(
        "TP2_ALLOCATION_PERCENT",
        20,
        minimum=0,
        maximum=100
    )

    tp3_allocation = (
        100.0 - tp1_allocation - tp2_allocation
    )

    if tp3_allocation <= 0:
        raise RuntimeError("UNIT 2 INVALID TP ALLOCATION")

    trailing_reference, _ = unit_2_env_number(
        "TP3_TRAILING_REFERENCE_PERCENT",
        0.20,
        minimum=0.01,
        maximum=100
    )

    trailing_min, _ = unit_2_env_number(
        "TP3_TRAILING_MIN_PERCENT",
        0.10,
        minimum=0.01,
        maximum=100
    )

    trailing_max, _ = unit_2_env_number(
        "TP3_TRAILING_MAX_PERCENT",
        0.40,
        minimum=0.01,
        maximum=100
    )

    if not (
        trailing_min <= trailing_reference <= trailing_max
    ):
        raise RuntimeError("UNIT 2 INVALID TRAILING RANGE")

    fee_rate, _ = unit_2_env_number(
        "WEEX_TAKER_FEE_RATE",
        0.0008,
        minimum=0,
        maximum=0.1
    )

    slippage_rate, _ = unit_2_env_number(
        "ESTIMATED_SLIPPAGE_RATE",
        0.0002,
        minimum=0,
        maximum=0.1
    )

    funding_rate, _ = unit_2_env_number(
        "ESTIMATED_FUNDING_RATE",
        0,
        minimum=0,
        maximum=0.1
    )

    demo_candidate = os.getenv(
        "WEEX_DEMO_ORDER_SYMBOL",
        base_coin + "SUSDT"
    ).strip().upper()

    if market_symbol == "BTCUSDT":
        # Preserve the proven Unit 12 mapping.
        demo_candidate = os.getenv(
            "WEEX_DEMO_ORDER_SYMBOL",
            "BTCSUSDT"
        ).strip().upper()

    # ========================================================
    # ORIGINAL 17248 EXCHANGE CONTRACT
    # ========================================================

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",

        "market_symbol": market_symbol,
        "demo_order_symbol": demo_candidate,

        "base_coin": base_coin,
        "quote_coin": quote_coin,

        "demo_symbol_candidate": demo_candidate,
        "demo_symbol_verified": False,

        "contract_precision_verified": False,
        "contract_value_verified": False,

        "margin_currency": "USDT",
        "settlement_currency": "USDT",
        "pnl_currency": "USDT",
    }

    # ========================================================
    # ORIGINAL UNIT 2 LOCAL SAFETY CONTRACT
    # THESE FLAGS DO NOT DISABLE UNIT 12 DEMO EXECUTION
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

        "real_cash_execution_enabled": False,
    }

    # ========================================================
    # ORIGINAL 17248 STRATEGY KEYS
    # PLUS CURRENT PROFIT AND HEDGE SETTINGS
    # ========================================================

    strategy = {
        "initial_fixed_usdt": entry_margin,
        "initial_margin_percent": 5.0,

        "initial_entry_margin_usdt": entry_margin,
        "entry_margin_usdt": entry_margin,
        "entry_margin_source": entry_source,

        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
        "leverage_long": long_leverage,
        "leverage_short": short_leverage,

        "leverage_source": "RENDER_MANUAL",
        "leverage_exchange_read_enabled": False,
        "leverage_exchange_write_enabled": False,

        "backup_margin_percent": backup_margin,
        "backup_buffer_percent": backup_buffer,
        "max_backups": 5,

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_trigger_reference":
            "LATEST_VERIFIED_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "backup_long_liquidation_factor":
            1.0 - backup_buffer / 100.0,

        "backup_short_liquidation_factor":
            1.0 + backup_buffer / 100.0,

        "backup_activation":
            "AFTER_FAILED_FIRST_HEDGE_RECOVERY",

        "exposure_cap_percent": exposure_cap,
        "exposure_cap_max_percent": 100.0,

        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        "tp1_allocation_percent": tp1_allocation,
        "tp2_allocation_percent": tp2_allocation,
        "tp3_allocation_percent": tp3_allocation,

        "tp_allocation": (
            tp1_allocation,
            tp2_allocation,
            tp3_allocation
        ),

        "tp1_net_roi_floor_percent": tp1_roi,
        "tp2_net_roi_floor_percent": tp2_roi,

        "tp1_net_roi_percent": tp1_roi,
        "tp2_net_roi_percent": tp2_roi,

        "tp1_tp2_min_roi_separation_percent":
            tp2_roi - tp1_roi,

        "tp3_mode": "DYNAMIC_TRAILING",

        "tp3_trailing_reference_percent":
            trailing_reference,

        "tp3_trailing_min_percent":
            trailing_min,

        "tp3_trailing_max_percent":
            trailing_max,

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,

        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,

        "capital_currency": "USDT",
        "margin_currency": "USDT",
        "profit_currency": "USDT",

        "fee_estimate_taker_rate": fee_rate,
        "estimated_slippage_rate": slippage_rate,
        "estimated_funding_rate": funding_rate,

        "hedge": {
            "enabled": True,
            "mode": "REVERSIBLE_ATR_TWO_STAGE",

            "trigger_1_atr": 1.0,
            "trigger_2_atr": 2.0,

            "stage_1_close_original_percent": 50.0,
            "stage_1_open_opposite_percent": 50.0,

            "stage_2_close_original_percent": 100.0,
            "stage_2_open_opposite_percent": 100.0,

            "recovery_enabled": True,
            "maximum_recovery_cycles": 1,
            "repeatable": False,

            "conventional_stop_loss_enabled": False,

            "position_mode_verification_required": True,
            "quantity_step_verification_required": True,
        },

        "backup_recovery": {
            "enabled": True,
            "activation":
                "AFTER_FAILED_FIRST_HEDGE_RECOVERY",

            "backup_count": 5,
            "margin_percent": backup_margin,
            "liquidation_buffer_percent": backup_buffer,

            "require_available_funds": True,
            "require_exposure_cap": True,

            "require_verified_liquidation_price": True,
        },

        "profit_protection": {
            "before_tp1":
                "ONE_ATR_HEDGE_RECOVERY_CYCLE",

            "after_tp1": "DYNAMIC_BREAK_EVEN",
            "after_tp2": "DYNAMIC_PROFIT_TRAILING",

            "protect_realized_profit": True,
            "fee_aware": True,
            "funding_aware": True,
            "slippage_aware": True,
        },
    }

    # ========================================================
    # ORIGINAL PRECISION INTERFACE
    # VALUES MUST COME FROM VERIFIED UNIT 8 CONTRACT
    # ========================================================

    market_precision = {
        "quantity_step": None,
        "minimum_quantity": None,
        "price_step": None,

        "contract_value": None,
        "contract_multiplier": None,

        "verified": False,
        "source": "PENDING_UNIT8_VERIFICATION",

        "symbol": market_symbol,
        "demo_order_symbol": demo_candidate,
    }

    # ========================================================
    # ORIGINAL 17248 QUALIFICATION STRUCTURE
    # WITH CURRENT UNIT 4-6 COMPATIBILITY
    # ========================================================

    qualification = {
        "common": {
            "mode_priority":
                ("BREAKOUT", "STRUCTURE", "SCALP"),

            "direction_votes_required": 2,
            "direction_votes_total": 3,

            "confirmations_required": 3,
            "exclusive_mode": True,

            "use_closed_candles": True,
            "protect_developing_candidates": True,
            "protect_developing_higher_modes": True,

            "arbitrate_before_scalp": True,
            "scalp_requires_higher_modes_clear": True,

            "signal_expiry_seconds": 120,
            "candidate_expiry_seconds": 120,

            "spike_count_rejection_above": 2,
            "reject_late_impulse_entry": True,

            "market_symbol": market_symbol,
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

            "fast_momentum_minutes": 5,
            "slow_momentum_minutes": 15,

            "require_momentum_confirmation": True,
            "require_direction_agreement": True,

            "require_fast_momentum": True,
            "require_slow_momentum": False,

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

            "ema_alignment_mode": "EARLY",

            "direction_votes_required": 2,

            "momentum_lookback_minutes": 15,

            "fast_momentum_minutes": 5,
            "slow_momentum_minutes": 15,

            "require_fast_momentum": True,
            "require_slow_momentum": True,

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

            "preliminary_ema_separation_percent": 0.03,
            "preliminary_move_5m_percent": 0.015,

            "fee_aware_enabled": True,

            "estimated_taker_fee_percent":
                fee_rate * 100.0,

            "estimated_slippage_percent":
                slippage_rate * 100.0,

            "include_entry_fee": True,
            "include_exit_fee": True,

            "minimum_fee_coverage_multiplier": 2.0,
            "require_positive_estimated_net": True,
            "minimum_net_roi_percent": 2.0,

            "blocked_by_developing_breakout": True,
            "blocked_by_developing_structure": True,
        },
    }

    # ========================================================
    # CENTRAL CONFIGURATION AND COMPATIBILITY ADAPTER
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",

        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
        "qualification": qualification,

        "market_symbol": market_symbol,
        "base_coin": base_coin,
        "quote_coin": quote_coin,

        "bot_mode": bot_mode,

        "initial_entry_margin_usdt": entry_margin,

        "leverage_long": long_leverage,
        "leverage_short": short_leverage,

        "exposure_cap_percent": exposure_cap,

        "tp1_net_roi_percent": tp1_roi,
        "tp2_net_roi_percent": tp2_roi,

        "universal_market_enabled": True,
        "capital_currency": "USDT",

        "real_cash_execution_enabled": False,
    }

    # ========================================================
    # VALIDATION
    # ========================================================

    if exchange["name"] != "WEEX":
        raise RuntimeError("UNIT 2 INVALID EXCHANGE")

    if exchange["api_version"] != "V3":
        raise RuntimeError("UNIT 2 INVALID API VERSION")

    if config["execution_environment"] != "DEMO":
        raise RuntimeError("UNIT 2 DEMO REQUIRED")

    if not market_symbol.endswith("USDT"):
        raise RuntimeError("UNIT 2 INVALID QUOTE")

    if entry_margin <= 0:
        raise RuntimeError("UNIT 2 INVALID ENTRY MARGIN")

    if not 0 <= exposure_cap <= 100:
        raise RuntimeError("UNIT 2 INVALID EXPOSURE CAP")

    if abs(
        tp1_allocation
        + tp2_allocation
        + tp3_allocation
        - 100.0
    ) > 0.000001:
        raise RuntimeError("UNIT 2 INVALID TP ALLOCATION")

    if strategy["max_backups"] != 5:
        raise RuntimeError("UNIT 2 BACKUP COUNT INVALID")

    if strategy["anti_duplicate_orders"] is not True:
        raise RuntimeError("UNIT 2 DUPLICATE PROTECTION INVALID")

    if config["real_cash_execution_enabled"] is not False:
        raise RuntimeError("UNIT 2 REAL CASH MUST BE DISABLED")

    # ========================================================
    # RENDER DIAGNOSTICS
    # ========================================================

    print("UNIT 2 VERSION = V10_17248_ADAPTED", flush=True)
    print("UNIT 2 MARKET SYMBOL =", market_symbol, flush=True)
    print("UNIT 2 DEMO SYMBOL CANDIDATE =", demo_candidate, flush=True)

    print("UNIT 2 BOT_MODE =", bot_mode, flush=True)
    print(
        "UNIT 2 EXISTING POSITION MANAGEMENT = INDEPENDENT",
        flush=True
    )

    print("UNIT 2 ENTRY MARGIN USDT =", entry_margin, flush=True)
    print("UNIT 2 ENTRY MARGIN SOURCE =", entry_source, flush=True)

    print("UNIT 2 LONG LEVERAGE =", long_leverage, flush=True)
    print("UNIT 2 SHORT LEVERAGE =", short_leverage, flush=True)

    print("UNIT 2 EXPOSURE CAP % =", exposure_cap, flush=True)
    print("UNIT 2 BACKUP COUNT = 5", flush=True)
    print("UNIT 2 BACKUP MARGIN % =", backup_margin, flush=True)
    print("UNIT 2 BACKUP BUFFER % =", backup_buffer, flush=True)

    print("UNIT 2 TP1 NET ROI % =", tp1_roi, flush=True)
    print("UNIT 2 TP2 NET ROI % =", tp2_roi, flush=True)

    print(
        "UNIT 2 TP ALLOCATION =",
        tp1_allocation,
        tp2_allocation,
        tp3_allocation,
        flush=True
    )

    print(
        "UNIT 2 HEDGE MODE =",
        strategy["hedge"]["mode"],
        flush=True
    )

    print(
        "UNIT 2 CONTRACT PRECISION = PENDING UNIT 8",
        flush=True
    )

    print(
        "UNIT 2 ORIGINAL 17248 CONFIG INTERFACE = RESTORED",
        flush=True
    )

    print(
        "UNIT 2 CURRENT MODEL INTERFACE = PRESERVED",
        flush=True
    )

    print("UNIT 2 EXCHANGE WRITE = NONE", flush=True)
    print("UNIT 2 REAL CASH EXECUTION = DISABLED", flush=True)

    print(
        "COMBINED RECONSTRUCTION UNIT 2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return config


# ============================================================
# ORIGINAL UNIT 2 EXECUTION AND HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)

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
        "UNIT 2 V10 OPTIMIZATION READINESS FAILED"
    )

print(
    "UNIT 2 HANDOVER READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 2 V10
# UNIT 3 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 3
# COMBINED 17248 + 18426 MODEL
# EXECUTABLE WEEX V3 LIVE MARKET PRICE
# UNIVERSAL USDT FUTURES SYMBOL
# ZERO INDENTATION
# ============================================================

import json
import math
import time
import urllib.request
import urllib.parse
import urllib.error


# ============================================================
# 3.1 MARKET RESPONSE VALIDATOR
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

    if (
        not isinstance(expected_symbol, str)
        or not expected_symbol.endswith("USDT")
    ):
        raise RuntimeError(
            "UNIT 3 INVALID EXPECTED SYMBOL"
        )

    if payload.get("symbol") != expected_symbol:
        raise RuntimeError(
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )

    raw_price = payload.get("price")

    if isinstance(raw_price, bool):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET PRICE"
        )

    try:
        price = float(raw_price)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET PRICE"
        ) from exc

    if not math.isfinite(price) or price <= 0:
        raise RuntimeError(
            "UNIT 3 NONFINITE OR NONPOSITIVE PRICE"
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
            "UNIT 3 MARKET TIMESTAMP IN FUTURE"
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
# 3.2 EXECUTABLE WEEX MARKET REQUEST
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)

    log(
        "COMBINED RECONSTRUCTION UNIT 3 START"
    )

    # --------------------------------------------------------
    # UNIT 2 HANDOVER
    # --------------------------------------------------------

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 CONFIGURATION MISSING"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 3 EXCHANGE CONFIG INVALID"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 3 SAFETY CONFIG INVALID"
        )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or config.get("execution_environment") != "DEMO"
    ):
        raise RuntimeError(
            "UNIT 3 EXCHANGE CONFIG MISMATCH"
        )

    if (
        safety.get(
            "public_market_data_read_enabled"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
        )

    # --------------------------------------------------------
    # UNIVERSAL SYMBOL FROM UNIT 2
    # --------------------------------------------------------

    market_symbol = exchange.get("market_symbol")
    base_coin = exchange.get("base_coin")
    quote_coin = exchange.get("quote_coin")

    if (
        not isinstance(market_symbol, str)
        or not market_symbol.endswith("USDT")
        or len(market_symbol) <= 4
        or base_coin != market_symbol[:-4]
        or quote_coin != "USDT"
    ):
        raise RuntimeError(
            "UNIT 3 UNIVERSAL SYMBOL INVALID"
        )

    print(
        "UNIT 3 MARKET SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 3 BASE COIN =",
        base_coin,
        flush=True
    )

    print(
        "UNIT 3 QUOTE CURRENCY = USDT",
        flush=True
    )

    # --------------------------------------------------------
    # WEEX PUBLIC MARKET API
    # --------------------------------------------------------

    base_url = exchange.get(
        "contract_base_url"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID API BASE URL"
        )

    endpoint = "/capi/v3/market/symbolPrice"
    price_type = "MARK"

    query = urllib.parse.urlencode({
        "symbol": market_symbol,
        "priceType": price_type,
    })

    url = base_url + endpoint + "?" + query

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent":
                "WEEX-Combined-Unit3",
        },
        method="GET"
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 3 HTTP METHOD INVALID"
        )

    # --------------------------------------------------------
    # ACTUAL EXCHANGE REQUEST
    # --------------------------------------------------------

    request_start = time.monotonic()

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw_body = response.read().decode(
                "utf-8"
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:
            error_body = exc.read().decode(
                "utf-8"
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

    received_time_ms = int(
        time.time() * 1000
    )

    latency_ms = round(
        (
            time.monotonic()
            - request_start
        ) * 1000,
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

    # --------------------------------------------------------
    # VERIFY LIVE PRICE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # UNIT 4-15 MARKET SNAPSHOT
    # PRESERVE ORIGINAL EIGHT-FIELD INTERFACE
    # --------------------------------------------------------

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
        field not in market_snapshot
        for field in required_fields
    ):
        raise RuntimeError(
            "UNIT 3 MARKET SNAPSHOT INCOMPLETE"
        )

    # --------------------------------------------------------
    # RENDER EXECUTION REPORT
    # --------------------------------------------------------

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True
    )

    print(
        "UNIT 3 LIVE MARK SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 3 LIVE MARK PRICE =",
        live_price,
        flush=True
    )

    print(
        "UNIT 3 PRICE CURRENCY = USDT PER",
        base_coin,
        flush=True
    )

    print(
        "UNIT 3 EXCHANGE TIMESTAMP =",
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
        "UNIT 3 MARKET FRESHNESS VERIFIED = True",
        flush=True
    )

    print(
        "UNIT 3 HANDOVER TO UNIT 4 = READY",
        flush=True
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "COMBINED RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# 3.3 INITIAL EXECUTION AND GLOBAL HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)

FRESH_UNIT_3_OPTIMIZATION_READY = True

print(
    "UNIT 3 OPTIMIZATION READY =",
    FRESH_UNIT_3_OPTIMIZATION_READY,
    flush=True
)


# ============================================================
# END COMPLETE UNIT 3
# UNIT 4 TO FOLLOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 4
# COMBINED 17248 + 18426 EXECUTABLE MODEL
# LIVE WEEX MARKET ANALYSIS
# EMA / ATR / BREAKOUT / STRUCTURE / SCALP
# ZERO INDENTATION
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error


# ============================================================
# 4.1 STRATEGY TUNING
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
        "proximity_atr": 0.5,
        "confirmation_atr": 0.1,
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
        "ema_compression_atr_max": 0.7,
        "range_atr_max": 8.0,
        "momentum_atr_max": 1.5,
        "preliminary_ema_separation_percent": 0.03,
        "preliminary_move_5m_percent": 0.015,
        "quality_threshold": 70.0,
        "minimum_fee_coverage_multiplier": 2.0,
    },
}


# ============================================================
# 4.2 NUMERIC AND INDICATOR HELPERS
# ============================================================

def unit_4_v5_number(value, name):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 4 INVALID " + name)

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID " + name
        ) from exc

    if not math.isfinite(number):
        raise RuntimeError(
            "UNIT 4 NONFINITE " + name
        )

    return number


def unit_4_v5_positive(value, name, allow_zero=True):

    number = unit_4_v5_number(value, name)

    if number < 0 or (number == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 4 INVALID RANGE " + name
        )

    return number


def unit_4_v5_integer(value, name, minimum, maximum):

    number = unit_4_v5_number(value, name)

    if (
        not number.is_integer()
        or number < minimum
        or number > maximum
    ):
        raise RuntimeError(
            "UNIT 4 INVALID INTEGER " + name
        )

    return int(number)


def unit_4_v5_ema(prices, period):

    if len(prices) < period:
        raise RuntimeError("UNIT 4 EMA HISTORY SHORT")

    value = sum(prices[:period]) / period
    alpha = 2.0 / (period + 1.0)

    for price in prices[period:]:
        value = alpha * price + (1 - alpha) * value

    return value


def unit_4_v5_same_direction(move, side):

    return (
        (side == "LONG" and move > 0)
        or (side == "SHORT" and move < 0)
    )


# ============================================================
# 4.3 WEEX CANDLE NORMALIZATION
# ============================================================

def unit_4_v5_normalize_candles(rows, market_time_ms):

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 4 INVALID KLINE RESPONSE"
        )

    candles = []

    for row in rows:

        if not isinstance(row, (list, tuple)) or len(row) < 7:
            raise RuntimeError(
                "UNIT 4 INVALID KLINE ROW"
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
                "UNIT 4 INVALID OHLC"
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
        key=lambda x: x["open_time_ms"]
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
        x for x in candles
        if x["close_time_ms"] <= market_time_ms
    ]

    if len(closed) < 201:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED CANDLES"
        )

    return candles, closed


# ============================================================
# 4.4 EXECUTABLE MARKET ANALYSIS
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)

    log("COMBINED RECONSTRUCTION UNIT 4 START")

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    exchange = config["exchange"]
    qualification = config["qualification"]

    symbol = exchange["market_symbol"]
    base_coin = exchange["base_coin"]

    if market.get("symbol") != symbol:
        raise RuntimeError(
            "UNIT 4 MARKET SYMBOL MISMATCH"
        )

    if market.get("price_type") != "MARK":
        raise RuntimeError(
            "UNIT 4 MARKET PRICE TYPE INVALID"
        )

    tuning = UNIT_4_V5_TUNING

    c = tuning["common"]
    b = tuning["breakout"]
    s = tuning["structure"]
    p = tuning["scalp"]

    market_time_ms = int(
        market["exchange_time_ms"]
    )

    live_mark = unit_4_v5_positive(
        market["price"],
        "MARK PRICE",
        False
    )

    age_ms = int(time.time() * 1000) - market_time_ms

    if not (
        -15000 <= age_ms
        <= c["market_age_seconds_max"] * 1000
    ):
        raise RuntimeError(
            "UNIT 4 STALE MARKET SNAPSHOT"
        )

    # --------------------------------------------------------
    # ACTUAL WEEX MARK PRICE CANDLES
    # --------------------------------------------------------

    base_url = exchange["contract_base_url"]

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "interval": "1m",
        "limit": 300,
    })

    request = urllib.request.Request(
        base_url + endpoint + "?" + query,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Combined-Unit4",
        }
    )

    started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:
            status = response.getcode()
            raw = response.read().decode("utf-8")

    except (
        urllib.error.HTTPError,
        urllib.error.URLError
    ) as exc:
        raise RuntimeError(
            "UNIT 4 WEEX CANDLE REQUEST FAILED"
        ) from exc

    latency_ms = round(
        (time.monotonic() - started) * 1000,
        2
    )

    if status != 200:
        raise RuntimeError(
            "UNIT 4 HTTP STATUS INVALID"
        )

    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 INVALID WEEX JSON"
        ) from exc

    candles, closed = unit_4_v5_normalize_candles(
        rows,
        market_time_ms
    )

    latest = closed[-1]
    previous = closed[-2]

    candle_age = (
        market_time_ms - latest["close_time_ms"]
    ) / 1000.0

    if not (
        0 <= candle_age
        <= c["candle_age_seconds_max"]
    ):
        raise RuntimeError(
            "UNIT 4 CLOSED CANDLE STALE"
        )

    prices = [x["close"] for x in closed]

    # --------------------------------------------------------
    # EMA INDICATORS
    # --------------------------------------------------------

    ema19 = unit_4_v5_ema(prices, 19)
    ema50 = unit_4_v5_ema(prices, 50)
    ema100 = unit_4_v5_ema(prices, 100)
    ema200 = unit_4_v5_ema(prices, 200)

    latest_close = latest["close"]
    previous_close = previous["close"]

    separation = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"
    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"
    else:
        ema_structure = "MIXED"

    # --------------------------------------------------------
    # PRICE MOMENTUM
    # --------------------------------------------------------

    moves = {}

    for period in (1, 5, 15, 30, 60, 120):

        reference = prices[-period - 1]

        moves[period] = (
            (latest_close - reference)
            / reference * 100.0
        )

    # --------------------------------------------------------
    # ATR14
    # --------------------------------------------------------

    true_ranges = []

    for i in range(1, len(closed)):

        item = closed[i]
        prior = closed[i - 1]["close"]

        true_ranges.append(max(
            item["high"] - item["low"],
            abs(item["high"] - prior),
            abs(item["low"] - prior)
        ))

    atr14 = sum(true_ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError(
            "UNIT 4 ATR14 INVALID"
        )

    atr_percent = (
        atr14 / latest_close * 100.0
    )

    # --------------------------------------------------------
    # DIRECTION VOTING
    # --------------------------------------------------------

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

    votes = (
        ema_vote,
        momentum_vote,
        price_vote
    )

    long_votes = votes.count("LONG")
    short_votes = votes.count("SHORT")

    required_votes = c["direction_votes_required"]

    direction = "NONE"

    if (
        long_votes >= required_votes
        and long_votes > short_votes
    ):
        direction = "LONG"

    elif (
        short_votes >= required_votes
        and short_votes > long_votes
    ):
        direction = "SHORT"

    def votes_ok(side, minimum):
        count = (
            long_votes if side == "LONG"
            else short_votes
        )
        return count >= minimum

    def momentum_ok(side, period, required):
        return (
            not required
            or unit_4_v5_same_direction(
                moves[int(period)],
                side
            )
        )

    # --------------------------------------------------------
    # BREAKOUT EVIDENCE
    # --------------------------------------------------------

    lookback = int(b["lookback_candles"])

    reference = closed[
        -lookback - 1:-1
    ]

    support = min(
        x["low"] for x in reference
    )

    resistance = max(
        x["high"] for x in reference
    )

    proximity = b["proximity_atr"]
    confirmation = b["confirmation_atr"]

    max_breakout_extension = (
        b["maximum_extension_atr"]
    )

    def breakout_eligible(side):

        return bool(
            b["enabled"]
            and direction == side
            and votes_ok(
                side,
                b["direction_votes_required"]
            )
            and atr_percent
                >= b["minimum_atr_percent"]
            and momentum_ok(
                side,
                b["fast_momentum_minutes"],
                b["require_fast_momentum"]
            )
            and momentum_ok(
                side,
                b["slow_momentum_minutes"],
                b["require_slow_momentum"]
            )
        )

    long_distance = (
        latest_close - resistance
    ) / atr14

    short_distance = (
        support - latest_close
    ) / atr14

    breakout_confirmed_long = bool(
        breakout_eligible("LONG")
        and confirmation < long_distance
        <= max_breakout_extension
    )

    breakout_confirmed_short = bool(
        breakout_eligible("SHORT")
        and confirmation < short_distance
        <= max_breakout_extension
    )

    breakout_developing_long = bool(
        b["developing_candidate_enabled"]
        and breakout_eligible("LONG")
        and -proximity
            <= long_distance
            <= confirmation
    )

    breakout_developing_short = bool(
        b["developing_candidate_enabled"]
        and breakout_eligible("SHORT")
        and -proximity
            <= short_distance
            <= confirmation
    )

    # --------------------------------------------------------
    # STRUCTURE EVIDENCE
    # --------------------------------------------------------

    alignment = str(
        s["ema_alignment_mode"]
    ).upper()

    if alignment not in ("EARLY", "STRICT"):
        raise RuntimeError(
            "UNIT 4 INVALID EMA ALIGNMENT"
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

    structure_max_extension = (
        s["maximum_extension_atr"]
    )

    structure_pullback = (
        s["pullback_tolerance_atr"]
    )

    def structure_eligible(side):

        signed_distance = (
            latest_close - ema19
            if side == "LONG"
            else ema19 - latest_close
        ) / atr14

        pullback = (
            abs(signed_distance)
            <= structure_pullback
        )

        continuation = bool(
            s["allow_continuation_entry"]
            and 0 <= signed_distance
            <= structure_max_extension
        )

        return bool(
            s["enabled"]
            and structure_side == side
            and direction == side
            and votes_ok(
                side,
                s["direction_votes_required"]
            )
            and separation >=
                s["minimum_ema_separation_percent"]
            and abs(signed_distance)
                <= structure_max_extension
            and (pullback or continuation)
            and momentum_ok(
                side,
                s["fast_momentum_minutes"],
                s["require_fast_momentum"]
            )
            and momentum_ok(
                side,
                s["slow_momentum_minutes"],
                s["require_slow_momentum"]
            )
        )

    structure_developing_long = (
        structure_eligible("LONG")
    )

    structure_developing_short = (
        structure_eligible("SHORT")
    )

    fast_structure_confirmed = (
        structure_side != "NONE"
        and unit_4_v5_same_direction(
            moves[int(s["fast_momentum_minutes"])],
            structure_side
        )
    )

    slow_structure_confirmed = (
        structure_side != "NONE"
        and unit_4_v5_same_direction(
            moves[int(s["slow_momentum_minutes"])],
            structure_side
        )
    )

    # --------------------------------------------------------
    # SCALP AND SIDEWAYS EVIDENCE
    # --------------------------------------------------------

    scalp_lookback = int(
        p["range_lookback_candles"]
    )

    scalp_history = closed[
        -scalp_lookback - 1:-1
    ]

    scalp_high = max(
        x["high"] for x in scalp_history
    )

    scalp_low = min(
        x["low"] for x in scalp_history
    )

    ema_cluster = (
        max(ema19, ema50, ema100, ema200)
        - min(ema19, ema50, ema100, ema200)
    )

    compression_atr = ema_cluster / atr14

    scalp_range_atr = (
        scalp_high - scalp_low
    ) / atr14

    momentum15_atr = (
        abs(latest_close - prices[-16])
        / atr14
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
        and compression_atr
            <= p["ema_compression_atr_max"]
        and scalp_range_atr
            <= p["range_atr_max"]
        and momentum15_atr
            <= p["momentum_atr_max"]
        and not higher_mode_developing
    )

    price_extension_atr = (
        abs(latest_close - ema19)
        / atr14
    )

    price_overextended = bool(
        price_extension_atr
        > structure_max_extension
    )

    # --------------------------------------------------------
    # UPDATE SHARED QUALIFICATION SETTINGS
    # --------------------------------------------------------

    qualification["common"][
        "direction_votes_required"
    ] = required_votes

    qualification["breakout"].update({
        "enabled": bool(b["enabled"]),
        "developing_candidate_enabled":
            bool(b["developing_candidate_enabled"]),
        "support_resistance_lookback": lookback,
        "developing_proximity_atr": proximity,
        "confirmation_distance_atr": confirmation,
        "max_price_extension_atr":
            max_breakout_extension,
        "minimum_atr_percent":
            b["minimum_atr_percent"],
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

    qualification["structure"].update({
        "enabled": bool(s["enabled"]),
        "ema_alignment_mode": alignment,
        "direction_votes_required":
            s["direction_votes_required"],
        "minimum_ema_separation_percent":
            s["minimum_ema_separation_percent"],
        "pullback_tolerance_atr":
            structure_pullback,
        "allow_continuation_entry":
            s["allow_continuation_entry"],
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

    qualification["scalp"].update({
        "enabled": bool(p["enabled"]),
        "require_sideways_market":
            p["require_sideways_market"],
        "ema_compression_atr_max":
            p["ema_compression_atr_max"],
        "range20_atr_max":
            p["range_atr_max"],
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

    # --------------------------------------------------------
    # UNIT 4 -> UNIT 5 EVIDENCE SNAPSHOT
    # PRESERVE ORIGINAL FIELD NAMES
    # --------------------------------------------------------

    snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": symbol,
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": live_mark,
        "previous_close": previous_close,
        "latest_close": latest_close,

        "latest_open_time_ms":
            latest["open_time_ms"],
        "latest_close_time_ms":
            latest["close_time_ms"],
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
            dict(x) for x in closed[-60:]
        ],

        "candle_count": len(candles),
        "closed_candle_count": len(closed),

        "newest_returned_candle_closed":
            candles[-1]["close_time_ms"]
            <= market_time_ms,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "atr14": atr14,
        "atr_percent": atr_percent,

        "support20": support,
        "resistance20": resistance,

        "range20_atr_ratio":
            (resistance - support) / atr14,

        "near_resistance":
            latest_close
            >= resistance - proximity * atr14,

        "near_support":
            latest_close
            <= support + proximity * atr14,

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

        "structure_trend_direction":
            structure_side,

        "structure_ema_alignment_mode":
            alignment,

        "structure_momentum_fast_confirmed":
            fast_structure_confirmed,

        "structure_momentum_slow_confirmed":
            slow_structure_confirmed,

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

        "price_extension_cluster":
            price_extension_atr,

        "price_overextended":
            price_overextended,

        "strategy_evidence_version":
            "U4_HYBRID_V2",

        "qualification_tuning_revision":
            "UNIT4_COMBINED_EXECUTABLE",

        "qualification_settings": {
            "breakout_lookback": lookback,
            "breakout_proximity_atr": proximity,
            "breakout_confirmation_atr": confirmation,
            "structure_pullback_atr":
                structure_pullback,
            "structure_max_extension_atr":
                structure_max_extension,
            "structure_ema_alignment_mode":
                alignment,
            "scalp_compression_atr":
                p["ema_compression_atr_max"],
            "scalp_range_atr":
                p["range_atr_max"],
            "scalp_momentum_atr":
                p["momentum_atr_max"],
        },

        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
    }

    # --------------------------------------------------------
    # ACTUAL EXECUTION REPORT
    # --------------------------------------------------------

    print(
        "UNIT 4 MARKET SYMBOL =", symbol,
        flush=True
    )

    print(
        "UNIT 4 HTTP STATUS =", status,
        flush=True
    )

    print(
        "UNIT 4 REQUEST LATENCY MS =",
        latency_ms,
        flush=True
    )

    print(
        "UNIT 4 CLOSED CANDLES =",
        len(closed),
        flush=True
    )

    print(
        "UNIT 4 EMA19 =", ema19,
        flush=True
    )

    print(
        "UNIT 4 EMA50 =", ema50,
        flush=True
    )

    print(
        "UNIT 4 EMA200 =", ema200,
        flush=True
    )

    print(
        "UNIT 4 ATR14 =", atr14,
        flush=True
    )

    print(
        "UNIT 4 ATR PERCENT =", atr_percent,
        flush=True
    )

    print(
        "UNIT 4 DIRECTION =", direction,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT LONG =",
        breakout_confirmed_long,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT SHORT =",
        breakout_confirmed_short,
        flush=True
    )

    print(
        "UNIT 4 STRUCTURE LONG =",
        structure_developing_long,
        flush=True
    )

    print(
        "UNIT 4 STRUCTURE SHORT =",
        structure_developing_short,
        flush=True
    )

    print(
        "UNIT 4 SIDEWAYS =",
        sideways_candidate,
        flush=True
    )

    print(
        "UNIT 4 EVIDENCE VERSION =",
        snapshot["strategy_evidence_version"],
        flush=True
    )

    print(
        "UNIT 4 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "COMBINED RECONSTRUCTION UNIT 4 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return snapshot


# ============================================================
# 4.5 EXECUTION AND GLOBAL HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END COMPLETE UNIT 4
# UNIT 5 TO FOLLOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 5
# COMBINED 17248 + 18426
# EXECUTABLE HYBRID STRATEGY CLASSIFICATION
# ZERO INDENTATION
# ============================================================

import math
import time


# ============================================================
# 5.1 HELPERS
# ============================================================

def unit_5_v8_number(value, name):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 5 INVALID " + name)

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 5 INVALID " + name
        ) from exc

    if not math.isfinite(result):
        raise RuntimeError(
            "UNIT 5 NONFINITE " + name
        )

    return result


def unit_5_v8_direction(value):

    if value > 0:
        return "LONG"

    if value < 0:
        return "SHORT"

    return "NONE"


def unit_5_v8_side_matches(value, side):

    return (
        (side == "LONG" and value > 0)
        or (side == "SHORT" and value < 0)
    )


def unit_5_v8_settings(config, group):

    section = config.get("qualification", {})
    result = section.get(group, {})

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 5 INVALID CONFIG " + group
        )

    return result


# ============================================================
# 5.2 EXECUTABLE CLASSIFIER
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot
):

    print("=" * 80, flush=True)

    log("COMBINED RECONSTRUCTION UNIT 5 START")

    config = unit_2_config
    analysis = unit_4_snapshot

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 5 CONFIG MISSING")

    if not isinstance(analysis, dict):
        raise RuntimeError("UNIT 5 ANALYSIS MISSING")

    common = unit_5_v8_settings(config, "common")
    b = unit_5_v8_settings(config, "breakout")
    s = unit_5_v8_settings(config, "structure")
    p = unit_5_v8_settings(config, "scalp")

    symbol = config["exchange"]["market_symbol"]

    if analysis.get("symbol") != symbol:
        raise RuntimeError(
            "UNIT 5 SYMBOL MISMATCH"
        )

    if analysis.get("price_type") != "MARK":
        raise RuntimeError(
            "UNIT 5 INVALID PRICE TYPE"
        )

    # --------------------------------------------------------
    # MARKET INDICATORS
    # --------------------------------------------------------

    def n(key):
        return unit_5_v8_number(
            analysis.get(key), key
        )

    live_price = n("live_mark_price")
    previous_close = n("previous_close")
    latest_close = n("latest_close")

    ema19 = n("ema19")
    ema50 = n("ema50")
    ema200 = n("ema200")

    atr14 = n("atr14")

    if atr14 <= 0 or live_price <= 0:
        raise RuntimeError(
            "UNIT 5 INVALID MARKET INDICATORS"
        )

    separation = n("ema19_50_separation_pct")
    short_move = n("short_term_move_pct")

    moves = {
        period: n("move_" + str(period) + "m_pct")
        for period in (1, 5, 15, 30, 60, 120)
    }

    directions = {
        period: unit_5_v8_direction(moves[period])
        for period in moves
    }

    ema_direction = (
        "LONG" if ema19 > ema50
        else "SHORT" if ema19 < ema50
        else "NONE"
    )

    momentum_direction = unit_5_v8_direction(
        moves[5] + moves[15]
    )

    ema_structure = analysis.get(
        "ema_structure", "MIXED"
    )

    # --------------------------------------------------------
    # MARKET FRESHNESS
    # --------------------------------------------------------

    candle_time = int(
        analysis["latest_close_time_ms"]
    )

    candle_age = (
        time.time() * 1000 - candle_time
    ) / 1000.0

    if candle_age < -15 or candle_age > 120:
        raise RuntimeError(
            "UNIT 5 MARKET CANDLE STALE"
        )

    # --------------------------------------------------------
    # DIRECTION VOTES
    # --------------------------------------------------------

    long_votes = int(
        analysis.get("direction_long_votes", 0)
    )

    short_votes = int(
        analysis.get("direction_short_votes", 0)
    )

    required_votes = int(
        common.get("direction_votes_required", 2)
    )

    direction_evidence = analysis.get(
        "direction_evidence", "NONE"
    )

    def votes_pass(side, minimum=None):

        threshold = (
            required_votes
            if minimum is None
            else int(minimum)
        )

        count = (
            long_votes if side == "LONG"
            else short_votes
        )

        return count >= threshold

    # --------------------------------------------------------
    # BREAKOUT QUALIFICATION
    # --------------------------------------------------------

    breakout_long = bool(
        analysis.get("breakout_confirmed_long")
    )

    breakout_short = bool(
        analysis.get("breakout_confirmed_short")
    )

    breakout_developing_long = bool(
        analysis.get("breakout_developing_long")
    )

    breakout_developing_short = bool(
        analysis.get("breakout_developing_short")
    )

    breakout_side = (
        "LONG" if breakout_long
        else "SHORT" if breakout_short
        else "NONE"
    )

    breakout_votes_ok = (
        breakout_side != "NONE"
        and votes_pass(
            breakout_side,
            b.get("direction_votes_required", 2)
        )
    )

    breakout_momentum_ok = bool(
        breakout_side != "NONE"
        and (
            not b.get("require_fast_momentum", True)
            or unit_5_v8_side_matches(
                moves[5], breakout_side
            )
        )
        and (
            not b.get("require_slow_momentum", False)
            or unit_5_v8_side_matches(
                moves[15], breakout_side
            )
        )
    )

    breakout_qualified = bool(
        b.get("enabled", True)
        and breakout_side != "NONE"
        and breakout_votes_ok
        and breakout_momentum_ok
    )

    breakout_developing = bool(
        breakout_developing_long
        or breakout_developing_short
    )

    developing_breakout_direction = (
        "LONG" if breakout_developing_long
        else "SHORT" if breakout_developing_short
        else "NONE"
    )

    # --------------------------------------------------------
    # STRUCTURE QUALIFICATION
    # --------------------------------------------------------

    structure_long = bool(
        analysis.get("structure_developing_long")
    )

    structure_short = bool(
        analysis.get("structure_developing_short")
    )

    structure_side = (
        "LONG" if structure_long
        else "SHORT" if structure_short
        else "NONE"
    )

    structure_trend = analysis.get(
        "structure_trend_direction", "NONE"
    )

    structure_ema_mode = str(
        s.get("ema_alignment_mode", "EARLY")
    ).upper()

    extension_atr = (
        abs(latest_close - ema19) / atr14
    )

    structure_extension_ok = (
        extension_atr
        <= float(s.get("max_price_extension_atr", 2))
    )

    structure_votes_ok = bool(
        structure_side != "NONE"
        and votes_pass(
            structure_side,
            s.get("direction_votes_required", 2)
        )
    )

    structure_momentum_ok = bool(
        structure_side != "NONE"
        and (
            not s.get("require_fast_momentum", True)
            or unit_5_v8_side_matches(
                moves[5], structure_side
            )
        )
        and (
            not s.get("require_slow_momentum", True)
            or unit_5_v8_side_matches(
                moves[15], structure_side
            )
        )
    )

    structure_qualified = bool(
        s.get("enabled", True)
        and structure_side != "NONE"
        and structure_side == structure_trend
        and structure_votes_ok
        and structure_momentum_ok
        and structure_extension_ok
    )

    structure_developing = bool(
        structure_long or structure_short
    )

    developing_structure_direction = (
        structure_side
        if structure_developing
        else "NONE"
    )

    # --------------------------------------------------------
    # SCALP QUALIFICATION
    # --------------------------------------------------------

    sideways_evidence = bool(
        analysis.get("sideways_candidate", False)
    )

    scalp_require_sideways = bool(
        p.get("require_sideways_market", True)
    )

    scalp_sideways_ok = (
        sideways_evidence
        or not scalp_require_sideways
    )

    scalp_ema_min = float(
        p.get(
            "preliminary_ema_separation_percent",
            0.03
        )
    )

    scalp_move_min = float(
        p.get(
            "preliminary_move_5m_percent",
            0.015
        )
    )

    scalp_direction_candidate = (
        direction_evidence
        if direction_evidence in ("LONG", "SHORT")
        else momentum_direction
    )

    scalp_direction = scalp_direction_candidate

    scalp_move = moves[1]

    scalp_1m_support = (
        unit_5_v8_side_matches(
            scalp_move,
            scalp_direction
        )
    )

    scalp_preliminary = bool(
        p.get("enabled", True)
        and scalp_sideways_ok
        and scalp_direction in ("LONG", "SHORT")
        and votes_pass(scalp_direction)
        and (
            abs(separation) >= scalp_ema_min
            or abs(moves[5]) >= scalp_move_min
        )
    )

    # --------------------------------------------------------
    # HIGHER MODE PROTECTION
    # --------------------------------------------------------

    higher_mode_developing = bool(
        breakout_qualified
        or breakout_developing
        or structure_qualified
        or structure_developing
    )

    scalp_ready = bool(
        scalp_preliminary
        and not higher_mode_developing
    )

    breakout_ready = breakout_qualified
    structure_ready = structure_qualified

    # --------------------------------------------------------
    # EXCLUSIVE PRIORITY
    # --------------------------------------------------------

    candidate_mode = "NONE"
    candidate_stage = "REJECTED"

    active_mode = "NONE"
    direction = "NONE"
    qualified = False

    reason = "NO_QUALIFIED_MARKET_MODE"

    if breakout_ready:

        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"

        active_mode = "BREAKOUT"
        direction = breakout_side

        qualified = True
        reason = "BREAKOUT_CONFIRMED"

    elif breakout_developing:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"

        direction = developing_breakout_direction
        reason = "BREAKOUT_DEVELOPING"

    elif structure_ready:

        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"

        active_mode = "STRUCTURE"
        direction = structure_side

        qualified = True
        reason = "STRUCTURE_CONFIRMED"

    elif structure_developing:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"

        direction = developing_structure_direction
        reason = "STRUCTURE_DEVELOPING"

    elif scalp_ready:

        candidate_mode = "SCALP"
        candidate_stage = "PRELIMINARY"

        active_mode = "SCALP"
        direction = scalp_direction

        qualified = True
        reason = "SCALP_PENDING_UNIT6_QUALITY"

    elif not scalp_sideways_ok:

        reason = "SCALP_NOT_SIDEWAYS_MARKET"

    # --------------------------------------------------------
    # FEE ESTIMATION
    # --------------------------------------------------------

    strategy = config.get("strategy", {})

    taker_fee = float(
        strategy.get(
            "fee_estimate_taker_rate",
            0.0008
        )
    )

    slippage = float(
        strategy.get(
            "estimated_slippage_rate",
            0.0002
        )
    )

    round_trip_fee = (
        2.0 * (taker_fee + slippage) * 100.0
    )

    fee_multiplier = float(
        p.get(
            "minimum_fee_coverage_multiplier",
            2.0
        )
    )

    # --------------------------------------------------------
    # REJECTION REASONS
    # --------------------------------------------------------

    breakout_rejection_reason = (
        "QUALIFIED"
        if breakout_qualified
        else "CONFIRMATION_OR_MOMENTUM_PENDING"
    )

    structure_rejection_reason = (
        "QUALIFIED"
        if structure_qualified
        else "STRUCTURE_EVIDENCE_PENDING"
    )

    scalp_rejection_reason = (
        "QUALIFIED"
        if scalp_ready
        else "HIGHER_MODE_PROTECTED"
        if higher_mode_developing
        else "NOT_SIDEWAYS"
        if not scalp_sideways_ok
        else "QUALITY_OR_DIRECTION_PENDING"
    )

    # --------------------------------------------------------
    # UNIT 6 HANDOVER
    # --------------------------------------------------------

    candidate = {
        "symbol": symbol,
        "base_coin": symbol[:-4],
        "quote_coin": "USDT",
        "margin_currency": "USDT",

        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": reason,

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "live_mark_price": live_price,
        "previous_close": previous_close,
        "latest_close": latest_close,

        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,

        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,
        "ema_direction": ema_direction,
        "momentum_direction": momentum_direction,

        "direction_agreement": (
            ema_direction == momentum_direction
            and ema_direction != "NONE"
        ),

        "short_term_move_pct": short_move,
        "absolute_short_term_move_pct":
            abs(short_move),

        "price_above_ema19": latest_close > ema19,
        "price_above_ema50": latest_close > ema50,
        "price_above_ema200": latest_close > ema200,

        "latest_close_above_previous":
            latest_close > previous_close,

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
        "scalp_1m_support": scalp_1m_support,

        "structure_direction": structure_side,
        "structure_move_pct": moves[15],

        "breakout_direction": breakout_side,
        "breakout_move_pct": moves[5],

        "breakout_fast_support":
            breakout_momentum_ok,

        "higher_mode_developing":
            higher_mode_developing,

        "breakout_candidate": bool(
            breakout_qualified
            or breakout_developing
        ),

        "structure_candidate": bool(
            structure_qualified
            or structure_developing
        ),

        "breakout_ready": breakout_ready,
        "structure_ready": structure_ready,
        "scalp_ready": scalp_ready,

        "sideways_context": sideways_evidence,
        "direction_evidence": direction_evidence,

        "scalp_quality_minimum": float(
            p.get("quality_threshold", 70)
        ),

        "scalp_price_weight_percent": 50.0,

        "estimated_round_trip_fee_pct":
            round_trip_fee,

        "scalp_minimum_fee_coverage":
            fee_multiplier,

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

        "classification_revision":
            "COMBINED_EXECUTABLE",

        "candidate_protected":
            candidate_stage == "DEVELOPING",

        "candidate_age_seconds": candle_age,

        "classification_source":
            "UNIT5_COMBINED_EXECUTABLE",

        "original_unit5_qualified": qualified,
        "original_unit5_mode": active_mode,
        "original_unit5_direction": direction,
        "original_unit5_reason": reason,
        "original_hybrid_conflict": False,

        "optimization_version": "UNIT5_V8",

        "hybrid_structure_qualified":
            structure_qualified,

        "hybrid_breakout_qualified":
            breakout_qualified,

        "structure_direction_votes": (
            long_votes if structure_side == "LONG"
            else short_votes
            if structure_side == "SHORT"
            else 0
        ),

        "structure_extension_atr": extension_atr,
        "structure_extension_pass":
            structure_extension_ok,

        "structure_momentum_agreement":
            structure_momentum_ok,

        "breakout_confirmation_votes": (
            long_votes if breakout_side == "LONG"
            else short_votes
            if breakout_side == "SHORT"
            else 0
        ),

        "developing_breakout_direction":
            developing_breakout_direction,

        "developing_structure_direction":
            developing_structure_direction,

        "scalp_preliminary": scalp_preliminary,

        "qualification_tuning_revision":
            "UNIT5_V8_FULLY_ADJUSTABLE",

        "structure_ema_alignment_mode":
            structure_ema_mode,

        "structure_trend_direction":
            structure_trend,

        "structure_votes_pass":
            structure_votes_ok,

        "structure_momentum_pass":
            structure_momentum_ok,

        "breakout_votes_pass":
            breakout_votes_ok,

        "breakout_momentum_pass":
            breakout_momentum_ok,

        "scalp_preliminary_ema_min_pct":
            scalp_ema_min,

        "scalp_preliminary_move_min_pct":
            scalp_move_min,

        "scalp_sideways_required":
            scalp_require_sideways,

        "scalp_sideways_pass":
            scalp_sideways_ok,

        "scalp_direction_candidate":
            scalp_direction_candidate,

        "scalp_quality_pending_unit6":
            scalp_ready,

        "universal_symbol_enabled": True,
        "unit5_revision":
            "UNIT5_COMBINED_EXECUTABLE",

        "breakout_rejection_reason":
            breakout_rejection_reason,

        "structure_rejection_reason":
            structure_rejection_reason,

        "scalp_rejection_reason":
            scalp_rejection_reason,
    }

    # --------------------------------------------------------
    # EXECUTION REPORT
    # --------------------------------------------------------

    print(
        "UNIT 5 SYMBOL =", symbol,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT QUALIFIED =",
        breakout_qualified,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE QUALIFIED =",
        structure_qualified,
        flush=True
    )

    print(
        "UNIT 5 SCALP PRELIMINARY =",
        scalp_preliminary,
        flush=True
    )

    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
        flush=True
    )

    print(
        "UNIT 5 MODE =", candidate_mode,
        flush=True
    )

    print(
        "UNIT 5 STAGE =", candidate_stage,
        flush=True
    )

    print(
        "UNIT 5 DIRECTION =", direction,
        flush=True
    )

    print(
        "UNIT 5 QUALIFIED =", qualified,
        flush=True
    )

    print(
        "UNIT 5 REASON =", reason,
        flush=True
    )

    print(
        "UNIT 5 ESTIMATED ROUND TRIP COST % =",
        round_trip_fee,
        flush=True
    )

    print(
        "UNIT 5 HANDOVER TO UNIT 6 = READY",
        flush=True
    )

    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "COMBINED RECONSTRUCTION UNIT 5 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return candidate


# ============================================================
# 5.3 GLOBAL EXECUTION AND HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT_5_RESULT = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
)

FRESH_UNIT_5_OPTIMIZATION_READY = True


# ============================================================
# END COMPLETE UNIT 5
# UNIT 6 TO FOLLOW
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE UNIT 6
# COMBINED 17248 + 18426
# EXECUTABLE SIGNAL QUALITY AND ADMISSION
# ZERO INDENTATION
# ============================================================

import math
import time


# ============================================================
# 6.1 NUMERIC HELPERS
# ============================================================

def unit_6_number(value, default=0.0):

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return float(default)

    if not math.isfinite(result):
        return float(default)

    return result


def unit_6_clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))


def unit_6_direction(value):

    if value > 0:
        return "LONG"

    if value < 0:
        return "SHORT"

    return "NONE"


def unit_6_matches(value, direction):

    return (
        (direction == "LONG" and value > 0)
        or (direction == "SHORT" and value < 0)
    )


# ============================================================
# 6.2 PERSISTENCE STATE
# ============================================================

UNIT_6_SIGNAL_HISTORY = {
    "symbol": None,
    "last_candle_id": None,
    "observations": [],
}


def unit_6_update_persistence(
    symbol,
    candle_id,
    direction,
    maximum=3
):

    state = UNIT_6_SIGNAL_HISTORY

    if state["symbol"] != symbol:

        state["symbol"] = symbol
        state["last_candle_id"] = None
        state["observations"] = []

    if state["last_candle_id"] != candle_id:

        state["last_candle_id"] = candle_id

        state["observations"].append(direction)

        state["observations"] = (
            state["observations"][-maximum:]
        )

    return list(state["observations"])


# ============================================================
# 6.3 EXECUTABLE SIGNAL ENGINE
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate
):

    print("=" * 80, flush=True)

    log("COMBINED RECONSTRUCTION UNIT 6 START")

    config = unit_2_config
    analysis = unit_4_analysis
    candidate = unit_5_candidate

    if not all(
        isinstance(item, dict)
        for item in (config, analysis, candidate)
    ):
        raise RuntimeError(
            "UNIT 6 INPUT DATA MISSING"
        )

    exchange = config["exchange"]
    symbol = exchange["market_symbol"]

    if (
        analysis.get("symbol") != symbol
        or candidate.get("symbol") != symbol
    ):
        raise RuntimeError(
            "UNIT 6 SYMBOL HANDOVER MISMATCH"
        )

    qualification = config.get(
        "qualification", {}
    )

    strategy = config.get("strategy", {})

    scalp_settings = qualification.get(
        "scalp", {}
    )

    # --------------------------------------------------------
    # MARKET EVIDENCE
    # --------------------------------------------------------

    price = unit_6_number(
        analysis.get("latest_close")
    )

    ema19 = unit_6_number(
        analysis.get("ema19")
    )

    ema50 = unit_6_number(
        analysis.get("ema50")
    )

    ema100 = unit_6_number(
        analysis.get("ema100")
    )

    ema200 = unit_6_number(
        analysis.get("ema200")
    )

    atr = unit_6_number(
        analysis.get("atr14")
    )

    if min(
        price, ema19, ema50, ema100, ema200, atr
    ) <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID MARKET INDICATORS"
        )

    move_1m = unit_6_number(
        analysis.get("move_1m_pct")
    )

    move_5m = unit_6_number(
        analysis.get("move_5m_pct")
    )

    move_15m = unit_6_number(
        analysis.get("move_15m_pct")
    )

    atr_pct = unit_6_number(
        analysis.get("atr_percent")
    )

    # --------------------------------------------------------
    # MARKET FRESHNESS
    # --------------------------------------------------------

    candle_id = int(
        analysis.get("latest_close_time_ms", 0)
    )

    candle_age_seconds = (
        time.time() * 1000 - candle_id
    ) / 1000.0

    fresh = bool(
        candle_id > 0
        and -15 <= candle_age_seconds <= 120
        and candidate.get(
            "candle_data_fresh", False
        ) is True
    )

    # --------------------------------------------------------
    # UNIT 5 CANDIDATE
    # --------------------------------------------------------

    mode = str(
        candidate.get("candidate_mode", "NONE")
    ).upper()

    stage = str(
        candidate.get("candidate_stage", "REJECTED")
    ).upper()

    incoming_side = str(
        candidate.get("direction", "NONE")
    ).upper()

    upstream_qualified = bool(
        candidate.get("qualified", False)
    )

    breakout_ready = bool(
        candidate.get("breakout_ready", False)
    )

    structure_ready = bool(
        candidate.get("structure_ready", False)
    )

    scalp_ready = bool(
        candidate.get("scalp_ready", False)
    )

    higher_developing = bool(
        candidate.get(
            "higher_mode_developing", False
        )
    )

    sideways = bool(
        analysis.get("sideways_candidate", False)
    )

    # --------------------------------------------------------
    # SCALP DIRECTION
    # --------------------------------------------------------

    scalp_side = str(
        candidate.get(
            "scalp_direction",
            incoming_side
        )
    ).upper()

    if scalp_side not in ("LONG", "SHORT"):
        scalp_side = unit_6_direction(
            move_5m + move_1m
        )

    # --------------------------------------------------------
    # SIGNAL PERSISTENCE
    # --------------------------------------------------------

    observed_direction = (
        incoming_side
        if mode in ("BREAKOUT", "STRUCTURE")
        and incoming_side in ("LONG", "SHORT")
        else scalp_side
        if mode == "SCALP"
        else "NONE"
    )

    persistence_directions = (
        unit_6_update_persistence(
            symbol,
            candle_id,
            observed_direction
        )
    )

    persistence_required = 2

    persistence_window = len(
        persistence_directions
    )

    persistence_confirmations = sum(
        item == observed_direction
        for item in persistence_directions
    )

    persistence_pass = bool(
        observed_direction in ("LONG", "SHORT")
        and persistence_confirmations
        >= persistence_required
    )

    # --------------------------------------------------------
    # MOMENTUM AND EMA QUALITY
    # --------------------------------------------------------

    momentum_conflict = bool(
        scalp_side in ("LONG", "SHORT")
        and move_5m != 0
        and move_15m != 0
        and unit_6_direction(move_5m)
            != unit_6_direction(move_15m)
    )

    fifteen_minute_support_pass = (
        unit_6_matches(
            move_15m,
            scalp_side
        )
    )

    compression_atr = unit_6_number(
        analysis.get("ema_compression_atr"),
        999.0
    )

    compression_limit = unit_6_number(
        scalp_settings.get(
            "ema_compression_atr_max", 0.7
        ),
        0.7
    )

    ema_compressed = (
        compression_atr <= compression_limit
    )

    extension_atr = (
        abs(price - ema19) / atr
    )

    extreme_extension = extension_atr > 3.0

    extreme_spike = (
        abs(move_1m) > atr_pct * 3.0
    )

    late_impulse = (
        abs(move_5m) > atr_pct * 5.0
    )

    # --------------------------------------------------------
    # SCALP QUALITY SCORING
    # --------------------------------------------------------

    price_action_score = 0.0
    persistence_score = 0.0
    location_score = 0.0
    ema_score = 0.0
    volatility_score = 0.0

    if scalp_side in ("LONG", "SHORT"):

        if unit_6_matches(
            move_1m, scalp_side
        ):
            price_action_score += 15

        if unit_6_matches(
            move_5m, scalp_side
        ):
            price_action_score += 15

        if fifteen_minute_support_pass:
            price_action_score += 10

        if not momentum_conflict:
            price_action_score += 5

        if persistence_window > 0:

            persistence_score = (
                15.0
                * persistence_confirmations
                / persistence_window
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
        unit_6_clamp(
            price_action_score
            + persistence_score
            + location_score
            + ema_score
            + volatility_score,
            0.0,
            100.0
        ),
        2
    )

    scalp_minimum = unit_6_number(
        scalp_settings.get(
            "quality_threshold", 70.0
        ),
        70.0
    )

    quality_pass = (
        quality_score >= scalp_minimum
    )

    # --------------------------------------------------------
    # FEE COVERAGE
    # --------------------------------------------------------

    estimated_fee = unit_6_number(
        candidate.get(
            "estimated_round_trip_fee_pct",
            0.0
        )
    )

    fee_coverage_multiplier = unit_6_number(
        scalp_settings.get(
            "minimum_fee_coverage_multiplier",
            2.0
        ),
        2.0
    )

    projected_move_pct = min(
        abs(move_5m),
        max(atr_pct, 0.0)
    )

    required_move_pct = (
        estimated_fee * fee_coverage_multiplier
    )

    fee_estimate_verified = bool(
        estimated_fee > 0
        and math.isfinite(estimated_fee)
    )

    fee_coverage_pass = bool(
        fee_estimate_verified
        and projected_move_pct >= required_move_pct
    )

    # --------------------------------------------------------
    # EXCLUSIVE STRATEGY ARBITRATION
    # --------------------------------------------------------

    active_mode = "NONE"
    direction = "NONE"

    signal_qualified = False
    execution_intent = False

    admission_reason = (
        "NO_QUALIFIED_CANDIDATE"
    )

    if not fresh:

        admission_reason = (
            "MARKET_EVIDENCE_STALE"
        )

    elif (
        mode == "BREAKOUT"
        and stage == "QUALIFIED"
        and upstream_qualified
        and breakout_ready
        and incoming_side in ("LONG", "SHORT")
    ):

        active_mode = "BREAKOUT"
        direction = incoming_side

        signal_qualified = True
        execution_intent = True

        admission_reason = (
            "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS"
        )

    elif (
        mode == "STRUCTURE"
        and stage == "QUALIFIED"
        and upstream_qualified
        and structure_ready
        and incoming_side in ("LONG", "SHORT")
    ):

        active_mode = "STRUCTURE"
        direction = incoming_side

        signal_qualified = True
        execution_intent = True

        admission_reason = (
            "STRUCTURE_QUALIFIED_FOR_NEXT_UNITS"
        )

    elif (
        mode == "SCALP"
        and stage in (
            "PRELIMINARY",
            "PENDING_UNIT_6",
            "QUALIFIED"
        )
        and scalp_ready
        and not higher_developing
    ):

        sideways_required = bool(
            scalp_settings.get(
                "require_sideways_market", True
            )
        )

        sideways_pass = (
            sideways or not sideways_required
        )

        if scalp_side == "NONE":

            admission_reason = (
                "SCALP_DIRECTION_MISSING"
            )

        elif not sideways_pass:

            admission_reason = (
                "SCALP_NOT_SIDEWAYS"
            )

        elif momentum_conflict:

            admission_reason = (
                "SCALP_MOMENTUM_CONFLICT"
            )

        elif not persistence_pass:

            admission_reason = (
                "SCALP_PERSISTENCE_PENDING"
            )

        elif not quality_pass:

            admission_reason = (
                "SCALP_QUALITY_PENDING"
            )

        elif not fee_coverage_pass:

            admission_reason = (
                "SCALP_FEE_COVERAGE_INSUFFICIENT"
            )

        else:

            active_mode = "SCALP"
            direction = scalp_side

            signal_qualified = True
            execution_intent = True

            admission_reason = (
                "SCALP_QUALIFIED_FOR_NEXT_UNITS"
            )

    elif stage == "DEVELOPING":

        admission_reason = (
            "HIGHER_MODE_DEVELOPING"
        )

    elif stage == "REJECTED":

        admission_reason = candidate.get(
            "qualification_reason",
            "UPSTREAM_REJECTED"
        )

    # --------------------------------------------------------
    # UNIT 7 EXECUTION CANDIDATE
    # --------------------------------------------------------

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

        "estimated_move_pct":
            projected_move_pct,

        "estimated_round_trip_fee_pct":
            estimated_fee,

        "required_move_pct":
            required_move_pct,

        "fee_coverage_pass":
            fee_coverage_pass,

        "fee_estimate_verified":
            fee_estimate_verified,
    }

    execution_candidate = {
        "symbol": symbol,
        "base_coin": symbol[:-4],
        "quote_coin": "USDT",
        "margin_currency": "USDT",

        "execution_intent":
            execution_intent,

        "signal_qualified":
            signal_qualified,

        "active_mode":
            active_mode,

        "direction":
            direction,

        "admission_reason":
            admission_reason,

        "unit_5_reason":
            candidate.get(
                "qualification_reason", "UNKNOWN"
            ),

        "candidate_mode":
            mode,

        "candidate_stage":
            stage,

        "higher_mode_developing":
            higher_developing,

        "breakout_ready":
            breakout_ready,

        "structure_ready":
            structure_ready,

        "scalp_ready":
            scalp_ready,

        "sideways_regime":
            sideways,

        "ema_compressed":
            ema_compressed,

        "compression_threshold_pct":
            compression_limit,

        "momentum_conflict":
            momentum_conflict,

        "persistence_window":
            persistence_window,

        "persistence_required":
            persistence_required,

        "persistence_confirmations":
            persistence_confirmations,

        "persistence_directions":
            persistence_directions,

        "persistence_pass":
            persistence_pass,

        "fifteen_minute_support_pass":
            fifteen_minute_support_pass,

        "scalp_quality_score":
            quality_score,

        "scalp_quality_minimum":
            scalp_minimum,

        "scalp_quality_pass":
            quality_pass,

        "scalp_quality_details":
            quality_details,

        "estimated_move_pct":
            projected_move_pct,

        "estimated_round_trip_fee_pct":
            estimated_fee,

        "required_move_pct":
            required_move_pct,

        "fee_estimate_verified":
            fee_estimate_verified,

        "fee_coverage_pass":
            fee_coverage_pass,

        "market_data_fresh":
            fresh,

        "unit_5_evidence_version":
            candidate.get(
                "strategy_evidence_version"
            ),

        "unit_4_evidence_version":
            analysis.get(
                "strategy_evidence_version"
            ),

        "classification_version":
            "UNIT6_COMBINED_EXECUTABLE",

        "leverage_target":
            None,

        "leverage_regime":
            "WEEX_MANUAL_RENDER_CONFIG",

        "position_sizing_performed":
            False,

        "order_payload_created":
            False,

        "exchange_write":
            False,

        "read_only":
            True,

        "trade_authorized":
            False,

        "universal_symbol_enabled":
            True,
    }

    # --------------------------------------------------------
    # RENDER EXECUTION REPORT
    # --------------------------------------------------------

    print(
        "UNIT 6 MARKET SYMBOL =",
        symbol,
        flush=True
    )

    print(
        "UNIT 6 CANDIDATE MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 6 CANDIDATE STAGE =",
        stage,
        flush=True
    )

    print(
        "UNIT 6 ACTIVE MODE =",
        active_mode,
        flush=True
    )

    print(
        "UNIT 6 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 6 SCALP QUALITY SCORE =",
        quality_score,
        flush=True
    )

    print(
        "UNIT 6 SCALP QUALITY MINIMUM =",
        scalp_minimum,
        flush=True
    )

    print(
        "UNIT 6 PERSISTENCE =",
        persistence_confirmations,
        "/",
        persistence_required,
        flush=True
    )

    print(
        "UNIT 6 ESTIMATED MOVE % =",
        projected_move_pct,
        flush=True
    )

    print(
        "UNIT 6 ESTIMATED FEE % =",
        estimated_fee,
        flush=True
    )

    print(
        "UNIT 6 REQUIRED COVERAGE % =",
        required_move_pct,
        flush=True
    )

    print(
        "UNIT 6 FEE COVERAGE PASS =",
        fee_coverage_pass,
        flush=True
    )

    print(
        "UNIT 6 SIGNAL QUALIFIED =",
        signal_qualified,
        flush=True
    )

    print(
        "UNIT 6 EXECUTION INTENT =",
        execution_intent,
        flush=True
    )

    print(
        "UNIT 6 ADMISSION REASON =",
        admission_reason,
        flush=True
    )

    print(
        "UNIT 6 HANDOVER TO UNIT 7 = READY",
        flush=True
    )

    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "COMBINED RECONSTRUCTION UNIT 6 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return execution_candidate


# ============================================================
# 6.4 GLOBAL EXECUTION AND HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT_6_RESULT = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_UNIT_5_RESULT
    )
)


# ============================================================
# END COMPLETE UNIT 6
# UNIT 7 TO FOLLOW
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE CORRECTED UNIT 7
# 17248 + 18426 FORWARD-ONLY EXECUTION HANDOVER
# ZERO INDENTATION
# ============================================================

from decimal import Decimal, InvalidOperation


def unit_7_decimal(value, name, allow_zero=False):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("UNIT 7 INVALID " + name)

    if not number.is_finite():
        raise ValueError("UNIT 7 NONFINITE " + name)

    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError("UNIT 7 INVALID " + name)

    return number


def unit_7_text(value):
    return format(value, "f")


def fresh_reconstruction_unit_7(
    config,
    market,
    analysis,
    signal
):
    print("=" * 80, flush=True)
    log("COMBINED RECONSTRUCTION UNIT 7 START")

    if not all(
        isinstance(item, dict)
        for item in (config, market, analysis, signal)
    ):
        raise RuntimeError("UNIT 7 INPUT DATA MISSING")

    exchange = config["exchange"]
    strategy = config["strategy"]

    symbol = exchange["market_symbol"]

    if any(
        item.get("symbol") != symbol
        for item in (market, analysis, signal)
    ):
        raise RuntimeError("UNIT 7 SYMBOL MISMATCH")

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled") is not False
    ):
        raise RuntimeError("UNIT 7 DEMO ONLY")

    mode = str(
        signal.get("active_mode", "NONE")
    ).upper()

    direction = str(
        signal.get("direction", "NONE")
    ).upper()

    qualified = (
        signal.get("signal_qualified") is True
        and signal.get("execution_intent") is True
        and mode in ("SCALP", "STRUCTURE", "BREAKOUT")
        and direction in ("LONG", "SHORT")
    )

    bot_mode = str(
        config.get("bot_mode", "PAUSE")
    ).upper()

    margin = unit_7_decimal(
        config.get(
            "initial_entry_margin_usdt",
            strategy.get("initial_entry_margin_usdt", 0.5)
        ),
        "ENTRY_MARGIN_USDT"
    )

    long_leverage = unit_7_decimal(
        config.get(
            "leverage_long",
            strategy.get("long_leverage", 10)
        ),
        "LONG_LEVERAGE"
    )

    short_leverage = unit_7_decimal(
        config.get(
            "leverage_short",
            strategy.get("short_leverage", 10)
        ),
        "SHORT_LEVERAGE"
    )

    exposure_cap = unit_7_decimal(
        config.get(
            "exposure_cap_percent",
            strategy.get("exposure_cap_percent", 100)
        ),
        "EXPOSURE_CAP",
        True
    )

    price = unit_7_decimal(
        market.get("price"),
        "MARK_PRICE"
    )

    atr = unit_7_decimal(
        analysis.get("atr14"),
        "ATR14"
    )

    hedge_settings = strategy.get("hedge", {})
    backup_settings = strategy.get("backup_recovery", {})

    first_atr = unit_7_decimal(
        hedge_settings.get("trigger_1_atr", 1),
        "FIRST_ATR"
    )

    second_atr = unit_7_decimal(
        hedge_settings.get("trigger_2_atr", 2),
        "SECOND_ATR"
    )

    if second_atr <= first_atr:
        raise ValueError("UNIT 7 ATR STAGE ORDER INVALID")

    backup_count = int(
        backup_settings.get("backup_count", 5)
    )

    backup_margin = unit_7_decimal(
        backup_settings.get("margin_percent", 0.5),
        "BACKUP_MARGIN_PERCENT",
        True
    )

    backup_buffer = unit_7_decimal(
        backup_settings.get(
            "liquidation_buffer_percent", 0.3
        ),
        "BACKUP_BUFFER_PERCENT",
        True
    )

    leverage = (
        long_leverage
        if direction == "LONG"
        else short_leverage
        if direction == "SHORT"
        else None
    )

    requested_notional = (
        margin * leverage
        if leverage is not None
        else None
    )

    # These levels are indicative only.
    # Existing positions use their actual fill prices
    # and reconciled ATR values in management units.

    indicative_stage1 = None
    indicative_stage2 = None

    if qualified:
        if direction == "LONG":
            indicative_stage1 = price - atr * first_atr
            indicative_stage2 = price - atr * second_atr
        else:
            indicative_stage1 = price + atr * first_atr
            indicative_stage2 = price + atr * second_atr

    hedge_policy = {
        "enabled": hedge_settings.get("enabled", True),
        "mode": "REVERSIBLE_ATR_TWO_STAGE",
        "first_trigger_atr": unit_7_text(first_atr),
        "second_trigger_atr": unit_7_text(second_atr),
        "stage1_close_original_percent": 50,
        "stage1_open_opposite_percent": 50,
        "stage2_close_remaining_percent": 100,
        "stage2_open_opposite_percent": 100,
        "maximum_recovery_cycles": 1,
        "conventional_stop_loss_enabled": False,
        "requires_actual_position_reconciliation": True,
        "requires_actual_fill_price": True
    }

    backup_policy = {
        "enabled": backup_settings.get("enabled", True),
        "count": backup_count,
        "margin_percent": unit_7_text(backup_margin),
        "liquidation_buffer_percent":
            unit_7_text(backup_buffer),
        "activation":
            "AFTER_FAILED_FIRST_HEDGE_RECOVERY",
        "independent_recalculation": True,
        "recalculate_after_every_fill": True,
        "require_available_balance": True,
        "require_exposure_cap": True,
        "require_verified_liquidation_price": True
    }

    entry_proposal = {
        "symbol": symbol,
        "direction": direction,
        "mode": mode,
        "signal_qualified": qualified,
        "requested_margin_usdt": unit_7_text(margin),
        "leverage": (
            unit_7_text(leverage)
            if leverage is not None
            else None
        ),
        "requested_notional_usdt": (
            unit_7_text(requested_notional)
            if requested_notional is not None
            else None
        ),
        "indicative_mark_price": unit_7_text(price),
        "quantity": None,
        "quantity_status": "AWAITING_EXCHANGE_METADATA",
        "contract_multiplier": None,
        "minimum_quantity": None,
        "quantity_step": None,
        "order_payload": None
    }

    if not qualified:
        entry_proposal["quantity_status"] = (
            "NO_QUALIFIED_SIGNAL"
        )

    # BOT_MODE controls only new initial entries.
    # Existing position management must remain independent.

    new_entry_enabled = (
        bot_mode == "RUN"
    )

    new_entry_intent = (
        qualified and new_entry_enabled
    )

    if not qualified:
        reason = "NO_QUALIFIED_ENTRY"
    elif not new_entry_enabled:
        reason = "QUALIFIED_ENTRY_PAUSED_BY_BOT_MODE"
    else:
        reason = "ENTRY_PROPOSAL_READY_FOR_UNIT8"

    result = {
        "unit": 7,
        "version": "UNIT7_FORWARD_ONLY_EXECUTABLE",

        "symbol": symbol,
        "base_coin": symbol[:-4],
        "quote_coin": "USDT",
        "capital_currency": "USDT",

        "active_mode": mode,
        "direction": direction,
        "signal_qualified": qualified,

        "execution_intent": qualified,
        "new_entry_intent": new_entry_intent,
        "new_entry_enabled": new_entry_enabled,
        "bot_mode": bot_mode,

        "entry_margin_usdt": unit_7_text(margin),
        "leverage_long": unit_7_text(long_leverage),
        "leverage_short": unit_7_text(short_leverage),
        "exposure_cap_percent":
            unit_7_text(exposure_cap),

        "entry_proposal": entry_proposal,
        "entry_sizing": entry_proposal,

        "quantity_status":
            entry_proposal["quantity_status"],

        "contract_verification_owner": "UNIT8",
        "final_quantity_calculation_owner":
            "DOWNSTREAM_AFTER_UNIT8",

        "hedge_policy": hedge_policy,
        "backup_policy": backup_policy,
        "backup_ladder": backup_policy,
        "backup_count": backup_count,

        "atr14": unit_7_text(atr),

        "indicative_stage1_trigger": (
            unit_7_text(indicative_stage1)
            if indicative_stage1 is not None
            else None
        ),

        "indicative_stage2_trigger": (
            unit_7_text(indicative_stage2)
            if indicative_stage2 is not None
            else None
        ),

        "existing_position_management_enabled": True,
        "existing_position_management_independent":
            True,

        "position_management_handover": {
            "enabled": True,
            "independent_of_bot_mode": True,
            "requires_exchange_position_read": True,
            "hedge_policy": hedge_policy,
            "backup_policy": backup_policy
        },

        "unit_6_candidate": signal,

        "execution_authorized": False,
        "order_payload_created": False,
        "exchange_write": False,
        "real_cash_execution_enabled": False,

        "reason": reason,
        "handover_to_unit8": "READY"
    }

    print(
        "UNIT 7 SYMBOL =", symbol,
        flush=True
    )

    print(
        "UNIT 7 MODE =", mode,
        flush=True
    )

    print(
        "UNIT 7 DIRECTION =", direction,
        flush=True
    )

    print(
        "UNIT 7 BOT_MODE =", bot_mode,
        flush=True
    )

    print(
        "UNIT 7 ENTRY MARGIN USDT =",
        unit_7_text(margin),
        flush=True
    )

    print(
        "UNIT 7 LONG LEVERAGE =",
        unit_7_text(long_leverage),
        flush=True
    )

    print(
        "UNIT 7 SHORT LEVERAGE =",
        unit_7_text(short_leverage),
        flush=True
    )

    print(
        "UNIT 7 REQUESTED NOTIONAL USDT =",
        entry_proposal["requested_notional_usdt"],
        flush=True
    )

    print(
        "UNIT 7 SIGNAL QUALIFIED =",
        qualified,
        flush=True
    )

    print(
        "UNIT 7 NEW ENTRY INTENT =",
        new_entry_intent,
        flush=True
    )

    print(
        "UNIT 7 QUANTITY STATUS =",
        result["quantity_status"],
        flush=True
    )

    print(
        "UNIT 7 HEDGE MODE =",
        hedge_policy["mode"],
        flush=True
    )

    print(
        "UNIT 7 BACKUP COUNT =",
        backup_count,
        flush=True
    )

    print(
        "UNIT 7 EXISTING POSITION MANAGEMENT = ENABLED",
        flush=True
    )

    print(
        "UNIT 7 REASON =", reason,
        flush=True
    )

    print(
        "UNIT 7 HANDOVER TO UNIT 8 = READY",
        flush=True
    )

    print(
        "UNIT 7 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "COMBINED RECONSTRUCTION UNIT 7 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# GLOBAL UNIT 7 EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_7_RESULT = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_UNIT_6_RESULT
    )
)

FRESH_UNIT_7_OPTIMIZATION_READY = True


# ============================================================
# END COMPLETE CORRECTED UNIT 7
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 8 V8
# COMBINED 17248 + 18426
# UNIVERSAL WEEX DEMO EXCHANGE ADAPTER
# USDT-BASED RENDER ENTRY MARGIN
# CONTRACT-AWARE QUANTITY
# UNIT 7 -> UNIT 8 -> UNIT 9 COMPATIBLE
# ZERO INDENTATION
# ============================================================

import os
import re
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.error

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_DOWN,
    ROUND_CEILING
)


U8_HOST = "https://api-contract.weex.com"
U8_MARKET_HOST = "https://api-sim.weex.com"

U8_PRIVATE_PATHS = {
    "/capi/v3/sim/balance",
    "/capi/v3/sim/position/allPosition",
    "/capi/v3/account/accountConfig",
}

U8_PUBLIC_PATHS = {
    "/capi/v3/market/exchangeInfo",
}


# ============================================================
# 8.1 DECIMAL HELPERS
# ============================================================

def u8_decimal(value, name, allow_zero=False):

    if value is None or isinstance(value, bool):
        raise ValueError(name + "_MISSING")

    try:
        number = Decimal(str(value))
    except (
        InvalidOperation,
        TypeError,
        ValueError
    ) as exc:
        raise ValueError(
            name + "_INVALID"
        ) from exc

    if not number.is_finite():
        raise ValueError(name + "_NONFINITE")

    if number < 0:
        raise ValueError(name + "_NEGATIVE")

    if number == 0 and not allow_zero:
        raise ValueError(name + "_ZERO")

    return number


def u8_text(value):
    return format(value, "f")


def u8_rows(payload):

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):

        for key in (
            "symbols",
            "list",
            "rows",
            "records",
            "positions",
            "balances",
        ):

            rows = payload.get(key)

            if isinstance(rows, list):
                return rows

    raise ValueError("WEEX_LIST_NOT_FOUND")


# ============================================================
# 8.2 UNIVERSAL SYMBOL
# ============================================================

def u8_selected_symbol(config):

    exchange = config.get("exchange", {})

    symbol = str(
        config.get("market_symbol")
        or exchange.get("market_symbol")
        or os.getenv("WEEX_SYMBOL", "")
    ).strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9]{2,20}USDT",
        symbol
    ):
        raise ValueError(
            "UNSUPPORTED_SYMBOL_FORMAT_" + symbol
        )

    return symbol


# ============================================================
# 8.3 WEEX READ-ONLY REQUEST
# ============================================================

def u8_get(path, private=False):

    if private:

        if path not in U8_PRIVATE_PATHS:
            raise RuntimeError(
                "UNIT8_PRIVATE_ENDPOINT_NOT_ALLOWED"
            )

        host = U8_HOST

    else:

        if path not in U8_PUBLIC_PATHS:
            raise RuntimeError(
                "UNIT8_PUBLIC_ENDPOINT_NOT_ALLOWED"
            )

        host = U8_MARKET_HOST

    headers = {
        "Accept": "application/json"
    }

    if private:

        key = (
            os.getenv("WEEX_API_KEY")
            or os.getenv("API_KEY")
        )

        secret = (
            os.getenv("WEEX_API_SECRET")
            or os.getenv("API_SECRET")
        )

        phrase = (
            os.getenv("WEEX_API_PASSPHRASE")
            or os.getenv("API_PASSPHRASE")
        )

        if not all((key, secret, phrase)):
            raise RuntimeError(
                "WEEX_API_CREDENTIALS_MISSING"
            )

        timestamp = str(int(time.time() * 1000))

        message = timestamp + "GET" + path

        signature = base64.b64encode(
            hmac.new(
                secret.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256
            ).digest()
        ).decode("utf-8")

        headers.update({
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": phrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US",
        })

    request = urllib.request.Request(
        host + path,
        headers=headers,
        method="GET"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            payload = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "WEEX_HTTP_" + str(exc.code)
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            "WEEX_REQUEST_" + type(exc).__name__
        ) from exc

    if isinstance(payload, dict):

        code = payload.get("code")

        if (
            payload.get("success") is False
            or (
                code is not None
                and str(code) not in (
                    "0", "200", "00000"
                )
            )
        ):
            raise RuntimeError(
                "WEEX_API_CODE_" + str(code)
            )

        return payload.get("data", payload)

    return payload


# ============================================================
# 8.4 CONTRACT METADATA
# ============================================================

def u8_contract(item, symbol):

    if not isinstance(item, dict):
        raise ValueError("CONTRACT_RECORD_INVALID")

    if str(
        item.get("symbol", "")
    ).upper() != symbol:
        raise ValueError("CONTRACT_SYMBOL_MISMATCH")

    base = symbol[:-4]

    if str(
        item.get("baseAsset", "")
    ).upper() != base:
        raise ValueError("CONTRACT_BASE_MISMATCH")

    if str(
        item.get("quoteAsset", "")
    ).upper() != "USDT":
        raise ValueError("CONTRACT_QUOTE_MISMATCH")

    quantity_precision = int(
        item["quantityPrecision"]
    )

    price_precision = int(
        item["pricePrecision"]
    )

    if not (
        0 <= quantity_precision <= 18
        and 0 <= price_precision <= 18
    ):
        raise ValueError("CONTRACT_PRECISION_INVALID")

    minimum = u8_decimal(
        item["minOrderSize"],
        "MINIMUM_QUANTITY"
    )

    multiplier = u8_decimal(
        item["contractVal"],
        "CONTRACT_MULTIPLIER"
    )

    quantity_step = Decimal(1).scaleb(
        -quantity_precision
    )

    price_step = Decimal(1).scaleb(
        -price_precision
    )

    maximum = item.get("maxOrderSize")

    if maximum not in (None, ""):
        maximum = u8_text(
            u8_decimal(
                maximum,
                "MAXIMUM_QUANTITY"
            )
        )

    return {
        "symbol": symbol,
        "base_asset": base,
        "quote_asset": "USDT",

        "margin_asset": str(
            item.get("marginAsset", "USDT")
        ).upper(),

        "minimum_quantity": u8_text(minimum),
        "maximum_quantity": maximum,

        "quantity_step": u8_text(quantity_step),
        "price_step": u8_text(price_step),

        "contract_multiplier": u8_text(
            multiplier
        ),

        "quantity_precision": quantity_precision,
        "price_precision": price_precision,

        "quantity_unit": "EXCHANGE_CONTRACT_UNITS",

        "verified": True,
        "source": "WEEX_MARKET_EXCHANGE_INFO",
    }


# ============================================================
# 8.5 DEMO POSITION EXTRACTION
# ============================================================

def u8_position_snapshot(rows, symbol):

    selected = []

    long_quantity = Decimal("0")
    short_quantity = Decimal("0")

    errors = []

    for item in rows:

        if not isinstance(item, dict):
            continue

        if str(
            item.get("symbol", "")
        ).upper() != symbol:
            continue

        raw_quantity = next(
            (
                item[key]
                for key in (
                    "size",
                    "total",
                    "holdVol",
                    "positionAmt",
                )
                if item.get(key) is not None
            ),
            None
        )

        if raw_quantity is None:
            errors.append("POSITION_SIZE_MISSING")
            continue

        try:
            quantity = u8_decimal(
                raw_quantity,
                "POSITION_QUANTITY",
                True
            )
        except ValueError:
            errors.append("POSITION_SIZE_INVALID")
            continue

        if quantity == 0:
            continue

        side = str(
            item.get("positionSide")
            or item.get("holdSide")
            or item.get("side")
            or ""
        ).upper()

        if side == "LONG":
            long_quantity += quantity

        elif side == "SHORT":
            short_quantity += quantity

        else:
            errors.append("POSITION_SIDE_UNKNOWN")

        selected.append(item)

    return {
        "positions": selected,

        "long_position_quantity":
            u8_text(long_quantity),

        "short_position_quantity":
            u8_text(short_quantity),

        "position_flat_verified": (
            not errors
            and long_quantity == 0
            and short_quantity == 0
        ),

        "position_data_complete": not errors,
        "position_parse_errors": errors,
    }


# ============================================================
# 8.6 USDT MARGIN -> EXCHANGE CONTRACT QUANTITY
# ============================================================

def u8_quantity_plan(proposal, contract):

    margin = u8_decimal(
        proposal["requested_margin_usdt"],
        "ENTRY_MARGIN_USDT"
    )

    leverage = u8_decimal(
        proposal["leverage"],
        "ENTRY_LEVERAGE"
    )

    price = u8_decimal(
        proposal["indicative_mark_price"],
        "ENTRY_MARK_PRICE"
    )

    step = u8_decimal(
        contract["quantity_step"],
        "QUANTITY_STEP"
    )

    minimum = u8_decimal(
        contract["minimum_quantity"],
        "MINIMUM_QUANTITY"
    )

    multiplier = u8_decimal(
        contract["contract_multiplier"],
        "CONTRACT_MULTIPLIER"
    )

    requested_notional = margin * leverage

    # Contract quantity, not USDT quantity.
    # Multiplier converts each contract to base asset.

    raw_quantity = (
        requested_notional
        / (price * multiplier)
    )

    quantity = (
        raw_quantity / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step

    minimum_steps = (
        minimum / step
    ).to_integral_value(
        rounding=ROUND_CEILING
    )

    executable_minimum = minimum_steps * step

    actual_notional = (
        quantity * multiplier * price
    )

    actual_margin = (
        actual_notional / leverage
    )

    maximum = contract.get("maximum_quantity")

    valid = (
        quantity > 0
        and quantity >= executable_minimum
        and actual_margin <= margin
    )

    if maximum not in (None, ""):
        valid = (
            valid
            and quantity <= u8_decimal(
                maximum,
                "MAXIMUM_QUANTITY"
            )
        )

    # Stage 1: approximately 50%.
    # Stage 2: the remaining quantity.
    # Both use the verified quantity step.

    first_half = (
        (quantity / 2) / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step

    remaining_half = quantity - first_half

    staged_hedge_valid = (
        valid
        and first_half >= executable_minimum
        and remaining_half >= executable_minimum
    )

    return {
        "valid": bool(valid),

        "reason": (
            "CONTRACT_QUANTITY_COMPLIANT"
            if valid
            else "ENTRY_QUANTITY_NOT_COMPLIANT"
        ),

        "raw_quantity": u8_text(raw_quantity),
        "quantity": u8_text(quantity),

        "requested_margin_usdt": u8_text(margin),
        "actual_margin_usdt": u8_text(actual_margin),

        "requested_notional_usdt":
            u8_text(requested_notional),

        "actual_notional_usdt":
            u8_text(actual_notional),

        "leverage": u8_text(leverage),
        "mark_price": u8_text(price),

        "minimum_quantity":
            u8_text(executable_minimum),

        "quantity_step": u8_text(step),

        "stage1_quantity": u8_text(first_half),

        "stage2_remaining_quantity":
            u8_text(remaining_half),

        "staged_hedge_quantity_valid":
            bool(staged_hedge_valid),

        "quantity_unit":
            "EXCHANGE_CONTRACT_UNITS",

        "contract_multiplier":
            u8_text(multiplier),

        "exchange_order_units_verified": False,
        "order_submitted": False,
    }


# ============================================================
# 8.7 MAIN UNIT
# ============================================================

def fresh_reconstruction_unit_8():

    print("=" * 80, flush=True)

    log("COMBINED RECONSTRUCTION UNIT 8 START")

    config = FRESH_RECONSTRUCTION_CONFIG
    unit7 = FRESH_RECONSTRUCTION_UNIT_7_RESULT

    if not isinstance(config, dict):
        raise RuntimeError("UNIT8_CONFIG_INVALID")

    if not isinstance(unit7, dict):
        raise RuntimeError("UNIT8_UNIT7_INVALID")

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled")
        is not False
    ):
        raise RuntimeError("UNIT8_DEMO_ONLY")

    symbol = u8_selected_symbol(config)

    if unit7.get("symbol") != symbol:
        raise RuntimeError(
            "UNIT8_UNIT7_SYMBOL_MISMATCH"
        )

    # Direct symbol mapping preserves the current
    # combined-model Unit 9 interface.

    demo_symbol = symbol

    result = {
        "unit": 8,
        "version": "UNIT8_V8_UNIVERSAL_USDT",

        "symbol": symbol,
        "market_symbol": symbol,
        "demo_symbol": demo_symbol,
        "demo_order_symbol": demo_symbol,

        "base_coin": symbol[:-4],
        "quote_coin": "USDT",

        "symbol_mapping": "DIRECT",

        "contract": None,
        "market_contract_verified": False,

        "demo_symbol_verified": False,
        "demo_contract_verified": False,

        "demo_balance_verified": False,
        "demo_positions_read_verified": False,

        "account_config_verified": False,
        "account_can_trade": None,
        "account_dual_side_enabled": None,

        "available_balance": None,
        "account_equity": None,

        "positions": [],
        "long_position_quantity": None,
        "short_position_quantity": None,
        "position_flat_verified": False,

        "quantity_plan": None,
        "size_preview": None,
        "quantity_valid": False,

        "trade_plan_ready": False,

        "active_mode": unit7.get(
            "active_mode", "NONE"
        ),

        "direction": unit7.get(
            "direction", "NONE"
        ),

        "signal_qualified": (
            unit7.get("signal_qualified") is True
        ),

        "execution_intent": (
            unit7.get("new_entry_intent") is True
        ),

        "entry_margin_usdt":
            config.get("initial_entry_margin_usdt"),

        "leverage_long":
            config.get("leverage_long"),

        "leverage_short":
            config.get("leverage_short"),

        "existing_position_management_enabled": True,
        "existing_position_management_independent": True,

        "status": "READ_PENDING",
        "reason": "ACCOUNT_AND_CONTRACT_PENDING",

        "errors": {},

        "read_only": True,
        "exchange_write": False,
        "order_payload_created": False,
        "real_cash_execution_enabled": False,

        "handover_to_unit9": "READY",
    }

    # ========================================================
    # PUBLIC MARKET CONTRACT
    # ========================================================

    try:
        directory = u8_rows(
            u8_get(
                "/capi/v3/market/exchangeInfo",
                private=False
            )
        )

        selected = next(
            (
                item
                for item in directory
                if isinstance(item, dict)
                and str(
                    item.get("symbol", "")
                ).upper() == symbol
            ),
            None
        )

        if selected is None:
            raise RuntimeError(
                "UNSUPPORTED_WEEX_CONTRACT_" + symbol
            )

        contract = u8_contract(
            selected,
            symbol
        )

        result["contract"] = contract
        result["market_contract_verified"] = True

    except Exception as exc:
        result["errors"]["market_contract"] = str(exc)

    # ========================================================
    # DEMO BALANCE
    # ========================================================

    try:
        balances = u8_rows(
            u8_get(
                "/capi/v3/sim/balance",
                private=True
            )
        )

        asset = next(
            (
                row
                for row in balances
                if isinstance(row, dict)
                and str(
                    row.get("asset", "")
                ).upper() == "SUSDT"
            ),
            None
        )

        if asset is None:
            raise RuntimeError(
                "DEMO_SUSDT_BALANCE_MISSING"
            )

        available = u8_decimal(
            asset.get("availableBalance"),
            "AVAILABLE_BALANCE",
            True
        )

        result["available_balance"] = u8_text(
            available
        )

        result["demo_balance_verified"] = True

        equity_raw = asset.get("equity")

        if equity_raw is not None:
            result["account_equity"] = u8_text(
                u8_decimal(
                    equity_raw,
                    "ACCOUNT_EQUITY",
                    True
                )
            )

    except Exception as exc:
        result["errors"]["demo_balance"] = str(exc)

    # ========================================================
    # DEMO POSITION READ
    # ========================================================

    try:
        positions = u8_rows(
            u8_get(
                "/capi/v3/sim/position/allPosition",
                private=True
            )
        )

        snapshot = u8_position_snapshot(
            positions,
            demo_symbol
        )

        result.update(snapshot)

        result["demo_positions_read_verified"] = (
            snapshot["position_data_complete"]
        )

    except Exception as exc:
        result["errors"]["demo_positions"] = str(exc)

    # ========================================================
    # ACCOUNT CONFIGURATION
    # ========================================================

    try:
        account = u8_get(
            "/capi/v3/account/accountConfig",
            private=True
        )

        if not isinstance(account, dict):
            raise RuntimeError(
                "ACCOUNT_CONFIG_INVALID"
            )

        can_trade = account.get("canTrade")

        dual_side = account.get(
            "dualSidePosition"
        )

        if isinstance(can_trade, bool):
            result["account_can_trade"] = can_trade

        if isinstance(dual_side, bool):
            result["account_dual_side_enabled"] = (
                dual_side
            )

        result["account_config_verified"] = True

    except Exception as exc:
        result["errors"]["account_config"] = str(exc)

    # ========================================================
    # CONTRACT-AWARE QUANTITY
    # ========================================================

    proposal = unit7.get(
        "entry_proposal", {}
    )

    if (
        unit7.get("signal_qualified") is True
        and isinstance(proposal, dict)
        and isinstance(result["contract"], dict)
        and proposal.get("leverage") is not None
    ):

        try:
            plan = u8_quantity_plan(
                proposal,
                result["contract"]
            )

            result["quantity_plan"] = plan
            result["size_preview"] = plan
            result["quantity_valid"] = (
                plan["valid"]
            )

        except Exception as exc:
            result["errors"]["quantity"] = str(exc)

    # ========================================================
    # SYMBOL VERIFICATION
    # ========================================================

    # Public contract verification is not proof
    # that a demo order will be accepted.
    # The demo endpoint remains authoritative.

    result["demo_symbol_verified"] = (
        result["market_contract_verified"]
    )

    result["demo_contract_verified"] = (
        result["market_contract_verified"]
    )

    result["demo_symbol_verification_basis"] = (
        "PUBLIC_CONTRACT_ONLY"
        if result["market_contract_verified"]
        else "NOT_VERIFIED"
    )

    # ========================================================
    # HANDOVER STATUS
    # ========================================================

    result["trade_plan_ready"] = bool(
        result["execution_intent"]
        and result["market_contract_verified"]
        and result["quantity_valid"]
        and result["demo_balance_verified"]
        and result["demo_positions_read_verified"]
        and result["account_can_trade"] is True
        and result["position_flat_verified"]
    )

    if result["trade_plan_ready"]:

        result["status"] = "TRADE_PLAN_PREPARED"

        result["reason"] = (
            "READY_FOR_DOWNSTREAM_DEMO_CHECKS"
        )

    elif not result["signal_qualified"]:

        result["status"] = "READ_COMPLETE"

        result["reason"] = (
            "ACCOUNT_AND_MARKET_READ_COMPLETE"
        )

    elif not result["execution_intent"]:

        result["status"] = "READ_COMPLETE"

        result["reason"] = "NEW_ENTRY_NOT_REQUESTED"

    else:

        result["status"] = "WAITING"

        result["reason"] = (
            "ENTRY_REQUIREMENTS_NOT_YET_MET"
        )

    # ========================================================
    # RENDER REPORT
    # ========================================================

    print(
        "UNIT 8 SELECTED SYMBOL =",
        symbol,
        flush=True
    )

    print(
        "UNIT 8 DEMO ORDER SYMBOL =",
        demo_symbol,
        flush=True
    )

    print(
        "UNIT 8 SYMBOL MAPPING = DIRECT",
        flush=True
    )

    print(
        "UNIT 8 MARKET CONTRACT VERIFIED =",
        result["market_contract_verified"],
        flush=True
    )

    print(
        "UNIT 8 DEMO BALANCE VERIFIED =",
        result["demo_balance_verified"],
        flush=True
    )

    print(
        "UNIT 8 DEMO POSITIONS READ =",
        result["demo_positions_read_verified"],
        flush=True
    )

    print(
        "UNIT 8 LONG POSITION QUANTITY =",
        result["long_position_quantity"],
        flush=True
    )

    print(
        "UNIT 8 SHORT POSITION QUANTITY =",
        result["short_position_quantity"],
        flush=True
    )

    print(
        "UNIT 8 AVAILABLE BALANCE =",
        result["available_balance"],
        flush=True
    )

    print(
        "UNIT 8 ACCOUNT CAN TRADE =",
        result["account_can_trade"],
        flush=True
    )

    print(
        "UNIT 8 ENTRY MARGIN USDT =",
        result["entry_margin_usdt"],
        flush=True
    )

    print(
        "UNIT 8 QUANTITY VALID =",
        result["quantity_valid"],
        flush=True
    )

    print(
        "UNIT 8 SIZE PREVIEW =",
        result["size_preview"],
        flush=True
    )

    print(
        "UNIT 8 TRADE PLAN READY =",
        result["trade_plan_ready"],
        flush=True
    )

    print(
        "UNIT 8 STATUS =",
        result["status"],
        flush=True
    )

    print(
        "UNIT 8 REASON =",
        result["reason"],
        flush=True
    )

    print(
        "UNIT 8 ERRORS =",
        result["errors"],
        flush=True
    )

    print(
        "UNIT 8 HANDOVER TO UNIT 9 = READY",
        flush=True
    )

    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "COMBINED RECONSTRUCTION UNIT 8 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 8.8 STARTUP AND GLOBAL HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    fresh_reconstruction_unit_8()
)

FRESH_UNIT_8_OPTIMIZATION_READY = True

# ============================================================
# END COMPLETE UNIT 8 V8
# UNIT 9 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 9 REPLACEMENT
# UNIT 9 - UNIVERSAL DEMO TRADE PLAN
# REFERENCES: 17248 AND 18426
# ZERO INDENTATION
# ============================================================

from decimal import Decimal, InvalidOperation, ROUND_DOWN


def u9_number(value, default=None):

    if value is None or isinstance(value, bool):
        return default

    try:
        number = Decimal(str(value))
        if not number.is_finite():
            return default
        return number
    except (ValueError, TypeError, InvalidOperation):
        return default


def u9_string(value):

    if isinstance(value, Decimal):
        return format(value, "f")

    return str(value)


def u9_config_value(config, key, default=None):

    if not isinstance(config, dict):
        return default

    if config.get(key) is not None:
        return config[key]

    strategy = config.get("strategy", {})

    if isinstance(strategy, dict):
        if strategy.get(key) is not None:
            return strategy[key]

    return default


def u9_result_template(symbol):

    return {
        "unit": 9,
        "version": "UNIT9_UNIVERSAL_FORWARD_V1",

        "status": "IDLE",
        "reason": "NO_ENTRY_CANDIDATE",
        "skip_reason": "NO_ENTRY_CANDIDATE",

        "symbol": symbol,
        "market_symbol": symbol,
        "demo_order_symbol": symbol,

        "active_mode": "NONE",
        "direction": "NONE",

        "signal_qualified": False,
        "execution_intent": False,

        "trade_plan_ready": False,
        "trade_plan": None,

        "execution_ready": False,
        "execution_candidate": None,

        "quantity": None,
        "selected_leverage": None,

        "margin_budget_prechecked": False,
        "margin_budget_fresh_verified": False,

        "trade_authorized": False,
        "execution_authorized": False,
        "order_submission_authorized": False,
        "order_payload_created": False,

        "existing_position_management_enabled": True,
        "existing_position_management_independent": True,

        "exchange_write": False,
        "read_only": True,
        "real_cash_execution_enabled": False,

        "handover_to_unit10": "READY"
    }


def fresh_reconstruction_unit_9(
    config,
    unit8,
    unit7
):

    print("=" * 80, flush=True)
    print(
        "COMBINED RECONSTRUCTION UNIT 9 START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError("UNIT9_CONFIG_INVALID")

    if not isinstance(unit8, dict):
        raise RuntimeError("UNIT9_UNIT8_INVALID")

    if not isinstance(unit7, dict):
        raise RuntimeError("UNIT9_UNIT7_INVALID")

    exchange = config.get("exchange", {})

    symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    if not symbol:
        raise RuntimeError("UNIT9_SYMBOL_MISSING")

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled")
        is not False
    ):
        raise RuntimeError("UNIT9_DEMO_ONLY")

    if (
        unit8.get("market_symbol") != symbol
        or unit8.get("demo_order_symbol") != symbol
        or unit7.get("symbol") != symbol
    ):
        raise RuntimeError(
            "UNIT9_SYMBOL_HANDOVER_MISMATCH"
        )

    result = u9_result_template(symbol)

    result["bot_mode"] = str(
        config.get("bot_mode", "PAUSE")
    ).upper()

    result["contract"] = unit8.get("contract")
    result["unit8_status"] = unit8.get("status")

    result["available_balance"] = (
        unit8.get("available_balance")
    )

    result["long_position_quantity"] = (
        unit8.get("long_position_quantity")
    )

    result["short_position_quantity"] = (
        unit8.get("short_position_quantity")
    )

    result["position_flat_verified"] = (
        unit8.get("position_flat_verified") is True
    )

    result["position_management_handover"] = (
        unit7.get("position_management_handover")
    )

    result["positions"] = unit8.get(
        "positions", []
    )

    result["demo_positions_read_verified"] = (
        unit8.get("demo_positions_read_verified")
        is True
    )

    result["hedge_policy"] = unit7.get(
        "hedge_policy", {}
    )

    result["backup_policy"] = unit7.get(
        "backup_policy", {}
    )

    result["backup_count"] = unit7.get(
        "backup_count", 5
    )

    result["exposure_cap_percent"] = (
        unit7.get(
            "exposure_cap_percent",
            u9_config_value(
                config,
                "exposure_cap_percent",
                100
            )
        )
    )

    result["tp1_net_roi_percent"] = u9_config_value(
        config, "tp1_net_roi_percent", 20
    )

    result["tp2_net_roi_percent"] = u9_config_value(
        config, "tp2_net_roi_percent", 40
    )

    result["tp_allocation"] = {
        "tp1_percent": 10,
        "tp2_percent": 20,
        "tp3_percent": 70
    }

    def finish(status, reason):

        result["status"] = status
        result["reason"] = reason
        result["skip_reason"] = (
            None if status == "READY" else reason
        )

        print(
            "UNIT 9 SYMBOL =",
            symbol,
            flush=True
        )

        print(
            "UNIT 9 DEMO SYMBOL =",
            result["demo_order_symbol"],
            flush=True
        )

        print(
            "UNIT 9 BOT_MODE =",
            result["bot_mode"],
            flush=True
        )

        print(
            "UNIT 9 MODE =",
            result["active_mode"],
            flush=True
        )

        print(
            "UNIT 9 DIRECTION =",
            result["direction"],
            flush=True
        )

        print(
            "UNIT 9 QUANTITY =",
            result["quantity"],
            flush=True
        )

        print(
            "UNIT 9 TRADE PLAN READY =",
            result["trade_plan_ready"],
            flush=True
        )

        print(
            "UNIT 9 EXECUTION READY =",
            result["execution_ready"],
            flush=True
        )

        print(
            "UNIT 9 EXISTING POSITION MANAGEMENT =",
            "INDEPENDENT",
            flush=True
        )

        print(
            "UNIT 9 STATUS =",
            status,
            flush=True
        )

        print(
            "UNIT 9 REASON =",
            reason,
            flush=True
        )

        print(
            "UNIT 9 HANDOVER TO UNIT 10 = READY",
            flush=True
        )

        print(
            "UNIT 9 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "COMBINED RECONSTRUCTION UNIT 9 RESULT = PASS",
            flush=True
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # EXISTING POSITION MANAGEMENT REMAINS INDEPENDENT
    # ========================================================

    # Unit 9 prepares new entry candidates only.
    # Units 13-14 will manage existing positions.
    # BOT_MODE=PAUSE must not disable position management.

    mode = str(
        unit7.get("active_mode", "NONE")
    ).upper()

    direction = str(
        unit7.get("direction", "NONE")
    ).upper()

    result["active_mode"] = mode
    result["direction"] = direction

    result["signal_qualified"] = (
        unit7.get("signal_qualified") is True
    )

    result["execution_intent"] = (
        unit7.get("new_entry_intent") is True
    )

    if not result["signal_qualified"]:
        return finish(
            "IDLE",
            "NO_QUALIFIED_ENTRY"
        )

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT"
    ):
        return finish(
            "IDLE",
            "NO_QUALIFIED_MODE"
        )

    if direction not in ("LONG", "SHORT"):
        return finish(
            "IDLE",
            "NO_QUALIFIED_DIRECTION"
        )

    if result["bot_mode"] != "RUN":
        return finish(
            "PAUSED",
            "NEW_ENTRIES_PAUSED"
        )

    if not result["execution_intent"]:
        return finish(
            "IDLE",
            "NO_NEW_ENTRY_INTENT"
        )

    # ========================================================
    # UNIT 8 EXCHANGE DATA
    # ========================================================

    if unit8.get("market_contract_verified") is not True:
        return finish(
            "WAITING",
            "MARKET_CONTRACT_UNAVAILABLE"
        )

    if unit8.get("demo_balance_verified") is not True:
        return finish(
            "WAITING",
            "DEMO_BALANCE_UNAVAILABLE"
        )

    if unit8.get("demo_positions_read_verified") is not True:
        return finish(
            "WAITING",
            "DEMO_POSITIONS_UNAVAILABLE"
        )

    if unit8.get("account_can_trade") is not True:
        return finish(
            "WAITING",
            "ACCOUNT_TRADING_NOT_ENABLED"
        )

    # This flat-position requirement applies only to
    # NEW INITIAL ENTRIES, not existing-position
    # management or hedge/backup execution.

    if not result["position_flat_verified"]:
        return finish(
            "IDLE",
            "EXISTING_POSITION_PRESENT_OR_UNVERIFIED"
        )

    contract = unit8.get("contract")
    preview = unit8.get("size_preview")

    if not isinstance(contract, dict):
        return finish(
            "WAITING",
            "CONTRACT_DATA_MISSING"
        )

    if not isinstance(preview, dict):
        return finish(
            "WAITING",
            "ENTRY_SIZE_PREVIEW_MISSING"
        )

    if preview.get("valid") is not True:
        return finish(
            "WAITING",
            "ENTRY_QUANTITY_INVALID"
        )

    # ========================================================
    # QUANTITY VALIDATION
    # ========================================================

    quantity = u9_number(
        preview.get("quantity")
    )

    minimum = u9_number(
        contract.get("minimum_quantity")
    )

    step = u9_number(
        contract.get("quantity_step")
    )

    multiplier = u9_number(
        contract.get("contract_multiplier")
    )

    leverage = u9_number(
        preview.get("leverage")
    )

    entry_margin = u9_number(
        preview.get("actual_margin_usdt")
    )

    available = u9_number(
        unit8.get("available_balance")
    )

    if any(
        value is None or value <= 0
        for value in (
            quantity,
            minimum,
            step,
            multiplier,
            leverage,
            entry_margin
        )
    ):
        return finish(
            "WAITING",
            "ENTRY_NUMERIC_DATA_INVALID"
        )

    if available is None or available < entry_margin:
        return finish(
            "WAITING",
            "INSUFFICIENT_DEMO_BALANCE"
        )

    if (
        quantity < minimum
        or quantity % step != 0
    ):
        return finish(
            "WAITING",
            "QUANTITY_STEP_OR_MINIMUM_INVALID"
        )

    maximum = u9_number(
        contract.get("maximum_quantity")
    )

    if maximum is not None and quantity > maximum:
        return finish(
            "WAITING",
            "QUANTITY_ABOVE_MAXIMUM"
        )

    configured_leverage = u9_number(
        unit7.get(
            "leverage_long"
            if direction == "LONG"
            else "leverage_short"
        )
    )

    if (
        configured_leverage is None
        or leverage != configured_leverage
    ):
        return finish(
            "WAITING",
            "LEVERAGE_CONFIGURATION_MISMATCH"
        )

    # ========================================================
    # EXPOSURE BUDGET PRECHECK
    # ========================================================

    exposure_cap = u9_number(
        result["exposure_cap_percent"]
    )

    if (
        exposure_cap is None
        or exposure_cap <= 0
        or exposure_cap > 100
    ):
        return finish(
            "WAITING",
            "EXPOSURE_CAP_INVALID"
        )

    # Available balance alone is not total equity.
    # This is a preliminary margin budget check.
    # Downstream execution must refresh account
    # balances, exposure and actual position state.

    result["margin_budget_prechecked"] = (
        entry_margin <= available
    )

    # ========================================================
    # PREPARE UNIVERSAL DEMO TRADE PLAN
    # ========================================================

    first_half = u9_number(
        preview.get("stage1_quantity")
    )

    second_half = u9_number(
        preview.get("stage2_remaining_quantity")
    )

    staged_hedge_valid = (
        preview.get("staged_hedge_quantity_valid")
        is True
    )

    trade_plan = {
        "symbol": symbol,
        "market_symbol": symbol,
        "demo_order_symbol": symbol,

        "execution_environment": "DEMO",

        "active_mode": mode,
        "direction": direction,

        "quantity": u9_string(quantity),

        "quantity_unit":
            preview.get("quantity_unit"),

        "minimum_quantity":
            u9_string(minimum),

        "quantity_step":
            u9_string(step),

        "contract_multiplier":
            u9_string(multiplier),

        "leverage":
            u9_string(leverage),

        "entry_margin_usdt":
            u9_string(entry_margin),

        "requested_margin_usdt":
            preview.get("requested_margin_usdt"),

        "requested_notional_usdt":
            preview.get("requested_notional_usdt"),

        "actual_notional_usdt":
            preview.get("actual_notional_usdt"),

        "indicative_mark_price":
            preview.get("mark_price"),

        "stage1_hedge_quantity":
            (
                u9_string(first_half)
                if first_half is not None
                else None
            ),

        "stage2_remaining_quantity":
            (
                u9_string(second_half)
                if second_half is not None
                else None
            ),

        "staged_hedge_quantity_valid":
            staged_hedge_valid,

        "hedge_policy":
            result["hedge_policy"],

        "backup_policy":
            result["backup_policy"],

        "backup_count":
            result["backup_count"],

        "tp1_net_roi_percent":
            result["tp1_net_roi_percent"],

        "tp2_net_roi_percent":
            result["tp2_net_roi_percent"],

        "tp_allocation":
            result["tp_allocation"],

        "contract": contract,

        "unit8_size_preview": preview,

        "requires_fresh_balance": True,
        "requires_fresh_position_read": True,
        "requires_demo_order_response": True,

        "order_submitted": False,
        "real_cash_execution_enabled": False
    }

    execution_candidate = {
        "active_mode": mode,
        "direction": direction,
        "trade_plan": trade_plan,
        "execution_environment": "DEMO"
    }

    result.update({
        "status": "READY",
        "reason": "VALIDATED_DEMO_ENTRY_CANDIDATE",
        "skip_reason": None,

        "trade_plan_ready": True,
        "trade_plan": trade_plan,

        "execution_ready": True,
        "execution_candidate": execution_candidate,

        "quantity": u9_string(quantity),

        "selected_leverage":
            u9_string(leverage),

        "margin_budget_prechecked": True,

        "margin_budget_fresh_verified": False,

        "trade_authorized": False,
        "execution_authorized": False,

        "order_submission_authorized": False,
        "order_payload_created": False,

        "exchange_write": False,
        "read_only": True
    })

    return finish(
        "READY",
        "VALIDATED_DEMO_ENTRY_CANDIDATE"
    )


# ============================================================
# UNIT 9 STARTUP EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
        FRESH_RECONSTRUCTION_UNIT_7_RESULT
    )
)

FRESH_UNIT_9_OPTIMIZATION_READY = True


# ============================================================
# END COMPLETE UNIT 9 REPLACEMENT
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 10 REPLACEMENT
# UNIVERSAL DEMO EXECUTION HANDOVER
# ZERO INDENTATION
# ============================================================

from decimal import Decimal, InvalidOperation


def u10_number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
        return number if number.is_finite() else None
    except (TypeError, ValueError, InvalidOperation):
        return None


def fresh_reconstruction_unit_10(
    config,
    unit9,
    unit8=None
):
    print("=" * 80, flush=True)
    print(
        "COMBINED RECONSTRUCTION UNIT 10 START",
        flush=True
    )

    if unit8 is None:
        unit8 = globals().get(
            "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
        )

    config = config if isinstance(config, dict) else {}
    unit9 = unit9 if isinstance(unit9, dict) else {}
    unit8 = unit8 if isinstance(unit8, dict) else {}

    exchange = config.get("exchange", {})
    exchange = exchange if isinstance(exchange, dict) else {}

    symbol = str(
        exchange.get("market_symbol")
        or config.get("market_symbol")
        or ""
    ).strip().upper()

    demo_symbol = str(
        unit8.get("demo_order_symbol")
        or ""
    ).strip().upper()

    mode = str(
        unit9.get("active_mode") or "NONE"
    ).upper()

    direction = str(
        unit9.get("direction") or "NONE"
    ).upper()

    bot_mode = str(
        config.get("bot_mode", "PAUSE")
    ).upper()

    result = {
        "unit": 10,
        "version": "U10_UNIVERSAL_DEMO_HANDOVER_V1",

        "market_symbol": symbol,
        "symbol": symbol,
        "demo_order_symbol": demo_symbol,

        "execution_environment": "DEMO",
        "bot_mode": bot_mode,

        "active_mode": mode,
        "direction": direction,

        "status": "IDLE",
        "reason": "NOT_EVALUATED",
        "skip_reason": None,

        "signal_qualified": False,
        "execution_intent": False,

        "trade_plan": unit9.get("trade_plan"),
        "execution_candidate":
            unit9.get("execution_candidate"),

        "trade_plan_ready": False,
        "demo_boundary_ready": False,
        "execution_ready": False,

        "quantity": unit9.get("quantity"),
        "contract": unit8.get("contract"),

        "demo_balance_verified": (
            unit8.get("demo_balance_verified") is True
        ),

        "demo_positions_read_verified": (
            unit8.get("demo_positions_read_verified") is True
        ),

        "position_flat_verified": (
            unit8.get("position_flat_verified") is True
        ),

        "position_management_handover":
            unit9.get("position_management_handover"),

        "positions": unit8.get("positions", []),

        "long_position_quantity":
            unit8.get("long_position_quantity"),

        "short_position_quantity":
            unit8.get("short_position_quantity"),

        "hedge_policy": unit9.get("hedge_policy", {}),
        "backup_policy": unit9.get("backup_policy", {}),

        "backup_count": unit9.get("backup_count", 5),

        "exposure_cap_percent":
            unit9.get("exposure_cap_percent"),

        "tp1_net_roi_percent":
            unit9.get("tp1_net_roi_percent"),

        "tp2_net_roi_percent":
            unit9.get("tp2_net_roi_percent"),

        "tp_allocation": unit9.get("tp_allocation"),

        "requires_fresh_balance": True,
        "requires_fresh_position_read": True,
        "requires_demo_order_response": True,

        "exchange_order_units_verified": (
            unit8.get("size_preview", {}).get(
                "exchange_order_units_verified", False
            )
            if isinstance(
                unit8.get("size_preview"), dict
            )
            else False
        ),

        "demo_order_permission_verified": False,
        "demo_order_submission_verified": False,

        "execution_authorized": False,
        "order_submission_authorized": False,
        "order_payload_created": False,
        "demo_submission_requested": False,

        "read_only": True,
        "exchange_write": False,
        "real_cash_execution": False
    }

    def finish(status, reason):
        result["status"] = status
        result["reason"] = reason
        result["skip_reason"] = (
            None if status == "READY" else reason
        )

        for label, key in (
            ("MARKET SYMBOL", "market_symbol"),
            ("DEMO ORDER SYMBOL", "demo_order_symbol"),
            ("BOT_MODE", "bot_mode"),
            ("MODE", "active_mode"),
            ("DIRECTION", "direction"),
            ("SIGNAL QUALIFIED", "signal_qualified"),
            ("TRADE PLAN READY", "trade_plan_ready"),
            ("DEMO BOUNDARY READY", "demo_boundary_ready"),
            ("EXECUTION READY", "execution_ready"),
            ("EXCHANGE ORDER UNITS VERIFIED",
             "exchange_order_units_verified"),
            ("STATUS", "status"),
            ("REASON", "reason"),
            ("EXECUTION AUTHORIZED",
             "execution_authorized")
        ):
            print(
                "UNIT 10 " + label + " =",
                result.get(key),
                flush=True
            )

        print(
            "UNIT 10 EXISTING POSITION MANAGEMENT = "
            "INDEPENDENT",
            flush=True
        )
        print(
            "UNIT 10 HANDOVER TO UNIT 11 = READY",
            flush=True
        )
        print(
            "UNIT 10 EXCHANGE WRITE = NONE",
            flush=True
        )
        print(
            "UNIT 10 REAL CASH EXECUTION = DISABLED",
            flush=True
        )
        print(
            "COMBINED RECONSTRUCTION UNIT 10 RESULT =",
            "PASS" if status != "ERROR" else "FAIL",
            flush=True
        )
        print("=" * 80, flush=True)

        return result

    # --------------------------------------------------------
    # DEMO CONFIGURATION
    # --------------------------------------------------------

    if not symbol:
        return finish(
            "ERROR", "MARKET_SYMBOL_MISSING"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled")
        is not False
    ):
        return finish(
            "ERROR", "DEMO_ONLY_CONFIGURATION_REQUIRED"
        )

    if (
        unit8.get("market_symbol") != symbol
        or demo_symbol != symbol
        or unit9.get("market_symbol") != symbol
    ):
        return finish(
            "ERROR", "SYMBOL_HANDOVER_MISMATCH"
        )

    # --------------------------------------------------------
    # PRESERVE PAUSED AND IDLE ENTRIES
    # --------------------------------------------------------

    status9 = str(
        unit9.get("status") or "IDLE"
    ).upper()

    if bot_mode != "RUN":
        return finish(
            "PAUSED", "NEW_ENTRIES_PAUSED"
        )

    if status9 in ("PAUSED", "IDLE", "WAITING"):
        return finish(
            status9,
            str(unit9.get("reason") or "NO_ENTRY")
        )

    if status9 != "READY":
        return finish(
            "WAITING", "UNIT_9_NOT_READY"
        )

    # --------------------------------------------------------
    # VERIFY READ HANDOVER
    # --------------------------------------------------------

    if unit8.get("market_contract_verified") is not True:
        return finish(
            "WAITING", "MARKET_CONTRACT_NOT_VERIFIED"
        )

    if unit8.get("demo_balance_verified") is not True:
        return finish(
            "WAITING", "DEMO_BALANCE_NOT_VERIFIED"
        )

    if (
        unit8.get("demo_positions_read_verified")
        is not True
    ):
        return finish(
            "WAITING", "DEMO_POSITIONS_NOT_VERIFIED"
        )

    if unit8.get("account_can_trade") is not True:
        return finish(
            "WAITING", "ACCOUNT_TRADING_UNAVAILABLE"
        )

    if unit8.get("position_flat_verified") is not True:
        return finish(
            "IDLE", "NEW_ENTRY_REQUIRES_FLAT_POSITION"
        )

    # --------------------------------------------------------
    # VERIFY UNIT 9 TRADE PLAN
    # --------------------------------------------------------

    plan = unit9.get("trade_plan")
    candidate = unit9.get("execution_candidate")

    if not isinstance(plan, dict):
        return finish(
            "WAITING", "TRADE_PLAN_MISSING"
        )

    if not isinstance(candidate, dict):
        return finish(
            "WAITING", "EXECUTION_CANDIDATE_MISSING"
        )

    if (
        unit9.get("trade_plan_ready") is not True
        or unit9.get("execution_ready") is not True
    ):
        return finish(
            "WAITING", "UNIT_9_PLAN_NOT_READY"
        )

    if (
        plan.get("market_symbol") != symbol
        or plan.get("demo_order_symbol") != demo_symbol
        or plan.get("execution_environment") != "DEMO"
    ):
        return finish(
            "WAITING", "TRADE_PLAN_SYMBOL_MISMATCH"
        )

    if mode not in (
        "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        return finish(
            "IDLE", "NO_QUALIFIED_MODE"
        )

    if direction not in ("LONG", "SHORT"):
        return finish(
            "IDLE", "NO_QUALIFIED_DIRECTION"
        )

    quantity = u10_number(plan.get("quantity"))
    leverage = u10_number(plan.get("leverage"))
    margin = u10_number(
        plan.get("entry_margin_usdt")
    )

    if (
        quantity is None or quantity <= 0
        or leverage is None or leverage <= 0
        or margin is None or margin <= 0
    ):
        return finish(
            "WAITING", "INVALID_ENTRY_SIZING"
        )

    preview = unit8.get("size_preview")

    if (
        not isinstance(preview, dict)
        or preview.get("valid") is not True
        or u10_number(preview.get("quantity")) != quantity
    ):
        return finish(
            "WAITING", "QUANTITY_PREVIEW_MISMATCH"
        )

    # --------------------------------------------------------
    # SUCCESSFUL READ-ONLY HANDOVER
    # --------------------------------------------------------

    result.update({
        "status": "READY",
        "reason": "DEMO_TRADE_PLAN_VALIDATED",

        "signal_qualified": (
            unit9.get("signal_qualified") is True
        ),

        "execution_intent": (
            unit9.get("execution_intent") is True
        ),

        "trade_plan_ready": True,
        "demo_boundary_ready": True,
        "execution_ready": True,

        "quantity": str(quantity),
        "selected_leverage": str(leverage),
        "entry_margin_usdt": str(margin),

        "trade_plan": plan,
        "execution_candidate": candidate,

        # Unit 11 prepares a fresh executable order.
        # Unit 12 submits it to WEEX demo.
        # Neither action happens in Unit 10.

        "execution_authorized": False,
        "order_submission_authorized": False,
        "order_payload_created": False,
        "demo_submission_requested": False,

        "exchange_write": False,
        "read_only": True,
        "real_cash_execution": False
    })

    return finish(
        "READY", "DEMO_TRADE_PLAN_VALIDATED"
    )


# ============================================================
# UNIT 10 STARTUP EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
    fresh_reconstruction_unit_10(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT
    )
)

FRESH_UNIT_10_OPTIMIZATION_READY = (
    isinstance(
        FRESH_RECONSTRUCTION_UNIT_10_RESULT, dict
    )
    and FRESH_RECONSTRUCTION_UNIT_10_RESULT.get(
        "read_only"
    ) is True
    and FRESH_RECONSTRUCTION_UNIT_10_RESULT.get(
        "exchange_write"
    ) is False
    and FRESH_RECONSTRUCTION_UNIT_10_RESULT.get(
        "status"
    ) in ("READY", "PAUSED", "IDLE", "WAITING")
)

print(
    "UNIT 10 OPTIMIZATION READY =",
    FRESH_UNIT_10_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 10 REPLACEMENT
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE UNIT 11 REPLACEMENT
# WEEX DEMO ORDER PREPARATION
# REFERENCES: 17248 / 18426 RECONSTRUCTION
# ZERO INDENTATION
# ============================================================

from decimal import Decimal, InvalidOperation


def u11_decimal(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
        if number.is_finite():
            return number
    except (InvalidOperation, TypeError, ValueError):
        pass
    return None


def u11_decimal_string(value):
    return format(value, "f")


def u11_positive(value):
    number = u11_decimal(value)
    return number is not None and number > 0


def fresh_reconstruction_unit_11(
    config,
    unit10,
    unit9,
    unit8
):
    print("=" * 80, flush=True)
    print(
        "COMBINED RECONSTRUCTION UNIT 11 START",
        flush=True
    )

    config = config if isinstance(config, dict) else {}
    unit10 = unit10 if isinstance(unit10, dict) else {}
    unit9 = unit9 if isinstance(unit9, dict) else {}
    unit8 = unit8 if isinstance(unit8, dict) else {}

    exchange = config.get("exchange", {})
    exchange = exchange if isinstance(exchange, dict) else {}

    symbol = str(
        exchange.get("market_symbol")
        or config.get("market_symbol")
        or ""
    ).strip().upper()

    bot_mode = str(
        config.get("bot_mode", "PAUSE")
    ).strip().upper()

    result = {
        "unit": 11,
        "version": "U11_DEMO_ORDER_PREPARATION_V1",

        "market_symbol": symbol,
        "symbol": symbol,
        "demo_order_symbol": symbol,

        "execution_environment": "DEMO",
        "bot_mode": bot_mode,

        "status": "IDLE",
        "reason": "NOT_EVALUATED",
        "skip_reason": None,

        "active_mode": "NONE",
        "direction": "NONE",

        "signal_qualified": False,
        "execution_intent": False,

        "trade_plan_ready": False,
        "trade_plan": None,

        "order_prepared": False,
        "order_payload_created": False,
        "order_request": None,

        "quantity": None,
        "selected_leverage": None,
        "entry_margin_usdt": None,

        "order_type": "MARKET",
        "order_intent": "OPEN_INITIAL_POSITION",

        "requires_fresh_balance": True,
        "requires_fresh_position_read": True,
        "requires_demo_order_response": True,

        "exchange_order_units_verified": False,
        "demo_order_permission_verified": False,

        "execution_ready": False,
        "execution_authorized": False,
        "order_submission_authorized": False,
        "order_submitted": False,

        "existing_position_management_enabled": True,
        "existing_position_management_independent": True,

        "position_management_handover":
            unit10.get("position_management_handover")
            or unit9.get("position_management_handover"),

        "positions": unit8.get("positions", []),

        "long_position_quantity":
            unit8.get("long_position_quantity"),

        "short_position_quantity":
            unit8.get("short_position_quantity"),

        "hedge_policy": unit9.get("hedge_policy", {}),
        "backup_policy": unit9.get("backup_policy", {}),
        "backup_count": unit9.get("backup_count", 5),

        "exposure_cap_percent":
            unit9.get("exposure_cap_percent"),

        "tp1_net_roi_percent":
            unit9.get("tp1_net_roi_percent"),

        "tp2_net_roi_percent":
            unit9.get("tp2_net_roi_percent"),

        "tp_allocation": unit9.get("tp_allocation"),

        "handover_to_unit12": "READY",

        "read_only": True,
        "exchange_write": False,
        "real_cash_execution": False,
        "real_cash_execution_enabled": False
    }

    def finish(status, reason):
        result["status"] = status
        result["reason"] = reason
        result["skip_reason"] = (
            None if status == "READY" else reason
        )

        for label, key in (
            ("MARKET SYMBOL", "market_symbol"),
            ("DEMO ORDER SYMBOL", "demo_order_symbol"),
            ("BOT_MODE", "bot_mode"),
            ("MODE", "active_mode"),
            ("DIRECTION", "direction"),
            ("SIGNAL QUALIFIED", "signal_qualified"),
            ("ORDER PREPARED", "order_prepared"),
            ("QUANTITY", "quantity"),
            ("SELECTED LEVERAGE", "selected_leverage"),
            ("ENTRY MARGIN USDT", "entry_margin_usdt"),
            ("EXCHANGE ORDER UNITS VERIFIED",
             "exchange_order_units_verified"),
            ("EXECUTION READY", "execution_ready"),
            ("STATUS", "status"),
            ("REASON", "reason"),
            ("ORDER SUBMISSION AUTHORIZED",
             "order_submission_authorized")
        ):
            print(
                "UNIT 11 " + label + " =",
                result.get(key),
                flush=True
            )

        print(
            "UNIT 11 EXISTING POSITION MANAGEMENT = "
            "INDEPENDENT",
            flush=True
        )

        print(
            "UNIT 11 HANDOVER TO UNIT 12 = READY",
            flush=True
        )

        print(
            "UNIT 11 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "UNIT 11 REAL CASH EXECUTION = DISABLED",
            flush=True
        )

        print(
            "COMBINED RECONSTRUCTION UNIT 11 RESULT =",
            "FAIL" if status == "ERROR" else "PASS",
            flush=True
        )

        print("=" * 80, flush=True)

        return result

    # ========================================================
    # DEMO-ONLY BOUNDARY
    # ========================================================

    if not symbol:
        return finish(
            "ERROR", "MARKET_SYMBOL_MISSING"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled")
        is not False
    ):
        return finish(
            "ERROR", "DEMO_ONLY_CONFIGURATION_REQUIRED"
        )

    if (
        unit10.get("market_symbol") != symbol
        or unit9.get("market_symbol") != symbol
        or unit8.get("market_symbol") != symbol
        or unit8.get("demo_order_symbol") != symbol
    ):
        return finish(
            "ERROR", "SYMBOL_HANDOVER_MISMATCH"
        )

    # ========================================================
    # BOT_MODE CONTROLS NEW ENTRIES ONLY
    # ========================================================

    if bot_mode != "RUN":
        return finish(
            "PAUSED", "NEW_ENTRIES_PAUSED"
        )

    status10 = str(
        unit10.get("status") or "IDLE"
    ).upper()

    if status10 != "READY":
        return finish(
            "WAITING",
            "UNIT_10_NOT_READY_" + status10
        )

    if (
        unit10.get("trade_plan_ready") is not True
        or unit10.get("execution_ready") is not True
    ):
        return finish(
            "WAITING", "UNIT_10_PLAN_NOT_READY"
        )

    if (
        unit9.get("status") != "READY"
        or unit9.get("trade_plan_ready") is not True
        or unit9.get("execution_ready") is not True
    ):
        return finish(
            "WAITING", "UNIT_9_PLAN_NOT_READY"
        )

    # ========================================================
    # VALIDATE QUALIFIED SIGNAL
    # ========================================================

    plan = unit10.get("trade_plan")

    if not isinstance(plan, dict):
        return finish(
            "WAITING", "TRADE_PLAN_MISSING"
        )

    if plan != unit9.get("trade_plan"):
        return finish(
            "WAITING", "TRADE_PLAN_HANDOVER_MISMATCH"
        )

    mode = str(
        plan.get("active_mode") or "NONE"
    ).upper()

    direction = str(
        plan.get("direction") or "NONE"
    ).upper()

    result["active_mode"] = mode
    result["direction"] = direction

    if mode not in (
        "SCALP", "STRUCTURE", "BREAKOUT"
    ):
        return finish(
            "IDLE", "NO_QUALIFIED_MODE"
        )

    if direction not in ("LONG", "SHORT"):
        return finish(
            "IDLE", "NO_QUALIFIED_DIRECTION"
        )

    if (
        unit9.get("signal_qualified") is not True
        or unit9.get("execution_intent") is not True
        or unit10.get("signal_qualified") is not True
        or unit10.get("execution_intent") is not True
    ):
        return finish(
            "IDLE", "NO_QUALIFIED_ENTRY_INTENT"
        )

    result["signal_qualified"] = True
    result["execution_intent"] = True

    if (
        plan.get("market_symbol") != symbol
        or plan.get("demo_order_symbol") != symbol
        or plan.get("execution_environment") != "DEMO"
        or plan.get("real_cash_execution_enabled")
        is not False
    ):
        return finish(
            "ERROR", "TRADE_PLAN_DEMO_MISMATCH"
        )

    # ========================================================
    # ACCOUNT AND CONTRACT CHECKS
    # ========================================================

    if (
        unit8.get("market_contract_verified") is not True
        or unit8.get("demo_balance_verified") is not True
        or unit8.get("demo_positions_read_verified")
        is not True
        or unit8.get("account_can_trade") is not True
    ):
        return finish(
            "WAITING", "DEMO_ACCOUNT_READ_INCOMPLETE"
        )

    # Flat-position rule is for NEW INITIAL ENTRIES.
    # It does not block hedge, backup or TP management.

    if unit8.get("position_flat_verified") is not True:
        return finish(
            "IDLE", "EXISTING_POSITION_PRESENT"
        )

    contract = unit8.get("contract")
    preview = unit8.get("size_preview")

    if not isinstance(contract, dict):
        return finish(
            "WAITING", "CONTRACT_METADATA_MISSING"
        )

    if not isinstance(preview, dict):
        return finish(
            "WAITING", "SIZE_PREVIEW_MISSING"
        )

    if preview.get("valid") is not True:
        return finish(
            "WAITING", "SIZE_PREVIEW_INVALID"
        )

    # ========================================================
    # ORDER QUANTITY AND MARGIN
    # ========================================================

    quantity = u11_decimal(plan.get("quantity"))
    leverage = u11_decimal(plan.get("leverage"))
    margin = u11_decimal(
        plan.get("entry_margin_usdt")
    )

    minimum = u11_decimal(
        contract.get("minimum_quantity")
    )

    step = u11_decimal(
        contract.get("quantity_step")
    )

    multiplier = u11_decimal(
        contract.get("contract_multiplier")
    )

    available = u11_decimal(
        unit8.get("available_balance")
    )

    mark_price = u11_decimal(
        plan.get("indicative_mark_price")
    )

    values = (
        quantity, leverage, margin,
        minimum, step, multiplier,
        mark_price
    )

    if any(
        number is None or number <= 0
        for number in values
    ):
        return finish(
            "WAITING", "INVALID_CONTRACT_OR_ORDER_SIZE"
        )

    if available is None or available < margin:
        return finish(
            "WAITING", "INSUFFICIENT_DEMO_MARGIN"
        )

    if (
        quantity < minimum
        or quantity % step != 0
        or u11_decimal(preview.get("quantity"))
        != quantity
    ):
        return finish(
            "WAITING", "ORDER_QUANTITY_NOT_COMPLIANT"
        )

    maximum = u11_decimal(
        contract.get("maximum_quantity")
    )

    if maximum is not None and quantity > maximum:
        return finish(
            "WAITING", "ORDER_EXCEEDS_CONTRACT_MAXIMUM"
        )

    expected_notional = (
        quantity * multiplier * mark_price
    )

    expected_margin = expected_notional / leverage

    if expected_notional <= 0 or expected_margin <= 0:
        return finish(
            "WAITING", "INVALID_NOTIONAL"
        )

    preview_margin = u11_decimal(
        preview.get("actual_margin_usdt")
    )

    if (
        preview_margin is None
        or abs(preview_margin - expected_margin)
        > Decimal("0.000001")
    ):
        return finish(
            "WAITING", "MARGIN_PREVIEW_MISMATCH"
        )

    # ========================================================
    # PREPARE DEMO ORDER INTENT
    # ========================================================

    # This is a normalized order intent, not the final
    # WEEX HTTP payload. Unit 12 must map it to the
    # verified demo API request schema.

    order_request = {
        "environment": "DEMO",
        "symbol": symbol,
        "market_symbol": symbol,
        "demo_order_symbol": symbol,

        "intent": "OPEN_INITIAL_POSITION",
        "direction": direction,
        "mode": mode,

        "order_type": "MARKET",
        "margin_mode": "ISOLATED",

        "quantity": u11_decimal_string(quantity),
        "quantity_unit":
            plan.get("quantity_unit"),

        "contract_multiplier":
            u11_decimal_string(multiplier),

        "leverage": u11_decimal_string(leverage),

        "entry_margin_usdt":
            u11_decimal_string(margin),

        "estimated_notional_usdt":
            u11_decimal_string(expected_notional),

        "indicative_mark_price":
            u11_decimal_string(mark_price),

        "contract": contract,

        "stage1_hedge_quantity":
            plan.get("stage1_hedge_quantity"),

        "stage2_remaining_quantity":
            plan.get("stage2_remaining_quantity"),

        "hedge_policy":
            plan.get("hedge_policy", {}),

        "backup_policy":
            plan.get("backup_policy", {}),

        "backup_count":
            plan.get("backup_count", 5),

        "tp1_net_roi_percent":
            plan.get("tp1_net_roi_percent"),

        "tp2_net_roi_percent":
            plan.get("tp2_net_roi_percent"),

        "tp_allocation":
            plan.get("tp_allocation"),

        "requires_fresh_balance": True,
        "requires_fresh_position_read": True,
        "requires_demo_order_response": True,

        "exchange_order_units_verified": (
            preview.get(
                "exchange_order_units_verified"
            ) is True
        ),

        "order_submitted": False,
        "real_cash_execution_enabled": False
    }

    result.update({
        "status": "READY",
        "reason": "DEMO_ORDER_INTENT_PREPARED",

        "trade_plan_ready": True,
        "trade_plan": plan,

        "order_prepared": True,
        "order_payload_created": False,
        "order_request": order_request,

        "quantity": u11_decimal_string(quantity),
        "selected_leverage":
            u11_decimal_string(leverage),

        "entry_margin_usdt":
            u11_decimal_string(margin),

        "exchange_order_units_verified": (
            preview.get(
                "exchange_order_units_verified"
            ) is True
        ),

        "execution_ready": True,

        # Unit 12 owns final demo submission.
        "execution_authorized": False,
        "order_submission_authorized": False,
        "order_submitted": False,

        "read_only": True,
        "exchange_write": False,
        "real_cash_execution": False
    })

    return finish(
        "READY", "DEMO_ORDER_INTENT_PREPARED"
    )


# ============================================================
# UNIT 11 STARTUP EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
    fresh_reconstruction_unit_11(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_10_RESULT,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT
    )
)

FRESH_UNIT_11_OPTIMIZATION_READY = (
    isinstance(
        FRESH_RECONSTRUCTION_UNIT_11_RESULT, dict
    )
    and FRESH_RECONSTRUCTION_UNIT_11_RESULT.get(
        "read_only"
    ) is True
    and FRESH_RECONSTRUCTION_UNIT_11_RESULT.get(
        "exchange_write"
    ) is False
    and FRESH_RECONSTRUCTION_UNIT_11_RESULT.get(
        "status"
    ) in ("READY", "PAUSED", "IDLE", "WAITING")
)

print(
    "UNIT 11 OPTIMIZATION READY =",
    FRESH_UNIT_11_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 11 REPLACEMENT
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 12
# WEEX DEMO SYMBOL-COMPATIBLE ORDER EXECUTION
# UNIT 11 -> UNIT 12 -> UNIT 13
# ZERO INDENTATION
# ============================================================

import os
import re
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.error

from decimal import Decimal, InvalidOperation, ROUND_DOWN


UNIT12_VERSION = "V7_DEMO_SYMBOL_COMPATIBLE"

UNIT12_BASE_URL = "https://api-contract.weex.com"

UNIT12_POSITION_PATH = (
    "/capi/v3/sim/position/allPosition"
)

UNIT12_ORDER_PATH = "/capi/v3/sim/order"

# Prevent repeated attempts within this Python process.
UNIT12_ATTEMPTED_IDS = set()


# ============================================================
# 12.1 HELPERS
# ============================================================

def u12_decimal(value):

    if value is None or isinstance(value, bool):
        return None

    try:
        number = Decimal(str(value))

        if number.is_finite():
            return number

    except (InvalidOperation, TypeError, ValueError):
        pass

    return None


def u12_text(value):

    return format(value, "f")


def u12_symbol(value):

    symbol = str(value or "").strip().upper()

    if not re.fullmatch(r"[A-Z0-9]{3,30}", symbol):
        return None

    return symbol


def u12_demo_symbol(market_symbol):

    # Explicit Render override takes precedence.
    configured = u12_symbol(
        os.getenv("WEEX_DEMO_ORDER_SYMBOL")
    )

    if configured:
        return configured

    # Known candidate from the previous demo configuration.
    # This mapping must still be confirmed by the
    # actual WEEX demo order response.
    known_candidates = {
        "BTCUSDT": "BTCSUSDT"
    }

    return known_candidates.get(market_symbol)


def u12_rows(response):

    if isinstance(response, list):
        return response

    if not isinstance(response, dict):
        return None

    data = response.get("data")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "list",
            "rows",
            "positions",
            "items"
        ):
            if isinstance(data.get(key), list):
                return data[key]

    return None


def u12_client_id(symbol, direction, candle_id):

    source = (
        symbol + "|"
        + direction + "|"
        + str(candle_id)
    )

    digest = hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()[:24]

    return "FR12" + digest


# ============================================================
# 12.2 AUTHENTICATED DEMO REQUEST
# ============================================================

def u12_request(method, path, payload=None):

    allowed = {
        ("GET", UNIT12_POSITION_PATH),
        ("POST", UNIT12_ORDER_PATH)
    }

    if (method, path) not in allowed:
        raise RuntimeError(
            "NON_DEMO_ENDPOINT_BLOCKED"
        )

    if method == "POST" and not isinstance(
        payload, dict
    ):
        raise RuntimeError("INVALID_POST_PAYLOAD")

    if method == "GET" and payload is not None:
        raise RuntimeError("INVALID_GET_PAYLOAD")

    key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "WEEX_CREDENTIALS_MISSING"
        )

    body = (
        json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False
        )
        if payload is not None
        else ""
    )

    timestamp = str(int(time.time() * 1000))

    message = timestamp + method + path + body

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        UNIT12_BASE_URL + path,
        data=(
            body.encode("utf-8")
            if method == "POST"
            else None
        ),
        method=method,
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

    except urllib.error.HTTPError as exc:

        http_status = exc.code

        raw = exc.read().decode(
            "utf-8",
            errors="replace"
        )

    try:
        data = json.loads(raw)
    except ValueError:
        data = {
            "raw_response": raw[:500]
        }

    return http_status, data


# ============================================================
# 12.3 POSITION VERIFICATION
# ============================================================

def u12_position_check(symbol):

    http_status, response = u12_request(
        "GET",
        UNIT12_POSITION_PATH
    )

    if not 200 <= http_status < 300:
        return False, "POSITION_HTTP_ERROR"

    if isinstance(response, dict):

        code = response.get("code")

        if code not in (None, 0, "0", "00000"):
            return False, "POSITION_API_REJECTED"

    rows = u12_rows(response)

    if rows is None:
        return False, "POSITION_FORMAT_UNVERIFIED"

    for position in rows:

        if not isinstance(position, dict):
            return False, "INVALID_POSITION_RECORD"

        position_symbol = u12_symbol(
            position.get("symbol")
        )

        if position_symbol != symbol:
            continue

        raw_size = None

        for key in (
            "size",
            "total",
            "holdVol",
            "positionAmt"
        ):
            if position.get(key) is not None:
                raw_size = position.get(key)
                break

        size = u12_decimal(raw_size)

        if size is None:
            return False, "POSITION_SIZE_UNVERIFIED"

        if abs(size) > 0:
            return False, "ACTIVE_POSITION_EXISTS"

    return True, "DEMO_POSITION_FLAT"


# ============================================================
# 12.4 ORDER QUANTITY CONVERSION
# ============================================================

def u12_order_quantity(instruction, contract):

    quantity = u12_decimal(
        instruction.get("quantity")
    )

    multiplier = u12_decimal(
        instruction.get("contract_multiplier")
        or contract.get("contract_multiplier")
    )

    if quantity is None or quantity <= 0:
        return None, "INVALID_INTERNAL_QUANTITY"

    if multiplier is None or multiplier <= 0:
        return None, "INVALID_CONTRACT_MULTIPLIER"

    source_unit = str(
        instruction.get("quantity_unit") or ""
    ).upper()

    if source_unit != "EXCHANGE_CONTRACT_UNITS":
        return None, "SOURCE_QUANTITY_UNIT_UNVERIFIED"

    # Explicitly confirm the demo endpoint's quantity
    # representation before any order submission.
    target_unit = str(
        os.getenv(
            "WEEX_DEMO_ORDER_QUANTITY_UNIT",
            "UNVERIFIED"
        )
    ).strip().upper()

    if target_unit == "BASE_ASSET":

        calculated = quantity * multiplier

    elif target_unit == "CONTRACT_UNITS":

        calculated = quantity

    else:

        return None, "DEMO_ORDER_QUANTITY_UNIT_UNVERIFIED"

    # The step and minimum must describe the actual
    # order endpoint's quantity representation.
    step = u12_decimal(
        os.getenv("WEEX_DEMO_ORDER_QTY_STEP")
    )

    minimum = u12_decimal(
        os.getenv("WEEX_DEMO_ORDER_MIN_QTY")
    )

    if (
        step is None
        or minimum is None
        or step <= 0
        or minimum <= 0
    ):
        return None, "DEMO_QUANTITY_RULES_UNVERIFIED"

    adjusted = (
        (calculated / step).to_integral_value(
            rounding=ROUND_DOWN
        ) * step
    )

    if adjusted < minimum:
        return None, "DEMO_QUANTITY_BELOW_MINIMUM"

    return u12_text(adjusted), "QUANTITY_READY"


# ============================================================
# 12.5 MAIN DEMO EXECUTION
# ============================================================

def fresh_reconstruction_unit_12(
    config,
    unit11,
    unit8
):

    config = config if isinstance(config, dict) else {}
    unit11 = unit11 if isinstance(unit11, dict) else {}
    unit8 = unit8 if isinstance(unit8, dict) else {}

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        exchange = {}

    market_symbol = u12_symbol(
        exchange.get("market_symbol")
        or config.get("market_symbol")
    )

    demo_symbol = u12_demo_symbol(market_symbol)

    bot_mode = str(
        os.getenv(
            "BOT_MODE",
            config.get("bot_mode", "PAUSE")
        )
    ).strip().upper()

    result = {
        "unit": 12,
        "version": UNIT12_VERSION,

        "market_symbol": market_symbol,
        "demo_order_symbol": demo_symbol,

        "bot_mode": bot_mode,

        "status": "IDLE",
        "reason": "NOT_EVALUATED",

        "order_id": None,
        "client_order_id": None,

        "order_request": None,
        "order_payload": None,
        "order_response": None,

        "order_submitted": False,
        "order_accepted": False,
        "fill_verified": False,

        "exchange_write": False,
        "real_cash_execution": False,

        "existing_position_management_enabled": True,
        "existing_position_management_independent": True
    }

    print("=" * 80, flush=True)
    print(
        "COMBINED RECONSTRUCTION UNIT 12 START",
        flush=True
    )

    print(
        "UNIT 12 VERSION =",
        UNIT12_VERSION,
        flush=True
    )

    print(
        "UNIT 12 MARKET SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 12 DEMO SYMBOL =",
        demo_symbol,
        flush=True
    )

    print(
        "UNIT 12 BOT_MODE =",
        bot_mode,
        flush=True
    )

    def finish(status, reason):

        result["status"] = status
        result["reason"] = reason
        result["skip_reason"] = reason

        print(
            "UNIT 12 STATUS =",
            status,
            flush=True
        )

        print(
            "UNIT 12 REASON =",
            reason,
            flush=True
        )

        print(
            "UNIT 12 ORDER ID =",
            result["order_id"],
            flush=True
        )

        print(
            "UNIT 12 EXCHANGE WRITE =",
            result["exchange_write"],
            flush=True
        )

        print(
            "UNIT 12 REAL CASH EXECUTION = DISABLED",
            flush=True
        )

        print("=" * 80, flush=True)

        return result

    # --------------------------------------------------------
    # DEMO-ONLY BOUNDARY
    # --------------------------------------------------------

    if (
        config.get("execution_environment") != "DEMO"
        or config.get(
            "real_cash_execution_enabled"
        ) is not False
    ):
        return finish(
            "BLOCKED",
            "DEMO_ONLY_CONFIGURATION_REQUIRED"
        )

    if not market_symbol or not demo_symbol:
        return finish(
            "BLOCKED",
            "DEMO_SYMBOL_MAPPING_UNAVAILABLE"
        )

    if bot_mode not in ("RUN", "PAUSE"):
        return finish(
            "BLOCKED",
            "INVALID_BOT_MODE"
        )

    # BOT_MODE controls initial entries only.
    # It does not disable Units 13-14 management.
    if bot_mode == "PAUSE":
        return finish(
            "PAUSED",
            "NEW_ENTRIES_PAUSED"
        )

    # --------------------------------------------------------
    # UNIT 11 HANDOVER
    # --------------------------------------------------------

    if (
        unit11.get("status") != "READY"
        or unit11.get("order_prepared") is not True
        or unit11.get("execution_ready") is not True
    ):
        return finish(
            "IDLE",
            "UNIT11_NOT_READY"
        )

    instruction = unit11.get("order_request")

    if not isinstance(instruction, dict):
        return finish(
            "BLOCKED",
            "UNIT11_ORDER_REQUEST_MISSING"
        )

    if instruction.get("environment") != "DEMO":
        return finish(
            "BLOCKED",
            "UNIT11_NON_DEMO_REQUEST"
        )

    if instruction.get("intent") != (
        "OPEN_INITIAL_POSITION"
    ):
        return finish(
            "BLOCKED",
            "INVALID_ORDER_INTENT"
        )

    if instruction.get("order_type") != "MARKET":
        return finish(
            "BLOCKED",
            "UNSUPPORTED_ORDER_TYPE"
        )

    if u12_symbol(
        instruction.get("market_symbol")
    ) != market_symbol:
        return finish(
            "BLOCKED",
            "MARKET_SYMBOL_MISMATCH"
        )

    direction = str(
        instruction.get("direction") or ""
    ).upper()

    if direction not in ("LONG", "SHORT"):
        return finish(
            "BLOCKED",
            "INVALID_DIRECTION"
        )

    if (
        instruction.get("real_cash_execution_enabled")
        is True
    ):
        return finish(
            "BLOCKED",
            "REAL_CASH_REQUEST_BLOCKED"
        )

    # --------------------------------------------------------
    # CONTRACT AND QUANTITY
    # --------------------------------------------------------

    contract = unit8.get("contract")

    if not isinstance(contract, dict):
        return finish(
            "BLOCKED",
            "CONTRACT_METADATA_MISSING"
        )

    if contract.get("verified") is not True:
        return finish(
            "BLOCKED",
            "MARKET_CONTRACT_UNVERIFIED"
        )

    if u12_symbol(
        contract.get("symbol")
    ) != market_symbol:
        return finish(
            "BLOCKED",
            "CONTRACT_SYMBOL_MISMATCH"
        )

    quantity, quantity_reason = (
        u12_order_quantity(
            instruction,
            contract
        )
    )

    print(
        "UNIT 12 QUANTITY STATUS =",
        quantity_reason,
        flush=True
    )

    if quantity is None:
        return finish(
            "BLOCKED",
            quantity_reason
        )

    print(
        "UNIT 12 DEMO ORDER QUANTITY =",
        quantity,
        flush=True
    )

    # --------------------------------------------------------
    # CANDLE-BASED CLIENT ID
    # --------------------------------------------------------

    snapshot = globals().get(
        "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT",
        {}
    )

    if not isinstance(snapshot, dict):
        snapshot = {}

    candle_id = snapshot.get(
        "latest_close_time_ms"
    )

    if candle_id is None:
        return finish(
            "BLOCKED",
            "SIGNAL_CANDLE_ID_MISSING"
        )

    client_id = u12_client_id(
        market_symbol,
        direction,
        candle_id
    )

    result["client_order_id"] = client_id

    if client_id in UNIT12_ATTEMPTED_IDS:
        return finish(
            "ORDER_UNCERTAIN",
            "DUPLICATE_ATTEMPT_BLOCKED"
        )

    payload = {
        "symbol": demo_symbol,

        "side": (
            "BUY"
            if direction == "LONG"
            else "SELL"
        ),

        "positionSide": direction,

        "type": "MARKET",

        "quantity": quantity,

        "newClientOrderId": client_id
    }

    result["order_request"] = dict(instruction)
    result["order_payload"] = dict(payload)

    print(
        "UNIT 12 ORDER PAYLOAD =",
        payload,
        flush=True
    )

    # --------------------------------------------------------
    # EXPLICIT ORDER AUTHORIZATION
    # --------------------------------------------------------

    # This additional control is deliberately separate
    # from BOT_MODE. It prevents a test order from being
    # sent automatically when Render restarts.
    #
    # It is not a substitute for durable idempotency.

    submission_enabled = str(
        os.getenv(
            "WEEX_DEMO_ORDER_SUBMISSION",
            "DISABLED"
        )
    ).strip().upper()

    if submission_enabled != "ENABLED":
        return finish(
            "PREPARED",
            "DEMO_SUBMISSION_NOT_ARMED"
        )

    # --------------------------------------------------------
    # FRESH DEMO POSITION CHECK
    # --------------------------------------------------------

    try:

        flat, position_reason = (
            u12_position_check(demo_symbol)
        )

    except Exception as exc:

        print(
            "UNIT 12 POSITION ERROR =",
            type(exc).__name__,
            str(exc)[:200],
            flush=True
        )

        return finish(
            "POSITION_CHECK_FAILED",
            "POSITION_REQUEST_FAILED"
        )

    print(
        "UNIT 12 POSITION CHECK =",
        position_reason,
        flush=True
    )

    if not flat:
        return finish(
            "BLOCKED",
            position_reason
        )

    # --------------------------------------------------------
    # DEMO ORDER SUBMISSION
    # --------------------------------------------------------

    # This in-memory guard covers only the current
    # process. For unattended trading, reconcile
    # persisted order attempts with exchange history
    # before enabling automatic retries.

    UNIT12_ATTEMPTED_IDS.add(client_id)

    result["exchange_write"] = True

    print(
        "UNIT 12 SENDING ACTUAL WEEX DEMO ORDER",
        flush=True
    )

    try:

        http_status, response = u12_request(
            "POST",
            UNIT12_ORDER_PATH,
            payload
        )

    except Exception as exc:

        print(
            "UNIT 12 ORDER ERROR =",
            type(exc).__name__,
            str(exc)[:200],
            flush=True
        )

        return finish(
            "ORDER_UNCERTAIN",
            "ORDER_REQUEST_EXCEPTION_RECONCILE_FIRST"
        )

    result["order_response"] = response

    print(
        "UNIT 12 ORDER HTTP STATUS =",
        http_status,
        flush=True
    )

    print(
        "UNIT 12 EXCHANGE RESPONSE =",
        response,
        flush=True
    )

    if not 200 <= http_status < 300:
        return finish(
            "DEMO_REJECTED",
            "WEEX_ORDER_HTTP_REJECTED"
        )

    if not isinstance(response, dict):
        return finish(
            "ORDER_UNCERTAIN",
            "INVALID_ORDER_RESPONSE"
        )

    code = response.get("code")

    if code not in (None, 0, "0", "00000"):
        return finish(
            "DEMO_REJECTED",
            "WEEX_ORDER_REJECTED"
        )

    if response.get("success") is False:
        return finish(
            "DEMO_REJECTED",
            "WEEX_ORDER_NOT_SUCCESSFUL"
        )

    order_data = response.get("data")

    if not isinstance(order_data, dict):
        order_data = {}

    order_id = (
        response.get("orderId")
        or order_data.get("orderId")
        or order_data.get("order_id")
    )

    if not order_id:
        return finish(
            "ORDER_UNCERTAIN",
            "ORDER_ID_NOT_CONFIRMED"
        )

    result["order_id"] = str(order_id)

    result["order_submitted"] = True
    result["order_accepted"] = True

    # Acceptance does not prove a fill.
    # Units 13-14 must read the resulting
    # exchange position before managing it.

    return finish(
        "DEMO_SUBMITTED",
        "WEEX_DEMO_ORDER_ACCEPTED_FILL_PENDING"
    )


# ============================================================
# 12.6 STARTUP EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_reconstruction_unit_12(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT
    )
)

FRESH_UNIT_12_OPTIMIZATION_READY = (
    FRESH_RECONSTRUCTION_UNIT_12_RESULT.get(
        "status"
    ) in (
        "IDLE",
        "PAUSED",
        "PREPARED",
        "DEMO_SUBMITTED"
    )
)

print(
    "UNIT 12 OPTIMIZATION READY =",
    FRESH_UNIT_12_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 12
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 13 - RESTORED 17248 TP ENGINE
# WEEX DEMO ONLY - TP1 / TP2 EXECUTION
# ZERO INDENTATION
# ============================================================

import os
import time
import hashlib
from decimal import Decimal, ROUND_DOWN, ROUND_UP

UNIT13_RESTORED_VERSION = "17248_TP_EXECUTION_RESTORED"


def u13_D(value, name="NUMBER", zero=False):
    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "UNIT13_INVALID_" + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError("UNIT13_NONFINITE_" + name)

    if number < 0 or (number == 0 and not zero):
        raise RuntimeError("UNIT13_RANGE_" + name)

    return number


def u13_floor(value, step):
    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    ) * step


def u13_ceil(value, step):
    return (
        value / step
    ).to_integral_value(
        rounding=ROUND_UP
    ) * step


def u13_position():
    status, response = u12_request(
        "GET", UNIT12_POSITION_PATH
    )

    if status != 200:
        raise RuntimeError(
            "UNIT13_POSITION_HTTP_" + str(status)
        )

    rows = u12_rows(response)

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT13_POSITION_RESPONSE_INVALID"
        )

    return rows


def u13_client_id(position_id, action, closed):
    raw = (
        str(position_id) + "|"
        + str(action) + "|"
        + str(closed)
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:24]

    return "FR13" + digest


def u13_targets(entry, leverage, side, strategy, price_step):
    tp1_roi = u13_D(
        strategy["tp1_net_roi_percent"],
        "TP1_ROI"
    )
    tp2_roi = u13_D(
        strategy["tp2_net_roi_percent"],
        "TP2_ROI"
    )

    fee_rate = u13_D(
        strategy.get("fee_estimate_taker_rate", 0.0008),
        "FEE_RATE",
        True
    )

    slippage = u13_D(
        strategy.get("estimated_slippage_rate", 0),
        "SLIPPAGE",
        True
    )

    funding = u13_D(
        strategy.get("estimated_funding_rate", 0),
        "FUNDING",
        True
    )

    cost_rate = (
        fee_rate * 2
        + slippage
        + funding
    )

    def price_for_roi(roi):
        required_move = (
            roi / (Decimal("100") * leverage)
            + cost_rate
        )

        if side == "LONG":
            return u13_ceil(
                entry * (1 + required_move),
                price_step
            )

        return u13_floor(
            entry * (1 - required_move),
            price_step
        )

    return (
        price_for_roi(tp1_roi),
        price_for_roi(tp2_roi)
    )


def fresh_reconstruction_unit_13_restored():
    config = FRESH_RECONSTRUCTION_CONFIG
    exchange = config["exchange"]
    strategy = config["strategy"]

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled") is not False
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
    ):
        raise RuntimeError(
            "UNIT13_DEMO_BOUNDARY_INVALID"
        )

    demo_symbol = str(
        exchange["demo_order_symbol"]
    ).upper()

    result = {
        "version": UNIT13_RESTORED_VERSION,
        "status": "STARTED",
        "position_exists": False,
        "tp_execution_attempted": False,
        "tp_execution_completed": False,
        "exchange_write": False,
        "tp3_armed": False,
        "hedge_execution": False,
        "backup_execution": False
    }

    print("=" * 80, flush=True)
    print(
        "UNIT 13 RESTORED EXECUTION START",
        flush=True
    )
    print(
        "UNIT 13 MANAGEMENT INDEPENDENT OF BOT_MODE = True",
        flush=True
    )

    rows = u13_position()

    active = [
        row for row in rows
        if isinstance(row, dict)
        and str(row.get("symbol", "")).upper()
            == demo_symbol
        and u13_D(
            row.get("size", 0),
            "POSITION_SIZE",
            True
        ) > 0
    ]

    if not active:
        result["status"] = "IDLE_NO_POSITION"
        print(
            "UNIT 13 STATUS = IDLE_NO_POSITION",
            flush=True
        )
        return result

    if len(active) != 1:
        raise RuntimeError(
            "UNIT13_MULTIPLE_ACTIVE_POSITIONS"
        )

    p = active[0]

    side = str(p.get("side", "")).upper()

    if side not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT13_POSITION_SIDE_INVALID"
        )

    size = u13_D(p["size"], "SIZE")
    leverage = u13_D(p["leverage"], "LEVERAGE")

    open_value = u13_D(
        p["openValue"], "OPEN_VALUE"
    )

    entry = open_value / size

    cum_open = u13_D(
        p["cumOpenSize"], "CUM_OPEN"
    )
    cum_close = u13_D(
        p["cumCloseSize"], "CUM_CLOSE", True
    )

    if cum_close > cum_open:
        raise RuntimeError(
            "UNIT13_CUMULATIVE_POSITION_INVALID"
        )

    unit8 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    if not isinstance(unit8, dict):
        raise RuntimeError(
            "UNIT13_UNIT8_CONTRACT_MISSING"
        )

    contract = unit8.get("contract", {})

    step = u13_D(
        contract.get("quantity_step"),
        "QUANTITY_STEP"
    )

    minimum = u13_D(
        contract.get("minimum_quantity"),
        "MINIMUM_QUANTITY"
    )

    price_step = u13_D(
        contract.get("price_step")
        or contract.get("price_resolution"),
        "PRICE_STEP"
    )

    # Position sizes and order quantities must share
    # the same units before a closing order is submitted.
    # Do not substitute Unit 8's entry contract count.
    if u13_floor(size, step) != size:
        raise RuntimeError(
            "UNIT13_POSITION_QUANTITY_STEP_MISMATCH"
        )

    q1 = u13_floor(
        cum_open * Decimal("0.10"), step
    )

    q2 = u13_floor(
        cum_open * Decimal("0.20"), step
    )

    q3 = cum_open - q1 - q2

    tp1, tp2 = u13_targets(
        entry,
        leverage,
        side,
        strategy,
        price_step
    )

    market = fresh_reconstruction_unit_3()
    mark = u13_D(market["price"], "MARK")

    # Zero-sized allocations are deferred, not filled.
    tp1_deferred = q1 < minimum
    tp2_deferred = q2 < minimum

    done1 = (
        not tp1_deferred
        and cum_close >= q1
    )

    done2 = (
        not tp2_deferred
        and done1
        and cum_close >= q1 + q2
    )

    print(
        "UNIT 13 TP1 DEFERRED =",
        tp1_deferred,
        flush=True
    )
    print(
        "UNIT 13 TP2 DEFERRED =",
        tp2_deferred,
        flush=True
    )


    reached1 = (
        mark >= tp1 if side == "LONG"
        else mark <= tp1
    )

    reached2 = (
        mark >= tp2 if side == "LONG"
        else mark <= tp2
    )

    action = "NONE"
    close_qty = Decimal("0")

    if reached2 and not done2:
        action = "TP2"
        close_qty = q1 + q2 - cum_close

    elif reached1 and not done1:
        action = "TP1"
        close_qty = q1 - cum_close

    close_qty = u13_floor(
        min(close_qty, size),
        step
    )

    result.update({
        "position_exists": True,
        "position_id": str(p.get("id")),
        "position_side": side,
        "position_size": str(size),
        "entry_price": str(entry),
        "mark_price": str(mark),
        "tp1_target": str(tp1),
        "tp2_target": str(tp2),
        "tp1_quantity": str(q1),
        "tp2_quantity": str(q2),
        "tp3_quantity": str(q3),
        "tp1_completed": done1,
        "tp2_completed": done2,
        "tp_action": action,
        "tp3_armed": bool(
            done1 and done2 and size > 0
        )
    })

    print(
        "UNIT 13 POSITION =",
        demo_symbol, side, size,
        flush=True
    )
    print(
        "UNIT 13 TP TARGETS =",
        tp1, tp2,
        flush=True
    )
    print(
        "UNIT 13 TP ACTION =",
        action,
        flush=True
    )

    if action == "NONE" or close_qty < minimum:
        result["status"] = "MONITORING"
        return result

    position_id = str(p.get("id") or "")

    if not position_id:
        raise RuntimeError(
            "UNIT13_POSITION_ID_MISSING"
        )

    client_id = u13_client_id(
        position_id,
        action,
        cum_close
    )

    # A deterministic ID protects retries within
    # this process. Exchange-side order reconciliation
    # is still required after uncertain submissions.
    guard = globals().setdefault(
        "_UNIT13_RESTORED_ATTEMPTS",
        set()
    )

    if client_id in guard:
        result["status"] = (
            "PREVIOUS_ATTEMPT_UNRESOLVED"
        )
        return result

    guard.add(client_id)

    payload = {
        "symbol": demo_symbol,
        "side": (
            "SELL" if side == "LONG"
            else "BUY"
        ),
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(close_qty, "f"),
        "newClientOrderId": client_id
    }

    result["tp_execution_attempted"] = True

    print(
        "UNIT 13 SUBMITTING DEMO TP =",
        action,
        payload["quantity"],
        flush=True
    )

    status, response = u12_request(
        "POST",
        UNIT12_ORDER_PATH,
        payload
    )

    result["exchange_write"] = True

    if status != 200:
        result["status"] = (
            "TP_SUBMISSION_NOT_CONFIRMED"
        )
        result["http_status"] = status
        result["exchange_response"] = response
        return result

    if not isinstance(response, dict):
        raise RuntimeError(
            "UNIT13_TP_RESPONSE_INVALID"
        )

    order_id = (
        response.get("orderId")
        or (
            response.get("data", {}).get("orderId")
            if isinstance(response.get("data"), dict)
            else None
        )
    )

    if not order_id:
        result["status"] = (
            "TP_ORDER_CONFIRMATION_PENDING"
        )
        result["exchange_response"] = response
        return result

    result.update({
        "status": "TP_ORDER_ACCEPTED",
        "tp_order_id": str(order_id),
        "tp_close_quantity": str(close_qty),
        "tp_execution_completed": False
    })

    print(
        "UNIT 13 TP ORDER ACCEPTED =",
        order_id,
        flush=True
    )

    return result


FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_reconstruction_unit_13_restored()
)

FRESH_UNIT_13_OPTIMIZATION_READY = True

print(
    "UNIT 13 FINAL STATUS =",
    FRESH_RECONSTRUCTION_UNIT_13_RESULT["status"],
    flush=True
)

# ============================================================
# END COMPLETE UNIT 13 RESTORED TP ENGINE
# ============================================================



# ============================================================
# START UNIT 14 V4
# PART 1 - ORIGINAL 17248 HISTORY AND RECONCILIATION
# ZERO INDENTATION
# DEMO GET REQUESTS ONLY
# ============================================================

import os
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.parse
import urllib.error

from decimal import Decimal, InvalidOperation

UNIT14_V4_VERSION = "V4_17248_HISTORY_RESTORED"
UNIT14_V4_BASE = "https://api-contract.weex.com"
UNIT14_V4_HISTORY = "/capi/v3/sim/order/history"
UNIT14_V4_POSITION = "/capi/v3/sim/position/allPosition"


def unit_14_v4_D(value, name="VALUE", zero=False):
    if value is None or isinstance(value, bool):
        raise RuntimeError("UNIT 14 MISSING " + name)

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 14 INVALID " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 14 NONFINITE " + name
        )

    if number < 0 or (number == 0 and not zero):
        raise RuntimeError(
            "UNIT 14 NONPOSITIVE " + name
        )

    return number


def unit_14_v4_demo_symbol():

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 14 CONFIG MISSING"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 14 DEMO ENVIRONMENT REQUIRED"
        )

    if config.get("real_cash_execution_enabled") is not False:
        raise RuntimeError(
            "UNIT 14 REAL CASH EXECUTION BLOCKED"
        )

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 14 EXCHANGE CONFIG INVALID"
        )

    symbol = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if not symbol:
        raise RuntimeError(
            "UNIT 14 DEMO SYMBOL MISSING"
        )

    return symbol


# ============================================================
# ORIGINAL 17248 SIGNED REQUEST PRINCIPLE
# ALLOWED: DEMO POSITION AND ORDER HISTORY GET
# ============================================================

def unit_14_v4_signed_get(path, query=""):

    if path not in (
        UNIT14_V4_HISTORY,
        UNIT14_V4_POSITION,
    ):
        raise RuntimeError(
            "UNIT 14 NON-DEMO ENDPOINT BLOCKED"
        )

    key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 14 DEMO CREDENTIALS MISSING"
        )

    timestamp = str(int(time.time() * 1000))

    prehash = timestamp + "GET" + path

    if query:
        prehash += "?" + query

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    url = UNIT14_V4_BASE + path

    if query:
        url += "?" + query

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            status = response.getcode()
            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "UNIT 14 WEEX HTTP " + str(exc.code)
        ) from exc

    if not 200 <= status < 300:
        raise RuntimeError(
            "UNIT 14 HTTP STATUS " + str(status)
        )

    try:
        result = json.loads(raw)
    except ValueError as exc:
        raise RuntimeError(
            "UNIT 14 INVALID RESPONSE JSON"
        ) from exc

    # The 17248 implementation expects a list.
    # Do not silently turn an API error into
    # an empty order history.
    if not isinstance(result, list):
        raise RuntimeError(
            "UNIT 14 UNRECOGNIZED RESPONSE FORMAT"
        )

    return result


# ============================================================
# RESTORED ORDER HISTORY WITH PAGINATION
# ============================================================

def unit_14_v4_history():

    symbol = unit_14_v4_demo_symbol()

    orders = []
    page_limit = 20
    page_size = 1000

    for page in range(page_limit):

        query = urllib.parse.urlencode({
            "symbol": symbol,
            "limit": page_size,
            "page": page,
        })

        batch = unit_14_v4_signed_get(
            UNIT14_V4_HISTORY,
            query
        )

        if not all(
            isinstance(item, dict)
            for item in batch
        ):
            raise RuntimeError(
                "UNIT 14 MALFORMED ORDER HISTORY"
            )

        orders.extend(batch)

        if len(batch) < page_size:

            print(
                "UNIT 14 ORDER HISTORY COMPLETE = True",
                flush=True
            )
            print(
                "UNIT 14 ORDER HISTORY RECORDS =",
                len(orders),
                flush=True
            )

            return orders

    raise RuntimeError(
        "UNIT 14 HISTORY PAGINATION INCOMPLETE"
    )


# ============================================================
# RESTORED ORIGINAL BACKUP ORDER ID CONVENTION
# ============================================================

def unit_14_v4_backup_id(stage, trade_key):

    if stage not in range(1, 6):
        raise RuntimeError(
            "UNIT 14 INVALID BACKUP STAGE"
        )

    if not trade_key:
        raise RuntimeError(
            "UNIT 14 TRADE KEY MISSING"
        )

    return (
        "FR-B"
        + str(stage)
        + "-"
        + str(trade_key)
    )[:36]


def unit_14_v4_trade_key(position):

    if not isinstance(position, dict):
        raise RuntimeError(
            "UNIT 14 POSITION INVALID"
        )

    created = str(
        position.get("createdTime") or ""
    )

    if created.isdigit():
        return created[-12:]

    position_id = str(
        position.get("id") or ""
    )

    if position_id:
        return position_id[-12:]

    raise RuntimeError(
        "UNIT 14 POSITION IDENTITY MISSING"
    )


# ============================================================
# RESTORED B1-B5 ORDER RECONCILIATION
# ============================================================

def unit_14_v4_reconcile(history, trade_key):

    if not isinstance(history, list):
        raise RuntimeError(
            "UNIT 14 HISTORY INVALID"
        )

    existing = set()
    filled = set()
    order_ids = {}

    for stage in range(1, 6):

        client_id = unit_14_v4_backup_id(
            stage,
            trade_key
        )

        matching = [
            order
            for order in history
            if isinstance(order, dict)
            and str(
                order.get("clientOrderId") or ""
            ) == client_id
        ]

        for order in matching:

            status = str(
                order.get("status") or ""
            ).upper()

            executed = unit_14_v4_D(
                order.get("executedQty", 0),
                "EXECUTED QUANTITY",
                True
            )

            order_id = (
                order.get("orderId")
                or order.get("id")
            )

            if order_id is not None:
                order_ids[stage] = str(order_id)

            if status not in (
                "CANCELED",
                "CANCELLED",
                "REJECTED",
                "EXPIRED",
            ):
                existing.add(stage)

            if status == "FILLED" and executed > 0:
                filled.add(stage)

            if executed > 0 and status != "FILLED":
                existing.add(stage)

    completed = 0

    for stage in range(1, 6):
        if stage in filled:
            completed = stage
        else:
            break

    if any(
        stage > completed + 1
        for stage in filled
    ):
        raise RuntimeError(
            "UNIT 14 NONSEQUENTIAL BACKUP FILLS"
        )

    return {
        "completed_backup_stage": completed,
        "existing_backup_stages": sorted(existing),
        "filled_backup_stages": sorted(filled),
        "backup_order_ids": order_ids,
    }


# ============================================================
# INITIAL HISTORY RESTORATION CHECK
# ============================================================

def unit_14_v4_history_check():

    result = {
        "version": UNIT14_V4_VERSION,
        "status": "STARTED",
        "history_verified": False,
        "order_count": 0,
        "orders_with_exchange_ids": 0,
        "position_read_verified": False,
        "raw_position_count": None,
        "exchange_write": False,
        "errors": [],
    }

    try:

        history = unit_14_v4_history()

        result["history_verified"] = True
        result["order_count"] = len(history)

        result["orders_with_exchange_ids"] = sum(
            1
            for order in history
            if order.get("orderId") is not None
            or order.get("id") is not None
        )

        positions = unit_14_v4_signed_get(
            UNIT14_V4_POSITION
        )

        result["position_read_verified"] = True
        result["raw_position_count"] = len(positions)

        result["status"] = "READ_COMPLETE"

    except Exception as exc:

        result["status"] = "READ_FAILED"
        result["errors"].append(
            type(exc).__name__ + ": " + str(exc)
        )

    print("=" * 80, flush=True)
    print(
        "UNIT 14 VERSION =",
        result["version"],
        flush=True
    )
    print(
        "UNIT 14 STATUS =",
        result["status"],
        flush=True
    )
    print(
        "UNIT 14 HISTORY VERIFIED =",
        result["history_verified"],
        flush=True
    )
    print(
        "UNIT 14 HISTORY ORDER COUNT =",
        result["order_count"],
        flush=True
    )
    print(
        "UNIT 14 EXCHANGE ORDER IDS FOUND =",
        result["orders_with_exchange_ids"],
        flush=True
    )
    print(
        "UNIT 14 POSITION READ VERIFIED =",
        result["position_read_verified"],
        flush=True
    )
    print(
        "UNIT 14 RAW POSITION COUNT =",
        result["raw_position_count"],
        flush=True
    )
    print(
        "UNIT 14 ERRORS =",
        result["errors"],
        flush=True
    )
    print(
        "UNIT 14 EXCHANGE WRITE = NONE",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    unit_14_v4_history_check()
)

# ============================================================
# END UNIT 14 V4 - HISTORY RESTORATION
# ============================================================


