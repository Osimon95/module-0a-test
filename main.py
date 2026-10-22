
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
