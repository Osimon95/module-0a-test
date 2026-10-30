
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
# START COMPLETE UNIT 2 V9
# WEEX DEMO CENTRAL CONFIGURATION + QUALIFICATION
# E0 INITIAL ENTRY / B1-B5 DYNAMIC BACKUPS
# NO BACKUP MULTIPLIERS
# ============================================================

import os
import math
from decimal import Decimal, InvalidOperation


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
        raise RuntimeError("UNIT 2 NONFINITE " + name)

    if number < 0 or (number == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 2 INVALID RANGE " + name
        )

    return number


def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 2 V9 START",
        flush=True
    )

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # ========================================================
    # CONFIGURABLE INPUTS
    # ========================================================
    # Set these directly or through Render environment values.
    # E0 is an amount, not a separate multiplier system.
    # Unit 2 never accesses private WEEX endpoints.
    # ========================================================

    def setting(name, default):
        return unit_2_v9_number(
            os.getenv(name, str(default)),
            name
        )

    e0_margin = setting(
        "INITIAL_ENTRY_MARGIN_USDT", "0.5"
    )

    backup_percent = setting(
        "BACKUP_MARGIN_PERCENT", "0.5"
    )

    buffer_percent = setting(
        "BACKUP_BUFFER_PERCENT", "0.3"
    )

    cap_percent = setting(
        "EXPOSURE_CAP_PERCENT", "35.0"
    )

    if backup_percent > 100:
        raise RuntimeError(
            "UNIT 2 BACKUP PERCENT EXCEEDS 100"
        )

    if buffer_percent >= 100:
        raise RuntimeError(
            "UNIT 2 INVALID LIQUIDATION BUFFER"
        )

    if cap_percent > 100:
        raise RuntimeError(
            "UNIT 2 EXPOSURE CAP EXCEEDS 100"
        )

    # ========================================================
    # EXCHANGE SETTINGS
    # ========================================================

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
    }

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
    }

    # These are local Unit 2 capabilities.
    # They must not disable subsequent authorized
    # DEMO execution in Unit 12.

    # ========================================================
    # CENTRAL STRATEGY CONFIGURATION
    # ========================================================

    strategy = {
        "initial_fixed_usdt": float(e0_margin),
        "initial_margin_percent": 5.0,

        "backup_margin_percent":
            float(backup_percent),
        "backup_buffer_percent":
            float(buffer_percent),
        "max_backups": 5,

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_trigger_reference":
            "FRESH_WEEX_LIQUIDATION_PRICE",

        "backup_trigger_recalculation":
            "AFTER_PRECEDING_CONFIRMED_FILL",

        "backup_long_liquidation_factor":
            float(
                Decimal("1")
                + buffer_percent / Decimal("100")
            ),

        "backup_short_liquidation_factor":
            float(
                Decimal("1")
                - buffer_percent / Decimal("100")
            ),

        "exposure_cap_percent":
            float(cap_percent),
        "exposure_cap_max_percent": 100.0,

        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        "tp1_allocation_percent": 10.0,
        "tp2_allocation_percent": 20.0,
        "tp3_allocation_percent": 70.0,

        "tp1_net_roi_floor_percent": 5.0,
        "tp2_net_roi_floor_percent": 10.0,
        "tp1_tp2_min_roi_separation_percent": 5.0,

        "tp3_trailing_reference_percent": 0.20,
        "tp3_trailing_min_percent": 0.10,
        "tp3_trailing_max_percent": 0.40,

        "signal_expiry_seconds": 120,
        "loss_cooldown_seconds": 300,

        "one_direction_only": True,
        "anti_duplicate_orders": True,
        "active_trade_mode_lock": True,
        "exclusive_mode": True,
        "mode_confirmations_required": 3,
    }

    # No backup_multipliers key.
    # No hardcoded leverage_target key.

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # ========================================================
    # PRESERVE UNIT 2 HYBRID QUALIFICATION CONTRACT
    # ========================================================

    qualification = {
        "common": {
            "mode_priority": (
                "BREAKOUT", "STRUCTURE", "SCALP"
            ),
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
            "estimated_taker_fee_percent": 0.08,
            "estimated_slippage_percent": 0.0,
            "include_entry_fee": True,
            "include_exit_fee": True,
            "minimum_fee_coverage_multiplier": 2.0,
            "require_positive_estimated_net": True,
            "minimum_net_roi_percent": 2.0,
        },
    }

    config = {
        "exchange": exchange,
        "execution_environment": "DEMO",
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
        "qualification": qualification,
    }

    # ========================================================
    # CONTRACT VALIDATION
    # ========================================================

    def require(condition, message):
        if not condition:
            raise RuntimeError(
                "UNIT 2 CONFIG INVALID: " + message
            )

    require(
        exchange["name"] == "WEEX",
        "EXCHANGE"
    )

    require(
        exchange["api_version"] == "V3",
        "API VERSION"
    )

    require(
        config["execution_environment"] == "DEMO",
        "DEMO ENVIRONMENT"
    )

    require(
        e0_margin > 0,
        "E0 MARGIN"
    )

    require(
        backup_percent > 0
        and backup_percent <= 100,
        "BACKUP BALANCE PERCENT"
    )

    require(
        buffer_percent > 0
        and buffer_percent < 100,
        "LIQUIDATION BUFFER"
    )

    require(
        strategy["max_backups"] == 5,
        "BACKUP COUNT"
    )

    require(
        Decimal("0") < cap_percent <= Decimal("100"),
        "EXPOSURE CAP"
    )

    require(
        "backup_multipliers" not in strategy,
        "OBSOLETE BACKUP MULTIPLIERS"
    )

    require(
        "leverage_target" not in strategy,
        "HARDCODED LEVERAGE"
    )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
        "progressive_backup_funding",
        "exposure_includes_initial",
        "exposure_includes_filled_backups",
        "exposure_includes_pending_margin",
    ):
        require(
            strategy.get(key) is True,
            key
        )

    require(
        strategy[
            "full_ladder_reservation_required"
        ] is False,
        "FULL LADDER RESERVATION"
    )

    for key in (
        "real_order_submission_enabled",
        "demo_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        require(
            safety[key] is False,
            "UNIT 2 WRITE SAFETY " + key
        )

    require(
        sum(
            strategy[key] for key in (
                "tp1_allocation_percent",
                "tp2_allocation_percent",
                "tp3_allocation_percent",
            )
        ) == 100.0,
        "TAKE PROFIT ALLOCATION"
    )

    require(
        strategy["tp1_net_roi_floor_percent"] >= 5.0,
        "TP1 ROI FLOOR"
    )

    require(
        strategy["tp2_net_roi_floor_percent"] >= 10.0,
        "TP2 ROI FLOOR"
    )

    require(
        0 < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"],
        "TP3 TRAILING RANGE"
    )

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
    ):
        require(
            market_precision[key] > 0,
            "MARKET PRECISION " + key
        )

    require(
        qualification["common"]["mode_priority"]
        == ("BREAKOUT", "STRUCTURE", "SCALP"),
        "STRATEGY PRIORITY"
    )

    require(
        qualification["scalp"]["quality_threshold"]
        == 70.0,
        "SCALP QUALITY"
    )

    # ========================================================
    # STARTUP REPORT
    # ========================================================

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True
    )
    print("PASS: EXCHANGE = WEEX", flush=True)
    print("PASS: API VERSION = V3", flush=True)
    print(
        "PASS: DEMO ORDER SYMBOL = BTCSUSDT",
        flush=True
    )
    print(
        "PASS: EXECUTION ENVIRONMENT = DEMO",
        flush=True
    )
    print(
        "PASS: LEVERAGE CONTROL = WEEX ONLY",
        flush=True
    )
    print(
        "PASS: INITIAL ENTRY DEFAULT USDT =",
        strategy["initial_fixed_usdt"],
        flush=True
    )
    print(
        "PASS: BACKUP MARGIN % AVAILABLE =",
        strategy["backup_margin_percent"],
        flush=True
    )
    print(
        "PASS: BACKUP BUFFER % =",
        strategy["backup_buffer_percent"],
        flush=True
    )
    print(
        "PASS: MAX BACKUPS =",
        strategy["max_backups"],
        flush=True
    )
    print(
        "PASS: BACKUP MULTIPLIERS = NONE",
        flush=True
    )
    print(
        "PASS: BACKUP FUNDING = PROGRESSIVE",
        flush=True
    )
    print(
        "PASS: EXPOSURE CAP DEFAULT/CURRENT % =",
        strategy["exposure_cap_percent"],
        flush=True
    )
    print(
        "PASS: EXPOSURE CAP MAX % =",
        strategy["exposure_cap_max_percent"],
        flush=True
    )
    print(
        "PASS: LONG BACKUP FACTOR =",
        strategy["backup_long_liquidation_factor"],
        flush=True
    )
    print(
        "PASS: SHORT BACKUP FACTOR =",
        strategy["backup_short_liquidation_factor"],
        flush=True
    )
    print(
        "PASS: QUALIFICATION MODE PRIORITY =",
        qualification["common"]["mode_priority"],
        flush=True
    )
    print(
        "PASS: SCALP QUALITY TARGET =",
        qualification["scalp"]["quality_threshold"],
        flush=True
    )
    print(
        "PASS: TP ALLOCATION = 10 / 20 / 70",
        flush=True
    )
    print(
        "PASS: MARKET QUANTITY STEP =",
        market_precision["quantity_step"],
        flush=True
    )
    print(
        "PASS: ANTI DUPLICATE = TRUE",
        flush=True
    )
    print(
        "PASS: NO EXCHANGE MUTATION IN UNIT 2",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 2 RESULT = PASS",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 2 ADAPTER RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return config


# ============================================================
# UNIT 2 V9 EXECUTION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)

# ============================================================
# END COMPLETE UNIT 2 V9
# UNIT 3 FOLLOWS
# ============================================================
# ============================================================
# UNIT 2 V9 -> UNIT 3 COMPATIBILITY
# RESTORE ORIGINAL OPTIMIZATION READINESS CONTRACT
# ============================================================

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
        "UNIT 2 V9 OPTIMIZATION READINESS FAILED"
    )

print(
    "UNIT 2 V9 OPTIMIZATION READY =",
    FRESH_UNIT_2_OPTIMIZATION_READY,
    flush=True
)

    

# ============================================================
# START COMPLETE UNIT 3 REPLACEMENT V2
# WEEX V3 MARK PRICE DATA + FRESHNESS VALIDATION
# COMPATIBLE WITH UNITS 2 AND 4-15
# ZERO INDENTATION
# NO AUTHENTICATED EXCHANGE WRITE
# ============================================================

import math
import time


# ============================================================
# UNIT 3 DATA VALIDATION
# PURE FUNCTION - NO HTTP REQUEST
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
# UNIT 3 DETERMINISTIC VALIDATION TESTS
# PURE SYNTHETIC DATA - NO EXCHANGE REQUESTS
# ============================================================

def unit_3_validation_tests_v2():

    print("=" * 80, flush=True)
    print(
        "UNIT 3 OPTIMIZATION VALIDATION V2 START",
        flush=True
    )

    now_ms = 1800000000000

    valid_payload = {
        "symbol": "BTCUSDT",
        "price": "80000.5",
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

    def rejected(payload, reason):

        try:
            unit_3_validate_mark_payload(
                payload,
                "BTCUSDT",
                now_ms
            )
        except RuntimeError as exc:
            return str(exc) == reason

        return False

    result = unit_3_validate_mark_payload(
        valid_payload,
        "BTCUSDT",
        now_ms
    )

    check(
        "VALID MARK PRICE",
        result["price"] == 80000.5
    )

    check(
        "VALID EXCHANGE TIMESTAMP",
        result["exchange_time_ms"]
        == now_ms - 1000
    )

    check(
        "VALID DATA AGE",
        result["market_age_ms"] == 1000
    )

    check(
        "REJECT WRONG SYMBOL",
        rejected(
            {
                **valid_payload,
                "symbol": "ETHUSDT"
            },
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )
    )

    check(
        "REJECT ZERO PRICE",
        rejected(
            {
                **valid_payload,
                "price": "0"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NEGATIVE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "-1"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT NONNUMERIC PRICE",
        rejected(
            {
                **valid_payload,
                "price": "invalid"
            },
            "UNIT 3 INVALID MARKET PRICE"
        )
    )

    check(
        "REJECT NONFINITE PRICE",
        rejected(
            {
                **valid_payload,
                "price": "nan"
            },
            "UNIT 3 NON-FINITE OR NON-POSITIVE PRICE"
        )
    )

    check(
        "REJECT STALE DATA",
        rejected(
            {
                **valid_payload,
                "time": now_ms - 130000
            },
            "UNIT 3 STALE MARKET DATA"
        )
    )

    check(
        "REJECT FUTURE TIMESTAMP",
        rejected(
            {
                **valid_payload,
                "time": now_ms + 20000
            },
            "UNIT 3 MARKET TIMESTAMP TOO FAR IN FUTURE"
        )
    )

    check(
        "REJECT MISSING TIMESTAMP",
        rejected(
            {
                "symbol": "BTCUSDT",
                "price": "80000.5"
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
        "UNIT 3 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 3 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 3 OPTIMIZATION VALIDATION FAILED"
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
# UNIT 3 ACTUAL WEEX PUBLIC MARKET DATA READ
# ============================================================

def fresh_reconstruction_unit_3():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 3 START")

    if FRESH_UNIT_2_OPTIMIZATION_READY is not True:
        raise RuntimeError(
            "UNIT 3 BLOCKED: UNIT 2 VALIDATION NOT READY"
        )

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 INVALID UNIT 2 CONFIGURATION"
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

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 INVALID API VERSION"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID CONTRACT BASE URL"
        )

    market_symbol = exchange.get("market_symbol")

    if market_symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 INVALID MARKET SYMBOL"
        )

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 3 INVALID EXECUTION ENVIRONMENT"
        )

    if (
        safety.get("public_market_data_read_enabled")
        is not True
    ):
        raise RuntimeError(
            "UNIT 3 PUBLIC MARKET READ DISABLED"
        )

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
                "UNIT 3 UNSAFE CONFIGURATION: " + key
            )

    print(
        "PASS: UNIT 3 RECEIVED UNIT 2 CONFIGURATION",
        flush=True
    )

    print(
        "PASS: UNIT 3 READ-ONLY SAFETY GATE",
        flush=True
    )

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
            "User-Agent": (
                "WEEX-Hybrid-Market-Data-V2"
            ),
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

    # --------------------------------------------------------
    # MEASURE REQUEST LATENCY
    # DO NOT REUSE PREVIOUS DATA AFTER FAILURE
    # --------------------------------------------------------

    request_start = time.monotonic()

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
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

    except Exception as exc:

        print(
            "UNIT 3 UNEXPECTED REQUEST ERROR =",
            repr(exc),
            flush=True
        )

        raise

    received_time_ms = int(
        time.time() * 1000
    )

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

    exchange_time_ms = validated[
        "exchange_time_ms"
    ]

    market_age_ms = validated[
        "market_age_ms"
    ]

    # ========================================================
    # ORIGINAL UNIT 3 -> UNIT 4 INTERFACE
    # PRESERVE ALL EIGHT EXISTING SNAPSHOT FIELDS
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
        key not in market_snapshot
        for key in required_fields
    ):
        raise RuntimeError(
            "UNIT 3 MARKET SNAPSHOT INCOMPLETE"
        )

    print(
        "UNIT 3 HTTP STATUS =",
        http_status,
        flush=True
    )

    print(
        "PASS: UNIT 3 LIVE BTC MARK PRICE =",
        live_price,
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
# RUN UNIT 3 VALIDATION FIRST
# ============================================================

FRESH_UNIT_3_OPTIMIZATION_READY = (
    unit_3_validation_tests_v2()
)


# ============================================================
# RUN UNIT 3 LIVE PUBLIC MARKET READ SECOND
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END COMPLETE UNIT 3 REPLACEMENT V2
# UNIT 4 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 4 V5 REPLACEMENT
# WEEX MARK DATA + EMA + ATR + ADJUSTABLE STRATEGIES
# ONE COMPLETE UNIT / ZERO INDENTATION
# NO SEPARATE ADAPTER / NO ORDER SUBMISSION
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error


# ============================================================
# 4.1 CENTRAL ADJUSTABLE QUALIFICATION PARAMETERS
# ============================================================
# Change values here to tune strategy sensitivity.
# These settings are also published into Unit 2's
# qualification configuration for downstream units.
#
# EARLY structure uses EMA19/50 direction.
# STRICT structure uses EMA19/50/200 alignment.
#
# SCALP remains subordinate to developing or qualified
# BREAKOUT and STRUCTURE candidates.
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
        "proximity_atr": 0.50,
        "confirmation_atr": 0.10,
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
        "ema_compression_atr_max": 0.70,
        "range_atr_max": 8.0,
        "momentum_atr_max": 1.50,
        "preliminary_ema_separation_percent": 0.03,
        "preliminary_move_5m_percent": 0.015,
        "quality_threshold": 70.0,
        "minimum_fee_coverage_multiplier": 2.0,
    },
}


# ============================================================
# 4.2 GENERAL VALIDATION HELPERS
# ============================================================

def unit_4_v5_number(value, name):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 4 INVALID NUMBER: " + name
        )

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID NUMBER: " + name
        ) from exc

    if not math.isfinite(result):
        raise RuntimeError(
            "UNIT 4 NONFINITE NUMBER: " + name
        )

    return result


def unit_4_v5_positive(value, name, allow_zero=True):

    result = unit_4_v5_number(value, name)

    if result < 0 or (result == 0 and not allow_zero):
        raise RuntimeError(
            "UNIT 4 INVALID RANGE: " + name
        )

    return result


def unit_4_v5_integer(value, name, minimum, maximum):

    result = unit_4_v5_number(value, name)

    if (
        not result.is_integer()
        or not minimum <= result <= maximum
    ):
        raise RuntimeError(
            "UNIT 4 INVALID INTEGER: " + name
        )

    return int(result)


def unit_4_v5_ema(prices, period):

    if len(prices) < period:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT EMA HISTORY"
        )

    current = sum(prices[:period]) / period
    alpha = 2.0 / (period + 1.0)

    for price in prices[period:]:
        current = alpha * price + (1 - alpha) * current

    return current


def unit_4_v5_same_direction(move, direction):

    if direction == "LONG":
        return move > 0

    if direction == "SHORT":
        return move < 0

    return False


# ============================================================
# 4.3 VALIDATE CLOSED WEEX CANDLES
# ============================================================

def unit_4_v5_normalize_candles(rows, market_time_ms):

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 4 INVALID KLINE RESPONSE"
        )

    candles = []

    for row in rows:

        if not isinstance(row, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 INVALID KLINE ROW"
            )

        if len(row) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE KLINE ROW"
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
                "UNIT 4 INVALID OHLC DATA"
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
        key=lambda item: item["open_time_ms"]
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
        c for c in candles
        if c["close_time_ms"] <= market_time_ms
    ]

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED HISTORY"
        )

    return candles, closed


# ============================================================
# 4.4 COMPLETE UNIT 4 MARKET ANALYSIS
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)
    print("UNIT 4 COMPLETE ADJUSTABLE V5 START", flush=True)

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    tuning = UNIT_4_V5_TUNING

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 CONFIG MISSING")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 MARKET SNAPSHOT MISSING")

    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != "BTCUSDT"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 3 HANDOVER INVALID"
        )

    exchange = config.get("exchange", {})
    qualification = config.get("qualification", {})
    safety = config.get("safety", {})

    if not all(
        isinstance(section, dict)
        for section in (exchange, qualification, safety)
    ):
        raise RuntimeError(
            "UNIT 4 CONFIG STRUCTURE INVALID"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or safety.get(
            "public_market_data_read_enabled"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 4 EXCHANGE CONFIG INVALID"
        )

    if tuple(
        qualification.get("common", {}).get(
            "mode_priority", ()
        )
    ) != ("BREAKOUT", "STRUCTURE", "SCALP"):
        raise RuntimeError(
            "UNIT 4 MODE PRIORITY INVALID"
        )

    b = tuning["breakout"]
    s = tuning["structure"]
    p = tuning["scalp"]
    c = tuning["common"]

    max_age = unit_4_v5_positive(
        c["market_age_seconds_max"],
        "MARKET AGE LIMIT",
        False
    )

    max_candle_age = unit_4_v5_positive(
        c["candle_age_seconds_max"],
        "CANDLE AGE LIMIT",
        False
    )

    market_time_ms = int(
        unit_4_v5_positive(
            market["exchange_time_ms"],
            "MARKET TIMESTAMP",
            False
        )
    )

    live_mark = unit_4_v5_positive(
        market["price"], "MARK PRICE", False
    )

    current_time_ms = int(time.time() * 1000)

    if not (
        0 <= current_time_ms - market_time_ms
        <= max_age * 1000
    ):
        raise RuntimeError(
            "UNIT 4 STALE UNIT 3 MARK PRICE"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 WEEX BASE URL INVALID"
        )

    # ========================================================
    # LIVE PUBLIC MARK-PRICE CANDLES
    # ========================================================

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 300,
    })

    request = urllib.request.Request(
        base_url + endpoint + "?" + query,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Unit4-Adjustable-V5",
        }
    )

    started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            http_status = response.getcode()
            payload = response.read().decode("utf-8")

    except (urllib.error.HTTPError,
            urllib.error.URLError) as exc:
        raise RuntimeError(
            "UNIT 4 WEEX CANDLE REQUEST FAILED"
        ) from exc

    latency_ms = (
        time.monotonic() - started
    ) * 1000.0

    if http_status != 200:
        raise RuntimeError(
            "UNIT 4 WEEX HTTP STATUS NOT 200"
        )

    try:
        rows = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 WEEX JSON INVALID"
        ) from exc

    candles, closed = unit_4_v5_normalize_candles(
        rows, market_time_ms
    )

    latest = closed[-1]
    previous = closed[-2]

    candle_age_seconds = (
        market_time_ms - latest["close_time_ms"]
    ) / 1000.0

    if not (
        0 <= candle_age_seconds <= max_candle_age
    ):
        raise RuntimeError(
            "UNIT 4 CLOSED CANDLE STALE"
        )

    prices = [item["close"] for item in closed]

    ema19 = unit_4_v5_ema(prices, 19)
    ema50 = unit_4_v5_ema(prices, 50)
    ema100 = unit_4_v5_ema(prices, 100)
    ema200 = unit_4_v5_ema(prices, 200)

    latest_close = latest["close"]
    previous_close = previous["close"]

    separation = abs(
        ema19 - ema50
    ) / ema50 * 100.0

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
            latest_close - reference
        ) / reference * 100.0

    # ========================================================
    # ATR14
    # ========================================================

    true_ranges = []

    for i in range(1, len(closed)):

        item = closed[i]
        previous_price = closed[i - 1]["close"]

        true_ranges.append(max(
            item["high"] - item["low"],
            abs(item["high"] - previous_price),
            abs(item["low"] - previous_price)
        ))

    atr14 = sum(true_ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError(
            "UNIT 4 ATR14 INVALID"
        )

    atr_percent = (
        atr14 / latest_close
    ) * 100.0

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

    common_votes_required = unit_4_v5_integer(
        c["direction_votes_required"],
        "COMMON DIRECTION VOTES",
        1, 3
    )

    direction = "NONE"

    if (
        long_votes >= common_votes_required
        and long_votes > short_votes
    ):
        direction = "LONG"

    elif (
        short_votes >= common_votes_required
        and short_votes > long_votes
    ):
        direction = "SHORT"

    def votes_sufficient(side, required):

        count = (
            long_votes if side == "LONG"
            else short_votes
        )

        return count >= unit_4_v5_integer(
            required,
            "STRATEGY DIRECTION VOTES",
            1, 3
        )

    def momentum_at(period):

        period = unit_4_v5_integer(
            period,
            "MOMENTUM PERIOD",
            1, 120
        )

        if period not in moves:
            raise RuntimeError(
                "UNIT 4 UNSUPPORTED MOMENTUM PERIOD"
            )

        return moves[period]

    # ========================================================
    # ADJUSTABLE BREAKOUT
    # ========================================================

    breakout_lookback = unit_4_v5_integer(
        b["lookback_candles"],
        "BREAKOUT LOOKBACK",
        2, 45
    )

    reference_candles = closed[
        -breakout_lookback - 1:-1
    ]

    support = min(
        item["low"] for item in reference_candles
    )

    resistance = max(
        item["high"] for item in reference_candles
    )

    proximity = unit_4_v5_positive(
        b["proximity_atr"],
        "BREAKOUT PROXIMITY"
    )

    confirmation = unit_4_v5_positive(
        b["confirmation_atr"],
        "BREAKOUT CONFIRMATION"
    )

    breakout_max_extension = unit_4_v5_positive(
        b["maximum_extension_atr"],
        "BREAKOUT EXTENSION",
        False
    )

    breakout_atr_min = unit_4_v5_positive(
        b["minimum_atr_percent"],
        "BREAKOUT MIN ATR"
    )

    def breakout_eligible(side):

        fast_ok = (
            not b["require_fast_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["fast_momentum_minutes"]),
                side
            )
        )

        slow_ok = (
            not b["require_slow_momentum"]
            or unit_4_v5_same_direction(
                momentum_at(b["slow_momentum_minutes"]),
                side
            )
        )

        return bool(
            b["enabled"]
            and direction == side
            and votes_sufficient(
                side, b["direction_votes_required"]
            )
            and fast_ok
            and slow_ok
            and atr_percent >= breakout_atr_min
        )

    breakout_long_eligible = breakout_eligible("LONG")
    breakout_short_eligible = breakout_eligible("SHORT")

    long_breakout_distance = (
        latest_close - resistance
    ) / atr14

    short_breakout_distance = (
        support - latest_close
    ) / atr14

    breakout_confirmed_long = bool(
        breakout_long_eligible
        and long_breakout_distance > confirmation
        and long_breakout_distance
        <= breakout_max_extension
    )

    breakout_confirmed_short = bool(
        breakout_short_eligible
        and short_breakout_distance > confirmation
        and short_breakout_distance
        <= breakout_max_extension
    )

    breakout_developing_long = bool(
        b["developing_candidate_enabled"]
        and breakout_long_eligible
        and -proximity
        <= long_breakout_distance
        <= confirmation
    )

    breakout_developing_short = bool(
        b["developing_candidate_enabled"]
        and breakout_short_eligible
        and -proximity
        <= short_breakout_distance
        <= confirmation
    )

    # ========================================================
    # ADJUSTABLE STRUCTURE
    # ========================================================

    alignment = str(
        s["ema_alignment_mode"]
    ).upper()

    if alignment not in ("STRICT", "EARLY"):
        raise RuntimeError(
            "UNIT 4 INVALID STRUCTURE ALIGNMENT MODE"
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

    structure_min_separation = unit_4_v5_positive(
        s["minimum_ema_separation_percent"],
        "STRUCTURE MIN EMA SEPARATION"
    )

    structure_pullback = unit_4_v5_positive(
        s["pullback_tolerance_atr"],
        "STRUCTURE PULLBACK"
    )

    structure_max_extension = unit_4_v5_positive(
        s["maximum_extension_atr"],
        "STRUCTURE MAX EXTENSION",
        False
    )

    fast_structure_move = momentum_at(
        s["fast_momentum_minutes"]
    )

    slow_structure_move = momentum_at(
        s["slow_momentum_minutes"]
    )

    def structure_eligible(side):

        fast_ok = (
            not s["require_fast_momentum"]
            or unit_4_v5_same_direction(
                fast_structure_move, side
            )
        )

        slow_ok = (
            not s["require_slow_momentum"]
            or unit_4_v5_same_direction(
                slow_structure_move, side
            )
        )

        signed_distance = (
            latest_close - ema19
            if side == "LONG"
            else ema19 - latest_close
        ) / atr14

        # Pullback entries are permitted near EMA19.
        # Continuation entries must remain on the
        # correct side of EMA19 and within extension.

        pullback_ok = (
            abs(signed_distance) <= structure_pullback
        )

        continuation_ok = (
            s["allow_continuation_entry"]
            and 0 <= signed_distance
            <= structure_max_extension
        )

        return bool(
            s["enabled"]
            and structure_side == side
            and direction == side
            and votes_sufficient(
                side, s["direction_votes_required"]
            )
            and fast_ok
            and slow_ok
            and separation >= structure_min_separation
            and abs(signed_distance)
            <= structure_max_extension
            and (pullback_ok or continuation_ok)
        )

    structure_developing_long = (
        structure_eligible("LONG")
    )

    structure_developing_short = (
        structure_eligible("SHORT")
    )

    structure_fast_confirmed = (
        unit_4_v5_same_direction(
            fast_structure_move, structure_side
        )
    )

    structure_slow_confirmed = (
        unit_4_v5_same_direction(
            slow_structure_move, structure_side
        )
    )

    # ========================================================
    # ADJUSTABLE SCALP / SIDEWAYS EVIDENCE
    # ========================================================

    scalp_lookback = unit_4_v5_integer(
        p["range_lookback_candles"],
        "SCALP LOOKBACK",
        2, 45
    )

    scalp_history = closed[
        -scalp_lookback - 1:-1
    ]

    scalp_high = max(
        item["high"] for item in scalp_history
    )

    scalp_low = min(
        item["low"] for item in scalp_history
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
        and compression_atr <= unit_4_v5_positive(
            p["ema_compression_atr_max"],
            "SCALP EMA COMPRESSION"
        )
        and scalp_range_atr <= unit_4_v5_positive(
            p["range_atr_max"],
            "SCALP RANGE"
        )
        and momentum15_atr <= unit_4_v5_positive(
            p["momentum_atr_max"],
            "SCALP MOMENTUM"
        )
        and not higher_mode_developing
    )

    # Price extension is diagnostic and still
    # retained as the existing Unit 5 evidence flag.

    price_extension_atr = (
        abs(latest_close - ema19) / atr14
    )

    price_overextended = bool(
        price_extension_atr > structure_max_extension
    )

    # ========================================================
    # PROPAGATE CENTRAL TUNING FOR UNITS 5 AND 6
    # ========================================================

    common_cfg = qualification["common"]
    breakout_cfg = qualification["breakout"]
    structure_cfg = qualification["structure"]
    scalp_cfg = qualification["scalp"]

    common_cfg["direction_votes_required"] = (
        common_votes_required
    )

    breakout_cfg.update({
        "enabled": bool(b["enabled"]),
        "developing_candidate_enabled": bool(
            b["developing_candidate_enabled"]
        ),
        "support_resistance_lookback":
            breakout_lookback,
        "developing_proximity_atr": proximity,
        "confirmation_distance_atr": confirmation,
        "max_price_extension_atr":
            breakout_max_extension,
        "minimum_atr_percent": breakout_atr_min,
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
            structure_min_separation,
        "pullback_tolerance_atr":
            structure_pullback,
        "allow_continuation_entry": bool(
            s["allow_continuation_entry"]
        ),
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
        "require_sideways_market": bool(
            p["require_sideways_market"]
        ),
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
    # BUILD UNIT 4 -> UNIT 5 SNAPSHOT
    # ========================================================

    snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
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
            dict(item) for item in closed[-60:]
        ],
        "candle_count": len(candles),
        "closed_candle_count": len(closed),
        "newest_returned_candle_closed": (
            candles[-1]["close_time_ms"]
            <= market_time_ms
        ),
        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "atr14": atr14,
        "atr_percent": atr_percent,

        "support20": support,
        "resistance20": resistance,
        "range20_atr_ratio": (
            resistance - support
        ) / atr14,

        "near_resistance": bool(
            latest_close >= resistance - proximity * atr14
        ),
        "near_support": bool(
            latest_close <= support + proximity * atr14
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
            structure_fast_confirmed,
        "structure_momentum_slow_confirmed":
            structure_slow_confirmed,

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

        "price_extension_cluster": (
            price_extension_atr
        ),
        "price_overextended": price_overextended,

        "strategy_evidence_version":
            "U4_HYBRID_V2",
        "qualification_tuning_revision":
            "UNIT4_V5_FULLY_INTEGRATED",

        "qualification_settings": {
            "breakout_lookback": breakout_lookback,
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

    # ========================================================
    # VERIFY DOWNSTREAM INPUTS
    # ========================================================

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
    # RENDER LOG REPORT
    # ========================================================

    print("UNIT 4 HTTP STATUS =", http_status, flush=True)
    print(
        "UNIT 4 REQUEST LATENCY MS =",
        round(latency_ms, 2),
        flush=True
    )
    print(
        "UNIT 4 CLOSED CANDLES =",
        len(closed),
        flush=True
    )
    print("UNIT 4 ATR14 =", round(atr14, 4), flush=True)
    print("UNIT 4 DIRECTION =", direction, flush=True)
    print(
        "UNIT 4 DIRECTION VOTES =",
        long_votes, "/", short_votes,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT PROXIMITY ATR =",
        proximity, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMATION ATR =",
        confirmation, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMED LONG =",
        breakout_confirmed_long, flush=True
    )
    print(
        "UNIT 4 BREAKOUT CONFIRMED SHORT =",
        breakout_confirmed_short, flush=True
    )
    print(
        "UNIT 4 BREAKOUT DEVELOPING LONG =",
        breakout_developing_long, flush=True
    )
    print(
        "UNIT 4 BREAKOUT DEVELOPING SHORT =",
        breakout_developing_short, flush=True
    )

    print(
        "UNIT 4 STRUCTURE EMA MODE =",
        alignment, flush=True
    )
    print(
        "UNIT 4 STRUCTURE TREND SIDE =",
        structure_side, flush=True
    )
    print(
        "UNIT 4 STRUCTURE DEVELOPING LONG =",
        structure_developing_long, flush=True
    )
    print(
        "UNIT 4 STRUCTURE DEVELOPING SHORT =",
        structure_developing_short, flush=True
    )

    print(
        "UNIT 4 SCALP QUALITY TARGET =",
        p["quality_threshold"], flush=True
    )
    print(
        "UNIT 4 SCALP SIDEWAYS =",
        sideways_candidate, flush=True
    )
    print(
        "UNIT 4 SCALP MIN MOVE 5M % =",
        p["preliminary_move_5m_percent"],
        flush=True
    )

    print(
        "UNIT 4 PRICE OVEREXTENDED =",
        price_overextended, flush=True
    )
    print(
        "UNIT 4 EVIDENCE VERSION =",
        snapshot["strategy_evidence_version"],
        flush=True
    )
    print(
        "UNIT 4 TUNING REVISION =",
        snapshot["qualification_tuning_revision"],
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
    print("UNIT 4 EXCHANGE WRITE = NONE", flush=True)
    print(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 4 ADAPTER RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return snapshot


# ============================================================
# 4.5 SINGLE EXECUTION CALL
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END COMPLETE UNIT 4 V5 REPLACEMENT
# UNIT 5 V7 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 5 V8 REPLACEMENT
# FULLY ADJUSTABLE HYBRID CLASSIFICATION
# WEEX DEMO / ZERO INDENTATION
# UNIT 4 V5 -> UNIT 5 V8 -> UNIT 6
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
        "UNIT 5 COMPLETE ADJUSTABLE V8 START",
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
    ) != "UNIT4_V5_FULLY_INTEGRATED":
        raise RuntimeError(
            "UNIT 5 ADJUSTABLE UNIT 4 V5 REQUIRED"
        )

    if (
        analysis.get("exchange") != "WEEX"
        or analysis.get("api_version") != "V3"
        or analysis.get("symbol") != "BTCUSDT"
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

    breakout_qualified = bool(
        breakout_enabled
        and breakout_side != "NONE"
        and breakout_side == direction_evidence
        and breakout_votes_ok
        and breakout_momentum_ok
        and not overextended
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

    # ========================================================
    # 5.10 SCALP COST ESTIMATE
    # ========================================================

    fee_sides = (
        int(p.get("include_entry_fee") is True)
        + int(p.get("include_exit_fee") is True)
    )

    round_trip_fee = (
        setting_number(
            p, "estimated_taker_fee_percent", 0.08
        ) * fee_sides
        + setting_number(
            p, "estimated_slippage_percent", 0.0
        )
    )

    # ========================================================
    # 5.11 PRESERVE ORIGINAL 42 OUTPUT FIELDS
    # ========================================================

    candidate = {
        "symbol": "BTCUSDT",
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

        "price_above_ema19": live_price > ema19,
        "price_above_ema50": live_price > ema50,
        "price_above_ema200": live_price > ema200,
        "latest_close_above_previous": (
            latest_close > previous_close
        ),

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
        "breakout_fast_support": breakout_fast_support,
    }

    if len(candidate) != 42:
        raise RuntimeError(
            "UNIT 5 ORIGINAL 42-FIELD CONTRACT FAILED"
        )

    # ========================================================
    # 5.12 EXTENDED ADJUSTABLE HANDOVER TO UNIT 6
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
            "UNIT5_V8_ADJUSTABLE",

        "original_unit5_qualified": (
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
            "INTEGRATED_V8_CLASSIFIER",

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

        "scalp_preliminary": scalp_preliminary,

        # New explicit adjustable diagnostics

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
    })

    # ========================================================
    # 5.13 FINAL CONSISTENCY CHECKS
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
            "UNIT 5 QUALIFIED DIRECTION INVALID"
        )

    if candidate_mode == "SCALP" and (
        higher_mode_developing
        or breakout_qualified
        or structure_qualified
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PRIORITY VIOLATION"
        )

    if (
        candidate["trade_authorized"] is not False
        or candidate["order_payload_created"] is not False
    ):
        raise RuntimeError(
            "UNIT 5 ORDER BOUNDARY VIOLATION"
        )

    # ========================================================
    # 5.14 RENDER REPORT
    # ========================================================

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
        "UNIT 5 STRUCTURE EMA MODE =",
        structure_ema_mode,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE TREND =",
        structure_trend,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE VOTES PASS =",
        structure_votes_ok,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE MOMENTUM PASS =",
        structure_momentum_ok,
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
        "UNIT 5 SCALP EMA MIN % =",
        scalp_ema_min,
        flush=True
    )

    print(
        "UNIT 5 SCALP MOVE MIN % =",
        scalp_move_min,
        flush=True
    )

    print(
        "UNIT 5 SCALP QUALITY TARGET =",
        scalp_quality_minimum,
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

    print(
        "UNIT 5 OPTIMIZATION V8 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return candidate


# ============================================================
# 5.15 DETERMINISTIC VALIDATION
# ============================================================

def unit_5_validation_v8():

    print("=" * 80, flush=True)
    print("UNIT 5 VALIDATION V8 START", flush=True)

    # Tests exercise the same integrated classifier
    # used for actual Unit 4 V5 snapshots.

    test_config = {
        "qualification": {

            "common": {
                "mode_priority": (
                    "BREAKOUT", "STRUCTURE", "SCALP"
                ),
                "direction_votes_required": 2,
            },

            "breakout": {
                "enabled": True,
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
                "fast_momentum_minutes": 5,
                "slow_momentum_minutes": 15,
                "require_fast_momentum": True,
                "require_slow_momentum": True,
                "max_price_extension_atr": 2.0,
            },

            "scalp": {
                "enabled": True,
                "require_sideways_market": True,
                "preliminary_ema_separation_percent":
                    0.03,
                "preliminary_move_5m_percent":
                    0.015,
                "quality_threshold": 70,
                "minimum_fee_coverage_multiplier": 2,
                "include_entry_fee": True,
                "include_exit_fee": True,
                "estimated_taker_fee_percent": 0.08,
            },
        },

        "market_data_policy": {
            "max_market_age_seconds": 120,
        },
    }

    def market(**changes):

        data = {
            "exchange": "WEEX",
            "api_version": "V3",
            "symbol": "BTCUSDT",
            "price_type": "MARK",
            "read_only": True,

            "strategy_evidence_version":
                "U4_HYBRID_V2",

            "qualification_tuning_revision":
                "UNIT4_V5_FULLY_INTEGRATED",

            "exchange_time_ms": 1800000060000,
            "latest_close_time_ms": 1800000000000,

            "live_mark_price": 80100.0,
            "previous_close": 80090.0,
            "latest_close": 80100.0,

            "ema19": 80080.0,
            "ema50": 80020.0,
            "ema200": 80140.0,

            "ema19_50_separation_pct": 0.075,
            "ema_structure": "MIXED",

            "short_term_move_pct": 0.02,
            "move_1m_pct": 0.02,
            "move_5m_pct": 0.05,
            "move_15m_pct": 0.12,
            "move_30m_pct": 0.15,
            "move_60m_pct": 0.25,
            "move_120m_pct": 0.30,

            "atr14": 100.0,

            "direction_evidence": "LONG",
            "direction_long_votes": 3,
            "direction_short_votes": 0,

            "breakout_confirmed_long": False,
            "breakout_confirmed_short": False,
            "breakout_developing_long": False,
            "breakout_developing_short": False,

            "structure_developing_long": True,
            "structure_developing_short": False,

            "structure_trend_direction": "LONG",
            "structure_ema_alignment_mode": "EARLY",

            "sideways_candidate": False,
            "price_overextended": False,
        }

        data.update(changes)
        return data

    tests = (
        (
            "EARLY STRUCTURE LONG MIXED EMA200",
            market(),
            "STRUCTURE",
            "QUALIFIED",
        ),

        (
            "QUALIFIED STRUCTURE BEATS DEVELOPING BREAKOUT",
            market(
                breakout_developing_long=True
            ),
            "STRUCTURE",
            "QUALIFIED",
        ),

        (
            "CONFIRMED BREAKOUT PRIORITY",
            market(
                breakout_confirmed_long=True
            ),
            "BREAKOUT",
            "QUALIFIED",
        ),

        (
            "BREAKOUT DEVELOPING PROTECTION",
            market(
                breakout_developing_long=True,
                structure_developing_long=False
            ),
            "BREAKOUT",
            "DEVELOPING",
        ),

        (
            "STRUCTURE DEVELOPING PROTECTION",
            market(
                move_5m_pct=-0.05
            ),
            "STRUCTURE",
            "DEVELOPING",
        ),

        (
            "STRUCTURE VOTES TOO LOW",
            market(
                direction_long_votes=1,
                direction_short_votes=1
            ),
            "STRUCTURE",
            "DEVELOPING",
        ),

        (
            "SCALP SIDEWAYS PENDING QUALITY",
            market(
                structure_developing_long=False,
                sideways_candidate=True
            ),
            "SCALP",
            "PENDING_UNIT_6",
        ),

        (
            "SCALP NOT SIDEWAYS REJECTED",
            market(
                structure_developing_long=False
            ),
            "NONE",
            "REJECTED",
        ),

        
(
    "BREAKOUT MOMENTUM INSUFFICIENT",
    market(
        breakout_confirmed_long=True,
        move_5m_pct=-0.05,
        structure_developing_long=False
    ),
    "NONE",
    "NONE",
),


        (
            "SCALP BELOW ADJUSTABLE THRESHOLD",
            market(
                ema19=80080.0,
                ema50=80070.0,
                ema200=80140.0,
                ema19_50_separation_pct=0.0125,
                move_1m_pct=0.0,
                move_5m_pct=0.005,
                structure_developing_long=False,
                sideways_candidate=True
            ),
            "NONE",
            "NONE",
        ),
    )

    passed = 0
    failed = 0

    for name, snapshot, expected_mode, expected_stage in tests:

        try:
            result = fresh_reconstruction_unit_5(
                test_config,
                snapshot
            )

            success = (
                result["candidate_mode"] == expected_mode
                and result["candidate_stage"] == expected_stage
                and result["trade_authorized"] is False
                and result["strategy_evidence_version"]
                == "U5_HYBRID_ADJUSTABLE_V3"
            )

        except Exception as exc:

            success = False

            print(
                "UNIT 5 TEST EXCEPTION:",
                name,
                str(exc),
                flush=True
            )

        if success:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 5 TEST:",
            name,
            "=",
            "PASS" if success else "FAIL",
            flush=True
        )

    print(
        "UNIT 5 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 5 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 5 V8 VALIDATION FAILED"
        )

    print(
        "UNIT 5 VALIDATION V8 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# 5.16 SINGLE EXECUTION SEQUENCE
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


# ============================================================
# END COMPLETE UNIT 5 V8 REPLACEMENT
# UNIT 6 FOLLOWS
# ZERO INDENTATION
# ============================================================


# ============================================================
# START COMPLETE UNIT 6 V9 REPLACEMENT
# WEEX DEMO STRATEGY ARBITRATION AND QUALITY
# INTEGRATED WITH UNIT 4 V5 AND UNIT 5 V8
# PRESERVES UNIT 7 OUTPUT CONTRACT
# ZERO INDENTATION / ONE EXECUTION CALL
# ============================================================

import copy
import math


# ============================================================
# 6.1 VALIDATION HELPERS
# ============================================================

def unit_6_v9_number(value, label):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 6 INVALID NUMBER: " + label
        )

    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 6 INVALID NUMBER: " + label
        ) from exc

    if not math.isfinite(value):
        raise RuntimeError(
            "UNIT 6 NONFINITE NUMBER: " + label
        )

    return value


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
# 6.2 MAIN CLASSIFICATION AND ADMISSION
# ============================================================

def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate
):

    print("=" * 80, flush=True)
    print(
        "UNIT 6 COMPLETE ADJUSTABLE V9 START",
        flush=True
    )

    # ========================================================
    # INPUT CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 6 UNIT 2 CONFIG INVALID"
        )

    if not isinstance(unit_4_analysis, dict):
        raise RuntimeError(
            "UNIT 6 UNIT 4 ANALYSIS INVALID"
        )

    if not isinstance(unit_5_candidate, dict):
        raise RuntimeError(
            "UNIT 6 UNIT 5 CANDIDATE INVALID"
        )

    config = unit_2_config
    analysis = unit_4_analysis
    candidate = unit_5_candidate

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
        ("SCALP", scalp),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 6 CONFIG MISSING: " + name
            )

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 MODE PRIORITY INVALID"
        )

    if (
        analysis.get("strategy_evidence_version")
        != "U4_HYBRID_V2"
        or analysis.get(
            "qualification_tuning_revision"
        ) != "UNIT4_V5_FULLY_INTEGRATED"
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 4 V5 EVIDENCE MISSING"
        )

    if (
        candidate.get("strategy_evidence_version")
        != "U5_HYBRID_ADJUSTABLE_V3"
        or candidate.get(
            "qualification_tuning_revision"
        ) != "UNIT5_V8_FULLY_ADJUSTABLE"
    ):
        raise RuntimeError(
            "UNIT 6 UNIT 5 V8 EVIDENCE MISSING"
        )

    if (
        candidate.get("symbol") != "BTCUSDT"
        or analysis.get("symbol") != "BTCUSDT"
    ):
        raise RuntimeError(
            "UNIT 6 SYMBOL MISMATCH"
        )

    if (
        analysis.get("read_only") is not True
        or candidate.get("read_only") is not True
        or candidate.get(
            "trade_authorized"
        ) is not False
        or candidate.get(
            "order_payload_created"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 6 INPUT SAFETY VIOLATION"
        )

    
        # ========================================================
    # UNIT 6 POSITION SAFETY POLICY
    # USE ORIGINAL UNIT 2 STRATEGY CONFIGURATION
    # ========================================================

    strategy = config.get("strategy")

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT 6 STRATEGY CONFIG MISSING"
        )

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 6 REQUIRED SAFETY DISABLED: "
                + key
            )

    print(
        "PASS: UNIT 6 ORIGINAL POSITION SAFETY POLICY",
        flush=True
    )


    # ========================================================
    # UNIT 5 CANDIDATE STATE
    # ========================================================

    stage = candidate.get(
        "candidate_stage", "NONE"
    )

    mode = candidate.get(
        "candidate_mode", "NONE"
    )

    incoming_active_mode = candidate.get(
        "active_mode", "NONE"
    )

    incoming_direction = candidate.get(
        "direction", "NONE"
    )

    qualified = unit_6_v9_bool(
        candidate.get("qualified"),
        "UNIT 5 QUALIFIED"
    )

    if mode not in (
        "NONE", "BREAKOUT", "STRUCTURE", "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE MODE"
        )

    if stage not in (
        "NONE",
        "REJECTED",
        "DEVELOPING",
        "QUALIFIED",
        "PENDING_UNIT_6",
    ):
        raise RuntimeError(
            "UNIT 6 INVALID CANDIDATE STAGE"
        )

    if incoming_active_mode not in (
        "NONE", "BREAKOUT", "STRUCTURE"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID ACTIVE MODE"
        )

    if incoming_direction not in (
        "NONE", "LONG", "SHORT"
    ):
        raise RuntimeError(
            "UNIT 6 INVALID DIRECTION"
        )

    if qualified != (stage == "QUALIFIED"):
        raise RuntimeError(
            "UNIT 6 CONTRADICTORY UNIT 5 STATE"
        )

    if qualified and (
        mode != incoming_active_mode
        or incoming_direction == "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 QUALIFIED STATE MISMATCH"
        )

    if not qualified and (
        incoming_active_mode != "NONE"
        or incoming_direction != "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 UNQUALIFIED ACTIVE STATE"
        )

    # ========================================================
    # MARKET AND FRESHNESS
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
        price, live_price, ema19, ema50,
        ema100, ema200, atr
    ) <= 0:
        raise RuntimeError(
            "UNIT 6 MARKET INDICATORS INVALID"
        )

    move_1m = a("move_1m_pct")
    move_5m = a("move_5m_pct")
    move_15m = a("move_15m_pct")

    atr_pct = atr / price * 100.0

    candle_age = c(
        "candidate_age_seconds"
    )

    max_age = unit_6_v9_number(
        config.get(
            "market_data_policy", {}
        ).get("max_market_age_seconds", 120),
        "MAX CANDLE AGE"
    )

    fresh = (
        candidate.get("candle_data_fresh") is True
        and 0 <= candle_age <= max_age
    )

    # ========================================================
    # HIGHER STRATEGY PRIORITY
    # ========================================================

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

    if sum((
        breakout_ready,
        structure_ready,
        scalp_ready
    )) > 1:
        raise RuntimeError(
            "UNIT 6 CONFLICTING READY STRATEGIES"
        )

    # ========================================================
    # QUALITY CONFIGURATION
    # ========================================================

    scalp_minimum = unit_6_v9_number(
        scalp.get("quality_threshold", 70),
        "SCALP QUALITY MINIMUM"
    )

    if not 0 <= scalp_minimum <= 100:
        raise RuntimeError(
            "UNIT 6 INVALID SCALP QUALITY MINIMUM"
        )

    fee_coverage = unit_6_v9_number(
        scalp.get(
            "minimum_fee_coverage_multiplier", 2
        ),
        "FEE COVERAGE MULTIPLIER"
    )

    if fee_coverage < 1:
        raise RuntimeError(
            "UNIT 6 INVALID FEE COVERAGE MULTIPLIER"
        )

    estimated_fee = c(
        "estimated_round_trip_fee_pct"
    )

    if estimated_fee < 0:
        raise RuntimeError(
            "UNIT 6 INVALID FEE ESTIMATE"
        )

    # If the upstream configuration has not
    # enabled fee estimation, fail closed for SCALP.

    fee_estimate_verified = (
        scalp.get("include_entry_fee") is True
        and scalp.get("include_exit_fee") is True
        and unit_6_v9_number(
            scalp.get(
                "estimated_taker_fee_percent", 0
            ),
            "TAKER FEE"
        ) > 0
        and estimated_fee > 0
    )

    # ========================================================
    # SCALP SIDEWAYS POLICY
    # ========================================================

    sideways = unit_6_v9_bool(
        analysis.get("sideways_candidate"),
        "SIDEWAYS EVIDENCE"
    )

    sideways_required = unit_6_v9_bool(
        scalp.get("require_sideways_market", True),
        "SIDEWAYS REQUIRED"
    )

    sideways_pass = (
        sideways or not sideways_required
    )

    # ========================================================
    # SCALP DIRECTION AND PERSISTENCE
    # ========================================================

    scalp_side = candidate.get(
        "scalp_direction_candidate", "NONE"
    )

    if scalp_side not in (
        "LONG", "SHORT", "NONE"
    ):
        raise RuntimeError(
            "UNIT 6 SCALP DIRECTION INVALID"
        )

    direction_1m = unit_6_v9_side(move_1m)
    direction_5m = unit_6_v9_side(move_5m)
    direction_15m = unit_6_v9_side(move_15m)

    persistence_directions = (
        direction_1m,
        direction_5m,
        direction_15m,
    )

    persistence_window = 3

    persistence_required = 2

    persistence_confirmations = sum(
        d == scalp_side
        for d in persistence_directions
    ) if scalp_side != "NONE" else 0

    persistence_pass = (
        persistence_confirmations
        >= persistence_required
    )

    fifteen_minute_support_pass = (
        direction_15m == scalp_side
    )

    momentum_conflict = (
        scalp_side != "NONE"
        and direction_5m not in (
            scalp_side, "NONE"
        )
    )

    # ========================================================
    # SCALP QUALITY SCORING / MAXIMUM 100 POINTS
    #
    # PRICE ACTION                 30
    # DIRECTION PERSISTENCE        20
    # EMA LOCATION                 15
    # EMA QUALITY                  15
    # VOLATILITY AND EXHAUSTION    20
    #
    # These scores are diagnostics, not predictions.
    # ========================================================

    quality_score = 0.0

    price_action_score = 0.0
    persistence_score = 0.0
    location_score = 0.0
    ema_score = 0.0
    volatility_score = 0.0

    ema_separation_pct = abs(
        ema19 - ema50
    ) / ema50 * 100.0

    compression_limit = unit_6_v9_number(
        scalp.get(
            "ema_compression_atr_max", 0.7
        ),
        "EMA COMPRESSION LIMIT"
    )

    compression_atr = a(
        "ema_compression_atr"
    )

    ema_compressed = (
        compression_atr <= compression_limit
    )

    extension_atr = abs(
        price - ema19
    ) / atr

    # Existing early-entry protection.
    # Larger ATR extensions and reversal evidence
    # reduce the score instead of rewarding
    # late momentum.

    extreme_extension = (
        extension_atr > 1.5
    )

    spike_ratio = (
        abs(move_1m) /
        max(abs(move_5m) / 5.0, 0.000001)
    )

    extreme_spike = spike_ratio > 2.0

    late_impulse = (
        extreme_extension and extreme_spike
    )

    if scalp_side != "NONE":

        # Price action: max 30

        if direction_5m == scalp_side:
            price_action_score += 15

        if direction_1m == scalp_side:
            price_action_score += 10

        if abs(move_5m) >= unit_6_v9_number(
            scalp.get(
                "preliminary_move_5m_percent",
                0.015
            ),
            "SCALP MOVE MINIMUM"
        ):
            price_action_score += 5

        # Persistence: max 20

        persistence_score = (
            20.0
            * persistence_confirmations
            / persistence_window
        )

        # EMA location: max 15

        location_pass = (
            price >= ema19
            if scalp_side == "LONG"
            else price <= ema19
        )

        if location_pass:
            location_score += 10

        if (
            ema100 <= price
            if scalp_side == "LONG"
            else ema100 >= price
        ):
            location_score += 5

        # EMA quality: max 15

        if ema_compressed:
            ema_score += 10

        if (
            (ema19 >= ema50 and scalp_side == "LONG")
            or
            (ema19 <= ema50 and scalp_side == "SHORT")
        ):
            ema_score += 5

        # Volatility and exhaustion: max 20

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
            0, 100
        ),
        2
    )

    quality_pass = (
        quality_score >= scalp_minimum
    )

    # ========================================================
    # FEE COVERAGE
    #
    # Estimate a potential near-term price excursion,
    # then compare it to estimated round-trip costs.
    #
    # This is only a screening estimate, not a
    # guaranteed profit projection.
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
    # FINAL ADMISSION ARBITRATION
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
            and incoming_direction in (
                "LONG", "SHORT"
            )
            and candidate.get(
                "hybrid_breakout_qualified"
            ) is True
        ):

            execution_intent = True
            signal_qualified = True

            active_mode = "BREAKOUT"
            direction = incoming_direction

            admission_reason = (
                "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS"
            )

        elif (
            qualified
            and mode == "STRUCTURE"
            and structure_ready
            and incoming_direction in (
                "LONG", "SHORT"
            )
            and candidate.get(
                "hybrid_structure_qualified"
            ) is True
        ):

            execution_intent = True
            signal_qualified = True

            active_mode = "STRUCTURE"
            direction = incoming_direction

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
                "SCALP_ESTIMATED_FEE_COVERAGE_FAILED"
            )

        else:

            execution_intent = True
            signal_qualified = True

            active_mode = "SCALP"
            direction = scalp_side

            admission_reason = (
                "SCALP_QUALIFIED_FOR_NEXT_UNITS"
            )

    else:

        admission_reason = str(
            candidate.get(
                "qualification_reason",
                "NO_ACCEPTABLE_CANDIDATE"
            )
        )

    # ========================================================
    # FINAL INVARIANTS
    # ========================================================

    if execution_intent != signal_qualified:
        raise RuntimeError(
            "UNIT 6 EXECUTION INTENT MISMATCH"
        )

    if execution_intent:

        if (
            active_mode not in (
                "BREAKOUT", "STRUCTURE", "SCALP"
            )
            or direction not in (
                "LONG", "SHORT"
            )
        ):
            raise RuntimeError(
                "UNIT 6 INVALID ADMITTED SIGNAL"
            )

    else:

        if (
            active_mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 6 INVALID IDLE SIGNAL"
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
    # OUTPUT TO UNIT 7
    # Preserve original interface and diagnostics.
    # ========================================================

    quality_details = {
        "price_action_score": price_action_score,
        "persistence_score": round(
            persistence_score, 2
        ),
        "ema_location_score": location_score,
        "ema_quality_score": ema_score,
        "volatility_score": volatility_score,
        "extreme_extension": extreme_extension,
        "extreme_spike": extreme_spike,
        "late_impulse": late_impulse,
        "estimated_move_pct": projected_move_pct,
        "estimated_round_trip_fee_pct":
            estimated_fee,
        "required_move_pct": required_move_pct,
        "fee_coverage_pass": fee_coverage_pass,
        "fee_estimate_verified":
            fee_estimate_verified,
    }

    execution_candidate = {

        # Original Unit 7 required contract

        "execution_intent": execution_intent,
        "active_mode": active_mode,
        "direction": direction,
        "signal_qualified": signal_qualified,
        "unit_5_reason": candidate.get(
            "qualification_reason", "UNKNOWN"
        ),
        "admission_reason": admission_reason,

        # Original Unit 6 diagnostics

        "leverage_target": None,
        "leverage_regime":
            "WEEX_EXCHANGE_SETTING",

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

        "scalp_quality_score": quality_score,
        "scalp_quality_minimum":
            scalp_minimum,
        "scalp_quality_pass": quality_pass,
        "scalp_quality_details":
            quality_details,

        # Unit 5/Unit 4 traceability

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
            "UNIT6_V9_ADJUSTABLE",

        "market_data_fresh": fresh,

        # Execution boundary

        "position_sizing_performed": False,
        "order_payload_created": False,
        "exchange_write": False,
        "read_only": True,
        "trade_authorized": False,
    }

    # ========================================================
    # RENDER REPORT
    # ========================================================

    print(
        "UNIT 6 INPUT CANDIDATE MODE =",
        mode,
        flush=True
    )
    print(
        "UNIT 6 INPUT STAGE =",
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
        round(projected_move_pct, 5),
        flush=True
    )
    print(
        "UNIT 6 ESTIMATED ROUND TRIP FEE % =",
        round(estimated_fee, 5),
        flush=True
    )
    print(
        "UNIT 6 REQUIRED FEE COVERAGE MOVE % =",
        round(required_move_pct, 5),
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
        "UNIT 6 LEVERAGE CONTROL = WEEX ONLY",
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
# 6.3 VALIDATION
# DO NOT ACCESS WEEX FOR SYNTHETIC TESTS
# ============================================================

def unit_6_validation_v9():

    print("=" * 80, flush=True)
    print(
        "UNIT 6 VALIDATION V9 START",
        flush=True
    )

    # Use the actual Unit 4/5 handover structure.
    # Work only on copies, never mutate working config.

    config = copy.deepcopy(
        FRESH_RECONSTRUCTION_CONFIG
    )
    analysis = copy.deepcopy(
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
    original = copy.deepcopy(
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    )

    tests = []

    def scenario(
        name,
        modifications,
        expected_intent,
        expected_mode
    ):

        local = copy.deepcopy(original)

        local.update(modifications)

        # Explicitly retest consistent classification
        # states rather than forging account orders.

        result = fresh_reconstruction_unit_6(
            config,
            analysis,
            local
        )

        passed = (
            result["execution_intent"]
            is expected_intent
            and result["active_mode"]
            == expected_mode
            and result["exchange_write"] is False
            and result["order_payload_created"]
            is False
        )

        tests.append((name, passed))

    scenario(
        "NORMAL IDLE",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "NONE",
            "candidate_stage": "NONE",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": False,
            "higher_mode_developing": False,
        },
        False,
        "NONE"
    )

    scenario(
        "DEVELOPING BREAKOUT PROTECTED",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "BREAKOUT",
            "candidate_stage": "DEVELOPING",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": False,
            "higher_mode_developing": True,
        },
        False,
        "NONE"
    )

    scenario(
        "DEVELOPING STRUCTURE PROTECTED",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "STRUCTURE",
            "candidate_stage": "DEVELOPING",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": False,
            "higher_mode_developing": True,
        },
        False,
        "NONE"
    )

    scenario(
        "QUALIFIED BREAKOUT HANDOVER",
        {
            "qualified": True,
            "active_mode": "BREAKOUT",
            "direction": "LONG",
            "candidate_mode": "BREAKOUT",
            "candidate_stage": "QUALIFIED",
            "breakout_ready": True,
            "structure_ready": False,
            "scalp_ready": False,
            "hybrid_breakout_qualified": True,
        },
        True,
        "BREAKOUT"
    )

    scenario(
        "QUALIFIED STRUCTURE HANDOVER",
        {
            "qualified": True,
            "active_mode": "STRUCTURE",
            "direction": "SHORT",
            "candidate_mode": "STRUCTURE",
            "candidate_stage": "QUALIFIED",
            "breakout_ready": False,
            "structure_ready": True,
            "scalp_ready": False,
            "hybrid_structure_qualified": True,
        },
        True,
        "STRUCTURE"
    )

    scenario(
        "SCALP BLOCKED BY DEVELOPING MODE",
        {
            "qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_mode": "SCALP",
            "candidate_stage": "PENDING_UNIT_6",
            "breakout_ready": False,
            "structure_ready": False,
            "scalp_ready": True,
            "higher_mode_developing": True,
        },
        False,
        "NONE"
    )

    # Validate the unmodified live candidate last.

    live_result = fresh_reconstruction_unit_6(
        config,
        analysis,
        original
    )

    live_pass = (
        isinstance(
            live_result["execution_intent"], bool
        )
        and live_result["exchange_write"] is False
        and live_result["order_payload_created"]
        is False
    )

    tests.append((
        "ACTUAL UNIT 5 V8 HANDOVER",
        live_pass
    ))

    passed_count = sum(
        success for _, success in tests
    )

    for name, passed in tests:

        print(
            "UNIT 6 TEST:",
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True
        )

    failed_count = len(tests) - passed_count

    print(
        "UNIT 6 TESTS PASSED =",
        passed_count,
        flush=True
    )
    print(
        "UNIT 6 TESTS FAILED =",
        failed_count,
        flush=True
    )

    if failed_count:
        raise RuntimeError(
            "UNIT 6 V9 VALIDATION FAILED"
        )

    print(
        "UNIT 6 VALIDATION V9 RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# 6.4 SINGLE EXECUTION SEQUENCE
# ============================================================

FRESH_UNIT_6_VALIDATION_READY = (
    unit_6_validation_v9()
)

FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)


# ============================================================
# END COMPLETE UNIT 6 V9 REPLACEMENT
# UNIT 7 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 7 V10
# WEEX DEMO DYNAMIC SIZING POLICY
# UNIT 2 V9 -> UNIT 6 V9 -> UNIT 7 V10 -> UNIT 8
#
# E0: ADJUSTABLE FIXED USDT
# B1-B5: 0.5% OF FRESH AVAILABLE BALANCE
# TRIGGER: 0.3% BEFORE FRESH WEEX LIQUIDATION PRICE
# EXPOSURE: 35% DEFAULT, MAXIMUM 100%
# NO BACKUP MULTIPLIERS
# NO EXCHANGE WRITE IN UNIT 7
# ============================================================

import copy
from decimal import Decimal, InvalidOperation


# ============================================================
# UNIT 7 DECIMAL VALIDATION
# ============================================================

def unit_7_v10_decimal(value, name, allow_zero=False):

    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 7 INVALID BOOLEAN: " + name
        )

    try:
        number = Decimal(str(value))

    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "UNIT 7 INVALID NUMBER: " + name
        ) from exc

    if not number.is_finite():
        raise RuntimeError(
            "UNIT 7 NONFINITE NUMBER: " + name
        )

    if number < 0:
        raise RuntimeError(
            "UNIT 7 NEGATIVE NUMBER: " + name
        )

    if number == 0 and not allow_zero:
        raise RuntimeError(
            "UNIT 7 ZERO NOT ALLOWED: " + name
        )

    return number


# ============================================================
# UNIT 7 DYNAMIC BACKUP MARGIN FORMULA
# REQUIRES FRESH AVAILABLE BALANCE FROM WEEX
# DOES NOT SUBMIT ORDERS
# ============================================================

def unit_7_v10_backup_margin(
    available_balance,
    backup_percent
):

    balance = unit_7_v10_decimal(
        available_balance,
        "AVAILABLE TRADING BALANCE",
        allow_zero=True
    )

    percent = unit_7_v10_decimal(
        backup_percent,
        "BACKUP MARGIN PERCENT"
    )

    if percent > Decimal("100"):
        raise RuntimeError(
            "UNIT 7 BACKUP PERCENT ABOVE 100"
        )

    return (
        balance * percent / Decimal("100")
    )


# ============================================================
# UNIT 7 BACKUP TRIGGER FORMULA
# REQUIRES FRESH WEEX LIQUIDATION PRICE
# DOES NOT SUBMIT ORDERS
# ============================================================

def unit_7_v10_backup_trigger(
    liquidation_price,
    direction,
    buffer_percent
):

    liquidation = unit_7_v10_decimal(
        liquidation_price,
        "WEEX LIQUIDATION PRICE"
    )

    buffer_pct = unit_7_v10_decimal(
        buffer_percent,
        "LIQUIDATION BUFFER PERCENT"
    )

    if buffer_pct >= Decimal("100"):
        raise RuntimeError(
            "UNIT 7 LIQUIDATION BUFFER INVALID"
        )

    buffer = buffer_pct / Decimal("100")

    if direction == "LONG":
        return liquidation * (
            Decimal("1") + buffer
        )

    if direction == "SHORT":
        return liquidation * (
            Decimal("1") - buffer
        )

    raise RuntimeError(
        "UNIT 7 INVALID BACKUP DIRECTION"
    )


# ============================================================
# UNIT 7 TOTAL MARGIN CAP FORMULA
# INCLUDES INITIAL + FILLED BACKUPS + RESERVED MARGIN
# REQUIRES VERIFIED ACCOUNT VALUES
# ============================================================

def unit_7_v10_remaining_margin_capacity(
    account_equity,
    committed_margin,
    reserved_margin,
    exposure_cap_percent
):

    equity = unit_7_v10_decimal(
        account_equity,
        "TRADING ACCOUNT EQUITY"
    )

    committed = unit_7_v10_decimal(
        committed_margin,
        "ALREADY COMMITTED MARGIN",
        allow_zero=True
    )

    reserved = unit_7_v10_decimal(
        reserved_margin,
        "OUTSTANDING RESERVED MARGIN",
        allow_zero=True
    )

    cap_pct = unit_7_v10_decimal(
        exposure_cap_percent,
        "EXPOSURE CAP PERCENT"
    )

    if cap_pct > Decimal("100"):
        raise RuntimeError(
            "UNIT 7 EXPOSURE CAP ABOVE 100"
        )

    maximum_margin = (
        equity * cap_pct / Decimal("100")
    )

    remaining = (
        maximum_margin - committed - reserved
    )

    return max(
        Decimal("0"),
        remaining
    )


# ============================================================
# UNIT 7 MAIN DYNAMIC POLICY HANDOVER
# ============================================================

def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate
):

    print("=" * 80, flush=True)
    print(
        "UNIT 7 V10 DYNAMIC SIZING START",
        flush=True
    )

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 UNIT 2 CONFIG MISSING"
        )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 UNIT 6 CANDIDATE MISSING"
        )

    config = unit_2_config
    signal = unit_6_candidate

    strategy = config.get("strategy")
    exchange = config.get("exchange")
    precision = config.get("market_precision")
    safety = config.get("safety")

    for name, section in (
        ("STRATEGY", strategy),
        ("EXCHANGE", exchange),
        ("PRECISION", precision),
        ("SAFETY", safety),
    ):
        if not isinstance(section, dict):
            raise RuntimeError(
                "UNIT 7 MISSING CONFIG SECTION: " + name
            )

    # ========================================================
    # EXCHANGE CONTRACT
    # ========================================================

    if config.get("execution_environment") != "DEMO":
        raise RuntimeError(
            "UNIT 7 NON-DEMO ENVIRONMENT"
        )

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 7 EXCHANGE IS NOT WEEX"
        )

    if exchange.get("market_symbol") != "BTCUSDT":
        raise RuntimeError(
            "UNIT 7 MARKET SYMBOL INVALID"
        )

    if exchange.get("demo_order_symbol") != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 7 DEMO SYMBOL INVALID"
        )

    # ========================================================
    # UPSTREAM UNIT 6 CONTRACT
    # ========================================================

    required_signal_fields = (
        "execution_intent",
        "signal_qualified",
        "active_mode",
        "direction",
        "admission_reason",
    )

    for key in required_signal_fields:
        if key not in signal:
            raise RuntimeError(
                "UNIT 7 MISSING UNIT 6 FIELD: " + key
            )

    if signal.get("classification_version") != (
        "UNIT6_V9_ADJUSTABLE"
    ):
        raise RuntimeError(
            "UNIT 7 REQUIRES UNIT 6 V9 HANDOVER"
        )

    intent = signal["execution_intent"]
    qualified = signal["signal_qualified"]

    mode = signal["active_mode"]
    direction = signal["direction"]
    admission = signal["admission_reason"]

    if (
        type(intent) is not bool
        or type(qualified) is not bool
    ):
        raise RuntimeError(
            "UNIT 7 INVALID SIGNAL BOOLEAN"
        )

    if intent != qualified:
        raise RuntimeError(
            "UNIT 7 SIGNAL FLAGS MISMATCH"
        )

    if signal.get("exchange_write") is not False:
        raise RuntimeError(
            "UNIT 7 UPSTREAM EXCHANGE WRITE DETECTED"
        )

    if signal.get("order_payload_created") is not False:
        raise RuntimeError(
            "UNIT 7 UPSTREAM ORDER PAYLOAD DETECTED"
        )

    # ========================================================
    # TRADING SAFETY CONTRACT
    # ========================================================

    for key in (
        "anti_duplicate_orders",
        "one_direction_only",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 7 REQUIRED SAFETY MISSING: " + key
            )

    if safety.get(
        "real_order_submission_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 7 LIVE-CASH SAFETY FAILED"
        )

    if safety.get(
        "exchange_mutation_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 7 CONFIGURATION MUST BE READ-ONLY"
        )

    # ========================================================
    # E0 INITIAL ENTRY
    # ========================================================

    initial_margin = unit_7_v10_decimal(
        strategy.get("initial_fixed_usdt"),
        "E0 INITIAL USDT"
    )

    # E0 default comes from Unit 2.
    # It may be adjusted upward by its configuration.
    # No predefined E0 multiplier is used.

    # ========================================================
    # BACKUP POLICY
    # ========================================================

    backup_count = strategy.get("max_backups")

    if (
        type(backup_count) is not int
        or backup_count != 5
    ):
        raise RuntimeError(
            "UNIT 7 MAX BACKUPS MUST BE FIVE"
        )

    backup_percent = unit_7_v10_decimal(
        strategy.get("backup_margin_percent"),
        "BACKUP MARGIN PERCENT"
    )

    buffer_percent = unit_7_v10_decimal(
        strategy.get("backup_buffer_percent"),
        "BACKUP BUFFER PERCENT"
    )

    if backup_percent > Decimal("100"):
        raise RuntimeError(
            "UNIT 7 BACKUP PERCENT TOO HIGH"
        )

    if buffer_percent >= Decimal("100"):
        raise RuntimeError(
            "UNIT 7 BUFFER PERCENT TOO HIGH"
        )

    if "backup_multipliers" in strategy:
        raise RuntimeError(
            "UNIT 7 OBSOLETE BACKUP MULTIPLIERS"
        )

    if strategy.get("backup_sizing_mode") != (
        "PERCENT_AVAILABLE_BALANCE"
    ):
        raise RuntimeError(
            "UNIT 7 BACKUP SIZING MODE INVALID"
        )

    if strategy.get(
        "backup_trigger_reference"
    ) != "FRESH_WEEX_LIQUIDATION_PRICE":
        raise RuntimeError(
            "UNIT 7 BACKUP TRIGGER SOURCE INVALID"
        )

    if strategy.get(
        "backup_trigger_recalculation"
    ) != "AFTER_PRECEDING_CONFIRMED_FILL":
        raise RuntimeError(
            "UNIT 7 BACKUP RECALCULATION INVALID"
        )

    if strategy.get(
        "progressive_backup_funding"
    ) is not True:
        raise RuntimeError(
            "UNIT 7 PROGRESSIVE FUNDING REQUIRED"
        )

    if strategy.get(
        "full_ladder_reservation_required"
    ) is not False:
        raise RuntimeError(
            "UNIT 7 FULL LADDER RESERVATION FORBIDDEN"
        )

    # ========================================================
    # EXPOSURE CAP
    # ========================================================

    exposure_cap = unit_7_v10_decimal(
        strategy.get("exposure_cap_percent"),
        "CURRENT EXPOSURE CAP"
    )

    exposure_max = unit_7_v10_decimal(
        strategy.get("exposure_cap_max_percent"),
        "MAX EXPOSURE CAP"
    )

    if (
        exposure_cap > exposure_max
        or exposure_max > Decimal("100")
    ):
        raise RuntimeError(
            "UNIT 7 EXPOSURE LIMIT INVALID"
        )

    if strategy.get("exposure_cap_basis") != (
        "TRADING_ACCOUNT_EQUITY"
    ):
        raise RuntimeError(
            "UNIT 7 EXPOSURE EQUITY BASIS INVALID"
        )

    for key in (
        "exposure_includes_initial",
        "exposure_includes_filled_backups",
        "exposure_includes_pending_margin",
    ):
        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 7 EXPOSURE POLICY INVALID: " + key
            )

    # ========================================================
    # MARKET PRECISION
    # ========================================================

    qty_step = unit_7_v10_decimal(
        precision.get("quantity_step"),
        "QUANTITY STEP"
    )

    min_qty = unit_7_v10_decimal(
        precision.get("minimum_quantity"),
        "MINIMUM QUANTITY"
    )

    price_step = unit_7_v10_decimal(
        precision.get("price_step"),
        "PRICE STEP"
    )

    if min_qty % qty_step != 0:
        raise RuntimeError(
            "UNIT 7 QUANTITY PRECISION INVALID"
        )

    # ========================================================
    # VERIFY BUFFER FACTORS
    # ========================================================

    long_factor = (
        Decimal("1")
        + buffer_percent / Decimal("100")
    )

    short_factor = (
        Decimal("1")
        - buffer_percent / Decimal("100")
    )

    configured_long = unit_7_v10_decimal(
        strategy.get(
            "backup_long_liquidation_factor"
        ),
        "LONG BUFFER FACTOR"
    )

    configured_short = unit_7_v10_decimal(
        strategy.get(
            "backup_short_liquidation_factor"
        ),
        "SHORT BUFFER FACTOR"
    )

    tolerance = Decimal("0.000000001")

    if abs(long_factor - configured_long) > tolerance:
        raise RuntimeError(
            "UNIT 7 LONG BUFFER FACTOR MISMATCH"
        )

    if abs(short_factor - configured_short) > tolerance:
        raise RuntimeError(
            "UNIT 7 SHORT BUFFER FACTOR MISMATCH"
        )

    # ========================================================
    # OUTPUT FOR UNIT 8
    # ========================================================

    output = {
        "unit_7_version": "UNIT7_V10_DYNAMIC",

        "status": "IDLE",
        "skip_reason": admission,

        "active_mode": "NONE",
        "direction": "NONE",

        "execution_intent": False,
        "signal_qualified": False,

        "unit_5_reason": signal.get("unit_5_reason"),
        "admission_reason": admission,

        "candidate_stage": signal.get(
            "candidate_stage", "NONE"
        ),
        "candidate_age_seconds": signal.get(
            "candidate_age_seconds"
        ),

        "symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",

        "initial_fixed_usdt": float(initial_margin),

        "initial_margin_percent": float(
            unit_7_v10_decimal(
                strategy.get("initial_margin_percent"),
                "INITIAL MARGIN PERCENT"
            )
        ),

        "max_backups": backup_count,

        "backup_margin_percent": float(backup_percent),
        "backup_buffer_percent": float(buffer_percent),

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

        "backup_margin_usdt": None,
        "full_ladder_margin_usdt": None,

        "exposure_cap_percent": float(exposure_cap),
        "exposure_cap_max_percent": float(exposure_max),

        "exposure_cap_basis":
            "TRADING_ACCOUNT_EQUITY",

        "exposure_includes_initial": True,
        "exposure_includes_filled_backups": True,
        "exposure_includes_pending_margin": True,

        "progressive_backup_funding": True,
        "full_ladder_reservation_required": False,

        "quantity_step": float(qty_step),
        "minimum_quantity": float(min_qty),
        "price_step": float(price_step),

        "leverage_target": None,
        "leverage_source": "WEEX_EXCHANGE_SETTING",
        "exchange_leverage_verified": False,

        "account_balance_required": False,

        "position_sizing_performed": False,
        "quantity_calculated": False,
        "proposed_quantity": None,

        "backup_margin_calculated": False,
        "backup_trigger_calculated": False,

        "trade_authorized": False,
        "order_payload_created": False,
        "exchange_write": False,
        "read_only": True,

        "source_unit_6": "UNIT6_V9_ADJUSTABLE",
    }

    # ========================================================
    # IDLE HANDOVER
    # ========================================================

    if intent is False:

        if mode != "NONE" or direction != "NONE":
            raise RuntimeError(
                "UNIT 7 INVALID IDLE MODE OR DIRECTION"
            )

        print(
            "UNIT 7 STATUS = IDLE",
            flush=True
        )

        print(
            "UNIT 7 SKIP REASON =",
            admission,
            flush=True
        )

        print(
            "UNIT 7 EXECUTION INTENT = False",
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

        return output

    # ========================================================
    # QUALIFIED HANDOVER
    # ========================================================

    approved_admissions = {
        "BREAKOUT":
            "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS",

        "STRUCTURE":
            "STRUCTURE_QUALIFIED_FOR_NEXT_UNITS",

        "SCALP":
            "SCALP_QUALIFIED_FOR_NEXT_UNITS",
    }

    if mode not in approved_admissions:
        raise RuntimeError(
            "UNIT 7 INVALID QUALIFIED MODE"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 7 INVALID QUALIFIED DIRECTION"
        )

    if admission != approved_admissions[mode]:
        raise RuntimeError(
            "UNIT 7 QUALIFICATION REASON MISMATCH"
        )

    if signal.get("candidate_stage") == "DEVELOPING":
        raise RuntimeError(
            "UNIT 7 DEVELOPING SIGNAL CANNOT EXECUTE"
        )

    if (
        mode == "SCALP"
        and signal.get("higher_mode_developing") is True
    ):
        raise RuntimeError(
            "UNIT 7 SCALP BLOCKED BY HIGHER MODE"
        )

    output.update({
        "status": "READY_FOR_BALANCE",
        "skip_reason": None,

        "active_mode": mode,
        "direction": direction,

        "execution_intent": True,
        "signal_qualified": True,

        "account_balance_required": True,
    })

    print(
        "UNIT 7 STATUS = READY_FOR_BALANCE",
        flush=True
    )

    print(
        "UNIT 7 ACTIVE MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 7 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 7 E0 INITIAL USDT =",
        initial_margin,
        flush=True
    )

    print(
        "UNIT 7 MAX BACKUPS =",
        backup_count,
        flush=True
    )

    print(
        "UNIT 7 BACKUP AVAILABLE BALANCE % =",
        backup_percent,
        flush=True
    )

    print(
        "UNIT 7 BACKUP BUFFER % =",
        buffer_percent,
        flush=True
    )

    print(
        "UNIT 7 BACKUP MULTIPLIERS = NONE",
        flush=True
    )

    print(
        "UNIT 7 LONG TRIGGER FACTOR =",
        long_factor,
        flush=True
    )

    print(
        "UNIT 7 SHORT TRIGGER FACTOR =",
        short_factor,
        flush=True
    )

    print(
        "UNIT 7 EXPOSURE CAP % =",
        exposure_cap,
        flush=True
    )

    print(
        "UNIT 7 EXPOSURE MAX % =",
        exposure_max,
        flush=True
    )

    print(
        "UNIT 7 BACKUP AMOUNTS = DEFERRED",
        flush=True
    )

    print(
        "UNIT 7 LEVERAGE = DEFERRED TO WEEX",
        flush=True
    )

    print(
        "UNIT 7 QUANTITY CALCULATED = FALSE",
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

    return output


# ============================================================
# UNIT 7 V10 COMPLETE VALIDATION
# ============================================================

def unit_7_validation_v10():

    print("=" * 80, flush=True)
    print(
        "UNIT 7 VALIDATION V10 START",
        flush=True
    )

    config = copy.deepcopy(
        FRESH_RECONSTRUCTION_CONFIG
    )

    base = copy.deepcopy(
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    )

    tests = []

    def check(name, changes, expected_status):

        candidate = copy.deepcopy(base)
        candidate.update(changes)

        try:
            result = fresh_reconstruction_unit_7(
                config,
                candidate
            )

            strategy = config["strategy"]

            passed = (
                result["status"] == expected_status
                and result["max_backups"] == 5
                and result["backup_margin_percent"]
                    == strategy["backup_margin_percent"]
                and result["full_ladder_margin_usdt"] is None
                and "backup_multipliers" not in result
                and result["order_payload_created"] is False
                and result["quantity_calculated"] is False
                and result["exchange_write"] is False
                and result["exposure_cap_percent"]
                    <= result["exposure_cap_max_percent"]
                    <= 100.0
            )

        except Exception as exc:

            print(
                "UNIT 7 TEST ERROR =",
                name,
                repr(exc),
                flush=True
            )

            passed = False

        tests.append((name, passed))

    # --------------------------------------------------------
    # TEST 1: NORMAL IDLE
    # --------------------------------------------------------

    check(
        "NORMAL IDLE",
        {
            "execution_intent": False,
            "signal_qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_stage": "NONE",
            "admission_reason": "NO_ACCEPTABLE_CANDIDATE",
        },
        "IDLE"
    )

    # --------------------------------------------------------
    # TEST 2: STRUCTURE LONG
    # --------------------------------------------------------

    check(
        "QUALIFIED STRUCTURE LONG",
        {
            "execution_intent": True,
            "signal_qualified": True,
            "active_mode": "STRUCTURE",
            "direction": "LONG",
            "candidate_stage": "QUALIFIED",
            "admission_reason":
                "STRUCTURE_QUALIFIED_FOR_NEXT_UNITS",
        },
        "READY_FOR_BALANCE"
    )

    # --------------------------------------------------------
    # TEST 3: BREAKOUT SHORT
    # --------------------------------------------------------

    check(
        "QUALIFIED BREAKOUT SHORT",
        {
            "execution_intent": True,
            "signal_qualified": True,
            "active_mode": "BREAKOUT",
            "direction": "SHORT",
            "candidate_stage": "QUALIFIED",
            "admission_reason":
                "BREAKOUT_QUALIFIED_FOR_NEXT_UNITS",
        },
        "READY_FOR_BALANCE"
    )

    # --------------------------------------------------------
    # TEST 4: SCALP LONG
    # --------------------------------------------------------

    check(
        "QUALIFIED SCALP LONG",
        {
            "execution_intent": True,
            "signal_qualified": True,
            "active_mode": "SCALP",
            "direction": "LONG",
            "candidate_stage": "PENDING_UNIT_6",
            "higher_mode_developing": False,
            "admission_reason":
                "SCALP_QUALIFIED_FOR_NEXT_UNITS",
        },
        "READY_FOR_BALANCE"
    )

    # --------------------------------------------------------
    # TEST 5: DEVELOPING STRUCTURE
    # --------------------------------------------------------

    check(
        "DEVELOPING STRUCTURE IDLE",
        {
            "execution_intent": False,
            "signal_qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_stage": "DEVELOPING",
            "admission_reason":
                "DEVELOPING_HIGHER_MODE_PROTECTED",
        },
        "IDLE"
    )

    # --------------------------------------------------------
    # TEST 6: DEVELOPING BREAKOUT
    # --------------------------------------------------------

    check(
        "DEVELOPING BREAKOUT IDLE",
        {
            "execution_intent": False,
            "signal_qualified": False,
            "active_mode": "NONE",
            "direction": "NONE",
            "candidate_stage": "DEVELOPING",
            "admission_reason":
                "DEVELOPING_HIGHER_MODE_PROTECTED",
        },
        "IDLE"
    )

    # --------------------------------------------------------
    # TEST 7: ACTUAL UNIT 6 HANDOVER
    # --------------------------------------------------------

    check(
        "ACTUAL UNIT 6 V9 HANDOVER",
        {},
        (
            "READY_FOR_BALANCE"
            if base.get("execution_intent") is True
            else "IDLE"
        )
    )

    # --------------------------------------------------------
    # TEST 8: DYNAMIC BACKUP MARGIN
    # --------------------------------------------------------

    try:
        percentage = config["strategy"][
            "backup_margin_percent"
        ]

        amount = unit_7_v10_backup_margin(
            Decimal("100"),
            percentage
        )

        expected_amount = (
            Decimal("100")
            * Decimal(str(percentage))
            / Decimal("100")
        )

        margin_pass = amount == expected_amount

    except Exception:
        margin_pass = False

    tests.append((
        "DYNAMIC BACKUP AVAILABLE BALANCE",
        margin_pass
    ))

    # --------------------------------------------------------
    # TEST 9: LONG/SHORT BACKUP TRIGGERS
    # --------------------------------------------------------

    try:
        buffer = config["strategy"][
            "backup_buffer_percent"
        ]

        long_trigger = unit_7_v10_backup_trigger(
            Decimal("80000"),
            "LONG",
            buffer
        )

        short_trigger = unit_7_v10_backup_trigger(
            Decimal("80000"),
            "SHORT",
            buffer
        )

        fraction = Decimal(
            str(buffer)
        ) / Decimal("100")

        trigger_pass = (
            long_trigger
                == Decimal("80000")
                * (Decimal("1") + fraction)
            and short_trigger
                == Decimal("80000")
                * (Decimal("1") - fraction)
        )

    except Exception:
        trigger_pass = False

    tests.append((
        "FRESH LIQUIDATION TRIGGER FORMULAS",
        trigger_pass
    ))

    # --------------------------------------------------------
    # TEST 10: ADJUSTABLE 100% CAP
    # --------------------------------------------------------

    try:
        modified_config = copy.deepcopy(config)

        modified_config["strategy"][
            "exposure_cap_percent"
        ] = 100.0

        result = fresh_reconstruction_unit_7(
            modified_config,
            base
        )

        remaining = (
            unit_7_v10_remaining_margin_capacity(
                Decimal("100"),
                Decimal("34.7"),
                Decimal("0"),
                Decimal("35")
            )
        )

        cap_pass = (
            result["exposure_cap_percent"] == 100.0
            and remaining == Decimal("0.3")
            and result["exchange_write"] is False
        )

    except Exception as exc:

        print(
            "UNIT 7 CAP TEST ERROR =",
            repr(exc),
            flush=True
        )

        cap_pass = False

    tests.append((
        "ADJUSTABLE EXPOSURE CAP",
        cap_pass
    ))

    # ========================================================
    # FINAL VALIDATION SUMMARY
    # ========================================================

    passed_count = sum(
        1 for _, passed in tests if passed
    )

    failed_count = len(tests) - passed_count

    for name, passed in tests:

        print(
            "UNIT 7 TEST:",
            name,
            "=",
            "PASS" if passed else "FAIL",
            flush=True
        )

    print(
        "UNIT 7 TESTS PASSED =",
        passed_count,
        flush=True
    )

    print(
        "UNIT 7 TESTS FAILED =",
        failed_count,
        flush=True
    )

    if failed_count:
        raise RuntimeError(
            "UNIT 7 V10 VALIDATION FAILED"
        )

    print(
        "UNIT 7 VALIDATION V10 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# UNIT 7 V10 EXECUTION
# KEEP THESE CALLS AFTER ALL UNIT 7 FUNCTION DEFINITIONS
# ============================================================

FRESH_UNIT_7_VALIDATION_READY = (
    unit_7_validation_v10()
)

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 7 V10 READY =",
    FRESH_UNIT_7_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 7 V10
# UNIT 8 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 8 V6
# WEEX DEMO + RENDER MANUAL LEVERAGE
# UNIT 7 V10 COMPATIBLE
# ZERO INDENTATION
#
# AUTHENTICATED DEMO GET REQUESTS ONLY
# NO LEVERAGE API REQUIRED
# NO LEVERAGE MUTATION
# NO ORDER SUBMISSION
# ============================================================

import os
import json
import time
import hmac
import hashlib
import base64
import urllib.request
import urllib.error

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_FLOOR,
    ROUND_CEILING,
)
from urllib.parse import urlencode


# ============================================================
# UNIT 8 NUMERIC VALIDATION
# ============================================================

def unit_8_v6_decimal(
    value,
    name,
    allow_zero=False,
):
    if isinstance(value, bool):
        raise RuntimeError(
            "UNIT 8 INVALID BOOLEAN: " + name
        )

    try:
        result = Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ) as exc:
        raise RuntimeError(
            "UNIT 8 INVALID NUMBER: " + name
        ) from exc

    if not result.is_finite():
        raise RuntimeError(
            "UNIT 8 NONFINITE NUMBER: " + name
        )

    if result < 0:
        raise RuntimeError(
            "UNIT 8 NEGATIVE NUMBER: " + name
        )

    if result == 0 and not allow_zero:
        raise RuntimeError(
            "UNIT 8 ZERO NOT ALLOWED: " + name
        )

    return result


# ============================================================
# UNIT 8 SIGNED WEEX DEMO GET
# ALLOWED ENDPOINTS ONLY
# ============================================================

def unit_8_v6_signed_get(path, params=None):

    allowed = {
        "/capi/v3/sim/balance",
        "/capi/v3/sim/position/allPosition",
    }

    if path not in allowed:
        raise RuntimeError(
            "UNIT 8 NON-DEMO ENDPOINT REJECTED"
        )

    key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, passphrase)):
        raise RuntimeError(
            "UNIT 8 API CREDENTIALS MISSING"
        )

    query = urlencode(params or {})

    target = path + (
        "?" + query if query else ""
    )

    timestamp = str(int(time.time() * 1000))

    message = timestamp + "GET" + target

    signature = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    request = urllib.request.Request(
        url=(
            "https://api-contract.weex.com"
            + target
        ),
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": "en-US",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=12,
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            "UNIT 8 WEEX HTTP " + str(exc.code)
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            "UNIT 8 WEEX REQUEST FAILED: "
            + type(exc).__name__
        ) from exc

    if isinstance(payload, dict):
        code = payload.get("code")

        if code is not None and str(code) not in (
            "0",
            "200",
            "00000",
        ):
            raise RuntimeError(
                "UNIT 8 WEEX API CODE: " + str(code)
            )

        if "data" in payload:
            return payload["data"]

    return payload


# ============================================================
# UNIT 8 RENDER LEVERAGE
# ALWAYS READ BOTH, INCLUDING FLAT POSITION
# ============================================================

def unit_8_v6_render_leverage():

    def read(name):
        raw = os.environ.get(name)

        if not raw or not raw.strip():
            raise RuntimeError(
                "UNIT 8 MISSING RENDER VARIABLE: "
                + name
            )

        leverage = unit_8_v6_decimal(
            raw.strip(),
            name,
        )

        if leverage > Decimal("200"):
            raise RuntimeError(
                "UNIT 8 LEVERAGE OUTSIDE LOCAL LIMIT"
            )

        return leverage

    return (
        read("WEEX_DEMO_LONG_LEVERAGE"),
        read("WEEX_DEMO_SHORT_LEVERAGE"),
    )


# ============================================================
# UNIT 8 MINIMUM QUANTITY CALCULATION
# NO SILENT INCREASE OF ENTRY MARGIN
# ============================================================

def unit_8_v6_quantity(
    margin,
    leverage,
    price,
    quantity_step,
    minimum_quantity,
):

    margin = unit_8_v6_decimal(
        margin, "MARGIN"
    )

    leverage = unit_8_v6_decimal(
        leverage, "LEVERAGE"
    )

    price = unit_8_v6_decimal(
        price, "MARK PRICE"
    )

    step = unit_8_v6_decimal(
        quantity_step, "QUANTITY STEP"
    )

    minimum = unit_8_v6_decimal(
        minimum_quantity, "MINIMUM QUANTITY"
    )

    raw_quantity = (
        margin * leverage / price
    )

    steps = (
        raw_quantity / step
    ).to_integral_value(
        rounding=ROUND_FLOOR
    )

    normalized = steps * step

    minimum_steps = (
        minimum / step
    ).to_integral_value(
        rounding=ROUND_CEILING
    )

    executable_minimum = (
        minimum_steps * step
    )

    required_margin = (
        executable_minimum * price / leverage
    )

    return {
        "raw_quantity": raw_quantity,
        "quantity": normalized,
        "minimum_quantity": executable_minimum,
        "minimum_margin_required": required_margin,
        "minimum_quantity_pass": (
            normalized >= executable_minimum
        ),
    }


# ============================================================
# UNIT 8 MAIN
# ============================================================

def fresh_reconstruction_unit_8(
    config,
    unit_7_result,
    market_snapshot=None,
):

    print("=" * 80, flush=True)
    print(
        "UNIT 8 V6 RENDER LEVERAGE START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 8 CONFIG INVALID"
        )

    if not isinstance(unit_7_result, dict):
        raise RuntimeError(
            "UNIT 8 UNIT 7 RESULT INVALID"
        )

    if unit_7_result.get(
        "unit_7_version"
    ) != "UNIT7_V10_DYNAMIC":
        raise RuntimeError(
            "UNIT 8 REQUIRES UNIT 7 V10"
        )

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    safety = config.get("safety", {})

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 8 DEMO ONLY"
        )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("market_symbol")
            != "BTCUSDT"
        or exchange.get("demo_order_symbol")
            != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 8 SYMBOL CONTRACT INVALID"
        )

    if (
        unit_7_result.get("max_backups") != 5
        or "backup_multipliers" in strategy
    ):
        raise RuntimeError(
            "UNIT 8 BACKUP POLICY MISMATCH"
        )

    if (
        unit_7_result.get("exchange_write")
            is not False
        or unit_7_result.get(
            "order_payload_created"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 8 UNIT 7 WRITE SAFETY FAILED"
        )

    if safety.get(
        "real_order_submission_enabled"
    ) is not False:
        raise RuntimeError(
            "UNIT 8 REAL CASH DISABLED REQUIRED"
        )

    # ========================================================
    # 1. LEVERAGE ALWAYS READ FIRST
    # ========================================================

    leverage_error = None
    long_leverage = None
    short_leverage = None

    try:
        (
            long_leverage,
            short_leverage,
        ) = unit_8_v6_render_leverage()

        print(
            "UNIT 8 RENDER LONG LEVERAGE =",
            long_leverage,
            flush=True
        )

        print(
            "UNIT 8 RENDER SHORT LEVERAGE =",
            short_leverage,
            flush=True
        )

    except Exception as exc:
        leverage_error = str(exc)

        print(
            "UNIT 8 LEVERAGE CONFIG ERROR =",
            leverage_error,
            flush=True
        )

    # ========================================================
    # 2. PRESERVE UNIT 9 NINE-FIELD CONTRACT
    # ========================================================

    mode = unit_7_result.get(
        "active_mode", "NONE"
    )

    direction = unit_7_result.get(
        "direction", "NONE"
    )

    qualified = (
        unit_7_result.get("signal_qualified")
        is True
    )

    intent = (
        unit_7_result.get("execution_intent")
        is True
    )

    output = {
        "status": "IDLE",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": qualified,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "skip_reason": "NONE",
        "read_only": True,

        "unit_8_version":
            "UNIT8_V6_RENDER_LEVERAGE",

        "demo_symbol": "BTCSUSDT",

        "weex_demo_long_leverage": (
            float(long_leverage)
            if long_leverage is not None
            else None
        ),

        "weex_demo_short_leverage": (
            float(short_leverage)
            if short_leverage is not None
            else None
        ),

        "long_leverage": (
            str(long_leverage)
            if long_leverage is not None
            else None
        ),

        "short_leverage": (
            str(short_leverage)
            if short_leverage is not None
            else None
        ),

        "selected_leverage": None,

        "leverage_source":
            "RENDER_MANUAL_WEEX_DEMO",

        "leverage_configured": (
            leverage_error is None
        ),

        "exchange_leverage_verified": False,
        "demo_leverage_verified": False,

        "demo_balance_verified": False,
        "demo_positions_verified": False,
        "position_flat_verified": False,

        "available_balance": None,
        "account_equity": None,
        "account_equity_source": None,

        "positions": [],
        "quantity_calculated": False,
        "execution_quantity": None,

        "max_backups": 5,
        "backup_margin_percent":
            unit_7_result.get(
                "backup_margin_percent"
            ),
        "backup_buffer_percent":
            unit_7_result.get(
                "backup_buffer_percent"
            ),
        "exposure_cap_percent":
            unit_7_result.get(
                "exposure_cap_percent"
            ),

        "order_payload_created": False,
        "exchange_write": False,
    }

    def finish(status, reason):

        output["status"] = status
        output["skip_reason"] = reason

        print(
            "UNIT 8 STATUS =",
            status,
            flush=True
        )

        print(
            "UNIT 8 REASON =",
            reason,
            flush=True
        )

        print(
            "UNIT 8 TRADE PLAN READY =",
            output["trade_plan_ready"],
            flush=True
        )

        print(
            "UNIT 8 EXCHANGE WRITE = NONE",
            flush=True
        )

        print("=" * 80, flush=True)

        return output

    # ========================================================
    # 3. READ DEMO BALANCE EVEN DURING IDLE
    # ========================================================

    try:
        balances = unit_8_v6_signed_get(
            "/capi/v3/sim/balance"
        )

        if isinstance(balances, dict):
            balances = [balances]

        if not isinstance(balances, list):
            raise RuntimeError(
                "INVALID DEMO BALANCE FORMAT"
            )

        asset = next(
            (
                record
                for record in balances
                if isinstance(record, dict)
                and str(
                    record.get("asset", "")
                ).upper() == "SUSDT"
            ),
            None
        )

        if asset is None:
            raise RuntimeError(
                "SUSDT ASSET NOT FOUND"
            )

        available = unit_8_v6_decimal(
            asset.get("availableBalance"),
            "AVAILABLE SUSDT",
            allow_zero=True
        )

        output["available_balance"] = str(
            available
        )

        output["demo_balance_verified"] = True

        # Equity is used only if the exchange supplied
        # values required for a reliable calculation.
        if (
            asset.get("equity") is not None
        ):
            equity = unit_8_v6_decimal(
                asset["equity"],
                "DEMO EQUITY",
                allow_zero=True
            )

            output["account_equity"] = str(equity)
            output["account_equity_source"] = (
                "WEEX_REPORTED_EQUITY"
            )

        elif (
            asset.get("balance") is not None
            and asset.get("unrealizePnl")
                is not None
        ):
            balance = unit_8_v6_decimal(
                asset["balance"],
                "BALANCE",
                allow_zero=True
            )

            pnl = Decimal(
                str(asset["unrealizePnl"])
            )

            if not pnl.is_finite():
                raise RuntimeError(
                    "INVALID UNREALIZED PNL"
                )

            equity = balance + pnl

            if equity < 0:
                raise RuntimeError(
                    "NEGATIVE EQUITY"
                )

            output["account_equity"] = str(equity)
            output["account_equity_source"] = (
                "PROVISIONAL_BALANCE_PLUS_PNL"
            )

        print(
            "UNIT 8 DEMO BALANCE VERIFIED = True",
            flush=True
        )

        print(
            "UNIT 8 AVAILABLE SUSDT =",
            available,
            flush=True
        )

    except Exception as exc:

        print(
            "UNIT 8 DEMO BALANCE ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "DEMO_BALANCE_UNVERIFIED"
        )

    # ========================================================
    # 4. READ DEMO POSITIONS EVEN DURING IDLE
    # ========================================================

    try:
        positions = unit_8_v6_signed_get(
            "/capi/v3/sim/position/allPosition"
        )

        if isinstance(positions, dict):
            positions = [positions]

        if not isinstance(positions, list):
            raise RuntimeError(
                "INVALID DEMO POSITIONS FORMAT"
            )

        open_positions = []

        for position in positions:

            if not isinstance(position, dict):
                continue

            if position.get("symbol") not in (
                "BTCSUSDT",
                "BTCUSDT"
            ):
                continue

            size = unit_8_v6_decimal(
                position.get("size", "0"),
                "POSITION SIZE",
                allow_zero=True
            )

            if size > 0:
                open_positions.append(position)

        output["positions"] = open_positions
        output["demo_positions_verified"] = True

        output["position_flat_verified"] = (
            len(open_positions) == 0
        )

        print(
            "UNIT 8 OPEN DEMO POSITIONS =",
            len(open_positions),
            flush=True
        )

        print(
            "UNIT 8 POSITION FLAT =",
            output["position_flat_verified"],
            flush=True
        )

    except Exception as exc:

        print(
            "UNIT 8 DEMO POSITION ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "DEMO_POSITIONS_UNVERIFIED"
        )

    # ========================================================
    # 5. BLOCK INVALID LEVERAGE CONFIGURATION
    # ========================================================

    if leverage_error is not None:
        return finish(
            "BLOCKED",
            "RENDER_DEMO_LEVERAGE_MISSING_OR_INVALID"
        )

    # ========================================================
    # 6. INDEPENDENT OPEN POSITION SAFETY
    # ========================================================

    if not output["position_flat_verified"]:
        return finish(
            "IDLE",
            "EXISTING_DEMO_POSITION"
        )

    # ========================================================
    # 7. NO QUALIFIED SIGNAL
    # ========================================================

    if not intent:
        return finish(
            "IDLE",
            unit_7_result.get("skip_reason")
            or "NO_QUALIFIED_SIGNAL"
        )

    if (
        not qualified
        or unit_7_result.get("status")
            != "READY_FOR_BALANCE"
    ):
        return finish(
            "BLOCKED",
            "UNIT_7_NOT_QUALIFIED"
        )

    if (
        mode not in (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        )
        or direction not in (
            "LONG",
            "SHORT",
        )
    ):
        return finish(
            "BLOCKED",
            "INVALID_TRADE_DIRECTION_OR_MODE"
        )

    # ========================================================
    # 8. SELECT RENDER LEVERAGE
    # ========================================================

    leverage = (
        long_leverage
        if direction == "LONG"
        else short_leverage
    )

    output["selected_leverage"] = float(
        leverage
    )

    # ========================================================
    # 9. MARKET SNAPSHOT
    # ========================================================

    if market_snapshot is None:
        market_snapshot = globals().get(
            "FRESH_RECONSTRUCTION_MARKET_SNAPSHOT"
        )

    if not isinstance(market_snapshot, dict):
        return finish(
            "BLOCKED",
            "MARKET_SNAPSHOT_MISSING"
        )

    if (
        market_snapshot.get("symbol")
        != "BTCUSDT"
    ):
        return finish(
            "BLOCKED",
            "MARKET_SYMBOL_MISMATCH"
        )

    try:
        price = unit_8_v6_decimal(
            market_snapshot.get("price"),
            "MARK PRICE"
        )

    except Exception:
        return finish(
            "BLOCKED",
            "INVALID_MARK_PRICE"
        )

    # ========================================================
    # 10. INITIAL ENTRY MARGIN
    # ========================================================

    raw_margin = os.getenv(
        "INITIAL_ENTRY_MARGIN_USDT"
    )

    if raw_margin is None or not raw_margin.strip():
        raw_margin = os.getenv(
            "ENTRY_FIXED_USDT"
        )

    if raw_margin is None or not raw_margin.strip():
        raw_margin = str(
            unit_7_result.get(
                "initial_fixed_usdt", "0.5"
            )
        )

    try:
        margin = unit_8_v6_decimal(
            raw_margin,
            "INITIAL ENTRY MARGIN"
        )

        available = unit_8_v6_decimal(
            output["available_balance"],
            "AVAILABLE BALANCE",
            allow_zero=True
        )

        cap = unit_8_v6_decimal(
            unit_7_result.get(
                "exposure_cap_percent"
            ),
            "EXPOSURE CAP"
        )

        if cap > Decimal("100"):
            raise RuntimeError(
                "EXPOSURE CAP TOO HIGH"
            )

    except Exception as exc:
        print(
            "UNIT 8 MARGIN CONFIG ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "INVALID_MARGIN_CONFIGURATION"
        )

    if margin > available:
        return finish(
            "BLOCKED",
            "INSUFFICIENT_DEMO_BALANCE"
        )

    if output["account_equity"] is None:
        return finish(
            "BLOCKED",
            "DEMO_EQUITY_UNVERIFIED"
        )

    equity = unit_8_v6_decimal(
        output["account_equity"],
        "ACCOUNT EQUITY",
        allow_zero=True
    )

    exposure_budget = (
        equity * cap / Decimal("100")
    )

    # Conservative preparation only.
    # Unit 9 must refresh actual committed and
    # reserved margin before authorizing submission.
    if margin > exposure_budget:
        return finish(
            "BLOCKED",
            "INITIAL_ENTRY_EXCEEDS_EXPOSURE_CAP"
        )

    # ========================================================
    # 11. STEP-AWARE BTC QUANTITY
    # ========================================================

    try:
        sizing = unit_8_v6_quantity(
            margin=margin,
            leverage=leverage,
            price=price,
            quantity_step=unit_7_result[
                "quantity_step"
            ],
            minimum_quantity=unit_7_result[
                "minimum_quantity"
            ],
        )

    except Exception as exc:
        print(
            "UNIT 8 SIZING ERROR =",
            str(exc),
            flush=True
        )

        return finish(
            "BLOCKED",
            "INVALID_QUANTITY_CALCULATION"
        )

    print(
        "UNIT 8 ENTRY MARGIN =",
        margin,
        flush=True
    )

    print(
        "UNIT 8 SELECTED LEVERAGE =",
        leverage,
        flush=True
    )

    print(
        "UNIT 8 RAW BTC QUANTITY =",
        sizing["raw_quantity"],
        flush=True
    )

    print(
        "UNIT 8 MINIMUM BTC QUANTITY =",
        sizing["minimum_quantity"],
        flush=True
    )

    print(
        "UNIT 8 MINIMUM REQUIRED MARGIN =",
        sizing["minimum_margin_required"],
        flush=True
    )

    if not sizing["minimum_quantity_pass"]:
        return finish(
            "BLOCKED",
            "QUANTITY_BELOW_EXCHANGE_MINIMUM"
        )

    quantity = sizing["quantity"]

    # Reject any accidental over-allocation
    # caused by contract rounding or conversions.
    required_margin = (
        quantity * price / leverage
    )

    if required_margin > margin:
        return finish(
            "BLOCKED",
            "NORMALIZED_ORDER_MARGIN_EXCEEDS_E0"
        )

    # ========================================================
    # 12. PRESERVE ORIGINAL POSITION SIZING CONTRACT
    # ========================================================

    position_sizing = {
        "asset": "SUSDT",
        "available_balance": float(available),

        "initial_margin_percent": float(
            unit_7_result.get(
                "initial_margin_percent"
            )
        ),

        "margin_allocation": float(margin),
        "leverage_target": float(leverage),
        "live_mark_price": float(price),

        "raw_quantity": float(
            sizing["raw_quantity"]
        ),

        "quantity_step": float(
            unit_7_result["quantity_step"]
        ),

        "minimum_quantity": float(
            sizing["minimum_quantity"]
        ),

        "quantity": float(quantity),

        "position_sizing_performed": True,
        "quantity_calculated": True,

        "source": "WEEX_V3_DEMO_BALANCE",
        "read_only": True,

        "leverage_source":
            "RENDER_MANUAL_WEEX_DEMO",

        "long_leverage": float(
            long_leverage
        ),

        "short_leverage": float(
            short_leverage
        ),

        "exchange_leverage_verified": False,

        "exposure_cap_percent": float(cap),
        "exposure_budget": float(exposure_budget),

        "max_backups": 5,

        "backup_margin_percent": float(
            unit_7_result[
                "backup_margin_percent"
            ]
        ),

        "backup_sizing_mode":
            "PERCENT_AVAILABLE_BALANCE",

        "backup_margin_reserved": False,
    }

    # ========================================================
    # 13. PRESERVE ORIGINAL UNIT 9 TRADE PLAN
    # ========================================================

    trade_plan = {
        "active_mode": mode,
        "direction": direction,
        "quantity": float(quantity),
        "position_sizing": position_sizing,
        "execution_environment": "DEMO",
    }

    output.update({
        "status": "READY",
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": trade_plan,
        "skip_reason": "NONE",

        "quantity_calculated": True,
        "execution_quantity": str(quantity),

        "trade_authorized": False,
        "order_payload_created": False,
        "exchange_write": False,
    })

    print(
        "UNIT 8 STATUS = READY",
        flush=True
    )

    print(
        "UNIT 8 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 8 EXECUTABLE QUANTITY =",
        quantity,
        flush=True
    )

    print(
        "UNIT 8 TRADE PLAN READY = TRUE",
        flush=True
    )

    print(
        "UNIT 8 TRADE AUTHORIZED = FALSE",
        flush=True
    )

    print(
        "UNIT 8 LEVERAGE SOURCE = RENDER",
        flush=True
    )

    print(
        "UNIT 8 LEVERAGE API VERIFIED = FALSE",
        flush=True
    )

    print(
        "UNIT 8 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        "UNIT 8 V6 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return output


# ============================================================
# UNIT 8 V6 VALIDATION
# PURE LOCAL CHECKS - NO NETWORK CALLS
# ============================================================

def unit_8_validation_v6():

    print("=" * 80, flush=True)
    print(
        "UNIT 8 V6 VALIDATION START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    incoming = (
        FRESH_RECONSTRUCTION_SIZING_CANDIDATE
    )

    tests = []

    tests.append((
        "UNIT 7 V10 HANDOVER",
        incoming.get("unit_7_version")
        == "UNIT7_V10_DYNAMIC"
    ))

    tests.append((
        "DEMO ENVIRONMENT",
        config.get("execution_environment")
        == "DEMO"
    ))

    tests.append((
        "FIVE DYNAMIC BACKUPS",
        incoming.get("max_backups") == 5
        and "backup_multipliers"
            not in config["strategy"]
    ))

    tests.append((
        "EXPOSURE CAP VALID",
        Decimal("0")
        < Decimal(str(
            incoming["exposure_cap_percent"]
        ))
        <= Decimal("100")
    ))

    tests.append((
        "RENDER LEVERAGE CONFIGURED",
        all(
            os.getenv(name, "").strip()
            for name in (
                "WEEX_DEMO_LONG_LEVERAGE",
                "WEEX_DEMO_SHORT_LEVERAGE",
            )
        )
    ))

    tests.append((
        "UNIT 8 UPSTREAM NO WRITE",
        incoming.get("exchange_write")
        is False
    ))

    tests.append((
        "MINIMUM BTC NORMALIZATION",
        unit_8_v6_quantity(
            "1",
            "10",
            "75000",
            "0.0001",
            "0.0001",
        )["minimum_quantity_pass"]
        is True
    ))

    tests.append((
        "BELOW MINIMUM REJECTED",
        unit_8_v6_quantity(
            "0.5",
            "10",
            "75000",
            "0.0001",
            "0.0001",
        )["minimum_quantity_pass"]
        is False
    ))

    tests.append((
        "LONG SHORT LEVERAGE INDEPENDENT",
        (
            unit_8_v6_quantity(
                "1", "10", "75000",
                "0.0001", "0.0001"
            )["quantity"]
            <
            unit_8_v6_quantity(
                "1", "20", "75000",
                "0.0001", "0.0001"
            )["quantity"]
        )
    ))

    tests.append((
        "UNIT 8 NO BACKUP MULTIPLIER",
        incoming.get("backup_sizing_mode")
        == "PERCENT_AVAILABLE_BALANCE"
    ))

    passed = sum(
        1 for _, ok in tests if ok
    )

    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 8 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 8 TESTS PASSED =",
        passed,
        flush=True
    )

    print(
        "UNIT 8 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 8 V6 VALIDATION FAILED"
        )

    print(
        "UNIT 8 V6 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# UNIT 8 V6 EXECUTION
# KEEP THESE CALLS BELOW ALL DEFINITIONS
# ============================================================

FRESH_UNIT_8_VALIDATION_READY = (
    unit_8_validation_v6()
)

FRESH_RECONSTRUCTION_ACCOUNT_CANDIDATE = (
    fresh_reconstruction_unit_8(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_SIZING_CANDIDATE,
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
    )
)

# Original model-compatible Unit 9 input name
FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    FRESH_RECONSTRUCTION_ACCOUNT_CANDIDATE
)

print(
    "FRESH RECONSTRUCTION UNIT 8 V6 READY =",
    FRESH_UNIT_8_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 8 V6
# UNIT 9 FOLLOWS
# ============================================================



# ============================================================
# START COMPLETE UNIT 9 V3
# WEEX DEMO EXECUTION PREPARATION
# RENDER ENTRY MARGIN AUTHORITATIVE
# UNIT 8 V6 -> UNIT 9 V3 -> UNIT 10
# ZERO INDENTATION
#
# NO HARDCODED ENTRY AMOUNT
# NO LEVERAGE MUTATION
# NO ORDER SUBMISSION
# NO NETWORK REQUESTS
# ============================================================

import os
from decimal import Decimal, InvalidOperation


def unit_9_v3_number(value, name, zero=False):

    if isinstance(value, bool):
        raise ValueError(name + "_BOOLEAN")

    try:
        result = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError(name + "_INVALID")

    if not result.is_finite():
        raise ValueError(name + "_NONFINITE")

    if result < 0 or (result == 0 and not zero):
        raise ValueError(name + "_NONPOSITIVE")

    return result


def unit_9_v3_render_entry():

    # One authoritative Render variable.
    # No default, fallback or fixed Python amount.
    raw = os.environ.get("INITIAL_ENTRY_MARGIN_USDT")

    if raw is None or not raw.strip():
        raise ValueError(
            "INITIAL_ENTRY_MARGIN_USDT_MISSING"
        )

    return unit_9_v3_number(
        raw.strip(), "RENDER_ENTRY_MARGIN"
    )


def fresh_reconstruction_unit_9(config, unit_8_result):

    print("=" * 80, flush=True)
    print("UNIT 9 V3 START", flush=True)

    if not isinstance(config, dict):
        raise RuntimeError("UNIT9_CONFIG_INVALID")

    if not isinstance(unit_8_result, dict):
        raise RuntimeError("UNIT9_UNIT8_INVALID")

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    safety = config.get("safety", {})

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("demo_order_symbol") != "BTCSUSDT"
        or safety.get("real_order_submission_enabled")
            is not False
    ):
        raise RuntimeError("UNIT9_DEMO_CONTRACT_FAILED")

    if (
        strategy.get("max_backups") != 5
        or "backup_multipliers" in strategy
    ):
        raise RuntimeError(
            "UNIT9_DYNAMIC_BACKUP_POLICY_FAILED"
        )

    required = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "trade_plan",
        "skip_reason",
        "read_only",
    )

    if any(k not in unit_8_result for k in required):
        raise RuntimeError(
            "UNIT9_UNIT8_INTERFACE_INCOMPLETE"
        )

    if (
        unit_8_result.get("unit_8_version")
            != "UNIT8_V6_RENDER_LEVERAGE"
        or unit_8_result["read_only"] is not True
        or unit_8_result.get("exchange_write")
            is not False
        or unit_8_result.get("order_payload_created")
            is not False
    ):
        raise RuntimeError(
            "UNIT9_UPSTREAM_SAFETY_FAILED"
        )

    mode = str(
        unit_8_result["active_mode"]
    ).upper()

    direction = str(
        unit_8_result["direction"]
    ).upper()

    status = str(
        unit_8_result["status"]
    ).upper()

    result = {
        "status": "IDLE",
        "active_mode": mode,
        "direction": direction,
        "signal_qualified": (
            unit_8_result["signal_qualified"] is True
        ),
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "execution_ready": False,
        "execution_candidate": None,
        "skip_reason": "NONE",
        "order_payload_created": False,
        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "read_only": True,

        "unit_9_version":
            "UNIT9_V3_RENDER_ENTRY",

        "entry_margin_source":
            "RENDER_INITIAL_ENTRY_MARGIN_USDT",
        "entry_margin_usdt": None,
        "entry_margin_verified": False,
        "leverage_source":
            "RENDER_MANUAL_WEEX_DEMO",
        "exchange_leverage_verified": False,
        "trade_authorized": False,
        "exchange_write": False,
    }

    def finish(state, reason):
        result["status"] = state
        result["skip_reason"] = reason

        print("UNIT 9 STATUS =", state, flush=True)
        print("UNIT 9 REASON =", reason, flush=True)
        print(
            "UNIT 9 EXECUTION READY =",
            result["execution_ready"],
            flush=True
        )
        print(
            "UNIT 9 EXCHANGE WRITE = NONE",
            flush=True
        )
        print("=" * 80, flush=True)

        return result

    # ========================================================
    # 1. READ CURRENT RENDER SETTING ON EVERY CALL
    # ========================================================

    try:
        render_entry = unit_9_v3_render_entry()
    except ValueError as exc:
        print(
            "UNIT 9 ENTRY CONFIG ERROR =",
            str(exc),
            flush=True
        )
        return finish(
            "BLOCKED",
            "RENDER_ENTRY_MARGIN_INVALID_OR_MISSING"
        )

    result["entry_margin_usdt"] = str(render_entry)

    print(
        "UNIT 9 RENDER ENTRY MARGIN SUSDT =",
        render_entry,
        flush=True
    )
    print(
        "UNIT 9 ENTRY SOURCE = INITIAL_ENTRY_MARGIN_USDT",
        flush=True
    )

    # ========================================================
    # 2. PRESERVE NORMAL NO-TRADE STATES
    # ========================================================

    if status == "BLOCKED":
        return finish(
            "BLOCKED",
            unit_8_result.get("skip_reason")
            or "UNIT8_BLOCKED"
        )

    if status == "IDLE":
        return finish(
            "IDLE",
            unit_8_result.get("skip_reason")
            or "NO_EXECUTION_INTENT"
        )

    if status != "READY":
        return finish(
            "BLOCKED",
            "UNIT8_STATUS_INVALID"
        )

    if not all((
        unit_8_result["signal_qualified"] is True,
        unit_8_result["execution_intent"] is True,
        unit_8_result["trade_plan_ready"] is True,
        unit_8_result.get("demo_balance_verified")
            is True,
        unit_8_result.get("demo_positions_verified")
            is True,
        unit_8_result.get("position_flat_verified")
            is True,
        unit_8_result.get("leverage_configured")
            is True,
    )):
        return finish(
            "BLOCKED",
            "UNIT8_READY_CONTRACT_INCOMPLETE"
        )

    if (
        mode not in ("BREAKOUT", "STRUCTURE", "SCALP")
        or direction not in ("LONG", "SHORT")
    ):
        return finish(
            "BLOCKED",
            "MODE_OR_DIRECTION_INVALID"
        )

    # ========================================================
    # 3. VALIDATE ORIGINAL TRADE PLAN IDENTITY
    # ========================================================

    plan = unit_8_result.get("trade_plan")

    if not isinstance(plan, dict):
        return finish(
            "BLOCKED",
            "TRADE_PLAN_MISSING"
        )

    if (
        plan.get("active_mode") != mode
        or plan.get("direction") != direction
        or plan.get("execution_environment") != "DEMO"
    ):
        return finish(
            "BLOCKED",
            "TRADE_PLAN_IDENTITY_MISMATCH"
        )

    sizing = plan.get("position_sizing")

    if not isinstance(sizing, dict):
        return finish(
            "BLOCKED",
            "POSITION_SIZING_MISSING"
        )

    # ========================================================
    # 4. CRITICAL RENDER MARGIN SYNCHRONIZATION
    # ========================================================

    try:
        plan_margin = unit_9_v3_number(
            sizing.get("margin_allocation"),
            "UNIT8_PLAN_MARGIN"
        )
    except ValueError:
        return finish(
            "BLOCKED",
            "UNIT8_PLAN_MARGIN_INVALID"
        )

    if plan_margin != render_entry:
        print(
            "UNIT 9 RENDER MARGIN =",
            render_entry,
            flush=True
        )
        print(
            "UNIT 9 UNIT 8 PLAN MARGIN =",
            plan_margin,
            flush=True
        )
        return finish(
            "BLOCKED",
            "RENDER_UNIT8_ENTRY_MARGIN_MISMATCH"
        )

    result["entry_margin_verified"] = True

    # ========================================================
    # 5. VALIDATE QUANTITY AND LEVERAGE
    # WITHOUT RESIZING OR CHANGING THEM
    # ========================================================

    try:
        quantity = unit_9_v3_number(
            plan.get("quantity"),
            "PLAN_QUANTITY"
        )
        sized_quantity = unit_9_v3_number(
            sizing.get("quantity"),
            "SIZING_QUANTITY"
        )
        minimum = unit_9_v3_number(
            sizing.get("minimum_quantity"),
            "MINIMUM_BTC"
        )
        step = unit_9_v3_number(
            sizing.get("quantity_step"),
            "QUANTITY_STEP"
        )
        leverage = unit_9_v3_number(
            sizing.get("leverage_target"),
            "PLAN_LEVERAGE"
        )
        price = unit_9_v3_number(
            sizing.get("live_mark_price"),
            "MARK_PRICE"
        )
        available = unit_9_v3_number(
            unit_8_result.get("available_balance"),
            "AVAILABLE_BALANCE",
            zero=True
        )
        equity = unit_9_v3_number(
            unit_8_result.get("account_equity"),
            "ACCOUNT_EQUITY",
            zero=True
        )
        cap = unit_9_v3_number(
            unit_8_result.get("exposure_cap_percent"),
            "EXPOSURE_CAP"
        )
    except ValueError as exc:
        print(
            "UNIT 9 PLAN ERROR =",
            str(exc),
            flush=True
        )
        return finish(
            "BLOCKED",
            "TRADE_PLAN_NUMERIC_ERROR"
        )

    if (
        quantity != sized_quantity
        or quantity < minimum
        or quantity % step != 0
    ):
        return finish(
            "BLOCKED",
            "QUANTITY_PRECISION_OR_MINIMUM_FAILED"
        )

    render_leverage = (
        unit_8_result.get("weex_demo_long_leverage")
        if direction == "LONG"
        else unit_8_result.get("weex_demo_short_leverage")
    )

    try:
        configured_leverage = unit_9_v3_number(
            render_leverage,
            "RENDER_DIRECTIONAL_LEVERAGE"
        )
    except ValueError:
        return finish(
            "BLOCKED",
            "RENDER_DIRECTIONAL_LEVERAGE_INVALID"
        )

    if leverage != configured_leverage:
        return finish(
            "BLOCKED",
            "LEVERAGE_PLAN_MISMATCH"
        )

    if (
        sizing.get("leverage_source")
            != "RENDER_MANUAL_WEEX_DEMO"
        or unit_8_result.get("leverage_source")
            != "RENDER_MANUAL_WEEX_DEMO"
    ):
        return finish(
            "BLOCKED",
            "LEVERAGE_SOURCE_MISMATCH"
        )

    # ========================================================
    # 6. AVAILABLE BALANCE AND EXPOSURE
    # PRELIMINARY CHECK ONLY
    # ========================================================

    if cap > Decimal("100"):
        return finish(
            "BLOCKED",
            "EXPOSURE_CAP_INVALID"
        )

    if render_entry > available:
        return finish(
            "BLOCKED",
            "INSUFFICIENT_DEMO_BALANCE"
        )

    if render_entry > (
        equity * cap / Decimal("100")
    ):
        return finish(
            "BLOCKED",
            "ENTRY_EXCEEDS_EXPOSURE_CAP"
        )

    if (
        quantity * price / leverage
    ) > render_entry + Decimal("0.00000001"):
        return finish(
            "BLOCKED",
            "NOTIONAL_EXCEEDS_RENDER_ENTRY_MARGIN"
        )

    # ========================================================
    # 7. FIVE DYNAMIC BACKUPS
    # NO FIXED MULTIPLIERS OR FULL-LADDER RESERVE
    # ========================================================

    if (
        unit_8_result.get("max_backups") != 5
        or sizing.get("max_backups") != 5
        or sizing.get("backup_sizing_mode")
            != "PERCENT_AVAILABLE_BALANCE"
        or sizing.get("backup_margin_reserved")
            is not False
    ):
        return finish(
            "BLOCKED",
            "DYNAMIC_BACKUP_CONTRACT_FAILED"
        )

    # ========================================================
    # 8. ORIGINAL UNIT 10 HANDOVER
    # ========================================================

    execution_candidate = {
        "active_mode": mode,
        "direction": direction,
        "trade_plan": plan,
        "execution_environment": "DEMO",
    }

    result.update({
        "status": "READY",
        "signal_qualified": True,
        "execution_intent": True,
        "trade_plan_ready": True,
        "trade_plan": plan,
        "execution_ready": True,
        "execution_candidate": execution_candidate,
        "skip_reason": "NONE",

        "quantity": float(quantity),
        "selected_leverage": float(leverage),

        "margin_budget_prechecked": True,
        "margin_budget_fresh_verified": False,

        "trade_authorized": False,
        "exchange_write": False,
    })

    print(
        "UNIT 9 RENDER ENTRY MARGIN =",
        render_entry,
        flush=True
    )
    print(
        "UNIT 9 BTC QUANTITY =",
        quantity,
        flush=True
    )
    print(
        "UNIT 9 LEVERAGE =",
        leverage,
        flush=True
    )
    print(
        "UNIT 9 ENTRY MARGIN VERIFIED = True",
        flush=True
    )
    print(
        "UNIT 9 EXECUTION READY = True",
        flush=True
    )
    print(
        "UNIT 9 TRADE AUTHORIZED = False",
        flush=True
    )
    print(
        "UNIT 9 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 9 RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 9 V3 VALIDATION
# ============================================================

def unit_9_validation_v3():

    print("=" * 80, flush=True)
    print(
        "UNIT 9 V3 VALIDATION START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    actual = FRESH_RECONSTRUCTION_UNIT_8_RESULT

    tests = []

    def record(name, condition):
        tests.append((name, bool(condition)))

    record(
        "UNIT 8 V6 INPUT",
        actual.get("unit_8_version")
        == "UNIT8_V6_RENDER_LEVERAGE"
    )

    record(
        "DEMO ONLY",
        config.get("execution_environment") == "DEMO"
    )

    record(
        "NO FIXED BACKUP MULTIPLIERS",
        "backup_multipliers"
        not in config["strategy"]
    )

    record(
        "RENDER ENTRY VARIABLE PRESENT",
        bool(
            os.getenv(
                "INITIAL_ENTRY_MARGIN_USDT", ""
            ).strip()
        )
    )

    try:
        margin = unit_9_v3_render_entry()
        record(
            "RENDER ENTRY POSITIVE",
            margin > 0
        )
    except ValueError:
        record(
            "RENDER ENTRY POSITIVE",
            False
        )

    record(
        "UNIT 8 NO EXCHANGE WRITE",
        actual.get("exchange_write") is False
    )

    record(
        "UNIT 8 LONG LEVERAGE PRESENT",
        actual.get("weex_demo_long_leverage")
        is not None
    )

    record(
        "UNIT 8 SHORT LEVERAGE PRESENT",
        actual.get("weex_demo_short_leverage")
        is not None
    )

    # Test an idle handover without fabricating a trade.
    idle = dict(actual)
    idle.update({
        "status": "IDLE",
        "active_mode": "NONE",
        "direction": "NONE",
        "signal_qualified": False,
        "execution_intent": False,
        "trade_plan_ready": False,
        "trade_plan": None,
        "skip_reason": "NO_ACCEPTABLE_CANDIDATE",
    })

    idle_result = fresh_reconstruction_unit_9(
        config, idle
    )

    record(
        "IDLE HANDOVER",
        idle_result["status"] == "IDLE"
    )

    record(
        "ORIGINAL UNIT 10 CONTRACT",
        all(
            key in idle_result
            for key in (
                "status",
                "active_mode",
                "direction",
                "signal_qualified",
                "execution_intent",
                "trade_plan_ready",
                "trade_plan",
                "execution_ready",
                "execution_candidate",
                "skip_reason",
                "order_payload_created",
                "tp_execution_requested",
                "sl_execution_requested",
                "read_only",
            )
        )
    )

    passed = sum(ok for _, ok in tests)
    failed = len(tests) - passed

    for name, ok in tests:
        print(
            "UNIT 9 TEST:",
            name,
            "=",
            "PASS" if ok else "FAIL",
            flush=True
        )

    print(
        "UNIT 9 TESTS PASSED =",
        passed,
        flush=True
    )
    print(
        "UNIT 9 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 9 V3 VALIDATION FAILED"
        )

    print(
        "UNIT 9 V3 VALIDATION RESULT = PASS",
        flush=True
    )

    return True


# ============================================================
# EXECUTE UNIT 9 V3
# ============================================================

FRESH_UNIT_9_VALIDATION_READY = (
    unit_9_validation_v3()
)

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
    )
)

print(
    "FRESH RECONSTRUCTION UNIT 9 V3 READY =",
    FRESH_UNIT_9_VALIDATION_READY,
    flush=True
)

# ============================================================
# END COMPLETE UNIT 9 V3
# UNIT 10 FOLLOWS
# ============================================================
