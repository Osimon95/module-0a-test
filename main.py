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
# START UNIT 8 V12 — ZERO INDENTATION
# UNIVERSAL WEEX MARKET + DEMO READ VERIFICATION
# PRESERVES UNIT 7 V12 HANDOVER
# NO ORDER SUBMISSION / NO EXCHANGE WRITES
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

from urllib.parse import urlencode
from decimal import Decimal, InvalidOperation, ROUND_FLOOR


UNIT_8_V12_BASE_URL = "https://api-contract.weex.com"

UNIT_8_V12_PUBLIC_PATHS = frozenset({
    "/capi/v3/market/exchangeInfo",
    "/capi/v3/market/apiTradingSymbols",
})

UNIT_8_V12_PRIVATE_PATHS = frozenset({
    "/capi/v3/sim/balance",
    "/capi/v3/sim/position/allPosition",
    "/capi/v3/sim/order/history",
    "/capi/v3/account/accountConfig",
})


# ============================================================
# 8.1 DECIMAL AND RESPONSE HELPERS
# ============================================================

def unit_8_v12_number(value, label, allow_zero=False):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 8 BOOLEAN INVALID: " + label)

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError("UNIT 8 NUMBER INVALID: " + label) from exc

    if not number.is_finite():
        raise RuntimeError("UNIT 8 NONFINITE: " + label)

    if number < 0 or (number == 0 and not allow_zero):
        raise RuntimeError("UNIT 8 RANGE INVALID: " + label)

    return number


def unit_8_v12_text(value):

    number = Decimal(str(value))

    if number == 0:
        return "0"

    return format(number.normalize(), "f")


def unit_8_v12_unwrap(payload):

    if not isinstance(payload, (dict, list)):
        raise RuntimeError("UNIT 8 RESPONSE STRUCTURE INVALID")

    if isinstance(payload, list):
        return payload

    code = payload.get("code")

    if code is not None and str(code) not in ("0", "200", "00000"):
        raise RuntimeError("UNIT 8 WEEX RESPONSE CODE " + str(code))

    if "data" in payload:
        return payload["data"]

    return payload


# ============================================================
# 8.2 RESTRICTED PUBLIC AND PRIVATE GET REQUESTS
# ============================================================

def unit_8_v12_public_get(path, params=None):

    if path not in UNIT_8_V12_PUBLIC_PATHS:
        raise RuntimeError("UNIT 8 PUBLIC PATH BLOCKED")

    query = urlencode(params or {})
    target = path + ("?" + query if query else "")

    request = urllib.request.Request(
        UNIT_8_V12_BASE_URL + target,
        headers={"Accept": "application/json"},
        method="GET"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.getcode() != 200:
                raise RuntimeError("UNIT 8 PUBLIC HTTP STATUS INVALID")
            payload = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as exc:
        raise RuntimeError("UNIT 8 PUBLIC HTTP " + str(exc.code)) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("UNIT 8 PUBLIC NETWORK FAILURE") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("UNIT 8 PUBLIC JSON INVALID") from exc

    return unit_8_v12_unwrap(payload)


def unit_8_v12_private_get(path, params=None):

    if path not in UNIT_8_V12_PRIVATE_PATHS:
        raise RuntimeError("UNIT 8 PRIVATE PATH BLOCKED")

    key = os.getenv("WEEX_API_KEY") or os.getenv("API_KEY")
    secret = os.getenv("WEEX_API_SECRET") or os.getenv("API_SECRET")
    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError("UNIT 8 API CREDENTIALS MISSING")

    query = urlencode(params or {})
    target = path + ("?" + query if query else "")
    timestamp = str(int(time.time() * 1000))
    message = timestamp + "GET" + target

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        UNIT_8_V12_BASE_URL + target,
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": phrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US",
        },
        method="GET"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.getcode() != 200:
                raise RuntimeError("UNIT 8 PRIVATE HTTP STATUS INVALID")
            payload = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8")[:300]
        except Exception:
            pass
        raise RuntimeError(
            "UNIT 8 PRIVATE HTTP " + str(exc.code) + " " + body
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("UNIT 8 PRIVATE NETWORK FAILURE") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("UNIT 8 PRIVATE JSON INVALID") from exc

    return unit_8_v12_unwrap(payload)


# ============================================================
# 8.3 UNIVERSAL MARKET / DEMO SYMBOL CANDIDATE
# ============================================================

def unit_8_v12_symbol(config):

    exchange = config.get("exchange", {})
    if not isinstance(exchange, dict):
        raise RuntimeError("UNIT 8 EXCHANGE CONFIG INVALID")

    symbol = str(exchange.get("market_symbol", "")).strip().upper()

    if not re.fullmatch(r"[A-Z0-9]{2,20}USDT", symbol):
        raise RuntimeError("UNIT 8 MARKET SYMBOL INVALID")

    base_coin = symbol[:-4]
    candidate = base_coin + "SUSDT"

    configured = exchange.get("demo_order_symbol")

    if configured != candidate:
        raise RuntimeError("UNIT 8 DEMO SYMBOL CANDIDATE MISMATCH")

    return symbol, candidate


# ============================================================
# 8.4 LIVE/API CONTRACT METADATA
# ============================================================

def unit_8_v12_contract_info(symbol):

    raw = unit_8_v12_public_get(
        "/capi/v3/market/exchangeInfo",
        {"symbol": symbol}
    )

    if not isinstance(raw, dict):
        raise RuntimeError("UNIT 8 EXCHANGE INFO INVALID")

    symbols = raw.get("symbols")

    if not isinstance(symbols, list):
        raise RuntimeError("UNIT 8 EXCHANGE SYMBOL LIST MISSING")

    matches = [
        item for item in symbols
        if isinstance(item, dict) and item.get("symbol") == symbol
    ]

    if len(matches) != 1:
        raise RuntimeError("UNIT 8 UNIQUE MARKET CONTRACT NOT FOUND")

    item = matches[0]

    if (
        item.get("baseAsset") != symbol[:-4]
        or item.get("quoteAsset") != "USDT"
        or item.get("marginAsset") != "USDT"
        or item.get("contractType") not in (
            "PERPETUAL", "TRADIFI_PERPETUAL"
        )
    ):
        raise RuntimeError("UNIT 8 MARKET CONTRACT ASSET/TYPE MISMATCH")

    forward_flag = item.get("forwardContractFlag")
    if forward_flag is False:
        raise RuntimeError("UNIT 8 CONTRACT IS NOT USDT MARGINED")

    quantity_precision = item.get("quantityPrecision")
    price_precision = item.get("pricePrecision")

    if (
        type(quantity_precision) is not int
        or type(price_precision) is not int
        or not 0 <= quantity_precision <= 18
        or not 0 <= price_precision <= 18
    ):
        raise RuntimeError("UNIT 8 CONTRACT PRECISION INVALID")

    minimum = unit_8_v12_number(
        item.get("minOrderSize"), "MINIMUM BASE QUANTITY"
    )
    contract_value = unit_8_v12_number(
        item.get("contractVal"), "CONTRACT VALUE"
    )
    minimum_leverage = unit_8_v12_number(
        item.get("minLeverage"), "MINIMUM LEVERAGE"
    )
    maximum_leverage = unit_8_v12_number(
        item.get("maxLeverage"), "MAXIMUM LEVERAGE"
    )

    if minimum_leverage > maximum_leverage:
        raise RuntimeError("UNIT 8 CONTRACT LEVERAGE RANGE INVALID")

    maximum_quantity = None
    if item.get("maxOrderSize") is not None:
        maximum_quantity = unit_8_v12_number(
            item["maxOrderSize"], "MAXIMUM ORDER QUANTITY"
        )

    quantity_step = Decimal("1").scaleb(-quantity_precision)
    price_step = Decimal("1").scaleb(-price_precision)

    if minimum % quantity_step != 0:
        raise RuntimeError("UNIT 8 MINIMUM QUANTITY NOT STEP ALIGNED")

    return {
        "symbol": symbol,
        "base_asset": item["baseAsset"],
        "quote_asset": item["quoteAsset"],
        "margin_asset": item["marginAsset"],
        "contract_type": item["contractType"],
        "forward_contract_flag": forward_flag,
        "minimum_quantity": unit_8_v12_text(minimum),
        "maximum_quantity": (
            unit_8_v12_text(maximum_quantity)
            if maximum_quantity is not None else None
        ),
        "quantity_precision": quantity_precision,
        "price_precision": price_precision,
        "quantity_step": unit_8_v12_text(quantity_step),
        "price_step": unit_8_v12_text(price_step),
        "contract_value": unit_8_v12_text(contract_value),
        "minimum_leverage": unit_8_v12_text(minimum_leverage),
        "maximum_leverage": unit_8_v12_text(maximum_leverage),
        "market_contract_verified": True,
        "source": "/capi/v3/market/exchangeInfo",
    }


def unit_8_v12_api_symbol_check(symbol):

    raw = unit_8_v12_public_get(
        "/capi/v3/market/apiTradingSymbols"
    )

    if not isinstance(raw, list) or not all(
        isinstance(item, str) for item in raw
    ):
        raise RuntimeError("UNIT 8 API TRADING SYMBOL LIST INVALID")

    return symbol in raw


# ============================================================
# 8.5 DEMO BALANCE / POSITIONS / HISTORY
# ============================================================

def unit_8_v12_balance(raw):

    if isinstance(raw, dict):
        raw = [raw]

    if not isinstance(raw, list):
        raise RuntimeError("UNIT 8 DEMO BALANCE INVALID")

    matches = [
        item for item in raw
        if isinstance(item, dict)
        and str(item.get("asset", "")).upper() == "SUSDT"
    ]

    if len(matches) != 1:
        raise RuntimeError("UNIT 8 SUSDT BALANCE NOT UNIQUE")

    row = matches[0]
    available = unit_8_v12_number(
        row.get("availableBalance"),
        "DEMO AVAILABLE BALANCE",
        allow_zero=True
    )

    return {
        "asset": "SUSDT",
        "available_balance": unit_8_v12_text(available),
        "raw": row,
        "verified": True,
    }


def unit_8_v12_positions(raw, demo_symbol):

    if isinstance(raw, dict):
        raw = [raw]

    if not isinstance(raw, list):
        raise RuntimeError("UNIT 8 DEMO POSITIONS INVALID")

    totals = {
        "LONG": Decimal("0"),
        "SHORT": Decimal("0"),
    }
    positions = []

    for item in raw:
        if not isinstance(item, dict):
            raise RuntimeError("UNIT 8 POSITION RECORD INVALID")

        item_symbol = str(item.get("symbol", "")).upper()

        if item_symbol != demo_symbol:
            continue

        quantity_field = next(
            (
                key for key in ("size", "total", "holdVol")
                if item.get(key) is not None
            ),
            None
        )

        if quantity_field is None:
            raise RuntimeError("UNIT 8 POSITION QUANTITY MISSING")

        quantity = unit_8_v12_number(
            item[quantity_field],
            "DEMO POSITION QUANTITY",
            allow_zero=True
        )

        if quantity == 0:
            continue

        sides = {
            str(item[key]).upper()
            for key in ("positionSide", "holdSide", "side")
            if item.get(key) is not None
            and str(item[key]).upper() in ("LONG", "SHORT")
        }

        if len(sides) != 1:
            raise RuntimeError("UNIT 8 POSITION SIDE AMBIGUOUS")

        side = next(iter(sides))
        totals[side] += quantity

        positions.append({
            "symbol": item_symbol,
            "positionSide": side,
            "size": unit_8_v12_text(quantity),
            "leverage": item.get("leverage"),
            "position_id": item.get("id"),
            "read_only": True,
        })

    return positions, {
        side: unit_8_v12_text(quantity)
        for side, quantity in totals.items()
    }


def unit_8_v12_history_evidence(raw, demo_symbol):

    if isinstance(raw, dict):
        raw = [raw]

    if not isinstance(raw, list):
        raise RuntimeError("UNIT 8 DEMO ORDER HISTORY INVALID")

    matching = [
        item for item in raw
        if isinstance(item, dict)
        and str(item.get("symbol", "")).upper() == demo_symbol
    ]

    executed = []
    for item in matching:
        filled = False
        if item.get("executedQty") is not None:
            try:
                filled = (
                    unit_8_v12_number(
                        item["executedQty"],
                        "HISTORY EXECUTED QUANTITY",
                        allow_zero=True
                    ) > 0
                )
            except RuntimeError:
                filled = False

        if filled or str(item.get("status", "")).upper() in (
            "FILLED", "PARTIALLY_FILLED"
        ):
            executed.append(item)

    sides = {
        str(item.get("positionSide", "")).upper()
        for item in executed
        if str(item.get("positionSide", "")).upper()
        in ("LONG", "SHORT")
    }

    return {
        "history_read_verified": True,
        "matching_demo_symbol_records": len(matching),
        "executed_demo_symbol_records": len(executed),
        "observed_demo_symbol": bool(matching),
        "long_side_filled": "LONG" in sides,
        "short_side_filled": "SHORT" in sides,
        "dual_side_history_evidence": (
            "LONG" in sides and "SHORT" in sides
        ),
    }



# ============================================================
# 8.6 BASE-ASSET ORDER SIZE PREVIEW
# ============================================================

def unit_8_v12_size_preview(
    margin_usdt,
    leverage,
    mark_price,
    contract,
):

    margin = unit_8_v12_number(margin_usdt, "ENTRY MARGIN")
    leverage = unit_8_v12_number(leverage, "LEVERAGE")
    price = unit_8_v12_number(mark_price, "MARK PRICE")

    minimum_leverage = Decimal(contract["minimum_leverage"])
    maximum_leverage = Decimal(contract["maximum_leverage"])

    if not minimum_leverage <= leverage <= maximum_leverage:
        raise RuntimeError("UNIT 8 LEVERAGE OUTSIDE CONTRACT LIMITS")

    step = Decimal(contract["quantity_step"])
    minimum = Decimal(contract["minimum_quantity"])
    contract_value = Decimal(contract["contract_value"])

    # WEEX demo Place Order quantity is sent in base-asset units.
    # Therefore: base quantity = USDT notional / mark price.
    # contract_value is reported for contract-count conversion only;
    # it must not be applied a second time to base-asset quantity.

    notional = margin * leverage
    raw_base_quantity = notional / price

    base_quantity = (
        (raw_base_quantity / step).to_integral_value(
            rounding=ROUND_FLOOR
        ) * step
    )

    half_quantity = base_quantity / Decimal("2")

    minimum_valid = (
        base_quantity >= minimum
        and base_quantity > 0
        and base_quantity % step == 0
    )

    half_valid = (
        half_quantity >= minimum
        and half_quantity % step == 0
    )

    maximum = (
        Decimal(contract["maximum_quantity"])
        if contract.get("maximum_quantity") is not None
        else None
    )

    maximum_valid = (
        maximum is None or base_quantity <= maximum
    )

    required_margin_for_entry = (
        minimum * price / leverage
    )

    required_margin_for_two_valid_halves = (
        (minimum * Decimal("2")) * price / leverage
    )

    return {
        "margin_usdt": unit_8_v12_text(margin),
        "leverage": unit_8_v12_text(leverage),
        "mark_price": unit_8_v12_text(price),
        "notional_usdt": unit_8_v12_text(notional),
        "raw_base_quantity": unit_8_v12_text(raw_base_quantity),
        "order_quantity_base_asset": unit_8_v12_text(base_quantity),
        "half_quantity_base_asset": unit_8_v12_text(half_quantity),
        "quantity_step": contract["quantity_step"],
        "minimum_quantity": contract["minimum_quantity"],
        "contract_value_metadata_only": unit_8_v12_text(contract_value),
        "minimum_quantity_valid": minimum_valid,
        "maximum_quantity_valid": maximum_valid,
        "hedge_half_quantity_valid": half_valid,
        "initial_order_quantity_valid": (
            minimum_valid and maximum_valid
        ),
        "minimum_margin_for_entry_usdt": (
            unit_8_v12_text(required_margin_for_entry)
        ),
        "minimum_margin_for_two_valid_hedge_halves_usdt": (
            unit_8_v12_text(required_margin_for_two_valid_halves)
        ),
        "quantity_unit": "BASE_ASSET",
        "preview_only": True,
    }


# ============================================================
# 8.7 MAIN UNIT 8 V12
# ============================================================

def unit_8_v12_main():

    config = globals().get("FRESH_RECONSTRUCTION_CONFIG")
    unit7 = globals().get("FRESH_RECONSTRUCTION_UNIT_7_RESULT")

    if unit7 is None:
        unit7 = globals().get("FRESH_RECONSTRUCTION_SIZING_PLAN")

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 8 UNIT 2 CONFIG MISSING")

    if not isinstance(unit7, dict):
        raise RuntimeError("UNIT 8 UNIT 7 HANDOVER MISSING")

    safety = config.get("safety", {})

    if (
        config.get("execution_environment") != "DEMO"
        or config.get("real_cash_execution_enabled") is not False
        or safety.get("real_order_submission_enabled") is not False
        or unit7.get("exchange_write") is not False
    ):
        raise RuntimeError("UNIT 8 DEMO SAFETY GATE FAILED")

    symbol, demo_candidate = unit_8_v12_symbol(config)

    if unit7.get("symbol") != symbol:
        raise RuntimeError("UNIT 8 UNIT 7 SYMBOL MISMATCH")

    direction = unit7.get("direction")

    result = {
        "unit": 8,
        "version": "V12_UNIVERSAL_DEMO_READ_VERIFY",
        "symbol": symbol,
        "market_symbol": symbol,
        "demo_order_symbol": demo_candidate,
        "demo_symbol_candidate": demo_candidate,
        "active_mode": unit7.get("active_mode"),
        "direction": direction,
        "execution_intent": unit7.get("execution_intent") is True,

        "market_contract_verified": False,
        "api_trading_symbol_verified": False,
        "demo_symbol_verified": False,
        "demo_contract_verified": False,
        "contract_precision_verified": False,
        "contract_value_verified": False,

        "demo_balance_verified": False,
        "demo_positions_verified": False,
        "demo_order_history_verified": False,
        "account_config_verified": False,
        "account_can_trade": None,
        "account_dual_side_enabled": None,
        "demo_dual_side_mode_verified": False,

        "position_flat_verified": False,
        "positions": [],
        "long_position_quantity": "0",
        "short_position_quantity": "0",

        "available_balance": None,
        "account_equity": None,
        "committed_margin": None,

        "minimum_quantity": None,
        "quantity_step": None,
        "price_step": None,
        "contract_multiplier": None,
        "size_preview": None,
        "verified_entry_sizing": None,

        "trade_plan_ready": False,
        "demo_order_permission_verified": False,
        "execution_authorized": False,
        "real_cash_execution_enabled": False,
        "exchange_write": False,
        "read_only": True,
        "status": "BLOCKED",
        "reason": "VERIFICATION_PENDING",
        "checked_at_ms": int(time.time() * 1000),
    }

    try:
        # A. Verify selected live/API market contract.
        contract = unit_8_v12_contract_info(symbol)
        result["contract"] = contract
        result["market_contract_verified"] = True
        result["contract_precision_verified"] = True
        result["contract_value_verified"] = True
        result["minimum_quantity"] = contract["minimum_quantity"]
        result["quantity_step"] = contract["quantity_step"]
        result["price_step"] = contract["price_step"]
        result["contract_multiplier"] = contract["contract_value"]

        # B. Verify public API trading eligibility.
        result["api_trading_symbol_verified"] = (
            unit_8_v12_api_symbol_check(symbol)
        )

        # C. Read demo balance.
        balance = unit_8_v12_balance(
            unit_8_v12_private_get("/capi/v3/sim/balance")
        )
        result["balance"] = balance
        result["demo_balance_verified"] = True
        result["available_balance"] = balance["available_balance"]

        raw_balance = balance["raw"]

        if raw_balance.get("equity") is not None:
            result["account_equity"] = unit_8_v12_text(
                unit_8_v12_number(
                    raw_balance["equity"],
                    "ACCOUNT EQUITY",
                    allow_zero=True
                )
            )

        for field in ("usedMargin", "marginUsed", "positionMargin"):
            if raw_balance.get(field) is not None:
                result["committed_margin"] = unit_8_v12_text(
                    unit_8_v12_number(
                        raw_balance[field],
                        "COMMITTED MARGIN",
                        allow_zero=True
                    )
                )
                break

        # D. Read demo positions. Only the derived demo symbol counts.
        positions, totals = unit_8_v12_positions(
            unit_8_v12_private_get(
                "/capi/v3/sim/position/allPosition"
            ),
            demo_candidate
        )
        result["positions"] = positions
        result["demo_positions_verified"] = True
        result["long_position_quantity"] = totals["LONG"]
        result["short_position_quantity"] = totals["SHORT"]
        result["position_flat_verified"] = len(positions) == 0

        # E. Read demo order history without assuming an empty result
        # proves that the candidate symbol is listed.
        history = unit_8_v12_private_get(
            "/capi/v3/sim/order/history",
            {"limit": 500, "page": 0}
        )
        history_evidence = unit_8_v12_history_evidence(
            history, demo_candidate
        )
        result["demo_order_history_verified"] = True
        result["demo_history_evidence"] = history_evidence

        result["demo_symbol_verified"] = bool(
            positions or history_evidence["observed_demo_symbol"]
        )
        result["demo_contract_verified"] = bool(
            result["market_contract_verified"]
            and result["demo_symbol_verified"]
        )

        # F. Read account configuration, but do not mislabel it as
        # proof that the demo account itself is in hedge mode.
        account = unit_8_v12_private_get(
            "/capi/v3/account/accountConfig"
        )

        if not isinstance(account, dict):
            raise RuntimeError("UNIT 8 ACCOUNT CONFIG INVALID")

        dual = account.get("dualSidePosition")
        if type(dual) is not bool:
            raise RuntimeError("UNIT 8 ACCOUNT DUAL-SIDE FIELD INVALID")

        result["account_config_verified"] = True
        result["account_dual_side_enabled"] = dual

        can_trade = account.get("canTrade")
        result["account_can_trade"] = (
            can_trade if type(can_trade) is bool else None
        )

        both_open_sides = (
            Decimal(totals["LONG"]) > 0
            and Decimal(totals["SHORT"]) > 0
        )

        result["demo_dual_side_mode_verified"] = bool(
            both_open_sides
            or history_evidence["dual_side_history_evidence"]
        )

        # G. Use the actual Unit 3 mark-price field ("price").
        market = globals().get(
            "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
        )
        if not isinstance(market, dict):
            market = globals().get(
                "FRESH_RECONSTRUCTION_UNIT_3_RESULT"
            )

        mark_price = None
        if isinstance(market, dict) and market.get("symbol") == symbol:
            mark_price = market.get("price", market.get("mark_price"))

        # Use Unit 7's selected margin/leverage, preserving its handover.
        margin = unit7.get("entry_margin_usdt")
        leverage = unit7.get("leverage")

        if margin is None:
            margin = config.get("initial_entry_margin_usdt")

        if leverage is None:
            strategy = config.get("strategy", {})
            leverage_key = (
                "long_leverage" if direction == "LONG"
                else "short_leverage"
            )
            leverage = strategy.get(leverage_key)

        if (
            direction in ("LONG", "SHORT")
            and mark_price is not None
            and margin is not None
            and leverage is not None
        ):
            preview = unit_8_v12_size_preview(
                margin,
                leverage,
                mark_price,
                contract
            )
            result["size_preview"] = preview
            result["verified_entry_sizing"] = preview

        # H. Read-only verification status. No demo order is submitted.
        if not result["demo_symbol_verified"]:
            result["status"] = "READ_COMPLETE"
            result["reason"] = (
                "DEMO_SYMBOL_CANDIDATE_NOT_OBSERVED_IN_POSITIONS_OR_HISTORY"
            )
        elif not result["demo_dual_side_mode_verified"]:
            result["status"] = "READ_COMPLETE"
            result["reason"] = (
                "DEMO_SYMBOL_OBSERVED_BUT_DEMO_HEDGE_MODE_NOT_PROVEN"
            )
        elif result["account_can_trade"] is not True:
            result["status"] = "READ_COMPLETE"
            result["reason"] = (
                "DEMO_SYMBOL_AND_HEDGE_EVIDENCE_FOUND_ACCOUNT_TRADE_PERMISSION_UNVERIFIED"
            )
        else:
            result["status"] = "READ_COMPLETE"
            result["reason"] = (
                "READ_VERIFICATION_COMPLETE_ORDER_PERMISSION_NOT_TESTED"
            )

    except (
        RuntimeError,
        ValueError,
        KeyError,
        TypeError
    ) as exc:
        result["status"] = "READ_BLOCKED"
        result["reason"] = str(exc)

    # Unit 8 is deliberately read-only. Unit 12 owns new-entry gating.
    result["trade_plan_ready"] = False
    result["demo_order_permission_verified"] = False
    result["execution_authorized"] = False
    result["exchange_write"] = False
    result["real_cash_execution_enabled"] = False
    result["read_only"] = True

    print("=" * 76, flush=True)
    print("UNIT 8 V12 MARKET SYMBOL =", symbol, flush=True)
    print("UNIT 8 V12 DEMO SYMBOL CANDIDATE =", demo_candidate, flush=True)

    for field in (
        "market_contract_verified",
        "api_trading_symbol_verified",
        "demo_symbol_verified",
        "demo_contract_verified",
        "contract_precision_verified",
        "contract_value_verified",
        "demo_balance_verified",
        "demo_positions_verified",
        "demo_order_history_verified",
        "account_config_verified",
        "account_can_trade",
        "account_dual_side_enabled",
        "demo_dual_side_mode_verified",
        "position_flat_verified",
        "available_balance",
        "minimum_quantity",
        "quantity_step",
        "price_step",
        "contract_multiplier",
        "status",
        "reason",
    ):
        print("UNIT 8", field.upper(), "=", result.get(field), flush=True)

    if result.get("size_preview") is not None:
        print(
            "UNIT 8 VERIFIED BASE-ASSET SIZE PREVIEW =",
            result["size_preview"],
            flush=True
        )

    print("UNIT 8 EXECUTION AUTHORIZED = False", flush=True)
    print("UNIT 8 EXCHANGE WRITE = NONE", flush=True)
    print("=" * 76, flush=True)

    return result


# ============================================================
# 8.8 OFFLINE VALIDATION
# ============================================================

def unit_8_v12_tests():

    config = {
        "exchange": {
            "market_symbol": "NEARUSDT",
            "demo_order_symbol": "NEARSUSDT",
        }
    }

    assert unit_8_v12_symbol(config) == (
        "NEARUSDT", "NEARSUSDT"
    )

    assert unit_8_v12_text(Decimal("1.200")) == "1.2"

    balance = unit_8_v12_balance([
        {
            "asset": "SUSDT",
            "availableBalance": "100"
        }
    ])
    assert balance["available_balance"] == "100"

    positions, totals = unit_8_v12_positions(
        [
            {
                "symbol": "NEARSUSDT",
                "size": "4",
                "positionSide": "LONG"
            },
            {
                "symbol": "NEARSUSDT",
                "size": "2",
                "positionSide": "SHORT"
            },
            {
                "symbol": "BTCUSDT",
                "size": "99",
                "positionSide": "LONG"
            }
        ],
        "NEARSUSDT"
    )

    assert len(positions) == 2
    assert totals["LONG"] == "4"
    assert totals["SHORT"] == "2"

    history = unit_8_v12_history_evidence(
        [
            {"symbol": "NEARSUSDT", "positionSide": "LONG", "executedQty": "1"},
            {"symbol": "NEARSUSDT", "positionSide": "SHORT", "executedQty": "1"},
            {"symbol": "BTCUSDT", "positionSide": "LONG", "executedQty": "1"}
        ],
        "NEARSUSDT"
    )
    assert history["observed_demo_symbol"] is True
    assert history["dual_side_history_evidence"] is True

    contract = {
        "minimum_quantity": "0.0001",
        "maximum_quantity": "1000",
        "quantity_step": "0.000001",
        "contract_value": "0.000001",
        "minimum_leverage": "1",
        "maximum_leverage": "100",
    }

    preview = unit_8_v12_size_preview(
        "0.5",
        "10",
        "5",
        contract
    )

    # 0.5 USDT margin * 10x / 5 USDT = 1 base coin.
    # contract_value must not be multiplied into base-asset order qty.
    assert preview["order_quantity_base_asset"] == "1"
    assert preview["initial_order_quantity_valid"] is True

    print(
        "UNIT 8 V12 OFFLINE VALIDATION = PASS",
        flush=True
    )

    return True


# ============================================================
# 8.9 STARTUP AND GLOBAL HANDOVER
# ============================================================

FRESH_UNIT_8_VALIDATION_READY = (
    unit_8_v12_tests()
)

FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    unit_8_v12_main()
)

FRESH_UNIT_8_OPTIMIZATION_READY = (
    FRESH_UNIT_8_VALIDATION_READY
)

FRESH_UNIT_8_VERIFIED_CONTRACT = (
    FRESH_RECONSTRUCTION_UNIT_8_RESULT.get("contract")
    if isinstance(FRESH_RECONSTRUCTION_UNIT_8_RESULT, dict)
    else None
)

# ============================================================
# END UNIT 8 V12 — ZERO INDENTATION
# UNIT 9 FOLLOWS
# ============================================================


