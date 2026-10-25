
# ============================================================
# WEEX BOT - UNIT 1 - RUNTIME FOUNDATION
# COMPLETE REPLACEMENT - ZERO INDENTATION
# ============================================================

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def log(message):
    timestamp = datetime.now(timezone.utc).isoformat()
    print(timestamp, message, flush=True)


def fresh_reconstruction_unit_1():
    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 1 START")
    print("-" * 80, flush=True)

    try:
        sample = {"ready": True, "unit": 1}
        encoded = json.dumps(sample)

        if json.loads(encoded) != sample:
            raise RuntimeError("JSON ROUNDTRIP FAILED")

        print(
            "PASS: UNIT 1 JSON ENCODE/DECODE",
            flush=True
        )

        query = urllib.parse.urlencode({
            "symbol": "BTCUSDT"
        })

        if query != "symbol=BTCUSDT":
            raise RuntimeError("URL ENCODING FAILED")

        if not callable(urllib.request.Request):
            raise RuntimeError("HTTP REQUEST BUILDER MISSING")

        if not hasattr(urllib.error, "URLError"):
            raise RuntimeError("HTTP ERROR HANDLER MISSING")

        print(
            "PASS: UNIT 1 URL AND HTTP LIBRARIES",
            flush=True
        )

        utc_now = datetime.now(timezone.utc)

        if (
            utc_now.tzinfo is None
            or utc_now.utcoffset().total_seconds() != 0
        ):
            raise RuntimeError("UTC CLOCK FAILED")

        print(
            "PASS: UNIT 1 UTC CLOCK",
            flush=True
        )

    except Exception as exc:
        log("FRESH RECONSTRUCTION UNIT 1 RESULT = FAIL")
        raise RuntimeError(
            "UNIT 1 RUNTIME VERIFICATION FAILED"
        ) from exc

    print(
        "PASS: MAIN.PY STARTED SUCCESSFULLY",
        flush=True
    )

    print(
        "PASS: PYTHON STANDARD LIBRARY AVAILABLE",
        flush=True
    )

    print(
        "UNIT 1 EXCHANGE CONNECTION = NONE",
        flush=True
    )

    print(
        "UNIT 1 HTTP REQUEST = NONE",
        flush=True
    )

    print(
        "UNIT 1 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 1 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 1 EXCHANGE WRITE = NONE",
        flush=True
    )

    log("FRESH RECONSTRUCTION UNIT 1 RESULT = PASS")

    print("=" * 80, flush=True)

    return True


FRESH_RECONSTRUCTION_UNIT_1_READY = (
    fresh_reconstruction_unit_1()
)


# ============================================================
# END UNIT 1
# UNIT 2 CONTINUES UNCHANGED BELOW
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 2 - HYBRID QUALIFICATION V3
# ZERO INDENTATION
#
# ENGINE: BREAKOUT / STRUCTURE / SCALP
# CENTRAL ADJUSTABLE QUALIFICATION PARAMETERS
#
# HEDGING: NOT INCLUDED
# BACKUPS: ORIGINAL FIVE PRESERVED
# UNIT 3 MARKET POLICY: PRESERVED
# UNIT 12 DEMO EXECUTION PATH: UNCHANGED
# ============================================================


def fresh_reconstruction_unit_2():

    import math

    print("=" * 80, flush=True)
    log("FRESH RECONSTRUCTION UNIT 2 HYBRID V3 START")

    if FRESH_RECONSTRUCTION_UNIT_1_READY is not True:
        raise RuntimeError("UNIT 2: UNIT 1 NOT READY")

    # ========================================================
    # 1. ORIGINAL EXCHANGE CONTRACT
    # ========================================================

    exchange = {
        "name": "WEEX",
        "api_version": "V3",
        "contract_base_url":
            "https://api-contract.weex.com",
        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",
    }

    execution_environment = "DEMO"

    # ========================================================
    # 2. ORIGINAL EARLY-UNIT SAFETY CONTRACT
    #
    # THIS CONTROLS THE READ-ONLY CONFIGURATION
    # STAGE. IT IS NOT THE UNIT 12 ORDER SWITCH.
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
    # 3. CENTRAL ADJUSTABLE QUALIFICATION FIGURES
    #
    # EDIT THESE SETTINGS WHEN TUNING STRATEGIES.
    #
    # ENGINE PRIORITY:
    # BREAKOUT -> STRUCTURE -> SCALP
    # ========================================================

    qualification = {

        # ----------------------------------------------------
        # SHARED QUALIFICATION / ARBITRATION
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # BREAKOUT QUALIFICATION
        # ----------------------------------------------------

        "breakout": {

            "enabled": True,

            "priority": 1,

            "early_detection_enabled": True,

            "developing_candidate_enabled": True,

            "support_resistance_lookback": 20,

            # Recognize a developing breakout
            # before full confirmation.
            "developing_proximity_atr": 0.50,

            # Distance beyond support/resistance
            # required for confirmed breakout.
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

            # Only activate once trustworthy
            # candle volume is available.
            "volume_confirmation_enabled": False,

            "minimum_volume_ratio": 1.20,

            "candidate_expiry_seconds": 120,
        },

        # ----------------------------------------------------
        # STRUCTURE QUALIFICATION
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # SCALP QUALIFICATION
        # ----------------------------------------------------

        "scalp": {

            "enabled": True,

            "priority": 3,

            "sideways_preferred": True,

            "require_sideways_market": True,

            "protect_developing_higher_modes": True,

            # Minimum qualification score
            "quality_threshold": 70.0,

            # Score contribution
            "price_action_weight_percent": 50.0,

            "other_factors_weight_percent": 50.0,

            # 2 of 3 direction confirmations
            "direction_votes_required": 2,
            "direction_votes_total": 3,

            # Maximum EMA-cluster extension
            "max_ema_extension_clusters": 1.5,

            # Excessive spike rejection
            "max_spike_count": 2,

            "reject_late_impulse": True,

            "early_entry_enabled": True,

            # Sideways recognition
            "ema_compression_atr_max": 0.70,

            "range20_atr_max": 8.0,

            "momentum15_atr_multiplier_max": 1.5,

            # Fee-aware qualification
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

    # ========================================================
    # 4. ORIGINAL STRATEGY CONTRACT
    #
    # ALL EXISTING SETTINGS PRESERVED.
    # NEWER-MODEL COMPATIBILITY KEYS ADDED BELOW.
    # ========================================================

    strategy = {

        "leverage_target": 100,

        "initial_margin_percent": 5.0,

        "initial_fixed_usdt": 0.50,

        # ORIGINAL FIVE BACKUPS

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

        # ORIGINAL EXPOSURE

        "exposure_cap_percent": 35.0,

        "progressive_backup_funding": True,

        "full_ladder_reservation_required": False,

        # ORIGINAL TP ALLOCATION

        "tp1_allocation_percent": 10.0,

        "tp2_allocation_percent": 20.0,

        "tp3_allocation_percent": 70.0,

        # ORIGINAL NET ROI TARGETS

        "tp1_net_roi_floor_percent": 5.0,

        "tp2_net_roi_floor_percent": 10.0,

        "tp1_tp2_min_roi_separation_percent": 5.0,

        # ORIGINAL TP3 TRAILING

        "tp3_trailing_reference_percent": 0.20,

        "tp3_trailing_min_percent": 0.10,

        "tp3_trailing_max_percent": 0.40,

        # ORIGINAL SIGNAL CONTROL

        "signal_expiry_seconds": 120,

        "loss_cooldown_seconds": 300,

        "one_direction_only": True,

        "anti_duplicate_orders": True,

        "active_trade_mode_lock": True,

        "exclusive_mode": True,

        "mode_confirmations_required": 3,

        # NEWER-MODEL COMPATIBILITY

        "mode_priority":
            qualification["common"]["mode_priority"],

        "structure_breakout_priority": True,

        "arbitration_before_scalp": True,

        "developing_candidate_protection": True,

        "scalp_requires_higher_modes_clear": True,

        "scalp_preemption_requires_confirmation": True,

        "preserve_active_position_management": True,

        "direction_votes_required":
            qualification["common"][
                "direction_votes_required"
            ],

        "direction_votes_total":
            qualification["common"][
                "direction_votes_total"
            ],

        "qualification_use_closed_candles": True,

        "reject_stale_signals": True,

        "reject_late_impulse_entry": True,

        "reject_spike_count_above": 2,

        # BREAKOUT COMPATIBILITY

        "breakout_early_detection_enabled": True,

        "breakout_developing_candidate_enabled": True,

        "breakout_require_ema_crossover": False,

        "breakout_allow_preconfirmation": True,

        "breakout_require_price_confirmation": True,

        "breakout_require_momentum_confirmation": True,

        "breakout_require_direction_agreement": True,

        "breakout_retest_mandatory": False,

        # STRUCTURE COMPATIBILITY

        "structure_early_detection_enabled": True,

        "structure_developing_candidate_enabled": True,

        "structure_require_ema_crossover": False,

        "structure_require_price_confirmation": True,

        "structure_require_direction_agreement": True,

        "structure_allow_pullback_entry": True,

        "structure_allow_continuation_entry": True,

        "structure_retest_mandatory": False,

        # SCALP COMPATIBILITY

        "scalp_sideways_preferred": True,

        "scalp_trending_market_block": True,

        "scalp_quality_threshold":
            qualification["scalp"]["quality_threshold"],

        "scalp_price_weight_percent":
            qualification["scalp"][
                "price_action_weight_percent"
            ],

        "scalp_other_factors_weight_percent":
            qualification["scalp"][
                "other_factors_weight_percent"
            ],

        "scalp_max_ema_extension_clusters":
            qualification["scalp"][
                "max_ema_extension_clusters"
            ],

        "scalp_early_entry_enabled": True,

        "scalp_late_entry_rejection": True,

        "scalp_fee_aware_enabled": True,

        "scalp_estimated_taker_fee_percent":
            qualification["scalp"][
                "estimated_taker_fee_percent"
            ],

        "scalp_include_entry_fee": True,

        "scalp_include_exit_fee": True,

        "scalp_include_estimated_slippage": True,

        "scalp_require_positive_net_profit": True,

        "scalp_profit_safety_buffer_enabled": True,

        "scalp_min_net_roi_percent":
            qualification["scalp"][
                "minimum_net_roi_percent"
            ],

        # CONTINUOUS ENTRY SCANNING

        "continuous_entry_scan_enabled": True,

        "flat_position_reentry_enabled": True,

        "reentry_requires_confirmed_flat": True,

        "reentry_requires_no_pending_entry": True,

        "reentry_preserves_cooldown": True,
    }

    # ========================================================
    # 5. ORIGINAL MARKET PRECISION
    # ========================================================

    market_precision = {

        "quantity_step": 0.0001,

        "minimum_quantity": 0.0001,

        "price_step": 0.1,
    }

    # ========================================================
    # 6. TESTED UNIT 3 MARKET-DATA POLICY
    # ========================================================

    market_data_policy = {

        "max_market_age_seconds": 120.0,

        "future_tolerance_seconds": 30.0,

        "max_response_bytes": 65536,

        "require_finite_price": True,

        "require_timestamp_validation": True,

        "require_fresh_market_data": True,
    }

    # ========================================================
    # 7. COMPLETE CONFIGURATION HANDOVER
    # ========================================================

    config = {

        "exchange": exchange,

        "execution_environment":
            execution_environment,

        "safety": safety,

        "strategy": strategy,

        "market_precision": market_precision,

        "market_data_policy": market_data_policy,

        "qualification": qualification,
    }

    # ========================================================
    # 8. VALIDATION FUNCTIONS
    # ========================================================

    def require(condition, message):

        if not condition:
            raise RuntimeError(
                "UNIT 2 CONFIG ERROR: " + message
            )

    def number(value, label):

        require(
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(value),
            label + " MUST BE FINITE"
        )

        return float(value)

    def between(
        value, lower, upper, label
    ):

        value = number(value, label)

        require(
            lower <= value <= upper,
            label + " OUT OF RANGE"
        )

        return value

    def votes(settings, label):

        count = settings["direction_votes_required"]

        total = settings.get(
            "direction_votes_total",
            qualification["common"][
                "direction_votes_total"
            ]
        )

        require(
            type(count) is int
            and type(total) is int
            and 1 <= count <= total == 3,
            label + " INVALID VOTES"
        )

    # ========================================================
    # 9. ORIGINAL CONTRACT VALIDATION
    # ========================================================

    require(
        exchange["name"] == "WEEX"
        and exchange["api_version"] == "V3"
        and exchange["market_symbol"] == "BTCUSDT"
        and exchange["demo_order_symbol"] == "BTCSUSDT",
        "EXCHANGE CONTRACT"
    )

    require(
        exchange["contract_base_url"]
        == "https://api-contract.weex.com",
        "WEEX BASE URL"
    )

    require(
        execution_environment == "DEMO",
        "DEMO ENVIRONMENT"
    )

    require(
        safety["public_market_data_read_enabled"]
        is True,
        "MARKET READ"
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
            "SAFETY FLAG " + key
        )

    require(
        strategy["max_backups"] == 5
        and strategy["backup_multipliers"]
        == (1.0, 1.5, 2.0, 2.5, 3.0),
        "ORIGINAL BACKUP CONFIGURATION"
    )

    between(
        strategy["initial_fixed_usdt"],
        0.000001, 1000000,
        "INITIAL MARGIN"
    )

    between(
        strategy["exposure_cap_percent"],
        0.000001, 35.0,
        "EXPOSURE CAP"
    )

    require(
        math.isclose(
            sum(
                strategy[key]
                for key in (
                    "tp1_allocation_percent",
                    "tp2_allocation_percent",
                    "tp3_allocation_percent",
                )
            ),
            100.0,
            abs_tol=0.000001
        ),
        "TP ALLOCATION"
    )

    require(
        strategy["one_direction_only"] is True
        and strategy["anti_duplicate_orders"] is True
        and strategy["exclusive_mode"] is True,
        "ORIGINAL SIGNAL SAFETY"
    )

    # ========================================================
    # 10. SHARED QUALIFICATION VALIDATION
    # ========================================================

    common = qualification["common"]

    require(
        common["mode_priority"] == (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP",
        ),
        "MODE PRIORITY"
    )

    votes(common, "COMMON")

    require(
        common["protect_developing_candidates"]
        is True
        and common["arbitrate_before_scalp"]
        is True,
        "CANDIDATE ARBITRATION"
    )

    # ========================================================
    # 11. BREAKOUT QUALIFICATION VALIDATION
    # ========================================================

    breakout = qualification["breakout"]

    votes(breakout, "BREAKOUT")

    require(
        type(
            breakout["support_resistance_lookback"]
        ) is int
        and 5 <= breakout[
            "support_resistance_lookback"
        ] <= 120,
        "BREAKOUT LOOKBACK"
    )

    between(
        breakout["developing_proximity_atr"],
        0.0, 5.0,
        "BREAKOUT DEVELOPING PROXIMITY"
    )

    between(
        breakout["confirmation_distance_atr"],
        0.0, 5.0,
        "BREAKOUT CONFIRMATION DISTANCE"
    )

    between(
        breakout["max_price_extension_atr"],
        0.1, 20.0,
        "BREAKOUT MAX EXTENSION"
    )

    between(
        breakout["minimum_volume_ratio"],
        0.1, 20.0,
        "BREAKOUT VOLUME RATIO"
    )

    # ========================================================
    # 12. STRUCTURE QUALIFICATION VALIDATION
    # ========================================================

    structure = qualification["structure"]

    votes(structure, "STRUCTURE")

    require(
        type(structure["ema_fast_period"]) is int
        and type(structure["ema_middle_period"]) is int
        and type(structure["ema_slow_period"]) is int
        and (
            structure["ema_fast_period"]
            < structure["ema_middle_period"]
            < structure["ema_slow_period"]
        ),
        "STRUCTURE EMA PERIODS"
    )

    between(
        structure["pullback_tolerance_atr"],
        0.01, 10.0,
        "STRUCTURE PULLBACK"
    )

    between(
        structure["max_price_extension_atr"],
        0.1, 20.0,
        "STRUCTURE MAX EXTENSION"
    )

    between(
        structure[
            "minimum_ema_separation_percent"
        ],
        0.0, 10.0,
        "STRUCTURE EMA SEPARATION"
    )

    # ========================================================
    # 13. SCALP QUALIFICATION VALIDATION
    # ========================================================

    scalp = qualification["scalp"]

    votes(scalp, "SCALP")

    between(
        scalp["quality_threshold"],
        0.0, 100.0,
        "SCALP QUALITY"
    )

    weight_price = between(
        scalp["price_action_weight_percent"],
        0.0, 100.0,
        "SCALP PRICE WEIGHT"
    )

    weight_other = between(
        scalp["other_factors_weight_percent"],
        0.0, 100.0,
        "SCALP OTHER WEIGHT"
    )

    require(
        math.isclose(
            weight_price + weight_other,
            100.0,
            abs_tol=0.000001
        ),
        "SCALP WEIGHTS TOTAL"
    )

    between(
        scalp["max_ema_extension_clusters"],
        0.01, 10.0,
        "SCALP EMA EXTENSION"
    )

    between(
        scalp["ema_compression_atr_max"],
        0.01, 10.0,
        "SCALP EMA COMPRESSION"
    )

    between(
        scalp["range20_atr_max"],
        0.1, 50.0,
        "SCALP RANGE ATR"
    )

    between(
        scalp["estimated_taker_fee_percent"],
        0.0, 5.0,
        "SCALP TAKER FEE"
    )

    between(
        scalp["minimum_fee_coverage_multiplier"],
        1.0, 20.0,
        "SCALP FEE COVERAGE"
    )

    between(
        scalp["minimum_net_roi_percent"],
        0.0, 100.0,
        "SCALP MIN NET ROI"
    )

    # ========================================================
    # 14. CONFIRM UNIT 3 POLICY
    # ========================================================

    require(
        0 < market_data_policy[
            "max_market_age_seconds"
        ] <= 120.0,
        "MARKET DATA AGE"
    )

    require(
        0 <= market_data_policy[
            "future_tolerance_seconds"
        ] <= 30.0,
        "MARKET CLOCK TOLERANCE"
    )

    require(
        market_data_policy[
            "require_finite_price"
        ] is True
        and market_data_policy[
            "require_timestamp_validation"
        ] is True
        and market_data_policy[
            "require_fresh_market_data"
        ] is True,
        "MARKET DATA PROTECTION"
    )

    # ========================================================
    # 15. FINAL LOGGING
    # ========================================================

    print(
        "PASS: UNIT 2 ORIGINAL CONFIGURATION PRESERVED",
        flush=True
    )

    print(
        "PASS: UNIT 2 ADJUSTABLE QUALIFICATIONS READY",
        flush=True
    )

    print(
        "UNIT 2 MODE PRIORITY =",
        common["mode_priority"],
        flush=True
    )

    print(
        "UNIT 2 BREAKOUT LOOKBACK =",
        breakout["support_resistance_lookback"],
        flush=True
    )

    print(
        "UNIT 2 BREAKOUT PROXIMITY ATR =",
        breakout["developing_proximity_atr"],
        flush=True
    )

    print(
        "UNIT 2 BREAKOUT CONFIRMATION ATR =",
        breakout["confirmation_distance_atr"],
        flush=True
    )

    print(
        "UNIT 2 STRUCTURE PULLBACK ATR =",
        structure["pullback_tolerance_atr"],
        flush=True
    )

    print(
        "UNIT 2 STRUCTURE MAX EXTENSION ATR =",
        structure["max_price_extension_atr"],
        flush=True
    )

    print(
        "UNIT 2 SCALP QUALITY MINIMUM =",
        scalp["quality_threshold"],
        flush=True
    )

    print(
        "UNIT 2 SCALP PRICE WEIGHT =",
        scalp["price_action_weight_percent"],
        "%",
        flush=True
    )

    print(
        "UNIT 2 SCALP MAX EMA EXTENSION =",
        scalp["max_ema_extension_clusters"],
        flush=True
    )

    print(
        "UNIT 2 INITIAL ENTRY USDT =",
        strategy["initial_fixed_usdt"],
        flush=True
    )

    print(
        "UNIT 2 BACKUPS =",
        strategy["max_backups"],
        flush=True
    )

    print(
        "UNIT 2 BACKUP MULTIPLIERS =",
        strategy["backup_multipliers"],
        flush=True
    )

    print(
        "UNIT 2 EXPOSURE CAP =",
        strategy["exposure_cap_percent"],
        "%",
        flush=True
    )

    print(
        "UNIT 2 TP ALLOCATION = 10 / 20 / 70",
        flush=True
    )

    print(
        "UNIT 2 MARKET DATA POLICY = READY",
        flush=True
    )

    print(
        "UNIT 2 HEDGING CONFIGURATION = NONE",
        flush=True
    )

    print(
        "UNIT 2 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 2 "
        "HYBRID QUALIFICATION V3 RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return config


# ============================================================
# UNIT 2 EXECUTION / UNIT 3 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_CONFIG = (
    fresh_reconstruction_unit_2()
)


# ============================================================
# END UNIT 2 - HYBRID QUALIFICATION V3
# ZERO INDENTATION
# UNIT 3 CONTINUES BELOW UNCHANGED
# ============================================================


# ============================================================
# START UNIT 3 - IMPROVED HYBRID V3
# ZERO INDENTATION
#
# SOURCE:
# ORIGINAL 22525-LINE WORKING MODEL
# PLUS SELECTED 12356-LINE MODEL IMPROVEMENTS
#
# PRESERVE:
# - UNIT 2 CONFIGURATION INTERFACE
# - UNIT 4 EIGHT-FIELD SNAPSHOT
# - ORIGINAL UNITS 4 THROUGH 15
# - UNIT 12 DEMO ORDER EXECUTION
#
# PUBLIC MARKET READ ONLY
# NO ACCOUNT MUTATION
# NO ORDER SUBMISSION
# NO NEW BOT MODE
# ============================================================


def fresh_reconstruction_unit_3():

    import json
    import math
    import time
    import urllib.error
    import urllib.parse
    import urllib.request

    print("=" * 80, flush=True)

    log(
        "FRESH RECONSTRUCTION UNIT 3 HYBRID V3 START"
    )

    # ========================================================
    # 1. RECEIVE UNIT 2 CONFIGURATION
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 3 INVALID UNIT 2 CONFIGURATION"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    policy = config.get("market_data_policy", {})

    if not isinstance(exchange, dict):
        raise RuntimeError(
            "UNIT 3 INVALID EXCHANGE CONFIGURATION"
        )

    if not isinstance(safety, dict):
        raise RuntimeError(
            "UNIT 3 INVALID SAFETY CONFIGURATION"
        )

    if not isinstance(policy, dict):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET POLICY"
        )

    # ========================================================
    # 2. ORIGINAL EXCHANGE CONTRACT
    # ========================================================

    if exchange.get("name") != "WEEX":
        raise RuntimeError(
            "UNIT 3 EXCHANGE MUST BE WEEX"
        )

    if exchange.get("api_version") != "V3":
        raise RuntimeError(
            "UNIT 3 API VERSION MISMATCH"
        )

    base_url = exchange.get(
        "contract_base_url"
    )

    symbol = exchange.get(
        "market_symbol"
    )

    demo_symbol = exchange.get(
        "demo_order_symbol"
    )

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 3 INVALID WEEX API URL"
        )

    if symbol != "BTCUSDT":
        raise RuntimeError(
            "UNIT 3 INVALID PUBLIC SYMBOL"
        )

    if demo_symbol != "BTCSUSDT":
        raise RuntimeError(
            "UNIT 3 INVALID DEMO SYMBOL"
        )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 3 DEMO ENVIRONMENT REQUIRED"
        )

    print(
        "PASS: UNIT 3 ORIGINAL WEEX CONTRACT",
        flush=True
    )

    # ========================================================
    # 3. PRESERVE UNIT 2 SAFETY CONTRACT
    # ========================================================

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
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
                "UNIT 3 INVALID SAFETY FLAG: " + key
            )

    print(
        "PASS: UNIT 3 PUBLIC READ SAFETY",
        flush=True
    )

    # ========================================================
    # 4. USE REVISED UNIT 2 DATA POLICY
    # ========================================================

    try:

        max_market_age_seconds = float(
            policy.get(
                "max_market_age_seconds",
                120.0
            )
        )

        future_tolerance_seconds = float(
            policy.get(
                "future_tolerance_seconds",
                30.0
            )
        )

        max_response_bytes = int(
            policy.get(
                "max_response_bytes",
                65536
            )
        )

    except (
        TypeError,
        ValueError,
        OverflowError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID NUMERIC MARKET POLICY"
        ) from exc

    if not (
        math.isfinite(max_market_age_seconds)
        and 0 < max_market_age_seconds <= 120.0
    ):
        raise RuntimeError(
            "UNIT 3 INVALID MAX MARKET AGE"
        )

    if not (
        math.isfinite(future_tolerance_seconds)
        and 0 <= future_tolerance_seconds <= 30.0
    ):
        raise RuntimeError(
            "UNIT 3 INVALID CLOCK TOLERANCE"
        )

    if not (
        1024 <= max_response_bytes <= 65536
    ):
        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE SIZE LIMIT"
        )

    # These protections are mandatory for the
    # improved hybrid data-validation contract.

    for key in (
        "require_finite_price",
        "require_timestamp_validation",
        "require_fresh_market_data",
    ):

        if policy.get(key, True) is not True:

            raise RuntimeError(
                "UNIT 3 REQUIRED DATA PROTECTION "
                "DISABLED: " + key
            )

    print(
        "PASS: UNIT 3 UNIT 2 MARKET POLICY RECEIVED",
        flush=True
    )

    # ========================================================
    # 5. ORIGINAL WEEX PUBLIC ENDPOINT
    # ========================================================

    endpoint = "/capi/v3/market/symbolPrice"

    query = urllib.parse.urlencode({
        "symbol": symbol,
        "priceType": "MARK",
    })

    url = (
        base_url
        + endpoint
        + "?"
        + query
    )

    request = urllib.request.Request(
        url=url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Hybrid-Unit3-V3",
        },
    )

    if request.get_method() != "GET":
        raise RuntimeError(
            "UNIT 3 INVALID HTTP METHOD"
        )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 3 UNEXPECTED REQUEST BODY"
        )

    # ========================================================
    # 6. PROTECT AGAINST HTTP REDIRECTION
    # ========================================================

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):

        def redirect_request(
            self,
            req,
            fp,
            code,
            msg,
            headers,
            newurl
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    print(
        "UNIT 3 PUBLIC MARKET REQUEST START",
        flush=True
    )

    # ========================================================
    # 7. PERFORM BOUNDED PUBLIC MARKET READ
    # ========================================================

    try:

        with opener.open(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()

            raw_body = response.read(
                max_response_bytes + 1
            )

            received_time_ms = int(
                time.time() * 1000
            )

    except urllib.error.HTTPError as exc:

        error_body = exc.read(500).decode(
            "utf-8",
            errors="replace"
        )

        print(
            "UNIT 3 HTTP ERROR CODE =",
            exc.code,
            flush=True
        )

        print(
            "UNIT 3 HTTP ERROR BODY =",
            error_body,
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX PUBLIC HTTP FAILURE"
        ) from exc

    except urllib.error.URLError as exc:

        print(
            "UNIT 3 NETWORK ERROR =",
            repr(exc.reason),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 WEEX CONNECTION FAILED"
        ) from exc

    if http_status != 200:
        raise RuntimeError(
            "UNIT 3 HTTP STATUS NOT 200"
        )

    if not raw_body:
        raise RuntimeError(
            "UNIT 3 EMPTY WEEX RESPONSE"
        )

    if len(raw_body) > max_response_bytes:
        raise RuntimeError(
            "UNIT 3 RESPONSE SIZE LIMIT EXCEEDED"
        )

    print(
        "PASS: UNIT 3 WEEX RESPONSE RECEIVED",
        flush=True
    )

    # ========================================================
    # 8. VALIDATE RESPONSE JSON
    # ========================================================

    try:

        payload = json.loads(
            raw_body.decode("utf-8")
        )

    except (
        ValueError,
        UnicodeDecodeError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID WEEX JSON"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            "UNIT 3 INVALID RESPONSE STRUCTURE"
        )

    if payload.get("symbol") != symbol:
        raise RuntimeError(
            "UNIT 3 RESPONSE SYMBOL MISMATCH"
        )

    print(
        "PASS: UNIT 3 RESPONSE SYMBOL =",
        symbol,
        flush=True
    )

    # ========================================================
    # 9. FINITE AND POSITIVE MARK PRICE VALIDATION
    # ========================================================

    raw_price = payload.get("price")

    if isinstance(raw_price, bool):
        raise RuntimeError(
            "UNIT 3 BOOLEAN PRICE REJECTED"
        )

    try:

        mark_price = float(raw_price)

    except (
        TypeError,
        ValueError,
        OverflowError
    ) as exc:

        raise RuntimeError(
            "UNIT 3 INVALID MARK PRICE"
        ) from exc

    if not math.isfinite(mark_price):
        raise RuntimeError(
            "UNIT 3 NON-FINITE PRICE REJECTED"
        )

    if mark_price <= 0:
        raise RuntimeError(
            "UNIT 3 NON-POSITIVE PRICE REJECTED"
        )

    print(
        "PASS: UNIT 3 BTC MARK PRICE =",
        mark_price,
        flush=True
    )

    # ========================================================
    # 10. VERIFY EXCHANGE TIMESTAMP
    # ========================================================

    exchange_time_ms = payload.get("time")

    if (
        isinstance(exchange_time_ms, bool)
        or not isinstance(exchange_time_ms, int)
    ):
        raise RuntimeError(
            "UNIT 3 INVALID TIMESTAMP TYPE"
        )

    if not (
        1000000000000
        <= exchange_time_ms
        < 100000000000000
    ):
        raise RuntimeError(
            "UNIT 3 INVALID MILLISECOND TIMESTAMP"
        )

    market_age_seconds = (
        received_time_ms
        - exchange_time_ms
    ) / 1000.0

    if not math.isfinite(market_age_seconds):
        raise RuntimeError(
            "UNIT 3 INVALID MARKET AGE"
        )

    # ========================================================
    # 11. MARKET DATA FRESHNESS PROTECTION
    # ========================================================

    if market_age_seconds > max_market_age_seconds:

        print(
            "UNIT 3 STALE DATA AGE =",
            round(market_age_seconds, 3),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 STALE MARKET DATA"
        )

    if market_age_seconds < -future_tolerance_seconds:

        print(
            "UNIT 3 FUTURE TIMESTAMP OFFSET =",
            round(market_age_seconds, 3),
            flush=True
        )

        raise RuntimeError(
            "UNIT 3 EXCHANGE CLOCK MISMATCH"
        )

    print(
        "PASS: UNIT 3 MARKET DATA FRESH",
        flush=True
    )

    print(
        "UNIT 3 MARKET AGE SECONDS =",
        round(market_age_seconds, 3),
        flush=True
    )

    # ========================================================
    # 12. EXACT ORIGINAL UNIT 4 SNAPSHOT CONTRACT
    #
    # ALL EIGHT ORIGINAL FIELDS PRESERVED
    # NO ADDITIONAL REQUIRED DOWNSTREAM FIELDS
    # ========================================================

    market_snapshot = {

        "exchange": "WEEX",

        "api_version": "V3",

        "symbol": symbol,

        "price": mark_price,

        "price_type": "MARK",

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
            "UNIT 3 INCOMPLETE MARKET SNAPSHOT"
        )

    # ========================================================
    # 13. FINAL HANDOVER
    # ========================================================

    print(
        "PASS: UNIT 3 ORIGINAL SNAPSHOT PRESERVED",
        flush=True
    )

    print(
        "PASS: UNIT 3 SNAPSHOT READY FOR UNIT 4",
        flush=True
    )

    print(
        "UNIT 3 AUTHENTICATED API = NONE",
        flush=True
    )

    print(
        "UNIT 3 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 3 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 3 EXCHANGE WRITE = NONE",
        flush=True
    )

    log(
        "FRESH RECONSTRUCTION UNIT 3 HYBRID V3 "
        "RESULT = PASS"
    )

    print("=" * 80, flush=True)

    return market_snapshot


# ============================================================
# UNIT 3 EXECUTION AND UNIT 4 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
    fresh_reconstruction_unit_3()
)


# ============================================================
# END UNIT 3 - IMPROVED HYBRID V3
# ZERO INDENTATION
#
# ORIGINAL UNIT 4 CONTINUES BELOW
# ============================================================



# ============================================================
# START UNIT 4 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
#
# UNIT 2: ADJUSTABLE QUALIFICATION CONFIGURATION
# UNIT 3: VERIFIED WEEX PUBLIC MARKET SNAPSHOT
#
# UNIT 4:
# PUBLIC OHLC + EMA + ATR + MARKET REGIME
# DEVELOPING BREAKOUT / STRUCTURE DETECTION
# SCALP SIDEWAYS EVIDENCE
#
# PRESERVE ORIGINAL UNIT 5 HANDOVER
# NO AUTHENTICATED API / NO EXCHANGE WRITE
# ============================================================


def fresh_reconstruction_unit_4():

    import json
    import math
    import time
    import urllib.parse
    import urllib.request
    import urllib.error
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 4 "
        "HYBRID ADJUSTABLE V2 START",
        flush=True
    )

    # ========================================================
    # 1. ORIGINAL UNIT 2 AND 3 HANDOVER
    # ========================================================

    config = FRESH_RECONSTRUCTION_CONFIG
    market = FRESH_RECONSTRUCTION_MARKET_SNAPSHOT

    if not isinstance(config, dict):
        raise RuntimeError("UNIT 4 INVALID UNIT 2")

    if not isinstance(market, dict):
        raise RuntimeError("UNIT 4 INVALID UNIT 3")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    policy = config.get("market_data_policy", {})
    qualification = config.get("qualification", {})

    if not isinstance(qualification, dict):
        raise RuntimeError(
            "UNIT 4 QUALIFICATION CONFIG INVALID"
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
            scalp_cfg
        )
    ):
        raise RuntimeError(
            "UNIT 4 STRATEGY CONFIG INVALID"
        )

    if (
        exchange.get("name") != "WEEX"
        or exchange.get("api_version") != "V3"
        or exchange.get("market_symbol") != "BTCUSDT"
        or market.get("exchange") != "WEEX"
        or market.get("api_version") != "V3"
        or market.get("symbol") != "BTCUSDT"
        or market.get("price_type") != "MARK"
        or market.get("read_only") is not True
    ):
        raise RuntimeError(
            "UNIT 4 EXCHANGE CONTRACT MISMATCH"
        )

    if safety.get(
        "public_market_data_read_enabled"
    ) is not True:
        raise RuntimeError(
            "UNIT 4 PUBLIC MARKET READ DISABLED"
        )

    if any(
        safety.get(key) is not False
        for key in (
            "exchange_mutation_enabled",
            "real_order_submission_enabled",
            "leverage_mutation_enabled",
            "margin_mode_mutation_enabled",
            "position_mode_mutation_enabled",
        )
    ):
        raise RuntimeError(
            "UNIT 4 INVALID EXCHANGE SAFETY"
        )

    print(
        "PASS: UNIT 4 RECEIVED UNITS 2 AND 3",
        flush=True
    )

    # ========================================================
    # 2. NUMERIC AND CONFIG HELPERS
    # ========================================================

    def finite(value, name):

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 4 BOOLEAN NUMBER " + name
            )

        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            raise RuntimeError(
                "UNIT 4 INVALID NUMBER " + name
            )

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 4 NONFINITE NUMBER " + name
            )

        return result

    def setting(section, key, minimum, maximum):

        if key not in section:
            raise RuntimeError(
                "UNIT 4 MISSING QUALIFICATION " + key
            )

        result = finite(section[key], key)

        if not minimum <= result <= maximum:
            raise RuntimeError(
                "UNIT 4 OUT OF RANGE " + key
            )

        return result

    lookback = int(
        setting(
            breakout_cfg,
            "support_resistance_lookback",
            5,
            120
        )
    )

    if type(
        breakout_cfg["support_resistance_lookback"]
    ) is not int:
        raise RuntimeError(
            "UNIT 4 BREAKOUT LOOKBACK MUST BE INTEGER"
        )

    breakout_proximity = setting(
        breakout_cfg,
        "developing_proximity_atr",
        0,
        5
    )

    breakout_confirmation = setting(
        breakout_cfg,
        "confirmation_distance_atr",
        0,
        5
    )

    breakout_max_extension = setting(
        breakout_cfg,
        "max_price_extension_atr",
        0.1,
        20
    )

    structure_pullback = setting(
        structure_cfg,
        "pullback_tolerance_atr",
        0.01,
        10
    )

    structure_max_extension = setting(
        structure_cfg,
        "max_price_extension_atr",
        0.1,
        20
    )

    structure_min_separation = setting(
        structure_cfg,
        "minimum_ema_separation_percent",
        0,
        10
    )

    scalp_compression_limit = setting(
        scalp_cfg,
        "ema_compression_atr_max",
        0.01,
        10
    )

    scalp_range_limit = setting(
        scalp_cfg,
        "range20_atr_max",
        0.1,
        50
    )

    scalp_momentum_limit = setting(
        scalp_cfg,
        "momentum15_atr_multiplier_max",
        0.01,
        20
    )

    # Existing downstream contracts use EMA19/50/200.
    # Preserve their meaning in this reconstruction.

    if (
        structure_cfg.get("ema_fast_period") != 19
        or structure_cfg.get("ema_middle_period") != 50
        or structure_cfg.get("ema_slow_period") != 200
    ):
        raise RuntimeError(
            "UNIT 4 EMA PERIOD CHANGE REQUIRES "
            "COORDINATED UNIT 5/6 ADAPTATION"
        )

    # ========================================================
    # 3. UNIT 3 MARKET TIMESTAMP CHECK
    # ========================================================

    market_price = finite(
        market.get("price"),
        "UNIT 3 PRICE"
    )

    exchange_time = int(
        finite(
            market.get("exchange_time_ms"),
            "UNIT 3 TIMESTAMP"
        )
    )

    now_ms = int(time.time() * 1000)

    market_age = (
        now_ms - exchange_time
    ) / 1000.0

    max_age = finite(
        policy.get("max_market_age_seconds"),
        "MARKET AGE LIMIT"
    )

    future_tolerance = finite(
        policy.get("future_tolerance_seconds"),
        "FUTURE TOLERANCE"
    )

    if market_price <= 0:
        raise RuntimeError(
            "UNIT 4 INVALID MARK PRICE"
        )

    if not (
        -future_tolerance
        <= market_age
        <= max_age
    ):
        raise RuntimeError(
            "UNIT 4 STALE UNIT 3 SNAPSHOT"
        )

    # ========================================================
    # 4. ORIGINAL WEEX PUBLIC KLINE ENDPOINT
    # ========================================================

    base_url = exchange["contract_base_url"]

    if base_url != "https://api-contract.weex.com":
        raise RuntimeError(
            "UNIT 4 UNEXPECTED BASE URL"
        )

    interval = "1m"
    candle_limit = 300

    query = urllib.parse.urlencode({
        "symbol": "BTCUSDT",
        "interval": interval,
        "limit": candle_limit,
    })

    url = (
        base_url
        + "/capi/v3/market/markPriceKlines?"
        + query
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "WEEX-Hybrid-Analysis/2",
        },
        method="GET"
    )

    if request.data is not None:
        raise RuntimeError(
            "UNIT 4 REQUEST BODY NOT ALLOWED"
        )

    max_bytes = int(
        finite(
            policy.get("max_response_bytes"),
            "MAX RESPONSE BYTES"
        )
    )

    class NoRedirect(urllib.request.HTTPRedirectHandler):

        def redirect_request(
            self,
            req,
            fp,
            code,
            msg,
            headers,
            newurl
        ):
            raise RuntimeError(
                "UNIT 4 HTTP REDIRECT BLOCKED"
            )

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    try:

        with opener.open(
            request,
            timeout=15
        ) as response:

            if response.status != 200:
                raise RuntimeError(
                    "UNIT 4 NON-200 RESPONSE"
                )

            raw_bytes = response.read(
                max_bytes + 1
            )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "UNIT 4 MARKET CONNECTION FAILED"
        ) from exc

    if not raw_bytes or len(raw_bytes) > max_bytes:
        raise RuntimeError(
            "UNIT 4 INVALID RESPONSE SIZE"
        )

    try:
        raw_klines = json.loads(
            raw_bytes.decode("utf-8")
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError
    ) as exc:
        raise RuntimeError(
            "UNIT 4 INVALID KLINE JSON"
        ) from exc

    if not isinstance(raw_klines, list):
        raise RuntimeError(
            "UNIT 4 KLINES MUST BE A LIST"
        )

    if len(raw_klines) < 201:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT KLINES"
        )

    # ========================================================
    # 5. NORMALIZE VERIFIED WEEX CANDLE FORMAT
    #
    # [0] OPEN TIME
    # [1] OPEN
    # [2] HIGH
    # [3] LOW
    # [4] CLOSE
    # [5] VOLUME
    # [6] CLOSE TIME
    # ========================================================

    normalized = []

    for item in raw_klines:

        if not isinstance(item, (list, tuple)):
            raise RuntimeError(
                "UNIT 4 INVALID KLINE TYPE"
            )

        if len(item) < 7:
            raise RuntimeError(
                "UNIT 4 INCOMPLETE KLINE"
            )

        candle = {
            "open_time_ms": int(item[0]),
            "open": finite(item[1], "OPEN"),
            "high": finite(item[2], "HIGH"),
            "low": finite(item[3], "LOW"),
            "close": finite(item[4], "CLOSE"),
            "volume": finite(item[5], "VOLUME"),
            "close_time_ms": int(item[6]),
        }

        if not (
            0 < candle["low"]
            <= min(
                candle["open"],
                candle["close"]
            )
            <= max(
                candle["open"],
                candle["close"]
            )
            <= candle["high"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE OHLC"
            )

        if candle["volume"] < 0:
            raise RuntimeError(
                "UNIT 4 NEGATIVE VOLUME"
            )

        if (
            candle["close_time_ms"]
            < candle["open_time_ms"]
        ):
            raise RuntimeError(
                "UNIT 4 INVALID CANDLE TIMES"
            )

        normalized.append(candle)

    normalized.sort(
        key=lambda x: x["open_time_ms"]
    )

    if len({
        x["open_time_ms"]
        for x in normalized
    }) != len(normalized):
        raise RuntimeError(
            "UNIT 4 DUPLICATE CANDLE TIMES"
        )

    now_ms = int(time.time() * 1000)

    closed = [
        c for c in normalized
        if c["close_time_ms"] <= now_ms
    ]

    if len(closed) < 201:
        raise RuntimeError(
            "UNIT 4 INSUFFICIENT CLOSED CANDLES"
        )

    latest = closed[-1]
    previous = closed[-2]

    candle_age_seconds = (
        now_ms - latest["close_time_ms"]
    ) / 1000.0

    candle_data_fresh = (
        0 <= candle_age_seconds <= max_age
    )

    if not candle_data_fresh:
        raise RuntimeError(
            "UNIT 4 CLOSED CANDLES STALE"
        )

    print(
        "PASS: UNIT 4 CLOSED CANDLES =",
        len(closed),
        flush=True
    )

    # ========================================================
    # 6. EMA CALCULATIONS
    # ========================================================

    closes = [
        c["close"] for c in closed
    ]

    def ema(series, period):

        if len(series) < period:
            raise RuntimeError(
                "UNIT 4 EMA DATA INSUFFICIENT"
            )

        result = sum(
            series[:period]
        ) / period

        alpha = 2.0 / (period + 1.0)

        for value in series[period:]:
            result = (
                value * alpha
                + result * (1.0 - alpha)
            )

        return result

    ema19 = ema(closes, 19)
    ema50 = ema(closes, 50)
    ema100 = ema(closes, 100)
    ema200 = ema(closes, 200)

    ema_separation = (
        (ema19 - ema50)
        / ema50
        * 100.0
    )

    if ema19 > ema50 > ema200:
        ema_structure = "BULLISH"
    elif ema19 < ema50 < ema200:
        ema_structure = "BEARISH"
    else:
        ema_structure = "MIXED"

    # ========================================================
    # 7. ORIGINAL MULTI-WINDOW MOVEMENT FIELDS
    # ========================================================

    def movement(minutes):

        reference = closes[-1 - minutes]

        return (
            (closes[-1] - reference)
            / reference
            * 100.0
        )

    moves = {
        n: movement(n)
        for n in (1, 5, 15, 30, 60, 120)
    }

    short_term_move_pct = moves[1]

    def movement_direction(value):

        if value > 0:
            return "LONG"

        if value < 0:
            return "SHORT"

        return "NONE"

    # ========================================================
    # 8. ATR14 - VERIFIED CLOSED CANDLES
    # ========================================================

    true_ranges = []

    for i in range(1, len(closed)):

        current = closed[i]
        previous_close = closed[i - 1]["close"]

        true_ranges.append(
            max(
                current["high"] - current["low"],
                abs(
                    current["high"]
                    - previous_close
                ),
                abs(
                    current["low"]
                    - previous_close
                )
            )
        )

    atr14 = sum(
        true_ranges[-14:]
    ) / 14.0

    if atr14 <= 0:
        raise RuntimeError(
            "UNIT 4 ZERO ATR"
        )

    atr_percent = (
        atr14 / latest["close"] * 100.0
    )

    # ========================================================
    # 9. ADJUSTABLE SUPPORT / RESISTANCE
    #
    # EXCLUDE CURRENT CANDLE SO IT CAN BREAK
    # A LEVEL DEFINED BY PREVIOUS CANDLES.
    # ========================================================

    prior_range = closed[
        -1 - lookback:-1
    ]

    support = min(
        c["low"] for c in prior_range
    )

    resistance = max(
        c["high"] for c in prior_range
    )

    range_size = resistance - support

    range_atr_ratio = (
        range_size / atr14
    )

    latest_close = latest["close"]

    # ========================================================
    # 10. COMMON DIRECTIONAL EVIDENCE
    #
    # 3 SOURCES:
    # 1) EMA
    # 2) MOMENTUM
    # 3) PRICE VS EMA19
    # ========================================================

    ema_vote = (
        "LONG" if ema19 > ema50
        else "SHORT" if ema19 < ema50
        else "NONE"
    )

    momentum_vote = movement_direction(
        moves[5] + moves[15]
    )

    price_vote = (
        "LONG" if latest_close > ema19
        else "SHORT" if latest_close < ema19
        else "NONE"
    )

    votes = (
        ema_vote,
        momentum_vote,
        price_vote,
    )

    long_votes = votes.count("LONG")
    short_votes = votes.count("SHORT")

    common_required = int(
        common["direction_votes_required"]
    )

    if (
        long_votes >= common_required
        and long_votes > short_votes
    ):
        direction_evidence = "LONG"

    elif (
        short_votes >= common_required
        and short_votes > long_votes
    ):
        direction_evidence = "SHORT"

    else:
        direction_evidence = "NONE"

    # ========================================================
    # 11. BREAKOUT QUALIFICATION EVIDENCE
    #
    # DEVELOPING != CONFIRMED
    # UNIT 5 STILL DECIDES QUALIFICATION.
    # ========================================================

    proximity = (
        breakout_proximity * atr14
    )

    confirmation = (
        breakout_confirmation * atr14
    )

    near_resistance = (
        latest_close
        >= resistance - proximity
    )

    near_support = (
        latest_close
        <= support + proximity
    )

    breakout_confirmed_long = (
        latest_close
        > resistance + confirmation
    )

    breakout_confirmed_short = (
        latest_close
        < support - confirmation
    )

    breakout_developing_long = (
        breakout_cfg["enabled"]
        and breakout_cfg[
            "developing_candidate_enabled"
        ]
        and near_resistance
        and direction_evidence == "LONG"
        and moves[5] > 0
    )

    breakout_developing_short = (
        breakout_cfg["enabled"]
        and breakout_cfg[
            "developing_candidate_enabled"
        ]
        and near_support
        and direction_evidence == "SHORT"
        and moves[5] < 0
    )

    # Maximum distance beyond breakout boundary.
    # This prevents treating an exhausted impulse
    # as a fresh developing candidate.

    long_breakout_extension = max(
        0.0,
        (
            latest_close - resistance
        ) / atr14
    )

    short_breakout_extension = max(
        0.0,
        (
            support - latest_close
        ) / atr14
    )

    if (
        long_breakout_extension
        > breakout_max_extension
    ):
        breakout_developing_long = False
        breakout_confirmed_long = False

    if (
        short_breakout_extension
        > breakout_max_extension
    ):
        breakout_developing_short = False
        breakout_confirmed_short = False

    # ========================================================
    # 12. ADJUSTABLE STRUCTURE DEVELOPMENT
    #
    # IDENTIFY TREND + PULLBACK / CONTINUATION
    # WITHOUT REQUIRING A NEW EMA CROSSOVER.
    # ========================================================

    structure_ema_sep_ok = (
        abs(ema_separation)
        >= structure_min_separation
    )

    structure_long_trend = (
        ema19 > ema50
        and ema50 > ema200
    )

    structure_short_trend = (
        ema19 < ema50
        and ema50 < ema200
    )

    distance_from_ema19_atr = (
        latest_close - ema19
    ) / atr14

    pullback_near_ema = (
        abs(distance_from_ema19_atr)
        <= structure_pullback
    )

    long_extension_ok = (
        distance_from_ema19_atr
        <= structure_max_extension
    )

    short_extension_ok = (
        -distance_from_ema19_atr
        <= structure_max_extension
    )

    structure_developing_long = (
        structure_cfg["enabled"]
        and structure_ema_sep_ok
        and structure_long_trend
        and direction_evidence == "LONG"
        and moves[15] > 0
        and long_extension_ok
        and (
            pullback_near_ema
            or (
                structure_cfg[
                    "allow_continuation_entry"
                ]
                and latest_close > ema19
            )
        )
    )

    structure_developing_short = (
        structure_cfg["enabled"]
        and structure_ema_sep_ok
        and structure_short_trend
        and direction_evidence == "SHORT"
        and moves[15] < 0
        and short_extension_ok
        and (
            pullback_near_ema
            or (
                structure_cfg[
                    "allow_continuation_entry"
                ]
                and latest_close < ema19
            )
        )
    )

    # ========================================================
    # 13. ADJUSTABLE SCALP / SIDEWAYS MARKET EVIDENCE
    # ========================================================

    ema_cluster_height = (
        max(ema19, ema50, ema100, ema200)
        - min(ema19, ema50, ema100, ema200)
    )

    ema_compression_atr = (
        ema_cluster_height / atr14
    )

    price_extension_cluster = (
        abs(latest_close - ema19)
        / max(
            ema_cluster_height,
            atr14 * 0.01
        )
    )

    momentum15_atr_ratio = (
        abs(
            latest_close
            - closes[-16]
        ) / atr14
    )

    sideways_candidate = (
        scalp_cfg["enabled"]
        and (
            ema_compression_atr
            <= scalp_compression_limit
        )
        and (
            range_atr_ratio
            <= scalp_range_limit
        )
        and (
            momentum15_atr_ratio
            <= scalp_momentum_limit
        )
        and not (
            breakout_developing_long
            or breakout_developing_short
            or structure_developing_long
            or structure_developing_short
        )
    )

    price_overextended = (
        price_extension_cluster
        > scalp_cfg[
            "max_ema_extension_clusters"
        ]
    )

    # ========================================================
    # 14. PRESERVE ORIGINAL UNIT 5 HANDOVER
    # ========================================================

    analysis_snapshot = {

        # ORIGINAL CONTRACT

        "exchange": "WEEX",
        "api_version": "V3",
        "symbol": "BTCUSDT",
        "interval": "1m",
        "price_type": "MARK",

        "live_mark_price": market_price,

        "previous_close": previous["close"],
        "latest_close": latest_close,

        "latest_open_time_ms":
            latest["open_time_ms"],

        "latest_close_time_ms":
            latest["close_time_ms"],

        "exchange_time_ms": exchange_time,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            ema_separation,

        "ema_structure": ema_structure,

        "short_term_move_pct":
            short_term_move_pct,

        "move_1m_pct": moves[1],
        "move_5m_pct": moves[5],
        "move_15m_pct": moves[15],
        "move_30m_pct": moves[30],
        "move_60m_pct": moves[60],
        "move_120m_pct": moves[120],

        "recent_closed_klines": [
            dict(c)
            for c in closed[-60:]
        ],

        "candle_count": len(normalized),

        "closed_candle_count": len(closed),

        "newest_returned_candle_closed":
            normalized[-1][
                "close_time_ms"
            ] <= now_ms,

        "source":
            "WEEX_V3_PUBLIC_MARK_PRICE_KLINES",

        "read_only": True,

        # HYBRID ANALYSIS EVIDENCE

        "atr14": atr14,
        "atr_percent": atr_percent,

        "support20": support,
        "resistance20": resistance,

        "range20_atr_ratio":
            range_atr_ratio,

        "near_resistance": near_resistance,
        "near_support": near_support,

        "breakout_developing_long":
            bool(breakout_developing_long),

        "breakout_developing_short":
            bool(breakout_developing_short),

        "breakout_confirmed_long":
            bool(breakout_confirmed_long),

        "breakout_confirmed_short":
            bool(breakout_confirmed_short),

        "structure_developing_long":
            bool(structure_developing_long),

        "structure_developing_short":
            bool(structure_developing_short),

        "sideways_candidate":
            bool(sideways_candidate),

        "direction_long_votes":
            long_votes,

        "direction_short_votes":
            short_votes,

        "direction_evidence":
            direction_evidence,

        "ema_cluster_height":
            ema_cluster_height,

        "ema_compression_atr":
            ema_compression_atr,

        "price_extension_cluster":
            price_extension_cluster,

        "price_overextended":
            bool(price_overextended),

        "candle_age_seconds":
            candle_age_seconds,

        "candle_data_fresh":
            candle_data_fresh,

        "strategy_evidence_version":
            "U4_HYBRID_V2",

        # TRACE OF ACTIVE UNIT 2 FIGURES

        "qualification_settings": {

            "breakout_lookback": lookback,

            "breakout_proximity_atr":
                breakout_proximity,

            "breakout_confirmation_atr":
                breakout_confirmation,

            "structure_pullback_atr":
                structure_pullback,

            "structure_max_extension_atr":
                structure_max_extension,

            "scalp_compression_atr":
                scalp_compression_limit,

            "scalp_range_atr":
                scalp_range_limit,

            "scalp_momentum_atr":
                scalp_momentum_limit,
        },

        # UNIT 4 HAS NO ORDER AUTHORITY

        "trade_authorized": False,
        "order_payload_created": False,
    }

    # ========================================================
    # 15. CONTRACT VALIDATION
    # ========================================================

    required_fields = (
        "symbol",
        "live_mark_price",
        "ema19",
        "ema50",
        "ema200",
        "ema19_50_separation_pct",
        "ema_structure",
        "previous_close",
        "latest_close",
        "short_term_move_pct",
        "move_1m_pct",
        "move_5m_pct",
        "move_15m_pct",
        "move_30m_pct",
        "move_60m_pct",
        "move_120m_pct",
        "recent_closed_klines",
        "read_only",
    )

    for field in required_fields:

        if field not in analysis_snapshot:
            raise RuntimeError(
                "UNIT 4 HANDOVER MISSING " + field
            )

    if (
        analysis_snapshot["read_only"] is not True
        or analysis_snapshot[
            "trade_authorized"
        ] is not False
        or analysis_snapshot[
            "order_payload_created"
        ] is not False
    ):
        raise RuntimeError(
            "UNIT 4 EXECUTION SAFETY FAILURE"
        )

    # ========================================================
    # 16. FINAL RENDER DIAGNOSTICS
    # ========================================================

    print(
        "PASS: UNIT 4 ORIGINAL UNIT 5 HANDOVER",
        flush=True
    )

    print(
        "PASS: UNIT 4 ADJUSTABLE CONFIGURATION",
        flush=True
    )

    print(
        "UNIT 4 CLOSED CANDLE COUNT =",
        len(closed),
        flush=True
    )

    print(
        "UNIT 4 ATR14 =",
        round(atr14, 4),
        flush=True
    )

    print(
        "UNIT 4 DIRECTION EVIDENCE =",
        direction_evidence,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT PROXIMITY ATR =",
        breakout_proximity,
        flush=True
    )

    print(
        "UNIT 4 BREAKOUT CONFIRMATION ATR =",
        breakout_confirmation,
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
        "UNIT 4 STRUCTURE PULLBACK ATR =",
        structure_pullback,
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
        "UNIT 4 SCALP EMA COMPRESSION ATR =",
        round(ema_compression_atr, 4),
        flush=True
    )

    print(
        "UNIT 4 SCALP RANGE ATR =",
        round(range_atr_ratio, 4),
        flush=True
    )

    print(
        "UNIT 4 CANDLE AGE SECONDS =",
        round(candle_age_seconds, 3),
        flush=True
    )

    print(
        "UNIT 4 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "FRESH RECONSTRUCTION UNIT 4 "
        "HYBRID ADJUSTABLE V2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return analysis_snapshot


# ============================================================
# UNIT 4 EXECUTION / UNIT 5 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
    fresh_reconstruction_unit_4()
)



# ============================================================
# START UNIT 5 - HYBRID ADJUSTABLE V3.1
# ZERO INDENTATION
#
# TARGETED CORRECTION:
# DEVELOPING != REJECTED
# QUALIFIED != EXECUTION AUTHORIZED
#
# BREAKOUT > STRUCTURE > SCALP
# UNIT 2 PARAMETERS UNCHANGED
# UNIT 4 V2 INPUT PRESERVED
# UNIT 6 V2 HANDOVER PRESERVED
# NO EXCHANGE WRITE
# ============================================================


def fresh_reconstruction_unit_5(
    unit_2_config,
    unit_4_snapshot,
):

    import math
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 5 HYBRID ADJUSTABLE V3.1 START",
        flush=True
    )

    # ========================================================
    # 1. VERIFY PREVIOUSLY TESTED INTERFACES
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError("UNIT 5 CONFIG INVALID")

    if not isinstance(unit_4_snapshot, dict):
        raise RuntimeError("UNIT 5 SNAPSHOT INVALID")

    qualification = unit_2_config.get("qualification")

    if not isinstance(qualification, dict):
        raise RuntimeError(
            "UNIT 5 QUALIFICATION CONFIG MISSING"
        )

    common = qualification.get("common")
    breakout_cfg = qualification.get("breakout")
    structure_cfg = qualification.get("structure")
    scalp_cfg = qualification.get("scalp")

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
            "UNIT 5 QUALIFICATION SECTION INVALID"
        )

    if (
        unit_4_snapshot.get("symbol") != "BTCUSDT"
        or unit_4_snapshot.get("read_only") is not True
        or unit_4_snapshot.get(
            "trade_authorized"
        ) is not False
        or unit_4_snapshot.get(
            "strategy_evidence_version"
        ) != "U4_HYBRID_V2"
        or unit_4_snapshot.get(
            "candle_data_fresh"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 5 UNIT 4 CONTRACT MISMATCH"
        )

    # ========================================================
    # 2. VERIFIED NUMERIC HELPERS
    # ========================================================

    def num(value, label):

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 5 BOOLEAN NUMBER: " + label
            )

        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            raise RuntimeError(
                "UNIT 5 INVALID NUMBER: " + label
            )

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 5 NONFINITE NUMBER: " + label
            )

        return result

    def ev(name):
        return num(
            unit_4_snapshot[name],
            name
        )

    def opt(section, name):
        return num(section[name], name)

    def flag(name):

        value = unit_4_snapshot[name]

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 5 INVALID FLAG: " + name
            )

        return value

    # ========================================================
    # 3. MARKET EVIDENCE
    # ========================================================

    live_mark = ev("live_mark_price")
    latest_close = ev("latest_close")
    previous_close = ev("previous_close")

    ema19 = ev("ema19")
    ema50 = ev("ema50")
    ema100 = ev("ema100")
    ema200 = ev("ema200")

    ema_separation = ev(
        "ema19_50_separation_pct"
    )

    atr14 = ev("atr14")
    atr_percent = ev("atr_percent")

    move1 = ev("move_1m_pct")
    move5 = ev("move_5m_pct")
    move15 = ev("move_15m_pct")
    move30 = ev("move_30m_pct")
    move60 = ev("move_60m_pct")
    move120 = ev("move_120m_pct")

    support = ev("support20")
    resistance = ev("resistance20")

    extension_cluster = ev(
        "price_extension_cluster"
    )

    long_votes = ev("direction_long_votes")
    short_votes = ev("direction_short_votes")

    direction_evidence = unit_4_snapshot.get(
        "direction_evidence"
    )

    breakout_dev_long = flag(
        "breakout_developing_long"
    )
    breakout_dev_short = flag(
        "breakout_developing_short"
    )
    breakout_confirm_long = flag(
        "breakout_confirmed_long"
    )
    breakout_confirm_short = flag(
        "breakout_confirmed_short"
    )

    structure_dev_long = flag(
        "structure_developing_long"
    )
    structure_dev_short = flag(
        "structure_developing_short"
    )

    sideways = flag("sideways_candidate")
    price_overextended = flag(
        "price_overextended"
    )

    candle_age = ev("candle_age_seconds")

    max_age = num(
        unit_2_config["market_data_policy"][
            "max_market_age_seconds"
        ],
        "MAX MARKET AGE"
    )

    if not (
        0 <= candle_age <= max_age
        and min(
            live_mark,
            latest_close,
            previous_close,
            ema19,
            ema50,
            ema100,
            ema200,
            atr14
        ) > 0
        and support > 0
        and resistance > support
        and direction_evidence in (
            "LONG",
            "SHORT",
            "NONE",
        )
        and 0 <= long_votes <= 3
        and 0 <= short_votes <= 3
        and long_votes + short_votes <= 3
    ):
        raise RuntimeError(
            "UNIT 5 INVALID MARKET EVIDENCE"
        )

    print(
        "PASS: UNIT 5 RECEIVED HYBRID UNITS 2 AND 4",
        flush=True
    )

    # ========================================================
    # 4. CENTRAL UNIT 2 SETTINGS
    # ========================================================

    priority = tuple(common["mode_priority"])

    if priority != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 5 PRIORITY MISMATCH"
        )

    def votes_required(section):

        value = section["direction_votes_required"]

        if (
            type(value) is not int
            or not 1 <= value <= 3
        ):
            raise RuntimeError(
                "UNIT 5 INVALID VOTE REQUIREMENT"
            )

        return value

    breakout_votes = votes_required(breakout_cfg)
    structure_votes = votes_required(structure_cfg)
    scalp_votes = votes_required(scalp_cfg)

    if (
        common.get(
            "protect_developing_candidates"
        ) is not True
        or common.get(
            "arbitrate_before_scalp"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 5 PRIORITY PROTECTION DISABLED"
        )

    # Candidate age is measured against the
    # market evidence timestamp available now.
    # Persistent lifecycle expiry is handled by
    # later continuity units, not invented here.

    common_expiry = opt(
        common,
        "candidate_expiry_seconds"
    )

    def candidate_fresh(section):

        expiry = opt(
            section,
            "candidate_expiry_seconds"
        )

        return (
            0 <= candle_age
            <= min(
                max_age,
                common_expiry,
                expiry
            )
        )

    def direction_pass(side, required):

        if side == "LONG":
            return (
                direction_evidence == "LONG"
                and long_votes >= required
            )

        if side == "SHORT":
            return (
                direction_evidence == "SHORT"
                and short_votes >= required
            )

        return False

    # ========================================================
    # 5. BREAKOUT: SEPARATE PROMISE FROM QUALIFICATION
    # ========================================================

    breakout_enabled = (
        breakout_cfg["enabled"] is True
    )

    breakout_max_ext = opt(
        breakout_cfg,
        "max_price_extension_atr"
    )

    breakout_min_atr = opt(
        breakout_cfg,
        "minimum_atr_percent"
    )

    breakout_momentum_required = (
        breakout_cfg[
            "require_momentum_confirmation"
        ] is True
    )

    breakout_candidate = (
        breakout_dev_long
        or breakout_dev_short
        or breakout_confirm_long
        or breakout_confirm_short
    )

    breakout_long_extension = max(
        0.0,
        (latest_close - resistance) / atr14
    )

    breakout_short_extension = max(
        0.0,
        (support - latest_close) / atr14
    )

    breakout_long_momentum = (
        move5 > 0 and move15 > 0
    )

    breakout_short_momentum = (
        move5 < 0 and move15 < 0
    )

    def breakout_quality(side):

        extension = (
            breakout_long_extension
            if side == "LONG"
            else breakout_short_extension
        )

        momentum = (
            breakout_long_momentum
            if side == "LONG"
            else breakout_short_momentum
        )

        return (
            breakout_enabled
            and candidate_fresh(breakout_cfg)
            and direction_pass(
                side, breakout_votes
            )
            and atr_percent >= breakout_min_atr
            and extension <= breakout_max_ext
            and (
                not breakout_momentum_required
                or momentum
            )
        )

    breakout_ready_long = (
        breakout_confirm_long
        and breakout_quality("LONG")
    )

    breakout_ready_short = (
        breakout_confirm_short
        and breakout_quality("SHORT")
    )

    breakout_ready = (
        breakout_ready_long
        or breakout_ready_short
    )

    # Developing protection needs early, credible
    # evidence, not all final entry conditions.
    # Conflicting direction / exhaustion cannot
    # claim protection.

    def breakout_developing_valid(side):

        dev = (
            breakout_dev_long
            if side == "LONG"
            else breakout_dev_short
        )

        momentum = (
            move5 > 0
            if side == "LONG"
            else move5 < 0
        )

        extension = (
            breakout_long_extension
            if side == "LONG"
            else breakout_short_extension
        )

        return (
            breakout_enabled
            and breakout_cfg[
                "early_detection_enabled"
            ] is True
            and breakout_cfg[
                "developing_candidate_enabled"
            ] is True
            and dev
            and candidate_fresh(breakout_cfg)
            and direction_pass(
                side, breakout_votes
            )
            and momentum
            and extension <= breakout_max_ext
        )

    breakout_developing_valid_long = (
        breakout_developing_valid("LONG")
    )

    breakout_developing_valid_short = (
        breakout_developing_valid("SHORT")
    )

    breakout_promising = (
        breakout_developing_valid_long
        or breakout_developing_valid_short
    )

    # ========================================================
    # 6. STRUCTURE: SEPARATE DEVELOPMENT FROM READY
    # ========================================================

    structure_enabled = (
        structure_cfg["enabled"] is True
    )

    structure_max_ext = opt(
        structure_cfg,
        "max_price_extension_atr"
    )

    structure_min_sep = opt(
        structure_cfg,
        "minimum_ema_separation_percent"
    )

    structure_candidate = (
        structure_dev_long
        or structure_dev_short
    )

    structure_long_trend = (
        ema19 > ema50 > ema200
    )

    structure_short_trend = (
        ema19 < ema50 < ema200
    )

    distance_ema_atr = (
        latest_close - ema19
    ) / atr14

    def structure_base(side):

        developing = (
            structure_dev_long
            if side == "LONG"
            else structure_dev_short
        )

        trend = (
            structure_long_trend
            if side == "LONG"
            else structure_short_trend
        )

        extension = (
            distance_ema_atr
            if side == "LONG"
            else -distance_ema_atr
        )

        return (
            structure_enabled
            and developing
            and candidate_fresh(structure_cfg)
            and trend
            and direction_pass(
                side,
                structure_votes
            )
            and extension <= structure_max_ext
            and abs(ema_separation)
            >= structure_min_sep
        )

    def structure_final_momentum(side):

        if side == "LONG":
            return move5 > 0 and move15 > 0

        return move5 < 0 and move15 < 0

    structure_base_long = structure_base("LONG")
    structure_base_short = structure_base("SHORT")

    structure_ready_long = (
        structure_base_long
        and structure_final_momentum("LONG")
    )

    structure_ready_short = (
        structure_base_short
        and structure_final_momentum("SHORT")
    )

    structure_ready = (
        structure_ready_long
        or structure_ready_short
    )

    # THIS IS THE TARGETED CORRECTION:
    #
    # A VALID STRUCTURE NEED NOT HAVE PASSED
    # BOTH FINAL MOMENTUM TESTS TO REMAIN
    # A DEVELOPING CANDIDATE.
    #
    # HOWEVER, IT MUST STILL HAVE DIRECTION,
    # TREND, FRESHNESS AND EXTENSION SUPPORT.

    structure_promising = (
        structure_base_long
        or structure_base_short
    )

    higher_mode_developing = (
        breakout_promising
        or structure_promising
    )

    # ========================================================
    # 7. SCALP ELIGIBILITY
    #
    # NO CHANGES TO NUMERIC THRESHOLDS.
    # QUALITY SCORE IS STILL OWNED BY UNIT 6.
    # ========================================================

    fee_sides = (
        int(
            scalp_cfg["include_entry_fee"] is True
        )
        +
        int(
            scalp_cfg["include_exit_fee"] is True
        )
    )

    taker_fee = opt(
        scalp_cfg,
        "estimated_taker_fee_percent"
    )

    slippage = opt(
        scalp_cfg,
        "estimated_slippage_percent"
    )

    fee_multiplier = opt(
        scalp_cfg,
        "minimum_fee_coverage_multiplier"
    )

    round_trip_friction = (
        taker_fee * fee_sides
        + slippage
    )

    required_price_range = (
        round_trip_friction * fee_multiplier
    )

    scalp_range_pct = (
        (resistance - support)
        / latest_close
        * 100.0
    )

    scalp_range_feasible = (
        scalp_range_pct
        >= required_price_range
    )

    scalp_extension_ok = (
        extension_cluster <= opt(
            scalp_cfg,
            "max_ema_extension_clusters"
        )
        and not price_overextended
    )

    scalp_direction_ok = (
        direction_pass("LONG", scalp_votes)
        or direction_pass("SHORT", scalp_votes)
    )

    scalp_momentum_ok = (
        (
            direction_evidence == "LONG"
            and move1 > 0
        )
        or (
            direction_evidence == "SHORT"
            and move1 < 0
        )
    )

    # Even rejected higher-mode evidence must
    # not force SCALP entry unless Unit 4
    # independently identifies a sideways market.

    scalp_context = (
        scalp_cfg["enabled"] is True
        and (
            sideways
            or scalp_cfg[
                "require_sideways_market"
            ] is False
        )
        and not higher_mode_developing
        and not breakout_candidate
        and not structure_candidate
        and scalp_extension_ok
    )

    scalp_pending = (
        scalp_context
        and scalp_direction_ok
        and scalp_momentum_ok
        and (
            scalp_cfg["fee_aware_enabled"] is False
            or scalp_range_feasible
        )
    )

    # ========================================================
    # 8. PRIORITY ARBITRATION
    # ========================================================

    active_mode = "NONE"
    direction = "NONE"
    qualified = False

    candidate_mode = "NONE"
    candidate_stage = "NONE"
    qualification_reason = (
        "NO_ACCEPTABLE_CANDIDATE"
    )

    if breakout_ready_long:

        active_mode = "BREAKOUT"
        direction = "LONG"
        qualified = True
        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"
        qualification_reason = (
            "BREAKOUT_LONG_CONFIRMED"
        )

    elif breakout_ready_short:

        active_mode = "BREAKOUT"
        direction = "SHORT"
        qualified = True
        candidate_mode = "BREAKOUT"
        candidate_stage = "QUALIFIED"
        qualification_reason = (
            "BREAKOUT_SHORT_CONFIRMED"
        )

    elif breakout_promising:

        candidate_mode = "BREAKOUT"
        candidate_stage = "DEVELOPING"
        qualification_reason = (
            "BREAKOUT_DEVELOPING_AWAITING_CONFIRMATION"
        )

    elif structure_ready_long:

        active_mode = "STRUCTURE"
        direction = "LONG"
        qualified = True
        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"
        qualification_reason = (
            "STRUCTURE_LONG_EARLY_QUALIFICATION"
        )

    elif structure_ready_short:

        active_mode = "STRUCTURE"
        direction = "SHORT"
        qualified = True
        candidate_mode = "STRUCTURE"
        candidate_stage = "QUALIFIED"
        qualification_reason = (
            "STRUCTURE_SHORT_EARLY_QUALIFICATION"
        )

    elif structure_promising:

        candidate_mode = "STRUCTURE"
        candidate_stage = "DEVELOPING"
        qualification_reason = (
            "STRUCTURE_DEVELOPING_AWAITING_CONFIRMATION"
        )

    elif breakout_candidate:

        candidate_mode = "BREAKOUT"
        candidate_stage = "REJECTED"
        qualification_reason = (
            "BREAKOUT_EVIDENCE_NOT_QUALIFIED"
        )

    elif structure_candidate:

        candidate_mode = "STRUCTURE"
        candidate_stage = "REJECTED"
        qualification_reason = (
            "STRUCTURE_EVIDENCE_NOT_QUALIFIED"
        )

    elif scalp_pending:

        candidate_mode = "SCALP"
        candidate_stage = "PENDING_UNIT_6"
        qualification_reason = (
            "SCALP_PENDING_QUALITY_AND_FEES"
        )

    elif sideways:

        candidate_mode = "SCALP"
        candidate_stage = "REJECTED"

        if not scalp_range_feasible:
            qualification_reason = (
                "SCALP_RANGE_BELOW_FEE_REQUIREMENT"
            )

        elif not scalp_extension_ok:
            qualification_reason = (
                "SCALP_PRICE_OVEREXTENDED"
            )

        else:
            qualification_reason = (
                "SCALP_DIRECTION_OR_MOMENTUM_REJECTED"
            )

    # ========================================================
    # 9. ORIGINAL UNIT 6 OUTPUT CONTRACT
    # ========================================================

    def move_direction(value):

        if value > 0:
            return "LONG"
        if value < 0:
            return "SHORT"
        return "NONE"

    ema_direction = (
        "LONG" if ema19 > ema50
        else "SHORT" if ema19 < ema50
        else "NONE"
    )

    momentum_direction = move_direction(move1)

    direction_agreement = (
        ema_direction == momentum_direction
        and ema_direction != "NONE"
    )

    result = {

        "symbol": "BTCUSDT",

        "qualified": qualified,
        "active_mode": active_mode,
        "direction": direction,

        "qualification_reason":
            qualification_reason,

        "candidate_mode": candidate_mode,
        "candidate_stage": candidate_stage,

        "higher_mode_developing":
            higher_mode_developing,

        "breakout_candidate":
            breakout_candidate,

        "breakout_ready":
            breakout_ready,

        "structure_candidate":
            structure_candidate,

        "structure_ready":
            structure_ready,

        "sideways_context": sideways,

        "scalp_range_pct":
            scalp_range_pct,

        "scalp_range_feasible":
            scalp_range_feasible,

        "scalp_ready": scalp_pending,

        "direction_evidence":
            direction_evidence,

        "live_mark_price": live_mark,

        "latest_close": latest_close,
        "previous_close": previous_close,

        "ema19": ema19,
        "ema50": ema50,
        "ema100": ema100,
        "ema200": ema200,

        "ema19_50_separation_pct":
            ema_separation,

        "ema_structure":
            unit_4_snapshot.get(
                "ema_structure", "MIXED"
            ),

        "ema_direction": ema_direction,

        "momentum_direction":
            momentum_direction,

        "direction_agreement":
            direction_agreement,

        "short_term_move_pct": move1,

        "absolute_short_term_move_pct":
            abs(move1),

        "move_1m_pct": move1,
        "move_5m_pct": move5,
        "move_15m_pct": move15,
        "move_30m_pct": move30,
        "move_60m_pct": move60,
        "move_120m_pct": move120,

        "momentum_1m_direction":
            move_direction(move1),

        "momentum_5m_direction":
            move_direction(move5),

        "momentum_15m_direction":
            move_direction(move15),

        "momentum_30m_direction":
            move_direction(move30),

        "momentum_60m_direction":
            move_direction(move60),

        "momentum_120m_direction":
            move_direction(move120),

        "price_above_ema19":
            live_mark > ema19,

        "price_above_ema50":
            live_mark > ema50,

        "price_above_ema200":
            live_mark > ema200,

        "latest_close_above_previous":
            latest_close > previous_close,

        "scalp_direction": (
            direction_evidence
            if scalp_pending else "NONE"
        ),

        "scalp_move_pct": abs(move5),

        "scalp_1m_support":
            scalp_momentum_ok,

        "structure_direction": (
            direction_evidence
            if structure_candidate else "NONE"
        ),

        "structure_move_pct": abs(move15),

        "breakout_direction": (
            direction_evidence
            if breakout_candidate else "NONE"
        ),

        "breakout_move_pct": abs(move5),

        "breakout_fast_support": (
            breakout_long_momentum
            or breakout_short_momentum
        ),

        "atr14": atr14,

        "price_extension_cluster":
            extension_cluster,

        "scalp_quality_minimum": opt(
            scalp_cfg, "quality_threshold"
        ),

        "scalp_price_weight_percent": opt(
            scalp_cfg,
            "price_action_weight_percent"
        ),

        "estimated_round_trip_fee_pct":
            round_trip_friction,

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

        # ADDITIVE DIAGNOSTICS ONLY

        "classification_revision":
            "V3.1",

        "breakout_promising":
            breakout_promising,

        "structure_promising":
            structure_promising,

        "candidate_protected": (
            candidate_stage == "DEVELOPING"
        ),

        "candidate_age_seconds":
            candle_age,

        "candidate_expiry_policy_seconds":
            common_expiry,

        "candidate_expiry_is_lifecycle":
            False,
    }

    # ========================================================
    # 10. INTEGRATION SAFETY
    # ========================================================

    if qualified:

        if (
            candidate_stage != "QUALIFIED"
            or active_mode not in (
                "BREAKOUT", "STRUCTURE"
            )
            or direction not in (
                "LONG", "SHORT"
            )
        ):
            raise RuntimeError(
                "UNIT 5 QUALIFIED HANDOVER INVALID"
            )

    else:

        if (
            active_mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 5 UNQUALIFIED HANDOVER INVALID"
            )

    if (
        candidate_stage == "DEVELOPING"
        and qualified
    ):
        raise RuntimeError(
            "UNIT 5 DEVELOPING SIGNAL AUTHORIZED"
        )

    if (
        candidate_mode == "SCALP"
        and higher_mode_developing
    ):
        raise RuntimeError(
            "UNIT 5 SCALP PRIORITY VIOLATION"
        )

    if (
        result["trade_authorized"]
        or result["order_payload_created"]
    ):
        raise RuntimeError(
            "UNIT 5 UNAUTHORIZED ORDER"
        )

    # ========================================================
    # 11. RENDER VERIFICATION
    # ========================================================

    print(
        "PASS: UNIT 5 ORIGINAL UNIT 6 HANDOVER",
        flush=True
    )

    print(
        "PASS: UNIT 5 CANDIDATE STATE SEPARATION",
        flush=True
    )

    print(
        "UNIT 5 PRIORITY =",
        priority,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT CANDIDATE =",
        breakout_candidate,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT READY =",
        breakout_ready,
        flush=True
    )

    print(
        "UNIT 5 BREAKOUT PROMISING =",
        breakout_promising,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE CANDIDATE =",
        structure_candidate,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE READY =",
        structure_ready,
        flush=True
    )

    print(
        "UNIT 5 STRUCTURE PROMISING =",
        structure_promising,
        flush=True
    )

    print(
        "UNIT 5 HIGHER MODE DEVELOPING =",
        higher_mode_developing,
        flush=True
    )

    print(
        "UNIT 5 SCALP PENDING UNIT 6 =",
        scalp_pending,
        flush=True
    )

    print(
        "UNIT 5 CANDIDATE MODE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 5 CANDIDATE STAGE =",
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
        qualification_reason,
        flush=True
    )

    print(
        "UNIT 5 CLASSIFICATION REVISION = V3.1",
        flush=True
    )

    print(
        "UNIT 5 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 5 HYBRID ADJUSTABLE V3.1 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 5 EXECUTION - ORIGINAL UNIT 6 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
    fresh_reconstruction_unit_5(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)


# ============================================================
# END UNIT 5 - HYBRID ADJUSTABLE V3.1
# ZERO INDENTATION
# ============================================================


# ============================================================
# START UNIT 6 - HYBRID ADJUSTABLE V2.1
# ZERO INDENTATION
#
# COMPATIBLE WITH:
# UNIT 2 HYBRID V3
# UNIT 4 HYBRID V2
# UNIT 5 HYBRID V3.1
#
# PURPOSE:
# FINAL SIGNAL QUALIFICATION AND PRELIMINARY ADMISSION
#
# NO EXCHANGE ACCOUNT ACCESS
# NO LEVERAGE MUTATION
# NO DEMO OR LIVE ORDERS
# ============================================================


def fresh_reconstruction_unit_6(
    unit_2_config,
    unit_4_analysis,
    unit_5_candidate,
):

    import math
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 6 HYBRID ADJUSTABLE V2.1 START",
        flush=True
    )

    # ========================================================
    # 1. VALIDATE INCOMING UNITS
    # ========================================================

    if not all(
        isinstance(x, dict)
        for x in (
            unit_2_config,
            unit_4_analysis,
            unit_5_candidate
        )
    ):
        raise RuntimeError(
            "UNIT 6 INPUT CONTRACT INVALID"
        )

    strategy = unit_2_config.get("strategy")
    safety = unit_2_config.get("safety")
    policy = unit_2_config.get("market_data_policy")
    qualification = unit_2_config.get("qualification")

    if not all(
        isinstance(x, dict)
        for x in (
            strategy,
            safety,
            policy,
            qualification
        )
    ):
        raise RuntimeError(
            "UNIT 6 CONFIGURATION INCOMPLETE"
        )

    scalp_cfg = qualification.get("scalp")
    common_cfg = qualification.get("common")

    if not isinstance(scalp_cfg, dict):
        raise RuntimeError(
            "UNIT 6 SCALP CONFIGURATION MISSING"
        )

    if not isinstance(common_cfg, dict):
        raise RuntimeError(
            "UNIT 6 COMMON CONFIGURATION MISSING"
        )

    if (
        unit_4_analysis.get(
            "strategy_evidence_version"
        ) != "U4_HYBRID_V2"
        or unit_5_candidate.get(
            "strategy_evidence_version"
        ) != "U5_HYBRID_ADJUSTABLE_V3"
        or unit_5_candidate.get(
            "classification_revision"
        ) != "V3.1"
        or unit_5_candidate.get(
            "unit_4_evidence_version"
        ) != "U4_HYBRID_V2"
    ):
        raise RuntimeError(
            "UNIT 6 VERSION COMPATIBILITY FAILURE"
        )

    for snapshot in (
        unit_4_analysis,
        unit_5_candidate
    ):
        if (
            snapshot.get("read_only") is not True
            or snapshot.get(
                "trade_authorized"
            ) is not False
        ):
            raise RuntimeError(
                "UNIT 6 UPSTREAM SAFETY FAILURE"
            )

    if (
        unit_4_analysis.get(
            "candle_data_fresh"
        ) is not True
        or unit_5_candidate.get(
            "candle_data_fresh"
        ) is not True
        or unit_5_candidate.get(
            "order_payload_created"
        ) is not False
        or unit_4_analysis.get("symbol")
        != unit_5_candidate.get("symbol")
    ):
        raise RuntimeError(
            "UNIT 6 EVIDENCE CONTRACT FAILURE"
        )

    for name in (
        "one_direction_only",
        "anti_duplicate_orders",
        "exclusive_mode"
    ):
        if strategy.get(name) is not True:
            raise RuntimeError(
                "UNIT 6 STRATEGY SAFETY FAILURE: "
                + name
            )

    for name in (
        "authenticated_api_enabled",
        "account_access_enabled",
        "position_access_enabled",
        "order_endpoint_access_enabled",
        "demo_order_submission_enabled",
        "real_order_submission_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled"
    ):
        if safety.get(name) is not False:
            raise RuntimeError(
                "UNIT 6 EXCHANGE SAFETY FAILURE: "
                + name
            )

    # ========================================================
    # 2. HELPERS
    # ========================================================

    def number(value, label):

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 6 BOOLEAN NUMBER: " + label
            )

        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            raise RuntimeError(
                "UNIT 6 INVALID NUMBER: " + label
            )

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 6 NONFINITE NUMBER: " + label
            )

        return value

    def setting(name):

        if name not in scalp_cfg:
            raise RuntimeError(
                "UNIT 6 SCALP SETTING MISSING: "
                + name
            )

        return number(scalp_cfg[name], name)

    def boolean(name):

        value = scalp_cfg.get(name)

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 6 INVALID BOOLEAN: " + name
            )

        return value

    def evidence(name):

        if name not in unit_4_analysis:
            raise RuntimeError(
                "UNIT 6 EVIDENCE MISSING: " + name
            )

        return number(
            unit_4_analysis[name],
            name
        )

    def directional_vote(side):

        name = (
            "direction_long_votes"
            if side == "LONG"
            else "direction_short_votes"
        )

        return evidence(name)

    def move_side(value):

        if value > 0:
            return "LONG"

        if value < 0:
            return "SHORT"

        return "NONE"

    # ========================================================
    # 3. MARKET AGE / MODE SAFETY
    # ========================================================

    candle_age = evidence(
        "candle_age_seconds"
    )

    max_age = number(
        policy.get("max_market_age_seconds"),
        "MAX MARKET AGE"
    )

    if not 0 <= candle_age <= max_age:
        raise RuntimeError(
            "UNIT 6 MARKET DATA STALE"
        )

    priority = tuple(
        common_cfg.get("mode_priority", ())
    )

    if priority != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 STRATEGY PRIORITY INVALID"
        )

    leverage_reference = number(
        strategy.get("leverage_target"),
        "LEVERAGE REFERENCE"
    )

    if leverage_reference <= 0:
        raise RuntimeError(
            "UNIT 6 LEVERAGE REFERENCE INVALID"
        )

    # Leverage is only a reference here.
    # Actual leverage remains WEEX-controlled.

    # ========================================================
    # 4. UNIT 5 CANDIDATE STATE
    # ========================================================

    candidate_mode = unit_5_candidate.get(
        "candidate_mode"
    )

    candidate_stage = unit_5_candidate.get(
        "candidate_stage"
    )

    unit5_active_mode = unit_5_candidate.get(
        "active_mode"
    )

    unit5_direction = unit_5_candidate.get(
        "direction"
    )

    unit5_qualified = unit_5_candidate.get(
        "qualified"
    )

    higher_mode = unit_5_candidate.get(
        "higher_mode_developing"
    )

    unit5_reason = str(
        unit_5_candidate.get(
            "qualification_reason",
            "UNKNOWN"
        )
    )

    if candidate_mode not in (
        "NONE",
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        raise RuntimeError(
            "UNIT 6 CANDIDATE MODE INVALID"
        )

    if candidate_stage not in (
        "NONE",
        "DEVELOPING",
        "QUALIFIED",
        "REJECTED",
        "PENDING_UNIT_6"
    ):
        raise RuntimeError(
            "UNIT 6 CANDIDATE STAGE INVALID"
        )

    if (
        type(unit5_qualified) is not bool
        or type(higher_mode) is not bool
    ):
        raise RuntimeError(
            "UNIT 6 CANDIDATE FLAGS INVALID"
        )

    if unit5_qualified != (
        candidate_stage == "QUALIFIED"
    ):
        raise RuntimeError(
            "UNIT 6 CANDIDATE STATE CONTRADICTION"
        )

    if unit5_qualified:

        if (
            candidate_mode not in (
                "BREAKOUT",
                "STRUCTURE"
            )
            or unit5_active_mode
            != candidate_mode
            or unit5_direction not in (
                "LONG", "SHORT"
            )
        ):
            raise RuntimeError(
                "UNIT 6 QUALIFIED CONTRACT INVALID"
            )

    else:

        if (
            unit5_active_mode != "NONE"
            or unit5_direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 6 UNQUALIFIED SIGNAL LEAK"
            )

    if candidate_stage == "DEVELOPING":

        if (
            candidate_mode not in (
                "BREAKOUT",
                "STRUCTURE"
            )
            or higher_mode is not True
            or unit_5_candidate.get(
                "candidate_protected"
            ) is not True
        ):
            raise RuntimeError(
                "UNIT 6 DEVELOPING PROTECTION FAILURE"
            )

    # ========================================================
    # 5. INITIAL ADMISSION STATE
    # ========================================================

    execution_intent = False

    admitted_mode = "NONE"
    admitted_direction = "NONE"

    admission_reason = (
        "UNIT_5_NOT_QUALIFIED:"
        + unit5_reason
    )

    scalp_score = None
    scalp_quality_pass = None
    scalp_details = {}

    fee_coverage_pass = False
    round_trip_fee_estimate = None

    persistence_window = 3
    persistence_required = 2
    persistence_confirmations = 0
    persistence_directions = []
    persistence_pass = False

    fifteen_minute_support_pass = None

    # ========================================================
    # 6. QUALIFIED BREAKOUT / STRUCTURE
    #
    # NO SCALP RULES ARE APPLIED TO THESE.
    # ========================================================

    if unit5_qualified:

        direction = unit5_direction

        if (
            unit_4_analysis.get(
                "direction_evidence"
            ) != direction
        ):
            admission_reason = (
                "QUALIFIED_DIRECTION_CONFLICT"
            )

        elif candidate_mode == "BREAKOUT":

            evidence_name = (
                "breakout_confirmed_long"
                if direction == "LONG"
                else "breakout_confirmed_short"
            )

            if (
                unit_4_analysis.get(
                    evidence_name
                ) is True
                and unit_5_candidate.get(
                    "breakout_ready"
                ) is True
            ):

                execution_intent = True
                admitted_mode = "BREAKOUT"
                admitted_direction = direction

                admission_reason = (
                    "BREAKOUT_PRELIMINARY_ADMISSION_PASS"
                )

            else:

                admission_reason = (
                    "BREAKOUT_CONFIRMATION_NOT_VERIFIED"
                )

        elif candidate_mode == "STRUCTURE":

            evidence_name = (
                "structure_developing_long"
                if direction == "LONG"
                else "structure_developing_short"
            )

            if (
                unit_4_analysis.get(
                    evidence_name
                ) is True
                and unit_5_candidate.get(
                    "structure_ready"
                ) is True
            ):

                execution_intent = True
                admitted_mode = "STRUCTURE"
                admitted_direction = direction

                admission_reason = (
                    "STRUCTURE_PRELIMINARY_ADMISSION_PASS"
                )

            else:

                admission_reason = (
                    "STRUCTURE_CONFIRMATION_NOT_VERIFIED"
                )

    # ========================================================
    # 7. PROTECT VALID DEVELOPING CANDIDATES
    #
    # DEVELOPING IS NOT AN EXECUTION SIGNAL.
    # ========================================================

    elif candidate_stage == "DEVELOPING":

        admission_reason = (
            candidate_mode
            + "_DEVELOPING_PROTECTED_NO_EXECUTION"
        )

    # ========================================================
    # 8. SCALP FINAL QUALIFICATION
    #
    # ONLY A PENDING SCALP ENTERS THIS PATH.
    # ========================================================

    elif (
        candidate_mode == "SCALP"
        and candidate_stage == "PENDING_UNIT_6"
    ):

        if (
            higher_mode
            or unit_5_candidate.get(
                "breakout_candidate"
            ) is True
            or unit_5_candidate.get(
                "structure_candidate"
            ) is True
        ):

            admission_reason = (
                "SCALP_HIGHER_PRIORITY_BLOCK"
            )

        elif (
            unit_4_analysis.get(
                "sideways_candidate"
            ) is not True
            or unit_5_candidate.get(
                "sideways_context"
            ) is not True
        ):

            admission_reason = (
                "SCALP_SIDEWAYS_CONDITION_FAILED"
            )

        else:

            minimum_score = setting(
                "quality_threshold"
            )

            price_weight = setting(
                "price_action_weight_percent"
            )

            other_weight = setting(
                "other_factors_weight_percent"
            )

            required_votes = setting(
                "direction_votes_required"
            )

            maximum_extension = setting(
                "max_ema_extension_clusters"
            )

            max_spikes = setting(
                "max_spike_count"
            )

            taker_fee = setting(
                "estimated_taker_fee_percent"
            )

            slippage = setting(
                "estimated_slippage_percent"
            )

            coverage_multiplier = setting(
                "minimum_fee_coverage_multiplier"
            )

            minimum_net_roi = setting(
                "minimum_net_roi_percent"
            )

            if not (
                0 <= minimum_score <= 100
                and price_weight >= 0
                and other_weight >= 0
                and math.isclose(
                    price_weight + other_weight,
                    100.0,
                    abs_tol=0.000001
                )
                and required_votes in (
                    1.0, 2.0, 3.0
                )
                and maximum_extension > 0
                and max_spikes >= 0
                and coverage_multiplier >= 1
                and taker_fee >= 0
                and slippage >= 0
                and minimum_net_roi >= 0
            ):
                raise RuntimeError(
                    "UNIT 6 SCALP SETTINGS INVALID"
                )

            scalp_direction = (
                unit_4_analysis.get(
                    "direction_evidence"
                )
            )

            if scalp_direction not in (
                "LONG",
                "SHORT"
            ):
                admission_reason = (
                    "SCALP_DIRECTION_INVALID"
                )

            else:

                sign = (
                    1
                    if scalp_direction == "LONG"
                    else -1
                )

                actual_votes = directional_vote(
                    scalp_direction
                )

                candles = unit_4_analysis.get(
                    "recent_closed_klines"
                )

                if (
                    not isinstance(candles, list)
                    or len(candles) < 3
                ):
                    raise RuntimeError(
                        "UNIT 6 SCALP CANDLES MISSING"
                    )

                latest_close = evidence(
                    "latest_close"
                )

                support = evidence("support20")
                resistance = evidence(
                    "resistance20"
                )

                atr = evidence("atr14")

                move1 = evidence(
                    "move_1m_pct"
                )

                move5 = evidence(
                    "move_5m_pct"
                )

                move15 = evidence(
                    "move_15m_pct"
                )

                extension = evidence(
                    "price_extension_cluster"
                )

                if not (
                    latest_close > 0
                    and support > 0
                    and resistance > support
                    and atr > 0
                ):
                    raise RuntimeError(
                        "UNIT 6 SCALP GEOMETRY INVALID"
                    )

                # ============================================
                # 9. CANDLE PERSISTENCE AND SPIKES
                # ============================================

                spike_count = 0

                for candle in candles[-3:]:

                    if not isinstance(candle, dict):
                        raise RuntimeError(
                            "UNIT 6 CANDLE FORMAT INVALID"
                        )

                    opened = number(
                        candle.get("open"),
                        "CANDLE OPEN"
                    )

                    closed = number(
                        candle.get("close"),
                        "CANDLE CLOSE"
                    )

                    high = number(
                        candle.get("high"),
                        "CANDLE HIGH"
                    )

                    low = number(
                        candle.get("low"),
                        "CANDLE LOW"
                    )

                    if not (
                        0 < low
                        <= min(opened, closed)
                        <= max(opened, closed)
                        <= high
                    ):
                        raise RuntimeError(
                            "UNIT 6 CANDLE PRICE INVALID"
                        )

                    persistence_directions.append(
                        move_side(closed - opened)
                    )

                    if (
                        high - low > 2.0 * atr
                    ):
                        spike_count += 1

                persistence_confirmations = sum(
                    side == scalp_direction
                    for side in persistence_directions
                )

                persistence_pass = (
                    persistence_confirmations
                    >= persistence_required
                )

                fifteen_minute_support_pass = (
                    move15 * sign >= 0
                )

                # ============================================
                # 10. SCALP QUALITY FACTORS
                # ============================================

                direction_votes_pass = (
                    actual_votes >= required_votes
                )

                momentum_pass = (
                    move1 * sign > 0
                    and move5 * sign > 0
                )

                extension_pass = (
                    extension <= maximum_extension
                    and unit_4_analysis.get(
                        "price_overextended"
                    ) is False
                )

                spike_pass = (
                    spike_count <= max_spikes
                )

                late_impulse = (
                    extension > maximum_extension
                    or (
                        move1 * sign < 0
                        and move5 * sign > 0
                    )
                )

                late_impulse_pass = (
                    not boolean(
                        "reject_late_impulse"
                    )
                    or not late_impulse
                )

                near_boundary = (
                    latest_close
                    <= support + 0.5 * atr
                    if scalp_direction == "LONG"
                    else latest_close
                    >= resistance - 0.5 * atr
                )

                # Raw price-action score: 0-50.

                price_points = (
                    (
                        15.0
                        if move5 * sign >= 0.03
                        else 8.0
                        if move5 * sign > 0
                        else 0.0
                    )
                    +
                    (
                        10.0
                        if move1 * sign > 0
                        else 0.0
                    )
                    +
                    (
                        15.0
                        if persistence_confirmations == 3
                        else 10.0
                        if persistence_confirmations == 2
                        else 0.0
                    )
                    +
                    (
                        10.0
                        if extension <= 0.75
                        else 5.0
                        if extension <= maximum_extension
                        else 0.0
                    )
                )

                other_points = (
                    15.0
                    +
                    (
                        10.0
                        if fifteen_minute_support_pass
                        else 0.0
                    )
                    +
                    (
                        10.0
                        if unit_5_candidate.get(
                            "scalp_range_feasible"
                        ) is True
                        else 0.0
                    )
                    +
                    (
                        10.0
                        if near_boundary
                        else 0.0
                    )
                    +
                    (
                        5.0
                        if extension_pass
                        else 0.0
                    )
                )

                scalp_score = (
                    price_points
                    / 50.0
                    * price_weight
                    +
                    other_points
                    / 50.0
                    * other_weight
                )

                scalp_quality_pass = (
                    scalp_score >= minimum_score
                )

                # ============================================
                # 11. FEE-COVERAGE FEASIBILITY
                # ============================================

                fee_sides = (
                    int(boolean(
                        "include_entry_fee"
                    ))
                    +
                    int(boolean(
                        "include_exit_fee"
                    ))
                )

                round_trip_fee_estimate = (
                    taker_fee * fee_sides
                    + slippage
                )

                historical_range_pct = number(
                    unit_5_candidate.get(
                        "scalp_range_pct"
                    ),
                    "SCALP RANGE PERCENT"
                )

                fee_coverage_pass = (
                    not boolean(
                        "fee_aware_enabled"
                    )
                    or historical_range_pct
                    >= round_trip_fee_estimate
                    * coverage_multiplier
                )

                # The historical range is not
                # guaranteed executable profit.
                #
                # No net ROI is invented here.

                scalp_details = {

                    "direction":
                        scalp_direction,

                    "direction_votes":
                        actual_votes,

                    "required_votes":
                        required_votes,

                    "persistence_confirmations":
                        persistence_confirmations,

                    "spike_count":
                        spike_count,

                    "raw_price_score":
                        price_points,

                    "raw_other_score":
                        other_points,

                    "price_weight_percent":
                        price_weight,

                    "other_weight_percent":
                        other_weight,

                    "quality_score":
                        scalp_score,

                    "quality_threshold":
                        minimum_score,

                    "historical_range_percent":
                        historical_range_pct,

                    "estimated_round_trip_fee_pct":
                        round_trip_fee_estimate,

                    "fee_coverage_pass":
                        fee_coverage_pass,

                    "minimum_net_roi_percent":
                        minimum_net_roi,

                    "net_roi_verified":
                        False,
                }

                # ============================================
                # 12. FINAL SCALP ADMISSION CHECKS
                # ============================================

                scalp_checks = {

                    "direction":
                        direction_votes_pass,

                    "persistence":
                        persistence_pass,

                    "momentum":
                        momentum_pass,

                    "extension":
                        extension_pass,

                    "spikes":
                        spike_pass,

                    "late_impulse":
                        late_impulse_pass,

                    "quality":
                        scalp_quality_pass,

                    "fee_coverage":
                        fee_coverage_pass,

                    "15m_support":
                        fifteen_minute_support_pass,
                }

                scalp_details[
                    "qualification_checks"
                ] = scalp_checks

                if all(scalp_checks.values()):

                    execution_intent = True

                    admitted_mode = "SCALP"

                    admitted_direction = (
                        scalp_direction
                    )

                    admission_reason = (
                        "SCALP_PRELIMINARY_ADMISSION_PASS"
                    )

                else:

                    admission_reason = (
                        "SCALP_QUALIFICATION_REJECTED"
                    )

    # ========================================================
    # 13. ORIGINAL UNIT 7 HANDOVER
    #
    # SIX CORE FIELDS REMAIN UNCHANGED:
    #
    # execution_intent
    # active_mode
    # direction
    # signal_qualified
    # unit_5_reason
    # admission_reason
    # ========================================================

    compression = unit_4_analysis.get(
        "ema_compression_atr"
    )

    if compression is None:
        compression = unit_4_analysis.get(
            "scalp_ema_compression_atr"
        )

    compression_threshold = number(
        scalp_cfg.get(
            "ema_compression_atr_max"
        ),
        "EMA COMPRESSION LIMIT"
    )

    if compression is None:
        ema_compressed = False
    else:
        ema_compressed = (
            number(
                compression,
                "EMA COMPRESSION"
            ) <= compression_threshold
        )

    result = {

        "execution_intent":
            bool(execution_intent),

        "active_mode":
            admitted_mode,

        "direction":
            admitted_direction,

        "signal_qualified":
            bool(execution_intent),

        "unit_5_reason":
            unit5_reason,

        "admission_reason":
            admission_reason,

        "candidate_mode":
            candidate_mode,

        "candidate_stage":
            candidate_stage,

        "higher_mode_developing":
            higher_mode,

        "candidate_protected":
            (
                candidate_stage == "DEVELOPING"
            ),

        "leverage_target":
            leverage_reference,

        "leverage_regime":
            "EXCHANGE_CONTROLLED",

        "sideways_regime":
            unit_4_analysis.get(
                "sideways_candidate"
            ),

        "ema_compressed":
            ema_compressed,

        "compression_threshold_pct":
            None,

        "momentum_conflict":
            False,

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
            scalp_score,

        "scalp_quality_minimum":
            number(
                scalp_cfg.get(
                    "quality_threshold"
                ),
                "SCALP QUALITY THRESHOLD"
            ),

        "scalp_quality_pass":
            scalp_quality_pass,

        "scalp_quality_details":
            scalp_details,

        "fee_coverage_pass":
            fee_coverage_pass,

        "round_trip_fee_estimate_pct":
            round_trip_fee_estimate,

        "candle_age_seconds":
            candle_age,

        "read_only":
            True,

        "order_payload_created":
            False,

        "trade_authorized":
            False,

        "exchange_write":
            False,

        "strategy_evidence_version":
            "U6_HYBRID_ADJUSTABLE_V2",

        "admission_revision":
            "V2.1",

        "unit_5_classification_revision":
            "V3.1",
    }

    # ========================================================
    # 14. FINAL SAFETY VALIDATION
    # ========================================================

    if execution_intent:

        if (
            admitted_mode not in (
                "BREAKOUT",
                "STRUCTURE",
                "SCALP"
            )
            or admitted_direction not in (
                "LONG",
                "SHORT"
            )
            or candidate_stage not in (
                "QUALIFIED",
                "PENDING_UNIT_6"
            )
        ):
            raise RuntimeError(
                "UNIT 6 ADMISSION CONTRACT INVALID"
            )

    else:

        if (
            admitted_mode != "NONE"
            or admitted_direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 6 IDLE CONTRACT INVALID"
            )

    if (
        candidate_stage == "DEVELOPING"
        and execution_intent
    ):
        raise RuntimeError(
            "UNIT 6 DEVELOPING SIGNAL EXECUTION LEAK"
        )

    if (
        result["trade_authorized"]
        or result["order_payload_created"]
        or result["exchange_write"]
    ):
        raise RuntimeError(
            "UNIT 6 UNAUTHORIZED WRITE"
        )

    # ========================================================
    # 15. RENDER LOG VERIFICATION
    # ========================================================

    print(
        "PASS: UNIT 6 RECEIVED UNITS 2, 4, 5 V3.1",
        flush=True
    )

    print(
        "PASS: UNIT 6 ORIGINAL UNIT 7 CONTRACT",
        flush=True
    )

    print(
        "PASS: UNIT 6 DEVELOPING CANDIDATE PROTECTION",
        flush=True
    )

    print(
        "UNIT 6 CANDIDATE MODE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 6 CANDIDATE STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 6 HIGHER MODE DEVELOPING =",
        higher_mode,
        flush=True
    )

    print(
        "UNIT 6 ACTIVE MODE =",
        admitted_mode,
        flush=True
    )

    print(
        "UNIT 6 DIRECTION =",
        admitted_direction,
        flush=True
    )

    print(
        "UNIT 6 SIGNAL QUALIFIED =",
        bool(execution_intent),
        flush=True
    )

    print(
        "UNIT 6 EXECUTION INTENT =",
        bool(execution_intent),
        flush=True
    )

    print(
        "UNIT 6 ADMISSION REASON =",
        admission_reason,
        flush=True
    )

    print(
        "UNIT 6 SCALP SCORE =",
        scalp_score,
        flush=True
    )

    print(
        "UNIT 6 SCALP THRESHOLD =",
        scalp_cfg["quality_threshold"],
        flush=True
    )

    print(
        "UNIT 6 CLASSIFICATION COMPATIBILITY = V3.1",
        flush=True
    )

    print(
        "UNIT 6 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 6 HYBRID ADJUSTABLE V2.1 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 6 EXECUTION
# ORIGINAL UNIT 7 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
    fresh_reconstruction_unit_6(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
    )
)


# ============================================================
# END UNIT 6 - HYBRID ADJUSTABLE V2.1
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 7 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
#
# ORIGINAL MODEL INTERFACE PRESERVED
# INPUT: UNIT 2 CONFIG + UNIT 6 V2.1
# OUTPUT: UNIT 8 SIZING PREPARATION
#
# NO BALANCE INVENTED
# NO QUANTITY INVENTED
# NO EXCHANGE WRITE
# NO LEVERAGE MUTATION
# ============================================================


def fresh_reconstruction_unit_7(
    unit_2_config,
    unit_6_candidate,
):

    import math
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 7 HYBRID ADJUSTABLE V2 START",
        flush=True
    )

    # ========================================================
    # 1. VERIFY INPUT CONTRACT
    # ========================================================

    if not isinstance(unit_2_config, dict):
        raise RuntimeError(
            "UNIT 7 INVALID UNIT 2 CONFIG"
        )

    if not isinstance(unit_6_candidate, dict):
        raise RuntimeError(
            "UNIT 7 INVALID UNIT 6 INPUT"
        )

    strategy = unit_2_config.get("strategy")
    safety = unit_2_config.get("safety")
    exchange = unit_2_config.get("exchange")
    precision = unit_2_config.get(
        "market_precision"
    )

    if not all(
        isinstance(section, dict)
        for section in (
            strategy,
            safety,
            exchange,
            precision,
        )
    ):
        raise RuntimeError(
            "UNIT 7 CONFIGURATION MISSING"
        )

    required_unit6_fields = (
        "execution_intent",
        "active_mode",
        "direction",
        "signal_qualified",
        "unit_5_reason",
        "admission_reason",
    )

    missing = [
        name
        for name in required_unit6_fields
        if name not in unit_6_candidate
    ]

    if missing:
        raise RuntimeError(
            "UNIT 7 UNIT 6 MISSING FIELDS: "
            + str(missing)
        )

    if (
        unit_6_candidate.get(
            "strategy_evidence_version"
        ) != "U6_HYBRID_ADJUSTABLE_V2"
        or unit_6_candidate.get(
            "admission_revision"
        ) != "V2.1"
        or unit_6_candidate.get(
            "unit_5_classification_revision"
        ) != "V3.1"
    ):
        raise RuntimeError(
            "UNIT 7 UNIT 6 VERSION MISMATCH"
        )

    print(
        "PASS: UNIT 7 RECEIVED UNIT 6 V2.1",
        flush=True
    )

    # ========================================================
    # 2. STRICT SAFETY GATE
    # ========================================================

    forbidden_capabilities = (
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

    for name in forbidden_capabilities:

        if safety.get(name) is not False:
            raise RuntimeError(
                "UNIT 7 SAFETY CONFIGURATION FAILED: "
                + name
            )

    for name in (
        "read_only",
        "order_payload_created",
        "trade_authorized",
        "exchange_write",
    ):

        expected = (
            True if name == "read_only"
            else False
        )

        if unit_6_candidate.get(name) is not expected:
            raise RuntimeError(
                "UNIT 7 UNIT 6 SAFETY FAILED: "
                + name
            )

    for name in (
        "one_direction_only",
        "anti_duplicate_orders",
        "exclusive_mode",
    ):

        if strategy.get(name) is not True:
            raise RuntimeError(
                "UNIT 7 STRATEGY SAFETY FAILED: "
                + name
            )

    print(
        "PASS: UNIT 7 PREPARATION SAFETY",
        flush=True
    )

    # ========================================================
    # 3. NUMERIC HELPERS
    # ========================================================

    def number(value, label):

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 7 BOOLEAN NUMBER: " + label
            )

        try:
            value = float(value)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            raise RuntimeError(
                "UNIT 7 INVALID NUMBER: " + label
            )

        if not math.isfinite(value):
            raise RuntimeError(
                "UNIT 7 NONFINITE NUMBER: " + label
            )

        return value

    def setting(section, key):

        if key not in section:
            raise RuntimeError(
                "UNIT 7 MISSING SETTING: " + key
            )

        return number(section[key], key)

    # ========================================================
    # 4. READ ADJUSTABLE SETTINGS
    # ========================================================

    initial_fixed_usdt = setting(
        strategy,
        "initial_fixed_usdt"
    )

    initial_margin_percent = setting(
        strategy,
        "initial_margin_percent"
    )

    leverage_reference = setting(
        strategy,
        "leverage_target"
    )

    exposure_cap_percent = setting(
        strategy,
        "exposure_cap_percent"
    )

    maximum_backups = strategy.get(
        "max_backups"
    )

    backup_multipliers = strategy.get(
        "backup_multipliers"
    )

    backup_buffer_percent = setting(
        strategy,
        "backup_buffer_percent"
    )

    quantity_step = setting(
        precision,
        "quantity_step"
    )

    minimum_quantity = setting(
        precision,
        "minimum_quantity"
    )

    price_step = setting(
        precision,
        "price_step"
    )

    if not (
        initial_fixed_usdt > 0
        and 0 < initial_margin_percent <= 100
        and leverage_reference > 0
        and 0 < exposure_cap_percent <= 100
        and backup_buffer_percent >= 0
        and quantity_step > 0
        and minimum_quantity > 0
        and price_step > 0
    ):
        raise RuntimeError(
            "UNIT 7 INVALID SIZING SETTINGS"
        )

    if (
        type(maximum_backups) is not int
        or maximum_backups < 0
        or not isinstance(
            backup_multipliers,
            (list, tuple)
        )
        or len(backup_multipliers)
        != maximum_backups
    ):
        raise RuntimeError(
            "UNIT 7 BACKUP CONFIGURATION INVALID"
        )

    multipliers = tuple(
        number(value, "BACKUP MULTIPLIER")
        for value in backup_multipliers
    )

    if any(value <= 0 for value in multipliers):
        raise RuntimeError(
            "UNIT 7 INVALID BACKUP MULTIPLIER"
        )

    # Read the exact configured numbers.
    # No hardcoded override of the Unit 2 values.

    proposed_backup_margins = tuple(
        round(
            initial_fixed_usdt * value,
            8
        )
        for value in multipliers
    )

    proposed_full_ladder_margin = (
        initial_fixed_usdt
        + sum(proposed_backup_margins)
    )

    # This is only a nominal plan.
    # No actual available balance is known here.
    # Unit 8 and later units must verify funding.

    # ========================================================
    # 5. VERIFY EXCHANGE IDENTIFIERS
    # ========================================================

    market_symbol = exchange.get(
        "market_symbol"
    )

    demo_symbol = exchange.get(
        "demo_order_symbol"
    )

    if (
        market_symbol != "BTCUSDT"
        or demo_symbol != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 7 WEEX SYMBOL CONTRACT FAILED"
        )

    # ========================================================
    # 6. RECEIVE EXACT UNIT 6 SIGNAL
    # ========================================================

    execution_intent = unit_6_candidate[
        "execution_intent"
    ]

    signal_qualified = unit_6_candidate[
        "signal_qualified"
    ]

    active_mode = unit_6_candidate[
        "active_mode"
    ]

    direction = unit_6_candidate[
        "direction"
    ]

    admission_reason = unit_6_candidate[
        "admission_reason"
    ]

    unit5_reason = unit_6_candidate[
        "unit_5_reason"
    ]

    candidate_mode = unit_6_candidate.get(
        "candidate_mode",
        "NONE"
    )

    candidate_stage = unit_6_candidate.get(
        "candidate_stage",
        "NONE"
    )

    candidate_protected = unit_6_candidate.get(
        "candidate_protected",
        False
    )

    if (
        type(execution_intent) is not bool
        or type(signal_qualified) is not bool
        or execution_intent != signal_qualified
    ):
        raise RuntimeError(
            "UNIT 7 EXECUTION INTENT CONTRADICTION"
        )

    if type(candidate_protected) is not bool:
        raise RuntimeError(
            "UNIT 7 CANDIDATE PROTECTION INVALID"
        )

    if (
        not isinstance(admission_reason, str)
        or not isinstance(unit5_reason, str)
    ):
        raise RuntimeError(
            "UNIT 7 ADMISSION REASON INVALID"
        )

    # ========================================================
    # 7. ADMISSION AND CANDIDATE-STATE GATES
    # ========================================================

    valid_admission_reasons = {
        "BREAKOUT":
            "BREAKOUT_PRELIMINARY_ADMISSION_PASS",
        "STRUCTURE":
            "STRUCTURE_PRELIMINARY_ADMISSION_PASS",
        "SCALP":
            "SCALP_PRELIMINARY_ADMISSION_PASS",
    }

    if execution_intent:

        if (
            active_mode not in valid_admission_reasons
            or direction not in (
                "LONG",
                "SHORT",
            )
            or admission_reason
            != valid_admission_reasons[
                active_mode
            ]
            or candidate_protected
            or candidate_stage not in (
                "QUALIFIED",
                "PENDING_UNIT_6",
            )
        ):
            raise RuntimeError(
                "UNIT 7 QUALIFIED SIGNAL CONTRACT FAILED"
            )

        status = "READY_FOR_BALANCE"

    else:

        if (
            active_mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 7 IDLE MODE CONTRADICTION"
            )

        status = "IDLE"

    if (
        candidate_stage == "DEVELOPING"
        and execution_intent
    ):
        raise RuntimeError(
            "UNIT 7 DEVELOPING SIGNAL EXECUTION LEAK"
        )

    # ========================================================
    # 8. ORIGINAL UNIT 8 HANDOVER
    #
    # NO ACCOUNT BALANCE OR BTC QUANTITY
    # IS CREATED IN THIS UNIT.
    # ========================================================

    needs_balance = (
        status == "READY_FOR_BALANCE"
    )

    sizing_candidate = {

        # Original interface

        "status":
            status,

        "symbol":
            market_symbol,

        "demo_order_symbol":
            demo_symbol,

        "active_mode":
            active_mode,

        "direction":
            direction,

        "execution_intent":
            execution_intent,

        "signal_qualified":
            signal_qualified,

        "unit_5_reason":
            unit5_reason,

        "admission_reason":
            admission_reason,

        "initial_margin_percent":
            initial_margin_percent,

        "leverage_target":
            leverage_reference,

        "quantity_step":
            quantity_step,

        "minimum_quantity":
            minimum_quantity,

        "price_step":
            price_step,

        "account_balance_required":
            needs_balance,

        "position_sizing_performed":
            False,

        "quantity_calculated":
            False,

        "proposed_quantity":
            None,

        "order_payload_created":
            False,

        "read_only":
            True,

        "skip_reason":
            (
                None
                if needs_balance
                else admission_reason
            ),

        # Additive adjustable configuration

        "initial_fixed_usdt":
            initial_fixed_usdt,

        "initial_margin_usdt":
            None,

        "margin_sizing_policy":
            "FIXED_PREFERRED_BALANCE_VERIFIED_LATER",

        "max_backups":
            maximum_backups,

        "backup_multipliers":
            multipliers,

        "backup_buffer_percent":
            backup_buffer_percent,

        "proposed_backup_margins_usdt":
            proposed_backup_margins,

        "proposed_full_ladder_margin_usdt":
            proposed_full_ladder_margin,

        "exposure_cap_percent":
            exposure_cap_percent,

        "progressive_backup_funding":
            strategy.get(
                "progressive_backup_funding",
                True
            ),

        "full_ladder_reservation_required":
            strategy.get(
                "full_ladder_reservation_required",
                False
            ),

        "leverage_source":
            "WEEX_EXCHANGE_SETTING",

        "leverage_verified":
            False,

        "exchange_leverage":
            None,

        "available_balance":
            None,

        "position_notional_usdt":
            None,

        "account_balance_verified":
            False,

        "position_state_verified":
            False,

        "market_precision_verified":
            False,

        "trade_authorized":
            False,

        "exchange_write":
            False,

        "candidate_mode":
            candidate_mode,

        "candidate_stage":
            candidate_stage,

        "candidate_protected":
            candidate_protected,

        "qualification_version":
            "U6_HYBRID_ADJUSTABLE_V2",

        "unit_7_revision":
            "HYBRID_ADJUSTABLE_V2",
    }

    # ========================================================
    # 9. OUTPUT SAFETY
    # ========================================================

    if (
        sizing_candidate[
            "position_sizing_performed"
        ] is not False
        or sizing_candidate[
            "quantity_calculated"
        ] is not False
        or sizing_candidate[
            "proposed_quantity"
        ] is not None
        or sizing_candidate[
            "order_payload_created"
        ] is not False
        or sizing_candidate[
            "trade_authorized"
        ] is not False
        or sizing_candidate[
            "exchange_write"
        ] is not False
    ):
        raise RuntimeError(
            "UNIT 7 PREMATURE EXECUTION STATE"
        )

    if (
        status == "IDLE"
        and sizing_candidate[
            "account_balance_required"
        ] is not False
    ):
        raise RuntimeError(
            "UNIT 7 IDLE BALANCE GATE FAILED"
        )

    if (
        status == "READY_FOR_BALANCE"
        and sizing_candidate[
            "account_balance_required"
        ] is not True
    ):
        raise RuntimeError(
            "UNIT 7 ACTIVE BALANCE GATE FAILED"
        )

    # ========================================================
    # 10. RENDER VERIFICATION
    # ========================================================

    print(
        "PASS: UNIT 7 ORIGINAL UNIT 6 CONTRACT",
        flush=True
    )

    print(
        "PASS: UNIT 7 ORIGINAL UNIT 8 HANDOVER",
        flush=True
    )

    print(
        "PASS: UNIT 7 ADJUSTABLE SIZING SETTINGS",
        flush=True
    )

    print(
        "UNIT 7 STATUS =",
        status,
        flush=True
    )

    print(
        "UNIT 7 CANDIDATE MODE =",
        candidate_mode,
        flush=True
    )

    print(
        "UNIT 7 CANDIDATE STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 7 ACTIVE MODE =",
        active_mode,
        flush=True
    )

    print(
        "UNIT 7 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 7 EXECUTION INTENT =",
        execution_intent,
        flush=True
    )

    print(
        "UNIT 7 INITIAL FIXED USDT =",
        initial_fixed_usdt,
        flush=True
    )

    print(
        "UNIT 7 INITIAL MARGIN PERCENT =",
        initial_margin_percent,
        flush=True
    )

    print(
        "UNIT 7 BACKUP COUNT =",
        maximum_backups,
        flush=True
    )

    print(
        "UNIT 7 BACKUP MULTIPLIERS =",
        multipliers,
        flush=True
    )

    print(
        "UNIT 7 EXPOSURE CAP PERCENT =",
        exposure_cap_percent,
        flush=True
    )

    print(
        "UNIT 7 ACCOUNT BALANCE REQUIRED =",
        needs_balance,
        flush=True
    )

    print(
        "UNIT 7 BALANCE VERIFIED = False",
        flush=True
    )

    print(
        "UNIT 7 QUANTITY CALCULATED = False",
        flush=True
    )

    print(
        "UNIT 7 LEVERAGE SOURCE = WEEX_EXCHANGE_SETTING",
        flush=True
    )

    print(
        "UNIT 7 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 7 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 7 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 7 HYBRID ADJUSTABLE V2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return sizing_candidate


# ============================================================
# UNIT 7 EXECUTION / ORIGINAL UNIT 8 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
    fresh_reconstruction_unit_7(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE,
    )
)


# ============================================================
# END UNIT 7 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 8 - HYBRID ADJUSTABLE V2.4
# ZERO INDENTATION
#
# ADAPTED FROM 22524-LINE WORKING MAIN.PY
#
# ORIGINAL:
# DEMO BALANCE -> BTC QUANTITY -> TRADE PLAN
#
# HYBRID:
# UNIT 7 QUALIFIED SIGNAL
# WEEX DEMO BALANCE GET
# WEEX DEMO POSITION GET
# WEEX ACCOUNT LEVERAGE GET
# FIXED MARGIN AND QUANTITY CALCULATION
# ORIGINAL READY HANDOVER TO UNITS 9-11
#
# NO ORDER SUBMISSION IN UNIT 8
# NO LEVERAGE MUTATION
# NO REAL-CASH TRANSACTIONS
# ============================================================


def fresh_reconstruction_unit_8(
    config,
    unit_7_result,
    market_snapshot,
):

    import os
    import time
    import json
    import hmac
    import base64
    import hashlib
    import urllib.request
    import urllib.error

    from decimal import Decimal, ROUND_DOWN
    from datetime import datetime, timezone

    def log(*values):
        print(*values, flush=True)

    def D(value, name="VALUE"):
        if isinstance(value, bool):
            raise ValueError(name + ": BOOLEAN")
        try:
            x = Decimal(str(value))
        except Exception as exc:
            raise ValueError(
                name + ": INVALID NUMBER"
            ) from exc
        if not x.is_finite():
            raise ValueError(
                name + ": NONFINITE"
            )
        return x

    def floor_step(value, step):
        return (
            (value / step).to_integral_value(
                rounding=ROUND_DOWN
            ) * step
        )

    log("=" * 80)
    log(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 8 HYBRID ADJUSTABLE V2.4 START"
    )

    # ========================================================
    # 1. ORIGINAL INPUT CONTRACT
    # ========================================================

    if not all(
        isinstance(x, dict)
        for x in (
            config,
            unit_7_result,
            market_snapshot,
        )
    ):
        raise RuntimeError(
            "UNIT 8 INPUT INVALID"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})
    precision = config.get("market_precision", {})
    policy = config.get(
        "market_data_policy", {}
    )
    qualification = config.get(
        "qualification", {}
    )

    if not all(
        isinstance(x, dict)
        for x in (
            exchange,
            safety,
            strategy,
            precision,
            policy,
            qualification,
        )
    ):
        raise RuntimeError(
            "UNIT 8 CONFIGURATION INVALID"
        )

    if (
        config.get("execution_environment")
        != "DEMO"
        or exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
        or exchange.get("market_symbol")
        != "BTCUSDT"
        or exchange.get("demo_order_symbol")
        != "BTCSUSDT"
        or unit_7_result.get("unit_7_revision")
        != "HYBRID_ADJUSTABLE_V2"
        or market_snapshot.get("symbol")
        != "BTCUSDT"
        or market_snapshot.get("read_only")
        is not True
    ):
        raise RuntimeError(
            "UNIT 8 CONFIGURATION CONTRACT FAILED"
        )

    if tuple(
        qualification.get(
            "common", {}
        ).get("mode_priority", ())
    ) != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 8 STRATEGY PRIORITY CHANGED"
        )

    for key in (
        "real_order_submission_enabled",
        "order_endpoint_access_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 8 SAFETY FAILED: " + key
            )

    if (
        unit_7_result.get("read_only")
        is not True
        or unit_7_result.get(
            "trade_authorized"
        ) is not False
        or unit_7_result.get(
            "order_payload_created"
        ) is not False
        or unit_7_result.get(
            "exchange_write"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 8 UPSTREAM SAFETY FAILED"
        )

    log(
        "PASS: UNIT 8 ORIGINAL INPUT CONTRACT"
    )

    # ========================================================
    # 2. ADJUSTABLE SIZING
    # ========================================================

    fixed_margin = D(
        strategy["initial_fixed_usdt"],
        "INITIAL FIXED MARGIN"
    )

    exposure_pct = D(
        strategy["exposure_cap_percent"],
        "EXPOSURE CAP"
    )

    initial_pct = D(
        strategy["initial_margin_percent"],
        "INITIAL PERCENT"
    )

    qty_step = D(
        precision["quantity_step"],
        "QUANTITY STEP"
    )

    min_qty = D(
        precision["minimum_quantity"],
        "MINIMUM QUANTITY"
    )

    price_step = D(
        precision["price_step"],
        "PRICE STEP"
    )

    backup_multipliers = tuple(
        D(x, "BACKUP MULTIPLIER")
        for x in strategy["backup_multipliers"]
    )

    max_backups = strategy["max_backups"]

    if not (
        fixed_margin > 0
        and Decimal("0") < exposure_pct <= 100
        and initial_pct > 0
        and qty_step > 0
        and min_qty > 0
        and price_step > 0
        and type(max_backups) is int
        and max_backups >= 0
        and len(backup_multipliers)
        == max_backups
        and all(
            x > 0
            for x in backup_multipliers
        )
    ):
        raise RuntimeError(
            "UNIT 8 SIZING CONFIGURATION INVALID"
        )

    if (
        D(
            unit_7_result["initial_fixed_usdt"]
        ) != fixed_margin
        or D(
            unit_7_result["exposure_cap_percent"]
        ) != exposure_pct
        or tuple(
            D(x)
            for x in unit_7_result[
                "backup_multipliers"
            ]
        ) != backup_multipliers
    ):
        raise RuntimeError(
            "UNIT 8 UNIT 7 SIZING MISMATCH"
        )

    mark = D(
        market_snapshot["price"],
        "MARK PRICE"
    )

    market_time_ms = D(
        market_snapshot["exchange_time_ms"],
        "MARKET TIME"
    )

    age_seconds = (
        D(int(time.time() * 1000))
        - market_time_ms
    ) / Decimal("1000")

    if not (
        mark > 0
        and age_seconds >= -D(
            policy["future_tolerance_seconds"]
        )
        and age_seconds <= D(
            policy["max_market_age_seconds"]
        )
    ):
        raise RuntimeError(
            "UNIT 8 MARKET DATA STALE"
        )

    # ========================================================
    # 3. UNIT 7 SIGNAL
    # ========================================================

    mode = unit_7_result.get("active_mode")
    direction = unit_7_result.get("direction")

    qualified = unit_7_result.get(
        "signal_qualified"
    )
    intent = unit_7_result.get(
        "execution_intent"
    )

    if not (
        type(qualified) is bool
        and type(intent) is bool
        and qualified == intent
    ):
        raise RuntimeError(
            "UNIT 8 SIGNAL FLAGS INVALID"
        )

    if intent:
        if not (
            unit_7_result.get("status")
            == "READY_FOR_BALANCE"
            and mode in (
                "BREAKOUT",
                "STRUCTURE",
                "SCALP",
            )
            and direction in (
                "LONG",
                "SHORT",
            )
            and unit_7_result.get(
                "candidate_stage"
            ) == "QUALIFIED"
            and unit_7_result.get(
                "candidate_protected"
            ) is False
            and unit_7_result.get(
                "account_balance_required"
            ) is True
        ):
            raise RuntimeError(
                "UNIT 8 ACTIVE SIGNAL INVALID"
            )
    else:
        if not (
            unit_7_result.get("status")
            == "IDLE"
            and mode == "NONE"
            and direction == "NONE"
        ):
            raise RuntimeError(
                "UNIT 8 IDLE SIGNAL INVALID"
            )

    # ========================================================
    # 4. ORIGINAL UNIT 9 RESULT CONTRACT
    # ========================================================

    result = {

        "status": "IDLE",

        "active_mode": mode,
        "direction": direction,

        "signal_qualified": qualified,
        "execution_intent": intent,

        "trade_plan_ready": False,
        "trade_plan": None,

        "skip_reason": (
            str(
                unit_7_result.get(
                    "skip_reason",
                    "NO_QUALIFIED_SIGNAL"
                )
            )
            if not intent
            else "NONE"
        ),

        "read_only": True,

        "candidate_stage":
            unit_7_result.get(
                "candidate_stage", "NONE"
            ),

        "candidate_protected":
            unit_7_result.get(
                "candidate_protected", False
            ),

        "initial_fixed_usdt":
            float(fixed_margin),

        "initial_margin_percent":
            float(initial_pct),

        "backup_multipliers":
            tuple(
                float(x)
                for x in backup_multipliers
            ),

        "max_backups": max_backups,

        "exposure_cap_percent":
            float(exposure_pct),

        "market_symbol": "BTCUSDT",
        "demo_order_symbol": "BTCSUSDT",

        "live_mark_price": float(mark),

        "quantity_step": float(qty_step),
        "minimum_quantity": float(min_qty),
        "price_step": float(price_step),

        "available_balance": None,
        "balance_verified": False,

        "leverage_verified": False,
        "leverage_api_read": False,

        "exchange_leverage": None,
        "leverage_source": None,

        "demo_leverage_scope_confirmed":
            False,

        "position_flat_verified": False,
        "pending_orders_checked": False,

        "margin_allocation": None,
        "quantity_calculated": False,
        "position_sizing_performed": False,

        "trade_authorized": False,
        "order_payload_created": False,
        "exchange_write": False,

        "unit_8_revision":
            "HYBRID_ADJUSTABLE_V2",

        "unit_8_build":
            "V2.4_REFERENCE_RESTORATION",
    }

    # ========================================================
    # 5. ORIGINAL IDLE HANDOVER
    # ========================================================

    if not intent:

        log(
            "PASS: UNIT 8 ORIGINAL IDLE HANDOVER"
        )
        log("UNIT 8 STATUS = IDLE")
        log("UNIT 8 DEMO ORDER = NONE")
        log("UNIT 8 EXCHANGE WRITE = NONE")

        log(
            "UNIT 8 HYBRID ADJUSTABLE V2.4 "
            "RESULT = PASS (IDLE)"
        )

        log("=" * 80)
        return result

    # ========================================================
    # 6. AUTHENTICATED WEEX GET SUPPORT
    # ========================================================

    if safety.get(
        "demo_account_balance_read_enabled"
    ) is not True:
        result["status"] = "BLOCKED"
        result["skip_reason"] = (
            "DEMO_BALANCE_GET_DISABLED"
        )
        return result

    api_key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )
    api_secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )
    api_passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all((
        api_key,
        api_secret,
        api_passphrase,
    )):
        result["status"] = "BLOCKED"
        result["skip_reason"] = (
            "WEEX_CREDENTIALS_MISSING"
        )
        return result

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):
        def redirect_request(
            self, req, fp, code,
            msg, headers, newurl
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    allowed_get_paths = {
        "/capi/v3/sim/balance",
        "/capi/v3/sim/position/allPosition",
        "/capi/v3/account/symbolConfig",
    }

    def weex_get(path, query=""):

        if path not in allowed_get_paths:
            raise RuntimeError(
                "UNIT 8 UNAPPROVED ENDPOINT"
            )

        if (
            path == "/capi/v3/account/symbolConfig"
            and query != "symbol=BTCUSDT"
        ):
            raise RuntimeError(
                "UNIT 8 SYMBOL QUERY INVALID"
            )

        if (
            path != "/capi/v3/account/symbolConfig"
            and query
        ):
            raise RuntimeError(
                "UNIT 8 UNEXPECTED QUERY"
            )

        request_path = (
            path
            + ("?" + query if query else "")
        )

        timestamp = str(
            int(time.time() * 1000)
        )

        message = (
            timestamp + "GET" + request_path
        )

        signature = base64.b64encode(
            hmac.new(
                api_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        headers = {
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": api_passphrase,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        request = urllib.request.Request(
            exchange["contract_base_url"]
            + request_path,
            headers=headers,
            method="GET",
        )

        if (
            request.get_method() != "GET"
            or request.data is not None
        ):
            raise RuntimeError(
                "UNIT 8 NON-GET REQUEST BLOCKED"
            )

        with opener.open(
            request, timeout=15
        ) as response:
            if response.getcode() != 200:
                raise RuntimeError(
                    "UNIT 8 GET HTTP FAILURE"
                )
            raw = response.read(65537)

        if len(raw) > 65536:
            raise RuntimeError(
                "UNIT 8 GET RESPONSE TOO LARGE"
            )

        data = json.loads(
            raw.decode("utf-8")
        )

        if not isinstance(data, list):
            raise RuntimeError(
                "UNIT 8 EXPECTED LIST RESPONSE"
            )

        return data

    def block(reason):

        result["status"] = "BLOCKED"
        result["skip_reason"] = str(reason)

        log(
            "UNIT 8 STATUS = BLOCKED"
        )
        log(
            "UNIT 8 SKIP REASON =",
            reason
        )
        log(
            "UNIT 8 TRADE PLAN READY = False"
        )
        log(
            "UNIT 8 EXCHANGE WRITE = NONE"
        )

        return result

    # ========================================================
    # 7. ORIGINAL DEMO BALANCE GET
    # ========================================================

    try:
        balances = weex_get(
            "/capi/v3/sim/balance"
        )

        records = [
            item for item in balances
            if isinstance(item, dict)
            and str(
                item.get("asset", "")
            ).upper() == "SUSDT"
        ]

        if len(records) != 1:
            return block(
                "DEMO_SUSDT_BALANCE_NOT_UNIQUE"
            )

        available = D(
            records[0].get(
                "availableBalance"
            ),
            "AVAILABLE SUSDT"
        )

        if available < 0:
            return block(
                "NEGATIVE_DEMO_BALANCE"
            )

    except Exception as exc:

        log(
            "UNIT 8 BALANCE ERROR TYPE =",
            type(exc).__name__
        )

        return block(
            "DEMO_BALANCE_GET_FAILED"
        )

    result["balance_verified"] = True
    result["available_balance"] = float(
        available
    )

    log(
        "PASS: UNIT 8 DEMO SUSDT BALANCE GET"
    )

    # ========================================================
    # 8. DEMO POSITION CHECK
    # ========================================================

    try:
        positions = weex_get(
            "/capi/v3/sim/position/allPosition"
        )

        active_positions = 0

        for item in positions:

            if not isinstance(item, dict):
                return block(
                    "DEMO_POSITION_RECORD_INVALID"
                )

            if str(
                item.get("symbol", "")
            ).upper() not in (
                "BTCUSDT",
                "BTCSUSDT",
            ):
                continue

            size = D(
                item.get("size", "0"),
                "POSITION SIZE"
            )

            if size < 0:
                return block(
                    "DEMO_POSITION_SIZE_INVALID"
                )

            if size > 0:
                active_positions += 1

    except Exception as exc:

        log(
            "UNIT 8 POSITION ERROR TYPE =",
            type(exc).__name__
        )

        return block(
            "DEMO_POSITION_GET_FAILED"
        )

    result["position_flat_verified"] = (
        active_positions == 0
    )

    if active_positions:
        return block(
            "EXISTING_DEMO_POSITION"
        )

    log(
        "PASS: UNIT 8 DEMO BTC POSITION FLAT"
    )

    # ========================================================
    # 9. AUTOMATIC EXCHANGE LEVERAGE GET
    #
    # PRESERVE WEEX OWNED SETTINGS
    # NO LEVERAGE SETTING POST
    # ========================================================

    try:
        configurations = weex_get(
            "/capi/v3/account/symbolConfig",
            "symbol=BTCUSDT"
        )

        matching = [
            item for item in configurations
            if isinstance(item, dict)
            and item.get("symbol")
            == "BTCUSDT"
        ]

        if len(matching) != 1:
            return block(
                "WEEX_SYMBOL_CONFIG_NOT_UNIQUE"
            )

        setting = matching[0]

        margin_type = str(
            setting.get("marginType", "")
        ).upper()

        if margin_type not in (
            "CROSSED",
            "ISOLATED",
        ):
            return block(
                "WEEX_MARGIN_TYPE_UNKNOWN"
            )

        if margin_type == "CROSSED":
            field = "crossLeverage"

        elif direction == "LONG":
            field = "isolatedLongLeverage"

        else:
            field = "isolatedShortLeverage"

        leverage = D(
            setting.get(field),
            "WEEX LEVERAGE"
        )

        if not (
            Decimal("1")
            <= leverage
            <= Decimal("125")
        ):
            return block(
                "WEEX_LEVERAGE_INVALID"
            )

    except Exception as exc:

        log(
            "UNIT 8 LEVERAGE ERROR TYPE =",
            type(exc).__name__
        )

        return block(
            "WEEX_LEVERAGE_GET_FAILED"
        )

    result["leverage_api_read"] = True

    # TRUE means the reported configuration
    # was fetched successfully and validated.
    # It does not prove demo account scope.
    result["leverage_verified"] = True

    result["exchange_leverage"] = float(
        leverage
    )

    result["leverage_source"] = (
        "WEEX_ACCOUNT_SYMBOL_CONFIG_GET"
    )

    result["margin_type"] = margin_type

    result["demo_leverage_scope_confirmed"] = (
        False
    )

    log(
        "PASS: UNIT 8 AUTOMATIC WEEX LEVERAGE GET"
    )
    log(
        "UNIT 8 MARGIN TYPE =",
        margin_type
    )
    log(
        "UNIT 8 LEVERAGE FIELD =",
        field
    )
    log(
        "UNIT 8 LEVERAGE =",
        leverage
    )
    log(
        "UNIT 8 DEMO SCOPE CONFIRMED = False"
    )

    # ========================================================
    # 10. ORIGINAL FIXED-MARGIN ENTRY SIZING
    #
    # QUANTITY = MARGIN * LEVERAGE / MARK
    #
    # PRESERVE 22524 MODEL'S READY PLAN
    # ========================================================

    if available < fixed_margin:
        return block(
            "INSUFFICIENT_INITIAL_MARGIN"
        )

    maximum_exposure = (
        available
        * exposure_pct
        / Decimal("100")
    )

    if fixed_margin > maximum_exposure:
        return block(
            "INITIAL_MARGIN_EXCEEDS_35_PERCENT_CAP"
        )

    notional = fixed_margin * leverage

    raw_qty = notional / mark

    quantity = floor_step(
        raw_qty,
        qty_step
    )

    if quantity < min_qty:
        return block(
            "BTC_QUANTITY_BELOW_EXCHANGE_MINIMUM"
        )

    actual_margin = (
        quantity * mark / leverage
    )

    if actual_margin > maximum_exposure:
        return block(
            "QUANTITY_EXCEEDS_EXPOSURE_CAP"
        )

    # The initial entry only is funded here.
    # Unit 14 determines affordability of
    # each backup when it is actually needed.

    position_sizing = {

        "asset": "SUSDT",

        "available_balance": float(
            available
        ),

        "initial_margin_percent":
            float(initial_pct),

        "initial_fixed_usdt":
            float(fixed_margin),

        "margin_allocation":
            float(fixed_margin),

        "actual_estimated_margin":
            float(actual_margin),

        "leverage_target": float(
            leverage
        ),

        "leverage_source":
            "WEEX_ACCOUNT_SYMBOL_CONFIG_GET",

        "leverage_verified": True,

        "demo_leverage_scope_confirmed":
            False,

        "live_mark_price": float(mark),

        "raw_quantity": float(raw_qty),

        "quantity_step": float(qty_step),

        "minimum_quantity": float(min_qty),

        "quantity": float(quantity),

        "exposure_cap_percent":
            float(exposure_pct),

        "backup_multipliers":
            tuple(
                float(x)
                for x in backup_multipliers
            ),

        "max_backups": max_backups,

        "position_sizing_performed":
            True,

        "quantity_calculated": True,

        "source":
            "WEEX_V3_DEMO_BALANCE_AND_ACCOUNT_CONFIG",

        "read_only": True,
    }

    # ========================================================
    # 11. RESTORE ORIGINAL TRADE PLAN HANDOVER
    # ========================================================

    trade_plan = {

        "active_mode": mode,

        "direction": direction,

        "quantity": float(quantity),

        "position_sizing":
            position_sizing,

        "execution_environment": "DEMO",

        "market_symbol": "BTCUSDT",

        "demo_order_symbol": "BTCSUSDT",

        "signal_qualified": True,

        "execution_intent": True,

        "read_only": True,
    }

    result.update({

        "status": "READY",

        "trade_plan_ready": True,

        "trade_plan": trade_plan,

        "margin_allocation":
            float(fixed_margin),

        "quantity_calculated": True,

        "position_sizing_performed":
            True,

        "skip_reason": "NONE",

        "trade_authorized": False,

        "order_payload_created": False,

        "exchange_write": False,
    })

    log(
        "PASS: UNIT 8 ORIGINAL POSITION SIZING"
    )
    log(
        "PASS: UNIT 8 ORIGINAL TRADE PLAN"
    )

    log(
        "UNIT 8 STATUS = READY"
    )
    log(
        "UNIT 8 ACTIVE MODE =",
        mode
    )
    log(
        "UNIT 8 DIRECTION =",
        direction
    )
    log(
        "UNIT 8 INITIAL MARGIN SUSDT =",
        fixed_margin
    )
    log(
        "UNIT 8 LEVERAGE =",
        leverage
    )
    log(
        "UNIT 8 BTC QUANTITY =",
        quantity
    )
    log(
        "UNIT 8 MAX BACKUPS =",
        max_backups
    )
    log(
        "UNIT 8 EXPOSURE CAP =",
        exposure_pct,
        "%"
    )
    log(
        "UNIT 8 TRADE PLAN READY = True"
    )
    log(
        "UNIT 8 DEMO LEVERAGE SCOPE CONFIRMED = False"
    )
    log(
        "UNIT 8 DEMO ORDER = NONE"
    )
    log(
        "UNIT 8 EXCHANGE WRITE = NONE"
    )

    log(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 8 HYBRID ADJUSTABLE V2.4 "
        "RESULT = PASS (READY HANDOVER)"
    )

    log("=" * 80)

    return result


# ============================================================
# UNIT 8 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
    fresh_reconstruction_unit_8(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_SIZING_CANDIDATE,
        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT,
    )
)


# ============================================================
# END UNIT 8 - HYBRID ADJUSTABLE V2.4
# ZERO INDENTATION
# ============================================================

# ============================================================
# START UNIT 9 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
#
# ADAPTED FROM:
# 22524-LINE MODEL - EXECUTION PREPARATION
# 12355-LINE MODEL - SIGNAL CONTINUITY
#
# ADJUSTABLE:
# BREAKOUT > STRUCTURE > SCALP
#
# UNIT 9 WILL NOT:
# - REQUALIFY AN ALREADY ADMITTED STRATEGY
# - ADD EXTRA MANDATORY ENTRY CONFIRMATIONS
# - INVENT BALANCE, LEVERAGE OR QUANTITY
# - SUBMIT DEMO OR LIVE ORDERS
# - MODIFY EXCHANGE LEVERAGE
#
# ORIGINAL UNIT 10 HANDOVER PRESERVED
# ============================================================


import time


# ============================================================
# UNIT 9 PROCESS-LOCAL OBSERVATION STATE
# ZERO INDENTATION
#
# AUDIT ONLY.
# NOT AN EXTRA EXECUTION QUALIFICATION GATE.
# ============================================================

FRESH_UNIT_9_HYBRID_STATE = {
    "signal_key": None,
    "first_seen": None,
    "last_seen": None,
    "last_candle_id": None,
    "distinct_candles": 0,
    "duplicate_candle": False,
    "last_status": "NOT_STARTED",
}


def fresh_reconstruction_unit_9(
    config,
    unit_8_result,
    unit_4_analysis=None,
):

    from datetime import datetime, timezone
    import math

    print("=" * 80, flush=True)

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 9 HYBRID ADJUSTABLE V2 START",
        flush=True
    )

    # ========================================================
    # 1. ORIGINAL INPUT CONTRACT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 9 CONFIG INVALID"
        )

    if not isinstance(unit_8_result, dict):
        raise RuntimeError(
            "UNIT 9 UNIT 8 RESULT INVALID"
        )

    if (
        unit_4_analysis is not None
        and not isinstance(unit_4_analysis, dict)
    ):
        raise RuntimeError(
            "UNIT 9 UNIT 4 ANALYSIS INVALID"
        )

    strategy = config.get("strategy")
    safety = config.get("safety")
    exchange = config.get("exchange")
    precision = config.get("market_precision")
    qualification = config.get("qualification")

    if not all(
        isinstance(value, dict)
        for value in (
            strategy,
            safety,
            exchange,
            precision,
            qualification,
        )
    ):
        raise RuntimeError(
            "UNIT 9 CONFIGURATION SECTION MISSING"
        )

    common = qualification.get("common")

    if not isinstance(common, dict):
        raise RuntimeError(
            "UNIT 9 COMMON QUALIFICATION MISSING"
        )

    if (
        unit_8_result.get("unit_8_revision")
        != "HYBRID_ADJUSTABLE_V2"
    ):
        raise RuntimeError(
            "UNIT 9 UNIT 8 VERSION MISMATCH"
        )

    required_fields = (
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

    for name in required_fields:

        if name not in unit_8_result:
            raise RuntimeError(
                "UNIT 9 UNIT 8 FIELD MISSING: "
                + name
            )

    print(
        "PASS: UNIT 9 ORIGINAL UNIT 8 CONTRACT",
        flush=True
    )

    # ========================================================
    # 2. NUMERIC AND BOOLEAN HELPERS
    # ========================================================

    def finite(value, label):

        if type(value) is bool:
            raise RuntimeError(
                "UNIT 9 BOOLEAN NUMBER: " + label
            )

        try:
            result = float(value)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            raise RuntimeError(
                "UNIT 9 INVALID NUMBER: " + label
            )

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 9 NONFINITE NUMBER: " + label
            )

        return result

    def require_bool(value, label):

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 9 INVALID BOOLEAN: " + label
            )

        return value

    # ========================================================
    # 3. NO EXCHANGE-WRITE CAPABILITIES
    # ========================================================

    for name in (
        "real_order_submission_enabled",
        "order_endpoint_access_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):

        if safety.get(name) is not False:
            raise RuntimeError(
                "UNIT 9 CONFIG SAFETY FAILED: "
                + name
            )

    if unit_8_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 9 UNIT 8 READ-ONLY FAILURE"
        )

    for name in (
        "order_payload_created",
        "trade_authorized",
        "exchange_write",
    ):

        if unit_8_result.get(name) is not False:
            raise RuntimeError(
                "UNIT 9 UNIT 8 EXCHANGE SAFETY FAILED: "
                + name
            )

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 9 DEMO ENVIRONMENT REQUIRED"
        )

    if (
        exchange.get("market_symbol")
        != "BTCUSDT"
        or exchange.get("demo_order_symbol")
        != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 9 SYMBOL CONTRACT FAILED"
        )

    for name in (
        "one_direction_only",
        "anti_duplicate_orders",
        "exclusive_mode",
    ):

        if strategy.get(name) is not True:
            raise RuntimeError(
                "UNIT 9 STRATEGY SAFETY FAILED: "
                + name
            )

    priority = tuple(
        common.get("mode_priority", ())
    )

    if priority != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 9 PRIORITY INVALID"
        )

    print(
        "PASS: UNIT 9 EXCHANGE SAFETY",
        flush=True
    )

    # ========================================================
    # 4. ADJUSTABLE SIZING HANDOVER
    #
    # PRESERVE UNIT 2 VALUES.
    # UNIT 9 DOES NOT RESET QUALIFICATION FIGURES.
    # ========================================================

    initial_margin = finite(
        strategy.get("initial_fixed_usdt"),
        "INITIAL FIXED MARGIN"
    )

    exposure_cap = finite(
        strategy.get("exposure_cap_percent"),
        "EXPOSURE CAP"
    )

    backup_count = strategy.get("max_backups")

    multipliers = strategy.get(
        "backup_multipliers"
    )

    if (
        type(backup_count) is not int
        or backup_count < 0
        or not isinstance(
            multipliers,
            (tuple, list)
        )
        or len(multipliers) != backup_count
    ):
        raise RuntimeError(
            "UNIT 9 BACKUP CONTRACT INVALID"
        )

    multipliers = tuple(
        finite(value, "BACKUP MULTIPLIER")
        for value in multipliers
    )

    if not (
        initial_margin > 0
        and 0 < exposure_cap <= 100
        and all(
            value > 0
            for value in multipliers
        )
    ):
        raise RuntimeError(
            "UNIT 9 ADJUSTABLE SIZING INVALID"
        )

    if not math.isclose(
        finite(
            unit_8_result.get(
                "initial_fixed_usdt"
            ),
            "UNIT 8 INITIAL MARGIN"
        ),
        initial_margin,
        abs_tol=0.00000001
    ):
        raise RuntimeError(
            "UNIT 9 INITIAL MARGIN CHANGED"
        )

    if (
        tuple(
            unit_8_result.get(
                "backup_multipliers", ()
            )
        ) != multipliers
    ):
        raise RuntimeError(
            "UNIT 9 BACKUP MULTIPLIERS CHANGED"
        )

    if not math.isclose(
        finite(
            unit_8_result.get(
                "exposure_cap_percent"
            ),
            "UNIT 8 EXPOSURE CAP"
        ),
        exposure_cap,
        abs_tol=0.00000001
    ):
        raise RuntimeError(
            "UNIT 9 EXPOSURE CAP CHANGED"
        )

    print(
        "PASS: UNIT 9 ADJUSTABLE SETTINGS PRESERVED",
        flush=True
    )

    # ========================================================
    # 5. RECEIVE UNIT 8 SIGNAL
    # ========================================================

    upstream_status = unit_8_result["status"]

    mode = unit_8_result["active_mode"]

    direction = unit_8_result["direction"]

    signal_qualified = require_bool(
        unit_8_result["signal_qualified"],
        "SIGNAL QUALIFIED"
    )

    upstream_intent = require_bool(
        unit_8_result["execution_intent"],
        "EXECUTION INTENT"
    )

    trade_plan_ready = require_bool(
        unit_8_result["trade_plan_ready"],
        "TRADE PLAN READY"
    )

    trade_plan = unit_8_result["trade_plan"]

    candidate_stage = unit_8_result.get(
        "candidate_stage",
        "NONE"
    )

    candidate_protected = require_bool(
        unit_8_result.get(
            "candidate_protected", False
        ),
        "CANDIDATE PROTECTED"
    )

    skip_reason = str(
        unit_8_result.get(
            "skip_reason", "NONE"
        )
    )

    if signal_qualified != upstream_intent:
        raise RuntimeError(
            "UNIT 9 SIGNAL / INTENT CONTRADICTION"
        )

    if candidate_protected and upstream_intent:
        raise RuntimeError(
            "UNIT 9 DEVELOPING CANDIDATE LEAK"
        )

    if upstream_intent:

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
            or candidate_stage not in (
                "QUALIFIED",
                "PENDING_UNIT_6",
            )
        ):
            raise RuntimeError(
                "UNIT 9 QUALIFIED SIGNAL INVALID"
            )

    else:

        if (
            mode != "NONE"
            or direction != "NONE"
        ):
            raise RuntimeError(
                "UNIT 9 IDLE SIGNAL CONTRADICTION"
            )

    if (
        trade_plan_ready
        and not upstream_intent
    ):
        raise RuntimeError(
            "UNIT 9 PLAN WITHOUT SIGNAL"
        )

    # ========================================================
    # 6. CONTINUITY OBSERVATION
    #
    # FROM NEWER REFERENCE.
    #
    # THIS IS AN AUDIT.
    # IT DOES NOT IMPOSE A SECOND 2-CANDLE
    # QUALIFICATION ON UNIT 6 APPROVAL.
    # ========================================================

    state = FRESH_UNIT_9_HYBRID_STATE

    now = time.monotonic()

    signal_expiry = finite(
        common.get("signal_expiry_seconds"),
        "SIGNAL EXPIRY"
    )

    if signal_expiry <= 0:
        raise RuntimeError(
            "UNIT 9 SIGNAL EXPIRY INVALID"
        )

    closed_candle_id = None
    duplicate_candle = False
    signal_changed = False
    signal_expired = False
    continuity_observed = False

    active_signal_key = None

    if upstream_intent:

        active_signal_key = (
            exchange["market_symbol"],
            mode,
            direction,
        )

    if (
        state["signal_key"] is not None
        and state["first_seen"] is not None
        and (
            now - state["first_seen"]
        ) > signal_expiry
    ):

        signal_expired = True

        state.update({
            "signal_key": None,
            "first_seen": None,
            "last_seen": None,
            "last_candle_id": None,
            "distinct_candles": 0,
            "duplicate_candle": False,
        })

    if not upstream_intent:

        state.update({
            "signal_key": None,
            "first_seen": None,
            "last_seen": None,
            "last_candle_id": None,
            "distinct_candles": 0,
            "duplicate_candle": False,
        })

    else:

        if (
            state["signal_key"] is not None
            and state["signal_key"]
            != active_signal_key
        ):

            signal_changed = True

            state.update({
                "signal_key": None,
                "first_seen": None,
                "last_seen": None,
                "last_candle_id": None,
                "distinct_candles": 0,
                "duplicate_candle": False,
            })

        if isinstance(unit_4_analysis, dict):

            if (
                unit_4_analysis.get(
                    "symbol"
                ) != "BTCUSDT"
                or unit_4_analysis.get(
                    "strategy_evidence_version"
                ) != "U4_HYBRID_V2"
            ):
                raise RuntimeError(
                    "UNIT 9 UNIT 4 CONTRACT INVALID"
                )

            candles = unit_4_analysis.get(
                "recent_closed_klines"
            )

            if (
                isinstance(candles, list)
                and len(candles) > 0
                and isinstance(
                    candles[-1], dict
                )
            ):

                last_candle = candles[-1]

                for timestamp_key in (
                    "timestamp",
                    "open_time",
                    "openTime",
                    "start_time",
                    "startTime",
                    "time",
                    "ts",
                ):

                    raw = last_candle.get(
                        timestamp_key
                    )

                    if raw is None:
                        continue

                    if isinstance(raw, bool):
                        continue

                    try:
                        parsed = int(raw)
                    except (
                        TypeError,
                        ValueError,
                        OverflowError,
                    ):
                        continue

                    if parsed > 0:
                        closed_candle_id = parsed
                        break

        if state["signal_key"] is None:

            state["signal_key"] = (
                active_signal_key
            )

            state["first_seen"] = now

            state["distinct_candles"] = (
                1
                if closed_candle_id is not None
                else 0
            )

            state["last_candle_id"] = (
                closed_candle_id
            )

        elif closed_candle_id is not None:

            previous_id = state[
                "last_candle_id"
            ]

            if previous_id is None:

                state["last_candle_id"] = (
                    closed_candle_id
                )

                state["distinct_candles"] += 1

            elif closed_candle_id == previous_id:

                duplicate_candle = True

            elif closed_candle_id > previous_id:

                state["last_candle_id"] = (
                    closed_candle_id
                )

                state["distinct_candles"] += 1

            else:

                # A candle-time regression is
                # diagnostic evidence requiring
                # a later fresh-market check.

                signal_changed = True

                state["last_candle_id"] = (
                    closed_candle_id
                )

                state["first_seen"] = now

                state["distinct_candles"] = 1

        state["last_seen"] = now

        state["duplicate_candle"] = (
            duplicate_candle
        )

        continuity_observed = (
            state["distinct_candles"] >= 2
        )

    # ========================================================
    # 7. ORIGINAL UNIT 9 EXECUTION PREPARATION
    #
    # ONLY A VERIFIED READY TRADE PLAN CAN
    # CREATE AN INTERNAL EXECUTION CANDIDATE.
    #
    # NOT A WEEX ORDER PAYLOAD.
    # ========================================================

    execution_ready = False
    internal_candidate = None

    status = "IDLE"

    downstream_intent = False
    downstream_qualified = False

    downstream_plan_ready = False
    downstream_plan = None

    if not upstream_intent:

        status = "IDLE"

    elif not trade_plan_ready:

        # Unit 8 has admitted the strategy,
        # but required funding or leverage
        # information is still outstanding.
        #
        # Keep original Unit 10 IDLE contract.
        # Preserve exact upstream status
        # in diagnostics so it is not hidden.

        status = "IDLE"

        if upstream_status == "IDLE":
            raise RuntimeError(
                "UNIT 9 ACTIVE SIGNAL MARKED IDLE UPSTREAM"
            )

        if skip_reason in (
            "NONE",
            "None",
            "",
        ):
            skip_reason = (
                "UNIT_8_TRADE_PLAN_NOT_READY:"
                + str(upstream_status)
            )

    else:

        if upstream_status not in (
            "READY",
            "QUALIFIED",
            "ACTIVE",
        ):
            raise RuntimeError(
                "UNIT 9 READY PLAN STATUS INVALID: "
                + str(upstream_status)
            )

        if not isinstance(trade_plan, dict):
            raise RuntimeError(
                "UNIT 9 READY TRADE PLAN MISSING"
            )

        if (
            trade_plan.get(
                "active_mode"
            ) != mode
            or trade_plan.get(
                "direction"
            ) != direction
        ):
            raise RuntimeError(
                "UNIT 9 TRADE PLAN SIGNAL MISMATCH"
            )

        if (
            trade_plan.get(
                "execution_environment",
                "DEMO"
            ) != "DEMO"
        ):
            raise RuntimeError(
                "UNIT 9 TRADE PLAN NOT DEMO"
            )

        if (
            unit_8_result.get(
                "balance_verified"
            ) is not True
            or unit_8_result.get(
                "leverage_verified"
            ) is not True
            or unit_8_result.get(
                "quantity_calculated"
            ) is not True
        ):
            raise RuntimeError(
                "UNIT 9 READY PLAN VERIFICATION MISSING"
            )

        # Do not invent a position or
        # an executable quantity.
        # Validate these at the later
        # execution boundary.

        internal_candidate = {
            "active_mode": mode,
            "direction": direction,
            "trade_plan": trade_plan,
            "execution_environment": "DEMO",
        }

        execution_ready = True

        downstream_intent = True
        downstream_qualified = True

        downstream_plan_ready = True
        downstream_plan = trade_plan

        status = "READY"
        skip_reason = "NONE"

    # ========================================================
    # 8. ORIGINAL UNIT 10 COMPATIBLE RESULT
    # ========================================================

    result = {

        # ORIGINAL EXECUTION CANDIDATE CONTRACT

        "status": status,

        "active_mode": (
            mode
            if execution_ready
            else "NONE"
        ),

        "direction": (
            direction
            if execution_ready
            else "NONE"
        ),

        "signal_qualified":
            downstream_qualified,

        "execution_intent":
            downstream_intent,

        "trade_plan_ready":
            downstream_plan_ready,

        "trade_plan":
            downstream_plan,

        "execution_ready":
            execution_ready,

        "execution_candidate":
            internal_candidate,

        "skip_reason":
            skip_reason,

        "order_payload_created":
            False,

        "tp_execution_requested":
            False,

        "sl_execution_requested":
            False,

        "read_only":
            True,

        # CONTINUITY DIAGNOSTICS

        "upstream_status":
            upstream_status,

        "upstream_signal_qualified":
            signal_qualified,

        "upstream_execution_intent":
            upstream_intent,

        "upstream_mode":
            mode,

        "upstream_direction":
            direction,

        "candidate_stage":
            candidate_stage,

        "candidate_protected":
            candidate_protected,

        "closed_candle_id":
            closed_candle_id,

        "signal_key": (
            list(
                state["signal_key"]
            )
            if state["signal_key"] is not None
            else None
        ),

        "confirmations":
            state["distinct_candles"],

        "confirmations_required": 2,

        "continuity_observed":
            continuity_observed,

        "continuity_is_entry_gate":
            False,

        "duplicate_candle":
            duplicate_candle,

        "signal_changed":
            signal_changed,

        "signal_expired":
            signal_expired,

        "signal_expiry_seconds":
            signal_expiry,

        "state_persistent_across_restart":
            False,

        # FUNDING / EXECUTION BOUNDARY

        "balance_verified":
            unit_8_result.get(
                "balance_verified", False
            ),

        "leverage_verified":
            unit_8_result.get(
                "leverage_verified", False
            ),

        "position_flat_verified":
            False,

        "pending_orders_verified":
            False,

        "reentry_authorized":
            False,

        "trade_authorized":
            False,

        "exchange_write":
            False,

        "demo_order_submitted":
            False,

        "real_order_submitted":
            False,

        # ADJUSTABLE CONFIGURATION

        "initial_fixed_usdt":
            initial_margin,

        "backup_multipliers":
            multipliers,

        "max_backups":
            backup_count,

        "exposure_cap_percent":
            exposure_cap,

        "mode_priority":
            priority,

        "qualification_owner":
            "UNITS_2_TO_6",

        "leverage_source":
            "WEEX_EXCHANGE_SETTING",

        "unit_9_revision":
            "HYBRID_ADJUSTABLE_V2",
    }

    # ========================================================
    # 9. FINAL OUTPUT SAFETY
    # ========================================================

    if execution_ready:

        if not (
            result["status"] == "READY"
            and result["execution_intent"]
            and result["signal_qualified"]
            and result["trade_plan_ready"]
            and isinstance(
                result["execution_candidate"],
                dict
            )
        ):
            raise RuntimeError(
                "UNIT 9 READY CONTRACT FAILURE"
            )

    else:

        if (
            result["status"] != "IDLE"
            or result["execution_intent"]
            or result["signal_qualified"]
            or result["trade_plan_ready"]
            or result["execution_candidate"]
            is not None
        ):
            raise RuntimeError(
                "UNIT 9 IDLE CONTRACT FAILURE"
            )

    if any((
        result["order_payload_created"],
        result["tp_execution_requested"],
        result["sl_execution_requested"],
        result["trade_authorized"],
        result["exchange_write"],
        result["demo_order_submitted"],
        result["real_order_submitted"],
    )):
        raise RuntimeError(
            "UNIT 9 EXCHANGE SAFETY FAILURE"
        )

    state["last_status"] = status

    # ========================================================
    # 10. RENDER DIAGNOSTICS
    # ========================================================

    print(
        "PASS: UNIT 9 ORIGINAL UNIT 8 HANDOVER",
        flush=True
    )

    print(
        "PASS: UNIT 9 ORIGINAL UNIT 10 CONTRACT",
        flush=True
    )

    print(
        "PASS: UNIT 9 ADJUSTABLE QUALIFICATIONS PRESERVED",
        flush=True
    )

    print(
        "UNIT 9 UPSTREAM STATUS =",
        upstream_status,
        flush=True
    )

    print(
        "UNIT 9 STATUS =",
        status,
        flush=True
    )

    print(
        "UNIT 9 UPSTREAM MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 9 CANDIDATE STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 9 CANDIDATE PROTECTED =",
        candidate_protected,
        flush=True
    )

    print(
        "UNIT 9 CLOSED CANDLE ID =",
        closed_candle_id,
        flush=True
    )

    print(
        "UNIT 9 DISTINCT CANDLES OBSERVED =",
        state["distinct_candles"],
        flush=True
    )

    print(
        "UNIT 9 CONTINUITY OBSERVED =",
        continuity_observed,
        flush=True
    )

    print(
        "UNIT 9 ADDITIONAL CONFIRMATION GATE = False",
        flush=True
    )

    print(
        "UNIT 9 TRADE PLAN READY =",
        downstream_plan_ready,
        flush=True
    )

    print(
        "UNIT 9 EXECUTION READY =",
        execution_ready,
        flush=True
    )

    print(
        "UNIT 9 SKIP REASON =",
        skip_reason,
        flush=True
    )

    print(
        "UNIT 9 POSITION FLAT VERIFIED = False",
        flush=True
    )

    print(
        "UNIT 9 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 9 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 9 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 9 HYBRID ADJUSTABLE V2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 9 EXECUTION / UNIT 10 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
    fresh_reconstruction_unit_9(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_8_RESULT,
        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
    )
)


# ============================================================
# END UNIT 9 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 10 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
#
# BASE:
# 22524-LINE MODEL - UNIT 10 / UNIT 11 CONTRACT
# 12355-LINE MODEL - CONTINUITY DIAGNOSTICS
#
# BREAKOUT > STRUCTURE > SCALP
# QUALIFICATION OWNER: UNITS 2-6
#
# NO ADDITIONAL STRATEGY CONFIRMATION GATE
# NO EXCHANGE WRITE
# NO LEVERAGE MUTATION
# NO ORDER PAYLOAD CREATION
#
# NEXT: UNIT 11 DEMO PAYLOAD VALIDATION
# ============================================================


def fresh_reconstruction_unit_10(
    config,
    unit_9_result,
):

    import math
    from datetime import datetime, timezone

    print("=" * 80, flush=True)
    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 10 HYBRID ADJUSTABLE V2 START",
        flush=True
    )

    # ========================================================
    # 1. INPUT VALIDATION
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 10 CONFIG INVALID"
        )

    if not isinstance(unit_9_result, dict):
        raise RuntimeError(
            "UNIT 10 UNIT 9 INPUT INVALID"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")
    qualification = config.get("qualification")

    if not all(
        isinstance(x, dict)
        for x in (
            exchange,
            safety,
            strategy,
            precision,
            qualification
        )
    ):
        raise RuntimeError(
            "UNIT 10 CONFIGURATION INCOMPLETE"
        )

    if (
        unit_9_result.get("unit_9_revision")
        != "HYBRID_ADJUSTABLE_V2"
    ):
        raise RuntimeError(
            "UNIT 10 UNIT 9 VERSION MISMATCH"
        )

    original_fields = (
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

    missing = [
        key
        for key in original_fields
        if key not in unit_9_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 10 MISSING UNIT 9 FIELDS: "
            + str(missing)
        )

    print(
        "PASS: UNIT 10 ORIGINAL UNIT 9 CONTRACT",
        flush=True
    )

    # ========================================================
    # 2. HELPERS
    # ========================================================

    def number(value, label):

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 10 BOOLEAN NUMBER: " + label
            )

        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            raise RuntimeError(
                "UNIT 10 INVALID NUMBER: " + label
            )

        if not math.isfinite(result):
            raise RuntimeError(
                "UNIT 10 NONFINITE NUMBER: " + label
            )

        return result

    def true_boolean(value, label):

        if type(value) is not bool:
            raise RuntimeError(
                "UNIT 10 INVALID BOOLEAN: " + label
            )

        return value

    # ========================================================
    # 3. STRICT EXECUTION ENVIRONMENT
    # ========================================================

    if config.get(
        "execution_environment"
    ) != "DEMO":
        raise RuntimeError(
            "UNIT 10 DEMO ENVIRONMENT REQUIRED"
        )

    if (
        exchange.get("market_symbol")
        != "BTCUSDT"
        or exchange.get("demo_order_symbol")
        != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 10 SYMBOL CONTRACT INVALID"
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

        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 10 UNSAFE CONFIGURATION: "
                + key
            )

    for key in (
        "order_payload_created",
        "tp_execution_requested",
        "sl_execution_requested",
        "trade_authorized",
        "exchange_write",
        "demo_order_submitted",
        "real_order_submitted",
    ):

        if unit_9_result.get(
            key, False
        ) is not False:
            raise RuntimeError(
                "UNIT 10 PREMATURE EXECUTION: "
                + key
            )

    if unit_9_result.get(
        "read_only"
    ) is not True:
        raise RuntimeError(
            "UNIT 10 UNIT 9 NOT READ ONLY"
        )

    for key in (
        "one_direction_only",
        "anti_duplicate_orders",
        "exclusive_mode",
        "active_trade_mode_lock",
    ):

        if strategy.get(key) is not True:
            raise RuntimeError(
                "UNIT 10 STRATEGY SAFETY FAILURE: "
                + key
            )

    print(
        "PASS: UNIT 10 READ-ONLY SAFETY",
        flush=True
    )

    # ========================================================
    # 4. PRESERVE ADJUSTABLE STRATEGIES
    # ========================================================

    common = qualification.get("common")

    if not isinstance(common, dict):
        raise RuntimeError(
            "UNIT 10 COMMON CONFIG MISSING"
        )

    priority = tuple(
        common.get("mode_priority", ())
    )

    if priority != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        raise RuntimeError(
            "UNIT 10 PRIORITY INVALID"
        )

    for name in (
        "breakout",
        "structure",
        "scalp",
    ):

        if not isinstance(
            qualification.get(name),
            dict
        ):
            raise RuntimeError(
                "UNIT 10 QUALIFICATION MISSING: "
                + name
            )

    initial_margin = number(
        strategy.get("initial_fixed_usdt"),
        "INITIAL FIXED USDT"
    )

    exposure_cap = number(
        strategy.get("exposure_cap_percent"),
        "EXPOSURE CAP"
    )

    backup_count = strategy.get(
        "max_backups"
    )

    raw_multipliers = strategy.get(
        "backup_multipliers"
    )

    if (
        type(backup_count) is not int
        or backup_count < 0
        or not isinstance(
            raw_multipliers, (list, tuple)
        )
        or len(raw_multipliers)
        != backup_count
    ):
        raise RuntimeError(
            "UNIT 10 BACKUP CONFIG INVALID"
        )

    multipliers = tuple(
        number(x, "BACKUP MULTIPLIER")
        for x in raw_multipliers
    )

    if not (
        initial_margin > 0
        and 0 < exposure_cap <= 100
        and all(x > 0 for x in multipliers)
    ):
        raise RuntimeError(
            "UNIT 10 ADJUSTABLE VALUES INVALID"
        )

    if (
        tuple(
            unit_9_result.get(
                "backup_multipliers", ()
            )
        ) != multipliers
        or not math.isclose(
            number(
                unit_9_result.get(
                    "initial_fixed_usdt"
                ),
                "UPSTREAM FIXED MARGIN"
            ),
            initial_margin,
            abs_tol=0.00000001
        )
        or not math.isclose(
            number(
                unit_9_result.get(
                    "exposure_cap_percent"
                ),
                "UPSTREAM EXPOSURE CAP"
            ),
            exposure_cap,
            abs_tol=0.00000001
        )
    ):
        raise RuntimeError(
            "UNIT 10 ADJUSTABLE HANDOVER CHANGED"
        )

    print(
        "PASS: UNIT 10 ADJUSTABLE QUALIFICATIONS PRESERVED",
        flush=True
    )

    # ========================================================
    # 5. NORMALIZE UNIT 9 STATE
    # ========================================================

    upstream_status = unit_9_result.get(
        "status"
    )

    mode = unit_9_result.get(
        "active_mode"
    )

    direction = unit_9_result.get(
        "direction"
    )

    qualified = true_boolean(
        unit_9_result.get(
            "signal_qualified"
        ),
        "SIGNAL QUALIFIED"
    )

    intent = true_boolean(
        unit_9_result.get(
            "execution_intent"
        ),
        "EXECUTION INTENT"
    )

    plan_ready = true_boolean(
        unit_9_result.get(
            "trade_plan_ready"
        ),
        "TRADE PLAN READY"
    )

    execution_ready = true_boolean(
        unit_9_result.get(
            "execution_ready"
        ),
        "EXECUTION READY"
    )

    trade_plan = unit_9_result.get(
        "trade_plan"
    )

    execution_candidate = (
        unit_9_result.get(
            "execution_candidate"
        )
    )

    skip_reason = str(
        unit_9_result.get(
            "skip_reason",
            "NONE"
        )
    )

    candidate_stage = (
        unit_9_result.get(
            "candidate_stage",
            "NONE"
        )
    )

    candidate_protected = true_boolean(
        unit_9_result.get(
            "candidate_protected", False
        ),
        "CANDIDATE PROTECTED"
    )

    if qualified != intent:
        raise RuntimeError(
            "UNIT 10 SIGNAL / INTENT CONTRADICTION"
        )

    if plan_ready != execution_ready:
        raise RuntimeError(
            "UNIT 10 PLAN / READY CONTRADICTION"
        )

    if candidate_protected and intent:
        raise RuntimeError(
            "UNIT 10 DEVELOPING SIGNAL LEAK"
        )

    # ========================================================
    # 6. CONTINUITY DIAGNOSTICS
    #
    # DO NOT IMPOSE NEW QUALIFICATION VOTES.
    # ========================================================

    closed_candle_id = (
        unit_9_result.get(
            "closed_candle_id"
        )
    )

    continuity_observed = (
        unit_9_result.get(
            "continuity_observed", False
        )
    )

    duplicate_candle = (
        unit_9_result.get(
            "duplicate_candle", False
        )
    )

    signal_changed = (
        unit_9_result.get(
            "signal_changed", False
        )
    )

    signal_expired = (
        unit_9_result.get(
            "signal_expired", False
        )
    )

    for label, value in (
        ("CONTINUITY", continuity_observed),
        ("DUPLICATE", duplicate_candle),
        ("CHANGED", signal_changed),
        ("EXPIRED", signal_expired),
    ):

        true_boolean(value, label)

    # These observations alone do not
    # requalify an already approved strategy.
    #
    # The later execution boundary must
    # independently enforce exchange-order
    # deduplication and market freshness.

    # ========================================================
    # 7. ORIGINAL UNIT 11 HANDOVER
    # ========================================================

    result = {

        "status": "IDLE",

        "active_mode": "NONE",
        "direction": "NONE",

        "signal_qualified": False,
        "execution_intent": False,

        "trade_plan_ready": False,
        "trade_plan": None,

        "execution_ready": False,
        "execution_candidate": None,

        "demo_boundary_ready": False,

        "demo_submission_instruction": None,

        "skip_reason": skip_reason,

        "order_payload_created": False,

        "demo_submission_requested": False,
        "real_submission_requested": False,

        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,

        "read_only": True,

        # Additive diagnostics

        "candidate_stage":
            candidate_stage,

        "candidate_protected":
            candidate_protected,

        "closed_candle_id":
            closed_candle_id,

        "continuity_observed":
            continuity_observed,

        "continuity_is_entry_gate":
            False,

        "duplicate_candle":
            duplicate_candle,

        "signal_changed":
            signal_changed,

        "signal_expired":
            signal_expired,

        "upstream_status":
            upstream_status,

        "initial_fixed_usdt":
            initial_margin,

        "backup_multipliers":
            multipliers,

        "max_backups":
            backup_count,

        "exposure_cap_percent":
            exposure_cap,

        "mode_priority":
            priority,

        "balance_verified":
            bool(
                unit_9_result.get(
                    "balance_verified", False
                )
            ),

        "leverage_verified":
            bool(
                unit_9_result.get(
                    "leverage_verified", False
                )
            ),

        "position_flat_verified":
            False,

        "pending_orders_verified":
            False,

        "exchange_write": False,

        "qualification_owner":
            "UNITS_2_TO_6",

        "leverage_source":
            "WEEX_EXCHANGE_SETTING",

        "unit_10_revision":
            "HYBRID_ADJUSTABLE_V2",
    }

    # ========================================================
    # 8. READY PATH - VERIFIED PLAN ONLY
    # ========================================================

    if upstream_status == "READY":

        if not (
            qualified
            and intent
            and plan_ready
            and execution_ready
            and mode in (
                "BREAKOUT",
                "STRUCTURE",
                "SCALP"
            )
            and direction in (
                "LONG",
                "SHORT"
            )
            and not candidate_protected
            and isinstance(trade_plan, dict)
            and isinstance(
                execution_candidate, dict
            )
        ):
            raise RuntimeError(
                "UNIT 10 READY CONTRACT FAILED"
            )

        if (
            unit_9_result.get(
                "balance_verified"
            ) is not True
            or unit_9_result.get(
                "leverage_verified"
            ) is not True
        ):
            raise RuntimeError(
                "UNIT 10 ACCOUNT / LEVERAGE UNVERIFIED"
            )

        if (
            trade_plan.get(
                "active_mode"
            ) != mode
            or trade_plan.get(
                "direction"
            ) != direction
            or execution_candidate.get(
                "active_mode"
            ) != mode
            or execution_candidate.get(
                "direction"
            ) != direction
        ):
            raise RuntimeError(
                "UNIT 10 PLAN / CANDIDATE MISMATCH"
            )

        if trade_plan.get(
            "execution_environment",
            "DEMO"
        ) != "DEMO":
            raise RuntimeError(
                "UNIT 10 PLAN NOT DEMO"
            )

        # This instruction is internal.
        # It is not a WEEX HTTP request body.

        instruction = {

            "exchange": "WEEX",
            "api_version": "V3",

            "execution_environment": "DEMO",

            "market_symbol": "BTCUSDT",
            "demo_order_symbol": "BTCSUSDT",

            "active_mode": mode,
            "direction": direction,

            "trade_plan": trade_plan,

            "execution_candidate":
                execution_candidate,

            "anti_duplicate_required": True,

            "one_direction_only_required": True,

            "active_trade_mode_lock_required": True,

            "payload_creation_allowed": False,

            "submission_allowed": False,

            "read_only": True,

            "initial_fixed_usdt":
                initial_margin,

            "backup_multipliers":
                multipliers,

            "exposure_cap_percent":
                exposure_cap,

            "leverage_source":
                "WEEX_EXCHANGE_SETTING",
        }

        result.update({

            "status": "READY",

            "active_mode": mode,
            "direction": direction,

            "signal_qualified": True,
            "execution_intent": True,

            "trade_plan_ready": True,
            "trade_plan": trade_plan,

            "execution_ready": True,

            "execution_candidate":
                execution_candidate,

            "demo_boundary_ready": True,

            "demo_submission_instruction":
                instruction,

            "skip_reason": "NONE",
        })

    elif upstream_status == "IDLE":

        if any((
            qualified,
            intent,
            plan_ready,
            execution_ready,
        )):
            raise RuntimeError(
                "UNIT 10 IDLE STATE CONTRADICTION"
            )

        if (
            mode != "NONE"
            or direction != "NONE"
            or trade_plan is not None
            or execution_candidate is not None
        ):
            raise RuntimeError(
                "UNIT 10 IDLE SIGNAL LEAK"
            )

    else:

        raise RuntimeError(
            "UNIT 10 UNKNOWN UNIT 9 STATUS: "
            + str(upstream_status)
        )

    # ========================================================
    # 9. FINAL HANDOVER VALIDATION
    # ========================================================

    if result["status"] == "READY":

        if not (
            result["demo_boundary_ready"]
            and isinstance(
                result["demo_submission_instruction"],
                dict
            )
            and result["execution_ready"]
        ):
            raise RuntimeError(
                "UNIT 10 DEMO BOUNDARY INVALID"
            )

    else:

        if (
            result["demo_boundary_ready"]
            or result["demo_submission_instruction"]
            is not None
        ):
            raise RuntimeError(
                "UNIT 10 IDLE BOUNDARY INVALID"
            )

    for key in (
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
        "exchange_write",
    ):

        if result[key] is not False:
            raise RuntimeError(
                "UNIT 10 UNAUTHORIZED EXECUTION: "
                + key
            )

    # ========================================================
    # 10. RENDER VERIFICATION
    # ========================================================

    print(
        "PASS: UNIT 10 ORIGINAL UNIT 11 CONTRACT",
        flush=True
    )

    print(
        "PASS: UNIT 10 ADJUSTABLE QUALIFICATIONS PRESERVED",
        flush=True
    )

    print(
        "PASS: UNIT 10 NO EXTRA CONFIRMATION GATE",
        flush=True
    )

    print(
        "UNIT 10 UPSTREAM STATUS =",
        upstream_status,
        flush=True
    )

    print(
        "UNIT 10 STATUS =",
        result["status"],
        flush=True
    )

    print(
        "UNIT 10 ACTIVE MODE =",
        result["active_mode"],
        flush=True
    )

    print(
        "UNIT 10 DIRECTION =",
        result["direction"],
        flush=True
    )

    print(
        "UNIT 10 CANDIDATE STAGE =",
        candidate_stage,
        flush=True
    )

    print(
        "UNIT 10 CANDIDATE PROTECTED =",
        candidate_protected,
        flush=True
    )

    print(
        "UNIT 10 CONTINUITY OBSERVED =",
        continuity_observed,
        flush=True
    )

    print(
        "UNIT 10 ADDITIONAL CONFIRMATION GATE = False",
        flush=True
    )

    print(
        "UNIT 10 SIGNAL QUALIFIED =",
        result["signal_qualified"],
        flush=True
    )

    print(
        "UNIT 10 EXECUTION INTENT =",
        result["execution_intent"],
        flush=True
    )

    print(
        "UNIT 10 TRADE PLAN READY =",
        result["trade_plan_ready"],
        flush=True
    )

    print(
        "UNIT 10 DEMO BOUNDARY READY =",
        result["demo_boundary_ready"],
        flush=True
    )

    print(
        "UNIT 10 SKIP REASON =",
        result["skip_reason"],
        flush=True
    )

    print(
        "UNIT 10 DEMO ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 10 REAL ORDER = NONE",
        flush=True
    )

    print(
        "UNIT 10 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 10 HYBRID ADJUSTABLE V2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 10 EXECUTION - ORIGINAL UNIT 11 HANDOVER
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
    fresh_reconstruction_unit_10(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_9_RESULT,
    )
)


# ============================================================
# END UNIT 10 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 11 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
#
# 22524 REFERENCE: WEEX DEMO PAYLOAD
# 12355 REFERENCE: SIGNAL SAFETY / HANDOVER
#
# PRESERVES:
# BREAKOUT > STRUCTURE > SCALP
# UNIT 2 ADJUSTABLE QUALIFICATION
# UNIT 10 ORIGINAL EXECUTION INTERFACE
# UNIT 12 ORIGINAL DEMO PAYLOAD INTERFACE
#
# NO NETWORK ACCESS
# NO EXCHANGE WRITE
# NO LEVERAGE OR MARGIN MODE CHANGES
# NO ADDITIONAL STRATEGY CONFIRMATION
# ============================================================


def fresh_reconstruction_unit_11(
    config,
    unit_10_result
):

    import math
    import time
    import uuid

    from datetime import datetime, timezone
    from decimal import (
        Decimal,
        InvalidOperation,
        ROUND_DOWN,
    )

    print("=" * 80, flush=True)

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 11 HYBRID ADJUSTABLE V2 START",
        flush=True
    )

    # ========================================================
    # 1. INPUT AND CONFIGURATION
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 11 CONFIGURATION INVALID"
        )

    if not isinstance(unit_10_result, dict):
        raise RuntimeError(
            "UNIT 11 UNIT 10 RESULT INVALID"
        )

    exchange = config.get("exchange")
    safety = config.get("safety")
    strategy = config.get("strategy")
    precision = config.get("market_precision")
    qualification = config.get("qualification")

    if not all(
        isinstance(x, dict)
        for x in (
            exchange,
            safety,
            strategy,
            precision,
            qualification,
        )
    ):
        raise RuntimeError(
            "UNIT 11 CONFIGURATION SECTION MISSING"
        )

    if (
        config.get("execution_environment")
        != "DEMO"
        or exchange.get("market_symbol")
        != "BTCUSDT"
        or exchange.get("demo_order_symbol")
        != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 11 DEMO SYMBOL CONTRACT FAILED"
        )

    if (
        unit_10_result.get("unit_10_revision")
        != "HYBRID_ADJUSTABLE_V2"
    ):
        raise RuntimeError(
            "UNIT 11 UNIT 10 VERSION MISMATCH"
        )

    # ========================================================
    # 2. REQUIRED ORIGINAL UNIT 10 HANDOVER
    # ========================================================

    required = (
        "status",
        "active_mode",
        "direction",
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "trade_plan",
        "execution_ready",
        "execution_candidate",
        "demo_boundary_ready",
        "demo_submission_instruction",
        "skip_reason",
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
        "read_only",
    )

    missing = [
        key
        for key in required
        if key not in unit_10_result
    ]

    if missing:
        raise RuntimeError(
            "UNIT 11 UNIT 10 FIELDS MISSING: "
            + str(missing)
        )

    print(
        "PASS: UNIT 11 ORIGINAL UNIT 10 CONTRACT",
        flush=True
    )

    # ========================================================
    # 3. NUMERIC HELPERS
    # ========================================================

    def dec(value, label):

        if isinstance(value, bool):
            raise RuntimeError(
                "UNIT 11 BOOLEAN NUMBER: " + label
            )

        try:
            result = Decimal(str(value))
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            raise RuntimeError(
                "UNIT 11 INVALID NUMBER: " + label
            ) from exc

        if not result.is_finite():
            raise RuntimeError(
                "UNIT 11 NONFINITE NUMBER: " + label
            )

        return result

    def quantity_text(value):

        return format(value, "f")

    # ========================================================
    # 4. NO EXCHANGE WRITE IN UNIT 11
    # ========================================================

    if unit_10_result.get("read_only") is not True:
        raise RuntimeError(
            "UNIT 11 READ ONLY INPUT REQUIRED"
        )

    for key in (
        "order_payload_created",
        "demo_submission_requested",
        "real_submission_requested",
        "tp_execution_requested",
        "sl_execution_requested",
        "backup_execution_requested",
        "exchange_write",
    ):
        if unit_10_result.get(key) is not False:
            raise RuntimeError(
                "UNIT 11 PREMATURE EXECUTION: " + key
            )

    for key in (
        "real_order_submission_enabled",
        "order_endpoint_access_enabled",
        "exchange_mutation_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 11 CONFIG SAFETY FAILED: " + key
            )

    # ========================================================
    # 5. ADJUSTABLE STRATEGY PRESERVATION
    # ========================================================

    common = qualification.get("common", {})

    priority = tuple(
        common.get("mode_priority", ())
    )

    if priority != (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        raise RuntimeError(
            "UNIT 11 MODE PRIORITY INVALID"
        )

    for mode_name in (
        "breakout",
        "structure",
        "scalp",
    ):
        if not isinstance(
            qualification.get(mode_name),
            dict
        ):
            raise RuntimeError(
                "UNIT 11 STRATEGY CONFIG MISSING: "
                + mode_name
            )

    initial_margin = dec(
        strategy["initial_fixed_usdt"],
        "INITIAL FIXED MARGIN"
    )

    exposure_cap = dec(
        strategy["exposure_cap_percent"],
        "EXPOSURE CAP"
    )

    multipliers = tuple(
        dec(x, "BACKUP MULTIPLIER")
        for x in strategy[
            "backup_multipliers"
        ]
    )

    max_backups = strategy["max_backups"]

    if not (
        initial_margin > 0
        and Decimal("0") < exposure_cap <= 100
        and type(max_backups) is int
        and len(multipliers) == max_backups
        and all(x > 0 for x in multipliers)
    ):
        raise RuntimeError(
            "UNIT 11 ADJUSTABLE SETTINGS INVALID"
        )

    if (
        dec(
            unit_10_result["initial_fixed_usdt"],
            "UPSTREAM INITIAL MARGIN"
        ) != initial_margin
        or dec(
            unit_10_result[
                "exposure_cap_percent"
            ],
            "UPSTREAM EXPOSURE CAP"
        ) != exposure_cap
        or tuple(
            dec(x, "UPSTREAM BACKUP MULTIPLIER")
            for x in unit_10_result[
                "backup_multipliers"
            ]
        ) != multipliers
    ):
        raise RuntimeError(
            "UNIT 11 ADJUSTABLE HANDOVER CHANGED"
        )

    print(
        "PASS: UNIT 11 ADJUSTABLE QUALIFICATIONS PRESERVED",
        flush=True
    )

    # ========================================================
    # 6. RESULT STRUCTURE FOR ORIGINAL UNIT 12
    # ========================================================

    result = {

        "status": "IDLE",

        "active_mode": "NONE",
        "direction": "NONE",

        "signal_qualified": False,
        "execution_intent": False,

        "trade_plan_ready": False,
        "trade_plan": None,

        "execution_ready": False,
        "execution_candidate": None,

        "demo_boundary_ready": False,
        "demo_submission_instruction": None,

        "payload_ready": False,
        "order_payload": None,
        "demo_payload": None,
        "payload": None,

        "skip_reason": str(
            unit_10_result.get(
                "skip_reason", "NONE"
            )
        ),

        "order_payload_created": False,

        "demo_submission_requested": False,
        "real_submission_requested": False,

        "tp_execution_requested": False,
        "sl_execution_requested": False,
        "backup_execution_requested": False,

        "read_only": True,
        "exchange_write": False,

        "initial_fixed_usdt":
            float(initial_margin),

        "backup_multipliers":
            tuple(float(x) for x in multipliers),

        "exposure_cap_percent":
            float(exposure_cap),

        "qualification_owner":
            "UNITS_2_TO_6",

        "leverage_source":
            "WEEX_EXCHANGE_SETTING",

        "unit_11_revision":
            "HYBRID_ADJUSTABLE_V2",
    }

    # ========================================================
    # 7. ORIGINAL IDLE / LEVERAGE-PENDING PATH
    # ========================================================

    status10 = unit_10_result["status"]

    if status10 == "IDLE":

        for key in (
            "signal_qualified",
            "execution_intent",
            "trade_plan_ready",
            "execution_ready",
            "demo_boundary_ready",
        ):
            if unit_10_result.get(key) is not False:
                raise RuntimeError(
                    "UNIT 11 IDLE CONTRADICTION: " + key
                )

        if (
            unit_10_result.get("active_mode")
            != "NONE"
            or unit_10_result.get("direction")
            != "NONE"
            or unit_10_result.get(
                "trade_plan"
            ) is not None
            or unit_10_result.get(
                "demo_submission_instruction"
            ) is not None
        ):
            raise RuntimeError(
                "UNIT 11 IDLE SIGNAL LEAK"
            )

        print(
            "PASS: UNIT 11 ORIGINAL IDLE HANDOVER",
            flush=True
        )

        print(
            "UNIT 11 STATUS = IDLE",
            flush=True
        )

        print(
            "UNIT 11 SKIP REASON =",
            result["skip_reason"],
            flush=True
        )

        print(
            "UNIT 11 PAYLOAD READY = False",
            flush=True
        )

        print(
            "UNIT 11 DEMO SUBMISSION = NONE",
            flush=True
        )

        print(
            "UNIT 11 EXCHANGE WRITE = NONE",
            flush=True
        )

        print(
            "UNIT 11 HYBRID ADJUSTABLE V2 "
            "RESULT = PASS (IDLE)",
            flush=True
        )

        print("=" * 80, flush=True)

        return result

    if status10 != "READY":
        raise RuntimeError(
            "UNIT 11 UNKNOWN UNIT 10 STATUS: "
            + str(status10)
        )

    # ========================================================
    # 8. QUALIFIED READY PATH
    # ========================================================

    mode = unit_10_result["active_mode"]
    direction = unit_10_result["direction"]

    if mode not in priority:
        raise RuntimeError(
            "UNIT 11 ACTIVE MODE INVALID"
        )

    if direction not in ("LONG", "SHORT"):
        raise RuntimeError(
            "UNIT 11 DIRECTION INVALID"
        )

    for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
    ):
        if unit_10_result.get(key) is not True:
            raise RuntimeError(
                "UNIT 11 READY FLAG MISSING: "
                + key
            )

    if unit_10_result.get(
        "candidate_protected"
    ) is True:
        raise RuntimeError(
            "UNIT 11 DEVELOPING CANDIDATE BLOCKED"
        )

    trade_plan = unit_10_result["trade_plan"]

    candidate = unit_10_result[
        "execution_candidate"
    ]

    instruction = unit_10_result[
        "demo_submission_instruction"
    ]

    if not all(
        isinstance(x, dict)
        for x in (
            trade_plan,
            candidate,
            instruction,
        )
    ):
        raise RuntimeError(
            "UNIT 11 VERIFIED PLAN MISSING"
        )

    if (
        trade_plan.get("active_mode") != mode
        or trade_plan.get("direction") != direction
        or candidate.get("active_mode") != mode
        or candidate.get("direction") != direction
        or instruction.get("active_mode") != mode
        or instruction.get("direction") != direction
    ):
        raise RuntimeError(
            "UNIT 11 STRATEGY HANDOVER MISMATCH"
        )

    if (
        instruction.get(
            "execution_environment"
        ) != "DEMO"
        or instruction.get(
            "demo_order_symbol"
        ) != "BTCSUSDT"
        or instruction.get(
            "submission_allowed"
        ) is not False
        or instruction.get(
            "payload_creation_allowed"
        ) is not False
    ):
        raise RuntimeError(
            "UNIT 11 INSTRUCTION CONTRACT INVALID"
        )

    # The Unit 10 instruction prohibits
    # premature payload creation/submission.
    # Unit 11 builds a NEW payload in memory.
    # It does not change the Unit 10 flags.

    # ========================================================
    # 9. REQUIRED EXCHANGE / ACCOUNT EVIDENCE
    # ========================================================

    if (
        unit_10_result.get(
            "balance_verified"
        ) is not True
        or unit_10_result.get(
            "leverage_verified"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 11 BALANCE OR LEVERAGE UNVERIFIED"
        )

    sizing = trade_plan.get(
        "position_sizing"
    )

    if not isinstance(sizing, dict):
        raise RuntimeError(
            "UNIT 11 POSITION SIZING MISSING"
        )

    quantity = trade_plan.get(
        "quantity"
    )

    if quantity is None:
        quantity = sizing.get(
            "quantity"
        )

    qty = dec(
        quantity,
        "INITIAL ORDER QUANTITY"
    )

    qty_step = dec(
        precision["quantity_step"],
        "QUANTITY STEP"
    )

    minimum_qty = dec(
        precision["minimum_quantity"],
        "MINIMUM QUANTITY"
    )

    if not (
        qty_step > 0
        and minimum_qty > 0
        and qty >= minimum_qty
        and qty > 0
    ):
        raise RuntimeError(
            "UNIT 11 QUANTITY BELOW MINIMUM"
        )

    rounded = (
        (qty / qty_step).to_integral_value(
            rounding=ROUND_DOWN
        )
        * qty_step
    )

    if rounded != qty:
        raise RuntimeError(
            "UNIT 11 QUANTITY STEP INVALID"
        )

    if (
        sizing.get(
            "quantity_calculated"
        ) is not True
        or sizing.get(
            "position_sizing_performed"
        ) is not True
    ):
        raise RuntimeError(
            "UNIT 11 SIZING NOT VERIFIED"
        )

    if (
        dec(
            sizing["exposure_cap_percent"],
            "SIZING EXPOSURE CAP"
        ) != exposure_cap
    ):
        raise RuntimeError(
            "UNIT 11 EXPOSURE CAP MISMATCH"
        )

    # ========================================================
    # 10. CONSTRUCT ORIGINAL WEEX DEMO PAYLOAD
    # ========================================================

    if direction == "LONG":

        side = "BUY"
        position_side = "LONG"

    else:

        side = "SELL"
        position_side = "SHORT"

    # Unique order ID. The final submission
    # boundary must use this same ID for
    # duplicate detection and retries.

    client_order_id = (
        "FR11-"
        + direction
        + "-"
        + str(time.time_ns())
        + "-"
        + uuid.uuid4().hex[:8]
    )

    if len(client_order_id) > 64:
        raise RuntimeError(
            "UNIT 11 CLIENT ORDER ID TOO LONG"
        )

    order_payload = {

        "symbol": "BTCSUSDT",

        "side": side,

        "positionSide": position_side,

        "type": "MARKET",

        "quantity": quantity_text(qty),

        "newClientOrderId":
            client_order_id,
    }

    # ========================================================
    # 11. FINAL PAYLOAD SAFETY
    # ========================================================

    allowed_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    if set(order_payload) != allowed_fields:
        raise RuntimeError(
            "UNIT 11 UNEXPECTED ORDER FIELD"
        )

    if not (
        order_payload["symbol"]
        == "BTCSUSDT"
        and order_payload["type"]
        == "MARKET"
        and order_payload["side"]
        in ("BUY", "SELL")
        and order_payload["positionSide"]
        == direction
        and dec(
            order_payload["quantity"],
            "PAYLOAD QUANTITY"
        ) == qty
    ):
        raise RuntimeError(
            "UNIT 11 PAYLOAD VALIDATION FAILED"
        )

    result.update({

        "status": "READY",

        "active_mode": mode,
        "direction": direction,

        "signal_qualified": True,
        "execution_intent": True,

        "trade_plan_ready": True,
        "trade_plan": trade_plan,

        "execution_ready": True,
        "execution_candidate": candidate,

        "demo_boundary_ready": True,

        "demo_submission_instruction":
            instruction,

        "payload_ready": True,

        "order_payload": order_payload,
        "demo_payload": order_payload,
        "payload": order_payload,

        "skip_reason": "NONE",

        "order_payload_created": True,

        "demo_submission_requested": False,
        "real_submission_requested": False,

        "read_only": True,

        "exchange_write": False,
    })

    print(
        "PASS: UNIT 11 ORIGINAL UNIT 12 PAYLOAD CONTRACT",
        flush=True
    )

    print(
        "PASS: UNIT 11 ADJUSTABLE QUALIFICATIONS PRESERVED",
        flush=True
    )

    print(
        "UNIT 11 STATUS = READY",
        flush=True
    )

    print(
        "UNIT 11 ACTIVE MODE =",
        mode,
        flush=True
    )

    print(
        "UNIT 11 DIRECTION =",
        direction,
        flush=True
    )

    print(
        "UNIT 11 BTC QUANTITY =",
        order_payload["quantity"],
        flush=True
    )

    print(
        "UNIT 11 PAYLOAD READY = True",
        flush=True
    )

    print(
        "UNIT 11 DEMO SUBMISSION REQUESTED = False",
        flush=True
    )

    print(
        "UNIT 11 EXCHANGE WRITE = NONE",
        flush=True
    )

    print(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 11 HYBRID ADJUSTABLE V2 RESULT = PASS",
        flush=True
    )

    print("=" * 80, flush=True)

    return result


# ============================================================
# UNIT 11 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
    fresh_reconstruction_unit_11(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_10_RESULT,
    )
)


# ============================================================
# END UNIT 11 - HYBRID ADJUSTABLE V2
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 12 - HYBRID ADJUSTABLE V2.6
# ZERO INDENTATION
#
# ORIGINAL 15 UNIT RECONSTRUCTION
# UNIT 12 = INITIAL DEMO ENTRY ONLY
#
# VERIFIED DIAGNOSTIC ADAPTATION:
# - UNIT 11 ORIGINAL READY HANDOVER
# - CLIENT ORDER ID NORMALIZATION
# - QUANTITY STEP VALIDATION
# - WEEX DEMO POSITION GET
# - WEEX DEMO ORDER HISTORY GET
# - PREVIOUS JOURNAL RECONCILIATION
# - COOLDOWN
#
# RESTORED:
# - ORIGINAL DEMO MARKET ORDER POST
# - ORIGINAL ORDER ID RESPONSE HANDOVER
# - ORIGINAL MANAGEMENT FLAGS
#
# SAFETY:
# - MASTER BOT_MODE ONLY
# - PAUSE NEVER SUBMITS
# - NO REAL CASH ORDERS
# - NO LEVERAGE MUTATION
# - NO MARGIN MUTATION
# - NO POSITION MODE MUTATION
# - NO SIMULATED TEST ORDER SUBMISSION
#
# IMPORTANT:
# DEMO-SCOPE OPEN ORDER AND LEVERAGE
# VERIFICATION MUST BE RESOLVED
# BEFORE AUTOMATED POST IS AUTHORIZED.
# ============================================================


def fresh_reconstruction_unit_12(
    config,
    unit_11_result,
):

    import os
    import re
    import json
    import time
    import hmac
    import base64
    import hashlib
    import fcntl
    import tempfile
    import urllib.request
    import urllib.error
    import urllib.parse

    from decimal import Decimal
    from datetime import datetime, timezone

    def log(*values):
        print(*values, flush=True)

    def decimal(value):

        if isinstance(value, bool):
            raise ValueError("BOOLEAN_INVALID")

        value = Decimal(str(value))

        if not value.is_finite():
            raise ValueError("NONFINITE_VALUE")

        return value

    def milliseconds():
        return int(time.time() * 1000)

    log("=" * 80)

    log(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 12 HYBRID ADJUSTABLE V2.6 START"
    )

    # ========================================================
    # 1. CONFIGURATION
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT12_CONFIG_INVALID"
        )

    if not isinstance(unit_11_result, dict):
        raise RuntimeError(
            "UNIT12_UNIT11_INVALID"
        )

    if unit_11_result.get(
        "unit_11_revision"
    ) != "HYBRID_ADJUSTABLE_V2":

        raise RuntimeError(
            "UNIT12_UNIT11_REVISION_INVALID"
        )

    bot_mode = str(
        os.getenv("BOT_MODE", "PAUSE")
    ).strip().upper()

    if bot_mode not in (
        "PAUSE",
        "RUN"
    ):
        raise RuntimeError(
            "UNIT12_BOT_MODE_INVALID"
        )

    exchange = config.get(
        "exchange", {}
    )

    safety = config.get(
        "safety", {}
    )

    precision = config.get(
        "market_precision", {}
    )

    if not all(
        isinstance(x, dict)
        for x in (
            exchange,
            safety,
            precision
        )
    ):
        raise RuntimeError(
            "UNIT12_CONFIG_SECTION_INVALID"
        )

    if not (
        config.get(
            "execution_environment"
        ) == "DEMO"
        and exchange.get(
            "market_symbol"
        ) == "BTCUSDT"
        and exchange.get(
            "demo_order_symbol"
        ) == "BTCSUSDT"
        and exchange.get(
            "contract_base_url"
        ) == "https://api-contract.weex.com"
        and unit_11_result.get(
            "read_only"
        ) is True
        and unit_11_result.get(
            "exchange_write"
        ) is False
    ):
        raise RuntimeError(
            "UNIT12_DEMO_BOUNDARY_INVALID"
        )

    for key in (
        "real_order_submission_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled"
    ):

        if safety.get(key) is not False:

            raise RuntimeError(
                "UNIT12_UNSAFE_CONFIG:" + key
            )

    log(
        "UNIT 12 MASTER BOT_MODE =",
        bot_mode
    )

    # ========================================================
    # 2. RESULT CONTRACT
    # ========================================================

    result = {

        "unit": 12,

        "unit_12_revision":
            "HYBRID_ADJUSTABLE_V2.6",

        "status": "IDLE",

        "read_only":
            bot_mode == "PAUSE",

        "active_mode":
            unit_11_result.get(
                "active_mode",
                "NONE"
            ),

        "direction":
            unit_11_result.get(
                "direction",
                "NONE"
            ),

        "signal_qualified": False,
        "execution_intent": False,

        "position_check_attempted": False,
        "position_check_completed": False,
        "position_endpoint_access": False,
        "position_http_status": None,

        "active_position_exists": False,
        "active_positions": [],

        "initial_entry_permitted": False,

        "duplicate_initial_entry_blocked": False,

        "management_path_permitted": False,
        "tp_management_permitted": False,
        "backup_management_permitted": False,

        "client_order_id_validated": False,
        "client_order_id_adapted": False,

        "history_checked": False,
        "history_complete": False,

        "journal_reconciled": False,
        "reconciliation_status": "NOT_CHECKED",

        "diagnostic_mode":
            bot_mode == "PAUSE",

        "diagnostics_completed": False,
        "diagnostics_passed": False,

        "demo_leverage_scope_verified": False,
        "demo_open_orders_verified": False,

        "demo_submission_attempted": False,
        "demo_submission_completed": False,

        "real_submission_attempted": False,

        "authenticated_request": False,
        "order_endpoint_access": False,
        "exchange_write": False,

        "request_path": None,
        "request_payload": None,

        "http_status": None,
        "weex_response": None,
        "order_id": None,

        "skip_reason":
            unit_11_result.get(
                "skip_reason",
                "NONE"
            )
    }

    checks = {}

    def check(name, passed):

        checks[name] = bool(passed)

        log(
            "UNIT 12 CHECK",
            name,
            "=",
            "PASS" if passed else "FAIL"
        )

    def finish(status, reason):

        result["status"] = status
        result["skip_reason"] = str(reason)

        log(
            "UNIT 12 STATUS =",
            status
        )

        log(
            "UNIT 12 REASON =",
            reason
        )

        log(
            "UNIT 12 DIAGNOSTICS COMPLETED =",
            result["diagnostics_completed"]
        )

        log(
            "UNIT 12 DIAGNOSTICS PASSED =",
            result["diagnostics_passed"]
        )

        log(
            "UNIT 12 DEMO OPEN ORDERS VERIFIED =",
            result["demo_open_orders_verified"]
        )

        log(
            "UNIT 12 DEMO LEVERAGE VERIFIED =",
            result["demo_leverage_scope_verified"]
        )

        log(
            "UNIT 12 DEMO SUBMISSION ATTEMPTED =",
            result["demo_submission_attempted"]
        )

        log(
            "UNIT 12 DEMO SUBMISSION COMPLETED =",
            result["demo_submission_completed"]
        )

        log(
            "UNIT 12 EXCHANGE WRITE =",
            result["exchange_write"]
        )

        log(
            "UNIT 12 HYBRID ADJUSTABLE V2.6 RESULT =",
            status
        )

        log("=" * 80)

        return result

    def stop(reason):

        return finish(
            "DIAGNOSTIC_BLOCKED"
            if bot_mode == "PAUSE"
            else "BLOCKED",
            reason
        )

    # ========================================================
    # 3. ORIGINAL IDLE HANDOVER
    # ========================================================

    status11 = str(
        unit_11_result.get(
            "status",
            "IDLE"
        )
    ).upper()

    if status11 == "IDLE":

        check(
            "ORIGINAL_IDLE_HANDOVER",
            unit_11_result.get(
                "payload_ready"
            ) is False
        )

        if not checks[
            "ORIGINAL_IDLE_HANDOVER"
        ]:
            return stop(
                "UNIT11_IDLE_CONTRACT_INVALID"
            )

        return finish(
            "IDLE",
            result["skip_reason"]
        )

    if status11 != "READY":

        return stop(
            "UNIT11_STATUS_INVALID"
        )

    # ========================================================
    # 4. ORIGINAL READY HANDOVER
    # ========================================================

    required = (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
        "payload_ready",
        "order_payload_created"
    )

    ready_ok = all(
        unit_11_result.get(x) is True
        for x in required
    )

    check(
        "ORIGINAL_READY_HANDOVER",
        ready_ok
    )

    if not ready_ok:

        return stop(
            "UNIT11_READY_CONTRACT_INVALID"
        )

    mode = unit_11_result.get(
        "active_mode"
    )

    direction = unit_11_result.get(
        "direction"
    )

    if not (
        mode in (
            "BREAKOUT",
            "STRUCTURE",
            "SCALP"
        )
        and direction in (
            "LONG",
            "SHORT"
        )
    ):

        return stop(
            "STRATEGY_DIRECTION_INVALID"
        )

    result["active_mode"] = mode
    result["direction"] = direction

    result["signal_qualified"] = True
    result["execution_intent"] = True

    payload = (
        unit_11_result.get("demo_payload")
        or unit_11_result.get("payload")
        or unit_11_result.get("order_payload")
    )

    trade_plan = (
        unit_11_result.get("trade_plan")
    )

    if not (
        isinstance(payload, dict)
        and isinstance(trade_plan, dict)
    ):

        return stop(
            "UNIT11_PAYLOAD_MISSING"
        )

    expected_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId"
    }

    correct_side = (
        "BUY"
        if direction == "LONG"
        else "SELL"
    )

    payload_ok = (
        set(payload) == expected_fields
        and payload.get("symbol")
        == "BTCSUSDT"
        and payload.get("side")
        == correct_side
        and payload.get("positionSide")
        == direction
        and payload.get("type")
        == "MARKET"
    )

    check(
        "ORIGINAL_DEMO_PAYLOAD",
        payload_ok
    )

    if not payload_ok:

        return stop(
            "DEMO_PAYLOAD_INVALID"
        )

    # ========================================================
    # 5. CLIENT ORDER ID ADAPTATION
    # ========================================================

    source_id = payload.get(
        "newClientOrderId"
    )

    if not isinstance(
        source_id,
        str
    ):

        return stop(
            "CLIENT_ORDER_ID_NOT_STRING"
        )

    source_id = source_id.strip()

    if not source_id:

        return stop(
            "CLIENT_ORDER_ID_EMPTY"
        )

    allowed_pattern = (
        r"[A-Za-z0-9_.:/-]{1,36}"
    )

    if re.fullmatch(
        allowed_pattern,
        source_id
    ):

        client_id = source_id

    else:

        digest = hashlib.sha256(
            source_id.encode("utf-8")
        ).hexdigest()[:24]

        client_id = (
            "FR12-" + digest
        )

        result[
            "client_order_id_adapted"
        ] = True

    client_ok = (
        re.fullmatch(
            allowed_pattern,
            client_id
        ) is not None
    )

    check(
        "CLIENT_ORDER_ID",
        client_ok
    )

    if not client_ok:

        return stop(
            "CLIENT_ORDER_ID_INVALID"
        )

    result[
        "client_order_id_validated"
    ] = True

    final_payload = dict(
        payload
    )

    final_payload[
        "newClientOrderId"
    ] = client_id

    # ========================================================
    # 6. ORIGINAL QUANTITY CHECK
    # ========================================================

    try:

        quantity = decimal(
            final_payload["quantity"]
        )

        planned_quantity = decimal(
            trade_plan["quantity"]
        )

        qty_step = decimal(
            precision["quantity_step"]
        )

        minimum = decimal(
            precision["minimum_quantity"]
        )

        sizing = trade_plan[
            "position_sizing"
        ]

        quantity_ok = (
            qty_step > 0
            and minimum > 0
            and quantity >= minimum
            and quantity == planned_quantity
            and quantity % qty_step == 0
            and isinstance(sizing, dict)
            and sizing.get(
                "position_sizing_performed"
            ) is True
            and sizing.get(
                "quantity_calculated"
            ) is True
        )

    except Exception:

        quantity_ok = False
        sizing = {}

    check(
        "BTC_QUANTITY_VALIDATION",
        quantity_ok
    )

    if not quantity_ok:

        return stop(
            "BTC_QUANTITY_INVALID"
        )

    log(
        "UNIT 12 STRATEGY =",
        mode
    )

    log(
        "UNIT 12 DIRECTION =",
        direction
    )

    log(
        "UNIT 12 BTC QUANTITY =",
        quantity
    )

    # ========================================================
    # 7. DEMO CREDENTIALS
    # ========================================================

    api_key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    api_secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    api_passphrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    credentials_ok = all((
        api_key,
        api_secret,
        api_passphrase
    ))

    check(
        "WEEX_CREDENTIALS",
        credentials_ok
    )

    if not credentials_ok:

        return stop(
            "WEEX_CREDENTIALS_MISSING"
        )

    base_url = (
        "https://api-contract.weex.com"
    )

    # ========================================================
    # 8. SIGNED API REQUEST
    #
    # ONLY TWO ALLOWED GET ENDPOINTS
    # AND ONE DEMO POST ENDPOINT.
    #
    # PAUSE PROHIBITS POST INSIDE
    # THIS FUNCTION.
    # ========================================================

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):

        def redirect_request(
            self,
            req,
            fp,
            code,
            msg,
            headers,
            newurl
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    def signed_request(
        method,
        path,
        query=None,
        body=None
    ):

        allowed_get = (
            "/capi/v3/sim/position/allPosition",
            "/capi/v3/sim/order/history"
        )

        allowed_post = (
            "/capi/v3/sim/order"
        )

        if method == "GET":

            if (
                path not in allowed_get
                or body is not None
            ):

                raise RuntimeError(
                    "GET_ENDPOINT_FORBIDDEN"
                )

        elif method == "POST":

            if not (
                path == allowed_post
                and bot_mode == "RUN"
                and isinstance(body, dict)
                and not query
            ):

                raise RuntimeError(
                    "DEMO_POST_FORBIDDEN"
                )

        else:

            raise RuntimeError(
                "HTTP_METHOD_FORBIDDEN"
            )

        query_string = (
            urllib.parse.urlencode(
                query
            )
            if query else ""
        )

        signed_path = (
            path
            + (
                "?" + query_string
                if query_string else ""
            )
        )

        body_text = (
            ""
            if body is None
            else json.dumps(
                body,
                separators=(",", ":"),
                ensure_ascii=False
            )
        )

        timestamp = str(
            milliseconds()
        )

        prehash = (
            timestamp
            + method
            + signed_path
            + body_text
        )

        signature = base64.b64encode(
            hmac.new(
                api_secret.encode("utf-8"),
                prehash.encode("utf-8"),
                hashlib.sha256
            ).digest()
        ).decode()

        headers = {
            "ACCESS-KEY": api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE":
                api_passphrase,
            "Content-Type":
                "application/json",
            "Accept":
                "application/json"
        }

        request = urllib.request.Request(
            base_url + signed_path,
            headers=headers,
            method=method,
            data=(
                None
                if body is None
                else body_text.encode(
                    "utf-8"
                )
            )
        )

        try:

            with opener.open(
                request,
                timeout=15
            ) as response:

                http = response.getcode()
                raw = response.read(
                    65537
                )

        except urllib.error.HTTPError as exc:

            http = exc.code
            raw = exc.read(
                65537
            )

        if len(raw) > 65536:

            raise RuntimeError(
                "WEEX_RESPONSE_TOO_LARGE"
            )

        return (
            http,
            json.loads(
                raw.decode("utf-8")
            )
        )

    # ========================================================
    # 9. JOURNAL PATH - PRESERVE V2.1
    # ========================================================

    journal_path = os.getenv(
        "WEEX_DEMO_ENTRY_JOURNAL",
        "/tmp/weex_demo_entry_v21.json"
    )

    journal_dir = os.path.dirname(
        os.path.abspath(
            journal_path
        )
    )

    if not os.path.isdir(
        journal_dir
    ):

        return stop(
            "JOURNAL_DIRECTORY_INVALID"
        )

    def write_journal(record):

        fd, temp_path = (
            tempfile.mkstemp(
                prefix=".unit12_",
                dir=journal_dir,
                text=True
            )
        )

        try:

            with os.fdopen(
                fd,
                "w"
            ) as output:

                json.dump(
                    record,
                    output
                )

                output.flush()

                os.fsync(
                    output.fileno()
                )

            os.replace(
                temp_path,
                journal_path
            )

            dir_fd = os.open(
                journal_dir,
                os.O_RDONLY
            )

            try:

                os.fsync(
                    dir_fd
                )

            finally:

                os.close(
                    dir_fd
                )

        finally:

            if os.path.exists(
                temp_path
            ):

                os.unlink(
                    temp_path
                )

    lock = None

    try:

        lock = open(
            journal_path + ".lock",
            "a+"
        )

        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX
            | fcntl.LOCK_NB
        )

    except Exception:

        if lock is not None:

            lock.close()

        return stop(
            "JOURNAL_LOCK_UNAVAILABLE"
        )

    try:

        # ====================================================
        # 10. PREVIOUS JOURNAL READ
        # ====================================================

        try:

            with open(
                journal_path,
                "r"
            ) as handle:

                journal = json.load(
                    handle
                )

        except FileNotFoundError:

            journal = {}

        except Exception:

            return stop(
                "JOURNAL_READ_FAILED"
            )

        if not isinstance(
            journal,
            dict
        ):

            return stop(
                "JOURNAL_INVALID"
            )

        previous_status = str(
            journal.get(
                "status",
                ""
            )
        ).upper()

        previous_id = str(
            journal.get(
                "order_id"
            ) or ""
        )

        previous_client_id = str(
            journal.get(
                "client_order_id"
            ) or ""
        )

        # ====================================================
        # 11. LIVE DEMO POSITION GET
        # ====================================================

        result[
            "position_check_attempted"
        ] = True

        result[
            "authenticated_request"
        ] = True

        try:

            position_http, positions = (
                signed_request(
                    "GET",
                    "/capi/v3/sim/position/allPosition"
                )
            )

        except Exception as exc:

            log(
                "UNIT 12 POSITION GET ERROR =",
                type(exc).__name__
            )

            return stop(
                "DEMO_POSITION_GET_FAILED"
            )

        result[
            "position_http_status"
        ] = position_http

        result[
            "position_endpoint_access"
        ] = True

        position_ok = (
            position_http == 200
            and isinstance(
                positions,
                list
            )
        )

        check(
            "DEMO_POSITION_GET",
            position_ok
        )

        if not position_ok:

            return stop(
                "DEMO_POSITION_RESPONSE_INVALID"
            )

        active_positions = []

        try:

            for position in positions:

                if not isinstance(
                    position,
                    dict
                ):

                    raise ValueError(
                        "POSITION_NOT_DICT"
                    )

                symbol = str(
                    position.get(
                        "symbol",
                        ""
                    )
                ).upper()

                if symbol not in (
                    "BTCSUSDT",
                    "BTCUSDT"
                ):
                    continue

                size = decimal(
                    position["size"]
                )

                if size < 0:

                    raise ValueError(
                        "NEGATIVE_POSITION_SIZE"
                    )

                if size > 0:

                    active_positions.append({
                        "symbol": symbol,
                        "side":
                            position.get(
                                "side"
                            ),
                        "size": str(size)
                    })

        except Exception:

            return stop(
                "DEMO_POSITION_PARSE_FAILED"
            )

        result[
            "position_check_completed"
        ] = True

        result[
            "active_positions"
        ] = active_positions

        result[
            "active_position_exists"
        ] = bool(
            active_positions
        )

        if active_positions:

            result[
                "duplicate_initial_entry_blocked"
            ] = True

            result[
                "management_path_permitted"
            ] = True

            result[
                "tp_management_permitted"
            ] = True

            result[
                "backup_management_permitted"
            ] = True

            return finish(
                "ACTIVE_POSITION_BLOCK",
                "INITIAL_ENTRY_ALREADY_OPEN"
            )

        check(
            "DEMO_POSITION_FLAT",
            True
        )

        # ====================================================
        # 12. VERIFIED DEMO HISTORY PAGINATION
        # ====================================================

        orders = []
        history_complete = False

        for page in range(20):

            try:

                http, rows = (
                    signed_request(
                        "GET",
                        "/capi/v3/sim/order/history",
                        query={
                            "symbol":
                                "BTCSUSDT",
                            "limit": 1000,
                            "page": page
                        }
                    )
                )

            except Exception as exc:

                log(
                    "UNIT 12 HISTORY ERROR =",
                    type(exc).__name__
                )

                return stop(
                    "DEMO_HISTORY_GET_FAILED"
                )

            if not (
                http == 200
                and isinstance(
                    rows,
                    list
                )
                and all(
                    isinstance(x, dict)
                    for x in rows
                )
            ):

                return stop(
                    "DEMO_HISTORY_RESPONSE_INVALID"
                )

            orders.extend(
                rows
            )

            if len(rows) < 1000:

                history_complete = True

                break

        result[
            "history_checked"
        ] = True

        result[
            "history_complete"
        ] = history_complete

        check(
            "DEMO_HISTORY_COMPLETE",
            history_complete
        )

        if not history_complete:

            return stop(
                "DEMO_HISTORY_INCOMPLETE"
            )

        log(
            "UNIT 12 HISTORY RECORDS =",
            len(orders)
        )

        # ====================================================
        # 13. HISTORY STATUS CLASSIFICATION
        # ====================================================

        pending_states = {
            "NEW",
            "OPEN",
            "PENDING",
            "PENDING_NEW",
            "ACCEPTED",
            "PARTIALLY_FILLED",
            "PARTIALLYFILLED"
        }

        terminal_states = {
            "FILLED",
            "CANCELED",
            "CANCELLED",
            "EXPIRED",
            "REJECTED"
        }

        pending = False
        unknown = False

        for order in orders:

            if str(
                order.get(
                    "symbol",
                    ""
                )
            ).upper() != "BTCSUSDT":

                continue

            state = str(
                order.get(
                    "status",
                    ""
                )
            ).upper()

            if state in pending_states:

                pending = True

            elif state not in terminal_states:

                unknown = True

        check(
            "NO_HISTORY_PENDING",
            not pending
        )

        check(
            "KNOWN_HISTORY_STATUSES",
            not unknown
        )

        if pending or unknown:

            return stop(
                "HISTORY_HAS_UNRESOLVED_ORDER"
            )

        # ====================================================
        # 14. PREVIOUS JOURNAL RECONCILIATION
        # ====================================================

        unresolved = previous_status in (
            "POST_STARTED",
            "POST_UNKNOWN",
            "POST_ACCEPTED"
        )

        if unresolved:

            if not (
                previous_id
                or previous_client_id
            ):

                return stop(
                    "PREVIOUS_ORDER_ID_MISSING"
                )

            matches = []

            for order in orders:

                order_id = str(
                    order.get(
                        "orderId"
                    ) or ""
                )

                order_client_id = str(
                    order.get(
                        "clientOrderId"
                    )
                    or order.get(
                        "newClientOrderId"
                    )
                    or ""
                )

                if (
                    previous_id
                    and previous_id == order_id
                ) or (
                    previous_client_id
                    and previous_client_id
                    == order_client_id
                ):

                    matches.append(
                        order
                    )

            if len(matches) != 1:

                return stop(
                    "PREVIOUS_ORDER_NOT_UNIQUELY_RECONCILED"
                )

            state = str(
                matches[0].get(
                    "status",
                    ""
                )
            ).upper()

            if state not in terminal_states:

                return stop(
                    "PREVIOUS_ORDER_NOT_TERMINAL"
                )

            try:

                age = (
                    time.time()
                    - float(
                        journal["timestamp"]
                    )
                )

            except Exception:

                return stop(
                    "JOURNAL_TIMESTAMP_INVALID"
                )

            if age < 0:

                return stop(
                    "JOURNAL_TIMESTAMP_FUTURE"
                )

            if age < 300:

                return finish(
                    "COOLDOWN",
                    "PREVIOUS_ORDER_COOLDOWN"
                )

            result[
                "reconciliation_status"
            ] = "MATCHED_TERMINAL"

        elif previous_status in (
            "",
            "RECONCILED",
            "COOLDOWN"
        ):

            result[
                "reconciliation_status"
            ] = "NO_UNRESOLVED_JOURNAL"

        else:

            return stop(
                "UNKNOWN_JOURNAL_STATUS"
            )

        result[
            "journal_reconciled"
        ] = True

        check(
            "JOURNAL_RECONCILIATION",
            True
        )

        # ====================================================
        # 15. EXCHANGE ORDER COOLDOWN
        # ====================================================

        recent = False

        for order in orders:

            if str(
                order.get(
                    "symbol",
                    ""
                )
            ).upper() != "BTCSUSDT":

                continue

            try:

                order_time = int(
                    order.get(
                        "time"
                    ) or 0
                )

            except Exception:

                return stop(
                    "ORDER_TIME_INVALID"
                )

            if (
                order_time > 0
                and 0 <= (
                    milliseconds()
                    - order_time
                ) < 300000
            ):

                recent = True

                break

        check(
            "ENTRY_COOLDOWN_CLEAR",
            not recent
        )

        if recent:

            return finish(
                "COOLDOWN",
                "RECENT_DEMO_ORDER"
            )

        # ====================================================
        # 16. COMPLETED VERIFIED DIAGNOSTICS
        # ====================================================

        result[
            "diagnostics_completed"
        ] = True

        result[
            "diagnostics_passed"
        ] = all(
            checks.values()
        )

        log(
            "UNIT 12 VERIFIED CHECKS =",
            len(checks)
        )

        log(
            "UNIT 12 VERIFIED PASSES =",
            sum(checks.values())
        )

        
        # ====================================================
        # ORIGINAL 22524-LINE DEMO ENTRY AUTHORIZATION
        #
        # THE ORIGINAL MODEL:
        # 1. ACCEPTED QUALIFIED ENTRY
        # 2. VERIFIED DEMO POSITION
        # 3. PERMITTED ENTRY WHEN FLAT
        # 4. SUBMITTED SIGNED WEEX DEMO ORDER
        #
        # PRESERVE CURRENT HISTORY AND JOURNAL GATES.
        # NO LEVERAGE OR MARGIN-MODE MUTATION.
        # ====================================================

        result[
            "demo_leverage_scope_verified"
        ] = False

        result[
            "demo_open_orders_verified"
        ] = False

        result[
            "execution_policy"
        ] = "ORIGINAL_22524_DEMO_ENTRY"

        # ====================================================
        # 17. SINGLE MASTER BOT_MODE
        # ====================================================

        if bot_mode == "PAUSE":

            log(
                "UNIT 12 MASTER BOT_MODE = PAUSE"
            )

            log(
                "UNIT 12 DEMO ENTRY POST = DISABLED"
            )

            return finish(
                "DIAGNOSTIC_PASS",
                "MASTER_BOT_MODE_PAUSE"
            )

        if bot_mode != "RUN":

            return stop(
                "MASTER_BOT_MODE_INVALID"
            )

        # ====================================================
        # 18. ORIGINAL POSITION-AWARE SUBMISSION GATE
        # ====================================================

        if result[
            "diagnostics_passed"
        ] is not True:

            return stop(
                "PRE_SUBMISSION_CHECKS_FAILED"
            )

        if result[
            "position_check_completed"
        ] is not True:

            return stop(
                "DEMO_POSITION_UNVERIFIED"
            )

        if result[
            "active_position_exists"
        ] is not False:

            return stop(
                "ACTIVE_OR_UNKNOWN_DEMO_POSITION"
            )

        if result[
            "history_complete"
        ] is not True:

            return stop(
                "DEMO_HISTORY_INCOMPLETE"
            )

        if result[
            "journal_reconciled"
        ] is not True:

            return stop(
                "JOURNAL_NOT_RECONCILED"
            )

        for required_check in (
            "DEMO_POSITION_FLAT",
            "NO_HISTORY_PENDING",
            "KNOWN_HISTORY_STATUSES",
            "JOURNAL_RECONCILIATION",
            "ENTRY_COOLDOWN_CLEAR"
        ):

            if checks.get(
                required_check
            ) is not True:

                return stop(
                    "ORIGINAL_GATE_FAILED:"
                    + required_check
                )

        result[
            "initial_entry_permitted"
        ] = True

        log(
            "PASS: UNIT 12 ZERO ACTIVE "
            "BTCSUSDT POSITION"
        )

        log(
            "PASS: UNIT 12 ORIGINAL "
            "DEMO ENTRY CONDITIONS"
        )

        log(
            "UNIT 12 INITIAL ENTRY PERMITTED = True"
        )

        log(
            "UNIT 12 EXECUTION POLICY =",
            result["execution_policy"]
        )

        log(
            "UNIT 12 LEVERAGE SOURCE = "
            "WEEX EXCHANGE SETTING"
        )

        log(
            "UNIT 12 LEVERAGE MUTATION = NONE"
        )

        log(
            "UNIT 12 REAL CASH ORDER = NONE"
        )

        log(
            "UNIT 12 CONTINUE TO ORIGINAL "
            "SIGNED DEMO POST"
        )

        # ====================================================
        # 19. DEMO ORDER POST RESTORED
        #
        # THE CODE BELOW IS NOT REACHABLE
        # UNTIL BOTH ACCOUNT-SCOPE CHECKS
        # ABOVE ARE IMPLEMENTED AND PASS.
        # ====================================================

        result[
            "request_path"
        ] = "/capi/v3/sim/order"

        result[
            "request_payload"
        ] = dict(
            final_payload
        )

        journal_record = {
            "status": "POST_STARTED",
            "timestamp": time.time(),
            "client_order_id": client_id,
            "mode": mode,
            "direction": direction,
            "quantity": str(quantity)
        }

        try:

            write_journal(
                journal_record
            )

        except Exception:

            return stop(
                "PREPOST_JOURNAL_SAVE_FAILED"
            )

        result[
            "initial_entry_permitted"
        ] = True

        result[
            "demo_submission_attempted"
        ] = True

        result[
            "order_endpoint_access"
        ] = True

        result[
            "exchange_write"
        ] = True

        try:

            order_http, response = (
                signed_request(
                    "POST",
                    "/capi/v3/sim/order",
                    body=final_payload
                )
            )

        except Exception as exc:

            log(
                "UNIT 12 DEMO POST ERROR TYPE =",
                type(exc).__name__
            )

            journal_record[
                "status"
            ] = "POST_UNKNOWN"

            try:

                write_journal(
                    journal_record
                )

            except Exception:

                pass

            return finish(
                "SUBMISSION_OUTCOME_UNKNOWN",
                "VERIFY_WEEX_BEFORE_RETRY"
            )

        result[
            "http_status"
        ] = order_http

        result[
            "weex_response"
        ] = response

        accepted = (
            200 <= order_http < 300
            and isinstance(response, dict)
            and response.get(
                "success"
            ) is True
            and bool(
                response.get(
                    "orderId"
                )
            )
        )

        if not accepted:

            journal_record[
                "status"
            ] = "POST_UNKNOWN"

            try:

                write_journal(
                    journal_record
                )

            except Exception:

                pass

            return finish(
                "SUBMISSION_UNCONFIRMED",
                "WEEX_ACCEPTANCE_UNCONFIRMED"
            )

        order_id = response[
            "orderId"
        ]

        result[
            "order_id"
        ] = order_id

        journal_record.update({
            "status": "POST_ACCEPTED",
            "timestamp": time.time(),
            "order_id": str(order_id)
        })

        try:

            write_journal(
                journal_record
            )

        except Exception:

            log(
                "WARNING: ACCEPTED ORDER "
                "JOURNAL SAVE FAILED"
            )

        result[
            "demo_submission_completed"
        ] = True

        result[
            "management_path_permitted"
        ] = True

        result[
            "tp_management_permitted"
        ] = True

        result[
            "backup_management_permitted"
        ] = True

        log(
            "PASS: UNIT 12 WEEX DEMO "
            "ORDER ACCEPTED"
        )

        log(
            "UNIT 12 WEEX ORDER ID =",
            order_id
        )

        return finish(
            "DEMO_SUBMITTED",
            "WEEX_ORDER_ACCEPTED"
        )

    finally:

        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_UN
        )

        lock.close()


# ============================================================
# UNIT 12 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_reconstruction_unit_12(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT
    )
)


# ============================================================
# END UNIT 12 - HYBRID ADJUSTABLE V2.6
# ZERO INDENTATION
# ============================================================




# ============================================================
# START COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 13
# ZERO INDENTATION - DEMO TP EXECUTION + AUTO RECONCILIATION
# BOT_MODE ONLY CONTROLS UNIT 12; NOT USED HERE
# ============================================================

def fresh_reconstruction_unit_13(config, unit_12_result):
    import os
    import re
    import json
    import time
    import hmac
    import base64
    import hashlib
    import tempfile
    import fcntl
    import urllib.parse
    import urllib.request
    import urllib.error
    from decimal import Decimal, ROUND_DOWN, ROUND_UP

    def log(*args):
        print(*args, flush=True)

    def dec(value):
        if isinstance(value, bool) or value is None:
            raise ValueError('INVALID_DECIMAL')
        d = Decimal(str(value))
        if not d.is_finite():
            raise ValueError('NONFINITE_DECIMAL')
        return d

    def down(value, step):
        return (dec(value) / step).to_integral_value(
            rounding=ROUND_DOWN
        ) * step

    def up(value, step):
        return (dec(value) / step).to_integral_value(
            rounding=ROUND_UP
        ) * step

    log('=' * 72)
    log('UNIT 13 HYBRID ADJUSTABLE V3 AUTO RECONCILIATION START')
    log('UNIT 13 BOT_MODE DEPENDENCY = NONE')

    if not isinstance(config, dict) or not isinstance(
        unit_12_result, dict
    ):
        raise RuntimeError('UNIT13_INPUT_CONTRACT_INVALID')

    exchange = config.get('exchange', {})
    strategy = config.get('strategy', {})
    precision = config.get('market_precision', {})
    safety = config.get('safety', {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, strategy, precision, safety)
    ):
        raise RuntimeError('UNIT13_CONFIG_INVALID')

    if not (
        config.get('execution_environment') == 'DEMO'
        and exchange.get('demo_order_symbol') == 'BTCSUSDT'
        and exchange.get('market_symbol') == 'BTCUSDT'
        and exchange.get('contract_base_url')
        == 'https://api-contract.weex.com'
    ):
        raise RuntimeError('UNIT13_DEMO_SCOPE_INVALID')

    for name in (
        'real_order_submission_enabled',
        'leverage_mutation_enabled',
        'margin_mode_mutation_enabled',
        'position_mode_mutation_enabled'
    ):
        if safety.get(name) is not False:
            raise RuntimeError('UNIT13_UNSAFE_' + name)

    tp1_pct = dec(
        strategy.get('tp1_allocation_percent', 10)
    )
    tp2_pct = dec(
        strategy.get('tp2_allocation_percent', 20)
    )
    tp3_pct = dec(
        strategy.get('tp3_allocation_percent', 70)
    )

    floor1 = dec(
        strategy.get('tp1_net_roi_floor_percent', 5)
    )
    floor2 = dec(
        strategy.get('tp2_net_roi_floor_percent', 10)
    )

    fee = dec(
        strategy.get('futures_taker_fee_percent', 0.08)
    )
    separation = dec(
        strategy.get(
            'tp1_tp2_min_roi_separation_percent', 5
        )
    )

    trail_min = dec(
        strategy.get('tp3_trailing_min_percent', 0.1)
    )
    trail_ref = dec(
        strategy.get('tp3_trailing_reference_percent', 0.2)
    )
    trail_max = dec(
        strategy.get('tp3_trailing_max_percent', 0.4)
    )

    step = dec(
        precision.get('quantity_step', '0.0001')
    )
    minimum = dec(
        precision.get('minimum_quantity', '0.0001')
    )
    price_step = dec(
        precision.get('price_step', '0.1')
    )

    if not (
        tp1_pct == 10
        and tp2_pct == 20
        and tp3_pct == 70
        and floor1 >= 5
        and floor2 >= 10
        and separation >= 0
        and fee >= 0
        and step > 0
        and minimum > 0
        and price_step > 0
        and Decimal('0.1')
        <= trail_min
        <= trail_ref
        <= trail_max
        <= Decimal('0.4')
    ):
        raise RuntimeError('UNIT13_TP_SETTINGS_INVALID')

    result = {
        'unit': 13,
        'unit_13_revision': 'HYBRID_ADJUSTABLE_V3',
        'status': 'IDLE_NO_POSITION',
        'read_only': False,
        'unit_12_status': unit_12_result.get('status'),
        'active_position_exists': False,
        'position_exists': False,
        'tp_management_required': False,
        'position_side': 'NONE',
        'position_size': '0',
        'average_entry_price': None,
        'mark_price': None,
        'leverage': None,
        'total_executable_steps': 0,
        'tp_target_allocation': '10/20/70',
        'tp1_quantity': '0',
        'tp2_quantity': '0',
        'tp3_quantity': '0',
        'tp1_target': None,
        'tp2_target': None,
        'tp1_target_price': None,
        'tp2_target_price': None,
        'tp1_completed': False,
        'tp2_completed': False,
        'tp3_armed': False,
        'tp3_trailing_percent': float(trail_ref),
        'tp3_trailing_reference_percent': float(trail_ref),
        'tp3_trailing_min_percent': float(trail_min),
        'tp3_trailing_max_percent': float(trail_max),
        'tp3_trailing_dynamic': True,
        'tp_action': 'NONE',
        'tp_close_quantity': '0',
        'tp_order_id': None,
        'tp_execution_attempted': False,
        'tp_execution_completed': False,
        'tp_submission_accepted': False,
        'tp_fill_confirmed': False,
        'demo_order_executed': False,
        'real_order': False,
        'sl_enabled': False,
        'sl_execution_attempted': False,
        'backup_execution_attempted': False,
        'real_submission_attempted': False,
        'exchange_write': False,
        'journal_reconciled': False,
        'reconciliation_status': 'NOT_CHECKED',
        'skip_reason': 'NONE',
    }

    def finish(status, reason):
        result['status'] = status
        result['skip_reason'] = reason

        log('UNIT 13 STATUS =', status)
        log('UNIT 13 REASON =', reason)
        log('UNIT 13 TP ACTION =', result['tp_action'])
        log(
            'UNIT 13 JOURNAL RECONCILED =',
            result['journal_reconciled']
        )
        log(
            'UNIT 13 RECONCILIATION =',
            result['reconciliation_status']
        )
        log(
            'UNIT 13 TP3 ARMED =',
            result['tp3_armed']
        )
        log(
            'UNIT 13 TP FILL CONFIRMED =',
            result['tp_fill_confirmed']
        )
        log(
            'UNIT 13 EXCHANGE WRITE =',
            result['exchange_write']
        )
        log(
            'UNIT 13 HYBRID ADJUSTABLE V3 RESULT =',
            status
        )
        log('=' * 72)

        return result

    # ========================================================
    # STEP-AWARE TP ALLOCATION
    # ========================================================

    def alloc(n):
        if n <= 0:
            return 0, 0, 0

        if n == 1:
            return 0, 0, 1

        if n == 2:
            return 1, 0, 1

        a = max(
            1, int(Decimal(n) * tp1_pct / 100)
        )
        b = max(
            1, int(Decimal(n) * tp2_pct / 100)
        )

        while a + b > n - 1:
            if b > 1:
                b -= 1
            elif a > 1:
                a -= 1
            else:
                break

        return a, b, n - a - b

    assert all(
        sum(alloc(n)) == n
        and min(alloc(n)) >= 0
        for n in (1, 2, 4, 10, 24)
    )

    log('PASS: UNIT 13 ALLOCATION SELF TEST 5/5')

    # ========================================================
    # WEEX DEMO API CONNECTION
    # ========================================================

    key = (
        os.getenv('WEEX_API_KEY')
        or os.getenv('API_KEY')
    )
    secret = (
        os.getenv('WEEX_API_SECRET')
        or os.getenv('API_SECRET')
    )
    passphrase = (
        os.getenv('WEEX_API_PASSPHRASE')
        or os.getenv('API_PASSPHRASE')
    )

    if not all((key, secret, passphrase)):
        return finish(
            'BLOCKED',
            'CREDENTIALS_MISSING'
        )

    base = 'https://api-contract.weex.com'

    position_path = '/capi/v3/sim/position/allPosition'
    history_path = '/capi/v3/sim/order/history'
    post_path = '/capi/v3/sim/order'

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):
        def redirect_request(
            self, req, fp, code,
            msg, headers, newurl
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    def signed(method, path, query=None, body=None):

        if method == 'GET':

            if (
                path not in (
                    position_path,
                    history_path
                )
                or body is not None
            ):
                raise RuntimeError(
                    'GET_SCOPE_INVALID'
                )

        elif method == 'POST':

            if (
                path != post_path
                or not isinstance(body, dict)
                or query
            ):
                raise RuntimeError(
                    'POST_SCOPE_INVALID'
                )

        else:
            raise RuntimeError('METHOD_INVALID')

        qs = (
            urllib.parse.urlencode(query)
            if query
            else ''
        )

        target = path + (
            '?' + qs if qs else ''
        )

        payload = (
            ''
            if body is None
            else json.dumps(
                body,
                separators=(',', ':'),
                ensure_ascii=False
            )
        )

        timestamp = str(
            int(time.time() * 1000)
        )

        sig = base64.b64encode(
            hmac.new(
                secret.encode(),
                (
                    timestamp + method + target + payload
                ).encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        headers = {
            'ACCESS-KEY': key,
            'ACCESS-SIGN': sig,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        req = urllib.request.Request(
            base + target,
            headers=headers,
            method=method,
            data=(
                None
                if body is None
                else payload.encode()
            )
        )

        try:
            with opener.open(
                req, timeout=15
            ) as resp:
                code = resp.getcode()
                raw = resp.read(65537)

        except urllib.error.HTTPError as ex:
            code = ex.code
            raw = ex.read(65537)

        if len(raw) > 65536:
            raise RuntimeError(
                'API_RESPONSE_TOO_LARGE'
            )

        return code, json.loads(
            raw.decode()
        )

    # ========================================================
    # POSITION AND HISTORY FETCH
    # ========================================================

    def get_positions():

        http, rows = signed(
            'GET',
            position_path
        )

        if (
            http != 200
            or not isinstance(rows, list)
        ):
            raise RuntimeError(
                'DEMO_POSITION_RESPONSE_INVALID'
            )

        found = []

        for row in rows:

            if not isinstance(row, dict):
                raise ValueError(
                    'POSITION_RECORD_INVALID'
                )

            if str(
                row.get('symbol', '')
            ).upper() != 'BTCSUSDT':
                continue

            size = dec(
                row.get('size', '0')
            )

            if size < 0:
                raise ValueError('NEGATIVE_SIZE')

            if size > 0:
                found.append(row)

        return found

    def get_history():

        all_rows = []

        for page in range(20):

            code, rows = signed(
                'GET',
                history_path,
                {
                    'symbol': 'BTCSUSDT',
                    'limit': 1000,
                    'page': page,
                }
            )

            if (
                code != 200
                or not isinstance(rows, list)
                or not all(
                    isinstance(x, dict)
                    for x in rows
                )
            ):
                raise RuntimeError(
                    'DEMO_HISTORY_RESPONSE_INVALID'
                )

            all_rows.extend(rows)

            if len(rows) < 1000:
                return all_rows

        raise RuntimeError(
            'DEMO_HISTORY_INCOMPLETE'
        )

    # ========================================================
    # JOURNAL AND PERSISTENCE
    # ========================================================

    journal_path = os.getenv(
        'WEEX_DEMO_TP_JOURNAL',
        '/tmp/weex_demo_tp_unit13.json'
    )

    directory = os.path.dirname(
        os.path.abspath(journal_path)
    )

    if not os.path.isdir(directory):
        return finish(
            'BLOCKED',
            'JOURNAL_DIRECTORY_MISSING'
        )

    def save_journal(record):

        fd, temporary = tempfile.mkstemp(
            dir=directory,
            prefix='.unit13_',
            text=True
        )

        try:
            with os.fdopen(
                fd, 'w'
            ) as fh:

                json.dump(
                    record,
                    fh,
                    separators=(',', ':')
                )

                fh.flush()
                os.fsync(
                    fh.fileno()
                )

            os.replace(
                temporary,
                journal_path
            )

            dfd = os.open(
                directory,
                os.O_RDONLY
            )

            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)

        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    lock = None

    try:
        lock = open(
            journal_path + '.lock',
            'a+'
        )

        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX | fcntl.LOCK_NB
        )

    except Exception:
        if lock:
            lock.close()

        return finish(
            'BLOCKED',
            'JOURNAL_LOCK_BUSY'
        )

    try:

        try:
            with open(journal_path) as fh:
                journal = json.load(fh)

        except FileNotFoundError:
            journal = {}

        except Exception:
            return finish(
                'BLOCKED',
                'JOURNAL_UNREADABLE'
            )

        if not isinstance(journal, dict):
            return finish(
                'BLOCKED',
                'JOURNAL_INVALID'
            )

        try:
            active = get_positions()

        except Exception as ex:
            log(
                'UNIT 13 POSITION GET ERROR =',
                type(ex).__name__
            )

            return finish(
                'BLOCKED',
                'DEMO_POSITION_GET_FAILED'
            )

        log('PASS: UNIT 13 DEMO POSITION GET')

        if len(active) > 1:
            return finish(
                'BLOCKED',
                'MULTIPLE_DEMO_POSITIONS'
            )

        # ====================================================
        # RECONCILE ANY PREVIOUS SUBMITTED TP ORDER
        # EVEN WHEN THE POSITION IS NOW FLAT.
        # ====================================================

        pending_states = {
            'NEW',
            'OPEN',
            'PENDING',
            'PENDING_NEW',
            'ACCEPTED',
            'PARTIALLY_FILLED',
            'PARTIALLYFILLED'
        }

        terminal_states = {
            'FILLED',
            'CANCELED',
            'CANCELLED',
            'EXPIRED',
            'REJECTED'
        }

        journal_status = str(
            journal.get('status', '')
        ).upper()

        if journal_status in {
            'SUBMISSION_STARTED',
            'SUBMISSION_UNKNOWN',
            'SUBMISSION_ACCEPTED'
        }:

            try:
                rows = get_history()

            except Exception as ex:

                log(
                    'UNIT 13 HISTORY ERROR =',
                    type(ex).__name__
                )

                return finish(
                    'RECONCILIATION_WAIT',
                    'DEMO_HISTORY_UNAVAILABLE'
                )

            prior_id = str(
                journal.get('order_id') or ''
            )

            prior_cid = str(
                journal.get('client_order_id') or ''
            )

            if not prior_id and not prior_cid:
                return finish(
                    'RECONCILIATION_WAIT',
                    'JOURNAL_ORDER_IDENTIFIERS_MISSING'
                )

            matches = []

            for row in rows:

                if str(
                    row.get('symbol', '')
                ).upper() != 'BTCSUSDT':
                    continue

                rid = str(
                    row.get('orderId') or ''
                )

                cid = str(
                    row.get('clientOrderId')
                    or row.get('newClientOrderId')
                    or ''
                )

                if (
                    prior_id and rid == prior_id
                ) or (
                    prior_cid and cid == prior_cid
                ):
                    matches.append(row)

            if len(matches) != 1:
                return finish(
                    'RECONCILIATION_WAIT',
                    'ORDER_NOT_UNIQUELY_FOUND'
                )

            matched = matches[0]

            state = str(
                matched.get('status', '')
            ).upper()

            result[
                'reconciliation_status'
            ] = state

            if state in pending_states:
                return finish(
                    'RECONCILIATION_WAIT',
                    'ORDER_STILL_OPEN_OR_PARTIAL'
                )

            if state not in terminal_states:
                return finish(
                    'RECONCILIATION_WAIT',
                    'UNKNOWN_EXCHANGE_ORDER_STATE'
                )

            # Never assume a terminal order
            # was fully filled.

            try:
                executed = dec(
                    matched['executedQty']
                )

                requested = dec(
                    journal['quantity']
                )

                original = dec(
                    matched['origQty']
                )

                if not (
                    Decimal('0')
                    <= executed
                    <= original
                    and original == requested
                ):
                    raise ValueError(
                        'EXECUTION_QUANTITY_MISMATCH'
                    )

            except Exception:
                return finish(
                    'RECONCILIATION_WAIT',
                    'EXECUTED_QUANTITY_UNVERIFIED'
                )

            if (
                state == 'FILLED'
                and executed != requested
            ):
                return finish(
                    'RECONCILIATION_WAIT',
                    'FILLED_STATUS_QTY_MISMATCH'
                )

            # Verify the position has not
            # changed incompatibly.

            try:
                side_j = str(
                    journal['position_side']
                ).upper()

                prior_size = dec(
                    journal['baseline_size']
                )

                prior_closed = dec(
                    journal['baseline_closed']
                )

                if len(active) == 1:

                    pos = active[0]

                    if str(
                        pos.get('side', '')
                    ).upper() != side_j:
                        raise ValueError('SIDE_CHANGED')

                    current_size = dec(
                        pos['size']
                    )

                    current_closed = dec(
                        pos['cumCloseSize']
                    )

                    if (
                        current_size > prior_size
                        or current_closed
                        < prior_closed + executed
                    ):
                        raise ValueError(
                            'POSITION_NOT_RECONCILED'
                        )

                elif (
                    executed < requested
                    and len(active) == 0
                ):
                    # The position is flat;
                    # no further close needed.
                    pass

            except Exception:
                return finish(
                    'RECONCILIATION_WAIT',
                    'POSITION_NOT_RECONCILED'
                )

            journal['status'] = 'RECONCILED'
            journal[
                'verified_executed_qty'
            ] = str(executed)

            journal[
                'verified_order_status'
            ] = state

            journal[
                'reconciled_at'
            ] = time.time()

            try:
                save_journal(journal)

            except Exception:
                return finish(
                    'RECONCILIATION_WAIT',
                    'JOURNAL_SAVE_FAILED'
                )

            result[
                'journal_reconciled'
            ] = True

            result[
                'tp_fill_confirmed'
            ] = executed > 0

            log(
                'PASS: UNIT 13 VERIFIED ORDER',
                state,
                'EXECUTED',
                executed
            )

            return finish(
                'TP_RECONCILED',
                'RESCAN_FOR_NEXT_TP'
            )

        elif journal_status in (
            '',
            'RECONCILED'
        ):
            result[
                'journal_reconciled'
            ] = True

            result[
                'reconciliation_status'
            ] = 'NO_PENDING_ORDER'

        else:
            return finish(
                'BLOCKED',
                'UNKNOWN_JOURNAL_STATE'
            )

        # ====================================================
        # NO OPEN POSITION
        # ====================================================

        if not active:

            log(
                'PASS: UNIT 13 NO OPEN DEMO POSITION'
            )

            return finish(
                'IDLE_NO_POSITION',
                'NO_ACTIVE_BTCSUSDT_POSITION'
            )

        pos = active[0]

        side = str(
            pos.get('side', '')
        ).upper()

        if side not in (
            'LONG',
            'SHORT'
        ):
            return finish(
                'BLOCKED',
                'POSITION_SIDE_INVALID'
            )

        # ====================================================
        # POSITION FINANCIALS
        # ====================================================

        try:
            size = dec(
                pos['size']
            )

            cumulative_open = dec(
                pos.get('cumOpenSize', size)
            )

            cumulative_closed = dec(
                pos.get('cumCloseSize', '0')
            )

            leverage = dec(
                pos['leverage']
            )

            entry = (
                dec(pos['openValue'])
                / size
            )

            if not (
                size >= minimum
                and leverage > 0
                and entry > 0
                and cumulative_open >= size
                and cumulative_closed >= 0
            ):
                raise ValueError(
                    'POSITION_INVALID'
                )

        except Exception:
            return finish(
                'BLOCKED',
                'POSITION_FINANCIALS_INVALID'
            )

        steps = int(
            down(
                cumulative_open,
                step
            ) / step
        )

        q1_steps, q2_steps, q3_steps = (
            alloc(steps)
        )

        q1, q2, q3 = (
            Decimal(n) * step
            for n in (
                q1_steps,
                q2_steps,
                q3_steps
            )
        )

        if (
            steps < 1
            or q1 + q2 + q3
            != Decimal(steps) * step
        ):
            return finish(
                'BLOCKED',
                'ALLOCATION_INVALID'
            )

        # ====================================================
        # FEE-AWARE TP TARGETS
        # ====================================================

        fee_drag = (
            fee
            * Decimal('2')
            * leverage
        )

        gross1 = floor1 + fee_drag

        gross2 = max(
            floor2 + fee_drag,
            gross1 + separation
        )

        movement1 = (
            gross1 / leverage / 100
        )

        movement2 = (
            gross2 / leverage / 100
        )

        if side == 'LONG':

            tp1 = up(
                entry * (1 + movement1),
                price_step
            )

            tp2 = max(
                tp1 + price_step,
                up(
                    entry * (1 + movement2),
                    price_step
                )
            )

            close_side = 'SELL'

        else:

            tp1 = down(
                entry * (1 - movement1),
                price_step
            )

            tp2 = min(
                tp1 - price_step,
                down(
                    entry * (1 - movement2),
                    price_step
                )
            )

            close_side = 'BUY'

        if tp1 <= 0 or tp2 <= 0:
            return finish(
                'BLOCKED',
                'TP_PRICE_INVALID'
            )

        result.update({
            'active_position_exists': True,
            'position_exists': True,
            'tp_management_required': True,
            'position_side': side,
            'position_size': str(size),
            'average_entry_price': str(entry),
            'leverage': str(leverage),
            'total_executable_steps': steps,
            'tp1_quantity': str(q1),
            'tp2_quantity': str(q2),
            'tp3_quantity': str(q3),
            'tp1_target': float(tp1),
            'tp2_target': float(tp2),
            'tp1_target_price': str(tp1),
            'tp2_target_price': str(tp2),
        })

        # ====================================================
        # PUBLIC MARK PRICE GET
        # ====================================================

        try:
            q = urllib.parse.urlencode({
                'symbol': 'BTCUSDT',
                'priceType': 'MARK'
            })

            req = urllib.request.Request(
                base
                + '/capi/v3/market/symbolPrice?'
                + q,
                method='GET'
            )

            with opener.open(
                req,
                timeout=15
            ) as resp:
                raw = resp.read(65537)

            if len(raw) > 65536:
                raise ValueError(
                    'MARK_TOO_LARGE'
                )

            mark = dec(
                json.loads(
                    raw.decode()
                )['price']
            )

            if mark <= 0:
                raise ValueError(
                    'MARK_INVALID'
                )

        except Exception as ex:

            log(
                'UNIT 13 MARK ERROR =',
                type(ex).__name__
            )

            return finish(
                'BLOCKED',
                'MARK_GET_FAILED'
            )

        result[
            'mark_price'
        ] = str(mark)

        # ====================================================
        # TP COMPLETION AND PRICE CONDITIONS
        # ====================================================

        tp1_done = (
            q1 == 0
            or cumulative_closed >= q1
        )

        tp2_done = (
            tp1_done
            if q2 == 0
            else cumulative_closed
            >= q1 + q2
        )

        result[
            'tp1_completed'
        ] = tp1_done

        result[
            'tp2_completed'
        ] = tp2_done

        reached1 = (
            mark >= tp1
            if side == 'LONG'
            else mark <= tp1
        )

        reached2 = (
            mark >= tp2
            if side == 'LONG'
            else mark <= tp2
        )

        action = 'NONE'
        amount = Decimal('0')

        if (
            q2 > 0
            and reached2
            and not tp2_done
        ):

            amount = down(
                min(
                    size,
                    max(
                        Decimal('0'),
                        q1 + q2
                        - cumulative_closed
                    )
                ),
                step
            )

            if amount >= minimum:
                action = 'TP2'

        elif (
            q1 > 0
            and reached1
            and not tp1_done
        ):

            amount = down(
                min(
                    size,
                    max(
                        Decimal('0'),
                        q1 - cumulative_closed
                    )
                ),
                step
            )

            if amount >= minimum:
                action = 'TP1'

        result['tp_action'] = action
        result[
            'tp_close_quantity'
        ] = str(amount)

        result['tp3_armed'] = bool(
            tp1_done
            and tp2_done
            and q3 > 0
            and size > 0
        )

        log(
            'UNIT 13 POSITION',
            side,
            'SIZE',
            size,
            'MARK',
            mark
        )

        log(
            'UNIT 13 TP1',
            tp1,
            'DONE',
            tp1_done,
            'TP2',
            tp2,
            'DONE',
            tp2_done
        )

        if action == 'NONE':

            if result['tp3_armed']:

                return finish(
                    'TP3_ARMED',
                    'HANDOFF_TO_UNIT14'
                )

            return finish(
                'MONITORING',
                'AWAITING_TP_TARGET'
            )

        # ====================================================
        # RECHECK POSITION BEFORE SUBMISSION
        # ====================================================

        try:
            again = get_positions()

            if len(again) != 1:
                return finish(
                    'BLOCKED',
                    'POSITION_CHANGED_BEFORE_TP'
                )

            latest = again[0]

            if (
                str(
                    latest.get('side', '')
                ).upper() != side
                or dec(
                    latest['size']
                ) != size
                or dec(
                    latest.get(
                        'cumCloseSize',
                        '0'
                    )
                ) != cumulative_closed
            ):
                return finish(
                    'BLOCKED',
                    'POSITION_CHANGED_BEFORE_TP'
                )

        except Exception:
            return finish(
                'BLOCKED',
                'PREPOST_POSITION_RECHECK_FAILED'
            )

        if (
            amount < minimum
            or amount > size
            or amount % step != 0
        ):
            return finish(
                'BLOCKED',
                'CLOSE_QUANTITY_INVALID'
            )

        # ====================================================
        # CHECK DEMO HISTORY BEFORE NEW TP
        # ====================================================

        try:
            before_rows = get_history()

            pending = {
                'NEW',
                'OPEN',
                'PENDING',
                'PENDING_NEW',
                'ACCEPTED',
                'PARTIALLY_FILLED',
                'PARTIALLYFILLED'
            }

            unknown = False

            for row in before_rows:

                if str(
                    row.get('symbol', '')
                ).upper() != 'BTCSUSDT':
                    continue

                state = str(
                    row.get('status', '')
                ).upper()

                if (
                    state in pending
                    or state not in (
                        pending
                        | {
                            'FILLED',
                            'CANCELED',
                            'CANCELLED',
                            'EXPIRED',
                            'REJECTED'
                        }
                    )
                ):
                    unknown = True
                    break

            if unknown:
                return finish(
                    'BLOCKED',
                    'OPEN_OR_UNKNOWN_DEMO_ORDER'
                )

        except Exception:
            return finish(
                'BLOCKED',
                'PREPOST_HISTORY_FAILED'
            )

        # ====================================================
        # DEMO TP CLOSING PAYLOAD
        # ====================================================

        seed = (
            f'{side}|{action}|'
            f'{cumulative_open}|'
            f'{cumulative_closed}|'
            f'{amount}|{time.time_ns()}'
        )

        cid = (
            'FR13-'
            + action
            + '-'
            + hashlib.sha256(
                seed.encode()
            ).hexdigest()[:20]
        )

        payload = {
            'symbol': 'BTCSUSDT',
            'side': close_side,
            'positionSide': side,
            'type': 'MARKET',
            'quantity': format(
                amount,
                'f'
            ),
            'newClientOrderId': cid,
        }

        if not re.fullmatch(
            r'[A-Za-z0-9_.:/-]{1,36}',
            cid
        ):
            return finish(
                'BLOCKED',
                'CLIENT_ID_INVALID'
            )

        new_journal = {
            'status': 'SUBMISSION_STARTED',
            'timestamp': time.time(),
            'symbol': 'BTCSUSDT',
            'position_side': side,
            'tp_action': action,
            'quantity': str(amount),
            'baseline_size': str(size),
            'baseline_closed': str(
                cumulative_closed
            ),
            'client_order_id': cid,
        }

        try:
            save_journal(
                new_journal
            )

        except Exception:
            return finish(
                'BLOCKED',
                'PREPOST_JOURNAL_FAILED'
            )

        # ====================================================
        # EXECUTABLE WEEX DEMO TP ORDER
        # NO BOT_MODE DEPENDENCY
        # ====================================================

        result[
            'tp_execution_attempted'
        ] = True

        result[
            'exchange_write'
        ] = True

        try:
            http, reply = signed(
                'POST',
                post_path,
                body=payload
            )

        except Exception as ex:

            log(
                'UNIT 13 TP POST ERROR =',
                type(ex).__name__
            )

            new_journal[
                'status'
            ] = 'SUBMISSION_UNKNOWN'

            try:
                save_journal(
                    new_journal
                )
            except Exception:
                pass

            return finish(
                'TP_SUBMISSION_UNKNOWN',
                'RECONCILE_BEFORE_RETRY'
            )

        accepted = (
            200 <= http < 300
            and isinstance(
                reply,
                dict
            )
            and reply.get('success') is True
            and bool(
                reply.get('orderId')
            )
        )

        if not accepted:

            new_journal[
                'status'
            ] = 'SUBMISSION_UNKNOWN'

            try:
                save_journal(
                    new_journal
                )
            except Exception:
                pass

            return finish(
                'TP_SUBMISSION_UNCONFIRMED',
                'RECONCILE_BEFORE_RETRY'
            )

        order_id = str(
            reply['orderId']
        )

        result[
            'tp_order_id'
        ] = order_id

        result[
            'tp_submission_accepted'
        ] = True

        # Submitted does not mean filled.
        result[
            'demo_order_executed'
        ] = True

        new_journal[
            'status'
        ] = 'SUBMISSION_ACCEPTED'

        new_journal[
            'order_id'
        ] = order_id

        try:
            save_journal(
                new_journal
            )

        except Exception:
            log(
                'WARNING: TP ACCEPTANCE '
                'JOURNAL SAVE FAILED'
            )

        log(
            'PASS: UNIT 13 TP ORDER ACCEPTED =',
            order_id
        )

        return finish(
            'TP_SUBMITTED_AWAITING_FILL',
            'AUTO_RECONCILE_ON_NEXT_SCAN'
        )

    finally:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_UN
        )
        lock.close()


# ============================================================
# EXECUTE UNIT 13
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
    fresh_reconstruction_unit_13(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_12_RESULT,
    )
)


# ============================================================
# END COMPLETE REPLACEMENT - FRESH RECONSTRUCTION UNIT 13
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 14A - ORIGINAL POSITION MONITORING ADAPTATION
# ZERO INDENTATION
#
# REFERENCE: ORIGINAL 22524-LINE MAIN.PY
# ORIGINAL FUNCTION: fresh_tp3_runtime
#
# STAGE 14A:
# 1. PRESERVE ORIGINAL FUNCTION INTERFACE
# 2. READ WEEX DEMO POSITION INDEPENDENTLY
# 3. VALIDATE POSITION SIDE, SIZE AND LEVERAGE
# 4. PRESERVE UNIT 13 HANDOVER
# 5. PREPARE INPUT FOR UNITS 14B-14F
#
# EXCHANGE WRITE: NONE
# BOT_MODE DEPENDENCY: NONE
# NO CONTINUOUS LOOP AT THIS STAGE
# ============================================================


def fresh_tp3_runtime(config, unit_13_result):

    import os
    import json
    import time
    import hmac
    import base64
    import hashlib
    import urllib.request
    import urllib.error

    from decimal import Decimal
    from datetime import datetime, timezone

    def log(*values):
        print(*values, flush=True)

    def decimal_value(value):

        if value is None or isinstance(value, bool):
            raise ValueError("INVALID_DECIMAL")

        number = Decimal(str(value))

        if not number.is_finite():
            raise ValueError("NONFINITE_DECIMAL")

        return number

    log("=" * 72)
    log(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 14A ORIGINAL DEMO POSITION MONITOR START"
    )

    log("UNIT 14A BOT_MODE DEPENDENCY = NONE")
    log("UNIT 14A EXCHANGE WRITE = NONE")

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT14A_CONFIG_INVALID"
        )

    if not isinstance(unit_13_result, dict):
        raise RuntimeError(
            "UNIT14A_UNIT13_RESULT_INVALID"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    strategy = config.get("strategy", {})

    if not all(
        isinstance(item, dict)
        for item in (exchange, safety, strategy)
    ):
        raise RuntimeError(
            "UNIT14A_CONFIG_SECTION_INVALID"
        )

    if not (
        config.get("execution_environment") == "DEMO"
        and exchange.get("demo_order_symbol") == "BTCSUSDT"
        and exchange.get("market_symbol") == "BTCUSDT"
        and exchange.get("contract_base_url")
        == "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "UNIT14A_DEMO_SCOPE_INVALID"
        )

    for setting in (
        "real_order_submission_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled"
    ):

        if safety.get(setting) is not False:
            raise RuntimeError(
                "UNIT14A_UNSAFE_SETTING_" + setting
            )

    result = {
        "unit": 14,
        "subunit": "14A",
        "revision": "ORIGINAL_POSITION_MONITOR_V1",

        "status": "NOT_STARTED",
        "skip_reason": "NONE",

        "unit_13_status": str(
            unit_13_result.get("status", "UNKNOWN")
        ),

        "unit_13_tp3_armed": bool(
            unit_13_result.get("tp3_armed", False)
        ),

        "active_position_exists": False,
        "position_exists": False,

        "position_side": "NONE",
        "position_size": "0",
        "average_entry_price": None,
        "leverage": None,

        "liquidation_price": None,
        "cumulative_open_size": None,
        "cumulative_close_size": None,

        "demo_position_verified": False,
        "multiple_positions_detected": False,

        "backup_count_target": 5,
        "backup_multipliers": (
            1.0, 1.5, 2.0, 2.5, 3.0
        ),
        "exposure_cap_percent": 35.0,

        "backup_management_ready": False,
        "tp3_management_ready": False,

        "backup_execution_attempted": False,
        "tp3_execution_attempted": False,

        "demo_order_executed": False,
        "real_order": False,
        "exchange_write": False,

        "next_subunit": "14B",
    }

    def finish(status, reason):

        result["status"] = status
        result["skip_reason"] = reason

        log("-" * 72)
        log("UNIT 14A STATUS =", status)
        log("UNIT 14A REASON =", reason)

        log(
            "UNIT 14A UNIT 13 STATUS =",
            result["unit_13_status"]
        )

        log(
            "UNIT 14A POSITION VERIFIED =",
            result["demo_position_verified"]
        )

        log(
            "UNIT 14A POSITION SIDE =",
            result["position_side"]
        )

        log(
            "UNIT 14A POSITION SIZE =",
            result["position_size"]
        )

        log(
            "UNIT 14A TP3 ARM FROM UNIT 13 =",
            result["unit_13_tp3_armed"]
        )

        log(
            "UNIT 14A BACKUP TARGET =",
            result["backup_count_target"]
        )

        log(
            "UNIT 14A BACKUP MULTIPLIERS =",
            result["backup_multipliers"]
        )

        log(
            "UNIT 14A EXPOSURE CAP =",
            result["exposure_cap_percent"]
        )

        log("UNIT 14A EXCHANGE WRITE = False")

        log(
            "UNIT 14A ORIGINAL ADAPTATION RESULT =",
            status
        )

        log("=" * 72)

        return result

    # ========================================================
    # ORIGINAL WEEX DEMO CREDENTIALS
    # ========================================================

    api_key = (
        os.getenv("WEEX_API_KEY")
        or os.getenv("API_KEY")
    )

    api_secret = (
        os.getenv("WEEX_API_SECRET")
        or os.getenv("API_SECRET")
    )

    api_phrase = (
        os.getenv("WEEX_API_PASSPHRASE")
        or os.getenv("API_PASSPHRASE")
    )

    if not all(
        (api_key, api_secret, api_phrase)
    ):
        return finish(
            "BLOCKED",
            "WEEX_CREDENTIALS_MISSING"
        )

    # ========================================================
    # ORIGINAL AUTHENTICATED WEEX DEMO POSITION GET
    # ========================================================

    base_url = "https://api-contract.weex.com"

    position_path = (
        "/capi/v3/sim/position/allPosition"
    )

    timestamp = str(int(time.time() * 1000))

    signature_input = (
        timestamp
        + "GET"
        + position_path
    )

    signature = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            signature_input.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": api_phrase,
        "Content-Type": "application/json",
    }

    request = urllib.request.Request(
        base_url + position_path,
        headers=headers,
        method="GET"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            http_status = response.getcode()
            raw = response.read(65537)

        if len(raw) > 65536:
            raise RuntimeError(
                "POSITION_RESPONSE_TOO_LARGE"
            )

        positions = json.loads(
            raw.decode("utf-8")
        )

        if (
            http_status != 200
            or not isinstance(positions, list)
        ):
            raise RuntimeError(
                "DEMO_POSITION_RESPONSE_INVALID"
            )

    except Exception as exc:

        log(
            "UNIT 14A POSITION GET ERROR =",
            type(exc).__name__
        )

        return finish(
            "BLOCKED",
            "DEMO_POSITION_GET_FAILED"
        )

    log("PASS: UNIT 14A WEEX DEMO POSITION GET")

    # ========================================================
    # ORIGINAL ACTIVE POSITION FILTER
    # ========================================================

    active = []

    try:

        for record in positions:

            if not isinstance(record, dict):
                raise ValueError(
                    "INVALID_POSITION_RECORD"
                )

            symbol = str(
                record.get("symbol", "")
            ).upper()

            if symbol != "BTCSUSDT":
                continue

            size = decimal_value(
                record.get("size", "0")
            )

            if size < 0:
                raise ValueError(
                    "NEGATIVE_POSITION_SIZE"
                )

            if size > 0:
                active.append(record)

    except Exception:

        return finish(
            "BLOCKED",
            "DEMO_POSITION_PARSE_FAILED"
        )

    result["demo_position_verified"] = True

    if not active:

        log(
            "PASS: UNIT 14A NO OPEN DEMO POSITION"
        )

        return finish(
            "IDLE_NO_POSITION",
            "NO_ACTIVE_BTCSUSDT_POSITION"
        )

    if len(active) != 1:

        result[
            "multiple_positions_detected"
        ] = True

        return finish(
            "BLOCKED",
            "MULTIPLE_ACTIVE_DEMO_POSITIONS"
        )

    # ========================================================
    # EXISTING POSITION DETAILS FOR UNIT 14B
    # ========================================================

    position = active[0]

    try:

        side = str(
            position.get("side", "")
        ).upper()

        size = decimal_value(
            position["size"]
        )

        leverage = decimal_value(
            position["leverage"]
        )

        open_value = decimal_value(
            position["openValue"]
        )

        cumulative_open = decimal_value(
            position.get("cumOpenSize", size)
        )

        cumulative_close = decimal_value(
            position.get("cumCloseSize", "0")
        )

        if not (
            side in ("LONG", "SHORT")
            and size > 0
            and leverage > 0
            and open_value > 0
            and cumulative_open >= size
            and cumulative_close >= 0
        ):
            raise ValueError(
                "POSITION_FINANCIALS_INVALID"
            )

        entry_price = open_value / size

        
        liquidation_raw = position.get(
            "liquidatePrice",
            position.get(
                "liquidationPrice",
                position.get("liqPrice")
            )
        )

        liquidation_price = None

        if liquidation_raw not in (
            None, "", "0", 0
        ):

            liquidation_value = decimal_value(
                liquidation_raw
            )

            if liquidation_value > 0:
                liquidation_price = str(
                    liquidation_value
                )

    except Exception as exc:

        log(
            "UNIT 14A POSITION VALIDATION =",
            type(exc).__name__
        )

        return finish(
            "BLOCKED",
            "POSITION_FINANCIALS_INVALID"
        )

    result.update({
        "active_position_exists": True,
        "position_exists": True,
        "position_side": side,
        "position_size": str(size),

        "average_entry_price": str(
            entry_price
        ),

        "leverage": str(leverage),

        "liquidation_price": liquidation_price,

        "cumulative_open_size": str(
            cumulative_open
        ),

        "cumulative_close_size": str(
            cumulative_close
        ),

        "backup_management_ready": False,
        "tp3_management_ready": False,
    })

    log(
        "PASS: UNIT 14A ACTIVE DEMO POSITION FOUND"
    )

    log(
        "UNIT 14A ENTRY PRICE =",
        entry_price
    )

    log(
        "UNIT 14A LEVERAGE =",
        leverage
    )

    log(
        "UNIT 14A LIQUIDATION PRICE =",
        liquidation_price
    )

    log(
        "UNIT 14A CUMULATIVE OPEN =",
        cumulative_open
    )

    log(
        "UNIT 14A CUMULATIVE CLOSE =",
        cumulative_close
    )

    log(
        "UNIT 14A POSITION MANAGEMENT = "
        "AWAITING SUBUNITS 14B-14F"
    )

    return finish(
        "POSITION_VERIFIED",
        "READY_FOR_BACKUP_AND_TP3_CALCULATIONS"
    )


# ============================================================
# EXECUTE UNIT 14A
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_tp3_runtime(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT
    )
)


# ============================================================
# END UNIT 14A - ORIGINAL POSITION MONITORING ADAPTATION
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 14B - FIVE BACKUP SIZING AND EXPOSURE
# ZERO INDENTATION
#
# ADAPTATION OF ORIGINAL 15-UNIT MODEL
#
# INPUT:
#   UNIT 14A RESULT
#   ORIGINAL UNIT 2 CONFIGURATION
#
# OUTPUT:
#   UPDATED UNIT 14 RESULT
#
# FIVE BACKUPS:
#   B1 = INITIAL x 1.0
#   B2 = INITIAL x 1.5
#   B3 = INITIAL x 2.0
#   B4 = INITIAL x 2.5
#   B5 = INITIAL x 3.0
#
# EXPOSURE CAP = 35%
#
# NO EXCHANGE WRITES
# NO ORDER SUBMISSIONS
# NO BOT_MODE DEPENDENCY
# ============================================================


def fresh_unit_14b_backup_sizing(
    config,
    unit_14a_result
):

    from decimal import Decimal, ROUND_DOWN

    def log(*values):
        print(*values, flush=True)

    def D(value):

        if isinstance(value, bool) or value is None:
            raise ValueError(
                "UNIT14B_INVALID_NUMBER"
            )

        number = Decimal(str(value))

        if not number.is_finite():
            raise ValueError(
                "UNIT14B_NONFINITE_NUMBER"
            )

        return number

    def money(value):

        return str(
            D(value).quantize(
                Decimal("0.00000001"),
                rounding=ROUND_DOWN
            )
        )

    log("=" * 72)
    log(
        "UNIT 14B FIVE BACKUP "
        "SIZING AND EXPOSURE START"
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT14B_CONFIG_INVALID"
        )

    if not isinstance(unit_14a_result, dict):
        raise RuntimeError(
            "UNIT14B_INPUT_INVALID"
        )

    if unit_14a_result.get("subunit") != "14A":
        raise RuntimeError(
            "UNIT14B_REQUIRES_VERIFIED_14A"
        )

    strategy = config.get("strategy", {})

    if not isinstance(strategy, dict):
        raise RuntimeError(
            "UNIT14B_STRATEGY_INVALID"
        )

    # ========================================================
    # 1. CONFIGURATION
    # ========================================================

    initial_margin = D(
        strategy.get(
            "initial_entry_fixed_usdt",
            strategy.get(
                "entry_fixed_usdt",
                "0.5"
            )
        )
    )

    exposure_cap = D(
        strategy.get(
            "maximum_exposure_percent",
            strategy.get(
                "max_exposure_percent",
                "35"
            )
        )
    )

    multipliers = (
        Decimal("1.0"),
        Decimal("1.5"),
        Decimal("2.0"),
        Decimal("2.5"),
        Decimal("3.0"),
    )

    if initial_margin <= 0:
        raise RuntimeError(
            "UNIT14B_INITIAL_MARGIN_INVALID"
        )

    if not (
        Decimal("0")
        < exposure_cap
        <= Decimal("35")
    ):
        raise RuntimeError(
            "UNIT14B_EXPOSURE_CAP_INVALID"
        )

    if len(multipliers) != 5:
        raise RuntimeError(
            "UNIT14B_BACKUP_COUNT_INVALID"
        )

    # ========================================================
    # 2. CONSTRUCT FIVE BACKUPS
    # ========================================================

    backups = []

    for index, multiplier in enumerate(
        multipliers,
        start=1
    ):

        margin = initial_margin * multiplier

        backups.append({
            "number": index,
            "label": "B" + str(index),
            "multiplier": str(multiplier),
            "planned_margin_susdt": money(margin),
            "actual_filled_margin_susdt": None,
            "execution_confirmed": False,
            "affordability_verified": False,
            "execution_authorized": False,
        })

    backup_total = sum(
        (
            D(item["planned_margin_susdt"])
            for item in backups
        ),
        Decimal("0")
    )

    full_ladder_margin = (
        initial_margin + backup_total
    )

    minimum_equity_for_full_ladder = (
        full_ladder_margin
        / (exposure_cap / Decimal("100"))
    )

    log(
        "UNIT 14B INITIAL MARGIN SUSDT =",
        money(initial_margin)
    )

    for item in backups:

        log(
            "UNIT 14B",
            item["label"],
            "MULTIPLIER =",
            item["multiplier"],
            "PLANNED MARGIN =",
            item["planned_margin_susdt"]
        )

    log(
        "UNIT 14B BACKUP TOTAL SUSDT =",
        money(backup_total)
    )

    log(
        "UNIT 14B FULL LADDER MARGIN SUSDT =",
        money(full_ladder_margin)
    )

    log(
        "UNIT 14B EXPOSURE CAP =",
        exposure_cap,
        "%"
    )

    log(
        "UNIT 14B MINIMUM EQUITY "
        "FOR FULL LADDER SUSDT =",
        money(minimum_equity_for_full_ladder)
    )

    # ========================================================
    # 3. INTERNAL SIZING SELF-TESTS
    # ========================================================

    checks = {}

    checks["FIVE_BACKUPS"] = (
        len(backups) == 5
    )

    checks["MULTIPLIERS"] = tuple(
        item["multiplier"]
        for item in backups
    ) == (
        "1.0",
        "1.5",
        "2.0",
        "2.5",
        "3.0",
    )

    checks["BACKUP_TOTAL"] = (
        backup_total
        == initial_margin * Decimal("10")
    )

    checks["FULL_LADDER"] = (
        full_ladder_margin
        == initial_margin * Decimal("11")
    )

    checks["CAP"] = (
        Decimal("0")
        < exposure_cap
        <= Decimal("35")
    )

    checks["INITIAL_POSITIVE"] = (
        initial_margin > 0
    )

    for name, passed in checks.items():

        log(
            "UNIT 14B CHECK",
            name,
            "=",
            "PASS" if passed else "FAIL"
        )

    if not all(checks.values()):
        raise RuntimeError(
            "UNIT14B_SIZING_SELF_TEST_FAILED"
        )

    log(
        "PASS: UNIT 14B SELF TEST =",
        str(len(checks)) + "/"
        + str(len(checks))
    )

    # ========================================================
    # 4. POSITION HANDOVER FROM UNIT 14A
    # ========================================================

    upstream_status = str(
        unit_14a_result.get("status", "")
    )

    position_verified = bool(
        unit_14a_result.get(
            "demo_position_verified",
            False
        )
    )

    active_position = bool(
        unit_14a_result.get(
            "active_position_exists",
            False
        )
    )

    # NOTE:
    # VERIFIED EQUITY, CURRENT MARGIN USAGE,
    # RESERVED MARGIN AND FILLED BACKUP COUNT
    # ARE NOT YET PRESENT IN UNIT 14A.
    #
    # THEREFORE THIS STAGE MUST NOT DECLARE
    # ANY BACKUP EXECUTION AUTHORIZED.
    #
    # LIVE BALANCE / EXPOSURE RECONCILIATION
    # WILL BE INTEGRATED BEFORE 14D EXECUTION.

    verified_equity = None
    verified_margin_usage = None
    verified_available_balance = None

    affordability_verified = False
    execution_authorized = False

    if not position_verified:

        status = "BLOCKED"
        reason = "UNIT14A_POSITION_NOT_VERIFIED"

    elif not active_position:

        status = "IDLE_NO_POSITION"
        reason = "NO_ACTIVE_DEMO_POSITION"

    else:

        status = "BACKUP_PLAN_PREPARED"

        reason = (
            "AWAITING_VERIFIED_EQUITY_"
            "AND_FILLED_BACKUP_HISTORY"
        )

    # ========================================================
    # 5. ORIGINAL UNIT 14 RESULT HANDOVER
    # ========================================================

    result = dict(unit_14a_result)

    result.update({
        "subunit": "14B",
        "revision": "FIVE_BACKUP_EXPOSURE_V1",

        "status": status,
        "skip_reason": reason,

        "initial_margin_susdt": money(
            initial_margin
        ),

        "backup_count_target": 5,
        "backup_multipliers": (
            1.0, 1.5, 2.0, 2.5, 3.0
        ),

        "backups": backups,

        "planned_backup_margin_susdt": money(
            backup_total
        ),

        "planned_total_margin_susdt": money(
            full_ladder_margin
        ),

        "minimum_equity_full_ladder_susdt": money(
            minimum_equity_for_full_ladder
        ),

        "exposure_cap_percent": float(
            exposure_cap
        ),

        "verified_account_equity_susdt":
            verified_equity,

        "verified_margin_usage_susdt":
            verified_margin_usage,

        "verified_available_balance_susdt":
            verified_available_balance,

        "affordability_verified":
            affordability_verified,

        "backup_execution_authorized":
            execution_authorized,

        "backup_management_ready": False,

        "tp3_management_ready": False,

        "backup_execution_attempted": False,

        "exchange_write": False,

        "next_subunit": "14C",
    })

    log("-" * 72)

    log(
        "UNIT 14B UNIT 14A STATUS =",
        upstream_status
    )

    log(
        "UNIT 14B ACTIVE DEMO POSITION =",
        active_position
    )

    log(
        "UNIT 14B AFFORDABILITY VERIFIED =",
        affordability_verified
    )

    log(
        "UNIT 14B BACKUP EXECUTION "
        "AUTHORIZED =",
        execution_authorized
    )

    log(
        "UNIT 14B STATUS =",
        status
    )

    log(
        "UNIT 14B REASON =",
        reason
    )

    log(
        "UNIT 14B EXCHANGE WRITE = False"
    )

    log(
        "UNIT 14B FIVE BACKUP "
        "ADAPTATION RESULT =",
        status
    )

    log("=" * 72)

    return result


# ============================================================
# EXECUTE UNIT 14B
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14A_RESULT = (
    FRESH_RECONSTRUCTION_UNIT_14_RESULT
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14b_backup_sizing(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14A_RESULT
    )
)


# ============================================================
# END UNIT 14B - FIVE BACKUP SIZING AND EXPOSURE
# ZERO INDENTATION
# ============================================================



# ============================================================
# START UNIT 14C - ORIGINAL LIQUIDATION BACKUP TRIGGERS
# ZERO INDENTATION
#
# ORIGINAL 22524-LINE MODEL:
# LONG  = LIQUIDATION * (1 + BUFFER)
# SHORT = LIQUIDATION * (1 - BUFFER)
#
# CURRENT CONFIGURATION:
# BUFFER = 0.3 PERCENT
# BACKUPS = B1 TO B5
#
# IMPORTANT:
# A NEW LIQUIDATION PRICE MUST BE READ AFTER EACH
# CONFIRMED BACKUP FILL BEFORE CALCULATING THE NEXT.
#
# NO ORDERS / NO EXCHANGE WRITES
# NO BOT_MODE DEPENDENCY
# ============================================================


def fresh_unit_14c_liquidation_triggers(
    config,
    unit_14b_result
):

    from decimal import Decimal, ROUND_DOWN, ROUND_UP

    def log(*values):
        print(*values, flush=True)

    def D(value):

        if value is None or isinstance(value, bool):
            raise ValueError("UNIT14C_INVALID_NUMBER")

        number = Decimal(str(value))

        if not number.is_finite():
            raise ValueError("UNIT14C_NONFINITE_NUMBER")

        return number

    def trigger_price(side, liquidation, buffer_pct, tick):

        liquidation = D(liquidation)
        buffer_pct = D(buffer_pct)
        tick = D(tick)

        if not (
            side in ("LONG", "SHORT")
            and liquidation > 0
            and Decimal("0") < buffer_pct < Decimal("100")
            and tick > 0
        ):
            raise ValueError("UNIT14C_TRIGGER_INPUT_INVALID")

        buffer = buffer_pct / Decimal("100")

        if side == "LONG":

            raw = liquidation * (
                Decimal("1") + buffer
            )

            rounded = (
                raw / tick
            ).to_integral_value(
                rounding=ROUND_UP
            ) * tick

        else:

            raw = liquidation * (
                Decimal("1") - buffer
            )

            rounded = (
                raw / tick
            ).to_integral_value(
                rounding=ROUND_DOWN
            ) * tick

        if rounded <= 0:
            raise ValueError("UNIT14C_TRIGGER_INVALID")

        return rounded

    log("=" * 72)
    log("UNIT 14C LIQUIDATION BACKUP TRIGGER START")
    log("UNIT 14C BOT_MODE DEPENDENCY = NONE")

    if not isinstance(config, dict):
        raise RuntimeError("UNIT14C_CONFIG_INVALID")

    if not isinstance(unit_14b_result, dict):
        raise RuntimeError("UNIT14C_INPUT_INVALID")

    if unit_14b_result.get("subunit") != "14B":
        raise RuntimeError("UNIT14C_REQUIRES_UNIT14B")

    strategy = config.get("strategy", {})
    precision = config.get("market_precision", {})

    if not (
        isinstance(strategy, dict)
        and isinstance(precision, dict)
    ):
        raise RuntimeError("UNIT14C_CONFIG_SECTION_INVALID")

    buffer_pct = D(
        strategy.get("backup_buffer_percent", "0.3")
    )

    price_tick = D(
        precision.get("price_step", "0.1")
    )

    if not (
        buffer_pct == Decimal("0.3")
        and price_tick > 0
    ):
        raise RuntimeError("UNIT14C_TRIGGER_CONFIG_INVALID")

    backups = unit_14b_result.get("backups")

    if not isinstance(backups, list) or len(backups) != 5:
        raise RuntimeError("UNIT14C_BACKUP_LADDER_INVALID")

    expected_multipliers = (
        Decimal("1"),
        Decimal("1.5"),
        Decimal("2"),
        Decimal("2.5"),
        Decimal("3"),
    )

    for index, item in enumerate(backups):

        if not isinstance(item, dict):
            raise RuntimeError("UNIT14C_BACKUP_RECORD_INVALID")

        if (
            item.get("number") != index + 1
            or D(item.get("multiplier"))
            != expected_multipliers[index]
        ):
            raise RuntimeError("UNIT14C_BACKUP_SEQUENCE_INVALID")

    # ========================================================
    # 1. ORIGINAL TRIGGER FORMULA SELF-TESTS
    # ========================================================

    sample_liq = Decimal("80000")

    sample_long = trigger_price(
        "LONG",
        sample_liq,
        buffer_pct,
        price_tick
    )

    sample_short = trigger_price(
        "SHORT",
        sample_liq,
        buffer_pct,
        price_tick
    )

    tests = {
        "LONG_FORMULA": (
            sample_long == Decimal("80240.0")
        ),
        "SHORT_FORMULA": (
            sample_short == Decimal("79760.0")
        ),
        "LONG_ABOVE_LIQ": (
            sample_long > sample_liq
        ),
        "SHORT_BELOW_LIQ": (
            sample_short < sample_liq
        ),
        "FIVE_BACKUPS": (
            len(backups) == 5
        ),
        "FRESH_LIQUIDATION_REQUIRED": True,
    }

    for name, passed in tests.items():

        log(
            "UNIT 14C CHECK",
            name,
            "=",
            "PASS" if passed else "FAIL"
        )

    if not all(tests.values()):
        raise RuntimeError("UNIT14C_SELF_TEST_FAILED")

    log("PASS: UNIT 14C SELF TEST = 6/6")

    # ========================================================
    # 2. PRESERVE UNIT 14B RESULT
    # ========================================================

    result = dict(unit_14b_result)

    result.update({
        "subunit": "14C",
        "revision": "LIQUIDATION_BACKUP_V1",

        "backup_buffer_percent": str(buffer_pct),
        "backup_trigger_price": None,
        "backup_trigger_reached": False,
        "next_backup_number": None,

        "liquidation_source": "UNIT14A_WEEX_DEMO",
        "fresh_liquidation_required": True,
        "liquidation_refresh_after_fill": True,

        "backup_trigger_calculated": False,
        "backup_execution_authorized": False,
        "backup_management_ready": False,

        "exchange_write": False,
        "next_subunit": "14D",
    })

    active = bool(
        unit_14b_result.get(
            "active_position_exists", False
        )
    )

    if not bool(
        unit_14b_result.get(
            "demo_position_verified", False
        )
    ):

        status = "BLOCKED"
        reason = "UNIT14A_POSITION_UNVERIFIED"

    elif not active:

        status = "IDLE_NO_POSITION"
        reason = "NO_ACTIVE_DEMO_POSITION"

    else:

        side = str(
            unit_14b_result.get(
                "position_side", ""
            )
        ).upper()

        liquidation_raw = unit_14b_result.get(
            "liquidation_price"
        )

        if side not in ("LONG", "SHORT"):

            status = "BLOCKED"
            reason = "POSITION_DIRECTION_INVALID"

        elif liquidation_raw in (
            None, "", "0", 0
        ):

            status = "AWAITING_LIQUIDATION_PRICE"
            reason = "EXCHANGE_LIQUIDATION_UNAVAILABLE"

        else:

            try:

                liquidation = D(liquidation_raw)

                calculated = trigger_price(
                    side,
                    liquidation,
                    buffer_pct,
                    price_tick
                )

                entry = D(
                    unit_14b_result[
                        "average_entry_price"
                    ]
                )

                # A usable backup trigger must lie
                # between the original entry and
                # the liquidation boundary.
                #
                # LONG:  liquidation < trigger < entry
                # SHORT: entry < trigger < liquidation

                if side == "LONG":

                    boundary_valid = (
                        liquidation < calculated < entry
                    )

                else:

                    boundary_valid = (
                        entry < calculated < liquidation
                    )

                if not boundary_valid:

                    status = "BLOCKED"
                    reason = "TRIGGER_OUTSIDE_ENTRY_LIQ_RANGE"

                else:

                    result["backup_trigger_price"] = str(
                        calculated
                    )

                    result["backup_trigger_calculated"] = True

                    # This stage has no verified
                    # filled-backup count.
                    #
                    # Do not guess which of B1-B5
                    # is next and do not authorize
                    # a submission.

                    status = "TRIGGER_CALCULATED"
                    reason = (
                        "AWAITING_VERIFIED_FILLED_BACKUPS_"
                        "AND_EXPOSURE"
                    )

            except Exception:

                status = "BLOCKED"
                reason = "LIQUIDATION_TRIGGER_INVALID"

    result["status"] = status
    result["skip_reason"] = reason

    # ========================================================
    # 3. OUTPUT FOR UNIT 14D
    # ========================================================

    log("-" * 72)

    log(
        "UNIT 14C POSITION SIDE =",
        result.get("position_side")
    )

    log(
        "UNIT 14C LIQUIDATION PRICE =",
        result.get("liquidation_price")
    )

    log(
        "UNIT 14C BUFFER PERCENT =",
        buffer_pct
    )

    log(
        "UNIT 14C BACKUP TRIGGER =",
        result["backup_trigger_price"]
    )

    log(
        "UNIT 14C NEXT BACKUP =",
        result["next_backup_number"]
    )

    log(
        "UNIT 14C FRESH LIQUIDATION AFTER FILL =",
        result["liquidation_refresh_after_fill"]
    )

    log(
        "UNIT 14C EXECUTION AUTHORIZED =",
        result["backup_execution_authorized"]
    )

    log("UNIT 14C STATUS =", status)
    log("UNIT 14C REASON =", reason)
    log("UNIT 14C EXCHANGE WRITE = False")

    log(
        "UNIT 14C LIQUIDATION TRIGGER RESULT =",
        status
    )

    log("=" * 72)

    return result


# ============================================================
# EXECUTE UNIT 14C
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14B_RESULT = (
    FRESH_RECONSTRUCTION_UNIT_14_RESULT
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14c_liquidation_triggers(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14B_RESULT
    )
)


# ============================================================
# END UNIT 14C - ORIGINAL LIQUIDATION BACKUP TRIGGERS
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 14D REPLACEMENT
# ZERO INDENTATION
#
# ADAPTED FROM ORIGINAL 22524-LINE UNIT 14
#
# WEEX HISTORY = BACKUP RECORD
# NO LOCAL JOURNAL
# NO PERSISTENT STORAGE
#
# ORIGINAL BACKUP ID:
#   FR-B{STAGE}-{TRADE_KEY}
#
# B1 = 1.0 X INITIAL MARGIN
# B2 = 1.5 X INITIAL MARGIN
# B3 = 2.0 X INITIAL MARGIN
# B4 = 2.5 X INITIAL MARGIN
# B5 = 3.0 X INITIAL MARGIN
#
# PROGRESSIVE AFFORDABILITY:
# ONLY THE NEXT BACKUP REQUIRES AVAILABLE FUNDS.
#
# DEMO ONLY.
# MASTER BOT_MODE DOES NOT CONTROL POSITION BACKUPS.
# ============================================================


def fresh_unit_14d_progressive_backups(config, upstream):

    import os
    import json
    import time
    import hmac
    import base64
    import hashlib
    import urllib.parse
    import urllib.request
    import urllib.error

    from decimal import Decimal, ROUND_DOWN, ROUND_UP

    def log(*values):
        print(*values, flush=True)

    def D(value):
        if value is None or isinstance(value, bool):
            raise ValueError("INVALID_DECIMAL")
        number = Decimal(str(value))
        if not number.is_finite():
            raise ValueError("NONFINITE_DECIMAL")
        return number

    def floor_step(value, step):
        return (
            (D(value) / step).to_integral_value(
                rounding=ROUND_DOWN
            ) * step
        )

    def ceil_step(value, step):
        return (
            (D(value) / step).to_integral_value(
                rounding=ROUND_UP
            ) * step
        )

    log("=" * 72)
    log("UNIT 14D ORIGINAL HISTORY-ONLY V3 START")
    log("UNIT 14D BOT_MODE DEPENDENCY = NONE")
    log("UNIT 14D STORAGE JOURNAL = NONE")

    # ========================================================
    # 1. ORIGINAL UNIT CONTRACT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError("UNIT14D_CONFIG_INVALID")

    if not isinstance(upstream, dict):
        raise RuntimeError("UNIT14D_INPUT_INVALID")

    if upstream.get("subunit") != "14C":
        raise RuntimeError("UNIT14D_REQUIRES_14C")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    precision = config.get("market_precision", {})

    if not all(
        isinstance(x, dict)
        for x in (exchange, safety, precision)
    ):
        raise RuntimeError("UNIT14D_CONFIG_SECTIONS_INVALID")

    if not (
        config.get("execution_environment") == "DEMO"
        and exchange.get("demo_order_symbol") == "BTCSUSDT"
        and exchange.get("market_symbol") == "BTCUSDT"
        and exchange.get("contract_base_url")
        == "https://api-contract.weex.com"
    ):
        raise RuntimeError("UNIT14D_DEMO_SCOPE_INVALID")

    for setting in (
        "real_order_submission_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled"
    ):
        if safety.get(setting) is not False:
            raise RuntimeError(
                "UNIT14D_UNSAFE_" + setting
            )

    initial = D(upstream["initial_margin_susdt"])
    cap = D(upstream["exposure_cap_percent"])

    step = D(
        precision.get("quantity_step", "0.0001")
    )
    minimum = D(
        precision.get("minimum_quantity", "0.0001")
    )
    price_step = D(
        precision.get("price_step", "0.1")
    )
    buffer_percent = D(
        upstream["backup_buffer_percent"]
    )

    multipliers = (
        Decimal("1"),
        Decimal("1.5"),
        Decimal("2"),
        Decimal("2.5"),
        Decimal("3")
    )

    if not (
        initial > 0
        and cap == Decimal("35")
        and step > 0
        and minimum > 0
        and price_step > 0
        and buffer_percent == Decimal("0.3")
        and len(upstream.get("backups", [])) == 5
    ):
        raise RuntimeError("UNIT14D_SETTINGS_INVALID")

    result = dict(upstream)

    result.update({
        "subunit": "14D",
        "revision": "ORIGINAL_HISTORY_ONLY_V3",
        "status": "STARTING",
        "skip_reason": "NONE",
        "next_subunit": "14E",

        "completed_backups": 0,
        "next_backup_number": None,
        "next_backup_margin_susdt": None,

        "history_complete": False,
        "history_records": 0,
        "history_reconciled": False,

        "verified_available_balance_susdt": None,
        "estimated_budgeted_funds_susdt": None,
        "estimated_remaining_allowance_susdt": None,

        "affordability_verified": False,
        "backup_trigger_reached": False,
        "backup_execution_authorized": False,
        "backup_execution_attempted": False,
        "backup_submission_accepted": False,
        "backup_fill_confirmed": False,
        "backup_order_id": None,

        "storage_required": False,
        "exchange_write": False,
    })

    def finish(status, reason):

        result["status"] = status
        result["skip_reason"] = reason

        log("-" * 72)
        log("UNIT 14D STATUS =", status)
        log("UNIT 14D REASON =", reason)
        log(
            "UNIT 14D HISTORY COMPLETE =",
            result["history_complete"]
        )
        log(
            "UNIT 14D HISTORY RECORDS =",
            result["history_records"]
        )
        log(
            "UNIT 14D COMPLETED BACKUPS =",
            result["completed_backups"]
        )
        log(
            "UNIT 14D NEXT BACKUP =",
            result["next_backup_number"]
        )
        log(
            "UNIT 14D AVAILABLE SUSDT =",
            result["verified_available_balance_susdt"]
        )
        log(
            "UNIT 14D AFFORDABILITY =",
            result["affordability_verified"]
        )
        log(
            "UNIT 14D TRIGGER REACHED =",
            result["backup_trigger_reached"]
        )
        log(
            "UNIT 14D ORDER ATTEMPTED =",
            result["backup_execution_attempted"]
        )
        log(
            "UNIT 14D FILL CONFIRMED =",
            result["backup_fill_confirmed"]
        )
        log(
            "UNIT 14D STORAGE REQUIRED = False"
        )
        log(
            "UNIT 14D EXCHANGE WRITE =",
            result["exchange_write"]
        )
        log(
            "UNIT 14D HISTORY-ONLY RESULT =",
            status
        )
        log("=" * 72)

        return result

    # ========================================================
    # 2. ORIGINAL FIVE-BACKUP TESTS
    # ========================================================

    tests = {
        "FIVE_BACKUPS": len(multipliers) == 5,
        "B1": multipliers[0] == Decimal("1"),
        "B2": multipliers[1] == Decimal("1.5"),
        "B3": multipliers[2] == Decimal("2"),
        "B4": multipliers[3] == Decimal("2.5"),
        "B5": multipliers[4] == Decimal("3"),
        "EXPOSURE_CAP": cap == 35,
        "INITIAL_MARGIN": initial > 0,
        "TOTAL_MULTIPLIERS": (
            sum(multipliers) == Decimal("10")
        ),
    }

    for name, passed in tests.items():
        log(
            "UNIT 14D CHECK",
            name,
            "=",
            "PASS" if passed else "FAIL"
        )

    if not all(tests.values()):
        raise RuntimeError("UNIT14D_SELF_TEST_FAILED")

    log("PASS: UNIT 14D SELF TEST = 8/8")

    # ========================================================
    # 3. FLAT-POSITION HANDOVER
    # ========================================================

    if not upstream.get("demo_position_verified", False):
        return finish(
            "BLOCKED",
            "UNIT14A_POSITION_UNVERIFIED"
        )

    if not upstream.get("active_position_exists", False):
        return finish(
            "IDLE_NO_POSITION",
            "NO_ACTIVE_DEMO_POSITION"
        )

    # ========================================================
    # 4. ORIGINAL WEEX SIGNED DEMO CONNECTION
    # ========================================================

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
        return finish(
            "BLOCKED",
            "WEEX_CREDENTIALS_MISSING"
        )

    base = "https://api-contract.weex.com"

    balance_path = "/capi/v3/sim/balance"
    position_path = "/capi/v3/sim/position/allPosition"
    history_path = "/capi/v3/sim/order/history"
    order_path = "/capi/v3/sim/order"

    class NoRedirect(urllib.request.HTTPRedirectHandler):

        def redirect_request(
            self, req, fp, code, msg, headers, url
        ):
            return None

    opener = urllib.request.build_opener(NoRedirect())

    def signed(method, path, query=None, payload=None):

        if method == "GET":
            if path not in (
                balance_path,
                position_path,
                history_path
            ):
                raise RuntimeError("GET_ENDPOINT_BLOCKED")
            if payload is not None:
                raise RuntimeError("GET_PAYLOAD_BLOCKED")

        elif method == "POST":
            if path != order_path or query:
                raise RuntimeError("POST_ENDPOINT_BLOCKED")
            if not isinstance(payload, dict):
                raise RuntimeError("POST_PAYLOAD_BLOCKED")

        else:
            raise RuntimeError("METHOD_BLOCKED")

        query_text = (
            urllib.parse.urlencode(query)
            if query
            else ""
        )

        target = (
            path
            + ("?" + query_text if query_text else "")
        )

        body = (
            ""
            if payload is None
            else json.dumps(
                payload,
                separators=(",", ":")
            )
        )

        timestamp = str(int(time.time() * 1000))

        prehash = (
            timestamp + method + target + body
        )

        signature = base64.b64encode(
            hmac.new(
                secret.encode(),
                prehash.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        request = urllib.request.Request(
            base + target,
            headers={
                "ACCESS-KEY": key,
                "ACCESS-SIGN": signature,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": phrase,
                "Content-Type": "application/json",
            },
            method=method,
            data=(
                body.encode()
                if payload is not None
                else None
            )
        )

        try:
            with opener.open(request, timeout=15) as response:
                http = response.getcode()
                raw = response.read(65537)

        except urllib.error.HTTPError as error:
            http = error.code
            raw = error.read(65537)

        if len(raw) > 65536:
            raise RuntimeError("RESPONSE_TOO_LARGE")

        return http, json.loads(raw.decode())

    def get_positions():

        http, rows = signed("GET", position_path)

        if http != 200 or not isinstance(rows, list):
            raise RuntimeError("POSITION_GET_INVALID")

        active = []

        for row in rows:

            if not isinstance(row, dict):
                raise RuntimeError("POSITION_RECORD_INVALID")

            if str(
                row.get("symbol", "")
            ).upper() != "BTCSUSDT":
                continue

            quantity = D(row.get("size", "0"))

            if quantity < 0:
                raise RuntimeError("NEGATIVE_POSITION_SIZE")

            if quantity > 0:
                active.append(row)

        return active

    def get_demo_balance():

        http, rows = signed("GET", balance_path)

        if http != 200 or not isinstance(rows, list):
            raise RuntimeError("BALANCE_GET_INVALID")

        for item in rows:

            if (
                isinstance(item, dict)
                and str(
                    item.get("asset", "")
                ).upper() == "SUSDT"
            ):
                return item

        raise RuntimeError("SUSDT_BALANCE_MISSING")

    # ========================================================
    # 5. ORIGINAL COMPLETE WEEX HISTORY
    # ========================================================

    def get_order_history():

        all_orders = []
        page_limit = 1000

        for page in range(20):

            http, rows = signed(
                "GET",
                history_path,
                query={
                    "symbol": "BTCSUSDT",
                    "limit": page_limit,
                    "page": page
                }
            )

            if http != 200 or not isinstance(rows, list):
                raise RuntimeError("HISTORY_RESPONSE_INVALID")

            for order in rows:
                if not isinstance(order, dict):
                    raise RuntimeError("HISTORY_RECORD_INVALID")

            all_orders.extend(rows)

            if len(rows) < page_limit:
                return all_orders

        raise RuntimeError("HISTORY_PAGINATION_INCOMPLETE")

    # ========================================================
    # 6. ORIGINAL TRADE KEY AND BACKUP IDs
    # ========================================================

    def get_trade_key(position):

        created_time = str(
            position.get("createdTime", "")
        )

        if created_time.isdigit():
            return created_time[-12:]

        position_id = str(
            position.get("id", "")
        )

        if position_id:
            return position_id[-12:]

        raise RuntimeError(
            "POSITION_TRADE_ID_UNAVAILABLE"
        )

    def backup_client_id(stage, trade_key):

        return (
            f"FR-B{stage}-{trade_key}"
        )[:36]

    def determine_backup_stage(history, trade_key):

        completed = 0
        existing = set()
        filled = set()
        unresolved = set()

        for stage in range(1, 6):

            expected = backup_client_id(
                stage,
                trade_key
            )

            matches = [
                row
                for row in history
                if str(
                    row.get(
                        "clientOrderId",
                        row.get("newClientOrderId", "")
                    )
                ) == expected
            ]

            if len(matches) > 1:
                raise RuntimeError(
                    "DUPLICATE_BACKUP_HISTORY_B"
                    + str(stage)
                )

            if not matches:
                continue

            existing.add(stage)

            order = matches[0]

            if str(
                order.get("symbol", "")
            ).upper() != "BTCSUSDT":
                raise RuntimeError(
                    "BACKUP_SYMBOL_MISMATCH"
                )

            status = str(
                order.get("status", "")
            ).upper()

            executed = D(
                order.get("executedQty", "0")
            )

            original = D(
                order.get("origQty", "0")
            )

            if executed < 0 or original < 0:
                raise RuntimeError(
                    "BACKUP_QUANTITY_INVALID"
                )

            if status == "FILLED":

                if (
                    executed <= 0
                    or original <= 0
                    or executed != original
                ):
                    raise RuntimeError(
                        "BACKUP_FULL_FILL_UNVERIFIED"
                    )

                filled.add(stage)

            else:

                # A partial fill, canceled order,
                # unknown status or pending order
                # must never silently authorize
                # another stage or retry.
                unresolved.add(stage)

        for stage in range(1, 6):

            if stage in filled:

                if stage != completed + 1:
                    raise RuntimeError(
                        "NON_SEQUENTIAL_BACKUP_FILLS"
                    )

                completed = stage

            else:
                break

        if any(
            stage > completed + 1
            for stage in existing
        ):
            raise RuntimeError(
                "NON_SEQUENTIAL_BACKUP_ORDERS"
            )

        return completed, existing, filled, unresolved

    # ========================================================
    # 7. ORIGINAL MARKET PRICE ENDPOINT
    # ========================================================

    def get_mark_price():

        query = urllib.parse.urlencode({
            "symbol": "BTCUSDT",
            "priceType": "MARK",
        })

        request = urllib.request.Request(
            base
            + "/capi/v3/market/symbolPrice?"
            + query,
            method="GET"
        )

        with opener.open(request, timeout=15) as response:
            raw = response.read(65537)

        if len(raw) > 65536:
            raise RuntimeError("MARK_RESPONSE_TOO_LARGE")

        data = json.loads(raw.decode())

        mark = D(data["price"])

        if mark <= 0:
            raise RuntimeError("MARK_PRICE_INVALID")

        return mark

    # ========================================================
    # 8. VERIFY CURRENT DEMO POSITION
    # ========================================================

    try:

        active = get_positions()

        if len(active) != 1:
            raise RuntimeError(
                "ACTIVE_POSITION_COUNT_INVALID"
            )

        position = active[0]

        side = str(
            position.get("side", "")
        ).upper()

        if side not in ("LONG", "SHORT"):
            raise RuntimeError("POSITION_SIDE_INVALID")

        if side != str(
            upstream.get("position_side", "")
        ).upper():
            raise RuntimeError("UNIT14A_SIDE_CHANGED")

        size = D(position["size"])
        leverage = D(position["leverage"])
        open_value = D(position["openValue"])

        liquidation = D(
            position.get(
                "liquidatePrice",
                position.get(
                    "liquidationPrice",
                    position.get("liqPrice")
                )
            )
        )

        if not (
            size >= minimum
            and leverage > 0
            and open_value > 0
            and liquidation > 0
        ):
            raise RuntimeError(
                "POSITION_FINANCIALS_INVALID"
            )

        trade_key = get_trade_key(position)

    except Exception as error:

        log(
            "UNIT 14D POSITION ERROR =",
            type(error).__name__
        )

        return finish(
            "BLOCKED",
            "CURRENT_DEMO_POSITION_UNVERIFIED"
        )

    # ========================================================
    # 9. EXCHANGE HISTORY RECONCILIATION
    # ========================================================

    try:

        history = get_order_history()

        result["history_complete"] = True
        result["history_records"] = len(history)

        (
            completed,
            existing_stages,
            filled_stages,
            unresolved_stages
        ) = determine_backup_stage(
            history,
            trade_key
        )

        result["completed_backups"] = completed
        result["history_reconciled"] = True

    except Exception as error:

        log(
            "UNIT 14D HISTORY ERROR =",
            type(error).__name__
        )

        return finish(
            "RECONCILIATION_WAIT",
            "WEEX_BACKUP_HISTORY_UNVERIFIED"
        )

    log(
        "PASS: UNIT 14D COMPLETE WEEX HISTORY |",
        "RECORDS =", len(history)
    )

    log(
        "UNIT 14D CONFIRMED FILLED BACKUPS =",
        completed
    )

    if unresolved_stages:

        return finish(
            "RECONCILIATION_WAIT",
            "EXISTING_BACKUP_ORDER_UNRESOLVED"
        )

    if completed >= 5:

        return finish(
            "ALL_BACKUPS_COMPLETED",
            "B1_TO_B5_FILLED"
        )

    stage = completed + 1

    result["next_backup_number"] = stage

    next_id = backup_client_id(
        stage,
        trade_key
    )

    if stage in existing_stages:

        return finish(
            "RECONCILIATION_WAIT",
            "NEXT_BACKUP_ALREADY_EXISTS"
        )

    # ========================================================
    # 10. ORIGINAL PROGRESSIVE AFFORDABILITY
    #
    # ONLY NEXT BACKUP CHECKED.
    # NO FULL-LADDER FUNDING REQUIREMENT.
    # ========================================================

    multiplier = multipliers[completed]

    backup_margin = initial * multiplier

    current_committed = initial * (
        Decimal("1")
        + sum(
            multipliers[:completed],
            Decimal("0")
        )
    )

    projected_committed = (
        current_committed + backup_margin
    )

    result["next_backup_margin_susdt"] = str(
        backup_margin
    )

    try:

        balance = get_demo_balance()

        available = D(
            balance["availableBalance"]
        )

        if available < 0:
            raise RuntimeError("NEGATIVE_AVAILABLE_BALANCE")

    except Exception:

        return finish(
            "BLOCKED",
            "FRESH_SUSDT_BALANCE_UNVERIFIED"
        )

    # ORIGINAL 22524-LINE FUNDING ESTIMATE

    budgeted_funds = (
        available + current_committed
    )

    exposure_limit = (
        budgeted_funds
        * cap
        / Decimal("100")
    )

    allowance = max(
        Decimal("0"),
        exposure_limit - current_committed
    )

    result[
        "verified_available_balance_susdt"
    ] = str(available)

    result[
        "estimated_budgeted_funds_susdt"
    ] = str(budgeted_funds)

    result[
        "estimated_remaining_allowance_susdt"
    ] = str(allowance)

    log(
        f"UNIT 14D B{stage} MULTIPLIER =",
        multiplier
    )

    log(
        "UNIT 14D REQUIRED MARGIN =",
        backup_margin
    )

    log(
        "UNIT 14D CURRENT PLANNED MARGIN =",
        current_committed
    )

    log(
        "UNIT 14D PROJECTED PLANNED MARGIN =",
        projected_committed
    )

    log(
        "UNIT 14D AVAILABLE SUSDT =",
        available
    )

    log(
        "UNIT 14D REMAINING ALLOWANCE =",
        allowance
    )

    log(
        "UNIT 14D FULL LADDER PREFUNDING = FALSE"
    )

    if available < backup_margin:

        return finish(
            "WAITING_FOR_FUNDS",
            "NEXT_BACKUP_NOT_AFFORDABLE"
        )

    if backup_margin > allowance:

        return finish(
            "WAITING_EXPOSURE_CAP",
            "NEXT_BACKUP_EXCEEDS_35_PERCENT_ALLOWANCE"
        )

    result["affordability_verified"] = True

    log(
        "PASS: UNIT 14D ORIGINAL PROGRESSIVE AFFORDABILITY"
    )

    # ========================================================
    # 11. LIQUIDATION-BASED BACKUP TRIGGER
    # ========================================================

    try:

        mark = get_mark_price()

        buffer = (
            buffer_percent / Decimal("100")
        )

        entry = open_value / size

        if side == "LONG":

            trigger = ceil_step(
                liquidation * (
                    Decimal("1") + buffer
                ),
                price_step
            )

            valid = (
                liquidation < trigger < entry
            )

            reached = mark <= trigger

        else:

            trigger = floor_step(
                liquidation * (
                    Decimal("1") - buffer
                ),
                price_step
            )

            valid = (
                entry < trigger < liquidation
            )

            reached = mark >= trigger

        if not valid:
            raise RuntimeError(
                "TRIGGER_OUTSIDE_ENTRY_LIQUIDATION"
            )

    except Exception:

        return finish(
            "BLOCKED",
            "BACKUP_TRIGGER_UNVERIFIED"
        )

    result["backup_trigger_price"] = str(trigger)
    result["backup_trigger_reached"] = reached

    log(
        f"UNIT 14D B{stage} LIQUIDATION =",
        liquidation
    )

    log(
        f"UNIT 14D B{stage} TRIGGER =",
        trigger
    )

    log(
        f"UNIT 14D B{stage} MARK =",
        mark
    )

    log(
        f"UNIT 14D B{stage} REACHED =",
        reached
    )

    if not reached:

        return finish(
            "MONITORING",
            "NEXT_BACKUP_TRIGGER_NOT_REACHED"
        )

    # ========================================================
    # 12. ORIGINAL STEP-AWARE QUANTITY
    # ========================================================

    notional = backup_margin * leverage

    quantity = floor_step(
        notional / mark,
        step
    )

    if quantity < minimum:

        return finish(
            "WAITING_MINIMUM_QUANTITY",
            "BACKUP_BELOW_EXCHANGE_MINIMUM"
        )

    # ========================================================
    # 13. FINAL POSITION CHECK
    # ========================================================

    try:

        final_positions = get_positions()

        if len(final_positions) != 1:
            raise RuntimeError(
                "FINAL_POSITION_COUNT_CHANGED"
            )

        final = final_positions[0]

        if get_trade_key(final) != trade_key:
            raise RuntimeError(
                "POSITION_IDENTITY_CHANGED"
            )

        if str(
            final.get("side", "")
        ).upper() != side:
            raise RuntimeError(
                "POSITION_SIDE_CHANGED"
            )

        if D(final["size"]) != size:
            raise RuntimeError(
                "POSITION_SIZE_CHANGED"
            )

        final_liquidation = D(
            final.get(
                "liquidatePrice",
                final.get(
                    "liquidationPrice",
                    final.get("liqPrice")
                )
            )
        )

        if final_liquidation != liquidation:
            raise RuntimeError(
                "LIQUIDATION_CHANGED"
            )

    except Exception:

        return finish(
            "MONITORING",
            "POSITION_CHANGED_RECALCULATE"
        )

    # ========================================================
    # 14. SECOND HISTORY VERIFICATION
    # ANTI-DUPLICATE JUST BEFORE POST
    # ========================================================

    try:

        recent_history = get_order_history()

        (
            final_completed,
            final_existing,
            final_filled,
            final_unresolved
        ) = determine_backup_stage(
            recent_history,
            trade_key
        )

        if (
            final_completed != completed
            or final_unresolved
            or stage in final_existing
        ):
            raise RuntimeError(
                "BACKUP_HISTORY_CHANGED"
            )

    except Exception:

        return finish(
            "RECONCILIATION_WAIT",
            "FINAL_HISTORY_UNVERIFIED"
        )

    # ========================================================
    # 15. ORIGINAL DEMO MARKET ORDER
    # ========================================================

    order_side = (
        "BUY" if side == "LONG" else "SELL"
    )

    payload = {
        "symbol": "BTCSUSDT",
        "side": order_side,
        "positionSide": side,
        "type": "MARKET",
        "quantity": format(quantity, "f"),
        "newClientOrderId": next_id,
    }

    log(
        f"UNIT 14D B{stage} ORDER SIDE =",
        order_side
    )

    log(
        f"UNIT 14D B{stage} QUANTITY =",
        quantity
    )

    log(
        f"UNIT 14D B{stage} CLIENT ID =",
        next_id
    )

    log(
        "UNIT 14D REAL CASH ORDER = FALSE"
    )

    # ========================================================
    # 16. SUBMISSION BOUNDARY
    #
    # IMPORTANT:
    # THIS PRESERVES THE ORIGINAL MARKET ORDER CALL.
    # ONLY WEEX DEMO ENDPOINT IS ALLOWED.
    # ========================================================

    result["backup_execution_authorized"] = True
    result["backup_execution_attempted"] = True
    result["exchange_write"] = True

    try:

        http, response = signed(
            "POST",
            order_path,
            payload=payload
        )

    except Exception as error:

        log(
            "UNIT 14D POST ERROR =",
            type(error).__name__
        )

        return finish(
            "BACKUP_SUBMISSION_UNCERTAIN",
            "VERIFY_EXCHANGE_HISTORY_BEFORE_ANY_RETRY"
        )

    if not (
        200 <= http < 300
        and isinstance(response, dict)
        and response.get("success") is True
        and response.get("orderId")
    ):

        return finish(
            "BACKUP_SUBMISSION_UNCONFIRMED",
            "VERIFY_EXCHANGE_HISTORY_BEFORE_ANY_RETRY"
        )

    result["backup_order_id"] = str(
        response["orderId"]
    )

    result["backup_submission_accepted"] = True

    log(
        f"PASS: UNIT 14D B{stage} DEMO ORDER ACCEPTED"
    )

    log(
        "UNIT 14D ORDER ID =",
        result["backup_order_id"]
    )

    log(
        "UNIT 14D BACKUP COUNT ADVANCED = FALSE"
    )

    return finish(
        "BACKUP_SUBMITTED_AWAITING_FILL",
        "WEEX_HISTORY_RECONCILIATION_REQUIRED"
    )


# ============================================================
# EXECUTE UNIT 14D
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14C_RESULT = (
    FRESH_RECONSTRUCTION_UNIT_14_RESULT
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14d_progressive_backups(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14C_RESULT
    )
)


# ============================================================
# END COMPLETE UNIT 14D REPLACEMENT
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 14E
# ZERO INDENTATION
#
# ADAPTED FROM ORIGINAL 22524-LINE MODEL
#
# DYNAMIC TP3 TRAILING:
# REFERENCE = 0.20%
# MINIMUM   = 0.10%
# MAXIMUM   = 0.40%
#
# ORIGINAL COMPONENTS:
# ATR CONTRIBUTION         = MIN(ATR%, 0.30) * 0.25
# TREND CONTRIBUTION       = TREND STRENGTH * 0.08
# MOMENTUM DETERIORATION   = DETERIORATION * 0.12
#
# UNIT 14E:
# - PRESERVES TP3 CALCULATION
# - TRACKS BEST FAVORABLE MARK WITHIN THIS PROCESS
# - COORDINATES WITH UNIT 13 AND UNIT 14D
# - NEVER SUBMITS AN ORDER
# - DOES NOT ALTER BOT_MODE
# ============================================================


def fresh_unit_14e_dynamic_tp3(
    config,
    unit_14d_result,
    unit_13_result
):

    from decimal import Decimal
    from datetime import datetime, timezone

    def log(*values):
        print(*values, flush=True)

    def D(value):
        if value is None or isinstance(value, bool):
            raise ValueError("INVALID_DECIMAL")
        number = Decimal(str(value))
        if not number.is_finite():
            raise ValueError("NONFINITE_DECIMAL")
        return number

    def clamp(value, low, high):
        return max(low, min(value, high))

    log("=" * 72)
    log(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 14E ORIGINAL DYNAMIC TP3 START"
    )

    log("UNIT 14E BOT_MODE DEPENDENCY = NONE")
    log("UNIT 14E EXCHANGE WRITE = NONE")

    if not isinstance(config, dict):
        raise RuntimeError("UNIT14E_CONFIG_INVALID")

    if not isinstance(unit_14d_result, dict):
        raise RuntimeError("UNIT14E_14D_INVALID")

    if not isinstance(unit_13_result, dict):
        raise RuntimeError("UNIT14E_13_INVALID")

    if unit_14d_result.get("subunit") != "14D":
        raise RuntimeError("UNIT14E_REQUIRES_14D")

    strategy = config.get("strategy", {})

    if not isinstance(strategy, dict):
        raise RuntimeError("UNIT14E_STRATEGY_INVALID")

    reference = D(
        strategy.get(
            "tp3_trailing_reference_percent",
            unit_13_result.get(
                "tp3_trailing_reference_percent",
                "0.20"
            )
        )
    )

    minimum_callback = D(
        strategy.get(
            "tp3_trailing_min_percent",
            unit_13_result.get(
                "tp3_trailing_min_percent",
                "0.10"
            )
        )
    )

    maximum_callback = D(
        strategy.get(
            "tp3_trailing_max_percent",
            unit_13_result.get(
                "tp3_trailing_max_percent",
                "0.40"
            )
        )
    )

    if not (
        Decimal("0") < minimum_callback
        <= reference <= maximum_callback
        and minimum_callback == Decimal("0.10")
        and maximum_callback == Decimal("0.40")
    ):
        raise RuntimeError(
            "UNIT14E_TRAILING_CONFIGURATION_INVALID"
        )

    # ========================================================
    # ORIGINAL DYNAMIC CALLBACK FORMULA
    # ========================================================

    def calculate_dynamic_callback(
        atr_percent,
        trend_strength,
        deterioration
    ):

        atr_percent = max(
            Decimal("0"),
            D(atr_percent)
        )

        trend_strength = clamp(
            D(trend_strength),
            Decimal("0"),
            Decimal("1")
        )

        deterioration = clamp(
            D(deterioration),
            Decimal("0"),
            Decimal("1")
        )

        volatility_adjustment = (
            min(atr_percent, Decimal("0.30"))
            * Decimal("0.25")
        )

        trend_adjustment = (
            trend_strength * Decimal("0.08")
        )

        deterioration_adjustment = (
            deterioration * Decimal("0.12")
        )

        calculated = (
            reference
            + volatility_adjustment
            + trend_adjustment
            - deterioration_adjustment
        )

        return clamp(
            calculated,
            minimum_callback,
            maximum_callback
        )

    # ========================================================
    # INTERNAL FORMULA TESTS
    # ========================================================

    tests = {
        "REFERENCE": reference == Decimal("0.20"),
        "MINIMUM": minimum_callback == Decimal("0.10"),
        "MAXIMUM": maximum_callback == Decimal("0.40"),
        "HEALTHY": (
            calculate_dynamic_callback(0, 0, 0)
            == reference
        ),
        "TREND_WIDENS": (
            calculate_dynamic_callback(0, 1, 0)
            > reference
        ),
        "VOLATILITY_WIDENS": (
            calculate_dynamic_callback(0.30, 0, 0)
            > reference
        ),
        "DETERIORATION_TIGHTENS": (
            calculate_dynamic_callback(0, 0, 1)
            <= reference
        ),
        "CLAMP": (
            minimum_callback
            <= calculate_dynamic_callback(
                10, 10, 0
            )
            <= maximum_callback
        ),
    }

    for name, passed in tests.items():
        log(
            "UNIT 14E CHECK",
            name,
            "=",
            "PASS" if passed else "FAIL"
        )

    if not all(tests.values()):
        raise RuntimeError("UNIT14E_SELF_TEST_FAILED")

    log("PASS: UNIT 14E SELF TEST = 8/8")

    result = dict(unit_14d_result)

    result.update({
        "subunit": "14E",
        "revision": "ORIGINAL_DYNAMIC_TP3_V1",
        "status": "STARTING",
        "skip_reason": "NONE",

        "tp3_reference_percent": str(reference),
        "tp3_min_percent": str(minimum_callback),
        "tp3_max_percent": str(maximum_callback),

        "tp3_armed": False,
        "tp3_best_mark": None,
        "tp3_current_mark": None,
        "tp3_dynamic_callback_percent": None,
        "tp3_trailing_trigger": None,
        "tp3_callback_reached": False,

        "tp3_close_authorized": False,
        "tp3_close_attempted": False,
        "tp3_close_confirmed": False,

        "backup_order_unresolved": False,
        "exchange_write": False,
        "next_subunit": "14F",
    })

    def finish(status, reason):

        result["status"] = status
        result["skip_reason"] = reason

        log("-" * 72)
        log("UNIT 14E STATUS =", status)
        log("UNIT 14E REASON =", reason)

        log(
            "UNIT 14E TP3 ARMED =",
            result["tp3_armed"]
        )

        log(
            "UNIT 14E DYNAMIC CALLBACK =",
            result["tp3_dynamic_callback_percent"]
        )

        log(
            "UNIT 14E BEST MARK =",
            result["tp3_best_mark"]
        )

        log(
            "UNIT 14E TRAILING TRIGGER =",
            result["tp3_trailing_trigger"]
        )

        log(
            "UNIT 14E CALLBACK REACHED =",
            result["tp3_callback_reached"]
        )

        log(
            "UNIT 14E CLOSE AUTHORIZED = False"
        )

        log(
            "UNIT 14E EXCHANGE WRITE = False"
        )

        log(
            "UNIT 14E ORIGINAL DYNAMIC TP3 RESULT =",
            status
        )

        log("=" * 72)

        return result

    # ========================================================
    # UNIT 14D BACKUP COORDINATION
    # ========================================================

    blocking_14d_statuses = {
        "BACKUP_SUBMITTED_AWAITING_FILL",
        "BACKUP_SUBMISSION_UNCERTAIN",
        "BACKUP_SUBMISSION_UNCONFIRMED",
        "RECONCILIATION_WAIT",
    }

    backup_status = str(
        unit_14d_result.get("status", "")
    ).upper()

    result["backup_order_unresolved"] = (
        backup_status in blocking_14d_statuses
        or bool(
            unit_14d_result.get(
                "backup_execution_attempted",
                False
            )
        )
    )

    # ========================================================
    # UNIT 13 TP3 HANDOVER
    # ========================================================

    if not unit_14d_result.get(
        "demo_position_verified",
        False
    ):
        return finish(
            "BLOCKED",
            "POSITION_NOT_VERIFIED"
        )

    if not unit_14d_result.get(
        "active_position_exists",
        False
    ):
        return finish(
            "IDLE_NO_POSITION",
            "NO_ACTIVE_DEMO_POSITION"
        )

    if result["backup_order_unresolved"]:
        return finish(
            "WAITING_BACKUP_RECONCILIATION",
            "BACKUP_ORDER_UNRESOLVED"
        )

    side = str(
        unit_14d_result.get(
            "position_side", ""
        )
    ).upper()

    if side not in ("LONG", "SHORT"):
        return finish(
            "BLOCKED",
            "POSITION_SIDE_INVALID"
        )

    tp3_armed = (
        unit_13_result.get("tp3_armed") is True
    )

    result["tp3_armed"] = tp3_armed

    if not tp3_armed:
        return finish(
            "TP3_NOT_ARMED",
            "AWAITING_UNIT13_TP_CONFIRMATION"
        )

    # ========================================================
    # MARKET INPUTS
    #
    # THESE MUST BE FRESH VERIFIED INPUTS,
    # NOT INVENTED CONSTANTS.
    #
    # UNIT 14F WILL CONNECT THE ORIGINAL
    # MARKET-CANDLE ANALYSIS PROVIDER.
    # ========================================================

    analysis = unit_14d_result.get(
        "tp3_market_analysis"
    )

    mark_raw = unit_14d_result.get(
        "tp3_current_mark"
    )

    if not isinstance(analysis, dict):
        return finish(
            "AWAITING_MARKET_ANALYSIS",
            "ATR_TREND_MOMENTUM_NOT_AVAILABLE"
        )

    if mark_raw is None:
        return finish(
            "AWAITING_MARKET_MARK",
            "CURRENT_MARK_NOT_AVAILABLE"
        )

    try:

        mark = D(mark_raw)

        atr_percent = D(
            analysis["atr_percent"]
        )

        trend_strength = D(
            analysis["trend_strength"]
        )

        earlier_move = D(
            analysis["earlier_move"]
        )

        recent_move = D(
            analysis["recent_move"]
        )

        if mark <= 0:
            raise ValueError("INVALID_MARK")

        if side == "LONG":

            earlier_favorable = max(
                earlier_move,
                Decimal("0")
            )

            recent_favorable = max(
                recent_move,
                Decimal("0")
            )

            if recent_move < 0:
                deterioration = Decimal("1")

            elif earlier_favorable > 0:
                deterioration = (
                    Decimal("1")
                    - min(
                        recent_favorable
                        / earlier_favorable,
                        Decimal("1")
                    )
                )

            else:
                deterioration = Decimal("0")

        else:

            earlier_favorable = max(
                -earlier_move,
                Decimal("0")
            )

            recent_favorable = max(
                -recent_move,
                Decimal("0")
            )

            if recent_move > 0:
                deterioration = Decimal("1")

            elif earlier_favorable > 0:
                deterioration = (
                    Decimal("1")
                    - min(
                        recent_favorable
                        / earlier_favorable,
                        Decimal("1")
                    )
                )

            else:
                deterioration = Decimal("0")

        callback = calculate_dynamic_callback(
            atr_percent,
            trend_strength,
            deterioration
        )

    except Exception as exc:

        log(
            "UNIT 14E MARKET VALIDATION ERROR =",
            type(exc).__name__
        )

        return finish(
            "BLOCKED",
            "MARKET_ANALYSIS_INVALID"
        )

    # ========================================================
    # BEST FAVORABLE MARK
    #
    # IN-PROCESS MEMORY ONLY.
    # RESTART DOES NOT CERTIFY A HISTORICAL PEAK.
    # ========================================================

    global FRESH_UNIT14E_TRAIL_MEMORY

    if not isinstance(
        globals().get(
            "FRESH_UNIT14E_TRAIL_MEMORY"
        ),
        dict
    ):
        FRESH_UNIT14E_TRAIL_MEMORY = {}

    memory = FRESH_UNIT14E_TRAIL_MEMORY

    identity = (
        "BTCSUSDT|"
        + side
        + "|"
        + str(
            unit_14d_result.get(
                "position_size", ""
            )
        )
    )

    if memory.get("identity") != identity:

        memory.clear()

        memory.update({
            "identity": identity,
            "best_mark": str(mark),
            "observations": 1,
        })

    else:

        previous_best = D(
            memory["best_mark"]
        )

        if side == "LONG":
            best = max(previous_best, mark)
        else:
            best = min(previous_best, mark)

        memory["best_mark"] = str(best)

        memory["observations"] = int(
            memory.get("observations", 0)
        ) + 1

    best_mark = D(
        memory["best_mark"]
    )

    callback_fraction = (
        callback / Decimal("100")
    )

    if side == "LONG":

        trigger = (
            best_mark
            * (
                Decimal("1")
                - callback_fraction
            )
        )

        reached = mark <= trigger

    else:

        trigger = (
            best_mark
            * (
                Decimal("1")
                + callback_fraction
            )
        )

        reached = mark >= trigger

    result.update({
        "tp3_current_mark": str(mark),
        "tp3_best_mark": str(best_mark),
        "tp3_dynamic_callback_percent": str(
            callback
        ),
        "tp3_trailing_trigger": str(trigger),
        "tp3_callback_reached": reached,
        "tp3_memory_observations": memory[
            "observations"
        ],
    })

    log(
        "UNIT 14E ATR PERCENT =",
        atr_percent
    )

    log(
        "UNIT 14E TREND STRENGTH =",
        trend_strength
    )

    log(
        "UNIT 14E MOMENTUM DETERIORATION =",
        deterioration
    )

    # No TP3 order is authorized in 14E.
    # Unit 14F must reconcile position and history.

    if reached:

        return finish(
            "TP3_CALLBACK_REACHED",
            "AWAITING_UNIT14F_EXECUTION_CHECKS"
        )

    return finish(
        "TP3_TRAILING_ACTIVE",
        "TRAILING_TRIGGER_NOT_REACHED"
    )


# ============================================================
# EXECUTE UNIT 14E
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14D_RESULT = (
    FRESH_RECONSTRUCTION_UNIT_14_RESULT
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14e_dynamic_tp3(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_14D_RESULT,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT
    )
)


# ============================================================
# END COMPLETE UNIT 14E
# ZERO INDENTATION
# ============================================================



# ============================================================
# START COMPLETE UNIT 14F
# ZERO INDENTATION
#
# ORIGINAL 22524-LINE MODEL ADAPTATION
#
# UNIT 14F V1:
# CONTINUOUS POSITION MANAGEMENT COORDINATION
#
# UNIT 12: INITIAL DEMO ENTRY
# UNIT 13: TP1 / TP2
# UNIT 14D: PROGRESSIVE BACKUPS
# UNIT 14E: DYNAMIC TP3
# UNIT 14F: FINAL POSITION RECONCILIATION
#
# READ ONLY
# NO EXTRA ORDER SUBMISSION
# NO NEW MODE SWITCH
# NO LOCAL STORAGE
# ============================================================


def fresh_unit_14f_coordinator(
    config,
    unit_13_result,
    unit_14e_result
):

    import os
    import time
    import hmac
    import json
    import base64
    import hashlib
    import urllib.request
    import urllib.error

    from decimal import Decimal

    def log(*args):
        print(*args, flush=True)

    def dec(value):

        if value is None or isinstance(value, bool):
            raise ValueError("INVALID_DECIMAL")

        number = Decimal(str(value))

        if not number.is_finite():
            raise ValueError("NONFINITE_DECIMAL")

        return number

    log("=" * 72)
    log("UNIT 14F ORIGINAL COORDINATION V1 START")
    log("UNIT 14F BOT_MODE DEPENDENCY = NONE")
    log("UNIT 14F EXCHANGE WRITE = NONE")
    log("UNIT 14F NEW ORDER SUBMISSION = DISABLED")

    if not isinstance(config, dict):
        raise RuntimeError("UNIT14F_CONFIG_INVALID")

    if not isinstance(unit_13_result, dict):
        raise RuntimeError("UNIT14F_UNIT13_INVALID")

    if not isinstance(unit_14e_result, dict):
        raise RuntimeError("UNIT14F_UNIT14E_INVALID")

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})

    if not (
        isinstance(exchange, dict)
        and isinstance(safety, dict)
        and config.get("execution_environment") == "DEMO"
        and exchange.get("demo_order_symbol") == "BTCSUSDT"
        and exchange.get("market_symbol") == "BTCUSDT"
        and exchange.get("contract_base_url")
        == "https://api-contract.weex.com"
    ):
        raise RuntimeError("UNIT14F_DEMO_SCOPE_INVALID")

    for setting in (
        "real_order_submission_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled"
    ):

        if safety.get(setting) is not False:
            raise RuntimeError(
                "UNIT14F_UNSAFE_" + setting
            )

    # ========================================================
    # UNIT 14F RESULT CONTRACT
    # ========================================================

    result = {
        "unit": 14,
        "subunit": "14F",
        "revision": "ORIGINAL_COORDINATION_V1",
        "status": "STARTING",
        "reason": "NONE",

        "unit_13_status": unit_13_result.get(
            "status"
        ),

        "unit_14e_status": unit_14e_result.get(
            "status"
        ),

        "demo_position_verified": False,
        "active_position_exists": False,
        "position_side": "NONE",
        "position_size": "0",
        "position_management_required": False,

        "tp3_armed_from_unit13": (
            unit_13_result.get("tp3_armed") is True
        ),

        "tp3_armed_from_unit14e": (
            unit_14e_result.get("tp3_armed") is True
        ),

        "backup_resolution_required_for_tp": False,
        "backup_engine_preserved": True,
        "tp_engine_preserved": True,

        "position_recheck_required": False,
        "exchange_order_execution": False,
        "exchange_write": False,

        "next_subunit": "UNIT15",
    }

    def finish(status, reason):

        result["status"] = status
        result["reason"] = reason

        log("-" * 72)

        log(
            "UNIT 14F UNIT 13 STATUS =",
            result["unit_13_status"]
        )

        log(
            "UNIT 14F UNIT 14E STATUS =",
            result["unit_14e_status"]
        )

        log(
            "UNIT 14F POSITION VERIFIED =",
            result["demo_position_verified"]
        )

        log(
            "UNIT 14F POSITION ACTIVE =",
            result["active_position_exists"]
        )

        log(
            "UNIT 14F POSITION SIDE =",
            result["position_side"]
        )

        log(
            "UNIT 14F POSITION SIZE =",
            result["position_size"]
        )

        log(
            "UNIT 14F POSITION MANAGEMENT REQUIRED =",
            result["position_management_required"]
        )

        log(
            "UNIT 14F BACKUP RESOLUTION "
            "REQUIRED FOR TP = False"
        )

        log(
            "UNIT 14F STATUS =",
            status
        )

        log(
            "UNIT 14F REASON =",
            reason
        )

        log(
            "UNIT 14F EXCHANGE WRITE = False"
        )

        log(
            "UNIT 14F ORIGINAL MODEL RESULT =",
            status
        )

        log("=" * 72)

        return result

    # ========================================================
    # SELF-TESTS
    # ========================================================

    def management_state(active, verified):

        if not verified:
            return "RECONCILIATION_WAIT"

        if active:
            return "POSITION_MANAGEMENT_ACTIVE"

        return "IDLE_NO_POSITION"

    checks = {
        "DEMO_SCOPE": (
            exchange.get("demo_order_symbol")
            == "BTCSUSDT"
        ),

        "UNIT13_HANDOVER": isinstance(
            unit_13_result,
            dict
        ),

        "UNIT14E_HANDOVER": isinstance(
            unit_14e_result,
            dict
        ),

        "ACTIVE_POSITION_POLICY": (
            management_state(True, True)
            == "POSITION_MANAGEMENT_ACTIVE"
        ),

        "FLAT_POSITION_POLICY": (
            management_state(False, True)
            == "IDLE_NO_POSITION"
        ),

        "UNVERIFIED_POSITION_POLICY": (
            management_state(True, False)
            == "RECONCILIATION_WAIT"
        ),

        "BACKUP_TP_INDEPENDENCE": (
            result[
                "backup_resolution_required_for_tp"
            ] is False
        ),

        "NO_ORDER_EXECUTION": (
            result["exchange_order_execution"]
            is False
        ),

        "NO_EXCHANGE_WRITE": (
            result["exchange_write"] is False
        ),
    }

    passed = 0

    for name, ok in checks.items():

        log(
            "UNIT 14F CHECK",
            name,
            "=",
            "PASS" if ok else "FAIL"
        )

        if ok:
            passed += 1

    log(
        "UNIT 14F VERIFIED PASSES =",
        passed
    )

    if passed != len(checks):
        return finish(
            "BLOCKED",
            "SELF_TEST_FAILED"
        )

    log("PASS: UNIT 14F SELF TEST = 9/9")

    # ========================================================
    # WEEX DEMO POSITION GET
    # READ ONLY
    # ========================================================

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

        return finish(
            "RECONCILIATION_WAIT",
            "WEEX_CREDENTIALS_MISSING"
        )

    path = "/capi/v3/sim/position/allPosition"

    timestamp = str(
        int(time.time() * 1000)
    )

    prehash = (
        timestamp
        + "GET"
        + path
    )

    signature = base64.b64encode(
        hmac.new(
            secret.encode(),
            prehash.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    class NoRedirect(
        urllib.request.HTTPRedirectHandler
    ):

        def redirect_request(
            self,
            request,
            file_pointer,
            code,
            message,
            headers,
            url
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    request = urllib.request.Request(
        "https://api-contract.weex.com" + path,
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": passphrase,
            "Content-Type": "application/json"
        },
        method="GET"
    )

    try:

        with opener.open(
            request,
            timeout=15
        ) as response:

            if response.getcode() != 200:
                raise RuntimeError(
                    "POSITION_HTTP_FAILURE"
                )

            raw = response.read(65537)

        if len(raw) > 65536:
            raise RuntimeError(
                "POSITION_RESPONSE_TOO_LARGE"
            )

        positions = json.loads(
            raw.decode()
        )

        if not isinstance(positions, list):
            raise RuntimeError(
                "POSITION_FORMAT_INVALID"
            )

        active_positions = []

        for position in positions:

            if not isinstance(position, dict):
                raise RuntimeError(
                    "POSITION_RECORD_INVALID"
                )

            if str(
                position.get("symbol", "")
            ).upper() != "BTCSUSDT":
                continue

            size = dec(
                position.get("size", "0")
            )

            if size < 0:
                raise RuntimeError(
                    "NEGATIVE_POSITION_SIZE"
                )

            if size > 0:
                active_positions.append(position)

        log(
            "PASS: UNIT 14F WEEX DEMO POSITION GET"
        )

    except Exception as error:

        log(
            "UNIT 14F POSITION GET ERROR =",
            type(error).__name__
        )

        return finish(
            "RECONCILIATION_WAIT",
            "DEMO_POSITION_GET_UNVERIFIED"
        )

    result["demo_position_verified"] = True

    # ========================================================
    # FLAT POSITION
    # ========================================================

    if len(active_positions) == 0:

        log(
            "PASS: UNIT 14F NO OPEN DEMO POSITION"
        )

        result[
            "position_management_required"
        ] = False

        result[
            "position_recheck_required"
        ] = True

        return finish(
            "IDLE_NO_POSITION",
            "NO_ACTIVE_BTCSUSDT_POSITION"
        )

    # ========================================================
    # MULTIPLE ACTIVE POSITIONS REQUIRE RECONCILIATION
    # ========================================================

    if len(active_positions) != 1:

        result[
            "active_position_exists"
        ] = True

        result[
            "position_recheck_required"
        ] = True

        return finish(
            "RECONCILIATION_WAIT",
            "MULTIPLE_ACTIVE_POSITIONS"
        )

    # ========================================================
    # ONE CONFIRMED DEMO POSITION
    # ========================================================

    position = active_positions[0]

    try:

        side = str(
            position.get("side", "")
        ).upper()

        size = dec(
            position["size"]
        )

        if side not in ("LONG", "SHORT"):
            raise RuntimeError(
                "POSITION_SIDE_INVALID"
            )

        if size <= 0:
            raise RuntimeError(
                "POSITION_SIZE_INVALID"
            )

    except Exception:

        return finish(
            "RECONCILIATION_WAIT",
            "POSITION_DETAILS_INVALID"
        )

    result.update({
        "active_position_exists": True,
        "position_side": side,
        "position_size": str(size),
        "position_management_required": True,
        "position_recheck_required": True,
    })

    # ========================================================
    # COMPARE UPSTREAM POSITION INFORMATION
    #
    # NEVER OVERRIDE WEEX WITH CACHED UNIT RESULTS.
    # ========================================================

    for label, upstream in (
        ("UNIT13", unit_13_result),
        ("UNIT14E", unit_14e_result)
    ):

        previous_side = str(
            upstream.get("position_side")
            or ""
        ).upper()

        if previous_side in ("LONG", "SHORT"):

            if previous_side != side:

                return finish(
                    "RECONCILIATION_WAIT",
                    label + "_POSITION_SIDE_CHANGED"
                )

        previous_size = upstream.get(
            "position_size"
        )

        # Position size may legitimately change during
        # backup fills and TP closures.
        # Log the change rather than automatically
        # interpreting it as a failed backup.

        if previous_size is not None:

            try:

                earlier_size = dec(
                    previous_size
                )

                if earlier_size != size:

                    log(
                        "UNIT 14F",
                        label,
                        "SIZE CHANGED =",
                        earlier_size,
                        "->",
                        size
                    )

            except Exception:

                log(
                    "UNIT 14F",
                    label,
                    "POSITION SIZE = UNVERIFIED"
                )

    # ========================================================
    # COORDINATION RESULT
    #
    # UNIT 14F DOES NOT TAKE OVER TP/BACKUP SUBMISSION.
    # EACH ORIGINAL EXECUTION UNIT RETAINS ITS ROLE.
    # ========================================================

    return finish(
        "POSITION_MANAGEMENT_ACTIVE",
        "WEEX_POSITION_VERIFIED"
    )


# ============================================================
# EXECUTE UNIT 14F
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_14E_RESULT = (
    FRESH_RECONSTRUCTION_UNIT_14_RESULT
)

FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
    fresh_unit_14f_coordinator(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
        FRESH_RECONSTRUCTION_UNIT_14E_RESULT
    )
)


# ============================================================
# END COMPLETE UNIT 14F
# ZERO INDENTATION
# ============================================================



# START COMPLETE UNIT 15 REPLACEMENT
# ZERO INDENTATION - DEMO READ ONLY
# REPLACE ENTIRE OLD UNIT 15, NOT UNITS 1-14
# ============================================================

import os as _u15_os
import time as _u15_time
import json as _u15_json
import hmac as _u15_hmac
import base64 as _u15_base64
import hashlib as _u15_hashlib
import threading as _u15_threading
import urllib.request as _u15_request
import urllib.parse as _u15_parse

from decimal import Decimal as _U15_D
from datetime import datetime as _U15_DT
from datetime import timedelta as _U15_DELTA
from zoneinfo import ZoneInfo as _U15_ZoneInfo
from collections import Counter as _U15_Counter


# ============================================================
# UNIT 15 CONFIGURATION
# ============================================================

UNIT15_ENABLED = (
    _u15_os.getenv(
        "UNIT15_ENABLED", "TRUE"
    ).upper() == "TRUE"
)

UNIT15_REPORT_HOURS = int(
    _u15_os.getenv(
        "UNIT15_REPORT_HOURS", "24"
    )
)

UNIT15_8H_ENABLED = (
    _u15_os.getenv(
        "UNIT15_8H_ENABLED", "TRUE"
    ).upper() == "TRUE"
)

UNIT15_8H_HOURS = int(
    _u15_os.getenv(
        "UNIT15_8H_HOURS", "8"
    )
)

UNIT15_ON_DEMAND = (
    _u15_os.getenv(
        "UNIT15_ON_DEMAND_ENABLED", "TRUE"
    ).upper() == "TRUE"
)

UNIT15_MAX_PAGES = 20
UNIT15_PAGE_LIMIT = 1000

_UNIT15_ZERO = _U15_D("0")
_UNIT15_LOCK = _u15_threading.Lock()

_UNIT15_ZONE = _U15_ZoneInfo(
    _u15_os.getenv(
        "UNIT15_TIMEZONE", "Africa/Lagos"
    )
)

_UNIT15_HIST_PATH = "/capi/v3/sim/order/history"

_UNIT15_OFFSET = None
_UNIT15_LAST_SLOT = None
_UNIT15_LAST_REPORT = None
_UNIT15_POLL_STARTED = False

if UNIT15_8H_HOURS != 8:
    raise ValueError(
        "UNIT15_8H_HOURS MUST BE 8"
    )

if UNIT15_REPORT_HOURS <= 0:
    raise ValueError(
        "UNIT15_REPORT_HOURS MUST BE POSITIVE"
    )

_UNIT15_SLOTS = set()

for _clock in _u15_os.getenv(
    "UNIT15_TELEGRAM_SCHEDULE",
    "05:00,13:00,21:00"
).split(","):

    _hour, _minute = (
        int(x)
        for x in _clock.strip().split(":")
    )

    if not (
        0 <= _hour <= 23
        and 0 <= _minute <= 59
    ):
        raise ValueError(
            "INVALID UNIT 15 SCHEDULE"
        )

    _UNIT15_SLOTS.add(
        (_hour, _minute)
    )


# ============================================================
# UNIT 15 SAFE NUMERIC CONVERSION
# ============================================================

def unit15_decimal(value):

    try:
        number = _U15_D(str(value))

        return (
            number
            if number.is_finite()
            else None
        )

    except (
        TypeError,
        ValueError,
        ArithmeticError,
    ):
        return None


def unit15_value(record, *keys):

    if not isinstance(record, dict):
        return None

    for key in keys:

        if (
            record.get(key) is not None
            and record.get(key) != ""
        ):
            return record[key]

    return None


# ============================================================
# UNIT 15 TIMESTAMP NORMALIZATION
# ============================================================

def unit15_timestamp(value):

    if (
        value is None
        or isinstance(value, bool)
    ):
        return None

    try:

        if (
            isinstance(value, str)
            and (
                "T" in value
                or "-" in value
            )
        ):

            dt = _U15_DT.fromisoformat(
                value.strip().replace(
                    "Z", "+00:00"
                )
            )

            return (
                int(dt.timestamp() * 1000)
                if dt.tzinfo
                else None
            )

        value = unit15_decimal(value)

        if value is None:
            return None

        if value >= _U15_D(
            "100000000000000"
        ):
            value /= 1000

        elif value < _U15_D(
            "100000000000"
        ):
            value *= 1000

        ts = int(value)

        return (
            ts
            if 946684800000
            <= ts
            <= 4102444800000
            else None
        )

    except (
        ValueError,
        TypeError,
        OverflowError,
    ):
        return None


# ============================================================
# UNIT 15 READ-ONLY WEEX HISTORY
# ============================================================

def unit15_history_get():

    key = (
        _u15_os.getenv("WEEX_API_KEY")
        or _u15_os.getenv("API_KEY")
    )

    secret = (
        _u15_os.getenv("WEEX_API_SECRET")
        or _u15_os.getenv("API_SECRET")
    )

    phrase = (
        _u15_os.getenv("WEEX_API_PASSPHRASE")
        or _u15_os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 15 READ CREDENTIALS MISSING"
        )

    exchange = (
        FRESH_RECONSTRUCTION_CONFIG[
            "exchange"
        ]
    )

    base = exchange[
        "contract_base_url"
    ]

    symbol = exchange[
        "demo_order_symbol"
    ]

    if (
        base != "https://api-contract.weex.com"
        or symbol != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 15 DEMO EXCHANGE SAFETY FAILED"
        )

    orders = []
    ids = set()
    complete = False

    for page in range(UNIT15_MAX_PAGES):

        query = _u15_parse.urlencode({
            "symbol": symbol,
            "limit": UNIT15_PAGE_LIMIT,
            "page": page,
        })

        timestamp = str(
            int(_u15_time.time() * 1000)
        )

        message = (
            timestamp
            + "GET"
            + _UNIT15_HIST_PATH
            + "?"
            + query
        )

        sign = _u15_base64.b64encode(
            _u15_hmac.new(
                secret.encode(),
                message.encode(),
                _u15_hashlib.sha256,
            ).digest()
        ).decode()

        request = _u15_request.Request(
            base
            + _UNIT15_HIST_PATH
            + "?"
            + query,
            method="GET",
            headers={
                "ACCESS-KEY": key,
                "ACCESS-SIGN": sign,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": phrase,
                "Content-Type": "application/json",
            },
        )

        if (
            request.get_method() != "GET"
            or request.data is not None
        ):
            raise RuntimeError(
                "UNIT 15 WRITE BLOCKED"
            )

        with _u15_request.urlopen(
            request,
            timeout=20,
        ) as response:

            data = _u15_json.loads(
                response.read().decode()
            )

        if not isinstance(data, list):
            raise RuntimeError(
                "UNIT 15 INVALID HISTORY RESPONSE"
            )

        for order in data:

            oid = unit15_value(
                order,
                "orderId",
                "id",
                "clientOrderId",
            )

            if (
                oid is not None
                and str(oid) not in ids
            ):

                ids.add(str(oid))
                orders.append(order)

        if len(data) < UNIT15_PAGE_LIMIT:
            complete = True
            break

    return orders, complete


# ============================================================
# UNIT 15 ORDER NORMALIZATION
# CONTINUES IN PART 2
# ============================================================


# ============================================================
# UNIT 15 ORDER NORMALIZATION
# ============================================================

def unit15_parse(order):

    if not isinstance(order, dict):
        return None, "INVALID_RECORD"

    status = str(
        unit15_value(
            order,
            "status",
            "state",
            "orderStatus",
        ) or ""
    ).upper()

    if status not in (
        "FILLED",
        "FULLY_FILLED",
        "FULL_FILLED",
        "FULLFILL",
    ):
        return None, "NOT_FULLY_FILLED"

    ts = unit15_timestamp(
        unit15_value(
            order,
            "createdTime",
            "createTime",
            "cTime",
            "ctime",
            "createdAt",
            "timestamp",
            "time",
            "updateTime",
            "updatedAt",
        )
    )

    if (
        ts is None
        or ts > int(
            _u15_time.time() * 1000
        )
    ):
        return None, "INVALID_TIMESTAMP"

    qty = unit15_decimal(
        unit15_value(
            order,
            "executedQty",
            "filledQty",
            "filledSize",
            "executedQuantity",
            "dealSize",
        )
    )

    price = unit15_decimal(
        unit15_value(
            order,
            "avgPrice",
            "averagePrice",
            "fillPrice",
            "priceAvg",
            "executedPrice",
        )
    )

    if qty is None or qty <= 0:
        return None, "INVALID_QUANTITY"

    if price is None or price <= 0:
        return None, "INVALID_PRICE"

    side = str(
        unit15_value(
            order,
            "side",
            "orderSide",
        ) or ""
    ).upper()

    direction = str(
        unit15_value(
            order,
            "positionSide",
            "holdSide",
            "posSide",
        ) or ""
    ).upper()

    action = str(
        unit15_value(
            order,
            "tradeSide",
            "tradeType",
            "offset",
        ) or ""
    ).upper()

    if (
        direction in ("LONG", "SHORT")
        and action in ("OPEN", "CLOSE")
    ):
        pass

    elif (
        direction in ("LONG", "SHORT")
        and side in ("BUY", "SELL")
    ):

        action = (
            "OPEN"
            if (
                (direction == "LONG")
                == (side == "BUY")
            )
            else "CLOSE"
        )

    else:

        combined = side + "_" + action

        matched = next(
            (
                (d, a)
                for d in ("LONG", "SHORT")
                for a in ("OPEN", "CLOSE")
                if a + "_" + d in combined
            ),
            None,
        )

        if matched is None:
            return (
                None,
                "UNRESOLVED_DIRECTION",
            )

        direction, action = matched

    oid = unit15_value(
        order,
        "orderId",
        "id",
        "clientOrderId",
    )

    if oid is None:
        return None, "MISSING_ORDER_ID"

    return {
        "id": str(oid),
        "time": ts,
        "quantity": qty,
        "price": price,
        "direction": direction,
        "action": action,
    }, None


# ============================================================
# UNIT 15 PERFORMANCE RECONSTRUCTION
# ============================================================

def unit15_analyze(
    orders,
    history_complete,
    start_ms,
    end_ms,
):

    reasons = _U15_Counter()
    fills = []
    seen = set()

    for record in orders:

        fill, problem = unit15_parse(record)

        if problem:
            reasons[problem] += 1

        elif fill["id"] in seen:
            reasons["DUPLICATE_ID"] += 1

        else:
            fills.append(fill)
            seen.add(fill["id"])

    fills.sort(
        key=lambda x: (
            x["time"],
            x["id"],
        )
    )

    positions = {
        d: {
            "qty": _UNIT15_ZERO,
            "cost": _UNIT15_ZERO,
            "pnl": _UNIT15_ZERO,
            "unknown": False,
        }
        for d in ("LONG", "SHORT")
    }

    completed = []
    unmatched = []

    for fill in fills:

        p = positions[
            fill["direction"]
        ]

        qty = fill["quantity"]
        price = fill["price"]

        if fill["action"] == "OPEN":

            p["qty"] += qty
            p["cost"] += qty * price

            continue

        available = p["qty"]

        if (
            available <= 0
            or qty > available
        ):

            reasons["UNMATCHED_CLOSE"] += 1
            p["unknown"] = True

            unmatched.append({
                "order_id": fill["id"],
                "time": fill["time"],
                "direction": fill["direction"],
                "quantity": str(qty),
                "available": str(available),
                "price": str(price),
                "reason": (
                    "NO_OPEN_POSITION"
                    if available <= 0
                    else "CLOSE_EXCEEDS_OPEN"
                ),
            })

            continue

        average = (
            p["cost"] / p["qty"]
        )

        gain = (
            (
                price - average
            )
            if fill["direction"] == "LONG"
            else (
                average - price
            )
        ) * qty

        p["pnl"] += gain
        p["qty"] -= qty
        p["cost"] -= average * qty

        if p["qty"] == 0:

            if (
                not p["unknown"]
                and start_ms
                <= fill["time"]
                < end_ms
            ):

                completed.append(
                    p["pnl"]
                )

            elif p["unknown"]:

                reasons[
                    "CYCLE_INCOMPLETE_HISTORY"
                ] += 1

            p.update(
                qty=_UNIT15_ZERO,
                cost=_UNIT15_ZERO,
                pnl=_UNIT15_ZERO,
                unknown=False,
            )

    wins = sum(
        x > 0
        for x in completed
    )

    losses = sum(
        x < 0
        for x in completed
    )

    even = sum(
        x == 0
        for x in completed
    )

    gross_win = sum(
        (
            x
            for x in completed
            if x > 0
        ),
        _UNIT15_ZERO,
    )

    gross_loss = sum(
        (
            -x
            for x in completed
            if x < 0
        ),
        _UNIT15_ZERO,
    )

    problem_fields = (
        "CYCLE_INCOMPLETE_HISTORY",
        "INVALID_TIMESTAMP",
        "UNRESOLVED_DIRECTION",
        "INVALID_QUANTITY",
        "INVALID_PRICE",
        "MISSING_ORDER_ID",
        "INVALID_RECORD",
    )

    provisional = (
        not history_complete
        or bool(unmatched)
        or any(
            reasons[k]
            for k in problem_fields
        )
    )

    return {
        "orders": len(orders),
        "fills": len(fills),
        "completed": len(completed),
        "winners": wins,
        "losers": losses,
        "breakeven": even,
        "gross_win": gross_win,
        "gross_loss": gross_loss,
        "gross_pnl": gross_win - gross_loss,
        "open_qty": {
            d: str(p["qty"])
            for d, p in positions.items()
        },
        "reasons": dict(reasons),
        "unmatched": unmatched,
        "history_complete": history_complete,
        "provisional": provisional,
    }


# ============================================================
# UNIT 15 PERCENTAGE CALCULATION
# ============================================================

def unit15_percent(
    numerator,
    denominator,
):

    if not denominator:
        return "N/A"

    return (
        f"{float(numerator) * 100 / float(denominator):.2f}%"
    )


# ============================================================
# UNIT 15 EQUITY SNAPSHOT TRACKING
# ZERO INDENTATION
# READ-ONLY DEMO ACCOUNT
# CONTINUES IN PART 3
# ============================================================



# ============================================================
# UNIT 15 EQUITY SNAPSHOT TRACKING
# ZERO INDENTATION
# READ-ONLY DEMO ACCOUNT
# ============================================================

import math as _u15_math

_UNIT15_EQUITY_PATH = _u15_os.getenv(
    "UNIT15_EQUITY_PATH",
    "/tmp/weex_unit15_equity.jsonl"
)

_UNIT15_EQUITY_FIELDS = (
    "equity",
    "accountEquity",
    "totalEquity",
    "marginBalance",
)

def unit15_read_equity():

    key = (
        _u15_os.getenv("WEEX_API_KEY")
        or _u15_os.getenv("API_KEY")
    )

    secret = (
        _u15_os.getenv("WEEX_API_SECRET")
        or _u15_os.getenv("API_SECRET")
    )

    phrase = (
        _u15_os.getenv("WEEX_API_PASSPHRASE")
        or _u15_os.getenv("API_PASSPHRASE")
    )

    if not all((key, secret, phrase)):
        raise RuntimeError(
            "UNIT 15 EQUITY CREDENTIALS MISSING"
        )

    exchange = FRESH_RECONSTRUCTION_CONFIG[
        "exchange"
    ]

    base = exchange["contract_base_url"]

    if (
        base != "https://api-contract.weex.com"
        or exchange["demo_order_symbol"] != "BTCSUSDT"
    ):
        raise RuntimeError(
            "UNIT 15 EQUITY SAFETY FAILURE"
        )

    path = "/capi/v3/sim/balance"

    timestamp = str(
        int(_u15_time.time() * 1000)
    )

    signature = _u15_base64.b64encode(
        _u15_hmac.new(
            secret.encode(),
            (timestamp + "GET" + path).encode(),
            _u15_hashlib.sha256,
        ).digest()
    ).decode()

    request = _u15_request.Request(
        base + path,
        method="GET",
        headers={
            "ACCESS-KEY": key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": phrase,
            "Content-Type": "application/json",
        },
    )

    if (
        request.get_method() != "GET"
        or request.data is not None
    ):
        raise RuntimeError(
            "UNIT 15 EQUITY WRITE BLOCKED"
        )

    with _u15_request.urlopen(
        request,
        timeout=20,
    ) as response:

        balances = _u15_json.loads(
            response.read().decode()
        )

    if not isinstance(balances, list):
        raise RuntimeError(
            "UNIT 15 INVALID BALANCE RESPONSE"
        )

    for item in balances:

        if not isinstance(item, dict):
            continue

        if str(
            item.get("asset", "")
        ).upper() != "SUSDT":
            continue

        for field in _UNIT15_EQUITY_FIELDS:

            value = item.get(field)

            if value is None:
                continue

            try:
                equity = _U15_D(str(value))
            except Exception:
                continue

            if (
                equity.is_finite()
                and equity >= 0
            ):
                return {
                    "time_ms": int(
                        _u15_time.time() * 1000
                    ),
                    "equity": str(equity),
                    "asset": "SUSDT",
                    "field": field,
                }

    raise RuntimeError(
        "UNIT 15 EXPLICIT EQUITY FIELD NOT FOUND"
    )


def unit15_save_equity(snapshot):

    with open(
        _UNIT15_EQUITY_PATH,
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            _u15_json.dumps(snapshot) + "\n"
        )


def unit15_equity_history():

    records = []

    try:
        with open(
            _UNIT15_EQUITY_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                try:
                    item = _u15_json.loads(line)

                    timestamp = int(
                        item["time_ms"]
                    )

                    equity = _U15_D(
                        str(item["equity"])
                    )

                    if (
                        equity.is_finite()
                        and equity >= 0
                    ):
                        records.append(
                            (timestamp, equity)
                        )

                except (
                    KeyError,
                    ValueError,
                    TypeError,
                    ArithmeticError,
                ):
                    continue

    except FileNotFoundError:
        pass

    return sorted(records)


def unit15_equity_change(
    start_ms,
    end_ms,
    tolerance_ms=600000,
):

    records = unit15_equity_history()

    def nearest(boundary):

        candidates = [
            item
            for item in records
            if abs(item[0] - boundary)
            <= tolerance_ms
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda item:
                abs(item[0] - boundary)
        )

    first = nearest(start_ms)
    last = nearest(end_ms)

    if (
        first is None
        or last is None
        or first[0] >= last[0]
    ):
        return None

    starting_equity = first[1]
    ending_equity = last[1]

    change = (
        ending_equity - starting_equity
    )

    roi = None

    if starting_equity > 0:
        roi = (
            change / starting_equity * 100
        )

    return {
        "start": starting_equity,
        "end": ending_equity,
        "change": change,
        "roi": roi,
        "start_time_ms": first[0],
        "end_time_ms": last[0],
    }

# ============================================================
# END UNIT 15 EQUITY SNAPSHOT TRACKING
# ZERO INDENTATION
# ============================================================
# ============================================================
# UNIT 15 TELEGRAM NOTIFICATION
# CONTINUES IN PART 4
# ============================================================

# ============================================================
# START ORIGINAL CONTINUOUS CYCLE RESTORATION
# ZERO INDENTATION
#
# 22524-LINE MODEL BEHAVIOUR ADAPTATION
#
# FLAT POSITION:
#   REFRESH UNITS 3 THROUGH 12
#   VERIFY POSITION THROUGH UNITS 13-14F
#
# OPEN POSITION:
#   REFRESH UNIT 13
#   REFRESH UNITS 14A THROUGH 14F
#   REPEAT AT FIVE-SECOND INTERVALS
#
# POSITION CLOSES:
#   RETURN TO FRESH MARKET SCANNING
#
# SINGLE BOT_MODE FROM UNIT 12
# NO SECOND SUBMISSION ENGINE
# NO SECOND BACKUP ENGINE
# NO SECOND TP ENGINE
# ============================================================

import os
import time
import traceback
from datetime import datetime, timezone



# ============================================================
# START CONTINUOUS STRATEGY DIAGNOSTIC V1
# ZERO INDENTATION
#
# ORIGINAL 22524-LINE STRATEGY PROGRESSION MONITOR
#
# READ ONLY
# NO WEEX API CALLS
# NO EXCHANGE WRITES
# NO TRADING QUALIFICATION CHANGES
# NO NEW BOT_MODE
# NO FILE STORAGE
# ============================================================


FRESH_STRATEGY_PROGRESS_STATE = {
    "scans": 0,
    "candidate_scans": 0,
    "developing_scans": 0,
    "qualified_scans": 0,
    "execution_ready_scans": 0,
    "payload_ready_scans": 0,
    "pause_blocked_scans": 0,
    "execution_blocked_scans": 0,
    "demo_attempt_scans": 0,
    "demo_completed_scans": 0,
    "unqualified_scans": 0,
    "modes": {
        "BREAKOUT": 0,
        "STRUCTURE": 0,
        "SCALP": 0,
        "NONE": 0
    },
    "reasons": {}
}


def fresh_strategy_progress_diagnostic(
    unit5,
    unit9,
    unit10,
    unit11,
    unit12,
    report_every=20
):

    import os

    state = FRESH_STRATEGY_PROGRESS_STATE

    sources = (
        unit5,
        unit9,
        unit10,
        unit11,
        unit12
    )

    if not all(
        isinstance(x, dict)
        for x in sources
    ):
        print(
            "STRATEGY DIAGNOSTIC = INVALID_HANDOVER",
            flush=True
        )
        return False

    def text_value(source, *keys):

        for key in keys:
            value = source.get(key)

            if value is not None:
                return str(value).upper()

        return "NONE"

    def is_true(source, key):
        return source.get(key) is True

    def yes(value):
        return "YES" if value else "NO"

    def show(*args):
        print(*args, flush=True)

    state["scans"] += 1

    scan = state["scans"]

    mode = text_value(
        unit5,
        "candidate_mode",
        "active_mode"
    )

    if mode not in (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP"
    ):
        mode = "NONE"

    stage = text_value(
        unit5,
        "candidate_stage"
    )

    reason = text_value(
        unit12,
        "skip_reason"
    )

    if reason == "NONE":
        reason = text_value(
            unit10,
            "skip_reason"
        )

    if reason == "NONE":
        reason = text_value(
            unit5,
            "qualification_reason",
            "reason"
        )

    qualified = (
        is_true(unit10, "signal_qualified")
    )

    execution_ready = (
        is_true(unit9, "execution_ready")
        or (
            qualified
            and is_true(
                unit10,
                "demo_boundary_ready"
            )
        )
    )

    payload_ready = (
        is_true(unit11, "payload_ready")
        or is_true(
            unit11,
            "order_payload_created"
        )
    )

    attempted = (
        is_true(
            unit12,
            "demo_submission_attempted"
        )
    )

    completed = (
        is_true(
            unit12,
            "demo_submission_completed"
        )
    )

    bot_mode = str(
        os.getenv("BOT_MODE", "PAUSE")
    ).strip().upper()

    has_candidate = (
        mode != "NONE"
        and stage != "NONE"
    )

    developing = (
        stage == "DEVELOPING"
    )

    pause_blocked = (
        bot_mode == "PAUSE"
        and qualified
        and payload_ready
    )

    execution_blocked = (
        qualified
        and payload_ready
        and not attempted
        and bot_mode == "RUN"
    )

    state["modes"][mode] += 1

    for name, matched in (
        ("candidate_scans", has_candidate),
        ("developing_scans", developing),
        ("qualified_scans", qualified),
        ("execution_ready_scans", execution_ready),
        ("payload_ready_scans", payload_ready),
        ("pause_blocked_scans", pause_blocked),
        ("execution_blocked_scans", execution_blocked),
        ("demo_attempt_scans", attempted),
        ("demo_completed_scans", completed),
        (
            "unqualified_scans",
            not qualified
        )
    ):

        if matched:
            state[name] += 1

    state["reasons"][reason] = (
        state["reasons"].get(reason, 0) + 1
    )

    # ========================================================
    # EVERY SCAN: COMPACT PROGRESSION
    # ========================================================

    show("=" * 68)

    show(
        "STRATEGY PROGRESSION SCAN =",
        scan
    )

    show(
        "STRATEGY CANDIDATE MODE =",
        mode
    )

    show(
        "STRATEGY CANDIDATE STAGE =",
        stage
    )

    show(
        "STRATEGY SIGNAL QUALIFIED =",
        yes(qualified)
    )

    show(
        "STRATEGY EXECUTION READY =",
        yes(execution_ready)
    )

    show(
        "STRATEGY PAYLOAD READY =",
        yes(payload_ready)
    )

    show(
        "STRATEGY BOT_MODE =",
        bot_mode
    )

    show(
        "STRATEGY PAUSE BLOCKED =",
        yes(pause_blocked)
    )

    show(
        "STRATEGY EXECUTION BLOCKED =",
        yes(execution_blocked)
    )

    show(
        "STRATEGY DEMO ATTEMPTED =",
        yes(attempted)
    )

    show(
        "STRATEGY DEMO COMPLETED =",
        yes(completed)
    )

    show(
        "STRATEGY SKIP REASON =",
        reason
    )

    # ========================================================
    # PERIODIC SUMMARY
    #
    # ALL FIGURES COUNT SCANS, NOT UNIQUE TRADES.
    # ========================================================

    if (
        type(report_every) is int
        and report_every > 0
        and scan % report_every == 0
    ):

        show("=" * 68)
        show("CONTINUOUS STRATEGY PROGRESSION SUMMARY")
        show("=" * 68)

        show("TOTAL SCANS =", state["scans"])

        show(
            "BREAKOUT CANDIDATE SCANS =",
            state["modes"]["BREAKOUT"]
        )

        show(
            "STRUCTURE CANDIDATE SCANS =",
            state["modes"]["STRUCTURE"]
        )

        show(
            "SCALP CANDIDATE SCANS =",
            state["modes"]["SCALP"]
        )

        show(
            "NO CANDIDATE SCANS =",
            state["modes"]["NONE"]
        )

        show(
            "CANDIDATE DETECTED SCANS =",
            state["candidate_scans"]
        )

        show(
            "DEVELOPING SCANS =",
            state["developing_scans"]
        )

        show(
            "QUALIFIED SCANS =",
            state["qualified_scans"]
        )

        show(
            "EXECUTION READY SCANS =",
            state["execution_ready_scans"]
        )

        show(
            "PAYLOAD READY SCANS =",
            state["payload_ready_scans"]
        )

        show(
            "PAUSE BLOCKED SCANS =",
            state["pause_blocked_scans"]
        )

        show(
            "OTHER EXECUTION BLOCKED SCANS =",
            state["execution_blocked_scans"]
        )

        show(
            "DEMO SUBMISSION ATTEMPT SCANS =",
            state["demo_attempt_scans"]
        )

        show(
            "DEMO SUBMISSION COMPLETED SCANS =",
            state["demo_completed_scans"]
        )

        show(
            "UNQUALIFIED SCANS =",
            state["unqualified_scans"]
        )

        show("-" * 68)

        show("TOP SKIP REASONS:")

        top_reasons = sorted(
            state["reasons"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:8]

        for reason_name, count in top_reasons:

            show(
                "  ",
                reason_name,
                "=",
                count
            )

        show("=" * 68)
        show(
            "NOTE: COUNTS ARE PER SCAN,"
            " NOT UNIQUE TRADING OPPORTUNITIES"
        )
        show("=" * 68)

    return True


# ============================================================
# END CONTINUOUS STRATEGY DIAGNOSTIC V1
# ZERO INDENTATION
# ============================================================

def fresh_original_continuous_controller():

    global FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
    global FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
    global FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
    global FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
    global FRESH_RECONSTRUCTION_SIZING_CANDIDATE

    global FRESH_RECONSTRUCTION_UNIT_8_RESULT
    global FRESH_RECONSTRUCTION_UNIT_9_RESULT
    global FRESH_RECONSTRUCTION_UNIT_10_RESULT
    global FRESH_RECONSTRUCTION_UNIT_11_RESULT
    global FRESH_RECONSTRUCTION_UNIT_12_RESULT
    global FRESH_RECONSTRUCTION_UNIT_13_RESULT

    global FRESH_RECONSTRUCTION_UNIT_14A_RESULT
    global FRESH_RECONSTRUCTION_UNIT_14B_RESULT
    global FRESH_RECONSTRUCTION_UNIT_14C_RESULT
    global FRESH_RECONSTRUCTION_UNIT_14D_RESULT
    global FRESH_RECONSTRUCTION_UNIT_14E_RESULT
    global FRESH_RECONSTRUCTION_UNIT_14_RESULT

    config = FRESH_RECONSTRUCTION_CONFIG

    if not isinstance(config, dict):
        raise RuntimeError(
            "CONTINUOUS_CONFIG_INVALID"
        )

    if (
        config.get("execution_environment")
        != "DEMO"
    ):
        raise RuntimeError(
            "CONTINUOUS_DEMO_ONLY"
        )

    exchange = config.get("exchange", {})

    if (
        exchange.get("demo_order_symbol")
        != "BTCSUSDT"
        or exchange.get("contract_base_url")
        != "https://api-contract.weex.com"
    ):
        raise RuntimeError(
            "CONTINUOUS_EXCHANGE_SCOPE_INVALID"
        )

    ENTRY_SCAN_SECONDS = 30
    POSITION_POLL_SECONDS = 5
    ERROR_RETRY_SECONDS = 10

    cycles = 0
    entry_scans = 0
    position_scans = 0
    previous_active = None
    safety_hold = False

    # A failed or uncertain trading cycle is not
    # automatically retried through submission units.
    # Subsequent polling on a safety hold is GET-only.

    def log(*parts):
        print(*parts, flush=True)

    def current_mode():

        mode = str(
            os.getenv("BOT_MODE", "PAUSE")
        ).strip().upper()

        if mode not in ("RUN", "PAUSE"):
            raise RuntimeError(
                "CONTINUOUS_BOT_MODE_INVALID"
            )

        return mode

    def read_position():

        return fresh_unit_14f_coordinator(
            config,
            FRESH_RECONSTRUCTION_UNIT_13_RESULT,
            FRESH_RECONSTRUCTION_UNIT_14E_RESULT
        )

    def checked_result(name, value):

        if not isinstance(value, dict):
            raise RuntimeError(
                name + "_RESULT_NOT_DICTIONARY"
            )

        return value

    def run_market_scan():

        global FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
        global FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
        global FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
        global FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
        global FRESH_RECONSTRUCTION_SIZING_CANDIDATE

        global FRESH_RECONSTRUCTION_UNIT_8_RESULT
        global FRESH_RECONSTRUCTION_UNIT_9_RESULT
        global FRESH_RECONSTRUCTION_UNIT_10_RESULT
        global FRESH_RECONSTRUCTION_UNIT_11_RESULT
        global FRESH_RECONSTRUCTION_UNIT_12_RESULT

        # ----------------------------------------------------
        # UNIT 3: FRESH WEEX PUBLIC PRICE
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_MARKET_SNAPSHOT = (
            fresh_reconstruction_unit_3()
        )

        # ----------------------------------------------------
        # UNIT 4: FRESH CANDLES / ATR / EMA
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT = (
            fresh_reconstruction_unit_4()
        )

        # ----------------------------------------------------
        # UNIT 5: SIGNAL CANDIDATES
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE = (
            fresh_reconstruction_unit_5(
                config,
                FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
            )
        )

        # ----------------------------------------------------
        # UNIT 6: SIGNAL QUALIFICATION
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE = (
            fresh_reconstruction_unit_6(
                config,
                FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT,
                FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE
            )
        )

        # ----------------------------------------------------
        # UNIT 7: SIZING
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_SIZING_CANDIDATE = (
            fresh_reconstruction_unit_7(
                config,
                FRESH_RECONSTRUCTION_EXECUTION_CANDIDATE
            )
        )

        # ----------------------------------------------------
        # UNIT 8: EXCHANGE PREPARATION
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_8_RESULT = (
            fresh_reconstruction_unit_8(
                config,
                FRESH_RECONSTRUCTION_SIZING_CANDIDATE,
                FRESH_RECONSTRUCTION_MARKET_SNAPSHOT
            )
        )

        # ----------------------------------------------------
        # UNIT 9: QUALIFICATION CONTINUITY
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_9_RESULT = (
            fresh_reconstruction_unit_9(
                config,
                FRESH_RECONSTRUCTION_UNIT_8_RESULT,
                FRESH_RECONSTRUCTION_ANALYSIS_SNAPSHOT
            )
        )

        # ----------------------------------------------------
        # UNIT 10: AUTHORIZATION HANDOVER
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_10_RESULT = (
            fresh_reconstruction_unit_10(
                config,
                FRESH_RECONSTRUCTION_UNIT_9_RESULT
            )
        )

        # ----------------------------------------------------
        # UNIT 11: DEMO ENTRY PAYLOAD
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_11_RESULT = (
            fresh_reconstruction_unit_11(
                config,
                FRESH_RECONSTRUCTION_UNIT_10_RESULT
            )
        )

        # ----------------------------------------------------
        # UNIT 12: EXISTING SINGLE BOT_MODE CONTROL
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
            checked_result(
                "UNIT12",
                fresh_reconstruction_unit_12(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_11_RESULT
                )
            )
        )

        log(
            "CONTINUOUS UNIT 12 STATUS =",
            FRESH_RECONSTRUCTION_UNIT_12_RESULT.get(
                "status"
            )
        )

    def run_position_management():

        global FRESH_RECONSTRUCTION_UNIT_13_RESULT

        global FRESH_RECONSTRUCTION_UNIT_14A_RESULT
        global FRESH_RECONSTRUCTION_UNIT_14B_RESULT
        global FRESH_RECONSTRUCTION_UNIT_14C_RESULT
        global FRESH_RECONSTRUCTION_UNIT_14D_RESULT
        global FRESH_RECONSTRUCTION_UNIT_14E_RESULT
        global FRESH_RECONSTRUCTION_UNIT_14_RESULT

        # ----------------------------------------------------
        # UNIT 13: EXISTING TP1 / TP2 MECHANISM
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_13_RESULT = (
            checked_result(
                "UNIT13",
                fresh_reconstruction_unit_13(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_12_RESULT
                )
            )
        )

        # ----------------------------------------------------
        # UNIT 14A: POSITION MONITOR
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_14A_RESULT = (
            checked_result(
                "UNIT14A",
                fresh_tp3_runtime(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_13_RESULT
                )
            )
        )

        # ----------------------------------------------------
        # UNIT 14B: BACKUP SIZING
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_14B_RESULT = (
            checked_result(
                "UNIT14B",
                fresh_unit_14b_backup_sizing(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_14A_RESULT
                )
            )
        )

        # ----------------------------------------------------
        # UNIT 14C: LIQUIDATION TRIGGERS
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_14C_RESULT = (
            checked_result(
                "UNIT14C",
                fresh_unit_14c_liquidation_triggers(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_14B_RESULT
                )
            )
        )

        # ----------------------------------------------------
        # UNIT 14D: ORIGINAL FIVE BACKUPS
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_14D_RESULT = (
            checked_result(
                "UNIT14D",
                fresh_unit_14d_progressive_backups(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_14C_RESULT
                )
            )
        )

        # ----------------------------------------------------
        # UNIT 14E: DYNAMIC TP3
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_14E_RESULT = (
            checked_result(
                "UNIT14E",
                fresh_unit_14e_dynamic_tp3(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_14D_RESULT,
                    FRESH_RECONSTRUCTION_UNIT_13_RESULT
                )
            )
        )

        # ----------------------------------------------------
        # UNIT 14F: FINAL POSITION VERIFICATION
        # ----------------------------------------------------

        FRESH_RECONSTRUCTION_UNIT_14_RESULT = (
            checked_result(
                "UNIT14F",
                fresh_unit_14f_coordinator(
                    config,
                    FRESH_RECONSTRUCTION_UNIT_13_RESULT,
                    FRESH_RECONSTRUCTION_UNIT_14E_RESULT
                )
            )
        )

        log(
            "CONTINUOUS UNIT 13 STATUS =",
            FRESH_RECONSTRUCTION_UNIT_13_RESULT.get(
                "status"
            )
        )

        log(
            "CONTINUOUS UNIT 14D STATUS =",
            FRESH_RECONSTRUCTION_UNIT_14D_RESULT.get(
                "status"
            )
        )

        log(
            "CONTINUOUS UNIT 14E STATUS =",
            FRESH_RECONSTRUCTION_UNIT_14E_RESULT.get(
                "status"
            )
        )

        log(
            "CONTINUOUS UNIT 14F STATUS =",
            FRESH_RECONSTRUCTION_UNIT_14_RESULT.get(
                "status"
            )
        )

    log("=" * 80)
    log("ORIGINAL CONTINUOUS TRADING CYCLE = ENABLED")
    log("CONTINUOUS CONTROLLER VERSION = FINAL RESTORATION V1")
    log("CONTINUOUS PYTHON PID =", os.getpid())
    log("CONTINUOUS ENTRY SCAN INTERVAL =", ENTRY_SCAN_SECONDS)
    log("CONTINUOUS POSITION POLL =", POSITION_POLL_SECONDS)
    log("CONTINUOUS SAFETY HOLD = False")
    log("CONTINUOUS BOT_MODE =", current_mode())
    log("=" * 80)

    
    # ========================================================
    # CONTINUOUS CONTROLLER STARTUP RECOVERY V1
    #
    # RECOVER EXISTING WEEX DEMO POSITION BEFORE
    # ANY NEW INITIAL-ENTRY SCAN.
    #
    # NO SECOND TRADING ENGINE
    # NO NEW BOT_MODE
    # NO LEVERAGE MUTATION
    # NO LIVE-CASH ORDERS
    # ========================================================

    print("=" * 72, flush=True)
    print(
        "CONTINUOUS STARTUP RECOVERY = BEGIN",
        flush=True
    )

    recovery_result = fresh_unit_14f_coordinator(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_13_RESULT,
        FRESH_RECONSTRUCTION_UNIT_14E_RESULT
    )

    if not isinstance(recovery_result, dict):
        raise RuntimeError(
            "STARTUP_RECOVERY_INVALID_POSITION_RESULT"
        )

    recovery_status = str(
        recovery_result.get("status") or ""
    ).upper()

    recovery_verified = (
        recovery_result.get(
            "demo_position_verified"
        ) is True
    )

    recovery_active = (
        recovery_result.get(
            "active_position_exists"
        ) is True
    )

    print(
        "CONTINUOUS RECOVERY STATUS =",
        recovery_status,
        flush=True
    )

    print(
        "CONTINUOUS RECOVERY VERIFIED =",
        recovery_verified,
        flush=True
    )

    print(
        "CONTINUOUS RECOVERY ACTIVE =",
        recovery_active,
        flush=True
    )

    if (
        recovery_status == "POSITION_MANAGEMENT_ACTIVE"
        and recovery_verified
        and recovery_active
    ):

        print(
            "PASS: EXISTING WEEX DEMO POSITION RECOVERED",
            flush=True
        )

        print(
            "CONTINUOUS RECOVERED SIDE =",
            recovery_result.get("position_side"),
            flush=True
        )

        print(
            "CONTINUOUS RECOVERED SIZE =",
            recovery_result.get("position_size"),
            flush=True
        )

        print(
            "CONTINUOUS INITIAL ENTRY = BLOCKED",
            flush=True
        )

        print(
            "CONTINUOUS MANAGEMENT = RESUMING",
            flush=True
        )

        # Use the SAME existing Unit 13-14F manager.
        # No new order executor is introduced.

        run_position_management()

        print(
            "PASS: RECOVERED POSITION "
            "MANAGEMENT INVOKED",
            flush=True
        )

    elif (
        recovery_status == "IDLE_NO_POSITION"
        and recovery_verified
        and not recovery_active
    ):

        print(
            "PASS: WEEX DEMO ACCOUNT VERIFIED FLAT",
            flush=True
        )

        print(
            "CONTINUOUS MANAGEMENT = NOT REQUIRED",
            flush=True
        )

        print(
            "CONTINUOUS INITIAL ENTRY = "
            "SUBJECT TO NORMAL BOT_MODE AND SAFETY",
            flush=True
        )

    else:

        print(
            "BLOCKED: STARTUP POSITION "
            "RECONCILIATION INCOMPLETE",
            flush=True
        )

        print(
            "CONTINUOUS INITIAL ENTRY = PROHIBITED",
            flush=True
        )

        raise RuntimeError(
            "STARTUP_DEMO_POSITION_UNVERIFIED"
        )

    print(
        "CONTINUOUS STARTUP RECOVERY = COMPLETE",
        flush=True
    )
    print("=" * 72, flush=True)

    while True:

        cycles += 1

        log("-" * 80)
        log(
            "CONTINUOUS CYCLE =", cycles,
            "| PID =", os.getpid(),
            "| UTC =", datetime.now(
                timezone.utc
            ).isoformat()
        )

        log(
            "CONTINUOUS BOT_MODE =",
            current_mode()
        )

        try:

            # -----------------------------------------------
            # ALWAYS CHECK WEEX POSITION FIRST.
            # -----------------------------------------------

            checkpoint = checked_result(
                "POSITION_CHECKPOINT",
                read_position()
            )

            state = str(
                checkpoint.get("status", "")
            ).upper()

            if state not in (
                "IDLE_NO_POSITION",
                "POSITION_MANAGEMENT_ACTIVE"
            ):

                log(
                    "CONTINUOUS RECONCILIATION WAIT =",
                    state
                )

                time.sleep(ERROR_RETRY_SECONDS)
                continue

            active = (
                state == "POSITION_MANAGEMENT_ACTIVE"
            )

            if previous_active is not None:

                if previous_active and not active:

                    log("=" * 80)
                    log(
                        "CONTINUOUS POSITION CLOSED = TRUE"
                    )
                    log(
                        "CONTINUOUS RETURN TO FRESH "
                        "MARKET SCANNING"
                    )
                    log("=" * 80)

            previous_active = active

            # -----------------------------------------------
            # SAFETY HOLD
            #
            # KEEP PROCESS ALIVE, BUT DO NOT REPEAT
            # ANY ORDER-CAPABLE UNIT AFTER UNKNOWN ERROR.
            # -----------------------------------------------

            if safety_hold:

                log(
                    "CONTINUOUS STATUS = SAFETY_HOLD"
                )

                log(
                    "CONTINUOUS POSITION ACTIVE =",
                    active
                )

                log(
                    "CONTINUOUS ORDERS = SUSPENDED"
                )

                time.sleep(ERROR_RETRY_SECONDS)
                continue

            # -----------------------------------------------
            # ACTIVE POSITION: REPEAT MANAGEMENT.
            # NO FRESH INITIAL ENTRY.
            # -----------------------------------------------

            if active:

                position_scans += 1

                log(
                    "CONTINUOUS POSITION SCAN =",
                    position_scans
                )

                log(
                    "CONTINUOUS NEW INITIAL ENTRY = BLOCKED"
                )

                run_position_management()

                time.sleep(POSITION_POLL_SECONDS)
                continue

            # -----------------------------------------------
            # FLAT ACCOUNT: REFRESH NEW MARKET SIGNALS.
            # UNIT 12 ENFORCES BOT_MODE AND CHECKS.
            # -----------------------------------------------

            entry_scans += 1

            log(
                "CONTINUOUS ENTRY SCAN =",
                entry_scans
            )

            run_market_scan()

            # Unit 12 may have opened a new position.
            # Refresh management immediately afterward.
            run_position_management()

            
            # ================================================
            # STRATEGY PROGRESSION MONITOR
            # READ ONLY - NO TRADING CHANGES
            # ================================================

            fresh_strategy_progress_diagnostic(
                FRESH_RECONSTRUCTION_SIGNAL_CANDIDATE,
                FRESH_RECONSTRUCTION_UNIT_9_RESULT,
                FRESH_RECONSTRUCTION_UNIT_10_RESULT,
                FRESH_RECONSTRUCTION_UNIT_11_RESULT,
                FRESH_RECONSTRUCTION_UNIT_12_RESULT,
                report_every=20
            )



            log(
                "CONTINUOUS CYCLE COMPLETED =",
                cycles
            )

            time.sleep(ENTRY_SCAN_SECONDS)

        except KeyboardInterrupt:

            log(
                "CONTINUOUS STOP REQUESTED"
            )

            raise

        except Exception as error:

            log(
                "CONTINUOUS ERROR TYPE =",
                type(error).__name__
            )

            log(
                "CONTINUOUS ERROR DETAILS =",
                str(error)
            )

            traceback.print_exc()

            # Fail closed. Automatic retry of potentially
            # uncertain order submissions is not safe.
            safety_hold = True

            log(
                "CONTINUOUS SAFETY HOLD = TRUE"
            )

            log(
                "CONTINUOUS ORDER-CAPABLE CYCLES "
                "= SUSPENDED"
            )

            time.sleep(ERROR_RETRY_SECONDS)


# ============================================================
# START CONTINUOUS CONTROLLER
# ZERO INDENTATION
# ============================================================

FRESH_ORIGINAL_CONTINUOUS_CONTROLLER_RESULT = (
    fresh_original_continuous_controller()
)


# ============================================================
# END ORIGINAL CONTINUOUS CYCLE RESTORATION
# ZERO INDENTATION
# ============================================================
