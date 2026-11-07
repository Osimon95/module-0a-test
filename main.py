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
# START COMPLETE UNIT 2
# COMBINED 17248 + 18426 MODEL
# UNIVERSAL WEEX DEMO CONFIGURATION
# ZERO INDENTATION
# ============================================================

import os
import re
from decimal import Decimal, InvalidOperation


# ============================================================
# 2.1 ENVIRONMENT HELPERS
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


def unit_2_env_number(
    names,
    default,
    minimum=0,
    maximum=None
):

    if isinstance(names, str):
        names = (names,)

    selected = "DEFAULT"
    raw = str(default)

    for name in names:
        candidate = os.getenv(name)

        if candidate is not None and candidate.strip():
            raw = candidate.strip()
            selected = name
            break

    number = unit_2_v9_number(
        raw,
        selected,
        allow_zero=(minimum == 0)
    )

    if number < Decimal(str(minimum)):
        raise RuntimeError(
            "UNIT 2 BELOW MINIMUM: " + selected
        )

    if (
        maximum is not None
        and number > Decimal(str(maximum))
    ):
        raise RuntimeError(
            "UNIT 2 ABOVE MAXIMUM: " + selected
        )

    return float(number), selected


def unit_2_env_bool(name, default=False):

    raw = os.getenv(
        name,
        "true" if default else "false"
    ).strip().lower()

    if raw in ("1", "true", "yes", "on"):
        return True

    if raw in ("0", "false", "no", "off"):
        return False

    raise RuntimeError(
        "UNIT 2 INVALID BOOLEAN " + name
    )


def unit_2_universal_symbol():

    symbol = os.getenv(
        "WEEX_SYMBOL",
        os.getenv("MARKET_SYMBOL", "BTCUSDT")
    ).strip().upper()

    symbol = symbol.replace("/", "").replace("-", "")

    if not re.fullmatch(
        r"[A-Z0-9]{2,20}USDT",
        symbol
    ):
        raise RuntimeError(
            "UNIT 2 INVALID MARKET SYMBOL: " + symbol
        )

    return symbol, symbol[:-4], "USDT"


# ============================================================
# 2.2 CENTRAL CONFIGURATION
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)

    log(
        "COMBINED RECONSTRUCTION UNIT 2 START"
    )

    if globals().get(
        "FRESH_RECONSTRUCTION_UNIT_1_READY"
    ) is not True:
        raise RuntimeError(
            "UNIT 2 REQUIRES UNIT 1"
        )

    market_symbol, base_coin, quote_coin = (
        unit_2_universal_symbol()
    )

    # --------------------------------------------------------
    # SINGLE BOT MODE
    # PAUSE DISABLES NEW ENTRIES ONLY
    # --------------------------------------------------------

    bot_mode = os.getenv(
        "BOT_MODE", "PAUSE"
    ).strip().upper()

    if bot_mode not in ("RUN", "PAUSE"):
        raise RuntimeError(
            "UNIT 2 INVALID BOT_MODE"
        )

    # --------------------------------------------------------
    # USDT ENTRY CAPITAL
    # --------------------------------------------------------

    entry_margin, entry_source = unit_2_env_number(
        (
            "INITIAL_ENTRY_MARGIN_USDT",
            "ENTRY_MARGIN_USDT",
            "ENTRY_FIXED_USDT",
        ),
        0.5,
        minimum=0.00000001
    )

    # --------------------------------------------------------
    # LEVERAGE
    # MANUALLY SET ON WEEX AND MIRRORED ON RENDER
    # --------------------------------------------------------

    long_leverage, long_source = unit_2_env_number(
        (
            "WEEX_LEVERAGE_LONG",
            "WEEX_DEMO_LONG_LEVERAGE",
        ),
        10,
        minimum=0.00000001
    )

    short_leverage, short_source = unit_2_env_number(
        (
            "WEEX_LEVERAGE_SHORT",
            "WEEX_DEMO_SHORT_LEVERAGE",
        ),
        10,
        minimum=0.00000001
    )

    # --------------------------------------------------------
    # EXPOSURE AND BACKUPS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PROFIT TARGETS
    # --------------------------------------------------------

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
        raise RuntimeError(
            "UNIT 2 TP2 MUST EXCEED TP1"
        )

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
        raise RuntimeError(
            "UNIT 2 INVALID TP ALLOCATION"
        )

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
        trailing_min
        <= trailing_reference
        <= trailing_max
    ):
        raise RuntimeError(
            "UNIT 2 INVALID TRAILING RANGE"
        )

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

    # --------------------------------------------------------
    # DEMO SYMBOL IS ONLY A CANDIDATE
    # UNIT 8 MUST VERIFY THE ACTUAL CONTRACT
    # --------------------------------------------------------

    demo_candidate = base_coin + "SUSDT"

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",

        "market_symbol": market_symbol,
        "base_coin": base_coin,
        "quote_coin": quote_coin,

        "demo_order_symbol": demo_candidate,
        "demo_symbol_candidate": demo_candidate,
        "demo_symbol_verified": False,

        "contract_precision_verified": False,
        "contract_value_verified": False,

        "margin_currency": "USDT",
        "settlement_currency": "USDT",
        "pnl_currency": "USDT",
    }

    # --------------------------------------------------------
    # UNIT 2 LOCAL SAFETY
    # LATER DEMO EXECUTION USES INDEPENDENT VERIFICATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # STRATEGY AND POSITION PROTECTION
    # --------------------------------------------------------

    strategy = {
        "initial_fixed_usdt": entry_margin,
        "initial_entry_margin_usdt": entry_margin,
        "entry_margin_usdt": entry_margin,
        "entry_margin_source": entry_source,
        "initial_margin_percent": 5.0,

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
            "PERCENT_OF_AVAILABLE_TRADING_BALANCE",

        "backup_trigger_reference":
            "LATEST_VERIFIED_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PREVIOUS_BACKUP_FILL",

        "backup_long_liquidation_factor":
            1.0 - backup_buffer / 100.0,

        "backup_short_liquidation_factor":
            1.0 + backup_buffer / 100.0,

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
        "estimated_funding_rate": funding_rate,

        "tp1_net_roi_percent": tp1_roi,
        "tp2_net_roi_percent": tp2_roi,

        "tp1_net_roi_floor_percent": tp1_roi,
        "tp2_net_roi_floor_percent": tp2_roi,

        "tp1_allocation_percent": tp1_allocation,
        "tp2_allocation_percent": tp2_allocation,
        "tp3_allocation_percent": tp3_allocation,

        "tp_allocation": (
            tp1_allocation,
            tp2_allocation,
            tp3_allocation,
        ),

        "tp3_mode": "DYNAMIC_TRAILING",

        "tp3_trailing_reference_percent":
            trailing_reference,

        "tp3_trailing_min_percent":
            trailing_min,

        "tp3_trailing_max_percent":
            trailing_max,

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

            "liquidation_buffer_percent":
                backup_buffer,

            "require_available_funds": True,
            "require_exposure_cap": True,

            "require_verified_liquidation_price":
                True,
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

    # --------------------------------------------------------
    # VERIFIED PRECISION IS PROVIDED BY UNIT 8
    # NEVER HARDCODE BTC PRECISION FOR OTHER COINS
    # --------------------------------------------------------

    market_precision = {
        "quantity_step": None,
        "minimum_quantity": None,
        "price_step": None,

        "contract_value": None,
        "contract_multiplier": None,

        "verified": False,
        "source":
            "PENDING_DEMO_CONTRACT_VERIFICATION",

        "symbol": market_symbol,
        "demo_order_symbol": demo_candidate,
    }

    # --------------------------------------------------------
    # QUALIFICATION
    # PRESERVE UNIT 4-6 INTERFACES
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CENTRAL CONFIGURATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FINAL CONFIGURATION VALIDATION
    # --------------------------------------------------------

    if (
        exchange["name"] != "WEEX"
        or exchange["api_version"] != "V3"
        or config["execution_environment"] != "DEMO"
    ):
        raise RuntimeError(
            "UNIT 2 EXCHANGE CONFIG INVALID"
        )

    if not market_symbol.endswith("USDT"):
        raise RuntimeError(
            "UNIT 2 QUOTE CURRENCY INVALID"
        )

    if entry_margin <= 0:
        raise RuntimeError(
            "UNIT 2 ENTRY MARGIN INVALID"
        )

    if not (0 <= exposure_cap <= 100):
        raise RuntimeError(
            "UNIT 2 EXPOSURE CAP INVALID"
        )

    if abs(
        tp1_allocation
        + tp2_allocation
        + tp3_allocation
        - 100.0
    ) > 0.000001:
        raise RuntimeError(
            "UNIT 2 TP ALLOCATION INVALID"
        )

    # --------------------------------------------------------
    # RENDER STARTUP REPORT
    # --------------------------------------------------------

    print(
        "UNIT 2 MARKET SYMBOL =",
        market_symbol,
        flush=True
    )

    print(
        "UNIT 2 DEMO SYMBOL CANDIDATE =",
        demo_candidate,
        flush=True
    )

    print(
        "UNIT 2 DEMO CONTRACT VERIFIED = False",
        flush=True
    )

    print(
        "UNIT 2 BOT_MODE =",
        bot_mode,
        flush=True
    )

    print(
        "UNIT 2 EXISTING POSITION MANAGEMENT = "
        "INDEPENDENT OF BOT_MODE",
        flush=True
    )

    print(
        "UNIT 2 ENTRY MARGIN USDT =",
        entry_margin,
        flush=True
    )

    print(
        "UNIT 2 LONG LEVERAGE =",
        long_leverage,
        flush=True
    )

    print(
        "UNIT 2 SHORT LEVERAGE =",
        short_leverage,
        flush=True
    )

    print(
        "UNIT 2 EXPOSURE CAP % =",
        exposure_cap,
        flush=True
    )

    print(
        "UNIT 2 BACKUP COUNT = 5",
        flush=True
    )

    print(
        "UNIT 2 BACKUP MARGIN % =",
        backup_margin,
        flush=True
    )

    print(
        "UNIT 2 BACKUP BUFFER % =",
        backup_buffer,
        flush=True
    )

    print(
        "UNIT 2 TP1 NET ROI % =",
        tp1_roi,
        flush=True
    )

    print(
        "UNIT 2 TP2 NET ROI % =",
        tp2_roi,
        flush=True
    )

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
        "UNIT 2 CONTRACT PRECISION = "
        "PENDING UNIT 8 VERIFICATION",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "UNIT 2 REAL CASH EXECUTION = DISABLED",
        flush=True
    )

    log(
        "COMBINED RECONSTRUCTION UNIT 2 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return config


# ============================================================
# 2.3 EXECUTION AND GLOBAL HANDOVER
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)

FRESH_UNIT_2_OPTIMIZATION_READY = True

print(
    "UNIT 2 HANDOVER READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)


# ============================================================
# END COMPLETE UNIT 2
# UNIT 3 TO FOLLOW
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
