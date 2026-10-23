
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
# START UNIT 12 - HYBRID ADJUSTABLE V2.2
# ZERO INDENTATION
#
# REFERENCE: 22524-LINE WORKING MAIN.PY
#
# RESTORED DEMO ORDER SUBMISSION
# ADDED EXCHANGE-HISTORY RECONCILIATION
# PERSISTENT JOURNAL SUPPORT
# SINGLE MASTER BOT_MODE
#
# NEVER SUBMITS REAL-CASH ORDERS
# NEVER CHANGES LEVERAGE
# NEVER CHANGES MARGIN OR POSITION MODE
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

    from decimal import Decimal
    from datetime import datetime, timezone
    from urllib.parse import urlencode

    def log(*values):
        print(*values, flush=True)

    def D(value, name):

        if isinstance(value, bool):
            raise ValueError(name + " BOOLEAN")

        try:
            value = Decimal(str(value))
        except Exception as exc:
            raise ValueError(
                name + " INVALID"
            ) from exc

        if not value.is_finite():
            raise ValueError(
                name + " NONFINITE"
            )

        return value

    def now_ms():
        return int(time.time() * 1000)

    log("=" * 80)

    log(
        datetime.now(timezone.utc).isoformat(),
        "UNIT 12 HYBRID ADJUSTABLE V2.2 START"
    )

    # ========================================================
    # 1. INPUT AND SAFETY CONTRACT
    # ========================================================

    if not isinstance(config, dict):
        raise RuntimeError(
            "UNIT 12 CONFIG INVALID"
        )

    if not isinstance(unit_11_result, dict):
        raise RuntimeError(
            "UNIT 12 UNIT 11 INVALID"
        )

    if unit_11_result.get(
        "unit_11_revision"
    ) != "HYBRID_ADJUSTABLE_V2":
        raise RuntimeError(
            "UNIT 12 UNIT 11 REVISION INVALID"
        )

    exchange = config.get("exchange", {})
    safety = config.get("safety", {})
    precision = config.get(
        "market_precision", {}
    )

    if not all(
        isinstance(x, dict)
        for x in (
            exchange,
            safety,
            precision,
        )
    ):
        raise RuntimeError(
            "UNIT 12 CONFIG SECTIONS INVALID"
        )

    if not (
        config.get("execution_environment")
        == "DEMO"
        and exchange.get("market_symbol")
        == "BTCUSDT"
        and exchange.get("demo_order_symbol")
        == "BTCSUSDT"
        and exchange.get("contract_base_url")
        == "https://api-contract.weex.com"
        and unit_11_result.get("read_only")
        is True
        and unit_11_result.get("exchange_write")
        is False
    ):
        raise RuntimeError(
            "UNIT 12 DEMO BOUNDARY INVALID"
        )

    for key in (
        "real_order_submission_enabled",
        "leverage_mutation_enabled",
        "margin_mode_mutation_enabled",
        "position_mode_mutation_enabled",
    ):

        if safety.get(key) is not False:
            raise RuntimeError(
                "UNIT 12 UNSAFE CONFIG " + key
            )

    # ========================================================
    # 2. DOWNSTREAM RESULT CONTRACT
    # ========================================================

    result = {

        "unit": 12,

        "unit_12_revision":
            "HYBRID_ADJUSTABLE_V2.2",

        "status": "IDLE",

        "read_only": False,

        "active_mode": unit_11_result.get(
            "active_mode", "NONE"
        ),

        "direction": unit_11_result.get(
            "direction", "NONE"
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

        "history_checked": False,
        "history_complete": False,

        "journal_reconciled": False,
        "reconciliation_status": "NOT_CHECKED",

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

        "skip_reason": unit_11_result.get(
            "skip_reason", "NONE"
        ),
    }

    def finish(status, reason):

        result["status"] = status
        result["skip_reason"] = str(reason)

        log(
            "UNIT 12 STATUS =",
            status
        )

        log(
            "UNIT 12 SKIP REASON =",
            reason
        )

        log(
            "UNIT 12 HISTORY CHECKED =",
            result["history_checked"]
        )

        log(
            "UNIT 12 JOURNAL RECONCILED =",
            result["journal_reconciled"]
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
            "UNIT 12 HYBRID ADJUSTABLE V2.2 RESULT =",
            status
        )

        log("=" * 80)

        return result

    # ========================================================
    # 3. ONE MASTER BOT_MODE
    # ========================================================

    bot_mode = str(
        os.getenv("BOT_MODE", "PAUSE")
    ).strip().upper()

    if bot_mode not in ("RUN", "PAUSE"):
        raise RuntimeError(
            "UNIT 12 INVALID BOT_MODE"
        )

    log(
        "UNIT 12 MASTER BOT_MODE =",
        bot_mode
    )

    # ========================================================
    # 4. IDLE AND PAUSE HANDOVER
    # ========================================================

    status11 = str(
        unit_11_result.get(
            "status", "IDLE"
        )
    ).upper()

    if status11 == "IDLE":

        if unit_11_result.get(
            "payload_ready"
        ) is not False:
            raise RuntimeError(
                "UNIT 12 IDLE PAYLOAD INVALID"
            )

        return finish(
            "IDLE",
            result["skip_reason"]
        )

    if status11 != "READY":
        return finish(
            "BLOCKED",
            "UNIT_11_NOT_READY"
        )

    if bot_mode == "PAUSE":
        return finish(
            "PAUSED",
            "MASTER_BOT_MODE_PAUSE"
        )

    # ========================================================
    # 5. UNIT 11 READY FLAGS
    # ========================================================

    for key in (
        "signal_qualified",
        "execution_intent",
        "trade_plan_ready",
        "execution_ready",
        "demo_boundary_ready",
        "payload_ready",
        "order_payload_created",
    ):

        if unit_11_result.get(key) is not True:

            return finish(
                "BLOCKED",
                "UNIT_11_FLAG_MISSING:" + key
            )

    mode = unit_11_result.get(
        "active_mode"
    )

    direction = unit_11_result.get(
        "direction"
    )

    if mode not in (
        "BREAKOUT",
        "STRUCTURE",
        "SCALP",
    ):
        return finish(
            "BLOCKED",
            "INVALID_TRADE_MODE"
        )

    if direction not in (
        "LONG",
        "SHORT",
    ):
        return finish(
            "BLOCKED",
            "INVALID_TRADE_DIRECTION"
        )

    result["active_mode"] = mode
    result["direction"] = direction
    result["signal_qualified"] = True
    result["execution_intent"] = True

    log(
        "PASS: UNIT 12 UNIT 11 READY CONTRACT"
    )

    # ========================================================
    # 6. ORIGINAL DEMO ORDER PAYLOAD
    # ========================================================

    payload = (
        unit_11_result.get("demo_payload")
        or unit_11_result.get("payload")
        or unit_11_result.get("order_payload")
    )

    trade_plan = unit_11_result.get(
        "trade_plan"
    )

    if not (
        isinstance(payload, dict)
        and isinstance(trade_plan, dict)
    ):
        return finish(
            "BLOCKED",
            "UNIT_11_PAYLOAD_OR_PLAN_MISSING"
        )

    expected_fields = {
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    }

    if set(payload) != expected_fields:
        return finish(
            "BLOCKED",
            "DEMO_PAYLOAD_FIELDS_INVALID"
        )

    expected_side = (
        "BUY" if direction == "LONG"
        else "SELL"
    )

    if not (
        payload.get("symbol") == "BTCSUSDT"
        and payload.get("side") == expected_side
        and payload.get("positionSide")
        == direction
        and payload.get("type") == "MARKET"
    ):
        return finish(
            "BLOCKED",
            "DEMO_PAYLOAD_DIRECTION_MISMATCH"
        )

    client_id = str(
        payload.get(
            "newClientOrderId", ""
        )
    )

    if not re.fullmatch(
        r"[A-Za-z0-9_.-]{1,36}",
        client_id
    ):
        return finish(
            "BLOCKED",
            "CLIENT_ORDER_ID_INVALID"
        )

    try:

        quantity = D(
            payload["quantity"],
            "ORDER QUANTITY"
        )

        planned_quantity = D(
            trade_plan["quantity"],
            "PLANNED QUANTITY"
        )

        quantity_step = D(
            precision["quantity_step"],
            "QUANTITY STEP"
        )

        min_quantity = D(
            precision["minimum_quantity"],
            "MINIMUM QUANTITY"
        )

        if not (
            quantity == planned_quantity
            and quantity_step > 0
            and min_quantity > 0
            and quantity >= min_quantity
            and quantity % quantity_step == 0
        ):
            return finish(
                "BLOCKED",
                "ORDER_QUANTITY_INVALID"
            )

        sizing = trade_plan.get(
            "position_sizing"
        )

        if not isinstance(sizing, dict):
            return finish(
                "BLOCKED",
                "POSITION_SIZING_MISSING"
            )

        if not (
            sizing.get(
                "position_sizing_performed"
            ) is True
            and sizing.get(
                "quantity_calculated"
            ) is True
        ):
            return finish(
                "BLOCKED",
                "POSITION_SIZING_NOT_VERIFIED"
            )

    except Exception:

        return finish(
            "BLOCKED",
            "ORDER_QUANTITY_VALIDATION_FAILED"
        )

    log(
        "PASS: UNIT 12 ORIGINAL DEMO PAYLOAD"
    )

    log(
        "UNIT 12 STRATEGY =", mode
    )

    log(
        "UNIT 12 DIRECTION =", direction
    )

    log(
        "UNIT 12 QUANTITY =", quantity
    )

    log(
        "UNIT 12 DEMO LEVERAGE SCOPE CONFIRMED =",
        sizing.get(
            "demo_leverage_scope_confirmed",
            False
        )
    )

    # ========================================================
    # 7. WEEX AUTHENTICATION
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

    if not all((
        api_key,
        api_secret,
        api_passphrase,
    )):
        return finish(
            "BLOCKED",
            "WEEX_CREDENTIALS_MISSING"
        )

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
            newurl,
        ):
            return None

    opener = urllib.request.build_opener(
        NoRedirect()
    )

    base_url = (
        "https://api-contract.weex.com"
    )

    allowed_paths = {
        (
            "GET",
            "/capi/v3/sim/position/allPosition"
        ),
        (
            "GET",
            "/capi/v3/sim/order/history"
        ),
        (
            "POST",
            "/capi/v3/sim/order"
        ),
    }

    def request_weex(
        method,
        path,
        query=None,
        body=None,
    ):

        if (method, path) not in allowed_paths:
            raise RuntimeError(
                "UNIT 12 UNAPPROVED ENDPOINT"
            )

        if method == "GET" and body is not None:
            raise RuntimeError(
                "UNIT 12 GET BODY INVALID"
            )

        if method == "POST" and (
            body is None or query
        ):
            raise RuntimeError(
                "UNIT 12 POST PARAMETERS INVALID"
            )

        query_text = (
            urlencode(query)
            if query else ""
        )

        request_path = (
            path
            + (
                "?" + query_text
                if query_text else ""
            )
        )

        body_text = (
            ""
            if body is None
            else json.dumps(
                body,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )

        timestamp = str(
            now_ms()
        )

        signature_text = (
            timestamp
            + method
            + request_path
            + body_text
        )

        signature = base64.b64encode(
            hmac.new(
                api_secret.encode(),
                signature_text.encode(),
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
            base_url + request_path,
            data=(
                None
                if body is None
                else body_text.encode()
            ),
            headers=headers,
            method=method,
        )

        try:

            with opener.open(
                request,
                timeout=15,
            ) as response:

                code = response.getcode()

                raw = response.read(
                    65537
                )

        except urllib.error.HTTPError as exc:

            code = exc.code

            raw = exc.read(
                65537
            )

        if len(raw) > 65536:
            raise RuntimeError(
                "UNIT 12 RESPONSE TOO LARGE"
            )

        data = json.loads(
            raw.decode("utf-8")
        )

        return code, data

    # ========================================================
    # 8. LOCAL SUBMISSION JOURNAL
    #
    # FOR CONTINUITY, USE A PERSISTENT
    # VOLUME WHEN AVAILABLE.
    #
    # /tmp IS NOT DURABLE ACROSS
    # ALL RENDER DEPLOYMENTS.
    # ========================================================

    journal_path = os.getenv(
        "WEEX_DEMO_ENTRY_JOURNAL",
        "/tmp/weex_demo_entry_v21.json"
    )

    journal_dir = os.path.dirname(
        os.path.abspath(journal_path)
    )

    if not os.path.isdir(journal_dir):
        return finish(
            "BLOCKED",
            "JOURNAL_DIRECTORY_MISSING"
        )

    def save_journal(value):

        fd, temporary = tempfile.mkstemp(
            prefix=".weex12_",
            dir=journal_dir,
            text=True,
        )

        try:

            with os.fdopen(fd, "w") as handle:

                json.dump(
                    value,
                    handle
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )

            os.replace(
                temporary,
                journal_path
            )

            dir_fd = os.open(
                journal_dir,
                os.O_RDONLY
            )

            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)

        finally:

            if os.path.exists(temporary):
                os.unlink(temporary)

    lock_file = None

    try:

        lock_file = open(
            journal_path + ".lock",
            "a+"
        )

        fcntl.flock(
            lock_file.fileno(),
            fcntl.LOCK_EX
            | fcntl.LOCK_NB
        )

    except Exception:

        if lock_file is not None:
            lock_file.close()

        return finish(
            "BLOCKED",
            "SUBMISSION_LOCK_UNAVAILABLE"
        )

    try:

        # ====================================================
        # 9. READ EXISTING JOURNAL
        # ====================================================

        try:

            with open(
                journal_path, "r"
            ) as handle:

                journal = json.load(handle)

        except FileNotFoundError:

            journal = {}

        except Exception:

            return finish(
                "BLOCKED",
                "JOURNAL_READ_FAILED"
            )

        if not isinstance(journal, dict):
            return finish(
                "BLOCKED",
                "JOURNAL_CONTENT_INVALID"
            )

        previous_status = str(
            journal.get("status", "")
        ).upper()

        previous_client_id = str(
            journal.get(
                "client_order_id", ""
            )
        )

        previous_order_id = str(
            journal.get(
                "order_id", ""
            )
        )

        previous_time = journal.get(
            "timestamp", 0
        )

        try:

            previous_age = (
                time.time()
                - float(previous_time)
            )

        except Exception:

            previous_age = -1

        # ====================================================
        # 10. RECHECK DEMO BTC POSITIONS
        # ====================================================

        result[
            "position_check_attempted"
        ] = True

        result[
            "authenticated_request"
        ] = True

        try:

            position_http, positions = request_weex(
                "GET",
                "/capi/v3/sim/position/allPosition"
            )

        except Exception as exc:

            log(
                "UNIT 12 POSITION GET ERROR =",
                type(exc).__name__
            )

            return finish(
                "BLOCKED",
                "DEMO_POSITION_GET_FAILED"
            )

        result[
            "position_endpoint_access"
        ] = True

        result[
            "position_http_status"
        ] = position_http

        if not (
            position_http == 200
            and isinstance(positions, list)
        ):
            return finish(
                "BLOCKED",
                "DEMO_POSITION_RESPONSE_INVALID"
            )

        active_positions = []

        try:

            for item in positions:

                if not isinstance(item, dict):
                    raise ValueError(
                        "POSITION_ROW_INVALID"
                    )

                symbol = str(
                    item.get("symbol", "")
                ).upper()

                if symbol not in (
                    "BTCUSDT",
                    "BTCSUSDT",
                ):
                    continue

                if "size" not in item:
                    raise ValueError(
                        "POSITION_SIZE_MISSING"
                    )

                size = D(
                    item["size"],
                    "POSITION SIZE"
                )

                if size < 0:
                    raise ValueError(
                        "NEGATIVE_POSITION_SIZE"
                    )

                if size > 0:

                    active_positions.append({
                        "symbol": symbol,
                        "side": item.get("side"),
                        "size": float(size),
                        "leverage": item.get(
                            "leverage"
                        ),
                    })

        except Exception:

            return finish(
                "BLOCKED",
                "DEMO_POSITION_PARSE_FAILED"
            )

        result[
            "position_check_completed"
        ] = True

        result[
            "active_positions"
        ] = active_positions

        if active_positions:

            result[
                "active_position_exists"
            ] = True

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
                "EXISTING_DEMO_POSITION"
            )

        log(
            "PASS: UNIT 12 DEMO POSITION FLAT"
        )

        # ====================================================
        # 11. VERIFY COMPLETE RECENT ORDER HISTORY
        #
        # THE WEEX DEMO ENDPOINT RETURNS
        # A LIST OF ORDER OBJECTS.
        #
        # PAGINATE UNTIL THE FINAL PAGE.
        # DO NOT INFER NO PENDING ORDER
        # FROM A TRUNCATED RESULT.
        # ====================================================

        all_orders = []

        limit = 1000

        max_pages = 10

        for page in range(max_pages):

            try:

                history_http, rows = request_weex(
                    "GET",
                    "/capi/v3/sim/order/history",
                    query={
                        "symbol": "BTCSUSDT",
                        "limit": limit,
                        "page": page,
                    },
                )

            except Exception as exc:

                log(
                    "UNIT 12 HISTORY GET ERROR =",
                    type(exc).__name__
                )

                return finish(
                    "BLOCKED",
                    "DEMO_HISTORY_GET_FAILED"
                )

            if not (
                history_http == 200
                and isinstance(rows, list)
                and all(
                    isinstance(row, dict)
                    for row in rows
                )
            ):

                return finish(
                    "BLOCKED",
                    "DEMO_HISTORY_RESPONSE_INVALID"
                )

            all_orders.extend(rows)

            if len(rows) < limit:
                result["history_complete"] = True
                break

        result["history_checked"] = True

        if not result["history_complete"]:

            return finish(
                "BLOCKED",
                "DEMO_HISTORY_PAGINATION_INCOMPLETE"
            )

        log(
            "PASS: UNIT 12 DEMO ORDER HISTORY COMPLETE"
        )

        log(
            "UNIT 12 HISTORY RECORDS =",
            len(all_orders)
        )

        # ====================================================
        # 12. PREVENT DUPLICATE OPEN ORDERS
        # ====================================================

        pending_states = {
            "NEW",
            "PENDING_NEW",
            "PARTIALLY_FILLED",
            "PARTIALLYFILLED",
            "OPEN",
            "PENDING",
            "ACCEPTED",
        }

        terminal_states = {
            "FILLED",
            "CANCELED",
            "CANCELLED",
            "EXPIRED",
            "REJECTED",
        }

        for order in all_orders:

            if str(
                order.get("symbol", "")
            ).upper() != "BTCSUSDT":
                continue

            order_status = str(
                order.get("status", "")
            ).upper()

            if order_status in pending_states:

                result[
                    "duplicate_initial_entry_blocked"
                ] = True

                return finish(
                    "BLOCKED",
                    "EXISTING_DEMO_PENDING_ORDER"
                )

            if order_status not in terminal_states:

                return finish(
                    "BLOCKED",
                    "UNKNOWN_DEMO_ORDER_STATUS"
                )

        log(
            "PASS: UNIT 12 NO PENDING ORDER "
            "IN RETURNED DEMO HISTORY"
        )

        # ====================================================
        # 13. RECONCILE PREVIOUS SUBMISSION
        # ====================================================

        previous_active_states = {
            "POST_STARTED",
            "POST_UNKNOWN",
            "POST_ACCEPTED",
        }

        if previous_status in previous_active_states:

            if not (
                previous_client_id
                or previous_order_id
            ):

                return finish(
                    "BLOCKED",
                    "JOURNAL_ORDER_IDENTITY_MISSING"
                )

            matched = []

            for order in all_orders:

                order_id = str(
                    order.get("orderId", "")
                )

                client_order_id = str(
                    order.get(
                        "clientOrderId", ""
                    )
                )

                if (
                    (
                        previous_order_id
                        and order_id
                        == previous_order_id
                    )
                    or (
                        previous_client_id
                        and client_order_id
                        == previous_client_id
                    )
                ):
                    matched.append(order)

            if not matched:

                return finish(
                    "BLOCKED",
                    "PREVIOUS_SUBMISSION_NOT_FOUND"
                )

            if len(matched) != 1:

                return finish(
                    "BLOCKED",
                    "PREVIOUS_SUBMISSION_NOT_UNIQUE"
                )

            previous_order = matched[0]

            last_exchange_status = str(
                previous_order.get(
                    "status", ""
                )
            ).upper()

            log(
                "UNIT 12 PREVIOUS WEEX ORDER STATUS =",
                last_exchange_status
            )

            if last_exchange_status not in terminal_states:

                return finish(
                    "BLOCKED",
                    "PREVIOUS_ORDER_NOT_TERMINAL"
                )

            if previous_age < 0:

                return finish(
                    "BLOCKED",
                    "JOURNAL_TIMESTAMP_INVALID"
                )

            if previous_age < 300:

                return finish(
                    "COOLDOWN",
                    "FIVE_MINUTE_REENTRY_COOLDOWN"
                )

            # A terminal entry plus flat
            # position permits reconciliation
            # of the initial submission.
            #
            # It does not itself prove
            # accurate TP / backup history.

            reconciled = {
                "status": "RECONCILED",
                "timestamp": time.time(),
                "previous_client_order_id":
                    previous_client_id,
                "previous_order_id":
                    str(
                        previous_order.get(
                            "orderId", ""
                        )
                    ),
                "previous_exchange_status":
                    last_exchange_status,
            }

            try:

                save_journal(reconciled)

            except Exception:

                return finish(
                    "BLOCKED",
                    "RECONCILIATION_SAVE_FAILED"
                )

            journal = reconciled

            previous_status = "RECONCILED"

            result[
                "journal_reconciled"
            ] = True

            result[
                "reconciliation_status"
            ] = "EXCHANGE_VERIFIED"

            log(
                "PASS: UNIT 12 PREVIOUS ORDER "
                "RECONCILED WITH WEEX"
            )

        elif previous_status in (
            "",
            "RECONCILED",
            "COOLDOWN",
        ):

            if (
                previous_status == "COOLDOWN"
                and previous_age < 300
            ):

                return finish(
                    "COOLDOWN",
                    "FIVE_MINUTE_REENTRY_COOLDOWN"
                )

            result[
                "journal_reconciled"
            ] = True

            result[
                "reconciliation_status"
            ] = (
                "NO_UNRESOLVED_JOURNAL"
            )

        else:

            return finish(
                "BLOCKED",
                "UNKNOWN_JOURNAL_STATUS"
            )

        # ====================================================
        # 14. RECENT EXCHANGE ENTRY COOLDOWN
        #
        # A RECENT COMPLETED OR CANCELLED
        # DEMO ORDER ALSO PREVENTS AN
        # IMMEDIATE NEW ENTRY.
        # ====================================================

        for order in all_orders:

            if str(
                order.get("symbol", "")
            ).upper() != "BTCSUSDT":
                continue

            if str(
                order.get("type", "")
            ).upper() != "MARKET":
                continue

            if str(
                order.get("side", "")
            ).upper() != "BUY" and str(
                order.get("side", "")
            ).upper() != "SELL":
                continue

            if str(
                order.get("reduceOnly", "")
            ).lower() == "true":
                continue

            # Use the WEEX creation timestamp.
            try:

                order_time = int(
                    order.get("time", 0)
                )

            except Exception:

                return finish(
                    "BLOCKED",
                    "EXCHANGE_ORDER_TIME_INVALID"
                )

            if (
                order_time > 0
                and 0 <= now_ms() - order_time
                < 300000
            ):

                return finish(
                    "COOLDOWN",
                    "RECENT_DEMO_MARKET_ORDER"
                )

        # ====================================================
        # 15. FINAL PRE-SUBMISSION CHECK
        # ====================================================

        result[
            "initial_entry_permitted"
        ] = True

        result[
            "request_path"
        ] = "/capi/v3/sim/order"

        final_payload = dict(payload)

        result[
            "request_payload"
        ] = final_payload

        log(
            "PASS: UNIT 12 PREVIOUS JOURNAL "
            "RECONCILED"
        )

        log(
            "PASS: UNIT 12 INITIAL ENTRY PATH READY"
        )

        log(
            "UNIT 12 DEMO SYMBOL =",
            final_payload["symbol"]
        )

        log(
            "UNIT 12 DEMO DIRECTION =",
            direction
        )

        log(
            "UNIT 12 DEMO QUANTITY =",
            quantity
        )

        # ====================================================
        # 16. DURABLE PRE-POST JOURNAL
        # ====================================================

        journal = {
            "status": "POST_STARTED",
            "timestamp": time.time(),
            "client_order_id": client_id,
            "mode": mode,
            "direction": direction,
            "quantity": str(quantity),
        }

        try:

            save_journal(journal)

        except Exception:

            return finish(
                "BLOCKED",
                "PREPOST_JOURNAL_SAVE_FAILED"
            )

        # ====================================================
        # 17. ORIGINAL WEEX DEMO POST
        # ====================================================

        result[
            "demo_submission_attempted"
        ] = True

        result[
            "order_endpoint_access"
        ] = True

        # The request may reach WEEX even
        # if the network returns an error.

        result["exchange_write"] = True

        log(
            "UNIT 12 SENDING DEMO MARKET ORDER"
        )

        try:

            order_http, response = request_weex(
                "POST",
                "/capi/v3/sim/order",
                body=final_payload,
            )

        except Exception as exc:

            log(
                "UNIT 12 POST ERROR =",
                type(exc).__name__
            )

            journal["status"] = "POST_UNKNOWN"

            try:

                save_journal(journal)

            except Exception:
                pass

            return finish(
                "SUBMISSION_OUTCOME_UNKNOWN",
                "VERIFY_WEEX_HISTORY_BEFORE_RETRY"
            )

        result["http_status"] = order_http

        result["weex_response"] = response

        if not (
            isinstance(response, dict)
            and 200 <= order_http < 300
            and response.get("success") is True
            and response.get("orderId")
        ):

            journal["status"] = "POST_UNKNOWN"

            try:

                save_journal(journal)

            except Exception:
                pass

            return finish(
                "SUBMISSION_UNCONFIRMED",
                "WEEX_ACCEPTANCE_NOT_CONFIRMED"
            )

        # ====================================================
        # 18. CONFIRMED DEMO ORDER
        # ====================================================

        order_id = response["orderId"]

        journal.update({
            "status": "POST_ACCEPTED",
            "timestamp": time.time(),
            "order_id": str(order_id),
        })

        try:

            save_journal(journal)

        except Exception:

            log(
                "UNIT 12 WARNING: ACCEPTED ORDER "
                "JOURNAL SAVE FAILED"
            )

        result[
            "demo_submission_completed"
        ] = True

        result["order_id"] = order_id

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
            "PASS: UNIT 12 WEEX DEMO ORDER ACCEPTED"
        )

        log(
            "UNIT 12 EXCHANGE ORDER ID =",
            order_id
        )

        log(
            "UNIT 12 REAL ORDER = NONE"
        )

        log(
            "UNIT 12 LEVERAGE CHANGE = NONE"
        )

        return finish(
            "DEMO_SUBMITTED",
            "WEEX_ORDER_ACCEPTED"
        )

    finally:

        fcntl.flock(
            lock_file.fileno(),
            fcntl.LOCK_UN
        )

        lock_file.close()


# ============================================================
# UNIT 12 EXECUTION
# ZERO INDENTATION
# ============================================================

FRESH_RECONSTRUCTION_UNIT_12_RESULT = (
    fresh_reconstruction_unit_12(
        FRESH_RECONSTRUCTION_CONFIG,
        FRESH_RECONSTRUCTION_UNIT_11_RESULT,
    )
)


# ============================================================
# END UNIT 12 - HYBRID ADJUSTABLE V2.2
# ZERO INDENTATION
# ============================================================
