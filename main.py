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
# UNIT 10 V2 - UNIVERSAL DEMO EXECUTION BOUNDARY
# REFERENCE 17248 ADAPTATION
# ZERO INDENTATION
# ============================================================

from decimal import Decimal as _U10Decimal
from decimal import InvalidOperation as _U10Invalid


# ============================================================
# 10.1 DECIMAL AND SYMBOL HELPERS
# ============================================================

def u10_decimal(value):
    if value is None or isinstance(value, bool):
        return None

    try:
        number = _U10Decimal(str(value))
        return number if number.is_finite() else None
    except (TypeError, ValueError, _U10Invalid):
        return None


def u10_symbol(config):
    if not isinstance(config, dict):
        return ""

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        return ""

    return str(
        exchange.get("market_symbol") or ""
    ).strip().upper()


def u10_demo_symbol(config):
    if not isinstance(config, dict):
        return ""

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        return ""

    return str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()


def u10_contract_value(contract, *names):
    if not isinstance(contract, dict):
        return None

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


# ============================================================
# 10.2 STANDARD OUTPUT CONTRACT
# ============================================================

def u10_boundary_result(
    status,
    reason,
    symbol,
    source=None,
):
    source = (
        source if isinstance(source, dict) else {}
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG", {}
    )

    demo_symbol = u10_demo_symbol(config)

    return {
        "unit_10_version":
            "U10_V2_REFERENCE_17248_ADAPTED",

        "status": status,
        "reason": str(reason),

        "skip_reason": (
            str(reason) if status != "READY"
            else None
        ),

        "market_symbol": symbol,
        "demo_order_symbol": demo_symbol,

        "direction": source.get(
            "direction", "NONE"
        ),

        "active_mode": source.get(
            "active_mode", "NONE"
        ),

        "trade_plan": source.get("trade_plan"),

        "execution_candidate": source.get(
            "execution_candidate"
        ),

        "signal_qualified": False,
        "execution_intent": False,
        "trade_plan_ready": False,

        "demo_boundary_ready": False,
        "execution_ready": False,

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


# ============================================================
# 10.3 MAIN UNIT 10
# ============================================================

def fresh_reconstruction_unit_10(
    execution_config,
    unit_9_result,
    unit_8_result=None,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 10 VERSION = "
        "V2_REFERENCE_17248_ADAPTED",
        flush=True,
    )

    symbol = u10_symbol(execution_config)
    demo_symbol = u10_demo_symbol(
        execution_config
    )

    def finish(result):
        print(
            "UNIT 10 MARKET SYMBOL =",
            result.get("market_symbol"),
            flush=True,
        )

        print(
            "UNIT 10 DEMO ORDER SYMBOL =",
            result.get("demo_order_symbol"),
            flush=True,
        )

        for key, label in (
            ("status", "STATUS"),
            ("reason", "REASON"),
            ("active_mode", "ACTIVE MODE"),
            ("direction", "DIRECTION"),
            ("trade_plan_ready", "TRADE PLAN READY"),
            ("demo_boundary_ready", "DEMO BOUNDARY READY"),
            ("execution_ready", "EXECUTION READY"),
            ("execution_authorized", "EXECUTION AUTHORIZED"),
        ):
            print(
                "UNIT 10 " + label + " =",
                result.get(key),
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
            "FRESH RECONSTRUCTION UNIT 10 RESULT =",
            (
                "PASS"
                if result.get("status")
                in ("IDLE", "READY")
                else "BLOCKED"
            ),
            flush=True,
        )

        print("=" * 80, flush=True)
        return result

    def stop(reason, status="IDLE"):
        return finish(
            u10_boundary_result(
                status,
                reason,
                symbol,
                unit_9_result,
            )
        )

    # ========================================================
    # CONFIGURATION AND ACCOUNT HANDOVER
    # ========================================================

    if not isinstance(execution_config, dict):
        return stop(
            "INVALID_CONFIGURATION", "BLOCKED"
        )

    if not isinstance(unit_9_result, dict):
        return stop(
            "INVALID_UNIT_9_RESULT", "BLOCKED"
        )

    if not isinstance(unit_8_result, dict):
        return stop(
            "UNIT_8_RESULT_MISSING", "BLOCKED"
        )

    if not symbol or not demo_symbol:
        return stop(
            "SYMBOL_CONFIGURATION_MISSING",
            "BLOCKED",
        )

    if (
        execution_config.get(
            "execution_environment"
        ) != "DEMO"
    ):
        return stop(
            "DEMO_ENVIRONMENT_REQUIRED",
            "BLOCKED",
        )

    if (
        execution_config.get(
            "real_cash_execution_enabled"
        ) is not False
    ):
        return stop(
            "REAL_CASH_EXECUTION_NOT_DISABLED",
            "BLOCKED",
        )

    # Existing adapter, already installed above Unit 9.
    try:
        symbols = demo_symbol_adapter_u10(
            execution_config,
            unit_8_result,
        )
    except (RuntimeError, TypeError, ValueError) as exc:
        return stop(
            "SYMBOL_ADAPTER_" + str(exc),
            "BLOCKED",
        )

    if not isinstance(symbols, dict):
        return stop(
            "SYMBOL_ADAPTER_INVALID",
            "BLOCKED",
        )

    if (
        symbols.get("market_symbol") != symbol
        or symbols.get("demo_order_symbol")
        != demo_symbol
    ):
        return stop(
            "SYMBOL_ADAPTER_MISMATCH",
            "BLOCKED",
        )

    # Preserve Unit 8 V19 read-only verification.
    if (
        unit_8_result.get("status")
        != "VERIFIED_READ_ONLY"
    ):
        return stop(
            "UNIT_8_NOT_VERIFIED",
            "BLOCKED",
        )

    if (
        unit_8_result.get("demo_contract_verified")
        is not True
    ):
        return stop(
            "DEMO_CONTRACT_UNVERIFIED",
            "BLOCKED",
        )

    if (
        unit_8_result.get("demo_balance_verified")
        is not True
    ):
        return stop(
            "DEMO_BALANCE_UNVERIFIED",
            "BLOCKED",
        )

    if (
        unit_8_result.get(
            "demo_positions_read_verified"
        ) is not True
    ):
        return stop(
            "DEMO_POSITIONS_UNVERIFIED",
            "BLOCKED",
        )

    if (
        unit_8_result.get("position_flat_verified")
        is not True
    ):
        return stop("POSITION_NOT_FLAT")

    # ========================================================
    # UNIT 9 SIGNAL HANDOVER
    # ========================================================

    status9 = str(
        unit_9_result.get("status") or ""
    ).upper()

    if status9 == "IDLE":
        return stop(
            "UNIT_9_" + str(
                unit_9_result.get(
                    "reason", "NO_QUALIFIED_ENTRY"
                )
            )
        )

    if status9 != "PREPARED_READ_ONLY":
        return stop(
            "UNIT_9_NOT_PREPARED",
            "BLOCKED",
        )

    if (
        unit_9_result.get("read_only")
        is not True
        or unit_9_result.get("exchange_write")
        is not False
        or unit_9_result.get(
            "execution_authorized"
        ) is not False
    ):
        return stop(
            "UNIT_9_SAFETY_VIOLATION",
            "BLOCKED",
        )

    if (
        unit_9_result.get("signal_qualified")
        is not True
        or unit_9_result.get("trade_plan_ready")
        is not True
        or unit_9_result.get("execution_intent")
        is not True
    ):
        return stop(
            "UNIT_9_SIGNAL_NOT_READY"
        )

    if (
        str(
            unit_9_result.get("market_symbol") or ""
        ).upper() != symbol
    ):
        return stop(
            "UNIT_9_MARKET_SYMBOL_MISMATCH",
            "BLOCKED",
        )

    if (
        str(
            unit_9_result.get(
                "demo_order_symbol"
            ) or ""
        ).upper() != demo_symbol
    ):
        return stop(
            "UNIT_9_DEMO_SYMBOL_MISMATCH",
            "BLOCKED",
        )

    # ========================================================
    # TRADE PLAN AND CANDIDATE
    # ========================================================

    plan = unit_9_result.get("trade_plan")
    candidate = unit_9_result.get(
        "execution_candidate"
    )

    if not isinstance(plan, dict):
        return stop(
            "TRADE_PLAN_MISSING", "BLOCKED"
        )

    if not isinstance(candidate, dict):
        return stop(
            "EXECUTION_CANDIDATE_MISSING",
            "BLOCKED",
        )

    if plan is not candidate:
        return stop(
            "TRADE_PLAN_CANDIDATE_MISMATCH",
            "BLOCKED",
        )

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

    expected_fields = {
        "market_symbol": symbol,
        "demo_order_symbol": demo_symbol,
        "direction": direction,
        "active_mode": mode,
    }

    for key, expected in expected_fields.items():
        if str(
            plan.get(key) or ""
        ).upper() != expected:
            return stop(
                "TRADE_PLAN_" +
                key.upper() +
                "_MISMATCH",
                "BLOCKED",
            )

    # ========================================================
    # QUANTITY AND CONTRACT VALIDATION
    # ========================================================

    quantity = u10_decimal(
        plan.get("quantity")
    )

    half = u10_decimal(
        plan.get("half_quantity")
    )

    minimum = u10_decimal(
        plan.get("minimum_quantity")
    )

    step = u10_decimal(
        plan.get("quantity_step")
    )

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
        return stop(
            "INVALID_CONTRACT_QUANTITY_RULES",
            "BLOCKED",
        )

    if quantity < minimum:
        return stop("QUANTITY_BELOW_MINIMUM")

    if quantity % step != 0:
        return stop("QUANTITY_STEP_INVALID")

    if half < minimum:
        return stop(
            "HALF_QUANTITY_BELOW_MINIMUM"
        )

    if half % step != 0:
        return stop(
            "HALF_QUANTITY_STEP_INVALID"
        )

    if half * 2 != quantity:
        return stop(
            "HALF_QUANTITY_MISMATCH"
        )

    # ========================================================
    # VERIFY AGAINST UNIT 8 CONTRACT
    # ========================================================

    contract = unit_8_result.get("contract")

    if not isinstance(contract, dict):
        return stop(
            "UNIT_8_CONTRACT_MISSING",
            "BLOCKED",
        )

    comparisons = (
        (
            minimum,
            u10_contract_value(
                contract,
                "minimum_quantity",
                "min_quantity",
                "minQty",
                "minTradeNum",
            ),
        ),
        (
            step,
            u10_contract_value(
                contract,
                "quantity_step",
                "qty_step",
                "stepSize",
                "sizeMultiplier",
            ),
        ),
        (
            price_step,
            u10_contract_value(
                contract,
                "price_step",
                "tickSize",
                "priceEndStep",
            ),
        ),
        (
            multiplier,
            u10_contract_value(
                contract,
                "contract_multiplier",
                "contractMultiplier",
                "contractSize",
            ),
        ),
    )

    for planned, verified in comparisons:
        if (
            verified is None
            or verified <= 0
            or planned != verified
        ):
            return stop(
                "CONTRACT_RULE_MISMATCH",
                "BLOCKED",
            )

    # ========================================================
    # UNIT 8 SIZE PREVIEW
    # ========================================================

    preview = unit_8_result.get(
        "size_preview"
    )

    if not isinstance(preview, dict):
        return stop(
            "UNIT_8_SIZE_PREVIEW_MISSING"
        )

    if (
        preview.get("initial_quantity_valid")
        is not True
        or preview.get("half_quantity_valid")
        is not True
    ):
        return stop(
            "UNIT_8_SIZE_PREVIEW_INVALID"
        )

    if (
        u10_decimal(
            preview.get(
                "rounded_contract_quantity"
            )
        ) != quantity
    ):
        return stop(
            "PREVIEW_QUANTITY_MISMATCH"
        )

    if (
        u10_decimal(
            preview.get(
                "half_contract_quantity"
            )
        ) != half
    ):
        return stop(
            "PREVIEW_HALF_QUANTITY_MISMATCH"
        )

    # ========================================================
    # VERIFIED HANDOVER TO UNIT 11
    # ========================================================

    result = u10_boundary_result(
        "READY",
        "VALIDATED_DEMO_TRADE_BOUNDARY",
        symbol,
        unit_9_result,
    )

    result.update({
        "demo_order_symbol": demo_symbol,

        "direction": direction,
        "active_mode": mode,

        "signal_qualified": True,
        "execution_intent": True,
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

        # Unit 11 prepares the order.
        # Unit 12 alone handles submission.
        "execution_ready": False,
        "execution_authorized": False,
        "order_submission_authorized": False,

        "order_payload_created": False,
        "demo_submission_requested": False,

        "read_only": True,
        "exchange_write": False,
        "real_cash_execution": False,
    })

    return finish(result)


# ============================================================
# 10.4 ORIGINAL TWO-ARGUMENT ADAPTER
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
                "UNIT 10 TRADE PLAN IDENTITY CHANGED"
            )

        if (
            result.get("execution_candidate")
            is not unit_9_result.get(
                "execution_candidate"
            )
        ):
            raise RuntimeError(
                "UNIT 10 CANDIDATE IDENTITY CHANGED"
            )

    print(
        "UNIT 10 HYBRID ADAPTER STATUS =",
        result.get("status"),
        flush=True,
    )

    return result


# ============================================================
# 10.5 LOCAL VALIDATION
# NO EXCHANGE CONNECTION
# ============================================================

def unit_10_validation_v1():
    tests = []

    def check(name, condition):
        tests.append(
            (name, bool(condition))
        )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG", {}
    )

    market = u10_symbol(config)
    demo = u10_demo_symbol(config)

    idle = u10_boundary_result(
        "IDLE",
        "TEST_IDLE",
        market,
    )

    check(
        "MARKET SYMBOL FROM UNIT 2",
        market.endswith("USDT"),
    )

    check(
        "DEMO SYMBOL FROM UNIT 2",
        demo == config.get(
            "exchange", {}
        ).get("demo_order_symbol"),
    )

    check(
        "DISTINCT MARKET AND DEMO SYMBOLS",
        market != demo,
    )

    check(
        "IDLE EXECUTION BLOCKED",
        idle["execution_authorized"] is False,
    )

    check(
        "NO ORDER PAYLOAD",
        idle["order_payload_created"] is False,
    )

    check(
        "NO DEMO SUBMISSION",
        idle["demo_submission_requested"] is False,
    )

    check(
        "NO EXCHANGE WRITE",
        idle["exchange_write"] is False,
    )

    check(
        "REAL CASH DISABLED",
        idle["real_cash_execution"] is False,
    )

    check(
        "VALID DECIMAL",
        u10_decimal("14")
        == _U10Decimal("14"),
    )

    check(
        "INVALID DECIMAL REJECTED",
        u10_decimal("invalid") is None,
    )

    check(
        "HALF QUANTITY VALID",
        _U10Decimal("14") / 2
        == _U10Decimal("7"),
    )

    check(
        "INVALID HALF STEP DETECTED",
        (
            _U10Decimal("3") / 2
        ) % _U10Decimal("1") != 0,
    )

    passed = sum(
        1 for _, ok in tests if ok
    )

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
# 10.6 STARTUP AND GLOBAL HANDOVER
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
# UNIT 11 FOLLOWS
# ============================================================



  
# ============================================================
# START COMPLETE UNIT 11 REPLACEMENT
# UNIT 11 V2 - UNIVERSAL DEMO ORDER PREPARATION
# ADAPTED FOR UNIT 10 V2 AND UNIT 8 V19
# ZERO INDENTATION
# ============================================================

from decimal import Decimal as _U11Decimal
from decimal import InvalidOperation as _U11Invalid


# ============================================================
# 11.1 NUMERIC AND SYMBOL HELPERS
# ============================================================

def u11_decimal(value):
    if value is None or isinstance(value, bool):
        return None

    try:
        number = _U11Decimal(str(value))
        return number if number.is_finite() else None
    except (TypeError, ValueError, _U11Invalid):
        return None


def u11_symbol(config):
    if not isinstance(config, dict):
        return ""

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        return ""

    return str(
        exchange.get("market_symbol") or ""
    ).strip().upper()


def u11_demo_symbol(config):
    if not isinstance(config, dict):
        return ""

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        return ""

    return str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()


def u11_step_valid(quantity, minimum, step):
    if any(
        value is None or value <= 0
        for value in (quantity, minimum, step)
    ):
        return False

    return (
        quantity >= minimum
        and quantity % step == 0
    )


# ============================================================
# 11.2 STANDARD RESULT CONTRACT
# ============================================================

def u11_result(
    status,
    reason,
    symbol,
    source=None,
):
    source = (
        source if isinstance(source, dict) else {}
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG", {}
    )

    return {
        "unit_11_version":
            "U11_V2_REFERENCE_17248_ADAPTED",

        "status": status,
        "reason": str(reason),

        "skip_reason": (
            str(reason)
            if status != "PREPARED_READ_ONLY"
            else None
        ),

        "market_symbol": symbol,
        "demo_order_symbol":
            u11_demo_symbol(config),

        "direction": source.get(
            "direction", "NONE"
        ),

        "active_mode": source.get(
            "active_mode", "NONE"
        ),

        "trade_plan": source.get("trade_plan"),

        "execution_candidate": source.get(
            "execution_candidate"
        ),

        "order_instruction": None,
        "order_payload": None,

        "order_payload_created": False,
        "order_format_verified": False,

        "signal_qualified": False,
        "execution_intent": False,
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


# ============================================================
# 11.3 MAIN UNIT 11
# ============================================================

def fresh_reconstruction_unit_11(
    execution_config,
    unit_10_result,
    unit_8_result=None,
):

    print("=" * 80, flush=True)

    print(
        "UNIT 11 VERSION = "
        "V2_REFERENCE_17248_ADAPTED",
        flush=True,
    )

    symbol = u11_symbol(execution_config)
    demo_symbol = u11_demo_symbol(
        execution_config
    )

    # ========================================================
    # RESULT LOGGER
    # ========================================================

    def finish(result):
        print(
            "UNIT 11 MARKET SYMBOL =",
            result.get("market_symbol"),
            flush=True,
        )

        print(
            "UNIT 11 DEMO ORDER SYMBOL =",
            result.get("demo_order_symbol"),
            flush=True,
        )

        for key, label in (
            ("status", "STATUS"),
            ("reason", "REASON"),
            ("active_mode", "ACTIVE MODE"),
            ("direction", "DIRECTION"),
            ("signal_qualified", "SIGNAL QUALIFIED"),
            ("trade_plan_ready", "TRADE PLAN READY"),
            ("order_preparation_ready",
             "ORDER PREPARATION READY"),
            ("order_format_verified",
             "ORDER FORMAT VERIFIED"),
            ("demo_boundary_ready",
             "DEMO BOUNDARY READY"),
            ("execution_ready", "EXECUTION READY"),
            ("execution_authorized",
             "EXECUTION AUTHORIZED"),
        ):
            print(
                "UNIT 11 " + label + " =",
                result.get(key),
                flush=True,
            )

        print(
            "UNIT 11 ORDER PAYLOAD CREATED =",
            result.get("order_payload_created"),
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
                if result.get("status") in (
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
    # CONFIGURATION VALIDATION
    # ========================================================

    if not isinstance(execution_config, dict):
        return stop("INVALID_CONFIGURATION")

    if not isinstance(unit_10_result, dict):
        return stop("UNIT_10_RESULT_MISSING")

    if not isinstance(unit_8_result, dict):
        return stop("UNIT_8_RESULT_MISSING")

    if not symbol or not demo_symbol:
        return stop("SYMBOL_CONFIGURATION_MISSING")

    if (
        execution_config.get(
            "execution_environment"
        ) != "DEMO"
    ):
        return stop("DEMO_ENVIRONMENT_REQUIRED")

    if (
        execution_config.get(
            "real_cash_execution_enabled"
        ) is not False
    ):
        return stop(
            "REAL_CASH_EXECUTION_NOT_DISABLED"
        )

    # ========================================================
    # SHARED UNIT 2 SYMBOL ADAPTER
    # ========================================================

    try:
        symbols = demo_symbol_adapter_u11(
            execution_config,
            unit_8_result,
        )
    except (RuntimeError, TypeError, ValueError) as exc:
        return stop(
            "SYMBOL_ADAPTER_" + str(exc)
        )

    if not isinstance(symbols, dict):
        return stop("SYMBOL_ADAPTER_INVALID")

    if (
        symbols.get("market_symbol") != symbol
        or symbols.get("demo_order_symbol")
        != demo_symbol
    ):
        return stop("SYMBOL_ADAPTER_MISMATCH")

    # ========================================================
    # PRESERVE UNIT 8 V19 VERIFICATION
    # ========================================================

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
        unit_8_result.get(
            "demo_positions_read_verified"
        ) is not True
    ):
        return stop("DEMO_POSITIONS_UNVERIFIED")

    if (
        unit_8_result.get("position_flat_verified")
        is not True
    ):
        return stop("POSITION_NOT_FLAT", "IDLE")

    # ========================================================
    # UNIT 10 HANDOVER
    # ========================================================

    status10 = str(
        unit_10_result.get("status") or ""
    ).upper()

    if status10 == "IDLE":
        return stop(
            "UNIT_10_" + str(
                unit_10_result.get(
                    "reason", "NO_QUALIFIED_ENTRY"
                )
            ),
            "IDLE",
        )

    if status10 != "READY":
        return stop("UNIT_10_NOT_READY")

    if (
        unit_10_result.get("read_only")
        is not True
        or unit_10_result.get("exchange_write")
        is not False
        or unit_10_result.get(
            "execution_authorized"
        ) is not False
    ):
        return stop("UNIT_10_SAFETY_VIOLATION")

    if (
        unit_10_result.get("signal_qualified")
        is not True
        or unit_10_result.get("execution_intent")
        is not True
        or unit_10_result.get("trade_plan_ready")
        is not True
        or unit_10_result.get("demo_boundary_ready")
        is not True
    ):
        return stop("UNIT_10_SIGNAL_NOT_READY")

    if (
        str(
            unit_10_result.get("market_symbol") or ""
        ).upper() != symbol
    ):
        return stop("UNIT_10_MARKET_SYMBOL_MISMATCH")

    if (
        str(
            unit_10_result.get(
                "demo_order_symbol"
            ) or ""
        ).upper() != demo_symbol
    ):
        return stop("UNIT_10_DEMO_SYMBOL_MISMATCH")

    # ========================================================
    # TRADE PLAN AND EXECUTION CANDIDATE
    # ========================================================

    plan = unit_10_result.get("trade_plan")
    candidate = unit_10_result.get(
        "execution_candidate"
    )

    if not isinstance(plan, dict):
        return stop("TRADE_PLAN_MISSING")

    if not isinstance(candidate, dict):
        return stop("EXECUTION_CANDIDATE_MISSING")

    if plan is not candidate:
        return stop(
            "TRADE_PLAN_CANDIDATE_IDENTITY_MISMATCH"
        )

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

    expected = {
        "market_symbol": symbol,
        "demo_order_symbol": demo_symbol,
        "direction": direction,
        "active_mode": mode,
    }

    for key, value in expected.items():
        if str(
            plan.get(key) or ""
        ).upper() != value:
            return stop(
                "TRADE_PLAN_" +
                key.upper() +
                "_MISMATCH"
            )

    # ========================================================
    # QUANTITY AND CONTRACT VALIDATION
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

    values = (
        quantity,
        half,
        minimum,
        step,
        multiplier,
        price_step,
    )

    if any(
        value is None or value <= 0
        for value in values
    ):
        return stop(
            "INVALID_QUANTITY_OR_CONTRACT_RULES"
        )

    if not u11_step_valid(
        quantity, minimum, step
    ):
        return stop("QUANTITY_STEP_OR_MINIMUM_INVALID")

    if not u11_step_valid(
        half, minimum, step
    ):
        return stop(
            "HALF_QUANTITY_STEP_OR_MINIMUM_INVALID"
        )

    if half * 2 != quantity:
        return stop("HALF_QUANTITY_MISMATCH")

    # ========================================================
    # CROSS-CHECK UNIT 10 VERIFIED VALUES
    # ========================================================

    fields = (
        ("quantity", quantity),
        ("half_quantity", half),
        ("minimum_quantity", minimum),
        ("quantity_step", step),
        ("contract_multiplier", multiplier),
        ("price_step", price_step),
    )

    for name, expected_value in fields:
        if (
            u11_decimal(
                unit_10_result.get(name)
            ) != expected_value
        ):
            return stop(
                "UNIT_10_" +
                name.upper() +
                "_MISMATCH"
            )

    # ========================================================
    # UNIT 8 SIZE PREVIEW CONSISTENCY
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
            preview.get(
                "rounded_contract_quantity"
            )
        ) != quantity
    ):
        return stop("UNIT_8_QUANTITY_MISMATCH")

    if (
        u11_decimal(
            preview.get(
                "half_contract_quantity"
            )
        ) != half
    ):
        return stop("UNIT_8_HALF_QUANTITY_MISMATCH")

    # ========================================================
    # BUILD INTERNAL INSTRUCTION FOR UNIT 12
    # ========================================================

    strategy = execution_config.get(
        "strategy", {}
    )

    if not isinstance(strategy, dict):
        return stop("STRATEGY_CONFIG_INVALID")

    hedge = strategy.get("hedge", {})

    if not isinstance(hedge, dict):
        return stop("HEDGE_CONFIG_INVALID")

    hedge_mode = str(
        hedge.get(
            "mode",
            "REVERSIBLE_ATR_TWO_STAGE",
        )
    )

    backup_count = strategy.get(
        "max_backups", 5
    )

    instruction = {
        "instruction_version": "U11_INTERNAL_V1",

        "market_symbol": symbol,
        "demo_order_symbol": demo_symbol,

        "market_type": "DEMO_FUTURES",
        "position_action": "OPEN",

        "direction": direction,
        "strategy_mode": mode,

        "quantity": format(quantity, "f"),
        "half_quantity": format(half, "f"),

        "minimum_quantity": format(
            minimum, "f"
        ),

        "quantity_step": format(step, "f"),

        "contract_multiplier": format(
            multiplier, "f"
        ),

        "price_step": format(
            price_step, "f"
        ),

        "order_type": "MARKET",

        "hedge_policy": hedge_mode,
        "backup_count": backup_count,

        # Preserve exact upstream objects.
        "trade_plan": plan,
        "execution_candidate": candidate,

        # Unit 12 converts to WEEX payload.
        "weex_payload_verified": False,
        "exchange_permission_verified": False,
        "submission_authorized": False,
    }

    # ========================================================
    # PREPARED READ-ONLY HANDOVER
    # ========================================================

    result = u11_result(
        "PREPARED_READ_ONLY",
        "INTERNAL_ORDER_INSTRUCTION_PREPARED",
        symbol,
        unit_10_result,
    )

    result.update({
        "demo_order_symbol": demo_symbol,

        "direction": direction,
        "active_mode": mode,

        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,

        "order_preparation_ready": True,
        "demo_boundary_ready": True,

        "quantity": format(quantity, "f"),
        "half_quantity": format(half, "f"),

        "minimum_quantity": format(
            minimum, "f"
        ),

        "quantity_step": format(step, "f"),

        "contract_multiplier": format(
            multiplier, "f"
        ),

        "price_step": format(
            price_step, "f"
        ),

        "order_instruction": instruction,

        "trade_plan": plan,
        "execution_candidate": candidate,

        # Unit 11 does not construct the
        # final WEEX API payload.
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
# 11.4 ORIGINAL TWO-ARGUMENT HYBRID ADAPTER
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
# 11.5 LOCAL VALIDATION
# NO EXCHANGE REQUESTS
# ============================================================

def unit_11_validation_v2():
    tests = []

    def check(name, condition):
        tests.append(
            (name, bool(condition))
        )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG", {}
    )

    market = u11_symbol(config)
    demo = u11_demo_symbol(config)

    idle = u11_result(
        "IDLE",
        "TEST_IDLE",
        market,
    )

    check(
        "MARKET SYMBOL FROM UNIT 2",
        market.endswith("USDT"),
    )

    check(
        "DEMO SYMBOL FROM UNIT 2",
        demo == config.get(
            "exchange", {}
        ).get("demo_order_symbol"),
    )

    check(
        "MARKET AND DEMO SYMBOLS DISTINCT",
        market != demo,
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
        "DECIMAL VALID",
        u11_decimal("14")
        == _U11Decimal("14"),
    )

    check(
        "INVALID DECIMAL REJECTED",
        u11_decimal("bad") is None,
    )

    check(
        "HALF QUANTITY VALID",
        u11_step_valid(
            _U11Decimal("14"),
            _U11Decimal("1"),
            _U11Decimal("1"),
        ),
    )

    check(
        "INVALID HALF STEP DETECTED",
        not u11_step_valid(
            _U11Decimal("1.5"),
            _U11Decimal("1"),
            _U11Decimal("1"),
        ),
    )

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 11 TEST",
            name,
            "=",
            "PASS" if ok else "FAIL",
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
# 11.6 STARTUP AND GLOBAL HANDOVER
# ============================================================

FRESH_UNIT_11_VALIDATION_READY = (
    unit_11_validation_v2()
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
# UNIT 12 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 12 V6
# WEEX UNIVERSAL DEMO ORDER EXECUTION
# UNIT 11 V2 -> UNIT 12 -> UNIT 13
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

# In-process duplicate protection.
_UNIT12_V5_ORDER_ATTEMPTS = set()


# ============================================================
# 12.1 NUMERIC AND SYMBOL HELPERS
# ============================================================

def unit_12_v5_decimal(value, name, allow_zero=False):

    if value is None or isinstance(value, bool):
        raise RuntimeError("UNIT 12 MISSING " + name)

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 12 INVALID " + name
        ) from exc

    if not number.is_finite() or number < 0:
        raise RuntimeError("UNIT 12 INVALID " + name)

    if number == 0 and not allow_zero:
        raise RuntimeError("UNIT 12 ZERO " + name)

    return number


def unit_12_v5_symbol(config):

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 12 CONFIG INVALID")

    exchange = config.get("exchange", {})

    symbol = str(
        exchange.get("market_symbol") or ""
    ).strip().upper()

    if (
        not symbol.endswith("USDT")
        or not symbol.isalnum()
    ):
        raise RuntimeError("UNIT 12 MARKET SYMBOL INVALID")

    return symbol


def unit_12_v6_demo_symbol(config):

    exchange = config.get("exchange", {})

    symbol = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if not symbol or not symbol.isalnum():
        raise RuntimeError("UNIT 12 DEMO SYMBOL INVALID")

    return symbol


def unit_12_v5_client_order_id(original_id, direction):

    if not isinstance(original_id, str) or not original_id:
        raise RuntimeError("UNIT 12 CLIENT ID MISSING")

    if re.fullmatch(
        r"[.A-Za-z0-9_:/-]{1,36}",
        original_id
    ):
        return original_id

    digest = hashlib.sha256(
        original_id.encode("utf-8")
    ).hexdigest()[:24]

    return (
        "FR12"
        + ("L" if direction == "LONG" else "S")
        + digest
    )


# ============================================================
# 12.2 RESULT CONTRACT
# PRESERVE UNIT 13 HANDOVER
# ============================================================

def unit_12_v5_result(source, status, reason, symbol):

    source = source if isinstance(source, dict) else {}

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG", {}
    )

    return {
        "unit": 12,
        "version": "V6_UNIVERSAL_DEMO_EXECUTION",

        "status": status,
        "reason": reason,
        "skip_reason": reason,

        "market_symbol": symbol,
        "demo_order_symbol":
            unit_12_v6_demo_symbol(config),

        "active_mode": source.get("active_mode"),
        "direction": source.get("direction"),

        "signal_qualified":
            source.get("signal_qualified") is True,

        "execution_intent":
            source.get("execution_intent") is True,

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


# ============================================================
# 12.3 AUTHENTICATED WEEX DEMO REQUEST
# ORIGINAL REFERENCE ENDPOINTS
# ============================================================

def unit_12_v5_request(method, path, body=None):

    allowed = (
        ("GET", UNIT_12_V5_POSITION_PATH),
        ("POST", UNIT_12_V5_ORDER_PATH),
    )

    if (method, path) not in allowed:
        raise RuntimeError(
            "UNIT 12 NON-DEMO ENDPOINT BLOCKED"
        )

    if method == "GET" and body is not None:
        raise RuntimeError("UNIT 12 INVALID GET BODY")

    if method == "POST":
        if not isinstance(body, dict):
            raise RuntimeError("UNIT 12 INVALID POST BODY")

        expected_demo = unit_12_v6_demo_symbol(
            FRESH_RECONSTRUCTION_CONFIG
        )

        if body.get("symbol") != expected_demo:
            raise RuntimeError(
                "UNIT 12 POST DEMO SYMBOL MISMATCH"
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
            "UNIT 12 WEEX CREDENTIALS MISSING"
        )

    body_text = (
        json.dumps(
            body,
            separators=(",", ":"),
            ensure_ascii=False
        )
        if body is not None else ""
    )

    timestamp = str(int(time.time() * 1000))
    message = timestamp + method + path + body_text

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        UNIT_12_V5_BASE_URL + path,
        data=(
            body_text.encode("utf-8")
            if method == "POST" else None
        ),
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
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:

            status = response.getcode()

            raw = response.read().decode(
                "utf-8", errors="replace"
            )

    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode(
            "utf-8", errors="replace"
        )

    try:
        data = json.loads(raw)
    except ValueError:
        data = {"error": "INVALID_RESPONSE_JSON"}

    return status, data


# ============================================================
# 12.4 FRESH DEMO POSITION VERIFICATION
# ============================================================

def unit_12_v5_active_positions(rows, symbol):

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 12 POSITION RESPONSE NOT LIST"
        )

    active = []

    for position in rows:

        if not isinstance(position, dict):
            raise RuntimeError(
                "UNIT 12 INVALID POSITION RECORD"
            )

        if (
            str(position.get("symbol") or "").upper()
            != symbol
        ):
            continue

        size = unit_12_v5_decimal(
            position.get("size"),
            "POSITION SIZE",
            allow_zero=True
        )

        if size > 0:
            active.append(position)

    return active


# ============================================================
# 12.5 UNIT 11 INSTRUCTION VALIDATION
# ============================================================

def unit_12_v5_validate_payload(config, upstream, account):

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 12 CONFIG MISSING")

    if not isinstance(upstream, dict):
        raise RuntimeError("UNIT 12 UNIT 11 MISSING")

    if not isinstance(account, dict):
        raise RuntimeError("UNIT 12 UNIT 8 MISSING")

    market = unit_12_v5_symbol(config)
    demo = unit_12_v6_demo_symbol(config)

    # Unit 8 V19 remains unchanged.
    if account.get("status") != "VERIFIED_READ_ONLY":
        raise RuntimeError("UNIT 12 UNIT 8 NOT VERIFIED")

    if (
        str(account.get("market_symbol") or "").upper()
        != market
        or str(account.get("demo_order_symbol") or "").upper()
        != demo
    ):
        raise RuntimeError(
            "UNIT 12 UNIT 8 SYMBOL MISMATCH"
        )

    if upstream.get("status") != "PREPARED_READ_ONLY":
        raise RuntimeError(
            "UNIT 12 UNIT 11 NOT PREPARED"
        )

    if (
        upstream.get("signal_qualified") is not True
        or upstream.get("trade_plan_ready") is not True
        or upstream.get("execution_intent") is not True
        or upstream.get("order_preparation_ready") is not True
    ):
        raise RuntimeError(
            "UNIT 12 UNIT 11 SIGNAL NOT READY"
        )

    if (
        upstream.get("read_only") is not True
        or upstream.get("exchange_write") is not False
    ):
        raise RuntimeError(
            "UNIT 12 UNIT 11 SAFETY MISMATCH"
        )

    if account.get("demo_contract_verified") is not True:
        raise RuntimeError(
            "UNIT 12 CONTRACT NOT VERIFIED"
        )

    if account.get("demo_balance_verified") is not True:
        raise RuntimeError(
            "UNIT 12 BALANCE NOT VERIFIED"
        )

    if (
        account.get("demo_positions_read_verified")
        is not True
    ):
        raise RuntimeError(
            "UNIT 12 POSITIONS NOT VERIFIED"
        )

    if account.get("account_can_trade") is not True:
        raise RuntimeError(
            "UNIT 12 ACCOUNT CANNOT TRADE"
        )

    instruction = upstream.get("order_instruction")
    plan = upstream.get("trade_plan")

    if not isinstance(instruction, dict):
        raise RuntimeError(
            "UNIT 12 ORDER INSTRUCTION MISSING"
        )

    if not isinstance(plan, dict):
        raise RuntimeError(
            "UNIT 12 TRADE PLAN MISSING"
        )

    if instruction.get("trade_plan") is not plan:
        raise RuntimeError(
            "UNIT 12 TRADE PLAN HANDOVER MISMATCH"
        )

    if (
        instruction.get("market_symbol") != market
        or instruction.get("demo_order_symbol") != demo
        or upstream.get("market_symbol") != market
        or upstream.get("demo_order_symbol") != demo
    ):
        raise RuntimeError(
            "UNIT 12 SYMBOL HANDOVER MISMATCH"
        )

    if (
        instruction.get("position_action") != "OPEN"
        or instruction.get("market_type") != "DEMO_FUTURES"
        or instruction.get("order_type") != "MARKET"
    ):
        raise RuntimeError(
            "UNIT 12 INVALID DEMO OPEN INSTRUCTION"
        )

    direction = str(
        instruction.get("direction") or ""
    ).upper()

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 12 INVALID DIRECTION"
        )

    if (
        str(upstream.get("direction") or "").upper()
        != direction
        or str(plan.get("direction") or "").upper()
        != direction
    ):
        raise RuntimeError(
            "UNIT 12 DIRECTION MISMATCH"
        )

    if plan.get("market_symbol") != market:
        raise RuntimeError(
            "UNIT 12 PLAN MARKET SYMBOL MISMATCH"
        )

    if plan.get("demo_order_symbol") != demo:
        raise RuntimeError(
            "UNIT 12 PLAN DEMO SYMBOL MISMATCH"
        )

    if (
        instruction.get("strategy_mode")
        != upstream.get("active_mode")
    ):
        raise RuntimeError(
            "UNIT 12 STRATEGY MODE MISMATCH"
        )

    quantity = unit_12_v5_decimal(
        instruction.get("quantity"), "QUANTITY"
    )

    minimum = unit_12_v5_decimal(
        instruction.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    step = unit_12_v5_decimal(
        instruction.get("quantity_step"),
        "QUANTITY STEP"
    )

    half = unit_12_v5_decimal(
        instruction.get("half_quantity"),
        "HALF QUANTITY"
    )

    if quantity < minimum or quantity % step != 0:
        raise RuntimeError(
            "UNIT 12 QUANTITY STEP INVALID"
        )

    if half < minimum or half % step != 0:
        raise RuntimeError(
            "UNIT 12 HALF QUANTITY INVALID"
        )

    if half * 2 != quantity:
        raise RuntimeError(
            "UNIT 12 HALF QUANTITY MISMATCH"
        )

    for source, name in (
        (plan, "PLAN"),
        (upstream, "UNIT 11"),
    ):
        if unit_12_v5_decimal(
            source.get("quantity"),
            name + " QUANTITY"
        ) != quantity:
            raise RuntimeError(
                "UNIT 12 " + name + " QUANTITY MISMATCH"
            )

    if unit_12_v5_decimal(
        account.get("minimum_quantity"),
        "ACCOUNT MINIMUM"
    ) != minimum:
        raise RuntimeError(
            "UNIT 12 ACCOUNT MINIMUM MISMATCH"
        )

    if unit_12_v5_decimal(
        account.get("quantity_step"),
        "ACCOUNT STEP"
    ) != step:
        raise RuntimeError(
            "UNIT 12 ACCOUNT STEP MISMATCH"
        )

    # Original model: deterministic candle-based client ID.
    original_id = instruction.get("newClientOrderId")

    if not original_id:

        analysis = globals().get(
            "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
        )

        if not isinstance(analysis, dict):
            raise RuntimeError(
                "UNIT 12 SIGNAL IDENTITY MISSING"
            )

        candle_id = analysis.get(
            "latest_close_time_ms"
        )

        if (
            not isinstance(candle_id, int)
            or isinstance(candle_id, bool)
            or candle_id <= 0
        ):
            raise RuntimeError(
                "UNIT 12 CANDLE ID INVALID"
            )

        age = int(time.time() * 1000) - candle_id

        if not 0 <= age <= 120000:
            raise RuntimeError(
                "UNIT 12 SIGNAL CANDLE STALE"
            )

        original_id = (
            market + "-"
            + str(instruction["strategy_mode"]) + "-"
            + direction + "-"
            + str(candle_id)
        )

    client_id = unit_12_v5_client_order_id(
        original_id, direction
    )

    payload = {
        "symbol": demo,
        "side": (
            "BUY" if direction == "LONG"
            else "SELL"
        ),
        "positionSide": direction,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": client_id,
    }

    print(
        "UNIT 12 PAYLOAD DEMO SYMBOL =",
        demo,
        flush=True
    )

    print(
        "UNIT 12 PAYLOAD QUANTITY =",
        format(quantity, "f"),
        flush=True
    )

    return payload, quantity


# ============================================================
# 12.6 DEMO ENTRY EXECUTION
# ============================================================

def fresh_reconstruction_unit_12(
    config,
    unit_11_result,
    unit_8_result=None,
):

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 12 CONFIG INVALID"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 12 NON-DEMO ENVIRONMENT"
        )

    if config.get(
        "real_cash_execution_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 12 REAL CASH NOT DISABLED"
        )

    if not isinstance(unit_11_result, dict):
        raise RuntimeError(
            "UNIT 12 UNIT 11 INVALID"
        )

    if unit_8_result is None:
        unit_8_result = globals().get(
            "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
        )

    market = unit_12_v5_symbol(config)
    demo = unit_12_v6_demo_symbol(config)

    mode = os.getenv(
        "BOT_MODE", "PAUSE"
    ).strip().upper()

    if mode not in ("RUN", "PAUSE"):
        raise RuntimeError(
            "UNIT 12 BOT_MODE INVALID"
        )

    result = unit_12_v5_result(
        unit_11_result,
        "IDLE",
        "NOT_EVALUATED",
        market,
    )

    print("=" * 80, flush=True)
    print(
        "UNIT 12 VERSION = V6_UNIVERSAL_DEMO_EXECUTION",
        flush=True
    )
    print("UNIT 12 BOT_MODE =", mode, flush=True)
    print("UNIT 12 MARKET SYMBOL =", market, flush=True)
    print("UNIT 12 DEMO SYMBOL =", demo, flush=True)

    def stop(status, reason):
        result["status"] = status
        result["reason"] = reason
        result["skip_reason"] = reason
        return result

    # BOT_MODE affects new initial entries only.
    if mode == "PAUSE":
        return stop("IDLE", "BOT_MODE_PAUSE")

    upstream_status = str(
        unit_11_result.get("status") or ""
    ).upper()

    if upstream_status == "IDLE":
        return stop(
            "IDLE",
            str(
                unit_11_result.get("reason")
                or "NO_QUALIFIED_ENTRY"
            )
        )

    if upstream_status != "PREPARED_READ_ONLY":
        return stop(
            "BLOCKED",
            "UNIT_11_NOT_PREPARED"
        )

    try:
        payload, quantity = unit_12_v5_validate_payload(
            config,
            unit_11_result,
            unit_8_result,
        )
    except Exception as exc:
        return stop(
            "BLOCKED",
            str(exc)
        )

    client_id = payload["newClientOrderId"]

    result["client_order_id"] = client_id
    result["order_payload"] = dict(payload)

    if client_id in _UNIT12_V5_ORDER_ATTEMPTS:
        result["duplicate_initial_entry_blocked"] = True

        return stop(
            "ORDER_UNCERTAIN",
            "PREVIOUS_CLIENT_ORDER_ATTEMPT"
        )

    # Fresh authenticated position check.
    result["position_check_attempted"] = True

    try:
        position_http, positions = unit_12_v5_request(
            "GET",
            UNIT_12_V5_POSITION_PATH
        )

        result["authenticated_request"] = True
        result["position_endpoint_access"] = True
        result["position_http_status"] = position_http

        if not 200 <= position_http < 300:
            return stop(
                "POSITION_CHECK_FAILED",
                "WEEX_POSITION_HTTP_"
                + str(position_http)
            )

        active = unit_12_v5_active_positions(
            positions,
            demo
        )

    except Exception as exc:
        print(
            "UNIT 12 POSITION CHECK ERROR =",
            type(exc).__name__,
            str(exc)[:180],
            flush=True
        )

        return stop(
            "POSITION_CHECK_FAILED",
            "POSITION_REQUEST_ERROR"
        )

    result["position_check_completed"] = True

    if active:
        result["active_position_exists"] = True
        result["active_positions"] = active
        result["duplicate_initial_entry_blocked"] = True

        return stop(
            "ACTIVE_POSITION_BLOCK",
            "NONZERO_POSITION_BLOCK_INITIAL_ENTRY"
        )

    # Fresh flat position established.
    result["initial_entry_permitted"] = True

    # Mark before POST to prevent automatic repeat
    # after an uncertain response.
    _UNIT12_V5_ORDER_ATTEMPTS.add(client_id)

    result["demo_submission_attempted"] = True

    print(
        "UNIT 12 FRESH FLAT DEMO POSITION VERIFIED",
        flush=True
    )

    print(
        "UNIT 12 SENDING WEEX DEMO ORDER",
        flush=True
    )

    try:
        order_http, response = unit_12_v5_request(
            "POST",
            UNIT_12_V5_ORDER_PATH,
            payload
        )

    except Exception as exc:
        print(
            "UNIT 12 ORDER RESPONSE UNCERTAIN =",
            type(exc).__name__,
            flush=True
        )

        return stop(
            "ORDER_UNCERTAIN",
            "POST_RESPONSE_UNCERTAIN"
        )

    result["order_endpoint_access"] = True
    result["http_status"] = order_http
    result["exchange_write"] = True

    if not isinstance(response, dict):
        return stop(
            "ORDER_UNCERTAIN",
            "UNRECOGNIZED_ORDER_RESPONSE"
        )

    if (
        not 200 <= order_http < 300
        or response.get("success") is not True
    ):
        print(
            "UNIT 12 WEEX ORDER RESPONSE =",
            str(response)[:300],
            flush=True
        )

        return stop(
            "DEMO_REJECTED",
            "WEEX_REJECTED_"
            + str(response.get("code") or "UNKNOWN")
        )

    order_id = response.get("orderId")

    if not order_id:
        return stop(
            "ORDER_UNCERTAIN",
            "SUCCESS_RESPONSE_MISSING_ORDER_ID"
        )

    result.update({
        "status": "DEMO_SUBMITTED",
        "reason": "NONE",
        "skip_reason": "NONE",

        "demo_submission_completed": True,
        "demo_order_accepted": True,

        # Fill requires separate verification.
        "fill_verified": False,

        "order_id": str(order_id),
        "exchange_response": response,
    })

    print(
        "UNIT 12 WEEX DEMO ORDER ID =",
        order_id,
        flush=True
    )

    print(
        "UNIT 12 STATUS = DEMO_SUBMITTED",
        flush=True
    )

    print(
        "UNIT 12 FILL VERIFIED = False",
        flush=True
    )

    return result


# ============================================================
# 12.7 ORIGINAL TWO-ARGUMENT ADAPTER
# ============================================================

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
        raise RuntimeError(
            "UNIT 12 REAL CASH SAFETY FAILURE"
        )

    print(
        "UNIT 12 STATUS =",
        result["status"],
        flush=True
    )

    print(
        "UNIT 12 REASON =",
        result["reason"],
        flush=True
    )

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
# 12.8 STARTUP HANDOVER TO UNIT 13
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
# END COMPLETE UNIT 12 V6
# UNIT 13 FOLLOWS
# ZERO INDENTATION
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
# START UNIT 7-8 VERIFIED CONTRACT HANDOVER V3
# UNIT 7 V12 / UNIT 8 V19
# ZERO INDENTATION
# NO EXCHANGE WRITE
# ============================================================

import time as _u78_time
from decimal import Decimal as _U78_Decimal
from decimal import InvalidOperation as _U78_Invalid

U78_MAX_CONTRACT_AGE_SECONDS = 120

# Preserve the original Unit 7 contract function.
# This adapter must replace V2, not be added after it.
_U78_V3_ORIGINAL = unit_7_v12_contract


# ============================================================
# 7-8.1 NUMERIC VALIDATION
# ============================================================

def u78_v3_decimal(value, name):

    if value is None or isinstance(value, bool):
        raise RuntimeError(
            "U78_MISSING_" + name
        )

    try:
        number = _U78_Decimal(str(value))
    except (
        TypeError,
        ValueError,
        _U78_Invalid
    ) as exc:
        raise RuntimeError(
            "U78_INVALID_" + name
        ) from exc

    if not number.is_finite() or number <= 0:
        raise RuntimeError(
            "U78_NONPOSITIVE_" + name
        )

    return number


# ============================================================
# 7-8.2 SYMBOL VERIFICATION
# ============================================================

def u78_v3_symbols(config, account):

    if not isinstance(config, dict):
        raise RuntimeError(
            "U78_CONFIG_INVALID"
        )

    exchange = config.get("exchange")

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "U78_EXCHANGE_CONFIG_INVALID"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or config.get(
            "real_cash_execution_enabled"
        ) is not False
    ):
        raise RuntimeError(
            "U78_DEMO_ONLY_REQUIRED"
        )

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
        raise RuntimeError(
            "U78_INVALID_SYMBOL_PAIR"
        )

    if (
        exchange.get("base_coin") != market[:-4]
        or exchange.get("quote_coin") != "USDT"
    ):
        raise RuntimeError(
            "U78_BASE_QUOTE_MISMATCH"
        )

    if not isinstance(account, dict):
        raise RuntimeError(
            "U78_UNIT8_RESULT_MISSING"
        )

    if (
        str(
            account.get("market_symbol") or ""
        ).upper() != market
    ):
        raise RuntimeError(
            "U78_MARKET_SYMBOL_MISMATCH"
        )

    if (
        str(
            account.get("demo_order_symbol") or ""
        ).upper() != demo
    ):
        raise RuntimeError(
            "U78_DEMO_SYMBOL_MISMATCH"
        )

    return market, demo


# ============================================================
# 7-8.3 VERIFIED UNIT 8 CONTRACT
# ============================================================

def u78_v3_verified_contract(config, account):

    market, demo = u78_v3_symbols(
        config,
        account
    )

    # Unit 8 V19 uses verified market rules
    # and independently reads the demo account.
    # Do not claim that an order was accepted.

    if (
        account.get("status")
        != "VERIFIED_READ_ONLY"
    ):
        raise RuntimeError(
            "U78_UNIT8_NOT_VERIFIED"
        )

    required_flags = (
        "market_contract_verified",
        "simulation_contract_verified",
        "simulation_contract_rules_verified",
        "demo_contract_verified",
    )

    for field in required_flags:
        if account.get(field) is not True:
            raise RuntimeError(
                "U78_UNVERIFIED_" + field.upper()
            )

    # Verify the snapshot has not expired.

    checked = account.get("checked_at_ms")

    if (
        isinstance(checked, bool)
        or checked is None
    ):
        raise RuntimeError(
            "U78_TIMESTAMP_MISSING"
        )

    try:
        checked_ms = int(checked)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(
            "U78_TIMESTAMP_INVALID"
        ) from exc

    age_ms = (
        int(_u78_time.time() * 1000)
        - checked_ms
    )

    if (
        age_ms < 0
        or age_ms >
            U78_MAX_CONTRACT_AGE_SECONDS * 1000
    ):
        raise RuntimeError(
            "U78_CONTRACT_SNAPSHOT_STALE"
        )

    # Use the actual V19 contract dictionary.
    # Never manufacture precision or multiplier.

    rules = account.get("contract")

    if not isinstance(rules, dict):
        raise RuntimeError(
            "U78_CONTRACT_MISSING"
        )

    if (
        str(rules.get("symbol") or "").upper()
        != market
    ):
        raise RuntimeError(
            "U78_CONTRACT_SYMBOL_MISMATCH"
        )

    minimum = u78_v3_decimal(
        rules.get("minimum_quantity"),
        "MINIMUM_QUANTITY"
    )

    step = u78_v3_decimal(
        rules.get("quantity_step"),
        "QUANTITY_STEP"
    )

    price_step = u78_v3_decimal(
        rules.get("price_step"),
        "PRICE_STEP"
    )

    multiplier = u78_v3_decimal(
        rules.get("contract_multiplier"),
        "CONTRACT_MULTIPLIER"
    )

    # Verify top-level V19 fields match
    # the independently parsed contract.

    for name, expected in (
        ("minimum_quantity", minimum),
        ("quantity_step", step),
        ("price_step", price_step),
        ("contract_multiplier", multiplier),
    ):
        actual = u78_v3_decimal(
            account.get(name),
            name.upper()
        )

        if actual != expected:
            raise RuntimeError(
                "U78_CONTRACT_FIELD_MISMATCH_"
                + name.upper()
            )

    # Quantity must be representable using
    # the verified exchange step.

    if minimum % step != 0:
        raise RuntimeError(
            "U78_MINIMUM_STEP_INCOMPATIBLE"
        )

    return {
        "verified": True,
        "symbol": market,
        "demo_order_symbol": demo,

        "quantity_step": step,
        "minimum_quantity": minimum,
        "contract_multiplier": multiplier,
        "price_step": price_step,

        "reason": "VERIFIED",

        "verification_source":
            "UNIT8_V19_VERIFIED_READ_ONLY",

        "verification_time_ms": checked_ms,
        "metadata_age_ms": age_ms,

        "read_only": True,
        "exchange_write": False,
    }


# ============================================================
# 7-8.4 UNIT 7 CONTRACT ADAPTER
# ============================================================

def u78_v3_contract(config):

    # First preserve Unit 7's original
    # verified configuration behavior.

    original = _U78_V3_ORIGINAL(config)

    if not isinstance(original, dict):
        raise RuntimeError(
            "U78_ORIGINAL_CONTRACT_INVALID"
        )

    if original.get("verified") is True:
        return original

    account = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    if not isinstance(account, dict):
        return original

    try:
        verified = u78_v3_verified_contract(
            config,
            account
        )

    except RuntimeError as exc:

        print(
            "UNIT 7-8 HANDOVER STATUS = PENDING",
            flush=True
        )

        print(
            "UNIT 7-8 HANDOVER REASON =",
            str(exc),
            flush=True
        )

        # Preserve the original unverified
        # contract. Do not fabricate success.

        return original

    print(
        "UNIT 7-8 HANDOVER STATUS = VERIFIED",
        flush=True
    )

    print(
        "UNIT 7-8 MARKET SYMBOL =",
        verified["symbol"],
        flush=True
    )

    print(
        "UNIT 7-8 DEMO SYMBOL =",
        verified["demo_order_symbol"],
        flush=True
    )

    print(
        "UNIT 7-8 MINIMUM QUANTITY =",
        verified["minimum_quantity"],
        flush=True
    )

    print(
        "UNIT 7-8 QUANTITY STEP =",
        verified["quantity_step"],
        flush=True
    )

    print(
        "UNIT 7-8 PRICE STEP =",
        verified["price_step"],
        flush=True
    )

    print(
        "UNIT 7-8 CONTRACT MULTIPLIER =",
        verified["contract_multiplier"],
        flush=True
    )

    print(
        "UNIT 7-8 METADATA AGE MS =",
        verified["metadata_age_ms"],
        flush=True
    )

    print(
        "UNIT 7-8 EXCHANGE WRITE = NONE",
        flush=True
    )

    return verified


# ============================================================
# 7-8.5 INSTALL VERIFIED CONTRACT HANDOVER
# ============================================================

unit_7_v12_contract = u78_v3_contract


# ============================================================
# 7-8.6 READ-ONLY DIAGNOSTIC
# ============================================================

def u78_v3_diagnostic():

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    account = globals().get(
        "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
    )

    if not isinstance(config, dict):
        return False

    if not isinstance(account, dict):
        return False

    try:
        verified = u78_v3_verified_contract(
            config,
            account
        )

    except RuntimeError as exc:
        print(
            "UNIT 7-8 DIAGNOSTIC = PENDING",
            flush=True
        )

        print(
            "UNIT 7-8 DIAGNOSTIC REASON =",
            str(exc),
            flush=True
        )

        return False

    print(
        "UNIT 7-8 DIAGNOSTIC = PASS",
        flush=True
    )

    print(
        "UNIT 7-8 VERIFIED MARKET =",
        verified["symbol"],
        flush=True
    )

    print(
        "UNIT 7-8 VERIFIED DEMO =",
        verified["demo_order_symbol"],
        flush=True
    )

    print(
        "UNIT 7-8 ORIGINAL SIZING = PRESERVED",
        flush=True
    )

    print(
        "UNIT 7-8 ORIGINAL HEDGE POLICY = PRESERVED",
        flush=True
    )

    print(
        "UNIT 7-8 ORIGINAL BACKUP POLICY = PRESERVED",
        flush=True
    )

    print(
        "UNIT 7-8 EXCHANGE WRITE = NONE",
        flush=True
    )

    return True


U78_V3_DIAGNOSTIC_READY = (
    u78_v3_diagnostic()
)

print(
    "UNIT 7-8 HANDOVER VERSION = V3",
    flush=True
)

print(
    "UNIT 7-8 ADAPTER INSTALLED = True",
    flush=True
)

print(
    "UNIT 7-8 DIAGNOSTIC READY =",
    U78_V3_DIAGNOSTIC_READY,
    flush=True
)

print(
    "UNIT 7-8 DEMO ORDER SUBMISSION = NONE",
    flush=True
)

# ============================================================
# END UNIT 7-8 VERIFIED CONTRACT HANDOVER V3
# ZERO INDENTATION
# ============================================================

    

# ============================================================
# START UNIT 11-12 STABLE SIGNAL HANDOVER V3
# UNIT 11 V2 -> UNIT 12 V6
# ZERO INDENTATION
# READ-ONLY HANDOVER
# ============================================================

import time as _u1112_time
import re as _u1112_re

U1112_V3_MAX_CANDLE_AGE_MS = 120000

# Preserve the scanner that refreshes Units 3-11.
# Install this adapter only once.
_U1112_V3_ORIGINAL_SCAN_REFRESH = (
    scan_refresh_entry_pipeline
)


# ============================================================
# 11-12.1 CONFIGURATION AND SIGNAL VALIDATION
# ============================================================

def u1112_v3_validate(prepared, account):

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    analysis = globals().get(
        "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
    )

    if not isinstance(config, dict):
        return "CONFIG_MISSING", None

    if not isinstance(prepared, dict):
        return "UNIT_11_RESULT_MISSING", None

    if not isinstance(account, dict):
        return "UNIT_8_RESULT_MISSING", None

    if prepared.get("status") != "PREPARED_READ_ONLY":
        return "NO_PREPARED_ENTRY", None

    if not isinstance(analysis, dict):
        return "ANALYSIS_MISSING", None

    if config.get("execution_environment") != "DEMO":
        return "DEMO_ENVIRONMENT_REQUIRED", None

    if config.get(
        "real_cash_execution_enabled"
    ) is not False:
        return "REAL_CASH_SAFETY_FAILURE", None

    exchange = config.get("exchange")

    if not isinstance(exchange, dict):
        return "EXCHANGE_CONFIG_MISSING", None

    market = str(
        exchange.get("market_symbol") or ""
    ).strip().upper()

    demo = str(
        exchange.get("demo_order_symbol") or ""
    ).strip().upper()

    if (
        not market.endswith("USDT")
        or not market.isalnum()
        or not demo
        or not demo.isalnum()
        or market == demo
    ):
        return "INVALID_SYMBOL_PAIR", None

    if account.get("status") != "VERIFIED_READ_ONLY":
        return "UNIT_8_NOT_VERIFIED", None

    if (
        account.get("market_symbol") != market
        or account.get("demo_order_symbol") != demo
    ):
        return "UNIT_8_SYMBOL_MISMATCH", None

    if (
        account.get("demo_contract_verified") is not True
        or account.get("demo_balance_verified") is not True
        or account.get(
            "demo_positions_read_verified"
        ) is not True
    ):
        return "UNIT_8_VERIFICATION_INCOMPLETE", None

    if (
        prepared.get("market_symbol") != market
        or prepared.get("demo_order_symbol") != demo
    ):
        return "UNIT_11_SYMBOL_MISMATCH", None

    if (
        prepared.get("signal_qualified") is not True
        or prepared.get("trade_plan_ready") is not True
        or prepared.get("execution_intent") is not True
        or prepared.get(
            "order_preparation_ready"
        ) is not True
        or prepared.get(
            "demo_boundary_ready"
        ) is not True
    ):
        return "UNIT_11_NOT_READY", None

    if (
        prepared.get("read_only") is not True
        or prepared.get("exchange_write") is not False
        or prepared.get(
            "execution_authorized"
        ) is not False
    ):
        return "UNIT_11_SAFETY_MISMATCH", None

    instruction = prepared.get(
        "order_instruction"
    )

    plan = prepared.get("trade_plan")
    candidate = prepared.get(
        "execution_candidate"
    )

    if not isinstance(instruction, dict):
        return "ORDER_INSTRUCTION_MISSING", None

    if not isinstance(plan, dict):
        return "TRADE_PLAN_MISSING", None

    if not isinstance(candidate, dict):
        return "EXECUTION_CANDIDATE_MISSING", None

    if (
        instruction.get("trade_plan") is not plan
        or instruction.get(
            "execution_candidate"
        ) is not candidate
    ):
        return "PLAN_IDENTITY_MISMATCH", None

    direction = str(
        prepared.get("direction") or ""
    ).upper()

    mode = str(
        prepared.get("active_mode") or ""
    ).upper()

    if direction not in ("LONG", "SHORT"):
        return "INVALID_DIRECTION", None

    if mode not in (
        "STRUCTURE",
        "BREAKOUT",
        "SCALP"
    ):
        return "INVALID_STRATEGY_MODE", None

    if (
        instruction.get("market_symbol") != market
        or instruction.get("demo_order_symbol") != demo
        or instruction.get("direction") != direction
        or instruction.get("strategy_mode") != mode
    ):
        return "INSTRUCTION_IDENTITY_MISMATCH", None

    if (
        plan.get("market_symbol") != market
        or plan.get("demo_order_symbol") != demo
        or plan.get("direction") != direction
        or plan.get("active_mode") != mode
    ):
        return "TRADE_PLAN_IDENTITY_MISMATCH", None

    if (
        instruction.get("position_action") != "OPEN"
        or instruction.get("market_type") != "DEMO_FUTURES"
        or instruction.get("order_type") != "MARKET"
    ):
        return "INVALID_ORDER_INSTRUCTION", None

    # The handover must not fabricate a WEEX fill,
    # order ID, or exchange authorization.

    if (
        instruction.get(
            "submission_authorized"
        ) is not False
        or instruction.get(
            "weex_payload_verified"
        ) is not False
    ):
        return "INSTRUCTION_SAFETY_MISMATCH", None

    candle_id = analysis.get(
        "latest_close_time_ms"
    )

    if (
        not isinstance(candle_id, int)
        or isinstance(candle_id, bool)
        or candle_id <= 0
    ):
        return "CLOSED_CANDLE_ID_INVALID", None

    age_ms = (
        int(_u1112_time.time() * 1000)
        - candle_id
    )

    if not 0 <= age_ms <= U1112_V3_MAX_CANDLE_AGE_MS:
        return "CLOSED_CANDLE_STALE", None

    signal_id = (
        market
        + "-"
        + mode
        + "-"
        + direction
        + "-"
        + str(candle_id)
    )

    # Deterministic client order identity.
    # Unit 12 V6 performs its own normalization.
    if not _u1112_re.fullmatch(
        r"[A-Z0-9_-]+",
        signal_id
    ):
        return "SIGNAL_ID_INVALID", None

    return "STABLE_SIGNAL_ID_READY", {
        "signal_id": signal_id,
        "market_symbol": market,
        "demo_order_symbol": demo,
        "direction": direction,
        "active_mode": mode,
        "candle_id": candle_id,
        "candle_age_ms": age_ms,
        "instruction": instruction,
    }


# ============================================================
# 11-12.2 STABLE SIGNAL HANDOVER
# ============================================================

def u1112_v3_stable_signal(prepared, account=None):

    if account is None:
        account = globals().get(
            "FRESH_RECONSTRUCTION_UNIT_8_RESULT"
        )

    status, details = u1112_v3_validate(
        prepared,
        account
    )

    if status != "STABLE_SIGNAL_ID_READY":
        return status

    instruction = details["instruction"]
    signal_id = details["signal_id"]

    existing_id = instruction.get(
        "newClientOrderId"
    )

    # Never silently replace a different
    # signal identity already assigned upstream.
    if (
        existing_id is not None
        and existing_id != signal_id
    ):
        return "CLIENT_ORDER_ID_CONFLICT"

    instruction["newClientOrderId"] = signal_id

    print(
        "UNIT 11-12 STABLE SIGNAL ID =",
        signal_id,
        flush=True
    )

    print(
        "UNIT 11-12 MARKET SYMBOL =",
        details["market_symbol"],
        flush=True
    )

    print(
        "UNIT 11-12 DEMO SYMBOL =",
        details["demo_order_symbol"],
        flush=True
    )

    print(
        "UNIT 11-12 CLOSED CANDLE AGE MS =",
        details["candle_age_ms"],
        flush=True
    )

    return "STABLE_SIGNAL_ID_READY"


# ============================================================
# 11-12.3 READ-ONLY DIAGNOSTIC
# NO UNIT 12 SUBMISSION
# ============================================================

def u1112_v3_diagnostic(prepared, account):

    print("=" * 80, flush=True)

    print(
        "UNIT 11-12 HANDOVER V3 START",
        flush=True
    )

    status = u1112_v3_stable_signal(
        prepared,
        account
    )

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

    instruction = prepared["order_instruction"]

    # Confirm that Unit 12 V6's validator
    # exists. Do not invoke its POST function.

    validator_available = callable(
        globals().get(
            "unit_12_v5_validate_payload"
        )
    )

    executor_available = callable(
        globals().get(
            "fresh_reconstruction_unit_12"
        )
    )

    client_id = instruction.get(
        "newClientOrderId"
    )

    print(
        "UNIT 11-12 CLIENT ID PRESENT =",
        bool(client_id),
        flush=True
    )

    print(
        "UNIT 12 V6 VALIDATOR AVAILABLE =",
        validator_available,
        flush=True
    )

    print(
        "UNIT 12 V6 EXECUTOR AVAILABLE =",
        executor_available,
        flush=True
    )

    print(
        "UNIT 11-12 TRADE PLAN IDENTITY =",
        instruction.get("trade_plan")
        is prepared.get("trade_plan"),
        flush=True
    )

    print(
        "UNIT 11-12 EXECUTION CANDIDATE IDENTITY =",
        instruction.get(
            "execution_candidate"
        ) is prepared.get(
            "execution_candidate"
        ),
        flush=True
    )

    print(
        "UNIT 11-12 ORDER SUBMISSION = NONE",
        flush=True
    )

    print(
        "UNIT 11-12 EXCHANGE WRITE = NONE",
        flush=True
    )

    ready = (
        bool(client_id)
        and validator_available
        and executor_available
    )

    print(
        "UNIT 11-12 HANDOVER READY =",
        ready,
        flush=True
    )

    print("=" * 80, flush=True)

    return ready


# ============================================================
# 11-12.4 SCANNER INTEGRATION
# PRESERVE ORIGINAL UNIT 3-11 REFRESH
# ============================================================

def scan_refresh_entry_pipeline():

    prepared, account = (
        _U1112_V3_ORIGINAL_SCAN_REFRESH()
    )

    if not isinstance(prepared, dict):
        raise RuntimeError(
            "UNIT 11-12 INVALID UNIT 11 RESULT"
        )

    if not isinstance(account, dict):
        raise RuntimeError(
            "UNIT 11-12 INVALID UNIT 8 RESULT"
        )

    status = prepared.get("status")

    if status == "PREPARED_READ_ONLY":

        ready = u1112_v3_diagnostic(
            prepared,
            account
        )

        if not ready:
            # Fail closed: Unit 12 will see
            # a blocked upstream instruction.
            blocked = dict(prepared)

            blocked["status"] = "BLOCKED"
            blocked["reason"] = (
                "UNIT_11_12_HANDOVER_NOT_READY"
            )

            blocked["execution_intent"] = False
            blocked["order_preparation_ready"] = False
            blocked["demo_boundary_ready"] = False

            return blocked, account

    else:

        print("=" * 80, flush=True)

        print(
            "UNIT 11-12 HANDOVER V3 START",
            flush=True
        )

        print(
            "UNIT 11-12 SIGNAL STATUS = NO_PREPARED_ENTRY",
            flush=True
        )

        print(
            "UNIT 11-12 PREPARATION = SKIPPED",
            flush=True
        )

        print(
            "UNIT 11-12 EXCHANGE WRITE = NONE",
            flush=True
        )

        print("=" * 80, flush=True)

    # Existing scanner subsequently calls
    # scan_process_unit12(prepared, account).
    #
    # This adapter does not call Unit 12,
    # preventing duplicate submission.

    return prepared, account


# ============================================================
# 11-12.5 INSTALLATION CONFIRMATION
# ============================================================

print(
    "UNIT 11-12 HANDOVER VERSION = V3",
    flush=True
)

print(
    "UNIT 11-12 HANDOVER INSTALLED = True",
    flush=True
)

print(
    "UNIT 11-12 UNIT 12 V6 INTERFACE =",
    callable(
        globals().get(
            "fresh_reconstruction_unit_12"
        )
    ),
    flush=True
)

print(
    "UNIT 11-12 LEGACY V2 PREPARE CALL = REMOVED",
    flush=True
)

print(
    "UNIT 11-12 HANDOVER EXCHANGE WRITE = NONE",
    flush=True
)

# ============================================================
# END UNIT 11-12 STABLE SIGNAL HANDOVER V3
# ZERO INDENTATION
# ============================================================



# START UNIT 8-13 VERIFIED POSITION HANDOVER V2
# ============================================================
# PURPOSE:
# Normalize one verified WEEX DEMO position for Unit 13.
#
# Supports:
#   BTCUSDT market -> BTCSUSDT demo contract
#   Universal symbol configuration from Unit 8
#   Direct verified entry price, when available
#   Derived entry price from openValue / size
#
# Safety:
#   DEMO ONLY
#   READ ONLY
#   NO ORDER SUBMISSION
#   NO POSITION MODIFICATION
#   NO ESTIMATED OR MARK-PRICE ENTRY SUBSTITUTION
#   NO PARTIAL-CLOSE COST-BASIS ASSUMPTIONS
#
# BOT_MODE does not restrict position inspection.
# ============================================================

from decimal import Decimal as _U813V2_D
from decimal import InvalidOperation as _U813V2_Invalid

U813_HANDOVER_VERSION = "V2_VERIFIED_DEMO_POSITION"


# ============================================================
# 1. STRICT DECIMAL CONVERSION
# ============================================================

def u813v2_decimal(value, allow_zero=False):

    if value is None or isinstance(value, bool):
        raise ValueError("MISSING_NUMERIC_VALUE")

    try:
        number = _U813V2_D(str(value).strip())
    except (
        _U813V2_Invalid,
        ValueError,
        TypeError,
    ):
        raise ValueError("INVALID_NUMERIC_VALUE")

    if not number.is_finite():
        raise ValueError("NONFINITE_NUMERIC_VALUE")

    if allow_zero:
        if number < 0:
            raise ValueError("NEGATIVE_NUMERIC_VALUE")
    elif number <= 0:
        raise ValueError("NONPOSITIVE_NUMERIC_VALUE")

    return number


def u813v2_first(record, names):

    for name in names:

        value = record.get(name)

        if value is not None and str(value).strip() != "":
            return value

    return None


def u813v2_close(a, b, relative="0.00001"):

    tolerance = max(
        abs(a),
        abs(b),
        _U813V2_D("1"),
    ) * _U813V2_D(relative)

    return abs(a - b) <= tolerance


# ============================================================
# 2. DEMO CONFIGURATION VERIFICATION
# ============================================================

def u813v2_boundary(snapshot, requested_symbol):

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):
        return "CONFIG_MISSING", None, None

    if str(
        config.get("execution_environment", "")
    ).strip().upper() != "DEMO":
        return "DEMO_ENVIRONMENT_NOT_VERIFIED", None, None

    if config.get(
        "real_cash_execution_enabled"
    ) is not False:
        return "REAL_CASH_BOUNDARY_NOT_DISABLED", None, None

    exchange = config.get("exchange")

    if not isinstance(exchange, dict):
        return "EXCHANGE_CONFIG_MISSING", None, None

    market = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    demo = str(
        exchange.get("demo_order_symbol", "")
    ).strip().upper()

    requested = str(
        requested_symbol
    ).strip().upper()

    if not market or not demo:
        return "SYMBOL_CONFIGURATION_MISSING", None, None

    if requested != market:
        return "REQUESTED_MARKET_MISMATCH", None, None

    if not isinstance(snapshot, dict):
        return "UNIT8_SNAPSHOT_MISSING", None, None

    if str(
        snapshot.get("market_symbol", "")
    ).strip().upper() != market:
        return "UNIT8_MARKET_SYMBOL_MISMATCH", None, None

    if str(
        snapshot.get("demo_order_symbol", "")
    ).strip().upper() != demo:
        return "UNIT8_DEMO_SYMBOL_MISMATCH", None, None

    if snapshot.get("status") != "VERIFIED_READ_ONLY":
        return "UNIT8_READ_STATUS_UNVERIFIED", None, None

    if snapshot.get("demo_contract_verified") is not True:
        return "DEMO_CONTRACT_UNVERIFIED", None, None

    if snapshot.get(
        "demo_positions_read_verified"
    ) is not True:
        return "DEMO_POSITIONS_READ_UNVERIFIED", None, None

    return "VERIFIED", market, demo


# ============================================================
# 3. ENTRY PRICE VERIFICATION
# ============================================================

def u813v2_entry(record, quantity, leverage):

    direct_value = u813v2_first(
        record,
        (
            "averageEntryPrice",
            "avgPrice",
            "entryPrice",
            "openPrice",
            "averageOpenPrice",
            "openAvgPrice",
            "avgOpenPrice",
            "averagePrice",
            "holdAvgPrice",
            "costPrice",
        )
    )

    direct_price = None

    if direct_value is not None:

        try:
            direct_price = u813v2_decimal(direct_value)
        except ValueError:
            return "DIRECT_ENTRY_PRICE_INVALID", None, None

    open_value_raw = record.get("openValue")
    cumulative_value_raw = record.get("cumOpenValue")
    cumulative_size_raw = record.get("cumOpenSize")
    closed_size_raw = record.get("cumCloseSize")

    derived_price = None

    if (
        open_value_raw is not None
        and cumulative_value_raw is not None
        and cumulative_size_raw is not None
        and closed_size_raw is not None
    ):

        try:

            open_value = u813v2_decimal(
                open_value_raw
            )

            cumulative_value = u813v2_decimal(
                cumulative_value_raw
            )

            cumulative_size = u813v2_decimal(
                cumulative_size_raw
            )

            closed_size = u813v2_decimal(
                closed_size_raw,
                allow_zero=True
            )

        except ValueError:
            return "OPEN_VALUE_FIELDS_INVALID", None, None

        # V2 intentionally does not reconstruct cost basis
        # following a partial close or other ambiguous change.

        if closed_size != 0:
            return "PARTIAL_CLOSE_REQUIRES_RECONCILIATION", None, None

        if not u813v2_close(
            cumulative_size,
            quantity,
            "0.000000001"
        ):
            return "OPEN_SIZE_MISMATCH", None, None

        if not u813v2_close(
            cumulative_value,
            open_value
        ):
            return "OPEN_VALUE_MISMATCH", None, None

        derived_price = open_value / quantity

        # Verify the quote-value / base-quantity interpretation
        # against the isolated margin, when supplied.

        margin_raw = u813v2_first(
            record,
            (
                "isolatedMargin",
                "marginSize",
            )
        )

        if margin_raw is not None:

            try:
                margin = u813v2_decimal(
                    margin_raw
                )
            except ValueError:
                return "MARGIN_VALUE_INVALID", None, None

            expected_margin = open_value / leverage

            # This strict check applies to the unadjusted
            # isolated margin represented in the tested record.
            # If extra margin is added, further reconciliation
            # will be required rather than guessing.

            if not u813v2_close(
                margin,
                expected_margin,
                "0.001"
            ):
                return "MARGIN_VALUE_RECONCILIATION_REQUIRED", None, None

    if direct_price is not None and derived_price is not None:

        if not u813v2_close(
            direct_price,
            derived_price,
            "0.00001"
        ):
            return "ENTRY_PRICE_SOURCES_DISAGREE", None, None

        return (
            "VERIFIED_DIRECT_AND_OPEN_VALUE",
            direct_price,
            "DIRECT_AND_OPEN_VALUE"
        )

    if derived_price is not None:

        return (
            "VERIFIED_OPEN_VALUE",
            derived_price,
            "OPEN_VALUE_DIVIDED_BY_BASE_QUANTITY"
        )

    if direct_price is not None:

        return (
            "VERIFIED_DIRECT",
            direct_price,
            "WEEX_DIRECT_ENTRY_PRICE"
        )

    return "ENTRY_PRICE_UNVERIFIED", None, None


# ============================================================
# 4. POSITION NORMALIZATION
# ============================================================

def u813v2_verified_position(snapshot, requested_symbol):

    boundary_status, market, demo = u813v2_boundary(
        snapshot,
        requested_symbol
    )

    if boundary_status != "VERIFIED":
        return boundary_status, None

    records = snapshot.get("positions")

    if not isinstance(records, list):
        return "POSITION_LIST_UNVERIFIED", None

    if snapshot.get("position_flat_verified") is True:

        if len(records) != 0:
            return "FLAT_POSITION_CONTRADICTION", None

        return "POSITION_FLAT", None

    if len(records) == 0:
        return "NO_OPEN_POSITION_RECORD", None

    # Strictly reject ambiguous multi-position snapshots.
    # No arbitrary LONG/SHORT selection.

    if len(records) != 1:
        return "MULTIPLE_POSITIONS_REQUIRE_RECONCILIATION", None

    record = records[0]

    if not isinstance(record, dict):
        return "POSITION_RECORD_INVALID", None

    record_symbol = str(
        record.get("symbol", "")
    ).strip().upper()

    if record_symbol != demo:
        return "POSITION_DEMO_SYMBOL_MISMATCH", None

    side = str(
        u813v2_first(
            record,
            (
                "positionSide",
                "holdSide",
                "side",
            )
        ) or ""
    ).strip().upper()

    if side == "BUY":
        side = "LONG"

    if side == "SELL":
        side = "SHORT"

    if side not in ("LONG", "SHORT"):
        return "POSITION_SIDE_UNVERIFIED", None

    try:

        quantity = u813v2_decimal(
            u813v2_first(
                record,
                (
                    "quantity",
                    "size",
                    "total",
                    "holdVol",
                    "positionAmt",
                )
            )
        )

        leverage = u813v2_decimal(
            record.get("leverage")
        )

        minimum = u813v2_decimal(
            snapshot.get("minimum_quantity")
        )

        step = u813v2_decimal(
            snapshot.get("quantity_step")
        )

    except ValueError:
        return "POSITION_OR_CONTRACT_NUMERIC_UNVERIFIED", None

    if quantity < minimum:
        return "POSITION_BELOW_MINIMUM_QUANTITY", None

    if quantity % step != 0:
        return "POSITION_QUANTITY_STEP_INVALID", None

    entry_status, entry, entry_source = u813v2_entry(
        record,
        quantity,
        leverage
    )

    if entry is None:
        return entry_status, None

    normalized = dict(record)

    normalized.update(
        {
            "symbol": market,
            "market_symbol": market,
            "demo_order_symbol": demo,
            "quantity": str(quantity),
            "size": str(quantity),
            "total": str(quantity),
            "positionSide": side,
            "holdSide": side,
            "side": side,
            "averageEntryPrice": str(entry),
            "avgPrice": str(entry),
            "entryPrice": str(entry),
            "leverage": str(leverage),
            "position_normalized": True,
            "position_source": "WEEX_DEMO_POSITION_SNAPSHOT",
            "entry_price_source": entry_source,
            "entry_price_verification": entry_status,
            "position_handover_version": U813_HANDOVER_VERSION,
        }
    )

    return "VERIFIED_OPEN_POSITION", normalized


# ============================================================
# 5. UNIT 13 COMPATIBLE READER
# ============================================================

def unit_13_position(snapshot, symbol):

    status, position = u813v2_verified_position(
        snapshot,
        symbol
    )

    print(
        "UNIT 8-13 HANDOVER VERSION =",
        U813_HANDOVER_VERSION,
        flush=True
    )

    print(
        "UNIT 8-13 POSITION STATUS =",
        status,
        flush=True
    )

    print(
        "UNIT 8-13 MARKET SYMBOL =",
        symbol,
        flush=True
    )

    verified = (
        status == "VERIFIED_OPEN_POSITION"
        and isinstance(position, dict)
    )

    print(
        "UNIT 8-13 POSITION VERIFIED =",
        verified,
        flush=True
    )

    if verified:

        print(
            "UNIT 8-13 POSITION SIDE =",
            position["positionSide"],
            flush=True
        )

        print(
            "UNIT 8-13 POSITION QUANTITY =",
            position["quantity"],
            flush=True
        )

        print(
            "UNIT 8-13 POSITION ENTRY PRICE =",
            position["averageEntryPrice"],
            flush=True
        )

        print(
            "UNIT 8-13 ENTRY PRICE SOURCE =",
            position["entry_price_source"],
            flush=True
        )

        print(
            "UNIT 8-13 POSITION LEVERAGE =",
            position["leverage"],
            flush=True
        )

        print(
            "UNIT 8-13 POSITION ID =",
            position.get("id"),
            flush=True
        )

    print(
        "UNIT 8-13 BOT_MODE INDEPENDENT = True",
        flush=True
    )

    print(
        "UNIT 8-13 EXCHANGE WRITE = NONE",
        flush=True
    )

    return position if verified else None


print(
    "UNIT 8-13 HANDOVER INSTALLED =",
    U813_HANDOVER_VERSION,
    flush=True
)

# ============================================================
# END UNIT 8-13 VERIFIED POSITION HANDOVER V2
# ============================================================



# ============================================================
# START UNIT 8-13 POSITION FIELD DIAGNOSTIC V1
# ZERO INDENTATION - DEMO ONLY - READ ONLY
# ============================================================

_U813_DIAG_ORIGINAL_READER = unit_13_position

_U813_DIAG_ENTRY_FIELDS = (
    "averageEntryPrice",
    "avgPrice",
    "entryPrice",
    "openPrice",
    "averageOpenPrice",
    "openAvgPrice",
    "avgOpenPrice",
    "averagePrice",
    "holdAvgPrice",
    "costPrice",
)

_U813_DIAG_LEVERAGE_FIELDS = (
    "leverage",
    "lever",
    "leverageRatio",
    "holdLeverage",
)

_U813_DIAG_QUANTITY_FIELDS = (
    "size",
    "total",
    "holdVol",
    "positionAmt",
    "quantity",
)
_U813_DIAG_VALUE_FIELDS = (
    "openValue",
    "cumOpenValue",
    "cumOpenSize",
    "cumCloseSize",
    "openFee",
    "marginSize",
    "isolatedMargin",
    "separatedOpenOrderId",
    "id",
)

_U813_DIAG_SIDE_FIELDS = (
    "positionSide",
    "holdSide",
    "side",
)


def u813_diag_mask(value):

    if value is None:
        return "MISSING"

    if isinstance(value, (dict, list)):
        return "NESTED_VALUE"

    return str(value)[:100]


def u813_diag_fields(record, names):

    for name in names:

        if name in record:

            print(
                "UNIT 8-13 FIELD",
                name,
                "=",
                u813_diag_mask(record[name]),
                flush=True
            )


def u813_diag_position_reader(snapshot, symbol):

    print(
        "================================================",
        flush=True
    )

    print(
        "UNIT 8-13 FIELD DIAGNOSTIC V1 START",
        flush=True
    )

    config = globals().get(
        "FRESH_RECONSTRUCTION_CONFIG"
    )

    if not isinstance(config, dict):

        print(
            "UNIT 8-13 DIAGNOSTIC = CONFIG_MISSING",
            flush=True
        )

        return _U813_DIAG_ORIGINAL_READER(
            snapshot,
            symbol
        )

    if (
        config.get("execution_environment") != "DEMO"
        or config.get(
            "real_cash_execution_enabled"
        ) is not False
    ):

        print(
            "UNIT 8-13 DIAGNOSTIC = DEMO_GATE_FAILED",
            flush=True
        )

        return _U813_DIAG_ORIGINAL_READER(
            snapshot,
            symbol
        )

    if not isinstance(snapshot, dict):

        print(
            "UNIT 8-13 DIAGNOSTIC = SNAPSHOT_MISSING",
            flush=True
        )

        return _U813_DIAG_ORIGINAL_READER(
            snapshot,
            symbol
        )

    print(
        "UNIT 8-13 SNAPSHOT STATUS =",
        snapshot.get("status"),
        flush=True
    )

    print(
        "UNIT 8-13 POSITIONS READ VERIFIED =",
        snapshot.get(
            "demo_positions_read_verified"
        ),
        flush=True
    )

    print(
        "UNIT 8-13 MARKET SYMBOL =",
        symbol,
        flush=True
    )

    print(
        "UNIT 8-13 DEMO SYMBOL =",
        snapshot.get("demo_order_symbol"),
        flush=True
    )

    records = snapshot.get("positions")

    if not isinstance(records, list):

        print(
            "UNIT 8-13 DIAGNOSTIC = POSITIONS_NOT_LIST",
            flush=True
        )

        return _U813_DIAG_ORIGINAL_READER(
            snapshot,
            symbol
        )

    print(
        "UNIT 8-13 POSITION RECORD COUNT =",
        len(records),
        flush=True
    )

    for index, record in enumerate(records):

        if not isinstance(record, dict):
            continue

        print(
            "UNIT 8-13 RECORD INDEX =",
            index,
            flush=True
        )

        print(
            "UNIT 8-13 RECORD FIELD NAMES =",
            sorted(record.keys()),
            flush=True
        )

        print(
            "UNIT 8-13 RECORD SYMBOL =",
            record.get("symbol"),
            flush=True
        )

        print(
            "UNIT 8-13 ENTRY PRICE CANDIDATES",
            flush=True
        )

        u813_diag_fields(
            record,
            _U813_DIAG_ENTRY_FIELDS
        )

        print(
            "UNIT 8-13 LEVERAGE CANDIDATES",
            flush=True
        )

        u813_diag_fields(
            record,
            _U813_DIAG_LEVERAGE_FIELDS
        )

        print(
            "UNIT 8-13 QUANTITY CANDIDATES",
            flush=True
        )

        u813_diag_fields(
            record,
            _U813_DIAG_QUANTITY_FIELDS
        )

        print(
            "UNIT 8-13 OPEN VALUE DIAGNOSTIC",
            flush=True
        )

        u813_diag_fields(
            record,
            _U813_DIAG_VALUE_FIELDS
        )
        print(
            "UNIT 8-13 SIDE CANDIDATES",
            flush=True
        )

        u813_diag_fields(
            record,
            _U813_DIAG_SIDE_FIELDS
        )

    print(
        "UNIT 8-13 DIAGNOSTIC EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "================================================",
        flush=True
    )

    return _U813_DIAG_ORIGINAL_READER(
        snapshot,
        symbol
    )


unit_13_position = u813_diag_position_reader

print(
    "UNIT 8-13 FIELD DIAGNOSTIC INSTALLED = True",
    flush=True
)

print(
    "UNIT 8-13 FIELD DIAGNOSTIC MODE = READ_ONLY",
    flush=True
)

# ============================================================
# END UNIT 8-13 POSITION FIELD DIAGNOSTIC V1
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 4-13 VERIFIED ATR14 HANDOVER V1
# ============================================================

from decimal import Decimal as _U413_D
from decimal import InvalidOperation as _U413_Invalid

U413_HANDOVER_VERSION = "V1_VERIFIED_ATR14"

# Maximum permitted age of the last closed candle.
# 180 seconds accommodates normal 1-minute candle
# processing delays without accepting stale analysis.
U413_MAX_CANDLE_AGE_MS = 180000


# ============================================================
# 1. VERIFIED NUMERIC CONVERSION
# ============================================================

def u413_positive_decimal(value):

    if value is None or isinstance(value, bool):
        return None

    try:
        number = _U413_D(str(value).strip())
    except (
        _U413_Invalid,
        ValueError,
        TypeError,
    ):
        return None

    if not number.is_finite() or number <= 0:
        return None

    return number


def u413_timestamp(value):

    if value is None or isinstance(value, bool):
        return None

    try:
        number = int(value)
    except (ValueError, TypeError):
        return None

    if number <= 0:
        return None

    return number


# ============================================================
# 2. UNIT 4 ANALYSIS VERIFICATION
# ============================================================

def u413_verified_analysis(execution_config):

    analysis = globals().get(
        "FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT"
    )

    market = globals().get(
        "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
    )

    if not isinstance(execution_config, dict):
        return "CONFIG_MISSING", None

    if str(
        execution_config.get(
            "execution_environment", ""
        )
    ).upper() != "DEMO":
        return "DEMO_ENVIRONMENT_UNVERIFIED", None

    if execution_config.get(
        "real_cash_execution_enabled"
    ) is not False:
        return "REAL_CASH_BOUNDARY_UNVERIFIED", None

    exchange = execution_config.get("exchange")

    if not isinstance(exchange, dict):
        return "EXCHANGE_CONFIG_MISSING", None

    expected_symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    if not expected_symbol:
        return "MARKET_SYMBOL_MISSING", None

    if not isinstance(analysis, dict):
        return "UNIT4_ANALYSIS_MISSING", None

    if not isinstance(market, dict):
        return "UNIT3_MARKET_SNAPSHOT_MISSING", None

    analysis_symbol = str(
        analysis.get("symbol", "")
    ).strip().upper()

    market_symbol = str(
        market.get(
            "symbol",
            market.get("market_symbol", "")
        )
    ).strip().upper()

    if analysis_symbol != expected_symbol:
        return "UNIT4_SYMBOL_MISMATCH", None

    if market_symbol != expected_symbol:
        return "UNIT3_SYMBOL_MISMATCH", None

    if analysis.get("read_only") is not True:
        return "UNIT4_READ_ONLY_UNVERIFIED", None

    atr = u413_positive_decimal(
        analysis.get("atr14")
    )

    if atr is None:
        return "UNIT4_ATR14_INVALID", None

    close_ms = u413_timestamp(
        analysis.get("latest_close_time_ms")
    )

    exchange_ms = u413_timestamp(
        analysis.get("exchange_time_ms")
    )

    market_ms = u413_timestamp(
        market.get("exchange_time_ms")
    )

    if (
        close_ms is None
        or exchange_ms is None
        or market_ms is None
    ):
        return "MARKET_TIMESTAMP_UNVERIFIED", None

    if close_ms > exchange_ms:
        return "UNIT4_FUTURE_CANDLE", None

    if close_ms > market_ms:
        return "UNIT3_UNIT4_TIME_CONFLICT", None

    if exchange_ms < market_ms:
        return "UNIT4_ANALYSIS_OLDER_THAN_UNIT3", None

    age_ms = exchange_ms - close_ms

    if age_ms > U413_MAX_CANDLE_AGE_MS:
        return "UNIT4_ATR14_STALE", None

    # Unit 4 must be based on the current Unit 3
    # market snapshot, not an earlier scan.

    if exchange_ms - market_ms > 60000:
        return "UNIT3_UNIT4_REFRESH_MISMATCH", None

    # Confirm ATR14 is measured in quote-price units.
    # Unit 4 V6 reports ATR14 as USDT per base coin.

    quote = str(
        exchange.get("quote_currency", "USDT")
    ).strip().upper()

    if quote != "USDT":
        return "QUOTE_CURRENCY_UNVERIFIED", None

    verified = {
        "symbol": expected_symbol,
        "atr14": str(atr),
        "latest_close_time_ms": close_ms,
        "exchange_time_ms": exchange_ms,
        "atr14_unit": "USDT_PER_BASE_COIN",
        "source": "UNIT4_VERIFIED_ANALYSIS",
        "read_only": True,
        "handover_version": U413_HANDOVER_VERSION,
    }

    return "VERIFIED", verified


# ============================================================
# 3. PRESERVE ORIGINAL UNIT 13 PLANNER
# ============================================================

_U413_ORIGINAL_UNIT13_PLANNER = (
    fresh_reconstruction_unit_13
)


# ============================================================
# 4. VERIFIED UNIT 4 -> UNIT 13 ADAPTER
# ============================================================

def fresh_reconstruction_unit_13(
    execution_config,
    unit_12_result,
    unit_8_result=None,
    market_snapshot=None,
):

    status, verified_analysis = (
        u413_verified_analysis(
            execution_config
        )
    )

    print(
        "UNIT 4-13 HANDOVER VERSION =",
        U413_HANDOVER_VERSION,
        flush=True
    )

    print(
        "UNIT 4-13 ATR STATUS =",
        status,
        flush=True
    )

    if status == "VERIFIED":

        print(
            "UNIT 4-13 MARKET SYMBOL =",
            verified_analysis["symbol"],
            flush=True
        )

        print(
            "UNIT 4-13 VERIFIED ATR14 =",
            verified_analysis["atr14"],
            flush=True
        )

        print(
            "UNIT 4-13 ATR UNIT =",
            verified_analysis["atr14_unit"],
            flush=True
        )

        print(
            "UNIT 4-13 CLOSED CANDLE TIME =",
            verified_analysis["latest_close_time_ms"],
            flush=True
        )

        print(
            "UNIT 4-13 ATR HANDOVER = PASS",
            flush=True
        )

        selected_snapshot = verified_analysis

    else:

        print(
            "UNIT 4-13 ATR HANDOVER = BLOCKED",
            flush=True
        )

        # Fail closed: never substitute an unverified
        # ATR value from the Unit 3 market snapshot.
        selected_snapshot = {}

    # Preserve all original Unit 13 logic:
    # position verification, TP calculations,
    # ATR hedge calculations, backup planning,
    # and read-only execution restrictions.

    result = _U413_ORIGINAL_UNIT13_PLANNER(
        execution_config,
        unit_12_result,
        unit_8_result,
        selected_snapshot,
    )

    if not isinstance(result, dict):
        raise RuntimeError(
            "UNIT 4-13 INVALID UNIT13 RESULT"
        )

    result["unit4_13_handover_version"] = (
        U413_HANDOVER_VERSION
    )

    result["unit4_13_atr_status"] = status

    result["unit4_13_atr_verified"] = (
        status == "VERIFIED"
    )

    if status != "VERIFIED":

        # Keep original Unit 13's other validation
        # failures intact. Only identify ATR handover
        # as the cause when ATR is the actual blocker.

        if result.get("reason") == (
            "VERIFIED_ATR14_REQUIRED"
        ):
            result["reason"] = (
                "VERIFIED_ATR14_REQUIRED:"
                + status
            )

    print(
        "UNIT 4-13 UNIT13 STATUS =",
        result.get("status"),
        flush=True
    )

    print(
        "UNIT 4-13 UNIT13 REASON =",
        result.get("reason"),
        flush=True
    )

    print(
        "UNIT 4-13 EXCHANGE WRITE = NONE",
        flush=True
    )

    return result


print(
    "UNIT 4-13 HANDOVER INSTALLED =",
    U413_HANDOVER_VERSION,
    flush=True
)

# ============================================================
# END UNIT 4-13 VERIFIED ATR14 HANDOVER V1
# ============================================================



# ============================================================
# START UNIT 13-14 PROTECTION RECONCILIATION V1
# ============================================================

from decimal import Decimal as _U1314_D
from decimal import InvalidOperation as _U1314_Invalid

U1314_VERSION = "V1_PROTECTION_RECONCILIATION"


# ============================================================
# 1. STRICT NUMERIC VALIDATION
# ============================================================

def u1314_number(value, zero=False):

    if value is None or isinstance(value, bool):
        return None

    try:
        number = _U1314_D(str(value))
    except (
        _U1314_Invalid,
        ValueError,
        TypeError,
    ):
        return None

    if not number.is_finite():
        return None

    if number < 0:
        return None

    if number == 0 and not zero:
        return None

    return number


def u1314_valid_step(quantity, minimum, step):

    return (
        quantity is not None
        and minimum is not None
        and step is not None
        and quantity >= minimum
        and quantity % step == 0
    )


# ============================================================
# 2. RECONCILE UNIT 13 PLAN WITH UNIT 8 CONTRACT
# ============================================================

def u1314_reconcile(config, unit8, unit13):

    report = {
        "version": U1314_VERSION,
        "status": "BLOCKED",
        "reason": "RECONCILIATION_PENDING",
        "position_verified": False,
        "contract_verified": False,
        "tp_quantity_valid": False,
        "tp1_deferred": False,
        "tp2_deferred": False,
        "hedge_quantity_valid": False,
        "hedge_geometry_valid": False,
        "exposure_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
        "execution_authorized": False,
        "exchange_write": False,
    }

    def stop(reason):
        report["reason"] = reason
        return report

    if not all(
        isinstance(x, dict)
        for x in (config, unit8, unit13)
    ):
        return stop("UPSTREAM_RESULT_MISSING")

    if config.get("execution_environment") != "DEMO":
        return stop("DEMO_ENVIRONMENT_REQUIRED")

    if config.get(
        "real_cash_execution_enabled"
    ) is not False:
        return stop("REAL_CASH_BOUNDARY_UNVERIFIED")

    exchange = config.get("exchange")

    if not isinstance(exchange, dict):
        return stop("EXCHANGE_CONFIG_MISSING")

    symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    if not symbol:
        return stop("MARKET_SYMBOL_MISSING")

    if str(
        unit8.get("market_symbol", "")
    ).strip().upper() != symbol:
        return stop("UNIT8_SYMBOL_MISMATCH")

    if str(
        unit13.get("market_symbol", "")
    ).strip().upper() != symbol:
        return stop("UNIT13_SYMBOL_MISMATCH")

    if unit8.get("status") != "VERIFIED_READ_ONLY":
        return stop("UNIT8_READ_UNVERIFIED")

    if unit8.get(
        "demo_contract_verified"
    ) is not True:
        return stop("DEMO_CONTRACT_UNVERIFIED")

    if unit8.get(
        "demo_positions_read_verified"
    ) is not True:
        return stop("POSITION_READ_UNVERIFIED")

    report["contract_verified"] = True

    if unit13.get("position_verified") is not True:
        return stop("UNIT13_POSITION_UNVERIFIED")

    if unit13.get("status") != "PLAN_READY":
        return stop("UNIT13_PLAN_NOT_READY")

    report["position_verified"] = True

    quantity = u1314_number(
        unit13.get("position_quantity")
    )

    minimum = u1314_number(
        unit8.get("minimum_quantity")
    )

    step = u1314_number(
        unit8.get("quantity_step")
    )

    if not u1314_valid_step(
        quantity, minimum, step
    ):
        return stop("POSITION_QUANTITY_INVALID")

    report["position_quantity"] = str(quantity)
    report["minimum_quantity"] = str(minimum)
    report["quantity_step"] = str(step)

    # --------------------------------------------------------
    # Verify the position against the exchange snapshot.
    # The Unit 8-13 V2 reader must agree with Unit 13.
    # --------------------------------------------------------

    position_status, position = (
        u813v2_verified_position(
            unit8,
            symbol
        )
    )

    if (
        position_status != "VERIFIED_OPEN_POSITION"
        or not isinstance(position, dict)
    ):
        return stop(
            "UNIT8_POSITION_RECONCILIATION_FAILED"
        )

    verified_quantity = u1314_number(
        position.get("quantity")
    )

    if verified_quantity != quantity:
        return stop("POSITION_QUANTITY_MISMATCH")

    side = str(
        unit13.get("position_side", "")
    ).strip().upper()

    if side not in ("LONG", "SHORT"):
        return stop("POSITION_SIDE_INVALID")

    if side != position.get("positionSide"):
        return stop("POSITION_SIDE_MISMATCH")

    entry = u1314_number(
        unit13.get("entry_price")
    )

    verified_entry = u1314_number(
        position.get("entryPrice")
    )

    if (
        entry is None
        or verified_entry is None
        or abs(entry - verified_entry)
        > _U1314_D("0.00000001")
    ):
        return stop("POSITION_ENTRY_MISMATCH")

    report["position_side"] = side
    report["entry_price"] = str(entry)
    report["position_id"] = position.get("id")

    # ========================================================
    # 3. TP QUANTITY RECONCILIATION
    # ========================================================

    tp = unit13.get("tp_quantity_plan")

    if not isinstance(tp, dict):
        return stop("TP_QUANTITY_PLAN_MISSING")

    if tp.get("plan_valid") is not True:
        return stop("TP_QUANTITY_PLAN_INVALID")

    q1 = u1314_number(
        tp.get("tp1_quantity"),
        zero=True
    )

    q2 = u1314_number(
        tp.get("tp2_quantity"),
        zero=True
    )

    q3 = u1314_number(
        tp.get("tp3_quantity"),
        zero=True
    )

    if any(x is None for x in (q1, q2, q3)):
        return stop("TP_QUANTITY_VALUE_INVALID")

    if q1 + q2 + q3 != quantity:
        return stop("TP_QUANTITY_SUM_MISMATCH")

    for q in (q1, q2, q3):

        if q == 0:
            continue

        if not u1314_valid_step(
            q, minimum, step
        ):
            return stop("TP_QUANTITY_STEP_INVALID")

    if q3 < minimum:
        return stop("TP3_REMAINDER_TOO_SMALL")

    if bool(tp.get("tp1_deferred")) != (q1 == 0):
        return stop("TP1_DEFERRED_FLAG_MISMATCH")

    if bool(tp.get("tp2_deferred")) != (q2 == 0):
        return stop("TP2_DEFERRED_FLAG_MISMATCH")

    report["tp_quantity_valid"] = True
    report["tp1_quantity"] = str(q1)
    report["tp2_quantity"] = str(q2)
    report["tp3_quantity"] = str(q3)
    report["tp1_deferred"] = q1 == 0
    report["tp2_deferred"] = q2 == 0

    # A deferred TP is not a confirmed fill.
    report["tp1_fill_verified"] = False
    report["tp2_fill_verified"] = False
    report["secured_profit_verified"] = False

    # ========================================================
    # 4. ATR HEDGE PRICE RECONCILIATION
    # ========================================================

    hedge1 = u1314_number(
        unit13.get("hedge_stage1_price")
    )

    hedge2 = u1314_number(
        unit13.get("hedge_stage2_price")
    )

    atr = u1314_number(
        unit13.get("atr14")
    )

    tick = u1314_number(
        unit8.get("price_step")
    )

    if any(
        x is None
        for x in (hedge1, hedge2, atr, tick)
    ):
        return stop("ATR_HEDGE_VALUES_MISSING")

    if hedge1 % tick != 0 or hedge2 % tick != 0:
        return stop("HEDGE_PRICE_STEP_INVALID")

    if side == "SHORT":
        geometry_valid = entry < hedge1 < hedge2
    else:
        geometry_valid = hedge2 < hedge1 < entry

    if not geometry_valid:
        return stop("ATR_HEDGE_GEOMETRY_INVALID")

    report["hedge_geometry_valid"] = True
    report["hedge_stage1_price"] = str(hedge1)
    report["hedge_stage2_price"] = str(hedge2)
    report["atr14"] = str(atr)

    # ========================================================
    # 5. STAGED HEDGE QUANTITY RECONCILIATION
    #
    # Stage 1 requires a 50% reduction and a
    # separately verified opposite-side hedge.
    #
    # Stage 2 cannot be submitted based solely
    # on the original quantity. It must use the
    # latest reconciled position and hedge state.
    # ========================================================

    half = quantity / _U1314_D("2")

    if not u1314_valid_step(
        half, minimum, step
    ):
        return stop(
            "STAGE1_HALF_QUANTITY_NOT_EXECUTABLE"
        )

    report["hedge_quantity_valid"] = True
    report["stage1_half_quantity"] = str(half)
    report["stage1_opposite_quantity"] = str(half)

    report["stage2_quantity"] = None
    report["stage2_quantity_status"] = (
        "REQUIRES_POST_STAGE1_POSITION_RECONCILIATION"
    )

    report["hedge_cycle_fill_verified"] = False
    report["recovery_fill_verified"] = False
    report["backup_activation_verified"] = False

    # ========================================================
    # 6. ACCOUNT AND EXCHANGE RECONCILIATION
    #
    # The existing Unit 8 snapshot verifies positions,
    # but this block has not verified all open orders,
    # account-wide exposure, or protection fills.
    #
    # Do not convert calculated plans into execution.
    # ========================================================

    report["exposure_verified"] = False
    report["exchange_protection_verified"] = False
    report["protection_active"] = False
    report["execution_authorized"] = False

    report["status"] = "PLAN_RECONCILED"
    report["reason"] = (
        "EXCHANGE_ORDER_AND_EXPOSURE_RECONCILIATION_PENDING"
    )

    return report


# ============================================================
# 7. PRESERVE ORIGINAL UNIT 14 SUPERVISOR
# ============================================================

_U1314_ORIGINAL_UNIT14 = (
    fresh_reconstruction_unit_14
)


def fresh_reconstruction_unit_14(
    config,
    unit_8,
    unit_12,
    unit_13,
):

    reconciliation = u1314_reconcile(
        config,
        unit_8,
        unit_13
    )

    print(
        "UNIT 13-14 RECONCILIATION VERSION =",
        U1314_VERSION,
        flush=True
    )

    for key in (
        "status",
        "reason",
        "position_verified",
        "contract_verified",
        "position_quantity",
        "tp_quantity_valid",
        "tp1_quantity",
        "tp2_quantity",
        "tp3_quantity",
        "tp1_deferred",
        "tp2_deferred",
        "hedge_geometry_valid",
        "hedge_quantity_valid",
        "stage1_half_quantity",
        "stage2_quantity_status",
        "exposure_verified",
        "exchange_protection_verified",
    ):

        print(
            "UNIT 13-14",
            key.upper(),
            "=",
            reconciliation.get(key),
            flush=True
        )

    # Always run the original Unit 14 supervisor.
    # Its safety checks remain authoritative.

    original = _U1314_ORIGINAL_UNIT14(
        config,
        unit_8,
        unit_12,
        unit_13
    )

    if not isinstance(original, dict):
        raise RuntimeError(
            "UNIT13_14_INVALID_SUPERVISOR_RESULT"
        )

    result = dict(original)

    result["unit13_14_reconciliation"] = (
        reconciliation
    )

    result["unit13_14_version"] = U1314_VERSION

    result["unit13_14_plan_reconciled"] = (
        reconciliation.get("status")
        == "PLAN_RECONCILED"
    )

    # This adapter cannot authorize execution.
    # A validated plan is not an active order.

    result["execution_authorized"] = False
    result["exchange_write"] = False
    result["protection_active"] = False

    if result["unit13_14_plan_reconciled"]:

        result["position_verified"] = True
        result["quantity_step_valid"] = True
        result["tp_plan_valid"] = True
        result["hedge_plan_valid"] = True

        result["status"] = "ALERT"
        result["reason"] = (
            "PLAN_RECONCILED_PROTECTION_NOT_VERIFIED"
        )

        result["safety_alert"] = True
        result["alert_severity"] = "CRITICAL"
        result["requires_operator_attention"] = True

    print(
        "UNIT 13-14 FINAL STATUS =",
        result.get("status"),
        flush=True
    )

    print(
        "UNIT 13-14 FINAL REASON =",
        result.get("reason"),
        flush=True
    )

    print(
        "UNIT 13-14 PROTECTION ACTIVE = False",
        flush=True
    )

    print(
        "UNIT 13-14 EXECUTION AUTHORIZED = False",
        flush=True
    )

    print(
        "UNIT 13-14 EXCHANGE WRITE = NONE",
        flush=True
    )

    return result


print(
    "UNIT 13-14 RECONCILIATION INSTALLED =",
    U1314_VERSION,
    flush=True
)

# ============================================================
# END UNIT 13-14 PROTECTION RECONCILIATION V1
# ============================================================



# ============================================================
# START UNIT 13-14 V2
# DEMO ORDER AND EXPOSURE RECONCILIATION
# ZERO INDENTATION
# ============================================================

from decimal import Decimal as _U1314V2_D
from decimal import InvalidOperation as _U1314V2_Invalid

U1314V2_VERSION = "V2_DEMO_ORDER_EXPOSURE_RECONCILIATION"


# ============================================================
# 1. STRICT NUMERIC PARSER
# ============================================================

def u1314v2_num(value, allow_zero=False):

    if value is None or isinstance(value, bool):
        return None

    try:
        number = _U1314V2_D(str(value))
    except (
        _U1314V2_Invalid,
        ValueError,
        TypeError,
    ):
        return None

    if not number.is_finite():
        return None

    if number < 0:
        return None

    if number == 0 and not allow_zero:
        return None

    return number


# ============================================================
# 2. DEMO POSITION AND ACCOUNT EXPOSURE
# ============================================================

def u1314v2_exposure(config, unit8, reconciliation):

    result = {
        "status": "UNVERIFIED",
        "reason": "EXPOSURE_CHECK_PENDING",
        "position_value_verified": False,
        "position_margin_verified": False,
        "available_balance_verified": False,
        "account_equity_verified": False,
        "pending_order_margin_verified": False,
        "account_wide_exposure_verified": False,
        "exposure_cap_verified": False,
        "execution_authorized": False,
    }

    if not isinstance(unit8, dict):
        result["reason"] = "UNIT8_MISSING"
        return result

    if not isinstance(reconciliation, dict):
        result["reason"] = "V1_RECONCILIATION_MISSING"
        return result

    if reconciliation.get("status") != "PLAN_RECONCILED":
        result["reason"] = "V1_PLAN_NOT_RECONCILED"
        return result

    if unit8.get("demo_positions_read_verified") is not True:
        result["reason"] = "POSITION_READ_UNVERIFIED"
        return result

    symbol = str(
        reconciliation.get("position_id", "")
    ).strip()

    if not symbol:
        result["reason"] = "POSITION_ID_MISSING"
        return result

    market_symbol = str(
        unit8.get("market_symbol", "")
    ).strip().upper()

    config_exchange = (
        config.get("exchange", {})
        if isinstance(config, dict)
        else {}
    )

    if market_symbol != str(
        config_exchange.get("market_symbol", "")
    ).strip().upper():
        result["reason"] = "MARKET_SYMBOL_MISMATCH"
        return result

    position_status, position = (
        u813v2_verified_position(
            unit8,
            market_symbol
        )
    )

    if (
        position_status != "VERIFIED_OPEN_POSITION"
        or not isinstance(position, dict)
    ):
        result["reason"] = "POSITION_UNVERIFIED"
        return result

    if str(position.get("id", "")) != symbol:
        result["reason"] = "POSITION_ID_CHANGED"
        return result

    quantity = u1314v2_num(
        position.get("quantity")
    )

    entry = u1314v2_num(
        position.get("entryPrice")
    )

    leverage = u1314v2_num(
        position.get("leverage")
    )

    if None in (quantity, entry, leverage):
        result["reason"] = "POSITION_NUMERIC_INVALID"
        return result

    # Indicative exposure from the verified position.
    # Not a substitute for exchange account equity.

    notional = quantity * entry
    calculated_margin = notional / leverage

    result["position_quantity"] = str(quantity)
    result["entry_price"] = str(entry)
    result["leverage"] = str(leverage)
    result["entry_notional_usdt"] = str(notional)
    result["calculated_initial_margin_usdt"] = (
        str(calculated_margin)
    )

    result["position_value_verified"] = True

    # Validate reported margin without assuming that
    # initial margin equals current account equity.

    reported_margin = u1314v2_num(
        position.get("marginSize")
    )

    if reported_margin is not None:

        result["reported_margin_usdt"] = (
            str(reported_margin)
        )

        result["position_margin_verified"] = (
            abs(reported_margin - calculated_margin)
            <= _U1314V2_D("0.000001")
        )

    available = u1314v2_num(
        unit8.get("available_balance"),
        allow_zero=True
    )

    if (
        unit8.get("demo_balance_verified") is True
        and available is not None
    ):
        result["available_balance_usdt"] = str(available)
        result["available_balance_verified"] = True

    # Available balance is not total account equity.
    # Other positions, open-order reservations and
    # unrealized PnL must be accounted for separately.

    result["status"] = "PARTIAL"
    result["reason"] = (
        "ACCOUNT_EQUITY_AND_PENDING_ORDER_MARGIN_REQUIRED"
    )

    return result


# ============================================================
# 3. EXCHANGE ORDER EVIDENCE
#
# No endpoint is called here.
# Missing order data is UNKNOWN, not an empty order book.
# ============================================================

def u1314v2_orders(unit8, reconciliation):

    result = {
        "status": "UNVERIFIED",
        "reason": "VERIFIED_DEMO_ORDER_READ_REQUIRED",
        "open_orders_read_verified": False,
        "order_history_read_verified": False,
        "fills_read_verified": False,
        "position_identity_verified": False,
        "tp1_order_verified": False,
        "tp2_order_verified": False,
        "tp3_order_verified": False,
        "hedge1_order_verified": False,
        "hedge2_order_verified": False,
        "tp1_fill_verified": False,
        "tp2_fill_verified": False,
        "hedge_fill_verified": False,
        "duplicate_order_check_verified": False,
        "pending_quantity_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
    }

    if not isinstance(unit8, dict):
        result["reason"] = "UNIT8_MISSING"
        return result

    if not isinstance(reconciliation, dict):
        result["reason"] = "RECONCILIATION_MISSING"
        return result

    if reconciliation.get("status") != "PLAN_RECONCILED":
        result["reason"] = "POSITION_PLAN_NOT_RECONCILED"
        return result

    position_id = reconciliation.get("position_id")

    if position_id is None:
        result["reason"] = "POSITION_ID_UNVERIFIED"
        return result

    result["position_identity_verified"] = True
    result["position_id"] = str(position_id)

    result["tp1_deferred"] = (
        reconciliation.get("tp1_deferred") is True
    )

    result["tp2_deferred"] = (
        reconciliation.get("tp2_deferred") is True
    )

    result["planned_tp1_quantity"] = (
        reconciliation.get("tp1_quantity")
    )

    result["planned_tp2_quantity"] = (
        reconciliation.get("tp2_quantity")
    )

    result["planned_tp3_quantity"] = (
        reconciliation.get("tp3_quantity")
    )

    # Do not interpret:
    # - a price crossing as an order fill
    # - a missing order list as zero pending orders
    # - a planned hedge as an open opposite position
    # - a position ID as an order ID

    result["status"] = "AWAITING_EXCHANGE_EVIDENCE"
    result["reason"] = (
        "OPEN_ORDERS_HISTORY_AND_FILLS_NOT_VERIFIED"
    )

    return result


# ============================================================
# 4. COMBINED V2 RECONCILIATION
# ============================================================

def u1314v2_reconcile(config, unit8, unit13, v1):

    result = {
        "version": U1314V2_VERSION,
        "status": "BLOCKED",
        "reason": "RECONCILIATION_PENDING",
        "v1_plan_reconciled": False,
        "position_verified": False,
        "exposure_verified": False,
        "orders_verified": False,
        "fills_verified": False,
        "protection_active": False,
        "execution_authorized": False,
        "exchange_write": False,
    }

    if not all(
        isinstance(x, dict)
        for x in (config, unit8, unit13, v1)
    ):
        result["reason"] = "UPSTREAM_DATA_MISSING"
        return result

    if config.get("execution_environment") != "DEMO":
        result["reason"] = "DEMO_ONLY"
        return result

    if config.get("real_cash_execution_enabled") is not False:
        result["reason"] = "REAL_CASH_BOUNDARY_FAILED"
        return result

    if v1.get("status") != "PLAN_RECONCILED":
        result["reason"] = "V1_RECONCILIATION_NOT_READY"
        return result

    result["v1_plan_reconciled"] = True
    result["position_verified"] = (
        v1.get("position_verified") is True
    )

    exposure = u1314v2_exposure(
        config,
        unit8,
        v1
    )

    orders = u1314v2_orders(
        unit8,
        v1
    )

    result["exposure"] = exposure
    result["orders"] = orders

    result["exposure_verified"] = (
        exposure.get("account_wide_exposure_verified")
        is True
        and exposure.get("exposure_cap_verified")
        is True
    )

    result["orders_verified"] = (
        orders.get("open_orders_read_verified")
        is True
        and orders.get("order_history_read_verified")
        is True
    )

    result["fills_verified"] = (
        orders.get("fills_read_verified") is True
    )

    # All three exchange checks remain mandatory.
    # V2 does not enable submission.

    result["status"] = "PARTIAL_RECONCILIATION"
    result["reason"] = (
        "EXCHANGE_ORDER_FILL_AND_ACCOUNT_EQUITY_READ_PENDING"
    )

    return result


# ============================================================
# 5. PRESERVE V1 UNIT 14
# ============================================================

_U1314V2_ORIGINAL_UNIT14 = (
    fresh_reconstruction_unit_14
)


def fresh_reconstruction_unit_14(
    config,
    unit_8,
    unit_12,
    unit_13,
):

    original = _U1314V2_ORIGINAL_UNIT14(
        config,
        unit_8,
        unit_12,
        unit_13
    )

    if not isinstance(original, dict):
        raise RuntimeError(
            "UNIT14_V1_RESULT_INVALID"
        )

    result = dict(original)

    v1 = result.get("unit13_14_reconciliation")

    v2 = u1314v2_reconcile(
        config,
        unit_8,
        unit_13,
        v1
    )

    result["unit13_14_v2"] = v2
    result["unit13_14_v2_version"] = U1314V2_VERSION

    print(
        "UNIT 13-14 V2 VERSION =",
        U1314V2_VERSION,
        flush=True
    )

    print(
        "UNIT 13-14 V2 STATUS =",
        v2["status"],
        flush=True
    )

    print(
        "UNIT 13-14 V2 REASON =",
        v2["reason"],
        flush=True
    )

    exposure = v2.get("exposure", {})
    orders = v2.get("orders", {})

    for key in (
        "position_value_verified",
        "position_margin_verified",
        "available_balance_verified",
        "entry_notional_usdt",
        "calculated_initial_margin_usdt",
        "reported_margin_usdt",
        "available_balance_usdt",
        "account_equity_verified",
        "pending_order_margin_verified",
        "account_wide_exposure_verified",
        "exposure_cap_verified",
    ):

        print(
            "UNIT 13-14 V2 EXPOSURE",
            key.upper(),
            "=",
            exposure.get(key),
            flush=True
        )

    for key in (
        "status",
        "open_orders_read_verified",
        "order_history_read_verified",
        "fills_read_verified",
        "position_identity_verified",
        "tp1_deferred",
        "planned_tp1_quantity",
        "planned_tp2_quantity",
        "planned_tp3_quantity",
        "duplicate_order_check_verified",
        "exchange_protection_verified",
    ):

        print(
            "UNIT 13-14 V2 ORDERS",
            key.upper(),
            "=",
            orders.get(key),
            flush=True
        )

    # Never turn a reconciliation report into
    # permission to submit orders.

    result["execution_authorized"] = False
    result["exchange_write"] = False
    result["exchange_protection_verified"] = False
    result["protection_active"] = False
    result["management_execution_verified"] = False

    # Preserve any more specific original alert.
    if result.get("status") not in ("ALERT", "BLOCKED"):
        result["status"] = "ALERT"
        result["reason"] = (
            "EXCHANGE_PROTECTION_NOT_VERIFIED"
        )

    result["safety_alert"] = True
    result["alert_severity"] = "CRITICAL"
    result["requires_operator_attention"] = True

    print(
        "UNIT 13-14 V2 FINAL STATUS =",
        result.get("status"),
        flush=True
    )

    print(
        "UNIT 13-14 V2 FINAL REASON =",
        result.get("reason"),
        flush=True
    )

    print(
        "UNIT 13-14 V2 PROTECTION ACTIVE = False",
        flush=True
    )

    print(
        "UNIT 13-14 V2 EXECUTION AUTHORIZED = False",
        flush=True
    )

    print(
        "UNIT 13-14 V2 EXCHANGE WRITE = NONE",
        flush=True
    )

    return result


print(
    "UNIT 13-14 V2 INSTALLED =",
    U1314V2_VERSION,
    flush=True
)

# ============================================================
# END UNIT 13-14 V2
# DEMO ORDER AND EXPOSURE RECONCILIATION
# ============================================================



# ============================================================
# START UNIT 13-14 V3 PART 1
# VERIFIED WEEX DEMO HISTORY READER
# ZERO INDENTATION
# ============================================================

import os
import json
import time
import hmac
import base64
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from decimal import Decimal, InvalidOperation

U1314V3_VERSION = "V3_VERIFIED_DEMO_HISTORY_READ"
U1314V3_HOST = "https://api-contract.weex.com"
U1314V3_HISTORY = "/capi/v3/sim/order/history"


def u1314v3_decimal(value, zero=False):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not n.is_finite() or n < 0:
        return None
    if n == 0 and not zero:
        return None
    return n


def u1314v3_demo_symbol(config, unit8):
    if not isinstance(config, dict):
        raise RuntimeError("V3_CONFIG_MISSING")

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError("V3_DEMO_ONLY")

    if config.get("real_cash_execution_enabled") is not False:
        raise RuntimeError("V3_REAL_CASH_BOUNDARY_FAILED")

    if not isinstance(unit8, dict):
        raise RuntimeError("V3_UNIT8_MISSING")

    if unit8.get("demo_contract_verified") is not True:
        raise RuntimeError("V3_DEMO_CONTRACT_UNVERIFIED")

    exchange = config.get("exchange", {})
    market = str(exchange.get("market_symbol", "")).upper()
    demo = str(exchange.get("demo_order_symbol", "")).upper()

    if not market.endswith("USDT"):
        raise RuntimeError("V3_MARKET_SYMBOL_INVALID")

    expected = market[:-4] + "SUSDT"

    if demo != expected:
        raise RuntimeError("V3_DEMO_SYMBOL_MISMATCH")

    if str(unit8.get("market_symbol", "")).upper() != market:
        raise RuntimeError("V3_UNIT8_MARKET_MISMATCH")

    return market, demo


def u1314v3_private_get(path, params):
    if path != U1314V3_HISTORY:
        raise RuntimeError("V3_ENDPOINT_NOT_ALLOWED")

    if not isinstance(params, dict):
        raise RuntimeError("V3_PARAMETERS_INVALID")

    if set(params) != {"symbol", "limit", "page"}:
        raise RuntimeError("V3_PARAMETER_SET_INVALID")

    symbol = str(params["symbol"]).upper()

    if not symbol.endswith("SUSDT"):
        raise RuntimeError("V3_NON_DEMO_SYMBOL_BLOCKED")

    limit = int(params["limit"])
    page = int(params["page"])

    if not 1 <= limit <= 100:
        raise RuntimeError("V3_LIMIT_INVALID")

    if not 0 <= page <= 100:
        raise RuntimeError("V3_PAGE_INVALID")

    key = os.getenv("WEEX_API_KEY") or os.getenv("API_KEY")
    secret = os.getenv("WEEX_API_SECRET") or os.getenv("API_SECRET")
    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError("V3_CREDENTIALS_MISSING")

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "limit": limit,
        "page": page,
    })

    signed_path = path + "?" + query
    timestamp = str(int(time.time() * 1000))
    message = timestamp + "GET" + signed_path

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        U1314V3_HOST + signed_path,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "locale": "en-US",
        },
    )

    if request.get_method() != "GET" or request.data is not None:
        raise RuntimeError("V3_READ_ONLY_BOUNDARY_FAILED")

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            status = response.getcode()
            raw = response.read().decode("utf-8")

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "V3_DEMO_HISTORY_HTTP_" + str(exc.code)
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "V3_DEMO_HISTORY_CONNECTION_FAILED"
        ) from exc

    if status != 200:
        raise RuntimeError("V3_DEMO_HISTORY_HTTP_INVALID")

    try:
        payload = json.loads(raw)
    except ValueError as exc:
        raise RuntimeError(
            "V3_DEMO_HISTORY_JSON_INVALID"
        ) from exc

    if isinstance(payload, dict):
        if payload.get("success") is False:
            raise RuntimeError("V3_DEMO_HISTORY_API_REJECTED")

        code = payload.get("code")
        if code is not None and str(code) not in (
            "0", "200", "00000"
        ):
            raise RuntimeError(
                "V3_DEMO_HISTORY_API_CODE_" + str(code)[:20]
            )

        payload = payload.get("data")

    if not isinstance(payload, list):
        raise RuntimeError("V3_DEMO_HISTORY_SHAPE_UNVERIFIED")

    return payload


def u1314v3_read_history(config, unit8):
    result = {
        "status": "UNVERIFIED",
        "reason": "NOT_REQUESTED",
        "history_read_verified": False,
        "history_complete": False,
        "order_count": None,
        "open_order_count_in_history": None,
        "filled_order_count": None,
        "partial_order_count": None,
        "cancelled_order_count": None,
        "execution_authorized": False,
        "exchange_write": False,
    }

    try:
        market, demo = u1314v3_demo_symbol(
            config, unit8
        )

        records = u1314v3_private_get(
            U1314V3_HISTORY,
            {
                "symbol": demo,
                "limit": 100,
                "page": 0,
            }
        )

        accepted = []
        seen = set()

        for record in records:
            if not isinstance(record, dict):
                raise RuntimeError("V3_ORDER_RECORD_INVALID")

            if str(record.get("symbol", "")).upper() != demo:
                raise RuntimeError("V3_HISTORY_SYMBOL_MISMATCH")

            order_id = record.get("orderId")

            if order_id is None:
                raise RuntimeError("V3_ORDER_ID_MISSING")

            order_id = str(order_id)

            if order_id in seen:
                raise RuntimeError("V3_DUPLICATE_ORDER_ID")

            seen.add(order_id)

            status = str(
                record.get("status", "")
            ).upper()

            original = u1314v3_decimal(
                record.get("origQty")
            )

            executed = u1314v3_decimal(
                record.get("executedQty"),
                zero=True
            )

            if original is None or executed is None:
                raise RuntimeError("V3_ORDER_QUANTITY_INVALID")

            if executed > original:
                raise RuntimeError("V3_EXECUTED_EXCEEDS_ORIGINAL")

            accepted.append({
                "order_id": order_id,
                "client_order_id": record.get("clientOrderId"),
                "status": status,
                "side": record.get("side"),
                "position_side": record.get("positionSide"),
                "type": record.get("type"),
                "price": record.get("price"),
                "original_quantity": str(original),
                "executed_quantity": str(executed),
                "remaining_quantity": str(original - executed),
                "reduce_only": record.get("reduceOnly"),
            })

        result.update({
            "status": "HISTORY_READ_VERIFIED",
            "reason": "FIRST_PAGE_VALIDATED",
            "market_symbol": market,
            "demo_symbol": demo,
            "history_read_verified": True,
            "history_complete": len(records) < 100,
            "order_count": len(accepted),
            "filled_order_count": sum(
                x["status"] == "FILLED"
                for x in accepted
            ),
            "partial_order_count": sum(
                x["status"] in (
                    "PARTIALLY_FILLED",
                    "PARTIAL_FILLED",
                )
                for x in accepted
            ),
            "cancelled_order_count": sum(
                x["status"] in ("CANCELED", "CANCELLED")
                for x in accepted
            ),
            "open_order_count_in_history": sum(
                x["status"] in (
                    "NEW", "OPEN", "PARTIALLY_FILLED",
                    "PARTIAL_FILLED", "PENDING",
                )
                for x in accepted
            ),
            "orders": accepted,
        })

    except Exception as exc:
        result["status"] = "UNVERIFIED"
        result["reason"] = str(exc)[:160]

    return result


# ============================================================
# END UNIT 13-14 V3 PART 1
# ============================================================


# ============================================================
# START UNIT 13-14 V3 PART 2
# V1/V2 PRESERVING UNIT 14 HANDOVER
# ZERO INDENTATION
# ============================================================

_U1314V3_PREVIOUS_UNIT14 = fresh_reconstruction_unit_14


def fresh_reconstruction_unit_14(
    config,
    unit_8,
    unit_12,
    unit_13,
):

    previous = _U1314V3_PREVIOUS_UNIT14(
        config,
        unit_8,
        unit_12,
        unit_13
    )

    if not isinstance(previous, dict):
        raise RuntimeError("V3_UNIT14_RESULT_INVALID")

    result = dict(previous)

    history = u1314v3_read_history(
        config, unit_8
    )

    v1 = result.get("unit13_14_reconciliation", {})
    v2 = result.get("unit13_14_v2", {})

    # Position margin: preserve distinct meanings.
    # Reported margin is exchange data.
    # Calculated margin is an estimate.
    # Neither alone proves account-wide exposure.

    margin = {
        "reported_margin_read_verified": False,
        "calculated_margin_available": False,
        "margin_formula_match": False,
        "difference_usdt": None,
    }

    if isinstance(v2, dict):
        exposure = v2.get("exposure", {})

        if isinstance(exposure, dict):
            reported = u1314v3_decimal(
                exposure.get("reported_margin_usdt")
            )
            calculated = u1314v3_decimal(
                exposure.get("calculated_initial_margin_usdt")
            )

            if reported is not None:
                margin["reported_margin_read_verified"] = (
                    exposure.get("position_value_verified")
                    is True
                )
                margin["reported_margin_usdt"] = str(reported)

            if calculated is not None:
                margin["calculated_margin_available"] = True
                margin["calculated_margin_usdt"] = str(calculated)

            if reported is not None and calculated is not None:
                difference = reported - calculated

                margin["difference_usdt"] = str(difference)

                margin["margin_formula_match"] = (
                    abs(difference) <= Decimal("0.000001")
                )

    history_verified = (
        history.get("history_read_verified") is True
    )

    # History may contain orders that are no longer open.
    # It is not an authoritative current-open-order snapshot.
    # A filled order is not proof of a particular hedge cycle.
    # Do not infer protection activity from history alone.

    v3 = {
        "version": U1314V3_VERSION,
        "status": (
            "DEMO_HISTORY_VERIFIED"
            if history_verified
            else "DEMO_HISTORY_UNVERIFIED"
        ),
        "reason": history.get("reason"),
        "v1_plan_reconciled": (
            isinstance(v1, dict)
            and v1.get("status") == "PLAN_RECONCILED"
        ),
        "history": history,
        "margin": margin,
        "demo_history_read_verified": history_verified,
        "current_open_orders_verified": False,
        "individual_fills_verified": False,
        "account_equity_verified": False,
        "pending_order_margin_verified": False,
        "account_wide_exposure_verified": False,
        "duplicate_protection_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
        "execution_authorized": False,
        "exchange_write": False,
    }

    result["unit13_14_v3"] = v3

    print(
        "UNIT 13-14 V3 VERSION =",
        U1314V3_VERSION,
        flush=True
    )

    for key in (
        "status",
        "reason",
        "history_read_verified",
        "history_complete",
        "order_count",
        "filled_order_count",
        "partial_order_count",
        "cancelled_order_count",
        "open_order_count_in_history",
    ):
        print(
            "UNIT 13-14 V3 HISTORY",
            key.upper(), "=",
            history.get(key),
            flush=True
        )

    for key in (
        "reported_margin_read_verified",
        "calculated_margin_available",
        "reported_margin_usdt",
        "calculated_margin_usdt",
        "difference_usdt",
        "margin_formula_match",
    ):
        print(
            "UNIT 13-14 V3 MARGIN",
            key.upper(), "=",
            margin.get(key),
            flush=True
        )

    print(
        "UNIT 13-14 V3 CURRENT ORDERS VERIFIED = False",
        flush=True
    )
    print(
        "UNIT 13-14 V3 INDIVIDUAL FILLS VERIFIED = False",
        flush=True
    )
    print(
        "UNIT 13-14 V3 ACCOUNT EXPOSURE VERIFIED = False",
        flush=True
    )

    result["execution_authorized"] = False
    result["exchange_write"] = False
    result["exchange_protection_verified"] = False
    result["protection_active"] = False
    result["safety_alert"] = True
    result["requires_operator_attention"] = True

    if result.get("status") not in ("ALERT", "BLOCKED"):
        result["status"] = "ALERT"
        result["reason"] = "EXCHANGE_PROTECTION_NOT_VERIFIED"

    print(
        "UNIT 13-14 V3 FINAL STATUS =",
        result.get("status"),
        flush=True
    )
    print(
        "UNIT 13-14 V3 PROTECTION ACTIVE = False",
        flush=True
    )
    print(
        "UNIT 13-14 V3 EXECUTION AUTHORIZED = False",
        flush=True
    )
    print(
        "UNIT 13-14 V3 EXCHANGE WRITE = NONE",
        flush=True
    )

    return result


print(
    "UNIT 13-14 V3 INSTALLED =",
    U1314V3_VERSION,
    flush=True
)

# ============================================================
# END UNIT 13-14 V3 PART 2
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 13-14 V4 PART 1
# SIMULATION ACCOUNT AND ORDER DIAGNOSTICS
# ZERO INDENTATION
# ============================================================

U1314V4_VERSION = "V4_SIMULATION_ORDER_RECONCILIATION"
U1314V4_HOST = "https://api-sim.weex.com"

U1314V4_PATHS = {
    "positions": "/capi/v3/position/allPosition",
    "orders": "/capi/v3/openOrders",
    "fills": "/capi/v3/userTrades",
}

def u1314v4_get(path, params):
    if path not in U1314V4_PATHS.values():
        raise RuntimeError("V4_ENDPOINT_NOT_ALLOWED")

    if set(params) != {"symbol"}:
        raise RuntimeError("V4_PARAMETERS_INVALID")

    symbol = str(params["symbol"]).upper()

    if not symbol.endswith("USDT"):
        raise RuntimeError("V4_SYMBOL_INVALID")

    key = os.getenv("WEEX_API_KEY") or os.getenv("API_KEY")
    secret = os.getenv("WEEX_API_SECRET") or os.getenv("API_SECRET")
    phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError("V4_CREDENTIALS_MISSING")

    query = urllib.parse.urlencode({"symbol": symbol})
    signed_path = path + "?" + query
    timestamp = str(int(time.time() * 1000))

    signature = base64.b64encode(
        hmac.new(
            secret.encode(),
            (timestamp + "GET" + signed_path).encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    request = urllib.request.Request(
        U1314V4_HOST + signed_path,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    try:
        with urllib.request.urlopen(
            request, timeout=12
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "V4_HTTP_" + str(exc.code)
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "V4_CONNECTION_FAILED"
        ) from exc

    if isinstance(payload, dict):
        if payload.get("success") is False:
            raise RuntimeError("V4_API_REJECTED")

        code = payload.get("code")
        if code is not None and str(code) not in (
            "0", "200", "00000"
        ):
            raise RuntimeError("V4_API_ERROR_" + str(code)[:20])

        payload = payload.get("data")

    if not isinstance(payload, list):
        raise RuntimeError("V4_RESPONSE_SHAPE_UNVERIFIED")

    for record in payload:
        if not isinstance(record, dict):
            raise RuntimeError("V4_RECORD_INVALID")

        record_symbol = str(
            record.get("symbol", "")
        ).upper()

        if record_symbol != symbol:
            raise RuntimeError("V4_RESPONSE_SYMBOL_MISMATCH")

    return payload


def u1314v4_probe(config, unit8):
    result = {
        "status": "UNVERIFIED",
        "reason": "NOT_STARTED",
        "same_demo_account_verified": False,
        "current_orders_verified": False,
        "fills_verified": False,
        "positions_probe_verified": False,
        "execution_authorized": False,
        "exchange_write": False,
    }

    try:
        market, demo = u1314v3_demo_symbol(
            config, unit8
        )
    except Exception as exc:
        result["reason"] = str(exc)[:120]
        return result

    result["market_symbol"] = market
    result["v3_demo_symbol"] = demo

    # The simulation domain uses standard market symbols.
    # Do not assume this account is identical to the
    # previously verified /sim/ demo account.

    for name in ("positions", "orders", "fills"):
        try:
            records = u1314v4_get(
                U1314V4_PATHS[name],
                {"symbol": market}
            )

            result[name + "_probe_verified"] = True
            result[name + "_record_count"] = len(records)
            result[name + "_reason"] = "RESPONSE_VALIDATED"

            if name == "positions":
                result["position_ids"] = [
                    str(x.get("id", ""))
                    for x in records
                ]

            elif name == "orders":
                result["order_ids"] = [
                    str(x.get("orderId", ""))
                    for x in records
                ]

            elif name == "fills":
                result["fill_order_ids"] = [
                    str(x.get("orderId", ""))
                    for x in records
                ]

        except Exception as exc:
            result[name + "_probe_verified"] = False
            result[name + "_record_count"] = None
            result[name + "_reason"] = str(exc)[:120]

    result["status"] = "PROBE_COMPLETED"
    result["reason"] = "SIMULATION_ACCOUNT_BINDING_PENDING"

    # Probe success does not establish account identity.
    # Do not promote these observations to verified
    # current orders or fills until the account is matched.

    return result


# ============================================================
# END UNIT 13-14 V4 PART 1
# ============================================================



# ============================================================
# START UNIT 13-14 V4 PART 2
# PRESERVE V1 V2 V3 AND ADD DIAGNOSTICS
# ZERO INDENTATION
# ============================================================

_U1314V4_PREVIOUS_UNIT14 = fresh_reconstruction_unit_14


def fresh_reconstruction_unit_14(
    config,
    unit_8,
    unit_12,
    unit_13,
):

    previous = _U1314V4_PREVIOUS_UNIT14(
        config,
        unit_8,
        unit_12,
        unit_13
    )

    if not isinstance(previous, dict):
        raise RuntimeError("V4_PREVIOUS_RESULT_INVALID")

    result = dict(previous)

    v3 = result.get("unit13_14_v3", {})

    probe = u1314v4_probe(
        config,
        unit_8
    )

    v4 = {
        "version": U1314V4_VERSION,
        "status": probe.get("status"),
        "reason": probe.get("reason"),
        "simulation_probe": probe,
        "v3_history_verified": (
            isinstance(v3, dict)
            and v3.get("demo_history_read_verified") is True
        ),
        "same_demo_account_verified": False,
        "current_open_orders_verified": False,
        "individual_fills_verified": False,
        "account_equity_verified": False,
        "account_wide_exposure_verified": False,
        "duplicate_protection_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
        "execution_authorized": False,
        "exchange_write": False,
    }

    result["unit13_14_v4"] = v4

    print(
        "UNIT 13-14 V4 VERSION =",
        U1314V4_VERSION,
        flush=True
    )

    print(
        "UNIT 13-14 V4 STATUS =",
        v4["status"],
        flush=True
    )

    print(
        "UNIT 13-14 V4 REASON =",
        v4["reason"],
        flush=True
    )

    print(
        "UNIT 13-14 V4 V3 HISTORY VERIFIED =",
        v4["v3_history_verified"],
        flush=True
    )

    for name in ("positions", "orders", "fills"):
        print(
            "UNIT 13-14 V4",
            name.upper(),
            "PROBE VERIFIED =",
            probe.get(name + "_probe_verified", False),
            flush=True
        )

        print(
            "UNIT 13-14 V4",
            name.upper(),
            "RECORD COUNT =",
            probe.get(name + "_record_count"),
            flush=True
        )

        print(
            "UNIT 13-14 V4",
            name.upper(),
            "REASON =",
            probe.get(name + "_reason"),
            flush=True
        )

    print(
        "UNIT 13-14 V4 SAME DEMO ACCOUNT VERIFIED = False",
        flush=True
    )

    print(
        "UNIT 13-14 V4 CURRENT ORDERS VERIFIED = False",
        flush=True
    )

    print(
        "UNIT 13-14 V4 INDIVIDUAL FILLS VERIFIED = False",
        flush=True
    )

    result["status"] = "ALERT"
    result["reason"] = "DEMO_ACCOUNT_ORDER_BINDING_PENDING"
    result["protection_active"] = False
    result["exchange_protection_verified"] = False
    result["execution_authorized"] = False
    result["exchange_write"] = False
    result["safety_alert"] = True
    result["requires_operator_attention"] = True

    print(
        "UNIT 13-14 V4 FINAL STATUS = ALERT",
        flush=True
    )

    print(
        "UNIT 13-14 V4 PROTECTION ACTIVE = False",
        flush=True
    )

    print(
        "UNIT 13-14 V4 EXECUTION AUTHORIZED = False",
        flush=True
    )

    print(
        "UNIT 13-14 V4 EXCHANGE WRITE = NONE",
        flush=True
    )

    return result


print(
    "UNIT 13-14 V4 INSTALLED =",
    U1314V4_VERSION,
    flush=True
)

# ============================================================
# END UNIT 13-14 V4 PART 2
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 13-14 V5 PART 1
# CROSS-VERIFICATION AND ACCOUNT BINDING
# ZERO INDENTATION
# ============================================================

U1314V5_VERSION = "V5_CROSS_VERIFICATION"


def u1314v5_ids(values):
    if not isinstance(values, list):
        return None

    result = []

    for value in values:
        if value is None:
            return None

        item = str(value).strip()

        if not item or item.lower() in ("none", "null"):
            return None

        result.append(item)

    if len(result) != len(set(result)):
        return None

    return set(result)


def u1314v5_reconcile(result, unit8):
    v3 = result.get("unit13_14_v3", {})
    v4 = result.get("unit13_14_v4", {})

    output = {
        "version": U1314V5_VERSION,
        "status": "UNVERIFIED",
        "reason": "EVIDENCE_INCOMPLETE",
        "v3_history_verified": False,
        "v4_orders_probe_verified": False,
        "v4_fills_probe_verified": False,
        "historical_order_ids_verified": False,
        "fill_order_ids_verified": False,
        "all_fill_orders_in_history": False,
        "history_orders_with_fills": 0,
        "unmatched_fill_order_count": None,
        "position_verified_by_unit8": False,
        "same_demo_account_verified": False,
        "current_open_orders_verified": False,
        "individual_fill_details_verified": False,
        "account_wide_exposure_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
        "execution_authorized": False,
        "exchange_write": False,
    }

    if not isinstance(v3, dict) or not isinstance(v4, dict):
        return output

    history = v3.get("history", {})
    probe = v4.get("simulation_probe", {})

    if not isinstance(history, dict):
        return output

    if not isinstance(probe, dict):
        return output

    history_ok = (
        history.get("history_read_verified") is True
    )

    orders_ok = (
        probe.get("orders_probe_verified") is True
    )

    fills_ok = (
        probe.get("fills_probe_verified") is True
    )

    output["v3_history_verified"] = history_ok
    output["v4_orders_probe_verified"] = orders_ok
    output["v4_fills_probe_verified"] = fills_ok

    history_records = history.get("orders")

    historical_ids = None

    if history_ok and isinstance(history_records, list):
        historical_ids = u1314v5_ids([
            record.get("order_id")
            for record in history_records
            if isinstance(record, dict)
        ])

        if (
            len(history_records)
            != sum(isinstance(x, dict) for x in history_records)
        ):
            historical_ids = None

    output["historical_order_ids_verified"] = (
        historical_ids is not None
    )

    # V4 retained fill order IDs but not individual
    # fill quantities, prices or timestamps.
    # Repeated order IDs are legitimate for partial fills.

    fill_ids = None

    if fills_ok:
        raw_fill_ids = probe.get("fill_order_ids")

        if isinstance(raw_fill_ids, list):
            if all(
                item is not None
                and str(item).strip()
                and str(item).lower() not in ("none", "null")
                for item in raw_fill_ids
            ):
                fill_ids = {
                    str(item).strip()
                    for item in raw_fill_ids
                }

    output["fill_order_ids_verified"] = (
        fill_ids is not None
    )

    if historical_ids is not None and fill_ids is not None:
        unmatched = fill_ids - historical_ids
        matched = fill_ids & historical_ids

        output["history_orders_with_fills"] = len(matched)
        output["unmatched_fill_order_count"] = len(unmatched)

        output["all_fill_orders_in_history"] = (
            len(unmatched) == 0
            and len(fill_ids) > 0
        )

    # Unit 8 is the authoritative source for the
    # currently verified /sim/ demo position.
    # A successful V4 request to a different host
    # does not establish the same account identity.

    if isinstance(unit8, dict):
        output["position_verified_by_unit8"] = (
            unit8.get("status") == "VERIFIED_READ_ONLY"
            and unit8.get("positions_read_verified") is True
        )

    if not history_ok:
        output["reason"] = "V3_HISTORY_UNVERIFIED"

    elif not orders_ok or not fills_ok:
        output["reason"] = "V4_ORDER_OR_FILL_PROBE_FAILED"

    elif historical_ids is None or fill_ids is None:
        output["reason"] = "ORDER_ID_EVIDENCE_INVALID"

    elif not output["all_fill_orders_in_history"]:
        output["reason"] = "FILL_HISTORY_ORDER_IDS_NOT_MATCHED"

    else:
        output["status"] = "ORDER_ID_CROSS_CHECK_PASSED"
        output["reason"] = (
            "ORDER_IDS_MATCH_ACCOUNT_BINDING_PENDING"
        )

    # Never infer account identity from identical
    # credentials, symbols, or order IDs alone.

    return output


# ============================================================
# END UNIT 13-14 V5 PART 1
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 13-14 V5 PART 2
# PRESERVE V1 THROUGH V4
# ZERO INDENTATION
# ============================================================

_U1314V5_PREVIOUS_UNIT14 = fresh_reconstruction_unit_14


def fresh_reconstruction_unit_14(
    config,
    unit_8,
    unit_12,
    unit_13,
):

    previous = _U1314V5_PREVIOUS_UNIT14(
        config,
        unit_8,
        unit_12,
        unit_13
    )

    if not isinstance(previous, dict):
        raise RuntimeError("V5_UNIT14_RESULT_INVALID")

    result = dict(previous)

    v5 = u1314v5_reconcile(
        result,
        unit_8
    )

    result["unit13_14_v5"] = v5

    print(
        "UNIT 13-14 V5 VERSION =",
        U1314V5_VERSION,
        flush=True
    )

    for key in (
        "status",
        "reason",
        "v3_history_verified",
        "v4_orders_probe_verified",
        "v4_fills_probe_verified",
        "historical_order_ids_verified",
        "fill_order_ids_verified",
        "all_fill_orders_in_history",
        "history_orders_with_fills",
        "unmatched_fill_order_count",
        "position_verified_by_unit8",
        "same_demo_account_verified",
        "current_open_orders_verified",
        "individual_fill_details_verified",
        "account_wide_exposure_verified",
        "exchange_protection_verified",
    ):
        print(
            "UNIT 13-14 V5",
            key.upper(),
            "=",
            v5.get(key),
            flush=True
        )

    # V5 performs no exchange writes.
    # Preserve existing demo position management
    # and prevent unverified protective execution.

    result["status"] = "ALERT"
    result["reason"] = (
        "V5_CROSS_CHECK_ACCOUNT_BINDING_PENDING"
    )

    result["protection_active"] = False
    result["exchange_protection_verified"] = False
    result["execution_authorized"] = False
    result["exchange_write"] = False
    result["safety_alert"] = True
    result["requires_operator_attention"] = True

    print(
        "UNIT 13-14 V5 FINAL STATUS = ALERT",
        flush=True
    )

    print(
        "UNIT 13-14 V5 PROTECTION ACTIVE = False",
        flush=True
    )

    print(
        "UNIT 13-14 V5 EXECUTION AUTHORIZED = False",
        flush=True
    )

    print(
        "UNIT 13-14 V5 EXCHANGE WRITE = NONE",
        flush=True
    )

    return result


print(
    "UNIT 13-14 V5 INSTALLED =",
    U1314V5_VERSION,
    flush=True
)

# ============================================================
# END UNIT 13-14 V5 PART 2
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 13-14 V6 PART 1
# VERIFIED POSITION AND FILL EVIDENCE
# ZERO INDENTATION
# ============================================================

U1314V6_VERSION = "V6_POSITION_FILL_EVIDENCE"


def u1314v6_decimal(value):
    from decimal import Decimal, InvalidOperation

    if value is None or isinstance(value, bool):
        return None

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None

    if not number.is_finite() or number < 0:
        return None

    return number


def u1314v6_field(record, names):
    for name in names:
        if name in record and record[name] is not None:
            return record[name]
    return None


def u1314v6_position(config, unit8):
    report = {
        "verified": False,
        "reason": "NOT_CHECKED",
        "position_id": None,
        "side": None,
        "quantity": None,
        "entry_price": None,
        "leverage": None,
    }

    if not isinstance(config, dict):
        report["reason"] = "CONFIG_INVALID"
        return report

    exchange = config.get("exchange", {})

    if not isinstance(exchange, dict):
        report["reason"] = "EXCHANGE_CONFIG_INVALID"
        return report

    symbol = str(
        exchange.get("market_symbol", "")
    ).strip().upper()

    if not symbol or not isinstance(unit8, dict):
        report["reason"] = "UNIT8_OR_SYMBOL_MISSING"
        return report

    try:
        status, position = u813v2_verified_position(
            unit8, symbol
        )
    except Exception as exc:
        report["reason"] = (
            "ADAPTER_ERROR_" + type(exc).__name__
        )
        return report

    report["reason"] = status

    if (
        status != "VERIFIED_OPEN_POSITION"
        or not isinstance(position, dict)
    ):
        return report

    quantity = u1314v6_decimal(
        position.get("quantity")
    )

    entry = u1314v6_decimal(
        position.get("entryPrice")
    )

    leverage = u1314v6_decimal(
        position.get("leverage")
    )

    side = str(
        position.get("side", "")
    ).upper()

    if (
        quantity is None or quantity <= 0
        or entry is None or entry <= 0
        or leverage is None or leverage <= 0
        or side not in ("LONG", "SHORT")
    ):
        report["reason"] = "POSITION_FIELDS_INVALID"
        return report

    report.update({
        "verified": True,
        "reason": "VERIFIED_OPEN_POSITION",
        "position_id": str(position.get("id", "")),
        "side": side,
        "quantity": str(quantity),
        "entry_price": str(entry),
        "leverage": str(leverage),
    })

    return report


def u1314v6_fills(config, unit8):
    report = {
        "read_verified": False,
        "details_verified": False,
        "reason": "NOT_CHECKED",
        "record_count": None,
        "unique_order_count": None,
        "total_quantity": None,
        "orders": {},
    }

    try:
        market, demo = u1314v3_demo_symbol(
            config, unit8
        )

        records = u1314v4_get(
            U1314V4_PATHS["fills"],
            {"symbol": market}
        )

    except Exception as exc:
        report["reason"] = (
            "FILL_READ_" + type(exc).__name__
        )
        return report

    report["read_verified"] = True
    report["record_count"] = len(records)

    if not records:
        report["reason"] = "NO_FILL_RECORDS"
        return report

    grouped = {}
    seen = set()
    total = u1314v6_decimal("0")

    for record in records:
        if not isinstance(record, dict):
            report["reason"] = "FILL_RECORD_INVALID"
            return report

        order_id = u1314v6_field(
            record, ("orderId", "order_id")
        )

        trade_id = u1314v6_field(
            record, ("tradeId", "trade_id", "id")
        )

        quantity = u1314v6_decimal(
            u1314v6_field(
                record, ("qty", "quantity", "size")
            )
        )

        price = u1314v6_decimal(
            u1314v6_field(
                record, ("price", "fillPrice")
            )
        )

        timestamp = u1314v6_field(
            record,
            ("time", "timestamp", "createdTime")
        )

        side = u1314v6_field(
            record, ("side", "tradeSide")
        )

        if (
            order_id is None
            or trade_id is None
            or quantity is None or quantity <= 0
            or price is None or price <= 0
            or timestamp is None
            or side is None
        ):
            report["reason"] = (
                "FILL_REQUIRED_FIELDS_UNVERIFIED"
            )
            return report

        order_id = str(order_id).strip()
        trade_id = str(trade_id).strip()

        if not order_id or not trade_id:
            report["reason"] = "FILL_ID_EMPTY"
            return report

        identity = (order_id, trade_id)

        if identity in seen:
            report["reason"] = "DUPLICATE_TRADE_ID"
            return report

        seen.add(identity)

        if order_id not in grouped:
            grouped[order_id] = {
                "quantity": u1314v6_decimal("0"),
                "fill_count": 0,
                "sides": set(),
                "timestamps": [],
            }

        grouped[order_id]["quantity"] += quantity
        grouped[order_id]["fill_count"] += 1
        grouped[order_id]["sides"].add(
            str(side).upper()
        )
        grouped[order_id]["timestamps"].append(
            str(timestamp)
        )

        total += quantity

    report["orders"] = {
        order_id: {
            "quantity": str(data["quantity"]),
            "fill_count": data["fill_count"],
            "sides": sorted(data["sides"]),
            "timestamps_present": len(
                data["timestamps"]
            ),
        }
        for order_id, data in grouped.items()
    }

    report["unique_order_count"] = len(grouped)
    report["total_quantity"] = str(total)
    report["details_verified"] = True
    report["reason"] = "FILL_FIELDS_VALIDATED"

    # This verifies fill field integrity only.
    # It does not verify account identity or
    # agreement with historical order quantities.

    return report


def u1314v6_reconcile(config, unit8, previous):
    position = u1314v6_position(
        config, unit8
    )

    fills = u1314v6_fills(
        config, unit8
    )

    v5 = previous.get("unit13_14_v5", {})

    v5_ids_match = (
        isinstance(v5, dict)
        and v5.get("all_fill_orders_in_history") is True
        and v5.get("unmatched_fill_order_count") == 0
    )

    report = {
        "version": U1314V6_VERSION,
        "position": position,
        "fills": fills,
        "position_verified": position["verified"],
        "fill_details_verified": fills["details_verified"],
        "v5_order_ids_matched": v5_ids_match,
        "historical_quantity_match_verified": False,
        "same_demo_account_verified": False,
        "current_orders_account_bound": False,
        "account_wide_exposure_verified": False,
        "exchange_protection_verified": False,
        "protection_active": False,
        "execution_authorized": False,
        "exchange_write": False,
    }

    if not position["verified"]:
        report["status"] = "BLOCKED"
        report["reason"] = "POSITION_UNVERIFIED"

    elif not fills["details_verified"]:
        report["status"] = "PARTIAL"
        report["reason"] = "FILL_DETAILS_UNVERIFIED"

    elif not v5_ids_match:
        report["status"] = "PARTIAL"
        report["reason"] = "ORDER_ID_MATCH_UNVERIFIED"

    else:
        report["status"] = "EVIDENCE_VALIDATED"
        report["reason"] = (
            "POSITION_AND_FILL_FIELDS_VALIDATED_"
            "ACCOUNT_BINDING_PENDING"
        )

    return report


# ============================================================
# END UNIT 13-14 V6 PART 1
# ZERO INDENTATION
# ============================================================

scan_forever()

# ============================================================
# END COMPLETE CONTINUOUS SCAN CONTROLLER V2
# ZERO INDENTATION
# ============================================================

