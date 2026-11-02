
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


# ============================================================
# UNIVERSAL WEEX 15-UNIT HYBRID TRADING BOT
# COMPLETE UNIT 3 V1 REPLACEMENT
#
# ADAPTED FROM:
# 17248-LINE WORKING MODEL UNIT 3
# 16414-LINE ATR HEDGE MODEL UNIT 3
#
# UNIVERSAL COIN MARKET PRICE
# SELECTED SYMBOL FROM UNIT 2
# WEEX V3 PUBLIC MARK PRICE
# FRESHNESS AND RESPONSE VALIDATION
# COIN-EQUIVALENT MARGIN CONVERSION
# ORIGINAL 8-FIELD SNAPSHOT PRESERVED
#
# PUBLIC GET REQUEST ONLY
# NO AUTHENTICATED API
# NO DEMO OR REAL ORDER
# ZERO INDENTATION AT UNIT BOUNDARY
# ============================================================

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request

from decimal import Decimal, InvalidOperation


# ============================================================
# 3.1 MARKET RESPONSE VALIDATION
# PURE FUNCTION
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

        price = float(
            payload.get("price")
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID MARKET PRICE"
        ) from exc

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

    age_ms = (
        int(received_time_ms) - timestamp
    )

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
# 3.2 COIN-EQUIVALENT MARGIN CONVERSION
#
# USE DECIMAL FOR PRICE * COIN QUANTITY.
#
# THE SELECTED COIN PRICE IS A REFERENCE
# FOR INITIAL USDT MARGIN.
#
# THIS DOES NOT CALCULATE CONTRACT QUANTITY.
# ============================================================

def unit_3_resolve_initial_margin(
    config,
    market_price,
):

    if not isinstance(config, dict):

        raise RuntimeError(
            "UNIT 3 INVALID CONFIG FOR MARGIN"
        )

    margin = config.get("margin")

    if not isinstance(margin, dict):

        raise RuntimeError(
            "UNIT 3 MARGIN CONFIG MISSING"
        )

    mode = margin.get("mode")

    try:

        price = Decimal(
            str(market_price)
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID CONVERSION PRICE"
        ) from exc

    if not price.is_finite() or price <= 0:

        raise RuntimeError(
            "UNIT 3 INVALID CONVERSION PRICE"
        )

    if mode == "COIN_EQUIVALENT":

        try:

            coin_amount = Decimal(
                str(
                    margin[
                        "coin_equivalent_amount"
                    ]
                )
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
            KeyError,
        ) as exc:

            raise RuntimeError(
                "UNIT 3 INVALID COIN MARGIN"
            ) from exc

        if (
            not coin_amount.is_finite()
            or coin_amount <= 0
        ):

            raise RuntimeError(
                "UNIT 3 INVALID COIN AMOUNT"
            )

        resolved = (
            coin_amount * price
        )

        source = (
            "VERIFIED_MARK_PRICE_COIN_CONVERSION"
        )

    elif mode == "FIXED_USDT":

        try:

            resolved = Decimal(
                str(margin["fixed_usdt"])
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
            KeyError,
        ) as exc:

            raise RuntimeError(
                "UNIT 3 INVALID FIXED MARGIN"
            ) from exc

        source = "RENDER_FIXED_USDT"

    else:

        raise RuntimeError(
            "UNIT 3 UNSUPPORTED MARGIN MODE"
        )

    if (
        not resolved.is_finite()
        or resolved <= 0
    ):

        raise RuntimeError(
            "UNIT 3 INVALID RESOLVED MARGIN"
        )

    return {

        "mode": mode,

        "margin_usdt": resolved,

        "source": source,

        "market_price": price,
    }


# ============================================================
# 3.3 DETERMINISTIC VALIDATION TESTS
#
# NO WEEX REQUESTS IN THESE TESTS.
# NO ORDER SUBMISSION.
# ============================================================

def unit_3_validation_tests_v2():

    print("=" * 80, flush=True)

    print(
        "UNIT 3 UNIVERSAL VALIDATION START",
        flush=True,
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

        "price": "2.5000",

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
            flush=True,
        )

    def rejected(payload, expected_error):

        try:

            unit_3_validate_mark_payload(
                payload,
                symbol,
                now_ms,
            )

        except RuntimeError as exc:

            return str(exc) == expected_error

        return False

    validated = unit_3_validate_mark_payload(
        valid_payload,
        symbol,
        now_ms,
    )

    check(
        "VALID SYMBOL",
        valid_payload["symbol"] == symbol,
    )

    check(
        "VALID MARK PRICE",
        validated["price"] == 2.5,
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

    check(
        "REJECT WRONG SYMBOL",
        rejected(
            {
                **valid_payload,
                "symbol": "INVALID_SYMBOL",
            },
            "UNIT 3 RESPONSE SYMBOL MISMATCH",
        ),
    )

    check(
        "REJECT ZERO PRICE",
        rejected(
            {
                **valid_payload,
                "price": "0",
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE",
        ),
    )

    check(
        "REJECT NEGATIVE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "-1",
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE",
        ),
    )

    check(
        "REJECT NONNUMERIC PRICE",
        rejected(
            {
                **valid_payload,
                "price": "invalid",
            },
            "UNIT 3 INVALID MARKET PRICE",
        ),
    )

    check(
        "REJECT NONFINITE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "nan",
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE",
        ),
    )

    check(
        "REJECT STALE DATA",
        rejected(
            {
                **valid_payload,
                "time": now_ms - 130000,
            },
            "UNIT 3 STALE MARKET DATA",
        ),
    )

    check(
        "REJECT FUTURE TIMESTAMP",
        rejected(
            {
                **valid_payload,
                "time": now_ms + 20000,
            },
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE",
        ),
    )

    check(
        "REJECT MISSING TIMESTAMP",
        rejected(
            {
                "symbol": symbol,
                "price": "2.5",
            },
            "UNIT 3 INVALID MARKET TIMESTAMP",
        ),
    )

    check(
        "REJECT INVALID PAYLOAD",
        rejected(
            [],
            "UNIT 3 INVALID RESPONSE TYPE",
        ),
    )

    # --------------------------------------------------------
    # MARGIN CONVERSION VALIDATION
    # --------------------------------------------------------

    synthetic_config = {

        "margin": {

            "mode": "COIN_EQUIVALENT",

            "coin_equivalent_amount": 1.0,

            "fixed_usdt": 2.0,
        }
    }

    converted = unit_3_resolve_initial_margin(
        synthetic_config,
        "2.50",
    )

    check(
        "ONE COIN MARGIN CONVERSION",
        converted["margin_usdt"]
        == Decimal("2.50"),
    )

    synthetic_config["margin"][
        "coin_equivalent_amount"
    ] = 2.0

    converted_two = unit_3_resolve_initial_margin(
        synthetic_config,
        "2.50",
    )

    check(
        "TWO COIN MARGIN CONVERSION",
        converted_two["margin_usdt"]
        == Decimal("5.00"),
    )

    synthetic_config["margin"]["mode"] = (
        "FIXED_USDT"
    )

    fixed_result = unit_3_resolve_initial_margin(
        synthetic_config,
        "2.50",
    )

    check(
        "FIXED USDT MARGIN",
        fixed_result["margin_usdt"]
        == Decimal("2.0"),
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
            "UNIT 3 UNIVERSAL VALIDATION FAILED"
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
# 3.4 ACTUAL WEEX PUBLIC MARKET DATA
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)

    log(
        "UNIVERSAL WEEX UNIT 3 V1 START"
    )

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:

        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 1 NOT READY"
        )

    if FRESH_UNIT_2_OPTIMIZATION_READY is not True:

        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 NOT READY"
        )

    if FRESH_UNIT_3_OPTIMIZATION_READY is not True:

        raise RuntimeError(
            "UNIT 3 TEST VALIDATION NOT READY"
        )

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):

        raise RuntimeError(
            "UNIT 3 INVALID UNIT 2 CONFIG"
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

    # ========================================================
    # 3.5 EXCHANGE CONFIGURATION VALIDATION
    # ========================================================

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

    if (
        not isinstance(market_symbol, str)
        or not market_symbol
    ):

        raise RuntimeError(
            "UNIT 3 MARKET SYMBOL MISSING"
        )

    # Confirm symbol has not changed between
    # Unit 2 initialization and Unit 3 startup.

    if market_symbol != os.getenv(
        "TRADING_SYMBOL",
        "",
    ).strip().upper():

        raise RuntimeError(
            "UNIT 3 SYMBOL ENVIRONMENT MISMATCH"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":

        raise RuntimeError(
            "UNIT 3 INVALID EXECUTION ENVIRONMENT"
        )

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:

        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
        )

    # --------------------------------------------------------
    # PRESERVE ORIGINAL UNIT-LOCAL SAFETY GATE
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
                "UNIT 3 UNSAFE CONFIGURATION: "
                + key
            )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 V2 CONFIG",
        flush=True,
    )

    print(
        "UNIT 3 SELECTED SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True,
    )

    # ========================================================
    # 3.6 WEEX V3 PUBLIC MARK PRICE REQUEST
    #
    # SAME PUBLIC ENDPOINT AS REFERENCE MODELS.
    # ONLY THE SYMBOL IS NOW DYNAMIC.
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
                "WEEX-Universal-Market-Data-V1",
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

    # ========================================================
    # 3.7 PERFORM PUBLIC MARKET REQUEST
    # ========================================================

    started = time.monotonic()

    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
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
            flush=True,
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            error_body[:500],
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 WEEX MARKET HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 CONNECTION ERROR =",
            repr(exc.reason),
            flush=True,
        )

        raise RuntimeError(
            "UNIT 3 WEEX CONNECTION FAILED"
        ) from exc

    except Exception as exc:

        print(
            "UNIT 3 UNEXPECTED REQUEST ERROR =",
            repr(exc),
            flush=True,
        )

        raise

    received_time_ms = int(
        time.time() * 1000
    )

    latency_ms = round(
        (
            time.monotonic() - started
        ) * 1000,
        2,
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

    # ========================================================
    # 3.8 VERIFY LIVE MARKET PRICE AND TIMESTAMP
    # ========================================================

    validated = unit_3_validate_mark_payload(

        payload=payload,

        expected_symbol=market_symbol,

        received_time_ms=received_time_ms,
    )

    live_price = validated["price"]

    exchange_time_ms = validated[
        "exchange_time_ms"
    ]

    market_age_ms = validated[
        "market_age_ms"
    ]

    # ========================================================
    # 3.9 PRESERVE ORIGINAL UNIT 3 -> UNIT 4 CONTRACT
    #
    # EXACT ORIGINAL EIGHT SNAPSHOT FIELDS.
    # ========================================================

    market_snapshot = {

        "exchange": "WEEX",

        "api_version": "V3",

        "symbol": market_symbol,

        "price": live_price,

        "price_type": "MARK",

        "exchange_time_ms":
            exchange_time_ms,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE",

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
    # 3.10 RESOLVE INITIAL MARGIN
    #
    # ONCE PRICE IS VERIFIED, CONVERT ANY
    # COIN-EQUIVALENT MARGIN TO USDT.
    #
    # PRESERVE UNIT 2 CONFIG AND LEGACY
    # STRATEGY INTERFACE FOR LATER UNITS.
    # ========================================================

    resolved = unit_3_resolve_initial_margin(
        config,
        live_price,
    )

    resolved_margin_usdt = float(
        resolved["margin_usdt"]
    )

    if (
        not math.isfinite(resolved_margin_usdt)
        or resolved_margin_usdt <= 0
    ):

        raise RuntimeError(
            "UNIT 3 RESOLVED MARGIN NOT REPRESENTABLE"
        )

    config["margin"][
        "resolved_initial_margin_usdt"
    ] = resolved_margin_usdt

    config["margin"][
        "resolved_market_price"
    ] = live_price

    config["margin"][
        "resolved_price_time_ms"
    ] = exchange_time_ms

    config["margin"][
        "resolved_margin_source"
    ] = resolved["source"]

    strategy = config.get("strategy")

    if not isinstance(strategy, dict):

        raise RuntimeError(
            "UNIT 3 STRATEGY CONFIG MISSING"
        )

    # Maintain the legacy value for later units.
    # This is a proposed margin, not permission
    # to submit an order.

    strategy[
        "initial_fixed_usdt"
    ] = resolved_margin_usdt

    # ========================================================
    # 3.11 FINAL REPORT
    # ========================================================

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True,
    )

    print(
        "UNIT 3 SELECTED SYMBOL =",
        market_symbol,
        flush=True,
    )

    print(
        "UNIT 3 LIVE MARK PRICE =",
        live_price,
        flush=True,
    )

    print(
        "UNIT 3 MARKET TIMESTAMP =",
        exchange_time_ms,
        flush=True,
    )

    print(
        "UNIT 3 MARKET AGE MS =",
        market_age_ms,
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
        "UNIT 3 INITIAL MARGIN MODE =",
        resolved["mode"],
        flush=True,
    )

    print(
        "UNIT 3 RESOLVED INITIAL MARGIN USDT =",
        resolved_margin_usdt,
        flush=True,
    )

    print(
        "UNIT 3 MARGIN SOURCE =",
        resolved["source"],
        flush=True,
    )

    print(
        "UNIT 3 CONTRACT PRECISION VERIFIED =",
        config.get(
            "market_precision",
            {},
        ).get(
            "precision_verified",
            False,
        ),
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

    log(
        "FRESH RECONSTRUCTION UNIT 3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# 3.12 RUN VALIDATION TESTS FIRST
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v2()
)


# ============================================================
# 3.13 RUN REAL WEEX PUBLIC MARKET READ
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# 3.14 FINAL UNIT 3 READINESS
# ============================================================

if (
    not isinstance(
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
        dict,
    )
    or FRESH_RECONSTRUCTION_MARKET_SNAPSHOT.get(
        "read_only"
    ) is not True
    or FRESH_RECONSTRUCTION_MARKET_SNAPSHOT.get(
        "symbol"
    ) != FRESH_RECONSTRUCTION_CONFIG[
        "exchange"
    ]["market_symbol"]
):

    raise RuntimeError(
        "UNIT 3 MARKET HANDOVER NOT READY"
    )


print(
    "UNIVERSAL UNIT 3 OPTIMIZATION READY =",
    FRESH_UNIT_3_OPTIMIZATION_READY,
    flush=True,
)


# ============================================================
# END COMPLETE UNIVERSAL UNIT 3 V1
# UNIT 4 FOLLOWS
# ZERO INDENTATION
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

    if (
        symbol
        != os.getenv(
            "TRADING_SYMBOL", ""
        ).strip().upper()
        or market.get("symbol") != symbol
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT4 MARKET HANDOVER FAILED"
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

