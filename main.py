
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
# START COMPLETE UNIT 2 REPLACEMENT V2
# WEEX HYBRID 15-UNIT MODEL
# CONFIGURATION + HYBRID QUALIFICATION + VALIDATION
# ZERO INDENTATION
# ============================================================

def fresh_reconstruction_unit_2():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 START")

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError(
            "UNIT 2 BLOCKED: UNIT 1 NOT READY"
        )

    # ========================================================
    # 1. EXCHANGE CONFIGURATION
    # ========================================================

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url": (
            "https://api-contract.weex.com"
        ),
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
    }

    execution_environment = "DEMO"

    # ========================================================
    # 2. UNIT-LOCAL SAFETY
    #
    # These flags apply to Unit 2 itself.
    # They do not disable later authorized DEMO orders.
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
    }

    # ========================================================
    # 3. ORIGINAL STRATEGY CONFIGURATION
    # PRESERVE EXISTING DOWNSTREAM KEYS
    # ========================================================

    strategy = {

        "initial_margin_percent": 5.0,

        # Fixed intended allocation for initial entries.
        "initial_fixed_usdt": 2.00,

        "backup_margin_percent": 5.0,
        "backup_buffer_percent": 0.30,

        "max_backups": 5,

        "backup_multipliers": (
            1.0,
            1.5,
            2.0,
            2.5,
            3.0,
        ),

        "exposure_cap_percent": 35.0,

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

    # ========================================================
    # 4. MARKET PRECISION
    # ========================================================

    market_precision = {
        "quantity_step": 0.0001,
        "minimum_quantity": 0.0001,
        "price_step": 0.1,
    }

    # ========================================================
    # 5. ORIGINAL CONFIGURATION CONTRACT
    # ========================================================

    config = {
        "exchange": exchange,
        "execution_environment": execution_environment,
        "safety": safety,
        "strategy": strategy,
        "market_precision": market_precision,
    }

    # ========================================================
    # 6. INITIAL CONFIGURATION VALIDATION
    # ========================================================

    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(
        exchange["name"] == "WEEX",
        "INVALID EXCHANGE"
    )

    require(
        exchange["api_version"] == "V3",
        "INVALID API VERSION"
    )

    require(
        exchange["contract_base_url"]
        == "https://api-contract.weex.com",
        "INVALID BASE URL"
    )

    require(
        exchange["market_symbol"] == "BTCUSDT",
        "INVALID MARKET SYMBOL"
    )

    require(
        exchange["demo_order_symbol"] == "BTCSUSDT",
        "INVALID DEMO SYMBOL"
    )

    require(
        execution_environment == "DEMO",
        "LIVE EXECUTION NOT ALLOWED"
    )

    require(
        0 < strategy["initial_margin_percent"] <= 5.0,
        "INVALID INITIAL MARGIN PERCENT"
    )

    require(
        strategy["initial_fixed_usdt"] > 0,
        "INVALID INITIAL ALLOCATION"
    )

    require(
        strategy["max_backups"] == 5,
        "INVALID BACKUP COUNT"
    )

    require(
        tuple(strategy["backup_multipliers"])
        == (1.0, 1.5, 2.0, 2.5, 3.0),
        "INVALID BACKUP MULTIPLIERS"
    )

    require(
        strategy["backup_buffer_percent"] == 0.30,
        "INVALID BACKUP BUFFER"
    )

    require(
        0 < strategy["backup_margin_percent"] <= 5.0,
        "INVALID BACKUP MARGIN PERCENT"
    )

    require(
        strategy["exposure_cap_percent"] == 35.0,
        "INVALID EXPOSURE CAP"
    )

    require(
        strategy["progressive_backup_funding"] is True,
        "PROGRESSIVE FUNDING DISABLED"
    )

    require(
        strategy["full_ladder_reservation_required"]
        is False,
        "FULL LADDER RESERVATION ENABLED"
    )

    tp_total = sum(
        strategy[key]
        for key in (
            "tp1_allocation_percent",
            "tp2_allocation_percent",
            "tp3_allocation_percent",
        )
    )

    require(
        abs(tp_total - 100.0) < 0.000001,
        "INVALID TP ALLOCATION"
    )

    require(
        strategy["tp1_net_roi_floor_percent"] >= 5.0,
        "TP1 FLOOR TOO LOW"
    )

    require(
        strategy["tp2_net_roi_floor_percent"] >= 10.0,
        "TP2 FLOOR TOO LOW"
    )

    require(
        strategy["tp2_net_roi_floor_percent"]
        > strategy["tp1_net_roi_floor_percent"],
        "TP2 MUST EXCEED TP1"
    )

    require(
        strategy["tp1_tp2_min_roi_separation_percent"]
        > 0,
        "INVALID TP SEPARATION"
    )

    require(
        0
        < strategy["tp3_trailing_min_percent"]
        <= strategy["tp3_trailing_reference_percent"]
        <= strategy["tp3_trailing_max_percent"],
        "INVALID TP3 RANGE"
    )

    for key in (
        "signal_expiry_seconds",
        "loss_cooldown_seconds",
        "mode_confirmations_required",
    ):
        require(
            strategy[key] > 0,
            "INVALID SIGNAL CONTROL: " + key
        )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "active_trade_mode_lock",
        "exclusive_mode",
    ):
        require(
            strategy[key] is True,
            "REQUIRED STRATEGY CONTROL DISABLED: " + key
        )

    for key in (
        "quantity_step",
        "minimum_quantity",
        "price_step",
    ):
        require(
            market_precision[key] > 0,
            "INVALID PRECISION: " + key
        )

    require(
        safety["public_market_data_read_enabled"] is True,
        "PUBLIC MARKET READ DISABLED"
    )

    for key in (
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
    ):
        require(
            safety[key] is False,
            "UNIT 2 UNSAFE CAPABILITY: " + key
        )

    if errors:
        print(
            "UNIT 2 VALIDATION ERRORS =",
            errors,
            flush=True
        )
        raise RuntimeError(
            "UNIT 2 CONFIGURATION VALIDATION FAILED"
        )

    full_ladder_margin = (
        strategy["initial_fixed_usdt"]
        * (
            1.0
            + sum(strategy["backup_multipliers"])
        )
    )

    print(
        "PASS: UNIT 2 CONFIGURATION CREATED",
        flush=True
    )

    print("PASS: EXCHANGE = WEEX", flush=True)
    print("PASS: API VERSION = V3", flush=True)
    print("PASS: MARKET SYMBOL = BTCUSDT", flush=True)
    print("PASS: DEMO ORDER SYMBOL = BTCSUSDT", flush=True)
    print("PASS: EXECUTION ENVIRONMENT = DEMO", flush=True)

    print(
        "PASS: LEVERAGE CONTROL = WEEX EXCHANGE ONLY",
        flush=True
    )
    print(
        "PASS: PYTHON FIXED LEVERAGE TARGET = NONE",
        flush=True
    )
    print(
        "PASS: LEVERAGE MUTATION = DISABLED",
        flush=True
    )

    print(
        "PASS: INITIAL MARGIN % =",
        strategy["initial_margin_percent"],
        flush=True
    )
    print(
        "PASS: DEFAULT INITIAL MARGIN USDT =",
        strategy["initial_fixed_usdt"],
        flush=True
    )
    print(
        "PASS: BACKUP MARGIN % =",
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
        "PASS: BACKUP MULTIPLIERS =",
        strategy["backup_multipliers"],
        flush=True
    )
    print(
        "PASS: EXPOSURE CAP % =",
        strategy["exposure_cap_percent"],
        flush=True
    )
    print(
        "PASS: BACKUP FUNDING = PROGRESSIVE",
        flush=True
    )
    print(
        "PASS: FULL LADDER RESERVATION = FALSE",
        flush=True
    )
    print(
        "UNIT 2 FULL LADDER MARGIN USDT =",
        full_ladder_margin,
        flush=True
    )

    print(
        "PASS: TP TARGET ALLOCATION = 10% / 20% / 70%",
        flush=True
    )
    print(
        "PASS: TP ALLOCATION TOTAL =",
        tp_total,
        "%",
        flush=True
    )
    print(
        "PASS: TP1 NET ROI FLOOR =",
        strategy["tp1_net_roi_floor_percent"],
        "%",
        flush=True
    )
    print(
        "PASS: TP2 NET ROI FLOOR =",
        strategy["tp2_net_roi_floor_percent"],
        "%",
        flush=True
    )
    print(
        "PASS: TP1 -> TP2 MIN ROI SEPARATION =",
        strategy[
            "tp1_tp2_min_roi_separation_percent"
        ],
        "%",
        flush=True
    )

    print(
        "PASS: TP3 TRAILING REFERENCE =",
        strategy["tp3_trailing_reference_percent"],
        "%",
        flush=True
    )
    print(
        "PASS: TP3 TRAILING RANGE =",
        strategy["tp3_trailing_min_percent"],
        "% TO",
        strategy["tp3_trailing_max_percent"],
        "%",
        flush=True
    )
    print("PASS: TP3 TRAILING MODE = DYNAMIC", flush=True)
    print(
        "PASS: TP3 DYNAMIC INPUTS = "
        "TREND + ATR/VOLATILITY + MOMENTUM DETERIORATION",
        flush=True
    )

    print("PASS: TP QUANTITY MODE = STEP-AWARE", flush=True)
    print(
        "PASS: QUANTITY STEP =",
        market_precision["quantity_step"],
        flush=True
    )
    print(
        "PASS: MINIMUM QUANTITY =",
        market_precision["minimum_quantity"],
        flush=True
    )
    print(
        "PASS: PRICE STEP =",
        market_precision["price_step"],
        flush=True
    )

    for key, label in (
        ("anti_duplicate_orders", "ANTI-DUPLICATE ORDERS"),
        ("one_direction_only", "ONE DIRECTION ONLY"),
        ("active_trade_mode_lock", "ACTIVE TRADE MODE LOCK"),
        ("exclusive_mode", "EXCLUSIVE MODE"),
    ):
        print(
            "PASS:",
            label,
            "=",
            strategy[key],
            flush=True
        )

    print("PASS: SL = DISABLED", flush=True)
    print("PASS: PUBLIC MARKET DATA READ ENABLED", flush=True)

    for name in (
        "AUTHENTICATED API ACCESS",
        "ACCOUNT ACCESS",
        "POSITION ACCESS",
        "ORDER ENDPOINT ACCESS",
        "DEMO ORDER SUBMISSION",
        "REAL ORDER SUBMISSION",
        "EXCHANGE MUTATION",
        "LEVERAGE MUTATION",
        "MARGIN MODE MUTATION",
        "POSITION MODE MUTATION",
    ):
        print(
            "ZERO " + name + " = TRUE",
            flush=True
        )

    log("FRESH RECONSTRUCTION UNIT 2 RESULT = PASS")
    print("=" * 80, flush=True)

    return config


# ============================================================
# 7. EXECUTE ORIGINAL UNIT 2 FIRST
# THIS CREATES THE CONFIGURATION REQUIRED BY ADAPTERS
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# 8. UNIT 2 HYBRID ADJUSTABLE CONFIGURATION
# PRESERVE ORIGINAL KEY NAMES
# ============================================================

def fresh_unit_2_hybrid_adjustable_adapter(config):

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 2 ADAPTER: INVALID CONFIGURATION"
        )

    if not isinstance(config.get("strategy"), dict):
        raise RuntimeError(
            "UNIT 2 ADAPTER: STRATEGY MISSING"
        )

    qualification = {

        # ====================================================
        # COMMON
        # ====================================================

        "common": {
            "mode_priority": (
                "BREAKOUT",
                "STRUCTURE",
                "SCALP",
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

        # ====================================================
        # BREAKOUT
        # ====================================================

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

        # ====================================================
        # STRUCTURE
        # ====================================================

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

        # ====================================================
        # SCALP
        # ====================================================

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

    config["qualification"] = qualification

    # No assumed or preverified exchange leverage.
    # Unit 8 remains responsible for the directional
    # leverage configuration and related checks.

    config["strategy"].pop("leverage_target", None)

    print("=" * 80, flush=True)
    print("UNIT 2 HYBRID ADJUSTABLE V3 ADAPTER", flush=True)
    print("UNIT 2 ORIGINAL CONFIGURATION = RETAINED", flush=True)

    print(
        "UNIT 2 MODE PRIORITY =",
        qualification["common"]["mode_priority"],
        flush=True
    )
    print(
        "UNIT 2 SCALP QUALITY DEFAULT =",
        qualification["scalp"]["quality_threshold"],
        flush=True
    )
    print(
        "UNIT 2 STRUCTURE PULLBACK ATR =",
        qualification["structure"]["pullback_tolerance_atr"],
        flush=True
    )
    print(
        "UNIT 2 BREAKOUT PROXIMITY ATR =",
        qualification["breakout"]["developing_proximity_atr"],
        flush=True
    )
    print(
        "UNIT 2 BREAKOUT CONFIRMATION ATR =",
        qualification["breakout"]["confirmation_distance_atr"],
        flush=True
    )

    print(
        "UNIT 2 REJECTED HIGHER MODE = NOT A SCALP LOCK",
        flush=True
    )
    print(
        "UNIT 2 DEVELOPING HIGHER MODE = PROTECTED",
        flush=True
    )
    print(
        "UNIT 2 EXCHANGE LEVERAGE CONTROL = WEEX ONLY",
        flush=True
    )
    print(
        "UNIT 2 FIXED PYTHON LEVERAGE = NONE",
        flush=True
    )
    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )
    print(
        "FRESH RECONSTRUCTION UNIT 2 ADAPTER RESULT = PASS",
        flush=True
    )
    print("=" * 80, flush=True)

    return config


# ============================================================
# 9. EXECUTE HYBRID ADAPTER SECOND
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_unit_2_hybrid_adjustable_adapter(
        FRESH_RECONSTRUCTION_CONFIG
    )
)


# ============================================================
# 10. UNIT 2 OPTIMIZATION VALIDATION V2
# READ ONLY / NO EXCHANGE REQUESTS
# ============================================================

def unit_2_optimization_validation_v2(config):

    print("=" * 80, flush=True)
    print(
        "UNIT 2 OPTIMIZATION VALIDATION V2 START",
        flush=True
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 2 TEST FAILED: CONFIGURATION MISSING"
        )

    exchange = config.get("exchange", {})
    strategy = config.get("strategy", {})
    safety = config.get("safety", {})
    precision = config.get("market_precision", {})
    qualification = config.get("qualification", {})

    common = qualification.get("common", {})
    breakout = qualification.get("breakout", {})
    structure = qualification.get("structure", {})
    scalp = qualification.get("scalp", {})

    tests = {

        "WEEX EXCHANGE":
            exchange.get("name") == "WEEX",

        "V3 API":
            exchange.get("api_version") == "V3",

        "MARKET SYMBOL":
            exchange.get("market_symbol") == "BTCUSDT",

        "DEMO ORDER SYMBOL":
            exchange.get("demo_order_symbol") == "BTCSUSDT",

        "DEMO ENVIRONMENT":
            config.get("execution_environment") == "DEMO",

        "INITIAL MARGIN 2 USDT":
            strategy.get("initial_fixed_usdt") == 2.00,

        "FIVE BACKUPS":
            strategy.get("max_backups") == 5,

        "BACKUP MULTIPLIERS":
            tuple(strategy.get("backup_multipliers", ()))
            == (1.0, 1.5, 2.0, 2.5, 3.0),

        "EXPOSURE CAP":
            strategy.get("exposure_cap_percent") == 35.0,

        "PROGRESSIVE FUNDING":
            strategy.get("progressive_backup_funding")
            is True,

        "NO FULL LADDER RESERVATION":
            strategy.get("full_ladder_reservation_required")
            is False,

        "MODE PRIORITY":
            tuple(common.get("mode_priority", ()))
            == ("BREAKOUT", "STRUCTURE", "SCALP"),

        "DEVELOPING MODE PROTECTION":
            common.get("protect_developing_candidates")
            is True,

        "BREAKOUT PROXIMITY":
            breakout.get("developing_proximity_atr")
            == 0.50,

        "BREAKOUT CONFIRMATION":
            breakout.get("confirmation_distance_atr")
            == 0.10,

        "STRUCTURE PULLBACK":
            structure.get("pullback_tolerance_atr")
            == 0.75,

        "SCALP QUALITY":
            scalp.get("quality_threshold") == 70.0,

        "SCALP SIDEWAYS RULE":
            scalp.get("require_sideways_market")
            is True,

        "SCALP FEE AWARE":
            scalp.get("fee_aware_enabled")
            is True,

        "TP TOTAL":
            sum(
                strategy.get(key, 0)
                for key in (
                    "tp1_allocation_percent",
                    "tp2_allocation_percent",
                    "tp3_allocation_percent",
                )
            ) == 100.0,

        "TP1 FLOOR":
            strategy.get("tp1_net_roi_floor_percent")
            >= 5.0,

        "TP2 FLOOR":
            strategy.get("tp2_net_roi_floor_percent")
            >= 10.0,

        "QUANTITY STEP":
            precision.get("quantity_step") == 0.0001,

        "NO PREVERIFIED LEVERAGE TARGET":
            "leverage_target" not in strategy,

        "NO LIVE ORDER CAPABILITY":
            safety.get("real_order_submission_enabled")
            is False,
    }

    passed = 0
    failed = 0

    for name, result in tests.items():

        if result:
            passed += 1
            verdict = "PASS"
        else:
            failed += 1
            verdict = "FAIL"

        print(
            "UNIT 2 TEST:",
            name,
            "=",
            verdict,
            flush=True
        )

    initial = float(
        strategy.get("initial_fixed_usdt", 0)
    )

    multipliers = strategy.get(
        "backup_multipliers", ()
    )

    full_ladder = (
        initial * (1.0 + sum(multipliers))
    )

    print(
        "UNIT 2 INITIAL MARGIN USDT =",
        initial,
        flush=True
    )
    print(
        "UNIT 2 FULL LADDER MARGIN USDT =",
        full_ladder,
        flush=True
    )
    print(
        "UNIT 2 TESTS PASSED =",
        passed,
        flush=True
    )
    print(
        "UNIT 2 TESTS FAILED =",
        failed,
        flush=True
    )

    if failed:
        raise RuntimeError(
            "UNIT 2 OPTIMIZATION VALIDATION FAILED"
        )

    print(
        "UNIT 2 OPTIMIZATION RESULT = PASS",
        flush=True
    )
    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )
    print("=" * 80, flush=True)

    return True


# ============================================================
# 11. EXECUTE VALIDATION LAST
# CONFIGURATION AND ADAPTER NOW EXIST
# ============================================================

FRESH_UNIT_2_OPTIMIZATION_READY = (
    unit_2_optimization_validation_v2(
        FRESH_RECONSTRUCTION_CONFIG
    )
)


# ============================================================
# END COMPLETE UNIT 2 REPLACEMENT V2
# UNIT 3 FOLLOWS BELOW
# ZERO INDENTATION
# ============================================================


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
# START COMPLETE UNIT 4 + HYBRID ADAPTER REPLACEMENT V4
# WEEX V3 MARKET DATA + STRATEGY EVIDENCE
# ONE INTEGRATED UNIT / ZERO INDENTATION
# COMPATIBLE WITH UNIT 5 V6
# NO AUTHENTICATED EXCHANGE WRITE
# ============================================================

import json
import math
import time
import urllib.parse
import urllib.request
import urllib.error


def unit_4_number_v4(value, name):

    if isinstance(value, bool):
        raise RuntimeError("UNIT 4 INVALID " + name)

    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID " + name
        ) from exc

    if not math.isfinite(result):
        raise RuntimeError(
            "UNIT 4 NONFINITE " + name
        )

    return result


def unit_4_ema_v4(prices, period):

    if len(prices) < period:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT EMA HISTORY"
        )

    result = sum(prices[:period]) / period
    multiplier = 2.0 / (period + 1.0)

    for price in prices[period:]:
        result = (
            multiplier * price
            + (1.0 - multiplier) * result
        )

    return result


def unit_4_normalize_v4(rows, market_time_ms):

    if not isinstance(rows, list):
        raise RuntimeError(
            "UNIT 4 INVALID WEEX CANDLE RESPONSE"
        )

    candles = []

    for row in rows:

        if not isinstance(row, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE FORMAT"
            )

        if len(row) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE CANDLE"
            )

        item = {
            "open_time_ms": int(row[0]),
            "open": unit_4_number_v4(row[1], "OPEN"),
            "high": unit_4_number_v4(row[2], "HIGH"),
            "low": unit_4_number_v4(row[3], "LOW"),
            "close": unit_4_number_v4(row[4], "CLOSE"),
            "volume": unit_4_number_v4(row[5], "VOLUME"),
            "close_time_ms": int(row[6]),
        }

        if not (
            0 < item["low"]
            <= min(item["open"], item["close"])
            <= max(item["open"], item["close"])
            <= item["high"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID OHLC RELATIONSHIP"
            )

        if item["volume"] < 0:
            raise RuntimeError(
                "UNIT 4 NEGATIVE CANDLE VOLUME"
            )

        if (
            item["close_time_ms"]
            <= item["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE TIMESTAMP"
            )

        candles.append(item)

    candles.sort(
        key=lambda candle: candle["open_time_ms"]
    )

    for i in range(1, len(candles)):

        if (
            candles[i]["open_time_ms"]
            - candles[i - 1]["open_time_ms"]
        ) != 60000:
            raise RuntimeError(
                "UNIT 4 MISSING OR DUPLICATE CANDLE"
            )

    closed = [
        candle for candle in candles
        if candle["close_time_ms"] <= market_time_ms
    ]

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED CANDLES"
        )

    age_ms = (
        market_time_ms - closed[-1]["close_time_ms"]
    )

    if not 0 <= age_ms <= 120000:
        raise RuntimeError(
            "UNIT 4 STALE CLOSED CANDLE"
        )

    return candles, closed


# ============================================================
# COMPLETE INTEGRATED UNIT 4
# ============================================================

def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)
    print(
        "UNIT 4 COMPLETE INTEGRATED V4 START",
        flush=True
    )

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 4 INVALID UNIT 2 CONFIGURATION"
        )

    if not isinstance(market, dict):
        raise RuntimeError(
            "UNIT 4 INVALID UNIT 3 SNAPSHOT"
        )

    exchange = config.get("exchange", {})
    qualification = config.get("qualification", {})
    safety = config.get("safety", {})

    if not all(
        isinstance(item, dict)
        for item in (
            exchange,
            qualification,
            safety
        )
    ):
        raise RuntimeError(
            "UNIT 4 INVALID CONFIGURATION SECTIONS"
        )

    if (
        market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != "BTCUSDT"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 3 MARKET CONTRACT FAILED"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("market_symbol") != "BTCUSDT"
        or exchange.get("api_version") != "V3"
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 2 EXCHANGE CONTRACT FAILED"
        )

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 4 PUBLIC MARKET READ DISABLED"
        )

    market_time_ms = int(market["exchange_time_ms"])
    live_mark_price = unit_4_number_v4(
        market["price"],
        "MARK PRICE"
    )

    now_ms = int(time.time() * 1000)

    if not (
        0 <= now_ms - market_time_ms <= 120000
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 3 MARKET DATA STALE"
        )

    if live_mark_price <= 0:
        raise RuntimeError(
            "UNIT 4 INVALID MARK PRICE"
        )

    common = qualification.get("common", {})
    breakout = qualification.get("breakout", {})
    structure = qualification.get("structure", {})
    scalp = qualification.get("scalp", {})

    if not all(
        isinstance(item, dict)
        for item in (
            common,
            breakout,
            structure,
            scalp
        )
    ):
        raise RuntimeError(
            "UNIT 4 QUALIFICATION CONFIG INVALID"
        )

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        raise RuntimeError(
            "UNIT 4 INVALID STRATEGY PRIORITY"
        )

    # ========================================================
    # 1. LIVE WEEX MARK PRICE CANDLE REQUEST
    # ========================================================

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 INVALID WEEX CONTRACT HOST"
        )

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
            "User-Agent": "WEEX-Unit4-Integrated-V4",
        }
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 4 HTTP METHOD INVALID"
        )

    request_started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            status = response.getcode()
            body = response.read().decode("utf-8")

    except urllib.error.HTTPError as exc:

        print(
            "UNIT 4 HTTP ERROR =",
            exc.code,
            flush=True
        )

        raise RuntimeError(
            "UNIT 4 WEEX HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 4 WEEX CONNECTION ERROR"
        ) from exc

    latency_ms = (
        time.monotonic() - request_started
    ) * 1000.0

    if status != 200 or not body:
        raise RuntimeError(
            "UNIT 4 INVALID HTTP RESPONSE"
        )

    try:
        raw_klines = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 INVALID WEEX JSON"
        ) from exc

    candles, closed = unit_4_normalize_v4(
        raw_klines,
        market_time_ms
    )

    # ========================================================
    # 2. EMA AND MOMENTUM
    # ========================================================

    prices = [c["close"] for c in closed]

    ema19 = unit_4_ema_v4(prices, 19)
    ema50 = unit_4_ema_v4(prices, 50)
    ema100 = unit_4_ema_v4(prices, 100)
    ema200 = unit_4_ema_v4(prices, 200)

    separation_pct = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    latest = closed[-1]
    previous = closed[-2]

    latest_close = latest["close"]
    previous_close = previous["close"]

    moves = {}

    for minutes in (1, 5, 15, 30, 60, 120):

        reference = prices[-minutes - 1]

        moves[minutes] = (
            (latest_close - reference)
            / reference * 100.0
        )

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"
    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"
    else:
        ema_structure = "MIXED"

    # ========================================================
    # 3. ATR14 FROM VERIFIED CLOSED CANDLES
    # ========================================================

    ranges = []

    for i in range(1, len(closed)):

        candle = closed[i]
        prior_close = closed[i - 1]["close"]

        true_range = max(
            candle["high"] - candle["low"],
            abs(candle["high"] - prior_close),
            abs(candle["low"] - prior_close)
        )

        ranges.append(true_range)

    atr14 = sum(ranges[-14:]) / 14.0

    if atr14 <= 0:
        raise RuntimeError(
            "UNIT 4 INVALID ATR14"
        )

    atr_percent = (
        atr14 / latest_close * 100.0
    )

    # ========================================================
    # 4. DIRECTION VOTES
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

    votes = (
        ema_vote,
        momentum_vote,
        price_vote
    )

    long_votes = votes.count("LONG")
    short_votes = votes.count("SHORT")

    votes_required = int(
        common["direction_votes_required"]
    )

    direction_evidence = "NONE"

    if (
        long_votes >= votes_required
        and long_votes > short_votes
    ):
        direction_evidence = "LONG"

    elif (
        short_votes >= votes_required
        and short_votes > long_votes
    ):
        direction_evidence = "SHORT"

    # ========================================================
    # 5. SUPPORT, RESISTANCE, BREAKOUT
    # ========================================================

    lookback = int(
        breakout["support_resistance_lookback"]
    )

    if not 2 <= lookback <= 45:
        raise RuntimeError(
            "UNIT 4 INVALID BREAKOUT LOOKBACK"
        )

    previous_range = closed[-lookback - 1:-1]

    support = min(
        candle["low"] for candle in previous_range
    )

    resistance = max(
        candle["high"] for candle in previous_range
    )

    proximity = unit_4_number_v4(
        breakout["developing_proximity_atr"],
        "BREAKOUT PROXIMITY"
    )

    confirmation = unit_4_number_v4(
        breakout["confirmation_distance_atr"],
        "BREAKOUT CONFIRMATION"
    )

    max_breakout_extension = unit_4_number_v4(
        breakout["max_price_extension_atr"],
        "BREAKOUT MAX EXTENSION"
    )

    long_extension = max(
        0.0,
        (latest_close - resistance) / atr14
    )

    short_extension = max(
        0.0,
        (support - latest_close) / atr14
    )

    near_resistance = (
        latest_close
        >= resistance - proximity * atr14
    )

    near_support = (
        latest_close
        <= support + proximity * atr14
    )

    breakout_developing_long = bool(
        breakout["enabled"]
        and breakout["developing_candidate_enabled"]
        and near_resistance
        and direction_evidence == "LONG"
        and moves[5] > 0
        and long_extension <= max_breakout_extension
    )

    breakout_developing_short = bool(
        breakout["enabled"]
        and breakout["developing_candidate_enabled"]
        and near_support
        and direction_evidence == "SHORT"
        and moves[5] < 0
        and short_extension <= max_breakout_extension
    )

    breakout_confirmed_long = bool(
        breakout["enabled"]
        and latest_close
        > resistance + confirmation * atr14
        and long_extension <= max_breakout_extension
    )

    breakout_confirmed_short = bool(
        breakout["enabled"]
        and latest_close
        < support - confirmation * atr14
        and short_extension <= max_breakout_extension
    )

    range20_atr_ratio = (
        resistance - support
    ) / atr14

    # ========================================================
    # 6. STRUCTURE DEVELOPING EVIDENCE
    # ========================================================

    minimum_separation = unit_4_number_v4(
        structure["minimum_ema_separation_percent"],
        "STRUCTURE MINIMUM SEPARATION"
    )

    pullback_atr = unit_4_number_v4(
        structure["pullback_tolerance_atr"],
        "STRUCTURE PULLBACK"
    )

    max_structure_extension = unit_4_number_v4(
        structure["max_price_extension_atr"],
        "STRUCTURE MAX EXTENSION"
    )

    ema_distance_atr = (
        latest_close - ema19
    ) / atr14

    near_ema = (
        abs(ema_distance_atr) <= pullback_atr
    )

    separation_ok = (
        separation_pct >= minimum_separation
    )

    structure_developing_long = bool(
        structure["enabled"]
        and separation_ok
        and ema19 > ema50 > ema200
        and direction_evidence == "LONG"
        and moves[15] > 0
        and 0 <= ema_distance_atr
        <= max_structure_extension
        and (
            near_ema
            or structure["allow_continuation_entry"]
        )
    )

    structure_developing_short = bool(
        structure["enabled"]
        and separation_ok
        and ema19 < ema50 < ema200
        and direction_evidence == "SHORT"
        and moves[15] < 0
        and 0 <= -ema_distance_atr
        <= max_structure_extension
        and (
            near_ema
            or structure["allow_continuation_entry"]
        )
    )

    # ========================================================
    # 7. SIDEWAYS MARKET AND OVEREXTENSION
    # ========================================================

    ema_cluster_height = (
        max(ema19, ema50, ema100, ema200)
        - min(ema19, ema50, ema100, ema200)
    )

    compression_atr = (
        ema_cluster_height / atr14
    )

    price_extension_cluster = (
        abs(latest_close - ema19)
        / max(ema_cluster_height, atr14 * 0.01)
    )

    momentum15_atr_ratio = (
        abs(latest_close - prices[-16]) / atr14
    )

    # For entry safety use actual ATR extension.
    # Do not automatically reject a trend merely
    # because a compressed EMA cluster was crossed.

    price_overextended = bool(
        abs(ema_distance_atr)
        > max_structure_extension
    )

    sideways_candidate = bool(
        scalp["enabled"]
        and compression_atr <= unit_4_number_v4(
            scalp["ema_compression_atr_max"],
            "SCALP COMPRESSION"
        )
        and range20_atr_ratio <= unit_4_number_v4(
            scalp["range20_atr_max"],
            "SCALP RANGE"
        )
        and momentum15_atr_ratio <= unit_4_number_v4(
            scalp["momentum15_atr_multiplier_max"],
            "SCALP MOMENTUM"
        )
        and not (
            breakout_developing_long
            or breakout_developing_short
            or structure_developing_long
            or structure_developing_short
        )
    )

    # ========================================================
    # 8. ORIGINAL SNAPSHOT + HYBRID EVIDENCE
    # PRESERVE UNIT 5 INPUT FIELD NAMES
    # ========================================================

    result = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": live_mark_price,
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

        "ema19_50_separation_pct":
            separation_pct,

        "short_term_move_pct": moves[1],

        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "ema_structure": ema_structure,

        "recent_closed_klines": [
            dict(candle)
            for candle in closed[-60:]
        ],

        "candle_count": len(candles),
        "closed_candle_count": len(closed),

        "newest_returned_candle_closed": (
            candles[-1]["close_time_ms"]
            <= market_time_ms
        ),

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only": True,

        # Hybrid evidence fields

        "atr14": atr14,
        "atr_percent": atr_percent,

        "support20": support,
        "resistance20": resistance,
        "range20_atr_ratio": range20_atr_ratio,

        "near_resistance": bool(near_resistance),
        "near_support": bool(near_support),

        "breakout_developing_long":
            breakout_developing_long,

        "breakout_developing_short":
            breakout_developing_short,

        "breakout_confirmed_long":
            breakout_confirmed_long,

        "breakout_confirmed_short":
            breakout_confirmed_short,

        "structure_developing_long":
            structure_developing_long,

        "structure_developing_short":
            structure_developing_short,

        "sideways_candidate": sideways_candidate,

        "direction_long_votes": long_votes,
        "direction_short_votes": short_votes,
        "direction_evidence": direction_evidence,

        "ema_cluster_height": ema_cluster_height,
        "ema_compression_atr": compression_atr,

        "price_extension_cluster":
            price_extension_cluster,

        "price_overextended": price_overextended,

        "strategy_evidence_version":
            "U4_HYBRID_V2",

        "qualification_settings": {
            "breakout_lookback": lookback,
            "breakout_proximity_atr": proximity,
            "breakout_confirmation_atr": confirmation,
            "structure_pullback_atr": pullback_atr,
            "structure_max_extension_atr":
                max_structure_extension,

            "scalp_compression_atr":
                scalp["ema_compression_atr_max"],

            "scalp_range_atr":
                scalp["range20_atr_max"],

            "scalp_momentum_atr":
                scalp["momentum15_atr_multiplier_max"],
        },

        "trade_authorized": False,
        "order_payload_created": False,
    }

    # ========================================================
    # 9. VERIFY UNIT 5 REQUIRED INPUT CONTRACT
    # ========================================================

    required = (
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
    )

    missing = [
        key for key in required
        if key not in result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 4 TO UNIT 5 HANDOVER INCOMPLETE: "
            + str(missing)
        )

    print(
        "UNIT 4 HTTP STATUS =",
        status,
        flush=True
    )

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

    print(
        "UNIT 4 ATR14 =",
        round(atr14, 4),
        flush=True
    )

    print(
        "UNIT 4 DIRECTION =",
        direction_evidence,
        flush=True
    )

    print(
        "UNIT 4 DIRECTION VOTES LONG/SHORT =",
        long_votes,
        "/",
        short_votes,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT CONFIRMED LONG =",
        breakout_confirmed_long,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT CONFIRMED SHORT =",
        breakout_confirmed_short,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT DEVELOPING LONG =",
        breakout_developing_long,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT DEVELOPING SHORT =",
        breakout_developing_short,
        flush=True
    )

    print(
        "UNIT 4 STRUCTURE DEVELOPING LONG =",
        structure_developing_long,
        flush=True
    )

    print(
        "UNIT 4 STRUCTURE DEVELOPING SHORT =",
        structure_developing_short,
        flush=True
    )

    print(
        "UNIT 4 SIDEWAYS CANDIDATE =",
        sideways_candidate,
        flush=True
    )

    print(
        "UNIT 4 PRICE OVEREXTENDED =",
        price_overextended,
        flush=True
    )

    print(
        "UNIT 4 STRATEGY EVIDENCE VERSION =",
        result["strategy_evidence_version"],
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

    print(
        "FRESH RECONSTRUCTION UNIT 4 ADAPTER RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# SINGLE EXECUTION CALL
# NO SEPARATE ADAPTER FUNCTION REQUIRED
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END COMPLETE UNIT 4 + HYBRID ADAPTER V4
# UNIT 5 V6 FOLLOWS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 5 REPLACEMENT V7
# WEEX DEMO HYBRID SIGNAL CLASSIFICATION
# SINGLE INTEGRATED CORE + VALIDATION + HANDOVER
# BREAKOUT > STRUCTURE > SCALP
# ZERO INDENTATION
# NO EXCHANGE ORDER SUBMISSION
# ============================================================

import math


# ============================================================
# 5.1 NUMERIC AND DIRECTION HELPERS
# ============================================================

def unit_5_v7_number(value, name):

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
            "UNIT 5 NONFINITE NUMBER: " + name
        )

    return result


def unit_5_v7_direction(value):

    if value > 0:
        return "LONG"

    if value < 0:
        return "SHORT"

    return "NONE"


# ============================================================
# 5.2 COMPLETE CLASSIFICATION ENGINE
# ============================================================

def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot
):

    print("=" * 80, flush=True)
    print(
        "UNIT 5 COMPLETE INTEGRATED V7 START",
        flush=True
    )

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 5 INVALID UNIT 2 CONFIG"
        )

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError(
            "UNIT 5 INVALID UNIT 4 SNAPSHOT"
        )

    config = unit_2_config
    analysis = unit_4_snapshot

    qualification = config.get("qualification", {})

    if not isinstance(qualification, dict):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION CONFIG MISSING"
        )

    common = qualification.get("common", {})
    breakout = qualification.get("breakout", {})
    structure = qualification.get("structure", {})
    scalp = qualification.get("scalp", {})

    if not all(
        isinstance(item, dict)
        for item in (
            common,
            breakout,
            structure,
            scalp
        )
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION SETTINGS INVALID"
        )

    if tuple(common.get("mode_priority", ())) != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        raise RuntimeError(
            "UNIT 5 MODE PRIORITY INVALID"
        )

    if analysis.get("strategy_evidence_version") != (
        "U4_HYBRID_V2"
    ):
        raise RuntimeError(
            "UNIT 5 UNIT 4 HYBRID EVIDENCE MISSING"
        )

    if (
        analysis.get("exchange") != "WEEX"
        or analysis.get("api_version") != "V3"
        or analysis.get("symbol") != "BTCUSDT"
        or analysis.get("price_type") != "MARK"
    ):
        raise RuntimeError(
            "UNIT 5 MARKET CONTRACT INVALID"
        )

    def number(key):
        return unit_5_v7_number(
            analysis.get(key),
            key
        )

    def flag(key):

        value = analysis.get(key)

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 5 INVALID EVIDENCE FLAG: " + key
            )

        return value

    # ========================================================
    # 5.3 VERIFY FRESH CANDLE EVIDENCE
    # ========================================================

    exchange_ms = number("exchange_time_ms")
    close_ms = number("latest_close_time_ms")

    candle_age = (
        exchange_ms - close_ms
    ) / 1000.0

    market_policy = (
        config.get("market_data_policy") or {}
    )

    if not isinstance(market_policy, dict):
        raise RuntimeError(
            "UNIT 5 INVALID MARKET POLICY"
        )

    max_age = unit_5_v7_number(
        market_policy.get(
            "max_market_age_seconds", 120.0
        ),
        "MAX CANDLE AGE"
    )

    if not 0 <= candle_age <= max_age:
        raise RuntimeError(
            "UNIT 5 STALE CANDLE EVIDENCE"
        )

    if analysis.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 5 INVALID ANALYSIS CONTRACT"
        )

    # ========================================================
    # 5.4 READ MARKET DATA
    # ========================================================

    live_price = number("live_mark_price")
    previous_close = number("previous_close")
    latest_close = number("latest_close")

    ema19 = number("ema19")
    ema50 = number("ema50")
    ema200 = number("ema200")

    separation = abs(
        number("ema19_50_separation_pct")
    )

    atr14 = number("atr14")

    if min(
        live_price,
        previous_close,
        latest_close,
        ema19,
        ema50,
        ema200,
        atr14
    ) <= 0:
        raise RuntimeError(
            "UNIT 5 INVALID MARKET PRICES OR ATR"
        )

    periods = (1, 5, 15, 30, 60, 120)

    moves = {
        period: number(
            "move_%dm_pct" % period
        )
        for period in periods
    }

    directions = {
        period: unit_5_v7_direction(moves[period])
        for period in periods
    }

    short_move = number("short_term_move_pct")

    ema_structure = str(
        analysis.get("ema_structure", "MIXED")
    ).upper()

    if ema_structure not in (
        "BULLISH",
        "BEARISH",
        "MIXED"
    ):
        raise RuntimeError(
            "UNIT 5 INVALID EMA STRUCTURE"
        )

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
            "UNIT 5 EMA STRUCTURE CONTRADICTION"
        )

    # ========================================================
    # 5.5 READ HYBRID STRATEGY EVIDENCE
    # ========================================================

    b_long = flag("breakout_confirmed_long")
    b_short = flag("breakout_confirmed_short")

    bd_long = flag("breakout_developing_long")
    bd_short = flag("breakout_developing_short")

    sd_long = flag("structure_developing_long")
    sd_short = flag("structure_developing_short")

    sideways = flag("sideways_candidate")
    overextended = flag("price_overextended")

    if b_long and b_short:
        raise RuntimeError(
            "UNIT 5 CONFLICTING BREAKOUT SIGNALS"
        )

    direction_evidence = str(
        analysis.get("direction_evidence", "NONE")
    ).upper()

    if direction_evidence not in (
        "LONG",
        "SHORT",
        "NONE"
    ):
        raise RuntimeError(
            "UNIT 5 INVALID DIRECTION EVIDENCE"
        )

    long_votes = number("direction_long_votes")
    short_votes = number("direction_short_votes")

    votes_required = unit_5_v7_number(
        common.get(
            "direction_votes_required", 2
        ),
        "DIRECTION VOTES REQUIRED"
    )

    if (
        votes_required < 1
        or long_votes < 0
        or short_votes < 0
    ):
        raise RuntimeError(
            "UNIT 5 INVALID DIRECTION VOTES"
        )

    # ========================================================
    # 5.6 ORIGINAL 42-FIELD SIGNAL CONTEXT
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
            directions[5],
            directions[15]
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
    # 5.7 ACTUAL BREAKOUT QUALIFICATION
    # ========================================================

    breakout_side = (
        "LONG" if b_long
        else "SHORT" if b_short
        else "NONE"
    )

    breakout_votes = (
        long_votes if breakout_side == "LONG"
        else short_votes if breakout_side == "SHORT"
        else 0
    )

    breakout_qualified = bool(
        breakout.get("enabled") is True
        and breakout_side in ("LONG", "SHORT")
        and direction_evidence == breakout_side
        and breakout_votes >= votes_required
        and not overextended
    )

    # ========================================================
    # 5.8 STRUCTURE QUALIFICATION
    # ========================================================

    trend_side = ema_direction

    trend_votes = (
        long_votes if trend_side == "LONG"
        else short_votes if trend_side == "SHORT"
        else 0
    )

    momentum_agreement = (
        moves[5] > 0 and moves[15] > 0
        if trend_side == "LONG"
        else moves[5] < 0 and moves[15] < 0
        if trend_side == "SHORT"
        else False
    )

    developing_structure_same_side = (
        sd_long if trend_side == "LONG"
        else sd_short if trend_side == "SHORT"
        else False
    )

    extension_atr = (
        abs(latest_close - ema19) / atr14
    )

    max_extension = unit_5_v7_number(
        structure.get(
            "max_price_extension_atr", 2.0
        ),
        "STRUCTURE MAX EXTENSION"
    )

    structure_qualified = bool(
        structure.get("enabled") is True
        and trend_side in ("LONG", "SHORT")
        and direction_evidence == trend_side
        and trend_votes >= votes_required
        and momentum_agreement
        and developing_structure_same_side
        and extension_atr <= max_extension
        and not overextended
    )

    # ========================================================
    # 5.9 SCALP CONTEXT
    # QUALIFICATION BELONGS TO UNIT 6
    # ========================================================

    original_scalp_signal = (
        scalp_direction in ("LONG", "SHORT")
        and (
            separation >= 0.03
            and scalp_move >= 0.015
        )
    )

    price_first_scalp_signal = (
        directions[5] in ("LONG", "SHORT")
        and abs(moves[5]) >= 0.015
        and directions[1] == directions[5]
    )

    scalp_direction_candidate = scalp_direction

    if (
        scalp_direction_candidate == "NONE"
        and price_first_scalp_signal
    ):
        scalp_direction_candidate = directions[5]

    scalp_preliminary = bool(
        scalp.get("enabled") is True
        and (
            original_scalp_signal
            or price_first_scalp_signal
        )
        and scalp_direction_candidate in (
            "LONG", "SHORT"
        )
    )

    # ========================================================
    # 5.10 DEVELOPING SIGNAL ARBITRATION
    # ========================================================

    breakout_developing = (
        bd_long or bd_short
    )

    structure_developing = (
        sd_long or sd_short
    )

    higher_mode_developing = (
        breakout_developing
        or structure_developing
    )

    # These are diagnostic candidate directions.
    # Active direction remains NONE until qualified.

    developing_breakout_direction = (
        "LONG" if bd_long and not bd_short
        else "SHORT" if bd_short and not bd_long
        else "NONE"
    )

    developing_structure_direction = (
        "LONG" if sd_long and not sd_short
        else "SHORT" if sd_short and not sd_long
        else "NONE"
    )

    qualified = False

    active_mode = "NONE"
    direction = "NONE"

    candidate_mode = "NONE"
    candidate_stage = "NONE"

    reason = "NO_ACCEPTABLE_CANDIDATE"
    source = "HYBRID_V7"

    breakout_ready = False
    structure_ready = False
    scalp_ready = False

    # A confirmed breakout has highest priority.

    if breakout_qualified:

        qualified = True
        active_mode = "BREAKOUT"
        direction = breakout_side

        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"

        breakout_ready = True

        reason = "HYBRID_BREAKOUT_CONFIRMED"

    # Independently qualified structure is not
    # blocked by a merely developing breakout.

    elif structure_qualified:

        qualified = True
        active_mode = "STRUCTURE"
        direction = trend_side

        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"

        structure_ready = True

        reason = "HYBRID_STRUCTURE_QUALIFIED"

    # Developing signals remain unqualified.

    elif breakout_developing:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"

        reason = "BREAKOUT_DEVELOPING_PROTECTED"

    elif structure_developing:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"

        reason = "STRUCTURE_DEVELOPING_PROTECTED"

    # SCALP cannot compete with any promising
    # higher-priority developing candidate.
    # Even here, Unit 6 decides fee/quality admission.

    elif scalp_preliminary and sideways:

        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"

        scalp_ready = True

        reason = "SCALP_SIDEWAYS_PENDING_UNIT_6"

    elif scalp_preliminary and not sideways:

        candidate_stage = "REJECTED"

        reason = "SCALP_NOT_SIDEWAYS_MARKET"

    # ========================================================
    # 5.11 FEE ESTIMATE FOR UNIT 6
    # ========================================================

    fee_sides = (
        int(scalp.get("include_entry_fee") is True)
        + int(scalp.get("include_exit_fee") is True)
    )

    round_trip_fee = (
        unit_5_v7_number(
            scalp.get(
                "estimated_taker_fee_percent", 0.08
            ),
            "TAKER FEE"
        ) * fee_sides
        + unit_5_v7_number(
            scalp.get(
                "estimated_slippage_percent", 0.0
            ),
            "SLIPPAGE"
        )
    )

    # ========================================================
    # 5.12 ORIGINAL 42-FIELD OUTPUT CONTRACT
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
            "UNIT 5 ORIGINAL 42 FIELD CONTRACT FAILED"
        )

    # ========================================================
    # 5.13 UNIT 6 HYBRID HANDOVER
    # ========================================================

    candidate.update({

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "breakout_candidate": (
            breakout_qualified
            or breakout_developing
        ),

        "structure_candidate": (
            structure_qualified
            or structure_developing
        ),

        "breakout_ready": breakout_ready,
        "structure_ready": structure_ready,
        "scalp_ready": scalp_ready,

        "sideways_context": sideways,
        "direction_evidence": direction_evidence,

        "scalp_quality_minimum":
            unit_5_v7_number(
                scalp.get("quality_threshold", 70),
                "SCALP THRESHOLD"
            ),

        "scalp_price_weight_percent":
            unit_5_v7_number(
                scalp.get(
                    "price_action_weight_percent", 50
                ),
                "SCALP PRICE WEIGHT"
            ),

        "estimated_round_trip_fee_pct":
            round_trip_fee,

        "scalp_minimum_fee_coverage":
            unit_5_v7_number(
                scalp.get(
                    "minimum_fee_coverage_multiplier", 2
                ),
                "FEE COVERAGE"
            ),

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

        "classification_source": source,

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
            else trend_side if structure_qualified
            else scalp_direction_candidate
            if scalp_preliminary
            else "NONE"
        ),

        "original_unit5_reason":
            "INTEGRATED_V7_CLASSIFIER",

        "original_hybrid_conflict": False,

        "optimization_version": "UNIT5_V7",

        "hybrid_structure_qualified":
            structure_qualified,

        "hybrid_breakout_qualified":
            breakout_qualified,

        "structure_direction_votes":
            trend_votes,

        "structure_extension_atr":
            extension_atr,

        "structure_extension_pass":
            extension_atr <= max_extension,

        "structure_momentum_agreement":
            momentum_agreement,

        "breakout_confirmation_votes":
            breakout_votes,

        "developing_breakout_direction":
            developing_breakout_direction,

        "developing_structure_direction":
            developing_structure_direction,

        "scalp_preliminary":
            scalp_preliminary,
    })

    # ========================================================
    # 5.14 FINAL CONTRACT CHECKS
    # ========================================================

    if qualified != (
        candidate_stage == "QUALIFIED"
    ):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION CONTRADICTION"
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
            "UNIT 5 INVALID QUALIFIED CANDIDATE"
        )

    if (
        candidate_mode == "SCALP"
        and (
            higher_mode_developing
            or not sideways
        )
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PRIORITY VIOLATION"
        )

    if (
        candidate["trade_authorized"] is not False
        or candidate["order_payload_created"]
        is not False
    ):
        raise RuntimeError(
            "UNIT 5 EXECUTION BOUNDARY VIOLATION"
        )

    # ========================================================
    # 5.15 RENDER REPORT
    # ========================================================

    print(
        "UNIT 5 ORIGINAL FIELDS = 42",
        flush=True
    )

    print(
        "UNIT 5 EVIDENCE VERSION =",
        candidate["strategy_evidence_version"],
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
        "UNIT 5 LONG / SHORT VOTES =",
        long_votes,
        "/",
        short_votes,
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
        "UNIT 5 SIDEWAYS =",
        sideways,
        flush=True
    )

    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
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
        "UNIT 5 OPTIMIZATION V7 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return candidate


# ============================================================
# 5.16 DETERMINISTIC TESTS
# TEST THE COMPLETE CLASSIFIER, NOT A MISSING ADAPTER
# ============================================================

def unit_5_validation_v7():

    print("=" * 80, flush=True)
    print("UNIT 5 VALIDATION V7 START", flush=True)

    test_config = {
        "qualification": {
            "common": {
                "mode_priority": (
                    "BREAKOUT",
                    "STRUCTURE",
                    "SCALP"
                ),
                "direction_votes_required": 2,
            },

            "breakout": {
                "enabled": True,
            },

            "structure": {
                "enabled": True,
                "max_price_extension_atr": 2.0,
            },

            "scalp": {
                "enabled": True,
                "quality_threshold": 70,
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

            "exchange_time_ms": 1800000060000,
            "latest_close_time_ms": 1800000000000,

            "live_mark_price": 80100.0,
            "previous_close": 80090.0,
            "latest_close": 80100.0,

            "ema19": 80080.0,
            "ema50": 80020.0,
            "ema200": 79900.0,

            "ema19_50_separation_pct": 0.075,
            "ema_structure": "BULLISH",

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

            "sideways_candidate": False,
            "price_overextended": False,
        }

        data.update(changes)

        return data

    tests = (
        (
            "STRUCTURE LONG",
            market(),
            "STRUCTURE",
            "QUALIFIED",
        ),
        (
            "STRUCTURE BEATS DEVELOPING BREAKOUT",
            market(breakout_developing_long=True),
            "STRUCTURE",
            "QUALIFIED",
        ),
        (
            "CONFIRMED BREAKOUT PRIORITY",
            market(breakout_confirmed_long=True),
            "BREAKOUT",
            "QUALIFIED",
        ),
        (
            "BREAKOUT DEVELOPING",
            market(
                breakout_developing_long=True,
                structure_developing_long=False,
            ),
            "BREAKOUT",
            "DEVELOPING",
        ),
        (
            "STRUCTURE DEVELOPING",
            market(
                move_5m_pct=-0.02,
            ),
            "STRUCTURE",
            "DEVELOPING",
        ),
        (
            "OVEREXTENDED REJECTED",
            market(
                price_overextended=True,
                structure_developing_long=False,
            ),
            "NONE",
            "REJECTED",
        ),
        (
            "STRUCTURE SHORT",
            market(
                live_mark_price=79900.0,
                previous_close=79910.0,
                latest_close=79900.0,

                ema19=79920.0,
                ema50=79980.0,
                ema200=80100.0,

                ema_structure="BEARISH",

                short_term_move_pct=-0.02,
                move_1m_pct=-0.02,
                move_5m_pct=-0.05,
                move_15m_pct=-0.12,
                move_30m_pct=-0.15,
                move_60m_pct=-0.25,
                move_120m_pct=-0.30,

                direction_evidence="SHORT",
                direction_long_votes=0,
                direction_short_votes=3,

                structure_developing_long=False,
                structure_developing_short=True,
            ),
            "STRUCTURE",
            "QUALIFIED",
        ),
        (
            "SCALP SIDEWAYS PENDING",
            market(
                ema19=80080.0,
                ema50=80090.0,
                ema200=80085.0,
                ema_structure="MIXED",

                structure_developing_long=False,
                sideways_candidate=True,
            ),
            "SCALP",
            "PENDING_UNIT_6",
        ),
    )

    passed = 0
    failed = 0

    for (
        test_name,
        snapshot,
        expected_mode,
        expected_stage
    ) in tests:

        try:
            result = fresh_reconstruction_unit_5(
                test_config,
                snapshot
            )

            success = (
                result["candidate_mode"]
                == expected_mode
                and result["candidate_stage"]
                == expected_stage
                and result["trade_authorized"] is False
                and result["strategy_evidence_version"]
                == "U5_HYBRID_ADJUSTABLE_V3"
            )

        except Exception as exc:

            success = False

            print(
                "UNIT 5 TEST EXCEPTION =",
                str(exc),
                flush=True
            )

        if success:
            passed += 1
        else:
            failed += 1

        print(
            "UNIT 5 TEST:",
            test_name,
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
            "UNIT 5 VALIDATION V7 FAILED"
        )

    print(
        "UNIT 5 VALIDATION V7 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return True


# ============================================================
# 5.17 SINGLE EXECUTION SEQUENCE
# VALIDATION -> LIVE CLASSIFICATION -> UNIT 6
# ============================================================

FRESH_UNIT_5_VALIDATION_READY = (
    unit_5_validation_v7()
)

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    )
)


# ============================================================
# END COMPLETE UNIT 5 REPLACEMENT V7
# UNIT 6 FOLLOWS
# ZERO INDENTATION
# ============================================================

