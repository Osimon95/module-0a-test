
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
