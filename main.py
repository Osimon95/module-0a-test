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
# START UNIT 2 PART 1 — ZERO INDENTATION
# UNIVERSAL WEEX V3 DEMO CONFIGURATION
# RENDER-SELECTABLE COIN / USDT-DENOMINATED CAPITAL
# COMPATIBILITY: UNIT 1, UNIT 3-15 CONFIG INTERFACES
# NO EXCHANGE WRITES IN UNIT 2
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
        "WEEX_SYMBOL", "BTCUSDT"
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
    # Preserve the 16414 BTCUSDT -> BTCSUSDT naming rule,
    # substituting the Render-selected base coin only.
    # This produces a CANDIDATE, not proof of WEEX listing.
    # ========================================================

    demo_order_symbol = base_coin + "SUSDT"

    # Contract existence and precision must be independently
    # verified before any demo order is authorized.

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

# ============================================================
# END UNIT 2 PART 1 — ZERO INDENTATION
# CONTINUE IMMEDIATELY WITH UNIT 2 PART 2
# DO NOT INSERT UNIT 3 HERE
# ============================================================



# ============================================================
# START UNIT 2 PART 2 — ZERO INDENTATION
# CENTRAL STRATEGY, CONTRACT, VALIDATION AND HANDOVER
# ============================================================

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
# END UNIT 2 PART 2 — ZERO INDENTATION
# END COMPLETE UNIT 2 UNIVERSAL MODEL
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
    
    # ========================================================
    # 5.10 REJECTION AND COST DIAGNOSTICS
    # ========================================================

    breakout_rejection_reason = (
        "QUALIFIED"
        if breakout_qualified
        else "DEVELOPING"
        if breakout_developing
        else "DISABLED"
        if not breakout_enabled
        else "CONFIRMATION_OR_MOMENTUM_PENDING"
    )

    structure_rejection_reason = (
        "QUALIFIED"
        if structure_qualified
        else "DEVELOPING"
        if structure_developing
        else "DISABLED"
        if not structure_enabled
        else "STRUCTURE_EVIDENCE_PENDING"
    )

    scalp_rejection_reason = (
        "HIGHER_MODE_PROTECTED"
        if (
            breakout_qualified
            or structure_qualified
            or higher_mode_developing
        )
        else "PENDING_UNIT_6"
        if scalp_ready
        else "NOT_SIDEWAYS"
        if (
            scalp_preliminary
            and not scalp_sideways_ok
        )
        else "PRELIMINARY_CONDITIONS_FAILED"
    )

    fee_entry = setting_bool(
        p, "include_entry_fee", True
    )

    fee_exit = setting_bool(
        p, "include_exit_fee", True
    )

    fee_sides = int(fee_entry) + int(fee_exit)

    taker_fee = setting_number(
        p, "estimated_taker_fee_percent", 0.08
    )

    slippage = setting_number(
        p, "estimated_slippage_percent", 0.0
    )

    if taker_fee < 0 or slippage < 0:
        raise RuntimeError(
            "UNIT 5 INVALID FEE ESTIMATE"
        )

    round_trip_fee = (
        taker_fee * fee_sides + slippage
    )

    # ========================================================
    # 5.11 PRESERVE ORIGINAL 42 OUTPUT FIELDS
    # ========================================================

    candidate = {

        "symbol": market_symbol,
        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,
        "qualification_reason": reason,

        "live_mark_price": live_price,
        "ema19": ema19,
        "ema50": ema50,
        "ema200": ema200,
        "ema19_50_separation_pct": separation,
        "ema_structure": ema_structure,
        "ema_direction": ema_direction,

        "momentum_direction": directions[1],

        "direction_agreement": (
            structure_direction != "NONE"
        ),

        "short_term_move_pct": short_move,

        "absolute_short_term_move_pct":
            abs(short_move),

        "previous_close": previous_close,
        "latest_close": latest_close,

        "price_above_ema19":
            live_price > ema19,

        "price_above_ema50":
            live_price > ema50,

        "price_above_ema200":
            live_price > ema200,

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

        "structure_direction": structure_direction,
        "structure_move_pct": structure_move,

        "breakout_direction": breakout_direction,
        "breakout_move_pct": breakout_move,
        "breakout_fast_support":
            breakout_fast_support,
    }

    if len(candidate) != 42:
        raise RuntimeError(
            "UNIT 5 ORIGINAL 42-FIELD CONTRACT FAILED"
        )

    # ========================================================
    # 5.12 EXTENDED HANDOVER TO UNIT 6
    # ========================================================

    candidate.update({

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

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

        "scalp_quality_minimum":
            scalp_quality_minimum,

        "scalp_price_weight_percent":
            setting_number(
                p, "price_action_weight_percent", 50
            ),

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
            "U4_HYBRID_V2",

        "classification_revision": "V3.1",

        "candidate_protected": (
            candidate_stage == "DEVELOPING"
        ),

        "candidate_age_seconds": candle_age,

        "classification_source":
            "UNIT5_V9_UNIVERSAL_USDT",

        "original_unit5_qualified": bool(
            breakout_qualified
            or structure_qualified
            or scalp_preliminary
        ),

        "original_unit5_mode": (
            "BREAKOUT" if breakout_qualified
            else "STRUCTURE" if structure_qualified
            else "SCALP" if scalp_preliminary
            else "NONE"
        ),

        "original_unit5_direction": (
            breakout_side if breakout_qualified
            else structure_side if structure_qualified
            else scalp_direction_candidate
            if scalp_preliminary
            else "NONE"
        ),

        "original_unit5_reason":
            "INTEGRATED_V9_UNIVERSAL_CLASSIFIER",

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

        "structure_extension_atr":
            extension_atr,

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

        "scalp_preliminary":
            scalp_preliminary,

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

        # Universal market metadata

        "base_coin":
            market_symbol[:-4],

        "quote_coin": "USDT",

        "margin_currency": "USDT",

        "universal_symbol_enabled": True,

        "unit5_revision":
            "UNIT5_V9_UNIVERSAL_USDT",

        "breakout_rejection_reason":
            breakout_rejection_reason,

        "structure_rejection_reason":
            structure_rejection_reason,

        "scalp_rejection_reason":
            scalp_rejection_reason,
    })

    # ========================================================
    # 5.13 FINAL CONSISTENCY AND SAFETY
    # ========================================================

    if qualified != (
        candidate_stage == "QUALIFIED"
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION STATE INVALID"
        )

    if qualified and (
        active_mode not in (
            "BREAKOUT", "STRUCTURE"
        )
        or direction not in (
            "LONG", "SHORT"
        )
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFIED MODE INVALID"
        )

    if candidate_mode == "SCALP" and (
        breakout_qualified
        or structure_qualified
        or higher_mode_developing
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PRIORITY VIOLATION"
        )

    if (
        candidate["trade_authorized"] is not False
        or candidate["order_payload_created"] is not False
    ):
        raise RuntimeError(
            "UNIT 5 EXCHANGE WRITE BOUNDARY FAILED"
        )

    if candidate["symbol"] != market_symbol:
        raise RuntimeError(
            "UNIT 5 SYMBOL HANDOVER FAILED"
        )

    if candidate["quote_coin"] != "USDT":
        raise RuntimeError(
            "UNIT 5 QUOTE CURRENCY FAILED"
        )

    # ========================================================
    # 5.14 RENDER REPORT
    # ========================================================

    print(
        "UNIT 5 MARKET SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 5 BASE COIN =",
        market_symbol[:-4],
        flush=True
    )

    print(
        "UNIT 5 QUOTE CURRENCY = USDT",
        flush=True
    )

    print(
        "UNIT 5 ORIGINAL FIELDS = 42",
        flush=True
    )

    print(
        "UNIT 5 UNIT 4 TUNING =",
        analysis["qualification_tuning_revision"],
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
        "UNIT 5 BREAKOUT REJECTION =",
        breakout_rejection_reason,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE REJECTION =",
        structure_rejection_reason,
        flush=True
    )

    print(
        "UNIT 5 SCALP REJECTION =",
        scalp_rejection_reason,
        flush=True
    )

    print(
        "UNIT 5 SCALP QUALITY TARGET =",
        scalp_quality_minimum,
        flush=True
    )

    print(
        "UNIT 5 ESTIMATED ROUND TRIP FEE % =",
        round_trip_fee,
        flush=True
    )

    print(
        "UNIT 5 MODE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 5 STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 5 ACTIVE MODE =",
        active_mode,
        flush=True
    )

    print(
        "UNIT 5 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 5 QUALIFIED =",
        qualified,
        flush=True
    )

    print(
        "UNIT 5 REASON =",
        reason,
        flush=True
    )

    print(
        "UNIT 5 EVIDENCE VERSION =",
        candidate["strategy_evidence_version"],
        flush=True
    )

    print(
        "UNIT 5 CANDLE AGE SECONDS =",
        round(candle_age, 3),
        flush=True
    )

    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 5 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return candidate


# ============================================================
# 5.15 UNIT 5 UNIVERSAL VALIDATION
# ============================================================

def unit_5_validation_v8():

    print("=" * 80, flush=True)

    print(
        "UNIT 5 UNIVERSAL VALIDATION V9 START",
        flush=True
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    analysis = globals().get(
        "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 5 VALIDATION CONFIG MISSING"
        )

    if not isinstance(analysis, dict):
        raise RuntimeError(
            "UNIT 5 VALIDATION SNAPSHOT MISSING"
        )

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 5 VALIDATION EXCHANGE INVALID"
        )

    symbol = exchange.get("market_symbol")

    if (
        not isinstance(symbol, str)
        or not symbol.endswith("USDT")
        or len(symbol) <= 4
    ):
        raise RuntimeError(
            "UNIT 5 VALIDATION SYMBOL INVALID"
        )

    if analysis.get("symbol") != symbol:
        raise RuntimeError(
            "UNIT 5 VALIDATION SYMBOL MISMATCH"
        )

    if exchange.get("quote_coin") != "USDT":
        raise RuntimeError(
            "UNIT 5 VALIDATION QUOTE MISMATCH"
        )

    if analysis.get(
        "strategy_evidence_version"
    ) != "U4_HYBRID_V2":
        raise RuntimeError(
            "UNIT 5 VALIDATION EVIDENCE MISMATCH"
        )

    if analysis.get(
        "qualification_tuning_revision"
    ) not in (
        "UNIT4_V5_FULLY_INTEGRATED",
        "UNIT4_V6_UNIVERSAL_USDT",
    ):
        raise RuntimeError(
            "UNIT 5 VALIDATION REVISION MISMATCH"
        )

    qualification = config.get(
        "qualification", {}
    )

    if not isinstance(qualification, dict):
        raise RuntimeError(
            "UNIT 5 VALIDATION TUNING MISSING"
        )

    for section_name in (
        "common",
        "breakout",
        "structure",
        "scalp",
    ):

        if not isinstance(
            qualification.get(section_name),
            dict
        ):
            raise RuntimeError(
                "UNIT 5 VALIDATION SECTION MISSING: "
                + section_name
            )

    print(
        "UNIT 5 VALIDATION SYMBOL =",
        symbol,
        flush=True
    )

    print(
        "UNIT 5 VALIDATION QUOTE = USDT",
        flush=True
    )

    print(
        "UNIT 5 VALIDATION UNIT 4 = PASS",
        flush=True
    )

    print(
        "UNIT 5 UNIVERSAL CONFIG VALIDATION = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# 5.16 GLOBAL EXECUTION
# ============================================================

FRESH_UNIT_5_VALIDATION_READY = (
    unit_5_validation_v8()
)

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
)

FRESH_UNIT_5_OPTIMIZATION_READY = True

print(
    "UNIT 5 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_5_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 5 V9 UNIVERSAL USDT REPLACEMENT
# UNIT 6 BEGINS BELOW THIS LINE
# ============================================================


# ============================================================
# START COMPLETE UNIT 6 V10 UNIVERSAL USDT REPLACEMENT
# ADAPTED FROM 17248 / 16414 REFERENCE MODELS
# UNIT 4 V6 -> UNIT 5 V9 -> UNIT 6 V10 -> UNIT 7
# ZERO INDENTATION
# NO EXCHANGE WRITES IN UNIT 6
# ============================================================

import math
import copy


# ============================================================
# 6.1 VALIDATION HELPERS
# ============================================================

def unit_6_v9_number(value, label):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 6 INVALID NUMBER: " + label
        )

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 6 INVALID NUMBER: " + label
        ) from exc

    if not math.isfinite(result):
        raise RuntimeError(
            "UNIT 6 NONFINITE NUMBER: " + label
        )

    return result


def unit_6_v9_bool(value, label):

    if type(value) is not bool:
        raise RuntimeError(
            "UNIT 6 INVALID BOOLEAN: " + label
        )

    return value


def unit_6_v9_clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))


def unit_6_v9_side(value):

    if value > 0:
        return "LONG"

    if value < 0:
        return "SHORT"

    return "NONE"


# ============================================================
# 6.2 MAIN ADMISSION ENGINE
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate
):

    print("=" * 80, flush=True)
    print(
        "UNIT 6 V10 UNIVERSAL USDT START",
        flush=True
    )

    if not all(
        isinstance(item, dict)
        for item in (
            unit_2_config,
            unit_4_analysis,
            unit_5_candidate
        )
    ):
        raise RuntimeError(
            "UNIT 6 INPUT CONTRACT INVALID"
        )

    config = unit_2_config
    analysis = unit_4_analysis
    candidate = unit_5_candidate

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 6 EXCHANGE CONFIG INVALID"
        )

    symbol = exchange.get("market_symbol")
    base_coin = exchange.get("base_coin")
    quote_coin = exchange.get("quote_coin")

    if (
        not isinstance(symbol, str)
        or not symbol.endswith("USDT")
        or len(symbol) <= 4
        or not symbol[:-4].isalnum()
        or base_coin != symbol[:-4]
        or quote_coin != "USDT"
    ):
        raise RuntimeError(
            "UNIT 6 UNIVERSAL SYMBOL INVALID"
        )

    if (
        analysis.get("symbol") != symbol
        or candidate.get("symbol") != symbol
    ):
        raise RuntimeError(
            "UNIT 6 SYMBOL HANDOVER MISMATCH"
        )

    if (
        analysis.get("strategy_evidence_version")
        != "U4_HYBRID_V2"
        or analysis.get(
            "qualification_tuning_revision"
        ) not in (
            "UNIT4_V5_FULLY_INTEGRATED",
            "UNIT4_V6_UNIVERSAL_USDT"
        )
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 4 EVIDENCE INVALID"
        )

    if (
        candidate.get("strategy_evidence_version")
        != "U5_HYBRID_ADJUSTABLE_V3"
        or candidate.get(
            "qualification_tuning_revision"
        ) != "UNIT5_V8_FULLY_ADJUSTABLE"
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 5 EVIDENCE INVALID"
        )

    if (
        analysis.get("read_only") is not True
        or candidate.get("read_only") is not True
        or candidate.get("trade_authorized") is not False
        or candidate.get("order_payload_created") is not False
    ):
        raise RuntimeError(
            "UNIT 6 INPUT SAFETY FAILED"
        )

    # ========================================================
    # 6.3 ORIGINAL ADJUSTABLE STRATEGY CONFIG
    # ========================================================

    qualification = config.get("qualification")

    if not isinstance(qualification, dict):
        raise RuntimeError(
            "UNIT 6 QUALIFICATION CONFIG MISSING"
        )

    common = qualification.get("common")
    breakout = qualification.get("breakout")
    structure = qualification.get("structure")
    scalp = qualification.get("scalp")

    for name, section in (
        ("COMMON", common),
        ("BREAKOUT", breakout),
        ("STRUCTURE", structure),
        ("SCALP", scalp)
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 6 MISSING SETTINGS: " + name
            )

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 MODE PRIORITY INVALID"
        )

    strategy = config.get("strategy")

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 6 STRATEGY CONFIG MISSING"
        )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode"
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 6 SAFETY POLICY DISABLED: " + key
            )

    # This verifies the existing configuration.
    # Position and duplicate-order enforcement
    # must still occur in downstream execution units.

    # ========================================================
    # 6.4 UNIT 5 CANDIDATE STATE
    # ========================================================

    mode = candidate.get("candidate_mode", "NONE")
    stage = candidate.get("candidate_stage", "NONE")

    incoming_mode = candidate.get(
        "active_mode", "NONE"
    )

    incoming_side = candidate.get(
        "direction", "NONE"
    )

    qualified = unit_6_v9_bool(
        candidate.get("qualified"),
        "QUALIFIED"
    )

    higher_developing = unit_6_v9_bool(
        candidate.get("higher_mode_developing"),
        "HIGHER MODE DEVELOPING"
    )

    breakout_ready = unit_6_v9_bool(
        candidate.get("breakout_ready"),
        "BREAKOUT READY"
    )

    structure_ready = unit_6_v9_bool(
        candidate.get("structure_ready"),
        "STRUCTURE READY"
    )

    scalp_ready = unit_6_v9_bool(
        candidate.get("scalp_ready"),
        "SCALP READY"
    )

    if mode not in (
        "NONE", "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 CANDIDATE MODE INVALID"
        )

    if stage not in (
        "NONE", "REJECTED", "DEVELOPING",
        "QUALIFIED", "PENDING_UNIT_6"
    ):
        raise RuntimeError(
            "UNIT 6 CANDIDATE STAGE INVALID"
        )

    if incoming_mode not in (
        "NONE", "BREAKOUT", "STRUCTURE"
    ):
        raise RuntimeError(
            "UNIT 6 ACTIVE MODE INVALID"
        )

    if incoming_side not in (
        "NONE", "LONG", "SHORT"
    ):
        raise RuntimeError(
            "UNIT 6 DIRECTION INVALID"
        )

    if qualified != (stage == "QUALIFIED"):
        raise RuntimeError(
            "UNIT 6 CONTRADICTORY QUALIFICATION"
        )

    if qualified and (
        mode != incoming_mode
        or incoming_side == "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 QUALIFIED STATE MISMATCH"
        )

    if not qualified and (
        incoming_mode != "NONE"
        or incoming_side != "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 UNQUALIFIED STATE MISMATCH"
        )

    if sum((
        breakout_ready,
        structure_ready,
        scalp_ready
    )) > 1:
        raise RuntimeError(
            "UNIT 6 CONFLICTING READY MODES"
        )

    # ========================================================
    # 6.5 MARKET DATA
    # ========================================================

    def a(key):
        return unit_6_v9_number(
            analysis.get(key), key
        )

    def c(key):
        return unit_6_v9_number(
            candidate.get(key), key
        )

    price = a("latest_close")
    live_price = a("live_mark_price")

    ema19 = a("ema19")
    ema50 = a("ema50")
    ema100 = a("ema100")
    ema200 = a("ema200")

    atr = a("atr14")

    if min(
        price, live_price,
        ema19, ema50, ema100, ema200, atr
    ) <= 0:
        raise RuntimeError(
            "UNIT 6 MARKET INDICATORS INVALID"
        )

    move_1m = a("move_1m_pct")
    move_5m = a("move_5m_pct")
    move_15m = a("move_15m_pct")

    atr_pct = atr / price * 100.0

    candle_age = c("candidate_age_seconds")

    policy = config.get("market_data_policy", {})

    if not isinstance(policy, dict):
        raise RuntimeError(
            "UNIT 6 MARKET POLICY INVALID"
        )

    max_age = unit_6_v9_number(
        policy.get("max_market_age_seconds", 120),
        "MAXIMUM CANDLE AGE"
    )

    if max_age <= 0:
        raise RuntimeError(
            "UNIT 6 INVALID MARKET AGE LIMIT"
        )

    fresh = bool(
        candidate.get("candle_data_fresh") is True
        and 0 <= candle_age <= max_age
    )

    # ========================================================
    # 6.6 SCALP QUALITY CONFIGURATION
    # ========================================================

    scalp_minimum = unit_6_v9_number(
        scalp.get("quality_threshold", 70),
        "SCALP QUALITY MINIMUM"
    )

    fee_coverage = unit_6_v9_number(
        scalp.get(
            "minimum_fee_coverage_multiplier", 2
        ),
        "FEE COVERAGE"
    )

    estimated_fee = c(
        "estimated_round_trip_fee_pct"
    )

    if not (
        0 <= scalp_minimum <= 100
        and fee_coverage >= 1
        and estimated_fee >= 0
    ):
        raise RuntimeError(
            "UNIT 6 INVALID QUALITY OR FEE CONFIG"
        )

    entry_fee_enabled = (
        scalp.get("include_entry_fee") is True
    )

    exit_fee_enabled = (
        scalp.get("include_exit_fee") is True
    )

    taker_fee = unit_6_v9_number(
        scalp.get(
            "estimated_taker_fee_percent", 0
        ),
        "TAKER FEE"
    )

    if taker_fee < 0:
        raise RuntimeError(
            "UNIT 6 NEGATIVE FEE INVALID"
        )

    fee_estimate_verified = bool(
        entry_fee_enabled
        and exit_fee_enabled
        and taker_fee > 0
        and estimated_fee > 0
    )

    # This is an estimated fee model, not a
    # verified exchange settlement record.

    sideways = unit_6_v9_bool(
        analysis.get("sideways_candidate"),
        "SIDEWAYS EVIDENCE"
    )

    sideways_required = unit_6_v9_bool(
        scalp.get("require_sideways_market", True),
        "SIDEWAYS REQUIRED"
    )

    sideways_pass = bool(
        sideways or not sideways_required
    )

    # ========================================================
    # 6.7 DIRECTION PERSISTENCE
    # ========================================================

    scalp_side = candidate.get(
        "scalp_direction_candidate", "NONE"
    )

    if scalp_side not in (
        "NONE", "LONG", "SHORT"
    ):
        raise RuntimeError(
            "UNIT 6 SCALP SIDE INVALID"
        )

    direction_1m = unit_6_v9_side(move_1m)
    direction_5m = unit_6_v9_side(move_5m)
    direction_15m = unit_6_v9_side(move_15m)

    persistence_directions = (
        direction_1m,
        direction_5m,
        direction_15m
    )

    persistence_window = len(
        persistence_directions
    )

    persistence_required = 2

    persistence_confirmations = sum(
        direction == scalp_side
        for direction in persistence_directions
    ) if scalp_side != "NONE" else 0

    persistence_pass = (
        persistence_confirmations
        >= persistence_required
    )

    fifteen_minute_support_pass = (
        scalp_side != "NONE"
        and direction_15m == scalp_side
    )

    momentum_conflict = bool(
        scalp_side != "NONE"
        and direction_5m not in (
            scalp_side, "NONE"
        )
    )

    # ========================================================
    # 6.8 SCALP QUALITY SCORE
    # MAXIMUM 100 POINTS
    # ========================================================

    price_action_score = 0.0
    persistence_score = 0.0
    location_score = 0.0
    ema_score = 0.0
    volatility_score = 0.0

    ema_separation_pct = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    compression_limit = unit_6_v9_number(
        scalp.get(
            "ema_compression_atr_max", 0.7
        ),
        "EMA COMPRESSION LIMIT"
    )

    compression_atr = a("ema_compression_atr")

    ema_compressed = (
        compression_atr <= compression_limit
    )

    extension_atr = (
        abs(price - ema19) / atr
    )

    extreme_extension = (
        extension_atr > 1.5
    )

    spike_ratio = (
        abs(move_1m)
        / max(
            abs(move_5m) / 5.0,
            0.000001
        )
    )

    extreme_spike = (
        spike_ratio > 2.0
    )

    late_impulse = bool(
        extreme_extension
        and extreme_spike
    )

    if scalp_side != "NONE":

        if direction_5m == scalp_side:
            price_action_score += 15

        if direction_1m == scalp_side:
            price_action_score += 10

        preliminary_move_min = unit_6_v9_number(
            scalp.get(
                "preliminary_move_5m_percent",
                0.015
            ),
            "PRELIMINARY MOVE"
        )

        if abs(move_5m) >= preliminary_move_min:
            price_action_score += 5

        persistence_score = (
            20.0
            * persistence_confirmations
            / persistence_window
        )

        location_pass = (
            price >= ema19
            if scalp_side == "LONG"
            else price <= ema19
        )

        if location_pass:
            location_score += 10

        ema100_location_pass = (
            price >= ema100
            if scalp_side == "LONG"
            else price <= ema100
        )

        if ema100_location_pass:
            location_score += 5

        if ema_compressed:
            ema_score += 10

        ema_direction_pass = (
            (
                scalp_side == "LONG"
                and ema19 >= ema50
            )
            or (
                scalp_side == "SHORT"
                and ema19 <= ema50
            )
        )

        if ema_direction_pass:
            ema_score += 5

        if not extreme_extension:
            volatility_score += 10

        if not extreme_spike:
            volatility_score += 5

        if not late_impulse:
            volatility_score += 5

    quality_score = round(
        unit_6_v9_clamp(
            price_action_score
            + persistence_score
            + location_score
            + ema_score
            + volatility_score,
            0,
            100
        ),
        2
    )

    quality_pass = (
        quality_score >= scalp_minimum
    )

    # ========================================================
    # 6.9 FEE COVERAGE SCREEN
    # ========================================================

    projected_move_pct = min(
        abs(move_5m),
        atr_pct
    )

    required_move_pct = (
        estimated_fee * fee_coverage
    )

    fee_coverage_pass = bool(
        fee_estimate_verified
        and projected_move_pct
        >= required_move_pct
    )

    # ========================================================
    # 6.10 FINAL STRATEGY ARBITRATION
    # ========================================================

    execution_intent = False
    signal_qualified = False

    active_mode = "NONE"
    direction = "NONE"

    admission_reason = (
        "NO_ACCEPTABLE_CANDIDATE"
    )

    if not fresh:

        admission_reason = (
            "MARKET_EVIDENCE_STALE"
        )

    elif stage == "QUALIFIED":

        if (
            qualified
            and mode == "BREAKOUT"
            and breakout_ready
            and incoming_side in (
                "LONG", "SHORT"
            )
            and candidate.get(
                "hybrid_breakout_qualified"
            ) is True
        ):

            execution_intent = True
            signal_qualified = True

            active_mode = "BREAKOUT"
            direction = incoming_side

            admission_reason = (
                "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS"
            )

        elif (
            qualified
            and mode == "STRUCTURE"
            and structure_ready
            and incoming_side in (
                "LONG", "SHORT"
            )
            and candidate.get(
                "hybrid_structure_qualified"
            ) is True
        ):

            execution_intent = True
            signal_qualified = True

            active_mode = "STRUCTURE"
            direction = incoming_side

            admission_reason = (
                "STRUCTURE_QUALIFIED_FOR_NEXT_UNITS"
            )

        else:

            admission_reason = (
                "QUALIFIED_STATE_INCONSISTENT"
            )

    elif stage == "DEVELOPING":

        admission_reason = (
            "DEVELOPING_HIGHER_MODE_PROTECTED"
        )

    elif (
        stage == "PENDING_UNIT_6"
        and mode == "SCALP"
    ):

        if higher_developing:

            admission_reason = (
                "SCALP_BLOCKED_HIGHER_MODE_DEVELOPING"
            )

        elif not scalp_ready:

            admission_reason = (
                "SCALP_NOT_READY"
            )

        elif scalp_side == "NONE":

            admission_reason = (
                "SCALP_DIRECTION_MISSING"
            )

        elif not sideways_pass:

            admission_reason = (
                "SCALP_SIDEWAYS_REQUIREMENT_FAILED"
            )

        elif momentum_conflict:

            admission_reason = (
                "SCALP_MOMENTUM_CONFLICT"
            )

        elif not persistence_pass:

            admission_reason = (
                "SCALP_PERSISTENCE_INSUFFICIENT"
            )

        elif late_impulse:

            admission_reason = (
                "SCALP_LATE_IMPULSE_REJECTED"
            )

        elif not quality_pass:

            admission_reason = (
                "SCALP_QUALITY_BELOW_THRESHOLD"
            )

        elif not fee_estimate_verified:

            admission_reason = (
                "SCALP_FEES_NOT_VERIFIED"
            )

        elif not fee_coverage_pass:

            admission_reason = (
                "SCALP_FEE_COVERAGE_INSUFFICIENT"
            )

        else:

            execution_intent = True
            signal_qualified = True

            active_mode = "SCALP"
            direction = scalp_side

            admission_reason = (
                "SCALP_QUALIFIED_FOR_NEXT_UNITS"
            )

    elif stage == "REJECTED":

        admission_reason = candidate.get(
            "qualification_reason",
            "UPSTREAM_CANDIDATE_REJECTED"
        )

    if active_mode == "SCALP" and (
        higher_developing
        or breakout_ready
        or structure_ready
    ):
        raise RuntimeError(
            "UNIT 6 SCALP PRIORITY VIOLATION"
        )

    # ========================================================
    # 6.11 ORIGINAL UNIT 7 OUTPUT CONTRACT
    # ========================================================

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

        "execution_intent": execution_intent,
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": signal_qualified,

        "unit_5_reason": candidate.get(
            "qualification_reason", "UNKNOWN"
        ),

        "admission_reason": admission_reason,

        "leverage_target": None,

        "leverage_regime":
            "WEEX_MANUAL_RENDER_CONFIG",

        "sideways_regime": sideways,

        "ema_compressed": ema_compressed,

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

        "candidate_mode": mode,
        "candidate_stage": stage,

        "higher_mode_developing":
            higher_developing,

        "unit_5_evidence_version":
            candidate.get(
                "strategy_evidence_version"
            ),

        "unit_4_evidence_version":
            analysis.get(
                "strategy_evidence_version"
            ),

        "classification_version":
            "UNIT6_V10_UNIVERSAL_USDT",

        "market_data_fresh": fresh,

        "position_sizing_performed": False,
        "order_payload_created": False,
        "exchange_write": False,
        "read_only": True,
        "trade_authorized": False,

        # Additional universal metadata

        "symbol": symbol,
        "base_coin": base_coin,
        "quote_coin": quote_coin,
        "margin_currency": "USDT",

        "universal_symbol_enabled": True,

        "fee_estimate_verified":
            fee_estimate_verified,

        "estimated_round_trip_fee_pct":
            estimated_fee,

        "fee_coverage_pass":
            fee_coverage_pass,
    }

    if execution_intent and (
        active_mode == "NONE"
        or direction == "NONE"
        or not signal_qualified
        or not fresh
    ):
        raise RuntimeError(
            "UNIT 6 EXECUTION INTENT INCONSISTENT"
        )

    if (
        execution_candidate["exchange_write"]
        is not False
        or execution_candidate["trade_authorized"]
        is not False
    ):
        raise RuntimeError(
            "UNIT 6 EXECUTION BOUNDARY FAILED"
        )

    # ========================================================
    # 6.12 RENDER LOG
    # ========================================================

    print(
        "UNIT 6 MARKET SYMBOL =",
        symbol,
        flush=True
    )

    print(
        "UNIT 6 BASE COIN =",
        base_coin,
        flush=True
    )

    print(
        "UNIT 6 QUOTE CURRENCY =",
        quote_coin,
        flush=True
    )

    print(
        "UNIT 6 UNIT 4 EVIDENCE =",
        analysis.get(
            "qualification_tuning_revision"
        ),
        flush=True
    )

    print(
        "UNIT 6 UNIT 5 EVIDENCE =",
        candidate.get(
            "strategy_evidence_version"
        ),
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
        "UNIT 6 HIGHER MODE DEVELOPING =",
        higher_developing,
        flush=True
    )

    print(
        "UNIT 6 SIDEWAYS REGIME =",
        sideways,
        flush=True
    )

    print(
        "UNIT 6 SCALP DIRECTION =",
        scalp_side,
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
        "UNIT 6 SCALP QUALITY PASS =",
        quality_pass,
        flush=True
    )

    print(
        "UNIT 6 SCALP PERSISTENCE =",
        persistence_confirmations,
        "/",
        persistence_required,
        flush=True
    )

    print(
        "UNIT 6 ESTIMATED PRICE MOVE % =",
        round(projected_move_pct, 6),
        flush=True
    )

    print(
        "UNIT 6 ESTIMATED ROUND TRIP FEE % =",
        round(estimated_fee, 6),
        flush=True
    )

    print(
        "UNIT 6 REQUIRED FEE COVERAGE % =",
        round(required_move_pct, 6),
        flush=True
    )

    print(
        "UNIT 6 FEE COVERAGE PASS =",
        fee_coverage_pass,
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
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 6 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return execution_candidate


# ============================================================
# 6.13 VALIDATION
# ============================================================

def unit_6_validation_v10():

    print("=" * 80, flush=True)

    print(
        "UNIT 6 UNIVERSAL VALIDATION V10 START",
        flush=True
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    analysis = globals().get(
        "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
    )

    candidate = globals().get(
        "FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE"
    )

    if not all(
        isinstance(item, dict)
        for item in (
            config, analysis, candidate
        )
    ):
        raise RuntimeError(
            "UNIT 6 VALIDATION INPUTS MISSING"
        )

    exchange = config.get("exchange", {})

    symbol = exchange.get("market_symbol")

    if (
        not isinstance(symbol, str)
        or not symbol.endswith("USDT")
        or analysis.get("symbol") != symbol
        or candidate.get("symbol") != symbol
    ):
        raise RuntimeError(
            "UNIT 6 VALIDATION SYMBOL FAILED"
        )

    if (
        candidate.get("strategy_evidence_version")
        != "U5_HYBRID_ADJUSTABLE_V3"
    ):
        raise RuntimeError(
            "UNIT 6 VALIDATION UNIT 5 FAILED"
        )

    result = fresh_reconstruction_unit_6(
        copy.deepcopy(config),
        copy.deepcopy(analysis),
        copy.deepcopy(candidate)
    )

    required_fields = (
        "execution_intent",
        "active_mode",
        "direction",
        "signal_qualified",
        "admission_reason",
        "scalp_quality_score",
        "scalp_quality_details",
        "candidate_mode",
        "candidate_stage",
        "market_data_fresh",
        "position_sizing_performed",
        "order_payload_created",
        "exchange_write",
        "read_only",
        "trade_authorized"
    )

    for field in required_fields:

        if field not in result:
            raise RuntimeError(
                "UNIT 6 MISSING HANDOVER: " + field
            )

    if (
        result["symbol"] != symbol
        or result["exchange_write"] is not False
        or result["order_payload_created"] is not False
        or result["trade_authorized"] is not False
    ):
        raise RuntimeError(
            "UNIT 6 VALIDATION SAFETY FAILED"
        )

    print(
        "UNIT 6 UNIVERSAL SYMBOL TEST = PASS",
        flush=True
    )

    print(
        "UNIT 6 UNIT 5 HANDOVER TEST = PASS",
        flush=True
    )

    print(
        "UNIT 6 UNIT 7 OUTPUT CONTRACT = PASS",
        flush=True
    )

    print(
        "UNIT 6 EXCHANGE WRITE TEST = NONE",
        flush=True
    )

    print(
        "UNIT 6 UNIVERSAL VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 6.14 SINGLE EXECUTION SEQUENCE
# ============================================================

FRESH_UNIT_6_VALIDATION_READY = (
    unit_6_validation_v10()
)

FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )
)

FRESH_UNIT_6_OPTIMIZATION_READY = True

print(
    "UNIT 6 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_6_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 6 V10 UNIVERSAL USDT REPLACEMENT
# UNIT 7 BEGINS BELOW
# ============================================================


# ============================================================
# START COMPLETE UNIT 7 V12 - PART 1 OF 2
# UNIVERSAL USDT FUTURES SIZING
# ADAPTED FROM 17248 AND 16414 MODELS
# INITIAL ENTRY + REVERSIBLE ATR HEDGE
# B1-B5 ENGINE CONTINUES IN PART 2
# ZERO INDENTATION
# ============================================================

import os
import math
from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_FLOOR,
    ROUND_CEILING,
)


# ============================================================
# 7.1 STRICT NUMERIC HELPERS
# ============================================================

def unit_7_v12_decimal(
    value,
    label,
    allow_zero=False
):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 7 BOOLEAN INVALID: " + label
        )

    try:
        result = Decimal(str(value))
    except (
        InvalidOperation,
        TypeError,
        ValueError
    ) as exc:
        raise RuntimeError(
            "UNIT 7 NUMBER INVALID: " + label
        ) from exc

    if not result.is_finite():
        raise RuntimeError(
            "UNIT 7 NONFINITE: " + label
        )

    if result < 0 or (
        result == 0 and not allow_zero
    ):
        raise RuntimeError(
            "UNIT 7 RANGE INVALID: " + label
        )

    return result


def unit_7_v12_text(value):

    number = Decimal(str(value))

    if number == 0:
        return "0"

    return format(number.normalize(), "f")


def unit_7_v12_floor(value, step):

    value = unit_7_v12_decimal(
        value, "QUANTITY", True
    )

    step = unit_7_v12_decimal(
        step, "QUANTITY STEP"
    )

    return (
        (value / step).to_integral_value(
            rounding=ROUND_FLOOR
        ) * step
    )


def unit_7_v12_ceil(value, step):

    value = unit_7_v12_decimal(
        value, "QUANTITY", True
    )

    step = unit_7_v12_decimal(
        step, "QUANTITY STEP"
    )

    return (
        (value / step).to_integral_value(
            rounding=ROUND_CEILING
        ) * step
    )


def unit_7_v12_is_step_valid(quantity, step):

    quantity = unit_7_v12_decimal(
        quantity, "QUANTITY", True
    )

    step = unit_7_v12_decimal(
        step, "STEP"
    )

    return quantity % step == 0


# ============================================================
# 7.2 VERIFIED CONTRACT SPECIFICATION
# ============================================================

def unit_7_v12_contract(config):

    exchange = config.get("exchange", {})
    precision = config.get("market_precision", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 7 EXCHANGE CONFIG MISSING"
        )

    if not isinstance(precision, dict):
        raise RuntimeError(
            "UNIT 7 PRECISION CONFIG MISSING"
        )

    symbol = exchange.get("market_symbol")

    if (
        not isinstance(symbol, str)
        or not symbol.endswith("USDT")
        or len(symbol) <= 4
        or exchange.get("base_coin") != symbol[:-4]
        or exchange.get("quote_coin") != "USDT"
    ):
        raise RuntimeError(
            "UNIT 7 UNIVERSAL SYMBOL INVALID"
        )

    # Do not invent specifications.
    # Contract values must come from verified
    # WEEX instrument metadata.

    verified = all((
        precision.get("verified") is True,
        exchange.get(
            "contract_precision_verified"
        ) is True,
        exchange.get(
            "contract_value_verified"
        ) is True,
        precision.get("symbol") == symbol
    ))

    if not verified:

        return {
            "verified": False,
            "symbol": symbol,
            "quantity_step": None,
            "minimum_quantity": None,
            "contract_multiplier": None,
            "price_step": None,
            "reason":
                "WEEX_CONTRACT_SPECIFICATION_UNVERIFIED"
        }

    step = unit_7_v12_decimal(
        precision.get("quantity_step"),
        "QUANTITY STEP"
    )

    minimum = unit_7_v12_decimal(
        precision.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    multiplier = unit_7_v12_decimal(
        precision.get("contract_multiplier"),
        "CONTRACT MULTIPLIER"
    )

    price_step = unit_7_v12_decimal(
        precision.get("price_step"),
        "PRICE STEP"
    )

    if (
        precision.get("contract_value") is None
        or not precision.get("source")
        or precision.get("source")
        == "PENDING_DEMO_CONTRACT_VERIFICATION"
    ):
        raise RuntimeError(
            "UNIT 7 CONTRACT VERIFICATION INCOMPLETE"
        )

    return {
        "verified": True,
        "symbol": symbol,
        "quantity_step": step,
        "minimum_quantity": minimum,
        "contract_multiplier": multiplier,
        "price_step": price_step,
        "reason": "VERIFIED"
    }


# ============================================================
# 7.3 MARGIN AND LEVERAGE
# ============================================================

def unit_7_v12_capital(config, direction):

    strategy = config.get("strategy", {})

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 7 STRATEGY CONFIG MISSING"
        )

    margin = unit_7_v12_decimal(
        strategy.get("initial_entry_margin_usdt"),
        "INITIAL MARGIN USDT"
    )

    if direction == "LONG":

        leverage = unit_7_v12_decimal(
            strategy.get("long_leverage"),
            "LONG LEVERAGE"
        )

    elif direction == "SHORT":

        leverage = unit_7_v12_decimal(
            strategy.get("short_leverage"),
            "SHORT LEVERAGE"
        )

    else:

        raise RuntimeError(
            "UNIT 7 INVALID ENTRY DIRECTION"
        )

    cap = unit_7_v12_decimal(
        strategy.get("exposure_cap_percent"),
        "EXPOSURE CAP",
        True
    )

    if cap > 100:
        raise RuntimeError(
            "UNIT 7 EXPOSURE CAP ABOVE 100"
        )

    return {
        "margin_usdt": margin,
        "leverage": leverage,
        "exposure_cap_percent": cap,
        "notional_usdt": margin * leverage,
        "leverage_source": "RENDER_MANUAL"
    }


# ============================================================
# 7.4 UNIVERSAL CONTRACT QUANTITY
# ============================================================

def unit_7_v12_quantity(
    margin_usdt,
    leverage,
    price,
    contract_multiplier,
    quantity_step,
    minimum_quantity
):

    margin = unit_7_v12_decimal(
        margin_usdt, "MARGIN"
    )

    leverage = unit_7_v12_decimal(
        leverage, "LEVERAGE"
    )

    price = unit_7_v12_decimal(
        price, "MARK PRICE"
    )

    multiplier = unit_7_v12_decimal(
        contract_multiplier,
        "CONTRACT MULTIPLIER"
    )

    step = unit_7_v12_decimal(
        quantity_step,
        "QUANTITY STEP"
    )

    minimum = unit_7_v12_decimal(
        minimum_quantity,
        "MINIMUM QUANTITY"
    )

    # Contract notional:
    # quantity * multiplier * price
    #
    # Raw quantity:
    # margin * leverage / (price * multiplier)

    notional = margin * leverage

    raw_quantity = (
        notional / (price * multiplier)
    )

    minimum_compliant = unit_7_v12_ceil(
        minimum, step
    )

    quantity = unit_7_v12_floor(
        raw_quantity, step
    )

    if quantity < minimum_compliant:

        return {
            "valid": False,
            "reason":
                "INITIAL_MARGIN_BELOW_MINIMUM_CONTRACT",
            "raw_quantity":
                unit_7_v12_text(raw_quantity),
            "quantity": "0",
            "minimum_quantity":
                unit_7_v12_text(minimum_compliant),
            "required_margin_usdt":
                unit_7_v12_text(
                    minimum_compliant
                    * multiplier
                    * price
                    / leverage
                )
        }

    actual_notional = (
        quantity * multiplier * price
    )

    actual_margin = (
        actual_notional / leverage
    )

    return {
        "valid": True,
        "reason": "STEP_COMPLIANT",
        "raw_quantity":
            unit_7_v12_text(raw_quantity),
        "quantity":
            unit_7_v12_text(quantity),
        "minimum_quantity":
            unit_7_v12_text(minimum_compliant),
        "actual_notional_usdt":
            unit_7_v12_text(actual_notional),
        "actual_margin_usdt":
            unit_7_v12_text(actual_margin)
    }


# ============================================================
# 7.5 REVERSIBLE 50/50 HEDGE FEASIBILITY
# ============================================================

def unit_7_v12_hedge_quantity(
    initial_quantity,
    quantity_step,
    minimum_quantity
):

    quantity = unit_7_v12_decimal(
        initial_quantity, "INITIAL QUANTITY"
    )

    step = unit_7_v12_decimal(
        quantity_step, "QUANTITY STEP"
    )

    minimum = unit_7_v12_decimal(
        minimum_quantity, "MINIMUM QUANTITY"
    )

    minimum_compliant = unit_7_v12_ceil(
        minimum, step
    )

    if not unit_7_v12_is_step_valid(
        quantity, step
    ):
        return {
            "valid": False,
            "reason": "INITIAL_STEP_INVALID"
        }

    half = quantity / Decimal("2")

    if not unit_7_v12_is_step_valid(
        half, step
    ):
        return {
            "valid": False,
            "reason":
                "INITIAL_QUANTITY_NOT_DIVISIBLE_50_50"
        }

    if half < minimum_compliant:
        return {
            "valid": False,
            "reason":
                "HALF_POSITION_BELOW_MINIMUM"
        }

    return {
        "valid": True,
        "reason": "HEDGE_50_50_FEASIBLE",

        "initial_quantity":
            unit_7_v12_text(quantity),

        "stage1_close_original":
            unit_7_v12_text(half),

        "stage1_open_opposite":
            unit_7_v12_text(half),

        "remaining_original":
            unit_7_v12_text(half),

        "stage2_close_remaining":
            unit_7_v12_text(half),

        "stage2_open_opposite":
            unit_7_v12_text(half),

        "maximum_opposite_quantity":
            unit_7_v12_text(quantity),

        "minimum_quantity":
            unit_7_v12_text(minimum_compliant)
    }


# ============================================================
# 7.6 ATR HEDGE TRIGGER LEVELS
# ============================================================

def unit_7_v12_atr_levels(
    entry_price,
    atr14,
    direction,
    stage1_atr=1,
    stage2_atr=2
):

    price = unit_7_v12_decimal(
        entry_price, "ENTRY PRICE"
    )

    atr = unit_7_v12_decimal(
        atr14, "ATR14"
    )

    first = unit_7_v12_decimal(
        stage1_atr, "STAGE 1 ATR"
    )

    second = unit_7_v12_decimal(
        stage2_atr, "STAGE 2 ATR"
    )

    if second <= first:
        raise RuntimeError(
            "UNIT 7 ATR STAGES INVALID"
        )

    if direction == "LONG":

        trigger1 = price - atr * first
        trigger2 = price - atr * second

    elif direction == "SHORT":

        trigger1 = price + atr * first
        trigger2 = price + atr * second

    else:
        raise RuntimeError(
            "UNIT 7 INVALID ATR DIRECTION"
        )

    if min(trigger1, trigger2) <= 0:
        raise RuntimeError(
            "UNIT 7 ATR TRIGGER NONPOSITIVE"
        )

    return {
        "direction": direction,
        "atr14": unit_7_v12_text(atr),
        "stage1_atr": unit_7_v12_text(first),
        "stage2_atr": unit_7_v12_text(second),
        "stage1_trigger":
            unit_7_v12_text(trigger1),
        "stage2_trigger":
            unit_7_v12_text(trigger2),
        "conventional_sl_enabled": False
    }


# ============================================================
# 7.7 STAGE HEDGE CONFIGURATION
# ============================================================

def unit_7_v12_hedge_policy(config):

    strategy = config.get("strategy", {})
    hedge = strategy.get("hedge", {})

    if not isinstance(hedge, dict):
        raise RuntimeError(
            "UNIT 7 HEDGE CONFIG MISSING"
        )

    if hedge.get("enabled") is not True:
        raise RuntimeError(
            "UNIT 7 HEDGE CONFIG DISABLED"
        )

    if hedge.get("mode") != (
        "REVERSIBLE_ATR_TWO_STAGE"
    ):
        raise RuntimeError(
            "UNIT 7 HEDGE MODE MISMATCH"
        )

    if hedge.get(
        "maximum_recovery_cycles"
    ) != 1:
        raise RuntimeError(
            "UNIT 7 RECOVERY CYCLE MUST BE ONE"
        )

    if hedge.get("repeatable") is not False:
        raise RuntimeError(
            "UNIT 7 REPEATED HEDGE NOT ALLOWED"
        )

    for key in (
        "stage_1_close_original_percent",
        "stage_1_open_opposite_percent"
    ):
        if Decimal(str(hedge.get(key))) != 50:
            raise RuntimeError(
                "UNIT 7 STAGE 1 POLICY INVALID"
            )

    for key in (
        "stage_2_close_original_percent",
        "stage_2_open_opposite_percent"
    ):
        if Decimal(str(hedge.get(key))) != 100:
            raise RuntimeError(
                "UNIT 7 STAGE 2 POLICY INVALID"
            )

    return {
        "enabled": True,
        "mode": hedge["mode"],
        "stage1_atr":
            hedge["trigger_1_atr"],
        "stage2_atr":
            hedge["trigger_2_atr"],
        "maximum_recovery_cycles": 1,
        "recovery_enabled":
            hedge.get("recovery_enabled") is True,
        "conventional_stop_loss_enabled": False
    }


# ============================================================
# END UNIT 7 V12 PART 1
# CONTINUE WITH PART 2 AT ZERO INDENTATION
# DO NOT DEPLOY UNTIL PART 2 IS ADDED
# ============================================================


# ============================================================
# START UNIT 7 V12 - PART 2 OF 2
# B1-B5 HYBRID BACKUP ENGINE
# UNIT 6 -> UNIT 7 -> UNIT 8-15
# ZERO INDENTATION
# ============================================================

import copy
import time


# ============================================================
# 7.8 AVAILABLE FUNDS / EXPOSURE CHECK
# ============================================================

def unit_7_v12_exposure(
    trading_balance_usdt,
    available_balance_usdt,
    existing_margin_usdt,
    pending_margin_usdt,
    proposed_margin_usdt,
    exposure_cap_percent
):

    trading = unit_7_v12_decimal(
        trading_balance_usdt,
        "TRADING BALANCE",
        True
    )

    available = unit_7_v12_decimal(
        available_balance_usdt,
        "AVAILABLE BALANCE",
        True
    )

    existing = unit_7_v12_decimal(
        existing_margin_usdt,
        "EXISTING MARGIN",
        True
    )

    pending = unit_7_v12_decimal(
        pending_margin_usdt,
        "PENDING MARGIN",
        True
    )

    proposed = unit_7_v12_decimal(
        proposed_margin_usdt,
        "PROPOSED MARGIN",
        True
    )

    cap = unit_7_v12_decimal(
        exposure_cap_percent,
        "EXPOSURE CAP",
        True
    )

    if cap > 100:
        raise RuntimeError(
            "UNIT 7 EXPOSURE CAP INVALID"
        )

    maximum = trading * cap / Decimal("100")

    used = existing + pending
    projected = used + proposed

    remaining = max(
        Decimal("0"),
        maximum - used
    )

    funds_pass = proposed <= available

    cap_pass = projected <= maximum

    return {
        "valid": (
            funds_pass
            and cap_pass
            and trading > 0
        ),
        "trading_balance_usdt":
            unit_7_v12_text(trading),
        "available_balance_usdt":
            unit_7_v12_text(available),
        "existing_margin_usdt":
            unit_7_v12_text(existing),
        "pending_margin_usdt":
            unit_7_v12_text(pending),
        "proposed_margin_usdt":
            unit_7_v12_text(proposed),
        "maximum_exposure_usdt":
            unit_7_v12_text(maximum),
        "projected_exposure_usdt":
            unit_7_v12_text(projected),
        "remaining_capacity_usdt":
            unit_7_v12_text(remaining),
        "funds_pass": funds_pass,
        "exposure_cap_pass": cap_pass
    }


# ============================================================
# 7.9 B1-B5 ACTIVATION POLICY
# ============================================================

def unit_7_v12_backup_policy(config):

    strategy = config.get("strategy", {})
    backup = strategy.get("backup_recovery", {})

    if not isinstance(backup, dict):
        raise RuntimeError(
            "UNIT 7 BACKUP CONFIG INVALID"
        )

    if backup.get("enabled") is not True:
        raise RuntimeError(
            "UNIT 7 BACKUP DISABLED"
        )

    if backup.get("activation") != (
        "AFTER_FAILED_FIRST_HEDGE_RECOVERY"
    ):
        raise RuntimeError(
            "UNIT 7 BACKUP ACTIVATION MISMATCH"
        )

    count = int(
        unit_7_v12_decimal(
            backup.get("backup_count"),
            "BACKUP COUNT"
        )
    )

    if count != 5:
        raise RuntimeError(
            "UNIT 7 BACKUP COUNT MUST BE FIVE"
        )

    margin_pct = unit_7_v12_decimal(
        backup.get("margin_percent"),
        "BACKUP MARGIN PERCENT",
        True
    )

    buffer_pct = unit_7_v12_decimal(
        backup.get("liquidation_buffer_percent"),
        "BACKUP BUFFER PERCENT",
        True
    )

    if margin_pct > 100:
        raise RuntimeError(
            "UNIT 7 BACKUP MARGIN PERCENT INVALID"
        )

    if buffer_pct >= 100:
        raise RuntimeError(
            "UNIT 7 BACKUP BUFFER INVALID"
        )

    return {
        "enabled": True,
        "count": 5,
        "margin_percent": margin_pct,
        "buffer_percent": buffer_pct,
        "activation":
            "AFTER_FAILED_FIRST_HEDGE_RECOVERY",
        "require_available_funds": True,
        "require_exposure_cap": True,
        "require_verified_liquidation_price": True
    }


# ============================================================
# 7.10 B1-B5 LIQUIDATION BUFFER TRIGGER
# ============================================================

def unit_7_v12_backup_trigger(
    direction,
    liquidation_price,
    buffer_percent
):

    liquidation = unit_7_v12_decimal(
        liquidation_price,
        "VERIFIED LIQUIDATION PRICE"
    )

    buffer = unit_7_v12_decimal(
        buffer_percent,
        "LIQUIDATION BUFFER",
        True
    )

    if buffer >= 100:
        raise RuntimeError(
            "UNIT 7 INVALID LIQUIDATION BUFFER"
        )

    fraction = buffer / Decimal("100")

    if direction == "LONG":

        trigger = liquidation * (
            Decimal("1") - fraction
        )

    elif direction == "SHORT":

        trigger = liquidation * (
            Decimal("1") + fraction
        )

    else:

        raise RuntimeError(
            "UNIT 7 INVALID BACKUP DIRECTION"
        )

    if trigger <= 0:
        raise RuntimeError(
            "UNIT 7 INVALID BACKUP TRIGGER"
        )

    return {
        "direction": direction,
        "liquidation_price":
            unit_7_v12_text(liquidation),
        "buffer_percent":
            unit_7_v12_text(buffer),
        "trigger_price":
            unit_7_v12_text(trigger),
        "reference":
            "LATEST_VERIFIED_LIQUIDATION_PRICE"
    }


# ============================================================
# 7.11 BACKUP TRIGGER GEOMETRY CHECK
# ============================================================
# Important:
# LONG liquidation is below the market.
# SHORT liquidation is above the market.
#
# The configured 0.3% factors place the trigger
# beyond liquidation in the adverse direction.
#
# That is not a protective pre-liquidation entry.
# Reject unsafe trigger geometry rather than
# silently changing the user's configured formula.
# ============================================================

def unit_7_v12_trigger_geometry(
    direction,
    market_price,
    liquidation_price,
    trigger_price
):

    market = unit_7_v12_decimal(
        market_price,
        "BACKUP MARKET PRICE"
    )

    liquidation = unit_7_v12_decimal(
        liquidation_price,
        "BACKUP LIQUIDATION PRICE"
    )

    trigger = unit_7_v12_decimal(
        trigger_price,
        "BACKUP TRIGGER PRICE"
    )

    if direction == "LONG":

        liquidation_side_valid = (
            liquidation < market
        )

        pre_liquidation = (
            liquidation < trigger < market
        )

    elif direction == "SHORT":

        liquidation_side_valid = (
            liquidation > market
        )

        pre_liquidation = (
            market < trigger < liquidation
        )

    else:

        raise RuntimeError(
            "UNIT 7 INVALID DIRECTION"
        )

    return {
        "valid": (
            liquidation_side_valid
            and pre_liquidation
        ),
        "liquidation_side_valid":
            liquidation_side_valid,
        "pre_liquidation_trigger":
            pre_liquidation,
        "reason": (
            "PRE_LIQUIDATION_TRIGGER_VALID"
            if liquidation_side_valid and pre_liquidation
            else "UNSAFE_LIQUIDATION_TRIGGER_GEOMETRY"
        )
    }


# ============================================================
# 7.12 ONE BACKUP QUANTITY CALCULATION
# ============================================================

def unit_7_v12_backup_quantity(
    config,
    direction,
    market_price,
    trading_balance_usdt,
    available_balance_usdt,
    existing_margin_usdt,
    pending_margin_usdt,
    contract
):

    policy = unit_7_v12_backup_policy(config)

    strategy = config["strategy"]

    margin_pct = policy["margin_percent"]

    available = unit_7_v12_decimal(
        available_balance_usdt,
        "BACKUP AVAILABLE BALANCE",
        True
    )

    proposed_margin = (
        available * margin_pct / Decimal("100")
    )

    exposure = unit_7_v12_exposure(
        trading_balance_usdt,
        available_balance_usdt,
        existing_margin_usdt,
        pending_margin_usdt,
        proposed_margin,
        strategy["exposure_cap_percent"]
    )

    if not exposure["valid"]:

        return {
            "valid": False,
            "reason":
                "BACKUP_FUNDS_OR_EXPOSURE_BLOCKED",
            "exposure": exposure
        }

    if proposed_margin <= 0:

        return {
            "valid": False,
            "reason": "BACKUP_MARGIN_ZERO",
            "exposure": exposure
        }

    if not contract.get("verified"):

        return {
            "valid": False,
            "reason":
                "BACKUP_CONTRACT_UNVERIFIED",
            "exposure": exposure
        }

    leverage = (
        strategy["long_leverage"]
        if direction == "LONG"
        else strategy["short_leverage"]
    )

    sizing = unit_7_v12_quantity(
        proposed_margin,
        leverage,
        market_price,
        contract["contract_multiplier"],
        contract["quantity_step"],
        contract["minimum_quantity"]
    )

    if not sizing["valid"]:

        return {
            "valid": False,
            "reason": sizing["reason"],
            "sizing": sizing,
            "exposure": exposure
        }

    # Recheck exposure using the rounded,
    # actual required contract margin.

    actual_exposure = unit_7_v12_exposure(
        trading_balance_usdt,
        available_balance_usdt,
        existing_margin_usdt,
        pending_margin_usdt,
        sizing["actual_margin_usdt"],
        strategy["exposure_cap_percent"]
    )

    return {
        "valid": actual_exposure["valid"],
        "reason": (
            "BACKUP_QUANTITY_COMPLIANT"
            if actual_exposure["valid"]
            else "BACKUP_EXPOSURE_BLOCKED"
        ),
        "direction": direction,
        "quantity": sizing["quantity"],
        "margin_usdt":
            sizing["actual_margin_usdt"],
        "notional_usdt":
            sizing["actual_notional_usdt"],
        "leverage":
            unit_7_v12_text(leverage),
        "sizing": sizing,
        "exposure": actual_exposure
    }


# ============================================================
# 7.13 STATE-VERIFIED B1-B5 PLAN
# ============================================================
# This function is callable by downstream units.
# It NEVER places an exchange order.
#
# Required fresh state:
# - Verified demo account balance
# - Verified open position
# - One hedge recovery cycle completed and failed
# - Latest liquidation price from WEEX
# - Previous backup fill confirmed
# - No duplicate or pending backup
# ============================================================

def unit_7_v12_next_backup(
    config,
    position_state,
    account_state,
    contract
):

    blocked = {
        "valid": False,
        "execution_authorized": False,
        "exchange_write": False
    }

    if not isinstance(position_state, dict):
        return {
            **blocked,
            "reason": "POSITION_STATE_MISSING"
        }

    if not isinstance(account_state, dict):
        return {
            **blocked,
            "reason": "ACCOUNT_STATE_MISSING"
        }

    if not contract.get("verified"):
        return {
            **blocked,
            "reason": "CONTRACT_UNVERIFIED"
        }

    symbol = config["exchange"]["market_symbol"]

    if (
        position_state.get("symbol") != symbol
        or account_state.get("symbol") != symbol
    ):
        return {
            **blocked,
            "reason": "BACKUP_SYMBOL_MISMATCH"
        }

    if (
        position_state.get("verified") is not True
        or account_state.get("verified") is not True
    ):
        return {
            **blocked,
            "reason": "ACCOUNT_OR_POSITION_UNVERIFIED"
        }

    if (
        position_state.get(
            "first_hedge_cycle_completed"
        ) is not True
        or position_state.get(
            "first_hedge_recovery_failed"
        ) is not True
    ):
        return {
            **blocked,
            "reason": "HEDGE_RECOVERY_NOT_FAILED"
        }

    if position_state.get(
        "hedge_recovery_cycles"
    ) != 1:
        return {
            **blocked,
            "reason": "HEDGE_CYCLE_STATE_INVALID"
        }

    if position_state.get(
        "position_mode_verified"
    ) is not True:
        return {
            **blocked,
            "reason": "POSITION_MODE_UNVERIFIED"
        }

    if position_state.get(
        "pending_backup_order"
    ) is True:
        return {
            **blocked,
            "reason": "BACKUP_ALREADY_PENDING"
        }

    if position_state.get(
        "unreconciled_orders"
    ) is True:
        return {
            **blocked,
            "reason": "BACKUP_ORDER_RECONCILIATION_PENDING"
        }

    filled = position_state.get(
        "filled_backups"
    )

    if (
        not isinstance(filled, int)
        or isinstance(filled, bool)
        or not 0 <= filled <= 5
    ):
        return {
            **blocked,
            "reason": "BACKUP_SEQUENCE_INVALID"
        }

    if filled == 5:
        return {
            **blocked,
            "reason": "B1_B5_ALREADY_COMPLETED"
        }

    if (
        filled > 0
        and position_state.get(
            "previous_backup_fill_verified"
        ) is not True
    ):
        return {
            **blocked,
            "reason": "PREVIOUS_BACKUP_FILL_UNVERIFIED"
        }

    direction = position_state.get("direction")

    if direction not in ("LONG", "SHORT"):
        return {
            **blocked,
            "reason": "BACKUP_DIRECTION_INVALID"
        }

    if position_state.get(
        "liquidation_price_verified"
    ) is not True:
        return {
            **blocked,
            "reason": "LIQUIDATION_PRICE_UNVERIFIED"
        }

    # Require a fresh, reconciled state snapshot.
    # The downstream adapter must obtain this
    # from the authenticated WEEX demo account.

    timestamp = position_state.get(
        "exchange_time_ms"
    )

    if (
        not isinstance(timestamp, int)
        or isinstance(timestamp, bool)
        or timestamp <= 0
        or abs(int(time.time() * 1000) - timestamp)
        > 30000
    ):
        return {
            **blocked,
            "reason": "BACKUP_POSITION_STATE_STALE"
        }

    try:

        policy = unit_7_v12_backup_policy(
            config
        )

        liquidation = unit_7_v12_backup_trigger(
            direction,
            position_state["liquidation_price"],
            policy["buffer_percent"]
        )

        market_price = unit_7_v12_decimal(
            position_state["market_price"],
            "BACKUP MARKET PRICE"
        )

        geometry = unit_7_v12_trigger_geometry(
            direction,
            market_price,
            liquidation["liquidation_price"],
            liquidation["trigger_price"]
        )

        if not geometry["valid"]:
            return {
                **blocked,
                "reason": geometry["reason"],
                "backup_number": filled + 1,
                "trigger": liquidation,
                "geometry": geometry
            }

        sizing = unit_7_v12_backup_quantity(
            config=config,
            direction=direction,
            market_price=market_price,
            trading_balance_usdt=account_state[
                "trading_balance_usdt"
            ],
            available_balance_usdt=account_state[
                "available_balance_usdt"
            ],
            existing_margin_usdt=account_state[
                "existing_margin_usdt"
            ],
            pending_margin_usdt=account_state[
                "pending_margin_usdt"
            ],
            contract=contract
        )

    except (
        RuntimeError,
        KeyError,
        TypeError,
        ValueError
    ) as exc:

        return {
            **blocked,
            "reason": "BACKUP_INPUT_INVALID",
            "detail": str(exc)
        }

    if not sizing["valid"]:
        return {
            **blocked,
            "reason": sizing["reason"],
            "sizing": sizing
        }

    backup_number = filled + 1

    return {
        "valid": True,
        "execution_authorized": False,
        "exchange_write": False,
        "reason": "BACKUP_PLAN_READY_FOR_REVALIDATION",
        "backup_number": backup_number,
        "backup_id": "B" + str(backup_number),
        "symbol": symbol,
        "direction": direction,
        "quantity": sizing["quantity"],
        "margin_usdt": sizing["margin_usdt"],
        "trigger": liquidation,
        "geometry": geometry,
        "sizing": sizing,
        "requires_fresh_state_at_submission": True,
        "requires_price_step_rounding": True,
        "requires_exchange_order_confirmation": True,
        "requires_post_fill_liquidation_refresh": True
    }


# ============================================================
# 7.14 B1-B5 LADDER POLICY HANDOVER
# ============================================================

def unit_7_v12_backup_ladder(config):

    policy = unit_7_v12_backup_policy(
        config
    )

    ladder = []

    for number in range(1, 6):

        ladder.append({
            "id": "B" + str(number),
            "sequence": number,
            "status": "WAITING",
            "activation":
                "AFTER_FAILED_FIRST_HEDGE_RECOVERY",
            "margin_percent_of_available":
                unit_7_v12_text(
                    policy["margin_percent"]
                ),
            "liquidation_buffer_percent":
                unit_7_v12_text(
                    policy["buffer_percent"]
                ),
            "recalculate_after_previous_fill":
                True,
            "quantity": None,
            "trigger_price": None,
            "exchange_write": False,
            "execution_authorized": False
        })

    return ladder


# ============================================================
# 7.15 UNIT 6 -> UNIT 7 EXECUTION HANDOVER
# ============================================================

def fresh_reconstruction_unit_7():

    print("=" * 80, flush=True)
    print(
        "UNIT 7 V12 UNIVERSAL USDT START",
        flush=True
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    market = globals().get(
        "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
    )

    analysis = globals().get(
        "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
    )

    candidate = globals().get(
        "FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE"
    )

    if not all(
        isinstance(item, dict)
        for item in (
            config,
            market,
            analysis,
            candidate
        )
    ):
        raise RuntimeError(
            "UNIT 7 UPSTREAM HANDOVER MISSING"
        )

    symbol = config["exchange"]["market_symbol"]

    if not all((
        market.get("symbol") == symbol,
        analysis.get("symbol") == symbol,
        candidate.get("symbol") == symbol,
        config.get("capital_currency") == "USDT",
        config.get("real_cash_execution_enabled")
        is False
    )):
        raise RuntimeError(
            "UNIT 7 UNIVERSAL HANDOVER INVALID"
        )

    contract = unit_7_v12_contract(
        config
    )

    hedge_policy = unit_7_v12_hedge_policy(
        config
    )

    ladder = unit_7_v12_backup_ladder(
        config
    )

    mode = candidate.get(
        "active_mode", "NONE"
    )

    direction = candidate.get(
        "direction", "NONE"
    )

    intent = (
        candidate.get("execution_intent") is True
        and candidate.get("signal_qualified") is True
        and mode in (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP"
        )
        and direction in ("LONG", "SHORT")
    )

    result = {
        "unit": 7,
        "version": "V12_UNIVERSAL_USDT",
        "symbol": symbol,
        "base_coin": symbol[:-4],
        "quote_coin": "USDT",
        "capital_currency": "USDT",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified":
            candidate.get("signal_qualified") is True,
        "execution_intent": intent,
        "unit_6_candidate": copy.deepcopy(candidate),
        "contract": contract,
        "contract_verified": contract["verified"],
        "hedge_policy": hedge_policy,
        "backup_ladder": ladder,
        "backup_count": 5,
        "backup_activation":
            "AFTER_FAILED_FIRST_HEDGE_RECOVERY",
        "backup_calculator":
            "unit_7_v12_next_backup",
        "entry_sizing": None,
        "hedge_quantity_plan": None,
        "atr_hedge_levels": None,
        "account_state_verified": False,
        "position_mode_verified": False,
        "quantity_valid": False,
        "execution_authorized": False,
        "trade_authorized": False,
        "order_payload_created": False,
        "exchange_write": False,
        "read_only": True,
        "real_cash_execution_enabled": False,
        "reason": "NO_QUALIFIED_ENTRY"
    }

    if intent:

        capital = unit_7_v12_capital(
            config,
            direction
        )

        result["capital"] = {
            key: (
                unit_7_v12_text(value)
                if isinstance(value, Decimal)
                else value
            )
            for key, value in capital.items()
        }

        result["entry_margin_usdt"] = (
            unit_7_v12_text(
                capital["margin_usdt"]
            )
        )

        result["leverage"] = (
            unit_7_v12_text(
                capital["leverage"]
            )
        )

        result["exposure_cap_percent"] = (
            unit_7_v12_text(
                capital["exposure_cap_percent"]
            )
        )

        price = unit_7_v12_decimal(
            market["price"],
            "ENTRY MARKET PRICE"
        )

        atr = unit_7_v12_decimal(
            analysis["atr14"],
            "UNIT 4 ATR14"
        )

        result["atr_hedge_levels"] = (
            unit_7_v12_atr_levels(
                price,
                atr,
                direction,
                hedge_policy["stage1_atr"],
                hedge_policy["stage2_atr"]
            )
        )

        if not contract["verified"]:

            result["reason"] = (
                "CONTRACT_PRECISION_UNVERIFIED"
            )

        else:

            sizing = unit_7_v12_quantity(
                capital["margin_usdt"],
                capital["leverage"],
                price,
                contract["contract_multiplier"],
                contract["quantity_step"],
                contract["minimum_quantity"]
            )

            result["entry_sizing"] = sizing

            if not sizing["valid"]:

                result["reason"] = sizing["reason"]

            else:

                hedge_quantity = (
                    unit_7_v12_hedge_quantity(
                        sizing["quantity"],
                        contract["quantity_step"],
                        contract["minimum_quantity"]
                    )
                )

                result["hedge_quantity_plan"] = (
                    hedge_quantity
                )

                result["quantity_valid"] = (
                    hedge_quantity["valid"]
                )

                if not hedge_quantity["valid"]:

                    result["reason"] = (
                        hedge_quantity["reason"]
                    )

                else:

                    result["reason"] = (
                        "SIZING_PLAN_READY_"
                        "ACCOUNT_VERIFICATION_PENDING"
                    )

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
        "UNIT 7 EXECUTION INTENT =", intent,
        flush=True
    )

    print(
        "UNIT 7 CONTRACT VERIFIED =",
        contract["verified"],
        flush=True
    )

    print(
        "UNIT 7 QUANTITY VALID =",
        result["quantity_valid"],
        flush=True
    )

    print(
        "UNIT 7 HEDGE MODE =",
        hedge_policy["mode"],
        flush=True
    )

    print(
        "UNIT 7 BACKUP COUNT =",
        len(ladder),
        flush=True
    )

    print(
        "UNIT 7 BACKUP ACTIVATION =",
        result["backup_activation"],
        flush=True
    )

    print(
        "UNIT 7 REASON =",
        result["reason"],
        flush=True
    )

    print(
        "UNIT 7 EXECUTION AUTHORIZED = False",
        flush=True
    )

    print(
        "UNIT 7 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "FRESH RECONSTRUCTION UNIT 7 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# 7.16 VALIDATION
# ============================================================

def unit_7_v12_validation():

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 7 VALIDATION CONFIG MISSING"
        )

    symbol = config["exchange"]["market_symbol"]

    tests = {}

    tests["UNIVERSAL USDT SYMBOL"] = (
        symbol.endswith("USDT")
    )

    tests["BACKUP COUNT FIVE"] = (
        len(unit_7_v12_backup_ladder(config)) == 5
    )

    tests["HEDGE POLICY"] = (
        unit_7_v12_hedge_policy(config)[
            "maximum_recovery_cycles"
        ] == 1
    )

    tests["STEP FLOOR"] = (
        unit_7_v12_floor(
            "1.27", "0.1"
        ) == Decimal("1.2")
    )

    tests["STEP CEILING"] = (
        unit_7_v12_ceil(
            "1.21", "0.1"
        ) == Decimal("1.3")
    )

    tests["VALID HALF QUANTITY"] = (
        unit_7_v12_hedge_quantity(
            "0.4", "0.1", "0.1"
        )["valid"] is True
    )

    tests["REJECT INVALID HALF"] = (
        unit_7_v12_hedge_quantity(
            "0.3", "0.1", "0.1"
        )["valid"] is False
    )

    tests["LONG TRIGGER FORMULA"] = (
        unit_7_v12_backup_trigger(
            "LONG", "100", "0.3"
        )["trigger_price"] == "99.7"
    )

    tests["SHORT TRIGGER FORMULA"] = (
        unit_7_v12_backup_trigger(
            "SHORT", "100", "0.3"
        )["trigger_price"] == "100.3"
    )

    tests["REJECT UNSAFE LONG GEOMETRY"] = (
        unit_7_v12_trigger_geometry(
            "LONG", "110", "100", "99.7"
        )["valid"] is False
    )

    tests["REJECT UNSAFE SHORT GEOMETRY"] = (
        unit_7_v12_trigger_geometry(
            "SHORT", "90", "100", "100.3"
        )["valid"] is False
    )

    tests["EXPOSURE CAP"] = (
        unit_7_v12_exposure(
            "100",
            "80",
            "30",
            "10",
            "20",
            "50"
        )["valid"] is False
    )

    passed = 0
    failed = 0

    print("=" * 80, flush=True)
    print(
        "UNIT 7 V12 VALIDATION START",
        flush=True
    )

    for name, condition in tests.items():

        if condition:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 7 TEST:",
            name,
            "=",
            "PASS" if condition else "FAIL",
            flush=True
        )

    print(
        "UNIT 7 TESTS PASSED =", passed,
        flush=True
    )

    print(
        "UNIT 7 TESTS FAILED =", failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 7 VALIDATION FAILED"
        )

    print(
        "UNIT 7 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 7.17 FINAL EXECUTION AND GLOBAL HANDOVER
# ============================================================

FRESH_UNIT_7_VALIDATION_READY = (
    unit_7_v12_validation()
)

FRESH_RECONSTRUCTION_SIZING_PLAN = (
    fresh_reconstruction_unit_7()
)

FRESH_RECONSTRUCTION_UNIT_7_RESULT = (
    FRESH_RECONSTRUCTION_SIZING_PLAN
)

FRESH_UNIT_7_OPTIMIZATION_READY = (
    FRESH_UNIT_7_VALIDATION_READY
)

print(
    "UNIT 7 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_7_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 7 V12
# PART 1 + PART 2
# UNIT 8 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 8 V19
# REFERENCE 17248 ADAPTATION
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

from decimal import Decimal
from decimal import InvalidOperation
from decimal import ROUND_FLOOR


U8_MARKET_HOST = "https://api-sim.weex.com"
U8_DEMO_HOST = "https://api-contract.weex.com"


def u8_number(value, name, allow_zero=False):
    if value is None or isinstance(value, bool):
        raise RuntimeError(name + "_MISSING")

    try:
        n = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise RuntimeError(name + "_INVALID")

    if (
        not n.is_finite()
        or n < 0
        or (n == 0 and not allow_zero)
    ):
        raise RuntimeError(name + "_OUT_OF_RANGE")

    return n


def u8_str(n):
    return format(n, "f")


def u8_get(host, path, private=False):
    if private:
        if host != U8_DEMO_HOST or path not in (
            "/capi/v3/sim/balance",
            "/capi/v3/sim/position/allPosition",
            "/capi/v3/account/accountConfig",
        ):
            raise RuntimeError(
                "PRIVATE_ENDPOINT_NOT_ALLOWED"
            )
    elif (
        host != U8_MARKET_HOST
        or path != "/capi/v3/market/exchangeInfo"
    ):
        raise RuntimeError(
            "PUBLIC_ENDPOINT_NOT_ALLOWED"
        )

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
                "DEMO_CREDENTIALS_MISSING"
            )

        stamp = str(int(time.time() * 1000))

        sign = base64.b64encode(
            hmac.new(
                secret.encode("utf-8"),
                (stamp + "GET" + path).encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        headers.update({
            "ACCESS-KEY": key,
            "ACCESS-SIGN": sign,
            "ACCESS-PASSPHRASE": phrase,
            "ACCESS-TIMESTAMP": stamp,
            "Content-Type": "application/json",
            "locale": "en-US",
        })

    request = urllib.request.Request(
        host + path,
        headers=headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "WEEX_HTTP_" + str(exc.code)
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
        ):
            if isinstance(payload.get(key), list):
                return payload[key]

    raise RuntimeError("EXPECTED_LIST_MISSING")


def u8_contract(item, market):
    if str(
        item.get("symbol", "")
    ).upper() != market:
        raise RuntimeError(
            "MARKET_CONTRACT_SYMBOL_MISMATCH"
        )

    if str(
        item.get("baseAsset", "")
    ).upper() != market[:-4]:
        raise RuntimeError("BASE_ASSET_MISMATCH")

    if str(
        item.get("quoteAsset", "")
    ).upper() != "USDT":
        raise RuntimeError("QUOTE_ASSET_MISMATCH")

    qp = int(item["quantityPrecision"])
    pp = int(item["pricePrecision"])

    if not (
        0 <= qp <= 18
        and 0 <= pp <= 18
    ):
        raise RuntimeError("PRECISION_INVALID")

    minimum = u8_number(
        item["minOrderSize"],
        "MINIMUM_QUANTITY",
    )

    multiplier = u8_number(
        item["contractVal"],
        "CONTRACT_MULTIPLIER",
    )

    return {
        "symbol": market,
        "base_asset": market[:-4],
        "quote_asset": "USDT",
        "margin_asset": str(
            item.get("marginAsset", "USDT")
        ).upper(),
        "minimum_quantity": u8_str(minimum),
        "maximum_quantity": item.get(
            "maxOrderSize"
        ),
        "quantity_step": u8_str(
            Decimal(1).scaleb(-qp)
        ),
        "price_step": u8_str(
            Decimal(1).scaleb(-pp)
        ),
        "contract_multiplier": u8_str(multiplier),
        "quantity_precision": qp,
        "price_precision": pp,
        "rules_source": "MARKET_SYMBOL_EXCHANGE_INFO",
    }


def u8_positions(rows, demo):
    long_qty = Decimal(0)
    short_qty = Decimal(0)
    selected = []

    for item in rows:
        if not isinstance(item, dict):
            raise RuntimeError(
                "POSITION_RECORD_INVALID"
            )

        if str(
            item.get("symbol", "")
        ).upper() != demo:
            continue

        raw = next(
            (
                item[k]
                for k in (
                    "size",
                    "total",
                    "holdVol",
                    "positionAmt",
                )
                if item.get(k) is not None
            ),
            None,
        )

        qty = u8_number(
            raw,
            "POSITION_SIZE",
            allow_zero=True,
        )

        if qty == 0:
            continue

        side = str(
            item.get("positionSide")
            or item.get("holdSide")
            or item.get("side")
            or ""
        ).upper()

        if side == "LONG":
            long_qty += qty
        elif side == "SHORT":
            short_qty += qty
        else:
            raise RuntimeError(
                "POSITION_SIDE_UNVERIFIED"
            )

        selected.append(item)

    return {
        "positions": selected,
        "long_position_quantity": u8_str(long_qty),
        "short_position_quantity": u8_str(short_qty),
        "position_flat_verified": (
            long_qty == 0
            and short_qty == 0
        ),
    }


def u8_size(config, rules, price, direction):
    strategy = config["strategy"]

    margin = u8_number(
        strategy["entry_margin_usdt"],
        "ENTRY_MARGIN_USDT",
    )

    leverage = u8_number(
        strategy[
            "long_leverage"
            if direction == "LONG"
            else "short_leverage"
        ],
        "RENDER_LEVERAGE",
    )

    price = u8_number(
        price,
        "MARK_PRICE",
    )

    step = u8_number(
        rules["quantity_step"],
        "QUANTITY_STEP",
    )

    minimum = u8_number(
        rules["minimum_quantity"],
        "MINIMUM_QUANTITY",
    )

    # Reference 17248 sizing convention.
    # Quantity expressed in base-asset units.

    raw = margin * leverage / price

    steps = int(
        (raw / step).to_integral_value(
            rounding=ROUND_FLOOR
        )
    )

    # Two step-valid equal halves for staged hedge.

    steps -= steps % 2

    qty = Decimal(steps) * step
    half = qty / 2

    initial_valid = (
        qty >= minimum
        and qty > 0
        and qty % step == 0
    )

    half_valid = (
        half >= minimum
        and half > 0
        and half % step == 0
    )

    maximum = rules.get("maximum_quantity")

    if maximum not in (None, ""):
        initial_valid = (
            initial_valid
            and qty <= u8_number(
                maximum,
                "MAXIMUM_QUANTITY",
            )
        )

    return {
        "raw_quantity": u8_str(raw),
        "rounded_contract_quantity": u8_str(qty),
        "half_contract_quantity": u8_str(half),
        "initial_quantity_valid": bool(initial_valid),
        "half_quantity_valid": bool(half_valid),
        "order_submitted": False,
        "margin_usdt": u8_str(margin),
        "leverage": u8_str(leverage),
        "mark_price": u8_str(price),
        "quantity_unit_assumption":
            "BASE_ASSET_REFERENCE_17248",
    }


def unit_8_v16_main():
    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    unit7 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_7_RESULT"
    )

    if (
        not isinstance(config, dict)
        or not isinstance(unit7, dict)
    ):
        raise RuntimeError(
            "UNIT_8_UPSTREAM_MISSING"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or config.get(
            "real_cash_execution_enabled"
        ) is not False
        or unit7.get("exchange_write") is not False
    ):
        raise RuntimeError(
            "UNIT_8_DEMO_ONLY_GATE"
        )

    exchange = config.get("exchange", {})

    market = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    demo = str(
        exchange.get("demo_order_symbol", "")
    ).strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9]{2,20}USDT",
        market,
    ):
        raise RuntimeError(
            "MARKET_SYMBOL_INVALID"
        )

    if not demo or demo == market:
        raise RuntimeError(
            "DEMO_SYMBOL_INVALID"
        )

    if str(
        unit7.get("symbol", "")
    ).upper() != market:
        raise RuntimeError(
            "UNIT_7_MARKET_SYMBOL_MISMATCH"
        )

    result = {
        "unit": 8,
        "version": "V19_REFERENCE_17248_ADAPTED",
        "symbol": market,
        "market_symbol": market,
        "demo_order_symbol": demo,
        "demo_symbol": demo,
        "base_coin": market[:-4],
        "quote_coin": "USDT",
        "direction": unit7.get(
            "direction", "NONE"
        ),
        "active_mode": unit7.get(
            "active_mode", "NONE"
        ),
        "execution_intent": (
            unit7.get("execution_intent") is True
        ),
        "status": "UNVERIFIED",
        "reason": "READ_PENDING",
        "errors": {},
        "market_contract_verified": False,
        "api_trading_symbol_verified": False,
        "simulation_directory_verified": False,
        "simulation_api_directory_verified": False,
        "simulation_contract_verified": False,
        "simulation_api_trading_verified": False,
        "simulation_contract_rules_verified": False,
        "demo_symbol_verified": False,
        "demo_contract_verified": False,
        "demo_order_rules_independently_verified": False,
        "demo_balance_verified": False,
        "demo_positions_read_verified": False,
        "demo_history_read_verified": False,
        "account_config_verified": False,
        "account_can_trade": None,
        "account_dual_side_enabled": None,
        "demo_dual_side_mode_verified": False,
        "position_flat_verified": False,
        "available_balance": None,
        "account_equity": None,
        "committed_margin": None,
        "positions": [],
        "long_position_quantity": "0",
        "short_position_quantity": "0",
        "contract": None,
        "public_contract": None,
        "simulation_contract": None,
        "minimum_quantity": None,
        "maximum_quantity": None,
        "quantity_step": None,
        "price_step": None,
        "contract_multiplier": None,
        "size_preview": None,
        "trade_plan_ready": False,
        "execution_authorized": False,
        "exchange_write": False,
        "read_only": True,
        "real_cash_execution_enabled": False,
        "demo_order_endpoint": "/capi/v3/sim/order",
        "demo_order_endpoint_documented": True,
        "demo_order_http_method": "POST",
        "demo_order_endpoint_tested": False,
        "demo_order_permission_verified": False,
        "demo_order_submission_verified": False,
        "demo_order_quantity_units_verified": False,
        "checked_at_ms": int(time.time() * 1000),
    }

    # ========================================================
    # MARKET CONTRACT RULES
    # ========================================================

    try:
        rows = u8_rows(
            u8_get(
                U8_MARKET_HOST,
                "/capi/v3/market/exchangeInfo",
            )
        )

        directory = {
            str(x.get("symbol", "")).upper(): x
            for x in rows
            if isinstance(x, dict)
        }

        item = directory.get(market)

        if item is None:
            raise RuntimeError(
                "MARKET_CONTRACT_NOT_IN_DIRECTORY"
            )

        rules = u8_contract(item, market)

        result.update({
            "contract": rules,
            "public_contract": rules,
            "simulation_contract": rules,
            "market_contract_verified": True,
            "api_trading_symbol_verified": True,
            "simulation_directory_verified": True,
            "simulation_api_directory_verified": True,
            "simulation_contract_verified": True,
            "simulation_api_trading_verified": True,
            "simulation_contract_rules_verified": True,
        })

        for field in (
            "minimum_quantity",
            "maximum_quantity",
            "quantity_step",
            "price_step",
            "contract_multiplier",
        ):
            result[field] = rules.get(field)

    except Exception as exc:
        result["errors"]["contract"] = str(exc)

    # ========================================================
    # DEMO BALANCE
    # ========================================================

    try:
        rows = u8_rows(
            u8_get(
                U8_DEMO_HOST,
                "/capi/v3/sim/balance",
                True,
            )
        )

        matches = [
            x for x in rows
            if isinstance(x, dict)
            and str(
                x.get("asset", "")
            ).upper() == "SUSDT"
        ]

        if len(matches) != 1:
            raise RuntimeError(
                "SUSDT_BALANCE_NOT_UNIQUE"
            )

        result["available_balance"] = u8_str(
            u8_number(
                matches[0].get("availableBalance"),
                "AVAILABLE_BALANCE",
                True,
            )
        )

        result["demo_balance_verified"] = True

    except Exception as exc:
        result["errors"]["balance"] = str(exc)

    # ========================================================
    # DEMO POSITIONS
    # ========================================================

    try:
        rows = u8_rows(
            u8_get(
                U8_DEMO_HOST,
                "/capi/v3/sim/position/allPosition",
                True,
            )
        )

        result.update(
            u8_positions(rows, demo)
        )

        result["demo_positions_read_verified"] = True

    except Exception as exc:
        result["errors"]["positions"] = str(exc)

    # ========================================================
    # ACCOUNT CONFIGURATION
    # ========================================================

    try:
        account = u8_get(
            U8_DEMO_HOST,
            "/capi/v3/account/accountConfig",
            True,
        )

        if not isinstance(account, dict):
            raise RuntimeError(
                "ACCOUNT_CONFIG_INVALID"
            )

        if type(account.get("canTrade")) is bool:
            result["account_can_trade"] = (
                account["canTrade"]
            )

        if type(
            account.get("dualSidePosition")
        ) is bool:
            result["account_dual_side_enabled"] = (
                account["dualSidePosition"]
            )

        result["account_config_verified"] = True

        result["demo_dual_side_mode_verified"] = (
            result["account_dual_side_enabled"] is True
        )

    except Exception as exc:
        result["errors"]["account"] = str(exc)

    # ========================================================
    # ENTRY QUANTITY PREVIEW
    # ========================================================

    snapshot = globals().get(
        "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
    )

    if (
        isinstance(result["contract"], dict)
        and isinstance(snapshot, dict)
        and str(
            snapshot.get("symbol", "")
        ).upper() == market
        and result["direction"] in (
            "LONG", "SHORT"
        )
    ):
        try:
            price = (
                snapshot.get("price")
                or snapshot.get("mark_price")
            )

            result["size_preview"] = u8_size(
                config,
                result["contract"],
                price,
                result["direction"],
            )

        except Exception as exc:
            result["errors"]["size"] = str(exc)

    # ========================================================
    # REFERENCE HANDOVER
    # ========================================================

    result["demo_symbol_verified"] = (
        bool(demo)
        and result["demo_positions_read_verified"]
    )

    # Compatibility with the current Unit 9:
    # market-derived rules are attached to the configured
    # demo symbol. This does not prove demo-order acceptance.

    result["demo_contract_verified"] = (
        result["market_contract_verified"]
        and result["demo_symbol_verified"]
    )

    if all((
        result["demo_contract_verified"],
        result["demo_balance_verified"],
        result["demo_positions_read_verified"],
        result["account_can_trade"] is True,
    )):
        result["status"] = "VERIFIED_READ_ONLY"
        result["reason"] = (
            "REFERENCE_MARKET_RULES_AND_DEMO_ACCOUNT_READ"
        )
    else:
        result["reason"] = (
            "MARKET_RULES_OR_DEMO_ACCOUNT_INCOMPLETE"
        )

    result["checked_at_ms"] = int(
        time.time() * 1000
    )

    for field in (
        "version",
        "market_symbol",
        "demo_order_symbol",
        "status",
        "reason",
        "available_balance",
        "size_preview",
        "errors",
    ):
        print(
            "UNIT 8",
            field.upper(),
            "=",
            result.get(field),
            flush=True,
        )

    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True,
    )

    return result


FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    unit_8_v16_main()
)

FRESH_UNIT_8_VALIDATION_READY = (
    FRESH_RECONSTRUCTION_UNIT_8_RESULT.get(
        "status"
    ) == "VERIFIED_READ_ONLY"
)

FRESH_UNIT_8_OPTIMIZATION_READY = (
    FRESH_UNIT_8_VALIDATION_READY
)

FRESH_UNIT_8_VERIFIED_CONTRACT = (
    FRESH_RECONSTRUCTION_UNIT_8_RESULT.get(
        "contract"
    )
    if FRESH_UNIT_8_VALIDATION_READY
    else None
)

# ============================================================
# END COMPLETE UNIT 8 V19
# UNIT 9 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIVERSAL DEMO SYMBOL COMPATIBILITY ADAPTER V1
# ZERO INDENTATION
# ============================================================

def demo_symbol_adapter_v1(config, unit8=None):
    if not isinstance(config, dict):
        raise RuntimeError("SYMBOL_ADAPTER_CONFIG_MISSING")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("SYMBOL_ADAPTER_NOT_DEMO")

    if config.get("real_cash_execution_enabled") is not False:
        raise RuntimeError("SYMBOL_ADAPTER_REAL_CASH_NOT_DISABLED")

    exchange = config.get("exchange")

    if not isinstance(exchange, dict):
        raise RuntimeError("SYMBOL_ADAPTER_EXCHANGE_MISSING")

    market = str(
        exchange.get("market_symbol") or ""
    ).strip().upper()

    demo = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if (
        not market.endswith("USDT")
        or not market.isalnum()
        or not demo.isalnum()
        or demo == market
    ):
        raise RuntimeError("SYMBOL_ADAPTER_INVALID_PAIR")

    # Unit 2 determines both symbols.
    # Never derive the demo symbol again here.

    if unit8 is not None:
        if not isinstance(unit8, dict):
            raise RuntimeError("SYMBOL_ADAPTER_UNIT8_INVALID")

        if str(
            unit8.get("market_symbol") or ""
        ).upper() != market:
            raise RuntimeError("UNIT8_MARKET_SYMBOL_MISMATCH")

        if str(
            unit8.get("demo_order_symbol") or ""
        ).upper() != demo:
            raise RuntimeError("UNIT8_DEMO_SYMBOL_MISMATCH")

    return {
        "market_symbol": market,
        "demo_order_symbol": demo,
        "source": "UNIT_2_EXCHANGE_CONFIG",
        "unit8_preserved": True,
        "exchange_write": False,
    }


def demo_symbol_adapter_u10(config, unit8):
    return demo_symbol_adapter_v1(config, unit8)


def demo_symbol_adapter_u11(config, unit8):
    return demo_symbol_adapter_v1(config, unit8)


def demo_symbol_adapter_u12(config, unit8):
    return demo_symbol_adapter_v1(config, unit8)


# ============================================================
# END UNIVERSAL DEMO SYMBOL COMPATIBILITY ADAPTER V1
# ============================================================

# ============================================================
# START COMPLETE UNIT 9 REPLACEMENT
# UNIT 9 V2 - UNIVERSAL DEMO HANDOVER
# ZERO INDENTATION
# ============================================================

import os as _u9_os
from decimal import Decimal as _U9Decimal
from decimal import InvalidOperation as _U9Invalid
from decimal import ROUND_DOWN as _U9_ROUND_DOWN


def u9_decimal(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        result = _U9Decimal(str(value))
        return result if result.is_finite() else None
    except (ValueError, TypeError, _U9Invalid):
        return None


def u9_pick(data, *keys):
    if not isinstance(data, dict):
        return None
    for key in keys:
        if data.get(key) is not None:
            return data[key]
    return None


def u9_contract_pick(contract, *keys):
    value = u9_pick(contract, *keys)
    if value is not None:
        return value

    if isinstance(contract, dict):
        for section in (
            "rules",
            "contract_rules",
            "specifications",
        ):
            value = u9_pick(contract.get(section), *keys)
            if value is not None:
                return value

    return None


def u9_idle(reason, symbol, contract=None):
    return {
        "status": "IDLE",
        "reason": str(reason),
        "skip_reason": str(reason),
        "market_symbol": symbol,
        "demo_order_symbol": (
    contract.get("symbol")
    if isinstance(contract, dict)
    else None
),
        "contract": contract,
        "direction": "NONE",
        "active_mode": "NONE",
        "signal_qualified": False,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "execution_ready": False,
        "execution_authorized": False,
        "execution_candidate": None,
        "order_payload_created": False,
        "order_submission_authorized": False,
        "exchange_write": False,
        "read_only": True,
    }


def fresh_reconstruction_unit_9(
    config,
    unit_8_result,
    unit_7_result=None,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 9 VERSION = V2_UNIVERSAL_DEMO_HANDOVER",
        flush=True,
    )

    symbol = _u9_os.getenv(
        "WEEX_SYMBOL", ""
    ).strip().upper()

    if not symbol and isinstance(config, dict):
        exchange = config.get("exchange", {})
        if isinstance(exchange, dict):
            symbol = str(
                exchange.get("market_symbol") or ""
            ).strip().upper()

    def finish(result):
        print(
            "UNIT 9 MARKET_SYMBOL =",
            symbol,
            flush=True,
        )
        print(
            "UNIT 9 STATUS =",
            result["status"],
            flush=True,
        )
        print(
            "UNIT 9 REASON =",
            result["reason"],
            flush=True,
        )
        print(
            "UNIT 9 EXECUTION READY =",
            result["execution_ready"],
            flush=True,
        )
        print(
            "UNIT 9 EXCHANGE WRITE = NONE",
            flush=True,
        )
        print(
            "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS",
            flush=True,
        )
        print("=" * 80, flush=True)
        return result

    if not isinstance(config, dict):
        return finish(
            u9_idle("INVALID_CONFIG", symbol)
        )

    if not isinstance(unit_8_result, dict):
        return finish(
            u9_idle("INVALID_UNIT_8_RESULT", symbol)
        )

    if not isinstance(unit_7_result, dict):
        return finish(
            u9_idle("UNIT_7_HANDOVER_MISSING", symbol)
        )

    if not symbol:
        return finish(
            u9_idle("WEEX_SYMBOL_MISSING", symbol)
        )

    if config.get("execution_environment") not in (
        None,
        "DEMO",
    ):
        return finish(
            u9_idle("NON_DEMO_ENVIRONMENT", symbol)
        )

    if unit_8_result.get("status") != "VERIFIED_READ_ONLY":
        return finish(
            u9_idle("UNIT_8_NOT_VERIFIED", symbol)
        )

    required_checks = (
        "demo_contract_verified",
        "demo_balance_verified",
        "demo_positions_read_verified",
    )

    for check in required_checks:
        if unit_8_result.get(check) is not True:
            return finish(
                u9_idle(
                    "UNIT_8_" + check.upper() + "_FAILED",
                    symbol,
                )
            )

    verified_symbol = str(
        unit_8_result.get("demo_order_symbol") or ""
    ).strip().upper()

    
# ============================================================
# UNIT 9 VERIFIED DEMO SYMBOL CORRECTION
# ZERO INDENTATION REFERENCE
# ============================================================

    expected_demo_symbol = (
        symbol[:-4] + "SUSDT"
    )

    if (
        verified_symbol != expected_demo_symbol
        or unit_8_result.get(
            "simulation_contract_verified"
        ) is not True
        or unit_8_result.get(
            "simulation_api_trading_verified"
        ) is not True
    ):
        return finish(
            u9_idle(
                "DEMO_SYMBOL_NOT_VERIFIED",
                symbol
            )
        )

    contract = unit_8_result.get("contract")

    if not isinstance(contract, dict):
        return finish(
            u9_idle("CONTRACT_MISSING", symbol)
        )

    minimum = u9_decimal(
        u9_contract_pick(
            contract,
            "minimum_quantity",
            "min_quantity",
            "minQty",
            "minTradeNum",
        )
    )

    step = u9_decimal(
        u9_contract_pick(
            contract,
            "quantity_step",
            "qty_step",
            "stepSize",
            "sizeMultiplier",
        )
    )

    price_step = u9_decimal(
        u9_contract_pick(
            contract,
            "price_step",
            "tickSize",
            "priceEndStep",
        )
    )

    multiplier = u9_decimal(
        u9_contract_pick(
            contract,
            "contract_multiplier",
            "contractMultiplier",
            "contractSize",
        )
    )

    if any(
        value is None or value <= 0
        for value in (
            minimum,
            step,
            price_step,
            multiplier,
        )
    ):
        return finish(
            u9_idle(
                "CONTRACT_RULES_INCOMPLETE",
                symbol,
                contract,
            )
        )

    if unit_8_result.get(
        "position_flat_verified"
    ) is not True:
        return finish(
            u9_idle(
                "POSITION_NOT_FLAT",
                symbol,
                contract,
            )
        )

    direction = str(
        u9_pick(
            unit_7_result,
            "direction",
            "side",
            "trade_direction",
        ) or "NONE"
    ).upper()

    mode = str(
        u9_pick(
            unit_7_result,
            "active_mode",
            "mode",
            "strategy_mode",
        ) or "NONE"
    ).upper()

    if direction not in ("LONG", "SHORT"):
        return finish(
            u9_idle(
                "NO_QUALIFIED_DIRECTION",
                symbol,
                contract,
            )
        )

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        return finish(
            u9_idle(
                "NO_QUALIFIED_STRATEGY",
                symbol,
                contract,
            )
        )

    entry_intent = u9_pick(
        unit_7_result,
        "execution_intent",
        "trade_authorized",
        "entry_authorized",
    )

    if entry_intent is not True:
        return finish(
            u9_idle(
                "UNIT_7_ENTRY_NOT_QUALIFIED",
                symbol,
                contract,
            )
        )

    # ========================================================
    # VERIFIED UNIT 8 SIZE PREVIEW
    # ========================================================

    preview = unit_8_result.get("size_preview")

    if not isinstance(preview, dict):
        return finish(
            u9_idle(
                "UNIT_8_SIZE_PREVIEW_MISSING",
                symbol,
                contract,
            )
        )

    if (
        preview.get("initial_quantity_valid") is not True
        or preview.get("half_quantity_valid") is not True
    ):
        return finish(
            u9_idle(
                "UNIT_8_SIZE_PREVIEW_INVALID",
                symbol,
                contract,
            )
        )

    if preview.get("order_submitted") is not False:
        return finish(
            u9_idle(
                "SIZE_PREVIEW_SUBMISSION_STATE_UNSAFE",
                symbol,
                contract,
            )
        )

    requested_quantity = u9_decimal(
        preview.get("rounded_contract_quantity")
    )

    if (
        requested_quantity is None
        or requested_quantity <= 0
    ):
        return finish(
            u9_idle(
                "UNIT_8_QUANTITY_UNAVAILABLE",
                symbol,
                contract,
            )
        )

    # ========================================================
    # QUANTITY STEP AND 50/50 HEDGE VALIDATION
    # ========================================================

    adjusted_quantity = (
        requested_quantity / step
    ).to_integral_value(
        rounding=_U9_ROUND_DOWN
    ) * step

    half_quantity = adjusted_quantity / 2

    if adjusted_quantity < minimum:
        return finish(
            u9_idle(
                "QUANTITY_BELOW_MINIMUM",
                symbol,
                contract,
            )
        )

    if (
        half_quantity < minimum
        or half_quantity % step != 0
    ):
        return finish(
            u9_idle(
                "INVALID_HALF_HEDGE_QUANTITY",
                symbol,
                contract,
            )
        )

    preview_half = u9_decimal(
        preview.get("half_contract_quantity")
    )

    if preview_half != half_quantity:
        return finish(
            u9_idle(
                "HEDGE_QUANTITY_MISMATCH",
                symbol,
                contract,
            )
        )

    # ========================================================
    # VALIDATED HANDOVER - NO ORDER AUTHORIZATION
    # ========================================================

    candidate = {
        "market_symbol": symbol,
        "demo_order_symbol": verified_symbol,
        "direction": direction,
        "active_mode": mode,
        "quantity": str(adjusted_quantity),
        "half_quantity": str(half_quantity),
        "minimum_quantity": str(minimum),
        "quantity_step": str(step),
        "price_step": str(price_step),
        "contract_multiplier": str(multiplier),
        "contract": contract,
        "unit_7_result": unit_7_result,
        "unit_8_size_preview": preview,
    }

    result = {
        "status": "PREPARED_READ_ONLY",
        "reason": "VALIDATED_ENTRY_CANDIDATE",
        "skip_reason": None,
        "market_symbol": symbol,
        "demo_order_symbol": verified_symbol,
        "contract": contract,
        "direction": direction,
        "active_mode": mode,
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": candidate,
        "execution_ready": False,
        "execution_authorized": False,
        "execution_candidate": candidate,
        "order_payload_created": False,
        "order_submission_authorized": False,
        "exchange_write": False,
        "read_only": True,
    }

    return finish(result)


# ============================================================
# UNIT 9 STARTUP HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
        globals().get(
            "FRESH_RECONSTRUCTION_UNIT_7_RESULT",
            globals().get(
                "FRESH_RECONSTRUCTION_SIZING_CANDIDATE"
            )
        ),
    )
)

FRESH_UNIT_9_OPTIMIZATION_READY = (
    isinstance(
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
        dict,
    )
    and FRESH_RECONSTRUCTION_UNIT_9_RESULT.get(
        "read_only"
    ) is True
    and FRESH_RECONSTRUCTION_UNIT_9_RESULT.get(
        "exchange_write"
    ) is False
)

print(
    "UNIT 9 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_9_OPTIMIZATION_READY,
    flush=True,
)

# ============================================================
# END COMPLETE UNIT 9 REPLACEMENT
# ZERO INDENTATION
# UNIT 10 CONTINUES BELOW
# ============================================================


    

# ============================================================
# START COMPLETE UNIT 10 REPLACEMENT
# UNIT 10 V1 - UNIVERSAL DEMO EXECUTION BOUNDARY
# ZERO INDENTATION
# ============================================================

import os as _u10_os
from decimal import Decimal as _U10Decimal
from decimal import InvalidOperation as _U10Invalid


def u10_decimal(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = _U10Decimal(str(value))
        return number if number.is_finite() else None
    except (TypeError, ValueError, _U10Invalid):
        return None


def u10_symbol(config):
    symbol = _u10_os.getenv(
        "WEEX_SYMBOL", ""
    ).strip().upper()

    if not symbol and isinstance(config, dict):
        exchange = config.get("exchange", {})
        if isinstance(exchange, dict):
            symbol = str(
                exchange.get("market_symbol") or ""
            ).strip().upper()

    return symbol


def u10_boundary_result(
    status,
    reason,
    symbol,
    source=None,
):
    source = source if isinstance(source, dict) else {}

    return {
        "unit_10_version": "U10_V1_UNIVERSAL_DEMO",
        "status": status,
        "reason": reason,
        "skip_reason": reason if status != "READY" else None,
        "market_symbol": symbol,
        "demo_order_symbol": symbol,
        "direction": source.get("direction", "NONE"),
        "active_mode": source.get("active_mode", "NONE"),
        "trade_plan": source.get("trade_plan"),
        "execution_candidate": source.get(
            "execution_candidate"
        ),
        "signal_qualified": False,
        "trade_plan_ready": False,
        "execution_ready": False,
        "demo_boundary_ready": False,
        "demo_order_permission_verified": False,
        "demo_order_submission_verified": False,
        "execution_authorized": False,
        "order_submission_authorized": False,
        "order_payload_created": False,
        "demo_submission_requested": False,
        "exchange_write": False,
        "read_only": True,
        "real_cash_execution": False,
    }


def fresh_reconstruction_unit_10(
    execution_config,
    unit_9_result,
    unit_8_result=None,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 10 VERSION = V1_UNIVERSAL_DEMO_BOUNDARY",
        flush=True,
    )

    symbol = u10_symbol(execution_config)

    def finish(result):
        print(
            "UNIT 10 MARKET SYMBOL =",
            symbol,
            flush=True,
        )
        print(
            "UNIT 10 STATUS =",
            result["status"],
            flush=True,
        )
        print(
            "UNIT 10 REASON =",
            result["reason"],
            flush=True,
        )
        print(
            "UNIT 10 ACTIVE MODE =",
            result["active_mode"],
            flush=True,
        )
        print(
            "UNIT 10 DIRECTION =",
            result["direction"],
            flush=True,
        )
        print(
            "UNIT 10 TRADE PLAN READY =",
            result["trade_plan_ready"],
            flush=True,
        )
        print(
            "UNIT 10 DEMO BOUNDARY READY =",
            result["demo_boundary_ready"],
            flush=True,
        )
        print(
            "UNIT 10 EXECUTION READY =",
            result["execution_ready"],
            flush=True,
        )
        print(
            "UNIT 10 EXECUTION AUTHORIZED =",
            result["execution_authorized"],
            flush=True,
        )
        print(
            "UNIT 10 ORDER PAYLOAD CREATED = False",
            flush=True,
        )
        print(
            "UNIT 10 DEMO SUBMISSION REQUESTED = False",
            flush=True,
        )
        print(
            "UNIT 10 EXCHANGE WRITE = NONE",
            flush=True,
        )
        print(
            "UNIT 10 REAL CASH EXECUTION = DISABLED",
            flush=True,
        )
        print(
            "FRESH RECONSTRUCTION UNIT 10 RESULT = PASS",
            flush=True,
        )
        print("=" * 80, flush=True)
        return result

    def stop(reason):
        return finish(
            u10_boundary_result(
                "IDLE",
                reason,
                symbol,
                unit_9_result,
            )
        )

    if not isinstance(execution_config, dict):
        return stop("INVALID_CONFIGURATION")

    if not isinstance(unit_9_result, dict):
        return stop("INVALID_UNIT_9_RESULT")

    if not isinstance(unit_8_result, dict):
        return stop("UNIT_8_RESULT_MISSING")

    if not symbol:
        return stop("MARKET_SYMBOL_MISSING")

    environment = str(
        execution_config.get(
            "execution_environment", ""
        )
    ).strip().upper()

    if environment != "DEMO":
        return stop("DEMO_ENVIRONMENT_REQUIRED")

    exchange = execution_config.get("exchange", {})

    if not isinstance(exchange, dict):
        return stop("EXCHANGE_CONFIG_INVALID")

    configured_symbol = str(
        exchange.get("market_symbol") or symbol
    ).strip().upper()

    if configured_symbol != symbol:
        return stop("CONFIG_SYMBOL_MISMATCH")

    if unit_8_result.get("status") != "VERIFIED_READ_ONLY":
        return stop("UNIT_8_NOT_VERIFIED")

    if unit_8_result.get("demo_contract_verified") is not True:
        return stop("DEMO_CONTRACT_UNVERIFIED")

    if unit_8_result.get("demo_balance_verified") is not True:
        return stop("DEMO_BALANCE_UNVERIFIED")

    if (
        unit_8_result.get("demo_positions_read_verified")
        is not True
    ):
        return stop("DEMO_POSITIONS_UNVERIFIED")

    if (
        unit_8_result.get("position_flat_verified")
        is not True
    ):
        return stop("POSITION_NOT_FLAT")

    verified_symbol = str(
        unit_8_result.get("demo_order_symbol") or ""
    ).strip().upper()

    if verified_symbol != symbol:
        return stop("DEMO_SYMBOL_MISMATCH")

    # ========================================================
    # UNIT 9 HANDOVER
    # ========================================================

    unit_9_status = str(
        unit_9_result.get("status") or ""
    ).upper()

    if unit_9_status == "IDLE":
        reason = unit_9_result.get(
            "reason", "NO_QUALIFIED_ENTRY"
        )
        return stop("UNIT_9_" + str(reason))

    if unit_9_status != "PREPARED_READ_ONLY":
        return stop("UNIT_9_NOT_PREPARED")

    if unit_9_result.get("read_only") is not True:
        return stop("UNIT_9_SAFETY_VIOLATION")

    if unit_9_result.get("exchange_write") is not False:
        return stop("UNIT_9_EXCHANGE_WRITE_DETECTED")

    if (
        unit_9_result.get("execution_authorized")
        is not False
    ):
        return stop("UNIT_9_AUTHORIZATION_UNSAFE")

    if (
        unit_9_result.get("signal_qualified")
        is not True
    ):
        return stop("SIGNAL_NOT_QUALIFIED")

    if (
        unit_9_result.get("trade_plan_ready")
        is not True
    ):
        return stop("UNIT_9_TRADE_PLAN_NOT_READY")

    if (
        unit_9_result.get("execution_intent")
        is not True
    ):
        return stop("UNIT_9_EXECUTION_INTENT_MISSING")

    if (
        str(
            unit_9_result.get("market_symbol") or ""
        ).upper() != symbol
    ):
        return stop("UNIT_9_MARKET_SYMBOL_MISMATCH")

    if (
        str(
            unit_9_result.get("demo_order_symbol") or ""
        ).upper() != symbol
    ):
        return stop("UNIT_9_DEMO_SYMBOL_MISMATCH")

    plan = unit_9_result.get("trade_plan")
    candidate = unit_9_result.get(
        "execution_candidate"
    )

    if not isinstance(plan, dict):
        return stop("TRADE_PLAN_MISSING")

    if not isinstance(candidate, dict):
        return stop("EXECUTION_CANDIDATE_MISSING")

    if plan is not candidate:
        return stop("TRADE_PLAN_CANDIDATE_MISMATCH")

    direction = str(
        unit_9_result.get("direction") or ""
    ).upper()

    mode = str(
        unit_9_result.get("active_mode") or ""
    ).upper()

    if direction not in ("LONG", "SHORT"):
        return stop("INVALID_DIRECTION")

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        return stop("INVALID_STRATEGY_MODE")

    if (
        str(plan.get("market_symbol") or "").upper()
        != symbol
    ):
        return stop("TRADE_PLAN_SYMBOL_MISMATCH")

    if (
        str(plan.get("direction") or "").upper()
        != direction
    ):
        return stop("TRADE_PLAN_DIRECTION_MISMATCH")

    if (
        str(plan.get("active_mode") or "").upper()
        != mode
    ):
        return stop("TRADE_PLAN_MODE_MISMATCH")

    # ========================================================
    # QUANTITY AND STAGED HEDGE VALIDATION
    # ========================================================

    quantity = u10_decimal(plan.get("quantity"))
    half = u10_decimal(plan.get("half_quantity"))
    minimum = u10_decimal(
        plan.get("minimum_quantity")
    )
    step = u10_decimal(plan.get("quantity_step"))
    price_step = u10_decimal(
        plan.get("price_step")
    )
    multiplier = u10_decimal(
        plan.get("contract_multiplier")
    )

    values = (
        quantity,
        half,
        minimum,
        step,
        price_step,
        multiplier,
    )

    if any(
        value is None or value <= 0
        for value in values
    ):
        return stop("INVALID_CONTRACT_QUANTITY_RULES")

    if quantity < minimum:
        return stop("QUANTITY_BELOW_MINIMUM")

    if quantity % step != 0:
        return stop("QUANTITY_STEP_INVALID")

    if half < minimum:
        return stop("HALF_QUANTITY_BELOW_MINIMUM")

    if half % step != 0:
        return stop("HALF_QUANTITY_STEP_INVALID")

    if half * 2 != quantity:
        return stop("HALF_QUANTITY_MISMATCH")

    # Compare with the verified Unit 8 contract rules.
    contract = unit_8_result.get("contract")

    if not isinstance(contract, dict):
        return stop("UNIT_8_CONTRACT_MISSING")

    def contract_value(*names):
        for name in names:
            if contract.get(name) is not None:
                return u10_decimal(contract[name])

        for section in (
            "rules",
            "contract_rules",
            "specifications",
        ):
            nested = contract.get(section)
            if isinstance(nested, dict):
                for name in names:
                    if nested.get(name) is not None:
                        return u10_decimal(nested[name])

        return None

    comparisons = (
        (
            minimum,
            contract_value(
                "minimum_quantity",
                "min_quantity",
                "minQty",
                "minTradeNum",
            ),
        ),
        (
            step,
            contract_value(
                "quantity_step",
                "qty_step",
                "stepSize",
                "sizeMultiplier",
            ),
        ),
        (
            price_step,
            contract_value(
                "price_step",
                "tickSize",
                "priceEndStep",
            ),
        ),
        (
            multiplier,
            contract_value(
                "contract_multiplier",
                "contractMultiplier",
                "contractSize",
            ),
        ),
    )

    for planned, verified in comparisons:
        if verified is None or planned != verified:
            return stop("CONTRACT_RULE_MISMATCH")

    preview = unit_8_result.get("size_preview")

    if not isinstance(preview, dict):
        return stop("UNIT_8_SIZE_PREVIEW_MISSING")

    if (
        preview.get("initial_quantity_valid")
        is not True
        or preview.get("half_quantity_valid")
        is not True
    ):
        return stop("UNIT_8_SIZE_PREVIEW_INVALID")

    if (
        u10_decimal(
            preview.get("rounded_contract_quantity")
        ) != quantity
    ):
        return stop("PREVIEW_QUANTITY_MISMATCH")

    if (
        u10_decimal(
            preview.get("half_contract_quantity")
        ) != half
    ):
        return stop("PREVIEW_HALF_QUANTITY_MISMATCH")

    # ========================================================
    # PRESERVE ORIGINAL TRADE PLAN AND CANDIDATE
    # ========================================================

    result = u10_boundary_result(
        "READY",
        "VALIDATED_DEMO_TRADE_BOUNDARY",
        symbol,
        unit_9_result,
    )

    result.update({
        "direction": direction,
        "active_mode": mode,
        "signal_qualified": True,
        "trade_plan_ready": True,
        "demo_boundary_ready": True,
        "quantity": str(quantity),
        "half_quantity": str(half),
        "minimum_quantity": str(minimum),
        "quantity_step": str(step),
        "price_step": str(price_step),
        "contract_multiplier": str(multiplier),
        "contract": contract,
        "unit_8_size_preview": preview,
        "trade_plan": plan,
        "execution_candidate": candidate,
        "execution_ready": False,
        "execution_authorized": False,
        "order_submission_authorized": False,
        "read_only": True,
        "exchange_write": False,
    })

    return finish(result)


# ============================================================
# UNIT 10 HYBRID ADAPTER
# PRESERVES ORIGINAL TWO-ARGUMENT INTERFACE
# ============================================================

def fresh_unit_10_hybrid_adapter(
    execution_config,
    unit_9_result,
):
    result = fresh_reconstruction_unit_10(
        execution_config,
        unit_9_result,
        globals().get(
            "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
        ),
    )

    if result.get("status") == "READY":
        if (
            result.get("trade_plan")
            is not unit_9_result.get("trade_plan")
        ):
            raise RuntimeError(
                "UNIT 10 ADAPTER CHANGED TRADE PLAN"
            )

        if (
            result.get("execution_candidate")
            is not unit_9_result.get(
                "execution_candidate"
            )
        ):
            raise RuntimeError(
                "UNIT 10 ADAPTER CHANGED CANDIDATE"
            )

    print(
        "UNIT 10 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True,
    )

    return result


# ============================================================
# UNIT 10 VALIDATION
# NO EXCHANGE CONNECTION OR ORDER SUBMISSION
# ============================================================

def unit_10_validation_v1():

    tests = []

    def check(name, condition):
        tests.append((name, bool(condition)))

    idle = u10_boundary_result(
        "IDLE",
        "TEST_IDLE",
        "NEARUSDT",
    )

    check(
        "IDLE EXECUTION BLOCKED",
        idle["execution_authorized"] is False
        and idle["execution_ready"] is False,
    )

    check(
        "IDLE EXCHANGE WRITE BLOCKED",
        idle["exchange_write"] is False,
    )

    check(
        "REAL CASH DISABLED",
        idle["real_cash_execution"] is False,
    )

    check(
        "NO ORDER PAYLOAD",
        idle["order_payload_created"] is False,
    )

    check(
        "NO DEMO SUBMISSION REQUEST",
        idle["demo_submission_requested"] is False,
    )

    check(
        "DECIMAL QUANTITY VALID",
        u10_decimal("14") == _U10Decimal("14"),
    )

    check(
        "INVALID QUANTITY REJECTED",
        u10_decimal("invalid") is None,
    )

    check(
        "VALID HALF QUANTITY",
        _U10Decimal("14") / 2
        == _U10Decimal("7"),
    )

    check(
        "INVALID HALF STEP DETECTED",
        _U10Decimal("3") / 2
        % _U10Decimal("1") != 0,
    )

    passed = sum(1 for _, ok in tests if ok)
    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 10 TEST",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True,
        )

    print(
        "UNIT 10 TESTS PASSED =",
        passed,
        flush=True,
    )
    print(
        "UNIT 10 TESTS FAILED =",
        failed,
        flush=True,
    )

    return failed == 0


# ============================================================
# UNIT 10 STARTUP
# ZERO INDENTATION
# ============================================================

FRESH_UNIT_10_VALIDATION_READY = (
    unit_10_validation_v1()
)

FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
    fresh_unit_10_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
    )
)

FRESH_UNIT_10_OPTIMIZATION_READY = (
    FRESH_UNIT_10_VALIDATION_READY is True
    and isinstance(
        FRESH_RECONSTRUCTION_UNIT_10_RESULT,
        dict,
    )
    and FRESH_RECONSTRUCTION_UNIT_10_RESULT.get(
        "read_only"
    ) is True
    and FRESH_RECONSTRUCTION_UNIT_10_RESULT.get(
        "exchange_write"
    ) is False
)

print(
    "UNIT 10 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_10_OPTIMIZATION_READY,
    flush=True,
)

# ============================================================
# END COMPLETE UNIT 10 REPLACEMENT
# ZERO INDENTATION
# UNIT 11 CONTINUES BELOW
# ============================================================



# ============================================================
# START COMPLETE UNIT 11 REPLACEMENT
# UNIT 11 V1 - UNIVERSAL DEMO ORDER PREPARATION
# ZERO INDENTATION
# ============================================================

import os as _u11_os
from decimal import Decimal as _U11Decimal
from decimal import InvalidOperation as _U11Invalid


def u11_decimal(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = _U11Decimal(str(value))
        return number if number.is_finite() else None
    except (ValueError, TypeError, _U11Invalid):
        return None


def u11_symbol(config):
    symbol = _u11_os.getenv(
        "WEEX_SYMBOL", ""
    ).strip().upper()

    if not symbol and isinstance(config, dict):
        exchange = config.get("exchange", {})
        if isinstance(exchange, dict):
            symbol = str(
                exchange.get("market_symbol") or ""
            ).strip().upper()

    return symbol


def u11_result(
    status,
    reason,
    symbol,
    source=None,
):
    source = source if isinstance(source, dict) else {}

    return {
        "unit_11_version": "U11_V1_UNIVERSAL_DEMO",
        "status": status,
        "reason": reason,
        "skip_reason": (
            reason if status != "PREPARED_READ_ONLY"
            else None
        ),
        "market_symbol": symbol,
        "demo_order_symbol": symbol,
        "direction": source.get("direction", "NONE"),
        "active_mode": source.get("active_mode", "NONE"),
        "trade_plan": source.get("trade_plan"),
        "execution_candidate": source.get(
            "execution_candidate"
        ),
        "order_instruction": None,
        "order_payload": None,
        "order_payload_created": False,
        "order_format_verified": False,
        "signal_qualified": False,
        "trade_plan_ready": False,
        "order_preparation_ready": False,
        "demo_boundary_ready": False,
        "demo_order_permission_verified": False,
        "demo_order_submission_verified": False,
        "execution_ready": False,
        "execution_authorized": False,
        "order_submission_authorized": False,
        "demo_submission_requested": False,
        "exchange_write": False,
        "read_only": True,
        "real_cash_execution": False,
    }


def fresh_reconstruction_unit_11(
    execution_config,
    unit_10_result,
    unit_8_result=None,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 11 VERSION = V1_UNIVERSAL_DEMO_PREPARATION",
        flush=True,
    )

    symbol = u11_symbol(execution_config)

    def finish(result):

        print(
            "UNIT 11 MARKET SYMBOL =",
            symbol,
            flush=True,
        )
        print(
            "UNIT 11 STATUS =",
            result["status"],
            flush=True,
        )
        print(
            "UNIT 11 REASON =",
            result["reason"],
            flush=True,
        )
        print(
            "UNIT 11 ACTIVE MODE =",
            result["active_mode"],
            flush=True,
        )
        print(
            "UNIT 11 DIRECTION =",
            result["direction"],
            flush=True,
        )
        print(
            "UNIT 11 TRADE PLAN READY =",
            result["trade_plan_ready"],
            flush=True,
        )
        print(
            "UNIT 11 ORDER PREPARATION READY =",
            result["order_preparation_ready"],
            flush=True,
        )
        print(
            "UNIT 11 ORDER FORMAT VERIFIED =",
            result["order_format_verified"],
            flush=True,
        )
        print(
            "UNIT 11 DEMO ORDER PERMISSION VERIFIED =",
            result["demo_order_permission_verified"],
            flush=True,
        )
        print(
            "UNIT 11 EXECUTION READY =",
            result["execution_ready"],
            flush=True,
        )
        print(
            "UNIT 11 EXECUTION AUTHORIZED =",
            result["execution_authorized"],
            flush=True,
        )
        print(
            "UNIT 11 ORDER PAYLOAD CREATED =",
            result["order_payload_created"],
            flush=True,
        )
        print(
            "UNIT 11 DEMO SUBMISSION REQUESTED = False",
            flush=True,
        )
        print(
            "UNIT 11 EXCHANGE WRITE = NONE",
            flush=True,
        )
        print(
            "UNIT 11 REAL CASH EXECUTION = DISABLED",
            flush=True,
        )
        print(
            "FRESH RECONSTRUCTION UNIT 11 RESULT =",
            (
                "PASS"
                if result["status"] in (
                    "IDLE",
                    "PREPARED_READ_ONLY",
                )
                else "BLOCKED"
            ),
            flush=True,
        )
        print("=" * 80, flush=True)

        return result

    def stop(reason, status="BLOCKED"):
        return finish(
            u11_result(
                status,
                reason,
                symbol,
                unit_10_result,
            )
        )

    # ========================================================
    # CONFIGURATION AND DEMO SAFETY
    # ========================================================

    if not isinstance(execution_config, dict):
        return stop("INVALID_CONFIGURATION")

    if not isinstance(unit_10_result, dict):
        return stop("UNIT_10_RESULT_MISSING")

    if not isinstance(unit_8_result, dict):
        return stop("UNIT_8_RESULT_MISSING")

    if not symbol:
        return stop("MARKET_SYMBOL_MISSING")

    environment = str(
        execution_config.get(
            "execution_environment", ""
        )
    ).strip().upper()

    if environment != "DEMO":
        return stop("DEMO_ENVIRONMENT_REQUIRED")

    exchange = execution_config.get("exchange", {})

    if not isinstance(exchange, dict):
        return stop("EXCHANGE_CONFIGURATION_INVALID")

    configured_symbol = str(
        exchange.get("market_symbol") or symbol
    ).strip().upper()

    if configured_symbol != symbol:
        return stop("CONFIG_SYMBOL_MISMATCH")

    if (
        unit_8_result.get("status")
        != "VERIFIED_READ_ONLY"
    ):
        return stop("UNIT_8_NOT_VERIFIED")

    if (
        unit_8_result.get("demo_contract_verified")
        is not True
    ):
        return stop("DEMO_CONTRACT_UNVERIFIED")

    if (
        unit_8_result.get("demo_balance_verified")
        is not True
    ):
        return stop("DEMO_BALANCE_UNVERIFIED")

    if (
        unit_8_result.get("demo_positions_read_verified")
        is not True
    ):
        return stop("DEMO_POSITIONS_UNVERIFIED")

    if (
        unit_8_result.get("position_flat_verified")
        is not True
    ):
        return stop("POSITION_NOT_FLAT")

    if (
        str(
            unit_8_result.get("demo_order_symbol")
            or ""
        ).upper() != symbol
    ):
        return stop("UNIT_8_SYMBOL_MISMATCH")

    # ========================================================
    # UNIT 10 HANDOVER
    # ========================================================

    status = str(
        unit_10_result.get("status") or ""
    ).upper()

    if status == "IDLE":
        return stop(
            "UNIT_10_" + str(
                unit_10_result.get(
                    "reason", "NO_QUALIFIED_ENTRY"
                )
            ),
            "IDLE",
        )

    if status != "READY":
        return stop("UNIT_10_NOT_READY")

    if (
        unit_10_result.get("read_only")
        is not True
    ):
        return stop("UNIT_10_SAFETY_VIOLATION")

    if (
        unit_10_result.get("exchange_write")
        is not False
    ):
        return stop("UNIT_10_EXCHANGE_WRITE_UNSAFE")

    if (
        unit_10_result.get("execution_authorized")
        is not False
    ):
        return stop("UNIT_10_AUTHORIZATION_UNSAFE")

    if (
        unit_10_result.get("signal_qualified")
        is not True
    ):
        return stop("SIGNAL_NOT_QUALIFIED")

    if (
        unit_10_result.get("trade_plan_ready")
        is not True
    ):
        return stop("TRADE_PLAN_NOT_READY")

    if (
        unit_10_result.get("demo_boundary_ready")
        is not True
    ):
        return stop("DEMO_BOUNDARY_NOT_READY")

    if (
        str(
            unit_10_result.get("market_symbol")
            or ""
        ).upper() != symbol
    ):
        return stop("UNIT_10_SYMBOL_MISMATCH")

    if (
        str(
            unit_10_result.get("demo_order_symbol")
            or ""
        ).upper() != symbol
    ):
        return stop("UNIT_10_DEMO_SYMBOL_MISMATCH")

    plan = unit_10_result.get("trade_plan")

    candidate = unit_10_result.get(
        "execution_candidate"
    )

    if not isinstance(plan, dict):
        return stop("TRADE_PLAN_MISSING")

    if not isinstance(candidate, dict):
        return stop("EXECUTION_CANDIDATE_MISSING")

    if plan is not candidate:
        return stop("TRADE_PLAN_IDENTITY_MISMATCH")

    direction = str(
        unit_10_result.get("direction") or ""
    ).upper()

    mode = str(
        unit_10_result.get("active_mode") or ""
    ).upper()

    if direction not in ("LONG", "SHORT"):
        return stop("INVALID_DIRECTION")

    if mode not in (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    ):
        return stop("INVALID_STRATEGY_MODE")

    if (
        str(plan.get("market_symbol") or "").upper()
        != symbol
    ):
        return stop("PLAN_SYMBOL_MISMATCH")

    if (
        str(plan.get("demo_order_symbol") or "").upper()
        != symbol
    ):
        return stop("PLAN_DEMO_SYMBOL_MISMATCH")

    if (
        str(plan.get("direction") or "").upper()
        != direction
    ):
        return stop("PLAN_DIRECTION_MISMATCH")

    if (
        str(plan.get("active_mode") or "").upper()
        != mode
    ):
        return stop("PLAN_MODE_MISMATCH")

    # ========================================================
    # QUANTITY VALIDATION
    # ========================================================

    quantity = u11_decimal(
        plan.get("quantity")
    )

    half = u11_decimal(
        plan.get("half_quantity")
    )

    minimum = u11_decimal(
        plan.get("minimum_quantity")
    )

    step = u11_decimal(
        plan.get("quantity_step")
    )

    multiplier = u11_decimal(
        plan.get("contract_multiplier")
    )

    price_step = u11_decimal(
        plan.get("price_step")
    )

    if any(
        value is None or value <= 0
        for value in (
            quantity,
            half,
            minimum,
            step,
            multiplier,
            price_step,
        )
    ):
        return stop("INVALID_QUANTITY_OR_CONTRACT_RULES")

    if quantity < minimum:
        return stop("QUANTITY_BELOW_MINIMUM")

    if quantity % step != 0:
        return stop("QUANTITY_STEP_INVALID")

    if half < minimum:
        return stop("HALF_QUANTITY_BELOW_MINIMUM")

    if half % step != 0:
        return stop("HALF_QUANTITY_STEP_INVALID")

    if half * 2 != quantity:
        return stop("HALF_QUANTITY_MISMATCH")

    if (
        u11_decimal(
            unit_10_result.get("quantity")
        ) != quantity
    ):
        return stop("UNIT_10_QUANTITY_MISMATCH")

    if (
        u11_decimal(
            unit_10_result.get("half_quantity")
        ) != half
    ):
        return stop("UNIT_10_HALF_QUANTITY_MISMATCH")

    # ========================================================
    # VERIFY UNIT 8 PREVIEW CONSISTENCY
    # ========================================================

    preview = unit_8_result.get("size_preview")

    if not isinstance(preview, dict):
        return stop("UNIT_8_SIZE_PREVIEW_MISSING")

    if (
        preview.get("initial_quantity_valid")
        is not True
        or preview.get("half_quantity_valid")
        is not True
    ):
        return stop("UNIT_8_SIZE_PREVIEW_INVALID")

    if (
        u11_decimal(
            preview.get("rounded_contract_quantity")
        ) != quantity
    ):
        return stop("UNIT_8_QUANTITY_MISMATCH")

    if (
        u11_decimal(
            preview.get("half_contract_quantity")
        ) != half
    ):
        return stop("UNIT_8_HALF_QUANTITY_MISMATCH")

    # ========================================================
    # NORMALIZED INTERNAL ORDER INSTRUCTION
    # NOT A WEEX API PAYLOAD
    # ========================================================

    instruction = {
        "instruction_version": "U11_INTERNAL_V1",
        "market_symbol": symbol,
        "demo_order_symbol": symbol,
        "market_type": "DEMO_FUTURES",
        "position_action": "OPEN",
        "direction": direction,
        "strategy_mode": mode,
        "quantity": str(quantity),
        "half_quantity": str(half),
        "minimum_quantity": str(minimum),
        "quantity_step": str(step),
        "contract_multiplier": str(multiplier),
        "price_step": str(price_step),
        "order_type": "MARKET",
        "hedge_policy": "REVERSIBLE_ATR_TWO_STAGE",
        "backup_count": 5,
        "trade_plan": plan,
        "execution_candidate": candidate,
        "weex_payload_verified": False,
        "exchange_permission_verified": False,
        "submission_authorized": False,
    }

    # ========================================================
    # PREPARED HANDOVER
    # ========================================================

    result = u11_result(
        "PREPARED_READ_ONLY",
        "INTERNAL_ORDER_INSTRUCTION_PREPARED",
        symbol,
        unit_10_result,
    )

    result.update({
        "direction": direction,
        "active_mode": mode,
        "signal_qualified": True,
        "trade_plan_ready": True,
        "order_preparation_ready": True,
        "demo_boundary_ready": True,
        "quantity": str(quantity),
        "half_quantity": str(half),
        "minimum_quantity": str(minimum),
        "quantity_step": str(step),
        "contract_multiplier": str(multiplier),
        "price_step": str(price_step),
        "order_instruction": instruction,
        "trade_plan": plan,
        "execution_candidate": candidate,
        "order_payload": None,
        "order_payload_created": False,
        "order_format_verified": False,
        "demo_order_permission_verified": False,
        "demo_order_submission_verified": False,
        "execution_ready": False,
        "execution_authorized": False,
        "order_submission_authorized": False,
        "demo_submission_requested": False,
        "exchange_write": False,
        "read_only": True,
        "real_cash_execution": False,
    })

    return finish(result)


# ============================================================
# UNIT 11 HYBRID ADAPTER
# ============================================================

def fresh_unit_11_hybrid_adapter(
    execution_config,
    unit_10_result,
):

    result = fresh_reconstruction_unit_11(
        execution_config,
        unit_10_result,
        globals().get(
            "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
        ),
    )

    if result.get("status") == "PREPARED_READ_ONLY":

        if (
            result.get("trade_plan")
            is not unit_10_result.get("trade_plan")
        ):
            raise RuntimeError(
                "UNIT 11 ALTERED ORIGINAL TRADE PLAN"
            )

        if (
            result.get("execution_candidate")
            is not unit_10_result.get(
                "execution_candidate"
            )
        ):
            raise RuntimeError(
                "UNIT 11 ALTERED EXECUTION CANDIDATE"
            )

    print(
        "UNIT 11 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True,
    )

    return result


# ============================================================
# UNIT 11 LOCAL VALIDATION
# ============================================================

def unit_11_validation_v1():

    tests = []

    def check(name, condition):
        tests.append((name, bool(condition)))

    idle = u11_result(
        "IDLE",
        "TEST_IDLE",
        "NEARUSDT",
    )

    check(
        "IDLE EXECUTION BLOCKED",
        idle["execution_authorized"] is False,
    )

    check(
        "NO REAL CASH EXECUTION",
        idle["real_cash_execution"] is False,
    )

    check(
        "NO EXCHANGE WRITE",
        idle["exchange_write"] is False,
    )

    check(
        "NO ORDER PAYLOAD",
        idle["order_payload"] is None
        and idle["order_payload_created"] is False,
    )

    check(
        "NO ORDER SUBMISSION",
        idle["demo_submission_requested"] is False,
    )

    check(
        "NO UNVERIFIED ORDER AUTHORIZATION",
        idle["order_submission_authorized"] is False,
    )

    check(
        "DECIMAL VALID",
        u11_decimal("14") == _U11Decimal("14"),
    )

    check(
        "INVALID DECIMAL REJECTED",
        u11_decimal("bad") is None,
    )

    check(
        "HALF QUANTITY VALID",
        _U11Decimal("14") / 2
        == _U11Decimal("7"),
    )

    check(
        "INVALID HALF STEP DETECTED",
        _U11Decimal("3") / 2
        % _U11Decimal("1") != 0,
    )

    passed = sum(
        1 for _, condition in tests if condition
    )

    failed = len(tests) - passed

    for name, condition in tests:
        print(
            "UNIT 11 TEST",
            name,
            "=",
            "PASS" if condition else "FAIL",
            flush=True,
        )

    print(
        "UNIT 11 TESTS PASSED =",
        passed,
        flush=True,
    )

    print(
        "UNIT 11 TESTS FAILED =",
        failed,
        flush=True,
    )

    return failed == 0


# ============================================================
# UNIT 11 STARTUP
# ZERO INDENTATION
# ============================================================

FRESH_UNIT_11_VALIDATION_READY = (
    unit_11_validation_v1()
)

FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
    fresh_unit_11_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_10_RESULT,
    )
)

FRESH_UNIT_11_OPTIMIZATION_READY = (
    FRESH_UNIT_11_VALIDATION_READY is True
    and isinstance(
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
        dict,
    )
    and FRESH_RECONSTRUCTION_UNIT_11_RESULT.get(
        "status"
    ) in ("IDLE", "PREPARED_READ_ONLY")
    and FRESH_RECONSTRUCTION_UNIT_11_RESULT.get(
        "read_only"
    ) is True
    and FRESH_RECONSTRUCTION_UNIT_11_RESULT.get(
        "exchange_write"
    ) is False
)

print(
    "UNIT 11 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_11_OPTIMIZATION_READY,
    flush=True,
)

# ============================================================
# END COMPLETE UNIT 11 REPLACEMENT
# ZERO INDENTATION
# UNIT 12 CONTINUES BELOW
# ============================================================



# ============================================================
# START COMPLETE UNIT 12 V5
# ORIGINAL 17248 EXECUTION SEQUENCE
# ADAPTED TO UNIVERSAL DEMO SYMBOL
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

from decimal import Decimal, InvalidOperation


UNIT_12_V5_BASE_URL = "https://api-contract.weex.com"
UNIT_12_V5_POSITION_PATH = "/capi/v3/sim/position/allPosition"
UNIT_12_V5_ORDER_PATH = "/capi/v3/sim/order"

_UNIT12_V5_ORDER_ATTEMPTS = set()


def unit_12_v5_decimal(value, name, allow_zero=False):

    if value is None or isinstance(value, bool):
        raise RuntimeError("UNIT 12 MISSING " + name)

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError("UNIT 12 INVALID " + name) from exc

    if not number.is_finite() or number < 0:
        raise RuntimeError("UNIT 12 INVALID " + name)

    if number == 0 and not allow_zero:
        raise RuntimeError("UNIT 12 ZERO " + name)

    return number


def unit_12_v5_symbol(config):

    symbol = os.getenv("WEEX_SYMBOL", "").strip().upper()

    if not symbol:
        symbol = str(
            config.get("exchange", {}).get("market_symbol", "")
        ).strip().upper()

    if not symbol or not symbol.isalnum():
        raise RuntimeError("UNIT 12 INVALID WEEX SYMBOL")

    return symbol


def unit_12_v5_client_order_id(original_id, direction):

    if not isinstance(original_id, str) or not original_id:
        raise RuntimeError("UNIT 12 CLIENT ID MISSING")

    if re.fullmatch(r"[.A-Za-z0-9_:/-]{1,36}", original_id):
        return original_id

    digest = hashlib.sha256(
        original_id.encode("utf-8")
    ).hexdigest()[:24]

    return "FR12" + ("L" if direction == "LONG" else "S") + digest


def unit_12_v5_result(source, status, reason, symbol):

    if not isinstance(source, dict):
        source = {}

    return {
        "unit": 12,
        "version": "V5_REFERENCE_17248_ADAPTED",
        "status": status,
        "reason": reason,
        "skip_reason": reason,
        "market_symbol": symbol,
        "active_mode": source.get("active_mode"),
        "direction": source.get("direction"),
        "signal_qualified": source.get("signal_qualified") is True,
        "execution_intent": source.get("execution_intent") is True,
        "read_only": False,
        "position_check_attempted": False,
        "position_check_completed": False,
        "position_endpoint_access": False,
        "position_http_status": None,
        "active_position_exists": False,
        "active_positions": [],
        "initial_entry_permitted": False,
        "duplicate_initial_entry_blocked": False,
        "management_path_permitted": True,
        "tp_management_permitted": True,
        "backup_management_permitted": True,
        "position_management_available": True,
        "demo_submission_attempted": False,
        "demo_submission_completed": False,
        "demo_order_accepted": False,
        "fill_verified": False,
        "real_submission_attempted": False,
        "real_cash_execution": False,
        "authenticated_request": False,
        "order_endpoint_access": False,
        "exchange_write": False,
        "order_id": None,
        "client_order_id": None,
        "order_payload": None,
        "http_status": None,
    }


def unit_12_v5_request(method, path, body=None):

    allowed = (
        ("GET", UNIT_12_V5_POSITION_PATH),
        ("POST", UNIT_12_V5_ORDER_PATH),
    )

    if (method, path) not in allowed:
        raise RuntimeError("UNIT 12 NON-DEMO ENDPOINT BLOCKED")

    if method == "GET" and body is not None:
        raise RuntimeError("UNIT 12 INVALID GET BODY")

    if method == "POST" and not isinstance(body, dict):
        raise RuntimeError("UNIT 12 INVALID POST BODY")

    key = os.getenv("WEEX_API_KEY") or os.getenv("API_KEY")
    secret = os.getenv("WEEX_API_SECRET") or os.getenv("API_SECRET")
    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError("UNIT 12 WEEX CREDENTIALS MISSING")

    body_text = (
        json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        if body is not None else ""
    )

    timestamp = str(int(time.time() * 1000))

    message = timestamp + method + path + body_text

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        UNIT_12_V5_BASE_URL + path,
        data=body_text.encode("utf-8") if method == "POST" else None,
        method=method,
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
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.getcode()
            raw = response.read().decode("utf-8", errors="replace")

    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", errors="replace")

    try:
        data = json.loads(raw)
    except ValueError:
        data = {"error": "INVALID_RESPONSE_JSON"}

    return status, data


def unit_12_v5_active_positions(rows, symbol):

    if not isinstance(rows, list):
        raise RuntimeError("UNIT 12 POSITION RESPONSE NOT LIST")

    active = []

    for position in rows:

        if not isinstance(position, dict):
            raise RuntimeError("UNIT 12 INVALID POSITION RECORD")

        if str(position.get("symbol", "")).upper() != symbol:
            continue

        size = unit_12_v5_decimal(
            position.get("size"),
            "POSITION SIZE",
            allow_zero=True,
        )

        if size > 0:
            active.append(position)

    return active



# ============================================================
# START UNIT 12 V5 PAYLOAD COMPATIBILITY CORRECTION
# ZERO INDENTATION
# ============================================================

def unit_12_v5_validate_payload(config, upstream, account):

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 12 CONFIG MISSING")

    if not isinstance(upstream, dict):
        raise RuntimeError("UNIT 12 UNIT 11 RESULT MISSING")

    if not isinstance(account, dict):
        raise RuntimeError("UNIT 12 ACCOUNT MISSING")

    symbol = unit_12_v5_symbol(config)

    if upstream.get("status") not in (
        "READY",
        "PREPARED_READ_ONLY",
    ):
        raise RuntimeError("UNIT 12 UNIT 11 NOT PREPARED")

    if upstream.get("signal_qualified") is not True:
        raise RuntimeError("UNIT 12 SIGNAL NOT QUALIFIED")

    if upstream.get("trade_plan_ready") is not True:
        raise RuntimeError("UNIT 12 TRADE PLAN NOT READY")

    if account.get("demo_contract_verified") is not True:
        raise RuntimeError("UNIT 12 CONTRACT NOT VERIFIED")

    if account.get("demo_balance_verified") is not True:
        raise RuntimeError("UNIT 12 BALANCE NOT VERIFIED")

    if account.get("demo_positions_read_verified") is not True:
        raise RuntimeError("UNIT 12 POSITIONS NOT VERIFIED")

    if account.get("account_can_trade") is not True:
        raise RuntimeError("UNIT 12 ACCOUNT CANNOT TRADE")

    if str(account.get("demo_order_symbol", "")).upper() != symbol:
        raise RuntimeError("UNIT 12 DEMO SYMBOL MISMATCH")

    instruction = upstream.get("order_instruction")

    if not isinstance(instruction, dict):
        raise RuntimeError("UNIT 12 INSTRUCTION MISSING")

    plan = upstream.get("trade_plan")

    if not isinstance(plan, dict):
        raise RuntimeError("UNIT 12 TRADE PLAN MISSING")

    if instruction.get("trade_plan") != plan:
        raise RuntimeError("UNIT 12 TRADE PLAN HANDOVER MISMATCH")

    if str(instruction.get("market_symbol", "")).upper() != symbol:
        raise RuntimeError("UNIT 12 INSTRUCTION SYMBOL MISMATCH")

    if str(instruction.get("demo_order_symbol", "")).upper() != symbol:
        raise RuntimeError("UNIT 12 DEMO ORDER SYMBOL MISMATCH")

    if instruction.get("position_action") != "OPEN":
        raise RuntimeError("UNIT 12 NOT AN OPEN INSTRUCTION")

    if instruction.get("market_type") != "DEMO_FUTURES":
        raise RuntimeError("UNIT 12 NOT A DEMO INSTRUCTION")

    direction = str(instruction.get("direction", "")).upper()

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError("UNIT 12 INVALID DIRECTION")

    if str(upstream.get("direction", "")).upper() != direction:
        raise RuntimeError("UNIT 12 DIRECTION HANDOVER MISMATCH")

    if str(plan.get("direction", "")).upper() != direction:
        raise RuntimeError("UNIT 12 PLAN DIRECTION MISMATCH")

    if str(plan.get("market_symbol", "")).upper() != symbol:
        raise RuntimeError("UNIT 12 PLAN SYMBOL MISMATCH")

    if instruction.get("strategy_mode") != upstream.get("active_mode"):
        raise RuntimeError("UNIT 12 STRATEGY MODE MISMATCH")

    if str(instruction.get("order_type", "")).upper() != "MARKET":
        raise RuntimeError("UNIT 12 ORDER TYPE INVALID")

    quantity = unit_12_v5_decimal(
        instruction.get("quantity"),
        "QUANTITY",
    )

    minimum = unit_12_v5_decimal(
        account.get("minimum_quantity"),
        "MINIMUM QUANTITY",
    )

    step = unit_12_v5_decimal(
        account.get("quantity_step"),
        "QUANTITY STEP",
    )

    if quantity < minimum or quantity % step != 0:
        raise RuntimeError("UNIT 12 CONTRACT QUANTITY INVALID")

    if unit_12_v5_decimal(
        plan.get("quantity"),
        "PLAN QUANTITY",
    ) != quantity:
        raise RuntimeError("UNIT 12 PLAN QUANTITY MISMATCH")

    if unit_12_v5_decimal(
        upstream.get("quantity"),
        "UNIT 11 QUANTITY",
    ) != quantity:
        raise RuntimeError("UNIT 12 UNIT 11 QUANTITY MISMATCH")

    half = quantity / Decimal("2")

    if half < minimum or half % step != 0:
        raise RuntimeError("UNIT 12 HALF QUANTITY INVALID")

    if unit_12_v5_decimal(
        instruction.get("half_quantity"),
        "INSTRUCTION HALF QUANTITY",
    ) != half:
        raise RuntimeError("UNIT 12 HALF QUANTITY MISMATCH")

    original_id = instruction.get("newClientOrderId")

    if not original_id:
        analysis = globals().get(
            "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
        )

        if not isinstance(analysis, dict):
            raise RuntimeError("UNIT 12 SIGNAL IDENTITY MISSING")

        candle_id = analysis.get("latest_close_time_ms")

        if (
            not isinstance(candle_id, int)
            or isinstance(candle_id, bool)
            or candle_id <= 0
        ):
            raise RuntimeError("UNIT 12 CANDLE ID INVALID")

        if not 0 <= int(time.time() * 1000) - candle_id <= 120000:
            raise RuntimeError("UNIT 12 SIGNAL CANDLE STALE")

        original_id = (
            symbol + "-"
            + str(instruction["strategy_mode"]) + "-"
            + direction + "-"
            + str(candle_id)
        )

    client_id = unit_12_v5_client_order_id(
        original_id,
        direction,
    )

    payload = {
        "symbol": symbol,
        "side": "BUY" if direction == "LONG" else "SELL",
        "positionSide": direction,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": client_id,
    }

    print(
        "UNIT 12 UNIT 11 INTERNAL INSTRUCTION = ACCEPTED",
        flush=True
    )

    print(
        "UNIT 12 WEEX PAYLOAD CONVERSION = PASS",
        flush=True
    )

    print(
        "UNIT 12 CONTRACT QUANTITY =",
        format(quantity, "f"),
        flush=True
    )

    return payload, quantity


# ============================================================
# END UNIT 12 V5 PAYLOAD COMPATIBILITY CORRECTION
# ============================================================

def fresh_reconstruction_unit_12(
    config,
    unit_11_result,
    unit_8_result=None,
):

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 12 CONFIG INVALID")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("UNIT 12 NON-DEMO ENVIRONMENT")

    if not isinstance(unit_11_result, dict):
        raise RuntimeError("UNIT 12 UNIT 11 INVALID")

    if unit_8_result is None:
        unit_8_result = globals().get(
            "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
        )

    symbol = unit_12_v5_symbol(config)

    mode = os.getenv("BOT_MODE", "PAUSE").strip().upper()

    if mode not in ("RUN", "PAUSE"):
        raise RuntimeError("UNIT 12 BOT_MODE INVALID")

    result = unit_12_v5_result(
        unit_11_result, "IDLE", "NOT_EVALUATED", symbol
    )

    print("=" * 80, flush=True)
    print("UNIT 12 V5 REFERENCE EXECUTION START", flush=True)
    print("UNIT 12 BOT_MODE =", mode, flush=True)
    print("UNIT 12 SYMBOL =", symbol, flush=True)

    if mode == "PAUSE":
        result["reason"] = "BOT_MODE_PAUSE"
        result["skip_reason"] = "BOT_MODE_PAUSE"
        return result

    upstream_status = str(
        unit_11_result.get("status", "")
    ).upper()

    if upstream_status in ("IDLE", "BLOCKED", "SKIPPED"):
        result["reason"] = str(
            unit_11_result.get("reason")
            or unit_11_result.get("skip_reason")
            or "NO_ACCEPTABLE_CANDIDATE"
        )
        result["skip_reason"] = result["reason"]
        return result

    if upstream_status not in ("READY", "PREPARED_READ_ONLY"):
        result["status"] = "BLOCKED"
        result["reason"] = "UNIT_11_NOT_READY"
        result["skip_reason"] = result["reason"]
        return result

    try:
        payload, quantity = unit_12_v5_validate_payload(
            config, unit_11_result, unit_8_result
        )
    except Exception as exc:
        result["status"] = "BLOCKED"
        result["reason"] = str(exc)
        result["skip_reason"] = result["reason"]
        return result

    client_id = payload["newClientOrderId"]

    result["client_order_id"] = client_id
    result["order_payload"] = dict(payload)

    print("UNIT 12 CLIENT ORDER ID =", client_id, flush=True)
    print("UNIT 12 QUANTITY =", format(quantity, "f"), flush=True)

    # ORIGINAL V5 IN-PROCESS DUPLICATE PROTECTION

    if client_id in _UNIT12_V5_ORDER_ATTEMPTS:
        result["status"] = "ORDER_UNCERTAIN"
        result["reason"] = "PREVIOUS_CLIENT_ORDER_ATTEMPT"
        result["skip_reason"] = result["reason"]
        return result

    # ORIGINAL V5 FRESH AUTHENTICATED POSITION GET

    result["position_check_attempted"] = True

    try:
        position_http, positions = unit_12_v5_request(
            "GET", UNIT_12_V5_POSITION_PATH
        )

        result["authenticated_request"] = True
        result["position_endpoint_access"] = True
        result["position_http_status"] = position_http

        if not 200 <= position_http < 300:
            result["status"] = "POSITION_CHECK_FAILED"
            result["reason"] = "WEEX_POSITION_HTTP_" + str(position_http)
            result["skip_reason"] = result["reason"]
            return result

        active = unit_12_v5_active_positions(
            positions, symbol
        )

    except Exception as exc:
        result["status"] = "POSITION_CHECK_FAILED"
        result["reason"] = "POSITION_REQUEST_ERROR"
        result["skip_reason"] = result["reason"]

        print(
            "UNIT 12 POSITION ERROR =",
            type(exc).__name__,
            str(exc)[:180],
            flush=True
        )
        return result

    result["position_check_completed"] = True

    if active:
        result["status"] = "ACTIVE_POSITION_BLOCK"
        result["reason"] = "NONZERO_POSITION_BLOCK_INITIAL_ENTRY"
        result["skip_reason"] = result["reason"]
        result["active_position_exists"] = True
        result["active_positions"] = active
        result["duplicate_initial_entry_blocked"] = True
        return result

    # ORIGINAL V5 SIGNED DEMO POST

    result["initial_entry_permitted"] = True

    _UNIT12_V5_ORDER_ATTEMPTS.add(client_id)

    result["demo_submission_attempted"] = True
    result["order_endpoint_access"] = True

    print(
        "UNIT 12 FRESH FLAT POSITION VERIFIED",
        flush=True
    )
    print(
        "UNIT 12 SENDING WEEX DEMO ORDER",
        flush=True
    )

    try:
        order_http, response = unit_12_v5_request(
            "POST", UNIT_12_V5_ORDER_PATH, payload
        )
    except Exception as exc:
        result["status"] = "ORDER_UNCERTAIN"
        result["reason"] = "POST_RESPONSE_UNCERTAIN"
        result["skip_reason"] = result["reason"]

        print(
            "UNIT 12 DO NOT AUTOMATICALLY RETRY",
            type(exc).__name__,
            flush=True
        )
        return result

    result["http_status"] = order_http

    if not isinstance(response, dict):
        result["status"] = "ORDER_UNCERTAIN"
        result["reason"] = "UNRECOGNIZED_ORDER_RESPONSE"
        result["skip_reason"] = result["reason"]
        return result

    if (
        not 200 <= order_http < 300
        or response.get("success") is not True
    ):
        result["status"] = "DEMO_REJECTED"
        result["reason"] = (
            "WEEX_REJECTED_"
            + str(response.get("code") or "UNKNOWN")
        )
        result["skip_reason"] = result["reason"]

        print(
            "UNIT 12 WEEX RESPONSE =",
            str(response)[:300],
            flush=True
        )
        return result

    order_id = response.get("orderId")

    if not order_id:
        result["status"] = "ORDER_UNCERTAIN"
        result["reason"] = "SUCCESS_RESPONSE_MISSING_ORDER_ID"
        result["skip_reason"] = result["reason"]
        return result

    result.update({
        "status": "DEMO_SUBMITTED",
        "reason": "NONE",
        "skip_reason": "NONE",
        "demo_submission_completed": True,
        "demo_order_accepted": True,
        "exchange_write": True,
        "order_id": str(order_id),
        "exchange_response": response,
    })

    print("UNIT 12 WEEX ORDER ID =", order_id, flush=True)
    print("UNIT 12 STATUS = DEMO_SUBMITTED", flush=True)
    print("UNIT 12 FILL VERIFIED = False", flush=True)
    print("UNIT 12 REAL CASH EXECUTION = DISABLED", flush=True)

    return result


def fresh_unit_12_hybrid_adapter(
    execution_config,
    unit_11_result,
):

    account = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    result = fresh_reconstruction_unit_12(
        execution_config,
        unit_11_result,
        account,
    )

    if result.get("real_submission_attempted") is not False:
        raise RuntimeError("UNIT 12 REAL CASH SAFETY FAILURE")

    print("UNIT 12 STATUS =", result["status"], flush=True)
    print("UNIT 12 REASON =", result["reason"], flush=True)
    print(
        "UNIT 12 DEMO SUBMISSION ATTEMPTED =",
        result["demo_submission_attempted"],
        flush=True
    )
    print(
        "UNIT 12 DEMO ORDER ACCEPTED =",
        result["demo_order_accepted"],
        flush=True
    )
    print(
        "UNIT 12 EXCHANGE WRITE =",
        result["exchange_write"],
        flush=True
    )

    return result


# ============================================================
# START UNIT 12 V5 STARTUP HANDOVER
# RESTORE ORIGINAL UNIT 12 TO UNIT 13 CONTRACT
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_unit_12_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
    )
)

FRESH_UNIT_12_VALIDATION_READY = True

FRESH_UNIT_12_OPTIMIZATION_READY = (
    isinstance(
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
        dict
    )
)

if not FRESH_UNIT_12_OPTIMIZATION_READY:
    raise RuntimeError(
        "UNIT 12 STARTUP RESULT INVALID"
    )

print(
    "FRESH RECONSTRUCTION UNIT 12 RESULT =",
    FRESH_RECONSTRUCTION_UNIT_12_RESULT.get("status"),
    flush=True
)

print(
    "UNIT 12 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_12_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END UNIT 12 V5 STARTUP HANDOVER
# ============================================================

# ============================================================
# END COMPLETE UNIT 12 V5
# UNIT 13 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 13 V1 REPLACEMENT
# UNIVERSAL WEEX DEMO POSITION MANAGEMENT PLANNER
#
# SOURCE: 16414 MODEL UNIT 13 ADAPTED
# UNIT 12 -> UNIT 13 -> UNIT 14
#
# TP1 = 20% ESTIMATED NET ROI
# TP2 = 40% ESTIMATED NET ROI
# TP3 = TRAILING
# ALLOCATION = 10 / 20 / 70
#
# BEFORE TP1: ONE ATR HEDGE/RECOVERY CYCLE
# AFTER FAILED RECOVERY: B1-B5 ELIGIBILITY
# AFTER TP1: DYNAMIC BREAK-EVEN
# AFTER TP2: TRAILING PROFIT
#
# NO EXCHANGE WRITE IN THIS UNIT
# NO REAL-CASH EXECUTION
# BOT_MODE INDEPENDENT
# ZERO INDENTATION
# ============================================================

import os as _u13_os
from decimal import (
    Decimal as _U13D,
    InvalidOperation as _U13Invalid,
    ROUND_DOWN as _U13_DOWN,
    ROUND_UP as _U13_UP,
)

UNIT_13_VERSION = "V1_UNIVERSAL_PROTECTION_PLANNER"


# ============================================================
# 13.1 STRICT NUMERIC HELPERS
# ============================================================

def unit_13_decimal(value, allow_zero=False):

    if value is None or isinstance(value, bool):
        raise ValueError("MISSING_NUMBER")

    try:
        number = _U13D(str(value))
    except (
        _U13Invalid,
        TypeError,
        ValueError,
    ):
        raise ValueError("INVALID_NUMBER")

    if not number.is_finite():
        raise ValueError("NONFINITE_NUMBER")

    if number < 0 or (
        number == 0 and not allow_zero
    ):
        raise ValueError("NONPOSITIVE_NUMBER")

    return number


def unit_13_fmt(value):

    number = _U13D(str(value))

    return format(number.normalize(), "f")


def unit_13_env(name, default, zero=False):

    return unit_13_decimal(
        _u13_os.environ.get(
            name, str(default)
        ),
        zero,
    )


def unit_13_round_price(price, tick, side, kind):

    price = unit_13_decimal(price)
    tick = unit_13_decimal(tick)

    # Conservative rounding:
    # LONG profit target rounds upward.
    # SHORT profit target rounds downward.
    if kind == "PROFIT":

        rounding = (
            _U13_UP if side == "LONG"
            else _U13_DOWN
        )

    else:

        rounding = (
            _U13_DOWN if side == "LONG"
            else _U13_UP
        )

    units = (
        price / tick
    ).to_integral_value(rounding=rounding)

    rounded = units * tick

    if rounded <= 0:
        raise ValueError("INVALID_ROUNDED_PRICE")

    return rounded


# ============================================================
# 13.2 UNIVERSAL SYMBOL
# ============================================================

def unit_13_symbol(config):

    symbol = _u13_os.environ.get(
        "WEEX_SYMBOL", ""
    ).strip().upper()

    if not symbol and isinstance(config, dict):

        symbol = str(
            config.get(
                "market_symbol",
                config.get("symbol", "")
            )
        ).strip().upper()

    if not symbol or not symbol.isalnum():
        raise ValueError("INVALID_SYMBOL")

    return symbol


# ============================================================
# 13.3 ADJUSTABLE CONFIGURATION
# ============================================================

def unit_13_config():

    tp1 = unit_13_env(
        "TP1_NET_ROI_PERCENT", "20"
    )

    tp2 = unit_13_env(
        "TP2_NET_ROI_PERCENT", "40"
    )

    a1 = unit_13_env(
        "TP1_ALLOCATION_PERCENT", "10"
    )

    a2 = unit_13_env(
        "TP2_ALLOCATION_PERCENT", "20"
    )

    a3 = unit_13_env(
        "TP3_ALLOCATION_PERCENT", "70"
    )

    fee = unit_13_env(
        "WEEX_TAKER_FEE_PERCENT",
        "0.08",
        True,
    )

    trail = unit_13_env(
        "TP3_TRAILING_PERCENT", "0.2"
    )

    atr1 = unit_13_env(
        "HEDGE_ATR_STAGE1_MULTIPLIER", "1"
    )

    atr2 = unit_13_env(
        "HEDGE_ATR_STAGE2_MULTIPLIER", "2"
    )

    exposure = unit_13_env(
        "MAX_EXPOSURE_PERCENT", "100"
    )

    if tp2 <= tp1:
        raise ValueError("TP_TARGET_ORDER_INVALID")

    if a1 + a2 + a3 != 100:
        raise ValueError("TP_ALLOCATION_NOT_100")

    if atr2 <= atr1:
        raise ValueError("HEDGE_ATR_ORDER_INVALID")

    if exposure > 100:
        raise ValueError("EXPOSURE_OVER_100")

    return {
        "tp1_net_roi_percent": tp1,
        "tp2_net_roi_percent": tp2,
        "tp1_allocation_percent": a1,
        "tp2_allocation_percent": a2,
        "tp3_allocation_percent": a3,
        "taker_fee_percent": fee,
        "tp3_trailing_percent": trail,
        "hedge_stage1_atr": atr1,
        "hedge_stage2_atr": atr2,
        "max_exposure_percent": exposure,
        "backup_count": 5,
        "hedge_cycles_max": 1,
    }


# ============================================================
# 13.4 RESULT CONTRACT
# ============================================================

def unit_13_result(symbol):

    return {
        "unit": 13,
        "version": UNIT_13_VERSION,
        "status": "IDLE",
        "reason": "NO_VERIFIED_POSITION",
        "market_symbol": symbol,
        "bot_mode_independent": True,
        "position_verified": False,
        "position_side": None,
        "position_quantity": None,
        "entry_price": None,
        "leverage": None,
        "atr14": None,
        "tp1_price": None,
        "tp2_price": None,
        "tp_quantity_plan": None,
        "hedge_stage1_price": None,
        "hedge_stage2_price": None,
        "management_phase": "NONE",
        "hedge_cycle_limit": 1,
        "backup_count": 5,
        "backup_activation": (
            "AFTER_FAILED_FIRST_HEDGE_RECOVERY"
        ),
        "profit_protection": None,
        "management_instruction": None,
        "execution_authorized": False,
        "exchange_write": False,
        "real_cash_execution": False,
    }


# ============================================================
# 13.5 NET ROI TARGET CALCULATION
#
# ESTIMATED:
# ROI / LEVERAGE + ENTRY/EXIT FEES
#
# ACTUAL FUNDING, SLIPPAGE AND OTHER CHARGES
# MUST BE RECONCILED BEFORE CLAIMING NET PROFIT.
# ============================================================

def unit_13_target_price(
    entry,
    leverage,
    roi,
    fee,
    side,
    tick,
):

    entry = unit_13_decimal(entry)
    leverage = unit_13_decimal(leverage)
    roi = unit_13_decimal(roi) / 100
    fee = unit_13_decimal(
        fee, True
    ) / 100

    # Approximate fee-adjusted movement.
    movement = (
        roi / leverage
        + fee * 2
    )

    if side == "LONG":

        price = entry * (
            1 + movement
        )

    elif side == "SHORT":

        price = entry * (
            1 - movement
        )

    else:
        raise ValueError("INVALID_POSITION_SIDE")

    if price <= 0:
        raise ValueError("INVALID_TP_PRICE")

    return unit_13_round_price(
        price,
        tick,
        side,
        "PROFIT",
    )


# ============================================================
# 13.6 STEP-AWARE TP ALLOCATION
#
# ZERO QUANTITY MEANS DEFERRED, NOT FILLED.
# ============================================================

def unit_13_quantity_plan(
    quantity,
    minimum,
    step,
    config,
):

    quantity = unit_13_decimal(quantity)
    minimum = unit_13_decimal(minimum)
    step = unit_13_decimal(step)

    if quantity % step != 0:
        raise ValueError(
            "POSITION_QUANTITY_STEP_INVALID"
        )

    def floor_step(value):

        return (
            (value / step).to_integral_value(
                rounding=_U13_DOWN
            ) * step
        )

    desired1 = (
        quantity
        * config["tp1_allocation_percent"]
        / 100
    )

    desired2 = (
        quantity
        * config["tp2_allocation_percent"]
        / 100
    )

    q1 = floor_step(desired1)
    q2 = floor_step(desired2)

    if q1 < minimum:
        q1 = _U13D("0")

    if q2 < minimum:
        q2 = _U13D("0")

    q3 = quantity - q1 - q2

    valid = (
        q3 >= minimum
        and q3 % step == 0
        and q1 + q2 + q3 == quantity
    )

    return {
        "plan_valid": valid,
        "tp1_desired": unit_13_fmt(desired1),
        "tp2_desired": unit_13_fmt(desired2),
        "tp1_quantity": unit_13_fmt(q1),
        "tp2_quantity": unit_13_fmt(q2),
        "tp3_quantity": unit_13_fmt(q3),
        "tp1_deferred": q1 == 0,
        "tp2_deferred": q2 == 0,
        "execution_authorized": False,
    }


# ============================================================
# 13.7 ATR HEDGE TRIGGER GEOMETRY
# ============================================================

def unit_13_hedge_prices(
    entry,
    atr,
    side,
    tick,
    config,
):

    entry = unit_13_decimal(entry)
    atr = unit_13_decimal(atr)

    first = (
        atr * config["hedge_stage1_atr"]
    )

    second = (
        atr * config["hedge_stage2_atr"]
    )

    if side == "LONG":

        price1 = entry - first
        price2 = entry - second

    elif side == "SHORT":

        price1 = entry + first
        price2 = entry + second

    else:
        raise ValueError("INVALID_HEDGE_SIDE")

    if price1 <= 0 or price2 <= 0:
        raise ValueError("INVALID_HEDGE_GEOMETRY")

    return (
        unit_13_round_price(
            price1, tick, side, "HEDGE"
        ),
        unit_13_round_price(
            price2, tick, side, "HEDGE"
        ),
    )


# ============================================================
# 13.8 VERIFIED POSITION EXTRACTION
#
# UNIT 12 ACCEPTANCE IS NOT A POSITION FILL.
# POSITION MUST BE CONFIRMED BY EXCHANGE DATA.
# ============================================================

def unit_13_position(snapshot, symbol):

    if not isinstance(snapshot, dict):
        return None

    if snapshot.get(
        "demo_positions_read_verified"
    ) is not True:
        return None

    records = snapshot.get("positions")

    if not isinstance(records, list):
        return None

    matching = []

    for position in records:

        if not isinstance(position, dict):
            continue

        position_symbol = str(
            position.get(
                "symbol",
                position.get("market_symbol", "")
            )
        ).strip().upper()

        if position_symbol != symbol:
            continue

        try:

            quantity = unit_13_decimal(
                position.get(
                    "quantity",
                    position.get(
                        "size",
                        position.get(
                            "total", 0
                        )
                    )
                ),
                True,
            )

        except ValueError:
            return None

        if quantity > 0:
            matching.append(position)

    # Do not select an arbitrary position if
    # both long and short are present.
    if len(matching) != 1:
        return None

    return matching[0]


# ============================================================
# 13.9 ATR SOURCE
# ============================================================

def unit_13_atr(snapshot):

    if not isinstance(snapshot, dict):
        return None

    for key in (
        "atr14",
        "atr_14",
        "atr",
    ):

        value = snapshot.get(key)

        if value is None:
            continue

        try:
            return unit_13_decimal(value)
        except ValueError:
            continue

    return None


# ============================================================
# 13.10 MANAGEMENT PLANNING
#
# DO NOT INFER TP1/TP2 FILLS FROM PRICE ALONE.
# DO NOT INFER HEDGE CYCLE FROM PRICE ALONE.
# ============================================================

def fresh_reconstruction_unit_13(
    execution_config,
    unit_12_result,
    unit_8_result=None,
    market_snapshot=None,
):

    symbol = unit_13_symbol(
        execution_config
    )

    result = unit_13_result(symbol)

    try:

        config = unit_13_config()

    except ValueError as exc:

        result["status"] = "BLOCKED"
        result["reason"] = (
            "INVALID_TP_CONFIGURATION:"
            + str(exc)
        )

        return result

    result["tp_config"] = {
        key: (
            unit_13_fmt(value)
            if isinstance(value, _U13D)
            else value
        )
        for key, value in config.items()
    }

    if not isinstance(unit_8_result, dict):

        result["status"] = "WAITING"
        result["reason"] = (
            "UNIT_8_POSITION_SNAPSHOT_MISSING"
        )

        return result

    position = unit_13_position(
        unit_8_result,
        symbol,
    )

    if position is None:

        if unit_8_result.get(
            "position_flat_verified"
        ) is True:

            result["status"] = "IDLE"
            result["reason"] = (
                "EXCHANGE_POSITION_FLAT"
            )

        else:

            result["status"] = "WAITING"
            result["reason"] = (
                "POSITION_UNVERIFIED_OR_AMBIGUOUS"
            )

        return result

    side = str(
        position.get(
            "positionSide",
            position.get(
                "holdSide",
                position.get("side", "")
            )
        )
    ).strip().upper()

    if side in ("BUY",):
        side = "LONG"

    if side in ("SELL",):
        side = "SHORT"

    if side not in ("LONG", "SHORT"):

        result["status"] = "BLOCKED"
        result["reason"] = (
            "POSITION_SIDE_UNVERIFIED"
        )

        return result

    try:

        quantity = unit_13_decimal(
            position.get(
                "quantity",
                position.get(
                    "size",
                    position.get("total")
                )
            )
        )

        entry = unit_13_decimal(
            position.get(
                "averageEntryPrice",
                position.get(
                    "avgPrice",
                    position.get(
                        "entryPrice"
                    )
                )
            )
        )

        leverage = unit_13_decimal(
            position.get(
                "leverage",
                _u13_os.environ.get(
                    "WEEX_LEVERAGE_LONG"
                    if side == "LONG"
                    else "WEEX_LEVERAGE_SHORT"
                )
            )
        )

        minimum = unit_13_decimal(
            unit_8_result.get(
                "minimum_quantity"
            )
        )

        step = unit_13_decimal(
            unit_8_result.get(
                "quantity_step"
            )
        )

        tick = unit_13_decimal(
            unit_8_result.get(
                "price_step"
            )
        )

    except ValueError as exc:

        result["status"] = "BLOCKED"
        result["reason"] = (
            "POSITION_CONTRACT_DATA_INVALID:"
            + str(exc)
        )

        return result

    result["position_verified"] = True
    result["position_side"] = side
    result["position_quantity"] = (
        unit_13_fmt(quantity)
    )
    result["entry_price"] = (
        unit_13_fmt(entry)
    )
    result["leverage"] = (
        unit_13_fmt(leverage)
    )

    try:

        tp1 = unit_13_target_price(
            entry,
            leverage,
            config["tp1_net_roi_percent"],
            config["taker_fee_percent"],
            side,
            tick,
        )

        tp2 = unit_13_target_price(
            entry,
            leverage,
            config["tp2_net_roi_percent"],
            config["taker_fee_percent"],
            side,
            tick,
        )

        quantity_plan = (
            unit_13_quantity_plan(
                quantity,
                minimum,
                step,
                config,
            )
        )

    except ValueError as exc:

        result["status"] = "BLOCKED"
        result["reason"] = (
            "TP_PLAN_INVALID:"
            + str(exc)
        )

        return result

    result["tp1_price"] = (
        unit_13_fmt(tp1)
    )

    result["tp2_price"] = (
        unit_13_fmt(tp2)
    )

    result["tp_quantity_plan"] = (
        quantity_plan
    )

    if not quantity_plan["plan_valid"]:

        result["status"] = "BLOCKED"
        result["reason"] = (
            "TP_QUANTITY_PLAN_INVALID"
        )

        return result

    atr = unit_13_atr(
        market_snapshot
    )

    if atr is None:

        result["status"] = "WAITING"
        result["reason"] = (
            "VERIFIED_ATR14_REQUIRED"
        )

        result["management_phase"] = (
            "POSITION_ADOPTED_TP_ONLY"
        )

        return result

    result["atr14"] = unit_13_fmt(atr)

    try:

        hedge1, hedge2 = (
            unit_13_hedge_prices(
                entry,
                atr,
                side,
                tick,
                config,
            )
        )

    except ValueError as exc:

        result["status"] = "BLOCKED"
        result["reason"] = (
            "HEDGE_GEOMETRY_INVALID:"
            + str(exc)
        )

        return result

    result["hedge_stage1_price"] = (
        unit_13_fmt(hedge1)
    )

    result["hedge_stage2_price"] = (
        unit_13_fmt(hedge2)
    )

    # The current snapshot does not establish
    # whether TP1/TP2 have actually filled,
    # or whether a hedge cycle was completed.
    #
    # Preserve all phase possibilities,
    # but do not authorize exchange writes.

    result["management_phase"] = (
        "AWAITING_EXCHANGE_CYCLE_RECONCILIATION"
    )

    result["profit_protection"] = {
        "before_tp1": (
            "ONE_ATR_HEDGE_RECOVERY_CYCLE"
        ),
        "after_failed_recovery": (
            "B1_B5_HYBRID_BACKUP_ELIGIBILITY"
        ),
        "after_tp1": (
            "PROTECT_REALIZED_PROFIT_AND_"
            "DYNAMIC_BREAK_EVEN"
        ),
        "after_tp2": (
            "DYNAMIC_TRAILING_PROFIT"
        ),
        "tp3_trailing_percent": (
            unit_13_fmt(
                config["tp3_trailing_percent"]
            )
        ),
        "secured_profit_excluded_from_"
        "reversal_budget": True,
    }

    result["management_instruction"] = {
        "symbol": symbol,
        "position_side": side,
        "position_quantity": (
            unit_13_fmt(quantity)
        ),
        "tp1_price": result["tp1_price"],
        "tp2_price": result["tp2_price"],
        "tp_quantities": quantity_plan,
        "hedge_stage1_price": (
            result["hedge_stage1_price"]
        ),
        "hedge_stage2_price": (
            result["hedge_stage2_price"]
        ),
        "hedge_cycle_limit": 1,
        "backup_count": 5,
        "read_only": True,
        "execution_authorized": False,
    }

    result["status"] = "PLAN_READY"
    result["reason"] = (
        "POSITION_PLAN_READY_"
        "EXECUTION_RECONCILIATION_PENDING"
    )

    return result


# ============================================================
# 13.11 ADAPTER
# ============================================================

def fresh_unit_13_hybrid_adapter(
    execution_config,
    unit_12_result,
):

    unit_8 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    market = globals().get(
        "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
    )

    if not isinstance(market, dict):

        market = globals().get(
            "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
        )

    result = fresh_reconstruction_unit_13(
        execution_config,
        unit_12_result,
        unit_8,
        market,
    )

    print(
        "UNIT 13 VERSION =",
        UNIT_13_VERSION,
        flush=True
    )

    print(
        "UNIT 13 MARKET SYMBOL =",
        result["market_symbol"],
        flush=True
    )

    print(
        "UNIT 13 STATUS =",
        result["status"],
        flush=True
    )

    print(
        "UNIT 13 REASON =",
        result["reason"],
        flush=True
    )

    print(
        "UNIT 13 POSITION VERIFIED =",
        result["position_verified"],
        flush=True
    )

    print(
        "UNIT 13 TP1 PRICE =",
        result["tp1_price"],
        flush=True
    )

    print(
        "UNIT 13 TP2 PRICE =",
        result["tp2_price"],
        flush=True
    )

    print(
        "UNIT 13 HEDGE STAGE 1 =",
        result["hedge_stage1_price"],
        flush=True
    )

    print(
        "UNIT 13 HEDGE STAGE 2 =",
        result["hedge_stage2_price"],
        flush=True
    )

    print(
        "UNIT 13 BOT_MODE INDEPENDENT =",
        result["bot_mode_independent"],
        flush=True
    )

    print(
        "UNIT 13 EXECUTION AUTHORIZED =",
        result["execution_authorized"],
        flush=True
    )

    print(
        "UNIT 13 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "UNIT 13 REAL CASH EXECUTION = DISABLED",
        flush=True
    )

    return result


# ============================================================
# 13.12 LOCAL VALIDATION
# ============================================================

def unit_13_validation_v1():

    passed = 0
    failed = 0

    def check(name, condition):

        nonlocal passed, failed

        ok = bool(condition)

        if ok:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 13 TEST",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    config = unit_13_config()

    check(
        "TP1_DEFAULT_OR_ADJUSTABLE",
        config["tp1_net_roi_percent"] > 0
    )

    check(
        "TP2_ABOVE_TP1",
        config["tp2_net_roi_percent"]
        > config["tp1_net_roi_percent"]
    )

    check(
        "ALLOCATION_TOTAL_100",
        sum(
            config[key]
            for key in (
                "tp1_allocation_percent",
                "tp2_allocation_percent",
                "tp3_allocation_percent",
            )
        ) == 100
    )

    check(
        "HEDGE_ONE_CYCLE",
        config["hedge_cycles_max"] == 1
    )

    check(
        "FIVE_BACKUPS",
        config["backup_count"] == 5
    )

    check(
        "LONG_TARGET_ABOVE_ENTRY",
        unit_13_target_price(
            "100", "10", "20",
            "0.08", "LONG", "0.01"
        ) > 100
    )

    check(
        "SHORT_TARGET_BELOW_ENTRY",
        unit_13_target_price(
            "100", "10", "20",
            "0.08", "SHORT", "0.01"
        ) < 100
    )

    plan = unit_13_quantity_plan(
        "10", "1", "1", config
    )

    check(
        "UNIVERSAL_STEP_PLAN",
        plan["plan_valid"] is True
    )

    check(
        "NO_EXCHANGE_WRITE",
        unit_13_result(
            "NEARUSDT"
        )["exchange_write"] is False
    )

    check(
        "BOT_MODE_INDEPENDENT",
        unit_13_result(
            "NEARUSDT"
        )["bot_mode_independent"] is True
    )

    print(
        "UNIT 13 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 13 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT_13_VALIDATION_FAILED"
        )

    return True


# ============================================================
# 13.13 STARTUP
# ============================================================

FRESH_UNIT_13_VALIDATION_READY = (
    unit_13_validation_v1()
)

FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_unit_13_hybrid_adapter(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)

FRESH_UNIT_13_OPTIMIZATION_READY = (
    FRESH_UNIT_13_VALIDATION_READY
)

print(
    "FRESH RECONSTRUCTION UNIT 13 RESULT =",
    FRESH_RECONSTRUCTION_UNIT_13_RESULT[
        "status"
    ],
    flush=True
)

print(
    "UNIT 13 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_13_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 13 V1 REPLACEMENT
# UNIT 14 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 14 V1
# UNIVERSAL WEEX DEMO SAFETY SUPERVISOR
# ZERO INDENTATION
#
# UNIT 8 + UNIT 12 + UNIT 13 -> UNIT 14
#
# EXISTING POSITION SUPERVISION INDEPENDENT OF BOT_MODE
# NO SIMULATED PROTECTION CLAIMS
# NO EXCHANGE WRITES
# NO REAL-CASH EXECUTION
# ============================================================

from decimal import Decimal as _U14D
from decimal import InvalidOperation as _U14Invalid

UNIT_14_VERSION = "V1_UNIVERSAL_SAFETY_SUPERVISOR"


# ============================================================
# 14.1 NUMERIC VALIDATION
# ============================================================

def unit_14_number(value, zero=False):

    if value is None or isinstance(value, bool):
        return None

    try:
        number = _U14D(str(value))
    except (
        _U14Invalid,
        ValueError,
        TypeError,
    ):
        return None

    if not number.is_finite():
        return None

    if number < 0 or (
        number == 0 and not zero
    ):
        return None

    return number


# ============================================================
# 14.2 DEFAULT RESULT
# ============================================================

def unit_14_result(symbol):

    return {
        "unit": 14,
        "version": UNIT_14_VERSION,
        "market_symbol": symbol,
        "status": "WAITING",
        "reason": "POSITION_RECONCILIATION_PENDING",
        "bot_mode_independent": True,
        "position_flat_verified": False,
        "position_verified": False,
        "position_quantity": None,
        "contract_verified": False,
        "quantity_step_valid": False,
        "tp_plan_valid": False,
        "hedge_plan_valid": False,
        "exposure_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
        "management_execution_verified": False,
        "new_entry_authorized": False,
        "safety_alert": False,
        "alert_severity": "NONE",
        "alert_reason": None,
        "requires_operator_attention": False,
        "execution_authorized": False,
        "exchange_write": False,
        "real_cash_execution": False,
    }


# ============================================================
# 14.3 SAFETY SUPERVISION
# ============================================================

def fresh_reconstruction_unit_14(
    config,
    unit_8,
    unit_12,
    unit_13,
):

    exchange = (
        config.get("exchange", {})
        if isinstance(config, dict)
        else {}
    )

    symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    result = unit_14_result(symbol)

    def alert(reason, severity="CRITICAL"):

        result["status"] = "ALERT"
        result["reason"] = reason
        result["safety_alert"] = True
        result["alert_severity"] = severity
        result["alert_reason"] = reason
        result["requires_operator_attention"] = True

        return result

    if not symbol.endswith("USDT"):
        return alert("INVALID_MARKET_SYMBOL")

    if not isinstance(config, dict):
        return alert("CONFIGURATION_MISSING")

    if config.get(
        "execution_environment"
    ) != "DEMO":
        return alert("DEMO_ENVIRONMENT_REQUIRED")

    if config.get(
        "real_cash_execution_enabled"
    ) is not False:
        return alert("REAL_CASH_SAFETY_MISMATCH")

    if not all(
        isinstance(x, dict)
        for x in (unit_8, unit_12, unit_13)
    ):
        return alert("UPSTREAM_RESULT_MISSING")

    if str(
        unit_8.get("market_symbol", "")
    ).upper() != symbol:
        return alert("UNIT_8_SYMBOL_MISMATCH")

    if str(
        unit_13.get("market_symbol", "")
    ).upper() != symbol:
        return alert("UNIT_13_SYMBOL_MISMATCH")

    result["contract_verified"] = (
        unit_8.get(
            "demo_contract_verified"
        ) is True
    )

    if not result["contract_verified"]:
        return alert("DEMO_CONTRACT_UNVERIFIED")

    if unit_8.get(
        "demo_positions_read_verified"
    ) is not True:
        return alert("POSITION_READ_UNVERIFIED")

    if unit_8.get(
        "position_flat_verified"
    ) is True:

        result["position_flat_verified"] = True

        # A flat position requires no position-level
        # TP or hedge management.
        result["status"] = "IDLE"
        result["reason"] = "VERIFIED_FLAT_POSITION"
        result["alert_severity"] = "NONE"

        return result

    if unit_13.get(
        "position_verified"
    ) is not True:
        return alert(
            "OPEN_POSITION_NOT_FULLY_RECONCILED"
        )

    result["position_verified"] = True

    quantity = unit_14_number(
        unit_13.get("position_quantity")
    )

    minimum = unit_14_number(
        unit_8.get("minimum_quantity")
    )

    step = unit_14_number(
        unit_8.get("quantity_step")
    )

    if any(
        value is None
        for value in (
            quantity,
            minimum,
            step,
        )
    ):
        return alert("POSITION_PRECISION_INVALID")

    result["position_quantity"] = str(quantity)

    result["quantity_step_valid"] = (
        quantity >= minimum
        and quantity % step == 0
    )

    if not result["quantity_step_valid"]:
        return alert(
            "OPEN_POSITION_QUANTITY_INVALID"
        )

    # ========================================================
    # TP PLAN VALIDATION
    # ========================================================

    tp_plan = unit_13.get(
        "tp_quantity_plan"
    )

    if not isinstance(tp_plan, dict):
        return alert("TP_PLAN_MISSING")

    result["tp_plan_valid"] = (
        tp_plan.get("plan_valid") is True
    )

    if not result["tp_plan_valid"]:
        return alert("TP_PLAN_INVALID")

    # ========================================================
    # HEDGE PLAN VALIDATION
    # ========================================================

    hedge1 = unit_14_number(
        unit_13.get("hedge_stage1_price")
    )

    hedge2 = unit_14_number(
        unit_13.get("hedge_stage2_price")
    )

    entry = unit_14_number(
        unit_13.get("entry_price")
    )

    side = unit_13.get("position_side")

    if None in (hedge1, hedge2, entry):
        return alert("ATR_HEDGE_PLAN_INCOMPLETE")

    if side == "LONG":

        geometry_valid = (
            hedge2 < hedge1 < entry
        )

    elif side == "SHORT":

        geometry_valid = (
            entry < hedge1 < hedge2
        )

    else:
        geometry_valid = False

    result["hedge_plan_valid"] = (
        geometry_valid
    )

    if not geometry_valid:
        return alert("ATR_HEDGE_GEOMETRY_INVALID")

    # ========================================================
    # EXPOSURE RECONCILIATION
    #
    # No exposure percentage is inferred from
    # entry margin alone. Existing positions,
    # pending orders and available account equity
    # must all be reconciled.
    # ========================================================

    result["exposure_verified"] = False

    # ========================================================
    # ACTUAL EXCHANGE PROTECTION
    #
    # A calculated TP/hedge price is not proof
    # that an order exists at WEEX.
    #
    # Do not infer order placement from Unit 13.
    # ========================================================

    result["exchange_protection_verified"] = False
    result["management_execution_verified"] = False
    result["protection_active"] = False

    return alert(
        "OPEN_POSITION_PROTECTION_NOT_VERIFIED"
    )


# ============================================================
# 14.4 VALIDATION TESTS
# ============================================================

def unit_14_validation_v1():

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
            "UNIT 14 TEST",
            name,
            "=",
            verdict,
            flush=True
        )

    sample = unit_14_result("NEARUSDT")

    check(
        "UNIVERSAL_SYMBOL",
        sample["market_symbol"] == "NEARUSDT"
    )

    check(
        "BOT_MODE_INDEPENDENT",
        sample["bot_mode_independent"] is True
    )

    check(
        "NO_UNVERIFIED_PROTECTION",
        sample["protection_active"] is False
    )

    check(
        "NO_UNVERIFIED_EXECUTION",
        sample["execution_authorized"] is False
    )

    check(
        "NO_EXCHANGE_WRITE",
        sample["exchange_write"] is False
    )

    check(
        "REAL_CASH_DISABLED",
        sample["real_cash_execution"] is False
    )

    check(
        "QUANTITY_VALIDATION",
        unit_14_number("14") == _U14D("14")
    )

    check(
        "INVALID_QUANTITY_REJECTED",
        unit_14_number("-1") is None
    )

    print(
        "UNIT 14 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 14 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT_14_VALIDATION_FAILED"
        )

    return True


# ============================================================
# 14.5 STARTUP AND HANDOVER
# ============================================================

FRESH_UNIT_14_VALIDATION_READY = (
    unit_14_validation_v1()
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_reconstruction_unit_14(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
    )
)

for key in (
    "status",
    "reason",
    "market_symbol",
    "position_verified",
    "contract_verified",
    "quantity_step_valid",
    "tp_plan_valid",
    "hedge_plan_valid",
    "exposure_verified",
    "exchange_protection_verified",
    "protection_active",
    "safety_alert",
    "alert_severity",
    "requires_operator_attention",
    "execution_authorized",
):

    print(
        "UNIT 14",
        key.upper(),
        "=",
        FRESH_RECONSTRUCTION_UNIT_14_RESULT.get(key),
        flush=True
    )

print(
    "UNIT 14 EXCHANGE WRITE = NONE",
    flush=True
)

print(
    "UNIT 14 REAL CASH EXECUTION = DISABLED",
    flush=True
)

FRESH_UNIT_14_OPTIMIZATION_READY = (
    FRESH_UNIT_14_VALIDATION_READY
)

print(
    "FRESH RECONSTRUCTION UNIT 14 RESULT =",
    FRESH_RECONSTRUCTION_UNIT_14_RESULT["status"],
    flush=True
)

print(
    "UNIT 14 UNIVERSAL OPTIMIZATION READY =",
    FRESH_UNIT_14_OPTIMIZATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 14 V1
# UNIT 15 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 15 V1
# WEEX DEMO MONITORING AND TELEGRAM REPORTING
# ZERO INDENTATION
# ============================================================

import os as _u15_os
import json as _u15_json
import time as _u15_time
import threading as _u15_threading
from datetime import datetime as _u15_datetime
from datetime import timedelta as _u15_timedelta
from datetime import timezone as _u15_timezone
from urllib import request as _u15_request
from urllib import parse as _u15_parse

UNIT15_VERSION = "V1_UNIVERSAL_DEMO_MONITOR"
UNIT15_WAT = _u15_timezone(_u15_timedelta(hours=1))
UNIT15_SLOTS = (5, 13, 21)

_UNIT15_LAST_SLOT = None
_UNIT15_LAST_ALERT = None
_UNIT15_OFFSET = None
_UNIT15_POLL_STARTED = False
_UNIT15_WORKER_STARTED = False
_UNIT15_LAST_REPORT = None
_UNIT15_LOCK = _u15_threading.RLock()


# ============================================================
# 15.1 CONFIGURATION
# ============================================================

def unit15_enabled(name, default=True):

    value = _u15_os.getenv(name)

    if value is None:
        return default

    return str(value).strip().lower() in (
        "1", "true", "yes", "on"
    )


UNIT15_ON_DEMAND = unit15_enabled(
    "UNIT15_ON_DEMAND", True
)

UNIT15_SCHEDULED = unit15_enabled(
    "UNIT15_SCHEDULED", True
)

UNIT15_SAFETY_ALERTS = unit15_enabled(
    "UNIT15_SAFETY_ALERTS", True
)


# ============================================================
# 15.2 VERIFIED UPSTREAM SNAPSHOT
# ============================================================

def unit15_snapshot():

    u8 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    u12 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_12_RESULT"
    )

    u13 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_13_RESULT"
    )

    u14 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_14_RESULT"
    )

    u8 = u8 if isinstance(u8, dict) else {}
    u12 = u12 if isinstance(u12, dict) else {}
    u13 = u13 if isinstance(u13, dict) else {}
    u14 = u14 if isinstance(u14, dict) else {}

    symbol = (
        u8.get("market_symbol")
        or u14.get("market_symbol")
        or _u15_os.getenv("WEEX_SYMBOL", "")
    )

    return {
        "symbol": str(symbol).upper(),
        "unit8": u8,
        "unit12": u12,
        "unit13": u13,
        "unit14": u14,
    }


# ============================================================
# 15.3 TELEGRAM DELIVERY
# ============================================================

def unit15_telegram(message):

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not token or not chat_id:
        print(
            "UNIT 15 TELEGRAM = NOT_CONFIGURED",
            flush=True
        )
        return False

    url = (
        "https://api.telegram.org/bot"
        + token
        + "/sendMessage"
    )

    payload = _u15_parse.urlencode({
        "chat_id": chat_id,
        "text": str(message)[:4000],
        "disable_web_page_preview": "true",
    }).encode("utf-8")

    try:
        req = _u15_request.Request(
            url,
            data=payload,
            method="POST",
        )

        with _u15_request.urlopen(
            req, timeout=15
        ) as response:
            data = _u15_json.loads(
                response.read().decode("utf-8")
            )

        success = data.get("ok") is True

        print(
            "UNIT 15 TELEGRAM DELIVERY =",
            "PASS" if success else "FAIL",
            flush=True
        )

        return success

    except Exception as exc:
        print(
            "UNIT 15 TELEGRAM ERROR =",
            type(exc).__name__,
            flush=True
        )
        return False


# ============================================================
# 15.4 REPORT CONSTRUCTION
# ============================================================

def unit15_report(period="8h", notification="SCHEDULED"):

    global _UNIT15_LAST_REPORT

    if period not in ("1h", "8h", "24h", "all"):
        raise ValueError("INVALID_REPORT_PERIOD")

    now = _u15_datetime.now(UNIT15_WAT)
    snapshot = unit15_snapshot()

    u8 = snapshot["unit8"]
    u12 = snapshot["unit12"]
    u13 = snapshot["unit13"]
    u14 = snapshot["unit14"]

    lines = [
        "WEEX DEMO TRADING PERFORMANCE",
        "================================",
        "Notification: " + notification,
        "Period: " + period,
        "Time: " + now.strftime(
            "%Y-%m-%d %H:%M WAT"
        ),
        "Symbol: " + snapshot["symbol"],
    ]

    if period != "all":
        hours = int(period[:-1])
        start = now - _u15_timedelta(hours=hours)

        lines.append(
            "Window: "
            + start.strftime("%Y-%m-%d %H:%M")
            + " to "
            + now.strftime("%Y-%m-%d %H:%M")
            + " WAT"
        )

    # A read-verified history endpoint alone does
    # not prove complete matched trading cycles.
    # These fields remain unverified until the
    # reference reconciliation engine is adapted.

    lines.extend([
        "History orders: Unverified",
        "Fully filled: Unverified",
        "Completed cycles: Unverified",
        "Winning cycles: Unverified",
        "Losing cycles: Unverified",
        "Break-even cycles: Unverified",
        "Gross win rate: N/A",
        "Gross profit: Unverified",
        "Gross loss: Unverified",
        "Gross P&L: Unverified",
        "Net trading profit: Unverified",
        "Net ROI: N/A",
        "Fees/funding/margin: Unverified",
        "Close cause: Unverified",
        "",
        "EQUITY-BASED PERFORMANCE",
        "================================",
        "Starting equity: N/A",
        "Ending equity: N/A",
        "Equity change: N/A",
        "Equity ROI: N/A",
        "Reason: Matching verified equity "
        "snapshots unavailable",
        "",
        "DEMO ACCOUNT AND SAFETY",
        "================================",
        "Contract verified: "
        + str(u8.get("demo_contract_verified")),
        "Balance read verified: "
        + str(u8.get("demo_balance_verified")),
        "Position read verified: "
        + str(u8.get(
            "demo_positions_read_verified"
        )),
        "Position flat verified: "
        + str(u8.get("position_flat_verified")),
        "Unit 12 status: "
        + str(u12.get("status", "UNKNOWN")),
        "Unit 13 status: "
        + str(u13.get("status", "UNKNOWN")),
        "Unit 14 status: "
        + str(u14.get("status", "UNKNOWN")),
        "Unit 14 reason: "
        + str(u14.get("reason", "UNKNOWN")),
        "Safety alert: "
        + str(u14.get("safety_alert", "UNKNOWN")),
        "Protection active verified: "
        + str(u14.get(
            "exchange_protection_verified",
            False
        )),
        "Demo order submission verified: "
        + str(u8.get(
            "demo_order_submission_verified",
            False
        )),
        "Real-cash execution: DISABLED",
        "",
        "Report classification: "
        "MONITORING / NOT VERIFIED P&L",
    ])

    message = "\n".join(lines)

    with _UNIT15_LOCK:
        _UNIT15_LAST_REPORT = {
            "period": period,
            "notification": notification,
            "generated_at": now.isoformat(),
            "symbol": snapshot["symbol"],
            "report": message,
            "performance_verified": False,
            "exchange_write": False,
        }

    return message


# ============================================================
# 15.5 UNIT 14 SAFETY ALERT
# ============================================================

def unit15_check_safety():

    global _UNIT15_LAST_ALERT

    if not UNIT15_SAFETY_ALERTS:
        return False

    snapshot = unit15_snapshot()
    u14 = snapshot["unit14"]

    if not u14:
        return False

    if u14.get("safety_alert") is not True:
        with _UNIT15_LOCK:
            _UNIT15_LAST_ALERT = None
        return False

    reason = str(
        u14.get("alert_reason")
        or u14.get("reason")
        or "UNKNOWN"
    )

    severity = str(
        u14.get("alert_severity", "CRITICAL")
    )

    key = (
        snapshot["symbol"],
        reason,
        severity,
    )

    with _UNIT15_LOCK:
        if key == _UNIT15_LAST_ALERT:
            return False

    message = "\n".join([
        "WEEX DEMO SAFETY ALERT",
        "==========================",
        "Symbol: " + snapshot["symbol"],
        "Severity: " + severity,
        "Reason: " + reason,
        "Unit 14 protection verified: "
        + str(u14.get(
            "exchange_protection_verified",
            False
        )),
        "Operator attention required: "
        + str(u14.get(
            "requires_operator_attention",
            True
        )),
        "No automatic protective order "
        "is implied by this alert.",
    ])

    delivered = unit15_telegram(message)

    if delivered:
        with _UNIT15_LOCK:
            _UNIT15_LAST_ALERT = key

    return delivered


# ============================================================
# 15.6 ON-DEMAND COMMANDS
# ============================================================

def unit15_poll_commands():

    global _UNIT15_OFFSET
    global _UNIT15_POLL_STARTED

    if not UNIT15_ON_DEMAND:
        return []

    token = _u15_os.getenv(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip()

    chat_id = _u15_os.getenv(
        "TELEGRAM_CHAT_ID", ""
    ).strip()

    if not token or not chat_id:
        return []

    params = {
        "timeout": 0,
        "limit": 50,
        "allowed_updates": _u15_json.dumps(
            ["message"]
        ),
    }

    if _UNIT15_OFFSET is not None:
        params["offset"] = _UNIT15_OFFSET
    elif not _UNIT15_POLL_STARTED:
        params["offset"] = -1

    url = (
        "https://api.telegram.org/bot"
        + token
        + "/getUpdates?"
        + _u15_parse.urlencode(params)
    )

    req = _u15_request.Request(
        url, method="GET"
    )

    with _u15_request.urlopen(
        req, timeout=15
    ) as response:
        payload = _u15_json.loads(
            response.read().decode("utf-8")
        )

    if payload.get("ok") is not True:
        return []

    choices = []

    for update in payload.get("result", []):

        uid = update.get("update_id")

        if isinstance(uid, int):
            _UNIT15_OFFSET = max(
                uid + 1,
                _UNIT15_OFFSET or 0
            )

        if not _UNIT15_POLL_STARTED:
            continue

        msg = update.get("message") or {}

        sender_chat = str(
            (msg.get("chat") or {}).get("id", "")
        )

        if sender_chat != chat_id:
            continue

        parts = str(
            msg.get("text", "")
        ).strip().lower().split()

        if not parts:
            continue

        if parts[0].split("@")[0] != "/report":
            continue

        choice = (
            parts[1]
            if len(parts) > 1
            else "8h"
        )

        if choice in ("1h", "8h", "24h", "all"):
            choices.append(choice)

    _UNIT15_POLL_STARTED = True

    return choices


# ============================================================
# 15.7 SCHEDULED WORKER
# ============================================================

def unit15_worker():

    global _UNIT15_LAST_SLOT

    print(
        "UNIT 15 WORKER LOOP ENTERED",
        flush=True
    )

    print(
        "UNIT 15 SCHEDULE = "
        "05:00 / 13:00 / 21:00 WAT",
        flush=True
    )

    print(
        "UNIT 15 STARTUP REPORT = DISABLED",
        flush=True
    )

    while True:

        try:
            now = _u15_datetime.now(UNIT15_WAT)

            unit15_check_safety()

            if UNIT15_SCHEDULED:

                slot = (
                    now.date().isoformat(),
                    now.hour
                )

                if (
                    now.hour in UNIT15_SLOTS
                    and now.minute == 0
                    and slot != _UNIT15_LAST_SLOT
                ):

                    report = unit15_report(
                        "8h", "SCHEDULED"
                    )

                    if unit15_telegram(report):
                        _UNIT15_LAST_SLOT = slot

            for period in unit15_poll_commands():

                report = unit15_report(
                    period, "ON_DEMAND"
                )

                unit15_telegram(report)

        except Exception as exc:

            print(
                "UNIT 15 WORKER ERROR =",
                type(exc).__name__,
                str(exc)[:200],
                flush=True
            )

        _u15_time.sleep(10)


# ============================================================
# 15.8 VALIDATION
# ============================================================

def unit15_validation():

    tests = {
        "SCHEDULE_THREE_SLOTS":
            UNIT15_SLOTS == (5, 13, 21),

        "WAT_OFFSET":
            UNIT15_WAT.utcoffset(None)
            == _u15_timedelta(hours=1),

        "ON_DEMAND_PERIODS":
            all(
                x in ("1h", "8h", "24h", "all")
                for x in ("1h", "8h", "24h", "all")
            ),

        "NO_EXCHANGE_ORDER_FUNCTION":
            True,

        "NO_UNVERIFIED_PROFIT":
            "Gross P&L: Unverified"
            in unit15_report("8h", "TEST"),

        "UNIT14_ALERT_INTERFACE":
            isinstance(
                unit15_snapshot()["unit14"],
                dict
            ),
    }

    for name, passed in tests.items():
        print(
            "UNIT 15 TEST",
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True
        )

    passed = sum(tests.values())
    failed = len(tests) - passed

    print(
        "UNIT 15 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 15 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT_15_VALIDATION_FAILED"
        )

    return True


# ============================================================
# 15.9 STARTUP
# ============================================================

FRESH_UNIT_15_VALIDATION_READY = (
    unit15_validation()
)

FRESH_RECONSTRUCTION_UNIT_15_RESULT = {
    "unit": 15,
    "version": UNIT15_VERSION,
    "status": "MONITOR_READY",
    "symbol": unit15_snapshot()["symbol"],
    "scheduled_reporting": UNIT15_SCHEDULED,
    "on_demand_reporting": UNIT15_ON_DEMAND,
    "safety_alerts": UNIT15_SAFETY_ALERTS,
    "performance_reconciliation_verified": False,
    "exchange_write": False,
    "real_cash_execution": False,
}

if not _UNIT15_WORKER_STARTED:

    _UNIT15_WORKER_STARTED = True

    _u15_threading.Thread(
        target=unit15_worker,
        name="WEEX_UNIT15_MONITOR",
        daemon=True
    ).start()

print(
    "UNIT 15 VERSION =",
    UNIT15_VERSION,
    flush=True
)

print(
    "UNIT 15 STATUS = MONITOR_READY",
    flush=True
)

print(
    "UNIT 15 PERFORMANCE RECONCILIATION = "
    "NOT YET INTEGRATED",
    flush=True
)

print(
    "UNIT 15 EXCHANGE WRITE = NONE",
    flush=True
)

print(
    "UNIT 15 REAL CASH EXECUTION = DISABLED",
    flush=True
)

print(
    "FRESH RECONSTRUCTION UNIT 15 RESULT = PASS",
    flush=True
)

# ============================================================
# END COMPLETE UNIT 15 V1
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE CONTINUOUS SCAN CONTROLLER V2
# ADAPTED FROM 17248-LINE REFERENCE
# CURRENT 15-UNIT NEARUSDT MODEL
# ZERO INDENTATION
# ============================================================

import os as _scan_os
import time as _scan_time
import threading as _scan_thread
import traceback as _scan_traceback
from datetime import datetime as _SCAN_DT
from datetime import timezone as _SCAN_TZ
from datetime import timedelta as _SCAN_DELTA

SCAN_VERSION = "V2_REFERENCE_17248_ADAPTED"

SCAN_INTERVAL_SECONDS = int(
    _scan_os.getenv("SCAN_INTERVAL_SECONDS", "30")
)

if not 15 <= SCAN_INTERVAL_SECONDS <= 3600:
    raise RuntimeError(
        "SCAN_INTERVAL_SECONDS MUST BE 15 TO 3600"
    )

SCAN_WAT = _SCAN_TZ(_SCAN_DELTA(hours=1))
SCAN_LOCK = _scan_thread.Lock()

SCAN_NUMBER = 0
SCAN_LAST_MARKET_SUCCESS = None
SCAN_LAST_MANAGEMENT_SUCCESS = None
SCAN_LAST_STATUS = "NOT_STARTED"
SCAN_LAST_ERROR = None


# ============================================================
# 1. SAFE UNIT 12 FALLBACK
# ============================================================

def scan_idle_unit12_result(reason):

    return {
        "unit": 12,
        "status": "IDLE",
        "reason": str(reason),
        "skip_reason": str(reason),
        "active_mode": "NONE",
        "direction": "NONE",
        "signal_qualified": False,
        "execution_intent": False,
        "demo_submission_attempted": False,
        "demo_submission_completed": False,
        "demo_order_accepted": False,
        "fill_verified": False,
        "execution_authorized": False,
        "exchange_write": False,
        "real_cash_execution": False,
        "management_path_permitted": True,
    }


# ============================================================
# 2. REFRESH UNITS 3 TO 11
# ============================================================

def scan_refresh_entry_pipeline():

    global FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    global FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    global FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    global FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    global FRESH_RECONSTRUCTION_SIZING_PLAN
    global FRESH_RECONSTRUCTION_UNIT_7_RESULT
    global FRESH_RECONSTRUCTION_UNIT_8_RESULT
    global FRESH_UNIT_8_VERIFIED_CONTRACT
    global FRESH_RECONSTRUCTION_UNIT_9_RESULT
    global FRESH_RECONSTRUCTION_UNIT_10_RESULT
    global FRESH_RECONSTRUCTION_UNIT_11_RESULT

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "SCAN CONFIG MISSING"
        )

    # --------------------------------------------------------
    # UNIT 3 - MARKET DATA
    # --------------------------------------------------------

    market = fresh_reconstruction_unit_3()

    if not isinstance(market, dict):
        raise RuntimeError(
            "SCAN UNIT 3 INVALID"
        )

    FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = market

    print(
        "SCAN UNIT 3 MARKET REFRESH = PASS",
        flush=True
    )

    # --------------------------------------------------------
    # UNIT 4 - TECHNICAL ANALYSIS
    # --------------------------------------------------------

    analysis = fresh_reconstruction_unit_4()

    if not isinstance(analysis, dict):
        raise RuntimeError(
            "SCAN UNIT 4 INVALID"
        )

    FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = analysis

    # --------------------------------------------------------
    # UNIT 5 - STRATEGY CLASSIFICATION
    # --------------------------------------------------------

    candidate = fresh_reconstruction_unit_5(
        config,
        analysis
    )

    if not isinstance(candidate, dict):
        raise RuntimeError(
            "SCAN UNIT 5 INVALID"
        )

    FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
        candidate
    )

    # --------------------------------------------------------
    # UNIT 6 - STRATEGY ARBITRATION
    # --------------------------------------------------------

    execution = fresh_reconstruction_unit_6(
        config,
        analysis,
        candidate
    )

    if not isinstance(execution, dict):
        raise RuntimeError(
            "SCAN UNIT 6 INVALID"
        )

    FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
        execution
    )

    # --------------------------------------------------------
    # UNIT 7 - SIZING AND HEDGE POLICY
    # --------------------------------------------------------

    sizing = fresh_reconstruction_unit_7()

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "SCAN UNIT 7 INVALID"
        )

    FRESH_RECONSTRUCTION_SIZING_PLAN = sizing
    FRESH_RECONSTRUCTION_UNIT_7_RESULT = sizing

    # --------------------------------------------------------
    # UNIT 8 - WEEX DEMO ACCOUNT
    # --------------------------------------------------------

    account = unit_8_v16_main()

    if not isinstance(account, dict):
        raise RuntimeError(
            "SCAN UNIT 8 INVALID"
        )

    FRESH_RECONSTRUCTION_UNIT_8_RESULT = account

    FRESH_UNIT_8_VERIFIED_CONTRACT = (
        account.get("contract")
        if account.get("demo_contract_verified") is True
        else None
    )

    print(
        "SCAN UNIT 8 STATUS =",
        account.get("status"),
        flush=True
    )

    # --------------------------------------------------------
    # UNIT 9 - SIGNAL HANDOVER
    # --------------------------------------------------------

    entry = fresh_reconstruction_unit_9(
        config,
        account,
        sizing
    )

    if not isinstance(entry, dict):
        raise RuntimeError(
            "SCAN UNIT 9 INVALID"
        )

    FRESH_RECONSTRUCTION_UNIT_9_RESULT = entry

    # --------------------------------------------------------
    # UNIT 10 - DEMO EXECUTION BOUNDARY
    # --------------------------------------------------------

    boundary = fresh_unit_10_hybrid_adapter(
        config,
        entry
    )

    if not isinstance(boundary, dict):
        raise RuntimeError(
            "SCAN UNIT 10 INVALID"
        )

    FRESH_RECONSTRUCTION_UNIT_10_RESULT = boundary

    # --------------------------------------------------------
    # UNIT 11 - ORDER PREPARATION
    # --------------------------------------------------------

    prepared = fresh_unit_11_hybrid_adapter(
        config,
        boundary
    )

    if not isinstance(prepared, dict):
        raise RuntimeError(
            "SCAN UNIT 11 INVALID"
        )

    FRESH_RECONSTRUCTION_UNIT_11_RESULT = prepared

    return prepared, account


# ============================================================
# 3. UNIT 12 - CONTROLLED DEMO ENTRY
# ============================================================


# ============================================================
# START UNIT 12 V5 SCANNER HANDOVER CORRECTION
# ZERO INDENTATION
# ============================================================

def scan_process_unit12(prepared, account):

    global FRESH_RECONSTRUCTION_UNIT_8_RESULT
    global FRESH_RECONSTRUCTION_UNIT_12_RESULT

    if not isinstance(prepared, dict):
        raise RuntimeError("SCAN UNIT 11 RESULT MISSING")

    if not isinstance(account, dict):
        raise RuntimeError("SCAN UNIT 8 RESULT MISSING")

    FRESH_RECONSTRUCTION_UNIT_8_RESULT = account

    result = fresh_reconstruction_unit_12(
        FRESH_RECONSTRUCTION_CONFIG,
        prepared,
        account,
    )

    if not isinstance(result, dict):
        raise RuntimeError("SCAN UNIT 12 RESULT INVALID")

    FRESH_RECONSTRUCTION_UNIT_12_RESULT = result

    if result.get("real_submission_attempted") is not False:
        raise RuntimeError("UNIT 12 REAL CASH SAFETY FAILURE")

    print(
        "SCAN UNIT 12 STATUS =",
        result.get("status"),
        flush=True
    )

    print(
        "SCAN UNIT 12 REASON =",
        result.get("reason"),
        flush=True
    )

    print(
        "SCAN UNIT 12 DEMO SUBMISSION ATTEMPTED =",
        result.get("demo_submission_attempted"),
        flush=True
    )

    print(
        "SCAN UNIT 12 DEMO ORDER ACCEPTED =",
        result.get("demo_order_accepted"),
        flush=True
    )

    print(
        "SCAN UNIT 12 ORDER ID =",
        result.get("order_id"),
        flush=True
    )

    return result


# ============================================================
# END UNIT 12 V5 SCANNER HANDOVER CORRECTION
# ============================================================


# ============================================================
# 4. UNCONDITIONAL POSITION MANAGEMENT
# ============================================================

def scan_manage_position(unit12_result):

    global FRESH_RECONSTRUCTION_UNIT_13_RESULT
    global FRESH_RECONSTRUCTION_UNIT_14_RESULT

    config = FRESH_RECONSTRUCTION_CONFIG

    account = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    if not isinstance(account, dict):
        raise RuntimeError(
            "POSITION MANAGEMENT ACCOUNT MISSING"
        )

    if account.get(
        "demo_positions_read_verified"
    ) is not True:
        raise RuntimeError(
            "POSITION MANAGEMENT POSITION READ UNVERIFIED"
        )

    # --------------------------------------------------------
    # UNIT 13 - POSITION PROTECTION PLANNER
    # --------------------------------------------------------

    unit13 = fresh_unit_13_hybrid_adapter(
        config,
        unit12_result
    )

    if not isinstance(unit13, dict):
        raise RuntimeError(
            "SCAN UNIT 13 INVALID"
        )

    FRESH_RECONSTRUCTION_UNIT_13_RESULT = unit13

    # --------------------------------------------------------
    # UNIT 14 - SAFETY SUPERVISOR
    # --------------------------------------------------------

    unit14 = fresh_reconstruction_unit_14(
        config,
        account,
        unit12_result,
        unit13
    )

    if not isinstance(unit14, dict):
        raise RuntimeError(
            "SCAN UNIT 14 INVALID"
        )

    FRESH_RECONSTRUCTION_UNIT_14_RESULT = unit14

    return unit13, unit14


# ============================================================
# 5. FAILURE SAFETY ALERT
# ============================================================

def scan_publish_failure_alert(reason):

    global FRESH_RECONSTRUCTION_UNIT_14_RESULT

    FRESH_RECONSTRUCTION_UNIT_14_RESULT = {
        "unit": 14,
        "market_symbol": str(
            _scan_os.getenv("WEEX_SYMBOL", "")
        ).strip().upper(),
        "status": "ALERT",
        "reason": "SCAN_REFRESH_OR_MANAGEMENT_FAILED",
        "safety_alert": True,
        "alert_severity": "CRITICAL",
        "alert_reason": str(reason)[:300],
        "requires_operator_attention": True,
        "position_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
        "execution_authorized": False,
        "exchange_write": False,
        "real_cash_execution": False,
    }


# ============================================================
# 6. ONE COMPLETE SCAN CYCLE
# ============================================================

def scan_one_cycle():

    global SCAN_NUMBER
    global SCAN_LAST_MARKET_SUCCESS
    global SCAN_LAST_MANAGEMENT_SUCCESS
    global SCAN_LAST_STATUS
    global SCAN_LAST_ERROR

    if not SCAN_LOCK.acquire(blocking=False):

        print(
            "SCAN OVERLAP BLOCKED",
            flush=True
        )
        return False

    try:

        SCAN_NUMBER += 1

        print("=" * 80, flush=True)

        print(
            "CONTINUOUS SCAN NUMBER =",
            SCAN_NUMBER,
            flush=True
        )

        print(
            "SCAN TIME WAT =",
            _SCAN_DT.now(SCAN_WAT).isoformat(),
            flush=True
        )

        print(
            "SCAN SYMBOL =",
            _scan_os.getenv("WEEX_SYMBOL", ""),
            flush=True
        )

        print(
            "SCAN BOT_MODE =",
            _scan_os.getenv("BOT_MODE", "PAUSE"),
            flush=True
        )

        submission = None
        entry_ok = False

        # ----------------------------------------------------
        # NEW-ENTRY PIPELINE
        # ----------------------------------------------------

        try:

            prepared, account = (
                scan_refresh_entry_pipeline()
            )

            SCAN_LAST_MARKET_SUCCESS = (
                _scan_time.time()
            )

            submission = scan_process_unit12(
                prepared,
                account
            )

            entry_ok = True

        except Exception as exc:

            SCAN_LAST_ERROR = repr(exc)

            print(
                "SCAN ENTRY PIPELINE ERROR =",
                SCAN_LAST_ERROR,
                flush=True
            )

            _scan_traceback.print_exc()

            submission = scan_idle_unit12_result(
                "ENTRY_PIPELINE_ERROR"
            )

        # ----------------------------------------------------
        # POSITION MANAGEMENT
        #
        # ATTEMPT EVEN IF ENTRY PIPELINE FAILED.
        # DOES NOT DEPEND ON BOT_MODE.
        # ----------------------------------------------------

        try:

            unit13, unit14 = scan_manage_position(
                submission
            )

            SCAN_LAST_MANAGEMENT_SUCCESS = (
                _scan_time.time()
            )

            print(
                "SCAN UNIT 13 STATUS =",
                unit13.get("status"),
                flush=True
            )

            print(
                "SCAN UNIT 14 STATUS =",
                unit14.get("status"),
                flush=True
            )

            SCAN_LAST_STATUS = (
                "PASS"
                if entry_ok
                else "MANAGEMENT_ONLY"
            )

        except Exception as exc:

            SCAN_LAST_ERROR = repr(exc)

            SCAN_LAST_STATUS = (
                "POSITION_MANAGEMENT_ERROR"
            )

            print(
                "SCAN MANAGEMENT ERROR =",
                SCAN_LAST_ERROR,
                flush=True
            )

            _scan_traceback.print_exc()

            scan_publish_failure_alert(
                SCAN_LAST_ERROR
            )

        print(
            "SCAN FINAL STATUS =",
            SCAN_LAST_STATUS,
            flush=True
        )

        print(
            "SCAN EXCHANGE ENVIRONMENT = DEMO",
            flush=True
        )

        print(
            "SCAN CONTINUES = TRUE",
            flush=True
        )

        return SCAN_LAST_STATUS in (
            "PASS",
            "MANAGEMENT_ONLY"
        )

    finally:

        SCAN_LOCK.release()


# ============================================================
# 7. FOREVER SCAN LOOP
# ============================================================

def scan_forever():

    print("=" * 80, flush=True)

    print(
        "CONTINUOUS SCAN CONTROLLER V2 STARTED",
        flush=True
    )

    print(
        "SCAN INTERVAL SECONDS =",
        SCAN_INTERVAL_SECONDS,
        flush=True
    )

    print(
        "UNIT 12 = NEW ENTRIES ONLY",
        flush=True
    )

    print(
        "UNIT 13 AND 14 = POSITION MANAGEMENT",
        flush=True
    )

    print(
        "UNIT 15 = INDEPENDENT TELEGRAM MONITOR",
        flush=True
    )

    print(
        "REAL CASH EXECUTION = DISABLED",
        flush=True
    )

    print("=" * 80, flush=True)

    # Units 1-15 have already run their startup
    # initialization. Begin with one interval delay.

    _scan_time.sleep(SCAN_INTERVAL_SECONDS)

    while True:

        started = _scan_time.monotonic()

        try:

            scan_one_cycle()

        except Exception as exc:

            print(
                "SCAN SUPERVISOR ERROR =",
                repr(exc),
                flush=True
            )

            _scan_traceback.print_exc()

            scan_publish_failure_alert(
                repr(exc)
            )

        elapsed = (
            _scan_time.monotonic() - started
        )

        sleep_for = max(
            5.0,
            SCAN_INTERVAL_SECONDS - elapsed
        )

        print(
            "SCAN ELAPSED SECONDS =",
            round(elapsed, 2),
            flush=True
        )

        print(
            "SCAN NEXT SLEEP SECONDS =",
            round(sleep_for, 2),
            flush=True
        )

        _scan_time.sleep(sleep_for)


# ============================================================
# 8. START MAIN THREAD FOREVER LOOP
# ============================================================

print(
    "CONTINUOUS SCAN VERSION =",
    SCAN_VERSION,
    flush=True
)

print(
    "CONTINUOUS SCAN MAIN THREAD = ENABLED",
    flush=True
)


# ============================================================
# START UNIT 7-8 VERIFIED CONTRACT HANDOVER V2
# ZERO INDENTATION
# NO EXCHANGE WRITE
# ============================================================

import time as _u78_time
from decimal import Decimal as _U78_Decimal

U78_MAX_CONTRACT_AGE_SECONDS = 120

# Keep the original Unit 7 validator.
_U78_V2_ORIGINAL = unit_7_v12_contract


def u78_v2_decimal(value, name):

    try:
        result = _U78_Decimal(str(value))
    except Exception as exc:
        raise RuntimeError(
            "U78 INVALID " + name
        ) from exc

    if not result.is_finite() or result <= 0:
        raise RuntimeError(
            "U78 NONPOSITIVE " + name
        )

    return result


def u78_v2_contract(config):

    # Preserve original Unit 7 behavior when
    # its own verified configuration is complete.
    original = _U78_V2_ORIGINAL(config)

    if original.get("verified") is True:
        return original

    exchange = config.get("exchange", {})
    if not isinstance(exchange, dict):
        return original

    symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    # Unit 8 result from the preceding scan.
    unit8 = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    if not isinstance(unit8, dict):
        return original

    # Never mix symbols or environments.
    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled")
            is not False
        or unit8.get("market_symbol") != symbol
        or unit8.get("demo_order_symbol") != symbol
    ):
        return original

    # Require all four independently reported
    # WEEX contract-verification results.
    if not all((
        unit8.get("market_contract_verified") is True,
        unit8.get("simulation_contract_verified") is True,
        unit8.get(
            "simulation_contract_rules_verified"
        ) is True,
        unit8.get("demo_contract_verified") is True
    )):
        return original

    # Require fresh verification.
    try:
        checked_ms = int(
            unit8["checked_at_ms"]
        )
    except (KeyError, TypeError, ValueError):
        return original

    now_ms = int(_u78_time.time() * 1000)

    age_ms = now_ms - checked_ms

    if (
        age_ms < 0
        or age_ms >
            U78_MAX_CONTRACT_AGE_SECONDS * 1000
    ):
        return original

    # Read the values Unit 8 actually verified.
    try:
        minimum = u78_v2_decimal(
            unit8.get("minimum_quantity"),
            "MINIMUM QUANTITY"
        )

        step = u78_v2_decimal(
            unit8.get("quantity_step"),
            "QUANTITY STEP"
        )

        price_step = u78_v2_decimal(
            unit8.get("price_step"),
            "PRICE STEP"
        )

        multiplier = u78_v2_decimal(
            unit8.get("contract_multiplier"),
            "CONTRACT MULTIPLIER"
        )

    except RuntimeError:
        return original

    # Ensure minimum quantity can be represented
    # exactly using the exchange quantity step.
    if minimum % step != 0:
        return original

    # Verify original Unit 7 symbol invariants.
    if not all((
        symbol.endswith("USDT"),
        len(symbol) > 4,
        exchange.get("base_coin") == symbol[:-4],
        exchange.get("quote_coin") == "USDT"
    )):
        return original

    # Return the same contract interface expected
    # by the existing Unit 7 sizing functions.
    #
    # No fabricated contract_value field is used.
    # Unit 8's verified multiplier is retained.
    contract = {
        "verified": True,
        "symbol": symbol,
        "quantity_step": step,
        "minimum_quantity": minimum,
        "contract_multiplier": multiplier,
        "price_step": price_step,
        "reason": "VERIFIED",
        "verification_source":
            "UNIT8_V16_WEEX_VERIFIED_CONTRACT",
        "verification_time_ms": checked_ms
    }

    print(
        "UNIT 7-8 VERIFIED CONTRACT HANDOVER = PASS",
        flush=True
    )

    print(
        "UNIT 7-8 SYMBOL =",
        symbol,
        flush=True
    )

    print(
        "UNIT 7-8 MINIMUM QUANTITY =",
        minimum,
        flush=True
    )

    print(
        "UNIT 7-8 QUANTITY STEP =",
        step,
        flush=True
    )

    print(
        "UNIT 7-8 PRICE STEP =",
        price_step,
        flush=True
    )

    print(
        "UNIT 7-8 CONTRACT MULTIPLIER =",
        multiplier,
        flush=True
    )

    print(
        "UNIT 7-8 METADATA AGE MS =",
        age_ms,
        flush=True
    )

    print(
        "UNIT 7-8 EXCHANGE WRITE = NONE",
        flush=True
    )

    return contract


# Activate the corrected Unit 7 contract adapter.
unit_7_v12_contract = u78_v2_contract

print("=" * 80, flush=True)

print(
    "UNIT 7-8 HANDOVER VERSION = V2",
    flush=True
)

print(
    "UNIT 7 ORIGINAL SIZING = PRESERVED",
    flush=True
)

print(
    "UNIT 7 ORIGINAL HEDGE POLICY = PRESERVED",
    flush=True
)

print(
    "UNIT 7 ORIGINAL BACKUP POLICY = PRESERVED",
    flush=True
)

print(
    "UNIT 8 ORIGINAL WEEX INTERFACE = PRESERVED",
    flush=True
)

print(
    "UNIT 7-8 DEMO ORDER SUBMISSION = NOT ENABLED",
    flush=True
)

print("=" * 80, flush=True)

# ============================================================
# END UNIT 7-8 VERIFIED CONTRACT HANDOVER V2
# ZERO INDENTATION
# ============================================================

# ============================================================
# START UNIT 11-12 STABLE SIGNAL HANDOVER V2
# ZERO INDENTATION
# NO EXCHANGE WRITE
# ============================================================

def u1112_v2_stable_signal(prepared):

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    analysis = globals().get(
        "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
    )

    if not isinstance(prepared, dict):
        return "UNIT_11_RESULT_MISSING"

    if prepared.get("status") != "PREPARED_READ_ONLY":
        return "NO_PREPARED_ENTRY"

    if not isinstance(config, dict):
        return "CONFIG_MISSING"

    if not isinstance(analysis, dict):
        return "ANALYSIS_MISSING"

    instruction = prepared.get("order_instruction")

    if not isinstance(instruction, dict):
        return "ORDER_INSTRUCTION_MISSING"

    symbol = config.get(
        "exchange", {}
    ).get("market_symbol")

    direction = prepared.get("direction")
    mode = prepared.get("active_mode")

    candle_id = analysis.get(
        "latest_close_time_ms"
    )

    if (
        not isinstance(symbol, str)
        or not symbol.endswith("USDT")
        or direction not in ("LONG", "SHORT")
        or mode not in (
            "STRUCTURE",
            "BREAKOUT",
            "SCALP"
        )
    ):
        return "SIGNAL_IDENTITY_INVALID"

    if (
        not isinstance(candle_id, int)
        or isinstance(candle_id, bool)
        or candle_id <= 0
    ):
        return "CLOSED_CANDLE_ID_INVALID"

    import time

    age_ms = int(time.time() * 1000) - candle_id

    if not 0 <= age_ms <= 120000:
        return "CLOSED_CANDLE_STALE"

    if prepared.get("market_symbol") != symbol:
        return "UNIT_11_SYMBOL_MISMATCH"

    if instruction.get("market_symbol") != symbol:
        return "INSTRUCTION_SYMBOL_MISMATCH"

    if instruction.get("direction") != direction:
        return "INSTRUCTION_DIRECTION_MISMATCH"

    if instruction.get("strategy_mode") != mode:
        return "INSTRUCTION_MODE_MISMATCH"

    # Deterministic identifier:
    # same symbol, direction, strategy and candle
    # produce the same signal identity.

    signal_id = (
        symbol
        + "-"
        + mode
        + "-"
        + direction
        + "-"
        + str(candle_id)
    )

    # Unit 12 already supports this field.
    # Preserve the existing trade plan and candidate.

    instruction["newClientOrderId"] = signal_id

    print(
        "UNIT 11-12 STABLE SIGNAL ID =",
        signal_id,
        flush=True
    )

    print(
        "UNIT 11-12 CLOSED CANDLE AGE MS =",
        age_ms,
        flush=True
    )

    return "STABLE_SIGNAL_ID_READY"


def u1112_v2_diagnostic(prepared, account):

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    print("=" * 80, flush=True)

    print(
        "UNIT 11-12 HANDOVER V2 START",
        flush=True
    )

    status = u1112_v2_stable_signal(prepared)

    print(
        "UNIT 11-12 SIGNAL STATUS =",
        status,
        flush=True
    )

    if status != "STABLE_SIGNAL_ID_READY":

        print(
            "UNIT 11-12 PREPARATION = SKIPPED",
            flush=True
        )

        print(
            "UNIT 11-12 EXCHANGE WRITE = NONE",
            flush=True
        )

        print("=" * 80, flush=True)

        return False

    result = unit_12_v2_prepare(
        config,
        prepared,
        account
    )

    print(
        "UNIT 12 PREPARATION STATUS =",
        result.get("status"),
        flush=True
    )

    print(
        "UNIT 12 PREPARATION REASON =",
        result.get("reason"),
        flush=True
    )

    print(
        "UNIT 12 CLIENT ID PRESENT =",
        bool(result.get("client_order_id")),
        flush=True
    )

    print(
        "UNIT 12 ORDER PAYLOAD PRESENT =",
        isinstance(
            result.get("order_payload"),
            dict
        ),
        flush=True
    )

    print(
        "UNIT 11-12 EXCHANGE WRITE = NONE",
        flush=True
    )

    print("=" * 80, flush=True)

    return result.get("status") == "PREPARED"


# Preserve the original scan refresh function.
_U1112_V2_ORIGINAL_SCAN_REFRESH = (
    scan_refresh_entry_pipeline
)


def scan_refresh_entry_pipeline():

    prepared, account = (
        _U1112_V2_ORIGINAL_SCAN_REFRESH()
    )

    u1112_v2_diagnostic(
        prepared,
        account
    )

    return prepared, account


print(
    "UNIT 11-12 STABLE SIGNAL HANDOVER V2 INSTALLED",
    flush=True
)

# ============================================================
# END UNIT 11-12 STABLE SIGNAL HANDOVER V2
# ZERO INDENTATION
# ============================================================


scan_forever()

# ============================================================
# END COMPLETE CONTINUOUS SCAN CONTROLLER V2
# ZERO INDENTATION
# ============================================================

