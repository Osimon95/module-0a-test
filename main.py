
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
# START COMPLETE UNIT 2
# UNIVERSAL WEEX V3 DEMO CONFIGURATION
# RENDER-SELECTABLE COIN / USDT-DENOMINATED CAPITAL
# COMPATIBILITY: UNIT 1, UNIT 3-15 CONFIG INTERFACES
# NO EXCHANGE WRITES IN UNIT 2
# ZERO INDENTATION
# ============================================================

import os
import math
import re
from decimal import Decimal, InvalidOperation


# ============================================================
# 2.1 UNIVERSAL ENVIRONMENT HELPERS
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

    if number < 0 or (number == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 2 INVALID RANGE " + name
        )

    return number


def unit_2_adapted_env_number(
    names, default, minimum=0.0, maximum=None
):

    if isinstance(names, str):
        names = (names,)

    selected_name = None
    raw = None

    for name in names:
        candidate = os.getenv(name)

        if candidate is not None and candidate.strip():
            selected_name = name
            raw = candidate.strip()
            break

    if raw is None:
        selected_name = "DEFAULT"
        raw = str(default)

    number = float(
        unit_2_v9_number(
            raw, selected_name, allow_zero=(minimum == 0)
        )
    )

    if number < minimum:
        raise RuntimeError(
            "UNIT 2 BELOW MINIMUM: " + selected_name
        )

    if maximum is not None and number > maximum:
        raise RuntimeError(
            "UNIT 2 ABOVE MAXIMUM: " + selected_name
        )

    return number, selected_name


def unit_2_adapted_bool(name, default=False):

    raw = os.getenv(
        name, "true" if default else "false"
    ).strip().lower()

    if raw in ("1", "true", "yes", "on", "run"):
        return True

    if raw in ("0", "false", "no", "off", "pause"):
        return False

    raise RuntimeError(
        "UNIT 2 INVALID BOOLEAN: " + name
    )


def unit_2_adapted_require(condition, reason):

    if not condition:
        raise RuntimeError("UNIT 2 " + reason)


# ============================================================
# 2.2 SYMBOL SELECTION
# ============================================================

def unit_2_universal_symbol():

    symbol = os.getenv(
        "WEEX_SYMBOL", "NEARUSDT"
    ).strip().upper()

    symbol = symbol.replace("/", "").replace("-", "")

    if not re.fullmatch(r"[A-Z0-9]{2,20}USDT", symbol):
        raise RuntimeError(
            "UNIT 2 INVALID WEEX_SYMBOL: " + symbol
        )

    base = symbol[:-4]

    if not base:
        raise RuntimeError(
            "UNIT 2 EMPTY BASE COIN"
        )

    return symbol, base, "USDT"


# ============================================================
# 2.3 CONFIGURATION CONSTRUCTOR
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print(
        "ADAPTED WORKING MODEL UNIT 2 UNIVERSAL START",
        flush=True
    )

    if globals().get(
        "FRESH_RECONSTRUCTION_UNIT_1_READY"
    ) is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    market_symbol, base_coin, quote_coin = (
        unit_2_universal_symbol()
    )

    # ========================================================
    # CAPITAL: ALWAYS USDT, NEVER FIXED COIN QUANTITY
    # ========================================================

    entry_margin, entry_margin_source = (
        unit_2_adapted_env_number(
            (
                "INITIAL_ENTRY_MARGIN_USDT",
                "ENTRY_MARGIN_USDT",
                "ENTRY_FIXED_USDT",
            ),
            0.5,
            minimum=0.00000001
        )
    )

    long_leverage, long_leverage_source = (
        unit_2_adapted_env_number(
            (
                "WEEX_LEVERAGE_LONG",
                "WEEX_DEMO_LONG_LEVERAGE",
            ),
            0,
            minimum=0.00000001
        )
    )

    short_leverage, short_leverage_source = (
        unit_2_adapted_env_number(
            (
                "WEEX_LEVERAGE_SHORT",
                "WEEX_DEMO_SHORT_LEVERAGE",
            ),
            0,
            minimum=0.00000001
        )
    )

    exposure_cap, _ = unit_2_adapted_env_number(
        "EXPOSURE_CAP_PERCENT",
        100.0,
        minimum=0,
        maximum=100
    )

    backup_margin_percent, _ = (
        unit_2_adapted_env_number(
            "BACKUP_MARGIN_PERCENT",
            0.5,
            minimum=0,
            maximum=100
        )
    )

    backup_buffer_percent, _ = (
        unit_2_adapted_env_number(
            "BACKUP_BUFFER_PERCENT",
            0.3,
            minimum=0,
            maximum=99.999
        )
    )

    tp1_roi, _ = unit_2_adapted_env_number(
        "TP1_NET_ROI_PERCENT",
        20.0,
        minimum=0.00000001
    )

    tp2_roi, _ = unit_2_adapted_env_number(
        "TP2_NET_ROI_PERCENT",
        40.0,
        minimum=0.00000001
    )

    if tp2_roi <= tp1_roi:
        raise RuntimeError(
            "UNIT 2 TP2 MUST EXCEED TP1"
        )

    tp1_allocation, _ = unit_2_adapted_env_number(
        "TP1_ALLOCATION_PERCENT",
        10.0,
        minimum=0,
        maximum=100
    )

    tp2_allocation, _ = unit_2_adapted_env_number(
        "TP2_ALLOCATION_PERCENT",
        20.0,
        minimum=0,
        maximum=100
    )

    tp3_allocation = (
        100.0 - tp1_allocation - tp2_allocation
    )

    if tp3_allocation <= 0:
        raise RuntimeError(
            "UNIT 2 INVALID TP ALLOCATION"
        )

    fee_rate, _ = unit_2_adapted_env_number(
        "WEEX_TAKER_FEE_RATE",
        0.0008,
        minimum=0,
        maximum=0.1
    )

    slippage_rate, _ = unit_2_adapted_env_number(
        "ESTIMATED_SLIPPAGE_RATE",
        0.0002,
        minimum=0,
        maximum=0.1
    )

    funding_buffer_rate, _ = unit_2_adapted_env_number(
        "ESTIMATED_FUNDING_RATE",
        0.0,
        minimum=0,
        maximum=0.1
    )

    # ========================================================
    # SYMBOL-SPECIFIC DEMO CONTRACT
    # ========================================================
    # Never derive an executable symbol by guessing.
    # Public market symbol is separate from demo order symbol.
    # ========================================================

    demo_order_symbol = os.getenv(
        "WEEX_DEMO_ORDER_SYMBOL", ""
    ).strip().upper()

    if demo_order_symbol:
        if not re.fullmatch(
            r"[A-Z0-9]{4,30}", demo_order_symbol
        ):
            raise RuntimeError(
                "UNIT 2 INVALID DEMO ORDER SYMBOL"
            )
    else:
        demo_order_symbol = None

    # A user-entered symbol is not exchange verification.
    # Unit 12 must require an independent contract check.

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",

        "market_symbol": market_symbol,
        "base_coin": base_coin,
        "quote_coin": quote_coin,

        "demo_order_symbol": demo_order_symbol,
        "demo_symbol_candidate": demo_order_symbol,
        "demo_symbol_verified": False,

        "contract_precision_verified": False,
        "contract_value_verified": False,

        "margin_currency": "USDT",
        "settlement_currency": "USDT",
        "pnl_currency": "USDT",
    }

    # ========================================================
    # ACCOUNT / ORDER SAFETY
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

    # These flags describe permissions of Unit 2 itself.
    # They must not be treated as a permanent global ban
    # on independently verified Unit 12 demo execution.

    # ========================================================
    # CENTRAL STRATEGY CONFIGURATION
    # ========================================================

    strategy = {
        "initial_fixed_usdt": entry_margin,
        "initial_entry_margin_usdt": entry_margin,
        "entry_margin_usdt": entry_margin,
        "entry_margin_source": entry_margin_source,

        "initial_margin_percent": 5.0,

        "long_leverage": long_leverage,
        "short_leverage": short_leverage,
        "leverage_long": long_leverage,
        "leverage_short": short_leverage,

        "leverage_source": "RENDER_MANUAL",
        "leverage_exchange_read_enabled": False,
        "leverage_exchange_write_enabled": False,

        "backup_margin_percent": backup_margin_percent,
        "backup_buffer_percent": backup_buffer_percent,
        "max_backups": 5,

        "backup_sizing_mode":
            "PERCENT_OF_AVAILABLE_TRADING_BALANCE",

        "backup_trigger_reference":
            "LATEST_VERIFIED_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PREVIOUS_BACKUP_FILL",

        "backup_long_liquidation_factor":
            1.0 - backup_buffer_percent / 100.0,

        "backup_short_liquidation_factor":
            1.0 + backup_buffer_percent / 100.0,

        "backup_activation":
            "AFTER_FAILED_FIRST_HEDGE_RECOVERY",

        "exposure_cap_percent": exposure_cap,
        "exposure_cap_max_percent": 100.0,
        "exposure_cap_basis": "TRADING_BALANCE",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

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
        "estimated_funding_rate": funding_buffer_rate,

        "tp1_net_roi_percent": tp1_roi,
        "tp2_net_roi_percent": tp2_roi,

        "tp1_allocation_percent": tp1_allocation,
        "tp2_allocation_percent": tp2_allocation,
        "tp3_allocation_percent": tp3_allocation,

        "tp_allocation": (
            tp1_allocation,
            tp2_allocation,
            tp3_allocation,
        ),

        "tp3_mode": "DYNAMIC_TRAILING",

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
            "margin_percent": backup_margin_percent,
            "liquidation_buffer_percent":
                backup_buffer_percent,

            "require_available_funds": True,
            "require_exposure_cap": True,
            "require_verified_liquidation_price": True,
        },

        "profit_protection": {
            "before_tp1": "ONE_ATR_HEDGE_RECOVERY_CYCLE",
            "after_tp1": "DYNAMIC_BREAK_EVEN",
            "after_tp2": "DYNAMIC_PROFIT_TRAILING",

            "protect_realized_profit": True,
            "fee_aware": True,
            "funding_aware": True,
            "slippage_aware": True,
        },
    }

    # ========================================================
    # CONTRACT PRECISION
    # ========================================================
    # Unknown until the selected WEEX contract is verified.
    # Never reuse BTC quantity steps for another coin.
    # ========================================================

    market_precision = {
        "quantity_step": None,
        "minimum_quantity": None,
        "price_step": None,

        "contract_value": None,
        "contract_multiplier": None,

        "verified": False,
        "source": "PENDING_DEMO_CONTRACT_VERIFICATION",

        "symbol": market_symbol,
        "demo_order_symbol": demo_order_symbol,
    }

    # ========================================================
    # SIGNAL QUALIFICATION
    # UNIT 4 MAY UPDATE THESE TUNABLE VALUES
    # ========================================================

    qualification = {
        "common": {
            "mode_priority": (
                "BREAKOUT",
                "STRUCTURE",
                "SCALP",
            ),

            "direction_votes_required": 2,
            "confirmations_required": 3,

            "exclusive_mode": True,
            "protect_developing_higher_modes": True,
            "market_symbol": market_symbol,
        },

        "breakout": {
            "enabled": True,
            "developing_candidate_enabled": True,

            "support_resistance_lookback": 20,
            "developing_proximity_atr": 0.5,
            "confirmation_distance_atr": 0.1,

            "max_price_extension_atr": 3.0,
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
            "max_price_extension_atr": 2.0,

            "fast_momentum_minutes": 5,
            "slow_momentum_minutes": 15,

            "require_fast_momentum": True,
            "require_slow_momentum": True,
        },

        "scalp": {
            "enabled": True,
            "require_sideways_market": True,

            "quality_threshold": 70.0,

            "ema_compression_atr_max": 0.7,
            "range20_atr_max": 8.0,
            "momentum15_atr_multiplier_max": 1.5,

            "preliminary_ema_separation_percent": 0.03,
            "preliminary_move_5m_percent": 0.015,

            "minimum_fee_coverage_multiplier": 2.0,

            "blocked_by_developing_breakout": True,
            "blocked_by_developing_structure": True,
        },
    }

    # ========================================================
    # COMPLETE CENTRAL CONFIGURATION
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

    unit_2_adapted_require(
        exchange["market_symbol"].endswith("USDT"),
        "QUOTE CURRENCY MUST BE USDT"
    )

    unit_2_adapted_require(
        strategy["initial_fixed_usdt"] > 0,
        "INVALID INITIAL MARGIN"
    )

    unit_2_adapted_require(
        0 <= exposure_cap <= 100,
        "INVALID EXPOSURE CAP"
    )

    unit_2_adapted_require(
        tp2_roi > tp1_roi,
        "INVALID TP TARGET ORDER"
    )

    unit_2_adapted_require(
        abs(
            tp1_allocation
            + tp2_allocation
            + tp3_allocation
            - 100.0
        ) < 0.000001,
        "INVALID TP ALLOCATION TOTAL"
    )

    # ========================================================
    # RENDER LOG REPORT
    # ========================================================

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True
    )

    print(
        "UNIVERSAL MARKET ENABLED = True",
        flush=True
    )

    print(
        "MARKET SYMBOL =", market_symbol,
        flush=True
    )

    print(
        "BASE COIN =", base_coin,
        flush=True
    )

    print(
        "QUOTE COIN =", quote_coin,
        flush=True
    )

    print(
        "DEMO ORDER SYMBOL =", demo_order_symbol,
        flush=True
    )

    print(
        "DEMO SYMBOL VERIFIED =",
        exchange["demo_symbol_verified"],
        flush=True
    )

    print(
        "CONTRACT PRECISION VERIFIED =",
        market_precision["verified"],
        flush=True
    )

    print(
        "INITIAL MARGIN USDT =", entry_margin,
        flush=True
    )

    print(
        "INITIAL MARGIN SOURCE =",
        entry_margin_source,
        flush=True
    )

    print(
        "LONG LEVERAGE =", long_leverage,
        flush=True
    )

    print(
        "SHORT LEVERAGE =", short_leverage,
        flush=True
    )

    print(
        "EXPOSURE CAP PERCENT =", exposure_cap,
        flush=True
    )

    print(
        "TP1 NET ROI TARGET =", tp1_roi,
        flush=True
    )

    print(
        "TP2 NET ROI TARGET =", tp2_roi,
        flush=True
    )

    print(
        "HEDGE MAXIMUM RECOVERY CYCLES =",
        strategy["hedge"]["maximum_recovery_cycles"],
        flush=True
    )

    print(
        "BACKUP ACTIVATION =",
        strategy["backup_recovery"]["activation"],
        flush=True
    )

    print(
        "BACKUP COUNT =",
        strategy["backup_recovery"]["backup_count"],
        flush=True
    )

    print(
        "CAPITAL DENOMINATION = USDT",
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
# 2.4 EXECUTION AND GLOBAL HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)

FRESH_UNIT_2_OPTIMIZATION_READY = True

print(
    "UNIT 2 ADAPTED OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)


# ============================================================
# END COMPLETE UNIT 2 UNIVERSAL MODEL
# UNIT 3 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 3 UNIVERSAL V3
# WEEX V3 LIVE MARK PRICE
# UNIVERSAL USDT-MARGined FUTURES MARKET
# COMPATIBLE WITH UNIT 1-2 AND UNIT 4-15 HANDOVER
# NO HARDCODED BTC OR NEAR SYMBOL
# NO ORDER SUBMISSION / ZERO INDENTATION
# ============================================================

import json
import math
import time
import urllib.request
import urllib.parse
import urllib.error


# ============================================================
# 3.1 UNIVERSAL MARKET RESPONSE VALIDATOR
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

    if not isinstance(expected_symbol, str):
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
# 3.2 UNIVERSAL VALIDATION TESTS
# TEST SYMBOL IS OBTAINED FROM UNIT 2
# ============================================================

def unit_3_validation_tests_v2():

    print("=" * 80, flush=True)
    print(
        "UNIT 3 UNIVERSAL VALIDATION V3 START",
        flush=True
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 UNIT 2 CONFIG MISSING"
        )

    exchange = config.get("exchange", {})

    symbol = exchange.get("market_symbol")

    if (
        not isinstance(symbol, str)
        or not symbol.endswith("USDT")
        or len(symbol) <= 4
    ):
        raise RuntimeError(
            "UNIT 3 INVALID UNIVERSAL SYMBOL"
        )

    now_ms = 1800000000000

    valid_payload = {
        "symbol": symbol,
        "price": "3.835",
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

    def rejected(payload, expected_error):

        try:
            unit_3_validate_mark_payload(
                payload,
                symbol,
                now_ms
            )
        except RuntimeError as exc:
            return str(exc) == expected_error

        return False

    result = unit_3_validate_mark_payload(
        valid_payload,
        symbol,
        now_ms
    )

    check(
        "VALID MARK PRICE",
        result["price"] == 3.835
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
        "TESTINVALIDUSDT"
        if symbol != "TESTINVALIDUSDT"
        else "OTHERINVALIDUSDT"
    )

    check(
        "REJECT WRONG SYMBOL",
        rejected(
            {
                **valid_payload,
                "symbol": wrong_symbol,
            },
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )
    )

    check(
        "REJECT ZERO PRICE",
        rejected(
            {
                **valid_payload,
                "price": "0",
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NEGATIVE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "-1",
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NONNUMERIC PRICE",
        rejected(
            {
                **valid_payload,
                "price": "invalid",
            },
            "UNIT 3 INVALID MARKET PRICE"
        )
    )

    check(
        "REJECT NONFINITE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "nan",
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT STALE DATA",
        rejected(
            {
                **valid_payload,
                "time": now_ms - 130000,
            },
            "UNIT 3 STALE MARKET DATA"
        )
    )

    check(
        "REJECT FUTURE TIMESTAMP",
        rejected(
            {
                **valid_payload,
                "time": now_ms + 20000,
            },
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE"
        )
    )

    check(
        "REJECT MISSING TIMESTAMP",
        rejected(
            {
                "symbol": symbol,
                "price": "3.835",
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
        "UNIT 3 TESTS PASSED =", passed,
        flush=True
    )

    print(
        "UNIT 3 TESTS FAILED =", failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 3 UNIVERSAL VALIDATION FAILED"
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
# 3.3 EXECUTABLE WEEX V3 LIVE MARKET REQUEST
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 3 UNIVERSAL START"
    )

    if globals().get(
        "FRESH_UNIT_2_OPTIMIZATION_READY"
    ) is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 NOT READY"
        )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 CONFIG MISSING"
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
            "UNIT 3 UNIVERSAL SYMBOL CONFIG INVALID"
        )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True
    )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True
    )

    print(
        "UNIT 3 REQUESTED SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 3 BASE COIN =",
        base_coin,
        flush=True
    )

    print(
        "UNIT 3 PRICE QUOTE CURRENCY = USDT",
        flush=True
    )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID WEEX API BASE URL"
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
            "User-Agent": "WEEX-Universal-Unit3-V3",
        },
        method="GET"
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 3 HTTP METHOD SAFETY FAILED"
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
            error_body = exc.read().decode("utf-8")
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

    received_time_ms = int(time.time() * 1000)

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
    exchange_time_ms = validated["exchange_time_ms"]
    market_age_ms = validated["market_age_ms"]

    # ========================================================
    # 3.4 PRESERVE ORIGINAL UNIT 4-15 HANDOVER
    # EXACT EIGHT CORE FIELDS
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
        field not in market_snapshot
        for field in required_fields
    ):
        raise RuntimeError(
            "UNIT 3 MARKET SNAPSHOT INCOMPLETE"
        )

    # ========================================================
    # 3.5 RENDER LOG REPORT
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
        "UNIT 3 PRICE UNIT = USDT PER",
        base_coin,
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
# 3.6 VALIDATION AND EXECUTION
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v2()
)

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3 UNIVERSAL V3
# UNIT 4 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 4 UNIVERSAL V6
# WEEX V3 / ANY CONFIGURED USDT FUTURES PAIR
# LIVE MARK CANDLES / EMA / ATR / STRATEGY EVIDENCE
# UNIT 1-3 INPUT / UNIT 5-15 HANDOVER
# NO EXCHANGE WRITES / ZERO INDENTATION
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error


# ============================================================
# 4.1 ADJUSTABLE STRATEGY PARAMETERS
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
# 4.2 VALIDATION HELPERS
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

    if number < 0 or (not allow_zero and number == 0):
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
# 4.3 CANDLE NORMALIZATION
# ============================================================

def unit_4_v5_normalize_candles(rows, market_time_ms):

    if not isinstance(rows, list):
        raise RuntimeError("UNIT 4 INVALID KLINE RESPONSE")

    candles = []

    for row in rows:

        if not isinstance(row, (list, tuple)) or len(row) < 7:
            raise RuntimeError("UNIT 4 INVALID KLINE ROW")

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
            raise RuntimeError("UNIT 4 INVALID OHLC")

        if candle["volume"] < 0:
            raise RuntimeError("UNIT 4 NEGATIVE VOLUME")

        if candle["close_time_ms"] <= candle["open_time_ms"]:
            raise RuntimeError("UNIT 4 INVALID CANDLE TIME")

        candles.append(candle)

    candles.sort(key=lambda x: x["open_time_ms"])

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
# 4.4 COMPLETE EXECUTABLE UNIT 4
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)
    print(
        "UNIT 4 UNIVERSAL USDT V6 START",
        flush=True
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    market = globals().get(
        "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
    )

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 UNIT 2 CONFIG MISSING")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 UNIT 3 SNAPSHOT MISSING")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    qualification = config.get("qualification", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, qualification)
    ):
        raise RuntimeError("UNIT 4 CONFIG INVALID")

    symbol = exchange.get("market_symbol")
    base_coin = exchange.get("base_coin")
    quote_coin = exchange.get("quote_coin")

    if (
        not isinstance(symbol, str)
        or not symbol.endswith("USDT")
        or len(symbol) <= 4
        or base_coin != symbol[:-4]
        or quote_coin != "USDT"
    ):
        raise RuntimeError(
            "UNIT 4 UNIVERSAL SYMBOL INVALID"
        )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or config.get("execution_environment") != "DEMO"
        or safety.get(
            "public_market_data_read_enabled"
        ) is not True
    ):
        raise RuntimeError("UNIT 4 CONFIG SAFETY FAILURE")

    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != symbol
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 3 HANDOVER MISMATCH"
        )

    if tuple(
        qualification.get("common", {}).get(
            "mode_priority", ()
        )
    ) != ("BREAKOUT", "STRUCTURE", "SCALP"):
        raise RuntimeError(
            "UNIT 4 MODE PRIORITY MISMATCH"
        )

    tuning = UNIT_4_V5_TUNING
    c = tuning["common"]
    b = tuning["breakout"]
    s = tuning["structure"]
    p = tuning["scalp"]

    market_time_ms = int(
        unit_4_v5_positive(
            market["exchange_time_ms"],
            "MARKET TIME",
            False
        )
    )

    live_mark = unit_4_v5_positive(
        market["price"], "MARK PRICE", False
    )

    age_ms = int(time.time() * 1000) - market_time_ms

    max_age_ms = int(
        c["market_age_seconds_max"] * 1000
    )

    if not -15000 <= age_ms <= max_age_ms:
        raise RuntimeError(
            "UNIT 4 STALE UNIT 3 MARKET DATA"
        )

    # ========================================================
    # WEEX V3 PUBLIC MARK PRICE CANDLES
    # ========================================================

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError("UNIT 4 API BASE INVALID")

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
            "User-Agent": "WEEX-Universal-Unit4-V6",
        }
    )

    if request.get_method() != "GET" or request.data is not None:
        raise RuntimeError("UNIT 4 REQUEST SAFETY FAILURE")

    start = time.monotonic()

    try:
        with urllib.request.urlopen(
            request, timeout=15
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
        (time.monotonic() - start) * 1000, 2
    )

    if status != 200:
        raise RuntimeError("UNIT 4 HTTP STATUS INVALID")

    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 INVALID WEEX JSON"
        ) from exc

    candles, closed = unit_4_v5_normalize_candles(
        rows, market_time_ms
    )

    latest = closed[-1]
    previous = closed[-2]

    candle_age = (
        market_time_ms - latest["close_time_ms"]
    ) / 1000.0

    if not (
        0 <= candle_age <= c["candle_age_seconds_max"]
    ):
        raise RuntimeError(
            "UNIT 4 LATEST CLOSED CANDLE STALE"
        )

    prices = [x["close"] for x in closed]

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
            (latest_close - reference)
            / reference * 100.0
        )

    # ========================================================
    # ATR14 IN USDT PER BASE COIN
    # ========================================================

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
        raise RuntimeError("UNIT 4 ATR14 INVALID")

    atr_percent = atr14 / latest_close * 100.0

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

    required_votes = unit_4_v5_integer(
        c["direction_votes_required"],
        "DIRECTION VOTES", 1, 3
    )

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
        return (
            long_votes if side == "LONG"
            else short_votes
        ) >= minimum

    def momentum_ok(side, period, required):
        return (
            not required
            or unit_4_v5_same_direction(
                moves[int(period)], side
            )
        )

    # ========================================================
    # BREAKOUT EVIDENCE
    # ========================================================

    lookback = unit_4_v5_integer(
        b["lookback_candles"],
        "BREAKOUT LOOKBACK", 2, 45
    )

    reference = closed[-lookback - 1:-1]

    support = min(x["low"] for x in reference)
    resistance = max(x["high"] for x in reference)

    proximity = unit_4_v5_positive(
        b["proximity_atr"], "BREAKOUT PROXIMITY"
    )

    confirmation = unit_4_v5_positive(
        b["confirmation_atr"], "BREAKOUT CONFIRMATION"
    )

    max_breakout_extension = unit_4_v5_positive(
        b["maximum_extension_atr"],
        "BREAKOUT MAX EXTENSION", False
    )

    def breakout_eligible(side):

        return bool(
            b["enabled"]
            and direction == side
            and votes_ok(
                side, b["direction_votes_required"]
            )
            and atr_percent >= b["minimum_atr_percent"]
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
        and -proximity <= long_distance <= confirmation
    )

    breakout_developing_short = bool(
        b["developing_candidate_enabled"]
        and breakout_eligible("SHORT")
        and -proximity <= short_distance <= confirmation
    )

    # ========================================================
    # STRUCTURE EVIDENCE
    # ========================================================

    alignment = str(
        s["ema_alignment_mode"]
    ).upper()

    if alignment not in ("EARLY", "STRICT"):
        raise RuntimeError(
            "UNIT 4 STRUCTURE ALIGNMENT INVALID"
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

    structure_max_extension = unit_4_v5_positive(
        s["maximum_extension_atr"],
        "STRUCTURE MAX EXTENSION", False
    )

    structure_pullback = unit_4_v5_positive(
        s["pullback_tolerance_atr"],
        "STRUCTURE PULLBACK"
    )

    def structure_eligible(side):

        signed_distance = (
            latest_close - ema19
            if side == "LONG"
            else ema19 - latest_close
        ) / atr14

        pullback = (
            abs(signed_distance) <= structure_pullback
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
                side, s["direction_votes_required"]
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

    # ========================================================
    # SCALP EVIDENCE
    # ========================================================

    scalp_lookback = unit_4_v5_integer(
        p["range_lookback_candles"],
        "SCALP LOOKBACK", 2, 45
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
        abs(latest_close - ema19) / atr14
    )

    price_overextended = bool(
        price_extension_atr > structure_max_extension
    )

    # ========================================================
    # PUBLISH TUNING TO SHARED UNIT 2 CONFIG
    # ========================================================

    common_cfg = qualification["common"]
    breakout_cfg = qualification["breakout"]
    structure_cfg = qualification["structure"]
    scalp_cfg = qualification["scalp"]

    common_cfg["direction_votes_required"] = required_votes

    breakout_cfg.update({
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

    structure_cfg.update({
        "enabled": bool(s["enabled"]),
        "ema_alignment_mode": alignment,
        "direction_votes_required":
            s["direction_votes_required"],
        "minimum_ema_separation_percent":
            s["minimum_ema_separation_percent"],
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
    # UNIT 4 -> UNIT 5 EVIDENCE SNAPSHOT
    # PRESERVE ORIGINAL FIELD NAMES
    # ========================================================

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
            "UNIT4_V6_UNIVERSAL_USDT",

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
            "scalp_range_atr": p["range_atr_max"],
            "scalp_momentum_atr":
                p["momentum_atr_max"],
        },

        "read_only": True,
        "trade_authorized": False,
        "order_payload_created": False,
    }

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
    # RENDER LOG VERIFICATION
    # ========================================================

    print(
        "UNIT 4 MARKET SYMBOL =", symbol,
        flush=True
    )

    print(
        "UNIT 4 BASE COIN =", base_coin,
        flush=True
    )

    print(
        "UNIT 4 QUOTE CURRENCY = USDT",
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
        "UNIT 4 ATR14 =", atr14,
        flush=True
    )

    print(
        "UNIT 4 ATR14 UNIT = USDT PER",
        base_coin,
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
        "UNIT 4 DIRECTION VOTES =",
        long_votes, "/", short_votes,
        flush=True
    )

    for name, value in (
        ("BREAKOUT CONFIRMED LONG", breakout_confirmed_long),
        ("BREAKOUT CONFIRMED SHORT", breakout_confirmed_short),
        ("BREAKOUT DEVELOPING LONG", breakout_developing_long),
        ("BREAKOUT DEVELOPING SHORT", breakout_developing_short),
        ("STRUCTURE DEVELOPING LONG", structure_developing_long),
        ("STRUCTURE DEVELOPING SHORT", structure_developing_short),
        ("SCALP SIDEWAYS", sideways_candidate),
    ):
        print(
            "UNIT 4", name, "=", value,
            flush=True
        )

    print(
        "UNIT 4 STRUCTURE TREND SIDE =",
        structure_side,
        flush=True
    )

    print(
        "UNIT 4 EVIDENCE VERSION =",
        snapshot["strategy_evidence_version"],
        flush=True
    )

    print(
        "PASS: UNIT 4 UNIVERSAL MARKET CONFIG",
        flush=True
    )

    print(
        "PASS: UNIT 4 COMPLETE CORE AND ADAPTER",
        flush=True
    )

    print(
        "PASS: UNIT 4 TO UNIT 5 HANDOVER",
        flush=True
    )

    print(
        "UNIT 4 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS",
        flush=True
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
# END COMPLETE UNIT 4 UNIVERSAL V6
# UNIT 5 FOLLOWS
# ============================================================



# START COMPLETE UNIT 5 V9 UNIVERSAL USDT REPLACEMENT
# FULLY ADJUSTABLE HYBRID CLASSIFICATION
# WEEX DEMO / ZERO INDENTATION
# UNIT 4 V5/V6 -> UNIT 5 V9 -> UNIT 6
# ============================================================

import math


# ============================================================
# 5.1 HELPERS
# ============================================================

def unit_5_v8_number(value, name):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 5 INVALID " + name)

    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 5 INVALID " + name
        ) from exc

    if not math.isfinite(value):
        raise RuntimeError(
            "UNIT 5 NONFINITE " + name
        )

    return value


def unit_5_v8_direction(value):

    if value > 0:
        return "LONG"
    if value < 0:
        return "SHORT"
    return "NONE"


def unit_5_v8_side_matches(value, side):

    return (
        value > 0 if side == "LONG"
        else value < 0 if side == "SHORT"
        else False
    )


def unit_5_v8_settings(config, group):

    section = config.get("qualification", {})

    if not isinstance(section, dict):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION CONFIG INVALID"
        )

    result = section.get(group)

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 5 MISSING CONFIG: " + group
        )

    return result


# ============================================================
# 5.2 COMPLETE CLASSIFICATION
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot
):

    print("=" * 80, flush=True)
    print(
        "UNIT 5 COMPLETE UNIVERSAL USDT V9 START",
        flush=True
    )

    if not isinstance(unit_2_config, dict):
        raise RuntimeError("UNIT 5 CONFIG INVALID")

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError("UNIT 5 SNAPSHOT INVALID")

    config = unit_2_config
    analysis = unit_4_snapshot

    common = unit_5_v8_settings(config, "common")
    b = unit_5_v8_settings(config, "breakout")
    s = unit_5_v8_settings(config, "structure")
    p = unit_5_v8_settings(config, "scalp")

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 5 STRATEGY PRIORITY INVALID"
        )

    if analysis.get(
        "strategy_evidence_version"
    ) != "U4_HYBRID_V2":
        raise RuntimeError(
            "UNIT 5 UNIT 4 EVIDENCE MISSING"
        )

    if analysis.get(
        "qualification_tuning_revision"
    ) not in (
        "UNIT4_V5_FULLY_INTEGRATED",
        "UNIT4_V6_UNIVERSAL_USDT",
    ):
        raise RuntimeError(
            "UNIT 5 COMPATIBLE UNIT 4 V5/V6 REQUIRED"
        )

    exchange = config.get("exchange", {})
    if not isinstance(exchange, dict):
        raise RuntimeError("UNIT 5 EXCHANGE CONFIG INVALID")
    market_symbol = exchange.get("market_symbol")
    if (
        not isinstance(market_symbol, str)
        or not market_symbol.endswith("USDT")
        or len(market_symbol) <= 4
        or not market_symbol[:-4].isalnum()
        or exchange.get("base_coin") != market_symbol[:-4]
        or exchange.get("quote_coin") != "USDT"
    ):
        raise RuntimeError("UNIT 5 UNIVERSAL USDT SYMBOL INVALID")

    if (
        analysis.get("exchange") != "WEEX"
        or analysis.get("api_version") != "V3"
        or analysis.get("symbol") != market_symbol
        or analysis.get("price_type") != "MARK"
        or analysis.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 5 MARKET CONTRACT INVALID"
        )

    def n(key):
        return unit_5_v8_number(
            analysis.get(key), key
        )

    def flag(key):

        result = analysis.get(key)

        if type(result) is not bool:
            raise RuntimeError(
                "UNIT 5 FLAG INVALID: " + key
            )

        return result

    def setting_number(section, key, fallback=None):

        value = section.get(key, fallback)

        if value is None:
            raise RuntimeError(
                "UNIT 5 SETTING MISSING: " + key
            )

        return unit_5_v8_number(value, key)

    def setting_bool(section, key, fallback=None):

        value = section.get(key, fallback)

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 5 BOOLEAN SETTING INVALID: " + key
            )

        return value

    # ========================================================
    # 5.3 MARKET INPUTS
    # ========================================================

    exchange_ms = n("exchange_time_ms")
    close_ms = n("latest_close_time_ms")

    candle_age = (
        exchange_ms - close_ms
    ) / 1000.0

    market_policy = config.get(
        "market_data_policy", {}
    )

    if not isinstance(market_policy, dict):
        raise RuntimeError(
            "UNIT 5 MARKET POLICY INVALID"
        )

    max_age = unit_5_v8_number(
        market_policy.get(
            "max_market_age_seconds", 120
        ),
        "MAX MARKET AGE"
    )

    if not 0 <= candle_age <= max_age:
        raise RuntimeError(
            "UNIT 5 CANDLE EVIDENCE STALE"
        )

    live_price = n("live_mark_price")
    previous_close = n("previous_close")
    latest_close = n("latest_close")

    ema19 = n("ema19")
    ema50 = n("ema50")
    ema200 = n("ema200")
    atr14 = n("atr14")

    separation = abs(
        n("ema19_50_separation_pct")
    )

    if min(
        live_price, previous_close, latest_close,
        ema19, ema50, ema200, atr14
    ) <= 0:
        raise RuntimeError(
            "UNIT 5 INVALID MARKET INDICATOR"
        )

    periods = (1, 5, 15, 30, 60, 120)

    moves = {
        period: n("move_%dm_pct" % period)
        for period in periods
    }

    directions = {
        period: unit_5_v8_direction(moves[period])
        for period in periods
    }

    short_move = n("short_term_move_pct")

    ema_structure = str(
        analysis.get("ema_structure", "MIXED")
    ).upper()

    if ema_structure not in (
        "BULLISH", "BEARISH", "MIXED"
    ):
        raise RuntimeError(
            "UNIT 5 EMA STRUCTURE INVALID"
        )

    # Diagnostic EMA direction from original classifier.
    # This does NOT override adjustable STRUCTURE mode.

    bullish = ema19 > ema50 > ema200
    bearish = ema19 < ema50 < ema200

    ema_direction = (
        "LONG" if bullish
        else "SHORT" if bearish
        else "NONE"
    )

    if (
        (bullish and ema_structure != "BULLISH")
        or (bearish and ema_structure != "BEARISH")
    ):
        raise RuntimeError(
            "UNIT 5 EMA STRUCTURE INCONSISTENT"
        )

    direction_evidence = str(
        analysis.get("direction_evidence", "NONE")
    ).upper()

    if direction_evidence not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 5 DIRECTION EVIDENCE INVALID"
        )

    long_votes = n("direction_long_votes")
    short_votes = n("direction_short_votes")

    if (
        long_votes < 0 or short_votes < 0
        or long_votes + short_votes > 3
    ):
        raise RuntimeError(
            "UNIT 5 DIRECTION VOTES INVALID"
        )

    def votes_pass(side, section):

        required = setting_number(
            section,
            "direction_votes_required",
            common.get("direction_votes_required", 2)
        )

        if (
            required != int(required)
            or not 1 <= required <= 3
        ):
            raise RuntimeError(
                "UNIT 5 VOTE THRESHOLD INVALID"
            )

        actual = (
            long_votes if side == "LONG"
            else short_votes
        )

        return actual >= required

    def momentum_pass(side, section):

        fast = int(setting_number(
            section, "fast_momentum_minutes", 5
        ))

        slow = int(setting_number(
            section, "slow_momentum_minutes", 15
        ))

        if fast not in moves or slow not in moves:
            raise RuntimeError(
                "UNIT 5 MOMENTUM WINDOW UNSUPPORTED"
            )

        require_fast = setting_bool(
            section, "require_fast_momentum", True
        )

        require_slow = setting_bool(
            section, "require_slow_momentum", True
        )

        return (
            (
                not require_fast
                or unit_5_v8_side_matches(
                    moves[fast], side
                )
            )
            and (
                not require_slow
                or unit_5_v8_side_matches(
                    moves[slow], side
                )
            )
        )

    # ========================================================
    # 5.4 STRATEGY EVIDENCE FROM UNIT 4
    # ========================================================

    b_long = flag("breakout_confirmed_long")
    b_short = flag("breakout_confirmed_short")

    bd_long = flag("breakout_developing_long")
    bd_short = flag("breakout_developing_short")

    sd_long = flag("structure_developing_long")
    sd_short = flag("structure_developing_short")

    sideways_evidence = flag("sideways_candidate")
    overextended = flag("price_overextended")

    if b_long and b_short:
        raise RuntimeError(
            "UNIT 5 CONFLICTING BREAKOUT EVIDENCE"
        )

    if bd_long and bd_short:
        raise RuntimeError(
            "UNIT 5 CONFLICTING DEVELOPING BREAKOUT"
        )

    if sd_long and sd_short:
        raise RuntimeError(
            "UNIT 5 CONFLICTING STRUCTURE EVIDENCE"
        )

    structure_trend = str(
        analysis.get(
            "structure_trend_direction", "NONE"
        )
    ).upper()

    structure_ema_mode = str(
        analysis.get(
            "structure_ema_alignment_mode", ""
        )
    ).upper()

    configured_ema_mode = str(
        s.get("ema_alignment_mode", "")
    ).upper()

    if configured_ema_mode not in (
        "EARLY", "STRICT"
    ):
        raise RuntimeError(
            "UNIT 5 STRUCTURE EMA MODE INVALID"
        )

    if structure_ema_mode != configured_ema_mode:
        raise RuntimeError(
            "UNIT 5 STRUCTURE TUNING NOT SYNCHRONIZED"
        )

    if structure_trend not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 5 STRUCTURE DIRECTION INVALID"
        )

    # ========================================================
    # 5.5 ORIGINAL 42-FIELD CLASSIFIER
    # ========================================================

    scalp_direction = "NONE"

    if ema19 > ema50 and moves[5] > 0:
        scalp_direction = "LONG"

    elif ema19 < ema50 and moves[5] < 0:
        scalp_direction = "SHORT"

    scalp_move = abs(moves[5])

    scalp_1m_support = (
        scalp_direction in ("LONG", "SHORT")
        and directions[1] == scalp_direction
    )

    structure_direction = "NONE"

    if (
        ema_direction != "NONE"
        and directions[15] == ema_direction
    ):
        structure_direction = ema_direction

    structure_move = abs(moves[15])

    breakout_primary = directions[30]

    breakout_fast_support = (
        breakout_primary != "NONE"
        and breakout_primary in (
            directions[5], directions[15]
        )
    )

    breakout_direction = "NONE"

    if (
        breakout_primary == "LONG"
        and breakout_fast_support
        and ema19 > ema50
        and latest_close > ema19
        and latest_close > ema200
    ):
        breakout_direction = "LONG"

    elif (
        breakout_primary == "SHORT"
        and breakout_fast_support
        and ema19 < ema50
        and latest_close < ema19
        and latest_close < ema200
    ):
        breakout_direction = "SHORT"

    breakout_move = abs(moves[30])

    # ========================================================
    # 5.6 ADJUSTABLE BREAKOUT QUALIFICATION
    # ========================================================

    breakout_side = (
        "LONG" if b_long
        else "SHORT" if b_short
        else "NONE"
    )

    breakout_enabled = setting_bool(
        b, "enabled", True
    )

    breakout_momentum_ok = (
        breakout_side != "NONE"
        and momentum_pass(breakout_side, b)
    )

    breakout_votes_ok = (
        breakout_side != "NONE"
        and votes_pass(breakout_side, b)
    )

    # BREAKOUT ADMISSION
    # Preserve Unit 4 confirmed breakout evidence.
    # Do not apply STRUCTURE overextension
    # to BREAKOUT qualification.

    breakout_qualified = bool(
        breakout_enabled
        and breakout_side != "NONE"
        and breakout_side == direction_evidence
        and breakout_votes_ok
        and breakout_momentum_ok
    )

    print(
        "UNIT 5 BREAKOUT CONFIRMED =",
        breakout_side != "NONE",
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT DIRECTION PASS =",
        breakout_side == direction_evidence,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT VOTES PASS =",
        breakout_votes_ok,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT MOMENTUM PASS =",
        breakout_momentum_ok,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE OVEREXTENSION =",
        overextended,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT ADMISSION =",
        breakout_qualified,
        flush=True
    )

    # ========================================================
    # 5.7 ADJUSTABLE STRUCTURE QUALIFICATION
    # ========================================================

    structure_enabled = setting_bool(
        s, "enabled", True
    )

    structure_side = structure_trend

    structure_developing_same_side = (
        sd_long if structure_side == "LONG"
        else sd_short if structure_side == "SHORT"
        else False
    )

    structure_votes_ok = (
        structure_side != "NONE"
        and votes_pass(structure_side, s)
    )

    structure_momentum_ok = (
        structure_side != "NONE"
        and momentum_pass(structure_side, s)
    )

    extension_atr = (
        abs(latest_close - ema19) / atr14
    )

    max_structure_extension = setting_number(
        s, "max_price_extension_atr", 2.0
    )

    structure_extension_ok = (
        extension_atr <= max_structure_extension
    )

    # STRUCTURE EMA mode is determined by Unit 4.
    # EARLY does not require EMA200 alignment.
    # It still requires Unit 4 developing evidence,
    # sufficient votes, momentum and extension.

    structure_qualified = bool(
        structure_enabled
        and structure_side != "NONE"
        and direction_evidence == structure_side
        and structure_developing_same_side
        and structure_votes_ok
        and structure_momentum_ok
        and structure_extension_ok
        and not overextended
    )

    # ========================================================
    # 5.8 ADJUSTABLE SCALP PRELIMINARY CONDITIONS
    # ========================================================

    scalp_enabled = setting_bool(
        p, "enabled", True
    )

    scalp_ema_min = setting_number(
        p,
        "preliminary_ema_separation_percent",
        0.03
    )

    scalp_move_min = setting_number(
        p,
        "preliminary_move_5m_percent",
        0.015
    )

    if scalp_ema_min < 0 or scalp_move_min < 0:
        raise RuntimeError(
            "UNIT 5 SCALP THRESHOLDS INVALID"
        )

    original_scalp_signal = bool(
        scalp_direction in ("LONG", "SHORT")
        and separation >= scalp_ema_min
        and scalp_move >= scalp_move_min
    )

    price_first_scalp_signal = bool(
        directions[5] in ("LONG", "SHORT")
        and abs(moves[5]) >= scalp_move_min
        and directions[1] == directions[5]
    )

    scalp_direction_candidate = scalp_direction

    if (
        scalp_direction_candidate == "NONE"
        and price_first_scalp_signal
    ):
        scalp_direction_candidate = directions[5]

    scalp_preliminary = bool(
        scalp_enabled
        and (
            original_scalp_signal
            or price_first_scalp_signal
        )
        and scalp_direction_candidate in (
            "LONG", "SHORT"
        )
    )

    scalp_require_sideways = setting_bool(
        p, "require_sideways_market", True
    )

    scalp_sideways_ok = (
        sideways_evidence
        if scalp_require_sideways
        else True
    )

    scalp_quality_minimum = setting_number(
        p, "quality_threshold", 70.0
    )

    fee_multiplier = setting_number(
        p,
        "minimum_fee_coverage_multiplier",
        2.0
    )

    if not (
        0 <= scalp_quality_minimum <= 100
        and fee_multiplier >= 1
    ):
        raise RuntimeError(
            "UNIT 5 SCALP QUALITY SETTINGS INVALID"
        )

    # An optional relaxed sideways policy does not
    # permit SCALP to override a developing higher mode.
    # Unit 6 still determines final fee/quality admission.

    # ========================================================
    # 5.9 HIGHER-PRIORITY CANDIDATE PROTECTION
    # ========================================================

    breakout_developing = bool(
        bd_long or bd_short
    )

    structure_developing = bool(
        sd_long or sd_short
    )

    higher_mode_developing = bool(
        breakout_developing
        or structure_developing
    )

    developing_breakout_direction = (
        "LONG" if bd_long
        else "SHORT" if bd_short
        else "NONE"
    )

    developing_structure_direction = (
        "LONG" if sd_long
        else "SHORT" if sd_short
        else "NONE"
    )

    qualified = False
    active_mode = "NONE"
    direction = "NONE"

    candidate_mode = "NONE"
    candidate_stage = "NONE"

    reason = "NO_ACCEPTABLE_CANDIDATE"

    breakout_ready = False
    structure_ready = False
    scalp_ready = False

    if breakout_qualified:

        qualified = True
        active_mode = "BREAKOUT"
        direction = breakout_side

        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"

        breakout_ready = True

        reason = "HYBRID_BREAKOUT_CONFIRMED"

    elif structure_qualified:

        qualified = True
        active_mode = "STRUCTURE"
        direction = structure_side

        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"

        structure_ready = True

        reason = "HYBRID_STRUCTURE_QUALIFIED"

    elif breakout_developing:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"

        reason = "BREAKOUT_DEVELOPING_PROTECTED"

    elif structure_developing:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"

        reason = "STRUCTURE_DEVELOPING_PROTECTED"

    elif scalp_preliminary and scalp_sideways_ok:

        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"

        scalp_ready = True

        reason = "SCALP_PENDING_UNIT_6_QUALITY"

    elif scalp_preliminary:

        candidate_stage = "REJECTED"

        reason = "SCALP_NOT_SIDEWAYS_MARKET"

    # PART 1 ENDS HERE.
    # CONTINUE WITH PART 2 AT THE SAME INDENTATION.
    # DO NOT EXECUTE MAIN.PY UNTIL PART 2 IS ADDED.
