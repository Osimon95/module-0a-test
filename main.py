
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
# START UNIT 4 OPTIMIZED CORE V3
# WEEX V3 CLOSED-CANDLE MARKET ANALYSIS
# PRESERVES ORIGINAL UNIT 4 OUTPUT CONTRACT
# ZERO INDENTATION
# ============================================================

import math
import time


def unit_4_validate_candles_v3(raw_klines, exchange_time_ms):

    if not isinstance(raw_klines, list):
        raise RuntimeError(
            "UNIT 4 INVALID KLINE RESPONSE TYPE"
        )

    if len(raw_klines) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT RETURNED KLINES"
        )

    candles = []

    for raw in raw_klines:

        if not isinstance(raw, (list, tuple)):
            raise RuntimeError("UNIT 4 INVALID CANDLE")

        if len(raw) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE CANDLE"
            )

        try:
            candle = {
                "open_time_ms": int(raw[0]),
                "open": float(raw[1]),
                "high": float(raw[2]),
                "low": float(raw[3]),
                "close": float(raw[4]),
                "volume": float(raw[5]),
                "close_time_ms": int(raw[6]),
            }

        except (TypeError, ValueError, OverflowError) as exc:
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE VALUE"
            ) from exc

        prices = (
            candle["open"],
            candle["high"],
            candle["low"],
            candle["close"],
        )

        if not all(
            math.isfinite(value) and value > 0
            for value in prices
        ):
            raise RuntimeError(
                "UNIT 4 INVALID NONFINITE CANDLE PRICE"
            )

        if (
            not math.isfinite(candle["volume"])
            or candle["volume"] < 0
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE VOLUME"
            )

        if not (
            candle["low"]
            <= min(candle["open"], candle["close"])
            <= max(candle["open"], candle["close"])
            <= candle["high"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID OHLC RELATIONSHIP"
            )

        if (
            candle["open_time_ms"] <= 0
            or candle["close_time_ms"]
            <= candle["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE TIME"
            )

        candles.append(candle)

    candles.sort(
        key=lambda item: item["open_time_ms"]
    )

    for index in range(1, len(candles)):

        difference = (
            candles[index]["open_time_ms"]
            - candles[index - 1]["open_time_ms"]
        )

        if difference != 60000:
            raise RuntimeError(
                "UNIT 4 DUPLICATE OR MISSING 1M CANDLE"
            )

    closed = [
        candle for candle in candles
        if candle["close_time_ms"]
        <= exchange_time_ms
    ]

    if len(closed) < 200:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED CANDLES"
        )

    latest_closed = closed[-1]

    age_ms = (
        exchange_time_ms
        - latest_closed["close_time_ms"]
    )

    if age_ms < 0 or age_ms > 120000:
        raise RuntimeError(
            "UNIT 4 STALE CLOSED CANDLE"
        )

    return candles, closed


def unit_4_calculate_ema_v3(prices, period):

    if len(prices) < period:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT EMA HISTORY"
        )

    value = sum(prices[:period]) / period
    multiplier = 2.0 / (period + 1.0)

    for price in prices[period:]:
        value = (
            price * multiplier
            + value * (1.0 - multiplier)
        )

    if not math.isfinite(value) or value <= 0:
        raise RuntimeError(
            "UNIT 4 INVALID EMA RESULT"
        )

    return float(value)


def fresh_reconstruction_unit_4():

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 4 START")

    config = FRESH_RECONSTRUCTION_CONFIG
    snapshot = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 4 INVALID UNIT 2 CONFIG"
        )

    if not isinstance(snapshot, dict):
        raise RuntimeError(
            "UNIT 4 INVALID UNIT 3 SNAPSHOT"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 4 EXCHANGE CONFIG INVALID"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 4 SAFETY CONFIG INVALID"
        )

    if (
        snapshot.get("exchange") != "WEEX"
        or snapshot.get("api_version") != "V3"
        or snapshot.get("symbol") != "BTCUSDT"
        or snapshot.get("price_type") != "MARK"
        or snapshot.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 3 SNAPSHOT CONTRACT FAILED"
        )

    if (
        config.get("execution_environment") != "DEMO"
        or exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
    ):
        raise RuntimeError(
            "UNIT 4 UNIT 2 CONTRACT FAILED"
        )

    if (
        safety.get("public_market_data_read_enabled")
        is not True
    ):
        raise RuntimeError(
            "UNIT 4 PUBLIC MARKET READ DISABLED"
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
                "UNIT 4 UNSAFE CONFIGURATION: " + key
            )

    exchange_time_ms = int(
        snapshot["exchange_time_ms"]
    )

    live_mark_price = float(
        snapshot["price"]
    )

    if (
        not math.isfinite(live_mark_price)
        or live_mark_price <= 0
        or exchange_time_ms <= 0
    ):
        raise RuntimeError(
            "UNIT 4 INVALID UNIT 3 MARKET DATA"
        )

    # Verify that the Unit 3 observation is still fresh
    # before retrieving new candle data.

    now_ms = int(time.time() * 1000)

    if (
        exchange_time_ms < now_ms - 120000
        or exchange_time_ms > now_ms + 15000
    ):
        raise RuntimeError(
            "UNIT 4 STALE UNIT 3 SNAPSHOT"
        )

    base_url = exchange.get("contract_base_url")

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 INVALID CONTRACT BASE URL"
        )

    interval = "1m"
    candle_limit = 300

    endpoint = "/capi/v3/market/markPriceKlines"

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "interval": interval,
        "limit": candle_limit,
    })

    url = base_url + endpoint + "?" + query

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Hybrid-Unit4-V3",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 4 NON-READ-ONLY REQUEST"
        )

    start = time.monotonic()

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()
            raw_body = (
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:

        error_body = ""

        try:
            error_body = (
                exc.read().decode("utf-8")
            )
        except Exception:
            pass

        print(
            "UNIT 4 HTTP ERROR BODY =",
            error_body[:500],
            flush=True
        )

        raise RuntimeError(
            "UNIT 4 WEEX KLINE HTTP ERROR"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "UNIT 4 WEEX KLINE CONNECTION FAILED"
        ) from exc

    latency_ms = (
        time.monotonic() - start
    ) * 1000.0

    if http_status != 200 or not raw_body:
        raise RuntimeError(
            "UNIT 4 INVALID KLINE HTTP RESPONSE"
        )

    try:
        raw_klines = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "UNIT 4 INVALID KLINE JSON"
        ) from exc

    # Use the validated Unit 3 exchange timestamp
    # as the authoritative candle-closing boundary.

    candles, closed = unit_4_validate_candles_v3(
        raw_klines,
        exchange_time_ms
    )

    close_prices = [
        candle["close"] for candle in closed
    ]

    ema19 = unit_4_calculate_ema_v3(
        close_prices, 19
    )
    ema50 = unit_4_calculate_ema_v3(
        close_prices, 50
    )
    ema100 = unit_4_calculate_ema_v3(
        close_prices, 100
    )
    ema200 = unit_4_calculate_ema_v3(
        close_prices, 200
    )

    ema_separation = (
        abs(ema19 - ema50) / ema50 * 100.0
    )

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"
    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"
    else:
        ema_structure = "MIXED"

    latest = closed[-1]
    previous = closed[-2]

    latest_close = latest["close"]
    previous_close = previous["close"]

    movements = {}

    for minutes in (1, 5, 15, 30, 60, 120):

        reference = close_prices[-(minutes + 1)]

        movements[minutes] = (
            (latest_close - reference)
            / reference * 100.0
        )

    short_term_move_pct = movements[1]

    newest_returned_is_closed = (
        candles[-1]["close_time_ms"]
        <= exchange_time_ms
    )

    # ========================================================
    # PRESERVED ORIGINAL UNIT 4 OUTPUT CONTRACT
    # ========================================================

    analysis_snapshot = {
        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "interval": interval,
        "price_type": "MARK",
        "live_mark_price": live_mark_price,
        "previous_close": previous_close,
        "latest_close": latest_close,
        "latest_open_time_ms":
            latest["open_time_ms"],
        "latest_close_time_ms":
            latest["close_time_ms"],
        "exchange_time_ms": exchange_time_ms,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,
        "ema19_50_separation_pct": ema_separation,

        "short_term_move_pct": short_term_move_pct,

        "move_1m_pct": movements[1],
        "move_5m_pct": movements[5],
        "move_15m_pct": movements[15],
        "move_30m_pct": movements[30],
        "move_60m_pct": movements[60],
        "move_120m_pct": movements[120],

        "ema_structure": ema_structure,

        "recent_closed_klines": [
            dict(candle) for candle in closed[-60:]
        ],

        "candle_count": len(candles),
        "closed_candle_count": len(closed),
        "newest_returned_candle_closed":
            newest_returned_is_closed,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",
        "read_only": True,
    }

    print(
        "UNIT 4 HTTP STATUS =",
        http_status,
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
        "UNIT 4 LATEST CLOSED CANDLE AGE MS =",
        exchange_time_ms
        - latest["close_time_ms"],
        flush=True
    )
    print(
        "UNIT 4 EMA19 =",
        round(ema19, 6),
        flush=True
    )
    print(
        "UNIT 4 EMA50 =",
        round(ema50, 6),
        flush=True
    )
    print(
        "UNIT 4 EMA100 =",
        round(ema100, 6),
        flush=True
    )
    print(
        "UNIT 4 EMA200 =",
        round(ema200, 6),
        flush=True
    )
    print(
        "UNIT 4 EMA STRUCTURE =",
        ema_structure,
        flush=True
    )

    for minutes in (1, 5, 15, 30, 60, 120):
        print(
            "UNIT 4",
            str(minutes) + "M MOVE % =",
            round(movements[minutes], 6),
            flush=True
        )

    print(
        "PASS: UNIT 4 CLOSED-CANDLE VALIDATION",
        flush=True
    )
    print(
        "PASS: UNIT 4 ORIGINAL SNAPSHOT CONTRACT",
        flush=True
    )
    print(
        "PASS: UNIT 4 HANDOVER READY FOR HYBRID ADAPTER",
        flush=True
    )
    print(
        "UNIT 4 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 4 RESULT = PASS"
    )
    print("=" * 80, flush=True)

    return analysis_snapshot


# ============================================================
# RUN UNIT 4 ORIGINAL CORE
# PRESERVE ORIGINAL HANDOVER NAME
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)


# ============================================================
# END UNIT 4 OPTIMIZED CORE V3
# EXISTING UNIT 4 HYBRID ADAPTER FOLLOWS
# DO NOT DELETE THE ADAPTER
# ============================================================


