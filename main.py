
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
# END COMPLETE UNIVERSAL UNIT 1 V1
# UNIT 2 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# UNIVERSAL WEEX 15-UNIT HYBRID BOT
# COMPLETE UNIT 2 V2 REPLACEMENT
#
# ADAPTED FROM:
# 17248-LINE WORKING BACKUP MODEL
# 16414-LINE REVERSIBLE ATR HEDGE MODEL
#
# ANY SUPPORTED USDT FUTURES COIN
# NO HARDCODED DEFAULT TRADING SYMBOL
# ADJUSTABLE EXPOSURE CAP
# MANUAL LONG / SHORT LEVERAGE
# ONE ATR HEDGE / RECOVERY CYCLE
# CONDITIONAL B1-B5 AFTER FIRST CYCLE
# ACTUAL-FILL-AWARE NET TP ACCOUNTING
# SECURED PROFIT PROTECTION
#
# DEMO ONLY
# ZERO INDENTATION AT UNIT BOUNDARY
# ============================================================

import os
import re
from decimal import Decimal, InvalidOperation


# ============================================================
# 2.1 VALIDATION AND ENVIRONMENT HELPERS
# ============================================================

def unit_2_v2_require(condition, message):

    if not condition:
        raise RuntimeError(
            "UNIT 2 CONFIG INVALID: " + message
        )


def unit_2_v2_env(name, default=None):

    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    return value.strip()


def unit_2_v2_number(
    value,
    name,
    allow_zero=False,
):

    if isinstance(value, bool) or value is None:
        raise RuntimeError(
            "UNIT 2 INVALID " + name
        )

    try:
        result = Decimal(str(value))

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:
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


def unit_2_v2_setting(
    name,
    default,
    allow_zero=False,
):

    return unit_2_v2_number(
        unit_2_v2_env(name, str(default)),
        name,
        allow_zero,
    )


def unit_2_v2_bool(name, default=False):

    raw = unit_2_v2_env(
        name,
        "true" if default else "false",
    ).lower()

    if raw in ("true", "yes", "on", "1"):
        return True

    if raw in ("false", "no", "off", "0"):
        return False

    raise RuntimeError(
        "UNIT 2 INVALID BOOLEAN " + name
    )


# Preserve number validation compatibility.
unit_2_v1_number = unit_2_v2_number
unit_2_v12_number = unit_2_v2_number


# ============================================================
# 2.2 COMPLETE CENTRAL CONFIGURATION
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)

    log(
        "UNIVERSAL WEEX UNIT 2 V2 START"
    )

    require = unit_2_v2_require
    env = unit_2_v2_env
    number = unit_2_v2_number
    setting = unit_2_v2_setting

    require(
        FRESH_RECONSTRUCTION_UNIT_1_READY is True,
        "UNIT 1 NOT READY",
    )

    # ========================================================
    # 2.3 UNIVERSAL COIN SELECTION
    #
    # NO BTC, NEAR OR OTHER COIN DEFAULT.
    # RENDER MUST DEFINE TRADING_SYMBOL.
    # ========================================================

    market_symbol = env("TRADING_SYMBOL")

    require(
        market_symbol is not None,
        "TRADING_SYMBOL MUST BE SET IN RENDER",
    )

    market_symbol = market_symbol.upper()

    require(
        re.fullmatch(
            r"[A-Z0-9]{2,30}",
            market_symbol,
        ) is not None,
        "INVALID TRADING SYMBOL",
    )

    require(
        market_symbol.endswith("USDT"),
        "ONLY USDT-MARGined FUTURES SUPPORTED",
    )

    base_coin = market_symbol[:-4]

    require(
        bool(base_coin),
        "MISSING BASE COIN",
    )

    demo_symbol = env("WEEX_DEMO_SYMBOL")

    if demo_symbol:
        demo_symbol = demo_symbol.upper()

        require(
            re.fullmatch(
                r"[A-Z0-9]{2,30}",
                demo_symbol,
            ) is not None,
            "INVALID DEMO SYMBOL",
        )

    # Providing a symbol in Render does not
    # prove that WEEX supports demo trading.
    # Later units must verify the mapping.

    exchange = {

        "name": "WEEX",

        "api_version": "V3",

        "contract_base_url":
            "https://api-contract.weex.com",

        "market_symbol": market_symbol,

        "demo_order_symbol": demo_symbol,

        "base_coin": base_coin,

        "quote_coin": "USDT",

        "contract_type": "USDT_PERPETUAL",

        "demo_symbol_verified": False,

        "contract_metadata_verified": False,

        "market_symbol_source":
            "RENDER_TRADING_SYMBOL",

        "demo_symbol_verification_required":
            True,
    }

    # ========================================================
    # 2.4 INITIAL MARGIN
    #
    # COIN_EQUIVALENT:
    # INITIAL_MARGIN_COINS * VERIFIED COIN PRICE
    #
    # FIXED_USDT:
    # ACTUAL FIXED USDT MARGIN FROM RENDER
    #
    # THE INITIAL MARGIN VALUE IS NOT NOTIONAL.
    # LEVERAGE IS APPLIED LATER.
    # ========================================================

    margin_mode = env(
        "INITIAL_MARGIN_MODE",
        "COIN_EQUIVALENT",
    ).upper()

    require(
        margin_mode in (
            "COIN_EQUIVALENT",
            "FIXED_USDT",
        ),
        "INVALID INITIAL MARGIN MODE",
    )

    coin_amount = setting(
        "INITIAL_MARGIN_COINS",
        "1",
    )

    # Preserve margin names from prior models.
    # An explicitly defined higher-priority name
    # takes precedence over older aliases.

    fixed_raw = None
    fixed_source = "DEFAULT_0_5"

    for name in (
        "INITIAL_ENTRY_MARGIN_USDT",
        "ENTRY_FIXED_USDT",
        "ENTRY_MARGIN_USDT",
    ):

        value = env(name)

        if value is not None:
            fixed_raw = value
            fixed_source = name
            break

    if fixed_raw is None:
        fixed_raw = "0.5"

    fixed_margin = number(
        fixed_raw,
        "FIXED ENTRY MARGIN",
    )

    resolved_margin = (
        float(fixed_margin)
        if margin_mode == "FIXED_USDT"
        else None
    )

    margin = {

        "mode": margin_mode,

        "coin_equivalent_amount":
            float(coin_amount),

        "fixed_usdt":
            float(fixed_margin),

        "fixed_margin_source": fixed_source,

        "resolved_initial_margin_usdt":
            resolved_margin,

        "market_price_required":
            margin_mode == "COIN_EQUIVALENT",

        "conversion_price_type": "MARK",

        "fresh_price_required": True,

        "contract_precision_required": True,

        "available_balance_check_required": True,

        "margin_calculation_authority":
            "LATER_VALIDATED_UNIT",
    }

    # ========================================================
    # 2.5 MANUAL LEVERAGE
    #
    # PRIMARY RENDER NAMES PRESERVED.
    # LEVERAGE IS NOT CHANGED BY THE BOT.
    # ========================================================

    long_raw = env(
        "WEEX_DEMO_LONG_LEVERAGE",
        env("WEEX_LEVERAGE_LONG"),
    )

    short_raw = env(
        "WEEX_DEMO_SHORT_LEVERAGE",
        env("WEEX_LEVERAGE_SHORT"),
    )

    require(
        long_raw is not None,
        "MISSING LONG LEVERAGE ENVIRONMENT",
    )

    require(
        short_raw is not None,
        "MISSING SHORT LEVERAGE ENVIRONMENT",
    )

    long_leverage = number(
        long_raw,
        "LONG LEVERAGE",
    )

    short_leverage = number(
        short_raw,
        "SHORT LEVERAGE",
    )

    require(
        long_leverage <= Decimal("200"),
        "LONG LEVERAGE ABOVE LOCAL LIMIT",
    )

    require(
        short_leverage <= Decimal("200"),
        "SHORT LEVERAGE ABOVE LOCAL LIMIT",
    )

    leverage = {

        "source":
            "RENDER_MANUAL_CONFIGURATION",

        "long": float(long_leverage),

        "short": float(short_leverage),

        "long_environment":
            (
                "WEEX_DEMO_LONG_LEVERAGE"
                if env("WEEX_DEMO_LONG_LEVERAGE")
                else "WEEX_LEVERAGE_LONG"
            ),

        "short_environment":
            (
                "WEEX_DEMO_SHORT_LEVERAGE"
                if env("WEEX_DEMO_SHORT_LEVERAGE")
                else "WEEX_LEVERAGE_SHORT"
            ),

        "read_from_weex": False,

        "write_to_weex": False,

        "automatic_sync": False,

        "exchange_setting_required": True,

        "position_side_specific": True,

        "contract_limit_validation_required": True,
    }

    # ========================================================
    # 2.6 ADJUSTABLE EXPOSURE CAP
    #
    # ANY VALUE > 0 AND <= 100.
    # DEFAULT = 100.
    #
    # CAP IS A CEILING, NOT A TARGET.
    # ========================================================

    exposure_cap = setting(
        "EXPOSURE_CAP_PERCENT",
        "100",
    )

    require(
        Decimal("0") < exposure_cap
        <= Decimal("100"),
        "EXPOSURE CAP MUST BE >0 AND <=100",
    )

    exposure = {

        "cap_percent": float(exposure_cap),

        "maximum_allowed_percent": 100.0,

        "basis": "TRADING_ACCOUNT_EQUITY",

        "include_initial_margin": True,

        "include_open_hedge_margin": True,

        "include_filled_backups": True,

        "include_pending_margin": True,

        "include_reserved_order_margin": True,

        "prevent_orders_exceeding_cap": True,

        "stop_backups_at_cap": True,

        "final_failed_trade_exit":
            "MAX_EXPOSURE_CAP",

        "early_profit_exit_before_tp1": False,

        "liquidation_distance_strategy_exit":
            False,

        "liquidation_risk_monitoring": True,

        "forced_exchange_liquidation_possible":
            True,

        "secured_profit_excluded_from_budget":
            True,
    }

    # ========================================================
    # 2.7 TP ALLOCATION AND NET ROI
    # ========================================================

    tp1_roi = setting(
        "TP1_NET_ROI_PERCENT",
        "20",
    )

    tp2_roi = setting(
        "TP2_NET_ROI_PERCENT",
        "40",
    )

    tp1_share = setting(
        "TP1_ALLOCATION_PERCENT",
        "10",
    )

    tp2_share = setting(
        "TP2_ALLOCATION_PERCENT",
        "20",
    )

    tp3_share = setting(
        "TP3_ALLOCATION_PERCENT",
        "70",
    )

    require(
        tp1_share + tp2_share + tp3_share
        == Decimal("100"),
        "TP ALLOCATIONS MUST TOTAL 100",
    )

    require(
        tp2_roi > tp1_roi,
        "TP2 ROI MUST EXCEED TP1 ROI",
    )

    trail_min = setting(
        "TP3_TRAILING_MIN_ROI_PERCENT",
        "1",
    )

    trail_reference = setting(
        "TP3_TRAILING_REFERENCE_ROI_PERCENT",
        "3",
    )

    trail_max = setting(
        "TP3_TRAILING_MAX_ROI_PERCENT",
        "6",
    )

    require(
        trail_min <= trail_reference <= trail_max,
        "INVALID TRAILING RANGE",
    )

    # ========================================================
    # 2.8 INITIAL ENTRY COST POLICY
    #
    # TP IS FINALIZED AFTER VERIFIED ENTRY FILL.
    # USE ACTUAL ENTRY FEE.
    # ESTIMATE UNKNOWN EXIT COSTS.
    #
    # EXCLUDE ANY FUTURE HEDGE / B1-B5 COST
    # FROM ORIGINAL TP PRICE CALCULATION.
    # ========================================================

    taker_fee = setting(
        "ESTIMATED_TAKER_FEE_PERCENT",
        "0.08",
        True,
    )

    maker_fee = setting(
        "ESTIMATED_MAKER_FEE_PERCENT",
        "0.02",
        True,
    )

    require(
        taker_fee < Decimal("100")
        and maker_fee < Decimal("100"),
        "INVALID FEE RATE",
    )

    slippage_reserve = setting(
        "EXIT_SLIPPAGE_RESERVE_PERCENT",
        "0.05",
        True,
    )

    funding_reserve = setting(
        "FUNDING_RESERVE_USDT",
        "0",
        True,
    )

    other_cost_reserve = setting(
        "OTHER_TP_COST_RESERVE_USDT",
        "0",
        True,
    )

    fee_policy = {

        "actual_entry_fee_required": True,

        "entry_fee_source":
            "CONFIRMED_ORDER_FILLS",

        "estimated_exit_fee_required": True,

        "exit_fee_source":
            "ESTIMATE_UNTIL_CONFIRMED_FILL",

        "estimated_taker_fee_percent":
            float(taker_fee),

        "estimated_maker_fee_percent":
            float(maker_fee),

        "exit_slippage_reserve_percent":
            float(slippage_reserve),

        "funding_reserve_usdt":
            float(funding_reserve),

        "other_cost_reserve_usdt":
            float(other_cost_reserve),

        "actual_funding_to_date_included": True,

        "applicable_transfer_cost_included": True,

        "avoid_double_counting_spread": True,

        "include_future_hedge_costs_in_initial_tp":
            False,

        "include_future_backup_costs_in_initial_tp":
            False,

        "final_tp_calculation_after_fill": True,

        "recalculate_when_actual_costs_change":
            True,

        "actual_exit_fee_reconciliation": True,

        "full_cycle_ledger_separate": True,
    }

    # ========================================================
    # 2.9 SECURED PROFIT AND BALANCE PROTECTION
    # ========================================================

    be_buffer = setting(
        "BE_PLUS_BUFFER_ROI_PERCENT",
        "2",
        True,
    )

    profit_protection = {

        "tp1_secure_profit_first": True,

        "tp1_confirmed_fill_required": True,

        "tp1_actual_net_profit_required": True,

        "post_tp1_mode":
            "DYNAMIC_BREAK_EVEN_PLUS",

        "post_tp1_buffer_roi_percent":
            float(be_buffer),

        "protect_remaining_trade_balance": True,

        "tp2_secure_profit_first": True,

        "tp2_confirmed_fill_required": True,

        "post_tp2_mode":
            "DYNAMIC_NET_ROI_TRAILING",

        "secured_profit_ledger_enabled": True,

        "secured_profit_reuse_allowed": False,

        "exclude_secured_profit_from_be": True,

        "exclude_secured_profit_from_trailing":
            True,

        "exclude_secured_profit_from_backup_margin":
            True,

        "exclude_secured_profit_from_hedge_margin":
            True,

        "ledger_persistence_required": True,

        "external_collateral_segregation":
            False,

        "reconcile_realized_net_pnl": True,

        "reconcile_remaining_positions": True,
    }

    # ========================================================
    # 2.10 ONE-CYCLE REVERSIBLE ATR HEDGE
    #
    # PRESERVE H1 / H2 / R1 / R2 FROM 16414.
    # ========================================================

    hedge = {

        "enabled": True,

        "execution_enabled": False,

        "mode": "REVERSIBLE_ATR_TWO_STAGE",

        "environment": "DEMO",

        "atr_source": "UNIT_4_ATR14",

        "atr_period": 14,

        "atr_capture": "ORIGINAL_ENTRY",

        "atr_frozen_per_cycle": True,

        "entry_reference":
            "ORIGINAL_ENTRY_PRICE",

        "direction_reference":
            "ORIGINAL_SIDE",

        "quantity_reference":
            "ORIGINAL_FILLED_QUANTITY",

        # H1: adverse 1 ATR
        "h1_atr_multiplier": 1.0,
        "h1_original_fraction": 0.50,
        "h1_opposite_fraction": 0.50,

        # H2: adverse 2 ATR
        "h2_atr_multiplier": 2.0,
        "h2_original_fraction": 0.00,
        "h2_opposite_fraction": 1.00,

        # R1: recovery toward 1 ATR
        "r1_atr_multiplier": 1.0,
        "r1_original_fraction": 0.50,
        "r1_opposite_fraction": 0.50,

        # R2: return to original entry
        "r2_atr_multiplier": 0.0,
        "r2_original_fraction": 1.00,
        "r2_opposite_fraction": 0.00,

        "reversible": True,

        "repeatable": False,

        "max_completed_cycles": 1,

        "second_cycle_allowed": False,

        "persist_cycle_state": True,

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

        "liquidation_risk_monitoring_enabled":
            True,

        "bot_mode_independent": True,

        "real_cash_enabled": False,
    }

    # ========================================================
    # 2.11 CONDITIONAL B1-B5
    #
    # FROM 17248 REFERENCE.
    # ONLY AFTER FIRST HEDGE CYCLE IS CONSUMED
    # AND ANOTHER ADVERSE REVERSAL IS CONFIRMED.
    # ========================================================

    backup_percent = setting(
        "BACKUP_MARGIN_PERCENT",
        "0.5",
    )

    backup_buffer = setting(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
    )

    require(
        backup_percent <= Decimal("100"),
        "BACKUP PERCENT ABOVE 100",
    )

    require(
        backup_buffer < Decimal("100"),
        "BACKUP BUFFER MUST BE BELOW 100",
    )

    # Inside the liquidation boundary:
    #
    # Long trigger:  LQ * (1 + buffer%)
    # Short trigger: LQ * (1 - buffer%)
    #
    # These are boundary-relative triggers only.
    # They do not guarantee margin safety.

    long_factor = (
        Decimal("1")
        + backup_buffer / Decimal("100")
    )

    short_factor = (
        Decimal("1")
        - backup_buffer / Decimal("100")
    )

    backup = {

        "enabled": True,

        "execution_enabled": False,

        "activation_mode":
            "AFTER_FIRST_HEDGE_RECOVERY_REVERSAL",

        "require_first_hedge_cycle_consumed":
            True,

        "allow_second_hedge_cycle": False,

        "max_backups": 5,

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_margin_percent":
            float(backup_percent),

        "backup_buffer_percent":
            float(backup_buffer),

        "backup_trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "backup_long_liquidation_factor":
            float(long_factor),

        "backup_short_liquidation_factor":
            float(short_factor),

        "one_backup_at_a_time": True,

        "confirmed_fill_required": True,

        "recalculate_available_balance": True,

        "recalculate_liquidation_price": True,

        "recalculate_exposure": True,

        "fresh_market_confirmation_required":
            True,

        "progressive_backup_funding": True,

        "full_ladder_reservation_required":
            False,

        "backup_multipliers_enabled": False,

        "exposure_cap_enforced": True,

        "stop_new_backups_at_cap": True,

        "secured_profit_funding_allowed": False,

        "bot_mode_independent": True,
    }

    # ========================================================
    # 2.12 CENTRAL STRATEGY
    #
    # PRESERVE ORIGINAL DOWNSTREAM KEY NAMES.
    # ========================================================

    strategy = {

        "initial_fixed_usdt": resolved_margin,

        "initial_margin_mode": margin_mode,

        "initial_margin_coin_equivalent":
            float(coin_amount),

        "initial_margin_percent": 5.0,

        "backup_margin_percent":
            float(backup_percent),

        "backup_buffer_percent":
            float(backup_buffer),

        "max_backups": 5,

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "backup_long_liquidation_factor":
            float(long_factor),

        "backup_short_liquidation_factor":
            float(short_factor),

        "progressive_backup_funding": True,

        "full_ladder_reservation_required":
            False,

        "exposure_cap_percent":
            float(exposure_cap),

        "exposure_cap_max_percent": 100.0,

        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,

        "exposure_includes_open_hedge_margin":
            True,

        "exposure_includes_filled_backups":
            True,

        "exposure_includes_pending_margin":
            True,

        "tp1_allocation_percent":
            float(tp1_share),

        "tp2_allocation_percent":
            float(tp2_share),

        "tp3_allocation_percent":
            float(tp3_share),

        "tp1_net_roi_floor_percent":
            float(tp1_roi),

        "tp2_net_roi_floor_percent":
            float(tp2_roi),

        "tp1_tp2_min_roi_separation_percent":
            float(tp2_roi - tp1_roi),

        "tp3_trailing_reference_percent":
            float(trail_reference),

        "tp3_trailing_min_percent":
            float(trail_min),

        "tp3_trailing_max_percent":
            float(trail_max),

        "tp3_trailing_unit":
            "NET_ROI_PERCENT",

        "signal_expiry_seconds": 120,

        "loss_cooldown_seconds": 300,

        "one_direction_only": True,

        "anti_duplicate_orders": True,

        "active_trade_mode_lock": True,

        "exclusive_mode": True,

        "mode_confirmations_required": 3,

        "hedge": hedge,

        "backup": backup,

        "fee_policy": fee_policy,

        "profit_protection": profit_protection,
    }

    # ========================================================
    # 2.13 UNIVERSAL CONTRACT PRECISION
    #
    # NEVER USE BTC PRECISION FOR OTHER COINS.
    # THE NEXT UNITS MUST RESOLVE MARKET RULES.
    # ========================================================

    market_precision = {

        "quantity_step": None,

        "minimum_quantity": None,

        "price_step": None,

        "contract_size": None,

        "minimum_notional": None,

        "maximum_leverage": None,

        "precision_verified": False,

        "source":
            "PENDING_WEEX_CONTRACT_METADATA",

        "tp_quantity_step_aware": True,

        "hedge_quantity_step_aware": True,

        "validate_tp_allocations": True,

        "validate_50_percent_hedge": True,

        "reject_infeasible_initial_entry":
            True,
    }

    # ========================================================
    # 2.14 UNIFIED ENTRY QUALIFICATION
    #
    # RETAIN ORIGINAL BREAKOUT / STRUCTURE /
    # SCALP CONFIGURATION AND PRIORITY CONTRACTS.
    # ========================================================

    qualification = {

        "common": {

            "mode_priority": (
                "BREAKOUT",
                "STRUCTURE",
                "SCALP",
            ),

            "unified_entry_enabled": True,

            "one_initial_entry": True,

            "direction_votes_required": 2,

            "direction_votes_total": 3,

            "use_closed_candles": True,

            "protect_developing_candidates": True,

            "arbitrate_before_scalp": True,

            "scalp_requires_higher_modes_clear":
                True,

            "signal_expiry_seconds": 120,

            "candidate_expiry_seconds": 120,

            "spike_count_rejection_above": 2,

            "reject_late_impulse_entry": True,

            "target_reachability_enabled": True,

            "estimated_cost_check_enabled": True,

            "coin_specific_tuning_enabled": True,
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

            "minimum_ema_separation_percent":
                0.0,

            "retest_mandatory": False,

            "reject_trend_exhaustion": True,

            "candidate_expiry_seconds": 120,
        },

        "scalp": {

            "enabled": True,

            "priority": 3,

            "sideways_preferred": True,

            "require_sideways_market": True,

            "protect_developing_higher_modes":
                True,

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

            "estimated_taker_fee_percent":
                float(taker_fee),

            "estimated_slippage_percent":
                float(slippage_reserve),

            "include_entry_fee": True,

            "include_exit_fee": True,

            "minimum_fee_coverage_multiplier":
                2.0,

            "require_positive_estimated_net":
                True,

            "minimum_net_roi_percent": 2.0,
        },
    }

    # ========================================================
    # 2.15 UNIT-LOCAL SAFETY
    #
    # THIS DOES NOT DISABLE AUTHORIZED DEMO
    # EXECUTION IN LATER UNITS.
    # ========================================================

    safety = {

        "public_market_data_read_enabled": True,

        "demo_account_balance_read_enabled":
            True,

        "authenticated_api_enabled": False,

        "account_access_enabled": False,

        "position_access_enabled": False,

        "order_endpoint_access_enabled": False,

        "demo_order_submission_enabled":
            False,

        "real_order_submission_enabled":
            False,

        "exchange_mutation_enabled": False,

        "leverage_mutation_enabled": False,

        "margin_mode_mutation_enabled": False,

        "position_mode_mutation_enabled": False,

        "demo_execution_later_units_allowed":
            True,

        "real_cash_enabled": False,
    }

    # ========================================================
    # 2.16 COMPLETE CONFIGURATION HANDOVER
    # ========================================================

    config = {

        "exchange": exchange,

        "execution_environment": "DEMO",

        "safety": safety,

        "margin": margin,

        "leverage": leverage,

        "exposure": exposure,

        "strategy": strategy,

        "market_precision": market_precision,

        "qualification": qualification,

        "fee_policy": fee_policy,

        "profit_protection": profit_protection,

        "universal_symbol_enabled": True,
    }

    # ========================================================
    # 2.17 FINAL VALIDATION
    # ========================================================

    require(
        config["execution_environment"]
        == "DEMO",
        "DEMO ENVIRONMENT",
    )

    require(
        exchange["market_symbol"]
        == market_symbol,
        "SYMBOL HANDOVER",
    )

    require(
        strategy["max_backups"] == 5,
        "BACKUP COUNT",
    )

    require(
        hedge["max_completed_cycles"] == 1,
        "HEDGE CYCLE LIMIT",
    )

    require(
        hedge["repeatable"] is False,
        "SECOND HEDGE CYCLE DISABLED",
    )

    require(
        backup["require_first_hedge_cycle_consumed"]
        is True,
        "BACKUP ACTIVATION SEQUENCE",
    )

    for stage in ("h1", "h2", "r1", "r2"):

        original = Decimal(
            str(
                hedge[
                    stage + "_original_fraction"
                ]
            )
        )

        opposite = Decimal(
            str(
                hedge[
                    stage + "_opposite_fraction"
                ]
            )
        )

        require(
            original + opposite == Decimal("1"),
            stage.upper() + " FRACTIONS",
        )

    require(
        strategy["anti_duplicate_orders"] is True,
        "ANTI DUPLICATE ORDERS",
    )

    require(
        qualification["common"]["mode_priority"]
        == (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        ),
        "MODE PRIORITY",
    )

    require(
        fee_policy[
            "include_future_hedge_costs_in_initial_tp"
        ] is False,
        "INITIAL TP HEDGE COST EXCLUSION",
    )

    require(
        fee_policy[
            "include_future_backup_costs_in_initial_tp"
        ] is False,
        "INITIAL TP BACKUP COST EXCLUSION",
    )

    require(
        profit_protection[
            "secured_profit_reuse_allowed"
        ] is False,
        "SECURED PROFIT REUSE",
    )

    require(
        safety["real_order_submission_enabled"]
        is False,
        "REAL CASH DISABLED",
    )

    # ========================================================
    # 2.18 STARTUP REPORT
    # ========================================================

    print(
        "PASS: UNIVERSAL UNIT 2 V2 CONFIG CREATED",
        flush=True,
    )

    print(
        "TRADING SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "BASE COIN =",
        base_coin,
        flush=True,
    )

    print(
        "DEMO SYMBOL =",
        demo_symbol,
        flush=True,
    )

    print(
        "DEMO SYMBOL VERIFIED = False",
        flush=True,
    )

    print(
        "INITIAL MARGIN MODE =",
        margin_mode,
        flush=True,
    )

    print(
        "INITIAL COIN AMOUNT =",
        float(coin_amount),
        flush=True,
    )

    print(
        "FIXED ENTRY MARGIN USDT =",
        float(fixed_margin),
        flush=True,
    )

    print(
        "RESOLVED INITIAL MARGIN USDT =",
        resolved_margin,
        flush=True,
    )

    print(
        "LONG LEVERAGE RENDER =",
        float(long_leverage),
        flush=True,
    )

    print(
        "SHORT LEVERAGE RENDER =",
        float(short_leverage),
        flush=True,
    )

    print(
        "LEVERAGE API READ = NONE",
        flush=True,
    )

    print(
        "LEVERAGE API WRITE = NONE",
        flush=True,
    )

    print(
        "EXPOSURE CAP PERCENT =",
        float(exposure_cap),
        flush=True,
    )

    print(
        "EXPOSURE CAP MAXIMUM = 100%",
        flush=True,
    )

    print(
        "HEDGE MODE =",
        hedge["mode"],
        flush=True,
    )

    print(
        "HEDGE CYCLES MAXIMUM = 1",
        flush=True,
    )

    print(
        "H1 = 1 ATR | 50 ORIGINAL / 50 OPPOSITE",
        flush=True,
    )

    print(
        "H2 = 2 ATR | 0 ORIGINAL / 100 OPPOSITE",
        flush=True,
    )

    print(
        "R1 = 1 ATR | 50 ORIGINAL / 50 OPPOSITE",
        flush=True,
    )

    print(
        "R2 = ENTRY | 100 ORIGINAL / 0 OPPOSITE",
        flush=True,
    )

    print(
        "SECOND HEDGE CYCLE = DISABLED",
        flush=True,
    )

    print(
        "POST HEDGE = CONDITIONAL B1-B5",
        flush=True,
    )

    print(
        "BACKUP MARGIN PERCENT =",
        float(backup_percent),
        flush=True,
    )

    print(
        "BACKUP BUFFER PERCENT =",
        float(backup_buffer),
        flush=True,
    )

    print(
        "TP1 NET ROI TARGET =",
        float(tp1_roi),
        flush=True,
    )

    print(
        "TP2 NET ROI TARGET =",
        float(tp2_roi),
        flush=True,
    )

    print(
        "TP ALLOCATION =",
        float(tp1_share),
        float(tp2_share),
        float(tp3_share),
        flush=True,
    )

    print(
        "TP CALCULATION = AFTER VERIFIED ENTRY FILL",
        flush=True,
    )

    print(
        "FUTURE HEDGE COST IN ORIGINAL TP = FALSE",
        flush=True,
    )

    print(
        "FUTURE BACKUP COST IN ORIGINAL TP = FALSE",
        flush=True,
    )

    print(
        "POST TP1 = SECURE PROFIT + DYNAMIC BE",
        flush=True,
    )

    print(
        "POST TP2 = SECURE PROFIT + DYNAMIC TRAIL",
        flush=True,
    )

    print(
        "SECURED PROFIT REUSE = FALSE",
        flush=True,
    )

    print(
        "CONTRACT PRECISION = PENDING VERIFICATION",
        flush=True,
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True,
    )

    print(
        "REAL CASH EXECUTION = DISABLED",
        flush=True,
    )

    print(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS",
        flush=True,
    )

    print("=" * 80, flush=True)

    return config


# ============================================================
# 2.19 RUN UNIT 2
# PRESERVE ORIGINAL CONFIG VARIABLE
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# 2.20 UNIT 2 -> UNIT 3 READINESS ADAPTER
# ============================================================

FRESH_UNIT_2_OPTIMIZATION_READY = (

    isinstance(
        FRESH_RECONSTRUCTION_CONFIG,
        dict,
    )

    and FRESH_RECONSTRUCTION_CONFIG.get(
        "execution_environment"
    ) == "DEMO"

    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get(
            "exchange"
        ),
        dict,
    )

    and bool(
        FRESH_RECONSTRUCTION_CONFIG[
            "exchange"
        ].get("market_symbol")
    )

    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get(
            "strategy"
        ),
        dict,
    )

    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get(
            "qualification"
        ),
        dict,
    )

    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get(
            "leverage"
        ),
        dict,
    )

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("anti_duplicate_orders") is True

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("hedge", {}).get("enabled") is True

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("hedge", {}).get("max_completed_cycles")
    == 1

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("backup", {}).get("max_backups")
    == 5

    and FRESH_RECONSTRUCTION_CONFIG[
        "leverage"
    ].get("source")
    == "RENDER_MANUAL_CONFIGURATION"

    and FRESH_RECONSTRUCTION_CONFIG.get(
        "universal_symbol_enabled"
    ) is True
)


if not FRESH_UNIT_2_OPTIMIZATION_READY:

    raise RuntimeError(
        "UNIVERSAL UNIT 2 V2 READINESS FAILED"
    )


print(
    "UNIVERSAL UNIT 2 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True,
)


# ============================================================
# END COMPLETE UNIVERSAL UNIT 2 V2
# UNIT 3 FOLLOWS
# ZERO INDENTATION
# ============================================================
