
# ============================================================
# UNIVERSAL WEEX 15-UNIT HYBRID TRADING BOT
# UNIT 1 V1 - COMPLETE RUNTIME FOUNDATION
#
# ADAPTED FROM:
# - 17248-LINE WORKING MODEL
# - 16414-LINE REVERSIBLE ATR HEDGE MODEL
#
# UNIVERSAL COIN SELECTION: UNIT 2
# UNIFIED ENTRY: SCALP + STRUCTURE + BREAKOUT
# ONE ATR HEDGE / RECOVERY CYCLE
# B1-B5 FOLLOWING FAILED FIRST RECOVERY
#
# TP1 = 20% NET ROI
# TP2 = 40% NET ROI
# TP3 = DYNAMIC TRAILING NET ROI
#
# TP1 SECURED PROFIT PROTECTED SEPARATELY
# POST-TP1 DYNAMIC BREAK-EVEN
# POST-TP2 DYNAMIC TRAILING
#
# WEEX DEMO ONLY
# REAL CASH EXECUTION DISABLED
# ZERO INDENTATION DEMARCATION
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

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_DOWN,
    ROUND_UP,
)

from datetime import (
    datetime,
    timezone,
)


# ============================================================
# SHARED LOGGER
# PRESERVE ORIGINAL log(message) INTERFACE
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
# UNIT 1 - UNIVERSAL RUNTIME FOUNDATION
# ============================================================

def fresh_reconstruction_unit_1():

    print(
        "=" * 80,
        flush=True,
    )

    log(
        "UNIVERSAL WEEX UNIT 1 V1 START"
    )

    print(
        "-" * 80,
        flush=True,
    )

    # ========================================================
    # 1. VERIFY STANDARD LIBRARY
    # ========================================================

    required_modules = {

        "OS": os,
        "JSON": json,
        "TIME": time,
        "MATH": math,
        "HMAC": hmac,
        "HASHLIB": hashlib,
        "BASE64": base64,
        "THREADING": threading,
        "URLLIB": urllib.request,
        "DECIMAL": Decimal,
        "DATETIME": datetime,
    }

    for name, module in required_modules.items():

        if module is None:

            raise RuntimeError(
                "UNIT 1 MODULE UNAVAILABLE: "
                + name
            )

        print(
            "PASS: UNIT 1 MODULE =",
            name,
            flush=True,
        )

    # ========================================================
    # 2. EXECUTION ENVIRONMENT
    # ========================================================

    execution_environment = "DEMO"

    if execution_environment != "DEMO":

        raise RuntimeError(
            "UNIT 1 INVALID EXECUTION ENVIRONMENT"
        )

    print(
        "PASS: EXECUTION ENVIRONMENT = DEMO",
        flush=True,
    )

    # ========================================================
    # 3. UNIVERSAL COIN ARCHITECTURE
    #
    # COIN SELECTION BELONGS TO UNIT 2.
    # UNIT 1 MUST NOT HARDCODE BTC, NEAR, OR SOL.
    # ========================================================

    print(
        "UNIVERSAL COIN SUPPORT = ENABLED BY DESIGN",
        flush=True,
    )

    print(
        "TRADING SYMBOL AUTHORITY = UNIT 2",
        flush=True,
    )

    print(
        "COIN-SPECIFIC CONTRACT VALIDATION = LATER UNITS",
        flush=True,
    )

    # ========================================================
    # 4. BOT MODE RESPONSIBILITY
    #
    # BOT_MODE CONTROLS NEW INITIAL ENTRIES ONLY.
    # EXISTING OPEN POSITIONS REMAIN UNDER MANAGEMENT.
    # ========================================================

    print(
        "BOT_MODE AUTHORITY = UNIT 12 NEW ENTRIES",
        flush=True,
    )

    print(
        "EXISTING POSITION MANAGEMENT = INDEPENDENT",
        flush=True,
    )

    # ========================================================
    # 5. HYBRID STRATEGY RESPONSIBILITIES
    #
    # THIS IS THE ARCHITECTURE CONTRACT.
    # NO TRADING LOGIC EXECUTES HERE.
    # ========================================================

    print(
        "ENTRY ENGINE = UNIFIED SCALP STRUCTURE BREAKOUT",
        flush=True,
    )

    print(
        "PRE-TP1 PROTECTION = ONE ATR HEDGE RECOVERY CYCLE",
        flush=True,
    )

    print(
        "SECOND ATR HEDGE CYCLE = PROHIBITED BY POLICY",
        flush=True,
    )

    print(
        "POST-HEDGE RECOVERY = CONDITIONAL B1-B5",
        flush=True,
    )

    print(
        "TP1 TARGET = 20% NET POSITION ROI",
        flush=True,
    )

    print(
        "TP2 TARGET = 40% NET POSITION ROI",
        flush=True,
    )

    print(
        "TP3 TARGET = DYNAMIC NET ROI TRAILING",
        flush=True,
    )

    print(
        "TP ALLOCATION = 10 / 20 / 70",
        flush=True,
    )

    print(
        "TP CALCULATION = AFTER VERIFIED INITIAL FILL",
        flush=True,
    )

    print(
        "INITIAL TP EXCLUDES FUTURE HEDGE AND BACKUP COSTS",
        flush=True,
    )

    print(
        "SECURED TP PROFITS = SEPARATE PROTECTED LEDGER",
        flush=True,
    )

    print(
        "POST TP1 = DYNAMIC BREAK EVEN ON REMAINING TRADE",
        flush=True,
    )

    print(
        "POST TP2 = DYNAMIC TRAILING ON REMAINING TRADE",
        flush=True,
    )

    print(
        "FAILING TRADE STRATEGY EXIT = EXPOSURE CAP",
        flush=True,
    )

    # ========================================================
    # 6. DEMO EXECUTION SAFETY
    #
    # UNIT 1 HAS NO EXCHANGE CONNECTION.
    # UNIT 1 NEVER SUBMITS AN ORDER.
    # LATER UNITS CONTROL VALIDATED DEMO EXECUTION.
    # ========================================================

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
        "REAL CASH EXECUTION = DISABLED",
        flush=True,
    )

    # ========================================================
    # 7. UNIT RESPONSIBILITY BOUNDARY
    #
    # UNIT 1 DOES NOT EXECUTE:
    #
    # - CONTRACT DISCOVERY
    # - MARKET DATA REQUESTS
    # - ENTRY SIGNAL QUALIFICATION
    # - DEMO ORDER SUBMISSION
    # - TP ORDER SUBMISSION
    # - ATR HEDGE EXECUTION
    # - B1-B5 RECOVERY EXECUTION
    # - PROFIT TRANSFERS
    # - POSITION CLOSURE
    #
    # THESE BELONG TO LATER VERIFIED UNITS.
    # ========================================================

    print(
        "PASS: UNIT 1 RUNTIME FOUNDATION READY",
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
# PRESERVE ORIGINAL READINESS VARIABLE
# ============================================================

FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)


if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:

    raise RuntimeError(
        "UNIT 1 STARTUP VALIDATION FAILED"
    )


# ============================================================
# UNIVERSAL WEEX — COMPLETE UNIT 2 V4
# CENTRAL CONFIGURATION AND READINESS FOUNDATION
# DEMO ONLY — REAL CASH DISABLED
# ZERO INDENTATION
# ============================================================

import os
from decimal import Decimal, InvalidOperation


def u2_v3_number(value, name, minimum=None, maximum=None):
    if isinstance(value, bool):
        raise RuntimeError("UNIT 2 INVALID " + name)

    try:
        n = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 2 INVALID " + name
        ) from exc

    if not n.is_finite():
        raise RuntimeError("UNIT 2 NONFINITE " + name)

    if minimum is not None:
        if n < Decimal(str(minimum)):
            raise RuntimeError(
                "UNIT 2 BELOW MINIMUM " + name
            )

    if maximum is not None:
        if n > Decimal(str(maximum)):
            raise RuntimeError(
                "UNIT 2 ABOVE MAXIMUM " + name
            )

    return n


def u2_v3_env(name, default, minimum=None, maximum=None):
    raw = os.getenv(name, str(default)).strip()
    return u2_v3_number(
        raw, name, minimum, maximum
    )


def u2_v3_bool(name, default=False):
    raw = os.getenv(
        name,
        "TRUE" if default else "FALSE"
    ).strip().upper()

    if raw in ("TRUE", "1", "ON", "YES"):
        return True

    if raw in ("FALSE", "0", "OFF", "NO"):
        return False

    raise RuntimeError(
        "UNIT 2 INVALID BOOLEAN " + name
    )


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print(
        "UNIVERSAL WEEX UNIT 2 V4 START",
        flush=True
    )

    # --------------------------------------------------------
    # 2.1 RENDER ENVIRONMENT
    # --------------------------------------------------------

    margin = u2_v3_env(
        "ENTRY_MARGIN_USDT", "5", "0.01"
    )

    symbol = os.getenv(
        "WEEX_SYMBOL", "NEARUSDT"
    ).strip().upper()

    if (
        not symbol.endswith("USDT")
        or not symbol[:-4].isalnum()
    ):
        raise RuntimeError(
            "UNIT 2 INVALID TRADING SYMBOL"
        )

    base_coin = symbol[:-4]

    leverage_long = u2_v3_env(
        "WEEX_LEVERAGE_LONG", "10", "1"
    )

    leverage_short = u2_v3_env(
        "WEEX_LEVERAGE_SHORT", "10", "1"
    )

    exposure_cap = u2_v3_env(
        "EXPOSURE_CAP_PERCENT", "50",
        "0.01", "100"
    )

    backup_margin = u2_v3_env(
        "BACKUP_MARGIN_PERCENT", "0.5",
        "0.01", "100"
    )

    backup_buffer = u2_v3_env(
        "BACKUP_BUFFER_PERCENT", "0.3",
        "0.01", "99"
    )

    tp1_roi = u2_v3_env(
        "TP1_NET_ROI_PERCENT", "20", "0.01"
    )

    tp2_roi = u2_v3_env(
        "TP2_NET_ROI_PERCENT", "40", "0.01"
    )

    if tp2_roi <= tp1_roi:
        raise RuntimeError(
            "UNIT 2 TP2 MUST EXCEED TP1"
        )

    # --------------------------------------------------------
    # 2.2 EXCHANGE
    # --------------------------------------------------------

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",
        "market_symbol": symbol,
        "base_coin": base_coin,
        "quote_coin": "USDT",

        # Candidate is not executable verification.
        "demo_order_symbol": None,
        "demo_symbol_candidate":
            base_coin + "SUSDT",
        "demo_symbol_verified": False,
        "contract_precision_verified": False,
        "contract_value_verified": False,
    }

    # --------------------------------------------------------
    # 2.3 ENTRY
    # --------------------------------------------------------

    entry = {
        "margin_mode": "FIXED_USDT",
        "initial_margin_mode": "FIXED_USDT",
        "fixed_margin_usdt": float(margin),
        "entry_margin_usdt": float(margin),
        "initial_fixed_usdt": float(margin),
        "configured_margin_usdt": float(margin),
        "resolved_margin_usdt": float(margin),
        "margin_source": "RENDER_FIXED_USDT",
        "coin_equivalent_enabled": False,
        "initial_coin_amount": None,
        "auto_increase_margin": False,
        "require_contract_minimum": True,
        "require_tp_partial_feasibility": True,
        "require_hedge_half_feasibility": True,
    }

    # --------------------------------------------------------
    # 2.4 MANUAL LEVERAGE AUTHORITY
    # --------------------------------------------------------

    leverage = {
        "long": float(leverage_long),
        "short": float(leverage_short),
        "authority": "RENDER_MANUAL_INPUT",

        # Do not change leverage on WEEX.
        "exchange_leverage_read_enabled": False,
        "exchange_leverage_write_enabled": False,

        # Manual values are configuration evidence,
        # not independent exchange confirmation.
        "actual_exchange_leverage_verified": False,
    }

    # --------------------------------------------------------
    # 2.5 EXECUTION SAFETY — CORRECTED
    # --------------------------------------------------------

    safety = {
        "public_market_data_read_enabled": True,
        "demo_account_balance_read_enabled": True,

        # Capability permissions for later units.
        # Each request must still authenticate and
        # validate its actual exchange response.
        "authenticated_api_enabled": True,
        "account_access_enabled": True,
        "position_access_enabled": True,
        "order_endpoint_access_enabled": True,

        # Unit 2 never submits orders.
        "demo_order_submission_enabled": False,
        "real_order_submission_enabled": False,
        "exchange_mutation_enabled": False,

        "leverage_mutation_enabled": False,
        "margin_mode_mutation_enabled": False,
        "position_mode_mutation_enabled": False,
        "unit2_exchange_write_enabled": False,

        "unit12_new_entry_authority": True,
        "units13_14_management_independent": True,

        # New readiness policy.
        "demo_read_permission_enabled": True,
        "demo_order_write_authority_unit": 12,
        "require_exchange_backed_verification": True,
        "allow_unverified_entry": False,
        "allow_live_cash_orders": False,
    }

    # --------------------------------------------------------
    # 2.6 STRATEGY
    # --------------------------------------------------------

    strategy = {
        "initial_margin_mode": "FIXED_USDT",
        "initial_fixed_usdt": float(margin),
        "entry_margin_usdt": float(margin),
        "initial_coin_amount": None,

        "exposure_cap_percent": float(exposure_cap),
        "exposure_cap_max_percent": 100.0,
        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",
        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "max_backups": 5,
        "backup_margin_percent":
            float(backup_margin),
        "backup_buffer_percent":
            float(backup_buffer),
        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",
        "backup_trigger_reference":
            "VERIFIED_WEEX_LIQUIDATION_PRICE",
        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",
        "backup_long_liquidation_factor":
            float(
                Decimal("1")
                - backup_buffer / 100
            ),
        "backup_short_liquidation_factor":
            float(
                Decimal("1")
                + backup_buffer / 100
            ),
        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        "tp1_net_roi_floor_percent":
            float(tp1_roi),
        "tp2_net_roi_floor_percent":
            float(tp2_roi),
        "tp1_net_roi_target_percent":
            float(tp1_roi),
        "tp2_net_roi_target_percent":
            float(tp2_roi),

        "tp_calculation_after_verified_fill": True,
        "initial_tp_excludes_future_hedge_costs": True,
        "initial_tp_excludes_future_backup_costs": True,

        "secured_profit_reuse_enabled": False,
        "post_tp1_dynamic_break_even": True,
        "post_tp2_dynamic_trailing": True,
        "tp3_trailing_enabled": True,
        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        "hedge_mode": "REVERSIBLE_ATR_TWO_STAGE",
        "hedge_cycles_maximum": 1,
        "hedge_h1_atr_multiple": 1.0,
        "hedge_h2_atr_multiple": 2.0,
        "hedge_h1_original_percent": 50.0,
        "hedge_h1_opposite_percent": 50.0,
        "hedge_h2_original_percent": 0.0,
        "hedge_h2_opposite_percent": 100.0,
        "hedge_recovery_enabled": True,
        "second_hedge_cycle_enabled": False,
        "post_hedge_backup_enabled": True,

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "one_direction_only": True,
        "mode_confirmations_required": 2,
    }

    # --------------------------------------------------------
    # 2.7 SIGNAL QUALIFICATION
    # --------------------------------------------------------

    qualification = {
        "common": {
            "mode_priority": (
                "BREAKOUT", "STRUCTURE", "SCALP"
            ),
            "unified_market_movement": True,
            "use_closed_candles": True,
            "protect_developing_candidates": True,
            "arbitrate_before_scalp": True,
            "scalp_requires_higher_modes_clear": True,
            "reject_late_impulse_entry": True,
            "direction_votes_required": 2,
            "direction_votes_total": 3,
            "signal_expiry_seconds": 120,
            "candidate_expiry_seconds": 600,
            "spike_count_rejection_above": 2,
        },

        "breakout": {
            "enabled": True,
            "priority": 1,
            "early_detection_enabled": True,
            "developing_candidate_enabled": True,
            "support_resistance_lookback": 20,
            "developing_proximity_atr": 0.5,
            "confirmation_distance_atr": 0.1,
            "momentum_lookback_fast": 5,
            "momentum_lookback_slow": 15,
            "require_momentum_confirmation": True,
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "retest_mandatory": False,
            "allow_preconfirmation": True,
            "max_price_extension_atr": 3.0,
            "false_breakout_rejection": True,
            "volume_confirmation_enabled": False,
            "minimum_volume_ratio": 1.2,
            "candidate_expiry_seconds": 600,
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
            "require_direction_agreement": True,
            "require_ema_crossover": False,
            "allow_pullback_entry": True,
            "allow_continuation_entry": True,
            "pullback_tolerance_atr": 0.75,
            "max_price_extension_atr": 2.0,
            "reject_trend_exhaustion": True,
            "candidate_expiry_seconds": 600,
        },

        "scalp": {
            "enabled": True,
            "priority": 3,
            "sideways_preferred": True,
            "require_sideways_market": True,
            "protect_developing_higher_modes": True,
            "quality_threshold": 70.0,
            "early_entry_enabled": True,
            "reject_late_impulse": True,
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
    # 2.8 CONTRACT METADATA
    # --------------------------------------------------------

    market_precision = {
        "quantity_step": None,
        "minimum_quantity": None,
        "price_step": None,
        "verified": False,
        "authority": "UNIT7_PUBLIC_CONTRACT_METADATA",
    }

    # --------------------------------------------------------
    # 2.9 MANAGEMENT RESPONSIBILITIES
    # --------------------------------------------------------

    management = {
        "new_entry_unit": 12,
        "tp_unit": 13,
        "hedge_backup_unit": 14,
        "reporting_unit": 15,

        "bot_mode_applies_to_new_entries_only": True,
        "position_management_independent_of_bot_mode":
            True,
        "tp_independent_of_entry_signal": True,
        "hedge_independent_of_entry_signal": True,
        "backup_independent_of_entry_signal": True,
        "require_verified_position_for_management":
            True,

        "tp1_net_roi_target_percent":
            float(tp1_roi),
        "tp2_net_roi_target_percent":
            float(tp2_roi),
        "tp3_trailing_enabled": True,
        "secured_profit_protected": True,
        "pre_tp1_hedge_cycles_maximum": 1,
        "second_hedge_cycle_allowed": False,
        "post_hedge_b1_b5_allowed": True,
    }

    # --------------------------------------------------------
    # 2.10 CONFIGURATION HANDOVER
    # --------------------------------------------------------

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",
        "entry": entry,
        "leverage": leverage,
        "safety": safety,
        "strategy": strategy,
        "qualification": qualification,
        "market_precision": market_precision,
        "management": management,

        "margin_mode": "FIXED_USDT",
        "entry_margin_usdt": float(margin),
        "initial_margin_mode": "FIXED_USDT",
        "initial_margin_usdt": float(margin),
    }

    # --------------------------------------------------------
    # 2.11 VALIDATION
    # --------------------------------------------------------

    assert config["execution_environment"] == "DEMO"
    assert config["margin_mode"] == "FIXED_USDT"

    assert (
        config["entry"]["entry_margin_usdt"]
        == config["strategy"]["entry_margin_usdt"]
        == config["entry_margin_usdt"]
    )

    assert (
        strategy["tp1_allocation_percent"]
        + strategy["tp2_allocation_percent"]
        + strategy["tp3_allocation_percent"]
        == 100.0
    )

    assert strategy["max_backups"] == 5
    assert strategy["hedge_cycles_maximum"] == 1

    assert safety["authenticated_api_enabled"] is True
    assert safety["account_access_enabled"] is True
    assert safety["position_access_enabled"] is True

    assert safety["demo_order_submission_enabled"] is False
    assert safety["real_order_submission_enabled"] is False
    assert safety["exchange_mutation_enabled"] is False
    assert safety["unit2_exchange_write_enabled"] is False

    # --------------------------------------------------------
    # 2.12 RENDER LOGS
    # --------------------------------------------------------

    print(
        "PASS: UNIVERSAL UNIT 2 V4 CONFIG CREATED",
        flush=True
    )

    print("TRADING SYMBOL =", symbol, flush=True)
    print("BASE COIN =", base_coin, flush=True)

    print(
        "DEMO SYMBOL CANDIDATE =",
        exchange["demo_symbol_candidate"],
        flush=True
    )

    print(
        "DEMO SYMBOL VERIFIED =",
        exchange["demo_symbol_verified"],
        flush=True
    )

    print(
        "INITIAL MARGIN MODE = FIXED_USDT",
        flush=True
    )

    print(
        "ENTRY MARGIN USDT =",
        float(margin),
        flush=True
    )

    print(
        "COIN EQUIVALENT MARGIN ACTIVE = False",
        flush=True
    )

    print(
        "LONG LEVERAGE RENDER =",
        float(leverage_long),
        flush=True
    )

    print(
        "SHORT LEVERAGE RENDER =",
        float(leverage_short),
        flush=True
    )

    print(
        "LEVERAGE AUTHORITY = RENDER_MANUAL_INPUT",
        flush=True
    )

    print(
        "LEVERAGE API READ = NONE",
        flush=True
    )

    print(
        "LEVERAGE API WRITE = NONE",
        flush=True
    )

    print(
        "EXPOSURE CAP PERCENT =",
        float(exposure_cap),
        flush=True
    )

    print(
        "BACKUP COUNT =",
        strategy["max_backups"],
        flush=True
    )

    print(
        "BACKUP MARGIN PERCENT =",
        float(backup_margin),
        flush=True
    )

    print(
        "BACKUP BUFFER PERCENT =",
        float(backup_buffer),
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
        "TP ALLOCATION = 10 / 20 / 70",
        flush=True
    )

    print(
        "HEDGE MODE = REVERSIBLE_ATR_TWO_STAGE",
        flush=True
    )

    print(
        "HEDGE CYCLES MAXIMUM = 1",
        flush=True
    )

    print(
        "POST HEDGE = CONDITIONAL B1-B5",
        flush=True
    )

    print(
        "DEMO ACCOUNT READ PERMISSION =",
        safety["authenticated_api_enabled"],
        flush=True
    )

    print(
        "DEMO ACCOUNT READ VERIFIED = False",
        flush=True
    )

    print(
        "DEMO CONTRACT VERIFIED = False",
        flush=True
    )

    print(
        "PENDING ORDERS VERIFIED = False",
        flush=True
    )

    print(
        "POSITION MODE VERIFIED = False",
        flush=True
    )

    print(
        "BOT_MODE AUTHORITY = UNIT 12 NEW ENTRIES",
        flush=True
    )

    print(
        "UNIT 13 TP MANAGEMENT INDEPENDENT = True",
        flush=True
    )

    print(
        "UNIT 14 HEDGE/BACKUP INDEPENDENT = True",
        flush=True
    )

    print(
        "UNIT 2 DEMO ORDER SUBMISSION = DISABLED",
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
# SINGLE CENTRAL CONFIGURATION AUTHORITY
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END COMPLETE UNIVERSAL UNIT 2 V4
# UNIT 3 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# UNIVERSAL WEEX — COMPLETE UNIT 3 V2
# FIXED USDT MARGIN — UNIT 2 V3 AUTHORITY
#
# PUBLIC WEEX V3 MARK PRICE
# UNIVERSAL COIN SUPPORT
# MARKET TIMESTAMP AND FRESHNESS VALIDATION
# FIXED ENTRY MARGIN FROM UNIT 2
# UNIT 4 LEGACY SNAPSHOT CONTRACT PRESERVED
#
# ZERO INDENTATION
# READ ONLY — NO PRIVATE API OR EXCHANGE WRITES
# ============================================================

import os
import json
import time
import math
import urllib.request
import urllib.parse
import urllib.error

from decimal import Decimal, InvalidOperation


# ============================================================
# 3.1 VALIDATE PUBLIC MARK PRICE RESPONSE
# ============================================================

def unit_3_validate_mark_payload(
    payload,
    expected_symbol,
    received_time_ms,
    max_age_ms=120000,
    future_tolerance_ms=15000,
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
            "UNIT 3 NONFINITE OR NONPOSITIVE PRICE"
        )

    timestamp = payload.get("time")

    if (
        type(timestamp) is not int
        or timestamp <= 0
    ):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET TIMESTAMP"
        )

    age_ms = int(received_time_ms) - timestamp

    if age_ms < -future_tolerance_ms:
        raise RuntimeError(
            "UNIT 3 FUTURE MARKET TIMESTAMP"
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
# 3.2 READ CENTRAL FIXED-USDT MARGIN
# ============================================================

def unit_3_validate_fixed_margin(config):

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 INVALID CONFIGURATION"
        )

    entry = config.get("entry")
    strategy = config.get("strategy")

    if not isinstance(entry, dict):
        raise RuntimeError(
            "UNIT 3 ENTRY CONFIG MISSING"
        )

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 3 STRATEGY CONFIG MISSING"
        )

    modes = (
        config.get("margin_mode"),
        config.get("initial_margin_mode"),
        entry.get("margin_mode"),
        entry.get("initial_margin_mode"),
        strategy.get("initial_margin_mode"),
    )

    if any(
        mode != "FIXED_USDT"
        for mode in modes
    ):
        raise RuntimeError(
            "UNIT 3 MARGIN MODE MISMATCH"
        )

    values = (
        config.get("entry_margin_usdt"),
        config.get("initial_margin_usdt"),
        entry.get("entry_margin_usdt"),
        entry.get("fixed_margin_usdt"),
        strategy.get("entry_margin_usdt"),
        strategy.get("initial_fixed_usdt"),
    )

    try:
        decimals = [
            Decimal(str(value))
            for value in values
        ]
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARGIN VALUE"
        ) from exc

    if any(
        not value.is_finite()
        or value <= 0
        for value in decimals
    ):
        raise RuntimeError(
            "UNIT 3 INVALID FIXED USDT MARGIN"
        )

    if len(set(decimals)) != 1:
        raise RuntimeError(
            "UNIT 3 MARGIN AUTHORITY MISMATCH"
        )

    return decimals[0]


# ============================================================
# 3.3 PURE VALIDATION TESTS
# NO HTTP REQUEST / NO EXCHANGE WRITES
# ============================================================

def unit_3_validation_tests_v3():

    print("=" * 80, flush=True)
    print(
        "UNIT 3 UNIVERSAL VALIDATION START",
        flush=True,
    )

    now_ms = 1800000000000

    valid = {
        "symbol": "NEARUSDT",
        "price": "4.152",
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
            "UNIT 3 TEST:",
            name,
            "=",
            "PASS" if condition else "FAIL",
            flush=True,
        )

    def rejected(payload):

        try:
            unit_3_validate_mark_payload(
                payload,
                "NEARUSDT",
                now_ms,
            )
        except RuntimeError:
            return True

        return False

    validated = unit_3_validate_mark_payload(
        valid,
        "NEARUSDT",
        now_ms,
    )

    check(
        "VALID SYMBOL",
        valid["symbol"] == "NEARUSDT",
    )

    check(
        "VALID MARK PRICE",
        validated["price"] == 4.152,
    )

    check(
        "VALID EXCHANGE TIMESTAMP",
        validated["exchange_time_ms"]
        == now_ms - 1000,
    )

    check(
        "VALID MARKET AGE",
        validated["market_age_ms"] == 1000,
    )

    tests = (
        (
            "REJECT WRONG SYMBOL",
            {**valid, "symbol": "BTCUSDT"},
        ),
        (
            "REJECT ZERO PRICE",
            {**valid, "price": "0"},
        ),
        (
            "REJECT NEGATIVE PRICE",
            {**valid, "price": "-1"},
        ),
        (
            "REJECT NONNUMERIC PRICE",
            {**valid, "price": "bad"},
        ),
        (
            "REJECT NONFINITE PRICE",
            {**valid, "price": "nan"},
        ),
        (
            "REJECT STALE DATA",
            {
                **valid,
                "time": now_ms - 130000,
            },
        ),
        (
            "REJECT FUTURE TIMESTAMP",
            {
                **valid,
                "time": now_ms + 20000,
            },
        ),
        (
            "REJECT MISSING TIMESTAMP",
            {
                "symbol": "NEARUSDT",
                "price": "4.152",
            },
        ),
        (
            "REJECT INVALID PAYLOAD",
            [],
        ),
    )

    for name, payload in tests:
        check(name, rejected(payload))

    original = FRESH_RECONSTRUCTION_CONFIG

    margin = unit_3_validate_fixed_margin(
        original
    )

    check(
        "FIXED USDT MARGIN AUTHORITY",
        margin > 0,
    )

    check(
        "FIXED USDT CONFIG CONSISTENCY",
        original["margin_mode"] == "FIXED_USDT"
        and original["entry"]["margin_mode"]
        == "FIXED_USDT",
    )

    check(
        "COIN CONVERSION DISABLED",
        original["entry"].get(
            "coin_equivalent_enabled"
        ) is False,
    )

    # Test that price changes never modify
    # the fixed entry margin.

    check(
        "PRICE INDEPENDENT MARGIN",
        margin == unit_3_validate_fixed_margin(
            original
        ),
    )

    print(
        "UNIT 3 TESTS PASSED =",
        passed,
        flush=True,
    )

    print(
        "UNIT 3 TESTS FAILED =",
        failed,
        flush=True,
    )

    if failed:
        raise RuntimeError(
            "UNIT 3 VALIDATION FAILED"
        )

    print(
        "UNIT 3 OPTIMIZATION VALIDATION RESULT = PASS",
        flush=True,
    )

    print(
        "UNIT 3 TEST EXCHANGE WRITE = NONE",
        flush=True,
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# 3.4 LIVE PUBLIC MARKET READ
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)

    print(
        "UNIVERSAL WEEX UNIT 3 V2 START",
        flush=True,
    )

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 CONFIGURATION MISSING"
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

    symbol = exchange.get("market_symbol")

    base_url = exchange.get(
        "contract_base_url"
    )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or base_url
        != "https://api-contract.weex.com"
        or not isinstance(symbol, str)
        or not symbol.endswith("USDT")
    ):
        raise RuntimeError(
            "UNIT 3 EXCHANGE CONFIG INVALID"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 3 NOT DEMO ENVIRONMENT"
        )

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
        )

    
    # ========================================================
    # UNIT 3 V4 COMPATIBILITY WITH UNIT 2 V4
    #
    # Later units may use authenticated DEMO reads.
    # Unit 3 itself remains PUBLIC GET ONLY.
    # No order submission or account mutation.
    # ========================================================

    required_read_permissions = (
        "public_market_data_read_enabled",
        "demo_account_balance_read_enabled",
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
    )

    for key in required_read_permissions:

        if safety.get(key) is not True:
            raise RuntimeError(
                "UNIT 3 REQUIRED READ PERMISSION MISSING: "
                + key
            )

    forbidden_mutations = (
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
        "unit2_exchange_write_enabled",
    )

    for key in forbidden_mutations:

        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 3 UNSAFE MUTATION CONFIG: "
                + key
            )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 3 NON-DEMO ENVIRONMENT"
        )

    print(
        "PASS: UNIT 3 V4 READ PERMISSIONS COMPATIBLE",
        flush=True
    )

    print(
        "PASS: UNIT 3 EXCHANGE MUTATIONS DISABLED",
        flush=True
    )

    fixed_margin = unit_3_validate_fixed_margin(
        config
    )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 V3 CONFIG",
        flush=True,
    )

    print(
        "UNIT 3 SELECTED SYMBOL =",
        symbol,
        flush=True,
    )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True,
    )

    endpoint = "/capi/v3/market/symbolPrice"

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "priceType": "MARK",
    })

    url = base_url + endpoint + "?" + query

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent":
                "WEEX-Universal-Market-Data-V3",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 3 NON READ-ONLY REQUEST"
        )

    print(
        "PASS: UNIT 3 ENDPOINT = WEEX V3 SYMBOL PRICE",
        flush=True,
    )

    print(
        "PASS: UNIT 3 HTTP METHOD = GET",
        flush=True,
    )

    print(
        "PASS: UNIT 3 PRICE TYPE = MARK",
        flush=True,
    )

    start = time.monotonic()

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:

            http_status = response.getcode()

            body = response.read(
                1000000
            ).decode("utf-8")

    except urllib.error.HTTPError as exc:

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET HTTP FAILED"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 MARKET CONNECTION FAILED"
        ) from exc

    received_ms = int(time.time() * 1000)

    latency_ms = round(
        (time.monotonic() - start) * 1000,
        2,
    )

    if http_status != 200 or not body:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET HTTP RESPONSE"
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 3 INVALID MARKET JSON"
        ) from exc

    validated = unit_3_validate_mark_payload(
        payload,
        expected_symbol=symbol,
        received_time_ms=received_ms,
    )

    price = validated["price"]

    market_time = validated[
        "exchange_time_ms"
    ]

    age_ms = validated[
        "market_age_ms"
    ]

    # ========================================================
    # 3.5 ORIGINAL UNIT 4 HANDOVER FIELDS
    # ========================================================

    market_snapshot = {

        "exchange": "WEEX",

        "api_version": "V3",

        "symbol": symbol,

        "price": price,

        "price_type": "MARK",

        "exchange_time_ms": market_time,

        "source": "WEEX_V3_PUBLIC_MARK_PRICE",

        "read_only": True,

        # Added fields for downstream validation.
        # The original eight fields stay unchanged.

        "initial_margin_mode": "FIXED_USDT",

        "margin_mode": "FIXED_USDT",

        "resolved_initial_margin_usdt":
            float(fixed_margin),

        "entry_margin_usdt":
            float(fixed_margin),

        "margin_source": "RENDER_FIXED_USDT",

        "coin_conversion_applied": False,

        "market_age_ms": age_ms,

        "request_latency_ms": latency_ms,

        "contract_precision_verified": False,

        "demo_symbol_verified": False,
    }

    # ========================================================
    # 3.6 VERIFY ALL HANDOVER FIELDS
    # ========================================================

    required = (
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
        for key in required
    ):
        raise RuntimeError(
            "UNIT 3 MARKET SNAPSHOT INCOMPLETE"
        )

    if (
        market_snapshot["entry_margin_usdt"]
        != config["entry"]["entry_margin_usdt"]
    ):
        raise RuntimeError(
            "UNIT 3 ENTRY MARGIN HANDOVER MISMATCH"
        )

    # ========================================================
    # 3.7 RENDER VERIFICATION LOGS
    # ========================================================

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True,
    )

    print(
        "UNIT 3 SELECTED SYMBOL =",
        symbol,
        flush=True,
    )

    print(
        "UNIT 3 LIVE MARK PRICE =",
        price,
        flush=True,
    )

    print(
        "UNIT 3 MARKET TIMESTAMP =",
        market_time,
        flush=True,
    )

    print(
        "UNIT 3 MARKET AGE MS =",
        age_ms,
        flush=True,
    )

    print(
        "UNIT 3 REQUEST LATENCY MS =",
        latency_ms,
        flush=True,
    )

    print(
        "PASS: UNIT 3 MARKET DATA FRESHNESS = TRUE",
        flush=True,
    )

    print(
        "UNIT 3 INITIAL MARGIN MODE = FIXED_USDT",
        flush=True,
    )

    print(
        "UNIT 3 RESOLVED INITIAL MARGIN USDT =",
        float(fixed_margin),
        flush=True,
    )

    print(
        "UNIT 3 MARGIN SOURCE = RENDER_FIXED_USDT",
        flush=True,
    )

    print(
        "UNIT 3 COIN CONVERSION APPLIED = False",
        flush=True,
    )

    print(
        "UNIT 3 CONTRACT PRECISION VERIFIED = False",
        flush=True,
    )

    print(
        "PASS: UNIT 3 NORMALIZED MARKET SNAPSHOT",
        flush=True,
    )

    print(
        "PASS: UNIT 3 HANDOVER READY FOR UNIT 4",
        flush=True,
    )

    print(
        "UNIT 3 AUTHENTICATED API = NONE",
        flush=True,
    )

    print(
        "UNIT 3 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 3 REAL ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# 3.8 VALIDATION THEN SINGLE LIVE MARKET READ
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v3()
)

if FRESH_UNIT_3_OPTIMIZATION_READY is not True:
    raise RuntimeError(
        "UNIT 3 VALIDATION NOT READY"
    )

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3 V2
# UNIT 4 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# UNIVERSAL WEEX HYBRID BOT
# COMPLETE UNIT 4 V4 REPLACEMENT
# PART 1 OF 2
#
# MARKET DATA FOUNDATION
# ADAPTATION OF WORKING UNIT 4 V3
#
# UNIT 2 = TRADING SYMBOL AUTHORITY
# UNIT 3 = VERIFIED MARK PRICE AUTHORITY
#
# PUBLIC WEEX MARKET DATA ONLY
# NO AUTHENTICATED REQUESTS
# NO DEMO OR LIVE ORDERS
# NO EXCHANGE WRITES
# ============================================================

import os
import json
import math
import time
import urllib.parse
import urllib.request

from decimal import Decimal


# ============================================================
# 4.1 PRESERVED ADJUSTABLE QUALIFICATION DEFAULTS
# ============================================================

UNIT_4_V5_TUNING = {

    "common": {
        "direction_votes_required": 2,
        "market_age_seconds_max": 120,
    },

    "breakout": {
        "lookback_candles": 20,
        "proximity_atr": 0.50,
        "confirmation_atr": 0.10,
        "maximum_extension_atr": 3.0,
    },

    "structure": {
        "ema_alignment_mode": "EARLY",
        "pullback_tolerance_atr": 0.75,
        "maximum_extension_atr": 2.0,
    },

    "scalp": {
        "ema_compression_atr_max": 0.70,
        "range_atr_max": 8.0,
        "momentum_atr_max": 1.50,
        "preliminary_ema_separation_percent": 0.03,
        "preliminary_move_5m_percent": 0.015,
    },
}


# ============================================================
# 4.2 VALIDATION HELPERS
# ============================================================

def u4v3_num(x, label, minimum=None):

    try:
        x = float(x)

    except (
        ValueError,
        TypeError,
        OverflowError,
    ) as exc:

        raise RuntimeError(
            "UNIT4 INVALID " + label
        ) from exc

    if not math.isfinite(x):

        raise RuntimeError(
            "UNIT4 NONFINITE " + label
        )

    if minimum is not None and x < minimum:

        raise RuntimeError(
            "UNIT4 INVALID RANGE " + label
        )

    return x


def u4v3_env(key, default, minimum=0):

    return u4v3_num(
        os.getenv(key, default),
        key,
        minimum,
    )


def u4v3_ema(prices, period):

    if len(prices) < period:

        raise RuntimeError(
            "UNIT4 EMA HISTORY"
        )

    result = (
        sum(prices[:period]) / period
    )

    multiplier = (
        2 / (period + 1)
    )

    for price in prices[period:]:

        result = (
            result
            + multiplier * (price - result)
        )

    return result


# ============================================================
# 4.3 PUBLIC WEEX CANDLE RETRIEVAL
# ============================================================

def u4v3_fetch(
    symbol,
    interval,
    limit,
    kind="MARK",
):

    # Only the two public market-data paths
    # used by the working Unit 4 are allowed.

    if kind == "MARK":

        endpoint = (
            "/capi/v3/market/markPriceKlines"
        )

    elif kind == "TRADE":

        endpoint = (
            "/capi/v3/market/klines"
        )

    else:

        raise RuntimeError(
            "UNIT4 INVALID CANDLE TYPE"
        )

    if (
        not isinstance(symbol, str)
        or not symbol
        or not isinstance(interval, str)
        or not interval
        or isinstance(limit, bool)
        or not isinstance(limit, int)
        or limit < 1
        or limit > 1000
    ):

        raise RuntimeError(
            "UNIT4 INVALID CANDLE REQUEST"
        )

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    })

    url = (
        "https://api-contract.weex.com"
        + endpoint
        + "?"
        + query
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
        },
        method="GET",
    )

    timeout = u4v3_env(
        "UNIT4_HTTP_TIMEOUT_SECONDS",
        15,
        1,
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        if response.status != 200:

            raise RuntimeError(
                "UNIT4 MARKET HTTP ERROR"
            )

        payload = json.loads(
            response.read(
                2000000
            ).decode("utf-8")
        )

    if not isinstance(payload, list):

        raise RuntimeError(
            "UNIT4 INVALID MARKET RESPONSE "
            + interval
        )

    return payload


# ============================================================
# 4.4 CLOSED CANDLE NORMALIZATION
# ============================================================

def u4v3_candles(
    rows,
    interval_minutes,
    reference_time_ms,
    minimum_history=201,
):

    normalized = []

    interval_ms = (
        interval_minutes * 60000
    )

    for row in rows:

        if (
            not isinstance(
                row,
                (list, tuple),
            )
            or len(row) < 7
        ):

            raise RuntimeError(
                "UNIT4 INVALID CANDLE SHAPE"
            )

        start_time = int(row[0])
        end_time = int(row[6])

        o, h, l, c, v = [
            u4v3_num(value, "OHLCV")
            for value in row[1:6]
        ]

        if not (
            0 < l
            <= min(o, c)
            <= max(o, c)
            <= h
        ):

            raise RuntimeError(
                "UNIT4 INVALID OHLC VALUES"
            )

        if not (
            v >= 0
            and start_time < end_time
            <= start_time + interval_ms
        ):

            raise RuntimeError(
                "UNIT4 INVALID CANDLE METADATA"
            )

        normalized.append({
            "open_time_ms": start_time,
            "open": o,
            "high": h,
            "low": l,
            "close": c,
            "volume": v,
            "close_time_ms": end_time,
        })

    normalized.sort(
        key=lambda x: x["open_time_ms"]
    )

    for previous, current in zip(
        normalized,
        normalized[1:],
    ):

        difference = (
            current["open_time_ms"]
            - previous["open_time_ms"]
        )

        if difference != interval_ms:

            raise RuntimeError(
                "UNIT4 CANDLE GAP OR DUPLICATE"
            )

    closed = [
        item
        for item in normalized
        if item["close_time_ms"]
        <= reference_time_ms
    ]

    if len(closed) < minimum_history:

        raise RuntimeError(
            "UNIT4 INSUFFICIENT CANDLE HISTORY "
            + str(interval_minutes)
        )

    age = (
        reference_time_ms
        - closed[-1]["close_time_ms"]
    )

    if age < 0:

        raise RuntimeError(
            "UNIT4 FUTURE CLOSED CANDLE"
        )

    if age > (
        interval_ms + 120000
    ):

        raise RuntimeError(
            "UNIT4 STALE CLOSED CANDLE"
        )

    return normalized, closed


# ============================================================
# END UNIT 4 V4 — PART 1
#
# PART 2 MUST FOLLOW IMMEDIATELY
# DO NOT INSERT UNIT 5 HERE
# DO NOT EXECUTE THIS PART ALONE
# ============================================================



# ============================================================
# UNIVERSAL WEEX HYBRID BOT
# COMPLETE UNIT 4 V3 REPLACEMENT
#
# ADAPTIVE MARKET TRANSITION INTELLIGENCE
# REFERENCE: 17248 / 16414 MODELS
#
# SIDEWAYS / LONG / SHORT
# SCALP -> STRUCTURE -> BREAKOUT
# MULTI-TIMEFRAME EMA AND ATR
# DIRECTIONAL PRESSURE / ACCELERATION
# VERIFIED TRADED MARKET VOLUME
# TP1 / TP2 REACHABILITY ESTIMATES
# HEDGE / RECOVERY PRICE EVIDENCE
# FOUR-CATEGORY DIAGNOSTIC EVIDENCE
#
# PRESERVES ORIGINAL UNIT 5 HANDOVER
# PUBLIC MARKET DATA ONLY
# NO EXCHANGE WRITES
# ============================================================

import os
import json
import math
import time
import urllib.parse
import urllib.request

from decimal import Decimal


# ============================================================
# 4.1 ADJUSTABLE QUALIFICATION DEFAULTS
# ============================================================

UNIT_4_V5_TUNING = {

    "common": {
        "direction_votes_required": 2,
        "market_age_seconds_max": 120,
    },

    "breakout": {
        "lookback_candles": 20,
        "proximity_atr": 0.50,
        "confirmation_atr": 0.10,
        "maximum_extension_atr": 3.0,
    },

    "structure": {
        "ema_alignment_mode": "EARLY",
        "pullback_tolerance_atr": 0.75,
        "maximum_extension_atr": 2.0,
    },

    "scalp": {
        "ema_compression_atr_max": 0.70,
        "range_atr_max": 8.0,
        "momentum_atr_max": 1.50,
        "preliminary_ema_separation_percent": 0.03,
        "preliminary_move_5m_percent": 0.015,
    },
}


# ============================================================
# 4.2 VALIDATION HELPERS
# ============================================================

def u4v3_num(x, label, minimum=None):

    try:
        x = float(x)

    except (
        ValueError,
        TypeError,
        OverflowError,
    ) as exc:
        raise RuntimeError(
            "UNIT4 INVALID " + label
        ) from exc

    if not math.isfinite(x):
        raise RuntimeError(
            "UNIT4 NONFINITE " + label
        )

    if minimum is not None and x < minimum:
        raise RuntimeError(
            "UNIT4 INVALID RANGE " + label
        )

    return x


def u4v3_env(key, default, minimum=0):

    return u4v3_num(
        os.getenv(key, default),
        key,
        minimum,
    )


def u4v3_ema(prices, period):

    if len(prices) < period:
        raise RuntimeError(
            "UNIT4 EMA HISTORY"
        )

    result = (
        sum(prices[:period]) / period
    )

    multiplier = (
        2 / (period + 1)
    )

    for price in prices[period:]:

        result = (
            result
            + multiplier * (price - result)
        )

    return result


# ============================================================
# 4.3 PUBLIC WEEX CANDLE RETRIEVAL
# ============================================================

def u4v3_fetch(
    symbol,
    interval,
    limit,
    kind="MARK",
):

    if kind == "MARK":

        endpoint = (
            "/capi/v3/market/markPriceKlines"
        )

    elif kind == "TRADE":

        endpoint = (
            "/capi/v3/market/klines"
        )

    else:

        raise RuntimeError(
            "UNIT4 INVALID CANDLE TYPE"
        )

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    })

    url = (
        "https://api-contract.weex.com"
        + endpoint
        + "?"
        + query
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
        },
        method="GET",
    )

    timeout = u4v3_env(
        "UNIT4_HTTP_TIMEOUT_SECONDS",
        15,
        1,
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        if response.status != 200:
            raise RuntimeError(
                "UNIT4 MARKET HTTP ERROR"
            )

        payload = json.loads(
            response.read(
                2000000
            ).decode("utf-8")
        )

    if not isinstance(payload, list):
        raise RuntimeError(
            "UNIT4 INVALID MARKET RESPONSE "
            + interval
        )

    return payload


# ============================================================
# 4.4 CLOSED CANDLE NORMALIZATION
# ============================================================

def u4v3_candles(
    rows,
    interval_minutes,
    reference_time_ms,
    minimum_history=201,
):

    normalized = []

    interval_ms = (
        interval_minutes * 60000
    )

    for row in rows:

        if not isinstance(
            row,
            (list, tuple),
        ) or len(row) < 7:

            raise RuntimeError(
                "UNIT4 INVALID CANDLE SHAPE"
            )

        start_time = int(row[0])
        end_time = int(row[6])

        o, h, l, c, v = [
            u4v3_num(value, "OHLCV")
            for value in row[1:6]
        ]

        if not (
            0 < l
            <= min(o, c)
            <= max(o, c)
            <= h
        ):
            raise RuntimeError(
                "UNIT4 INVALID OHLC VALUES"
            )

        if not (
            v >= 0
            and start_time < end_time
            <= start_time + interval_ms
        ):
            raise RuntimeError(
                "UNIT4 INVALID CANDLE METADATA"
            )

        normalized.append({
            "open_time_ms": start_time,
            "open": o,
            "high": h,
            "low": l,
            "close": c,
            "volume": v,
            "close_time_ms": end_time,
        })

    normalized.sort(
        key=lambda x: x["open_time_ms"]
    )

    for previous, current in zip(
        normalized,
        normalized[1:],
    ):

        difference = (
            current["open_time_ms"]
            - previous["open_time_ms"]
        )

        if difference != interval_ms:

            raise RuntimeError(
                "UNIT4 CANDLE GAP OR DUPLICATE"
            )

    closed = [
        item
        for item in normalized
        if item["close_time_ms"]
        <= reference_time_ms
    ]

    if len(closed) < minimum_history:

        raise RuntimeError(
            "UNIT4 INSUFFICIENT CANDLE HISTORY "
            + str(interval_minutes)
        )

    age = (
        reference_time_ms
        - closed[-1]["close_time_ms"]
    )

    if age > (
        interval_ms + 120000
    ):
        raise RuntimeError(
            "UNIT4 STALE CLOSED CANDLE"
        )

    return normalized, closed


# ============================================================
# 4.5 MULTI-TIMEFRAME INDICATORS
# ============================================================

def u4v3_indicators(candles):

    prices = [
        candle["close"]
        for candle in candles
    ]

    ema = {
        period: u4v3_ema(
            prices,
            period,
        )
        for period in (
            19, 50, 100, 200
        )
    }

    true_ranges = []

    for index in range(
        1,
        len(candles),
    ):

        item = candles[index]
        previous = prices[index - 1]

        true_ranges.append(max(
            item["high"] - item["low"],
            abs(
                item["high"] - previous
            ),
            abs(
                item["low"] - previous
            ),
        ))

    atr14 = (
        sum(true_ranges[-14:]) / 14
    )

    if atr14 <= 0:

        raise RuntimeError(
            "UNIT4 ZERO ATR"
        )

    # Historical baseline excludes the
    # current ATR sample.

    baseline_samples = []

    for index in range(
        len(true_ranges) - 34,
        len(true_ranges),
    ):

        baseline_samples.append(
            sum(
                true_ranges[
                    index - 14:index
                ]
            ) / 14
        )

    baseline = (
        sum(baseline_samples)
        / len(baseline_samples)
    )

    if ema[19] > ema[50] > ema[200]:

        trend = "LONG"

    elif ema[19] < ema[50] < ema[200]:

        trend = "SHORT"

    elif ema[19] > ema[50]:

        trend = "EARLY_LONG"

    elif ema[19] < ema[50]:

        trend = "EARLY_SHORT"

    else:

        trend = "MIXED"

    acceleration = (
        (
            prices[-1] - prices[-4]
        )
        - (
            prices[-4] - prices[-7]
        )
    ) / atr14

    return {
        "ema19": ema[19],
        "ema50": ema[50],
        "ema100": ema[100],
        "ema200": ema[200],

        "atr14": atr14,

        "atr_percent": (
            100 * atr14 / prices[-1]
        ),

        "atr_expansion_ratio": (
            atr14 / baseline
            if baseline > 0
            else 1.0
        ),

        "trend": trend,

        "momentum_acceleration_atr":
            acceleration,

        "move_5_candles_pct": (
            100 * (
                prices[-1] / prices[-6] - 1
            )
        ),

        "move_15_candles_pct": (
            100 * (
                prices[-1] / prices[-16] - 1
            )
        ),
    }


# ============================================================
# 4.6 PRE-ENTRY NET ROI TARGET ESTIMATION
#
# ACTUAL TP ORDERS REMAIN UNIT 13 RESPONSIBILITY.
# ============================================================

def u4v3_tp(
    roi_percent,
    leverage,
    fee_percent,
    slippage_percent,
    other_cost_roi_percent,
    side,
):

    fee = (
        Decimal(str(fee_percent))
        / Decimal("100")
    )

    exit_cost = (
        Decimal(str(fee_percent))
        + Decimal(str(slippage_percent))
    ) / Decimal("100")

    desired_return = (
        Decimal(str(roi_percent))
        + Decimal(str(other_cost_roi_percent))
    ) / (
        Decimal("100")
        * Decimal(str(leverage))
    )

    required = (
        desired_return
        + fee
        + exit_cost
    )

    if side == "LONG":

        denominator = (
            Decimal("1") - exit_cost
        )

    elif side == "SHORT":

        denominator = (
            Decimal("1") + exit_cost
        )

    else:

        raise RuntimeError(
            "UNIT4 INVALID TARGET SIDE"
        )

    if denominator <= 0:
        raise RuntimeError(
            "UNIT4 INVALID TARGET COST"
        )

    movement = (
        required / denominator
    )

    return float(
        movement * 100
    )


# ============================================================
# 4.7 COMPLETE UNIT 4 MARKET ENGINE
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)

    log(
        "UNIVERSAL WEEX UNIT 4 V3 START"
    )

    config = FRESH_RECONSTRUCTION_CONFIG

    market = (
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    )

    exchange = config["exchange"]

    symbol = exchange["market_symbol"]

    
    # ========================================================
    # UNIT 4 V4 — CENTRAL SYMBOL AUTHORITY
    # Unit 2 determines the configured trading symbol.
    # Unit 3 must supply matching verified market data.
    # ========================================================

    if (
        not isinstance(symbol, str)
        or not symbol
        or market.get("symbol") != symbol
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT4 MARKET HANDOVER FAILED"
        )

    print(
        "PASS: UNIT 4 SYMBOL AUTHORITY = UNIT 2",
        flush=True,
    )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT4 NOT DEMO CONFIG"
        )

    if (
        exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT4 EXCHANGE BASE URL INVALID"
        )

    if config.get(
        "safety", {}
    ).get(
        "real_order_submission_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT4 REAL ORDER SAFETY FAILED"
        )

    timestamp = int(
        market["exchange_time_ms"]
    )

    mark_price = u4v3_num(
        market["price"],
        "MARK PRICE",
        0.000000001,
    )

    market_age = (
        int(time.time() * 1000)
        - timestamp
    )

    if not (
        0 <= market_age <= 120000
    ):
        raise RuntimeError(
            "UNIT4 STALE MARKET PRICE"
        )

    # ========================================================
    # 4.8 REQUEST FOUR TIMEFRAMES
    # ========================================================

    timeframes = (
        ("1m", 1),
        ("5m", 5),
        ("15m", 15),
        ("1h", 60),
    )

    closed_by_timeframe = {}
    returned_by_timeframe = {}
    timeframe_analysis = {}

    for interval, minutes in timeframes:

        count = (
            300 if interval == "1m"
            else 240
        )

        raw = u4v3_fetch(
            symbol,
            interval,
            count,
        )

        returned, closed = (
            u4v3_candles(
                raw,
                minutes,
                timestamp,
            )
        )

        returned_by_timeframe[
            interval
        ] = returned

        closed_by_timeframe[
            interval
        ] = closed

        timeframe_analysis[
            interval
        ] = u4v3_indicators(
            closed
        )

    candles = closed_by_timeframe["1m"]

    one = timeframe_analysis["1m"]

    prices = [
        item["close"]
        for item in candles
    ]

    latest_close = prices[-1]
    previous_close = prices[-2]

    atr14 = one["atr14"]

    def movement(period):

        return (
            100
            * (
                latest_close
                / prices[-period - 1]
                - 1
            )
        )

    # ========================================================
    # 4.9 MARKET DIRECTION VOTING
    # ========================================================

    ema19 = one["ema19"]
    ema50 = one["ema50"]
    ema100 = one["ema100"]
    ema200 = one["ema200"]

    ema_vote = (
        "LONG"
        if ema19 > ema50
        else "SHORT"
        if ema19 < ema50
        else "NONE"
    )

    combined_momentum = (
        movement(5) + movement(15)
    )

    momentum_vote = (
        "LONG"
        if combined_momentum > 0
        else "SHORT"
        if combined_momentum < 0
        else "NONE"
    )

    price_vote = (
        "LONG"
        if latest_close > ema19
        else "SHORT"
        if latest_close < ema19
        else "NONE"
    )

    votes = (
        ema_vote,
        momentum_vote,
        price_vote,
    )

    long_votes = votes.count("LONG")
    short_votes = votes.count("SHORT")

    if long_votes >= 2:

        direction = "LONG"

    elif short_votes >= 2:

        direction = "SHORT"

    else:

        direction = "NONE"

    # ========================================================
    # 4.10 MULTI-TIMEFRAME ALIGNMENT
    # ========================================================

    bullish_frames = sum(
        item["trend"] in (
            "LONG",
            "EARLY_LONG",
        )
        for item
        in timeframe_analysis.values()
    )

    bearish_frames = sum(
        item["trend"] in (
            "SHORT",
            "EARLY_SHORT",
        )
        for item
        in timeframe_analysis.values()
    )

    confirmed_bullish = sum(
        item["trend"] == "LONG"
        for item
        in timeframe_analysis.values()
    )

    confirmed_bearish = sum(
        item["trend"] == "SHORT"
        for item
        in timeframe_analysis.values()
    )

    if bullish_frames >= 3:

        mtf_direction = "LONG"

    elif bearish_frames >= 3:

        mtf_direction = "SHORT"

    else:

        mtf_direction = "MIXED"

    # ========================================================
    # 4.11 BREAKOUT DEVELOPMENT
    # ========================================================

    tuning = UNIT_4_V5_TUNING

    breakout_settings = tuning["breakout"]

    lookback = int(
        u4v3_env(
            "UNIT4_BREAKOUT_LOOKBACK",
            breakout_settings[
                "lookback_candles"
            ],
            2,
        )
    )

    lookback = min(
        lookback,
        80,
    )

    reference = candles[
        -lookback - 1:-1
    ]

    support = min(
        item["low"]
        for item in reference
    )

    resistance = max(
        item["high"]
        for item in reference
    )

    proximity = u4v3_env(
        "BREAKOUT_PROXIMITY_ATR",
        breakout_settings[
            "proximity_atr"
        ],
    )

    confirmation = u4v3_env(
        "BREAKOUT_CONFIRMATION_ATR",
        breakout_settings[
            "confirmation_atr"
        ],
    )

    breakout_extension = u4v3_env(
        "BREAKOUT_MAX_EXTENSION_ATR",
        breakout_settings[
            "maximum_extension_atr"
        ],
    )

    long_breakout_distance = (
        latest_close - resistance
    ) / atr14

    short_breakout_distance = (
        support - latest_close
    ) / atr14

    breakout_confirmed_long = bool(
        direction == "LONG"
        and confirmation
        < long_breakout_distance
        <= breakout_extension
    )

    breakout_confirmed_short = bool(
        direction == "SHORT"
        and confirmation
        < short_breakout_distance
        <= breakout_extension
    )

    breakout_developing_long = bool(
        direction == "LONG"
        and -proximity
        <= long_breakout_distance
        <= confirmation
    )

    breakout_developing_short = bool(
        direction == "SHORT"
        and -proximity
        <= short_breakout_distance
        <= confirmation
    )

    # ========================================================
    # 4.12 STRUCTURE DEVELOPMENT
    # ========================================================

    structure_settings = tuning["structure"]

    alignment = os.getenv(
        "STRUCTURE_EMA_MODE",
        structure_settings[
            "ema_alignment_mode"
        ],
    ).upper()

    if alignment not in (
        "EARLY",
        "STRICT",
    ):
        raise RuntimeError(
            "UNIT4 INVALID STRUCTURE MODE"
        )

    structure_side = (
        "LONG"
        if ema19 > ema50
        else "SHORT"
        if ema19 < ema50
        else "NONE"
    )

    strict_long = (
        ema19 > ema50 > ema200
    )

    strict_short = (
        ema19 < ema50 < ema200
    )

    structure_pullback = u4v3_env(
        "STRUCTURE_PULLBACK_ATR",
        structure_settings[
            "pullback_tolerance_atr"
        ],
    )

    structure_extension = u4v3_env(
        "STRUCTURE_MAX_EXTENSION_ATR",
        structure_settings[
            "maximum_extension_atr"
        ],
    )

    price_extension = (
        abs(latest_close - ema19)
        / atr14
    )

    structure_fast_ok = (
        movement(5) > 0
        if structure_side == "LONG"
        else movement(5) < 0
        if structure_side == "SHORT"
        else False
    )

    structure_slow_ok = (
        movement(15) > 0
        if structure_side == "LONG"
        else movement(15) < 0
        if structure_side == "SHORT"
        else False
    )

    strict_alignment_ok = (
        strict_long
        if direction == "LONG"
        else strict_short
    )

    structure_qualifies = bool(
        direction == structure_side
        and direction != "NONE"
        and price_extension
        <= structure_extension
        and (
            alignment == "EARLY"
            or strict_alignment_ok
        )
        and structure_fast_ok
        and structure_slow_ok
    )

    structure_developing_long = bool(
        structure_qualifies
        and direction == "LONG"
    )

    structure_developing_short = bool(
        structure_qualifies
        and direction == "SHORT"
    )

    # ========================================================
    # 4.13 SIDEWAYS BUILDUP
    # ========================================================

    ema_cluster = (
        max(
            ema19,
            ema50,
            ema100,
            ema200,
        )
        - min(
            ema19,
            ema50,
            ema100,
            ema200,
        )
    )

    compression_atr = (
        ema_cluster / atr14
    )

    scalp_reference = candles[-21:-1]

    scalp_range_atr = (
        max(
            item["high"]
            for item in scalp_reference
        )
        - min(
            item["low"]
            for item in scalp_reference
        )
    ) / atr14

    scalp_momentum_atr = (
        abs(
            latest_close - prices[-16]
        ) / atr14
    )

    higher_mode_developing = any((
        breakout_confirmed_long,
        breakout_confirmed_short,
        breakout_developing_long,
        breakout_developing_short,
        structure_developing_long,
        structure_developing_short,
    ))

    compression_limit = u4v3_env(
        "SCALP_COMPRESSION_ATR_MAX",
        0.70,
    )

    range_limit = u4v3_env(
        "SCALP_RANGE_ATR_MAX",
        8.0,
    )

    momentum_limit = u4v3_env(
        "SCALP_MOMENTUM_ATR_MAX",
        1.50,
    )

    sideways_candidate = bool(
        compression_atr
        <= compression_limit
        and scalp_range_atr
        <= range_limit
        and scalp_momentum_atr
        <= momentum_limit
        and not higher_mode_developing
    )

    # ========================================================
    # 4.14 VERIFIED TRADED MARKET VOLUME
    # ========================================================

    volume_available = False
    volume_ratio20 = None
    average_volume20 = None
    latest_volume = None
    volume_error = None

    try:

        trade_rows = u4v3_fetch(
            symbol,
            "1m",
            50,
            "TRADE",
        )

        _, traded_closed = (
            u4v3_candles(
                trade_rows,
                1,
                timestamp,
                21,
            )
        )

        baseline_volumes = [
            item["volume"]
            for item in traded_closed[
                -21:-1
            ]
        ]

        average_volume20 = (
            sum(baseline_volumes) / 20
        )

        latest_volume = (
            traded_closed[-1]["volume"]
        )

        volume_available = (
            average_volume20 > 0
        )

        if volume_available:

            volume_ratio20 = (
                latest_volume
                / average_volume20
            )

    except Exception as exc:

        volume_error = (
            str(exc)[:160]
        )

    volume_threshold = u4v3_env(
        "UNIT4_VOLUME_RATIO_MIN",
        1.20,
    )

    volume_confirmed = bool(
        volume_available
        and volume_ratio20
        >= volume_threshold
    )

    # ========================================================
    # 4.15 MOMENTUM ACCELERATION / ATR EXPANSION
    # ========================================================

    acceleration = (
        one[
            "momentum_acceleration_atr"
        ]
    )

    acceleration_threshold = u4v3_env(
        "UNIT4_MOMENTUM_ACCELERATION_ATR_MIN",
        0.10,
    )

    momentum_accelerating = bool(
        (
            direction == "LONG"
            and acceleration
            >= acceleration_threshold
        )
        or (
            direction == "SHORT"
            and acceleration
            <= -acceleration_threshold
        )
    )

    atr_expansion = (
        one["atr_expansion_ratio"]
    )

    expansion_threshold = u4v3_env(
        "UNIT4_ATR_EXPANSION_RATIO_MIN",
        1.10,
    )

    volatility_expanding = bool(
        atr_expansion
        >= expansion_threshold
    )

    # ========================================================
    # 4.16 DIRECTIONAL PRESSURE SCORES
    #
    # THESE ARE DESCRIPTIVE SCORES,
    # NOT STATISTICAL TP PROBABILITIES.
    # ========================================================

    momentum_reference = max(
        one["atr_percent"] * 5,
        0.000000001,
    )

    bullish_momentum_component = max(
        0,
        min(
            1,
            movement(5)
            / momentum_reference,
        ),
    )

    bearish_momentum_component = max(
        0,
        min(
            1,
            -movement(5)
            / momentum_reference,
        ),
    )

    bullish_acceleration = max(
        0,
        min(1, acceleration),
    )

    bearish_acceleration = max(
        0,
        min(1, -acceleration),
    )

    bullish_pressure = min(
        100,
        25 * long_votes / 3
        + 25 * bullish_frames / 4
        + 25 * bullish_momentum_component
        + 25 * bullish_acceleration,
    )

    bearish_pressure = min(
        100,
        25 * short_votes / 3
        + 25 * bearish_frames / 4
        + 25 * bearish_momentum_component
        + 25 * bearish_acceleration,
    )

    buildup_score = min(
        100,
        50 * max(
            0,
            1 - compression_atr
            / max(
                compression_limit,
                0.000000001,
            ),
        )
        + 25 * max(
            0,
            1 - scalp_range_atr
            / max(
                range_limit,
                0.000000001,
            ),
        )
        + 25 * (
            1 if volatility_expanding
            else 0
        ),
    )

    # ========================================================
    # 4.17 MARKET REGIME CLASSIFICATION
    # ========================================================

    if sideways_candidate:

        regime = "SIDEWAYS"

    elif mtf_direction == "LONG":

        regime = "LONG"

    elif mtf_direction == "SHORT":

        regime = "SHORT"

    else:

        regime = "TRANSITION"

    # These are current transition candidates.
    # Confirmed transitions require previous
    # snapshots, which Unit 5 will manage.

    transition_evidence = {

        "sideways_to_long": bool(
            regime == "LONG"
            and direction == "LONG"
        ),

        "sideways_to_short": bool(
            regime == "SHORT"
            and direction == "SHORT"
        ),

        "long_to_short": bool(
            direction == "SHORT"
            and bearish_frames >= 3
        ),

        "short_to_long": bool(
            direction == "LONG"
            and bullish_frames >= 3
        ),

        "momentum_accelerating":
            momentum_accelerating,

        "volatility_expanding":
            volatility_expanding,

        "transition_confirmed_from_previous_snapshot":
            False,
    }

    # ========================================================
    # 4.18 TP1 / TP2 PRICE REACHABILITY
    # ========================================================

    fee_policy = config.get(
        "fee_policy",
        {},
    )

    leverage_config = config["leverage"]

    strategy = config["strategy"]

    fee = u4v3_num(
        fee_policy.get(
            "estimated_taker_fee_percent",
            0.08,
        ),
        "FEE",
        0,
    )

    slippage = u4v3_env(
        "UNIT4_EXIT_SLIPPAGE_RESERVE_PERCENT",
        0.05,
    )

    other_cost = u4v3_env(
        "UNIT4_OTHER_COST_ROI_RESERVE_PERCENT",
        0.0,
    )

    target_distances = {}
    reachability = {}

    for side in (
        "LONG",
        "SHORT",
    ):

        leverage = u4v3_num(
            leverage_config["long"]
            if side == "LONG"
            else leverage_config["short"],
            "LEVERAGE",
            0.01,
        )

        target_distances[side] = {}
        reachability[side] = {}

        for target_name, roi in (
            (
                "tp1",
                strategy.get(
                    "tp1_net_roi_floor_percent",
                    20,
                ),
            ),
            (
                "tp2",
                strategy.get(
                    "tp2_net_roi_floor_percent",
                    40,
                ),
            ),
        ):

            required_move = u4v3_tp(
                roi,
                leverage,
                fee,
                slippage,
                other_cost,
                side,
            )

            target_price = (
                mark_price
                * (
                    1 + required_move / 100
                    if side == "LONG"
                    else 1 - required_move / 100
                )
            )

            if target_price <= 0:

                raise RuntimeError(
                    "UNIT4 INVALID TP PRICE"
                )

            target_distances[side][
                target_name + "_move_pct"
            ] = required_move

            target_distances[side][
                target_name + "_price"
            ] = target_price

            target_distances[side][
                target_name + "_atr1m"
            ] = (
                abs(
                    target_price - mark_price
                ) / atr14
            )

        reachability[side] = {

            "tp1_price":
                target_distances[
                    side
                ]["tp1_price"],

            "tp2_price":
                target_distances[
                    side
                ]["tp2_price"],

            "tp1_move_pct":
                target_distances[
                    side
                ]["tp1_move_pct"],

            "tp2_move_pct":
                target_distances[
                    side
                ]["tp2_move_pct"],

            "tp1_atr1m_distance":
                target_distances[
                    side
                ]["tp1_atr1m"],

            "tp2_atr1m_distance":
                target_distances[
                    side
                ]["tp2_atr1m"],

            "historical_target_hit_rate":
                None,

            "probability_verified":
                False,
        }

    # ========================================================
    # 4.19 PRESERVE LEGACY MARKET SNAPSHOT
    # AND ADD V3 OPTIMIZATION EVIDENCE
    # ========================================================

    ema_structure = (
        "BULLISH"
        if strict_long
        else "BEARISH"
        if strict_short
        else "MIXED"
    )

    snapshot = {

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": symbol,
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": mark_price,
        "previous_close": previous_close,
        "latest_close": latest_close,

        "latest_open_time_ms":
            candles[-1]["open_time_ms"],

        "latest_close_time_ms":
            candles[-1]["close_time_ms"],

        "exchange_time_ms": timestamp,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            abs(ema19 - ema50)
            / ema50 * 100,

        "ema_structure": ema_structure,

        "short_term_move_pct":
            movement(1),

        "move_1m_pct": movement(1),
        "move_5m_pct": movement(5),
        "move_15m_pct": movement(15),
        "move_30m_pct": movement(30),
        "move_60m_pct": movement(60),
        "move_120m_pct": movement(120),

        "recent_closed_klines": [
            dict(item)
            for item in candles[-60:]
        ],

        "candle_count": len(
            returned_by_timeframe["1m"]
        ),

        "closed_candle_count":
            len(candles),

        "newest_returned_candle_closed":
            (
                returned_by_timeframe[
                    "1m"
                ][-1]["close_time_ms"]
                <= timestamp
            ),

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "atr14": atr14,

        "atr_percent":
            one["atr_percent"],

        "support20": support,
        "resistance20": resistance,

        "range20_atr_ratio":
            (resistance - support) / atr14,

        "near_resistance": bool(
            latest_close
            >= resistance - proximity * atr14
        ),

        "near_support": bool(
            latest_close
            <= support + proximity * atr14
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

        "structure_trend_direction":
            structure_side,

        "structure_ema_alignment_mode":
            alignment,

        "structure_momentum_fast_confirmed":
            structure_fast_ok,

        "structure_momentum_slow_confirmed":
            structure_slow_ok,

        "sideways_candidate":
            sideways_candidate,

        "direction_long_votes":
            long_votes,

        "direction_short_votes":
            short_votes,

        "direction_evidence":
            direction,

        "ema_cluster_height":
            ema_cluster,

        "ema_compression_atr":
            compression_atr,

        "scalp_range_atr":
            scalp_range_atr,

        "scalp_momentum_atr":
            scalp_momentum_atr,

        "scalp_preliminary_ema_min_pct":
            tuning["scalp"][
                "preliminary_ema_separation_percent"
            ],

        "scalp_preliminary_move_min_pct":
            tuning["scalp"][
                "preliminary_move_5m_percent"
            ],

        "price_extension_cluster":
            price_extension,

        "price_overextended":
            price_extension
            > structure_extension,

        "average_volume20":
            average_volume20,

        "latest_volume":
            latest_volume,

        "volume_ratio20":
            volume_ratio20,

        "volume_data_available":
            volume_available,

        "verified_trade_volume_ratio":
            volume_ratio20,

        "volume_confirmed":
            volume_confirmed,

        "volume_error":
            volume_error,

        "multi_timeframe_analysis":
            timeframe_analysis,

        "multi_timeframe_direction":
            mtf_direction,

        "multi_timeframe_supports_direction":
            direction == mtf_direction,

        "multi_timeframe_bullish_count":
            bullish_frames,

        "multi_timeframe_bearish_count":
            bearish_frames,

        "multi_timeframe_confirmed_bullish":
            confirmed_bullish,

        "multi_timeframe_confirmed_bearish":
            confirmed_bearish,

        "momentum_acceleration_atr":
            acceleration,

        "momentum_accelerating":
            momentum_accelerating,

        "atr_expansion_ratio":
            atr_expansion,

        "volatility_expanding":
            volatility_expanding,

        "tp_target_reachability":
            reachability,

        "tp_target_distance":
            target_distances,

        "tp_probability_verified":
            False,

        "tp_price_calculation_status":
            "PRE_ENTRY_ESTIMATE_ONLY",

        # ====================================================
        # V3 MARKET REGIME EVIDENCE
        # ====================================================

        "market_regime": {

            "current": regime,

            "previous": None,

            "confidence": None,

            "sideways_buildup_score":
                round(
                    buildup_score, 2
                ),

            "bullish_pressure_score":
                round(
                    bullish_pressure, 2
                ),

            "bearish_pressure_score":
                round(
                    bearish_pressure, 2
                ),
        },

        # ====================================================
        # V3 ENTRY QUALIFICATION EVIDENCE
        # ====================================================

        "entry_evidence": {

            "early_long": bool(
                direction == "LONG"
                and bullish_pressure
                > bearish_pressure
            ),

            "early_short": bool(
                direction == "SHORT"
                and bearish_pressure
                > bullish_pressure
            ),

            "structure_long":
                structure_developing_long,

            "structure_short":
                structure_developing_short,

            "breakout_long":
                breakout_confirmed_long,

            "breakout_short":
                breakout_confirmed_short,

            "entry_risk_factors": (
                (
                    ["UNVERIFIED_VOLUME"]
                    if not volume_available
                    else []
                )
                +
                (
                    ["HIGH_EXTENSION"]
                    if price_extension
                    > structure_extension
                    else []
                )
            ),

            "target_reachability":
                reachability,
        },

        # ====================================================
        # V3 DIRECTION CONVERSION EVIDENCE
        # ====================================================

        "transition_evidence":
            transition_evidence,

        # ====================================================
        # V3 ATR / RECOVERY EVIDENCE
        #
        # POSITION-DEPENDENT VALUES REMAIN
        # UNKNOWN UNTIL ACTUAL ENTRY/RECONCILIATION.
        # ====================================================

        "protection_evidence": {

            "atr14": atr14,

            "entry_atr_frozen":
                False,

            "adverse_atr_movement":
                None,

            "recovery_atr_movement":
                None,

            "h1_price_crossed":
                False,

            "h2_price_crossed":
                False,

            "sharp_gap_detected":
                False,

            "opposite_direction_strength":
                max(
                    bullish_pressure,
                    bearish_pressure,
                ),

            "position_reconciliation_required":
                True,
        },

        # ====================================================
        # V3 PROFIT-TARGET EVIDENCE
        # ====================================================

        "profit_evidence": {

            "tp1_estimated_price":
                target_distances.get(
                    direction,
                    {},
                ).get("tp1_price"),

            "tp2_estimated_price":
                target_distances.get(
                    direction,
                    {},
                ).get("tp2_price"),

            "tp1_reachability":
                reachability.get(
                    direction,
                    {},
                ).get(
                    "tp1_atr1m_distance"
                ),

            "tp2_reachability":
                reachability.get(
                    direction,
                    {},
                ).get(
                    "tp2_atr1m_distance"
                ),

            "target_probability_verified":
                False,

            "confirmed_fills_available":
                False,
        },

        # ====================================================
        # V3 FOUR-CATEGORY DIAGNOSTIC INPUT
        #
        # UNIT 15 PERFORMS OUTCOME CLASSIFICATION.
        # ====================================================

        "diagnostic_evidence": {

            "qualification_metrics": {

                "ema_compression_atr":
                    compression_atr,

                "direction_votes_long":
                    long_votes,

                "direction_votes_short":
                    short_votes,

                "atr_expansion_ratio":
                    atr_expansion,

                "volume_ratio20":
                    volume_ratio20,

                "price_extension_atr":
                    price_extension,
            },

            "qualification_thresholds": {

                "breakout_proximity_atr":
                    proximity,

                "breakout_confirmation_atr":
                    confirmation,

                "structure_max_extension_atr":
                    structure_extension,
            },

            "market_conditions": {

                "regime": regime,

                "mtf_direction":
                    mtf_direction,

                "atr14": atr14,
            },

            "data_quality_flags": {

                "volume_verified":
                    volume_available,

                "historical_tp_probability_verified":
                    False,
            },
        },

        "higher_mode_developing":
            higher_mode_developing,

        # Original evidence version retained
        # for downstream legacy compatibility.

        "strategy_evidence_version":
            "U4_HYBRID_V2",

        "qualification_tuning_revision":
            "UNIT4_UNIVERSAL_V3",

        "qualification_settings": {

            "breakout_lookback":
                lookback,

            "breakout_proximity_atr":
                proximity,

            "breakout_confirmation_atr":
                confirmation,

            "structure_pullback_atr":
                structure_pullback,

            "structure_max_extension_atr":
                structure_extension,

            "structure_ema_alignment_mode":
                alignment,

            "scalp_compression_atr":
                compression_limit,

            "scalp_range_atr":
                range_limit,

            "scalp_momentum_atr":
                momentum_limit,
        },

        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
    }

    # ========================================================
    # 4.20 PRESERVE QUALIFICATION CONFIG HANDOVER
    # ========================================================

    qualification = (
        config["qualification"]
    )

    qualification["breakout"].update({

        "support_resistance_lookback":
            lookback,

        "developing_proximity_atr":
            proximity,

        "confirmation_distance_atr":
            confirmation,

        "max_price_extension_atr":
            breakout_extension,
    })

    qualification["structure"].update({

        "ema_alignment_mode":
            alignment,

        "pullback_tolerance_atr":
            structure_pullback,

        "max_price_extension_atr":
            structure_extension,
    })

    qualification["scalp"].update({

        "ema_compression_atr_max":
            compression_limit,

        "range20_atr_max":
            range_limit,

        "momentum15_atr_multiplier_max":
            momentum_limit,
    })

    # ========================================================
    # 4.21 RENDER VERIFICATION LOGS
    # ========================================================

    print(
        "UNIT 4 SELECTED SYMBOL =",
        symbol,
        flush=True,
    )

    print(
        "UNIT 4 MARKET REGIME =",
        regime,
        flush=True,
    )

    print(
        "UNIT 4 DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 4 PRESSURE LONG / SHORT =",
        round(bullish_pressure, 2),
        round(bearish_pressure, 2),
        flush=True,
    )

    print(
        "UNIT 4 SIDEWAYS BUILDUP SCORE =",
        round(buildup_score, 2),
        flush=True,
    )

    for interval in timeframe_analysis:

        item = timeframe_analysis[
            interval
        ]

        print(
            "UNIT 4 TIMEFRAME =",
            interval,
            "TREND =",
            item["trend"],
            "ATR =",
            item["atr14"],
            flush=True,
        )

    print(
        "UNIT 4 MTF DIRECTION =",
        mtf_direction,
        flush=True,
    )

    print(
        "UNIT 4 ATR EXPANSION =",
        round(
            atr_expansion,
            4,
        ),
        flush=True,
    )

    print(
        "UNIT 4 MOMENTUM ACCELERATING =",
        momentum_accelerating,
        flush=True,
    )

    print(
        "UNIT 4 TRADED VOLUME AVAILABLE =",
        volume_available,
        flush=True,
    )

    print(
        "UNIT 4 VOLUME RATIO =",
        volume_ratio20,
        flush=True,
    )

    print(
        "UNIT 4 BREAKOUT LONG / SHORT =",
        breakout_confirmed_long,
        breakout_confirmed_short,
        flush=True,
    )

    print(
        "UNIT 4 STRUCTURE LONG / SHORT =",
        structure_developing_long,
        structure_developing_short,
        flush=True,
    )

    print(
        "UNIT 4 SIDEWAYS CANDIDATE =",
        sideways_candidate,
        flush=True,
    )

    for side in (
        "LONG",
        "SHORT",
    ):

        distances = (
            target_distances[side]
        )

        print(
            "UNIT 4",
            side,
            "TP1 MOVE % =",
            round(
                distances["tp1_move_pct"],
                4,
            ),
            flush=True,
        )

        print(
            "UNIT 4",
            side,
            "TP2 MOVE % =",
            round(
                distances["tp2_move_pct"],
                4,
            ),
            flush=True,
        )

    print(
        "UNIT 4 TARGET PROBABILITY VERIFIED = False",
        flush=True,
    )

    print(
        "UNIT 4 POSITION/PROFIT EVIDENCE = PRE_ENTRY_ONLY",
        flush=True,
    )

    print(
        "PASS: UNIT 4 TO UNIT 5 HANDOVER",
        flush=True,
    )

    print(
        "UNIT 4 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 4 ADAPTER RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return snapshot


# ============================================================
# 4.22 ORIGINAL GLOBAL HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END COMPLETE UNIVERSAL UNIT 4 V3
# UNIT 5 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# UNIVERSAL WEEX HYBRID BOT
# COMPLETE UNIT 5 V2 REPLACEMENT
#
# UNIT 4 V3 -> UNIT 5 V2 -> UNIT 6
#
# TWO QUALIFICATION ROUTES:
# 1. EARLY_TRANSITION
# 2. ESTABLISHED_TREND
#
# SIDEWAYS -> LONG / SHORT
# SCALP -> STRUCTURE -> BREAKOUT
# INDEPENDENT LONG / SHORT SCORES
# BEST REJECTED CANDIDATE PRESERVED
# TP1 / TP2 DISTANCE AND COST ANALYSIS
# UNIT 15 DIAGNOSTIC EVIDENCE
#
# LEGACY UNIT 5 INTERFACE RETAINED
# NO EXCHANGE WRITES
# ============================================================

import os
import math
import time


# ============================================================
# 5.1 VALIDATION HELPERS
# ============================================================

def unit_5_v2_number(
    value,
    name,
    minimum=None,
    maximum=None,
):
    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 5 INVALID NUMBER: " + name
        )

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 5 INVALID NUMBER: " + name
        ) from exc

    if not math.isfinite(result):
        raise RuntimeError(
            "UNIT 5 NONFINITE: " + name
        )

    if minimum is not None and result < minimum:
        raise RuntimeError(
            "UNIT 5 BELOW MINIMUM: " + name
        )

    if maximum is not None and result > maximum:
        raise RuntimeError(
            "UNIT 5 ABOVE MAXIMUM: " + name
        )

    return result


def unit_5_v2_env(
    name,
    default,
    minimum=0,
    maximum=None,
):
    raw = os.getenv(name, "")

    if not raw.strip():
        raw = default

    return unit_5_v2_number(
        raw,
        name,
        minimum,
        maximum,
    )


def unit_5_v2_bool_env(name, default=False):
    raw = os.getenv(name, "").strip().upper()

    if not raw:
        return bool(default)

    if raw in ("1", "TRUE", "YES", "ON"):
        return True

    if raw in ("0", "FALSE", "NO", "OFF"):
        return False

    raise RuntimeError(
        "UNIT 5 INVALID BOOLEAN ENV: " + name
    )


def unit_5_v2_direction(value):
    if value > 0:
        return "LONG"
    if value < 0:
        return "SHORT"
    return "NONE"


def unit_5_v2_matches(value, side):
    if side == "LONG":
        return value > 0
    if side == "SHORT":
        return value < 0
    return False


def unit_5_v2_clamp(value):
    return max(0.0, min(100.0, value))


# ============================================================
# 5.2 MAIN UNIT 5 V2
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot,
):

    print("=" * 80, flush=True)

    log("UNIVERSAL WEEX UNIT 5 V2 START")

    if not isinstance(unit_2_config, dict):
        raise RuntimeError("UNIT 5 CONFIG INVALID")

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError("UNIT 5 SNAPSHOT INVALID")

    config = unit_2_config
    analysis = unit_4_snapshot

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    qualification = config.get("qualification", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, qualification)
    ):
        raise RuntimeError(
            "UNIT 5 CONFIG STRUCTURE INVALID"
        )

    common = qualification.get("common", {})
    breakout_cfg = qualification.get("breakout", {})
    structure_cfg = qualification.get("structure", {})
    scalp_cfg = qualification.get("scalp", {})

    if not all(
        isinstance(x, dict)
        for x in (
            common,
            breakout_cfg,
            structure_cfg,
            scalp_cfg,
        )
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION GROUP INVALID"
        )

    symbol = exchange.get("market_symbol")

    if (
        not isinstance(symbol, str)
        or symbol != os.getenv(
            "TRADING_SYMBOL", ""
        ).strip().upper()
        or analysis.get("symbol") != symbol
        or analysis.get("exchange") != "WEEX"
        or analysis.get("api_version") != "V3"
        or analysis.get("price_type") != "MARK"
        or analysis.get("read_only") is not True
        or analysis.get(
            "strategy_evidence_version"
        ) != "U4_HYBRID_V2"
        or analysis.get(
            "qualification_tuning_revision"
        ) != "UNIT4_UNIVERSAL_V3"
    ):
        raise RuntimeError(
            "UNIT 5 UNIT 4 HANDOVER INVALID"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or safety.get(
            "public_market_data_read_enabled"
        ) is not True
        or safety.get(
            "real_order_submission_enabled"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 5 SAFETY GATE FAILED"
        )

    if tuple(
        common.get("mode_priority", ())
    ) != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 5 LEGACY MODE CONTRACT INVALID"
        )

    # ========================================================
    # 5.3 ANALYSIS FRESHNESS
    # ========================================================

    market_time_ms = unit_5_v2_number(
        analysis.get("exchange_time_ms"),
        "EXCHANGE TIME",
        1,
    )

    max_age_seconds = unit_5_v2_env(
        "UNIT5_MARKET_MAX_AGE_SECONDS",
        120,
        1,
    )

    age_seconds = (
        time.time()
        - market_time_ms / 1000
    )

    if not 0 <= age_seconds <= max_age_seconds:
        raise RuntimeError(
            "UNIT 5 STALE ANALYSIS"
        )

    def n(key):
        return unit_5_v2_number(
            analysis.get(key),
            key,
        )

    def flag(key):
        value = analysis.get(key)

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 5 INVALID BOOLEAN: " + key
            )

        return value

    live_price = n("live_mark_price")
    latest_close = n("latest_close")
    previous_close = n("previous_close")
    atr14 = n("atr14")

    if min(
        live_price,
        latest_close,
        previous_close,
        atr14,
    ) <= 0:
        raise RuntimeError(
            "UNIT 5 INVALID MARKET VALUES"
        )

    ema19 = n("ema19")
    ema50 = n("ema50")
    ema200 = n("ema200")
    separation = n("ema19_50_separation_pct")
    short_move = n("short_term_move_pct")
    extension_atr = n("price_extension_cluster")

    moves = {
        period: n("move_" + str(period) + "m_pct")
        for period in (1, 5, 15, 30, 60, 120)
    }

    regime_data = analysis.get("market_regime", {})
    timeframes = analysis.get(
        "multi_timeframe_analysis", {}
    )
    targets = analysis.get(
        "tp_target_reachability", {}
    )

    if not all(
        isinstance(x, dict)
        for x in (
            regime_data,
            timeframes,
            targets,
        )
    ):
        raise RuntimeError(
            "UNIT 5 ADAPTIVE DATA INVALID"
        )

    for timeframe in ("1m", "5m", "15m", "1h"):
        if not isinstance(
            timeframes.get(timeframe), dict
        ):
            raise RuntimeError(
                "UNIT 5 MISSING " + timeframe
            )

    regime = regime_data.get("current")

    if regime not in (
        "SIDEWAYS",
        "LONG",
        "SHORT",
        "TRANSITION",
    ):
        raise RuntimeError(
            "UNIT 5 INVALID MARKET REGIME"
        )

    long_pressure = unit_5_v2_number(
        regime_data.get("bullish_pressure_score"),
        "LONG PRESSURE",
        0, 100,
    )

    short_pressure = unit_5_v2_number(
        regime_data.get("bearish_pressure_score"),
        "SHORT PRESSURE",
        0, 100,
    )

    buildup_score = unit_5_v2_number(
        regime_data.get("sideways_buildup_score"),
        "BUILDUP",
        0, 100,
    )

    acceleration = n("momentum_acceleration_atr")
    atr_expansion = n("atr_expansion_ratio")

    if atr_expansion <= 0:
        raise RuntimeError(
            "UNIT 5 INVALID ATR EXPANSION"
        )

    volume_available = flag(
        "volume_data_available"
    )

    volume_ratio = None

    if volume_available:
        volume_ratio = unit_5_v2_number(
            analysis.get(
                "verified_trade_volume_ratio"
            ),
            "VOLUME RATIO",
            0,
        )

    # ========================================================
    # 5.4 ADJUSTABLE WEIGHTS
    # ========================================================

    weights = {
        "trend": unit_5_v2_env(
            "UNIT5_WEIGHT_TREND_ALIGNMENT", 20
        ),
        "reach": unit_5_v2_env(
            "UNIT5_WEIGHT_TARGET_REACHABILITY", 25
        ),
        "momentum": unit_5_v2_env(
            "UNIT5_WEIGHT_MOMENTUM_STRENGTH", 20
        ),
        "volatility": unit_5_v2_env(
            "UNIT5_WEIGHT_VOLATILITY_EXPANSION", 10
        ),
        "volume": unit_5_v2_env(
            "UNIT5_WEIGHT_VOLUME_CONFIRMATION", 10
        ),
        "timing": unit_5_v2_env(
            "UNIT5_WEIGHT_ENTRY_TIMING", 10
        ),
        "cost": unit_5_v2_env(
            "UNIT5_WEIGHT_COST_EFFICIENCY", 5
        ),
    }

    if abs(sum(weights.values()) - 100) > 0.001:
        raise RuntimeError(
            "UNIT 5 WEIGHTS MUST TOTAL 100"
        )

    # ========================================================
    # 5.5 TWO-PATH ENTRY THRESHOLDS
    # ========================================================

    established_score_min = unit_5_v2_env(
        "UNIT5_ENTRY_SCORE_MIN",
        75,
        0, 100,
    )

    early_score_min = unit_5_v2_env(
        "UNIT5_EARLY_SCORE_MIN",
        65,
        0, 100,
    )

    established_pressure_min = unit_5_v2_env(
        "UNIT5_DIRECTION_PRESSURE_MIN",
        55,
        0, 100,
    )

    early_pressure_min = unit_5_v2_env(
        "UNIT5_EARLY_PRESSURE_MIN",
        40,
        0, 100,
    )

    established_advantage_min = unit_5_v2_env(
        "UNIT5_PRESSURE_ADVANTAGE_MIN",
        10,
        0, 100,
    )

    early_advantage_min = unit_5_v2_env(
        "UNIT5_EARLY_PRESSURE_ADVANTAGE_MIN",
        8,
        0, 100,
    )

    established_mtf_min = int(unit_5_v2_env(
        "UNIT5_MTF_CONFIRMATION_MIN",
        2,
        1, 4,
    ))

    early_mtf_min = int(unit_5_v2_env(
        "UNIT5_EARLY_MTF_MIN",
        1,
        1, 4,
    ))

    extension_limit = unit_5_v2_env(
        "UNIT5_ENTRY_MAX_EXTENSION_ATR",
        2.0,
        0.01,
    )

    early_extension_limit = unit_5_v2_env(
        "UNIT5_EARLY_MAX_EXTENSION_ATR",
        1.5,
        0.01,
    )

    tp2_distance_limit = unit_5_v2_env(
        "UNIT5_TP2_MAX_ATR1H_DISTANCE",
        12,
        0.1,
    )

    early_tp2_limit = unit_5_v2_env(
        "UNIT5_EARLY_TP2_MAX_ATR1H",
        12,
        0.1,
    )

    minimum_volume_ratio = unit_5_v2_env(
        "UNIT5_VOLUME_RATIO_MIN",
        1.20,
        0.01,
    )

    early_momentum_min = unit_5_v2_env(
        "UNIT5_EARLY_MOMENTUM_MIN_ATR",
        0.05,
        0,
    )

    # Volume may support a signal, but absence
    # cannot be interpreted as zero activity.
    # Early volume requirement remains adjustable.

    early_require_volume = unit_5_v2_bool_env(
        "UNIT5_EARLY_REQUIRE_VOLUME",
        False,
    )

    # ========================================================
    # 5.6 SCORE LONG AND SHORT INDEPENDENTLY
    # ========================================================

    scored = {}

    fee_policy = config.get("fee_policy", {})

    if not isinstance(fee_policy, dict):
        raise RuntimeError(
            "UNIT 5 FEE POLICY INVALID"
        )

    taker_fee = unit_5_v2_number(
        fee_policy.get(
            "estimated_taker_fee_percent",
            0.08,
        ),
        "TAKER FEE",
        0,
    )

    slippage = unit_5_v2_env(
        "UNIT5_EXPECTED_SLIPPAGE_PERCENT",
        0.05,
    )

    estimated_cost_pct = (
        2 * taker_fee + slippage
    )

    for side in ("LONG", "SHORT"):

        sign = 1 if side == "LONG" else -1

        own_pressure = (
            long_pressure
            if side == "LONG"
            else short_pressure
        )

        opposite_pressure = (
            short_pressure
            if side == "LONG"
            else long_pressure
        )

        pressure_advantage = (
            own_pressure - opposite_pressure
        )

        own_votes = int(
            n(
                "direction_long_votes"
                if side == "LONG"
                else "direction_short_votes"
            )
        )

        if not 0 <= own_votes <= 3:
            raise RuntimeError(
                "UNIT 5 INVALID DIRECTION VOTES"
            )

        agreeing_frames = sum(
            tf.get("trend")
            in (
                ("LONG", "EARLY_LONG")
                if side == "LONG"
                else ("SHORT", "EARLY_SHORT")
            )
            for tf in timeframes.values()
        )

        confirmed_frames = sum(
            tf.get("trend") == side
            for tf in timeframes.values()
        )

        trend_score = unit_5_v2_clamp(
            60 * agreeing_frames / 4
            + 40 * confirmed_frames / 4
        )

        side_momentum = sign * (
            moves[5] + moves[15]
        )

        side_acceleration = sign * acceleration

        momentum_scale = max(
            n("atr_percent") * 10,
            0.000001,
        )

        momentum_score = unit_5_v2_clamp(
            45 * max(
                0,
                min(1, side_momentum / momentum_scale),
            )
            + 35 * max(
                0,
                min(1, side_acceleration),
            )
            + 20 * own_votes / 3
        )

        volatility_score = unit_5_v2_clamp(
            50 + 100 * (atr_expansion - 1)
        )

        volume_score = (
            unit_5_v2_clamp(
                100 * volume_ratio
                / minimum_volume_ratio
            )
            if volume_available
            else 50.0
        )

        target = targets.get(side)

        if not isinstance(target, dict):
            raise RuntimeError(
                "UNIT 5 MISSING TARGET " + side
            )

        tp1_move = unit_5_v2_number(
            target.get("tp1_move_pct"),
            "TP1 MOVE",
            0,
        )

        tp2_move = unit_5_v2_number(
            target.get("tp2_move_pct"),
            "TP2 MOVE",
            0,
        )

        atr1h = unit_5_v2_number(
            timeframes["1h"].get("atr14"),
            "ATR1H",
            0.000000001,
        )

        tp1_atr1h = (
            live_price * tp1_move / 100
        ) / atr1h

        tp2_atr1h = (
            live_price * tp2_move / 100
        ) / atr1h

        reach_score = unit_5_v2_clamp(
            100 * max(
                0,
                1 - tp2_atr1h
                / (2 * tp2_distance_limit),
            )
        )

        timing_score = unit_5_v2_clamp(
            100
            - 55 * min(
                1,
                extension_atr / extension_limit,
            )
            + 0.15 * pressure_advantage
        )

        cost_coverage = (
            tp1_move
            / max(estimated_cost_pct, 0.000001)
        )

        cost_score = unit_5_v2_clamp(
            100 * min(
                1,
                cost_coverage / 3,
            )
        )

        components = {
            "trend": trend_score,
            "reach": reach_score,
            "momentum": momentum_score,
            "volatility": volatility_score,
            "volume": volume_score,
            "timing": timing_score,
            "cost": cost_score,
        }

        total_score = sum(
            weights[key] * components[key] / 100
            for key in weights
        )

        # ================================================
        # 5.7 PROGRESSIVE DEVELOPMENTAL PHASE
        # ================================================

        if analysis.get(
            "breakout_confirmed_" + side.lower()
        ) is True:

            phase = "BREAKOUT"

        elif analysis.get(
            "breakout_developing_" + side.lower()
        ) is True:

            phase = "DEVELOPING_BREAKOUT"

        elif analysis.get(
            "structure_developing_" + side.lower()
        ) is True:

            phase = "STRUCTURE"

        elif (
            own_pressure >= early_pressure_min
            and own_votes >= 1
        ):

            phase = "EARLY_SCALP"

        else:

            phase = "BUILDUP"

        # ================================================
        # 5.8 TWO DISTINCT QUALIFICATION ROUTES
        # ================================================

        cost_pass = (
            tp1_move > estimated_cost_pct
            and tp2_move > tp1_move
        )

        directional_evidence = (
            own_votes >= 2
            and side_momentum > 0
        )

        volume_pass = (
            volume_available
            and volume_ratio >= minimum_volume_ratio
        )

        established_route = bool(
            total_score >= established_score_min
            and own_pressure
            >= established_pressure_min
            and pressure_advantage
            >= established_advantage_min
            and agreeing_frames
            >= established_mtf_min
            and directional_evidence
            and extension_atr <= extension_limit
            and tp2_atr1h <= tp2_distance_limit
            and cost_pass
            and phase in (
                "STRUCTURE",
                "DEVELOPING_BREAKOUT",
                "BREAKOUT",
            )
        )

        # Early route accepts a developing directional
        # impulse without requiring a fully confirmed
        # EMA structure or breakout.
        #
        # It still requires price direction, momentum,
        # cost room and conservative extension checks.

        early_route = bool(
            total_score >= early_score_min
            and own_pressure >= early_pressure_min
            and pressure_advantage
            >= early_advantage_min
            and agreeing_frames >= early_mtf_min
            and own_votes >= 2
            and side_momentum > 0
            and (
                side_acceleration >= early_momentum_min
                or (
                    sign * moves[1] > 0
                    and sign * moves[5] > 0
                )
            )
            and extension_atr
            <= early_extension_limit
            and tp2_atr1h <= early_tp2_limit
            and cost_pass
            and (
                not early_require_volume
                or volume_pass
            )
        )

        if established_route:

            route = "ESTABLISHED_TREND"
            qualified = True

        elif early_route:

            route = "EARLY_TRANSITION"
            qualified = True

        else:

            route = "NONE"
            qualified = False

        failures = []

        if own_pressure < early_pressure_min:
            failures.append("PRESSURE_BELOW_EARLY_MIN")

        if pressure_advantage < early_advantage_min:
            failures.append("PRESSURE_ADVANTAGE_WEAK")

        if agreeing_frames < early_mtf_min:
            failures.append("MTF_ALIGNMENT_WEAK")

        if not directional_evidence:
            failures.append("DIRECTIONAL_MOMENTUM_WEAK")

        if side_acceleration < early_momentum_min:
            failures.append("ACCELERATION_NOT_CONFIRMED")

        if extension_atr > early_extension_limit:
            failures.append("PRICE_OVEREXTENDED")

        if tp2_atr1h > early_tp2_limit:
            failures.append("TP2_DISTANCE_HIGH")

        if not cost_pass:
            failures.append("TARGET_COST_COVERAGE_FAILED")

        if not volume_available:
            failures.append("VOLUME_UNAVAILABLE")

        if volume_available and not volume_pass:
            failures.append("LOW_RELATIVE_VOLUME")

        if total_score < early_score_min:
            failures.append("ENTRY_SCORE_BELOW_EARLY_MIN")

        scored[side] = {
            "score": round(total_score, 3),
            "components": {
                k: round(v, 3)
                for k, v in components.items()
            },
            "pressure": own_pressure,
            "opposite_pressure": opposite_pressure,
            "pressure_advantage": pressure_advantage,
            "agreeing_timeframes": agreeing_frames,
            "confirmed_timeframes": confirmed_frames,
            "direction_votes": own_votes,
            "momentum": side_momentum,
            "acceleration": side_acceleration,
            "phase": phase,
            "entry_route": route,
            "qualified": qualified,
            "early_route_pass": early_route,
            "established_route_pass": established_route,
            "tp1_move_pct": tp1_move,
            "tp2_move_pct": tp2_move,
            "tp1_atr1h": tp1_atr1h,
            "tp2_atr1h": tp2_atr1h,
            "cost_coverage": cost_coverage,
            "volume_pass": volume_pass,
            "risk_factors": failures,
        }

    # ========================================================
    # 5.9 SELECT QUALIFIED DIRECTION
    #
    # PRESERVE BEST CANDIDATE EVEN IF REJECTED.
    # ========================================================

    ranking = sorted(
        ("LONG", "SHORT"),
        key=lambda side: (
            scored[side]["score"],
            scored[side]["pressure_advantage"],
        ),
        reverse=True,
    )

    best_side = ranking[0]
    best_record = scored[best_side]

    qualified_sides = [
        side
        for side in ranking
        if scored[side]["qualified"]
    ]

    if len(qualified_sides) == 2:
        # Conflicting qualified signals must not
        # authorize a new entry.
        qualified_sides = []
        conflict = True
    else:
        conflict = False

    selected_side = (
        qualified_sides[0]
        if qualified_sides
        else "NONE"
    )

    selected_record = (
        scored[selected_side]
        if selected_side != "NONE"
        else None
    )

    qualified = selected_record is not None

    direction = (
        selected_side if qualified else "NONE"
    )

    def mode_of(phase):
        if "BREAKOUT" in phase:
            return "BREAKOUT"
        if "STRUCTURE" in phase:
            return "STRUCTURE"
        return "SCALP"

    candidate_mode = (
        mode_of(selected_record["phase"])
        if qualified
        else "NONE"
    )

    active_mode = (
        candidate_mode if qualified
        else "NONE"
    )

    candidate_stage = (
        "QUALIFIED"
        if qualified
        else "DEVELOPING"
        if best_record["score"] >= early_score_min
        else "REJECTED"
    )

    reason = (
        "ADAPTIVE_" + selected_record["entry_route"]
        if qualified
        else "CONFLICTING_QUALIFIED_DIRECTIONS"
        if conflict
        else "BEST_CANDIDATE_NOT_YET_QUALIFIED"
    )

    best_mode = mode_of(best_record["phase"])

    # ========================================================
    # 5.10 PRESERVE ORIGINAL 42-FIELD CANDIDATE
    # ========================================================

    ema_direction = unit_5_v2_direction(
        ema19 - ema50
    )

    legacy_candidate = {

        "symbol": symbol,
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": reason,

        "live_mark_price": live_price,
        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,
        "ema19_50_separation_pct": separation,
        "ema_structure": analysis["ema_structure"],
        "ema_direction": ema_direction,

        "momentum_direction":
            unit_5_v2_direction(moves[1]),

        "direction_agreement": bool(
            qualified
            and direction == analysis[
                "direction_evidence"
            ]
        ),

        "short_term_move_pct": short_move,
        "absolute_short_term_move_pct":
            abs(short_move),

        "previous_close": previous_close,
        "latest_close": latest_close,

        "price_above_ema19": live_price > ema19,
        "price_above_ema50": live_price > ema50,
        "price_above_ema200": live_price > ema200,

        "latest_close_above_previous":
            latest_close > previous_close,

        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "momentum_1m_direction":
            unit_5_v2_direction(moves[1]),

        "momentum_5m_direction":
            unit_5_v2_direction(moves[5]),

        "momentum_15m_direction":
            unit_5_v2_direction(moves[15]),

        "momentum_30m_direction":
            unit_5_v2_direction(moves[30]),

        "momentum_60m_direction":
            unit_5_v2_direction(moves[60]),

        "momentum_120m_direction":
            unit_5_v2_direction(moves[120]),

        "scalp_direction":
            direction if (
                candidate_mode == "SCALP"
            ) else "NONE",

        "scalp_move_pct": moves[1],
        "scalp_1m_support": abs(moves[1]),

        "structure_direction":
            direction if (
                candidate_mode == "STRUCTURE"
            ) else "NONE",

        "structure_move_pct": moves[15],

        "breakout_direction":
            direction if (
                candidate_mode == "BREAKOUT"
            ) else "NONE",

        "breakout_move_pct": moves[5],
        "breakout_fast_support": abs(moves[5]),
    }

    if len(legacy_candidate) != 42:
        raise RuntimeError(
            "UNIT 5 LEGACY 42-FIELD CONTRACT FAILED"
        )

    candidate = dict(legacy_candidate)

    # ========================================================
    # 5.11 EXTENDED UNIT 6 HANDOVER
    # ========================================================

    selected_votes = (
        selected_record["direction_votes"]
        if qualified else 0
    )

    selected_extension_pass = (
        extension_atr <= extension_limit
    )

    candidate.update({

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing":
            flag("higher_mode_developing"),

        "breakout_candidate": any((
            flag("breakout_confirmed_long"),
            flag("breakout_confirmed_short"),
            flag("breakout_developing_long"),
            flag("breakout_developing_short"),
        )),

        "structure_candidate": any((
            flag("structure_developing_long"),
            flag("structure_developing_short"),
        )),

        "breakout_ready": bool(
            qualified and candidate_mode == "BREAKOUT"
        ),

        "structure_ready": bool(
            qualified and candidate_mode == "STRUCTURE"
        ),

        "scalp_ready": bool(
            qualified and candidate_mode == "SCALP"
        ),

        "sideways_context":
            flag("sideways_candidate"),

        "direction_evidence":
            analysis["direction_evidence"],

        "scalp_quality_minimum":
            established_score_min,

        "scalp_price_weight_percent":
            weights["timing"],

        "estimated_round_trip_fee_pct":
            estimated_cost_pct,

        "scalp_minimum_fee_coverage":
            selected_record["cost_coverage"]
            if qualified else None,

        "candle_data_fresh": True,
        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,

        "strategy_evidence_version":
            "U5_HYBRID_ADJUSTABLE_V3",

        "unit_4_evidence_version":
            "U4_HYBRID_V2",

        "classification_revision":
            "UNIVERSAL_ADAPTIVE_V2",

        "candidate_protected": bool(
            candidate_stage == "DEVELOPING"
        ),

        "candidate_age_seconds": age_seconds,

        "classification_source":
            "UNIT5_ADAPTIVE_V2",

        "original_unit5_qualified": qualified,
        "original_unit5_mode": candidate_mode,
        "original_unit5_direction": direction,
        "original_unit5_reason": reason,

        "original_hybrid_conflict": conflict,

        "optimization_version":
            "UNIT5_ADAPTIVE_V2",

        "hybrid_structure_qualified": bool(
            qualified and candidate_mode == "STRUCTURE"
        ),

        "hybrid_breakout_qualified": bool(
            qualified and candidate_mode == "BREAKOUT"
        ),

        "structure_direction_votes": selected_votes,

        "structure_extension_atr": extension_atr,

        "structure_extension_pass":
            selected_extension_pass,

        "structure_momentum_agreement": bool(
            qualified and unit_5_v2_matches(
                moves[15], direction
            )
        ),

        "breakout_confirmation_votes": selected_votes,

        "developing_breakout_direction":
            "LONG"
            if flag("breakout_developing_long")
            else "SHORT"
            if flag("breakout_developing_short")
            else "NONE",

        "developing_structure_direction":
            "LONG"
            if flag("structure_developing_long")
            else "SHORT"
            if flag("structure_developing_short")
            else "NONE",

        "scalp_preliminary": bool(
            qualified and candidate_mode == "SCALP"
        ),

        "qualification_tuning_revision":
            "UNIT5_UNIVERSAL_ADAPTIVE_V2",

        "structure_ema_alignment_mode":
            analysis.get(
                "structure_ema_alignment_mode", "EARLY"
            ),

        "structure_trend_direction":
            analysis.get(
                "structure_trend_direction", "NONE"
            ),

        "structure_votes_pass":
            selected_votes >= 2,

        "structure_momentum_pass": bool(
            qualified and unit_5_v2_matches(
                moves[15], direction
            )
        ),

        "breakout_votes_pass":
            selected_votes >= 2,

        "breakout_momentum_pass": bool(
            qualified and unit_5_v2_matches(
                moves[5], direction
            )
        ),

        "scalp_preliminary_ema_min_pct":
            analysis.get(
                "scalp_preliminary_ema_min_pct"
            ),

        "scalp_preliminary_move_min_pct":
            analysis.get(
                "scalp_preliminary_move_min_pct"
            ),

        "scalp_sideways_required":
            scalp_cfg.get(
                "require_sideways_market", True
            ),

        "scalp_sideways_pass":
            flag("sideways_candidate"),

        "scalp_direction_candidate":
            direction
            if candidate_mode == "SCALP"
            else "NONE",

        "scalp_quality_pending_unit6": bool(
            not qualified
            and best_mode == "SCALP"
            and candidate_stage == "DEVELOPING"
        ),

        # ====================================================
        # NEW ADAPTIVE V2 EVIDENCE
        # ====================================================

        "market_regime": regime,

        "market_progression": {
            side: scored[side]["phase"]
            for side in ("LONG", "SHORT")
        },

        "long_entry_quality": scored["LONG"],
        "short_entry_quality": scored["SHORT"],

        "entry_quality_score":
            selected_record["score"]
            if qualified else 0.0,

        "entry_quality_threshold":
            established_score_min,

        "entry_quality_weights": dict(weights),

        "entry_quality_components":
            selected_record["components"]
            if qualified else {},

        "entry_risk_factors":
            selected_record["risk_factors"]
            if qualified else [],

        "entry_target_reachability": targets,

        "entry_target_probability_verified":
            False,

        "entry_route":
            selected_record["entry_route"]
            if qualified else "NONE",

        "best_developing_direction":
            best_side,

        "best_developing_mode":
            best_mode,

        "best_developing_score":
            best_record["score"],

        "best_developing_phase":
            best_record["phase"],

        "best_developing_risk_factors":
            list(best_record["risk_factors"]),

        "early_entry_threshold":
            early_score_min,

        "established_entry_threshold":
            established_score_min,

        "early_entry_route_available":
            True,

        "established_entry_route_available":
            True,

        "conversion_evidence": {

            "market_regime": regime,

            "long_pressure": long_pressure,
            "short_pressure": short_pressure,

            "long_score":
                scored["LONG"]["score"],

            "short_score":
                scored["SHORT"]["score"],

            "potential_long_to_short": bool(
                scored["SHORT"]["qualified"]
                and short_pressure > long_pressure
            ),

            "potential_short_to_long": bool(
                scored["LONG"]["qualified"]
                and long_pressure > short_pressure
            ),

            "reversal_confirmed_for_position":
                False,

            "open_position_verified": False,

            "requires_position_reconciliation":
                True,

            "hedge_execution_authorized": False,
        },

        "initial_entry_only": True,

        "position_management_independent":
            True,

        "hedge_stage_execution_authorized":
            False,

        "backup_execution_authorized":
            False,

        "tp_execution_authorized": False,

        "unit15_diagnostic_input": {

            "symbol": symbol,
            "market_time_ms": market_time_ms,

            "market_regime": regime,

            "qualified": qualified,
            "candidate_mode": candidate_mode,
            "candidate_stage": candidate_stage,

            "selected_direction": direction,

            "best_developing_direction": best_side,
            "best_developing_mode": best_mode,

            "best_developing_score":
                best_record["score"],

            "entry_route":
                selected_record["entry_route"]
                if qualified else "NONE",

            "long_score":
                scored["LONG"]["score"],

            "short_score":
                scored["SHORT"]["score"],

            "weights": dict(weights),

            "early_threshold": early_score_min,

            "established_threshold":
                established_score_min,

            "long_risk_factors":
                scored["LONG"]["risk_factors"],

            "short_risk_factors":
                scored["SHORT"]["risk_factors"],

            "target_reachability": targets,

            "trade_outcome_classification":
                "PENDING_TRADE_HISTORY",
        },
    })

    # ========================================================
    # 5.12 SAFETY CHECK
    # ========================================================

    if qualified and (
        direction not in ("LONG", "SHORT")
        or candidate_mode not in (
            "SCALP", "STRUCTURE", "BREAKOUT"
        )
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFIED STATE INVALID"
        )

    if (
        candidate["trade_authorized"] is not False
        or candidate["order_payload_created"] is not False
        or candidate["read_only"] is not True
    ):
        raise RuntimeError(
            "UNIT 5 WRITE SAFETY FAILED"
        )

    # ========================================================
    # 5.13 RENDER LOGS
    # ========================================================

    print(
        "UNIT 5 SYMBOL =", symbol,
        flush=True,
    )

    print(
        "UNIT 5 MARKET REGIME =", regime,
        flush=True,
    )

    for side in ("LONG", "SHORT"):

        data = scored[side]

        print(
            "UNIT 5", side,
            "ENTRY SCORE =", data["score"],
            flush=True,
        )

        print(
            "UNIT 5", side,
            "PHASE =", data["phase"],
            flush=True,
        )

        print(
            "UNIT 5", side,
            "EARLY ROUTE =", data["early_route_pass"],
            flush=True,
        )

        print(
            "UNIT 5", side,
            "ESTABLISHED ROUTE =",
            data["established_route_pass"],
            flush=True,
        )

        print(
            "UNIT 5", side,
            "RISK FACTORS =", data["risk_factors"],
            flush=True,
        )

        print(
            "UNIT 5", side,
            "TP1/TP2 ATR1H =",
            round(data["tp1_atr1h"], 3),
            round(data["tp2_atr1h"], 3),
            flush=True,
        )

    print(
        "UNIT 5 EARLY THRESHOLD =",
        early_score_min,
        flush=True,
    )

    print(
        "UNIT 5 ESTABLISHED THRESHOLD =",
        established_score_min,
        flush=True,
    )

    print(
        "UNIT 5 BEST DEVELOPING DIRECTION =",
        best_side,
        flush=True,
    )

    print(
        "UNIT 5 BEST DEVELOPING SCORE =",
        best_record["score"],
        flush=True,
    )

    print(
        "UNIT 5 BEST DEVELOPING MODE =",
        best_mode,
        flush=True,
    )

    print(
        "UNIT 5 SELECTED DIRECTION =",
        direction,
        flush=True,
    )

    print(
        "UNIT 5 SELECTED MODE =",
        candidate_mode,
        flush=True,
    )

    print(
        "UNIT 5 ENTRY ROUTE =",
        candidate["entry_route"],
        flush=True,
    )

    print(
        "UNIT 5 CANDIDATE STAGE =",
        candidate_stage,
        flush=True,
    )

    print(
        "UNIT 5 ENTRY QUALIFIED =",
        qualified,
        flush=True,
    )

    print(
        "UNIT 5 QUALIFICATION REASON =",
        reason,
        flush=True,
    )

    print(
        "UNIT 5 HISTORICAL TP PROBABILITY = UNVERIFIED",
        flush=True,
    )

    print(
        "UNIT 5 ORIGINAL FIELDS =",
        len(legacy_candidate),
        flush=True,
    )

    print(
        "PASS: UNIT 5 V2 ADAPTIVE HANDOVER",
        flush=True,
    )

    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return candidate


# ============================================================
# 5.14 GLOBAL UNIT 6 HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)


# ============================================================
# END COMPLETE UNIVERSAL UNIT 5 V2
# UNIT 6 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# UNIVERSAL WEEX BOT — COMPLETE UNIT 6 V1
# SIGNAL CONTINUITY, CANDIDATE TRACKING, ENTRY GATE
# UNITS 13–14 POSITION MANAGEMENT IS INDEPENDENT
# PUBLIC-DATA / READ-ONLY; NO ORDER SUBMISSION
# ============================================================

import os
import time
import math
import copy


def u6_num(value, label, minimum=None, maximum=None):

    if isinstance(value, bool):
        raise ValueError(
            "UNIT 6 INVALID NUMBER: " + label
        )

    try:
        result = float(value)

    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            "UNIT 6 INVALID NUMBER: " + label
        ) from exc

    if (
        not math.isfinite(result)
        or (
            minimum is not None
            and result < minimum
        )
        or (
            maximum is not None
            and result > maximum
        )
    ):
        raise ValueError(
            "UNIT 6 NUMBER OUT OF RANGE: " + label
        )

    return result


def u6_env(name, default, minimum=None, maximum=None):

    raw = os.getenv(
        name,
        str(default),
    ).strip()

    return u6_num(
        raw if raw else default,
        name,
        minimum,
        maximum,
    )


# ============================================================
# 6.1 VERIFY UNIT 5 V2 AND UNIT 4 V3 HANDOVER
# ============================================================

def u6_snapshot(candidate, analysis, config):

    if not all(
        isinstance(item, dict)
        for item in (
            candidate,
            analysis,
            config,
        )
    ):
        raise RuntimeError(
            "UNIT 6 MISSING HANDOVER"
        )

    symbol = config.get(
        "exchange", {}
    ).get("market_symbol")

    if (
        not symbol
        or symbol != candidate.get("symbol")
        or symbol != analysis.get("symbol")
    ):
        raise RuntimeError(
            "UNIT 6 SYMBOL MISMATCH"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 6 DEMO SAFETY FAILED"
        )

    if (
        candidate.get(
            "classification_revision"
        ) != "UNIVERSAL_ADAPTIVE_V2"
        or candidate.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 6 EXPECTS UNIT 5 V2"
        )

    if (
        candidate.get("trade_authorized") is not False
        or candidate.get(
            "order_payload_created"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 5 SAFETY FAILED"
        )

    if analysis.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 6 UNIT 4 SAFETY FAILED"
        )

    if config.get(
        "safety", {}
    ).get(
        "real_order_submission_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 6 LIVE CASH SAFETY FAILED"
        )

    timestamp = int(
        u6_num(
            analysis.get("exchange_time_ms"),
            "MARKET TIMESTAMP",
            1,
        )
    )

    candidate_ts = int(
        u6_num(
            candidate.get(
                "unit15_diagnostic_input", {}
            ).get("market_time_ms"),
            "CANDIDATE TIMESTAMP",
            1,
        )
    )

    if timestamp != candidate_ts:
        raise RuntimeError(
            "UNIT 6 MIXED SCAN DATA"
        )

    age = (
        time.time() * 1000 - timestamp
    )

    max_age = (
        u6_env(
            "UNIT6_MAX_MARKET_AGE_SECONDS",
            120,
            1,
        ) * 1000
    )

    if age < 0 or age > max_age:
        raise RuntimeError(
            "UNIT 6 STALE DATA"
        )

    return symbol, timestamp


# ============================================================
# 6.2 IN-MEMORY SIGNAL CONTINUITY STATE
#
# WORKS ACROSS SCANS IN SAME PYTHON PROCESS.
# DOES NOT CLAIM PERSISTENCE ACROSS RENDER RESTARTS.
# ============================================================

FRESH_RECONSTRUCTION_UNIT6_STATE = {

    "symbol": None,

    "last_candle_id": None,

    "last_market_time_ms": None,

    "last_fingerprint": None,

    "candidate_direction": "NONE",

    "candidate_mode": "NONE",

    "first_seen_ms": None,

    "last_seen_ms": None,

    "consecutive_observations": 0,

    "qualified_observations": 0,

    "last_outcome": "NONE",
}


# ============================================================
# 6.3 CONTINUITY ENGINE
# ============================================================

def fresh_reconstruction_unit_6(
    candidate=None,
    analysis=None,
    config=None,
    state=None,
    now_ms=None,
):

    if candidate is None:
        candidate = (
            FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
        )

    if analysis is None:
        analysis = (
            FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
        )

    if config is None:
        config = FRESH_RECONSTRUCTION_CONFIG

    if state is None:
        state = FRESH_RECONSTRUCTION_UNIT6_STATE

    print("=" * 80, flush=True)

    print(
        "UNIVERSAL WEEX UNIT 6 V1 START",
        flush=True,
    )

    symbol, market_time_ms = u6_snapshot(
        candidate,
        analysis,
        config,
    )

    candle_id = int(
        u6_num(
            analysis.get(
                "latest_open_time_ms"
            ),
            "CANDLE ID",
            1,
        )
    )

    if now_ms is None:
        now_ms = int(time.time() * 1000)

    max_life_ms = int(
        u6_env(
            "UNIT6_CANDIDATE_MAX_AGE_SECONDS",
            600,
            5,
        ) * 1000
    )

    min_observations = int(
        u6_env(
            "UNIT6_MIN_QUALIFIED_OBSERVATIONS",
            2,
            1,
            20,
        )
    )

    track_developing = (
        os.getenv(
            "UNIT6_TRACK_DEVELOPING",
            "TRUE",
        ).strip().upper()
        not in (
            "FALSE",
            "0",
            "NO",
            "OFF",
        )
    )

    qualified = candidate.get("qualified")

    if type(qualified) is not bool:
        raise RuntimeError(
            "UNIT 6 INVALID QUALIFIED FLAG"
        )

    best_side = candidate.get(
        "best_developing_direction"
    )

    best_mode = candidate.get(
        "best_developing_mode"
    )

    direction = candidate.get("direction")

    mode = candidate.get("active_mode")

    if best_side not in (
        "LONG",
        "SHORT",
    ):
        raise RuntimeError(
            "UNIT 6 INVALID BEST SIDE"
        )

    if best_mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        raise RuntimeError(
            "UNIT 6 INVALID BEST MODE"
        )

    if direction not in (
        "LONG",
        "SHORT",
        "NONE",
    ):
        raise RuntimeError(
            "UNIT 6 INVALID DIRECTION"
        )

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
        "NONE",
    ):
        raise RuntimeError(
            "UNIT 6 INVALID MODE"
        )

    if qualified and (
        direction == "NONE"
        or mode == "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 QUALIFICATION INCONSISTENCY"
        )

    if not qualified and (
        direction != "NONE"
        or mode != "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 UNQUALIFIED DIRECTION LEAK"
        )

    # ========================================================
    # 6.4 RETAIN DEVELOPING SIGNAL WITHOUT
    # OVERRIDING THE LATEST UNIT 5 DECISION
    # ========================================================

    proposed_side = (
        direction
        if qualified
        else best_side
        if track_developing
        else "NONE"
    )

    proposed_mode = (
        mode
        if qualified
        else best_mode
        if track_developing
        else "NONE"
    )

    fingerprint = (
        symbol,
        candle_id,
        proposed_side,
        proposed_mode,
    )

    s = copy.deepcopy(state)

    if s.get("symbol") not in (
        None,
        symbol,
    ):
        s = {
            "symbol": symbol,
        }

    previous_ms = s.get(
        "last_market_time_ms"
    )

    if (
        previous_ms is not None
        and market_time_ms < previous_ms
    ):
        raise RuntimeError(
            "UNIT 6 TIME MOVED BACKWARDS"
        )

    duplicate_candle = (
        s.get("last_candle_id")
        == candle_id
    )

    same_candidate = (
        s.get("candidate_direction")
        == proposed_side
    )

    expired = bool(
        s.get("first_seen_ms") is not None
        and now_ms - s["first_seen_ms"]
        > max_life_ms
    )

    changed = bool(
        s.get("candidate_direction")
        not in (
            None,
            "NONE",
            proposed_side,
        )
    )

    if proposed_side == "NONE":

        s.update(
            candidate_direction="NONE",
            candidate_mode="NONE",
            first_seen_ms=None,
            last_seen_ms=now_ms,
            consecutive_observations=0,
            qualified_observations=0,
        )

    elif not same_candidate or expired:

        s.update(
            candidate_direction=proposed_side,
            candidate_mode=proposed_mode,
            first_seen_ms=now_ms,
            last_seen_ms=now_ms,
            consecutive_observations=1,
            qualified_observations=(
                1 if qualified else 0
            ),
        )

    else:

        # Developmental mode changes preserve
        # directional continuity.
        #
        # SCALP -> STRUCTURE -> BREAKOUT
        # does not become a new trading cycle.

        s["candidate_mode"] = proposed_mode

        s["last_seen_ms"] = now_ms

        if not duplicate_candle:

            s["consecutive_observations"] = (
                int(
                    s.get(
                        "consecutive_observations",
                        0,
                    )
                ) + 1
            )

            s["qualified_observations"] = (
                int(
                    s.get(
                        "qualified_observations",
                        0,
                    )
                ) + 1
                if qualified else 0
            )

        elif not qualified:

            s["qualified_observations"] = 0

    # ========================================================
    # 6.5 INITIAL ENTRY CONTINUITY GATE
    # ========================================================

    continuity_pass = bool(
        qualified
        and s["qualified_observations"]
        >= min_observations
        and not expired
        and not changed
    )

    if continuity_pass:

        status = (
            "READY_FOR_DOWNSTREAM_CHECKS"
        )

    elif qualified:

        status = (
            "QUALIFIED_AWAITING_CONTINUITY"
        )

    else:

        status = (
            "DEVELOPING_OBSERVATION"
        )

    s.update(
        symbol=symbol,
        last_candle_id=candle_id,
        last_market_time_ms=market_time_ms,
        last_fingerprint=fingerprint,
        last_outcome=status,
    )

    state.clear()
    state.update(s)

    # ========================================================
    # 6.6 HANDOVER TO UNIT 7
    #
    # QUALIFIED = CONTINUITY PASSED ONLY.
    # IT IS NOT AN EXECUTABLE ORDER AUTHORIZATION.
    # ========================================================

    result = {

        "symbol": symbol,

        "unit5_qualified": qualified,

        "unit5_mode": mode,

        "unit5_direction": direction,

        "candidate_mode": (
            mode if continuity_pass
            else "NONE"
        ),

        "active_mode": (
            mode if continuity_pass
            else "NONE"
        ),

        "direction": (
            direction if continuity_pass
            else "NONE"
        ),

        "qualified": continuity_pass,

        "entry_continuity_verified":
            continuity_pass,

        "entry_authorized": False,

        "trade_authorized": False,

        "order_payload_created": False,

        "read_only": True,

        "entry_status": status,

        "entry_reason": candidate.get(
            "qualification_reason"
        ),

        "developing_candidate": {

            "direction": proposed_side,

            "mode": proposed_mode,

            "score": candidate.get(
                "best_developing_score"
            ),

            "stage": candidate.get(
                "candidate_stage"
            ),

            "risk_factors": list(
                candidate.get(
                    "best_developing_risk_factors",
                    [],
                )
            ),

            "first_seen_ms":
                s.get("first_seen_ms"),

            "consecutive_observations":
                s.get(
                    "consecutive_observations"
                ),

            "qualified_observations":
                s.get(
                    "qualified_observations"
                ),

            "duplicate_candle":
                duplicate_candle,

            "expired": expired,

            "direction_changed": changed,
        },

        "unit5_snapshot": copy.deepcopy(
            candidate
        ),

        "market_time_ms": market_time_ms,

        "market_candle_id": candle_id,

        # ====================================================
        # ABSOLUTE MANAGEMENT INDEPENDENCE
        # ====================================================

        "position_management": {

            "requires_verified_exchange_position":
                True,

            "units_13_14_independent_of_entry_signal":
                True,

            "units_13_14_independent_of_bot_mode":
                True,

            "tp_management_blocked_by_unit6":
                False,

            "dynamic_break_even_blocked_by_unit6":
                False,

            "trailing_profit_blocked_by_unit6":
                False,

            "atr_hedge_recovery_blocked_by_unit6":
                False,

            "b1_b5_backup_blocked_by_unit6":
                False,

            "execution_authorized_by_unit6":
                False,
        },

        "diagnostic": {

            "qualification_snapshot":
                copy.deepcopy(
                    candidate.get(
                        "unit15_diagnostic_input",
                        {},
                    )
                ),

            "continuity_status": status,

            "duplicate_candle":
                duplicate_candle,

            "expired": expired,

            "direction_changed": changed,

            "reason": candidate.get(
                "qualification_reason"
            ),
        },

        "unit6_revision":
            "UNIVERSAL_CONTINUITY_V1",
    }

    # ========================================================
    # 6.7 RENDER VERIFICATION LOGS
    # ========================================================

    print(
        "UNIT 6 SYMBOL =",
        symbol,
        flush=True,
    )

    print(
        "UNIT 6 UNIT5 QUALIFIED =",
        qualified,
        flush=True,
    )

    print(
        "UNIT 6 BEST DEVELOPING =",
        proposed_side,
        proposed_mode,
        flush=True,
    )

    print(
        "UNIT 6 DUPLICATE CANDLE =",
        duplicate_candle,
        flush=True,
    )

    print(
        "UNIT 6 QUALIFIED OBSERVATIONS =",
        s["qualified_observations"],
        "/",
        min_observations,
        flush=True,
    )

    print(
        "UNIT 6 ENTRY STATUS =",
        status,
        flush=True,
    )

    print(
        "UNIT 6 ENTRY CONTINUITY VERIFIED =",
        continuity_pass,
        flush=True,
    )

    print(
        "UNIT 6 TP MANAGEMENT INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 6 ATR HEDGE RECOVERY INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 6 B1-B5 BACKUP INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 6 BOT_MODE APPLIES ONLY TO UNIT 12 ENTRIES = True",
        flush=True,
    )

    print(
        "UNIT 6 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 6.8 GLOBAL HANDOVER TO UNIT 7
# ============================================================

FRESH_RECONSTRUCTION_UNIT6_RESULT = (
    fresh_reconstruction_unit_6()
)


# ============================================================
# END COMPLETE UNIVERSAL UNIT 6 V1
# UNIT 7 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# UNIT 6 V1 — CONTINUITY TEST EXTENSION
# INSERT AFTER UNIT 6
# NO EXCHANGE WRITES
# ============================================================

def fresh_reconstruction_unit_6_continuity_test():

    import copy
    import time

    original_candidate = copy.deepcopy(
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )

    original_analysis = copy.deepcopy(
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )

    config = copy.deepcopy(
        FRESH_RECONSTRUCTION_CONFIG
    )

    state = {
        "symbol": None,
        "last_candle_id": None,
        "last_market_time_ms": None,
        "last_fingerprint": None,
        "candidate_direction": "NONE",
        "candidate_mode": "NONE",
        "first_seen_ms": None,
        "last_seen_ms": None,
        "consecutive_observations": 0,
        "qualified_observations": 0,
        "last_outcome": "NONE",
    }

    now = int(time.time() * 1000)

    base_candle = (
        now // 60000
    ) * 60000 - 120000

    def make_scan(
        candle_id,
        side,
        qualified,
    ):

        candidate = copy.deepcopy(
            original_candidate
        )

        analysis = copy.deepcopy(
            original_analysis
        )

        market_time = now - 1000

        analysis["exchange_time_ms"] = (
            market_time
        )

        analysis["latest_open_time_ms"] = (
            candle_id
        )

        candidate[
            "unit15_diagnostic_input"
        ]["market_time_ms"] = market_time

        candidate["qualified"] = qualified

        candidate["direction"] = (
            side if qualified else "NONE"
        )

        candidate["active_mode"] = (
            "SCALP" if qualified else "NONE"
        )

        candidate["best_developing_direction"] = side
        candidate["best_developing_mode"] = "SCALP"

        candidate["candidate_stage"] = (
            "QUALIFIED"
            if qualified
            else "DEVELOPING"
        )

        return candidate, analysis

    scenarios = [
        ("FIRST_QUALIFICATION", base_candle, "SHORT", True, False),
        ("DUPLICATE_CANDLE", base_candle, "SHORT", True, False),
        ("SECOND_CANDLE", base_candle + 60000, "SHORT", True, True),
        ("QUALIFICATION_LOST", base_candle + 120000, "SHORT", False, False),
        ("DIRECTION_CHANGED", base_candle + 180000, "LONG", True, False),
    ]

    passed = 0
    failed = 0

    for (
        name,
        candle_id,
        side,
        qualified,
        expected,
    ) in scenarios:

        candidate, analysis = make_scan(
            candle_id,
            side,
            qualified,
        )

        result = fresh_reconstruction_unit_6(
            candidate=candidate,
            analysis=analysis,
            config=config,
            state=state,
            now_ms=now,
        )

        actual = result[
            "entry_continuity_verified"
        ]

        success = actual is expected

        if success:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 6 CONTINUITY TEST =",
            name,
            "| EXPECTED =", expected,
            "| ACTUAL =", actual,
            "| RESULT =",
            "PASS" if success else "FAIL",
            flush=True,
        )

    print(
        "UNIT 6 CONTINUITY TESTS PASSED =",
        passed,
        flush=True,
    )

    print(
        "UNIT 6 CONTINUITY TESTS FAILED =",
        failed,
        flush=True,
    )

    if failed:
        raise RuntimeError(
            "UNIT 6 CONTINUITY VALIDATION FAILED"
        )

    print(
        "UNIT 6 TWO-CANDLE CONTINUITY = PASS",
        flush=True,
    )

    print(
        "UNIT 6 CONTINUITY TEST EXCHANGE WRITE = NONE",
        flush=True,
    )

    return True


if os.getenv(
    "UNIT6_CONTINUITY_TEST",
    "OFF",
).strip().upper() == "ON":

    fresh_reconstruction_unit_6_continuity_test()


# ============================================================
# END UNIT 6 CONTINUITY TEST EXTENSION
# ============================================================



# ============================================================
# UNIVERSAL WEEX — COMPLETE UNIT 7 V2
#
# PRIMARY POSITION SIZING: USDT
# INITIAL MARGIN: ENTRY_MARGIN_USDT
# SEPARATE LONG / SHORT LEVERAGE
# VERIFIED PUBLIC FUTURES CONTRACT RULES
# EXACT 10 / 20 / 70 TP QUANTITY ALLOCATION
# EXACT 50 / 50 STAGED HEDGE QUANTITY
# MINIMUM REQUIRED USDT MARGIN CALCULATION
# NO AUTOMATIC INCREASE OF USER MARGIN
#
# UNIT 6 -> UNIT 7 -> UNIT 8
# READ ONLY — NO EXCHANGE ORDER SUBMISSION
# ============================================================

import os
import json
import time
import urllib.parse
import urllib.request

from decimal import (
    Decimal,
    ROUND_DOWN,
    ROUND_CEILING,
)


# ============================================================
# 7.1 DECIMAL / ENVIRONMENT HELPERS
# ============================================================

def u7_v2_decimal(
    value,
    name,
    positive=False,
):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT7 INVALID BOOLEAN: " + name
        )

    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "UNIT7 INVALID NUMBER: " + name
        ) from exc

    if not result.is_finite():
        raise RuntimeError(
            "UNIT7 NONFINITE NUMBER: " + name
        )

    if positive and result <= 0:
        raise RuntimeError(
            "UNIT7 NONPOSITIVE NUMBER: " + name
        )

    return result


def u7_v2_text(value):
    return format(value, "f")


def u7_v2_env(
    name,
    default,
    positive=True,
):

    raw = os.getenv(name, "").strip()

    return u7_v2_decimal(
        raw if raw else default,
        name,
        positive=positive,
    )


def u7_v2_floor(value):
    return int(
        value.to_integral_value(
            rounding=ROUND_DOWN
        )
    )


def u7_v2_ceil(value):
    return int(
        value.to_integral_value(
            rounding=ROUND_CEILING
        )
    )


# ============================================================
# 7.2 PUBLIC FUTURES CONTRACT INFORMATION
# ============================================================

def u7_v2_exchange_info(symbol):

    parameters = urllib.parse.urlencode({
        "symbol": symbol,
    })

    url = (
        "https://api-contract.weex.com"
        "/capi/v3/market/exchangeInfo?"
        + parameters
    )

    timeout = float(
        u7_v2_env(
            "UNIT7_HTTP_TIMEOUT_SECONDS",
            "15",
        )
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
        },
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:

        if response.status != 200:
            raise RuntimeError(
                "UNIT7 EXCHANGE INFO HTTP FAILED"
            )

        payload = json.loads(
            response.read(
                2000000
            ).decode("utf-8")
        )

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT7 INVALID EXCHANGE PAYLOAD"
        )

    entries = payload.get("symbols")

    if not isinstance(entries, list):
        raise RuntimeError(
            "UNIT7 MISSING CONTRACT LIST"
        )

    matches = [
        entry
        for entry in entries
        if (
            isinstance(entry, dict)
            and entry.get("symbol") == symbol
        )
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "UNIT7 CONTRACT NOT FOUND OR DUPLICATED"
        )

    data = matches[0]

    quantity_precision = data.get(
        "quantityPrecision"
    )

    price_precision = data.get(
        "pricePrecision"
    )

    for name, precision in (
        ("QUANTITY", quantity_precision),
        ("PRICE", price_precision),
    ):

        if (
            isinstance(precision, bool)
            or not isinstance(precision, int)
            or not 0 <= precision <= 12
        ):
            raise RuntimeError(
                "UNIT7 INVALID " + name + " PRECISION"
            )

    quantity_step = (
        Decimal(1).scaleb(-quantity_precision)
    )

    price_step = (
        Decimal(1).scaleb(-price_precision)
    )

    minimum = u7_v2_decimal(
        data.get("minOrderSize"),
        "MINIMUM QUANTITY",
        positive=True,
    )

    maximum = u7_v2_decimal(
        data.get("maxOrderSize"),
        "MAXIMUM QUANTITY",
        positive=True,
    )

    market_maximum = u7_v2_decimal(
        data.get("marketOpenLimitSize"),
        "MARKET OPEN MAXIMUM",
        positive=True,
    )

    position_maximum = u7_v2_decimal(
        data.get("maxPositionSize"),
        "POSITION MAXIMUM",
        positive=True,
    )

    contract_value = u7_v2_decimal(
        data.get("contractVal"),
        "CONTRACT VALUE",
        positive=True,
    )

    minimum_leverage = u7_v2_decimal(
        data.get("minLeverage"),
        "MINIMUM LEVERAGE",
        positive=True,
    )

    maximum_leverage = u7_v2_decimal(
        data.get("maxLeverage"),
        "MAXIMUM LEVERAGE",
        positive=True,
    )

    if (
        minimum > maximum
        or minimum_leverage > maximum_leverage
    ):
        raise RuntimeError(
            "UNIT7 INCONSISTENT CONTRACT LIMITS"
        )

    if (
        data.get("quoteAsset") != "USDT"
        or data.get("marginAsset") != "USDT"
        or data.get("contractType") != "PERPETUAL"
    ):
        raise RuntimeError(
            "UNIT7 UNSUPPORTED CONTRACT"
        )

    if data.get("forwardContractFlag") is not True:
        raise RuntimeError(
            "UNIT7 NOT VERIFIED USDT-MARGINED"
        )

    return {

        "symbol": symbol,

        "base_asset": data.get("baseAsset"),
        "quote_asset": data.get("quoteAsset"),
        "margin_asset": data.get("marginAsset"),

        "quantity_precision": quantity_precision,
        "quantity_step": quantity_step,

        "price_precision": price_precision,
        "price_step": price_step,

        "minimum_quantity": minimum,
        "maximum_quantity": maximum,
        "maximum_market_open_quantity":
            market_maximum,

        "maximum_position_quantity":
            position_maximum,

        "contract_value": contract_value,

        "minimum_leverage": minimum_leverage,
        "maximum_leverage": maximum_leverage,

        "status": data.get("status"),

        "source": (
            "WEEX_V3_FUTURES_EXCHANGE_INFO"
        ),

        "public_contract_verified": True,

        # Public contract information does not
        # verify the private demo order interface.
        "demo_contract_verified": False,

        "order_quantity_encoding_verified": False,
    }


# ============================================================
# 7.3 MAIN UNIT 7 V2
# ============================================================

def fresh_reconstruction_unit_7(
    unit6=None,
    config=None,
    market=None,
):

    print("=" * 80, flush=True)

    print(
        "UNIVERSAL WEEX UNIT 7 V2 START",
        flush=True,
    )

    if unit6 is None:
        unit6 = FRESH_RECONSTRUCTION_UNIT6_RESULT

    if config is None:
        config = FRESH_RECONSTRUCTION_CONFIG

    if market is None:
        market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not all(
        isinstance(item, dict)
        for item in (
            unit6,
            config,
            market,
        )
    ):
        raise RuntimeError(
            "UNIT7 INVALID HANDOVER"
        )

    exchange_cfg = config.get("exchange", {})
    leverage_cfg = config.get("leverage", {})
    safety = config.get("safety", {})

    if not all(
        isinstance(x, dict)
        for x in (
            exchange_cfg,
            leverage_cfg,
            safety,
        )
    ):
        raise RuntimeError(
            "UNIT7 INVALID CONFIG STRUCTURE"
        )

    symbol = exchange_cfg.get(
        "market_symbol"
    )

    if (
        not isinstance(symbol, str)
        or not symbol
        or unit6.get("symbol") != symbol
        or market.get("symbol") != symbol
        or unit6.get(
            "unit6_revision"
        ) != "UNIVERSAL_CONTINUITY_V1"
        or unit6.get("read_only") is not True
        or unit6.get("trade_authorized") is not False
        or market.get("read_only") is not True
        or config.get(
            "execution_environment"
        ) != "DEMO"
        or safety.get(
            "real_order_submission_enabled"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT7 SAFETY / SYMBOL GATE FAILED"
        )

    management = unit6.get(
        "position_management", {}
    )

    if not isinstance(management, dict):
        raise RuntimeError(
            "UNIT7 MANAGEMENT CONTRACT INVALID"
        )

    if (
        management.get(
            "units_13_14_independent_of_entry_signal"
        ) is not True
        or management.get(
            "units_13_14_independent_of_bot_mode"
        ) is not True
        or management.get(
            "tp_management_blocked_by_unit6"
        ) is not False
        or management.get(
            "b1_b5_backup_blocked_by_unit6"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT7 MANAGEMENT INDEPENDENCE FAILED"
        )

    price = u7_v2_decimal(
        market.get("price"),
        "MARK PRICE",
        positive=True,
    )

    # ========================================================
    # 7.4 USDT IS THE PRIMARY MARGIN AUTHORITY
    # ========================================================

    margin_usdt = u7_v2_env(
        "ENTRY_MARGIN_USDT",
        "4",
    )

    # The entry margin is never silently increased
    # to achieve minimum contract or TP quantities.

    long_leverage = u7_v2_decimal(
        leverage_cfg.get("long"),
        "LONG LEVERAGE",
        positive=True,
    )

    short_leverage = u7_v2_decimal(
        leverage_cfg.get("short"),
        "SHORT LEVERAGE",
        positive=True,
    )

    # ========================================================
    # 7.5 GET VERIFIED CONTRACT LIMITS
    # ========================================================

    contract = u7_v2_exchange_info(symbol)

    step = contract["quantity_step"]
    minimum = contract["minimum_quantity"]

    maximum = min(
        contract["maximum_quantity"],
        contract["maximum_market_open_quantity"],
        contract["maximum_position_quantity"],
    )

    minimum_steps = u7_v2_ceil(
        minimum / step
    )

    # Require exact 10/20/70 TP allocation.
    # This automatically supports 50/50 halves.
    #
    # The initial size must be a multiple of
    # ten quantity increments.

    minimum_initial_steps = (
        10 * minimum_steps
    )

    minimum_initial_qty = (
        Decimal(minimum_initial_steps) * step
    )

    # ========================================================
    # 7.6 INDEPENDENT LONG / SHORT CALCULATION
    # ========================================================

    plans = {}

    for side, leverage in (
        ("LONG", long_leverage),
        ("SHORT", short_leverage),
    ):

        blocking = []

        leverage_valid = (
            contract["minimum_leverage"]
            <= leverage
            <= contract["maximum_leverage"]
        )

        if not leverage_valid:
            blocking.append(
                "LEVERAGE_OUTSIDE_EXCHANGE_LIMIT"
            )

        # Primary user control:
        # margin_usdt = fixed USDT capital.
        #
        # Leveraged position notional:
        # margin * leverage.

        desired_notional = (
            margin_usdt * leverage
        )

        # WEEX futures market metadata describes
        # order sizes in base-asset units.
        #
        # Do not divide by contractVal again here.
        # The order endpoint encoding is separately
        # verified by later units.

        desired_quantity = (
            desired_notional / price
        )

        desired_steps = u7_v2_floor(
            desired_quantity / step
        )

        executable_steps = (
            desired_steps // 10
        ) * 10

        executable_qty = (
            Decimal(executable_steps) * step
        )

        tp1_steps = (
            executable_steps // 10
        )

        tp2_steps = (
            executable_steps * 2 // 10
        )

        tp3_steps = (
            executable_steps * 7 // 10
        )

        half_steps = (
            executable_steps // 2
        )

        tp1_qty = Decimal(tp1_steps) * step
        tp2_qty = Decimal(tp2_steps) * step
        tp3_qty = Decimal(tp3_steps) * step

        half_qty = (
            Decimal(half_steps) * step
        )

        exact_split_valid = (
            executable_steps
            >= minimum_initial_steps
            and tp1_steps >= minimum_steps
            and tp2_steps >= minimum_steps
            and tp3_steps >= minimum_steps
            and half_steps >= minimum_steps
            and (
                tp1_steps
                + tp2_steps
                + tp3_steps
                == executable_steps
            )
            and (
                half_steps * 2
                == executable_steps
            )
        )

        if not exact_split_valid:
            blocking.append(
                "TP_HEDGE_SPLITS_BELOW_MINIMUM"
            )

        if (
            executable_qty < minimum
            or executable_qty > maximum
        ):
            blocking.append(
                "INITIAL_QUANTITY_OUTSIDE_LIMITS"
            )

        actual_notional = (
            executable_qty * price
        )

        actual_margin = (
            actual_notional / leverage
        )

        if actual_margin > margin_usdt:
            blocking.append(
                "PROPOSED_MARGIN_EXCEEDS_USER_BUDGET"
            )

        # The lowest user-controlled margin that
        # could support exact allocation at the
        # current reference mark price.
        #
        # Does not include account fee reserve,
        # exchange minimum notional or slippage.

        minimum_margin = (
            minimum_initial_qty
            * price
            / leverage
        )

        minimum_notional = (
            minimum_initial_qty * price
        )

        shortfall = max(
            Decimal("0"),
            minimum_margin - margin_usdt,
        )

        plans[side] = {

            "side": side,

            "leverage": u7_v2_text(
                leverage
            ),

            "user_margin_usdt": u7_v2_text(
                margin_usdt
            ),

            "desired_notional_usdt":
                u7_v2_text(
                    desired_notional
                ),

            "desired_base_quantity":
                u7_v2_text(
                    desired_quantity
                ),

            "proposed_quantity":
                u7_v2_text(
                    executable_qty
                ),

            "proposed_quantity_steps":
                executable_steps,

            "proposed_notional_usdt":
                u7_v2_text(
                    actual_notional
                ),

            "effective_margin_usdt":
                u7_v2_text(
                    actual_margin
                ),

            "tp1_quantity":
                u7_v2_text(
                    tp1_qty
                ),

            "tp2_quantity":
                u7_v2_text(
                    tp2_qty
                ),

            "tp3_quantity":
                u7_v2_text(
                    tp3_qty
                ),

            "tp1_notional_usdt":
                u7_v2_text(
                    tp1_qty * price
                ),

            "tp2_notional_usdt":
                u7_v2_text(
                    tp2_qty * price
                ),

            "tp3_notional_usdt":
                u7_v2_text(
                    tp3_qty * price
                ),

            "h1_original_half_quantity":
                u7_v2_text(
                    half_qty
                ),

            "h1_opposite_half_quantity":
                u7_v2_text(
                    half_qty
                ),

            "h2_full_opposite_quantity":
                u7_v2_text(
                    executable_qty
                ),

            "hedge_half_notional_usdt":
                u7_v2_text(
                    half_qty * price
                ),

            "minimum_initial_quantity":
                u7_v2_text(
                    minimum_initial_qty
                ),

            "minimum_required_notional_usdt":
                u7_v2_text(
                    minimum_notional
                ),

            "minimum_required_margin_usdt":
                u7_v2_text(
                    minimum_margin
                ),

            "margin_shortfall_usdt":
                u7_v2_text(
                    shortfall
                ),

            "quantity_plan_valid":
                len(blocking) == 0,

            "exact_tp_split_valid":
                exact_split_valid,

            "exact_hedge_split_valid":
                (
                    executable_steps > 0
                    and half_steps >= minimum_steps
                ),

            "blocking_reasons": blocking,
        }

    # ========================================================
    # 7.7 STRICT NEW ENTRY GATE
    # ========================================================

    continuity = (
        unit6.get(
            "entry_continuity_verified"
        ) is True
    )

    direction = unit6.get(
        "direction",
        "NONE",
    )

    if direction not in (
        "LONG",
        "SHORT",
        "NONE",
    ):
        raise RuntimeError(
            "UNIT7 INVALID ENTRY DIRECTION"
        )

    selected = plans.get(direction)

    sizing_valid = bool(
        selected is not None
        and selected["quantity_plan_valid"]
    )

    candidate_ready = bool(
        continuity and sizing_valid
    )

    if not continuity:

        entry_reason = (
            "AWAITING_UNIT6_CONTINUITY"
        )

    elif not sizing_valid:

        entry_reason = (
            "USDT_MARGIN_OR_QUANTITY_INVALID"
        )

    else:

        entry_reason = (
            "SIZING_VALID_ACCOUNT_CHECK_PENDING"
        )

    # ========================================================
    # 7.8 UNIT 8 HANDOVER
    # ========================================================

    result = {

        "symbol": symbol,

        "margin_mode": "FIXED_USDT",

        "initial_margin_coins": None,

        "initial_margin_usdt":
            u7_v2_text(
                margin_usdt
            ),

        "mark_price": u7_v2_text(
            price
        ),

        "selected_direction": direction,

        "long_plan": plans["LONG"],
        "short_plan": plans["SHORT"],

        "contract": {
            key: (
                u7_v2_text(value)
                if isinstance(value, Decimal)
                else value
            )
            for key, value in contract.items()
        },

        "entry_continuity_verified":
            continuity,

        "entry_sizing_valid":
            sizing_valid,

        "candidate_ready_for_account_checks":
            candidate_ready,

        "entry_status_reason":
            entry_reason,

        "demo_contract_eligibility_verified":
            False,

        "account_balance_verified":
            False,

        "free_margin_verified":
            False,

        "exposure_cap_verified":
            False,

        "position_mode_verified":
            False,

        "order_quantity_encoding_verified":
            False,

        "new_entry_order_authorized":
            False,

        "trade_authorized": False,

        "position_management_independent":
            True,

        "tp_management_blocked": False,

        "dynamic_break_even_blocked": False,

        "atr_hedge_recovery_blocked": False,

        "b1_b5_backup_blocked": False,

        "read_only": True,

        "exchange_write": "NONE",

        "unit7_revision":
            "UNIVERSAL_USDT_SIZING_V2",
    }

    # ========================================================
    # 7.9 RENDER VERIFICATION LOGS
    # ========================================================

    print(
        "UNIT 7 SYMBOL =",
        symbol,
        flush=True,
    )

    print(
        "UNIT 7 MARGIN MODE = FIXED_USDT",
        flush=True,
    )

    print(
        "UNIT 7 ENTRY MARGIN USDT =",
        u7_v2_text(
            margin_usdt
        ),
        flush=True,
    )

    print(
        "UNIT 7 MARK PRICE =",
        u7_v2_text(
            price
        ),
        flush=True,
    )

    print(
        "UNIT 7 CONTRACT SOURCE =",
        contract["source"],
        flush=True,
    )

    print(
        "UNIT 7 MINIMUM QUANTITY =",
        u7_v2_text(
            minimum
        ),
        flush=True,
    )

    print(
        "UNIT 7 QUANTITY STEP =",
        u7_v2_text(
            step
        ),
        flush=True,
    )

    print(
        "UNIT 7 CONTRACT VALUE =",
        u7_v2_text(
            contract["contract_value"]
        ),
        flush=True,
    )

    print(
        "UNIT 7 PRICE PRECISION =",
        contract["price_precision"],
        flush=True,
    )

    for side in ("LONG", "SHORT"):

        plan = plans[side]

        print(
            "UNIT 7", side,
            "LEVERAGE =",
            plan["leverage"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "DESIRED NOTIONAL USDT =",
            plan["desired_notional_usdt"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "PROPOSED QUANTITY =",
            plan["proposed_quantity"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "TP1 / TP2 / TP3 QTY =",
            plan["tp1_quantity"],
            plan["tp2_quantity"],
            plan["tp3_quantity"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "TP1 / TP2 / TP3 NOTIONAL USDT =",
            plan["tp1_notional_usdt"],
            plan["tp2_notional_usdt"],
            plan["tp3_notional_usdt"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "HEDGE HALF QUANTITY =",
            plan["h1_original_half_quantity"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "MIN REQUIRED MARGIN USDT =",
            plan["minimum_required_margin_usdt"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "MARGIN SHORTFALL USDT =",
            plan["margin_shortfall_usdt"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "SIZING VALID =",
            plan["quantity_plan_valid"],
            flush=True,
        )

        print(
            "UNIT 7", side,
            "BLOCKING REASONS =",
            plan["blocking_reasons"],
            flush=True,
        )

    print(
        "UNIT 7 ENTRY CONTINUITY VERIFIED =",
        continuity,
        flush=True,
    )

    print(
        "UNIT 7 CANDIDATE READY FOR ACCOUNT CHECKS =",
        candidate_ready,
        flush=True,
    )

    print(
        "UNIT 7 DEMO ELIGIBILITY VERIFIED = False",
        flush=True,
    )

    print(
        "UNIT 7 TP INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 7 HEDGE RECOVERY INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 7 B1-B5 BACKUP INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 7 NEW ENTRY ORDER AUTHORIZED = False",
        flush=True,
    )

    print(
        "UNIT 7 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 7.10 SINGLE EXECUTION / UNIT 8 HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT7_RESULT = (
    fresh_reconstruction_unit_7()
)


# ============================================================
# END COMPLETE UNIVERSAL WEEX UNIT 7 V2
# NO DUPLICATE UNIT 7 V1 EXECUTION
# ============================================================

            

# ============================================================
# UNIVERSAL WEEX — COMPLETE UNIT 8 V1
# AUTHENTICATED DEMO BALANCE / POSITION INSPECTION
#
# UNIT 7 -> UNIT 8 -> UNIT 9
#
# READ-ONLY WEEX SIMULATION ENDPOINTS
# NO LEVERAGE READ REQUEST WHEN FLAT
# NO LEVERAGE WRITE
# NO ORDER SUBMISSION / CANCELLATION
# NO ACCOUNT OR POSITION MODE MUTATION
# EXISTING POSITION MANAGEMENT INDEPENDENT
# ============================================================

import os
import json
import time
import hmac
import hashlib
import base64
import urllib.request
import urllib.error

from decimal import Decimal, InvalidOperation


# ============================================================
# 8.1 STRICT DECIMAL AND ENV HELPERS
# ============================================================

def u8_decimal(value, name, allow_zero=True):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT8 BOOLEAN VALUE: " + name
        )

    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RuntimeError(
            "UNIT8 INVALID DECIMAL: " + name
        ) from exc

    if not result.is_finite():
        raise RuntimeError(
            "UNIT8 NONFINITE DECIMAL: " + name
        )

    if not allow_zero and result <= 0:
        raise RuntimeError(
            "UNIT8 NONPOSITIVE DECIMAL: " + name
        )

    return result


def u8_optional_decimal(value, name):

    if value is None or value == "":
        return None

    return u8_decimal(value, name)


def u8_fmt(value):

    if value is None:
        return None

    return format(value, "f")


def u8_env_first(*names):

    for name in names:
        value = os.getenv(name, "").strip()

        if value:
            return value

    return ""


# ============================================================
# 8.2 AUTHENTICATED DEMO GET ONLY
# ============================================================

def u8_demo_get(path, credentials):

    allowed_paths = (
        "/capi/v3/sim/balance",
        "/capi/v3/sim/position/allPosition",
    )

    if path not in allowed_paths:
        raise RuntimeError(
            "UNIT8 PATH NOT ALLOWED"
        )

    api_key, secret, passphrase = credentials

    timestamp = str(
        int(time.time() * 1000)
    )

    method = "GET"

    # GET with no query string or request body.
    prehash = (
        timestamp + method + path
    )

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("ascii")

    request = urllib.request.Request(
        url=(
            "https://api-contract.weex.com"
            + path
        ),
        method="GET",
        headers={
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT8 NON-READ-ONLY REQUEST BLOCKED"
        )

    timeout = float(
        os.getenv(
            "UNIT8_HTTP_TIMEOUT_SECONDS",
            "15",
        )
    )

    if not (0 < timeout <= 60):
        raise RuntimeError(
            "UNIT8 INVALID HTTP TIMEOUT"
        )

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            status = response.getcode()

            raw = response.read(
                2000000
            ).decode("utf-8")

    except urllib.error.HTTPError as exc:

        # Avoid logging response bodies that may
        # contain account information.

        raise RuntimeError(
            "UNIT8 HTTP STATUS "
            + str(exc.code)
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT8 DEMO CONNECTION FAILED"
        ) from exc

    if status != 200:
        raise RuntimeError(
            "UNIT8 UNEXPECTED HTTP STATUS"
        )

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT8 INVALID DEMO JSON"
        ) from exc

    # A 200 response with an error object
    # must never be interpreted as a flat
    # position or a zero balance.

    if isinstance(payload, dict):
        raise RuntimeError(
            "UNIT8 UNEXPECTED RESPONSE OBJECT"
        )

    if not isinstance(payload, list):
        raise RuntimeError(
            "UNIT8 RESPONSE IS NOT ARRAY"
        )

    return payload


# ============================================================
# 8.3 BALANCE VERIFICATION
# ============================================================

def u8_parse_balance(payload):

    matches = [
        item
        for item in payload
        if (
            isinstance(item, dict)
            and item.get("asset") == "SUSDT"
        )
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "UNIT8 SUSDT BALANCE NOT UNIQUE"
        )

    account = matches[0]

    total = u8_decimal(
        account.get("balance"),
        "DEMO TOTAL BALANCE",
    )

    available = u8_decimal(
        account.get("availableBalance"),
        "DEMO AVAILABLE BALANCE",
    )

    frozen = u8_decimal(
        account.get("frozen"),
        "DEMO FROZEN BALANCE",
    )

    unrealized = u8_decimal(
        account.get("unrealizePnl"),
        "DEMO UNREALIZED PNL",
    )

    if (
        total < 0
        or available < 0
        or frozen < 0
    ):
        raise RuntimeError(
            "UNIT8 NEGATIVE ACCOUNT FUNDS"
        )

    return {

        "asset": "SUSDT",

        "balance": u8_fmt(total),

        "available_balance": u8_fmt(
            available
        ),

        "frozen": u8_fmt(frozen),

        "unrealized_pnl": u8_fmt(
            unrealized
        ),

        "balance_verified": True,
    }


# ============================================================
# 8.4 POSITION RECONCILIATION
# ============================================================

def u8_parse_positions(payload, symbol):

    selected = []

    total_long = Decimal("0")
    total_short = Decimal("0")

    for item in payload:

        if not isinstance(item, dict):
            raise RuntimeError(
                "UNIT8 INVALID POSITION RECORD"
            )

        if item.get("symbol") != symbol:
            continue

        side = str(
            item.get("side", "")
        ).strip().upper()

        if side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "UNIT8 UNKNOWN POSITION SIDE"
            )

        size = u8_decimal(
            item.get("size"),
            "POSITION SIZE",
        )

        if size < 0:
            raise RuntimeError(
                "UNIT8 NEGATIVE POSITION SIZE"
            )

        if size == 0:
            continue

        leverage = u8_optional_decimal(
            item.get("leverage"),
            "POSITION LEVERAGE",
        )

        if (
            leverage is not None
            and leverage <= 0
        ):
            raise RuntimeError(
                "UNIT8 INVALID POSITION LEVERAGE"
            )

        if side == "LONG":
            total_long += size
        else:
            total_short += size

        selected.append({

            "id": item.get("id"),

            "symbol": symbol,

            "side": side,

            "quantity": u8_fmt(size),

            "leverage": u8_fmt(leverage),

            "margin_type":
                item.get("marginType"),

            "separated_mode":
                item.get("separatedMode"),

            "open_value":
                item.get("openValue"),

            "raw_liquidation_price":
                item.get("liquidationPrice"),

            "raw_entry_price":
                item.get("entryPrice"),

            "source":
                "WEEX_DEMO_POSITION",
        })

    return {

        "symbol": symbol,

        "positions": selected,

        "position_count": len(selected),

        "flat": len(selected) == 0,

        "long_quantity": u8_fmt(
            total_long
        ),

        "short_quantity": u8_fmt(
            total_short
        ),

        "both_sides_observed": (
            total_long > 0
            and total_short > 0
        ),

        # Do not infer account settings
        # from an empty position list.
        "flat_leverage_verified": False,

        "account_hedge_mode_verified": False,

        "position_reconciliation_verified": True,
    }


# ============================================================
# 8.5 MAIN UNIT 8
# ============================================================

def fresh_reconstruction_unit_8():

    print("=" * 80, flush=True)

    print(
        "UNIVERSAL WEEX UNIT 8 V1 START",
        flush=True,
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    unit6 = FRESH_RECONSTRUCTION_UNIT6_RESULT
    unit7 = FRESH_RECONSTRUCTION_UNIT7_RESULT

    if not all(
        isinstance(x, dict)
        for x in (
            config,
            market,
            unit6,
            unit7,
        )
    ):
        raise RuntimeError(
            "UNIT8 HANDOVER MISSING"
        )

    symbol = config.get(
        "exchange", {}
    ).get("market_symbol")

    if (
        config.get(
            "execution_environment"
        ) != "DEMO"
        or symbol != market.get("symbol")
        or symbol != unit6.get("symbol")
        or symbol != unit7.get("symbol")
        or unit7.get("read_only") is not True
        or unit7.get("trade_authorized") is not False
        or unit7.get(
            "unit7_revision"
        ) != "UNIVERSAL_USDT_SIZING_V2"
        or config.get(
            "safety", {}
        ).get(
            "real_order_submission_enabled"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT8 DEMO SAFETY HANDOVER FAILED"
        )

    # New-entry sizing is separate from
    # existing-position reconciliation.

    initial_margin = u8_decimal(
        config["entry"]["entry_margin_usdt"],
        "ENTRY MARGIN",
        allow_zero=False,
    )

    unit7_margin = u8_decimal(
        unit7.get("initial_margin_usdt"),
        "UNIT7 ENTRY MARGIN",
        allow_zero=False,
    )

    market_margin = u8_decimal(
        market.get("entry_margin_usdt"),
        "UNIT3 ENTRY MARGIN",
        allow_zero=False,
    )

    if not (
        initial_margin
        == unit7_margin
        == market_margin
    ):
        raise RuntimeError(
            "UNIT8 USDT MARGIN AUTHORITY MISMATCH"
        )

    cap = u8_decimal(
        config["strategy"][
            "exposure_cap_percent"
        ],
        "EXPOSURE CAP",
        allow_zero=False,
    )

    if cap > 100:
        raise RuntimeError(
            "UNIT8 EXPOSURE CAP ABOVE 100"
        )

    result = {

        "symbol": symbol,

        "execution_environment": "DEMO",

        "entry_margin_usdt":
            u8_fmt(initial_margin),

        "exposure_cap_percent": u8_fmt(cap),

        "account_read_status":
            "NOT_STARTED",

        "account_balance": None,

        "positions": [],

        "position_count": None,

        "position_flat_verified": False,

        "long_quantity": None,

        "short_quantity": None,

        "long_position_leverage": None,

        "short_position_leverage": None,

        "account_balance_verified": False,

        "available_margin_verified": False,

        "entry_margin_affordable": False,

        "entry_exposure_verified": False,

        "exposure_cap_verified": False,

        "position_reconciliation_verified": False,

        "demo_contract_eligibility_verified":
            False,

        "account_hedge_mode_verified": False,

        "position_mode_verified": False,

        "flat_long_leverage_verified": False,

        "flat_short_leverage_verified": False,

        "configured_leverage_account_verified":
            False,

        "unit7_candidate_ready":
            unit7.get(
                "candidate_ready_for_account_checks"
            ) is True,

        "new_entry_order_authorized": False,

        "trade_authorized": False,

        "position_management_independent":
            True,

        "tp_management_blocked": False,

        "atr_hedge_recovery_blocked": False,

        "b1_b5_backup_blocked": False,

        "read_only": True,

        "exchange_write": "NONE",

        "unit8_revision":
            "DEMO_ACCOUNT_RECONCILIATION_V1",
    }

    # ========================================================
    # 8.6 CREDENTIAL SELECTION
    # ========================================================

    api_key = u8_env_first(
        "WEEX_API_KEY",
        "WEEX_ACCESS_KEY",
    )

    api_secret = u8_env_first(
        "WEEX_API_SECRET",
        "WEEX_SECRET_KEY",
    )

    passphrase = u8_env_first(
        "WEEX_API_PASSPHRASE",
        "WEEX_PASSPHRASE",
    )

    if not all((
        api_key,
        api_secret,
        passphrase,
    )):

        result["account_read_status"] = (
            "MISSING_DEMO_API_CREDENTIALS"
        )

        print(
            "UNIT 8 ACCOUNT READ = "
            "MISSING DEMO API CREDENTIALS",
            flush=True,
        )

    else:

        credentials = (
            api_key,
            api_secret,
            passphrase,
        )

        try:

            balance_payload = u8_demo_get(
                "/capi/v3/sim/balance",
                credentials,
            )

            position_payload = u8_demo_get(
                "/capi/v3/sim/position/allPosition",
                credentials,
            )

            balance = u8_parse_balance(
                balance_payload
            )

            positions = u8_parse_positions(
                position_payload,
                symbol,
            )

            available = u8_decimal(
                balance["available_balance"],
                "AVAILABLE",
            )

            equity = u8_decimal(
                balance["balance"],
                "ACCOUNT BALANCE",
            )

            # First-level funding check only.
            # Fee reserves and exposure must be
            # validated in later execution gates.

            affordable = (
                available >= initial_margin
            )

            max_capital = (
                equity * cap / Decimal("100")
            )

            # We do NOT infer current position
            # margin from openValue alone.
            # Pending orders are not loaded here.
            #
            # Hence full exposure reconciliation
            # must remain unverified.

            result.update({

                "account_read_status": "PASS",

                "account_balance": balance,

                "positions":
                    positions["positions"],

                "position_count":
                    positions["position_count"],

                "position_flat_verified":
                    positions["flat"],

                "long_quantity":
                    positions["long_quantity"],

                "short_quantity":
                    positions["short_quantity"],

                "account_balance_verified": True,

                "available_margin_verified": True,

                "entry_margin_affordable":
                    affordable,

                "position_reconciliation_verified":
                    True,

                "maximum_account_margin_usdt":
                    u8_fmt(max_capital),

                "account_hedge_mode_verified":
                    False,

                "position_mode_verified":
                    False,

                "flat_long_leverage_verified":
                    False,

                "flat_short_leverage_verified":
                    False,

                "entry_exposure_verified":
                    False,

                "exposure_cap_verified": False,

                "new_entry_order_authorized":
                    False,
            })

            print(
                "UNIT 8 DEMO BALANCE ASSET = SUSDT",
                flush=True,
            )

            print(
                "UNIT 8 DEMO BALANCE =",
                balance["balance"],
                flush=True,
            )

            print(
                "UNIT 8 DEMO AVAILABLE =",
                balance["available_balance"],
                flush=True,
            )

            print(
                "UNIT 8 DEMO FROZEN =",
                balance["frozen"],
                flush=True,
            )

            print(
                "UNIT 8 DEMO UNREALIZED PNL =",
                balance["unrealized_pnl"],
                flush=True,
            )

            print(
                "UNIT 8 POSITION COUNT =",
                positions["position_count"],
                flush=True,
            )

            print(
                "UNIT 8 POSITION FLAT VERIFIED =",
                positions["flat"],
                flush=True,
            )

            print(
                "UNIT 8 LONG QUANTITY =",
                positions["long_quantity"],
                flush=True,
            )

            print(
                "UNIT 8 SHORT QUANTITY =",
                positions["short_quantity"],
                flush=True,
            )

            for position in positions["positions"]:

                print(
                    "UNIT 8 POSITION =",
                    position["side"],
                    "| QTY =",
                    position["quantity"],
                    "| LEVERAGE =",
                    position["leverage"],
                    "| MARGIN MODE =",
                    position["margin_type"],
                    "| SEPARATED MODE =",
                    position["separated_mode"],
                    flush=True,
                )

            print(
                "UNIT 8 INITIAL MARGIN AFFORDABLE =",
                affordable,
                flush=True,
            )

            print(
                "UNIT 8 EXPOSURE CAP VERIFIED = False",
                flush=True,
            )

            print(
                "UNIT 8 POSITION MODE VERIFIED = False",
                flush=True,
            )

        except Exception as exc:

            # Fail closed without leaking API
            # credentials or private payloads.

            result["account_read_status"] = (
                "FAILED_"
                + type(exc).__name__
            )

            print(
                "UNIT 8 ACCOUNT READ FAILURE =",
                str(exc),
                flush=True,
            )

    # ========================================================
    # 8.7 MANAGEMENT INDEPENDENCE
    # ========================================================

    print(
        "UNIT 8 UNIT7 ENTRY CANDIDATE READY =",
        result["unit7_candidate_ready"],
        flush=True,
    )

    print(
        "UNIT 8 ACCOUNT READ STATUS =",
        result["account_read_status"],
        flush=True,
    )

    print(
        "UNIT 8 TP MANAGEMENT INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 8 ATR HEDGE INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 8 B1-B5 BACKUP INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 8 NEW ENTRY AUTHORIZED = False",
        flush=True,
    )

    print(
        "UNIT 8 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 8 RESULT =",
        (
            "PASS"
            if result["account_read_status"] == "PASS"
            else "INCOMPLETE"
        ),
        flush=True,
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 8.8 SINGLE EXECUTION / UNIT 9 HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT8_RESULT = (
    fresh_reconstruction_unit_8()
)


# ============================================================
# END COMPLETE UNIVERSAL WEEX UNIT 8 V1
# ============================================================



# ============================================================
# UNIVERSAL WEEX — COMPLETE UNIT 9 V1
# ACCOUNT-WIDE DEMO EXPOSURE AND ENTRY SAFETY
#
# UNIT 8 -> UNIT 9 -> UNIT 10
#
# VERIFIED DEMO POSITIONS ACROSS ALL COINS
# FIXED USDT MARGIN FROM UNIT 2
# ENTRY QUANTITY FROM UNIT 7
# ACCOUNT-WIDE MARGIN EXPOSURE
# PENDING ORDER EXPOSURE: UNVERIFIED
# POSITION MODE: UNVERIFIED
# EXISTING POSITION MANAGEMENT: INDEPENDENT
#
# READ ONLY — NO EXCHANGE WRITES
# ============================================================

import os
import time
from decimal import Decimal, InvalidOperation


# ============================================================
# 9.1 STRICT DECIMAL HANDLING
# ============================================================

def u9_decimal(
    value,
    name,
    allow_negative=False,
):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT9 INVALID BOOLEAN " + name
        )

    try:
        number = Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:
        raise RuntimeError(
            "UNIT9 INVALID NUMBER " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT9 NONFINITE NUMBER " + name
        )

    if not allow_negative and number < 0:
        raise RuntimeError(
            "UNIT9 NEGATIVE VALUE " + name
        )

    return number


def u9_text(number):
    return format(number, "f")


def u9_env_number(name, default):

    raw = os.getenv(name, str(default)).strip()

    return u9_decimal(
        raw,
        name,
    )


# ============================================================
# 9.2 FULL ACCOUNT DEMO POSITION READ
# ============================================================

def u9_read_all_demo_positions():

    key = u8_env_first(
        "WEEX_API_KEY",
        "WEEX_ACCESS_KEY",
    )

    secret = u8_env_first(
        "WEEX_API_SECRET",
        "WEEX_SECRET_KEY",
    )

    passphrase = u8_env_first(
        "WEEX_API_PASSPHRASE",
        "WEEX_PASSPHRASE",
    )

    if not all((key, secret, passphrase)):
        raise RuntimeError(
            "UNIT9 DEMO CREDENTIALS MISSING"
        )

    # Reuse the signed, restricted GET from Unit 8.
    # Never switch to the live positions endpoint.

    return u8_demo_get(
        "/capi/v3/sim/position/allPosition",
        (key, secret, passphrase),
    )


# ============================================================
# 9.3 ACCOUNT-WIDE POSITION RECONCILIATION
# ============================================================

def u9_reconcile_positions(records):

    if not isinstance(records, list):
        raise RuntimeError(
            "UNIT9 INVALID POSITION ARRAY"
        )

    positions = []

    observed_margin = Decimal("0")
    observed_notional = Decimal("0")

    margin_complete = True
    notional_complete = True

    by_symbol = {}

    for item in records:

        if not isinstance(item, dict):
            raise RuntimeError(
                "UNIT9 INVALID POSITION RECORD"
            )

        symbol = item.get("symbol")
        side = str(
            item.get("side", "")
        ).upper()

        if (
            not isinstance(symbol, str)
            or not symbol
            or side not in ("LONG", "SHORT")
        ):
            raise RuntimeError(
                "UNIT9 INVALID SYMBOL OR SIDE"
            )

        size = u9_decimal(
            item.get("size"),
            "POSITION SIZE",
        )

        if size == 0:
            continue

        leverage = None

        if item.get("leverage") not in (
            None, ""
        ):
            leverage = u9_decimal(
                item["leverage"],
                "POSITION LEVERAGE",
            )

            if leverage <= 0:
                raise RuntimeError(
                    "UNIT9 INVALID LEVERAGE"
                )

        # marginSize is the directly reported
        # margin field when supplied by WEEX.
        #
        # Do not estimate missing margin from
        # quantity * current NEAR price, since
        # other symbols may have different prices.

        raw_margin = item.get("marginSize")

        margin = None

        if raw_margin not in (None, ""):
            margin = u9_decimal(
                raw_margin,
                "POSITION MARGIN",
            )
            observed_margin += margin
        else:
            margin_complete = False

        raw_notional = item.get("openValue")

        notional = None

        if raw_notional not in (None, ""):
            notional = u9_decimal(
                raw_notional,
                "POSITION OPEN VALUE",
            )
            observed_notional += notional
        else:
            notional_complete = False

        margin_type = item.get(
            "marginType"
        )

        positions.append({

            "symbol": symbol,
            "side": side,
            "quantity": u9_text(size),

            "leverage": (
                u9_text(leverage)
                if leverage is not None
                else None
            ),

            "margin_type": margin_type,

            "reported_margin_usdt": (
                u9_text(margin)
                if margin is not None
                else None
            ),

            "open_value_usdt": (
                u9_text(notional)
                if notional is not None
                else None
            ),

            "margin_verified": (
                margin is not None
            ),
        })

        if symbol not in by_symbol:
            by_symbol[symbol] = {
                "long_count": 0,
                "short_count": 0,
                "observed_margin": Decimal("0"),
            }

        if side == "LONG":
            by_symbol[symbol]["long_count"] += 1
        else:
            by_symbol[symbol]["short_count"] += 1

        if margin is not None:
            by_symbol[symbol][
                "observed_margin"
            ] += margin

    symbol_summary = {
        symbol: {
            "long_count": data["long_count"],
            "short_count": data["short_count"],
            "observed_margin_usdt":
                u9_text(
                    data["observed_margin"]
                ),
        }
        for symbol, data in by_symbol.items()
    }

    return {

        "positions": positions,

        "total_position_count":
            len(positions),

        "all_positions_flat":
            len(positions) == 0,

        "observed_position_margin_usdt":
            u9_text(observed_margin),

        "observed_open_notional_usdt":
            u9_text(observed_notional),

        "position_margin_fields_complete":
            margin_complete,

        "position_notional_fields_complete":
            notional_complete,

        "symbols": symbol_summary,

        "read_verified": True,
    }


# ============================================================
# 9.4 MAIN ACCOUNT SAFETY CHECK
# ============================================================

def fresh_reconstruction_unit_9():

    print("=" * 80, flush=True)

    print(
        "UNIVERSAL WEEX UNIT 9 V1 START",
        flush=True,
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    unit6 = FRESH_RECONSTRUCTION_UNIT6_RESULT
    unit7 = FRESH_RECONSTRUCTION_UNIT7_RESULT
    unit8 = FRESH_RECONSTRUCTION_UNIT8_RESULT

    if not all(
        isinstance(x, dict)
        for x in (
            config,
            market,
            unit6,
            unit7,
            unit8,
        )
    ):
        raise RuntimeError(
            "UNIT9 HANDOVER INCOMPLETE"
        )

    symbol = config["exchange"][
        "market_symbol"
    ]

    if (
        config.get(
            "execution_environment"
        ) != "DEMO"
        or symbol != market.get("symbol")
        or symbol != unit6.get("symbol")
        or symbol != unit7.get("symbol")
        or symbol != unit8.get("symbol")
        or unit8.get(
            "unit8_revision"
        ) != "DEMO_ACCOUNT_RECONCILIATION_V1"
        or unit7.get(
            "unit7_revision"
        ) != "UNIVERSAL_USDT_SIZING_V2"
        or config.get(
            "safety", {}
        ).get(
            "real_order_submission_enabled"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT9 DEMO SAFETY HANDOVER FAILED"
        )

    margin = u9_decimal(
        config["entry"][
            "entry_margin_usdt"
        ],
        "ENTRY MARGIN",
    )

    if margin <= 0:
        raise RuntimeError(
            "UNIT9 INVALID ENTRY MARGIN"
        )

    for name, value in (
        (
            "UNIT3",
            market.get(
                "entry_margin_usdt"
            ),
        ),
        (
            "UNIT7",
            unit7.get(
                "initial_margin_usdt"
            ),
        ),
        (
            "UNIT8",
            unit8.get(
                "entry_margin_usdt"
            ),
        ),
    ):
        if u9_decimal(
            value,
            name + " MARGIN",
        ) != margin:
            raise RuntimeError(
                "UNIT9 MARGIN MISMATCH: "
                + name
            )

    cap_percent = u9_decimal(
        config["strategy"][
            "exposure_cap_percent"
        ],
        "EXPOSURE CAP",
    )

    if not (
        Decimal("0")
        < cap_percent
        <= Decimal("100")
    ):
        raise RuntimeError(
            "UNIT9 INVALID EXPOSURE CAP"
        )

    # This is account entry safety.
    # A failed new-entry signal does NOT
    # prevent position reconciliation.

    unit6_ready = (
        unit6.get(
            "entry_continuity_verified"
        ) is True
    )

    unit7_ready = (
        unit7.get(
            "candidate_ready_for_account_checks"
        ) is True
    )

    account_read_pass = (
        unit8.get(
            "account_read_status"
        ) == "PASS"
        and unit8.get(
            "account_balance_verified"
        ) is True
    )

    result = {

        "symbol": symbol,

        "unit9_revision":
            "DEMO_ACCOUNT_EXPOSURE_V1",

        "margin_mode": "FIXED_USDT",

        "entry_margin_usdt":
            u9_text(margin),

        "exposure_cap_percent":
            u9_text(cap_percent),

        "account_read_status":
            "PENDING",

        "account_wide_positions": [],

        "account_wide_position_count": None,

        "observed_position_margin_usdt":
            None,

        "observed_open_notional_usdt":
            None,

        "total_account_equity_usdt":
            None,

        "available_balance_usdt":
            None,

        "maximum_margin_exposure_usdt":
            None,

        "indicative_remaining_capacity_usdt":
            None,

        "all_positions_flat_verified":
            False,

        "account_wide_positions_verified":
            False,

        "position_margin_fields_complete":
            False,

        "account_wide_exposure_verified":
            False,

        "pending_orders_verified": False,

        "pending_order_margin_usdt": None,

        "exposure_cap_verified": False,

        "account_position_mode_verified":
            False,

        "demo_contract_eligibility_verified":
            False,

        "quantity_encoding_verified":
            False,

        "leverage_account_verified":
            False,

        "entry_margin_affordable": False,

        "unit6_continuity_verified":
            unit6_ready,

        "unit7_candidate_ready":
            unit7_ready,

        "account_preliminary_margin_pass":
            False,

        "new_entry_order_authorized": False,

        "trade_authorized": False,

        # Existing positions remain manageable
        # independently of entry eligibility.

        "existing_position_management_allowed":
            True,

        "tp_management_blocked":
            False,

        "atr_hedge_recovery_blocked":
            False,

        "b1_b5_backup_blocked":
            False,

        "read_only": True,

        "exchange_write": "NONE",
    }

    # ========================================================
    # 9.5 ACCOUNT BALANCE FROM UNIT 8
    # ========================================================

    if not account_read_pass:

        result["account_read_status"] = (
            "UNIT8_ACCOUNT_UNVERIFIED"
        )

    else:

        balance = unit8.get(
            "account_balance"
        )

        if not isinstance(balance, dict):
            raise RuntimeError(
                "UNIT9 MISSING VERIFIED BALANCE"
            )

        equity = u9_decimal(
            balance.get("balance"),
            "DEMO BALANCE",
        )

        available = u9_decimal(
            balance.get(
                "available_balance"
            ),
            "DEMO AVAILABLE",
        )

        frozen = u9_decimal(
            balance.get("frozen"),
            "DEMO FROZEN",
        )

        # The WEEX balance field is used as
        # the provisional cap base.
        #
        # Exact account equity treatment
        # needs separate reconciliation.

        maximum_exposure = (
            equity
            * cap_percent
            / Decimal("100")
        )

        result.update({

            "total_account_equity_usdt":
                u9_text(equity),

            "available_balance_usdt":
                u9_text(available),

            "frozen_balance_usdt":
                u9_text(frozen),

            "maximum_margin_exposure_usdt":
                u9_text(
                    maximum_exposure
                ),

            "entry_margin_affordable":
                available >= margin,
        })

        # ====================================================
        # 9.6 FULL ACCOUNT POSITION RECONCILIATION
        # ====================================================

        try:

            raw_positions = (
                u9_read_all_demo_positions()
            )

            account = u9_reconcile_positions(
                raw_positions
            )

            observed_margin = u9_decimal(
                account[
                    "observed_position_margin_usdt"
                ],
                "OBSERVED MARGIN",
            )

            indicative_capacity = max(
                Decimal("0"),
                maximum_exposure - observed_margin,
            )

            provisional_margin_pass = (
                available >= margin
                and (
                    observed_margin + margin
                    <= maximum_exposure
                )
            )

            result.update({

                "account_read_status": "PASS",

                "account_wide_positions":
                    account["positions"],

                "account_wide_position_count":
                    account[
                        "total_position_count"
                    ],

                "all_positions_flat_verified":
                    account[
                        "all_positions_flat"
                    ],

                "account_wide_positions_verified":
                    True,

                "observed_position_margin_usdt":
                    account[
                        "observed_position_margin_usdt"
                    ],

                "observed_open_notional_usdt":
                    account[
                        "observed_open_notional_usdt"
                    ],

                "position_margin_fields_complete":
                    account[
                        "position_margin_fields_complete"
                    ],

                "indicative_remaining_capacity_usdt":
                    u9_text(
                        indicative_capacity
                    ),

                "account_preliminary_margin_pass":
                    provisional_margin_pass
                    and account[
                        "position_margin_fields_complete"
                    ],

                "symbols":
                    account["symbols"],
            })

            print(
                "UNIT 9 ACCOUNT-WIDE POSITION COUNT =",
                account[
                    "total_position_count"
                ],
                flush=True,
            )

            print(
                "UNIT 9 ALL POSITIONS FLAT =",
                account[
                    "all_positions_flat"
                ],
                flush=True,
            )

            print(
                "UNIT 9 OBSERVED POSITION MARGIN USDT =",
                account[
                    "observed_position_margin_usdt"
                ],
                flush=True,
            )

            print(
                "UNIT 9 MARGIN FIELDS COMPLETE =",
                account[
                    "position_margin_fields_complete"
                ],
                flush=True,
            )

            for (
                position_symbol,
                details,
            ) in account[
                "symbols"
            ].items():

                print(
                    "UNIT 9 SYMBOL =",
                    position_symbol,
                    "| LONG COUNT =",
                    details["long_count"],
                    "| SHORT COUNT =",
                    details["short_count"],
                    "| MARGIN =",
                    details[
                        "observed_margin_usdt"
                    ],
                    flush=True,
                )

        except Exception as exc:

            result["account_read_status"] = (
                "FAILED_"
                + type(exc).__name__
            )

            # Keep account data unverified.
            # Never treat failure as zero exposure.

            print(
                "UNIT 9 ACCOUNT-WIDE READ ERROR =",
                type(exc).__name__,
                flush=True,
            )

    # ========================================================
    # 9.7 CONSERVATIVE NEW-ENTRY DECISION
    # ========================================================

    reasons = []

    if not unit6_ready:
        reasons.append(
            "UNIT6_CONTINUITY_NOT_VERIFIED"
        )

    if not unit7_ready:
        reasons.append(
            "UNIT7_CANDIDATE_NOT_READY"
        )

    if result[
        "account_read_status"
    ] != "PASS":
        reasons.append(
            "ACCOUNT_WIDE_READ_NOT_VERIFIED"
        )

    if not result[
        "account_preliminary_margin_pass"
    ]:
        reasons.append(
            "PRELIMINARY_MARGIN_CHECK_NOT_PASSED"
        )

    if not result[
        "pending_orders_verified"
    ]:
        reasons.append(
            "PENDING_ORDERS_NOT_RECONCILED"
        )

    if not result[
        "account_position_mode_verified"
    ]:
        reasons.append(
            "POSITION_MODE_NOT_VERIFIED"
        )

    if not result[
        "demo_contract_eligibility_verified"
    ]:
        reasons.append(
            "DEMO_CONTRACT_NOT_VERIFIED"
        )

    if not result[
        "quantity_encoding_verified"
    ]:
        reasons.append(
            "ORDER_QUANTITY_ENCODING_NOT_VERIFIED"
        )

    if not result[
        "leverage_account_verified"
    ]:
        reasons.append(
            "ACCOUNT_LEVERAGE_NOT_VERIFIED"
        )

    result["new_entry_blocking_reasons"] = (
        reasons
    )

    result["new_entry_order_authorized"] = (
        False
    )

    result["trade_authorized"] = False

    # ========================================================
    # 9.8 RENDER VERIFICATION
    # ========================================================

    print(
        "UNIT 9 ENTRY MARGIN USDT =",
        u9_text(margin),
        flush=True,
    )

    print(
        "UNIT 9 EXPOSURE CAP PERCENT =",
        u9_text(cap_percent),
        flush=True,
    )

    print(
        "UNIT 9 DEMO BALANCE =",
        result[
            "total_account_equity_usdt"
        ],
        flush=True,
    )

    print(
        "UNIT 9 AVAILABLE BALANCE =",
        result[
            "available_balance_usdt"
        ],
        flush=True,
    )

    print(
        "UNIT 9 MAX MARGIN EXPOSURE =",
        result[
            "maximum_margin_exposure_usdt"
        ],
        flush=True,
    )

    print(
        "UNIT 9 INDICATIVE REMAINING CAPACITY =",
        result[
            "indicative_remaining_capacity_usdt"
        ],
        flush=True,
    )

    print(
        "UNIT 9 PRELIMINARY MARGIN PASS =",
        result[
            "account_preliminary_margin_pass"
        ],
        flush=True,
    )

    print(
        "UNIT 9 ACCOUNT-WIDE READ STATUS =",
        result[
            "account_read_status"
        ],
        flush=True,
    )

    print(
        "UNIT 9 PENDING ORDERS VERIFIED = False",
        flush=True,
    )

    print(
        "UNIT 9 EXPOSURE CAP VERIFIED = False",
        flush=True,
    )

    print(
        "UNIT 9 POSITION MODE VERIFIED = False",
        flush=True,
    )

    print(
        "UNIT 9 NEW ENTRY BLOCKING REASONS =",
        reasons,
        flush=True,
    )

    print(
        "UNIT 9 NEW ENTRY ORDER AUTHORIZED = False",
        flush=True,
    )

    print(
        "UNIT 9 TP MANAGEMENT INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 9 ATR HEDGE RECOVERY INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 9 B1-B5 BACKUP INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 9 DEMO ORDER = NONE",
        flush=True,
    )

    print(
        "UNIT 9 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 9 RESULT =",
        (
            "PASS"
            if result[
                "account_read_status"
            ] == "PASS"
            else "INCOMPLETE"
        ),
        flush=True,
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 9.9 SINGLE EXECUTION / UNIT 10 HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT9_RESULT = (
    fresh_reconstruction_unit_9()
)


# ============================================================
# END COMPLETE UNIT 9 V1
# ZERO INDENTATION
# ============================================================



# ============================================================
# UNIVERSAL WEEX — COMPLETE UNIT 10 V1
# DEMO EXECUTION READINESS / ACCOUNT RECONCILIATION
#
# READ ONLY. NO ORDER SUBMISSION.
# NO LIVE CASH ENDPOINT.
# NO LEVERAGE OR POSITION MODE CHANGES.
# ============================================================

import os
import re
import time
from decimal import Decimal, InvalidOperation


def u10_dec(value, name, positive=False):
    if isinstance(value, bool):
        raise RuntimeError("UNIT10 INVALID " + name)
    try:
        n = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError("UNIT10 INVALID " + name) from exc
    if not n.is_finite() or (positive and n <= 0):
        raise RuntimeError("UNIT10 INVALID " + name)
    return n


def u10_fmt(value):
    return format(value, "f")


def u10_bool(value):
    return value is True


def u10_demo_symbol(market_symbol):
    # The public symbol and demo order symbol
    # are deliberately distinct.
    if not isinstance(market_symbol, str):
        raise RuntimeError("UNIT10 INVALID SYMBOL")

    if not re.fullmatch(r"[A-Z0-9]+USDT", market_symbol):
        raise RuntimeError("UNIT10 INVALID SYMBOL FORMAT")

    candidate = market_symbol[:-4] + "SUSDT"

    override = os.getenv(
        "WEEX_DEMO_ORDER_SYMBOL", ""
    ).strip().upper()

    if override:
        if not re.fullmatch(r"[A-Z0-9]+SUSDT", override):
            raise RuntimeError(
                "UNIT10 INVALID DEMO SYMBOL OVERRIDE"
            )
        candidate = override

    # A valid-looking name is NOT proof
    # that the demo contract is tradable.
    return candidate


def u10_position_evidence(unit8, unit9, symbol):
    positions = unit9.get("account_wide_positions")

    if not isinstance(positions, list):
        return {
            "status": "UNVERIFIED",
            "selected_positions": [],
            "observed_sides": [],
            "position_mode_verified": False,
        }

    selected = [
        p for p in positions
        if isinstance(p, dict)
        and p.get("symbol") == symbol
    ]

    sides = sorted({
        p.get("side")
        for p in selected
        if p.get("side") in ("LONG", "SHORT")
    })

    # Unit 9 does not retain separatedMode
    # in its normalized position records.
    # Therefore we cannot prove account mode
    # from this handover.
    return {
        "status": (
            "POSITIONS_OBSERVED"
            if selected else "FLAT"
        ),
        "selected_positions": selected,
        "observed_sides": sides,
        "position_mode_verified": False,
        "dual_side_execution_verified": False,
    }


def u10_build_order_preview(
    demo_symbol,
    direction,
    plan,
):
    if direction not in ("LONG", "SHORT"):
        return None

    if not isinstance(plan, dict):
        return None

    if plan.get("quantity_plan_valid") is not True:
        return None

    qty = u10_dec(
        plan.get("proposed_quantity"),
        "ORDER QUANTITY",
        positive=True,
    )

    # This is a preview only.
    # No client ID or signed request is created.
    return {
        "endpoint": "/capi/v3/sim/order",
        "symbol": demo_symbol,
        "side": (
            "BUY" if direction == "LONG" else "SELL"
        ),
        "positionSide": direction,
        "type": "MARKET",
        "quantity": u10_fmt(qty),
        "preview_only": True,
        "submission_authorized": False,
    }


def fresh_reconstruction_unit_10():

    print("=" * 80, flush=True)
    print(
        "UNIVERSAL WEEX UNIT 10 V1 START",
        flush=True,
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    unit6 = FRESH_RECONSTRUCTION_UNIT6_RESULT
    unit7 = FRESH_RECONSTRUCTION_UNIT7_RESULT
    unit8 = FRESH_RECONSTRUCTION_UNIT8_RESULT
    unit9 = FRESH_RECONSTRUCTION_UNIT9_RESULT

    sources = (
        config, market, unit6,
        unit7, unit8, unit9,
    )

    if not all(isinstance(x, dict) for x in sources):
        raise RuntimeError("UNIT10 HANDOVER MISSING")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, strategy)
    ):
        raise RuntimeError("UNIT10 CONFIG INVALID")

    symbol = exchange.get("market_symbol")

    if (
        config.get("execution_environment") != "DEMO"
        or safety.get(
            "real_order_submission_enabled"
        ) is not False
        or unit7.get("read_only") is not True
        or unit8.get("read_only") is not True
        or unit9.get("read_only") is not True
        or unit9.get("exchange_write") != "NONE"
        or any(
            x.get("symbol") != symbol
            for x in (
                market, unit6, unit7, unit8, unit9
            )
        )
    ):
        raise RuntimeError(
            "UNIT10 DEMO SAFETY HANDOVER FAILED"
        )

    # ========================================================
    # 10.1 CENTRAL USDT MARGIN AUTHORITY
    # ========================================================

    margins = [
        u10_dec(
            config["entry"]["entry_margin_usdt"],
            "UNIT2 MARGIN",
            positive=True,
        ),
        u10_dec(
            market["entry_margin_usdt"],
            "UNIT3 MARGIN",
            positive=True,
        ),
        u10_dec(
            unit7["initial_margin_usdt"],
            "UNIT7 MARGIN",
            positive=True,
        ),
        u10_dec(
            unit8["entry_margin_usdt"],
            "UNIT8 MARGIN",
            positive=True,
        ),
        u10_dec(
            unit9["entry_margin_usdt"],
            "UNIT9 MARGIN",
            positive=True,
        ),
    ]

    if len(set(margins)) != 1:
        raise RuntimeError(
            "UNIT10 USDT MARGIN AUTHORITY MISMATCH"
        )

    entry_margin = margins[0]

    # ========================================================
    # 10.2 DEMO SYMBOL
    # ========================================================

    demo_symbol = u10_demo_symbol(symbol)

    # The candidate name alone is insufficient
    # to verify WEEX demo instrument eligibility.
    demo_contract_verified = False

    # ========================================================
    # 10.3 SIGNAL AND SIZING
    # ========================================================

    continuity = u10_bool(
        unit6.get("entry_continuity_verified")
    )

    candidate_ready = u10_bool(
        unit7.get(
            "candidate_ready_for_account_checks"
        )
    )

    direction = unit7.get(
        "selected_direction", "NONE"
    )

    if direction not in ("LONG", "SHORT", "NONE"):
        raise RuntimeError(
            "UNIT10 INVALID ENTRY DIRECTION"
        )

    plans = {
        "LONG": unit7.get("long_plan"),
        "SHORT": unit7.get("short_plan"),
    }

    plan = plans.get(direction)

    preview = u10_build_order_preview(
        demo_symbol,
        direction,
        plan,
    )

    # ========================================================
    # 10.4 ACCOUNT AND POSITION EVIDENCE
    # ========================================================

    account_verified = (
        unit8.get("account_read_status") == "PASS"
        and unit9.get("account_read_status") == "PASS"
        and unit9.get(
            "account_wide_positions_verified"
        ) is True
    )

    evidence = u10_position_evidence(
        unit8, unit9, demo_symbol
    )

    account_positions = unit9.get(
        "account_wide_positions", []
    )

    observed_leverage = {
        "LONG": [],
        "SHORT": [],
    }

    if isinstance(account_positions, list):
        for position in account_positions:
            if not isinstance(position, dict):
                continue

            if position.get("symbol") not in (
                symbol, demo_symbol
            ):
                continue

            side = position.get("side")

            if side not in observed_leverage:
                continue

            raw = position.get("leverage")

            if raw not in (None, ""):
                observed_leverage[side].append(
                    u10_fmt(
                        u10_dec(
                            raw,
                            "POSITION LEVERAGE",
                            positive=True,
                        )
                    )
                )

    configured_leverage = {
        "LONG": u10_fmt(
            u10_dec(
                config["leverage"]["long"],
                "LONG LEVERAGE",
                positive=True,
            )
        ),
        "SHORT": u10_fmt(
            u10_dec(
                config["leverage"]["short"],
                "SHORT LEVERAGE",
                positive=True,
            )
        ),
    }

    leverage_status = {}

    for side in ("LONG", "SHORT"):
        seen = observed_leverage[side]

        if not seen:
            leverage_status[side] = (
                "UNVERIFIED_NO_POSITION"
            )
        elif all(
            u10_dec(x, "OBSERVED LEVERAGE")
            == u10_dec(
                configured_leverage[side],
                "CONFIGURED LEVERAGE",
            )
            for x in seen
        ):
            leverage_status[side] = (
                "OPEN_POSITION_MATCH"
            )
        else:
            leverage_status[side] = (
                "OPEN_POSITION_MISMATCH"
            )

    # Existing positions cannot prove the
    # leverage setting for future flat entries.
    future_entry_leverage_verified = False

    # ========================================================
    # 10.5 ENTRY BLOCKERS
    # ========================================================

    pending_orders_verified = u10_bool(
        unit9.get("pending_orders_verified")
    )

    exposure_verified = u10_bool(
        unit9.get("exposure_cap_verified")
    )

    quantity_encoding_verified = False
    position_mode_verified = False

    checks = {
        "UNIT6_CONTINUITY": continuity,
        "UNIT7_CANDIDATE": candidate_ready,
        "ACCOUNT_RECONCILIATION": account_verified,
        "PENDING_ORDERS": pending_orders_verified,
        "EXPOSURE_CAP": exposure_verified,
        "POSITION_MODE": position_mode_verified,
        "DEMO_CONTRACT": demo_contract_verified,
        "QUANTITY_ENCODING": quantity_encoding_verified,
        "ACCOUNT_LEVERAGE":
            future_entry_leverage_verified,
    }

    blockers = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    # Unit 10 is read-only, regardless of
    # whether any individual checks pass.
    authorized = False

    # ========================================================
    # 10.6 EXISTING POSITION MANAGEMENT HANDOVER
    # ========================================================

    management = {
        "independent_of_unit6_signal": True,
        "independent_of_unit7_sizing": True,
        "independent_of_bot_mode": True,
        "account_snapshot_verified": account_verified,
        "positions": (
            account_positions
            if account_verified
            else []
        ),
        "positions_usable_for_execution":
            account_verified,
        "tp_execution_authorized": False,
        "hedge_execution_authorized": False,
        "backup_execution_authorized": False,
    }

    result = {
        "unit10_revision":
            "DEMO_EXECUTION_READINESS_V1",
        "symbol": symbol,
        "demo_symbol_candidate": demo_symbol,
        "demo_symbol_verified":
            demo_contract_verified,
        "entry_margin_usdt":
            u10_fmt(entry_margin),
        "configured_leverage":
            configured_leverage,
        "observed_position_leverage":
            observed_leverage,
        "leverage_status": leverage_status,
        "account_read_verified":
            account_verified,
        "position_evidence": evidence,
        "entry_direction": direction,
        "entry_continuity_verified":
            continuity,
        "candidate_ready":
            candidate_ready,
        "order_preview": preview,
        "readiness_checks": checks,
        "blocking_reasons": blockers,
        "pending_orders_verified":
            pending_orders_verified,
        "exposure_cap_verified":
            exposure_verified,
        "position_mode_verified":
            position_mode_verified,
        "demo_contract_eligibility_verified":
            demo_contract_verified,
        "quantity_encoding_verified":
            quantity_encoding_verified,
        "account_leverage_verified":
            future_entry_leverage_verified,
        "new_entry_order_authorized":
            authorized,
        "trade_authorized": False,
        "position_management": management,
        "position_management_independent": True,
        "read_only": True,
        "exchange_write": "NONE",
    }

    # ========================================================
    # 10.7 RENDER LOGS
    # ========================================================

    print(
        "UNIT 10 MARKET SYMBOL =",
        symbol, flush=True,
    )

    print(
        "UNIT 10 DEMO SYMBOL CANDIDATE =",
        demo_symbol, flush=True,
    )

    print(
        "UNIT 10 DEMO SYMBOL VERIFIED =",
        demo_contract_verified, flush=True,
    )

    print(
        "UNIT 10 ENTRY MARGIN USDT =",
        u10_fmt(entry_margin), flush=True,
    )

    print(
        "UNIT 10 ACCOUNT READ VERIFIED =",
        account_verified, flush=True,
    )

    print(
        "UNIT 10 POSITION EVIDENCE =",
        evidence["status"], flush=True,
    )

    print(
        "UNIT 10 LONG LEVERAGE STATUS =",
        leverage_status["LONG"], flush=True,
    )

    print(
        "UNIT 10 SHORT LEVERAGE STATUS =",
        leverage_status["SHORT"], flush=True,
    )

    print(
        "UNIT 10 ENTRY DIRECTION =",
        direction, flush=True,
    )

    print(
        "UNIT 10 ENTRY CONTINUITY =",
        continuity, flush=True,
    )

    print(
        "UNIT 10 CANDIDATE READY =",
        candidate_ready, flush=True,
    )

    print(
        "UNIT 10 ORDER PREVIEW =",
        preview, flush=True,
    )

    print(
        "UNIT 10 READINESS CHECKS =",
        checks, flush=True,
    )

    print(
        "UNIT 10 BLOCKING REASONS =",
        blockers, flush=True,
    )

    print(
        "UNIT 10 EXISTING POSITION MANAGEMENT "
        "INDEPENDENT = True",
        flush=True,
    )

    print(
        "UNIT 10 NEW ENTRY AUTHORIZED = False",
        flush=True,
    )

    print(
        "UNIT 10 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 10.8 SINGLE EXECUTION / UNIT 11 HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT10_RESULT = (
    fresh_reconstruction_unit_10()
)

# ============================================================
# END COMPLETE UNIT 10 V1
# ============================================================



# ============================================================
# UNIVERSAL WEEX UNIT 11 V1
# DEMO CONTRACT / QUANTITY / EXECUTION READINESS
#
# INSERT AFTER UNIT 10.
# READ ONLY — NO POST, PUT OR DELETE.
# NO LIVE CASH ORDER SUBMISSION.
# ============================================================

import os
import re
import json
import urllib.request
import urllib.error
from decimal import Decimal, InvalidOperation


def u11_decimal(value, label, positive=False):
    if isinstance(value, bool):
        raise ValueError(label + ": BOOLEAN INVALID")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(label + ": INVALID DECIMAL")

    if not result.is_finite():
        raise ValueError(label + ": NONFINITE")

    if positive and result <= 0:
        raise ValueError(label + ": NOT POSITIVE")

    return result


def u11_number(value):
    return format(value, "f")


def u11_public_get(path):
    if not path.startswith("/capi/v3/market/"):
        raise RuntimeError(
            "UNIT11 NONPUBLIC PATH REJECTED"
        )

    url = "https://api-contract.weex.com" + path

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Demo-Readiness/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=12
        ) as response:
            status = response.status
            raw = response.read(2000000)
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "http_status": exc.code,
            "error": "HTTP_ERROR",
            "data": None,
        }
    except Exception as exc:
        return {
            "ok": False,
            "http_status": None,
            "error": type(exc).__name__,
            "data": None,
        }

    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {
            "ok": False,
            "http_status": status,
            "error": "INVALID_JSON",
            "data": None,
        }

    return {
        "ok": status == 200,
        "http_status": status,
        "error": None,
        "data": data,
    }


def u11_extract_symbols(payload):
    """
    Extract WEEX symbol names from:
    - Lists of symbol strings
    - Lists of symbol dictionaries
    - Nested API response structures
    """

    found = set()

    def walk(node, depth=0):

        if depth > 8:
            return

        if isinstance(node, str):
            symbol = node.strip().upper()

            if re.fullmatch(
                r"[A-Z0-9]+(?:USDT|SUSDT)",
                symbol
            ):
                found.add(symbol)

        elif isinstance(node, list):
            for item in node:
                walk(item, depth + 1)

        elif isinstance(node, dict):

            symbol = node.get("symbol")

            if isinstance(symbol, str):
                walk(symbol, depth + 1)

            for key in (
                "data", "symbols", "list", "rows"
            ):
                if key in node:
                    walk(node[key], depth + 1)

    walk(payload)

    return found


def u11_validate_plan(plan, label):
    result = {
        "valid": False,
        "reason": "MISSING_PLAN",
        "quantity": None,
        "tp_quantities": None,
        "hedge_half": None,
    }

    if not isinstance(plan, dict):
        return result

    if plan.get("quantity_plan_valid") is not True:
        result["reason"] = "UNIT7_PLAN_INVALID"
        return result

    try:
        qty = u11_decimal(
            plan.get("proposed_quantity"),
            label + " QUANTITY",
            positive=True,
        )

        tp1 = u11_decimal(
            plan.get("tp1_quantity"),
            label + " TP1",
        )
        tp2 = u11_decimal(
            plan.get("tp2_quantity"),
            label + " TP2",
        )
        tp3 = u11_decimal(
            plan.get("tp3_quantity"),
            label + " TP3",
        )

        half = u11_decimal(
            plan.get("h1_original_half_quantity"),
            label + " HEDGE HALF",
            positive=True,
        )

        opposite = u11_decimal(
            plan.get("h1_opposite_half_quantity"),
            label + " OPPOSITE HALF",
            positive=True,
        )

        full_opposite = u11_decimal(
            plan.get("h2_full_opposite_quantity"),
            label + " FULL OPPOSITE",
            positive=True,
        )

        contract = plan.get("contract", {})
        if not isinstance(contract, dict):
            contract = {}

        if (
            qty <= 0
            or min(tp1, tp2, tp3) <= 0
            or tp1 + tp2 + tp3 != qty
            or half * 2 != qty
            or opposite != half
            or full_opposite != qty
            or plan.get("exact_tp_split_valid") is not True
            or plan.get("exact_hedge_split_valid") is not True
        ):
            result["reason"] = "SPLIT_MISMATCH"
            return result

        result.update({
            "valid": True,
            "reason": "UNIT7_QUANTITY_ARITHMETIC_PASS",
            "quantity": u11_number(qty),
            "tp_quantities": [
                u11_number(tp1),
                u11_number(tp2),
                u11_number(tp3),
            ],
            "hedge_half": u11_number(half),
        })

    except (ValueError, TypeError):
        result["reason"] = "INVALID_QUANTITY"

    return result


def u11_preview(symbol, direction, plan):
    if not plan["valid"]:
        return None

    return {
        "endpoint": "/capi/v3/sim/order",
        "method": "POST",
        "body_template": {
            "symbol": symbol,
            "side": (
                "BUY" if direction == "LONG"
                else "SELL"
            ),
            "positionSide": direction,
            "type": "MARKET",
            "quantity": plan["quantity"],
            "newClientOrderId":
                "GENERATE_UNIQUE_ID_AT_SUBMISSION",
        },
        "client_id_generated": False,
        "verified_executable": False,
        "submission_authorized": False,
    }


def fresh_reconstruction_unit_11():

    print("=" * 80, flush=True)
    print(
        "UNIVERSAL WEEX UNIT 11 V1 START",
        flush=True,
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    unit7 = FRESH_RECONSTRUCTION_UNIT7_RESULT
    unit8 = FRESH_RECONSTRUCTION_UNIT8_RESULT
    unit9 = FRESH_RECONSTRUCTION_UNIT9_RESULT
    unit10 = FRESH_RECONSTRUCTION_UNIT10_RESULT

    if not all(
        isinstance(x, dict)
        for x in (
            config, unit7, unit8,
            unit9, unit10
        )
    ):
        raise RuntimeError(
            "UNIT11 REQUIRED HANDOVER MISSING"
        )

    market_symbol = unit10.get("symbol")
    demo_symbol = unit10.get(
        "demo_symbol_candidate"
    )

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("safety", {}).get(
            "real_order_submission_enabled"
        ) is not False
        or unit7.get("read_only") is not True
        or unit8.get("read_only") is not True
        or unit9.get("read_only") is not True
        or unit10.get("read_only") is not True
        or unit10.get("exchange_write") != "NONE"
        or unit7.get("symbol") != market_symbol
        or unit8.get("symbol") != market_symbol
        or unit9.get("symbol") != market_symbol
    ):
        raise RuntimeError(
            "UNIT11 DEMO SAFETY HANDOVER FAILED"
        )

    if not isinstance(demo_symbol, str):
        raise RuntimeError(
            "UNIT11 DEMO SYMBOL MISSING"
        )

    if not re.fullmatch(
        r"[A-Z0-9]+SUSDT", demo_symbol
    ):
        raise RuntimeError(
            "UNIT11 INVALID DEMO SYMBOL"
        )

    entry_margin = u11_decimal(
        unit10.get("entry_margin_usdt"),
        "ENTRY MARGIN",
        positive=True,
    )

    # ========================================================
    # 11.1 PUBLIC API SYMBOL CHECK
    # ========================================================

    api_symbols = u11_public_get(
        "/capi/v3/market/apiTradingSymbols"
    )
    
    # ====================================================
    # UNIT 11 PUBLIC SYMBOL RESPONSE DIAGNOSTIC
    # NO CREDENTIALS / NO EXCHANGE WRITE
    # ====================================================

    response_data = api_symbols.get("data")

    print(
        "UNIT 11 SYMBOL RESPONSE TYPE =",
        type(response_data).__name__,
        flush=True,
    )

    if isinstance(response_data, dict):
        print(
            "UNIT 11 SYMBOL RESPONSE KEYS =",
            list(response_data.keys())[:30],
            flush=True,
        )

        for key in (
            "code", "msg", "message",
            "success", "status"
        ):
            if key in response_data:
                print(
                    "UNIT 11 SYMBOL RESPONSE " +
                    key.upper() + " =",
                    str(response_data[key])[:200],
                    flush=True,
                )

        for key in (
            "data", "symbols", "list", "rows"
        ):
            if key in response_data:
                value = response_data[key]

                print(
                    "UNIT 11 SYMBOL FIELD =",
                    key,
                    "TYPE =",
                    type(value).__name__,
                    "LENGTH =",
                    len(value)
                    if isinstance(
                        value, (list, dict, str)
                    )
                    else "N/A",
                    flush=True,
                )

                if isinstance(value, list):
                    print(
                        "UNIT 11 SYMBOL SAMPLE =",
                        repr(value[:2])[:800],
                        flush=True,
                    )

    elif isinstance(response_data, list):
        print(
            "UNIT 11 SYMBOL TOP LEVEL COUNT =",
            len(response_data),
            flush=True,
        )

        print(
            "UNIT 11 SYMBOL SAMPLE =",
            repr(response_data[:2])[:800],
            flush=True,
        )

    else:
        print(
            "UNIT 11 SYMBOL RESPONSE PREVIEW =",
            repr(response_data)[:800],
            flush=True,
        )

    # ====================================================
    # END DIAGNOSTIC
    # ====================================================


    listed_symbols = set()

    if api_symbols["ok"]:
        listed_symbols = u11_extract_symbols(
            api_symbols["data"]
        )

    public_market_listed = (
        market_symbol in listed_symbols
    )

    demo_symbol_publicly_listed = (
        demo_symbol in listed_symbols
    )

    # Public listing is not definitive proof that
    # this account can trade the demo contract.
    demo_contract_verified = False

    # ========================================================
    # 11.2 VALIDATE BOTH SIDES
    # ========================================================

    long_plan = u11_validate_plan(
        unit7.get("long_plan"),
        "LONG",
    )

    short_plan = u11_validate_plan(
        unit7.get("short_plan"),
        "SHORT",
    )

    arithmetic_verified = (
        long_plan["valid"]
        and short_plan["valid"]
    )

    # Exact exchange-side demo quantity encoding
    # still requires confirmed demo contract rules
    # and a controlled exchange execution test.
    demo_quantity_encoding_verified = False

    # ========================================================
    # 11.3 DEMO ORDER PAYLOAD PREVIEWS
    # ========================================================

    previews = {
        "LONG": u11_preview(
            demo_symbol, "LONG", long_plan
        ),
        "SHORT": u11_preview(
            demo_symbol, "SHORT", short_plan
        ),
    }

    # ========================================================
    # 11.4 ACCOUNT READINESS
    # ========================================================

    account_verified = (
        unit10.get("account_read_verified")
        is True
    )

    balance = unit8.get(
        "account_balance", {}
    )

    if not isinstance(balance, dict):
        raise RuntimeError(
            "UNIT11 BALANCE HANDOVER INVALID"
        )

    available = u11_decimal(
        balance.get("available_balance"),
        "AVAILABLE BALANCE",
    )

    affordable = available >= entry_margin

    exposure_cap_verified = (
        unit9.get("exposure_cap_verified")
        is True
    )

    pending_orders_verified = (
        unit9.get("pending_orders_verified")
        is True
    )

    # No unsupported demo open-order endpoint
    # is called or silently substituted.
    pending_orders_status = (
        "VERIFIED_UPSTREAM"
        if pending_orders_verified
        else "NOT_RECONCILED"
    )

    position_mode_verified = (
        unit10.get("position_mode_verified")
        is True
    )

    account_leverage_verified = (
        unit10.get("account_leverage_verified")
        is True
    )

    continuity = (
        unit10.get(
            "entry_continuity_verified"
        ) is True
    )

    candidate = (
        unit10.get("candidate_ready")
        is True
    )

    # ========================================================
    # 11.5 EXPLICIT READINESS CHECKS
    # ========================================================

    checks = {
        "ACCOUNT_READ": account_verified,
        "ENTRY_MARGIN_AFFORDABLE": affordable,
        "UNIT7_QUANTITY_ARITHMETIC":
            arithmetic_verified,
        "UNIT6_CONTINUITY": continuity,
        "UNIT7_CANDIDATE": candidate,
        "PENDING_ORDERS":
            pending_orders_verified,
        "EXPOSURE_CAP":
            exposure_cap_verified,
        "POSITION_MODE":
            position_mode_verified,
        "DEMO_CONTRACT":
            demo_contract_verified,
        "DEMO_QUANTITY_ENCODING":
            demo_quantity_encoding_verified,
        "ACCOUNT_LEVERAGE":
            account_leverage_verified,
    }

    blockers = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    # This unit never authorizes exchange writes.
    # Unit 12 must independently refresh and
    # verify all execution-critical conditions.
    result = {
        "unit11_revision":
            "DEMO_ORDER_READINESS_V1",
        "symbol": market_symbol,
        "demo_symbol": demo_symbol,
        "entry_margin_usdt":
            u11_number(entry_margin),
        "available_balance":
            u11_number(available),
        "public_symbol_http_status":
            api_symbols["http_status"],
        "public_symbol_read_ok":
            api_symbols["ok"],
        "public_symbol_count":
            len(listed_symbols),
        "market_symbol_publicly_listed":
            public_market_listed,
        "demo_symbol_publicly_listed":
            demo_symbol_publicly_listed,
        "demo_contract_verified":
            demo_contract_verified,
        "long_quantity_plan": long_plan,
        "short_quantity_plan": short_plan,
        "quantity_arithmetic_verified":
            arithmetic_verified,
        "demo_quantity_encoding_verified":
            demo_quantity_encoding_verified,
        "order_previews": previews,
        "pending_orders_status":
            pending_orders_status,
        "pending_orders_verified":
            pending_orders_verified,
        "exposure_cap_verified":
            exposure_cap_verified,
        "position_mode_verified":
            position_mode_verified,
        "account_leverage_verified":
            account_leverage_verified,
        "readiness_checks": checks,
        "blocking_reasons": blockers,
        "position_management_independent":
            True,
        "new_entry_order_authorized":
            False,
        "trade_authorized": False,
        "read_only": True,
        "exchange_write": "NONE",
    }

    # ========================================================
    # 11.6 RENDER DIAGNOSTICS
    # ========================================================

    print(
        "UNIT 11 MARKET SYMBOL =",
        market_symbol, flush=True,
    )
    print(
        "UNIT 11 DEMO SYMBOL =",
        demo_symbol, flush=True,
    )
    print(
        "UNIT 11 PUBLIC SYMBOL HTTP STATUS =",
        api_symbols["http_status"], flush=True,
    )
    print(
        "UNIT 11 PUBLIC SYMBOL READ OK =",
        api_symbols["ok"], flush=True,
    )
    print(
        "UNIT 11 PUBLIC SYMBOL COUNT =",
        len(listed_symbols), flush=True,
    )
    print(
        "UNIT 11 MARKET SYMBOL PUBLICLY LISTED =",
        public_market_listed, flush=True,
    )
    print(
        "UNIT 11 DEMO SYMBOL PUBLICLY LISTED =",
        demo_symbol_publicly_listed, flush=True,
    )
    print(
        "UNIT 11 DEMO CONTRACT VERIFIED =",
        demo_contract_verified, flush=True,
    )
    print(
        "UNIT 11 LONG QUANTITY PLAN =",
        long_plan, flush=True,
    )
    print(
        "UNIT 11 SHORT QUANTITY PLAN =",
        short_plan, flush=True,
    )
    print(
        "UNIT 11 QUANTITY ARITHMETIC VERIFIED =",
        arithmetic_verified, flush=True,
    )
    print(
        "UNIT 11 DEMO QUANTITY ENCODING VERIFIED =",
        demo_quantity_encoding_verified,
        flush=True,
    )
    print(
        "UNIT 11 AVAILABLE BALANCE =",
        u11_number(available), flush=True,
    )
    print(
        "UNIT 11 ENTRY MARGIN AFFORDABLE =",
        affordable, flush=True,
    )
    print(
        "UNIT 11 PENDING ORDERS STATUS =",
        pending_orders_status, flush=True,
    )
    print(
        "UNIT 11 ORDER PREVIEWS =",
        previews, flush=True,
    )
    print(
        "UNIT 11 READINESS CHECKS =",
        checks, flush=True,
    )
    print(
        "UNIT 11 BLOCKING REASONS =",
        blockers, flush=True,
    )
    print(
        "UNIT 11 NEW ENTRY AUTHORIZED = False",
        flush=True,
    )
    print(
        "UNIT 11 EXCHANGE WRITE = NONE",
        flush=True,
    )
    print(
        "FRESH RECONSTRUCTION UNIT 11 RESULT = PASS",
        flush=True,
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# 11.7 UNIT 11 EXECUTION AND UNIT 12 HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_UNIT11_RESULT = (
    fresh_reconstruction_unit_11()
)

# ============================================================
# END UNIT 11 V1
# ============================================================
