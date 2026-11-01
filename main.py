
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
# UNIVERSAL WEEX HYBRID TRADING BOT
# COMPLETE UNIT 2 V1
#
# ADAPTED FROM:
# 17248-LINE B1-B5 WORKING MODEL
# 16414-LINE REVERSIBLE ATR HEDGE MODEL
#
# UNIVERSAL SYMBOL CONFIGURATION
# MANUAL LONG / SHORT LEVERAGE
# COIN-EQUIVALENT OR FIXED USDT INITIAL MARGIN
# UNIFIED SCALP / STRUCTURE / BREAKOUT
# ONE ATR HEDGE + RECOVERY CYCLE
# CONDITIONAL B1-B5 AFTER FIRST CYCLE
# TP1 20% NET ROI
# TP2 40% NET ROI
# TP3 DYNAMIC NET ROI TRAILING
# SECURED PROFIT LEDGER CONTRACT
# EXPOSURE CAP DEFAULT 100%
#
# DEMO ACCOUNT ONLY
# NO EXCHANGE WRITE IN UNIT 2
# ZERO INDENTATION
# ============================================================

import os
import re
from decimal import Decimal, InvalidOperation


# ============================================================
# 2.1 SHARED NUMBER VALIDATION
# ============================================================

def unit_2_v1_number(
    value,
    name,
    allow_zero=False,
):

    if isinstance(value, bool):
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


def unit_2_v1_require(
    condition,
    message,
):

    if not condition:
        raise RuntimeError(
            "UNIT 2 CONFIG INVALID: "
            + message
        )


def unit_2_v1_environment(
    name,
    default,
):

    value = os.getenv(name)

    if value is None or not value.strip():
        return str(default)

    return value.strip()


def unit_2_v1_bool(
    name,
    default=False,
):

    raw = unit_2_v1_environment(
        name,
        "true" if default else "false",
    ).lower()

    if raw in ("true", "1", "yes", "on"):
        return True

    if raw in ("false", "0", "no", "off"):
        return False

    raise RuntimeError(
        "UNIT 2 INVALID BOOLEAN " + name
    )


# ============================================================
# 2.2 COMPLETE CENTRAL CONFIGURATION
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)

    log(
        "UNIVERSAL WEEX UNIT 2 V1 START"
    )

    require = unit_2_v1_require
    number = unit_2_v1_number
    setting = unit_2_v1_environment

    require(
        FRESH_RECONSTRUCTION_UNIT_1_READY is True,
        "UNIT 1 NOT READY",
    )

    # ========================================================
    # 2.3 UNIVERSAL TRADING SYMBOL
    #
    # MARKET SYMBOL IS THE ACTUAL CONTRACT SYMBOL.
    # DEMO SYMBOL MUST BE VERIFIED SEPARATELY.
    #
    # NEVER AUTOMATICALLY ADD S TO CREATE A DEMO SYMBOL.
    # ========================================================

    market_symbol = setting(
        "TRADING_SYMBOL",
        "NEARUSDT",
    ).upper()

    require(
        bool(
            re.fullmatch(
                r"[A-Z0-9]{2,30}",
                market_symbol,
            )
        ),
        "INVALID TRADING SYMBOL",
    )

    require(
        market_symbol.endswith("USDT"),
        "ONLY USDT CONTRACTS SUPPORTED",
    )

    base_coin = market_symbol[:-4]

    require(
        bool(base_coin),
        "INVALID BASE COIN",
    )

    configured_demo_symbol = setting(
        "WEEX_DEMO_SYMBOL",
        "",
    ).upper()

    # Known legacy BTC demo symbol from the references.
    # Other demo symbols require explicit verification.

    if market_symbol == "BTCUSDT":

        demo_symbol = (
            configured_demo_symbol
            or "BTCSUSDT"
        )

    else:

        demo_symbol = (
            configured_demo_symbol
            or None
        )

    # Unit 2 does not claim that a configured demo
    # symbol is supported by the exchange.

    demo_symbol_verified = False

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

        "demo_symbol_verified":
            demo_symbol_verified,

        "contract_metadata_verified": False,

        "market_symbol_source":
            "RENDER_TRADING_SYMBOL",
    }

    # ========================================================
    # 2.4 INITIAL MARGIN
    #
    # MODE 1:
    # COIN_EQUIVALENT
    # 1 COIN MULTIPLIED BY VERIFIED MARKET PRICE
    # GIVES THE INITIAL USDT MARGIN.
    #
    # MODE 2:
    # FIXED_USDT
    # PRESERVES HISTORICAL ENTRY MARGIN VARIABLES.
    #
    # CONVERSION IS PERFORMED BY A LATER UNIT.
    # ========================================================

    margin_mode = setting(
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

    coin_margin = number(
        setting(
            "INITIAL_MARGIN_COINS",
            "1",
        ),
        "INITIAL MARGIN COINS",
    )

    primary_margin = os.getenv(
        "INITIAL_ENTRY_MARGIN_USDT"
    )

    secondary_margin = os.getenv(
        "ENTRY_FIXED_USDT"
    )

    tertiary_margin = os.getenv(
        "ENTRY_MARGIN_USDT"
    )

    if primary_margin and primary_margin.strip():

        fixed_margin_raw = primary_margin.strip()
        margin_source = "INITIAL_ENTRY_MARGIN_USDT"

    elif secondary_margin and secondary_margin.strip():

        fixed_margin_raw = secondary_margin.strip()
        margin_source = "ENTRY_FIXED_USDT"

    elif tertiary_margin and tertiary_margin.strip():

        fixed_margin_raw = tertiary_margin.strip()
        margin_source = "ENTRY_MARGIN_USDT"

    else:

        fixed_margin_raw = "0.5"
        margin_source = "DEFAULT_0_5"

    fixed_margin = number(
        fixed_margin_raw,
        "FIXED USDT MARGIN",
    )

    initial_margin_usdt = (
        float(fixed_margin)
        if margin_mode == "FIXED_USDT"
        else None
    )

    margin = {

        "mode": margin_mode,

        "coin_equivalent_amount":
            float(coin_margin),

        "fixed_usdt":
            float(fixed_margin),

        "fixed_margin_source":
            margin_source,

        "resolved_initial_margin_usdt":
            initial_margin_usdt,

        "market_price_required":
            margin_mode == "COIN_EQUIVALENT",

        "conversion_required":
            margin_mode == "COIN_EQUIVALENT",

        "conversion_price_type": "MARK",

        "conversion_freshness_required": True,

        "exchange_minimum_validation_required": True,
    }

    # ========================================================
    # 2.5 MANUAL LONG AND SHORT LEVERAGE
    #
    # PRESERVE 16414 MODEL RENDER NAMES.
    #
    # LEVERAGE SET MANUALLY ON WEEX DEMO.
    # SAME VALUE ENTERED INTO RENDER.
    #
    # NO AUTOMATIC WEEX LEVERAGE CHANGE.
    # ========================================================

    long_raw = setting(
        "WEEX_DEMO_LONG_LEVERAGE",
        "10",
    )

    short_raw = setting(
        "WEEX_DEMO_SHORT_LEVERAGE",
        "10",
    )

    long_leverage = number(
        long_raw,
        "LONG LEVERAGE",
    )

    short_leverage = number(
        short_raw,
        "SHORT LEVERAGE",
    )

    # The earlier 200x local ceiling is retained
    # as a configuration sanity check only.
    # The actual contract maximum must be checked
    # independently before execution.

    require(
        long_leverage <= Decimal("200"),
        "LONG LEVERAGE ABOVE LOCAL CEILING",
    )

    require(
        short_leverage <= Decimal("200"),
        "SHORT LEVERAGE ABOVE LOCAL CEILING",
    )

    leverage = {

        "source":
            "RENDER_MANUAL_CONFIGURATION",

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

        "contract_limit_validation_required": True,

        "position_side_specific": True,
    }

    # ========================================================
    # 2.6 EXPOSURE CAP
    #
    # PRESERVE DEFAULT 100% FROM 16414.
    # HARD MAXIMUM 100%.
    #
    # EXPOSURE IS NOT A MANDATORY TRADING TARGET.
    # ========================================================

    exposure_cap = number(
        setting(
            "EXPOSURE_CAP_PERCENT",
            "100",
        ),
        "EXPOSURE CAP",
    )

    require(
        Decimal("0") < exposure_cap
        <= Decimal("100"),
        "EXPOSURE CAP MUST BE 0-100%",
    )

    exposure = {

        "cap_percent": float(exposure_cap),

        "maximum_allowed_percent": 100.0,

        "basis": "TRADING_ACCOUNT_EQUITY",

        "include_initial_margin": True,

        "include_open_hedge_margin": True,

        "include_filled_backups": True,

        "include_pending_margin": True,

        "prevent_orders_exceeding_cap": True,

        "final_failed_trade_exit":
            "MAX_EXPOSURE_CAP",

        "early_profit_exit_before_tp1": False,

        "liquidation_distance_strategy_exit":
            False,

        "exchange_liquidation_risk_monitoring":
            True,

        "forced_exchange_liquidation_possible":
            True,

        "margin_reservation_required": True,

        "secured_profit_excluded_from_budget":
            True,
    }

    # ========================================================
    # 2.7 CENTRAL TAKE-PROFIT SETTINGS
    #
    # DEFAULT 20% / 40% NET ROI
    # ALLOCATION 10 / 20 / 70
    #
    # FINAL TP PRICES CALCULATED AFTER VERIFIED FILL.
    # ========================================================

    tp1_target = number(
        setting(
            "TP1_NET_ROI_PERCENT",
            "20",
        ),
        "TP1 NET ROI",
    )

    tp2_target = number(
        setting(
            "TP2_NET_ROI_PERCENT",
            "40",
        ),
        "TP2 NET ROI",
    )

    tp1_allocation = number(
        setting(
            "TP1_ALLOCATION_PERCENT",
            "10",
        ),
        "TP1 ALLOCATION",
        True,
    )

    tp2_allocation = number(
        setting(
            "TP2_ALLOCATION_PERCENT",
            "20",
        ),
        "TP2 ALLOCATION",
        True,
    )

    tp3_allocation = number(
        setting(
            "TP3_ALLOCATION_PERCENT",
            "70",
        ),
        "TP3 ALLOCATION",
        True,
    )

    require(
        (
            tp1_allocation
            + tp2_allocation
            + tp3_allocation
        ) == Decimal("100"),
        "TP ALLOCATION MUST TOTAL 100%",
    )

    require(
        tp1_allocation > 0
        and tp2_allocation > 0
        and tp3_allocation > 0,
        "ALL TP ALLOCATIONS MUST BE POSITIVE",
    )

    require(
        tp2_target > tp1_target,
        "TP2 MUST EXCEED TP1",
    )

    # Trailing percentages below are NET ROI
    # percentages, not price-movement percentages.

    trailing_reference = number(
        setting(
            "TP3_TRAILING_REFERENCE_ROI_PERCENT",
            "3",
        ),
        "TRAILING REFERENCE",
    )

    trailing_min = number(
        setting(
            "TP3_TRAILING_MIN_ROI_PERCENT",
            "1",
        ),
        "TRAILING MINIMUM",
    )

    trailing_max = number(
        setting(
            "TP3_TRAILING_MAX_ROI_PERCENT",
            "6",
        ),
        "TRAILING MAXIMUM",
    )

    require(
        trailing_min
        <= trailing_reference
        <= trailing_max,
        "INVALID TRAILING RANGE",
    )

    # ========================================================
    # 2.8 FEE AND NET ROI POLICY
    #
    # CONFIRMED ENTRY COSTS ARE USED WHEN AVAILABLE.
    # FUTURE EXIT COSTS ARE ESTIMATED UNTIL FILL.
    #
    # HEDGE AND BACKUP COSTS ARE EXCLUDED FROM
    # THE ORIGINAL TP PRICE CALCULATION.
    # ========================================================

    taker_fee = number(
        setting(
            "ESTIMATED_TAKER_FEE_PERCENT",
            "0.08",
        ),
        "TAKER FEE",
        True,
    )

    maker_fee = number(
        setting(
            "ESTIMATED_MAKER_FEE_PERCENT",
            "0.02",
        ),
        "MAKER FEE",
        True,
    )

    require(
        taker_fee < Decimal("100")
        and maker_fee < Decimal("100"),
        "INVALID FEE RATE",
    )

    fee_policy = {

        "entry_fee_source":
            "ACTUAL_CONFIRMED_FILL",

        "exit_fee_source":
            "ESTIMATE_THEN_RECONCILE",

        "estimated_taker_fee_percent":
            float(taker_fee),

        "estimated_maker_fee_percent":
            float(maker_fee),

        "include_actual_entry_fee": True,

        "include_estimated_exit_fee": True,

        "include_actual_funding_to_date": True,

        "include_estimated_future_funding": True,

        "include_expected_exit_slippage": True,

        "include_applicable_transfer_cost": True,

        "avoid_double_counting_spread": True,

        "include_future_hedge_costs_in_initial_tp":
            False,

        "include_future_backup_costs_in_initial_tp":
            False,

        "reconcile_actual_exit_fees": True,

        "target_calculation_after_initial_fill":
            True,

        "provisional_target_before_entry":
            True,
    }

    # ========================================================
    # 2.9 TP PROFIT PROTECTION
    # ========================================================

    be_buffer = number(
        setting(
            "BE_PLUS_BUFFER_ROI_PERCENT",
            "2",
        ),
        "BREAK EVEN BUFFER",
        True,
    )

    profit_protection = {

        "tp1_secure_profit_first": True,

        "tp1_require_confirmed_fill": True,

        "tp1_record_actual_net_profit": True,

        "tp1_protect_remaining_trade_balance":
            True,

        "tp1_protection_mode":
            "DYNAMIC_BREAK_EVEN_PLUS",

        "tp1_be_buffer_roi_percent":
            float(be_buffer),

        "tp2_secure_profit_first": True,

        "tp2_require_confirmed_fill": True,

        "tp2_protection_mode":
            "DYNAMIC_NET_ROI_TRAILING",

        "tp3_protect_remaining_trade_balance":
            True,

        "secured_profit_ledger_enabled": True,

        "secured_profit_reuse_allowed": False,

        "secured_profit_excluded_from_be":
            True,

        "secured_profit_excluded_from_trailing":
            True,

        "actual_external_profit_segregation":
            False,

        "reconcile_confirmed_positions": True,
    }

    # ========================================================
    # 2.10 REVERSIBLE ATR HEDGE
    #
    # PRESERVE 16414 H1 H2 R1 R2 CONTRACT.
    # CHANGE REPEATABLE TO FALSE.
    #
    # ONLY ONE COMPLETE HEDGE/RECOVERY CYCLE.
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

        # H1 - adverse one ATR

        "h1_atr_multiplier": 1.0,

        "h1_original_fraction": 0.50,

        "h1_opposite_fraction": 0.50,

        # H2 - adverse two ATR

        "h2_atr_multiplier": 2.0,

        "h2_original_fraction": 0.00,

        "h2_opposite_fraction": 1.00,

        # R1 - recovery toward one ATR

        "r1_atr_multiplier": 1.0,

        "r1_original_fraction": 0.50,

        "r1_opposite_fraction": 0.50,

        # R2 - return to original entry

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

        "liquidation_risk_monitoring_enabled": True,

        "bot_mode_independent": True,

        "real_cash_enabled": False,
    }

    # ========================================================
    # 2.11 HYBRID B1-B5 BACKUPS
    #
    # ADAPTED FROM 17248 MODEL.
    #
    # BACKUPS ONLY AFTER ONE HEDGE RECOVERY CYCLE
    # AND A FRESH QUALIFIED ADVERSE REVERSAL.
    #
    # SIZING IS A PERCENTAGE OF AVAILABLE BALANCE.
    # NO MULTIPLIER LADDER.
    # ========================================================

    backup_percent = number(
        setting(
            "BACKUP_MARGIN_PERCENT",
            "0.5",
        ),
        "BACKUP MARGIN PERCENT",
    )

    backup_buffer = number(
        setting(
            "BACKUP_BUFFER_PERCENT",
            "0.3",
        ),
        "BACKUP BUFFER PERCENT",
    )

    require(
        backup_percent <= Decimal("100"),
        "BACKUP PERCENT ABOVE 100%",
    )

    require(
        backup_buffer < Decimal("100"),
        "INVALID BACKUP BUFFER",
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

        # Correct directional factors for a trigger
        # located inside the liquidation boundary.
        #
        # LONG liquidation is normally below market.
        # SHORT liquidation is normally above market.
        #
        # A positive 0.3% inward buffer is therefore:
        # LONG: LQ * 1.003
        # SHORT: LQ * 0.997

        "backup_long_liquidation_factor":
            float(
                Decimal("1")
                + backup_buffer / Decimal("100")
            ),

        "backup_short_liquidation_factor":
            float(
                Decimal("1")
                - backup_buffer / Decimal("100")
            ),

        "fresh_market_confirmation_required": True,

        "sequential_execution_required": True,

        "one_backup_at_a_time": True,

        "confirmed_fill_required": True,

        "recalculate_balance_after_fill": True,

        "recalculate_liquidation_after_fill": True,

        "recalculate_exposure_after_fill": True,

        "progressive_backup_funding": True,

        "full_ladder_reservation_required": False,

        "backup_multipliers_enabled": False,

        "exposure_cap_enforced": True,

        "secured_profit_funding_allowed": False,

        "stop_new_backups_at_cap": True,

        "bot_mode_independent": True,
    }

    # ========================================================
    # 2.12 CENTRAL STRATEGY
    #
    # PRESERVE ORIGINAL FIELD NAMES WHERE POSSIBLE.
    # ========================================================

    strategy = {

        "initial_fixed_usdt":
            initial_margin_usdt,

        "initial_margin_mode":
            margin_mode,

        "initial_margin_coin_equivalent":
            float(coin_margin),

        "initial_margin_percent": 5.0,

        "exposure_cap_percent":
            float(exposure_cap),

        "exposure_cap_max_percent": 100.0,

        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,

        "exposure_includes_open_hedge_margin": True,

        "exposure_includes_filled_backups": True,

        "exposure_includes_pending_margin": True,

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
            backup["backup_long_liquidation_factor"],

        "backup_short_liquidation_factor":
            backup["backup_short_liquidation_factor"],

        "progressive_backup_funding": True,

        "full_ladder_reservation_required": False,

        "tp1_allocation_percent":
            float(tp1_allocation),

        "tp2_allocation_percent":
            float(tp2_allocation),

        "tp3_allocation_percent":
            float(tp3_allocation),

        "tp1_net_roi_floor_percent":
            float(tp1_target),

        "tp2_net_roi_floor_percent":
            float(tp2_target),

        "tp1_tp2_min_roi_separation_percent":
            float(tp2_target - tp1_target),

        "tp3_trailing_reference_percent":
            float(trailing_reference),

        "tp3_trailing_min_percent":
            float(trailing_min),

        "tp3_trailing_max_percent":
            float(trailing_max),

        "tp3_trailing_unit": "NET_ROI_PERCENT",

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
    # 2.13 UNIVERSAL MARKET PRECISION
    #
    # DO NOT COPY BTC MINIMUM QUANTITY OR TICK SIZE.
    #
    # MARKET RULES ARE RESOLVED FROM CONTRACT DATA
    # BY THE LATER VALIDATION UNITS.
    # ========================================================

    market_precision = {

        "quantity_step": None,

        "minimum_quantity": None,

        "price_step": None,

        "contract_size": None,

        "minimum_notional": None,

        "maximum_leverage": None,

        "precision_verified": False,

        "source": "PENDING_WEEX_CONTRACT_METADATA",

        "tp_quantity_step_aware": True,

        "hedge_quantity_step_aware": True,

        "validate_tp1_tp2_tp3": True,

        "validate_50_percent_hedge": True,

        "reject_infeasible_initial_entry": True,
    }

    # ========================================================
    # 2.14 UNIFIED ENTRY QUALIFICATION
    #
    # ADAPTED FROM BOTH REFERENCE MODELS.
    #
    # PRESERVE PRIORITIES AND EXISTING SETTINGS.
    # ONE INITIAL ORDER FROM A COORDINATED DECISION.
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

            "scalp_requires_higher_modes_clear": True,

            "signal_expiry_seconds": 120,

            "candidate_expiry_seconds": 120,

            "spike_count_rejection_above": 2,

            "reject_late_impulse_entry": True,

            "target_reachability_enabled": True,

            "estimated_cost_check_enabled": True,

            "positive_expected_value_required": True,

            "coin_specific_tuning_required": True,
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

            "estimated_taker_fee_percent":
                float(taker_fee),

            "estimated_slippage_percent": 0.0,

            "include_entry_fee": True,

            "include_exit_fee": True,

            "minimum_fee_coverage_multiplier": 2.0,

            "require_positive_estimated_net": True,

            "minimum_net_roi_percent": 2.0,
        },
    }

    # ========================================================
    # 2.15 SAFETY AND EXECUTION RESPONSIBILITY
    #
    # UNIT 2 ONLY DEFINES CONFIGURATION.
    # LATER VERIFIED UNITS HANDLE DEMO EXECUTION.
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
    # 2.17 CONTRACT VALIDATION
    # ========================================================

    require(
        exchange["name"] == "WEEX",
        "EXCHANGE",
    )

    require(
        exchange["api_version"] == "V3",
        "API VERSION",
    )

    require(
        config["execution_environment"] == "DEMO",
        "DEMO ENVIRONMENT",
    )

    require(
        strategy["max_backups"] == 5,
        "BACKUP COUNT",
    )

    require(
        strategy["anti_duplicate_orders"] is True,
        "ANTI DUPLICATE",
    )

    require(
        hedge["repeatable"] is False,
        "HEDGE REPEATABILITY",
    )

    require(
        hedge["max_completed_cycles"] == 1,
        "HEDGE CYCLE LIMIT",
    )

    require(
        backup["require_first_hedge_cycle_consumed"]
        is True,
        "BACKUP ACTIVATION",
    )

    require(
        hedge["required_position_mode"] == "HEDGE",
        "POSITION MODE REQUIREMENT",
    )

    for stage in (
        "h1",
        "h2",
        "r1",
        "r2",
    ):

        original_fraction = Decimal(
            str(
                hedge[
                    stage + "_original_fraction"
                ]
            )
        )

        opposite_fraction = Decimal(
            str(
                hedge[
                    stage + "_opposite_fraction"
                ]
            )
        )

        require(
            original_fraction + opposite_fraction
            == Decimal("1"),
            stage.upper() + " ALLOCATION",
        )

    require(
        qualification["common"]["mode_priority"]
        == (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        ),
        "STRATEGY PRIORITY",
    )

    require(
        qualification["scalp"]["quality_threshold"]
        == 70.0,
        "SCALP QUALITY",
    )

    require(
        fee_policy[
            "include_future_hedge_costs_in_initial_tp"
        ] is False,
        "HEDGE COST EXCLUSION",
    )

    require(
        fee_policy[
            "include_future_backup_costs_in_initial_tp"
        ] is False,
        "BACKUP COST EXCLUSION",
    )

    require(
        profit_protection[
            "secured_profit_reuse_allowed"
        ] is False,
        "SECURED PROFIT ISOLATION",
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
        "PASS: UNIVERSAL UNIT 2 CONFIG CREATED",
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
        "DEMO SYMBOL VERIFIED =",
        demo_symbol_verified,
        flush=True,
    )

    print(
        "INITIAL MARGIN MODE =",
        margin_mode,
        flush=True,
    )

    print(
        "INITIAL COIN EQUIVALENT =",
        float(coin_margin),
        flush=True,
    )

    print(
        "FIXED USDT MARGIN =",
        float(fixed_margin),
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
        "POST FIRST HEDGE = CONDITIONAL B1-B5",
        flush=True,
    )

    print(
        "BACKUP MARGIN AVAILABLE BALANCE % =",
        float(backup_percent),
        flush=True,
    )

    print(
        "TP1 NET ROI TARGET =",
        float(tp1_target),
        flush=True,
    )

    print(
        "TP2 NET ROI TARGET =",
        float(tp2_target),
        flush=True,
    )

    print(
        "TP ALLOCATION =",
        float(tp1_allocation),
        float(tp2_allocation),
        float(tp3_allocation),
        flush=True,
    )

    print(
        "TP CALCULATION = AFTER CONFIRMED ENTRY",
        flush=True,
    )

    print(
        "FUTURE HEDGE/BACKUP COSTS IN INITIAL TP = NONE",
        flush=True,
    )

    print(
        "POST TP1 = SECURE PROFIT + DYNAMIC BREAK EVEN",
        flush=True,
    )

    print(
        "POST TP2 = SECURE PROFIT + DYNAMIC TRAILING",
        flush=True,
    )

    print(
        "SECURED PROFIT REUSE = DISABLED BY POLICY",
        flush=True,
    )

    print(
        "MARKET PRECISION = PENDING VERIFICATION",
        flush=True,
    )

    print(
        "DEMO ORDER EXECUTION = LATER UNITS",
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
# 2.19 RUN COMPLETE UNIT 2
# PRESERVE ORIGINAL GLOBAL INTERFACE
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# 2.20 UNIT 2 -> UNIT 3 READINESS CONTRACT
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
        FRESH_RECONSTRUCTION_CONFIG.get("strategy"),
        dict,
    )

    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get("qualification"),
        dict,
    )

    and isinstance(
        FRESH_RECONSTRUCTION_CONFIG.get("leverage"),
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
    ].get("hedge", {}).get("mode")
    == "REVERSIBLE_ATR_TWO_STAGE"

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("hedge", {}).get("max_completed_cycles") == 1

    and FRESH_RECONSTRUCTION_CONFIG[
        "strategy"
    ].get("backup", {}).get("max_backups") == 5

    and FRESH_RECONSTRUCTION_CONFIG[
        "leverage"
    ].get("source")
    == "RENDER_MANUAL_CONFIGURATION"

    and FRESH_RECONSTRUCTION_CONFIG[
        "universal_symbol_enabled"
    ] is True
)


if not FRESH_UNIT_2_OPTIMIZATION_READY:

    raise RuntimeError(
        "UNIVERSAL UNIT 2 OPTIMIZATION READINESS FAILED"
    )


print(
    "UNIVERSAL UNIT 2 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True,
)


# ============================================================
# END COMPLETE UNIVERSAL UNIT 2 V1
# UNIT 3 FOLLOWS
# ZERO INDENTATION
# ============================================================
